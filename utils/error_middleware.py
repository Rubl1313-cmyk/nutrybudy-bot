"""
Middleware для перехвата необработанных ошибок
"""
import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from keyboards.main_menu import get_main_menu

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseMiddleware):
    """Middleware для перехвата необработанных ошибок"""
    
    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Unhandled error in {handler.__name__}: {e}", exc_info=True)
            
            # Отправляем пользователю сообщение об ошибке
            if isinstance(event, Message):
                await event.answer(
                    "⚠️ Произошла непредвиденная ошибка. Попробуйте позже или обратитесь к разработчику.",
                    reply_markup=get_main_menu()
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⚠️ Произошла ошибка при обработке нажатия. Попробуйте позже.",
                    show_alert=True
                )
            
            # Не пробрасываем исключение дальше, чтобы aiogram обработал его
            return None
