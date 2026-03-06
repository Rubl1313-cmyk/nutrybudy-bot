"""
Умный поиск продуктов с автодополнением и КБЖУ.
✅ Показывает калории, белки, жиры, углеводы
✅ Кэширование результатов
✅ Fuzzy-поиск через difflib
"""
import logging
from typing import List, Dict
from difflib import SequenceMatcher

from services.food_api import LOCAL_FOOD_DB

logger = logging.getLogger(__name__)

# 🔥 Кэш: {запрос: [результаты]}
_search_cache: Dict[str, List[Dict]] = {}
_CACHE_LIMIT = 100
_CACHE_TTL = 300

# 🔥 Популярные продукты — приоритет в выдаче
POPULAR = {
    "курица", "куриная грудка", "рис", "гречка", "овсянка",
    "яйцо", "творог", "молоко", "хлеб", "картофель",
    "помидор", "огурец", "яблоко", "банан", "сыр"
}


def _similarity(a: str, b: str) -> float:
    """Схожесть строк 0.0–1.0."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def format_kbzu(item: Dict) -> str:
    """Форматирует КБЖУ для отображения."""
    calories = item.get('calories', 0)
    protein = item.get('protein', 0)
    fat = item.get('fat', 0)
    carbs = item.get('carbs', 0)
    
    return f"{calories:.0f} ккал | Б:{protein:.1f} Ж:{fat:.1f} У:{carbs:.1f}"


async def search_with_autocomplete(
    query: str,
    limit: int = 5,
    use_cache: bool = True
) -> List[Dict]:
    """
    Поиск с поддержкой автодополнения и КБЖУ.
    
    Args:
        query: Поисковый запрос
        limit: Макс. количество результатов
        use_cache: Использовать ли кэш
    
    Returns:
        Список продуктов с КБЖУ
    """
    query = query.lower().strip()
    if not query:
        return []
    
    # 🔥 Проверка кэша
    if use_cache and query in _search_cache:
        logger.info(f"♻️ Cache hit for '{query}'")
        return _search_cache[query][:limit]
    
    results = []
    seen = set()
    
    # 1️⃣ Точное совпадение
    for key, item in LOCAL_FOOD_DB.items():
        if query == key or query == item["name"].lower():
            results.append({**item, "score": 1.0, "source": "exact"})
            seen.add(item["name"])
            if len(results) >= limit:
                _search_cache[query] = results
                return results
    
    # 2️⃣ Префиксное совпадение (автодополнение)
    for key, item in LOCAL_FOOD_DB.items():
        if item["name"] in seen:
            continue
        if key.startswith(query) or item["name"].lower().startswith(query):
            score = 0.9 if key in POPULAR else 0.8
            results.append({**item, "score": score, "source": "prefix"})
            seen.add(item["name"])
            if len(results) >= limit:
                _search_cache[query] = results
                return results
    
    # 3️⃣ Fuzzy-поиск (опечатки)
    fuzzy = []
    for key, item in LOCAL_FOOD_DB.items():
        if item["name"] in seen:
            continue
        score = max(
            _similarity(query, key),
            _similarity(query, item["name"].lower())
        )
        if score >= 0.5:
            if key in POPULAR:
                score += 0.05
            fuzzy.append({**item, "score": score, "source": "fuzzy"})
    
    fuzzy.sort(key=lambda x: x["score"], reverse=True)
    results.extend(fuzzy[:limit - len(results)])
    
    # 🔥 Кэширование
    _search_cache[query] = results[:limit]
    if len(_search_cache) > _CACHE_LIMIT:
        keys = list(_search_cache.keys())[:_CACHE_LIMIT//2]
        for k in keys:
            del _search_cache[k]
    
    return results[:limit]


def get_suggestions_with_kbzu(query: str, limit: int = 5) -> List[str]:
    """
    Возвращает названия продуктов с КБЖУ для inline-кнопок.
    Формат: "Название — 165 ккал | Б:31 Ж:3.6 У:0"
    """
    results = search_with_autocomplete(query, limit=limit)
    suggestions = []
    for item in results:
        kbzu_str = format_kbzu(item)
        suggestions.append(f"{item['name']} — {kbzu_str}")
    return suggestions


def clear_cache():
    """Очистка кэша."""
    _search_cache.clear()
    logger.info("🗑️ Search cache cleared")
