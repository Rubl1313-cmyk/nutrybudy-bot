"""
Сервис погоды для NutriBuddy
✅ Улучшена обработка ошибок, добавлен fallback на статическое значение
✅ Исправлены URL и импорты
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Словарь координат городов России
CITY_COORDINATES = {
    'москва': (55.7558, 37.6173),
    'санкт-петербург': (59.9343, 30.3351),
    'спб': (59.9343, 30.3351),
    'ленинградская область': (59.9343, 30.3351),
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
    'мурманск': (68.9585, 33.0827),  # ✅ Мурманск
    'архангельск': (64.5393, 40.5320),
    'петрозаводск': (61.7849, 34.3469),
    'калининград': (54.7104, 20.4522),
    'владивосток': (43.1056, 131.8735),
    'хабаровск': (48.4827, 135.0838),
    'иркутск': (52.2978, 104.2964),
    'якутск': (62.0355, 129.6755),
    'сочи': (43.6028, 39.7342),
    'севастополь': (44.6167, 33.5254),
    'симферополь': (44.9521, 34.1024),
    'минск': (53.9006, 27.5590),
    'киев': (50.4501, 30.5234),
    'алматы': (43.2220, 76.8512),
}


async def get_temperature(city: str) -> float:
    """
    Получает текущую температуру в городе.
    Возвращает 20.0 при ошибке и логирует предупреждение.
    
    Args:
        city: Название города
        
    Returns:
        float: Температура в °C или 20.0 при ошибке
    """
    try:
        city_lower = city.lower().strip()
        
        # 🔥 Ищем в словаре координат
        if city_lower in CITY_COORDINATES:
            lat, lon = CITY_COORDINATES[city_lower]
            logger.info(f"🌍 Found '{city}' in database: {lat}, {lon}")
        else:
            # Пробуем геокодинг
            lat, lon = await geocode_city(city)
            if lat is None:
                logger.warning(f"⚠️ City '{city}' not found, using default 20°C")
                return 20.0
        
        # 🔥 Пробуем Open-Meteo
        temp = await get_weather_openmeteo(lat, lon)
        if temp is not None:
            return temp
        
        # 🔥 Если Open-Meteo не отвечает, возвращаем разумное значение
        logger.warning(f"⚠️ All weather APIs failed for {city}, using default 20°C")
        return 20.0
        
    except Exception as e:
        logger.error(f"💥 Unexpected weather error: {e}", exc_info=True)
        return 20.0


async def geocode_city(city: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Геокодинг города через Open-Meteo API.
    
    Args:
        city: Название города
        
    Returns:
        Tuple[Optional[float], Optional[float]]: (latitude, longitude) или (None, None)
    """
    try:
        # ✅ Исправлено: убраны пробелы в URL
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city,
            "count": 1,
            "language": "ru",
            "format": "json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("results"):
                        result = data["results"][0]
                        return result["latitude"], result["longitude"]
                else:
                    logger.warning(f"⚠️ Geocoding API error: {resp.status}")
    except asyncio.TimeoutError:
        logger.warning("⚠️ Geocoding timeout")
    except Exception as e:
        logger.error(f"❌ Geocoding error: {e}")
    
    return None, None


async def get_weather_openmeteo(lat: float, lon: float) -> Optional[float]:
    """
    Получение погоды через Open-Meteo API.
    
    Args:
        lat: Широта
        lon: Долгота
        
    Returns:
        Optional[float]: Температура в °C или None при ошибке
    """
    try:
        # ✅ Исправлено: убраны пробелы в URL
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "timezone": "auto"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    temp = data.get("current_weather", {}).get("temperature")
                    if temp is not None:
                        logger.info(f"✅ Open-Meteo: {temp}°C")
                        return round(float(temp), 1)
                else:
                    error_text = await resp.text()
                    logger.warning(f"⚠️ Open-Meteo error {resp.status}: {error_text[:200]}")
    except asyncio.TimeoutError:
        logger.warning("⚠️ Open-Meteo timeout")
    except Exception as e:
        logger.error(f"❌ Open-Meteo error: {e}")
    
    return None
