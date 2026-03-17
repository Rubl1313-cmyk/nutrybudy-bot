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
from database.models import User, Meal, Activity, WaterEntry, WeightEntry
from keyboards.reply_v2 import get_main_keyboard_v2
from keyboards.inline import get_progress_menu

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("progress"))
async def cmd_progress(message: Message, state: FSMContext):
    """Показать статистику прогресса"""
    await state.clear()
    
    await message.answer(
        "📊 <b>Выберите период для просмотра статистики:</b>",
        reply_markup=get_progress_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("progress_"))
async def progress_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора периода прогресса"""
    await callback.answer()
    
    period = callback.data.split("_")[1]  # day, week, month, all
    user_id = callback.from_user.id
    
    try:
        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await callback.message.answer(
                    "❌ Пользователь не найден. Сначала настройте профиль командой /set_profile",
                    reply_markup=get_main_keyboard_v2()
                )
                return
            
            # Определяем период
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            if period == "day":
                start_date = today
                period_name = "сегодня"
            elif period == "week":
                start_date = today - timedelta(days=7)
                period_name = "за неделю"
            elif period == "month":
                start_date = today - timedelta(days=30)
                period_name = "за месяц"
            else:  # all
                start_date = today - timedelta(days=365)
                period_name = "за всё время"
            
            # Получаем статистику
            stats = await get_period_stats(user.id, session, start_date)
            
            # Формируем сообщение
            message_text = await create_progress_message(user, stats, period_name)
            
            await callback.message.answer(
                message_text,
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении прогресса: {e}")
        await callback.message.answer(
            "❌ Произошла ошибка при загрузке статистики. Попробуйте еще раз.",
            reply_markup=get_main_keyboard_v2()
        )

@router.callback_query(F.data.startswith("period_"))
async def period_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка периода (для совместимости с common.py)"""
    await progress_callback(callback, state)

async def get_period_stats(user_id: int, session, start_date) -> dict:
    """Получение статистики за период - использует unified функцию из utils.daily_stats"""
    from utils.daily_stats import get_period_stats as unified_get_period_stats
    
    return await unified_get_period_stats(user_id, session, start_date)

async def create_progress_message(user, stats: dict, period_name: str) -> str:
    """Создание сообщения с прогрессом"""
    
    # Определяем статусы
    calorie_status = "🎯" if stats['avg_cal_consumed'] <= user.daily_calorie_goal else "⚠️"
    water_status = "💧" if stats['avg_water'] >= user.daily_water_goal else "💦"
    
    # Прогресс в процентах
    calorie_progress = (stats['avg_cal_consumed'] / user.daily_calorie_goal * 100) if user.daily_calorie_goal > 0 else 0
    water_progress = (stats['avg_water'] / user.daily_water_goal * 100) if user.daily_water_goal > 0 else 0
    
    # Тренд веса
    trend_emoji = "📈" if stats['weight_trend'] and stats['weight_trend'] < 0 else "📊"
    weight_info = f"{trend_emoji} Тренд веса: {stats['weight_trend']:+.1f} кг" if stats['weight_trend'] else ""
    
    message = (
        f"📊 <b>Ваш прогресс {period_name}</b>\n\n"
        f"🔥 <b>Калории:</b>\n"
        f"   {calorie_status} Потреблено: {stats['total_cal_consumed']:.0f} ккал\n"
        f"   🔥 Сожжено: {stats['total_cal_burned']:.0f} ккал\n"
        f"   ⚖️ Баланс: {stats['total_cal_consumed'] - stats['total_cal_burned']:+.0f} ккал\n"
        f"   📊 Среднее: {stats['avg_cal_consumed']:.0f}/{user.daily_calorie_goal:.0f} ккал/день\n"
        f"   📈 Прогресс: {calorie_progress:.1f}%\n\n"
        f"💧 <b>Вода:</b>\n"
        f"   {water_status} Всего: {stats['total_water']:.0f} мл\n"
        f"   📊 Среднее: {stats['avg_water']:.0f}/{user.daily_water_goal:.0f} мл/день\n"
        f"   📈 Прогресс: {water_progress:.1f}%\n\n"
        f"🥩 <b>БЖУ (среднее в день):</b>\n"
        f"   🥪 Белки: {stats['avg_protein']:.1f}/{user.daily_protein_goal:.0f} г\n"
        f"   🧈 Жиры: {stats['avg_fat']:.1f}/{user.daily_fat_goal:.0f} г\n"
        f"   🍞 Углеводы: {stats['avg_carbs']:.1f}/{user.daily_carbs_goal:.0f} г\n\n"
        f"📈 <b>Активность:</b>\n"
        f"   🍽️ Приемов пищи: {stats['meals_count']}\n"
        f"   🏃 Тренировок: {stats['activities_count']}\n"
        f"   📅 Дней в периоде: {stats['days_count']}\n"
    )
    
    if weight_info:
        message += f"\n{weight_info}"
    
    if stats['latest_weight']:
        message += f"\n⚖️ Текущий вес: {stats['latest_weight']:.1f} кг"
    
    # Мотивация
    if calorie_progress >= 90 and calorie_progress <= 110:
        message += f"\n\n🎯 Отличный результат! Вы на цели!"
    elif calorie_progress > 110:
        message += f"\n\n⚠️ Немного превышаем норму калорий"
    else:
        message += f"\n\n💪 Можно добавить немного калорий"
    
    return message

@router.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext):
    """Быстрая статистика за сегодня"""
    await state.clear()
    
    async with get_session() as session:
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль командой /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Статистика за сегодня
        today = message.date
        stats = await get_period_stats(user.id, session, today)
        
        # Прогресс
        calorie_progress = (stats['total_cal_consumed'] / user.daily_calorie_goal * 100) if user.daily_calorie_goal > 0 else 0
        water_progress = (stats['total_water'] / user.daily_water_goal * 100) if user.daily_water_goal > 0 else 0
        
        await message.answer(
            f"📊 <b>Статистика за сегодня</b>\n\n"
            f"🔥 Калории: {stats['total_cal_consumed']:.0f}/{user.daily_calorie_goal:.0f} ккал ({calorie_progress:.1f}%)\n"
            f"💧 Вода: {stats['total_water']:.0f}/{user.daily_water_goal:.0f} мл ({water_progress:.1f}%)\n"
            f"🥪 Белки: {stats['total_protein']:.1f}/{user.daily_protein_goal:.0f} г\n"
            f"🧈 Жиры: {stats['total_fat']:.1f}/{user.daily_fat_goal:.0f} г\n"
            f"🍞 Углеводы: {stats['total_carbs']:.1f}/{user.daily_carbs_goal:.0f} г\n\n"
            f"🍽️ Приемов пищи: {stats['meals_count']}\n"
            f"🏃 Активность: {stats['activities_count']} раз",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )
