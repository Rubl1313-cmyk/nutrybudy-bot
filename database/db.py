"""
Планировщик задач для NutriBuddy
✅ Обработка ошибок при отсутствии таблиц
✅ Простые SQL-запросы без ORM (избегает lazy loading)
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from database.db import async_session
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def send_reminder(bot: Bot, user_id: int, title: str):
    """Отправка напоминания"""
    try:
        await bot.send_message(user_id, f"🔔 {title}")
    except Exception as e:
        logger.error(f"❌ Failed to send reminder: {e}")


def setup_scheduler(bot: Bot):
    """Настройка планировщика"""
    
    @scheduler.scheduled_job(CronTrigger(second=0))
    async def check_reminders():
        """Проверка напоминаний каждую минуту"""
        try:
            async with async_session() as session:
                now = datetime.now().strftime("%H:%M")
                day = datetime.now().strftime("%a").lower()[:3]
                
                # 🔥 Простой SQL-запрос без ORM (избегает lazy loading)
                result = await session.execute(
                    text("SELECT id, user_id, title, time, days, enabled FROM reminders WHERE enabled = true")
                )
                rows = result.fetchall()
                
                for row in rows:
                    rem_id, user_id, title, rem_time, rem_days, enabled = row
                    
                    if rem_time == now and (rem_days == 'daily' or day in rem_days):
                        await send_reminder(bot, user_id, title)
                        
        except ProgrammingError as e:
            # 🔥 Игнорируем, если таблица ещё не создана
            if "does not exist" in str(e).lower():
                logger.warning("⚠️ Reminders table not ready yet — skipping check")
            else:
                logger.error(f"❌ Reminder check error: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error in check_reminders: {e}")
    
    return scheduler
