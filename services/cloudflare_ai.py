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
    {"id": "@cf/llava-hf/llava-1.5-7b-hf", "priority": 1, "timeout": 90, "weight": 0.6},
    {"id": "@cf/unum/uform-gen2-qwen-500m", "priority": 2, "timeout": 60, "weight": 0.4},
    {"id": "@cf/llava-hf/bakllava-1", "priority": 3, "timeout": 90, "weight": 0.3},
]

# Кэш результатов (hash изображения → результат)
_RECOGNITION_CACHE: Dict[str, Tuple[Dict, datetime]] = {}
_CACHE_TTL = 3600  # 1 час

# ========== УЛУЧШЕННЫЕ ПРОМПТЫ ==========
FOOD_RECOGNITION_PROMPT = """You are an advanced computer vision system specialized in food ingredient identification and nutritional analysis. Analyze this food image systematically and return ONLY valid JSON.

PRIMARY OBJECTIVE:
Identify ALL visible food items with their cooking methods and estimated weights. Focus on ingredient-level recognition rather than attempting to name complex dishes.

ANALYSIS METHODOLOGY:
1. Scan the entire image systematically
2. Identify each distinct food component
3. Determine cooking method for each component
4. Estimate realistic weights based on visual portion size
5. Assess confidence for each identification

FOOD CATEGORIES TO IDENTIFY:

PROTEINS:
- Meats: beef, pork, lamb, chicken, turkey - identify specific cuts
- Seafood: fish (salmon, tuna, cod, etc.), shrimp, crab, squid
- Plant-based: tofu, tempeh, legumes, eggs

CARBOHYDRATES:
- Grains: rice (white, brown), pasta (spaghetti, penne, etc.), bread
- Root vegetables: potatoes, sweet potatoes, carrots, beets
- Legumes: beans, lentils, chickpeas

VEGETABLES:
- Leafy greens: lettuce, spinach, kale, cabbage
- Cruciferous: broccoli, cauliflower, Brussels sprouts
- Nightshade: tomatoes, peppers, eggplant
- Allium: onions, garlic, leeks
- Others: cucumbers, zucchini, mushrooms, corn

FRUITS:
- Fresh: apples, bananas, berries, citrus
- Dried: raisins, dates, apricots

FATS & OILS:
- Visible oils: olive oil, butter, vegetable oil
- Nuts & seeds: almonds, walnuts, sesame seeds
- Avocado, cheese, cream

SAUCES & DRESSINGS:
- Tomato-based: marinara, ketchup, tomato sauce
- Cream-based: cream sauce, mayonnaise, ranch
- Oil-based: vinaigrette, pesto
- Other: soy sauce, teriyaki, BBQ sauce

COOKING METHODS IDENTIFICATION:
- Grilled: visible grill marks, charred areas
- Fried: golden-brown exterior, oil sheen
- Baked/Roasted: dry heat appearance, even browning
- Boiled/Steamed: moist appearance, no browning
- Raw: natural colors, unprocessed appearance
- Stir-fried: high heat searing, Asian style

VISUAL ANALYSIS CRITERIA:
- Color: Natural vs processed colors
- Texture: Smooth, rough, crispy, soft
- Shape: Cut forms (slices, cubes, strips)
- Arrangement: How items are combined on plate
- Cooking indicators: Grill marks, browning, moisture

REQUIRED JSON FORMAT:
{
  "ingredients": [
    {
      "name": "specific ingredient name",
      "category": "protein|carb|vegetable|fruit|fat|sauce|other",
      "cooking_method": "grilled|fried|baked|boiled|steamed|raw|stir-fried|roasted",
      "estimated_weight_grams": number,
      "confidence": 0.0-1.0,
      "visual_notes": "brief description of appearance"
    }
  ],
  "preparation_style": "mixed|separated|layered|casserole|soup|salad",
  "meal_type": "breakfast|lunch|dinner|snack",
  "overall_confidence": 0.0-1.0
}

ACCURACY REQUIREMENTS:
- Each ingredient must be individually identifiable
- Cooking methods must match visual evidence
- Weight estimates must be realistic for portion size
- Confidence scores must reflect identification certainty
- Use standard culinary terminology

EXAMPLES OF CORRECT ANALYSIS:
{
  "ingredients": [
    {
      "name": "grilled chicken breast",
      "category": "protein",
      "cooking_method": "grilled",
      "estimated_weight_grams": 150,
      "confidence": 0.9,
      "visual_notes": "white meat with grill marks, sliced"
    },
    {
      "name": "spaghetti pasta",
      "category": "carb",
      "cooking_method": "boiled",
      "estimated_weight_grams": 120,
      "confidence": 0.95,
      "visual_notes": "long strands, white color, moist appearance"
    },
    {
      "name": "lettuce mix",
      "category": "vegetable",
      "cooking_method": "raw",
      "estimated_weight_grams": 50,
      "confidence": 0.85,
      "visual_notes": "mixed green leaves, fresh appearance"
    }
  ],
  "preparation_style": "mixed",
  "meal_type": "lunch",
  "overall_confidence": 0.9
}

CRITICAL RULES:
1. Identify EACH visible ingredient separately
2. Be specific about cooking methods based on visual evidence
3. Provide realistic weight estimates
4. Use confidence scores honestly
5. Focus on ingredients, not complex dish names
6. If uncertain, lower confidence and describe visually
7. Include all components - even small garnishes
8. Distinguish between similar items (e.g., different vegetable types)

Now analyze the image systematically and return JSON with all identifiable ingredients:"""

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
    
    # Умное определение известных блюд
    dish_name = _identify_known_dish(converted_ingredients, data.get('preparation_style', 'mixed'))
    
    if dish_name:
        old_format_data['dish_name'] = dish_name
        logger.info(f"🎯 Identified known dish: {dish_name}")
    else:
        # Генерируем название на основе ингредиентов
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


def _identify_known_dish(ingredients: List[Dict], prep_style: str) -> Optional[str]:
    """
    Умное определение известных блюд по ингредиентам и методу приготовления.
    """
    if not ingredients:
        return None
    
    # Нормализуем названия ингредиентов для анализа
    ingredient_names = []
    for ing in ingredients:
        name = ing.get('name', '').lower()
        # Убираем модификаторы приготовления
        name = name.replace('grilled ', '').replace('fried ', '').replace('boiled ', '')
        name = name.replace('baked ', '').replace('roasted ', '').replace('steamed ', '')
        ingredient_names.append(name)
    
    # Словарь известных блюд с их сигнатурами
    known_dishes = {
        # Русские блюда
        'борщ': {
            'ingredients': ['beef', 'beetroot', 'cabbage', 'potato', 'carrot', 'onion'],
            'required': ['beetroot'],
            'prep_style': 'soup',
            'min_match': 3
        },
        'щи': {
            'ingredients': ['cabbage', 'carrot', 'onion', 'potato'],
            'required': ['cabbage'],
            'prep_style': 'soup',
            'min_match': 2
        },
        'солянка': {
            'ingredients': ['meat', 'cucumber', 'olive', 'tomato'],
            'required': ['cucumber', 'olive'],
            'prep_style': 'soup',
            'min_match': 2
        },
        'уха': {
            'ingredients': ['fish', 'potato', 'carrot', 'onion'],
            'required': ['fish'],
            'prep_style': 'soup',
            'min_match': 2
        },
        'пельмени': {
            'ingredients': ['dough', 'meat', 'onion'],
            'required': ['dough', 'meat'],
            'prep_style': 'mixed',
            'min_match': 2
        },
        'голубцы': {
            'ingredients': ['cabbage', 'meat', 'rice', 'carrot'],
            'required': ['cabbage', 'meat'],
            'prep_style': 'mixed',
            'min_match': 2
        },
        
        # Салаты
        'салат цезарь': {
            'ingredients': ['lettuce', 'chicken', 'parmesan', 'croutons', 'caesar dressing'],
            'required': ['lettuce', 'caesar dressing'],
            'prep_style': 'salad',
            'min_match': 3
        },
        'греческий салат': {
            'ingredients': ['lettuce', 'tomato', 'cucumber', 'feta', 'olive'],
            'required': ['feta', 'olive'],
            'prep_style': 'salad',
            'min_match': 3
        },
        'салат оливье': {
            'ingredients': ['potato', 'carrot', 'peas', 'egg', 'mayonnaise'],
            'required': ['potato', 'mayonnaise'],
            'prep_style': 'salad',
            'min_match': 3
        },
        
        # Итальянские блюда
        'спагетти болоньезе': {
            'ingredients': ['spaghetti', 'beef', 'tomato', 'onion'],
            'required': ['spaghetti', 'beef', 'tomato'],
            'prep_style': 'mixed',
            'min_match': 3
        },
        'спагетти карбонара': {
            'ingredients': ['spaghetti', 'egg', 'bacon', 'parmesan'],
            'required': ['spaghetti', 'egg', 'bacon'],
            'prep_style': 'mixed',
            'min_match': 3
        },
        'лазанья': {
            'ingredients': ['pasta', 'beef', 'tomato', 'cheese'],
            'required': ['pasta', 'beef', 'cheese'],
            'prep_style': 'baked',
            'min_match': 3
        },
        
        # Азиатские блюда
        'жареный рис': {
            'ingredients': ['rice', 'egg', 'vegetables', 'soy sauce'],
            'required': ['rice', 'egg'],
            'prep_style': 'fried',
            'min_match': 2
        },
        'рамен': {
            'ingredients': ['noodles', 'broth', 'egg', 'pork'],
            'required': ['noodles', 'broth'],
            'prep_style': 'soup',
            'min_match': 2
        },
        
        # Американские блюда
        'гамбургер': {
            'ingredients': ['beef patty', 'bun', 'lettuce', 'tomato', 'cheese'],
            'required': ['beef patty', 'bun'],
            'prep_style': 'mixed',
            'min_match': 2
        },
        'стейк': {
            'ingredients': ['beef'],
            'required': ['beef'],
            'prep_style': 'mixed',
            'min_match': 1
        }
    }
    
    # Ищем совпадения с известными блюдами
    best_match = None
    best_score = 0
    
    for dish_name, dish_info in known_dishes.items():
        # Проверяем соответствие стиля приготовления
        if dish_info['prep_style'] != prep_style and dish_info['prep_style'] != 'mixed':
            continue
        
        # Считаем совпадения ингредиентов
        matches = 0
        required_matches = 0
        
        for ingredient in ingredient_names:
            if ingredient in dish_info['ingredients']:
                matches += 1
                if ingredient in dish_info['required']:
                    required_matches += 1
        
        # Проверяем минимальные требования
        if matches < dish_info['min_match']:
            continue
        
        if required_matches < len(dish_info['required']):
            continue
        
        # Вычисляем score (процент совпадения)
        score = matches / len(dish_info['ingredients'])
        
        if score > best_score and score >= 0.5:  # Минимальный порог 50%
            best_score = score
            best_match = dish_name
    
    return best_match


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
                                data = _fix_protein_identification(data)
                            
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

