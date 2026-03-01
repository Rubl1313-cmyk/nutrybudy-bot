from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from database.db import async_session
from database.models import Reminder
from datetime import datetime
from sqlalchemy import select

scheduler = AsyncIOScheduler()


async def send_reminder(bot: Bot, user_id: int, text: str):
    try:
        await bot.send_message(user_id, f"🔔 {text}")
    except Exception as e:
        print(f"Failed to send reminder to {user_id}: {e}")


def setup_scheduler(bot: Bot):
    @scheduler.scheduled_job(CronTrigger(second=0))
    async def check_reminders():
        async with async_session() as session:
            now = datetime.now().strftime("%H:%M")
            day = datetime.now().strftime("%a").lower()[:3]
            
            result = await session.execute(
                select(Reminder).where(Reminder.enabled == True)
            )
            
            for rem in result.scalars():
                if rem.time == now and (rem.days == 'daily' or day in rem.days):
                    await send_reminder(bot, rem.user_id, rem.title)
    
    return scheduler
