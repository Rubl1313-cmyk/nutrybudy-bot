"""
Ğ¡ĞµÑ€Ğ²Ğ¸Ñ� Ğ´Ğ»Ñ� Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ� Ñ�ÑƒĞ¿Ğ¾Ğ² (ĞµĞ´Ğ° + Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ)
"""
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from database.db import get_session
from database.models import User, Meal, DrinkEntry
from services.dish_db import COMPOSITE_DISHES, normalize_ai_dish_name
from utils.drink_parser import parse_drink

logger = logging.getLogger(__name__)

# Ğ‘Ğ°Ğ·Ğ° Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ¿Ğ¾ Ñ�ÑƒĞ¿Ğ°Ğ¼ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡Ñ‘Ñ‚Ğ° Ñ�Ğ¾Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ñ� Ğ²Ğ¾Ğ´Ñ‹
SOUP_WATER_CONTENT = {
    'Ğ±Ğ¾Ñ€Ñ‰': 0.85,        # 85% Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸
    'Ñ‰Ğ¸': 0.88,
    'Ñ�ÑƒĞ¿': 0.85,         # Ğ�Ğ±Ñ‹Ñ‡Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿
    'ÑƒÑ…Ğ°': 0.90,
    'Ñ€Ğ°Ñ�Ñ�Ğ¾Ğ»ÑŒĞ½Ğ¸Ğº': 0.86,
    'Ñ�Ğ¾Ğ»Ñ�Ğ½ĞºĞ°': 0.82,
    'Ğ¾ĞºÑ€Ğ¾ÑˆĞºĞ°': 0.92,
    'Ğ³ÑƒĞ»Ñ�Ñˆ': 0.75,       # Ğ‘Ğ¾Ğ»ĞµĞµ Ğ³ÑƒÑ�Ñ‚Ğ¾Ğ¹
    'Ñ€Ğ°Ğ³Ñƒ': 0.70,
    'ĞºĞ°Ñ€Ñ‚Ğ¾ÑˆĞºĞ°': 0.80,    # ĞšĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ñ€Ğ°Ğ³Ñƒ
}

# Ğ¡Ñ€ĞµĞ´Ğ½Ğ¸Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ� ĞšĞ‘Ğ–Ğ£ Ğ´Ğ»Ñ� Ñ�ÑƒĞ¿Ğ¾Ğ² (Ğ½Ğ° 100 Ğ¼Ğ»)
SOUP_NUTRITION_DEFAULTS = {
    'calories': 50,
    'protein': 2.0,
    'fat': 1.5,
    'carbs': 5.0,
}

def is_soup(dish_name: str) -> bool:
    """
    Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµÑ‚, Ñ�Ğ²Ğ»Ñ�ĞµÑ‚Ñ�Ñ� Ğ»Ğ¸ Ğ±Ğ»Ñ�Ğ´Ğ¾ Ñ�ÑƒĞ¿Ğ¾Ğ¼
    """
    dish_name = dish_name.lower()
    
    # ĞŸÑ€Ñ�Ğ¼Ñ‹Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ�
    soup_keywords = ['Ğ±Ğ¾Ñ€Ñ‰', 'Ñ‰Ğ¸', 'ÑƒÑ…Ğ°', 'Ñ�ÑƒĞ¿', 'Ñ€Ğ°Ñ�Ñ�Ğ¾Ğ»ÑŒĞ½Ğ¸Ğº', 'Ñ�Ğ¾Ğ»Ñ�Ğ½ĞºĞ°', 'Ğ¾ĞºÑ€Ğ¾ÑˆĞºĞ°', 'Ğ±ÑƒĞ»ÑŒĞ¾Ğ½']
    
    for keyword in soup_keywords:
        if keyword in dish_name:
            return True
    
    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¿Ğ¾ Ğ±Ğ°Ğ·Ğµ COMPOSITE_DISHES
    dish_key = normalize_ai_dish_name(dish_name)
    dish_info = COMPOSITE_DISHES.get(dish_key)
    
    if dish_info and dish_info.get('category') == 'soup':
        return True
    
    return False

def get_soup_water_content(dish_name: str) -> float:
    """
    Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµÑ‚ Ñ�Ğ¾Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ğµ Ğ²Ğ¾Ğ´Ñ‹ Ğ² Ñ�ÑƒĞ¿Ğµ
    """
    dish_name = dish_name.lower()
    
    # Ğ˜Ñ‰ĞµĞ¼ Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğµ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğµ
    for soup_name, water_content in SOUP_WATER_CONTENT.items():
        if soup_name in dish_name:
            return water_content
    
    # ĞŸĞ¾ ÑƒĞ¼Ğ¾Ğ»Ñ‡Ğ°Ğ½Ğ¸Ñ� - 85% Ğ²Ğ¾Ğ´Ñ‹
    return 0.85

def get_soup_nutrition(dish_name: str, volume_ml: float) -> dict:
    """
    Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµÑ‚ ĞšĞ‘Ğ–Ğ£ Ğ´Ğ»Ñ� Ñ�ÑƒĞ¿Ğ°
    
    Args:
        dish_name: Ğ�Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ñ�ÑƒĞ¿Ğ°
        volume_ml: Ğ�Ğ±ÑŠÑ‘Ğ¼ Ğ² Ğ¼Ğ»
        
    Returns:
        dict Ñ� ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ñ�Ğ¼Ğ¸, Ğ±ĞµĞ»ĞºĞ°Ğ¼Ğ¸, Ğ¶Ğ¸Ñ€Ğ°Ğ¼Ğ¸, ÑƒĞ³Ğ»ĞµĞ²Ğ¾Ğ´Ğ°Ğ¼Ğ¸
    """
    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ±Ğ°Ğ·Ñƒ COMPOSITE_DISHES
    dish_key = normalize_ai_dish_name(dish_name)
    dish_info = COMPOSITE_DISHES.get(dish_key)
    
    if dish_info and 'nutrition_per_100' in dish_info:
        nutrition = dish_info['nutrition_per_100']
        factor = volume_ml / 100
        
        return {
            'calories': nutrition.get('calories', 50) * factor,
            'protein': nutrition.get('protein', 2.0) * factor,
            'fat': nutrition.get('fat', 1.5) * factor,
            'carbs': nutrition.get('carbs', 5.0) * factor,
        }
    else:
        # Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ� Ğ¿Ğ¾ ÑƒĞ¼Ğ¾Ğ»Ñ‡Ğ°Ğ½Ğ¸Ñ�
        factor = volume_ml / 100
        return {
            key: value * factor 
            for key, value in SOUP_NUTRITION_DEFAULTS.items()
        }

async def save_soup(user_id: int, dish_name: str, volume_ml: float, meal_type: str = "soup"):
    """
    Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµÑ‚ Ñ�ÑƒĞ¿ ĞºĞ°Ğº Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸ Ğ¸ ĞºĞ°Ğº Ğ·Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸
    
    Returns:
        dict Ñ� ID Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ·Ğ°Ğ¿Ğ¸Ñ�ĞµĞ¹
    """
    try:
        # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ ĞšĞ‘Ğ–Ğ£
        nutrition = get_soup_nutrition(dish_name, volume_ml)
        
        # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¾Ğ±ÑŠÑ‘Ğ¼ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸
        water_content = get_soup_water_content(dish_name)
        water_volume = volume_ml * water_content
        
        async with get_session() as session:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # 1. Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ ĞºĞ°Ğº Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸ (Meal)
            meal = Meal(
                user_id=user.id,
                meal_type=meal_type,
                datetime=datetime.now(),
                total_calories=nutrition['calories'],
                total_protein=nutrition['protein'],
                total_fat=nutrition['fat'],
                total_carbs=nutrition['carbs'],
                ai_description=f"{dish_name} ({volume_ml} Ğ¼Ğ»)"
            )
            session.add(meal)
            await session.flush()
            
            # 2. Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ (DrinkEntry)
            drink = DrinkEntry(
                user_id=user.id,
                name=f"Ğ²Ğ¾Ğ´Ğ° Ğ¸Ğ· {dish_name}",
                volume_ml=water_volume,
                calories=0.0,  # Ğ’Ğ¾Ğ´Ñƒ Ğ¸Ğ· Ñ�ÑƒĞ¿Ğ° Ñ�Ñ‡Ğ¸Ñ‚Ğ°ĞµĞ¼ Ğ±ĞµĞ·ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹Ğ½Ğ¾Ğ¹
                source='food',  # Ğ˜Ñ�Ñ‚Ğ¾Ñ‡Ğ½Ğ¸Ğº - ĞµĞ´Ğ° (Ñ�ÑƒĞ¿)
                reference_id=meal.id,  # Ğ¡Ñ�Ñ‹Ğ»ĞºĞ° Ğ½Ğ° Ñ�Ğ²Ñ�Ğ·Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¸ĞµĞ¼ Ğ¿Ğ¸Ñ‰Ğ¸
                datetime=datetime.now(timezone.utc)
            )
            session.add(drink)
            await session.commit()
            
            logger.info(f"ğŸ�² Ğ¡ÑƒĞ¿ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ‘Ğ½: {dish_name} {volume_ml}Ğ¼Ğ» = {nutrition['calories']:.1f}ĞºĞºĞ°Ğ» + {water_volume:.0f}Ğ¼Ğ» Ğ²Ğ¾Ğ´Ñ‹")
            
            return {
                "meal_id": meal.id,
                "drink_id": drink.id,
                "calories": nutrition['calories'],
                "water_volume": water_volume
            }
            
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğ¸ Ñ�ÑƒĞ¿Ğ°: {e}")
        raise

async def save_drink(user_id: int, text: str):
    """
    Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµÑ‚ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº Ğ¸Ğ· Ñ‚ĞµĞºÑ�Ñ‚Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¸Ñ�
    
    Returns:
        dict Ñ� Ğ¸Ğ½Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ†Ğ¸ĞµĞ¹ Ğ¾ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ‘Ğ½Ğ½Ğ¾Ğ¼ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞµ
    """
    try:
        # ĞŸĞ°Ñ€Ñ�Ğ¸Ğ¼ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº
        volume, drink_name, calories = await parse_drink(text)
        
        if not volume:
            raise ValueError("Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ğ¸Ñ‚ÑŒ Ğ¾Ğ±ÑŠÑ‘Ğ¼ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°")
        
        async with get_session() as session:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº
            drink = DrinkEntry(
                user_id=user.id,
                name=drink_name,
                volume_ml=volume,
                calories=calories,
                source='drink',  # Ğ˜Ñ�Ñ‚Ğ¾Ñ‡Ğ½Ğ¸Ğº - Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº
                datetime=datetime.now(timezone.utc)
            )
            session.add(drink)
            await session.commit()
            
            logger.info(f"ğŸ¥¤ Ğ�Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ‘Ğ½: {drink_name} {volume}Ğ¼Ğ», {calories:.1f}ĞºĞºĞ°Ğ»")
            
            return {
                "drink_id": drink.id,
                "name": drink_name,
                "volume": volume,
                "calories": calories
            }
            
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğ¸ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°: {e}")
        raise
