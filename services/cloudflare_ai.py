import aiohttp
import os
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.warning("⚠️ Cloudflare credentials not set")

BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

MODELS = {
    "uform_gen2": "@cf/unum/uform-gen2-qwen-500m",
    "llava": "@cf/llava-hf/llava-1.5-7b-hf",
    "whisper": "@openai/whisper",
    "llama3": "@cf/meta/llama-3-8b-instruct",
    "tinyllama": "@cf/tinyllama/tinyllama-1.1b-chat-v1.0",
}


def _bytes_to_array(image_bytes: bytes) -> List[int]:
    return list(image_bytes)


async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "What food is in this image? Describe briefly in Russian.",
    max_tokens: int = 150
) -> Optional[str]:
    try:
        if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
            return None
        
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
                    
                    if "result" in result:
                        description = result["result"].get("description", "")
                    elif "choices" in result:
                        description = result["choices"][0].get("message", {}).get("content", "")
                    else:
                        description = str(result)
                    
                    if description and len(description.strip()) > 5 and len(description.strip()) < 200:
                        logger.info(f"✅ Vision success: {description[:100]}...")
                        return description.strip()
                    
                    logger.warning(f"⚠️ Invalid description: {description}")
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ API error {resp.status}: {error_text[:300]}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 analyze_food_image error: {e}")
        return None


async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
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
                    if text:
                        logger.info(f"✅ Whisper success: {text[:100]}...")
                        return text.strip()
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Whisper error {resp.status}: {error_text}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 transcribe_audio error: {e}")
        return None


async def generate_recipe(ingredients: str, max_tokens: int = 800) -> Optional[str]:
    prompt = f"""Ты — шеф-повар. Составь подробный рецепт блюда из: {ingredients}.

Формат:
1. 🍽️ Название
2. 🛒 Ингредиенты с количеством
3. 👨‍🍳 Пошаговое приготовление
4. 📊 КБЖУ на порцию

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
                        logger.info(f"✅ Recipe: {len(recipe)} chars")
                        return recipe
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Recipe error {resp.status}: {error_text[:300]}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 generate_recipe error: {e}")
        return None
