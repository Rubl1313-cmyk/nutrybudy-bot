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
import os
import matplotlib.dates as mdates

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
    """
    # Список возможных путей к шрифтам с эмодзи
    font_paths = []
    
    if os.name == 'nt':  # Windows
        font_paths = [
            'C:/Windows/Fonts/seguiemj.ttf',
            'C:/Windows/Fonts/SEGUIEMJ.TTF'
        ]
    elif os.name == 'posix':  # Linux/macOS
        font_paths = [
            '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',  # fallback
            '/System/Library/Fonts/Apple Color Emoji.ttc',  # macOS
        ]
    
    # Пробуем каждый путь
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return fm.FontProperties(fname=font_path)
            except Exception as e:
                logger.warning(f"Failed to load font {font_path}: {e}")
                continue
    
    # Если ничего не нашли, используем шрифт по умолчанию (без эмодзи, но не будет ошибок)
    logger.warning("No emoji font found, using default font")
    return None

# Кешируем шрифт, чтобы не искать каждый раз
_EMOJI_FONT = get_emoji_font()

def add_text_with_emoji(ax, x, y, text, **kwargs):
    """
    Добавляет текст с поддержкой эмодзи.
    Если доступен шрифт с эмодзи, использует его, иначе обычный шрифт.
    """
    if _EMOJI_FONT:
        ax.text(x, y, text, fontproperties=_EMOJI_FONT, **kwargs)
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

    # Настройка оси X
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))  # формат: день.месяц
    # Устанавливаем локатор на каждый день, где есть данные
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45, ha='right')

    # Заголовок и подписи
    title_font = get_emoji_font()
    if title_font:
        plt.title('📈 Динамика веса', fontsize=16, fontweight='bold', pad=20, fontproperties=title_font)
    else:
        plt.title('Динамика веса', fontsize=16, fontweight='bold', pad=20)

    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Вес (кг)', fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='best')
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
        title="💧 Потребление воды",
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
        title="🔥 Потребление калорий",
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
        title="🏃 Активность (сожжённые калории)",
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

        # Подписи значений
        for bar, val in zip(bars, values):
            if val > 0:
                plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                         f'{int(val)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.xticks(x, labels, rotation=45, ha='right')
        
        # Заголовок с эмодзи
        ax = plt.gca()
        ax.set_title("")
        add_text_with_emoji(ax, 0.5, 1.02, f"{title} (последние 24 часа)", 
                            transform=ax.transAxes, ha='center', fontsize=16, fontweight='bold')
        
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
        ax = plt.gca()
        ax.set_title("")
        add_text_with_emoji(ax, 0.5, 1.02, f"{title}{title_suffix}", 
                            transform=ax.transAxes, ha='center', fontsize=16, fontweight='bold')
        
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
