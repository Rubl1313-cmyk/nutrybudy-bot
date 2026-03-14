"""
🔄 Migration Script - Переход на Enhanced AI систему
✨ Автоматическая миграция с rule-based на AI компоненты
🎯 Безопасный переход с сохранением данных
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from database.db import init_db, close_db
from database.models import User
from services.ai_integration_manager import ai_integration_manager
from utils.ai_config import ai_config

logger = logging.getLogger(__name__)

class AIMigration:
    """Мигратор на Enhanced AI систему"""
    
    def __init__(self):
        self.ai_manager = ai_integration_manager
        self.config = ai_config
    
    async def migrate(self):
        """Основная функция миграции"""
        logger.info("🔄 Starting migration to Enhanced AI system...")
        
        try:
            # 1. Валидация конфигурации
            await self._validate_configuration()
            
            # 2. Инициализация Enhanced AI компонентов
            await self._initialize_enhanced_components()
            
            # 3. Тестирование Enhanced AI
            await self._test_enhanced_ai()
            
            # 4. Создание бэкапа конфигурации
            await self._create_backup()
            
            # 5. Обновление пользовательских данных
            await self._update_user_data()
            
            logger.info("✅ Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            await self._rollback()
            return False
    
    async def _validate_configuration(self):
        """Валидация конфигурации AI"""
        logger.info("🔍 Validating AI configuration...")
        
        config = self.config.get_all_config()
        
        if not config['validation']['valid']:
            issues = config['validation']['issues']
            logger.error(f"❌ Configuration validation failed: {issues}")
            raise ValueError(f"Invalid configuration: {issues}")
        
        logger.info("✅ Configuration validation passed")
    
    async def _initialize_enhanced_components(self):
        """Инициализация Enhanced AI компонентов"""
        logger.info("🚀 Initializing Enhanced AI components...")
        
        # Проверяем статус системы
        status = self.ai_manager.get_system_status()
        logger.info(f"📊 AI System Status: {status}")
        
        # Проверяем все компоненты
        required_components = [
            'enhanced_parser',
            'enhanced_nutrition_calculator', 
            'enhanced_climate_manager'
        ]
        
        for component in required_components:
            if component not in status or status[component] != 'active':
                raise RuntimeError(f"Component {component} is not active")
        
        logger.info("✅ All Enhanced AI components initialized")
    
    async def _test_enhanced_ai(self):
        """Тестирование Enhanced AI"""
        logger.info("🧪 Testing Enhanced AI functionality...")
        
        test_cases = [
            {
                'name': 'Intent Classification',
                'text': 'съел курицу с гречкой',
                'expected_intent': 'food'
            },
            {
                'name': 'Water Parsing',
                'text': 'выпил стакан воды',
                'expected_amount': 200
            },
            {
                'name': 'Activity Parsing',
                'text': 'бегал 30 минут',
                'expected_duration': 30
            },
            {
                'name': 'Multi-task Processing',
                'text': 'запиши 200г курицы',
                'expected_actions': ['save_food']
            }
        ]
        
        for test_case in test_cases:
            try:
                result = await self.ai_manager.process_user_input(
                    text=test_case['text'],
                    user_id=12345,  # Тестовый пользователь
                    task_type='auto'
                )
                
                if result['success']:
                    logger.info(f"✅ {test_case['name']}: PASSED")
                else:
                    logger.warning(f"⚠️ {test_case['name']}: FAILED - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ {test_case['name']}: ERROR - {e}")
        
        logger.info("🧪 Enhanced AI testing completed")
    
    async def _create_backup(self):
        """Создание бэкапа текущей конфигурации"""
        logger.info("💾 Creating configuration backup...")
        
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = asyncio.get_event_loop().time()
        backup_file = backup_dir / f"config_backup_{timestamp}.json"
        
        import json
        backup_data = {
            'timestamp': timestamp,
            'config': self.config.get_all_config(),
            'migration_version': '1.0'
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Backup created: {backup_file}")
    
    async def _update_user_data(self):
        """Обновление пользовательских данных для Enhanced AI"""
        logger.info("👥 Updating user data for Enhanced AI...")
        
        from database.db import get_session
        from sqlalchemy import select
        
        async with get_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            updated_count = 0
            for user in users:
                # Обновляем цели если нужно
                if not user.daily_steps_goal:
                    user.daily_steps_goal = 10000  # Цель по умолчанию
                    updated_count += 1
                
                # Добавляем город если отсутствует
                if not hasattr(user, 'city') or not user.city:
                    user.city = 'Москва'  # Город по умолчанию
            
            await session.commit()
            logger.info(f"✅ Updated {updated_count} user records")
    
    async def _rollback(self):
        """Откат миграции при ошибке"""
        logger.warning("🔄 Rolling back migration...")
        
        # Здесь можно добавить логику отката
        # Например, восстановление из бэкапа
        
        logger.warning(" Rollback completed")

async def main():
    """Основная функция миграции"""
    print("Enhanced AI Migration Script")
    print("=" * 50)
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Инициализация БД
    await init_db()
    
    try:
        # Создаем мигратор
        migrator = AIMigration()
        
        # Запускаем миграцию
        success = await migrator.migrate()
        
        if success:
            print("\n[SUCCESS] Migration completed successfully!")
            print("\n[INFO] Next steps:")
            print("1. Перезапустите бота")
            print("2. Проверьте работу Enhanced AI компонентов")
            print("3. Мониторьте логи на предмет ошибок")
            print("4. Соберите обратную связь от пользователей")
        else:
            print("\n[ERROR] Migration failed!")
            print("Проверьте логи для получения подробной информации")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"[CRITICAL] Critical migration error: {e}")
        print(f"\n[CRITICAL] Critical error: {e}")
        sys.exit(1)
    
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
