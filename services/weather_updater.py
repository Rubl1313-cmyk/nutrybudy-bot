"""
services/weather_updater.py
Фоновая задача для ежедневного обновления нормы воды всех пользователей.
"""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select

from database.db import get_session
from database.models import User
from services.calculator import calculate_water_goal
from services.weather import get_temperature
from utils.activity_normalizer import normalize_activity_level

logger = logging.getLogger(__name__)

async def update_all_users_water_goal():
    """
    Обновляет daily_water_goal для всех пользователей, у которых указан город.
    Группирует пользователей по городам для оптимизации запросов к API.
    Запросы к API кэшируются на день, поэтому повторные обращения к тому же городу
    в течение дня не создают лишней нагрузки.
    """
    async with get_session() as session:
        # Получаем всех пользователей, у которых есть город
        result = await session.execute(
            select(User).where(User.city.isnot(None))
        )
        users = result.scalars().all()
        
        # Группируем пользователей по городам для оптимизации запросов
        city_users = {}
        for user in users:
            if user.city not in city_users:
                city_users[user.city] = []
            city_users[user.city].append(user)
        
        logger.info(f"[WORLD] Обновляем нормы воды для {len(users)} пользователей в {len(city_users)} городах")
        
        # Обрабатываем каждый город отдельно
        for city, city_user_list in city_users.items():
            try:
                # Получаем температуру один раз для всех пользователей города
                temperature = await get_temperature(city)
                logger.info(f"[TEMP] Температура в {city}: {temperature}°C для {len(city_user_list)} пользователей")
                
                # Обновляем норму воды для всех пользователей города
                for user in city_user_list:
                    try:
                        # Нормализуем уровень активности
                        normalized_activity = normalize_activity_level(user.activity_level)
                        
                        # Рассчитываем новую норму воды
                        water_goal = calculate_water_goal(
                            weight=user.weight,
                            activity_level=normalized_activity,
                            temperature=temperature,
                            goal=user.goal,
                            gender=user.gender
                        )
                        
                        # Обновляем норму воды
                        user.daily_water_goal = water_goal
                        # Обновляем updated_at без timezone для PostgreSQL
                        from datetime import datetime, timezone
                        user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        
                    except Exception as e:
                        logger.error(f"[ERROR] Ошибка обновления нормы воды для пользователя {user.id}: {e}")
                        continue
                        
                await session.commit()
                
            except Exception as e:
                logger.error(f"[ERROR] Ошибка получения погоды для города {city}: {e}")
                continue

    logger.info(f"[DONE] Обновление норм воды завершено для {len(city_users)} городов")
