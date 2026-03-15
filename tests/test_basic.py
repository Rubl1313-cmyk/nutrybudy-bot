"""
Базовые тесты для NutriBuddy Bot
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Тесты утилит
class TestSafeParser:
    """Тесты безопасного парсинга"""
    
    def test_safe_parse_float_valid(self):
        from utils.safe_parser import safe_parse_float
        
        # Тест корректных значений
        assert safe_parse_float("70.5", "вес") == (70.5, None)
        assert safe_parse_float("70", "вес") == (70.0, None)
        assert safe_parse_float("70 кг", "вес") == (70.0, None)
        assert safe_parse_float("70.5 кг", "вес") == (70.5, None)
    
    def test_safe_parse_float_invalid(self):
        from utils.safe_parser import safe_parse_float
        
        # Тест некорректных значений
        value, error = safe_parse_float("abc", "вес")
        assert error is not None
        assert "Введите число" in error
        
        value, error = safe_parse_float("-5", "вес")
        assert error is not None
        assert "минимальное значение" in error
    
    def test_safe_parse_int_valid(self):
        from utils.safe_parser import safe_parse_int
        
        # Тест корректных значений
        assert safe_parse_int("25", "возраст") == (25, None)
        assert safe_parse_int("25 лет", "возраст") == (25, None)
    
    def test_safe_parse_int_invalid(self):
        from utils.safe_parser import safe_parse_int
        
        # Тест некорректных значений
        value, error = safe_parse_int("abc", "возраст")
        assert error is not None

class TestRateLimiter:
    """Тесты rate limiting"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_basic(self):
        from utils.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_requests=2, time_window=60)
        
        # Первые два запроса должны пройти
        assert await limiter.is_allowed("user1") == True
        assert await limiter.is_allowed("user1") == True
        
        # Третий запрос должен быть заблокирован
        assert await limiter.is_allowed("user1") == False
    
    @pytest.mark.asyncio
    async def test_user_rate_limiter(self):
        from utils.rate_limiter import UserRateLimiter
        
        with patch.dict('os.environ', {
            'RATE_LIMIT_AI_REQUESTS': '3',
            'RATE_LIMIT_AI_WINDOW': '60'
        }):
            limiter = UserRateLimiter()
            
            # Проверяем, что лимиты настроены правильно
            assert limiter.limits['ai_requests'].max_requests == 3
            
            # Тестируем лимит
            user_id = 12345
            for i in range(3):
                assert await limiter.is_allowed(user_id, 'ai_requests') == True
            
            # Четвертый запрос должен быть заблокирован
            assert await limiter.is_allowed(user_id, 'ai_requests') == False

class TestGamification:
    """Тесты системы геймификации"""
    
    @pytest.mark.asyncio
    async def test_first_achievement(self):
        from utils.gamification import gamification, AchievementType
        
        # Мокаем БД
        with patch('utils.gamification.get_session') as mock_session:
            mock_session.return_value.__aenter__.return_value = Mock()
            mock_session.return_value.__aexit__.return_value = None
            
            # Проверяем получение первого достижения
            achievements = await gamification.check_achievements(
                user_id=123,
                event_type="meal_logged",
                data={"time": datetime.now(), "meal_type": "breakfast"}
            )
            
            # Должно быть получено достижение "first_meal"
            first_meal = [a for a in achievements if a.id == "first_meal"]
            assert len(first_meal) == 1
    
    def test_achievement_conditions(self):
        from utils.gamification import Achievement, AchievementType
        
        # Создаем тестовое достижение
        achievement = Achievement(
            "test", AchievementType.FIRST_MEAL,
            "Test", "Test description",
            "🧪", 10, {"count": 1}
        )
        
        # Проверяем условие
        progress = Mock()
        progress.meals_logged = 1
        
        condition_met = gamification._check_achievement_condition(
            achievement, progress, {}
        )
        assert condition_met == True

class TestLocalizedCommands:
    """Тесты локализованных команд"""
    
    def test_command_mapping(self):
        from utils.localized_commands import get_command_mapping
        
        mapping = get_command_mapping()
        
        # Проверяем основные команды
        assert mapping["достижения"] == "achievements"
        assert mapping["прогресс"] == "progress"
        assert mapping["профиль"] == "profile"
    
    def test_localized_help(self):
        from utils.localized_commands import get_localized_help
        
        help_text = get_localized_help()
        
        # Проверяем, что справка содержит команды
        assert "/достижения" in help_text
        assert "/прогресс" in help_text
        assert "/профиль" in help_text
        assert "русские, так и английские" in help_text

class TestMigrations:
    """Тесты системы миграций"""
    
    @pytest.mark.asyncio
    async def test_migration_manager_init(self):
        from database.migrations import MigrationManager
        
        manager = MigrationManager()
        
        # Проверяем, что миграции инициализированы
        assert len(manager.migrations) > 0
        
        # Проверяем версии
        versions = [m.version for m in manager.migrations]
        assert "1.0.0" in versions
        assert "1.4.0" in versions
    
    def test_migration_structure(self):
        from database.migrations import Migration
        
        migration = Migration(
            "1.0.0", "Test migration", 
            "CREATE TABLE test (id INTEGER);",
            "DROP TABLE test;"
        )
        
        assert migration.version == "1.0.0"
        assert migration.description == "Test migration"
        assert migration.up_sql == "CREATE TABLE test (id INTEGER);"
        assert migration.down_sql == "DROP TABLE test;"

# Тесты интеграции
class TestIntegration:
    """Интеграционные тесты"""
    
    @pytest.mark.asyncio
    async def test_profile_creation_flow(self):
        """Тест полного потока создания профиля"""
        # Этот тест требует мокирования FSM и БД
        # Для примера показана структура
        pass
    
    @pytest.mark.asyncio 
    async def test_food_logging_flow(self):
        """Тест потока записи еды"""
        # Этот тест требует мокирования AI и БД
        pass

# Функция для запуска всех тестов
async def run_all_tests():
    """Запустить все тесты"""
    print("🧪 Запуск тестов NutriBuddy Bot...")
    
    try:
        # Запускаем pytest
        import subprocess
        result = subprocess.run([
            "python", "-m", "pytest", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Все тесты пройдены!")
            print(result.stdout)
        else:
            print("❌ Некоторые тесты не пройдены:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
