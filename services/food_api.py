"""
API для поиска продуктов в OpenFoodFacts
"""
import aiohttp
from typing import List, Dict, Optional

async def search_food(query: str, max_results: int = 5) -> List[Dict]:
    """
    Поиск продуктов в OpenFoodFacts по названию.
    Возвращает список словарей с ключами: name, calories, protein, fat, carbs, barcode.
    """
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 20,
        "language": "ru"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            products = data.get('products', [])

            result = []
            for p in products:
                name = p.get('product_name', '') or p.get('product_name_en', '') or 'Неизвестно'
                if not name or len(name) < 3:
                    continue
                nutriments = p.get('nutriments', {})
                # Исключаем напитки, приправы, соусы (по ключевым словам)
                exclude_keywords = ['напиток', 'вода', 'сок', 'лимонад', 'соус', 'кетчуп', 'приправа', 'специи']
                if any(kw in name.lower() for kw in exclude_keywords):
                    continue
                result.append({
                    'name': name,
                    'calories': nutriments.get('energy-kcal_100g', 0) or 0,
                    'protein': nutriments.get('proteins_100g', 0) or 0,
                    'fat': nutriments.get('fat_100g', 0) or 0,
                    'carbs': nutriments.get('carbohydrates_100g', 0) or 0,
                    'barcode': p.get('code')
                })
                if len(result) >= max_results:
                    break
            return result

async def get_food_by_barcode(barcode: str) -> List[Dict]:
    """
    Поиск продукта по штрихкоду.
    Возвращает список с одним продуктом (если найден).
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            if data.get('status') == 1:
                p = data['product']
                nutriments = p.get('nutriments', {})
                return [{
                    'name': p.get('product_name', 'Неизвестно'),
                    'calories': nutriments.get('energy-kcal_100g', 0) or 0,
                    'protein': nutriments.get('proteins_100g', 0) or 0,
                    'fat': nutriments.get('fat_100g', 0) or 0,
                    'carbs': nutriments.get('carbohydrates_100g', 0) or 0,
                    'barcode': barcode
                }]
            return []
