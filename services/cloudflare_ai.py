"""
Cloudflare Workers AI Integration for NutriBuddy
✅ Улучшено: профессиональные промпты для точного распознавания еды
✅ Добавлено: каскадная валидация, пост-обработка, калибровка весов
✅ Исправлено: надёжное извлечение JSON, обработка ошибок
"""
import aiohttp
import os
import logging
import asyncio
import json
import re
from typing import Optional, Dict, Any, Tuple, List

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Модели (порядок: сначала более точные, потом лёгкие)
VISION_MODELS = [
    "@cf/llava-hf/llava-1.5-7b-hf",      # Лучшее качество
    "@cf/unum/uform-gen2-qwen-500m",     # Быстрая проверка
]

WHISPER_MODELS = [
    "@cf/openai/whisper-large-v3-turbo", # Лучшее качество
    "@cf/openai/whisper",                 # Запасной вариант
]

# ========== ПРОМПТЫ ==========

FOOD_RECOGNITION_PROMPT = """You are an expert food nutritionist and computer vision specialist. Analyze this food image with surgical precision.

Return STRICTLY VALID JSON matching this schema:
{
    "dish_name": "Specific dish name in English (e.g., 'Grilled chicken breast with roasted vegetables')",
    "ingredients": [
        {
            "name": "ingredient name in English",
            "type": "protein|vegetable|carb|fat|sauce|garnish|other",
            "estimated_weight_grams": integer (10-500),
            "confidence": float (0.0-1.0)
        }
    ],
    "confidence": float (0.0-1.0),
    "meal_type": "breakfast|lunch|dinner|snack",
    "cooking_method": "grilled|fried|boiled|steamed|baked|raw|mixed",
    "portion_size": "small|medium|large",
    "notes": "Brief observation about presentation or uncertainty"
}

CRITICAL RULES:
1. DISH NAME: Be SPECIFIC. "Grilled salmon with lemon and dill" NOT "fish dish"
2. INGREDIENTS: List EVERY visible component:
   - Proteins: chicken, beef, fish, eggs, tofu, beans
   - Vegetables: tomatoes, lettuce, carrots, onions, peppers
   - Carbs: rice, pasta, bread, potatoes, quinoa
   - Fats: olive oil, butter, avocado, nuts
   - Sauces: mayonnaise, ketchup, soy sauce, dressing
   - Garnishes: parsley, lemon wedge, sesame seeds
3. WEIGHTS: Estimate realistically:
   - Small portion: 150-250g total
   - Medium: 300-450g total
   - Large: 500-700g total
   - Distribute among ingredients proportionally
4. CONFIDENCE: Be honest - 0.9+ for clear items, 0.5-0.7 for uncertain
5. COOKING METHOD: Identify from visual cues:
   - Grill marks → grilled
   - Golden crust → fried/baked
   - Steam/moisture → steamed/boiled
   - Raw texture → raw/salad

EXAMPLE OUTPUT:
{
    "dish_name": "Grilled chicken breast with quinoa and steamed broccoli",
    "ingredients": [
        {"name": "chicken breast", "type": "protein", "estimated_weight_grams": 150, "confidence": 0.95},
        {"name": "quinoa", "type": "carb", "estimated_weight_grams": 100, "confidence": 0.85},
        {"name": "broccoli", "type": "vegetable", "estimated_weight_grams": 80, "confidence": 0.90},
        {"name": "olive oil", "type": "fat", "estimated_weight_grams": 10, "confidence": 0.60}
    ],
    "confidence": 0.88,
    "meal_type": "lunch",
    "cooking_method": "grilled",
    "portion_size": "medium",
    "notes": "Well-lit image, clear visibility of components"
}

Return ONLY valid JSON. No markdown, no explanations, no extra text."""

SIMPLE_INGREDIENTS_PROMPT = """List visible food ingredients as a simple comma-separated list in English. Be specific: "chicken breast, brown rice, broccoli, olive oil" not just "meat, vegetables". Return only the list, nothing else."""

# ========== УТИЛИТЫ ==========

def _bytes_to_array(image_bytes: bytes) -> list:
    """Конвертирует байты изображения в массив для API."""
    return list(image_bytes)


def _extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Извлекает JSON из текста с поддержкой различных форматов.
    ✅ Улучшено: обработка markdown, экранирований, вложенных структур
    """
    if not text or not isinstance(text, str):
        return None
    
    original_text = text.strip()
    
    # 1. Убираем markdown блоки кода
    if '```json' in text:
        text = text.split('```json', 1)[1].split('```', 1)[0].strip()
    elif '```' in text:
        text = text.split('```', 1)[1].split('```', 1)[0].strip()
    
    # 2. Находим границы JSON объекта
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1 or end <= start:
        # Пробуем найти массив
        start_arr = text.find('[')
        end_arr = text.rfind(']')
        if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
            start, end = start_arr, end_arr
        else:
            logger.warning(f"❌ No JSON structure found in: {text[:100]}...")
            return None
    
    json_str = text[start:end+1]
    
    # 3. Очистка экранирований
    json_str = re.sub(r'\\(["\\])', r'\1', json_str)  # \" → ", \\ → \
    json_str = json_str.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
    
    # 4. Исправляем частые ошибки: одинарные кавычки → двойные
    # (только если это не внутри строки с экранированием)
    if "'dish_name'" in json_str or "'ingredients'" in json_str:
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
    
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            return data
        elif isinstance(data, list) and len(data) > 0:
            # Если вернули массив ингредиентов, оборачиваем в структуру
            return {"ingredients": data, "dish_name": "Mixed dish", "confidence": 0.7}
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ JSON decode failed: {e}. Snippet: {json_str[:200]}...")
        return None


def _validate_ingredient(ing: Any) -> bool:
    """Проверяет валидность одного ингредиента."""
    if not isinstance(ing, dict):
        return False
    
    name = ing.get('name', '')
    if not name or not isinstance(name, str) or len(name.strip()) < 2:
        return False
    
    # Проверка веса
    weight = ing.get('estimated_weight_grams')
    if weight is not None:
        if not isinstance(weight, (int, float)) or weight < 1 or weight > 2000:
            return False
    
    # Проверка типа
    valid_types = {'protein', 'vegetable', 'carb', 'fat', 'sauce', 'garnish', 'other'}
    ing_type = ing.get('type', 'other')
    if ing_type not in valid_types:
        ing['type'] = 'other'  # Исправляем, а не отклоняем
    
    # Проверка уверенности
    conf = ing.get('confidence')
    if conf is not None and (not isinstance(conf, (int, float)) or not 0 <= conf <= 1):
        ing['confidence'] = 0.7  # Значение по умолчанию
    
    return True


def _validate_food_data(data: Dict) -> Tuple[bool, str]:
    """
    Расширенная валидация данных о еде.
    Возвращает (is_valid, reason_if_invalid).
    """
    if not isinstance(data, dict):
        return False, "Not a dictionary"
    
    dish = data.get('dish_name', '')
    if not dish or not isinstance(dish, str) or len(dish.strip()) < 3:
        return False, "Invalid or missing dish_name"
    
    ingredients = data.get('ingredients', [])
    if not isinstance(ingredients, list):
        return False, "Ingredients not a list"
    
    if len(ingredients) == 0:
        return False, "Empty ingredients list"
    
    # Валидация каждого ингредиента
    valid_count = 0
    for ing in ingredients:
        if _validate_ingredient(ing):
            valid_count += 1
    
    if valid_count == 0:
        return False, "No valid ingredients"
    
    if valid_count < len(ingredients) * 0.5:
        logger.warning(f"⚠️ Only {valid_count}/{len(ingredients)} ingredients valid")
    
    # Проверка на бессмысленные названия
    meaningless = {'and', 'the', 'with', 'on', 'in', 'a', 'an', 'to', 'of', 'dish', 'plate', 'food', 'meal'}
    valid_names = [
        ing.get('name', '').lower().strip() 
        for ing in ingredients 
        if _validate_ingredient(ing)
    ]
    meaningful_count = sum(1 for name in valid_names if name not in meaningless and len(name) > 2)
    
    if meaningful_count < 1:
        return False, "No meaningful ingredient names"
    
    # Проверка общей уверенности
    confidence = data.get('confidence')
    if confidence is not None and (not isinstance(confidence, (int, float)) or confidence < 0.3):
        logger.warning(f"⚠️ Low confidence: {confidence}")
    
    return True, "OK"


def _calibrate_weights(ingredients: List[Dict], portion_size: str) -> List[Dict]:
    """
    Калибрует веса ингредиентов на основе размера порции.
    Стандартные диапазоны: small=200g, medium=350g, large=500g
    """
    if not ingredients:
        return ingredients
    
    # Целевые веса по типам ингредиентов
    TARGETS = {
        'small': {'total': 200, 'protein': 80, 'carb': 70, 'vegetable': 40, 'fat': 10},
        'medium': {'total': 350, 'protein': 120, 'carb': 130, 'vegetable': 80, 'fat': 20},
        'large': {'total': 500, 'protein': 180, 'carb': 200, 'vegetable': 100, 'fat': 20},
    }
    
    target = TARGETS.get(portion_size, TARGETS['medium'])
    
    # Группировка по типам
    by_type: Dict[str, List[Dict]] = {}
    for ing in ingredients:
        ing_type = ing.get('type', 'other')
        if ing_type not in by_type:
            by_type[ing_type] = []
        by_type[ing_type].append(ing)
    
    # Распределение весов
    for ing_type, items in by_type.items():
        target_weight = target.get(ing_type, target['vegetable'])
        if not items:
            continue
        
        # Если у AI уже есть веса, корректируем пропорционально
        current_total = sum(ing.get('estimated_weight_grams', 0) for ing in items)
        
        if current_total < 50 or current_total > target_weight * 2:
            # Перераспределяем равномерно
            weight_per_item = target_weight / len(items)
            for ing in items:
                ing['estimated_weight_grams'] = int(weight_per_item)
                ing['weight_calibrated'] = True
        else:
            # Масштабируем к целевому значению
            scale = target_weight / current_total
            for ing in items:
                old_weight = ing.get('estimated_weight_grams', 100)
                ing['estimated_weight_grams'] = int(old_weight * scale)
                ing['weight_calibrated'] = True
    
    return ingredients


def _merge_ingredients(ingredients_list: List[List[Dict]]) -> List[Dict]:
    """
    Объединяет списки ингредиентов от нескольких моделей, устраняя дубликаты.
    """
    merged = []
    seen = {}  # name_lower -> best ingredient
    
    for ingredients in ingredients_list:
        for ing in ingredients:
            if not _validate_ingredient(ing):
                continue
            
            name = ing.get('name', '').lower().strip()
            if not name:
                continue
            
            if name in seen:
                # Берём ингредиент с большей уверенностью
                if ing.get('confidence', 0) > seen[name].get('confidence', 0):
                    seen[name] = ing
            else:
                seen[name] = ing
    
    return list(seen.values())


# ========== ОСНОВНЫЕ ФУНКЦИИ ==========

async def identify_food_multimodel(
    image_bytes: bytes,
    prompt: str = None,
    max_tokens: int = 800,
    temperature: float = 0.1
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Пробует несколько vision-моделей для распознавания еды.
    Возвращает (data, model_name) или (None, None) при неудаче.
    ✅ Улучшено: валидация, пост-обработка, калибровка весов
    """
    if not BASE_URL:
        logger.error("❌ Cloudflare BASE_URL not configured")
        return None, None
    
    image_array = _bytes_to_array(image_bytes)
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if prompt is None:
        prompt = FOOD_RECOGNITION_PROMPT
    
    for model in VISION_MODELS:
        try:
            url = f"{BASE_URL}{model}"
            payload = {
                "image": image_array,
                "prompt": prompt,
                "max_tokens": max_tokens,
            }
            
            # Параметры модели
            if model == "@cf/llava-hf/llava-1.5-7b-hf":
                payload["temperature"] = temperature
            
            logger.info(f"🤖 Trying vision model: {model}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=90) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        description = result.get("result", {}).get("description", "").strip()
                        
                        if not description:
                            logger.warning(f"⚠️ Model {model} returned empty description")
                            continue
                        
                        logger.debug(f"📝 Raw AI response ({model}): {description[:400]}...")
                        
                        # Извлечение и валидация JSON
                        data = _extract_json_from_text(description)
                        
                        if not data:
                            logger.warning(f"⚠️ Model {model}: failed to extract JSON")
                            continue
                        
                        is_valid, reason = _validate_food_data(data)
                        if not is_valid:
                            logger.warning(f"⚠️ Model {model}: validation failed - {reason}")
                            continue
                        
                        # Пост-обработка: калибровка весов
                        portion_size = data.get('portion_size', 'medium')
                        if 'ingredients' in data:
                            data['ingredients'] = _calibrate_weights(data['ingredients'], portion_size)
                        
                        logger.info(f"✅ Model {model} returned valid data (confidence: {data.get('confidence', 'N/A')})")
                        return data, model
                        
                    else:
                        error_text = await resp.text()
                        logger.warning(f"❌ Model {model} HTTP {resp.status}: {error_text[:200]}")
                        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Model {model} timeout after 90s")
            continue
        except aiohttp.ClientError as e:
            logger.warning(f"❌ Model {model} connection error: {e}")
            continue
        except Exception as e:
            logger.warning(f"❌ Model {model} unexpected error: {type(e).__name__}: {e}")
            continue
    
    logger.error("❌ All vision models failed")
    return None, None


async def identify_food_cascade(image_bytes: bytes) -> Dict[str, Any]:
    """
    Каскадное распознавание: несколько моделей + консенсус.
    Возвращает объединённые результаты с метаинформацией.
    """
    results = []
    
    for model in VISION_MODELS:
        data, used_model = await identify_food_multimodel(image_bytes)
        if data and used_model:
            weight = 0.6 if used_model == VISION_MODELS[0] else 0.4
            results.append((used_model, data, weight))
    
    if not results:
        return {
            "success": False,
            "data": None,
            "model": None,
            "consensus": False,
            "confidence": 0.0,
            "error": "All models failed"
        }
    
    if len(results) == 1:
        model, data, weight = results[0]
        return {
            "success": True,
            "data": data,
            "model": model,
            "consensus": False,
            "confidence": data.get('confidence', weight)
        }
    
    # Консенсус для 2+ моделей
    return _build_consensus(results)


def _build_consensus(results: List[Tuple[str, Dict, float]]) -> Dict[str, Any]:
    """
    Строит консенсус из результатов нескольких моделей.
    """
    # 1. Dish name: голосование
    dish_votes = {}
    for _, data, weight in results:
        dish = data.get('dish_name', '')
        if dish:
            dish_votes[dish] = dish_votes.get(dish, 0) + weight
    
    best_dish = max(dish_votes, key=dish_votes.get) if dish_votes else "Unknown dish"
    
    # 2. Ингредиенты: объединение с дедупликацией
    all_ingredients = [data.get('ingredients', []) for _, data, _ in results]
    merged_ingredients = _merge_ingredients(all_ingredients)
    
    # 3. Мета-данные: усреднение
    confidences = [data.get('confidence', 0.5) for _, data, _ in results]
    avg_confidence = sum(confidences) / len(confidences)
    
    # 4. Выбор наиболее частых значений для категорий
    meal_types = [data.get('meal_type') for _, data, _ in results if data.get('meal_type')]
    cooking_methods = [data.get('cooking_method') for _, data, _ in results if data.get('cooking_method')]
    portion_sizes = [data.get('portion_size') for _, data, _ in results if data.get('portion_size')]
    
    def most_common(lst):
        if not lst:
            return None
        return max(set(lst), key=lst.count)
    
    consensus_data = {
        "dish_name": best_dish,
        "ingredients": merged_ingredients,
        "confidence": round(avg_confidence, 2),
        "meal_type": most_common(meal_types),
        "cooking_method": most_common(cooking_methods),
        "portion_size": most_common(portion_sizes),
        "consensus": True,
        "models_used": [r[0] for r in results]
    }
    
    return {
        "success": True,
        "data": consensus_data,
        "model": "consensus",
        "consensus": True,
        "confidence": avg_confidence
    }


async def get_simple_ingredients(image_bytes: bytes) -> Optional[List[str]]:
    """
    Быстрое извлечение списка ингредиентов (упрощённый промпт).
    Для случаев, когда не нужна полная структура.
    """
    data, _ = await identify_food_multimodel(
        image_bytes,
        prompt=SIMPLE_INGREDIENTS_PROMPT,
        max_tokens=200
    )
    
    if not data:
        return None
    
    ingredients = data.get('ingredients', [])
    
    # Если ингредиенты в новом формате (словари)
    if ingredients and isinstance(ingredients[0], dict):
        return [ing.get('name', '') for ing in ingredients if ing.get('name')]
    
    # Если в старом формате (строки)
    if ingredients and isinstance(ingredients[0], str):
        return ingredients
    
    return None


# ========== ТРАНСКРИБАЦИЯ АУДИО ==========

async def _convert_ogg_to_wav(ogg_bytes: bytes) -> Optional[bytes]:
    """Конвертирует OGG в WAV для Whisper."""
    try:
        if len(ogg_bytes) > 20 * 1024 * 1024:
            logger.warning("⚠️ Audio file too large (>20MB)")
            return None
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f_in:
            f_in.write(ogg_bytes)
            in_path = f_in.name
        
        out_path = in_path.replace('.ogg', '.wav')
        
        try:
            cmd = [
                'ffmpeg', '-i', in_path,
                '-ar', '16000', '-ac', '1',
                '-acodec', 'pcm_s16le', '-y',
                out_path
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
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
        logger.exception(f"❌ Conversion error: {e}")
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
    """Возвращает только название блюда (для обратной совместимости)."""
    data, _ = await identify_food_multimodel(image_bytes, max_tokens=100)
    return data.get("dish_name") if data else None


async def analyze_food_image(image_bytes: bytes, prompt: str = None) -> Optional[str]:
    """Возвращает строку ингредиентов (для обратной совместимости)."""
    if prompt is None:
        prompt = SIMPLE_INGREDIENTS_PROMPT
    
    ingredients = await get_simple_ingredients(image_bytes)
    if ingredients:
        return ", ".join(ingredients)
    return None
