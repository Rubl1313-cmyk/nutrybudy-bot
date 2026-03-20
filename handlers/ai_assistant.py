"""
handlers/ai_assistant.py
Диалоговый AI ассистент
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from sqlalchemy import select

from database.db import get_session
from database.models import User
from services.cloudflare_manager import cf_manager
from keyboards.reply import get_main_keyboard
from utils.premium_templates import loading_card, error_card

logger = logging.getLogger(__name__)
router = Router()

class AIStates(StatesGroup):
    """Состояния для диалога с AI"""
    in_conversation = State()

@router.message(Command("ask"))
@router.message(Command("спросить"))
async def cmd_ask(message: Message, state: FSMContext):
    """Начать диалог с AI ассистентом"""
    await state.clear()
    await state.set_state(AIStates.in_conversation)
    await state.update_data(conversation_history=[])  # Инициализируем историю
    
    text = "🤖 <b>AI Ассистент NutriBuddy</b>\n\n"
    text += "Я ваш персональный помощник по питанию и фитнесу!\n\n"
    text += "📝 <b>Что я могу помочь:</b>\n"
    text += "• Рассчитать калорийность блюд\n"
    text += "• Дать рекомендации по питанию\n"
    text += "• Подсказать упражнения\n"
    text += "• Ответить на вопросы о здоровье\n"
    text += "• Помочь с выбором продуктов\n\n"
    text += "💬 <b>Задайте ваш вопрос:</b>"
    
    await message.answer(text)

@router.message(AIStates.in_conversation)
async def handle_ai_conversation(message: Message, state: FSMContext):
    """Обработка сообщений в диалоге с AI"""
    user_question = message.text
    
    # Показываем индикатор загрузки
    loading_msg = await message.answer(loading_card("AI думает над ответом..."))
    
    try:
        # Получаем данные пользователя для контекста
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
        
        # Получаем историю диалога
        data = await state.get_data()
        conversation_history = data.get('conversation_history', [])
        
        # Формируем контекст для AI
        context = build_ai_context(user, conversation_history)
        
        # Получаем ответ от AI
        ai_response = await cf_manager.get_assistant_response(
            user_message=user_question,
            context=context
        )
        
        # Обновляем историю диалога
        conversation_history.append({
            'user': user_question,
            'assistant': ai_response,
            'timestamp': message.date.isoformat()
        })
        
        # Ограничиваем историю последними 10 сообщениями
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        await state.update_data(conversation_history=conversation_history)
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Формируем красивый ответ
        response_text = f"🤖 <b>AI Ассистент</b>\n\n"
        response_text += f"{ai_response}\n\n"
        response_text += "💡 <i>Хотите задать еще вопрос?</i>"
        
        await message.answer(response_text)
        
    except Exception as e:
        logger.error(f"Error in AI conversation: {e}")
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Очищаем состояние, чтобы пользователь не застрял в AI режиме
        await state.clear()
        
        await message.answer(
            "❌ Произошла ошибка при обработке запроса. Диалог завершён.\n"
            "Вы можете начать новый диалог командой /ask"
        )

@router.message(Command("stop"))
@router.message(Command("стоп"))
async def cmd_stop_conversation(message: Message, state: FSMContext):
    """Завершить диалог с AI"""
    current_state = await state.get_state()
    
    if current_state == AIStates.in_conversation:
        await state.clear()
        
        text = "👋 <b>Диалог завершен</b>\n\n"
        text += "Спасибо за использование AI ассистента!\n"
        text += "Всегда рад помочь снова. Используйте /ask для начала нового диалога."
        
        await message.answer(text, reply_markup=get_main_keyboard())
    else:
        await message.answer("❌ Нет активного диалога")

@router.callback_query(F.data == "continue_ai_chat")
async def callback_continue_ai_chat(callback: CallbackQuery):
    """Продолжить диалог с AI"""
    text = "💬 <b>Продолжаем диалог</b>\n\n"
    text += "Задайте ваш следующий вопрос:"
    
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "end_ai_chat")
async def callback_end_ai_chat(callback: CallbackQuery, state: FSMContext):
    """Завершить диалог с AI"""
    await state.clear()
    
    text = "👋 <b>Диалог завершен</b>\n\n"
    text += "Спасибо за использование AI ассистента!\n"
    text += "Всегда рад помочь снова. Используйте /ask для начала нового диалога."
    
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())
    await callback.answer()

def build_ai_context(user: User, conversation_history: list) -> str:
    """Построить контекст для AI на основе данных пользователя и истории"""
    context = "Ты - AI ассистент NutriBuddy, эксперт по питанию и фитнесу.\n\n"
    
    if user:
        context += f"Данные пользователя:\n"
        context += f"- Имя: {user.first_name or 'Пользователь'}\n"
        context += f"- Возраст: {user.age} лет\n"
        context += f"- Вес: {user.weight} кг\n"
        context += f"- Рост: {user.height} см\n"
        context += f"- Пол: {user.gender}\n"
        context += f"- Уровень активности: {user.activity_level}\n"
        context += f"- Цель: {user.goal}\n"
        
        if user.daily_calorie_goal:
            context += f"- Дневная норма калорий: {user.daily_calorie_goal} ккал\n"
        if user.daily_protein_goal:
            context += f"- Дневная норма белка: {user.daily_protein_goal} г\n"
        if user.daily_fat_goal:
            context += f"- Дневная норма жиров: {user.daily_fat_goal} г\n"
        if user.daily_carbs_goal:
            context += f"- Дневная норма углеводов: {user.daily_carbs_goal} г\n"
        
        context += "\n"
    
    if conversation_history:
        context += "История диалога (последние сообщения):\n"
        for msg in conversation_history[-3:]:  # Последние 3 сообщения для контекста
            context += f"Пользователь: {msg['user']}\n"
            context += f"Ассистент: {msg['assistant']}\n\n"
    
    context += """
Правила:
1. Отвечай на русском языке
2. Будь дружелюбным и поддерживающим
3. Давай практические и обоснованные советы
4. Учитывай персональные данные пользователя
5. Если вопрос не по теме питания/фитнеса, вежливо перенаправь к теме
6. Не давай медицинских диагнозов, рекомендуй консультацию с врачом при необходимости
"""
    
    return context

@router.message(Command("ai_help"))
@router.message(Command("помощь_ai"))
async def cmd_ai_help(message: Message):
    """Помощь по использованию AI ассистента"""
    text = "🤖 <b>Помощь AI ассистента</b>\n\n"
    text += "📝 <b>Команды:</b>\n"
    text += "• /ask или /спросить - начать диалог с AI\n"
    text += "• /stop или /стоп - завершить диалог\n"
    text += "• /ai_help или /помощь_ai - эта справка\n\n"
    text += "💡 <b>Примеры вопросов:</b>\n"
    text += "• Сколько калорий в гречке с курицей?\n"
    text += "• Какие упражнения для пресса эффективны?\n"
    text += "• Помоги составить меню на день\n"
    text += "• Какой белок лучше для набора массы?\n"
    text += "• Сколько воды нужно пить в день?\n\n"
    text += "⚡ <b>Советы:</b>\n"
    text += "• Будьте конкретны в вопросах\n"
    text += "• Укажите свои параметры для точных рекомендаций\n"
    text += "• Можно спрашивать про рецепты и подсчет калорий\n"
    text += "• AI помнит контекст диалога\n\n"
    text += "🚀 <b>Начните диалог:</b> /ask"
    
    await message.answer(text)
