#!/usr/bin/env python3
"""
Миграция для создания всех таблиц если они не существуют
"""
import asyncio
import logging
from database.db import Base, engine

logger = logging.getLogger(__name__)

async def create_all_tables():
    """Создает все таблицы согласно моделям"""
    try:
        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Все таблицы успешно созданы")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании таблиц: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_all_tables())
