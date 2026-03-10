"""
🎨 Современный обработчик прогресса и статистики NutriBuddy Bot
✨ Визуально привлекательный интерфейс с мотивацией и достижениями
📊 Умная аналитика и тренды
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
from utils.ui_templates import (
    ProgressBar, NutritionCard, WaterTracker, 
    ActivityCard, StreakCard, StatisticsCard
)
from utils.message_templates import MessageTemplates
from utils.animations import AnimationEngine
from keyboards.improved_keyboards import get_time_period_keyboard
from utils.states import ProgressStates

router = Router()

@router.message(Command("progress"))
@router.message(F.text == "📊 Прогресс")
async def cmd_progress(message: Message, state: FSMContext, user_id: int = None):
    """🎨 Показать современное меню прогресса"""
    target_user_id = user_id or message.from_user.id

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == target_user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile",
                reply_markup=get_main_keyboard(),
            )
            return

    # 🎨 Современное приветствие прогресса
    welcome_text = MessageTemplates.get_progress_welcome(user.first_name or "Пользователь")
    
    # 🎨 Современная клавиатура выбора периода
    keyboard = get_time_period_keyboard()
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

# Убираем дублирующий обработчик, так как он есть в common.py
# @router.callback_query(F.data.startswith("period_"))
# async def process_progress_period(callback: CallbackQuery, state: FSMContext):

async def _get_period_stats(user_id: int, session, start_date) -> dict:
    """📊 Получение статистики за период"""
    # Статистика приемов пищи
    meals_result = await session.execute(
        select(Meal).where(
            Meal.user_id == user_id,
            func.date(Meal.datetime) >= start_date,
        )
    )
    meals = meals_result.scalars().all()

    # Статистика активности
    activities_result = await session.execute(
        select(Activity).where(
            Activity.user_id == user_id,
            func.date(Activity.datetime) >= start_date,
        )
    )
    activities = activities_result.scalars().all()

    # Статистика воды
    water_result = await session.execute(
        select(WaterEntry).where(
            WaterEntry.user_id == user_id,
            func.date(WaterEntry.datetime) >= start_date,
        )
    )
    water_entries = water_result.scalars().all()

    # Статистика веса
    weight_result = await session.execute(
        select(WeightEntry).where(
            WeightEntry.user_id == user_id,
            func.date(WeightEntry.datetime) >= start_date,
        )
    )
    weight_entries = weight_result.scalars().all()

    # Суммируем за период
    total_cal_consumed = sum(m.total_calories or 0 for m in meals)
    total_protein = sum(m.total_protein or 0 for m in meals)
    total_fat = sum(m.total_fat or 0 for m in meals)
    total_carbs = sum(m.total_carbs or 0 for m in meals)
    total_cal_burned = sum(a.calories_burned or 0 for a in activities)
    total_water = sum(w.amount or 0 for w in water_entries)

    # Расчёт средних
    days_count = (datetime.now().date() - start_date).days + 1
    avg_cal_consumed = total_cal_consumed / days_count if days_count else 0
    avg_protein = total_protein / days_count if days_count else 0
    avg_fat = total_fat / days_count if days_count else 0
    avg_carbs = total_carbs / days_count if days_count else 0
    avg_cal_burned = total_cal_burned / days_count if days_count else 0
    avg_water = total_water / days_count if days_count else 0

    # Тренды веса
    weight_trend = None
    if len(weight_entries) >= 2:
        start_weight = weight_entries[0].weight
        end_weight = weight_entries[-1].weight
        weight_trend = end_weight - start_weight

    return {
        'total_cal_consumed': total_cal_consumed,
        'total_protein': total_protein,
        'total_fat': total_fat,
        'total_carbs': total_carbs,
        'total_cal_burned': total_cal_burned,
        'total_water': total_water,
        'avg_cal_consumed': avg_cal_consumed,
        'avg_protein': avg_protein,
        'avg_fat': avg_fat,
        'avg_carbs': avg_carbs,
        'avg_cal_burned': avg_cal_burned,
        'avg_water': avg_water,
        'days_count': days_count,
        'meals_count': len(meals),
        'activities_count': len(activities),
        'weight_trend': weight_trend,
        'latest_weight': weight_entries[-1].weight if weight_entries else None
    }

async def _create_modern_progress_message(user, stats: dict, period_name: str, period: str) -> str:
    """🎨 Создание современного сообщения с прогрессом"""
    
    # 🎯 Определяем статусы и мотивацию
    calorie_status = "🎯" if stats['avg_cal_consumed'] <= user.daily_calorie_goal else "⚠️"
    water_status = "💧" if stats['avg_water'] >= user.daily_water_goal else "💦"
    
    # 📊 Прогресс-бары
    calorie_bar = ProgressBar.create_modern_bar(
        stats['avg_cal_consumed'], user.daily_calorie_goal, style="gradient"
    )
    water_bar = ProgressBar.create_modern_bar(
        stats['avg_water'], user.daily_water_goal, style="neon"
    )
    
    # 🎨 Карточки питательных веществ
    nutrition_card = NutritionCard.create_modern_macro_card(
        stats['avg_protein'], stats['avg_fat'], stats['avg_carbs']
    )
    
    # 🏆 Достижения и мотивация
    achievements = []
    if stats['meals_count'] >= stats['days_count'] * 3:  # 3+ приема в день
        achievements.append("🍽️ Регулярное питание")
    if stats['activities_count'] >= stats['days_count'] * 0.5:  # Активность половину дней
        achievements.append("🏃 Активность")
    if stats['avg_water'] >= user.daily_water_goal:
        achievements.append("💧 Гидратация")
    
    # 📈 Тренды
    trend_emoji = "📈" if stats['weight_trend'] and stats['weight_trend'] < 0 else "📊"
    weight_info = f"{trend_emoji} Тренд веса: {stats['weight_trend']:+.1f} кг" if stats['weight_trend'] else ""
    
    message = (
        f"📊 <b>Ваш прогресс {period_name}</b>\n\n"
        f"🔥 <b>Калории:</b>\n"
        f"   {calorie_status} Потреблено: {stats['total_cal_consumed']:.0f} ккал\n"
        f"   🔥 Сожжено: {stats['total_cal_burned']:.0f} ккал\n"
        f"   ⚖️ Баланс: {stats['total_cal_consumed'] - stats['total_cal_burned']:+.0f} ккал\n"
        f"   📊 Среднее: {stats['avg_cal_consumed']:.0f}/{user.daily_calorie_goal:.0f} ккал/день\n"
        f"   {calorie_bar}\n\n"
        f"💧 <b>Вода:</b>\n"
        f"   {water_status} Всего: {stats['total_water']:.0f} мл\n"
        f"   📊 Среднее: {stats['avg_water']:.0f}/{user.daily_water_goal:.0f} мл/день\n"
        f"   {water_bar}\n\n"
        f"{nutrition_card}\n\n"
    )
    
    # Добавляем достижения
    if achievements:
        message += f"🏆 <b>Ваши достижения:</b>\n"
        for achievement in achievements:
            message += f"   ✨ {achievement}\n"
        message += "\n"
    
    # Добавляем статистику
    message += (
        f"📈 <b>Статистика периода:</b>\n"
        f"   🍽️ Приемов пищи: {stats['meals_count']}\n"
        f"   🏃 Тренировок: {stats['activities_count']}\n"
        f"   📅 Дней в периоде: {stats['days_count']}\n"
    )
    
    if weight_info:
        message += f"   {weight_info}\n"
    
    # Мотивирующее завершение
    motivation = MessageTemplates.get_progress_motivation(stats, user)
    message += f"\n{motivation}"
    
    return message

async def _send_progress_charts(callback, user, session, period: str, period_name: str):
    """📊 Отправка графиков прогресса"""
    
    # 📈 График веса
    weight_plot = await generate_weight_plot(user.id, session)
    if weight_plot:
        await callback.message.answer_photo(
            BufferedInputFile(weight_plot, filename="weight.png"),
            caption="📈 Динамика веса (все записи)",
        )

    # 💧 График воды
    water_plot = await generate_water_plot(
        user.id,
        session,
        period=period,
        daily_goal=user.daily_water_goal
    )
    if water_plot:
        await callback.message.answer_photo(
            BufferedInputFile(water_plot, filename="water.png"),
            caption=f"💧 Потребление воды {period_name}",
        )

    # 🔥 График калорий
    calorie_plot = await generate_calorie_plot(
        user.id,
        session,
        period=period,
        daily_goal=user.daily_calorie_goal
    )
    if calorie_plot:
        await callback.message.answer_photo(
            BufferedInputFile(calorie_plot, filename="calories.png"),
            caption=f"🔥 Потребление калорий {period_name}",
        )

    # 🏃 График активности
    activity_plot = await generate_activity_plot(
        user.id,
        session,
        period=period,
        daily_goal=None
    )
    if activity_plot:
        await callback.message.answer_photo(
            BufferedInputFile(activity_plot, filename="activity.png"),
            caption=f"🏃 Активность {period_name}",
        )
