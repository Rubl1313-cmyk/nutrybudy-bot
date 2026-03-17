"""
handlers/food.py
Обработчики для записи еды
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from database.db import get_session
from database.models import User, MealEntry
from services.ai_processor import AIProcessor
from handlers.food_clarification import handle_food_text
from keyboards.reply_v2 import get_main_keyboard_v2

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    """Запись еды"""
    await state.clear()
    
    await message.answer(
        "🍽️ <b>Запись еды</b>\n\n"
        "Напишите, что вы съели:\n\n"
        "Примеры:\n"
        "• 200г гречки с курицей\n"
        "• салат цезарь\n"
        "• яблоко 2шт\n"
        "• омлет из 3 яиц\n\n"
        "📸 Можно отправить фото еды!",
        parse_mode="HTML"
    )

@router.message(F.text)
async def handle_food_message(message: Message, state: FSMContext):
    """Обработка текстовых сообщений о еде"""
    # Сначала пробуем обработать через food_clarification
    if await handle_food_text(message, state):
        return  # Если food_clarification обработал, выходим
    
    # Иначе пробуем через AI процессор
    try:
        user_id = message.from_user.id
        ai_processor = AIProcessor()
        
        result = await ai_processor.process_text_input(message.text, user_id)
        
        if result.get("success") and result.get("intent") == "log_food":
            # Если AI определил еду, обрабатываем через food_clarification
            if await handle_food_text(message, state):
                return
        
        # Если не еда, передаем в универсальный обработчик
        from handlers.universal import universal_handler
        await universal_handler(message, state)
        
    except Exception as e:
        logger.error(f"Error in handle_food_message: {e}")
        await message.answer(
            "❌ Ошибка при обработке. Попробуйте еще раз.",
            reply_markup=get_main_keyboard_v2()
        )
