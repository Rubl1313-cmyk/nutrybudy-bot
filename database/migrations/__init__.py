# Миграции базы данных

async def run_migrations():
    """Запуск всех миграций базы данных"""
    import logging
    from .create_all_tables import create_all_tables
    from .upgrade_to_drink_entries import upgrade
    from .add_all_missing_columns import add_missing_columns
    
    logger = logging.getLogger(__name__)
    
    try:
        # 0. Создание всех таблиц если их нет
        logger.info("🔄 Создаем все таблицы...")
        await create_all_tables()
        logger.info("✅ Все таблицы созданы!")
        
        # 1. Миграция water_entries → drink_entries
        logger.info("🔄 Запускаем миграцию water_entries → drink_entries...")
        await upgrade()
        logger.info("✅ Миграция water_entries завершена!")
        
        # 2. Добавление недостающих колонок во все таблицы
        logger.info("🔄 Добавляем недостающие колонки во все таблицы...")
        await add_missing_columns()
        logger.info("✅ Все колонки добавлены!")
        
        logger.info("✅ Все миграции успешно завершены!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при миграции: {e}")
        raise
