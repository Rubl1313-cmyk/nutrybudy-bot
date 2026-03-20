"""
Подключение к базе данных NutriBuddy.
Гарантирует создание недостающих колонок и приводит типы к BIGINT через синхронный SQL-запрос.
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
    logger.info("[DB] Используется PostgreSQL")
else:
    DATABASE_URL = "sqlite+aiosqlite:///nutribudy.db"
    logger.warning("[DB] Используется SQLite")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    poolclass=None if "sqlite" in DATABASE_URL else None,
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ===== КЛАСС DatabaseSession ПЕРЕМЕЩЁН СЮДА =====
class DatabaseSession:
    """Контекстный менеджер для работы с сессией БД"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        
        await self.session.close()
        self.session = None
# ==============================================

def get_session() -> DatabaseSession:
    """Получить сессию базы данных"""
    return DatabaseSession()

async def init_db():
    """Инициализация базы данных"""
    try:
        # Создаем таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("[DB] База данных инициализирована")
        
        # Проверяем и создаем недостающие колонки
        await ensure_columns_exist()
        
    except Exception as e:
        logger.error(f"[DB] Ошибка инициализации БД: {e}")
        raise

async def close_db():
    """Закрытие соединения с базой данных"""
    await engine.dispose()
    logger.info("[DB] Соединение с БД закрыто")

async def ensure_columns_exist():
    """Проверяет и создает недостающие колонки в таблице users"""
    try:
        # Список колонок для проверки и добавления
        columns_to_add = [
            ("daily_activity_goal", "INTEGER DEFAULT 300"),
            ("neck_cm", "FLOAT"),
            ("waist_cm", "FLOAT"),
            ("hip_cm", "FLOAT"),
            ("wrist_cm", "FLOAT"),
            ("bicep_cm", "FLOAT"),
            ("chest_cm", "FLOAT"),
            ("forearm_cm", "FLOAT"),
            ("calf_cm", "FLOAT"),
            ("shoulder_width_cm", "FLOAT"),
            ("hip_width_cm", "FLOAT"),
            ("goal_weight", "FLOAT"),
            ("last_bodyfat", "FLOAT"),
            ("last_muscle_mass", "FLOAT"),
            ("last_body_water", "FLOAT"),
            ("reminder_enabled", "BOOLEAN DEFAULT TRUE"),
            ("timezone", "VARCHAR(50) DEFAULT 'UTC'")
        ]
        
        async with engine.begin() as conn:
            # Получаем существующие колонки
            if "postgresql" in DATABASE_URL:
                result = await conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                """))
                existing_columns = {row[0] for row in result}
                is_sqlite = False
            else:  # SQLite
                result = await conn.execute(text("PRAGMA table_info(users)"))
                existing_columns = {row[1] for row in result}
                is_sqlite = True

            # Добавляем недостающие колонки
            for column_name, column_def in columns_to_add:
                if column_name not in existing_columns:
                    if is_sqlite:
                        await conn.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"))
                    else:
                        await conn.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {column_def}"))
                    logger.info(f"[DB] Добавлена колонка: {column_name}")
            
            # Обновляем типы telegram_id и user_id в BIGINT если нужно
            if "postgresql" in DATABASE_URL:
                # Проверяем текущие типы колонок
                result = await conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('telegram_id', 'user_id')
                """))
                
                for row in result:
                    column_name, current_type = row
                    if current_type != 'bigint' and column_name == 'telegram_id':
                        alter_sql = f"ALTER TABLE users ALTER COLUMN {column_name} TYPE BIGINT"
                        await conn.execute(text(alter_sql))
                        logger.info(f"[DB] Обновлен тип колонки {column_name} на BIGINT")
        
        logger.info("[DB] Проверка колонок завершена")
        
    except Exception as e:
        logger.error(f"[DB] Ошибка при проверке колонок: {e}")
        # Не прерываем работу, если не удалось добавить колонки

async def execute_raw_sql(query: str, params: dict = None):
    """Выполнить произвольный SQL-запрос"""
    try:
        async with engine.begin() as conn:
            if params:
                result = await conn.execute(text(query), params)
            else:
                result = await conn.execute(text(query))
            return result
    except Exception as e:
        logger.error(f"[DB] Ошибка выполнения SQL: {e}")
        raise

async def get_table_info(table_name: str) -> list:
    """Получить информацию о таблице"""
    try:
        async with engine.begin() as conn:
            if "postgresql" in DATABASE_URL:
                result = await conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """))
            else:  # SQLite
                result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
            
            return result.fetchall()
    except Exception as e:
        logger.error(f"[DB] Ошибка получения информации о таблице {table_name}: {e}")
        return []

async def check_database_health() -> dict:
    """Проверить здоровье базы данных"""
    try:
        health_info = {
            'connected': True,
            'tables': {},
            'errors': []
        }
        
        async with engine.begin() as conn:
            # Проверяем основные таблицы
            tables = ['users', 'food_entries', 'water_entries', 'drink_entries', 
                     'weight_entries', 'activity_entries', 'achievements']
            
            for table in tables:
                try:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    health_info['tables'][table] = {
                        'exists': True,
                        'rows': count
                    }
                except Exception as e:
                    health_info['tables'][table] = {
                        'exists': False,
                        'error': str(e)
                    }
                    health_info['errors'].append(f"Таблица {table}: {e}")
        
        return health_info
        
    except Exception as e:
        return {
            'connected': False,
            'error': str(e),
            'tables': {},
            'errors': [str(e)]
        }

async def backup_database(backup_path: str = None):
    """Создать резервную копию базы данных (только для SQLite)"""
    if "sqlite" not in DATABASE_URL:
        logger.warning("[DB] Бэкап доступен только для SQLite")
        return False
    
    try:
        import shutil
        from datetime import datetime
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"nutribudy_backup_{timestamp}.db"
        
        # Копируем файл базы данных
        shutil.copy2("nutribudy.db", backup_path)
        logger.info(f"[DB] Бэкап создан: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"[DB] Ошибка создания бэкапа: {e}")
        return False

async def vacuum_database():
    """Оптимизировать базу данных (только для SQLite)"""
    if "sqlite" not in DATABASE_URL:
        logger.warning("[DB] VACUUM доступен только для SQLite")
        return False
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text("VACUUM"))
        logger.info("[DB] База данных оптимизирована")
        return True
        
    except Exception as e:
        logger.error(f"[DB] Ошибка оптимизации БД: {e}")
        return False

async def get_database_stats() -> dict:
    """Получить статистику базы данных"""
    try:
        stats = {
            'total_users': 0,
            'total_food_entries': 0,
            'total_water_entries': 0,
            'total_weight_entries': 0,
            'total_activity_entries': 0,
            'database_size': 0
        }
        
        async with engine.begin() as conn:
            # Получаем количество записей в каждой таблице
            tables_stats = {
                'users': 'total_users',
                'food_entries': 'total_food_entries',
                'water_entries': 'total_water_entries',
                'weight_entries': 'total_weight_entries',
                'activity_entries': 'total_activity_entries'
            }
            
            for table, stat_key in tables_stats.items():
                try:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    stats[stat_key] = result.scalar()
                except:
                    stats[stat_key] = 0
            
            # Размер базы данных (только для SQLite)
            if "sqlite" in DATABASE_URL:
                try:
                    import os
                    stats['database_size'] = os.path.getsize("nutribudy.db")
                except:
                    stats['database_size'] = 0
        
        return stats
        
    except Exception as e:
        logger.error(f"[DB] Ошибка получения статистики: {e}")
        return {}

# Функции для работы с транзакциями

async def transaction_rollback():
    """Откат транзакций"""
    try:
        async with engine.begin() as conn:
            await conn.rollback()
        logger.info("[DB] Транзакция отменена")
    except Exception as e:
        logger.error(f"[DB] Ошибка отката транзакции: {e}")

# Контекстный менеджер для безопасной работы с БД
# Класс DatabaseSession перемещен наверх для корректной работы get_session()

# Утилитарные функции

async def test_connection():
    """Тест подключения к базе данных"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("[DB] Тест подключения прошел успешно")
        return True
    except Exception as e:
        logger.error(f"[DB] Тест подключения не удался: {e}")
        return False

# Экспорт основных компонентов
__all__ = [
    'Base',
    'engine',
    'get_session',
    'init_db',
    'close_db',
    'ensure_columns_exist',
    'execute_raw_sql',
    'get_table_info',
    'check_database_health',
    'backup_database',
    'vacuum_database',
    'get_database_stats',
    'DatabaseSession',
    'test_connection'
]
