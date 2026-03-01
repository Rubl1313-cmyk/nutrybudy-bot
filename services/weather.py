"""
Сервис погоды через Open-Meteo (бесплатно, без ключа)
✅ Исправлено: поддержка русских названий городов
"""
import aiohttp
from typing import Optional

# Словарь популярных российских городов для точного поиска
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
    'мурманск': 'Murmansk',  # ✅ Ваш город!
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
    """
    Преобразует русское название города в английское для API.
    """
    city_lower = city.lower().strip()
    
    # Проверяем словарь известных городов
    if city_lower in RUSSIAN_CITIES:
        return RUSSIAN_CITIES[city_lower]
    
    # Простая транслитерация для остальных
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
    """
    Получает текущую температуру в городе через Open-Meteo.
    Возвращает 20.0 по умолчанию при ошибке.
    """
    try:
        # Преобразуем название города
        city_en = transliterate_city(city)
        
        # 1. Геокодинг: получаем координаты
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
                    # Пробуем поиск по оригинальному названию (на случай, если API поймёт)
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
                
                # 2. Получаем погоду по координатам
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
        import logging
        logging.warning(f"⚠️ Weather API error for '{city}': {e}")
        return 20.0  # Дефолтное значение при ошибке


async def get_weather_details(city: str) -> dict:
    """
    Получает расширенную информацию о погоде.
    Returns: {'temp': float, 'condition': str, 'humidity': int, 'city_name': str}
    """
    try:
        city_en = transliterate_city(city)
        
        async with aiohttp.ClientSession() as session:
            # Геокодинг
            geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {"name": city_en, "count": 1, "language": "en"}
            
            async with session.get(geocode_url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return {'temp': 20.0, 'condition': 'unknown', 'humidity': None, 'city_name': city}
                    
                data = await resp.json()
                if not data.get("results"):
                    return {'temp': 20.0, 'condition': 'unknown', 'humidity': None, 'city_name': city}
                
                result = data["results"][0]
                lat = result["latitude"]
                lon = result["longitude"]
                city_name = result.get("name", city)
                
                # Погода с дополнительными параметрами
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
                        return {'temp': 20.0, 'condition': 'unknown', 'humidity': None, 'city_name': city_name}
                        
                    weather_data = await resp.json()
                    current = weather_data.get("current_weather", {})
                    
                    # Коды погоды WMO: https://open-meteo.com/en/docs
                    weather_codes = {
                        0: "☀️ Ясно", 1: "🌤️ Преим. ясно", 2: "⛅ Переменно", 3: "☁️ Облачно",
                        45: "🌫️ Туман", 48: "🌫️ Туман с изморозью",
                        51: "🌦️ Морось", 53: "🌦️ Морось", 55: "🌧️ Сильная морось",
                        61: "🌧️ Дождь", 63: "🌧️ Дождь", 65: "🌧️ Сильный дождь",
                        71: "🌨️ Снег", 73: "🌨️ Снег", 75: "❄️ Сильный снег",
                        95: "⛈️ Гроза", 96: "⛈️ Гроза с градом", 99: "⛈️ Сильная гроза"
                    }
                    
                    code = current.get("weather_code", 0)
                    condition = weather_codes.get(code, "🌡️ Неизвестно")
                    
                    return {
                        'temp': round(current.get("temperature", 20.0), 1),
                        'condition': condition,
                        'humidity': weather_data.get("current", {}).get("relative_humidity_2m"),
                        'city_name': city_name
                    }
                    
    except Exception as e:
        import logging
        logging.warning(f"⚠️ Weather details error: {e}")
        return {'temp': 20.0, 'condition': 'unknown', 'humidity': None, 'city_name': city}
