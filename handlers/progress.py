"""
Обработчик прогресса и графиков.
✅ Выбор периода (сегодня/неделя/месяц)
✅ Progress bar для воды и калорий
✅ Графики воды, активности и баланса
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from datetime import datetime, timedelta
from database.db import get_session
from database.models import User, Meal, Activity, WaterEntry, WeightEntry
from services.plots import (
    generate_weight_plot,
    generate_water_plot,
    generate_calorie_balance_plot,
    generate_activity_plot,
)
from services.calculator import calculate_calorie_balance
from keyboards.reply import get_main_keyboard
from keyboards.inline import get_progress_options_keyboard, get_back_keyboard
from utils.states import ProgressStates

router = Router()


def _progress_bar(current: float, goal: float, length: int = 10) -> str:
    """Генерирует текстовый прогресс-бар."""
    if goal <= 0:
        return "░" * length
    filled = int((current / goal) * length)
    filled = min(filled, length)
    return "█" * filled + "░" * (length - filled)


@router.message(Command("progress"))
@router.message(F.text == "📊 Прогресс")
async def cmd_progress(message: Message, state: FSMContext):
    """Показать меню выбора периода."""
    await state.clear()
    user_id = message.from_user.id

    async with get_session() as session:
        # Проверяем существование пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile",
                reply_markup=get_main_keyboard(),
            )
            return

    await message.answer(
        "📊 Выберите период для отображения прогресса:",
        reply_markup=get_progress_options_keyboard(),
    )
    await state.set_state(ProgressStates.selecting_period)


@router.callback_query(F.data.startswith("progress_"), ProgressStates.selecting_period)
async def process_period_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора периода."""
    period = callback.data.split("_")[1]  # day / week / month
    user_id = callback.from_user.id

    await callback.message.delete()
    await state.clear()

    async with get_session() as session:
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await callback.message.answer(
                "❌ Ошибка: пользователь не найден.", reply_markup=get_main_keyboard()
            )
            return

        # Определяем диапазон дат
        today = datetime.now().date()
        if period == "day":
            start_date = today
        elif period == "week":
            start_date = today - timedelta(days=7)
        else:  # month
            start_date = today - timedelta(days=30)

        # Статистика за период
        meals_result = await session.execute(
            select(Meal).where(
                Meal.user_id == user.id,
                func.date(Meal.datetime) >= start_date,
            )
        )
        meals = meals_result.scalars().all()

        activities_result = await session.execute(
            select(Activity).where(
                Activity.user_id == user.id,
                func.date(Activity.datetime) >= start_date,
            )
        )
        activities = activities_result.scalars().all()

        water_result = await session.execute(
            select(WaterEntry).where(
                WaterEntry.user_id == user.id,
                func.date(WaterEntry.datetime) >= start_date,
            )
        )
        water_entries = water_result.scalars().all()

        weight_result = await session.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user.id,
                func.date(WeightEntry.datetime) >= start_date,
            )
        )
        weight_entries = weight_result.scalars().all()

    # Суммируем за период
    total_cal_consumed = sum(m.total_calories or 0 for m in meals)
    total_cal_burned = sum(a.calories_burned or 0 for a in activities)
    total_water = sum(w.amount or 0 for w in water_entries)

    # Расчёт средних
    days_count = (datetime.now().date() - start_date).days + 1
    avg_cal_consumed = total_cal_consumed / days_count if days_count else 0
    avg_cal_burned = total_cal_burned / days_count if days_count else 0
    avg_water = total_water / days_count if days_count else 0

    # Прогресс-бары (на основе цели пользователя)
    water_bar = _progress_bar(avg_water, user.daily_water_goal)
    calorie_bar = _progress_bar(avg_cal_consumed, user.daily_calorie_goal)

    period_names = {"day": "сегодня", "week": "за 7 дней", "month": "за 30 дней"}

    text = (
        f"📊 <b>Прогресс {period_names[period]}</b>\n\n"
        f"🔥 <b>Калории:</b>\n"
        f"   Потреблено: {total_cal_consumed:.0f} ккал\n"
        f"   Сожжено: {total_cal_burned:.0f} ккал\n"
        f"   Баланс: {total_cal_consumed - total_cal_burned:.0f} ккал\n"
        f"   Среднее потребление: {avg_cal_consumed:.0f} ккал/день\n"
        f"   {calorie_bar} {avg_cal_consumed:.0f}/{user.daily_calorie_goal:.0f} ккал\n\n"
        f"💧 <b>Вода:</b>\n"
        f"   Всего: {total_water:.0f} мл\n"
        f"   Среднее: {avg_water:.0f} мл/день\n"
        f"   {water_bar} {avg_water:.0f}/{user.daily_water_goal:.0f} мл\n"
    )

    await callback.message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")

    # Генерация графиков (если есть данные)
    # График веса (все записи, не только за период)
    weight_plot = await generate_weight_plot(user.id, session)
    if weight_plot:
        await callback.message.answer_photo(
            BufferedInputFile(weight_plot, filename="weight.png"),
            caption="📈 Динамика веса (все записи)",
        )

    # График воды за период
    water_plot = await generate_water_plot(user.id, session, days=30 if period == "month" else 7)
    if water_plot:
        await callback.message.answer_photo(
            BufferedInputFile(water_plot, filename="water.png"),
            caption=f"💧 Потребление воды {period_names[period]}",
        )

    # График баланса калорий за период
    calorie_plot = await generate_calorie_balance_plot(user.id, session, days=30 if period == "month" else 7)
    if calorie_plot:
        await callback.message.answer_photo(
            BufferedInputFile(calorie_plot, filename="calories.png"),
            caption=f"🔥 Баланс калорий {period_names[period]}",
        )

    # График активности за период
    activity_plot = await generate_activity_plot(user.id, session, days=30 if period == "month" else 7)
    if activity_plot:
        await callback.message.answer_photo(
            BufferedInputFile(activity_plot, filename="activity.png"),
            caption=f"🏃 Активность {period_names[period]}",
        )
