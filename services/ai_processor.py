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
                # Проверяем уверенность распознавания
                confidence = data.get("total_confidence", 0)
                if confidence >= 70:
                    return {
                        "intent": "log_food",
                        "parameters": {
                            "food_items": data.get("food_items", []),
                            "meal_type": data.get("meal_type", "unknown"),
                            "confidence": confidence,
                            "model_used": food_result["model_used"],
                            "tokens_used": food_result["tokens_used"]
                        },
                        "success": True
                    }
                elif data.get("needs_clarification"):
                    return {
                        "intent": "clarify",
                        "parameters": {
                            "question": data.get("clarification", "Уточните, пожалуйста."),
                            "model_used": food_result["model_used"],
                            "tokens_used": food_result["tokens_used"]
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
                
                # Форматируем результат для удобства использования
                return {
                    "intent": "log_food_from_photo",
                    "parameters": {
                        "dish_name": data.get("dish_name", "Неизвестное блюдо"),
                        "ingredients": data.get("ingredients", []),
                        "estimated_total_calories": data.get("estimated_total_calories", 0),
                        "estimated_total_protein": data.get("estimated_total_protein", 0),
                        "estimated_total_fat": data.get("estimated_total_fat", 0),
                        "estimated_total_carbs": data.get("estimated_total_carbs", 0),
                        "meal_type": data.get("meal_type", "unknown"),
                        "confidence": data.get("confidence", 0),
                        "model_used": result["model_used"],
                        "tokens_used": result["tokens_used"]
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
