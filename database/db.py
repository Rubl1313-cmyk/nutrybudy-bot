"""
Подключение к базе данных
✅ ИСПРАВЛЕНО: get_session() теперь синхронная функция
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from database.models import Base

DATABASE_URL = os.getenv("DATABASE_URL")

# Конвертация postgres:// в postgresql+asyncpg://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Создание движка
engine = create_async_engine(
    DATABASE_URL or "sqlite+aiosqlite:///nutribudy.db",
    echo=False
)

# Session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Инициализация таблиц БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_session() -> AsyncSession:
    """
    ✅ Возвращает сессию БД.
    ⚠️ ВАЖНО: Это СИНХРОННАЯ функция!
    Используется как: async with get_session() as session:
    """
    return async_session()
