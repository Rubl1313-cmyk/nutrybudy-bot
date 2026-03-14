"""
Утилиты для статистики - общий модуль чтобы избежать дублирования
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func
from database.models import Meal, Activity, WaterEntry, WeightEntry, StepsEntry

logger = logging.getLogger(__name__)

async def get_period_stats(user_id: int, session, start_date: datetime) -> dict:
    """📊 Получение статистики за период (универсальная функция)
    
    Args:
        user_id: Telegram ID пользователя
        session: Сессия базы данных
        start_date: Начальная дата периода
        
    Returns:
        dict: Статистика за период
    """
    try:
        # Получаем внутренний ID пользователя
        from database.models import User
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Пользователь {user_id} не найден в базе")
            return {}
            
        internal_user_id = user.id
        
        # Статистика приемов пищи
        meals_result = await session.execute(
            select(Meal).where(
                Meal.user_id == internal_user_id,
                Meal.datetime >= start_date
            )
        )
        meals = meals_result.scalars().all()
        
        # Статистика воды
        water_result = await session.execute(
            select(WaterEntry).where(
                WaterEntry.user_id == internal_user_id,
                WaterEntry.datetime >= start_date
            )
        )
        water_entries = water_result.scalars().all()
        
        # Статистика активности
        activity_result = await session.execute(
            select(Activity).where(
                Activity.user_id == internal_user_id,
                Activity.datetime >= start_date
            )
        )
        activities = activity_result.scalars().all()
        
        # Статистика веса
        weight_result = await session.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == internal_user_id,
                WeightEntry.datetime >= start_date
            )
        )
        weight_entries = weight_result.scalars().all()
        
        # Статистика шагов
        steps_result = await session.execute(
            select(StepsEntry).where(
                StepsEntry.user_id == internal_user_id,
                StepsEntry.datetime >= start_date
            )
        )
        steps_entries = steps_result.scalars().all()
        
        # Агрегированные данные
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_fat = sum(meal.fat for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        total_water = sum(entry.amount for entry in water_entries)
        total_steps = sum(entry.steps_count for entry in steps_entries)
        
        # Средние значения
        days_count = (datetime.utcnow() - start_date).days + 1
        avg_calories = total_calories / days_count if days_count > 0 else 0
        avg_protein = total_protein / days_count if days_count > 0 else 0
        avg_fat = total_fat / days_count if days_count > 0 else 0
        avg_carbs = total_carbs / days_count if days_count > 0 else 0
        avg_water = total_water / days_count if days_count > 0 else 0
        avg_steps = total_steps / days_count if days_count > 0 else 0
        
        # Тренд веса
        weight_trend = None
        if len(weight_entries) >= 2:
            weights = sorted([entry.weight for entry in weight_entries])
            weight_trend = weights[-1] - weights[0]
        
        return {
            'period_days': days_count,
            'meals_count': len(meals),
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_fat': total_fat,
            'total_carbs': total_carbs,
            'total_water': total_water,
            'total_steps': total_steps,
            'avg_calories': avg_calories,
            'avg_protein': avg_protein,
            'avg_fat': avg_fat,
            'avg_carbs': avg_carbs,
            'avg_water': avg_water,
            'avg_steps': avg_steps,
            'activities_count': len(activities),
            'weight_entries_count': len(weight_entries),
            'weight_trend': weight_trend,
            'start_date': start_date,
            'user_goals': {
                'calories': user.daily_calorie_goal or 2000,
                'protein': user.daily_protein_goal or 150,
                'fat': user.daily_fat_goal or 65,
                'carbs': user.daily_carbs_goal or 250,
                'water': user.daily_water_goal or 2000,
                'steps': user.daily_steps_goal or 10000
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return {}
