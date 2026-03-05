"""
Обработчик для записи веса.
Позволяет пользователю вводить текущий вес, сохраняет его в базу данных.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from datetime import datetime

from database.db import get_session
from database.models import User, WeightEntry
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import WeightStates

router = Router()

@router.message(Command("log_weight"))
@router.message(F.text == "⚖️ Записать вес")
async def cmd_log_weight(message: Message, state: FSMContext):
    """Начало записи веса."""
    user_id = message.from_user.id

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile.",
                reply_markup=get_main_keyboard()
            )
            return

    await state.set_state(WeightStates.waiting_for_weight)
    await message.answer(
        "⚖️ Введите ваш текущий вес в килограммах (только число, например: 75.5):",
        reply_markup=get_cancel_keyboard()
    )

@router.message(WeightStates.waiting_for_weight, F.text)
async def process_weight_input(message: Message, state: FSMContext):
    """Обработка введённого веса."""
    text = message.text.strip()
    try:
        # Парсим число (может быть с точкой или запятой)
        weight = float(text.replace(',', '.'))
        if weight <= 0 or weight > 500:
            raise ValueError("Вес вне допустимого диапазона (1-500 кг)")
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число (например: 70.5)")
        return

    user_id = message.from_user.id
    async with get_session() as session:
        # Получаем пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        # Сохраняем запись веса
        weight_entry = WeightEntry(
            user_id=user.id,
            weight=weight,
            datetime=datetime.now()
        )
        session.add(weight_entry)
        await session.commit()

    await state.clear()
    await message.answer(
        f"✅ Вес {weight:.1f} кг записан!\n\n"
        f"Вы можете посмотреть динамику в разделе 📊 Прогресс.",
        reply_markup=get_main_keyboard()
    )
