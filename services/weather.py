"""
Сервис погоды для NutriBuddy
✅ Использует WeatherAPI.com (1M запросов/мес бесплатно)
✅ Кэширование на день
"""
import aiohttp
import asyncio
import os
import logging
from datetime import date
from typing import Dict

logger = logging.getLogger(__name__)

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")  # получите на https://www.weatherapi.com

# Кэш: {город: (дата, температура_°C)}
_weather_cache: Dict[str, tuple[date, float]] = {}


async def get_temperature(city: str) -> float:
    """
    Получает температуру через WeatherAPI.com с кэшированием на день.
    Возвращает 20.0 при ошибке.
    """
    today = date.today()
    city_clean = city.strip().lower()

    # Проверка кэша
    if city_clean in _weather_cache:
        cache_date, temp = _weather_cache[city_clean]
        if cache_date == today:
            logger.info(f"♻️ Using cached temp for {city}: {temp}°C")
            return temp
        else:
            del _weather_cache[city_clean]

    # Если нет ключа — возвращаем заглушку
    if not WEATHERAPI_KEY:
        logger.warning("⚠️ WEATHERAPI_KEY not set, using default 20°C")
        return 20.0

    try:
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": WEATHERAPI_KEY,
            "q": city,
            "lang": "ru",
            "aqi": "no"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    temp_c = data["current"]["temp_c"]
                    _weather_cache[city_clean] = (today, temp_c)
                    logger.info(f"✅ WeatherAPI for {city}: {temp_c}°C")
                    return float(temp_c)
                elif resp.status == 429:
                    logger.warning("⚠️ WeatherAPI rate limit exceeded (429)")
                else:
                    text = await resp.text()
                    logger.error(f"❌ WeatherAPI error {resp.status}: {text[:200]}")
    except asyncio.TimeoutError:
        logger.warning("⏱️ WeatherAPI timeout")
    except Exception as e:
        logger.error(f"💥 WeatherAPI exception: {e}")

    # Fallback
    return 20.0
