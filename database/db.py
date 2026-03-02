"""
Подключение к базе данных для NutriBuddy
✅ PostgreSQL + надёжная инициализация таблиц
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text
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
    DATABASE_URL = "sqlite+aiosqlite:///nutribudy.db"
    logger.warning("⚠️ Using SQLite for local development")

# 🔥 Настройки движка
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
    Инициализация таблиц БД.
    🔥 Создаёт таблицы, если они не существуют.
    """
    try:
        logger.info("🔍 Checking database tables...")
        
        async with engine.begin() as conn:
            # 🔥 Создаём все таблицы
            await conn.run_sync(Base.metadata.create_all)
            
            # 🔥 Проверяем, что таблицы созданы (для отладки)
            if "postgresql" in DATABASE_URL:
                result = await conn.execute(
                    text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                )
                tables = [row[0] for row in result]
                logger.info(f"✅ PostgreSQL tables: {tables}")
            else:
                logger.info("✅ SQLite tables created")
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
        raise


def get_session() -> AsyncSession:
    """
    Возвращает новую сессию БД.
    ⚠️ Синхронная функция! Используйте: async with get_session() as session:
    """
    return async_session()


async def close_db():
    """Закрытие соединений с БД"""
    await engine.dispose()
    logger.info("🔌 Database connections closed")
