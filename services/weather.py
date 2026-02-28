import aiohttp
from typing import Optional

async def get_temperature(city: str) -> Optional[float]:
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "ru"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(geocode_url, params=params) as resp:
            if resp.status != 200:
                return 20.0
            data = await resp.json()
            if not data.get("results"):
                return 20.0
            
            lat = data["results"][0]["latitude"]
            lon = data["results"][0]["longitude"]
            
            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "timezone": "auto"
            }
            
            async with session.get(weather_url, params=weather_params) as resp:
                if resp.status != 200:
                    return 20.0
                weather_data = await resp.json()
                return weather_data.get("current_weather", {}).get("temperature", 20.0)