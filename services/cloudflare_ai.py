"""
Cloudflare Workers AI Integration for NutriBuddy
✅ УЛУЧШЕНО: Progressive loading, надёжное извлечение JSON, кэширование
✅ Добавлено: Retry-логика, валидация, fallback-механизмы, прогресс-бар
"""
import aiohttp
import os
import logging
import asyncio
import json
import re
import hashlib
from typing import Optional, Dict, Any, Tuple, List
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Модели с приоритетами (от лучших к быстрым)
VISION_MODELS = [
    {"id": "@cf/llava-hf/llava-1.5-7b-hf", "priority": 1, "timeout": 90, "weight": 0.6},
    {"id": "@cf/unum/uform-gen2-qwen-500m", "priority": 2, "timeout": 60, "weight": 0.4},
    {"id": "@cf/llava-hf/bakllava-1", "priority": 3, "timeout": 90, "weight": 0.3},
]

# Кэш результатов (hash изображения → результат)
_RECOGNITION_CACHE: Dict[str, Tuple[Dict, datetime]] = {}
_CACHE_TTL = 3600  # 1 час

# ========== УЛУЧШЕННЫЕ ПРОМПТЫ ==========
FOOD_RECOGNITION_PROMPT = """You are an expert food nutritionist with 10+ years of experience. Analyze this food image carefully and return ONLY valid JSON.

CRITICAL REQUIREMENTS:
1. Return pure JSON without markdown, without backslashes before underscores, without any formatting
2. Be SPECIFIC about dishes - use exact names like "grilled chicken breast" not just "chicken"
3. Estimate weights realistically based on portion size
4. Consider cooking methods visible in the image

REQUIRED JSON FORMAT:
{
  "dish_name": "Specific dish name in English",
  "ingredients": [
    {"name": "ingredient", "type": "protein|vegetable|carb|fat|sauce|garnish|other", "estimated_weight_grams": 100, "confidence": 0.9}
  ],
  "confidence": 0.85,
  "meal_type": "breakfast|lunch|dinner|snack",
  "cooking_method": "grilled|fried|boiled|steamed|baked|raw|roasted",
  "portion_size": "small|medium|large",
  "complexity": "simple|moderate|complex"
}

RULES:
1. Use ONLY double quotes, never single quotes
2. NO backslashes before underscores (use "dish_name" NOT "dish\_name")
3. NO markdown code blocks ```json```
4. NO trailing commas
5. All numbers must be unquoted
6. Be as specific as possible about dishes and ingredients
7. Consider visual cues for cooking methods
8. Estimate portion sizes realistically

EXAMPLES:
{"dish_name":"grilled chicken breast with vegetables","ingredients":[{"name":"chicken breast","type":"protein","estimated_weight_grams":150,"confidence":0.95},{"name":"broccoli","type":"vegetable","estimated_weight_grams":100,"confidence":0.9}],"confidence":0.9,"meal_type":"lunch","cooking_method":"grilled","portion_size":"medium","complexity":"simple"}

{"dish_name":"spaghetti carbonara","ingredients":[{"name":"spaghetti pasta","type":"carb","estimated_weight_grams":80,"confidence":0.9},{"name":"bacon","type":"protein","estimated_weight_grams":60,"confidence":0.85},{"name":"eggs","type":"protein","estimated_weight_grams":50,"confidence":0.8}],"confidence":0.85,"meal_type":"dinner","cooking_method":"boiled","portion_size":"medium","complexity":"moderate"}

Now analyze the image and return JSON:"""

# ========== КЭШИРОВАНИЕ ==========
def _get_image_hash(image_bytes: bytes) -> str:
    """Создаёт hash изображения для кэширования."""
    return hashlib.md5(image_bytes).hexdigest()


def _get_cached_result(image_hash: str) -> Optional[Dict]:
    """Проверяет кэш."""
    if image_hash in _RECOGNITION_CACHE:
        result, timestamp = _RECOGNITION_CACHE[image_hash]
        if datetime.now() - timestamp < timedelta(seconds=_CACHE_TTL):
            logger.info(f"♻️ Cache hit for image {image_hash[:8]}")
            return result
        else:
            del _RECOGNITION_CACHE[image_hash]
    return None


def _cache_result(image_hash: str, result: Dict):
    """Сохраняет в кэш."""
    _RECOGNITION_CACHE[image_hash] = (result, datetime.now())
    # Очистка старого кэша
    if len(_RECOGNITION_CACHE) > 100:
        oldest = sorted(_RECOGNITION_CACHE.items(), key=lambda x: x[1][1])[:20]
        for key, _ in oldest:
            del _RECOGNITION_CACHE[key]


# ========== УЛУЧШЕННОЕ ИЗВЛЕЧЕНИЕ JSON ==========
def _extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Извлекает JSON из текста с улучшенной обработкой экранирований.
    ✅ ИСПРАВЛЕНО: обработка \_ → _, \" → "
    """
    if not text or not isinstance(text, str):
        return None
    
    original_text = text.strip()
    
    # 1. Убираем markdown блоки кода
    for marker in ['```json', '```JSON', '```']:
        if marker in text:
            parts = text.split(marker, 1)
            if len(parts) > 1:
                text = parts[1].split('```', 1)[0].strip()
    
    # 2. Находим границы JSON объекта
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1 or end <= start:
        start_arr = text.find('[')
        end_arr = text.rfind(']')
        if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
            start, end = start_arr, end_arr
        else:
            logger.warning(f"❌ No JSON structure found")
            return None
    
    json_str = text[start:end+1]
    
    # 3. 🔥 ИСПРАВЛЕНИЕ: Убираем неправильные экранирования
    json_str = json_str.replace('\\_', '_')  # \_ → _
    json_str = json_str.replace('\\"', '"')  # \" → "
    json_str = re.sub(r'\\(["\\])', r'\1', json_str)
    json_str = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # 4. Исправляем одинарные кавычки → двойные
    if "'dish_name'" in json_str or "'ingredients'" in json_str:
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
    
    # 5. Убираем trailing commas
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # 6. Попытка парсинга
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            return data
        elif isinstance(data, list) and len(data) > 0:
            return {"ingredients": data, "dish_name": "Mixed dish", "confidence": 0.7}
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ JSON decode failed: {e}")
        
        # 7. Последняя попытка: ручное исправление
        try:
            json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', json_str)
            data = json.loads(json_str)
            return data if isinstance(data, dict) else None
        except:
            return None

# ========== ВАЛИДАЦИЯ ДАННЫХ ==========
def _validate_ingredient(ing: Any) -> bool:
    """Проверяет валидность одного ингредиента."""
    if not isinstance(ing, dict):
        return False
    
    name = ing.get('name', '')
    if not name or not isinstance(name, str) or len(name.strip()) < 2:
        return False
    
    weight = ing.get('estimated_weight_grams')
    if weight is not None:
        if not isinstance(weight, (int, float)) or weight < 1 or weight > 2000:
            ing['estimated_weight_grams'] = 100
    
    valid_types = {'protein', 'vegetable', 'carb', 'fat', 'sauce', 'garnish', 'other'}
    ing_type = ing.get('type', 'other')
    if ing_type not in valid_types:
        ing['type'] = 'other'
    
    conf = ing.get('confidence')
    if conf is None or not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        ing['confidence'] = 0.7
    
    return True


def _validate_food_data(data: Dict) -> Tuple[bool, str]:
    """Расширенная валидация данных о еде."""
    if not isinstance(data, dict):
        return False, "Not a dictionary"
    
    dish = data.get('dish_name', '')
    if not dish or not isinstance(dish, str) or len(dish.strip()) < 3:
        return False, "Invalid dish_name"
    
    ingredients = data.get('ingredients', [])
    if not isinstance(ingredients, list) or len(ingredients) == 0:
        return False, "Empty ingredients"
    
    valid_count = sum(1 for ing in ingredients if _validate_ingredient(ing))
    if valid_count == 0:
        return False, "No valid ingredients"
    
    return True, "OK"


# ========== КАЛИБРОВКА ВЕСОВ ==========
def _calibrate_weights(ingredients: List[Dict], portion_size: str) -> List[Dict]:
    """Калибрует веса ингредиентов на основе размера порции."""
    if not ingredients:
        return ingredients
    
    TARGETS = {
        'small': {'total': 200, 'protein': 80, 'carb': 70, 'vegetable': 40, 'fat': 10},
        'medium': {'total': 350, 'protein': 120, 'carb': 130, 'vegetable': 80, 'fat': 20},
        'large': {'total': 500, 'protein': 180, 'carb': 200, 'vegetable': 100, 'fat': 20},
    }
    
    target = TARGETS.get(portion_size, TARGETS['medium'])
    
    by_type: Dict[str, List[Dict]] = {}
    for ing in ingredients:
        ing_type = ing.get('type', 'other')
        if ing_type not in by_type:
            by_type[ing_type] = []
        by_type[ing_type].append(ing)
    
    for ing_type, items in by_type.items():
        target_weight = target.get(ing_type, target['vegetable'])
        if not items:
            continue
        
        current_total = sum(ing.get('estimated_weight_grams', 0) for ing in items)
        if current_total < 50 or current_total > target_weight * 2:
            weight_per_item = target_weight / len(items)
            for ing in items:
                ing['estimated_weight_grams'] = int(weight_per_item)
                ing['weight_calibrated'] = True
        else:
            scale = target_weight / current_total
            for ing in items:
                old_weight = ing.get('estimated_weight_grams', 100)
                ing['estimated_weight_grams'] = int(old_weight * scale)
                ing['weight_calibrated'] = True
    
    return ingredients


# ========== ПРОГРЕСС-КОЛЛБЭК ==========
async def _send_progress_update(
    bot,
    chat_id: int,
    message_id: int,
    stage: str,
    progress: int,
    total_stages: int
):
    """Отправляет обновление прогресса пользователю."""
    try:
        stages = [
            "📸 Загрузка изображения",
            "🔍 Анализ изображения",
            "🧠 Распознавание блюд",
            "📊 Обработка результатов",
            "✅ Готово"
        ]
        
        current_stage = min(stage, len(stages) - 1)
        progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
        
        text = (
            f"🔄 <b>Анализ изображения</b>\n"
            f"{progress_bar} {progress}%\n\n"
            f"<i>{stages[current_stage]}</i>\n"
            f"Шаг {current_stage + 1} из {total_stages}"
        )
        
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"⚠️ Progress update failed: {e}")


# ========== ОСНОВНЫЕ ФУНКЦИИ ==========
async def identify_food_multimodel(
    image_bytes: bytes,
    prompt: str = None,
    max_tokens: int = 800,
    temperature: float = 0.1,
    retry_count: int = 2,
    progress_callback=None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Пробует несколько vision-моделей с retry-логикой.
    ✅ Улучшено: валидация, пост-обработка, кэширование, прогресс
    """
    if not BASE_URL:
        logger.error("❌ Cloudflare BASE_URL not configured")
        return None, None
    
    # Проверка кэша
    image_hash = _get_image_hash(image_bytes)
    cached = _get_cached_result(image_hash)
    if cached:
        return cached, "cache"
    
    image_array = list(image_bytes)
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if prompt is None:
        prompt = FOOD_RECOGNITION_PROMPT
    
    for attempt in range(retry_count):
        for idx, model_info in enumerate(VISION_MODELS):
            model = model_info["id"]
            timeout = model_info["timeout"]
            
            try:
                url = f"{BASE_URL}{model}"
                payload = {
                    "image": image_array,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                }
                
                if model == "@cf/llava-hf/llava-1.5-7b-hf":
                    payload["temperature"] = temperature
                
                logger.info(f"🤖 Trying vision model: {model} (attempt {attempt + 1})")
                
                # Обновление прогресса
                if progress_callback:
                    await progress_callback(stage=1, progress=30 + (idx * 20))
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            description = result.get("result", {}).get("description", "").strip()
                            
                            if not description:
                                logger.warning(f"⚠️ Model {model} returned empty description")
                                continue
                            
                            # Обновление прогресса
                            if progress_callback:
                                await progress_callback(stage=2, progress=60)
                            
                            # Извлечение и валидация JSON
                            data = _extract_json_from_text(description)
                            if not data:
                                logger.warning(f"⚠️ Model {model}: failed to extract JSON")
                                continue
                            
                            if progress_callback:
                                await progress_callback(stage=3, progress=80)
                            
                            is_valid, reason = _validate_food_data(data)
                            if not is_valid:
                                logger.warning(f"⚠️ Model {model}: validation failed - {reason}")
                                continue
                            
                            # Пост-обработка
                            portion_size = data.get('portion_size', 'medium')
                            if 'ingredients' in data:
                                data['ingredients'] = _calibrate_weights(data['ingredients'], portion_size)
                            
                            # Кэширование результата
                            _cache_result(image_hash, data)
                            
                            logger.info(f"✅ Model {model} returned valid data (confidence: {data.get('confidence', 'N/A')})")
                            
                            if progress_callback:
                                await progress_callback(stage=4, progress=100)
                            
                            return data, model
                        else:
                            error_text = await resp.text()
                            logger.warning(f"❌ Model {model} HTTP {resp.status}: {error_text[:200]}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Model {model} timeout after {timeout}s")
                continue
            except aiohttp.ClientError as e:
                logger.warning(f"❌ Model {model} connection error: {e}")
                continue
            except Exception as e:
                logger.warning(f"❌ Model {model} unexpected error: {type(e).__name__}: {e}")
                continue
        
        # Если все модели failed, ждём перед retry
        if attempt < retry_count - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    logger.error("❌ All vision models failed after all attempts")
    return None, None


async def identify_food_cascade(
    image_bytes: bytes,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Каскадное распознавание с улучшенной обработкой ошибок.
    """
    try:
        data, used_model = await identify_food_multimodel(
            image_bytes,
            progress_callback=progress_callback
        )
        
        if data and used_model:
            return {
                "success": True,
                "data": data,
                "model": used_model,
                "consensus": False,
                "confidence": data.get('confidence', 0.5)
            }
    except Exception as e:
        logger.error(f"❌ Cascade recognition error: {e}", exc_info=True)
    
    return {
        "success": False,
        "data": None,
        "model": None,
        "consensus": False,
        "confidence": 0.0,
        "error": "All models failed"
    }


async def get_simple_ingredients(image_bytes: bytes) -> Optional[List[str]]:
    """Быстрое извлечение списка ингредиентов (fallback)."""
    data, _ = await identify_food_multimodel(
        image_bytes,
        prompt=SIMPLE_INGREDIENTS_PROMPT,
        max_tokens=200
    )
    
    if not data:
        return None
    
    ingredients = data.get('ingredients', [])
    if ingredients and isinstance(ingredients[0], dict):
        return [ing.get('name', '') for ing in ingredients if ing.get('name')]
    if ingredients and isinstance(ingredients[0], str):
        return ingredients
    
    return None


# ========== ТРАНСКРИБАЦИЯ АУДИО ==========
async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """Распознавание голоса через Cloudflare Whisper."""
    if not BASE_URL:
        return None
    
    WHISPER_MODELS = [
        "@cf/openai/whisper-large-v3-turbo",
        "@cf/openai/whisper"
    ]
    
    try:
        audio_array = list(audio_bytes)
        payload = {"audio": audio_array, "language": language}
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        for model in WHISPER_MODELS:
            try:
                url = f"{BASE_URL}{model}"
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "").strip()
                            if text:
                                logger.info(f"✅ Transcription: {text[:50]}...")
                                return text
            except Exception:
                continue
        
        return None
    except Exception as e:
        logger.exception(f"❌ Transcription error: {e}")
        return None


# ========== БЭКВАРД-СОВМЕСТИМОСТЬ ==========
async def identify_dish_from_image(image_bytes: bytes) -> Optional[str]:
    """Возвращает только название блюда."""
    data, _ = await identify_food_multimodel(image_bytes, max_tokens=100)
    return data.get("dish_name") if data else None


async def analyze_food_image(image_bytes: bytes, prompt: str = None) -> Optional[str]:
    """Возвращает строку ингредиентов."""
    if prompt is None:
        prompt = SIMPLE_INGREDIENTS_PROMPT
    
    ingredients = await get_simple_ingredients(image_bytes)
    if ingredients:
        return ", ".join(ingredients)
    return None
