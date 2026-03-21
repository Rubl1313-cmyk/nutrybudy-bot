"""
handlers/universal.py
Универсальный обработчик всех сообщений с автоопределением намерений через LangChain
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, FoodEntry, DrinkEntry, ActivityEntry
from services.langchain_agent import get_agent
from keyboards.main_menu import get_main_menu

logger = logging.getLogger(__name__)
router = Router()

# Состояния для FSM
class UniversalStates:
    waiting_for_confirmation = "waiting_for_confirmation"

@router.message(~F.command)
async def universal_message_handler(message: Message, state: FSMContext):
    """
    Универсальный обработчик всех текстовых сообщений
    Автоопределяет намерение через LangChain и выполняет действие
    """
    user_id = message.from_user.id
    user_text = message.text
    
    # Проверяем, не находится ли пользователь в другом диалоге (AI Ассистент)
    current_state = await state.get_state()
    if current_state == "ai_conversation":
        return  # Пропускаем, это обрабатывает AI Ассистент
    
    try:
        # Показываем индикатор загрузки
        loading_msg = await message.answer("🤖 Анализирую...")
        
        # Получаем агента для пользователя
        agent = await get_agent(user_id, state)
        
        # Обрабатываем сообщение через агента
        result = await agent.process_message(user_text)
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Выводим результат
        await message.answer(result, reply_markup=get_main_menu(), parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in universal handler: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при обработке. Попробуйте ещё раз.",
            reply_markup=get_main_menu()
        )

@router.message(F.photo)
async def universal_photo_handler(message: Message, state: FSMContext):
    """
    Обработчик фотографий еды
    """
    user_id = message.from_user.id
    
    try:
        # Показываем индикатор загрузки
        loading_msg = await message.answer("📸 Анализирую фото...")
        
        # Получаем фото
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        photo_data = await message.bot.download_file(file_info.file_path)
        
        # Получаем агента
        agent = await get_agent(user_id, state)
        
        # Обрабатываем фото
        result = await agent.process_photo(user_id, photo_data.read(), "photo.jpg")
        
        await loading_msg.delete()
        
        if result.get('success'):
            await message.answer(result['message'], reply_markup=get_main_menu(), parse_mode="HTML")
        else:
            await message.answer(
                "❌ Не удалось распознать еду на фото. Попробуйте отправить другое фото.",
                reply_markup=get_main_menu()
            )
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при обработке фото. Попробуйте ещё раз.",
            reply_markup=get_main_menu()
        )
