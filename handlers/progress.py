"""
Обработчик прогресса и графиков.
✅ Выбор периода (сегодня/неделя/месяц)
✅ Progress bar для воды и калорий
✅ Графики воды, активности и баланса с учётом периода
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
    generate_calorie_plot,
    generate_activity_plot,
)
from services.calculator import calculate_calorie_balance
from keyboards.reply import get_main_keyboard
from keyboards.inline import get_progress_options_keyboard
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
        # Сохраним цель воды для последующего использования
        daily_water_goal = user.daily_water_goal
        daily_calorie_goal = user.daily_calorie_goal

    await message.answer(
        "📊 Выберите период для отображения прогресса:",
        reply_markup=get_progress_options_keyboard(),
    )
    await state.set_state(ProgressStates.selecting_period)
    await state.update_data(
        daily_water_goal=daily_water_goal,
        daily_calorie_goal=daily_calorie_goal
    )


@router.callback_query(F.data.startswith("progress_"), ProgressStates.selecting_period)
async def process_period_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора периода."""
    period = callback.data.split("_")[1]  # day / week / month
    user_id = callback.from_user.id
    data = await state.get_data()
    daily_water_goal = data.get('daily_water_goal', 2000)
    daily_calorie_goal = data.get('daily_calorie_goal', 2000)

    await callback.message.delete()
    await state.clear()

    async with get_session() as session:
        # Получаем пользователя для проверки существования (необязательно, но оставим)
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await callback.message.answer(
                "❌ Пользователь не найден.",
                reply_markup=get_main_keyboard()
            )
            return

    # Генерируем графики в зависимости от периода
    if period == 'day':
        # График воды за день
        water_plot = await generate_water_plot(user_id, session, period='day', daily_goal=daily_water_goal)
        if water_plot:
            await callback.message.answer_photo(
                BufferedInputFile(water_plot, filename="water_day.png"),
                caption="💧 Потребление воды (почасово + итоги)"
            )
        else:
            await callback.message.answer("💧 Нет данных о воде за сегодня.")

        # График калорий за день
        calorie_plot = await generate_calorie_plot(user_id, session, period='day', daily_goal=daily_calorie_goal)
        if calorie_plot:
            await callback.message.answer_photo(
                BufferedInputFile(calorie_plot, filename="calories_day.png"),
                caption="🔥 Потребление калорий (почасово + итоги)"
            )
        else:
            await callback.message.answer("🔥 Нет данных о питании за сегодня.")

        # График активности за день
        activity_plot = await generate_activity_plot(user_id, session, period='day')
        if activity_plot:
            await callback.message.answer_photo(
                BufferedInputFile(activity_plot, filename="activity_day.png"),
                caption="🏃 Активность (почасово)"
            )
        else:
            await callback.message.answer("🏃 Нет данных об активности за сегодня.")

    elif period == 'week':
        # График воды за неделю
        water_plot = await generate_water_plot(user_id, session, period='week')
        if water_plot:
            await callback.message.answer_photo(
                BufferedInputFile(water_plot, filename="water_week.png"),
                caption="💧 Потребление воды за 7 дней"
            )
        else:
            await callback.message.answer("💧 Нет данных о воде за неделю.")

        # График калорий за неделю
        calorie_plot = await generate_calorie_plot(user_id, session, period='week')
        if calorie_plot:
            await callback.message.answer_photo(
                BufferedInputFile(calorie_plot, filename="calories_week.png"),
                caption="🔥 Потребление калорий за 7 дней"
            )
        else:
            await callback.message.answer("🔥 Нет данных о питании за неделю.")

        # График активности за неделю
        activity_plot = await generate_activity_plot(user_id, session, period='week')
        if activity_plot:
            await callback.message.answer_photo(
                BufferedInputFile(activity_plot, filename="activity_week.png"),
                caption="🏃 Активность за 7 дней"
            )
        else:
            await callback.message.answer("🏃 Нет данных об активности за неделю.")

    else:  # month
        # График воды за месяц
        water_plot = await generate_water_plot(user_id, session, period='month')
        if water_plot:
            await callback.message.answer_photo(
                BufferedInputFile(water_plot, filename="water_month.png"),
                caption="💧 Потребление воды за 30 дней"
            )
        else:
            await callback.message.answer("💧 Нет данных о воде за месяц.")

        # График калорий за месяц
        calorie_plot = await generate_calorie_plot(user_id, session, period='month')
        if calorie_plot:
            await callback.message.answer_photo(
                BufferedInputFile(calorie_plot, filename="calories_month.png"),
                caption="🔥 Потребление калорий за 30 дней"
            )
        else:
            await callback.message.answer("🔥 Нет данных о питании за месяц.")

        # График активности за месяц
        activity_plot = await generate_activity_plot(user_id, session, period='month')
        if activity_plot:
            await callback.message.answer_photo(
                BufferedInputFile(activity_plot, filename="activity_month.png"),
                caption="🏃 Активность за 30 дней"
            )
        else:
            await callback.message.answer("🏃 Нет данных об активности за месяц.")

    # График веса (всегда все записи)
    weight_plot = await generate_weight_plot(user_id, session)
    if weight_plot:
        await callback.message.answer_photo(
            BufferedInputFile(weight_plot, filename="weight.png"),
            caption="📈 Динамика веса (все записи)"
        )

    await callback.message.answer(
        "📊 Выберите другой период или вернитесь в меню.",
        reply_markup=get_main_keyboard()
    )
