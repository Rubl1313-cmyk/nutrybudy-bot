"""
Очистка устаревших данных FSM
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from typing import List

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
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
                if current_time - created_at > timedelta(seconds=self.ttl):
                    expired_keys.append(analysis_id)
            
            # Удаляем устаревшие данные
            if expired_keys:
                for key in expired_keys:
                    del photo_analysis[key]
                    logger.info(f"🧹 Cleaned up expired photo analysis: {key}")
                
                await state.update_data(photo_analysis=photo_analysis)
                logger.info(f"🧹 Cleaned up {len(expired_keys)} expired photo analyses")
        
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
                    data = await storage.redis.get(key)
                    if not data:
                        continue
                    
                    # Проверяем время последнего обновления
                    ttl = await storage.redis.ttl(key)
                    if ttl == -1:  # Нет TTL
                        # Устанавливаем TTL если данных нет больше часа
                        await storage.redis.expire(key, self.ttl)
                        cleaned_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing key {key}: {e}")
                    continue
            
            if cleaned_count > 0:
                logger.info(f"🧹 Set TTL for {cleaned_count} FSM keys")
        
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
