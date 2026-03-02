"""
NutriBuddy Telegram Bot - Webhook Version for Render
✅ С оповещением при запуске бота
"""
import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher
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

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://nutrybudy-bot.onrender.com")
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 8080))
ADMIN_ID = os.getenv("ADMIN_ID")  # Ваш Telegram ID для уведомлений

dp = None
scheduler = None


async def set_bot_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="help", description="📚 Помощь"),
        BotCommand(command="set_profile", description="👤 Профиль"),
        BotCommand(command="log_food", description="🍽️ Еда"),
        BotCommand(command="log_water", description="💧 Вода"),
        BotCommand(command="log_weight", description="⚖️ Вес"),
        BotCommand(command="fitness", description="🏋️ Активность"),
        BotCommand(command="progress", description="📊 Прогресс"),
        BotCommand(command="recipe", description="📖 Рецепт"),
        BotCommand(command="shopping", description="📋 Покупки"),
        BotCommand(command="reminders", description="🔔 Напоминания"),
        BotCommand(command="cancel", description="❌ Отмена")
    ]
    await bot.set_my_commands(commands)
    logging.info("✅ Bot commands set")


async def send_startup_notification(bot: Bot):
    """
    🔔 Отправляет уведомление о запуске бота администратору
    """
    if not ADMIN_ID:
        logging.warning("⚠️ ADMIN_ID not set — startup notification disabled")
        return
    
    try:
        bot_info = await bot.get_me()
        
        # Формируем красивое сообщение
        startup_message = (
            f"🟢 <b>NutriBuddy успешно запущен!</b>\n\n"
            f"🤖 <b>Бот:</b> @{bot_info.username}\n"
            f"🆔 <b>ID:</b> <code>{bot_info.id}</code>\n"
            f"📅 <b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"🌐 <b>Webhook:</b> <code>{WEBHOOK_URL}{WEBHOOK_PATH}</code>\n"
            f"🗄️ <b>База:</b> {'PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite'}\n"
            f"✅ <b>Статус:</b> готов к работе\n\n"
            f"<i>Бот работает на Render (Free tier)</i>"
        )
        
        # Отправляем сообщение администратору
        await bot.send_message(
            chat_id=int(ADMIN_ID),
            text=startup_message,
            parse_mode="HTML"
        )
        
        logging.info(f"📬 Startup notification sent to admin {ADMIN_ID}")
        
    except Exception as e:
        logging.error(f"❌ Failed to send startup notification: {e}")


async def send_health_check(bot: Bot):
    """
    🔍 Периодическая проверка здоровья бота (каждые 30 мин)
    """
    if not ADMIN_ID:
        return
    
    try:
        bot_info = await bot.get_me()
        health_message = (
            f"💚 <b>NutriBuddy: проверка связи</b>\n\n"
            f"🤖 @{bot_info.username} работает\n"
            f"⏰ {datetime.now().strftime('%H:%M')} UTC"
        )
        await bot.send_message(
            chat_id=int(ADMIN_ID),
            text=health_message,
            parse_mode="HTML"
        )
    except:
        pass  # Игнорируем ошибки health check


async def webhook_handler(request):
    """Обработчик вебхуков от Telegram"""
    try:
        bot = request.app['bot']
        update = await request.json()
        update_obj = Update(**update)
        await dp.feed_update(bot, update_obj)
        return web.Response(status=200)
    except Exception as e:
        logging.error(f"❌ Webhook handler error: {e}", exc_info=True)
        return web.Response(status=500)


async def health_handler(request):
    """Health check endpoint для Render"""
    return web.Response(text="OK")


async def on_startup(app):
    """Выполняется при запуске приложения"""
    bot = app['bot']
    
    try:
        # Проверка подключения к Telegram
        bot_info = await bot.get_me()
        logging.info(f"🤖 Connected as @{bot_info.username}")
        
        # Установка вебхука
        webhook_full_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url != webhook_full_url:
            await bot.set_webhook(
                url=webhook_full_url,
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=True
            )
            logging.info("✅ Webhook set")
        else:
            logging.info("✅ Webhook already configured")
        
        # Установка команд
        await set_bot_commands(bot)
        
        # Запуск планировщика
        global scheduler
        scheduler = setup_scheduler(bot)
        scheduler.start()
        logging.info("⏰ Scheduler started")
        
        # 🔥 ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ О ЗАПУСКЕ
        await send_startup_notification(bot)
        
        # 🔥 Запускаем периодическую проверку здоровья
        async def periodic_health_check():
            while True:
                await asyncio.sleep(1800)  # 30 минут
                await send_health_check(bot)
        
        asyncio.create_task(periodic_health_check())
        
    except Exception as e:
        logging.error(f"❌ Startup error: {e}", exc_info=True)
        raise


async def on_shutdown(app):
    """Выполняется при остановке приложения"""
    try:
        bot = app['bot']
        
        if scheduler:
            scheduler.shutdown(wait=False)
            logging.info("⏰ Scheduler stopped")
        
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()
        logging.info("🔴 Bot stopped")
        
    except Exception as e:
        logging.error(f"❌ Shutdown error: {e}")


def create_app():
    """Создаёт и настраивает aiohttp приложение"""
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


async def main():
    logging.info("🔧 Initializing NutriBuddy...")
    
    # 🔥 Инициализация БД (создаёт таблицы, если нет)
    await init_db()
    logging.info("💾 Database initialized")
    
    
    # Создание бота
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Dispatcher
    storage = MemoryStorage()
    global dp
    dp = Dispatcher(storage=storage)
    
    # Подключение роутеров (ВАЖНО: common.router первым!)
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
    
    logging.info("✅ All routers included")
    
    # Web server
    app = create_app()
    app['bot'] = bot
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    logging.info(f"🚀 Server started on port {PORT}")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logging.info("⏹️ Server stopped")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        logging.info("🔵 Starting NutriBuddy Bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("👋 Keyboard interrupt")
    except Exception as e:
        logging.error(f"💥 Fatal error: {e}", exc_info=True)
        exit(1)
