"""
handlers/profile.py
Обработчики профиля пользователя
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from sqlalchemy import select

from database.db import get_session
from database.models import User
from keyboards.reply import get_main_keyboard
from utils.states import ProfileStates

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    """Начало настройки профиля"""
    await state.clear()
    
    await message.answer(
        "👤 <b>Настройка профиля</b>\n\n"
        "Давайте настроим ваш персональный профиль для точного расчета КБЖУ.\n\n"
        "Начнем с основного:\n\n"
        "📏 <b>Ваш вес (в кг):</b>\n"
        "Например: 70.5",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.weight)

@router.message(ProfileStates.weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка веса"""
    try:
        weight = float(message.text.replace(",", "."))
        if weight < 30 or weight > 300:
            await message.answer(
                "❌ Вес должен быть от 30 до 300 кг. Попробуйте еще раз:"
            )
            return
        
        await state.update_data(weight=weight)
        await message.answer(
            "📏 <b>Ваш рост (в см):</b>\n"
            "Например: 175",
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.height)
        
    except ValueError:
        await message.answer("❌ Введите корректное число. Попробуйте еще раз:")

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    """Обработка роста"""
    try:
        height = int(message.text)
        if height < 100 or height > 250:
            await message.answer(
                "❌ Рост должен быть от 100 до 250 см. Попробуйте еще раз:"
            )
            return
        
        await state.update_data(height=height)
        await message.answer(
            "🎂 <b>Ваш возраст:</b>\n"
            "Например: 25",
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.age)
        
    except ValueError:
        await message.answer("❌ Введите корректное число. Попробуйте еще раз:")

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    """Обработка возраста"""
    try:
        age = int(message.text)
        if age < 10 or age > 120:
            await message.answer(
                "❌ Возраст должен быть от 10 до 120 лет. Попробуйте еще раз:"
            )
            return
        
        await state.update_data(age=age)
        
        # Клавиатура для выбора пола
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        await message.answer(
            "⚧️ <b>Ваш пол:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.gender)
        
    except ValueError:
        await message.answer("❌ Введите корректное число. Попробуйте еще раз:")

@router.message(ProfileStates.gender)
async def process_gender(message: Message, state: FSMContext):
    """Обработка пола"""
    gender = message.text.lower()
    
    if gender in ["мужской", "м"]:
        gender = "male"
    elif gender in ["женский", "ж"]:
        gender = "female"
    else:
        await message.answer("❌ Выберите 'Мужской' или 'Женский'")
        return
    
    await state.update_data(gender=gender)
    
    # Клавиатура для уровня активности
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Минимальная")],
            [KeyboardButton(text="Легкая")],
            [KeyboardButton(text="Умеренная")],
            [KeyboardButton(text="Высокая")],
            [KeyboardButton(text="Очень высокая")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "🏃 <b>Уровень активности:</b>\n\n"
        "• Минимальная - сидячая работа, нет тренировок\n"
        "• Легкая - легкие тренировки 1-3 раза в неделю\n"
        "• Умеренная - тренировки 3-5 раза в неделю\n"
        "• Высокая - интенсивные тренировки 6-7 раз в неделю\n"
        "• Очень высокая - физическая работа/профессиональный спорт",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.activity)

@router.message(ProfileStates.activity)
async def process_activity(message: Message, state: FSMContext):
    """Обработка уровня активности"""
    activity = message.text.lower()
    
    activity_map = {
        "минимальная": 1.2,
        "легкая": 1.375,
        "умеренная": 1.55,
        "высокая": 1.725,
        "очень высокая": 1.9
    }
    
    if activity not in activity_map:
        await message.answer("❌ Выберите один из предложенных вариантов")
        return
    
    activity_level = activity_map[activity]
    await state.update_data(activity_level=activity_level)
    
    # Клавиатура для цели
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Похудение")],
            [KeyboardButton(text="Поддержание")],
            [KeyboardButton(text="Набор массы")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "🎯 <b>Ваша цель:</b>\n\n"
        "• Похудение - дефицит калорий\n"
        "• Поддержание - баланс калорий\n"
        "• Набор массы - профицит калорий",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.goal)

@router.message(ProfileStates.goal)
async def process_goal(message: Message, state: FSMContext):
    """Обработка цели"""
    goal = message.text.lower()
    
    goal_map = {
        "похудение": "lose_weight",
        "поддержание": "maintain",
        "набор массы": "gain_weight"
    }
    
    if goal not in goal_map:
        await message.answer("❌ Выберите один из предложенных вариантов")
        return
    
    goal_type = goal_map[goal]
    await state.update_data(goal=goal_type)
    
    await message.answer(
        "🏙️ <b>Ваш город:</b>\n"
        "Нужен для определения погоды и учета климата в расчетах.\n\n"
        "Например: Москва",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.city)

@router.message(ProfileStates.city)
async def process_city(message: Message, state: FSMContext):
    """Обработка города и сохранение профиля"""
    city = message.text.strip()
    
    # Получаем все данные
    profile_data = await state.get_data()
    
    weight = profile_data['weight']
    height = profile_data['height']
    age = profile_data['age']
    gender = profile_data['gender']
    activity_level = profile_data['activity_level']
    goal = profile_data['goal']
    
    # Рассчитываем КБЖУ с использованием калькулятора
    from services.calculator import calculate_calorie_goal, calculate_water_goal
    
    nutrition_goals = calculate_calorie_goal(
        weight=weight,
        height=height, 
        age=age,
        gender=gender,
        activity_level=activity_level,
        goal=goal
    )
    
    # Распаковываем кортеж: (calories, protein_g, fat_g, carbs_g)
    daily_calorie_goal, daily_protein_goal, daily_fat_goal, daily_carbs_goal = nutrition_goals
    
    # Получаем реальную температуру для расчета воды
    temperature = 20.0  # По умолчанию
    try:
        from services.weather import get_temperature
        temperature = await get_temperature(city)
    except Exception as e:
        logger.warning(f"Не удалось получить температуру для {city}: {e}")
        temperature = 20.0
    
    water_goal = calculate_water_goal(
        weight=weight,
        activity_level=activity_level,
        temperature=temperature  # Реальная температура
    )
    daily_water_goal = water_goal
    
    # Сохраняем в базу данных
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.weight = weight
            user.height = height
            user.age = age
            user.gender = gender
            user.activity_level = activity_level
            user.goal = goal
            user.city = city
            user.daily_calorie_goal = round(daily_calorie_goal)
            user.daily_protein_goal = round(daily_protein_goal)
            user.daily_fat_goal = round(daily_fat_goal)
            user.daily_carbs_goal = round(daily_carbs_goal)
            user.daily_water_goal = round(daily_water_goal)
            
            await session.commit()
    
    await state.clear()
    
    await message.answer(
        f"✅ <b>Профиль успешно настроен!</b>\n\n"
        f"👤 <b>Ваши данные:</b>\n"
        f"📏 Вес: {weight} кг\n"
        f"📏 Рост: {height} см\n"
        f"🎂 Возраст: {age} лет\n"
        f"⚧️ Пол: {'Мужской' if gender == 'male' else 'Женский'}\n"
        f"🎯 Цель: {message.text}\n"
        f"🏙️ Город: {city}\n\n"
        f"📊 <b>Ваши нормы:</b>\n"
        f"🔥 Калории: {round(daily_calorie_goal)} ккал/день\n"
        f"🥩 Белки: {round(daily_protein_goal)} г/день\n"
        f"🧈 Жиры: {round(daily_fat_goal)} г/день\n"
        f"🍞 Углеводы: {round(daily_carbs_goal)} г/день\n"
        f"💧 Вода: {round(daily_water_goal)} мл/день\n\n"
        f"Теперь вы можете использовать все функции бота!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    """Просмотр текущего профиля"""
    await state.clear()
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Профиль не найден. Сначала настройте профиль командой /set_profile",
                reply_markup=get_main_keyboard()
            )
            return
        
        await message.answer(
            f"👤 <b>Ваш профиль</b>\n\n"
            f"📏 Вес: {user.weight} кг\n"
            f"📏 Рост: {user.height} см\n"
            f"🎂 Возраст: {user.age} лет\n"
            f"⚧️ Пол: {'Мужской' if user.gender == 'male' else 'Женский'}\n"
            f"🎯 Цель: {user.goal}\n"
            f"🏙️ Город: {user.city}\n\n"
            f"📊 <b>Ваши нормы:</b>\n"
            f"🔥 Калории: {user.daily_calorie_goal} ккал/день\n"
            f"🥩 Белки: {user.daily_protein_goal} г/день\n"
            f"🧈 Жиры: {user.daily_fat_goal} г/день\n"
            f"🍞 Углеводы: {user.daily_carbs_goal} г/день\n"
            f"💧 Вода: {user.daily_water_goal} мл/день\n\n"
            f"Для изменения профиля используйте /set_profile",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
