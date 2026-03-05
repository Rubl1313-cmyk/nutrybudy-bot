"""
Обработчик профиля пользователя
✅ Все запросы к БД — асинхронные
✅ Нет lazy loading в клавиатурах
"""
import logging
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

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("set_profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, state: FSMContext, user_id: int = None):
    """Показать профиль или начать настройку"""
    await state.clear()

    if user_id is None:
        user_id = message.from_user.id

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user and user.weight and user.height:
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

            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await state.set_state(ProfileStates.weight)
            await message.answer(
                "⚖️ <b>Настройка профиля</b>\n\n"
                "Введи вес (кг):",
                reply_markup=get_cancel_keyboard(),
                parse_mode="HTML"
            )

@router.message(F.text == "✏️ Изменить профиль")
async def edit_profile(message: Message, state: FSMContext, user_id: int = None):
    await state.clear()
    await state.set_state(ProfileStates.weight)
    await message.answer(
        "⚖️ Введи новый вес (кг):",
        reply_markup=get_cancel_keyboard()
    )

# ... остальные функции (process_weight, process_height и т.д.) без изменений, 
# так как они работают с состоянием и message.from_user.id
