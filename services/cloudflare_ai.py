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

# ========== СПЕЦИАЛИЗИРОВАННЫЕ ПРОМПТЫ ДЛЯ АНСАМБЛЯ ==========

# Улучшенный промпт для LLaVA на основе исследований 2024-2025
ENHANCED_FOOD_RECOGNITION_PROMPT = """You are an expert food recognition AI specialized in Russian and international cuisine.

TASK: Analyze this food image and identify:
1) The COMPLETE DISH with specific name (not just an ingredient)
2) All visible food ingredients with accurate names

CRITICAL RULE #1 - NEVER RETURN INGREDIENTS AS DISH:
- ❌ WRONG: "meat", "beef", "pork", "chicken", "fish", "rice", "potato" - these are INGREDIENTS!
- ✅ RIGHT: "grilled pork", "beef stew", "chicken soup", "fried fish", "pilaf", "potato pancakes"

CRITICAL RULE #2 - DISH NAME MUST INCLUDE COOKING METHOD:
- "grilled pork" not just "pork"
- "fried chicken" not just "chicken"
- "baked fish" not just "fish"
- "boiled rice" not just "rice"

CRITICAL RULE #3 - IDENTIFY DISH CATEGORY BY VISUAL CUES:

SOUPS (liquid in bowl, steam, broth):
- With beets + cabbage → "borscht" (борщ)
- With cabbage only → "shchi" (щи)
- With pickles → "rassolnik" (рассольник)
- With fish → "ukha" (уха)
- Clear broth + meat/vegetables → "soup" (суп)

GRILLED/SKEWERED (visible skewers, grill marks, charred marks):
- Meat on wooden/metal sticks → "pork shashlik" / "beef shashlik" / "chicken shashlik" (шашлык)
- Multiple small pieces on skewer → "kebab" (кебаб)

FRIED DISHES (golden color, oil, pan visible):
- Meat in pan → "fried pork" / "fried beef"
- Potatoes in pan → "fried potatoes" / "home fries"
- Eggs in pan → "fried eggs" / "scrambled eggs"

BAKED (oven dish, casserole, golden top):
- Meat with vegetables in oven dish → "baked meat" / "baked chicken"
- With cheese topping → "casserole" (запеканка)

STEAMED/DUMPLINGS (folded dough, steam):
- Small folded dough → "dumplings" (пельмени, манты, хинкали)
- With soup → "dumplings in broth"

SALADS (fresh vegetables, bowl, no heat):
- Mixed vegetables → "salad" (салат)
- With herring → "herring salad" (селедка под шубой)
- With potatoes + eggs → "olivier salad" (оливье)

PILAF/RICE DISHES (rice with meat/vegetables, large pot):
- Rice with meat → "pilaf" (плов)
- Rice with vegetables → "vegetable rice"

CRITICAL RULE #4 - MEAT TYPE IDENTIFICATION:
- White meat → chicken/turkey
- Red meat → beef/pork/lamb
- Pink pork → pork
- Dark red → beef
- Fish: pink/orange → salmon, white flaky → cod/whitefish

CRITICAL RULE #5 - ACCURATE INGREDIENT NAMING:
- White crystals on surface → salt (соль), NOT rice
- Green herb sprigs → parsley/dill/rosemary (петрушка/укроп/розмарин), NOT onion
- Brown particles → pepper/spices (перец/специи), NOT bell pepper
- Orange/red flakes → paprika, NOT tomato
- Dark liquid → soy sauce (соевый соус), NOT just "sauce"

CRITICAL RULE #6 - RUSSIAN NAMES (MUST INCLUDE):
- Always provide both English and Russian dish names
- Use Russian cuisine terminology: борщ, щи, шашлык, плов, пельмени, оливье, etc.

OUTPUT: Return ONLY strict JSON (no markdown, no extra text):
{
  "dish_name": "specific dish name with cooking method (e.g., grilled pork shashlik)",
  "dish_name_ru": "название на русском с методом приготовления (e.g., свиной шашлык)",
  "category": "soup|grilled|fried|baked|steamed|salad|pilaf|dumplings|other",
  "cooking_method": "grilled|fried|boiled|steamed|baked|raw|stewed",
  "meal_type": "breakfast|lunch|dinner|snack",
  "portion_size": "small|medium|large",
  "is_soup": false,
  "has_skewers": true,
  "meat_type": "pork|beef|chicken|lamb|fish|turkey|none",
  "ingredients": [
    {"name": "ingredient", "type": "protein|vegetable|carb|fat|sauce|herb|spice|other", "estimated_weight_grams": 100, "confidence": 0.9}
  ],
  "confidence": 0.0
}
"""

# Экспертная система для вероятностного определения блюд на основе визуальных признаков
FOOD_VISUAL_CLASSIFICATION_PROMPT = """You are an expert food analyst specializing in visual food recognition and classification.

🎯 CRITICAL TASK: Analyze visual characteristics and provide PROBABILISTIC dish identification with confidence scores.

📋 VISUAL ANALYSIS FRAMEWORK:

1️⃣ MEAT ANALYSIS:
   - TYPE: beef, pork, chicken, lamb, turkey, duck
   - FORM: whole, steak, chunks, cubes, strips, ground, minced
   - CUT: fillet, chop, cutlet, leg, wing, breast, thigh, ribs
   - PREPARATION: grilled, roasted, fried, stewed, boiled, smoked
   - VISUAL CUES: grill marks, charred, browned, crispy, juicy, tender

2️⃣ FISH ANALYSIS:
   - TYPE: salmon, tuna, cod, tilapia, mackerel, herring, trout
   - FORM: whole fish, steak, fillet, pieces, smoked, salted
   - PREPARATION: grilled, fried, baked, steamed, raw (sushi)
   - VISUAL CUES: pink flesh, white flakes, skin on/off, bones, herbs

3️⃣ SOUP/STEW ANALYSIS:
   - CONSISTENCY: clear, creamy, thick, chunky, pureed
   - COLOR: red (borscht), green (shchi), orange (pumpkin), white (cream), brown (meat)
   - INGREDIENTS: visible vegetables, meat pieces, noodles, dumplings
   - GARNISH: sour cream, herbs, croutons, cheese

4️⃣ COOKING METHOD DETECTION:
   - GRILLED: parallel char marks, smoky appearance
   - FRIED: golden crust, oil sheen, crispy edges
   - STEWED: soft texture, liquid base, mixed ingredients
   - BAKED: uniform browning, dry surface
   - BOILED: moist appearance, no browning

🎲 PROBABILISTIC IDENTIFICATION RULES:

MEAT DISHES:
- Steak: single thick piece + grill marks + no sauce
  → "beef steak" (0.9), "pork steak" (0.8), "chicken breast" (0.7)
- Shashlik/Kebab: cubes + sticks + charred + often with onion
  → "pork shashlik" (0.85), "chicken kebab" (0.8), "beef shashlik" (0.8)
- Stew/Ragout: chunks + sauce + vegetables + soft texture
  → "beef stew" (0.8), "chicken ragout" (0.7), "meat goulash" (0.75)
- Cutlet/Fillet: flattened piece + breading + fried
  → "chicken cutlet" (0.8), "pork cutlet" (0.75), "turkey fillet" (0.7)
- Whole roasted: intact shape + golden skin + roasted appearance
  → "roast chicken" (0.85), "roast duck" (0.8), "roast pork" (0.75)

FISH DISHES:
- Fish steak: thick cross-section + visible bone structure + grilled
  → "salmon steak" (0.85), "tuna steak" (0.8), "cod steak" (0.75)
- Fish fillet: flat piece + skin/boneless + pan-fried/baked
  → "grilled salmon" (0.8), "baked cod" (0.75), "fried tilapia" (0.7)
- Smoked fish: pink/orange color + shiny surface + distinct texture
  → "smoked salmon" (0.9), "smoked mackerel" (0.85), "smoked herring" (0.8)
- Whole fish: head + tail + scales + stuffed/fried
  → "stuffed fish" (0.8), "fried whole fish" (0.75)

SOUPS:
- Borscht: red/pink color + visible beets + cabbage + sour cream
  → "borscht" (0.95), "ukrainian borscht" (0.85)
- Shchi: green color + cabbage + sour cream + clear broth
  → "shchi" (0.9), "cabbage soup" (0.75)
- Cream soup: smooth texture + uniform color + no chunks
  → "cream of mushroom" (0.8), "pumpkin soup" (0.75), "tomato soup" (0.7)
- Chunky soup: visible pieces + thick consistency + mixed vegetables
  → "vegetable soup" (0.75), "chicken noodle soup" (0.8), "minestrone" (0.7)

📊 OUTPUT FORMAT:
{
  "primary_dish": {
    "name": "most likely dish",
    "name_ru": "название на русском",
    "confidence": 0.85,
    "reasoning": "visual cues that led to this conclusion"
  },
  "alternative_dishes": [
    {
      "name": "second possibility",
      "name_ru": "второй вариант",
      "confidence": 0.65,
      "reasoning": "why this could also be possible"
    }
  ],
  "visual_analysis": {
    "main_ingredient": "meat/fish/vegetable",
    "ingredient_type": "beef/chicken/salmon/etc",
    "form": "steak/chunks/fillet/etc",
    "cooking_method": "grilled/fried/stewed/etc",
    "texture": "tender/crispy/soft/etc",
    "color": "red/green/brown/etc",
    "consistency": "thick/creamy/clear/etc"
  },
  "key_visual_cues": ["grill marks", "cubes", "red color", "sour cream"],
  "certainty_level": "high/medium/low"
}

🔍 ANALYSIS PROCESS:
1. Identify main ingredient (meat/fish/vegetable)
2. Determine form and preparation method
3. Analyze visual cues and texture
4. Match against dish patterns
5. Provide probabilistic results with reasoning

NOW ANALYZE THE IMAGE and provide detailed probabilistic classification:"""


# Промпт для LLaVA - "шеф-повар" (контекст и структура блюда)
LLAVA_ENSEMBLE_PROMPT = """You are an expert food recognition AI specialized in Russian and international cuisine.

🚨 CRITICAL TASK: Identify COMPLETE DISH with SPECIFIC NAME.

🔍 VISUAL ANALYSIS CHECKLIST - CHECK EACH:
1. Are there WOODEN or METAL STICKS/SKEWERS visible? → YES = SHASHLIK/KEBAB
2. Are there GRILL MARKS (dark parallel lines) on meat? → YES = GRILLED
3. Is meat in CUBES threaded on sticks? → YES = SHASHLIK
4. Is there CHARRED/BROWNED exterior? → YES = GRILLED/ROASTED
5. Is it LIQUID in a bowl? → YES = SOUP
6. Is it RED soup with sour cream? → YES = BORSCHT

⚠️ MOST IMPORTANT RULES:

RULE 1: MEAT ON STICKS = SHASHLIK (100% CERTAINTY)
- If you see ANY sticks/skewers with meat → dish_name MUST include "shashlik" or "kebabs" or "skewers"
- Examples: "pork shashlik", "beef kebabs", "chicken skewers"
- NEVER return just "pork", "beef", "chicken" - these are INGREDIENTS!

RULE 2: THICK MEAT PIECE = STEAK (NOT SHASHLIK)
- If you see THICK cut meat with grill marks BUT NO sticks → "steak"
- Examples: "beef steak", "pork steak", "chicken steak"
- Steak is a SINGLE thick piece, shashlik is meat CUBES on sticks

RULE 3: MEAT CHUNKS IN SAUCE = STEW/RAGOUT
- If you see meat PIECES in thick liquid/sauce → "stew", "ragout", "goulash"
- Examples: "beef stew", "chicken ragout", "meat goulash"

RULE 4: RED SOUP + BEETS = BORSCHT
- If you see red/pink liquid + vegetables → "borscht" (борщ)
- If sour cream on top → definitely borscht

RULE 5: FISH ANALYSIS
- Fish steak = thick cross-section with visible structure
- Fish fillet = flat piece, skin-on/off, no bones visible
- Smoked fish = pink/orange color, shiny surface
- Whole fish = head + tail + scales intact

RULE 6: SOUP CONSISTENCY
- Clear soup = visible ingredients in clear broth
- Cream soup = smooth, uniform, no chunks
- Chunky soup = visible pieces, thick consistency
- Red soup = beets + red/pink color

RULE 7: COOKING METHOD DETECTION
- Sticks/skewers visible → cooking_method = "grilled"
- Grill marks → cooking_method = "grilled"  
- Liquid in bowl → cooking_method = "boiled" or "stewed"
- Golden brown crust → cooking_method = "fried" or "baked"
- Soft pieces in sauce → cooking_method = "stewed"

SPECIFIC DISH EXAMPLES:
Image: Meat cubes on wooden sticks
✅ CORRECT: {"dish_name": "pork shashlik", "dish_name_ru": "свиной шашлык", "cooking_method": "grilled", "has_skewers": true}
❌ WRONG: {"dish_name": "pork"} ← This is an INGREDIENT!

Image: Thick piece of meat with grill marks (no sticks)
✅ CORRECT: {"dish_name": "beef steak", "dish_name_ru": "говяжий стейк", "cooking_method": "grilled", "has_skewers": false}
❌ WRONG: {"dish_name": "beef shashlik"} ← No sticks = NOT shashlik!

Image: Meat chunks in thick brown sauce
✅ CORRECT: {"dish_name": "beef stew", "dish_name_ru": "говядина в соусе", "cooking_method": "stewed", "has_skewers": false}
❌ WRONG: {"dish_name": "beef"} ← This is an INGREDIENT!

Image: Red soup with sour cream and herbs
✅ CORRECT: {"dish_name": "borscht", "dish_name_ru": "борщ", "cooking_method": "boiled", "is_soup": true}
❌ WRONG: {"dish_name": "soup"} ← Too generic!

Image: Fish with pink flesh and grill marks
✅ CORRECT: {"dish_name": "salmon steak", "dish_name_ru": "стейк лосося", "cooking_method": "grilled", "fish_type": "salmon"}
❌ WRONG: {"dish_name": "fish"} ← Too generic!

REQUIRED JSON FORMAT:
{
  "dish_name": "SPECIFIC DISH NAME (e.g., 'pork shashlik', 'beef steak', 'borscht', 'salmon steak')",
  "dish_name_ru": "Russian name",
  "category": "skewers|main|soup|fish|side|salad",
  "cooking_method": "grilled|fried|boiled|baked|steamed|stewed",
  "has_skewers": true/false,
  "is_soup": true/false,
  "meat_type": "pork|beef|chicken|lamb|fish|none",
  "fish_type": "salmon|tuna|cod|none",
  "confidence": 0.0-1.0,
  "ingredients": [
    {"name": "ingredient", "type": "protein|vegetable|carb|fat", "estimated_weight_grams": 100, "confidence": 0.9}
  ],
  "visual_cues": "Describe what you see: sticks, grill marks, thick pieces, cubes, color, consistency, etc."
}

NOW ANALYZE THE IMAGE CAREFULLY:
- Look for STICKS/SKEWERS first!
- Look for GRILL MARKS!
- Check if meat is in CUBES (shashlik) or THICK PIECES (steak) or CHUNKS (stew)
- Identify the SPECIFIC DISH, not ingredients!
- Analyze fish form: steak, fillet, whole, smoked
- Determine soup consistency: clear, creamy, chunky, red

Return ONLY valid JSON:"""

# Промпт для UForm - "помощник по ингредиентам" (детальное перечисление)
UFORM_INGREDIENTS_PROMPT = """You are an expert at identifying food ingredients from images.

CRITICAL RULES FOR ACCURATE IDENTIFICATION:
1. White crystals on food surface → SALT (соль), NOT rice
2. Green herb sprigs/leaves → PARSLEY (петрушка), DILL (укроп), or ROSEMARY (розмарин), NOT onion
3. Brown/red particles → PEPPER (перец) or SPICES (специи), NOT bell pepper
4. Dark liquid → SOY SAUCE (соевый соус), not just "sauce"
5. Orange/red flakes → PAPRIKA (паприка), NOT tomato
6. Small green leaves → BASIL (базилик), NOT lettuce

List ALL visible food ingredients:
- Main ingredients (meat, fish, vegetables, grains)
- Garnishes and herbs (parsley, dill, rosemary, basil)
- Sauces and dressings
- Seasonings and spices

Return only ingredient names as comma-separated list.
Examples: pork, salt, rosemary, black pepper, vegetable oil
Do NOT include: plates, forks, napkins, table, hands

Ingredient names:"""

# Промпт для UForm - расширенная детализация
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
  "dish_name": "SPECIFIC DISH NAME",
  "dish_name_ru": "Название на русском",
  "category": "skewers|steak|soup|pasta|salad|main|side",
  "confidence": 0.0-1.0,
  "ingredients": [
    {
      "name": "ingredient name",
      "type": "protein|carb|vegetable|fat|sauce",
      "estimated_weight_grams": number,
      "confidence": 0.0-1.0
    }
  ],
  "cooking_method": "grilled|fried|boiled|baked|steamed|raw|stewed",
  "visual_cues": "brief description of what you see"
}

✅ EXAMPLES OF CORRECT RECOGNITION:

Image: Meat pieces on wooden sticks with grill marks
CORRECT: {
  "dish_name": "chicken skewers",
  "dish_name_ru": "шашлык из курицы",
  "category": "skewers",
  "ingredients": [
    {"name": "chicken", "type": "protein", "estimated_weight_grams": 200},
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
    """Исправляет типичные ошибки с ПРИОРИТЕТОМ на шашлык и борщ"""
    if not data or 'dish_name' not in data:
        return data
    
    dish_name = data.get('dish_name', '').lower()
    ingredients = data.get('ingredients', [])
    ingredient_names = [ing.get('name', '').lower() for ing in ingredients]
    cooking_method = data.get('cooking_method', '').lower()
    
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

            logger.info(f"👨‍🍳 Starting LLaVA model: {model}")
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
                logger.info(f"👨‍🍳 LLaVA provided structured dish data")
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
                            
                            # Фильтрация бытовых предметов
                            data = _filter_non_food_items(data)
                            if data.get('success') == False:
                                logger.warning(f"⚠️ Model {model} detected non-food items: {data.get('error')}")
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

