"""
Миграция для создания таблицы drink_entries
"""
from sqlalchemy import text
from database.db import engine

async def upgrade():
    """Создание таблицы drink_entries с миграцией данных"""
    
    # Импортируем engine и DATABASE_URL для актуального состояния
    from database.db import engine
    import os
    import logging
    logger = logging.getLogger(__name__)
    
    # Определяем тип БД более надежным способом
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    is_postgresql = "postgresql" in DATABASE_URL.lower()
    
    # Принудительно используем PostgreSQL, если есть DATABASE_URL
    if DATABASE_URL and not is_postgresql:
        logger.warning(f"[MIGRATION] DATABASE_URL found but no postgresql keyword, forcing PostgreSQL")
        is_postgresql = True
    
    logger.info(f"[MIGRATION] Database dialect: {engine.dialect.name}")
    logger.info(f"[MIGRATION] DATABASE_URL contains postgresql: {is_postgresql}")
    logger.info(f"[MIGRATION] DATABASE_URL length: {len(DATABASE_URL)}")
    
    async with engine.begin() as conn:
        # Проверяем существование таблицы water_entries (универсальный способ)
        try:
            if is_postgresql:
                # PostgreSQL
                result = await conn.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'water_entries'
                """))
            else:
                # SQLite
                result = await conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='water_entries'
                """))
            
            water_exists = result.fetchone()
        except Exception:
            water_exists = None
        
        if water_exists:
            # Сначала проверяем структуру water_entries
            try:
                if is_postgresql:
                    columns_result = await conn.execute(text("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'water_entries'
                    """))
                else:
                    columns_result = await conn.execute(text("PRAGMA table_info(water_entries)"))
                
                columns = [row[0] for row in columns_result.fetchall()]
                logger.info(f"[MIGRATION] water_entries columns: {columns}")
                
                # Проверяем наличие колонки datetime
                has_datetime = 'datetime' in columns
                logger.info(f"[MIGRATION] water_entries has datetime column: {has_datetime}")
                
            except Exception as e:
                logger.warning(f"[MIGRATION] Failed to check water_entries structure: {e}")
                has_datetime = False  # Предполагаем, что колонки нет
            
            # Создаем новую таблицу drink_entries с учетом типа БД
            if is_postgresql:
                logger.info("[MIGRATION] Creating PostgreSQL table")
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS drink_entries (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL DEFAULT 'вода',
                        volume_ml FLOAT NOT NULL,
                        calories FLOAT DEFAULT 0.0,
                        datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """))
            else:
                logger.info("[MIGRATION] Creating SQLite table")
                # SQLite
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
                
            # Дополнительная проверка - если все еще ошибка, пробуем принудительно PostgreSQL
            try:
                # Копируем данные из water_entries в drink_entries с учетом наличия колонки datetime
                if has_datetime:
                    await conn.execute(text("""
                        INSERT INTO drink_entries (user_id, name, volume_ml, calories, datetime)
                        SELECT user_id, 'вода', amount, 0.0, datetime 
                        FROM water_entries
                    """))
                else:
                    # Если колонки datetime нет, используем CURRENT_TIMESTAMP
                    await conn.execute(text("""
                        INSERT INTO drink_entries (user_id, name, volume_ml, calories)
                        SELECT user_id, 'вода', amount, 0.0
                        FROM water_entries
                    """))
                
                # Удаляем старую таблицу
                await conn.execute(text("DROP TABLE water_entries"))
                
                logger.info("[SUCCESS] Миграция завершена: water_entries → drink_entries")
                
            except Exception as e:
                if "AUTOINCREMENT" in str(e) and is_postgresql:
                    logger.error("[MIGRATION] PostgreSQL detected but SQLite syntax used, forcing PostgreSQL recreation")
                    # Пересоздаем таблицу с правильным синтаксисом
                    await conn.execute(text("DROP TABLE IF EXISTS drink_entries"))
                    await conn.execute(text("""
                        CREATE TABLE drink_entries (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            name VARCHAR(100) NOT NULL DEFAULT 'вода',
                            volume_ml FLOAT NOT NULL,
                            calories FLOAT DEFAULT 0.0,
                            datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                        )
                    """))
                    # Повторяем копирование данных с учетом структуры
                    if has_datetime:
                        await conn.execute(text("""
                            INSERT INTO drink_entries (user_id, name, volume_ml, calories, datetime)
                            SELECT user_id, 'вода', amount, 0.0, datetime 
                            FROM water_entries
                        """))
                    else:
                        await conn.execute(text("""
                            INSERT INTO drink_entries (user_id, name, volume_ml, calories)
                            SELECT user_id, 'вода', amount, 0.0
                            FROM water_entries
                        """))
                    await conn.execute(text("DROP TABLE water_entries"))
                    logger.info("[SUCCESS] Миграция завершена с принудительным PostgreSQL синтаксисом")
                else:
                    raise e
            
            logger.info("[SUCCESS] Миграция завершена: water_entries → drink_entries")
        else:
            # Просто создаем новую таблицу с правильным синтаксисом
            if is_postgresql:
                logger.info("[MIGRATION] Creating PostgreSQL table (no water_entries)")
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS drink_entries (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL DEFAULT 'вода',
                        volume_ml FLOAT NOT NULL,
                        calories FLOAT DEFAULT 0.0,
                        datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """))
            else:
                logger.info("[MIGRATION] Creating SQLite table (no water_entries)")
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
            
            logger.info("[SUCCESS] Таблица drink_entries создана")

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
        
        logger.info("[SUCCESS] Откат миграции завершен")
