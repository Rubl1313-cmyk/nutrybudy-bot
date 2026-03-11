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

# ========== ПРОМПТЫ РАСПОЗНАВАНИЯ ЕДЫ ==========

FOOD_RECOGNITION_PROMPT = """You are an expert food recognition AI. Analyze this food image and return ONLY valid JSON.

CRITICAL RULES:
1. Identify the COMPLETE DISH, not just ingredients
2. NEVER return just "meat", "beef", "chicken" - these are ingredients, not dishes!
3. If you see meat on wooden/metal sticks → it's "shashlik" or "meat skewers" or "kebabs"
4. Be specific about cooking method and dish type

VISUAL CUES FOR SHASHLIK/KEBABS:
- Cylindrical meat pieces threaded on sticks
- Wooden or metal skewers visible
- Grill marks on meat
- Charred edges
- Meat pieces stacked linearly
- Often served with onions, vegetables on the side

REQUIRED JSON FORMAT:
{
  "dish_name": "Specific dish name (e.g., 'beef shashlik', 'chicken skewers', 'borscht')",
  "ingredients": [
    {"name": "ingredient", "type": "protein|vegetable|carb|fat|other", "estimated_weight_grams": 100, "confidence": 0.9}
  ],
  "confidence": 0.85,
  "meal_type": "breakfast|lunch|dinner|snack",
  "cooking_method": "grilled|fried|boiled|steamed|baked|raw",
  "portion_size": "small|medium|large"
}

EXAMPLES OF CORRECT RECOGNITION:

Image: Meat pieces on wooden sticks with grill marks
CORRECT: {"dish_name": "beef shashlik", "ingredients": [{"name": "beef", "type": "protein", "estimated_weight_grams": 200}], "cooking_method": "grilled"}
WRONG: {"dish_name": "beef"} This is an ingredient, not a dish!

Image: Red soup with beets and sour cream
CORRECT: {"dish_name": "borscht", "ingredients": [{"name": "beets", "type": "vegetable"}, {"name": "cabbage", "type": "vegetable"}], "cooking_method": "boiled"}
WRONG: {"dish_name": "meat with bread"} Completely wrong!

Image: Pink fish fillet with pasta
CORRECT: {"dish_name": "grilled salmon with pasta", "ingredients": [{"name": "salmon", "type": "protein"}, {"name": "pasta", "type": "carb"}]}
WRONG: {"dish_name": "meat with pasta"} Fish is not meat!

Image: Chicken pieces on metal skewers
CORRECT: {"dish_name": "chicken shashlik", "ingredients": [{"name": "chicken", "type": "protein"}], "cooking_method": "grilled"}
WRONG: {"dish_name": "chicken"} This is an ingredient!

Image: Pork on wooden sticks with onions
CORRECT: {"dish_name": "pork kebabs", "ingredients": [{"name": "pork", "type": "protein"}, {"name": "onion", "type": "vegetable"}], "cooking_method": "grilled"}
WRONG: {"dish_name": "pork with bread"} Wrong identification!

JSON FORMATTING RULES:
1. Use ONLY double quotes "not single quotes"
2. NO backslashes before underscores (use "dish_name" NOT "dish_name")
3. NO markdown code blocks (no ```json)
4. NO trailing commas
5. All numbers unquoted
6. Return ONLY the JSON object, nothing else

Now analyze the image and return ONLY valid JSON:"""

ENHANCED_FOOD_RECOGNITION_PROMPT = """You are an expert food recognition AI specializing in Russian and international cuisine. Your task is to identify COMPLETE DISHES, not just ingredients.

CRITICAL RULE - MOST IMPORTANT:
NEVER return just a raw ingredient name (like "beef", "chicken", "pork") as dish_name!
ALWAYS identify the PREPARED DISH based on cooking method and presentation!

VISUAL DISH IDENTIFICATION RULES:

1. MEAT ON SKEWERS/WOODEN STICKS:
   - Visual cues: cylindrical meat pieces, wooden/metal sticks, grill marks, charred edges
   - CORRECT dish_name: "beef skewers", "chicken shashlik", "pork kebabs"
   - WRONG dish_name: "beef", "chicken", "meat" (these are ingredients!)
   - Example: Meat on wooden sticks → "шашлык из говядины" NOT "говядина"

2. STEAKS:
   - Visual cues: thick cut meat, grill marks, seared exterior, meat texture visible
   - CORRECT dish_name: "beef steak", "pork steak", "grilled steak"
   - WRONG dish_name: "beef", "pork", "meat"
   - Example: Grilled meat cutlet → "стейк из говядины" NOT "говядина"

3. GRILLED/ROASTED MEAT:
   - Visual cues: browning, grill marks, roasted appearance, whole pieces
   - CORRECT dish_name: "grilled chicken", "roasted pork", "grilled lamb"
   - WRONG dish_name: "chicken", "pork", "lamb"

4. SOUPS (LIQUID IN BOWL):
   - Visual cues: liquid broth, ingredients submerged, served in deep bowl
   - CORRECT dish_name: "borscht", "shchi", "chicken soup", "ukha"
   - WRONG dish_name: "meat with vegetables", "beet soup" (too generic)

5. COMPLEX DISHES:
   - Identify complete dish: "pasta with salmon", "chicken with rice", "beef stew"
   - NOT just: "salmon", "chicken", "beef"

FOOD CATEGORIES WITH DISH EXAMPLES:

🍢 SKEWERS/KEBABS (ПРИОРИТЕТ 100%):
- Beef on sticks → "beef skewers" / "шашлык из говядины"
- Chicken on sticks → "chicken shashlik" / "шашлык из курицы"
- Pork on sticks → "pork kebabs" / "шашлык из свинины"
- Lamb on sticks → "lamb shashlik" / "шашлык из баранины"
- NEVER just "beef", "chicken", "pork"!

🥩 STEAKS & GRILLED MEAT:
- Thick beef cut with grill marks → "beef steak" / "стейк из говядины"
- Grilled pork chop → "pork steak" / "стейк из свинины"
- Grilled chicken breast → "grilled chicken breast" / "куриная грудка гриль"
- NEVER just "beef", "pork", "chicken"!

🍲 SOUPS:
- Red soup with beets → "borscht" / "борщ"
- Cabbage soup → "shchi" / "щи"
- Fish soup → "ukha" / "уха"
- Pickle soup → "solyanka" / "солянка"
- NEVER "meat with vegetables"!

🍝 PASTA & GRAINS:
- Pasta with sauce → "pasta with tomato sauce" / "паста с томатным соусом"
- Rice with meat → "rice with beef" / "рис с говядиной"
- Buckwheat with meat → "buckwheat with meat" / "гречка с мясом"

🥗 SALADS:
- Mixed greens → "green salad" / "зеленый салат"
- Caesar salad → "caesar salad" / "салат цезарь"
- Olivier salad → "olivier salad" / "салат оливье"

OUTPUT FORMAT - STRICT JSON:
{
  "dish_name": "SPECIFIC DISH NAME (e.g., 'beef skewers', 'borscht', 'grilled chicken breast')",
  "dish_name_ru": "Название на русском (e.g., 'шашлык из говядины', 'борщ', 'куриная грудка гриль')",
  "category": "skewers|steak|soup|pasta|salad|main|side",
  "confidence": 0.0-1.0,
  "ingredients": [
    {
      "name": "ingredient name (e.g., 'beef', 'onion', 'tomato')",
      "type": "protein|carb|vegetable|fat|sauce",
      "estimated_weight_grams": number,
      "confidence": 0.0-1.0
    }
  ],
  "cooking_method": "grilled|fried|boiled|baked|steamed|raw|stewed",
  "visual_cues": "brief description of what you see (e.g., 'meat on wooden sticks with grill marks')"
}

✅ EXAMPLES OF CORRECT RECOGNITION:

Example 1 - Meat Skewers:
Image: Meat pieces on wooden sticks with grill marks
CORRECT: {
  "dish_name": "beef skewers",
  "dish_name_ru": "шашлык из говядины",
  "category": "skewers",
  "ingredients": [
    {"name": "beef", "type": "protein", "estimated_weight_grams": 200},
    {"name": "onion", "type": "vegetable", "estimated_weight_grams": 30}
  ],
  "cooking_method": "grilled",
  "visual_cues": "cylindrical meat pieces threaded on wooden sticks, charred exterior, grill marks"
}
WRONG: {"dish_name": "beef"} ❌ This is an ingredient, not a dish!

Example 2 - Steak:
Image: Thick cut beef with grill marks
CORRECT: {
  "dish_name": "beef steak",
  "dish_name_ru": "стейк из говядины",
  "category": "steak",
  "ingredients": [
    {"name": "beef", "type": "protein", "estimated_weight_grams": 250}
  ],
  "cooking_method": "grilled",
  "visual_cues": "thick cut meat, seared exterior, visible grill marks, meat texture"
}
WRONG: {"dish_name": "beef"} ❌ This is an ingredient, not a dish!

Example 3 - Borscht:
Image: Red soup in bowl with sour cream
CORRECT: {
  "dish_name": "borscht",
  "dish_name_ru": "борщ",
  "category": "soup",
  "ingredients": [
    {"name": "beets", "type": "vegetable", "estimated_weight_grams": 80},
    {"name": "cabbage", "type": "vegetable", "estimated_weight_grams": 60},
    {"name": "beef", "type": "protein", "estimated_weight_grams": 50},
    {"name": "sour cream", "type": "fat", "estimated_weight_grams": 30}
  ],
  "cooking_method": "stewed",
  "visual_cues": "red liquid broth, vegetables submerged, sour cream garnish on top"
}
WRONG: {"dish_name": "meat with bread"} ❌ Completely wrong!

Example 4 - Grilled Chicken:
Image: Chicken breast with grill marks
CORRECT: {
  "dish_name": "grilled chicken breast",
  "dish_name_ru": "куриная грудка гриль",
  "category": "main",
  "ingredients": [
    {"name": "chicken", "type": "protein", "estimated_weight_grams": 200}
  ],
  "cooking_method": "grilled",
  "visual_cues": "white meat, grill marks, seared exterior"
}
WRONG: {"dish_name": "chicken"} ❌ This is an ingredient, not a dish!

Example 5 - Pasta with Salmon:
Image: Pink fish fillet with pasta and salad
CORRECT: {
  "dish_name": "grilled salmon with pasta",
  "dish_name_ru": "лосось гриль с пастой",
  "category": "main",
  "ingredients": [
    {"name": "salmon", "type": "protein", "estimated_weight_grams": 150},
    {"name": "pasta", "type": "carb", "estimated_weight_grams": 120},
    {"name": "lettuce", "type": "vegetable", "estimated_weight_grams": 50}
  ],
  "cooking_method": "grilled",
  "visual_cues": "pink flaky fish fillet, pasta strands, green salad leaves"
}
WRONG: {"dish_name": "meat with pasta"} ❌ Fish is not meat!

🚨 FINAL CHECKLIST BEFORE RETURNING:
1. ✅ Is dish_name a COMPLETE DISH (not just an ingredient)?
2. ✅ Does it include cooking method if visible (grilled, fried, etc.)?
3. ✅ Are ingredients listed separately from dish_name?
4. ✅ For skewers: did you include "skewers/shashlik/kebabs" in dish_name?
5. ✅ For steaks: did you include "steak" in dish_name?
6. ✅ For soups: is it identified as specific soup (borscht, shchi, etc.)?

NOW ANALYZE THE IMAGE AND RETURN ONLY VALID JSON WITH SPECIFIC DISH NAME!"""

# ========== FOOD EXPERT AI PROMPT ==========
FOOD_EXPERT_AI_PROMPT = """You are FoodExpert-AI. Analyze this food image and return ONLY valid JSON.

═══════════════════════════════════════════════════════════════
🎯 CRITICAL RULE #1 (MOST IMPORTANT):
═══════════════════════════════════════════════════════════════
dish_name MUST be a COMPLETE PREPARED DISH, NEVER just an ingredient!

❌ WRONG: {"dish_name": "beef"} ← This is an INGREDIENT!
❌ WRONG: {"dish_name": "chicken"} ← This is an INGREDIENT!
❌ WRONG: {"dish_name": "salmon"} ← This is an INGREDIENT!
❌ WRONG: {"dish_name": "mixed dish"} ← Too generic!

✅ CORRECT: {"dish_name": "beef shashlik"} ← Complete dish!
✅ CORRECT: {"dish_name": "grilled chicken breast"} ← Complete dish!
✅ CORRECT: {"dish_name": "borscht"} ← Complete dish!
✅ CORRECT: {"dish_name": "salmon with pasta"} ← Complete dish!

═══════════════════════════════════════════════════════════════
📋 VISUAL DISH IDENTIFICATION TABLE:
═══════════════════════════════════════════════════════════════
┌─────────────────────────────────┬──────────────────────────────┐
│ WHAT YOU SEE                    │ CORRECT dish_name            │
├─────────────────────────────────┼──────────────────────────────┤
│ Meat on wooden/metal sticks     │ "{meat} shashlik/kebabs"     │
│ Thick meat + grill marks        │ "{meat} steak"                │
│ Red soup + beets + sour cream   │ "borscht"                     │
│ Liquid broth + vegetables       │ "{type} soup"                 │
│ Pink fish + pasta shapes        │ "salmon with pasta"           │
│ Pink fish + rice grains         │ "salmon with rice"            │
│ Bowtie/farfalle pasta           │ "pasta" NOT "rice"            │
│ Mixed raw vegetables + dressing │ "{type} salad"                │
│ Breaded cutlet + fried          │ "cutlet" or "schnitzel"       │
│ Dumplings in broth              │ "pelmeni" or "dumplings"      │
└─────────────────────────────────┴──────────────────────────────┘

═══════════════════════════════════════════════════════════════
🔍 INGREDIENT TYPE RULES:
═══════════════════════════════════════════════════════════════
• FISH ≠ MEAT: salmon/trout/tuna = "protein" type "fish"
• PASTA ≠ RICE: farfalle/spaghetti/penne = "carb" type "pasta"
• SOUP = liquid in bowl with submerged ingredients
• SKEWERS = meat ONLY (fish on sticks is rare, verify carefully)

═══════════════════════════════════════════════════════════════
📦 REQUIRED JSON FORMAT (STRICT):
═══════════════════════════════════════════════════════════════
{
  "dish_name": "SPECIFIC DISH (e.g., 'beef shashlik', 'borscht')",
  "dish_name_ru": "Название на русском",
  "category": "skewers|steak|soup|pasta|salad|main|side|dessert",
  "confidence": 0.0-1.0,
  "ingredients": [
    {
      "name": "ingredient",
      "name_ru": "название на русском",
      "type": "protein|carb|vegetable|fat|dairy|sauce",
      "estimated_weight_grams": 100,
      "confidence": 0.9,
      "visual_cue": "brief description"
    }
  ],
  "cooking_method": "grilled|fried|boiled|baked|steamed|raw|stewed",
  "portion_size": "small|medium|large",
  "visual_cues": "what you see in 1 sentence"
}

═══════════════════════════════════════════════════════════════
✅ FEW-SHOT EXAMPLES:
═══════════════════════════════════════════════════════════════

EXAMPLE 1 - SHASHLIK:
Image: Brown meat pieces on wooden sticks, grill marks, onions
{
  "dish_name": "beef shashlik",
  "dish_name_ru": "шашлык из говядины",
  "category": "skewers",
  "ingredients": [
    {"name": "beef", "name_ru": "говядина", "type": "protein", "estimated_weight_grams": 200, "confidence": 0.92, "visual_cue": "charred meat on wooden skewers"},
    {"name": "onion", "name_ru": "лук", "type": "vegetable", "estimated_weight_grams": 30, "confidence": 0.78, "visual_cue": "caramelized onion pieces"}
  ],
  "cooking_method": "grilled",
  "portion_size": "medium",
  "visual_cues": "grilled meat pieces threaded on wooden sticks with char marks"
}

EXAMPLE 2 - BORSCHT:
Image: Red soup in white bowl, sour cream, dill, bread
{
  "dish_name": "borscht",
  "dish_name_ru": "борщ",
  "category": "soup",
  "ingredients": [
    {"name": "beef", "name_ru": "говядина", "type": "protein", "estimated_weight_grams": 80, "confidence": 0.88, "visual_cue": "dark meat chunks"},
    {"name": "beetroot", "name_ru": "свёкла", "type": "vegetable", "estimated_weight_grams": 60, "confidence": 0.95, "visual_cue": "deep red shredded vegetable"},
    {"name": "cabbage", "name_ru": "капуста", "type": "vegetable", "estimated_weight_grams": 40, "confidence": 0.85, "visual_cue": "pale green shreds"},
    {"name": "sour cream", "name_ru": "сметана", "type": "dairy", "estimated_weight_grams": 30, "confidence": 0.90, "visual_cue": "white dollop on surface"}
  ],
  "cooking_method": "stewed",
  "portion_size": "medium",
  "visual_cues": "red broth with beetroot shreds, meat, and sour cream garnish"
}

EXAMPLE 3 - SALMON WITH PASTA:
Image: Pink fish fillet, bowtie pasta, green salad
{
  "dish_name": "grilled salmon with pasta",
  "dish_name_ru": "лосось гриль с пастой",
  "category": "main",
  "ingredients": [
    {"name": "salmon", "name_ru": "лосось", "type": "protein", "estimated_weight_grams": 150, "confidence": 0.93, "visual_cue": "pink-orange flaky fish with grill marks"},
    {"name": "pasta", "name_ru": "паста", "type": "carb", "estimated_weight_grams": 120, "confidence": 0.88, "visual_cue": "bowtie-shaped pasta, not rice grains"},
    {"name": "lettuce", "name_ru": "салат", "type": "vegetable", "estimated_weight_grams": 50, "confidence": 0.82, "visual_cue": "fresh green leaves"}
  ],
  "cooking_method": "grilled",
  "portion_size": "medium",
  "visual_cues": "pink fish fillet with bowtie pasta and green salad"
}

═══════════════════════════════════════════════════════════════
🚨 FINAL VALIDATION CHECKLIST (BEFORE RETURNING):
═══════════════════════════════════════════════════════════════
□ Is dish_name a COMPLETE DISH (not just ingredient like "beef")?
□ For skewers: does dish_name include "shashlik/kebabs/skewers"?
□ For soups: is category = "soup" and dish specific (borscht/shchi)?
□ For pasta: did I verify it's NOT rice (check shape visually)?
□ For fish: is type = "protein" but NOT called "meat"?
□ Are all ingredients visually supported (no hallucinations)?
□ Is JSON valid (double quotes, no trailing commas)?

═══════════════════════════════════════════════════════════════
NOW ANALYZE THE IMAGE AND RETURN ONLY VALID JSON:
═══════════════════════════════════════════════════════════════
"""

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
    """
    Исправляет типичные ошибки распознавания, особенно для шашлыка
    """
    if not data or 'dish_name' not in data:
        return data
    
    dish_name = data.get('dish_name', '').lower()
    ingredients = data.get('ingredients', [])
    ingredient_names = [ing.get('name', '').lower() for ing in ingredients]
    cooking_method = data.get('cooking_method', '').lower()
    
    logger.info(f"🔧 Starting error correction for: {dish_name}")
    
    # ========== КРИТИЧЕСКОЕ: ШАШЛЫК/KEBABS ==========
    skewer_indicators = [
        'grilled', 'stick', 'skewer', 'kebab', 'shashlik',
        'шашлык', 'шампур', 'на палочке', 'на шпажке'
    ]
    meat_types = ['beef', 'pork', 'chicken', 'lamb', 'meat', 
                  'говядина', 'свинина', 'курица', 'баранина', 'мясо']
    
    # Если есть признаки шампуров + мясо = это шашлык!
    has_skewer_hint = any(ind in dish_name or ind in ' '.join(ingredient_names) 
                          for ind in skewer_indicators)
    has_meat = any(meat in ingredient_names for meat in meat_types)
    is_grilled = cooking_method == 'grilled'
    
    if has_meat and (has_skewer_hint or is_grilled):
        # Определяем тип мяса
        meat_type = 'meat'
        for meat in meat_types:
            if meat in ingredient_names or meat in dish_name:
                meat_type = meat
                break
        
        # Выбираем название блюда
        if 'chicken' in meat_type or 'курица' in meat_type:
            data['dish_name'] = 'chicken shashlik'
        elif 'beef' in meat_type or 'говядина' in meat_type:
            data['dish_name'] = 'beef shashlik'
        elif 'pork' in meat_type or 'свинина' in meat_type:
            data['dish_name'] = 'pork shashlik'
        elif 'lamb' in meat_type or 'баранина' in meat_type:
            data['dish_name'] = 'lamb shashlik'
        else:
            data['dish_name'] = 'meat shashlik'
        
        data['cooking_method'] = 'grilled'
        logger.info(f"🔧 FIXED: Identified as shashlik - {data['dish_name']}")
    
    # ========== ЗАЩИТА: ingredient ≠ dish ==========
    # Если dish_name совпадает с ingredient - это ошибка!
    ingredient_only_dishes = ['beef', 'pork', 'chicken', 'lamb', 'meat', 'fish', 
                              'говядина', 'свинина', 'курица', 'баранина', 'мясо', 'рыба']
    
    if dish_name in ingredient_only_dishes:
        # Это ингредиент, а не блюдо! Нужно определить блюдо по контексту
        if cooking_method == 'grilled':
            data['dish_name'] = f"{dish_name} grilled"
        elif cooking_method == 'fried':
            data['dish_name'] = f"{dish_name} fried"
        elif cooking_method == 'baked':
            data['dish_name'] = f"{dish_name} baked"
        else:
            data['dish_name'] = f"{dish_name} dish"
        
        logger.info(f"🔧 FIXED: Changed ingredient '{dish_name}' to dish '{data['dish_name']}'")
    
    # ========== СУПЫ ==========
    if ('beets' in ingredient_names or 'свекла' in ingredient_names) and \
       ('cabbage' in ingredient_names or 'капуста' in ingredient_names):
        data['dish_name'] = 'borscht'
        data['category'] = 'soup'
        logger.info("🔧 FIXED: Identified as borscht")
    
    logger.info(f"🔧 Final result: {data['dish_name']}")
    return data


async def identify_food_ensemble(
    image_bytes: bytes,
    model_indices: Optional[List[int]] = None,
    progress_callback=None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Запускает несколько vision-моделей параллельно и объединяет результаты.
    model_indices: список индексов моделей из VISION_MODELS (по умолчанию [0,1] — LLaVA и UForm)
    Возвращает (объединённые данные, строка с именами использованных моделей)
    """
    if not BASE_URL:
        logger.error("❌ Cloudflare BASE_URL not configured")
        return None, None

    if model_indices is None:
        model_indices = [0, 1]  # первые две: LLaVA и UForm

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

    prompt = FOOD_EXPERT_AI_PROMPT  # используем тот же улучшенный промпт

    async def run_single_model(model_info: dict) -> Tuple[Optional[Dict], Optional[str]]:
        model = model_info["id"]
        timeout = model_info["timeout"]
        try:
            url = f"{BASE_URL}{model}"
            payload = {
                "image": image_array,
                "prompt": prompt,
                "max_tokens": 800,
            }
            if model == "@cf/llava-hf/llava-1.5-7b-hf":
                payload["temperature"] = 0.1

            logger.info(f"🤖 Starting ensemble model: {model}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.warning(f"❌ Model {model} HTTP {resp.status}: {error_text[:100]}")
                        return None, model

                    result = await resp.json()
                    description = result.get("result", {}).get("description", "").strip()
                    if not description:
                        logger.warning(f"⚠️ Model {model} empty description")
                        return None, model

                    data = _extract_json_from_text(description)
                    if not data:
                        logger.warning(f"⚠️ Model {model} failed to extract JSON")
                        return None, model

                    is_valid, reason = _validate_food_data(data)
                    if not is_valid:
                        logger.warning(f"⚠️ Model {model} validation failed: {reason}")
                        return None, model

                    # пост-обработка
                    portion_size = data.get('portion_size', 'medium')
                    if 'ingredients' in data:
                        data['ingredients'] = _calibrate_weights(data['ingredients'], portion_size)
                        data = _fix_protein_identification(data)

                    logger.info(f"✅ Model {model} succeeded, confidence: {data.get('confidence', 0)}")
                    return data, model
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Model {model} timeout")
        except Exception as e:
            logger.warning(f"❌ Model {model} error: {type(e).__name__}: {e}")
        return None, model

    # Запускаем все модели параллельно
    tasks = [run_single_model(m) for m in models_to_use]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Собираем успешные результаты
    valid_results = []
    for res in results:
        if isinstance(res, Exception):
            logger.warning(f"🔥 Exception in ensemble task: {res}")
            continue
        data, model_name = res
        if data:
            # Добавляем вес модели для взвешенного голосования
            model_weight = next((m["weight"] for m in models_to_use if m["id"] == model_name), 1.0)
            valid_results.append((data, model_name, model_weight))

    if not valid_results:
        logger.error("❌ All ensemble models failed")
        return None, None

    if progress_callback:
        await progress_callback(stage=3, progress=80)

    # --- Агрегация результатов ---
    # Простой вариант: выбрать результат с максимальной уверенностью * вес модели
    best_data = None
    best_score = -1
    best_model = None
    for data, model_name, weight in valid_results:
        conf = data.get('confidence', 0) * weight
        if conf > best_score:
            best_score = conf
            best_data = data
            best_model = model_name

    # Усложнённый вариант: если несколько результатов с близкой уверенностью,
    # можно объединить ингредиенты (взять пересечение или объединение с фильтром по confidence)
    # Для простоты пока оставляем выбор лучшего.

    # Финальная проверка: если dish_name остался ингредиентом, применяем фикс ещё раз
    best_data = _fix_common_recognition_errors(best_data)

    # Кэшируем результат
    _cache_result(image_hash, best_data)

    if progress_callback:
        await progress_callback(stage=4, progress=100)

    logger.info(f"🏆 Ensemble chose model {best_model} with confidence {best_data.get('confidence', 0)}")
    return best_data, f"ensemble({best_model})"


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
        prompt = FOOD_EXPERT_AI_PROMPT
    
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
                "consensus": True,  # Ансамбль обеспечивает консенсус
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
        prompt = SIMPLE_INGREDIENTS_PROMPT
    
    ingredients = await get_simple_ingredients(image_bytes)
    if ingredients:
        return ", ".join(ingredients)
    return None

