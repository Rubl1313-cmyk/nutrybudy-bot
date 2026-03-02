"""
Подключение к базе данных для NutriBuddy
✅ PostgreSQL + надёжное создание таблиц
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text, inspect
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
    logger.info(f"🗄️ Using PostgreSQL: {DATABASE_URL[:50]}...")
else:
    DATABASE_URL = "sqlite+aiosqlite:///nutribudy.db"
    logger.warning("⚠️ Using SQLite for local development")

# 🔥 Настройки движка
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Включите True для отладки SQL
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Переподключение каждые 1 час
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
    🔥 Надёжная инициализация таблиц БД.
    Создаёт таблицы, если они не существуют.
    """
    try:
        logger.info("🔍 Initializing database tables...")
        
        async with engine.begin() as conn:
            # 🔥 Создаём все таблицы из Base.metadata
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tables created via create_all()")
            
            # 🔥 Проверяем, что таблицы действительно созданы
            inspector = inspect(conn.sync_engine)
            tables = inspector.get_table_names()
            logger.info(f"✅ Tables in database: {tables}")
            
            # 🔥 Если нет нужных таблиц — создаём вручную (fallback)
            required_tables = ['users', 'meals', 'food_items', 'water_entries', 
                             'weight_entries', 'shopping_lists', 'shopping_items',
                             'reminders', 'activities']
            
            missing = [t for t in required_tables if t not in tables]
            if missing:
                logger.warning(f"⚠️ Missing tables: {missing}. Trying manual creation...")
                for table_name in missing:
                    table = Base.metadata.tables.get(table_name)
                    if table is not None:
                        await conn.run_sync(table.create, checkfirst=True)
                        logger.info(f"✅ Created table: {table_name}")
        
        logger.info("✅ Database initialization complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
        return False


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
