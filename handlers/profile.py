"""
Обработчик профиля пользователя
✅ Все запросы к БД — асинхронные
✅ Нет lazy loading в клавиатурах
✅ Универсальная функция display_profile для проверки и отображения
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.db import get_session
from database.models import User
from services.calculator import calculate_water_goal, calculate_calorie_goal
from services.weather import get_temperature
from keyboards.reply import get_cancel_keyboard, get_main_keyboard, get_edit_profile_keyboard
from utils.states import ProfileStates

logger = logging.getLogger(__name__)
router = Router()

# Список обязательных полей профиля
REQUIRED_FIELDS = ['weight', 'height', 'age', 'gender', 'activity_level', 'goal', 'city']

async def is_profile_complete(user) -> bool:
    """Проверяет, заполнены ли все обязательные поля профиля."""
    if not user:
        return False
    for field in REQUIRED_FIELDS:
        if getattr(user, field) is None:
            return False
    return True

async def display_profile(target: Message | CallbackQuery, user_id: int, state: FSMContext = None):
    """
    Универсальная функция для отображения профиля.
    Если профиль не заполнен и передан state, запускает процесс настройки.
    Если state не передан, просто сообщает о необходимости настройки.
    """
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user and await is_profile_complete(user):
            # Профиль полностью заполнен — показываем данные
            gender_emoji = "♂️" if user.gender == "male" else "♀️"
            goal_emoji = {"lose": "⬇️", "maintain": "➡️", "gain": "⬆️"}.get(user.goal, "🎯")

            text = (
                f"👤 <b>Твой профиль</b>\n\n"
                f"⚖️ Вес: {user.weight} кг\n"
                f"📏 Рост: {user.height} см\n"
                f"🎂 Возраст: {user.age} лет\n"
                f"🚻 Пол: {gender_emoji}\n"
                f"🏃 Активность: {user.activity_level}\n"
                f"🎯 Цель: {goal_emoji} {user.goal}\n"
                f"🌆 Город: {user.city}\n\n"
                f"📊 <b>Нормы:</b>\n"
                f"🔥 Калории: {user.daily_calorie_goal:.0f} ккал\n"
                f"🥩 Белки: {user.daily_protein_goal:.1f} г\n"
                f"🥑 Жиры: {user.daily_fat_goal:.1f} г\n"
                f"🍚 Углеводы: {user.daily_carbs_goal:.1f} г\n"
                f"💧 Вода: {user.daily_water_goal:.0f} мл"
            )

            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="✏️ Изменить профиль")],
                    [KeyboardButton(text="📊 Прогресс")],
                    [KeyboardButton(text="🏠 Главное меню")]
                ],
                resize_keyboard=True
            )

            if isinstance(target, Message):
                await target.answer(text, reply_markup=keyboard, parse_mode="HTML")
            else:
                await target.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
                await target.answer()
        else:
            # Профиль неполный или отсутствует
            if state is not None:
                # Запускаем процесс настройки
                await state.set_state(ProfileStates.weight)
                msg = "⚖️ <b>Настройка профиля</b>\n\nВведи вес (кг):"
                if isinstance(target, Message):
                    await target.answer(msg, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
                else:
                    await target.message.answer(msg, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
                    await target.answer()
            else:
                # Просто сообщаем о необходимости настройки
                msg = "❌ Профиль не заполнен. Используйте /set_profile для настройки."
                if isinstance(target, Message):
                    await target.answer(msg, reply_markup=get_main_keyboard())
                else:
                    await target.message.answer(msg, reply_markup=get_main_keyboard())
                    await target.answer()

@router.message(Command("set_profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, state: FSMContext, user_id: int = None):
    """Показать профиль или начать настройку."""
    if user_id is None:
        user_id = message.from_user.id
    await display_profile(message, user_id, state)

@router.message(F.text == "✏️ Изменить профиль")
async def edit_profile(message: Message, state: FSMContext, user_id: int = None):
    """Начало редактирования профиля."""
    if user_id is None:
        user_id = message.from_user.id
    await state.clear()
    await state.set_state(ProfileStates.weight)
    await message.answer(
        "⚖️ Введи новый вес (кг):",
        reply_markup=get_cancel_keyboard()
    )

@router.message(ProfileStates.weight)
async def process_weight(message: Message, state: FSMContext):
    """Ввод веса — надёжный парсинг"""
    try:
        text = message.text.strip()
        import re
        match = re.search(r'(\d+([.,]\d+)?)', text)

        if match:
            weight_str = match.group(1).replace(',', '.')
            weight = float(weight_str)
        else:
            weight = float(text.replace(',', '.'))

        if not 30 <= weight <= 300:
            raise ValueError("Вес вне диапазона")

        await state.update_data(weight=weight)
        await state.set_state(ProfileStates.height)
        await message.answer(f"✅ {weight} кг\n\n📏 Введи рост (см):")

    except (ValueError, IndexError, AttributeError, TypeError) as e:
        logger.warning(f"⚠️ Weight parse error: {e}")
        await message.answer(
            "❌ Введи число от 30 до 300 кг\n"
            "<i>Примеры: 75, 75.5, 75,5</i>",
            parse_mode="HTML"
        )

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    """Ввод роста"""
    try:
        text = message.text.strip()
        import re
        match = re.search(r'(\d+([.,]\d+)?)', text)

        if match:
            height_str = match.group(1).replace(',', '.')
            height = float(height_str)
        else:
            height = float(text.replace(',', '.'))

        if not 100 <= height <= 250:
            raise ValueError("Рост вне диапазона")

        await state.update_data(height=height)
        await state.set_state(ProfileStates.age)
        await message.answer(f"✅ {height} см\n\n🎂 Введи возраст:")

    except (ValueError, IndexError, AttributeError, TypeError):
        await message.answer("❌ Введи число от 100 до 250")

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    """Ввод возраста"""
    try:
        age = int(message.text.strip())
        if not 10 <= age <= 120:
            raise ValueError("Возраст вне диапазона")

        await state.update_data(age=age)
        await state.set_state(ProfileStates.gender)

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="♂️ Мужской")],
                [KeyboardButton(text="♀️ Женский")]
            ],
            resize_keyboard=True
        )
        await message.answer(f"✅ {age} лет\n\n🚻 Выбери пол:", reply_markup=keyboard)

    except (ValueError, TypeError):
        await message.answer("❌ Введи целое число от 10 до 120")

@router.message(ProfileStates.gender)
async def process_gender(message: Message, state: FSMContext):
    """Выбор пола"""
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
        resize_keyboard=True
    )
    await message.answer(f"✅ {message.text}\n\n🏋️ Активность:", reply_markup=keyboard)

@router.message(ProfileStates.activity)
async def process_activity(message: Message, state: FSMContext):
    """Выбор активности"""
    act_map = {"🪑 Сидячий": "low", "🚶 Средний": "medium", "🏃 Высокий": "high"}

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
        resize_keyboard=True
    )
    await message.answer(f"✅ {message.text}\n\n🎯 Цель:", reply_markup=keyboard)

@router.message(ProfileStates.goal)
async def process_goal(message: Message, state: FSMContext):
    """Выбор цели"""
    goal_map = {"⬇️ Похудение": "lose", "➡️ Поддержание": "maintain", "⬆️ Набор массы": "gain"}

    if message.text not in goal_map:
        await message.answer("❌ Выбери из кнопок")
        return

    await state.update_data(goal=goal_map[message.text])
    await state.set_state(ProfileStates.city)
    await message.answer(f"✅ {message.text}\n\n🌆 Город:", reply_markup=get_cancel_keyboard())

@router.message(ProfileStates.city)
async def process_city(message: Message, state: FSMContext):
    """Сохранение профиля с обработкой ошибок"""
    city = message.text.strip()
    data = await state.get_data()

    # Проверяем, что все необходимые данные есть
    required_fields = ['weight', 'height', 'age', 'gender', 'activity', 'goal']
    missing = [field for field in required_fields if field not in data]
    if missing:
        logger.error(f"Missing fields in state: {missing}")
        await message.answer(
            "❌ Произошла ошибка: не все данные профиля были заполнены. Начните заново.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return

    try:
        # Получаем температуру (всегда число, даже при ошибке)
        temp = await get_temperature(city)

        # Рассчитываем нормы
        water_goal = calculate_water_goal(data['weight'], data['activity'], temp)
        calorie_goal, protein, fat, carbs = calculate_calorie_goal(
            data['weight'], data['height'], data['age'],
            data['gender'], data['activity'], data['goal']
        )

        # Сохраняем в БД
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
            logger.info(f"✅ Profile saved for user {message.from_user.id}")

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

    except Exception as e:
        logger.error(f"❌ Error saving profile: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла внутренняя ошибка при сохранении профиля. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
