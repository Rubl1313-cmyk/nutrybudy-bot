"""
NutriBuddy Telegram Bot - Webhook Version for Render
Оптимизировано для работы на Render с webhook вместо polling
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, WebhookInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update, BotCommand
from dotenv import load_dotenv
from aiohttp import web
from database.db import init_db
from handlers import (
    common, profile, food, water, shopping,
    reminders, recipes, activity, progress, ai_handlers
)
from scheduler.jobs import setup_scheduler

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Константы
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://nutrybudy-bot.onrender.com")
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 8080))

# Глобальные переменные
dp = None
scheduler = None


async def set_bot_commands(bot: Bot):
    """Устанавливает команды бота для меню"""
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="help", description="📚 Помощь и команды"),
        BotCommand(command="set_profile", description="👤 Настроить профиль"),
        BotCommand(command="log_food", description="🍽️ Записать приём пищи"),
        BotCommand(command="log_water", description="💧 Добавить воду"),
        BotCommand(command="log_weight", description="⚖️ Записать вес"),
        BotCommand(command="fitness", description="🏋️ Добавить активность"),
        BotCommand(command="progress", description="📊 Графики прогресса"),
        BotCommand(command="recipe", description="📖 Генерировать рецепт"),
        BotCommand(command="shopping", description="📋 Списки покупок"),
        BotCommand(command="reminders", description="🔔 Напоминания"),
        BotCommand(command="cancel", description="❌ Отменить действие")
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Bot commands set")


async def webhook_handler(request):
    """
    Обработчик вебхуков от Telegram
    Получает updates и передаёт их в Dispatcher
    """
    try:
        bot = request.app['bot']
        update = await request.json()
        
        # Преобразуем JSON в Update объект
        update_obj = Update(**update)
        
        # Передаём update в Dispatcher
        await dp.feed_update(bot, update_obj)
        
        return web.Response(status=200)
        
    except Exception as e:
        logger.error(f"❌ Webhook handler error: {e}", exc_info=True)
        return web.Response(status=500, text="Internal Server Error")


async def health_handler(request):
    """
    Health check endpoint для Render
    Используется для проверки работоспособности сервиса
    """
    return web.Response(text="OK", content_type="text/plain")


async def on_startup(app):
    """
    Выполняется при запуске приложения
    Устанавливает вебхук и инициализирует планировщик
    """
    bot = app['bot']
    
    try:
        # Проверяем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Bot started: @{bot_info.username} (ID: {bot_info.id})")
        
        # Формируем полный URL вебхука
        webhook_full_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        
        # Получаем текущую информацию о вебхуке
        webhook_info = await bot.get_webhook_info()
        
        # Если вебхук отличается - обновляем
        if webhook_info.url != webhook_full_url:
            logger.info(f"🔗 Setting webhook to: {webhook_full_url}")
            await bot.set_webhook(
                url=webhook_full_url,
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=True  # Отбрасываем старые обновления
            )
            logger.info("✅ Webhook set successfully")
        else:
            logger.info("✅ Webhook already configured correctly")
        
        # Устанавливаем команды бота
        await set_bot_commands(bot)
        
        # Инициализируем и запускаем планировщик
        global scheduler
        scheduler = setup_scheduler(bot)
        scheduler.start()
        logger.info("⏰ Scheduler started")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)
        raise


async def on_shutdown(app):
    """
    Выполняется при остановке приложения
    Удаляет вебхук для корректного завершения
    """
    try:
        bot = app['bot']
        
        # Останавливаем планировщик
        if scheduler:
            scheduler.shutdown(wait=False)
            logger.info("⏰ Scheduler stopped")
        
        # Удаляем вебхук
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🔌 Webhook deleted")
        
        # Закрываем сессию бота
        await bot.session.close()
        logger.info("🔒 Bot session closed")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}", exc_info=True)


def create_app():
    """
    Создаёт и настраивает aiohttp приложение
    """
    app = web.Application()
    
    # Регистрируем роуты
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/webhook_info", webhook_info_handler)
    
    # Регистрируем хуки запуска/остановки
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    return app


async def webhook_info_handler(request):
    """
    Эндпоинт для проверки информации о вебхуке
    Доступен только для отладки
    """
    try:
        bot = request.app['bot']
        info = await bot.get_webhook_info()
        return web.json_response({
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def main():
    """
    Точка входа приложения
    """
    # Инициализация базы данных
    await init_db()
    logger.info("💾 Database initialized")
    
    # Создаём бота
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создаём Dispatcher
    storage = MemoryStorage()
    global dp
    dp = Dispatcher(storage=storage)
    
    # Подключаем роутеры
    dp.include_router(common.router)
    dp.include_router(profile.router)
    dp.include_router(food.router)
    dp.include_router(water.router)
    dp.include_router(shopping.router)
    dp.include_router(reminders.router)
    dp.include_router(recipes.router)
    dp.include_router(activity.router)
    dp.include_router(progress.router)
    dp.include_router(ai_handlers.router)
    
    logger.info("✅ All routers included")
    
    # Создаём приложение
    app = create_app()
    app['bot'] = bot
    
    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    logger.info(f"🚀 Server started on port {PORT}")
    logger.info(f"🌐 Webhook URL: {WEBHOOK_URL}{WEBHOOK_PATH}")
    logger.info(f"❤️ Health check: {WEBHOOK_URL}/health")
    
    # Держим процесс активным
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("⏹️ Server stopped")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        exit(1)
