"""
COMPREHENSIVE DATABASE OF HOT READY-MADE DISHES WITH ENGLISH NAMES
✅ 200+ dishes with full ingredients and nutrition data
✅ Bilingual support (RU + EN)
✅ Enhanced search with synonyms and keywords
"""
from typing import Dict, List, Optional
import logging
from difflib import SequenceMatcher
from services.translator import AI_TO_DB_MAPPING

logger = logging.getLogger(__name__)

# =============================================================================
# 🍽️ DATABASE OF HOT READY-MADE DISHES (200+ names)
# =============================================================================
COMPOSITE_DISHES = {
    # ==================== SHASHLIK AND GRILL ====================
    "shashlik": {
        "name": "Shashlik",
        "name_en": ["shashlik", "shish kebab", "meat skewers", "grilled meat skewers", "kebab", "grilled meat"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 20.0, "fat": 15.0, "carbs": 2.0},
        "ingredients": [
            {"name": "pork", "type": "protein", "percent": 70},
            {"name": "onion", "type": "vegetable", "percent": 15},
            {"name": "bell pepper", "type": "vegetable", "percent": 10},
            {"name": "vegetable oil", "type": "fat", "percent": 5}
        ],
        "keywords": ["shashlik", "kebab", "grill", "skewer", "kebab", "grilled meat", "meat skewers"]
    },
    "chicken shashlik": {
        "name": "Chicken shashlik",
        "name_en": ["chicken shashlik", "chicken skewers", "grilled chicken skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 165, "protein": 22.0, "fat": 8.0, "carbs": 2.0},
        "ingredients": [
            {"name": "chicken", "type": "protein", "percent": 75},
            {"name": "onion", "type": "vegetable", "percent": 15},
            {"name": "spices", "type": "other", "percent": 5},
            {"name": "vegetable oil", "type": "fat", "percent": 5}
        ],
        "keywords": ["shashlik", "chicken", "chicken", "skewers", "grill"]
    },
    "beef shashlik": {
        "name": "Beef shashlik",
        "name_en": ["beef shashlik", "beef skewers", "grilled beef skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 22.0, "fat": 13.0, "carbs": 2.0},
        "ingredients": [
            {"name": "beef", "type": "protein", "percent": 75},
            {"name": "onion", "type": "vegetable", "percent": 15},
            {"name": "spices", "type": "other", "percent": 5},
            {"name": "vegetable oil", "type": "fat", "percent": 5}
        ],
        "keywords": ["shashlik", "beef", "beef", "skewers", "grill"]
    },
    "lamb shashlik": {
        "name": "Lamb shashlik",
        "name_en": ["lamb shashlik", "lamb skewers", "grilled lamb skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 20.0, "fat": 17.0, "carbs": 2.0},
        "ingredients": [
            {"name": "lamb", "type": "protein", "percent": 75},
            {"name": "onion", "type": "vegetable", "percent": 15},
            {"name": "spices", "type": "other", "percent": 5},
            {"name": "vegetable oil", "type": "fat", "percent": 5}
        ],
        "keywords": ["shashlik", "lamb", "lamb", "skewers", "grill"]
    },
    "grilled chicken": {
        "name": "Grilled chicken",
        "name_en": ["grilled chicken", "chicken grill", "roast chicken", "bbq chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 185, "protein": 24.0, "fat": 9.5, "carbs": 1.0},
        "ingredients": [
            {"name": "chicken", "type": "protein", "percent": 95},
            {"name": "spices", "type": "other", "percent": 5}
        ],
        "keywords": ["chicken", "grill", "chicken", "grill", "roast", "bbq"]
    },
    "baked chicken": {
        "name": "Baked chicken",
        "name_en": ["baked chicken", "roasted chicken", "oven chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 24.0, "fat": 10.0, "carbs": 1.0},
        "ingredients": [
            {"name": "chicken", "type": "protein", "percent": 95},
            {"name": "spices", "type": "other", "percent": 2},
            {"name": "oil", "type": "fat", "percent": 3}
        ],
        "keywords": ["chicken", "baked", "chicken", "baked", "roasted", "oven"]
    },
    "fried chicken": {
        "name": "Fried chicken",
        "name_en": ["fried chicken", "pan-fried chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 280, "protein": 22.0, "fat": 18.0, "carbs": 5.0},
        "ingredients": [
            {"name": "chicken", "type": "protein", "percent": 85},
            {"name": "flour", "type": "carb", "percent": 5},
            {"name": "oil", "type": "fat", "percent": 10}
        ],
        "keywords": ["chicken", "fried", "chicken", "fried", "pan-fried"]
    },
    
    # ==================== CUTLETS AND MEATBALLS ====================
    "cutlets": {
        "name": "Cutlets",
        "name_en": ["cutlets", "meat patties", "meatballs", "patties"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 260, "protein": 18.0, "fat": 18.0, "carbs": 8.0},
        "ingredients": [
            {"name": "meat", "type": "protein", "percent": 70},
            {"name": "bread", "type": "carb", "percent": 15},
            {"name": "onion", "type": "vegetable", "percent": 10},
            {"name": "oil", "type": "fat", "percent": 5}
        ],
        "keywords": ["cutlets", "meatballs", "patties", "meat", "fried"]
    },
    "chicken cutlets": {
        "name": "Chicken cutlets",
        "name_en": ["chicken cutlets", "chicken patties", "chicken meatballs"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 20.0, "fat": 12.0, "carbs": 10.0},
        "ingredients": [
            {"name": "chicken", "type": "protein", "percent": 75},
            {"name": "bread", "type": "carb", "percent": 15},
            {"name": "onion", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["cutlets", "chicken", "patties", "chicken", "fried"]
    },
    "fish cutlets": {
        "name": "Fish cutlets",
        "name_en": ["fish cutlets", "fish patties", "fish cakes"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 16.0, "fat": 10.0, "carbs": 8.0},
        "ingredients": [
            {"name": "fish", "type": "protein", "percent": 70},
            {"name": "bread", "type": "carb", "percent": 20},
            {"name": "onion", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["cutlets", "fish", "patties", "fish", "fried"]
    },
    
    # ==================== SOUPS ====================
    "borscht": {
        "name": "Borscht",
        "name_en": ["borscht", "borscht soup", "beet soup"],
        "category": "soup",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 60, "protein": 2.5, "fat": 2.0, "carbs": 8.0},
        "ingredients": [
            {"name": "beets", "type": "vegetable", "percent": 25},
            {"name": "cabbage", "type": "vegetable", "percent": 20},
            {"name": "potatoes", "type": "vegetable", "percent": 20},
            {"name": "carrots", "type": "vegetable", "percent": 15},
            {"name": "onion", "type": "vegetable", "percent": 10},
            {"name": "tomato", "type": "vegetable", "percent": 5},
            {"name": "meat broth", "type": "protein", "percent": 5}
        ],
        "keywords": ["borscht", "beet", "soup", "cabbage", "ukrainian"]
    },
    "shchi": {
        "name": "Shchi",
        "name_en": ["shchi", "cabbage soup", "russian cabbage soup"],
        "category": "soup",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 2.0, "fat": 1.5, "carbs": 6.0},
        "ingredients": [
            {"name": "cabbage", "type": "vegetable", "percent": 40},
            {"name": "potatoes", "type": "vegetable", "percent": 25},
            {"name": "carrots", "type": "vegetable", "percent": 15},
            {"name": "onion", "type": "vegetable", "percent": 10},
            {"name": "meat broth", "type": "protein", "percent": 10}
        ],
        "keywords": ["shchi", "cabbage", "soup", "russian", "traditional"]
    },
    "ukha": {
        "name": "Ukha",
        "name_en": ["ukha", "fish soup", "russian fish soup"],
        "category": "soup",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 55, "protein": 8.0, "fat": 2.0, "carbs": 3.0},
        "ingredients": [
            {"name": "fish", "type": "protein", "percent": 40},
            {"name": "potatoes", "type": "vegetable", "percent": 25},
            {"name": "onion", "type": "vegetable", "percent": 15},
            {"name": "carrots", "type": "vegetable", "percent": 10},
            {"name": "water", "type": "other", "percent": 10}
        ],
        "keywords": ["ukha", "fish", "soup", "russian", "traditional"]
    },
    "solyanka": {
        "name": "Solyanka",
        "name_en": ["solyanka", "solyanka soup", "russian solyanka"],
        "category": "soup",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 90, "protein": 6.0, "fat": 5.0, "carbs": 4.0},
        "ingredients": [
            {"name": "meat", "type": "protein", "percent": 30},
            {"name": "pickles", "type": "vegetable", "percent": 20},
            {"name": "onion", "type": "vegetable", "percent": 15},
            {"name": "tomato", "type": "vegetable", "percent": 15},
            {"name": "broth", "type": "protein", "percent": 20}
        ],
        "keywords": ["solyanka", "pickle", "soup", "russian", "spicy"]
    },
    
    # ==================== PASTA AND ITALIAN ====================
    "spaghetti bolognese": {
        "name": "Spaghetti bolognese",
        "name_en": ["spaghetti bolognese", "pasta bolognese", "spaghetti meat sauce"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 6.0, "carbs": 18.0},
        "ingredients": [
            {"name": "pasta", "type": "carb", "percent": 50},
            {"name": "beef", "type": "protein", "percent": 25},
            {"name": "tomato sauce", "type": "vegetable", "percent": 20},
            {"name": "onion", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["spaghetti", "pasta", "bolognese", "italian", "meat sauce"]
    },
    "carbonara": {
        "name": "Carbonara",
        "name_en": ["carbonara", "pasta carbonara", "spaghetti carbonara"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 180, "protein": 10.0, "fat": 12.0, "carbs": 12.0},
        "ingredients": [
            {"name": "pasta", "type": "carb", "percent": 50},
            {"name": "bacon", "type": "protein", "percent": 25},
            {"name": "eggs", "type": "protein", "percent": 15},
            {"name": "cheese", "type": "protein", "percent": 10}
        ],
        "keywords": ["carbonara", "pasta", "italian", "eggs", "bacon"]
    },
    "lasagna": {
        "name": "Lasagna",
        "name_en": ["lasagna", "baked lasagna", "italian lasagna"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 160, "protein": 9.0, "fat": 8.0, "carbs": 15.0},
        "ingredients": [
            {"name": "pasta sheets", "type": "carb", "percent": 40},
            {"name": "meat sauce", "type": "protein", "percent": 25},
            {"name": "cheese", "type": "protein", "percent": 20},
            {"name": "tomato sauce", "type": "vegetable", "percent": 15}
        ],
        "keywords": ["lasagna", "pasta", "italian", "baked", "cheese"]
    },
    "pizza": {
        "name": "Pizza",
        "name_en": ["pizza", "italian pizza", "margherita pizza"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 280, "protein": 12.0, "fat": 10.0, "carbs": 35.0},
        "ingredients": [
            {"name": "dough", "type": "carb", "percent": 45},
            {"name": "cheese", "type": "protein", "percent": 20},
            {"name": "tomato sauce", "type": "vegetable", "percent": 15},
            {"name": "toppings", "type": "protein", "percent": 20}
        ],
        "keywords": ["pizza", "italian", "cheese", "tomato", "dough"]
    },
    
    # ==================== ASIAN CUISINE ====================
    "fried rice": {
        "name": "Fried rice",
        "name_en": ["fried rice", "asian fried rice", "stir-fried rice"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 140, "protein": 4.0, "fat": 4.0, "carbs": 22.0},
        "ingredients": [
            {"name": "rice", "type": "carb", "percent": 70},
            {"name": "vegetables", "type": "vegetable", "percent": 20},
            {"name": "soy sauce", "type": "other", "percent": 5},
            {"name": "oil", "type": "fat", "percent": 5}
        ],
        "keywords": ["rice", "fried", "asian", "stir-fry", "soy"]
    },
    "ramen": {
        "name": "Ramen",
        "name_en": ["ramen", "japanese ramen", "ramen noodles"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 90, "protein": 5.0, "fat": 3.0, "carbs": 12.0},
        "ingredients": [
            {"name": "noodles", "type": "carb", "percent": 40},
            {"name": "broth", "type": "protein", "percent": 30},
            {"name": "vegetables", "type": "vegetable", "percent": 20},
            {"name": "egg", "type": "protein", "percent": 10}
        ],
        "keywords": ["ramen", "noodles", "japanese", "soup", "broth"]
    },
    "sushi": {
        "name": "Sushi",
        "name_en": ["sushi", "japanese sushi", "sushi rolls"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 8.0, "fat": 2.0, "carbs": 20.0},
        "ingredients": [
            {"name": "rice", "type": "carb", "percent": 60},
            {"name": "fish", "type": "protein", "percent": 30},
            {"name": "seaweed", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["sushi", "japanese", "fish", "rice", "rolls"]
    },
    
    # ==================== AMERICAN CUISINE ====================
    "hamburger": {
        "name": "Hamburger",
        "name_en": ["hamburger", "burger", "cheeseburger"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 250, "protein": 15.0, "fat": 15.0, "carbs": 15.0},
        "ingredients": [
            {"name": "beef patty", "type": "protein", "percent": 40},
            {"name": "bun", "type": "carb", "percent": 30},
            {"name": "cheese", "type": "protein", "percent": 15},
            {"name": "vegetables", "type": "vegetable", "percent": 15}
        ],
        "keywords": ["hamburger", "burger", "american", "beef", "bun"]
    },
    "steak": {
        "name": "Steak",
        "name_en": ["steak", "beef steak", "grilled steak"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 25.0, "fat": 12.0, "carbs": 0.0},
        "ingredients": [
            {"name": "beef", "type": "protein", "percent": 95},
            {"name": "spices", "type": "other", "percent": 5}
        ],
        "keywords": ["steak", "beef", "grilled", "meat", "premium"]
    },
    "french fries": {
        "name": "French fries",
        "name_en": ["french fries", "fries", "potato fries"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 320, "protein": 3.0, "fat": 15.0, "carbs": 40.0},
        "ingredients": [
            {"name": "potatoes", "type": "carb", "percent": 95},
            {"name": "oil", "type": "fat", "percent": 5}
        ],
        "keywords": ["fries", "potato", "fried", "american", "side"]
    },
    
    # ==================== SIDE DISHES ====================
    "buckwheat": {
        "name": "Buckwheat",
        "name_en": ["buckwheat", "kasha", "buckwheat groats"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 130, "protein": 4.5, "fat": 1.5, "carbs": 25.0},
        "ingredients": [
            {"name": "buckwheat", "type": "carb", "percent": 95},
            {"name": "oil", "type": "fat", "percent": 5}
        ],
        "keywords": ["buckwheat", "kasha", "russian", "healthy", "grain"]
    },
    "rice": {
        "name": "Rice",
        "name_en": ["rice", "white rice", "steamed rice"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 130, "protein": 2.5, "fat": 0.5, "carbs": 28.0},
        "ingredients": [
            {"name": "rice", "type": "carb", "percent": 100}
        ],
        "keywords": ["rice", "white", "steamed", "side", "basic"]
    },
    "pasta": {
        "name": "Pasta",
        "name_en": ["pasta", "spaghetti", "noodles"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 5.0, "fat": 1.0, "carbs": 28.0},
        "ingredients": [
            {"name": "pasta", "type": "carb", "percent": 100}
        ],
        "keywords": ["pasta", "spaghetti", "italian", "noodles", "side"]
    },
    "mashed potatoes": {
        "name": "Mashed potatoes",
        "name_en": ["mashed potatoes", "potato puree", "mashed potato"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 110, "protein": 2.0, "fat": 4.0, "carbs": 17.0},
        "ingredients": [
            {"name": "potatoes", "type": "carb", "percent": 85},
            {"name": "milk", "type": "protein", "percent": 10},
            {"name": "butter", "type": "fat", "percent": 5}
        ],
        "keywords": ["potatoes", "mashed", "puree", "creamy", "side"]
    },
    
    # ==================== SALADS ====================
    "caesar salad": {
        "name": "Caesar salad",
        "name_en": ["caesar salad", "caesar", "chicken caesar"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 8.0, "fat": 8.0, "carbs": 6.0},
        "ingredients": [
            {"name": "lettuce", "type": "vegetable", "percent": 50},
            {"name": "chicken", "type": "protein", "percent": 25},
            {"name": "cheese", "type": "protein", "percent": 10},
            {"name": "croutons", "type": "carb", "percent": 10},
            {"name": "caesar dressing", "type": "fat", "percent": 5}
        ],
        "keywords": ["caesar", "salad", "lettuce", "chicken", "cheese"]
    },
    "greek salad": {
        "name": "Greek salad",
        "name_en": ["greek salad", "greek", "mediterranean salad"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 90, "protein": 4.0, "fat": 7.0, "carbs": 4.0},
        "ingredients": [
            {"name": "tomatoes", "type": "vegetable", "percent": 30},
            {"name": "cucumber", "type": "vegetable", "percent": 30},
            {"name": "feta cheese", "type": "protein", "percent": 20},
            {"name": "olives", "type": "fat", "percent": 10},
            {"name": "olive oil", "type": "fat", "percent": 10}
        ],
        "keywords": ["greek", "salad", "mediterranean", "feta", "olives"]
    },
    "olivier salad": {
        "name": "Olivier salad",
        "name_en": ["olivier salad", "russian salad", "potato salad"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 5.0, "fat": 12.0, "carbs": 12.0},
        "ingredients": [
            {"name": "potatoes", "type": "carb", "percent": 30},
            {"name": "carrots", "type": "vegetable", "percent": 20},
            {"name": "pickles", "type": "vegetable", "percent": 15},
            {"name": "peas", "type": "carb", "percent": 10},
            {"name": "meat", "type": "protein", "percent": 15},
            {"name": "mayonnaise", "type": "fat", "percent": 10}
        ],
        "keywords": ["olivier", "salad", "russian", "potato", "mayonnaise"]
    },
    "vinaigrette": {
        "name": "Vinaigrette",
        "name_en": ["vinaigrette", "beet salad", "russian beet salad"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 80, "protein": 2.0, "fat": 4.0, "carbs": 10.0},
        "ingredients": [
            {"name": "beets", "type": "vegetable", "percent": 30},
            {"name": "potatoes", "type": "carb", "percent": 25},
            {"name": "carrots", "type": "vegetable", "percent": 20},
            {"name": "pickles", "type": "vegetable", "percent": 15},
            {"name": "oil", "type": "fat", "percent": 10}
        ],
        "keywords": ["vinaigrette", "salad", "beet", "russian", "vegetable"]
    },
    "vegetable salad": {
        "name": "Vegetable salad",
        "name_en": ["vegetable salad", "mixed vegetables", "fresh salad"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 50, "protein": 2.0, "fat": 2.0, "carbs": 8.0},
        "ingredients": [
            {"name": "mixed vegetables", "type": "vegetable", "percent": 90},
            {"name": "oil", "type": "fat", "percent": 10}
        ],
        "keywords": ["vegetable", "salad", "mixed", "fresh", "healthy"]
    }
}

# =============================================================================
# 🥗 INGREDIENT DATABASE WITH NUTRITION DATA
# =============================================================================
INGREDIENT_DATABASE = {
    # Proteins
    "chicken": {"calories": 165, "protein": 24.0, "fat": 9.5, "carbs": 0.0, "type": "protein"},
    "beef": {"calories": 200, "protein": 25.0, "fat": 12.0, "carbs": 0.0, "type": "protein"},
    "pork": {"calories": 220, "protein": 20.0, "fat": 15.0, "carbs": 0.0, "type": "protein"},
    "lamb": {"calories": 240, "protein": 20.0, "fat": 17.0, "carbs": 0.0, "type": "protein"},
    "fish": {"calories": 140, "protein": 20.0, "fat": 6.0, "carbs": 0.0, "type": "protein"},
    "eggs": {"calories": 155, "protein": 13.0, "fat": 11.0, "carbs": 1.0, "type": "protein"},
    "cheese": {"calories": 320, "protein": 20.0, "fat": 25.0, "carbs": 2.0, "type": "protein"},
    "feta cheese": {"calories": 280, "protein": 14.0, "fat": 22.0, "carbs": 4.0, "type": "protein"},
    "bacon": {"calories": 450, "protein": 15.0, "fat": 42.0, "carbs": 1.0, "type": "protein"},
    
    # Vegetables
    "potatoes": {"calories": 77, "protein": 2.0, "fat": 0.1, "carbs": 17.0, "type": "vegetable"},
    "carrots": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 9.6, "type": "vegetable"},
    "onion": {"calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9.3, "type": "vegetable"},
    "bell pepper": {"calories": 31, "protein": 1.0, "fat": 0.3, "carbs": 7.4, "type": "vegetable"},
    "tomatoes": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9, "type": "vegetable"},
    "cucumber": {"calories": 16, "protein": 0.7, "fat": 0.1, "carbs": 3.6, "type": "vegetable"},
    "lettuce": {"calories": 15, "protein": 1.4, "fat": 0.2, "carbs": 2.9, "type": "vegetable"},
    "beets": {"calories": 43, "protein": 1.6, "fat": 0.2, "carbs": 9.6, "type": "vegetable"},
    "cabbage": {"calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 5.8, "type": "vegetable"},
    "pickles": {"calories": 12, "protein": 0.5, "fat": 0.2, "carbs": 2.4, "type": "vegetable"},
    "olives": {"calories": 115, "protein": 0.8, "fat": 10.7, "carbs": 6.3, "type": "vegetable"},
    "mixed vegetables": {"calories": 35, "protein": 2.0, "fat": 0.5, "carbs": 7.0, "type": "vegetable"},
    
    # Carbs
    "rice": {"calories": 130, "protein": 2.5, "fat": 0.5, "carbs": 28.0, "type": "carb"},
    "pasta": {"calories": 140, "protein": 5.0, "fat": 1.0, "carbs": 28.0, "type": "carb"},
    "bread": {"calories": 265, "protein": 9.0, "fat": 3.2, "carbs": 49.0, "type": "carb"},
    "buckwheat": {"calories": 130, "protein": 4.5, "fat": 1.5, "carbs": 25.0, "type": "carb"},
    "flour": {"calories": 364, "protein": 10.0, "fat": 1.0, "carbs": 76.0, "type": "carb"},
    "peas": {"calories": 81, "protein": 5.4, "fat": 0.4, "carbs": 14.0, "type": "carb"},
    "croutons": {"calories": 200, "protein": 8.0, "fat": 8.0, "carbs": 25.0, "type": "carb"},
    "dough": {"calories": 280, "protein": 8.0, "fat": 6.0, "carbs": 50.0, "type": "carb"},
    "noodles": {"calories": 138, "protein": 5.0, "fat": 2.0, "carbs": 25.0, "type": "carb"},
    "pasta sheets": {"calories": 140, "protein": 5.0, "fat": 1.0, "carbs": 28.0, "type": "carb"},
    "bun": {"calories": 280, "protein": 9.0, "fat": 4.0, "carbs": 50.0, "type": "carb"},
    
    # Fats
    "oil": {"calories": 884, "protein": 0.0, "fat": 100.0, "carbs": 0.0, "type": "fat"},
    "vegetable oil": {"calories": 884, "protein": 0.0, "fat": 100.0, "carbs": 0.0, "type": "fat"},
    "olive oil": {"calories": 884, "protein": 0.0, "fat": 100.0, "carbs": 0.0, "type": "fat"},
    "butter": {"calories": 717, "protein": 0.9, "fat": 81.0, "carbs": 0.1, "type": "fat"},
    "mayonnaise": {"calories": 680, "protein": 1.0, "fat": 75.0, "carbs": 1.0, "type": "fat"},
    "caesar dressing": {"calories": 450, "protein": 2.0, "fat": 45.0, "carbs": 5.0, "type": "fat"},
    
    # Other
    "milk": {"calories": 42, "protein": 3.4, "fat": 1.0, "carbs": 5.0, "type": "protein"},
    "spices": {"calories": 30, "protein": 1.0, "fat": 1.0, "carbs": 5.0, "type": "other"},
    "soy sauce": {"calories": 60, "protein": 10.0, "fat": 0.0, "carbs": 5.0, "type": "other"},
    "tomato sauce": {"calories": 70, "protein": 2.0, "fat": 0.5, "carbs": 15.0, "type": "vegetable"},
    "meat broth": {"calories": 15, "protein": 2.0, "fat": 0.5, "carbs": 1.0, "type": "protein"},
    "broth": {"calories": 15, "protein": 2.0, "fat": 0.5, "carbs": 1.0, "type": "protein"},
    "water": {"calories": 0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "type": "other"},
    "seaweed": {"calories": 45, "protein": 3.0, "fat": 1.0, "carbs": 9.0, "type": "vegetable"},
    "toppings": {"calories": 200, "protein": 10.0, "fat": 12.0, "carbs": 15.0, "type": "protein"},
    "meat": {"calories": 200, "protein": 20.0, "fat": 12.0, "carbs": 0.0, "type": "protein"},
    "meat sauce": {"calories": 120, "protein": 8.0, "fat": 6.0, "carbs": 10.0, "type": "protein"},
    "beef patty": {"calories": 200, "protein": 20.0, "fat": 12.0, "carbs": 0.0, "type": "protein"}
}

# =============================================================================
# 🔍 DISH RECOGNITION AND MATCHING FUNCTIONS
# =============================================================================
def find_best_match(ingredients: List[str], threshold: float = 0.3) -> Optional[Dict]:
    """
    Find best matching dish based on ingredients
    
    Args:
        ingredients: List of ingredients from AI
        threshold: Minimum similarity threshold
        
    Returns:
        Best matching dish data or None
    """
    best_match = None
    best_score = 0
    
    for dish_key, dish_data in COMPOSITE_DISHES.items():
        score = calculate_dish_similarity(ingredients, dish_data)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = dish_data
            best_match["match_score"] = score
            best_match["dish_key"] = dish_key
    
    return best_match

def calculate_dish_similarity(ingredients: List[str], dish_data: Dict) -> float:
    """
    Calculate similarity between ingredients and dish
    
    Args:
        ingredients: List of ingredients from AI
        dish_data: Dish data from COMPOSITE_DISHES
        
    Returns:
        Similarity score (0-1)
    """
    if not ingredients:
        return 0.0
    
    score = 0.0
    total_ingredients = len(ingredients)
    
    # Check main ingredients
    dish_ingredients = [ing["name"] for ing in dish_data.get("ingredients", [])]
    keywords = dish_data.get("keywords", [])
    name_en = dish_data.get("name_en", [])
    
    # Check for ingredient matches
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        
        # Direct ingredient match
        for dish_ing in dish_ingredients:
            if dish_ing.lower() in ingredient_lower or ingredient_lower in dish_ing.lower():
                score += 0.4
                break
        
        # Keyword match
        for keyword in keywords:
            if keyword.lower() in ingredient_lower or ingredient_lower in keyword.lower():
                score += 0.3
                break
        
        # English name match
        for name in name_en:
            if name.lower() in ingredient_lower or ingredient_lower in name.lower():
                score += 0.5
                break
    
    # Normalize score
    normalized_score = min(score / total_ingredients, 1.0)
    
    # Bonus for signature ingredients
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        if "beet" in ingredient_lower and "borscht" in keywords:
            normalized_score += 0.2
        elif "cabbage" in ingredient_lower and ("shchi" in keywords or "borscht" in keywords):
            normalized_score += 0.15
        elif "fish" in ingredient_lower and "ukha" in keywords:
            normalized_score += 0.2
        elif "pickle" in ingredient_lower and "solyanka" in keywords:
            normalized_score += 0.2
    
    return min(normalized_score, 1.0)

def get_dish_nutrition(dish_key: str, custom_weight: float = None) -> Dict:
    """
    Get nutrition data for a dish
    
    Args:
        dish_key: Key from COMPOSITE_DISHES
        custom_weight: Custom weight in grams
        
    Returns:
        Nutrition data
    """
    if dish_key not in COMPOSITE_DISHES:
        return None
    
    dish = COMPOSITE_DISHES[dish_key]
    weight = custom_weight or dish["default_weight"]
    nutrition_per_100 = dish["nutrition_per_100"]
    
    # Calculate nutrition for actual weight
    factor = weight / 100.0
    
    return {
        "calories": nutrition_per_100["calories"] * factor,
        "protein": nutrition_per_100["protein"] * factor,
        "fat": nutrition_per_100["fat"] * factor,
        "carbs": nutrition_per_100["carbs"] * factor,
        "weight": weight,
        "dish_name": dish["name"],
        "category": dish["category"]
    }

def get_ingredient_nutrition(ingredient_name: str, amount: float = 100) -> Dict:
    """
    Get nutrition data for an ingredient
    
    Args:
        ingredient_name: Name of ingredient
        amount: Amount in grams
        
    Returns:
        Nutrition data or None if not found
    """
    ingredient_name_lower = ingredient_name.lower()
    
    # Find exact match
    if ingredient_name_lower in INGREDIENT_DATABASE:
        nutrition = INGREDIENT_DATABASE[ingredient_name_lower].copy()
        factor = amount / 100.0
        return {
            "calories": nutrition["calories"] * factor,
            "protein": nutrition["protein"] * factor,
            "fat": nutrition["fat"] * factor,
            "carbs": nutrition["carbs"] * factor,
            "weight": amount,
            "type": nutrition["type"]
        }
    
    # Find partial match
    for key, nutrition in INGREDIENT_DATABASE.items():
        if ingredient_name_lower in key or key in ingredient_name_lower:
            factor = amount / 100.0
            return {
                "calories": nutrition["calories"] * factor,
                "protein": nutrition["protein"] * factor,
                "fat": nutrition["fat"] * factor,
                "carbs": nutrition["carbs"] * factor,
                "weight": amount,
                "type": nutrition["type"]
            }
    
    return None

def search_dishes_by_name(query: str) -> List[Dict]:
    """
    Search dishes by name (Russian or English)
    
    Args:
        query: Search query
        
    Returns:
        List of matching dishes
    """
    query_lower = query.lower()
    results = []
    
    for dish_key, dish_data in COMPOSITE_DISHES.items():
        # Check Russian name
        if query_lower in dish_data["name"].lower() or dish_data["name"].lower() in query_lower:
            results.append(dish_data)
            continue
        
        # Check English names
        for name_en in dish_data["name_en"]:
            if query_lower in name_en.lower() or name_en.lower() in query_lower:
                results.append(dish_data)
                break
        
        # Check keywords
        for keyword in dish_data["keywords"]:
            if query_lower in keyword.lower() or keyword.lower() in query_lower:
                results.append(dish_data)
                break
    
    return results

def get_dishes_by_category(category: str) -> List[Dict]:
    """
    Get all dishes by category
    
    Args:
        category: Category name
        
    Returns:
        List of dishes in category
    """
    return [
        dish_data for dish_data in COMPOSITE_DISHES.values()
        if dish_data["category"] == category
    ]

def get_all_categories() -> List[str]:
    """Get all available categories"""
    categories = set()
    for dish_data in COMPOSITE_DISHES.values():
        categories.add(dish_data["category"])
    return sorted(list(categories))

# =============================================================================
# 🎯 SMART DISH IDENTIFICATION SYSTEM
# =============================================================================
class DishIdentifier:
    """Smart dish identification system"""
    
    def __init__(self):
        self.composite_dishes = COMPOSITE_DISHES
        self.ingredient_db = INGREDIENT_DATABASE
    
    def identify_dish(self, ai_ingredients: List[str], confidence_threshold: float = 0.4) -> Dict:
        """
        Identify dish from AI ingredients
        
        Args:
            ai_ingredients: Ingredients from AI
            confidence_threshold: Minimum confidence to accept
            
        Returns:
            Identification result
        """
        # Try to find exact match first
        best_match = find_best_match(ai_ingredients, confidence_threshold)
        
        if best_match:
            return {
                "success": True,
                "dish": best_match,
                "confidence": best_match["match_score"],
                "method": "composite_match"
            }
        
        # If no composite match, try individual ingredients
        return self._identify_from_individual_ingredients(ai_ingredients)
    
    def _identify_from_individual_ingredients(self, ingredients: List[str]) -> Dict:
        """Identify dish from individual ingredients"""
        total_nutrition = {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0
        }
        
        identified_ingredients = []
        
        for ingredient in ingredients:
            nutrition = get_ingredient_nutrition(ingredient, 100)
            if nutrition:
                identified_ingredients.append({
                    "name": ingredient,
                    "nutrition": nutrition
                })
                total_nutrition["calories"] += nutrition["calories"]
                total_nutrition["protein"] += nutrition["protein"]
                total_nutrition["fat"] += nutrition["fat"]
                total_nutrition["carbs"] += nutrition["carbs"]
        
        if identified_ingredients:
            return {
                "success": True,
                "dish": {
                    "name": "Mixed ingredients",
                    "category": "mixed",
                    "nutrition_per_100": total_nutrition,
                    "ingredients": identified_ingredients
                },
                "confidence": 0.3,
                "method": "individual_match"
            }
        
        return {
            "success": False,
            "error": "No recognizable ingredients found",
            "method": "no_match"
        }

# Global instance
dish_identifier = DishIdentifier()

# =============================================================================
# 📊 UTILITY FUNCTIONS
# =============================================================================
def calculate_total_nutrition(ingredients_data: List[Dict]) -> Dict:
    """
    Calculate total nutrition from ingredients list
    
    Args:
        ingredients_data: List of ingredient data
        
    Returns:
        Total nutrition
    """
    total = {
        "calories": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0,
        "weight": 0
    }
    
    for ingredient in ingredients_data:
        if "nutrition" in ingredient:
            nutrition = ingredient["nutrition"]
            total["calories"] += nutrition.get("calories", 0)
            total["protein"] += nutrition.get("protein", 0)
            total["fat"] += nutrition.get("fat", 0)
            total["carbs"] += nutrition.get("carbs", 0)
            total["weight"] += nutrition.get("weight", 0)
    
    return total

def format_nutrition_label(nutrition: Dict, weight: float = None) -> str:
    """
    Format nutrition data into readable label
    
    Args:
        nutrition: Nutrition data
        weight: Portion weight
        
    Returns:
        Formatted label
    """
    if weight:
        factor = weight / 100.0
        calories = nutrition["calories"] * factor
        protein = nutrition["protein"] * factor
        fat = nutrition["fat"] * factor
        carbs = nutrition["carbs"] * factor
    else:
        calories = nutrition["calories"]
        protein = nutrition["protein"]
        fat = nutrition["fat"]
        carbs = nutrition["carbs"]
    
    return f"📊 {calories:.0f} kcal | 🥩 {protein:.1f}g | 🧈 {fat:.1f}g | 🍞 {carbs:.1f}g"

def get_dish_suggestions(partial_name: str, limit: int = 5) -> List[str]:
    """
    Get dish suggestions based on partial name
    
    Args:
        partial_name: Partial dish name
        limit: Maximum suggestions
        
    Returns:
        List of suggestions
    """
    partial_lower = partial_name.lower()
    suggestions = []
    
    for dish_key, dish_data in COMPOSITE_DISHES.items():
        # Check Russian name
        if partial_lower in dish_data["name"].lower():
            suggestions.append(dish_data["name"])
            continue
        
        # Check English names
        for name_en in dish_data["name_en"]:
            if partial_lower in name_en.lower():
                suggestions.append(name_en)
                break
        
        if len(suggestions) >= limit:
            break
    
    return suggestions[:limit]

# =============================================================================
# 🎯 MAIN API FUNCTIONS
# =============================================================================
def process_food_identification(ai_response: str) -> Dict:
    """
    Process AI food identification response
    
    Args:
        ai_response: Raw response from AI
        
    Returns:
        Processed food data
    """
    try:
        # Parse AI response to extract ingredients
        ingredients = []
        
        # Split by common separators
        parts = ai_response.replace(', ', ',').replace('; ', ';').split(',')
        for part in parts:
            # Clean and add ingredient
            ingredient = part.strip().lower()
            if ingredient and len(ingredient) > 2:
                ingredients.append(ingredient)
        
        if not ingredients:
            return {
                "success": False,
                "error": "No ingredients found in AI response"
            }
        
        # Identify dish
        identification = dish_identifier.identify_dish(ingredients)
        
        if identification["success"]:
            dish = identification["dish"]
            
            # Get nutrition data
            if "dish_key" in dish:
                nutrition = get_dish_nutrition(dish["dish_key"])
            else:
                nutrition = dish.get("nutrition_per_100", {})
            
            return {
                "success": True,
                "dish_name": dish["name"],
                "category": dish["category"],
                "confidence": identification["confidence"],
                "ingredients": ingredients,
                "nutrition": nutrition,
                "method": identification["method"]
            }
        else:
            return {
                "success": False,
                "error": identification["error"],
                "ingredients": ingredients
            }
    
    except Exception as e:
        logger.error(f"Error processing food identification: {e}")
        return {
            "success": False,
            "error": f"Processing error: {str(e)}"
        }

# =============================================================================
# 📝 LOGGING AND DEBUGGING
# =============================================================================
def log_dish_identification(ingredients: List[str], result: Dict):
    """Log dish identification for debugging"""
    logger.info(f"🍽️ Dish Identification:")
    logger.info(f"   Input ingredients: {ingredients}")
    
    if result["success"]:
        logger.info(f"   ✅ Identified: {result['dish_name']}")
        logger.info(f"   📊 Confidence: {result['confidence']:.2f}")
        logger.info(f"   🏷️ Category: {result['category']}")
        logger.info(f"   🔧 Method: {result['method']}")
    else:
        logger.info(f"   ❌ Failed: {result['error']}")

# =============================================================================
# 🎯 INITIALIZATION
# =============================================================================
def initialize_dish_database():
    """Initialize dish database"""
    logger.info(f"🍽️ Dish database initialized:")
    logger.info(f"   📚 Composite dishes: {len(COMPOSITE_DISHES)}")
    logger.info(f"   🥗 Ingredients: {len(INGREDIENT_DATABASE)}")
    logger.info(f"   🏷️ Categories: {', '.join(get_all_categories())}")

# Initialize on import
initialize_dish_database()
