"""
services/activity_service.py
Сервис для сохранения и обработки активности
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from database.db import get_session
from database.models import Activity, User
from sqlalchemy import select

logger = logging.getLogger(__name__)

def estimate_calories_burned(activity_type: str, duration_min: int, weight_kg: Optional[float] = None) -> int:
    """
    Оценивает сожженные калории по типу активности и длительности
    
    Args:
        activity_type: Тип активности
        duration_min: Длительность в минутах
        weight_kg: Вес пользователя (для более точного расчета)
        
    Returns:
        int: Примерное количество сожженных калорий
    """
    # Используем единый словарь из activity.py
    from services.activity import CALORIES_PER_MINUTE
    
    # Получаем MET значение из единого источника
    met_value = CALORIES_PER_MINUTE.get(activity_type, 3.5)  # По умолчанию ходьба
    
    # Если вес не указан, используем среднее значение
    if weight_kg is None:
        weight_kg = 70.0
    
    # Расчет калорий: MET × вес(кг) × время(мин) / 60
    calories = int(met_value * weight_kg * duration_min / 60)
    
    return max(calories, 1)  # Минимум 1 калория

async def save_activity(user_id: int, activity_type: str, duration_min: int, 
                       calories_burned: Optional[int] = None, 
                       description: Optional[str] = None) -> Dict[str, Any]:
    """
    Сохраняет активность пользователя в базу данных
    
    Args:
        user_id: ID пользователя
        activity_type: Тип активности
        duration_min: Длительность в минутах
        calories_burned: Сожженные калории (если None, рассчитываются автоматически)
        description: Описание активности
        
    Returns:
        dict: Результат сохранения с данными активности
    """
    try:
        async with get_session() as session:
            # Получаем пользователя для веса
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            # Рассчитываем калории если не указаны
            if calories_burned is None:
                weight_kg = user.weight if user else None
                calories_burned = estimate_calories_burned(activity_type, duration_min, weight_kg)
            
            # Создаем запись об активности
            activity = Activity(
                user_id=user_id,
                activity_type=activity_type,
                duration_min=duration_min,
                calories_burned=calories_burned,
                description=description or f"{activity_type} {duration_min} мин",
                datetime=datetime.now()
            )
            
            session.add(activity)
            await session.commit()
            await session.refresh(activity)
            
            logger.info(f"Activity saved: {activity_type} for user {user_id}, {calories_burned} cal")
            
            return {
                "success": True,
                "activity_id": activity.id,
                "activity_type": activity_type,
                "duration_min": duration_min,
                "calories_burned": calories_burned,
                "description": description,
                "datetime": activity.datetime
            }
            
    except Exception as e:
        logger.error(f"Error saving activity for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def get_user_activities(user_id: int, days: int = 7) -> list:
    """
    Получает активность пользователя за последние дни
    
    Args:
        user_id: ID пользователя
        days: Количество дней для выборки
        
    Returns:
        list: Список активностей
    """
    try:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        async with get_session() as session:
            result = await session.execute(
                select(Activity).where(
                    Activity.user_id == user_id,
                    Activity.datetime >= start_date
                ).order_by(Activity.datetime.desc())
            )
            activities = result.scalars().all()
            return list(activities)
            
    except Exception as e:
        logger.error(f"Error getting activities for user {user_id}: {e}")
        return []

async def get_activity_stats(user_id: int, days: int = 7) -> Dict[str, Any]:
    """
    Получает статистику активности пользователя
    
    Args:
        user_id: ID пользователя
        days: Количество дней для статистики
        
    Returns:
        dict: Статистика активности
    """
    try:
        activities = await get_user_activities(user_id, days)
        
        if not activities:
            return {
                "total_activities": 0,
                "total_duration": 0,
                "total_calories": 0,
                "avg_duration": 0,
                "most_common_type": None
            }
        
        total_duration = sum(a.duration_min for a in activities)
        total_calories = sum(a.calories_burned for a in activities)
        
        # Самый частый тип активности
        type_counts = {}
        for activity in activities:
            type_counts[activity.activity_type] = type_counts.get(activity.activity_type, 0) + 1
        
        most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        
        return {
            "total_activities": len(activities),
            "total_duration": total_duration,
            "total_calories": total_calories,
            "avg_duration": total_duration // len(activities),
            "most_common_type": most_common_type,
            "period_days": days
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
