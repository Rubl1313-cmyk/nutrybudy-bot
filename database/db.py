"""
ĞŸĞ¾Ğ´ĞºĞ»Ñ�Ñ‡ĞµĞ½Ğ¸Ğµ Ğº Ğ±Ğ°Ğ·Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ´Ğ»Ñ� NutriBuddy.
Ğ“Ğ°Ñ€Ğ°Ğ½Ñ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ¾ Ñ�Ğ¾Ğ·Ğ´Ğ°Ñ‘Ñ‚ Ğ½ĞµĞ´Ğ¾Ñ�Ñ‚Ğ°Ñ�Ñ‰Ğ¸Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸ Ğ¸ Ğ¿Ñ€Ğ¸Ğ²Ğ¾Ğ´Ğ¸Ñ‚ Ñ‚Ğ¸Ğ¿Ñ‹ Ğº BIGINT Ñ‡ĞµÑ€ĞµĞ· Ñ�Ğ²Ğ½Ñ‹Ğµ SQL-Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ñ‹.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "postgresql+asyncpg://" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("[DB] Using PostgreSQL")
else:
    DATABASE_URL = "sqlite+aiosqlite:///nutribudy.db"
    logger.warning("[DB] Using SQLite")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "server_settings": {"application_name": "nutribudy-bot"},
    } if "postgresql" in DATABASE_URL else {}
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def _ensure_bigint_columns(conn):
    """
    ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµÑ‚ Ğ¸ Ğ¸Ğ·Ğ¼ĞµĞ½Ñ�ĞµÑ‚ Ñ‚Ğ¸Ğ¿ ĞºĞ¾Ğ»Ğ¾Ğ½Ğ¾Ğº, Ñ…Ñ€Ğ°Ğ½Ñ�Ñ‰Ğ¸Ñ… Telegram ID, Ñ� INTEGER Ğ½Ğ° BIGINT.
    Ğ’Ñ‹Ğ¿Ğ¾Ğ»Ğ½Ñ�ĞµÑ‚Ñ�Ñ� Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ğ´Ğ»Ñ� PostgreSQL.
    """
    if "postgresql" not in DATABASE_URL:
        logger.info("[DB] Skipping BIGINT migration for non-PostgreSQL database")
        return

    # 1. ĞšĞ¾Ğ»Ğ¾Ğ½ĞºĞ° telegram_id Ğ² Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†Ğµ users
    result = await conn.execute(text(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name='users' AND column_name='telegram_id'"
    ))
    row = result.first()
    if row and row[0] == 'integer':
        logger.info("[DB] Migrating users.telegram_id from INTEGER to BIGINT...")
        await conn.execute(text("ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT;"))
        logger.info("[DB] users.telegram_id is now BIGINT")
    else:
        logger.info("[DB] users.telegram_id already BIGINT or not found")

    # 2. ĞšĞ¾Ğ»Ğ¾Ğ½ĞºĞ° telegram_id Ğ² Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†Ğµ meals
    result = await conn.execute(text(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name='meals' AND column_name='telegram_id'"
    ))
    row = result.first()
    if row and row[0] == 'integer':
        logger.info("[DB] Migrating meals.telegram_id from INTEGER to BIGINT...")
        await conn.execute(text("ALTER TABLE meals ALTER COLUMN telegram_id TYPE BIGINT;"))
        logger.info("[DB] meals.telegram_id is now BIGINT")
    else:
        logger.info("[DB] meals.telegram_id already BIGINT or not found")

async def init_db():
    """
    Ğ£Ğ»ÑƒÑ‡ÑˆĞµĞ½Ğ½Ğ°Ñ� Ğ¸Ğ½Ğ¸Ñ†Ğ¸Ğ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸Ñ� Ğ±Ğ°Ğ·Ñ‹ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ´Ğ»Ñ� NutriBuddy.
    """
    try:
        logger.info("[DB] Initializing database with improved migrations...")
        from database import models  # noqa: F401

        async with engine.begin() as conn:
            # Ğ¡Ğ¾Ğ·Ğ´Ğ°Ñ‘Ğ¼ Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†Ñ‹
            await conn.run_sync(Base.metadata.create_all)
            logger.info("[DB] Tables created via create_all()")

            # Ğ£Ğ»ÑƒÑ‡ÑˆĞµĞ½Ğ½Ğ°Ñ� Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ñ� Ğ´Ğ»Ñ� PostgreSQL
            if "postgresql" in DATABASE_URL:
                await _run_postgresql_migrations(conn)
            else:
                logger.info("[DB] Skipping PostgreSQL migrations for SQLite")

            # ĞœĞ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ñ� BIGINT
            await _ensure_bigint_columns(conn)

            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¸Ğ½Ñ‚ĞµĞ³Ñ€Ğ¸Ñ‚ĞµÑ‚ Ğ±Ğ°Ğ·Ñ‹ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
            await _verify_database_integrity(conn)
            
        logger.info("[DB] Database initialized successfully with improved migrations")
        logger.info("[DB] Database ready")
        return True

    except Exception as e:
        logger.error(f"❌ Database init failed: {e}", exc_info=True)
        return False

async def _run_postgresql_migrations(conn):
    """
    Ğ’Ñ‹Ğ¿Ğ¾Ğ»Ğ½Ñ�ĞµÑ‚ Ğ²Ñ�Ğµ Ğ½ĞµĞ¾Ğ±Ñ…Ğ¾Ğ´Ğ¸Ğ¼Ñ‹Ğµ Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ğ¸ Ğ´Ğ»Ñ� PostgreSQL.
    """
    logger.info("[DB] Running PostgreSQL migrations...")
    
    migrations = [
        # 1. Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸ source Ğ² drink_entries
        {
            "name": "drink_entries_source",
            "check": "SELECT column_name FROM information_schema.columns WHERE table_name='drink_entries' AND column_name='source'",
            "sql": "ALTER TABLE drink_entries ADD COLUMN source VARCHAR(20) DEFAULT 'drink';",
            "description": "drink_entries.source column"
        },
        # 2. Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸ reference_id Ğ² drink_entries  
        {
            "name": "drink_entries_reference_id",
            "check": "SELECT column_name FROM information_schema.columns WHERE table_name='drink_entries' AND column_name='reference_id'",
            "sql": "ALTER TABLE drink_entries ADD COLUMN reference_id INTEGER;",
            "description": "drink_entries.reference_id column"
        },
        # 3. Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸ daily_steps_goal Ğ² users
        {
            "name": "users_daily_steps_goal",
            "check": "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='daily_steps_goal'",
            "sql": "ALTER TABLE users ADD COLUMN daily_steps_goal INTEGER DEFAULT 10000;",
            "description": "users.daily_steps_goal column"
        },
        # 4. Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸ timezone Ğ² users (ĞµÑ�Ğ»Ğ¸ Ğ¾Ñ‚Ñ�ÑƒÑ‚Ñ�Ñ‚Ğ²ÑƒĞµÑ‚)
        {
            "name": "users_timezone",
            "check": "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='timezone'",
            "sql": "ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';",
            "description": "users.timezone column"
        },
        # 5. Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ğµ Ğ¸Ğ½Ğ´ĞµĞºÑ�Ğ° Ğ´Ğ»Ñ� telegram_id Ğ´Ğ»Ñ� Ğ¿Ñ€Ğ¾Ğ¸Ğ·Ğ²Ğ¾Ğ´Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚Ğ¸
        {
            "name": "users_telegram_id_index",
            "check": "SELECT indexname FROM pg_indexes WHERE indexname = 'ix_users_telegram_id'",
            "sql": "CREATE INDEX IF NOT EXISTS ix_users_telegram_id ON users (telegram_id);",
            "description": "users.telegram_id index"
        }
    ]
    
    for migration in migrations:
        try:
            result = await conn.execute(text(migration["check"]))
            if not result.first():
                logger.info(f"[DB] Adding {migration['description']}...")
                await conn.execute(text(migration["sql"]))
                logger.info(f"[DB] {migration['description']} added")
            else:
                logger.info(f"[DB] {migration['description']} already exists")
        except Exception as e:
            logger.error(f"[DB] Failed to apply migration {migration['name']}: {e}")
            # ĞŸĞ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°ĞµĞ¼ Ğ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ¸Ğµ Ğ´Ñ€ÑƒĞ³Ğ¸Ñ… Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ğ¹
    
    logger.info("[DB] PostgreSQL migrations completed")

async def _verify_database_integrity(conn):
    """
    ĞŸĞ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¸Ğ½Ñ‚ĞµĞ³Ñ€Ğ¸Ñ‚ĞµÑ‚ Ğ±Ğ°Ğ·Ñ‹ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
    """
    try:
        # ĞŸĞ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ğµ Ğ¸ Ğ¼ĞµĞ¶Ğ´Ñƒ Ğ½Ğ¸Ğ¼Ğ¸ Ğ¿Ñ€ĞµĞ´Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½Ğ½Ñ‹Ğµ Ğ¸ Ğ¼ĞµĞ¶Ğ´Ñƒ Ğ½Ğ¸Ğ¼Ğ¸ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½Ğ½Ñ‹Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        ))
        tables = [row[0] for row in result]
        expected_tables = ['users', 'meals', 'weight_entries', 'drink_entries', 'water_entries', 'activity_entries']
        
        missing_tables = [table for table in expected_tables if table not in tables]
        if missing_tables:
            logger.warning(f"⚠️ Missing tables: {missing_tables}")
        
        # ĞŸĞ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ ĞºÑ€Ğ¸Ñ‚Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸
        critical_columns = [
            ('users', 'telegram_id', 'BIGINT'),
            ('users', 'timezone', 'VARCHAR'),
            ('meals', 'user_id', 'INTEGER'),
            ('weight_entries', 'user_id', 'INTEGER'),
        ]
        
        for table, column, expected_type in critical_columns:
            result = await conn.execute(text(
                f"SELECT data_type FROM information_schema.columns "
                f"WHERE table_name='{table}' AND column_name='{column}'"
            ))
            row = result.first()
            if not row:
                logger.warning(f"⚠️ Missing {table}.{column}")
            else:
                # Нормализуем типы для сравнения (приводим к нижнему регистру)
                actual_type = row[0].lower().replace(' ', '')
                expected_normalized = expected_type.lower().replace(' ', '')
                
                # Проверяем синонимы типов
                type_synonyms = {
                    'bigint': ['bigint', 'int8'],
                    'varchar': ['varchar', 'character varying', 'char varying'],
                    'integer': ['integer', 'int', 'int4'],
                    'timestamp': ['timestamp', 'timestamp without time zone'],
                    'timestamptz': ['timestamptz', 'timestamp with time zone']
                }
                
                # Проверяем, является ли фактический тип синонимом ожидаемого
                is_valid_type = False
                for base_type, synonyms in type_synonyms.items():
                    if expected_normalized == base_type.lower():
                        if actual_type in [s.lower().replace(' ', '') for s in synonyms]:
                            is_valid_type = True
                            break
                    elif actual_type == expected_normalized:
                        is_valid_type = True
                        break
                
                if not is_valid_type:
                    logger.warning(f"⚠️ {table}.{column} has wrong type: {row[0]} (expected {expected_type})")
        
        logger.info(f"[DB] Database integrity check completed. Tables: {len(tables)}")
        
    except Exception as e:
        logger.error(f"[DB] Database integrity check failed: {e}")

def get_session() -> AsyncSession:
    return async_session()

async def close_db():
    await engine.dispose()
    logger.info("[DB] Database connections closed")
