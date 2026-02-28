import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from database.models import WeightEntry, WaterEntry, Meal, Activity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

async def generate_weight_plot(user_id: int, session: AsyncSession) -> bytes:
    result = await session.execute(
        select(WeightEntry).where(WeightEntry.user_id == user_id).order_by(WeightEntry.datetime)
    )
    entries = result.scalars().all()
    
    if len(entries) < 2:
        return None
    
    dates = [e.datetime for e in entries]
    weights = [e.weight for e in entries]
    
    plt.figure(figsize=(10, 5))
    plt.plot(dates, weights, marker='o', linestyle='-', color='blue', linewidth=2)
    plt.title('Динамика веса', fontsize=14, fontweight='bold')
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

async def generate_water_plot(user_id: int, session: AsyncSession) -> bytes:
    week_ago = datetime.now() - timedelta(days=7)
    result = await session.execute(
        select(WaterEntry).where(
            WaterEntry.user_id == user_id,
            WaterEntry.datetime >= week_ago
        ).order_by(WaterEntry.datetime)
    )
    entries = result.scalars().all()
    
    if not entries:
        return None
    
    days = {}
    for e in entries:
        day = e.datetime.date()
        days[day] = days.get(day, 0) + e.amount
    
    dates = list(days.keys())
    amounts = list(days.values())
    
    plt.figure(figsize=(10, 5))
    plt.bar(dates, amounts, color='blue', alpha=0.7)
    plt.title('Потребление воды за последние 7 дней', fontsize=14, fontweight='bold')
    plt.xlabel('Дата')
    plt.ylabel('Вода (мл)')
    plt.grid(True, axis='y', alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf.read()

async def generate_calorie_balance_plot(user_id: int, session: AsyncSession) -> bytes:
    week_ago = datetime.now() - timedelta(days=7)
    
    meals_result = await session.execute(
        select(Meal).where(
            Meal.user_id == user_id,
            Meal.datetime >= week_ago
        )
    )
    meals = meals_result.scalars().all()
    
    activities_result = await session.execute(
        select(Activity).where(
            Activity.user_id == user_id,
            Activity.datetime >= week_ago
        )
    )
    activities = activities_result.scalars().all()
    
    if not meals and not activities:
        return None
    
    days_consumed = {}
    days_burned = {}
    
    for m in meals:
        day = m.datetime.date()
        days_consumed[day] = days_consumed.get(day, 0) + m.total_calories
    
    for a in activities:
        day = a.datetime.date()
        days_burned[day] = days_burned.get(day, 0) + a.calories_burned
    
    all_days = sorted(set(days_consumed.keys()) | set(days_burned.keys()))
    consumed = [days_consumed.get(d, 0) for d in all_days]
    burned = [days_burned.get(d, 0) for d in all_days]
    
    plt.figure(figsize=(10, 5))
    x = range(len(all_days))
    plt.bar(x, consumed, label='Потреблено', color='orange', alpha=0.7)
    plt.bar(x, burned, label='Сожжено', color='green', alpha=0.7)
    plt.title('Баланс калорий за 7 дней', fontsize=14, fontweight='bold')
    plt.xlabel('Дата')
    plt.ylabel('Калории')
    plt.xticks(x, [d.strftime('%d.%m') for d in all_days], rotation=45)
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf.read()