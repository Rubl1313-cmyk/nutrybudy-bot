"""
Система миграций базы данных для NutriBuddy Bot
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import text, inspect
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
        
        # Версия 1.1: Добавление геймификации
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
            """
            DROP TABLE IF EXISTS achievement_history;
            DROP TABLE IF EXISTS user_gamification;
            DROP TABLE IF EXISTS user_achievements;
            """
        ))
        
        # Версия 1.2: Добавление полей антропометрии
        self.migrations.append(Migration(
            "1.2.0",
            "Add anthropometry fields to users table",
            """
            -- Добавляем поля антропометрии если их нет
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
        
        # Версия 1.3: Исправление поля amount в water_entries
        self.migrations.append(Migration(
            "1.3.0",
            "Fix water_entries amount field",
            """
            -- Проверяем и исправляем поле amount
            DO $$
            BEGIN
                -- Если есть колонка amount_ml, переименовываем ее
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'water_entries' AND column_name = 'amount_ml'
                ) THEN
                    ALTER TABLE water_entries RENAME COLUMN amount_ml TO amount;
                END IF;
                
                -- Убедимся что колонка существует
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'water_entries' AND column_name = 'amount'
                ) THEN
                    ALTER TABLE water_entries ADD COLUMN amount FLOAT;
                END IF;
            END $$;
            """,
            """
            ALTER TABLE water_entries RENAME COLUMN amount TO amount_ml;
            """
        ))
        
        # Версия 1.4: Добавление поля бицепса для мужчин
        self.migrations.append(Migration(
            "1.4.0",
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
        """Применение миграции с поддержкой asyncpg"""
        logger.info(f"Applying migration {migration.version}: {migration.description}")
        
        async with get_session() as session:
            try:
                if migration.up_sql:
                    # Разделяем SQL на отдельные операторы для asyncpg
                    statements = re.split(r';\s*\n', migration.up_sql)
                    
                    for stmt in statements:
                        stmt = stmt.strip()
                        # Пропускаем пустые строки и комментарии
                        if stmt and not stmt.startswith('--'):
                            logger.debug(f"Executing SQL: {stmt[:100]}...")
                            await session.execute(text(stmt))
                
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
                Base.metadata.create_all(bind=session.bind)
                GamificationBase.metadata.create_all(bind=session.bind)
                
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
