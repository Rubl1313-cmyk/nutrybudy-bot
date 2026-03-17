#!/usr/bin/env python3
"""
Миграция для добавления недостающих колонок в таблицу users
"""
import asyncio
import logging
from sqlalchemy import text
from database.db import get_session

logger = logging.getLogger(__name__)

async def add_missing_columns():
    """Добавляет недостающие колонки в таблицу users"""
    
    # Список колонок для добавления
    columns_to_add = [
        ("daily_activity_goal", "INTEGER DEFAULT 300"),
        ("neck_cm", "FLOAT"),
        ("waist_cm", "FLOAT"), 
        ("hip_cm", "FLOAT"),
        ("wrist_cm", "FLOAT"),
        ("bicep_cm", "FLOAT"),
        ("chest_cm", "FLOAT"),
        ("forearm_cm", "FLOAT"),
        ("calf_cm", "FLOAT"),
        ("shoulder_width_cm", "FLOAT"),
        ("hip_width_cm", "FLOAT"),
        ("last_bodyfat", "FLOAT"),
        ("last_muscle_mass", "FLOAT"),
        ("last_body_water", "FLOAT"),
        ("goal_weight", "FLOAT"),
        ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
    ]
    
    async with get_session() as session:
        try:
            # Получаем информацию о таблице для SQLite
            result = await session.execute(text("PRAGMA table_info(users)"))
            existing_columns = {row[1] for row in result.fetchall()}
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    # Добавляем колонку, если она не существует
                    await session.execute(text(f"""
                        ALTER TABLE users 
                        ADD COLUMN {column_name} {column_type}
                    """))
                    logger.info(f"✅ Добавлена колонка: {column_name}")
                else:
                    logger.info(f"ℹ️ Колонка {column_name} уже существует")
            
            await session.commit()
            logger.info("✅ Миграция завершена успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении миграции: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(add_missing_columns())
