"""
handlers/reply_handlers.py
Обработчики для новых reply-кнопок
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)
router = Router()

# Обработчики для основных кнопок

@router.message(F.text.contains("🍽️ Записать приём пищи"))
async def food_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки записи еды"""
    await state.clear()
    await message.answer(
        "🍽️ <b>Запись приема пищи</b>\n\n"
        "💡 <b>Как это работает:</b>\n"
        "• Отправьте фото блюда — я распознаю продукты\n"
        "• Или опишите еду текстом\n\n"
        "📝 <b>Примеры:</b>\n"
        "• «200г куриной грудки с гречкой»\n"
        "• «Овсянка на молоке с бананом»\n"
        "• «Салат с тунцом и овощами»\n\n"
        "📸 <b>Отправьте фото или напишите что съели:</b>",
        parse_mode="HTML"
    )

@router.message(F.text.contains("💧 Записать воду"))
async def water_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки записи воды"""
    await state.clear()
    await message.answer(
        "💧 <b>Запись потребления воды</b>\n\n"
        "💡 <b>Напишите сколько выпили:</b>\n\n"
        "📝 <b>Примеры:</b>\n"
        "• «250 мл»\n"
        "• «2 стакана»\n"
        "• «1.5 литра»\n"
        "• «500 мл»\n\n"
        "🔍 <b>Или выберите быстрый вариант:</b>",
        parse_mode="HTML"
    )
    
    # Показываем быстрые варианты
    from keyboards.reply_v2 import get_water_keyboard
    await message.answer(
        "⚡ <b>Быстрые варианты:</b>",
        reply_markup=get_water_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("🤖 Спросить AI"))
async def ai_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки AI ассистента"""
    from handlers.ai_assistant import cmd_ask
    await cmd_ask(message, state)

@router.message(F.text.contains("📊 Прогресс"))
async def progress_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки прогресса"""
    await state.clear()
    from keyboards.inline import get_progress_menu
    await message.answer(
        "📊 <b>Выберите период для статистики:</b>",
        reply_markup=get_progress_menu(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("Профиль"))
async def profile_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки профиля"""
    await state.clear()
    from handlers.profile import cmd_profile
    await cmd_profile(message, state)

@router.message(F.text.contains("❓ Помощь"))
async def help_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки помощи"""
    await state.clear()
    from handlers.common import cmd_help
    await cmd_help(message, state)

# Обработчики для быстрых действий

@router.message(F.text == "⚖️ Записать вес")
async def weight_quick_handler(message: Message, state: FSMContext):
    """Быстрая запись веса"""
    await state.clear()
    await message.answer(
        "⚖️ <b>Запись веса</b>\n\n"
        "💡 <b>Напишите ваш вес:</b>\n\n"
        "📝 <b>Примеры:</b>\n"
        "• «70.5 кг»\n"
        "• «Вес 72»\n"
        "• «68.2»\n\n"
        "⚠️ <b>Записывайте вес в одно и то же время!</b>",
        parse_mode="HTML"
    )

@router.message(F.text == "🏃 Активность")
async def activity_quick_handler(message: Message, state: FSMContext):
    """Быстрая запись активности"""
    await state.clear()
    await message.answer(
        "🏃 <b>Запись активности</b>\n\n"
        "💡 <b>Опишите вашу активность:</b>\n\n"
        "📝 <b>Примеры:</b>\n"
        "• «Пробежал 5 км»\n"
        "• «Тренировка 45 минут»\n"
        "• «10000 шагов»\n"
        "• «Йога 30 минут»\n\n"
        "⚡ <b>Или выберите тип активности:</b>",
        parse_mode="HTML"
    )
    
    # Показываем быстрые варианты
    from keyboards.reply_v2 import get_activity_keyboard
    await message.answer(
        "⚡ <b>Быстрые варианты:</b>",
        reply_markup=get_activity_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "🌦️ Погода")
async def weather_quick_handler(message: Message, state: FSMContext):
    """Быстрый запрос погоды"""
    await state.clear()
    from handlers.ai_assistant import cmd_weather
    await cmd_weather(message, state)

# Обработчики для быстрых вариантов воды

@router.message(F.text.startswith("💧"))
async def water_quick_variants(message: Message, state: FSMContext):
    """Обработчики быстрых вариантов воды"""
    text = message.text
    
    # Парсим количество из кнопки
    if "1 стакан" in text:
        amount = 250
    elif "2 стакана" in text:
        amount = 500
    elif "500 мл" in text:
        amount = 500
    elif "1 литр" in text:
        amount = 1000
    else:
        return  # Не обрабатываем другие кнопки
    
    # Вызываем обработчик воды
    from services.tool_caller import ToolCaller
    await ToolCaller.handle_log_water(f"выпил {amount} мл", message.from_user.id, message, state)

# Обработчики для быстрых вариантов активности

@router.message(F.text.startswith("🏃"))
@router.message(F.text.startswith("🚶"))
@router.message(F.text.startswith("🏋️"))
@router.message(F.text.startswith("🧘"))
async def activity_quick_variants(message: Message, state: FSMContext):
    """Обработчики быстрых вариантов активности"""
    text = message.text
    
    # Определяем тип активности
    activity_map = {
        "🏃 Бег": "бег 30 минут",
        "🚶 Ходьба": "ходьба 45 минут", 
        "🏋️ Тренировка": "тренировка 45 минут",
        "🧘 Йога": "йога 30 минут"
    }
    
    for button_text, activity_text in activity_map.items():
        if button_text in text:
            # Вызываем обработчик активности
            from services.tool_caller import ToolCaller
            await ToolCaller.handle_log_activity(activity_text, message.from_user.id, message, state)
            break

# Обработчики для AI быстрых запросов

@router.message(F.text == "🌦️ Погода")
async def ai_weather_handler(message: Message, state: FSMContext):
    """Запрос погоды через AI"""
    from handlers.ai_assistant import cmd_weather
    await cmd_weather(message, state)

@router.message(F.text == "🍳 Рецепт")
async def ai_recipe_handler(message: Message, state: FSMContext):
    """Запрос рецепта через AI"""
    from handlers.ai_assistant import cmd_recipe
    await cmd_recipe(message, state)

@router.message(F.text == "🧮 Рассчитать КБЖУ")
async def ai_calculate_handler(message: Message, state: FSMContext):
    """Расчет КБЖУ через AI"""
    from handlers.ai_assistant import cmd_calculate
    await cmd_calculate(message, state)

@router.message(F.text == "💬 Общий вопрос")
async def ai_general_handler(message: Message, state: FSMContext):
    """Общий вопрос к AI"""
    await message.answer(
        "💬 <b>Задайте ваш вопрос:</b>\n\n"
        "💡 <b>Примеры:</b>\n"
        "• «Сколько калорий в авокадо?»\n"
        "• «Полезна ли гречка на ужин?»\n"
        "• «Какие продукты богаты белком?»\n"
        "• «Посоветуй легкий ужин»\n\n"
        "❌ Напишите «выход» для завершения диалога",
        parse_mode="HTML"
    )
    
    # Включаем режим диалога
    from handlers.ai_assistant import cmd_ask
    await cmd_ask(message, state)

# Обработчики навигации

@router.message(F.text == "🔙 Главное меню")
async def back_to_main_handler(message: Message, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    from keyboards.reply_v2 import get_main_keyboard_v2
    await message.answer(
        "🏠 <b>Главное меню</b>",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text == "📝 Редактировать профиль")
async def edit_profile_handler(message: Message, state: FSMContext):
    """Редактирование профиля"""
    from handlers.profile import cmd_set_profile
    await cmd_set_profile(message, state)

@router.message(F.text == "🧬 Полный анализ")
async def full_analysis_handler(message: Message, state: FSMContext):
    """Полный анализ тела"""
    await state.clear()
    
    from database.db import get_session
    from database.models import User, WeightEntry
    from sqlalchemy import select
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Сначала создайте профиль командой /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Получаем предыдущие веса для тренда
        weights_result = await session.execute(
            select(WeightEntry.weight).where(
                WeightEntry.user_id == user.id
            ).order_by(WeightEntry.datetime.desc()).limit(10)
        )
        previous_weights = [row[0] for row in weights_result.fetchall()]
        
        # Формируем анализ
        from utils.body_templates import get_body_analysis_text
        analysis_text = get_body_analysis_text(user, previous_weights)
        
        await message.answer(
            analysis_text,
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )
