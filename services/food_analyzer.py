# services/food_analyzer.py

"""
Анализатор распознанных данных от AI.
Калибрует веса, сопоставляет с базой продуктов, рассчитывает КБЖУ.
"""

import logging
from typing import Dict, List, Optional
from services.food_api import search_food

logger = logging.getLogger(__name__)

# Стандартные веса порций для калибровки
STANDARD_PORTIONS = {
    "small": {"total": 200, "main": 100, "side": 70, "sauce": 30},
    "medium": {"total": 350, "main": 150, "side": 150, "sauce": 50},
    "large": {"total": 500, "main": 200, "side": 250, "sauce": 50}
}

# Калибровочные коэффициенты для типов продуктов
WEIGHT_CALIBRATION = {
    "meat": {"raw": 1.0, "cooked": 0.75},  # мясо ужаривается
    "fish": {"raw": 1.0, "cooked": 0.8},
    "vegetables": {"raw": 1.0, "cooked": 0.6},  # овощи ужариваются сильнее
    "grains": {"raw": 1.0, "cooked": 2.5}  # крупы развариваются
}


async def analyze_ai_response(ai_data: Dict) -> Dict:
    """
    Обрабатывает ответ от AI, улучшает оценки весов и сопоставляет с базой.
    
    Args:
        ai_data: Данные от Cloudflare AI
        
    Returns:
        Словарь с обработанными ингредиентами и КБЖУ
    """
    if not ai_data or not isinstance(ai_data, dict):
        return {"error": "Invalid AI response"}
    
    result = {
        "dish_name": ai_data.get("dish_name", "Неизвестное блюдо"),
        "confidence": ai_data.get("confidence", 0.5),
        "ingredients": [],
        "total_calories": 0,
        "total_protein": 0,
        "total_fat": 0,
        "total_carbs": 0,
        "cooking_method": ai_data.get("cooking_method", ""),
        "portion_size": ai_data.get("portion_size", "medium")
    }
    
    # Получаем оценку размера порции
    portion_size = ai_data.get("portion_size", "medium")
    portion_std = STANDARD_PORTIONS.get(portion_size, STANDARD_PORTIONS["medium"])
    
    ingredients = ai_data.get("ingredients", [])
    
    # 🔥 Калибровка весов
    total_estimated_weight = sum(
        ing.get("estimated_weight_grams", 0) 
        for ing in ingredients
    )
    
    # Если AI не указал веса или они нереалистичны
    if total_estimated_weight < 100 or total_estimated_weight > 1500:
        logger.info(f"⚖️ Recalibrating weights: {total_estimated_weight}g → {portion_std['total']}g")
        ingredients = _redistribute_weights(ingredients, portion_std)
    
    # 🔥 Сопоставление с базой продуктов и расчёт КБЖУ
    for ing in ingredients:
        product_data = await _match_with_database(ing["name"])
        
        weight = ing.get("estimated_weight_grams", 100)
        ing_type = ing.get("type", "side")
        
        # Рассчитываем КБЖУ для указанного веса
        multiplier = weight / 100
        calories = product_data.get("calories", 0) * multiplier
        protein = product_data.get("protein", 0) * multiplier
        fat = product_data.get("fat", 0) * multiplier
        carbs = product_data.get("carbs", 0) * multiplier
        
        result["ingredients"].append({
            "name": product_data.get("name", ing["name"]),
            "type": ing_type,
            "weight": weight,
            "calories": round(calories, 1),
            "protein": round(protein, 1),
            "fat": round(fat, 1),
            "carbs": round(carbs, 1),
            "confidence": ing.get("confidence", 0.7),
            "ai_name": ing["name"]  # Оригинальное название от AI
        })
        
        result["total_calories"] += calories
        result["total_protein"] += protein
        result["total_fat"] += fat
        result["total_carbs"] += carbs
    
    # 🔥 Сравнение с AI-оценкой калорий
    ai_calories = ai_data.get("total_estimated_calories", 0)
    if ai_calories > 0:
        diff = abs(result["total_calories"] - ai_calories) / ai_calories
        if diff > 0.3:  # Если разница > 30%
            logger.warning(f"⚠️ Calorie mismatch: AI={ai_calories}, Calculated={result['total_calories']}")
            result["calorie_warning"] = True
    
    return result


def _redistribute_weights(ingredients: List[Dict], portion_std: Dict) -> List[Dict]:
    """Перераспределяет веса ингредиентов по стандарту порции."""
    if not ingredients:
        return ingredients
    
    # Группируем по типам
    by_type = {"main": [], "side": [], "garnish": [], "sauce": []}
    for ing in ingredients:
        ing_type = ing.get("type", "side")
        by_type.get(ing_type, by_type["side"]).append(ing)
    
    # Распределяем веса
    for ing_type, items in by_type.items():
        if not items:
            continue
        target_weight = portion_std.get(ing_type, portion_std["side"])
        weight_per_item = target_weight / len(items)
        for item in items:
            item["estimated_weight_grams"] = int(weight_per_item)
    
    return ingredients


async def _match_with_database(product_name: str) -> Dict:
    """Ищет продукт в базе и возвращает лучшие совпадения."""
    results = await search_food(product_name)
    if results:
        return {
            "name": results[0].get("name", product_name),
            "calories": results[0].get("calories", 0),
            "protein": results[0].get("protein", 0),
            "fat": results[0].get("fat", 0),
            "carbs": results[0].get("carbs", 0)
        }
    
    # Если не найдено, возвращаем заглушку
    return {
        "name": product_name,
        "calories": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0
    }


async def get_user_calibration(telegram_id: int) -> Dict:
    """
    Возвращает персональные коэффициенты пользователя.
    В будущем можно анализировать историю коррекций.
    """
    # Пока возвращаем стандартные значения
    return {
        "weight_multiplier": 1.0,
        "preferred_portion": "medium"
    }
