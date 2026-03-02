"""
Сервис перевода для NutriBuddy.
Использует бесплатный переводчик MyMemory API.
"""
import aiohttp
import logging

logger = logging.getLogger(__name__)


async def translate_to_russian(text: str) -> str:
    """
    Переводит текст с английского на русский через MyMemory API.
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
    Извлекает отдельные продукты из описания (простая версия).
    """
    # Убираем лишние слова
    import re
    # Заменяем союзы на запятые
    text = re.sub(r'\band\b|\bwith\b|\bin\b', ',', description.lower())
    # Разделяем по запятым
    items = [item.strip() for item in text.split(',') if item.strip()]
    return items
