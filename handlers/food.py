"""
Food handling - delegates to AI processor
"""
from aiogram import types
from aiogram.fsm.context import FSMContext
from services.ai_processor import ai_processor
from database.db import get_session
from database.models import User
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

async def cmd_log_food(message: types.Message, state: FSMContext, user_id: int = None):
    """Handle food logging command - delegates to AI processor"""
    if user_id is None:
        user_id = message.from_user.id
    
    # Use AI processor to understand intent (though command is explicit)
    # For simplicity, we'll ask user to describe food
    await message.answer(
        "🍽️ Опишите, что вы съели (например: '200г курицы с рисом' или отправьте фото):"
    )
    # In a full implementation, we'd set a state to wait for food description
    # For now, just inform user they can use AI handler
    await message.answer(
        "💡 Вы также можете просто отправить сообщение с описанием еды или фото, "
        "и я автоматически обработаю его через ИИ."
    )