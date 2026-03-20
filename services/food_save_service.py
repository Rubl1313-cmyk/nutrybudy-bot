"""
Сервис сохранения питания - унифицированная логика
Избегает дублирования кода между media_handlers и enhanced_universal_handler
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy import select

from database.db import get_session
from database.models import User, FoodEntry
from utils.unit_converter import convert_to_grams

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
            meal_type: Тип приема пищи

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

                total_calories = 0

                # Сохраняем продукты
                for item in food_items:
                    # Конвертируем вес в граммы
                    quantity_str = item.get('quantity', '100 г')
                    unit = item.get('unit', 'г')

                    # Извлекаем число из строки quantity
                    try:
                        if isinstance(quantity_str, str):
                            match = re.search(r'[-+]?\d*\.?\d+', quantity_str)
                            if match:
                                quantity = float(match.group())
                            else:
                                quantity = 100.0
                        else:
                            quantity = float(quantity_str) if quantity_str else 100.0
                    except (ValueError, TypeError):
                        quantity = 100.0

                    weight_grams = convert_to_grams(item.get('name', ''), quantity, unit)

                    # Рассчитываем КБЖУ с учётом веса
                    factor = weight_grams / 100.0
                    food_calories = item.get('calories', 0) * factor
                    food_protein = item.get('protein', 0) * factor
                    food_fat = item.get('fat', 0) * factor
                    food_carbs = item.get('carbs', 0) * factor
                    total_calories += food_calories

                    # Создаем запись еды
                    food_entry = FoodEntry(
                        user_id=user.telegram_id,
                        food_name=item.get('name', 'Неизвестный продукт'),
                        calories=food_calories,
                        protein=food_protein,
                        fat=food_fat,
                        carbs=food_carbs,
                        fiber=item.get('fiber', 0),
                        sugar=item.get('sugar', 0),
                        sodium=item.get('sodium', 0),
                        meal_type=meal_type,
                        quantity=weight_grams,
                        unit='г',
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(food_entry)

                await session.commit()

                logger.info(f"[FOOD_SAVE] Сохранен прием пищи: {meal_type}, {len(food_items)} продуктов")

                return {
                    "success": True,
                    "message": f"Сохранено {len(food_items)} продуктов на {total_calories:.0f} ккал"
                }

        except Exception as e:
            logger.error(f"[FOOD_SAVE] Ошибка сохранения еды: {e}")
            return {
                "success": False,
                "error": f"Ошибка сохранения: {str(e)}"
            }

# Глобальный экземпляр сервиса
food_save_service = FoodSaveService()
