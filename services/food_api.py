async def search_food(query: str, max_results: int = 5) -> List[Dict]:
    """
    Поиск продуктов в OpenFoodFacts с фильтрацией.
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
                # Фильтр: исключаем напитки, приправы, соусы (по ключевым словам)
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
