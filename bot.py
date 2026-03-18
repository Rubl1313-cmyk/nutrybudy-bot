import asyncio
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
# Начинаем настраивать логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log') if os.getenv('LOG_TO_FILE') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальные переменные
dp = None
bot = None

# Импортируем Redis (обязательная зависимость)
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

# Validate required environment variables
required_vars = {
    'BOT_TOKEN': 'Telegram Bot Token',
    'REDIS_URL': 'Redis connection URL'
}

optional_vars = {
    'WEBHOOK_URL': 'Webhook URL (optional for polling)',
    'ADMIN_ID': 'Admin user ID for notifications',
    'CLOUDFLARE_ACCOUNT_ID': 'Cloudflare Account ID',
    'CLOUDFLARE_API_TOKEN': 'Cloudflare API Token',
    'LOG_TO_FILE': 'Enable file logging'
}

missing_vars = []
for var, desc in required_vars.items():
    if not os.getenv(var):
        missing_vars.append(f"{var} ({desc})")

if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

TOKEN = os.getenv('BOT_TOKEN')
REDIS_URL = os.getenv('REDIS_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
ADMIN_ID = os.getenv('ADMIN_ID')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')

# Initialize Redis storage
redis_client = redis.from_url(REDIS_URL)
storage = RedisStorage(redis_client, key_builder=DefaultKeyBuilder(with_bot_id=True))

# FSM Strategy
fsm_strategy = FSMStrategy.CHAT

# Global dispatcher
dp = Dispatcher(storage=storage, fsm_strategy=fsm_strategy)

async def setup_bot_commands(bot: Bot):
    """Настраивает команды бота"""
    commands = [
        BotCommand(command="start", description="🚀 Запуск бота"),
        BotCommand(command="help", description="❓ Помощь"),
        BotCommand(command="set_profile", description="👤 Настроить профиль"),
        BotCommand(command="weight", description="⚖️ Записать вес"),
        BotCommand(command="water", description="💧 Выпить воды"),
        BotCommand(command="fitness", description="🏃‍♂️ Записать активность"),
        BotCommand(command="progress", description="📊 Мой прогресс"),
        BotCommand(command="meal_plan", description="🍽️ План питания"),
        BotCommand(command="achievements", description="🏆 Достижения"),
        BotCommand(command="ask", description="🤖 AI ассистент"),
        BotCommand(command="stats", description="📈 Статистика"),
        BotCommand(command="cancel", description="❌ Отмена")
    ]
    await bot.set_my_commands(commands)

async def on_startup(dispatcher: Dispatcher):
    """Действия при запуске бота"""
    logger.info("Starting NutriBuddy Bot...")
    
    # Инициализация базы данных
    await init_db()
    logger.info("Database initialized")
    
    # Настройка команд бота
    await setup_bot_commands(bot)
    logger.info("Bot commands configured")
    
    # Уведомление админа
    if ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                "🚀 NutriBuddy Bot запущен!\n\n"
                f"📅 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"🤖 Бот готов к работе!"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")
    
    logger.info("NutriBuddy Bot started successfully!")

async def on_shutdown(dispatcher: Dispatcher):
    """Действия при остановке бота"""
    logger.info("Shutting down NutriBuddy Bot...")
    
    # Закрытие соединения с базой данных
    await close_db()
    logger.info("Database connection closed")
    
    # Закрытие Redis
    await redis_client.close()
    logger.info("Redis connection closed")
    
    # Уведомление админа
    if ADMIN_ID:
        try:
            await dispatcher.bot.send_message(
                ADMIN_ID,
                "🛑 NutriBuddy Bot остановлен\n\n"
                f"📅 Время остановки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")
    
    logger.info("NutriBuddy Bot stopped")

def register_handlers():
    """Регистрация всех обработчиков"""
    # Импорты обработчиков
    from handlers.common import router as common_router
    from handlers.profile import router as profile_router
    from handlers.weight import router as weight_router
    from handlers.drinks import router as drinks_router
    from handlers.activity import router as activity_router
    from handlers.progress import router as progress_router
    from handlers.meal_plan import router as meal_plan_router
    from handlers.achievements import router as achievements_router
    from handlers.ai_assistant import router as ai_assistant_router
    from handlers.food_clarification import router as food_clarification_router
    from handlers.reply_handlers import router as reply_handlers_router
    from handlers.universal import router as universal_router
    from handlers.reminder_callbacks import router as reminder_callbacks_router
    
    # Регистрация роутеров
    dp.include_router(common_router)
    dp.include_router(profile_router)
    dp.include_router(weight_router)
    dp.include_router(drinks_router)
    dp.include_router(activity_router)
    dp.include_router(progress_router)
    dp.include_router(meal_plan_router)
    dp.include_router(achievements_router)
    dp.include_router(ai_assistant_router)
    dp.include_router(food_clarification_router)
    dp.include_router(reply_handlers_router)
    dp.include_router(universal_router)
    dp.include_router(reminder_callbacks_router)
    
    # Установка middleware
    from utils.middleware import SmartRateLimitMiddleware
    
    dp.message.middleware(SmartRateLimitMiddleware(user_rate_limiter))
    dp.callback_query.middleware(SmartRateLimitMiddleware(user_rate_limiter))
    dp.message.middleware(SmartRateLimitMiddleware(global_rate_limiter))
    dp.callback_query.middleware(SmartRateLimitMiddleware(global_rate_limiter))
    
    logger.info("All handlers registered")
    
async def schedule_reminders(reminder_service):
    """Планировщик напоминаний"""
    import asyncio
    while True:
        try:
            await reminder_service.check_weekly_reminders()
            await asyncio.sleep(6 * 3600)  # Проверка каждые 6 часов
        except Exception as e:
            logger.error(f"Error in reminder scheduler: {e}")
            await asyncio.sleep(3600)  # При ошибке ждем 1 час

    # Запуск фоновых задач
    logger.info("Starting background tasks...")
    
    # Запуск напоминаний (если включены)
    if os.getenv('ENABLE_REMINDERS', 'true').lower() == 'true':
        from services.reminder_service import ReminderService
        reminder_service = ReminderService(dp.bot)
        # Запуск проверки напоминаний каждые 6 часов
        asyncio.create_task(schedule_reminders(reminder_service))
        logger.info("Reminder service started")
    else:
        logger.info("Reminders disabled")

async def create_app():
    """Создание веб-приложения для webhook"""
    app = web.Application()
    
    # Регистрация webhook handlers
    async def handle_webhook(request):
        """Обработка webhook запросов"""
        if request.method == 'POST':
            update_data = await request.json()
            update = Update.model_validate(update_data, context={"bot": dp.bot})
            # Используем только update, bot уже в context
            await dp.feed_update(update)
            return web.Response(status=200)
        return web.Response(status=405)
    
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_get('/health', lambda request: web.Response(text='OK'))
    
    # Настройка webhook
    if WEBHOOK_URL:
        await dp.bot.set_webhook(
            url=f"{WEBHOOK_URL}/webhook",
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to {WEBHOOK_URL}/webhook")
    
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

async def main():
    """Основная функция"""
    global dp, bot
    logging.info("Starting NutriBuddy Bot...")
    
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
    
    # Redis storage для FSM (обязательный) c fallback
    try:
        redis_client = redis.from_url(REDIS_URL)
        storage = RedisStorage(redis_client, key_builder=DefaultKeyBuilder(with_bot_id=True))
        logger.info("Redis storage initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Redis storage: {e}")
        logger.info("Falling back to memory storage (not recommended for production)")
        from aiogram.fsm.storage.memory import MemoryStorage
        storage = MemoryStorage()
    
    dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.CHAT)
    dp.bot = bot
    
    # Регистрация обработчиков
    register_handlers()
    
    # Запуск в зависимости от режима
    if WEBHOOK_URL:
        # Режим webhook
        app = await create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
        await site.start()
        logger.info(f"Webhook server started on port {os.getenv('PORT', 8080)}")
        
        try:
            # Бесконечный цикл для поддержания работы
            while True:
                await asyncio.sleep(3600)  # Проверка каждую секунду
        except (KeyboardInterrupt, SystemExit):
            logger.info("Received shutdown signal")
        finally:
            await runner.cleanup()
            await on_shutdown(dp)
    else:
        # Режим polling
        await on_startup(dp)
        try:
            await dp.start_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query", "inline_query", "chat_member"]
            )
        except (KeyboardInterrupt, SystemExit):
            logger.info("Received shutdown signal")
        finally:
            await on_shutdown(dp)

def run_polling():
    """Запуск в режиме polling"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

def run_webhook():
    """Запуск в режиме webhook"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == "__main__":
    # Проверка режима запуска
    if WEBHOOK_URL:
        logger.info("Starting in webhook mode")
        run_webhook()
    else:
        logger.info("Starting in polling mode")
        run_polling()
