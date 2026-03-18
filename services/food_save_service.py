"""
Сервис сохранения питания - унифицированная логика
Избегает дублирования кода между media_handlers и enhanced_universal_handler
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from database.db import get_session
from database.models import User, Meal, FoodItem
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
                
                # Создаем прием пищи
                meal = Meal(
                    user_id=user.id,
                    meal_type=meal_type,
                    date=datetime.now(timezone.utc).date(),
                    created_at=datetime.now(timezone.utc)
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
                    quantity_str = item.get('quantity', '100 г')
                    unit = item.get('unit', 'г')
                    
                    # Извлекаем число из строки quantity
                    try:
                        if isinstance(quantity_str, str):
                            # Ищем число в строке
                            match = re.search(r'[-+]?\d*\.?\d+', quantity_str)
                            if match:
                                quantity = float(match.group())
                            else:
                                quantity = 100.0  # По умолчанию
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
                    
                    # Создаем FoodItem с пересчитанными значениями
                    food_item = FoodItem(
                        meal_id=meal.id,
                        name=item.get('name', 'Неизвестный продукт'),
                        quantity=weight_grams,
                        unit='г',
                        calories=food_calories,
                        protein=food_protein,
                        fat=food_fat,
                        carbs=food_carbs,
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(food_item)
                    
                    # Накапливаем totals
                    total_calories += food_calories
                    total_protein += food_protein
                    total_fat += food_fat
                    total_carbs += food_carbs
                
                # Обновляем totals в meal
                meal.total_calories = total_calories
                meal.total_protein = total_protein
                meal.total_fat = total_fat
                meal.total_carbs = total_carbs
                
                # Сохраняем всё в базе
                await session.commit()
                
                logger.info(f"[FOOD_SAVE] Сохранен прием пищи: {meal_type}, {len(food_items)} продуктов, {total_calories:.0f} ккал")
                
                return {
                    "success": True,
                    "meal_id": meal.id,
                    "total_calories": total_calories,
                    "total_protein": total_protein,
                    "total_fat": total_fat,
                    "total_carbs": total_carbs,
                    "items_count": len(food_items)
                }
                
        except Exception as e:
            logger.error(f"[FOOD_SAVE] Ошибка сохранения еды: {e}")
            return {
                "success": False,
                "error": f"Ошибка сохранения: {str(e)}"
            }
    
    @staticmethod
    async def update_meal_description(
        meal_id: int,
        description: str
    ) -> Dict[str, Any]:
        """
        Обновляет описание приема пищи
        
        Args:
            meal_id: ID приема пищи
            description: Новое описание
            
        Returns:
            Dict с результатом обновления
        """
        try:
            async with get_session() as session:
                # Получаем прием пищи
                meal_result = await session.execute(
                    select(Meal).where(Meal.id == meal_id)
                )
                meal = meal_result.scalar_one_or_none()
                
                if not meal:
                    return {
                        "success": False,
                        "error": "Прием пищи не найден"
                    }
                
                # Обновляем описание
                meal.ai_description = description
                await session.commit()
                
                logger.info(f"[FOOD_SAVE] Обновлено описание приема пищи {meal_id}")
                
                return {
                    "success": True,
                    "meal_id": meal_id
                }
                
        except Exception as e:
            logger.error(f"[FOOD_SAVE] Ошибка обновления описания: {e}")
            return {
                "success": False,
                "error": f"Ошибка обновления: {str(e)}"
            }
    
    @staticmethod
    async def delete_meal(meal_id: int) -> Dict[str, Any]:
        """
        Удаляет прием пищи и все связанные продукты
        
        Args:
            meal_id: ID приема пищи
            
        Returns:
            Dict с результатом удаления
        """
        try:
            async with get_session() as session:
                # Получаем прием пищи
                meal_result = await session.execute(
                    select(Meal).where(Meal.id == meal_id)
                )
                meal = meal_result.scalar_one_or_none()
                
                if not meal:
                    return {
                        "success": False,
                        "error": "Прием пищи не найден"
                    }
                
                # Удаляем все связанные FoodItem (каскадное удаление должно работать, но для надежности)
                await session.execute(
                    delete(FoodItem).where(FoodItem.meal_id == meal_id)
                )
                
                # Удаляем сам прием пищи
                await session.delete(meal)
                await session.commit()
                
                logger.info(f"[FOOD_SAVE] Удален прием пищи {meal_id}")
                
                return {
                    "success": True,
                    "meal_id": meal_id
                }
                
        except Exception as e:
            logger.error(f"[FOOD_SAVE] Ошибка удаления приема пищи: {e}")
            return {
                "success": False,
                "error": f"Ошибка удаления: {str(e)}"
            }
    
    @staticmethod
    async def get_meal_details(meal_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает подробную информацию о приеме пищи
        
        Args:
            meal_id: ID приема пищи
            
        Returns:
            Dict с деталями приема пищи или None
        """
        try:
            async with get_session() as session:
                # Получаем прием пищи с продуктами
                result = await session.execute(
                    select(Meal, FoodItem)
                    .join(FoodItem, Meal.id == FoodItem.meal_id)
                    .where(Meal.id == meal_id)
                )
                
                records = result.all()
                
                if not records:
                    return None
                
                # Берем первую запись для данных Meal
                meal = records[0][0]
                
                # Собираем все продукты
                food_items = []
                for meal_record, food_item in records:
                    food_items.append({
                        'name': food_item.name,
                        'quantity': food_item.quantity,
                        'unit': food_item.unit,
                        'calories': food_item.calories,
                        'protein': food_item.protein,
                        'fat': food_item.fat,
                        'carbs': food_item.carbs
                    })
                
                return {
                    'meal_id': meal.id,
                    'meal_type': meal.meal_type,
                    'date': meal.date,
                    'created_at': meal.created_at,
                    'ai_description': meal.ai_description,
                    'total_calories': meal.total_calories,
                    'total_protein': meal.total_protein,
                    'total_fat': meal.total_fat,
                    'total_carbs': meal.total_carbs,
                    'food_items': food_items
                }
                
        except Exception as e:
            logger.error(f"[FOOD_SAVE] Ошибка получения деталей приема пищи: {e}")
            return None
    
    @staticmethod
    async def get_user_meals(
        user_id: int,
        limit: int = 50,
        date_from: Optional[datetime.date] = None,
        date_to: Optional[datetime.date] = None
    ) -> List[Dict[str, Any]]:
        """
        Получает приемы пищи пользователя
        
        Args:
            user_id: Telegram ID пользователя
            limit: Лимит записей
            date_from: Начальная дата (опционально)
            date_to: Конечная дата (опционально)
            
        Returns:
            Список приемов пищи
        """
        try:
            async with get_session() as session:
                # Базовый запрос
                query = select(Meal).where(Meal.user_id == user_id)
                
                # Добавляем фильтры по датам
                if date_from:
                    query = query.where(Meal.date >= date_from)
                if date_to:
                    query = query.where(Meal.date <= date_to)
                
                # Добавляем сортировку и лимит
                query = query.order_by(Meal.date.desc(), Meal.created_at.desc()).limit(limit)
                
                result = await session.execute(query)
                meals = result.scalars().all()
                
                # Формируем результат
                meals_list = []
                for meal in meals:
                    meals_list.append({
                        'meal_id': meal.id,
                        'meal_type': meal.meal_type,
                        'date': meal.date,
                        'created_at': meal.created_at,
                        'ai_description': meal.ai_description,
                        'total_calories': meal.total_calories,
                        'total_protein': meal.total_protein,
                        'total_fat': meal.total_fat,
                        'total_carbs': meal.total_carbs
                    })
                
                return meals_list
                
        except Exception as e:
            logger.error(f"[FOOD_SAVE] Ошибка получения приемов пищи: {e}")
            return []
    
    @staticmethod
    async def update_meal_type(meal_id: int, new_meal_type: str) -> Dict[str, Any]:
        """
        Обновляет тип приема пищи
        
        Args:
            meal_id: ID приема пищи
            new_meal_type: Новый тип
            
        Returns:
            Dict с результатом обновления
        """
        try:
            async with get_session() as session:
                # Получаем прием пищи
                meal_result = await session.execute(
                    select(Meal).where(Meal.id == meal_id)
                )
                meal = meal_result.scalar_one_or_none()
                
                if not meal:
                    return {
                        "success": False,
                        "error": "Прием пищи не найден"
                    }
                
                # Обновляем тип
                meal.meal_type = new_meal_type
                await session.commit()
                
                logger.info(f"[FOOD_SAVE] Обновлен тип приема пищи {meal_id} на {new_meal_type}")
                
                return {
                    "success": True,
                    "meal_id": meal_id,
                    "old_type": meal.meal_type,
                    "new_type": new_meal_type
                }
                
        except Exception as e:
            logger.error(f"[FOOD_SAVE] Ошибка обновления типа приема пищи: {e}")
            return {
                "success": False,
                "error": f"Ошибка обновления: {str(e)}"
            }

# Глобальный экземпляр сервиса
food_save_service = FoodSaveService()
