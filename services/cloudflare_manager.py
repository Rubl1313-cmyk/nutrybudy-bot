"""
Ğ£Ğ½Ğ¸Ñ„Ğ¸Ñ†Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ AI Ğ¼ĞµĞ½ĞµĞ´Ğ¶ĞµÑ€ Ğ´Ğ»Ñ� Cloudflare Workers AI
Ğ—Ğ°Ğ¼ĞµĞ½Ñ�ĞµÑ‚ Ñ�Ñ‚Ğ°Ñ€Ñ‹Ğµ hermes_engine.py, llama_vision_engine.py Ğ¸ ai_engine_manager.py
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
    """Ğ•Ğ´Ğ¸Ğ½Ñ‹Ğ¹ Ğ¼ĞµĞ½ĞµĞ´Ğ¶ĞµÑ€ Ğ´Ğ»Ñ� Ğ²Ñ�ĞµÑ… AI Ğ¼Ğ¾Ğ´ĞµĞ»ĞµĞ¹ Ñ‡ĞµÑ€ĞµĞ· Cloudflare Workers AI"""
    
    def __init__(self):
        """Ğ˜Ğ½Ğ¸Ñ†Ğ¸Ğ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸Ñ� Ğ¼ĞµĞ½ĞµĞ´Ğ¶ĞµÑ€Ğ° Cloudflare AI"""
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        
        if not self.account_id or not self.api_token:
            logger.warning("âš ï¸� Cloudflare AI credentials not found! AI functionality will be limited.")
            logger.warning("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in environment variables for full AI functionality.")
            self.base_url = None
            self.headers = None
        else:
            self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/"
            self.headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

        # ĞœĞ¾Ğ´ĞµĞ»Ğ¸ Ğ´Ğ»Ñ� Ñ€Ğ°Ğ·Ğ½Ñ‹Ñ… Ğ·Ğ°Ğ´Ğ°Ñ‡
        self.models = {
            "food_parser": "@hf/nousresearch/hermes-2-pro-mistral-7b",   # â†� Ğ±Ñ‹Ñ�Ñ‚Ñ€ĞµĞµ Ğ¸ Ğ±ĞµĞ· Ğ»Ğ¸ÑˆĞ½Ğ¸Ñ… Ñ€Ğ°Ñ�Ñ�ÑƒĞ¶Ğ´ĞµĞ½Ğ¸Ğ¹
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
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¼ĞµÑ‚Ğ¾Ğ´ Ğ²Ñ‹Ğ·Ğ¾Ğ²Ğ° Ğ»Ñ�Ğ±Ğ¾Ğ¹ Ğ¼Ğ¾Ğ´ĞµĞ»Ğ¸ Ñ� Ğ²Ñ�Ñ‚Ñ€Ğ¾ĞµĞ½Ğ½Ñ‹Ğ¼Ğ¸ Ñ€ĞµÑ‚Ñ€Ğ°Ñ�Ğ¼Ğ¸"""
        
        # Ğ•Ñ�Ğ»Ğ¸ Ğ½ĞµÑ‚ credentials, Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Ñ�Ğ¼ÑƒĞ»Ñ�Ñ†Ğ¸Ñ�
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
        
        # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ response_format ĞµÑ�Ğ»Ğ¸ Ğ¼Ğ¾Ğ´ĞµĞ»ÑŒ Ğ¿Ğ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ¸Ğ²Ğ°ĞµÑ‚
        if response_format and model_key in ["food_parser", "assistant"]:
            payload["response_format"] = response_format

        # Ğ’Ñ�Ñ‚Ñ€Ğ¾ĞµĞ½Ğ½Ñ‹Ğµ Ñ€ĞµÑ‚Ñ€Ğ°Ğ¸ Ñ� Ñ�ĞºÑ�Ğ¿Ğ¾Ğ½ĞµĞ½Ñ†Ğ¸Ğ°Ğ»ÑŒĞ½Ğ¾Ğ¹ Ğ·Ğ°Ğ´ĞµÑ€Ğ¶ĞºĞ¾Ğ¹
        max_attempts = 3
        base_delay = 1.0
        
        for attempt in range(max_attempts):
            try:
                timeout = aiohttp.ClientTimeout(total=60, connect=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.base_url}{model_id}",
                        headers=self.headers,
                        json=payload
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            logger.info(f"âœ… Success from {model_key} (attempt {attempt+1})")
                            
                            # Ğ˜Ğ·Ğ²Ğ»ĞµÑ‡ĞµĞ½Ğ¸Ğµ Ñ‚ĞµĞºÑ�Ñ‚Ğ° Ğ¾Ñ‚Ğ²ĞµÑ‚Ğ°
                            content = result.get("result", {}).get("response")
                            if not content:
                                # ĞŸÑ€Ğ¾Ğ±ÑƒĞµĞ¼ Ğ´Ñ€ÑƒĞ³Ğ¾Ğ¹ Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚
                                content = result.get("choices", [{}])[0].get("message", {}).get("content")
                            if not content:
                                # ĞŸÑ€Ğ¾Ğ±ÑƒĞµĞ¼ Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚ Ğ´Ğ»Ñ� Llama Vision
                                content = result.get("result", {}).get("description")
                            
                            if content:
                                return {
                                    "success": True,
                                    "content": content, 
                                    "model_used": model_key,
                                    "tokens_used": result.get("result", {}).get("usage", {}).get("total_tokens", 0)
                                }
                            else:
                                logger.error(f"â�Œ Empty response from {model_key}")
                        elif resp.status == 429:
                            logger.warning(f"âš ï¸� Rate limit for {model_key} (attempt {attempt+1})")
                        else:
                            error_text = await resp.text()
                            logger.warning(f"âš ï¸ Attempt {attempt+1} failed for {model_key}: {resp.status} - HTTP error")
                            
            except asyncio.TimeoutError:
                logger.warning(f"â�±ï¸� Timeout for {model_key} (attempt {attempt+1})")
            except Exception as e:
                logger.exception(f"â�Œ Exception calling {model_key} (attempt {attempt+1}): {e}")
            
            # Ğ•Ñ�Ğ»Ğ¸ Ñ�Ñ‚Ğ¾ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ñ�Ñ� Ğ¿Ğ¾Ğ¿Ñ‹Ñ‚ĞºĞ°, Ğ¿Ñ€Ğ¾Ğ±ÑƒĞµĞ¼ fallback
            if attempt == max_attempts - 1:
                return await self._call_fallback(messages, response_format, temperature, max_tokens)
            
            # Ğ­ĞºÑ�Ğ¿Ğ¾Ğ½ĞµĞ½Ñ†Ğ¸Ğ°Ğ»ÑŒĞ½Ğ°Ñ� Ğ·Ğ°Ğ´ĞµÑ€Ğ¶ĞºĞ° Ñ� jitter
            delay = base_delay * (2 ** attempt) + (0.1 * attempt)
            logger.info(f"â�³ Retrying {model_key} in {delay:.1f}s...")
            await asyncio.sleep(delay)

        return {"success": False, "error": "All attempts failed"}

    async def _emulate_response(self, model_key: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ğ­Ğ¼ÑƒĞ»Ñ�Ñ†Ğ¸Ñ� Ğ¾Ñ‚Ğ²ĞµÑ‚Ğ° ĞºĞ¾Ğ³Ğ´Ğ° Ğ½ĞµÑ‚ API ĞºĞ»Ñ�Ñ‡ĞµĞ¹"""
        logger.info(f"ğŸ�­ Emulating {model_key} response")
        
        if model_key == "food_parser":
            # Ğ­Ğ¼ÑƒĞ»Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³ ĞµĞ´Ñ‹
            user_message = messages[-1].get("content", "")
            if "ĞºÑƒÑ€Ğ¸Ñ†Ğ°" in user_message.lower() or "Ğ¼Ñ�Ñ�Ğ¾" in user_message.lower():
                mock_response = {
                    "food_items": [
                        {
                            "name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
                            "quantity": 150,
                            "unit": "Ğ³",
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
                    "clarification": "ĞŸĞ¾Ğ¶Ğ°Ğ»ÑƒĞ¹Ñ�Ñ‚Ğ°, ÑƒÑ‚Ğ¾Ñ‡Ğ½Ğ¸Ñ‚Ğµ, Ñ‡Ñ‚Ğ¾ Ğ²Ñ‹ Ñ�ÑŠĞµĞ»Ğ¸"
                }
            
            return {
                "success": True,
                "data": json.dumps(mock_response),
                "model_used": "food_parser_emulated",
                "tokens_used": 50
            }
        
        elif model_key == "assistant":
            # Ğ­Ğ¼ÑƒĞ»Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¾Ñ‚Ğ²ĞµÑ‚ Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚Ğ°
            return {
                "success": True,
                "data": "Ğ¯ Ğ²Ğ°Ñˆ AI Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�! Ğ¯ Ğ¼Ğ¾Ğ³Ñƒ Ğ¿Ğ¾Ğ¼Ğ¾Ñ‡ÑŒ Ğ²Ğ°Ğ¼ Ñ� Ñ�Ğ¾Ğ²ĞµÑ‚Ğ°Ğ¼Ğ¸ Ğ¿Ğ¾ Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²Ğ¾Ğ¼Ñƒ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�, Ğ¿Ğ¾Ğ´Ñ�Ñ‡ĞµÑ‚Ğ¾Ğ¼ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹ Ğ¸ Ñ�Ğ¾Ñ�Ñ‚Ğ°Ğ²Ğ»ĞµĞ½Ğ¸ĞµĞ¼ Ğ¿Ğ»Ğ°Ğ½Ğ° Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�. Ğ”Ğ»Ñ� Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‹ Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile.",
                "model_used": "assistant_emulated",
                "tokens_used": 30
            }
        
        elif model_key == "vision":
            # Ğ­Ğ¼ÑƒĞ»Ğ¸Ñ€ÑƒĞµĞ¼ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ· Ñ„Ğ¾Ñ‚Ğ¾
            mock_response = {
                "dish_name": "Ğ±Ğ»Ñ�Ğ´Ğ¾ Ñ� Ñ„Ğ¾Ñ‚Ğ¾",
                "ingredients": [
                    {
                        "name": "Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚",
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
        """Ğ’Ñ‹Ğ·Ğ¾Ğ² fallback Ğ¼Ğ¾Ğ´ĞµĞ»Ğ¸ (Hermes 2 Pro) Ğ¿Ñ€Ğ¸ Ñ�Ğ±Ğ¾Ğµ Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ¾Ğ¹"""
        logger.warning("âš ï¸� Using fallback model (Hermes 2 Pro)")
        
        return await self._call("fallback", messages, response_format, temperature, max_tokens)

    # === ĞŸÑƒĞ±Ğ»Ğ¸Ñ‡Ğ½Ñ‹Ğµ Ğ¼ĞµÑ‚Ğ¾Ğ´Ñ‹ ===
    
    async def parse_food(self, text: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """ĞŸĞ°Ñ€Ñ�Ğ¸Ğ½Ğ³ ĞµĞ´Ñ‹ Ñ� Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰ÑŒÑ� GLM-4.7-Flash (Ğ¾Ğ±Ñ�Ğ·Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ¾ JSON)"""
        system_prompt = """Ğ¢Ñ‹ â€” Ñ�ĞºÑ�Ğ¿ĞµÑ€Ñ‚ Ğ¿Ğ¾ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ñƒ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�. Ğ˜Ğ·Ğ²Ğ»ĞµĞºĞ¸ Ğ¸Ğ· Ñ‚ĞµĞºÑ�Ñ‚Ğ° Ğ¸Ğ½Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ†Ğ¸Ñ� Ğ¾ ĞµĞ´Ğµ.
Ğ•Ñ�Ğ»Ğ¸ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ Ğ¿ĞµÑ€ĞµÑ‡Ğ¸Ñ�Ğ»Ğ¸Ğ» Ğ½ĞµÑ�ĞºĞ¾Ğ»ÑŒĞºĞ¾ Ğ±Ğ»Ñ�Ğ´ Ğ¸Ğ»Ğ¸ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ², Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ¹ Ğ¾Ñ‚Ğ´ĞµĞ»ÑŒĞ½Ñ‹Ğ¹ Ğ¾Ğ±ÑŠĞµĞºÑ‚ Ğ´Ğ»Ñ� ĞºĞ°Ğ¶Ğ´Ğ¾Ğ³Ğ¾.
Ğ’ĞµÑ€Ğ½Ğ¸ Ğ¢Ğ�Ğ›Ğ¬ĞšĞ� JSON Ğ² Ñ�Ğ»ĞµĞ´ÑƒÑ�Ñ‰ĞµĞ¼ Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğµ:
{
  "food_items": [
    {
      "name": "Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ° Ğ¸Ğ»Ğ¸ Ğ±Ğ»Ñ�Ğ´Ğ° (Ğ½Ğ° Ñ€ÑƒÑ�Ñ�ĞºĞ¾Ğ¼)",
      "quantity": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
      "unit": "Ğ³|Ğ¼Ğ»|ÑˆÑ‚",
      "calories_per_100g": Ñ‡Ğ¸Ñ�Ğ»Ğ¾ (ĞµÑ�Ğ»Ğ¸ Ğ½ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ¾, Ğ¿Ğ¾Ñ�Ñ‚Ğ°Ğ²ÑŒ 0),
      "protein_per_100g": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
      "fat_per_100g": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
      "carbs_per_100g": Ñ‡Ğ¸Ñ�Ğ»Ğ¾
    }
  ],
  "meal_type": "breakfast|lunch|dinner|snack",
  "total_confidence": 0-100
}

Ğ•Ñ�Ğ»Ğ¸ Ğ¸Ğ½Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ†Ğ¸Ğ¸ Ğ½ĞµĞ´Ğ¾Ñ�Ñ‚Ğ°Ñ‚Ğ¾Ñ‡Ğ½Ğ¾ Ğ´Ğ»Ñ� Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½Ğ¸Ñ� ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ° Ğ¸Ğ»Ğ¸ Ñ�Ğ¾Ñ�Ñ‚Ğ°Ğ²Ğ° Ğ±Ğ»Ñ�Ğ´Ğ°, Ğ²ĞµÑ€Ğ½Ğ¸:
{
  "food_items": [],
  "needs_clarification": true,
  "clarification": "ÑƒÑ‚Ğ¾Ñ‡Ğ½Ñ�Ñ�Ñ‰Ğ¸Ğ¹ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�"
}

Ğ’Ğ�Ğ–Ğ�Ğ�: Ğ’ĞµÑ€Ğ½Ğ¸ Ğ¢Ğ�Ğ›Ğ¬ĞšĞ� JSON, Ğ±ĞµĞ· Ğ´Ğ¾Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğ³Ğ¾ Ñ‚ĞµĞºÑ�Ñ‚Ğ°!"""
        
        user_message = f"Ğ¢ĞµĞºÑ�Ñ‚: {text}\nĞšĞ¾Ğ½Ñ‚ĞµĞºÑ�Ñ‚ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�: {user_context or {}}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        result = await self._call(
            "food_parser", 
            messages, 
            response_format={"type": "json_object"}, 
            temperature=0.2,  # â†� Ğ¿Ğ¾Ğ½Ğ¸Ğ¶Ğ°ĞµĞ¼ Ğ´Ğ»Ñ� Ğ±Ğ¾Ğ»ĞµĞµ Ğ´ĞµÑ‚ĞµÑ€Ğ¼Ğ¸Ğ½Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ¾Ñ‚Ğ²ĞµÑ‚Ğ¾Ğ²
            max_tokens=500
        )
        
        if result.get("success"):
            try:
                # ĞŸÑ‹Ñ‚Ğ°ĞµĞ¼Ñ�Ñ� Ñ€Ğ°Ñ�Ğ¿Ğ°Ñ€Ñ�Ğ¸Ñ‚ÑŒ JSON Ğ¾Ñ‚Ğ²ĞµÑ‚
                data = result["data"]
                try:
                    # Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ¿Ñ€Ğ¾Ğ±ÑƒĞµĞ¼ Ñ€Ğ°Ñ�Ğ¿Ğ°Ñ€Ñ�Ğ¸Ñ‚ÑŒ Ğ²ĞµÑ�ÑŒ Ğ¾Ñ‚Ğ²ĞµÑ‚ ĞºĞ°Ğº JSON
                    parsed_data = json.loads(data)
                    data = parsed_data
                except json.JSONDecodeError:
                    # Ğ•Ñ�Ğ»Ğ¸ Ğ½Ğµ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ°ĞµÑ‚Ñ�Ñ�, Ğ¸Ñ‰ĞµĞ¼ Ğ¿ĞµÑ€Ğ²Ñ‹Ğ¹ JSON-Ğ¾Ğ±ÑŠĞµĞºÑ‚
                    import re
                    json_match = re.search(r'(\{.*?\})', data, re.DOTALL)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON from response: {data[:200]}...")
                            return {"success": False, "error": "Failed to parse AI response"}
                
                # Ğ Ğ°Ñ�Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ²Ğ°ĞµĞ¼ JSON
                parsed = json.loads(data)
                return {
                    "success": True,
                    "data": parsed,
                    "model_used": result["model_used"],
                    "tokens_used": result["tokens_used"]
                }
            except json.JSONDecodeError as e:
                logger.error(f"â�Œ Failed to parse JSON from food_parser: {e}")
                logger.error(f"â�Œ Raw data: {result['data']}")
                return {"success": False, "error": "Invalid JSON response"}
        
        return result

    async def ai_assistant(self, message: str, history: Optional[List[Dict]] = None, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """Ğ�Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚ Ğ½Ğ° Llama 3.3 70B"""
        system_prompt = """Ğ¢Ñ‹ - Ğ´Ñ€ÑƒĞ¶ĞµĞ»Ñ�Ğ±Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚ NutriBuddy, Ñ�ĞºÑ�Ğ¿ĞµÑ€Ñ‚ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ¸ Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²Ğ¾Ğ¼Ñƒ Ğ¾Ğ±Ñ€Ğ°Ğ·Ñƒ Ğ¶Ğ¸Ğ·Ğ½Ğ¸.
Ğ�Ñ‚Ğ²ĞµÑ‡Ğ°Ğ¹ ĞºÑ€Ğ°Ñ‚ĞºĞ¾, Ğ¿Ğ¾ Ğ´ĞµĞ»Ñƒ Ğ¸ Ğ¿Ğ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ¸Ğ²Ğ°Ğ¹ Ğ¿Ğ¾Ğ·Ğ¸Ñ‚Ğ¸Ğ²Ğ½Ñ‹Ğ¹ Ñ‚Ğ¾Ğ½. Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹ Ñ�Ğ¼Ğ¾Ğ´Ğ·Ğ¸ ÑƒĞ¼ĞµÑ€ĞµĞ½Ğ½Ğ¾.
ĞŸĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€ÑƒĞ¹ Ğ¾Ñ‚Ğ²ĞµÑ‚Ñ‹, ĞµÑ�Ğ»Ğ¸ ĞµÑ�Ñ‚ÑŒ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�. Ğ�Ğµ Ğ´Ğ°Ğ²Ğ°Ğ¹ Ğ¼ĞµĞ´Ğ¸Ñ†Ğ¸Ğ½Ñ�ĞºĞ¸Ñ… Ñ�Ğ¾Ğ²ĞµÑ‚Ğ¾Ğ², Ñ€ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´ÑƒĞ¹ ĞºĞ¾Ğ½Ñ�ÑƒĞ»ÑŒÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒÑ�Ñ� Ñ� Ğ²Ñ€Ğ°Ñ‡Ğ¾Ğ¼."""
        
        # Ğ¡Ñ‚Ñ€Ğ¾Ğ¸Ğ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ¼Ğ¾Ğ´ĞµĞ»Ğ¸ Ñ� Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸ĞµĞ¹
        messages = [{"role": "system", "content": system_prompt}]
        
        # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ� Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ° Ğ² Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ�
        if history:
            messages.extend(history[-5:])  # ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ 5 Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğ¹
        
        # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ñ‚ĞµĞºÑƒÑ‰ĞµĞµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ
        messages.append({"role": "user", "content": message})
        
        # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ² Ñ�Ğ¸Ñ�Ñ‚ĞµĞ¼Ğ½Ğ¾Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ ĞµÑ�Ğ»Ğ¸ ĞµÑ�Ñ‚ÑŒ
        if user_profile:
            profile_context = f"ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�: {json.dumps(user_profile, ensure_ascii=False)}"
            messages[0]["content"] = f"{system_prompt}\n\n{profile_context}"
        
        return await self._call(
            "assistant", 
            messages, 
            temperature=0.7,
            max_tokens=800
        )

    async def analyze_food_photo(self, image_bytes: bytes, caption: Optional[str] = None) -> Dict[str, Any]:
        """Ğ�Ğ½Ğ°Ğ»Ğ¸Ğ· Ñ„Ğ¾Ñ‚Ğ¾ ĞµĞ´Ñ‹ Ñ‡ĞµÑ€ĞµĞ· Llama Vision"""
        system_prompt = """Ğ¢Ñ‹ - Ñ�ĞºÑ�Ğ¿ĞµÑ€Ñ‚ Ğ¿Ğ¾ ĞºÑƒĞ»Ğ¸Ğ½Ğ°Ñ€Ğ¸Ğ¸ Ğ¸ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�. Ğ�Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€ÑƒĞ¹ Ñ„Ğ¾Ñ‚Ğ¾ ĞµĞ´Ñ‹ Ğ¸ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�Ğ¹:
1. Ğ�Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ±Ğ»Ñ�Ğ´Ğ° (Ğ½Ğ° Ñ€ÑƒÑ�Ñ�ĞºĞ¾Ğ¼)
2. Ğ�Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ğµ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ Ğ¸ Ğ¸Ñ… Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ� Ğ² Ğ³Ñ€Ğ°Ğ¼Ğ¼Ğ°Ñ…
3. ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ğ½ÑƒÑ� ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ğ¸ Ğ‘Ğ–Ğ£ Ğ½Ğ° 100Ğ³ ĞºĞ°Ğ¶Ğ´Ğ¾Ğ³Ğ¾ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°
4. Ğ¢Ğ¸Ğ¿ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸ (Ğ·Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº/Ğ¾Ğ±ĞµĞ´/ÑƒĞ¶Ğ¸Ğ½/Ğ¿ĞµÑ€ĞµĞºÑƒÑ�)
5. Ğ�Ğ±Ñ‰ÑƒÑ� ÑƒĞ²ĞµÑ€ĞµĞ½Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ğ²Ğ°Ğ½Ğ¸Ñ�

Ğ’ĞµÑ€Ğ½Ğ¸ Ğ¢Ğ�Ğ›Ğ¬ĞšĞ� JSON Ğ² Ñ�Ğ»ĞµĞ´ÑƒÑ�Ñ‰ĞµĞ¼ Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğµ:
{
  "dish_name": "Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ±Ğ»Ñ�Ğ´Ğ°",
  "ingredients": [
    {
      "name": "Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚",
      "weight": Ğ²ĞµÑ�_Ğ²_Ğ³Ñ€Ğ°Ğ¼Ğ¼Ğ°Ñ…,
      "calories_per_100g": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
      "protein_per_100g": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
      "fat_per_100g": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
      "carbs_per_100g": Ñ‡Ğ¸Ñ�Ğ»Ğ¾
    }
  ],
  "estimated_total_calories": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
  "estimated_total_protein": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
  "estimated_total_fat": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
  "estimated_total_carbs": Ñ‡Ğ¸Ñ�Ğ»Ğ¾,
  "meal_type": "breakfast|lunch|dinner|snack",
  "confidence": 0.0-1.0
}

Ğ’Ğ�Ğ–Ğ�Ğ�: Ğ’ĞµÑ€Ğ½Ğ¸ Ğ¢Ğ�Ğ›Ğ¬ĞšĞ� JSON, Ğ±ĞµĞ· Ğ´Ğ¾Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğ³Ğ¾ Ñ‚ĞµĞºÑ�Ñ‚Ğ°!"""
        
        prompt = "Ğ�Ğ¿Ğ¸ÑˆĞ¸ ĞµĞ´Ñƒ Ğ½Ğ° Ñ�Ñ‚Ğ¾Ğ¼ Ñ„Ğ¾Ñ‚Ğ¾. Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ğ¸ Ğ±Ğ»Ñ�Ğ´Ğ¾, Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ Ğ¸ Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ� ĞºĞ°Ğ¶Ğ´Ğ¾Ğ³Ğ¾."
        if caption:
            prompt += f" ĞŸĞ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ Ñ‚Ğ°ĞºĞ¶Ğµ Ğ½Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ»: {caption}"
        
        # ĞšĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¸Ğ·Ğ¾Ğ±Ñ€Ğ°Ğ¶ĞµĞ½Ğ¸Ğµ Ğ² base64
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
                # Ğ Ğ°Ñ�Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ²Ğ°ĞµĞ¼ JSON Ğ¸Ğ· Ğ¾Ñ‚Ğ²ĞµÑ‚Ğ°
                data = json.loads(result["data"])
                return {
                    "success": True,
                    "data": data,
                    "model_used": result["model_used"],
                    "tokens_used": result["tokens_used"]
                }
            except json.JSONDecodeError as e:
                logger.error(f"â�Œ Failed to parse JSON from vision: {e}")
                # Ğ•Ñ�Ğ»Ğ¸ Ğ½Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ€Ğ°Ñ�Ğ¿Ğ°Ñ€Ñ�Ğ¸Ñ‚ÑŒ JSON, Ğ²Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµĞ¼ ĞºĞ°Ğº Ñ‚ĞµĞºÑ�Ñ‚
                return {
                    "success": True,
                    "data": result["data"],
                    "model_used": result["model_used"],
                    "tokens_used": result["tokens_used"]
                }
        
        return result

    async def get_health_advice(self, question: str, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """ĞŸĞ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğµ Ñ�Ğ¾Ğ²ĞµÑ‚Ğ° Ğ¿Ğ¾ Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²ÑŒÑ�"""
        system_prompt = """Ğ¢Ñ‹ - Ñ�ĞµÑ€Ñ‚Ğ¸Ñ„Ğ¸Ñ†Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ğ´Ğ¸ĞµÑ‚Ğ¾Ğ»Ğ¾Ğ³ Ğ¸ Ñ‚Ñ€ĞµĞ½ĞµÑ€. Ğ”Ğ°ĞµÑˆÑŒ Ñ�ĞºÑ�Ğ¿ĞµÑ€Ñ‚Ğ½Ñ‹Ğµ Ñ�Ğ¾Ğ²ĞµÑ‚Ñ‹ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ¸ Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²ÑŒÑ�.
Ğ’Ñ�ĞµĞ³Ğ´Ğ° ÑƒÑ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°Ğ¹ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�. Ğ�Ñ‚Ğ²ĞµÑ‡Ğ°Ğ¹ Ñ€Ğ°Ğ·Ğ²ĞµÑ€Ğ½ÑƒÑ‚Ğ¾, Ğ½Ğ¾ Ğ¿Ğ¾ Ğ´ĞµĞ»Ñƒ.
Ğ�Ğµ Ğ´Ğ°Ğ²Ğ°Ğ¹ Ğ¼ĞµĞ´Ğ¸Ñ†Ğ¸Ğ½Ñ�ĞºĞ¸Ñ… Ğ´Ğ¸Ğ°Ğ³Ğ½Ğ¾Ğ·Ğ¾Ğ², Ğ²Ñ�ĞµĞ³Ğ´Ğ° Ñ€ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´ÑƒĞ¹ ĞºĞ¾Ğ½Ñ�ÑƒĞ»ÑŒÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒÑ�Ñ� Ñ� Ğ²Ñ€Ğ°Ñ‡Ğ¾Ğ¼."""
        
        context = f"ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ: {json.dumps(user_profile, ensure_ascii=False)}" if user_profile else ""
        full_prompt = f"{context}{chr(10)}Ğ’Ğ¾Ğ¿Ñ€Ğ¾Ñ�: {question}"
        
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
        """Ğ“ĞµĞ½ĞµÑ€Ğ°Ñ†Ğ¸Ñ� Ğ¿Ğ»Ğ°Ğ½Ğ° Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"""
        system_prompt = """Ğ¢Ñ‹ - Ğ¿Ñ€Ğ¾Ñ„ĞµÑ�Ñ�Ğ¸Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ´Ğ¸ĞµÑ‚Ğ¾Ğ»Ğ¾Ğ³. Ğ¡Ğ¾Ğ·Ğ´Ğ°Ğ²Ğ°Ğ¹ Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¿Ğ»Ğ°Ğ½Ñ‹ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�.
Ğ£Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°Ğ¹ Ñ†ĞµĞ»Ğ¸ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� (Ğ¿Ğ¾Ñ…ÑƒĞ´ĞµĞ½Ğ¸Ğµ/Ğ½Ğ°Ğ±Ğ¾Ñ€/Ğ¿Ğ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ğµ), Ğ¿Ñ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ñ� Ğ¸ Ğ¾Ğ³Ñ€Ğ°Ğ½Ğ¸Ñ‡ĞµĞ½Ğ¸Ñ�.
ĞŸĞ»Ğ°Ğ½ Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ñ�Ğ±Ğ°Ğ»Ğ°Ğ½Ñ�Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¼ Ğ¿Ğ¾ Ğ‘Ğ–Ğ– Ğ¸ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ñ�Ğ¼.
Ğ’ĞµÑ€Ğ½Ğ¸ Ğ¿Ğ»Ğ°Ğ½ Ğ² Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğµ JSON Ñ� Ñ€Ğ°Ğ·Ğ±Ğ¸Ğ²ĞºĞ¾Ğ¹ Ğ¿Ğ¾ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ°Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸."""
        
        context = f"ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ: {json.dumps(user_profile, ensure_ascii=False)}"
        if preferences:
            context += f"{chr(10)}ĞŸÑ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ñ�: {json.dumps(preferences, ensure_ascii=False)}"
        
        prompt = f"{context}{chr(10)}Ğ¡Ğ¾Ğ·Ğ´Ğ°Ğ¹ Ğ¿Ğ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ½Ğ° 1 Ğ´ĞµĞ½ÑŒ Ñ� Ñ€Ğ°Ğ·Ğ±Ğ¸Ğ²ĞºĞ¾Ğ¹ Ğ¿Ğ¾ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ°Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸."
        
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

    @with_timeout(timeout_seconds=60)
    @with_retry(max_attempts=3, delay_seconds=1.0)
    async def transcribe_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Ğ¢Ñ€Ğ°Ğ½Ñ�ĞºÑ€Ğ¸Ğ±Ğ°Ñ†Ğ¸Ñ� Ğ°ÑƒĞ´Ğ¸Ğ¾ Ñ‡ĞµÑ€ĞµĞ· Cloudflare Whisper
        
        Args:
            audio_bytes: Ğ‘Ğ°Ğ¹Ñ‚Ñ‹ Ğ°ÑƒĞ´Ğ¸Ğ¾ Ñ„Ğ°Ğ¹Ğ»Ğ°
            
        Returns:
            Dict Ñ� Ñ€ĞµĞ·ÑƒĞ»ÑŒÑ‚Ğ°Ñ‚Ğ¾Ğ¼ Ñ‚Ñ€Ğ°Ğ½Ñ�ĞºÑ€Ğ¸Ğ±Ğ°Ñ†Ğ¸Ğ¸
        """
        if not self.base_url:
            return {"success": False, "error": "Cloudflare credentials not configured"}
        
        try:
            # Ğ”Ğ»Ñ� Whisper Ğ½ÑƒĞ¶ĞµĞ½ Ğ´Ñ€ÑƒĞ³Ğ¾Ğ¹ Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ°
            url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/@cf/openai/whisper"
            
            # Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field('audio', audio_bytes, filename='audio.ogg', content_type='audio/ogg')
            
            timeout = aiohttp.ClientTimeout(total=60, connect=10, sock_read=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers={"Authorization": f"Bearer {self.api_token}"}, data=form_data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return {
                            "success": True,
                            "text": result["result"]["text"]
                        }
                    else:
                        error_text = await resp.text()
                        logger.error(f"Whisper API error: {resp.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API Error: {resp.status}"
                        }
                        
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Ğ“Ğ»Ğ¾Ğ±Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ñ�ĞºĞ·ĞµĞ¼Ğ¿Ğ»Ñ�Ñ€
cf_manager = CloudflareAIManager()
