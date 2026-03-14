"""
🍽️ Сервис сохранения питания - унифицированная логика
Избегает дублирования кода между media_handlers и enhanced_universal_handler
"""

import logging
from typing import Dict, List, Any
from sqlalchemy import select
from database.db import get_session
from database.models import User, Meal, FoodItem
from utils.unit_converter import convert_to_grams
from datetime import datetime

logger = logging.getLogger(__name__)

class FoodSaveService:
    """Унифицированный сервис сохранения еды"""
    
    @staticmethod
    async def save_food_to_db(
        user_id: int,
        food_items: List[Dict[str, Any]],
        meal_type: str = "main"
    ) -> Dict[str, Any]:
        """
        Сохраняет еду в базу данных
        
        Args:
            user_id: Telegram ID пользователя
            food_items: Список продуктов от AI
            meal_type: Тип приёма пищи
            
        Returns:
            Dict с результатом сохранения
        """
        try:
            async with get_session() as session:
                # Получаем пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    return {
                        "success": False,
                        "error": "Пользователь не найден"
                    }
                
                # Создаём приём пищи
                meal = Meal(
                    user_id=user.id,
                    meal_type=meal_type,
                    datetime=datetime.now()
                )
                session.add(meal)
                await session.flush()  # Получаем ID meal
                
                total_calories = 0
                total_protein = 0
                total_fat = 0
                total_carbs = 0
                
                # Сохраняем продукты
                for item in food_items:
                    # Конвертируем вес в граммы
                    quantity = item.get('quantity', '100 г')
                    unit = item.get('unit', 'г')
                    weight_grams = convert_to_grams(item.get('name', ''), quantity, unit)
                    
                    # Рассчитываем КБЖУ с учётом веса
                    factor = weight_grams / 100.0
                    food_calories = item.get('calories', 0) * factor
                    food_protein = item.get('protein', 0) * factor
                    food_fat = item.get('fat', 0) * factor
                    food_carbs = item.get('carbs', 0) * factor
                    
                    # Создаём FoodItem с пересчитанными значениями
                    food_item = FoodItem(
                        meal_id=meal.id,
                        name=item.get('name', 'Неизвестный продукт'),
                        calories=food_calories,
                        protein=food_protein,
                        fat=food_fat,
                        carbs=food_carbs,
                        weight_grams=weight_grams
                    )
                    session.add(food_item)
                    
                    # Суммируем итоговые значения
                    total_calories += food_calories
                    total_protein += food_protein
                    total_fat += food_fat
                    total_carbs += food_carbs
                
                # Обновляем итоговые значения в приёме пищи
                meal.calories = total_calories
                meal.protein = total_protein
                meal.fat = total_fat
                meal.carbs = total_carbs
                
                await session.commit()
                
                return {
                    "success": True,
                    "message": f"Сохранено {len(food_items)} продуктов",
                    "total_calories": total_calories,
                    "total_protein": total_protein,
                    "total_fat": total_fat,
                    "total_carbs": total_carbs
                }
                
        except Exception as e:
            logger.error(f"Error saving food: {e}")
            return {
                "success": False,
                "error": f"Ошибка сохранения: {str(e)}"
            }

# Создаём экземпляр сервиса
food_save_service = FoodSaveService()
