"""
Ğ Ğ�Ğ¡Ğ¨Ğ˜Ğ Ğ•Ğ�Ğ�Ğ�Ğ¯ Ğ‘Ğ�Ğ—Ğ� Ğ”Ğ�Ğ�Ğ�Ğ«Ğ¥ Ğ“Ğ�Ğ¢Ğ�Ğ’Ğ«Ğ¥ Ğ‘Ğ›Ğ®Ğ” Ğ¡ ĞŸĞ�Ğ”Ğ”Ğ•Ğ Ğ–ĞšĞ�Ğ™ Ğ�Ğ�Ğ“Ğ›Ğ˜Ğ™Ğ¡ĞšĞ˜Ğ¥ Ğ�Ğ�Ğ—Ğ’Ğ�Ğ�Ğ˜Ğ™
âœ… 200+ Ğ±Ğ»Ñ�Ğ´ Ñ� Ğ¿Ğ¾Ğ»Ğ½Ñ‹Ğ¼Ğ¸ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸ Ğ¸ ĞšĞ‘Ğ–Ğ£
âœ… Ğ‘Ğ¸Ğ»Ğ¸Ğ½Ğ³Ğ²Ğ°Ğ»ÑŒĞ½Ğ°Ñ� Ğ¿Ğ¾Ğ´Ğ´ĞµÑ€Ğ¶ĞºĞ° (RU + EN)
âœ… Ğ£Ğ»ÑƒÑ‡ÑˆĞµĞ½Ğ½Ñ‹Ğ¹ Ğ¿Ğ¾Ğ¸Ñ�Ğº Ñ� ÑƒÑ‡Ñ‘Ñ‚Ğ¾Ğ¼ Ñ�Ğ¸Ğ½Ğ¾Ğ½Ğ¸Ğ¼Ğ¾Ğ² Ğ¸ keywords
"""
from typing import Dict, List, Optional
import logging
from difflib import SequenceMatcher
from services.translator import AI_TO_DB_MAPPING

logger = logging.getLogger(__name__)

# =============================================================================
# ğŸ�½ï¸� Ğ‘Ğ�Ğ—Ğ� Ğ“Ğ�Ğ¢Ğ�Ğ’Ğ«Ğ¥ Ğ‘Ğ›Ğ®Ğ” (200+ Ğ½Ğ°Ğ¸Ğ¼ĞµĞ½Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğ¹)
# =============================================================================
COMPOSITE_DISHES = {
    # ==================== Ğ¨Ğ�Ğ¨Ğ›Ğ«ĞšĞ˜ Ğ˜ Ğ“Ğ Ğ˜Ğ›Ğ¬ ====================
    "ÑˆĞ°ÑˆĞ»Ñ‹Ğº": {
        "name": "Ğ¨Ğ°ÑˆĞ»Ñ‹Ğº",
        "name_en": ["shashlik", "shish kebab", "meat skewers", "grilled meat skewers", "kebab", "grilled meat"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 20.0, "fat": 15.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 70},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ÑˆĞ°ÑˆĞ»Ñ‹Ğº", "ĞºĞµĞ±Ğ°Ğ±", "Ğ³Ñ€Ğ¸Ğ»ÑŒ", "skewer", "kebab", "grilled meat", "meat skewers"]
    },
    "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· ĞºÑƒÑ€Ğ¸Ñ†Ñ‹": {
        "name": "Ğ¨Ğ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· ĞºÑƒÑ€Ğ¸Ñ†Ñ‹",
        "name_en": ["chicken shashlik", "chicken skewers", "grilled chicken skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 165, "protein": 22.0, "fat": 8.0, "carbs": 2.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 75},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "other", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ÑˆĞ°ÑˆĞ»Ñ‹Ğº", "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "chicken", "skewers", "Ğ³Ñ€Ğ¸Ğ»ÑŒ"]
    },
    "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹": {
        "name": "Ğ¨Ğ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹",
        "name_en": ["beef shashlik", "beef skewers", "grilled beef skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 22.0, "fat": 13.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 75},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "other", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ÑˆĞ°ÑˆĞ»Ñ‹Ğº", "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "beef", "skewers", "Ğ³Ñ€Ğ¸Ğ»ÑŒ"]
    },
    "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ñ‹": {
        "name": "Ğ¨Ğ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ñ‹",
        "name_en": ["lamb shashlik", "lamb skewers", "grilled lamb skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 20.0, "fat": 17.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 75},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "other", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ÑˆĞ°ÑˆĞ»Ñ‹Ğº", "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "lamb", "skewers", "Ğ³Ñ€Ğ¸Ğ»ÑŒ"]
    },
    "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ³Ñ€Ğ¸Ğ»ÑŒ": {
        "name": "ĞšÑƒÑ€Ğ¸Ñ†Ğ° Ğ³Ñ€Ğ¸Ğ»ÑŒ",
        "name_en": ["grilled chicken", "chicken grill", "roast chicken", "bbq chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 185, "protein": 24.0, "fat": 9.5, "carbs": 1.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 95},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "other", "percent": 5}
        ],
        "keywords": ["ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "Ğ³Ñ€Ğ¸Ğ»ÑŒ", "chicken", "grill", "roast", "bbq"]
    },
    "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�": {
        "name": "ĞšÑƒÑ€Ğ¸Ñ†Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�",
        "name_en": ["baked chicken", "roasted chicken", "oven chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 24.0, "fat": 10.0, "carbs": 1.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 95},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "other", "percent": 2},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 3}
        ],
        "keywords": ["ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�", "chicken", "baked", "roasted", "oven"]
    },
    "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�": {
        "name": "ĞšÑƒÑ€Ğ¸Ñ†Ğ° Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�",
        "name_en": ["fried chicken", "pan-fried chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 23.0, "fat": 14.0, "carbs": 2.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 85},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "other", "percent": 5}
        ],
        "keywords": ["ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�", "chicken", "fried"]
    },
    # ==================== Ğ¡Ğ£ĞŸĞ« ====================
    "Ğ±Ğ¾Ñ€Ñ‰": {
        "name": "Ğ‘Ğ¾Ñ€Ñ‰",
        "name_en": ["borscht", "borsch", "beet soup", "russian soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 60, "protein": 3.0, "fat": 2.5, "carbs": 6.5},
        "ingredients": [
            {"name": "Ñ�Ğ²ĞµĞºĞ»Ğ°", "type": "vegetable", "percent": 15},
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "type": "vegetable", "percent": 20},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 15},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 15}
        ],
        "keywords": ["Ğ±Ğ¾Ñ€Ñ‰", "Ñ�Ğ²ĞµĞºĞ»Ğ°", "borscht", "beet", "soup"]
    },
    "Ğ±Ğ¾Ñ€Ñ‰ ÑƒĞºÑ€Ğ°Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹": {
        "name": "Ğ‘Ğ¾Ñ€Ñ‰ ÑƒĞºÑ€Ğ°Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹",
        "name_en": ["ukrainian borscht", "ukrainian beet soup"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 75, "protein": 4.0, "fat": 3.0, "carbs": 7.5},
        "ingredients": [
            {"name": "Ñ�Ğ²ĞµĞºĞ»Ğ°", "type": "vegetable", "percent": 15},
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "type": "vegetable", "percent": 15},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 12},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5},
            {"name": "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ°Ğ»Ğ¾", "type": "fat", "percent": 2},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 18}
        ],
        "keywords": ["Ğ±Ğ¾Ñ€Ñ‰", "ÑƒĞºÑ€Ğ°Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "ukrainian", "borscht"]
    },
    "Ñ‰Ğ¸": {
        "name": "Ğ©Ğ¸",
        "name_en": ["shchi", "cabbage soup", "russian cabbage soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 2.5, "fat": 1.8, "carbs": 5.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "type": "vegetable", "percent": 30},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 12},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 3},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 27}
        ],
        "keywords": ["Ñ‰Ğ¸", "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "shchi", "cabbage", "soup"]
    },
    "Ñ€Ğ°Ñ�Ñ�Ğ¾Ğ»ÑŒĞ½Ğ¸Ğº": {
        "name": "Ğ Ğ°Ñ�Ñ�Ğ¾Ğ»ÑŒĞ½Ğ¸Ğº",
        "name_en": ["rassolnik", "pickle soup", "russian pickle soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 55, "protein": 2.8, "fat": 2.2, "carbs": 6.0},
        "ingredients": [
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ", "type": "vegetable", "percent": 15},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¿ĞµÑ€Ğ»Ğ¾Ğ²ĞºĞ°", "type": "carb", "percent": 10},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 12},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 30}
        ],
        "keywords": ["Ñ€Ğ°Ñ�Ñ�Ğ¾Ğ»ÑŒĞ½Ğ¸Ğº", "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹", "rassolnik", "pickle", "soup"]
    },
    "Ñ�Ğ¾Ğ»Ñ�Ğ½ĞºĞ°": {
        "name": "Ğ¡Ğ¾Ğ»Ñ�Ğ½ĞºĞ° Ğ¼Ñ�Ñ�Ğ½Ğ°Ñ�",
        "name_en": ["solyanka", "meat solyanka", "russian mixed soup"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 95, "protein": 7.0, "fat": 5.5, "carbs": 4.5},
        "ingredients": [
            {"name": "Ğ¼Ñ�Ñ�Ğ¾ Ğ°Ñ�Ñ�Ğ¾Ñ€Ñ‚Ğ¸", "type": "protein", "percent": 25},
            {"name": "ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ°", "type": "protein", "percent": 10},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "vegetable", "percent": 5},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5},
            {"name": "ĞºĞ°Ğ¿ĞµÑ€Ñ�Ñ‹", "type": "vegetable", "percent": 2},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 30}
        ],
        "keywords": ["Ñ�Ğ¾Ğ»Ñ�Ğ½ĞºĞ°", "Ğ¼Ñ�Ñ�Ğ¾", "solyanka", "meat", "soup"]
    },
    "ÑƒÑ…Ğ°": {
        "name": "Ğ£Ñ…Ğ°",
        "name_en": ["ukha", "fish soup", "russian fish soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 4.5, "fat": 1.5, "carbs": 3.0},
        "ingredients": [
            {"name": "Ñ€Ñ‹Ğ±Ğ°", "type": "protein", "percent": 25},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 47}
        ],
        "keywords": ["ÑƒÑ…Ğ°", "Ñ€Ñ‹Ğ±Ğ°", "ukha", "fish", "soup"]
    },
    "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿": {
        "name": "Ğ¡ÑƒĞ¿ ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹",
        "name_en": ["chicken soup", "chicken noodle soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 3.5, "fat": 1.5, "carbs": 3.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 20},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ²ĞµÑ€Ğ¼Ğ¸ÑˆĞµĞ»ÑŒ", "type": "carb", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 47}
        ],
        "keywords": ["Ñ�ÑƒĞ¿", "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "chicken", "soup"]
    },
    "Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ¾Ğ¹ Ñ�ÑƒĞ¿": {
        "name": "Ğ¡ÑƒĞ¿ Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ¾Ğ¹",
        "name_en": ["mushroom soup", "cream of mushroom soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 2.0, "fat": 1.8, "carbs": 4.0},
        "ingredients": [
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹", "type": "vegetable", "percent": 20},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 47}
        ],
        "keywords": ["Ñ�ÑƒĞ¿", "Ğ³Ñ€Ğ¸Ğ±Ñ‹", "mushroom", "soup"]
    },
    "Ğ³Ğ¾Ñ€Ğ¾Ñ…Ğ¾Ğ²Ñ‹Ğ¹ Ñ�ÑƒĞ¿": {
        "name": "Ğ¡ÑƒĞ¿ Ğ³Ğ¾Ñ€Ğ¾Ñ…Ğ¾Ğ²Ñ‹Ğ¹",
        "name_en": ["pea soup", "split pea soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 70, "protein": 4.5, "fat": 2.0, "carbs": 9.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ñ€Ğ¾Ñ…", "type": "protein", "percent": 25},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "ĞºĞ¾Ğ¿Ñ‡ĞµĞ½Ğ¾Ñ�Ñ‚Ğ¸", "type": "protein", "percent": 7},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 40}
        ],
        "keywords": ["Ñ�ÑƒĞ¿", "Ğ³Ğ¾Ñ€Ğ¾Ñ…", "pea", "soup"]
    },
    # ==================== Ğ¡Ğ�Ğ›Ğ�Ğ¢Ğ« ====================
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ†ĞµĞ·Ğ°Ñ€ÑŒ": {
        "name": "Ğ¦ĞµĞ·Ğ°Ñ€ÑŒ Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
        "name_en": ["caesar salad", "chicken caesar"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 185, "protein": 15.0, "fat": 12.0, "carbs": 5.5},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ°Ñ� Ğ³Ñ€ÑƒĞ´ĞºĞ°", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ€Ğ¾Ğ¼Ğ°Ğ½Ğ¾", "type": "vegetable", "percent": 35},
            {"name": "Ğ¿Ğ°Ñ€Ğ¼ĞµĞ·Ğ°Ğ½", "type": "dairy", "percent": 10},
            {"name": "Ñ�ÑƒÑ…Ğ°Ñ€Ğ¸ĞºĞ¸", "type": "carb", "percent": 10},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ†ĞµĞ·Ğ°Ñ€ÑŒ", "type": "sauce", "percent": 15}
        ],
        "keywords": ["Ñ†ĞµĞ·Ğ°Ñ€ÑŒ", "caesar", "Ñ�Ğ°Ğ»Ğ°Ñ‚", "salad"]
    },
    "Ğ³Ñ€ĞµÑ‡ĞµÑ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚": {
        "name": "Ğ“Ñ€ĞµÑ‡ĞµÑ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚",
        "name_en": ["greek salad", "horiatiki"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 135, "protein": 4.5, "fat": 11.0, "carbs": 4.0},
        "ingredients": [
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 35},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹", "type": "vegetable", "percent": 30},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹", "type": "vegetable", "percent": 15},
            {"name": "Ñ„ĞµÑ‚Ğ°", "type": "dairy", "percent": 15},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "vegetable", "percent": 5},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ³Ñ€ĞµÑ‡ĞµÑ�ĞºĞ¸Ğ¹", "greek", "Ñ„ĞµÑ‚Ğ°", "feta", "Ñ�Ğ°Ğ»Ğ°Ñ‚", "salad"]
    },
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ¾Ğ»Ğ¸Ğ²ÑŒĞµ": {
        "name": "Ğ�Ğ»Ğ¸Ğ²ÑŒĞµ",
        "name_en": ["olivier salad", "russian salad", "potato salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 8.0, "fat": 16.0, "carbs": 8.5},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 30},
            {"name": "ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ° Ğ²Ğ°Ñ€ĞµĞ½Ğ°Ñ�", "type": "protein", "percent": 25},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ", "type": "vegetable", "percent": 10},
            {"name": "Ğ³Ğ¾Ñ€Ğ¾ÑˆĞµĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 10}
        ],
        "keywords": ["Ğ¾Ğ»Ğ¸Ğ²ÑŒĞµ", "olivier", "Ñ�Ğ°Ğ»Ğ°Ñ‚", "salad", "Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ğ²Ğ¸Ğ½ĞµĞ³Ñ€ĞµÑ‚": {
        "name": "Ğ’Ğ¸Ğ½ĞµĞ³Ñ€ĞµÑ‚",
        "name_en": ["vinegret", "russian beet salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 90, "protein": 2.0, "fat": 4.5, "carbs": 10.5},
        "ingredients": [
            {"name": "Ñ�Ğ²ĞµĞºĞ»Ğ°", "type": "vegetable", "percent": 30},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 25},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 20},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ¿Ğ¾Ğ´Ñ�Ğ¾Ğ»Ğ½ĞµÑ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ²Ğ¸Ğ½ĞµĞ³Ñ€ĞµÑ‚", "vinegret", "Ñ�Ğ°Ğ»Ğ°Ñ‚", "salad", "Ñ�Ğ²ĞµĞºĞ»Ğ°"]
    },
    "Ñ�ĞµĞ»ĞµĞ´ĞºĞ° Ğ¿Ğ¾Ğ´ ÑˆÑƒĞ±Ğ¾Ğ¹": {
        "name": "Ğ¡ĞµĞ»ĞµĞ´ĞºĞ° Ğ¿Ğ¾Ğ´ ÑˆÑƒĞ±Ğ¾Ğ¹",
        "name_en": ["herring under fur coat", "russian herring salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 8.0, "fat": 14.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ñ�ĞµĞ»ÑŒĞ´ÑŒ Ñ�Ğ¾Ğ»ĞµĞ½Ğ°Ñ�", "type": "protein", "percent": 20},
            {"name": "Ñ�Ğ²ĞµĞºĞ»Ğ°", "type": "vegetable", "percent": 30},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 25},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 5}
        ],
        "keywords": ["ÑˆÑƒĞ±Ğ°", "Ñ�ĞµĞ»ĞµĞ´ĞºĞ°", "herring", "Ñ�Ğ°Ğ»Ğ°Ñ‚", "salad"]
    },
    # ==================== Ğ’Ğ¢Ğ�Ğ Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� ====================
    "Ğ¿Ğ»Ğ¾Ğ²": {
        "name": "ĞŸĞ»Ğ¾Ğ²",
        "name_en": ["pilaf", "pilau", "rice with meat"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 10.0, "carbs": 19.0},
        "ingredients": [
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 40},
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¿Ğ»Ğ¾Ğ²", "Ñ€Ğ¸Ñ�", "pilaf", "rice", "meat"]
    },
    "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹": {
        "name": "ĞšĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹",
        "name_en": ["cutlets", "meat patties", "meatballs"],
        "category": "main",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 240, "protein": 16.0, "fat": 18.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 80},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ…Ğ»ĞµĞ±", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹", "cutlets", "patties", "meatballs", "Ñ„Ğ°Ñ€Ñˆ"]
    },
    "Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸": {
        "name": "ĞŸĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸",
        "name_en": ["pelmeni", "dumplings", "russian dumplings"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 10.0, "fat": 9.0, "carbs": 22.0},
        "ingredients": [
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 40},
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 50},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸", "dumplings", "pelmeni"]
    },
    "Ğ²Ğ°Ñ€ĞµĞ½Ğ¸ĞºĞ¸": {
        "name": "Ğ’Ğ°Ñ€ĞµĞ½Ğ¸ĞºĞ¸",
        "name_en": ["vareniki", "dumplings with filling"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 6.0, "fat": 5.0, "carbs": 28.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 60},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 25},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ²Ğ°Ñ€ĞµĞ½Ğ¸ĞºĞ¸", "vareniki", "dumplings", "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ"]
    },
    "Ğ³Ğ¾Ğ»ÑƒĞ±Ñ†Ñ‹": {
        "name": "Ğ“Ğ¾Ğ»ÑƒĞ±Ñ†Ñ‹",
        "name_en": ["golubtsy", "cabbage rolls", "stuffed cabbage"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 10.0, "fat": 8.0, "carbs": 10.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "type": "vegetable", "percent": 40},
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 30},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5}
        ],
        "keywords": ["Ğ³Ğ¾Ğ»ÑƒĞ±Ñ†Ñ‹", "golubtsy", "cabbage", "rolls"]
    },
    "Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€ĞµÑ†": {
        "name": "ĞŸĞµÑ€ĞµÑ† Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹",
        "name_en": ["stuffed peppers", "bell peppers with meat"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 140, "protein": 9.0, "fat": 7.0, "carbs": 12.0},
        "ingredients": [
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹", "type": "vegetable", "percent": 40},
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 30},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5}
        ],
        "keywords": ["Ğ¿ĞµÑ€ĞµÑ†", "Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹", "stuffed", "peppers"]
    },
    "Ğ¼Ñ�Ñ�Ğ¾ Ğ¿Ğ¾-Ñ„Ñ€Ğ°Ğ½Ñ†ÑƒĞ·Ñ�ĞºĞ¸": {
        "name": "ĞœÑ�Ñ�Ğ¾ Ğ¿Ğ¾-Ñ„Ñ€Ğ°Ğ½Ñ†ÑƒĞ·Ñ�ĞºĞ¸",
        "name_en": ["french meat", "meat french style"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 250, "protein": 16.0, "fat": 18.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 45},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 15},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 10}
        ],
        "keywords": ["Ğ¼Ñ�Ñ�Ğ¾", "meat", "Ñ„Ñ€Ğ°Ğ½Ñ†ÑƒĞ·Ñ�ĞºĞ¸", "french"]
    },
    "Ğ³Ñ€ĞµÑ‡ĞºĞ° Ñ� Ğ¼Ñ�Ñ�Ğ¾Ğ¼": {
        "name": "Ğ“Ñ€ĞµÑ‡ĞºĞ° Ñ� Ğ¼Ñ�Ñ�Ğ¾Ğ¼",
        "name_en": ["buckwheat with meat", "meat with buckwheat"],
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 10.0, "fat": 6.0, "carbs": 16.0},
        "ingredients": [
            {"name": "Ğ³Ñ€ĞµÑ‡ĞºĞ°", "type": "carb", "percent": 50},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ³Ñ€ĞµÑ‡ĞºĞ°", "Ğ¼Ñ�Ñ�Ğ¾", "buckwheat", "meat"]
    },
    # ==================== ĞŸĞ�Ğ¡Ğ¢Ğ� ====================
    "Ğ¿Ğ°Ñ�Ñ‚Ğ° ĞºĞ°Ñ€Ğ±Ğ¾Ğ½Ğ°Ñ€Ğ°": {
        "name": "ĞŸĞ°Ñ�Ñ‚Ğ° ĞšĞ°Ñ€Ğ±Ğ¾Ğ½Ğ°Ñ€Ğ°",
        "name_en": ["pasta carbonara", "carbonara", "spaghetti carbonara"],
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 280, "protein": 14.0, "fat": 16.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸", "type": "carb", "percent": 45},
            {"name": "Ğ±ĞµĞºĞ¾Ğ½", "type": "protein", "percent": 20},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 15},
            {"name": "Ğ¿Ğ°Ñ€Ğ¼ĞµĞ·Ğ°Ğ½", "type": "dairy", "percent": 10},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 10}
        ],
        "keywords": ["ĞºĞ°Ñ€Ğ±Ğ¾Ğ½Ğ°Ñ€Ğ°", "carbonara", "Ğ¿Ğ°Ñ�Ñ‚Ğ°", "pasta", "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸"]
    },
    "Ğ¿Ğ°Ñ�Ñ‚Ğ° Ğ±Ğ¾Ğ»Ğ¾Ğ½ÑŒĞµĞ·Ğµ": {
        "name": "ĞŸĞ°Ñ�Ñ‚Ğ° Ğ‘Ğ¾Ğ»Ğ¾Ğ½ÑŒĞµĞ·Ğµ",
        "name_en": ["pasta bolognese", "bolognese", "spaghetti bolognese"],
        "category": "pasta",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸", "type": "carb", "percent": 40},
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 25},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ğ±Ğ¾Ğ»Ğ¾Ğ½ÑŒĞµĞ·Ğµ", "bolognese", "Ğ¿Ğ°Ñ�Ñ‚Ğ°", "pasta", "Ñ„Ğ°Ñ€Ñˆ"]
    },
    "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ğ¿Ğ¾-Ñ„Ğ»Ğ¾Ñ‚Ñ�ĞºĞ¸": {
        "name": "ĞœĞ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ğ¿Ğ¾-Ñ„Ğ»Ğ¾Ñ‚Ñ�ĞºĞ¸",
        "name_en": ["navy-style pasta", "macaroni with minced meat"],
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 10.0, "carbs": 19.0},
        "ingredients": [
            {"name": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹", "type": "carb", "percent": 50},
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 35},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹", "Ñ„Ğ»Ğ¾Ñ‚Ñ�ĞºĞ¸", "navy", "pasta", "Ñ„Ğ°Ñ€Ñˆ"]
    },
    # ==================== Ğ—Ğ�Ğ’Ğ¢Ğ Ğ�ĞšĞ˜ ====================
    "Ğ¾Ğ¼Ğ»ĞµÑ‚": {
        "name": "Ğ�Ğ¼Ğ»ĞµÑ‚",
        "name_en": ["omelette", "omelet", "scrambled eggs"],
        "category": "breakfast",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 150, "protein": 9.0, "fat": 11.0, "carbs": 2.5},
        "ingredients": [
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 60},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 35},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¾Ğ¼Ğ»ĞµÑ‚", "omelette", "omelet", "Ñ�Ğ¹Ñ†Ğ°", "eggs"]
    },
    "Ñ�Ğ¸Ñ‡Ğ½Ğ¸Ñ†Ğ°": {
        "name": "Ğ¯Ğ¸Ñ‡Ğ½Ğ¸Ñ†Ğ° Ğ³Ğ»Ğ°Ğ·ÑƒĞ½ÑŒÑ�",
        "name_en": ["fried eggs", "sunny side up", "egg fry"],
        "category": "breakfast",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 190, "protein": 13.0, "fat": 15.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 90},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 10}
        ],
        "keywords": ["Ñ�Ğ¸Ñ‡Ğ½Ğ¸Ñ†Ğ°", "Ñ�Ğ¹Ñ†Ğ°", "fried", "eggs", "Ğ³Ğ»Ğ°Ğ·ÑƒĞ½ÑŒÑ�"]
    },
    "Ñ�Ñ‹Ñ€Ğ½Ğ¸ĞºĞ¸": {
        "name": "Ğ¡Ñ‹Ñ€Ğ½Ğ¸ĞºĞ¸",
        "name_en": ["syrniki", "cottage cheese pancakes", "quark pancakes"],
        "category": "breakfast",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 210, "protein": 14.0, "fat": 9.0, "carbs": 19.0},
        "ingredients": [
            {"name": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "type": "dairy", "percent": 70},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 15},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ñ�Ñ‹Ñ€Ğ½Ğ¸ĞºĞ¸", "syrniki", "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "cottage cheese"]
    },
    "ĞºĞ°ÑˆĞ° Ğ¾Ğ²Ñ�Ñ�Ğ½Ğ°Ñ�": {
        "name": "Ğ�Ğ²Ñ�Ñ�Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ°",
        "name_en": ["oatmeal", "oat porridge", "oats"],
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 90, "protein": 3.5, "fat": 2.5, "carbs": 14.0},
        "ingredients": [
            {"name": "Ğ¾Ğ²Ñ�Ñ�Ğ½Ñ‹Ğµ Ñ…Ğ»Ğ¾Ğ¿ÑŒÑ�", "type": "carb", "percent": 30},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 65},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5}
        ],
        "keywords": ["Ğ¾Ğ²Ñ�Ñ�Ğ½ĞºĞ°", "ĞºĞ°ÑˆĞ°", "oatmeal", "oats", "porridge"]
    },
    "Ğ±Ğ»Ğ¸Ğ½Ñ‹": {
        "name": "Ğ‘Ğ»Ğ¸Ğ½Ñ‹",
        "name_en": ["blini", "russian pancakes", "crepes"],
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 6.0, "fat": 8.0, "carbs": 32.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 40},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 35},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5}
        ],
        "keywords": ["Ğ±Ğ»Ğ¸Ğ½Ñ‹", "blini", "pancakes", "Ğ±Ğ»Ğ¸Ğ½Ñ‡Ğ¸ĞºĞ¸", "crepes"]
    },
    "Ğ´Ñ€Ğ°Ğ½Ğ¸ĞºĞ¸": {
        "name": "Ğ”Ñ€Ğ°Ğ½Ğ¸ĞºĞ¸",
        "name_en": ["dranniki", "potato pancakes", "latkes"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 4.0, "fat": 10.0, "carbs": 28.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 70},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 8},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 7},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ´Ñ€Ğ°Ğ½Ğ¸ĞºĞ¸", "dranniki", "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "Ğ¾Ğ»Ğ°Ğ´ÑŒĞ¸", "potato pancakes"]
    },
    "Ğ·Ğ°Ğ¿ĞµĞºĞ°Ğ½ĞºĞ° Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ¶Ğ½Ğ°Ñ�": {
        "name": "Ğ—Ğ°Ğ¿ĞµĞºĞ°Ğ½ĞºĞ° Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ¶Ğ½Ğ°Ñ�",
        "name_en": ["cottage cheese casserole", "cheesecake bake"],
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 14.0, "fat": 6.0, "carbs": 16.0},
        "ingredients": [
            {"name": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "type": "dairy", "percent": 60},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 10},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 10},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 5}
        ],
        "keywords": ["Ğ·Ğ°Ğ¿ĞµĞºĞ°Ğ½ĞºĞ°", "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ¶Ğ½Ğ°Ñ�", "casserole", "cottage cheese"]
    },
    "Ğ±ĞµÑ„Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ°Ğ½Ğ¾Ğ²": {
        "name": "Ğ‘ĞµÑ„Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ°Ğ½Ğ¾Ğ²",
        "name_en": ["beef stroganoff", "stroganoff"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 230, "protein": 18.0, "fat": 14.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 50},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ğ³Ğ¾Ñ€Ñ‡Ğ¸Ñ†Ğ°", "type": "sauce", "percent": 5}
        ],
        "keywords": ["Ğ±ĞµÑ„Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ°Ğ½Ğ¾Ğ²", "beef stroganoff", "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°"]
    },
    "Ğ³ÑƒĞ»Ñ�Ñˆ": {
        "name": "Ğ“ÑƒĞ»Ñ�Ñˆ",
        "name_en": ["goulash", "hungarian goulash"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 15.0, "fat": 10.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 45},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 10},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ğ³ÑƒĞ»Ñ�Ñˆ", "goulash", "Ğ¼Ñ�Ñ�Ğ¾", "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚"]
    },
    "Ğ¾Ğ²Ğ¾Ñ‰Ğ½Ğ¾Ğµ Ñ€Ğ°Ğ³Ñƒ": {
        "name": "Ğ�Ğ²Ğ¾Ñ‰Ğ½Ğ¾Ğµ Ñ€Ğ°Ğ³Ñƒ",
        "name_en": ["vegetable stew", "ratatouille", "mixed vegetables"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 65, "protein": 2.5, "fat": 3.0, "carbs": 8.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ±Ğ°Ñ‡Ğ¾Ğº", "type": "vegetable", "percent": 25},
            {"name": "Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½", "type": "vegetable", "percent": 20},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€", "type": "vegetable", "percent": 20},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["Ñ€Ğ°Ğ³Ñƒ", "Ğ¾Ğ²Ğ¾Ñ‰Ğ½Ğ¾Ğµ", "vegetable stew", "Ğ¾Ğ²Ğ¾Ñ‰Ğ¸", "Ñ‚ÑƒÑˆĞµĞ½Ñ‹Ğµ"]
    },
    "Ğ¿Ğ»Ğ¾Ğ² Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹": {
        "name": "ĞŸĞ»Ğ¾Ğ² Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
        "name_en": ["pilaf with chicken", "chicken pilaf"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 12.0, "fat": 7.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 40},
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 30},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 7}
        ],
        "keywords": ["Ğ¿Ğ»Ğ¾Ğ²", "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "pilaf", "Ñ€Ğ¸Ñ�", "Ğ¼Ñ�Ñ�Ğ¾"]
    },
    "Ñ‚ĞµÑ„Ñ‚ĞµĞ»Ğ¸": {
        "name": "Ğ¢ĞµÑ„Ñ‚ĞµĞ»Ğ¸",
        "name_en": ["meatballs", "meatballs in sauce"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 200, "protein": 14.0, "fat": 12.0, "carbs": 10.0},
        "ingredients": [
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 50},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 10},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 5}
        ],
        "keywords": ["Ñ‚ĞµÑ„Ñ‚ĞµĞ»Ğ¸", "meatballs", "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹", "Ñ„Ğ°Ñ€Ñˆ"]
    },
    "Ğ¿ĞµÑ€ĞµÑ† Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹": {
        "name": "ĞŸĞµÑ€ĞµÑ† Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹",
        "name_en": ["stuffed peppers", "filled peppers"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 150, "protein": 10.0, "fat": 6.0, "carbs": 14.0},
        "ingredients": [
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹", "type": "vegetable", "percent": 35},
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 30},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 7},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ğ¿ĞµÑ€ĞµÑ†", "Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹", "stuffed peppers", "Ğ³Ğ¾Ğ»ÑƒĞ±Ñ†Ñ‹"]
    },
    "Ğ»Ğ°Ğ³Ğ¼Ğ°Ğ½": {
        "name": "Ğ›Ğ°Ğ¿ÑˆĞ° Ğ»Ğ°Ğ³Ğ¼Ğ°Ğ½",
        "name_en": ["lagman", "uzbek noodles", "hand-pulled noodles"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 160, "protein": 10.0, "fat": 6.0, "carbs": 18.0},
        "ingredients": [
            {"name": "Ğ»Ğ°Ğ¿ÑˆĞ°", "type": "carb", "percent": 35},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 25},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 12},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8}
        ],
        "keywords": ["Ğ»Ğ°Ğ³Ğ¼Ğ°Ğ½", "lagman", "Ğ»Ğ°Ğ¿ÑˆĞ°", "ÑƒĞ·Ğ±ĞµĞºÑ�ĞºĞ¸Ğ¹", "noodles"]
    },
    "ÑˆÑƒÑ€Ğ¿Ğ°": {
        "name": "Ğ¨ÑƒÑ€Ğ¿Ğ°",
        "name_en": ["shurpa", "uzbek soup", "meat soup"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 85, "protein": 8.0, "fat": 4.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 25},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 12},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 17}
        ],
        "keywords": ["ÑˆÑƒÑ€Ğ¿Ğ°", "shurpa", "Ñ�ÑƒĞ¿", "ÑƒĞ·Ğ±ĞµĞºÑ�ĞºĞ¸Ğ¹", "Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹"]
    },
    "Ğ¼Ğ°Ğ½Ñ‚Ñ‹": {
        "name": "ĞœĞ°Ğ½Ñ‚Ñ‹",
        "name_en": ["manti", "steamed dumplings", "uzbek dumplings"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 200, "protein": 12.0, "fat": 9.0, "carbs": 18.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 30},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5}
        ],
        "keywords": ["Ğ¼Ğ°Ğ½Ñ‚Ñ‹", "manti", "Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸", "dumplings", "ÑƒĞ·Ğ±ĞµĞºÑ�ĞºĞ¸Ğ¹"]
    },
    "Ñ‡ĞµĞ±ÑƒÑ€ĞµĞºĞ¸": {
        "name": "Ğ§ĞµĞ±ÑƒÑ€ĞµĞºĞ¸",
        "name_en": ["cheburek", "fried dough with meat", "crimean pastry"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 280, "protein": 10.0, "fat": 16.0, "carbs": 26.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 40},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 12},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 13},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ñ‡ĞµĞ±ÑƒÑ€ĞµĞºĞ¸", "cheburek", "Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹", "Ğ¿Ğ¸Ñ€Ğ¾Ğ¶Ğ¾Ğº", "Ğ¼Ñ�Ñ�Ğ¾"]
    },
    "Ğ±ĞµĞ»Ñ�ÑˆĞ¸": {
        "name": "Ğ‘ĞµĞ»Ñ�ÑˆĞ¸",
        "name_en": ["belyashi", "meat pies", "fried buns"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 260, "protein": 11.0, "fat": 14.0, "carbs": 24.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 35},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 12},
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶Ğ¸", "type": "other", "percent": 3},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ğ±ĞµĞ»Ñ�ÑˆĞ¸", "belyashi", "Ğ¿Ğ¸Ñ€Ğ¾Ğ¶ĞºĞ¸", "Ğ¼Ñ�Ñ�Ğ¾", "Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğµ"]
    },
    "Ğ¿Ğ¸Ñ€Ğ¾Ğ¶ĞºĞ¸ Ğ¿ĞµÑ‡ĞµĞ½Ñ‹Ğµ": {
        "name": "ĞŸĞ¸Ñ€Ğ¾Ğ¶ĞºĞ¸ Ğ¿ĞµÑ‡ĞµĞ½Ñ‹Ğµ",
        "name_en": ["baked pies", "pirozhki"],
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 6.0, "fat": 8.0, "carbs": 32.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 50},
            {"name": "Ğ¼Ñ�Ñ�Ğ¾", "type": "protein", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶Ğ¸", "type": "other", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ğ¿Ğ¸Ñ€Ğ¾Ğ¶ĞºĞ¸", "pirozhki", "Ğ²Ñ‹Ğ¿ĞµÑ‡ĞºĞ°", "Ğ¿ĞµÑ‡ĞµĞ½Ñ‹Ğµ", "Ğ¿Ğ¸Ñ€Ğ¾Ğ³"]
    },
    # ==================== Ğ¤Ğ�Ğ¡Ğ¢Ğ¤Ğ£Ğ” ====================
    "Ğ³Ğ°Ğ¼Ğ±ÑƒÑ€Ğ³ĞµÑ€": {
        "name": "Ğ“Ğ°Ğ¼Ğ±ÑƒÑ€Ğ³ĞµÑ€",
        "name_en": ["hamburger", "burger", "cheeseburger"],
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 250, "protein": 12.0, "fat": 10.0, "carbs": 28.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ° Ğ´Ğ»Ñ� Ğ±ÑƒÑ€Ğ³ĞµÑ€Ğ°", "type": "carb", "percent": 35},
            {"name": "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ° Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ�", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "ĞºĞµÑ‚Ñ‡ÑƒĞ¿", "type": "sauce", "percent": 5},
            {"name": "Ğ³Ğ¾Ñ€Ñ‡Ğ¸Ñ†Ğ°", "type": "sauce", "percent": 5}
        ],
        "keywords": ["Ğ±ÑƒÑ€Ğ³ĞµÑ€", "Ğ³Ğ°Ğ¼Ğ±ÑƒÑ€Ğ³ĞµÑ€", "burger", "hamburger"]
    },
    "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°": {
        "name": "ĞŸĞ¸Ñ†Ñ†Ğ° ĞœĞ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°",
        "name_en": ["pizza margherita", "margherita pizza", "pizza"],
        "category": "bakery",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 240, "protein": 10.0, "fat": 9.0, "carbs": 30.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ğ»Ñ� Ğ¿Ğ¸Ñ†Ñ†Ñ‹", "type": "carb", "percent": 50},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹", "type": "sauce", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 25},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["Ğ¿Ğ¸Ñ†Ñ†Ğ°", "pizza", "Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°", "margherita"]
    },
    "ÑˆĞ°ÑƒÑ€Ğ¼Ğ°": {
        "name": "Ğ¨Ğ°ÑƒÑ€Ğ¼Ğ° Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
        "name_en": ["shawarma", "doner kebab", "gyro"],
        "category": "fastfood",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 10.0, "fat": 7.0, "carbs": 19.0},
        "ingredients": [
            {"name": "Ğ»Ğ°Ğ²Ğ°Ñˆ", "type": "carb", "percent": 30},
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ³Ñ€Ğ¸Ğ»ÑŒ", "type": "protein", "percent": 25},
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "type": "vegetable", "percent": 15},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 8},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 4}
        ],
        "keywords": ["ÑˆĞ°ÑƒÑ€Ğ¼Ğ°", "shawarma", "doner", "kebab", "Ğ»Ğ°Ğ²Ğ°Ñˆ"]
    },
    # ==================== Ğ�Ğ—Ğ˜Ğ�Ğ¢Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "Ñ€Ğ¾Ğ»Ğ» Ñ„Ğ¸Ğ»Ğ°Ğ´ĞµĞ»ÑŒÑ„Ğ¸Ñ�": {
        "name": "Ğ Ğ¾Ğ»Ğ» Ğ¤Ğ¸Ğ»Ğ°Ğ´ĞµĞ»ÑŒÑ„Ğ¸Ñ�",
        "name_en": ["philadelphia roll", "philly roll", "salmon roll"],
        "category": "asian",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 7.0, "fat": 8.0, "carbs": 23.0},
        "ingredients": [
            {"name": "Ñ€Ğ¸Ñ� Ğ´Ğ»Ñ� Ñ�ÑƒÑˆĞ¸", "type": "carb", "percent": 50},
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "type": "protein", "percent": 20},
            {"name": "Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 15},
            {"name": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†", "type": "vegetable", "percent": 10},
            {"name": "Ğ½Ğ¾Ñ€Ğ¸", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ñ€Ğ¾Ğ»Ğ»", "Ñ�ÑƒÑˆĞ¸", "roll", "sushi", "Ñ„Ğ¸Ğ»Ğ°Ğ´ĞµĞ»ÑŒÑ„Ğ¸Ñ�", "philadelphia"]
    },
    "Ñ�ÑƒÑˆĞ¸": {
        "name": "Ğ¡ÑƒÑˆĞ¸ Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼",
        "name_en": ["sushi", "sushi with salmon", "nigiri"],
        "category": "asian",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 4.0, "carbs": 28.0},
        "ingredients": [
            {"name": "Ñ€Ğ¸Ñ� Ğ´Ğ»Ñ� Ñ�ÑƒÑˆĞ¸", "type": "carb", "percent": 70},
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "type": "protein", "percent": 25},
            {"name": "Ğ½Ğ¾Ñ€Ğ¸", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ñ�ÑƒÑˆĞ¸", "sushi", "Ñ€Ğ¾Ğ»Ğ»", "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "salmon"]
    },
    "Ñ€Ğ°Ğ¼ĞµĞ½": {
        "name": "Ğ Ğ°Ğ¼ĞµĞ½ Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
        "name_en": ["ramen", "chicken ramen", "japanese noodle soup"],
        "category": "asian",
        "default_weight": 500,
        "nutrition_per_100": {"calories": 90, "protein": 5.0, "fat": 3.0, "carbs": 11.0},
        "ingredients": [
            {"name": "Ğ»Ğ°Ğ¿ÑˆĞ° Ñ€Ğ°Ğ¼ĞµĞ½", "type": "carb", "percent": 30},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½ ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹", "type": "liquid", "percent": 50},
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 3},
            {"name": "ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚", "type": "vegetable", "percent": 3},
            {"name": "Ğ»ÑƒĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 2},
            {"name": "Ğ½Ğ¾Ñ€Ğ¸", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["Ñ€Ğ°Ğ¼ĞµĞ½", "ramen", "Ğ»Ğ°Ğ¿ÑˆĞ°", "noodle", "Ñ�ÑƒĞ¿"]
    },
    # ==================== Ğ“Ğ�Ğ Ğ�Ğ˜Ğ Ğ« ====================
    "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ": {
        "name": "ĞšĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ",
        "name_en": ["mashed potatoes", "potato puree"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 105, "protein": 2.5, "fat": 3.5, "carbs": 16.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 80},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¿Ñ�Ñ€Ğµ", "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "mashed", "potatoes", "puree"]
    },
    "Ñ€Ğ¸Ñ� Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ¾Ğ¹": {
        "name": "Ğ Ğ¸Ñ� Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ¾Ğ¹",
        "name_en": ["boiled rice", "white rice", "steamed rice"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 130, "protein": 2.5, "fat": 0.5, "carbs": 29.0},
        "ingredients": [
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 100}
        ],
        "keywords": ["Ñ€Ğ¸Ñ�", "rice", "Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ¾Ğ¹", "boiled", "steamed"]
    },
    "Ğ³Ñ€ĞµÑ‡ĞºĞ° Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ°Ñ�": {
        "name": "Ğ“Ñ€ĞµÑ‡ĞºĞ° Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ°Ñ�",
        "name_en": ["buckwheat", "buckwheat porridge", "kasha"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 110, "protein": 4.0, "fat": 1.0, "carbs": 21.0},
        "ingredients": [
            {"name": "Ğ³Ñ€ĞµÑ‡ĞºĞ°", "type": "carb", "percent": 100}
        ],
        "keywords": ["Ğ³Ñ€ĞµÑ‡ĞºĞ°", "Ğ³Ñ€ĞµÑ‡Ğ½ĞµĞ²Ğ°Ñ�", "buckwheat", "kasha", "ĞºĞ°ÑˆĞ°"]
    },
    "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹": {
        "name": "ĞšĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹",
        "name_en": ["fried potatoes", "home fries", "pan-fried potatoes"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 190, "protein": 3.0, "fat": 9.0, "carbs": 24.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 85},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 15}
        ],
        "keywords": ["ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹", "fried", "potatoes"]
    },
    "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ñ„Ñ€Ğ¸": {
        "name": "ĞšĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ñ„Ñ€Ğ¸",
        "name_en": ["french fries", "fries", "chips"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 290, "protein": 3.5, "fat": 15.0, "carbs": 34.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 70},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 30}
        ],
        "keywords": ["Ñ„Ñ€Ğ¸", "fries", "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "potatoes", "chips"]
    },

        # ==================== Ğ“Ğ Ğ£Ğ—Ğ˜Ğ�Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸ Ğ¿Ğ¾-Ğ°Ğ´Ğ¶Ğ°Ñ€Ñ�ĞºĞ¸": {
        "name": "Ğ¥Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸ Ğ¿Ğ¾-Ğ°Ğ´Ğ¶Ğ°Ñ€Ñ�ĞºĞ¸",
        "name_en": ["Adjarian khachapuri", "Georgian cheese bread boat"],
        "category": "bakery",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 280, "protein": 10.0, "fat": 14.0, "carbs": 28.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ñ€Ğ¾Ğ¶Ğ¶ĞµĞ²Ğ¾Ğµ", "type": "carb", "percent": 50},
            {"name": "Ñ�Ñ‹Ñ€ Ñ�ÑƒĞ»ÑƒĞ³ÑƒĞ½Ğ¸", "type": "dairy", "percent": 30},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10}
        ],
        "keywords": ["Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸", "khachapuri", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "Ñ�Ñ‹Ñ€", "Ğ»Ğ¾Ğ´Ğ¾Ñ‡ĞºĞ°"]
    },
    "Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸ Ğ¿Ğ¾-Ğ¸Ğ¼ĞµÑ€ĞµÑ‚Ğ¸Ğ½Ñ�ĞºĞ¸": {
        "name": "Ğ¥Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸ Ğ¿Ğ¾-Ğ¸Ğ¼ĞµÑ€ĞµÑ‚Ğ¸Ğ½Ñ�ĞºĞ¸",
        "name_en": ["Imeretian khachapuri", "Georgian cheese flatbread"],
        "category": "bakery",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 260, "protein": 9.0, "fat": 11.0, "carbs": 31.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ñ€Ğ¾Ğ¶Ğ¶ĞµĞ²Ğ¾Ğµ", "type": "carb", "percent": 55},
            {"name": "Ñ�Ñ‹Ñ€ Ğ¸Ğ¼ĞµÑ€ĞµÑ‚Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "type": "dairy", "percent": 40},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸", "Ğ¸Ğ¼ĞµÑ€ĞµÑ‚Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "Ñ�Ñ‹Ñ€Ğ½Ğ°Ñ� Ğ»ĞµĞ¿ĞµÑˆĞºĞ°"]
    },
    "Ñ…Ğ¸Ğ½ĞºĞ°Ğ»Ğ¸": {
        "name": "Ğ¥Ğ¸Ğ½ĞºĞ°Ğ»Ğ¸",
        "name_en": ["khinkali", "Georgian dumplings"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 45},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ñ…Ğ¸Ğ½ĞºĞ°Ğ»Ğ¸", "khinkali", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¸Ğµ Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸"]
    },
    "Ñ…Ğ¸Ğ½ĞºĞ°Ğ»Ğ¸ Ñ� Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ¾Ğ¹": {
        "name": "Ğ¥Ğ¸Ğ½ĞºĞ°Ğ»Ğ¸ Ñ� Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ¾Ğ¹",
        "name_en": ["lamb khinkali", "Georgian lamb dumplings"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 230, "protein": 13.0, "fat": 12.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 45},
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 40},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "ĞºĞ¸Ğ½Ğ·Ğ°", "type": "vegetable", "percent": 2},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ñ…Ğ¸Ğ½ĞºĞ°Ğ»Ğ¸", "khinkali", "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "lamb"]
    },
    "Ñ‡Ğ°Ñ…Ğ¾Ñ…Ğ±Ğ¸Ğ»Ğ¸": {
        "name": "Ğ§Ğ°Ñ…Ğ¾Ñ…Ğ±Ğ¸Ğ»Ğ¸",
        "name_en": ["chakhokhbili", "Georgian chicken stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 140, "protein": 15.0, "fat": 7.0, "carbs": 5.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 45},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 25},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 8},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "ĞºĞ¸Ğ½Ğ·Ğ°", "type": "vegetable", "percent": 4}
        ],
        "keywords": ["Ñ‡Ğ°Ñ…Ğ¾Ñ…Ğ±Ğ¸Ğ»Ğ¸", "chakhokhbili", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "ĞºÑƒÑ€Ğ¸Ñ†Ğ°"]
    },
    "Ğ¾Ğ´Ğ¶Ğ°ĞºÑ…ÑƒÑ€Ğ¸": {
        "name": "Ğ�Ğ´Ğ¶Ğ°ĞºÑ…ÑƒÑ€Ğ¸",
        "name_en": ["ojakhuri", "Georgian pork and potatoes"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 200, "protein": 12.0, "fat": 12.0, "carbs": 12.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 35},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 40},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ğ¾Ğ´Ğ¶Ğ°ĞºÑ…ÑƒÑ€Ğ¸", "ojakhuri", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ° Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾ÑˆĞºĞ¾Ğ¹"]
    },
    "Ğ»Ğ¾Ğ±Ğ¸Ğ¾": {
        "name": "Ğ›Ğ¾Ğ±Ğ¸Ğ¾",
        "name_en": ["lobio", "Georgian bean stew"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 6.0, "fat": 4.0, "carbs": 15.0},
        "ingredients": [
            {"name": "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ ĞºÑ€Ğ°Ñ�Ğ½Ğ°Ñ�", "type": "protein", "percent": 60},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğµ Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 10},
            {"name": "ĞºĞ¸Ğ½Ğ·Ğ°", "type": "vegetable", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ğ»Ğ¾Ğ±Ğ¸Ğ¾", "lobio", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ"]
    },
    "Ğ¿Ñ…Ğ°Ğ»Ğ¸": {
        "name": "ĞŸÑ…Ğ°Ğ»Ğ¸ Ğ¸Ğ· ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚Ğ°",
        "name_en": ["phali", "Georgian spinach pate"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 5.0, "fat": 10.0, "carbs": 7.0},
        "ingredients": [
            {"name": "ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚", "type": "vegetable", "percent": 50},
            {"name": "Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğµ Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "ĞºĞ¸Ğ½Ğ·Ğ°", "type": "vegetable", "percent": 5},
            {"name": "Ğ³Ñ€Ğ°Ğ½Ğ°Ñ‚Ğ¾Ğ²Ñ‹Ğµ Ğ·ĞµÑ€Ğ½Ğ°", "type": "fruit", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["Ğ¿Ñ…Ğ°Ğ»Ğ¸", "phali", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ°Ñ� Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°", "ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚"]
    },
    "Ñ�Ğ°Ñ†Ğ¸Ğ²Ğ¸": {
        "name": "Ğ¡Ğ°Ñ†Ğ¸Ğ²Ğ¸",
        "name_en": ["satsivi", "Georgian chicken in walnut sauce"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 250, "protein": 15.0, "fat": 19.0, "carbs": 6.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 40},
            {"name": "Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğµ Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5},
            {"name": "ÑƒĞºÑ�ÑƒÑ�", "type": "other", "percent": 5},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ñ�Ğ°Ñ†Ğ¸Ğ²Ğ¸", "satsivi", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "Ğ¾Ñ€ĞµÑ…Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�"]
    },
    "Ñ‡Ğ°ĞºĞ°Ğ¿ÑƒĞ»Ğ¸": {
        "name": "Ğ§Ğ°ĞºĞ°Ğ¿ÑƒĞ»Ğ¸",
        "name_en": ["chakapuli", "Georgian lamb stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 14.0, "fat": 10.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 40},
            {"name": "Ñ‰Ğ°Ğ²ĞµĞ»ÑŒ", "type": "vegetable", "percent": 15},
            {"name": "Ñ�Ñ�Ñ‚Ñ€Ğ°Ğ³Ğ¾Ğ½", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ±ĞµĞ»Ğ¾Ğµ Ğ²Ğ¸Ğ½Ğ¾", "type": "liquid", "percent": 15},
            {"name": "Ğ·ĞµĞ»ĞµĞ½ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ñ‡Ğ°ĞºĞ°Ğ¿ÑƒĞ»Ğ¸", "chakapuli", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°"]
    },
    "ĞºÑƒĞ¿Ğ°Ñ‚Ñ‹": {
        "name": "ĞšÑƒĞ¿Ğ°Ñ‚Ñ‹",
        "name_en": ["kupaty", "Georgian sausages", "grilled sausages"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 270, "protein": 15.0, "fat": 22.0, "carbs": 3.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 70},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 15},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["ĞºÑƒĞ¿Ğ°Ñ‚Ñ‹", "kupaty", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¸Ğµ ĞºĞ¾Ğ»Ğ±Ğ°Ñ�ĞºĞ¸"]
    },
    "Ğ°Ğ´Ğ¶Ğ°Ğ¿Ñ�Ğ°Ğ½Ğ´Ğ°Ğ»Ğ¸": {
        "name": "Ğ�Ğ´Ğ¶Ğ°Ğ¿Ñ�Ğ°Ğ½Ğ´Ğ°Ğ»Ğ¸",
        "name_en": ["ajapsandali", "Georgian vegetable stew"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 70, "protein": 2.0, "fat": 3.0, "carbs": 9.0},
        "ingredients": [
            {"name": "Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½Ñ‹", "type": "vegetable", "percent": 30},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 20},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "ĞºĞ¸Ğ½Ğ·Ğ°", "type": "vegetable", "percent": 5},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10}
        ],
        "keywords": ["Ğ°Ğ´Ğ¶Ğ°Ğ¿Ñ�Ğ°Ğ½Ğ´Ğ°Ğ»Ğ¸", "ajapsandali", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¾Ğµ Ğ¾Ğ²Ğ¾Ñ‰Ğ½Ğ¾Ğµ Ñ€Ğ°Ğ³Ñƒ"]
    },
    "Ñ‡Ğ°Ğ½Ğ°Ñ…Ğ¸": {
        "name": "Ğ§Ğ°Ğ½Ğ°Ñ…Ğ¸",
        "name_en": ["chanakhi", "Georgian lamb and vegetables"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 150, "protein": 9.0, "fat": 8.0, "carbs": 11.0},
        "ingredients": [
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 25},
            {"name": "Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½Ñ‹", "type": "vegetable", "percent": 15},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ğ·ĞµĞ»ĞµĞ½ÑŒ", "type": "vegetable", "percent": 7},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ñ‡Ğ°Ğ½Ğ°Ñ…Ğ¸", "chanakhi", "Ğ³Ñ€ÑƒĞ·Ğ¸Ğ½Ñ�ĞºĞ¾Ğµ Ñ€Ğ°Ğ³Ñƒ"]
    },

    # ==================== Ğ’Ğ•Ğ�Ğ“Ğ•Ğ Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "Ğ³ÑƒĞ»Ñ�Ñˆ": {
        "name": "Ğ“ÑƒĞ»Ñ�Ñˆ",
        "name_en": ["goulash", "hungarian goulash", "beef stew"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 110, "protein": 9.0, "fat": 5.0, "carbs": 7.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 8},
            {"name": "Ğ¿Ğ°Ğ¿Ñ€Ğ¸ĞºĞ°", "type": "spice", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°/Ğ±ÑƒĞ»ÑŒĞ¾Ğ½", "type": "liquid", "percent": 12}
        ],
        "keywords": ["Ğ³ÑƒĞ»Ñ�Ñˆ", "goulash", "Ğ²ĞµĞ½Ğ³ĞµÑ€Ñ�ĞºĞ¸Ğ¹ Ñ�ÑƒĞ¿"]
    },
    "Ğ¿ĞµÑ€ĞºĞµĞ»ÑŒÑ‚": {
        "name": "ĞŸĞµÑ€ĞºĞµĞ»ÑŒÑ‚",
        "name_en": ["pÃ¶rkÃ¶lt", "hungarian meat stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 18.0, "fat": 12.0, "carbs": 4.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°/Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 60},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 20},
            {"name": "Ğ¿Ğ°Ğ¿Ñ€Ğ¸ĞºĞ°", "type": "spice", "percent": 8},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 7}
        ],
        "keywords": ["Ğ¿ĞµÑ€ĞºĞµĞ»ÑŒÑ‚", "pÃ¶rkÃ¶lt", "Ğ²ĞµĞ½Ğ³ĞµÑ€Ñ�ĞºĞ¾Ğµ Ñ€Ğ°Ğ³Ñƒ"]
    },
    "Ğ¿Ğ°Ğ¿Ñ€Ğ¸ĞºĞ°Ñˆ": {
        "name": "ĞŸĞ°Ğ¿Ñ€Ğ¸ĞºĞ°Ñˆ",
        "name_en": ["paprikash", "hungarian chicken in paprika sauce"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 160, "protein": 15.0, "fat": 9.0, "carbs": 6.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 45},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¿Ğ°Ğ¿Ñ€Ğ¸ĞºĞ°", "type": "spice", "percent": 8},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 7},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¿Ğ°Ğ¿Ñ€Ğ¸ĞºĞ°Ñˆ", "paprikash", "Ğ²ĞµĞ½Ğ³ĞµÑ€Ñ�ĞºĞ¸Ğ¹", "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ"]
    },
    "Ğ»ĞµÑ‡Ğ¾": {
        "name": "Ğ›ĞµÑ‡Ğ¾",
        "name_en": ["lecho", "hungarian pepper stew"],
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 1.5, "fat": 2.0, "carbs": 6.5},
        "ingredients": [
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 50},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ¿Ğ°Ğ¿Ñ€Ğ¸ĞºĞ°", "type": "spice", "percent": 3},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 2}
        ],
        "keywords": ["Ğ»ĞµÑ‡Ğ¾", "lecho", "Ğ²ĞµĞ½Ğ³ĞµÑ€Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ñ‚Ğ¾ĞºĞ°Ğ½Ğ¸": {
        "name": "Ğ¢Ğ¾ĞºĞ°Ğ½Ğ¸",
        "name_en": ["tokÃ¡ny", "hungarian beef strips"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 17.0, "fat": 11.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 55},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 7},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ñ‚Ğ¾ĞºĞ°Ğ½Ğ¸", "tokÃ¡ny", "Ğ²ĞµĞ½Ğ³ĞµÑ€Ñ�ĞºĞ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾"]
    },

    # ==================== Ğ‘Ğ�Ğ›ĞšĞ�Ğ�Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "Ñ‡ĞµĞ²Ğ°Ğ¿Ñ‡Ğ¸Ñ‡Ğ¸": {
        "name": "Ğ§ĞµĞ²Ğ°Ğ¿Ñ‡Ğ¸Ñ‡Ğ¸",
        "name_en": ["Ä‡evapi", "chevapchichi", "balkan sausages"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 16.0, "fat": 19.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 50},
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 25},
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["Ñ‡ĞµĞ²Ğ°Ğ¿Ñ‡Ğ¸Ñ‡Ğ¸", "Ä‡evapi", "Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ¸Ğµ ĞºĞ¾Ğ»Ğ±Ğ°Ñ�ĞºĞ¸"]
    },
    "Ğ¿Ğ»ĞµÑ�ĞºĞ°Ğ²Ğ¸Ñ†Ğ°": {
        "name": "ĞŸĞ»ĞµÑ�ĞºĞ°Ğ²Ğ¸Ñ†Ğ°",
        "name_en": ["pljeskavica", "balkan burger"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 230, "protein": 15.0, "fat": 17.0, "carbs": 4.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 60},
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¿Ğ»ĞµÑ�ĞºĞ°Ğ²Ğ¸Ñ†Ğ°", "pljeskavica", "Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ°Ñ� ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ°"]
    },
    "ÑˆĞ¾Ğ¿Ñ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚": {
        "name": "Ğ¨Ğ¾Ğ¿Ñ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚",
        "name_en": ["shopska salad", "bulgarian salad"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 85, "protein": 2.5, "fat": 6.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 30},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹", "type": "vegetable", "percent": 25},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ñ‹Ñ€ Ñ�Ğ¸Ñ€ĞµĞ½Ğµ", "type": "dairy", "percent": 12},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ÑˆĞ¾Ğ¿Ñ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚", "shopska", "Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ğ¼ÑƒÑ�Ğ°ĞºĞ°": {
        "name": "ĞœÑƒÑ�Ğ°ĞºĞ° Ğ¿Ğ¾-Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ¸",
        "name_en": ["moussaka", "balkan moussaka"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 8.0, "carbs": 12.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 35},
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¾Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 25},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5},
            {"name": "Ğ¹Ğ¾Ğ³ÑƒÑ€Ñ‚", "type": "dairy", "percent": 7},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ğ¼ÑƒÑ�Ğ°ĞºĞ°", "moussaka", "Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ°Ñ� Ğ·Ğ°Ğ¿ĞµĞºĞ°Ğ½ĞºĞ°"]
    },
    "Ñ�Ğ°Ñ€Ğ¼Ğ°": {
        "name": "Ğ¡Ğ°Ñ€Ğ¼Ğ°",
        "name_en": ["sarma", "stuffed cabbage rolls"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 7.0, "carbs": 13.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° ĞºĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ�", "type": "vegetable", "percent": 40},
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¾Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 30},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "ĞºĞ¾Ğ¿Ñ‡ĞµĞ½Ğ¾Ñ�Ñ‚Ğ¸", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["Ñ�Ğ°Ñ€Ğ¼Ğ°", "sarma", "Ğ³Ğ¾Ğ»ÑƒĞ±Ñ†Ñ‹", "Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ¸Ğµ"]
    },
    "Ğ°Ğ¹Ğ²Ğ°Ñ€": {
        "name": "Ğ�Ğ¹Ğ²Ğ°Ñ€",
        "name_en": ["ajvar", "balkan pepper spread"],
        "category": "sauce",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 70, "protein": 1.5, "fat": 4.0, "carbs": 7.0},
        "ingredients": [
            {"name": "ĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 75},
            {"name": "Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½Ñ‹", "type": "vegetable", "percent": 15},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5},
            {"name": "ÑƒĞºÑ�ÑƒÑ�", "type": "other", "percent": 2}
        ],
        "keywords": ["Ğ°Ğ¹Ğ²Ğ°Ñ€", "ajvar", "Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ¸Ğ¹ Ñ�Ğ¾ÑƒÑ�"]
    },
    "ĞºĞ°Ğ¹Ğ¼Ğ°Ğº": {
        "name": "ĞšĞ°Ğ¹Ğ¼Ğ°Ğº",
        "name_en": ["kajmak", "balkan clotted cream"],
        "category": "dairy",
        "default_weight": 80,
        "nutrition_per_100": {"calories": 400, "protein": 5.0, "fat": 40.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 95},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 5}
        ],
        "keywords": ["ĞºĞ°Ğ¹Ğ¼Ğ°Ğº", "kajmak", "Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ¸Ğ¹ Ñ�Ñ‹Ñ€"]
    },
    "Ğ±ÑƒÑ€ĞµĞº": {
        "name": "Ğ‘ÑƒÑ€ĞµĞº",
        "name_en": ["burek", "balkan pie"],
        "category": "bakery",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 280, "protein": 9.0, "fat": 15.0, "carbs": 27.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ñ„Ğ¸Ğ»Ğ¾", "type": "carb", "percent": 50},
            {"name": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹", "type": "protein", "percent": 25},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 15}
        ],
        "keywords": ["Ğ±ÑƒÑ€ĞµĞº", "burek", "Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ¸Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³"]
    },
    "Ğ±ÑƒÑ€ĞµĞº Ñ� Ñ�Ñ‹Ñ€Ğ¾Ğ¼": {
        "name": "Ğ‘ÑƒÑ€ĞµĞº Ñ� Ñ�Ñ‹Ñ€Ğ¾Ğ¼",
        "name_en": ["cheese burek", "balkan cheese pie"],
        "category": "bakery",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 270, "protein": 10.0, "fat": 14.0, "carbs": 26.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ñ„Ğ¸Ğ»Ğ¾", "type": "carb", "percent": 50},
            {"name": "Ğ±Ñ€Ñ‹Ğ½Ğ·Ğ°", "type": "dairy", "percent": 30},
            {"name": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "type": "dairy", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ±ÑƒÑ€ĞµĞº", "burek", "Ñ�Ñ‹Ñ€Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³"]
    },
    "Ğ¿Ğ¾Ğ³Ğ°Ñ‡Ğ°": {
        "name": "ĞŸĞ¾Ğ³Ğ°Ñ‡Ğ°",
        "name_en": ["pogaÄ�a", "balkan bread"],
        "category": "bakery",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 260, "protein": 8.0, "fat": 5.0, "carbs": 45.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 70},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 20},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5},
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶Ğ¸", "type": "other", "percent": 3},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 2}
        ],
        "keywords": ["Ğ¿Ğ¾Ğ³Ğ°Ñ‡Ğ°", "pogaÄ�a", "Ğ±Ğ°Ğ»ĞºĞ°Ğ½Ñ�ĞºĞ¸Ğ¹ Ñ…Ğ»ĞµĞ±"]
    },

    # ==================== Ğ¡ĞšĞ�Ğ�Ğ”Ğ˜Ğ�Ğ�Ğ’Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "ÑˆĞ²ĞµĞ´Ñ�ĞºĞ¸Ğµ Ñ„Ñ€Ğ¸ĞºĞ°Ğ´ĞµĞ»ÑŒĞºĞ¸": {
        "name": "Ğ¨Ğ²ĞµĞ´Ñ�ĞºĞ¸Ğµ Ñ„Ñ€Ğ¸ĞºĞ°Ğ´ĞµĞ»ÑŒĞºĞ¸",
        "name_en": ["swedish meatballs", "kÃ¶ttbullar"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 250, "protein": 14.0, "fat": 18.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¾Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 40},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ…Ğ»ĞµĞ±Ğ½Ñ‹Ğµ ĞºÑ€Ğ¾ÑˆĞºĞ¸", "type": "carb", "percent": 8},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 7},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5}
        ],
        "keywords": ["ÑˆĞ²ĞµĞ´Ñ�ĞºĞ¸Ğµ Ñ„Ñ€Ğ¸ĞºĞ°Ğ´ĞµĞ»ÑŒĞºĞ¸", "swedish meatballs", "kÃ¶ttbullar"]
    },
    "Ğ³Ñ€Ğ°Ğ²Ğ»Ğ°ĞºÑ�": {
        "name": "Ğ“Ñ€Ğ°Ğ²Ğ»Ğ°ĞºÑ�",
        "name_en": ["gravlax", "cured salmon"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 22.0, "fat": 10.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "type": "protein", "percent": 85},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "ÑƒĞºÑ€Ğ¾Ğ¿", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ğ³Ñ€Ğ°Ğ²Ğ»Ğ°ĞºÑ�", "gravlax", "Ñ�ĞºĞ°Ğ½Ğ´Ğ¸Ğ½Ğ°Ğ²Ñ�ĞºĞ¸Ğ¹", "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ"]
    },
    "Ñ�Ğ¼Ñ‘Ñ€Ñ€ĞµĞ±Ñ€Ñ‘Ğ´": {
        "name": "Ğ¡Ğ¼Ñ‘Ñ€Ñ€ĞµĞ±Ñ€Ñ‘Ğ´",
        "name_en": ["smÃ¸rrebrÃ¸d", "danish open sandwich"],
        "category": "sandwich",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 9.0, "carbs": 17.0},
        "ingredients": [
            {"name": "Ñ€Ğ¶Ğ°Ğ½Ğ¾Ğ¹ Ñ…Ğ»ĞµĞ±", "type": "carb", "percent": 40},
            {"name": "Ñ�ĞµĞ»ÑŒĞ´ÑŒ", "type": "protein", "percent": 20},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ€ĞµĞ´Ğ¸Ñ�", "type": "vegetable", "percent": 7},
            {"name": "ÑƒĞºÑ€Ğ¾Ğ¿", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 10}
        ],
        "keywords": ["Ñ�Ğ¼Ñ‘Ñ€Ñ€ĞµĞ±Ñ€Ñ‘Ğ´", "smÃ¸rrebrÃ¸d", "Ğ´Ğ°Ñ‚Ñ�ĞºĞ¸Ğ¹ Ğ±ÑƒÑ‚ĞµÑ€Ğ±Ñ€Ğ¾Ğ´"]
    },
    "Ñ€Ğ°Ñ�Ñ‚ĞµĞ½Ğ¸Ğµ": {
        "name": "Ğ Ğ°Ñ�Ñ‚ĞµĞ½Ğ¸Ğµ (Ğ¶Ğ°Ñ€ĞºĞ¾Ğµ Ğ¸Ğ· Ğ¼Ñ�Ñ�Ğ° Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ĞµĞ¼)",
        "name_en": ["rastenie", "danish meatloaf with potatoes"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 160, "protein": 10.0, "fat": 7.0, "carbs": 14.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 35},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 40},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 15},
            {"name": "Ğ±ĞµĞºĞ¾Ğ½", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ñ€Ğ°Ñ�Ñ‚ĞµĞ½Ğ¸Ğµ", "rastenie", "Ğ´Ğ°Ñ‚Ñ�ĞºĞ¾Ğµ Ğ¶Ğ°Ñ€ĞºĞ¾Ğµ"]
    },
    "ĞºĞ»Ñ‘Ñ†ĞºĞ¸ Ñ� Ğ¿ĞµÑ‡ĞµĞ½ÑŒÑ�": {
        "name": "ĞšĞ»Ñ‘Ñ†ĞºĞ¸ Ñ� Ğ¿ĞµÑ‡ĞµĞ½ÑŒÑ�",
        "name_en": ["leverpostej", "danish liver pate"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 260, "protein": 12.0, "fat": 21.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ°Ñ� Ğ¿ĞµÑ‡ĞµĞ½ÑŒ", "type": "protein", "percent": 50},
            {"name": "Ñ�Ğ°Ğ»Ğ¾", "type": "fat", "percent": 25},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 8},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 7}
        ],
        "keywords": ["leverpostej", "Ğ´Ğ°Ñ‚Ñ�ĞºĞ¸Ğ¹", "Ğ¿Ğ°ÑˆÑ‚ĞµÑ‚"]
    },
    "Ñ„Ñ€Ğ¸ĞºĞ°Ğ´ĞµĞ»ÑŒĞºĞ¸ Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ¾Ğ¹": {
        "name": "Ğ¤Ñ€Ğ¸ĞºĞ°Ğ´ĞµĞ»ÑŒĞºĞ¸ Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ¾Ğ¹",
        "name_en": ["frikadeller med rÃ¸dkÃ¥l", "danish meatballs with red cabbage"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 11.0, "fat": 9.0, "carbs": 12.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¾Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 35},
            {"name": "ĞºÑ€Ğ°Ñ�Ğ½Ğ¾ĞºĞ¾Ñ‡Ğ°Ğ½Ğ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "type": "vegetable", "percent": 40},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ±Ğ»Ğ¾ĞºĞ¸", "type": "fruit", "percent": 8},
            {"name": "ÑƒĞºÑ�ÑƒÑ�", "type": "other", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 2}
        ],
        "keywords": ["frikadeller", "Ğ´Ğ°Ñ‚Ñ�ĞºĞ¸Ğµ Ñ„Ñ€Ğ¸ĞºĞ°Ğ´ĞµĞ»ÑŒĞºĞ¸", "ĞºÑ€Ğ°Ñ�Ğ½Ğ¾ĞºĞ¾Ñ‡Ğ°Ğ½Ğ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°"]
    },
    "Ğ½Ğ¾Ñ€Ğ²ĞµĞ¶Ñ�ĞºĞ¸Ğ¹ Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ": {
        "name": "Ğ—Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ",
        "name_en": ["baked salmon", "norwegian salmon"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 22.0, "fat": 12.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "type": "protein", "percent": 85},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 5},
            {"name": "ÑƒĞºÑ€Ğ¾Ğ¿", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "salmon", "Ğ½Ğ¾Ñ€Ğ²ĞµĞ¶Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ğ¼Ğ¾Ğ»Ğ»Ğµ Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ĞµĞ¼": {
        "name": "ĞœĞ¾Ğ»Ğ»Ğµ (ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ Ñ� Ñ€Ñ‹Ğ±Ğ¾Ğ¹)",
        "name_en": ["mÃ¸lle", "norwegian fish and potato mash"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 130, "protein": 8.0, "fat": 5.0, "carbs": 13.0},
        "ingredients": [
            {"name": "Ñ‚Ñ€ĞµÑ�ĞºĞ°", "type": "protein", "percent": 35},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 45},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 5}
        ],
        "keywords": ["mÃ¸lle", "Ğ½Ğ¾Ñ€Ğ²ĞµĞ¶Ñ�ĞºĞ¸Ğ¹", "Ñ‚Ñ€ĞµÑ�ĞºĞ°"]
    },
    "ĞºĞ¾Ğ¿Ñ‡ĞµĞ½Ğ°Ñ� ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ°": {
        "name": "ĞšĞ¾Ğ¿Ñ‡ĞµĞ½Ğ°Ñ� ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ°",
        "name_en": ["rakfisk", "norwegian fermented fish"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 20.0, "fat": 10.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ñ„Ğ¾Ñ€ĞµĞ»ÑŒ", "type": "protein", "percent": 90},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 8},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 2}
        ],
        "keywords": ["rakfisk", "Ğ½Ğ¾Ñ€Ğ²ĞµĞ¶Ñ�ĞºĞ°Ñ�", "Ñ„ĞµÑ€Ğ¼ĞµĞ½Ñ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°"]
    },
    "Ğ¿Ğ¸Ğ¸Ñ€Ğ¾Ğ¿ÑƒÑƒ": {
        "name": "ĞŸĞ¸Ğ¸Ñ€Ğ¾Ğ¿ÑƒÑƒ (ĞºĞ°Ñ€ĞµĞ»ÑŒÑ�ĞºĞ¸Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³)",
        "name_en": ["karjalanpiirakka", "finnish carelian pie"],
        "category": "bakery",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 210, "protein": 5.0, "fat": 6.0, "carbs": 34.0},
        "ingredients": [
            {"name": "Ñ€Ğ¶Ğ°Ğ½Ğ°Ñ� Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 45},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 35},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 5}
        ],
        "keywords": ["ĞºĞ°Ñ€ĞµĞ»ÑŒÑ�ĞºĞ¸Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³", "karjalanpiirakka", "Ñ„Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹"]
    },
    "ĞºĞ°Ğ»Ğ°ĞºÑƒĞºĞºĞ¾": {
        "name": "ĞšĞ°Ğ»Ğ°ĞºÑƒĞºĞºĞ¾ (Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³)",
        "name_en": ["kalakukko", "finnish fish pie"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 12.0, "fat": 7.0, "carbs": 17.0},
        "ingredients": [
            {"name": "Ñ€Ğ¶Ğ°Ğ½Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 45},
            {"name": "Ñ€Ñ‹Ğ±Ğ°", "type": "protein", "percent": 35},
            {"name": "Ğ±ĞµĞºĞ¾Ğ½", "type": "protein", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["kalakukko", "Ñ„Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹", "Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³"]
    },
    "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ğ¿Ğ¾-Ñ„Ğ¸Ğ½Ñ�ĞºĞ¸": {
        "name": "Ğ›Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ğ¿Ğ¾-Ñ„Ğ¸Ğ½Ñ�ĞºĞ¸",
        "name_en": ["lohipyÃ¶rykÃ¤t", "finnish salmon balls"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 12.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "type": "protein", "percent": 60},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 5}
        ],
        "keywords": ["lohipyÃ¶rykÃ¤t", "Ñ„Ğ¸Ğ½Ñ�ĞºĞ¸Ğµ Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğµ ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹"]
    },

    # ==================== Ğ‘Ğ›Ğ˜Ğ–Ğ�Ğ•Ğ’Ğ�Ğ¡Ğ¢Ğ�Ğ§Ğ�Ğ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "Ñ…ÑƒĞ¼ÑƒÑ�": {
        "name": "Ğ¥ÑƒĞ¼ÑƒÑ�",
        "name_en": ["hummus", "chickpea dip"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 200, "protein": 6.0, "fat": 12.0, "carbs": 17.0},
        "ingredients": [
            {"name": "Ğ½ÑƒÑ‚", "type": "protein", "percent": 50},
            {"name": "Ñ‚Ğ°Ñ…Ğ¸Ğ½Ğ¸", "type": "sauce", "percent": 15},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 15},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 10},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ñ…ÑƒĞ¼ÑƒÑ�", "hummus", "Ğ¸Ğ·Ñ€Ğ°Ğ¸Ğ»ÑŒÑ�ĞºĞ¸Ğ¹"]
    },
    "Ğ±Ğ°Ğ±Ğ° Ğ³Ğ°Ğ½ÑƒÑˆ": {
        "name": "Ğ‘Ğ°Ğ±Ğ° Ğ³Ğ°Ğ½ÑƒÑˆ",
        "name_en": ["baba ganoush", "eggplant dip"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 2.0, "fat": 10.0, "carbs": 10.0},
        "ingredients": [
            {"name": "Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½", "type": "vegetable", "percent": 65},
            {"name": "Ñ‚Ğ°Ñ…Ğ¸Ğ½Ğ¸", "type": "sauce", "percent": 15},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ğ¿ĞµÑ‚Ñ€ÑƒÑˆĞºĞ°", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["Ğ±Ğ°Ğ±Ğ° Ğ³Ğ°Ğ½ÑƒÑˆ", "baba ganoush", "Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½Ğ½Ğ°Ñ� Ğ¸ĞºÑ€Ğ°"]
    },
    "Ñ„Ğ°Ğ»Ğ°Ñ„ĞµĞ»ÑŒ": {
        "name": "Ğ¤Ğ°Ğ»Ğ°Ñ„ĞµĞ»ÑŒ",
        "name_en": ["falafel"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 8.0, "fat": 12.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ğ½ÑƒÑ‚", "type": "protein", "percent": 70},
            {"name": "Ğ¿ĞµÑ‚Ñ€ÑƒÑˆĞºĞ°", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "ĞºÑƒĞ¼Ğ¸Ğ½", "type": "spice", "percent": 2},
            {"name": "ĞºĞ¾Ñ€Ğ¸Ğ°Ğ½Ğ´Ñ€", "type": "spice", "percent": 2},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 10}
        ],
        "keywords": ["Ñ„Ğ°Ğ»Ğ°Ñ„ĞµĞ»ÑŒ", "falafel"]
    },
    "ÑˆĞ°ĞºÑˆÑƒĞºĞ°": {
        "name": "Ğ¨Ğ°ĞºÑˆÑƒĞºĞ°",
        "name_en": ["shakshuka"],
        "category": "breakfast",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 100, "protein": 5.0, "fat": 6.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 30},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 40},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ğ¿Ğ°Ğ¿Ñ€Ğ¸ĞºĞ°", "type": "spice", "percent": 2},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 7}
        ],
        "keywords": ["ÑˆĞ°ĞºÑˆÑƒĞºĞ°", "shakshuka"]
    },
    "Ñ‚Ğ°Ğ±ÑƒĞ»Ğµ": {
        "name": "Ğ¢Ğ°Ğ±ÑƒĞ»Ğµ",
        "name_en": ["tabbouleh", "bulgur salad"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 3.0, "fat": 5.0, "carbs": 16.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ³ÑƒÑ€", "type": "carb", "percent": 35},
            {"name": "Ğ¿ĞµÑ‚Ñ€ÑƒÑˆĞºĞ°", "type": "vegetable", "percent": 30},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ñ�Ñ‚Ğ°", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 5},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 2}
        ],
        "keywords": ["Ñ‚Ğ°Ğ±ÑƒĞ»Ğµ", "tabbouleh", "Ğ±Ğ»Ğ¸Ğ¶Ğ½ĞµĞ²Ğ¾Ñ�Ñ‚Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚"]
    },
    "ĞºĞ¸Ğ±Ğ±Ğµ": {
        "name": "ĞšĞ¸Ğ±Ğ±Ğµ",
        "name_en": ["kibbeh", "middle eastern meatballs"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 12.0, "fat": 13.0, "carbs": 15.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ³ÑƒÑ€", "type": "carb", "percent": 40},
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 40},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["ĞºĞ¸Ğ±Ğ±Ğµ", "kibbeh", "Ğ»Ğ¸Ğ²Ğ°Ğ½Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ğ»Ğ°Ğ¼Ğ°Ğ´Ğ¶ÑƒĞ½": {
        "name": "Ğ›Ğ°Ğ¼Ğ°Ğ´Ğ¶ÑƒĞ½",
        "name_en": ["lahmacun", "armenian pizza", "turkish pizza"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 210, "protein": 9.0, "fat": 8.0, "carbs": 26.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 50},
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 25},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 5},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¿ĞµÑ‚Ñ€ÑƒÑˆĞºĞ°", "type": "vegetable", "percent": 3},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["Ğ»Ğ°Ğ¼Ğ°Ğ´Ğ¶ÑƒĞ½", "lahmacun", "Ñ‚ÑƒÑ€ĞµÑ†ĞºĞ°Ñ� Ğ¿Ğ¸Ñ†Ñ†Ğ°"]
    },
    "Ğ¿Ğ°Ñ…Ğ»Ğ°Ğ²Ğ°": {
        "name": "ĞŸĞ°Ñ…Ğ»Ğ°Ğ²Ğ°",
        "name_en": ["baklava"],
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 450, "protein": 5.0, "fat": 25.0, "carbs": 50.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ñ„Ğ¸Ğ»Ğ¾", "type": "carb", "percent": 40},
            {"name": "Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğµ Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 25},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 20},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "ĞºĞ¾Ñ€Ğ¸Ñ†Ğ°", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ğ¿Ğ°Ñ…Ğ»Ğ°Ğ²Ğ°", "baklava"]
    },
    "ĞºĞ°Ğ½Ğ°Ñ„Ğµ": {
        "name": "ĞšĞ°Ğ½Ğ°Ñ„Ğµ",
        "name_en": ["knafeh", "middle eastern cheese pastry"],
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 350, "protein": 8.0, "fat": 18.0, "carbs": 40.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ ĞºĞ°Ñ‚Ğ°Ğ¸Ñ„Ğ¸", "type": "carb", "percent": 45},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 30},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 15},
            {"name": "Ñ„Ğ¸Ñ�Ñ‚Ğ°ÑˆĞºĞ¸", "type": "protein", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["ĞºĞ°Ğ½Ğ°Ñ„Ğµ", "knafeh", "Ğ°Ñ€Ğ°Ğ±Ñ�ĞºĞ¸Ğ¹ Ğ´ĞµÑ�ĞµÑ€Ñ‚"]
    },
    "Ñ„ĞµÑ‚Ñ‚ÑƒÑˆ": {
        "name": "Ğ¤ĞµÑ‚Ñ‚ÑƒÑˆ",
        "name_en": ["fattoush", "levantine bread salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 110, "protein": 3.0, "fat": 6.0, "carbs": 11.0},
        "ingredients": [
            {"name": "Ğ¿Ğ¸Ñ‚Ñ‚Ğ°", "type": "carb", "percent": 25},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 25},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹", "type": "vegetable", "percent": 15},
            {"name": "Ñ€ĞµĞ´Ğ¸Ñ�", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ñ�Ñ‚Ğ°", "type": "vegetable", "percent": 5},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5},
            {"name": "Ñ�ÑƒĞ¼Ğ°Ñ…", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ñ„ĞµÑ‚Ñ‚ÑƒÑˆ", "fattoush", "Ğ»Ğ¸Ğ²Ğ°Ğ½Ñ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚"]
    },

    # ==================== Ğ�Ğ¤Ğ Ğ˜ĞšĞ�Ğ�Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "Ñ‚Ğ°Ğ¶Ğ¸Ğ½": {
        "name": "Ğ¢Ğ°Ğ¶Ğ¸Ğ½",
        "name_en": ["tagine", "moroccan tagine"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 180, "protein": 12.0, "fat": 10.0, "carbs": 10.0},
        "ingredients": [
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 35},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 15},
            {"name": "Ñ‚Ñ‹ĞºĞ²Ğ°", "type": "vegetable", "percent": 10},
            {"name": "Ğ½ÑƒÑ‚", "type": "protein", "percent": 10},
            {"name": "Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²", "type": "fruit", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ¸Ğ½Ğ´Ğ°Ğ»ÑŒ", "type": "protein", "percent": 4},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ñ‚Ğ°Ğ¶Ğ¸Ğ½", "tagine", "Ğ¼Ğ°Ñ€Ğ¾ĞºĞºĞ°Ğ½Ñ�ĞºĞ¸Ğ¹"]
    },
    "ĞºÑƒÑ�ĞºÑƒÑ�": {
        "name": "ĞšÑƒÑ�ĞºÑƒÑ�",
        "name_en": ["couscous"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 140, "protein": 5.0, "fat": 4.0, "carbs": 21.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ�ĞºÑƒÑ�", "type": "carb", "percent": 45},
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 20},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "ĞºĞ°Ğ±Ğ°Ñ‡Ğ¾Ğº", "type": "vegetable", "percent": 8},
            {"name": "Ğ½ÑƒÑ‚", "type": "protein", "percent": 5},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¸Ğ·Ñ�Ğ¼", "type": "fruit", "percent": 3},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 4}
        ],
        "keywords": ["ĞºÑƒÑ�ĞºÑƒÑ�", "couscous"]
    },
    "Ñ…Ğ°Ñ€Ğ¸Ñ€Ğ°": {
        "name": "Ğ¥Ğ°Ñ€Ğ¸Ñ€Ğ°",
        "name_en": ["harira", "moroccan soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 70, "protein": 4.0, "fat": 2.0, "carbs": 9.0},
        "ingredients": [
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 15},
            {"name": "Ğ½ÑƒÑ‚", "type": "protein", "percent": 10},
            {"name": "Ñ‡ĞµÑ‡ĞµĞ²Ğ¸Ñ†Ğ°", "type": "protein", "percent": 8},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�ĞµĞ»ÑŒĞ´ĞµÑ€ĞµĞ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 3},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 37}
        ],
        "keywords": ["Ñ…Ğ°Ñ€Ğ¸Ñ€Ğ°", "harira"]
    },
    "Ğ¿Ğ°Ñ�Ñ‚Ğ¸Ğ»ÑŒÑ�": {
        "name": "ĞŸĞ°Ñ�Ñ‚Ğ¸Ğ»ÑŒÑ�",
        "name_en": ["pastilla", "moroccan pie"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 240, "protein": 12.0, "fat": 12.0, "carbs": 21.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ²Ğ°Ñ€ĞºĞ°", "type": "carb", "percent": 35},
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 25},
            {"name": "Ğ¼Ğ¸Ğ½Ğ´Ğ°Ğ»ÑŒ", "type": "protein", "percent": 12},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ğ°Ñ� Ğ¿ÑƒĞ´Ñ€Ğ°", "type": "carb", "percent": 5},
            {"name": "ĞºĞ¾Ñ€Ğ¸Ñ†Ğ°", "type": "spice", "percent": 2},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¿Ğ°Ñ�Ñ‚Ğ¸Ğ»ÑŒÑ�", "pastilla", "b'stilla"]
    },
    "Ñ„ÑƒĞ» Ğ¼ĞµĞ´Ğ°Ğ¼ĞµÑ�": {
        "name": "Ğ¤ÑƒĞ» Ğ¼ĞµĞ´Ğ°Ğ¼ĞµÑ�",
        "name_en": ["ful medames", "egyptian fava beans"],
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 7.0, "fat": 4.0, "carbs": 14.0},
        "ingredients": [
            {"name": "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ Ñ„Ğ°Ğ²Ğ°", "type": "protein", "percent": 60},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 8},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ‚Ğ¼Ğ¸Ğ½", "type": "spice", "percent": 2},
            {"name": "Ğ¿ĞµÑ‚Ñ€ÑƒÑˆĞºĞ°", "type": "vegetable", "percent": 5},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ñ„ÑƒĞ»", "ful medames", "ĞµĞ³Ğ¸Ğ¿ĞµÑ‚Ñ�ĞºĞ¸Ğ¹ Ğ·Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº"]
    },
    "ĞºĞ¾ÑˆĞ°Ñ€Ğ¸": {
        "name": "ĞšĞ¾ÑˆĞ°Ñ€Ğ¸",
        "name_en": ["koshari", "egyptian street food"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 160, "protein": 6.0, "fat": 4.0, "carbs": 26.0},
        "ingredients": [
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 30},
            {"name": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹", "type": "carb", "percent": 20},
            {"name": "Ñ‡ĞµÑ‡ĞµĞ²Ğ¸Ñ†Ğ°", "type": "protein", "percent": 20},
            {"name": "Ğ½ÑƒÑ‚", "type": "protein", "percent": 8},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 12},
            {"name": "Ğ»ÑƒĞº Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["ĞºĞ¾ÑˆĞ°Ñ€Ğ¸", "koshari", "ĞµĞ³Ğ¸Ğ¿ĞµÑ‚Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ğ¼Ğ¾Ñ…Ğ¸Ğ½Ğ³Ğ°": {
        "name": "ĞœĞ¾Ñ…Ğ¸Ğ½Ğ³Ğ°",
        "name_en": ["mohinga", "burmese fish soup"],
        "category": "soup",
        "default_weight": 450,
        "nutrition_per_100": {"calories": 70, "protein": 5.0, "fat": 2.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ñ€Ñ‹Ğ±Ğ°", "type": "protein", "percent": 15},
            {"name": "Ñ€Ğ¸Ñ�Ğ¾Ğ²Ğ°Ñ� Ğ»Ğ°Ğ¿ÑˆĞ°", "type": "carb", "percent": 25},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½", "type": "liquid", "percent": 45},
            {"name": "Ğ±Ğ°Ğ½Ğ°Ğ½", "type": "fruit", "percent": 5},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¸Ğ¼Ğ±Ğ¸Ñ€ÑŒ", "type": "spice", "percent": 3},
            {"name": "ĞºÑƒÑ€ĞºÑƒĞ¼Ğ°", "type": "spice", "percent": 2}
        ],
        "keywords": ["Ğ¼Ğ¾Ñ…Ğ¸Ğ½Ğ³Ğ°", "mohinga", "Ğ±Ğ¸Ñ€Ğ¼Ğ°Ğ½Ñ�ĞºĞ¸Ğ¹ Ñ�ÑƒĞ¿"]
    },
    "Ğ°Ğ´Ğ¾Ğ±Ğ¾": {
        "name": "Ğ�Ğ´Ğ¾Ğ±Ğ¾",
        "name_en": ["adobo", "filipino chicken adobo"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 18.0, "fat": 13.0, "carbs": 6.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 50},
            {"name": "Ñ�Ğ¾ĞµĞ²Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 15},
            {"name": "ÑƒĞºÑ�ÑƒÑ�", "type": "other", "percent": 15},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 8},
            {"name": "Ğ»Ğ°Ğ²Ñ€Ğ¾Ğ²Ñ‹Ğ¹ Ğ»Ğ¸Ñ�Ñ‚", "type": "spice", "percent": 2},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "spice", "percent": 2},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 8}
        ],
        "keywords": ["adobo", "Ñ„Ğ¸Ğ»Ğ¸Ğ¿Ğ¿Ğ¸Ğ½Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ñ�Ñ�Ñ�Ğ°": {
        "name": "Ğ¯Ñ�Ñ�Ğ°",
        "name_en": ["yassa", "senegalese chicken"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 16.0, "fat": 9.0, "carbs": 7.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 45},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 30},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 10},
            {"name": "Ğ³Ğ¾Ñ€Ñ‡Ğ¸Ñ†Ğ°", "type": "sauce", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ñ‡Ğ¸Ğ»Ğ¸", "type": "vegetable", "percent": 3},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["yassa", "senegalese", "chicken"]
    },
    "Ğ½'Ğ´Ğ¾Ğ»Ğµ": {
        "name": "Ğ�'Ğ´Ğ¾Ğ»Ğµ",
        "name_en": ["ndole", "cameroonian bitter leaf stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 12.0, "fat": 11.0, "carbs": 9.0},
        "ingredients": [
            {"name": "Ğ°Ñ€Ğ°Ñ…Ğ¸Ñ�", "type": "protein", "percent": 30},
            {"name": "Ğ³Ğ¾Ñ€ÑŒĞºĞ¸Ğµ Ğ»Ğ¸Ñ�Ñ‚ÑŒÑ�", "type": "vegetable", "percent": 30},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 20},
            {"name": "ĞºÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸", "type": "protein", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 7},
            {"name": "Ğ¿Ğ°Ğ»ÑŒĞ¼Ğ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["ndole", "cameroonian", "cameroon"]
    },
    "Ñ�Ğ³ÑƒÑ�Ğ¸": {
        "name": "Ğ­Ğ³ÑƒÑ�Ğ¸",
        "name_en": ["egusi soup", "nigerian melon seed soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 10.0, "fat": 15.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ñ‚Ñ‹ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğµ Ñ�ĞµĞ¼ĞµÑ‡ĞºĞ¸", "type": "protein", "percent": 35},
            {"name": "ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚", "type": "vegetable", "percent": 25},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 15},
            {"name": "Ñ€Ñ‹Ğ±Ğ°", "type": "protein", "percent": 10},
            {"name": "Ğ¿Ğ°Ğ»ÑŒĞ¼Ğ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["egusi", "nigerian", "soup"]
    },
    "Ğ´Ğ¶Ğ¾Ğ»Ğ»Ğ¾Ñ„ Ñ€Ğ°Ğ¹Ñ�": {
        "name": "Ğ”Ğ¶Ğ¾Ğ»Ğ»Ğ¾Ñ„ Ñ€Ğ°Ğ¹Ñ�",
        "name_en": ["jollof rice", "west african rice"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 150, "protein": 5.0, "fat": 4.0, "carbs": 24.0},
        "ingredients": [
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 55},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 8},
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 7},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5}
        ],
        "keywords": ["jollof", "jollof rice", "west african"]
    },
    "Ñ„ÑƒÑ„Ñƒ": {
        "name": "Ğ¤ÑƒÑ„Ñƒ",
        "name_en": ["fufu", "west african dough"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 2.0, "fat": 1.0, "carbs": 30.0},
        "ingredients": [
            {"name": "Ğ¼Ğ°Ğ½Ğ¸Ğ¾ĞºĞ°", "type": "carb", "percent": 60},
            {"name": "Ğ¿Ğ»Ğ°Ğ½Ñ‚Ğ°Ğ½", "type": "carb", "percent": 40}
        ],
        "keywords": ["fufu", "west african"]
    },

    # ==================== Ğ¡Ğ•Ğ’Ğ•Ğ Ğ�Ğ�ĞœĞ•Ğ Ğ˜ĞšĞ�Ğ�Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "Ğ¿ÑƒÑ‚Ğ¸Ğ½": {
        "name": "ĞŸÑƒÑ‚Ğ¸Ğ½",
        "name_en": ["poutine", "canadian poutine"],
        "category": "fastfood",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 230, "protein": 6.0, "fat": 14.0, "carbs": 20.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ñ„Ñ€Ğ¸", "type": "carb", "percent": 60},
            {"name": "Ñ�Ñ‹Ñ€Ğ½Ñ‹Ğµ Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ¶ĞºĞ¸", "type": "dairy", "percent": 20},
            {"name": "Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 20}
        ],
        "keywords": ["Ğ¿ÑƒÑ‚Ğ¸Ğ½", "poutine", "ĞºĞ°Ğ½Ğ°Ğ´Ñ�ĞºĞ¸Ğ¹"]
    },
    "ĞºÑ�Ğ¶ÑƒĞ°Ğ»": {
        "name": "ĞšÑ�Ğ¶ÑƒĞ°Ğ» (Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹ Ñ€ÑƒĞ»ĞµÑ‚)",
        "name_en": ["casual", "canadian meat roll"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 16.0, "fat": 17.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¾Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 60},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ…Ğ»ĞµĞ±Ğ½Ñ‹Ğµ ĞºÑ€Ğ¾ÑˆĞºĞ¸", "type": "carb", "percent": 7},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5}
        ],
        "keywords": ["casual", "canadian meatloaf"]
    },
    "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ½Ñ‹Ğ¹ Ñ…Ğ»ĞµĞ±": {
        "name": "ĞšÑƒĞºÑƒÑ€ÑƒĞ·Ğ½Ñ‹Ğ¹ Ñ…Ğ»ĞµĞ±",
        "name_en": ["cornbread", "american cornbread"],
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 260, "protein": 5.0, "fat": 8.0, "carbs": 42.0},
        "ingredients": [
            {"name": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ½Ğ°Ñ� Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 60},
            {"name": "Ğ¼ÑƒĞºĞ° Ğ¿ÑˆĞµĞ½Ğ¸Ñ‡Ğ½Ğ°Ñ�", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 8},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 2}
        ],
        "keywords": ["cornbread", "american bread"]
    },
    "ĞºĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�": {
        "name": "ĞšĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
        "name_en": ["cranberry sauce", "american sauce"],
        "category": "sauce",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 150, "protein": 0.5, "fat": 0.1, "carbs": 37.0},
        "ingredients": [
            {"name": "ĞºĞ»Ñ�ĞºĞ²Ğ°", "type": "fruit", "percent": 60},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 35},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["cranberry sauce", "thanksgiving"]
    },
    "Ñ‚Ñ‹ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³": {
        "name": "Ğ¢Ñ‹ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³",
        "name_en": ["pumpkin pie", "american pumpkin pie"],
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 210, "protein": 4.0, "fat": 9.0, "carbs": 28.0},
        "ingredients": [
            {"name": "Ñ‚Ñ‹ĞºĞ²Ğ°", "type": "vegetable", "percent": 35},
            {"name": "Ğ¿ĞµÑ�Ğ¾Ñ‡Ğ½Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 30},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 8},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 15},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 10},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["pumpkin pie", "thanksgiving"]
    },
    "Ğ¿ĞµĞºĞ°Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³": {
        "name": "ĞŸĞµĞºĞ°Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³",
        "name_en": ["pecan pie", "american pecan pie"],
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 400, "protein": 5.0, "fat": 22.0, "carbs": 47.0},
        "ingredients": [
            {"name": "Ğ¿ĞµĞºĞ°Ğ½", "type": "protein", "percent": 30},
            {"name": "Ğ¿ĞµÑ�Ğ¾Ñ‡Ğ½Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 30},
            {"name": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 20},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 10},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["pecan pie", "american dessert"]
    },
    "ĞºĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�": {
        "name": "ĞšĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
        "name_en": ["cranberry sauce"],
        "category": "sauce",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 150, "protein": 0.5, "fat": 0.1, "carbs": 37.0},
        "ingredients": [
            {"name": "ĞºĞ»Ñ�ĞºĞ²Ğ°", "type": "fruit", "percent": 60},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 35},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["cranberry sauce"]
    },
    "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ğ¿Ğ¾-ĞºĞ°Ğ½Ğ°Ğ´Ñ�ĞºĞ¸": {
        "name": "Ğ›Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ğ¿Ğ¾-ĞºĞ°Ğ½Ğ°Ğ´Ñ�ĞºĞ¸",
        "name_en": ["canadian salmon"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 22.0, "fat": 11.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "type": "protein", "percent": 85},
            {"name": "ĞºĞ»ĞµĞ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 8},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 4}
        ],
        "keywords": ["canadian salmon", "maple salmon"]
    },

    # ==================== Ğ®Ğ–Ğ�Ğ�Ğ�ĞœĞ•Ğ Ğ˜ĞšĞ�Ğ�Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ ====================
    "Ñ„ĞµĞ¹Ğ¶Ğ¾Ğ°Ğ´Ğ°": {
        "name": "Ğ¤ĞµĞ¹Ğ¶Ğ¾Ğ°Ğ´Ğ°",
        "name_en": ["feijoada", "brazilian black bean stew"],
        "category": "main",
        "default_weight": 450,
        "nutrition_per_100": {"calories": 170, "protein": 12.0, "fat": 8.0, "carbs": 13.0},
        "ingredients": [
            {"name": "Ñ‡ĞµÑ€Ğ½Ğ°Ñ� Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ", "type": "protein", "percent": 40},
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 25},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 15},
            {"name": "ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ°", "type": "protein", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 2}
        ],
        "keywords": ["feijoada", "Ğ±Ñ€Ğ°Ğ·Ğ¸Ğ»ÑŒÑ�ĞºĞ¸Ğ¹"]
    },
    "Ğ¼Ğ¾ÑƒĞºĞµĞºĞµ": {
        "name": "ĞœĞ¾ÑƒĞºĞµĞºĞµ",
        "name_en": ["mole", "mexican mole poblano"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 8.0, "fat": 13.0, "carbs": 16.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 35},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ñ‡Ğ¸Ğ»Ğ¸", "type": "vegetable", "percent": 20},
            {"name": "ÑˆĞ¾ĞºĞ¾Ğ»Ğ°Ğ´", "type": "other", "percent": 10},
            {"name": "Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 10},
            {"name": "Ñ�ĞµĞ¼ĞµĞ½Ğ°", "type": "protein", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 7},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["mole", "mexican", "poblano"]
    },
    "Ğ°Ñ€ĞµĞ¿Ğ°Ñ�": {
        "name": "Ğ�Ñ€ĞµĞ¿Ğ°Ñ�",
        "name_en": ["arepas", "venezuelan corn cakes"],
        "category": "bread",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 4.0, "fat": 6.0, "carbs": 36.0},
        "ingredients": [
            {"name": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ½Ğ°Ñ� Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 70},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 20},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 5}
        ],
        "keywords": ["arepas", "venezuelan"]
    },
    "Ñ�Ğ¼Ğ¿Ğ°Ğ½Ğ°Ğ´Ğ°Ñ�": {
        "name": "Ğ­Ğ¼Ğ¿Ğ°Ğ½Ğ°Ğ´Ğ°Ñ�",
        "name_en": ["empanadas", "argentinian pastries"],
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 260, "protein": 8.0, "fat": 14.0, "carbs": 25.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 50},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 25},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¸Ğ½Ñ‹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["empanadas", "argentinian"]
    },
    "Ñ�ĞµĞ²Ğ¸Ñ‡Ğµ": {
        "name": "Ğ¡ĞµĞ²Ğ¸Ñ‡Ğµ",
        "name_en": ["ceviche", "peruvian ceviche"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 90, "protein": 12.0, "fat": 2.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ€Ñ‹Ğ±Ğ°", "type": "protein", "percent": 50},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 20},
            {"name": "Ğ»ÑƒĞº ĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ñ‡Ğ¸Ğ»Ğ¸", "type": "vegetable", "percent": 5},
            {"name": "ĞºĞ¸Ğ½Ğ·Ğ°", "type": "vegetable", "percent": 5},
            {"name": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ°", "type": "carb", "percent": 5},
            {"name": "Ğ±Ğ°Ñ‚Ğ°Ñ‚", "type": "carb", "percent": 5}
        ],
        "keywords": ["ceviche", "peruvian"]
    },
    "Ğ¼Ğ°Ñ‚Ğµ": {
        "name": "ĞœĞ°Ñ‚Ğµ",
        "name_en": ["mate", "yerba mate"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 5, "protein": 0.2, "fat": 0.1, "carbs": 1.0},
        "ingredients": [
            {"name": "Ğ¹ĞµÑ€Ğ±Ğ° Ğ¼Ğ°Ñ‚Ğµ", "type": "other", "percent": 10},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 90}
        ],
        "keywords": ["mate", "yerba mate", "south american tea"]
    },
    "Ğ¿Ğ°Ñ�Ñ‚ĞµĞ»ÑŒ Ğ´Ğµ Ñ‡Ğ¾ĞºĞ»Ğ¾": {
        "name": "ĞŸĞ°Ñ�Ñ‚ĞµĞ»ÑŒ Ğ´Ğµ Ñ‡Ğ¾ĞºĞ»Ğ¾",
        "name_en": ["pastel de choclo", "chilean corn pie"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 160, "protein": 7.0, "fat": 6.0, "carbs": 20.0},
        "ingredients": [
            {"name": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ°", "type": "carb", "percent": 50},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 20},
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¸Ğ½Ñ‹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¸Ğ·Ñ�Ğ¼", "type": "fruit", "percent": 2}
        ],
        "keywords": ["pastel de choclo", "chilean pie"]
    },
    "Ğ¿Ğ°Ğ¿Ğ°Ğ´Ğ·Ñ�Ğ»ĞµÑ�": {
        "name": "ĞŸĞ°Ğ¿Ğ°Ğ´Ğ·Ñ�Ğ»ĞµÑ�",
        "name_en": ["papadzules", "mexican egg rolls"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 10.0, "carbs": 15.0},
        "ingredients": [
            {"name": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ½Ğ°Ñ� Ñ‚Ğ¾Ñ€Ñ‚Ğ¸Ğ»ÑŒÑ�", "type": "carb", "percent": 40},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 25},
            {"name": "Ñ‚Ñ‹ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğµ Ñ�ĞµĞ¼ĞµÑ‡ĞºĞ¸", "type": "protein", "percent": 15},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["papadzules", "mexican"]
    },

    # ==================== Ğ�ĞšĞ•Ğ�Ğ�Ğ˜Ğ¯ ====================
    "Ğ¿Ğ°Ğ²Ğ»Ğ¾Ğ²Ğ°": {
        "name": "ĞŸĞ°Ğ²Ğ»Ğ¾Ğ²Ğ°",
        "name_en": ["pavlova", "australian dessert", "new zealand dessert"],
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 250, "protein": 3.0, "fat": 5.0, "carbs": 48.0},
        "ingredients": [
            {"name": "Ğ±ĞµĞ·Ğµ", "type": "carb", "percent": 50},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 25},
            {"name": "ĞºĞ»ÑƒĞ±Ğ½Ğ¸ĞºĞ°", "type": "fruit", "percent": 10},
            {"name": "ĞºĞ¸Ğ²Ğ¸", "type": "fruit", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ€Ğ°ĞºÑƒĞ¹Ñ�", "type": "fruit", "percent": 5}
        ],
        "keywords": ["pavlova", "australian", "new zealand dessert"]
    },
    "Ğ»Ğ°Ğ¼Ğ¸Ğ½Ñ‚Ğ¾Ğ½": {
        "name": "Ğ›Ğ°Ğ¼Ğ¸Ğ½Ñ‚Ğ¾Ğ½",
        "name_en": ["lamington", "australian cake"],
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 300, "protein": 4.0, "fat": 12.0, "carbs": 44.0},
        "ingredients": [
            {"name": "Ğ±Ğ¸Ñ�ĞºĞ²Ğ¸Ñ‚", "type": "carb", "percent": 60},
            {"name": "ÑˆĞ¾ĞºĞ¾Ğ»Ğ°Ğ´Ğ½Ğ°Ñ� Ğ³Ğ»Ğ°Ğ·ÑƒÑ€ÑŒ", "type": "sugar", "percent": 25},
            {"name": "ĞºĞ¾ĞºĞ¾Ñ�Ğ¾Ğ²Ğ°Ñ� Ñ�Ñ‚Ñ€ÑƒĞ¶ĞºĞ°", "type": "other", "percent": 15}
        ],
        "keywords": ["lamington", "australian cake"]
    },
    "Ğ¼Ğ¸Ñ‚ Ğ¿Ğ°Ğ¹": {
        "name": "ĞœĞ¸Ñ‚ Ğ¿Ğ°Ğ¹",
        "name_en": ["meat pie", "australian meat pie"],
        "category": "bakery",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 270, "protein": 10.0, "fat": 16.0, "carbs": 21.0},
        "ingredients": [
            {"name": "Ñ�Ğ»Ğ¾ĞµĞ½Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 45},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 10},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["meat pie", "australian pie"]
    },
    "Ñ„Ğ¸Ñˆ Ñ�Ğ½Ğ´ Ñ‡Ğ¸Ğ¿Ñ�": {
        "name": "Ğ¤Ğ¸Ñˆ Ñ�Ğ½Ğ´ Ñ‡Ğ¸Ğ¿Ñ�",
        "name_en": ["fish and chips"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 220, "protein": 12.0, "fat": 12.0, "carbs": 17.0},
        "ingredients": [
            {"name": "Ñ‚Ñ€ĞµÑ�ĞºĞ°", "type": "protein", "percent": 35},
            {"name": "ĞºĞ»Ñ�Ñ€", "type": "carb", "percent": 20},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 30},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 15}
        ],
        "keywords": ["fish and chips", "Ğ±Ñ€Ğ¸Ñ‚Ğ°Ğ½Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ğ°Ğ½Ğ·Ğ°Ğº Ğ±Ğ¸Ñ�ĞºĞ²Ğ¸Ñ‚": {
        "name": "Ğ�Ğ½Ğ·Ğ°Ğº Ğ±Ğ¸Ñ�ĞºĞ²Ğ¸Ñ‚",
        "name_en": ["anzac biscuit", "australian cookie"],
        "category": "dessert",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 400, "protein": 5.0, "fat": 16.0, "carbs": 60.0},
        "ingredients": [
            {"name": "Ğ¾Ğ²Ñ�Ñ�Ğ½Ñ‹Ğµ Ñ…Ğ»Ğ¾Ğ¿ÑŒÑ�", "type": "carb", "percent": 40},
            {"name": "ĞºĞ¾ĞºĞ¾Ñ�", "type": "other", "percent": 20},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 15},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10}
        ],
        "keywords": ["anzac biscuit", "australian cookie"]
    },
    "ĞºĞ¸Ğ²Ğ¸ Ğ±ÑƒÑ€Ğ³ĞµÑ€": {
        "name": "ĞšĞ¸Ğ²Ğ¸ Ğ±ÑƒÑ€Ğ³ĞµÑ€",
        "name_en": ["kiwi burger", "new zealand burger"],
        "category": "fastfood",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 12.0, "fat": 11.0, "carbs": 19.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ°", "type": "carb", "percent": 30},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ� ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ°", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ²ĞµĞºĞ»Ğ°", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 8},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 8},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 7},
            {"name": "Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 7}
        ],
        "keywords": ["kiwi burger", "new zealand burger"]
    },
    "Ñ…Ğ°Ğ½Ğ³Ğ¸": {
        "name": "Ğ¥Ğ°Ğ½Ğ³Ğ¸",
        "name_en": ["hangi", "maori earth oven"],
        "category": "main",
        "default_weight": 500,
        "nutrition_per_100": {"calories": 160, "protein": 14.0, "fat": 8.0, "carbs": 9.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 25},
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 20},
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 15},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ğ±Ğ°Ñ‚Ğ°Ñ‚", "type": "carb", "percent": 10},
            {"name": "Ñ‚Ñ‹ĞºĞ²Ğ°", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["hangi", "maori", "new zealand"]
    },
    "ÑƒĞ°Ğ¹Ñ‚Ğ°ĞºĞ¸Ñ‚Ğ°": {
        "name": "Ğ£Ğ°Ğ¹Ñ‚Ğ°ĞºĞ¸Ñ‚Ğ° (Ñ�ÑƒĞ¿ Ğ¸Ğ· Ğ¼Ğ¾Ğ»Ğ»Ñ�Ñ�ĞºĞ¾Ğ²)",
        "name_en": ["waitakita", "clam soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 70, "protein": 6.0, "fat": 2.0, "carbs": 7.0},
        "ingredients": [
            {"name": "Ğ¼Ğ¾Ğ»Ğ»Ñ�Ñ�ĞºĞ¸", "type": "protein", "percent": 25},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ğ»ÑƒĞº-Ğ¿Ğ¾Ñ€ĞµĞ¹", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 10},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½", "type": "liquid", "percent": 20}
        ],
        "keywords": ["waitakita", "new zealand soup"]
    },
    # =============================================================================
    # ğŸ‡·ğŸ‡º Ğ Ğ�Ğ¡Ğ¨Ğ˜Ğ Ğ•Ğ�Ğ�Ğ�Ğ¯ Ğ‘Ğ�Ğ—Ğ�: Ğ¢Ğ Ğ�Ğ”Ğ˜Ğ¦Ğ˜Ğ�Ğ�Ğ�Ğ«Ğ• Ğ˜ ĞŸĞ�ĞŸĞ£Ğ›Ğ¯Ğ Ğ�Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� Ğ Ğ�Ğ¡Ğ¡Ğ˜Ğ˜
    # =============================================================================
    
    # ==================== Ğ¡Ğ£ĞŸĞ« (Ğ�Ğ�Ğ’Ğ«Ğ• ĞŸĞ�Ğ—Ğ˜Ğ¦Ğ˜Ğ˜) ====================
    "Ñ‰Ğ¸ Ğ¸Ğ· ĞºĞ²Ğ°ÑˆĞµĞ½Ğ¾Ğ¹ ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ñ‹": {
        "name": "Ğ©Ğ¸ Ğ¸Ğ· ĞºĞ²Ğ°ÑˆĞµĞ½Ğ¾Ğ¹ ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ñ‹",
        "name_en": ["sauerkraut shchi", "russian cabbage soup with sauerkraut"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 50, "protein": 2.5, "fat": 2.0, "carbs": 5.5},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° ĞºĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ�", "type": "vegetable", "percent": 30},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 15},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 3},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 24}
        ],
        "keywords": ["Ñ‰Ğ¸", "ĞºĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "sauerkraut", "shchi", "Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğ¹ Ñ�ÑƒĞ¿"]
    },
    "Ñ‰Ğ¸ Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğµ": {
        "name": "Ğ©Ğ¸ Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğµ",
        "name_en": ["green shchi", "sorrel soup", "russian sorrel soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 2.0, "fat": 1.8, "carbs": 4.5},
        "ingredients": [
            {"name": "Ñ‰Ğ°Ğ²ĞµĞ»ÑŒ", "type": "vegetable", "percent": 30},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 8},
            {"name": "Ğ»ÑƒĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "ÑƒĞºÑ€Ğ¾Ğ¿", "type": "vegetable", "percent": 3},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½", "type": "liquid", "percent": 39}
        ],
        "keywords": ["Ñ‰Ğ¸", "Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğµ Ñ‰Ğ¸", "Ñ‰Ğ°Ğ²ĞµĞ»ÑŒ", "sorrel soup"]
    },
    "Ñ�Ğ²ĞµĞºĞ¾Ğ»ÑŒĞ½Ğ¸Ğº": {
        "name": "Ğ¡Ğ²ĞµĞºĞ¾Ğ»ÑŒĞ½Ğ¸Ğº",
        "name_en": ["svyokolnik", "cold beet soup", "russian beet soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 1.5, "fat": 1.5, "carbs": 5.0},
        "ingredients": [
            {"name": "Ñ�Ğ²ĞµĞºĞ»Ğ°", "type": "vegetable", "percent": 25},
            {"name": "ĞºĞµÑ„Ğ¸Ñ€", "type": "dairy", "percent": 40},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ²ĞµĞ¶Ğ¸Ğµ", "type": "vegetable", "percent": 15},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5},
            {"name": "ÑƒĞºÑ€Ğ¾Ğ¿", "type": "vegetable", "percent": 3},
            {"name": "Ğ»ÑƒĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 7}
        ],
        "keywords": ["Ñ�Ğ²ĞµĞºĞ¾Ğ»ÑŒĞ½Ğ¸Ğº", "Ñ…Ğ¾Ğ»Ğ¾Ğ´Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿", "beet soup", "Ñ�Ğ²ĞµĞºĞ»Ğ°"]
    },
    "Ğ±Ğ¾Ñ‚Ğ²Ğ¸Ğ½ÑŒÑ�": {
        "name": "Ğ‘Ğ¾Ñ‚Ğ²Ğ¸Ğ½ÑŒÑ�",
        "name_en": ["botvinya", "russian cold soup with greens"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 3.0, "fat": 1.5, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "type": "protein", "percent": 20},
            {"name": "Ñ‰Ğ°Ğ²ĞµĞ»ÑŒ", "type": "vegetable", "percent": 20},
            {"name": "ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚", "type": "vegetable", "percent": 15},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ²ĞµĞ¶Ğ¸Ğµ", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "ĞºĞ²Ğ°Ñ�", "type": "liquid", "percent": 22}
        ],
        "keywords": ["Ğ±Ğ¾Ñ‚Ğ²Ğ¸Ğ½ÑŒÑ�", "botvinya", "Ñ…Ğ¾Ğ»Ğ¾Ğ´Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿", "Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğ¹ Ñ�ÑƒĞ¿"]
    },
    "Ğ¿Ğ¾Ñ…Ğ»ĞµĞ±ĞºĞ° Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ°Ñ�": {
        "name": "ĞŸĞ¾Ñ…Ğ»ĞµĞ±ĞºĞ° Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ°Ñ�",
        "name_en": ["mushroom pohljobka", "russian mushroom soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 2.0, "fat": 1.5, "carbs": 4.5},
        "ingredients": [
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹ Ğ»ĞµÑ�Ğ½Ñ‹Ğµ", "type": "vegetable", "percent": 25},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¿ĞµÑ€Ğ»Ğ¾Ğ²ĞºĞ°", "type": "carb", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 42}
        ],
        "keywords": ["Ğ¿Ğ¾Ñ…Ğ»ĞµĞ±ĞºĞ°", "Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ¾Ğ¹ Ñ�ÑƒĞ¿", "mushroom soup"]
    },
    "ÑƒÑ…Ğ° Ñ†Ğ°Ñ€Ñ�ĞºĞ°Ñ�": {
        "name": "Ğ£Ñ…Ğ° Ñ†Ğ°Ñ€Ñ�ĞºĞ°Ñ�",
        "name_en": ["tsar's ukha", "russian fish soup deluxe"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 60, "protein": 6.0, "fat": 2.5, "carbs": 3.0},
        "ingredients": [
            {"name": "Ğ¾Ñ�ĞµÑ‚Ñ€Ğ¸Ğ½Ğ°", "type": "protein", "percent": 25},
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "type": "protein", "percent": 15},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 10},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "other", "percent": 3},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 37}
        ],
        "keywords": ["ÑƒÑ…Ğ°", "Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿", "fish soup", "Ğ¾Ñ�ĞµÑ‚Ñ€Ğ¸Ğ½Ğ°"]
    },
    "ĞºĞ°Ğ»ÑŒÑ�": {
        "name": "ĞšĞ°Ğ»ÑŒÑ�",
        "name_en": ["kalya", "russian pickle fish soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 55, "protein": 5.0, "fat": 2.0, "carbs": 4.5},
        "ingredients": [
            {"name": "Ñ€Ñ‹Ğ±Ğ° ĞºÑ€Ğ°Ñ�Ğ½Ğ°Ñ�", "type": "protein", "percent": 25},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ", "type": "vegetable", "percent": 20},
            {"name": "Ñ€Ğ°Ñ�Ñ�Ğ¾Ğ» Ğ¾Ğ³ÑƒÑ€ĞµÑ‡Ğ½Ñ‹Ğ¹", "type": "liquid", "percent": 20},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 22}
        ],
        "keywords": ["ĞºĞ°Ğ»ÑŒÑ�", "Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿", "pickle fish soup"]
    },
    
    # ==================== Ğ¡Ğ�Ğ›Ğ�Ğ¢Ğ« (Ğ�Ğ�Ğ’Ğ«Ğ• ĞŸĞ�Ğ—Ğ˜Ğ¦Ğ˜Ğ˜) ====================
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ¼Ğ¸Ğ¼Ğ¾Ğ·Ğ°": {
        "name": "ĞœĞ¸Ğ¼Ğ¾Ğ·Ğ°",
        "name_en": ["mimosa salad", "russian mimosa salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 10.0, "fat": 17.0, "carbs": 6.0},
        "ingredients": [
            {"name": "ĞºĞ¾Ğ½Ñ�ĞµÑ€Ğ²Ñ‹ Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğµ", "type": "protein", "percent": 25},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 20},
            {"name": "Ñ�Ñ‹Ñ€ Ñ‚Ğ²ĞµÑ€Ğ´Ñ‹Ğ¹", "type": "dairy", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 25}
        ],
        "keywords": ["Ğ¼Ğ¸Ğ¼Ğ¾Ğ·Ğ°", "mimosa", "Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚", "Ñ�Ğ»Ğ¾ĞµĞ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚"]
    },
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ�Ñ‚Ğ¾Ğ»Ğ¸Ñ‡Ğ½Ñ‹Ğ¹": {
        "name": "Ğ¡Ñ‚Ğ¾Ğ»Ğ¸Ñ‡Ğ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚",
        "name_en": ["stolichny salad", "russian capital salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 9.0, "fat": 15.0, "carbs": 7.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ°Ñ�", "type": "protein", "percent": 30},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 20},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ", "type": "vegetable", "percent": 10},
            {"name": "Ğ³Ğ¾Ñ€Ğ¾ÑˆĞµĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 7},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 10}
        ],
        "keywords": ["Ñ�Ñ‚Ğ¾Ğ»Ğ¸Ñ‡Ğ½Ñ‹Ğ¹", "stolichny", "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹"]
    },
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ½ĞµĞ¶Ğ½Ğ¾Ñ�Ñ‚ÑŒ": {
        "name": "Ğ�ĞµĞ¶Ğ½Ğ¾Ñ�Ñ‚ÑŒ",
        "name_en": ["nezhnost salad", "russian tender salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 8.0, "fat": 16.0, "carbs": 8.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 25},
            {"name": "Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²", "type": "fruit", "percent": 15},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ²ĞµĞ¶Ğ¸Ğµ", "type": "vegetable", "percent": 10},
            {"name": "Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğµ Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 10},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 10},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 15}
        ],
        "keywords": ["Ğ½ĞµĞ¶Ğ½Ğ¾Ñ�Ñ‚ÑŒ", "Ñ�Ğ»Ğ¾ĞµĞ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚", "Ñ� Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²Ğ¾Ğ¼"]
    },
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� ĞºÑ€Ğ°Ğ±Ğ¾Ğ²Ñ‹Ğ¼Ğ¸ Ğ¿Ğ°Ğ»Ğ¾Ñ‡ĞºĞ°Ğ¼Ğ¸": {
        "name": "Ğ¡Ğ°Ğ»Ğ°Ñ‚ Ñ� ĞºÑ€Ğ°Ğ±Ğ¾Ğ²Ñ‹Ğ¼Ğ¸ Ğ¿Ğ°Ğ»Ğ¾Ñ‡ĞºĞ°Ğ¼Ğ¸",
        "name_en": ["crab stick salad", "russian imitation crab salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 170, "protein": 6.0, "fat": 11.0, "carbs": 11.0},
        "ingredients": [
            {"name": "ĞºÑ€Ğ°Ğ±Ğ¾Ğ²Ñ‹Ğµ Ğ¿Ğ°Ğ»Ğ¾Ñ‡ĞºĞ¸", "type": "protein", "percent": 30},
            {"name": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ° ĞºĞ¾Ğ½Ñ�ĞµÑ€Ğ²Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ�", "type": "carb", "percent": 25},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ñ€Ğ¸Ñ� Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ¾Ğ¹", "type": "carb", "percent": 10},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ²ĞµĞ¶Ğ¸Ğµ", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 5}
        ],
        "keywords": ["ĞºÑ€Ğ°Ğ±Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚", "crab salad", "Ñ� ĞºÑ€Ğ°Ğ±Ğ¾Ğ²Ñ‹Ğ¼Ğ¸ Ğ¿Ğ°Ğ»Ğ¾Ñ‡ĞºĞ°Ğ¼Ğ¸"]
    },
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ¼ÑƒĞ¶Ñ�ĞºĞ¾Ğ¹ ĞºĞ°Ğ¿Ñ€Ğ¸Ğ·": {
        "name": "ĞœÑƒĞ¶Ñ�ĞºĞ¾Ğ¹ ĞºĞ°Ğ¿Ñ€Ğ¸Ğ·",
        "name_en": ["man's whim salad", "russian layered meat salad"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 12.0, "fat": 17.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ²ĞµÑ‚Ñ‡Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ° Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ°Ñ�", "type": "protein", "percent": 20},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹ Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 10},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 15}
        ],
        "keywords": ["Ğ¼ÑƒĞ¶Ñ�ĞºĞ¾Ğ¹ ĞºĞ°Ğ¿Ñ€Ğ¸Ğ·", "Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚"]
    },
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ°Ñ� Ğ¿Ğ¾Ğ»Ñ�Ğ½Ğ°": {
        "name": "Ğ“Ñ€Ğ¸Ğ±Ğ½Ğ°Ñ� Ğ¿Ğ¾Ğ»Ñ�Ğ½Ğ°",
        "name_en": ["mushroom glade salad", "russian mushroom salad"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 5.0, "fat": 10.0, "carbs": 9.0},
        "ingredients": [
            {"name": "ÑˆĞ°Ğ¼Ğ¿Ğ¸Ğ½ÑŒĞ¾Ğ½Ñ‹ Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ", "type": "vegetable", "percent": 30},
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 20},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 10},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 8},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 7}
        ],
        "keywords": ["Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ°Ñ� Ğ¿Ğ¾Ğ»Ñ�Ğ½Ğ°", "mushroom salad", "Ñ�Ğ»Ğ¾ĞµĞ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚"]
    },
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ‚Ğ¸Ñ„Ñ„Ğ°Ğ½Ğ¸": {
        "name": "Ğ¢Ğ¸Ñ„Ñ„Ğ°Ğ½Ğ¸",
        "name_en": ["tiffany salad", "chicken and grape salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 12.0, "fat": 13.0, "carbs": 10.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 35},
            {"name": "Ğ²Ğ¸Ğ½Ğ¾Ğ³Ñ€Ğ°Ğ´", "type": "fruit", "percent": 25},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 10},
            {"name": "Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğµ Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 8},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 7}
        ],
        "keywords": ["Ñ‚Ğ¸Ñ„Ñ„Ğ°Ğ½Ğ¸", "tiffany", "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ğ²Ğ¸Ğ½Ğ¾Ğ³Ñ€Ğ°Ğ´Ğ¾Ğ¼"]
    },
    "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ²ĞµĞ½Ñ�ĞºĞ¸Ğ¹": {
        "name": "Ğ’ĞµĞ½Ñ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚",
        "name_en": ["viennese salad", "russian layered salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 8.0, "fat": 14.0, "carbs": 9.0},
        "ingredients": [
            {"name": "Ğ²ĞµÑ‚Ñ‡Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 20},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 10},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ", "type": "vegetable", "percent": 7},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 10}
        ],
        "keywords": ["Ğ²ĞµĞ½Ñ�ĞºĞ¸Ğ¹", "viennese", "Ñ�Ğ»Ğ¾ĞµĞ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚"]
    },
    
    # ==================== Ğ’Ğ¢Ğ�Ğ Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� (Ğ�Ğ�Ğ’Ğ«Ğ• ĞŸĞ�Ğ—Ğ˜Ğ¦Ğ˜Ğ˜) ====================
    "Ğ±ĞµÑ„Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ°Ğ½Ğ¾Ğ²": {
        "name": "Ğ‘ĞµÑ„Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ°Ğ½Ğ¾Ğ²",
        "name_en": ["beef stroganoff", "stroganoff"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 12.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 50},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 15},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 5},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ±ĞµÑ„Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ°Ğ½Ğ¾Ğ²", "stroganoff", "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ° Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ"]
    },
    "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ¿Ğ¾Ğ¶Ğ°Ñ€Ñ�ĞºĞ°Ñ�": {
        "name": "ĞšĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹ Ğ¿Ğ¾Ğ¶Ğ°Ñ€Ñ�ĞºĞ¸Ğµ",
        "name_en": ["pozharsky cutlets", "russian breaded chicken cutlets"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 11.0, "carbs": 8.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 60},
            {"name": "Ñ…Ğ»ĞµĞ± Ğ±ĞµĞ»Ñ‹Ğ¹", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 8},
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğµ Ñ�ÑƒÑ…Ğ°Ñ€Ğ¸", "type": "carb", "percent": 7}
        ],
        "keywords": ["Ğ¿Ğ¾Ğ¶Ğ°Ñ€Ñ�ĞºĞ¸Ğµ ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹", "pozharsky cutlets", "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹"]
    },
    "Ğ·Ñ€Ğ°Ğ·Ñ‹ Ğ¼Ñ�Ñ�Ğ½Ñ‹Ğµ": {
        "name": "Ğ—Ñ€Ğ°Ğ·Ñ‹ Ğ¼Ñ�Ñ�Ğ½Ñ‹Ğµ",
        "name_en": ["zrazy", "stuffed meat rolls"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 15.0, "fat": 14.0, "carbs": 7.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 60},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 10},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹", "type": "vegetable", "percent": 8},
            {"name": "Ñ…Ğ»ĞµĞ±", "type": "carb", "percent": 7},
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°", "type": "carb", "percent": 5}
        ],
        "keywords": ["Ğ·Ñ€Ğ°Ğ·Ñ‹", "zrazy", "Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹"]
    },
    "Ğ·Ñ€Ğ°Ğ·Ñ‹ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ñ‹Ğµ": {
        "name": "Ğ—Ñ€Ğ°Ğ·Ñ‹ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ñ‹Ğµ",
        "name_en": ["potato zrazy", "stuffed potato patties"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 5.0, "fat": 5.0, "carbs": 22.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 65},
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹", "type": "vegetable", "percent": 15},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 5}
        ],
        "keywords": ["Ğ·Ñ€Ğ°Ğ·Ñ‹", "potato zrazy", "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ·Ñ€Ğ°Ğ·Ñ‹"]
    },
    "Ğ¿Ğ»Ğ¾Ğ² Ñ�Ğ¾ Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ¾Ğ¹": {
        "name": "ĞŸĞ»Ğ¾Ğ² Ñ�Ğ¾ Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ¾Ğ¹",
        "name_en": ["pork pilaf", "russian style pork pilaf"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 200, "protein": 10.0, "fat": 9.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 45},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 12},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 2}
        ],
        "keywords": ["Ğ¿Ğ»Ğ¾Ğ²", "pilaf", "Ğ¿Ğ»Ğ¾Ğ² Ñ�Ğ¾ Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ¾Ğ¹"]
    },
    "Ğ³ÑƒĞ»Ñ�Ñˆ Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹": {
        "name": "Ğ“ÑƒĞ»Ñ�Ñˆ Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹",
        "name_en": ["beef goulash", "russian style goulash"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 170, "protein": 15.0, "fat": 9.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 50},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 8},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 5},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 7},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ğ³ÑƒĞ»Ñ�Ñˆ", "goulash", "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ° Ğ² Ğ¿Ğ¾Ğ´Ğ»Ğ¸Ğ²Ğµ"]
    },
    "Ğ¿Ğ¾Ğ´Ğ¶Ğ°Ñ€ĞºĞ° Ğ¸Ğ· Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ñ‹": {
        "name": "ĞŸĞ¾Ğ´Ğ¶Ğ°Ñ€ĞºĞ° Ğ¸Ğ· Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ñ‹",
        "name_en": ["pork podzharka", "fried pork with gravy"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 16.0, "fat": 16.0, "carbs": 4.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 70},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 2}
        ],
        "keywords": ["Ğ¿Ğ¾Ğ´Ğ¶Ğ°Ñ€ĞºĞ°", "podzharka", "Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ� Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°"]
    },
    "Ğ¿ĞµÑ‡ĞµĞ½ÑŒ Ğ¿Ğ¾-Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ°Ğ½Ğ¾Ğ²Ñ�ĞºĞ¸": {
        "name": "ĞŸĞµÑ‡ĞµĞ½ÑŒ Ğ¿Ğ¾-Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ°Ğ½Ğ¾Ğ²Ñ�ĞºĞ¸",
        "name_en": ["liver stroganoff", "beef liver in sour cream"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 16.0, "fat": 9.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ� Ğ¿ĞµÑ‡ĞµĞ½ÑŒ", "type": "protein", "percent": 60},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 15},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 5}
        ],
        "keywords": ["Ğ¿ĞµÑ‡ĞµĞ½ÑŒ", "liver", "Ğ¿ĞµÑ‡ĞµĞ½ÑŒ Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ"]
    },
    "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ Ñ�ĞµÑ€Ğ´ĞµÑ‡ĞºĞ¸ Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ": {
        "name": "ĞšÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ Ñ�ĞµÑ€Ğ´ĞµÑ‡ĞºĞ¸ Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ",
        "name_en": ["chicken hearts in sour cream", "stewed chicken hearts"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 14.0, "fat": 10.0, "carbs": 3.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ Ñ�ĞµÑ€Ğ´ĞµÑ‡ĞºĞ¸", "type": "protein", "percent": 65},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 10},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 2}
        ],
        "keywords": ["Ñ�ĞµÑ€Ğ´ĞµÑ‡ĞºĞ¸", "chicken hearts", "Ñ�ÑƒĞ±Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹"]
    },
    "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¿Ğ¾-Ğ´ĞµÑ€ĞµĞ²ĞµĞ½Ñ�ĞºĞ¸": {
        "name": "ĞšĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¿Ğ¾-Ğ´ĞµÑ€ĞµĞ²ĞµĞ½Ñ�ĞºĞ¸",
        "name_en": ["country style potatoes", "russian baked potatoes"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 150, "protein": 3.0, "fat": 5.0, "carbs": 23.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 80},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "ÑƒĞºÑ€Ğ¾Ğ¿", "type": "vegetable", "percent": 3},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "country potatoes", "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ"]
    },
    "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ´Ñ€Ğ°Ğ½Ğ¸ĞºĞ¸": {
        "name": "Ğ”Ñ€Ğ°Ğ½Ğ¸ĞºĞ¸",
        "name_en": ["draniki", "potato pancakes", "belarusian potato pancakes"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 4.0, "fat": 8.0, "carbs": 23.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 70},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 10}
        ],
        "keywords": ["Ğ´Ñ€Ğ°Ğ½Ğ¸ĞºĞ¸", "draniki", "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ¾Ğ»Ğ°Ğ´ÑŒĞ¸"]
    },
    "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ°Ñ� Ğ±Ğ°Ğ±ĞºĞ°": {
        "name": "ĞšĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ°Ñ� Ğ±Ğ°Ğ±ĞºĞ°",
        "name_en": ["kartofelnaya babka", "potato casserole"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 160, "protein": 6.0, "fat": 7.0, "carbs": 18.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 60},
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 20},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 5}
        ],
        "keywords": ["Ğ±Ğ°Ğ±ĞºĞ°", "babka", "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ°Ñ� Ğ·Ğ°Ğ¿ĞµĞºĞ°Ğ½ĞºĞ°"]
    },
    "ĞºĞ°ÑˆĞ° Ğ³Ñ€ĞµÑ‡Ğ½ĞµĞ²Ğ°Ñ� Ñ� Ğ³Ñ€Ğ¸Ğ±Ğ°Ğ¼Ğ¸": {
        "name": "Ğ“Ñ€ĞµÑ‡Ğ½ĞµĞ²Ğ°Ñ� ĞºĞ°ÑˆĞ° Ñ� Ğ³Ñ€Ğ¸Ğ±Ğ°Ğ¼Ğ¸",
        "name_en": ["buckwheat with mushrooms", "kasha with mushrooms"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 5.0, "fat": 4.0, "carbs": 16.0},
        "ingredients": [
            {"name": "Ğ³Ñ€ĞµÑ‡ĞºĞ°", "type": "carb", "percent": 60},
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹", "type": "vegetable", "percent": 25},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 7}
        ],
        "keywords": ["Ğ³Ñ€ĞµÑ‡ĞºĞ°", "buckwheat", "ĞºĞ°ÑˆĞ° Ñ� Ğ³Ñ€Ğ¸Ğ±Ğ°Ğ¼Ğ¸"]
    },
    "ĞºĞ°ÑˆĞ° Ğ¿ÑˆĞµĞ½Ğ½Ğ°Ñ� Ñ� Ñ‚Ñ‹ĞºĞ²Ğ¾Ğ¹": {
        "name": "ĞŸÑˆĞµĞ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ° Ñ� Ñ‚Ñ‹ĞºĞ²Ğ¾Ğ¹",
        "name_en": ["millet porridge with pumpkin", "kasha with pumpkin"],
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 110, "protein": 3.0, "fat": 3.0, "carbs": 18.0},
        "ingredients": [
            {"name": "Ğ¿ÑˆĞµĞ½Ğ¾", "type": "carb", "percent": 40},
            {"name": "Ñ‚Ñ‹ĞºĞ²Ğ°", "type": "vegetable", "percent": 30},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 20},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¿ÑˆĞµĞ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ°", "millet porridge", "Ñ‚Ñ‹ĞºĞ²ĞµĞ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ°"]
    },
    "ĞºĞ°ÑˆĞ° Ğ¿ĞµÑ€Ğ»Ğ¾Ğ²Ğ°Ñ�": {
        "name": "ĞŸĞµÑ€Ğ»Ğ¾Ğ²Ğ°Ñ� ĞºĞ°ÑˆĞ°",
        "name_en": ["pearl barley porridge", "kasha"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 3.0, "fat": 2.0, "carbs": 23.0},
        "ingredients": [
            {"name": "Ğ¿ĞµÑ€Ğ»Ğ¾Ğ²ĞºĞ°", "type": "carb", "percent": 90},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 5}
        ],
        "keywords": ["Ğ¿ĞµÑ€Ğ»Ğ¾Ğ²ĞºĞ°", "pearl barley", "ĞºĞ°ÑˆĞ°"]
    },
    "ĞºĞ°ÑˆĞ° Ğ¾Ğ²Ñ�Ñ�Ğ½Ğ°Ñ� Ğ½Ğ° Ğ¼Ğ¾Ğ»Ğ¾ĞºĞµ": {
        "name": "Ğ�Ğ²Ñ�Ñ�Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ° Ğ½Ğ° Ğ¼Ğ¾Ğ»Ğ¾ĞºĞµ",
        "name_en": ["milk oatmeal", "oatmeal porridge"],
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 100, "protein": 4.0, "fat": 3.0, "carbs": 14.0},
        "ingredients": [
            {"name": "Ğ¾Ğ²Ñ�Ñ�Ğ½Ñ‹Ğµ Ñ…Ğ»Ğ¾Ğ¿ÑŒÑ�", "type": "carb", "percent": 30},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 60},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¾Ğ²Ñ�Ñ�Ğ½ĞºĞ°", "oatmeal", "ĞºĞ°ÑˆĞ°"]
    },
    "Ğ³ÑƒÑ€ÑŒĞµĞ²Ñ�ĞºĞ°Ñ� ĞºĞ°ÑˆĞ°": {
        "name": "Ğ“ÑƒÑ€ÑŒĞµĞ²Ñ�ĞºĞ°Ñ� ĞºĞ°ÑˆĞ°",
        "name_en": ["guryev porridge", "russian semolina dessert"],
        "category": "dessert",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 5.0, "fat": 8.0, "carbs": 22.0},
        "ingredients": [
            {"name": "Ğ¼Ğ°Ğ½Ğ½Ğ°Ñ� ĞºÑ€ÑƒĞ¿Ğ°", "type": "carb", "percent": 30},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 35},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 10},
            {"name": "Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 8},
            {"name": "Ñ�ÑƒÑ…Ğ¾Ñ„Ñ€ÑƒĞºÑ‚Ñ‹", "type": "fruit", "percent": 7},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ³ÑƒÑ€ÑŒĞµĞ²Ñ�ĞºĞ°Ñ� ĞºĞ°ÑˆĞ°", "guryev porridge", "Ğ´ĞµÑ�ĞµÑ€Ñ‚"]
    },
    
    # ==================== Ğ’Ğ«ĞŸĞ•Ğ§ĞšĞ� Ğ˜ Ğ”Ğ•Ğ¡Ğ•Ğ Ğ¢Ğ« ====================
    "Ğ²Ğ°Ñ‚Ñ€ÑƒÑˆĞºĞ° Ñ� Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³Ğ¾Ğ¼": {
        "name": "Ğ’Ğ°Ñ‚Ñ€ÑƒÑˆĞºĞ° Ñ� Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³Ğ¾Ğ¼",
        "name_en": ["vatrushka", "russian cottage cheese bun"],
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 260, "protein": 9.0, "fat": 10.0, "carbs": 34.0},
        "ingredients": [
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶ĞµĞ²Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 55},
            {"name": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "type": "dairy", "percent": 35},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5}
        ],
        "keywords": ["Ğ²Ğ°Ñ‚Ñ€ÑƒÑˆĞºĞ°", "vatrushka", "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ¶Ğ½Ğ°Ñ� Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ°"]
    },
    "ĞºÑƒĞ»ĞµĞ±Ñ�ĞºĞ°": {
        "name": "ĞšÑƒĞ»ĞµĞ±Ñ�ĞºĞ°",
        "name_en": ["kulebyaka", "russian layered pie"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 10.0, "fat": 9.0, "carbs": 25.0},
        "ingredients": [
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶ĞµĞ²Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 50},
            {"name": "Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 20},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 8},
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹", "type": "vegetable", "percent": 7},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["ĞºÑƒĞ»ĞµĞ±Ñ�ĞºĞ°", "kulebyaka", "Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³"]
    },
    "Ñ€Ğ°Ñ�Ñ�Ñ‚ĞµĞ³Ğ°Ğ¹": {
        "name": "Ğ Ğ°Ñ�Ñ�Ñ‚ĞµĞ³Ğ°Ğ¹",
        "name_en": ["rasstegai", "russian open pie"],
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 240, "protein": 9.0, "fat": 10.0, "carbs": 29.0},
        "ingredients": [
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶ĞµĞ²Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 55},
            {"name": "Ñ€Ñ‹Ğ±Ğ°", "type": "protein", "percent": 25},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 10},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ñ€Ğ°Ñ�Ñ�Ñ‚ĞµĞ³Ğ°Ğ¹", "rasstegai", "Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ¶Ğ¾Ğº"]
    },
    "ĞºÑƒÑ€Ğ½Ğ¸Ğº": {
        "name": "ĞšÑƒÑ€Ğ½Ğ¸Ğº",
        "name_en": ["kurnik", "russian chicken pie"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "Ñ�Ğ»Ğ¾ĞµĞ½Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 45},
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 25},
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹", "type": "vegetable", "percent": 10},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 8},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 7},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["ĞºÑƒÑ€Ğ½Ğ¸Ğº", "kurnik", "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³"]
    },
    "ÑˆĞ°Ğ½ÑŒĞ³Ğ°": {
        "name": "Ğ¨Ğ°Ğ½ÑŒĞ³Ğ°",
        "name_en": ["shanga", "northern russian bun"],
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 250, "protein": 6.0, "fat": 10.0, "carbs": 34.0},
        "ingredients": [
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶ĞµĞ²Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 60},
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ", "type": "carb", "percent": 25},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ÑˆĞ°Ğ½ÑŒĞ³Ğ°", "shanga", "Ñ�ĞµĞ²ĞµÑ€Ğ½Ğ°Ñ� Ğ²Ñ‹Ğ¿ĞµÑ‡ĞºĞ°"]
    },
    "Ñ�Ğ¾Ñ‡Ğ½Ğ¸Ğº Ñ� Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³Ğ¾Ğ¼": {
        "name": "Ğ¡Ğ¾Ñ‡Ğ½Ğ¸Ğº Ñ� Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³Ğ¾Ğ¼",
        "name_en": ["sochnik", "russian curd filled pastry"],
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 270, "protein": 8.0, "fat": 11.0, "carbs": 35.0},
        "ingredients": [
            {"name": "Ğ¿ĞµÑ�Ğ¾Ñ‡Ğ½Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 55},
            {"name": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "type": "dairy", "percent": 30},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 5}
        ],
        "keywords": ["Ñ�Ğ¾Ñ‡Ğ½Ğ¸Ğº", "sochnik", "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ¶Ğ½Ğ°Ñ� Ğ²Ñ‹Ğ¿ĞµÑ‡ĞºĞ°"]
    },
    "ĞºĞ¾Ğ²Ñ€Ğ¸Ğ¶ĞºĞ° Ğ¼ĞµĞ´Ğ¾Ğ²Ğ°Ñ�": {
        "name": "ĞšĞ¾Ğ²Ñ€Ğ¸Ğ¶ĞºĞ° Ğ¼ĞµĞ´Ğ¾Ğ²Ğ°Ñ�",
        "name_en": ["kovrizhka", "russian honey cake"],
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 320, "protein": 4.0, "fat": 9.0, "carbs": 55.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 45},
            {"name": "Ğ¼ĞµĞ´", "type": "sugar", "percent": 30},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 8},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 7},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5},
            {"name": "Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 5}
        ],
        "keywords": ["ĞºĞ¾Ğ²Ñ€Ğ¸Ğ¶ĞºĞ°", "kovrizhka", "Ğ¼ĞµĞ´Ğ¾Ğ²Ğ¸Ğº", "Ğ¿Ñ€Ñ�Ğ½Ğ¸Ğº"]
    },
    "Ğ¿Ñ‹ÑˆĞºĞ¸ Ğ¼Ğ¾Ñ�ĞºĞ¾Ğ²Ñ�ĞºĞ¸Ğµ": {
        "name": "ĞŸÑ‹ÑˆĞºĞ¸ Ğ¼Ğ¾Ñ�ĞºĞ¾Ğ²Ñ�ĞºĞ¸Ğµ",
        "name_en": ["pushki", "moscow doughnuts"],
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 310, "protein": 5.0, "fat": 15.0, "carbs": 38.0},
        "ingredients": [
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶ĞµĞ²Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 60},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 30},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ğ°Ñ� Ğ¿ÑƒĞ´Ñ€Ğ°", "type": "carb", "percent": 10}
        ],
        "keywords": ["Ğ¿Ñ‹ÑˆĞºĞ¸", "pushki", "Ğ¿Ğ¾Ğ½Ñ‡Ğ¸ĞºĞ¸", "Ğ¼Ğ¾Ñ�ĞºĞ¾Ğ²Ñ�ĞºĞ¸Ğµ Ğ¿Ñ‹ÑˆĞºĞ¸"]
    },
    "Ñ…Ğ²Ğ¾Ñ€Ğ¾Ñ�Ñ‚": {
        "name": "Ğ¥Ğ²Ğ¾Ñ€Ğ¾Ñ�Ñ‚",
        "name_en": ["khvorost", "russian twisted crisps"],
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 340, "protein": 5.0, "fat": 18.0, "carbs": 40.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 45},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 10},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 20}
        ],
        "keywords": ["Ñ…Ğ²Ğ¾Ñ€Ğ¾Ñ�Ñ‚", "khvorost", "Ğ¿ĞµÑ‡ĞµĞ½ÑŒĞµ"]
    },
    "Ğ¾Ñ€ĞµÑˆĞºĞ¸ Ñ�Ğ¾ Ñ�Ğ³ÑƒÑ‰ĞµĞ½ĞºĞ¾Ğ¹": {
        "name": "Ğ�Ñ€ĞµÑˆĞºĞ¸ Ñ�Ğ¾ Ñ�Ğ³ÑƒÑ‰ĞµĞ½ĞºĞ¾Ğ¹",
        "name_en": ["oreshki", "russian nut cookies with condensed milk"],
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 380, "protein": 6.0, "fat": 18.0, "carbs": 48.0},
        "ingredients": [
            {"name": "Ğ¿ĞµÑ�Ğ¾Ñ‡Ğ½Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 60},
            {"name": "Ñ�Ğ³ÑƒÑ‰ĞµĞ½Ğ½Ğ¾Ğµ Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾ Ğ²Ğ°Ñ€ĞµĞ½Ğ¾Ğµ", "type": "dairy", "percent": 35},
            {"name": "Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğµ Ğ¾Ñ€ĞµÑ…Ğ¸", "type": "protein", "percent": 5}
        ],
        "keywords": ["Ğ¾Ñ€ĞµÑˆĞºĞ¸", "oreshki", "Ğ¿ĞµÑ‡ĞµĞ½ÑŒĞµ Ñ�Ğ¾ Ñ�Ğ³ÑƒÑ‰ĞµĞ½ĞºĞ¾Ğ¹"]
    },
    
    # ==================== Ğ—Ğ�ĞšĞ£Ğ¡ĞšĞ˜ ====================
    "Ñ�Ñ‚ÑƒĞ´ĞµĞ½ÑŒ Ğ³Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹": {
        "name": "Ğ¡Ñ‚ÑƒĞ´ĞµĞ½ÑŒ Ğ³Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹",
        "name_en": ["beef studen", "russian beef aspic"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 160, "protein": 14.0, "fat": 11.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒĞ¸ Ğ½Ğ¾Ğ¶ĞºĞ¸", "type": "protein", "percent": 50},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 30},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 10}
        ],
        "keywords": ["Ñ�Ñ‚ÑƒĞ´ĞµĞ½ÑŒ", "studen", "Ñ…Ğ¾Ğ»Ğ¾Ğ´ĞµÑ†", "aspic"]
    },
    "Ğ·Ğ°Ğ»Ğ¸Ğ²Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°": {
        "name": "Ğ—Ğ°Ğ»Ğ¸Ğ²Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°",
        "name_en": ["jellied fish", "russian fish aspic"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 12.0, "fat": 5.0, "carbs": 4.0},
        "ingredients": [
            {"name": "Ñ€Ñ‹Ğ±Ğ°", "type": "protein", "percent": 50},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½ Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹", "type": "liquid", "percent": 35},
            {"name": "Ğ¶ĞµĞ»Ğ°Ñ‚Ğ¸Ğ½", "type": "other", "percent": 5},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 5}
        ],
        "keywords": ["Ğ·Ğ°Ğ»Ğ¸Ğ²Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°", "jellied fish", "Ñ€Ñ‹Ğ±Ğ½Ğ¾Ğµ Ğ·Ğ°Ğ»Ğ¸Ğ²Ğ½Ğ¾Ğµ"]
    },
    "Ğ±ÑƒÑ‚ĞµÑ€Ğ±Ñ€Ğ¾Ğ´Ñ‹ Ñ�Ğ¾ ÑˆĞ¿Ñ€Ğ¾Ñ‚Ğ°Ğ¼Ğ¸": {
        "name": "Ğ‘ÑƒÑ‚ĞµÑ€Ğ±Ñ€Ğ¾Ğ´Ñ‹ Ñ�Ğ¾ ÑˆĞ¿Ñ€Ğ¾Ñ‚Ğ°Ğ¼Ğ¸",
        "name_en": ["sprat sandwiches", "russian sprats on bread"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 250, "protein": 10.0, "fat": 14.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ñ…Ğ»ĞµĞ± Ğ±ĞµĞ»Ñ‹Ğ¹", "type": "carb", "percent": 45},
            {"name": "ÑˆĞ¿Ñ€Ğ¾Ñ‚Ñ‹", "type": "protein", "percent": 30},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 5},
            {"name": "Ğ·ĞµĞ»ĞµĞ½ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 5}
        ],
        "keywords": ["ÑˆĞ¿Ñ€Ğ¾Ñ‚Ñ‹", "sprats", "Ğ±ÑƒÑ‚ĞµÑ€Ğ±Ñ€Ğ¾Ğ´Ñ‹", "Ğ¿Ñ€Ğ°Ğ·Ğ´Ğ½Ğ¸Ñ‡Ğ½Ğ°Ñ� Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°"]
    },
    "Ñ�Ğ¹Ñ†Ğ° Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ": {
        "name": "Ğ¯Ğ¹Ñ†Ğ° Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ",
        "name_en": ["stuffed eggs", "russian deviled eggs"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 10.0, "fat": 14.0, "carbs": 3.0},
        "ingredients": [
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 60},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 15},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 10},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ·ĞµĞ»ĞµĞ½ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ğ¿ĞµÑ‡ĞµĞ½ÑŒ Ñ‚Ñ€ĞµÑ�ĞºĞ¸", "type": "protein", "percent": 5}
        ],
        "keywords": ["Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ñ�Ğ¹Ñ†Ğ°", "stuffed eggs", "Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°"]
    },
    "Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ Ğ³Ñ€ÑƒĞ·Ğ´Ğ¸": {
        "name": "Ğ¡Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ Ğ³Ñ€ÑƒĞ·Ğ´Ğ¸",
        "name_en": ["salted mushrooms", "russian salted milk caps"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 30, "protein": 2.0, "fat": 0.5, "carbs": 4.0},
        "ingredients": [
            {"name": "Ğ³Ñ€ÑƒĞ·Ğ´Ğ¸ Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ", "type": "vegetable", "percent": 85},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ³Ñ€ÑƒĞ·Ğ´Ğ¸", "salted mushrooms", "Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ°Ñ� Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°"]
    },
    "ĞºĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°": {
        "name": "ĞšĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°",
        "name_en": ["sauerkraut", "russian fermented cabbage"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 25, "protein": 1.5, "fat": 0.5, "carbs": 4.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° Ğ±ĞµĞ»Ğ¾ĞºĞ¾Ñ‡Ğ°Ğ½Ğ½Ğ°Ñ�", "type": "vegetable", "percent": 85},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 5},
            {"name": "ĞºĞ»Ñ�ĞºĞ²Ğ°", "type": "fruit", "percent": 2}
        ],
        "keywords": ["ĞºĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "sauerkraut", "Ñ�Ğ¾Ğ»ĞµĞ½ÑŒÑ�"]
    },
    "Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹": {
        "name": "ĞœĞ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹",
        "name_en": ["pickled cucumbers", "russian pickles"],
        "category": "side",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 20, "protein": 0.5, "fat": 0.1, "carbs": 4.0},
        "ingredients": [
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹", "type": "vegetable", "percent": 90},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "ÑƒĞºÑ€Ğ¾Ğ¿", "type": "vegetable", "percent": 3},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 4}
        ],
        "keywords": ["Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹", "pickles", "Ñ�Ğ¾Ğ»ĞµĞ½ÑŒÑ�"]
    },
    
    # ==================== Ğ�Ğ�ĞŸĞ˜Ğ¢ĞšĞ˜ ====================
    "ĞºĞ²Ğ°Ñ� Ñ…Ğ»ĞµĞ±Ğ½Ñ‹Ğ¹": {
        "name": "ĞšĞ²Ğ°Ñ� Ñ…Ğ»ĞµĞ±Ğ½Ñ‹Ğ¹",
        "name_en": ["kvass", "russian rye bread drink"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 30, "protein": 0.5, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ€Ğ¶Ğ°Ğ½Ğ¾Ğ¹ Ñ…Ğ»ĞµĞ±", "type": "carb", "percent": 30},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 65},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 4},
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶Ğ¸", "type": "other", "percent": 1}
        ],
        "keywords": ["ĞºĞ²Ğ°Ñ�", "kvass", "Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğ¹ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº"]
    },
    "Ğ¼Ğ¾Ñ€Ñ� ĞºĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹": {
        "name": "ĞœĞ¾Ñ€Ñ� ĞºĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹",
        "name_en": ["cranberry morse", "russian cranberry drink"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 40, "protein": 0.1, "fat": 0.1, "carbs": 9.0},
        "ingredients": [
            {"name": "ĞºĞ»Ñ�ĞºĞ²Ğ°", "type": "fruit", "percent": 20},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 70},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 10}
        ],
        "keywords": ["Ğ¼Ğ¾Ñ€Ñ�", "morse", "ĞºĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ¼Ğ¾Ñ€Ñ�", "cranberry juice"]
    },
    "Ğ¼Ğ¾Ñ€Ñ� Ğ±Ñ€ÑƒÑ�Ğ½Ğ¸Ñ‡Ğ½Ñ‹Ğ¹": {
        "name": "ĞœĞ¾Ñ€Ñ� Ğ±Ñ€ÑƒÑ�Ğ½Ğ¸Ñ‡Ğ½Ñ‹Ğ¹",
        "name_en": ["lingonberry morse", "russian lingonberry drink"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 35, "protein": 0.1, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ±Ñ€ÑƒÑ�Ğ½Ğ¸ĞºĞ°", "type": "fruit", "percent": 20},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 72},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 8}
        ],
        "keywords": ["Ğ¼Ğ¾Ñ€Ñ�", "morse", "Ğ±Ñ€ÑƒÑ�Ğ½Ğ¸Ñ‡Ğ½Ñ‹Ğ¹ Ğ¼Ğ¾Ñ€Ñ�", "lingonberry drink"]
    },
    "ĞºĞ¾Ğ¼Ğ¿Ğ¾Ñ‚ Ğ¸Ğ· Ñ�ÑƒÑ…Ğ¾Ñ„Ñ€ÑƒĞºÑ‚Ğ¾Ğ²": {
        "name": "ĞšĞ¾Ğ¼Ğ¿Ğ¾Ñ‚ Ğ¸Ğ· Ñ�ÑƒÑ…Ğ¾Ñ„Ñ€ÑƒĞºÑ‚Ğ¾Ğ²",
        "name_en": ["dried fruit compote", "russian kompot"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 0.3, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "Ñ�ÑƒÑ…Ğ¾Ñ„Ñ€ÑƒĞºÑ‚Ñ‹", "type": "fruit", "percent": 20},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 75},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5}
        ],
        "keywords": ["ĞºĞ¾Ğ¼Ğ¿Ğ¾Ñ‚", "kompot", "ÑƒĞ·Ğ²Ğ°Ñ€", "dried fruit compote"]
    },
    "Ñ�Ğ±Ğ¸Ñ‚ĞµĞ½ÑŒ": {
        "name": "Ğ¡Ğ±Ğ¸Ñ‚ĞµĞ½ÑŒ",
        "name_en": ["sbiten", "russian honey drink"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 60, "protein": 0.2, "fat": 0.1, "carbs": 14.0},
        "ingredients": [
            {"name": "Ğ¼ĞµĞ´", "type": "sugar", "percent": 15},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 80},
            {"name": "Ğ¿Ñ€Ñ�Ğ½Ğ¾Ñ�Ñ‚Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ñ�Ğ±Ğ¸Ñ‚ĞµĞ½ÑŒ", "sbiten", "Ğ¼ĞµĞ´Ğ¾Ğ²Ñ‹Ğ¹ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº"]
    },
    "ĞºĞ¸Ñ�ĞµĞ»ÑŒ ĞºĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹": {
        "name": "ĞšĞ¸Ñ�ĞµĞ»ÑŒ ĞºĞ»Ñ�ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¹",
        "name_en": ["cranberry kissel", "russian fruit jelly drink"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 60, "protein": 0.2, "fat": 0.1, "carbs": 14.0},
        "ingredients": [
            {"name": "ĞºĞ»Ñ�ĞºĞ²Ğ°", "type": "fruit", "percent": 15},
            {"name": "ĞºÑ€Ğ°Ñ…Ğ¼Ğ°Ğ»", "type": "carb", "percent": 8},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 10},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 67}
        ],
        "keywords": ["ĞºĞ¸Ñ�ĞµĞ»ÑŒ", "kissel", "Ñ�Ğ³Ğ¾Ğ´Ğ½Ñ‹Ğ¹ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº"]
    },

    # =============================================================================
    # ğŸ‡·ğŸ‡º Ğ�Ğ�Ğ’Ğ«Ğ• Ğ Ğ�Ğ¡Ğ¡Ğ˜Ğ™Ğ¡ĞšĞ˜Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� (ĞŸĞ Ğ�ĞŸĞ£Ğ©Ğ•Ğ�Ğ�Ğ«Ğ• Ğ’ ĞŸĞ Ğ�Ğ¨Ğ›Ğ«Ğ™ Ğ Ğ�Ğ—)
    # =============================================================================
    
    # ==================== Ğ Ğ•Ğ”ĞšĞ˜Ğ• Ğ˜ Ğ¡Ğ¢Ğ�Ğ Ğ˜Ğ�Ğ�Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� ====================
    "Ğ²Ğ¸Ğ·Ğ¸Ğ³Ğ°": {
        "name": "Ğ’Ğ¸Ğ·Ğ¸Ğ³Ğ° (Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ²Ñ�Ğ·Ğ¸Ğ³Ğ¾Ğ¹)",
        "name_en": ["viziga", "dried sturgeon spinal cord pie"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 15.0, "fat": 8.0, "carbs": 22.0},
        "ingredients": [
            {"name": "Ğ²Ñ�Ğ·Ğ¸Ğ³Ğ°", "type": "protein", "percent": 20},
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶ĞµĞ²Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 50},
            {"name": "Ñ€Ğ¸Ñ�", "type": "carb", "percent": 15},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 8},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 7}
        ],
        "keywords": ["Ğ²Ğ¸Ğ·Ğ¸Ğ³Ğ°", "Ğ²Ñ�Ğ·Ğ¸Ğ³Ğ°", "Ğ¾Ñ�ĞµÑ‚Ñ€Ğ¾Ğ²Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³", "viziga", "Ñ�Ñ‚Ğ°Ñ€Ğ¸Ğ½Ğ½Ğ¾Ğµ Ğ±Ğ»Ñ�Ğ´Ğ¾"]
    },
    "Ğ³Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹ Ñ€ÑƒĞ±ĞµÑ†": {
        "name": "Ğ“Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹ Ñ€ÑƒĞ±ĞµÑ†",
        "name_en": ["tripe", "russian beef tripe"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 15.0, "fat": 8.0, "carbs": 3.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹ Ñ€ÑƒĞ±ĞµÑ†", "type": "protein", "percent": 70},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 12},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ñ€ÑƒĞ±ĞµÑ†", "tripe", "Ğ¿Ğ¾Ñ‚Ñ€Ğ¾Ñ…Ğ°", "Ñ�ÑƒĞ±Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹"]
    },
    "Ğ²ĞµĞºĞ¾ÑˆĞ½Ğ¸ĞºĞ¸": {
        "name": "Ğ’ĞµĞºĞ¾ÑˆĞ½Ğ¸ĞºĞ¸",
        "name_en": ["vekoshniki", "russian potato pancakes with meat"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 9.0, "fat": 8.0, "carbs": 21.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 50},
            {"name": "Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 25},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 7}
        ],
        "keywords": ["Ğ²ĞµĞºĞ¾ÑˆĞ½Ğ¸ĞºĞ¸", "vekoshniki", "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ¾Ğ»Ğ°Ğ´ÑŒĞ¸ Ñ� Ğ¼Ñ�Ñ�Ğ¾Ğ¼"]
    },
    "ĞºĞ°Ğ»ÑŒÑ�": {
        "name": "ĞšĞ°Ğ»ÑŒÑ� Ñ€Ñ‹Ğ±Ğ½Ğ°Ñ�",
        "name_en": ["kalya", "russian pickle fish soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 60, "protein": 5.0, "fat": 2.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ñ€Ñ‹Ğ±Ğ°", "type": "protein", "percent": 25},
            {"name": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹ Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğµ", "type": "vegetable", "percent": 15},
            {"name": "Ñ€Ğ°Ñ�Ñ�Ğ¾Ğ» Ğ¾Ğ³ÑƒÑ€ĞµÑ‡Ğ½Ñ‹Ğ¹", "type": "liquid", "percent": 20},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 7},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 25}
        ],
        "keywords": ["ĞºĞ°Ğ»ÑŒÑ�", "kalya", "Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿ Ñ� Ñ€Ğ°Ñ�Ñ�Ğ¾Ğ»Ğ¾Ğ¼"]
    },
    "ĞºÑƒĞ½Ğ´Ñ�Ğ¼Ñ‹": {
        "name": "ĞšÑƒĞ½Ğ´Ñ�Ğ¼Ñ‹",
        "name_en": ["kundyumy", "russian mushroom dumplings"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 5.0, "fat": 6.0, "carbs": 27.0},
        "ingredients": [
            {"name": "Ğ³Ñ€Ğ¸Ğ±Ñ‹ Ğ»ĞµÑ�Ğ½Ñ‹Ğµ", "type": "vegetable", "percent": 30},
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 45},
            {"name": "Ğ³Ñ€ĞµÑ‡ĞºĞ°", "type": "carb", "percent": 10},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 7}
        ],
        "keywords": ["ĞºÑƒĞ½Ğ´Ñ�Ğ¼Ñ‹", "kundyumy", "Ğ¿Ğ¾Ñ�Ñ‚Ğ½Ñ‹Ğµ Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸", "Ğ³Ñ€Ğ¸Ğ±Ğ½Ñ‹Ğµ Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸"]
    },
    
    # ==================== Ğ”Ğ˜Ğ§Ğ¬ Ğ˜ Ğ�Ğ¥Ğ�Ğ¢Ğ�Ğ˜Ğ§Ğ¬Ğ˜ Ğ‘Ğ›Ğ®Ğ”Ğ� ====================
    "ĞºÑƒÑ€Ğ¾Ğ¿Ğ°Ñ‚ĞºĞ¸ Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ": {
        "name": "ĞšÑƒÑ€Ğ¾Ğ¿Ğ°Ñ‚ĞºĞ¸ Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ",
        "name_en": ["partridge in sour cream", "russian partridge"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 22.0, "fat": 11.0, "carbs": 2.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¾Ğ¿Ğ°Ñ‚ĞºĞ°", "type": "protein", "percent": 60},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 25},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["ĞºÑƒÑ€Ğ¾Ğ¿Ğ°Ñ‚ĞºĞ¸", "partridge", "Ğ´Ğ¸Ñ‡ÑŒ", "Ğ¾Ñ…Ğ¾Ñ‚Ğ°"]
    },
    "Ñ€Ñ�Ğ±Ñ‡Ğ¸ĞºĞ¸": {
        "name": "Ğ Ñ�Ğ±Ñ‡Ğ¸ĞºĞ¸ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğµ",
        "name_en": ["fried hazel grouse", "russian game birds"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 180, "protein": 23.0, "fat": 9.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ñ€Ñ�Ğ±Ñ‡Ğ¸Ğº", "type": "protein", "percent": 80},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 15},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 5}
        ],
        "keywords": ["Ñ€Ñ�Ğ±Ñ‡Ğ¸ĞºĞ¸", "hazel grouse", "Ğ´Ğ¸Ñ‡ÑŒ"]
    },
    "Ñ‚ĞµÑ‚ĞµÑ€ĞµĞ²": {
        "name": "Ğ¢ĞµÑ‚ĞµÑ€ĞµĞ² Ñ‚ÑƒÑˆĞµĞ½Ñ‹Ğ¹",
        "name_en": ["stewed black grouse", "russian game"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 190, "protein": 21.0, "fat": 11.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ‚ĞµÑ€ĞµĞ²", "type": "protein", "percent": 65},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 12},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ñ‚ĞµÑ‚ĞµÑ€ĞµĞ²", "black grouse", "Ğ´Ğ¸Ñ‡ÑŒ"]
    },
    "Ğ·Ğ°Ñ�Ñ† Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ": {
        "name": "Ğ—Ğ°Ñ�Ñ† Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ",
        "name_en": ["hare in sour cream", "russian hare stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 24.0, "fat": 8.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ·Ğ°Ğ¹Ñ‡Ğ°Ñ‚Ğ¸Ğ½Ğ°", "type": "protein", "percent": 65},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["Ğ·Ğ°Ñ�Ñ†", "hare", "Ğ´Ğ¸Ñ‡ÑŒ"]
    },
    
    # ==================== Ğ Ğ«Ğ‘Ğ�Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� ====================
    "Ñ�Ñ‚ĞµÑ€Ğ»Ñ�Ğ´ÑŒ Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�": {
        "name": "Ğ¡Ñ‚ĞµÑ€Ğ»Ñ�Ğ´ÑŒ, Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ� Ğ² Ñ�Ğ¾Ğ»Ğ¸",
        "name_en": ["sterlet baked in salt", "russian sterlet"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 150, "protein": 18.0, "fat": 8.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ñ�Ñ‚ĞµÑ€Ğ»Ñ�Ğ´ÑŒ", "type": "protein", "percent": 70},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ ĞºÑ€ÑƒĞ¿Ğ½Ğ°Ñ�", "type": "other", "percent": 25},
            {"name": "Ñ�Ğ¸Ñ‡Ğ½Ñ‹Ğ¹ Ğ±ĞµĞ»Ğ¾Ğº", "type": "protein", "percent": 5}
        ],
        "keywords": ["Ñ�Ñ‚ĞµÑ€Ğ»Ñ�Ğ´ÑŒ", "sterlet", "Ğ¾Ñ�ĞµÑ‚Ñ€Ğ¾Ğ²Ñ‹Ğµ", "Ñ†Ğ°Ñ€Ñ�ĞºĞ°Ñ� Ñ€Ñ‹Ğ±Ğ°"]
    },
    "ĞºĞ°Ñ€Ğ°Ñ�Ğ¸ Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ": {
        "name": "ĞšĞ°Ñ€Ğ°Ñ�Ğ¸ Ğ² Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğµ",
        "name_en": ["crucian carp in sour cream", "russian carp"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 160, "protein": 16.0, "fat": 9.0, "carbs": 3.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ğ°Ñ�ÑŒ", "type": "protein", "percent": 65},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 25},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 2}
        ],
        "keywords": ["ĞºĞ°Ñ€Ğ°Ñ�Ğ¸", "crucian carp", "Ñ€ĞµÑ‡Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°", "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°"]
    },
    "Ğ½Ğ°Ğ»Ğ¸Ğ¼ÑŒÑ� Ğ¿ĞµÑ‡ĞµĞ½ÑŒ": {
        "name": "ĞŸĞµÑ‡ĞµĞ½ÑŒ Ğ½Ğ°Ğ»Ğ¸Ğ¼Ğ°",
        "name_en": ["burbot liver", "russian delicacy"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 280, "protein": 12.0, "fat": 24.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ¿ĞµÑ‡ĞµĞ½ÑŒ Ğ½Ğ°Ğ»Ğ¸Ğ¼Ğ°", "type": "protein", "percent": 85},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 7}
        ],
        "keywords": ["Ğ½Ğ°Ğ»Ğ¸Ğ¼", "burbot liver", "Ğ´ĞµĞ»Ğ¸ĞºĞ°Ñ‚ĞµÑ�"]
    },
    "Ñ‰ÑƒĞºĞ° Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ�": {
        "name": "Ğ©ÑƒĞºĞ° Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ�",
        "name_en": ["stuffed pike", "russian gefilte fish"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 130, "protein": 15.0, "fat": 5.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ‰ÑƒĞºĞ°", "type": "protein", "percent": 60},
            {"name": "Ñ…Ğ»ĞµĞ± Ğ±ĞµĞ»Ñ‹Ğ¹", "type": "carb", "percent": 15},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 8},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 7}
        ],
        "keywords": ["Ñ‰ÑƒĞºĞ°", "pike", "Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°"]
    },
    "Ñ�Ğ¸Ğ³ Ğ·Ğ°Ğ»Ğ¸Ğ²Ğ½Ğ¾Ğ¹": {
        "name": "Ğ¡Ğ¸Ğ³ Ğ·Ğ°Ğ»Ğ¸Ğ²Ğ½Ğ¾Ğ¹",
        "name_en": ["jellied whitefish", "russian fish aspic"],
        "category": "appetizer",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 110, "protein": 13.0, "fat": 5.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ñ�Ğ¸Ğ³", "type": "protein", "percent": 50},
            {"name": "Ğ±ÑƒĞ»ÑŒĞ¾Ğ½ Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹", "type": "liquid", "percent": 35},
            {"name": "Ğ¶ĞµĞ»Ğ°Ñ‚Ğ¸Ğ½", "type": "other", "percent": 5},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 5},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 5}
        ],
        "keywords": ["Ñ�Ğ¸Ğ³", "whitefish", "Ğ·Ğ°Ğ»Ğ¸Ğ²Ğ½Ğ¾Ğµ"]
    },
    
    # ==================== ĞšĞ�Ğ¨Ğ˜ (Ğ�Ğ�Ğ’Ğ«Ğ•) ====================
    "Ğ¿Ğ¾Ğ»Ğ±Ğ° Ñ� ĞºÑƒÑ€ĞºÑƒĞ¼Ğ¾Ğ¹": {
        "name": "ĞŸĞ¾Ğ»Ğ±Ğ° Ñ� ĞºÑƒÑ€ĞºÑƒĞ¼Ğ¾Ğ¹",
        "name_en": ["spelt with turmeric", "russian ancient grain"],
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 130, "protein": 5.0, "fat": 2.5, "carbs": 23.0},
        "ingredients": [
            {"name": "Ğ¿Ğ¾Ğ»Ğ±Ğ°", "type": "carb", "percent": 85},
            {"name": "ĞºÑƒÑ€ĞºÑƒĞ¼Ğ°", "type": "spice", "percent": 2},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 8},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 5}
        ],
        "keywords": ["Ğ¿Ğ¾Ğ»Ğ±Ğ°", "spelt", "Ğ´Ñ€ĞµĞ²Ğ½Ñ�Ñ� ĞºÑ€ÑƒĞ¿Ğ°"]
    },
    "Ğ³Ğ¾Ñ€Ğ¾Ñ…Ğ¾Ğ²Ğ°Ñ� ĞºĞ°ÑˆĞ°": {
        "name": "Ğ“Ğ¾Ñ€Ğ¾Ñ…Ğ¾Ğ²Ğ°Ñ� ĞºĞ°ÑˆĞ°",
        "name_en": ["pea porridge", "russian pea mash"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 7.0, "fat": 2.0, "carbs": 18.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ñ€Ğ¾Ñ… ĞºĞ¾Ğ»Ğ¾Ñ‚Ñ‹Ğ¹", "type": "protein", "percent": 80},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ", "type": "fat", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ğ³Ğ¾Ñ€Ğ¾Ñ…Ğ¾Ğ²Ğ°Ñ� ĞºĞ°ÑˆĞ°", "pea porridge"]
    },
    "ĞºÑ€ÑƒĞ¿ĞµĞ½Ğ¸Ğº Ğ¸Ğ· Ğ¿ÑˆĞµĞ½Ğ°": {
        "name": "ĞšÑ€ÑƒĞ¿ĞµĞ½Ğ¸Ğº Ğ¸Ğ· Ğ¿ÑˆĞµĞ½Ğ° Ñ� Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³Ğ¾Ğ¼",
        "name_en": ["millet krupennik", "millet cottage cheese casserole"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 160, "protein": 7.0, "fat": 5.0, "carbs": 22.0},
        "ingredients": [
            {"name": "Ğ¿ÑˆĞµĞ½Ğ¾", "type": "carb", "percent": 40},
            {"name": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "type": "dairy", "percent": 30},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 10},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 10},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ĞºÑ€ÑƒĞ¿ĞµĞ½Ğ¸Ğº", "krupennik", "Ğ¿ÑˆĞµĞ½Ğ½Ğ°Ñ� Ğ·Ğ°Ğ¿ĞµĞºĞ°Ğ½ĞºĞ°"]
    },
    "Ğ¼Ğ°Ğ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ° Ñ� Ğ³Ñ€ÑƒÑˆĞµĞ¹": {
        "name": "ĞœĞ°Ğ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ° Ñ� Ğ³Ñ€ÑƒÑˆĞµĞ¹",
        "name_en": ["semolina with pear", "russian breakfast"],
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 4.0, "fat": 3.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ğ¼Ğ°Ğ½Ğ½Ğ°Ñ� ĞºÑ€ÑƒĞ¿Ğ°", "type": "carb", "percent": 25},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 50},
            {"name": "Ğ³Ñ€ÑƒÑˆĞ°", "type": "fruit", "percent": 15},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["Ğ¼Ğ°Ğ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ°", "semolina", "Ğ·Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº"]
    },
    
    # ==================== ĞœĞ¯Ğ¡Ğ�Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� (Ğ�Ğ�Ğ’Ğ«Ğ•) ====================
    "Ğ¾ĞºĞ¾Ñ€Ğ¾Ğº Ñ�Ğ²Ğ¸Ğ½Ğ¾Ğ¹ Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹": {
        "name": "Ğ�ĞºĞ¾Ñ€Ğ¾Ğº Ñ�Ğ²Ğ¸Ğ½Ğ¾Ğ¹, Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹ ĞºÑƒÑ�ĞºĞ¾Ğ¼",
        "name_en": ["baked ham", "russian baked pork"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 260, "protein": 22.0, "fat": 19.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¾Ğ¹ Ğ¾ĞºĞ¾Ñ€Ğ¾Ğº", "type": "protein", "percent": 90},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ğ¾ĞºĞ¾Ñ€Ğ¾Ğº", "ham", "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ� Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°"]
    },
    "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ° Ñ� ĞºĞ²Ğ°ÑˆĞµĞ½Ğ¾Ğ¹ ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ¾Ğ¹": {
        "name": "Ğ¡Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ° Ñ� ĞºĞ²Ğ°ÑˆĞµĞ½Ğ¾Ğ¹ ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ¾Ğ¹ Ğ² Ğ³Ğ¾Ñ€ÑˆĞ¾Ñ‡ĞºĞµ",
        "name_en": ["pork with sauerkraut", "russian pot roast"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 200, "protein": 15.0, "fat": 12.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 45},
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° ĞºĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ�", "type": "vegetable", "percent": 35},
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 7},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ° Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ¾Ğ¹", "Ğ³Ğ¾Ñ€ÑˆĞ¾Ñ‡ĞµĞº", "pork with sauerkraut"]
    },
    "Ñ‚ĞµĞ»Ñ�Ñ‚Ğ¸Ğ½Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�": {
        "name": "Ğ¢ĞµĞ»Ñ�Ñ‚Ğ¸Ğ½Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�",
        "name_en": ["roasted veal", "russian veal"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 180, "protein": 24.0, "fat": 9.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ñ‚ĞµĞ»Ñ�Ñ‚Ğ¸Ğ½Ğ°", "type": "protein", "percent": 85},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ€Ğ¾Ğ·Ğ¼Ğ°Ñ€Ğ¸Ğ½", "type": "spice", "percent": 3},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ", "type": "fat", "percent": 7}
        ],
        "keywords": ["Ñ‚ĞµĞ»Ñ�Ñ‚Ğ¸Ğ½Ğ°", "veal", "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾"]
    },
    
    # ==================== Ğ’Ğ«ĞŸĞ•Ğ§ĞšĞ� (Ğ�Ğ�Ğ’Ğ«Ğ•) ====================
    "ĞºĞ°Ğ»Ğ¸Ñ‚ĞºĞ¸": {
        "name": "ĞšĞ°Ğ»Ğ¸Ñ‚ĞºĞ¸",
        "name_en": ["kalitki", "karelian open pies"],
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 210, "protein": 6.0, "fat": 7.0, "carbs": 31.0},
        "ingredients": [
            {"name": "Ñ€Ğ¶Ğ°Ğ½Ğ¾Ğµ Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 55},
            {"name": "Ğ¿ÑˆĞµĞ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ°", "type": "carb", "percent": 25},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ĞºĞ°Ğ»Ğ¸Ñ‚ĞºĞ¸", "kalitki", "ĞºĞ°Ñ€ĞµĞ»ÑŒÑ�ĞºĞ¸Ğµ Ğ¿Ğ¸Ñ€Ğ¾Ğ¶ĞºĞ¸"]
    },
    "Ğ²ĞµÑ€Ğ³ÑƒĞ½Ñ‹": {
        "name": "Ğ’ĞµÑ€Ğ³ÑƒĞ½Ñ‹",
        "name_en": ["verguns", "russian twisted pastries"],
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 330, "protein": 5.0, "fat": 15.0, "carbs": 43.0},
        "ingredients": [
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 50},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 15},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 10}
        ],
        "keywords": ["Ğ²ĞµÑ€Ğ³ÑƒĞ½Ñ‹", "verguns", "Ñ…Ğ²Ğ¾Ñ€Ğ¾Ñ�Ñ‚"]
    },
    "Ğ»ĞµĞ²Ğ°ÑˆĞ½Ğ¸ĞºĞ¸": {
        "name": "Ğ›ĞµĞ²Ğ°ÑˆĞ½Ğ¸ĞºĞ¸",
        "name_en": ["levashniki", "russian filled pancakes"],
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 6.0, "fat": 8.0, "carbs": 32.0},
        "ingredients": [
            {"name": "Ğ±Ğ»Ğ¸Ğ½Ñ‹", "type": "carb", "percent": 50},
            {"name": "Ñ�Ğ³Ğ¾Ğ´Ğ½Ğ¾Ğµ Ğ¿Ğ¾Ğ²Ğ¸Ğ´Ğ»Ğ¾", "type": "fruit", "percent": 35},
            {"name": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "type": "dairy", "percent": 15}
        ],
        "keywords": ["Ğ»ĞµĞ²Ğ°ÑˆĞ½Ğ¸ĞºĞ¸", "levashniki", "Ğ±Ğ»Ğ¸Ğ½Ñ‹ Ñ� Ğ½Ğ°Ñ‡Ğ¸Ğ½ĞºĞ¾Ğ¹"]
    },
    
    # ==================== Ğ�Ğ�ĞŸĞ˜Ğ¢ĞšĞ˜ (Ğ�Ğ�Ğ’Ğ«Ğ•) ====================
    "Ğ¼ĞµĞ´Ğ¾Ğ²ÑƒÑ…Ğ°": {
        "name": "ĞœĞµĞ´Ğ¾Ğ²ÑƒÑ…Ğ°",
        "name_en": ["medovukha", "russian honey drink"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 80, "protein": 0.1, "fat": 0.1, "carbs": 18.0},
        "ingredients": [
            {"name": "Ğ¼ĞµĞ´", "type": "sugar", "percent": 25},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 70},
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶Ğ¸", "type": "other", "percent": 3},
            {"name": "Ñ…Ğ¼ĞµĞ»ÑŒ", "type": "other", "percent": 2}
        ],
        "keywords": ["Ğ¼ĞµĞ´Ğ¾Ğ²ÑƒÑ…Ğ°", "medovukha", "Ğ¼ĞµĞ´Ğ¾Ğ²Ñ‹Ğ¹ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº"]
    },
    "Ğ²Ğ°Ñ€ĞµĞ½ĞµÑ†": {
        "name": "Ğ’Ğ°Ñ€ĞµĞ½ĞµÑ†",
        "name_en": ["varenets", "russian fermented baked milk"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 60, "protein": 3.0, "fat": 3.5, "carbs": 4.5},
        "ingredients": [
            {"name": "Ñ‚Ğ¾Ğ¿Ğ»ĞµĞ½Ğ¾Ğµ Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 90},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 10}
        ],
        "keywords": ["Ğ²Ğ°Ñ€ĞµĞ½ĞµÑ†", "varenets", "Ñ€Ñ�Ğ¶ĞµĞ½ĞºĞ°", "ĞºĞ¸Ñ�Ğ»Ğ¾Ğ¼Ğ¾Ğ»Ğ¾Ñ‡Ğ½Ñ‹Ğ¹"]
    },
    "Ñ€Ñ�Ğ¶ĞµĞ½ĞºĞ°": {
        "name": "Ğ Ñ�Ğ¶ĞµĞ½ĞºĞ°",
        "name_en": ["ryazhenka", "baked fermented milk"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 60, "protein": 3.0, "fat": 3.5, "carbs": 4.5},
        "ingredients": [
            {"name": "Ñ‚Ğ¾Ğ¿Ğ»ĞµĞ½Ğ¾Ğµ Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 95},
            {"name": "Ğ·Ğ°ĞºĞ²Ğ°Ñ�ĞºĞ°", "type": "other", "percent": 5}
        ],
        "keywords": ["Ñ€Ñ�Ğ¶ĞµĞ½ĞºĞ°", "ryazhenka", "ĞºĞ¸Ñ�Ğ»Ğ¾Ğ¼Ğ¾Ğ»Ğ¾Ñ‡Ğ½Ñ‹Ğ¹"]
    },
    "Ğ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¾ĞºĞ²Ğ°ÑˆĞ°": {
        "name": "ĞŸÑ€Ğ¾Ñ�Ñ‚Ğ¾ĞºĞ²Ğ°ÑˆĞ°",
        "name_en": ["prostokvasha", "russian sour milk"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 55, "protein": 3.0, "fat": 3.0, "carbs": 4.0},
        "ingredients": [
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 95},
            {"name": "Ğ·Ğ°ĞºĞ²Ğ°Ñ�ĞºĞ°", "type": "other", "percent": 5}
        ],
        "keywords": ["Ğ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¾ĞºĞ²Ğ°ÑˆĞ°", "prostokvasha", "ĞºĞ¸Ñ�Ğ»Ğ¾Ğ¼Ğ¾Ğ»Ğ¾Ñ‡Ğ½Ñ‹Ğ¹"]
    },
    
    # ==================== Ğ¡Ğ�Ğ›Ğ�Ğ¢ Ğ¦Ğ•Ğ—Ğ�Ğ Ğ¬ Ğ¡ ĞšĞ Ğ�Ğ¡Ğ�Ğ�Ğ™ Ğ Ğ«Ğ‘Ğ�Ğ™ ====================
    "Ñ†ĞµĞ·Ğ°Ñ€ÑŒ Ñ� ĞºÑ€Ğ°Ñ�Ğ½Ğ¾Ğ¹ Ñ€Ñ‹Ğ±Ğ¾Ğ¹": {
        "name": "Ğ¦ĞµĞ·Ğ°Ñ€ÑŒ Ñ� ĞºÑ€Ğ°Ñ�Ğ½Ğ¾Ğ¹ Ñ€Ñ‹Ğ±Ğ¾Ğ¹",
        "name_en": ["caesar with salmon", "salmon caesar salad", "caesar with red fish"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 15.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ñ�Ğ»Ğ°Ğ±Ğ¾Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğ¹", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ€Ğ¾Ğ¼Ğ°Ğ½Ğ¾", "type": "vegetable", "percent": 30},
            {"name": "Ğ¿Ğ°Ñ€Ğ¼ĞµĞ·Ğ°Ğ½", "type": "dairy", "percent": 8},
            {"name": "Ñ�ÑƒÑ…Ğ°Ñ€Ğ¸ĞºĞ¸", "type": "carb", "percent": 10},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ñ‡ĞµÑ€Ñ€Ğ¸", "type": "vegetable", "percent": 8},
            {"name": "Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾", "type": "fruit", "percent": 7},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ†ĞµĞ·Ğ°Ñ€ÑŒ", "type": "sauce", "percent": 7}
        ],
        "keywords": ["Ñ†ĞµĞ·Ğ°Ñ€ÑŒ", "caesar", "ĞºÑ€Ğ°Ñ�Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°", "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "Ñ�ĞµĞ¼Ğ³Ğ°", "salmon caesar"]
    },
    "Ñ†ĞµĞ·Ğ°Ñ€ÑŒ Ñ� Ñ�ĞµĞ¼Ğ³Ğ¾Ğ¹": {
        "name": "Ğ¦ĞµĞ·Ğ°Ñ€ÑŒ Ñ� Ñ�ĞµĞ¼Ğ³Ğ¾Ğ¹",
        "name_en": ["salmon caesar", "caesar with salmon"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 215, "protein": 13.0, "fat": 15.5, "carbs": 7.5},
        "ingredients": [
            {"name": "Ñ�ĞµĞ¼Ğ³Ğ° Ñ�Ğ»Ğ°Ğ±Ğ¾Ñ�Ğ¾Ğ»ĞµĞ½Ğ°Ñ�", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ°Ğ¹Ñ�Ğ±ĞµÑ€Ğ³", "type": "vegetable", "percent": 30},
            {"name": "Ğ¿Ğ°Ñ€Ğ¼ĞµĞ·Ğ°Ğ½", "type": "dairy", "percent": 8},
            {"name": "Ğ³Ñ€ĞµĞ½ĞºĞ¸ Ñ‡ĞµÑ�Ğ½Ğ¾Ñ‡Ğ½Ñ‹Ğµ", "type": "carb", "percent": 10},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ñ‡ĞµÑ€Ñ€Ğ¸", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ†ĞµĞ·Ğ°Ñ€ÑŒ", "type": "sauce", "percent": 8},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ Ğ¿ĞµÑ€ĞµĞ¿ĞµĞ»Ğ¸Ğ½Ğ¾Ğµ", "type": "protein", "percent": 6}
        ],
        "keywords": ["Ñ†ĞµĞ·Ğ°Ñ€ÑŒ Ñ� Ñ�ĞµĞ¼Ğ³Ğ¾Ğ¹", "salmon caesar", "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ"]
    },
    "Ñ†ĞµĞ·Ğ°Ñ€ÑŒ Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼ Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¼": {
        "name": "Ğ¦ĞµĞ·Ğ°Ñ€ÑŒ Ñ� Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¼ Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼",
        "name_en": ["baked salmon caesar", "warm salmon caesar"],
        "category": "salad",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 14.0, "fat": 11.0, "carbs": 9.0},
        "ingredients": [
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹", "type": "protein", "percent": 35},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ€Ğ¾Ğ¼Ğ°Ğ½Ğ¾", "type": "vegetable", "percent": 30},
            {"name": "Ğ¿Ğ°Ñ€Ğ¼ĞµĞ·Ğ°Ğ½", "type": "dairy", "percent": 8},
            {"name": "Ğ³Ñ€ĞµĞ½ĞºĞ¸", "type": "carb", "percent": 10},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ñ‡ĞµÑ€Ñ€Ğ¸", "type": "vegetable", "percent": 7},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ†ĞµĞ·Ğ°Ñ€ÑŒ", "type": "sauce", "percent": 10}
        ],
        "keywords": ["Ñ†ĞµĞ·Ğ°Ñ€ÑŒ Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼", "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "warm salmon caesar"]
    },

    # =============================================================================
    # ğŸ�½ï¸� Ğ Ğ•Ğ¡Ğ¢Ğ�Ğ Ğ�Ğ�Ğ�Ğ«Ğ• Ğ¢Ğ Ğ•Ğ�Ğ”Ğ« 2026 Ğ˜ ĞŸĞ�ĞŸĞ£Ğ›Ğ¯Ğ Ğ�Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ�
    # =============================================================================
    
    # ==================== Ğ Ğ•Ğ¡Ğ¢Ğ�Ğ Ğ�Ğ�Ğ�Ğ�Ğ¯ ĞšĞ›Ğ�Ğ¡Ğ¡Ğ˜ĞšĞ� Ğ˜ Ğ¢Ğ Ğ•Ğ�Ğ”Ğ« ====================
    "Ñ‚Ğ°Ñ‚Ğ°Ñ€ Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹": {
        "name": "Ğ¢Ğ°Ñ‚Ğ°Ñ€ Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹",
        "name_en": ["beef tartare", "steak tartare"],
        "category": "appetizer",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 180, "protein": 20.0, "fat": 10.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ� Ğ²Ñ‹Ñ€ĞµĞ·ĞºĞ°", "type": "protein", "percent": 75},
            {"name": "Ğ»ÑƒĞº ÑˆĞ°Ğ»Ğ¾Ñ‚", "type": "vegetable", "percent": 5},
            {"name": "ĞºĞ°Ğ¿ĞµÑ€Ñ�Ñ‹", "type": "vegetable", "percent": 4},
            {"name": "ĞºĞ¾Ñ€Ğ½Ğ¸ÑˆĞ¾Ğ½Ñ‹", "type": "vegetable", "percent": 4},
            {"name": "Ğ¶ĞµĞ»Ñ‚Ğ¾Ğº Ñ�Ğ¸Ñ‡Ğ½Ñ‹Ğ¹", "type": "protein", "percent": 5},
            {"name": "Ğ³Ğ¾Ñ€Ñ‡Ğ¸Ñ†Ğ° Ğ´Ğ¸Ğ¶Ğ¾Ğ½Ñ�ĞºĞ°Ñ�", "type": "sauce", "percent": 3},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ğ²Ğ¾Ñ€Ñ‡ĞµÑ�Ñ‚ĞµÑ€", "type": "sauce", "percent": 2},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ", "type": "fat", "percent": 2}
        ],
        "keywords": ["Ñ‚Ğ°Ñ‚Ğ°Ñ€", "tartare", "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°", "Ñ€ĞµÑ�Ñ‚Ğ¾Ñ€Ğ°Ğ½"]
    },
    "Ñ‚Ğ°Ñ€Ñ‚Ğ°Ñ€ Ğ¸Ğ· Ğ»Ğ¾Ñ�Ğ¾Ñ�Ñ�": {
        "name": "Ğ¢Ğ°Ñ€Ñ‚Ğ°Ñ€ Ğ¸Ğ· Ğ»Ğ¾Ñ�Ğ¾Ñ�Ñ�",
        "name_en": ["salmon tartare", "salmon tartar"],
        "category": "appetizer",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 13.0, "carbs": 3.0},
        "ingredients": [
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ñ�Ğ²ĞµĞ¶Ğ¸Ğ¹", "type": "protein", "percent": 70},
            {"name": "Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾", "type": "fruit", "percent": 12},
            {"name": "Ğ»ÑƒĞº ÑˆĞ°Ğ»Ğ¾Ñ‚", "type": "vegetable", "percent": 4},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 4},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ�Ğ¾ĞµĞ²Ñ‹Ğ¹", "type": "sauce", "percent": 3},
            {"name": "ĞºÑƒĞ½Ğ¶ÑƒÑ‚Ğ½Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 2},
            {"name": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ñ‚Ğ°Ñ€Ñ‚Ğ°Ñ€", "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "salmon tartare", "Ñ€Ñ‹Ğ±Ğ½Ğ°Ñ� Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°"]
    },
    "ĞºĞ°Ñ€Ğ¿Ğ°Ñ‡Ñ‡Ğ¾ Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹": {
        "name": "ĞšĞ°Ñ€Ğ¿Ğ°Ñ‡Ñ‡Ğ¾ Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹",
        "name_en": ["beef carpaccio"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 150, "protein": 18.0, "fat": 8.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ� Ğ²Ñ‹Ñ€ĞµĞ·ĞºĞ°", "type": "protein", "percent": 75},
            {"name": "Ğ¿Ğ°Ñ€Ğ¼ĞµĞ·Ğ°Ğ½", "type": "dairy", "percent": 8},
            {"name": "Ñ€ÑƒĞºĞ¾Ğ»Ğ°", "type": "vegetable", "percent": 7},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 3},
            {"name": "ĞºĞ°Ğ¿ĞµÑ€Ñ�Ñ‹", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["ĞºĞ°Ñ€Ğ¿Ğ°Ñ‡Ñ‡Ğ¾", "carpaccio", "Ğ¸Ñ‚Ğ°Ğ»ÑŒÑ�Ğ½Ñ�ĞºĞ°Ñ� Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°"]
    },
    "Ğ¾Ğ²Ğ¾Ñ‰Ğ¸ Ğ½Ğ° Ğ³Ñ€Ğ¸Ğ»Ğµ": {
        "name": "Ğ�Ğ²Ğ¾Ñ‰Ğ¸ Ğ½Ğ° Ğ³Ñ€Ğ¸Ğ»Ğµ",
        "name_en": ["grilled vegetables", "vegetable grill"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 90, "protein": 3.0, "fat": 5.0, "carbs": 8.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ±Ğ°Ñ‡ĞºĞ¸", "type": "vegetable", "percent": 25},
            {"name": "Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½Ñ‹", "type": "vegetable", "percent": 25},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹", "type": "vegetable", "percent": 20},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ñ‡ĞµÑ€Ñ€Ğ¸", "type": "vegetable", "percent": 15},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10},
            {"name": "Ñ‚Ğ¸Ğ¼ÑŒÑ�Ğ½", "type": "spice", "percent": 5}
        ],
        "keywords": ["Ğ³Ñ€Ğ¸Ğ»ÑŒ", "grilled vegetables", "Ğ¾Ğ²Ğ¾Ñ‰Ğ¸"]
    },
    "ĞºĞ°Ğ»ÑŒĞ¼Ğ°Ñ€Ñ‹ Ğ³Ñ€Ğ¸Ğ»ÑŒ": {
        "name": "ĞšĞ°Ğ»ÑŒĞ¼Ğ°Ñ€Ñ‹ Ğ½Ğ° Ğ³Ñ€Ğ¸Ğ»Ğµ",
        "name_en": ["grilled squid", "calamari grill"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 130, "protein": 20.0, "fat": 4.0, "carbs": 4.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ»ÑŒĞ¼Ğ°Ñ€Ñ‹", "type": "protein", "percent": 75},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¿ĞµÑ‚Ñ€ÑƒÑˆĞºĞ°", "type": "vegetable", "percent": 5},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 8},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 5},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 2}
        ],
        "keywords": ["ĞºĞ°Ğ»ÑŒĞ¼Ğ°Ñ€Ñ‹", "squid", "calamari", "Ğ³Ñ€Ğ¸Ğ»ÑŒ"]
    },
    "Ğ¼ĞµĞ´Ğ°Ğ»ÑŒĞ¾Ğ½Ñ‹ Ğ¸Ğ· Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ñ‹": {
        "name": "ĞœĞµĞ´Ğ°Ğ»ÑŒĞ¾Ğ½Ñ‹ Ğ¸Ğ· Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ñ‹",
        "name_en": ["pork medallions"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 24.0, "fat": 12.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ°Ñ� Ğ²Ñ‹Ñ€ĞµĞ·ĞºĞ°", "type": "protein", "percent": 80},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ñ€Ğ¾Ğ·Ğ¼Ğ°Ñ€Ğ¸Ğ½", "type": "spice", "percent": 2},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 10},
            {"name": "Ğ²Ğ¸Ğ½Ğ¾ Ğ±ĞµĞ»Ğ¾Ğµ", "type": "liquid", "percent": 5}
        ],
        "keywords": ["Ğ¼ĞµĞ´Ğ°Ğ»ÑŒĞ¾Ğ½Ñ‹", "pork medallions", "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°"]
    },
    "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ° Ñ� Ñ€Ğ¾Ğ·Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ¼": {
        "name": "Ğ‘Ğ°Ñ€Ğ°Ğ½ÑŒĞ¸ Ñ€ĞµĞ±Ñ€Ñ‹ÑˆĞºĞ¸ Ñ� Ñ€Ğ¾Ğ·Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ¼",
        "name_en": ["lamb ribs with rosemary"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 260, "protein": 22.0, "fat": 19.0, "carbs": 2.0},
        "ingredients": [
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½ÑŒĞ¸ Ñ€ĞµĞ±Ñ€Ñ‹ÑˆĞºĞ¸", "type": "protein", "percent": 80},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ€Ğ¾Ğ·Ğ¼Ğ°Ñ€Ğ¸Ğ½", "type": "spice", "percent": 3},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 2}
        ],
        "keywords": ["Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°", "lamb ribs", "Ñ€ĞµĞ±Ñ€Ñ‹ÑˆĞºĞ¸"]
    },
    "ÑƒÑ‚Ğ¸Ğ½Ğ°Ñ� Ğ³Ñ€ÑƒĞ´ĞºĞ° Ñ� Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ°Ğ¼Ğ¸": {
        "name": "Ğ£Ñ‚Ğ¸Ğ½Ğ°Ñ� Ğ³Ñ€ÑƒĞ´ĞºĞ° Ñ� Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğ¾Ğ¼",
        "name_en": ["duck breast with orange sauce"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 18.0, "fat": 14.0, "carbs": 6.0},
        "ingredients": [
            {"name": "ÑƒÑ‚Ğ¸Ğ½Ğ°Ñ� Ğ³Ñ€ÑƒĞ´ĞºĞ°", "type": "protein", "percent": 65},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ñ‹", "type": "fruit", "percent": 15},
            {"name": "Ğ¼ĞµĞ´", "type": "sugar", "percent": 5},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ�Ğ¾ĞµĞ²Ñ‹Ğ¹", "type": "sauce", "percent": 5},
            {"name": "Ğ»ÑƒĞº ÑˆĞ°Ğ»Ğ¾Ñ‚", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["ÑƒÑ‚ĞºĞ°", "duck", "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "Ñ€ĞµÑ�Ñ‚Ğ¾Ñ€Ğ°Ğ½"]
    },
    "Ğ¼Ğ¾Ñ€Ñ�ĞºĞ¾Ğ¹ Ñ�Ğ·Ñ‹Ğº": {
        "name": "ĞœĞ¾Ñ€Ñ�ĞºĞ¾Ğ¹ Ñ�Ğ·Ñ‹Ğº",
        "name_en": ["sole fish", "dover sole"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 120, "protein": 22.0, "fat": 3.0, "carbs": 1.0},
        "ingredients": [
            {"name": "Ğ¼Ğ¾Ñ€Ñ�ĞºĞ¾Ğ¹ Ñ�Ğ·Ñ‹Ğº", "type": "protein", "percent": 80},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ", "type": "fat", "percent": 8},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 5},
            {"name": "Ğ¿ĞµÑ‚Ñ€ÑƒÑˆĞºĞ°", "type": "vegetable", "percent": 5},
            {"name": "ĞºĞ°Ğ¿ĞµÑ€Ñ�Ñ‹", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["Ğ¼Ğ¾Ñ€Ñ�ĞºĞ¾Ğ¹ Ñ�Ğ·Ñ‹Ğº", "sole", "Ñ€Ñ‹Ğ±Ğ°"]
    },
    "Ğ¼Ğ¸Ğ´Ğ¸Ğ¸ Ğ² Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğµ": {
        "name": "ĞœĞ¸Ğ´Ğ¸Ğ¸ Ğ² Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğµ",
        "name_en": ["mussels in cream sauce"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 130, "protein": 12.0, "fat": 7.0, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ¼Ğ¸Ğ´Ğ¸Ğ¸", "type": "protein", "percent": 50},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 25},
            {"name": "Ğ»ÑƒĞº ÑˆĞ°Ğ»Ğ¾Ñ‚", "type": "vegetable", "percent": 8},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ²Ğ¸Ğ½Ğ¾ Ğ±ĞµĞ»Ğ¾Ğµ", "type": "liquid", "percent": 7},
            {"name": "Ğ¿ĞµÑ‚Ñ€ÑƒÑˆĞºĞ°", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ğ¼Ğ¸Ğ´Ğ¸Ğ¸", "mussels", "Ğ¼Ğ¾Ñ€ĞµĞ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹"]
    },
    "ĞºÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸ Ñ‚ĞµĞ¼Ğ¿ÑƒÑ€Ğ°": {
        "name": "ĞšÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸ Ğ² Ñ‚ĞµĞ¼Ğ¿ÑƒÑ€Ğµ",
        "name_en": ["shrimp tempura", "tempura shrimp"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 210, "protein": 14.0, "fat": 10.0, "carbs": 16.0},
        "ingredients": [
            {"name": "ĞºÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸", "type": "protein", "percent": 50},
            {"name": "Ğ¼ÑƒĞºĞ° Ğ´Ğ»Ñ� Ñ‚ĞµĞ¼Ğ¿ÑƒÑ€Ñ‹", "type": "carb", "percent": 20},
            {"name": "Ğ²Ğ¾Ğ´Ğ° Ğ»ĞµĞ´Ñ�Ğ½Ğ°Ñ�", "type": "liquid", "percent": 15},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 10}
        ],
        "keywords": ["Ñ‚ĞµĞ¼Ğ¿ÑƒÑ€Ğ°", "tempura", "ĞºÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸", "Ñ�Ğ¿Ğ¾Ğ½Ñ�ĞºĞ°Ñ� Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°"]
    },
    "Ğ»ÑƒĞºĞ¾Ğ²Ñ‹Ğµ ĞºĞ¾Ğ»ÑŒÑ†Ğ°": {
        "name": "Ğ›ÑƒĞºĞ¾Ğ²Ñ‹Ğµ ĞºĞ¾Ğ»ÑŒÑ†Ğ°",
        "name_en": ["onion rings"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 280, "protein": 4.0, "fat": 16.0, "carbs": 30.0},
        "ingredients": [
            {"name": "Ğ»ÑƒĞº Ñ€ĞµĞ¿Ñ‡Ğ°Ñ‚Ñ‹Ğ¹", "type": "vegetable", "percent": 50},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 15},
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğµ Ñ�ÑƒÑ…Ğ°Ñ€Ğ¸", "type": "carb", "percent": 15},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 12}
        ],
        "keywords": ["onion rings", "Ğ»ÑƒĞºĞ¾Ğ²Ñ‹Ğµ ĞºĞ¾Ğ»ÑŒÑ†Ğ°", "Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°"]
    },
    "Ñ�Ñ‹Ñ€Ğ½Ñ‹Ğµ Ğ¿Ğ°Ğ»Ğ¾Ñ‡ĞºĞ¸": {
        "name": "Ğ¡Ñ‹Ñ€Ğ½Ñ‹Ğµ Ğ¿Ğ°Ğ»Ğ¾Ñ‡ĞºĞ¸",
        "name_en": ["cheese sticks", "mozzarella sticks"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 310, "protein": 14.0, "fat": 18.0, "carbs": 22.0},
        "ingredients": [
            {"name": "Ñ�Ñ‹Ñ€ Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 60},
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğµ Ñ�ÑƒÑ…Ğ°Ñ€Ğ¸", "type": "carb", "percent": 15},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 8},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 7},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 10}
        ],
        "keywords": ["cheese sticks", "mozzarella sticks", "Ğ·Ğ°ĞºÑƒÑ�ĞºĞ°"]
    },
    "Ğ½Ğ°Ğ³Ğ³ĞµÑ‚Ñ�Ñ‹ ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ": {
        "name": "ĞšÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ Ğ½Ğ°Ğ³Ğ³ĞµÑ‚Ñ�Ñ‹",
        "name_en": ["chicken nuggets"],
        "category": "appetizer",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 250, "protein": 16.0, "fat": 15.0, "carbs": 14.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 60},
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğµ Ñ�ÑƒÑ…Ğ°Ñ€Ğ¸", "type": "carb", "percent": 15},
            {"name": "Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 8},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 7},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 10}
        ],
        "keywords": ["nuggets", "Ğ½Ğ°Ğ³Ğ³ĞµÑ‚Ñ�Ñ‹", "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "Ñ„Ğ°Ñ�Ñ‚Ñ„ÑƒĞ´"]
    },
    "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ°Ğ¹Ğ´Ğ°Ñ…Ğ¾": {
        "name": "ĞšĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¿Ğ¾-Ğ°Ğ¹Ğ´Ğ°Ñ…Ğ¾Ğ²Ñ�ĞºĞ¸",
        "name_en": ["idaho potatoes", "baked potatoes"],
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 3.0, "fat": 5.0, "carbs": 23.0},
        "ingredients": [
            {"name": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ", "type": "carb", "percent": 75},
            {"name": "Ñ�Ñ‹Ñ€ Ñ‡ĞµĞ´Ğ´ĞµÑ€", "type": "dairy", "percent": 10},
            {"name": "Ğ±ĞµĞºĞ¾Ğ½", "type": "protein", "percent": 5},
            {"name": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°", "type": "dairy", "percent": 8},
            {"name": "Ğ»ÑƒĞº Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["Ğ°Ğ¹Ğ´Ğ°Ñ…Ğ¾", "idaho potatoes", "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ"]
    },
    
    # ==================== Ğ¤Ğ�Ğ¡Ğ¢Ğ¤Ğ£Ğ”-Ğ¥Ğ˜Ğ¢Ğ« ====================
    "Ñ‡Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€": {
        "name": "Ğ§Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€",
        "name_en": ["cheeseburger"],
        "category": "fastfood",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 260, "protein": 14.0, "fat": 12.0, "carbs": 25.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ° Ğ´Ğ»Ñ� Ğ±ÑƒÑ€Ğ³ĞµÑ€Ğ°", "type": "carb", "percent": 30},
            {"name": "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ° Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ�", "type": "protein", "percent": 30},
            {"name": "Ñ�Ñ‹Ñ€ Ñ‡ĞµĞ´Ğ´ĞµÑ€", "type": "dairy", "percent": 10},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 8},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 6},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 4},
            {"name": "ĞºĞµÑ‚Ñ‡ÑƒĞ¿", "type": "sauce", "percent": 5},
            {"name": "Ğ³Ğ¾Ñ€Ñ‡Ğ¸Ñ†Ğ°", "type": "sauce", "percent": 2},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 5}
        ],
        "keywords": ["Ñ‡Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€", "cheeseburger", "Ğ±ÑƒÑ€Ğ³ĞµÑ€"]
    },
    "Ğ´Ğ°Ğ±Ğ» Ñ‡Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€": {
        "name": "Ğ”Ğ°Ğ±Ğ» Ñ‡Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€",
        "name_en": ["double cheeseburger"],
        "category": "fastfood",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 270, "protein": 16.0, "fat": 14.0, "carbs": 22.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ° Ğ´Ğ»Ñ� Ğ±ÑƒÑ€Ğ³ĞµÑ€Ğ°", "type": "carb", "percent": 25},
            {"name": "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ° Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ�", "type": "protein", "percent": 40},
            {"name": "Ñ�Ñ‹Ñ€ Ñ‡ĞµĞ´Ğ´ĞµÑ€", "type": "dairy", "percent": 15},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 6},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 4},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 3},
            {"name": "ĞºĞµÑ‚Ñ‡ÑƒĞ¿", "type": "sauce", "percent": 4},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 3}
        ],
        "keywords": ["Ğ´Ğ°Ğ±Ğ»", "double cheeseburger", "Ğ±ÑƒÑ€Ğ³ĞµÑ€"]
    },
    "Ğ±ÑƒÑ€Ğ³ĞµÑ€ Ñ� Ğ±ĞµĞºĞ¾Ğ½Ğ¾Ğ¼": {
        "name": "Ğ‘ÑƒÑ€Ğ³ĞµÑ€ Ñ� Ğ±ĞµĞºĞ¾Ğ½Ğ¾Ğ¼",
        "name_en": ["bacon burger"],
        "category": "fastfood",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 280, "protein": 16.0, "fat": 16.0, "carbs": 21.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ° Ğ´Ğ»Ñ� Ğ±ÑƒÑ€Ğ³ĞµÑ€Ğ°", "type": "carb", "percent": 25},
            {"name": "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ° Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ�", "type": "protein", "percent": 30},
            {"name": "Ğ±ĞµĞºĞ¾Ğ½", "type": "protein", "percent": 15},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 8},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 6},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 4},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 3},
            {"name": "Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 9}
        ],
        "keywords": ["bacon burger", "Ğ±ÑƒÑ€Ğ³ĞµÑ€ Ñ� Ğ±ĞµĞºĞ¾Ğ½Ğ¾Ğ¼"]
    },
    "Ñ‡Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€ Ñ� Ğ±ĞµĞºĞ¾Ğ½Ğ¾Ğ¼": {
        "name": "Ğ§Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€ Ñ� Ğ±ĞµĞºĞ¾Ğ½Ğ¾Ğ¼",
        "name_en": ["bacon cheeseburger"],
        "category": "fastfood",
        "default_weight": 320,
        "nutrition_per_100": {"calories": 280, "protein": 17.0, "fat": 16.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ° Ğ´Ğ»Ñ� Ğ±ÑƒÑ€Ğ³ĞµÑ€Ğ°", "type": "carb", "percent": 25},
            {"name": "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ° Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒÑ�", "type": "protein", "percent": 30},
            {"name": "Ğ±ĞµĞºĞ¾Ğ½", "type": "protein", "percent": 12},
            {"name": "Ñ�Ñ‹Ñ€ Ñ‡ĞµĞ´Ğ´ĞµÑ€", "type": "dairy", "percent": 10},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 6},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 4},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 3},
            {"name": "Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 10}
        ],
        "keywords": ["bacon cheeseburger", "Ñ‡Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€ Ñ� Ğ±ĞµĞºĞ¾Ğ½Ğ¾Ğ¼"]
    },
    "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹ Ğ±ÑƒÑ€Ğ³ĞµÑ€": {
        "name": "ĞšÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹ Ğ±ÑƒÑ€Ğ³ĞµÑ€",
        "name_en": ["chicken burger"],
        "category": "fastfood",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 15.0, "fat": 10.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ° Ğ´Ğ»Ñ� Ğ±ÑƒÑ€Ğ³ĞµÑ€Ğ°", "type": "carb", "percent": 30},
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ°Ñ� ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ°", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·", "type": "sauce", "percent": 10},
            {"name": "ĞºĞµÑ‚Ñ‡ÑƒĞ¿", "type": "sauce", "percent": 7}
        ],
        "keywords": ["chicken burger", "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹ Ğ±ÑƒÑ€Ğ³ĞµÑ€"]
    },
    "Ğ¾Ñ�Ñ‚Ñ€Ğ°Ñ� ĞºÑƒÑ€Ğ¸Ñ†Ğ°": {
        "name": "Ğ�Ñ�Ñ‚Ñ€Ğ°Ñ� ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
        "name_en": ["spicy chicken", "hot chicken"],
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 20.0, "fat": 12.0, "carbs": 10.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 60},
            {"name": "Ğ¾Ñ�Ñ‚Ñ€Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 15},
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°", "type": "carb", "percent": 15},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 10}
        ],
        "keywords": ["spicy chicken", "hot chicken", "Ğ¾Ñ�Ñ‚Ñ€Ñ‹Ğ¹"]
    },
    "Ñ�Ñ‚Ñ€Ğ¸Ğ¿Ñ�Ñ‹ ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ": {
        "name": "ĞšÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ Ñ�Ñ‚Ñ€Ğ¸Ğ¿Ñ�Ñ‹",
        "name_en": ["chicken strips", "chicken tenders"],
        "category": "fastfood",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 230, "protein": 18.0, "fat": 13.0, "carbs": 12.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 65},
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°", "type": "carb", "percent": 18},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 7},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 10}
        ],
        "keywords": ["Ñ�Ñ‚Ñ€Ğ¸Ğ¿Ñ�Ñ‹", "chicken strips", "chicken tenders"]
    },
    "ĞºÑ€Ñ‹Ğ»Ñ‹ÑˆĞºĞ¸ Ğ±Ğ°Ñ€Ğ±ĞµĞºÑ�": {
        "name": "ĞšÑ€Ñ‹Ğ»Ñ‹ÑˆĞºĞ¸ Ğ±Ğ°Ñ€Ğ±ĞµĞºÑ�",
        "name_en": ["bbq chicken wings"],
        "category": "appetizer",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 18.0, "fat": 16.0, "carbs": 6.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ ĞºÑ€Ñ‹Ğ»ÑŒÑ�", "type": "protein", "percent": 70},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ğ±Ğ°Ñ€Ğ±ĞµĞºÑ�", "type": "sauce", "percent": 20},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10}
        ],
        "keywords": ["ĞºÑ€Ñ‹Ğ»Ñ‹ÑˆĞºĞ¸", "chicken wings", "bbq"]
    },
    "ĞºÑ€Ñ‹Ğ»Ñ‹ÑˆĞºĞ¸ Ğ¾Ñ�Ñ‚Ñ€Ñ‹Ğµ": {
        "name": "Ğ�Ñ�Ñ‚Ñ€Ñ‹Ğµ ĞºÑ€Ñ‹Ğ»Ñ‹ÑˆĞºĞ¸",
        "name_en": ["hot wings"],
        "category": "appetizer",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 230, "protein": 18.0, "fat": 15.0, "carbs": 5.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ ĞºÑ€Ñ‹Ğ»ÑŒÑ�", "type": "protein", "percent": 70},
            {"name": "Ğ¾Ñ�Ñ‚Ñ€Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 20},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10}
        ],
        "keywords": ["hot wings", "Ğ¾Ñ�Ñ‚Ñ€Ñ‹Ğµ ĞºÑ€Ñ‹Ğ»Ñ‹ÑˆĞºĞ¸"]
    },
    "Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³": {
        "name": "Ğ¥Ğ¾Ñ‚-Ğ´Ğ¾Ğ³",
        "name_en": ["hot dog"],
        "category": "fastfood",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 240, "protein": 8.0, "fat": 13.0, "carbs": 23.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ° Ğ´Ğ»Ñ� Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³Ğ°", "type": "carb", "percent": 40},
            {"name": "Ñ�Ğ¾Ñ�Ğ¸Ñ�ĞºĞ°", "type": "protein", "percent": 30},
            {"name": "ĞºĞµÑ‚Ñ‡ÑƒĞ¿", "type": "sauce", "percent": 8},
            {"name": "Ğ³Ğ¾Ñ€Ñ‡Ğ¸Ñ†Ğ°", "type": "sauce", "percent": 5},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 7},
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° ĞºĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ�", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["hot dog", "Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³"]
    },
    "Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³ Ğ¿Ğ¾-Ğ¼ĞµĞºÑ�Ğ¸ĞºĞ°Ğ½Ñ�ĞºĞ¸": {
        "name": "Ğ¥Ğ¾Ñ‚-Ğ´Ğ¾Ğ³ Ğ¿Ğ¾-Ğ¼ĞµĞºÑ�Ğ¸ĞºĞ°Ğ½Ñ�ĞºĞ¸",
        "name_en": ["mexican hot dog"],
        "category": "fastfood",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 230, "protein": 8.0, "fat": 12.0, "carbs": 23.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ¾Ñ‡ĞºĞ°", "type": "carb", "percent": 35},
            {"name": "Ñ�Ğ¾Ñ�Ğ¸Ñ�ĞºĞ°", "type": "protein", "percent": 25},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ñ…Ğ°Ğ»Ğ°Ğ¿ĞµĞ½ÑŒĞ¾", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ°Ğ»ÑŒÑ�Ğ°", "type": "sauce", "percent": 12},
            {"name": "Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾", "type": "fruit", "percent": 8},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 7},
            {"name": "ĞºĞ¸Ğ½Ğ·Ğ°", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["mexican hot dog", "Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³"]
    },
    "Ñ„Ñ€Ğ°Ğ½Ñ†ÑƒĞ·Ñ�ĞºĞ¸Ğ¹ Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³": {
        "name": "Ğ¤Ñ€Ğ°Ğ½Ñ†ÑƒĞ·Ñ�ĞºĞ¸Ğ¹ Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³",
        "name_en": ["french hot dog"],
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 250, "protein": 8.0, "fat": 14.0, "carbs": 24.0},
        "ingredients": [
            {"name": "Ğ±Ğ°Ğ³ĞµÑ‚", "type": "carb", "percent": 50},
            {"name": "Ñ�Ğ¾Ñ�Ğ¸Ñ�ĞºĞ°", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 15},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 5}
        ],
        "keywords": ["french hot dog", "Ñ„Ñ€Ğ°Ğ½Ñ†ÑƒĞ·Ñ�ĞºĞ¸Ğ¹ Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³"]
    },
    "ĞºĞ¾Ñ€Ğ½-Ğ´Ğ¾Ğ³": {
        "name": "ĞšĞ¾Ñ€Ğ½-Ğ´Ğ¾Ğ³",
        "name_en": ["corn dog"],
        "category": "fastfood",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 260, "protein": 7.0, "fat": 12.0, "carbs": 31.0},
        "ingredients": [
            {"name": "Ñ�Ğ¾Ñ�Ğ¸Ñ�ĞºĞ°", "type": "protein", "percent": 35},
            {"name": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ½Ğ°Ñ� Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 35},
            {"name": "Ğ¿ÑˆĞµĞ½Ğ¸Ñ‡Ğ½Ğ°Ñ� Ğ¼ÑƒĞºĞ°", "type": "carb", "percent": 10},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ´Ğ»Ñ� Ñ„Ñ€Ğ¸Ñ‚Ñ�Ñ€Ğ°", "type": "fat", "percent": 12}
        ],
        "keywords": ["corn dog", "ĞºĞ¾Ñ€Ğ½-Ğ´Ğ¾Ğ³"]
    },
    
    # ==================== ĞŸĞ˜Ğ¦Ğ¦Ğ� (ĞŸĞ�ĞŸĞ£Ğ›Ğ¯Ğ Ğ�Ğ«Ğ• Ğ’Ğ�Ğ Ğ˜Ğ�Ğ�Ğ¢Ğ«) ====================
    "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ¿ĞµĞ¿Ğ¿ĞµÑ€Ğ¾Ğ½Ğ¸": {
        "name": "ĞŸĞ¸Ñ†Ñ†Ğ° ĞŸĞµĞ¿Ğ¿ĞµÑ€Ğ¾Ğ½Ğ¸",
        "name_en": ["pepperoni pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 270, "protein": 12.0, "fat": 12.0, "carbs": 29.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ğ»Ñ� Ğ¿Ğ¸Ñ†Ñ†Ñ‹", "type": "carb", "percent": 45},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹", "type": "sauce", "percent": 15},
            {"name": "Ñ�Ñ‹Ñ€ Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 25},
            {"name": "Ğ¿ĞµĞ¿Ğ¿ĞµÑ€Ğ¾Ğ½Ğ¸", "type": "protein", "percent": 15}
        ],
        "keywords": ["Ğ¿Ğ¸Ñ†Ñ†Ğ°", "pizza", "Ğ¿ĞµĞ¿Ğ¿ĞµÑ€Ğ¾Ğ½Ğ¸", "pepperoni"]
    },
    "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ñ‡ĞµÑ‚Ñ‹Ñ€Ğµ Ñ�Ñ‹Ñ€Ğ°": {
        "name": "ĞŸĞ¸Ñ†Ñ†Ğ° Ğ§ĞµÑ‚Ñ‹Ñ€Ğµ Ñ�Ñ‹Ñ€Ğ°",
        "name_en": ["four cheese pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 290, "protein": 14.0, "fat": 14.0, "carbs": 27.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ğ»Ñ� Ğ¿Ğ¸Ñ†Ñ†Ñ‹", "type": "carb", "percent": 45},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğ¹", "type": "sauce", "percent": 10},
            {"name": "Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ¿Ğ°Ñ€Ğ¼ĞµĞ·Ğ°Ğ½", "type": "dairy", "percent": 10},
            {"name": "Ğ³Ğ¾Ñ€Ğ³Ğ¾Ğ½Ğ·Ğ¾Ğ»Ğ°", "type": "dairy", "percent": 8},
            {"name": "Ñ„ĞµÑ‚Ğ°", "type": "dairy", "percent": 7}
        ],
        "keywords": ["Ñ‡ĞµÑ‚Ñ‹Ñ€Ğµ Ñ�Ñ‹Ñ€Ğ°", "four cheese", "Ğ¿Ğ¸Ñ†Ñ†Ğ°"]
    },
    "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ³Ğ°Ğ²Ğ°Ğ¹Ñ�ĞºĞ°Ñ�": {
        "name": "ĞŸĞ¸Ñ†Ñ†Ğ° Ğ“Ğ°Ğ²Ğ°Ğ¹Ñ�ĞºĞ°Ñ�",
        "name_en": ["hawaiian pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 240, "protein": 10.0, "fat": 8.0, "carbs": 32.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ğ»Ñ� Ğ¿Ğ¸Ñ†Ñ†Ñ‹", "type": "carb", "percent": 45},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹", "type": "sauce", "percent": 15},
            {"name": "Ñ�Ñ‹Ñ€ Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ²ĞµÑ‚Ñ‡Ğ¸Ğ½Ğ°", "type": "protein", "percent": 10},
            {"name": "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�", "type": "fruit", "percent": 10}
        ],
        "keywords": ["hawaiian", "Ğ³Ğ°Ğ²Ğ°Ğ¹Ñ�ĞºĞ°Ñ�", "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ñ� Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�Ğ¾Ğ¼"]
    },
    "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ¼Ñ�Ñ�Ğ½Ğ°Ñ�": {
        "name": "ĞŸĞ¸Ñ†Ñ†Ğ° ĞœÑ�Ñ�Ğ½Ğ°Ñ�",
        "name_en": ["meat pizza"],
        "category": "bakery",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 260, "protein": 14.0, "fat": 11.0, "carbs": 27.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ğ»Ñ� Ğ¿Ğ¸Ñ†Ñ†Ñ‹", "type": "carb", "percent": 40},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹", "type": "sauce", "percent": 12},
            {"name": "Ñ�Ñ‹Ñ€ Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ¿ĞµĞ¿Ğ¿ĞµÑ€Ğ¾Ğ½Ğ¸", "type": "protein", "percent": 8},
            {"name": "Ğ²ĞµÑ‚Ñ‡Ğ¸Ğ½Ğ°", "type": "protein", "percent": 8},
            {"name": "Ğ±ĞµĞºĞ¾Ğ½", "type": "protein", "percent": 7},
            {"name": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°", "type": "protein", "percent": 5}
        ],
        "keywords": ["Ğ¼Ñ�Ñ�Ğ½Ğ°Ñ� Ğ¿Ğ¸Ñ†Ñ†Ğ°", "meat pizza"]
    },
    "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ñ� Ğ³Ñ€Ğ¸Ğ±Ğ°Ğ¼Ğ¸": {
        "name": "ĞŸĞ¸Ñ†Ñ†Ğ° Ñ� Ğ³Ñ€Ğ¸Ğ±Ğ°Ğ¼Ğ¸",
        "name_en": ["mushroom pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 220, "protein": 9.0, "fat": 8.0, "carbs": 29.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ğ»Ñ� Ğ¿Ğ¸Ñ†Ñ†Ñ‹", "type": "carb", "percent": 45},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹", "type": "sauce", "percent": 15},
            {"name": "Ñ�Ñ‹Ñ€ Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 20},
            {"name": "ÑˆĞ°Ğ¼Ğ¿Ğ¸Ğ½ÑŒĞ¾Ğ½Ñ‹", "type": "vegetable", "percent": 20}
        ],
        "keywords": ["Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ°Ñ� Ğ¿Ğ¸Ñ†Ñ†Ğ°", "mushroom pizza"]
    },
    "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹": {
        "name": "ĞŸĞ¸Ñ†Ñ†Ğ° Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
        "name_en": ["chicken pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 230, "protein": 12.0, "fat": 8.0, "carbs": 28.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ğ»Ñ� Ğ¿Ğ¸Ñ†Ñ†Ñ‹", "type": "carb", "percent": 45},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğ¹", "type": "sauce", "percent": 12},
            {"name": "Ñ�Ñ‹Ñ€ Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 20},
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 15},
            {"name": "ÑˆĞ°Ğ¼Ğ¿Ğ¸Ğ½ÑŒĞ¾Ğ½Ñ‹", "type": "vegetable", "percent": 8}
        ],
        "keywords": ["chicken pizza", "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹"]
    },
    
    # ==================== Ğ‘Ğ�Ğ£Ğ›Ğ« Ğ˜ ĞŸĞ�Ğ›Ğ•Ğ—Ğ�Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� ====================
    "Ğ±Ğ¾ÑƒĞ» Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼ Ğ¸ Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾": {
        "name": "Ğ‘Ğ¾ÑƒĞ» Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼ Ğ¸ Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾",
        "name_en": ["salmon and avocado bowl"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 130, "protein": 8.0, "fat": 6.0, "carbs": 11.0},
        "ingredients": [
            {"name": "Ñ€Ğ¸Ñ� Ğ±ÑƒÑ€Ñ‹Ğ¹", "type": "carb", "percent": 30},
            {"name": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ñ�Ğ»Ğ°Ğ±Ğ¾Ñ�Ğ¾Ğ»ĞµĞ½Ñ‹Ğ¹", "type": "protein", "percent": 20},
            {"name": "Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾", "type": "fruit", "percent": 15},
            {"name": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†", "type": "vegetable", "percent": 10},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ´Ğ°Ğ¼Ğ°Ğ¼Ğµ", "type": "protein", "percent": 7},
            {"name": "Ğ²Ğ¾Ğ´Ğ¾Ñ€Ğ¾Ñ�Ğ»Ğ¸ Ğ½Ğ¾Ñ€Ğ¸", "type": "vegetable", "percent": 5},
            {"name": "ĞºÑƒĞ½Ğ¶ÑƒÑ‚", "type": "seed", "percent": 5}
        ],
        "keywords": ["Ğ±Ğ¾ÑƒĞ»", "bowl", "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ", "Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾", "Ğ¿Ğ¿"]
    },
    "Ğ±Ğ¾ÑƒĞ» Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹ Ğ¸ ĞºĞ¸Ğ½Ğ¾Ğ°": {
        "name": "Ğ‘Ğ¾ÑƒĞ» Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹ Ğ¸ ĞºĞ¸Ğ½Ğ¾Ğ°",
        "name_en": ["chicken quinoa bowl"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 120, "protein": 10.0, "fat": 4.0, "carbs": 11.0},
        "ingredients": [
            {"name": "ĞºĞ¸Ğ½Ğ¾Ğ°", "type": "carb", "percent": 30},
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 25},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ñ‡ĞµÑ€Ñ€Ğ¸", "type": "vegetable", "percent": 12},
            {"name": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ğ¿ĞµÑ�Ñ‚Ğ¾", "type": "sauce", "percent": 8},
            {"name": "Ñ€ÑƒĞºĞºĞ¾Ğ»Ğ°", "type": "vegetable", "percent": 7}
        ],
        "keywords": ["Ğ±Ğ¾ÑƒĞ»", "bowl", "ĞºĞ¸Ğ½Ğ¾Ğ°", "quinoa", "Ğ¿Ğ¿"]
    },
    "Ğ±Ğ¾ÑƒĞ» Ñ� Ğ¾Ğ²Ğ¾Ñ‰Ğ°Ğ¼Ğ¸ Ğ¸ Ñ…ÑƒĞ¼ÑƒÑ�Ğ¾Ğ¼": {
        "name": "Ğ�Ğ²Ğ¾Ñ‰Ğ½Ğ¾Ğ¹ Ğ±Ğ¾ÑƒĞ» Ñ� Ñ…ÑƒĞ¼ÑƒÑ�Ğ¾Ğ¼",
        "name_en": ["vegetable bowl with hummus"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 100, "protein": 4.0, "fat": 4.0, "carbs": 13.0},
        "ingredients": [
            {"name": "Ğ±ÑƒĞ»Ğ³ÑƒÑ€", "type": "carb", "percent": 30},
            {"name": "Ñ…ÑƒĞ¼ÑƒÑ�", "type": "sauce", "percent": 15},
            {"name": "Ğ½ÑƒÑ‚", "type": "protein", "percent": 10},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ñ‡ĞµÑ€Ñ€Ğ¸", "type": "vegetable", "percent": 12},
            {"name": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 8},
            {"name": "Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾", "type": "fruit", "percent": 8},
            {"name": "Ñ€ÑƒĞºĞºĞ¾Ğ»Ğ°", "type": "vegetable", "percent": 7}
        ],
        "keywords": ["Ğ±Ğ¾ÑƒĞ»", "bowl", "Ğ²ĞµĞ³Ğ°Ğ½", "vegan", "Ñ…ÑƒĞ¼ÑƒÑ�"]
    },
    "Ñ�Ñ�Ğ½Ğ´Ğ²Ğ¸Ñ‡ Ñ� Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾ Ğ¸ Ñ�Ğ¹Ñ†Ğ¾Ğ¼": {
        "name": "Ğ¡Ñ�Ğ½Ğ´Ğ²Ğ¸Ñ‡ Ñ� Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾ Ğ¸ Ñ�Ğ¹Ñ†Ğ¾Ğ¼",
        "name_en": ["avocado egg sandwich"],
        "category": "sandwich",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 10.0, "carbs": 15.0},
        "ingredients": [
            {"name": "Ñ‚Ğ¾Ñ�Ñ‚Ğ¾Ğ²Ñ‹Ğ¹ Ñ…Ğ»ĞµĞ±", "type": "carb", "percent": 40},
            {"name": "Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾", "type": "fruit", "percent": 25},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾ Ğ¿Ğ°ÑˆĞ¾Ñ‚", "type": "protein", "percent": 15},
            {"name": "Ñ€ÑƒĞºĞºĞ¾Ğ»Ğ°", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ğ¿ĞµÑ�Ñ‚Ğ¾", "type": "sauce", "percent": 7},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["Ñ�Ñ�Ğ½Ğ´Ğ²Ğ¸Ñ‡", "avocado toast", "sandwich"]
    },
    "Ñ�Ñ�Ğ½Ğ´Ğ²Ğ¸Ñ‡ Ñ� Ğ¸Ğ½Ğ´ĞµĞ¹ĞºĞ¾Ğ¹": {
        "name": "Ğ¡Ñ�Ğ½Ğ´Ğ²Ğ¸Ñ‡ Ñ� Ğ¸Ğ½Ğ´ĞµĞ¹ĞºĞ¾Ğ¹",
        "name_en": ["turkey sandwich"],
        "category": "sandwich",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 12.0, "fat": 5.0, "carbs": 17.0},
        "ingredients": [
            {"name": "Ñ…Ğ»ĞµĞ± Ñ†ĞµĞ»ÑŒĞ½Ğ¾Ğ·ĞµÑ€Ğ½Ğ¾Ğ²Ğ¾Ğ¹", "type": "carb", "percent": 40},
            {"name": "Ğ¸Ğ½Ğ´ĞµĞ¹ĞºĞ°", "type": "protein", "percent": 30},
            {"name": "Ñ�Ğ°Ğ»Ğ°Ñ‚", "type": "vegetable", "percent": 10},
            {"name": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹", "type": "vegetable", "percent": 8},
            {"name": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†", "type": "vegetable", "percent": 5},
            {"name": "Ğ¹Ğ¾Ğ³ÑƒÑ€Ñ‚Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 7}
        ],
        "keywords": ["Ñ�Ñ�Ğ½Ğ´Ğ²Ğ¸Ñ‡", "turkey sandwich", "Ğ¸Ğ½Ğ´ĞµĞ¹ĞºĞ°"]
    },
    
    # ==================== Ğ‘Ğ›Ğ®Ğ”Ğ� Ğ˜Ğ— ĞšĞ�ĞŸĞ£Ğ¡Ğ¢Ğ« (Ğ¢Ğ Ğ•Ğ�Ğ” 2026) ====================
    "Ñ�Ñ‚ĞµĞ¹Ğº Ğ¸Ğ· ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ñ‹": {
        "name": "Ğ¡Ñ‚ĞµĞ¹Ğº Ğ¸Ğ· ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ñ‹",
        "name_en": ["cabbage steak", "grilled cabbage steak"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 70, "protein": 3.0, "fat": 3.0, "carbs": 8.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° Ğ±ĞµĞ»Ğ¾ĞºĞ¾Ñ‡Ğ°Ğ½Ğ½Ğ°Ñ�", "type": "vegetable", "percent": 80},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ñ‚Ğ¸Ğ¼ÑŒÑ�Ğ½", "type": "spice", "percent": 2},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "other", "percent": 5}
        ],
        "keywords": ["Ñ�Ñ‚ĞµĞ¹Ğº Ğ¸Ğ· ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ñ‹", "cabbage steak", "Ñ‚Ñ€ĞµĞ½Ğ´ 2026"]
    },
    "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ñ�Ğ±Ğ»Ğ¾ĞºĞ¾Ğ¼": {
        "name": "Ğ¡Ğ°Ğ»Ğ°Ñ‚ Ğ¸Ğ· ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ñ‹ Ñ� Ñ�Ğ±Ğ»Ğ¾ĞºĞ¾Ğ¼",
        "name_en": ["cabbage and apple salad"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 60, "protein": 2.0, "fat": 2.5, "carbs": 7.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° Ğ±ĞµĞ»Ğ¾ĞºĞ¾Ñ‡Ğ°Ğ½Ğ½Ğ°Ñ�", "type": "vegetable", "percent": 60},
            {"name": "Ñ�Ğ±Ğ»Ğ¾ĞºĞ¾", "type": "fruit", "percent": 20},
            {"name": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ", "type": "vegetable", "percent": 10},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 3},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ", "type": "fat", "percent": 5},
            {"name": "Ğ·ĞµĞ»ĞµĞ½ÑŒ", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚", "cabbage salad", "Ñ‚Ñ€ĞµĞ½Ğ´ 2026"]
    },
    "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğµ ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹": {
        "name": "ĞšĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğµ ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹",
        "name_en": ["cabbage patties", "cabbage cutlets"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 4.0, "fat": 5.0, "carbs": 15.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "type": "vegetable", "percent": 60},
            {"name": "Ñ�Ğ¹Ñ†Ğ¾", "type": "protein", "percent": 8},
            {"name": "Ğ¼Ğ°Ğ½Ğ½Ğ°Ñ� ĞºÑ€ÑƒĞ¿Ğ°", "type": "carb", "percent": 12},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğµ Ñ�ÑƒÑ…Ğ°Ñ€Ğ¸", "type": "carb", "percent": 7},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğµ ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹", "cabbage cutlets", "Ğ¿Ğ¾Ñ�Ñ‚Ğ½Ñ‹Ğµ"]
    },
    "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° Ñ‚ÑƒÑˆĞµĞ½Ğ°Ñ� Ñ� Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²Ğ¾Ğ¼": {
        "name": "ĞšĞ°Ğ¿ÑƒÑ�Ñ‚Ğ° Ñ‚ÑƒÑˆĞµĞ½Ğ°Ñ� Ñ� Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²Ğ¾Ğ¼",
        "name_en": ["stewed cabbage with prunes"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 80, "protein": 2.5, "fat": 2.0, "carbs": 13.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "type": "vegetable", "percent": 70},
            {"name": "Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²", "type": "fruit", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 2}
        ],
        "keywords": ["Ñ‚ÑƒÑˆĞµĞ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°", "stewed cabbage", "Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²"]
    },
    "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğµ Ñ€ÑƒĞ»ĞµÑ‚Ğ¸ĞºĞ¸ Ñ� Ñ�Ñ‹Ñ€Ğ¾Ğ¼": {
        "name": "ĞšĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğµ Ñ€ÑƒĞ»ĞµÑ‚Ğ¸ĞºĞ¸ Ñ� Ñ�Ñ‹Ñ€Ğ¾Ğ¼",
        "name_en": ["cabbage rolls with cheese"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 6.0, "fat": 8.0, "carbs": 10.0},
        "ingredients": [
            {"name": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğµ Ğ»Ğ¸Ñ�Ñ‚ÑŒÑ�", "type": "vegetable", "percent": 40},
            {"name": "Ñ�Ñ‹Ñ€", "type": "dairy", "percent": 30},
            {"name": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³", "type": "dairy", "percent": 15},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 10}
        ],
        "keywords": ["ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ½Ñ‹Ğµ Ñ€ÑƒĞ»ĞµÑ‚Ğ¸ĞºĞ¸", "cabbage rolls"]
    },
    
    # ==================== Ğ˜Ğ�Ğ”Ğ˜Ğ™Ğ¡ĞšĞ�Ğ¯ ĞšĞ£Ğ¥Ğ�Ğ¯ (FAST-CASUAL) ====================
    "Ñ‚Ğ¸ĞºĞºĞ° Ğ¼Ğ°Ñ�Ğ°Ğ»Ğ°": {
        "name": "Ğ¢Ğ¸ĞºĞºĞ° Ğ¼Ğ°Ñ�Ğ°Ğ»Ğ°",
        "name_en": ["chicken tikka masala"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 12.0, "fat": 10.0, "carbs": 9.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°", "type": "protein", "percent": 40},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 25},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 15},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸ (Ğ³Ğ°Ñ€Ğ°Ğ¼ Ğ¼Ğ°Ñ�Ğ°Ğ»Ğ°)", "type": "spice", "percent": 7},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ‚Ğ¾Ğ¿Ğ»ĞµĞ½Ğ¾Ğµ", "type": "fat", "percent": 5}
        ],
        "keywords": ["tikka masala", "Ğ¸Ğ½Ğ´Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¹", "curry"]
    },
    "Ğ¿Ğ°Ğ½Ğ¸Ñ€ Ñ‚Ğ¸ĞºĞºĞ°": {
        "name": "ĞŸĞ°Ğ½Ğ¸Ñ€ Ñ‚Ğ¸ĞºĞºĞ°",
        "name_en": ["paneer tikka"],
        "category": "appetizer",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 10.0, "fat": 14.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€", "type": "dairy", "percent": 60},
            {"name": "Ğ¹Ğ¾Ğ³ÑƒÑ€Ñ‚", "type": "dairy", "percent": 15},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 7}
        ],
        "keywords": ["paneer", "Ñ‚Ğ¸ĞºĞºĞ°", "Ğ¸Ğ½Ğ´Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ñ�Ğ°Ğ³ Ğ¿Ğ°Ğ½Ğ¸Ñ€": {
        "name": "Ğ¡Ğ°Ğ³ Ğ¿Ğ°Ğ½Ğ¸Ñ€",
        "name_en": ["saag paneer"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 11.0, "carbs": 6.0},
        "ingredients": [
            {"name": "Ğ¿Ğ°Ğ½Ğ¸Ñ€", "type": "dairy", "percent": 40},
            {"name": "ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚", "type": "vegetable", "percent": 35},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 3},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 7}
        ],
        "keywords": ["saag paneer", "Ğ¸Ğ½Ğ´Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¹", "ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚"]
    },
    "Ğ´Ğ°Ğ» Ğ¼Ğ°ĞºÑ…Ğ°Ğ½Ğ¸": {
        "name": "Ğ”Ğ°Ğ» Ğ¼Ğ°ĞºÑ…Ğ°Ğ½Ğ¸",
        "name_en": ["dal makhani"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 140, "protein": 7.0, "fat": 6.0, "carbs": 15.0},
        "ingredients": [
            {"name": "Ñ‡ĞµÑ€Ğ½Ğ°Ñ� Ñ‡ĞµÑ‡ĞµĞ²Ğ¸Ñ†Ğ°", "type": "protein", "percent": 50},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 15},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ°Ñ�Ñ‚Ğ°", "type": "sauce", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ğ¸Ğ¼Ğ±Ğ¸Ñ€ÑŒ", "type": "spice", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ‚Ğ¾Ğ¿Ğ»ĞµĞ½Ğ¾Ğµ", "type": "fat", "percent": 7}
        ],
        "keywords": ["dal makhani", "Ğ¸Ğ½Ğ´Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¹", "Ñ‡ĞµÑ‡ĞµĞ²Ğ¸Ñ†Ğ°"]
    },
    "Ñ‡Ğ°Ğ½Ğ° Ğ¼Ğ°Ñ�Ğ°Ğ»Ğ°": {
        "name": "Ğ§Ğ°Ğ½Ğ° Ğ¼Ğ°Ñ�Ğ°Ğ»Ğ°",
        "name_en": ["chana masala"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 130, "protein": 6.0, "fat": 5.0, "carbs": 16.0},
        "ingredients": [
            {"name": "Ğ½ÑƒÑ‚", "type": "protein", "percent": 60},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 20},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 8},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 4}
        ],
        "keywords": ["chana masala", "Ğ½ÑƒÑ‚", "Ğ¸Ğ½Ğ´Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¹"]
    },
    "Ñ�Ğ°Ğ¼Ğ¾Ñ�Ğ° Ñ� Ğ¼Ñ�Ñ�Ğ¾Ğ¼": {
        "name": "Ğ¡Ğ°Ğ¼Ğ¾Ñ�Ğ° Ñ� Ğ¼Ñ�Ñ�Ğ¾Ğ¼",
        "name_en": ["meat samosa"],
        "category": "appetizer",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 270, "protein": 9.0, "fat": 15.0, "carbs": 25.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾", "type": "carb", "percent": 45},
            {"name": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ¹ Ñ„Ğ°Ñ€Ñˆ", "type": "protein", "percent": 30},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 10},
            {"name": "Ğ³Ğ¾Ñ€Ğ¾ÑˆĞµĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¿ĞµÑ†Ğ¸Ğ¸", "type": "spice", "percent": 7}
        ],
        "keywords": ["Ñ�Ğ°Ğ¼Ğ¾Ñ�Ğ°", "samosa", "Ğ¸Ğ½Ğ´Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ¶Ğ¾Ğº"]
    },
    
    # ==================== Ğ¡Ğ›Ğ�Ğ”ĞšĞ�-Ğ�Ğ¡Ğ¢Ğ Ğ«Ğ• Ğ‘Ğ›Ğ®Ğ”Ğ� (Ğ¢Ğ Ğ•Ğ�Ğ” 2026) ====================
    "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ñ� Ğ¼ĞµĞ´Ğ¾Ğ¼ Ğ¸ Ñ‡Ğ¸Ğ»Ğ¸": {
        "name": "ĞšÑƒÑ€Ğ¸Ñ†Ğ° Ñ� Ğ¼ĞµĞ´Ğ¾Ğ¼ Ğ¸ Ñ‡Ğ¸Ğ»Ğ¸",
        "name_en": ["honey chili chicken"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 190, "protein": 18.0, "fat": 7.0, "carbs": 14.0},
        "ingredients": [
            {"name": "ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğµ Ñ„Ğ¸Ğ»Ğµ", "type": "protein", "percent": 60},
            {"name": "Ğ¼ĞµĞ´", "type": "sugar", "percent": 15},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ�Ğ¾ĞµĞ²Ñ‹Ğ¹", "type": "sauce", "percent": 10},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ñ‡Ğ¸Ğ»Ğ¸", "type": "vegetable", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["honey chili", "Ñ�Ğ»Ğ°Ğ´ĞºĞ¾-Ğ¾Ñ�Ñ‚Ñ€Ñ‹Ğ¹", "Ñ‚Ñ€ĞµĞ½Ğ´"]
    },
    "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ° Ğ² ĞºĞ¸Ñ�Ğ»Ğ¾-Ñ�Ğ»Ğ°Ğ´ĞºĞ¾Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğµ": {
        "name": "Ğ¡Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ° Ğ² ĞºĞ¸Ñ�Ğ»Ğ¾-Ñ�Ğ»Ğ°Ğ´ĞºĞ¾Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğµ",
        "name_en": ["sweet and sour pork"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 14.0, "fat": 9.0, "carbs": 20.0},
        "ingredients": [
            {"name": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°", "type": "protein", "percent": 45},
            {"name": "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�", "type": "fruit", "percent": 15},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "vegetable", "percent": 10},
            {"name": "Ğ»ÑƒĞº", "type": "vegetable", "percent": 8},
            {"name": "Ñ�Ğ¾ÑƒÑ� ĞºĞ¸Ñ�Ğ»Ğ¾-Ñ�Ğ»Ğ°Ğ´ĞºĞ¸Ğ¹", "type": "sauce", "percent": 20},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 2}
        ],
        "keywords": ["sweet and sour", "ĞºĞ¸Ñ�Ğ»Ğ¾-Ñ�Ğ»Ğ°Ğ´ĞºĞ¸Ğ¹", "ĞºĞ¸Ñ‚Ğ°Ğ¹Ñ�ĞºĞ¸Ğ¹"]
    },
    "ĞºÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸ Ñ� Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ¼ Ğ¸ Ñ‡Ğ¸Ğ»Ğ¸": {
        "name": "ĞšÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸ Ñ� Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ¼ Ğ¸ Ñ‡Ğ¸Ğ»Ğ¸",
        "name_en": ["orange chili shrimp"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 140, "protein": 16.0, "fat": 4.0, "carbs": 10.0},
        "ingredients": [
            {"name": "ĞºÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸", "type": "protein", "percent": 60},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½", "type": "fruit", "percent": 20},
            {"name": "Ğ¿ĞµÑ€ĞµÑ† Ñ‡Ğ¸Ğ»Ğ¸", "type": "vegetable", "percent": 5},
            {"name": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ�Ğ¾ĞµĞ²Ñ‹Ğ¹", "type": "sauce", "percent": 5},
            {"name": "Ğ¼Ğ°Ñ�Ğ»Ğ¾", "type": "fat", "percent": 5}
        ],
        "keywords": ["shrimp", "orange chili", "Ñ�Ğ»Ğ°Ğ´ĞºĞ¾-Ğ¾Ñ�Ñ‚Ñ€Ñ‹Ğ¹"]
    },
    "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ñ� Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�Ğ¾Ğ¼ Ğ¸ Ñ…Ğ°Ğ»Ğ°Ğ¿ĞµĞ½ÑŒĞ¾": {
        "name": "ĞŸĞ¸Ñ†Ñ†Ğ° Ñ� Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�Ğ¾Ğ¼ Ğ¸ Ñ…Ğ°Ğ»Ğ°Ğ¿ĞµĞ½ÑŒĞ¾",
        "name_en": ["pineapple jalapeno pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 240, "protein": 10.0, "fat": 9.0, "carbs": 30.0},
        "ingredients": [
            {"name": "Ñ‚ĞµÑ�Ñ‚Ğ¾ Ğ´Ğ»Ñ� Ğ¿Ğ¸Ñ†Ñ†Ñ‹", "type": "carb", "percent": 45},
            {"name": "Ñ�Ğ¾ÑƒÑ� Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹", "type": "sauce", "percent": 12},
            {"name": "Ñ�Ñ‹Ñ€ Ğ¼Ğ¾Ñ†Ğ°Ñ€ĞµĞ»Ğ»Ğ°", "type": "dairy", "percent": 20},
            {"name": "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�", "type": "fruit", "percent": 12},
            {"name": "Ñ…Ğ°Ğ»Ğ°Ğ¿ĞµĞ½ÑŒĞ¾", "type": "vegetable", "percent": 8},
            {"name": "Ğ²ĞµÑ‚Ñ‡Ğ¸Ğ½Ğ°", "type": "protein", "percent": 3}
        ],
        "keywords": ["pineapple jalapeno", "Ñ�Ğ»Ğ°Ğ´ĞºĞ¾-Ğ¾Ñ�Ñ‚Ñ€Ğ°Ñ� Ğ¿Ğ¸Ñ†Ñ†Ğ°"]
    },
    
    # ==================== ĞœĞ�ĞšĞ¢Ğ•Ğ™Ğ›Ğ˜ (Ğ‘Ğ•Ğ—Ğ�Ğ›ĞšĞ�Ğ“Ğ�Ğ›Ğ¬Ğ�Ğ«Ğ• ĞšĞ�ĞšĞ¢Ğ•Ğ™Ğ›Ğ˜) ====================
    "Ğ¼Ğ¾Ñ…Ğ¸Ñ‚Ğ¾ Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ñ‹Ğ¹": {
        "name": "ĞœĞ¾Ñ…Ğ¸Ñ‚Ğ¾ Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ñ‹Ğ¹",
        "name_en": ["virgin mojito", "non-alcoholic mojito"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 35, "protein": 0.2, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 10},
            {"name": "Ğ¼Ñ�Ñ‚Ğ°", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 8},
            {"name": "Ñ�Ğ¾Ğ´Ğ¾Ğ²Ğ°Ñ�", "type": "liquid", "percent": 75},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 2}
        ],
        "keywords": ["Ğ¼Ğ¾Ñ…Ğ¸Ñ‚Ğ¾", "mojito", "virgin", "Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ñ‹Ğ¹"]
    },
    "Ğ¿Ğ¸Ğ½Ğ° ĞºĞ¾Ğ»Ğ°Ğ´Ğ° Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ğ°Ñ�": {
        "name": "ĞŸĞ¸Ğ½Ğ° ĞºĞ¾Ğ»Ğ°Ğ´Ğ° Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ğ°Ñ�",
        "name_en": ["virgin pina colada"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 70, "protein": 0.3, "fat": 1.5, "carbs": 13.0},
        "ingredients": [
            {"name": "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 50},
            {"name": "ĞºĞ¾ĞºĞ¾Ñ�Ğ¾Ğ²Ğ¾Ğµ Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 30},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 15},
            {"name": "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�", "type": "fruit", "percent": 5}
        ],
        "keywords": ["pina colada", "virgin", "Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ñ‹Ğ¹"]
    },
    "Ğ±ĞµĞ»Ğ»Ğ¸Ğ½Ğ¸ Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ñ‹Ğ¹": {
        "name": "Ğ‘ĞµĞ»Ğ»Ğ¸Ğ½Ğ¸ Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ñ‹Ğ¹",
        "name_en": ["virgin bellini"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 0.3, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "Ğ¿ĞµÑ€Ñ�Ğ¸ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ", "type": "fruit", "percent": 40},
            {"name": "Ğ³Ğ°Ğ·Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°", "type": "liquid", "percent": 60}
        ],
        "keywords": ["bellini", "virgin", "Ğ±ĞµĞ·Ğ°Ğ»ĞºĞ¾Ğ³Ğ¾Ğ»ÑŒĞ½Ñ‹Ğ¹"]
    },
    "Ğ¼Ğ°Ñ‚Ñ‡Ğ°-Ğ»Ğ°Ñ‚Ñ‚Ğµ": {
        "name": "ĞœĞ°Ñ‚Ñ‡Ğ°-Ğ»Ğ°Ñ‚Ñ‚Ğµ",
        "name_en": ["matcha latte"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 45, "protein": 2.0, "fat": 1.5, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ¼Ğ°Ñ‚Ñ‡Ğ°", "type": "other", "percent": 3},
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 80},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 7},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 10}
        ],
        "keywords": ["matcha", "Ğ¼Ğ°Ñ‚Ñ‡Ğ°", "Ğ»Ğ°Ñ‚Ñ‚Ğµ", "Ñ‚Ñ€ĞµĞ½Ğ´"]
    },
    "Ğ»Ğ°Ñ‚Ñ‚Ğµ Ñ� ĞºÑƒÑ€ĞºÑƒĞ¼Ğ¾Ğ¹": {
        "name": "Ğ—Ğ¾Ğ»Ğ¾Ñ‚Ğ¾Ğµ Ğ»Ğ°Ñ‚Ñ‚Ğµ Ñ� ĞºÑƒÑ€ĞºÑƒĞ¼Ğ¾Ğ¹",
        "name_en": ["golden latte", "turmeric latte"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 40, "protein": 1.5, "fat": 1.2, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 85},
            {"name": "ĞºÑƒÑ€ĞºÑƒĞ¼Ğ°", "type": "spice", "percent": 3},
            {"name": "Ğ¸Ğ¼Ğ±Ğ¸Ñ€ÑŒ", "type": "spice", "percent": 2},
            {"name": "Ğ¼ĞµĞ´", "type": "sugar", "percent": 5},
            {"name": "Ñ‡ĞµÑ€Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€ĞµÑ†", "type": "spice", "percent": 1},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 4}
        ],
        "keywords": ["golden latte", "turmeric", "ĞºÑƒÑ€ĞºÑƒĞ¼Ğ°"]
    },
    "Ñ‡Ğ°Ğ¹ ĞºĞ¾Ğ¼Ğ±ÑƒÑ‡Ğ°": {
        "name": "ĞšĞ¾Ğ¼Ğ±ÑƒÑ‡Ğ°",
        "name_en": ["kombucha"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 15, "protein": 0.1, "fat": 0.1, "carbs": 3.0},
        "ingredients": [
            {"name": "Ñ‡Ğ°Ğ¹Ğ½Ñ‹Ğ¹ Ğ³Ñ€Ğ¸Ğ±", "type": "other", "percent": 5},
            {"name": "Ñ‡Ğ°Ğ¹", "type": "other", "percent": 10},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 80}
        ],
        "keywords": ["kombucha", "ĞºĞ¾Ğ¼Ğ±ÑƒÑ‡Ğ°", "Ñ„ĞµÑ€Ğ¼ĞµĞ½Ñ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ñ‡Ğ°Ğ¹"]
    },
    "Ğ¸Ğ¼Ğ±Ğ¸Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ»ÑŒ": {
        "name": "Ğ˜Ğ¼Ğ±Ğ¸Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ»ÑŒ",
        "name_en": ["ginger ale", "ginger beer"],
        "category": "drink",
        "default_weight": 330,
        "nutrition_per_100": {"calories": 40, "protein": 0.1, "fat": 0.1, "carbs": 10.0},
        "ingredients": [
            {"name": "Ğ¸Ğ¼Ğ±Ğ¸Ñ€ÑŒ", "type": "spice", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "carb", "percent": 8},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ñ‹", "type": "fruit", "percent": 5},
            {"name": "Ğ³Ğ°Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ� Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 80},
            {"name": "Ğ´Ñ€Ğ¾Ğ¶Ğ¶Ğ¸", "type": "other", "percent": 2}
        ],
        "keywords": ["ginger ale", "Ğ¸Ğ¼Ğ±Ğ¸Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ»ÑŒ"]
    },
    "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´ Ñ� Ğ±Ğ°Ğ·Ğ¸Ğ»Ğ¸ĞºĞ¾Ğ¼": {
        "name": "Ğ›Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´ Ñ� Ğ±Ğ°Ğ·Ğ¸Ğ»Ğ¸ĞºĞ¾Ğ¼",
        "name_en": ["basil lemonade"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 35, "protein": 0.2, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ñ‹", "type": "fruit", "percent": 15},
            {"name": "Ğ±Ğ°Ğ·Ğ¸Ğ»Ğ¸Ğº", "type": "vegetable", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 8},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 70},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 2}
        ],
        "keywords": ["basil lemonade", "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´ Ñ� Ğ±Ğ°Ğ·Ğ¸Ğ»Ğ¸ĞºĞ¾Ğ¼"]
    },
    "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´ Ñ� Ğ¾Ğ³ÑƒÑ€Ñ†Ğ¾Ğ¼ Ğ¸ Ğ¼Ñ�Ñ‚Ğ¾Ğ¹": {
        "name": "Ğ›Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´ Ñ� Ğ¾Ğ³ÑƒÑ€Ñ†Ğ¾Ğ¼ Ğ¸ Ğ¼Ñ�Ñ‚Ğ¾Ğ¹",
        "name_en": ["cucumber mint lemonade"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 30, "protein": 0.2, "fat": 0.1, "carbs": 7.0},
        "ingredients": [
            {"name": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†", "type": "vegetable", "percent": 15},
            {"name": "Ğ¼Ñ�Ñ‚Ğ°", "type": "vegetable", "percent": 5},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 8},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 7},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 63},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 2}
        ],
        "keywords": ["cucumber lemonade", "Ğ¾Ğ³ÑƒÑ€ĞµÑ‡Ğ½Ñ‹Ğ¹ Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´"]
    },
    "Ñ„Ñ€ĞµÑˆ Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹": {
        "name": "Ğ¤Ñ€ĞµÑˆ Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹",
        "name_en": ["fresh orange juice"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 10.0},
        "ingredients": [
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ñ‹", "type": "fruit", "percent": 100}
        ],
        "keywords": ["fresh", "Ñ„Ñ€ĞµÑˆ", "orange juice"]
    },
    "Ñ�Ğ¼ÑƒĞ·Ğ¸ Ğ±Ğ°Ğ½Ğ°Ğ½Ğ¾Ğ²Ğ¾-ĞºĞ»ÑƒĞ±Ğ½Ğ¸Ñ‡Ğ½Ñ‹Ğ¹": {
        "name": "Ğ¡Ğ¼ÑƒĞ·Ğ¸ Ğ±Ğ°Ğ½Ğ°Ğ½Ğ¾Ğ²Ğ¾-ĞºĞ»ÑƒĞ±Ğ½Ğ¸Ñ‡Ğ½Ñ‹Ğ¹",
        "name_en": ["banana strawberry smoothie"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 60, "protein": 1.0, "fat": 0.5, "carbs": 13.0},
        "ingredients": [
            {"name": "Ğ±Ğ°Ğ½Ğ°Ğ½", "type": "fruit", "percent": 30},
            {"name": "ĞºĞ»ÑƒĞ±Ğ½Ğ¸ĞºĞ°", "type": "fruit", "percent": 30},
            {"name": "Ğ¹Ğ¾Ğ³ÑƒÑ€Ñ‚", "type": "dairy", "percent": 30},
            {"name": "Ğ¼ĞµĞ´", "type": "sugar", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 5}
        ],
        "keywords": ["smoothie", "Ñ�Ğ¼ÑƒĞ·Ğ¸", "Ğ±Ğ°Ğ½Ğ°Ğ½", "ĞºĞ»ÑƒĞ±Ğ½Ğ¸ĞºĞ°"]
    },
    "Ñ�Ğ¼ÑƒĞ·Ğ¸ Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹": {
        "name": "Ğ—ĞµĞ»ĞµĞ½Ñ‹Ğ¹ Ñ�Ğ¼ÑƒĞ·Ğ¸",
        "name_en": ["green smoothie"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 1.5, "fat": 0.8, "carbs": 8.0},
        "ingredients": [
            {"name": "ÑˆĞ¿Ğ¸Ğ½Ğ°Ñ‚", "type": "vegetable", "percent": 30},
            {"name": "Ñ�Ğ±Ğ»Ğ¾ĞºĞ¾", "type": "fruit", "percent": 25},
            {"name": "Ñ�ĞµĞ»ÑŒĞ´ĞµÑ€ĞµĞ¹", "type": "vegetable", "percent": 15},
            {"name": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†", "type": "vegetable", "percent": 15},
            {"name": "Ğ¸Ğ¼Ğ±Ğ¸Ñ€ÑŒ", "type": "spice", "percent": 3},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½", "type": "fruit", "percent": 2},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 10}
        ],
        "keywords": ["green smoothie", "Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹ Ñ�Ğ¼ÑƒĞ·Ğ¸", "Ğ´ĞµÑ‚Ğ¾ĞºÑ�"]
    },

    # =============================================================================
    # ğŸ�¸ Ğ�Ğ›ĞšĞ�Ğ“Ğ�Ğ›Ğ¬Ğ�Ğ«Ğ• ĞšĞ�ĞšĞ¢Ğ•Ğ™Ğ›Ğ˜ Ğ˜ Ğ¨Ğ�Ğ¢Ğ«
    # =============================================================================
    
    # ==================== ĞšĞ›Ğ�Ğ¡Ğ¡Ğ˜Ğ§Ğ•Ğ¡ĞšĞ˜Ğ• Ğ›Ğ�Ğ�Ğ“-Ğ”Ğ Ğ˜Ğ�ĞšĞ˜ ====================
    "Ğ¼Ğ¾Ñ…Ğ¸Ñ‚Ğ¾": {
        "name": "ĞœĞ¾Ñ…Ğ¸Ñ‚Ğ¾",
        "name_en": ["Mojito", "Mint Mojito"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 0.2, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ñ�Ğ²ĞµÑ‚Ğ»Ñ‹Ğ¹ Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 15},
            {"name": "Ğ¼Ñ�Ñ‚Ğ°", "type": "vegetable", "percent": 2},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 8},
            {"name": "Ñ�Ğ¾Ğ´Ğ¾Ğ²Ğ°Ñ�", "type": "liquid", "percent": 40},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["Ğ¼Ğ¾Ñ…Ğ¸Ñ‚Ğ¾", "mojito", "Ñ€Ğ¾Ğ¼", "Ğ¼Ñ�Ñ‚Ğ°", "Ğ»Ğ°Ğ¹Ğ¼", "ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ğ¿Ğ¸Ğ½Ğ° ĞºĞ¾Ğ»Ğ°Ğ´Ğ°": {
        "name": "ĞŸĞ¸Ğ½Ğ° ĞšĞ¾Ğ»Ğ°Ğ´Ğ°",
        "name_en": ["PiÃ±a Colada"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 70, "protein": 0.3, "fat": 1.5, "carbs": 12.0},
        "ingredients": [
            {"name": "Ğ±ĞµĞ»Ñ‹Ğ¹ Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 15},
            {"name": "ĞºĞ¾ĞºĞ¾Ñ�Ğ¾Ğ²Ğ¾Ğµ Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾", "type": "dairy", "percent": 20},
            {"name": "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 35},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["Ğ¿Ğ¸Ğ½Ğ° ĞºĞ¾Ğ»Ğ°Ğ´Ğ°", "pina colada", "ĞºĞ¾ĞºĞ¾Ñ�", "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�", "ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "ĞºÑƒĞ±Ğ° Ğ»Ğ¸Ğ±Ñ€Ğµ": {
        "name": "ĞšÑƒĞ±Ğ° Ğ›Ğ¸Ğ±Ñ€Ğµ",
        "name_en": ["Cuba Libre", "Rum and Coke"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 50, "protein": 0.1, "fat": 0.1, "carbs": 7.0},
        "ingredients": [
            {"name": "Ñ�Ğ²ĞµÑ‚Ğ»Ñ‹Ğ¹ Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 15},
            {"name": "ĞºĞ¾Ğ»Ğ°", "type": "liquid", "percent": 45},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 35}
        ],
        "keywords": ["cuba libre", "ĞºÑƒĞ±Ğ° Ğ»Ğ¸Ğ±Ñ€Ğµ", "Ñ€Ğ¾Ğ¼ Ñ� ĞºĞ¾Ğ»Ğ¾Ğ¹", "rum and coke"]
    },
    "Ğ´Ğ¶Ğ¸Ğ½-Ñ‚Ğ¾Ğ½Ğ¸Ğº": {
        "name": "Ğ”Ğ¶Ğ¸Ğ½-Ñ‚Ğ¾Ğ½Ğ¸Ğº",
        "name_en": ["Gin and Tonic", "Gin Tonic"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 55, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 15},
            {"name": "Ñ‚Ğ¾Ğ½Ğ¸Ğº", "type": "liquid", "percent": 50},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 3},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 32}
        ],
        "keywords": ["Ğ´Ğ¶Ğ¸Ğ½ Ñ‚Ğ¾Ğ½Ğ¸Ğº", "gin tonic", "gin and tonic"]
    },
    "Ğ¾Ñ‚Ğ²ĞµÑ€Ñ‚ĞºĞ°": {
        "name": "Ğ�Ñ‚Ğ²ĞµÑ€Ñ‚ĞºĞ°",
        "name_en": ["Screwdriver"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 55, "protein": 0.3, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 20},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 50},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["Ğ¾Ñ‚Ğ²ĞµÑ€Ñ‚ĞºĞ°", "screwdriver", "Ğ²Ğ¾Ğ´ĞºĞ° Ñ� Ñ�Ğ¾ĞºĞ¾Ğ¼"]
    },
    "ĞºÑ€Ğ¾Ğ²Ğ°Ğ²Ğ°Ñ� Ğ¼Ñ�Ñ€Ğ¸": {
        "name": "ĞšÑ€Ğ¾Ğ²Ğ°Ğ²Ğ°Ñ� ĞœÑ�Ñ€Ğ¸",
        "name_en": ["Bloody Mary"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 45, "protein": 0.5, "fat": 0.2, "carbs": 3.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 15},
            {"name": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "vegetable", "percent": 50},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 5},
            {"name": "Ğ²ÑƒÑ�Ñ‚ĞµÑ€Ñ�ĞºĞ¸Ğ¹ Ñ�Ğ¾ÑƒÑ�", "type": "sauce", "percent": 1},
            {"name": "Ñ‚Ğ°Ğ±Ğ°Ñ�ĞºĞ¾", "type": "sauce", "percent": 1},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "spice", "percent": 1},
            {"name": "Ğ¿ĞµÑ€ĞµÑ†", "type": "spice", "percent": 1},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 26}
        ],
        "keywords": ["bloody mary", "ĞºÑ€Ğ¾Ğ²Ğ°Ğ²Ğ°Ñ� Ğ¼Ñ�Ñ€Ğ¸", "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "Ğ²Ğ¾Ğ´ĞºĞ°"]
    },
    "Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°": {
        "name": "ĞœĞ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°",
        "name_en": ["Margarita"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 70, "protein": 0.2, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ‚ĞµĞºĞ¸Ğ»Ğ°", "type": "alcohol", "percent": 20},
            {"name": "Ñ‚Ñ€Ğ¸Ğ¿Ğ» Ñ�ĞµĞº", "type": "alcohol", "percent": 10},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 8},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 62}
        ],
        "keywords": ["margarita", "Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°", "Ñ‚ĞµĞºĞ¸Ğ»Ğ°", "Ñ‚Ñ€Ğ¸Ğ¿Ğ» Ñ�ĞµĞº"]
    },
    "Ñ‚ĞµĞºĞ¸Ğ»Ğ° Ñ�Ğ°Ğ½Ñ€Ğ°Ğ¹Ğ·": {
        "name": "Ğ¢ĞµĞºĞ¸Ğ»Ğ° Ğ¡Ğ°Ğ½Ñ€Ğ°Ğ¹Ğ·",
        "name_en": ["Tequila Sunrise"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 65, "protein": 0.3, "fat": 0.1, "carbs": 7.0},
        "ingredients": [
            {"name": "Ñ‚ĞµĞºĞ¸Ğ»Ğ°", "type": "alcohol", "percent": 15},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 45},
            {"name": "Ğ³Ñ€ĞµĞ½Ğ°Ğ´Ğ¸Ğ½", "type": "sugar", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 35}
        ],
        "keywords": ["tequila sunrise", "Ñ‚ĞµĞºĞ¸Ğ»Ğ° Ñ�Ğ°Ğ½Ñ€Ğ°Ğ¹Ğ·", "Ğ²Ğ¾Ñ�Ñ…Ğ¾Ğ´ Ñ�Ğ¾Ğ»Ğ½Ñ†Ğ°"]
    },
    "Ğ»Ğ¾Ğ½Ğ³ Ğ°Ğ¹Ğ»ĞµĞ½Ğ´": {
        "name": "Ğ›Ğ¾Ğ½Ğ³-Ğ�Ğ¹Ğ»ĞµĞ½Ğ´",
        "name_en": ["Long Island Iced Tea"],
        "category": "drink",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 80, "protein": 0.2, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 5},
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 5},
            {"name": "Ğ±ĞµĞ»Ñ‹Ğ¹ Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 5},
            {"name": "Ñ‚ĞµĞºĞ¸Ğ»Ğ°", "type": "alcohol", "percent": 5},
            {"name": "Ñ‚Ñ€Ğ¸Ğ¿Ğ» Ñ�ĞµĞº", "type": "alcohol", "percent": 5},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 8},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 5},
            {"name": "ĞºĞ¾Ğ»Ğ°", "type": "liquid", "percent": 22},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 40}
        ],
        "keywords": ["long island", "Ğ»Ğ¾Ğ½Ğ³ Ğ°Ğ¹Ğ»ĞµĞ½Ğ´", "iced tea"]
    },
    "Ğ°Ğ¿ĞµÑ€Ğ¾Ğ»ÑŒ ÑˆĞ¿Ñ€Ğ¸Ñ†": {
        "name": "Ğ�Ğ¿ĞµÑ€Ğ¾Ğ»ÑŒ Ğ¨Ğ¿Ñ€Ğ¸Ñ†",
        "name_en": ["Aperol Spritz"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 60, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ°Ğ¿ĞµÑ€Ğ¾Ğ»ÑŒ", "type": "alcohol", "percent": 15},
            {"name": "Ğ¿Ñ€Ğ¾Ñ�ĞµĞºĞºĞ¾", "type": "alcohol", "percent": 30},
            {"name": "Ñ�Ğ¾Ğ´Ğ¾Ğ²Ğ°Ñ�", "type": "liquid", "percent": 15},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½", "type": "fruit", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 35}
        ],
        "keywords": ["aperol spritz", "Ğ°Ğ¿ĞµÑ€Ğ¾Ğ»ÑŒ ÑˆĞ¿Ñ€Ğ¸Ñ†", "Ğ¸Ñ‚Ğ°Ğ»ÑŒÑ�Ğ½Ñ�ĞºĞ¸Ğ¹ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ğ¼Ğ¸Ğ¼Ğ¾Ğ·Ğ°": {
        "name": "ĞœĞ¸Ğ¼Ğ¾Ğ·Ğ°",
        "name_en": ["Mimosa"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 55, "protein": 0.3, "fat": 0.1, "carbs": 4.0},
        "ingredients": [
            {"name": "ÑˆĞ°Ğ¼Ğ¿Ğ°Ğ½Ñ�ĞºĞ¾Ğµ", "type": "alcohol", "percent": 50},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 50}
        ],
        "keywords": ["mimosa", "Ğ¼Ğ¸Ğ¼Ğ¾Ğ·Ğ°", "ÑˆĞ°Ğ¼Ğ¿Ğ°Ğ½Ñ�ĞºĞ¾Ğµ Ñ� Ñ�Ğ¾ĞºĞ¾Ğ¼"]
    },
    "Ñ�ĞµĞ²ĞµÑ€Ğ½Ğ¾Ğµ Ñ�Ğ¸Ñ�Ğ½Ğ¸Ğµ": {
        "name": "Ğ¡ĞµĞ²ĞµÑ€Ğ½Ğ¾Ğµ Ñ�Ğ¸Ñ�Ğ½Ğ¸Ğµ",
        "name_en": ["Northern Lights", "Aurora Borealis"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 65, "protein": 0.2, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 20},
            {"name": "Ğ»Ğ¸ĞºĞµÑ€ Ğ±Ğ»Ñ� ĞºÑ�Ñ€Ğ°Ñ�Ğ°Ğ¾", "type": "alcohol", "percent": 10},
            {"name": "Ñ�Ğ¿Ñ€Ğ°Ğ¹Ñ‚", "type": "liquid", "percent": 35},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["Ñ�ĞµĞ²ĞµÑ€Ğ½Ğ¾Ğµ Ñ�Ğ¸Ñ�Ğ½Ğ¸Ğµ", "northern lights", "Ğ±Ğ»Ñ� ĞºÑ�Ñ€Ğ°Ñ�Ğ°Ğ¾"]
    },
    
    # ==================== Ğ¨Ğ�Ğ¢Ğ« (Ğ¡Ğ›Ğ�Ğ˜Ğ¡Ğ¢Ğ«Ğ• Ğ˜ Ğ¡ĞœĞ•Ğ¨Ğ�Ğ�Ğ�Ğ«Ğ•) ====================
    "Ğ±-52": {
        "name": "B-52",
        "name_en": ["B-52", "B52 Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 220, "protein": 1.0, "fat": 6.0, "carbs": 18.0},
        "ingredients": [
            {"name": "ĞºĞ¾Ñ„ĞµĞ¹Ğ½Ñ‹Ğ¹ Ğ»Ğ¸ĞºĞµÑ€", "type": "alcohol", "percent": 33},
            {"name": "Ğ°Ğ¹Ñ€Ğ¸Ñˆ ĞºÑ€Ğ¸Ğ¼", "type": "alcohol", "percent": 33},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ»Ğ¸ĞºĞµÑ€", "type": "alcohol", "percent": 34}
        ],
        "keywords": ["b-52", "b52", "ÑˆĞ¾Ñ‚", "Ñ�Ğ»Ğ¾Ğ¸Ñ�Ñ‚Ñ‹Ğ¹", "ĞºĞ¾Ñ„ĞµĞ¹Ğ½Ñ‹Ğ¹", "Ğ¸Ñ€Ğ»Ğ°Ğ½Ğ´Ñ�ĞºĞ¸Ğµ Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸"]
    },
    "ĞºĞ°Ğ¼Ğ¸ĞºĞ°Ğ´Ğ·Ğµ": {
        "name": "ĞšĞ°Ğ¼Ğ¸ĞºĞ°Ğ´Ğ·Ğµ",
        "name_en": ["Kamikaze Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 180, "protein": 0.1, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 40},
            {"name": "Ñ‚Ñ€Ğ¸Ğ¿Ğ» Ñ�ĞµĞº", "type": "alcohol", "percent": 30},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 30}
        ],
        "keywords": ["kamikaze", "ĞºĞ°Ğ¼Ğ¸ĞºĞ°Ğ´Ğ·Ğµ", "ÑˆĞ¾Ñ‚", "Ğ²Ğ¾Ğ´ĞºĞ°"]
    },
    "Ñ…Ğ¸Ñ€Ğ¾Ñ�Ğ¸Ğ¼Ğ°": {
        "name": "Ğ¥Ğ¸Ñ€Ğ¾Ñ�Ğ¸Ğ¼Ğ°",
        "name_en": ["Hiroshima Shot"],
        "category": "shot",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 200, "protein": 1.0, "fat": 5.0, "carbs": 15.0},
        "ingredients": [
            {"name": "Ñ�Ğ°Ğ¼Ğ±ÑƒĞºĞ°", "type": "alcohol", "percent": 30},
            {"name": "Ğ°Ğ¹Ñ€Ğ¸Ñˆ ĞºÑ€Ğ¸Ğ¼", "type": "alcohol", "percent": 25},
            {"name": "Ğ°Ğ±Ñ�ĞµĞ½Ñ‚", "type": "alcohol", "percent": 15},
            {"name": "Ğ³Ñ€ĞµĞ½Ğ°Ğ´Ğ¸Ğ½", "type": "sugar", "percent": 30}
        ],
        "keywords": ["hiroshima", "Ñ…Ğ¸Ñ€Ğ¾Ñ�Ğ¸Ğ¼Ğ°", "Ñ�Ğ»Ğ¾Ğ¸Ñ�Ñ‚Ñ‹Ğ¹ ÑˆĞ¾Ñ‚", "Ğ°Ğ±Ñ�ĞµĞ½Ñ‚"]
    },
    "Ğ¼ĞµĞ´ÑƒĞ·Ğ°": {
        "name": "ĞœĞµĞ´ÑƒĞ·Ğ°",
        "name_en": ["Medusa Shot"],
        "category": "shot",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 190, "protein": 1.0, "fat": 4.0, "carbs": 16.0},
        "ingredients": [
            {"name": "Ğ¼Ğ°Ğ»Ğ¸Ğ±Ñƒ", "type": "alcohol", "percent": 30},
            {"name": "ĞºÑƒĞ°Ğ½Ñ‚Ñ€Ğ¾", "type": "alcohol", "percent": 20},
            {"name": "Ğ±ĞµĞ»Ñ‹Ğ¹ Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 20},
            {"name": "Ğ±Ğ°Ğ¹Ğ»Ğ¸Ñ�", "type": "alcohol", "percent": 15},
            {"name": "Ğ±Ğ»Ñ� ĞºÑ�Ñ€Ğ°Ñ�Ğ°Ğ¾", "type": "alcohol", "percent": 15}
        ],
        "keywords": ["Ğ¼ĞµĞ´ÑƒĞ·Ğ°", "medusa", "Ñ�Ğ»Ğ¾Ğ¸Ñ�Ñ‚Ñ‹Ğ¹ ÑˆĞ¾Ñ‚", "Ñ�Ñ„Ñ„ĞµĞºÑ‚Ğ½Ñ‹Ğ¹"]
    },
    "Ñ„Ğ»Ğ°Ğ³ Ñ€Ğ¾Ñ�Ñ�Ğ¸Ğ¸": {
        "name": "Ğ¤Ğ»Ğ°Ğ³ Ğ Ğ¾Ñ�Ñ�Ğ¸Ğ¸",
        "name_en": ["Russian Flag Shot"],
        "category": "shot",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 180, "protein": 0.5, "fat": 2.0, "carbs": 14.0},
        "ingredients": [
            {"name": "Ğ³Ñ€ĞµĞ½Ğ°Ğ´Ğ¸Ğ½", "type": "sugar", "percent": 25},
            {"name": "Ğ±Ğ»Ñ� ĞºÑ�Ñ€Ğ°Ñ�Ğ°Ğ¾", "type": "alcohol", "percent": 25},
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 25},
            {"name": "Ğ±Ğ°Ğ¹Ğ»Ğ¸Ñ�", "type": "alcohol", "percent": 25}
        ],
        "keywords": ["Ñ„Ğ»Ğ°Ğ³ Ñ€Ğ¾Ñ�Ñ�Ğ¸Ğ¸", "russian flag", "Ñ‚Ñ€Ğ¸ĞºĞ¾Ğ»Ğ¾Ñ€", "Ñ�Ğ»Ğ¾Ğ¸Ñ�Ñ‚Ñ‹Ğ¹ ÑˆĞ¾Ñ‚"]
    },
    "ĞµĞ³ĞµÑ€Ğ¼ĞµĞ¹Ñ�Ñ‚ĞµÑ€ ÑˆĞ¾Ñ‚": {
        "name": "Ğ•Ğ³ĞµÑ€Ğ¼ĞµĞ¹Ñ�Ñ‚ĞµÑ€ ÑˆĞ¾Ñ‚",
        "name_en": ["JÃ¤germeister Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 180, "protein": 0.1, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "ĞµĞ³ĞµÑ€Ğ¼ĞµĞ¹Ñ�Ñ‚ĞµÑ€", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["jagermeister", "ĞµĞ³ĞµÑ€Ğ¼ĞµĞ¹Ñ�Ñ‚ĞµÑ€", "ÑˆĞ¾Ñ‚", "Ñ‚Ñ€Ğ°Ğ²Ñ�Ğ½Ğ¾Ğ¹ Ğ»Ğ¸ĞºĞµÑ€"]
    },
    "Ñ�Ğ°Ğ¼Ğ±ÑƒĞºĞ° ĞºĞ¾Ğ½ Ğ¼Ğ¾Ñ�Ñ�ĞºĞ°": {
        "name": "Ğ¡Ğ°Ğ¼Ğ±ÑƒĞºĞ° Ñ� Ğ¼ÑƒÑ…Ğ°Ğ¼Ğ¸",
        "name_en": ["Sambuca con Mosca", "Sambuca with Flies"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 200, "protein": 0.1, "fat": 0.1, "carbs": 15.0},
        "ingredients": [
            {"name": "Ñ�Ğ°Ğ¼Ğ±ÑƒĞºĞ°", "type": "alcohol", "percent": 80},
            {"name": "ĞºĞ¾Ñ„ĞµĞ¹Ğ½Ñ‹Ğµ Ğ·ĞµÑ€Ğ½Ğ°", "type": "other", "percent": 20}
        ],
        "keywords": ["sambuca", "Ñ�Ğ°Ğ¼Ğ±ÑƒĞºĞ°", "con mosca", "ĞºĞ¾Ñ„ĞµĞ¹Ğ½Ñ‹Ğµ Ğ·ĞµÑ€Ğ½Ğ°"]
    },
    "Ğ°Ğ±Ñ�ĞµĞ½Ñ‚ ÑˆĞ¾Ñ‚": {
        "name": "Ğ�Ğ±Ñ�ĞµĞ½Ñ‚",
        "name_en": ["Absinthe Shot"],
        "category": "shot",
        "default_weight": 40,
        "nutrition_per_100": {"calories": 210, "protein": 0.1, "fat": 0.1, "carbs": 9.0},
        "ingredients": [
            {"name": "Ğ°Ğ±Ñ�ĞµĞ½Ñ‚", "type": "alcohol", "percent": 80},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€", "type": "sugar", "percent": 10},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 10}
        ],
        "keywords": ["absinthe", "Ğ°Ğ±Ñ�ĞµĞ½Ñ‚", "Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹ ÑˆĞ¾Ñ‚", "Ğ¿Ğ¾Ğ»Ñ‹Ğ½Ğ½Ñ‹Ğ¹"]
    },
    "Ğ·ĞµĞ»ĞµĞ½Ğ°Ñ� Ñ„ĞµÑ�": {
        "name": "Ğ—ĞµĞ»ĞµĞ½Ğ°Ñ� Ñ„ĞµÑ�",
        "name_en": ["Green Fairy"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 200, "protein": 0.1, "fat": 0.1, "carbs": 10.0},
        "ingredients": [
            {"name": "Ğ°Ğ±Ñ�ĞµĞ½Ñ‚", "type": "alcohol", "percent": 50},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 20},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 30}
        ],
        "keywords": ["Ğ·ĞµĞ»ĞµĞ½Ğ°Ñ� Ñ„ĞµÑ�", "Ğ°Ğ±Ñ�ĞµĞ½Ñ‚", "green fairy"]
    },
    "ÑƒÑ‚Ñ€ĞµĞ½Ğ½Ñ�Ñ� Ñ€Ğ¾Ñ�Ğ°": {
        "name": "Ğ£Ñ‚Ñ€ĞµĞ½Ğ½Ñ�Ñ� Ñ€Ğ¾Ñ�Ğ°",
        "name_en": ["Morning Dew"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 40},
            {"name": "Ğ»Ğ¸ĞºĞµÑ€ Ğ´Ñ‹Ğ½Ğ½Ñ‹Ğ¹", "type": "alcohol", "percent": 30},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 30}
        ],
        "keywords": ["ÑƒÑ‚Ñ€ĞµĞ½Ğ½Ñ�Ñ� Ñ€Ğ¾Ñ�Ğ°", "Ğ´Ñ‹Ğ½Ğ½Ñ‹Ğ¹ ÑˆĞ¾Ñ‚", "midori"]
    },
    "Ñ� Ğ½ÑƒÑ‚ĞµĞ»Ğ»Ğ¾Ğ¹": {
        "name": "Ğ¨Ğ¾Ñ‚ Ñ� Ğ½ÑƒÑ‚ĞµĞ»Ğ»Ğ¾Ğ¹",
        "name_en": ["Nutella Shot"],
        "category": "shot",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 250, "protein": 2.0, "fat": 10.0, "carbs": 25.0},
        "ingredients": [
            {"name": "Ñ„Ñ€Ğ°Ğ½Ğ¶ĞµĞ»Ğ¸ĞºĞ¾", "type": "alcohol", "percent": 40},
            {"name": "Ğ±Ğ°Ğ¹Ğ»Ğ¸Ñ�", "type": "alcohol", "percent": 30},
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 30}
        ],
        "keywords": ["nutella shot", "Ğ½ÑƒÑ‚ĞµĞ»Ğ»Ğ°", "Ğ´ĞµÑ�ĞµÑ€Ñ‚Ğ½Ñ‹Ğ¹ ÑˆĞ¾Ñ‚"]
    },
    "Ğ¶Ğ¸Ğ´ĞºĞ¸Ğ¹ ĞºĞµĞºÑ�": {
        "name": "Ğ–Ğ¸Ğ´ĞºĞ¸Ğ¹ ĞºĞµĞºÑ�",
        "name_en": ["Liquid Cupcake"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 230, "protein": 1.0, "fat": 6.0, "carbs": 22.0},
        "ingredients": [
            {"name": "Ğ²Ğ°Ğ½Ğ¸Ğ»ÑŒĞ½Ğ°Ñ� Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 40},
            {"name": "Ğ»Ğ¸ĞºĞµÑ€ ĞºĞ°ĞºĞ°Ğ¾", "type": "alcohol", "percent": 30},
            {"name": "Ğ±Ğ°Ğ¹Ğ»Ğ¸Ñ�", "type": "alcohol", "percent": 30}
        ],
        "keywords": ["liquid cupcake", "Ğ¶Ğ¸Ğ´ĞºĞ¸Ğ¹ ĞºĞµĞºÑ�", "Ğ´ĞµÑ�ĞµÑ€Ñ‚Ğ½Ñ‹Ğ¹"]
    },
    
    # ==================== Ğ”Ğ˜Ğ–Ğ•Ğ¡Ğ¢Ğ˜Ğ’Ğ« Ğ˜ Ğ�ĞŸĞ•Ğ Ğ˜Ğ¢Ğ˜Ğ’Ğ« ====================
    "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ñ‡ĞµĞ»Ğ»Ğ¾": {
        "name": "Ğ›Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ñ‡ĞµĞ»Ğ»Ğ¾",
        "name_en": ["Limoncello"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 200, "protein": 0.1, "fat": 0.1, "carbs": 25.0},
        "ingredients": [
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ñ‡ĞµĞ»Ğ»Ğ¾", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["limoncello", "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ñ‡ĞµĞ»Ğ»Ğ¾", "Ğ¸Ñ‚Ğ°Ğ»ÑŒÑ�Ğ½Ñ�ĞºĞ¸Ğ¹ Ğ»Ğ¸ĞºĞµÑ€"]
    },
    "Ñ„Ñ€Ğ°Ğ½Ğ¶ĞµĞ»Ğ¸ĞºĞ¾": {
        "name": "Ğ¤Ñ€Ğ°Ğ½Ğ¶ĞµĞ»Ğ¸ĞºĞ¾",
        "name_en": ["Frangelico"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 190, "protein": 0.5, "fat": 0.2, "carbs": 18.0},
        "ingredients": [
            {"name": "Ñ„Ñ€Ğ°Ğ½Ğ¶ĞµĞ»Ğ¸ĞºĞ¾", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["frangelico", "Ñ„Ñ€Ğ°Ğ½Ğ¶ĞµĞ»Ğ¸ĞºĞ¾", "Ğ¾Ñ€ĞµÑ…Ğ¾Ğ²Ñ‹Ğ¹ Ğ»Ğ¸ĞºĞµÑ€"]
    },
    "Ğ°Ğ¼Ğ±Ñ€ĞµÑ‚Ñ‚Ğ¾": {
        "name": "Ğ�Ğ¼Ğ±Ñ€ĞµÑ‚Ñ‚Ğ¾",
        "name_en": ["Amaretto"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 22.0},
        "ingredients": [
            {"name": "Ğ°Ğ¼Ğ±Ñ€ĞµÑ‚Ñ‚Ğ¾", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["amaretto", "Ğ°Ğ¼Ğ±Ñ€ĞµÑ‚Ñ‚Ğ¾", "Ğ¼Ğ¸Ğ½Ğ´Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ»Ğ¸ĞºĞµÑ€"]
    },
    "Ğ´Ğ¶Ğ¸Ğ½ ÑˆĞ¾Ñ‚": {
        "name": "Ğ”Ğ¶Ğ¸Ğ½",
        "name_en": ["Gin Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 160, "protein": 0.1, "fat": 0.1, "carbs": 0.5},
        "ingredients": [
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["gin", "Ğ´Ğ¶Ğ¸Ğ½", "ÑˆĞ¾Ñ‚"]
    },
    "Ğ²Ğ¾Ğ´ĞºĞ° ÑˆĞ¾Ñ‚": {
        "name": "Ğ’Ğ¾Ğ´ĞºĞ°",
        "name_en": ["Vodka Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 150, "protein": 0.1, "fat": 0.1, "carbs": 0.1},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["vodka", "Ğ²Ğ¾Ğ´ĞºĞ°", "Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğ¹ ÑˆĞ¾Ñ‚"]
    },
    "Ñ‚ĞµĞºĞ¸Ğ»Ğ° ÑˆĞ¾Ñ‚": {
        "name": "Ğ¢ĞµĞºĞ¸Ğ»Ğ°",
        "name_en": ["Tequila Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 160, "protein": 0.1, "fat": 0.1, "carbs": 0.5},
        "ingredients": [
            {"name": "Ñ‚ĞµĞºĞ¸Ğ»Ğ°", "type": "alcohol", "percent": 80},
            {"name": "Ñ�Ğ¾Ğ»ÑŒ", "type": "spice", "percent": 10},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 10}
        ],
        "keywords": ["tequila", "Ñ‚ĞµĞºĞ¸Ğ»Ğ°", "Ñ�Ğ¾Ğ»ÑŒ", "Ğ»Ğ°Ğ¹Ğ¼"]
    },
    "Ğ²Ğ¸Ñ�ĞºĞ¸ ÑˆĞ¾Ñ‚": {
        "name": "Ğ’Ğ¸Ñ�ĞºĞ¸",
        "name_en": ["Whiskey Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 0.1},
        "ingredients": [
            {"name": "Ğ²Ğ¸Ñ�ĞºĞ¸", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["whiskey", "Ğ²Ğ¸Ñ�ĞºĞ¸", "Ğ±ÑƒÑ€Ğ±Ğ¾Ğ½", "Ñ�ĞºĞ¾Ñ‚Ñ‡"]
    },
    "ĞºĞ¾Ğ½ÑŒÑ�Ğº ÑˆĞ¾Ñ‚": {
        "name": "ĞšĞ¾Ğ½ÑŒÑ�Ğº",
        "name_en": ["Cognac Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 0.1},
        "ingredients": [
            {"name": "ĞºĞ¾Ğ½ÑŒÑ�Ğº", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["cognac", "ĞºĞ¾Ğ½ÑŒÑ�Ğº"]
    },
    "Ñ€Ğ¾Ğ¼ ÑˆĞ¾Ñ‚": {
        "name": "Ğ Ğ¾Ğ¼",
        "name_en": ["Rum Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 160, "protein": 0.1, "fat": 0.1, "carbs": 0.5},
        "ingredients": [
            {"name": "Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["rum", "Ñ€Ğ¾Ğ¼"]
    },
    
    # ==================== ĞšĞ�ĞšĞ¢Ğ•Ğ™Ğ›Ğ¬Ğ�Ğ�Ğ¯ ĞšĞ›Ğ�Ğ¡Ğ¡Ğ˜ĞšĞ� IBA ====================
    "Ğ¼Ğ°Ñ€Ñ‚Ğ¸Ğ½ĞµĞ·": {
        "name": "ĞœĞ°Ñ€Ñ‚Ğ¸Ğ½ĞµĞ·",
        "name_en": ["Martinez"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 0.1, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 40},
            {"name": "ĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ€Ğ¼ÑƒÑ‚", "type": "alcohol", "percent": 25},
            {"name": "Ğ»Ğ¸ĞºĞµÑ€ Ğ¼Ğ°Ñ€Ğ°Ñ�ĞºĞ¸Ğ½", "type": "alcohol", "percent": 10},
            {"name": "Ğ±Ğ¸Ñ‚Ñ‚ĞµÑ€ Ğ°Ğ½Ğ³Ğ¾Ñ�Ñ‚ÑƒÑ€Ğ°", "type": "alcohol", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 20}
        ],
        "keywords": ["martinez", "Ğ¼Ğ°Ñ€Ñ‚Ğ¸Ğ½ĞµĞ·", "Ğ¿Ñ€ĞµĞ´ÑˆĞµÑ�Ñ‚Ğ²ĞµĞ½Ğ½Ğ¸Ğº Ğ¼Ğ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸"]
    },
    "Ğ°Ğ²Ğ¸Ğ°Ñ†Ğ¸Ñ�": {
        "name": "Ğ�Ğ²Ğ¸Ğ°Ñ†Ğ¸Ñ�",
        "name_en": ["Aviation"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 40},
            {"name": "Ğ»Ğ¸ĞºĞµÑ€ Ğ¼Ğ°Ñ€Ğ°Ñ�ĞºĞ¸Ğ½", "type": "alcohol", "percent": 10},
            {"name": "Ñ„Ğ¸Ğ°Ğ»ĞºĞ¾Ğ²Ñ‹Ğ¹ Ğ»Ğ¸ĞºĞµÑ€", "type": "alcohol", "percent": 10},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 10},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["aviation", "Ğ°Ğ²Ğ¸Ğ°Ñ†Ğ¸Ñ�", "Ñ„Ğ¸Ğ°Ğ»ĞºĞ¾Ğ²Ñ‹Ğ¹ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ğ±Ğ¸Ğ¶Ñƒ": {
        "name": "Ğ‘Ğ¸Ğ¶Ñƒ",
        "name_en": ["Bijou"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 7.0},
        "ingredients": [
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 35},
            {"name": "ĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ€Ğ¼ÑƒÑ‚", "type": "alcohol", "percent": 25},
            {"name": "Ğ·ĞµĞ»ĞµĞ½Ñ‹Ğ¹ ÑˆĞ°Ñ€Ñ‚Ñ€ĞµĞ·", "type": "alcohol", "percent": 15},
            {"name": "Ğ±Ğ¸Ñ‚Ñ‚ĞµÑ€", "type": "alcohol", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 20}
        ],
        "keywords": ["bijou", "Ğ±Ğ¸Ğ¶Ñƒ", "Ğ´Ñ€Ğ°Ğ³Ğ¾Ñ†ĞµĞ½Ğ½Ñ‹Ğ¹ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ğ°Ğ»ĞµĞºÑ�Ğ°Ğ½Ğ´Ñ€": {
        "name": "Ğ�Ğ»ĞµĞºÑ�Ğ°Ğ½Ğ´Ñ€",
        "name_en": ["Alexander"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 200, "protein": 1.5, "fat": 5.0, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 20},
            {"name": "Ğ»Ğ¸ĞºĞµÑ€ ĞºĞ°ĞºĞ°Ğ¾", "type": "alcohol", "percent": 20},
            {"name": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "dairy", "percent": 20},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 40}
        ],
        "keywords": ["alexander", "Ğ°Ğ»ĞµĞºÑ�Ğ°Ğ½Ğ´Ñ€", "ĞºÑ€ĞµĞ¼Ğ¾Ğ²Ñ‹Ğ¹ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ğ±Ğ¾Ğ±Ğ±Ğ¸ Ğ±ĞµÑ€Ğ½Ñ�": {
        "name": "Ğ‘Ğ¾Ğ±Ğ±Ğ¸ Ğ‘ĞµÑ€Ğ½Ñ�",
        "name_en": ["Bobby Burns"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "ÑˆĞ¾Ñ‚Ğ»Ğ°Ğ½Ğ´Ñ�ĞºĞ¸Ğ¹ Ğ²Ğ¸Ñ�ĞºĞ¸", "type": "alcohol", "percent": 45},
            {"name": "ĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ€Ğ¼ÑƒÑ‚", "type": "alcohol", "percent": 20},
            {"name": "Ğ±ĞµĞ½ĞµĞ´Ğ¸ĞºÑ‚Ğ¸Ğ½", "type": "alcohol", "percent": 15},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 20}
        ],
        "keywords": ["bobby burns", "Ğ±Ğ¾Ğ±Ğ±Ğ¸ Ğ±ĞµÑ€Ğ½Ñ�", "Ğ²Ğ¸Ñ�ĞºĞ¸ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ñ„Ğ¸Ñˆ Ñ…Ğ°ÑƒÑ� Ğ¿Ğ°Ğ½Ñ‡": {
        "name": "Ğ¤Ğ¸Ñˆ Ğ¥Ğ°ÑƒÑ� ĞŸĞ°Ğ½Ñ‡",
        "name_en": ["Fish House Punch"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 0.2, "fat": 0.1, "carbs": 10.0},
        "ingredients": [
            {"name": "Ñ‚ĞµĞ¼Ğ½Ñ‹Ğ¹ Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 15},
            {"name": "ĞºĞ¾Ğ½ÑŒÑ�Ğº", "type": "alcohol", "percent": 5},
            {"name": "Ğ¿ĞµÑ€Ñ�Ğ¸ĞºĞ¾Ğ²Ñ‹Ğ¹ Ğ»Ğ¸ĞºĞµÑ€", "type": "alcohol", "percent": 5},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 5},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 3},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 5},
            {"name": "Ğ²Ğ¾Ğ´Ğ°", "type": "liquid", "percent": 22},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 40}
        ],
        "keywords": ["fish house punch", "Ñ„Ğ¸Ñˆ Ñ…Ğ°ÑƒÑ�", "Ğ¿ÑƒĞ½Ñˆ", "Ñ�Ñ‚Ğ°Ñ€Ğ¸Ğ½Ğ½Ñ‹Ğ¹ Ñ€ĞµÑ†ĞµĞ¿Ñ‚"]
    },
    "Ğ²ĞµÑ€Ğ¼ÑƒÑ‚ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ": {
        "name": "Ğ’ĞµÑ€Ğ¼ÑƒÑ‚ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ",
        "name_en": ["Vermouth Cocktail"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ²ĞµÑ€Ğ¼ÑƒÑ‚", "type": "alcohol", "percent": 60},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ±Ğ¸Ñ‚Ñ‚ĞµÑ€", "type": "alcohol", "percent": 10},
            {"name": "Ğ»Ğ¸ĞºĞµÑ€ Ğ¼Ğ°Ñ€Ğ°Ñ�ĞºĞ¸Ğ½", "type": "alcohol", "percent": 10},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 20}
        ],
        "keywords": ["vermouth cocktail", "Ğ²ĞµÑ€Ğ¼ÑƒÑ‚ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ", "ĞºĞ»Ğ°Ñ�Ñ�Ğ¸ĞºĞ°"]
    },
    "Ğ´Ñ€Ğ°Ğ¹ Ğ¼Ğ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸": {
        "name": "Ğ”Ñ€Ğ°Ğ¹ ĞœĞ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸",
        "name_en": ["Dry Martini"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 1.0},
        "ingredients": [
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 60},
            {"name": "Ñ�ÑƒÑ…Ğ¾Ğ¹ Ğ²ĞµÑ€Ğ¼ÑƒÑ‚", "type": "alcohol", "percent": 15},
            {"name": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¸", "type": "vegetable", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 20}
        ],
        "keywords": ["dry martini", "Ğ¼Ğ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸", "Ğ´Ğ¶Ğ¸Ğ½", "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¸", "Ğ±Ğ¾Ğ½Ğ´"]
    },
    "Ğ½ĞµĞ³Ñ€Ğ¾Ğ½Ğ¸": {
        "name": "Ğ�ĞµĞ³Ñ€Ğ¾Ğ½Ğ¸",
        "name_en": ["Negroni"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ´Ğ¶Ğ¸Ğ½", "type": "alcohol", "percent": 25},
            {"name": "ĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ€Ğ¼ÑƒÑ‚", "type": "alcohol", "percent": 25},
            {"name": "ĞºĞ°Ğ¼Ğ¿Ğ°Ñ€Ğ¸", "type": "alcohol", "percent": 25},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½", "type": "fruit", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 20}
        ],
        "keywords": ["negroni", "Ğ½ĞµĞ³Ñ€Ğ¾Ğ½Ğ¸", "Ğ¸Ñ‚Ğ°Ğ»ÑŒÑ�Ğ½Ñ�ĞºĞ¸Ğ¹ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ", "Ğ³Ğ¾Ñ€ÑŒĞºĞ¸Ğ¹"]
    },
    "Ğ¼Ğ°Ğ½Ñ…Ñ�Ñ‚Ñ‚ĞµĞ½": {
        "name": "ĞœĞ°Ğ½Ñ…Ñ�Ñ‚Ñ‚ĞµĞ½",
        "name_en": ["Manhattan"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 4.0},
        "ingredients": [
            {"name": "Ğ²Ğ¸Ñ�ĞºĞ¸ Ñ€Ğ¶Ğ°Ğ½Ğ¾Ğ¹", "type": "alcohol", "percent": 50},
            {"name": "ĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ€Ğ¼ÑƒÑ‚", "type": "alcohol", "percent": 25},
            {"name": "Ğ±Ğ¸Ñ‚Ñ‚ĞµÑ€ Ğ°Ğ½Ğ³Ğ¾Ñ�Ñ‚ÑƒÑ€Ğ°", "type": "alcohol", "percent": 5},
            {"name": "Ğ²Ğ¸ÑˆĞ½Ñ�", "type": "fruit", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 15}
        ],
        "keywords": ["manhattan", "Ğ¼Ğ°Ğ½Ñ…Ñ�Ñ‚Ñ‚ĞµĞ½", "Ğ²Ğ¸Ñ�ĞºĞ¸ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ğ´Ğ°Ğ¹ĞºĞ¸Ñ€Ğ¸": {
        "name": "Ğ”Ğ°Ğ¹ĞºĞ¸Ñ€Ğ¸",
        "name_en": ["Daiquiri"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 160, "protein": 0.1, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "Ğ±ĞµĞ»Ñ‹Ğ¹ Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 40},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 15},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 10},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 35}
        ],
        "keywords": ["daiquiri", "Ğ´Ğ°Ğ¹ĞºĞ¸Ñ€Ğ¸", "Ñ€Ğ¾Ğ¼", "Ğ»Ğ°Ğ¹Ğ¼"]
    },
    "Ğ¼Ğ¾Ñ…Ğ¸Ñ‚Ğ¾": {
        "name": "ĞœĞ¾Ñ…Ğ¸Ñ‚Ğ¾",
        "name_en": ["Mojito"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 0.2, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ñ�Ğ²ĞµÑ‚Ğ»Ñ‹Ğ¹ Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 15},
            {"name": "Ğ¼Ñ�Ñ‚Ğ°", "type": "vegetable", "percent": 2},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 5},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 8},
            {"name": "Ñ�Ğ¾Ğ´Ğ¾Ğ²Ğ°Ñ�", "type": "liquid", "percent": 40},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["Ğ¼Ğ¾Ñ…Ğ¸Ñ‚Ğ¾", "mojito", "Ñ€Ğ¾Ğ¼", "Ğ¼Ñ�Ñ‚Ğ°", "Ğ»Ğ°Ğ¹Ğ¼", "ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°": {
        "name": "ĞœĞ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°",
        "name_en": ["Margarita"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 70, "protein": 0.2, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "Ñ‚ĞµĞºĞ¸Ğ»Ğ°", "type": "alcohol", "percent": 20},
            {"name": "Ñ‚Ñ€Ğ¸Ğ¿Ğ» Ñ�ĞµĞº", "type": "alcohol", "percent": 10},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 8},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 62}
        ],
        "keywords": ["margarita", "Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°", "Ñ‚ĞµĞºĞ¸Ğ»Ğ°", "Ñ‚Ñ€Ğ¸Ğ¿Ğ» Ñ�ĞµĞº"]
    },
    "Ğ¿Ğ¸Ñ�ĞºĞ¾ Ñ�Ğ°ÑƒÑ�Ñ€": {
        "name": "ĞŸĞ¸Ñ�ĞºĞ¾ Ğ¡Ğ°ÑƒÑ�Ñ€",
        "name_en": ["Pisco Sour"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 1.0, "fat": 0.5, "carbs": 7.0},
        "ingredients": [
            {"name": "Ğ¿Ğ¸Ñ�ĞºĞ¾", "type": "alcohol", "percent": 40},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ½Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 15},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 10},
            {"name": "Ñ�Ğ¸Ñ‡Ğ½Ñ‹Ğ¹ Ğ±ĞµĞ»Ğ¾Ğº", "type": "protein", "percent": 5},
            {"name": "Ğ±Ğ¸Ñ‚Ñ‚ĞµÑ€", "type": "alcohol", "percent": 2},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 28}
        ],
        "keywords": ["pisco sour", "Ğ¿Ğ¸Ñ�ĞºĞ¾ Ñ�Ğ°ÑƒÑ�Ñ€", "Ğ¿ĞµÑ€ÑƒĞ°Ğ½Ñ�ĞºĞ¸Ğ¹ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    
    # ==================== ĞŸĞ�ĞŸĞ£Ğ›Ğ¯Ğ Ğ�Ğ«Ğ• ĞšĞ�ĞšĞ¢Ğ•Ğ™Ğ›Ğ˜ 2026 ====================
    "Ñ�Ñ�Ğ¿Ñ€ĞµÑ�Ñ�Ğ¾ Ğ¼Ğ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸": {
        "name": "Ğ­Ñ�Ğ¿Ñ€ĞµÑ�Ñ�Ğ¾ ĞœĞ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸",
        "name_en": ["Espresso Martini"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 150, "protein": 0.5, "fat": 0.2, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 30},
            {"name": "ĞºĞ¾Ñ„ĞµĞ¹Ğ½Ñ‹Ğ¹ Ğ»Ğ¸ĞºĞµÑ€", "type": "alcohol", "percent": 20},
            {"name": "Ñ�Ñ�Ğ¿Ñ€ĞµÑ�Ñ�Ğ¾", "type": "other", "percent": 20},
            {"name": "Ñ�Ğ°Ñ…Ğ°Ñ€Ğ½Ñ‹Ğ¹ Ñ�Ğ¸Ñ€Ğ¾Ğ¿", "type": "sugar", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 25}
        ],
        "keywords": ["espresso martini", "ĞºĞ¾Ñ„ĞµĞ¹Ğ½Ñ‹Ğ¹ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ", "Ñ‚Ñ€ĞµĞ½Ğ´ 2026"]
    },
    "Ñ�Ğ¿Ñ€Ğ¸Ñ‚Ñ†": {
        "name": "Ğ¡Ğ¿Ñ€Ğ¸Ñ‚Ñ†",
        "name_en": ["Spritz"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 55, "protein": 0.1, "fat": 0.1, "carbs": 4.0},
        "ingredients": [
            {"name": "Ğ¿Ñ€Ğ¾Ñ�ĞµĞºĞºĞ¾", "type": "alcohol", "percent": 35},
            {"name": "Ğ°Ğ¿ĞµÑ€Ğ¾Ğ»ÑŒ", "type": "alcohol", "percent": 15},
            {"name": "Ñ�Ğ¾Ğ´Ğ¾Ğ²Ğ°Ñ�", "type": "liquid", "percent": 15},
            {"name": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½", "type": "fruit", "percent": 5},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["spritz", "Ñ�Ğ¿Ñ€Ğ¸Ñ‚Ñ†", "Ğ°Ğ¿ĞµÑ€Ğ¾Ğ»ÑŒ", "Ğ¿Ğ¾Ğ¿ÑƒĞ»Ñ�Ñ€Ğ½Ñ‹Ğ¹ 2026"]
    },
    "Ğ²Ğ¾Ğ´ĞºĞ° Ğ»ĞµĞ¼Ğ¾Ğ½Ğ°Ğ´": {
        "name": "Ğ’Ğ¾Ğ´ĞºĞ° Ğ›ĞµĞ¼Ğ¾Ğ½Ğ°Ğ´",
        "name_en": ["Vodka Lemonade"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 15},
            {"name": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´", "type": "liquid", "percent": 55},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["vodka lemonade", "Ğ²Ğ¾Ğ´ĞºĞ° Ñ� Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´Ğ¾Ğ¼", "Ğ»ĞµĞ³ĞºĞ¸Ğ¹ ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ"]
    },
    "Ğ²Ğ¾Ğ´ĞºĞ° Ñ�Ğ¾Ğ´Ğ°": {
        "name": "Ğ’Ğ¾Ğ´ĞºĞ° Ğ¡Ğ¾Ğ´Ğ°",
        "name_en": ["Vodka Soda"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 35, "protein": 0.1, "fat": 0.1, "carbs": 1.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 15},
            {"name": "Ñ�Ğ¾Ğ´Ğ¾Ğ²Ğ°Ñ�", "type": "liquid", "percent": 55},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 3},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 27}
        ],
        "keywords": ["vodka soda", "Ğ²Ğ¾Ğ´ĞºĞ° Ñ� Ñ�Ğ¾Ğ´Ğ¾Ğ²Ğ¾Ğ¹", "Ğ½Ğ¸Ğ·ĞºĞ¾ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹Ğ½Ñ‹Ğ¹"]
    },
    "Ğ²Ğ¸Ñ�ĞºĞ¸ Ñ�Ğ½Ğ´ ĞºĞ¾Ğ»Ğ°": {
        "name": "Ğ’Ğ¸Ñ�ĞºĞ¸ Ñ� ĞºĞ¾Ğ»Ğ¾Ğ¹",
        "name_en": ["Whisky and Coke"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 55, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ğ²Ğ¸Ñ�ĞºĞ¸", "type": "alcohol", "percent": 15},
            {"name": "ĞºĞ¾Ğ»Ğ°", "type": "liquid", "percent": 55},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["whisky coke", "Ğ²Ğ¸Ñ�ĞºĞ¸ Ñ� ĞºĞ¾Ğ»Ğ¾Ğ¹", "ĞºĞ»Ğ°Ñ�Ñ�Ğ¸ĞºĞ°"]
    },
    "Ñ€Ğ¾Ğ¼ Ñ�Ğ½Ğ´ ĞºĞ¾Ğ»Ğ°": {
        "name": "Ğ Ğ¾Ğ¼ Ñ� ĞºĞ¾Ğ»Ğ¾Ğ¹",
        "name_en": ["Rum and Coke"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 50, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "Ñ€Ğ¾Ğ¼", "type": "alcohol", "percent": 15},
            {"name": "ĞºĞ¾Ğ»Ğ°", "type": "liquid", "percent": 55},
            {"name": "Ğ»Ğ°Ğ¹Ğ¼", "type": "fruit", "percent": 3},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 27}
        ],
        "keywords": ["rum and coke", "Ñ€Ğ¾Ğ¼ Ñ� ĞºĞ¾Ğ»Ğ¾Ğ¹", "ĞºÑƒĞ±Ğ° Ğ»Ğ¸Ğ±Ñ€Ğµ"]
    },
    "Ñ„Ñ€ĞµĞ½Ñ‡ Ğ¼Ğ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸": {
        "name": "Ğ¤Ñ€ĞµĞ½Ñ‡ ĞœĞ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸",
        "name_en": ["French Martini"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 0.1, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "Ğ²Ğ¾Ğ´ĞºĞ°", "type": "alcohol", "percent": 30},
            {"name": "Ğ¼Ğ°Ğ»Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ»Ğ¸ĞºĞµÑ€", "type": "alcohol", "percent": 15},
            {"name": "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ğº", "type": "fruit", "percent": 25},
            {"name": "Ğ»ĞµĞ´", "type": "other", "percent": 30}
        ],
        "keywords": ["french martini", "Ñ„Ñ€Ğ°Ğ½Ñ†ÑƒĞ·Ñ�ĞºĞ¸Ğ¹ Ğ¼Ğ°Ñ€Ñ‚Ğ¸Ğ½Ğ¸", "Ğ¼Ğ°Ğ»Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹"]
    }
}

# =============================================================================
# ğŸ”� Ğ¤Ğ£Ğ�ĞšĞ¦Ğ˜Ğ˜ ĞŸĞ�Ğ˜Ğ¡ĞšĞ�
# =============================================================================

def _similarity(a: str, b: str) -> float:
    """Ğ’Ñ‹Ñ‡Ğ¸Ñ�Ğ»Ñ�ĞµÑ‚ Ñ�Ñ…Ğ¾Ğ¶ĞµÑ�Ñ‚ÑŒ Ñ�Ñ‚Ñ€Ğ¾Ğº (0.0â€“1.0)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_ai_dish_name(dish_name: str) -> str:
    """
    Ğ�Ğ¾Ñ€Ğ¼Ğ°Ğ»Ğ¸Ğ·ÑƒĞµÑ‚ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ±Ğ»Ñ�Ğ´Ğ° Ğ¾Ñ‚ Ğ˜Ğ˜ Ğ´Ğ»Ñ� Ğ¿Ğ¾Ğ¸Ñ�ĞºĞ° Ğ² Ğ±Ğ°Ğ·Ğµ.
    """
    if not dish_name:
        return ""
    
    dish_lower = dish_name.lower().strip()
    
    # ĞŸÑ€Ñ�Ğ¼Ğ¾Ğ¹ Ğ¿Ğ¾Ğ¸Ñ�Ğº Ğ¿Ğ¾ ĞºĞ»Ñ�Ñ‡Ğ°Ğ¼
    if dish_lower in COMPOSITE_DISHES:
        return dish_lower
    
    # ĞŸĞ¾Ğ¸Ñ�Ğº Ğ¿Ğ¾ Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¼ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ�Ğ¼
    for key, dish_data in COMPOSITE_DISHES.items():
        name_en_list = dish_data.get("name_en", [])
        for name_en in name_en_list:
            if name_en.lower() == dish_lower or dish_lower in name_en.lower():
                logger.info(f"ğŸ”� Ğ�Ğ°Ğ¹Ğ´ĞµĞ½Ğ¾ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğµ Ğ¿Ğ¾ EN: '{dish_name}' â†’ '{key}'")
                return key
    
    # ĞŸĞ¾Ğ¸Ñ�Ğº Ğ¿Ğ¾ ĞºĞ»Ñ�Ñ‡ĞµĞ²Ñ‹Ğ¼ Ñ�Ğ»Ğ¾Ğ²Ğ°Ğ¼
    for key, dish_data in COMPOSITE_DISHES.items():
        keywords = dish_data.get("keywords", [])
        for keyword in keywords:
            if keyword in dish_lower:
                logger.info(f"ğŸ”� Ğ�Ğ°Ğ¹Ğ´ĞµĞ½Ğ¾ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğµ Ğ¿Ğ¾ keyword: '{dish_name}' â†’ '{key}'")
                return key
    
    # Fuzzy-Ğ¿Ğ¾Ğ¸Ñ�Ğº Ğ¿Ğ¾ Ñ€ÑƒÑ�Ñ�ĞºĞ¾Ğ¼Ñƒ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ�
    best_match = None
    best_score = 0.5
    for key, dish_data in COMPOSITE_DISHES.items():
        name_ru = dish_data.get("name", "").lower()
        score = _similarity(dish_lower, name_ru)
        if score > best_score:
            best_score = score
            best_match = key
    
    if best_match:
        logger.info(f"ğŸ”� Fuzzy-Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğµ: '{dish_name}' â†’ '{best_match}' (score: {best_score:.2f})")
        return best_match
    
    return ""

def find_matching_dishes(
    dish_name: str,
    ai_ingredients: list = None,
    threshold: float = 0.3
) -> list:
    """
    Ğ£Ğ»ÑƒÑ‡ÑˆĞµĞ½Ğ½Ñ‹Ğ¹ Ğ¿Ğ¾Ğ¸Ñ�Ğº Ğ³Ğ¾Ñ‚Ğ¾Ğ²Ñ‹Ñ… Ğ±Ğ»Ñ�Ğ´ Ğ² COMPOSITE_DISHES.
    âœ… Ğ£Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ�
    âœ… Ğ£Ğ»ÑƒÑ‡ÑˆĞµĞ½Ğ½Ñ‹Ğ¹ scoring
    """
    if not dish_name and not ai_ingredients:
        return []
    
    dish_name_lower = dish_name.lower().strip() if dish_name else ""
    
    logger.info(f"ğŸ”� ĞŸĞ¾Ğ¸Ñ�Ğº Ğ±Ğ»Ñ�Ğ´ Ğ´Ğ»Ñ� '{dish_name}'")
    
    matches = []
    
    for key, dish_data in COMPOSITE_DISHES.items():
        dish_display_name = dish_data.get('name', key)
        
        # Score Ğ¿Ğ¾ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ�
        name_score = 0.0
        if dish_name_lower:
            if dish_name_lower == key:
                name_score = 1.0
            elif dish_name_lower == dish_display_name.lower():
                name_score = 1.0
            elif any(dish_name_lower == en.lower() or dish_name_lower in en.lower() 
                    for en in dish_data.get('name_en', [])):
                name_score = 0.9
            elif any(kw in dish_name_lower for kw in dish_data.get('keywords', [])):
                name_score = 0.7
            elif (dish_name_lower in key or key in dish_name_lower or
                  dish_name_lower in dish_display_name.lower()):
                name_score = 0.5
            else:
                name_score = _similarity(dish_name_lower, key) * 0.5
        
        if name_score >= threshold:
            matches.append({
                'name': dish_display_name,
                'score': round(name_score, 2),
                'dish_key': key.strip(),
                'nutrition_per_100': dish_data.get('nutrition_per_100', {}),
                'default_weight': dish_data.get('default_weight', 300)
            })
            logger.info(f"âœ… Ğ�Ğ°Ğ¹Ğ´ĞµĞ½Ğ¾: {dish_display_name} (score: {name_score:.2f}, key: '{key}')")
    
    # Ğ¡Ğ¾Ñ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¿Ğ¾ score
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:5]

def get_dish_ingredients(dish_name: str, total_weight: int = 300) -> list:
    """Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ Ğ±Ğ»Ñ�Ğ´Ğ° Ñ� Ñ€Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ğ°Ğ½Ğ½Ñ‹Ğ¼Ğ¸ Ğ²ĞµÑ�Ğ°Ğ¼Ğ¸."""
    dish_name_lower = dish_name.lower().strip()
    
    # Ğ˜Ñ‰ĞµĞ¼ Ğ±Ğ»Ñ�Ğ´Ğ¾
    dish_data = COMPOSITE_DISHES.get(dish_name_lower)
    if not dish_data:
        for key, value in COMPOSITE_DISHES.items():
            if key in dish_name_lower or dish_name_lower in key:
                dish_data = value
                break
    
    if not dish_data:
        return []
    
    ingredients = dish_data.get('ingredients', [])
    if not ingredients:
        return []
    
    # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ²ĞµÑ�Ğ°
    result = []
    for ing in ingredients:
        name = ing.get('name', '')
        percent = ing.get('percent', 0)
        weight = int(total_weight * percent / 100)
        if weight > 0 and name:
            result.append({
                'name': name,
                'estimated_weight_grams': weight,
                'type': ing.get('type', 'other'),
                'confidence': 0.8,
                'percent': percent
            })
    
    return result

def calculate_dish_nutrition(dish_name: str, total_weight: int = 300) -> Dict:
    """Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµÑ‚ ĞšĞ‘Ğ–Ğ£ Ğ´Ğ»Ñ� Ğ³Ğ¾Ñ‚Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ğ±Ğ»Ñ�Ğ´Ğ°."""
    from services.food_api import LOCAL_FOOD_DB
    
    dish_name_lower = dish_name.lower().strip()
    dish_data = COMPOSITE_DISHES.get(dish_name_lower)
    
    if not dish_data:
        for key, value in COMPOSITE_DISHES.items():
            if key in dish_name_lower or dish_name_lower in key:
                dish_data = value
                break
    
    if not dish_data:
        return {'name': dish_name, 'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
    
    # Ğ•Ñ�Ğ»Ğ¸ ĞµÑ�Ñ‚ÑŒ nutrition_per_100 â€” Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ ĞµĞ³Ğ¾
    nutrition = dish_data.get('nutrition_per_100', {})
    if nutrition:
        multiplier = total_weight / 100
        return {
            'name': dish_data.get('name', dish_name),
            'calories': round(nutrition.get('calories', 0) * multiplier, 1),
            'protein': round(nutrition.get('protein', 0) * multiplier, 1),
            'fat': round(nutrition.get('fat', 0) * multiplier, 1),
            'carbs': round(nutrition.get('carbs', 0) * multiplier, 1),
        }
    
    # Ğ˜Ğ½Ğ°Ñ‡Ğµ Ñ�Ñ‡Ğ¸Ñ‚Ğ°ĞµĞ¼ Ğ¿Ğ¾ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼
    ingredients = dish_data.get('ingredients', [])
    total_calories = total_protein = total_fat = total_carbs = 0
    
    for ing in ingredients:
        ing_name = ing.get('name', '')
        percent = ing.get('percent', 0)
        ing_weight = int(total_weight * percent / 100)
        
        # Ğ˜Ñ‰ĞµĞ¼ Ğ² LOCAL_FOOD_DB
        food_data = None
        for key, value in LOCAL_FOOD_DB.items():
            if ing_name.lower() in key or key in ing_name.lower():
                food_data = value
                break
        
        if food_data:
            multiplier = ing_weight / 100
            total_calories += food_data.get('calories', 0) * multiplier
            total_protein += food_data.get('protein', 0) * multiplier
            total_fat += food_data.get('fat', 0) * multiplier
            total_carbs += food_data.get('carbs', 0) * multiplier
    
    return {
        'name': dish_data.get('name', dish_name),
        'calories': round(total_calories, 1),
        'protein': round(total_protein, 1),
        'fat': round(total_fat, 1),
        'carbs': round(total_carbs, 1),
    }
def identify_known_dish_by_ingredients(ingredient_names_en: List[str], prep_style: str = 'mixed') -> Optional[str]:
    """
    Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµÑ‚ Ğ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ¾Ğµ Ğ±Ğ»Ñ�Ğ´Ğ¾ Ğ¿Ğ¾ Ñ�Ğ¿Ğ¸Ñ�ĞºÑƒ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ¾Ğ² (Ğ½Ğ° Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¾Ğ¼) Ğ¸ Ñ�Ñ‚Ğ¸Ğ»Ñ� Ğ¿Ñ€Ğ¸Ğ³Ğ¾Ñ‚Ğ¾Ğ²Ğ»ĞµĞ½Ğ¸Ñ�.
    Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµÑ‚ Ğ±Ğ°Ğ·Ñƒ COMPOSITE_DISHES Ğ¸ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´Ñ‡Ğ¸Ğº AI_TO_DB_MAPPING.
    Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ±Ğ»Ñ�Ğ´Ğ° (Ğ½Ğ° Ñ€ÑƒÑ�Ñ�ĞºĞ¾Ğ¼) Ğ¸Ğ»Ğ¸ None.
    """
    # ĞŸĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ¸Ğ¼ Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ� Ğ² Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğµ
    ingredient_names_ru = set()
    for name_en in ingredient_names_en:
        name_clean = name_en.lower().replace('grilled ', '').replace('fried ', '').replace('boiled ', '')
        name_clean = name_clean.replace('baked ', '').replace('roasted ', '').replace('steamed ', '')
        name_clean = name_clean.replace('raw ', '').replace('fresh ', '')
        # Ğ˜Ñ‰ĞµĞ¼ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´
        ru = AI_TO_DB_MAPPING.get(name_clean)
        if ru:
            ingredient_names_ru.add(ru)
        else:
            # Ğ•Ñ�Ğ»Ğ¸ Ğ½ĞµÑ‚ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ°, Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¾Ñ€Ğ¸Ğ³Ğ¸Ğ½Ğ°Ğ» (Ğ²Ğ¾Ğ·Ğ¼Ğ¾Ğ¶Ğ½Ğ¾, Ğ¾Ğ½ ÑƒĞ¶Ğµ Ğ½Ğ° Ñ€ÑƒÑ�Ñ�ĞºĞ¾Ğ¼)
            ingredient_names_ru.add(name_clean)

    logger.info(f"ğŸ”� ĞŸĞ¾Ğ¸Ñ�Ğº Ğ±Ğ»Ñ�Ğ´Ğ° Ğ¿Ğ¾ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼: {ingredient_names_ru}")

    best_match = None
    best_score = 0.0

    for dish_key, dish_data in COMPOSITE_DISHES.items():
        dish_ingredients = dish_data.get('ingredients', [])
        dish_names = [ing['name'].lower() for ing in dish_ingredients]
        dish_set = set(dish_names)

        # Ğ–Ğ°ĞºĞºĞ°Ñ€Ğ¾Ğ²Ñ�ĞºĞ¾Ğµ Ñ�Ñ…Ğ¾Ğ´Ñ�Ñ‚Ğ²Ğ¾: Ğ¿ĞµÑ€ĞµÑ�ĞµÑ‡ĞµĞ½Ğ¸Ğµ / Ğ¾Ğ±ÑŠĞµĞ´Ğ¸Ğ½ĞµĞ½Ğ¸Ğµ
        intersection = ingredient_names_ru & dish_set
        union = ingredient_names_ru | dish_set
        if not union:
            continue
        score = len(intersection) / len(union)

        # Ğ�ĞµĞ±Ğ¾Ğ»ÑŒÑˆĞ¾Ğ¹ Ğ±Ğ¾Ğ½ÑƒÑ� Ğ·Ğ° Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğµ Ñ�Ñ‚Ğ¸Ğ»Ñ� Ğ¿Ñ€Ğ¸Ğ³Ğ¾Ñ‚Ğ¾Ğ²Ğ»ĞµĞ½Ğ¸Ñ�
        if dish_data.get('prep_style') == prep_style:
            score += 0.05

        if score > best_score and score >= 0.3:  # Ğ¿Ğ¾Ñ€Ğ¾Ğ³ 30%
            best_score = score
            best_match = dish_data['name']

    if best_match:
        logger.info(f"ğŸ�¯ Ğ˜Ğ´ĞµĞ½Ñ‚Ğ¸Ñ„Ğ¸Ñ†Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¾ Ğ±Ğ»Ñ�Ğ´Ğ¾ Ğ¿Ğ¾ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼: {best_match} (score: {best_score:.2f})")
        return best_match

    return None

def find_matching_dishes_by_ingredients(ingredient_names_en: List[str], threshold: float = 0.4) -> List[Dict]:
    """
    Ğ˜Ñ‰ĞµÑ‚ Ğ±Ğ»Ñ�Ğ´Ğ°, ĞºĞ¾Ñ‚Ğ¾Ñ€Ñ‹Ğµ Ñ�Ğ¾Ğ´ĞµÑ€Ğ¶Ğ°Ñ‚ ÑƒĞºĞ°Ğ·Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ (Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ� Ğ´Ğ°Ğ½Ñ‹ Ğ½Ğ° Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¾Ğ¼).
    Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ Ñ�Ğ¿Ğ¸Ñ�Ğ¾Ğº Ğ±Ğ»Ñ�Ğ´ Ñ� Ğ¾Ñ†ĞµĞ½ĞºĞ¾Ğ¹ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ñ�.
    """
    # ĞŸĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ¸Ğ¼ Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ� Ğ² Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğµ
    ingredient_names_ru = set()
    for name_en in ingredient_names_en:
        name_clean = name_en.lower().replace('grilled ', '').replace('fried ', '').replace('boiled ', '')
        name_clean = name_clean.replace('baked ', '').replace('roasted ', '').replace('steamed ', '')
        name_clean = name_clean.replace('raw ', '').replace('fresh ', '')
        # Ğ˜Ñ‰ĞµĞ¼ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´
        ru = AI_TO_DB_MAPPING.get(name_clean)
        if ru:
            ingredient_names_ru.add(ru.lower())
        else:
            # Ğ•Ñ�Ğ»Ğ¸ Ğ½ĞµÑ‚ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ°, Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ ĞºĞ°Ğº ĞµÑ�Ñ‚ÑŒ (Ğ²Ğ¾Ğ·Ğ¼Ğ¾Ğ¶Ğ½Ğ¾, ÑƒĞ¶Ğµ Ñ€ÑƒÑ�Ñ�ĞºĞ¾Ğµ)
            ingredient_names_ru.add(name_clean)

    logger.info(f"ğŸ”� ĞŸĞ¾Ğ¸Ñ�Ğº Ğ±Ğ»Ñ�Ğ´ Ğ¿Ğ¾ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼ (Ñ€ÑƒÑ�): {ingredient_names_ru}")

    matches = []
    for dish_key, dish_data in COMPOSITE_DISHES.items():
        dish_ingredients = dish_data.get('ingredients', [])
        dish_ingredient_names = {ing['name'].lower() for ing in dish_ingredients}

        # Ğ–Ğ°ĞºĞºĞ°Ñ€Ğ¾Ğ²Ñ�ĞºĞ¾Ğµ Ñ�Ñ…Ğ¾Ğ´Ñ�Ñ‚Ğ²Ğ¾: Ğ¿ĞµÑ€ĞµÑ�ĞµÑ‡ĞµĞ½Ğ¸Ğµ / Ğ¾Ğ±ÑŠĞµĞ´Ğ¸Ğ½ĞµĞ½Ğ¸Ğµ
        intersection = ingredient_names_ru & dish_ingredient_names
        union = ingredient_names_ru | dish_ingredient_names
        if not union:
            continue
        score = len(intersection) / len(union)

        if score >= threshold:
            matches.append({
                'name': dish_data['name'],
                'score': round(score, 2),
                'dish_key': dish_key,
                'nutrition_per_100': dish_data.get('nutrition_per_100', {}),
                'default_weight': dish_data.get('default_weight', 300),
                'matched_ingredients': list(intersection)
            })

    matches.sort(key=lambda x: x['score'], reverse=True)
    logger.info(f"ğŸ”� Ğ�Ğ°Ğ¹Ğ´ĞµĞ½Ğ¾ {len(matches)} Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğ¹ Ğ¿Ğ¾ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼")
    return matches
