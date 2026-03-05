"""
Cloudflare Workers AI Integration для NutriBuddy
Улучшенная версия с поддержкой JSON, повторными попытками и перебором моделей.
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

# Модели для Whisper (голос)
WHISPER_MODELS = [
    "@cf/openai/whisper",                # базовая
    "@cf/openai/whisper-large-v3-turbo", # быстрая
]

# Промпт для распознавания блюда (JSON)
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
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if not json_match:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        logger.warning("No JSON found in response")
        return None
    try:
        data = json.loads(json_match.group())
        dishes = data.get("dishes", [])
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
            await asyncio.sleep(1 * (attempt + 1))
    logger.error("All models/attempts failed")
    return None

# =============================================================================
# 🎤 РАСПОЗНАВАНИЕ ГОЛОСА (WHISPER) – восстановлено из оригинального файла
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
                logger.info(f"🎤 Sending to {model} as JSON array")
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        headers=headers,
                        json=payload,
                        timeout=60
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "").strip()
                            if text:
                                logger.info(f"✅ Success: {text[:100]}...")
                                return text
                            else:
                                logger.warning("⚠️ Empty response")
                        else:
                            error_text = await resp.text()
                            logger.warning(f"⚠️ {model} failed {resp.status}: {error_text[:200]}")
            except Exception as e:
                logger.warning(f"⚠️ {model} error: {e}")
                continue

        logger.error("❌ All models failed")
        return None
    except Exception as e:
        logger.exception(f"💥 Critical error: {e}")
        return None
