"""
Обработчик прогресса и графиков
✅ Исправлен поиск пользователя по telegram_id
✅ Вода теперь отображается
"""
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from sqlalchemy import select, func
from datetime import datetime
from database.db import get_session
from database.models import User, Meal, Activity, WaterEntry, WeightEntry
from services.plots import generate_weight_plot, generate_calorie_balance_plot
from services.calculator import calculate_calorie_balance
from keyboards.reply import get_main_keyboard
from utils.states import WeightStates

router = Router()


@router.message(Command("progress"))
@router.message(F.text == "📊 Прогресс")
async def cmd_progress(message: Message):
    user_telegram_id = message.from_user.id

    async with get_session() as session:
        # Ищем пользователя по telegram_id
        result = await session.execute(
            select(User).where(User.telegram_id == user_telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.weight:
            await message.answer(
                "❌ <b>Сначала настройте профиль!</b>\n\n"
                "Нажмите 👤 Профиль или введите /set_profile",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            return

        today = datetime.now().date()

        # Калории из еды
        meals_result = await session.execute(
            select(func.sum(Meal.total_calories)).where(
                Meal.user_id == user.id,
                func.date(Meal.datetime) == today
            )
        )
        consumed = meals_result.scalar() or 0

        # Сожжённые калории (активность)
        activities_result = await session.execute(
            select(func.sum(Activity.calories_burned)).where(
                Activity.user_id == user.id,
                func.date(Activity.datetime) == today
            )
        )
        burned = activities_result.scalar() or 0

        # Вода
        water_result = await session.execute(
            select(func.sum(WaterEntry.amount)).where(
                WaterEntry.user_id == user.id,
                func.date(WaterEntry.datetime) == today
            )
        )
        water = water_result.scalar() or 0

        balance = calculate_calorie_balance(consumed, burned, user.daily_calorie_goal)

        text = (
            f"📊 <b>Прогресс за сегодня</b>\n\n"
            f"🔥 <b>Калории:</b>\n"
            f"   Потреблено: {balance['consumed']} ккал\n"
            f"   Сожжено: {balance['burned']} ккал\n"
            f"   Баланс: {balance['balance']} ккал\n"
            f"   Осталось: {balance['remaining']} ккал\n"
            f"   Статус: {balance['status']}\n\n"
            f"💧 <b>Вода:</b> {water:.0f} / {user.daily_water_goal:.0f} мл\n"
        )

        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")

        # Графики (если есть)
        weight_plot = await generate_weight_plot(user.id, session)
        if weight_plot:
            await message.answer_photo(
                BufferedInputFile(weight_plot, filename="weight.png"),
                caption="📈 Динамика веса"
            )

        calorie_plot = await generate_calorie_balance_plot(user.id, session)
        if calorie_plot:
            await message.answer_photo(
                BufferedInputFile(calorie_plot, filename="calories.png"),
                caption="🔥 Баланс калорий за 7 дней"
            )
