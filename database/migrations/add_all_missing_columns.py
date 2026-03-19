#!/usr/bin/env python3
"""
Миграция для добавления недостающих колонок во все таблицы
"""
import asyncio
import logging
from sqlalchemy import text
from database.db import get_session

logger = logging.getLogger(__name__)

async def add_missing_columns():
    """Добавляет недостающие колонки во все таблицы"""
    
    # Определения колонок для каждой таблицы
    tables_columns = {
        'weight_entries': [
            ("body_fat", "FLOAT"),
            ("muscle_mass", "FLOAT"), 
            ("body_water", "FLOAT")
        ],
        'food_entries': [
            ("fiber", "FLOAT DEFAULT 0"),
            ("sugar", "FLOAT DEFAULT 0"),
            ("sodium", "FLOAT DEFAULT 0"),
            ("meal_type", "VARCHAR(20) NOT NULL DEFAULT 'snack'"),
            ("quantity", "FLOAT DEFAULT 1"),
            ("unit", "VARCHAR(20) DEFAULT 'шт'")
        ],
        'drink_entries': [
            ("sugar", "FLOAT DEFAULT 0"),
            ("caffeine", "FLOAT DEFAULT 0")
        ],
        'activity_entries': [
            ("distance", "FLOAT"),
            ("intensity", "VARCHAR(20) DEFAULT 'moderate'")
        ],
        'users': [
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
            ("goal_weight", "FLOAT"),
            ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
        ]
    }
    
    from database.db import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            from database.db import engine
            
            # Получаем существующие колонки для всех таблиц
            existing_columns = {}
            
            if engine.dialect.name == 'postgresql':
                # PostgreSQL
                for table_name in tables_columns.keys():
                    result = await session.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}' 
                        AND table_schema = 'public'
                    """))
                    existing_columns[table_name] = {row[0] for row in result.fetchall()}
            else:
                # SQLite
                for table_name in tables_columns.keys():
                    result = await session.execute(text(f"PRAGMA table_info({table_name})"))
                    existing_columns[table_name] = {row[1] for row in result.fetchall()}
            
            # Добавляем недостающие колонки
            for table_name, columns in tables_columns.items():
                logger.info(f"🔍 Проверяем таблицу: {table_name}")
                
                for column_name, column_type in columns:
                    if column_name not in existing_columns.get(table_name, set()):
                        # Добавляем колонку, если она не существует
                        if engine.dialect.name == 'postgresql':
                            alter_sql = f"""
                                ALTER TABLE {table_name} 
                                ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                            """
                        else:
                            alter_sql = f"""
                                ALTER TABLE {table_name} 
                                ADD COLUMN {column_name} {column_type}
                            """
                        
                        await session.execute(text(alter_sql))
                        logger.info(f"✅ Добавлена колонка {column_name} в таблицу {table_name}")
                    else:
                        logger.info(f"ℹ️ Колонка {column_name} уже существует в таблице {table_name}")
            
            await session.commit()
            logger.info("✅ Все миграции завершены успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении миграции: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(add_missing_columns())
