"""
utils/daily_stats.py
Централизованные функции для получения дневной статистики
"""
import logging
from datetime import date, datetime, timedelta, timezone
from utils.timezone_utils import get_user_local_date
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def get_daily_water(user_id: int, user_timezone: str = 'UTC') -> int:
    """
    Получает количество выпитой жидкости за сегодня с учетом часового пояса
    
    Args:
        user_id: ID пользователя
        user_timezone: Часовой пояс пользователя
        
    Returns:
        int: Объем жидкости в мл
    """
    try:
        from database.db import get_session
        from database.models import DrinkEntry, User
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
            
            result = await session.execute(
                select(func.sum(DrinkEntry.amount)).where(
                    DrinkEntry.user_id == user_id,
                    func.date(DrinkEntry.created_at) == today_local
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily water for user {user_id}: {e}")
        return 0

async def get_daily_drink_calories(user_id: int, user_timezone: str = 'UTC') -> int:
    """
    Получает калории из напитков за сегодня с учетом часового пояса
    
    Args:
        user_id: ID пользователя
        user_timezone: Часовой пояс пользователя
        
    Returns:
        int: Калории из напитков
    """
    try:
        from database.db import get_session
        from database.models import DrinkEntry, User
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
            
            result = await session.execute(
                select(func.sum(DrinkEntry.calories)).where(
                    DrinkEntry.user_id == user_id,
                    func.date(DrinkEntry.created_at) == today_local
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily drink calories for user {user_id}: {e}")
        return 0

async def get_daily_activity_calories(user_id: int, user_timezone: str = 'UTC') -> int:
    """
    Получает сожженные калории через активность за сегодня с учетом часового пояса
    
    Args:
        user_id: ID пользователя
        user_timezone: Часовой пояс пользователя
        
    Returns:
        int: Сожженные калории
    """
    try:
        from database.db import get_session
        from database.models import ActivityEntry, User
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
            
            result = await session.execute(
                select(func.sum(ActivityEntry.calories_burned)).where(
                    ActivityEntry.user_id == user_id,
                    func.date(ActivityEntry.created_at) == today_local
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily activity calories for user {user_id}: {e}")
        return 0

async def get_daily_meals_count(user_id: int, user_timezone: str = 'UTC') -> int:
    """
    Получает количество приемов пищи за сегодня с учетом часового пояса
    
    Args:
        user_id: ID пользователя
        user_timezone: Часовой пояс пользователя
        
    Returns:
        int: Количество приемов пищи
    """
    try:
        from database.db import get_session
        from database.models import FoodEntry, User
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
            
            result = await session.execute(
                select(func.count(FoodEntry.id)).where(
                    FoodEntry.user_id == user_id,
                    func.date(FoodEntry.created_at) == today_local
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily meals count for user {user_id}: {e}")
        return 0

async def get_period_stats(user_id: int, period: str = "day", user_timezone: str = 'UTC') -> Dict[str, Any]:
    """
    Получает статистику за период с учетом часового пояса
    
    Args:
        user_id: ID пользователя
        period: period (day, week, month, all)
        user_timezone: Часовой пояс пользователя
        
    Returns:
        dict: Статистика за период
    """
    try:
        from database.db import get_session
        from database.models import FoodEntry, DrinkEntry, ActivityEntry, WeightEntry, User
        from sqlalchemy import select, func
        from datetime import timedelta
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Определяем дату начала периода
            if period == "day":
                start_date = get_user_local_date(user_tz)
            elif period == "week":
                start_date = get_user_local_date(user_tz) - timedelta(days=7)
            elif period == "month":
                start_date = get_user_local_date(user_tz) - timedelta(days=30)
            else:  # all
                start_date = None
            
            # Базовые условия
            conditions = [FoodEntry.user_id == user_id]
            if start_date:
                conditions.append(FoodEntry.created_at >= start_date)
            
            # Статистика по приемам пищи
            meals_result = await session.execute(select(FoodEntry).where(*conditions))
            meals = meals_result.scalars().all()
            
            stats = {
                'period': period,
                'meals_count': len(meals),
                'total_calories': sum(m.calories or 0 for m in meals),
                'total_protein': sum(m.protein or 0 for m in meals),
                'total_fat': sum(m.fat or 0 for m in meals),
                'total_carbs': sum(m.carbs or 0 for m in meals),
            }
            
            # Добавляем статистику по жидкости и активности
            if start_date:
                drink_conditions = [DrinkEntry.user_id == user_id, DrinkEntry.created_at >= start_date]
                activity_conditions = [ActivityEntry.user_id == user_id, ActivityEntry.created_at >= start_date]
            else:
                drink_conditions = [DrinkEntry.user_id == user_id]
                activity_conditions = [ActivityEntry.user_id == user_id]
            
            # Жидкость
            drink_result = await session.execute(
                select(func.sum(DrinkEntry.amount), func.sum(DrinkEntry.calories)).where(*drink_conditions)
            )
            water_total, calories_drinks = drink_result.first() or (0, 0)
            
            # Активность
            activity_result = await session.execute(
                select(func.sum(ActivityEntry.calories_burned), func.count(ActivityEntry.id)).where(*activity_conditions)
            )
            calories_activity, activities_count = activity_result.first() or (0, 0)
            
            # Вес
            if start_date:
                weight_conditions = [WeightEntry.user_id == user_id, WeightEntry.created_at >= start_date]
            else:
                weight_conditions = [WeightEntry.user_id == user_id]
                
            weight_result = await session.execute(
                select(WeightEntry.weight, WeightEntry.created_at).where(*weight_conditions).order_by(WeightEntry.created_at.desc())
            )
            weight_entries = weight_result.all()
            
            latest_weight = weight_entries[0].weight if weight_entries else None
            weight_trend = None
            if len(weight_entries) >= 2:
                first_weight = weight_entries[-1].weight
                latest_weight = weight_entries[0].weight
                weight_trend = latest_weight - first_weight
            
            stats.update({
                'total_water_ml': water_total or 0,
                'calories_from_drinks': calories_drinks or 0,
                'calories_burned': calories_activity,
                'activities_count': activities_count,
                'latest_weight': latest_weight,
                'weight_trend': weight_trend,
                'net_calories': stats['total_calories'] - calories_activity
            })
            
            return stats
            
    except Exception as e:
        logger.error(f"Error getting period stats for user {user_id}, period {period}: {e}")
        return {
            'period': period,
            'meals_count': 0,
            'total_calories': 0,
            'total_protein': 0,
            'total_fat': 0,
            'total_carbs': 0,
            'total_water_ml': 0,
            'calories_from_drinks': 0,
            'calories_burned': 0,
            'activities_count': 0,
            'latest_weight': None,
            'weight_trend': None,
            'net_calories': 0
        }

async def get_daily_calories(user_id: int) -> int:
    """
    Получает калории из еды за сегодня
    
    Args:
        user_id: ID пользователя
        
    Returns:
        int: Калории из еды
    """
    try:
        from database.db import get_session
        from database.models import FoodEntry, User
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
            
            result = await session.execute(
                select(func.sum(FoodEntry.calories)).where(
                    FoodEntry.user_id == user_id,
                    func.date(FoodEntry.created_at) == today_local
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily calories for user {user_id}: {e}")
        return 0

async def get_daily_protein(user_id: int) -> int:
    """
    Получает белок из еды за сегодня
    
    Args:
        user_id: ID пользователя
        
    Returns:
        int: Белок в граммах
    """
    try:
        from database.db import get_session
        from database.models import FoodEntry, User
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
            
            result = await session.execute(
                select(func.sum(FoodEntry.protein)).where(
                    FoodEntry.user_id == user_id,
                    func.date(FoodEntry.created_at) == today_local
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily protein for user {user_id}: {e}")
        return 0

async def get_daily_fat(user_id: int) -> int:
    """
    Получает жиры из еды за сегодня
    
    Args:
        user_id: ID пользователя
        
    Returns:
        int: Жиры в граммах
    """
    try:
        from database.db import get_session
        from database.models import FoodEntry, User
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
            
            result = await session.execute(
                select(func.sum(FoodEntry.fat)).where(
                    FoodEntry.user_id == user_id,
                    func.date(FoodEntry.created_at) == today_local
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily fat for user {user_id}: {e}")
        return 0

async def get_daily_carbs(user_id: int) -> int:
    """
    Получает углеводы из еды за сегодня
    
    Args:
        user_id: ID пользователя
        
    Returns:
        int: Углеводы в граммах
    """
    try:
        from database.db import get_session
        from database.models import FoodEntry, User
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
            
            result = await session.execute(
                select(func.sum(FoodEntry.carbs)).where(
                    FoodEntry.user_id == user_id,
                    func.date(FoodEntry.created_at) == today_local
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily carbs for user {user_id}: {e}")
        return 0

async def get_daily_stats(user_id: int) -> Dict[str, Any]:
    """
    Получает статистику за текущий день
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Dict с дневной статистикой
    """
    try:
        from database.db import get_session
        from database.models import User
        from sqlalchemy import select
        
        async with get_session() as session:
            # Получаем часовой пояс пользователя
            user_result = await session.execute(
                select(User.timezone).where(User.telegram_id == user_id)
            )
            user_tz = user_result.scalar() or 'UTC'
            
            # Получаем локальную дату пользователя
            today_local = get_user_local_date(user_tz)
        
        # Получаем статистику за день
        calories = await get_daily_calories(user_id)
        protein = await get_daily_protein(user_id)
        fat = await get_daily_fat(user_id)
        carbs = await get_daily_carbs(user_id)
        water = await get_daily_water(user_id)
        calories_burned = await get_daily_activity_calories(user_id)
        
        return {
            'date': today_local.isoformat(),
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
            'water_ml': water,
            'calories_burned': calories_burned,
            'net_calories': calories - calories_burned
        }
            
    except Exception as e:
        logger.error(f"Error getting daily stats for user {user_id}: {e}")
        return {
            'date': datetime.now(timezone.utc).date().isoformat(),
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
            'water_ml': 0,
            'calories_burned': 0,
            'net_calories': 0
        }
