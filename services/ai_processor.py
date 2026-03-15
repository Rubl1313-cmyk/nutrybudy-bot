"""
AI Processor - Центральный процессор на реальных AI моделях
Использует GLM-4.7-Flash для парсинга, Llama Vision для фото
"""
import logging
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from services.ai_model_manager import ai_manager
from database.db import get_session
from database.models import User
from sqlalchemy import select

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.ai_manager = ai_manager
    
    async def process_text_input(
        self,
        text: str,
        user_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Обработка текста через GLM-4.7-Flash
        """
        if not text or not text.strip():
            return {"intent": "error", "parameters": {}, "error": "Empty input"}
        
        try:
            # Используем GLM-4.7-Flash для парсинга
            result = await self.ai_manager.parse_food(text, user_context)
            
            if not result["success"]:
                logger.error(f"❌ AI parsing error: {result.get('error')}")
                return {"intent": "error", "parameters": {}, "error": result.get("error")}
            
            # Извлекаем спарсенные данные
            parsed_data = result.get("parsed_data", {})
            intent = parsed_data.get("intent", "unknown")
            confidence = parsed_data.get("confidence", 0)
            extracted_data = parsed_data.get("extracted_data", {})
            
            logger.info(f"🧠 AI parsed: {intent} (confidence: {confidence:.2f})")
            
            # Конвертируем в единый формат
            if intent == "food":
                return await self._process_food_intent(extracted_data, text)
            elif intent == "water":
                return await self._process_water_intent(extracted_data, text)
            elif intent == "steps":
                return await self._process_steps_intent(extracted_data, text)
            elif intent == "activity":
                return await self._process_activity_intent(extracted_data, text)
            else:
                # Для неизвестных намерений используем AI ассистента
                return await self._process_with_assistant(text, user_context)
                
        except Exception as e:
            logger.exception("❌ Error in AI text processing")
            return {"intent": "error", "parameters": {}, "error": str(e)}
    
    async def process_photo_input(
        self,
        image_bytes: bytes,
        user_context: Optional[Dict[str, Any]] = None,
        accompanying_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Обработка фото через Llama 3.2 Vision
        """
        try:
            logger.info("📸 Processing photo with Llama Vision")
            
            # Формируем промпт для vision
            prompt = "Опиши еду на этом фото. Определи блюдо, ингредиенты и примерный вес."
            if accompanying_text:
                prompt += f"\nДополнительно от пользователя: {accompanying_text}"
            
            # Вызываем Llama 3.2 Vision
            result = await self.ai_manager.analyze_image(image_bytes, prompt)
            
            if not result["success"]:
                logger.error(f"❌ Vision error: {result.get('error')}")
                return {"intent": "error", "parameters": {}, "error": result.get("error")}
            
            # Извлекаем данные
            parsed_data = result.get("parsed_data", {})
            dish_name = parsed_data.get("dish_name", "Неизвестное блюдо")
            ingredients = parsed_data.get("ingredients", [])
            nutrition = parsed_data.get("nutrition_estimate", {})
            confidence = parsed_data.get("confidence", 0)
            
            logger.info(f"🍽️ Vision recognized: {dish_name} (confidence: {confidence:.2f})")
            
            # Конвертируем в формат для сохранения
            return {
                "intent": "log_food",
                "parameters": {
                    "description": dish_name,
                    "ingredients": ingredients,
                    "calories": nutrition.get("calories", 0),
                    "protein": nutrition.get("protein", 0),
                    "fat": nutrition.get("fat", 0),
                    "carbs": nutrition.get("carbs", 0),
                    "confidence": confidence,
                    "raw_ai_response": result["response"]
                }
            }
            
        except Exception as e:
            logger.exception("❌ Error in AI photo processing")
            return {"intent": "error", "parameters": {}, "error": str(e)}
    
    async def _process_food_intent(self, extracted_data: Dict, original_text: str) -> Dict[str, Any]:
        """Обработка намерения еды"""
        food_items = extracted_data.get("food_items", [])
        
        if not food_items:
            # Если AI не извлек продукты, используем оригинальный текст
            return {
                "intent": "log_food",
                "parameters": {
                    "description": original_text,
                    "calories": 0,
                    "protein": 0,
                    "fat": 0,
                    "carbs": 0
                }
            }
        
        # Рассчитываем общие КБЖУ
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        
        food_descriptions = []
        for item in food_items:
            name = item.get("name", "Неизвестно")
            weight = item.get("weight_g", 100)
            confidence = item.get("confidence", 0.5)
            
            # Приблизительный расчет КБЖУ (можно улучшить с базой данных)
            calories = weight * 2.0  # ~2 ккал/г средняя
            protein = weight * 0.15  # ~15% белка
            fat = weight * 0.08     # ~8% жира
            carbs = weight * 0.25   # ~25% углеводов
            
            total_calories += calories
            total_protein += protein
            total_fat += fat
            total_carbs += carbs
            
            food_descriptions.append(f"{name} ({weight}г)")
        
        description = ", ".join(food_descriptions) if food_descriptions else original_text
        
        return {
            "intent": "log_food",
            "parameters": {
                "description": description,
                "calories": total_calories,
                "protein": total_protein,
                "fat": total_fat,
                "carbs": total_carbs,
                "items": food_items
            }
        }
    
    async def _process_water_intent(self, extracted_data: Dict, original_text: str) -> Dict[str, Any]:
        """Обработка намерения воды"""
        amount = extracted_data.get("water_ml")
        
        if not amount:
            # Пробуем извлечь из текста
            amount = self._parse_water_amount(original_text)
        
        return {
            "intent": "log_water",
            "parameters": {
                "amount_ml": amount or 0,
                "description": f"{amount or 0}мл воды"
            }
        }
    
    async def _process_steps_intent(self, extracted_data: Dict, original_text: str) -> Dict[str, Any]:
        """Обработка намерения шагов"""
        steps = extracted_data.get("steps")
        
        if not steps:
            # Пробуем извлечь из текста
            steps = self._parse_steps_amount(original_text)
        
        return {
            "intent": "log_steps",
            "parameters": {
                "count": steps or 0,
                "description": f"{steps or 0} шагов"
            }
        }
    
    async def _process_activity_intent(self, extracted_data: Dict, original_text: str) -> Dict[str, Any]:
        """Обработка намерения активности"""
        activity_type = extracted_data.get("activity_type", "другое")
        duration = extracted_data.get("duration_min")
        
        if not duration:
            duration = self._parse_duration(original_text)
        
        return {
            "intent": "log_activity",
            "parameters": {
                "type": activity_type,
                "duration_min": duration or 0,
                "description": f"{activity_type} - {duration or 0} мин"
            }
        }
    
    async def _process_with_assistant(self, text: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Обработка через AI ассистента"""
        try:
            result = await self.ai_manager.ai_assistant(text, user_context)
            
            if result["success"]:
                return {
                    "intent": "ai_response",
                    "parameters": {
                        "response": result["response"],
                        "description": "AI ассистент"
                    }
                }
            else:
                return {"intent": "error", "parameters": {}, "error": result.get("error")}
                
        except Exception as e:
            logger.error(f"❌ Assistant error: {e}")
            return {"intent": "error", "parameters": {}, "error": str(e)}
    
    def _parse_water_amount(self, text: str) -> Optional[int]:
        """Парсинг количества воды"""
        patterns = [
            r'(\d+)\s*мл',
            r'(\d+)\s*ml',
            r'(\d+)\s*стакан(?:а|ов)?',
            r'выпил\s+(\d+)',
            r'попил\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount = int(match.group(1))
                if "стакан" in pattern:
                    amount *= 250
                return amount
        return None
    
    def _parse_steps_amount(self, text: str) -> Optional[int]:
        """Парсинг количества шагов"""
        patterns = [
            r'(\d+)\s*шаг(?:ов|а)?',
            r'прош(?:ел|ла)?\s+(\d+)\s*шаг',
            r'сделал\s+(\d+)\s*шаг'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return None
    
    def _parse_duration(self, text: str) -> Optional[int]:
        """Парсинг длительности"""
        patterns = [
            r'(\d+)\s*мин(?:ут)?',
            r'(\d+)\s*час(?:ов|а)?',
            r'(\d+)\s*ч'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                duration = int(match.group(1))
                if "час" in pattern or "ч" in pattern:
                    duration *= 60
                return duration
        return None

# Глобальный экземпляр
ai_processor = AIProcessor()
