"""
utils/timezone_auto.py
Автоматическое определение часового пояса по городу
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Словарь соответствия городов и часовых поясов
CITY_TIMEZONE_MAP = {
    # Россия
    'москва': 'Europe/Moscow',
    'санкт-петербург': 'Europe/Moscow',
    'новосибирск': 'Asia/Novosibirsk',
    'мурманск': 'Europe/Moscow',
    'екатеринбург': 'Asia/Yekaterinburg',
    'казань': 'Europe/Moscow',
    'нижний новгород': 'Europe/Moscow',
    'челябинск': 'Asia/Yekaterinburg',
    'самара': 'Europe/Samara',
    'ростов-на-дону': 'Europe/Moscow',
    'уфа': 'Asia/Yekaterinburg',
    'красноярск': 'Asia/Krasnoyarsk',
    'пермь': 'Asia/Yekaterinburg',
    'воронеж': 'Europe/Moscow',
    'волгоград': 'Europe/Volgograd',
    'краснодар': 'Europe/Moscow',
    'саратов': 'Europe/Saratov',
    'тюмень': 'Asia/Yekaterinburg',
    'тольятти': 'Europe/Moscow',
    'ижевск': 'Europe/Samara',
    'барнаул': 'Asia/Novosibirsk',
    'иркутск': 'Asia/Irkutsk',
    'хабаровск': 'Asia/Khabarovsk',
    'владивосток': 'Asia/Vladivostok',
    'якутск': 'Asia/Yakutsk',
    
    # Украина
    'киев': 'Europe/Kyiv',
    'харьков': 'Europe/Kyiv',
    'одесса': 'Europe/Kyiv',
    'днепр': 'Europe/Kyiv',
    'донецк': 'Europe/Kyiv',
    'львов': 'Europe/Kyiv',
    
    # Беларусь
    'минск': 'Europe/Minsk',
    'гомель': 'Europe/Minsk',
    'брест': 'Europe/Minsk',
    
    # Казахстан
    'алматы': 'Asia/Almaty',
    'нур-султан': 'Asia/Qyzylorda',
    'шымкент': 'Asia/Qyzylorda',
    'астана': 'Asia/Almaty',
    
    # Узбекистан
    'ташкент': 'Asia/Tashkent',
    'самарканд': 'Asia/Samarkand',
    'бухара': 'Asia/Samarkand',
    
    # Страны Балтии
    'рига': 'Europe/Riga',
    'таллин': 'Europe/Tallinn',
    'вильнюс': 'Europe/Vilnius',
    
    # Кавказ
    'баку': 'Asia/Baku',
    'тбилиси': 'Asia/Tbilisi',
    'ереван': 'Asia/Yerevan',
    
    # Средняя Азия
    'бишкек': 'Asia/Bishkek',
    'душанбе': 'Asia/Dushanbe',
    'ашхабад': 'Asia/Ashgabat',
    
    # Европа
    'лондон': 'Europe/London',
    'берлин': 'Europe/Berlin',
    'париж': 'Europe/Paris',
    'рим': 'Europe/Rome',
    'мадрид': 'Europe/Madrid',
    'амстердам': 'Europe/Amsterdam',
    'брюссель': 'Europe/Brussels',
    'вена': 'Europe/Vienna',
    'прага': 'Europe/Prague',
    'будапешт': 'Europe/Budapest',
    'варшава': 'Europe/Warsaw',
    'стокгольм': 'Europe/Stockholm',
    'копенгаген': 'Europe/Copenhagen',
    'хельсинки': 'Europe/Helsinki',
    
    # Азия
    'пекин': 'Asia/Shanghai',
    'шанхай': 'Asia/Shanghai',
    'гонконг': 'Asia/Hong_Kong',
    'сингапур': 'Asia/Singapore',
    'токио': 'Asia/Tokyo',
    'сеул': 'Asia/Seoul',
    'бангкок': 'Asia/Bangkok',
    'джакарта': 'Asia/Jakarta',
    'куала-лумпур': 'Asia/Kuala_Lumpur',
    'манчестер': 'Europe/London',
    
    # Америка
    'нью-йорк': 'America/New_York',
    'лос-анджелес': 'America/Los_Angeles',
    'чикаго': 'America/Chicago',
    'вашингтон': 'America/New_York',
    'бостон': 'America/New_York',
    'миами': 'America/New_York',
    'сан-франциско': 'America/Los_Angeles',
    'торонто': 'America/Toronto',
    'ванкувер': 'America/Vancouver',
    'мехико': 'America/Mexico_City',
    
    # Другие крупные города
    'дубай': 'Asia/Dubai',
    'каир': 'Africa/Cairo',
    'кейптаун': 'Africa/Johannesburg',
    'мумбаи': 'Asia/Kolkata',
    'дели': 'Asia/Kolkata',
    'сидней': 'Australia/Sydney',
    'мельбурн': 'Australia/Melbourne',
    'аукленд': 'Pacific/Auckland',
}

def get_timezone_by_city(city: str) -> str:
    """
    Автоматическое определение часового пояса по названию города
    
    Args:
        city: Название города
        
    Returns:
        str: Часовой пояс в формате IANA
    """
    if not city:
        return 'UTC'
    
    city_clean = city.strip().lower()
    
    # Прямое соответствие
    if city_clean in CITY_TIMEZONE_MAP:
        timezone = CITY_TIMEZONE_MAP[city_clean]
        logger.info(f"🌍 Автоматически определён часовой пояс для города '{city}': {timezone}")
        return timezone
    
    # Поиск по вхождению (для сложных названий)
    for city_name, timezone in CITY_TIMEZONE_MAP.items():
        if city_clean in city_name or city_name in city_clean:
            logger.info(f"🌍 Автоматически определён часовой пояс для города '{city}': {timezone}")
            return timezone
    
    # Поиск по ключевым словам
    if any(keyword in city_clean for keyword in ['москва', 'московская']):
        return 'Europe/Moscow'
    elif any(keyword in city_clean for keyword in ['санкт-петербург', 'спб', 'петербург']):
        return 'Europe/Moscow'
    elif any(keyword in city_clean for keyword in ['мурманск', 'мурма']):
        return 'Europe/Moscow'
    elif any(keyword in city_clean for keyword in ['новосибирск', 'нск']):
        return 'Asia/Novosibirsk'
    elif any(keyword in city_clean for keyword in ['екатеринбург', 'екб']):
        return 'Asia/Yekaterinburg'
    elif any(keyword in city_clean for keyword in ['казань']):
        return 'Europe/Moscow'
    elif any(keyword in city_clean for keyword in ['нижний новгород', 'нн']):
        return 'Europe/Moscow'
    elif any(keyword in city_clean for keyword in ['самара']):
        return 'Europe/Samara'
    elif any(keyword in city_clean for keyword in ['ростов', 'ростов-на-дону']):
        return 'Europe/Moscow'
    elif any(keyword in city_clean for keyword in ['уфа']):
        return 'Asia/Yekaterinburg'
    elif any(keyword in city_clean for keyword in ['красноярск']):
        return 'Asia/Krasnoyarsk'
    elif any(keyword in city_clean for keyword in ['пермь']):
        return 'Asia/Yekaterinburg'
    elif any(keyword in city_clean for keyword in ['воронеж']):
        return 'Europe/Moscow'
    elif any(keyword in city_clean for keyword in ['волгоград']):
        return 'Europe/Volgograd'
    elif any(keyword in city_clean for keyword in ['краснодар']):
        return 'Europe/Moscow'
    
    # Европа
    elif any(keyword in city_clean for keyword in ['лондон', 'london']):
        return 'Europe/London'
    elif any(keyword in city_clean for keyword in ['берлин', 'berlin']):
        return 'Europe/Berlin'
    elif any(keyword in city_clean for keyword in ['париж', 'paris']):
        return 'Europe/Paris'
    elif any(keyword in city_clean for keyword in ['рим', 'rome']):
        return 'Europe/Rome'
    elif any(keyword in city_clean for keyword in ['мадрид', 'madrid']):
        return 'Europe/Madrid'
    
    # Америка
    elif any(keyword in city_clean for keyword in ['нью-йорк', 'new york']):
        return 'America/New_York'
    elif any(keyword in city_clean for keyword in ['лос-анджелес', 'los angeles']):
        return 'America/Los_Angeles'
    elif any(keyword in city_clean for keyword in ['чикаго', 'chicago']):
        return 'America/Chicago'
    
    # Азия
    elif any(keyword in city_clean for keyword in ['пекин', 'beijing']):
        return 'Asia/Shanghai'
    elif any(keyword in city_clean for keyword in ['токио', 'tokyo']):
        return 'Asia/Tokyo'
    elif any(keyword in city_clean for keyword in ['дубай', 'dubai']):
        return 'Asia/Dubai'
    
    logger.warning(f"⚠️ Часовой пояс для города '{city}' не найден, используется UTC")
    return 'UTC'

async def auto_detect_timezone_from_weather(city: str) -> Optional[str]:
    """
    Попытка получить часовой пояс из Weather API
    
    Args:
        city: Название города
        
    Returns:
        Optional[str]: Часовой пояс или None
    """
    try:
        from services.weather import get_weather
        weather_data = await get_weather(city)
        
        if 'timezone' in weather_data:
            timezone = weather_data['timezone']
            logger.info(f"🌍 Часовой пояс из Weather API для '{city}': {timezone}")
            return timezone
            
    except Exception as e:
        logger.warning(f"⚠️ Не удалось получить часовой пояс из Weather API для '{city}': {e}")
    
    return None
