"""
Unified AI manager for Cloudflare Workers AI
Replaces old hermes_engine.py, llama_vision_engine.py and ai_engine_manager.py
"""
import aiohttp
import asyncio
import base64
import json
import logging
import os
from typing import Dict, List, Optional, Any
from utils.retry_utils import with_timeout, with_retry, ai_circuit_breaker, TimeoutError, RetryError

logger = logging.getLogger(__name__)

class CloudflareAIManager:
    """Unified manager for all AI models through Cloudflare Workers AI"""
    
    def __init__(self):
        """Initialize Cloudflare AI manager"""
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        
        if not self.account_id or not self.api_token:
            logger.warning("⚠️ Cloudflare AI credentials not found! AI functionality will be limited.")
            logger.warning("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in environment variables for full AI functionality.")
            self.base_url = None
            self.headers = None
        else:
            self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/"
            self.headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

        # Models for different tasks
        self.models = {
            "food_parser": "@hf/nousresearch/hermes-2-pro-mistral-7b",   # → faster and without unnecessary reasoning
            "assistant": "@cf/meta/llama-3.3-70b-instruct-fp8-fast", 
            "vision": "@cf/meta/llama-3.2-11b-vision-instruct",
            "whisper": "@cf/openai/whisper",
            "fallback": "@cf/zai-org/glm-4.7-flash"
        }

    async def _call(
        self,
        model_key: str,
        messages: List[Dict[str, Any]],
        response_format: Optional[Dict] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Universal call to Cloudflare AI with retry and error handling"""
        
        if not self.base_url or not self.headers:
            logger.error("❌ Cloudflare AI not configured - missing credentials")
            return {"error": "Cloudflare AI not configured", "success": False}
        
        model = self.models.get(model_key)
        if not model:
            logger.error(f"❌ Unknown model: {model_key}")
            return {"error": f"Unknown model: {model_key}", "success": False}
        
        url = f"{self.base_url}{model}"
        
        # Prepare request payload
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ Cloudflare AI error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}", "success": False}
                    
                    result = await response.json()
                    
                    if result.get("success", False):
                        return {"success": True, "data": result.get("result", {})}
                    else:
                        logger.error(f"❌ Cloudflare AI failed: {result}", exc_info=True)
                        return {"success": False, "data": None, "error": "API call failed"}
                        
        except asyncio.TimeoutError:
            logger.error(f"❌ Cloudflare AI timeout after {timeout}s", exc_info=True)
            return {"success": False, "data": None, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ Cloudflare AI exception: {e}", exc_info=True)
            return {"success": False, "data": None, "error": str(e)}

    @with_timeout(60)
    @with_retry(max_attempts=3, delay_seconds=1)
    @ai_circuit_breaker(failure_threshold=5, recovery_timeout=60)
    async def parse_food_image(self, image_data: bytes) -> Dict[str, Any]:
        """Parse food from image using vision model
        
        Cloudflare Llama-3.2-11b-vision-instruct поддерживает:
        - Форматы: JPEG, PNG, WebP, GIF
        - Максимальный размер: 20MB
        - Кодируем в base64 с data URI scheme
        """
        from PIL import Image
        import io
        
        # Логгируем размер и первые байты для отладки
        logger.info(f"[VISION] Image data size: {len(image_data)} bytes")
        logger.info(f"[VISION] First 20 bytes: {image_data[:20].hex()}")
        
        # Конвертируем изображение в JPEG для совместимости
        try:
            # Открываем изображение через PIL
            img = Image.open(io.BytesIO(image_data))
            
            # Логгируем формат
            logger.info(f"[VISION] Image format: {img.format}, mode: {img.mode}, size: {img.size}")
            
            # Конвертируем в RGB (если есть альфа-канал)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Сохраняем как JPEG в память
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Кодируем в base64
            image_b64 = base64.b64encode(output.read()).decode('utf-8')
            logger.info(f"[VISION] Converted to JPEG, base64 size: {len(image_b64)} bytes")
            
        except Exception as e:
            logger.error(f"❌ Image conversion error: {e}")
            logger.error(f"❌ Image data type: {type(image_data)}, size: {len(image_data) if image_data else 0}")
            
            # Проверяем, это вообще изображение?
            if len(image_data) < 10:
                return {"success": False, "error": "Файл слишком маленький для изображения"}
            
            # Проверяем магические байты
            if image_data[:2] == b'\xFF\xD8':
                logger.info("[VISION] Detected JPEG")
            elif image_data[:8] == b'\x89PNG\r\n\x1a\n':
                logger.info("[VISION] Detected PNG")
            elif image_data[:6] in (b'RIFF', b'WEBP'):
                logger.info("[VISION] Detected WebP")
            else:
                logger.warning(f"[VISION] Unknown image format: {image_data[:10].hex()}")
            
            # Если не удалось конвертировать, пробуем оригинал
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            logger.info(f"[VISION] Using original file, base64 size: {len(image_b64)} bytes")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Ты — эксперт-повар и диетолог с 20+ летним опытом.

ВАЖНО: Отвечай ТОЛЬКО на русском языке!

ТВОЯ ЗАДАЧА: Опиши блюдо КРАСИВО и ТОЧНО, как это сделал бы профессиональный ресторанный критик.

ПРАВИЛА НАЗВАНИЯ БЛЮДА:
✅ Используй ПОЭТИЧНЫЕ, АППЕТИТНЫЕ описания
✅ Указывай способ приготовления (запечённый, тушёный, жареный, на гриле)
✅ Упоминай ключевые ингредиенты в названии
✅ Используй правильные кулинарные термины

ПРИМЕРЫ ХОРОШИХ НАЗВАНИЙ:
• "Запечённый лосось с лимонным соусом и свежими овощами"
• "Нежные куриные котлеты с картофельным пюре"
• "Салат Цезарь с курицей гриль и пармезаном"
• "Ароматный борщ со сметаной и чесночными пампушками"
• "Паста карбонара с хрустящим беконом и пармезаном"
• "Сочный стейк из говядины с овощами гриль"
• "Домашние пельмени в сливочном соусе"

ПРАВИЛА ИНГРЕДИЕНТОВ:
• Указывай ВСЕ видимые ингредиенты
• Оценивай вес РЕАЛИСТИЧНО (порция = 150-400г для основного блюда)
• Классифицируй правильно: protein/carb/vegetable/fat/dairy

ОПРЕДЕЛЕНИЕ ТИПОВ ИНГРЕДИЕНТОВ:
🥩 БЕЛКИ: мясо, рыба, птица, яйца, сыр, творог
🍞 УГЛЕВОДЫ: хлеб, рис, паста, картофель, крупы, бобовые
🥬 ОВОЩИ: все овощи, зелень, грибы
🧈 ЖИРЫ: масло, сливки, орехи, авокадо
🥛 МОЛОЧНЫЕ: молоко, йогурт, сметана, сыр

ФОРМАТ ОТВЕТА (строго JSON):
{
  "dish_name": "Красивое аппетитное название блюда",
  "ingredients": [
    {"name": "ингредиент", "weight_grams": 150, "type": "protein"}
  ],
  "category": "main",
  "preparation_style": "grilled",
  "confidence": 0.95
}"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]
        
        # Не используем response_format чтобы Vision модель возвращала свободный текст
        # который мы затем парсим через _parse_text_response
        
        result = await self._call(
            model_key="vision",
            messages=messages,
            temperature=0.2,
            max_tokens=1500
        )
        
        if result.get("success"):
            data = result.get("data", {})
            
            # Cloudflare API может вернуть JSON внутри текстового поля response
            # Пытаемся извлечь JSON из разных мест
            analysis = None
            
            # Вариант 1: data уже является JSON объектом с нужными полями
            if isinstance(data, dict) and "dish_name" in data:
                analysis = data
            # Вариант 2: JSON внутри поля response (текстовый ответ)
            elif isinstance(data, dict) and "response" in data:
                response_text = data.get("response", "")
                # Проверяем, является ли response уже JSON объектом
                if isinstance(response_text, dict):
                    analysis = response_text
                else:
                    # Ищем JSON в тексте ответа
                    import re
                    # Ищем JSON блок между { и }
                    json_match = re.search(r'\{[\s\S]*\}', response_text)
                    if json_match:
                        try:
                            analysis = json.loads(json_match.group())
                        except json.JSONDecodeError as e:
                            logger.error(f"[VISION] Failed to parse JSON from response: {e}")
                            logger.error(f"[VISION] Response text: {response_text[:500]}")
                    else:
                        # Если JSON не найден, парсим текстовый ответ вручную
                        logger.info(f"[VISION] No JSON found in response, parsing text manually")
                        analysis = self._parse_text_response(response_text)
            # Вариант 3: data является строкой с JSON
            elif isinstance(data, str):
                import re
                json_match = re.search(r'\{[\s\S]*\}', data)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                    except json.JSONDecodeError as e:
                        logger.error(f"[VISION] Failed to parse JSON from string: {e}")
            
            if analysis and "dish_name" in analysis:
                logger.info(f"[VISION] Analysis result: {json.dumps(analysis, ensure_ascii=False, indent=2)}")
                return {
                    "success": True,
                    "analysis": analysis,
                    "model": self.models["vision"]
                }
            else:
                logger.error(f"[VISION] Could not extract valid analysis from response")
                logger.error(f"[VISION] Raw data: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
                return {"success": False, "data": None, "error": "Could not parse vision response"}
        else:
            logger.error(f"❌ Vision analysis failed: {result.get('error')}", exc_info=True)
            return {"success": False, "data": None, "error": result.get("error")}

    @with_timeout(25)
    @with_retry(max_attempts=2, delay_seconds=1)
    async def parse_food_text(self, food_description: str) -> Dict[str, Any]:
        """Parse food from text description"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert nutritionist and food analyst with 20+ years of experience.

TASK: Parse the food description and extract ingredients with weights.

RULES:
1. Extract ALL food items mentioned
2. Estimate realistic weights (grams) based on typical portions
3. Classify each ingredient as: protein, carb, vegetable, fruit, fat, dairy, other
4. Use standard food names (no abbreviations)
5. Consider cooking methods and preparation styles

WEIGHT GUIDELINES:
- Protein portions: 100-250g
- Carb portions: 100-300g (cooked weight)
- Vegetables: 50-200g
- Fruits: 100-200g
- Fats/oils: 5-30g
- Dairy: 100-250g

EXAMPLES:
Input: "200g chicken breast with rice and salad"
Output: chicken breast (200g, protein), white rice (150g, carb), mixed vegetables (100g, vegetable)

Input: "pasta carbonara"
Output: pasta (200g, carb), bacon (50g, protein), eggs (100g, protein), parmesan (20g, fat), cream (50g, fat)

Respond in JSON format:
{
  "ingredients": [
    {"name": "food item", "weight_grams": 100, "type": "category"}
  ],
  "estimated_calories": 500,
  "confidence": 0.8
}"""
            },
            {
                "role": "user",
                "content": f"Parse this food description: {food_description}"
            }
        ]
        
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "food_text_parsing",
                "schema": {
                    "type": "object",
                    "properties": {
                        "ingredients": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "weight_grams": {"type": "number"},
                                    "type": {"type": "string"}
                                },
                                "required": ["name", "weight_grams", "type"]
                            }
                        },
                        "estimated_calories": {"type": "number"},
                        "confidence": {"type": "number"}
                    },
                    "required": ["ingredients", "estimated_calories", "confidence"]
                }
            }
        }
        
        result = await self._call(
            model_key="food_parser",
            messages=messages,
            response_format=response_format,
            temperature=0.1,
            max_tokens=500  # Уменьшено до 500 (лимит Cloudflare 1024)
        )
        
        if result.get("success"):
            return {
                "success": True,
                "analysis": result.get("data", {}),
                "model": self.models["food_parser"]
            }
        else:
            logger.error(f"❌ Text parsing failed: {result.get('error')}", exc_info=True)
            return {"success": False, "data": None, "error": result.get("error")}

    @with_timeout(20)
    @with_retry(max_attempts=2, delay_seconds=1)
    async def get_assistant_response(self, user_message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get AI assistant response for general queries"""
        
        system_prompt = """You are a helpful AI nutrition and health assistant. You provide:

1. **Nutrition Advice**: Evidence-based nutrition information
2. **Recipe Suggestions**: Healthy and tasty meal ideas
3. **Fitness Guidance**: Exercise and workout recommendations
4. **Health Tips**: General wellness and lifestyle advice
5. **Progress Analysis**: Help users understand their health data

GUIDELINES:
- Be encouraging and supportive
- Provide practical, actionable advice
- Cite scientific evidence when relevant
- Recommend consulting doctors for medical issues
- Focus on sustainable, healthy habits
- Be concise but thorough

RESPONSE STYLE:
- Use emojis for visual appeal 🥗💪🏃
- Structure with clear headings
- Include specific examples when helpful
- End with a motivational message"""

        if context:
            system_prompt += f"\n\nUSER CONTEXT:\n{json.dumps(context, indent=2)}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        result = await self._call(
            model_key="assistant",
            messages=messages,
            temperature=0.7,
            max_tokens=500  # Уменьшено до 500 (лимит Cloudflare 1024)
        )
        
        if result.get("success"):
            return {
                "success": True,
                "response": result.get("data", {}).get("response", ""),
                "model": self.models["assistant"]
            }
        else:
            logger.error(f"❌ Assistant response failed: {result.get('error')}", exc_info=True)
            return {"success": False, "data": None, "error": result.get("error")}

    @with_timeout(15)
    async def transcribe_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """Transcribe audio using Whisper model"""
        
        # Convert audio to base64
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe this audio to text. The audio is in Russian or English."
                    },
                    {
                        "type": "audio_url",
                        "audio_url": {
                            "url": f"data:audio/wav;base64,{audio_b64}"
                        }
                    }
                ]
            }
        ]
        
        result = await self._call(
            model_key="whisper",
            messages=messages,
            temperature=0.0,
            max_tokens=500
        )
        
        if result.get("success"):
            transcription = result.get("data", {}).get("response", "")
            return {
                "success": True,
                "transcription": transcription,
                "model": self.models["whisper"]
            }
        else:
            logger.error(f"❌ Audio transcription failed: {result.get('error')}", exc_info=True)
            return {"success": False, "data": None, "error": result.get("error")}

    async def health_check(self) -> Dict[str, Any]:
        """Check if Cloudflare AI is accessible"""
        
        if not self.base_url or not self.headers:
            return {
                "success": False,
                "error": "Not configured - missing credentials",
                "status": "not_configured"
            }
        
        try:
            # Simple test call
            messages = [
                {"role": "user", "content": "Hello, are you working?"}
            ]
            
            result = await self._call(
                model_key="food_parser",
                messages=messages,
                temperature=0.1,
                max_tokens=50,
                timeout=10
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "status": "healthy",
                    "models": list(self.models.keys()),
                    "account_id": self.account_id[:8] + "..." if self.account_id else None
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "status": "unhealthy"
                }
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "error"
            }

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        
        return {
            "models": {
                key: {
                    "name": model,
                    "purpose": self._get_model_purpose(key)
                }
                for key, model in self.models.items()
            },
            "configured": bool(self.base_url and self.headers),
            "account_id": self.account_id[:8] + "..." if self.account_id else None
        }

    def _get_model_purpose(self, model_key: str) -> str:
        """Get purpose description for model"""
        purposes = {
            "food_parser": "Fast food text parsing and analysis",
            "assistant": "General AI assistant for nutrition and health",
            "vision": "Image analysis for food recognition",
            "whisper": "Audio transcription for voice messages",
            "fallback": "Backup model when others fail"
        }
        return purposes.get(model_key, "Unknown purpose")

    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response from Vision model when JSON is not found"""
        import re
        
        # Извлекаем название блюда
        dish_name = "Неизвестное блюдо"
        dish_match = re.search(r'(?:блюдо|основное блюдо|название)[:\s]*([^\n]+)', text, re.IGNORECASE)
        if dish_match:
            dish_name = dish_match.group(1).strip()
        
        # Извлекаем ингредиенты
        ingredients = []
        # Ищем паттерны типа "Картофель: 150 грамм" или "Картофель 150г"
        ingredient_patterns = [
            r'([А-Яа-яёЁ\s]+)[:\s]+(\d+)\s*(?:грамм|г|gram)',
            r'([А-Яа-яёЁ\s]+)[:\s]+(\d+)\s*г\b',
            r'([А-Яа-яёЁ\s]+)[:\s]+(\d+)\s*$'
        ]
        
        for pattern in ingredient_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                name = match[0].strip()
                weight = int(match[1])
                if name and weight > 0:
                    # Определяем тип ингредиента
                    ing_type = "other"
                    name_lower = name.lower()
                    if any(word in name_lower for word in ['курица', 'говядина', 'свинина', 'рыба', 'лосось', 'тунец', 'яйцо', 'мясо']):
                        ing_type = "protein"
                    elif any(word in name_lower for word in ['картофель', 'рис', 'паста', 'хлеб', 'макароны', 'лапша']):
                        ing_type = "carb"
                    elif any(word in name_lower for word in ['морковь', 'свекла', 'лук', 'капуста', 'томат', 'помидор', 'огурец', 'перец', 'брокколи']):
                        ing_type = "vegetable"
                    elif any(word in name_lower for word in ['масло', 'сливочное масло', 'сыр', 'сметана']):
                        ing_type = "fat"
                    
                    ingredients.append({
                        "name": name,
                        "weight_grams": weight,
                        "type": ing_type
                    })
        
        # Определяем категорию
        category = "main"
        if any(word in text.lower() for word in ['суп', 'борщ', 'уха', 'солянка']):
            category = "soup"
        elif any(word in text.lower() for word in ['салат']):
            category = "salad"
        elif any(word in text.lower() for word in ['десерт', 'торт', 'пирог', 'мороженое']):
            category = "dessert"
        elif any(word in text.lower() for word in ['напиток', 'сок', 'чай', 'кофе']):
            category = "drink"
        
        # Определяем способ приготовления
        preparation_style = "boiled"
        if any(word in text.lower() for word in ['жарен', 'жарка']):
            preparation_style = "fried"
        elif any(word in text.lower() for word in ['запечён', 'запекание', 'духовка']):
            preparation_style = "baked"
        elif any(word in text.lower() for word in ['гриль', 'гриля']):
            preparation_style = "grilled"
        elif any(word in text.lower() for word in ['сырой', 'свежий']):
            preparation_style = "raw"
        
        return {
            "dish_name": dish_name,
            "ingredients": ingredients,
            "category": category,
            "preparation_style": preparation_style,
            "confidence": 0.7
        }

# Global instance
cloudflare_ai = CloudflareAIManager()

# Backward compatibility alias
cf_manager = cloudflare_ai

# =============================================================================
# 🎯 CONVENIENCE FUNCTIONS
# =============================================================================
async def parse_food_from_image(image_data: bytes) -> Dict[str, Any]:
    """Convenience function for food image parsing"""
    return await cloudflare_ai.parse_food_image(image_data)

async def parse_food_from_text(food_description: str) -> Dict[str, Any]:
    """Convenience function for food text parsing"""
    return await cloudflare_ai.parse_food_text(food_description)

async def get_ai_assistant_response(message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Convenience function for AI assistant"""
    return await cloudflare_ai.get_assistant_response(message, context)

async def transcribe_voice_message(audio_data: bytes) -> Dict[str, Any]:
    """Convenience function for audio transcription"""
    return await cloudflare_ai.transcribe_audio(audio_data)

async def check_ai_health() -> Dict[str, Any]:
    """Convenience function for health check"""
    return await cloudflare_ai.health_check()
