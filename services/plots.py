"""
Генерация современных и понятных графиков для прогресса.
✅ Линейные графики с заливкой области
✅ Горизонтальная линия нормы (где применимо)
✅ Поддержка периода: день (почасово + итоги), неделя/месяц (подневно)
✅ Исправлено отображение эмодзи через системные шрифты
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
from datetime import datetime, timedelta
from database.models import WeightEntry, WaterEntry, Meal, Activity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Literal
import logging
import numpy as np
import sys

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

# ========== ФУНКЦИЯ ДЛЯ ЗАГРУЗКИ ШРИФТА С ЭМОДЗИ ==========
def get_emoji_font():
    """
    Возвращает шрифт с поддержкой эмодзи в зависимости от ОС.
    Источник: https://github.com/matplotlib/matplotlib/issues/4492
    """
    if sys.platform == 'win32':
        # Windows: Segoe UI Emoji
        font_path = 'C:/Windows/Fonts/seguiemj.ttf'
    elif sys.platform == 'darwin':
        # macOS: Apple Color Emoji
        font_path = '/System/Library/Fonts/Apple Color Emoji.ttc'
    else:
        # Linux: Noto Color Emoji (нужно установить: apt install fonts-noto-color-emoji)
        font_path = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
    
    try:
        # Проверяем существование файла
        import os
        if os.path.exists(font_path):
            return fm.FontProperties(fname=font_path)
        else:
            logger.warning(f"Шрифт с эмодзи не найден по пути: {font_path}")
            return None
    except Exception as e:
        logger.warning(f"Ошибка загрузки шрифта с эмодзи: {e}")
        return None

# ========== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ТЕКСТА ==========
def add_text_with_emoji(ax, x, y, text, **kwargs):
    """
    Добавляет текст с поддержкой эмодзи.
    Если доступен шрифт с эмодзи, использует его, иначе обычный шрифт.
    """
    emoji_font = get_emoji_font()
    if emoji_font:
        ax.text(x, y, text, fontproperties=emoji_font, **kwargs)
    else:
        ax.text(x, y, text, **kwargs)

# ========== ОСНОВНЫЕ ФУНКЦИИ ГРАФИКОВ ==========

async def generate_weight_plot(user_id: int, session: AsyncSession) -> Optional[bytes]:
    """
    График динамики веса (все записи).
    Линейный график + линия тренда.
    """
    result = await session.execute(
        select(WeightEntry).where(WeightEntry.user_id == user_id).order_by(WeightEntry.datetime)
    )
    entries = result.scalars().all()
    if len(entries) < 2:
        return None

    dates = [e.datetime for e in entries]
    weights = [e.weight for e in entries]

    plt.figure(figsize=(12, 6))
    # Основная линия
    plt.plot(dates, weights, marker='o', linestyle='-', linewidth=2.5,
             color=COLORS['weight'], markersize=6, label='Вес')
    plt.fill_between(dates, min(weights)-1, weights, alpha=0.15, color=COLORS['weight'])

    # Линия тренда (полиномиальная регрессия 1-й степени)
    if len(weights) > 3:
        z = np.polyfit(range(len(weights)), weights, 1)
        p = np.poly1d(z)
        plt.plot(dates, p(range(len(weights))), '--', linewidth=2,
                 color=COLORS['trend'], label='Тренд')

    # Заголовок с эмодзи
    title_font = get_emoji_font()
    if title_font:
        plt.title('📈 Динамика веса', fontsize=16, fontweight='bold', pad=20, fontproperties=title_font)
    else:
        plt.title('Динамика веса', fontsize=16, fontweight='bold', pad=20)
    
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Вес (кг)', fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='best')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    plt.close()
    buf.seek(0)
    return buf.read()

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
        model=WaterEntry,
        amount_field='amount',
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
        x = range(len(labels))
        bars = plt.bar(x, values, color=['#1f77b4']*len(hours) + ['#ff7f0e', '#2ca02c'],
                       alpha=0.8, edgecolor='white', linewidth=1)

        # Подписи значений с поддержкой эмодзи
        for bar, val in zip(bars, values):
            if val > 0:
                plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                         f'{int(val)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.xticks(x, labels, rotation=45, ha='right')
        
        # Заголовок с эмодзи
        title_font = get_emoji_font()
        if title_font:
            plt.title(f'{title} (последние 24 часа)', fontsize=16, fontweight='bold', pad=20, fontproperties=title_font)
        else:
            plt.title(f'{title} (последние 24 часа)', fontsize=16, fontweight='bold', pad=20)
        
        plt.xlabel('Время', fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, axis='y', alpha=0.3, linestyle='--')
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
            return None

        # Группировка по дням
        daily = {}
        for e in entries:
            day_key = e.datetime.date()
            amount = getattr(e, amount_field) or 0
            daily[day_key] = daily.get(day_key, 0) + amount

        days = sorted(daily.keys())
        values = [daily[d] for d in days]
        labels = [d.strftime('%d.%m') for d in days]

        plt.figure(figsize=(12, 6))
        # Линейный график с маркерами
        plt.plot(range(len(labels)), values, marker='o', linestyle='-', linewidth=2.5,
                 color=color, markersize=6, label='Факт')
        plt.fill_between(range(len(labels)), 0, values, alpha=0.2, color=color)

        # Линия нормы (если передана)
        if daily_goal is not None:
            plt.axhline(y=daily_goal, color=COLORS['goal'], linestyle='--', linewidth=2,
                        alpha=0.8, label=f'Норма {daily_goal:.0f}')

        # Подписи значений
        for i, val in enumerate(values):
            if val > 0:
                plt.text(i, val + (max(values)*0.02), f'{int(val)}',
                         ha='center', va='bottom', fontsize=8, rotation=0)

        plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
        
        # Заголовок с эмодзи
        title_font = get_emoji_font()
        if title_font:
            plt.title(title + title_suffix, fontsize=16, fontweight='bold', pad=20, fontproperties=title_font)
        else:
            plt.title(title + title_suffix, fontsize=16, fontweight='bold', pad=20)
        
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend(loc='best')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        plt.close()
        buf.seek(0)
        return buf.read()
