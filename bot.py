"""
NutriBuddy Telegram Bot - Webhook Version for Render
✅ Правильный порядок подключения роутеров
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

dp = None
scheduler = None


async def set_bot_commands(bot: Bot):
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


async def send_startup_notification(bot: Bot, admin_id: int = None):
    try:
        bot_info = await bot.get_me()
        startup_message = (
            f"🟢 <b>NutriBuddy запущен!</b>\n\n"
            f"🤖 Бот: @{bot_info.username}\n"
            f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🌐 Webhook: {WEBHOOK_URL}{WEBHOOK_PATH}\n"
            f"✅ Статус: готов к работе"
        )
        
        if admin_id:
            try:
                await bot.send_message(admin_id, startup_message, parse_mode="HTML")
            except:
                pass
        
        logging.info("=" * 60)
        logging.info("🟢 NutriBuddy Bot Successfully Started!")
        logging.info(f"🤖 Bot Username: @{bot_info.username}")
        logging.info(f"🌐 Webhook URL: {WEBHOOK_URL}{WEBHOOK_PATH}")
        logging.info("=" * 60)
        
    except Exception as e:
        logging.error(f"❌ Startup notification error: {e}")


async def webhook_handler(request):
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
    return web.Response(text="OK")


async def on_startup(app):
    bot = app['bot']
    
    try:
        bot_info = await bot.get_me()
        logging.info(f"🤖 Connected as @{bot_info.username}")
        
        webhook_full_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url != webhook_full_url:
            await bot.set_webhook(
                url=webhook_full_url,
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=True
            )
            logging.info("✅ Webhook set")
        
        await set_bot_commands(bot)
        
        global scheduler
        scheduler = setup_scheduler(bot)
        scheduler.start()
        logging.info("⏰ Scheduler started")
        
        admin_id = os.getenv("ADMIN_ID")
        if admin_id:
            await send_startup_notification(bot, int(admin_id))
        else:
            await send_startup_notification(bot)
        
    except Exception as e:
        logging.error(f"❌ Startup error: {e}", exc_info=True)
        raise


async def on_shutdown(app):
    try:
        bot = app['bot']
        if scheduler:
            scheduler.shutdown(wait=False)
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()
        logging.info("🔴 Bot stopped")
    except Exception as e:
        logging.error(f"❌ Shutdown error: {e}")


def create_app():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


async def main():
    logging.info("🔧 Initializing NutriBuddy...")
    
    await init_db()
    logging.info("💾 Database initialized")
    
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    global dp
    dp = Dispatcher(storage=storage)
    
    # ✅ ВАЖНО: common.router ПЕРВЫМ!
    dp.include_router(common.router)      # 1
    dp.include_router(profile.router)     # 2
    dp.include_router(food.router)        # 3
    dp.include_router(water.router)       # 4
    dp.include_router(shopping.router)    # 5
    dp.include_router(reminders.router)   # 6
    dp.include_router(recipes.router)     # 7
    dp.include_router(activity.router)    # 8
    dp.include_router(progress.router)    # 9
    dp.include_router(ai_handlers.router) # 10
    
    logging.info("✅ All routers included")
    
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
