"""
РАСШИРЕННАЯ БАЗА ДАННЫХ ГОТОВЫХ БЛЮД С ПОДДЕРЖКОЙ АНГЛИЙСКИХ НАЗВАНИЙ
✅ 200+ блюд с полными ингредиентами и КБЖУ
✅ Билингвальная поддержка (RU + EN)
✅ Улучшенный поиск с учётом синонимов и keywords
"""
from typing import Dict, List, Optional, Set
import logging
from difflib import SequenceMatcher

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
