"""
Чистка устаревших данных FSM
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage

logger = logging.getLogger(__name__)

class FSMCleanupService:
    """Сервис очистки устаревших данных FSM"""
    
    def __init__(self, storage: RedisStorage, ttl_seconds: int = 3600):
        self.storage = storage
        self.ttl = ttl_seconds
    
    async def cleanup_expired_photo_data(self, state: FSMContext):
        """Очищает устаревшие данные анализа фото"""
        try:
            data = await state.get_data()
            photo_analysis = data.get('photo_analysis', {})
            
            if not photo_analysis:
                return
            
            current_time = datetime.now(timezone.utc)
            expired_keys = []
            
            for analysis_id, analysis_data in photo_analysis.items():
                # Проверяем время создания данных
                created_at = analysis_data.get('created_at')
                if not created_at:
                    continue
                
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                
                if current_time - created_at > timedelta(seconds=self.ttl):
                    expired_keys.append(analysis_id)
            
            # Удаляем устаревшие данные
            if expired_keys:
                for key in expired_keys:
                    del photo_analysis[key]
                    logger.info(f"[CLEANUP] Cleaned up expired photo analysis: {key}")
                
                await state.update_data(photo_analysis=photo_analysis)
                logger.info(f"[CLEANUP] Cleaned up {len(expired_keys)} expired photo analyses")
        
        except Exception as e:
            logger.error(f"Error cleaning up photo data: {e}")
    
    async def cleanup_all_expired_data(self, storage: RedisStorage):
        """Очищает все устаревшие данные FSM"""
        try:
            # Получаем все ключи из Redis
            keys = await storage.redis.keys("fsm:*")
            
            current_time = datetime.now(timezone.utc)
            cleaned_count = 0
            
            for key in keys:
                try:
                    data = await storage.get_data(key=key)
                    
                    if not data:
                        continue
                    
                    # Проверяем время последнего обновления
                    ttl = await storage.redis.ttl(key)
                    if ttl == -1:  # Нет TTL
                        # Устанавливаем TTL если данных нет больше часа
                        await storage.redis.expire(key, self.ttl)
                        cleaned_count += 1
                
                except Exception:
                    # Пропускаем ключи с ошибками
                    continue
            
            if cleaned_count > 0:
                logger.info(f"[CLEANUP] Set TTL for {cleaned_count} FSM keys")
        
        except Exception as e:
            logger.error(f"Error in FSM cleanup: {e}")

# Глобальная функция для периодической очистки
async def periodic_fsm_cleanup(storage: RedisStorage):
    """Периодическая очистка FSM данных"""
    cleanup_service = FSMCleanupService(storage)
    
    while True:
        try:
            await cleanup_service.cleanup_all_expired_data(storage)
            await asyncio.sleep(300)  # Каждые 5 минут
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")
            await asyncio.sleep(60)  # При ошибке ждем 1 минуту

# Утилиты для работы с FSM
class FSMUtils:
    """Утилиты для работы с FSM"""
    
    @staticmethod
    async def set_data_with_ttl(state: FSMContext, key: str, value: Any, ttl_seconds: int = 3600):
        """Устанавливает данные с TTL"""
        try:
            data = await state.get_data()
            
            if 'temp_data' not in data:
                data['temp_data'] = {}
            
            data['temp_data'][key] = {
                'value': value,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'ttl': ttl_seconds
            }
            
            await state.update_data(data)
            logger.info(f"[FSM] Set temporary data: {key}")
            
        except Exception as e:
            logger.error(f"Error setting data with TTL: {e}")
    
    @staticmethod
    async def get_temp_data(state: FSMContext, key: str) -> Any:
        """Получает временные данные"""
        try:
            data = await state.get_data()
            temp_data = data.get('temp_data', {})
            
            if key not in temp_data:
                return None
            
            item = temp_data[key]
            created_at = datetime.fromisoformat(item['created_at'])
            
            # Проверяем TTL
            if datetime.now(timezone.utc) - created_at > timedelta(seconds=item['ttl']):
                # Удаляем устаревшие данные
                del temp_data[key]
                await state.update_data({'temp_data': temp_data})
                return None
            
            return item['value']
            
        except Exception as e:
            logger.error(f"Error getting temp data: {e}")
            return None
    
    @staticmethod
    async def cleanup_temp_data(state: FSMContext):
        """Очищает все временные данные"""
        try:
            data = await state.get_data()
            if 'temp_data' in data:
                del data['temp_data']
                await state.update_data(data)
                logger.info(f"[FSM] Cleaned up temporary data")
            
        except Exception as e:
            logger.error(f"Error cleaning up temp data: {e}")
    
    @staticmethod
    async def get_fsm_stats(storage: RedisStorage) -> Dict[str, int]:
        """Получает статистику FSM"""
        try:
            keys = await storage.redis.keys("fsm:*")
            
            stats = {
                'total_states': len(keys),
                'states_with_ttl': 0,
                'states_without_ttl': 0,
                'expired_states': 0
            }
            
            current_time = datetime.now(timezone.utc)
            
            for key in keys:
                try:
                    ttl = await storage.redis.ttl(key)
                    
                    if ttl == -1:
                        stats['states_without_ttl'] += 1
                    else:
                        stats['states_with_ttl'] += 1
                        
                        if ttl <= 0:
                            stats['expired_states'] += 1
                
                except Exception:
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting FSM stats: {e}")
            return {}
    
    @staticmethod
    async def force_cleanup_all(storage: RedisStorage):
        """Принудительная очистка всех данных FSM"""
        try:
            keys = await storage.redis.keys("fsm:*")
            
            if keys:
                await storage.redis.delete(*keys)
                logger.info(f"[CLEANUP] Force deleted {len(keys)} FSM keys")
            
            return len(keys)
            
        except Exception as e:
            logger.error(f"Error in force cleanup: {e}")
            return 0

# Класс для мониторинга FSM
class FSMMonitor:
    """Мониторинг состояния FSM"""
    
    def __init__(self, storage: RedisStorage):
        self.storage = storage
    
    async def get_active_states(self) -> List[Dict]:
        """Получает список активных состояний"""
        try:
            keys = await storage.redis.keys("fsm:*")
            active_states = []
            
            for key in keys:
                try:
                    data = await self.storage.get_data(key=key)
                    state = await self.storage.get_state(key=key)
                    
                    active_states.append({
                        'key': key.decode() if isinstance(key, bytes) else key,
                        'state': state,
                        'data_keys': list(data.keys()) if data else [],
                        'ttl': await self.storage.redis.ttl(key)
                    })
                
                except Exception:
                    continue
            
            return active_states
            
        except Exception as e:
            logger.error(f"Error getting active states: {e}")
            return []
    
    async def get_user_state(self, user_id: int) -> Dict:
        """Получает состояние конкретного пользователя"""
        try:
            key = f"fsm:{user_id}:chat"
            
            state = await self.storage.get_state(chat=user_id)
            data = await self.storage.get_data(chat=user_id)
            ttl = await self.storage.redis.ttl(key)
            
            return {
                'user_id': user_id,
                'state': state,
                'data': data,
                'ttl': ttl
            }
            
        except Exception as e:
            logger.error(f"Error getting user state: {e}")
            return {}
    
    async def reset_user_state(self, user_id: int) -> bool:
        """Сбрасывает состояние пользователя"""
        try:
            await self.storage.set_state(chat=user_id, state=None)
            await self.storage.set_data(chat=user_id, data={})
            
            logger.info(f"[FSM] Reset state for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting user state: {e}")
            return False

# Декоратор для автоматической очистки
def auto_cleanup(ttl_seconds: int = 3600):
    """Декоратор для автоматической очистки данных после выполнения функции"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                # Ищем state в аргументах
                state = None
                for arg in args:
                    if isinstance(arg, FSMContext):
                        state = arg
                        break
                
                result = await func(*args, **kwargs)
                
                # Очищаем временные данные после выполнения
                if state:
                    await FSMUtils.cleanup_temp_data(state)
                
                return result
                
            except Exception as e:
                logger.error(f"Error in auto_cleanup function: {e}")
                raise
        
        return wrapper
    return decorator

# Функции для работы с фото данными
class PhotoDataManager:
    """Менеджер данных анализа фото"""
    
    @staticmethod
    async def store_photo_analysis(state: FSMContext, analysis_id: str, analysis_data: Dict):
        """Сохраняет данные анализа фото"""
        try:
            data = await state.get_data()
            
            if 'photo_analysis' not in data:
                data['photo_analysis'] = {}
            
            data['photo_analysis'][analysis_id] = {
                **analysis_data,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            await state.update_data(data)
            logger.info(f"[PHOTO] Stored analysis: {analysis_id}")
            
        except Exception as e:
            logger.error(f"Error storing photo analysis: {e}")
    
    @staticmethod
    async def get_photo_analysis(state: FSMContext, analysis_id: str) -> Dict:
        """Получает данные анализа фото"""
        try:
            data = await state.get_data()
            photo_analysis = data.get('photo_analysis', {})
            
            return photo_analysis.get(analysis_id, {})
            
        except Exception as e:
            logger.error(f"Error getting photo analysis: {e}")
            return {}
    
    @staticmethod
    async def cleanup_expired_analyses(state: FSMContext, ttl_seconds: int = 3600):
        """Очищает устаревшие анализы фото"""
        cleanup_service = FSMCleanupService(None, ttl_seconds)
        await cleanup_service.cleanup_expired_photo_data(state)
