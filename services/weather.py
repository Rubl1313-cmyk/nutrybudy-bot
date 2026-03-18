"""
Сервис погоды для NutriBuddy
[WEATHER] Использует WeatherAPI.com (1M запросов/месяц бесплатно)
[WEATHER] Кэширование на день
"""
import aiohttp
import asyncio
import os
import logging
from datetime import date
from typing import Dict

logger = logging.getLogger(__name__)

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")  # Получите на https://www.weatherapi.com

# Кэш: {город: (дата, данные_о_погоде)}
_weather_cache: Dict[str, tuple[date, Dict]] = {}


async def get_temperature(city: str) -> float:
    """
    Получает температуру через WeatherAPI.com с кэшированием на день.
    Возвращает 20.0 при ошибке.
    """
    weather_data = await get_weather(city)
    return weather_data.get('temp', 20.0)


async def get_weather(city: str) -> Dict:
    """
    Получает полные данные о погоде через WeatherAPI.com с кэшированием на день.
    Возвращает полный словарь с температурой, условиями, влажностью, ветром.
    """
    today = date.today()
    city_clean = city.strip().lower()

    # Проверка кэша
    if city_clean in _weather_cache:
        cache_date, weather_data = _weather_cache[city_clean]
        if cache_date == today:
            logger.info(f"[CACHE] Using cached weather for {city}: {weather_data.get('temp', 'N/A')}°C")
            return weather_data
        else:
            del _weather_cache[city_clean]

    # Если нет ключа API
    if not WEATHERAPI_KEY:
        logger.warning("[WARNING] WEATHERAPI_KEY not set, using default weather data")
        return {
            'temp': 20.0,
            'condition': 'неизвестно',
            'humidity': 50,
            'wind': 3.0,
            'timezone': 'UTC',
            'localtime': None,
            'city': city
        }

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
                    
                    # Извлечение необходимых данных
                    current = data["current"]
                    location = data.get("location", {})
                    
                    weather_data = {
                        'temp': float(current["temp_c"]),
                        'condition': current["condition"]["text"],
                        'humidity': current["humidity"],
                        'wind': float(current["wind_kph"]) / 3.6,  # Конвертация в м/с
                        'pressure': current["pressure_mb"],
                        'feels_like': float(current["feelslike_c"]),
                        # Добавление данных о времени
                        'timezone': location.get("tz_id", "UTC"),
                        'localtime': location.get("localtime"),
                        'city': location.get("name", city)
                    }
                    
                    # Кэширование результата
                    _weather_cache[city_clean] = (today, weather_data)
                    logger.info(f"[WEATHER] WeatherAPI for {city}: {weather_data['temp']}°C, {weather_data['condition']}")
                    return weather_data
                    
                elif resp.status == 429:
                    logger.warning("[WARNING] WeatherAPI rate limit exceeded (429)")
                else:
                    text = await resp.text()
                    logger.error(f"[ERROR] WeatherAPI error {resp.status}: {text[:200]}")
    except asyncio.TimeoutError:
        logger.warning("[WARNING] WeatherAPI timeout")
    except Exception as e:
        logger.error(f"[ERROR] WeatherAPI exception: {e}")

    # Fallback
    return {
        'temp': 20.0,
        'condition': 'неизвестно',
        'humidity': 50,
        'wind': 3.0,
        'timezone': 'UTC',
        'localtime': None,
        'city': city
    }
