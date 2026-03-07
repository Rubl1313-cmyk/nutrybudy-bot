"""
База данных готовых блюд с ПОЛНЫМ списком ингредиентов.
Используется для разбивки блюд на компоненты при распознавании.
Объединяет данные из dish_db.py и food_api.py (LOCAL_FOOD_DB).
"""
from utils.normalizer import normalize_product_name

# 🔥 БАЗА ГОТОВЫХ БЛЮД С ПОЛНЫМИ ИНГРЕДИЕНТАМИ
COMPOSITE_DISHES = {
    # ========== САЛАТЫ ==========
    "капрезе": {
        "name": "Капрезе",
        "category": "salad",
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
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 50},
            {"name": "морковь", "type": "vegetable", "percent": 30},
            {"name": "майонез", "type": "fat", "percent": 15},
            {"name": "уксус", "type": "sauce", "percent": 5}
        ]
    },
    "капустный салат": {
        "name": "Коул слоу",
        "category": "salad",
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 50},
            {"name": "морковь", "type": "vegetable", "percent": 30},
            {"name": "майонез", "type": "fat", "percent": 15},
            {"name": "уксус", "type": "sauce", "percent": 5}
        ]
    },
    
    # ========== СУПЫ ==========
    "борщ": {
        "name": "Борщ",
        "category": "soup",
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 20},
            {"name": "капуста", "type": "vegetable", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "говядина", "type": "protein", "percent": 20},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ]
    },
    "щи": {
        "name": "Щи",
        "category": "soup",
        "ingredients": [
            {"name": "капуста", "type": "vegetable", "percent": 40},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ]
    },
    "рассольник": {
        "name": "Рассольник",
        "category": "soup",
        "ingredients": [
            {"name": "соленые огурцы", "type": "vegetable", "percent": 25},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "перловка", "type": "carb", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "говядина", "type": "protein", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ]
    },
    "солянка": {
        "name": "Солянка",
        "category": "soup",
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 20},
            {"name": "колбаса", "type": "protein", "percent": 15},
            {"name": "соленые огурцы", "type": "vegetable", "percent": 15},
            {"name": "оливки", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 10},
            {"name": "лимон", "type": "fruit", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 5},
            {"name": "картофель", "type": "carb", "percent": 20}
        ]
    },
    "уха": {
        "name": "Уха",
        "category": "soup",
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 40},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "зелень", "type": "herb", "percent": 5},
            {"name": "лавровый лист", "type": "spice", "percent": 5}
        ]
    },
    "окрошка": {
        "name": "Окрошка",
        "category": "soup",
        "ingredients": [
            {"name": "квас", "type": "liquid", "percent": 40},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "колбаса", "type": "protein", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 10},
            {"name": "редис", "type": "vegetable", "percent": 10},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ]
    },
    "свекольник": {
        "name": "Свекольник",
        "category": "soup",
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 40},
            {"name": "кефир", "type": "dairy", "percent": 30},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "редис", "type": "vegetable", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5}
        ]
    },
    "грибной суп": {
        "name": "Грибной суп",
        "category": "soup",
        "ingredients": [
            {"name": "грибы", "type": "vegetable", "percent": 35},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "зелень", "type": "herb", "percent": 5}
        ]
    },
    "куриный суп": {
        "name": "Куриный суп",
        "category": "soup",
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 25},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "лапша", "type": "carb", "percent": 15},
            {"name": "зелень", "type": "herb", "percent": 5}
        ]
    },
    "том ям": {
        "name": "Том Ям",
        "category": "soup",
        "ingredients": [
            {"name": "креветки", "type": "protein", "percent": 25},
            {"name": "кокосовое молоко", "type": "liquid", "percent": 30},
            {"name": "грибы", "type": "vegetable", "percent": 15},
            {"name": "лемонграсс", "type": "herb", "percent": 5},
            {"name": "лайм", "type": "fruit", "percent": 5},
            {"name": "бульон", "type": "liquid", "percent": 20}
        ]
    },
    "том-ям": {
        "name": "Том Ям",
        "category": "soup",
        "ingredients": [
            {"name": "креветки", "type": "protein", "percent": 25},
            {"name": "кокосовое молоко", "type": "liquid", "percent": 30},
            {"name": "грибы", "type": "vegetable", "percent": 15},
            {"name": "лемонграсс", "type": "herb", "percent": 5},
            {"name": "лайм", "type": "fruit", "percent": 5},
            {"name": "бульон", "type": "liquid", "percent": 20}
        ]
    },
    "фо": {
        "name": "Фо",
        "category": "soup",
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 25},
            {"name": "лапша рисовая", "type": "carb", "percent": 30},
            {"name": "бульон", "type": "liquid", "percent": 35},
            {"name": "зелень", "type": "herb", "percent": 5},
            {"name": "лайм", "type": "fruit", "percent": 5}
        ]
    },
    "фо-бо": {
        "name": "Фо-бо",
        "category": "soup",
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 25},
            {"name": "лапша рисовая", "type": "carb", "percent": 30},
            {"name": "бульон", "type": "liquid", "percent": 35},
            {"name": "зелень", "type": "herb", "percent": 5},
            {"name": "лайм", "type": "fruit", "percent": 5}
        ]
    },
    "рамен": {
        "name": "Рамен",
        "category": "soup",
        "ingredients": [
            {"name": "лапша", "type": "carb", "percent": 35},
            {"name": "свинина", "type": "protein", "percent": 25},
            {"name": "бульон", "type": "liquid", "percent": 30},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "водоросли", "type": "vegetable", "percent": 5}
        ]
    },
    "мисо суп": {
        "name": "Мисо суп",
        "category": "soup",
        "ingredients": [
            {"name": "мисо паста", "type": "sauce", "percent": 15},
            {"name": "тофу", "type": "protein", "percent": 20},
            {"name": "водоросли", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "бульон", "type": "liquid", "percent": 50}
        ]
    },
    "луковый суп": {
        "name": "Луковый суп",
        "category": "soup",
        "ingredients": [
            {"name": "лук", "type": "vegetable", "percent": 50},
            {"name": "бульон", "type": "liquid", "percent": 30},
            {"name": "сыр", "type": "dairy", "percent": 15},
            {"name": "гренки", "type": "carb", "percent": 5}
        ]
    },
    "гаспачо": {
        "name": "Гаспачо",
        "category": "soup",
        "ingredients": [
            {"name": "помидоры", "type": "vegetable", "percent": 40},
            {"name": "огурец", "type": "vegetable", "percent": 20},
            {"name": "перец", "type": "vegetable", "percent": 15},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "хлеб", "type": "carb", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ]
    },
    "минестроне": {
        "name": "Минестроне",
        "category": "soup",
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "кабачок", "type": "vegetable", "percent": 15},
            {"name": "макароны", "type": "carb", "percent": 15},
            {"name": "бульон", "type": "liquid", "percent": 10}
        ]
    },
    "харчо": {
        "name": "Харчо",
        "category": "soup",
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 30},
            {"name": "рис", "type": "carb", "percent": 20},
            {"name": "грецкие орехи", "type": "nut", "percent": 10},
            {"name": "ткемали", "type": "sauce", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 5},
            {"name": "бульон", "type": "liquid", "percent": 10}
        ]
    },
    "буйабес": {
        "name": "Буйабес",
        "category": "soup",
        "ingredients": [
            {"name": "рыба", "type": "protein", "percent": 35},
            {"name": "морепродукты", "type": "protein", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "шафран", "type": "spice", "percent": 5},
            {"name": "фенхель", "type": "vegetable", "percent": 10},
            {"name": "бульон", "type": "liquid", "percent": 15}
        ]
    },
    
    # ========== ПАСТА И МАКАРОНЫ ==========
    "спагетти": {
        "name": "Спагетти",
        "category": "pasta",
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 70},
            {"name": "томатный соус", "type": "sauce", "percent": 20},
            {"name": "пармезан", "type": "dairy", "percent": 10}
        ]
    },
    "спагетти болоньезе": {
        "name": "Спагетти Болоньезе",
        "category": "pasta",
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "пармезан", "type": "dairy", "percent": 5}
        ]
    },
    "спагетти карбонара": {
        "name": "Спагетти Карбонара",
        "category": "pasta",
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 45},
            {"name": "бекон", "type": "protein", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "сливки", "type": "dairy", "percent": 5}
        ]
    },
    "паста болоньезе": {
        "name": "Паста Болоньезе",
        "category": "pasta",
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5},
            {"name": "пармезан", "type": "dairy", "percent": 5}
        ]
    },
    "паста карбонара": {
        "name": "Паста Карбонара",
        "category": "pasta",
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 45},
            {"name": "бекон", "type": "protein", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "сливки", "type": "dairy", "percent": 5}
        ]
    },
    "лазанья": {
        "name": "Лазанья",
        "category": "pasta",
        "ingredients": [
            {"name": "листы для лазаньи", "type": "carb", "percent": 30},
            {"name": "фарш", "type": "protein", "percent": 25},
            {"name": "томатный соус", "type": "sauce", "percent": 20},
            {"name": "бешамель", "type": "sauce", "percent": 15},
            {"name": "пармезан", "type": "dairy", "percent": 10}
        ]
    },
    "ризотто": {
        "name": "Ризотто",
        "category": "pasta",
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "бульон", "type": "liquid", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "ньокки": {
        "name": "Ньокки",
        "category": "pasta",
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 50},
            {"name": "мука", "type": "carb", "percent": 30},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 10}
        ]
    },
    "феттучине": {
        "name": "Феттучине",
        "category": "pasta",
        "ingredients": [
            {"name": "феттучине", "type": "carb", "percent": 60},
            {"name": "сливки", "type": "dairy", "percent": 25},
            {"name": "пармезан", "type": "dairy", "percent": 15}
        ]
    },
    "пенне": {
        "name": "Пенне",
        "category": "pasta",
        "ingredients": [
            {"name": "пенне", "type": "carb", "percent": 60},
            {"name": "томатный соус", "type": "sauce", "percent": 25},
            {"name": "базилик", "type": "herb", "percent": 5},
            {"name": "пармезан", "type": "dairy", "percent": 10}
        ]
    },
    "фузилли": {
        "name": "Фузилли",
        "category": "pasta",
        "ingredients": [
            {"name": "фузилли", "type": "carb", "percent": 60},
            {"name": "песто", "type": "sauce", "percent": 30},
            {"name": "пармезан", "type": "dairy", "percent": 10}
        ]
    },
    "макароны": {
        "name": "Макароны",
        "category": "pasta",
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 70},
            {"name": "масло сливочное", "type": "fat", "percent": 20},
            {"name": "сыр", "type": "dairy", "percent": 10}
        ]
    },
    
    # ========== ПИЦЦА ==========
    "пицца": {
        "name": "Пицца",
        "category": "pizza",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "томатный соус", "type": "sauce", "percent": 15},
            {"name": "сыр", "type": "dairy", "percent": 25},
            {"name": "начинка", "type": "protein", "percent": 20}
        ]
    },
    "пицца маргарита": {
        "name": "Пицца Маргарита",
        "category": "pizza",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "томатный соус", "type": "sauce", "percent": 20},
            {"name": "моцарелла", "type": "dairy", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 5},
            {"name": "базилик", "type": "herb", "percent": 5}
        ]
    },
    "пицца пепперони": {
        "name": "Пицца Пепперони",
        "category": "pizza",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 35},
            {"name": "томатный соус", "type": "sauce", "percent": 15},
            {"name": "моцарелла", "type": "dairy", "percent": 25},
            {"name": "пепперони", "type": "protein", "percent": 25}
        ]
    },
    "пицца четыре сыра": {
        "name": "Пицца 4 сыра",
        "category": "pizza",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 35},
            {"name": "сливки", "type": "dairy", "percent": 15},
            {"name": "моцарелла", "type": "dairy", "percent": 20},
            {"name": "пармезан", "type": "dairy", "percent": 15},
            {"name": "горгонзола", "type": "dairy", "percent": 15}
        ]
    },
    "пицца с грибами": {
        "name": "Пицца с грибами",
        "category": "pizza",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "томатный соус", "type": "sauce", "percent": 15},
            {"name": "моцарелла", "type": "dairy", "percent": 25},
            {"name": "грибы", "type": "vegetable", "percent": 20}
        ]
    },
    "пицца гавайская": {
        "name": "Гавайская пицца",
        "category": "pizza",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 35},
            {"name": "томатный соус", "type": "sauce", "percent": 15},
            {"name": "моцарелла", "type": "dairy", "percent": 25},
            {"name": "ветчина", "type": "protein", "percent": 15},
            {"name": "ананас", "type": "fruit", "percent": 10}
        ]
    },
    
    # ========== БУРГЕРЫ И ФАСТФУД ==========
    "бургер": {
        "name": "Бургер",
        "category": "fastfood",
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 30},
            {"name": "котлета", "type": "protein", "percent": 35},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сыр", "type": "dairy", "percent": 10}
        ]
    },
    "гамбургер": {
        "name": "Гамбургер",
        "category": "fastfood",
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 30},
            {"name": "котлета", "type": "protein", "percent": 35},
            {"name": "салат", "type": "vegetable", "percent": 10},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "соус", "type": "sauce", "percent": 10}
        ]
    },
    "чизбургер": {
        "name": "Чизбургер",
        "category": "fastfood",
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 28},
            {"name": "котлета", "type": "protein", "percent": 32},
            {"name": "сыр чеддер", "type": "dairy", "percent": 15},
            {"name": "салат", "type": "vegetable", "percent": 8},
            {"name": "помидоры", "type": "vegetable", "percent": 8},
            {"name": "лук", "type": "vegetable", "percent": 4},
            {"name": "соус", "type": "sauce", "percent": 5}
        ]
    },
    "хот-дог": {
        "name": "Хот-дог",
        "category": "fastfood",
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 40},
            {"name": "сосиска", "type": "protein", "percent": 40},
            {"name": "кетчуп", "type": "sauce", "percent": 10},
            {"name": "горчица", "type": "sauce", "percent": 10}
        ]
    },
    "хотдог": {
        "name": "Хот-дог",
        "category": "fastfood",
        "ingredients": [
            {"name": "булочка", "type": "carb", "percent": 40},
            {"name": "сосиска", "type": "protein", "percent": 40},
            {"name": "кетчуп", "type": "sauce", "percent": 10},
            {"name": "горчица", "type": "sauce", "percent": 10}
        ]
    },
    "шаурма": {
        "name": "Шаурма",
        "category": "fastfood",
        "ingredients": [
            {"name": "лаваш", "type": "carb", "percent": 25},
            {"name": "курица", "type": "protein", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "капуста", "type": "vegetable", "percent": 10},
            {"name": "соус чесночный", "type": "sauce", "percent": 5}
        ]
    },
    "шаверма": {
        "name": "Шаверма",
        "category": "fastfood",
        "ingredients": [
            {"name": "лаваш", "type": "carb", "percent": 25},
            {"name": "курица", "type": "protein", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "капуста", "type": "vegetable", "percent": 10},
            {"name": "соус чесночный", "type": "sauce", "percent": 5}
        ]
    },
    "гирос": {
        "name": "Гирос",
        "category": "fastfood",
        "ingredients": [
            {"name": "пита", "type": "carb", "percent": 25},
            {"name": "мясо", "type": "protein", "percent": 30},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "картофель фри", "type": "carb", "percent": 10},
            {"name": "дзадзики", "type": "sauce", "percent": 10}
        ]
    },
    "сувлаки": {
        "name": "Сувлаки",
        "category": "fastfood",
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 50},
            {"name": "перец", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "специи", "type": "spice", "percent": 5},
            {"name": "пита", "type": "carb", "percent": 10}
        ]
    },
    "картофель фри": {
        "name": "Картофель фри",
        "category": "fastfood",
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 80},
            {"name": "масло", "type": "fat", "percent": 20}
        ]
    },
    "фри": {
        "name": "Картофель фри",
        "category": "fastfood",
        "ingredients": [
            {"name": "картофель", "type": "carb", "percent": 80},
            {"name": "масло", "type": "fat", "percent": 20}
        ]
    },
    "наггетсы": {
        "name": "Наггетсы",
        "category": "fastfood",
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 60},
            {"name": "панировка", "type": "carb", "percent": 30},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "куриные наггетсы": {
        "name": "Наггетсы",
        "category": "fastfood",
        "ingredients": [
            {"name": "куриное филе", "type": "protein", "percent": 60},
            {"name": "панировка", "type": "carb", "percent": 30},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "крылья баффало": {
        "name": "Крылья Баффало",
        "category": "fastfood",
        "ingredients": [
            {"name": "куриные крылья", "type": "protein", "percent": 70},
            {"name": "соус баффало", "type": "sauce", "percent": 20},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "сельдерей", "type": "vegetable", "percent": 5}
        ]
    },
    
    # ========== РУССКИЕ БЛЮДА ==========
    "пельмени": {
        "name": "Пельмени",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ]
    },
    "вареники": {
        "name": "Вареники",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 50},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ]
    },
    "вареники с картошкой": {
        "name": "Вареники с картошкой",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 50},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "сметана", "type": "dairy", "percent": 5}
        ]
    },
    "вареники с творогом": {
        "name": "Вареники с творогом",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 45},
            {"name": "творог", "type": "dairy", "percent": 45},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "манты": {
        "name": "Манты",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 5}
        ]
    },
    "хинкали": {
        "name": "Хинкали",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 35},
            {"name": "фарш", "type": "protein", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "бульон", "type": "liquid", "percent": 5}
        ]
    },
    "чебуреки": {
        "name": "Чебуреки",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "беляши": {
        "name": "Беляши",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 45},
            {"name": "фарш", "type": "protein", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 10}
        ]
    },
    "самса": {
        "name": "Самса",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 45},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 5}
        ]
    },
    "плов": {
        "name": "Плов",
        "category": "main",
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "говядина", "type": "protein", "percent": 30},
            {"name": "морковь", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "гречка с мясом": {
        "name": "Гречка с мясом",
        "category": "main",
        "ingredients": [
            {"name": "гречка", "type": "carb", "percent": 50},
            {"name": "говядина", "type": "protein", "percent": 30},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10}
        ]
    },
    "котлеты": {
        "name": "Котлеты",
        "category": "main",
        "ingredients": [
            {"name": "фарш", "type": "protein", "percent": 70},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "хлеб", "type": "carb", "percent": 10},
            {"name": "яйцо", "type": "protein", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "шашлык": {
        "name": "Шашлык",
        "category": "main",
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "уксус", "type": "sauce", "percent": 5},
            {"name": "специи", "type": "spice", "percent": 5}
        ]
    },
    "шашлык из курицы": {
        "name": "Шашлык из курицы",
        "category": "main",
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 10}
        ]
    },
    "шашлык из баранины": {
        "name": "Шашлык из баранины",
        "category": "main",
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 80},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 10}
        ]
    },
    "люля-кебаб": {
        "name": "Люля-кебаб",
        "category": "main",
        "ingredients": [
            {"name": "баранина", "type": "protein", "percent": 70},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "сало", "type": "fat", "percent": 10},
            {"name": "зелень", "type": "herb", "percent": 5}
        ]
    },
    "бефстроганов": {
        "name": "Бефстроганов",
        "category": "main",
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "сметана", "type": "dairy", "percent": 20},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "грибы", "type": "vegetable", "percent": 10}
        ]
    },
    "гуляш": {
        "name": "Гуляш",
        "category": "main",
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 10},
            {"name": "мука", "type": "carb", "percent": 5},
            {"name": "бульон", "type": "liquid", "percent": 10}
        ]
    },
    "азу": {
        "name": "Азу",
        "category": "main",
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 45},
            {"name": "соленые огурцы", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "томатная паста", "type": "sauce", "percent": 10},
            {"name": "картофель", "type": "carb", "percent": 15}
        ]
    },
    "жаркое": {
        "name": "Жаркое",
        "category": "main",
        "ingredients": [
            {"name": "свинина", "type": "protein", "percent": 35},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "чеснок", "type": "vegetable", "percent": 5}
        ]
    },
    
    # ========== ЗАВТРАКИ ==========
    "омлет": {
        "name": "Омлет",
        "category": "breakfast",
        "ingredients": [
            {"name": "яйцо", "type": "protein", "percent": 60},
            {"name": "молоко", "type": "dairy", "percent": 20},
            {"name": "масло сливочное", "type": "fat", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 10}
        ]
    },
    "яичница": {
        "name": "Яичница",
        "category": "breakfast",
        "ingredients": [
            {"name": "яйцо", "type": "protein", "percent": 80},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "соль", "type": "spice", "percent": 5}
        ]
    },
    "блины": {
        "name": "Блины",
        "category": "breakfast",
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "молоко", "type": "dairy", "percent": 35},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "блинчики": {
        "name": "Блинчики",
        "category": "breakfast",
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "молоко", "type": "dairy", "percent": 35},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "масло сливочное", "type": "fat", "percent": 10}
        ]
    },
    "оладьи": {
        "name": "Оладьи",
        "category": "breakfast",
        "ingredients": [
            {"name": "мука", "type": "carb", "percent": 40},
            {"name": "кефир", "type": "dairy", "percent": 35},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 5},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "сырники": {
        "name": "Сырники",
        "category": "breakfast",
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 60},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "мука", "type": "carb", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10}
        ]
    },
    "запеканка": {
        "name": "Запеканка",
        "category": "breakfast",
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 50},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "манка", "type": "carb", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "сметана", "type": "dairy", "percent": 10}
        ]
    },
    "запеканка творожная": {
        "name": "Запеканка творожная",
        "category": "breakfast",
        "ingredients": [
            {"name": "творог", "type": "dairy", "percent": 50},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "манка", "type": "carb", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 10},
            {"name": "сметана", "type": "dairy", "percent": 10}
        ]
    },
    
    # ========== ДЕСЕРТЫ ==========
    "чизкейк": {
        "name": "Чизкейк",
        "category": "dessert",
        "ingredients": [
            {"name": "сыр сливочный", "type": "dairy", "percent": 40},
            {"name": "печенье", "type": "carb", "percent": 25},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "сахар", "type": "carb", "percent": 10}
        ]
    },
    "тирамису": {
        "name": "Тирамису",
        "category": "dessert",
        "ingredients": [
            {"name": "маскарпоне", "type": "dairy", "percent": 35},
            {"name": "савоярди", "type": "carb", "percent": 25},
            {"name": "кофе", "type": "liquid", "percent": 20},
            {"name": "яйцо", "type": "protein", "percent": 10},
            {"name": "какао", "type": "other", "percent": 10}
        ]
    },
    "наполеон": {
        "name": "Наполеон",
        "category": "dessert",
        "ingredients": [
            {"name": "тесто слоеное", "type": "carb", "percent": 40},
            {"name": "заварной крем", "type": "dairy", "percent": 40},
            {"name": "масло сливочное", "type": "fat", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 5}
        ]
    },
    "медовик": {
        "name": "Медовик",
        "category": "dessert",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "мед", "type": "carb", "percent": 20},
            {"name": "сгущенка", "type": "dairy", "percent": 25},
            {"name": "сметана", "type": "dairy", "percent": 15}
        ]
    },
    "брауни": {
        "name": "Брауни",
        "category": "dessert",
        "ingredients": [
            {"name": "шоколад", "type": "carb", "percent": 40},
            {"name": "масло сливочное", "type": "fat", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "сахар", "type": "carb", "percent": 15},
            {"name": "мука", "type": "carb", "percent": 5}
        ]
    },
    "панна-котта": {
        "name": "Панна-котта",
        "category": "dessert",
        "ingredients": [
            {"name": "сливки", "type": "dairy", "percent": 60},
            {"name": "сахар", "type": "carb", "percent": 20},
            {"name": "желатин", "type": "other", "percent": 10},
            {"name": "ваниль", "type": "spice", "percent": 10}
        ]
    },
    "мороженое": {
        "name": "Мороженое",
        "category": "dessert",
        "ingredients": [
            {"name": "молоко", "type": "dairy", "percent": 50},
            {"name": "сливки", "type": "dairy", "percent": 30},
            {"name": "сахар", "type": "carb", "percent": 20}
        ]
    },
    
    # ========== КАВКАЗСКАЯ КУХНЯ ==========
    "цыпленок табака": {
        "name": "Цыпленок табака",
        "category": "main",
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 70},
            {"name": "чеснок", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 10},
            {"name": "масло", "type": "fat", "percent": 10}
        ]
    },
    "чахохбили": {
        "name": "Чахохбили",
        "category": "main",
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 50},
            {"name": "помидоры", "type": "vegetable", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "чеснок", "type": "vegetable", "percent": 5},
            {"name": "вино", "type": "liquid", "percent": 5}
        ]
    },
    "сациви": {
        "name": "Сациви",
        "category": "main",
        "ingredients": [
            {"name": "курица", "type": "protein", "percent": 40},
            {"name": "грецкие орехи", "type": "nut", "percent": 30},
            {"name": "чеснок", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 10},
            {"name": "бульон", "type": "liquid", "percent": 10}
        ]
    },
    "хачапури": {
        "name": "Хачапури",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 40},
            {"name": "сыр", "type": "dairy", "percent": 50},
            {"name": "яйцо", "type": "protein", "percent": 10}
        ]
    },
    "лобио": {
        "name": "Лобио",
        "category": "main",
        "ingredients": [
            {"name": "фасоль", "type": "protein", "percent": 50},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "грецкие орехи", "type": "nut", "percent": 15},
            {"name": "чеснок", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 10}
        ]
    },
    "долма": {
        "name": "Долма",
        "category": "main",
        "ingredients": [
            {"name": "виноградные листья", "type": "vegetable", "percent": 20},
            {"name": "фарш", "type": "protein", "percent": 40},
            {"name": "рис", "type": "carb", "percent": 25},
            {"name": "лук", "type": "vegetable", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 5}
        ]
    },
    "мусака": {
        "name": "Мусака",
        "category": "main",
        "ingredients": [
            {"name": "баклажаны", "type": "vegetable", "percent": 30},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "фарш", "type": "protein", "percent": 25},
            {"name": "томаты", "type": "vegetable", "percent": 10},
            {"name": "бешамель", "type": "sauce", "percent": 10},
            {"name": "сыр", "type": "dairy", "percent": 5}
        ]
    },
    "дзадзики": {
        "name": "Дзадзики",
        "category": "sauce",
        "ingredients": [
            {"name": "йогурт", "type": "dairy", "percent": 60},
            {"name": "огурец", "type": "vegetable", "percent": 25},
            {"name": "чеснок", "type": "vegetable", "percent": 10},
            {"name": "укроп", "type": "herb", "percent": 5}
        ]
    },
    "хумус": {
        "name": "Хумус",
        "category": "sauce",
        "ingredients": [
            {"name": "нут", "type": "protein", "percent": 50},
            {"name": "тахини", "type": "sauce", "percent": 20},
            {"name": "чеснок", "type": "vegetable", "percent": 10},
            {"name": "лимон", "type": "fruit", "percent": 10},
            {"name": "оливковое масло", "type": "fat", "percent": 10}
        ]
    },
    "фалафель": {
        "name": "Фалафель",
        "category": "main",
        "ingredients": [
            {"name": "нут", "type": "protein", "percent": 50},
            {"name": "петрушка", "type": "herb", "percent": 20},
            {"name": "чеснок", "type": "vegetable", "percent": 10},
            {"name": "кунжут", "type": "nut", "percent": 10},
            {"name": "специи", "type": "spice", "percent": 10}
        ]
    },
    "кускус": {
        "name": "Кускус",
        "category": "main",
        "ingredients": [
            {"name": "кускус", "type": "carb", "percent": 50},
            {"name": "овощи", "type": "vegetable", "percent": 30},
            {"name": "нут", "type": "protein", "percent": 20}
        ]
    },
    "паэлья": {
        "name": "Паэлья",
        "category": "main",
        "ingredients": [
            {"name": "рис", "type": "carb", "percent": 40},
            {"name": "курица", "type": "protein", "percent": 20},
            {"name": "морепродукты", "type": "protein", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 10},
            {"name": "перец", "type": "vegetable", "percent": 5},
            {"name": "шафран", "type": "spice", "percent": 5}
        ]
    },
    "рататуй": {
        "name": "Рататуй",
        "category": "main",
        "ingredients": [
            {"name": "кабачок", "type": "vegetable", "percent": 25},
            {"name": "баклажан", "type": "vegetable", "percent": 25},
            {"name": "перец", "type": "vegetable", "percent": 20},
            {"name": "помидоры", "type": "vegetable", "percent": 20},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "чеснок", "type": "vegetable", "percent": 5}
        ]
    },
    "киш лорен": {
        "name": "Киш Лорен",
        "category": "main",
        "ingredients": [
            {"name": "тесто", "type": "carb", "percent": 30},
            {"name": "яйцо", "type": "protein", "percent": 25},
            {"name": "сливки", "type": "dairy", "percent": 20},
            {"name": "бекон", "type": "protein", "percent": 20},
            {"name": "сыр", "type": "dairy", "percent": 5}
        ]
    },
    "тортилья": {
        "name": "Тортилья",
        "category": "main",
        "ingredients": [
            {"name": "яйцо", "type": "protein", "percent": 40},
            {"name": "картофель", "type": "carb", "percent": 40},
            {"name": "лук", "type": "vegetable", "percent": 15},
            {"name": "масло", "type": "fat", "percent": 5}
        ]
    },
    "карбонара": {
        "name": "Карбонара",
        "category": "pasta",
        "ingredients": [
            {"name": "спагетти", "type": "carb", "percent": 45},
            {"name": "бекон", "type": "protein", "percent": 25},
            {"name": "яйцо", "type": "protein", "percent": 15},
            {"name": "пармезан", "type": "dairy", "percent": 10},
            {"name": "сливки", "type": "dairy", "percent": 5}
        ]
    },
    "болоньезе": {
        "name": "Болоньезе",
        "category": "pasta",
        "ingredients": [
            {"name": "макароны", "type": "carb", "percent": 40},
            {"name": "фарш", "type": "protein", "percent": 35},
            {"name": "помидоры", "type": "vegetable", "percent": 15},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "морковь", "type": "vegetable", "percent": 5}
        ]
    },
}

# 🔥 Ключевые ингредиенты для каждого блюда (основной белок)
KEY_INGREDIENTS = {
    "борщ": "говядина",
    "щи": "говядина",
    "рассольник": "говядина",
    "солянка": "говядина",
    "уха": "рыба",
    "окрошка": "колбаса",
    "грибной суп": "грибы",
    "куриный суп": "курица",
    "том ям": "креветки",
    "том-ям": "креветки",
    "фо": "говядина",
    "фо-бо": "говядина",
    "рамен": "свинина",
    "мисо суп": "тофу",
    "луковый суп": "лук",
    "гаспачо": "помидоры",
    "минестроне": "овощи",
    "харчо": "говядина",
    "буйабес": "рыба",
    "оливье": "колбаса",
    "винегрет": "свекла",
    "цезарь": "курица",
    "цезарь с курицей": "курица",
    "греческий салат": "фета",
    "капрезе": "моцарелла",
    "мимоза": "рыбные консервы",
    "селедка под шубой": "сельдь",
    "сельдь под шубой": "сельдь",
    "крабовый салат": "крабовые палочки",
    "нисуаз": "тунец",
    "вальдорф": "яблоко",
    "табуле": "булгур",
    "коул слоу": "капуста",
    "спагетти": "спагетти",
    "спагетти болоньезе": "фарш",
    "спагетти карбонара": "бекон",
    "паста болоньезе": "фарш",
    "паста карбонара": "бекон",
    "лазанья": "фарш",
    "ризотто": "рис",
    "пицца": "сыр",
    "пицца маргарита": "моцарелла",
    "пицца пепперони": "пепперони",
    "бургер": "котлета",
    "гамбургер": "котлета",
    "чизбургер": "котлета",
    "хот-дог": "сосиска",
    "шаурма": "курица",
    "шаверма": "курица",
    "пельмени": "фарш",
    "вареники": "картофель",
    "вареники с картошкой": "картофель",
    "манты": "фарш",
    "хинкали": "фарш",
    "чебуреки": "фарш",
    "беляши": "фарш",
    "плов": "говядина",
    "гречка с мясом": "говядина",
    "котлеты": "фарш",
    "шашлык": "свинина",
    "шашлык из курицы": "курица",
    "шашлык из баранины": "баранина",
    "омлет": "яйцо",
    "яичница": "яйцо",
    "блины": "мука",
    "блинчики": "мука",
    "оладьи": "мука",
    "сырники": "творог",
    "запеканка": "творог",
    "чизкейк": "сыр сливочный",
    "тирамису": "маскарпоне",
    "наполеон": "тесто",
    "медовик": "мед",
    "брауни": "шоколад",
    "мороженое": "молоко",
    "хумус": "нут",
    "фалафель": "нут",
    "шаурма": "курица",
    "гирос": "мясо",
    "сувлаки": "свинина",
    "кускус": "кускус",
    "паэлья": "рис",
    "рататуй": "кабачок",
    "киш лорен": "бекон",
    "тортилья": "яйцо",
    "мусака": "фарш",
    "дзадзики": "йогурт",
    "долма": "фарш",
    "лобио": "фасоль",
    "хачапури": "сыр",
    "сациви": "курица",
    "чахохбили": "курица",
    "цыпленок табака": "курица",
    "бефстроганов": "говядина",
    "гуляш": "говядина",
    "азу": "говядина",
    "жаркое": "свинина",
    "люля-кебаб": "баранина",
    "карбонара": "бекон",
    "болоньезе": "фарш",
}


def get_dish_ingredients(dish_name: str, total_weight: int = 300) -> list:
    """
    Возвращает список ингредиентов для блюда с рассчитанными весами.
    
    Args:
        dish_name: Название блюда
        total_weight: Общий вес порции (граммы)
    
    Returns:
        Список ингредиентов с весами
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
    
    # Рассчитываем веса на основе процентов
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
                'confidence': 0.8
            })
    
    return result


def find_matching_dish(ingredients: list, threshold: float = 0.3) -> tuple:
    """
    Ищет блюдо, чей набор ингредиентов наиболее похож на предоставленный.
    """
    if not ingredients:
        return None, 0.0
    
    input_names = set(ing.get('name', '').lower() for ing in ingredients if ing.get('name'))
    
    best_match = None
    best_score = 0.0
    
    for dish_name, dish_data in COMPOSITE_DISHES.items():
        dish_ingredients = dish_data.get('ingredients', [])
        dish_names = set(ing.get('name', '').lower() for ing in dish_ingredients)
        
        if not dish_names:
            continue
        
        intersection = len(input_names & dish_names)
        union = len(input_names | dish_names)
        score = intersection / union if union > 0 else 0.0
        
        # Штрафуем если ключевой ингредиент отсутствует
        key = KEY_INGREDIENTS.get(dish_name)
        if key and key.lower() not in input_names:
            score *= 0.5
        
        if score > best_score:
            best_score = score
            best_match = dish_name
    
    if best_score >= threshold:
        return best_match, best_score
    
    return None, best_score

# ========== ДОБАВИТЬ В КОНЕЦ ФАЙЛА ==========

def calculate_dish_nutrition(dish_name: str, total_weight: int = 300) -> Dict:
    """
    🔥 Рассчитывает КБЖУ для готового блюда
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
