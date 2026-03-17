"""
Подключение к базе данных для NutriBuddy.
Гарантированно создаёт недостающие колонки и приводит типы к BIGINT через явные SQL-запросы.
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
    logger.info("Using PostgreSQL")
else:
    DATABASE_URL = "sqlite+aiosqlite:///nutribudy.db"
    logger.warning("Using SQLite")

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
    Проверяет и изменяет тип колонок, хранящих Telegram ID, с INTEGER на BIGINT.
    Выполняется только для PostgreSQL.
    """
    if "postgresql" not in DATABASE_URL:
        logger.info("ℹ️ Skipping BIGINT migration for non-PostgreSQL database")
        return

    # 1. Колонка telegram_id в таблице users
    result = await conn.execute(text(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name='users' AND column_name='telegram_id'"
    ))
    row = result.first()
    if row and row[0] == 'integer':
        logger.info("🔄 Migrating users.telegram_id from INTEGER to BIGINT...")
        await conn.execute(text("ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT;"))
        logger.info("✅ users.telegram_id is now BIGINT")
    else:
        logger.info("ℹ️ users.telegram_id already BIGINT or not found")

    # 2. Колонка added_by в таблице shopping_items
    result = await conn.execute(text(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name='shopping_items' AND column_name='added_by'"
    ))
    row = result.first()
    if row and row[0] == 'integer':
        logger.info("🔄 Migrating shopping_items.added_by from INTEGER to BIGINT...")
        await conn.execute(text("ALTER TABLE shopping_items ALTER COLUMN added_by TYPE BIGINT;"))
        logger.info("✅ shopping_items.added_by is now BIGINT")
    else:
        logger.info("ℹ️ shopping_items.added_by already BIGINT or not found")

async def init_db():
    """
    Инициализация таблиц, добавление недостающих колонок и приведение типов к BIGINT.
    """
    try:
        logger.info("🔍 Initializing database tables...")
        from database import models  # noqa: F401

        async with engine.begin() as conn:
            # Создаём таблицы
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tables created via create_all()")

            # Проверяем и добавляем недостающие колонки
            if "postgresql" in DATABASE_URL:
                # Колонка unit в shopping_items
                result = await conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='shopping_items' AND column_name='unit'"
                ))
                if not result.first():
                    logger.info("➕ Adding column shopping_items.unit...")
                    await conn.execute(text("ALTER TABLE shopping_items ADD COLUMN unit VARCHAR(20);"))
                    logger.info("✅ shopping_items.unit added")
                else:
                    logger.info("ℹ️ Column 'unit' already exists")

                # Колонка daily_steps_goal в users
                result = await conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='users' AND column_name='daily_steps_goal'"
                ))
                if not result.first():
                    logger.info("➕ Adding column users.daily_steps_goal...")
                    await conn.execute(text("ALTER TABLE users ADD COLUMN daily_steps_goal INTEGER DEFAULT 10000;"))
                    logger.info("✅ users.daily_steps_goal added")
                else:
                    logger.info("ℹ️ Column 'daily_steps_goal' already exists")

            # Миграция BIGINT
            await _ensure_bigint_columns(conn)

            # Проверяем список таблиц для отладки (только для PostgreSQL)
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            ))
            tables = [row[0] for row in result]
            logger.info(f"✅ Tables in DB: {tables}")
            
        logger.info("✅ Database initialized successfully")
        logger.info("💾 Database ready")
        return True

    except Exception as e:
        logger.error(f"❌ Database init failed: {e}", exc_info=True)
        return False

def get_session() -> AsyncSession:
    return async_session()

async def close_db():
    await engine.dispose()
    logger.info("🔌 Database connections closed")
