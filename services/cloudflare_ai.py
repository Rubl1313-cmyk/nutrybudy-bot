"""
Cloudflare Workers AI Integration для NutriBuddy
Исправленная версия с поддержкой разных форматов изображений
"""

import aiohttp
import os
import base64
import logging
from typing import Optional, Dict
from PIL import Image
import io

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# 🔥 Альтернативные модели для анализа изображений
VISION_MODELS = [
    "@cf/llava-hf/llava-1.5-7b-hf",      # Более стабильная модель
    "@cf/unum/uform-gen2-qwen-500m",     # Оригинальная (проблемная)
    "@cf/meta/llama-3.2-11b-vision-instruct",  # Новая модель с vision
]


async def _prepare_image(image_bytes: bytes) -> tuple[str, str]:
    """
    Конвертирует изображение в совместимый формат.
    Returns: (base64_string, mime_type)
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Конвертируем в RGB для совместимости
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Сохраняем в JPEG с оптимизацией
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
        img_byte_arr.seek(0)
        
        # Кодируем в base64
        image_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        return image_base64, 'image/jpeg'
        
    except Exception as e:
        logger.error(f"Image preparation error: {e}")
        # Fallback: попробуем исходные байты
        return base64.b64encode(image_bytes).decode('utf-8'), 'image/jpeg'


async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "Опиши еду на этом изображении. Укажи название блюда и основные ингредиенты. Отвечай кратко на русском.",
    max_tokens: int = 200
) -> Optional[str]:
    """
    Анализирует изображение еды через Cloudflare AI с fallback на другие модели.
    """
    try:
        image_base64, mime_type = await _prepare_image(image_bytes)
        logger.info(f"📊 Prepared image: {len(image_base64)} chars base64, mime: {mime_type}")
        
        # 🔁 Пробуем модели по очереди
        for model in VISION_MODELS:
            try:
                logger.info(f"🔄 Trying model: {model}")
                
                # Формат payload зависит от модели
                if "llava" in model or "vision" in model:
                    # Модели с поддержкой vision через messages API
                    payload = {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {
                                        "url": f"data:{mime_type};base64,{image_base64}"
                                    }}
                                ]
                            }
                        ],
                        "max_tokens": max_tokens
                    }
                    endpoint = model
                else:
                    # Старый формат для UForm-Gen2
                    payload = {
                        "image": image_base64,
                        "prompt": prompt,
                        "max_tokens": max_tokens
                    }
                    endpoint = model
                
                headers = {
                    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
                    "Content-Type": "application/json"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{BASE_URL}{endpoint}",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        
                        logger.info(f"📥 {model} response: {resp.status}")
                        
                        if resp.status == 200:
                            result = await resp.json()
                            
                            # Разные форматы ответов
                            if "result" in result:
                                # UForm-Gen2 формат
                                description = result["result"].get("description", "")
                            elif "response" in result.get("result", {}):
                                # Llama формат
                                description = result["result"]["response"]
                            elif "choices" in result:
                                # OpenAI-совместимый формат
                                description = result["choices"][0]["message"]["content"]
                            else:
                                description = str(result)
                            
                            if description and len(description.strip()) > 10:
                                logger.info(f"✅ Success with {model}: {description[:100]}...")
                                return description.strip()
                        
                        # Если ошибка - пробуем следующую модель
                        error_text = await resp.text()
                        logger.warning(f"⚠️ {model} failed: {resp.status} - {error_text[:200]}")
                        
            except Exception as model_error:
                logger.warning(f"⚠️ Model {model} exception: {model_error}")
                continue
        
        # Все модели не сработали
        logger.error("❌ All vision models failed")
        return None
        
    except Exception as e:
        logger.exception(f"💥 analyze_food_image critical error: {e}")
        return None


async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """Распознавание речи через Whisper"""
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
    """Генерация рецепта через Llama 3"""
    prompt = f"""Ты — шеф-повар. Составь рецепт блюда из: {ingredients}.
Формат: 1) Название 2) Ингредиенты с количеством 3) Пошаговое приготовление 4) КБЖУ на порцию.
Отвечай на русском, используй эмодзи."""

    payload = {
        "messages": [
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
                    recipe = result.get("result", {}).get("response", "")
                    if recipe:
                        logger.info(f"✅ Recipe generated: {len(recipe)} chars")
                        return recipe
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Recipe error {resp.status}: {error_text}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 generate_recipe error: {e}")
        return None
