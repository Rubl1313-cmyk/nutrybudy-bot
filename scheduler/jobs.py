"""
Планировщик задач для NutriBuddy
✅ Исправлено: используется get_session() вместо async_session
✅ Поддержка московского времени (UTC+3)
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from database.db import get_session
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from datetime import datetime, timedelta
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
        """Проверка напоминаний каждую минуту по московскому времени"""
        try:
            async with get_session() as session:
                # Получаем текущее московское время (UTC+3)
                now_utc = datetime.utcnow()
                now_msk = now_utc + timedelta(hours=3)
                current_time = now_msk.strftime("%H:%M")
                # День недели на московское время (сокращённо: mon, tue, wed...)
                day_msk = now_msk.strftime("%a").lower()[:3]
                
                result = await session.execute(
                    text("""
                        SELECT u.telegram_id, r.title, r.time, r.days 
                        FROM reminders r
                        JOIN users u ON r.user_id = u.id
                        WHERE r.enabled = true
                    """)
                )
                rows = result.fetchall()
                
                for row in rows:
                    telegram_id, title, rem_time, rem_days = row
                    # Проверяем по московскому времени
                    if rem_time == current_time and (rem_days == 'daily' or day_msk in rem_days):
                        await send_reminder(bot, telegram_id, title)
                        
        except ProgrammingError as e:
            if "does not exist" in str(e).lower():
                logger.warning("⚠️ Tables not ready yet — skipping check")
            else:
                logger.error(f"❌ Reminder check error: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error in check_reminders: {e}", exc_info=True)
    
    return scheduler
