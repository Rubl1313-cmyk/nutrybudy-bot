"""
Генерация графиков для прогресса.
✅ Поддержка любого количества дней
✅ Красивые заголовки с эмодзи
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from database.models import WeightEntry, WaterEntry, Meal, Activity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional


async def generate_weight_plot(user_id: int, session: AsyncSession) -> Optional[bytes]:
    """График динамики веса (все записи)."""
    result = await session.execute(
        select(WeightEntry).where(WeightEntry.user_id == user_id).order_by(WeightEntry.datetime)
    )
    entries = result.scalars().all()
    if len(entries) < 2:
        return None

    dates = [e.datetime for e in entries]
    weights = [e.weight for e in entries]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, weights, marker='o', linestyle='-', color='blue', linewidth=2, markersize=6)
    plt.title('📈 Динамика веса', fontsize=14, fontweight='bold')
    plt.xlabel('Дата')
    plt.ylabel('Вес (кг)')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf.read()


async def generate_water_plot(user_id: int, session: AsyncSession, days: int = 7) -> Optional[bytes]:
    """График потребления воды за последние N дней."""
    start_date = datetime.now() - timedelta(days=days)
    result = await session.execute(
        select(WaterEntry).where(
            WaterEntry.user_id == user_id,
            WaterEntry.datetime >= start_date
        ).order_by(WaterEntry.datetime)
    )
    entries = result.scalars().all()
    if not entries:
        return None

    # Группировка по дням
    daily = {}
    for e in entries:
        day = e.datetime.date()
        daily[day] = daily.get(day, 0) + e.amount

    dates = sorted(daily.keys())
    amounts = [daily[d] for d in dates]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(dates, amounts, color='blue', alpha=0.7)
    plt.title(f'💧 Потребление воды (последние {days} дней)', fontsize=14, fontweight='bold')
    plt.xlabel('Дата')
    plt.ylabel('Вода (мл)')
    plt.grid(True, axis='y', alpha=0.3)
    plt.xticks(rotation=45)

    # Добавляем подписи значений на столбцы
    for bar, val in zip(bars, amounts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(val)}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf.read()


async def generate_calorie_balance_plot(user_id: int, session: AsyncSession, days: int = 7) -> Optional[bytes]:
    """График баланса калорий (потребление vs сжигание) за последние N дней."""
    start_date = datetime.now() - timedelta(days=days)

    meals_result = await session.execute(
        select(Meal).where(
            Meal.user_id == user_id,
            Meal.datetime >= start_date
        )
    )
    meals = meals_result.scalars().all()

    activities_result = await session.execute(
        select(Activity).where(
            Activity.user_id == user_id,
            Activity.datetime >= start_date
        )
    )
    activities = activities_result.scalars().all()

    if not meals and not activities:
        return None

    daily_consumed = {}
    daily_burned = {}

    for m in meals:
        day = m.datetime.date()
        daily_consumed[day] = daily_consumed.get(day, 0) + (m.total_calories or 0)

    for a in activities:
        day = a.datetime.date()
        daily_burned[day] = daily_burned.get(day, 0) + (a.calories_burned or 0)

    all_days = sorted(set(daily_consumed.keys()) | set(daily_burned.keys()))
    consumed = [daily_consumed.get(d, 0) for d in all_days]
    burned = [daily_burned.get(d, 0) for d in all_days]

    plt.figure(figsize=(10, 5))
    x = range(len(all_days))
    bar_width = 0.35
    plt.bar([i - bar_width/2 for i in x], consumed, bar_width, label='Потреблено', color='orange', alpha=0.7)
    plt.bar([i + bar_width/2 for i in x], burned, bar_width, label='Сожжено', color='green', alpha=0.7)

    plt.title(f'🔥 Баланс калорий (последние {days} дней)', fontsize=14, fontweight='bold')
    plt.xlabel('Дата')
    plt.ylabel('Калории')
    plt.xticks(x, [d.strftime('%d.%m') for d in all_days], rotation=45)
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)

    # Подписи значений
    for i, (c, b) in enumerate(zip(consumed, burned)):
        if c > 0:
            plt.text(i - bar_width/2, c + 5, f'{int(c)}', ha='center', va='bottom', fontsize=8)
        if b > 0:
            plt.text(i + bar_width/2, b + 5, f'{int(b)}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf.read()


async def generate_activity_plot(user_id: int, session: AsyncSession, days: int = 7) -> Optional[bytes]:
    """График активности (сожжённые калории) за последние N дней."""
    start_date = datetime.now() - timedelta(days=days)
    result = await session.execute(
        select(Activity).where(
            Activity.user_id == user_id,
            Activity.datetime >= start_date
        ).order_by(Activity.datetime)
    )
    activities = result.scalars().all()
    if not activities:
        return None

    daily = {}
    for a in activities:
        day = a.datetime.date()
        daily[day] = daily.get(day, 0) + (a.calories_burned or 0)

    dates = sorted(daily.keys())
    calories = [daily[d] for d in dates]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(dates, calories, color='green', alpha=0.7)
    plt.title(f'🏃 Активность (последние {days} дней)', fontsize=14, fontweight='bold')
    plt.xlabel('Дата')
    plt.ylabel('Сожжено калорий')
    plt.grid(True, axis='y', alpha=0.3)
    plt.xticks(rotation=45)

    for bar, val in zip(bars, calories):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(val)}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf.read()
