"""
РАСШИРЕННАЯ БАЗА ДАННЫХ ГОТОВЫХ БЛЮД С ПОДДЕРЖКОЙ АНГЛИЙСКИХ НАЗВАНИЙ
✅ 200+ блюд с полными ингредиентами и КБЖУ
✅ Билингвальная поддержка (RU + EN)
✅ Улучшенный поиск с учётом синонимов и keywords
"""
from typing import Dict, List, Optional
import logging
from difflib import SequenceMatcher
from services.translator import AI_TO_DB_MAPPING

logger = logging.getLogger(__name__)

# =============================================================================
# 🍽️ БАЗА ГОТОВЫХ БЛЮД (200+ наименований)
# =============================================================================
COMPOSITE_DISHES = {
    # ==================== ШАШЛЫКИ И ГРИЛЬ ====================
    "шашлык": {
        "name": "Шашлык",
        "name_en": ["shashlik", "shish kebab", "meat skewers", "grilled meat skewers", "kebab", "grilled meat"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 20.0, "fat": 15.0, "carbs": 2.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 70},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "перец болгарский", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ],
        "keywords": ["шашлык", "кебаб", "гриль", "skewer", "kebab", "grilled meat", "meat skewers"]
    },
    "шашлык из курицы": {
        "name": "Шашлык из курицы",
        "name_en": ["chicken shashlik", "chicken skewers", "grilled chicken skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 165, "protein": 22.0, "fat": 8.0, "carbs": 2.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 75},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "специи", "type": "other", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ],
        "keywords": ["шашлык", "курица", "chicken", "skewers", "гриль"]
    },
    "шашлык из говядины": {
        "name": "Шашлык из говядины",
        "name_en": ["beef shashlik", "beef skewers", "grilled beef skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 22.0, "fat": 13.0, "carbs": 2.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 75},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "специи", "type": "other", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ],
        "keywords": ["шашлык", "говядина", "beef", "skewers", "гриль"]
    },
    "шашлык из баранины": {
        "name": "Шашлык из баранины",
        "name_en": ["lamb shashlik", "lamb skewers", "grilled lamb skewers"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 20.0, "fat": 17.0, "carbs": 2.0},
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 75},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "специи", "type": "other", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ],
        "keywords": ["шашлык", "баранина", "lamb", "skewers", "гриль"]
    },
    "курица гриль": {
        "name": "Курица гриль",
        "name_en": ["grilled chicken", "chicken grill", "roast chicken", "bbq chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 185, "protein": 24.0, "fat": 9.5, "carbs": 1.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 95},
            {"name": "специи", "type": "other", "percent": 5}
        ],
        "keywords": ["курица", "гриль", "chicken", "grill", "roast", "bbq"]
    },
    "курица запеченная": {
        "name": "Курица запеченная",
        "name_en": ["baked chicken", "roasted chicken", "oven chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 24.0, "fat": 10.0, "carbs": 1.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 95},
            {"name": "специи", "type": "other", "percent": 2},
            {"name": "масло", "type": "fat", "percent": 3}
        ],
        "keywords": ["курица", "запеченная", "chicken", "baked", "roasted", "oven"]
    },
    "курица жареная": {
        "name": "Курица жареная",
        "name_en": ["fried chicken", "pan-fried chicken"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 23.0, "fat": 14.0, "carbs": 2.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 85},
            {"name": "масло растительное", "type": "fat", "percent": 10},
            {"name": "специи", "type": "other", "percent": 5}
        ],
        "keywords": ["курица", "жареная", "chicken", "fried"]
    },
    # ==================== СУПЫ ====================
    "борщ": {
        "name": "Борщ",
        "name_en": ["borscht", "borsch", "beet soup", "russian soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 60, "protein": 3.0, "fat": 2.5, "carbs": 6.5},
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 15},
            {"name": "капуста", "type": "vegetable", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "мясо", "type": "protein", "percent": 15},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 15}
        ],
        "keywords": ["борщ", "свекла", "borscht", "beet", "soup"]
    },
    "борщ украинский": {
        "name": "Борщ украинский",
        "name_en": ["ukrainian borscht", "ukrainian beet soup"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 75, "protein": 4.0, "fat": 3.0, "carbs": 7.5},
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 15},
            {"name": "капуста", "type": "vegetable", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "свинина", "type": "protein", "percent": 12},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "фасоль", "type": "protein", "percent": 5},
            {"name": "сало", "type": "fat", "percent": 2},
            {"name": "вода", "type": "liquid", "percent": 18}
        ],
        "keywords": ["борщ", "украинский", "ukrainian", "borscht"]
    },
    "щи": {
        "name": "Щи",
        "name_en": ["shchi", "cabbage soup", "russian cabbage soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 2.5, "fat": 1.8, "carbs": 5.0},
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "мясо", "type": "protein", "percent": 12},
            {"name": "томатная паста", "type": "sauce", "percent": 3},
            {"name": "вода", "type": "liquid", "percent": 27}
        ],
        "keywords": ["щи", "капуста", "shchi", "cabbage", "soup"]
    },
    "рассольник": {
        "name": "Рассольник",
        "name_en": ["rassolnik", "pickle soup", "russian pickle soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 55, "protein": 2.8, "fat": 2.2, "carbs": 6.0},
        "ingredients": [
            {"name": "огурцы соленые", "type": "vegetable", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "перловка", "type": "carb", "percent": 10},
            {"name": "мясо", "type": "protein", "percent": 12},
            {"name": "вода", "type": "liquid", "percent": 30}
        ],
        "keywords": ["рассольник", "огурцы", "rassolnik", "pickle", "soup"]
    },
    "солянка": {
        "name": "Солянка мясная",
        "name_en": ["solyanka", "meat solyanka", "russian mixed soup"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 95, "protein": 7.0, "fat": 5.5, "carbs": 4.5},
        "ingredients": [
            {"name": "мясо ассорти", "type": "protein", "percent": 25},
            {"name": "колбаса", "type": "protein", "percent": 10},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "оливки", "type": "vegetable", "percent": 5},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "каперсы", "type": "vegetable", "percent": 2},
            {"name": "вода", "type": "liquid", "percent": 30}
        ],
        "keywords": ["солянка", "мясо", "solyanka", "meat", "soup"]
    },
    "уха": {
        "name": "Уха",
        "name_en": ["ukha", "fish soup", "russian fish soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 4.5, "fat": 1.5, "carbs": 3.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 47}
        ],
        "keywords": ["уха", "рыба", "ukha", "fish", "soup"]
    },
    "куриный суп": {
        "name": "Суп куриный",
        "name_en": ["chicken soup", "chicken noodle soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 3.5, "fat": 1.5, "carbs": 3.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вермишель", "type": "carb", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 47}
        ],
        "keywords": ["суп", "курица", "chicken", "soup"]
    },
    "грибной суп": {
        "name": "Суп грибной",
        "name_en": ["mushroom soup", "cream of mushroom soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 2.0, "fat": 1.8, "carbs": 4.0},
        "ingredients": [
            {"name": "грибы", "type": "vegetable", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 47}
        ],
        "keywords": ["суп", "грибы", "mushroom", "soup"]
    },
    "гороховый суп": {
        "name": "Суп гороховый",
        "name_en": ["pea soup", "split pea soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 70, "protein": 4.5, "fat": 2.0, "carbs": 9.0},
        "ingredients": [
            {"name": "горох", "type": "protein", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "копчености", "type": "protein", "percent": 7},
            {"name": "вода", "type": "liquid", "percent": 40}
        ],
        "keywords": ["суп", "горох", "pea", "soup"]
    },
    # ==================== САЛАТЫ ====================
    "салат цезарь": {
        "name": "Цезарь с курицей",
        "name_en": ["caesar salad", "chicken caesar"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 185, "protein": 15.0, "fat": 12.0, "carbs": 5.5},
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "салат романо", "type": "vegetable", "percent": 35},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "сухарики", "type": "carb", "percent": 10},
            {"name": "соус цезарь", "type": "sauce", "percent": 15}
        ],
        "keywords": ["цезарь", "caesar", "салат", "salad"]
    },
    "греческий салат": {
        "name": "Греческий салат",
        "name_en": ["greek salad", "horiatiki"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 135, "protein": 4.5, "fat": 11.0, "carbs": 4.0},
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 35},
            {"name": "огурцы", "type": "vegetable", "percent": 30},
            {"name": "перец болгарский", "type": "vegetable", "percent": 15},
            {"name": "фета", "type": "dairy", "percent": 15},
            {"name": "оливки", "type": "vegetable", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["греческий", "greek", "фета", "feta", "салат", "salad"]
    },
    "салат оливье": {
        "name": "Оливье",
        "name_en": ["olivier salad", "russian salad", "potato salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 8.0, "fat": 16.0, "carbs": 8.5},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 30},
            {"name": "колбаса вареная", "type": "protein", "percent": 25},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 10},
            {"name": "горошек зеленый", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ],
        "keywords": ["оливье", "olivier", "салат", "salad", "русский"]
    },
    "винегрет": {
        "name": "Винегрет",
        "name_en": ["vinegret", "russian beet salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 90, "protein": 2.0, "fat": 4.5, "carbs": 10.5},
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 20},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 15},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "масло подсолнечное", "type": "fat", "percent": 5}
        ],
        "keywords": ["винегрет", "vinegret", "салат", "salad", "свекла"]
    },
    "селедка под шубой": {
        "name": "Селедка под шубой",
        "name_en": ["herring under fur coat", "russian herring salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 8.0, "fat": 14.0, "carbs": 8.0},
        "ingredients": [
            {"name": "сельдь соленая", "type": "protein", "percent": 20},
            {"name": "свекла", "type": "vegetable", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 5}
        ],
        "keywords": ["шуба", "селедка", "herring", "салат", "salad"]
    },
    # ==================== ВТОРЫЕ БЛЮДА ====================
    "плов": {
        "name": "Плов",
        "name_en": ["pilaf", "pilau", "rice with meat"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 10.0, "carbs": 19.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "баранина", "type": "protein", "percent": 30},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["плов", "рис", "pilaf", "rice", "meat"]
    },
    "котлеты": {
        "name": "Котлеты",
        "name_en": ["cutlets", "meat patties", "meatballs"],
        "category": "main",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 240, "protein": 16.0, "fat": 18.0, "carbs": 6.0},
        "ingredients": [
            {"name": "фарш мясной", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "хлеб", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ],
        "keywords": ["котлеты", "cutlets", "patties", "meatballs", "фарш"]
    },
    "пельмени": {
        "name": "Пельмени",
        "name_en": ["pelmeni", "dumplings", "russian dumplings"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 10.0, "fat": 9.0, "carbs": 22.0},
        "ingredients": [
            {"name": "фарш мясной", "type": "protein", "percent": 40},
            {"name": "тесто", "type": "carb", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["пельмени", "dumplings", "pelmeni"]
    },
    "вареники": {
        "name": "Вареники",
        "name_en": ["vareniki", "dumplings with filling"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 6.0, "fat": 5.0, "carbs": 28.0},
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 60},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["вареники", "vareniki", "dumplings", "картофель"]
    },
    "голубцы": {
        "name": "Голубцы",
        "name_en": ["golubtsy", "cabbage rolls", "stuffed cabbage"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 10.0, "fat": 8.0, "carbs": 10.0},
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 40},
            {"name": "фарш мясной", "type": "protein", "percent": 30},
            {"name": "рис", "type": "carb", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5}
        ],
        "keywords": ["голубцы", "golubtsy", "cabbage", "rolls"]
    },
    "фаршированный перец": {
        "name": "Перец фаршированный",
        "name_en": ["stuffed peppers", "bell peppers with meat"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 140, "protein": 9.0, "fat": 7.0, "carbs": 12.0},
        "ingredients": [
            {"name": "перец болгарский", "type": "vegetable", "percent": 40},
            {"name": "фарш мясной", "type": "protein", "percent": 30},
            {"name": "рис", "type": "carb", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5}
        ],
        "keywords": ["перец", "фаршированный", "stuffed", "peppers"]
    },
    "мясо по-французски": {
        "name": "Мясо по-французски",
        "name_en": ["french meat", "meat french style"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 250, "protein": 16.0, "fat": 18.0, "carbs": 5.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 45},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 15},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ],
        "keywords": ["мясо", "meat", "французски", "french"]
    },
    "гречка с мясом": {
        "name": "Гречка с мясом",
        "name_en": ["buckwheat with meat", "meat with buckwheat"],
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 10.0, "fat": 6.0, "carbs": 16.0},
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 50},
            {"name": "мясо", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["гречка", "мясо", "buckwheat", "meat"]
    },
    # ==================== ПАСТА ====================
    "паста карбонара": {
        "name": "Паста Карбонара",
        "name_en": ["pasta carbonara", "carbonara", "spaghetti carbonara"],
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 280, "protein": 14.0, "fat": 16.0, "carbs": 20.0},
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 45},
            {"name": "бекон", "type": "protein", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "сливки", "type": "dairy", "percent": 10}
        ],
        "keywords": ["карбонара", "carbonara", "паста", "pasta", "спагетти"]
    },
    "паста болоньезе": {
        "name": "Паста Болоньезе",
        "name_en": ["pasta bolognese", "bolognese", "spaghetti bolognese"],
        "category": "pasta",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 40},
            {"name": "фарш мясной", "type": "protein", "percent": 25},
            {"name": "томатный соус", "type": "sauce", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["болоньезе", "bolognese", "паста", "pasta", "фарш"]
    },
    "макароны по-флотски": {
        "name": "Макароны по-флотски",
        "name_en": ["navy-style pasta", "macaroni with minced meat"],
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 10.0, "carbs": 19.0},
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 50},
            {"name": "фарш мясной", "type": "protein", "percent": 35},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["макароны", "флотски", "navy", "pasta", "фарш"]
    },
    # ==================== ЗАВТРАКИ ====================
    "омлет": {
        "name": "Омлет",
        "name_en": ["omelette", "omelet", "scrambled eggs"],
        "category": "breakfast",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 150, "protein": 9.0, "fat": 11.0, "carbs": 2.5},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 60},
            {"name": "молоко", "type": "dairy", "percent": 35},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["омлет", "omelette", "omelet", "яйца", "eggs"]
    },
    "яичница": {
        "name": "Яичница глазунья",
        "name_en": ["fried eggs", "sunny side up", "egg fry"],
        "category": "breakfast",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 190, "protein": 13.0, "fat": 15.0, "carbs": 1.0},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 90},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ],
        "keywords": ["яичница", "яйца", "fried", "eggs", "глазунья"]
    },
    "сырники": {
        "name": "Сырники",
        "name_en": ["syrniki", "cottage cheese pancakes", "quark pancakes"],
        "category": "breakfast",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 210, "protein": 14.0, "fat": 9.0, "carbs": 19.0},
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 70},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["сырники", "syrniki", "творог", "cottage cheese"]
    },
    "каша овсяная": {
        "name": "Овсяная каша",
        "name_en": ["oatmeal", "oat porridge", "oats"],
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 90, "protein": 3.5, "fat": 2.5, "carbs": 14.0},
        "ingredients": [
            {"name": "овсяные хлопья", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5}
        ],
        "keywords": ["овсянка", "каша", "oatmeal", "oats", "porridge"]
    },
    "блины": {
        "name": "Блины",
        "name_en": ["blini", "russian pancakes", "crepes"],
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 6.0, "fat": 8.0, "carbs": 32.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "молоко", "type": "dairy", "percent": 35},
            {"name": "яйцо куриное", "type": "protein", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5}
        ],
        "keywords": ["блины", "blini", "pancakes", "блинчики", "crepes"]
    },
    "драники": {
        "name": "Драники",
        "name_en": ["dranniki", "potato pancakes", "latkes"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 4.0, "fat": 10.0, "carbs": 28.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 70},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "мука", "type": "carb", "percent": 7},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ],
        "keywords": ["драники", "dranniki", "картофель", "оладьи", "potato pancakes"]
    },
    "запеканка творожная": {
        "name": "Запеканка творожная",
        "name_en": ["cottage cheese casserole", "cheesecake bake"],
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 14.0, "fat": 6.0, "carbs": 16.0},
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 60},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "мука", "type": "carb", "percent": 10},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ],
        "keywords": ["запеканка", "творожная", "casserole", "cottage cheese"]
    },
    "бефстроганов": {
        "name": "Бефстроганов",
        "name_en": ["beef stroganoff", "stroganoff"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 230, "protein": 18.0, "fat": 14.0, "carbs": 8.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 50},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "горчица", "type": "sauce", "percent": 5}
        ],
        "keywords": ["бефстроганов", "beef stroganoff", "говядина", "сметана"]
    },
    "гуляш": {
        "name": "Гуляш",
        "name_en": ["goulash", "hungarian goulash"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 15.0, "fat": 10.0, "carbs": 8.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 10},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["гуляш", "goulash", "мясо", "томат"]
    },
    "овощное рагу": {
        "name": "Овощное рагу",
        "name_en": ["vegetable stew", "ratatouille", "mixed vegetables"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 65, "protein": 2.5, "fat": 3.0, "carbs": 8.0},
        "ingredients": [
            {"name": "кабачок", "type": "vegetable", "percent": 25},
            {"name": "баклажан", "type": "vegetable", "percent": 20},
            {"name": "помидор", "type": "vegetable", "percent": 20},
            {"name": "перец болгарский", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["рагу", "овощное", "vegetable stew", "овощи", "тушеные"]
    },
    "плов с курицей": {
        "name": "Плов с курицей",
        "name_en": ["pilaf with chicken", "chicken pilaf"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 12.0, "fat": 7.0, "carbs": 20.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "курица", "type": "protein", "percent": 30},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "масло растительное", "type": "fat", "percent": 7}
        ],
        "keywords": ["плов", "курица", "pilaf", "рис", "мясо"]
    },
    "тефтели": {
        "name": "Тефтели",
        "name_en": ["meatballs", "meatballs in sauce"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 200, "protein": 14.0, "fat": 12.0, "carbs": 10.0},
        "ingredients": [
            {"name": "фарш мясной", "type": "protein", "percent": 50},
            {"name": "рис", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 5},
            {"name": "томатная паста", "type": "sauce", "percent": 10},
            {"name": "мука", "type": "carb", "percent": 5}
        ],
        "keywords": ["тефтели", "meatballs", "котлеты", "фарш"]
    },
    "перец фаршированный": {
        "name": "Перец фаршированный",
        "name_en": ["stuffed peppers", "filled peppers"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 150, "protein": 10.0, "fat": 6.0, "carbs": 14.0},
        "ingredients": [
            {"name": "перец болгарский", "type": "vegetable", "percent": 35},
            {"name": "фарш мясной", "type": "protein", "percent": 30},
            {"name": "рис", "type": "carb", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "томатная паста", "type": "sauce", "percent": 7},
            {"name": "морковь", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["перец", "фаршированный", "stuffed peppers", "голубцы"]
    },
    "лагман": {
        "name": "Лапша лагман",
        "name_en": ["lagman", "uzbek noodles", "hand-pulled noodles"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 160, "protein": 10.0, "fat": 6.0, "carbs": 18.0},
        "ingredients": [
            {"name": "лапша", "type": "carb", "percent": 35},
            {"name": "мясо", "type": "protein", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 12},
            {"name": "перец болгарский", "type": "vegetable", "percent": 10},
            {"name": "помидор", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8}
        ],
        "keywords": ["лагман", "lagman", "лапша", "узбекский", "noodles"]
    },
    "шурпа": {
        "name": "Шурпа",
        "name_en": ["shurpa", "uzbek soup", "meat soup"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 85, "protein": 8.0, "fat": 4.0, "carbs": 6.0},
        "ingredients": [
            {"name": "мясо", "type": "protein", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 12},
            {"name": "помидор", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "перец болгарский", "type": "vegetable", "percent": 8},
            {"name": "вода", "type": "liquid", "percent": 17}
        ],
        "keywords": ["шурпа", "shurpa", "суп", "узбекский", "мясной"]
    },
    "манты": {
        "name": "Манты",
        "name_en": ["manti", "steamed dumplings", "uzbek dumplings"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 200, "protein": 12.0, "fat": 9.0, "carbs": 18.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "мясо", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "масло растительное", "type": "fat", "percent": 5},
            {"name": "яйцо куриное", "type": "protein", "percent": 5}
        ],
        "keywords": ["манты", "manti", "пельмени", "dumplings", "узбекский"]
    },
    "чебуреки": {
        "name": "Чебуреки",
        "name_en": ["cheburek", "fried dough with meat", "crimean pastry"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 280, "protein": 10.0, "fat": 16.0, "carbs": 26.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "мясо", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 12},
            {"name": "масло растительное", "type": "fat", "percent": 13},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["чебуреки", "cheburek", "жареный", "пирожок", "мясо"]
    },
    "беляши": {
        "name": "Беляши",
        "name_en": ["belyashi", "meat pies", "fried buns"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 260, "protein": 11.0, "fat": 14.0, "carbs": 24.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "мясо", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "масло растительное", "type": "fat", "percent": 12},
            {"name": "дрожжи", "type": "other", "percent": 3},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["беляши", "belyashi", "пирожки", "мясо", "жареные"]
    },
    "пирожки печеные": {
        "name": "Пирожки печеные",
        "name_en": ["baked pies", "pirozhki"],
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 6.0, "fat": 8.0, "carbs": 32.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 50},
            {"name": "мясо", "type": "protein", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10},
            {"name": "дрожжи", "type": "other", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["пирожки", "pirozhki", "выпечка", "печеные", "пирог"]
    },
    # ==================== ФАСТФУД ====================
    "гамбургер": {
        "name": "Гамбургер",
        "name_en": ["hamburger", "burger", "cheeseburger"],
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 250, "protein": 12.0, "fat": 10.0, "carbs": 28.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 35},
            {"name": "котлета говяжья", "type": "protein", "percent": 30},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "кетчуп", "type": "sauce", "percent": 5},
            {"name": "горчица", "type": "sauce", "percent": 5}
        ],
        "keywords": ["бургер", "гамбургер", "burger", "hamburger"]
    },
    "пицца маргарита": {
        "name": "Пицца Маргарита",
        "name_en": ["pizza margherita", "margherita pizza", "pizza"],
        "category": "bakery",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 240, "protein": 10.0, "fat": 9.0, "carbs": 30.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 50},
            {"name": "соус томатный", "type": "sauce", "percent": 15},
            {"name": "моцарелла", "type": "dairy", "percent": 25},
            {"name": "помидоры", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["пицца", "pizza", "маргарита", "margherita"]
    },
    "шаурма": {
        "name": "Шаурма с курицей",
        "name_en": ["shawarma", "doner kebab", "gyro"],
        "category": "fastfood",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 10.0, "fat": 7.0, "carbs": 19.0},
        "ingredients": [
            {"name": "лаваш", "type": "carb", "percent": 30},
            {"name": "курица гриль", "type": "protein", "percent": 25},
            {"name": "капуста", "type": "vegetable", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 8},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "чесночный соус", "type": "sauce", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 4}
        ],
        "keywords": ["шаурма", "shawarma", "doner", "kebab", "лаваш"]
    },
    # ==================== АЗИАТСКАЯ КУХНЯ ====================
    "ролл филадельфия": {
        "name": "Ролл Филадельфия",
        "name_en": ["philadelphia roll", "philly roll", "salmon roll"],
        "category": "asian",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 7.0, "fat": 8.0, "carbs": 23.0},
        "ingredients": [
            {"name": "рис для суши", "type": "carb", "percent": 50},
            {"name": "лосось", "type": "protein", "percent": 20},
            {"name": "сливочный сыр", "type": "dairy", "percent": 15},
            {"name": "огурец", "type": "vegetable", "percent": 10},
            {"name": "нори", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["ролл", "суши", "roll", "sushi", "филадельфия", "philadelphia"]
    },
    "суши": {
        "name": "Суши с лососем",
        "name_en": ["sushi", "sushi with salmon", "nigiri"],
        "category": "asian",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 4.0, "carbs": 28.0},
        "ingredients": [
            {"name": "рис для суши", "type": "carb", "percent": 70},
            {"name": "лосось", "type": "protein", "percent": 25},
            {"name": "нори", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["суши", "sushi", "ролл", "лосось", "salmon"]
    },
    "рамен": {
        "name": "Рамен с курицей",
        "name_en": ["ramen", "chicken ramen", "japanese noodle soup"],
        "category": "asian",
        "default_weight": 500,
        "nutrition_per_100": {"calories": 90, "protein": 5.0, "fat": 3.0, "carbs": 11.0},
        "ingredients": [
            {"name": "лапша рамен", "type": "carb", "percent": 30},
            {"name": "бульон куриный", "type": "liquid", "percent": 50},
            {"name": "курица", "type": "protein", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 3},
            {"name": "шпинат", "type": "vegetable", "percent": 3},
            {"name": "лук зеленый", "type": "vegetable", "percent": 2},
            {"name": "нори", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["рамен", "ramen", "лапша", "noodle", "суп"]
    },
    # ==================== ГАРНИРЫ ====================
    "картофельное пюре": {
        "name": "Картофельное пюре",
        "name_en": ["mashed potatoes", "potato puree"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 105, "protein": 2.5, "fat": 3.5, "carbs": 16.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 80},
            {"name": "молоко", "type": "dairy", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["пюре", "картофель", "mashed", "potatoes", "puree"]
    },
    "рис отварной": {
        "name": "Рис отварной",
        "name_en": ["boiled rice", "white rice", "steamed rice"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 130, "protein": 2.5, "fat": 0.5, "carbs": 29.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 100}
        ],
        "keywords": ["рис", "rice", "отварной", "boiled", "steamed"]
    },
    "гречка отварная": {
        "name": "Гречка отварная",
        "name_en": ["buckwheat", "buckwheat porridge", "kasha"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 110, "protein": 4.0, "fat": 1.0, "carbs": 21.0},
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 100}
        ],
        "keywords": ["гречка", "гречневая", "buckwheat", "kasha", "каша"]
    },
    "картофель жареный": {
        "name": "Картофель жареный",
        "name_en": ["fried potatoes", "home fries", "pan-fried potatoes"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 190, "protein": 3.0, "fat": 9.0, "carbs": 24.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 85},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ],
        "keywords": ["картофель", "жареный", "fried", "potatoes"]
    },
    "картофель фри": {
        "name": "Картофель фри",
        "name_en": ["french fries", "fries", "chips"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 290, "protein": 3.5, "fat": 15.0, "carbs": 34.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 70},
            {"name": "масло растительное", "type": "fat", "percent": 30}
        ],
        "keywords": ["фри", "fries", "картофель", "potatoes", "chips"]
    },

        # ==================== ГРУЗИНСКАЯ КУХНЯ ====================
    "хачапури по-аджарски": {
        "name": "Хачапури по-аджарски",
        "name_en": ["Adjarian khachapuri", "Georgian cheese bread boat"],
        "category": "bakery",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 280, "protein": 10.0, "fat": 14.0, "carbs": 28.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 50},
            {"name": "сыр сулугуни", "type": "dairy", "percent": 30},
            {"name": "яйцо куриное", "type": "protein", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ],
        "keywords": ["хачапури", "khachapuri", "грузинский", "сыр", "лодочка"]
    },
    "хачапури по-имеретински": {
        "name": "Хачапури по-имеретински",
        "name_en": ["Imeretian khachapuri", "Georgian cheese flatbread"],
        "category": "bakery",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 260, "protein": 9.0, "fat": 11.0, "carbs": 31.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 55},
            {"name": "сыр имеретинский", "type": "dairy", "percent": 40},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["хачапури", "имеретинский", "сырная лепешка"]
    },
    "хинкали": {
        "name": "Хинкали",
        "name_en": ["khinkali", "Georgian dumplings"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 45},
            {"name": "говядина", "type": "protein", "percent": 30},
            {"name": "свинина", "type": "protein", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "бульон", "type": "liquid", "percent": 5}
        ],
        "keywords": ["хинкали", "khinkali", "грузинские пельмени"]
    },
    "хинкали с бараниной": {
        "name": "Хинкали с бараниной",
        "name_en": ["lamb khinkali", "Georgian lamb dumplings"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 230, "protein": 13.0, "fat": 12.0, "carbs": 20.0},
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 45},
            {"name": "баранина", "type": "protein", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "кинза", "type": "vegetable", "percent": 2},
            {"name": "бульон", "type": "liquid", "percent": 5}
        ],
        "keywords": ["хинкали", "khinkali", "баранина", "lamb"]
    },
    "чахохбили": {
        "name": "Чахохбили",
        "name_en": ["chakhokhbili", "Georgian chicken stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 140, "protein": 15.0, "fat": 7.0, "carbs": 5.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 45},
            {"name": "помидоры", "type": "vegetable", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "перец", "type": "vegetable", "percent": 8},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "кинза", "type": "vegetable", "percent": 4}
        ],
        "keywords": ["чахохбили", "chakhokhbili", "грузинский", "курица"]
    },
    "оджакхури": {
        "name": "Оджакхури",
        "name_en": ["ojakhuri", "Georgian pork and potatoes"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 200, "protein": 12.0, "fat": 12.0, "carbs": 12.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 35},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "перец", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["оджакхури", "ojakhuri", "грузинский", "свинина с картошкой"]
    },
    "лобио": {
        "name": "Лобио",
        "name_en": ["lobio", "Georgian bean stew"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 6.0, "fat": 4.0, "carbs": 15.0},
        "ingredients": [
            {"name": "фасоль красная", "type": "protein", "percent": 60},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "грецкие орехи", "type": "protein", "percent": 10},
            {"name": "кинза", "type": "vegetable", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["лобио", "lobio", "грузинский", "фасоль"]
    },
    "пхали": {
        "name": "Пхали из шпината",
        "name_en": ["phali", "Georgian spinach pate"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 5.0, "fat": 10.0, "carbs": 7.0},
        "ingredients": [
            {"name": "шпинат", "type": "vegetable", "percent": 50},
            {"name": "грецкие орехи", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "кинза", "type": "vegetable", "percent": 5},
            {"name": "гранатовые зерна", "type": "fruit", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["пхали", "phali", "грузинская закуска", "шпинат"]
    },
    "сациви": {
        "name": "Сациви",
        "name_en": ["satsivi", "Georgian chicken in walnut sauce"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 250, "protein": 15.0, "fat": 19.0, "carbs": 6.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 40},
            {"name": "грецкие орехи", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5},
            {"name": "уксус", "type": "other", "percent": 5},
            {"name": "бульон", "type": "liquid", "percent": 5}
        ],
        "keywords": ["сациви", "satsivi", "грузинский", "ореховый соус"]
    },
    "чакапули": {
        "name": "Чакапули",
        "name_en": ["chakapuli", "Georgian lamb stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 14.0, "fat": 10.0, "carbs": 6.0},
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 40},
            {"name": "щавель", "type": "vegetable", "percent": 15},
            {"name": "эстрагон", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "белое вино", "type": "liquid", "percent": 15},
            {"name": "зелень", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["чакапули", "chakapuli", "грузинский", "баранина"]
    },
    "купаты": {
        "name": "Купаты",
        "name_en": ["kupaty", "Georgian sausages", "grilled sausages"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 270, "protein": 15.0, "fat": 22.0, "carbs": 3.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 70},
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["купаты", "kupaty", "грузинские колбаски"]
    },
    "аджапсандали": {
        "name": "Аджапсандали",
        "name_en": ["ajapsandali", "Georgian vegetable stew"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 70, "protein": 2.0, "fat": 3.0, "carbs": 9.0},
        "ingredients": [
            {"name": "баклажаны", "type": "vegetable", "percent": 30},
            {"name": "перец", "type": "vegetable", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "кинза", "type": "vegetable", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ],
        "keywords": ["аджапсандали", "ajapsandali", "грузинское овощное рагу"]
    },
    "чанахи": {
        "name": "Чанахи",
        "name_en": ["chanakhi", "Georgian lamb and vegetables"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 150, "protein": 9.0, "fat": 8.0, "carbs": 11.0},
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "баклажаны", "type": "vegetable", "percent": 15},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "зелень", "type": "vegetable", "percent": 7},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["чанахи", "chanakhi", "грузинское рагу"]
    },

    # ==================== ВЕНГЕРСКАЯ КУХНЯ ====================
    "гуляш": {
        "name": "Гуляш",
        "name_en": ["goulash", "hungarian goulash", "beef stew"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 110, "protein": 9.0, "fat": 5.0, "carbs": 7.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "перец", "type": "vegetable", "percent": 8},
            {"name": "паприка", "type": "spice", "percent": 5},
            {"name": "вода/бульон", "type": "liquid", "percent": 12}
        ],
        "keywords": ["гуляш", "goulash", "венгерский суп"]
    },
    "перкельт": {
        "name": "Перкельт",
        "name_en": ["pörkölt", "hungarian meat stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 18.0, "fat": 12.0, "carbs": 4.0},
        "ingredients": [
            {"name": "свинина/говядина", "type": "protein", "percent": 60},
            {"name": "лук", "type": "vegetable", "percent": 20},
            {"name": "паприка", "type": "spice", "percent": 8},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 7}
        ],
        "keywords": ["перкельт", "pörkölt", "венгерское рагу"]
    },
    "паприкаш": {
        "name": "Паприкаш",
        "name_en": ["paprikash", "hungarian chicken in paprika sauce"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 160, "protein": 15.0, "fat": 9.0, "carbs": 6.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 45},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "паприка", "type": "spice", "percent": 8},
            {"name": "перец", "type": "vegetable", "percent": 7},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["паприкаш", "paprikash", "венгерский", "курица в сметане"]
    },
    "лечо": {
        "name": "Лечо",
        "name_en": ["lecho", "hungarian pepper stew"],
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 1.5, "fat": 2.0, "carbs": 6.5},
        "ingredients": [
            {"name": "перец", "type": "vegetable", "percent": 50},
            {"name": "помидоры", "type": "vegetable", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "паприка", "type": "spice", "percent": 3},
            {"name": "масло", "type": "fat", "percent": 2}
        ],
        "keywords": ["лечо", "lecho", "венгерский"]
    },
    "токани": {
        "name": "Токани",
        "name_en": ["tokány", "hungarian beef strips"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 17.0, "fat": 11.0, "carbs": 5.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 55},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "грибы", "type": "vegetable", "percent": 10},
            {"name": "перец", "type": "vegetable", "percent": 8},
            {"name": "сметана", "type": "dairy", "percent": 7},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["токани", "tokány", "венгерское мясо"]
    },

    # ==================== БАЛКАНСКАЯ КУХНЯ ====================
    "чевапчичи": {
        "name": "Чевапчичи",
        "name_en": ["ćevapi", "chevapchichi", "balkan sausages"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 16.0, "fat": 19.0, "carbs": 2.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 50},
            {"name": "баранина", "type": "protein", "percent": 25},
            {"name": "свинина", "type": "protein", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["чевапчичи", "ćevapi", "балканские колбаски"]
    },
    "плескавица": {
        "name": "Плескавица",
        "name_en": ["pljeskavica", "balkan burger"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 230, "protein": 15.0, "fat": 17.0, "carbs": 4.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 60},
            {"name": "свинина", "type": "protein", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "специи", "type": "spice", "percent": 2},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["плескавица", "pljeskavica", "балканская котлета"]
    },
    "шопский салат": {
        "name": "Шопский салат",
        "name_en": ["shopska salad", "bulgarian salad"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 85, "protein": 2.5, "fat": 6.0, "carbs": 5.0},
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 30},
            {"name": "огурцы", "type": "vegetable", "percent": 25},
            {"name": "перец", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "сыр сирене", "type": "dairy", "percent": 12},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ],
        "keywords": ["шопский салат", "shopska", "болгарский"]
    },
    "мусака": {
        "name": "Мусака по-балкански",
        "name_en": ["moussaka", "balkan moussaka"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 8.0, "carbs": 12.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 35},
            {"name": "свиной фарш", "type": "protein", "percent": 25},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "йогурт", "type": "dairy", "percent": 7},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["мусака", "moussaka", "балканская запеканка"]
    },
    "сарма": {
        "name": "Сарма",
        "name_en": ["sarma", "stuffed cabbage rolls"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 7.0, "carbs": 13.0},
        "ingredients": [
            {"name": "капуста квашеная", "type": "vegetable", "percent": 40},
            {"name": "свиной фарш", "type": "protein", "percent": 30},
            {"name": "рис", "type": "carb", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "копчености", "type": "protein", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["сарма", "sarma", "голубцы", "балканские"]
    },
    "айвар": {
        "name": "Айвар",
        "name_en": ["ajvar", "balkan pepper spread"],
        "category": "sauce",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 70, "protein": 1.5, "fat": 4.0, "carbs": 7.0},
        "ingredients": [
            {"name": "красный перец", "type": "vegetable", "percent": 75},
            {"name": "баклажаны", "type": "vegetable", "percent": 15},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "масло", "type": "fat", "percent": 5},
            {"name": "уксус", "type": "other", "percent": 2}
        ],
        "keywords": ["айвар", "ajvar", "балканский соус"]
    },
    "каймак": {
        "name": "Каймак",
        "name_en": ["kajmak", "balkan clotted cream"],
        "category": "dairy",
        "default_weight": 80,
        "nutrition_per_100": {"calories": 400, "protein": 5.0, "fat": 40.0, "carbs": 2.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 95},
            {"name": "соль", "type": "other", "percent": 5}
        ],
        "keywords": ["каймак", "kajmak", "балканский сыр"]
    },
    "бурек": {
        "name": "Бурек",
        "name_en": ["burek", "balkan pie"],
        "category": "bakery",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 280, "protein": 9.0, "fat": 15.0, "carbs": 27.0},
        "ingredients": [
            {"name": "тесто фило", "type": "carb", "percent": 50},
            {"name": "фарш мясной", "type": "protein", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 15}
        ],
        "keywords": ["бурек", "burek", "балканский пирог"]
    },
    "бурек с сыром": {
        "name": "Бурек с сыром",
        "name_en": ["cheese burek", "balkan cheese pie"],
        "category": "bakery",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 270, "protein": 10.0, "fat": 14.0, "carbs": 26.0},
        "ingredients": [
            {"name": "тесто фило", "type": "carb", "percent": 50},
            {"name": "брынза", "type": "dairy", "percent": 30},
            {"name": "творог", "type": "dairy", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["бурек", "burek", "сырный пирог"]
    },
    "погача": {
        "name": "Погача",
        "name_en": ["pogača", "balkan bread"],
        "category": "bakery",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 260, "protein": 8.0, "fat": 5.0, "carbs": 45.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 70},
            {"name": "вода", "type": "liquid", "percent": 20},
            {"name": "масло", "type": "fat", "percent": 5},
            {"name": "дрожжи", "type": "other", "percent": 3},
            {"name": "соль", "type": "other", "percent": 2}
        ],
        "keywords": ["погача", "pogača", "балканский хлеб"]
    },

    # ==================== СКАНДИНАВСКАЯ КУХНЯ ====================
    "шведские фрикадельки": {
        "name": "Шведские фрикадельки",
        "name_en": ["swedish meatballs", "köttbullar"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 250, "protein": 14.0, "fat": 18.0, "carbs": 8.0},
        "ingredients": [
            {"name": "свиной фарш", "type": "protein", "percent": 40},
            {"name": "говяжий фарш", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "хлебные крошки", "type": "carb", "percent": 8},
            {"name": "молоко", "type": "dairy", "percent": 7},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ],
        "keywords": ["шведские фрикадельки", "swedish meatballs", "köttbullar"]
    },
    "гравлакс": {
        "name": "Гравлакс",
        "name_en": ["gravlax", "cured salmon"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 22.0, "fat": 10.0, "carbs": 1.0},
        "ingredients": [
            {"name": "лосось", "type": "protein", "percent": 85},
            {"name": "соль", "type": "other", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "укроп", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["гравлакс", "gravlax", "скандинавский", "лосось"]
    },
    "смёрребрёд": {
        "name": "Смёрребрёд",
        "name_en": ["smørrebrød", "danish open sandwich"],
        "category": "sandwich",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 9.0, "carbs": 17.0},
        "ingredients": [
            {"name": "ржаной хлеб", "type": "carb", "percent": 40},
            {"name": "сельдь", "type": "protein", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "редис", "type": "vegetable", "percent": 7},
            {"name": "укроп", "type": "vegetable", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 10}
        ],
        "keywords": ["смёрребрёд", "smørrebrød", "датский бутерброд"]
    },
    "растение": {
        "name": "Растение (жаркое из мяса с картофелем)",
        "name_en": ["rastenie", "danish meatloaf with potatoes"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 160, "protein": 10.0, "fat": 7.0, "carbs": 14.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 35},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "бекон", "type": "protein", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["растение", "rastenie", "датское жаркое"]
    },
    "клёцки с печенью": {
        "name": "Клёцки с печенью",
        "name_en": ["leverpostej", "danish liver pate"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 260, "protein": 12.0, "fat": 21.0, "carbs": 6.0},
        "ingredients": [
            {"name": "свиная печень", "type": "protein", "percent": 50},
            {"name": "сало", "type": "fat", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "мука", "type": "carb", "percent": 7}
        ],
        "keywords": ["leverpostej", "датский", "паштет"]
    },
    "фрикадельки с капустой": {
        "name": "Фрикадельки с капустой",
        "name_en": ["frikadeller med rødkål", "danish meatballs with red cabbage"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 11.0, "fat": 9.0, "carbs": 12.0},
        "ingredients": [
            {"name": "свиной фарш", "type": "protein", "percent": 35},
            {"name": "краснокочанная капуста", "type": "vegetable", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "яблоки", "type": "fruit", "percent": 8},
            {"name": "уксус", "type": "other", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 2}
        ],
        "keywords": ["frikadeller", "датские фрикадельки", "краснокочанная капуста"]
    },
    "норвежский лосось": {
        "name": "Запеченный лосось",
        "name_en": ["baked salmon", "norwegian salmon"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 22.0, "fat": 12.0, "carbs": 1.0},
        "ingredients": [
            {"name": "лосось", "type": "protein", "percent": 85},
            {"name": "лимон", "type": "fruit", "percent": 5},
            {"name": "укроп", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["лосось", "salmon", "норвежский"]
    },
    "молле с картофелем": {
        "name": "Молле (картофельное пюре с рыбой)",
        "name_en": ["mølle", "norwegian fish and potato mash"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 130, "protein": 8.0, "fat": 5.0, "carbs": 13.0},
        "ingredients": [
            {"name": "треска", "type": "protein", "percent": 35},
            {"name": "картофель", "type": "carb", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "сливочное масло", "type": "fat", "percent": 5},
            {"name": "молоко", "type": "dairy", "percent": 5}
        ],
        "keywords": ["mølle", "норвежский", "треска"]
    },
    "копченая колбаса": {
        "name": "Копченая колбаса",
        "name_en": ["rakfisk", "norwegian fermented fish"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 20.0, "fat": 10.0, "carbs": 1.0},
        "ingredients": [
            {"name": "форель", "type": "protein", "percent": 90},
            {"name": "соль", "type": "other", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 2}
        ],
        "keywords": ["rakfisk", "норвежская", "ферментированная рыба"]
    },
    "пииропуу": {
        "name": "Пииропуу (карельский пирог)",
        "name_en": ["karjalanpiirakka", "finnish carelian pie"],
        "category": "bakery",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 210, "protein": 5.0, "fat": 6.0, "carbs": 34.0},
        "ingredients": [
            {"name": "ржаная мука", "type": "carb", "percent": 45},
            {"name": "рис", "type": "carb", "percent": 35},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "молоко", "type": "dairy", "percent": 5}
        ],
        "keywords": ["карельский пирог", "karjalanpiirakka", "финский"]
    },
    "калакукко": {
        "name": "Калакукко (рыбный пирог)",
        "name_en": ["kalakukko", "finnish fish pie"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 12.0, "fat": 7.0, "carbs": 17.0},
        "ingredients": [
            {"name": "ржаное тесто", "type": "carb", "percent": 45},
            {"name": "рыба", "type": "protein", "percent": 35},
            {"name": "бекон", "type": "protein", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["kalakukko", "финский", "рыбный пирог"]
    },
    "лосось по-фински": {
        "name": "Лосось по-фински",
        "name_en": ["lohipyörykät", "finnish salmon balls"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 12.0, "carbs": 5.0},
        "ingredients": [
            {"name": "лосось", "type": "protein", "percent": 60},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сливки", "type": "dairy", "percent": 5}
        ],
        "keywords": ["lohipyörykät", "финские рыбные котлеты"]
    },

    # ==================== БЛИЖНЕВОСТОЧНАЯ КУХНЯ ====================
    "хумус": {
        "name": "Хумус",
        "name_en": ["hummus", "chickpea dip"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 200, "protein": 6.0, "fat": 12.0, "carbs": 17.0},
        "ingredients": [
            {"name": "нут", "type": "protein", "percent": 50},
            {"name": "тахини", "type": "sauce", "percent": 15},
            {"name": "оливковое масло", "type": "fat", "percent": 15},
            {"name": "лимонный сок", "type": "fruit", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["хумус", "hummus", "израильский"]
    },
    "баба гануш": {
        "name": "Баба гануш",
        "name_en": ["baba ganoush", "eggplant dip"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 2.0, "fat": 10.0, "carbs": 10.0},
        "ingredients": [
            {"name": "баклажан", "type": "vegetable", "percent": 65},
            {"name": "тахини", "type": "sauce", "percent": 15},
            {"name": "оливковое масло", "type": "fat", "percent": 10},
            {"name": "лимонный сок", "type": "fruit", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "петрушка", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["баба гануш", "baba ganoush", "баклажанная икра"]
    },
    "фалафель": {
        "name": "Фалафель",
        "name_en": ["falafel"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 8.0, "fat": 12.0, "carbs": 20.0},
        "ingredients": [
            {"name": "нут", "type": "protein", "percent": 70},
            {"name": "петрушка", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "кумин", "type": "spice", "percent": 2},
            {"name": "кориандр", "type": "spice", "percent": 2},
            {"name": "масло для фритюра", "type": "fat", "percent": 10}
        ],
        "keywords": ["фалафель", "falafel"]
    },
    "шакшука": {
        "name": "Шакшука",
        "name_en": ["shakshuka"],
        "category": "breakfast",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 100, "protein": 5.0, "fat": 6.0, "carbs": 6.0},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 40},
            {"name": "перец", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "паприка", "type": "spice", "percent": 2},
            {"name": "оливковое масло", "type": "fat", "percent": 7}
        ],
        "keywords": ["шакшука", "shakshuka"]
    },
    "табуле": {
        "name": "Табуле",
        "name_en": ["tabbouleh", "bulgur salad"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 3.0, "fat": 5.0, "carbs": 16.0},
        "ingredients": [
            {"name": "булгур", "type": "carb", "percent": 35},
            {"name": "петрушка", "type": "vegetable", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "мята", "type": "vegetable", "percent": 8},
            {"name": "лук зеленый", "type": "vegetable", "percent": 5},
            {"name": "лимонный сок", "type": "fruit", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 2}
        ],
        "keywords": ["табуле", "tabbouleh", "ближневосточный салат"]
    },
    "киббе": {
        "name": "Киббе",
        "name_en": ["kibbeh", "middle eastern meatballs"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 12.0, "fat": 13.0, "carbs": 15.0},
        "ingredients": [
            {"name": "булгур", "type": "carb", "percent": 40},
            {"name": "баранина", "type": "protein", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "орехи", "type": "protein", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["киббе", "kibbeh", "ливанский"]
    },
    "ламаджун": {
        "name": "Ламаджун",
        "name_en": ["lahmacun", "armenian pizza", "turkish pizza"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 210, "protein": 9.0, "fat": 8.0, "carbs": 26.0},
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 50},
            {"name": "бараний фарш", "type": "protein", "percent": 25},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "перец", "type": "vegetable", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "петрушка", "type": "vegetable", "percent": 3},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["ламаджун", "lahmacun", "турецкая пицца"]
    },
    "пахлава": {
        "name": "Пахлава",
        "name_en": ["baklava"],
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 450, "protein": 5.0, "fat": 25.0, "carbs": 50.0},
        "ingredients": [
            {"name": "тесто фило", "type": "carb", "percent": 40},
            {"name": "грецкие орехи", "type": "protein", "percent": 25},
            {"name": "сахарный сироп", "type": "sugar", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "корица", "type": "spice", "percent": 5}
        ],
        "keywords": ["пахлава", "baklava"]
    },
    "канафе": {
        "name": "Канафе",
        "name_en": ["knafeh", "middle eastern cheese pastry"],
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 350, "protein": 8.0, "fat": 18.0, "carbs": 40.0},
        "ingredients": [
            {"name": "тесто катаифи", "type": "carb", "percent": 45},
            {"name": "сыр", "type": "dairy", "percent": 30},
            {"name": "сахарный сироп", "type": "sugar", "percent": 15},
            {"name": "фисташки", "type": "protein", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["канафе", "knafeh", "арабский десерт"]
    },
    "феттуш": {
        "name": "Феттуш",
        "name_en": ["fattoush", "levantine bread salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 110, "protein": 3.0, "fat": 6.0, "carbs": 11.0},
        "ingredients": [
            {"name": "питта", "type": "carb", "percent": 25},
            {"name": "помидоры", "type": "vegetable", "percent": 25},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "редис", "type": "vegetable", "percent": 10},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "мята", "type": "vegetable", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5},
            {"name": "сумах", "type": "spice", "percent": 5}
        ],
        "keywords": ["феттуш", "fattoush", "ливанский салат"]
    },

    # ==================== АФРИКАНСКАЯ КУХНЯ ====================
    "тажин": {
        "name": "Тажин",
        "name_en": ["tagine", "moroccan tagine"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 180, "protein": 12.0, "fat": 10.0, "carbs": 10.0},
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 35},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "тыква", "type": "vegetable", "percent": 10},
            {"name": "нут", "type": "protein", "percent": 10},
            {"name": "чернослив", "type": "fruit", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "миндаль", "type": "protein", "percent": 4},
            {"name": "специи", "type": "spice", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["тажин", "tagine", "марокканский"]
    },
    "кускус": {
        "name": "Кускус",
        "name_en": ["couscous"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 140, "protein": 5.0, "fat": 4.0, "carbs": 21.0},
        "ingredients": [
            {"name": "кускус", "type": "carb", "percent": 45},
            {"name": "баранина", "type": "protein", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "кабачок", "type": "vegetable", "percent": 8},
            {"name": "нут", "type": "protein", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "изюм", "type": "fruit", "percent": 3},
            {"name": "масло", "type": "fat", "percent": 4}
        ],
        "keywords": ["кускус", "couscous"]
    },
    "харира": {
        "name": "Харира",
        "name_en": ["harira", "moroccan soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 70, "protein": 4.0, "fat": 2.0, "carbs": 9.0},
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 15},
            {"name": "нут", "type": "protein", "percent": 10},
            {"name": "чечевица", "type": "protein", "percent": 8},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сельдерей", "type": "vegetable", "percent": 5},
            {"name": "мука", "type": "carb", "percent": 3},
            {"name": "специи", "type": "spice", "percent": 2},
            {"name": "вода", "type": "liquid", "percent": 37}
        ],
        "keywords": ["харира", "harira"]
    },
    "пастилья": {
        "name": "Пастилья",
        "name_en": ["pastilla", "moroccan pie"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 240, "protein": 12.0, "fat": 12.0, "carbs": 21.0},
        "ingredients": [
            {"name": "тесто варка", "type": "carb", "percent": 35},
            {"name": "курица", "type": "protein", "percent": 25},
            {"name": "миндаль", "type": "protein", "percent": 12},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "сахарная пудра", "type": "carb", "percent": 5},
            {"name": "корица", "type": "spice", "percent": 2},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["пастилья", "pastilla", "b'stilla"]
    },
    "фул медамес": {
        "name": "Фул медамес",
        "name_en": ["ful medames", "egyptian fava beans"],
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 7.0, "fat": 4.0, "carbs": 14.0},
        "ingredients": [
            {"name": "фасоль фава", "type": "protein", "percent": 60},
            {"name": "оливковое масло", "type": "fat", "percent": 10},
            {"name": "лимонный сок", "type": "fruit", "percent": 8},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "тмин", "type": "spice", "percent": 2},
            {"name": "петрушка", "type": "vegetable", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["фул", "ful medames", "египетский завтрак"]
    },
    "кошари": {
        "name": "Кошари",
        "name_en": ["koshari", "egyptian street food"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 160, "protein": 6.0, "fat": 4.0, "carbs": 26.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 30},
            {"name": "макароны", "type": "carb", "percent": 20},
            {"name": "чечевица", "type": "protein", "percent": 20},
            {"name": "нут", "type": "protein", "percent": 8},
            {"name": "томатный соус", "type": "sauce", "percent": 12},
            {"name": "лук жареный", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["кошари", "koshari", "египетский"]
    },
    "мохинга": {
        "name": "Мохинга",
        "name_en": ["mohinga", "burmese fish soup"],
        "category": "soup",
        "default_weight": 450,
        "nutrition_per_100": {"calories": 70, "protein": 5.0, "fat": 2.0, "carbs": 8.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 15},
            {"name": "рисовая лапша", "type": "carb", "percent": 25},
            {"name": "бульон", "type": "liquid", "percent": 45},
            {"name": "банан", "type": "fruit", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "имбирь", "type": "spice", "percent": 3},
            {"name": "куркума", "type": "spice", "percent": 2}
        ],
        "keywords": ["мохинга", "mohinga", "бирманский суп"]
    },
    "адобо": {
        "name": "Адобо",
        "name_en": ["adobo", "filipino chicken adobo"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 18.0, "fat": 13.0, "carbs": 6.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 50},
            {"name": "соевый соус", "type": "sauce", "percent": 15},
            {"name": "уксус", "type": "other", "percent": 15},
            {"name": "чеснок", "type": "vegetable", "percent": 8},
            {"name": "лавровый лист", "type": "spice", "percent": 2},
            {"name": "перец", "type": "spice", "percent": 2},
            {"name": "масло", "type": "fat", "percent": 8}
        ],
        "keywords": ["adobo", "филиппинский"]
    },
    "ясса": {
        "name": "Ясса",
        "name_en": ["yassa", "senegalese chicken"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 16.0, "fat": 9.0, "carbs": 7.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 30},
            {"name": "лимон", "type": "fruit", "percent": 10},
            {"name": "горчица", "type": "sauce", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5},
            {"name": "перец чили", "type": "vegetable", "percent": 3},
            {"name": "оливки", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["yassa", "senegalese", "chicken"]
    },
    "н'доле": {
        "name": "Н'доле",
        "name_en": ["ndole", "cameroonian bitter leaf stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 12.0, "fat": 11.0, "carbs": 9.0},
        "ingredients": [
            {"name": "арахис", "type": "protein", "percent": 30},
            {"name": "горькие листья", "type": "vegetable", "percent": 30},
            {"name": "говядина", "type": "protein", "percent": 20},
            {"name": "креветки", "type": "protein", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 7},
            {"name": "пальмовое масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["ndole", "cameroonian", "cameroon"]
    },
    "эгуси": {
        "name": "Эгуси",
        "name_en": ["egusi soup", "nigerian melon seed soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 10.0, "fat": 15.0, "carbs": 8.0},
        "ingredients": [
            {"name": "тыквенные семечки", "type": "protein", "percent": 35},
            {"name": "шпинат", "type": "vegetable", "percent": 25},
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "рыба", "type": "protein", "percent": 10},
            {"name": "пальмовое масло", "type": "fat", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["egusi", "nigerian", "soup"]
    },
    "джоллоф райс": {
        "name": "Джоллоф райс",
        "name_en": ["jollof rice", "west african rice"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 150, "protein": 5.0, "fat": 4.0, "carbs": 24.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 55},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "перец", "type": "vegetable", "percent": 8},
            {"name": "курица", "type": "protein", "percent": 7},
            {"name": "томатная паста", "type": "sauce", "percent": 5}
        ],
        "keywords": ["jollof", "jollof rice", "west african"]
    },
    "фуфу": {
        "name": "Фуфу",
        "name_en": ["fufu", "west african dough"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 2.0, "fat": 1.0, "carbs": 30.0},
        "ingredients": [
            {"name": "маниока", "type": "carb", "percent": 60},
            {"name": "плантан", "type": "carb", "percent": 40}
        ],
        "keywords": ["fufu", "west african"]
    },

    # ==================== СЕВЕРОАМЕРИКАНСКАЯ КУХНЯ ====================
    "путин": {
        "name": "Путин",
        "name_en": ["poutine", "canadian poutine"],
        "category": "fastfood",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 230, "protein": 6.0, "fat": 14.0, "carbs": 20.0},
        "ingredients": [
            {"name": "картофель фри", "type": "carb", "percent": 60},
            {"name": "сырные творожки", "type": "dairy", "percent": 20},
            {"name": "соус", "type": "sauce", "percent": 20}
        ],
        "keywords": ["путин", "poutine", "канадский"]
    },
    "кэжуал": {
        "name": "Кэжуал (мясной рулет)",
        "name_en": ["casual", "canadian meat roll"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 16.0, "fat": 17.0, "carbs": 6.0},
        "ingredients": [
            {"name": "свиной фарш", "type": "protein", "percent": 60},
            {"name": "говяжий фарш", "type": "protein", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "хлебные крошки", "type": "carb", "percent": 7},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ],
        "keywords": ["casual", "canadian meatloaf"]
    },
    "кукурузный хлеб": {
        "name": "Кукурузный хлеб",
        "name_en": ["cornbread", "american cornbread"],
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 260, "protein": 5.0, "fat": 8.0, "carbs": 42.0},
        "ingredients": [
            {"name": "кукурузная мука", "type": "carb", "percent": 60},
            {"name": "мука пшеничная", "type": "carb", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "молоко", "type": "dairy", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 2}
        ],
        "keywords": ["cornbread", "american bread"]
    },
    "клюквенный соус": {
        "name": "Клюквенный соус",
        "name_en": ["cranberry sauce", "american sauce"],
        "category": "sauce",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 150, "protein": 0.5, "fat": 0.1, "carbs": 37.0},
        "ingredients": [
            {"name": "клюква", "type": "fruit", "percent": 60},
            {"name": "сахар", "type": "carb", "percent": 35},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["cranberry sauce", "thanksgiving"]
    },
    "тыквенный пирог": {
        "name": "Тыквенный пирог",
        "name_en": ["pumpkin pie", "american pumpkin pie"],
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 210, "protein": 4.0, "fat": 9.0, "carbs": 28.0},
        "ingredients": [
            {"name": "тыква", "type": "vegetable", "percent": 35},
            {"name": "песочное тесто", "type": "carb", "percent": 30},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "сливки", "type": "dairy", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["pumpkin pie", "thanksgiving"]
    },
    "пекановый пирог": {
        "name": "Пекановый пирог",
        "name_en": ["pecan pie", "american pecan pie"],
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 400, "protein": 5.0, "fat": 22.0, "carbs": 47.0},
        "ingredients": [
            {"name": "пекан", "type": "protein", "percent": 30},
            {"name": "песочное тесто", "type": "carb", "percent": 30},
            {"name": "кукурузный сироп", "type": "sugar", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["pecan pie", "american dessert"]
    },
    "клюквенный соус": {
        "name": "Клюквенный соус",
        "name_en": ["cranberry sauce"],
        "category": "sauce",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 150, "protein": 0.5, "fat": 0.1, "carbs": 37.0},
        "ingredients": [
            {"name": "клюква", "type": "fruit", "percent": 60},
            {"name": "сахар", "type": "carb", "percent": 35},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["cranberry sauce"]
    },
    "лосось по-канадски": {
        "name": "Лосось по-канадски",
        "name_en": ["canadian salmon"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 22.0, "fat": 11.0, "carbs": 1.0},
        "ingredients": [
            {"name": "лосось", "type": "protein", "percent": 85},
            {"name": "кленовый сироп", "type": "sugar", "percent": 8},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "специи", "type": "spice", "percent": 4}
        ],
        "keywords": ["canadian salmon", "maple salmon"]
    },

    # ==================== ЮЖНОАМЕРИКАНСКАЯ КУХНЯ ====================
    "фейжоада": {
        "name": "Фейжоада",
        "name_en": ["feijoada", "brazilian black bean stew"],
        "category": "main",
        "default_weight": 450,
        "nutrition_per_100": {"calories": 170, "protein": 12.0, "fat": 8.0, "carbs": 13.0},
        "ingredients": [
            {"name": "черная фасоль", "type": "protein", "percent": 40},
            {"name": "свинина", "type": "protein", "percent": 25},
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "колбаса", "type": "protein", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "масло", "type": "fat", "percent": 2}
        ],
        "keywords": ["feijoada", "бразильский"]
    },
    "моукеке": {
        "name": "Моукеке",
        "name_en": ["mole", "mexican mole poblano"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 8.0, "fat": 13.0, "carbs": 16.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 35},
            {"name": "перец чили", "type": "vegetable", "percent": 20},
            {"name": "шоколад", "type": "other", "percent": 10},
            {"name": "орехи", "type": "protein", "percent": 10},
            {"name": "семена", "type": "protein", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 7},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["mole", "mexican", "poblano"]
    },
    "арепас": {
        "name": "Арепас",
        "name_en": ["arepas", "venezuelan corn cakes"],
        "category": "bread",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 4.0, "fat": 6.0, "carbs": 36.0},
        "ingredients": [
            {"name": "кукурузная мука", "type": "carb", "percent": 70},
            {"name": "вода", "type": "liquid", "percent": 20},
            {"name": "масло", "type": "fat", "percent": 5},
            {"name": "соль", "type": "other", "percent": 5}
        ],
        "keywords": ["arepas", "venezuelan"]
    },
    "эмпанадас": {
        "name": "Эмпанадас",
        "name_en": ["empanadas", "argentinian pastries"],
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 260, "protein": 8.0, "fat": 14.0, "carbs": 25.0},
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 50},
            {"name": "говядина", "type": "protein", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "маслины", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["empanadas", "argentinian"]
    },
    "севиче": {
        "name": "Севиче",
        "name_en": ["ceviche", "peruvian ceviche"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 90, "protein": 12.0, "fat": 2.0, "carbs": 6.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 50},
            {"name": "лайм", "type": "fruit", "percent": 20},
            {"name": "лук красный", "type": "vegetable", "percent": 10},
            {"name": "перец чили", "type": "vegetable", "percent": 5},
            {"name": "кинза", "type": "vegetable", "percent": 5},
            {"name": "кукуруза", "type": "carb", "percent": 5},
            {"name": "батат", "type": "carb", "percent": 5}
        ],
        "keywords": ["ceviche", "peruvian"]
    },
    "мате": {
        "name": "Мате",
        "name_en": ["mate", "yerba mate"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 5, "protein": 0.2, "fat": 0.1, "carbs": 1.0},
        "ingredients": [
            {"name": "йерба мате", "type": "other", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 90}
        ],
        "keywords": ["mate", "yerba mate", "south american tea"]
    },
    "пастель де чокло": {
        "name": "Пастель де чокло",
        "name_en": ["pastel de choclo", "chilean corn pie"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 160, "protein": 7.0, "fat": 6.0, "carbs": 20.0},
        "ingredients": [
            {"name": "кукуруза", "type": "carb", "percent": 50},
            {"name": "говядина", "type": "protein", "percent": 20},
            {"name": "курица", "type": "protein", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "маслины", "type": "vegetable", "percent": 5},
            {"name": "изюм", "type": "fruit", "percent": 2}
        ],
        "keywords": ["pastel de choclo", "chilean pie"]
    },
    "пападзюлес": {
        "name": "Пападзюлес",
        "name_en": ["papadzules", "mexican egg rolls"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 10.0, "carbs": 15.0},
        "ingredients": [
            {"name": "кукурузная тортилья", "type": "carb", "percent": 40},
            {"name": "яйцо", "type": "protein", "percent": 25},
            {"name": "тыквенные семечки", "type": "protein", "percent": 15},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "перец", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["papadzules", "mexican"]
    },

    # ==================== ОКЕАНИЯ ====================
    "павлова": {
        "name": "Павлова",
        "name_en": ["pavlova", "australian dessert", "new zealand dessert"],
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 250, "protein": 3.0, "fat": 5.0, "carbs": 48.0},
        "ingredients": [
            {"name": "безе", "type": "carb", "percent": 50},
            {"name": "сливки", "type": "dairy", "percent": 25},
            {"name": "клубника", "type": "fruit", "percent": 10},
            {"name": "киви", "type": "fruit", "percent": 10},
            {"name": "маракуйя", "type": "fruit", "percent": 5}
        ],
        "keywords": ["pavlova", "australian", "new zealand dessert"]
    },
    "ламинтон": {
        "name": "Ламинтон",
        "name_en": ["lamington", "australian cake"],
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 300, "protein": 4.0, "fat": 12.0, "carbs": 44.0},
        "ingredients": [
            {"name": "бисквит", "type": "carb", "percent": 60},
            {"name": "шоколадная глазурь", "type": "sugar", "percent": 25},
            {"name": "кокосовая стружка", "type": "other", "percent": 15}
        ],
        "keywords": ["lamington", "australian cake"]
    },
    "мит пай": {
        "name": "Мит пай",
        "name_en": ["meat pie", "australian meat pie"],
        "category": "bakery",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 270, "protein": 10.0, "fat": 16.0, "carbs": 21.0},
        "ingredients": [
            {"name": "слоеное тесто", "type": "carb", "percent": 45},
            {"name": "говядина", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "соус", "type": "sauce", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["meat pie", "australian pie"]
    },
    "фиш энд чипс": {
        "name": "Фиш энд чипс",
        "name_en": ["fish and chips"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 220, "protein": 12.0, "fat": 12.0, "carbs": 17.0},
        "ingredients": [
            {"name": "треска", "type": "protein", "percent": 35},
            {"name": "кляр", "type": "carb", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 30},
            {"name": "масло для фритюра", "type": "fat", "percent": 15}
        ],
        "keywords": ["fish and chips", "британский"]
    },
    "анзак бисквит": {
        "name": "Анзак бисквит",
        "name_en": ["anzac biscuit", "australian cookie"],
        "category": "dessert",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 400, "protein": 5.0, "fat": 16.0, "carbs": 60.0},
        "ingredients": [
            {"name": "овсяные хлопья", "type": "carb", "percent": 40},
            {"name": "кокос", "type": "other", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 10}
        ],
        "keywords": ["anzac biscuit", "australian cookie"]
    },
    "киви бургер": {
        "name": "Киви бургер",
        "name_en": ["kiwi burger", "new zealand burger"],
        "category": "fastfood",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 12.0, "fat": 11.0, "carbs": 19.0},
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 30},
            {"name": "говяжья котлета", "type": "protein", "percent": 30},
            {"name": "свекла", "type": "vegetable", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "салат", "type": "vegetable", "percent": 8},
            {"name": "помидоры", "type": "vegetable", "percent": 7},
            {"name": "соус", "type": "sauce", "percent": 7}
        ],
        "keywords": ["kiwi burger", "new zealand burger"]
    },
    "ханги": {
        "name": "Ханги",
        "name_en": ["hangi", "maori earth oven"],
        "category": "main",
        "default_weight": 500,
        "nutrition_per_100": {"calories": 160, "protein": 14.0, "fat": 8.0, "carbs": 9.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 25},
            {"name": "курица", "type": "protein", "percent": 20},
            {"name": "баранина", "type": "protein", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "батат", "type": "carb", "percent": 10},
            {"name": "тыква", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["hangi", "maori", "new zealand"]
    },
    "уайтакита": {
        "name": "Уайтакита (суп из моллюсков)",
        "name_en": ["waitakita", "clam soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 70, "protein": 6.0, "fat": 2.0, "carbs": 7.0},
        "ingredients": [
            {"name": "моллюски", "type": "protein", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "лук-порей", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "сливки", "type": "dairy", "percent": 10},
            {"name": "бульон", "type": "liquid", "percent": 20}
        ],
        "keywords": ["waitakita", "new zealand soup"]
    },
    # =============================================================================
    # 🇷🇺 РАСШИРЕННАЯ БАЗА: ТРАДИЦИОННЫЕ И ПОПУЛЯРНЫЕ БЛЮДА РОССИИ
    # =============================================================================
    
    # ==================== СУПЫ (НОВЫЕ ПОЗИЦИИ) ====================
    "щи из квашеной капусты": {
        "name": "Щи из квашеной капусты",
        "name_en": ["sauerkraut shchi", "russian cabbage soup with sauerkraut"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 50, "protein": 2.5, "fat": 2.0, "carbs": 5.5},
        "ingredients": [
            {"name": "капуста квашеная", "type": "vegetable", "percent": 30},
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "томатная паста", "type": "sauce", "percent": 3},
            {"name": "вода", "type": "liquid", "percent": 24}
        ],
        "keywords": ["щи", "квашеная капуста", "sauerkraut", "shchi", "русский суп"]
    },
    "щи зеленые": {
        "name": "Щи зеленые",
        "name_en": ["green shchi", "sorrel soup", "russian sorrel soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 2.0, "fat": 1.8, "carbs": 4.5},
        "ingredients": [
            {"name": "щавель", "type": "vegetable", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "лук зеленый", "type": "vegetable", "percent": 5},
            {"name": "укроп", "type": "vegetable", "percent": 3},
            {"name": "бульон", "type": "liquid", "percent": 39}
        ],
        "keywords": ["щи", "зеленые щи", "щавель", "sorrel soup"]
    },
    "свекольник": {
        "name": "Свекольник",
        "name_en": ["svyokolnik", "cold beet soup", "russian beet soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 1.5, "fat": 1.5, "carbs": 5.0},
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 25},
            {"name": "кефир", "type": "dairy", "percent": 40},
            {"name": "огурцы свежие", "type": "vegetable", "percent": 15},
            {"name": "яйцо куриное", "type": "protein", "percent": 5},
            {"name": "укроп", "type": "vegetable", "percent": 3},
            {"name": "лук зеленый", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 7}
        ],
        "keywords": ["свекольник", "холодный суп", "beet soup", "свекла"]
    },
    "ботвинья": {
        "name": "Ботвинья",
        "name_en": ["botvinya", "russian cold soup with greens"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 3.0, "fat": 1.5, "carbs": 5.0},
        "ingredients": [
            {"name": "лосось", "type": "protein", "percent": 20},
            {"name": "щавель", "type": "vegetable", "percent": 20},
            {"name": "шпинат", "type": "vegetable", "percent": 15},
            {"name": "огурцы свежие", "type": "vegetable", "percent": 15},
            {"name": "лук зеленый", "type": "vegetable", "percent": 8},
            {"name": "квас", "type": "liquid", "percent": 22}
        ],
        "keywords": ["ботвинья", "botvinya", "холодный суп", "русский суп"]
    },
    "похлебка грибная": {
        "name": "Похлебка грибная",
        "name_en": ["mushroom pohljobka", "russian mushroom soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 2.0, "fat": 1.5, "carbs": 4.5},
        "ingredients": [
            {"name": "грибы лесные", "type": "vegetable", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "перловка", "type": "carb", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 42}
        ],
        "keywords": ["похлебка", "грибной суп", "mushroom soup"]
    },
    "уха царская": {
        "name": "Уха царская",
        "name_en": ["tsar's ukha", "russian fish soup deluxe"],
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 60, "protein": 6.0, "fat": 2.5, "carbs": 3.0},
        "ingredients": [
            {"name": "осетрина", "type": "protein", "percent": 25},
            {"name": "лосось", "type": "protein", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "водка", "type": "other", "percent": 3},
            {"name": "вода", "type": "liquid", "percent": 37}
        ],
        "keywords": ["уха", "рыбный суп", "fish soup", "осетрина"]
    },
    "калья": {
        "name": "Калья",
        "name_en": ["kalya", "russian pickle fish soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 55, "protein": 5.0, "fat": 2.0, "carbs": 4.5},
        "ingredients": [
            {"name": "рыба красная", "type": "protein", "percent": 25},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 20},
            {"name": "рассол огуречный", "type": "liquid", "percent": 20},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 22}
        ],
        "keywords": ["калья", "рыбный суп", "pickle fish soup"]
    },
    
    # ==================== САЛАТЫ (НОВЫЕ ПОЗИЦИИ) ====================
    "салат мимоза": {
        "name": "Мимоза",
        "name_en": ["mimosa salad", "russian mimosa salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 10.0, "fat": 17.0, "carbs": 6.0},
        "ingredients": [
            {"name": "консервы рыбные", "type": "protein", "percent": 25},
            {"name": "яйцо куриное", "type": "protein", "percent": 20},
            {"name": "сыр твердый", "type": "dairy", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 25}
        ],
        "keywords": ["мимоза", "mimosa", "рыбный салат", "слоеный салат"]
    },
    "салат столичный": {
        "name": "Столичный салат",
        "name_en": ["stolichny salad", "russian capital salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 9.0, "fat": 15.0, "carbs": 7.0},
        "ingredients": [
            {"name": "курица отварная", "type": "protein", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 10},
            {"name": "горошек зеленый", "type": "vegetable", "percent": 8},
            {"name": "морковь", "type": "vegetable", "percent": 7},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ],
        "keywords": ["столичный", "stolichny", "салат с курицей"]
    },
    "салат нежность": {
        "name": "Нежность",
        "name_en": ["nezhnost salad", "russian tender salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 8.0, "fat": 16.0, "carbs": 8.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 25},
            {"name": "чернослив", "type": "fruit", "percent": 15},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "огурцы свежие", "type": "vegetable", "percent": 10},
            {"name": "грецкие орехи", "type": "protein", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 10},
            {"name": "майонез", "type": "sauce", "percent": 15}
        ],
        "keywords": ["нежность", "слоеный салат", "с черносливом"]
    },
    "салат с крабовыми палочками": {
        "name": "Салат с крабовыми палочками",
        "name_en": ["crab stick salad", "russian imitation crab salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 170, "protein": 6.0, "fat": 11.0, "carbs": 11.0},
        "ingredients": [
            {"name": "крабовые палочки", "type": "protein", "percent": 30},
            {"name": "кукуруза консервированная", "type": "carb", "percent": 25},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "рис отварной", "type": "carb", "percent": 10},
            {"name": "огурцы свежие", "type": "vegetable", "percent": 10},
            {"name": "лук зеленый", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 5}
        ],
        "keywords": ["крабовый салат", "crab salad", "с крабовыми палочками"]
    },
    "салат мужской каприз": {
        "name": "Мужской каприз",
        "name_en": ["man's whim salad", "russian layered meat salad"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 12.0, "fat": 17.0, "carbs": 5.0},
        "ingredients": [
            {"name": "ветчина", "type": "protein", "percent": 30},
            {"name": "говядина отварная", "type": "protein", "percent": 20},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "лук репчатый маринованный", "type": "vegetable", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 10},
            {"name": "майонез", "type": "sauce", "percent": 15}
        ],
        "keywords": ["мужской каприз", "мясной салат"]
    },
    "салат грибная поляна": {
        "name": "Грибная поляна",
        "name_en": ["mushroom glade salad", "russian mushroom salad"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 5.0, "fat": 10.0, "carbs": 9.0},
        "ingredients": [
            {"name": "шампиньоны маринованные", "type": "vegetable", "percent": 30},
            {"name": "куриное филе", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 8},
            {"name": "майонез", "type": "sauce", "percent": 7}
        ],
        "keywords": ["грибная поляна", "mushroom salad", "слоеный салат"]
    },
    "салат тиффани": {
        "name": "Тиффани",
        "name_en": ["tiffany salad", "chicken and grape salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 12.0, "fat": 13.0, "carbs": 10.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 35},
            {"name": "виноград", "type": "fruit", "percent": 25},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "сыр", "type": "dairy", "percent": 10},
            {"name": "грецкие орехи", "type": "protein", "percent": 8},
            {"name": "майонез", "type": "sauce", "percent": 7}
        ],
        "keywords": ["тиффани", "tiffany", "салат с виноградом"]
    },
    "салат венский": {
        "name": "Венский салат",
        "name_en": ["viennese salad", "russian layered salad"],
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 8.0, "fat": 14.0, "carbs": 9.0},
        "ingredients": [
            {"name": "ветчина", "type": "protein", "percent": 30},
            {"name": "сыр", "type": "dairy", "percent": 20},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "огурцы маринованные", "type": "vegetable", "percent": 7},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ],
        "keywords": ["венский", "viennese", "слоеный салат"]
    },
    
    # ==================== ВТОРЫЕ БЛЮДА (НОВЫЕ ПОЗИЦИИ) ====================
    "бефстроганов": {
        "name": "Бефстроганов",
        "name_en": ["beef stroganoff", "stroganoff"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 12.0, "carbs": 5.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 50},
            {"name": "лук репчатый", "type": "vegetable", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["бефстроганов", "stroganoff", "говядина в сметане"]
    },
    "курица пожарская": {
        "name": "Котлеты пожарские",
        "name_en": ["pozharsky cutlets", "russian breaded chicken cutlets"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 11.0, "carbs": 8.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 60},
            {"name": "хлеб белый", "type": "carb", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "сливки", "type": "dairy", "percent": 8},
            {"name": "панировочные сухари", "type": "carb", "percent": 7}
        ],
        "keywords": ["пожарские котлеты", "pozharsky cutlets", "куриные котлеты"]
    },
    "зразы мясные": {
        "name": "Зразы мясные",
        "name_en": ["zrazy", "stuffed meat rolls"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 15.0, "fat": 14.0, "carbs": 7.0},
        "ingredients": [
            {"name": "говяжий фарш", "type": "protein", "percent": 60},
            {"name": "яйцо куриное", "type": "protein", "percent": 10},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "грибы", "type": "vegetable", "percent": 8},
            {"name": "хлеб", "type": "carb", "percent": 7},
            {"name": "панировка", "type": "carb", "percent": 5}
        ],
        "keywords": ["зразы", "zrazy", "фаршированные котлеты"]
    },
    "зразы картофельные": {
        "name": "Зразы картофельные",
        "name_en": ["potato zrazy", "stuffed potato patties"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 5.0, "fat": 5.0, "carbs": 22.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 65},
            {"name": "грибы", "type": "vegetable", "percent": 15},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 5},
            {"name": "мука", "type": "carb", "percent": 5}
        ],
        "keywords": ["зразы", "potato zrazy", "картофельные зразы"]
    },
    "плов со свининой": {
        "name": "Плов со свининой",
        "name_en": ["pork pilaf", "russian style pork pilaf"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 200, "protein": 10.0, "fat": 9.0, "carbs": 20.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 30},
            {"name": "рис", "type": "carb", "percent": 45},
            {"name": "морковь", "type": "vegetable", "percent": 12},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "масло растительное", "type": "fat", "percent": 2}
        ],
        "keywords": ["плов", "pilaf", "плов со свининой"]
    },
    "гуляш из говядины": {
        "name": "Гуляш из говядины",
        "name_en": ["beef goulash", "russian style goulash"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 170, "protein": 15.0, "fat": 9.0, "carbs": 6.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 50},
            {"name": "лук репчатый", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 8},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 7},
            {"name": "вода", "type": "liquid", "percent": 5}
        ],
        "keywords": ["гуляш", "goulash", "говядина в подливе"]
    },
    "поджарка из свинины": {
        "name": "Поджарка из свинины",
        "name_en": ["pork podzharka", "fried pork with gravy"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 16.0, "fat": 16.0, "carbs": 4.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 70},
            {"name": "лук репчатый", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 2}
        ],
        "keywords": ["поджарка", "podzharka", "жареная свинина"]
    },
    "печень по-строгановски": {
        "name": "Печень по-строгановски",
        "name_en": ["liver stroganoff", "beef liver in sour cream"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 16.0, "fat": 9.0, "carbs": 5.0},
        "ingredients": [
            {"name": "говяжья печень", "type": "protein", "percent": 60},
            {"name": "лук репчатый", "type": "vegetable", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 5}
        ],
        "keywords": ["печень", "liver", "печень в сметане"]
    },
    "куриные сердечки в сметане": {
        "name": "Куриные сердечки в сметане",
        "name_en": ["chicken hearts in sour cream", "stewed chicken hearts"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 14.0, "fat": 10.0, "carbs": 3.0},
        "ingredients": [
            {"name": "куриные сердечки", "type": "protein", "percent": 65},
            {"name": "лук репчатый", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "сметана", "type": "dairy", "percent": 10},
            {"name": "мука", "type": "carb", "percent": 2}
        ],
        "keywords": ["сердечки", "chicken hearts", "субпродукты"]
    },
    "картофель по-деревенски": {
        "name": "Картофель по-деревенски",
        "name_en": ["country style potatoes", "russian baked potatoes"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 150, "protein": 3.0, "fat": 5.0, "carbs": 23.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 80},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "укроп", "type": "vegetable", "percent": 3},
            {"name": "масло растительное", "type": "fat", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["картофель", "country potatoes", "запеченный картофель"]
    },
    "картофельные драники": {
        "name": "Драники",
        "name_en": ["draniki", "potato pancakes", "belarusian potato pancakes"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 4.0, "fat": 8.0, "carbs": 23.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 70},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 5},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ],
        "keywords": ["драники", "draniki", "картофельные оладьи"]
    },
    "картофельная бабка": {
        "name": "Картофельная бабка",
        "name_en": ["kartofelnaya babka", "potato casserole"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 160, "protein": 6.0, "fat": 7.0, "carbs": 18.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 60},
            {"name": "свинина", "type": "protein", "percent": 20},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ],
        "keywords": ["бабка", "babka", "картофельная запеканка"]
    },
    "каша гречневая с грибами": {
        "name": "Гречневая каша с грибами",
        "name_en": ["buckwheat with mushrooms", "kasha with mushrooms"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 5.0, "fat": 4.0, "carbs": 16.0},
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 60},
            {"name": "грибы", "type": "vegetable", "percent": 25},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "масло сливочное", "type": "fat", "percent": 7}
        ],
        "keywords": ["гречка", "buckwheat", "каша с грибами"]
    },
    "каша пшенная с тыквой": {
        "name": "Пшенная каша с тыквой",
        "name_en": ["millet porridge with pumpkin", "kasha with pumpkin"],
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 110, "protein": 3.0, "fat": 3.0, "carbs": 18.0},
        "ingredients": [
            {"name": "пшено", "type": "carb", "percent": 40},
            {"name": "тыква", "type": "vegetable", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["пшенная каша", "millet porridge", "тыквенная каша"]
    },
    "каша перловая": {
        "name": "Перловая каша",
        "name_en": ["pearl barley porridge", "kasha"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 3.0, "fat": 2.0, "carbs": 23.0},
        "ingredients": [
            {"name": "перловка", "type": "carb", "percent": 90},
            {"name": "масло сливочное", "type": "fat", "percent": 5},
            {"name": "соль", "type": "other", "percent": 5}
        ],
        "keywords": ["перловка", "pearl barley", "каша"]
    },
    "каша овсяная на молоке": {
        "name": "Овсяная каша на молоке",
        "name_en": ["milk oatmeal", "oatmeal porridge"],
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 100, "protein": 4.0, "fat": 3.0, "carbs": 14.0},
        "ingredients": [
            {"name": "овсяные хлопья", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 60},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["овсянка", "oatmeal", "каша"]
    },
    "гурьевская каша": {
        "name": "Гурьевская каша",
        "name_en": ["guryev porridge", "russian semolina dessert"],
        "category": "dessert",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 5.0, "fat": 8.0, "carbs": 22.0},
        "ingredients": [
            {"name": "манная крупа", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 35},
            {"name": "сливки", "type": "dairy", "percent": 10},
            {"name": "орехи", "type": "protein", "percent": 8},
            {"name": "сухофрукты", "type": "fruit", "percent": 7},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["гурьевская каша", "guryev porridge", "десерт"]
    },
    
    # ==================== ВЫПЕЧКА И ДЕСЕРТЫ ====================
    "ватрушка с творогом": {
        "name": "Ватрушка с творогом",
        "name_en": ["vatrushka", "russian cottage cheese bun"],
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 260, "protein": 9.0, "fat": 10.0, "carbs": 34.0},
        "ingredients": [
            {"name": "дрожжевое тесто", "type": "carb", "percent": 55},
            {"name": "творог", "type": "dairy", "percent": 35},
            {"name": "яйцо куриное", "type": "protein", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5}
        ],
        "keywords": ["ватрушка", "vatrushka", "творожная булочка"]
    },
    "кулебяка": {
        "name": "Кулебяка",
        "name_en": ["kulebyaka", "russian layered pie"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 10.0, "fat": 9.0, "carbs": 25.0},
        "ingredients": [
            {"name": "дрожжевое тесто", "type": "carb", "percent": 50},
            {"name": "мясной фарш", "type": "protein", "percent": 20},
            {"name": "рис", "type": "carb", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "грибы", "type": "vegetable", "percent": 7},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["кулебяка", "kulebyaka", "русский пирог"]
    },
    "расстегай": {
        "name": "Расстегай",
        "name_en": ["rasstegai", "russian open pie"],
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 240, "protein": 9.0, "fat": 10.0, "carbs": 29.0},
        "ingredients": [
            {"name": "дрожжевое тесто", "type": "carb", "percent": 55},
            {"name": "рыба", "type": "protein", "percent": 25},
            {"name": "рис", "type": "carb", "percent": 10},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["расстегай", "rasstegai", "рыбный пирожок"]
    },
    "курник": {
        "name": "Курник",
        "name_en": ["kurnik", "russian chicken pie"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "слоеное тесто", "type": "carb", "percent": 45},
            {"name": "курица", "type": "protein", "percent": 25},
            {"name": "грибы", "type": "vegetable", "percent": 10},
            {"name": "рис", "type": "carb", "percent": 8},
            {"name": "яйцо куриное", "type": "protein", "percent": 7},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["курник", "kurnik", "куриный пирог"]
    },
    "шаньга": {
        "name": "Шаньга",
        "name_en": ["shanga", "northern russian bun"],
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 250, "protein": 6.0, "fat": 10.0, "carbs": 34.0},
        "ingredients": [
            {"name": "дрожжевое тесто", "type": "carb", "percent": 60},
            {"name": "картофельное пюре", "type": "carb", "percent": 25},
            {"name": "сметана", "type": "dairy", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["шаньга", "shanga", "северная выпечка"]
    },
    "сочник с творогом": {
        "name": "Сочник с творогом",
        "name_en": ["sochnik", "russian curd filled pastry"],
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 270, "protein": 8.0, "fat": 11.0, "carbs": 35.0},
        "ingredients": [
            {"name": "песочное тесто", "type": "carb", "percent": 55},
            {"name": "творог", "type": "dairy", "percent": 30},
            {"name": "яйцо куриное", "type": "protein", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ],
        "keywords": ["сочник", "sochnik", "творожная выпечка"]
    },
    "коврижка медовая": {
        "name": "Коврижка медовая",
        "name_en": ["kovrizhka", "russian honey cake"],
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 320, "protein": 4.0, "fat": 9.0, "carbs": 55.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 45},
            {"name": "мед", "type": "sugar", "percent": 30},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 7},
            {"name": "масло сливочное", "type": "fat", "percent": 5},
            {"name": "орехи", "type": "protein", "percent": 5}
        ],
        "keywords": ["коврижка", "kovrizhka", "медовик", "пряник"]
    },
    "пышки московские": {
        "name": "Пышки московские",
        "name_en": ["pushki", "moscow doughnuts"],
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 310, "protein": 5.0, "fat": 15.0, "carbs": 38.0},
        "ingredients": [
            {"name": "дрожжевое тесто", "type": "carb", "percent": 60},
            {"name": "масло для фритюра", "type": "fat", "percent": 30},
            {"name": "сахарная пудра", "type": "carb", "percent": 10}
        ],
        "keywords": ["пышки", "pushki", "пончики", "московские пышки"]
    },
    "хворост": {
        "name": "Хворост",
        "name_en": ["khvorost", "russian twisted crisps"],
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 340, "protein": 5.0, "fat": 18.0, "carbs": 40.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 45},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "молоко", "type": "dairy", "percent": 10},
            {"name": "масло для фритюра", "type": "fat", "percent": 20}
        ],
        "keywords": ["хворост", "khvorost", "печенье"]
    },
    "орешки со сгущенкой": {
        "name": "Орешки со сгущенкой",
        "name_en": ["oreshki", "russian nut cookies with condensed milk"],
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 380, "protein": 6.0, "fat": 18.0, "carbs": 48.0},
        "ingredients": [
            {"name": "песочное тесто", "type": "carb", "percent": 60},
            {"name": "сгущенное молоко вареное", "type": "dairy", "percent": 35},
            {"name": "грецкие орехи", "type": "protein", "percent": 5}
        ],
        "keywords": ["орешки", "oreshki", "печенье со сгущенкой"]
    },
    
    # ==================== ЗАКУСКИ ====================
    "студень говяжий": {
        "name": "Студень говяжий",
        "name_en": ["beef studen", "russian beef aspic"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 160, "protein": 14.0, "fat": 11.0, "carbs": 1.0},
        "ingredients": [
            {"name": "говяжьи ножки", "type": "protein", "percent": 50},
            {"name": "говядина", "type": "protein", "percent": 30},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 10}
        ],
        "keywords": ["студень", "studen", "холодец", "aspic"]
    },
    "заливная рыба": {
        "name": "Заливная рыба",
        "name_en": ["jellied fish", "russian fish aspic"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 12.0, "fat": 5.0, "carbs": 4.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 50},
            {"name": "бульон рыбный", "type": "liquid", "percent": 35},
            {"name": "желатин", "type": "other", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "лимон", "type": "fruit", "percent": 5}
        ],
        "keywords": ["заливная рыба", "jellied fish", "рыбное заливное"]
    },
    "бутерброды со шпротами": {
        "name": "Бутерброды со шпротами",
        "name_en": ["sprat sandwiches", "russian sprats on bread"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 250, "protein": 10.0, "fat": 14.0, "carbs": 20.0},
        "ingredients": [
            {"name": "хлеб белый", "type": "carb", "percent": 45},
            {"name": "шпроты", "type": "protein", "percent": 30},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "лимон", "type": "fruit", "percent": 5},
            {"name": "зелень", "type": "vegetable", "percent": 5},
            {"name": "яйцо куриное", "type": "protein", "percent": 5}
        ],
        "keywords": ["шпроты", "sprats", "бутерброды", "праздничная закуска"]
    },
    "яйца фаршированные": {
        "name": "Яйца фаршированные",
        "name_en": ["stuffed eggs", "russian deviled eggs"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 10.0, "fat": 14.0, "carbs": 3.0},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 60},
            {"name": "майонез", "type": "sauce", "percent": 15},
            {"name": "сыр", "type": "dairy", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "зелень", "type": "vegetable", "percent": 5},
            {"name": "печень трески", "type": "protein", "percent": 5}
        ],
        "keywords": ["фаршированные яйца", "stuffed eggs", "закуска"]
    },
    "соленые грузди": {
        "name": "Соленые грузди",
        "name_en": ["salted mushrooms", "russian salted milk caps"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 30, "protein": 2.0, "fat": 0.5, "carbs": 4.0},
        "ingredients": [
            {"name": "грузди соленые", "type": "vegetable", "percent": 85},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ],
        "keywords": ["грузди", "salted mushrooms", "грибная закуска"]
    },
    "квашеная капуста": {
        "name": "Квашеная капуста",
        "name_en": ["sauerkraut", "russian fermented cabbage"],
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 25, "protein": 1.5, "fat": 0.5, "carbs": 4.0},
        "ingredients": [
            {"name": "капуста белокочанная", "type": "vegetable", "percent": 85},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "соль", "type": "other", "percent": 5},
            {"name": "клюква", "type": "fruit", "percent": 2}
        ],
        "keywords": ["квашеная капуста", "sauerkraut", "соленья"]
    },
    "маринованные огурцы": {
        "name": "Маринованные огурцы",
        "name_en": ["pickled cucumbers", "russian pickles"],
        "category": "side",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 20, "protein": 0.5, "fat": 0.1, "carbs": 4.0},
        "ingredients": [
            {"name": "огурцы", "type": "vegetable", "percent": 90},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "укроп", "type": "vegetable", "percent": 3},
            {"name": "соль", "type": "other", "percent": 4}
        ],
        "keywords": ["маринованные огурцы", "pickles", "соленья"]
    },
    
    # ==================== НАПИТКИ ====================
    "квас хлебный": {
        "name": "Квас хлебный",
        "name_en": ["kvass", "russian rye bread drink"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 30, "protein": 0.5, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "ржаной хлеб", "type": "carb", "percent": 30},
            {"name": "вода", "type": "liquid", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 4},
            {"name": "дрожжи", "type": "other", "percent": 1}
        ],
        "keywords": ["квас", "kvass", "русский напиток"]
    },
    "морс клюквенный": {
        "name": "Морс клюквенный",
        "name_en": ["cranberry morse", "russian cranberry drink"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 40, "protein": 0.1, "fat": 0.1, "carbs": 9.0},
        "ingredients": [
            {"name": "клюква", "type": "fruit", "percent": 20},
            {"name": "вода", "type": "liquid", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 10}
        ],
        "keywords": ["морс", "morse", "клюквенный морс", "cranberry juice"]
    },
    "морс брусничный": {
        "name": "Морс брусничный",
        "name_en": ["lingonberry morse", "russian lingonberry drink"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 35, "protein": 0.1, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "брусника", "type": "fruit", "percent": 20},
            {"name": "вода", "type": "liquid", "percent": 72},
            {"name": "сахар", "type": "carb", "percent": 8}
        ],
        "keywords": ["морс", "morse", "брусничный морс", "lingonberry drink"]
    },
    "компот из сухофруктов": {
        "name": "Компот из сухофруктов",
        "name_en": ["dried fruit compote", "russian kompot"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 0.3, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "сухофрукты", "type": "fruit", "percent": 20},
            {"name": "вода", "type": "liquid", "percent": 75},
            {"name": "сахар", "type": "carb", "percent": 5}
        ],
        "keywords": ["компот", "kompot", "узвар", "dried fruit compote"]
    },
    "сбитень": {
        "name": "Сбитень",
        "name_en": ["sbiten", "russian honey drink"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 60, "protein": 0.2, "fat": 0.1, "carbs": 14.0},
        "ingredients": [
            {"name": "мед", "type": "sugar", "percent": 15},
            {"name": "вода", "type": "liquid", "percent": 80},
            {"name": "пряности", "type": "spice", "percent": 5}
        ],
        "keywords": ["сбитень", "sbiten", "медовый напиток"]
    },
    "кисель клюквенный": {
        "name": "Кисель клюквенный",
        "name_en": ["cranberry kissel", "russian fruit jelly drink"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 60, "protein": 0.2, "fat": 0.1, "carbs": 14.0},
        "ingredients": [
            {"name": "клюква", "type": "fruit", "percent": 15},
            {"name": "крахмал", "type": "carb", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 67}
        ],
        "keywords": ["кисель", "kissel", "ягодный напиток"]
    },

    # =============================================================================
    # 🇷🇺 НОВЫЕ РОССИЙСКИЕ БЛЮДА (ПРОПУЩЕННЫЕ В ПРОШЛЫЙ РАЗ)
    # =============================================================================
    
    # ==================== РЕДКИЕ И СТАРИННЫЕ БЛЮДА ====================
    "визига": {
        "name": "Визига (пирог с вязигой)",
        "name_en": ["viziga", "dried sturgeon spinal cord pie"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 15.0, "fat": 8.0, "carbs": 22.0},
        "ingredients": [
            {"name": "вязига", "type": "protein", "percent": 20},
            {"name": "дрожжевое тесто", "type": "carb", "percent": 50},
            {"name": "рис", "type": "carb", "percent": 15},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "лук репчатый", "type": "vegetable", "percent": 7}
        ],
        "keywords": ["визига", "вязига", "осетровый пирог", "viziga", "старинное блюдо"]
    },
    "говяжий рубец": {
        "name": "Говяжий рубец",
        "name_en": ["tripe", "russian beef tripe"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 15.0, "fat": 8.0, "carbs": 3.0},
        "ingredients": [
            {"name": "говяжий рубец", "type": "protein", "percent": 70},
            {"name": "лук репчатый", "type": "vegetable", "percent": 12},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["рубец", "tripe", "потроха", "субпродукты"]
    },
    "векошники": {
        "name": "Векошники",
        "name_en": ["vekoshniki", "russian potato pancakes with meat"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 9.0, "fat": 8.0, "carbs": 21.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 50},
            {"name": "мясной фарш", "type": "protein", "percent": 25},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "масло растительное", "type": "fat", "percent": 7}
        ],
        "keywords": ["векошники", "vekoshniki", "картофельные оладьи с мясом"]
    },
    "калья": {
        "name": "Калья рыбная",
        "name_en": ["kalya", "russian pickle fish soup"],
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 60, "protein": 5.0, "fat": 2.0, "carbs": 5.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 25},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 15},
            {"name": "рассол огуречный", "type": "liquid", "percent": 20},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "морковь", "type": "vegetable", "percent": 7},
            {"name": "вода", "type": "liquid", "percent": 25}
        ],
        "keywords": ["калья", "kalya", "рыбный суп с рассолом"]
    },
    "кундюмы": {
        "name": "Кундюмы",
        "name_en": ["kundyumy", "russian mushroom dumplings"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 5.0, "fat": 6.0, "carbs": 27.0},
        "ingredients": [
            {"name": "грибы лесные", "type": "vegetable", "percent": 30},
            {"name": "тесто", "type": "carb", "percent": 45},
            {"name": "гречка", "type": "carb", "percent": 10},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "масло растительное", "type": "fat", "percent": 7}
        ],
        "keywords": ["кундюмы", "kundyumy", "постные пельмени", "грибные пельмени"]
    },
    
    # ==================== ДИЧЬ И ОХОТНИЧЬИ БЛЮДА ====================
    "куропатки в сметане": {
        "name": "Куропатки в сметане",
        "name_en": ["partridge in sour cream", "russian partridge"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 22.0, "fat": 11.0, "carbs": 2.0},
        "ingredients": [
            {"name": "куропатка", "type": "protein", "percent": 60},
            {"name": "сметана", "type": "dairy", "percent": 25},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "масло сливочное", "type": "fat", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["куропатки", "partridge", "дичь", "охота"]
    },
    "рябчики": {
        "name": "Рябчики жареные",
        "name_en": ["fried hazel grouse", "russian game birds"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 180, "protein": 23.0, "fat": 9.0, "carbs": 1.0},
        "ingredients": [
            {"name": "рябчик", "type": "protein", "percent": 80},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "соль", "type": "other", "percent": 5}
        ],
        "keywords": ["рябчики", "hazel grouse", "дичь"]
    },
    "тетерев": {
        "name": "Тетерев тушеный",
        "name_en": ["stewed black grouse", "russian game"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 190, "protein": 21.0, "fat": 11.0, "carbs": 2.0},
        "ingredients": [
            {"name": "тетерев", "type": "protein", "percent": 65},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "сметана", "type": "dairy", "percent": 12},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["тетерев", "black grouse", "дичь"]
    },
    "заяц в сметане": {
        "name": "Заяц в сметане",
        "name_en": ["hare in sour cream", "russian hare stew"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 24.0, "fat": 8.0, "carbs": 2.0},
        "ingredients": [
            {"name": "зайчатина", "type": "protein", "percent": 65},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["заяц", "hare", "дичь"]
    },
    
    # ==================== РЫБНЫЕ БЛЮДА ====================
    "стерлядь запеченная": {
        "name": "Стерлядь, запеченная в соли",
        "name_en": ["sterlet baked in salt", "russian sterlet"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 150, "protein": 18.0, "fat": 8.0, "carbs": 1.0},
        "ingredients": [
            {"name": "стерлядь", "type": "protein", "percent": 70},
            {"name": "соль крупная", "type": "other", "percent": 25},
            {"name": "яичный белок", "type": "protein", "percent": 5}
        ],
        "keywords": ["стерлядь", "sterlet", "осетровые", "царская рыба"]
    },
    "караси в сметане": {
        "name": "Караси в сметане",
        "name_en": ["crucian carp in sour cream", "russian carp"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 160, "protein": 16.0, "fat": 9.0, "carbs": 3.0},
        "ingredients": [
            {"name": "карась", "type": "protein", "percent": 65},
            {"name": "сметана", "type": "dairy", "percent": 25},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "мука", "type": "carb", "percent": 2}
        ],
        "keywords": ["караси", "crucian carp", "речная рыба", "сметана"]
    },
    "налимья печень": {
        "name": "Печень налима",
        "name_en": ["burbot liver", "russian delicacy"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 280, "protein": 12.0, "fat": 24.0, "carbs": 2.0},
        "ingredients": [
            {"name": "печень налима", "type": "protein", "percent": 85},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "масло сливочное", "type": "fat", "percent": 7}
        ],
        "keywords": ["налим", "burbot liver", "деликатес"]
    },
    "щука фаршированная": {
        "name": "Щука фаршированная",
        "name_en": ["stuffed pike", "russian gefilte fish"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 130, "protein": 15.0, "fat": 5.0, "carbs": 6.0},
        "ingredients": [
            {"name": "щука", "type": "protein", "percent": 60},
            {"name": "хлеб белый", "type": "carb", "percent": 15},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "сливки", "type": "dairy", "percent": 7}
        ],
        "keywords": ["щука", "pike", "фаршированная рыба"]
    },
    "сиг заливной": {
        "name": "Сиг заливной",
        "name_en": ["jellied whitefish", "russian fish aspic"],
        "category": "appetizer",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 110, "protein": 13.0, "fat": 5.0, "carbs": 2.0},
        "ingredients": [
            {"name": "сиг", "type": "protein", "percent": 50},
            {"name": "бульон рыбный", "type": "liquid", "percent": 35},
            {"name": "желатин", "type": "other", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "лимон", "type": "fruit", "percent": 5}
        ],
        "keywords": ["сиг", "whitefish", "заливное"]
    },
    
    # ==================== КАШИ (НОВЫЕ) ====================
    "полба с куркумой": {
        "name": "Полба с куркумой",
        "name_en": ["spelt with turmeric", "russian ancient grain"],
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 130, "protein": 5.0, "fat": 2.5, "carbs": 23.0},
        "ingredients": [
            {"name": "полба", "type": "carb", "percent": 85},
            {"name": "куркума", "type": "spice", "percent": 2},
            {"name": "масло сливочное", "type": "fat", "percent": 8},
            {"name": "соль", "type": "other", "percent": 5}
        ],
        "keywords": ["полба", "spelt", "древняя крупа"]
    },
    "гороховая каша": {
        "name": "Гороховая каша",
        "name_en": ["pea porridge", "russian pea mash"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 7.0, "fat": 2.0, "carbs": 18.0},
        "ingredients": [
            {"name": "горох колотый", "type": "protein", "percent": 80},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["гороховая каша", "pea porridge"]
    },
    "крупеник из пшена": {
        "name": "Крупеник из пшена с творогом",
        "name_en": ["millet krupennik", "millet cottage cheese casserole"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 160, "protein": 7.0, "fat": 5.0, "carbs": 22.0},
        "ingredients": [
            {"name": "пшено", "type": "carb", "percent": 40},
            {"name": "творог", "type": "dairy", "percent": 30},
            {"name": "яйцо куриное", "type": "protein", "percent": 10},
            {"name": "молоко", "type": "dairy", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["крупеник", "krupennik", "пшенная запеканка"]
    },
    "манная каша с грушей": {
        "name": "Манная каша с грушей",
        "name_en": ["semolina with pear", "russian breakfast"],
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 4.0, "fat": 3.0, "carbs": 20.0},
        "ingredients": [
            {"name": "манная крупа", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 50},
            {"name": "груша", "type": "fruit", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["манная каша", "semolina", "завтрак"]
    },
    
    # ==================== МЯСНЫЕ БЛЮДА (НОВЫЕ) ====================
    "окорок свиной запеченный": {
        "name": "Окорок свиной, запеченный куском",
        "name_en": ["baked ham", "russian baked pork"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 260, "protein": 22.0, "fat": 19.0, "carbs": 1.0},
        "ingredients": [
            {"name": "свиной окорок", "type": "protein", "percent": 90},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ],
        "keywords": ["окорок", "ham", "запеченная свинина"]
    },
    "свинина с квашеной капустой": {
        "name": "Свинина с квашеной капустой в горшочке",
        "name_en": ["pork with sauerkraut", "russian pot roast"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 200, "protein": 15.0, "fat": 12.0, "carbs": 8.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 45},
            {"name": "капуста квашеная", "type": "vegetable", "percent": 35},
            {"name": "лук репчатый", "type": "vegetable", "percent": 8},
            {"name": "морковь", "type": "vegetable", "percent": 7},
            {"name": "чеснок", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["свинина с капустой", "горшочек", "pork with sauerkraut"]
    },
    "телятина запеченная": {
        "name": "Телятина запеченная",
        "name_en": ["roasted veal", "russian veal"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 180, "protein": 24.0, "fat": 9.0, "carbs": 1.0},
        "ingredients": [
            {"name": "телятина", "type": "protein", "percent": 85},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "розмарин", "type": "spice", "percent": 3},
            {"name": "масло оливковое", "type": "fat", "percent": 7}
        ],
        "keywords": ["телятина", "veal", "запеченное мясо"]
    },
    
    # ==================== ВЫПЕЧКА (НОВЫЕ) ====================
    "калитки": {
        "name": "Калитки",
        "name_en": ["kalitki", "karelian open pies"],
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 210, "protein": 6.0, "fat": 7.0, "carbs": 31.0},
        "ingredients": [
            {"name": "ржаное тесто", "type": "carb", "percent": 55},
            {"name": "пшенная каша", "type": "carb", "percent": 25},
            {"name": "сметана", "type": "dairy", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["калитки", "kalitki", "карельские пирожки"]
    },
    "вергуны": {
        "name": "Вергуны",
        "name_en": ["verguns", "russian twisted pastries"],
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 330, "protein": 5.0, "fat": 15.0, "carbs": 43.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 50},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "масло для фритюра", "type": "fat", "percent": 10}
        ],
        "keywords": ["вергуны", "verguns", "хворост"]
    },
    "левашники": {
        "name": "Левашники",
        "name_en": ["levashniki", "russian filled pancakes"],
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 6.0, "fat": 8.0, "carbs": 32.0},
        "ingredients": [
            {"name": "блины", "type": "carb", "percent": 50},
            {"name": "ягодное повидло", "type": "fruit", "percent": 35},
            {"name": "творог", "type": "dairy", "percent": 15}
        ],
        "keywords": ["левашники", "levashniki", "блины с начинкой"]
    },
    
    # ==================== НАПИТКИ (НОВЫЕ) ====================
    "медовуха": {
        "name": "Медовуха",
        "name_en": ["medovukha", "russian honey drink"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 80, "protein": 0.1, "fat": 0.1, "carbs": 18.0},
        "ingredients": [
            {"name": "мед", "type": "sugar", "percent": 25},
            {"name": "вода", "type": "liquid", "percent": 70},
            {"name": "дрожжи", "type": "other", "percent": 3},
            {"name": "хмель", "type": "other", "percent": 2}
        ],
        "keywords": ["медовуха", "medovukha", "медовый напиток"]
    },
    "варенец": {
        "name": "Варенец",
        "name_en": ["varenets", "russian fermented baked milk"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 60, "protein": 3.0, "fat": 3.5, "carbs": 4.5},
        "ingredients": [
            {"name": "топленое молоко", "type": "dairy", "percent": 90},
            {"name": "сметана", "type": "dairy", "percent": 10}
        ],
        "keywords": ["варенец", "varenets", "ряженка", "кисломолочный"]
    },
    "ряженка": {
        "name": "Ряженка",
        "name_en": ["ryazhenka", "baked fermented milk"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 60, "protein": 3.0, "fat": 3.5, "carbs": 4.5},
        "ingredients": [
            {"name": "топленое молоко", "type": "dairy", "percent": 95},
            {"name": "закваска", "type": "other", "percent": 5}
        ],
        "keywords": ["ряженка", "ryazhenka", "кисломолочный"]
    },
    "простокваша": {
        "name": "Простокваша",
        "name_en": ["prostokvasha", "russian sour milk"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 55, "protein": 3.0, "fat": 3.0, "carbs": 4.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 95},
            {"name": "закваска", "type": "other", "percent": 5}
        ],
        "keywords": ["простокваша", "prostokvasha", "кисломолочный"]
    },
    
    # ==================== САЛАТ ЦЕЗАРЬ С КРАСНОЙ РЫБОЙ ====================
    "цезарь с красной рыбой": {
        "name": "Цезарь с красной рыбой",
        "name_en": ["caesar with salmon", "salmon caesar salad", "caesar with red fish"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 15.0, "carbs": 8.0},
        "ingredients": [
            {"name": "лосось слабосоленый", "type": "protein", "percent": 30},
            {"name": "салат романо", "type": "vegetable", "percent": 30},
            {"name": "пармезан", "type": "dairy", "percent": 8},
            {"name": "сухарики", "type": "carb", "percent": 10},
            {"name": "помидоры черри", "type": "vegetable", "percent": 8},
            {"name": "авокадо", "type": "fruit", "percent": 7},
            {"name": "соус цезарь", "type": "sauce", "percent": 7}
        ],
        "keywords": ["цезарь", "caesar", "красная рыба", "лосось", "семга", "salmon caesar"]
    },
    "цезарь с семгой": {
        "name": "Цезарь с семгой",
        "name_en": ["salmon caesar", "caesar with salmon"],
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 215, "protein": 13.0, "fat": 15.5, "carbs": 7.5},
        "ingredients": [
            {"name": "семга слабосоленая", "type": "protein", "percent": 30},
            {"name": "салат айсберг", "type": "vegetable", "percent": 30},
            {"name": "пармезан", "type": "dairy", "percent": 8},
            {"name": "гренки чесночные", "type": "carb", "percent": 10},
            {"name": "помидоры черри", "type": "vegetable", "percent": 8},
            {"name": "соус цезарь", "type": "sauce", "percent": 8},
            {"name": "яйцо перепелиное", "type": "protein", "percent": 6}
        ],
        "keywords": ["цезарь с семгой", "salmon caesar", "лосось"]
    },
    "цезарь с лососем запеченным": {
        "name": "Цезарь с запеченным лососем",
        "name_en": ["baked salmon caesar", "warm salmon caesar"],
        "category": "salad",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 14.0, "fat": 11.0, "carbs": 9.0},
        "ingredients": [
            {"name": "лосось запеченный", "type": "protein", "percent": 35},
            {"name": "салат романо", "type": "vegetable", "percent": 30},
            {"name": "пармезан", "type": "dairy", "percent": 8},
            {"name": "гренки", "type": "carb", "percent": 10},
            {"name": "помидоры черри", "type": "vegetable", "percent": 7},
            {"name": "соус цезарь", "type": "sauce", "percent": 10}
        ],
        "keywords": ["цезарь с лососем", "запеченный лосось", "warm salmon caesar"]
    },

    # =============================================================================
    # 🍽️ РЕСТОРАННЫЕ ТРЕНДЫ 2026 И ПОПУЛЯРНЫЕ БЛЮДА
    # =============================================================================
    
    # ==================== РЕСТОРАННАЯ КЛАССИКА И ТРЕНДЫ ====================
    "татар из говядины": {
        "name": "Татар из говядины",
        "name_en": ["beef tartare", "steak tartare"],
        "category": "appetizer",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 180, "protein": 20.0, "fat": 10.0, "carbs": 2.0},
        "ingredients": [
            {"name": "говяжья вырезка", "type": "protein", "percent": 75},
            {"name": "лук шалот", "type": "vegetable", "percent": 5},
            {"name": "каперсы", "type": "vegetable", "percent": 4},
            {"name": "корнишоны", "type": "vegetable", "percent": 4},
            {"name": "желток яичный", "type": "protein", "percent": 5},
            {"name": "горчица дижонская", "type": "sauce", "percent": 3},
            {"name": "соус ворчестер", "type": "sauce", "percent": 2},
            {"name": "масло оливковое", "type": "fat", "percent": 2}
        ],
        "keywords": ["татар", "tartare", "говядина", "закуска", "ресторан"]
    },
    "тартар из лосося": {
        "name": "Тартар из лосося",
        "name_en": ["salmon tartare", "salmon tartar"],
        "category": "appetizer",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 13.0, "carbs": 3.0},
        "ingredients": [
            {"name": "лосось свежий", "type": "protein", "percent": 70},
            {"name": "авокадо", "type": "fruit", "percent": 12},
            {"name": "лук шалот", "type": "vegetable", "percent": 4},
            {"name": "лайм", "type": "fruit", "percent": 4},
            {"name": "соус соевый", "type": "sauce", "percent": 3},
            {"name": "кунжутное масло", "type": "fat", "percent": 2},
            {"name": "огурец", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["тартар", "лосось", "salmon tartare", "рыбная закуска"]
    },
    "карпаччо из говядины": {
        "name": "Карпаччо из говядины",
        "name_en": ["beef carpaccio"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 150, "protein": 18.0, "fat": 8.0, "carbs": 2.0},
        "ingredients": [
            {"name": "говяжья вырезка", "type": "protein", "percent": 75},
            {"name": "пармезан", "type": "dairy", "percent": 8},
            {"name": "рукола", "type": "vegetable", "percent": 7},
            {"name": "оливковое масло", "type": "fat", "percent": 5},
            {"name": "лимонный сок", "type": "fruit", "percent": 3},
            {"name": "каперсы", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["карпаччо", "carpaccio", "итальянская закуска"]
    },
    "овощи на гриле": {
        "name": "Овощи на гриле",
        "name_en": ["grilled vegetables", "vegetable grill"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 90, "protein": 3.0, "fat": 5.0, "carbs": 8.0},
        "ingredients": [
            {"name": "кабачки", "type": "vegetable", "percent": 25},
            {"name": "баклажаны", "type": "vegetable", "percent": 25},
            {"name": "перец болгарский", "type": "vegetable", "percent": 20},
            {"name": "помидоры черри", "type": "vegetable", "percent": 15},
            {"name": "оливковое масло", "type": "fat", "percent": 10},
            {"name": "тимьян", "type": "spice", "percent": 5}
        ],
        "keywords": ["гриль", "grilled vegetables", "овощи"]
    },
    "кальмары гриль": {
        "name": "Кальмары на гриле",
        "name_en": ["grilled squid", "calamari grill"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 130, "protein": 20.0, "fat": 4.0, "carbs": 4.0},
        "ingredients": [
            {"name": "кальмары", "type": "protein", "percent": 75},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "петрушка", "type": "vegetable", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 8},
            {"name": "лимон", "type": "fruit", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 2}
        ],
        "keywords": ["кальмары", "squid", "calamari", "гриль"]
    },
    "медальоны из свинины": {
        "name": "Медальоны из свинины",
        "name_en": ["pork medallions"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 24.0, "fat": 12.0, "carbs": 2.0},
        "ingredients": [
            {"name": "свиная вырезка", "type": "protein", "percent": 80},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "розмарин", "type": "spice", "percent": 2},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "вино белое", "type": "liquid", "percent": 5}
        ],
        "keywords": ["медальоны", "pork medallions", "свинина"]
    },
    "баранина с розмарином": {
        "name": "Бараньи ребрышки с розмарином",
        "name_en": ["lamb ribs with rosemary"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 260, "protein": 22.0, "fat": 19.0, "carbs": 2.0},
        "ingredients": [
            {"name": "бараньи ребрышки", "type": "protein", "percent": 80},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "розмарин", "type": "spice", "percent": 3},
            {"name": "оливковое масло", "type": "fat", "percent": 10},
            {"name": "лимон", "type": "fruit", "percent": 2}
        ],
        "keywords": ["баранина", "lamb ribs", "ребрышки"]
    },
    "утиная грудка с апельсинами": {
        "name": "Утиная грудка с апельсиновым соусом",
        "name_en": ["duck breast with orange sauce"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 18.0, "fat": 14.0, "carbs": 6.0},
        "ingredients": [
            {"name": "утиная грудка", "type": "protein", "percent": 65},
            {"name": "апельсины", "type": "fruit", "percent": 15},
            {"name": "мед", "type": "sugar", "percent": 5},
            {"name": "соус соевый", "type": "sauce", "percent": 5},
            {"name": "лук шалот", "type": "vegetable", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ],
        "keywords": ["утка", "duck", "апельсиновый соус", "ресторан"]
    },
    "морской язык": {
        "name": "Морской язык",
        "name_en": ["sole fish", "dover sole"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 120, "protein": 22.0, "fat": 3.0, "carbs": 1.0},
        "ingredients": [
            {"name": "морской язык", "type": "protein", "percent": 80},
            {"name": "масло сливочное", "type": "fat", "percent": 8},
            {"name": "лимон", "type": "fruit", "percent": 5},
            {"name": "петрушка", "type": "vegetable", "percent": 5},
            {"name": "каперсы", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["морской язык", "sole", "рыба"]
    },
    "мидии в сливочном соусе": {
        "name": "Мидии в сливочном соусе",
        "name_en": ["mussels in cream sauce"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 130, "protein": 12.0, "fat": 7.0, "carbs": 5.0},
        "ingredients": [
            {"name": "мидии", "type": "protein", "percent": 50},
            {"name": "сливки", "type": "dairy", "percent": 25},
            {"name": "лук шалот", "type": "vegetable", "percent": 8},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "вино белое", "type": "liquid", "percent": 7},
            {"name": "петрушка", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["мидии", "mussels", "морепродукты"]
    },
    "креветки темпура": {
        "name": "Креветки в темпуре",
        "name_en": ["shrimp tempura", "tempura shrimp"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 210, "protein": 14.0, "fat": 10.0, "carbs": 16.0},
        "ingredients": [
            {"name": "креветки", "type": "protein", "percent": 50},
            {"name": "мука для темпуры", "type": "carb", "percent": 20},
            {"name": "вода ледяная", "type": "liquid", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло для фритюра", "type": "fat", "percent": 10}
        ],
        "keywords": ["темпура", "tempura", "креветки", "японская закуска"]
    },
    "луковые кольца": {
        "name": "Луковые кольца",
        "name_en": ["onion rings"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 280, "protein": 4.0, "fat": 16.0, "carbs": 30.0},
        "ingredients": [
            {"name": "лук репчатый", "type": "vegetable", "percent": 50},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "панировочные сухари", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "масло для фритюра", "type": "fat", "percent": 12}
        ],
        "keywords": ["onion rings", "луковые кольца", "закуска"]
    },
    "сырные палочки": {
        "name": "Сырные палочки",
        "name_en": ["cheese sticks", "mozzarella sticks"],
        "category": "appetizer",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 310, "protein": 14.0, "fat": 18.0, "carbs": 22.0},
        "ingredients": [
            {"name": "сыр моцарелла", "type": "dairy", "percent": 60},
            {"name": "панировочные сухари", "type": "carb", "percent": 15},
            {"name": "мука", "type": "carb", "percent": 8},
            {"name": "яйцо", "type": "protein", "percent": 7},
            {"name": "масло для фритюра", "type": "fat", "percent": 10}
        ],
        "keywords": ["cheese sticks", "mozzarella sticks", "закуска"]
    },
    "наггетсы куриные": {
        "name": "Куриные наггетсы",
        "name_en": ["chicken nuggets"],
        "category": "appetizer",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 250, "protein": 16.0, "fat": 15.0, "carbs": 14.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 60},
            {"name": "панировочные сухари", "type": "carb", "percent": 15},
            {"name": "мука", "type": "carb", "percent": 8},
            {"name": "яйцо", "type": "protein", "percent": 7},
            {"name": "масло для фритюра", "type": "fat", "percent": 10}
        ],
        "keywords": ["nuggets", "наггетсы", "курица", "фастфуд"]
    },
    "картофель айдахо": {
        "name": "Картофель по-айдаховски",
        "name_en": ["idaho potatoes", "baked potatoes"],
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 3.0, "fat": 5.0, "carbs": 23.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 75},
            {"name": "сыр чеддер", "type": "dairy", "percent": 10},
            {"name": "бекон", "type": "protein", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 8},
            {"name": "лук зеленый", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["айдахо", "idaho potatoes", "запеченный картофель"]
    },
    
    # ==================== ФАСТФУД-ХИТЫ ====================
    "чизбургер": {
        "name": "Чизбургер",
        "name_en": ["cheeseburger"],
        "category": "fastfood",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 260, "protein": 14.0, "fat": 12.0, "carbs": 25.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 30},
            {"name": "котлета говяжья", "type": "protein", "percent": 30},
            {"name": "сыр чеддер", "type": "dairy", "percent": 10},
            {"name": "салат", "type": "vegetable", "percent": 8},
            {"name": "помидоры", "type": "vegetable", "percent": 6},
            {"name": "лук", "type": "vegetable", "percent": 4},
            {"name": "кетчуп", "type": "sauce", "percent": 5},
            {"name": "горчица", "type": "sauce", "percent": 2},
            {"name": "майонез", "type": "sauce", "percent": 5}
        ],
        "keywords": ["чизбургер", "cheeseburger", "бургер"]
    },
    "дабл чизбургер": {
        "name": "Дабл чизбургер",
        "name_en": ["double cheeseburger"],
        "category": "fastfood",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 270, "protein": 16.0, "fat": 14.0, "carbs": 22.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 25},
            {"name": "котлета говяжья", "type": "protein", "percent": 40},
            {"name": "сыр чеддер", "type": "dairy", "percent": 15},
            {"name": "салат", "type": "vegetable", "percent": 6},
            {"name": "помидоры", "type": "vegetable", "percent": 4},
            {"name": "лук", "type": "vegetable", "percent": 3},
            {"name": "кетчуп", "type": "sauce", "percent": 4},
            {"name": "майонез", "type": "sauce", "percent": 3}
        ],
        "keywords": ["дабл", "double cheeseburger", "бургер"]
    },
    "бургер с беконом": {
        "name": "Бургер с беконом",
        "name_en": ["bacon burger"],
        "category": "fastfood",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 280, "protein": 16.0, "fat": 16.0, "carbs": 21.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 25},
            {"name": "котлета говяжья", "type": "protein", "percent": 30},
            {"name": "бекон", "type": "protein", "percent": 15},
            {"name": "сыр", "type": "dairy", "percent": 8},
            {"name": "салат", "type": "vegetable", "percent": 6},
            {"name": "помидоры", "type": "vegetable", "percent": 4},
            {"name": "лук", "type": "vegetable", "percent": 3},
            {"name": "соус", "type": "sauce", "percent": 9}
        ],
        "keywords": ["bacon burger", "бургер с беконом"]
    },
    "чизбургер с беконом": {
        "name": "Чизбургер с беконом",
        "name_en": ["bacon cheeseburger"],
        "category": "fastfood",
        "default_weight": 320,
        "nutrition_per_100": {"calories": 280, "protein": 17.0, "fat": 16.0, "carbs": 20.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 25},
            {"name": "котлета говяжья", "type": "protein", "percent": 30},
            {"name": "бекон", "type": "protein", "percent": 12},
            {"name": "сыр чеддер", "type": "dairy", "percent": 10},
            {"name": "салат", "type": "vegetable", "percent": 6},
            {"name": "помидоры", "type": "vegetable", "percent": 4},
            {"name": "лук", "type": "vegetable", "percent": 3},
            {"name": "соус", "type": "sauce", "percent": 10}
        ],
        "keywords": ["bacon cheeseburger", "чизбургер с беконом"]
    },
    "куриный бургер": {
        "name": "Куриный бургер",
        "name_en": ["chicken burger"],
        "category": "fastfood",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 220, "protein": 15.0, "fat": 10.0, "carbs": 20.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 30},
            {"name": "куриная котлета", "type": "protein", "percent": 30},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 10},
            {"name": "кетчуп", "type": "sauce", "percent": 7}
        ],
        "keywords": ["chicken burger", "куриный бургер"]
    },
    "острая курица": {
        "name": "Острая курица",
        "name_en": ["spicy chicken", "hot chicken"],
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 20.0, "fat": 12.0, "carbs": 10.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 60},
            {"name": "острый соус", "type": "sauce", "percent": 15},
            {"name": "панировка", "type": "carb", "percent": 15},
            {"name": "масло для фритюра", "type": "fat", "percent": 10}
        ],
        "keywords": ["spicy chicken", "hot chicken", "острый"]
    },
    "стрипсы куриные": {
        "name": "Куриные стрипсы",
        "name_en": ["chicken strips", "chicken tenders"],
        "category": "fastfood",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 230, "protein": 18.0, "fat": 13.0, "carbs": 12.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 65},
            {"name": "панировка", "type": "carb", "percent": 18},
            {"name": "яйцо", "type": "protein", "percent": 7},
            {"name": "масло для фритюра", "type": "fat", "percent": 10}
        ],
        "keywords": ["стрипсы", "chicken strips", "chicken tenders"]
    },
    "крылышки барбекю": {
        "name": "Крылышки барбекю",
        "name_en": ["bbq chicken wings"],
        "category": "appetizer",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 18.0, "fat": 16.0, "carbs": 6.0},
        "ingredients": [
            {"name": "куриные крылья", "type": "protein", "percent": 70},
            {"name": "соус барбекю", "type": "sauce", "percent": 20},
            {"name": "масло", "type": "fat", "percent": 10}
        ],
        "keywords": ["крылышки", "chicken wings", "bbq"]
    },
    "крылышки острые": {
        "name": "Острые крылышки",
        "name_en": ["hot wings"],
        "category": "appetizer",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 230, "protein": 18.0, "fat": 15.0, "carbs": 5.0},
        "ingredients": [
            {"name": "куриные крылья", "type": "protein", "percent": 70},
            {"name": "острый соус", "type": "sauce", "percent": 20},
            {"name": "масло", "type": "fat", "percent": 10}
        ],
        "keywords": ["hot wings", "острые крылышки"]
    },
    "хот-дог": {
        "name": "Хот-дог",
        "name_en": ["hot dog"],
        "category": "fastfood",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 240, "protein": 8.0, "fat": 13.0, "carbs": 23.0},
        "ingredients": [
            {"name": "булочка для хот-дога", "type": "carb", "percent": 40},
            {"name": "сосиска", "type": "protein", "percent": 30},
            {"name": "кетчуп", "type": "sauce", "percent": 8},
            {"name": "горчица", "type": "sauce", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 7},
            {"name": "капуста квашеная", "type": "vegetable", "percent": 10}
        ],
        "keywords": ["hot dog", "хот-дог"]
    },
    "хот-дог по-мексикански": {
        "name": "Хот-дог по-мексикански",
        "name_en": ["mexican hot dog"],
        "category": "fastfood",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 230, "protein": 8.0, "fat": 12.0, "carbs": 23.0},
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 35},
            {"name": "сосиска", "type": "protein", "percent": 25},
            {"name": "перец халапеньо", "type": "vegetable", "percent": 8},
            {"name": "сальса", "type": "sauce", "percent": 12},
            {"name": "авокадо", "type": "fruit", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 7},
            {"name": "кинза", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["mexican hot dog", "хот-дог"]
    },
    "французский хот-дог": {
        "name": "Французский хот-дог",
        "name_en": ["french hot dog"],
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 250, "protein": 8.0, "fat": 14.0, "carbs": 24.0},
        "ingredients": [
            {"name": "багет", "type": "carb", "percent": 50},
            {"name": "сосиска", "type": "protein", "percent": 30},
            {"name": "соус", "type": "sauce", "percent": 15},
            {"name": "сыр", "type": "dairy", "percent": 5}
        ],
        "keywords": ["french hot dog", "французский хот-дог"]
    },
    "корн-дог": {
        "name": "Корн-дог",
        "name_en": ["corn dog"],
        "category": "fastfood",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 260, "protein": 7.0, "fat": 12.0, "carbs": 31.0},
        "ingredients": [
            {"name": "сосиска", "type": "protein", "percent": 35},
            {"name": "кукурузная мука", "type": "carb", "percent": 35},
            {"name": "пшеничная мука", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "масло для фритюра", "type": "fat", "percent": 12}
        ],
        "keywords": ["corn dog", "корн-дог"]
    },
    
    # ==================== ПИЦЦА (ПОПУЛЯРНЫЕ ВАРИАНТЫ) ====================
    "пицца пепперони": {
        "name": "Пицца Пепперони",
        "name_en": ["pepperoni pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 270, "protein": 12.0, "fat": 12.0, "carbs": 29.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "соус томатный", "type": "sauce", "percent": 15},
            {"name": "сыр моцарелла", "type": "dairy", "percent": 25},
            {"name": "пепперони", "type": "protein", "percent": 15}
        ],
        "keywords": ["пицца", "pizza", "пепперони", "pepperoni"]
    },
    "пицца четыре сыра": {
        "name": "Пицца Четыре сыра",
        "name_en": ["four cheese pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 290, "protein": 14.0, "fat": 14.0, "carbs": 27.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "соус сливочный", "type": "sauce", "percent": 10},
            {"name": "моцарелла", "type": "dairy", "percent": 20},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "горгонзола", "type": "dairy", "percent": 8},
            {"name": "фета", "type": "dairy", "percent": 7}
        ],
        "keywords": ["четыре сыра", "four cheese", "пицца"]
    },
    "пицца гавайская": {
        "name": "Пицца Гавайская",
        "name_en": ["hawaiian pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 240, "protein": 10.0, "fat": 8.0, "carbs": 32.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "соус томатный", "type": "sauce", "percent": 15},
            {"name": "сыр моцарелла", "type": "dairy", "percent": 20},
            {"name": "ветчина", "type": "protein", "percent": 10},
            {"name": "ананас", "type": "fruit", "percent": 10}
        ],
        "keywords": ["hawaiian", "гавайская", "пицца с ананасом"]
    },
    "пицца мясная": {
        "name": "Пицца Мясная",
        "name_en": ["meat pizza"],
        "category": "bakery",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 260, "protein": 14.0, "fat": 11.0, "carbs": 27.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 40},
            {"name": "соус томатный", "type": "sauce", "percent": 12},
            {"name": "сыр моцарелла", "type": "dairy", "percent": 20},
            {"name": "пепперони", "type": "protein", "percent": 8},
            {"name": "ветчина", "type": "protein", "percent": 8},
            {"name": "бекон", "type": "protein", "percent": 7},
            {"name": "говядина", "type": "protein", "percent": 5}
        ],
        "keywords": ["мясная пицца", "meat pizza"]
    },
    "пицца с грибами": {
        "name": "Пицца с грибами",
        "name_en": ["mushroom pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 220, "protein": 9.0, "fat": 8.0, "carbs": 29.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "соус томатный", "type": "sauce", "percent": 15},
            {"name": "сыр моцарелла", "type": "dairy", "percent": 20},
            {"name": "шампиньоны", "type": "vegetable", "percent": 20}
        ],
        "keywords": ["грибная пицца", "mushroom pizza"]
    },
    "пицца с курицей": {
        "name": "Пицца с курицей",
        "name_en": ["chicken pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 230, "protein": 12.0, "fat": 8.0, "carbs": 28.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "соус сливочный", "type": "sauce", "percent": 12},
            {"name": "сыр моцарелла", "type": "dairy", "percent": 20},
            {"name": "куриное филе", "type": "protein", "percent": 15},
            {"name": "шампиньоны", "type": "vegetable", "percent": 8}
        ],
        "keywords": ["chicken pizza", "пицца с курицей"]
    },
    
    # ==================== БОУЛЫ И ПОЛЕЗНЫЕ БЛЮДА ====================
    "боул с лососем и авокадо": {
        "name": "Боул с лососем и авокадо",
        "name_en": ["salmon and avocado bowl"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 130, "protein": 8.0, "fat": 6.0, "carbs": 11.0},
        "ingredients": [
            {"name": "рис бурый", "type": "carb", "percent": 30},
            {"name": "лосось слабосоленый", "type": "protein", "percent": 20},
            {"name": "авокадо", "type": "fruit", "percent": 15},
            {"name": "огурец", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "эдамаме", "type": "protein", "percent": 7},
            {"name": "водоросли нори", "type": "vegetable", "percent": 5},
            {"name": "кунжут", "type": "seed", "percent": 5}
        ],
        "keywords": ["боул", "bowl", "лосось", "авокадо", "пп"]
    },
    "боул с курицей и киноа": {
        "name": "Боул с курицей и киноа",
        "name_en": ["chicken quinoa bowl"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 120, "protein": 10.0, "fat": 4.0, "carbs": 11.0},
        "ingredients": [
            {"name": "киноа", "type": "carb", "percent": 30},
            {"name": "куриное филе", "type": "protein", "percent": 25},
            {"name": "помидоры черри", "type": "vegetable", "percent": 12},
            {"name": "огурец", "type": "vegetable", "percent": 10},
            {"name": "перец", "type": "vegetable", "percent": 8},
            {"name": "соус песто", "type": "sauce", "percent": 8},
            {"name": "руккола", "type": "vegetable", "percent": 7}
        ],
        "keywords": ["боул", "bowl", "киноа", "quinoa", "пп"]
    },
    "боул с овощами и хумусом": {
        "name": "Овощной боул с хумусом",
        "name_en": ["vegetable bowl with hummus"],
        "category": "main",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 100, "protein": 4.0, "fat": 4.0, "carbs": 13.0},
        "ingredients": [
            {"name": "булгур", "type": "carb", "percent": 30},
            {"name": "хумус", "type": "sauce", "percent": 15},
            {"name": "нут", "type": "protein", "percent": 10},
            {"name": "помидоры черри", "type": "vegetable", "percent": 12},
            {"name": "огурец", "type": "vegetable", "percent": 10},
            {"name": "перец", "type": "vegetable", "percent": 8},
            {"name": "авокадо", "type": "fruit", "percent": 8},
            {"name": "руккола", "type": "vegetable", "percent": 7}
        ],
        "keywords": ["боул", "bowl", "веган", "vegan", "хумус"]
    },
    "сэндвич с авокадо и яйцом": {
        "name": "Сэндвич с авокадо и яйцом",
        "name_en": ["avocado egg sandwich"],
        "category": "sandwich",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 10.0, "carbs": 15.0},
        "ingredients": [
            {"name": "тостовый хлеб", "type": "carb", "percent": 40},
            {"name": "авокадо", "type": "fruit", "percent": 25},
            {"name": "яйцо пашот", "type": "protein", "percent": 15},
            {"name": "руккола", "type": "vegetable", "percent": 8},
            {"name": "соус песто", "type": "sauce", "percent": 7},
            {"name": "помидоры", "type": "vegetable", "percent": 5}
        ],
        "keywords": ["сэндвич", "avocado toast", "sandwich"]
    },
    "сэндвич с индейкой": {
        "name": "Сэндвич с индейкой",
        "name_en": ["turkey sandwich"],
        "category": "sandwich",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 12.0, "fat": 5.0, "carbs": 17.0},
        "ingredients": [
            {"name": "хлеб цельнозерновой", "type": "carb", "percent": 40},
            {"name": "индейка", "type": "protein", "percent": 30},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "огурец", "type": "vegetable", "percent": 5},
            {"name": "йогуртовый соус", "type": "sauce", "percent": 7}
        ],
        "keywords": ["сэндвич", "turkey sandwich", "индейка"]
    },
    
    # ==================== БЛЮДА ИЗ КАПУСТЫ (ТРЕНД 2026) ====================
    "стейк из капусты": {
        "name": "Стейк из капусты",
        "name_en": ["cabbage steak", "grilled cabbage steak"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 70, "protein": 3.0, "fat": 3.0, "carbs": 8.0},
        "ingredients": [
            {"name": "капуста белокочанная", "type": "vegetable", "percent": 80},
            {"name": "оливковое масло", "type": "fat", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "тимьян", "type": "spice", "percent": 2},
            {"name": "соль", "type": "other", "percent": 5}
        ],
        "keywords": ["стейк из капусты", "cabbage steak", "тренд 2026"]
    },
    "капустный салат с яблоком": {
        "name": "Салат из капусты с яблоком",
        "name_en": ["cabbage and apple salad"],
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 60, "protein": 2.0, "fat": 2.5, "carbs": 7.0},
        "ingredients": [
            {"name": "капуста белокочанная", "type": "vegetable", "percent": 60},
            {"name": "яблоко", "type": "fruit", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лимонный сок", "type": "fruit", "percent": 3},
            {"name": "масло оливковое", "type": "fat", "percent": 5},
            {"name": "зелень", "type": "vegetable", "percent": 2}
        ],
        "keywords": ["капустный салат", "cabbage salad", "тренд 2026"]
    },
    "капустные котлеты": {
        "name": "Капустные котлеты",
        "name_en": ["cabbage patties", "cabbage cutlets"],
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 4.0, "fat": 5.0, "carbs": 15.0},
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 60},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "манная крупа", "type": "carb", "percent": 12},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "панировочные сухари", "type": "carb", "percent": 7},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["капустные котлеты", "cabbage cutlets", "постные"]
    },
    "капуста тушеная с черносливом": {
        "name": "Капуста тушеная с черносливом",
        "name_en": ["stewed cabbage with prunes"],
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 80, "protein": 2.5, "fat": 2.0, "carbs": 13.0},
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 70},
            {"name": "чернослив", "type": "fruit", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 2}
        ],
        "keywords": ["тушеная капуста", "stewed cabbage", "чернослив"]
    },
    "капустные рулетики с сыром": {
        "name": "Капустные рулетики с сыром",
        "name_en": ["cabbage rolls with cheese"],
        "category": "appetizer",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 6.0, "fat": 8.0, "carbs": 10.0},
        "ingredients": [
            {"name": "капустные листья", "type": "vegetable", "percent": 40},
            {"name": "сыр", "type": "dairy", "percent": 30},
            {"name": "творог", "type": "dairy", "percent": 15},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 10}
        ],
        "keywords": ["капустные рулетики", "cabbage rolls"]
    },
    
    # ==================== ИНДИЙСКАЯ КУХНЯ (FAST-CASUAL) ====================
    "тикка масала": {
        "name": "Тикка масала",
        "name_en": ["chicken tikka masala"],
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 170, "protein": 12.0, "fat": 10.0, "carbs": 9.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 40},
            {"name": "томатный соус", "type": "sauce", "percent": 25},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "специи (гарам масала)", "type": "spice", "percent": 7},
            {"name": "масло топленое", "type": "fat", "percent": 5}
        ],
        "keywords": ["tikka masala", "индийский", "curry"]
    },
    "панир тикка": {
        "name": "Панир тикка",
        "name_en": ["paneer tikka"],
        "category": "appetizer",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 10.0, "fat": 14.0, "carbs": 8.0},
        "ingredients": [
            {"name": "панир", "type": "dairy", "percent": 60},
            {"name": "йогурт", "type": "dairy", "percent": 15},
            {"name": "перец", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "специи", "type": "spice", "percent": 7}
        ],
        "keywords": ["paneer", "тикка", "индийский"]
    },
    "саг панир": {
        "name": "Саг панир",
        "name_en": ["saag paneer"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 11.0, "carbs": 6.0},
        "ingredients": [
            {"name": "панир", "type": "dairy", "percent": 40},
            {"name": "шпинат", "type": "vegetable", "percent": 35},
            {"name": "сливки", "type": "dairy", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 3},
            {"name": "специи", "type": "spice", "percent": 7}
        ],
        "keywords": ["saag paneer", "индийский", "шпинат"]
    },
    "дал макхани": {
        "name": "Дал макхани",
        "name_en": ["dal makhani"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 140, "protein": 7.0, "fat": 6.0, "carbs": 15.0},
        "ingredients": [
            {"name": "черная чечевица", "type": "protein", "percent": 50},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "томатная паста", "type": "sauce", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "имбирь", "type": "spice", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "масло топленое", "type": "fat", "percent": 7}
        ],
        "keywords": ["dal makhani", "индийский", "чечевица"]
    },
    "чана масала": {
        "name": "Чана масала",
        "name_en": ["chana masala"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 130, "protein": 6.0, "fat": 5.0, "carbs": 16.0},
        "ingredients": [
            {"name": "нут", "type": "protein", "percent": 60},
            {"name": "томатный соус", "type": "sauce", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "специи", "type": "spice", "percent": 8},
            {"name": "масло", "type": "fat", "percent": 4}
        ],
        "keywords": ["chana masala", "нут", "индийский"]
    },
    "самоса с мясом": {
        "name": "Самоса с мясом",
        "name_en": ["meat samosa"],
        "category": "appetizer",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 270, "protein": 9.0, "fat": 15.0, "carbs": 25.0},
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 45},
            {"name": "бараний фарш", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "горошек", "type": "vegetable", "percent": 8},
            {"name": "специи", "type": "spice", "percent": 7}
        ],
        "keywords": ["самоса", "samosa", "индийский пирожок"]
    },
    
    # ==================== СЛАДКО-ОСТРЫЕ БЛЮДА (ТРЕНД 2026) ====================
    "курица с медом и чили": {
        "name": "Курица с медом и чили",
        "name_en": ["honey chili chicken"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 190, "protein": 18.0, "fat": 7.0, "carbs": 14.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 60},
            {"name": "мед", "type": "sugar", "percent": 15},
            {"name": "соус соевый", "type": "sauce", "percent": 10},
            {"name": "перец чили", "type": "vegetable", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["honey chili", "сладко-острый", "тренд"]
    },
    "свинина в кисло-сладком соусе": {
        "name": "Свинина в кисло-сладком соусе",
        "name_en": ["sweet and sour pork"],
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 14.0, "fat": 9.0, "carbs": 20.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 45},
            {"name": "ананас", "type": "fruit", "percent": 15},
            {"name": "перец", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "соус кисло-сладкий", "type": "sauce", "percent": 20},
            {"name": "масло", "type": "fat", "percent": 2}
        ],
        "keywords": ["sweet and sour", "кисло-сладкий", "китайский"]
    },
    "креветки с апельсином и чили": {
        "name": "Креветки с апельсином и чили",
        "name_en": ["orange chili shrimp"],
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 140, "protein": 16.0, "fat": 4.0, "carbs": 10.0},
        "ingredients": [
            {"name": "креветки", "type": "protein", "percent": 60},
            {"name": "апельсин", "type": "fruit", "percent": 20},
            {"name": "перец чили", "type": "vegetable", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "соус соевый", "type": "sauce", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ],
        "keywords": ["shrimp", "orange chili", "сладко-острый"]
    },
    "пицца с ананасом и халапеньо": {
        "name": "Пицца с ананасом и халапеньо",
        "name_en": ["pineapple jalapeno pizza"],
        "category": "bakery",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 240, "protein": 10.0, "fat": 9.0, "carbs": 30.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "соус томатный", "type": "sauce", "percent": 12},
            {"name": "сыр моцарелла", "type": "dairy", "percent": 20},
            {"name": "ананас", "type": "fruit", "percent": 12},
            {"name": "халапеньо", "type": "vegetable", "percent": 8},
            {"name": "ветчина", "type": "protein", "percent": 3}
        ],
        "keywords": ["pineapple jalapeno", "сладко-острая пицца"]
    },
    
    # ==================== МОКТЕЙЛИ (БЕЗАЛКОГОЛЬНЫЕ КОКТЕЙЛИ) ====================
    "мохито безалкогольный": {
        "name": "Мохито безалкогольный",
        "name_en": ["virgin mojito", "non-alcoholic mojito"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 35, "protein": 0.2, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "лайм", "type": "fruit", "percent": 10},
            {"name": "мята", "type": "vegetable", "percent": 5},
            {"name": "сахарный сироп", "type": "sugar", "percent": 8},
            {"name": "содовая", "type": "liquid", "percent": 75},
            {"name": "лед", "type": "other", "percent": 2}
        ],
        "keywords": ["мохито", "mojito", "virgin", "безалкогольный"]
    },
    "пина колада безалкогольная": {
        "name": "Пина колада безалкогольная",
        "name_en": ["virgin pina colada"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 70, "protein": 0.3, "fat": 1.5, "carbs": 13.0},
        "ingredients": [
            {"name": "ананасовый сок", "type": "fruit", "percent": 50},
            {"name": "кокосовое молоко", "type": "dairy", "percent": 30},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "ананас", "type": "fruit", "percent": 5}
        ],
        "keywords": ["pina colada", "virgin", "безалкогольный"]
    },
    "беллини безалкогольный": {
        "name": "Беллини безалкогольный",
        "name_en": ["virgin bellini"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 0.3, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "персиковое пюре", "type": "fruit", "percent": 40},
            {"name": "газировка", "type": "liquid", "percent": 60}
        ],
        "keywords": ["bellini", "virgin", "безалкогольный"]
    },
    "матча-латте": {
        "name": "Матча-латте",
        "name_en": ["matcha latte"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 45, "protein": 2.0, "fat": 1.5, "carbs": 5.0},
        "ingredients": [
            {"name": "матча", "type": "other", "percent": 3},
            {"name": "молоко", "type": "dairy", "percent": 80},
            {"name": "сахарный сироп", "type": "sugar", "percent": 7},
            {"name": "вода", "type": "liquid", "percent": 10}
        ],
        "keywords": ["matcha", "матча", "латте", "тренд"]
    },
    "латте с куркумой": {
        "name": "Золотое латте с куркумой",
        "name_en": ["golden latte", "turmeric latte"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 40, "protein": 1.5, "fat": 1.2, "carbs": 5.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 85},
            {"name": "куркума", "type": "spice", "percent": 3},
            {"name": "имбирь", "type": "spice", "percent": 2},
            {"name": "мед", "type": "sugar", "percent": 5},
            {"name": "черный перец", "type": "spice", "percent": 1},
            {"name": "вода", "type": "liquid", "percent": 4}
        ],
        "keywords": ["golden latte", "turmeric", "куркума"]
    },
    "чай комбуча": {
        "name": "Комбуча",
        "name_en": ["kombucha"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 15, "protein": 0.1, "fat": 0.1, "carbs": 3.0},
        "ingredients": [
            {"name": "чайный гриб", "type": "other", "percent": 5},
            {"name": "чай", "type": "other", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 80}
        ],
        "keywords": ["kombucha", "комбуча", "ферментированный чай"]
    },
    "имбирный эль": {
        "name": "Имбирный эль",
        "name_en": ["ginger ale", "ginger beer"],
        "category": "drink",
        "default_weight": 330,
        "nutrition_per_100": {"calories": 40, "protein": 0.1, "fat": 0.1, "carbs": 10.0},
        "ingredients": [
            {"name": "имбирь", "type": "spice", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 8},
            {"name": "лимоны", "type": "fruit", "percent": 5},
            {"name": "газированная вода", "type": "liquid", "percent": 80},
            {"name": "дрожжи", "type": "other", "percent": 2}
        ],
        "keywords": ["ginger ale", "имбирный эль"]
    },
    "лимонад с базиликом": {
        "name": "Лимонад с базиликом",
        "name_en": ["basil lemonade"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 35, "protein": 0.2, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "лимоны", "type": "fruit", "percent": 15},
            {"name": "базилик", "type": "vegetable", "percent": 5},
            {"name": "сахарный сироп", "type": "sugar", "percent": 8},
            {"name": "вода", "type": "liquid", "percent": 70},
            {"name": "лед", "type": "other", "percent": 2}
        ],
        "keywords": ["basil lemonade", "лимонад с базиликом"]
    },
    "лимонад с огурцом и мятой": {
        "name": "Лимонад с огурцом и мятой",
        "name_en": ["cucumber mint lemonade"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 30, "protein": 0.2, "fat": 0.1, "carbs": 7.0},
        "ingredients": [
            {"name": "огурец", "type": "vegetable", "percent": 15},
            {"name": "мята", "type": "vegetable", "percent": 5},
            {"name": "лайм", "type": "fruit", "percent": 8},
            {"name": "сахарный сироп", "type": "sugar", "percent": 7},
            {"name": "вода", "type": "liquid", "percent": 63},
            {"name": "лед", "type": "other", "percent": 2}
        ],
        "keywords": ["cucumber lemonade", "огуречный лимонад"]
    },
    "фреш апельсиновый": {
        "name": "Фреш апельсиновый",
        "name_en": ["fresh orange juice"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 10.0},
        "ingredients": [
            {"name": "апельсины", "type": "fruit", "percent": 100}
        ],
        "keywords": ["fresh", "фреш", "orange juice"]
    },
    "смузи бананово-клубничный": {
        "name": "Смузи бананово-клубничный",
        "name_en": ["banana strawberry smoothie"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 60, "protein": 1.0, "fat": 0.5, "carbs": 13.0},
        "ingredients": [
            {"name": "банан", "type": "fruit", "percent": 30},
            {"name": "клубника", "type": "fruit", "percent": 30},
            {"name": "йогурт", "type": "dairy", "percent": 30},
            {"name": "мед", "type": "sugar", "percent": 5},
            {"name": "лед", "type": "other", "percent": 5}
        ],
        "keywords": ["smoothie", "смузи", "банан", "клубника"]
    },
    "смузи зеленый": {
        "name": "Зеленый смузи",
        "name_en": ["green smoothie"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 1.5, "fat": 0.8, "carbs": 8.0},
        "ingredients": [
            {"name": "шпинат", "type": "vegetable", "percent": 30},
            {"name": "яблоко", "type": "fruit", "percent": 25},
            {"name": "сельдерей", "type": "vegetable", "percent": 15},
            {"name": "огурец", "type": "vegetable", "percent": 15},
            {"name": "имбирь", "type": "spice", "percent": 3},
            {"name": "лимон", "type": "fruit", "percent": 2},
            {"name": "вода", "type": "liquid", "percent": 10}
        ],
        "keywords": ["green smoothie", "зеленый смузи", "детокс"]
    },

    # =============================================================================
    # 🍸 АЛКОГОЛЬНЫЕ КОКТЕЙЛИ И ШОТЫ
    # =============================================================================
    
    # ==================== КЛАССИЧЕСКИЕ ЛОНГ-ДРИНКИ ====================
    "мохито": {
        "name": "Мохито",
        "name_en": ["Mojito", "Mint Mojito"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 0.2, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "светлый ром", "type": "alcohol", "percent": 15},
            {"name": "мята", "type": "vegetable", "percent": 2},
            {"name": "лайм", "type": "fruit", "percent": 5},
            {"name": "сахарный сироп", "type": "sugar", "percent": 8},
            {"name": "содовая", "type": "liquid", "percent": 40},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["мохито", "mojito", "ром", "мята", "лайм", "коктейль"]
    },
    "пина колада": {
        "name": "Пина Колада",
        "name_en": ["Piña Colada"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 70, "protein": 0.3, "fat": 1.5, "carbs": 12.0},
        "ingredients": [
            {"name": "белый ром", "type": "alcohol", "percent": 15},
            {"name": "кокосовое молоко", "type": "dairy", "percent": 20},
            {"name": "ананасовый сок", "type": "fruit", "percent": 35},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["пина колада", "pina colada", "кокос", "ананас", "коктейль"]
    },
    "куба либре": {
        "name": "Куба Либре",
        "name_en": ["Cuba Libre", "Rum and Coke"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 50, "protein": 0.1, "fat": 0.1, "carbs": 7.0},
        "ingredients": [
            {"name": "светлый ром", "type": "alcohol", "percent": 15},
            {"name": "кола", "type": "liquid", "percent": 45},
            {"name": "лайм", "type": "fruit", "percent": 5},
            {"name": "лед", "type": "other", "percent": 35}
        ],
        "keywords": ["cuba libre", "куба либре", "ром с колой", "rum and coke"]
    },
    "джин-тоник": {
        "name": "Джин-тоник",
        "name_en": ["Gin and Tonic", "Gin Tonic"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 55, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "джин", "type": "alcohol", "percent": 15},
            {"name": "тоник", "type": "liquid", "percent": 50},
            {"name": "лайм", "type": "fruit", "percent": 3},
            {"name": "лед", "type": "other", "percent": 32}
        ],
        "keywords": ["джин тоник", "gin tonic", "gin and tonic"]
    },
    "отвертка": {
        "name": "Отвертка",
        "name_en": ["Screwdriver"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 55, "protein": 0.3, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 20},
            {"name": "апельсиновый сок", "type": "fruit", "percent": 50},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["отвертка", "screwdriver", "водка с соком"]
    },
    "кровавая мэри": {
        "name": "Кровавая Мэри",
        "name_en": ["Bloody Mary"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 45, "protein": 0.5, "fat": 0.2, "carbs": 3.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 15},
            {"name": "томатный сок", "type": "vegetable", "percent": 50},
            {"name": "лимонный сок", "type": "fruit", "percent": 5},
            {"name": "вустерский соус", "type": "sauce", "percent": 1},
            {"name": "табаско", "type": "sauce", "percent": 1},
            {"name": "соль", "type": "spice", "percent": 1},
            {"name": "перец", "type": "spice", "percent": 1},
            {"name": "лед", "type": "other", "percent": 26}
        ],
        "keywords": ["bloody mary", "кровавая мэри", "томатный сок", "водка"]
    },
    "маргарита": {
        "name": "Маргарита",
        "name_en": ["Margarita"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 70, "protein": 0.2, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "текила", "type": "alcohol", "percent": 20},
            {"name": "трипл сек", "type": "alcohol", "percent": 10},
            {"name": "лайм", "type": "fruit", "percent": 8},
            {"name": "лед", "type": "other", "percent": 62}
        ],
        "keywords": ["margarita", "маргарита", "текила", "трипл сек"]
    },
    "текила санрайз": {
        "name": "Текила Санрайз",
        "name_en": ["Tequila Sunrise"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 65, "protein": 0.3, "fat": 0.1, "carbs": 7.0},
        "ingredients": [
            {"name": "текила", "type": "alcohol", "percent": 15},
            {"name": "апельсиновый сок", "type": "fruit", "percent": 45},
            {"name": "гренадин", "type": "sugar", "percent": 5},
            {"name": "лед", "type": "other", "percent": 35}
        ],
        "keywords": ["tequila sunrise", "текила санрайз", "восход солнца"]
    },
    "лонг айленд": {
        "name": "Лонг-Айленд",
        "name_en": ["Long Island Iced Tea"],
        "category": "drink",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 80, "protein": 0.2, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 5},
            {"name": "джин", "type": "alcohol", "percent": 5},
            {"name": "белый ром", "type": "alcohol", "percent": 5},
            {"name": "текила", "type": "alcohol", "percent": 5},
            {"name": "трипл сек", "type": "alcohol", "percent": 5},
            {"name": "лимонный сок", "type": "fruit", "percent": 8},
            {"name": "сахарный сироп", "type": "sugar", "percent": 5},
            {"name": "кола", "type": "liquid", "percent": 22},
            {"name": "лед", "type": "other", "percent": 40}
        ],
        "keywords": ["long island", "лонг айленд", "iced tea"]
    },
    "апероль шприц": {
        "name": "Апероль Шприц",
        "name_en": ["Aperol Spritz"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 60, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "апероль", "type": "alcohol", "percent": 15},
            {"name": "просекко", "type": "alcohol", "percent": 30},
            {"name": "содовая", "type": "liquid", "percent": 15},
            {"name": "апельсин", "type": "fruit", "percent": 5},
            {"name": "лед", "type": "other", "percent": 35}
        ],
        "keywords": ["aperol spritz", "апероль шприц", "итальянский коктейль"]
    },
    "мимоза": {
        "name": "Мимоза",
        "name_en": ["Mimosa"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 55, "protein": 0.3, "fat": 0.1, "carbs": 4.0},
        "ingredients": [
            {"name": "шампанское", "type": "alcohol", "percent": 50},
            {"name": "апельсиновый сок", "type": "fruit", "percent": 50}
        ],
        "keywords": ["mimosa", "мимоза", "шампанское с соком"]
    },
    "северное сияние": {
        "name": "Северное сияние",
        "name_en": ["Northern Lights", "Aurora Borealis"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 65, "protein": 0.2, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 20},
            {"name": "ликер блю кюрасао", "type": "alcohol", "percent": 10},
            {"name": "спрайт", "type": "liquid", "percent": 35},
            {"name": "лимонный сок", "type": "fruit", "percent": 5},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["северное сияние", "northern lights", "блю кюрасао"]
    },
    
    # ==================== ШОТЫ (СЛОИСТЫЕ И СМЕШАННЫЕ) ====================
    "б-52": {
        "name": "B-52",
        "name_en": ["B-52", "B52 Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 220, "protein": 1.0, "fat": 6.0, "carbs": 18.0},
        "ingredients": [
            {"name": "кофейный ликер", "type": "alcohol", "percent": 33},
            {"name": "айриш крим", "type": "alcohol", "percent": 33},
            {"name": "апельсиновый ликер", "type": "alcohol", "percent": 34}
        ],
        "keywords": ["b-52", "b52", "шот", "слоистый", "кофейный", "ирландские сливки"]
    },
    "камикадзе": {
        "name": "Камикадзе",
        "name_en": ["Kamikaze Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 180, "protein": 0.1, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 40},
            {"name": "трипл сек", "type": "alcohol", "percent": 30},
            {"name": "лайм", "type": "fruit", "percent": 30}
        ],
        "keywords": ["kamikaze", "камикадзе", "шот", "водка"]
    },
    "хиросима": {
        "name": "Хиросима",
        "name_en": ["Hiroshima Shot"],
        "category": "shot",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 200, "protein": 1.0, "fat": 5.0, "carbs": 15.0},
        "ingredients": [
            {"name": "самбука", "type": "alcohol", "percent": 30},
            {"name": "айриш крим", "type": "alcohol", "percent": 25},
            {"name": "абсент", "type": "alcohol", "percent": 15},
            {"name": "гренадин", "type": "sugar", "percent": 30}
        ],
        "keywords": ["hiroshima", "хиросима", "слоистый шот", "абсент"]
    },
    "медуза": {
        "name": "Медуза",
        "name_en": ["Medusa Shot"],
        "category": "shot",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 190, "protein": 1.0, "fat": 4.0, "carbs": 16.0},
        "ingredients": [
            {"name": "малибу", "type": "alcohol", "percent": 30},
            {"name": "куантро", "type": "alcohol", "percent": 20},
            {"name": "белый ром", "type": "alcohol", "percent": 20},
            {"name": "байлис", "type": "alcohol", "percent": 15},
            {"name": "блю кюрасао", "type": "alcohol", "percent": 15}
        ],
        "keywords": ["медуза", "medusa", "слоистый шот", "эффектный"]
    },
    "флаг россии": {
        "name": "Флаг России",
        "name_en": ["Russian Flag Shot"],
        "category": "shot",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 180, "protein": 0.5, "fat": 2.0, "carbs": 14.0},
        "ingredients": [
            {"name": "гренадин", "type": "sugar", "percent": 25},
            {"name": "блю кюрасао", "type": "alcohol", "percent": 25},
            {"name": "водка", "type": "alcohol", "percent": 25},
            {"name": "байлис", "type": "alcohol", "percent": 25}
        ],
        "keywords": ["флаг россии", "russian flag", "триколор", "слоистый шот"]
    },
    "егермейстер шот": {
        "name": "Егермейстер шот",
        "name_en": ["Jägermeister Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 180, "protein": 0.1, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "егермейстер", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["jagermeister", "егермейстер", "шот", "травяной ликер"]
    },
    "самбука кон мосска": {
        "name": "Самбука с мухами",
        "name_en": ["Sambuca con Mosca", "Sambuca with Flies"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 200, "protein": 0.1, "fat": 0.1, "carbs": 15.0},
        "ingredients": [
            {"name": "самбука", "type": "alcohol", "percent": 80},
            {"name": "кофейные зерна", "type": "other", "percent": 20}
        ],
        "keywords": ["sambuca", "самбука", "con mosca", "кофейные зерна"]
    },
    "абсент шот": {
        "name": "Абсент",
        "name_en": ["Absinthe Shot"],
        "category": "shot",
        "default_weight": 40,
        "nutrition_per_100": {"calories": 210, "protein": 0.1, "fat": 0.1, "carbs": 9.0},
        "ingredients": [
            {"name": "абсент", "type": "alcohol", "percent": 80},
            {"name": "сахар", "type": "sugar", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 10}
        ],
        "keywords": ["absinthe", "абсент", "зеленый шот", "полынный"]
    },
    "зеленая фея": {
        "name": "Зеленая фея",
        "name_en": ["Green Fairy"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 200, "protein": 0.1, "fat": 0.1, "carbs": 10.0},
        "ingredients": [
            {"name": "абсент", "type": "alcohol", "percent": 50},
            {"name": "сахарный сироп", "type": "sugar", "percent": 20},
            {"name": "лимонный сок", "type": "fruit", "percent": 30}
        ],
        "keywords": ["зеленая фея", "абсент", "green fairy"]
    },
    "утренняя роса": {
        "name": "Утренняя роса",
        "name_en": ["Morning Dew"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 40},
            {"name": "ликер дынный", "type": "alcohol", "percent": 30},
            {"name": "лайм", "type": "fruit", "percent": 30}
        ],
        "keywords": ["утренняя роса", "дынный шот", "midori"]
    },
    "с нутеллой": {
        "name": "Шот с нутеллой",
        "name_en": ["Nutella Shot"],
        "category": "shot",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 250, "protein": 2.0, "fat": 10.0, "carbs": 25.0},
        "ingredients": [
            {"name": "франжелико", "type": "alcohol", "percent": 40},
            {"name": "байлис", "type": "alcohol", "percent": 30},
            {"name": "водка", "type": "alcohol", "percent": 30}
        ],
        "keywords": ["nutella shot", "нутелла", "десертный шот"]
    },
    "жидкий кекс": {
        "name": "Жидкий кекс",
        "name_en": ["Liquid Cupcake"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 230, "protein": 1.0, "fat": 6.0, "carbs": 22.0},
        "ingredients": [
            {"name": "ванильная водка", "type": "alcohol", "percent": 40},
            {"name": "ликер какао", "type": "alcohol", "percent": 30},
            {"name": "байлис", "type": "alcohol", "percent": 30}
        ],
        "keywords": ["liquid cupcake", "жидкий кекс", "десертный"]
    },
    
    # ==================== ДИЖЕСТИВЫ И АПЕРИТИВЫ ====================
    "лимоначелло": {
        "name": "Лимоначелло",
        "name_en": ["Limoncello"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 200, "protein": 0.1, "fat": 0.1, "carbs": 25.0},
        "ingredients": [
            {"name": "лимоначелло", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["limoncello", "лимоначелло", "итальянский ликер"]
    },
    "франжелико": {
        "name": "Франжелико",
        "name_en": ["Frangelico"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 190, "protein": 0.5, "fat": 0.2, "carbs": 18.0},
        "ingredients": [
            {"name": "франжелико", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["frangelico", "франжелико", "ореховый ликер"]
    },
    "амбретто": {
        "name": "Амбретто",
        "name_en": ["Amaretto"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 22.0},
        "ingredients": [
            {"name": "амбретто", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["amaretto", "амбретто", "миндальный ликер"]
    },
    "джин шот": {
        "name": "Джин",
        "name_en": ["Gin Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 160, "protein": 0.1, "fat": 0.1, "carbs": 0.5},
        "ingredients": [
            {"name": "джин", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["gin", "джин", "шот"]
    },
    "водка шот": {
        "name": "Водка",
        "name_en": ["Vodka Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 150, "protein": 0.1, "fat": 0.1, "carbs": 0.1},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["vodka", "водка", "русский шот"]
    },
    "текила шот": {
        "name": "Текила",
        "name_en": ["Tequila Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 160, "protein": 0.1, "fat": 0.1, "carbs": 0.5},
        "ingredients": [
            {"name": "текила", "type": "alcohol", "percent": 80},
            {"name": "соль", "type": "spice", "percent": 10},
            {"name": "лайм", "type": "fruit", "percent": 10}
        ],
        "keywords": ["tequila", "текила", "соль", "лайм"]
    },
    "виски шот": {
        "name": "Виски",
        "name_en": ["Whiskey Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 0.1},
        "ingredients": [
            {"name": "виски", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["whiskey", "виски", "бурбон", "скотч"]
    },
    "коньяк шот": {
        "name": "Коньяк",
        "name_en": ["Cognac Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 0.1},
        "ingredients": [
            {"name": "коньяк", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["cognac", "коньяк"]
    },
    "ром шот": {
        "name": "Ром",
        "name_en": ["Rum Shot"],
        "category": "shot",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 160, "protein": 0.1, "fat": 0.1, "carbs": 0.5},
        "ingredients": [
            {"name": "ром", "type": "alcohol", "percent": 100}
        ],
        "keywords": ["rum", "ром"]
    },
    
    # ==================== КОКТЕЙЛЬНАЯ КЛАССИКА IBA ====================
    "мартинез": {
        "name": "Мартинез",
        "name_en": ["Martinez"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 0.1, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "джин", "type": "alcohol", "percent": 40},
            {"name": "красный вермут", "type": "alcohol", "percent": 25},
            {"name": "ликер мараскин", "type": "alcohol", "percent": 10},
            {"name": "биттер ангостура", "type": "alcohol", "percent": 5},
            {"name": "лед", "type": "other", "percent": 20}
        ],
        "keywords": ["martinez", "мартинез", "предшественник мартини"]
    },
    "авиация": {
        "name": "Авиация",
        "name_en": ["Aviation"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "джин", "type": "alcohol", "percent": 40},
            {"name": "ликер мараскин", "type": "alcohol", "percent": 10},
            {"name": "фиалковый ликер", "type": "alcohol", "percent": 10},
            {"name": "лимонный сок", "type": "fruit", "percent": 10},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["aviation", "авиация", "фиалковый коктейль"]
    },
    "бижу": {
        "name": "Бижу",
        "name_en": ["Bijou"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 7.0},
        "ingredients": [
            {"name": "джин", "type": "alcohol", "percent": 35},
            {"name": "красный вермут", "type": "alcohol", "percent": 25},
            {"name": "зеленый шартрез", "type": "alcohol", "percent": 15},
            {"name": "биттер", "type": "alcohol", "percent": 5},
            {"name": "лед", "type": "other", "percent": 20}
        ],
        "keywords": ["bijou", "бижу", "драгоценный коктейль"]
    },
    "александр": {
        "name": "Александр",
        "name_en": ["Alexander"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 200, "protein": 1.5, "fat": 5.0, "carbs": 8.0},
        "ingredients": [
            {"name": "джин", "type": "alcohol", "percent": 20},
            {"name": "ликер какао", "type": "alcohol", "percent": 20},
            {"name": "сливки", "type": "dairy", "percent": 20},
            {"name": "лед", "type": "other", "percent": 40}
        ],
        "keywords": ["alexander", "александр", "кремовый коктейль"]
    },
    "бобби бернс": {
        "name": "Бобби Бернс",
        "name_en": ["Bobby Burns"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "шотландский виски", "type": "alcohol", "percent": 45},
            {"name": "красный вермут", "type": "alcohol", "percent": 20},
            {"name": "бенедиктин", "type": "alcohol", "percent": 15},
            {"name": "лед", "type": "other", "percent": 20}
        ],
        "keywords": ["bobby burns", "бобби бернс", "виски коктейль"]
    },
    "фиш хаус панч": {
        "name": "Фиш Хаус Панч",
        "name_en": ["Fish House Punch"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 0.2, "fat": 0.1, "carbs": 10.0},
        "ingredients": [
            {"name": "темный ром", "type": "alcohol", "percent": 15},
            {"name": "коньяк", "type": "alcohol", "percent": 5},
            {"name": "персиковый ликер", "type": "alcohol", "percent": 5},
            {"name": "лимонный сок", "type": "fruit", "percent": 5},
            {"name": "лайм", "type": "fruit", "percent": 3},
            {"name": "сахарный сироп", "type": "sugar", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 22},
            {"name": "лед", "type": "other", "percent": 40}
        ],
        "keywords": ["fish house punch", "фиш хаус", "пунш", "старинный рецепт"]
    },
    "вермут коктейль": {
        "name": "Вермут коктейль",
        "name_en": ["Vermouth Cocktail"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "вермут", "type": "alcohol", "percent": 60},
            {"name": "апельсиновый биттер", "type": "alcohol", "percent": 10},
            {"name": "ликер мараскин", "type": "alcohol", "percent": 10},
            {"name": "лед", "type": "other", "percent": 20}
        ],
        "keywords": ["vermouth cocktail", "вермут коктейль", "классика"]
    },
    "драй мартини": {
        "name": "Драй Мартини",
        "name_en": ["Dry Martini"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 1.0},
        "ingredients": [
            {"name": "джин", "type": "alcohol", "percent": 60},
            {"name": "сухой вермут", "type": "alcohol", "percent": 15},
            {"name": "оливки", "type": "vegetable", "percent": 5},
            {"name": "лед", "type": "other", "percent": 20}
        ],
        "keywords": ["dry martini", "мартини", "джин", "оливки", "бонд"]
    },
    "негрони": {
        "name": "Негрони",
        "name_en": ["Negroni"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 170, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "джин", "type": "alcohol", "percent": 25},
            {"name": "красный вермут", "type": "alcohol", "percent": 25},
            {"name": "кампари", "type": "alcohol", "percent": 25},
            {"name": "апельсин", "type": "fruit", "percent": 5},
            {"name": "лед", "type": "other", "percent": 20}
        ],
        "keywords": ["negroni", "негрони", "итальянский коктейль", "горький"]
    },
    "манхэттен": {
        "name": "Манхэттен",
        "name_en": ["Manhattan"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 190, "protein": 0.1, "fat": 0.1, "carbs": 4.0},
        "ingredients": [
            {"name": "виски ржаной", "type": "alcohol", "percent": 50},
            {"name": "красный вермут", "type": "alcohol", "percent": 25},
            {"name": "биттер ангостура", "type": "alcohol", "percent": 5},
            {"name": "вишня", "type": "fruit", "percent": 5},
            {"name": "лед", "type": "other", "percent": 15}
        ],
        "keywords": ["manhattan", "манхэттен", "виски коктейль"]
    },
    "дайкири": {
        "name": "Дайкири",
        "name_en": ["Daiquiri"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 160, "protein": 0.1, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "белый ром", "type": "alcohol", "percent": 40},
            {"name": "лайм", "type": "fruit", "percent": 15},
            {"name": "сахарный сироп", "type": "sugar", "percent": 10},
            {"name": "лед", "type": "other", "percent": 35}
        ],
        "keywords": ["daiquiri", "дайкири", "ром", "лайм"]
    },
    "мохито": {
        "name": "Мохито",
        "name_en": ["Mojito"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 0.2, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "светлый ром", "type": "alcohol", "percent": 15},
            {"name": "мята", "type": "vegetable", "percent": 2},
            {"name": "лайм", "type": "fruit", "percent": 5},
            {"name": "сахарный сироп", "type": "sugar", "percent": 8},
            {"name": "содовая", "type": "liquid", "percent": 40},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["мохито", "mojito", "ром", "мята", "лайм", "коктейль"]
    },
    "маргарита": {
        "name": "Маргарита",
        "name_en": ["Margarita"],
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 70, "protein": 0.2, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "текила", "type": "alcohol", "percent": 20},
            {"name": "трипл сек", "type": "alcohol", "percent": 10},
            {"name": "лайм", "type": "fruit", "percent": 8},
            {"name": "лед", "type": "other", "percent": 62}
        ],
        "keywords": ["margarita", "маргарита", "текила", "трипл сек"]
    },
    "писко сауэр": {
        "name": "Писко Сауэр",
        "name_en": ["Pisco Sour"],
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 1.0, "fat": 0.5, "carbs": 7.0},
        "ingredients": [
            {"name": "писко", "type": "alcohol", "percent": 40},
            {"name": "лимонный сок", "type": "fruit", "percent": 15},
            {"name": "сахарный сироп", "type": "sugar", "percent": 10},
            {"name": "яичный белок", "type": "protein", "percent": 5},
            {"name": "биттер", "type": "alcohol", "percent": 2},
            {"name": "лед", "type": "other", "percent": 28}
        ],
        "keywords": ["pisco sour", "писко сауэр", "перуанский коктейль"]
    },
    
    # ==================== ПОПУЛЯРНЫЕ КОКТЕЙЛИ 2026 ====================
    "эспрессо мартини": {
        "name": "Эспрессо Мартини",
        "name_en": ["Espresso Martini"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 150, "protein": 0.5, "fat": 0.2, "carbs": 8.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 30},
            {"name": "кофейный ликер", "type": "alcohol", "percent": 20},
            {"name": "эспрессо", "type": "other", "percent": 20},
            {"name": "сахарный сироп", "type": "sugar", "percent": 5},
            {"name": "лед", "type": "other", "percent": 25}
        ],
        "keywords": ["espresso martini", "кофейный коктейль", "тренд 2026"]
    },
    "спритц": {
        "name": "Спритц",
        "name_en": ["Spritz"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 55, "protein": 0.1, "fat": 0.1, "carbs": 4.0},
        "ingredients": [
            {"name": "просекко", "type": "alcohol", "percent": 35},
            {"name": "апероль", "type": "alcohol", "percent": 15},
            {"name": "содовая", "type": "liquid", "percent": 15},
            {"name": "апельсин", "type": "fruit", "percent": 5},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["spritz", "спритц", "апероль", "популярный 2026"]
    },
    "водка лемонад": {
        "name": "Водка Лемонад",
        "name_en": ["Vodka Lemonade"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 15},
            {"name": "лимонад", "type": "liquid", "percent": 55},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["vodka lemonade", "водка с лимонадом", "легкий коктейль"]
    },
    "водка сода": {
        "name": "Водка Сода",
        "name_en": ["Vodka Soda"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 35, "protein": 0.1, "fat": 0.1, "carbs": 1.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 15},
            {"name": "содовая", "type": "liquid", "percent": 55},
            {"name": "лайм", "type": "fruit", "percent": 3},
            {"name": "лед", "type": "other", "percent": 27}
        ],
        "keywords": ["vodka soda", "водка с содовой", "низкокалорийный"]
    },
    "виски энд кола": {
        "name": "Виски с колой",
        "name_en": ["Whisky and Coke"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 55, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "виски", "type": "alcohol", "percent": 15},
            {"name": "кола", "type": "liquid", "percent": 55},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["whisky coke", "виски с колой", "классика"]
    },
    "ром энд кола": {
        "name": "Ром с колой",
        "name_en": ["Rum and Coke"],
        "category": "drink",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 50, "protein": 0.1, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "ром", "type": "alcohol", "percent": 15},
            {"name": "кола", "type": "liquid", "percent": 55},
            {"name": "лайм", "type": "fruit", "percent": 3},
            {"name": "лед", "type": "other", "percent": 27}
        ],
        "keywords": ["rum and coke", "ром с колой", "куба либре"]
    },
    "френч мартини": {
        "name": "Френч Мартини",
        "name_en": ["French Martini"],
        "category": "drink",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 0.1, "fat": 0.1, "carbs": 8.0},
        "ingredients": [
            {"name": "водка", "type": "alcohol", "percent": 30},
            {"name": "малиновый ликер", "type": "alcohol", "percent": 15},
            {"name": "ананасовый сок", "type": "fruit", "percent": 25},
            {"name": "лед", "type": "other", "percent": 30}
        ],
        "keywords": ["french martini", "французский мартини", "малиновый"]
    }
}

# =============================================================================
# 🔍 ФУНКЦИИ ПОИСКА
# =============================================================================

def _similarity(a: str, b: str) -> float:
    """Вычисляет схожесть строк (0.0–1.0)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_ai_dish_name(dish_name: str) -> str:
    """
    Нормализует название блюда от ИИ для поиска в базе.
    """
    if not dish_name:
        return ""
    
    dish_lower = dish_name.lower().strip()
    
    # Прямой поиск по ключам
    if dish_lower in COMPOSITE_DISHES:
        return dish_lower
    
    # Поиск по английским названиям
    for key, dish_data in COMPOSITE_DISHES.items():
        name_en_list = dish_data.get("name_en", [])
        for name_en in name_en_list:
            if name_en.lower() == dish_lower or dish_lower in name_en.lower():
                logger.info(f"🔍 Найдено совпадение по EN: '{dish_name}' → '{key}'")
                return key
    
    # Поиск по ключевым словам
    for key, dish_data in COMPOSITE_DISHES.items():
        keywords = dish_data.get("keywords", [])
        for keyword in keywords:
            if keyword in dish_lower:
                logger.info(f"🔍 Найдено совпадение по keyword: '{dish_name}' → '{key}'")
                return key
    
    # Fuzzy-поиск по русскому названию
    best_match = None
    best_score = 0.5
    for key, dish_data in COMPOSITE_DISHES.items():
        name_ru = dish_data.get("name", "").lower()
        score = _similarity(dish_lower, name_ru)
        if score > best_score:
            best_score = score
            best_match = key
    
    if best_match:
        logger.info(f"🔍 Fuzzy-совпадение: '{dish_name}' → '{best_match}' (score: {best_score:.2f})")
        return best_match
    
    return ""

def find_matching_dishes(
    dish_name: str,
    ai_ingredients: list = None,
    threshold: float = 0.3
) -> list:
    """
    Улучшенный поиск готовых блюд в COMPOSITE_DISHES.
    ✅ Учитывает английские названия
    ✅ Улучшенный scoring
    """
    if not dish_name and not ai_ingredients:
        return []
    
    dish_name_lower = dish_name.lower().strip() if dish_name else ""
    
    logger.info(f"🔍 Поиск блюд для '{dish_name}'")
    
    matches = []
    
    for key, dish_data in COMPOSITE_DISHES.items():
        dish_display_name = dish_data.get('name', key)
        
        # Score по названию
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
            logger.info(f"✅ Найдено: {dish_display_name} (score: {name_score:.2f}, key: '{key}')")
    
    # Сортируем по score
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:5]

def get_dish_ingredients(dish_name: str, total_weight: int = 300) -> list:
    """Возвращает ингредиенты блюда с рассчитанными весами."""
    dish_name_lower = dish_name.lower().strip()
    
    # Ищем блюдо
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
    
    # Рассчитываем веса
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
    """Рассчитывает КБЖУ для готового блюда."""
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
    
    # Если есть nutrition_per_100 — используем его
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
    
    # Иначе считаем по ингредиентам
    ingredients = dish_data.get('ingredients', [])
    total_calories = total_protein = total_fat = total_carbs = 0
    
    for ing in ingredients:
        ing_name = ing.get('name', '')
        percent = ing.get('percent', 0)
        ing_weight = int(total_weight * percent / 100)
        
        # Ищем в LOCAL_FOOD_DB
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
    Определяет известное блюдо по списку ингредиентов (на английском) и стилю приготовления.
    Использует базу COMPOSITE_DISHES и переводчик AI_TO_DB_MAPPING.
    Возвращает название блюда (на русском) или None.
    """
    # Переводим английские названия в русские
    ingredient_names_ru = set()
    for name_en in ingredient_names_en:
        name_clean = name_en.lower().replace('grilled ', '').replace('fried ', '').replace('boiled ', '')
        name_clean = name_clean.replace('baked ', '').replace('roasted ', '').replace('steamed ', '')
        name_clean = name_clean.replace('raw ', '').replace('fresh ', '')
        # Ищем перевод
        ru = AI_TO_DB_MAPPING.get(name_clean)
        if ru:
            ingredient_names_ru.add(ru)
        else:
            # Если нет перевода, добавляем оригинал (возможно, он уже на русском)
            ingredient_names_ru.add(name_clean)

    logger.info(f"🔍 Поиск блюда по ингредиентам: {ingredient_names_ru}")

    best_match = None
    best_score = 0.0

    for dish_key, dish_data in COMPOSITE_DISHES.items():
        dish_ingredients = dish_data.get('ingredients', [])
        dish_names = [ing['name'].lower() for ing in dish_ingredients]
        dish_set = set(dish_names)

        # Жаккаровское сходство: пересечение / объединение
        intersection = ingredient_names_ru & dish_set
        union = ingredient_names_ru | dish_set
        if not union:
            continue
        score = len(intersection) / len(union)

        # Небольшой бонус за совпадение стиля приготовления
        if dish_data.get('prep_style') == prep_style:
            score += 0.05

        if score > best_score and score >= 0.3:  # порог 30%
            best_score = score
            best_match = dish_data['name']

    if best_match:
        logger.info(f"🎯 Идентифицировано блюдо по ингредиентам: {best_match} (score: {best_score:.2f})")
        return best_match

    return None

def find_matching_dishes_by_ingredients(ingredient_names_en: List[str], threshold: float = 0.4) -> List[Dict]:
    """
    Ищет блюда, которые содержат указанные ингредиенты (названия даны на английском).
    Возвращает список блюд с оценкой совпадения.
    """
    # Переводим английские названия в русские
    ingredient_names_ru = set()
    for name_en in ingredient_names_en:
        name_clean = name_en.lower().replace('grilled ', '').replace('fried ', '').replace('boiled ', '')
        name_clean = name_clean.replace('baked ', '').replace('roasted ', '').replace('steamed ', '')
        name_clean = name_clean.replace('raw ', '').replace('fresh ', '')
        # Ищем перевод
        ru = AI_TO_DB_MAPPING.get(name_clean)
        if ru:
            ingredient_names_ru.add(ru.lower())
        else:
            # Если нет перевода, добавляем как есть (возможно, уже русское)
            ingredient_names_ru.add(name_clean)

    logger.info(f"🔍 Поиск блюд по ингредиентам (рус): {ingredient_names_ru}")

    matches = []
    for dish_key, dish_data in COMPOSITE_DISHES.items():
        dish_ingredients = dish_data.get('ingredients', [])
        dish_ingredient_names = {ing['name'].lower() for ing in dish_ingredients}

        # Жаккаровское сходство: пересечение / объединение
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
    logger.info(f"🔍 Найдено {len(matches)} совпадений по ингредиентам")
    return matches
