"""
Генерация современных и понятных графиков для прогресса.
✅ Линейные графики с заливкой области
✅ Горизонтальная линия нормы (где применимо)
✅ Поддержка периода: день (почасово + итоги), неделя/месяц (подневно)
✅ Корректное форматирование оси X (даты)
✅ Без эмодзи (для стабильности)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
from datetime import datetime, timedelta
from database.models import WeightEntry, DrinkEntry, Meal, Activity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Literal
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Современная цветовая палитра
COLORS = {
    'weight': '#2E86AB',      # синий
    'water': '#56A3A6',       # бирюзовый
    'calories': '#F18F01',     # оранжевый
    'activity': '#C73E1D',     # красный
    'trend': '#A23B72',        # фиолетовый для тренда
    'goal': '#E15554'          # красный для линии нормы
}

def clean_title(text: str) -> str:
    """Удаляет эмодзи из заголовка (первые символы, если это эмодзи)."""
    if text and len(text) > 2 and (text[0] not in 'abcdefghijklmnopqrstuvwxyzАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'):
        # Предполагаем, что первые два символа — эмодзи и пробел
        return text[2:].strip()
    return text

# ========== ОСНОВНЫЕ ФУНКЦИИ ГРАФИКОВ ==========

async def generate_weight_plot(user_id: int, session: AsyncSession) -> Optional[bytes]:
    """
    График динамики веса (все записи).
    Линейный график + линия тренда.
    """
    try:
        result = await session.execute(
            select(WeightEntry).where(WeightEntry.user_id == user_id).order_by(WeightEntry.datetime)
        )
        entries = result.scalars().all()
        logger.info(f"📊 generate_weight_plot: получено {len(entries)} записей для user_id={user_id}")

        if len(entries) < 2:
            logger.warning(f"⚠️ Недостаточно записей веса для графика: {len(entries)}")
            return None

        dates = [e.datetime for e in entries]
        weights = [e.weight for e in entries]

        plt.figure(figsize=(12, 6))
        ax = plt.gca()

        # Основная линия
        ax.plot(dates, weights, marker='o', linestyle='-', linewidth=2.5,
                color=COLORS['weight'], markersize=6, label='Вес')
        ax.fill_between(dates, min(weights)-1, weights, alpha=0.15, color=COLORS['weight'])

        # Линия тренда (полиномиальная регрессия 1-й степени)
        if len(weights) > 3:
            z = np.polyfit(range(len(weights)), weights, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(range(len(weights))), '--', linewidth=2,
                    color=COLORS['trend'], label='Тренд')

        # Настройка оси X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        # Устанавливаем локатор на каждый день, где есть данные
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45, ha='right')

        # Заголовок (без эмодзи)
        ax.set_title(clean_title('📈 Динамика веса'), fontsize=16, fontweight='bold', pad=20)

        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Вес (кг)', fontsize=12)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        plt.close()
        buf.seek(0)
        logger.info(f"✅ График веса успешно сгенерирован, размер {len(buf.getvalue())} байт")
        return buf.read()

    except Exception as e:
        logger.error(f"❌ Ошибка при генерации графика веса: {e}", exc_info=True)
        return None

async def generate_water_plot(
    user_id: int,
    session: AsyncSession,
    period: Literal['day', 'week', 'month'] = 'week',
    daily_goal: Optional[float] = None
) -> Optional[bytes]:
    """График потребления воды."""
    return await _generate_consumption_plot(
        user_id=user_id,
        session=session,
        model=DrinkEntry,
        amount_field='volume_ml',
        ylabel='Вода (мл)',
        title='💧 Потребление воды',
        color=COLORS['water'],
        period=period,
        daily_goal=daily_goal
    )

async def generate_calorie_plot(
    user_id: int,
    session: AsyncSession,
    period: Literal['day', 'week', 'month'] = 'week',
    daily_goal: Optional[float] = None
) -> Optional[bytes]:
    """График потребления калорий."""
    return await _generate_consumption_plot(
        user_id=user_id,
        session=session,
        model=Meal,
        amount_field='total_calories',
        ylabel='Калории (ккал)',
        title='🔥 Потребление калорий',
        color=COLORS['calories'],
        period=period,
        daily_goal=daily_goal
    )

async def generate_activity_plot(
    user_id: int,
    session: AsyncSession,
    period: Literal['day', 'week', 'month'] = 'week',
    daily_goal: Optional[float] = None
) -> Optional[bytes]:
    """График сожжённых калорий (активность)."""
    return await _generate_consumption_plot(
        user_id=user_id,
        session=session,
        model=Activity,
        amount_field='calories_burned',
        ylabel='Сожжено (ккал)',
        title='🏃 Активность (сожжённые калории)',
        color=COLORS['activity'],
        period=period,
        daily_goal=daily_goal
    )

async def _generate_consumption_plot(
    user_id: int,
    session: AsyncSession,
    model,
    amount_field: str,
    ylabel: str,
    title: str,
    color: str,
    period: Literal['day', 'week', 'month'] = 'week',
    daily_goal: Optional[float] = None
) -> Optional[bytes]:
    """
    Универсальная функция для графиков потребления/активности.
    Для дня: столбцовая диаграмма + итоговые столбцы.
    Для недели/месяца: линейный график с заливкой и линией нормы.
    """
    try:
        now = datetime.now()

        if period == 'day':
            start_date = now - timedelta(hours=24)
            result = await session.execute(
                select(model).where(
                    model.user_id == user_id,
                    model.datetime >= start_date
                ).order_by(model.datetime)
            )
            entries = result.scalars().all()
            if not entries:
                logger.warning(f"Нет записей для графика {clean_title(title)} за день")
                return None

            # Почасовая группировка
            hourly = {}
            for e in entries:
                hour_key = e.datetime.replace(minute=0, second=0, microsecond=0)
                amount = getattr(e, amount_field) or 0
                hourly[hour_key] = hourly.get(hour_key, 0) + amount

            hours = sorted(hourly.keys())
            values = [hourly[h] for h in hours]
            labels = [h.strftime('%H:%M') for h in hours]

            # Добавляем итоговые столбцы
            total_value = sum(values)
            labels.append('Всего')
            values.append(total_value)
            if daily_goal is not None:
                labels.append('Норма')
                values.append(daily_goal)

            plt.figure(figsize=(12, 6))
            ax = plt.gca()
            x = range(len(labels))
            bars = ax.bar(x, values, color=['#1f77b4']*len(hours) + ['#ff7f0e', '#2ca02c'],
                           alpha=0.8, edgecolor='white', linewidth=1)

            # Подписи значений
            for bar, val in zip(bars, values):
                if val > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                             f'{int(val)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')

            # Заголовок (без эмодзи)
            ax.set_title(clean_title(f'{title} (последние 24 часа)'), fontsize=16, fontweight='bold', pad=20)

            ax.set_xlabel('Время', fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.grid(True, axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
            plt.close()
            buf.seek(0)
            return buf.read()

        else:  # week или month
            if period == 'week':
                start_date = now - timedelta(days=7)
                title_suffix = ' (последние 7 дней)'
            else:
                start_date = now - timedelta(days=30)
                title_suffix = ' (последние 30 дней)'

            result = await session.execute(
                select(model).where(
                    model.user_id == user_id,
                    model.datetime >= start_date
                ).order_by(model.datetime)
            )
            entries = result.scalars().all()
            if not entries:
                logger.warning(f"Нет записей для графика {clean_title(title)} за {period}")
                return None

            # Группировка по дням
            daily = {}
            for e in entries:
                day_key = e.datetime.date()
                amount = getattr(e, amount_field) or 0
                daily[day_key] = daily.get(day_key, 0) + amount

            days = sorted(daily.keys())
            values = [daily[d] for d in days]
            # Преобразуем даты в datetime для правильного отображения на оси
            dates = [datetime.combine(d, datetime.min.time()) for d in days]

            plt.figure(figsize=(12, 6))
            ax = plt.gca()

            # Линейный график с маркерами
            ax.plot(dates, values, marker='o', linestyle='-', linewidth=2.5,
                     color=color, markersize=6, label='Факт')
            ax.fill_between(dates, 0, values, alpha=0.2, color=color)

            # Линия нормы (если передана)
            if daily_goal is not None:
                ax.axhline(y=daily_goal, color=COLORS['goal'], linestyle='--', linewidth=2,
                            alpha=0.8, label=f'Норма {daily_goal:.0f}')

            # Подписи значений
            for i, (d, val) in enumerate(zip(dates, values)):
                if val > 0:
                    ax.text(d, val + (max(values)*0.02), f'{int(val)}',
                             ha='center', va='bottom', fontsize=8, rotation=0)

            # Настройка оси X
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            # Если дней много, показываем не все подписи, чтобы не сливались
            if len(dates) > 10:
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            else:
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=45, ha='right')

            # Заголовок (без эмодзи)
            ax.set_title(clean_title(title + title_suffix), fontsize=16, fontweight='bold', pad=20)

            ax.set_xlabel('Дата', fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='best')
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
            plt.close()
            buf.seek(0)
            return buf.read()

    except Exception as e:
        logger.error(f"❌ Ошибка при генерации графика {clean_title(title)}: {e}", exc_info=True)
        return None
