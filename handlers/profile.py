"""
handlers/profile.py
Обработчики профиля пользователя
"""
import logging
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router, types
from sqlalchemy import select

from database.db import get_session
from database.models import User
from keyboards.reply_v2 import get_main_keyboard_v2, get_profile_keyboard
from keyboards.reply import get_gender_keyboard
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
    """Обработка веса с безопасным парсингом"""
    from utils.safe_parser import safe_parse_float
    
    weight, error = safe_parse_float(message.text, "вес")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "📏 <b>Примеры:</b>\n"
            "• 75.5\n"
            "• 80 кг\n"
            "• 72,3",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="❌ Отмена")]],
                resize_keyboard=True,
                one_time_keyboard=True
            ),
            parse_mode="HTML"
        )
        return
    
    await state.update_data(weight=weight)
    await message.answer(
        "📏 <b>Ваш рост (в см):</b>\n"
        "Например: 175",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.height)

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    """Обработка роста с безопасным парсингом"""
    from utils.safe_parser import safe_parse_int
    
    height, error = safe_parse_int(message.text, "рост")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "💡 <b>Примеры:</b>\n"
            "• 175\n"
            "• 180 см\n"
            "• 165",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(height=height)
    await message.answer(
        "🎂 <b>Ваш возраст:</b>\n"
        "Например: 25",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.age)

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    """Обработка возраста с безопасным парсингом"""
    from utils.safe_parser import safe_parse_int
    
    age, error = safe_parse_int(message.text, "возраст")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "💡 <b>Примеры:</b>\n"
            "• 25\n"
            "• 30 лет\n"
            "• 22",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(age=age)
    await message.answer(
        "⚧️ <b>Ваш пол:</b>\n\n"
        "Выберите из кнопок ниже:",
        parse_mode="HTML",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(ProfileStates.gender)

@router.message(ProfileStates.gender)
async def process_gender(message: Message, state: FSMContext):
    """Обработка пола"""
    gender_text = message.text.lower()
    
    if "мужской" in gender_text:
        gender = "male"
    elif "женский" in gender_text:
        gender = "female"
    else:
        await message.answer("❌ Выберите 'Мужской' или 'Женский'")
        return
    
    await state.update_data(gender=gender)
    
    # Далее код без изменений...
    if gender == "female":
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📐 Ввести обхват шеи", callback_data="add_neck")
        builder.button(text="⏭️ Пропустить шею", callback_data="skip_neck")
        builder.adjust(1)
        
        await message.answer(
            "📏 <b>Антропометрические данные</b>\n\n"
            "Для точного анализа жировой массы нужны обхваты.\n\n"
            "📐 <b>Обхват шеи (в см):</b>\n"
            "Или пропустите, нажав кнопку ниже:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_neck)
    elif gender == "male":
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📐 Ввести обхват запястья", callback_data="add_wrist")
        builder.button(text="⏭️ Пропустить запястье", callback_data="skip_wrist")
        builder.adjust(1)
        
        await message.answer(
            "📏 <b>Антропометрические данные</b>\n\n"
            "Для точного анализа мышечной массы и жира нужны обхваты.\n\n"
            "📐 <b>Обхват запястья (в см):</b>\n"
            "Или пропустите, нажав кнопку ниже:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_wrist)
    else:
        # Пропускаем антропометрию
        await show_activity_keyboard(message, state)

@router.message(ProfileStates.waiting_for_neck)
async def process_neck(message: Message, state: FSMContext):
    """Обработка обхвата шеи"""
    from utils.safe_parser import safe_parse_float
    
    # Проверяем, не хочет ли пользователь пропустить
    if message.text.lower() in ["пропустить", "пропуст", "skip", "далее"]:
        await message.answer(
            "📏 <b>Обхват талии (в см):</b>\n"
            "Например: 70",
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_waist)
        return
    
    neck, error = safe_parse_float(message.text, "обхват шеи")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "💡 <b>Примеры:</b>\n"
            "• 34\n"
            "• 35.5 см",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(neck_cm=neck)
    await message.answer(
        "📏 <b>Обхват талии (в см):</b>\n"
        "Например: 70",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_waist)

@router.message(ProfileStates.waiting_for_waist)
async def process_waist(message: Message, state: FSMContext):
    """Обработка обхвата талии"""
    from utils.safe_parser import safe_parse_float
    
    waist, error = safe_parse_float(message.text, "обхват талии")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "💡 <b>Примеры:</b>\n"
            "• 70\n"
            "• 68.5 см",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(waist_cm=waist)
    await message.answer(
        "📏 <b>Обхват бедер (в см):</b>\n"
        "Например: 95",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_hip)

@router.message(ProfileStates.waiting_for_hip)
async def process_hip(message: Message, state: FSMContext):
    """Обработка обхвата бедер"""
    from utils.safe_parser import safe_parse_float
    
    hip, error = safe_parse_float(message.text, "обхват бедер")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "💡 <b>Примеры:</b>\n"
            "• 95\n"
            "• 97.5 см",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(hip_cm=hip)
    
    # Переходим к активности
    await show_activity_keyboard(message, state)

@router.message(ProfileStates.waiting_for_wrist)
async def process_wrist(message: Message, state: FSMContext):
    """Обработка обхвата запястья для мужчин"""
    from utils.safe_parser import safe_parse_float
    
    # Проверяем, не хочет ли пользователь пропустить
    if message.text.lower() in ["пропустить", "пропуст", "skip", "далее"]:
        await message.answer(
            "💪 <b>Дополнительные замеры (необязательно)</b>\n\n"
            "Для более точного анализа можно добавить:\n\n"
            "📐 <b>Обхват бицепса (в см):</b>\n"
            "Например: 32\n\n"
            "Или напишите «Пропустить»",
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_bicep)
        return
    
    wrist, error = safe_parse_float(message.text, "обхват запястья")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "💡 <b>Примеры:</b>\n"
            "• 17\n"
            "• 18.5 см",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(wrist_cm=wrist)
# Для мужчин можно добавить еще обхваты по желанию
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📐 Ввести обхват бицепса", callback_data="add_bicep")
    builder.button(text="⏭️ Пропустить", callback_data="skip_measurements")
    builder.adjust(1)
    
    await message.answer(
        "💪 <b>Дополнительные замеры (необязательно)</b>\n\n"
        "Для более точного анализа можно добавить:\n\n"
        "📐 <b>Обхват бицепса (в см):</b>\n"
        "Или пропустите, нажав кнопку ниже:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_bicep)

@router.message(ProfileStates.waiting_for_bicep)
async def process_bicep(message: Message, state: FSMContext):
    """Обработка обхвата бицепса для мужчин"""
    from utils.safe_parser import safe_parse_float
    
    # Проверяем, не хочет ли пользователь пропустить
    if message.text.lower() in ["пропустить", "пропуст", "skip", "далее"]:
        await show_activity_keyboard(message, state)
        return
    
    bicep, error = safe_parse_float(message.text, "обхват бицепса")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "💡 <b>Примеры:</b>\n"
            "• 32\n"
            "• 33.5 см",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(bicep_cm=bicep)
    await show_activity_keyboard(message, state)


async def show_activity_keyboard(message: Message, state: FSMContext):
    """Показываем клавиатуру активности"""
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
        "• Высокая - интенсивные тренировки 5-6 раз в неделю\n"
        "• Очень высокая - ежедневные тренировки",
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
    await state.update_data(activity_level=activity)  # сохраняем строку, а не число
    
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
    """Обработка города и начало расширенной антропометрии"""
    city = message.text.strip()
    await state.update_data(city=city)
    
    # Начинаем расширенную антропометрию с обхвата груди
    await ask_measurement(
        message, state,
        "Обхват груди",
        ProfileStates.waiting_for_chest,
        "Измеряется на уровне сосков, в спокойном состоянии (не на вдохе). Лента горизонтально.",
        50, 200
    )

async def ask_measurement(message: Message, state: FSMContext, 
                        measurement_name: str, next_state: State, 
                        instruction: str, min_val: float, max_val: float):
    """Универсальная функция для запроса измерения"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏭️ Пропустить")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        f"📏 <b>Расширенная антропометрия</b>\n\n"
        f"📐 <b>{measurement_name} (в см):</b>\n\n"
        f"💡 <b>Инструкция:</b> {instruction}\n\n"
        f"Или нажмите «Пропустить», если нет сантиметровой ленты:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(next_state)

@router.message(ProfileStates.waiting_for_chest)
async def process_chest(message: Message, state: FSMContext):
    """Обработка обхвата груди"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["пропустить", "⏭️ пропустить"]:
        await state.update_data(chest_cm=None)
    else:
        chest, error = safe_parse_float(message.text, "обхват груди")
        if error or chest < 50 or chest > 200:
            await message.answer("❌ Некорректное значение. Попробуйте ещё раз или нажмите «Пропустить».")
            return
        await state.update_data(chest_cm=chest)
    
    # Следующий замер - обхват предплечья
    await ask_measurement(
        message, state,
        "Обхват предплечья",
        ProfileStates.waiting_for_forearm,
        "Самое широкое место предплечья (чуть ниже локтя). Рука расслаблена, висит свободно.",
        20, 50
    )

@router.message(ProfileStates.waiting_for_forearm)
async def process_forearm(message: Message, state: FSMContext):
    """Обработка обхвата предплечья"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["пропустить", "⏭️ пропустить"]:
        await state.update_data(forearm_cm=None)
    else:
        forearm, error = safe_parse_float(message.text, "обхват предплечья")
        if error or forearm < 20 or forearm > 50:
            await message.answer("❌ Некорректное значение. Попробуйте ещё раз или нажмите «Пропустить».")
            return
        await state.update_data(forearm_cm=forearm)
    
    # Следующий замер - обхват голени
    await ask_measurement(
        message, state,
        "Обхват голени",
        ProfileStates.waiting_for_calf,
        "Самое широкое место икры (обычно чуть ниже колена). Стоя, вес равномерно на обе ноги.",
        25, 60
    )

@router.message(ProfileStates.waiting_for_calf)
async def process_calf(message: Message, state: FSMContext):
    """Обработка обхвата голени"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["пропустить", "⏭️ пропустить"]:
        await state.update_data(calf_cm=None)
    else:
        calf, error = safe_parse_float(message.text, "обхват голени")
        if error or calf < 25 or calf > 60:
            await message.answer("❌ Некорректное значение. Попробуйте ещё раз или нажмите «Пропустить».")
            return
        await state.update_data(calf_cm=calf)
    
    # Следующий замер - ширина плеч
    await ask_measurement(
        message, state,
        "Ширина плеч",
        ProfileStates.waiting_for_shoulder_width,
        "Расстояние между акромиальными точками (крайние костные выступы плеч). Лучше с помощником.",
        30, 60
    )

@router.message(ProfileStates.waiting_for_shoulder_width)
async def process_shoulder_width(message: Message, state: FSMContext):
    """Обработка ширины плеч"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["пропустить", "⏭️ пропустить"]:
        await state.update_data(shoulder_width_cm=None)
    else:
        shoulder_width, error = safe_parse_float(message.text, "ширина плеч")
        if error or shoulder_width < 30 or shoulder_width > 60:
            await message.answer("❌ Некорректное значение. Попробуйте ещё раз или нажмите «Пропустить».")
            return
        await state.update_data(shoulder_width_cm=shoulder_width)
    
    # Последний замер - ширина таза
    await ask_measurement(
        message, state,
        "Ширина таза",
        ProfileStates.waiting_for_hip_width,
        "Расстояние между гребнями подвздошных костей (самые широкие точки таза).",
        25, 50
    )

@router.message(ProfileStates.waiting_for_hip_width)
async def process_hip_width(message: Message, state: FSMContext):
    """Обработка ширины таза и сохранение профиля"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["пропустить", "⏭️ пропустить"]:
        await state.update_data(hip_width_cm=None)
    else:
        hip_width, error = safe_parse_float(message.text, "ширина таза")
        if error or hip_width < 25 or hip_width > 50:
            await message.answer("❌ Некорректное значение. Попробуйте ещё раз или нажмите «Пропустить».")
            return
        await state.update_data(hip_width_cm=hip_width)
    
    # Сохраняем полный профиль
    await save_profile(message, state)

async def save_profile(message: Message, state: FSMContext):
    """Сохранение полного профиля с расширенной антропометрией"""
    
    # Получаем все данные
    profile_data = await state.get_data()
    
    weight = profile_data['weight']
    height = profile_data['height']
    age = profile_data['age']
    gender = profile_data['gender']
    activity_level = profile_data['activity_level']
    goal = profile_data['goal']
    city = profile_data['city']
    
    # Преобразуем русское название активности в английский код для калькулятора
    activity_map_calc = {
        "минимальная": "low",
        "легкая": "medium", 
        "умеренная": "medium",
        "высокая": "high",
        "очень высокая": "high"
    }
    activity_calc = activity_map_calc.get(activity_level, "medium")
    
    # Рассчитываем КБЖУ с использованием калькулятора
    from services.calculator import calculate_calorie_goal, calculate_water_goal
    
    nutrition_goals = calculate_calorie_goal(
        weight=weight,
        height=height, 
        age=age,
        gender=gender,
        activity_level=activity_calc,  # используем английский код
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
            user.activity_level = activity_level  # сохраняем строку, а не число
            user.goal = goal
            user.city = city
            user.daily_calorie_goal = round(daily_calorie_goal)
            user.daily_protein_goal = round(daily_protein_goal)
            user.daily_fat_goal = round(daily_fat_goal)
            user.daily_carbs_goal = round(daily_carbs_goal)
            user.daily_water_goal = round(daily_water_goal)
            
            # Сохраняем антропометрические данные
            if gender == "female":
                user.neck_cm = profile_data.get('neck_cm')
                user.waist_cm = profile_data.get('waist_cm')
                user.hip_cm = profile_data.get('hip_cm')
            elif gender == "male":
                user.wrist_cm = profile_data.get('wrist_cm')
                user.bicep_cm = profile_data.get('bicep_cm')
            
            # Сохраняем новые расширенные антропометрические данные
            user.chest_cm = profile_data.get('chest_cm')
            user.forearm_cm = profile_data.get('forearm_cm')
            user.calf_cm = profile_data.get('calf_cm')
            user.shoulder_width_cm = profile_data.get('shoulder_width_cm')
            user.hip_width_cm = profile_data.get('hip_width_cm')
            
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
        reply_markup=get_main_keyboard_v2(),
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
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Формируем текст с расширенными данными
        profile_text = f"""👤 <b>Ваш профиль</b>

📏 <b>Основные параметры:</b>
• Вес: {user.weight} кг
• Рост: {user.height} см
• Возраст: {user.age} лет
• Пол: {'Мужской' if user.gender == 'male' else 'Женский'}
• Город: {user.city}
• Цель: {user.goal}

� <b>Ваши нормы:</b>
• Калории: {user.daily_calorie_goal} ккал/день
• Белки: {user.daily_protein_goal} г/день
• Жиры: {user.daily_fat_goal} г/день
• Углеводы: {user.daily_carbs_goal} г/день
• Вода: {user.daily_water_goal} мл/день

📐 <b>Антропометрия:</b>
"""
        
        # Добавляем базовые антропометрические данные
        if user.gender == "female":
            if user.neck_cm:
                profile_text += f"• Обхват шеи: {user.neck_cm} см\n"
            if user.waist_cm:
                profile_text += f"• Обхват талии: {user.waist_cm} см\n"
            if user.hip_cm:
                profile_text += f"• Обхват бедер: {user.hip_cm} см\n"
        elif user.gender == "male":
            if user.wrist_cm:
                profile_text += f"• Обхват запястья: {user.wrist_cm} см\n"
            if user.bicep_cm:
                profile_text += f"• Обхват бицепса: {user.bicep_cm} см\n"
        
        # Добавляем расширенные антропометрические данные
        extended_measurements = []
        if user.chest_cm:
            extended_measurements.append(f"Обхват груди: {user.chest_cm} см")
        if user.forearm_cm:
            extended_measurements.append(f"Обхват предплечья: {user.forearm_cm} см")
        if user.calf_cm:
            extended_measurements.append(f"Обхват голени: {user.calf_cm} см")
        if user.shoulder_width_cm:
            extended_measurements.append(f"Ширина плеч: {user.shoulder_width_cm} см")
        if user.hip_width_cm:
            extended_measurements.append(f"Ширина таза: {user.hip_width_cm} см")
        
        if extended_measurements:
            profile_text += "\n📏 <b>Расширенные замеры:</b>\n"
            for measurement in extended_measurements:
                profile_text += f"• {measurement}\n"
        else:
            profile_text += "• Расширенные замеры: не указаны\n"
        
        profile_text += "\n🔧 Для изменения профиля используйте /edit_profile"
        
        await message.answer(
            profile_text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )

@router.message(Command("edit_profile"))
async def cmd_edit_profile(message: Message, state: FSMContext):
    """Начало редактирования профиля"""
    await state.clear()
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Профиль не найден. Сначала настройте профиль командой /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Сохраняем ID пользователя для редактирования
        await state.update_data(user_id=user.id, original_data=user.__dict__.copy())
        
        # Показываем клавиатуру выбора параметра для редактирования
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📏 Вес", callback_data="edit_weight")],
            [InlineKeyboardButton(text="📐 Рост", callback_data="edit_height")],
            [InlineKeyboardButton(text="🎂 Возраст", callback_data="edit_age")],
            [InlineKeyboardButton(text="⚧️ Пол", callback_data="edit_gender")],
            [InlineKeyboardButton(text="🏙️ Город", callback_data="edit_city")],
            [InlineKeyboardButton(text="🎯 Цель", callback_data="edit_goal")],
            [InlineKeyboardButton(text="📐 Обхваты", callback_data="edit_measurements")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="edit_cancel")]
        ])
        
        await message.answer(
            "🔧 <b>Редактирование профиля</b>\n\n"
            "Выберите параметр, который хотите изменить:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

async def process_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора параметра для редактирования"""
    action = callback.data.split("_")[1]
    
    if action == "cancel":
        await state.clear()
        await callback.message.answer(
            "❌ Редактирование отменено",
            reply_markup=get_main_keyboard_v2()
        )
        return
    
    # Устанавливаем состояние в зависимости от выбранного параметра
    if action == "weight":
        await callback.message.answer("📏 Введите новый вес (в кг):")
        await state.set_state(ProfileStates.weight)
    elif action == "height":
        await callback.message.answer("📐 Введите новый рост (в см):")
        await state.set_state(ProfileStates.height)
    elif action == "age":
        await callback.message.answer("🎂 Введите новый возраст:")
        await state.set_state(ProfileStates.age)
    elif action == "gender":
        await callback.message.answer(
            "⚧️ Выберите пол:",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(ProfileStates.gender)
    elif action == "city":
        await callback.message.answer("🏙️ Введите новый город:")
        await state.set_state(ProfileStates.city)
    elif action == "goal":
        await show_goal_keyboard(callback.message, state)
    elif action == "measurements":
        await show_measurements_keyboard(callback.message, state)
    elif action == "neck":
        await callback.message.answer("📐 Введите новый обхват шеи (в см):")
        await state.set_state(ProfileStates.waiting_for_neck)
    elif action == "waist":
        await callback.message.answer("⭕ Введите новый обхват талии (в см):")
        await state.set_state(ProfileStates.waiting_for_waist)
    elif action == "hip":
        await callback.message.answer("🍑 Введите новый обхват бедер (в см):")
        await state.set_state(ProfileStates.waiting_for_hip)
    elif action == "wrist":
        await callback.message.answer("⌚ Введите новый обхват запястья (в см):")
        await state.set_state(ProfileStates.waiting_for_wrist)
    elif action == "bicep":
        await callback.message.answer("💪 Введите новый обхват бицепса (в см):")
        await state.set_state(ProfileStates.waiting_for_bicep)
    elif action == "extended":
        await show_extended_measurements_keyboard(callback.message, state)
    elif action == "chest":
        await callback.message.answer("📊 Введите новый обхват груди (в см):")
        await state.set_state(ProfileStates.waiting_for_chest)
    elif action == "forearm":
        await callback.message.answer("💪 Введите новый обхват предплечья (в см):")
        await state.set_state(ProfileStates.waiting_for_forearm)
    elif action == "calf":
        await callback.message.answer("🦵 Введите новый обхват голени (в см):")
        await state.set_state(ProfileStates.waiting_for_calf)
    elif action == "shoulder_width":
        await callback.message.answer("📏 Введите новую ширину плеч (в см):")
        await state.set_state(ProfileStates.waiting_for_shoulder_width)
    elif action == "hip_width":
        await callback.message.answer("📐 Введите новую ширину таза (в см):")
        await state.set_state(ProfileStates.waiting_for_hip_width)
    
    await callback.answer()

async def show_extended_measurements_keyboard(message: Message, state: FSMContext):
    """Показ клавиатуры для расширенных замеров"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Обхват груди", callback_data="edit_chest")],
        [InlineKeyboardButton(text="💪 Обхват предплечья", callback_data="edit_forearm")],
        [InlineKeyboardButton(text="🦵 Обхват голени", callback_data="edit_calf")],
        [InlineKeyboardButton(text="📏 Ширина плеч", callback_data="edit_shoulder_width")],
        [InlineKeyboardButton(text="📐 Ширина таза", callback_data="edit_hip_width")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="edit_cancel")]
    ])
    
    await message.answer(
        "📏 <b>Выберите расширенный замер:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# Обработчики для базовых антропометрических замеров
@router.message(ProfileStates.waiting_for_neck)
async def process_edit_neck(message: Message, state: FSMContext):
    """Обработка изменения обхвата шеи"""
    await process_measurement_edit(message, state, "neck_cm", "обхват шеи")

@router.message(ProfileStates.waiting_for_waist)
async def process_edit_waist(message: Message, state: FSMContext):
    """Обработка изменения обхвата талии"""
    await process_measurement_edit(message, state, "waist_cm", "обхват талии")

@router.message(ProfileStates.waiting_for_hip)
async def process_edit_hip(message: Message, state: FSMContext):
    """Обработка изменения обхвата бедер"""
    await process_measurement_edit(message, state, "hip_cm", "обхват бедер")

@router.message(ProfileStates.waiting_for_wrist)
async def process_edit_wrist(message: Message, state: FSMContext):
    """Обработка изменения обхвата запястья"""
    await process_measurement_edit(message, state, "wrist_cm", "обхват запястья")

@router.message(ProfileStates.waiting_for_bicep)
async def process_edit_bicep(message: Message, state: FSMContext):
    """Обработка изменения обхвата бицепса"""
    await process_measurement_edit(message, state, "bicep_cm", "обхват бицепса")

# Обработчики для расширенных антропометрических замеров (только message обработчики)
@router.message(ProfileStates.waiting_for_chest)
async def process_chest(message: Message, state: FSMContext):
    """Обработка изменения обхвата груди"""
    await process_measurement_edit(message, state, "chest_cm", "обхват груди")

@router.message(ProfileStates.waiting_for_forearm)
async def process_forearm(message: Message, state: FSMContext):
    """Обработка изменения обхвата предплечья"""
    await process_measurement_edit(message, state, "forearm_cm", "обхват предплечья")

@router.message(ProfileStates.waiting_for_calf)
async def process_calf(message: Message, state: FSMContext):
    """Обработка изменения обхвата голени"""
    await process_measurement_edit(message, state, "calf_cm", "обхват голени")

@router.message(ProfileStates.waiting_for_shoulder_width)
async def process_shoulder_width(message: Message, state: FSMContext):
    """Обработка изменения ширины плеч"""
    await process_measurement_edit(message, state, "shoulder_width_cm", "ширина плеч")

@router.message(ProfileStates.waiting_for_hip_width)
async def process_hip_width(message: Message, state: FSMContext):
    """Обработка изменения ширины таза"""
    await process_measurement_edit(message, state, "hip_width_cm", "ширина таза")

async def process_measurement_edit(message: Message, state: FSMContext, field_name: str, field_display: str):
    """Универсальная функция обработки изменения замера"""
    from utils.safe_parser import safe_parse_float
    
    value, error = safe_parse_float(message.text, field_display)
    if error:
        await message.answer(f"❌ {error}\nПопробуйте ещё раз:")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_value = original_data.get(field_name, 'не указан')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            setattr(user, field_name, value)
            await session.commit()
            
            await message.answer(
                f"✅ <b>{field_display.title()} обновлен!</b>\n\n"
                f"📏 <b>Изменение:</b>\n"
                f"Было: {old_value} см\n"
                f"Стало: {value} см\n"
                f"Разница: {value - old_value:+.1f} см\n\n"
                f"💡 Профиль успешно обновлен!",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

async def show_goal_keyboard(message: Message, state: FSMContext):
    """Показ клавиатуры для выбора цели"""
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
        "🎯 <b>Выберите новую цель:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.goal)

async def show_measurements_keyboard(message: Message, state: FSMContext):
    """Показ клавиатуры для выбора замеров"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📐 Обхват шеи", callback_data="edit_neck")],
        [InlineKeyboardButton(text="⭕ Обхват талии", callback_data="edit_waist")],
        [InlineKeyboardButton(text="🍑 Обхват бедер", callback_data="edit_hip")],
        [InlineKeyboardButton(text="⌚ Обхват запястья", callback_data="edit_wrist")],
        [InlineKeyboardButton(text="💪 Обхват бицепса", callback_data="edit_bicep")],
        [InlineKeyboardButton(text="📊 Расширенные замеры", callback_data="edit_extended")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="edit_cancel")]
    ])
    
    await message.answer(
            "📏 <b>Выберите замер для изменения:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@router.message(ProfileStates.weight)
async def process_edit_weight(message: Message, state: FSMContext):
    """Обработка изменения веса"""
    from utils.safe_parser import safe_parse_float
    
    weight, error = safe_parse_float(message.text, "вес")
    if error:
        await message.answer(f"❌ {error}\nПопробуйте ещё раз:")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_weight = original_data.get('weight', 'не указан')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.weight = weight
            # Пересчитываем цели
            from services.calculator import calculate_calorie_goal, calculate_water_goal
            
            activity_map_calc = {
                "минимальная": "low",
                "легкая": "medium",
                "умеренная": "medium",
                "высокая": "high",
                "очень высокая": "high"
            }
            activity_calc = activity_map_calc.get(user.activity_level, "medium")
            
            nutrition_goals = calculate_calorie_goal(
                weight=weight,
                height=user.height,
                age=user.age,
                gender=user.gender,
                activity_level=activity_calc,
                goal=user.goal
            )
            
            daily_calorie_goal, daily_protein_goal, daily_fat_goal, daily_carbs_goal = nutrition_goals
            
            try:
                from services.weather import get_temperature
                temperature = await get_temperature(user.city)
            except:
                temperature = 20.0
                
            water_goal = calculate_water_goal(
                weight=weight,
                activity_level=user.activity_level,
                temperature=temperature
            )
            
            user.daily_calorie_goal = round(daily_calorie_goal)
            user.daily_protein_goal = round(daily_protein_goal)
            user.daily_fat_goal = round(daily_fat_goal)
            user.daily_carbs_goal = round(daily_carbs_goal)
            user.daily_water_goal = round(water_goal)
            
            await session.commit()
            
            await message.answer(
                f"✅ <b>Вес обновлен!</b>\n\n"
                f"📏 <b>Изменение:</b>\n"
                f"Было: {old_weight} кг\n"
                f"Стало: {weight} кг\n"
                f"Разница: {weight - old_weight:+.1f} кг\n\n"
                f"📊 <b>Новые нормы:</b>\n"
                f"🔥 Калории: {user.daily_calorie_goal} ккал/день\n"
                f"💧 Вода: {user.daily_water_goal} мл/день\n\n"
                f"💡 Все цели автоматически пересчитаны!",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.height)
async def process_edit_height(message: Message, state: FSMContext):
    """Обработка изменения роста"""
    from utils.safe_parser import safe_parse_int
    
    height, error = safe_parse_int(message.text, "рост")
    if error:
        await message.answer(f"❌ {error}\nПопробуйте ещё раз:")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_height = original_data.get('height', 'не указан')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.height = height
            await session.commit()
            
            await message.answer(
                f"✅ <b>Рост обновлен!</b>\n\n"
                f"📐 <b>Изменение:</b>\n"
                f"Было: {old_height} см\n"
                f"Стало: {height} см\n"
                f"Разница: {height - old_height:+d} см\n\n"
                f"💡 Рекомендуется пересчитать цели командой /set_profile",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.age)
async def process_edit_age(message: Message, state: FSMContext):
    """Обработка изменения возраста"""
    from utils.safe_parser import safe_parse_int
    
    age, error = safe_parse_int(message.text, "возраст")
    if error:
        await message.answer(f"❌ {error}\nПопробуйте ещё раз:")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_age = original_data.get('age', 'не указан')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.age = age
            await session.commit()
            
            await message.answer(
                f"✅ <b>Возраст обновлен!</b>\n\n"
                f"🎂 <b>Изменение:</b>\n"
                f"Было: {old_age} лет\n"
                f"Стало: {age} лет\n"
                f"Разница: {age - old_age:+d} лет\n\n"
                f"💡 Рекомендуется пересчитать цели командой /set_profile",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.gender)
async def process_edit_gender(message: Message, state: FSMContext):
    """Обработка изменения пола"""
    gender_text = message.text.lower()
    
    if "мужской" in gender_text:
        gender = "male"
        gender_display = "Мужской"
    elif "женский" in gender_text:
        gender = "female"
        gender_display = "Женский"
    else:
        await message.answer("❌ Выберите 'Мужской' или 'Женский'")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_gender = original_data.get('gender', 'не указан')
    old_display = "Мужской" if old_gender == 'male' else "Женский" if old_gender == 'female' else old_gender
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.gender = gender
            await session.commit()
            
            await message.answer(
                f"✅ <b>Пол обновлен!</b>\n\n"
                f"⚧️ <b>Изменение:</b>\n"
                f"Было: {old_display}\n"
                f"Стало: {gender_display}\n\n"
                f"💡 Рекомендуется пересчитать цели командой /set_profile",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.city)
async def process_edit_city(message: Message, state: FSMContext):
    """Обработка изменения города"""
    city = message.text.strip()
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_city = original_data.get('city', 'не указан')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.city = city
            
            # Пересчитываем цель по воде с учетом погоды
            try:
                from services.weather import get_temperature
                from services.calculator import calculate_water_goal
                
                temperature = await get_temperature(city)
                water_goal = calculate_water_goal(
                    weight=user.weight,
                    activity_level=user.activity_level,
                    temperature=temperature
                )
                user.daily_water_goal = round(water_goal)
                
                weather_info = f"\n💧 <b>Новая цель по воде:</b> {user.daily_water_goal} мл/день (учтена погода)"
            except:
                weather_info = ""
            
            await session.commit()
            
            await message.answer(
                f"✅ <b>Город обновлен!</b>\n\n"
                f"🏙️ <b>Изменение:</b>\n"
                f"Было: {old_city}\n"
                f"Стало: {city}\n{weather_info}\n\n"
                f"💡 Профиль успешно обновлен!",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.goal)
async def process_edit_goal(message: Message, state: FSMContext):
    """Обработка изменения цели"""
    goal_text = message.text.lower()
    
    goal_map = {
        "похудение": "lose_weight",
        "поддержание": "maintain",
        "набор массы": "gain_weight"
    }
    
    if goal_text not in goal_map:
        await message.answer("❌ Выберите из предложенных вариантов")
        return
    
    goal_type = goal_map[goal_text]
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_goal = original_data.get('goal', 'не указана')
    old_display = old_goal.replace('_', ' ').title() if old_goal != 'не указана' else old_goal
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.goal = goal_type
            
            # Пересчитываем цели
            from services.calculator import calculate_calorie_goal
            
            activity_map_calc = {
                "минимальная": "low",
                "легкая": "medium",
                "умеренная": "medium",
                "высокая": "high",
                "очень высокая": "high"
            }
            activity_calc = activity_map_calc.get(user.activity_level, "medium")
            
            nutrition_goals = calculate_calorie_goal(
                weight=user.weight,
                height=user.height,
                age=user.age,
                gender=user.gender,
                activity_level=activity_calc,
                goal=goal_type
            )
            
            daily_calorie_goal, daily_protein_goal, daily_fat_goal, daily_carbs_goal = nutrition_goals
            
            user.daily_calorie_goal = round(daily_calorie_goal)
            user.daily_protein_goal = round(daily_protein_goal)
            user.daily_fat_goal = round(daily_fat_goal)
            user.daily_carbs_goal = round(daily_carbs_goal)
            
            await session.commit()
            
            profile_text = ""
            profile_text += f"• Город: {user.city}\n"
            profile_text += f"• Цель: {user.goal}\n\n"
            profile_text += f"📊 <b>Ваши нормы:</b>\n"
            profile_text += f"• Калории: {user.daily_calorie_goal} ккал/день\n"
            profile_text += f"• Белки: {user.daily_protein_goal} г/день\n"
            profile_text += f"• Жиры: {user.daily_fat_goal} г/день\n"
            profile_text += f"• Углеводы: {user.daily_carbs_goal} г/день\n"
            profile_text += f"• Вода: {user.daily_water_goal} мл/день\n\n"
            profile_text += "📐 <b>Антропометрия:</b>\n"
            
            await message.answer(
                f"✅ <b>Цель обновлена!</b>\n\n"
                f"🎯 <b>Изменение:</b>\n"
                f"Было: {old_display}\n"
                f"Стало: {message.text}\n\n"
                f"{profile_text}",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()
