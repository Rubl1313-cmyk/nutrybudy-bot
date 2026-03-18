"""
Миграция: Удаление полей состава тела из таблицы users
Эти поля теперь рассчитываются автоматически из обхватов
"""
import logging
from sqlalchemy import text
from database.db import get_session

logger = logging.getLogger(__name__)

async def run_migration():
    """Удаление полей состава тела из таблицы users"""
    logger.info("🔄 Начинаю миграцию: удаление полей состава тела")
    
    try:
        async with get_session() as session:
            # Проверяем существование колонок перед удалением
            check_columns_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('last_bodyfat', 'last_muscle_mass', 'last_body_water')
            """
            
            result = await session.execute(text(check_columns_sql))
            existing_columns = [row[0] for row in result.fetchall()]
            
            logger.info(f"📋 Найденные колонки для удаления: {existing_columns}")
            
            # Удаляем колонки если они существуют
            for column in existing_columns:
                alter_sql = f"ALTER TABLE users DROP COLUMN {column}"
                await session.execute(text(alter_sql))
                logger.info(f"✅ Удалена колонка: {column}")
            
            await session.commit()
            
            logger.info("✅ Миграция успешно завершена: поля состава тела удалены")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при миграции: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_migration())
