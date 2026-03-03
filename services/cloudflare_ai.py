"""
Cloudflare Workers AI Integration для NutriBuddy
✅ Полный набор функций:
- Распознавание голоса (Whisper) с автоматической конвертацией OGG → WAV
- Анализ изображений еды (Vision)
- Генерация текста (LLM)
"""

import aiohttp
import os
import logging
import subprocess
import asyncio
import tempfile
from typing import Optional, List

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# 🔥 Модели
WHISPER_MODELS = [
    "@cf/openai/whisper",                # базовая
    "@cf/openai/whisper-large-v3-turbo", # быстрая
]

VISION_MODELS = [
    "@cf/unum/uform-gen2-qwen-500m",     # анализ изображений
    "@cf/llava-hf/llava-1.5-7b-hf",      # альтернатива
]

LLM_MODELS = {
    "llama3": "@cf/meta/llama-3-8b-instruct",
    "llama3.1": "@cf/meta/llama-3.1-8b-instruct",
    "mistral": "@cf/mistral/mistral-7b-instruct-v0.1",
    "qwen": "@cf/qwen/qwen1.5-7b-chat-awq",
}


# =============================================================================
# 🔧 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def _bytes_to_array(image_bytes: bytes) -> List[int]:
    """Конвертирует bytes в список целых чисел 0-255 (для Vision API)"""
    return list(image_bytes)


async def _convert_ogg_to_wav(ogg_bytes: bytes) -> Optional[bytes]:
    """
    Конвертирует OGG (Opus) в WAV (16-bit PCM, 16kHz, mono).
    Требует ffmpeg в системе.
    """
    try:
        if len(ogg_bytes) > 20 * 1024 * 1024:  # лимит Telegram
            logger.warning(f"⚠️ Audio too large: {len(ogg_bytes)/1024/1024:.1f} MB")
            return None

        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f_in:
            f_in.write(ogg_bytes)
            in_path = f_in.name

        out_path = in_path.replace('.ogg', '.wav')

        try:
            cmd = [
                'ffmpeg', '-i', in_path,
                '-ar', '16000',      # 16 kHz
                '-ac', '1',           # mono
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-y',                 # перезаписать
                out_path
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


# =============================================================================
# 🎤 РАСПОЗНАВАНИЕ ГОЛОСА (WHISPER)
# =============================================================================

async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """
    Распознавание голоса через Cloudflare Whisper.
    🔥 Автоматически приводит аудио к нужному формату.
    """
    try:
        if not BASE_URL:
            return None

        logger.info(f"🎤 Original size: {len(audio_bytes)/1024:.1f} KB")

        wav_bytes = await _convert_ogg_to_wav(audio_bytes)
        if not wav_bytes:
            logger.error("❌ Failed to convert audio")
            return None

        for model in WHISPER_MODELS:
            try:
                form = aiohttp.FormData()
                form.add_field(
                    'file',
                    wav_bytes,
                    filename='audio.wav',
                    content_type='audio/wav'
                )

                headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
                url = f"{BASE_URL}{model}"

                logger.info(f"🎤 Sending to {model}")

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        headers=headers,
                        data=form,
                        timeout=aiohttp.ClientTimeout(total=60)
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


# =============================================================================
# 📸 АНАЛИЗ ИЗОБРАЖЕНИЙ (VISION)
# =============================================================================

async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "Describe the food in this image briefly in Russian.",
    max_tokens: int = 150
) -> Optional[str]:
    """
    Анализирует изображение еды через Cloudflare Vision API.
    """
    try:
        if not BASE_URL:
            return None

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
                    async with session.post(
                        url,
                        headers=headers,
                        json=payload,
                        timeout=30
                    ) as resp:

                        if resp.status == 200:
                            result = await resp.json()
                            description = result.get("result", {}).get("description", "")
                            if description and 5 < len(description.strip()) < 500:
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


# =============================================================================
# 🧠 ГЕНЕРАЦИЯ ТЕКСТА (LLM)
# =============================================================================

async def generate_text(
    prompt: str,
    system_prompt: str = "Ты полезный ассистент. Отвечай на русском.",
    model: str = "llama3",
    max_tokens: int = 500,
    temperature: float = 0.7
) -> Optional[str]:
    """
    Генерация текста через Cloudflare LLM (например, Llama 3).
    """
    try:
        if not BASE_URL:
            return None

        model_id = LLM_MODELS.get(model, LLM_MODELS["llama3"])

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        url = f"{BASE_URL}{model_id}"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            ) as resp:

                if resp.status == 200:
                    result = await resp.json()
                    text = result.get("result", {}).get("response", "")
                    if text and len(text.strip()) > 10:
                        logger.info(f"✅ LLM success: {text[:100]}...")
                        return text.strip()
                else:
                    error_text = await resp.text()
                    logger.warning(f"⚠️ LLM error {resp.status}: {error_text[:200]}")

        return None

    except Exception as e:
        logger.exception(f"💥 generate_text error: {e}")
        return None
