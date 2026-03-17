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
    Использует текущую температуру в городе.
    Запросы к API кэшируются на день, поэтому повторные обращения к тому же городу
    в течение дня не создают лишней нагрузки.
    """
    async with get_session() as session:
        # Получаем всех пользователей, у которых есть город
        result = await session.execute(
            select(User).where(User.city.isnot(None))
        )
        users = result.scalars().all()

    logger.info(f"Starting daily water goal update for {len(users)} users")

    updated_count = 0
    for user in users:
        try:
            # Получаем текущую температуру (из кэша или API)
            temp = await get_temperature(user.city)

            # Нормализуем уровень активности (если нужно)
            activity_norm = normalize_activity_level(user.activity_level)

            # Пересчитываем норму воды
            new_goal = calculate_water_goal(
                weight=user.weight,
                activity_level=activity_norm,
                temperature=temp,
                goal=user.goal,
                gender=user.gender
            )
            new_goal = round(new_goal)

            # Если значение изменилось, обновляем
            if user.daily_water_goal != new_goal:
                user.daily_water_goal = new_goal
                async with get_session() as update_session:
                    await update_session.merge(user)
                    await update_session.commit()
                updated_count += 1
                logger.debug(f"Updated user {user.id}: new water goal {new_goal} ml")

            # Небольшая задержка, чтобы не перегружать БД (необязательно)
            await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Failed to update user {user.id} ({user.city}): {e}")
            continue

    logger.info(f"Daily water goal update completed. Updated {updated_count} users.")
