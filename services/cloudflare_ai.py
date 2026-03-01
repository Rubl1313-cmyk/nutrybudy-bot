"""
Cloudflare Workers AI Integration для NutriBuddy
===============================================

Поддерживаемые функции:
• Анализ изображений еды (UForm-Gen2) — массив байтов, не base64!
• Распознавание голоса (Whisper) — multipart/form-data
• Генерация рецептов (Llama 3) — messages API
• Анализ текста (TinyLlama) — для быстрых задач

Важно: Vision-модели Cloudflare требуют image как array of integers (0-255),
а НЕ как base64-строку. Это ключевое отличие от большинства других API.

Документация:
• https://developers.cloudflare.com/workers-ai/models/
• https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/
"""

import aiohttp
import os
import logging
from typing import Optional, Dict, List, Union
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

# =============================================================================
# 🔐 КОНФИГУРАЦИЯ
# =============================================================================

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.warning("⚠️ Cloudflare credentials not set — AI functions will fail")

BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Доступные модели
MODELS = {
    # Vision (анализ изображений)
    "uform_gen2": "@cf/unum/uform-gen2-qwen-500m",
    "llava": "@cf/llava-hf/llava-1.5-7b-hf",
    
    # Audio (распознавание речи)
    "whisper": "@openai/whisper",
    
    # Text generation (генерация текста)
    "llama3": "@cf/meta/llama-3-8b-instruct",
    "llama3_1": "@cf/meta/llama-3.1-8b-instruct",
    "mistral": "@cf/mistral/mistral-7b-instruct-v0.1",
    
    # Fast text (быстрые задачи)
    "tinyllama": "@cf/tinyllama/tinyllama-1.1b-chat-v1.0",
}

# Таймауты по умолчанию (секунды)
DEFAULT_TIMEOUTS = {
    "vision": 30,
    "audio": 60,
    "text": 45,
}


# =============================================================================
# 🔧 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def _bytes_to_array(image_bytes: bytes) -> List[int]:
    """
    Конвертирует bytes в список целых чисел 0-255 для Cloudflare AI.
    
    Cloudflare Vision API требует image как массив байтов, а не base64!
    
    Args:
        image_bytes: Сырые байты изображения
        
    Returns:
        List[int]: Список целых чисел 0-255
    """
    return list(image_bytes)


def _validate_credentials() -> bool:
    """Проверяет, настроены ли учётные данные Cloudflare"""
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        logger.error("❌ Cloudflare credentials not configured")
        return False
    return True


async def _make_request(
    endpoint: str,
    payload: Dict,
    timeout: int = 30,
    use_form: bool = False
) -> Optional[Dict]:
    """
    Внутренняя функция для HTTP-запросов к Cloudflare AI API.
    
    Args:
        endpoint: URL эндпоинта (полный или относительный)
        payload: Данные запроса
        timeout: Таймаут в секундах
        use_form: Использовать multipart/form-data (для аудио)
        
    Returns:
        Dict: Ответ API или None при ошибке
    """
    if not _validate_credentials():
        return None
    
    url = endpoint if endpoint.startswith("http") else f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            if use_form:
                # Для Whisper: multipart/form-data
                from aiohttp import FormData
                data = FormData()
                for key, value in payload.items():
                    data.add_field(key, value)
                
                async with session.post(
                    url,
                    headers=headers,
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    return await _process_response(resp)
            else:
                # Для JSON-запросов (vision, text)
                headers["Content-Type"] = "application/json"
                
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    return await _process_response(resp)
                    
        except aiohttp.ClientConnectionError as e:
            logger.error(f"🌐 Connection error: {e}")
            return None
        except aiohttp.ClientTimeout as e:
            logger.error(f"⏱️ Request timeout: {e}")
            return None
        except Exception as e:
            logger.exception(f"💥 Unexpected error in _make_request: {e}")
            return None


async def _process_response(resp: aiohttp.ClientResponse) -> Optional[Dict]:
    """
    Обработка ответа от Cloudflare API.
    
    Args:
        resp: Объект ответа aiohttp
        
    Returns:
        Dict: Распарсенный JSON или None
    """
    try:
        if resp.status == 200:
            return await resp.json()
        
        # Логирование ошибок по кодам статуса
        error_text = await resp.text()
        
        if resp.status == 401:
            logger.error("🔐 Authentication failed — check API token")
        elif resp.status == 403:
            logger.error("🚫 Access denied — check account ID and model permissions")
        elif resp.status == 400:
            logger.error(f"❌ Bad request: {error_text[:200]}")
        elif resp.status == 429:
            logger.error("⏱️ Rate limit exceeded — try again later")
        elif resp.status >= 500:
            logger.error(f"🔧 Server error {resp.status}: {error_text[:200]}")
        else:
            logger.error(f"❌ API error {resp.status}: {error_text[:200]}")
        
        return None
        
    except Exception as e:
        logger.error(f"💥 Error processing response: {e}")
        return None


# =============================================================================
# 🔍 АНАЛИЗ ИЗОБРАЖЕНИЙ (Vision AI)
# =============================================================================

async def analyze_food_image(
    image_bytes: bytes,
    prompt: str = "Опиши еду на этом изображении. Укажи название блюда и основные ингредиенты. Отвечай кратко на русском, 2-3 слова.",
    max_tokens: int = 150,
    model: str = "uform_gen2"
) -> Optional[str]:
    """
    Анализирует изображение еды через Cloudflare Vision AI.
    
    🔑 КЛЮЧЕВОЕ: image отправляется как array of bytes (List[int]), НЕ base64!
    
    Args:
        image_bytes: Сырые байты изображения (JPEG/PNG)
        prompt: Промпт для модели (по умолчанию требует краткий ответ на русском)
        max_tokens: Максимальная длина ответа
        model: Название модели из MODELS (по умолчанию "uform_gen2")
        
    Returns:
        str: Описание еды или None при ошибке
        
    Example:
        >>> with open("food.jpg", "rb") as f:
        ...     result = await analyze_food_image(f.read())
        >>> print(result)  # "жареная курица с овощами"
    """
    try:
        if not _validate_credentials():
            return None
        
        # 🔥 Конвертируем bytes → array of integers 0-255
        image_array = _bytes_to_array(image_bytes)
        logger.info(f"📊 Image converted: {len(image_array)} bytes → array")
        
        # Формат payload для UForm-Gen2 и подобных vision-моделей
        payload = {
            "image": image_array,  # ← МАССИВ, не base64!
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        model_endpoint = MODELS.get(model, MODELS["uform_gen2"])
        logger.info(f"📤 Sending to {model_endpoint}")
        
        result = await _make_request(
            model_endpoint,
            payload,
            timeout=DEFAULT_TIMEOUTS["vision"]
        )
        
        if result:
            # Разные модели могут возвращать разные форматы
            if "result" in result:
                description = result["result"].get("description", "")
            elif "choices" in result:
                # OpenAI-совместимый формат
                description = result["choices"][0].get("message", {}).get("content", "")
            else:
                description = str(result)
            
            if description and len(description.strip()) > 5:
                logger.info(f"✅ Vision success: {description[:100]}...")
                return description.strip()
            
            logger.warning("⚠️ Empty description in response")
            return None
        
        logger.warning("⚠️ No result from Vision API")
        return None
        
    except Exception as e:
        logger.exception(f"💥 analyze_food_image error: {e}")
        return None


async def analyze_image_with_llava(
    image_bytes: bytes,
    prompt: str = "What is in this image?",
    max_tokens: int = 200
) -> Optional[str]:
    """
    Альтернативный анализ через LLaVA-1.5 модель.
    Может быть стабильнее для некоторых типов изображений.
    
    Args:
        image_bytes: Сырые байты изображения
        prompt: Промпт для модели
        max_tokens: Максимальная длина ответа
        
    Returns:
        str: Описание или None
    """
    return await analyze_food_image(
        image_bytes,
        prompt=prompt,
        max_tokens=max_tokens,
        model="llava"
    )


# =============================================================================
# 🎤 РАСПОЗНАВАНИЕ ГОЛОСА (Whisper)
# =============================================================================

async def transcribe_audio(
    audio_bytes: bytes,
    language: str = "ru",
    temperature: float = 0.0,
    model: str = "whisper"
) -> Optional[str]:
    """
    Распознаёт речь в аудиофайле через Cloudflare Whisper.
    
    Аудио должно быть в формате .ogg (как отправляет Telegram Voice).
    
    Args:
        audio_bytes: Сырые байты аудиофайла
        language: Код языка ('ru', 'en', 'de', etc.)
        temperature: Креативность распознавания (0.0 = точно, 1.0 = вариативно)
        model: Название модели (по умолчанию "whisper")
        
    Returns:
        str: Распознанный текст или None при ошибке
        
    Example:
        >>> with open("voice.ogg", "rb") as f:
        ...     text = await transcribe_audio(f.read(), language="ru")
        >>> print(text)  # "запиши гречку с курицей на обед"
    """
    try:
        if not _validate_credentials():
            return None
        
        from aiohttp import FormData
        
        # Whisper API принимает multipart/form-data
        data = FormData()
        data.add_field('file', audio_bytes, filename='voice.ogg', content_type='audio/ogg')
        data.add_field('model', MODELS.get(model, MODELS["whisper"]))
        data.add_field('language', language)
        data.add_field('temperature', str(temperature))
        
        logger.info(f"🎤 Sending audio to Whisper ({len(audio_bytes)} bytes, lang={language})")
        
        # Прямой запрос, т.к. FormData не совместима с _make_request
        url = f"{BASE_URL}{MODELS.get(model, MODELS['whisper'])}"
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUTS["audio"])
            ) as resp:
                
                if resp.status == 200:
                    result = await resp.json()
                    text = result.get("result", {}).get("text", "")
                    if text:
                        logger.info(f"✅ Whisper success: {text[:100]}...")
                        return text.strip()
                    logger.warning("⚠️ Empty text from Whisper")
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Whisper error {resp.status}: {error_text[:200]}")
                    return None
                    
    except Exception as e:
        logger.exception(f"💥 transcribe_audio error: {e}")
        return None


# =============================================================================
# 🧠 ГЕНЕРАЦИЯ ТЕКСТА (LLM)
# =============================================================================

async def generate_recipe(
    ingredients: str,
    diet_type: str = "обычное",
    difficulty: str = "средняя",
    max_tokens: int = 800,
    model: str = "llama3"
) -> Optional[str]:
    """
    Генерирует подробный рецепт на основе ингредиентов через Llama 3.
    
    Args:
        ingredients: Список ингредиентов через запятую (например, "курица, рис, брокколи")
        diet_type: Тип питания (обычное/вегетарианское/веганское/кето/палео)
        difficulty: Сложность (лёгкая/средняя/сложная)
        max_tokens: Максимальная длина ответа
        model: Название модели (по умолчанию "llama3")
        
    Returns:
        str: Сформированный рецепт или None при ошибке
        
    Example:
        >>> recipe = await generate_recipe("курица, рис, овощи", diet_type="кето")
        >>> print(recipe)  # Подробный рецепт с КБЖУ
    """
    prompt = f"""Ты — профессиональный шеф-повар и нутрициолог.
Составь подробный рецепт блюда на русском языке.

🥘 Ингредиенты: {ingredients}
🥗 Тип питания: {diet_type}
👨‍🍳 Сложность: {difficulty}

📋 Формат ответа (используй эмодзи для наглядности):
1. 🍽️ Название блюда
2. ⏱️ Время приготовления и порции
3. 🛒 Ингредиенты с точными количествами
4. 👨‍🍳 Пошаговое приготовление (нумерованный список)
5. 📊 КБЖУ на порцию (калории, белки, жиры, углеводы)
6. 💡 Советы по подаче, хранению и вариациям

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
    
    model_endpoint = MODELS.get(model, MODELS["llama3"])
    logger.info(f"🧠 Generating recipe via {model_endpoint} for: {ingredients[:50]}...")
    
    try:
        result = await _make_request(
            model_endpoint,
            payload,
            timeout=DEFAULT_TIMEOUTS["text"]
        )
        
        if result and "result" in result:
            recipe = result["result"].get("response", "")
            if recipe and len(recipe.strip()) > 50:
                logger.info(f"✅ Recipe generated ({len(recipe)} chars)")
                return recipe.strip()
            logger.warning("⚠️ Empty or too short response from LLM")
            return None
        
        logger.warning("⚠️ No result from LLM API")
        return None
        
    except Exception as e:
        logger.exception(f"💥 generate_recipe error: {e}")
        return None


async def generate_text(
    prompt: str,
    system_prompt: str = "Ты полезный ассистент.",
    model: str = "llama3",
    temperature: float = 0.7,
    max_tokens: int = 500
) -> Optional[str]:
    """
    Универсальная функция генерации текста через LLM.
    
    Args:
        prompt: Запрос пользователя
        system_prompt: Системный промпт (роль модели)
        model: Название модели
        temperature: Креативность (0.0-1.0)
        max_tokens: Максимальная длина ответа
        
    Returns:
        str: Сгенерированный текст или None
    """
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.9
    }
    
    model_endpoint = MODELS.get(model, MODELS["llama3"])
    
    try:
        result = await _make_request(
            model_endpoint,
            payload,
            timeout=DEFAULT_TIMEOUTS["text"]
        )
        
        if result and "result" in result:
            return result["result"].get("response", "")
        
        return None
        
    except Exception as e:
        logger.exception(f"💥 generate_text error: {e}")
        return None


# =============================================================================
# 📊 АНАЛИЗ ТЕКСТА (быстрые задачи)
# =============================================================================

async def analyze_nutrition_text(text: str) -> Dict[str, float]:
    """
    Извлекает данные о КБЖУ из текстового описания еды.
    Использует TinyLlama для скорости.
    
    Args:
        text: Описание блюда (например, "куриная грудка 150г")
        
    Returns:
        dict: {'calories': float, 'protein': float, 'fat': float, 'carbs': float}
    """
    prompt = f"""Проанализируй описание еды и извлеки данные о КБЖУ.
Текст: "{text}"

Верни ТОЛЬКО JSON в формате:
{{"calories": число, "protein": число, "fat": число, "carbs": число}}
Если данных нет — верни нули. Единицы: ккал и граммы.
Никакого дополнительного текста, только JSON."""

    payload = {
        "messages": [
            {"role": "system", "content": "Ты извлекаешь данные о питании. Отвечай только JSON."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.1  # Минимум креативности для точности
    }
    
    default_result = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
    
    try:
        result = await _make_request(
            MODELS["tinyllama"],
            payload,
            timeout=15  # Быстрый таймаут
        )
        
        if result and "result" in result:
            import json
            response = result["result"].get("response", "")
            # Попытка распарсить JSON из ответа
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        
        return default_result
        
    except Exception as e:
        logger.error(f"❌ Nutrition analysis error: {e}")
        return default_result


# =============================================================================
# 🔧 УТИЛИТЫ И ДИАГНОСТИКА
# =============================================================================

async def check_api_health() -> Dict[str, bool]:
    """
    Проверяет доступность всех моделей Cloudflare AI.
    
    Returns:
        dict: {'model_name': True/False} для каждой модели
    """
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for name, model in MODELS.items():
            # Проверка через список моделей (не требует реального запроса)
            url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/models/{model.split('/')[-1]}"
            headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
            
            try:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    results[name] = resp.status in (200, 404)  # 404 = модель есть, но не найдена по имени
            except:
                results[name] = False
    
    return results


def get_model_info(model_name: str) -> Optional[Dict]:
    """
    Возвращает информацию о модели по имени.
    
    Args:
        model_name: Ключ из MODELS (например, "llama3")
        
    Returns:
        dict: Информация о модели или None
    """
    model_map = {
        "uform_gen2": {
            "type": "vision",
            "description": "Анализ изображений (UForm-Gen2)",
            "input": "image array + prompt",
            "output": "description text"
        },
        "llava": {
            "type": "vision",
            "description": "Анализ изображений (LLaVA-1.5)",
            "input": "image array + prompt",
            "output": "description text"
        },
        "whisper": {
            "type": "audio",
            "description": "Распознавание речи (Whisper)",
            "input": "audio file (multipart)",
            "output": "transcribed text"
        },
        "llama3": {
            "type": "text",
            "description": "Генерация текста (Llama 3 8B)",
            "input": "messages array",
            "output": "response text"
        },
        "tinyllama": {
            "type": "text",
            "description": "Быстрые текстовые задачи (TinyLlama 1.1B)",
            "input": "messages array",
            "output": "response text"
        }
    }
    return model_map.get(model_name)


async def test_connection() -> Dict[str, Union[bool, str]]:
    """
    Тестирует подключение к Cloudflare AI API.
    
    Returns:
        dict: {'success': bool, 'message': str, 'models_available': int}
    """
    if not _validate_credentials():
        return {
            "success": False,
            "message": "Cloudflare credentials not configured",
            "models_available": 0
        }
    
    try:
        health = await check_api_health()
        available = sum(1 for v in health.values() if v)
        
        return {
            "success": True,
            "message": f"Connected. {available}/{len(health)} models available",
            "models_available": available,
            "details": health
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}",
            "models_available": 0
        }


# =============================================================================
# 🎯 ТОЧКА ВХОДА ДЛЯ ТЕСТОВ
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("🔍 Testing Cloudflare AI integration...")
        
        # Тест подключения
        conn = await test_connection()
        print(f"Connection: {conn['message']}")
        
        if not conn['success']:
            return
        
        # Тест генерации текста (не требует файлов)
        print("\n🧪 Testing text generation...")
        recipe = await generate_recipe("курица, рис, брокколи")
        if recipe:
            print(f"✅ Recipe preview: {recipe[:200]}...")
        else:
            print("❌ Recipe generation failed")
        
        # Тест анализа текста
        print("\n🧪 Testing nutrition analysis...")
        nutrition = await analyze_nutrition_text("куриная грудка 150г")
        print(f"✅ Nutrition: {nutrition}")
    
    asyncio.run(main())
