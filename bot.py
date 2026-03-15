import asyncio
import logging
import os
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
from sqlalchemy import text
from aiogram.fsm.strategy import FSMStrategy

load_dotenv('.env')

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
        BotCommand(command="set_profile", description="👤 Настроить профиль"),
        BotCommand(command="profile", description="👤 Мой профиль"),
        BotCommand(command="log_food", description="🍽️ Добавить еду"),
        BotCommand(command="log_water", description="💧 Записать воду"),
        BotCommand(command="water", description="💧 Статистика воды"),
        BotCommand(command="log_weight", description="⚖️ Записать вес"),
        BotCommand(command="weight", description="⚖️ Статистика веса"),
        BotCommand(command="fitness", description="� Добавить активность"),
        BotCommand(command="activity", description="🏃 Статистика активности"),
        BotCommand(command="progress", description="📊 Мой прогресс"),
        BotCommand(command="stats", description="📊 Статистика за сегодня"),
        BotCommand(command="ask", description="💬 AI ассистент"),
        BotCommand(command="ai", description="💬 AI ассистент"),
        BotCommand(command="weather", description="🌦️ Погода"),
        BotCommand(command="recipe", description="🍳 Рецепт"),
        BotCommand(command="calculate", description="🧮 Рассчитать КБЖУ"),
        BotCommand(command="meal_plan", description="🍽️ План питания"),
        BotCommand(command="diet", description="🍽️ План питания"),
        BotCommand(command="nutrition", description="🥗 Советы по питанию"),
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
            f"✅ Статус: готов к работе"
        )
        await bot.send_message(chat_id=int(ADMIN_ID), text=startup_message, parse_mode="HTML")
        logger.info(f"📬 Startup notification sent to admin {ADMIN_ID}")
    except Exception as e:
        logger.error(f"❌ Failed to send startup notification: {e}")

async def webhook_handler(request):
    """Обработчик вебхука"""
    try:
        bot = request.app['bot']
        dp = request.app['dp']
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
    global dp
    logging.info("Starting NutriBuddy Bot on Railway...")
    
    # Запускаем миграции БД
    from database.migrations import run_migrations
    await run_migrations()
    
    # Валидация токена только в production
    validate_token = os.getenv('RAILWAY_ENVIRONMENT') == 'production'
    
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        validate_token=validate_token
    )
    
    storage = MemoryStorage()
    
    dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.GLOBAL_USER)
    
    # Подключение роутеров в правильном порядке:
    # 1. Команды и специфические обработчики (должны быть первыми)
    # 2. Медиа и AI обработчики
    # 3. Универсальный обработчик текста (dialog) - должен быть последним
    
    from handlers import dialog, ai_handler, common, profile, water, progress, activity, weight, meal_plan, ai_assistant, reply_handlers, achievements

    # Команды и специфические обработчики
    dp.include_router(common.router)           # /start, /help, /cancel и т.д.
    dp.include_router(profile.router)          # /set_profile, /profile
    dp.include_router(water.router)            # /log_water, /water
    dp.include_router(progress.router)         # /progress, /stats
    dp.include_router(activity.router)         # /fitness, /activity
    dp.include_router(weight.router)           # /log_weight, /weight
    dp.include_router(meal_plan.router)        # /meal_plan, /diet
    dp.include_router(ai_assistant.router)     # /ask, /ai, /weather
    dp.include_router(achievements.router)     # /achievements
    
    # Медиа и AI обработчики
    dp.include_router(ai_handler.router)       # Фото и другие медиа
    
    # Обработчики reply-кнопок – ДО универсального!
    dp.include_router(reply_handlers.router)   # Reply-кнопки
    
    # Универсальный обработчик текста – ПОСЛЕДНИМ
    dp.include_router(dialog.router)           # Все остальные текстовые сообщения
    
    logging.info("All routers included in correct order for FSM")
    
    app = create_app()
    app['bot'] = bot
    app['dp'] = dp  # Передаем диспетчер в контекст
    
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