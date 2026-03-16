"""
utils/helpers.py
Вспомогательные функции для NutriBuddy Bot
"""
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

async def get_daily_stats(user_id: int) -> Dict[str, Any]:
    """
    Получает суточную статистику питания пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        dict: Словарь с калориями и БЖУ за сегодня
    """
    try:
        from database.db import get_session
        from database.models import Meal
        from sqlalchemy import select, func
        
        async with get_session() as session:
            # Получаем все приемы пищи за сегодня
            meals_result = await session.execute(
                select(Meal).where(
                    Meal.user_id == user_id,
                    func.date(Meal.datetime) == date.today()
                )
            )
            meals = meals_result.scalars().all()
            
            # Суммируем значения
            stats = {
                'calories': sum(meal.total_calories or 0 for meal in meals),
                'protein': sum(meal.total_protein or 0 for meal in meals),
                'fat': sum(meal.total_fat or 0 for meal in meals),
                'carbs': sum(meal.total_carbs or 0 for meal in meals),
                'meals_count': len(meals)
            }
            
            logger.info(f"Daily stats for user {user_id}: {stats}")
            return stats
            
    except Exception as e:
        logger.error(f"Error getting daily stats for user {user_id}: {e}")
        return {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
            'meals_count': 0
        }

async def get_weekly_stats(user_id: int) -> Dict[str, Any]:
    """
    Получает недельную статистику питания пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        dict: Словарь со статистикой за неделю
    """
    try:
        from database.db import get_session
        from database.models import Meal
        from sqlalchemy import select, func
        from datetime import timedelta
        
        start_date = datetime.now() - timedelta(days=7)
        
        async with get_session() as session:
            meals_result = await session.execute(
                select(Meal).where(
                    Meal.user_id == user_id,
                    Meal.datetime >= start_date
                )
            )
            meals = meals_result.scalars().all()
            
            stats = {
                'calories': sum(meal.total_calories or 0 for meal in meals),
                'protein': sum(meal.total_protein or 0 for meal in meals),
                'fat': sum(meal.total_fat or 0 for meal in meals),
                'carbs': sum(meal.total_carbs or 0 for meal in meals),
                'meals_count': len(meals),
                'avg_daily_calories': sum(meal.total_calories or 0 for meal in meals) / 7
            }
            
            return stats
            
    except Exception as e:
        logger.error(f"Error getting weekly stats for user {user_id}: {e}")
        return {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
            'meals_count': 0,
            'avg_daily_calories': 0
        }

async def get_daily_water(user_id: int) -> int:
    """
    Получает количество выпитой жидкости за сегодня
    
    Args:
        user_id: ID пользователя
        
    Returns:
        int: Объем жидкости в мл
    """
    try:
        from database.db import get_session
        from database.models import DrinkEntry
        from sqlalchemy import select, func
        
        async with get_session() as session:
            result = await session.execute(
                select(func.sum(DrinkEntry.volume_ml)).where(
                    DrinkEntry.user_id == user_id,
                    func.date(DrinkEntry.datetime) == date.today()
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily water for user {user_id}: {e}")
        return 0

async def get_daily_drink_calories(user_id: int) -> int:
    """
    Получает калории из напитков за сегодня
    
    Args:
        user_id: ID пользователя
        
    Returns:
        int: Калории из напитков
    """
    try:
        from database.db import get_session
        from database.models import DrinkEntry
        from sqlalchemy import select, func
        
        async with get_session() as session:
            result = await session.execute(
                select(func.sum(DrinkEntry.calories)).where(
                    DrinkEntry.user_id == user_id,
                    func.date(DrinkEntry.datetime) == date.today()
                )
            )
            return result.scalar() or 0
            
    except Exception as e:
        logger.error(f"Error getting daily drink calories for user {user_id}: {e}")
        return 0

async def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает профиль пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        dict: Данные профиля или None
    """
    try:
        from database.db import get_session
        from database.models import User
        from sqlalchemy import select
        
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                return {
                    'id': user.id,
                    'telegram_id': user.telegram_id,
                    'name': user.name,
                    'age': user.age,
                    'gender': user.gender,
                    'height': user.height,
                    'weight': user.weight,
                    'activity_level': user.activity_level,
                    'goal': user.goal,
                    'daily_calorie_goal': user.daily_calorie_goal,
                    'daily_protein_goal': user.daily_protein_goal,
                    'daily_fat_goal': user.daily_fat_goal,
                    'daily_carbs_goal': user.daily_carbs_goal,
                    'daily_water_goal': user.daily_water_goal
                }
            return None
            
    except Exception as e:
        logger.error(f"Error getting user profile for {user_id}: {e}")
        return None

def format_nutrition_value(value: float, unit: str = "г") -> str:
    """
    Форматирует значение питательного вещества
    
    Args:
        value: Числовое значение
        unit: Единица измерения
        
    Returns:
        str: Отформатированная строка
    """
    if value == 0:
        return f"0{unit}"
    elif value < 1:
        return f"{value:.1f}{unit}"
    else:
        return f"{int(value)}{unit}"

def calculate_bmi(weight: float, height: float) -> float:
    """
    Рассчитывает ИМТ
    
    Args:
        weight: Вес в кг
        height: Рост в см
        
    Returns:
        float: Значение ИМТ
    """
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)

def get_bmi_category(bmi: float) -> str:
    """
    Возвращает категорию ИМТ
    
    Args:
        bmi: Значение ИМТ
        
    Returns:
        str: Категория ИМТ
    """
    if bmi < 18.5:
        return "Недостаточный вес"
    elif bmi < 25:
        return "Нормальный вес"
    elif bmi < 30:
        return "Избыточный вес"
    else:
        return "Ожирение"

# Старые функции для обратной совместимости
def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def format_date(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y")

def get_meal_type_emoji(meal_type: str) -> str:
    emojis = {
        'breakfast': '🥐',
        'lunch': '🥗',
        'dinner': '🍲',
        'snack': '🍎'
    }
    return emojis.get(meal_type, '🍽️')

def get_activity_type_emoji(activity_type: str) -> str:
    emojis = {
        'walking': '🚶',
        'running': '🏃',
        'cycling': '🚴',
        'gym': '🏋️',
        'yoga': '🧘',
        'swimming': '🏊',
        'hiit': '💪',
        'stretching': '🤸',
        'dancing': '💃',
        'sports': '⚽'
    }
    return emojis.get(activity_type, '🏃')

def normalize_exit_command(text: str) -> str:
    """
    Нормализует текст для проверки на выход: убирает пунктуацию, лишние пробелы.
    Используется для команд "выход", "выйти" и т.п.
    """
    # Удаляем все знаки препинания и лишние пробелы
    text = re.sub(r'[^\w\s]', '', text)
    text = text.strip().lower()
    return text
