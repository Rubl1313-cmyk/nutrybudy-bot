import aiohttp
from typing import List, Dict

async def search_food(query: str) -> List[Dict]:
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
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
                nutriments = p.get('nutriments', {})
                result.append({
                    'name': p.get('product_name', 'Неизвестно'),
                    'calories': nutriments.get('energy-kcal_100g', 0) or 0,
                    'protein': nutriments.get('proteins_100g', 0) or 0,
                    'fat': nutriments.get('fat_100g', 0) or 0,
                    'carbs': nutriments.get('carbohydrates_100g', 0) or 0,
                    'barcode': p.get('code')
                })
            return result

async def get_food_by_barcode(barcode: str) -> List[Dict]:
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