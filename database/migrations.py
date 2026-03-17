"""
Система миграций базы данных для NutriBuddy Bot
"""
import logging
from typing import List, Dict, Any
import sqlalchemy
from .migration_add_timezone import add_timezone_column
import text, inspect
import re
from database.db import get_session
from database.models import Base
from database.gamification_models import Base as GamificationBase

logger = logging.getLogger(__name__)

class Migration:
    """Класс миграции"""
    def __init__(self, version: str, description: str, up_sql: str = None, down_sql: str = None):
        self.version = version
        self.description = description
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.applied_at = None

class MigrationManager:
    """Менеджер миграций"""
    
    def __init__(self):
        self.migrations: List[Migration] = []
        self._init_migrations()
    
    def _init_migrations(self):
        """Инициализация списка миграций"""
        # Версия 1.0: Начальная схема
        self.migrations.append(Migration(
            "1.0.0",
            "Initial database schema",
            None,  # Создается через Base.metadata.create_all()
            None
        ))
        
        # Версия 1.1.0: Добавление геймификации
        self.migrations.append(Migration(
            "1.1.0",
            "Add gamification tables",
            """
            -- Таблица достижений пользователей
            CREATE TABLE IF NOT EXISTS user_achievements (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                achievement_id VARCHAR(50) NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                points INTEGER NOT NULL
            );

            -- Таблица статистики геймификации
            CREATE TABLE IF NOT EXISTS user_gamification (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
                total_points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                current_streak INTEGER DEFAULT 0,
                max_streak INTEGER DEFAULT 0,
                meals_logged INTEGER DEFAULT 0,
                water_ml_total INTEGER DEFAULT 0,
                start_weight FLOAT,
                current_weight FLOAT,
                last_activity_date TIMESTAMP,
                early_breakfasts INTEGER DEFAULT 0,
                late_dinners INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Таблица истории достижений
            CREATE TABLE IF NOT EXISTS achievement_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                achievement_id VARCHAR(50) NOT NULL,
                achievement_name VARCHAR(100) NOT NULL,
                achievement_description VARCHAR(255) NOT NULL,
                points_earned INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Индексы для производительности
            CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_gamification_user_id ON user_gamification(user_id);
            CREATE INDEX IF NOT EXISTS idx_achievement_history_user_id ON achievement_history(user_id);
            """,
            None  # down_sql (можно оставить как есть или тоже упростить)
        ))
        
        # Версия 1.2: Добавление полей антропометрии
        self.migrations.append(Migration(
            "1.2.0",
            "Add anthropometry fields to users table",
            """
            -- Добавляем поля антропометрии если их нет (PostgreSQL)
            ALTER TABLE users ADD COLUMN IF NOT EXISTS neck_cm FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS waist_cm FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS hip_cm FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS wrist_cm FLOAT;
            
            -- Добавляем поля композиции тела
            ALTER TABLE users ADD COLUMN IF NOT EXISTS last_bodyfat FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS last_muscle_mass FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS last_body_water FLOAT;
            """,
            """
            -- Удаление полей антропометрии (если понадобится откат)
            ALTER TABLE users DROP COLUMN IF EXISTS neck_cm;
            ALTER TABLE users DROP COLUMN IF EXISTS waist_cm;
            ALTER TABLE users DROP COLUMN IF EXISTS hip_cm;
            ALTER TABLE users DROP COLUMN IF EXISTS wrist_cm;
            ALTER TABLE users DROP COLUMN IF EXISTS last_bodyfat;
            ALTER TABLE users DROP COLUMN IF EXISTS last_muscle_mass;
            ALTER TABLE users DROP COLUMN IF EXISTS last_body_water;
            """
        ))
        
        # Версия 1.3.0: Создание отдельной таблицы для воды
        self.migrations.append(Migration(
            "1.3.0",
            "Create separate water_entries table",
            """
            -- Создаем отдельную таблицу для записей о воде
            CREATE TABLE IF NOT EXISTS water_entries (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                volume_ml FLOAT NOT NULL,
                datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Индекс для производительности
            CREATE INDEX IF NOT EXISTS idx_water_entries_user_id ON water_entries(user_id);
            CREATE INDEX IF NOT EXISTS idx_water_entries_datetime ON water_entries(datetime);
            """,
            """
            -- Удаление таблицы water_entries (если понадобится откат)
            DROP TABLE IF EXISTS water_entries;
            """
        ))
        
        # Версия 1.4.0: Миграция на единую таблицу DrinkEntry
        self.migrations.append(Migration(
            "1.4.0",
            "Migrate to unified DrinkEntry table",
            """
-- Добавляем поля source и reference_id в drink_entries (PostgreSQL)
-- Для SQLite эти поля будут добавлены через init_db()

-- Проверяем существование таблицы water_entries перед миграцией
-- Это предотвратит ошибку при повторном применении миграции
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'water_entries') THEN
        INSERT INTO drink_entries (user_id, name, volume_ml, calories, source, datetime)
        SELECT user_id, 'вода', volume_ml, 0.0, 'drink', datetime
        FROM water_entries
        WHERE NOT EXISTS (
            SELECT 1 FROM drink_entries 
            WHERE drink_entries.user_id = water_entries.user_id 
            AND drink_entries.datetime = water_entries.datetime
            AND drink_entries.name = 'вода'
        );
        
        -- Удаляем таблицу water_entries
        DROP TABLE water_entries;
    END IF;
END $$;
""",
            """
-- Откат миграции (если понадобится)
-- Создаем таблицу water_entries
CREATE TABLE water_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    volume_ml FLOAT NOT NULL,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Переносим данные обратно
INSERT INTO water_entries (user_id, volume_ml, datetime)
SELECT user_id, volume_ml, datetime
FROM drink_entries
WHERE name = 'вода' AND source = 'drink';

-- Удаляем поля из drink_entries
ALTER TABLE drink_entries DROP COLUMN IF EXISTS source;
ALTER TABLE drink_entries DROP COLUMN IF EXISTS reference_id;
            """
        ))
        
        # Версия 1.5.0: Добавление поля бицепса для мужчин
        self.migrations.append(Migration(
            "1.5.0",
            "Add bicep_cm field for male anthropometry",
            """
            -- Добавляем поле бицепса если его нет
            ALTER TABLE users ADD COLUMN IF NOT EXISTS bicep_cm FLOAT;
            """,
            """
            -- Удаление поля бицепса (если понадобится откат)
            ALTER TABLE users DROP COLUMN IF EXISTS bicep_cm;
            """
        ))
        
        # Версия 1.6.0: Добавление поля goal_weight
        self.migrations.append(Migration(
            "1.6.0",
            "Add goal_weight field for target weight tracking",
            """
            -- Добавляем поле целевого веса если его нет
            ALTER TABLE users ADD COLUMN IF NOT EXISTS goal_weight FLOAT;
            """,
            """
            -- Удаление поля целевого веса (если понадобится откат)
            ALTER TABLE users DROP COLUMN IF EXISTS goal_weight;
            """
        ))
        
        # Версия 1.8.0: Добавление часового пояса
        self.migrations.append(Migration(
            "1.8.0",
            "Add timezone field for user timezone tracking",
            add_timezone_column(),
            """
            -- Удаление поля timezone (если понадобится откат)
            ALTER TABLE users DROP COLUMN IF EXISTS timezone;
            """
        ))
        
        # Версия 1.7.0: Расширенная антропометрия (только обхваты)
        self.migrations.append(Migration(
            "1.7.0",
            "Add advanced anthropometry fields (girths only)",
            """
            -- Добавляем новые антропометрические поля
            ALTER TABLE users ADD COLUMN IF NOT EXISTS chest_cm FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS forearm_cm FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS calf_cm FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS shoulder_width_cm FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS hip_width_cm FLOAT;
            """,
            """
            -- Удаление полей (если понадобится откат)
            ALTER TABLE users DROP COLUMN IF EXISTS chest_cm;
            ALTER TABLE users DROP COLUMN IF EXISTS forearm_cm;
            ALTER TABLE users DROP COLUMN IF EXISTS calf_cm;
            ALTER TABLE users DROP COLUMN IF EXISTS shoulder_width_cm;
            ALTER TABLE users DROP COLUMN IF EXISTS hip_width_cm;
            """
        ))
    
    async def get_applied_migrations(self) -> List[str]:
        """Получение списка примененных миграций"""
        async with get_session() as session:
            # Создаем таблицу миграций если нет
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(20) PRIMARY KEY,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await session.commit()
            
            # Получаем примененные миграции
            result = await session.execute(text("SELECT version FROM schema_migrations ORDER BY version"))
            return [row[0] for row in result.fetchall()]
    
    async def apply_migration(self, migration: Migration):
        """Применение миграции с поддержкой PostgreSQL и SQLite"""
        logger.info(f"Applying migration {migration.version}: {migration.description}")
        
        async with get_session() as session:
            try:
                if migration.up_sql:
                    # Определяем тип базы данных
                    is_sqlite = "sqlite" in str(session.bind.url)
                    
                    # Разделяем по точке с запятой, фильтруем пустые строки и комментарии
                    commands = []
                    for cmd in migration.up_sql.split(';'):
                        cmd = cmd.strip()
                        if cmd and not cmd.startswith('--'):
                            # Для SQLite заменяем несовместимые команды
                            if is_sqlite:
                                if "CREATE INDEX IF NOT EXISTS" in cmd:
                                    # Для SQLite проверяем существование таблицы и индекса
                                    index_name = cmd.split("CREATE INDEX IF NOT EXISTS ")[1].split(" ")[0]
                                    table_name = cmd.split("ON ")[1].split("(")[0].strip()
                                    
                                    # Проверяем существование таблицы
                                    table_check = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
                                    table_result = await session.execute(text(table_check))
                                    
                                    if table_result.fetchone():
                                        # Проверяем существование индекса
                                        check_cmd = f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}'"
                                        result = await session.execute(text(check_cmd))
                                        if not result.fetchone():
                                            # Создаем индекс без IF NOT EXISTS
                                            sqlite_cmd = cmd.replace("CREATE INDEX IF NOT EXISTS", "CREATE INDEX")
                                            commands.append(sqlite_cmd)  # Добавляем команду
                                        else:
                                            logger.info(f"Index {index_name} already exists, skipping")
                                    else:
                                        logger.info(f"Table {table_name} does not exist, skipping index {index_name}")
                                        continue
                                elif "ALTER TABLE" in cmd and "IF NOT EXISTS" in cmd:
                                    # Пропускаем миграции с IF NOT EXISTS для SQLite
                                    logger.info(f"Skipping SQLite-incompatible command: {cmd}")
                                    continue
                                elif "DO $$" in cmd or "END $$" in cmd or "END IF" in cmd or ("BEGIN" in cmd and "IF" in cmd):
                                    # Пропускаем PostgreSQL-specific блоки для SQLite
                                    logger.info(f"Skipping PostgreSQL-specific block: {cmd[:50]}...")
                                    continue
                                else:
                                    commands.append(cmd)
                            else:
                                commands.append(cmd)
                    
                    logger.info(f"Executing {len(commands)} SQL commands for migration {migration.version}")
                    
                    for i, cmd in enumerate(commands, 1):
                        if cmd:  # Дополнительная проверка
                            try:
                                logger.info(f"Command {i}: {cmd}")
                                await session.execute(text(cmd))
                            except Exception as cmd_error:
                                # Проверяем, не ошибка дублирования колонки
                                error_str = str(cmd_error).lower()
                                if "already exists" in error_str or "duplicate column" in error_str:
                                    logger.warning(f"Column already exists in command {i}: {cmd_error}")
                                    continue  # Пропускаем эту команду
                                else:
                                    logger.error(f"Error in command {i}: {cmd}")
                                    logger.error(f"Error details: {cmd_error}")
                                    raise cmd_error  # Пробрасываем другие ошибки
                
                # Записываем миграцию как примененную
                await session.execute(text("""
                    INSERT INTO schema_migrations (version, description, applied_at)
                    VALUES (:version, :description, :applied_at)
                    ON CONFLICT (version) DO NOTHING
                """), {
                    'version': migration.version,
                    'description': migration.description,
                    'applied_at': datetime.now()
                })
                
                await session.commit()
                migration.applied_at = datetime.now()
                logger.info(f"Migration {migration.version} applied successfully")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to apply migration {migration.version}: {e}")
                logger.error(f"SQL that failed: {migration.up_sql}")
                raise
    
    async def migrate(self):
        """Выполнение всех необходимых миграций"""
        applied = await self.get_applied_migrations()
        logger.info(f"Applied migrations: {applied}")
        
        for migration in self.migrations:
            if migration.version not in applied:
                await self.apply_migration(migration)
            else:
                logger.info(f"Migration {migration.version} already applied")
        
        logger.info("All migrations applied successfully")
    
    async def create_initial_schema(self):
        """Создание начальной схемы БД"""
        logger.info("Creating initial database schema...")
        
        async with get_session() as session:
            try:
                # Создаем все таблицы из моделей
                await session.run_sync(Base.metadata.create_all)
                await session.run_sync(GamificationBase.metadata.create_all)
                
                # Записываем начальную миграцию
                await session.execute(text("""
                    INSERT INTO schema_migrations (version, description, applied_at)
                    VALUES ('1.0.0', 'Initial database schema', :applied_at)
                    ON CONFLICT (version) DO NOTHING
                """), {'applied_at': datetime.now()})
                
                await session.commit()
                logger.info("Initial schema created successfully")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to create initial schema: {e}")
                raise

# Глобальный менеджер миграций
migration_manager = MigrationManager()

async def run_migrations():
    """Запуск миграций при старте приложения"""
    try:
        await migration_manager.migrate()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise
