from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from database.db import get_session
from database.models import User, Activity
from services.calculator import calculate_activity_calories
from keyboards.inline import get_activity_type_keyboard, get_confirmation_keyboard
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from utils.states import ActivityStates
from utils.helpers import get_activity_type_emoji

router = Router()

@router.message(Command("log_activity"))
@router.message(F.text == "🔥 Активность")
async def cmd_activity(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with get_session() as session:
        user = await session.get(User, user_id)
        if not user or not user.weight:
            await message.answer("❌ Сначала настройте профиль (/set_profile)")
            return
    
    await state.set_state(ActivityStates.choosing_type)
    await message.answer(
        "Выбери тип активности:",
        reply_markup=get_activity_type_keyboard()
    )

@router.callback_query(F.data.startswith("activity_"))
async def process_activity_type(callback: CallbackQuery, state: FSMContext):
    activity_type = callback.data.split("_")[1]
    await state.update_data(activity_type=activity_type)
    await state.set_state(ActivityStates.entering_duration)
    await callback.message.edit_text("⏱️ Введите длительность в минутах:")
    await callback.answer()

@router.message(ActivityStates.entering_duration, F.text)
async def process_duration(message: Message, state: FSMContext):
    try:
        duration = int(message.text)
        if duration <= 0 or duration > 1440:
            raise ValueError
        await state.update_data(duration=duration)
        await state.set_state(ActivityStates.entering_distance)
        await message.answer("📏 Введите дистанцию в км (или 0, если не применимо):")
    except ValueError:
        await message.answer("❌ Введите число от 1 до 1440 минут")

@router.message(ActivityStates.entering_distance, F.text)
async def process_distance(message: Message, state: FSMContext):
    try:
        distance = float(message.text)
        if distance < 0:
            raise ValueError
        await state.update_data(distance=distance)
        await state.set_state(ActivityStates.entering_steps)
        await message.answer("👣 Введите количество шагов (или 0):")
    except ValueError:
        await message.answer("❌ Введите неотрицательное число")

@router.message(ActivityStates.entering_steps, F.text)
async def process_steps(message: Message, state: FSMContext):
    try:
        steps = int(message.text)
        if steps < 0:
            raise ValueError
        
        data = await state.get_data()
        user_id = message.from_user.id
        
        async with get_session() as session:
            user = await session.get(User, user_id)
            weight = user.weight if user else 70
        
        calories = calculate_activity_calories(
            data['activity_type'],
            data['duration'],
            weight,
            data['distance'],
            steps
        )
        
        await state.update_data(steps=steps, calories=calories)
        await state.set_state(ActivityStates.confirming)
        
        emoji = get_activity_type_emoji(data['activity_type'])
        await message.answer(
            f"✅ <b>{emoji} Активность</b>\n\n"
            f"Тип: {data['activity_type']}\n"
            f"⏱️ Длительность: {data['duration']} мин\n"
            f"📏 Дистанция: {data['distance']} км\n"
            f"👣 Шаги: {steps}\n"
            f"🔥 Сожжено калорий: {calories}\n\n"
            f"Всё верно?",
            reply_markup=get_confirmation_keyboard(),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Введите неотрицательное целое число")

@router.callback_query(F.data == "confirm", ActivityStates.confirming)
async def confirm_activity(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    
    async with get_session() as session:
        activity = Activity(
            user_id=user_id,
            activity_type=data['activity_type'],
            duration=data['duration'],
            distance=data['distance'],
            calories_burned=data['calories'],
            steps=data['steps'],
            source='manual',
            datetime=datetime.now()
        )
        session.add(activity)
        await session.commit()
    
    await state.clear()
    await callback.message.edit_text(f"✅ Активность записана! Сожжено {data['calories']} ккал")
    await callback.answer()

@router.callback_query(F.data == "cancel", ActivityStates.confirming)
async def cancel_activity(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Запись отменена.")
    await callback.answer()