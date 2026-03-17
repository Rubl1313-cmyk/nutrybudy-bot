"""
utils/helpers.py
Ğ’Ñ�Ğ¿Ğ¾Ğ¼Ğ¾Ğ³Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ğ¸ Ğ´Ğ»Ñ� NutriBuddy Bot
"""
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

# Ğ£Ğ½Ğ¸Ñ„Ğ¸Ñ†Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ğ¸ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸ - Ğ¸Ğ¼Ğ¿Ğ¾Ñ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¸Ğ· daily_stats
from utils.daily_stats import (
    get_daily_stats, get_daily_water, get_daily_drink_calories, 
    get_daily_activity_calories, get_period_stats
)

async def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """
    ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµÑ‚ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
    
    Args:
        user_id: ID Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
        
    Returns:
        dict: Ğ”Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ� Ğ¸Ğ»Ğ¸ None
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

def format_nutrition_value(value: float, unit: str = "Ğ³") -> str:
    """
    Ğ¤Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ¸Ñ€ÑƒĞµÑ‚ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ Ğ¿Ğ¸Ñ‚Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğ³Ğ¾ Ğ²ĞµÑ‰ĞµÑ�Ñ‚Ğ²Ğ°
    
    Args:
        value: Ğ§Ğ¸Ñ�Ğ»Ğ¾Ğ²Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ
        unit: Ğ•Ğ´Ğ¸Ğ½Ğ¸Ñ†Ğ° Ğ¸Ğ·Ğ¼ĞµÑ€ĞµĞ½Ğ¸Ñ�
        
    Returns:
        str: Ğ�Ñ‚Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ� Ñ�Ñ‚Ñ€Ğ¾ĞºĞ°
    """
    if value == 0:
        return f"0{unit}"
    elif value < 1:
        return f"{value:.1f}{unit}"
    else:
        return f"{int(value)}{unit}"

def calculate_bmi(weight: float, height: float) -> float:
    """
    Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ˜ĞœĞ¢
    
    Args:
        weight: Ğ’ĞµÑ� Ğ² ĞºĞ³
        height: Ğ Ğ¾Ñ�Ñ‚ Ğ² Ñ�Ğ¼
        
    Returns:
        float: Ğ—Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ Ğ˜ĞœĞ¢
    """
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)

def get_bmi_category(bmi: float) -> str:
    """
    Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ ĞºĞ°Ñ‚ĞµĞ³Ğ¾Ñ€Ğ¸Ñ� Ğ˜ĞœĞ¢
    
    Args:
        bmi: Ğ—Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ Ğ˜ĞœĞ¢
        
    Returns:
        str: ĞšĞ°Ñ‚ĞµĞ³Ğ¾Ñ€Ğ¸Ñ� Ğ˜ĞœĞ¢
    """
    if bmi < 18.5:
        return "Ğ�ĞµĞ´Ğ¾Ñ�Ñ‚Ğ°Ñ‚Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ�"
    elif bmi < 25:
        return "Ğ�Ğ¾Ñ€Ğ¼Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ²ĞµÑ�"
    elif bmi < 30:
        return "Ğ˜Ğ·Ğ±Ñ‹Ñ‚Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ�"
    else:
        return "Ğ�Ğ¶Ğ¸Ñ€ĞµĞ½Ğ¸Ğµ"

# Ğ¡Ñ‚Ğ°Ñ€Ñ‹Ğµ Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ğ¸ Ğ´Ğ»Ñ� Ğ¾Ğ±Ñ€Ğ°Ñ‚Ğ½Ğ¾Ğ¹ Ñ�Ğ¾Ğ²Ğ¼ĞµÑ�Ñ‚Ğ¸Ğ¼Ğ¾Ñ�Ñ‚Ğ¸
def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def format_date(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y")

def get_meal_type_emoji(meal_type: str) -> str:
    emojis = {
        'breakfast': 'ğŸ¥�',
        'lunch': 'ğŸ¥—',
        'dinner': 'ğŸ�²',
        'snack': 'ğŸ��'
    }
    return emojis.get(meal_type, 'ğŸ�½ï¸�')

def get_activity_type_emoji(activity_type: str) -> str:
    emojis = {
        'walking': 'ğŸš¶',
        'running': 'ğŸ�ƒ',
        'cycling': 'ğŸš´',
        'gym': 'ğŸ�‹ï¸�',
        'yoga': 'ğŸ§˜',
        'swimming': 'ğŸ�Š',
        'hiit': 'ğŸ’ª',
        'stretching': 'ğŸ¤¸',
        'dancing': 'ğŸ’ƒ',
        'sports': 'âš½'
    }
    return emojis.get(activity_type, 'ğŸ�ƒ')

def normalize_exit_command(text: str) -> str:
    """
    Ğ�Ğ¾Ñ€Ğ¼Ğ°Ğ»Ğ¸Ğ·ÑƒĞµÑ‚ Ñ‚ĞµĞºÑ�Ñ‚ Ğ´Ğ»Ñ� Ğ¿Ñ€Ğ¾Ğ²ĞµÑ€ĞºĞ¸ Ğ½Ğ° Ğ²Ñ‹Ñ…Ğ¾Ğ´: ÑƒĞ±Ğ¸Ñ€Ğ°ĞµÑ‚ Ğ¿ÑƒĞ½ĞºÑ‚ÑƒĞ°Ñ†Ğ¸Ñ�, Ğ»Ğ¸ÑˆĞ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ğ±ĞµĞ»Ñ‹.
    Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµÑ‚Ñ�Ñ� Ğ´Ğ»Ñ� ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´ "Ğ²Ñ‹Ñ…Ğ¾Ğ´", "Ğ²Ñ‹Ğ¹Ñ‚Ğ¸" Ğ¸ Ñ‚.Ğ¿.
    """
    # Ğ£Ğ´Ğ°Ğ»Ñ�ĞµĞ¼ Ğ²Ñ�Ğµ Ğ·Ğ½Ğ°ĞºĞ¸ Ğ¿Ñ€ĞµĞ¿Ğ¸Ğ½Ğ°Ğ½Ğ¸Ñ� Ğ¸ Ğ»Ğ¸ÑˆĞ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ğ±ĞµĞ»Ñ‹
    text = re.sub(r'[^\w\s]', '', text)
    text = text.strip().lower()
    return text
