import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Union

logger = logging.getLogger(__name__)

def SmartRateLimitMiddleware(rate_limiter, is_global: bool = False):
    """Фабрика middleware для aiogram 3.x"""
    
    class _SmartRateLimitMiddleware(BaseMiddleware):
        def __init__(self):
            self.rate_limiter = rate_limiter
            self.is_global = is_global

        async def __call__(
            self,
            handler: Callable,
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
        ) -> Any:
            # Определяем пользователя
            user_id = None
            if isinstance(event, Message):
                user_id = event.from_user.id
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id

            if not user_id:
                return await handler(event, data)

            # Глобальный лимит – без параметров
            if self.is_global:
                if not await self.rate_limiter.is_allowed():
                    logger.warning("Global rate limit exceeded")
                    return
            else:
                # Пользовательский лимит – с типом запроса
                request_type = self._determine_request_type(event)
                if not await self.rate_limiter.is_allowed(user_id, request_type):
                    logger.warning(f"Rate limit exceeded for user {user_id}, type: {request_type}")
                    if isinstance(event, Message):
                        await event.answer(
                            "⚠️ Слишком много запросов! Пожалуйста, подождите немного.",
                            parse_mode="HTML"
                        )
                    elif isinstance(event, CallbackQuery):
                        await event.answer(
                            "⚠️ Слишком много запросов!",
                            show_alert=True
                        )
                    return

            return await handler(event, data)

        def _determine_request_type(self, event: Union[Message, CallbackQuery]) -> str:
            """Определяет тип запроса для пользовательского лимита"""
            if isinstance(event, Message):
                message = event
                # Фото
                if message.photo:
                    return 'photo_upload'
                # Голос
                if message.voice:
                    return 'voice_transcription'
                # Команды
                if message.text and message.text.startswith('/'):
                    command = message.text.lower()
                    if any(cmd in command for cmd in ['/ai', '/ask', '/question']):
                        return 'ai_requests'
                    if any(cmd in command for cmd in ['/profile', '/set_profile']):
                        return 'profile_updates'
                    if any(cmd in command for cmd in ['/weight', '/log_weight']):
                        return 'weight_updates'
                    return 'general'
                # Текст
                if message.text:
                    text = message.text.lower()
                    if any(keyword in text for keyword in ['?', 'как', 'что', 'почему']):
                        return 'ai_requests'
                    if any(keyword in text for keyword in ['съел', 'ел', 'калории', 'ккал']):
                        return 'food_logging'
                    if any(keyword in text for keyword in ['выпил', 'вода', 'мл']):
                        return 'water_logging'
                    if any(keyword in text for keyword in ['тренировка', 'спорт', 'активность']):
                        return 'activity_logging'
                    return 'general'
                return 'general'
            elif isinstance(event, CallbackQuery):
                data = event.data.lower()
                if 'ai' in data or 'ask' in data:
                    return 'ai_requests'
                if 'photo' in data or 'analyze' in data:
                    return 'photo_upload'
                if 'profile' in data or 'edit' in data:
                    return 'profile_updates'
                if 'weight' in data:
                    return 'weight_updates'
                return 'general'
            return 'general'

    return _SmartRateLimitMiddleware()
