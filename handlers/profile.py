"""
Обработчик профиля пользователя для NutriBuddy
✅ Исправлено: получение пользователя по telegram_id
✅ Исправлено: погода для российских городов
"""
import logging  # ← ДОБАВЛЕНО!
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.db import get_session
from database.models import User
from services.calculator import calculate_water_goal, calculate_calorie_goal
from services.weather import get_temperature
from keyboards.reply import get_cancel_keyboard, get_main_keyboard, get_edit_profile_keyboard
from utils.states import ProfileStates

logger = logging.getLogger(__name__)  # ← ДОБАВЛЕНО!

router = Router()


@router.message(Command("set_profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, state: FSMContext):
    """Показать профиль или начать настройку"""
    await state.clear()
    
    user_id = message.from_user.id
    
@router.message(Command("set_profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, state: FSMContext):
    await state.clear()
    
    user_id = message.from_user.id
    logger.info(f"🔍 Profile request from telegram_id={user_id}")
    
    async with get_session() as session:
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            logger.info(f"🔍 User found: {user is not None}")
            if user:
                logger.info(f"  - weight={user.weight}, height={user.height}")
            gender_emoji = "♂️" if user.gender == "male" else "♀️"
            goal_emoji = {"lose": "⬇️", "maintain": "➡️", "gain": "⬆️"}.get(user.goal, "🎯")
            
            text = (
                f"👤 <b>Твой профиль</b>\n\n"
                f"⚖️ <b>Вес:</b> {user.weight} кг\n"
                f"📏 <b>Рост:</b> {user.height} см\n"
                f"🎂 <b>Возраст:</b> {user.age} лет\n"
                f"🚻 <b>Пол:</b> {gender_emoji}\n"
                f"🏃 <b>Активность:</b> {user.activity_level}\n"
                f"🎯 <b>Цель:</b> {goal_emoji} {user.goal}\n"
                f"🌆 <b>Город:</b> {user.city}\n\n"
                f"📊 <b>Дневные нормы:</b>\n"
                f"🔥 <b>Калории:</b> {user.daily_calorie_goal:.0f} ккал\n"
                f"🥩 <b>Белки:</b> {user.daily_protein_goal:.1f} г\n"
                f"🥑 <b>Жиры:</b> {user.daily_fat_goal:.1f} г\n"
                f"🍚 <b>Углеводы:</b> {user.daily_carbs_goal:.1f} г\n"
                f"💧 <b>Вода:</b> {user.daily_water_goal:.0f} мл"
            )
            
            await message.answer(
                text,
                reply_markup=get_edit_profile_keyboard(),
                parse_mode="HTML"
            )
        else:
            await state.set_state(ProfileStates.weight)
            await message.answer(
                "⚖️ <b>Настройка профиля</b>\n\n"
                "Введи свой вес (кг):\n<i>Пример: 75.5</i>",
                reply_markup=get_cancel_keyboard(),
                parse_mode="HTML"
            )
 except Exception as e:
            logger.error(f"❌ Profile query error: {e}", exc_info=True)
            await message.answer("❌ Ошибка загрузки профиля. Попробуйте позже.")
            return

@router.message(F.text == "✏️ Изменить профиль")
async def edit_profile(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ProfileStates.weight)
    await message.answer(
        "⚖️ <b>Изменение веса</b>\n\nВведи новый вес (кг):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(ProfileStates.weight, F.text.regexp(r'^\s*\d+([.,]\d+)?\s*$'))
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.').strip())
        
        if not 30 <= weight <= 300:
            raise ValueError
            
        await state.update_data(weight=weight)
        await state.set_state(ProfileStates.height)
        
        await message.answer(
            f"✅ Вес: <b>{weight} кг</b>\n\n📏 Введи рост (см):",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(
            "❌ Введи число от 30 до 300 кг\n<i>Примеры: 75, 75.5, 75,5</i>",
            parse_mode="HTML"
        )


@router.message(ProfileStates.height, F.text.regexp(r'^\s*\d+([.,]\d+)?\s*$'))
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text.replace(',', '.').strip())
        
        if not 100 <= height <= 250:
            raise ValueError
            
        await state.update_data(height=height)
        await state.set_state(ProfileStates.age)
        
        await message.answer(
            f"✅ Рост: <b>{height} см</b>\n\n🎂 Введи возраст:",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Введи число от 100 до 250 см", parse_mode="HTML")


@router.message(ProfileStates.age, F.text.regexp(r'^\s*\d+\s*$'))
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        
        if not 10 <= age <= 120:
            raise ValueError
            
        await state.update_data(age=age)
        await state.set_state(ProfileStates.gender)
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="♂️ Мужской")],
                [KeyboardButton(text="♀️ Женский")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        await message.answer(
            f"✅ Возраст: <b>{age} лет</b>\n\n🚻 Выбери пол:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Введи целое число от 10 до 120")


@router.message(ProfileStates.gender, F.text)
async def process_gender(message: Message, state: FSMContext):
    gender_map = {"♂️ Мужской": "male", "♀️ Женский": "female"}
    
    if message.text not in gender_map:
        await message.answer("❌ Выбери из кнопок")
        return
        
    await state.update_data(gender=gender_map[message.text])
    await state.set_state(ProfileStates.activity)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪑 Сидячий")],
            [KeyboardButton(text="🚶 Средний")],
            [KeyboardButton(text="🏃 Высокий")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        f"✅ Пол: <b>{message.text}</b>\n\n🏋️ Выбери активность:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.message(ProfileStates.activity, F.text)
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
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬇️ Похудение")],
            [KeyboardButton(text="➡️ Поддержание")],
            [KeyboardButton(text="⬆️ Набор массы")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        f"✅ Активность: <b>{message.text}</b>\n\n🎯 Выбери цель:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.message(ProfileStates.goal, F.text)
async def process_goal(message: Message, state: FSMContext):
    goal_map = {
        "⬇️ Похудение": "lose",
        "➡️ Поддержание": "maintain",
        "⬆️ Набор массы": "gain"
    }
    
    if message.text not in goal_map:
        await message.answer("❌ Выбери из кнопок")
        return
        
    await state.update_data(goal=goal_map[message.text])
    await state.set_state(ProfileStates.city)
    
    await message.answer(
        f"✅ Цель: <b>{message.text}</b>\n\n🌆 Введи город:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(ProfileStates.city, F.text)
async def process_city(message: Message, state: FSMContext):
    """Сохранение профиля с правильной погодой"""
    city = message.text.strip()
    data = await state.get_data()
    
    # 🔥 Получаем температуру через исправленный сервис
    temp = await get_temperature(city)
    logger.info(f"🌡️ Temperature for {city}: {temp}°C")
    
    water_goal = calculate_water_goal(data['weight'], data['activity'], temp)
    calorie_goal, protein, fat, carbs = calculate_calorie_goal(
        data['weight'], data['height'], data['age'],
        data['gender'], data['activity'], data['goal']
    )
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
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
        
        await session.commit()
    
    await state.clear()
    
    gender_emoji = "♂️" if data['gender'] == "male" else "♀️"
    goal_emoji = {"lose": "⬇️", "maintain": "➡️", "gain": "⬆️"}.get(data['goal'], "🎯")
    
    await message.answer(
        f"🎉 <b>Профиль сохранён!</b>\n\n"
        f"👤 {gender_emoji} {data['gender'].capitalize()}, {data['age']} лет\n"
        f"⚖️ {data['weight']} кг | 📏 {data['height']} см\n"
        f"🏃 {data['activity']} | 🎯 {goal_emoji} {data['goal']}\n"
        f"🌆 {city} ({temp}°C)\n\n"
        f"📊 <b>Твои нормы:</b>\n"
        f"🔥 Калории: <b>{calorie_goal} ккал</b>\n"
        f"🥩 Белки: {protein} г | 🥑 Жиры: {fat} г | 🍚 Углеводы: {carbs} г\n"
        f"💧 Вода: <b>{water_goal} мл</b>",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
