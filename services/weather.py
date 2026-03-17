"""
Ğ¡ĞµÑ€Ğ²Ğ¸Ñ� Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñ‹ Ğ´Ğ»Ñ� NutriBuddy
âœ… Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµÑ‚ WeatherAPI.com (1M Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ¾Ğ²/Ğ¼ĞµÑ� Ğ±ĞµÑ�Ğ¿Ğ»Ğ°Ñ‚Ğ½Ğ¾)
âœ… ĞšÑ�ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ½Ğ° Ğ´ĞµĞ½ÑŒ
"""
import aiohttp
import asyncio
import os
import logging
from datetime import date
from typing import Dict

logger = logging.getLogger(__name__)

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")  # Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚Ğµ Ğ½Ğ° https://www.weatherapi.com

# ĞšÑ�Ñˆ: {Ğ³Ğ¾Ñ€Ğ¾Ğ´: (Ğ´Ğ°Ñ‚Ğ°, Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ_Ğ¾_Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ğµ)}
_weather_cache: Dict[str, tuple[date, Dict]] = {}


async def get_temperature(city: str) -> float:
    """
    ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµÑ‚ Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ñƒ Ñ‡ĞµÑ€ĞµĞ· WeatherAPI.com Ñ� ĞºÑ�ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸ĞµĞ¼ Ğ½Ğ° Ğ´ĞµĞ½ÑŒ.
    Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ 20.0 Ğ¿Ñ€Ğ¸ Ğ¾ÑˆĞ¸Ğ±ĞºĞµ.
    """
    weather_data = await get_weather(city)
    return weather_data.get('temp', 20.0)


async def get_weather(city: str) -> Dict:
    """
    ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµÑ‚ Ğ¿Ğ¾Ğ»Ğ½Ñ‹Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾ Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ğµ Ñ‡ĞµÑ€ĞµĞ· WeatherAPI.com Ñ� ĞºÑ�ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸ĞµĞ¼ Ğ½Ğ° Ğ´ĞµĞ½ÑŒ.
    Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ Ñ�Ğ»Ğ¾Ğ²Ğ°Ñ€ÑŒ Ñ� Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ğ¾Ğ¹, Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸ĞµĞ¼, Ğ²Ğ»Ğ°Ğ¶Ğ½Ğ¾Ñ�Ñ‚ÑŒÑ� Ğ¸ Ğ²ĞµÑ‚Ñ€Ğ¾Ğ¼.
    """
    today = date.today()
    city_clean = city.strip().lower()

    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€ĞºĞ° ĞºÑ�ÑˆĞ°
    if city_clean in _weather_cache:
        cache_date, weather_data = _weather_cache[city_clean]
        if cache_date == today:
            logger.info(f"â™»ï¸� Using cached weather for {city}: {weather_data.get('temp', 'N/A')}Â°C")
            return weather_data
        else:
            del _weather_cache[city_clean]

    # Ğ•Ñ�Ğ»Ğ¸ Ğ½ĞµÑ‚ ĞºĞ»Ñ�Ñ‡Ğ° â€” Ğ²Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµĞ¼ Ğ·Ğ°Ğ³Ğ»ÑƒÑˆĞºÑƒ
    if not WEATHERAPI_KEY:
        logger.warning("âš ï¸� WEATHERAPI_KEY not set, using default weather data")
        return {
            'temp': 20.0,
            'condition': 'Ğ¾Ğ±Ğ»Ğ°Ñ‡Ğ½Ğ¾',
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
                    
                    # Ğ˜Ğ·Ğ²Ğ»ĞµĞºĞ°ĞµĞ¼ Ğ½ÑƒĞ¶Ğ½Ñ‹Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ
                    current = data["current"]
                    weather_data = {
                        'temp': float(current["temp_c"]),
                        'condition': current["condition"]["text"],
                        'humidity': current["humidity"],
                        'wind': float(current["wind_kph"] / 3.6),  # ĞšĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ² Ğ¼/Ñ�
                        'pressure': current["pressure_mb"],
                        'feels_like': float(current["feelslike_c"])
                    }
                    
                    # ĞšÑ�ÑˆĞ¸Ñ€ÑƒĞµĞ¼ Ñ€ĞµĞ·ÑƒĞ»ÑŒÑ‚Ğ°Ñ‚
                    _weather_cache[city_clean] = (today, weather_data)
                    logger.info(f"âœ… WeatherAPI for {city}: {weather_data['temp']}Â°C, {weather_data['condition']}")
                    return weather_data
                    
                elif resp.status == 429:
                    logger.warning("âš ï¸� WeatherAPI rate limit exceeded (429)")
                else:
                    text = await resp.text()
                    logger.error(f"â�Œ WeatherAPI error {resp.status}: {text[:200]}")
    except asyncio.TimeoutError:
        logger.warning("â�±ï¸� WeatherAPI timeout")
    except Exception as e:
        logger.error(f"ğŸ’¥ WeatherAPI exception: {e}")

    # Fallback
    return {
        'temp': 20.0,
        'condition': 'Ğ½ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ¾',
        'humidity': 50,
        'wind': 3.0
    }
