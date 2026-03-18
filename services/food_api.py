"""
services/food_api.py
API для поиска продуктов и блюд
"""
from typing import List, Dict, Optional
import logging
from services.dish_db import search_dishes_by_name, get_dish_nutrition
from services.translator import translate_to_russian

logger = logging.getLogger(__name__)

async def get_product_variants(product_name: str) -> List[Dict]:
    """
    Получить варианты продуктов по названию
    
    Args:
        product_name: Название продукта для поиска
        
    Returns:
        List[Dict]: Список вариантов с информацией о питательности
    """
    try:
        # Ищем блюда по названию
        dishes = search_dishes_by_name(product_name)
        
        if not dishes:
            logger.warning(f"Продукт '{product_name}' не найден в базе")
            return []
        
        # Конвертируем блюда в формат вариантов
        variants = []
        for dish in dishes:
            nutrition = get_dish_nutrition(dish.get('name', product_name))
            
            variant = {
                'id': dish.get('name', product_name),
                'name': dish.get('name', product_name),
                'name_en': dish.get('name_en', [product_name])[0] if dish.get('name_en') else product_name,
                'category': dish.get('category', 'main'),
                'calories': nutrition.get('calories', 0),
                'protein': nutrition.get('protein', 0),
                'fat': nutrition.get('fat', 0),
                'carbs': nutrition.get('carbs', 0),
                'default_weight': dish.get('default_weight', 100)
            }
            variants.append(variant)
        
        logger.info(f"Найдено {len(variants)} вариантов для '{product_name}'")
        return variants
        
    except Exception as e:
        logger.error(f"Ошибка при поиске вариантов для '{product_name}': {e}")
        return []

def get_product_nutrition(product_name: str, weight: float = 100) -> Dict:
    """
    Получить информацию о питательности продукта
    
    Args:
        product_name: Название продукта
        weight: Вес в граммах
        
    Returns:
        Dict: Информация о питательности
    """
    try:
        dishes = search_dishes_by_name(product_name)
        
        if not dishes:
            return {
                'calories': 0,
                'protein': 0,
                'fat': 0,
                'carbs': 0
            }
        
        # Берем первый найденный вариант
        nutrition = get_dish_nutrition(dishes[0].get('name', product_name), weight)
        
        return nutrition
        
    except Exception as e:
        logger.error(f"Ошибка при получении питательности для '{product_name}': {e}")
        return {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0
        }
