"""
Подключение к базе данных для NutriBuddy.
Гарантированно создаёт недостающие колонки.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, inspect
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
    logger.info("🗄️ Using PostgreSQL")
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
    Инициализация таблиц и добавление недостающих колонок.
    """
    try:
        logger.info("🔍 Initializing database tables...")
        from database import models  # noqa: F401

        async with engine.begin() as conn:
            # Создаём таблицы
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tables created via create_all()")

            # 🔥 Добавляем колонку unit, если её нет (для PostgreSQL)
            if "postgresql" in DATABASE_URL:
                # Проверяем существование колонки
                inspector = inspect(conn.sync_engine)
                columns = [col['name'] for col in inspector.get_columns('shopping_items')]
                if 'unit' not in columns:
                    await conn.execute(text(
                        "ALTER TABLE shopping_items ADD COLUMN unit VARCHAR(20) DEFAULT 'шт'"
                    ))
                    logger.info("✅ Column 'unit' added to shopping_items")
                else:
                    logger.info("ℹ️ Column 'unit' already exists")

            # Проверяем все таблицы
            inspector = inspect(conn.sync_engine)
            tables = inspector.get_table_names()
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
