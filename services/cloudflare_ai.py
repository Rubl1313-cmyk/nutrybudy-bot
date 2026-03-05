"""
Cloudflare Workers AI Integration для NutriBuddy
Содержит:
- identify_dish_from_image: распознавание названия блюда (LLaVA)
- analyze_food_image: распознавание ингредиентов (старый метод, для fallback)
- transcribe_audio: распознавание голоса
"""
import aiohttp
import os
import logging
import asyncio
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

# Модели
VISION_MODELS = [
    "@cf/llava-hf/llava-1.5-7b-hf",
    "@cf/unum/uform-gen2-qwen-500m",
]

WHISPER_MODELS = [
    "@cf/openai/whisper",
    "@cf/openai/whisper-large-v3-turbo",
]

def _bytes_to_array(image_bytes: bytes) -> list:
    return list(image_bytes)

async def identify_dish_from_image(image_bytes: bytes) -> Optional[str]:
    if not BASE_URL:
        return None

    image_array = _bytes_to_array(image_bytes)
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Максимально простой и короткий промпт
    prompt = (
        "Identify the specific dish in this image. If it's a salad, name its type (e.g., 'Caesar salad', 'Greek salad', 'Salmon salad'). "
        "If it's a main course, name it precisely (e.g., 'Grilled chicken breast', 'Roast beef'). "
        "Answer with only the dish name, nothing else."
    )

    for model in VISION_MODELS:
        try:
            url = f"{BASE_URL}{model}"
            payload = {
                "image": image_array,
                "prompt": prompt,
                "max_tokens": 50,
                "temperature": 0.1
            }
            logger.info(f"Trying vision model {model} for dish name")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        description = result.get("result", {}).get("description", "").strip()
                        # Простейшая валидация
                        if description and len(description) < 100:
                            logger.info(f"✅ Model {model} identified dish: {description}")
                            return description
                        else:
                            logger.warning(f"Model {model} returned invalid: {description}")
                    else:
                        logger.warning(f"Model {model} failed with status {resp.status}")
        except Exception as e:
            logger.warning(f"Model {model} error: {e}")
            continue

    logger.error("All vision models failed to identify dish")
    return None
    
async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "List all food items visible in this image. Be specific. Return as a comma-separated list.",
    max_retries: int = 2
) -> Optional[str]:
    """
    Анализирует изображение и возвращает текстовое описание (например, список ингредиентов).
    Используется для fallback, когда нужно получить ингредиенты.
    """
    if not BASE_URL:
        return None

    image_array = _bytes_to_array(image_bytes)
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    for model in VISION_MODELS:
        for attempt in range(max_retries):
            try:
                url = f"{BASE_URL}{model}"
                payload = {
                    "image": image_array,
                    "prompt": prompt,
                    "max_tokens": 150,
                    "temperature": 0.3
                }
                logger.info(f"Trying vision model {model}, attempt {attempt+1}")
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            description = result.get("result", {}).get("description", "").strip()
                            if description:
                                logger.info(f"✅ Model {model} returned description")
                                return description
            except Exception as e:
                logger.warning(f"Model {model} attempt {attempt+1} failed: {e}")
            await asyncio.sleep(1)
    logger.error("All models failed to analyze food image")
    return None

# =============================================================================
# 🎤 РАСПОЗНАВАНИЕ ГОЛОСА (WHISPER)
# =============================================================================

async def _convert_ogg_to_wav(ogg_bytes: bytes) -> Optional[bytes]:
    """Конвертирует OGG в WAV."""
    try:
        if len(ogg_bytes) > 20 * 1024 * 1024:
            return None
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f_in:
            f_in.write(ogg_bytes)
            in_path = f_in.name
        out_path = in_path.replace('.ogg', '.wav')
        try:
            cmd = ['ffmpeg', '-i', in_path, '-ar', '16000', '-ac', '1', '-acodec', 'pcm_s16le', '-y', out_path]
            process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await process.communicate()
            if process.returncode != 0:
                return None
            with open(out_path, 'rb') as f:
                return f.read()
        finally:
            try:
                os.unlink(in_path)
                if os.path.exists(out_path):
                    os.unlink(out_path)
            except:
                pass
    except Exception as e:
        logger.exception(f"Conversion error: {e}")
        return None

async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """Распознавание голоса через Cloudflare Whisper."""
    if not BASE_URL:
        return None
    try:
        wav_bytes = await _convert_ogg_to_wav(audio_bytes)
        if not wav_bytes:
            return None
        audio_array = list(wav_bytes)
        payload = {"audio": audio_array, "language": language}
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"}
        for model in WHISPER_MODELS:
            try:
                url = f"{BASE_URL}{model}"
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "").strip()
                            if text:
                                return text
            except Exception:
                continue
        return None
    except Exception as e:
        logger.exception(f"Transcription error: {e}")
        return None
