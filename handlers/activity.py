"""
Обработчик активности для NutriBuddy.
✅ Для ходьбы теперь используется отдельный пункт "Записать шаги".
✅ Для остальных типов активности сохраняется ввод времени.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from datetime import datetime
from database.db import get_session
from database.models import User, Activity
from keyboards.inline import get_activity_type_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import ActivityStates, StepsStates
from services.activity import CALORIES_PER_MINUTE  # импортируем общий словарь

router = Router()

# Функция для проверки наличия профиля
async def check_user_exists(user_id: int) -> bool:
    """Проверяет, существует ли пользователь в БД."""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        return result.scalar_one_or_none() is not None

@router.message(Command("fitness"))
@router.message(F.text == "🏋️ Активность")
async def cmd_fitness(message: Message, state: FSMContext):
    """Начало записи активности (выбор типа)."""
    # Проверяем, есть ли профиль
    if not await check_user_exists(message.from_user.id):
        await message.answer(
            "❌ Сначала настройте профиль через /set_profile.",
            reply_markup=get_main_keyboard()
        )
        return

    await state.clear()
    await state.set_state(ActivityStates.manual_type)
    await message.answer(
        "🏋️ <b>Запись активности</b>\n\n"
        "Выберите тип активности (ходьба теперь записывается через 'Записать шаги'):",
        reply_markup=get_activity_type_keyboard()
    )

@router.callback_query(F.data.startswith("activity_"), ActivityStates.manual_type)
async def process_activity_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа активности."""
    act_type = callback.data.split("_")[1]
    await state.update_data(activity_type=act_type)
    await state.set_state(ActivityStates.manual_duration)

    type_names = {
        "walking": "🚶 Ходьба (используйте пункт 'Записать шаги')",
        "running": "🏃 Бег",
        "cycling": "🚴 Велосипед",
        "gym": "🏋️ Тренажёрный зал",
        "yoga": "🧘 Йога",
        "swimming": "🏊 Плавание",
        "other": "🎾 Другое"
    }

    await callback.message.edit_text(
        f"✅ Тип: <b>{type_names.get(act_type, act_type)}</b>\n\n"
        "⏱️ <b>Сколько длилась тренировка?</b>\n"
        "Введите длительность в минутах:\n"
        "<i>Пример: 30, 45, 60</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(ActivityStates.manual_duration, F.text.regexp(r'^\s*\d+\s*$'))
async def process_duration(message: Message, state: FSMContext):
    """Ввод длительности."""
    try:
        duration = int(message.text.strip())
        if not 1 <= duration <= 480:
            raise ValueError

        data = await state.get_data()
        act_type = data.get('activity_type', 'other')

        # Получаем вес пользователя
        user_id = message.from_user.id
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                await message.answer("❌ Профиль не найден.")
                return
            weight = user.weight or 70

        met = CALORIES_PER_MINUTE.get(act_type, 5)
        calories = met * weight * (duration / 60)   # ИСПРАВЛЕНО

        await state.update_data(duration=duration, calories=calories)
        await state.set_state(ActivityStates.confirming)

        type_names = {
            "walking": "🚶 Ходьба (используйте пункт 'Записать шаги')",
            "running": "🏃 Бег",
            "cycling": "🚴 Велосипед",
            "gym": "🏋️ Тренажёрный зал",
            "yoga": "🧘 Йога",
            "swimming": "🏊 Плавание",
            "other": "🎾 Другое"
        }

        await message.answer(
            f"✅ <b>Подтверждение</b>\n\n"
            f"🏃 {type_names.get(act_type, act_type)}\n"
            f"⏱️ {duration} минут\n"
            f"🔥 {calories:.0f} ккал\n\n"
            f"Всё верно?",
            reply_markup=get_confirmation_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите число от 1 до 480 минут")

@router.callback_query(F.data == "confirm", ActivityStates.confirming)
async def confirm_activity(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение активности."""
    data = await state.get_data()
    user_id = callback.from_user.id

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден.")
            await state.clear()
            return
        weight = user.weight or 70

        activity = Activity(
            user_id=user.id,
            activity_type=data['activity_type'],
            duration=data['duration'],
            distance=0,
            calories_burned=data['calories'],  # уже пересчитано в process_duration
            steps=0,
            datetime=datetime.now(),
            source='manual'
        )
        session.add(activity)
        await session.commit()

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Активность записана!</b>\n\n"
        f"🔥 +{data['calories']:.0f} ккал к сегодняшнему балансу",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "cancel", ActivityStates.confirming)
async def cancel_activity(callback: CallbackQuery, state: FSMContext):
    """Отмена записи активности."""
    await state.clear()
    await callback.message.edit_text("❌ Запись отменена.")
    await callback.answer()

# ========== Обработчик для шагов ==========

@router.message(StepsStates.waiting_for_steps, F.text)
async def process_steps_input(message: Message, state: FSMContext):
    """Обрабатывает ввод количества шагов."""
    try:
        steps = int(message.text.strip())
        if steps <= 0 or steps > 100000:
            raise ValueError
    except ValueError:
        await message.answer("❌ Пожалуйста, введите целое положительное число (до 100000).")
        return

    user_id = message.from_user.id
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала настройте профиль через /set_profile.")
            await state.clear()
            return

        # Приблизительный расчёт: 0.04 ккал на шаг (зависит от веса)
        calories = round(steps * 0.04, 1)
        activity = Activity(
            user_id=user.id,
            activity_type="walking",
            duration=0,
            distance=steps * 0.00075,
            calories_burned=calories,
            steps=steps,
            datetime=datetime.now(),
            source="manual"
        )
        session.add(activity)
        await session.commit()

    await message.answer(f"✅ Записано {steps} шагов (сожжено ~{calories} ккал).")
    await state.clear()
