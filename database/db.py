"""
Подключение к базе данных
✅ Поддержка PostgreSQL для постоянного хранения
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")

# 🔥 Конвертация URL для asyncpg
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "postgresql+asyncpg://" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    # Fallback на SQLite (только для локальной разработки!)
    DATABASE_URL = "sqlite+aiosqlite:///nutribudy.db"
    logger.warning("⚠️ Using SQLite for local development. Use PostgreSQL for production!")

# 🔥 Настройки движка
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Включите True для отладки SQL запросов
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Переподключение каждые 1 час
    connect_args={
        "server_settings": {
            "application_name": "nutribudy-bot",
        },
    } if "postgresql" in DATABASE_URL else {}
)

# 🔥 Session maker
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def init_db():
    """
    Инициализация таблиц БД.
    Создаёт таблицы, если они не существуют.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def get_session() -> AsyncSession:
    """
    Возвращает новую сессию БД.
    
    ⚠️ ВАЖНО: Это синхронная функция!
    Используйте как: async with get_session() as session:
    """
    return async_session()


async def close_db():
    """Закрытие соединений с БД (при остановке бота)"""
    await engine.dispose()
    logger.info("🔌 Database connections closed")
