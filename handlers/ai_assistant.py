"""
handlers/ai_assistant.py
AI Ассистент с поддержкой диалога до 50 сообщений и автоопределением намерений
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from sqlalchemy import select

from database.db import get_session
from database.models import User
from services.cloudflare_manager import cf_manager
from services.ai_processor import ai_processor
from keyboards.main_menu import get_main_menu

logger = logging.getLogger(__name__)
router = Router()

# Состояния для AI ассистента
class AIStates(StatesGroup):
    in_conversation = State()

# Команды для выхода из диалога
EXIT_COMMANDS = ["выход", "выйти", "стоп", "хватит", "закончить", "завершить", "отмена", "главное меню"]

@router.message(Command("ask"))
@router.message(F.text.lower().in_(["🤖 ai ассистент", "ai ассистент"]))
async def cmd_ai_assistant(message: Message, state: FSMContext):
    """Начать диалог с AI ассистентом"""
    await state.clear()
    await state.set_state(AIStates.in_conversation)
    
    # Инициализируем историю диалога
    await state.update_data(
        conversation_history=[],
        message_count=0
    )
    
    text = "🤖 <b>AI Ассистент NutriBuddy</b>\n\n"
    text += "Я ваш персональный помощник по питанию, фитнесу и здоровью!\n\n"
    text += "💬 <b>Что я умею:</b>\n"
    text += "• Отвечать на вопросы о питании и здоровье\n"
    text += "• Помогать с расчётом КБЖУ\n"
    text += "• Давать рекомендации по тренировкам\n"
    text += "• Отвечать на вопросы о погоде\n"
    text += "• Помогать с использованием бота\n\n"
    text += "📝 <b>Просто напишите ваш вопрос!</b>\n\n"
    text += "ℹ️ <i>Для выхода напишите «выход» или «выйти»</i>"
    
    await message.answer(text, parse_mode="HTML")

@router.message(AIStates.in_conversation)
async def handle_ai_message(message: Message, state: FSMContext):
    """Обработка сообщений в диалоге с AI"""
    user_text = message.text.strip().lower()
    
    # Проверяем команды выхода
    if user_text in EXIT_COMMANDS:
        await state.clear()
        await message.answer(
            "👋 Диалог завершён. Возвращаюсь в главное меню.",
            reply_markup=get_main_menu()
        )
        return
    
    # Показываем индикатор загрузки
    loading_msg = await message.answer("🤖 AI думает...")
    
    try:
        # Получаем данные пользователя
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
        
        # Получаем историю диалога
        data = await state.get_data()
        conversation_history = data.get('conversation_history', [])
        message_count = data.get('message_count', 0)
        
        # Проверяем лимит сообщений (50)
        if message_count >= 50:
            await state.clear()
            await message.answer(
                "📝 <b>Достигнут лимит сообщений в диалоге (50)</b>\n\n"
                "Начните новый диалог командой /ask или нажмите «🤖 AI Ассистент»",
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
            return
        
        # Формируем контекст для AI
        context = build_ai_context(user, conversation_history)
        
        # Получаем ответ от AI
        ai_response = await cf_manager.get_assistant_response(
            user_message=message.text,
            context=context
        )
        
        # Обновляем историю диалога
        conversation_history.append({
            'user': message.text,
            'assistant': ai_response,
            'timestamp': message.date.isoformat()
        })
        
        # Ограничиваем историю последними 20 сообщениями (для экономии токенов)
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        # Увеличиваем счётчик сообщений
        message_count += 1
        
        await state.update_data(
            conversation_history=conversation_history,
            message_count=message_count
        )
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Формируем ответ
        response_text = f"🤖 <b>AI Ассистент</b> ({message_count}/50)\n\n"
        response_text += f"{ai_response}\n\n"
        response_text += "💡 <i>Хотите задать ещё вопрос? Просто напишите!</i>\n"
        response_text += "ℹ️ <i>Для выхода напишите «выход»</i>"
        
        await message.answer(response_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in AI conversation: {e}", exc_info=True)
        await loading_msg.delete()
        await message.answer(
            "❌ Произошла ошибка при обработке запроса. Попробуйте ещё раз.",
            reply_markup=get_main_menu()
        )

def build_ai_context(user, conversation_history):
    """Строит контекст для AI"""
    context = "Вы — AI ассистент NutriBuddy, помощник по питанию и здоровью.\n\n"
    
    if user:
        context += "Информация о пользователе:\n"
        context += f"• Имя: {user.first_name or 'Не указано'}\n"
        context += f"• Возраст: {user.age or 'Не указан'} лет\n"
        context += f"• Пол: {user.gender or 'Не указан'}\n"
        context += f"• Рост: {user.height or 'Не указан'} см\n"
        context += f"• Вес: {user.weight or 'Не указан'} кг\n"
        context += f"• Цель: {user.goal or 'Не указана'}\n"
        context += f"• Активность: {user.activity_level or 'Не указана'}\n"
        context += f"• Норма калорий: {user.daily_calorie_goal or 'Не указана'} ккал\n"
        context += f"• Норма белков: {user.daily_protein_goal or 'Не указана'} г\n"
        context += f"• Норма жиров: {user.daily_fat_goal or 'Не указана'} г\n"
        context += f"• Норма углеводов: {user.daily_carb_goal or 'Не указана'} г\n"
        context += f"• Норма воды: {user.daily_water_goal or 'Не указана'} мл\n\n"
    
    if conversation_history:
        context += "История диалога:\n"
        for msg in conversation_history[-5:]:  # Последние 5 сообщений
            context += f"Пользователь: {msg['user']}\n"
            context += f"Ассистент: {msg['assistant']}\n"
        context += "\n"
    
    context += "Отвечайте кратко, по делу, используйте эмодзи для наглядности."
    
    return context
