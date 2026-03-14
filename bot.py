import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update, BotCommand
from aiohttp import web
from database.db import init_db, close_db, engine
from handlers import (
    common, profile, progress, media_handlers,
    meal_plan, smart_ai_handler, enhanced_universal_handler
)
# Убираем дублирующий импорт register_ai_handlers
# from handlers.smart_ai_handler import register_ai_handlers
from sqlalchemy import text
from aiogram.fsm.strategy import FSMStrategy

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log') if os.getenv('LOG_TO_FILE') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 8080))
ADMIN_ID = os.getenv("ADMIN_ID")

dp = None

async def set_bot_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="help", description="📚 Помощь"),
        BotCommand(command="set_profile", description="👤 Профиль"),
        BotCommand(command="progress", description="📊 Прогресс"),
        BotCommand(command="ask", description="💬 Умный помощник"),
        BotCommand(command="analytics", description="🔮 Аналитика и прогнозы"),
        BotCommand(command="challenge", description="🎮 Челленджи"),
        BotCommand(command="level", description="🏆 Уровень и награды"),
        BotCommand(command="meal_plan", description="🍽️ План питания"),
        BotCommand(command="cancel", description="❌ Отмена")
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Bot commands set")

async def send_startup_notification(bot: Bot):
    """Отправка уведомления о запуске админу"""
    if not ADMIN_ID:
        return
    try:
        bot_info = await bot.get_me()
        startup_message = (
            f"🟢 <b>NutriBuddy запущен!</b>\n"
            f"🤖 Бот: @{bot_info.username}\n"
            f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"🌐 Railway: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}\n"
            f"✅ Статус: готов к работе с умными функциями"
        )
        await bot.send_message(chat_id=int(ADMIN_ID), text=startup_message, parse_mode="HTML")
        logger.info(f"📬 Startup notification sent to admin {ADMIN_ID}")
    except Exception as e:
        logger.error(f"❌ Failed to send startup notification: {e}")

async def webhook_handler(request):
    """Обработчик вебхука"""
    try:
        bot = request.app['bot']
        update = await request.json()
        update_obj = Update(**update)
        await dp.feed_update(bot, update_obj)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"❌ Webhook handler error: {e}", exc_info=True)
        return web.Response(status=500)

async def health_handler(request):
    """Health check для Railway с проверкой БД"""
    try:
        bot = request.app['bot']
        await bot.get_me()
        
        # Проверка подключения к БД
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "bot": "running"
        })
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return web.json_response({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=503)

async def on_startup(app):
    """Запуск бота"""
    bot = app['bot']
    try:
        logger.info("🔧 Starting database initialization...")
        db_ok = await init_db()
        if not db_ok:
            logger.error("❌ Database initialization failed")
            raise Exception("Database init failed")
        logger.info("💾 Database ready")

        bot_info = await bot.get_me()
        logger.info(f"🤖 Connected as @{bot_info.username}")

        # Установка вебхука только если указан WEBHOOK_URL
        if WEBHOOK_URL:
            webhook_full_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
            webhook_info = await bot.get_webhook_info()
            if webhook_info.url != webhook_full_url:
                await bot.set_webhook(
                    url=webhook_full_url,
                    allowed_updates=dp.resolve_used_update_types(),
                    drop_pending_updates=True
                )
                logger.info(f"✅ Webhook set to {webhook_full_url}")
        else:
            logger.warning("⚠️ WEBHOOK_URL not set, webhook not configured")

        await set_bot_commands(bot)
        
        # Роутеры уже подключены в main()
        logger.info("💬 All handlers registered")
        
        await send_startup_notification(bot)
        
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)
        raise

async def on_shutdown(app):
    """Остановка бота"""
    try:
        bot = app['bot']
        await bot.delete_webhook(drop_pending_updates=True)
        await close_db()
        await bot.session.close()
        logger.info("🔴 Bot stopped")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

def create_app():
    """Создание приложения"""
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

async def main():
    """Основная функция"""
    logging.info("🔵 Starting NutriBuddy Bot on Railway...")
    
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    
    global dp
    dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.GLOBAL_USER)
    
    # Подключение роутеров (ПОРЯДОК ВАЖЕН!)
    dp.include_router(common.router)
    dp.include_router(profile.router)
    dp.include_router(progress.router)
    dp.include_router(media_handlers.router)
    dp.include_router(meal_plan.router)
    dp.include_router(smart_ai_handler.router)
    dp.include_router(enhanced_universal_handler.router)  # enhanced AI обработчик
    
    logging.info("✅ All routers included")
    
    app = create_app()
    app['bot'] = bot
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    logging.info(f"🚀 Server started on port {PORT}")
    logging.info(f"🌐 Railway environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    
    # Создаём событие для graceful shutdown
    shutdown_event = asyncio.Event()
    
    # Обработчики сигналов
    def signal_handler(signum, frame):
        logging.info(f"📡 Received signal {signum}")
        shutdown_event.set()
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while not shutdown_event.is_set():
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logging.info("⏹️ Server stopped")
    finally:
        await runner.cleanup()
        await close_db()
        logging.info("👋 Graceful shutdown completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("👋 Keyboard interrupt")
    except Exception as e:
        logging.error(f"💥 Fatal error: {e}", exc_info=True)
        exit(1)
