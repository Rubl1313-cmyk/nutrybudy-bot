from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import get_session
from database.models import User
from services.calculator import calculate_water_goal, calculate_calorie_goal
from services.weather import get_temperature
from keyboards.reply import get_cancel_keyboard, get_main_keyboard, get_gender_keyboard, get_activity_level_keyboard, get_goal_keyboard
from utils.states import ProfileStates

router = Router()

@router.message(Command("set_profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with get_session() as session:
        user = await session.get(User, user_id)
        if user and user.weight:
            text = (
                f"👤 <b>Твой профиль</b>\n\n"
                f"⚖️ Вес: {user.weight} кг\n"
                f"📏 Рост: {user.height} см\n"
                f"🎂 Возраст: {user.age}\n"
                f"🚻 Пол: {'Мужской' if user.gender=='male' else 'Женский'}\n"
                f"🏃 Активность: {user.activity_level}\n"
                f"🎯 Цель: {user.goal}\n"
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
            await state.set_state(ProfileStates.weight)
            await message.answer("⚖️ Введи свой вес (в кг):", reply_markup=get_cancel_keyboard())

@router.message(ProfileStates.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight < 30 or weight > 300:
            raise ValueError
        await state.update_data(weight=weight)
        await state.set_state(ProfileStates.height)
        await message.answer("📏 Введи свой рост (в см):")
    except ValueError:
        await message.answer("❌ Пожалуйста, введи корректное число (30-300 кг)")

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if height < 100 or height > 250:
            raise ValueError
        await state.update_data(height=height)
        await state.set_state(ProfileStates.age)
        await message.answer("🎂 Сколько тебе лет?")
    except ValueError:
        await message.answer("❌ Пожалуйста, введи корректное число (100-250 см)")

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 10 or age > 120:
            raise ValueError
        await state.update_data(age=age)
        await state.set_state(ProfileStates.gender)
        await message.answer("🚻 Выбери пол:", reply_markup=get_gender_keyboard())
    except ValueError:
        await message.answer("❌ Введи целое число (10-120)")

@router.message(ProfileStates.gender)
async def process_gender(message: Message, state: FSMContext):
    gender_map = {"♂️ Мужской": "male", "♀️ Женский": "female"}
    if message.text not in gender_map:
        await message.answer("❌ Выбери из кнопок")
        return
    await state.update_data(gender=gender_map[message.text])
    await state.set_state(ProfileStates.activity)
    await message.answer("🏋️‍♂️ Уровень активности:", reply_markup=get_activity_level_keyboard())

@router.message(ProfileStates.activity)
async def process_activity(message: Message, state: FSMContext):
    act_map = {
        "🪑 Сидячий": "low",
        "🚶 Средний": "medium",
        "🏃 Высокий": "high"
    }
    if message.text not in act_map:
        await message.answer("❌ Выбери из кнопок")
        return
    await state.update_data(activity=act_map[message.text])
    await state.set_state(ProfileStates.goal)
    await message.answer("🎯 Выбери цель:", reply_markup=get_goal_keyboard())

@router.message(ProfileStates.goal)
async def process_goal(message: Message, state: FSMContext):
    goal_map = {"⬇️ Похудение": "lose", "➡️ Поддержание": "maintain", "⬆️ Набор массы": "gain"}
    if message.text not in goal_map:
        await message.answer("❌ Выбери из кнопок")
        return
    await state.update_data(goal=goal_map[message.text])
    await state.set_state(ProfileStates.city)
    await message.answer("🌆 Твой город (для учёта погоды):", reply_markup=get_cancel_keyboard())

# В handlers/profile.py (конец функции process_city):

@router.message(ProfileStates.city, F.text)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    data = await state.get_data()
    temp = await get_temperature(city)
    water_goal = calculate_water_goal(data['weight'], data['activity'], temp)
    calorie_goal, protein, fat, carbs = calculate_calorie_goal(
        data['weight'], data['height'], data['age'],
        data['gender'], data['activity'], data['goal']
    )
    
    # ✅ ПРАВИЛЬНО: get_session() без await
    async with get_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(telegram_id=message.from_user.id)
            session.add(user)
        
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
        
        await session.commit()  # 🔥 ВАЖНО: commit!
    
    await state.clear()
    
    await message.answer(
        f"✅ <b>Профиль сохранён!</b>\n\n"
        f"🔥 Калории: {calorie_goal} ккал\n"
        f"🥩 Белки: {protein} г | 🥑 Жиры: {fat} г | 🍚 Углеводы: {carbs} г\n"
        f"💧 Вода: {water_goal} мл",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
