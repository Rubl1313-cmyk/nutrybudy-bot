"""
База данных готовых блюд с ПОЛНЫМ списком ингредиентов.
Используется для разбивки блюд на компоненты при распознавании.
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
            {"name": "салат романо", "type": "vegetable", "percent": 40},
            {"name": "пармезан", "type": "dairy", "percent": 15},
            {"name": "сухарики", "type": "carb", "percent": 10},
            {"name": "соус цезарь", "type": "sauce", "percent": 5}
        ]
    },
    "салат цезарь": {
        "name": "Цезарь",
        "category": "salad",
        "ingredients": [
            {"name": "куриная грудка", "type": "protein", "percent": 30},
            {"name": "салат романо", "type": "vegetable", "percent": 40},
            {"name": "пармезан", "type": "dairy", "percent": 15},
            {"name": "сухарики", "type": "carb", "percent": 10},
            {"name": "соус цезарь", "type": "sauce", "percent": 5}
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
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "майонез", "type": "fat", "percent": 5}
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
            {"name": "огурцы", "type": "vegetable", "percent": 15},
            {"name": "майонез", "type": "fat", "percent": 5}
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
    
    # ========== СУПЫ ==========
    "борщ": {
        "name": "Борщ",
        "category": "soup",
        "ingredients": [
            {"name": "свекла", "type": "vegetable", "percent": 25},
            {"name": "капуста", "type": "vegetable", "percent": 20},
            {"name": "картофель", "type": "carb", "percent": 20},
            {"name": "морковь", "type": "vegetable", "percent": 10},
            {"name": "лук", "type": "vegetable", "percent": 5},
            {"name": "говядина", "type": "protein", "percent": 15},
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
    "солянка": {
        "name": "Солянка",
        "category": "soup",
        "ingredients": [
            {"name": "говядина", "type": "protein", "percent": 20},
            {"name": "колбаса", "type": "protein", "percent": 15},
            {"name": "огурцы", "type": "vegetable", "percent": 15},
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
    
    # ========== ПАСТА ==========
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
    
    # ========== ПИЦЦА ==========
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
    
    # ========== БУРГЕРЫ ==========
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
    
    # ========== ВТОРЫЕ БЛЮДА ==========
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
    }
}

# 🔥 Ключевые ингредиенты для каждого блюда (основной белок)
KEY_INGREDIENTS = {
    "борщ": "говядина",
    "щи": "говядина",
    "солянка": "говядина",
    "уха": "рыба",
    "оливье": "колбаса",
    "винегрет": "свекла",
    "цезарь": "курица",
    "греческий салат": "фета",
    "капрезе": "моцарелла",
    "спагетти болоньезе": "фарш",
    "спагетти карбонара": "бекон",
    "лазанья": "фарш",
    "пицца пепперони": "пепперони",
    "пицца маргарита": "моцарелла",
    "бургер": "котлета",
    "чизбургер": "котлета",
    "шаурма": "курица",
    "плов": "говядина",
    "гречка с мясом": "говядина",
    "пельмени": "фарш",
    "котлеты": "фарш",
    "шашлык": "свинина",
    "омлет": "яйцо",
    "яичница": "яйцо",
    "блины": "мука",
    "сырники": "творог",
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
