"""
Подключение к базе данных для NutriBuddy
✅ Полностью асинхронное создание таблиц
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
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
    logger.info(f"🗄️ Using PostgreSQL")
else:
    DATABASE_URL = "sqlite+aiosqlite:///nutribudy.db"
    logger.warning("⚠️ Using SQLite")

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


async def init_db():
    """
    🔥 Создаёт все таблицы, если их нет.
    """
    try:
        logger.info("🔍 Initializing database tables...")
        
        # Импортируем модели, чтобы они зарегистрировались в Base.metadata
        from database import models  # noqa: F401

        async with engine.begin() as conn:
            # Создаём таблицы
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tables created via create_all()")

            # 🔥 Асинхронная проверка списка таблиц
            from sqlalchemy import inspect
            def get_tables(sync_conn):
                inspector = inspect(sync_conn)
                return inspector.get_table_names()

            tables = await conn.run_sync(get_tables)
            logger.info(f"✅ Tables in DB: {tables}")

        logger.info("✅ Database initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Database init failed: {e}", exc_info=True)
        return False


def get_session() -> AsyncSession:
    return async_session()


async def close_db():
    await engine.dispose()
    logger.info("🔌 Database connections closed")
