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
    ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµÑ‚ Ğ¸ Ğ¸Ğ·Ğ¼ĞµĞ½Ñ�ĞµÑ‚ Ñ‚Ğ¸Ğ¿ ĞºĞ¾Ğ»Ğ¾Ğ½Ğ¾Ğº, Ñ…Ñ€Ğ°Ğ½Ñ�Ñ‰Ğ¸Ñ… Telegram ID, Ñ� INTEGER Ğ½Ğ° BIGINT.
    Ğ’Ñ‹Ğ¿Ğ¾Ğ»Ğ½Ñ�ĞµÑ‚Ñ�Ñ� Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ğ´Ğ»Ñ� PostgreSQL.
    """
    if "postgresql" not in DATABASE_URL:
        logger.info("â„¹ï¸� Skipping BIGINT migration for non-PostgreSQL database")
        return

    # 1. ĞšĞ¾Ğ»Ğ¾Ğ½ĞºĞ° telegram_id Ğ² Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†Ğµ users
    result = await conn.execute(text(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name='users' AND column_name='telegram_id'"
    ))
    row = result.first()
    if row and row[0] == 'integer':
        logger.info("ğŸ”„ Migrating users.telegram_id from INTEGER to BIGINT...")
        await conn.execute(text("ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT;"))
        logger.info("âœ… users.telegram_id is now BIGINT")
    else:
        logger.info("â„¹ï¸� users.telegram_id already BIGINT or not found")

    # 2. ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�ĞºĞ°ĞµĞ¼ Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ñ� shopping_items - Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†Ğ° Ğ½Ğµ Ñ�ÑƒÑ‰ĞµÑ�Ñ‚Ğ²ÑƒĞµÑ‚ Ğ² Ğ¼Ğ¾Ğ´ĞµĞ»Ñ�Ñ…
    logger.info("â„¹ï¸� Skipping shopping_items migration - table not defined in models")

async def init_db():
    """
    Ğ˜Ğ½Ğ¸Ñ†Ğ¸Ğ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸Ñ� Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†, Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ğµ Ğ½ĞµĞ´Ğ¾Ñ�Ñ‚Ğ°Ñ�Ñ‰Ğ¸Ñ… ĞºĞ¾Ğ»Ğ¾Ğ½Ğ¾Ğº Ğ¸ Ğ¿Ñ€Ğ¸Ğ²ĞµĞ´ĞµĞ½Ğ¸Ğµ Ñ‚Ğ¸Ğ¿Ğ¾Ğ² Ğº BIGINT.
    """
    try:
        logger.info("ğŸ”� Initializing database tables...")
        from database import models  # noqa: F401

        async with engine.begin() as conn:
            # Ğ¡Ğ¾Ğ·Ğ´Ğ°Ñ‘Ğ¼ Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†Ñ‹
            await conn.run_sync(Base.metadata.create_all)
            logger.info("âœ… Tables created via create_all()")

            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¸ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ½ĞµĞ´Ğ¾Ñ�Ñ‚Ğ°Ñ�Ñ‰Ğ¸Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸
            if "postgresql" in DATABASE_URL:
                # ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�ĞºĞ°ĞµĞ¼ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ğµ ĞºĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸ Ğ² shopping_items - Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†Ğ° Ğ½Ğµ Ñ�ÑƒÑ‰ĞµÑ�Ñ‚Ğ²ÑƒĞµÑ‚
                logger.info("â„¹ï¸� Skipping shopping_items.unit column - table not defined in models")

                # ĞšĞ¾Ğ»Ğ¾Ğ½ĞºĞ¸ source Ğ¸ reference_id Ğ² drink_entries (Ğ´Ğ»Ñ� PostgreSQL)
                result = await conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='drink_entries' AND column_name='source'"
                ))
                if not result.first():
                    logger.info("â�• Adding column drink_entries.source...")
                    await conn.execute(text("ALTER TABLE drink_entries ADD COLUMN source VARCHAR(20) DEFAULT 'drink';"))
                    logger.info("âœ… drink_entries.source added")
                else:
                    logger.info("â„¹ï¸� Column 'source' already exists in drink_entries")

                result = await conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='drink_entries' AND column_name='reference_id'"
                ))
                if not result.first():
                    logger.info("â�• Adding column drink_entries.reference_id...")
                    await conn.execute(text("ALTER TABLE drink_entries ADD COLUMN reference_id INTEGER;"))
                    logger.info("âœ… drink_entries.reference_id added")
                else:
                    logger.info("â„¹ï¸� Column 'reference_id' already exists in drink_entries")

                # ĞšĞ¾Ğ»Ğ¾Ğ½ĞºĞ° daily_steps_goal Ğ² users
                result = await conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='users' AND column_name='daily_steps_goal'"
                ))
                if not result.first():
                    logger.info("â�• Adding column users.daily_steps_goal...")
                    await conn.execute(text("ALTER TABLE users ADD COLUMN daily_steps_goal INTEGER DEFAULT 10000;"))
                    logger.info("âœ… users.daily_steps_goal added")
                else:
                    logger.info("â„¹ï¸� Column 'daily_steps_goal' already exists")

            # ĞœĞ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ñ� BIGINT
            await _ensure_bigint_columns(conn)

            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ñ�Ğ¿Ğ¸Ñ�Ğ¾Ğº Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ† Ğ´Ğ»Ñ� Ğ¾Ñ‚Ğ»Ğ°Ğ´ĞºĞ¸ (Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ğ´Ğ»Ñ� PostgreSQL)
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            ))
            tables = [row[0] for row in result]
            logger.info(f"âœ… Tables in DB: {tables}")
            
        logger.info("âœ… Database initialized successfully")
        logger.info("ğŸ’¾ Database ready")
        return True

    except Exception as e:
        logger.error(f"â�Œ Database init failed: {e}", exc_info=True)
        return False

def get_session() -> AsyncSession:
    return async_session()

async def close_db():
    await engine.dispose()
    logger.info("ğŸ”Œ Database connections closed")
