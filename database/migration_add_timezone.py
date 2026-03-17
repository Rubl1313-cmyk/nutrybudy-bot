"""
Миграция для добавления поля timezone в таблицу users
"""
from datetime import datetime, timezone

async def add_timezone_column():
    """Добавляет колонку timezone в таблицу users"""
    
    migration_sql = """
    -- Добавляем колонку timezone в таблицу users
    ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';
    
    -- Обновляем существующие записи
    UPDATE users SET timezone = 'UTC' WHERE timezone IS NULL;
    """
    
    return migration_sql

# Версия миграции
MIGRATION_VERSION = "1.8.0"
MIGRATION_DESCRIPTION = "Добавление поля timezone для хранения часового пояса пользователя"
