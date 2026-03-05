"""
Обработчик трекера воды.
✅ Исправлено: уникальные callback_data для кнопок подтверждения.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from datetime import datetime
from database.db import get_session
from database.models import User, WaterEntry
from keyboards.inline import get_water_preset_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import WaterStates

router = Router()

async def add_water_quick(telegram_id: int, amount: int) -> bool:
    """Быстрое добавление воды без диалога с логированием."""
    logger.info(f"💧 add_water_quick: начало для user_id={telegram_id}, amount={amount}")
    try:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                logger.warning(f"💧 add_water_quick: пользователь {telegram_id} не найден")
                return False
            logger.info(f"💧 add_water_quick: пользователь найден, user_id={user.id}")
            entry = WaterEntry(
                user_id=user.id,
                amount=amount,
                datetime=datetime.now()
            )
            session.add(entry)
            await session.commit()
            logger.info(f"💧 add_water_quick: успешно записано {amount} мл")
            return True
    except Exception as e:
        logger.error(f"💧 add_water_quick: ошибка {e}", exc_info=True)
        return False
        
@router.message(Command("log_water"))
@router.message(F.text == "💧 Вода")
async def cmd_water(message: Message, state: FSMContext, user_id: int = None):
    """Начало записи воды."""
    if user_id is None:
        user_id = message.from_user.id

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile.",
                reply_markup=get_main_keyboard()
            )
            return

    await state.set_state(WaterStates.entering_amount)

    today = datetime.now().date()
    async with get_session() as session:
        result = await session.execute(
            select(func.sum(WaterEntry.amount)).where(
                WaterEntry.user_id == user.id,
                func.date(WaterEntry.datetime) == today
            )
        )
        consumed = result.scalar() or 0
        goal = user.daily_water_goal

    progress = min(100, int(consumed / goal * 100)) if goal > 0 else 0
    await message.answer(
        f"💧 <b>Водный баланс</b>\n\n"
        f"📊 Выпито сегодня: {consumed:.0f} / {goal:.0f} мл ({progress}%)\n\n"
        f"Сколько воды выпили?",
        reply_markup=get_water_preset_keyboard()
    )

# ✅ Исправлено: обработчик только для числовых значений (water_200, water_500 и т.д.)
@router.callback_query(F.data.regexp(r'^water_(\d+)$'))
async def preset_water(callback: CallbackQuery, state: FSMContext):
    """Выбор предустановленного объёма."""
    try:
        amount = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    await state.update_data(amount=amount)
    await state.set_state(WaterStates.confirming)
    await callback.message.edit_text(
        f"💧 Добавить {amount} мл?",
        reply_markup=get_confirmation_keyboard("water")
    )
    await callback.answer()

@router.message(WaterStates.entering_amount)
async def manual_water(message: Message, state: FSMContext):
    """Ручной ввод объёма."""
    text = message.text.strip()
    try:
        import re
        match = re.search(r'\d+([.,]\d+)?', text)
        amount = float(match.group(0).replace(',', '.')) if match else float(text.replace(',', '.'))
        if not 0 < amount <= 5000:
            raise ValueError
    except:
        await message.answer("❌ Введите число от 1 до 5000 мл\n<i>Примеры: 200, 500</i>", parse_mode="HTML")
        return
    await state.update_data(amount=amount)
    await state.set_state(WaterStates.confirming)
    await message.answer(
        f"💧 Добавить {amount:.0f} мл?",
        reply_markup=get_confirmation_keyboard("water")
    )

@router.callback_query(F.data == "confirm_water", WaterStates.confirming)
async def confirm_water(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение воды."""
    data = await state.get_data()
    amount = data.get('amount')
    if not amount:
        await callback.answer("❌ Ошибка", show_alert=True)
        return

    telegram_id = callback.from_user.id
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await callback.answer("❌ Профиль не найден", show_alert=True)
            await state.clear()
            return

        entry = WaterEntry(
            user_id=user.id,
            amount=amount,
            datetime=datetime.now()
        )
        session.add(entry)
        await session.commit()

        today = datetime.now().date()
        result = await session.execute(
            select(func.sum(WaterEntry.amount)).where(
                WaterEntry.user_id == user.id,
                func.date(WaterEntry.datetime) == today
            )
        )
        consumed = result.scalar() or 0
        goal = user.daily_water_goal

    await state.clear()
    progress = min(100, int(consumed / goal * 100))
    await callback.message.edit_text(
        f"✅ Записано {amount:.0f} мл!\n"
        f"📊 Всего: {consumed:.0f} / {goal:.0f} мл ({progress}%)"
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_water", WaterStates.confirming)
async def cancel_water(callback: CallbackQuery, state: FSMContext):
    """Отмена добавления воды."""
    await state.clear()
    await callback.message.edit_text("❌ Отменено")
    await callback.answer()
