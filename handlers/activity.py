"""
handlers/activity.py
Обработчики учета активности
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from sqlalchemy import select

from database.db import get_session
from database.models import User, ActivityEntry
from keyboards.reply import get_main_keyboard
from utils.premium_templates import activity_card
from utils.ui_templates import ProgressBar
from utils.activity_calculator import calculate_calories_burned

logger = logging.getLogger(__name__)
router = Router()

class ActivityStates(StatesGroup):
    """Состояния для записи активности"""
    waiting_for_activity_type = State()
    waiting_for_duration = State()
    waiting_for_calories = State()

@router.message(Command("fitness"))
@router.message(Command("активность"))
async def cmd_fitness(message: Message, state: FSMContext):
    """Запись фитнес активности"""
    await state.clear()
    
    from keyboards.reply_v2 import get_activity_keyboard
    
    text = "🏃‍♂️ <b>Записать активность</b>\n\n"
    text += "Выберите тип активности:"
    
    await message.answer(text, reply_markup=get_activity_keyboard())
    await state.set_state(ActivityStates.waiting_for_activity_type)

@router.message(ActivityStates.waiting_for_activity_type)
async def process_activity_type(message: Message, state: FSMContext):
    """Обработка типа активности"""
    activity_type = message.text.lower()
    
    # Маппинг типов активности
    activity_mapping = {
        "🏃 бег": "running",
        "🚴 велосипед": "cycling", 
        "🏋️ тренировка": "gym",
        "🧘 йога": "yoga",
        "🚶 ходьба": "walking",
        "🏊 плавание": "swimming",
        "🤸 другое": "other"
    }
    
    mapped_type = activity_mapping.get(activity_type, "other")
    
    # Сохраняем тип активности
    await state.update_data(activity_type=mapped_type, activity_name=activity_type)
    
    # Запрашиваем длительность
    text = f"⏱️ <b>Длительность активности</b>\n\n"
    text += f"Выбрана активность: {activity_type}\n"
    text += "Введите длительность в минутах (например: 30):"
    
    await message.answer(text)
    await state.set_state(ActivityStates.waiting_for_duration)

@router.message(ActivityStates.waiting_for_duration)
async def process_duration(message: Message, state: FSMContext):
    """Обработка длительности активности"""
    try:
        duration = int(message.text)
        
        if duration <= 0:
            await message.answer("❌ Длительность должна быть положительным числом. Попробуйте еще раз:")
            return
        
        if duration > 480:  # 8 часов максимум
            await message.answer("❌ Слишком большая длительность. Максимум 480 минут. Попробуйте еще раз:")
            return
        
        # Сохраняем длительность
        await state.update_data(duration=duration)
        
        # Получаем данные о пользователе для расчета калорий
        data = await state.get_data()
        activity_type = data['activity_type']
        
        # Запрашиваем вес для расчета калорий
        text = f"⚖️ <b>Расчет калорий</b>\n\n"
        text += f"Активность: {data['activity_name']}\n"
        text += f"Длительность: {duration} минут\n\n"
        text += "Введите ваш вес в кг для расчета сожженных калорий (например: 70):"
        
        await message.answer(text)
        await state.set_state(ActivityStates.waiting_for_calories)
        
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число (например: 30):")

@router.message(ActivityStates.waiting_for_calories)
async def process_calories(message: Message, state: FSMContext):
    """Обработка калорий и сохранение активности"""
    try:
        weight = float(message.text)
        
        if weight <= 0:
            await message.answer("❌ Вес должен быть положительным числом. Попробуйте еще раз:")
            return
        
        if weight > 300:
            await message.answer("❌ Слишком большой вес. Попробуйте еще раз:")
            return
        
        # Получаем сохраненные данные
        data = await state.get_data()
        activity_type = data['activity_type']
        activity_name = data['activity_name']
        duration = data['duration']
        
        # Рассчитываем сожженные калории
        calories_burned = calculate_calories_burned(activity_type, duration, weight)
        
        # Сохраняем в базу данных
        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await message.answer(
                    "❌ Сначала настройте профиль с помощью /set_profile",
                    reply_markup=get_main_keyboard()
                )
                await state.clear()
                return
            
            # Создаем запись об активности
            activity_entry = ActivityEntry(
                user_id=user.telegram_id,
                activity_type=activity_type,
                duration=duration,
                calories_burned=calories_burned,
                intensity='moderate'  # По умолчанию средняя интенсивность
            )
            
            session.add(activity_entry)
            await session.commit()
        
        # Получаем статистику за день
        daily_stats = await get_daily_activity_stats(user.telegram_id)
        
        # Создаем красивую карточку активности
        card = activity_card(activity_name, duration, calories_burned, daily_stats)
        
        await message.answer(card, reply_markup=get_main_keyboard())
        
        # Проверяем достижения
        from handlers.achievements import check_achievements
        await check_achievements(user.telegram_id, 'activity', duration)
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число (например: 70.5):")

async def get_daily_activity_stats(user_id: int) -> dict:
    """Получить статистику активности за день"""
    from datetime import datetime, timezone
    
    async with get_session() as session:
        # Получаем записи активности за сегодня
        today = datetime.now(timezone.utc).date()
        
        result = await session.execute(
            select(ActivityEntry).where(
                ActivityEntry.user_id == user_id,
                ActivityEntry.created_at >= today
            )
        )
        activities = result.scalars().all()
        
        # Считаем статистику
        total_duration = sum(a.duration for a in activities)
        total_calories = sum(a.calories_burned for a in activities)
        
        return {
            'activity_minutes': total_duration,
            'calories_burned': total_calories,
            'activities_count': len(activities)
        }

@router.message(Command("activity_stats"))
@router.message(Command("статистика_активности"))
async def cmd_activity_stats(message: Message):
    """Показать статистику активности"""
    user_id = message.from_user.id
    
    # Получаем статистику за разные периоды
    stats = await get_activity_stats_by_periods(user_id)
    
    text = "📊 <b>Статистика активности</b>\n\n"
    
    # Сегодня
    today_progress = min(stats['today']['minutes'] / 60 * 100, 100)  # Цель 60 минут
    today_bar = ProgressBar.create_modern_bar(today_progress, 100, 15, 'activity')
    
    text += f"📅 <b>Сегодня:</b>\n"
    text += f"   Время: {stats['today']['minutes']} мин\n"
    text += f"   Калории: {stats['today']['calories']} ккал\n"
    text += f"   Прогресс: {today_bar}\n\n"
    
    # За неделю
    week_progress = min(stats['week']['minutes'] / 300 * 100, 100)  # Цель 300 минут в неделю
    week_bar = ProgressBar.create_modern_bar(week_progress, 100, 15, 'activity')
    
    text += f"📆 <b>За неделю:</b>\n"
    text += f"   Время: {stats['week']['minutes']} мин\n"
    text += f"   Калории: {stats['week']['calories']} ккал\n"
    text += f"   Прогресс: {week_bar}\n\n"
    
    # За месяц
    month_progress = min(stats['month']['minutes'] / 1200 * 100, 100)  # Цель 1200 минут в месяц
    month_bar = ProgressBar.create_modern_bar(month_progress, 100, 15, 'activity')
    
    text += f"🗓️ <b>За месяц:</b>\n"
    text += f"   Время: {stats['month']['minutes']} мин\n"
    text += f"   Калории: {stats['month']['calories']} ккал\n"
    text += f"   Прогресс: {month_bar}\n\n"
    
    # Мотивация
    if stats['today']['minutes'] >= 60:
        text += "🔥 <b>Отличный результат!</b> Вы выполнили дневную норму активности!\n"
    elif stats['today']['minutes'] >= 30:
        text += "💪 <b>Хорошая работа!</b> Вы на полпути к дневной цели!\n"
    else:
        text += "🌱 <b>Продолжайте!</b> Даже небольшая активность важна!\n"
    
    await message.answer(text)

async def get_activity_stats_by_periods(user_id: int) -> dict:
    """Получить статистику активности по периодам"""
    from datetime import datetime, timezone, timedelta
    
    async with get_session() as session:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        
        # Функция для получения статистики за период
        def get_period_stats(start_date):
            result = session.execute(
                select(ActivityEntry).where(
                    ActivityEntry.user_id == user_id,
                    ActivityEntry.created_at >= start_date
                )
            )
            activities = result.scalars().all()
            
            return {
                'minutes': sum(a.duration for a in activities),
                'calories': sum(a.calories_burned for a in activities),
                'count': len(activities)
            }
        
        return {
            'today': get_period_stats(today_start),
            'week': get_period_stats(week_start),
            'month': get_period_stats(month_start)
        }
