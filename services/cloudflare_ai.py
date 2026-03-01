"""
Cloudflare Workers AI Integration — ИСПРАВЛЕННАЯ ВЕРСИЯ
Ключевое: image отправляется как array of bytes (List[int]), НЕ base64!
"""

import aiohttp
import os
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"


def _bytes_to_array(image_bytes: bytes) -> List[int]:
    """Конвертирует bytes в список целых чисел 0-255 для Cloudflare AI"""
    return list(image_bytes)


async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "Опиши еду на этом изображении. Укажи название блюда и основные ингредиенты. Отвечай кратко на русском.",
    max_tokens: int = 200
) -> Optional[str]:
    """
    Анализирует изображение через Cloudflare Vision AI.
    
    🔑 КЛЮЧЕВОЕ: image отправляется как array of bytes, НЕ base64!
    Документация: https://developers.cloudflare.com/workers-ai/models/uform-gen2-qwen-500m/
    """
    try:
        # 🔥 Конвертируем bytes → array of integers 0-255
        image_array = _bytes_to_array(image_bytes)
        logger.info(f"📊 Image converted: {len(image_array)} bytes → array")
        
        # Формат payload для UForm-Gen2
        payload = {
            "image": image_array,  # ← МАССИВ, не base64!
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        model = "@cf/unum/uform-gen2-qwen-500m"
        url = f"{BASE_URL}{model}"
        
        logger.info(f"📤 Sending to {model}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                
                logger.info(f"📥 Response: {resp.status}")
                
                if resp.status == 200:
                    result = await resp.json()
                    # UForm-Gen2 возвращает {"result": {"description": "..."}}
                    description = result.get("result", {}).get("description", "")
                    if description and len(description.strip()) > 10:
                        logger.info(f"✅ Success: {description[:100]}...")
                        return description.strip()
                    logger.warning("⚠️ Empty description in response")
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ API error {resp.status}: {error_text[:300]}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 analyze_food_image error: {e}")
        return None


async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """
    Распознавание речи через Whisper.
    Здесь формат не менялся — отправляем как multipart/form-data.
    """
    try:
        from aiohttp import FormData
        
        data = FormData()
        data.add_field('file', audio_bytes, filename='voice.ogg', content_type='audio/ogg')
        
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}@openai/whisper",
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                
                if resp.status == 200:
                    result = await resp.json()
                    text = result.get("result", {}).get("text", "")
                    logger.info(f"✅ Whisper: {text[:100]}...")
                    return text
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Whisper error {resp.status}: {error_text}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 transcribe_audio error: {e}")
        return None


async def generate_recipe(ingredients: str, max_tokens: int = 800) -> Optional[str]:
    """
    Генерация рецепта через Llama 3 (текстовая модель).
    Здесь используем messages API.
    """
    prompt = f"""Ты — шеф-повар. Составь подробный рецепт блюда из: {ingredients}.

Формат:
1. 🍽️ Название
2. 🛒 Ингредиенты с количеством
3. 👨‍🍳 Пошаговое приготовление
4. 📊 КБЖУ на порцию

Отвечай на русском, используй эмодзи."""

    payload = {
        "messages": [  # ← Llama 3 требует messages array
            {"role": "system", "content": "Ты полезный ассистент-повар."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}@cf/meta/llama-3-8b-instruct",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=45)
            ) as resp:
                
                if resp.status == 200:
                    result = await resp.json()
                    # Llama 3 возвращает {"result": {"response": "..."}}
                    recipe = result.get("result", {}).get("response", "")
                    if recipe:
                        logger.info(f"✅ Recipe: {len(recipe)} chars")
                        return recipe
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Recipe error {resp.status}: {error_text[:300]}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 generate_recipe error: {e}")
        return None
