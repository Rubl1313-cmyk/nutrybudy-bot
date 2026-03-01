"""
Сервис перевода для NutriBuddy
Использует бесплатный переводчик
"""
import aiohttp
import logging

logger = logging.getLogger(__name__)


async def translate_to_russian(text: str) -> str:
    """
    Переводит текст с английского на русский.
    Использует бесплатный API MyMemory Translation
    """
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": "en|ru"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    translated = data.get('responseData', {}).get('translatedText', text)
                    logger.info(f"🔄 Translated: '{text}' → '{translated}'")
                    return translated
                else:
                    logger.warning(f"⚠️ Translation API error: {resp.status}")
                    return text
                    
    except Exception as e:
        logger.error(f"❌ Translation error: {e}")
        return text


async def extract_food_items(description: str) -> list:
    """
    Извлекает отдельные продукты из описания.
    Пример: "Roasted chicken with carrots and potatoes" 
    → ["chicken", "carrots", "potatoes"]
    """
    # Простая эвристика: разбиваем по союзам и предлогам
    separators = [' with ', ' and ', ', ', ' in ', ' on ']
    
    items = [description]
    for sep in separators:
        new_items = []
        for item in items:
            parts = item.split(sep)
            new_items.extend([p.strip() for p in parts if p.strip()])
        items = new_items
    
    # Фильтруем короткие и неинформативные слова
    filtered = [item for item in items if len(item) > 3 and item.lower() not in 
                ['the', 'and', 'with', 'for', 'from', 'rice', 'bread', 'salt', 'pepper']]
    
    # Если ничего не нашли, возвращаем исходное описание
    return filtered if filtered else [description]
