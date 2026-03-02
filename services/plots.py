"""
Генерация графиков для прогресса.
✅ Поддержка периода: день (почасово + итоги), неделя/месяц (подневно)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from database.models import WeightEntry, WaterEntry, Meal, Activity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)


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


async def generate_water_plot(
    user_id: int,
    session: AsyncSession,
    period: Literal['day', 'week', 'month'] = 'week',
    daily_goal: float = 2000
) -> Optional[bytes]:
    """
    График потребления воды.
    - day: почасовой (24 часа) + столбцы "Всего" и "Норма"
    - week / month: подневной
    """
    return await _generate_consumption_plot(
        user_id=user_id,
        session=session,
        model=WaterEntry,
        amount_field='amount',
        ylabel='Вода (мл)',
        title_prefix='💧 Потребление воды',
        period=period,
        daily_goal=daily_goal
    )


async def generate_calorie_plot(
    user_id: int,
    session: AsyncSession,
    period: Literal['day', 'week', 'month'] = 'week',
    daily_goal: float = 2000
) -> Optional[bytes]:
    """
    График потребления калорий.
    - day: почасовой + итоги
    - week/month: подневной
    """
    return await _generate_consumption_plot(
        user_id=user_id,
        session=session,
        model=Meal,
        amount_field='total_calories',
        ylabel='Калории (ккал)',
        title_prefix='🔥 Потребление калорий',
        period=period,
        daily_goal=daily_goal
    )


async def generate_activity_plot(
    user_id: int,
    session: AsyncSession,
    period: Literal['day', 'week', 'month'] = 'week',
    daily_goal: Optional[float] = None
) -> Optional[bytes]:
    """
    График сожжённых калорий.
    - day: почасовой + итоги
    - week/month: подневной
    """
    return await _generate_consumption_plot(
        user_id=user_id,
        session=session,
        model=Activity,
        amount_field='calories_burned',
        ylabel='Сожжено (ккал)',
        title_prefix='🏃 Активность',
        period=period,
        daily_goal=daily_goal
    )


async def _generate_consumption_plot(
    user_id: int,
    session: AsyncSession,
    model,
    amount_field: str,
    ylabel: str,
    title_prefix: str,
    period: Literal['day', 'week', 'month'] = 'week',
    daily_goal: Optional[float] = None
) -> Optional[bytes]:
    """Общая функция для построения графиков потребления/активности."""
    now = datetime.now()

    if period == 'day':
        start_date = now - timedelta(hours=24)
        # Получаем записи за последние 24 часа
        result = await session.execute(
            select(model).where(
                model.user_id == user_id,
                model.datetime >= start_date
            ).order_by(model.datetime)
        )
        entries = result.scalars().all()
        if not entries:
            return None

        # Группировка по часам
        hourly = {}
        for e in entries:
            hour_key = e.datetime.replace(minute=0, second=0, microsecond=0)
            amount = getattr(e, amount_field) or 0
            hourly[hour_key] = hourly.get(hour_key, 0) + amount

        # Сортируем часы
        hours = sorted(hourly.keys())
        values = [hourly[h] for h in hours]

        # Подготавливаем метки для оси X (часы)
        labels = [h.strftime('%H:%M') for h in hours]

        # Добавляем итоговые столбцы: "Всего" и "Норма"
        total_value = sum(values)
        labels.append('Всего')
        values.append(total_value)
        if daily_goal is not None:
            labels.append('Норма')
            values.append(daily_goal)

        # Строим график
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(labels)), values, color=['#1f77b4']*len(hours) + ['#ff7f0e', '#2ca02c'])
        # Окрашиваем последние два столбца в разные цвета
        if daily_goal is not None:
            bars[-2].set_color('#ff7f0e')  # всего
            bars[-1].set_color('#2ca02c')  # норма
        else:
            bars[-1].set_color('#ff7f0e')  # всего

        plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
        plt.title(f'{title_prefix} (последние 24 часа)', fontsize=14, fontweight='bold')
        plt.xlabel('Время')
        plt.ylabel(ylabel)
        plt.grid(True, axis='y', alpha=0.3)

        # Подписи значений на столбцах
        for bar, val in zip(bars, values):
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width()/2., height,
                         f'{int(val)}', ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        return buf.read()

    elif period == 'week':
        start_date = now - timedelta(days=7)
        date_format = '%d.%m'
        xlabel = 'День'
        title = f'{title_prefix} (последние 7 дней)'
        group_by = 'day'
    else:  # month
        start_date = now - timedelta(days=30)
        date_format = '%d.%m'
        xlabel = 'День'
        title = f'{title_prefix} (последние 30 дней)'
        group_by = 'day'

    # Для недели и месяца
    result = await session.execute(
        select(model).where(
            model.user_id == user_id,
            model.datetime >= start_date
        ).order_by(model.datetime)
    )
    entries = result.scalars().all()
    if not entries:
        return None

    # Группировка по дням
    daily = {}
    for e in entries:
        day_key = e.datetime.date()
        amount = getattr(e, amount_field) or 0
        daily[day_key] = daily.get(day_key, 0) + amount

    # Сортируем дни
    days = sorted(daily.keys())
    values = [daily[d] for d in days]
    labels = [d.strftime(date_format) for d in days]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(range(len(labels)), values, color='blue', alpha=0.7)
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, axis='y', alpha=0.3)

    for bar, val in zip(bars, values):
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{int(val)}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf.read()
