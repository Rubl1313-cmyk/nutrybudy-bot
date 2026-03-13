"""
Сервис для обработки результата распознавания AI.
Собирает воедино: исправление ошибок, перевод, поиск готовых блюд.
"""
import logging
from typing import Dict, List, Optional

from services.dish_db import find_matching_dishes, find_matching_dishes_by_ingredients
from services.translator import translate_smart_dish_name, translate_to_russian
from services.cloudflare_ai import _fix_common_recognition_errors

logger = logging.getLogger(__name__)

async def process_ai_result(ai_data: dict) -> dict:
    """
    Обрабатывает сырой ответ AI, переводит, исправляет ошибки, ищет совпадения.
    Возвращает структуру с вариантами блюд и ингредиентами.
    """
    # 1. Исправляем типичные ошибки
    fixed = _fix_common_recognition_errors(ai_data)
    
    # 2. Переводим название блюда
    dish_name_en = fixed.get('dish_name', '')
    dish_name_ru = await translate_smart_dish_name(dish_name_en)
    
    # 3. Переводим ингредиенты
    ingredients_ru = []
    for ing in fixed.get('ingredients', []):
        if isinstance(ing, dict):
            ing_name = ing.get('name', '')
            if ing_name:
                ing['name_ru'] = await translate_to_russian(ing_name)
                ingredients_ru.append(ing)
        elif isinstance(ing, str):
            ingredients_ru.append({
                'name': ing,
                'name_ru': await translate_to_russian(ing),
                'type': 'other',
                'estimated_weight_grams': 100,
                'confidence': 0.7
            })
    
    # 4. Ищем готовые блюда по названию
    dish_matches = find_matching_dishes(dish_name_ru, threshold=0.3)
    
    # 5. Если ничего не нашли, пробуем поиск по ингредиентам
    if not dish_matches and ingredients_ru:
        # Собираем названия ингредиентов (русские)
        ingredient_names = [ing.get('name_ru', ing.get('name', '')) for ing in ingredients_ru]
        dish_matches = find_matching_dishes_by_ingredients(ingredient_names, threshold=0.4)
        if dish_matches:
            logger.info(f"🔍 Found {len(dish_matches)} dishes by ingredients: {[m['name'] for m in dish_matches]}")
    
    # 6. Возвращаем итоговую структуру
    return {
        'dish_name': dish_name_en,
        'dish_name_ru': dish_name_ru,
        'confidence': fixed.get('confidence', 0.5),
        'cooking_method': fixed.get('cooking_method', 'unknown'),
        'meal_type': fixed.get('meal_type', 'meal'),
        'ingredients': ingredients_ru,
        'matches': dish_matches[:5]  # топ-5 совпадений
    }
