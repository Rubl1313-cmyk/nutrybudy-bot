"""
Обработчик профиля пользователя
✅ ИСПРАВЛЕНО: правильное получение пользователя по telegram_id
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
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from utils.states import ProfileStates

router = Router()


@router.message(Command("set_profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, state: FSMContext):
    """Показать профиль или начать настройку"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        # ✅ ИСПРАВЛЕНО: ищем по telegram_id, а не по id
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user and user.weight and user.height:
            # Профиль заполнен — показываем
            gender_emoji = "♂️" if user.gender == "male" else "♀️"
            goal_emoji = {"lose": "⬇️", "maintain": "➡️", "gain": "⬆️"}.get(user.goal, "🎯")
            
            text = (
                f"👤 <b>Твой профиль</b>\n\n"
                f"⚖️ Вес: {user.weight} кг\n"
                f"📏 Рост: {user.height} см\n"
                f"🎂 Возраст: {user.age}\n"
                f"🚻 Пол: {gender_emoji} {'Мужской' if user.gender == 'male' else 'Женский'}\n"
                f"🏃 Активность: {user.activity_level}\n"
                f"🎯 Цель: {goal_emoji} {user.goal}\n"
                f"🌆 Город: {user.city}\n\n"
                f"📊 <b>Дневные нормы:</b>\n"
                f"🔥 Калории: {user.daily_calorie_goal:.0f} ккал\n"
                f"🥩 Белки: {user.daily_protein_goal:.1f} г\n"
                f"🥑 Жиры: {user.daily_fat_goal:.1f} г\n"
                f"🍚 Углеводы: {user.daily_carbs_goal:.1f} г\n"
                f"💧 Вода: {user.daily_water_goal:.0f} мл"
            )
            await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        else:
            # Профиль не заполнен — начинаем настройку
            await state.set_state(ProfileStates.weight)
            await message.answer(
                "⚖️ <b>Давай настроим твой профиль!</b>\n\n"
                "Введи свой вес в килограммах (например, 75.5):",
                reply_markup=get_cancel_keyboard(),
                parse_mode="HTML"
            )


@router.message(ProfileStates.weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    """Обработка ввода веса"""
    try:
        weight = float(message.text.replace(',', '.'))
        if not 30 <= weight <= 300:
            raise ValueError("Вес вне диапазона")
            
        await state.update_data(weight=weight)
        await state.set_state(ProfileStates.height)
        await message.answer(
            f"✅ Вес: {weight} кг\n\n"
            "📏 Теперь введи свой рост в сантиметрах (например, 180):"
        )
    except ValueError:
        await message.answer("❌ Пожалуйста, введи корректное число от 30 до 300 кг")


@router.message(ProfileStates.height, F.text)
async def process_height(message: Message, state: FSMContext):
    """Обработка ввода роста"""
    try:
        height = float(message.text.replace(',', '.'))
        if not 100 <= height <= 250:
            raise ValueError("Рост вне диапазона")
            
        await state.update_data(height=height)
        await state.set_state(ProfileStates.age)
        await message.answer(
            f"✅ Рост: {height} см\n\n"
            "🎂 Сколько тебе лет?"
        )
    except ValueError:
        await message.answer("❌ Пожалуйста, введи корректное число от 100 до 250 см")


@router.message(ProfileStates.age, F.text)
async def process_age(message: Message, state: FSMContext):
    """Обработка ввода возраста"""
    try:
        age = int(message.text)
        if not 10 <= age <= 120:
            raise ValueError("Возраст вне диапазона")
            
        await state.update_data(age=age)
        await state.set_state(ProfileStates.gender)
        
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="♂️ Мужской")],
                [KeyboardButton(text="♀️ Женский")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"✅ Возраст: {age} лет\n\n"
            "🚻 Выбери свой пол:",
            reply_markup=kb
        )
    except ValueError:
        await message.answer("❌ Пожалуйста, введи целое число от 10 до 120")


@router.message(ProfileStates.gender, F.text)
async def process_gender(message: Message, state: FSMContext):
    """Обработка выбора пола"""
    gender_map = {"♂️ Мужской": "male", "♀️ Женский": "female"}
    
    if message.text not in gender_map:
        await message.answer("❌ Пожалуйста, выбери один из вариантов кнопками")
        return
        
    await state.update_data(gender=gender_map[message.text])
    await state.set_state(ProfileStates.activity)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪑 Сидячий")],
            [KeyboardButton(text="🚶 Средний")],
            [KeyboardButton(text="🏃 Высокий")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        f"✅ Пол: {message.text}\n\n"
        "🏋️ Выбери уровень физической активности:",
        reply_markup=kb
    )


@router.message(ProfileStates.activity, F.text)
async def process_activity(message: Message, state: FSMContext):
    """Обработка выбора уровня активности"""
    act_map = {
        "🪑 Сидячий": "low",
        "🚶 Средний": "medium", 
        "🏃 Высокий": "high"
    }
    
    if message.text not in act_map:
        await message.answer("❌ Пожалуйста, выбери один из вариантов кнопками")
        return
        
    await state.update_data(activity=act_map[message.text])
    await state.set_state(ProfileStates.goal)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬇️ Похудение")],
            [KeyboardButton(text="➡️ Поддержание")],
            [KeyboardButton(text="⬆️ Набор массы")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        f"✅ Активность: {message.text}\n\n"
        "🎯 Какова твоя цель?",
        reply_markup=kb
    )


@router.message(ProfileStates.goal, F.text)
async def process_goal(message: Message, state: FSMContext):
    """Обработка выбора цели"""
    goal_map = {
        "⬇️ Похудение": "lose",
        "➡️ Поддержание": "maintain",
        "⬆️ Набор массы": "gain"
    }
    
    if message.text not in goal_map:
        await message.answer("❌ Пожалуйста, выбери один из вариантов кнопками")
        return
        
    await state.update_data(goal=goal_map[message.text])
    await state.set_state(ProfileStates.city)
    await message.answer(
        f"✅ Цель: {message.text}\n\n"
        "🌆 Введи название своего города (для учёта погоды при расчёте нормы воды):",
        reply_markup=get_cancel_keyboard()
    )


@router.message(ProfileStates.city, F.text)
async def process_city(message: Message, state: FSMContext):
    """Финальный шаг: сохранение профиля в БД"""
    city = message.text.strip()
    data = await state.get_data()
    
    # Получаем температуру для расчёта нормы воды
    temp = await get_temperature(city)
    
    # Рассчитываем нормы
    water_goal = calculate_water_goal(data['weight'], data['activity'], temp)
    calorie_goal, protein, fat, carbs = calculate_calorie_goal(
        data['weight'], data['height'], data['age'],
        data['gender'], data['activity'], data['goal']
    )
    
    # ✅ ИСПРАВЛЕНО: правильное получение/создание пользователя
    async with get_session() as session:
        # Ищем пользователя по telegram_id
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
            await session.flush()  # Получаем ID
        else:
            # Обновляем существующего пользователя
            user.username = message.from_user.username
            user.first_name = message.from_user.first_name
        
        # Заполняем все поля
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
        
        await session.commit()  # ✅ ВАЖНО: commit!
    
    await state.clear()
    
    # Формируем красивое сообщение с результатами
    gender_emoji = "♂️" if data['gender'] == "male" else "♀️"
    goal_emoji = {"lose": "⬇️", "maintain": "➡️", "gain": "⬆️"}.get(data['goal'], "🎯")
    
    await message.answer(
        f"🎉 <b>Профиль успешно сохранён!</b>\n\n"
        f"👤 {gender_emoji} {data['gender'].capitalize()}, {data['age']} лет\n"
        f"⚖️ {data['weight']} кг | 📏 {data['height']} см\n"
        f"🏃 {data['activity']} | 🎯 {goal_emoji} {data['goal']}\n"
        f"🌆 {city} ({temp}°C)\n\n"
        f"📊 <b>Твои дневные нормы:</b>\n"
        f"🔥 Калории: <b>{calorie_goal} ккал</b>\n"
        f"🥩 Белки: {protein} г | 🥑 Жиры: {fat} г | 🍚 Углеводы: {carbs} г\n"
        f"💧 Вода: <b>{water_goal} мл</b>\n\n"
        f"<i>Нормы рассчитаны по формуле Миффлина-Сан Жеора с учётом твоей цели и погоды</i>",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
