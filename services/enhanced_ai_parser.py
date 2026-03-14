import logging
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from services.ai_engine_manager import ai
from database.db import get_session
from database.models import User, Meal, WeightEntry, Activity

logger = logging.getLogger(__name__)

class EnhancedAIParser:
    """Улучшенный AI парсер с многократными попытками и валидацией"""
    
    def __init__(self):
        self.max_retries = 3
        self.confidence_threshold = 70
    
    async def parse_food_enhanced(
        self, 
        text: str, 
        context: Dict = None, 
        history: List[str] = None
    ) -> Dict:
        """
        Улучшенный парсер еды с AI
        """
        prompt = f"""
        Ты - умный ассистент NutriBuddy. Проанализируй текст о еде с максимальной точностью.
        
        📝 ТЕКСТ: "{text}"
        
        📚 КОНТЕКСТ:
        {self._format_context(context)}
        
        📜 ИСТОРИЯ ДИАЛОГА:
        {self._format_history(history)}
        
        🎯 ПРАВИЛА ПАРСИНГА:
        
        1. **Продукты:**
           - Извлеки все упомянутые продукты
           - Определи количество и единицы измерения
           - Учитывай синонимы и разговорные названия
           - Примеры: "курица" → "куриное филе", "картошка" → "картофель"
           
        2. **Количество:**
           - Определи точный вес/объем
           - При отсутствии укажи стандартные порции:
           * Мясо/рыба: 100-200г
           * Гарниры: 150-250г
           * Супы: 200-300мл
           * Фрукты: 1шт = 100-150г
           
        3. **Тип приема пищи:**
           - Определи по времени и контексту:
           * Утро (6-11): завтрак
           * День (11-16): обед
           * Вечер (16-22): ужин
           * Другое: перекус
           
        4. **Уверенность:**
           - Оцени точность распознавания 0-100%
           - Учитывай ясность описания
        
        ВАЖНО: Верни ТОЛЬКО JSON в формате:
        {{
            "food_items": [
                {{
                    "name": "название продукта",
                    "quantity": количество,
                    "unit": "г|мл|шт|стакан|ложка",
                    "calories": калории_на_100г,
                    "protein": белки_на_100г,
                    "fat": жиры_на_100г,
                    "carbs": углеводы_на_100г
                }}
            ],
            "meal_type": "завтрак|обед|ужин|перекус",
            "total_confidence": 0-100,
            "needs_clarification": true/false,
            "clarification": "уточняющий вопрос если нужно"
        }}
        
        Примеры:
        {{"text": "Я съел яблоко"}} -> {{"food_items": [{"name": "яблоко", "quantity": 1, "unit": "шт"}], "meal_type": "завтрак", "total_confidence": 80}}
        """
        
        try:
            result = await ai.process_text(prompt, task_type="json", system_prompt="You are NutriBuddy assistant. Return JSON only.")
            
            logger.info(f"🧠 Enhanced AI food result success: {result.get('success', False)}")
            
            if result.get("success"):
                response_data = result.get("data", {})
                
                # Получаем текстовый контент из разных форматов ответа
                if isinstance(response_data, dict):
                    if "content" in response_data:
                        # Если content это dict, берем его как строку
                        content = response_data.get("content")
                        if isinstance(content, dict):
                            # Если content это dict с JSON структурой, используем его напрямую
                            if "intent" in content or "food_items" in content:
                                response_text = json.dumps(content)  # Конвертируем в JSON строку
                            else:
                                response_text = str(content)
                        else:
                            response_text = str(content)
                    else:
                        response_text = str(response_data)
                else:
                    response_text = str(response_data)
                
                # Пробуем извлечь JSON из ответа
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    
                    # Валидация и обогащение данных
                    validated_data = await self._validate_food_data(parsed_data)
                    
                    logger.info(f"🧠 Enhanced AI food: {len(validated_data.get('food_items', []))} items (confidence: {validated_data.get('total_confidence', 0)}%)")
                    return validated_data
            
            return self._fallback_food(text)
            
        except Exception as e:
            logger.error(f"🧠 Enhanced AI food parser error: {e}")
            # Возвращаем ошибку вместо fallback - заставляем использовать AI
            return {
                "food_items": [],
                "meal_type": "неизвестно",
                "total_confidence": 0,
                "needs_clarification": True,
                "error": "AI parsing failed"
            }
    
    async def parse_water_enhanced(self, text: str) -> Dict:
        """Улучшенный парсер воды"""
        prompt = f"""
        Ты - умный ассистент NutriBuddy. Проанализируй текст о воде и определи точное количество.

        Текст: "{text}"

        ВАЖНО: Верни ТОЛЬКО JSON в формате:
        {{
            "amount_ml": количество_в_мл,
            "unit": "мл",
            "confidence": 0-100
        }}

        ПРИМЕРЫ:
        - "выпил большую кружку чая" -> {{"amount_ml": 300, "unit": "мл", "confidence": 85}}
        - "выпил стакан воды" -> {{"amount_ml": 250, "unit": "мл", "confidence": 90}}
        - "выпил полтора литра воды" -> {{"amount_ml": 1500, "unit": "мл", "confidence": 95}}
        - "выпил бутылку воды" -> {{"amount_ml": 500, "unit": "мл", "confidence": 90}}

        Анализируй контекст: "большую кружку" = 250-350мл, "стакан" = 200-250мл, "бутылка" = 500мл.
        """
        
        try:
            result = await ai.process_text(prompt, task_type="json", system_prompt="You are NutriBuddy assistant. Return JSON only.")
            
            if result.get("success"):
                response_data = result.get("data", {})
                
                # Получаем текстовый контент
                if isinstance(response_data, dict) and "content" in response_data:
                    response_text = str(response_data.get("content"))
                else:
                    response_text = str(response_data)
                
                # Извлекаем JSON
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    
                    amount = parsed_data.get("amount_ml", 0)
                    confidence = parsed_data.get("confidence", 0)
                    
                    logger.info(f"🧠 Enhanced AI water: {amount} мл (confidence: {confidence}%)")
                    return parsed_data
            
            return self._fallback_water(text)
            
        except Exception as e:
            logger.error(f"🧠 Enhanced AI water parser error: {e}")
            # Возвращаем ошибку вместо fallback - заставляем использовать AI
            return {
                "amount_ml": 0,
                "unit": "мл",
                "confidence": 0,
                "needs_clarification": True,
                "error": "AI parsing failed"
            }
    
    async def parse_activity_enhanced(self, text: str) -> Dict:
        """Улучшенный парсер активности"""
        prompt = f"""
        Ты - умный ассистент NutriBuddy. Проанализируй текст о физической активности.

        Текст: "{text}"

        ВАЖНО: Верни ТОЛЬКО JSON в формате:
        {{
            "activity_type": "бег|ходьба|тренировка|плавание|велосипед",
            "duration_minutes": продолжительность_в_минутах,
            "intensity": "низкая|средняя|высокая",
            "calories_estimate": примерные_калории,
            "confidence": 0-100
        }}

        ПРИМЕРЫ:
        - "бегал 30 минут" -> {{"activity_type": "бег", "duration_minutes": 30, "intensity": "средняя", "calories_estimate": 300, "confidence": 90}}
        - "ходил пешком час" -> {{"activity_type": "ходьба", "duration_minutes": 60, "intensity": "низкая", "calories_estimate": 200, "confidence": 85}}
        - "был в спортзале 45 минут" -> {{"activity_type": "тренировка", "duration_minutes": 45, "intensity": "высокая", "calories_estimate": 400, "confidence": 80}}
        """
        
        try:
            result = await ai.process_text(prompt, task_type="json", system_prompt="You are NutriBuddy assistant. Return JSON only.")
            
            if result.get("success"):
                response_data = result.get("data", {})
                
                # Получаем текстовый контент
                if isinstance(response_data, dict) and "content" in response_data:
                    response_text = str(response_data.get("content"))
                else:
                    response_text = str(response_data)
                
                # Извлекаем JSON
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    
                    activity_type = parsed_data.get("activity_type", "неизвестно")
                    confidence = parsed_data.get("confidence", 0)
                    
                    logger.info(f"🧠 Enhanced AI activity: {activity_type} (confidence: {confidence}%)")
                    return parsed_data
            
            return self._fallback_activity(text)
            
        except Exception as e:
            logger.error(f"🧠 Enhanced AI activity parser error: {e}")
            # Возвращаем ошибку вместо fallback - заставляем использовать AI
            return {
                "activity_type": "неизвестно",
                "duration_minutes": 0,
                "intensity": "неизвестно",
                "confidence": 0,
                "needs_clarification": True,
                "error": "AI parsing failed"
            }
    
    async def analyze_intent(self, text: str, context: Dict = None) -> Dict:
        """Анализ намерения (совместимость с тестами)"""
        return await self.classify_intent_enhanced(text, context)
    
    async def validate_input_semantic(self, input_type: str, value: Any) -> Dict:
        """Семантическая валидация ввода"""
        if input_type == 'weight':
            # Проверяем реалистичность веса
            if isinstance(value, (int, float)):
                if value < 30 or value > 300:
                    return {"realistic": False, "reason": "Вес вне реалистичного диапазона"}
                else:
                    return {"realistic": True, "reason": "Вес в нормальном диапазоне"}
            else:
                return {"realistic": False, "reason": "Некорректный тип данных"}
        else:
            return {"realistic": True, "reason": "Тип не требует валидации"}
    
    async def classify_intent_enhanced(
        self, 
        text: str, 
        context: Dict = None, 
        history: List[str] = None
    ) -> Dict:
        """Улучшенный классификатор намерений"""
        prompt = f"""
        Ты - умный ассистент NutriBuddy. Проанализируй намерение пользователя с максимальной точностью.
        
        📝 ТЕКСТ: "{text}"
        
        📚 КОНТЕКСТ:
        {self._format_context(context)}
        
        📜 ИСТОРИЯ ДИАЛОГА:
        {self._format_history(history)}
        
        🎯 ВОЗМОЖНЫЕ НАМЕРЕНИЯ:
        - food: запись еды/продуктов
        - water: запись воды
        - activity: запись физической активности
        - weight: запись веса
        - steps: запись шагов
        - question: вопрос/помощь
        - other: другое
        
        ВАЖНО: Верни ТОЛЬКО JSON в формате:
        {{
            "intent": "food|water|activity|weight|steps|question|other",
            "confidence": 0-100,
            "entities": {{
                "food_items": [...],
                "amount_ml": число,
                "activity_type": "тип",
                "duration_minutes": число
            }},
            "response": "текст ответа пользователю",
            "actions": [
                {{
                    "type": "save_food|save_water|save_activity|save_steps|save_weight|answer_question|show_help",
                    "data": {...}
                }}
            ],
            "needs_clarification": true/false,
            "clarification": "уточняющий вопрос если нужно"
        }}
        """
        
        try:
            result = await ai.process_text(prompt, task_type="json", system_prompt="You are NutriBuddy assistant. Return JSON only.")
            
            if result.get("success"):
                response_data = result.get("data", {})
                
                # Получаем текстовый контент
                if isinstance(response_data, dict) and "content" in response_data:
                    response_text = str(response_data.get("content"))
                else:
                    response_text = str(response_data)
                
                # Извлекаем JSON
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    logger.info(f"🧠 Enhanced AI intent: {parsed_data.get('intent')} (confidence: {parsed_data.get('confidence', 0)}%)")
                    return parsed_data
            
            return self._fallback_intent(text)
            
        except Exception as e:
            logger.error(f"🧠 Enhanced AI intent parser error: {e}")
            return self._fallback_intent(text)
    
    # Вспомогательные методы
    def _format_context(self, context: Dict = None) -> str:
        """Форматирует контекст для AI"""
        if not context:
            return "Нет контекста"
        
        formatted = []
        for key, value in context.items():
            formatted.append(f"{key}: {value}")
        
        return "\n".join(formatted)
    
    def _format_history(self, history: List[str] = None) -> str:
        """Форматирует историю диалога для AI"""
        if not history:
            return "Нет истории"
        
        return "\n".join([f"- {msg}" for msg in history[-5:]])
    
    async def _validate_food_data(self, data: Dict) -> Dict:
        """Валидация и обогащение данных о еде"""
        validated = data.copy()
        
        # Валидация food_items
        food_items = validated.get("food_items", [])
        if not isinstance(food_items, list):
            validated["food_items"] = []
        
        # Валидация meal_type
        valid_meal_types = ["завтрак", "обед", "ужин", "перекус", "неизвестно"]
        meal_type = validated.get("meal_type", "неизвестно")
        if meal_type not in valid_meal_types:
            validated["meal_type"] = "неизвестно"
        
        # Валидация confidence
        confidence = validated.get("total_confidence", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
            validated["total_confidence"] = 0
        
        return validated
    
    def _fallback_food(self, text: str) -> Dict:
        """Fallback для парсера еды"""
        text_lower = text.lower()
        
        # Простые паттерны для базового распознавания
        food_patterns = {
            'яблоко': {'name': 'яблоко', 'quantity': 1, 'unit': 'шт', 'calories': 52},
            'банан': {'name': 'банан', 'quantity': 1, 'unit': 'шт', 'calories': 89},
            'хлеб': {'name': 'хлеб', 'quantity': 1, 'unit': 'кусок', 'calories': 80},
            'суп': {'name': 'суп', 'quantity': 200, 'unit': 'мл', 'calories': 50},
        }
        
        for pattern, data in food_patterns.items():
            if pattern in text_lower:
                return {
                    "food_items": [data],
                    "meal_type": self._guess_meal_type(),
                    "total_confidence": 60,
                    "needs_clarification": True
                }
        
        return {
            "food_items": [],
            "meal_type": "неизвестно",
            "total_confidence": 0,
            "needs_clarification": True
        }
    
    def _fallback_water(self, text: str) -> Dict:
        """Fallback для парсера воды"""
        text_lower = text.lower()
        
        # Простые паттерны для воды
        if 'стакан' in text_lower:
            return {"amount_ml": 250, "unit": "мл", "confidence": 70}
        elif 'чашка' in text_lower:
            return {"amount_ml": 200, "unit": "мл", "confidence": 65}
        elif 'бутылка' in text_lower:
            return {"amount_ml": 500, "unit": "мл", "confidence": 80}
        
        return {"amount_ml": 0, "unit": "мл", "confidence": 0}
    
    def _fallback_activity(self, text: str) -> Dict:
        """Fallback для парсера активности"""
        text_lower = text.lower()
        
        # Простые паттерны для активности
        if 'бег' in text_lower:
            return {"activity_type": "бег", "duration_minutes": 30, "intensity": "средняя", "confidence": 70}
        elif 'ходьба' in text_lower or 'ходил' in text_lower:
            return {"activity_type": "ходьба", "duration_minutes": 60, "intensity": "низкая", "confidence": 75}
        elif 'спорт' in text_lower or 'тренировка' in text_lower:
            return {"activity_type": "тренировка", "duration_minutes": 45, "intensity": "высокая", "confidence": 65}
        
        return {"activity_type": "неизвестно", "duration_minutes": 0, "intensity": "неизвестно", "confidence": 0}
    
    def _fallback_intent(self, text: str) -> Dict:
        """Fallback для классификатора намерений"""
        text_lower = text.lower()
        
        # Простые паттерны для намерений
        if any(word in text_lower for word in ['съел', 'ел', 'пое', 'завтрак', 'обед', 'ужин']):
            intent = "food"
        elif any(word in text_lower for word in ['выпил', 'пил', 'вода', 'чай', 'кофе']):
            intent = "water"
        elif any(word in text_lower for word in ['бег', 'ходьба', 'спорт', 'тренировка']):
            intent = "activity"
        elif any(word in text_lower for word in ['вес', 'масса', 'кг']):
            intent = "weight"
        elif any(word in text_lower for word in ['шаги', 'шаг']):
            intent = "steps"
        elif any(word in text_lower for word in ['?', 'помощь', 'как', 'что', 'почему']):
            intent = "question"
        else:
            intent = "other"

        return {
            "intent": intent,
            "confidence": 50 if intent != "other" else 30,
            "entities": {},
            "response": f"Понял, вы хотите {intent}. Уточните детали." if intent != "other" else "Я не понял. Попробуйте переформулировать.",
            "actions": [],
            "needs_clarification": True
        }
    
    def _guess_meal_type(self) -> str:
        """Определяет тип приема пищи по текущему времени"""
        hour = datetime.now().hour
        
        if 6 <= hour < 11:
            return "завтрак"
        elif 11 <= hour < 16:
            return "обед"
        elif 16 <= hour < 22:
            return "ужин"
        else:
            return "перекус"

# Глобальный экземпляр
enhanced_ai_parser = EnhancedAIParser()
