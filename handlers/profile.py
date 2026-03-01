"""
Обработчик профиля пользователя для NutriBuddy
✅ Полностью функциональный модуль настройки и просмотра профиля
✅ Исправлено: правильное получение пользователя по telegram_id
✅ Исправлено: корректная работа с async session
"""

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.db import get_session
from database.models import User
from services.calculator import calculate_water_goal, calculate_calorie_goal
from services.weather import get_temperature
from keyboards.reply import get_cancel_keyboard, get_main_keyboard, get_gender_keyboard, get_activity_level_keyboard, get_goal_keyboard
from utils.states import ProfileStates, WeightStates

router = Router()


# =============================================================================
# 👤 ПРОСМОТР И НАСТРОЙКА ПРОФИЛЯ
# =============================================================================

@router.message(Command("set_profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, state: FSMContext):
    """
    Показать профиль или начать настройку.
    Если профиль заполнен — показываем данные.
    Если нет — начинаем пошаговую настройку.
    """
    user_id = message.from_user.id
    
    async with get_session() as session:
        # ✅ ИСПРАВЛЕНО: ищем по telegram_id, а не по первичному ключу id
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user and user.weight and user.height:
            # Профиль заполнен — показываем красивое отображение
            gender_emoji = "♂️" if user.gender == "male" else "♀️"
            goal_emoji = {"lose": "⬇️", "maintain": "➡️", "gain": "⬆️"}.get(user.goal, "🎯")
            activity_emoji = {"low": "🪑", "medium": "🚶", "high": "🏃"}.get(user.activity_level, "🏃")
            
            text = (
                f"👤 <b>Твой профиль</b>\n\n"
                f"⚖️ Вес: <b>{user.weight} кг</b>\n"
                f"📏 Рост: <b>{user.height} см</b>\n"
                f"🎂 Возраст: <b>{user.age} лет</b>\n"
                f"🚻 Пол: {gender_emoji} {'Мужской' if user.gender == 'male' else 'Женский'}\n"
                f"🏃 Активность: {activity_emoji} {user.activity_level}\n"
                f"🎯 Цель: {goal_emoji} {user.goal}\n"
                f"🌆 Город: <i>{user.city}</i>\n\n"
                f"📊 <b>Дневные нормы:</b>\n"
                f"🔥 Калории: <b>{user.daily_calorie_goal:.0f} ккал</b>\n"
                f"🥩 Белки: {user.daily_protein_goal:.1f} г\n"
                f"🥑 Жиры: {user.daily_fat_goal:.1f} г\n"
                f"🍚 Углеводы: {user.daily_carbs_goal:.1f} г\n"
                f"💧 Вода: <b>{user.daily_water_goal:.0f} мл</b>\n\n"
                f"<i>Для изменения профиля пройди настройку ещё раз</i>"
            )
            await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        else:
            # Профиль не заполнен — начинаем настройку с веса
            await state.set_state(ProfileStates.weight)
            await message.answer(
                "⚖️ <b>Давай настроим твой профиль!</b>\n\n"
                "Это поможет мне рассчитать твои индивидуальные нормы.\n\n"
                "Введи свой вес в килограммах (например, <code>75.5</code>):",
                reply_markup=get_cancel_keyboard(),
                parse_mode="HTML"
            )


# =============================================================================
# ⚖️ ШАГ 1: ВЕС
# =============================================================================

@router.message(ProfileStates.weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    """Обработка ввода веса"""
    try:
        # Поддержка запятой и точки как разделителя
        weight = float(message.text.replace(',', '.').strip())
        
        if not 30 <= weight <= 300:
            raise ValueError("Вес вне допустимого диапазона")
            
        await state.update_data(weight=weight)
        await state.set_state(ProfileStates.height)
        
        await message.answer(
            f"✅ Вес: <b>{weight} кг</b>\n\n"
            "📏 Теперь введи свой рост в сантиметрах (например, <code>180</code>):",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введи корректное число от 30 до 300 кг\n\n"
            "Примеры: <code>75</code>, <code>75.5</code>, <code>75,5</code>",
            parse_mode="HTML"
        )


# =============================================================================
# 📏 ШАГ 2: РОСТ
# =============================================================================

@router.message(ProfileStates.height, F.text)
async def process_height(message: Message, state: FSMContext):
    """Обработка ввода роста"""
    try:
        height = float(message.text.replace(',', '.').strip())
        
        if not 100 <= height <= 250:
            raise ValueError("Рост вне допустимого диапазона")
            
        await state.update_data(height=height)
        await state.set_state(ProfileStates.age)
        
        await message.answer(
            f"✅ Рост: <b>{height} см</b>\n\n"
            "🎂 Сколько тебе лет? (введи целое число):",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введи корректное число от 100 до 250 см",
            parse_mode="HTML"
        )


# =============================================================================
# 🎂 ШАГ 3: ВОЗРАСТ
# =============================================================================

@router.message(ProfileStates.age, F.text)
async def process_age(message: Message, state: FSMContext):
    """Обработка ввода возраста"""
    try:
        age = int(message.text.strip())
        
        if not 10 <= age <= 120:
            raise ValueError("Возраст вне допустимого диапазона")
            
        await state.update_data(age=age)
        await state.set_state(ProfileStates.gender)
        
        await message.answer(
            f"✅ Возраст: <b>{age} лет</b>\n\n"
            "🚻 Выбери свой пол:",
            reply_markup=get_gender_keyboard(),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введи целое число от 10 до 120",
            parse_mode="HTML"
        )


# =============================================================================
# 🚻 ШАГ 4: ПОЛ
# =============================================================================

@router.message(ProfileStates.gender, F.text)
async def process_gender(message: Message, state: FSMContext):
    """Обработка выбора пола"""
    gender_map = {"♂️ Мужской": "male", "♀️ Женский": "female"}
    
    if message.text not in gender_map:
        await message.answer(
            "❌ Пожалуйста, выбери один из вариантов кнопками ниже:",
            reply_markup=get_gender_keyboard()
        )
        return
        
    await state.update_data(gender=gender_map[message.text])
    await state.set_state(ProfileStates.activity)
    
    await message.answer(
        f"✅ Пол: <b>{message.text}</b>\n\n"
        "🏋️ Выбери уровень своей физической активности:",
        reply_markup=get_activity_level_keyboard(),
        parse_mode="HTML"
    )


# =============================================================================
# 🏃 ШАГ 5: УРОВЕНЬ АКТИВНОСТИ
# =============================================================================

@router.message(ProfileStates.activity, F.text)
async def process_activity(message: Message, state: FSMContext):
    """Обработка выбора уровня активности"""
    act_map = {
        "🪑 Сидячий": "low",
        "🚶 Средний": "medium", 
        "🏃 Высокий": "high"
    }
    
    if message.text not in act_map:
        await message.answer(
            "❌ Пожалуйста, выбери один из вариантов кнопками:",
            reply_markup=get_activity_level_keyboard()
        )
        return
        
    await state.update_data(activity=act_map[message.text])
    await state.set_state(ProfileStates.goal)
    
    await message.answer(
        f"✅ Активность: <b>{message.text}</b>\n\n"
        "🎯 Какова твоя основная цель?",
        reply_markup=get_goal_keyboard(),
        parse_mode="HTML"
    )


# =============================================================================
# 🎯 ШАГ 6: ЦЕЛЬ
# =============================================================================

@router.message(ProfileStates.goal, F.text)
async def process_goal(message: Message, state: FSMContext):
    """Обработка выбора цели"""
    goal_map = {
        "⬇️ Похудение": "lose",
        "➡️ Поддержание": "maintain",
        "⬆️ Набор массы": "gain"
    }
    
    if message.text not in goal_map:
        await message.answer(
            "❌ Пожалуйста, выбери один из вариантов кнопками:",
            reply_markup=get_goal_keyboard()
        )
        return
        
    await state.update_data(goal=goal_map[message.text])
    await state.set_state(ProfileStates.city)
    
    await message.answer(
        f"✅ Цель: <b>{message.text}</b>\n\n"
        "🌆 Введи название своего города\n"
        "<i>(нужно для учёта погоды при расчёте нормы воды)</i>:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


# =============================================================================
# 🌆 ШАГ 7: ГОРОД + СОХРАНЕНИЕ В БД
# =============================================================================

@router.message(ProfileStates.city, F.text)
async def process_city(message: Message, state: FSMContext):
    """
    Финальный шаг: получение погоды, расчёт норм и сохранение профиля в БД.
    """
    city = message.text.strip()
    data = await state.get_data()
    
    # Получаем температуру для расчёта нормы воды (бесплатно через Open-Meteo)
    temp = await get_temperature(city)
    
    # Рассчитываем индивидуальные нормы
    water_goal = calculate_water_goal(data['weight'], data['activity'], temp)
    calorie_goal, protein, fat, carbs = calculate_calorie_goal(
        data['weight'], data['height'], data['age'],
        data['gender'], data['activity'], data['goal']
    )
    
    # ✅ СОХРАНЕНИЕ В БАЗУ ДАННЫХ
    async with get_session() as session:
        # 🔥 Ищем пользователя по telegram_id (не по id!)
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Создаём нового пользователя
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            session.add(user)
            await session.flush()  # Получаем auto-increment ID
        else:
            # Обновляем данные существующего пользователя
            user.username = message.from_user.username
            user.first_name = message.from_user.first_name
        
        # Заполняем все поля профиля
        user.weight = data['weight']
        user.height = data['height']
        user.age = data['age']
        user.gender = data['gender']
        user.activity_level = data['activity']
        user.goal = data['goal']
        user.city = city
        user.daily_water_goal = water_goal
        user.daily_calorie_goal = calorie_goal
        user.daily_protein_goal = protein
        user.daily_fat_goal = fat
        user.daily_carbs_goal = carbs
        
        # 🔥 ВАЖНО: commit для сохранения изменений!
        await session.commit()
    
    # Очищаем состояние FSM
    await state.clear()
    
    # Формируем красивое сообщение с результатами
    gender_emoji = "♂️" if data['gender'] == "male" else "♀️"
    goal_emoji = {"lose": "⬇️", "maintain": "➡️", "gain": "⬆️"}.get(data['goal'], "🎯")
    activity_emoji = {"low": "🪑", "medium": "🚶", "high": "🏃"}.get(data['activity'], "🏃")
    
    await message.answer(
        f"🎉 <b>Профиль успешно сохранён!</b>\n\n"
        f"👤 {gender_emoji} {data['gender'].capitalize()}, {data['age']} лет\n"
        f"⚖️ {data['weight']} кг | 📏 {data['height']} см\n"
        f"🏃 {activity_emoji} {data['activity']} | 🎯 {goal_emoji} {data['goal']}\n"
        f"🌆 {city} ({temp}°C)\n\n"
        f"📊 <b>Твои дневные нормы:</b>\n"
        f"🔥 Калории: <b>{calorie_goal} ккал</b>\n"
        f"🥩 Белки: {protein} г | 🥑 Жиры: {fat} г | 🍚 Углеводы: {carbs} г\n"
        f"💧 Вода: <b>{water_goal} мл</b>\n\n"
        f"<i>Нормы рассчитаны по формуле Миффлина-Сан Жеора</i>\n"
        f"<i>с учётом твоей цели, активности и погоды 🌤️</i>",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


# =============================================================================
# ⚖️ БЫСТРАЯ ЗАПИСЬ ВЕСА (/log_weight)
# =============================================================================

@router.message(Command("log_weight"))
async def cmd_log_weight(message: Message, state: FSMContext):
    """
    Быстрая запись текущего веса без полной настройки профиля.
    """
    await state.set_state(WeightStates.entering_weight)
    await message.answer(
        "⚖️ <b>Запись веса</b>\n\n"
        "Введи свой текущий вес в килограммах:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(WeightStates.entering_weight, F.text)
async def process_weight_log(message: Message, state: FSMContext):
    """Сохранение веса в историю и обновление профиля"""
    try:
        weight = float(message.text.replace(',', '.').strip())
        
        if not 30 <= weight <= 300:
            raise ValueError("Вес вне диапазона")
        
        async with get_session() as session:
            # 1. Записываем в историю взвешиваний
            from database.models import WeightEntry
            from datetime import datetime
            
            entry = WeightEntry(
                user_id=message.from_user.id,
                weight=weight,
                datetime=datetime.now()
            )
            session.add(entry)
            
            # 2. Обновляем текущий вес в профиле (если он есть)
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.weight = weight
                # Пересчитываем нормы при изменении веса
                if user.height and user.age and user.gender and user.activity_level and user.goal:
                    temp = await get_temperature(user.city or "Moscow")
                    user.daily_water_goal = calculate_water_goal(weight, user.activity_level, temp)
                    cal, prot, fat, carb = calculate_calorie_goal(
                        weight, user.height, user.age,
                        user.gender, user.activity_level, user.goal
                    )
                    user.daily_calorie_goal = cal
                    user.daily_protein_goal = prot
                    user.daily_fat_goal = fat
                    user.daily_carbs_goal = carb
            
            await session.commit()
        
        await state.clear()
        
        await message.answer(
            f"✅ <b>Вес {weight} кг записан!</b>\n\n"
            f"📈 Продолжай отслеживать прогресс в разделе 📊 Прогресс",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ Введи корректное число от 30 до 300 кг\n\n"
            "Примеры: <code>75</code>, <code>75.5</code>, <code>75,5</code>",
            parse_mode="HTML"
        )


# =============================================================================
# ❌ ОТМЕНА ДЕЙСТВИЯ
# =============================================================================

@router.message(F.text == "❌ Отмена", ProfileStates.weight | ProfileStates.height | ProfileStates.age | 
                ProfileStates.gender | ProfileStates.activity | ProfileStates.goal | ProfileStates.city)
async def cancel_profile_setup(message: Message, state: FSMContext):
    """Отмена настройки профиля"""
    await state.clear()
    await message.answer(
        "❌ Настройка профиля отменена.\n\n"
        "Нажми 👤 Профиль в любое время, чтобы начать заново.",
        reply_markup=get_main_keyboard()
    )
