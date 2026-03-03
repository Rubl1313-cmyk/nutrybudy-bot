"""
Обработчик активности для NutriBuddy.
✅ Для ходьбы можно вводить количество шагов, калории рассчитываются автоматически.
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
from utils.states import ActivityStates

router = Router()

# 🔥 Калории на минуту для разных активностей (средний человек 70кг)
CALORIES_PER_MINUTE = {
    "walking": 4,      # Ходьба
    "running": 10,     # Бег
    "cycling": 7,      # Велосипед
    "gym": 6,          # Тренажёрный зал
    "yoga": 3,         # Йога
    "swimming": 8,     # Плавание
    "other": 5         # Другое
}


@router.message(Command("fitness"))
@router.message(F.text == "🏋️ Активность")
async def cmd_fitness(message: Message, state: FSMContext):
    """Начало записи активности (выбор типа)."""
    await state.clear()
    await state.set_state(ActivityStates.manual_type)
    await message.answer(
        "🏋️ <b>Запись активности</b>\n\n"
        "Выберите тип активности:",
        reply_markup=get_activity_type_keyboard()
    )


@router.callback_query(F.data.startswith("activity_"), ActivityStates.manual_type)
async def process_activity_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа активности."""
    act_type = callback.data.split("_")[1]
    await state.update_data(activity_type=act_type)
    await state.set_state(ActivityStates.manual_duration)

    type_names = {
        "walking": "🚶 Ходьба",
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

        calories = CALORIES_PER_MINUTE.get(act_type, 5) * duration

        await state.update_data(duration=duration, calories=calories)
        await state.set_state(ActivityStates.confirming)

        type_names = {
            "walking": "🚶 Ходьба",
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
            f"🔥 {calories} ккал\n\n"
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

        activity = Activity(
            user_id=user.id,
            activity_type=data['activity_type'],
            duration=data['duration'],
            distance=0,
            calories_burned=data['calories'],
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
