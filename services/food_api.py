"""
API для поиска продуктов в OpenFoodFacts
✅ Поддержка сложных запросов, разбивка на ключевые слова
"""
import aiohttp
from typing import List, Dict

async def search_food(query: str, max_results: int = 5) -> List[Dict]:
    """
    Поиск продуктов по названию.
    Разбивает запрос на отдельные слова и пробует найти совпадения.
    """
    # Разбиваем на ключевые слова (длиной >2)
    words = [w for w in query.split() if len(w) > 2]
    search_queries = [query] + words  # сначала полная фраза, потом отдельные слова

    seen_names = set()
    results = []

    for q in search_queries:
        if not q:
            continue
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": q,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 10,
            "language": "ru"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                products = data.get('products', [])
                for p in products:
                    name = p.get('product_name', '') or p.get('product_name_en', '') or 'Неизвестно'
                    if not name or len(name) < 3 or name in seen_names:
                        continue
                    nutriments = p.get('nutriments', {})
                    # Исключаем явно не продукты (напитки, соусы и т.п.)
                    exclude = ['напиток', 'вода', 'сок', 'лимонад', 'соус', 'кетчуп', 'приправа', 'специи']
                    if any(kw in name.lower() for kw in exclude):
                        continue
                    results.append({
                        'name': name,
                        'calories': nutriments.get('energy-kcal_100g', 0) or 0,
                        'protein': nutriments.get('proteins_100g', 0) or 0,
                        'fat': nutriments.get('fat_100g', 0) or 0,
                        'carbs': nutriments.get('carbohydrates_100g', 0) or 0,
                        'barcode': p.get('code')
                    })
                    seen_names.add(name)
                    if len(results) >= max_results:
                        break
            if len(results) >= max_results:
                break
    return results[:max_results]


async def get_food_by_barcode(barcode: str) -> List[Dict]:
    """Поиск по штрихкоду"""
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
