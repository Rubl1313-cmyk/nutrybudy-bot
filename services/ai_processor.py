"""
AI Processor - использует унифицированный Cloudflare AI Manager
Принимает пользовательский ввод, контекст и решает, какую модель вызвать
"""
import logging
from typing import Dict, Any, Optional
from services.cloudflare_manager import cf_manager
from database.db import get_session
from database.models import User
from sqlalchemy import select

logger = logging.getLogger(__name__)

class AIProcessor:
    """Процессор AI, который решает какую модель использовать для разных задач"""
    
    def __init__(self):
        self.ai_manager = cf_manager
        
    async def process_text_input(self, text: str, user_id: int) -> Dict[str, Any]:
        """
        Обработка текстового ввода пользователя

        Args:
            text: Текст от пользователя
            user_id: ID пользователя

        Returns:
            Dict с результатом обработки
        """
        try:
            # Получаем профиль пользователя для контекста
            user_profile = await self._get_user_profile(user_id)

            # Сначала пробуем распарсить еду
            food_result = await self.ai_manager.parse_food_text(text)
            if food_result.get("success") and food_result.get("data"):
                data = food_result["data"]
                
                # parse_food_text возвращает: ingredients, estimated_calories, confidence
                ingredients = data.get("ingredients", [])
                confidence = data.get("confidence", 0)
                
                # Проверяем уверенность распознавания
                if confidence >= 0.5 or len(ingredients) > 0:  # confidence 0-1 или есть ингредиенты
                    # Конвертируем ingredients в food_items формат
                    food_items = []
                    for ing in ingredients:
                        food_items.append({
                            "name": ing.get("name", ""),
                            "quantity": ing.get("weight_grams", 0),
                            "unit": "г",
                            "calories": 0,  # Будет рассчитано позже
                            "protein": 0,
                            "fat": 0,
                            "carbs": 0
                        })
                    
                    return {
                        "intent": "log_food",
                        "parameters": {
                            "food_items": food_items,
                            "meal_type": "main",  # По умолчанию
                            "confidence": confidence,
                            "model_used": food_result.get("model", "food_parser"),
                            "tokens_used": 0
                        },
                        "success": True
                    }

            # Если не еда, обрабатываем как общий запрос к ассистенту
            assistant_result = await self.ai_manager.get_assistant_response(
                text, context=user_profile
            )

            if assistant_result.get("success"):
                return {
                    "intent": "ai_response",
                    "parameters": {
                        "response": assistant_result.get("response", ""),
                        "model_used": assistant_result.get("model", ""),
                        "tokens_used": 0
                    },
                    "success": True
                }

            # Fallback - если не удалось определить интент
            return {
                "intent": "unknown",
                "parameters": {
                    "original_text": text,
                    "suggestion": "Попробуйте переформулировать запрос"
                },
                "success": False,
                "error": "Could not determine intent"
            }

        except Exception as e:
            logger.error(f"❌ Error processing text input: {e}")
            return {
                "intent": "error",
                "parameters": {
                    "error": str(e),
                    "original_text": text
                },
                "success": False
            }
    
    async def process_photo_input(self, image_bytes: bytes, user_id: int, caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Обработка изображения

        Args:
            image_bytes: Байты изображения
            user_id: ID пользователя
            caption: Подпись к фото

        Returns:
            Dict с результатом анализа изображения
        """
        try:
            # Анализируем фото еды
            result = await self.ai_manager.parse_food_image(image_bytes)

            if result.get("success"):
                data = result.get("analysis", {})
                ingredients = data.get("ingredients", [])

                # Рассчитываем КБЖУ на основе ингредиентов
                total_calories = 0
                total_protein = 0
                total_fat = 0
                total_carbs = 0

                # Базовая таблица калорийности для распространённых продуктов
                nutrition_db = {
                    # Белки
                    "chicken": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
                    "chicken breast": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
                    "beef": {"calories": 250, "protein": 26, "fat": 15, "carbs": 0},
                    "fish": {"calories": 206, "protein": 22, "fat": 12, "carbs": 0},
                    "salmon": {"calories": 208, "protein": 20, "fat": 13, "carbs": 0},
                    "tuna": {"calories": 144, "protein": 23, "fat": 5, "carbs": 0},
                    "egg": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
                    "eggs": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
                    # Углеводы
                    "rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
                    "pasta": {"calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
                    "potato": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
                    "potatoes": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
                    "bread": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
                    # Овощи
                    "vegetable": {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5},
                    "vegetables": {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5},
                    "tomato": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
                    "cucumber": {"calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
                    "lettuce": {"calories": 15, "protein": 1.4, "fat": 0.2, "carbs": 2.9},
                    "cabbage": {"calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 6},
                    "carrot": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
                    "broccoli": {"calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
                    # Жиры
                    "oil": {"calories": 884, "protein": 0, "fat": 100, "carbs": 0},
                    "butter": {"calories": 717, "protein": 0.9, "fat": 81, "carbs": 0.1},
                    "cheese": {"calories": 402, "protein": 25, "fat": 33, "carbs": 1.3},
                    # Фрукты
                    "fruit": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                    "apple": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                    "banana": {"calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23},
                }

                for ingredient in ingredients:
                    name = ingredient.get("name", "").lower()
                    weight = ingredient.get("weight_grams", 0)

                    # Ищем продукт в базе
                    nutrition = None
                    for key, value in nutrition_db.items():
                        if key in name:
                            nutrition = value
                            break

                    # Если не нашли, используем средние значения
                    if not nutrition:
                        ing_type = ingredient.get("type", "")
                        if "protein" in ing_type:
                            nutrition = {"calories": 150, "protein": 25, "fat": 5, "carbs": 0}
                        elif "carb" in ing_type:
                            nutrition = {"calories": 120, "protein": 3, "fat": 0.5, "carbs": 25}
                        elif "vegetable" in ing_type:
                            nutrition = {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5}
                        elif "fat" in ing_type:
                            nutrition = {"calories": 800, "protein": 0, "fat": 90, "carbs": 0}
                        else:
                            nutrition = {"calories": 100, "protein": 5, "fat": 3, "carbs": 15}

                    # Рассчитываем КБЖУ для этого ингредиента
                    total_calories += (nutrition["calories"] * weight) / 100
                    total_protein += (nutrition["protein"] * weight) / 100
                    total_fat += (nutrition["fat"] * weight) / 100
                    total_carbs += (nutrition["carbs"] * weight) / 100

                # Определяем meal_type из category
                category = data.get("category", "main")
                meal_type_map = {
                    "breakfast": "breakfast",
                    "lunch": "main",
                    "dinner": "main",
                    "main": "main",
                    "salad": "snack",
                    "side": "side",
                    "snack": "snack",
                    "dessert": "dessert",
                    "soup": "main",
                    "drink": "drink"
                }
                meal_type = meal_type_map.get(category, "main")

                # Форматируем результат
                return {
                    "intent": "log_food_from_photo",
                    "parameters": {
                        "dish_name": data.get("dish_name", "Неизвестное блюдо"),
                        "ingredients": ingredients,
                        "estimated_total_calories": total_calories,
                        "estimated_total_protein": total_protein,
                        "estimated_total_fat": total_fat,
                        "estimated_total_carbs": total_carbs,
                        "meal_type": meal_type,
                        "confidence": data.get("confidence", 0),
                        "model_used": result.get("model", "vision"),
                        "tokens_used": 0
                    },
                    "success": True
                }

            # Другие контексты для фото можно добавить здесь
            return {
                "intent": "unknown",
                "parameters": {
                    "context": "food_logging",
                    "suggestion": "Не удалось распознать еду на фото"
                },
                "success": False
            }

        except Exception as e:
            logger.error(f"❌ Error processing photo input: {e}")
            return {
                "intent": "error",
                "parameters": {
                    "error": str(e),
                    "context": "food_logging"
                },
                "success": False
            }
    
    async def _get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Получает профиль пользователя для контекста"""
        try:
            async with get_session() as session:
                user_result = await session.execute(select(User).where(User.telegram_id == user_id))
                user = user_result.scalar_one_or_none()
                
                if user:
                    return {
                        "id": user.id,
                        "first_name": user.first_name,
                        "age": user.age,
                        "gender": user.gender,
                        "weight_kg": user.weight,
                        "height_cm": user.height,
                        "goal": user.goal,
                        "activity_level": user.activity_level,
                        "daily_calorie_goal": user.daily_calorie_goal,
                        "daily_protein_goal": user.daily_protein_goal,
                        "daily_fat_goal": user.daily_fat_goal,
                        "daily_carbs_goal": user.daily_carbs_goal,
                        "daily_water_goal": user.daily_water_goal,
                        "daily_steps_goal": user.daily_steps_goal
                    }
                return None
        except Exception as e:
            logger.error(f"❌ Error getting user profile: {e}")
            return None
    
    def format_food_result(self, food_data: Dict) -> Dict:
        """
        Форматирует результат распознавания еды в удобный формат
        
        Args:
            food_data: Данные от AI модели
            
        Returns:
            Отформатированный словарь
        """
        food_items = food_data.get("food_items", [])
        
        # Суммируем калории и БЖУ если есть
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        
        for item in food_items:
            # Расчет калорийности на основе веса
            weight = item.get("quantity", 0)
            calories_per_100g = item.get("calories_per_100g", 0)
            protein_per_100g = item.get("protein_per_100g", 0)
            fat_per_100g = item.get("fat_per_100g", 0)
            carbs_per_100g = item.get("carbs_per_100g", 0)
            
            total_calories += (weight * calories_per_100g) / 100
            total_protein += (weight * protein_per_100g) / 100
            total_fat += (weight * fat_per_100g) / 100
            total_carbs += (weight * carbs_per_100g) / 100
        
        # Формируем описание
        description = ", ".join([f"{item.get('quantity', 0)}{item.get('unit', 'г')} {item.get('name')}" for item in food_items])
        
        return {
            "description": description,
            "total_calories": round(total_calories, 1),
            "total_protein": round(total_protein, 1),
            "total_fat": round(total_fat, 1),
            "total_carbs": round(total_carbs, 1),
            "meal_type": food_data.get("meal_type", "unknown"),
            "confidence": food_data.get("total_confidence", 0),
            "items_count": len(food_items)
        }
    
    def format_photo_result(self, photo_data: Dict) -> Dict:
        """
        Форматирует результат анализа фото
        
        Args:
            photo_data: Данные от AI модели
            
        Returns:
            Отформатированный словарь
        """
        ingredients = photo_data.get("ingredients", [])
        
        # Формируем описание из ингредиентов
        description = photo_data.get("dish_name", "Неизвестное блюдо")
        if ingredients:
            ingredient_list = [f"{ing.get('weight', 0)}г {ing.get('name')}" for ing in ingredients[:5]]
            description += f" ({', '.join(ingredient_list)})"
        
        return {
            "description": description,
            "dish_name": photo_data.get("dish_name"),
            "ingredients": ingredients,
            "calories": photo_data.get("estimated_total_calories", 0),
            "protein": photo_data.get("estimated_total_protein", 0),
            "fat": photo_data.get("estimated_total_fat", 0),
            "carbs": photo_data.get("estimated_total_carbs", 0),
            "meal_type": photo_data.get("meal_type", "unknown"),
            "confidence": photo_data.get("confidence", 0)
        }

# Глобальный экземпляр
ai_processor = AIProcessor()
