"""
Скрипт для запуска миграции базы данных
"""
import asyncio
import logging
from database.migrations.upgrade_to_drink_entries import upgrade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Запуск миграции"""
    try:
        logger.info("🔄 Начинаем миграцию water_entries → drink_entries...")
        await upgrade()
        logger.info("✅ Миграция успешно завершена!")
    except Exception as e:
        logger.error(f"❌ Ошибка при миграции: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
