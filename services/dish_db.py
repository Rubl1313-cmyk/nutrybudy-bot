"""
База данных готовых блюд с разбивкой на ингредиенты (в процентах).
Каждый ингредиент должен присутствовать в LOCAL_FOOD_DB.
Добавлен параметр default_weight - средняя масса готовой порции в граммах.
"""
from typing import Dict, List, Optional

# 🔥 БАЗА ГОТОВЫХ БЛЮД С ПОЛНЫМИ ИНГРЕДИЕНТАМИ
COMPOSITE_DISHES = {
    # ========== САЛАТЫ ==========
    "капрезе": {
        "name": "Капрезе",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 40},
            {"name": "моцарелла", "type": "dairy", "percent": 40},
            {"name": "базилик", "type": "herb", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 15}
        ]
    },
    "салат капрезе": {
        "name": "Капрезе",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 40},
            {"name": "моцарелла", "type": "dairy", "percent": 40},
            {"name": "базилик", "type": "herb", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 15}
        ]
    },
    "цезарь": {
        "name": "Цезарь",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "салат романо", "type": "vegetable", "percent": 35},
            {"name": "пармезан", "type": "dairy", "percent": 15},
            {"name": "сухарики", "type": "carb", "percent": 10},
            {"name": "соус цезарь", "type": "sauce", "percent": 10}
        ]
    },
    "салат цезарь": {
        "name": "Цезарь",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "салат романо", "type": "vegetable", "percent": 35},
            {"name": "пармезан", "type": "dairy", "percent": 15},
            {"name": "сухарики", "type": "carb", "percent": 10},
            {"name": "соус цезарь", "type": "sauce", "percent": 10}
        ]
    },
    "цезарь с курицей": {
        "name": "Цезарь с курицей",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "салат", "type": "vegetable", "percent": 35},
            {"name": "пармезан", "type": "dairy", "percent": 15},
            {"name": "сухарики", "type": "carb", "percent": 10},
            {"name": "соус цезарь", "type": "sauce", "percent": 10}
        ]
    },
    "оливье": {
        "name": "Оливье",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "колбаса", "type": "protein", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "fat", "percent": 10}
        ]
    },
    "салат оливье": {
        "name": "Оливье",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "колбаса", "type": "protein", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "fat", "percent": 10}
        ]
    },
    "винегрет": {
        "name": "Винегрет",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло подсолнечное", "type": "fat", "percent": 5}
        ]
    },
    "салат винегрет": {
        "name": "Винегрет",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло подсолнечное", "type": "fat", "percent": 5}
        ]
    },
    "греческий салат": {
        "name": "Греческий салат",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 30},
            {"name": "огурцы", "type": "vegetable", "percent": 30},
            {"name": "фета", "type": "dairy", "percent": 20},
            {"name": "оливки", "type": "vegetable", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ]
    },
    "мимоза": {
        "name": "Мимоза",
        "category": "salad",
        "default_weight": 220,
        "ingredients": [
            {"name": "рыбные консервы", "type": "protein", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "fat", "percent": 10}
        ]
    },
    "салат мимоза": {
        "name": "Мимоза",
        "category": "salad",
        "default_weight": 220,
        "ingredients": [
            {"name": "рыбные консервы", "type": "protein", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "fat", "percent": 10}
        ]
    },
    "селедка под шубой": {
        "name": "Селедка под шубой",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "сельдь", "type": "protein", "percent": 25},
            {"name": "свекла", "type": "vegetable", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "fat", "percent": 5}
        ]
    },
    "сельдь под шубой": {
        "name": "Селедка под шубой",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "сельдь", "type": "protein", "percent": 25},
            {"name": "свекла", "type": "vegetable", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "fat", "percent": 5}
        ]
    },
    "крабовый салат": {
        "name": "Крабовый салат",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "крабовые палочки", "type": "protein", "percent": 30},
            {"name": "кукуруза", "type": "vegetable", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "рис", "type": "carb", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "fat", "percent": 5}
        ]
    },
    "салат с крабовыми палочками": {
        "name": "Крабовый салат",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "крабовые палочки", "type": "protein", "percent": 30},
            {"name": "кукуруза", "type": "vegetable", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "рис", "type": "carb", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 10},
            {"name": "майонез", "type": "fat", "percent": 5}
        ]
    },
    "салат нисуаз": {
        "name": "Нисуаз",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "тунец", "type": "protein", "percent": 30},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "стручковая фасоль", "type": "vegetable", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "оливки", "type": "vegetable", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ]
    },
    "нисуаз": {
        "name": "Нисуаз",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "тунец", "type": "protein", "percent": 30},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "стручковая фасоль", "type": "vegetable", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "оливки", "type": "vegetable", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ]
    },
    "салат вальдорф": {
        "name": "Вальдорф",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "яблоко", "type": "fruit", "percent": 30},
            {"name": "сельдерей", "type": "vegetable", "percent": 25},
            {"name": "грецкий орех", "type": "nut", "percent": 20},
            {"name": "виноград", "type": "fruit", "percent": 15},
            {"name": "майонез", "type": "fat", "percent": 10}
        ]
    },
    "табуле": {
        "name": "Табуле",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "булгур", "type": "carb", "percent": 30},
            {"name": "петрушка", "type": "herb", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 20},
            {"name": "мята", "type": "herb", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ]
    },
    "салат табуле": {
        "name": "Табуле",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "булгур", "type": "carb", "percent": 30},
            {"name": "петрушка", "type": "herb", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 20},
            {"name": "мята", "type": "herb", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ]
    },
    "коул слоу": {
        "name": "Коул слоу",
        "category": "salad",
        "default_weight": 150,
        "ingredients": [
            {"name": "капуста белокочанная", "type": "vegetable", "percent": 60},
            {"name": "морковь", "type": "vegetable", "percent": 20},
            {"name": "майонез", "type": "fat", "percent": 20}
        ]
    },
    "салат из свеклы с чесноком": {
        "name": "Салат из свеклы с чесноком",
        "category": "salad",
        "default_weight": 150,
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 80},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "fat", "percent": 15}
        ]
    },
    "салат из моркови с изюмом": {
        "name": "Салат из моркови с изюмом",
        "category": "salad",
        "default_weight": 150,
        "ingredients": [
            {"name": "морковь", "type": "vegetable", "percent": 70},
            {"name": "изюм", "type": "fruit", "percent": 20},
            {"name": "сметана", "type": "dairy", "percent": 10}
        ]
    },
    "салат с тунцом и фасолью": {
        "name": "Салат с тунцом и фасолью",
        "category": "salad",
        "default_weight": 220,
        "ingredients": [
            {"name": "тунец консервированный", "type": "protein", "percent": 30},
            {"name": "фасоль красная", "type": "carb", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 20},
            {"name": "лук красный", "type": "vegetable", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ]
    },
    "салат с печенью трески": {
        "name": "Салат с печенью трески",
        "category": "salad",
        "default_weight": 200,
        "ingredients": [
            {"name": "печень трески", "type": "protein", "percent": 30},
            {"name": "яйцо", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10}
        ]
    },
    "салат с курицей и ананасом": {
        "name": "Салат с курицей и ананасом",
        "category": "salad",
        "default_weight": 220,
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 35},
            {"name": "ананас консервированный", "type": "fruit", "percent": 30},
            {"name": "сыр", "type": "dairy", "percent": 20},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "майонез", "type": "fat", "percent": 10}
        ]
    },
    "салат с фетой и арбузом": {
        "name": "Салат с фетой и арбузом",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "арбуз", "type": "fruit", "percent": 50},
            {"name": "фета", "type": "dairy", "percent": 25},
            {"name": "мята", "type": "herb", "percent": 5},
            {"name": "руккола", "type": "vegetable", "percent": 15},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "панцанелла": {
        "name": "Панцанелла",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 35},
            {"name": "огурцы", "type": "vegetable", "percent": 20},
            {"name": "лук красный", "type": "vegetable", "percent": 5},
            {"name": "базилик", "type": "herb", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "салат с киноа и овощами": {
        "name": "Салат с киноа и овощами",
        "category": "salad",
        "default_weight": 250,
        "ingredients": [
            {"name": "киноа", "type": "carb", "percent": 30},
            {"name": "помидоры черри", "type": "vegetable", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 20},
            {"name": "перец болгарский", "type": "vegetable", "percent": 15},
            {"name": "фета", "type": "dairy", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },

    # ========== СУПЫ ==========
    "борщ": {
        "name": "Борщ",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 15},
            {"name": "капуста", "type": "vegetable", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "мясо", "type": "protein", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "вода", "type": "other", "percent": 25}
        ]
    },
    "щи": {
        "name": "Щи",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "мясо", "type": "protein", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "вода", "type": "other", "percent": 30}
        ]
    },
    "солянка": {
        "name": "Солянка",
        "category": "soup",
        "default_weight": 350,
        "ingredients": [
            {"name": "колбаса", "type": "protein", "percent": 15},
            {"name": "мясо", "type": "protein", "percent": 10},
            {"name": "огурцы", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "оливки", "type": "vegetable", "percent": 5},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "вода", "type": "other", "percent": 50}
        ]
    },
    "куриный суп": {
        "name": "Куриный суп",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вермишель", "type": "carb", "percent": 5},
            {"name": "вода", "type": "other", "percent": 50}
        ]
    },
    "куриный суп с лапшой": {
        "name": "Куриный суп с лапшой",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "лапша", "type": "carb", "percent": 10},
            {"name": "вода", "type": "other", "percent": 50}
        ]
    },
    "рассольник": {
        "name": "Рассольник",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "огурцы соленые", "type": "vegetable", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "перловка", "type": "carb", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "мясо", "type": "protein", "percent": 10},
            {"name": "вода", "type": "other", "percent": 35}
        ]
    },
    "уха": {
        "name": "Уха",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "other", "percent": 50}
        ]
    },
    "грибной суп": {
        "name": "Грибной суп",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "грибы", "type": "protein", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "вода", "type": "other", "percent": 55}
        ]
    },
    "сырный суп": {
        "name": "Сырный суп",
        "category": "soup",
        "default_weight": 250,
        "ingredients": [
            {"name": "сыр плавленый", "type": "dairy", "percent": 15},
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "курица", "type": "protein", "percent": 10},
            {"name": "вода", "type": "other", "percent": 45}
        ]
    },
    "том ям": {
        "name": "Том Ям",
        "category": "soup",
        "default_weight": 350,
        "ingredients": [
            {"name": "креветки", "type": "protein", "percent": 15},
            {"name": "курица", "type": "protein", "percent": 10},
            {"name": "грибы", "type": "protein", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "кокосовое молоко", "type": "dairy", "percent": 20},
            {"name": "бульон", "type": "other", "percent": 40}
        ]
    },
    "фо бо": {
        "name": "Фо Бо",
        "category": "soup",
        "default_weight": 400,
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "рисовая лапша", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "зелень", "type": "herb", "percent": 5},
            {"name": "бульон", "type": "other", "percent": 55}
        ]
    },
    "минестроне": {
        "name": "Минестроне",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сельдерей", "type": "vegetable", "percent": 5},
            {"name": "фасоль", "type": "carb", "percent": 10},
            {"name": "кабачки", "type": "vegetable", "percent": 10},
            {"name": "бульон", "type": "other", "percent": 45}
        ]
    },
    "гаспачо": {
        "name": "Гаспачо",
        "category": "soup",
        "default_weight": 250,
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 60},
            {"name": "огурцы", "type": "vegetable", "percent": 20},
            {"name": "перец болгарский", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "оливковое масло", "type": "fat", "percent": 5}
        ]
    },
    "чечевичный суп": {
        "name": "Чечевичный суп",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "чечевица", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "вода", "type": "other", "percent": 55}
        ]
    },
    "гороховый суп": {
        "name": "Гороховый суп",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "горох", "type": "carb", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "мясо", "type": "protein", "percent": 10},
            {"name": "вода", "type": "other", "percent": 50}
        ]
    },
    "окрошка": {
        "name": "Окрошка",
        "category": "soup",
        "default_weight": 350,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 15},
            {"name": "колбаса", "type": "protein", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "редис", "type": "vegetable", "percent": 10},
            {"name": "зелень", "type": "herb", "percent": 5},
            {"name": "кефир", "type": "dairy", "percent": 35}
        ]
    },
    "свекольник": {
        "name": "Свекольник",
        "category": "soup",
        "default_weight": 300,
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 10},
            {"name": "огурцы", "type": "vegetable", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "кефир", "type": "dairy", "percent": 50}
        ]
    },
    "тыквенный суп пюре": {
        "name": "Тыквенный суп-пюре",
        "category": "soup",
        "default_weight": 250,
        "ingredients": [
            {"name": "тыква", "type": "vegetable", "percent": 40},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "бульон", "type": "other", "percent": 30}
        ]
    },
    "брокколи суп пюре": {
        "name": "Суп-пюре из брокколи",
        "category": "soup",
        "default_weight": 250,
        "ingredients": [
            {"name": "брокколи", "type": "vegetable", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "сыр", "type": "dairy", "percent": 5},
            {"name": "бульон", "type": "other", "percent": 30}
        ]
    },
    "лапша быстрого приготовления": {
        "name": "Лапша быстрого приготовления",
        "category": "soup",
        "default_weight": 250,
        "ingredients": [
            {"name": "лапша", "type": "carb", "percent": 60},
            {"name": "вода", "type": "other", "percent": 40}
        ]
    },
    "доширак": {
        "name": "Доширак",
        "category": "soup",
        "default_weight": 250,
        "ingredients": [
            {"name": "лапша", "type": "carb", "percent": 60},
            {"name": "вода", "type": "other", "percent": 40}
        ]
    },
    "роллтон": {
        "name": "Роллтон",
        "category": "soup",
        "default_weight": 250,
        "ingredients": [
            {"name": "лапша", "type": "carb", "percent": 60},
            {"name": "вода", "type": "other", "percent": 40}
        ]
    },
    "мивина": {
        "name": "Мивина",
        "category": "soup",
        "default_weight": 250,
        "ingredients": [
            {"name": "лапша", "type": "carb", "percent": 60},
            {"name": "вода", "type": "other", "percent": 40}
        ]
    },

    # ========== ВТОРЫЕ БЛЮДА ==========
    "гречка с мясом": {
        "name": "Гречка с мясом",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 40},
            {"name": "мясо", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "рис с курицей": {
        "name": "Рис с курицей",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "макароны с сыром": {
        "name": "Макароны с сыром",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 60},
            {"name": "сыр", "type": "dairy", "percent": 25},
            {"name": "масло сливочное", "type": "fat", "percent": 15}
        ]
    },
    "макароны по флотски": {
        "name": "Макароны по-флотски",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 50},
            {"name": "фарш", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "пюре картофельное": {
        "name": "Пюре картофельное",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 80},
            {"name": "молоко", "type": "dairy", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "картофельное пюре": {
        "name": "Пюре картофельное",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 80},
            {"name": "молоко", "type": "dairy", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "картошка с мясом": {
        "name": "Картошка с мясом",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 50},
            {"name": "мясо", "type": "protein", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "жаркое": {
        "name": "Жаркое",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "мясо", "type": "protein", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "жаркое по домашнему": {
        "name": "Жаркое по-домашнему",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "бефстроганов": {
        "name": "Бефстроганов",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "плов": {
        "name": "Плов",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "мясо", "type": "protein", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "плов с курицей": {
        "name": "Плов с курицей",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "курица", "type": "protein", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "плов со свининой": {
        "name": "Плов со свининой",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "свинина", "type": "protein", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "плов с говядиной": {
        "name": "Плов с говядиной",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "говядина", "type": "protein", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "плов с бараниной": {
        "name": "Плов с бараниной",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "баранина", "type": "protein", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "рис с овощами": {
        "name": "Рис с овощами",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 50},
            {"name": "перец болгарский", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "кукуруза", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "гречка с грибами": {
        "name": "Гречка с грибами",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 50},
            {"name": "грибы", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "чечевица с овощами": {
        "name": "Чечевица с овощами",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "чечевица", "type": "carb", "percent": 50},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "курица запеченная": {
        "name": "Курица запеченная",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 80},
            {"name": "специи", "type": "other", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "куриная грудка на гриле": {
        "name": "Куриная грудка на гриле",
        "category": "main",
        "default_weight": 180,
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 90},
            {"name": "специи", "type": "other", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "стейк из говядины": {
        "name": "Стейк из говядины",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 95},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "котлеты": {
        "name": "Котлеты",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "фарш", "type": "protein", "percent": 70},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "хлеб", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "котлеты куриные": {
        "name": "Котлеты куриные",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "куриный фарш", "type": "protein", "percent": 75},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "хлеб", "type": "carb", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "котлеты рыбные": {
        "name": "Котлеты рыбные",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "рыбный фарш", "type": "protein", "percent": 75},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "хлеб", "type": "carb", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "тефтели": {
        "name": "Тефтели",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "фарш", "type": "protein", "percent": 50},
            {"name": "рис", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "томатный соус", "type": "sauce", "percent": 15},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "голубцы": {
        "name": "Голубцы",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 30},
            {"name": "фарш", "type": "protein", "percent": 30},
            {"name": "рис", "type": "carb", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 10}
        ]
    },
    "перец фаршированный": {
        "name": "Перец фаршированный",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "перец болгарский", "type": "vegetable", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 25},
            {"name": "рис", "type": "carb", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "томатный соус", "type": "sauce", "percent": 10}
        ]
    },
    "запеканка картофельная": {
        "name": "Запеканка картофельная",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 60},
            {"name": "фарш", "type": "protein", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 10}
        ]
    },
    "запеканка творожная": {
        "name": "Запеканка творожная",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 60},
            {"name": "манка", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "изюм", "type": "fruit", "percent": 5}
        ]
    },
    "омлет": {
        "name": "Омлет",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "яйцо", "type": "protein", "percent": 60},
            {"name": "молоко", "type": "dairy", "percent": 30},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "яичница": {
        "name": "Яичница",
        "category": "main",
        "default_weight": 100,
        "ingredients": [
            {"name": "яйцо", "type": "protein", "percent": 85},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "глазунья": {
        "name": "Глазунья",
        "category": "main",
        "default_weight": 100,
        "ingredients": [
            {"name": "яйцо", "type": "protein", "percent": 85},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "паста карбонара": {
        "name": "Паста Карбонара",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 50},
            {"name": "бекон", "type": "protein", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "пармезан", "type": "dairy", "percent": 15},
            {"name": "масло оливковое", "type": "fat", "percent": 5}
        ]
    },
    "паста болоньезе": {
        "name": "Паста Болоньезе",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 25},
            {"name": "томатный соус", "type": "sauce", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "пармезан", "type": "dairy", "percent": 5}
        ]
    },
    "лазанья": {
        "name": "Лазанья",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "листы для лазаньи", "type": "carb", "percent": 25},
            {"name": "фарш", "type": "protein", "percent": 25},
            {"name": "томатный соус", "type": "sauce", "percent": 15},
            {"name": "соус бешамель", "type": "sauce", "percent": 20},
            {"name": "сыр", "type": "dairy", "percent": 15}
        ]
    },
    "ризотто": {
        "name": "Ризотто",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 50},
            {"name": "бульон", "type": "other", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сыр пармезан", "type": "dairy", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "ризотто с грибами": {
        "name": "Ризотто с грибами",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "грибы", "type": "protein", "percent": 20},
            {"name": "бульон", "type": "other", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сыр пармезан", "type": "dairy", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "курица тушеная": {
        "name": "Курица тушеная",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 10},
            {"name": "вода", "type": "other", "percent": 10}
        ]
    },
    "рыба жареная": {
        "name": "Рыба жареная",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 70},
            {"name": "мука", "type": "carb", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 20}
        ]
    },
    "рыба запеченная": {
        "name": "Рыба запеченная",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 75},
            {"name": "лимон", "type": "fruit", "percent": 5},
            {"name": "специи", "type": "other", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "рыба на пару": {
        "name": "Рыба на пару",
        "category": "main",
        "default_weight": 180,
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 95},
            {"name": "лимон", "type": "fruit", "percent": 5}
        ]
    },
    "тушеная капуста": {
        "name": "Тушеная капуста",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 70},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "рагу овощное": {
        "name": "Рагу овощное",
        "category": "main",
        "default_weight": 250,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 30},
            {"name": "кабачки", "type": "vegetable", "percent": 20},
            {"name": "баклажаны", "type": "vegetable", "percent": 15},
            {"name": "перец болгарский", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "картошка жареная": {
        "name": "Картошка жареная",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 75},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "картошка отварная": {
        "name": "Картошка отварная",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 95},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "картошка в мундире": {
        "name": "Картошка в мундире",
        "category": "main",
        "default_weight": 200,
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 100}
        ]
    },
    "брокколи отварная": {
        "name": "Брокколи отварная",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "брокколи", "type": "vegetable", "percent": 100}
        ]
    },
    "цветная капуста": {
        "name": "Цветная капуста",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "цветная капуста", "type": "vegetable", "percent": 100}
        ]
    },
    "фасоль стручковая": {
        "name": "Фасоль стручковая",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "стручковая фасоль", "type": "vegetable", "percent": 100}
        ]
    },
    "шпинат": {
        "name": "Шпинат",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "шпинат", "type": "vegetable", "percent": 100}
        ]
    },
    "спаржа": {
        "name": "Спаржа",
        "category": "main",
        "default_weight": 150,
        "ingredients": [
            {"name": "спаржа", "type": "vegetable", "percent": 100}
        ]
    },

    # ========== ВЫПЕЧКА И ДЕСЕРТЫ ==========
    "блины": {
        "name": "Блины",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 50},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "оладьи": {
        "name": "Оладьи",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 35},
            {"name": "кефир", "type": "dairy", "percent": 45},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "сырники": {
        "name": "Сырники",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 70},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 5}
        ]
    },
    "запеканка творожная": {
        "name": "Запеканка творожная",
        "category": "dessert",
        "default_weight": 200,
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 60},
            {"name": "манка", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "изюм", "type": "fruit", "percent": 5}
        ]
    },
    "ватрушка": {
        "name": "Ватрушка",
        "category": "dessert",
        "default_weight": 100,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "творог", "type": "dairy", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "пирожок с капустой": {
        "name": "Пирожок с капустой",
        "category": "dessert",
        "default_weight": 100,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "капуста", "type": "vegetable", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "пирожок с картошкой": {
        "name": "Пирожок с картошкой",
        "category": "dessert",
        "default_weight": 100,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "пирожок с яблоком": {
        "name": "Пирожок с яблоком",
        "category": "dessert",
        "default_weight": 100,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "яблоко", "type": "fruit", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "пирожок с вишней": {
        "name": "Пирожок с вишней",
        "category": "dessert",
        "default_weight": 100,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "вишня", "type": "fruit", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "пирожок с мясом": {
        "name": "Пирожок с мясом",
        "category": "dessert",
        "default_weight": 120,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "мясо", "type": "protein", "percent": 35},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "чебурек": {
        "name": "Чебурек",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "мясо", "type": "protein", "percent": 35},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "вода", "type": "other", "percent": 5},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "беляш": {
        "name": "Беляш",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "мясо", "type": "protein", "percent": 35},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 15}
        ]
    },
    "самса": {
        "name": "Самса",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "мясо", "type": "protein", "percent": 35},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "хачапури": {
        "name": "Хачапури",
        "category": "dessert",
        "default_weight": 200,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "сыр", "type": "dairy", "percent": 40},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 20}
        ]
    },
    "шарлотка": {
        "name": "Шарлотка",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "яблоко", "type": "fruit", "percent": 40},
            {"name": "мука", "type": "carb", "percent": 25},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "чизкейк": {
        "name": "Чизкейк",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "сыр сливочный", "type": "dairy", "percent": 50},
            {"name": "печенье", "type": "carb", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "тирамису": {
        "name": "Тирамису",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "сыр маскарпоне", "type": "dairy", "percent": 40},
            {"name": "печенье савоярди", "type": "carb", "percent": 20},
            {"name": "кофе", "type": "other", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 10}
        ]
    },
    "медовик": {
        "name": "Медовик",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 25},
            {"name": "сгущенка", "type": "dairy", "percent": 40},
            {"name": "мед", "type": "carb", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "наполеон": {
        "name": "Наполеон",
        "category": "dessert",
        "default_weight": 200,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 25},
            {"name": "масло сливочное", "type": "fat", "percent": 20},
            {"name": "заварной крем", "type": "dairy", "percent": 50},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "эклер": {
        "name": "Эклер",
        "category": "dessert",
        "default_weight": 80,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 20},
            {"name": "заварной крем", "type": "dairy", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "кекс": {
        "name": "Кекс",
        "category": "dessert",
        "default_weight": 80,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 20},
            {"name": "изюм", "type": "fruit", "percent": 5}
        ]
    },
    "печенье": {
        "name": "Печенье",
        "category": "dessert",
        "default_weight": 50,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 50},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "вафли": {
        "name": "Вафли",
        "category": "dessert",
        "default_weight": 50,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "сахар", "type": "carb", "percent": 30},
            {"name": "масло сливочное", "type": "fat", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 10}
        ]
    },
    "панкейки": {
        "name": "Панкейки",
        "category": "dessert",
        "default_weight": 150,
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 40},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "масло растительное", "type": "fat", "percent": 10}
        ]
    },
    "фруктовый салат": {
        "name": "Фруктовый салат",
        "category": "dessert",
        "default_weight": 200,
        "ingredients": [
            {"name": "яблоко", "type": "fruit", "percent": 25},
            {"name": "банан", "type": "fruit", "percent": 25},
            {"name": "апельсин", "type": "fruit", "percent": 25},
            {"name": "йогурт", "type": "dairy", "percent": 25}
        ]
    },
    "йогурт с ягодами": {
        "name": "Йогурт с ягодами",
        "category": "dessert",
        "default_weight": 200,
        "ingredients": [
            {"name": "йогурт", "type": "dairy", "percent": 70},
            {"name": "клубника", "type": "fruit", "percent": 15},
            {"name": "черника", "type": "fruit", "percent": 15}
        ]
    },
    "творог с фруктами": {
        "name": "Творог с фруктами",
        "category": "dessert",
        "default_weight": 200,
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 60},
            {"name": "банан", "type": "fruit", "percent": 20},
            {"name": "яблоко", "type": "fruit", "percent": 20}
        ]
    },
    "смузи": {
        "name": "Смузи",
        "category": "dessert",
        "default_weight": 250,
        "ingredients": [
            {"name": "банан", "type": "fruit", "percent": 30},
            {"name": "клубника", "type": "fruit", "percent": 30},
            {"name": "йогурт", "type": "dairy", "percent": 40}
        ]
    },
    "смузи банан-клубника": {
        "name": "Смузи банан-клубника",
        "category": "dessert",
        "default_weight": 250,
        "ingredients": [
            {"name": "банан", "type": "fruit", "percent": 30},
            {"name": "клубника", "type": "fruit", "percent": 30},
            {"name": "йогурт", "type": "dairy", "percent": 40}
        ]
    },
    "смуби": {
        "name": "Смузи",
        "category": "dessert",
        "default_weight": 250,
        "ingredients": [
            {"name": "банан", "type": "fruit", "percent": 30},
            {"name": "клубника", "type": "fruit", "percent": 30},
            {"name": "йогурт", "type": "dairy", "percent": 40}
        ]
    },
    "зеленый смузи": {
        "name": "Зеленый смузи",
        "category": "dessert",
        "default_weight": 250,
        "ingredients": [
            {"name": "шпинат", "type": "vegetable", "percent": 30},
            {"name": "банан", "type": "fruit", "percent": 30},
            {"name": "яблоко", "type": "fruit", "percent": 20},
            {"name": "вода", "type": "other", "percent": 20}
        ]
    },

    # ========== ЗАВТРАКИ ==========
    "каша овсяная": {
        "name": "Каша овсяная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "овсянка", "type": "carb", "percent": 20},
            {"name": "молоко", "type": "dairy", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "овсянка": {
        "name": "Каша овсяная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "овсянка", "type": "carb", "percent": 20},
            {"name": "молоко", "type": "dairy", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "геркулес": {
        "name": "Каша овсяная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "овсянка", "type": "carb", "percent": 20},
            {"name": "молоко", "type": "dairy", "percent": 70},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "каша гречневая": {
        "name": "Каша гречневая",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 60},
            {"name": "масло сливочное", "type": "fat", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "гречневая каша": {
        "name": "Каша гречневая",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 60},
            {"name": "масло сливочное", "type": "fat", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "каша рисовая": {
        "name": "Каша рисовая",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "рисовая каша": {
        "name": "Каша рисовая",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "каша пшенная": {
        "name": "Каша пшенная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "пшено", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "пшенная каша": {
        "name": "Каша пшенная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "пшено", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "каша манная": {
        "name": "Каша манная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "манка", "type": "carb", "percent": 15},
            {"name": "молоко", "type": "dairy", "percent": 75},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "манная каша": {
        "name": "Каша манная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "манка", "type": "carb", "percent": 15},
            {"name": "молоко", "type": "dairy", "percent": 75},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "каша кукурузная": {
        "name": "Каша кукурузная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "кукурузная крупа", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "кукурузная каша": {
        "name": "Каша кукурузная",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "кукурузная крупа", "type": "carb", "percent": 25},
            {"name": "молоко", "type": "dairy", "percent": 65},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло сливочное", "type": "fat", "percent": 5}
        ]
    },
    "гранола с йогуртом": {
        "name": "Гранола с йогуртом",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "гранола", "type": "carb", "percent": 30},
            {"name": "йогурт", "type": "dairy", "percent": 60},
            {"name": "ягоды", "type": "fruit", "percent": 10}
        ]
    },
    "мюсли с молоком": {
        "name": "Мюсли с молоком",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "мюсли", "type": "carb", "percent": 30},
            {"name": "молоко", "type": "dairy", "percent": 70}
        ]
    },
    "творог со сметаной": {
        "name": "Творог со сметаной",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 70},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "сахар", "type": "carb", "percent": 10}
        ]
    },
    "тост с авокадо": {
        "name": "Тост с авокадо",
        "category": "breakfast",
        "default_weight": 150,
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 30},
            {"name": "авокадо", "type": "fruit", "percent": 50},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "специи", "type": "other", "percent": 5}
        ]
    },
    "бутерброд с сыром": {
        "name": "Бутерброд с сыром",
        "category": "breakfast",
        "default_weight": 80,
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 60},
            {"name": "сыр", "type": "dairy", "percent": 40}
        ]
    },
    "бутерброд с колбасой": {
        "name": "Бутерброд с колбасой",
        "category": "breakfast",
        "default_weight": 80,
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 50},
            {"name": "колбаса", "type": "protein", "percent": 40},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "бутерброд с маслом": {
        "name": "Бутерброд с маслом",
        "category": "breakfast",
        "default_weight": 60,
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 70},
            {"name": "масло сливочное", "type": "fat", "percent": 30}
        ]
    },
    "бутерброд с икрой": {
        "name": "Бутерброд с икрой",
        "category": "breakfast",
        "default_weight": 60,
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 50},
            {"name": "икра", "type": "protein", "percent": 40},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "сэндвич с курицей": {
        "name": "Сэндвич с курицей",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "хлеб", "type": "carb", "percent": 30},
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "салат", "type": "vegetable", "percent": 15},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "соус", "type": "sauce", "percent": 10}
        ]
    },
    "гамбургер": {
        "name": "Гамбургер",
        "category": "breakfast",
        "default_weight": 200,
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 30},
            {"name": "котлета", "type": "protein", "percent": 30},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "соус", "type": "sauce", "percent": 15}
        ]
    },
    "чизбургер": {
        "name": "Чизбургер",
        "category": "breakfast",
        "default_weight": 220,
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 25},
            {"name": "котлета", "type": "protein", "percent": 25},
            {"name": "сыр", "type": "dairy", "percent": 15},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "соус", "type": "sauce", "percent": 10}
        ]
    },
    "пицца": {
        "name": "Пицца",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "сыр", "type": "dairy", "percent": 25},
            {"name": "колбаса", "type": "protein", "percent": 15},
            {"name": "томатный соус", "type": "sauce", "percent": 10},
            {"name": "грибы", "type": "protein", "percent": 10}
        ]
    },
    "пицца маргарита": {
        "name": "Пицца Маргарита",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 45},
            {"name": "сыр моцарелла", "type": "dairy", "percent": 25},
            {"name": "томатный соус", "type": "sauce", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 10}
        ]
    },
    "пицца пепперони": {
        "name": "Пицца Пепперони",
        "category": "main",
        "default_weight": 300,
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "сыр", "type": "dairy", "percent": 25},
            {"name": "пепперони", "type": "protein", "percent": 20},
            {"name": "томатный соус", "type": "sauce", "percent": 15}
        ]
    },
    "хот дог": {
        "name": "Хот-дог",
        "category": "breakfast",
        "default_weight": 150,
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 40},
            {"name": "сосиска", "type": "protein", "percent": 30},
            {"name": "кетчуп", "type": "sauce", "percent": 15},
            {"name": "горчица", "type": "sauce", "percent": 15}
        ]
    },
    "шаурма": {
        "name": "Шаурма",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "лаваш", "type": "carb", "percent": 20},
            {"name": "курица", "type": "protein", "percent": 25},
            {"name": "капуста", "type": "vegetable", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "соус", "type": "sauce", "percent": 10}
        ]
    },
    "шаверма": {
        "name": "Шаурма",
        "category": "main",
        "default_weight": 350,
        "ingredients": [
            {"name": "лаваш", "type": "carb", "percent": 20},
            {"name": "курица", "type": "protein", "percent": 25},
            {"name": "капуста", "type": "vegetable", "percent": 20},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "соус", "type": "sauce", "percent": 10}
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
