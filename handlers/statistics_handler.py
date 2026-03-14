"""
Обработчик для красивой статистики
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.ui_templates import StatisticsCard, StreakCard
from utils.message_templates import MessageTemplates

router = Router()

@router.message(Command("stats"))
async def cmd_statistics(message: Message, state: FSMContext):
    """Показывает красивую статистику"""
    
    # Получаем данные пользователя
    # ... код для получения данных из БД ...
    
    keyboard = get_time_period_keyboard()
    
    await message.answer(
        "📊 <b>Выберите период</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "stats_week")
async def stats_week_callback(callback: CallbackQuery, state: FSMContext):
    """Еженедельная статистика"""
    
    # Получаем данные за неделю
    week_data = [
        {'day': 'Пн', 'cal': 1850, 'achieved': True},
        {'day': 'Вт', 'cal': 2100, 'achieved': True},
        {'day': 'Ср', 'cal': 1650, 'achieved': False},
        {'day': 'Чт', 'cal': 2200, 'achieved': True},
        {'day': 'Пт', 'cal': 1900, 'achieved': True},
        {'day': 'Сб', 'cal': 2300, 'achieved': True},
        {'day': 'Вс', 'cal': 1750, 'achieved': False},
    ]
    
    avg_cal = sum(d['cal'] for d in week_data) / len(week_data)
    
    stats_text = StatisticsCard.create_weekly_stats(week_data)
    
    report = MessageTemplates.progress_report_weekly(
        week_data, avg_cal, 2000,
        ["3 дня подряд с целью", "Неделя активности"]
    )
    
    await callback.message.edit_text(report, parse_mode="HTML")

@router.callback_query(F.data == "stats_month")
async def stats_month_callback(callback: CallbackQuery, state: FSMContext):
    """Ежемесячная статистика"""
    
    month_data = {
        i: {'cal': 1800 + (i * 50) % 400, 'water': 2000 - (i * 30) % 500}
        for i in range(1, 31)
    }
    
    heatmap = StatisticsCard.create_monthly_heatmap(month_data)
    
    text = (
        "🔥 <b>Активность месяца</b>\n"
        f"{heatmap}\n"
        "🟠 Активен | 🟡 Норм | 🟢 Мало | ⬜ Нет данных"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")
