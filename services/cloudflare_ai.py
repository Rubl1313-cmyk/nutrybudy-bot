"""
Cloudflare Workers AI Integration для NutriBuddy.
Поддержка анализа изображений и распознавания речи.
"""
import aiohttp
import os
import base64
import logging
from typing import Optional, Dict, List
from PIL import Image
import io

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Доступные модели (из скриншота)
WHISPER_MODELS = [
    "@cf/openai/whisper",                # базовая модель
    "@cf/openai/whisper-large-v3-turbo", # быстрая версия
    "@cf/openai/whisper-tiny-en",        # маленькая английская
]


def _bytes_to_array(image_bytes: bytes) -> List[int]:
    """Конвертирует bytes в список целых чисел 0-255"""
    return list(image_bytes)


async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "What food is in this image? Describe briefly in Russian.",
    max_tokens: int = 150
) -> Optional[str]:
    """Анализирует изображение еды через Cloudflare Vision."""
    try:
        if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
            logger.error("❌ Cloudflare credentials not set")
            return None
        
        # Конвертируем в массив байтов
        image_array = _bytes_to_array(image_bytes)
        logger.info(f"📊 Image converted: {len(image_array)} bytes → array")
        
        payload = {
            "image": image_array,
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Используем модель для анализа изображений
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
                    description = result.get("result", {}).get("description", "")
                    if description:
                        logger.info(f"✅ Vision success: {description[:100]}...")
                        return description.strip()
                    logger.warning("⚠️ Empty description")
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Vision API error {resp.status}: {error_text[:300]}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 analyze_food_image error: {e}")
        return None


async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    try:
        from aiohttp import FormData

        # Логируем размер файла
        file_size = len(audio_bytes)
        logger.info(f"🎤 Audio file size: {file_size / 1024 / 1024:.2f} MB")

        # Проверка размера (лимит Whisper ~25MB, но для надёжности 20MB)
        if file_size > 20 * 1024 * 1024:
            logger.warning("Audio file too large (>20MB), skipping")
            return None

        for model in WHISPER_MODELS:
            try:
                # Создаём НОВЫЙ FormData для каждой попытки
                data = FormData()
                data.add_field('file', audio_bytes, filename='voice.ogg', content_type='audio/ogg')

                url = f"{BASE_URL}{model}"
                headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}

                logger.info(f"🎤 Sending to {model}, size: {file_size} bytes")

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=data, timeout=60) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "")
                            if text:
                                logger.info(f"✅ Whisper success with {model}: {text[:100]}...")
                                return text.strip()
                        else:
                            error_text = await resp.text()
                            logger.warning(f"❌ Model {model} failed: {resp.status} - {error_text[:200]}")
            except Exception as e:
                logger.warning(f"⚠️ Exception with {model}: {e}")
                continue

        logger.error("❌ All Whisper models failed")
        return None
    except Exception as e:
        logger.exception(f"💥 Critical error in transcribe_audio: {e}")
        return None
