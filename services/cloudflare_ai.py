"""
Cloudflare Workers AI Integration для NutriBuddy
Поддерживает:
- Анализ изображений еды (UForm-Gen2)
- Распознавание голоса (Whisper)
- Генерация рецептов (Llama 3)
"""

import aiohttp
import os
import base64
import logging
from typing import Optional, Dict, List
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Настройки из переменных окружения
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

# Базовый URL API
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Доступные модели
MODELS = {
    "vision": "@cf/unum/uform-gen2-qwen-500m",      # Анализ изображений
    "whisper": "@openai/whisper",                    # Распознавание речи
    "llama3": "@cf/meta/llama-3-8b-instruct",        # Генерация текста/рецептов
}


class CloudflareAIError(Exception):
    """Кастомное исключение для ошибок Cloudflare AI"""
    pass


async def _make_request(model: str, payload: Dict, use_form: bool = False) -> Optional[Dict]:
    """Внутренняя функция для HTTP-запросов к Cloudflare AI"""
    
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        logger.error("❌ Cloudflare credentials not set")
        raise CloudflareAIError("Cloudflare API credentials not configured")
    
    url = f"{BASE_URL}{model}"
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            if use_form:
                from aiohttp import FormData
                data = FormData()
                for key, value in payload.items():
                    data.add_field(key, value)
                async with session.post(url, headers=headers, data=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    return await _process_response(resp)
            else:
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    return await _process_response(resp)
        except aiohttp.ClientError as e:
            logger.error(f"🌐 Network error: {e}")
            raise CloudflareAIError(f"Network error: {e}")
        except Exception as e:
            logger.exception(f"💥 Unexpected error: {e}")
            raise CloudflareAIError(f"Unexpected error: {e}")


async def _process_response(resp: aiohttp.ClientResponse) -> Optional[Dict]:
    """Обработка ответа от API"""
    if resp.status == 200:
        return await resp.json()
    
    error_text = await resp.text()
    if resp.status == 401:
        logger.error("🔐 Authentication failed - check your API token")
    elif resp.status == 403:
        logger.error("🚫 Access denied - check account ID and permissions")
    elif resp.status == 429:
        logger.error("⏱️ Rate limit exceeded - try again later")
    elif resp.status >= 500:
        logger.error(f"🔧 Server error {resp.status}: {error_text}")
    else:
        logger.error(f"❌ API error {resp.status}: {error_text}")
    return None


# =============================================================================
# 🔍 АНАЛИЗ ИЗОБРАЖЕНИЙ (UForm-Gen2) — С ОБРАБОТКОЙ ЧЕРЕZ PILLOW
# =============================================================================

async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "Опиши еду на этом изображении. Укажи название блюда и основные ингредиенты. Отвечай кратко на русском.",
    max_tokens: int = 200
) -> Optional[str]:
    """
    Анализирует изображение еды и возвращает текстовое описание.
    Конвертирует изображение в совместимый JPEG формат.
    """
    try:
        # Открываем изображение через Pillow
        img = Image.open(io.BytesIO(image_bytes))
        
        # Конвертируем в RGB (убираем альфа-канал для совместимости)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Сохраняем в JPEG с оптимизацией
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
        img_byte_arr.seek(0)
        
        # Проверяем размер (лимит Cloudflare ~4MB)
        image_size = len(img_byte_arr.getvalue())
        logger.info(f"📊 Image size: {image_size / 1024 / 1024:.2f} MB")
        
        # Если слишком большое — уменьшаем
        if image_size > 4 * 1024 * 1024:
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=75, optimize=True)
            img_byte_arr.seek(0)
            logger.info("📉 Image resized to fit Cloudflare limits")
        
        # Конвертируем в base64
        image_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        payload = {
            "image": image_base64,
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        logger.info(f"📤 Sending image to Cloudflare Vision AI")
        
        result = await _make_request(MODELS["vision"], payload)
        
        if result and "result" in result:
            description = result["result"].get("description", "")
            if description:
                logger.info(f"✅ Vision AI result: {description[:100]}...")
                return description
            logger.warning("⚠️ Empty description in response")
            return None
        
        logger.warning("⚠️ Empty or invalid response from Vision AI")
        return None
        
    except CloudflareAIError as e:
        logger.error(f"❌ Vision AI error: {e}")
        return None
    except Exception as e:
        logger.exception(f"💥 Unexpected error in analyze_food_image: {e}")
        return None


# =============================================================================
# 🎤 РАСПОЗНАВАНИЕ ГОЛОСА (Whisper)
# =============================================================================

async def transcribe_audio(
    audio_bytes: bytes,
    language: str = "ru",
    temperature: float = 0.0
) -> Optional[str]:
    """
    Распознаёт речь в аудиофайле и возвращает текст.
    Аудио должно быть в формате .ogg (как отправляет Telegram).
    """
    try:
        from aiohttp import FormData
        
        data = FormData()
        data.add_field('file', audio_bytes, filename='voice.ogg', content_type='audio/ogg')
        data.add_field('model', 'whisper')
        data.add_field('language', language)
        data.add_field('temperature', str(temperature))
        
        logger.info(f"🎤 Sending audio to Whisper ({len(audio_bytes)} bytes)")
        
        url = f"{BASE_URL}{MODELS['whisper']}"
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    text = result.get("result", {}).get("text", "")
                    logger.info(f"✅ Whisper result: {text[:100]}...")
                    return text
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Whisper error {resp.status}: {error_text}")
                    return None
                    
    except CloudflareAIError as e:
        logger.error(f"❌ Whisper error: {e}")
        return None
    except Exception as e:
        logger.exception(f"💥 Unexpected error in transcribe_audio: {e}")
        return None


# =============================================================================
# 🧠 ГЕНЕРАЦИЯ РЕЦЕПТОВ (Llama 3)
# =============================================================================

async def generate_recipe(
    ingredients: str,
    diet_type: str = "обычное",
    difficulty: str = "средняя",
    max_tokens: int = 800
) -> Optional[str]:
    """
    Генерирует подробный рецепт на основе ингредиентов через Llama 3.
    """
    prompt = f"""Ты — профессиональный шеф-повар и нутрициолог.
Составь подробный рецепт блюда на русском языке.

🥘 Ингредиенты: {ingredients}
🥗 Тип питания: {diet_type}
👨‍🍳 Сложность: {difficulty}

📋 Формат ответа:
1. 🍽️ Название блюда
2. ⏱️ Время приготовления и сложность
3. 🛒 Ингредиенты с точными количествами
4. 👨‍🍳 Пошаговое приготовление (нумерованный список)
5. 📊 КБЖУ на порцию (калории, белки, жиры, углеводы)
6. 💡 Советы по подаче и хранению

Отвечай структурированно, используй эмодзи для наглядности."""

    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    logger.info(f"🧠 Generating recipe for: {ingredients[:50]}...")
    
    try:
        result = await _make_request(MODELS["llama3"], payload)
        
        if result and "result" in result:
            recipe = result["result"].get("response", "")
            if recipe:
                logger.info(f"✅ Recipe generated ({len(recipe)} chars)")
                return recipe
        
        logger.warning("⚠️ Empty response from LLM")
        return None
        
    except CloudflareAIError as e:
        logger.error(f"❌ Recipe generation error: {e}")
        return None
    except Exception as e:
        logger.exception(f"💥 Unexpected error in generate_recipe: {e}")
        return None


# =============================================================================
# 🔧 УТИЛИТЫ
# =============================================================================

async def check_api_health() -> Dict[str, bool]:
    """Проверяет доступность всех моделей Cloudflare AI."""
    results = {}
    async with aiohttp.ClientSession() as session:
        for name, model in MODELS.items():
            url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/models/{model.split('/')[-1]}"
            headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    results[name] = resp.status == 200
            except:
                results[name] = False
    return results
