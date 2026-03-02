"""
Клиент для Spoonacular API.
Генерирует планы питания и получает детали рецептов.
"""
import aiohttp
import os
from typing import Optional, Dict, List

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com"

async def generate_meal_plan(
    target_calories: int,
    time_frame: str = "day",
    diet: Optional[str] = None,
    exclude: Optional[str] = None
) -> Optional[Dict]:
    """
    Генерирует план питания через Spoonacular API.

    Args:
        target_calories: Целевая калорийность на день.
        time_frame: 'day' или 'week'.
        diet: Опциональная диета (e.g., 'vegetarian', 'ketogenic').
        exclude: Ингредиенты для исключения (через запятую).

    Returns:
        Словарь с планом питания или None при ошибке.
    """
    if not SPOONACULAR_API_KEY:
        print("❌ Ошибка: SPOONACULAR_API_KEY не задан в переменных окружения.")
        return None

    url = f"{BASE_URL}/mealplanner/generate"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "timeFrame": time_frame,
        "targetCalories": target_calories,
    }
    if diet:
        params["diet"] = diet
    if exclude:
        params["exclude"] = exclude

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    print(f"Ошибка Spoonacular API: {resp.status}")
                    return None
    except Exception as e:
        print(f"Исключение при запросе к Spoonacular: {e}")
        return None


async def get_recipe_details(recipe_id: int) -> Optional[Dict]:
    """
    Получает детальную информацию о рецепте по его ID.

    Args:
        recipe_id: ID рецепта из Spoonacular.

    Returns:
        Словарь с данными рецепта (изображение, инструкции, etc.) или None.
    """
    if not SPOONACULAR_API_KEY:
        return None

    url = f"{BASE_URL}/recipes/{recipe_id}/information"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "includeNutrition": False  # Нам не нужна нутриция, она уже есть в плане
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return None
    except Exception:
        return None
