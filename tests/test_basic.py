"""
Ğ‘Ğ°Ğ·Ğ¾Ğ²Ñ‹Ğµ Ñ‚ĞµÑ�Ñ‚Ñ‹ Ğ´Ğ»Ñ� NutriBuddy Bot
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Ğ¢ĞµÑ�Ñ‚Ñ‹ ÑƒÑ‚Ğ¸Ğ»Ğ¸Ñ‚
class TestSafeParser:
    """Ğ¢ĞµÑ�Ñ‚Ñ‹ Ğ±ĞµĞ·Ğ¾Ğ¿Ğ°Ñ�Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ°"""
    
    def test_safe_parse_float_valid(self):
        from utils.safe_parser import safe_parse_float
        
        # Ğ¢ĞµÑ�Ñ‚ ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ñ‹Ñ… Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğ¹
        assert safe_parse_float("70.5", "Ğ²ĞµÑ�") == (70.5, None)
        assert safe_parse_float("70", "Ğ²ĞµÑ�") == (70.0, None)
        assert safe_parse_float("70 ĞºĞ³", "Ğ²ĞµÑ�") == (70.0, None)
        assert safe_parse_float("70.5 ĞºĞ³", "Ğ²ĞµÑ�") == (70.5, None)
    
    def test_safe_parse_float_invalid(self):
        from utils.safe_parser import safe_parse_float
        
        # Ğ¢ĞµÑ�Ñ‚ Ğ½ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ñ‹Ñ… Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğ¹
        value, error = safe_parse_float("abc", "Ğ²ĞµÑ�")
        assert error is not None
        assert "Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ñ‡Ğ¸Ñ�Ğ»Ğ¾" in error
        
        value, error = safe_parse_float("-5", "Ğ²ĞµÑ�")
        assert error is not None
        assert "Ğ¼Ğ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ" in error
    
    def test_safe_parse_int_valid(self):
        from utils.safe_parser import safe_parse_int
        
        # Ğ¢ĞµÑ�Ñ‚ ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ñ‹Ñ… Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğ¹
        assert safe_parse_int("25", "Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚") == (25, None)
        assert safe_parse_int("25 Ğ»ĞµÑ‚", "Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚") == (25, None)
    
    def test_safe_parse_int_invalid(self):
        from utils.safe_parser import safe_parse_int
        
        # Ğ¢ĞµÑ�Ñ‚ Ğ½ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ñ‹Ñ… Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğ¹
        value, error = safe_parse_int("abc", "Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚")
        assert error is not None

class TestRateLimiter:
    """Ğ¢ĞµÑ�Ñ‚Ñ‹ rate limiting"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_basic(self):
        from utils.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_requests=2, time_window=60)
        
        # ĞŸĞµÑ€Ğ²Ñ‹Ğµ Ğ´Ğ²Ğ° Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ° Ğ´Ğ¾Ğ»Ğ¶Ğ½Ñ‹ Ğ¿Ñ€Ğ¾Ğ¹Ñ‚Ğ¸
        assert await limiter.is_allowed("user1") == True
        assert await limiter.is_allowed("user1") == True
        
        # Ğ¢Ñ€ĞµÑ‚Ğ¸Ğ¹ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ·Ğ°Ğ±Ğ»Ğ¾ĞºĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½
        assert await limiter.is_allowed("user1") == False
    
    @pytest.mark.asyncio
    async def test_user_rate_limiter(self):
        from utils.rate_limiter import UserRateLimiter
        
        with patch.dict('os.environ', {
            'RATE_LIMIT_AI_REQUESTS': '3',
            'RATE_LIMIT_AI_WINDOW': '60'
        }):
            limiter = UserRateLimiter()
            
            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼, Ñ‡Ñ‚Ğ¾ Ğ»Ğ¸Ğ¼Ğ¸Ñ‚Ñ‹ Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾ĞµĞ½Ñ‹ Ğ¿Ñ€Ğ°Ğ²Ğ¸Ğ»ÑŒĞ½Ğ¾
            assert limiter.limits['ai_requests'].max_requests == 3
            
            # Ğ¢ĞµÑ�Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ»Ğ¸Ğ¼Ğ¸Ñ‚
            user_id = 12345
            for i in range(3):
                assert await limiter.is_allowed(user_id, 'ai_requests') == True
            
            # Ğ§ĞµÑ‚Ğ²ĞµÑ€Ñ‚Ñ‹Ğ¹ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ·Ğ°Ğ±Ğ»Ğ¾ĞºĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½
            assert await limiter.is_allowed(user_id, 'ai_requests') == False

class TestGamification:
    """Ğ¢ĞµÑ�Ñ‚Ñ‹ Ñ�Ğ¸Ñ�Ñ‚ĞµĞ¼Ñ‹ Ğ³ĞµĞ¹Ğ¼Ğ¸Ñ„Ğ¸ĞºĞ°Ñ†Ğ¸Ğ¸"""
    
    @pytest.mark.asyncio
    async def test_first_achievement(self):
        from utils.gamification import gamification, AchievementType
        
        # ĞœĞ¾ĞºĞ°ĞµĞ¼ Ğ‘Ğ”
        with patch('utils.gamification.get_session') as mock_session:
            mock_session.return_value.__aenter__.return_value = Mock()
            mock_session.return_value.__aexit__.return_value = None
            
            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğµ Ğ¿ĞµÑ€Ğ²Ğ¾Ğ³Ğ¾ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�
            achievements = await gamification.check_achievements(
                user_id=123,
                event_type="meal_logged",
                data={"time": datetime.now(), "meal_type": "breakfast"}
            )
            
            # Ğ”Ğ¾Ğ»Ğ¶Ğ½Ğ¾ Ğ±Ñ‹Ñ‚ÑŒ Ğ¿Ğ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¾ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğµ "first_meal"
            first_meal = [a for a in achievements if a.id == "first_meal"]
            assert len(first_meal) == 1
    
    def test_achievement_conditions(self):
        from utils.gamification import Achievement, AchievementType
        
        # Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ñ‚ĞµÑ�Ñ‚Ğ¾Ğ²Ğ¾Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğµ
        achievement = Achievement(
            "test", AchievementType.FIRST_MEAL,
            "Test", "Test description",
            "ğŸ§ª", 10, {"count": 1}
        )
        
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ ÑƒÑ�Ğ»Ğ¾Ğ²Ğ¸Ğµ
        progress = Mock()
        progress.meals_logged = 1
        
        condition_met = gamification._check_achievement_condition(
            achievement, progress, {}
        )
        assert condition_met == True

class TestLocalizedCommands:
    """Ğ¢ĞµÑ�Ñ‚Ñ‹ Ğ»Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ñ… ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´"""
    
    def test_command_mapping(self):
        from utils.localized_commands import get_command_mapping
        
        mapping = get_command_mapping()
        
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ğµ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹
        assert mapping["Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�"] == "achievements"
        assert mapping["Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�"] == "progress"
        assert mapping["Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"] == "profile"
    
    def test_localized_help(self):
        from utils.localized_commands import get_localized_help
        
        help_text = get_localized_help()
        
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼, Ñ‡Ñ‚Ğ¾ Ñ�Ğ¿Ñ€Ğ°Ğ²ĞºĞ° Ñ�Ğ¾Ğ´ĞµÑ€Ğ¶Ğ¸Ñ‚ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹
        assert "/Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�" in help_text
        assert "/Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�" in help_text
        assert "/Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ" in help_text
        assert "Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğµ, Ñ‚Ğ°Ğº Ğ¸ Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğµ" in help_text

class TestMigrations:
    """Ğ¢ĞµÑ�Ñ‚Ñ‹ Ñ�Ğ¸Ñ�Ñ‚ĞµĞ¼Ñ‹ Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ğ¹"""
    
    @pytest.mark.asyncio
    async def test_migration_manager_init(self):
        from database.migrations import MigrationManager
        
        manager = MigrationManager()
        
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼, Ñ‡Ñ‚Ğ¾ Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ğ¸ Ğ¸Ğ½Ğ¸Ñ†Ğ¸Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ñ‹
        assert len(manager.migrations) > 0
        
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ²ĞµÑ€Ñ�Ğ¸Ğ¸
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

# Ğ¢ĞµÑ�Ñ‚Ñ‹ Ğ¸Ğ½Ñ‚ĞµĞ³Ñ€Ğ°Ñ†Ğ¸Ğ¸
class TestIntegration:
    """Ğ˜Ğ½Ñ‚ĞµĞ³Ñ€Ğ°Ñ†Ğ¸Ğ¾Ğ½Ğ½Ñ‹Ğµ Ñ‚ĞµÑ�Ñ‚Ñ‹"""
    
    @pytest.mark.asyncio
    async def test_profile_creation_flow(self):
        """Ğ¢ĞµÑ�Ñ‚ Ğ¿Ğ¾Ğ»Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ğ¾Ñ‚Ğ¾ĞºĞ° Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ½Ğ¸Ñ� Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�"""
        # Ğ­Ñ‚Ğ¾Ñ‚ Ñ‚ĞµÑ�Ñ‚ Ñ‚Ñ€ĞµĞ±ÑƒĞµÑ‚ Ğ¼Ğ¾ĞºĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ� FSM Ğ¸ Ğ‘Ğ”
        # Ğ”Ğ»Ñ� Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€Ğ° Ğ¿Ğ¾ĞºĞ°Ğ·Ğ°Ğ½Ğ° Ñ�Ñ‚Ñ€ÑƒĞºÑ‚ÑƒÑ€Ğ°
        pass
    
    @pytest.mark.asyncio 
    async def test_food_logging_flow(self):
        """Ğ¢ĞµÑ�Ñ‚ Ğ¿Ğ¾Ñ‚Ğ¾ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ ĞµĞ´Ñ‹"""
        # Ğ­Ñ‚Ğ¾Ñ‚ Ñ‚ĞµÑ�Ñ‚ Ñ‚Ñ€ĞµĞ±ÑƒĞµÑ‚ Ğ¼Ğ¾ĞºĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ� AI Ğ¸ Ğ‘Ğ”
        pass

# Ğ¤ÑƒĞ½ĞºÑ†Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ·Ğ°Ğ¿ÑƒÑ�ĞºĞ° Ğ²Ñ�ĞµÑ… Ñ‚ĞµÑ�Ñ‚Ğ¾Ğ²
async def run_all_tests():
    """Ğ—Ğ°Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ Ğ²Ñ�Ğµ Ñ‚ĞµÑ�Ñ‚Ñ‹"""
    print("ğŸ§ª Ğ—Ğ°Ğ¿ÑƒÑ�Ğº Ñ‚ĞµÑ�Ñ‚Ğ¾Ğ² NutriBuddy Bot...")
    
    try:
        # Ğ—Ğ°Ğ¿ÑƒÑ�ĞºĞ°ĞµĞ¼ pytest
        import subprocess
        result = subprocess.run([
            "python", "-m", "pytest", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("âœ… Ğ’Ñ�Ğµ Ñ‚ĞµÑ�Ñ‚Ñ‹ Ğ¿Ñ€Ğ¾Ğ¹Ğ´ĞµĞ½Ñ‹!")
            print(result.stdout)
        else:
            print("â�Œ Ğ�ĞµĞºĞ¾Ñ‚Ğ¾Ñ€Ñ‹Ğµ Ñ‚ĞµÑ�Ñ‚Ñ‹ Ğ½Ğµ Ğ¿Ñ€Ğ¾Ğ¹Ğ´ĞµĞ½Ñ‹:")
            print(result.stderr)
            
    except Exception as e:
        print(f"â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ·Ğ°Ğ¿ÑƒÑ�ĞºĞ° Ñ‚ĞµÑ�Ñ‚Ğ¾Ğ²: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
