"""
Унифицированный AI менеджер для Cloudflare Workers AI
Заменяет старые hermes_engine.py, llama_vision_engine.py и ai_engine_manager.py
"""
import aiohttp
import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from utils.retry_utils import with_timeout, with_retry, ai_circuit_breaker, TimeoutError, RetryError

logger = logging.getLogger(__name__)

class CloudflareAIManager:
    """Единый менеджер для всех AI моделей через Cloudflare Workers AI"""
    
    def __init__(self):
        """Инициализация менеджера Cloudflare AI"""
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        
        if not self.account_id or not self.api_token:
            logger.warning("⚠️ Cloudflare AI credentials not found. Using emulation mode.")
            logger.warning("AI functionality will be limited. Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in environment.")
            self.base_url = None
            self.headers = {}
        else:
            self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/"
            self.headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

        # Модели для разных задач
        self.models = {
            "food_parser": "@cf/zai-org/glm-4.7-flash",
            "assistant": "@cf/meta/llama-3.3-70b-instruct-fp8-fast", 
            "vision": "@cf/meta/llama-3.2-11b-vision-instruct",
            "fallback": "@cf/hermes-2-pro-mistral-7b"
        }

    @with_timeout(timeout_seconds=90)
    @with_retry(max_attempts=5, delay_seconds=1.0)
    async def _call(
        self,
        model_key: str,
        messages: List[Dict[str, Any]],
        response_format: Optional[Dict] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        retries: int = 2
    ) -> Dict[str, Any]:
        """Универсальный метод вызова любой модели с повторными попытками и fallback"""
        
        # Если нет credentials, используем эмуляцию
        if not self.base_url:
            return await self._emulate_response(model_key, messages)
        
        model_id = self.models.get(model_key)
        if not model_id:
            return {"success": False, "error": f"Unknown model key: {model_key}"}

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Добавляем response_format если модель поддерживает
        if response_format and model_key in ["food_parser", "assistant"]:
            payload["response_format"] = response_format

        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}{model_id}",
                        headers=self.headers,
                        json=payload,
                        timeout=60
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            logger.info(f"Raw response from {model_key}: {result}")
                            
                            # Извлечение текста ответа
                            content = result.get("result", {}).get("response")
                            if not content:
                                # Пробуем другой формат
                                content = result.get("choices", [{}])[0].get("message", {}).get("content")
                            
                            if content:
                                logger.info(f"✅ {model_key} response received successfully")
                                return {
                                    "success": True, 
                                    "data": content, 
                                    "model_used": model_key,
                                    "tokens_used": result.get("result", {}).get("usage", {}).get("total_tokens", 0)
                                }
                            else:
                                logger.error(f"❌ Empty response from {model_key}")
                        else:
                            error_text = await resp.text()
                            logger.warning(f"⚠️ Attempt {attempt+1} failed for {model_key}: {resp.status} - {error_text}")
                            
                            if attempt == retries - 1:
                                # Последняя попытка - пробуем fallback
                                return await self._call_fallback(messages, response_format, temperature, max_tokens)
                            
                            await asyncio.sleep(1)
            except Exception as e:
                logger.exception(f"❌ Exception calling {model_key}: {e}")
                if attempt == retries - 1:
                    return await self._call_fallback(messages, response_format, temperature, max_tokens)
                await asyncio.sleep(1)

        return {"success": False, "error": "All attempts failed"}

    async def _emulate_response(self, model_key: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Эмуляция ответа когда нет API ключей"""
        logger.info(f"🎭 Emulating {model_key} response")
        
        if model_key == "food_parser":
            # Эмулируем парсинг еды
            user_message = messages[-1].get("content", "")
            if "курица" in user_message.lower() or "мясо" in user_message.lower():
                mock_response = {
                    "food_items": [
                        {
                            "name": "курица",
                            "quantity": 150,
                            "unit": "г",
                            "calories_per_100g": 165,
                            "protein_per_100g": 31,
                            "fat_per_100g": 3.6,
                            "carbs_per_100g": 0
                        }
                    ],
                    "meal_type": "lunch",
                    "total_confidence": 85
                }
            else:
                mock_response = {
                    "food_items": [],
                    "needs_clarification": True,
                    "clarification": "Пожалуйста, уточните, что вы съели"
                }
            
            return {
                "success": True,
                "data": json.dumps(mock_response),
                "model_used": "food_parser_emulated",
                "tokens_used": 50
            }
        
        elif model_key == "assistant":
            # Эмулируем ответ ассистента
            return {
                "success": True,
                "data": "Я ваш AI ассистент по питанию! Я могу помочь вам с советами по здоровому питанию, подсчетом калорий и составлением плана питания. Для начала работы создайте профиль командой /set_profile.",
                "model_used": "assistant_emulated",
                "tokens_used": 30
            }
        
        elif model_key == "vision":
            # Эмулируем анализ фото
            mock_response = {
                "dish_name": "блюдо с фото",
                "ingredients": [
                    {
                        "name": "ингредиент",
                        "weight": 100,
                        "calories_per_100g": 100,
                        "protein_per_100g": 10,
                        "fat_per_100g": 5,
                        "carbs_per_100g": 10
                    }
                ],
                "estimated_total_calories": 100,
                "estimated_total_protein": 10,
                "estimated_total_fat": 5,
                "estimated_total_carbs": 10,
                "meal_type": "lunch",
                "confidence": 0.8
            }
            
            return {
                "success": True,
                "data": json.dumps(mock_response),
                "model_used": "vision_emulated",
                "tokens_used": 80
            }
        
        else:
            return {
                "success": False,
                "error": f"Emulation not supported for model: {model_key}"
            }

    async def _call_fallback(self, messages: List[Dict[str, Any]], response_format: Optional[Dict], temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Вызов fallback модели (Hermes 2 Pro) при сбое основной"""
        logger.warning("⚠️ Using fallback model (Hermes 2 Pro)")
        
        return await self._call("fallback", messages, response_format, temperature, max_tokens, retries=1)

    # === Публичные методы ===
    
    async def parse_food(self, text: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Парсинг еды с помощью GLM-4.7-Flash (обязательно JSON)"""
        system_prompt = """Ты - эксперт по анализу питания. Извлеки из текста информацию о еде.
Верни ТОЛЬКО JSON в следующем формате:
{
  "food_items": [
    {
      "name": "название продукта (на русском)",
      "quantity": число,
      "unit": "г|мл|шт",
      "calories_per_100g": число (если неизвестно, поставь 0),
      "protein_per_100g": число,
      "fat_per_100g": число,
      "carbs_per_100g": число
    }
  ],
  "meal_type": "breakfast|lunch|dinner|snack",
  "total_confidence": 0-100
}

Если информации недостаточно, верни:
{
  "food_items": [],
  "needs_clarification": true,
  "clarification": "уточняющий вопрос"
}

ВАЖНО: Верни ТОЛЬКО JSON, без дополнительного текста!"""
        
        user_message = f"Текст: {text}\nКонтекст пользователя: {user_context or {}}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        result = await self._call(
            "food_parser", 
            messages, 
            response_format={"type": "json_object"}, 
            temperature=0.2,
            max_tokens=500
        )
        
        if result.get("success"):
            try:
                # Распарсиваем JSON из ответа
                data = json.loads(result["data"])
                return {
                    "success": True,
                    "data": data,
                    "model_used": result["model_used"],
                    "tokens_used": result["tokens_used"]
                }
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse JSON from food_parser: {e}")
                return {"success": False, "error": "Invalid JSON response"}
        
        return result

    async def ai_assistant(self, message: str, history: Optional[List[Dict]] = None, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """Ассистент на Llama 3.3 70B"""
        system_prompt = """Ты - дружелюбный персональный ассистент NutriBuddy, эксперт по питанию и здоровому образу жизни.
Отвечай кратко, по делу и поддерживай позитивный тон. Используй эмодзи умеренно.
Персонализируй ответы, если есть данные профиля. Не давай медицинских советов, рекомендуй консультироваться с врачом."""
        
        # Строим сообщения для модели с историей
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем историю диалога в сообщения
        if history:
            messages.extend(history[-5:])  # Последние 5 сообщений
        
        # Добавляем текущее сообщение
        messages.append({"role": "user", "content": message})
        
        # Добавляем профиль в системное сообщение если есть
        if user_profile:
            profile_context = f"Профиль пользователя: {json.dumps(user_profile, ensure_ascii=False)}"
            messages[0]["content"] = f"{system_prompt}\n\n{profile_context}"
        
        return await self._call(
            "assistant", 
            messages, 
            temperature=0.7,
            max_tokens=800
        )

    async def analyze_food_photo(self, image_bytes: bytes, caption: Optional[str] = None) -> Dict[str, Any]:
        """Анализ фото еды через Llama Vision"""
        system_prompt = """Ты - эксперт по кулинарии и питанию. Анализируй фото еды и определяй:
1. Название блюда (на русском)
2. Основные ингредиенты и их примерный вес в граммах
3. Примерную калорийность и БЖУ на 100г каждого ингредиента
4. Тип приема пищи (завтрак/обед/ужин/перекус)
5. Общую уверенность распознавания

Верни ТОЛЬКО JSON в следующем формате:
{
  "dish_name": "название блюда",
  "ingredients": [
    {
      "name": "ингредиент",
      "weight": вес_в_граммах,
      "calories_per_100g": число,
      "protein_per_100g": число,
      "fat_per_100g": число,
      "carbs_per_100g": число
    }
  ],
  "estimated_total_calories": число,
  "estimated_total_protein": число,
  "estimated_total_fat": число,
  "estimated_total_carbs": число,
  "meal_type": "breakfast|lunch|dinner|snack",
  "confidence": 0.0-1.0
}

ВАЖНО: Верни ТОЛЬКО JSON, без дополнительного текста!"""
        
        prompt = "Опиши еду на этом фото. Определи блюдо, ингредиенты и примерный вес каждого."
        if caption:
            prompt += f" Пользователь также написал: {caption}"
        
        # Конвертируем изображение в base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_b64}"}
                ]
            }
        ]
        
        result = await self._call(
            "vision",
            messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        if result.get("success"):
            try:
                # Распарсиваем JSON из ответа
                data = json.loads(result["data"])
                return {
                    "success": True,
                    "data": data,
                    "model_used": result["model_used"],
                    "tokens_used": result["tokens_used"]
                }
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse JSON from vision: {e}")
                # Если не удалось распарсить JSON, возвращаем как текст
                return {
                    "success": True,
                    "data": result["data"],
                    "model_used": result["model_used"],
                    "tokens_used": result["tokens_used"]
                }
        
        return result

    async def get_health_advice(self, question: str, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """Получение совета по здоровью"""
        system_prompt = """Ты - сертифицированный диетолог и тренер. Даешь экспертные советы по питанию и здоровью.
Всегда учитывай профиль пользователя. Отвечай развернуто, но по делу.
Не давай медицинских диагнозов, всегда рекомендуй консультироваться с врачом."""
        
        context = f"Профиль: {json.dumps(user_profile, ensure_ascii=False)}" if user_profile else ""
        full_prompt = f"{context}{chr(10)}Вопрос: {question}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ]
        
        return await self._call(
            "assistant",
            messages,
            temperature=0.5,
            max_tokens=1000
        )

    async def generate_meal_plan(self, user_profile: Dict, preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Генерация плана питания"""
        system_prompt = """Ты - профессиональный диетолог. Создавай персонализированные планы питания.
Учитывай цели пользователя (похудение/набор/поддержание), предпочтения и ограничения.
План должен быть сбалансированным по БЖЖ и калориям.
Верни план в формате JSON с разбивкой по приемам пищи."""
        
        context = f"Профиль: {json.dumps(user_profile, ensure_ascii=False)}"
        if preferences:
            context += f"{chr(10)}Предпочтения: {json.dumps(preferences, ensure_ascii=False)}"
        
        prompt = f"{context}{chr(10)}Создай план питания на 1 день с разбивкой по приемам пищи."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        return await self._call(
            "assistant",
            messages,
            temperature=0.4,
            max_tokens=1500
        )

# Глобальный экземпляр
cf_manager = CloudflareAIManager()
