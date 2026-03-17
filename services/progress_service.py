"""
services/progress_service.py
Сервис для получения статистики и прогресса
"""
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from database.db import get_session
from database.models import Meal, DrinkEntry, Activity, WeightEntry, User
from sqlalchemy import select, func, extract
from utils.daily_stats import get_daily_stats, get_daily_water, get_daily_drink_calories, get_daily_activity_calories

logger = logging.getLogger(__name__)

async def get_progress_stats(user_id: int, period: str = "day") -> Dict[str, Any]:
    """
    Получает полную статистику прогресса пользователя за период
    
    Args:
        user_id: ID пользователя
        period: Период (day, week, month, all)
        
    Returns:
        dict: Статистика прогресса
    """
    try:
        # Определяем дату начала периода
        if period == "day":
            start_date = date.today()
            period_name = "сегодня"
        elif period == "week":
            start_date = date.today() - timedelta(days=7)
            period_name = "за неделю"
        elif period == "month":
            start_date = date.today() - timedelta(days=30)
            period_name = "за месяц"
        else:  # all
            start_date = None
            period_name = "за всё время"
        
        # Получаем статистику питания
        nutrition_stats = await get_nutrition_stats(user_id, start_date)
        
        # Получаем статистику активности
        activity_stats = await get_activity_stats(user_id, start_date)
        
        # Получаем статистику веса
        weight_stats = await get_weight_progress(user_id, start_date)
        
        # Получаем статистику жидкости
        hydration_stats = await get_hydration_stats(user_id, start_date)
        
        # Получаем цели пользователя
        user_goals = await get_user_goals(user_id)
        
        # Рассчитываем прогресс по целям
        progress_by_goals = calculate_progress_by_goals(nutrition_stats, hydration_stats, user_goals)
        
        return {
            "period": period,
            "period_name": period_name,
            "nutrition": nutrition_stats,
            "activity": activity_stats,
            "weight": weight_stats,
            "hydration": hydration_stats,
            "goals": user_goals,
            "progress": progress_by_goals,
            "start_date": start_date,
            "end_date": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting progress stats for user {user_id}, period {period}: {e}")
        return {
            "period": period,
            "period_name": period,
            "nutrition": {"error": str(e)},
            "activity": {"error": str(e)},
            "weight": {"error": str(e)},
            "hydration": {"error": str(e)},
            "goals": {},
            "progress": {}
        }

async def get_nutrition_stats(user_id: int, start_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Получает статистику питания
    
    Args:
        user_id: ID пользователя
        start_date: Начальная дата периода
        
    Returns:
        dict: Статистика питания
    """
    try:
        async with get_session() as session:
            # Базовые условия
            conditions = [Meal.user_id == user_id]
            if start_date:
                conditions.append(Meal.datetime >= start_date)
            
            # Статистика по приемам пищи
            result = await session.execute(
                select(
                    func.count(Meal.id).label('total_meals'),
                    func.sum(Meal.total_calories).label('total_calories'),
                    func.sum(Meal.total_protein).label('total_protein'),
                    func.sum(Meal.total_fat).label('total_fat'),
                    func.sum(Meal.total_carbs).label('total_carbs')
                ).where(*conditions)
            )
            stats = result.first()
            
            return {
                "total_meals": stats.total_meals or 0,
                "total_calories": int(stats.total_calories or 0),
                "total_protein": float(stats.total_protein or 0),
                "total_fat": float(stats.total_fat or 0),
                "total_carbs": float(stats.total_carbs or 0),
                "avg_calories_per_meal": int((stats.total_calories or 0) / (stats.total_meals or 1))
            }
            
    except Exception as e:
        logger.error(f"Error getting nutrition stats for user {user_id}: {e}")
        return {
            "total_meals": 0,
            "total_calories": 0,
            "total_protein": 0,
            "total_fat": 0,
            "total_carbs": 0,
            "avg_calories_per_meal": 0
        }

async def get_activity_stats(user_id: int, start_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Получает статистику активности
    
    Args:
        user_id: ID пользователя
        start_date: Начальная дата периода
        
    Returns:
        dict: Статистика активности
    """
    try:
        async with get_session() as session:
            # Базовые условия
            conditions = [Activity.user_id == user_id]
            if start_date:
                conditions.append(Activity.datetime >= start_date)
            
            # Статистика по активности
            result = await session.execute(
                select(
                    func.count(Activity.id).label('total_activities'),
                    func.sum(Activity.duration_min).label('total_duration'),
                    func.sum(Activity.calories_burned).label('total_calories')
                ).where(*conditions)
            )
            stats = result.first()
            
            # Самый частый тип активности
            type_result = await session.execute(
                select(
                    Activity.activity_type,
                    func.count(Activity.id).label('count')
                ).where(*conditions).group_by(Activity.activity_type).order_by(func.count(Activity.id).desc()).limit(1)
            )
            most_common = type_result.first()
            
            return {
                "total_activities": stats.total_activities or 0,
                "total_duration": int(stats.total_duration or 0),
                "total_calories": int(stats.total_calories or 0),
                "avg_duration": int((stats.total_duration or 0) / (stats.total_activities or 1)),
                "most_common_type": most_common.activity_type if most_common else None
            }
            
    except Exception as e:
        logger.error(f"Error getting activity stats for user {user_id}: {e}")
        return {
            "total_activities": 0,
            "total_duration": 0,
            "total_calories": 0,
            "avg_duration": 0,
            "most_common_type": None
        }

async def get_weight_progress(user_id: int, start_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Получает прогресс веса
    
    Args:
        user_id: ID пользователя
        start_date: Начальная дата периода
        
    Returns:
        dict: Прогресс веса
    """
    try:
        async with get_session() as session:
            # Базовые условия
            conditions = [WeightEntry.user_id == user_id]
            if start_date:
                conditions.append(WeightEntry.datetime >= start_date)
            
            # Получаем записи веса
            result = await session.execute(
                select(WeightEntry).where(*conditions).order_by(WeightEntry.datetime.desc())
            )
            weights = result.scalars().all()
            
            if not weights:
                return {
                    "total_records": 0,
                    "current_weight": None,
                    "weight_change": 0,
                    "trend": "no_data"
                }
            
            current_weight = weights[0].weight
            weight_change = 0
            
            if len(weights) > 1:
                oldest_weight = weights[-1].weight
                weight_change = current_weight - oldest_weight
            
            # Определяем тренд
            if abs(weight_change) < 0.5:
                trend = "stable"
            elif weight_change > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            return {
                "total_records": len(weights),
                "current_weight": current_weight,
                "weight_change": round(weight_change, 1),
                "trend": trend
            }
            
    except Exception as e:
        logger.error(f"Error getting weight progress for user {user_id}: {e}")
        return {
            "total_records": 0,
            "current_weight": None,
            "weight_change": 0,
            "trend": "no_data"
        }

async def get_hydration_stats(user_id: int, start_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Получает статистику гидрации
    
    Args:
        user_id: ID пользователя
        start_date: Начальная дата периода
        
    Returns:
        dict: Статистика гидрации
    """
    try:
        async with get_session() as session:
            # Базовые условия
            conditions = [DrinkEntry.user_id == user_id]
            if start_date:
                conditions.append(DrinkEntry.datetime >= start_date)
            
            # Статистика по напиткам
            result = await session.execute(
                select(
                    func.count(DrinkEntry.id).label('total_entries'),
                    func.sum(DrinkEntry.volume_ml).label('total_volume'),
                    func.sum(DrinkEntry.calories).label('total_calories')
                ).where(*conditions)
            )
            stats = result.first()
            
            return {
                "total_entries": stats.total_entries or 0,
                "total_volume_ml": int(stats.total_volume or 0),
                "total_calories": int(stats.total_calories or 0),
                "avg_volume_per_entry": int((stats.total_volume or 0) / (stats.total_entries or 1))
            }
            
    except Exception as e:
        logger.error(f"Error getting hydration stats for user {user_id}: {e}")
        return {
            "total_entries": 0,
            "total_volume_ml": 0,
            "total_calories": 0,
            "avg_volume_per_entry": 0
        }

async def get_user_goals(user_id: int) -> Dict[str, Any]:
    """
    Получает цели пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        dict: Цели пользователя
    """
    try:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                return {
                    "daily_calorie_goal": user.daily_calorie_goal,
                    "daily_protein_goal": user.daily_protein_goal,
                    "daily_fat_goal": user.daily_fat_goal,
                    "daily_carbs_goal": user.daily_carbs_goal,
                    "daily_water_goal": user.daily_water_goal,
                    "goal_weight": user.goal_weight
                }
            else:
                return {}
                
    except Exception as e:
        logger.error(f"Error getting user goals for {user_id}: {e}")
        return {}

def calculate_progress_by_goals(nutrition_stats: Dict, hydration_stats: Dict, user_goals: Dict) -> Dict[str, Any]:
    """
    Рассчитывает прогресс по целям
    
    Args:
        nutrition_stats: Статистика питания
        hydration_stats: Статистика гидрации
        user_goals: Цели пользователя
        
    Returns:
        dict: Прогресс по целям
    """
    progress = {}
    
    # Прогресс по калориям
    if user_goals.get("daily_calorie_goal"):
        calorie_progress = min(100, (nutrition_stats["total_calories"] / user_goals["daily_calorie_goal"]) * 100)
        progress["calories"] = {
            "goal": user_goals["daily_calorie_goal"],
            "actual": nutrition_stats["total_calories"],
            "progress_percent": round(calorie_progress, 1)
        }
    
    # Прогресс по белкам
    if user_goals.get("daily_protein_goal"):
        protein_progress = min(100, (nutrition_stats["total_protein"] / user_goals["daily_protein_goal"]) * 100)
        progress["protein"] = {
            "goal": user_goals["daily_protein_goal"],
            "actual": nutrition_stats["total_protein"],
            "progress_percent": round(protein_progress, 1)
        }
    
    # Прогресс по воде
    if user_goals.get("daily_water_goal"):
        water_progress = min(100, (hydration_stats["total_volume_ml"] / user_goals["daily_water_goal"]) * 100)
        progress["water"] = {
            "goal": user_goals["daily_water_goal"],
            "actual": hydration_stats["total_volume_ml"],
            "progress_percent": round(water_progress, 1)
        }
    
    return progress
