"""
handlers/progress.py
Обработчики статистики и прогресса
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, FoodEntry, ActivityEntry, DrinkEntry, WeightEntry
from keyboards.reply_v2 import get_main_keyboard_v2, get_progress_keyboard, get_water_keyboard, get_activity_keyboard, get_cancel_keyboard
from utils.daily_stats import get_period_stats
from utils.timezone_utils import get_user_local_date
from utils.premium_templates import daily_summary, weekly_summary
from utils.ui_templates import ProgressBar

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("progress"))
@router.message(Command("прогресс"))
async def cmd_progress(message: Message, state: FSMContext):
    """Показать прогресс"""
    await state.clear()
    
    text = "📊 <b>Выберите период для просмотра прогресса:</b>\n\n"
    text += "📅 <b>Доступные периоды:</b>\n"
    text += "• Сегодня - статистика за текущий день\n"
    text += "• Неделя - прогресс за 7 дней\n"
    text += "• Месяц - результаты за 30 дней\n"
    text += "• Всё время - общая статистика\n\n"
    text += "📈 <b>Что включает:</b>\n"
    text += "• Питание (калории, БЖУ)\n"
    text += "• Активность (минуты, калории)\n"
    text += "• Вес (динамика изменений)\n"
    text += "• Вода (потребление)\n\n"
    text += "🚀 <b>Выберите период:</b>"
    
    await message.answer(text, reply_markup=get_progress_keyboard())

@router.message(F.text.lower().regexp(r'(📅 сегодня|сегодня|today|📅 неделя|неделя|week|📅 месяц|месяц|month|📊 всё время|всё время|все время|all time)'))
async def handle_period_selection(message: Message):
    """Обработка выбора периода"""
    text = message.text.lower()
    
    if "сегодня" in text or "today" in text:
        await show_today_progress(message)
    elif "неделя" in text or "week" in text:
        await show_week_progress(message)
    elif "месяц" in text or "month" in text:
        await show_month_progress(message)
    elif "всё время" in text or "все время" in text or "all time" in text:
        await show_all_time_progress(message)
    else:
        await message.answer("❌ Пожалуйста, выберите период из меню")

@router.message(F.text.regexp(r'(🏠 Главное меню|Главное меню|menu)'))
async def handle_main_menu_from_progress(message: Message, state: FSMContext):
    """Возврат в главное меню из прогресса"""
    from handlers.common import cmd_start
    await cmd_start(message, state)

async def show_today_progress(message: Message):
    """Показать прогресс за сегодня"""
    user_id = message.from_user.id
    
    try:
        # Получаем статистику за сегодня
        stats = await get_today_stats(user_id)
        
        if not stats:
            text = "📅 <b>Прогресс за сегодня</b>\n\n"
            text += "У вас еще нет записей на сегодня.\n\n"
            text += "🚀 <b>Начните отслеживать:</b>\n"
            text += "• /food - записать прием пищи\n"
            text += "• /water - выпить воды\n"
            text += "• /fitness - записать активность\n"
            text += "• /weight - записать вес"
            
            await message.answer(text, reply_markup=get_main_keyboard_v2())
            return
        
        # Получаем цели пользователя
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
        if not user:
            await message.answer("❌ Профиль не найден", reply_markup=get_cancel_keyboard())
            return
        
        text = "📅 <b>Прогресс за сегодня</b>\n\n"
        
        # Питание
        if stats['calories_consumed'] > 0:
            calorie_progress = min(stats['calories_consumed'] / user.daily_calorie_goal * 100, 100)
            calorie_bar = ProgressBar.create_modern_bar(calorie_progress, 100, 15, 'neon')
            
            text += f"🍽️ <b>Питание:</b>\n"
            text += f"   Калории: {stats['calories_consumed']}/{user.daily_calorie_goal} ккал\n"
            text += f"   Прогресс: {calorie_bar}\n"
            
            if stats['protein_consumed'] > 0:
                protein_progress = min(stats['protein_consumed'] / user.daily_protein_goal * 100, 100)
                protein_bar = ProgressBar.create_modern_bar(protein_progress, 100, 12, 'protein')
                text += f"   Белки: {stats['protein_consumed']:.1f}/{user.daily_protein_goal} г {protein_bar}\n"
            
            if stats['water_consumed'] > 0:
                water_progress = min(stats['water_consumed'] / user.daily_water_goal * 100, 100)
                water_bar = ProgressBar.create_modern_bar(water_progress, 100, 12, 'water')
                text += f"   Вода: {stats['water_consumed']}/{user.daily_water_goal} мл {water_bar}\n"
            
            text += "\n"
        
        # Активность
        if stats['activity_minutes'] > 0:
            activity_progress = min(stats['activity_minutes'] / 60 * 100, 100)  # Цель 60 минут
            activity_bar = ProgressBar.create_modern_bar(activity_progress, 100, 12, 'activity')
            
            text += f"🏃‍♂️ <b>Активность:</b>\n"
            text += f"   Минуты: {stats['activity_minutes']}/60 мин\n"
            text += f"   Прогресс: {activity_bar}\n"
            text += f"   Калории сожжено: {stats['calories_burned']:.0f} ккал\n\n"
        
        # Вес
        if stats.get('weight'):
            text += f"⚖️ <b>Вес:</b>\n"
            text += f"   Текущий: {stats['weight']} кг\n"
            if stats.get('weight_change'):
                change = stats['weight_change']
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                text += f"   Изменение: {emoji} {abs(change):.1f} кг\n\n"
        
        # Мотивация
        text += get_motivation_message(stats, user)
        
        await message.answer(text, reply_markup=get_main_keyboard_v2())
        
    except Exception as e:
        logger.error(f"Error in show_today_progress: {e}", exc_info=True)
        await message.answer(
            "⚠️ Временная проблема с базой данных. Попробуйте позже или обратитесь к разработчику.",
            reply_markup=get_main_keyboard_v2()
        )

async def show_week_progress(message: Message):
    """Показать прогресс за неделю"""
    user_id = message.from_user.id
    
    # Получаем статистику за неделю
    stats = await get_week_stats(user_id)
    
    if not stats or stats['total_days'] == 0:
        text = "📆 <b>Прогресс за неделю</b>\n\n"
        text += "У вас еще нет записей за эту неделю.\n\n"
        text += "🚀 <b>Начните отслеживать прогресс!</b>"
        
        await message.answer(text, reply_markup=get_main_keyboard_v2())
        return
    
    # Получаем цели пользователя
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
    
    text = "📆 <b>Прогресс за неделю</b>\n\n"
    
    # Общая статистика
    avg_calories = stats['total_calories'] / stats['total_days']
    avg_protein = stats['total_protein'] / stats['total_days']
    avg_water = stats['total_water'] / stats['total_days']
    avg_activity = stats['total_activity_minutes'] / stats['total_days']
    
    text += f"📊 <b>Средние значения в день:</b>\n"
    text += f"   Калории: {avg_calories:.0f}/{user.daily_calorie_goal} ккал\n"
    text += f"   Белки: {avg_protein:.1f}/{user.daily_protein_goal} г\n"
    text += f"   Вода: {avg_water:.0f}/{user.daily_water_goal} мл\n"
    text += f"   Активность: {avg_activity:.0f}/60 мин\n\n"
    
    # Прогресс по целям
    calorie_progress = min(avg_calories / user.daily_calorie_goal * 100, 100)
    protein_progress = min(avg_protein / user.daily_protein_goal * 100, 100)
    water_progress = min(avg_water / user.daily_water_goal * 100, 100)
    activity_progress = min(avg_activity / 60 * 100, 100)
    
    text += f"📈 <b>Выполнение целей:</b>\n"
    text += f"   Калории: {ProgressBar.create_modern_bar(calorie_progress, 100, 12, 'neon')}\n"
    text += f"   Белки: {ProgressBar.create_modern_bar(protein_progress, 100, 12, 'protein')}\n"
    text += f"   Вода: {ProgressBar.create_modern_bar(water_progress, 100, 12, 'water')}\n"
    text += f"   Активность: {ProgressBar.create_modern_bar(activity_progress, 100, 12, 'activity')}\n\n"
    
    # Вес
    if stats.get('weight_start') and stats.get('weight_end'):
        weight_change = stats['weight_end'] - stats['weight_start']
        emoji = "📈" if weight_change > 0 else "📉" if weight_change < 0 else "➡️"
        text += f"⚖️ <b>Изменение веса:</b> {emoji} {abs(weight_change):.1f} кг\n\n"
    
    # Дни с записями
    days_with_records = stats['total_days']
    text += f"📅 <b>Активность:</b> {days_with_records}/7 дней с записями\n\n"
    
    # Мотивация
    if calorie_progress >= 90 and protein_progress >= 90 and water_progress >= 90:
        text += "🎉 <b>Отличная неделя!</b> Вы придерживаетесь плана!\n"
    elif calorie_progress >= 70:
        text += "💪 <b>Хорошая неделя!</b> Продолжайте в том же духе!\n"
    else:
        text += "💡 <b>Совет:</b> Старайтесь более регулярно следовать плану\n"
    
    await message.answer(text, reply_markup=get_main_keyboard_v2())

async def show_month_progress(message: Message):
    """Показать прогресс за месяц"""
    user_id = message.from_user.id
    
    # Получаем статистику за месяц
    stats = await get_month_stats(user_id)
    
    if not stats or stats['total_days'] == 0:
        text = "🗓️ <b>Прогресс за месяц</b>\n\n"
        text += "У вас еще нет записей за этот месяц.\n\n"
        text += "🚀 <b>Начните отслеживать прогресс!</b>"
        
        await message.answer(text, reply_markup=get_main_keyboard_v2())
        return
    
    # Получаем цели пользователя
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
    
    text = "🗓️ <b>Прогресс за месяц</b>\n\n"
    
    # Общая статистика
    avg_calories = stats['total_calories'] / stats['total_days']
    avg_protein = stats['total_protein'] / stats['total_days']
    avg_water = stats['total_water'] / stats['total_days']
    avg_activity = stats['total_activity_minutes'] / stats['total_days']
    
    text += f"📊 <b>Средние значения в день:</b>\n"
    text += f"   Калории: {avg_calories:.0f}/{user.daily_calorie_goal} ккал\n"
    text += f"   Белки: {avg_protein:.1f}/{user.daily_protein_goal} г\n"
    text += f"   Вода: {avg_water:.0f}/{user.daily_water_goal} мл\n"
    text += f"   Активность: {avg_activity:.0f}/60 мин\n\n"
    
    # Прогресс по целям
    calorie_progress = min(avg_calories / user.daily_calorie_goal * 100, 100)
    protein_progress = min(avg_protein / user.daily_protein_goal * 100, 100)
    water_progress = min(avg_water / user.daily_water_goal * 100, 100)
    activity_progress = min(avg_activity / 60 * 100, 100)
    
    text += f"📈 <b>Выполнение целей:</b>\n"
    text += f"   Калории: {ProgressBar.create_modern_bar(calorie_progress, 100, 12, 'neon')}\n"
    text += f"   Белки: {ProgressBar.create_modern_bar(protein_progress, 100, 12, 'protein')}\n"
    text += f"   Вода: {ProgressBar.create_modern_bar(water_progress, 100, 12, 'water')}\n"
    text += f"   Активность: {ProgressBar.create_modern_bar(activity_progress, 100, 12, 'activity')}\n\n"
    
    # Вес
    if stats.get('weight_start') and stats.get('weight_end'):
        weight_change = stats['weight_end'] - stats['weight_start']
        emoji = "📈" if weight_change > 0 else "📉" if weight_change < 0 else "➡️"
        text += f"⚖️ <b>Изменение веса:</b> {emoji} {abs(weight_change):.1f} кг\n\n"
    
    # Дни с записями
    days_with_records = stats['total_days']
    text += f"📅 <b>Активность:</b> {days_with_records}/30 дней с записями\n\n"
    
    # Мотивация
    if calorie_progress >= 90:
        text += "🏆 <b>Превосходный месяц!</b> Вы достигли отличных результатов!\n"
    elif calorie_progress >= 70:
        text += "👍 <b>Хороший месяц!</b> У вас стабильный прогресс!\n"
    else:
        text += "📈 <b>Есть куда расти!</b> Продолжайте работать над собой!\n"
    
    await message.answer(text, reply_markup=get_main_keyboard_v2())

async def show_all_time_progress(message: Message):
    """Показать прогресс за всё время"""
    user_id = message.from_user.id
    
    # Получаем общую статистику
    stats = await get_all_time_stats(user_id)
    
    if not stats:
        text = "📊 <b>Прогресс за всё время</b>\n\n"
        text += "У вас еще нет записей.\n\n"
        text += "🚀 <b>Начните отслеживать прогресс!</b>"
        
        await message.answer(text, reply_markup=get_main_keyboard_v2())
        return
    
    text = "📊 <b>Прогресс за всё время</b>\n\n"
    
    text += f"📅 <b>Период отслеживания:</b> {stats['days_tracked']} дней\n"
    text += f"🍽️ <b>Всего приемов пищи:</b> {stats['total_meals']}\n"
    text += f"💧 <b>Всего воды выпито:</b> {stats['total_water']:.0f} л\n"
    text += f"🏃‍♂️ <b>Всего активности:</b> {stats['total_activities']} минут\n"
    text += f"⚖️ <b>Записей веса:</b> {stats['weight_entries']}\n\n"
    
    # Средние значения
    if stats['days_tracked'] > 0:
        avg_calories = stats['total_calories'] / stats['days_tracked']
        avg_protein = stats['total_protein'] / stats['days_tracked']
        avg_water = stats['total_water'] / stats['days_tracked']
        
        text += f"📈 <b>Средние значения в день:</b>\n"
        text += f"   Калории: {avg_calories:.0f} ккал\n"
        text += f"   Белки: {avg_protein:.1f} г\n"
        text += f"   Вода: {avg_water:.0f} мл\n\n"
    
    # Вес
    if stats.get('weight_start') and stats.get('weight_end'):
        weight_change = stats['weight_end'] - stats['weight_start']
        emoji = "📈" if weight_change > 0 else "📉" if weight_change < 0 else "➡️"
        text += f"⚖️ <b>Общее изменение веса:</b> {emoji} {abs(weight_change):.1f} кг\n\n"
    
    text += "🎯 <b>Продолжайте работать над собой!</b>\n"
    text += "Каждая запись приближает вас к цели!"
    
    await message.answer(text, reply_markup=get_main_keyboard_v2())

def get_motivation_message(stats: dict, user: User) -> str:
    """Получить мотивационное сообщение"""
    if not stats:
        return "🌱 <b>Начните свой путь!</b> Первая запись - это уже победа!"
    
    calorie_progress = min(stats['calories_consumed'] / user.daily_calorie_goal * 100, 100) if user.daily_calorie_goal else 0
    
    if calorie_progress >= 100:
        return "🎉 <b>Отлично!</b> Вы выполнили дневную норму калорий!"
    elif calorie_progress >= 80:
        return "💪 <b>Хорошо!</b> Почти достигли цели!"
    elif calorie_progress >= 50:
        return "👍 <b>Неплохо!</b> Вы на полпути к цели!"
    else:
        return "💡 <b>Продолжайте!</b> Каждый шаг важен для достижения цели!"

# Функции для получения статистики
async def get_today_stats(user_id: int) -> dict:
    """Получить статистику за сегодня"""
    
    async for session in get_session():
        result = await session.execute(
            select(User.timezone).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        user_timezone = user.timezone if user else 'UTC'
        
        today = get_user_local_date(user_timezone)
        
        # Питание
        food_result = await session.execute(
            select(
                func.sum(FoodEntry.calories),
                func.sum(FoodEntry.protein),
                func.sum(FoodEntry.fat),
                func.sum(FoodEntry.carbs)
            ).where(
                FoodEntry.user_id == user_id,
                func.date(FoodEntry.created_at) == today
            )
        )
        food_stats = food_result.first()
        
        # Вода
        water_result = await session.execute(
            select(func.sum(DrinkEntry.amount)).where(
                DrinkEntry.user_id == user_id,
                DrinkEntry.created_at >= today
            )
        )
        water_stats = water_result.scalar() or 0
        
        # Активность
        activity_result = await session.execute(
            select(
                func.sum(ActivityEntry.duration),
                func.sum(ActivityEntry.calories_burned)
            ).where(
                ActivityEntry.user_id == user_id,
                ActivityEntry.created_at >= today
            )
        )
        activity_stats = activity_result.first()
        
        # Вес
        weight_result = await session.execute(
            select(WeightEntry.weight).where(
                WeightEntry.user_id == user_id,
                WeightEntry.created_at >= today
            ).order_by(WeightEntry.created_at.desc())
        )
        weight_stats = weight_result.scalar()
        
        return {
            'calories_consumed': food_stats[0] or 0,
            'protein_consumed': food_stats[1] or 0,
            'meals_count': food_stats[2] or 0,
            'water_consumed': water_stats,
            'activity_minutes': activity_stats[0] or 0,
            'calories_burned': activity_stats[1] or 0,
            'weight': weight_stats
        }

async def get_week_stats(user_id: int) -> dict:
    """Получить статистику за неделю"""
    from datetime import datetime, timezone, timedelta
    
    async for session in get_session():
        week_start = datetime.now(timezone.utc).date() - timedelta(days=datetime.now(timezone.utc).weekday())
        week_end = week_start + timedelta(days=7)
        
        # Получаем статистику питания за неделю
        result = await session.execute(
            select(Meal).where(
                Meal.user_id == user_id,
                Meal.date >= week_start,
                Meal.date < week_end
            )
        )
        meals = result.scalars().all()
        
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_fat = sum(meal.fat for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        
        # Получаем статистику активности за неделю
        result = await session.execute(
            select(Activity).where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date < week_end
            )
        )
        activities = result.scalars().all()
        
        total_activity_minutes = sum(activity.duration_minutes for activity in activities)
        total_activity_calories = sum(activity.calories_burned for activity in activities)
        
        # Получаем статистику веса за неделю
        result = await session.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user_id,
                WeightEntry.created_at >= datetime.combine(week_start, datetime.min.time()),
                WeightEntry.created_at < datetime.combine(week_end, datetime.min.time())
            ).order_by(WeightEntry.created_at)
        )
        weight_entries = result.scalars().all()
        
        weight_start = weight_entries[0].weight if weight_entries else None
        weight_end = weight_entries[-1].weight if weight_entries else None
        
        # Получаем статистику воды за неделю
        result = await session.execute(
            select(WaterEntry).where(
                WaterEntry.user_id == user_id,
                WaterEntry.created_at >= datetime.combine(week_start, datetime.min.time()),
                WaterEntry.created_at < datetime.combine(week_end, datetime.min.time())
            )
        )
        water_entries = result.scalars().all()
        total_water = sum(water.amount for water in water_entries)
        
        # Подсчет дней с записями
        days_with_entries = len(set(meal.date for meal in meals))
        
        return {
            'total_days': days_with_entries,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_fat': total_fat,
            'total_carbs': total_carbs,
            'total_activity_minutes': total_activity_minutes,
            'total_activity_calories': total_activity_calories,
            'total_water': total_water,
            'weight_start': weight_start,
            'weight_end': weight_end
        }

async def get_month_stats(user_id: int) -> dict:
    """Получить статистику за месяц"""
    from datetime import datetime, timezone, timedelta
    
    async for session in get_session():
        month_start = datetime.now(timezone.utc).date().replace(day=1)
        month_end = month_start + timedelta(days=31)
        
        # Получаем статистику питания за месяц
        result = await session.execute(
            select(Meal).where(
                Meal.user_id == user_id,
                Meal.date >= month_start,
                Meal.date < month_end
            )
        )
        meals = result.scalars().all()
        
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_fat = sum(meal.fat for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        
        # Получаем статистику активности за месяц
        result = await session.execute(
            select(Activity).where(
                Activity.user_id == user_id,
                Activity.date >= month_start,
                Activity.date < month_end
            )
        )
        activities = result.scalars().all()
        
        total_activity_minutes = sum(activity.duration_minutes for activity in activities)
        total_activity_calories = sum(activity.calories_burned for activity in activities)
        
        # Получаем статистику веса за месяц
        result = await session.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user_id,
                WeightEntry.created_at >= datetime.combine(month_start, datetime.min.time()),
                WeightEntry.created_at < datetime.combine(month_end, datetime.min.time())
            ).order_by(WeightEntry.created_at)
        )
        weight_entries = result.scalars().all()
        
        weight_start = weight_entries[0].weight if weight_entries else None
        weight_end = weight_entries[-1].weight if weight_entries else None
        
        # Получаем статистику воды за месяц
        result = await session.execute(
            select(WaterEntry).where(
                WaterEntry.user_id == user_id,
                WaterEntry.created_at >= datetime.combine(month_start, datetime.min.time()),
                WaterEntry.created_at < datetime.combine(month_end, datetime.min.time())
            )
        )
        water_entries = result.scalars().all()
        total_water = sum(water.amount for water in water_entries)
        
        # Подсчет дней с записями
        days_with_entries = len(set(meal.date for meal in meals))
        
        return {
            'total_days': days_with_entries,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_fat': total_fat,
            'total_carbs': total_carbs,
            'total_activity_minutes': total_activity_minutes,
            'total_activity_calories': total_activity_calories,
            'total_water': total_water,
            'weight_start': weight_start,
            'weight_end': weight_end
        }

async def get_all_time_stats(user_id: int) -> dict:
    """Получить статистику за всё время"""
    from datetime import datetime, timezone
    
    async for session in get_session():
        # Получаем всю статистику питания
        result = await session.execute(
            select(Meal).where(Meal.user_id == user_id)
        )
        meals = result.scalars().all()
        
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_fat = sum(meal.fat for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        
        # Получаем всю статистику активности
        result = await session.execute(
            select(Activity).where(Activity.user_id == user_id)
        )
        activities = result.scalars().all()
        
        total_activity_minutes = sum(activity.duration_minutes for activity in activities)
        total_activity_calories = sum(activity.calories_burned for activity in activities)
        
        # Получаем всю статистику веса
        result = await session.execute(
            select(WeightEntry).where(WeightEntry.user_id == user_id).order_by(WeightEntry.created_at)
        )
        weight_entries = result.scalars().all()
        
        weight_start = weight_entries[0].weight if weight_entries else None
        weight_end = weight_entries[-1].weight if weight_entries else None
        
        # Получаем всю статистику воды
        result = await session.execute(
            select(WaterEntry).where(WaterEntry.user_id == user_id)
        )
        water_entries = result.scalars().all()
        total_water = sum(water.amount for water in water_entries)
        
        # Подсчет дней с записями
        days_with_entries = len(set(meal.date for meal in meals))
        
        return {
            'total_days': days_with_entries,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_fat': total_fat,
            'total_carbs': total_carbs,
            'total_activity_minutes': total_activity_minutes,
            'total_activity_calories': total_activity_calories,
            'total_water': total_water,
            'weight_start': weight_start,
            'weight_end': weight_end
        }
