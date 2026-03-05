"""
Cloudflare Workers AI Integration for NutriBuddy
Расширено: identify_food_multimodel с валидацией и возвратом модели.
Всегда возвращает кортеж (dict|None, str|None)
"""
import aiohttp
import os
import logging
import asyncio
import json
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Модели (порядок важен: сначала LLaVA, потом UForm)
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

def _extract_json_from_text(text: str) -> Optional[Dict]:
    """Извлекает JSON из текста, удаляя возможные экранирования."""
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return None
    json_str = text[start:end+1]
    # Удаляем экранирование перед подчеркиванием и кавычками
    json_str = json_str.replace('\\_', '_').replace('\\"', '"')
    try:
        data = json.loads(json_str)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None

def _validate_food_data(data: Dict) -> bool:
    """Проверяет, что распознанные данные выглядят правдоподобно."""
    if not isinstance(data, dict):
        return False
    dish = data.get('dish_name', '')
    ingredients = data.get('ingredients', [])
    if not dish or len(dish) < 3:
        return False
    if not isinstance(ingredients, list) or len(ingredients) < 1:
        return False
    # Проверка на чрезмерные повторы
    unique_ingredients = set(ingredients)
    if len(unique_ingredients) < len(ingredients) * 0.5:
        logger.warning(f"Validation failed: too many repeats in ingredients: {ingredients}")
        return False
    return True

async def identify_food_multimodel(
    image_bytes: bytes,
    prompt: str = None,
    max_tokens: int = 300,
    temperature: float = 0.0
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Пробует несколько vision-моделей для распознавания еды.
    Возвращает (data, model_name) или (None, None) при неудаче.
    """
    if not BASE_URL:
        return None, None

    image_array = _bytes_to_array(image_bytes)
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    if prompt is None:
        prompt = (
            "You are a precise food recognition AI. Look at this image and describe exactly what you see. "
            "Return a JSON object with:\n"
            '- "dish_name": a short, specific name of the dish in Russian (if known, otherwise in English),\n'
            '- "ingredients": list of main visible ingredients in Russian (each as a string).\n'
            "Only output valid JSON, no other text. Do not escape characters.\n"
            "Example: {\"dish_name\": \"жареная курица с овощами\", \"ingredients\": [\"курица\", \"помидоры\", \"огурцы\", \"лимон\"]}"
        )

    for model in VISION_MODELS:
        try:
            url = f"{BASE_URL}{model}"
            payload = {
                "image": image_array,
                "prompt": prompt,
                "max_tokens": max_tokens,
            }
            # Добавляем параметры, специфичные для модели
            if model == "@cf/llava-hf/llava-1.5-7b-hf":
                payload["temperature"] = temperature
            # UForm не поддерживает temperature

            logger.info(f"Trying vision model {model} with payload keys: {list(payload.keys())}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        description = result.get("result", {}).get("description", "").strip()
                        if description:
                            data = _extract_json_from_text(description)
                            if data and _validate_food_data(data):
                                logger.info(f"✅ Model {model} returned valid and plausible JSON: {data}")
                                return data, model
                            else:
                                logger.warning(f"Model {model} returned invalid or implausible data: {data}")
                    else:
                        error_text = await resp.text()
                        logger.warning(f"Model {model} failed with status {resp.status}: {error_text}")
        except Exception as e:
            logger.warning(f"Model {model} error: {e}")
            continue

    logger.error("All vision models failed to return valid JSON")
    return None, None

# Для обратной совместимости оставляем старые функции
async def identify_dish_from_image(image_bytes: bytes) -> Optional[str]:
    """Возвращает только название блюда (строку) или None."""
    data, _ = await identify_food_multimodel(image_bytes, max_tokens=50)
    if data:
        return data.get("dish_name")
    return None

async def analyze_food_image(image_bytes: bytes, prompt: str = None) -> Optional[str]:
    """Возвращает текстовое описание (ингредиенты) или None."""
    if prompt is None:
        prompt = "List all food items visible in this image. Be specific. Return as a comma-separated list."
    data, _ = await identify_food_multimodel(image_bytes, prompt=prompt, max_tokens=150)
    if data and "ingredients" in data:
        return ", ".join(data["ingredients"])
    return None

# Транскрибация (без изменений)
async def _convert_ogg_to_wav(ogg_bytes: bytes) -> Optional[bytes]:
    """Конвертирует OGG в WAV."""
    try:
        if len(ogg_bytes) > 20 * 1024 * 1024:
            return None
        import tempfile
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
