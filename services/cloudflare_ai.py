"""
Cloudflare Workers AI Integration для NutriBuddy
Улучшенная версия с поддержкой JSON, повторными попытками и перебором моделей.
Все запросы на английском, ответы парсятся и затем переводятся.
"""
import aiohttp
import os
import logging
import asyncio
import json
import re
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Модели для Vision (основная и запасная)
VISION_MODELS = [
    "@cf/unum/uform-gen2-qwen-500m",  # основная
    "@cf/llava-hf/llava-1.5-7b-hf",   # fallback с лучшим пониманием контекста
]

# Промпт на английском, требующий JSON
FOOD_RECOGNITION_PROMPT = """
Analyze this food image and return a STRICT JSON object with the following structure:
{
  "dishes": [
    {
      "name_en": "Name of the dish in English",
      "confidence": 0.8,
      "ingredients": ["ingredient1", "ingredient2"],
      "estimated_weight_g": 150,
      "preparation": "boiled/fried/baked"
    }
  ],
  "total_items": 1,
  "notes": "additional context if needed"
}
Rules:
- Be specific: "grilled chicken breast", not just "chicken"
- If unsure, set confidence < 0.5
- For mixed dishes, list main ingredients
- Return ONLY the JSON, no other text
"""

def _bytes_to_array(image_bytes: bytes) -> list:
    """Конвертирует bytes в список целых чисел 0-255."""
    return list(image_bytes)

def _parse_json_response(text: str) -> Optional[List[Dict]]:
    """Извлекает JSON из ответа модели и возвращает список блюд с confidence >= 0.3."""
    # Ищем JSON-блок (может быть обёрнут в ```json ... ```)
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if not json_match:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        logger.warning("No JSON found in response")
        return None
    try:
        data = json.loads(json_match.group())
        dishes = data.get("dishes", [])
        # Фильтруем по confidence
        valid_dishes = [d for d in dishes if d.get("confidence", 0) >= 0.3]
        return valid_dishes
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return None

async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = FOOD_RECOGNITION_PROMPT,
    max_retries: int = 2
) -> Optional[List[Dict]]:
    """
    Распознаёт еду на изображении и возвращает список блюд с деталями на английском.
    Использует несколько моделей и повторные попытки.
    """
    if not BASE_URL:
        return None

    image_array = _bytes_to_array(image_bytes)
    payload = {
        "image": image_array,
        "prompt": prompt,
        "max_tokens": 300
    }
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    for model in VISION_MODELS:
        for attempt in range(max_retries):
            try:
                url = f"{BASE_URL}{model}"
                logger.info(f"Trying model {model}, attempt {attempt+1}")
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            description = result.get("result", {}).get("description", "")
                            if description:
                                dishes = _parse_json_response(description)
                                if dishes:
                                    logger.info(f"✅ Recognized {len(dishes)} dishes with model {model}")
                                    return dishes
                                else:
                                    logger.warning(f"Model {model} returned no valid dishes")
                        else:
                            error_text = await resp.text()
                            logger.warning(f"Model {model} attempt {attempt+1} failed: {resp.status} - {error_text[:200]}")
            except asyncio.TimeoutError:
                logger.warning(f"Model {model} attempt {attempt+1} timeout")
            except Exception as e:
                logger.warning(f"Model {model} attempt {attempt+1} exception: {e}")
            await asyncio.sleep(1 * (attempt + 1))  # exponential backoff
    logger.error("All models/attempts failed")
    return None
