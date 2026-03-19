"""
services/weight_service.py
Сервис для сохранения и обработки веса
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from database.db import get_session
from database.models import WeightEntry, User
from sqlalchemy import select, func

logger = logging.getLogger(__name__)

async def save_weight(user_id: int, weight_kg: float, 
                      notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Сохраняет запись веса пользователя
    
    Args:
        user_id: ID пользователя
        weight_kg: Вес в килограммах
        notes: Заметки
        
    Returns:
        dict: Результат сохранения
    """
    try:
        async for session in get_session():
            # Создаем запись о весе
            weight_entry = WeightEntry(
                user_id=user_id,
                weight=weight_kg,
                datetime=datetime.now(timezone.utc)
            )
            
            session.add(weight_entry)
            await session.commit()
            await session.refresh(weight_entry)
            
            logger.info(f"Weight saved: {weight_kg}kg for user {user_id}")
            
            return {
                "success": True,
                "weight_id": weight_entry.id,
                "weight_kg": weight_kg,
                "datetime": weight_entry.datetime
            }
            
    except Exception as e:
        logger.error(f"Error saving weight for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def get_user_weights(user_id: int, days: int = 30) -> List[WeightEntry]:
    """
    Получает записи веса пользователя за последние дни
    
    Args:
        user_id: ID пользователя
        days: Количество дней для выборки
        
    Returns:
        List[WeightEntry]: Список записей веса
    """
    try:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        async for session in get_session():
            result = await session.execute(
                select(WeightEntry).where(
                    WeightEntry.user_id == user_id,
                    WeightEntry.datetime >= start_date
                ).order_by(WeightEntry.datetime.desc())
            )
            weights = result.scalars().all()
            return list(weights)
            
    except Exception as e:
        logger.error(f"Error getting weights for user {user_id}: {e}")
        return []

async def get_weight_stats(user_id: int, days: int = 30) -> Dict[str, Any]:
    """
    Получает статистику веса пользователя
    
    Args:
        user_id: ID пользователя
        days: Количество дней для статистики
        
    Returns:
        dict: Статистика веса
    """
    try:
        weights = await get_user_weights(user_id, days)
        
        if not weights:
            return {
                "total_records": 0,
                "current_weight": None,
                "weight_change": 0,
                "avg_weight": None,
                "min_weight": None,
                "max_weight": None,
                "trend": "no_data"
            }
        
        current_weight = weights[0].weight  # Самая свежая запись
        oldest_weight = weights[-1].weight  # Самая старая запись
        weight_change = current_weight - oldest_weight
        
        # Средний вес
        avg_weight = sum(w.weight for w in weights) / len(weights)
        
        # Минимальный и максимальный вес
        min_weight = min(w.weight for w in weights)
        max_weight = max(w.weight for w in weights)
        
        # Определяем тренд
        if abs(weight_change) < 0.5:  # Менее 0.5 кг изменения
            trend = "stable"
        elif weight_change > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "total_records": len(weights),
            "current_weight": current_weight,
            "weight_change": round(weight_change, 1),
            "avg_weight": round(avg_weight, 1),
            "min_weight": min_weight,
            "max_weight": max_weight,
            "trend": trend,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting weight stats for user {user_id}: {e}")
        return {
            "total_records": 0,
            "current_weight": None,
            "weight_change": 0,
            "avg_weight": None,
            "min_weight": None,
            "max_weight": None,
            "trend": "no_data"
        }

async def get_latest_weight(user_id: int) -> Optional[WeightEntry]:
    """
    Получает последнюю запись веса пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Optional[WeightEntry]: Последняя запись веса или None
    """
    try:
        async for session in get_session():
            result = await session.execute(
                select(WeightEntry).where(
                    WeightEntry.user_id == user_id
                ).order_by(WeightEntry.datetime.desc()).limit(1)
            )
            return result.scalar_one_or_none()
            
    except Exception as e:
        logger.error(f"Error getting latest weight for user {user_id}: {e}")
        return None

async def update_user_weight_goal(user_id: int, goal_weight_kg: float) -> Dict[str, Any]:
    """
    Обновляет целевой вес пользователя
    
    Args:
        user_id: ID пользователя
        goal_weight_kg: Целевой вес в килограммах
        
    Returns:
        dict: Результат обновления
    """
    try:
        async for session in get_session():
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.goal_weight = goal_weight_kg
                await session.commit()
                
                logger.info(f"Updated weight goal for user {user_id}: {goal_weight_kg}kg")
                
                return {
                    "success": True,
                    "goal_weight_kg": goal_weight_kg,
                    "previous_goal": getattr(user, 'goal_weight', None)
                }
            else:
                return {
                    "success": False,
                    "error": "User not found"
                }
                
    except Exception as e:
        logger.error(f"Error updating weight goal for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
