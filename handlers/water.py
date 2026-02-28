from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from database.db import get_session
from database.models import User, WaterEntry
from keyboards.inline import get_water_preset_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard
from utils.states import WaterStates

router = Router()

@router.message(Command("log_water"))
@router.message(F.text == "💧 Вода")
async def cmd_water(message: Message, state: FSMContext):
    await state.set_state(WaterStates.entering_amount)
    await message.answer(
        "💧 Сколько воды вы выпили?\n\nВыберите из предложенных или введите вручную:",
        reply_markup=get_water_preset_keyboard()
    )

@router.callback_query(F.data.startswith("water_"))
async def preset_water(callback: CallbackQuery, state: FSMContext):
    amount = int(callback.data.split("_")[1])
    await state.update_data(amount=amount)
    await callback.message.edit_text(
        f"Выбрано {amount} мл. Подтвердите:",
        reply_markup=get_confirmation_keyboard()
    )
    await callback.answer()

@router.message(WaterStates.entering_amount, F.text)
async def manual_water(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
        await state.update_data(amount=amount)
        await message.answer(
            f"Добавить {amount} мл воды?",
            reply_markup=get_confirmation_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите положительное число")

@router.callback_query(F.data == "confirm")
async def confirm_water(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data.get('amount')
    if not amount:
        await callback.answer("Ошибка")
        return
    
    async with get_session() as session:
        entry = WaterEntry(
            user_id=callback.from_user.id,
            amount=amount,
            datetime=datetime.now()
        )
        session.add(entry)
        await session.commit()
    
    await state.clear()
    await callback.message.edit_text(f"✅ Записано {amount} мл воды!")
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_water(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отменено")
    await callback.answer()