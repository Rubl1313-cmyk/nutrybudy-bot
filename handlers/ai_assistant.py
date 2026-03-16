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

logger = logging.getLogger(__name__)
router = Router()

class AIStates(StatesGroup):
    """Состояния для диалога с AI"""
    in_conversation = State()

@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    """Начать диалог с AI ассистентом"""
    await state.clear()
    await state.set_state(AIStates.in_conversation)
    await state.update_data(conversation_history=[])  # Инициализируем историю
    
    await message.answer(
        "🤖 <b>AI ассистент</b>\n\n"
        "Я готов помочь вам с вопросами о питании, тренировках, здоровье и многом другом!\n\n"
        "💡 <b>Что я могу:</b>\n"
        "• Рассчитать КБЖУ блюд\n"
        "• Дать рекомендации по питанию\n"
        "• Подсказать рецепты\n"
        "• Рассказать о погоде\n"
        "• Помочь с тренировками\n\n"
        "📝 <b>Задайте ваш вопрос:</b>\n\n"
        "❌ Для выхода напишите \"выход\" или /cancel",
        parse_mode="HTML"
    )

@router.message(AIStates.in_conversation)
async def process_ai_question(message: Message, state: FSMContext):
    """Обработка вопросов к AI"""
    user_question = message.text.strip()
    
    # Проверка на выход
    if user_question.lower() in ["выход", "exit", "quit", "/cancel"]:
        await state.clear()
        await message.answer(
            "👋 <b>Диалог завершен</b>\n\n"
            "Всегда рад помочь! Используйте /ask для нового диалога.",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        return
    
    try:
        # Получаем историю диалога
        state_data = await state.get_data()
        conversation_history = state_data.get('conversation_history', [])
        
        # Получаем информацию о пользователе для контекста
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            # Формируем профиль пользователя для AI
            user_profile = None
            if user and user.weight and user.height and user.age:
                user_profile = {
                    'name': user.first_name or 'Anonymous',
                    'weight': user.weight,
                    'height': user.height,
                    'age': user.age,
                    'gender': user.gender,
                    'goal': user.goal,
                    'daily_calories': user.daily_calorie_goal,
                    'daily_protein': user.daily_protein_goal,
                    'daily_fat': user.daily_fat_goal,
                    'daily_carbs': user.daily_carbs_goal,
                    'city': user.city
                }
        
        # Отправляем "печатает..."
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        # Запрос к AI с правильными параметрами и историей
        response_dict = await cf_manager.ai_assistant(
            message=user_question,
            history=conversation_history,  # Передаем историю
            user_profile=user_profile
        )
        
        response = response_dict.get('response', 'Извините, произошла ошибка')
        
        # Обновляем историю диалога
        conversation_history.append({
            'role': 'user',
            'message': user_question
        })
        conversation_history.append({
            'role': 'assistant', 
            'message': response
        })
        
        # Ограничиваем историю последними 10 сообщениями (5 пар)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        await state.update_data(conversation_history=conversation_history)
        
        await message.answer(
            f"🤖 <b>AI ассистент:</b>\n\n{response}\n\n"
            f"💡 <b>Продолжайте диалог!</b>\n"
            f"❌ Напишите \"выход\" для завершения",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке AI вопроса: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте переформулировать вопрос.\n\n"
            "❌ Или напишите \"выход\" для завершения диалога.",
            parse_mode="HTML"
        )

@router.message(Command("ai"))
async def cmd_ai(message: Message, state: FSMContext):
    """Альтернативная команда для AI"""
    await cmd_ask(message, state)

@router.message(Command("weather"))
async def cmd_weather(message: Message, state: FSMContext):
    """Узнать погоду"""
    await state.clear()
    
    try:
        # Получаем город пользователя
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.city:
                await message.answer(
                    "❌ Указан город. Сначала настройте профиль командой /set_profile",
                    reply_markup=get_main_keyboard()
                )
                return
            
            city = user.city
            
            # Отправляем "печатает..."
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            # Запрос погоды через реальное API
            from services.weather import get_weather
            weather_data = await get_weather(city)
            
            if weather_data:
                temp = weather_data.get('temp', 'N/A')
                condition = weather_data.get('condition', 'неизвестно')
                humidity = weather_data.get('humidity', 'N/A')
                wind = weather_data.get('wind', 'N/A')
                
                response = (f"🌡️ <b>Температура:</b> {temp}°C\n"
                           f"☁️ <b>Состояние:</b> {condition}\n"
                           f"💧 <b>Влажность:</b> {humidity}%\n"
                           f"💨 <b>Ветер:</b> {wind} м/с")
            else:
                response = "Не удалось получить данные о погоде. Попробуйте позже."
            
            await message.answer(
                f"🌦️ <b>Погода в {city}</b>\n\n{response}",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении погоды: {e}")
        await message.answer(
            "❌ Не удалось получить погоду. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )

@router.message(Command("recipe"))
async def cmd_recipe(message: Message, state: FSMContext):
    """Получить рецепт"""
    await state.clear()
    
    await message.answer(
        "🍳 <b>Подбор рецепта</b>\n\n"
        "Напишите, какой рецепт вы хотите:\n\n"
        "Примеры:\n"
        "• Рецепт куриной грудки\n"
        "• Как приготовить пасту\n"
        "• Блюдо из гречки\n"
        "• Салат с курицей",
        parse_mode="HTML"
    )
    await state.set_state(AIStates.in_conversation)

@router.message(Command("calculate"))
async def cmd_calculate(message: Message, state: FSMContext):
    """Рассчитать КБЖУ блюда"""
    await state.clear()
    
    await message.answer(
        "🧮 <b>Расчет КБЖУ блюда</b>\n\n"
        "Опишите блюдо и его состав:\n\n"
        "Пример:\n"
        "Куриная грудка 200г, рис 100г, овощи 150г",
        parse_mode="HTML"
    )
    await state.set_state(AIStates.in_conversation)

@router.callback_query(F.data == "ai_assistant")
async def ai_assistant_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для AI ассистента из меню"""
    await callback.answer()
    await cmd_ask(callback.message, state)

@router.callback_query(F.data == "ask_weather")
async def ask_weather_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для погоды из меню"""
    await callback.answer()
    await cmd_weather(callback.message, state)

@router.callback_query(F.data == "get_recipe")
async def get_recipe_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для рецепта из меню"""
    await callback.answer()
    await cmd_recipe(callback.message, state)
