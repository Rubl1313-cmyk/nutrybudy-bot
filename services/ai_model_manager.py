"""
AI Model Manager - Управление разными AI моделями для разных задач
Реальная архитектура без эмуляций и fallback
"""
import logging
import os
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AIModelManager:
    """Менеджер AI моделей для разных задач"""
    
    def __init__(self):
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.cloudflare_api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        
        # Проверяем наличие учетных данных
        if not all([self.cloudflare_account_id, self.cloudflare_api_token]):
            logger.warning("🤖 AI Model Manager: отсутствуют Cloudflare учетные данные - AI недоступен")
            self.use_real_api = False
        else:
            self.use_real_api = True
            logger.info("🤖 AI Model Manager: Cloudflare AI настроен для реальной работы")
        
        # Модели для разных задач
        self.models = {
            "food_parsing": "@cf/glm/glm-4.7-flash",      # Быстрый парсинг еды
            "vision": "@cf/meta/llama-3.2-11b-vision-instruct",  # Распознавание фото
            "assistant": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",  # AI ассистент
            "analytics": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",  # Аналитика
            "fallback": "@cf/hermes-2-pro-mistral-7b"      # Fallback модель
        }
        
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_account_id}/ai/run/"
        logger.info("🤖 AI Model Manager initialized with real models")
    
    async def call_model(self, model_name: str, prompt: str, system_prompt: str = None, 
                        temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Вызвать конкретную модель"""
        
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_id = self.models[model_name]
        
        # Формируем запрос
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt} if system_prompt else None,
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Убираем None значения
        payload["messages"] = [msg for msg in payload["messages"] if msg is not None]
        
        headers = {
            "Authorization": f"Bearer {self.cloudflare_api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}{model_id}",
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Извлекаем ответ
                        if "result" in result and "response" in result["result"]:
                            ai_response = result["result"]["response"]
                        elif "response" in result:
                            ai_response = result["response"]
                        else:
                            ai_response = str(result)
                        
                        return {
                            "success": True,
                            "response": ai_response,
                            "model": model_id,
                            "usage": result.get("result", {}).get("usage", {}),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ AI API Error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"API Error {response.status}: {error_text}",
                            "model": model_id
                        }
                        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Network error calling {model_id}: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "model": model_id
            }
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout calling {model_id}")
            return {
                "success": False,
                "error": "Request timeout",
                "model": model_id
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error calling {model_id}: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "model": model_id
            }
    
    async def parse_food(self, text: str, user_context: Dict = None) -> Dict[str, Any]:
        """Парсинг еды с помощью GLM-4.7-Flash"""
        
        system_prompt = """Ты - эксперт по анализу еды. Анализируй текст и извлекай информацию о еде.
        
Верни ТОЛЬКО JSON с такой структурой:
{
  "intent": "food|water|steps|activity|other",
  "confidence": 0.0-1.0,
  "extracted_data": {
    "food_items": [{"name": "название", "weight_g": число, "confidence": 0.0-1.0}],
    "water_ml": число,
    "steps": число,
    "activity_type": "тип",
    "duration_min": число
  },
  "reasoning": "почему так определил"
}

Правила:
- Если еда - извлеки продукты и вес
- Если вода - извлеки количество в мл
- Если шаги - извлеки количество
- Если активность - извлеки тип и длительность
- Верни ТОЛЬКО JSON без текста"""
        
        context_str = ""
        if user_context:
            context_str = f"Контекст пользователя: {user_context}\n"
        
        full_prompt = f"{context_str}Анализируй: '{text}'"
        
        result = await self.call_model(
            model_name="food_parsing",
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.2,  # Низкая температура для точного парсинга
            max_tokens=500
        )
        
        if result["success"]:
            try:
                import json
                # Пытаемся извлечь JSON из ответа
                response_text = result["response"]
                
                # Ищем JSON в ответе
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    parsed_data = json.loads(json_match.group(0))
                    result["parsed_data"] = parsed_data
                    return result
                else:
                    # Если не нашли JSON, пробуем распарсить весь ответ
                    parsed_data = json.loads(response_text)
                    result["parsed_data"] = parsed_data
                    return result
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse JSON from food parsing: {e}")
                result["success"] = False
                result["error"] = f"JSON parse error: {str(e)}"
                return result
        
        return result
    
    async def analyze_image(self, image_bytes: bytes, prompt: str = "Опиши еду на фото") -> Dict[str, Any]:
        """Анализ изображения с помощью Llama 3.2 Vision"""
        
        system_prompt = """Ты - эксперт по распознаванию еды на фото. Анализируй изображение и возвращай JSON:
{
  "dish_name": "название блюда на русском",
  "ingredients": [{"name": "ингредиент", "weight_estimate_g": число, "confidence": 0.0-1.0}],
  "cooking_method": "fried|boiled|baked|grilled|raw",
  "category": "soup|main|salad|snack|dessert",
  "confidence": 0.0-1.0,
  "nutrition_estimate": {
    "calories": число,
    "protein": число,
    "fat": число,
    "carbs": число
  }
}

Верни ТОЛЬКО JSON без дополнительного текста."""
        
        # Для vision модели нужно использовать специальный формат
        payload = {
            "image": image_bytes,  # Передаем как base64
            "prompt": f"{system_prompt}\n\n{prompt}",
            "max_tokens": 800
        }
        
        headers = {
            "Authorization": f"Bearer {self.cloudflare_api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}{self.models['vision']}",
                    headers=headers,
                    json=payload,
                    timeout=90  # Дольше таймаут для vision
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if "result" in result and "response" in result["result"]:
                            ai_response = result["result"]["response"]
                        else:
                            ai_response = str(result)
                        
                        # Пытаемся извлечь JSON
                        try:
                            import json
                            import re
                            json_match = re.search(r'\{[\s\S]*\}', ai_response)
                            if json_match:
                                parsed_data = json.loads(json_match.group(0))
                                return {
                                    "success": True,
                                    "response": ai_response,
                                    "parsed_data": parsed_data,
                                    "model": self.models['vision']
                                }
                        except:
                            pass
                        
                        return {
                            "success": True,
                            "response": ai_response,
                            "model": self.models['vision']
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Vision API Error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"Vision API Error {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ Vision error: {e}")
            return {
                "success": False,
                "error": f"Vision error: {str(e)}"
            }
    
    async def ai_assistant(self, message: str, user_context: Dict = None, conversation_history: list = None) -> Dict[str, Any]:
        """AI ассистент с помощью Llama 3.3 70B"""
        
        system_prompt = """Ты - дружелюбный помощник по питанию и здоровому образу жизни NutriBuddy.
Твоя задача - помогать пользователям с питанием, тренировками, достижением целей.

Отвечай:
- Кратко и по делу
- На русском языке
- С поддержкой и мотивацией
- Только по теме здоровья и питания

Если спрашивают о боте - объясняй, как работают функции."""
        
        context_str = ""
        if user_context:
            context_str = f"Профиль пользователя: {user_context}\n"
        
        if conversation_history:
            context_str += f"История диалога: {conversation_history[-3:]}\n"
        
        full_prompt = f"{context_str}Пользователь: {message}"
        
        result = await self.call_model(
            model_name="assistant",
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=800
        )
        
        return result
    
    async def analytics(self, data: Dict, analysis_type: str = "general") -> Dict[str, Any]:
        """Аналитика с помощью Llama 3.3 70B"""
        
        system_prompt = f"""Ты - эксперт по анализу данных питания и здоровья.
Проанализируй данные и верни JSON с инсайтами и рекомендациями.

Тип анализа: {analysis_type}
Верни структурированный JSON с выводами."""
        
        prompt = f"Проанализируй данные пользователя: {data}"
        
        result = await self.call_model(
            model_name="analytics",
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1000
        )
        
        return result

# Глобальный экземпляр
ai_manager = AIModelManager()
