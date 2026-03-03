"""
Cloudflare Workers AI Integration для NutriBuddy.
✅ Поддержка конвертации аудио через ffmpeg (если доступен)
✅ Проверка учётных данных
✅ Стабильные модели
"""
import aiohttp
import os
import logging
from typing import Optional, List
import tempfile
import subprocess

logger = logging.getLogger(__name__)

# Проверка наличия ffmpeg в системе
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except:
        return False

FFMPEG_AVAILABLE = check_ffmpeg()
if not FFMPEG_AVAILABLE:
    logger.warning("⚠️ ffmpeg not found in system — audio conversion may fail")

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set — AI functions will fail")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Стабильные Whisper-модели (проверены)
WHISPER_MODELS = [
    "@cf/openai/whisper",               # базовая, поддерживает русский
    "@cf/openai/whisper-large-v3",       # более точная
]

# Модели для анализа изображений
VISION_MODELS = [
    "@cf/unum/uform-gen2-qwen-500m",
    "@cf/llava-hf/llava-1.5-7b-hf",
]

def _bytes_to_array(image_bytes: bytes) -> List[int]:
    return list(image_bytes)

async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "Describe the food in this image briefly in Russian.",
    max_tokens: int = 150
) -> Optional[str]:
    if not BASE_URL:
        logger.error("❌ Cloudflare credentials not set")
        return None
    try:
        image_array = _bytes_to_array(image_bytes)
        payload = {
            "image": image_array,
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        for model in VISION_MODELS:
            try:
                url = f"{BASE_URL}{model}"
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            description = result.get("result", {}).get("description", "")
                            if description and len(description.strip()) > 5:
                                logger.info(f"✅ Vision success ({model}): {description[:100]}...")
                                return description.strip()
                        else:
                            error_text = await resp.text()
                            logger.warning(f"⚠️ {model} failed {resp.status}: {error_text[:200]}")
            except Exception as e:
                logger.warning(f"⚠️ {model} exception: {e}")
                continue
        logger.error("❌ All vision models failed")
        return None
    except Exception as e:
        logger.exception(f"💥 analyze_food_image error: {e}")
        return None

async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    if not BASE_URL:
        logger.error("❌ Cloudflare credentials not set")
        return None
    try:
        file_size = len(audio_bytes)
        logger.info(f"🎤 Audio size: {file_size / 1024:.1f} KB")

        if file_size > 20 * 1024 * 1024:
            logger.warning("⚠️ Audio too large (>20MB)")
            return None

        # Конвертируем аудио в WAV (16kHz, mono) если доступен ffmpeg
        processed_bytes = audio_bytes
        if FFMPEG_AVAILABLE:
            try:
                import ffmpeg
                with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f_in:
                    f_in.write(audio_bytes)
                    in_path = f_in.name
                out_path = in_path.replace('.ogg', '.wav')
                try:
                    logger.info("🎧 Converting audio to WAV (16kHz, mono)")
                    ffmpeg.input(in_path).output(
                        out_path,
                        acodec='pcm_s16le',
                        ar='16000',
                        ac=1
                    ).run(quiet=True, overwrite_output=True)
                    with open(out_path, 'rb') as f:
                        processed_bytes = f.read()
                    logger.info("✅ Conversion successful")
                finally:
                    if os.path.exists(in_path):
                        os.unlink(in_path)
                    if os.path.exists(out_path):
                        os.unlink(out_path)
            except Exception as conv_error:
                logger.warning(f"⚠️ Audio conversion failed: {conv_error}, using original")
        else:
            logger.info("🎧 ffmpeg not available, sending original audio")

        # Пробуем модели Whisper
        for model in WHISPER_MODELS:
            try:
                from aiohttp import FormData
                data = FormData()
                # Определяем MIME-тип
                if processed_bytes != audio_bytes:
                    content_type = 'audio/wav'
                    filename = 'audio.wav'
                else:
                    content_type = 'audio/ogg'
                    filename = 'audio.ogg'
                data.add_field('file', processed_bytes, filename=filename, content_type=content_type)

                url = f"{BASE_URL}{model}"
                headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=data, timeout=60) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "").strip()
                            if text:
                                logger.info(f"✅ Whisper success ({model}): {text[:100]}...")
                                return text
                        else:
                            error_text = await resp.text()
                            logger.warning(f"⚠️ {model} failed {resp.status}: {error_text[:200]}")
            except Exception as e:
                logger.warning(f"⚠️ {model} exception: {e}")
                continue

        logger.error("❌ All Whisper models failed")
        return None
    except Exception as e:
        logger.exception(f"💥 transcribe_audio error: {e}")
        return None
