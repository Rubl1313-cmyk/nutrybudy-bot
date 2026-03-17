"""
ğŸ�½ï¸� Ğ¡ĞµÑ€Ğ²Ğ¸Ñ� Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ� Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� - ÑƒĞ½Ğ¸Ñ„Ğ¸Ñ†Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ� Ğ»Ğ¾Ğ³Ğ¸ĞºĞ°
Ğ˜Ğ·Ğ±ĞµĞ³Ğ°ĞµÑ‚ Ğ´ÑƒĞ±Ğ»Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ� ĞºĞ¾Ğ´Ğ° Ğ¼ĞµĞ¶Ğ´Ñƒ media_handlers Ğ¸ enhanced_universal_handler
"""

import logging
import re
from typing import Dict, List, Any
from sqlalchemy import select
from database.db import get_session
from database.models import User, Meal, FoodItem
from utils.unit_converter import convert_to_grams
from datetime import datetime

logger = logging.getLogger(__name__)

class FoodSaveService:
    """Ğ£Ğ½Ğ¸Ñ„Ğ¸Ñ†Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ñ�ĞµÑ€Ğ²Ğ¸Ñ� Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ� ĞµĞ´Ñ‹"""
    
    @staticmethod
    async def save_food_to_db(
        user_id: int,
        food_items: List[Dict[str, Any]],
        meal_type: str = "main"
    ) -> Dict[str, Any]:
        """
        Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµÑ‚ ĞµĞ´Ñƒ Ğ² Ğ±Ğ°Ğ·Ñƒ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
        
        Args:
            user_id: Telegram ID Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            food_items: Ğ¡Ğ¿Ğ¸Ñ�Ğ¾Ğº Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ² Ğ¾Ñ‚ AI
            meal_type: Ğ¢Ğ¸Ğ¿ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸
            
        Returns:
            Dict Ñ� Ñ€ĞµĞ·ÑƒĞ»ÑŒÑ‚Ğ°Ñ‚Ğ¾Ğ¼ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�
        """
        try:
            async with get_session() as session:
                # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    return {
                        "success": False,
                        "error": "ĞŸĞ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ Ğ½Ğµ Ğ½Ğ°Ğ¹Ğ´ĞµĞ½"
                    }
                
                # Ğ¡Ğ¾Ğ·Ğ´Ğ°Ñ‘Ğ¼ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸
                meal = Meal(
                    user_id=user.id,
                    meal_type=meal_type,
                    datetime=datetime.now()
                )
                session.add(meal)
                await session.flush()  # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ ID meal
                
                total_calories = 0
                total_protein = 0
                total_fat = 0
                total_carbs = 0
                
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹
                for item in food_items:
                    # ĞšĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ²ĞµÑ� Ğ² Ğ³Ñ€Ğ°Ğ¼Ğ¼Ñ‹
                    quantity_str = item.get('quantity', '100 Ğ³')
                    unit = item.get('unit', 'Ğ³')
                    
                    # Ğ˜Ğ·Ğ²Ğ»ĞµĞºĞ°ĞµĞ¼ Ñ‡Ğ¸Ñ�Ğ»Ğ¾ Ğ¸Ğ· Ñ�Ñ‚Ñ€Ğ¾ĞºĞ¸ quantity
                    try:
                        if isinstance(quantity_str, str):
                            # Ğ˜Ñ‰ĞµĞ¼ Ñ‡Ğ¸Ñ�Ğ»Ğ¾ Ğ² Ñ�Ñ‚Ñ€Ğ¾ĞºĞµ
                            match = re.search(r'[-+]?\d*\.?\d+', quantity_str)
                            if match:
                                quantity = float(match.group())
                            else:
                                quantity = 100.0
                        elif quantity_str is None:
                            quantity = 100.0
                        else:
                            quantity = float(quantity_str)
                    except (ValueError, TypeError):
                        quantity = 100.0
                    
                    weight_grams = convert_to_grams(item.get('name', ''), quantity, unit)
                    
                    # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ ĞšĞ‘Ğ–Ğ£ Ñ� ÑƒÑ‡Ñ‘Ñ‚Ğ¾Ğ¼ Ğ²ĞµÑ�Ğ°
                    factor = weight_grams / 100.0
                    food_calories = item.get('calories', 0) * factor
                    food_protein = item.get('protein', 0) * factor
                    food_fat = item.get('fat', 0) * factor
                    food_carbs = item.get('carbs', 0) * factor
                    
                    # Ğ¡Ğ¾Ğ·Ğ´Ğ°Ñ‘Ğ¼ FoodItem Ñ� Ğ¿ĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ğ°Ğ½Ğ½Ñ‹Ğ¼Ğ¸ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ�Ğ¼Ğ¸
                    food_item = FoodItem(
                        meal_id=meal.id,
                        name=item.get('name', 'Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚'),
                        calories=food_calories,
                        protein=food_protein,
                        fat=food_fat,
                        carbs=food_carbs,
                        weight_grams=weight_grams
                    )
                    session.add(food_item)
                    
                    # Ğ¡ÑƒĞ¼Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¸Ñ‚Ğ¾Ğ³Ğ¾Ğ²Ñ‹Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ�
                    total_calories += food_calories
                    total_protein += food_protein
                    total_fat += food_fat
                    total_carbs += food_carbs
                
                # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¸Ñ‚Ğ¾Ğ³Ğ¾Ğ²Ñ‹Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ� Ğ² Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğµ Ğ¿Ğ¸Ñ‰Ğ¸
                meal.calories = total_calories
                meal.protein = total_protein
                meal.fat = total_fat
                meal.carbs = total_carbs
                
                await session.commit()
                
                return {
                    "success": True,
                    "message": f"Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¾ {len(food_items)} Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ²",
                    "total_calories": total_calories,
                    "total_protein": total_protein,
                    "total_fat": total_fat,
                    "total_carbs": total_carbs
                }
                
        except Exception as e:
            logger.error(f"Error saving food: {e}")
            return {
                "success": False,
                "error": f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�: {str(e)}"
            }

# Ğ¡Ğ¾Ğ·Ğ´Ğ°Ñ‘Ğ¼ Ñ�ĞºĞ·ĞµĞ¼Ğ¿Ğ»Ñ�Ñ€ Ñ�ĞµÑ€Ğ²Ğ¸Ñ�Ğ°
food_save_service = FoodSaveService()
