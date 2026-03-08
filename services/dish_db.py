"""
РАСШИРЕННАЯ БАЗА ДАННЫХ ГОТОВЫХ БЛЮД
Содержит информацию о КБЖУ на 100 грамм (nutrition_per_100).
Структура полностью сохранена: название, категория, вес порции, ингредиенты в процентах.
"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# 🍽️ БАЗА ГОТОВЫХ БЛЮД С ПОЛНЫМИ ИНГРЕДИЕНТАМИ И КБЖУ НА 100 Г
# =============================================================================

COMPOSITE_DISHES = {
    # =========================================================================
    # 🥗 САЛАТЫ
    # =========================================================================
    # --- Классические салаты ---
    "капрезе": {
        "name": "Капрезе",
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 280, "protein": 10.5, "fat": 24.0, "carbs": 4.5},
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 40},
            {"name": "моцарелла", "type": "dairy", "percent": 40},
            {"name": "базилик", "type": "herb", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 15}
        ]
    },
    "салат цезарь": {
        "name": "Цезарь с курицей",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 185, "protein": 15.0, "fat": 12.0, "carbs": 5.5},
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "салат романо", "type": "vegetable", "percent": 35},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "сухарики", "type": "carb", "percent": 10},
            {"name": "соус цезарь", "type": "sauce", "percent": 15}
        ]
    },
    "греческий салат": {
        "name": "Греческий салат",
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
        ]
    },
    "салат оливье": {
        "name": "Оливье",
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
        ]
    },
    "селедка под шубой": {
        "name": "Селедка под шубой",
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
        ]
    },
    "винегрет": {
        "name": "Винегрет",
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
        ]
    },
    "мимоза": {
        "name": "Мимоза",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 230, "protein": 12.0, "fat": 18.0, "carbs": 5.0},
        "ingredients": [
            {"name": "рыбные консервы", "type": "protein", "percent": 30},
            {"name": "яйцо куриное", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ]
    },
    "крабовый салат": {
        "name": "Крабовый салат",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 7.0, "fat": 9.0, "carbs": 10.0},
        "ingredients": [
            {"name": "крабовые палочки", "type": "protein", "percent": 30},
            {"name": "кукуруза консервированная", "type": "vegetable", "percent": 25},
            {"name": "яйцо куриное", "type": "protein", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 20},
            {"name": "майонез", "type": "sauce", "percent": 5}
        ]
    },
    "цезарь с креветками": {
        "name": "Цезарь с креветками",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 165, "protein": 16.0, "fat": 9.0, "carbs": 4.5},
        "ingredients": [
            {"name": "креветки", "type": "protein", "percent": 35},
            {"name": "салат айсберг", "type": "vegetable", "percent": 35},
            {"name": "помидоры черри", "type": "vegetable", "percent": 10},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "соус цезарь", "type": "sauce", "percent": 10}
        ]
    },
    "салат с тунцом": {
        "name": "Салат с тунцом",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 140, "protein": 18.0, "fat": 6.0, "carbs": 4.0},
        "ingredients": [
            {"name": "тунец консервированный", "type": "protein", "percent": 40},
            {"name": "листья салата", "type": "vegetable", "percent": 25},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 10},
            {"name": "яйцо куриное", "type": "protein", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "салат нисуаз": {
        "name": "Нисуаз",
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 160, "protein": 14.0, "fat": 9.0, "carbs": 5.0},
        "ingredients": [
            {"name": "тунец", "type": "protein", "percent": 25},
            {"name": "фасоль стручковая", "type": "vegetable", "percent": 20},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "оливки", "type": "vegetable", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "салат с авокадо и креветками": {
        "name": "Салат с авокадо и креветками",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 16.0, "carbs": 5.0},
        "ingredients": [
            {"name": "креветки", "type": "protein", "percent": 35},
            {"name": "авокадо", "type": "fruit", "percent": 30},
            {"name": "помидоры черри", "type": "vegetable", "percent": 20},
            {"name": "руккола", "type": "vegetable", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "салат с курицей и ананасом": {
        "name": "Салат с курицей и ананасом",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 170, "protein": 16.0, "fat": 8.0, "carbs": 10.0},
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 40},
            {"name": "ананас консервированный", "type": "fruit", "percent": 25},
            {"name": "сыр твердый", "type": "dairy", "percent": 15},
            {"name": "яйцо куриное", "type": "protein", "percent": 10},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ]
    },
    "коул слоу": {
        "name": "Коул слоу",
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 2.0, "fat": 11.0, "carbs": 8.0},
        "ingredients": [
            {"name": "капуста белокочанная", "type": "vegetable", "percent": 50},
            {"name": "морковь", "type": "vegetable", "percent": 20},
            {"name": "йогурт греческий", "type": "dairy", "percent": 20},
            {"name": "майонез", "type": "sauce", "percent": 5},
            {"name": "горчица", "type": "sauce", "percent": 5}
        ]
    },
    "табуле": {
        "name": "Табуле",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 4.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "булгур", "type": "carb", "percent": 40},
            {"name": "петрушка", "type": "herb", "percent": 25},
            {"name": "помидоры", "type": "vegetable", "percent": 20},
            {"name": "мята", "type": "herb", "percent": 5},
            {"name": "лук зеленый", "type": "vegetable", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "салат с фетой и арбузом": {
        "name": "Салат с фетой и арбузом",
        "category": "salad",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 95, "protein": 3.5, "fat": 6.0, "carbs": 7.0},
        "ingredients": [
            {"name": "арбуз", "type": "fruit", "percent": 50},
            {"name": "фета", "type": "dairy", "percent": 25},
            {"name": "руккола", "type": "vegetable", "percent": 15},
            {"name": "мята", "type": "herb", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "салат вальдорф": {
        "name": "Вальдорф",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 4.0, "fat": 15.0, "carbs": 13.0},
        "ingredients": [
            {"name": "яблоко", "type": "fruit", "percent": 35},
            {"name": "сельдерей стебель", "type": "vegetable", "percent": 30},
            {"name": "грецкий орех", "type": "nut", "percent": 20},
            {"name": "виноград", "type": "fruit", "percent": 10},
            {"name": "йогурт", "type": "dairy", "percent": 5}
        ]
    },
    "салат с печенью трески": {
        "name": "Салат с печенью трески",
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 320, "protein": 10.0, "fat": 30.0, "carbs": 4.0},
        "ingredients": [
            {"name": "печень трески", "type": "protein", "percent": 35},
            {"name": "яйцо куриное", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 15},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 5}
        ]
    },
    "салат с копченой курицей": {
        "name": "Салат с копченой курицей",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 200, "protein": 18.0, "fat": 13.0, "carbs": 5.0},
        "ingredients": [
            {"name": "курица копченая", "type": "protein", "percent": 40},
            {"name": "перец болгарский", "type": "vegetable", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "кукуруза", "type": "vegetable", "percent": 15},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ]
    },
    "салат с семгой слабосоленой": {
        "name": "Салат с семгой",
        "category": "salad",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 210, "protein": 16.0, "fat": 15.0, "carbs": 4.0},
        "ingredients": [
            {"name": "семга слабосоленая", "type": "protein", "percent": 35},
            {"name": "авокадо", "type": "fruit", "percent": 25},
            {"name": "огурцы", "type": "vegetable", "percent": 20},
            {"name": "руккола", "type": "vegetable", "percent": 15},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "салат с курицей и грибами": {
        "name": "Салат с курицей и грибами",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 16.0, "fat": 11.0, "carbs": 5.0},
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "шампиньоны", "type": "vegetable", "percent": 30},
            {"name": "яйцо куриное", "type": "protein", "percent": 15},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 5}
        ]
    },
    "салат с языком": {
        "name": "Салат с языком",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 16.0, "fat": 15.0, "carbs": 4.0},
        "ingredients": [
            {"name": "язык говяжий", "type": "protein", "percent": 35},
            {"name": "яйцо куриное", "type": "protein", "percent": 20},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ]
    },
    "салат с фасолью": {
        "name": "Салат с фасолью",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 7.0, "carbs": 14.0},
        "ingredients": [
            {"name": "фасоль красная", "type": "protein", "percent": 40},
            {"name": "кукуруза", "type": "vegetable", "percent": 20},
            {"name": "перец болгарский", "type": "vegetable", "percent": 15},
            {"name": "лук репчатый", "type": "vegetable", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "салат с курицей и апельсином": {
        "name": "Салат с курицей и апельсином",
        "category": "salad",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 15.0, "fat": 6.0, "carbs": 9.0},
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 35},
            {"name": "апельсин", "type": "fruit", "percent": 30},
            {"name": "листья салата", "type": "vegetable", "percent": 20},
            {"name": "грецкий орех", "type": "nut", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "салат с сыром и чесноком": {
        "name": "Салат с сыром и чесноком",
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 260, "protein": 12.0, "fat": 22.0, "carbs": 3.0},
        "ingredients": [
            {"name": "сыр твердый", "type": "dairy", "percent": 60},
            {"name": "яйцо куриное", "type": "protein", "percent": 20},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 15}
        ]
    },
    "салат с редиской и огурцом": {
        "name": "Весенний салат",
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 70, "protein": 2.0, "fat": 4.5, "carbs": 5.5},
        "ingredients": [
            {"name": "редис", "type": "vegetable", "percent": 35},
            {"name": "огурцы", "type": "vegetable", "percent": 35},
            {"name": "лук зеленый", "type": "vegetable", "percent": 15},
            {"name": "укроп", "type": "herb", "percent": 10},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ]
    },
    "салат с капустой и морковью": {
        "name": "Салат из капусты",
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 80, "protein": 1.8, "fat": 4.5, "carbs": 8.5},
        "ingredients": [
            {"name": "капуста белокочанная", "type": "vegetable", "percent": 70},
            {"name": "морковь", "type": "vegetable", "percent": 20},
            {"name": "лук репчатый", "type": "vegetable", "percent": 5},
            {"name": "масло подсолнечное", "type": "fat", "percent": 5}
        ]
    },
    "салат с крапивой и яйцом": {
        "name": "Салат с крапивой",
        "category": "salad",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 110, "protein": 6.0, "fat": 8.0, "carbs": 4.0},
        "ingredients": [
            {"name": "крапива", "type": "vegetable", "percent": 40},
            {"name": "яйцо куриное", "type": "protein", "percent": 30},
            {"name": "лук зеленый", "type": "vegetable", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 15}
        ]
    },

    # =========================================================================
    # 🍲 СУПЫ
    # =========================================================================
    # --- Первые блюда ---
    "борщ": {
        "name": "Борщ",
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
        ]
    },
    "борщ украинский": {
        "name": "Борщ украинский",
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
        ]
    },
    "щи": {
        "name": "Щи",
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
        ]
    },
    "щи зеленые": {
        "name": "Щи зеленые",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 50, "protein": 3.0, "fat": 2.0, "carbs": 5.0},
        "ingredients": [
            {"name": "щавель", "type": "vegetable", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "мясо", "type": "protein", "percent": 12},
            {"name": "сметана", "type": "dairy", "percent": 3},
            {"name": "вода", "type": "liquid", "percent": 27}
        ]
    },
    "рассольник": {
        "name": "Рассольник",
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
        ]
    },
    "солянка мясная": {
        "name": "Солянка мясная",
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
        ]
    },
    "солянка сборная": {
        "name": "Солянка сборная мясная",
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 100, "protein": 8.0, "fat": 6.0, "carbs": 4.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "свинина", "type": "protein", "percent": 10},
            {"name": "курица", "type": "protein", "percent": 5},
            {"name": "ветчина", "type": "protein", "percent": 5},
            {"name": "сосиски", "type": "protein", "percent": 5},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "оливки", "type": "vegetable", "percent": 5},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 27}
        ]
    },
    "солянка грибная": {
        "name": "Солянка грибная",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 60, "protein": 3.0, "fat": 2.5, "carbs": 6.0},
        "ingredients": [
            {"name": "грибы", "type": "vegetable", "percent": 25},
            {"name": "капуста квашеная", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 30}
        ]
    },
    "уха": {
        "name": "Уха",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 4.5, "fat": 1.5, "carbs": 3.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 47}
        ]
    },
    "уха царская": {
        "name": "Уха царская",
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 65, "protein": 7.0, "fat": 2.5, "carbs": 3.5},
        "ingredients": [
            {"name": "семга", "type": "protein", "percent": 15},
            {"name": "судак", "type": "protein", "percent": 10},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 47}
        ]
    },
    "куриный суп": {
        "name": "Суп куриный",
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
        ]
    },
    "суп с фрикадельками": {
        "name": "Суп с фрикадельками",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 55, "protein": 4.0, "fat": 2.8, "carbs": 4.0},
        "ingredients": [
            {"name": "фрикадельки", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 18},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вермишель", "type": "carb", "percent": 4},
            {"name": "вода", "type": "liquid", "percent": 45}
        ]
    },
    "грибной суп": {
        "name": "Суп грибной",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 40, "protein": 2.0, "fat": 1.8, "carbs": 4.0},
        "ingredients": [
            {"name": "грибы", "type": "vegetable", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 47}
        ]
    },
    "суп гороховый": {
        "name": "Суп гороховый",
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
        ]
    },
    "суп с чечевицей": {
        "name": "Суп чечевичный",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 75, "protein": 5.0, "fat": 1.8, "carbs": 10.0},
        "ingredients": [
            {"name": "чечевица", "type": "protein", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "томаты", "type": "vegetable", "percent": 7},
            {"name": "вода", "type": "liquid", "percent": 50}
        ]
    },
    "сырный суп": {
        "name": "Суп сырный",
        "category": "soup",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 85, "protein": 4.5, "fat": 5.5, "carbs": 4.0},
        "ingredients": [
            {"name": "сыр плавленый", "type": "dairy", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 18},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "курица", "type": "protein", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 44}
        ]
    },
    "том ям": {
        "name": "Том Ям",
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 55, "protein": 4.0, "fat": 2.5, "carbs": 4.0},
        "ingredients": [
            {"name": "креветки", "type": "protein", "percent": 15},
            {"name": "курица", "type": "protein", "percent": 10},
            {"name": "грибы", "type": "vegetable", "percent": 15},
            {"name": "томаты", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 45}
        ]
    },
    "минестроне": {
        "name": "Минестроне",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 2.0, "fat": 1.2, "carbs": 7.0},
        "ingredients": [
            {"name": "кабачки", "type": "vegetable", "percent": 12},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "фасоль стручковая", "type": "vegetable", "percent": 8},
            {"name": "горошек", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 52}
        ]
    },
    "гаспачо": {
        "name": "Гаспачо",
        "category": "soup",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 1.5, "fat": 2.8, "carbs": 5.0},
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 60},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "перец болгарский", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 5}
        ]
    },
    "окрошка": {
        "name": "Окрошка",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 60, "protein": 3.5, "fat": 3.0, "carbs": 4.5},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "яйцо куриное", "type": "protein", "percent": 10},
            {"name": "колбаса", "type": "protein", "percent": 12},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "редис", "type": "vegetable", "percent": 8},
            {"name": "лук зеленый", "type": "vegetable", "percent": 5},
            {"name": "укроп", "type": "herb", "percent": 3},
            {"name": "квас", "type": "liquid", "percent": 32}
        ]
    },
    "окрошка на кефире": {
        "name": "Окрошка на кефире",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 70, "protein": 4.5, "fat": 3.5, "carbs": 5.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "яйцо куриное", "type": "protein", "percent": 10},
            {"name": "курица", "type": "protein", "percent": 12},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "редис", "type": "vegetable", "percent": 8},
            {"name": "лук зеленый", "type": "vegetable", "percent": 5},
            {"name": "укроп", "type": "herb", "percent": 3},
            {"name": "кефир", "type": "dairy", "percent": 32}
        ]
    },
    "свекольник": {
        "name": "Свекольник",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 45, "protein": 2.0, "fat": 1.8, "carbs": 5.5},
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 25},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "яйцо куриное", "type": "protein", "percent": 8},
            {"name": "лук зеленый", "type": "vegetable", "percent": 5},
            {"name": "укроп", "type": "herb", "percent": 3},
            {"name": "кефир", "type": "dairy", "percent": 44}
        ]
    },
    "харчо": {
        "name": "Харчо",
        "category": "soup",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 85, "protein": 6.0, "fat": 4.0, "carbs": 6.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 20},
            {"name": "рис", "type": "carb", "percent": 12},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "томаты", "type": "vegetable", "percent": 8},
            {"name": "вода", "type": "liquid", "percent": 50}
        ]
    },
    "лагман": {
        "name": "Лагман",
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 95, "protein": 6.0, "fat": 4.5, "carbs": 8.0},
        "ingredients": [
            {"name": "мясо", "type": "protein", "percent": 18},
            {"name": "лапша", "type": "carb", "percent": 22},
            {"name": "перец болгарский", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "морковь", "type": "vegetable", "percent": 6},
            {"name": "томаты", "type": "vegetable", "percent": 6},
            {"name": "вода", "type": "liquid", "percent": 32}
        ]
    },
    "шурпа": {
        "name": "Шурпа",
        "category": "soup",
        "default_weight": 400,
        "nutrition_per_100": {"calories": 70, "protein": 5.0, "fat": 3.5, "carbs": 4.5},
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 18},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "вода", "type": "liquid", "percent": 44}
        ]
    },
    "суп-пюре из тыквы": {
        "name": "Суп-пюре из тыквы",
        "category": "soup",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 55, "protein": 1.5, "fat": 2.5, "carbs": 7.0},
        "ingredients": [
            {"name": "тыква", "type": "vegetable", "percent": 40},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сливки", "type": "dairy", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 35}
        ]
    },
    "суп-пюре грибной": {
        "name": "Суп-пюре грибной",
        "category": "soup",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 60, "protein": 3.0, "fat": 3.0, "carbs": 5.0},
        "ingredients": [
            {"name": "шампиньоны", "type": "vegetable", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "сливки", "type": "dairy", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 37}
        ]
    },
    "суп-пюре из брокколи": {
        "name": "Суп-пюре из брокколи",
        "category": "soup",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 45, "protein": 2.5, "fat": 2.0, "carbs": 4.5},
        "ingredients": [
            {"name": "брокколи", "type": "vegetable", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "сливки", "type": "dairy", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 37}
        ]
    },

    # =========================================================================
    # 🍲 ВТОРЫЕ БЛЮДА
    # =========================================================================
    # --- Мясные блюда ---
    "котлеты": {
        "name": "Котлеты",
        "category": "main",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 240, "protein": 16.0, "fat": 18.0, "carbs": 6.0},
        "ingredients": [
            {"name": "фарш мясной", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "хлеб", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "котлеты куриные": {
        "name": "Котлеты куриные",
        "category": "main",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 170, "protein": 20.0, "fat": 9.0, "carbs": 4.0},
        "ingredients": [
            {"name": "куриный фарш", "type": "protein", "percent": 85},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "котлеты рыбные": {
        "name": "Котлеты рыбные",
        "category": "main",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 150, "protein": 16.0, "fat": 8.0, "carbs": 4.0},
        "ingredients": [
            {"name": "рыбный фарш", "type": "protein", "percent": 85},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "котлеты по-киевски": {
        "name": "Котлеты по-киевски",
        "category": "main",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 320, "protein": 18.0, "fat": 27.0, "carbs": 3.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 65},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сухари", "type": "carb", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "шницель": {
        "name": "Шницель",
        "category": "main",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 280, "protein": 22.0, "fat": 20.0, "carbs": 4.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 80},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сухари", "type": "carb", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "отбивная": {
        "name": "Отбивная",
        "category": "main",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 260, "protein": 20.0, "fat": 19.0, "carbs": 2.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 85},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "бефстроганов": {
        "name": "Бефстроганов",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 180, "protein": 18.0, "fat": 11.0, "carbs": 4.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 60},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 15},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "гуляш": {
        "name": "Гуляш",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 12.0, "carbs": 5.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 60},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "азу": {
        "name": "Азу",
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 165, "protein": 14.0, "fat": 10.0, "carbs": 6.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 45},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 7}
        ]
    },
    "жаркое по-домашнему": {
        "name": "Жаркое по-домашнему",
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 175, "protein": 12.0, "fat": 10.0, "carbs": 10.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "плов": {
        "name": "Плов",
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 10.0, "carbs": 19.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "баранина", "type": "protein", "percent": 30},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "плов с курицей": {
        "name": "Плов с курицей",
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 160, "protein": 12.0, "fat": 5.0, "carbs": 18.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 45},
            {"name": "курица", "type": "protein", "percent": 30},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10}
        ]
    },
    "плов с говядиной": {
        "name": "Плов с говядиной",
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 14.0, "fat": 8.0, "carbs": 18.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 45},
            {"name": "говядина", "type": "protein", "percent": 30},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10}
        ]
    },
    "плов со свининой": {
        "name": "Плов со свининой",
        "category": "main",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 11.0, "carbs": 18.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 45},
            {"name": "свинина", "type": "protein", "percent": 30},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10}
        ]
    },
    "мясо по-французски": {
        "name": "Мясо по-французски",
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 250, "protein": 16.0, "fat": 18.0, "carbs": 5.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 45},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 15},
            {"name": "майонез", "type": "sauce", "percent": 10}
        ]
    },
    "мясо по-французски с грибами": {
        "name": "Мясо по-французски с грибами",
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 15.0, "fat": 15.0, "carbs": 6.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 40},
            {"name": "шампиньоны", "type": "vegetable", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 10},
            {"name": "майонез", "type": "sauce", "percent": 5}
        ]
    },
    "курица запеченная": {
        "name": "Курица запеченная",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 24.0, "fat": 10.0, "carbs": 1.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 95},
            {"name": "специи", "type": "other", "percent": 2},
            {"name": "масло", "type": "fat", "percent": 3}
        ]
    },
    "курица гриль": {
        "name": "Курица гриль",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 185, "protein": 24.0, "fat": 9.5, "carbs": 1.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 95},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "куриные крылышки": {
        "name": "Куриные крылышки",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 240, "protein": 20.0, "fat": 17.0, "carbs": 2.0},
        "ingredients": [
            {"name": "крылья куриные", "type": "protein", "percent": 90},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "куриные ножки": {
        "name": "Куриные ножки",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 200, "protein": 20.0, "fat": 13.0, "carbs": 1.0},
        "ingredients": [
            {"name": "куриные ножки", "type": "protein", "percent": 95},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "куриное филе": {
        "name": "Куриное филе",
        "category": "main",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 140, "protein": 26.0, "fat": 3.5, "carbs": 1.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 95},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "куриная грудка": {
        "name": "Куриная грудка",
        "category": "main",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 135, "protein": 27.0, "fat": 2.5, "carbs": 1.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 100}
        ]
    },
    "куриное филе в сливочном соусе": {
        "name": "Куриное филе в сливочном соусе",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 185, "protein": 18.0, "fat": 11.0, "carbs": 3.5},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 60},
            {"name": "сливки", "type": "dairy", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "курица в кисло-сладком соусе": {
        "name": "Курица в кисло-сладком соусе",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 16.0, "fat": 8.0, "carbs": 15.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 50},
            {"name": "перец болгарский", "type": "vegetable", "percent": 15},
            {"name": "ананас", "type": "fruit", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "соус", "type": "sauce", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "гуляш из курицы": {
        "name": "Гуляш из курицы",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 16.0, "fat": 7.0, "carbs": 5.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 60},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "куриное рагу": {
        "name": "Куриное рагу",
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 145, "protein": 15.0, "fat": 7.0, "carbs": 6.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 45},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "горошек", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "говядина тушеная": {
        "name": "Говядина тушеная",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 22.0, "fat": 11.0, "carbs": 2.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "говядина с черносливом": {
        "name": "Говядина с черносливом",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 20.0, "fat": 10.0, "carbs": 11.0},
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 70},
            {"name": "чернослив", "type": "fruit", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "свинина тушеная": {
        "name": "Свинина тушеная",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 250, "protein": 18.0, "fat": 19.0, "carbs": 2.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "свинина с грибами": {
        "name": "Свинина с грибами",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 230, "protein": 17.0, "fat": 16.0, "carbs": 4.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 60},
            {"name": "шампиньоны", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "сметана", "type": "dairy", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "свинина с ананасом": {
        "name": "Свинина с ананасом",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 15.0, "fat": 12.0, "carbs": 12.0},
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 60},
            {"name": "ананас", "type": "fruit", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 5},
            {"name": "соус", "type": "sauce", "percent": 5}
        ]
    },
    "баранина тушеная": {
        "name": "Баранина тушеная",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 230, "protein": 20.0, "fat": 16.0, "carbs": 2.0},
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "люля-кебаб": {
        "name": "Люля-кебаб",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 250, "protein": 18.0, "fat": 19.0, "carbs": 2.0},
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 70},
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "зелень", "type": "herb", "percent": 5}
        ]
    },
    "чахохбили": {
        "name": "Чахохбили",
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 165, "protein": 18.0, "fat": 9.0, "carbs": 4.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 60},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "перец", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "сациви": {
        "name": "Сациви",
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 18.0, "fat": 15.0, "carbs": 5.0},
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 50},
            {"name": "грецкий орех", "type": "nut", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "other", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 15}
        ]
    },

    # --- Рыбные блюда ---
    "рыба жареная": {
        "name": "Рыба жареная",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 20.0, "fat": 10.0, "carbs": 2.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 85},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "рыба запеченная": {
        "name": "Рыба запеченная",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 150, "protein": 22.0, "fat": 6.0, "carbs": 2.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 90},
            {"name": "лимон", "type": "fruit", "percent": 3},
            {"name": "масло", "type": "fat", "percent": 5},
            {"name": "специи", "type": "other", "percent": 2}
        ]
    },
    "рыба тушеная": {
        "name": "Рыба тушеная",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 140, "protein": 18.0, "fat": 6.0, "carbs": 4.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 70},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5}
        ]
    },
    "рыба в кляре": {
        "name": "Рыба в кляре",
        "category": "main",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 210, "protein": 16.0, "fat": 12.0, "carbs": 11.0},
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 60},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "семга запеченная": {
        "name": "Семга запеченная",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 200, "protein": 22.0, "fat": 12.0, "carbs": 1.0},
        "ingredients": [
            {"name": "семга", "type": "protein", "percent": 95},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "семга на пару": {
        "name": "Семга на пару",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 170, "protein": 22.0, "fat": 9.0, "carbs": 1.0},
        "ingredients": [
            {"name": "семга", "type": "protein", "percent": 100}
        ]
    },
    "судак запеченный": {
        "name": "Судак запеченный",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 21.0, "fat": 3.5, "carbs": 1.0},
        "ingredients": [
            {"name": "судак", "type": "protein", "percent": 95},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "треска запеченная": {
        "name": "Треска запеченная",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 110, "protein": 22.0, "fat": 2.0, "carbs": 1.0},
        "ingredients": [
            {"name": "треска", "type": "protein", "percent": 95},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "скумбрия запеченная": {
        "name": "Скумбрия запеченная",
        "category": "main",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 200, "protein": 20.0, "fat": 13.0, "carbs": 1.0},
        "ingredients": [
            {"name": "скумбрия", "type": "protein", "percent": 95},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "котлеты рыбные": {
        "name": "Котлеты рыбные",
        "category": "main",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 160, "protein": 16.0, "fat": 9.0, "carbs": 5.0},
        "ingredients": [
            {"name": "рыбный фарш", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "хлеб", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "рыбные палочки": {
        "name": "Рыбные палочки",
        "category": "main",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 210, "protein": 14.0, "fat": 12.0, "carbs": 13.0},
        "ingredients": [
            {"name": "рыбный фарш", "type": "protein", "percent": 60},
            {"name": "сухари", "type": "carb", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },

    # --- Блюда из птицы ---
    "утка запеченная": {
        "name": "Утка запеченная",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 270, "protein": 20.0, "fat": 20.0, "carbs": 1.0},
        "ingredients": [
            {"name": "утка", "type": "protein", "percent": 95},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "утка с яблоками": {
        "name": "Утка с яблоками",
        "category": "main",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 230, "protein": 16.0, "fat": 16.0, "carbs": 6.0},
        "ingredients": [
            {"name": "утка", "type": "protein", "percent": 70},
            {"name": "яблоко", "type": "fruit", "percent": 25},
            {"name": "мед", "type": "carb", "percent": 5}
        ]
    },
    "индейка запеченная": {
        "name": "Индейка запеченная",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 25.0, "fat": 6.0, "carbs": 1.0},
        "ingredients": [
            {"name": "индейка", "type": "protein", "percent": 95},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "индейка тушеная": {
        "name": "Индейка тушеная",
        "category": "main",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 150, "protein": 22.0, "fat": 6.0, "carbs": 2.0},
        "ingredients": [
            {"name": "индейка", "type": "protein", "percent": 70},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "котлеты из индейки": {
        "name": "Котлеты из индейки",
        "category": "main",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 160, "protein": 20.0, "fat": 8.0, "carbs": 3.0},
        "ingredients": [
            {"name": "фарш индейки", "type": "protein", "percent": 85},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },

    # =========================================================================
    # 🍝 ПАСТА И МАКАРОННЫЕ ИЗДЕЛИЯ
    # =========================================================================
    "паста карбонара": {
        "name": "Паста Карбонара",
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 280, "protein": 14.0, "fat": 16.0, "carbs": 20.0},
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 45},
            {"name": "бекон", "type": "protein", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "сливки", "type": "dairy", "percent": 10}
        ]
    },
    "паста болоньезе": {
        "name": "Паста Болоньезе",
        "category": "pasta",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 40},
            {"name": "фарш мясной", "type": "protein", "percent": 25},
            {"name": "томатный соус", "type": "sauce", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5}
        ]
    },
    "паста с курицей": {
        "name": "Паста с курицей",
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 190, "protein": 14.0, "fat": 7.0, "carbs": 18.0},
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 50},
            {"name": "куриное филе", "type": "protein", "percent": 25},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "паста с грибами": {
        "name": "Паста с грибами",
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 170, "protein": 8.0, "fat": 6.0, "carbs": 22.0},
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 55},
            {"name": "шампиньоны", "type": "vegetable", "percent": 25},
            {"name": "сливки", "type": "dairy", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "паста с морепродуктами": {
        "name": "Паста с морепродуктами",
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 180, "protein": 14.0, "fat": 6.0, "carbs": 18.0},
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 45},
            {"name": "мидии", "type": "protein", "percent": 15},
            {"name": "креветки", "type": "protein", "percent": 15},
            {"name": "кальмары", "type": "protein", "percent": 10},
            {"name": "томатный соус", "type": "sauce", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "паста с тунцом": {
        "name": "Паста с тунцом",
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 190, "protein": 13.0, "fat": 6.0, "carbs": 20.0},
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 50},
            {"name": "тунец консервированный", "type": "protein", "percent": 25},
            {"name": "томатный соус", "type": "sauce", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "лазанья": {
        "name": "Лазанья",
        "category": "pasta",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 10.0, "fat": 9.0, "carbs": 16.0},
        "ingredients": [
            {"name": "листы лазаньи", "type": "carb", "percent": 30},
            {"name": "фарш мясной", "type": "protein", "percent": 25},
            {"name": "соус бешамель", "type": "sauce", "percent": 20},
            {"name": "томатный соус", "type": "sauce", "percent": 15},
            {"name": "сыр", "type": "dairy", "percent": 10}
        ]
    },
    "лазанья с грибами": {
        "name": "Лазанья с грибами",
        "category": "pasta",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 160, "protein": 8.0, "fat": 7.0, "carbs": 17.0},
        "ingredients": [
            {"name": "листы лазаньи", "type": "carb", "percent": 35},
            {"name": "шампиньоны", "type": "vegetable", "percent": 25},
            {"name": "соус бешамель", "type": "sauce", "percent": 20},
            {"name": "сыр", "type": "dairy", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 10}
        ]
    },
    "фетучини с курицей": {
        "name": "Фетучини с курицей",
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 200, "protein": 14.0, "fat": 8.0, "carbs": 19.0},
        "ingredients": [
            {"name": "фетучини", "type": "carb", "percent": 50},
            {"name": "куриное филе", "type": "protein", "percent": 25},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "пармезан", "type": "dairy", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "макароны по-флотски": {
        "name": "Макароны по-флотски",
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 10.0, "carbs": 19.0},
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 50},
            {"name": "фарш мясной", "type": "protein", "percent": 35},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "макароны с сыром": {
        "name": "Макароны с сыром",
        "category": "pasta",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 230, "protein": 9.0, "fat": 11.0, "carbs": 24.0},
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 70},
            {"name": "сыр", "type": "dairy", "percent": 20},
            {"name": "молоко", "type": "dairy", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "макароны с тушенкой": {
        "name": "Макароны с тушенкой",
        "category": "pasta",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 220, "protein": 10.0, "fat": 13.0, "carbs": 16.0},
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 50},
            {"name": "тушенка", "type": "protein", "percent": 35},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },

    # =========================================================================
    # 🥔 ГАРНИРЫ
    # =========================================================================
    "картофельное пюре": {
        "name": "Картофельное пюре",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 105, "protein": 2.5, "fat": 3.5, "carbs": 16.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 80},
            {"name": "молоко", "type": "dairy", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "картофель жареный": {
        "name": "Картофель жареный",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 190, "protein": 3.0, "fat": 9.0, "carbs": 24.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 85},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "картофель отварной": {
        "name": "Картофель отварной",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 80, "protein": 2.0, "fat": 0.5, "carbs": 17.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 100}
        ]
    },
    "картофель фри": {
        "name": "Картофель фри",
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 290, "protein": 3.5, "fat": 15.0, "carbs": 34.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 70},
            {"name": "масло растительное", "type": "fat", "percent": 30}
        ]
    },
    "картофель по-деревенски": {
        "name": "Картофель по-деревенски",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 170, "protein": 3.0, "fat": 7.0, "carbs": 24.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 85},
            {"name": "масло растительное", "type": "fat", "percent": 10},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "картофель запеченный": {
        "name": "Картофель запеченный",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 95, "protein": 2.5, "fat": 1.5, "carbs": 18.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 95},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "рис отварной": {
        "name": "Рис отварной",
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 130, "protein": 2.5, "fat": 0.5, "carbs": 29.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 100}
        ]
    },
    "рис с овощами": {
        "name": "Рис с овощами",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 110, "protein": 2.5, "fat": 2.0, "carbs": 20.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 60},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "горошек", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "гречка отварная": {
        "name": "Гречка отварная",
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 110, "protein": 4.0, "fat": 1.0, "carbs": 21.0},
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 100}
        ]
    },
    "гречка с грибами": {
        "name": "Гречка с грибами",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 5.0, "fat": 3.0, "carbs": 18.0},
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 60},
            {"name": "шампиньоны", "type": "vegetable", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "гречка с мясом": {
        "name": "Гречка с мясом",
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 160, "protein": 10.0, "fat": 6.0, "carbs": 16.0},
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 50},
            {"name": "мясо", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "овсянка": {
        "name": "Овсяная каша",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 90, "protein": 3.5, "fat": 2.5, "carbs": 14.0},
        "ingredients": [
            {"name": "овсяные хлопья", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "овсянка на воде": {
        "name": "Овсяная каша на воде",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 65, "protein": 2.5, "fat": 1.5, "carbs": 11.0},
        "ingredients": [
            {"name": "овсяные хлопья", "type": "carb", "percent": 30},
            {"name": "вода", "type": "liquid", "percent": 70}
        ]
    },
    "перловка": {
        "name": "Перловая каша",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 110, "protein": 3.0, "fat": 0.5, "carbs": 23.0},
        "ingredients": [
            {"name": "перловка", "type": "carb", "percent": 40},
            {"name": "вода", "type": "liquid", "percent": 60}
        ]
    },
    "пшено": {
        "name": "Пшенная каша",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 115, "protein": 3.5, "fat": 1.5, "carbs": 22.0},
        "ingredients": [
            {"name": "пшено", "type": "carb", "percent": 35},
            {"name": "молоко", "type": "dairy", "percent": 60},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "кукурузная каша": {
        "name": "Кукурузная каша",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 100, "protein": 2.5, "fat": 0.8, "carbs": 21.0},
        "ingredients": [
            {"name": "кукурузная крупа", "type": "carb", "percent": 35},
            {"name": "вода", "type": "liquid", "percent": 65}
        ]
    },
    "чечевица": {
        "name": "Чечевица отварная",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 115, "protein": 9.0, "fat": 0.5, "carbs": 20.0},
        "ingredients": [
            {"name": "чечевица", "type": "protein", "percent": 50},
            {"name": "вода", "type": "liquid", "percent": 50}
        ]
    },
    "нут": {
        "name": "Нут отварной",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 140, "protein": 8.0, "fat": 2.5, "carbs": 22.0},
        "ingredients": [
            {"name": "нут", "type": "protein", "percent": 50},
            {"name": "вода", "type": "liquid", "percent": 50}
        ]
    },
    "фасоль": {
        "name": "Фасоль отварная",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 125, "protein": 8.5, "fat": 0.5, "carbs": 22.0},
        "ingredients": [
            {"name": "фасоль", "type": "protein", "percent": 50},
            {"name": "вода", "type": "liquid", "percent": 50}
        ]
    },
    "горох": {
        "name": "Горох отварной",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 115, "protein": 8.0, "fat": 0.5, "carbs": 20.0},
        "ingredients": [
            {"name": "горох", "type": "protein", "percent": 50},
            {"name": "вода", "type": "liquid", "percent": 50}
        ]
    },
    "овощи на пару": {
        "name": "Овощи на пару",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 45, "protein": 2.0, "fat": 0.5, "carbs": 8.0},
        "ingredients": [
            {"name": "брокколи", "type": "vegetable", "percent": 30},
            {"name": "цветная капуста", "type": "vegetable", "percent": 30},
            {"name": "морковь", "type": "vegetable", "percent": 20},
            {"name": "фасоль стручковая", "type": "vegetable", "percent": 20}
        ]
    },
    "овощи гриль": {
        "name": "Овощи гриль",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 80, "protein": 2.5, "fat": 4.0, "carbs": 9.0},
        "ingredients": [
            {"name": "кабачки", "type": "vegetable", "percent": 25},
            {"name": "баклажаны", "type": "vegetable", "percent": 25},
            {"name": "перец болгарский", "type": "vegetable", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "рагу овощное": {
        "name": "Рагу овощное",
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 70, "protein": 2.0, "fat": 3.0, "carbs": 9.0},
        "ingredients": [
            {"name": "кабачки", "type": "vegetable", "percent": 25},
            {"name": "баклажаны", "type": "vegetable", "percent": 20},
            {"name": "перец", "type": "vegetable", "percent": 15},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "тушеные овощи": {
        "name": "Тушеные овощи",
        "category": "side",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 65, "protein": 2.0, "fat": 2.5, "carbs": 8.5},
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 40},
            {"name": "морковь", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "томаты", "type": "vegetable", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "тушеная капуста": {
        "name": "Тушеная капуста",
        "category": "side",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 55, "protein": 2.0, "fat": 2.5, "carbs": 6.5},
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 75},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5}
        ]
    },
    "квашеная капуста": {
        "name": "Квашеная капуста",
        "category": "side",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 25, "protein": 1.5, "fat": 0.1, "carbs": 5.0},
        "ingredients": [
            {"name": "капуста квашеная", "type": "vegetable", "percent": 100}
        ]
    },

    # =========================================================================
    # 🥚 ЗАВТРАКИ
    # =========================================================================
    "омлет": {
        "name": "Омлет",
        "category": "breakfast",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 150, "protein": 9.0, "fat": 11.0, "carbs": 2.5},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 60},
            {"name": "молоко", "type": "dairy", "percent": 35},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "омлет с сыром": {
        "name": "Омлет с сыром",
        "category": "breakfast",
        "default_weight": 170,
        "nutrition_per_100": {"calories": 200, "protein": 12.0, "fat": 15.0, "carbs": 3.0},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 55},
            {"name": "молоко", "type": "dairy", "percent": 25},
            {"name": "сыр", "type": "dairy", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "омлет с ветчиной": {
        "name": "Омлет с ветчиной",
        "category": "breakfast",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 190, "protein": 13.0, "fat": 14.0, "carbs": 2.5},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 50},
            {"name": "ветчина", "type": "protein", "percent": 20},
            {"name": "молоко", "type": "dairy", "percent": 25},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "омлет с овощами": {
        "name": "Омлет с овощами",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 130, "protein": 8.0, "fat": 9.0, "carbs": 4.0},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 50},
            {"name": "помидоры", "type": "vegetable", "percent": 20},
            {"name": "перец", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "молоко", "type": "dairy", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "яичница глазунья": {
        "name": "Яичница глазунья",
        "category": "breakfast",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 190, "protein": 13.0, "fat": 15.0, "carbs": 1.0},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 90},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "яичница с беконом": {
        "name": "Яичница с беконом",
        "category": "breakfast",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 250, "protein": 15.0, "fat": 20.0, "carbs": 1.5},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 60},
            {"name": "бекон", "type": "protein", "percent": 30},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "яичница с помидорами": {
        "name": "Яичница с помидорами",
        "category": "breakfast",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 140, "protein": 8.0, "fat": 10.0, "carbs": 3.5},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 60},
            {"name": "помидоры", "type": "vegetable", "percent": 30},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "яйца пашот": {
        "name": "Яйца пашот",
        "category": "breakfast",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 155, "protein": 12.5, "fat": 11.0, "carbs": 1.0},
        "ingredients": [
            {"name": "яйцо куриное", "type": "protein", "percent": 100}
        ]
    },
    "каша манная": {
        "name": "Манная каша",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 110, "protein": 3.0, "fat": 3.0, "carbs": 18.0},
        "ingredients": [
            {"name": "манка", "type": "carb", "percent": 20},
            {"name": "молоко", "type": "dairy", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "каша рисовая молочная": {
        "name": "Рисовая молочная каша",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 3.5, "fat": 3.0, "carbs": 20.0},
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "каша гречневая молочная": {
        "name": "Гречневая молочная каша",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 115, "protein": 4.5, "fat": 3.0, "carbs": 17.0},
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "каша пшенная молочная": {
        "name": "Пшенная молочная каша",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 120, "protein": 4.0, "fat": 3.5, "carbs": 18.0},
        "ingredients": [
            {"name": "пшено", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "сырники": {
        "name": "Сырники",
        "category": "breakfast",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 210, "protein": 14.0, "fat": 9.0, "carbs": 19.0},
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 70},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "сырники с изюмом": {
        "name": "Сырники с изюмом",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 13.0, "fat": 8.0, "carbs": 24.0},
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 65},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "изюм", "type": "fruit", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "оладьи": {
        "name": "Оладьи",
        "category": "breakfast",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 220, "protein": 6.0, "fat": 9.0, "carbs": 29.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "кефир", "type": "dairy", "percent": 40},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "оладьи с яблоками": {
        "name": "Оладьи с яблоками",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 200, "protein": 5.0, "fat": 7.0, "carbs": 30.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "кефир", "type": "dairy", "percent": 35},
            {"name": "яблоко", "type": "fruit", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 7}
        ]
    },
    "блины": {
        "name": "Блины",
        "category": "breakfast",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 200, "protein": 6.0, "fat": 6.0, "carbs": 31.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "молоко", "type": "dairy", "percent": 50},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "блины с маслом": {
        "name": "Блины с маслом",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 230, "protein": 6.0, "fat": 10.0, "carbs": 29.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 45},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 12}
        ]
    },
    "блины со сметаной": {
        "name": "Блины со сметаной",
        "category": "breakfast",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 210, "protein": 6.0, "fat": 8.0, "carbs": 28.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 45},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 12}
        ]
    },
    "блины с икрой": {
        "name": "Блины с икрой",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 10.0, "fat": 8.0, "carbs": 27.0},
        "ingredients": [
            {"name": "блины", "type": "carb", "percent": 70},
            {"name": "икра красная", "type": "protein", "percent": 30}
        ]
    },
    "блины с творогом": {
        "name": "Блины с творогом",
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 9.0, "fat": 6.0, "carbs": 25.0},
        "ingredients": [
            {"name": "блины", "type": "carb", "percent": 50},
            {"name": "творог", "type": "dairy", "percent": 45},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "запеканка творожная": {
        "name": "Запеканка творожная",
        "category": "breakfast",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 180, "protein": 14.0, "fat": 7.0, "carbs": 16.0},
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 70},
            {"name": "манка", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "запеканка с изюмом": {
        "name": "Творожная запеканка с изюмом",
        "category": "breakfast",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 190, "protein": 13.0, "fat": 6.0, "carbs": 20.0},
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 65},
            {"name": "изюм", "type": "fruit", "percent": 15},
            {"name": "манка", "type": "carb", "percent": 8},
            {"name": "яйцо", "type": "protein", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 4}
        ]
    },
    "гренки": {
        "name": "Гренки",
        "category": "breakfast",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 280, "protein": 7.0, "fat": 13.0, "carbs": 34.0},
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 70},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "молоко", "type": "dairy", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "гренки с сыром": {
        "name": "Гренки с сыром",
        "category": "breakfast",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 300, "protein": 10.0, "fat": 16.0, "carbs": 29.0},
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 60},
            {"name": "сыр", "type": "dairy", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "тосты": {
        "name": "Тосты",
        "category": "breakfast",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 250, "protein": 8.0, "fat": 10.0, "carbs": 32.0},
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 80},
            {"name": "масло сливочное", "type": "fat", "percent": 20}
        ]
    },
    "тосты с авокадо": {
        "name": "Тосты с авокадо",
        "category": "breakfast",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 5.0, "fat": 14.0, "carbs": 19.0},
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 50},
            {"name": "авокадо", "type": "fruit", "percent": 40},
            {"name": "лимон", "type": "fruit", "percent": 5},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "тосты с яйцом": {
        "name": "Тосты с яйцом",
        "category": "breakfast",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 210, "protein": 9.0, "fat": 12.0, "carbs": 16.0},
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 50},
            {"name": "яйцо", "type": "protein", "percent": 30},
            {"name": "масло", "type": "fat", "percent": 20}
        ]
    },
    "мюсли с молоком": {
        "name": "Мюсли с молоком",
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 120, "protein": 4.0, "fat": 3.5, "carbs": 18.0},
        "ingredients": [
            {"name": "мюсли", "type": "carb", "percent": 40},
            {"name": "молоко", "type": "dairy", "percent": 60}
        ]
    },
    "мюсли с йогуртом": {
        "name": "Мюсли с йогуртом",
        "category": "breakfast",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 130, "protein": 4.5, "fat": 3.0, "carbs": 21.0},
        "ingredients": [
            {"name": "мюсли", "type": "carb", "percent": 45},
            {"name": "йогурт", "type": "dairy", "percent": 55}
        ]
    },

    # =========================================================================
    # 🥧 ВЫПЕЧКА
    # =========================================================================
    "пицца маргарита": {
        "name": "Пицца Маргарита",
        "category": "bakery",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 240, "protein": 10.0, "fat": 9.0, "carbs": 30.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 50},
            {"name": "соус томатный", "type": "sauce", "percent": 15},
            {"name": "моцарелла", "type": "dairy", "percent": 25},
            {"name": "помидоры", "type": "vegetable", "percent": 10}
        ]
    },
    "пицца пепперони": {
        "name": "Пицца Пепперони",
        "category": "bakery",
        "default_weight": 320,
        "nutrition_per_100": {"calories": 280, "protein": 13.0, "fat": 13.0, "carbs": 28.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "соус томатный", "type": "sauce", "percent": 15},
            {"name": "моцарелла", "type": "dairy", "percent": 20},
            {"name": "пепперони", "type": "protein", "percent": 20}
        ]
    },
    "пицца с грибами": {
        "name": "Пицца с грибами",
        "category": "bakery",
        "default_weight": 320,
        "nutrition_per_100": {"calories": 230, "protein": 10.0, "fat": 9.0, "carbs": 29.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 50},
            {"name": "соус томатный", "type": "sauce", "percent": 15},
            {"name": "моцарелла", "type": "dairy", "percent": 20},
            {"name": "шампиньоны", "type": "vegetable", "percent": 15}
        ]
    },
    "пицца четыре сыра": {
        "name": "Пицца Четыре сыра",
        "category": "bakery",
        "default_weight": 300,
        "nutrition_per_100": {"calories": 290, "protein": 14.0, "fat": 14.0, "carbs": 27.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "моцарелла", "type": "dairy", "percent": 25},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "дор блю", "type": "dairy", "percent": 10},
            {"name": "фета", "type": "dairy", "percent": 10}
        ]
    },
    "пицца гавайская": {
        "name": "Пицца Гавайская",
        "category": "bakery",
        "default_weight": 320,
        "nutrition_per_100": {"calories": 250, "protein": 12.0, "fat": 9.0, "carbs": 31.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 50},
            {"name": "соус томатный", "type": "sauce", "percent": 10},
            {"name": "моцарелла", "type": "dairy", "percent": 20},
            {"name": "курица", "type": "protein", "percent": 10},
            {"name": "ананас", "type": "fruit", "percent": 10}
        ]
    },
    "пицца с ветчиной и грибами": {
        "name": "Пицца с ветчиной и грибами",
        "category": "bakery",
        "default_weight": 330,
        "nutrition_per_100": {"calories": 250, "protein": 12.0, "fat": 11.0, "carbs": 27.0},
        "ingredients": [
            {"name": "тесто для пиццы", "type": "carb", "percent": 45},
            {"name": "соус томатный", "type": "sauce", "percent": 10},
            {"name": "моцарелла", "type": "dairy", "percent": 20},
            {"name": "ветчина", "type": "protein", "percent": 15},
            {"name": "шампиньоны", "type": "vegetable", "percent": 10}
        ]
    },
    "чебуреки": {
        "name": "Чебуреки",
        "category": "bakery",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 320, "protein": 10.0, "fat": 20.0, "carbs": 25.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "вода", "type": "liquid", "percent": 20},
            {"name": "фарш мясной", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "беляши": {
        "name": "Беляши",
        "category": "bakery",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 290, "protein": 9.0, "fat": 16.0, "carbs": 27.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "вода", "type": "liquid", "percent": 15},
            {"name": "фарш мясной", "type": "protein", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 15}
        ]
    },
    "пирожки с мясом": {
        "name": "Пирожки с мясом",
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 280, "protein": 10.0, "fat": 13.0, "carbs": 31.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 55},
            {"name": "фарш мясной", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "пирожки с капустой": {
        "name": "Пирожки с капустой",
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 230, "protein": 5.0, "fat": 10.0, "carbs": 30.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 60},
            {"name": "капуста", "type": "vegetable", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "пирожки с картошкой": {
        "name": "Пирожки с картошкой",
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 240, "protein": 5.0, "fat": 11.0, "carbs": 31.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 60},
            {"name": "картофель", "type": "carb", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "пирожки с яблоками": {
        "name": "Пирожки с яблоками",
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 4.0, "fat": 8.0, "carbs": 34.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 60},
            {"name": "яблоки", "type": "fruit", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 10}
        ]
    },
    "пирожки с вишней": {
        "name": "Пирожки с вишней",
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 4.0, "fat": 8.0, "carbs": 34.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 60},
            {"name": "вишня", "type": "fruit", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 10}
        ]
    },
    "пирожки с повидлом": {
        "name": "Пирожки с повидлом",
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 240, "protein": 4.0, "fat": 8.0, "carbs": 38.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 60},
            {"name": "повидло", "type": "fruit", "percent": 35},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "ватрушки с творогом": {
        "name": "Ватрушки с творогом",
        "category": "bakery",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 250, "protein": 10.0, "fat": 9.0, "carbs": 33.0},
        "ingredients": [
            {"name": "тесто дрожжевое", "type": "carb", "percent": 60},
            {"name": "творог", "type": "dairy", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "булочки с маком": {
        "name": "Булочки с маком",
        "category": "bakery",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 320, "protein": 8.0, "fat": 10.0, "carbs": 50.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 60},
            {"name": "молоко", "type": "dairy", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "мак", "type": "other", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "булочки с корицей": {
        "name": "Булочки с корицей",
        "category": "bakery",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 330, "protein": 7.0, "fat": 11.0, "carbs": 51.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 60},
            {"name": "молоко", "type": "dairy", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 8},
            {"name": "корица", "type": "other", "percent": 2}
        ]
    },
    "кекс": {
        "name": "Кекс",
        "category": "bakery",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 340, "protein": 6.0, "fat": 15.0, "carbs": 46.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 20}
        ]
    },
    "кекс с изюмом": {
        "name": "Кекс с изюмом",
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 330, "protein": 6.0, "fat": 14.0, "carbs": 47.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "изюм", "type": "fruit", "percent": 10}
        ]
    },
    "кекс с шоколадом": {
        "name": "Кекс с шоколадом",
        "category": "bakery",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 360, "protein": 6.0, "fat": 17.0, "carbs": 47.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "шоколад", "type": "other", "percent": 15}
        ]
    },
    "печенье овсяное": {
        "name": "Печенье овсяное",
        "category": "bakery",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 420, "protein": 8.0, "fat": 17.0, "carbs": 60.0},
        "ingredients": [
            {"name": "овсяные хлопья", "type": "carb", "percent": 40},
            {"name": "мука", "type": "carb", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "печенье песочное": {
        "name": "Печенье песочное",
        "category": "bakery",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 450, "protein": 6.0, "fat": 22.0, "carbs": 58.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 50},
            {"name": "масло сливочное", "type": "fat", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "пряники": {
        "name": "Пряники",
        "category": "bakery",
        "default_weight": 80,
        "nutrition_per_100": {"calories": 360, "protein": 5.0, "fat": 6.0, "carbs": 74.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 60},
            {"name": "сахар", "type": "carb", "percent": 30},
            {"name": "мед", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "блинчики с мясом": {
        "name": "Блинчики с мясом",
        "category": "bakery",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 210, "protein": 10.0, "fat": 9.0, "carbs": 22.0},
        "ingredients": [
            {"name": "блины", "type": "carb", "percent": 50},
            {"name": "фарш мясной", "type": "protein", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 10}
        ]
    },
    "блинчики с творогом": {
        "name": "Блинчики с творогом",
        "category": "bakery",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 190, "protein": 9.0, "fat": 6.0, "carbs": 25.0},
        "ingredients": [
            {"name": "блины", "type": "carb", "percent": 50},
            {"name": "творог", "type": "dairy", "percent": 45},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "блинчики с вишней": {
        "name": "Блинчики с вишней",
        "category": "bakery",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 170, "protein": 5.0, "fat": 4.0, "carbs": 29.0},
        "ingredients": [
            {"name": "блины", "type": "carb", "percent": 50},
            {"name": "вишня", "type": "fruit", "percent": 45},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },

    # =========================================================================
    # 🍰 ДЕСЕРТЫ
    # =========================================================================
    "торт наполеон": {
        "name": "Торт Наполеон",
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 380, "protein": 6.0, "fat": 22.0, "carbs": 40.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "масло сливочное", "type": "fat", "percent": 25},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "молоко", "type": "dairy", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 10}
        ]
    },
    "торт медовик": {
        "name": "Торт Медовик",
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 360, "protein": 5.0, "fat": 18.0, "carbs": 47.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "мед", "type": "carb", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 15}
        ]
    },
    "торт прага": {
        "name": "Торт Прага",
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 400, "protein": 6.0, "fat": 24.0, "carbs": 41.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 25},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 20},
            {"name": "какао", "type": "other", "percent": 5},
            {"name": "шоколад", "type": "other", "percent": 10}
        ]
    },
    "торт киевский": {
        "name": "Торт Киевский",
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 450, "protein": 5.0, "fat": 25.0, "carbs": 52.0},
        "ingredients": [
            {"name": "сахар", "type": "carb", "percent": 40},
            {"name": "орехи", "type": "nut", "percent": 25},
            {"name": "масло сливочное", "type": "fat", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "торт панчо": {
        "name": "Торт Панчо",
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 340, "protein": 4.0, "fat": 16.0, "carbs": 46.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 25},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "сметана", "type": "dairy", "percent": 30},
            {"name": "ананас", "type": "fruit", "percent": 10},
            {"name": "какао", "type": "other", "percent": 5},
            {"name": "орехи", "type": "nut", "percent": 5}
        ]
    },
    "чизкейк": {
        "name": "Чизкейк",
        "category": "dessert",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 320, "protein": 9.0, "fat": 20.0, "carbs": 26.0},
        "ingredients": [
            {"name": "сыр сливочный", "type": "dairy", "percent": 50},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "печенье", "type": "carb", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "чизкейк нью-йорк": {
        "name": "Чизкейк Нью-Йорк",
        "category": "dessert",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 330, "protein": 9.0, "fat": 22.0, "carbs": 24.0},
        "ingredients": [
            {"name": "сыр филадельфия", "type": "dairy", "percent": 55},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "печенье", "type": "carb", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "пирожное картошка": {
        "name": "Пирожное Картошка",
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 380, "protein": 5.0, "fat": 20.0, "carbs": 46.0},
        "ingredients": [
            {"name": "печенье", "type": "carb", "percent": 40},
            {"name": "сгущенка", "type": "dairy", "percent": 25},
            {"name": "масло сливочное", "type": "fat", "percent": 20},
            {"name": "какао", "type": "other", "percent": 15}
        ]
    },
    "эклеры": {
        "name": "Эклеры",
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 290, "protein": 6.0, "fat": 15.0, "carbs": 32.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "молоко", "type": "dairy", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 20}
        ]
    },
    "профитроли": {
        "name": "Профитроли",
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 300, "protein": 7.0, "fat": 16.0, "carbs": 32.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "молоко", "type": "dairy", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 20}
        ]
    },
    "зебра": {
        "name": "Пирог Зебра",
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 330, "protein": 5.0, "fat": 16.0, "carbs": 42.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 15},
            {"name": "какао", "type": "other", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "шарлотка": {
        "name": "Шарлотка",
        "category": "dessert",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 200, "protein": 4.0, "fat": 4.5, "carbs": 36.0},
        "ingredients": [
            {"name": "яблоки", "type": "fruit", "percent": 50},
            {"name": "мука", "type": "carb", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 15}
        ]
    },
    "манник": {
        "name": "Манник",
        "category": "dessert",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 240, "protein": 6.0, "fat": 7.0, "carbs": 39.0},
        "ingredients": [
            {"name": "манка", "type": "carb", "percent": 35},
            {"name": "кефир", "type": "dairy", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "кекс творожный": {
        "name": "Кекс творожный",
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 280, "protein": 10.0, "fat": 12.0, "carbs": 33.0},
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 40},
            {"name": "мука", "type": "carb", "percent": 25},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "пудинг": {
        "name": "Пудинг",
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 140, "protein": 4.0, "fat": 4.0, "carbs": 22.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "крахмал", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 10}
        ]
    },
    "желе": {
        "name": "Желе",
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 70, "protein": 1.5, "fat": 0.0, "carbs": 16.0},
        "ingredients": [
            {"name": "сок", "type": "liquid", "percent": 80},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "желатин", "type": "other", "percent": 5}
        ]
    },
    "мусс": {
        "name": "Мусс",
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 160, "protein": 3.0, "fat": 5.0, "carbs": 26.0},
        "ingredients": [
            {"name": "ягоды", "type": "fruit", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "манка", "type": "carb", "percent": 10},
            {"name": "вода", "type": "liquid", "percent": 25}
        ]
    },
    "суфле": {
        "name": "Суфле",
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 230, "protein": 5.0, "fat": 9.0, "carbs": 33.0},
        "ingredients": [
            {"name": "яйцо", "type": "protein", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 30},
            {"name": "желатин", "type": "other", "percent": 10}
        ]
    },
    "крем-брюле": {
        "name": "Крем-брюле",
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 220, "protein": 5.0, "fat": 10.0, "carbs": 27.0},
        "ingredients": [
            {"name": "сливки", "type": "dairy", "percent": 60},
            {"name": "желток", "type": "protein", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 20}
        ]
    },
    "панна-котта": {
        "name": "Панна-котта",
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 250, "protein": 4.0, "fat": 16.0, "carbs": 23.0},
        "ingredients": [
            {"name": "сливки", "type": "dairy", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "молоко", "type": "dairy", "percent": 10},
            {"name": "желатин", "type": "other", "percent": 5}
        ]
    },
    "тирамису": {
        "name": "Тирамису",
        "category": "dessert",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 320, "protein": 7.0, "fat": 20.0, "carbs": 28.0},
        "ingredients": [
            {"name": "маскарпоне", "type": "dairy", "percent": 50},
            {"name": "савоярди", "type": "carb", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "кофе", "type": "liquid", "percent": 5}
        ]
    },
    "брауни": {
        "name": "Брауни",
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 420, "protein": 6.0, "fat": 24.0, "carbs": 47.0},
        "ingredients": [
            {"name": "шоколад", "type": "other", "percent": 35},
            {"name": "масло сливочное", "type": "fat", "percent": 25},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "маффины шоколадные": {
        "name": "Маффины шоколадные",
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 360, "protein": 6.0, "fat": 18.0, "carbs": 45.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "шоколад", "type": "other", "percent": 20},
            {"name": "масло", "type": "fat", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "молоко", "type": "dairy", "percent": 5}
        ]
    },
    "маффины с черникой": {
        "name": "Маффины с черникой",
        "category": "dessert",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 300, "protein": 5.0, "fat": 12.0, "carbs": 44.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "черника", "type": "fruit", "percent": 20},
            {"name": "масло", "type": "fat", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "молоко", "type": "dairy", "percent": 5}
        ]
    },
    "зефир": {
        "name": "Зефир",
        "category": "dessert",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 300, "protein": 1.0, "fat": 0.1, "carbs": 74.0},
        "ingredients": [
            {"name": "сахар", "type": "carb", "percent": 70},
            {"name": "пюре фруктовое", "type": "fruit", "percent": 20},
            {"name": "желатин", "type": "other", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "мармелад": {
        "name": "Мармелад",
        "category": "dessert",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 280, "protein": 0.5, "fat": 0.1, "carbs": 69.0},
        "ingredients": [
            {"name": "сахар", "type": "carb", "percent": 70},
            {"name": "пюре фруктовое", "type": "fruit", "percent": 25},
            {"name": "желатин", "type": "other", "percent": 5}
        ]
    },
    "халва": {
        "name": "Халва",
        "category": "dessert",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 520, "protein": 12.0, "fat": 30.0, "carbs": 50.0},
        "ingredients": [
            {"name": "семечки", "type": "nut", "percent": 50},
            {"name": "сахар", "type": "carb", "percent": 40},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "лукум": {
        "name": "Лукум",
        "category": "dessert",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 330, "protein": 1.0, "fat": 1.0, "carbs": 78.0},
        "ingredients": [
            {"name": "сахар", "type": "carb", "percent": 70},
            {"name": "крахмал", "type": "carb", "percent": 20},
            {"name": "орехи", "type": "nut", "percent": 5},
            {"name": "ароматизаторы", "type": "other", "percent": 5}
        ]
    },
    "щербет": {
        "name": "Щербет",
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 400, "protein": 3.0, "fat": 10.0, "carbs": 75.0},
        "ingredients": [
            {"name": "сахар", "type": "carb", "percent": 50},
            {"name": "сгущенка", "type": "dairy", "percent": 30},
            {"name": "орехи", "type": "nut", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "сгущенка вареная": {
        "name": "Сгущенка вареная",
        "category": "dessert",
        "default_weight": 30,
        "nutrition_per_100": {"calories": 330, "protein": 7.0, "fat": 8.5, "carbs": 56.0},
        "ingredients": [
            {"name": "молоко сгущенное", "type": "dairy", "percent": 100}
        ]
    },

    # =========================================================================
    # 🥤 НАПИТКИ
    # =========================================================================
    "компот": {
        "name": "Компот",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 0.2, "fat": 0.1, "carbs": 12.0},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 80},
            {"name": "фрукты сушеные", "type": "fruit", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "компот из сухофруктов": {
        "name": "Компот из сухофруктов",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 60, "protein": 0.5, "fat": 0.1, "carbs": 14.0},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 80},
            {"name": "сухофрукты", "type": "fruit", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "кисель": {
        "name": "Кисель",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 55, "protein": 0.2, "fat": 0.1, "carbs": 13.0},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 85},
            {"name": "сахар", "type": "carb", "percent": 8},
            {"name": "крахмал", "type": "carb", "percent": 5},
            {"name": "ягоды", "type": "fruit", "percent": 2}
        ]
    },
    "морс": {
        "name": "Морс",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 40, "protein": 0.1, "fat": 0.1, "carbs": 9.5},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 80},
            {"name": "ягоды", "type": "fruit", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "квас": {
        "name": "Квас",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 30, "protein": 0.3, "fat": 0.1, "carbs": 6.5},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 90},
            {"name": "хлеб", "type": "carb", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "смузи": {
        "name": "Смузи",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 60, "protein": 1.5, "fat": 1.0, "carbs": 11.0},
        "ingredients": [
            {"name": "банан", "type": "fruit", "percent": 30},
            {"name": "йогурт", "type": "dairy", "percent": 30},
            {"name": "ягоды", "type": "fruit", "percent": 30},
            {"name": "мед", "type": "carb", "percent": 10}
        ]
    },
    "смузи зеленый": {
        "name": "Зеленый смузи",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 50, "protein": 2.0, "fat": 1.0, "carbs": 8.0},
        "ingredients": [
            {"name": "шпинат", "type": "vegetable", "percent": 40},
            {"name": "банан", "type": "fruit", "percent": 30},
            {"name": "яблоко", "type": "fruit", "percent": 20},
            {"name": "вода", "type": "liquid", "percent": 10}
        ]
    },
    "смузи ягодный": {
        "name": "Ягодный смузи",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 55, "protein": 1.0, "fat": 0.5, "carbs": 12.0},
        "ingredients": [
            {"name": "ягоды", "type": "fruit", "percent": 60},
            {"name": "йогурт", "type": "dairy", "percent": 30},
            {"name": "банан", "type": "fruit", "percent": 10}
        ]
    },
    "молочный коктейль": {
        "name": "Молочный коктейль",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 85, "protein": 3.0, "fat": 2.5, "carbs": 12.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 80},
            {"name": "мороженое", "type": "dairy", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "какао": {
        "name": "Какао",
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 70, "protein": 2.5, "fat": 2.5, "carbs": 9.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 85},
            {"name": "какао-порошок", "type": "other", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 10}
        ]
    },
    "кофе": {
        "name": "Кофе",
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 2, "protein": 0.2, "fat": 0.1, "carbs": 0.3},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 98},
            {"name": "кофе", "type": "other", "percent": 2}
        ]
    },
    "кофе с молоком": {
        "name": "Кофе с молоком",
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 25, "protein": 1.5, "fat": 1.0, "carbs": 2.5},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 80},
            {"name": "кофе", "type": "other", "percent": 2},
            {"name": "молоко", "type": "dairy", "percent": 18}
        ]
    },
    "кофе капучино": {
        "name": "Капучино",
        "category": "drink",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 35, "protein": 2.0, "fat": 1.8, "carbs": 2.8},
        "ingredients": [
            {"name": "эспрессо", "type": "other", "percent": 20},
            {"name": "молоко", "type": "dairy", "percent": 70},
            {"name": "молочная пена", "type": "dairy", "percent": 10}
        ]
    },
    "кофе латте": {
        "name": "Латте",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 45, "protein": 2.2, "fat": 2.0, "carbs": 4.0},
        "ingredients": [
            {"name": "эспрессо", "type": "other", "percent": 15},
            {"name": "молоко", "type": "dairy", "percent": 80},
            {"name": "пена", "type": "dairy", "percent": 5}
        ]
    },
    "чай": {
        "name": "Чай",
        "category": "drink",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 1, "protein": 0.1, "fat": 0.0, "carbs": 0.2},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 99},
            {"name": "чай", "type": "other", "percent": 1}
        ]
    },
    "чай с лимоном": {
        "name": "Чай с лимоном",
        "category": "drink",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 3, "protein": 0.1, "fat": 0.0, "carbs": 0.6},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 95},
            {"name": "чай", "type": "other", "percent": 1},
            {"name": "лимон", "type": "fruit", "percent": 4}
        ]
    },
    "чай с сахаром": {
        "name": "Чай с сахаром",
        "category": "drink",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 20, "protein": 0.1, "fat": 0.0, "carbs": 5.0},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 95},
            {"name": "чай", "type": "other", "percent": 1},
            {"name": "сахар", "type": "carb", "percent": 4}
        ]
    },
    "лимонад": {
        "name": "Лимонад",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 40, "protein": 0.1, "fat": 0.1, "carbs": 9.8},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 85},
            {"name": "лимон", "type": "fruit", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "лимонад с мятой": {
        "name": "Лимонад с мятой",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 38, "protein": 0.1, "fat": 0.1, "carbs": 9.5},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 85},
            {"name": "лимон", "type": "fruit", "percent": 8},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "мята", "type": "herb", "percent": 2}
        ]
    },
    "имбирный напиток": {
        "name": "Имбирный напиток",
        "category": "drink",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 25, "protein": 0.2, "fat": 0.1, "carbs": 6.0},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 90},
            {"name": "имбирь", "type": "vegetable", "percent": 5},
            {"name": "лимон", "type": "fruit", "percent": 3},
            {"name": "мед", "type": "carb", "percent": 2}
        ]
    },

    # =========================================================================
    # 🥫 СОУСЫ И ЗАПРАВКИ
    # =========================================================================
    "соус цезарь": {
        "name": "Соус Цезарь",
        "category": "sauce",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 480, "protein": 2.0, "fat": 48.0, "carbs": 8.0},
        "ingredients": [
            {"name": "майонез", "type": "sauce", "percent": 60},
            {"name": "пармезан", "type": "dairy", "percent": 15},
            {"name": "анчоусы", "type": "protein", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "горчица", "type": "sauce", "percent": 5},
            {"name": "лимон", "type": "fruit", "percent": 10}
        ]
    },
    "соус песто": {
        "name": "Соус Песто",
        "category": "sauce",
        "default_weight": 40,
        "nutrition_per_100": {"calories": 520, "protein": 6.0, "fat": 50.0, "carbs": 8.0},
        "ingredients": [
            {"name": "базилик", "type": "herb", "percent": 40},
            {"name": "кедровые орехи", "type": "nut", "percent": 20},
            {"name": "пармезан", "type": "dairy", "percent": 20},
            {"name": "оливковое масло", "type": "fat", "percent": 15},
            {"name": "чеснок", "type": "vegetable", "percent": 5}
        ]
    },
    "соус бешамель": {
        "name": "Соус Бешамель",
        "category": "sauce",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 150, "protein": 4.0, "fat": 10.0, "carbs": 11.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 70},
            {"name": "мука", "type": "carb", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "мускатный орех", "type": "other", "percent": 5}
        ]
    },
    "соус сырный": {
        "name": "Соус сырный",
        "category": "sauce",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 280, "protein": 10.0, "fat": 24.0, "carbs": 6.0},
        "ingredients": [
            {"name": "сыр", "type": "dairy", "percent": 50},
            {"name": "сливки", "type": "dairy", "percent": 40},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "соус томатный": {
        "name": "Соус томатный",
        "category": "sauce",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 80, "protein": 2.0, "fat": 2.5, "carbs": 12.0},
        "ingredients": [
            {"name": "томаты", "type": "vegetable", "percent": 70},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5},
            {"name": "специи", "type": "other", "percent": 10}
        ]
    },
    "соус грибной": {
        "name": "Соус грибной",
        "category": "sauce",
        "default_weight": 60,
        "nutrition_per_100": {"calories": 90, "protein": 3.0, "fat": 5.0, "carbs": 8.0},
        "ingredients": [
            {"name": "грибы", "type": "vegetable", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "соус сметанный": {
        "name": "Соус сметанный",
        "category": "sauce",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 190, "protein": 3.0, "fat": 18.0, "carbs": 5.0},
        "ingredients": [
            {"name": "сметана", "type": "dairy", "percent": 80},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5},
            {"name": "специи", "type": "other", "percent": 10}
        ]
    },
    "соус тартар": {
        "name": "Соус Тартар",
        "category": "sauce",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 350, "protein": 2.0, "fat": 35.0, "carbs": 8.0},
        "ingredients": [
            {"name": "майонез", "type": "sauce", "percent": 70},
            {"name": "огурцы соленые", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "каперсы", "type": "vegetable", "percent": 5},
            {"name": "зелень", "type": "herb", "percent": 5}
        ]
    },
    "соус барбекю": {
        "name": "Соус Барбекю",
        "category": "sauce",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 160, "protein": 1.5, "fat": 5.0, "carbs": 28.0},
        "ingredients": [
            {"name": "томатная паста", "type": "sauce", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "уксус", "type": "other", "percent": 10},
            {"name": "специи", "type": "other", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "соус терияки": {
        "name": "Соус Терияки",
        "category": "sauce",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 120, "protein": 4.0, "fat": 0.5, "carbs": 26.0},
        "ingredients": [
            {"name": "соевый соус", "type": "sauce", "percent": 60},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "имбирь", "type": "vegetable", "percent": 5},
            {"name": "кунжут", "type": "other", "percent": 5}
        ]
    },
    "соус кисло-сладкий": {
        "name": "Соус кисло-сладкий",
        "category": "sauce",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 150, "protein": 1.0, "fat": 0.5, "carbs": 36.0},
        "ingredients": [
            {"name": "сахар", "type": "carb", "percent": 40},
            {"name": "вода", "type": "liquid", "percent": 30},
            {"name": "уксус", "type": "other", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 10},
            {"name": "крахмал", "type": "carb", "percent": 5},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "горчица": {
        "name": "Горчица",
        "category": "sauce",
        "default_weight": 20,
        "nutrition_per_100": {"calories": 140, "protein": 7.0, "fat": 8.0, "carbs": 11.0},
        "ingredients": [
            {"name": "горчичный порошок", "type": "other", "percent": 40},
            {"name": "вода", "type": "liquid", "percent": 30},
            {"name": "уксус", "type": "other", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "хрен": {
        "name": "Хрен",
        "category": "sauce",
        "default_weight": 20,
        "nutrition_per_100": {"calories": 80, "protein": 2.5, "fat": 1.5, "carbs": 14.0},
        "ingredients": [
            {"name": "хрен", "type": "vegetable", "percent": 60},
            {"name": "вода", "type": "liquid", "percent": 20},
            {"name": "уксус", "type": "other", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "соль", "type": "other", "percent": 5}
        ]
    },
    "аджика": {
        "name": "Аджика",
        "category": "sauce",
        "default_weight": 30,
        "nutrition_per_100": {"calories": 60, "protein": 2.0, "fat": 2.5, "carbs": 8.0},
        "ingredients": [
            {"name": "перец", "type": "vegetable", "percent": 50},
            {"name": "чеснок", "type": "vegetable", "percent": 20},
            {"name": "томаты", "type": "vegetable", "percent": 15},
            {"name": "специи", "type": "other", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "кетчуп": {
        "name": "Кетчуп",
        "category": "sauce",
        "default_weight": 30,
        "nutrition_per_100": {"calories": 100, "protein": 1.5, "fat": 0.5, "carbs": 23.0},
        "ingredients": [
            {"name": "томаты", "type": "vegetable", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "уксус", "type": "other", "percent": 5},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "майонез": {
        "name": "Майонез",
        "category": "sauce",
        "default_weight": 30,
        "nutrition_per_100": {"calories": 620, "protein": 1.5, "fat": 67.0, "carbs": 3.5},
        "ingredients": [
            {"name": "масло растительное", "type": "fat", "percent": 70},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "горчица", "type": "sauce", "percent": 5},
            {"name": "уксус", "type": "other", "percent": 5},
            {"name": "вода", "type": "liquid", "percent": 10}
        ]
    },
        # =========================================================================
    # 🍔 ФАСТФУД
    # =========================================================================
    "гамбургер": {
        "name": "Гамбургер",
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
        ]
    },
    "чизбургер": {
        "name": "Чизбургер",
        "category": "fastfood",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 270, "protein": 13.0, "fat": 13.0, "carbs": 26.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 30},
            {"name": "котлета говяжья", "type": "protein", "percent": 25},
            {"name": "сыр чеддер", "type": "dairy", "percent": 15},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "кетчуп", "type": "sauce", "percent": 4},
            {"name": "горчица", "type": "sauce", "percent": 3}
        ]
    },
    "двойной чизбургер": {
        "name": "Двойной чизбургер",
        "category": "fastfood",
        "default_weight": 280,
        "nutrition_per_100": {"calories": 290, "protein": 16.0, "fat": 16.0, "carbs": 21.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 25},
            {"name": "котлета говяжья (2 шт)", "type": "protein", "percent": 35},
            {"name": "сыр чеддер (2 ломтика)", "type": "dairy", "percent": 15},
            {"name": "салат", "type": "vegetable", "percent": 8},
            {"name": "помидоры", "type": "vegetable", "percent": 6},
            {"name": "лук", "type": "vegetable", "percent": 4},
            {"name": "кетчуп", "type": "sauce", "percent": 4},
            {"name": "горчица", "type": "sauce", "percent": 3}
        ]
    },
    "бургер с курицей": {
        "name": "Бургер с курицей",
        "category": "fastfood",
        "default_weight": 210,
        "nutrition_per_100": {"calories": 220, "protein": 14.0, "fat": 8.0, "carbs": 25.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 35},
            {"name": "куриная котлета", "type": "protein", "percent": 30},
            {"name": "салат", "type": "vegetable", "percent": 12},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "sauce", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5}
        ]
    },
    "бургер с рыбой": {
        "name": "Бургер с рыбой",
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 210, "protein": 11.0, "fat": 9.0, "carbs": 23.0},
        "ingredients": [
            {"name": "булочка для бургера", "type": "carb", "percent": 35},
            {"name": "рыбное филе в панировке", "type": "protein", "percent": 30},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "соус тартар", "type": "sauce", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сыр", "type": "dairy", "percent": 5}
        ]
    },
    "хот-дог": {
        "name": "Хот-дог",
        "category": "fastfood",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 250, "protein": 9.0, "fat": 14.0, "carbs": 22.0},
        "ingredients": [
            {"name": "булочка для хот-дога", "type": "carb", "percent": 50},
            {"name": "сосиска", "type": "protein", "percent": 30},
            {"name": "кетчуп", "type": "sauce", "percent": 10},
            {"name": "горчица", "type": "sauce", "percent": 5},
            {"name": "лук жареный", "type": "vegetable", "percent": 5}
        ]
    },
    "шаурма (донер) с курицей": {
        "name": "Шаурма с курицей",
        "category": "fastfood",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 180, "protein": 10.0, "fat": 7.0, "carbs": 19.0},
        "ingredients": [
            {"name": "лаваш", "type": "carb", "percent": 30},
            {"name": "курица гриль", "type": "protein", "percent": 25},
            {"name": "капуста", "type": "vegetable", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 8},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 4},
            {"name": "чесночный соус", "type": "sauce", "percent": 10}
        ]
    },
    "шаурма с говядиной": {
        "name": "Шаурма с говядиной",
        "category": "fastfood",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 11.0, "fat": 8.0, "carbs": 18.0},
        "ingredients": [
            {"name": "лаваш", "type": "carb", "percent": 30},
            {"name": "говядина", "type": "protein", "percent": 25},
            {"name": "капуста", "type": "vegetable", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 8},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 4},
            {"name": "чесночный соус", "type": "sauce", "percent": 10}
        ]
    },
    "наггетсы куриные": {
        "name": "Наггетсы куриные",
        "category": "fastfood",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 290, "protein": 16.0, "fat": 17.0, "carbs": 18.0},
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 60},
            {"name": "панировка", "type": "carb", "percent": 20},
            {"name": "масло растительное", "type": "fat", "percent": 20}
        ]
    },
    "луковые кольца": {
        "name": "Луковые кольца",
        "category": "fastfood",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 310, "protein": 4.0, "fat": 18.0, "carbs": 33.0},
        "ingredients": [
            {"name": "лук репчатый", "type": "vegetable", "percent": 50},
            {"name": "мука", "type": "carb", "percent": 20},
            {"name": "панировка", "type": "carb", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 20}
        ]
    },
    "сырные палочки": {
        "name": "Сырные палочки",
        "category": "fastfood",
        "default_weight": 120,
        "nutrition_per_100": {"calories": 350, "protein": 14.0, "fat": 22.0, "carbs": 23.0},
        "ingredients": [
            {"name": "сыр моцарелла", "type": "dairy", "percent": 60},
            {"name": "панировка", "type": "carb", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "сэндвич с ветчиной и сыром": {
        "name": "Сэндвич с ветчиной и сыром",
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 240, "protein": 11.0, "fat": 11.0, "carbs": 24.0},
        "ingredients": [
            {"name": "хлеб тостовый", "type": "carb", "percent": 50},
            {"name": "ветчина", "type": "protein", "percent": 20},
            {"name": "сыр", "type": "dairy", "percent": 15},
            {"name": "салат", "type": "vegetable", "percent": 5},
            {"name": "помидоры", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "sauce", "percent": 5}
        ]
    },
    "клубный сэндвич": {
        "name": "Клубный сэндвич",
        "category": "fastfood",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 210, "protein": 12.0, "fat": 9.0, "carbs": 21.0},
        "ingredients": [
            {"name": "тостовый хлеб (3 ломтика)", "type": "carb", "percent": 40},
            {"name": "куриная грудка", "type": "protein", "percent": 20},
            {"name": "бекон", "type": "protein", "percent": 10},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "майонез", "type": "sauce", "percent": 7},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "сэндвич с тунцом": {
        "name": "Сэндвич с тунцом",
        "category": "fastfood",
        "default_weight": 220,
        "nutrition_per_100": {"calories": 200, "protein": 11.0, "fat": 8.0, "carbs": 22.0},
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 50},
            {"name": "тунец консервированный", "type": "protein", "percent": 25},
            {"name": "майонез", "type": "sauce", "percent": 10},
            {"name": "сельдерей", "type": "vegetable", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "салат", "type": "vegetable", "percent": 5}
        ]
    },
    "картофель по-деревенски (фастфуд)": {
        "name": "Картофель по-деревенски",
        "category": "fastfood",
        "default_weight": 180,
        "nutrition_per_100": {"calories": 180, "protein": 3.0, "fat": 8.0, "carbs": 24.0},
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 80},
            {"name": "масло растительное", "type": "fat", "percent": 15},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "крылышки буффало": {
        "name": "Крылышки Буффало",
        "category": "fastfood",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 260, "protein": 20.0, "fat": 18.0, "carbs": 5.0},
        "ingredients": [
            {"name": "куриные крылья", "type": "protein", "percent": 80},
            {"name": "соус острый", "type": "sauce", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },

    # =========================================================================
    # 🍣 АЗИАТСКАЯ КУХНЯ
    # =========================================================================
    "суши с лососем": {
        "name": "Суши с лососем",
        "category": "asian",
        "default_weight": 50,
        "nutrition_per_100": {"calories": 180, "protein": 8.0, "fat": 4.0, "carbs": 28.0},
        "ingredients": [
            {"name": "рис для суши", "type": "carb", "percent": 70},
            {"name": "лосось", "type": "protein", "percent": 25},
            {"name": "нори", "type": "vegetable", "percent": 5}
        ]
    },
    "суши с угрем": {
        "name": "Суши с угрем",
        "category": "asian",
        "default_weight": 55,
        "nutrition_per_100": {"calories": 200, "protein": 9.0, "fat": 6.0, "carbs": 27.0},
        "ingredients": [
            {"name": "рис для суши", "type": "carb", "percent": 65},
            {"name": "угорь копченый", "type": "protein", "percent": 30},
            {"name": "нори", "type": "vegetable", "percent": 5}
        ]
    },
    "ролл Филадельфия": {
        "name": "Ролл Филадельфия",
        "category": "asian",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 190, "protein": 7.0, "fat": 8.0, "carbs": 23.0},
        "ingredients": [
            {"name": "рис для суши", "type": "carb", "percent": 50},
            {"name": "лосось", "type": "protein", "percent": 20},
            {"name": "сливочный сыр", "type": "dairy", "percent": 15},
            {"name": "огурец", "type": "vegetable", "percent": 10},
            {"name": "нори", "type": "vegetable", "percent": 5}
        ]
    },
    "ролл Калифорния": {
        "name": "Ролл Калифорния",
        "category": "asian",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 170, "protein": 6.0, "fat": 5.0, "carbs": 26.0},
        "ingredients": [
            {"name": "рис для суши", "type": "carb", "percent": 55},
            {"name": "крабовое мясо", "type": "protein", "percent": 15},
            {"name": "авокадо", "type": "fruit", "percent": 10},
            {"name": "огурец", "type": "vegetable", "percent": 10},
            {"name": "икра тобико", "type": "protein", "percent": 5},
            {"name": "нори", "type": "vegetable", "percent": 5}
        ]
    },
    "ролл с огурцом": {
        "name": "Ролл с огурцом",
        "category": "asian",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 130, "protein": 3.0, "fat": 1.0, "carbs": 28.0},
        "ingredients": [
            {"name": "рис для суши", "type": "carb", "percent": 70},
            {"name": "огурец", "type": "vegetable", "percent": 25},
            {"name": "нори", "type": "vegetable", "percent": 5}
        ]
    },
    "ролл с лососем и авокадо": {
        "name": "Ролл с лососем и авокадо",
        "category": "asian",
        "default_weight": 240,
        "nutrition_per_100": {"calories": 190, "protein": 7.0, "fat": 7.0, "carbs": 24.0},
        "ingredients": [
            {"name": "рис для суши", "type": "carb", "percent": 55},
            {"name": "лосось", "type": "protein", "percent": 20},
            {"name": "авокадо", "type": "fruit", "percent": 15},
            {"name": "нори", "type": "vegetable", "percent": 10}
        ]
    },
    "лапша WOK с курицей": {
        "name": "Лапша WOK с курицей",
        "category": "asian",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 150, "protein": 8.0, "fat": 5.0, "carbs": 18.0},
        "ingredients": [
            {"name": "лапша удон", "type": "carb", "percent": 40},
            {"name": "куриное филе", "type": "protein", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "перец болгарский", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 8},
            {"name": "соус соевый", "type": "sauce", "percent": 7},
            {"name": "масло кунжутное", "type": "fat", "percent": 5}
        ]
    },
    "лапша WOK с морепродуктами": {
        "name": "Лапша WOK с морепродуктами",
        "category": "asian",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 140, "protein": 9.0, "fat": 4.0, "carbs": 17.0},
        "ingredients": [
            {"name": "лапша удон", "type": "carb", "percent": 40},
            {"name": "креветки", "type": "protein", "percent": 15},
            {"name": "кальмары", "type": "protein", "percent": 10},
            {"name": "мидии", "type": "protein", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 8},
            {"name": "перец", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "соус", "type": "sauce", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 4}
        ]
    },
    "рамен с курицей": {
        "name": "Рамен с курицей",
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
        ]
    },
    "фо-бо с говядиной": {
        "name": "Фо-бо с говядиной",
        "category": "asian",
        "default_weight": 500,
        "nutrition_per_100": {"calories": 85, "protein": 6.0, "fat": 2.0, "carbs": 11.0},
        "ingredients": [
            {"name": "бульон говяжий", "type": "liquid", "percent": 70},
            {"name": "рисовая лапша", "type": "carb", "percent": 15},
            {"name": "говядина", "type": "protein", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 3},
            {"name": "зелень", "type": "herb", "percent": 2},
            {"name": "проростки сои", "type": "vegetable", "percent": 2}
        ]
    },

    # =========================================================================
    # 🌮 МЕКСИКАНСКАЯ КУХНЯ
    # =========================================================================
    "тако с говядиной": {
        "name": "Тако с говядиной",
        "category": "mexican",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 200, "protein": 10.0, "fat": 9.0, "carbs": 20.0},
        "ingredients": [
            {"name": "тортилья кукурузная", "type": "carb", "percent": 40},
            {"name": "говяжий фарш", "type": "protein", "percent": 25},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "сыр", "type": "dairy", "percent": 7},
            {"name": "сметана", "type": "dairy", "percent": 5},
            {"name": "соус сальса", "type": "sauce", "percent": 5}
        ]
    },
    "тако с курицей": {
        "name": "Тако с курицей",
        "category": "mexican",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 180, "protein": 11.0, "fat": 6.0, "carbs": 21.0},
        "ingredients": [
            {"name": "тортилья кукурузная", "type": "carb", "percent": 45},
            {"name": "курица", "type": "protein", "percent": 25},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "сыр", "type": "dairy", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 4},
            {"name": "соус", "type": "sauce", "percent": 3}
        ]
    },
    "буррито с говядиной": {
        "name": "Буррито с говядиной",
        "category": "mexican",
        "default_weight": 350,
        "nutrition_per_100": {"calories": 190, "protein": 9.0, "fat": 7.0, "carbs": 23.0},
        "ingredients": [
            {"name": "тортилья пшеничная", "type": "carb", "percent": 40},
            {"name": "говяжий фарш", "type": "protein", "percent": 20},
            {"name": "рис", "type": "carb", "percent": 15},
            {"name": "фасоль", "type": "protein", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 4},
            {"name": "салат", "type": "vegetable", "percent": 3},
            {"name": "помидоры", "type": "vegetable", "percent": 3}
        ]
    },
    "кесадилья с курицей": {
        "name": "Кесадилья с курицей",
        "category": "mexican",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 240, "protein": 13.0, "fat": 11.0, "carbs": 22.0},
        "ingredients": [
            {"name": "тортилья пшеничная", "type": "carb", "percent": 40},
            {"name": "курица", "type": "protein", "percent": 20},
            {"name": "сыр моцарелла", "type": "dairy", "percent": 25},
            {"name": "перец", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5}
        ]
    },
    "начос с сыром": {
        "name": "Начос с сыром",
        "category": "mexican",
        "default_weight": 250,
        "nutrition_per_100": {"calories": 300, "protein": 8.0, "fat": 16.0, "carbs": 32.0},
        "ingredients": [
            {"name": "чипсы начос", "type": "carb", "percent": 60},
            {"name": "сыр чеддер", "type": "dairy", "percent": 30},
            {"name": "халапеньо", "type": "vegetable", "percent": 5},
            {"name": "соус", "type": "sauce", "percent": 5}
        ]
    },
    "гуакамоле": {
        "name": "Гуакамоле",
        "category": "mexican",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 160, "protein": 2.0, "fat": 14.0, "carbs": 9.0},
        "ingredients": [
            {"name": "авокадо", "type": "fruit", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "помидоры", "type": "vegetable", "percent": 5},
            {"name": "лайм", "type": "fruit", "percent": 5},
            {"name": "кинза", "type": "herb", "percent": 3},
            {"name": "соль", "type": "other", "percent": 2}
        ]
    },

    # =========================================================================
    # 🍨 ДЕСЕРТЫ (ДОПОЛНИТЕЛЬНО)
    # =========================================================================
    "мороженое пломбир": {
        "name": "Мороженое пломбир",
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 230, "protein": 3.5, "fat": 15.0, "carbs": 20.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 50},
            {"name": "сливки", "type": "dairy", "percent": 25},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "мороженое шоколадное": {
        "name": "Мороженое шоколадное",
        "category": "dessert",
        "default_weight": 100,
        "nutrition_per_100": {"calories": 240, "protein": 4.0, "fat": 14.0, "carbs": 25.0},
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 45},
            {"name": "сливки", "type": "dairy", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "какао", "type": "other", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "мороженое фруктовый лед": {
        "name": "Фруктовый лед",
        "category": "dessert",
        "default_weight": 80,
        "nutrition_per_100": {"calories": 80, "protein": 0.2, "fat": 0.1, "carbs": 20.0},
        "ingredients": [
            {"name": "сок фруктовый", "type": "liquid", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "вода", "type": "liquid", "percent": 5}
        ]
    },
    "панкейки": {
        "name": "Панкейки",
        "category": "dessert",
        "default_weight": 200,
        "nutrition_per_100": {"calories": 220, "protein": 6.0, "fat": 7.0, "carbs": 34.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 35},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10},
            {"name": "разрыхлитель", "type": "other", "percent": 5}
        ]
    },
    "вафли бельгийские": {
        "name": "Вафли бельгийские",
        "category": "dessert",
        "default_weight": 150,
        "nutrition_per_100": {"calories": 300, "protein": 6.0, "fat": 13.0, "carbs": 40.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "молоко", "type": "dairy", "percent": 25},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "дрожжи", "type": "other", "percent": 5}
        ]
    },
    "вафли венские": {
        "name": "Вафли венские",
        "category": "dessert",
        "default_weight": 130,
        "nutrition_per_100": {"calories": 280, "protein": 5.0, "fat": 11.0, "carbs": 40.0},
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "молоко", "type": "dairy", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 12},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "разрыхлитель", "type": "other", "percent": 3}
        ]
    },

    # =========================================================================
    # 🥤 НАПИТКИ (ГАЗИРОВАННЫЕ)
    # =========================================================================
    "кола": {
        "name": "Кола",
        "category": "drink",
        "default_weight": 330,
        "nutrition_per_100": {"calories": 42, "protein": 0.0, "fat": 0.0, "carbs": 10.6},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 90},
            {"name": "сахар", "type": "carb", "percent": 10}
        ]
    },
    "спрайт": {
        "name": "Спрайт",
        "category": "drink",
        "default_weight": 330,
        "nutrition_per_100": {"calories": 40, "protein": 0.0, "fat": 0.0, "carbs": 10.0},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 92},
            {"name": "сахар", "type": "carb", "percent": 8}
        ]
    },
    "фанта": {
        "name": "Фанта",
        "category": "drink",
        "default_weight": 330,
        "nutrition_per_100": {"calories": 45, "protein": 0.0, "fat": 0.0, "carbs": 11.2},
        "ingredients": [
            {"name": "вода", "type": "liquid", "percent": 90},
            {"name": "сахар", "type": "carb", "percent": 9},
            {"name": "сок", "type": "liquid", "percent": 1}
        ]
    }
}
# Функция для поиска блюда по названию (без учета регистра)
def find_dish(query: str) -> Optional[Dict]:
    """Поиск блюда в базе COMPOSITE_DISHES по ключевому слову."""
    if not query:
        return None
    
    query_lower = query.lower().strip()
    
    # Прямое совпадение
    if query_lower in COMPOSITE_DISHES:
        return COMPOSITE_DISHES[query_lower]
    
    # Поиск по вхождению ключа в запрос
    for key, dish in COMPOSITE_DISHES.items():
        if key in query_lower or query_lower in key:
            return dish
    
    return None

def get_all_dishes() -> List[Dict]:
    """Возвращает список всех уникальных блюд (без дубликатов по name)."""
    unique_dishes = {}
    for dish_data in COMPOSITE_DISHES.values():
        dish_name = dish_data["name"]
        if dish_name not in unique_dishes:
            unique_dishes[dish_name] = dish_data
    return list(unique_dishes.values())
def get_dish_ingredients(dish_name: str, total_weight: int = 300) -> list:
    """
    ✅ Возвращает список ингредиентов для блюда с рассчитанными весами
    """
    dish_name_lower = dish_name.lower().strip()
    
    # Ищем блюдо в базе
    dish_data = COMPOSITE_DISHES.get(dish_name_lower)
    
    if not dish_data:
        # Пробуем найти по частичному совпадению
        for key, value in COMPOSITE_DISHES.items():
            if key in dish_name_lower or dish_name_lower in key:
                dish_data = value
                break
    
    if not dish_data:
        return []
    
    ingredients = dish_data.get('ingredients', [])
    if not ingredients:
        return []
    
    # 🔥 Рассчитываем веса на основе процентов
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
    """
    🔥 Исправлено: теперь Dict импортирован
    Рассчитывает КБЖУ для готового блюда
    """
    dish_name_lower = dish_name.lower().strip()
    dish_data = COMPOSITE_DISHES.get(dish_name_lower)
    
    if not dish_data:
        # Пробуем найти по частичному совпадению
        for key, value in COMPOSITE_DISHES.items():
            if key in dish_name_lower or dish_name_lower in key:
                dish_data = value
                break
    
    if not dish_data:
        return {
            'name': dish_name,
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0
        }
    
    ingredients = dish_data.get('ingredients', [])
    
    # 🔥 Суммируем КБЖУ всех ингредиентов
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    
    for ing in ingredients:
        ing_name = ing.get('name', '')
        percent = ing.get('percent', 0)
        ing_weight = int(total_weight * percent / 100)
        
        # 🔥 Получаем КБЖУ ингредиента из базы
        from services.food_api import LOCAL_FOOD_DB
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
        'ingredients_count': len(ingredients)
    }
# services/dish_db.py
def find_matching_dishes(dish_name: str, ai_ingredients: list = None, threshold: float = 0.2) -> list:
    """
    Ищет похожие готовые блюда в COMPOSITE_DISHES.
    Возвращает список словарей с ключами: name, score, dish_key, ingredients.
    """
    if not dish_name and not ai_ingredients:
        return []
    
    dish_name_lower = dish_name.lower().strip() if dish_name else ""
    
    # Множество имён ингредиентов от AI (если есть)
    ai_ingredient_names = set()
    if ai_ingredients:
        for ing in ai_ingredients:
            if isinstance(ing, dict):
                name = ing.get('name', '').lower()
                if name:
                    ai_ingredient_names.add(name)
            elif isinstance(ing, str):
                ai_ingredient_names.add(ing.lower())
    
    logger.info(f"🔍 Поиск готовых блюд для '{dish_name_lower}' с ингредиентами {ai_ingredient_names}")
    
    matches = []
    for key, dish_data in COMPOSITE_DISHES.items():
        dish_display_name = dish_data.get('name', key)
        
        # Ингредиенты блюда
        dish_ingredients = dish_data.get('ingredients', [])
        dish_ingredient_names = set(ing.get('name', '').lower() for ing in dish_ingredients if ing.get('name'))
        
        # Score по названию
        name_score = 0.0
        if dish_name_lower:
            if dish_name_lower == key or dish_name_lower == dish_display_name.lower():
                name_score = 1.0
            elif (dish_name_lower in key or key in dish_name_lower or
                  dish_name_lower in dish_display_name.lower() or dish_display_name.lower() in dish_name_lower):
                name_score = 0.6  # частичное совпадение
        
        # Score по ингредиентам
        ingredient_score = 0.0
        if ai_ingredient_names and dish_ingredient_names:
            intersection = len(ai_ingredient_names & dish_ingredient_names)
            union = len(ai_ingredient_names | dish_ingredient_names)
            if union > 0:
                jaccard = intersection / union
                coverage = intersection / len(dish_ingredient_names) if dish_ingredient_names else 0
                ingredient_score = (jaccard * 0.7 + coverage * 0.3)
        
        # Комбинируем
        if dish_name_lower and ai_ingredient_names:
            combined = name_score * 0.5 + ingredient_score * 0.5
        elif dish_name_lower:
            combined = name_score
        elif ai_ingredient_names:
            combined = ingredient_score
        else:
            combined = 0.0
        
        if combined >= threshold:
            matches.append({
                'name': dish_display_name,
                'score': round(combined, 2),
                'dish_key': key,  # 🔥 ИСПРАВЛЕНО: не key.lower(), а оригинальный key
                'ingredients': list(dish_ingredient_names)
            })
            logger.info(f"✅ Найдено совпадение: {dish_display_name} со скором {combined}, ключ: '{key}'")
    
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:5]
