"""
Планировщик задач для NutriBuddy
✅ Обработка ошибок БД
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from database.db import async_session
from database.models import Reminder
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def send_reminder(bot: Bot, user_id: int, text: str):
    """Отправка напоминания"""
    try:
        await bot.send_message(user_id, f"🔔 {text}")
        logger.info(f"✅ Reminder sent to {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send reminder to {user_id}: {e}")


def setup_scheduler(bot: Bot):
    """Настройка планировщика"""
    
    @scheduler.scheduled_job(CronTrigger(second=0))
    async def check_reminders():
        """Проверка напоминаний каждую минуту"""
        try:
            async with async_session() as session:
                now = datetime.now().strftime("%H:%M")
                day = datetime.now().strftime("%a").lower()[:3]
                
                result = await session.execute(
                    select(Reminder).where(Reminder.enabled == True)
                )
                reminders = result.scalars().all()
                
                for rem in reminders:
                    if rem.time == now and (rem.days == 'daily' or day in rem.days):
                        await send_reminder(bot, rem.user_id, rem.title)
                        
        except Exception as e:
            # 🔥 Игнорируем ошибки, если таблицы ещё не созданы
            if "does not exist" in str(e):
                logger.warning("⚠️ Reminders table not ready yet")
            else:
                logger.error(f"❌ Reminder check error: {e}")
    
    return scheduler
