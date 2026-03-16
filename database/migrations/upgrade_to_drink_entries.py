"""
Миграция для создания таблицы drink_entries
"""
from sqlalchemy import text
from database.db import engine

async def upgrade():
    """Создание таблицы drink_entries с миграцией данных"""
    
    async with engine.begin() as conn:
        # Проверяем существование таблицы water_entries
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='water_entries'
        """))
        water_exists = result.fetchone()
        
        if water_exists:
            # Создаем новую таблицу drink_entries
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS drink_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL DEFAULT 'вода',
                    volume_ml FLOAT NOT NULL,
                    calories FLOAT DEFAULT 0.0,
                    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """))
            
            # Копируем данные из water_entries в drink_entries
            await conn.execute(text("""
                INSERT INTO drink_entries (user_id, name, volume_ml, calories, datetime)
                SELECT user_id, 'вода', amount, 0.0, datetime 
                FROM water_entries
            """))
            
            # Удаляем старую таблицу
            await conn.execute(text("DROP TABLE water_entries"))
            
            print("✅ Миграция завершена: water_entries → drink_entries")
        else:
            # Просто создаем новую таблицу
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS drink_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL DEFAULT 'вода',
                    volume_ml FLOAT NOT NULL,
                    calories FLOAT DEFAULT 0.0,
                    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """))
            
            print("✅ Таблица drink_entries создана")

async def downgrade():
    """Откат миграции"""
    async with engine.begin() as conn:
        # Создаем старую таблицу water_entries
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS water_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount FLOAT NOT NULL,
                datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """))
        
        # Копируем только записи о воде (без калорий)
        await conn.execute(text("""
            INSERT INTO water_entries (user_id, amount, datetime)
            SELECT user_id, volume_ml, datetime 
            FROM drink_entries 
            WHERE name = 'вода' AND calories = 0.0
        """))
        
        # Удаляем drink_entries
        await conn.execute(text("DROP TABLE drink_entries"))
        
        print("✅ Откат миграции завершен")
