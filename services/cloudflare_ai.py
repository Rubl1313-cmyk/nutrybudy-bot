"""
Cloudflare Workers AI Integration for NutriBuddy
УЛУЧШЕНО: Progressive loading, надёжное извлечение JSON, кэширование
Добавлено: Retry-логика, валидация, fallback-механизмы, прогресс-бар
"""
import aiohttp
import asyncio
import hashlib
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from functools import lru_cache

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
    {"id": "@cf/llava-hf/llava-1.5-7b-hf", "priority": 1, "timeout": 120, "weight": 0.6},
    {"id": "@cf/unum/uform-gen2-qwen-500m", "priority": 2, "timeout": 90, "weight": 0.4},
]

# Кэш результатов (hash изображения → результат)
_RECOGNITION_CACHE: Dict[str, Tuple[Dict, datetime]] = {}
_CACHE_TTL = 3600  # 1 час

# ========== ЕДИНЫЙ УЛУЧШЕННЫЙ ПРОМПТ ДЛЯ LLAVA ==========
LLAVA_ENSEMBLE_PROMPT = """You are an expert food recognition AI. Analyze the image and return a JSON with the following fields:
- dish_name: The FULL NAME of the dish (e.g., "beef shashlik", "chicken soup", "borscht"). NEVER return a single ingredient like "beef" or "chicken" here.
- dish_name_ru: The Russian name of the dish (e.g., "шашлык из говядины", "куриный суп", "борщ").
- category: one of ["soup", "main", "salad", "skewers", "side", "dessert", "other"].
- cooking_method: how it's cooked (e.g., "grilled", "fried", "boiled", "baked").
- confidence: overall confidence 0.0-1.0.
- ingredients: list of visible ingredients, each with name, type (protein, carb, vegetable, fat, sauce), estimated weight in grams, confidence.

CRITICAL RULES:
1. dish_name MUST be a complete dish, never an ingredient.
2. If you see meat on sticks/skewers, dish_name must include "shashlik" or "kebabs".
3. If you see a red soup with beets, it's "borscht".
4. If you see a thick piece of meat with grill marks, it's "steak".
5. If you see meat chunks in sauce, it's "stew" or "goulash".
6. Always provide both English and Russian names.

Return ONLY valid JSON, no extra text."""

# Промпт для UForm (оставляем для детального перечисления ингредиентов)
UFORM_DETAILED_PROMPT = """You are an expert at identifying food ingredients from images.

CRITICAL RULES:
- White crystals on surface → salt (соль), NOT rice
- Green herb sprigs → parsley/dill/rosemary (петрушка/укроп/розмарин), NOT onion
- Brown particles → pepper/spices (перец/специи)
- Dark liquid → soy sauce (соевый соус)
- Small green leaves → basil (базилик)

Format: ingredient1:type1, ingredient2:type2
Types: protein, carb, vegetable, fat, sauce, herb, spice, other

Examples:
- pork:protein, salt:spice, rosemary:herb, black pepper:spice
- salmon:protein, rice:carb, soy sauce:sauce, cucumber:vegetable

List all visible food ingredients:"""

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
    ✅ ИСПРАВЛЕНО: обработка _ → _, " → "
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
    """Проверяет валидность одного ингредиента для нового формата."""
    if not isinstance(ing, dict):
        return False

    # Проверяем обязательные поля для нового формата
    name = ing.get('name', '')
    if not name or not isinstance(name, str) or len(name.strip()) < 2:
        return False

    # Проверяем category
    valid_categories = {'protein', 'carb', 'vegetable', 'fruit', 'fat', 'sauce', 'other'}
    category = ing.get('category', '')
    if category not in valid_categories:
        # Пробуем старый формат с 'type'
        valid_types = {'protein', 'vegetable', 'carb', 'fat', 'sauce', 'garnish', 'other'}
        type_field = ing.get('type', '')
        if type_field not in valid_types:
            ing['type'] = 'other'
        else:
            ing['category'] = type_field

    weight = ing.get('estimated_weight_grams')
    if weight is not None:
        if not isinstance(weight, (int, float)) or weight < 1 or weight > 2000:
            ing['estimated_weight_grams'] = 100

    conf = ing.get('confidence')
    if conf is None or not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        ing['confidence'] = 0.7

    return True

def _convert_food_expert_format(data: Dict) -> Dict:
    """
    Конвертирует формат FoodExpert-AI в формат бота
    """
    if not data:
        return data

    # Конвертируем основные поля
    converted_data = {
        'dish_name': data.get('dish_name', 'unknown dish'),
        'category': data.get('category', 'main'),
        'confidence': data.get('confidence_overall', 0.8),
        'preparation_style': data.get('cooking_method', 'mixed'),
        'portion_size': data.get('portion_size', 'medium'),
        'meal_type': data.get('meal_context', 'lunch'),
        'cuisine': data.get('cuisine', 'other')
    }

    # Конвертируем ингредиенты
    ingredients = data.get('ingredients', [])
    converted_ingredients = []

    for ing in ingredients:
        converted_ing = {
            'name': ing.get('name', ''),
            'name_ru': ing.get('name_ru', ing.get('name', '')),
            'type': ing.get('type', 'other'),
            'estimated_weight_grams': ing.get('estimated_weight_grams', 100),
            'confidence': ing.get('confidence', 0.8),
            'visual_cue': ing.get('visual_cue', ''),
            'weight_calibrated': True
        }
        converted_ingredients.append(converted_ing)

    converted_data['ingredients'] = converted_ingredients

    # Добавляем дополнительные поля
    if 'allergens_detected' in data:
        converted_data['allergens'] = data['allergens_detected']

    if 'reasoning_summary' in data:
        converted_data['reasoning'] = data['reasoning_summary']

    logger.info(f"🔄 Converted FoodExpert-AI format: {len(converted_ingredients)} ingredients, dish: {converted_data['dish_name']}")
    return converted_data

def _fix_protein_identification(data: Dict) -> Dict:
    """
    Обрабатывает результаты AI для нового формата ингредиентов.
    Конвертирует в формат, ожидаемый ботом.
    """
    if not data or 'ingredients' not in data:
        return data

    ingredients = data.get('ingredients', [])

    # Конвертируем новый формат в старый для совместимости
    converted_ingredients = []

    for ing in ingredients:
        # Конвертируем category в type
        category_map = {
            'protein': 'protein',
            'carb': 'carb', 
            'vegetable': 'vegetable',
            'fruit': 'vegetable',  # фрукты как овощи для КБЖУ
            'fat': 'fat',
            'sauce': 'sauce',
            'other': 'other'
        }

        converted_ing = {
            'name': ing.get('name', ''),
            'type': category_map.get(ing.get('category', 'other'), 'other'),
            'estimated_weight_grams': ing.get('estimated_weight_grams', 100),
            'confidence': ing.get('confidence', 0.8)
        }

        # Добавляем весовую калибровку если нужно
        if 'weight_calibrated' not in converted_ing:
            converted_ing['weight_calibrated'] = True

        converted_ingredients.append(converted_ing)

    # Создаем старый формат для совместимости
    old_format_data = {
        'ingredients': converted_ingredients,
        'confidence': data.get('overall_confidence', 0.8),
        'meal_type': data.get('meal_type', 'lunch')
    }

    # 🔧 ИСПОЛЬЗУЕМ НОВУЮ ФУНКЦИЮ ИЗ dish_db ДЛЯ ОПРЕДЕЛЕНИЯ БЛЮДА ПО ИНГРЕДИЕНТАМ
    from services.dish_db import identify_known_dish_by_ingredients
    ingredient_names_en = [ing['name'] for ing in converted_ingredients]  # английские названия
    prep_style = data.get('preparation_style', 'mixed')
    dish_name = identify_known_dish_by_ingredients(ingredient_names_en, prep_style)

    if dish_name:
        old_format_data['dish_name'] = dish_name
        logger.info(f"🎯 Identified known dish: {dish_name}")
    else:
        # Генерируем название на основе ингредиентов (как раньше)
        prep_style = data.get('preparation_style', 'mixed')
        protein_names = [ing['name'] for ing in converted_ingredients if ing['type'] == 'protein']
        carb_names = [ing['name'] for ing in converted_ingredients if ing['type'] == 'carb']

        if protein_names and carb_names:
            if prep_style == 'salad':
                old_format_data['dish_name'] = f"{protein_names[0]} with {carb_names[0]} salad"
            else:
                old_format_data['dish_name'] = f"{protein_names[0]} with {carb_names[0]}"
        elif protein_names:
            old_format_data['dish_name'] = protein_names[0]
        elif carb_names:
            old_format_data['dish_name'] = carb_names[0]
        else:
            old_format_data['dish_name'] = 'mixed dish'

    logger.info(f"🔄 Converted AI result: {len(converted_ingredients)} ingredients, dish: {old_format_data['dish_name']}")

    return old_format_data
    
# ========== УДАЛЁН ДУБЛИРУЮЩИЙСЯ СЛОВАРЬ known_dishes И ФУНКЦИЯ _identify_known_dish ==========

def _validate_food_data(data: Dict) -> Tuple[bool, str]:
    """Валидация данных о еде для нового формата."""
    if not isinstance(data, dict):
        return False, "Not a dictionary"

    # Новый формат - проверяем ingredients
    if 'ingredients' in data:
        ingredients = data.get('ingredients', [])
        if not isinstance(ingredients, list) or len(ingredients) == 0:
            return False, "Empty ingredients list"

        # Проверяем каждый ингредиент
        valid_count = 0
        for ing in ingredients:
            if _validate_ingredient(ing):
                valid_count += 1

        if valid_count == 0:
            return False, "No valid ingredients"

        return True, "OK"

    # Старый формат - для совместимости
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
async def identify_food(
    image_bytes: bytes,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Улучшенное каскадное распознавание с пост-обработкой
    """
    try:
        # Используем новый ансамбль моделей
        data, used_model = await identify_food_ensemble(
            image_bytes,
            model_indices=[0, 1],  # LLaVA + UForm
            progress_callback=progress_callback
        )

        if data and used_model:
            # Пост-обработка: исправляем типичные ошибки
            logger.info("🔧 Applying post-processing error fixes...")
            original_dish = data.get('dish_name', 'unknown')
            data = _fix_common_recognition_errors(data)
            final_dish = data.get('dish_name', 'unknown')

            if original_dish != final_dish:
                logger.info(f"🔧 Fixed dish name: {original_dish} → {final_dish}")

            return {
                "success": True,
                "data": data,
                "model": used_model,
                "consensus": True,  # Ансамбль обеспечивает консенсус
                "confidence": data.get('confidence', 0.5),
                "fixes_applied": original_dish != final_dish
            }
    except Exception as e:
        logger.error(f"❌ Enhanced recognition error: {e}", exc_info=True)

    return {
        "success": False,
        "data": None,
        "model": None,
        "consensus": False,
        "confidence": 0.0,
        "error": "All models failed"
    }

def _fix_common_recognition_errors(data: Dict) -> Dict:
    """Исправляет типичные ошибки с ПРИОРИТЕТОМ на шашлык и борщ"""
    if not data or 'dish_name' not in data:
        return data

    dish_name = data.get('dish_name', '').lower()
    ingredients = data.get('ingredients', [])
    ingredient_names = [ing.get('name', '').lower() for ing in ingredients]
    cooking_method = data.get('cooking_method', '').lower()

    # ========== НОВАЯ ПРОВЕРКА: если dish_name – это просто ингредиент ==========
    ingredient_only = {'beef', 'pork', 'chicken', 'lamb', 'meat', 'fish', 'turkey',
                       'говядина', 'свинина', 'курица', 'баранина', 'мясо', 'рыба'}
    if dish_name in ingredient_only:
        # Пытаемся определить блюдо по ингредиентам и визуальным признакам
        logger.info(f"⚠️ dish_name is ingredient '{dish_name}', calling expert analysis")
        expert_result = _expert_food_analysis(data)
        if expert_result.get('dish_name') and expert_result['dish_name'].lower() != dish_name:
            data = expert_result
            logger.info(f"🔧 Fixed ingredient dish: {dish_name} → {data['dish_name']}")

    # ========== ПРИОРИТЕТ 1: ПРОВЕРКА НА ШАШЛЫК vs СТЕЙК ==========
    # Проверяем визуальные признаки ДАЖЕ если cooking_method = "unknown"

    has_meat_protein = any(meat in ingredient_names for meat in 
                          ['pork', 'beef', 'chicken', 'lamb', 'turkey', 
                           'свинина', 'говядина', 'курица', 'баранина'])

    # Ищем признаки шампуров/шашлыка в visual_cues
    visual_cues = data.get('visual_cues', '').lower()
    skewer_indicators = ['stick', 'skewer', 'wooden', 'metal', 'threaded', 'cubes']
    has_skewer_hint = any(ind in visual_cues for ind in skewer_indicators)

    # Ищем признаки стейка
    steak_indicators = ['thick', 'cut', 'piece', 'slab', 'fillet', 'chop']
    has_steak_hint = any(ind in visual_cues for ind in steak_indicators)

    # Ищем признаки гриля
    grill_indicators = ['grilled', 'grill', 'charred', 'brown', 'seared']
    has_grill_hint = any(ind in dish_name or ind in ' '.join(ingredient_names) 
                        for ind in grill_indicators)

    # 🎯 УМНАЯ ЛОГИКА: Шашлык vs Стейк vs Нарезанное мясо
    # Шашлык = кубики мяса + характерные признаки (даже без шампуров)
    # Стейк = цельный кусок мяса
    # Нарезанное мясо = кусочки, но не шашлык

    if has_meat_protein and (cooking_method in ['grilled', 'unknown', '']):
        if data.get('confidence', 0) > 0.7:
            # Признаки именно ШАШЛЫКА (даже без шампуров)
            shashlik_indicators = ['cubes', 'cubed', 'chunks', 'pieces', 'diced']
            # Дополнительные признаки шашлыка:
            # - Лук и овощи (обычно с шашлыком)
            # - Соус/маринад (характерно для шашлыка)
            # - Маленькие ровные кусочки (не большой кусок как стейк)
            has_shashlik_pieces = any(ind in visual_cues for ind in shashlik_indicators)
            has_onion = any(onion in visual_cues for onion in ['onion', 'лук'])
            has_sauce = any(sauce in visual_cues for sauce in ['sauce', 'маринад', 'marinade'])

            # Признаки СТЕЙКА (большой цельный кусок)
            has_large_piece = any(ind in visual_cues for ind in ['thick', 'large', 'whole', 'single'])

            # 🥩 ЛОГИКА ОПРЕДЕЛЕНИЯ:
            if has_skewer_hint:
                # Есть шампуры = точно шашлык
                dish_type = 'shashlik'
                logger.info(f"🍢 Шашлык определен по шампурам")
            elif has_shashlik_pieces and (has_onion or has_sauce) and not has_large_piece:
                # Кусочки + лук/соус = вероятно шашлык (без шампуров)
                dish_type = 'shashlik'
                logger.info(f"🍢 Шашлык определен по кусочкам + лук/соус")
            elif has_shashlik_pieces and not has_large_piece:
                # Маленькие кусочки = возможно шашлык (но меньше уверенности)
                dish_type = 'shashlik'
                logger.info(f"🍢 Шашлык определен по кусочкам (меньшая уверенность)")
            elif has_steak_hint or has_large_piece:
                # Большой кусок = это стейк
                dish_type = 'steak'
                logger.info(f"🥩 Стейк определен по большому куску")
            else:
                # Неясно - оставляем как есть или определяем как grilled meat
                logger.info(f"❓ Неясно, оставляем оригинальное определение: {dish_name}")
                return data

            if dish_type == 'shashlik':
                # ✅ Это ШАШЛЫК
                meat_type = 'pork'  # по умолчанию
                meat_type_ru = 'свиной'

                if 'beef' in ingredient_names or 'говядина' in ingredient_names:
                    meat_type = 'beef'
                    meat_type_ru = 'говяжий'
                elif 'chicken' in ingredient_names or 'курица' in ingredient_names:
                    meat_type = 'chicken'
                    meat_type_ru = 'куриный'
                elif 'lamb' in ingredient_names or 'баранина' in ingredient_names:
                    meat_type = 'lamb'
                    meat_type_ru = 'бараний'
                elif 'pork' in ingredient_names or 'свинина' in ingredient_names:
                    meat_type = 'pork'
                    meat_type_ru = 'свиной'

                # УСТАНАВЛИВАЕМ ШАШЛЫК
                data['dish_name'] = f"{meat_type} shashlik"
                data['dish_name_ru'] = f"{meat_type_ru} шашлык"
                data['category'] = 'skewers'
                data['cooking_method'] = 'grilled'
                data['has_skewers'] = has_skewer_hint  # Может быть False если без шампуров
                data['confidence'] = max(data.get('confidence', 0.8), 0.85)

                logger.info(f"🔧 FORCE-FIXED to shashlik: {data['dish_name']} / {data['dish_name_ru']}")
                return data

            elif dish_type == 'steak':
                # ✅ Это СТЕЙК (не трогаем, но можем улучшить)
                meat_type = 'pork'  # по умолчанию
                meat_type_ru = 'свиной'

                if 'beef' in ingredient_names or 'говядина' in ingredient_names:
                    meat_type = 'beef'
                    meat_type_ru = 'говяжий'
                elif 'chicken' in ingredient_names or 'курица' in ingredient_names:
                    meat_type = 'chicken'
                    meat_type_ru = 'куриный'
                elif 'lamb' in ingredient_names or 'баранина' in ingredient_names:
                    meat_type = 'lamb'
                    meat_type_ru = 'бараний'

                # Улучшаем определение стейка
                data['dish_name'] = f"{meat_type} steak"
                data['dish_name_ru'] = f"{meat_type_ru} стейк"
                data['category'] = 'main'
                data['cooking_method'] = 'grilled'
                data['has_skewers'] = False
                data['confidence'] = max(data.get('confidence', 0.8), 0.85)

                logger.info(f"🥩 FORCE-FIXED to steak: {data['dish_name']} / {data['dish_name_ru']}")
                return data

    # ========== ПРИОРИТЕТ 2: ПРОВЕРКА НА БОРЩ ==========
    has_beets = any(beet in ingredient_names for beet in 
                   ['beet', 'beetroot', 'beets', 'свекла', 'свёкла'])
    has_cabbage = any(cab in ingredient_names for cab in 
                     ['cabbage', 'капуста'])
    has_sour_cream = any(cream in ingredient_names for cream in 
                        ['sour cream', 'smetana', 'сметана'])
    is_red_soup = data.get('visual_cues', '').lower()
    is_red_soup = is_red_soup and ('red' in is_red_soup or 'pink' in is_red_soup)

    if (has_beets and (has_cabbage or has_sour_cream)) or \
       (has_beets and data.get('is_soup')) or \
       ('borscht' in dish_name) or ('борщ' in dish_name):
        data['dish_name'] = 'borscht'
        data['dish_name_ru'] = 'борщ'
        data['category'] = 'soup'
        data['cooking_method'] = 'boiled'
        data['is_soup'] = True
        data['confidence'] = max(data.get('confidence', 0.8), 0.9)

        logger.info(f"🔧 FORCE-FIXED to borscht: {data['dish_name']}")
        return data

    # ========== СТАРАЯ ЛОГИКА ДЛЯ ДРУГИХ СЛУЧАЕВ ==========
    # Категории и переводы
    meat_translations = {
        'pork': ('свинина', 'свиной'),
        'beef': ('говядина', 'говяжий'),
        'chicken': ('курица', 'куриный'),
        'lamb': ('баранина', 'бараний'),
        'turkey': ('индейка', 'индейка'),
        'fish': ('рыба', 'рыбный'),
        'salmon': ('лосось', 'лосось'),
    }

    def _contains_any(name_list: List[str], keywords: List[str]) -> bool:
        return any(any(kw in (name or '') for kw in keywords) for name in name_list)

    # ЗАЩИТА: ingredient ≠ dish
    ingredient_only_dishes = ['beef', 'pork', 'chicken', 'lamb', 'meat', 'fish', 'turkey',
                              'говядина', 'свинина', 'курица', 'баранина', 'мясо', 'рыба', 'индейка']

    if dish_name in ingredient_only_dishes:
        meat_key = None
        for m in ['pork', 'beef', 'chicken', 'lamb', 'turkey', 'fish']:
            if m in dish_name:
                meat_key = m
                break

        if meat_key and meat_key in meat_translations:
            ru_base, _ = meat_translations[meat_key]
            if cooking_method == 'grilled':
                data['dish_name'] = f"{meat_key} grilled"
                data['dish_name_ru'] = f"{ru_base} жареный на гриле"
            elif cooking_method == 'fried':
                data['dish_name'] = f"{meat_key} fried"
                data['dish_name_ru'] = f"{ru_base} жареный"
            elif cooking_method == 'baked':
                data['dish_name'] = f"{meat_key} baked"
                data['dish_name_ru'] = f"{ru_base} запеченный"
            elif cooking_method == 'boiled':
                data['dish_name'] = f"{meat_key} boiled"
                data['dish_name_ru'] = f"{ru_base} отварной"
            else:
                data['dish_name'] = f"{meat_key} dish"
                data['dish_name_ru'] = f"Блюдо из {ru_base}"

        logger.info(f"🔧 FIXED: Changed ingredient '{dish_name}' to dish '{data['dish_name']}'")

    logger.info(f"🔧 Final result: {data['dish_name']} / {data.get('dish_name_ru', 'N/A')}")
    return data

def _filter_non_food_items(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Фильтрует бытовые предметы и непищевые объекты из результатов распознавания.
    Возвращает отфильтрованные данные и информацию об удаленных элементах.
    """
    if not data or 'ingredients' not in data:
        return data

    # Список бытовых предметов и непищевых объектов
    NON_FOOD_ITEMS = {
        # 🍽️ Столовые приборы
        'fork', 'spoon', 'knife', 'chopsticks', 'forks', 'spoons', 'knives',
        'вилка', 'ложка', 'нож', 'палочки', 'вилки', 'ложки', 'ножи',

        # 🍽️ Посуда
        'plate', 'bowl', 'cup', 'glass', 'mug', 'saucer', 'platter', 'tray',
        'тарелка', 'миска', 'чашка', 'стакан', 'кружка', 'блюдце', 'поднос', 'лоток',
        'plates', 'bowls', 'cups', 'glasses', 'mugs', 'тарелки', 'миски', 'чашки',

        # 🔪 Кухонные принадлежности
        'cutting board', 'board', 'napkin', 'tissue', 'paper towel',
        'разделочная доска', 'доска', 'салфетка', 'бумажное полотенце',

        # 🕯️ Другие непищевые объекты
        'table', 'chair', 'menu', 'book', 'phone', 'bottle cap',
        'стол', 'стул', 'меню', 'книга', 'телефон', 'крышка бутылки',

        # 🧼 Чистящие средства
        'soap', 'detergent', 'sponge', 'cloth', 'towel',
        'мыло', 'моющее средство', 'губка', 'ткань', 'полотенце',

        # 📦 Упаковка
        'wrapper', 'package', 'bag', 'container', 'box', 'foil', 'plastic',
        'обертка', 'упаковка', 'пакет', 'контейнер', 'коробка', 'фольга', 'пластик',

        # 🌿 Декоративные элементы (только НЕпищевые)
        'flower', 'leaf', 'decoration', 'garnish',
        'цветок', 'лист', 'декорация', 'гарнир',

        # ⚠️ Мусор и посторонние предметы
        'trash', 'dirt', 'dust', 'hair', 'string', 'paper',
        'мусор', 'грязь', 'пыль', 'волос', 'нить', 'бумага'
    }

    # Также фильтруем названия блюд, которые являются бытовыми предметами
    NON_FOOD_DISHES = {
        'plate', 'bowl', 'cup', 'glass', 'fork', 'spoon', 'knife',
        'тарелка', 'миска', 'чашка', 'стакан', 'вилка', 'ложка', 'нож'
    }

    original_ingredients = data.get('ingredients', [])
    filtered_ingredients = []
    removed_items = []

    for ingredient in original_ingredients:
        ingredient_name = ingredient.get('name', '').lower().strip()

        # Проверяем, является ли ингредиент бытовым предметом
        is_non_food = False

        # Прямое совпадение
        if ingredient_name in NON_FOOD_ITEMS:
            is_non_food = True

        # Проверка на вхождение ключевых слов
        elif any(non_food in ingredient_name for non_food in NON_FOOD_ITEMS):
            is_non_food = True

        # Дополнительные проверки для составных слов
        elif any(keyword in ingredient_name for keyword in ['plastic', 'metal', 'wood', 'glass', 'paper']):
            # Исключаем случаи, когда это может быть пищей (например, "wood ear mushrooms")
            if not any(food_word in ingredient_name for food_word in ['mushroom', 'vegetable', 'food']):
                is_non_food = True

        if is_non_food:
            removed_items.append(ingredient_name)
            logger.info(f"🚫 Filtered non-food item: {ingredient_name}")
        else:
            filtered_ingredients.append(ingredient)

    # Фильтруем название блюда
    dish_name = data.get('dish_name', '').lower().strip()
    if dish_name in NON_FOOD_DISHES:
        logger.warning(f"🚫 Filtered non-food dish name: {dish_name}")
        # Если название блюда - это бытовой предмет, сбрасываем результат
        return {
            'success': False,
            'error': f'Detected non-food item: {dish_name}',
            'filtered_items': removed_items,
            'original_dish': dish_name
        }

    # Обновляем данные
    result = data.copy()
    result['ingredients'] = filtered_ingredients

    # Логируем результаты фильтрации
    if removed_items:
        logger.info(f"🧹 Filtered {len(removed_items)} non-food items: {', '.join(removed_items)}")
        logger.info(f"✅ Kept {len(filtered_ingredients)} food ingredients")

    # Если после фильтрации не осталось ингредиентов, помечаем как подозрительный результат
    if len(filtered_ingredients) == 0 and len(original_ingredients) > 0:
        logger.warning(f"⚠️ All ingredients were filtered as non-food items")
        result['suspicious'] = True
        result['warning'] = 'All detected items appear to be non-food objects'

    # Добавляем информацию о фильтрации
    result['filter_info'] = {
        'original_count': len(original_ingredients),
        'filtered_count': len(filtered_ingredients),
        'removed_items': removed_items
    }

    return result

def _parse_uform_response(response_text: str) -> List[Dict[str, Any]]:
    """
    Парсит ответ UForm модели в формате текста.
    Поддерживает два формата:
    1. "ingredient1, ingredient2, ingredient3" - простой список
    2. "ingredient1:type1, ingredient2:type2" - с типами
    """
    if not response_text:
        return []

    ingredients = []

    # Очищаем текст от лишних символов
    cleaned_text = response_text.strip().lower()

    # UForm часто возвращает буллет-листы/строки. Нормализуем в список токенов.
    cleaned_text = cleaned_text.replace('\n', ',')
    cleaned_text = cleaned_text.replace(';', ',')

    # Разделяем по запятым
    items = [item.strip() for item in cleaned_text.split(',') if item.strip()]

    for item in items:
        # Убираем буллеты/нумерацию типа "- beef", "* beef", "1. beef"
        name_candidate = item.strip()
        while name_candidate.startswith(('-', '*')):
            name_candidate = name_candidate[1:].strip()
        if len(name_candidate) > 2 and name_candidate[0].isdigit() and name_candidate[1] in {'.', ')'}:
            name_candidate = name_candidate[2:].strip()

        if ':' in name_candidate:
            # Формат с типами: "beef:protein"
            name, ingredient_type = name_candidate.split(':', 1)
            name = name.strip()
            ingredient_type = ingredient_type.strip()

            # Валидация типа
            valid_types = ['protein', 'carb', 'vegetable', 'fat', 'sauce', 'spice']
            if ingredient_type not in valid_types:
                ingredient_type = 'other'  # тип по умолчанию
        else:
            # Простой формат: "beef"
            name = name_candidate.strip()
            ingredient_type = _guess_ingredient_type(name)

        name = name.strip(' \t\r\n-•*')

        if name and len(name) > 1:  # фильтруем пустые и слишком короткие
            ingredients.append({
                'name': name,
                'type': ingredient_type,
                'confidence': 0.7,  # базовая уверенность для UForm
                'source': 'uform_text'
            })

    logger.info(f"📝 Parsed {len(ingredients)} ingredients from UForm text response")
    return ingredients

def _guess_ingredient_type(ingredient_name: str) -> str:
    """
    Определяет тип ингредиента по названию на основе эвристики.
    """
    name = ingredient_name.lower()

    # Белковые продукты
    protein_keywords = [
        'beef', 'pork', 'chicken', 'turkey', 'lamb', 'veal', 'duck',
        'salmon', 'tuna', 'cod', 'trout', 'fish', 'shrimp', 'crab',
        'egg', 'cheese', 'tofu', 'beans', 'lentils', 'peas',
        'говядина', 'свинина', 'курица', 'индейка', 'баранина', 'рыба', 'яйцо', 'сыр'
    ]

    # Углеводы
    carb_keywords = [
        'rice', 'pasta', 'bread', 'potato', 'noodles', 'couscous', 'quinoa',
        'flour', 'oats', 'barley', 'bulgur', 'rice', 'macaroni',
        'рис', 'паста', 'хлеб', 'картошка', 'картофель', 'лапша', 'мука'
    ]

    # Овощи
    vegetable_keywords = [
        'tomato', 'onion', 'garlic', 'carrot', 'bell pepper', 'cucumber',
        'lettuce', 'spinach', 'broccoli', 'cauliflower', 'cabbage', 'mushroom',
        'zucchini', 'eggplant', 'pumpkin', 'beetroot', 'corn', 'peas',
        'tomato', 'помидор', 'лук', 'чеснок', 'морковь', 'перец', 'огурец', 'салат',
        'капуста', 'грибы', 'кабачок', 'баклажан', 'тыква', 'свекла', 'кукуруза'
    ]

    # Жиры и соусы
    fat_keywords = [
        'oil', 'butter', 'cream', 'mayonnaise', 'avocado', 'nuts', 'seeds',
        'olive', 'coconut', 'fat', 'grease',
        'масло', 'сливки', 'майонез', 'авокадо', 'орехи', 'жиры'
    ]

    # Соусы и специи
    sauce_keywords = [
        'sauce', 'ketchup', 'mustard', 'soy sauce', 'vinegar', 'lemon',
        'herbs', 'spices', 'salt', 'pepper', 'paprika', 'cumin',
        'соус', 'кетчуп', 'горчица', 'уксус', 'лимон', 'травы', 'специи', 'соль'
    ]

    if any(keyword in name for keyword in protein_keywords):
        return 'protein'
    elif any(keyword in name for keyword in carb_keywords):
        return 'carb'
    elif any(keyword in name for keyword in vegetable_keywords):
        return 'vegetable'
    elif any(keyword in name for keyword in fat_keywords):
        return 'fat'
    elif any(keyword in name for keyword in sauce_keywords):
        return 'sauce'
    else:
        return 'other'

def _merge_ensemble_results(valid_results: List[Tuple[Dict, str, float]]) -> Dict[str, Any]:
    """
    Умно объединяет результаты от нескольких моделей ансамбля.
    Приоритет: лучшее название блюда + объединенные ингредиенты
    """
    logger.info(f"🔄 Merging results from {len(valid_results)} models...")

    # 1. Выбираем лучшее название блюда по взвешенной уверенности
    best_dish_data = None
    best_dish_score = -1

    for data, model_name, weight in valid_results:
        dish_confidence = data.get('confidence', 0) * weight
        if dish_confidence > best_dish_score:
            best_dish_score = dish_confidence
            best_dish_data = data

    if not best_dish_data:
        return valid_results[0][0]  # fallback

    # 2. Собираем все ингредиенты от всех моделей
    all_ingredients = []
    ingredient_map = {}  # name -> [ingredient_data, sources]

    for data, model_name, weight in valid_results:
        ingredients = data.get('ingredients', [])
        model_confidence = data.get('confidence', 0)

        for ing in ingredients:
            ing_name = ing.get('name', '').lower().strip()
            if not ing_name:
                continue

            # Нормализуем название ингредиента
            normalized_name = ing_name.lower()

            if normalized_name not in ingredient_map:
                ingredient_map[normalized_name] = {
                    'data': ing.copy(),
                    'sources': [],
                    'total_confidence': 0,
                    'detection_count': 0
                }

            # Добавляем информацию о детекции
            ingredient_map[normalized_name]['sources'].append({
                'model': model_name,
                'confidence': ing.get('confidence', 0),
                'weight': weight,
                'model_confidence': model_confidence
            })

            # Суммируем взвешенную уверенность
            weighted_conf = ing.get('confidence', 0) * weight * model_confidence
            ingredient_map[normalized_name]['total_confidence'] += weighted_conf
            ingredient_map[normalized_name]['detection_count'] += 1

            # Обновляем данные лучшим вариантом
            current_weighted = ing.get('confidence', 0) * weight
            best_weighted = ingredient_map[normalized_name]['data'].get('confidence', 0) * 1.0

            if current_weighted > best_weighted:
                ingredient_map[normalized_name]['data'] = ing.copy()

    # 3. Фильтруем и объединяем ингредиенты
    merged_ingredients = []

    for name, info in ingredient_map.items():
        # Усредняем уверенность по всем моделям
        avg_confidence = info['total_confidence'] / info['detection_count']

        # Учитываем количество моделей, которые обнаружили ингредиент
        detection_bonus = 0.1 * (info['detection_count'] - 1)  # +0.1 за каждую дополнительную модель
        final_confidence = min(avg_confidence + detection_bonus, 1.0)

        # Берем ингредиент только если уверенность достаточно высока
        if final_confidence >= 0.3:  # Порог можно настроить
            ingredient = info['data'].copy()
            ingredient['confidence'] = final_confidence

            # Добавляем мета-информацию
            ingredient['detected_by'] = [s['model'] for s in info['sources']]
            ingredient['detection_count'] = info['detection_count']

            merged_ingredients.append(ingredient)
            logger.info(f"🔗 Merged ingredient: {name} (confidence: {final_confidence:.2f}, models: {info['detection_count']})")

    # 4. Сортируем ингредиенты по уверенности
    merged_ingredients.sort(key=lambda x: x['confidence'], reverse=True)

    # 5. Создаем финальный результат
    result = best_dish_data.copy()
    result['ingredients'] = merged_ingredients
    result['ensemble_info'] = {
        'models_count': len(valid_results),
        'ingredients_merged': len(merged_ingredients),
        'source_models': [name for _, name, _ in valid_results]
    }

    # Усредняем общую уверенность
    total_confidence = sum(data.get('confidence', 0) for data, _, _ in valid_results) / len(valid_results)
    result['confidence'] = total_confidence

    # Финальная фильтрация объединенных результатов
    result = _filter_non_food_items(result)
    if result.get('success') == False:
        logger.warning(f"⚠️ Ensemble detected non-food items: {result.get('error')}")
        # Возвращаем лучший результат без фильтрации как fallback
        result = best_dish_data.copy()
        result['ingredients'] = merged_ingredients
        result['confidence'] = total_confidence
        result['ensemble_info'] = {
            'models_count': len(valid_results),
            'ingredients_merged': len(merged_ingredients),
            'source_models': [name for _, name, _ in valid_results],
            'filter_warning': 'Non-food items detected in ensemble result'
        }

    logger.info(f"✅ Merged {len(merged_ingredients)} ingredients from {len(valid_results)} models")
    logger.info(f"🏆 Best dish: {result.get('dish_name', 'unknown')} (confidence: {total_confidence:.2f})")

    return result

async def identify_food_ensemble(
    image_bytes: bytes,
    model_indices: Optional[List[int]] = None,
    progress_callback=None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Умный ансамбль: LLaVA (шеф-повар) + UForm (помощник по ингредиентам).
    LLaVA отвечает за контекст блюда, UForm - за детальное перечисление ингредиентов.
    """
    if not BASE_URL:
        logger.error("❌ Cloudflare BASE_URL not configured")
        return None, None

    if model_indices is None:
        model_indices = [0, 1]  # LLaVA + UForm

    models_to_use = [VISION_MODELS[i] for i in model_indices if i < len(VISION_MODELS)]
    if not models_to_use:
        logger.error("❌ No valid models selected for ensemble")
        return None, None

    image_hash = _get_image_hash(image_bytes)
    cached = _get_cached_result(image_hash)
    if cached:
        return cached, "cache"

    image_array = list(image_bytes)
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    async def run_llava_model(model_info: dict) -> Tuple[Optional[Dict], Optional[str]]:
        """LLaVA - шеф-повар: определяет блюдо и основные ингредиенты"""
        model = model_info["id"]
        timeout = model_info["timeout"]
        try:
            url = f"{BASE_URL}{model}"
            payload = {
                "image": image_array,
                "prompt": LLAVA_ENSEMBLE_PROMPT,
                "max_tokens": 1200,  # Увеличили с 800 до 1200 для более подробных ответов
                "temperature": 0.1
            }

            logger.info(f"👨🍳 Starting LLaVA model: {model}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.warning(f"❌ LLaVA model {model} HTTP {resp.status}: {error_text[:100]}")
                        return None, model

                    result = await resp.json()
                    description = result.get("result", {}).get("description", "").strip()
                    if not description:
                        logger.warning(f"⚠️ LLaVA model {model} empty description")
                        return None, model

                    data = _extract_json_from_text(description)
                    if not data:
                        logger.warning(f"⚠️ LLaVA model {model} failed to extract JSON")
                        return None, model

                    is_valid, reason = _validate_food_data(data)
                    if not is_valid:
                        logger.warning(f"⚠️ LLaVA model {model} validation failed: {reason}")
                        return None, model

                    # Фильтрация бытовых предметов
                    data = _filter_non_food_items(data)
                    if data.get('success') == False:
                        logger.warning(f"⚠️ LLaVA model {model} detected non-food items")
                        return None, model

                    # Пост-обработка
                    portion_size = data.get('portion_size', 'medium')
                    if 'ingredients' in data:
                        data['ingredients'] = _calibrate_weights(data['ingredients'], portion_size)
                        data = _fix_protein_identification(data)

                    logger.info(f"✅ LLaVA model {model} succeeded, confidence: {data.get('confidence', 0)}")
                    return data, model
        except Exception as e:
            logger.warning(f"❌ LLaVA model {model} error: {type(e).__name__}: {e}")
            return None, model

    async def run_uform_model(model_info: dict) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """UForm - помощник по ингредиентам: подробно перечисляет все ингредиенты"""
        model = model_info["id"]
        timeout = model_info["timeout"]
        try:
            url = f"{BASE_URL}{model}"
            payload = {
                "image": image_array,
                "prompt": UFORM_DETAILED_PROMPT,  # Используем детальный промпт
                "max_tokens": 500  # Увеличили с 300 до 500 для более подробных списков
                # UForm не поддерживает temperature
            }

            logger.info(f"🥘 Starting UForm model: {model}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.warning(f"❌ UForm model {model} HTTP {resp.status}: {error_text[:100]}")
                        return None, model

                    result = await resp.json()
                    description = result.get("result", {}).get("description", "").strip()
                    if not description:
                        logger.warning(f"⚠️ UForm model {model} empty description")
                        return None, model

                    # Парсим текстовый ответ UForm
                    ingredients = _parse_uform_response(description)
                    if not ingredients:
                        logger.warning(f"⚠️ UForm model {model} failed to parse ingredients")
                        return None, model

                    # Фильтрация бытовых предметов для ингредиентов UForm
                    filtered_data = {'ingredients': ingredients}
                    filtered_data = _filter_non_food_items(filtered_data)
                    if filtered_data.get('success') == False:
                        logger.warning(f"⚠️ UForm model {model} detected non-food items")
                        return None, model

                    filtered_ingredients = filtered_data.get('ingredients', [])
                    logger.info(f"✅ UForm model {model} found {len(filtered_ingredients)} ingredients")
                    return filtered_ingredients, model
        except Exception as e:
            logger.warning(f"❌ UForm model {model} error: {type(e).__name__}: {e}")
            return None, model

    # Запускаем модели параллельно
    tasks = []
    for model_info in models_to_use:
        if "llava" in model_info["id"].lower():
            tasks.append(run_llava_model(model_info))
        elif "uform" in model_info["id"].lower():
            tasks.append(run_uform_model(model_info))
        else:
            # Для других моделей используем старый подход
            tasks.append(run_legacy_model(model_info))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Обрабатываем результаты
    llava_result = None
    uform_ingredients = []
    used_models = []

    for i, res in enumerate(results):
        if isinstance(res, Exception):
            logger.warning(f"🔥 Exception in ensemble task: {res}")
            continue

        model_name = models_to_use[i]["id"]
        used_models.append(model_name)

        if "llava" in model_name.lower():
            data, _ = res
            if data:
                llava_result = data
                logger.info(f"👨🍳 LLaVA provided structured dish data")
        elif "uform" in model_name.lower():
            ingredients, _ = res
            if ingredients:
                uform_ingredients = ingredients
                logger.info(f"🥘 UForm provided {len(ingredients)} detailed ingredients")

    if progress_callback:
        await progress_callback(stage=3, progress=80)

    # --- Умная агрегация результатов ---
    if llava_result and uform_ingredients:
        # Идеальный случай: есть данные от обеих моделей
        final_result = _merge_llava_with_uform(llava_result, uform_ingredients)
        ensemble_model = f"ensemble(LLaVA+UForm)"
        logger.info(f"🎯 Perfect ensemble: LLaVA context + UForm ingredients")
    elif llava_result:
        # Fallback: только LLaVA
        final_result = llava_result
        ensemble_model = f"ensemble(LLaVA-only)"
        logger.info(f"🔄 Fallback to LLaVA only")
    elif uform_ingredients:
        # Fallback: только UForm, пытаемся реконструировать блюдо
        final_result = _reconstruct_dish_from_ingredients(uform_ingredients)
        ensemble_model = f"ensemble(UForm-only)"
        logger.info(f"🔄 Fallback to UForm ingredients only")
    else:
        logger.error("❌ All ensemble models failed")
        return None, None

    # Финальная проверка и пост-обработка
    final_result = _fix_common_recognition_errors(final_result)

    # 🎯 ЭКСПЕРТНЫЙ АНАЛИЗ для вероятностного определения
    final_result = _expert_food_analysis(final_result)

    # ФИНАЛЬНАЯ ПРОВЕРКА: если результат подозрительный
    dish_name = final_result.get('dish_name', '').lower()
    ingredient_only_dishes = ['pork', 'beef', 'chicken', 'lamb', 'meat', 'fish']

    if dish_name in ingredient_only_dishes:
        logger.warning(f"⚠️ CRITICAL: Model returned ingredient '{dish_name}' instead of dish!")

        # Принудительно вызываем коррекцию
        final_result = _force_dish_identification(final_result)

    # Кэшируем результат
    _cache_result(image_hash, final_result)

    if progress_callback:
        await progress_callback(stage=4, progress=100)

    logger.info(f"🏆 Ensemble result: {ensemble_model}")
    logger.info(f"📊 Final confidence: {final_result.get('confidence', 0):.2f}")
    logger.info(f"🥘 Total ingredients: {len(final_result.get('ingredients', []))}")

    return final_result, ensemble_model

async def run_legacy_model(model_info: dict) -> Tuple[Optional[Dict], Optional[str]]:
    """Заглушка для старых моделей - не используется в новом ансамбле"""
    return None, model_info["id"]

def _expert_food_analysis(data: Dict) -> Dict:
    """Экспертный анализ блюд для вероятностного определения на основе визуальных признаков"""

    if not data:
        return data

    visual_cues = data.get('visual_cues', '').lower()
    ingredients = data.get('ingredients', [])
    ingredient_names = [ing.get('name', '').lower() for ing in ingredients]
    dish_name = data.get('dish_name', '').lower()

    # 🚨 КРИТИЧЕСКАЯ ПРОВЕРКА: если название общее - анализируем ингредиенты
    if dish_name in ['mixed dish', 'food dish', 'dish', 'unknown']:
        logger.info(f"🎯 Expert analysis TRIGGERED for generic dish: '{dish_name}'")
        logger.info(f"🎯 Available ingredients: {ingredient_names}")
        logger.info(f"🎯 Visual cues: '{visual_cues}'")

        # 🎯 АНАЛИЗ МЯСА
        meat_types = {
            'beef': ['говядина', 'телятина'],
            'pork': ['свинина', 'сало'],
            'chicken': ['курица', 'куриное'],
            'lamb': ['баранина', 'ягнятина'],
            'turkey': ['индейка'],
            'duck': ['утка', 'утиное']
        }

        # Определяем тип мяса
        detected_meat = None
        for meat_en, meat_ru_list in meat_types.items():
            if meat_en in ingredient_names or any(ru in ingredient_names for ru in meat_ru_list):
                detected_meat = meat_en
                logger.info(f"🥩 DETECTED MEAT TYPE: {meat_en}")
                break

        if detected_meat:
            # 🥩 АНАЛИЗ ФОРМЫ МЯСА - по ингредиентам и визуальным признакам
            meat_form_analysis = _analyze_meat_form(visual_cues, data)
            data.update(meat_form_analysis)

            # 🔥 АНАЛИЗ МЕТОДА ПРИГОТОВЛЕНИЯ
            cooking_analysis = _analyze_cooking_method(visual_cues, data)
            data.update(cooking_analysis)

            # 📊 ВЕРОЯТНОСТНОЕ ОПРЕДЕЛЕНИЕ БЛЮДА
            dish_probabilities = _calculate_meat_dish_probabilities(detected_meat, visual_cues, data)
            logger.info(f"🎯 CALCULATED PROBABILITIES: {len(dish_probabilities)} options")
            for i, prob in enumerate(dish_probabilities):
                logger.info(f"🎯   Option {i+1}: {prob['name']} (confidence: {prob['confidence']}) - {prob.get('reasoning', '')}")

            if dish_probabilities:
                best_dish = dish_probabilities[0]
                data['dish_name'] = best_dish['name']
                data['dish_name_ru'] = best_dish['name_ru']
                data['confidence'] = best_dish['confidence']
                data['category'] = best_dish.get('category', 'main')
                data['reasoning'] = best_dish.get('reasoning', '')

                logger.info(f"🎯 Expert analysis FIXED: {best_dish['name']} → {best_dish['name_ru']} (confidence: {best_dish['confidence']})")
                logger.info(f"🎯 Reasoning: {best_dish.get('reasoning', '')}")
                logger.info(f"🎯 Category: {best_dish.get('category', 'main')}")
                return data
        else:
            logger.info(f"🎯 No meat detected in ingredients: {ingredient_names}")
    else:
        logger.info(f"🎯 Expert analysis SKIPPED - dish name is specific: '{dish_name}'")

    # 🐟 АНАЛИЗ РЫБЫ
    fish_types = {
        'salmon': ['лосось', 'семга'],
        'tuna': ['тунец'],
        'cod': ['треска', 'пикша'],
        'mackerel': ['скумбрия', 'макрель'],
        'herring': ['сельдь', 'селедка'],
        'trout': ['форель']
    }

    detected_fish = None
    for fish_en, fish_ru_list in fish_types.items():
        if fish_en in ingredient_names or any(ru in ingredient_names for ru in fish_ru_list):
            detected_fish = fish_en
            break

    if detected_fish:
        fish_analysis = _analyze_fish_form(detected_fish, visual_cues, data)
        data.update(fish_analysis)

        fish_probabilities = _calculate_fish_dish_probabilities(detected_fish, visual_cues, data)
        if fish_probabilities:
            best_dish = fish_probabilities[0]
            data['dish_name'] = best_dish['name']
            data['dish_name_ru'] = best_dish['name_ru']
            data['confidence'] = best_dish['confidence']
            data['category'] = best_dish.get('category', 'fish')
            data['fish_type'] = detected_fish

            logger.info(f"🐟 Fish analysis FIXED: {best_dish['name']} → {best_dish['name_ru']} (confidence: {best_dish['confidence']})")
            logger.info(f"🐟 Fish type: {detected_fish}")
            return data

    # 🍲 АНАЛИЗ СУПОВ
    if 'soup' in data.get('category', '').lower() or data.get('is_soup', False):
        soup_analysis = _analyze_soup_type(visual_cues, ingredient_names, data)
        data.update(soup_analysis)

        soup_probabilities = _calculate_soup_probabilities(visual_cues, ingredient_names, data)
        if soup_probabilities:
            best_dish = soup_probabilities[0]
            data['dish_name'] = best_dish['name']
            data['dish_name_ru'] = best_dish['name_ru']
            data['confidence'] = best_dish['confidence']
            data['soup_type'] = best_dish.get('soup_type', 'unknown')

            logger.info(f"🍲 Soup analysis FIXED: {best_dish['name']} → {best_dish['name_ru']} (confidence: {best_dish['confidence']})")
            return data

    return data

def _analyze_meat_form(visual_cues: str, data: Dict) -> Dict:
    """Анализ формы мяса"""
    analysis = {}
    ingredients = data.get('ingredients', [])
    ingredient_names = [ing.get('name', '').lower() for ing in ingredients]
    dish_name = data.get('dish_name', '').lower()

    # 🚨 ПРОВЕРКА НА ШАШЛЫК по множеству признаков
    shashlik_indicators = 0

    # Визуальные признаки
    if any(ind in visual_cues for ind in ['stick', 'skewer', 'wooden', 'metal']):
        shashlik_indicators += 3  # Самый сильный признак
        logger.info("🍢 Found skewer indicators in visual cues")

    # Признаки из ингредиентов (лук часто с шашлыком)
    if any(onion in ingredient_names for onion in ['onion', 'лук']):
        shashlik_indicators += 1
        logger.info("🧅 Found onion - typical for shashlik")

    # Если блюд называется "mixed dish" + есть мясо = вероятно шашлык
    if dish_name in ['mixed dish', 'food dish'] and any(meat in ingredient_names for meat in ['pork', 'beef', 'chicken', 'lamb']):
        shashlik_indicators += 2
        logger.info("🎯 Mixed dish with meat - likely shashlik")

    # Множество типов мяса = вероятно шашлык (ассорти)
    meat_count = sum(1 for name in ingredient_names if name in ['pork', 'beef', 'chicken', 'lamb', 'salmon'])
    if meat_count >= 2:
        shashlik_indicators += 1
        logger.info(f"🥩 Multiple meat types ({meat_count}) - likely shashlik assortment")

    # Определяем форму мяса
    if shashlik_indicators >= 3:
        analysis['meat_form'] = 'on_skewers'
        analysis['has_skewers'] = True
        analysis['shashlik_confidence'] = min(shashlik_indicators * 0.2, 0.9)
        logger.info(f"🍢 SHASHLIK DETECTED: confidence {analysis['shashlik_confidence']}")
    elif any(ind in visual_cues for ind in ['thick', 'piece', 'cut', 'slab']):
        analysis['meat_form'] = 'steak'
        analysis['has_skewers'] = False
    elif any(ind in visual_cues for ind in ['chunks', 'cubes', 'pieces', 'diced']):
        analysis['meat_form'] = 'chunks'
        analysis['has_skewers'] = False
    elif any(ind in visual_cues for ind in ['ground', 'minced', 'patties']):
        analysis['meat_form'] = 'ground'
        analysis['has_skewers'] = False
    elif any(ind in visual_cues for ind in ['whole', 'intact', 'roasted']):
        analysis['meat_form'] = 'whole'
        analysis['has_skewers'] = False
    else:
        # Если нет визуальных признаков, используем эвристику
        if dish_name in ['mixed dish', 'food dish'] and meat_count >= 1:
            analysis['meat_form'] = 'on_skewers'  # Наиболее вероятно для шашлыка
            analysis['has_skewers'] = True
            analysis['shashlik_confidence'] = 0.7
            logger.info("🎯 Defaulting to shashlik for mixed dish with meat")
        else:
            analysis['meat_form'] = 'unknown'
            analysis['has_skewers'] = False

    return analysis

def _analyze_cooking_method(visual_cues: str, data: Dict) -> Dict:
    """Анализ метода приготовления"""
    analysis = {}

    if any(ind in visual_cues for ind in ['grill', 'charred', 'marks', 'seared']):
        analysis['cooking_method'] = 'grilled'
    elif any(ind in visual_cues for ind in ['fried', 'crispy', 'golden', 'brown crust']):
        analysis['cooking_method'] = 'fried'
    elif any(ind in visual_cues for ind in ['stewed', 'sauce', 'soft', 'tender']):
        analysis['cooking_method'] = 'stewed'
    elif any(ind in visual_cues for ind in ['baked', 'roasted', 'oven']):
        analysis['cooking_method'] = 'baked'
    elif any(ind in visual_cues for ind in ['boiled', 'moist', 'steamed']):
        analysis['cooking_method'] = 'boiled'
    else:
        analysis['cooking_method'] = 'unknown'

    return analysis

def _calculate_meat_dish_probabilities(meat_type: str, visual_cues: str, data: Dict) -> List[Dict]:
    """Расчет вероятностей для мясных блюд"""
    probabilities = []
    meat_form = data.get('meat_form', 'unknown')
    cooking_method = data.get('cooking_method', 'unknown')
    shashlik_confidence = data.get('shashlik_confidence', 0)

    # 🍢 Шашлык - УЛУЧШЕННАЯ ЛОГИКА
    if meat_form == 'on_skewers':
        # Базовая уверенность для шашлыка на шампурах
        base_confidence = 0.9
        if shashlik_confidence > 0:
            base_confidence = max(base_confidence, shashlik_confidence)

        probabilities.append({
            'name': f"{meat_type} shashlik",
            'name_ru': f"{_translate_meat_type(meat_type)} шашлык",
            'confidence': base_confidence,
            'category': 'skewers',
            'reasoning': f'Meat on skewers detected (confidence: {shashlik_confidence:.2f})'
        })
        logger.info(f"🍢 SHASHLIK PROBABILITY: {base_confidence} (indicators: {shashlik_confidence:.2f})")

    # 🥩 Стейк
    elif meat_form == 'steak' and cooking_method in ['grilled', 'fried']:
        probabilities.append({
            'name': f"{meat_type} steak",
            'name_ru': f"{_translate_meat_type(meat_type)} стейк",
            'confidence': 0.85,
            'category': 'main',
            'reasoning': 'Thick piece of meat with grill/fry marks'
        })

    # 🍲 Рагу/тушеное мясо
    elif meat_form == 'chunks' and cooking_method in ['stewed', 'unknown']:
        if any(ind in visual_cues for ind in ['sauce', 'liquid', 'thick']):
            probabilities.append({
                'name': f"{meat_type} stew",
                'name_ru': f"{_translate_meat_type(meat_type)} рагу",
                'confidence': 0.8,
                'category': 'main',
                'reasoning': 'Meat chunks in sauce'
            })
        else:
            probabilities.append({
                'name': f"{meat_type} goulash",
                'name_ru': f"{_translate_meat_type(meat_type)} гуляш",
                'confidence': 0.75,
                'category': 'main',
                'reasoning': 'Meat chunks, likely goulash'
            })

    # 🍖 Отбивная/котлета
    elif meat_form == 'ground' and cooking_method == 'fried':
        probabilities.append({
            'name': f"{meat_type} cutlet",
            'name_ru': f"{_translate_meat_type(meat_type)} котлета",
            'confidence': 0.8,
            'category': 'main',
            'reasoning': 'Ground meat, fried'
        })

    # 🍗 Цыпленок/утка запеченная
    elif meat_form == 'whole' and cooking_method in ['baked', 'roasted']:
        probabilities.append({
            'name': f"roast {meat_type}",
            'name_ru': f"запеченная {_translate_meat_type(meat_type)}",
            'confidence': 0.85,
            'category': 'main',
            'reasoning': 'Whole roasted meat'
        })

    # 🚨 FALLBACK: Если ничего не подошло, но есть мясо
    elif meat_form == 'unknown' and meat_type:
        # Проверяем индикаторы шашлыка даже при unknown форме
        if shashlik_confidence >= 0.5:
            probabilities.append({
                'name': f"{meat_type} shashlik",
                'name_ru': f"{_translate_meat_type(meat_type)} шашлык",
                'confidence': shashlik_confidence,
                'category': 'skewers',
                'reasoning': f'Mixed dish with meat indicators - likely shashlik (confidence: {shashlik_confidence:.2f})'
            })
            logger.info(f"🚨 FALLBACK SHASHLIK: {shashlik_confidence} from indicators")
        else:
            # Общее grilled meat
            probabilities.append({
                'name': f"grilled {meat_type}",
                'name_ru': f"гриль {_translate_meat_type(meat_type)}",
                'confidence': 0.6,
                'category': 'main',
                'reasoning': 'Mixed meat dish, grilled preparation assumed'
            })

    return sorted(probabilities, key=lambda x: x['confidence'], reverse=True)

def _analyze_fish_form(fish_type: str, visual_cues: str, data: Dict) -> Dict:
    """Анализ формы рыбы"""
    analysis = {'fish_form': 'unknown'}

    if any(ind in visual_cues for ind in ['steak', 'cross-section', 'thick']):
        analysis['fish_form'] = 'steak'
    elif any(ind in visual_cues for ind in ['fillet', 'flat', 'skin']):
        analysis['fish_form'] = 'fillet'
    elif any(ind in visual_cues for ind in ['smoked', 'pink', 'orange', 'shiny']):
        analysis['fish_form'] = 'smoked'
    elif any(ind in visual_cues for ind in ['whole', 'head', 'tail', 'scales']):
        analysis['fish_form'] = 'whole'

    return analysis

def _calculate_fish_dish_probabilities(fish_type: str, visual_cues: str, data: Dict) -> List[Dict]:
    """Расчет вероятностей для рыбных блюд"""
    probabilities = []
    fish_form = data.get('fish_form', 'unknown')
    cooking_method = data.get('cooking_method', 'unknown')

    if fish_form == 'steak' and cooking_method in ['grilled', 'fried']:
        probabilities.append({
            'name': f"{fish_type} steak",
            'name_ru': f"{_translate_fish_type(fish_type)} стейк",
            'confidence': 0.9,
            'category': 'fish',
            'reasoning': 'Fish steak with grill marks'
        })
    elif fish_form == 'fillet':
        probabilities.append({
            'name': f"grilled {fish_type}",
            'name_ru': f"гриль {_translate_fish_type(fish_type)}",
            'confidence': 0.85,
            'category': 'fish',
            'reasoning': 'Fish fillet, grilled'
        })
    elif fish_form == 'smoked':
        probabilities.append({
            'name': f"smoked {fish_type}",
            'name_ru': f"копченая {_translate_fish_type(fish_type)}",
            'confidence': 0.95,
            'category': 'fish',
            'reasoning': 'Smoked fish with characteristic color'
        })
    elif fish_form == 'whole':
        probabilities.append({
            'name': f"whole {fish_type}",
            'name_ru': f"цельная {_translate_fish_type(fish_type)}",
            'confidence': 0.8,
            'category': 'fish',
            'reasoning': 'Whole fish preparation'
        })

    return sorted(probabilities, key=lambda x: x['confidence'], reverse=True)

def _analyze_soup_type(visual_cues: str, ingredient_names: List[str], data: Dict) -> Dict:
    """Анализ типа супа"""
    analysis = {}

    # Определяем консистенцию
    if any(ind in visual_cues for ind in ['clear', 'transparent']):
        analysis['consistency'] = 'clear'
    elif any(ind in visual_cues for ind in ['creamy', 'smooth', 'uniform']):
        analysis['consistency'] = 'creamy'
    elif any(ind in visual_cues for ind in ['thick', 'chunky', 'pieces']):
        analysis['consistency'] = 'chunky'
    else:
        analysis['consistency'] = 'unknown'

    # Определяем цвет
    if any(ind in visual_cues for ind in ['red', 'pink', 'beet']):
        analysis['color'] = 'red'
    elif any(ind in visual_cues for ind in ['green', 'cabbage']):
        analysis['color'] = 'green'
    elif any(ind in visual_cues for ind in ['orange', 'pumpkin', 'carrot']):
        analysis['color'] = 'orange'
    elif any(ind in visual_cues for ind in ['white', 'cream']):
        analysis['color'] = 'white'
    else:
        analysis['color'] = 'brown'

    return analysis

def _calculate_soup_probabilities(visual_cues: str, ingredient_names: List[str], data: Dict) -> List[Dict]:
    """Расчет вероятностей для супов"""
    probabilities = []
    consistency = data.get('consistency', 'unknown')
    color = data.get('color', 'unknown')

    # 🍲 Борщ
    if color == 'red' and any(x in ingredient_names for x in ['beet', 'beetroot', 'свекла']):
        if any(x in ingredient_names for x in ['cabbage', 'капуста', 'sour cream', 'сметана']):
            probabilities.append({
                'name': 'borscht',
                'name_ru': 'борщ',
                'confidence': 0.95,
                'category': 'soup',
                'soup_type': 'borscht',
                'reasoning': 'Red soup with beets and cabbage/sour cream'
            })

    # 🥬 Щи
    elif color == 'green' and any(x in ingredient_names for x in ['cabbage', 'капуста']):
        probabilities.append({
            'name': 'shchi',
            'name_ru': 'щи',
            'confidence': 0.9,
            'category': 'soup',
            'soup_type': 'shchi',
            'reasoning': 'Green cabbage soup'
        })

    # 🥣 Крем-суп
    elif consistency == 'creamy':
        if any(x in ingredient_names for x in ['mushroom', 'гриб']):
            probabilities.append({
                'name': 'cream of mushroom soup',
                'name_ru': 'грибной крем-суп',
                'confidence': 0.8,
                'category': 'soup',
                'soup_type': 'cream',
                'reasoning': 'Creamy soup with mushrooms'
            })
        elif color == 'orange':
            probabilities.append({
                'name': 'pumpkin soup',
                'name_ru': 'тыквенный суп',
                'confidence': 0.75,
                'category': 'soup',
                'soup_type': 'cream',
                'reasoning': 'Orange creamy soup'
            })

    # 🍲 Густой суп
    elif consistency == 'chunky':
        if any(x in ingredient_names for x in ['chicken', 'курица']):
            probabilities.append({
                'name': 'chicken soup',
                'name_ru': 'куриный суп',
                'confidence': 0.8,
                'category': 'soup',
                'soup_type': 'chunky',
                'reasoning': 'Chunky chicken soup'
            })
        else:
            probabilities.append({
                'name': 'vegetable soup',
                'name_ru': 'овощной суп',
                'confidence': 0.75,
                'category': 'soup',
                'soup_type': 'chunky',
                'reasoning': 'Chunky vegetable soup'
            })

    return sorted(probabilities, key=lambda x: x['confidence'], reverse=True)

def _translate_meat_type(meat_type: str) -> str:
    """Перевод типа мяса на русский"""
    translations = {
        'beef': 'говяжий',
        'pork': 'свиной',
        'chicken': 'куриный',
        'lamb': 'бараний',
        'turkey': 'индюшиный',
        'duck': 'утиный'
    }
    return translations.get(meat_type, meat_type)

def _translate_fish_type(fish_type: str) -> str:
    """Перевод типа рыбы на русский"""
    translations = {
        'salmon': 'лосось',
        'tuna': 'тунец',
        'cod': 'треска',
        'mackerel': 'скумбрия',
        'herring': 'сельдь',
        'trout': 'форель'
    }
    return translations.get(fish_type, fish_type)

def _force_dish_identification(data: Dict) -> Dict:
    """Принудительная идентификация блюда когда модель вернула ингредиент"""

    ingredients = data.get('ingredients', [])
    ingredient_names = [ing.get('name', '').lower() for ing in ingredients]
    cooking_method = data.get('cooking_method', 'unknown')
    visual_cues = data.get('visual_cues', '').lower()

    # 🎯 УМНАЯ ЛОГИКА: различаем шашлык, стейк и нарезанное мясо
    # Шашлык = кубики/кусочки + характерные признаки (даже без шампуров)
    # Стейк = большой цельный кусок
    # Нарезанное = кусочки, но не шашлык

    # Признаки шампуров
    skewer_indicators = ['stick', 'skewer', 'wooden', 'metal', 'threaded', 'cubes']
    has_skewer_hint = any(ind in visual_cues for ind in skewer_indicators)

    # Признаки стейка
    steak_indicators = ['thick', 'cut', 'piece', 'slab', 'fillet', 'chop']
    has_steak_hint = any(ind in visual_cues for ind in steak_indicators)

    # Список мясных ингредиентов на английском и русском
    meat_types = {
        'beef': 'говяжий',
        'pork': 'свиной',
        'chicken': 'куриный',
        'lamb': 'бараний',
        'turkey': 'индюшиный',
        'fish': 'рыбный',
        'salmon': 'лососевый'
    }

    for meat_en, meat_ru in meat_types.items():
        if meat_en in ingredient_names:
            if cooking_method in ['grilled', 'unknown', '']:
                # Признаки именно ШАШЛЫКА (даже без шампуров)
                shashlik_indicators = ['cubes', 'cubed', 'chunks', 'pieces', 'diced']
                has_shashlik_pieces = any(ind in visual_cues for ind in shashlik_indicators)
                has_onion = any(onion in visual_cues for onion in ['onion', 'лук'])
                has_sauce = any(sauce in visual_cues for sauce in ['sauce', 'маринад', 'marinade'])

                # Признаки большого куска (стейк)
                has_large_piece = any(ind in visual_cues for ind in ['thick', 'large', 'whole', 'single'])

                # 🥩 ЛОГИКА ОПРЕДЕЛЕНИЯ:
                if has_skewer_hint:
                    # Есть шампуры = точно шашлык
                    dish_type = 'shashlik'
                    logger.info(f"🍢 Шашлык определен по шампурам")
                elif has_shashlik_pieces and (has_onion or has_sauce) and not has_large_piece:
                    # Кусочки + лук/соус = вероятно шашлык (без шампуров)
                    dish_type = 'shashlik'
                    logger.info(f"🍢 Шашлык определен по кусочкам + лук/соус")
                elif has_shashlik_pieces and not has_large_piece:
                    # Маленькие кусочки = возможно шашлык (но меньше уверенности)
                    dish_type = 'shashlik'
                    logger.info(f"🍢 Шашлык определен по кусочкам (меньшая уверенность)")
                elif has_steak_hint or has_large_piece:
                    # Большой кусок = это стейк
                    dish_type = 'steak'
                    logger.info(f"🥩 Стейк определен по большому куску")
                else:
                    # Неясно - оставляем как есть
                    logger.info(f"❓ Неясно, оставляем оригинальное определение: {data.get('dish_name', '')}")
                    return data

                if dish_type == 'shashlik':
                    # ✅ Это ШАШЛЫК
                    data['dish_name'] = f"{meat_en} shashlik"
                    data['dish_name_ru'] = f"{meat_ru} шашлык"
                    data['category'] = 'skewers'
                    data['cooking_method'] = 'grilled'
                    data['has_skewers'] = has_skewer_hint  # Может быть False если без шампуров
                    data['confidence'] = 0.85

                    logger.info(f"🚨 FORCE-IDENTIFIED: {data['dish_name']} (шашлык по визуальным признакам)")
                    return data
                elif dish_type == 'steak':
                    # ✅ Это СТЕЙК
                    data['dish_name'] = f"{meat_en} steak"
                    data['dish_name_ru'] = f"{meat_ru} стейк"
                    data['category'] = 'main'
                    data['cooking_method'] = 'grilled'
                    data['has_skewers'] = False
                    data['confidence'] = 0.85

                    logger.info(f"🚨 FORCE-IDENTIFIED: {data['dish_name']} (стейк по визуальным признакам)")
                    return data

    # Проверяем на борщ
    if any(x in ingredient_names for x in ['beet', 'beetroot', 'свекла']):
        if any(x in ingredient_names for x in ['cabbage', 'капуста', 'sour cream', 'сметана']):
            data['dish_name'] = 'borscht'
            data['dish_name_ru'] = 'борщ'
            data['category'] = 'soup'
            data['cooking_method'] = 'boiled'
            data['is_soup'] = True
            data['confidence'] = 0.9

            logger.info(f"🚨 FORCE-IDENTIFIED: {data['dish_name']}")
            return data

    return data

def _merge_llava_with_uform(llava_data: Dict, uform_ingredients: List[Dict]) -> Dict:
    """Объединяет результаты с ЖЕСТКОЙ ФИЛЬТРАЦИЕЙ UForm"""

    logger.info("🔗 Merging LLaVA context with UForm ingredients...")

    # 🔥 ЖЕСТКОЕ ОГРАНИЧЕНИЕ: максимум 5 ингредиентов от UForm
    MAX_UFORM_INGREDIENTS = 5  # Было 10, уменьшили до 5

    # Фильтруем только важные ингредиенты от UForm
    important_types = ['protein', 'vegetable', 'carb']
    filtered_uform = [ing for ing in uform_ingredients 
                     if ing.get('type') in important_types and 
                     ing.get('confidence', 0) > 0.6]

    # Берем топ-5 по уверенности
    filtered_uform.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    uform_ingredients = filtered_uform[:MAX_UFORM_INGREDIENTS]

    logger.info(f"🔗 Filtered UForm: {len(uform_ingredients)} important ingredients")

    # Начинаем с данных LLaVA (структура блюда)
    merged = llava_data.copy()

    # Собираем все ингредиенты
    all_ingredients = []

    # Добавляем основные ингредиенты от LLaVA (приоритет!)
    llava_ingredients = llava_data.get('ingredients', [])
    for ing in llava_ingredients:
        ing_copy = ing.copy()
        ing_copy['source'] = 'llava'
        all_ingredients.append(ing_copy)

    existing_names = {ing.get('name', '').lower().strip() for ing in all_ingredients if ing.get('name')}

    # Добавляем ингредиенты от UForm только если их нет от LLaVA
    for uform_ing in uform_ingredients:
        uform_name = (uform_ing.get('name', '') or '').lower().strip()
        if not uform_name or len(uform_name) < 2:
            continue

        if uform_name not in existing_names:
            uform_copy = uform_ing.copy()
            uform_copy['source'] = 'uform'
            all_ingredients.append(uform_copy)
            existing_names.add(uform_name)
            continue

        for existing in all_ingredients:
            if (existing.get('name', '') or '').lower().strip() == uform_name:
                avg_confidence = (existing.get('confidence', 0.7) + uform_ing.get('confidence', 0.7)) / 2
                existing['confidence'] = avg_confidence
                existing['source'] = 'both'
                break

    # Сортируем: сначала LLaVA (высокий приоритет), затем по уверенности
    all_ingredients.sort(key=lambda x: (x.get('source') != 'llava', -(x.get('confidence', 0))))

    # Ограничиваем общее количество ингредиентов
    MAX_TOTAL_INGREDIENTS = 12
    if len(all_ingredients) > MAX_TOTAL_INGREDIENTS:
        all_ingredients = all_ingredients[:MAX_TOTAL_INGREDIENTS]
        logger.info(f"🔗 Limited total ingredients to {MAX_TOTAL_INGREDIENTS}")

    # Обновляем результат
    merged['ingredients'] = all_ingredients
    merged['ensemble_info'] = {
        'llava_confidence': llava_data.get('confidence', 0),
        'uform_ingredients_count': len(uform_ingredients),
        'total_ingredients_count': len(all_ingredients),
        'merge_strategy': 'llava_context_plus_uform_ingredients'
    }

    logger.info(f"✅ Merged: {len(llava_ingredients)} LLaVA + {len(uform_ingredients)} UForm = {len(all_ingredients)} total")
    return merged

def _reconstruct_dish_from_ingredients(ingredients: List[Dict]) -> Dict:
    """
    Реконструирует блюдо из списка ингредиентов (когда нет данных от LLaVA).
    """
    logger.info("🔧 Reconstructing dish from ingredients only...")

    # Анализируем ингредиенты для определения типа блюда
    protein_ingredients = [ing for ing in ingredients if ing.get('type') == 'protein']
    carb_ingredients = [ing for ing in ingredients if ing.get('type') == 'carb']

    dish_name = "mixed dish"
    cooking_method = "unknown"
    category = "main"

    # Простая эвристика для определения блюда
    if protein_ingredients:
        main_protein = protein_ingredients[0].get('name', 'meat')
        if carb_ingredients:
            dish_name = f"{main_protein} with {carb_ingredients[0].get('name', 'grains')}"
            category = "main"
        else:
            dish_name = f"grilled {main_protein}"
            cooking_method = "grilled"
            category = "main"

    confidence = 0.6  # ниже уверенность для реконструированного блюда

    return {
        'dish_name': dish_name,
        'dish_name_ru': dish_name,
        'category': category,
        'cooking_method': cooking_method,
        'confidence': confidence,
        'ingredients': ingredients,
        'ensemble_info': {
            'reconstruction': True,
            'ingredients_only': True,
            'reconstruction_strategy': 'ingredients_to_dish'
        }
    }

async def identify_food_cascade(
    image_bytes: bytes,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Каскадное распознавание с улучшенной обработкой ошибок.
    Использует ансамбль моделей для повышения точности.
    """
    try:
        # Используем новый ансамбль моделей
        data, used_model = await identify_food_ensemble(
            image_bytes,
            model_indices=[0, 1],  # LLaVA + UForm
            progress_callback=progress_callback
        )

        if data and used_model:
            return {
                "success": True,
                "data": data,
                "model": used_model,
                "consensus": True,
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
    data, _ = await identify_food_ensemble(
        image_bytes,
        model_indices=[1],  # Используем только UForm для скорости
        progress_callback=None
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
    data, _ = await identify_food_ensemble(
        image_bytes,
        model_indices=[0],  # Используем только LLaVA для скорости
        progress_callback=None
    )
    return data.get("dish_name") if data else None

async def analyze_food_image(image_bytes: bytes, prompt: str = None) -> Optional[str]:
    """Возвращает строку ингредиентов."""
    if prompt is None:
        prompt = UFORM_DETAILED_PROMPT

    ingredients = await get_simple_ingredients(image_bytes)
    if ingredients:
        return ", ".join(ingredients)
    return None
