# Миграции базы данных

async def run_migrations():
    """Запуск всех миграций базы данных"""
    import logging
    from .upgrade_to_drink_entries import upgrade
    from .add_missing_columns import add_missing_columns
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Миграция water_entries → drink_entries
        logger.info("🔄 Запускаем миграцию water_entries → drink_entries...")
        await upgrade()
        logger.info("✅ Миграция water_entries завершена!")
        
        # 2. Добавление недостающих колонок
        logger.info("🔄 Добавляем недостающие колонки...")
        await add_missing_columns()
        logger.info("✅ Колонки добавлены!")
        
        logger.info("✅ Все миграции успешно завершены!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при миграции: {e}")
        raise
