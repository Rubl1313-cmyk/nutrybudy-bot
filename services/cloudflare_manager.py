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

    @with_timeout(30)
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
                        "text": """You are an expert chef and food scientist with 20+ years of international cuisine experience.

CARBOHYDRATE IDENTIFICATION:
🍝 PASTA/NOODLES: Long strands, various shapes, Italian/Asian
🍚 RICE: Grains, sticky or separate
🥔 POTATOES: White/yellow flesh, various preparations
🍞 BREAD: Soft/crisp texture, baked

VEGETABLE IDENTIFICATION:
🥬 LEAFY: Lettuce, spinach, cabbage - soft leaves
🥦 FLORETS: Broccoli, cauliflower - tree-like
🥕 ROOT: Carrots, beets, radishes - grow underground
🌱 PODS: Peas, beans - in pods

PROTEIN IDENTIFICATION - PAY EXTREME ATTENTION:
🐟 FISH IDENTIFICATION:
- SALMON: Pink/orange flesh, distinct texture, visible fat lines
- TUNA: Dark red/purple flesh, dense texture
- COD: White flaky flesh, mild appearance
- TROUT: Pink flesh with white stripes
- ANY FISH: Has fish-like texture, no mammal muscle structure

🐔 CHICKEN IDENTIFICATION:
- Chicken breast: White/light pink, smooth fibrous texture
- Chicken thigh: Darker pink, more fat
- Whole chicken: Bird shape, wings, legs

KEY DIFFERENCES:
- FISH: Softer texture, no muscle fibers like meat, often has skin
- CHICKEN: Distinctive fibrous muscle structure, bird anatomy

IMPORTANT CULINARY RULES:
1. "Pasta salad" is NOT a real dish - use "pasta with sauce" or specific pasta dish
2. "Salad" requires leafy greens + dressing + vegetables
3. "Soup" is liquid-based with vegetables/meat
4. "Stew" is thick, slow-cooked with meat/vegetables
5. "Risotto" is creamy rice with specific texture
6. "Curry" has Indian/Asian spices, coconut base
7. "Stir-fry" is Asian style with high heat cooking

REAL DISH EXAMPLES:
- Italian: spaghetti carbonara, lasagna, risotto, pizza margherita
- Russian: borscht, pelmeni, golubtsy, solyanka
- Asian: stir-fry noodles, fried rice, curry, sushi
- American: hamburger, BBQ ribs, mac and cheese
- Mediterranean: Greek salad, hummus, falafel

WRONG EXAMPLES (DO NOT USE):
❌ "pasta salad with grilled chicken" - NOT A REAL DISH
❌ "meat with vegetables" - TOO VAGUE
❌ "food dish" - MEANINGLESS

TASK: Analyze this food image and provide:
1. Main dish name (use REAL dish names)
2. All ingredients with estimated weights
3. Category (soup, main, salad, side, dessert, drink)
4. Preparation style (grilled, boiled, fried, baked, raw)

Respond in JSON format:
{
  "dish_name": "specific dish name",
  "ingredients": [
    {"name": "ingredient", "weight_grams": 100, "type": "protein/carb/vegetable/fat"}
  ],
  "category": "soup/main/salad/side/dessert/drink",
  "preparation_style": "grilled/boiled/fried/baked/raw",
  "confidence": 0.9
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
        
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "food_analysis",
                "schema": {
                    "type": "object",
                    "properties": {
                        "dish_name": {"type": "string"},
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
                        "category": {"type": "string"},
                        "preparation_style": {"type": "string"},
                        "confidence": {"type": "number"}
                    },
                    "required": ["dish_name", "ingredients", "category", "preparation_style", "confidence"]
                }
            }
        }
        
        result = await self._call(
            model_key="vision",
            messages=messages,
            response_format=response_format,
            temperature=0.2,
            max_tokens=1500
        )
        
        if result.get("success"):
            return {
                "success": True,
                "analysis": result.get("data", {}),
                "model": self.models["vision"]
            }
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
