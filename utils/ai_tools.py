"""
Инструменты для AI-ассистента.
"""
from database.db import get_session
from services.weather import get_temperature



async def get_weather(city: str) -> str:
    temp = await get_temperature(city)
    return f"🌆 {city}: {temp}°C"
