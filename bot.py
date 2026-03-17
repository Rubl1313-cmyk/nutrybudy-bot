import asyncio
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
# Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ°Ğ¸Ğ²Ğ°ĞµĞ¼ Ğ»Ğ¾Ğ³Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log') if os.getenv('LOG_TO_FILE') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ğ˜Ğ¼Ğ¿Ğ¾Ñ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Redis (Ğ¾Ğ±Ñ�Ğ·Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ°Ñ� Ğ·Ğ°Ğ²Ğ¸Ñ�Ğ¸Ğ¼Ğ¾Ñ�Ñ‚ÑŒ)
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
import redis.asyncio as redis
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update, BotCommand
from aiohttp import web
from database.db import init_db, close_db, engine
from sqlalchemy import text
from aiogram.fsm.strategy import FSMStrategy
from utils.rate_limiter import user_rate_limiter, global_rate_limiter

load_dotenv('.env')


TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 8080))
ADMIN_ID = os.getenv("ADMIN_ID")

dp = None

async def set_bot_commands(bot: Bot):
    """Ğ£Ñ�Ñ‚Ğ°Ğ½Ğ¾Ğ²ĞºĞ° ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´ Ğ±Ğ¾Ñ‚Ğ°"""
    commands = [
        BotCommand(command="start", description="ğŸš€ Ğ—Ğ°Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ Ğ±Ğ¾Ñ‚Ğ°"),
        BotCommand(command="help", description="ğŸ“š ĞŸĞ¾Ğ¼Ğ¾Ñ‰ÑŒ"),
        BotCommand(command="set_profile", description="ğŸ‘¤ Ğ�Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¸Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"),
        BotCommand(command="profile", description="ğŸ‘¤ ĞœĞ¾Ğ¹ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"),
        BotCommand(command="log_food", description="ğŸ�½ï¸� Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ¸Ñ‚ÑŒ ĞµĞ´Ñƒ"),
        BotCommand(command="log_drink", description="ğŸ’§ Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ"),
        BotCommand(command="log_water", description="ğŸ’§ Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ"),
        BotCommand(command="drink", description="ğŸ’§ Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸"),
        BotCommand(command="water", description="ğŸ’§ Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ²Ğ¾Ğ´Ñ‹"),
        BotCommand(command="log_weight", description="âš–ï¸� Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²ĞµÑ�"),
        BotCommand(command="weight", description="âš–ï¸� Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ²ĞµÑ�Ğ°"),
        BotCommand(command="fitness", description="ğŸ�ƒ Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ¸Ñ‚ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ"),
        BotCommand(command="activity", description="ğŸ�ƒ Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"),
        BotCommand(command="progress", description="ğŸ“Š ĞœĞ¾Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�"),
        BotCommand(command="stats", description="ğŸ“Š Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�"),
        BotCommand(command="ask", description="ğŸ’¬ AI Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚"),  # Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ°Ñ�
        # BotCommand(command="ai", description="ğŸ’¬ AI Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚"),  # ÑƒĞ±Ñ€Ğ°Ğ½Ğ¾
        BotCommand(command="weather", description="ğŸŒ¦ï¸� ĞŸĞ¾Ğ³Ğ¾Ğ´Ğ°"),
        BotCommand(command="recipe", description="ğŸ�³ Ğ ĞµÑ†ĞµĞ¿Ñ‚"),
        BotCommand(command="calculate", description="ğŸ§® Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ğ°Ñ‚ÑŒ ĞšĞ‘Ğ–Ğ£"),
        BotCommand(command="meal_plan", description="ğŸ�½ï¸� ĞŸĞ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"),
        # BotCommand(command="diet", description="ğŸ�½ï¸� ĞŸĞ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"),  # ÑƒĞ±Ñ€Ğ°Ğ½Ğ¾
        BotCommand(command="nutrition", description="ğŸ¥— Ğ¡Ğ¾Ğ²ĞµÑ‚Ñ‹ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"),
        BotCommand(command="cancel", description="â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°")
    ]
    await bot.set_my_commands(commands)
    logger.info("âœ… Bot commands set")

async def send_startup_notification(bot: Bot):
    """Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²ĞºĞ° ÑƒĞ²ĞµĞ´Ğ¾Ğ¼Ğ»ĞµĞ½Ğ¸Ñ� Ğ¾ Ğ·Ğ°Ğ¿ÑƒÑ�ĞºĞµ Ğ°Ğ´Ğ¼Ğ¸Ğ½Ñƒ"""
    if not ADMIN_ID:
        return
    try:
        bot_info = await bot.get_me()
        startup_message = (
            f"ğŸŸ¢ <b>NutriBuddy Ğ·Ğ°Ğ¿ÑƒÑ‰ĞµĞ½!</b>\n"
            f"ğŸ¤– Ğ‘Ğ¾Ñ‚: @{bot_info.username}\n"
            f"ğŸ“… Ğ’Ñ€ĞµĞ¼Ñ�: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"ğŸŒ� Railway: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}\n"
            f"âœ… Ğ¡Ñ‚Ğ°Ñ‚ÑƒÑ�: Ğ³Ğ¾Ñ‚Ğ¾Ğ² Ğº Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğµ"
        )
        await bot.send_message(chat_id=int(ADMIN_ID), text=startup_message, parse_mode="HTML")
        logger.info(f"ğŸ“¬ Startup notification sent to admin {ADMIN_ID}")
    except Exception as e:
        logger.error(f"â�Œ Failed to send startup notification: {e}")

async def webhook_handler(request):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ²ĞµĞ±Ñ…ÑƒĞºĞ°"""
    try:
        bot = request.app['bot']
        dp = request.app['dp']
        update = await request.json()
        update_obj = Update(**update)
        await dp.feed_update(bot, update_obj)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"â�Œ Webhook handler error: {e}", exc_info=True)
        return web.Response(status=500)

async def health_handler(request):
    """Health check Ğ´Ğ»Ñ� Railway Ñ� Ğ¿Ñ€Ğ¾Ğ²ĞµÑ€ĞºĞ¾Ğ¹ Ğ‘Ğ”"""
    try:
        bot = request.app['bot']
        await bot.get_me()
        
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€ĞºĞ° Ğ¿Ğ¾Ğ´ĞºĞ»Ñ�Ñ‡ĞµĞ½Ğ¸Ñ� Ğº Ğ‘Ğ”
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "bot": "running"
        })
    except Exception as e:
        logger.error(f"â�Œ Health check failed: {e}")
        return web.json_response({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=503)

async def on_startup(app):
    """Ğ—Ğ°Ğ¿ÑƒÑ�Ğº Ğ±Ğ¾Ñ‚Ğ°"""
    bot = app['bot']
    try:
        logger.info("ğŸ”§ Starting database initialization...")
        db_ok = await init_db()
        if not db_ok:
            logger.error("â�Œ Database initialization failed")
            raise Exception("Database init failed")
        logger.info("ğŸ’¾ Database ready")

        bot_info = await bot.get_me()
        logger.info(f"ğŸ¤– Connected as @{bot_info.username}")

        # Ğ£Ñ�Ñ‚Ğ°Ğ½Ğ¾Ğ²ĞºĞ° Ğ²ĞµĞ±Ñ…ÑƒĞºĞ° Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ ĞµÑ�Ğ»Ğ¸ ÑƒĞºĞ°Ğ·Ğ°Ğ½ WEBHOOK_URL
        if WEBHOOK_URL:
            webhook_full_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
            webhook_info = await bot.get_webhook_info()
            if webhook_info.url != webhook_full_url:
                await bot.set_webhook(
                    url=webhook_full_url,
                    allowed_updates=dp.resolve_used_update_types(),
                    drop_pending_updates=True
                )
                logger.info(f"âœ… Webhook set to {webhook_full_url}")
        else:
            logger.warning("âš ï¸� WEBHOOK_URL not set, webhook not configured")

        await set_bot_commands(bot)
        
    except Exception as e:
        logger.error(f"â�Œ Startup error: {e}", exc_info=True)
        raise

async def on_shutdown(app):
    """Ğ�Ñ�Ñ‚Ğ°Ğ½Ğ¾Ğ²ĞºĞ° Ğ±Ğ¾Ñ‚Ğ°"""
    try:
        bot = app['bot']
        await bot.delete_webhook(drop_pending_updates=True)
        await close_db()
        await bot.session.close()
        logger.info("ğŸ”´ Bot stopped")
    except Exception as e:
        logger.error(f"â�Œ Shutdown error: {e}")

def create_app():
    """Ğ¡Ğ¾Ğ·Ğ´Ğ°Ğ½Ğ¸Ğµ Ğ¿Ñ€Ğ¸Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ñ�"""
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

async def main():
    """Ğ�Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ°Ñ� Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ñ�"""
    global dp
    logging.info("Starting NutriBuddy Bot on Railway...")
    
    # Ğ—Ğ°Ğ¿ÑƒÑ�ĞºĞ°ĞµĞ¼ Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ğ¸ Ğ‘Ğ”
    from database.migrations import run_migrations
    await run_migrations()
    
    # Ğ’Ğ°Ğ»Ğ¸Ğ´Ğ°Ñ†Ğ¸Ñ� Ñ‚Ğ¾ĞºĞµĞ½Ğ° Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ğ² production
    validate_token = os.getenv('RAILWAY_ENVIRONMENT') == 'production'
    
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        validate_token=validate_token
    )
    
    # Redis storage Ğ´Ğ»Ñ� FSM (Ğ¾Ğ±Ñ�Ğ·Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğ¹)
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = await redis.from_url(redis_url)
    storage = RedisStorage(redis_client, key_builder=DefaultKeyBuilder(with_destiny=True))
    logger.info("âœ… Redis storage initialized")
    
    # Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ğ´Ğ¸Ñ�Ğ¿ĞµÑ‚Ñ‡ĞµÑ€ Ñ� FSM
    dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.GLOBAL_USER)
    
    # Middleware Ğ´Ğ»Ñ� Ğ»Ğ¾Ğ³Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ� Ğ¸ rate limiting
    from aiogram import BaseMiddleware
    from aiogram.types import Message
    from aiogram.filters import Command
    
    class LoggingMiddleware(BaseMiddleware):
        async def __call__(self, handler, event: Message, data: dict):
            logger.info(f"ğŸ“¨ Incoming message: {repr(event.text)}")
            return await handler(event, data)
    
    class RateLimitMiddleware(BaseMiddleware):
        async def __call__(self, handler, event: Message, data: dict):
            user_id = event.from_user.id
            
            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ³Ğ»Ğ¾Ğ±Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ»Ğ¸Ğ¼Ğ¸Ñ‚
            if not await global_rate_limiter.is_allowed():
                logger.warning(f"ğŸš« Global rate limit exceeded for user {user_id}")
                await event.answer("âš ï¸� Ğ¡Ğ»Ğ¸ÑˆĞºĞ¾Ğ¼ Ğ¼Ğ½Ğ¾Ğ³Ğ¾ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ¾Ğ²! ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¿Ğ¾Ğ·Ğ¶Ğµ.")
                return
            
            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒÑ�ĞºĞ¸Ğ¹ Ğ»Ğ¸Ğ¼Ğ¸Ñ‚
            if not await user_rate_limiter.is_allowed(user_id, 'general'):
                logger.warning(f"ğŸš« User rate limit exceeded for user {user_id}")
                await event.answer("âš ï¸� Ğ¡Ğ»Ğ¸ÑˆĞºĞ¾Ğ¼ Ğ¼Ğ½Ğ¾Ğ³Ğ¾ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ¾Ğ²! ĞŸĞ¾Ğ´Ğ¾Ğ¶Ğ´Ğ¸Ñ‚Ğµ Ğ½ĞµĞ¼Ğ½Ğ¾Ğ³Ğ¾.")
                return
            
            return await handler(event, data)
    
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    
    # ĞŸĞ¾Ğ´ĞºĞ»Ñ�Ñ‡ĞµĞ½Ğ¸Ğµ Ñ€Ğ¾ÑƒÑ‚ĞµÑ€Ğ¾Ğ² Ğ² Ğ¿Ñ€Ğ°Ğ²Ğ¸Ğ»ÑŒĞ½Ğ¾Ğ¼ Ğ¿Ğ¾Ñ€Ñ�Ğ´ĞºĞµ:
    # 1. ĞšĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹ Ğ¸ Ñ�Ğ¿ĞµÑ†Ğ¸Ñ„Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ (Ğ´Ğ¾Ğ»Ğ¶Ğ½Ñ‹ Ğ±Ñ‹Ñ‚ÑŒ Ğ¿ĞµÑ€Ğ²Ñ‹Ğ¼Ğ¸)
    # 2. ĞœĞµĞ´Ğ¸Ğ° Ğ¸ AI Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸
    # 3. Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ñ‚ĞµĞºÑ�Ñ‚Ğ° (universal) - Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğ¼
    
    from handlers import universal, common, profile, drinks, progress, activity, weight, meal_plan, ai_assistant, reply_handlers, achievements, food_clarification

    # ĞšĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹ Ğ¸ Ñ�Ğ¿ĞµÑ†Ğ¸Ñ„Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ (Ğ´Ğ¾Ğ»Ğ¶Ğ½Ñ‹ Ğ±Ñ‹Ñ‚ÑŒ Ğ¿ĞµÑ€Ğ²Ñ‹Ğ¼Ğ¸)
    dp.include_router(common.router)           # /start, /help, /cancel Ğ¸ Ñ‚.Ğ´.
    dp.include_router(profile.router)          # /set_profile, /profile
    dp.include_router(drinks.router)           # /log_drink, /drink (ĞµĞ´Ğ¸Ğ½Ğ°Ñ� Ñ�Ğ¸Ñ�Ñ‚ĞµĞ¼Ğ° Ğ²Ğ¾Ğ´Ñ‹)
    dp.include_router(progress.router)         # /progress, /stats
    dp.include_router(activity.router)         # /fitness, /activity
    dp.include_router(weight.router)           # /log_weight, /weight
    dp.include_router(meal_plan.router)        # /meal_plan, /diet
    dp.include_router(ai_assistant.router)     # /ask, /ai, /weather
    dp.include_router(achievements.router)     # /achievements
    
    # Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ reply-ĞºĞ½Ğ¾Ğ¿Ğ¾Ğº â€“ Ğ´Ğ¾Ğ»Ğ¶Ğ½Ñ‹ Ğ±Ñ‹Ñ‚ÑŒ ĞŸĞ•Ğ Ğ•Ğ” ÑƒĞ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¼
    dp.include_router(reply_handlers.router)   # Reply-ĞºĞ½Ğ¾Ğ¿ĞºĞ¸
    
    # Ğ£Ñ‚Ğ¾Ñ‡Ğ½ĞµĞ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ² â€“ ĞŸĞ•Ğ Ğ•Ğ” ÑƒĞ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¼ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¾Ğ¼
    dp.include_router(food_clarification.router)  # Ğ£Ñ‚Ğ¾Ñ‡Ğ½ĞµĞ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ²
    
    # Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ñ‚ĞµĞºÑ�Ñ‚Ğ° â€“ ĞŸĞ�Ğ¡Ğ›Ğ•Ğ”Ğ�Ğ˜Ğ™ (Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ°ĞµÑ‚ Ğ²Ñ�Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ�)
    dp.include_router(universal.router)         # ĞŸĞ¾Ğ»Ğ½Ñ‹Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº (Ñ� LangChain)
    # ai_handler.router ÑƒĞ´Ğ°Ğ»ĞµĞ½ - ĞµĞ³Ğ¾ Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ Ğ¸Ğ½Ñ‚ĞµĞ³Ñ€Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ° Ğ² universal.router
    # dialog.router ÑƒĞ´Ğ°Ğ»ĞµĞ½ - ĞµĞ³Ğ¾ Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ Ğ¿Ğ¾ĞºÑ€Ñ‹Ğ²Ğ°ĞµÑ‚Ñ�Ñ� universal.router
    
    logging.info("All routers included in correct order for FSM")
    
    # Запускаем фоновую задачу для очистки неактивных агентов
    async def cleanup_agents_task():
        while True:
            try:
                from services.langchain_agent import LangChainAgent
                LangChainAgent.cleanup_inactive(max_age_hours=1)
                logger.info("Agent cleanup completed")
            except Exception as e:
                logger.error(f"Agent cleanup error: {e}")
            await asyncio.sleep(3600)  # Каждый час
    
    asyncio.create_task(cleanup_agents_task())
    logger.info("Agent cleanup task started")
    
    # Запускаем фоновую задачу для ежедневного обновления нормы воды
    async def periodic_weather_update():
        """Запускает обновление раз в 24 часа."""
        while True:
            try:
                from services.weather_updater import update_all_users_water_goal
                await update_all_users_water_goal()
                logger.info("Daily water goal update completed")
            except Exception as e:
                logger.exception(f"Error in periodic weather update: {e}")
            # Ждём 24 часа (86400 секунд)
            await asyncio.sleep(86400)
    
    asyncio.create_task(periodic_weather_update())
    logger.info("Weather update task started")
    
    app = create_app()
    app['bot'] = bot
    app['dp'] = dp  # ĞŸĞµÑ€ĞµĞ´Ğ°ĞµĞ¼ Ğ´Ğ¸Ñ�Ğ¿ĞµÑ‚Ñ‡ĞµÑ€ Ğ² ĞºĞ¾Ğ½Ñ‚ĞµĞºÑ�Ñ‚
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    logging.info(f"Server started on port {PORT}")
    logging.info(f"Railway environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logging.info("Server stopped")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        exit(1)