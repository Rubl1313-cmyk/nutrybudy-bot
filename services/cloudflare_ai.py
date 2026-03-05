"""
Cloudflare Workers AI Integration для NutriBuddy
Использует ResNet-50 для классификации еды и LLaVA как fallback.
Все запросы на английском, ответы парсятся и затем переводятся.
Сохраняет функциональность распознавания голоса (transcribe_audio).
"""
import aiohttp
import os
import logging
import asyncio
import json
import re
import subprocess
import tempfile
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Модели в порядке приоритета
CLASSIFICATION_MODELS = [
    "@cf/microsoft/resnet-50",  # Быстрая классификация ImageNet [citation:1]
]

VISION_MODELS = [
    "@cf/llava-hf/llava-1.5-7b-hf",  # Fallback для сложных случаев [citation:4]
]

# Модели для Whisper (голос)
WHISPER_MODELS = [
    "@cf/openai/whisper",
    "@cf/openai/whisper-large-v3-turbo",
]

# Промпт для LLaVA (упрощённый, без примеров)
LLAVA_FALLBACK_PROMPT = """
What food is in this image? Answer with the name of the dish in English only, nothing else.
Example: "Caesar salad" or "Grilled chicken breast"
"""

def _bytes_to_array(image_bytes: bytes) -> list:
    """Конвертирует bytes в список целых чисел 0-255."""
    return list(image_bytes)

def _is_valid_food_label(label: str) -> bool:
    """Проверяет, что метка выглядит как еда (не шаблон)."""
    if not label or len(label) < 3:
        return False
    
    label_lower = label.lower()
    # Исключаем общие категории, не относящиеся к еде
    non_food = ['person', 'people', 'man', 'woman', 'child', 'dog', 'cat', 
                'car', 'truck', 'building', 'house', 'animal', 'furniture']
    
    for item in non_food:
        if item in label_lower:
            return False
    return True

def _format_classification_result(classes: List[Dict[str, Any]]) -> Optional[List[Dict]]:
    """
    Преобразует результат ResNet-50 в формат, ожидаемый media_handlers.
    """
    if not classes:
        return None
    
    # Берём топ-1 результат с достаточной уверенностью
    top_result = classes[0]
    confidence = top_result.get("score", 0)
    label = top_result.get("label", "")
    
    if confidence < 0.3 or not _is_valid_food_label(label):
        logger.info(f"Classification confidence too low or non-food: {label} ({confidence})")
        return None
    
    return [{
        "name_en": label,
        "confidence": confidence,
        "ingredients": [],
        "estimated_weight_g": None,
        "preparation": None
    }]

async def analyze_food_image(
    image_bytes: bytes,
    max_retries: int = 2
) -> Optional[List[Dict]]:
    """
    Распознаёт еду на изображении, используя ResNet-50 в приоритете.
    Возвращает список блюд с деталями на английском.
    """
    if not BASE_URL:
        return None

    image_array = _bytes_to_array(image_bytes)
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # 1. Сначала пробуем ResNet-50 для классификации [citation:1]
    for model in CLASSIFICATION_MODELS:
        try:
            url = f"{BASE_URL}{model}"
            payload = {"image": image_array}  # ResNet-50 не требует промпта [citation:1]
            
            logger.info(f"Trying classification model {model}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        classes = result.get("result", {}).get("classes", [])
                        
                        if classes:
                            formatted = _format_classification_result(classes)
                            if formatted:
                                logger.info(f"✅ ResNet-50 identified: {classes[0].get('label')} ({classes[0].get('score')})")
                                return formatted
                            else:
                                logger.info("ResNet-50 result rejected (low confidence or non-food)")
        except Exception as e:
            logger.warning(f"Classification model {model} failed: {e}")
            continue

    # 2. Если ResNet-50 не сработал, пробуем LLaVA [citation:4]
    logger.info("Classification failed, falling back to LLaVA")
    for model in VISION_MODELS:
        for attempt in range(max_retries):
            try:
                url = f"{BASE_URL}{model}"
                payload = {
                    "image": image_array,
                    "prompt": LLAVA_FALLBACK_PROMPT,
                    "max_tokens": 50
                }
                
                logger.info(f"Trying vision model {model}, attempt {attempt+1}")
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            description = result.get("result", {}).get("description", "").strip()
                            
                            if description and len(description) < 100 and not description.startswith("What food"):
                                logger.info(f"✅ LLaVA identified: {description}")
                                return [{
                                    "name_en": description,
                                    "confidence": 0.7,  # Условная уверенность
                                    "ingredients": [],
                                    "estimated_weight_g": None,
                                    "preparation": None
                                }]
                        else:
                            error_text = await resp.text()
                            logger.warning(f"Model {model} attempt {attempt+1} failed: {resp.status}")
            except asyncio.TimeoutError:
                logger.warning(f"Model {model} attempt {attempt+1} timeout")
            except Exception as e:
                logger.warning(f"Model {model} attempt {attempt+1} exception: {e}")
            await asyncio.sleep(1 * (attempt + 1))

    logger.error("All models failed to identify food")
    return None

# =============================================================================
# 🎤 РАСПОЗНАВАНИЕ ГОЛОСА (WHISPER)
# =============================================================================

async def _convert_ogg_to_wav(ogg_bytes: bytes) -> Optional[bytes]:
    """Конвертирует OGG (Opus) в WAV (16-bit PCM, 16kHz, mono)."""
    try:
        if len(ogg_bytes) > 20 * 1024 * 1024:
            logger.warning(f"⚠️ Audio too large: {len(ogg_bytes)/1024/1024:.1f} MB")
            return None

        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f_in:
            f_in.write(ogg_bytes)
            in_path = f_in.name

        out_path = in_path.replace('.ogg', '.wav')

        try:
            cmd = [
                'ffmpeg', '-i', in_path,
                '-ar', '16000',
                '-ac', '1',
                '-acodec', 'pcm_s16le',
                '-y', out_path
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"❌ ffmpeg error: {stderr.decode()[:200]}")
                return None

            with open(out_path, 'rb') as f:
                wav_bytes = f.read()
            logger.info(f"✅ Conversion successful: {len(wav_bytes)} bytes")
            return wav_bytes

        finally:
            try:
                os.unlink(in_path)
                if os.path.exists(out_path):
                    os.unlink(out_path)
            except:
                pass
    except Exception as e:
        logger.exception(f"💥 Conversion error: {e}")
        return None

async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """Распознавание голоса через Cloudflare Whisper."""
    try:
        if not BASE_URL:
            return None

        file_size = len(audio_bytes)
        logger.info(f"🎤 Original size: {file_size/1024:.1f} KB")

        if file_size > 20 * 1024 * 1024:
            logger.warning("⚠️ Audio too large (>20MB)")
            return None

        wav_bytes = await _convert_ogg_to_wav(audio_bytes)
        if not wav_bytes:
            return None

        audio_array = list(wav_bytes)
        logger.info(f"📊 Audio array size: {len(audio_array)} samples")

        payload = {"audio": audio_array}
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        for model in WHISPER_MODELS:
            try:
                url = f"{BASE_URL}{model}"
                logger.info(f"🎤 Sending to {model}")
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "").strip()
                            if text:
                                logger.info(f"✅ Success: {text[:100]}...")
                                return text
                        else:
                            error_text = await resp.text()
                            logger.warning(f"⚠️ {model} failed {resp.status}")
            except Exception as e:
                logger.warning(f"⚠️ {model} error: {e}")
                continue

        logger.error("❌ All models failed")
        return None
    except Exception as e:
        logger.exception(f"💥 Critical error: {e}")
        return None
