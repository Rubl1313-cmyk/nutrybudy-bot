"""
Cloudflare Workers AI Integration для NutriBuddy
Поддерживает:
- Анализ изображений еды (UForm-Gen2)
- Распознавание голоса (Whisper)
- Генерация рецептов (Llama 3)
- Анализ текста (микро-модели)
"""

import aiohttp
import os
import base64
import logging
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Настройки из переменных окружения
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

# Базовый URL API
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Доступные модели
MODELS = {
    "vision": "@cf/unum/uform-gen2-qwen-500m",      # Анализ изображений
    "whisper": "@openai/whisper",                    # Распознавание речи
    "llama3": "@cf/meta/llama-3-8b-instruct",        # Генерация текста/рецептов
    "mistral": "@cf/mistral/mistral-7b-instruct-v0.1",  # Альтернатива Llama
    "tiny": "@cf/tinyllama/tinyllama-1.1b-chat-v1.0",   # Быстрые простые задачи
}


class CloudflareAIError(Exception):
    """Кастомное исключение для ошибок Cloudflare AI"""
    pass


async def _make_request(
    model: str,
    payload: Dict,
    headers: Optional[Dict] = None,
    use_form: bool = False
) -> Optional[Dict]:
    """Внутренняя функция для HTTP-запросов к Cloudflare AI"""
    
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        logger.error("❌ Cloudflare credentials not set")
        raise CloudflareAIError("Cloudflare API credentials not configured")
    
    url = f"{BASE_URL}{model}"
    request_headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        **(headers or {})
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            if use_form:
                # Для FormData (аудио)
                from aiohttp import FormData
                data = FormData()
                for key, value in payload.items():
                    data.add_field(key, value)
                
                async with session.post(url, headers=request_headers, data=data) as resp:
                    return await _process_response(resp)
            else:
                # Для JSON
                async with session.post(url, headers=request_headers, json=payload) as resp:
                    return await _process_response(resp)
                    
        except aiohttp.ClientError as e:
            logger.error(f"🌐 Network error: {e}")
            raise CloudflareAIError(f"Network error: {e}")
        except Exception as e:
            logger.exception(f"💥 Unexpected error: {e}")
            raise CloudflareAIError(f"Unexpected error: {e}")


async def _process_response(resp: aiohttp.ClientResponse) -> Optional[Dict]:
    """Обработка ответа от API"""
    
    if resp.status == 200:
        return await resp.json()
    
    error_text = await resp.text()
    
    # Логирование разных типов ошибок
    if resp.status == 401:
        logger.error("🔐 Authentication failed - check your API token")
    elif resp.status == 403:
        logger.error("🚫 Access denied - check account ID and permissions")
    elif resp.status == 429:
        logger.error("⏱️ Rate limit exceeded - try again later")
    elif resp.status >= 500:
        logger.error(f"🔧 Server error {resp.status}: {error_text}")
    else:
        logger.error(f"❌ API error {resp.status}: {error_text}")
    
    return None


# =============================================================================
# 🔍 АНАЛИЗ ИЗОБРАЖЕНИЙ (UForm-Gen2)
# =============================================================================

async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "Опиши еду на этом изображении. Укажи название блюда, основные ингредиенты и примерную калорийность. Отвечай кратко на русском.",
    max_tokens: int = 200
) -> Optional[str]:
    """
    Анализирует изображение еды и возвращает текстовое описание.
    
    Args:
        image_bytes: Байты изображения (JPEG/PNG)
        prompt: Промпт для модели
        max_tokens: Максимальная длина ответа
    
    Returns:
        str: Описание еды или None при ошибке
    """
    try:
        # Конвертация в base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        payload = {
            "image": image_base64,
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        logger.info(f"📤 Sending image to Cloudflare Vision AI ({len(image_bytes)} bytes)")
        
        result = await _make_request(MODELS["vision"], payload)
        
        if result and "result" in result:
            description = result["result"].get("description", "")
            logger.info(f"✅ Vision AI result: {description[:100]}...")
            return description
        
        logger.warning("⚠️ Empty or invalid response from Vision AI")
        return None
        
    except CloudflareAIError as e:
        logger.error(f"❌ Vision AI error: {e}")
        return None
    except Exception as e:
        logger.exception(f"💥 Unexpected error in analyze_food_image: {e}")
        return None


# =============================================================================
# 🎤 РАСПОЗНАВАНИЕ ГОЛОСА (Whisper)
# =============================================================================

async def transcribe_audio(
    audio_bytes: bytes,
    language: str = "ru",
    temperature: float = 0.0
) -> Optional[str]:
    """
    Распознаёт речь в аудиофайле и возвращает текст.
    
    Args:
        audio_bytes: Байты аудио (OGG/MP3/WAV, как отправляет Telegram)
        language: Язык распознавания ('ru', 'en', etc.)
        temperature: Креативность (0.0 = точно, 1.0 = вариативно)
    
    Returns:
        str: Распознанный текст или None при ошибке
    """
    try:
        from aiohttp import FormData
        
        data = FormData()
        data.add_field('file', audio_bytes, filename='voice.ogg', content_type='audio/ogg')
        data.add_field('model', 'whisper')
        data.add_field('language', language)
        data.add_field('temperature', str(temperature))
        
        logger.info(f"🎤 Sending audio to Whisper ({len(audio_bytes)} bytes)")
        
        # Whisper API принимает FormData, а не JSON
        url = f"{BASE_URL}{MODELS['whisper']}"
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    text = result.get("result", {}).get("text", "")
                    logger.info(f"✅ Whisper result: {text[:100]}...")
                    return text
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Whisper error {resp.status}: {error_text}")
                    return None
                    
    except CloudflareAIError as e:
        logger.error(f"❌ Whisper error: {e}")
        return None
    except Exception as e:
        logger.exception(f"💥 Unexpected error in transcribe_audio: {e}")
        return None


# =============================================================================
# 🧠 ГЕНЕРАЦИЯ ТЕКСТА (Llama 3 / Mistral)
# =============================================================================

async def generate_recipe(
    ingredients: str,
    diet_type: str = "обычное",
    difficulty: str = "средняя",
    max_tokens: int = 800
) -> Optional[str]:
    """
    Генерирует подробный рецепт на основе ингредиентов.
    
    Args:
        ingredients: Список ингредиентов через запятую
        diet_type: Тип питания (обычное/вегетарианское/веганское/кето)
        difficulty: Сложность (лёгкая/средняя/сложная)
        max_tokens: Максимальная длина ответа
    
    Returns:
        str: Сформированный рецепт или None при ошибке
    """
    prompt = f"""Ты — профессиональный шеф-повар и нутрициолог.
Составь подробный рецепт блюда на русском языке.

🥘 Ингредиенты: {ingredients}
🥗 Тип питания: {diet_type}
👨‍🍳 Сложность: {difficulty}

📋 Формат ответа:
1. 🍽️ Название блюда
2. ⏱️ Время приготовления и сложность
3. 🛒 Ингредиенты с точными количествами
4. 👨‍🍳 Пошаговое приготовление (нумерованный список)
5. 📊 КБЖУ на порцию (калории, белки, жиры, углеводы)
6. 💡 Советы по подаче и хранению

Отвечай структурированно, используй эмодзи для наглядности."""

    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,  # Баланс креативности и точности
        "top_p": 0.9
    }
    
    logger.info(f"🧠 Generating recipe for: {ingredients[:50]}...")
    
    try:
        result = await _make_request(MODELS["llama3"], payload)
        
        if result and "result" in result:
            recipe = result["result"].get("response", "")
            logger.info(f"✅ Recipe generated ({len(recipe)} chars)")
            return recipe
        
        logger.warning("⚠️ Empty response from LLM")
        return None
        
    except CloudflareAIError as e:
        logger.error(f"❌ Recipe generation error: {e}")
        return None


async def generate_text(
    prompt: str,
    model: str = "llama3",
    temperature: float = 0.7,
    max_tokens: int = 500
) -> Optional[str]:
    """
    Универсальная функция генерации текста.
    
    Args:
        prompt: Запрос к модели
        model: Название модели ('llama3', 'mistral', 'tiny')
        temperature: Креативность (0.0-1.0)
        max_tokens: Максимальная длина ответа
    
    Returns:
        str: Сгенерированный текст или None
    """
    model_name = MODELS.get(model, MODELS["llama3"])
    
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.9
    }
    
    try:
        result = await _make_request(model_name, payload)
        
        if result and "result" in result:
            return result["result"].get("response", "")
        
        return None
        
    except CloudflareAIError:
        return None


# =============================================================================
# 📊 АНАЛИЗ ТЕКСТА (быстрые задачи)
# =============================================================================

async def analyze_nutrition_text(text: str) -> Optional[Dict]:
    """
    Извлекает данные о КБЖУ из текстового описания еды.
    
    Args:
        text: Описание блюда
    
    Returns:
        dict: {'calories': float, 'protein': float, 'fat': float, 'carbs': float}
    """
    prompt = f"""Проанализируй описание еды и извлеки данные о КБЖУ.
Текст: "{text}"

Верни ТОЛЬКО JSON в формате:
{{"calories": число, "protein": число, "fat": число, "carbs": число}}
Если данных нет — верни нули. Единицы: ккал и граммы."""

    try:
        result = await _make_request(MODELS["tiny"], {
            "prompt": prompt,
            "max_tokens": 150,
            "temperature": 0.1  # Минимум креативности для точности
        })
        
        if result and "result" in result:
            import json
            response = result["result"].get("response", "")
            # Попытка распарсить JSON из ответа
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        
        return {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        
    except Exception as e:
        logger.error(f"❌ Nutrition analysis error: {e}")
        return {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}


# =============================================================================
# 🔧 УТИЛИТЫ
# =============================================================================

async def check_api_health() -> Dict[str, bool]:
    """
    Проверяет доступность всех моделей Cloudflare AI.
    
    Returns:
        dict: Статус каждой модели
    """
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for name, model in MODELS.items():
            url = f"{BASE_URL}{model}"
            headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
            
            try:
                # Пустой запрос для проверки доступности
                async with session.get(
                    f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/models/{model.split('/')[-1]}",
                    headers=headers
                ) as resp:
                    results[name] = resp.status == 200
            except:
                results[name] = False
    
    return results


def get_usage_stats() -> Dict:
    """
    Возвращает информацию об использовании API (требует дополнительного эндпоинта).
    Пока заглушка.
    """
    return {
        "requests_today": 0,
        "quota_limit": 10000,
        "quota_remaining": 10000
    }
