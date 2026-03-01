import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

RUSSIAN_CITIES = {
    'москва': 'Moscow',
    'санкт-петербург': 'Saint Petersburg',
    'спб': 'Saint Petersburg',
    'новосибирск': 'Novosibirsk',
    'екатеринбург': 'Yekaterinburg',
    'казань': 'Kazan',
    'нижний новгород': 'Nizhny Novgorod',
    'челябинск': 'Chelyabinsk',
    'омск': 'Omsk',
    'самара': 'Samara',
    'ростов-на-дону': 'Rostov-on-Don',
    'уфа': 'Ufa',
    'красноярск': 'Krasnoyarsk',
    'воронеж': 'Voronezh',
    'пермь': 'Perm',
    'волгоград': 'Volgograd',
    'краснодар': 'Krasnodar',
    'саратов': 'Saratov',
    'тюмень': 'Tyumen',
    'мурманск': 'Murmansk',
    'архангельск': 'Arkhangelsk',
    'петрозаводск': 'Petrozavodsk',
    'калининград': 'Kaliningrad',
    'владивосток': 'Vladivostok',
    'хабаровск': 'Khabarovsk',
    'иркутск': 'Irkutsk',
    'якутск': 'Yakutsk',
    'сочи': 'Sochi',
}


def transliterate_city(city: str) -> str:
    city_lower = city.lower().strip()
    
    if city_lower in RUSSIAN_CITIES:
        return RUSSIAN_CITIES[city_lower]
    
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    
    result = ''.join(translit_map.get(c, c) for c in city_lower)
    return result.replace(' ', '+')


async def get_temperature(city: str) -> float:
    try:
        city_en = transliterate_city(city)
        
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_en,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(geocode_url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return 20.0
                    
                data = await resp.json()
                if not data.get("results"):
                    params["name"] = city
                    params["language"] = "ru"
                    async with session.get(geocode_url, params=params, timeout=10) as resp2:
                        if resp2.status != 200:
                            return 20.0
                        data = await resp2.json()
                        if not data.get("results"):
                            return 20.0
                
                result = data["results"][0]
                lat = result["latitude"]
                lon = result["longitude"]
                
                weather_url = "https://api.open-meteo.com/v1/forecast"
                weather_params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": "true",
                    "timezone": "auto"
                }
                
                async with session.get(weather_url, params=weather_params, timeout=10) as resp:
                    if resp.status != 200:
                        return 20.0
                        
                    weather_data = await resp.json()
                    temp = weather_data.get("current_weather", {}).get("temperature")
                    
                    if temp is not None:
                        return round(float(temp), 1)
                    return 20.0
                    
    except Exception as e:
        logger.warning(f"⚠️ Weather API error for '{city}': {e}")
        return 20.0


async def get_weather_details(city: str) -> dict:
    try:
        city_en = transliterate_city(city)
        
        async with aiohttp.ClientSession() as session:
            geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {"name": city_en, "count": 1, "language": "en"}
            
            async with session.get(geocode_url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return {'temp': 20.0, 'condition': 'unknown', 'city_name': city}
                    
                data = await resp.json()
                if not data.get("results"):
                    return {'temp': 20.0, 'condition': 'unknown', 'city_name': city}
                
                result = data["results"][0]
                lat = result["latitude"]
                lon = result["longitude"]
                city_name = result.get("name", city)
                
                weather_url = "https://api.open-meteo.com/v1/forecast"
                weather_params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": "true",
                    "current": "temperature_2m,relative_humidity_2m,weather_code",
                    "timezone": "auto"
                }
                
                async with session.get(weather_url, params=weather_params, timeout=10) as resp:
                    if resp.status != 200:
                        return {'temp': 20.0, 'condition': 'unknown', 'city_name': city_name}
                        
                    weather_data = await resp.json()
                    current = weather_data.get("current_weather", {})
                    
                    weather_codes = {
                        0: "☀️ Ясно", 1: "🌤️ Преим. ясно", 2: "⛅ Переменно", 3: "☁️ Облачно",
                        45: "🌫️ Туман", 51: "🌦️ Морось", 61: "🌧️ Дождь",
                        71: "🌨️ Снег", 95: "⛈️ Гроза"
                    }
                    
                    code = current.get("weather_code", 0)
                    condition = weather_codes.get(code, "🌡️ Неизвестно")
                    
                    return {
                        'temp': round(current.get("temperature", 20.0), 1),
                        'condition': condition,
                        'city_name': city_name
                    }
                    
    except Exception as e:
        logger.warning(f"⚠️ Weather details error: {e}")
        return {'temp': 20.0, 'condition': 'unknown', 'city_name': city}
