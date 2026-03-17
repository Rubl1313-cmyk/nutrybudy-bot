"""
Улучшенный middleware для rate limiting с определением типа запроса
"""
import logging
from typing import Callable, Dict, Any, Optional
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from aiogram.fsm.context import FSMContext

from utils.rate_limiter import UserRateLimiter

logger = logging.getLogger(__name__)

class SmartRateLimitMiddleware(BaseMiddleware):
    """Middleware с умным определением типа запроса для rate limiting"""
    
    def __init__(self, user_rate_limiter: UserRateLimiter):
        self.user_rate_limiter = user_rate_limiter
    
    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Определяем пользователя
        user_id = None
        if event.message:
            user_id = event.message.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
        
        if not user_id:
            return await handler(event, data)
        
        # Определяем тип запроса
        request_type = self._determine_request_type(event)
        
        # Проверяем rate limit
        if not self.user_rate_limiter.is_allowed(user_id, request_type):
            logger.warning(f"Rate limit exceeded for user {user_id}, type: {request_type}")
            
            # Отправляем сообщение о превышении лимита
            if event.message:
                await event.message.answer(
                    "⚠️ Слишком много запросов! Пожалуйста, подождите немного.",
                    parse_mode="HTML"
                )
            elif event.callback_query:
                await event.callback_query.answer(
                    "⚠️ Слишком много запросов!",
                    show_alert=True
                )
            return
        
        # Вызываем обработчик
        return await handler(event, data)
    
    def _determine_request_type(self, event: Update) -> str:
        """Определяет тип запроса на основе содержимого"""
        
        # Сообщения
        if event.message:
            message = event.message
            
            # Фото
            if message.photo:
                return 'photo_upload'
            
            # Голос
            if message.voice:
                return 'voice_transcription'
            
            # Команды
            if message.text and message.text.startswith('/'):
                command = message.text.lower()
                
                # AI команды
                if any(cmd in command for cmd in ['/ai', '/ask', '/question']):
                    return 'ai_requests'
                
                # Команды профиля
                if any(cmd in command for cmd in ['/profile', '/set_profile']):
                    return 'profile_updates'
                
                # Команды веса
                if any(cmd in command for cmd in ['/weight', '/log_weight']):
                    return 'weight_updates'
                
                # Остальные команды
                return 'general'
            
            # Текстовые сообщения
            if message.text:
                text = message.text.lower()
                
                # AI запросы
                if any(keyword in text for keyword in ['?', 'как', 'что', 'почему', 'когда', 'где']):
                    return 'ai_requests'
                
                # Запись еды
                if any(keyword in text for keyword in ['съел', 'ел', 'калории', 'ккал']):
                    return 'food_logging'
                
                # Запись воды
                if any(keyword in text for keyword in ['выпил', 'вода', 'мл', 'литр']):
                    return 'water_logging'
                
                # Запись активности
                if any(keyword in text for keyword in ['тренировка', 'спорт', 'активность', 'калорий сожжено']):
                    return 'activity_logging'
                
                # По умолчанию
                return 'general'
        
        # Callback queries
        elif event.callback_query:
            callback = event.callback_query
            data = callback.data.lower()
            
            # AI ассистент
            if 'ai' in data or 'ask' in data:
                return 'ai_requests'
            
            # Фото
            if 'photo' in data or 'analyze' in data:
                return 'photo_upload'
            
            # Профиль
            if 'profile' in data or 'edit' in data:
                return 'profile_updates'
            
            # Вес
            if 'weight' in data:
                return 'weight_updates'
            
            # Прогресс
            if 'progress' in data or 'stats' in data:
                return 'general'
            
            # По умолчанию
            return 'general'
        
        # По умолчанию
        return 'general'
