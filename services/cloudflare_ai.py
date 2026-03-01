"""
Cloudflare Workers AI Integration для NutriBuddy
✅ Полная версия с поддержкой всех параметров
"""
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
    """Конвертирует bytes в список целых чисел 0-255"""
    return list(image_bytes)


async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "What food is in this image? Describe briefly in Russian.",
    max_tokens: int = 150
) -> Optional[str]:
    """Анализ изображения еды"""
    try:
        if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
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
        
        model = "@cf/unum/uform-gen2-qwen-500m"
        url = f"{BASE_URL}{model}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                
                if resp.status == 200:
                    result = await resp.json()
                    
                    if "result" in result:
                        description = result["result"].get("description", "")
                    elif "choices" in result:
                        description = result["choices"][0].get("message", {}).get("content", "")
                    else:
                        description = str(result)
                    
                    if description and len(description.strip()) > 5 and len(description.strip()) < 500:
                        return description.strip()
                    
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ API error {resp.status}: {error_text[:300]}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 analyze_food_image error: {e}")
        return None


async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """Распознавание голоса через Whisper"""
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
                        return text.strip()
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Whisper error {resp.status}: {error_text}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 transcribe_audio error: {e}")
        return None


async def generate_recipe(
    ingredients: str,
    diet_type: str = "обычное",
    difficulty: str = "средняя",
    max_tokens: int = 800
) -> Optional[str]:
    """
    Генерация рецепта через Llama 3.
    
    Args:
        ingredients: Список ингредиентов через запятую
        diet_type: Тип питания (обычное/вегетарианское/веганское/кето/палео)
        difficulty: Сложность (лёгкая/средняя/сложная)
        max_tokens: Максимальная длина ответа
        
    Returns:
        str: Сформированный рецепт или None
    """
    # Перевод difficulty на английский для промпта
    difficulty_map = {
        "лёгкая": "quick (~15 min)",
        "легкая": "quick (~15 min)",
        "средняя": "medium (~30 min)",
        "сложная": "advanced (~60 min)"
    }
    difficulty_en = difficulty_map.get(difficulty, "medium (~30 min)")
    
    prompt = f"""Ты — профессиональный шеф-повар и нутрициолог.
Составь подробный рецепт блюда на русском языке.

🥘 Ингредиенты: {ingredients}
🥗 Тип питания: {diet_type}
⏱️ Сложность: {difficulty} ({difficulty_en})

📋 Формат ответа (используй эмодзи):
1. 🍽️ Название блюда
2. ⏱️ Время приготовления и количество порций
3. 🛒 Ингредиенты с точными количествами
4. 👨‍🍳 Пошаговое приготовление (нумерованный список)
5. 📊 КБЖУ на порцию (калории, белки, жиры, углеводы)
6. 💡 Советы по подаче и хранению

Отвечай только рецептом, без лишних вступлений."""

    payload = {
        "messages": [
            {"role": "system", "content": "Ты полезный ассистент-повар. Отвечай на русском."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    model = "@cf/meta/llama-3-8b-instruct"
    url = f"{BASE_URL}{model}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=45)
            ) as resp:
                
                if resp.status == 200:
                    result = await resp.json()
                    recipe = result.get("result", {}).get("response", "")
                    if recipe and len(recipe.strip()) > 50:
                        return recipe.strip()
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Recipe error {resp.status}: {error_text[:300]}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 generate_recipe error: {e}")
        return None
