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
ENHANCED_FOOD_RECOGNITION_PROMPT = """You are an expert food recognition AI specializing in Russian and international cuisine. Your task is to identify dishes and ingredients with MAXIMUM precision.

CRITICAL RULES:
1. NEVER confuse fish with meat - they are DIFFERENT categories
2. NEVER confuse soups with main dishes - soups are LIQUID dishes
3. Identify SPECIFIC types, not generic categories
4. Recognize COMPLETE dishes, not just components
5. SKEWERER/KEBAB IDENTIFICATION IS CRITICAL - NEVER identify meat skewers as fish!
6. Meat on skewers has distinct texture and structure - recognize this pattern!

FOOD CATEGORIES (MUTUALLY EXCLUSIVE):

 FISH & SEAFOOD (НЕ МЯСО):
- Salmon/лосось/семга, trout/форель, tuna/тунец, cod/треска
- Mackerel/скумбрия, herring/сельдь, pike/щука, carp/карп
- Shrimp/креветки, crab/краб, squid/кальмары, mussels/мидии
- NEVER call fish "meat" - it's "fish" or "seafood"

 MEAT (МЯСО):
- Beef/говядина, pork/свинина, chicken/курица, lamb/ягнятина, turkey/индейка
- Sausages/колбасы, hot dogs/сосиски
- Steak/стейк, cutlets/отбивные
- Ground meat/фарш, minced meat/фарш
- CRITICAL: Meat on skewers (шашлик/кебаб) is ALWAYS meat, NEVER fish!
- Look for: cylindrical shape, grill marks, wooden/metal sticks, meat pieces threaded on sticks

 SOUPS (СУПЫ - ЖИДКИЕ БЛЮДА):
- Borscht/борщ (beet soup with meat and vegetables)
- Shchi/щи (cabbage soup)
- Solyanka/солянка (mixed meat and pickle soup)
- Ukha/уха (fish soup)
- Chicken soup/куриный суп
- Mushroom soup/грибной суп
- Pea soup/гороховый суп
- ALWAYS identify as "soup", NEVER as "meat with bread"

 PASTA & GRAINS (ГАРНИРЫ):
- Pasta/макароны/спагетти (specify type if visible)
- Rice/рис (white, brown, basmati)
- Buckwheat/гречка
- Potatoes/картофель (boiled, fried, mashed)

 SALADS & VEGETABLES (САЛАТЫ И ОВОЩИ):
- Green salad/зеленый салат
- Caesar salad/салат цезарь
- Greek salad/греческий салат
- Olivier salad/оливье
- Mixed vegetables/овощное ассорти
- ALWAYS identify salads separately from main dishes

 BREAD & BAKERY (ХЛЕБ И ВЫПЕЧКА):
- Bread/хлеб (white, black, rye)
- Bun/булка
- ONLY if clearly visible as separate item

SPECIFIC DISH IDENTIFICATION:

For BORSHCH (борщ):
- MUST identify as: "borscht" or "beet soup"
- Ingredients: beets, cabbage, potatoes, carrots, meat (optional), sour cream
- NEVER identify as "meat with bread"

For FISH dishes:
- MUST specify: "salmon", "trout", "tuna", etc.
- NEVER call it "meat"
- Example: "grilled salmon" NOT "grilled meat"

For COMPLEX dishes:
- Identify EACH component separately
- Example: "salmon with pasta and salad" has 3 components:
  1. Fish: salmon
  2. Carb: pasta
  3. Vegetable: salad

RECOGNITION PRIORITY:
1. First identify if it's a SOUP (liquid in bowl)
2. Then identify MAIN PROTEIN (fish vs meat vs chicken)
3. Then identify SIDES (pasta, rice, potatoes, vegetables)
4. Then identify SALADS separately
5. Then identify BREAD if visible

OUTPUT FORMAT:
For EACH visible dish/component, provide:
{
  "dish_name": "SPECIFIC name (e.g., 'grilled salmon', 'borscht', 'chicken with rice')",
  "category": "fish|meat|chicken|soup|pasta|salad|vegetables|bread",
  "ingredients": [
    {
      "name": "specific ingredient (e.g., 'salmon', 'beets', 'pasta')",
      "type": "protein|carb|vegetable|fat|sauce",
      "estimated_weight_grams": number,
      "confidence": 0.0-1.0
    }
  ],
  "cooking_method": "grilled|fried|boiled|baked|steamed|raw",
  "portion_size": "small|medium|large",
  "confidence": 0.0-1.0
}

EXAMPLES OF CORRECT RECOGNITION:

Image: Red soup with meat and sour cream
 CORRECT: {"dish_name": "borscht", "category": "soup", ...}
 WRONG: {"dish_name": "meat with bread", ...}

Image: Pink fish fillet with pasta and green salad
 CORRECT: [
  {"dish_name": "grilled salmon", "category": "fish", ...},
  {"dish_name": "pasta", "category": "pasta", ...},
  {"dish_name": "green salad", "category": "salad", ...}
]
 WRONG: {"dish_name": "meat with pasta", ...}

Image: Clear soup with fish and vegetables
 CORRECT: {"dish_name": "ukha", "category": "soup", ...}
 WRONG: {"dish_name": "fish with vegetables", ...}

Image: Chicken breast with buckwheat
 CORRECT: [
  {"dish_name": "grilled chicken breast", "category": "chicken", ...},
  {"dish_name": "buckwheat", "category": "grains", ...}
]

Image: Meat pieces on wooden/metal skewers (шашлик)
 CORRECT: {"dish_name": "meat skewers", "category": "meat", "cooking_method": "grilled", ...}
 WRONG: {"dish_name": "salmon with bread", ...}  # CRITICAL ERROR!

CRITICAL DISTINCTIONS:
- FISH ≠ MEAT (рыба ≠ мясо)
- SOUP ≠ MAIN DISH (суп ≠ второе блюдо)
- SALAD ≠ SIDE DISH (салат ≠ гарнир)
- Be SPECIFIC: "salmon" NOT "fish", "borscht" NOT "soup"
- SKEWERS = MEAT, NEVER FISH! (шампуры = мясо, никогда рыба!)

Now analyze image with MAXIMUM precision and return ONLY valid JSON."""

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


def _identify_known_dish(ingredients: List[Dict], prep_style: str = 'mixed') -> Optional[str]:
    """
    Универсальное определение известных блюд по ингредиентам с улучшенной логикой
    """
    # Нормализуем названия ингредиентов
    ingredient_names = []
    for ing in ingredients:
        name = ing.get('name', '').lower()
        # Убираем модификаторы приготовления
        name = name.replace('grilled ', '').replace('fried ', '').replace('boiled ', '')
        name = name.replace('baked ', '').replace('roasted ', '').replace('steamed ', '')
        name = name.replace('raw ', '').replace('fresh ', '')
        ingredient_names.append(name)
    
    # Расширенная база известных блюд с их сигнатурами
    known_dishes = {
        # Русские блюда
        'борщ': {
            'ingredients': ['beef', 'beetroot', 'cabbage', 'potato', 'carrot', 'onion'],
            'required': ['beetroot'],
            'prep_style': 'soup',
            'min_match': 3,
            'priority': 100  # Высокий приоритет
        },
        'щи': {
            'ingredients': ['cabbage', 'carrot', 'onion', 'potato'],
            'required': ['cabbage'],
            'prep_style': 'soup',
            'min_match': 2,
            'priority': 90
        },
        'солянка': {
            'ingredients': ['meat', 'cucumber', 'olive', 'tomato'],
            'required': ['cucumber', 'olive'],
            'prep_style': 'soup',
            'min_match': 2,
            'priority': 85
        },
        'уха': {
            'ingredients': ['fish', 'potato', 'carrot', 'onion'],
            'required': ['fish'],
            'prep_style': 'soup',
            'min_match': 2,
            'priority': 85
        },
        'пельмени': {
            'ingredients': ['dough', 'meat', 'onion'],
            'required': ['dough', 'meat'],
            'prep_style': 'mixed',
            'min_match': 2,
            'priority': 80
        },
        'голубцы': {
            'ingredients': ['cabbage', 'meat', 'rice', 'carrot'],
            'required': ['cabbage', 'meat'],
            'prep_style': 'mixed',
            'min_match': 2,
            'priority': 80
        },
        'котлеты': {
            'ingredients': ['meat', 'bread', 'onion', 'egg'],
            'required': ['meat'],
            'prep_style': 'fried',
            'min_match': 2,
            'priority': 75
        },
        'гречка с мясом': {
            'ingredients': ['buckwheat', 'meat', 'onion'],
            'required': ['buckwheat', 'meat'],
            'prep_style': 'mixed',
            'min_match': 2,
            'priority': 70
        },
        
        # Салаты
        'салат цезарь': {
            'ingredients': ['lettuce', 'chicken', 'parmesan', 'croutons', 'caesar dressing'],
            'required': ['lettuce', 'caesar dressing'],
            'prep_style': 'salad',
            'min_match': 3,
            'priority': 85
        },
        'греческий салат': {
            'ingredients': ['lettuce', 'tomato', 'cucumber', 'feta', 'olive'],
            'required': ['feta', 'olive'],
            'prep_style': 'salad',
            'min_match': 3,
            'priority': 85
        },
        'салат оливье': {
            'ingredients': ['potato', 'carrot', 'peas', 'egg', 'mayonnaise'],
            'required': ['potato', 'mayonnaise'],
            'prep_style': 'salad',
            'min_match': 3,
            'priority': 85
        },
        'винегрет': {
            'ingredients': ['beetroot', 'potato', 'carrot', 'peas', 'pickles'],
            'required': ['beetroot'],
            'prep_style': 'salad',
            'min_match': 3,
            'priority': 80
        },
        
        # Итальянские блюда
        'спагетти болоньезе': {
            'ingredients': ['spaghetti', 'beef', 'tomato', 'onion'],
            'required': ['spaghetti', 'beef', 'tomato'],
            'prep_style': 'mixed',
            'min_match': 3,
            'priority': 90
        },
        'спагетти карбонара': {
            'ingredients': ['spaghetti', 'egg', 'bacon', 'parmesan'],
            'required': ['spaghetti', 'egg', 'bacon'],
            'prep_style': 'mixed',
            'min_match': 3,
            'priority': 90
        },
        'лазанья': {
            'ingredients': ['pasta', 'beef', 'tomato', 'cheese'],
            'required': ['pasta', 'beef', 'cheese'],
            'prep_style': 'baked',
            'min_match': 3,
            'priority': 85
        },
        'пицца маргарита': {
            'ingredients': ['dough', 'tomato', 'cheese', 'basil'],
            'required': ['dough', 'tomato', 'cheese'],
            'prep_style': 'baked',
            'min_match': 3,
            'priority': 85
        },
        
        # Азиатские блюда
        'жареный рис': {
            'ingredients': ['rice', 'egg', 'vegetables', 'soy sauce'],
            'required': ['rice', 'egg'],
            'prep_style': 'fried',
            'min_match': 2,
            'priority': 80
        },
        'рамен': {
            'ingredients': ['noodles', 'broth', 'egg', 'pork'],
            'required': ['noodles', 'broth'],
            'prep_style': 'soup',
            'min_match': 2,
            'priority': 85
        },
        'суші': {
            'ingredients': ['rice', 'fish', 'seaweed', 'cucumber'],
            'required': ['rice', 'fish', 'seaweed'],
            'prep_style': 'mixed',
            'min_match': 3,
            'priority': 85
        },
        
        # Американские блюда
        'гамбургер': {
            'ingredients': ['beef patty', 'bun', 'lettuce', 'tomato', 'cheese'],
            'required': ['beef patty', 'bun'],
            'prep_style': 'mixed',
            'min_match': 2,
            'priority': 80
        },
        'стейк': {
            'ingredients': ['beef'],
            'required': ['beef'],
            'prep_style': 'grilled',
            'min_match': 1,
            'priority': 75
        },
        'картофель фрі': {
            'ingredients': ['potato'],
            'required': ['potato'],
            'prep_style': 'fried',
            'min_match': 1,
            'priority': 70
        },
        
        # Закуски и гарниры
        'картофельне пюре': {
            'ingredients': ['potato', 'milk', 'butter'],
            'required': ['potato'],
            'prep_style': 'boiled',
            'min_match': 1,
            'priority': 60
        },
        'гречка': {
            'ingredients': ['buckwheat'],
            'required': ['buckwheat'],
            'prep_style': 'boiled',
            'min_match': 1,
            'priority': 60
        },
        'рис': {
            'ingredients': ['rice'],
            'required': ['rice'],
            'prep_style': 'boiled',
            'min_match': 1,
            'priority': 60
        },
        'макарони': {
            'ingredients': ['pasta', 'spaghetti'],
            'required': ['pasta'],
            'prep_style': 'boiled',
            'min_match': 1,
            'priority': 60
        },
        
        # Супы (дополнительные)
        'куриний суп': {
            'ingredients': ['chicken', 'vegetables', 'noodles'],
            'required': ['chicken'],
            'prep_style': 'soup',
            'min_match': 2,
            'priority': 80
        },
        'грибний суп': {
            'ingredients': ['mushrooms', 'potato', 'onion'],
            'required': ['mushrooms'],
            'prep_style': 'soup',
            'min_match': 2,
            'priority': 80
        },
        'гороховий суп': {
            'ingredients': ['peas', 'potato', 'carrot'],
            'required': ['peas'],
            'prep_style': 'soup',
            'min_match': 2,
            'priority': 75
        },
        
        # Мясні страви
        'курка гриль': {
            'ingredients': ['chicken'],
            'required': ['chicken'],
            'prep_style': 'grilled',
            'min_match': 1,
            'priority': 75
        },
        'жарена риба': {
            'ingredients': ['fish'],
            'required': ['fish'],
            'prep_style': 'fried',
            'min_match': 1,
            'priority': 75
        },
        'запечена риба': {
            'ingredients': ['fish'],
            'required': ['fish'],
            'prep_style': 'baked',
            'min_match': 1,
            'priority': 75
        },
        
        # Овочеві страви
        'овочевий салат': {
            'ingredients': ['vegetables', 'lettuce', 'tomato', 'cucumber'],
            'required': ['vegetables'],
            'prep_style': 'salad',
            'min_match': 2,
            'priority': 70
        },
        'тушені овочі': {
            'ingredients': ['vegetables', 'carrot', 'onion', 'potato'],
            'required': ['vegetables'],
            'prep_style': 'stewed',
            'min_match': 2,
            'priority': 70
        }
    }
    
    # Улучшенный алгоритм сопоставления с приоритетами
    best_match = None
    best_score = 0
    best_priority = 0
    
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
        
        # Вычисляем score с учетом приоритета
        score = (matches / len(dish_info['ingredients'])) * 100
        priority_bonus = dish_info.get('priority', 50)
        final_score = score + (priority_bonus / 10)
        
        # Логирование для отладки
        if final_score > best_score:
            logger.info(f"🔍 {dish_name}: matches={matches}/{len(dish_info['ingredients'])}, score={final_score:.1f}")
        
        if final_score > best_score and final_score >= 50:  # Минимальный порог 50%
            best_score = final_score
            best_priority = dish_info.get('priority', 50)
            best_match = dish_name
    
    if best_match:
        logger.info(f"🎯 Identified known dish: {best_match} (score: {best_score:.1f}, priority: {best_priority})")
        return best_match
    
    return None


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
async def identify_food_cascade(
    image_bytes: bytes,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Улучшенное каскадное распознавание с пост-обработкой
    """
    try:
        # Используем новый промпт
        data, used_model = await identify_food_multimodel(
            image_bytes,
            prompt=ENHANCED_FOOD_RECOGNITION_PROMPT,  # Новый промпт
            progress_callback=progress_callback
        )
        
        if data and used_model:
            # Пост-обработка: исправляем типичные ошибки
            data = _fix_common_recognition_errors(data)
            
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


def _fix_common_recognition_errors(data: Dict) -> Dict:
    """
    Универсальная система исправления ошибок распознавания для ВСЕХ типов блюд
    """
    if not data or 'dish_name' not in data:
        return data
    
    dish_name = data['dish_name'].lower()
    ingredients = data.get('ingredients', [])
    ingredient_names = [ing.get('name', '').lower() for ing in ingredients]
    
    logger.info(f"🔧 Starting universal error correction for: {dish_name}")
    logger.info(f"🔧 Ingredients detected: {ingredient_names}")
    
    # ========== РУССКИЕ СУПЫ ==========
    
    # Борщ - главный приоритет
    if ('beets' in ingredient_names or 'beetroot' in ingredient_names or 'свекла' in ingredient_names) and \
       ('cabbage' in ingredient_names or 'капуста' in ingredient_names):
        data['dish_name'] = 'борщ'
        data['category'] = 'soup'
        data['preparation_style'] = 'soup'
        logger.info("🔧 Fixed: Identified as borscht (beets + cabbage signature)")
    
    # Щи
    elif 'cabbage' in ingredient_names and not ('beets' in ingredient_names or 'beetroot' in ingredient_names):
        if any(ing in ingredient_names for ing in ['carrot', 'onion', 'potato']):
            data['dish_name'] = 'щи'
            data['category'] = 'soup'
            data['preparation_style'] = 'soup'
            logger.info("🔧 Fixed: Identified as shchi (cabbage soup signature)")
    
    # Уха
    elif 'fish' in ingredient_names and any(ing in ingredient_names for ing in ['potato', 'carrot', 'onion']):
        data['dish_name'] = 'уха'
        data['category'] = 'soup'
        data['preparation_style'] = 'soup'
        logger.info("🔧 Fixed: Identified as ukha (fish soup signature)")
    
    # Солянка
    elif ('cucumber' in ingredient_names or 'olive' in ingredient_names) and 'meat' in ingredient_names:
        data['dish_name'] = 'солянка'
        data['category'] = 'soup'
        data['preparation_style'] = 'soup'
        logger.info("🔧 Fixed: Identified as solyanka (cucumber + olive + meat signature)")
    
    # Куриний суп
    elif 'chicken' in ingredient_names and any(ing in ingredient_names for ing in ['noodles', 'vegetables']):
        data['dish_name'] = 'куриний суп'
        data['category'] = 'soup'
        data['preparation_style'] = 'soup'
        logger.info("🔧 Fixed: Identified as chicken soup")
    
    # Грибний суп
    elif 'mushrooms' in ingredient_names and any(ing in ingredient_names for ing in ['potato', 'carrot', 'onion']):
        data['dish_name'] = 'грибний суп'
        data['category'] = 'soup'
        data['preparation_style'] = 'soup'
        logger.info("🔧 Fixed: Identified as mushroom soup")
    
    # Гороховий суп
    elif 'peas' in ingredient_names and any(ing in ingredient_names for ing in ['potato', 'carrot']):
        data['dish_name'] = 'гороховий суп'
        data['category'] = 'soup'
        data['preparation_style'] = 'soup'
        logger.info("🔧 Fixed: Identified as pea soup")
    
    # ========== РУССКИЕ ОСНОВНЫЕ БЛЮДА ==========
    
    # Пельмени
    elif 'dough' in ingredient_names and 'meat' in ingredient_names:
        data['dish_name'] = 'пельмени'
        data['category'] = 'main'
        data['preparation_style'] = 'mixed'
        logger.info("🔧 Fixed: Identified as pelmeni (dough + meat signature)")
    
    # Голубцы
    elif 'cabbage' in ingredient_names and 'meat' in ingredient_names and not ('beets' in ingredient_names):
        data['dish_name'] = 'голубцы'
        data['category'] = 'main'
        data['preparation_style'] = 'mixed'
        logger.info("🔧 Fixed: Identified as golubtsy (cabbage + meat signature)")
    
    # Котлеты
    elif 'meat' in ingredient_names and any(ing in ingredient_names for ing in ['bread', 'onion', 'egg']):
        data['dish_name'] = 'котлеты'
        data['category'] = 'main'
        data['preparation_style'] = 'fried'
        logger.info("🔧 Fixed: Identified as kotlety (meat cutlets signature)")
    
    # Гречка с мясом
    elif 'buckwheat' in ingredient_names and 'meat' in ingredient_names:
        data['dish_name'] = 'гречка с мясом'
        data['category'] = 'main'
        data['preparation_style'] = 'mixed'
        logger.info("🔧 Fixed: Identified as buckwheat with meat")
    
    # ========== САЛАТЫ ==========
    
    # Салат Цезарь
    elif 'lettuce' in ingredient_names and 'caesar dressing' in ingredient_names:
        data['dish_name'] = 'салат цезарь'
        data['category'] = 'salad'
        data['preparation_style'] = 'salad'
        logger.info("🔧 Fixed: Identified as Caesar salad")
    
    # Греческий салат
    elif 'feta' in ingredient_names and 'olive' in ingredient_names:
        data['dish_name'] = 'греческий салат'
        data['category'] = 'salad'
        data['preparation_style'] = 'salad'
        logger.info("🔧 Fixed: Identified as Greek salad")
    
    # Салат Оливье
    elif 'potato' in ingredient_names and 'mayonnaise' in ingredient_names and any(ing in ingredient_names for ing in ['carrot', 'peas', 'egg']):
        data['dish_name'] = 'салат оливье'
        data['category'] = 'salad'
        data['preparation_style'] = 'salad'
        logger.info("🔧 Fixed: Identified as Olivier salad")
    
    # Винегрет
    elif 'beetroot' in ingredient_names and 'potato' in ingredient_names and 'carrot' in ingredient_names:
        data['dish_name'] = 'винегрет'
        data['category'] = 'salad'
        data['preparation_style'] = 'salad'
        logger.info("🔧 Fixed: Identified as vinaigrette")
    
    # Овощевий салат
    elif any(ing in ingredient_names for ing in ['lettuce', 'tomato', 'cucumber']) and len(ingredient_names) >= 3:
        data['dish_name'] = 'овочевий салат'
        data['category'] = 'salad'
        data['preparation_style'] = 'salad'
        logger.info("🔧 Fixed: Identified as vegetable salad")
    
    # ========== ИТАЛЬЯНСКИЕ БЛЮДА ==========
    
    # Спагетти Болоньезе
    elif 'spaghetti' in ingredient_names and 'beef' in ingredient_names and 'tomato' in ingredient_names:
        data['dish_name'] = 'спагетти болоньезе'
        data['category'] = 'pasta'
        data['preparation_style'] = 'mixed'
        logger.info("🔧 Fixed: Identified as spaghetti bolognese")
    
    # Спагетти Карбонара
    elif 'spaghetti' in ingredient_names and 'egg' in ingredient_names and 'bacon' in ingredient_names:
        data['dish_name'] = 'спагетти карбонара'
        data['category'] = 'pasta'
        data['preparation_style'] = 'mixed'
        logger.info("🔧 Fixed: Identified as spaghetti carbonara")
    
    # Лазанья
    elif 'pasta' in ingredient_names and 'beef' in ingredient_names and 'cheese' in ingredient_names:
        data['dish_name'] = 'лазанья'
        data['category'] = 'pasta'
        data['preparation_style'] = 'baked'
        logger.info("🔧 Fixed: Identified as lasagna")
    
    # Пицца Маргарита
    elif 'dough' in ingredient_names and 'tomato' in ingredient_names and 'cheese' in ingredient_names:
        data['dish_name'] = 'пицца маргарита'
        data['category'] = 'pizza'
        data['preparation_style'] = 'baked'
        logger.info("🔧 Fixed: Identified as pizza margherita")
    
    # ========== АЗИАТСКИЕ БЛЮДА ==========
    
    # Жареный рис
    elif 'rice' in ingredient_names and 'egg' in ingredient_names:
        data['dish_name'] = 'жареный рис'
        data['category'] = 'rice'
        data['preparation_style'] = 'fried'
        logger.info("🔧 Fixed: Identified as fried rice")
    
    # Рамен
    elif 'noodles' in ingredient_names and 'broth' in ingredient_names:
        data['dish_name'] = 'рамен'
        data['category'] = 'soup'
        data['preparation_style'] = 'soup'
        logger.info("🔧 Fixed: Identified as ramen")
    
    # Суші
    elif 'rice' in ingredient_names and 'fish' in ingredient_names and 'seaweed' in ingredient_names:
        data['dish_name'] = 'суші'
        data['category'] = 'sushi'
        data['preparation_style'] = 'mixed'
        logger.info("🔧 Fixed: Identified as sushi")
    
    # ========== АМЕРИКАНСКИЕ БЛЮДА ==========
    
    # Гамбургер
    elif 'beef patty' in ingredient_names and 'bun' in ingredient_names:
        data['dish_name'] = 'гамбургер'
        data['category'] = 'burger'
        data['preparation_style'] = 'mixed'
        logger.info("🔧 Fixed: Identified as hamburger")
    
    # Стейк
    elif 'beef' in ingredient_names and len(ingredient_names) <= 2:
        data['dish_name'] = 'стейк'
        data['category'] = 'meat'
        data['preparation_style'] = 'grilled'
        logger.info("🔧 Fixed: Identified as steak")
    
    # ========== ГАРНИРЫ И ПРОСТЫЕ БЛЮДА ==========
    
    # Картофель фрі
    elif 'potato' in ingredient_names and len(ingredient_names) == 1:
        data['dish_name'] = 'картофель фрі'
        data['category'] = 'potato'
        data['preparation_style'] = 'fried'
        logger.info("🔧 Fixed: Identified as french fries")
    
    # Картофельне пюре
    elif 'potato' in ingredient_names and any(ing in ingredient_names for ing in ['milk', 'butter']):
        data['dish_name'] = 'картофельне пюре'
        data['category'] = 'potato'
        data['preparation_style'] = 'boiled'
        logger.info("🔧 Fixed: Identified as mashed potatoes")
    
    # Гречка
    elif 'buckwheat' in ingredient_names and len(ingredient_names) <= 2:
        data['dish_name'] = 'гречка'
        data['category'] = 'grain'
        data['preparation_style'] = 'boiled'
        logger.info("🔧 Fixed: Identified as buckwheat")
    
    # Рис
    elif 'rice' in ingredient_names and len(ingredient_names) <= 2:
        data['dish_name'] = 'рис'
        data['category'] = 'grain'
        data['preparation_style'] = 'boiled'
        logger.info("🔧 Fixed: Identified as rice")
    
    # Макарони
    elif 'pasta' in ingredient_names or 'spaghetti' in ingredient_names:
        data['dish_name'] = 'макарони'
        data['category'] = 'pasta'
        data['preparation_style'] = 'boiled'
        logger.info("🔧 Fixed: Identified as pasta")
    
    # ========== МЯСНЫЕ БЛЮДА ==========
    
    # Курка гриль
    elif 'chicken' in ingredient_names and len(ingredient_names) <= 2:
        data['dish_name'] = 'курка гриль'
        data['category'] = 'chicken'
        data['preparation_style'] = 'grilled'
        logger.info("🔧 Fixed: Identified as grilled chicken")
    
    # Жарена риба
    elif 'fish' in ingredient_names and len(ingredient_names) <= 2:
        data['dish_name'] = 'жарена риба'
        data['category'] = 'fish'
        data['preparation_style'] = 'fried'
        logger.info("🔧 Fixed: Identified as fried fish")
    
    # Запечена риба
    elif 'fish' in ingredient_names and 'baked' in dish_name:
        data['dish_name'] = 'запечена риба'
        data['category'] = 'fish'
        data['preparation_style'] = 'baked'
        logger.info("🔧 Fixed: Identified as baked fish")
    
    # ========== КРИТИЧЕСКОЕ: ШАМПУРЫ/ШАШЛИК ==========
    
    # Шашлик/кебаб - КРИТИЧЕСКИ ВАЖНОЕ ПРАВИЛО!
    skewer_keywords = ['skewer', 'kebab', 'shashlik', 'шашлик', 'шампур', 'шпажка', 'stick']
    meat_keywords = ['beef', 'pork', 'chicken', 'lamb', 'meat', 'говядина', 'свинина', 'курица', 'баранина', 'мясо']
    
    if (any(skewer in dish_name for skewer in skewer_keywords) or 
        any(skewer in ' '.join(ingredient_names) for skewer in skewer_keywords)) and \
       any(meat in ingredient_names for meat in meat_keywords):
        data['dish_name'] = 'шашлик'
        data['category'] = 'meat'
        data['preparation_style'] = 'grilled'
        logger.info("🔧 CRITICAL FIX: Identified as meat skewers (шашлик) - NOT fish!")
    
    # ЗАЩИТА от ошибки "лосось с хлебом" вместо шашлика
    if ('salmon' in dish_name or 'лосось' in dish_name) and \
       ('bread' in dish_name or 'хлеб' in dish_name):
        # Проверяем, возможно это шашлик
        if any(skewer in ' '.join(ingredient_names) for skewer in skewer_keywords) or \
           'grilled' in dish_name or 'grill' in dish_name:
            data['dish_name'] = 'шашлик'
            data['category'] = 'meat'
            data['preparation_style'] = 'grilled'
            logger.info("🔧 CRITICAL FIX: Corrected 'salmon with bread' to meat skewers!")
    
    # ========== ОВощеві БЛЮДА ==========
    
    # Тушені овочі
    elif 'vegetables' in ingredient_names and len(ingredient_names) >= 3:
        data['dish_name'] = 'тушені овочі'
        data['category'] = 'vegetables'
        data['preparation_style'] = 'stewed'
        logger.info("🔧 Fixed: Identified as stewed vegetables")
    
    # ========== ЗАЩИТА ОТ ОШИБОК ==========
    
    # Исправление: рыба ≠ мясо
    fish_keywords = ['salmon', 'trout', 'tuna', 'cod', 'fish', 'лосось', 'форель', 'рыба']
    if any(fish in dish_name for fish in fish_keywords):
        if 'meat' in dish_name:
            data['dish_name'] = dish_name.replace('meat', 'fish')
            logger.info("🔧 Fixed: Changed 'meat' to 'fish'")
    
    # КРИТИЧЕСКАЯ ЗАЩИТА: шашлик НЕ МОЖЕТ БЫТЬ рыбой!
    if ('salmon' in dish_name or 'лосось' in dish_name) and \
       ('bread' in dish_name or 'хлеб' in dish_name):
        # Это почти наверняка шашлик, а не лосось с хлебом
        skewer_indicators = ['grilled', 'stick', 'skewer', 'kebab', 'шампур', 'шашлик']
        if any(indicator in dish_name for indicator in skewer_indicators) or \
           any(indicator in ' '.join(ingredient_names) for indicator in skewer_indicators):
            data['dish_name'] = 'шашлик'
            data['category'] = 'meat'
            data['preparation_style'] = 'grilled'
            logger.info("🔧 CRITICAL SAFEGUARD: Fixed 'salmon with bread' to 'шашлик' (meat skewers)")
    
    # Исправление: жидкое блюдо = суп
    if data.get('preparation_style') == 'liquid' or data.get('soup'):
        if 'soup' not in dish_name and 'суп' not in dish_name and 'борщ' not in dish_name:
            if any(ing in ingredient_names for ing in ['broth', 'бульон', 'суп']):
                data['category'] = 'soup'
                logger.info("🔧 Fixed: Identified as soup by liquid style")
    
    logger.info(f"🔧 Final result: {data['dish_name']} (category: {data.get('category', 'unknown')})")
    return data


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
        prompt = ENHANCED_FOOD_RECOGNITION_PROMPT
    
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

