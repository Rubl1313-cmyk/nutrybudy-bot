"""
Сервис погоды через Open-Meteo (бесплатно, без ключа)
✅ Исправлено: корректная обработка русских городов
"""
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Словарь координат популярных городов
CITY_COORDINATES = {
    'москва': (55.7558, 37.6173),
    'санкт-петербург': (59.9343, 30.3351),
    'спб': (59.9343, 30.3351),
    'новосибирск': (55.0084, 82.9357),
    'екатеринбург': (56.8389, 60.6057),
    'казань': (55.8304, 49.0661),
    'нижний новгород': (56.2965, 43.9361),
    'челябинск': (55.1644, 61.4368),
    'омск': (54.9885, 73.3242),
    'самара': (53.1959, 50.1002),
    'ростов-на-дону': (47.2357, 39.7015),
    'уфа': (54.7388, 55.9721),
    'красноярск': (56.0153, 92.8932),
    'воронеж': (51.6720, 39.1843),
    'пермь': (58.0105, 56.2502),
    'волгоград': (48.7080, 44.5133),
    'краснодар': (45.0355, 38.9753),
    'саратов': (51.5924, 46.0348),
    'тюмень': (57.1522, 65.5272),
    'мурманск': (68.9585, 33.0827),  # ✅ Мурманск!
    'архангельск': (64.5393, 40.5320),
    'петрозаводск': (61.7849, 34.3469),
    'калининград': (54.7104, 20.4522),
    'владивосток': (43.1056, 131.8735),
    'хабаровск': (48.4827, 135.0838),
    'иркутск': (52.2978, 104.2964),
    'якутск': (62.0355, 129.6755),
    'сочи': (43.6028, 39.7342),
}


async def get_temperature(city: str) -> float:
    """
    Получает текущую температуру в городе через Open-Meteo.
    Возвращает 20.0 по умолчанию при ошибке.
    """
    try:
        city_lower = city.lower().strip()
        
        # 🔥 Ищем в словаре координат
        if city_lower in CITY_COORDINATES:
            lat, lon = CITY_COORDINATES[city_lower]
            logger.info(f"🌍 Found city '{city}' in database: {lat}, {lon}")
        else:
            # Пробуем геокодинг
            geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {
                "name": city,
                "count": 1,
                "language": "ru",
                "format": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(geocode_url, params=params, timeout=10) as resp:
                    if resp.status != 200:
                        logger.warning(f"⚠️ Geocoding API error: {resp.status}")
                        return 20.0
                    
                    data = await resp.json()
                    if not data.get("results"):
                        logger.warning(f"⚠️ City '{city}' not found in geocoding")
                        return 20.0
                    
                    result = data["results"][0]
                    lat = result["latitude"]
                    lon = result["longitude"]
                    logger.info(f"🌍 Geocoded '{city}' to: {lat}, {lon}")
        
        # Получаем погоду по координатам
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "timezone": "auto"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(weather_url, params=weather_params, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"❌ Weather API error: {resp.status}")
                    return 20.0
                
                weather_data = await resp.json()
                temp = weather_data.get("current_weather", {}).get("temperature")
                
                if temp is not None:
                    logger.info(f"✅ Temperature for {city}: {temp}°C")
                    return round(float(temp), 1)
                
                logger.warning("⚠️ No temperature in weather response")
                return 20.0
                
    except Exception as e:
        logger.error(f"💥 Weather API error for '{city}': {e}")
        return 20.0
