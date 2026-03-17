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
    Возвращает словарь с температурой, состоянием, влажностью и ветром.
    """
    today = date.today()
    city_clean = city.strip().lower()

    # Проверка кэша
    if city_clean in _weather_cache:
        cache_date, weather_data = _weather_cache[city_clean]
        if cache_date == today:
            logger.info(f"♻️ Using cached weather for {city}: {weather_data.get('temp', 'N/A')}°C")
            return weather_data
        else:
            del _weather_cache[city_clean]

    # Если нет ключа — возвращаем заглушку
    if not WEATHERAPI_KEY:
        logger.warning("⚠️ WEATHERAPI_KEY not set, using default weather data")
        return {
            'temp': 20.0,
            'condition': 'облачно',
            'humidity': 50,
            'wind': 3.0
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
                    
                    # Извлекаем нужные данные
                    current = data["current"]
                    weather_data = {
                        'temp': float(current["temp_c"]),
                        'condition': current["condition"]["text"],
                        'humidity': current["humidity"],
                        'wind': float(current["wind_kph"] / 3.6),  # Конвертируем в м/с
                        'pressure': current["pressure_mb"],
                        'feels_like': float(current["feelslike_c"])
                    }
                    
                    # Кэшируем результат
                    _weather_cache[city_clean] = (today, weather_data)
                    logger.info(f"✅ WeatherAPI for {city}: {weather_data['temp']}°C, {weather_data['condition']}")
                    return weather_data
                    
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
    return {
        'temp': 20.0,
        'condition': 'неизвестно',
        'humidity': 50,
        'wind': 3.0
    }
