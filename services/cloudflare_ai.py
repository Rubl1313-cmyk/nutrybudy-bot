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
    "@cf/microsoft/resnet-50",  # Быстрая классификация ImageNet
]

VISION_MODELS = [
    "@cf/llava-hf/llava-1.5-7b-hf",  # Fallback для сложных случаев
]

WHISPER_MODELS = [
    "@cf/openai/whisper",
    "@cf/openai/whisper-large-v3-turbo",
]

# Улучшенный промпт для LLaVA: просим конкретное название блюда
LLAVA_FALLBACK_PROMPT = """
Look at this image. If it contains a plate or bowl with food, describe the specific dish in English.
If it's a known salad like Caesar salad, Greek salad, etc., name it precisely.
If it's a main course, name it (e.g., 'Grilled chicken breast', 'Spaghetti bolognese').
Answer with the dish name only, no extra words.
Examples: 'Caesar salad', 'Grilled salmon', 'Vegetable soup'.
"""

def _bytes_to_array(image_bytes: bytes) -> list:
    """Конвертирует bytes в список целых чисел 0-255."""
    return list(image_bytes)

def _is_valid_food_label(label: str) -> bool:
    """Проверяет, что метка выглядит как еда (не шаблон и не посуда)."""
    if not label or len(label) < 3:
        return False
    label_lower = label.lower()
    # Исключаем посуду и не-еду
    non_food = ['person', 'people', 'man', 'woman', 'child', 'dog', 'cat', 
                'car', 'truck', 'building', 'house', 'animal', 'furniture',
                'plate', 'bowl', 'dish', 'cup', 'glass', 'fork', 'knife', 'spoon',
                'table', 'napkin']
    for item in non_food:
        if item in label_lower:
            return False
    return True

def _format_classification_result(api_result: Any) -> Optional[List[Dict]]:
    """
    Преобразует результат ResNet-50 в формат, ожидаемый media_handlers.
    Учитывает возможные варианты структуры ответа.
    """
    logger.info(f"Raw API result type: {type(api_result)}")
    logger.info(f"Raw API result preview: {str(api_result)[:200]}")
    
    if isinstance(api_result, dict) and 'result' in api_result:
        classes_data = api_result['result']
    else:
        classes_data = api_result
    
    if not isinstance(classes_data, list):
        logger.warning(f"Classes data is not a list: {type(classes_data)}")
        return None
    
    if not classes_data:
        logger.info("Empty classes list")
        return None
    
    first_item = classes_data[0]
    logger.info(f"First item type: {type(first_item)}")
    
    if isinstance(first_item, dict):
        confidence = first_item.get("score", 0)
        label = first_item.get("label", "")
    elif isinstance(first_item, (list, tuple)) and len(first_item) >= 2:
        label, confidence = first_item[0], first_item[1]
    else:
        logger.warning(f"Unexpected item format: {first_item}")
        return None
    
    # Если это посуда или не еда, считаем, что ResNet-50 не помог
    if not _is_valid_food_label(label):
        logger.info(f"Classification result is not food: {label} ({confidence})")
        return None
    
    if confidence < 0.3:
        logger.info(f"Classification confidence too low: {label} ({confidence})")
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
    Если ResNet-50 видит посуду, сразу переходим к LLaVA для описания блюда.
    Возвращает список блюд с деталями на английском.
    """
    if not BASE_URL:
        return None

    image_array = _bytes_to_array(image_bytes)
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # 1. Сначала пробуем ResNet-50 для классификации
    for model in CLASSIFICATION_MODELS:
        try:
            url = f"{BASE_URL}{model}"
            payload = {"image": image_array}
            
            logger.info(f"Trying classification model {model}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        logger.info(f"ResNet-50 raw response: {json.dumps(result)[:500]}")
                        
                        formatted = _format_classification_result(result)
                        if formatted:
                            logger.info(f"✅ ResNet-50 identified: {formatted[0]['name_en']}")
                            return formatted
                        else:
                            logger.info("ResNet-50 result rejected (non-food or low confidence)")
                    else:
                        logger.warning(f"ResNet-50 failed: {resp.status}")
        except Exception as e:
            logger.warning(f"Classification model {model} failed: {e}")
            continue

    # 2. Если ResNet-50 не дал результата, пробуем LLaVA с улучшенным промптом
    logger.info("Classification failed, falling back to LLaVA with enhanced prompt")
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
                            
                            if description and len(description) < 100:
                                # Фильтруем слишком общие ответы
                                if description.lower() in ["salad", "food", "dish", "plate"]:
                                    logger.info(f"LLaVA response too generic: {description}, retrying...")
                                    continue
                                logger.info(f"✅ LLaVA identified: {description}")
                                return [{
                                    "name_en": description,
                                    "confidence": 0.7,
                                    "ingredients": [],
                                    "estimated_weight_g": None,
                                    "preparation": None
                                }]
                            else:
                                logger.warning(f"LLaVA response invalid: {description}")
            except Exception as e:
                logger.warning(f"LLaVA attempt {attempt+1} failed: {e}")
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
