"""
🎨 Современный обработчик прогресса и статистики NutriBuddy Bot
✨ Визуально привлекательный интерфейс с мотивацией и достижениями
📊 Умная аналитика и тренды
"""
import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.db import get_session
from database.models import User
from services.plots import (
    generate_weight_plot,
    generate_water_plot,
    generate_calorie_plot,
    generate_activity_plot,
)
from services.ai_progress_analyzer import ai_analyzer
from services.climate_manager_enhanced import enhanced_climate_manager as ai_climate_manager
from keyboards.reply import get_main_keyboard
from utils.ui_templates import (
    ProgressBar, NutritionCard, WaterTracker, 
    ActivityCard, StreakCard, StatisticsCard
)
from utils.message_templates import MessageTemplates
from utils.animations import AnimationEngine
from keyboards.improved_keyboards import get_time_period_keyboard
from utils.statistics import get_period_stats

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "📊 Прогресс и статистика")
async def cmd_progress(message: Message, state: FSMContext):
    """🎨 Современное меню прогресса с анимацией"""
    await state.clear()
    
    # Персонализированное приветствие
    user_name = message.from_user.first_name or "Пользователь"
    welcome_text = MessageTemplates.get_progress_welcome(user_name)
    
    # 🎨 Современная клавиатура выбора периода
    keyboard = get_time_period_keyboard()
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

async def show_enhanced_progress(callback: CallbackQuery, period: str):
    """🎨 Показать улучшенный прогресс с AI-анализом"""
    user_id = callback.from_user.id
    
    # Определяем период
    now = datetime.utcnow()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_name = "сегодня"
    elif period == "week":
        start_date = now - timedelta(days=7)
        period_name = "за неделю"
    elif period == "month":
        start_date = now - timedelta(days=30)
        period_name = "за месяц"
    else:  # all
        start_date = now - timedelta(days=365)
        period_name = "за всё время"
    
    await callback.answer("📊 Загружаю статистику...")
    
    async with get_session() as session:
        # Получаем статистику через универсальную функцию
        stats = await get_period_stats(user_id, session, start_date)
        
        if not stats:
            await callback.message.answer("📊 Нет данных за выбранный период")
            return
        
        # Получаем пользователя для целей
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            await callback.message.answer("❌ Пользователь не найден")
            return
        
        # 🎨 Создаем современное сообщение с прогрессом
        progress_message = await _create_modern_progress_message(
            user, stats, period_name, period
        )
        
        await callback.message.answer(progress_message, parse_mode="HTML")
        
        # 📊 Отправляем графики
        await _send_progress_charts(callback, user_id, start_date, period_name)

async def _create_modern_progress_message(user, stats: dict, period_name: str, period: str) -> str:
    """🎨 Создание современного сообщения с прогрессом"""
    
    # 🎯 Определяем статусы и мотивацию
    calorie_status = "🎯" if stats['avg_calories'] <= user.daily_calorie_goal else "⚠️"
    water_status = "💧" if stats['avg_water'] >= user.daily_water_goal else "💦"
    
    # 🎨 Создаем прогресс-бары
    calorie_bar = ProgressBar.create_modern_bar(
        stats['avg_calories'], user.daily_calorie_goal, style="gradient"
    )
    water_bar = ProgressBar.create_modern_bar(
        stats['avg_water'], user.daily_water_goal, style="neon"
    )
    
    # 🌟 Получаем мотивацию
    motivation = MessageTemplates.get_progress_motivation(stats, user)
    
    # 🎨 Собираем сообщение
    message = f"""
📊 Ваш прогресс {period_name}
═══════════════════════════════════

🔥 Калории:
   🎯 Потреблено: {stats['total_calories']:.0f} ккал
   📊 Среднее: {stats['avg_calories']:.0f}/{user.daily_calorie_goal} ккал/день
   {calorie_bar}

💧 Вода:
   💧 Всего: {stats['total_water']:.0f} мл
   📊 Среднее: {stats['avg_water']:.0f}/{user.daily_water_goal} мл/день
   {water_bar}

🍽️ Питательные вещества:
   🥩 Белки: {stats['avg_protein']:.1f}г ({'🟢' if stats['avg_protein'] >= user.daily_protein_goal else '🟡'})
   🥑 Жиры: {stats['avg_fat']:.1f}г ({'🟢' if stats['avg_fat'] >= user.daily_fat_goal else '🟡'})
   🍚 Углеводы: {stats['avg_carbs']:.1f}г ({'🟢' if stats['avg_carbs'] >= user.daily_carbs_goal else '🟡'})

🏆 Достижения:
   ✨ Приемов пищи: {stats['meals_count']}
   ✨ Активность: {stats['activities_count']} раз
   ✨ Шаги: {stats['total_steps']:,}

{motivation}
"""
    
    return message

async def _send_progress_charts(callback: CallbackQuery, user_id: int, start_date: datetime, period_name: str):
    """📊 Отправка графиков прогресса"""
    try:
        from database.db import get_session
        from database.models import User
        from sqlalchemy import select
        
        async with get_session() as session:
            # Получаем внутренний ID пользователя
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not user:
                await callback.message.answer("❌ Пользователь не найден")
                return
            
            internal_id = user.id
            
            # Генерируем графики с внутренним ID
            weight_plot = await generate_weight_plot(internal_id, session)
            water_plot = await generate_water_plot(internal_id, session)
            calorie_plot = await generate_calorie_plot(internal_id, session)
            activity_plot = await generate_activity_plot(internal_id, session)
            
            # Отправляем графики
            if weight_plot:
                await callback.message.answer_photo(
                    weight_plot,
                    caption=f"⚖️ Вес {period_name}"
                )
            
            if water_plot:
                await callback.message.answer_photo(
                    water_plot,
                    caption=f"💧 Водный баланс {period_name}"
                )
            
            if calorie_plot:
                await callback.message.answer_photo(
                    calorie_plot,
                    caption=f"🔥 Калории {period_name}"
                )
            
            if activity_plot:
                await callback.message.answer_photo(
                    activity_plot,
                    caption=f"🏃 Активность {period_name}"
                )
            
    except Exception as e:
        logger.error(f"Ошибка при отправке графиков: {e}")
        await callback.message.answer("📊 Не удалось загрузить графики")
