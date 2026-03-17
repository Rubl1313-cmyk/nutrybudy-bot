"""
Ğ¡Ğ¸Ñ�Ñ‚ĞµĞ¼Ğ° Ğ³ĞµĞ¹Ğ¼Ğ¸Ñ„Ğ¸ĞºĞ°Ñ†Ğ¸Ğ¸ Ğ¸ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹ Ğ´Ğ»Ñ� NutriBuddy Bot Ñ� Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸ĞµĞ¼ Ğ² Ğ‘Ğ”
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from database.db import get_session
from database.gamification_models import UserAchievement, UserGamification, AchievementHistory
from database.models import User
from sqlalchemy import select, func

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Ğ¢Ğ¸Ğ¿Ñ‹ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹"""
    FIRST_MEAL = "first_meal"
    WEEK_STREAK = "week_streak"
    MONTH_STREAK = "month_streak"
    CALORIE_GOAL = "calorie_goal"
    WATER_GOAL = "water_goal"
    WEIGHT_LOSS = "weight_loss"
    PERFECT_DAY = "perfect_day"
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"

class Achievement:
    """ĞšĞ»Ğ°Ñ�Ñ� Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�"""
    def __init__(self, id: str, type: AchievementType, name: str, description: str, 
                 icon: str, points: int, condition: Dict):
        self.id = id
        self.type = type
        self.name = name
        self.description = description
        self.icon = icon
        self.points = points
        self.condition = condition

class GamificationSystem:
    """Ğ¡Ğ¸Ñ�Ñ‚ĞµĞ¼Ğ° Ğ³ĞµĞ¹Ğ¼Ğ¸Ñ„Ğ¸ĞºĞ°Ñ†Ğ¸Ğ¸ Ñ� Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸ĞµĞ¼ Ğ² Ğ‘Ğ”"""
    
    def __init__(self):
        self.achievements = self._init_achievements()
    
    def _init_achievements(self) -> Dict[str, Achievement]:
        """Ğ˜Ğ½Ğ¸Ñ†Ğ¸Ğ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸Ñ� Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹"""
        achievements = {
            # Ğ•Ğ´Ğ°
            "first_meal": Achievement(
                "first_meal", AchievementType.FIRST_MEAL,
                "ĞŸĞµÑ€Ğ²Ñ‹Ğ¹ ÑˆĞ°Ğ³", "Ğ—Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ¿ĞµÑ€Ğ²Ñ‹Ğ¹ Ğ¿Ñ€Ğ¸ĞµĞ¼ Ğ¿Ğ¸Ñ‰Ğ¸",
                "ğŸ�½ï¸�", 10, {"count": 1}
            ),
            
            # Ğ¡ĞµÑ€Ğ¸Ğ¸ Ğ´Ğ½ĞµĞ¹
            "week_streak": Achievement(
                "week_streak", AchievementType.WEEK_STREAK,
                "Ğ�ĞµĞ´ĞµĞ»Ñ� Ğ´Ğ¸Ñ�Ñ†Ğ¸Ğ¿Ğ»Ğ¸Ğ½Ñ‹", "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°Ğ¹Ñ‚Ğµ ĞµĞ´Ñƒ 7 Ğ´Ğ½ĞµĞ¹ Ğ¿Ğ¾Ğ´Ñ€Ñ�Ğ´",
                "ğŸ”¥", 50, {"days": 7}
            ),
            
            "month_streak": Achievement(
                "month_streak", AchievementType.MONTH_STREAK,
                "ĞœĞµÑ�Ñ�Ñ† Ğ¼Ğ°Ñ�Ñ‚ĞµÑ€Ñ�Ñ‚Ğ²Ğ°", "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°Ğ¹Ñ‚Ğµ ĞµĞ´Ñƒ 30 Ğ´Ğ½ĞµĞ¹ Ğ¿Ğ¾Ğ´Ñ€Ñ�Ğ´",
                "ğŸ’�", 200, {"days": 30}
            ),
            
            # Ğ¦ĞµĞ»Ğ¸
            "calorie_goal": Achievement(
                "calorie_goal", AchievementType.CALORIE_GOAL,
                "ĞœĞ°Ñ�Ñ‚ĞµÑ€ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹", "Ğ’Ñ‹Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚Ğµ Ğ´Ğ½ĞµĞ²Ğ½ÑƒÑ� Ğ½Ğ¾Ñ€Ğ¼Ñƒ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹",
                "ğŸ�¯", 30, {"type": "daily_goal", "metric": "calories"}
            ),
            
            "water_goal": Achievement(
                "water_goal", AchievementType.WATER_GOAL,
                "Ğ“Ğ¸Ğ´Ñ€Ğ°Ñ‚Ğ°Ñ†Ğ¸Ñ�", "Ğ’Ñ‹Ğ¿ĞµĞ¹Ñ‚Ğµ Ğ´Ğ½ĞµĞ²Ğ½ÑƒÑ� Ğ½Ğ¾Ñ€Ğ¼Ñƒ Ğ²Ğ¾Ğ´Ñ‹",
                "ğŸ’§", 25, {"type": "daily_goal", "metric": "water"}
            ),
            
            # Ğ’ĞµÑ�
            "weight_loss_1kg": Achievement(
                "weight_loss_1kg", AchievementType.WEIGHT_LOSS,
                "ĞŸĞµÑ€Ğ²Ñ‹Ğ¹ ĞºĞ¸Ğ»Ğ¾Ğ³Ñ€Ğ°Ğ¼Ğ¼", "ĞŸĞ¾Ñ…ÑƒĞ´ĞµĞ¹Ñ‚Ğµ Ğ½Ğ° 1 ĞºĞ³",
                "âš–ï¸�", 40, {"kg": 1}
            ),
            
            "weight_loss_5kg": Achievement(
                "weight_loss_5kg", AchievementType.WEIGHT_LOSS,
                "Ğ—Ğ½Ğ°Ñ‡Ğ¸Ğ¼Ñ‹Ğ¹ Ñ€ĞµĞ·ÑƒĞ»ÑŒÑ‚Ğ°Ñ‚", "ĞŸĞ¾Ñ…ÑƒĞ´ĞµĞ¹Ñ‚Ğµ Ğ½Ğ° 5 ĞºĞ³",
                "ğŸ�†", 150, {"kg": 5}
            ),
            
            # Ğ˜Ğ´ĞµĞ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ´ĞµĞ½ÑŒ
            "perfect_day": Achievement(
                "perfect_day", AchievementType.PERFECT_DAY,
                "Ğ˜Ğ´ĞµĞ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ´ĞµĞ½ÑŒ", "Ğ’Ñ‹Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚Ğµ Ğ²Ñ�Ğµ Ñ†ĞµĞ»Ğ¸ Ğ·Ğ° Ğ´ĞµĞ½ÑŒ",
                "â­�", 75, {"type": "perfect_day"}
            ),
            
            # Ğ’Ñ€ĞµĞ¼Ñ�
            "early_bird": Achievement(
                "early_bird", AchievementType.EARLY_BIRD,
                "Ğ–Ğ°Ğ²Ğ¾Ñ€Ğ¾Ğ½Ğ¾Ğº", "Ğ—Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ·Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº Ğ´Ğ¾ 8 ÑƒÑ‚Ñ€Ğ°",
                "ğŸŒ…", 20, {"time_before": "08:00", "meal_type": "breakfast"}
            ),
            
            "night_owl": Achievement(
                "night_owl", AchievementType.NIGHT_OWL,
                "Ğ¡Ğ¾Ğ²Ğ°", "Ğ—Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ ÑƒĞ¶Ğ¸Ğ½ Ğ¿Ğ¾Ñ�Ğ»Ğµ 9 Ğ²ĞµÑ‡ĞµÑ€Ğ°",
                "ğŸŒ™", 15, {"time_after": "21:00", "meal_type": "dinner"}
            )
        }
        return achievements
    
    async def check_achievements(self, user_id: int, event_type: str, data: Dict) -> List[Achievement]:
        """ĞŸÑ€Ğ¾Ğ²ĞµÑ€ĞºĞ° Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹ Ğ´Ğ»Ñ� Ñ�Ğ¾Ğ±Ñ‹Ñ‚Ğ¸Ñ� Ñ� Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸ĞµĞ¼ Ğ² Ğ‘Ğ”"""
        new_achievements = []
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¸Ğ»Ğ¸ Ñ�Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ¸Ğ· Ğ‘Ğ”
        user_progress = await self._get_user_progress(user_id)
        
        # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ
        await self._update_progress_in_db(user_progress, event_type, data)
        
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ ĞºĞ°Ğ¶Ğ´Ğ¾Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğµ
        for achievement in self.achievements.values():
            if not await self._has_achievement(user_id, achievement.id):
                if self._check_achievement_condition(achievement, user_progress, data):
                    await self._award_achievement(user_id, achievement)
                    new_achievements.append(achievement)
                    logger.info(f"User {user_id} earned achievement: {achievement.name}")
        
        return new_achievements
    
    async def _get_user_progress(self, user_id: int) -> UserGamification:
        """ĞŸĞ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ° Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ¸Ğ· Ğ‘Ğ”"""
        async with get_session() as session:
            # Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ¸Ñ‰ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ² Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ¾Ğ¹ Ñ‚Ğ°Ğ±Ğ»Ğ¸Ñ†Ğµ
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User {user_id} not found in main table")
                raise ValueError(f"User {user_id} not found")
            
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¸Ğ»Ğ¸ Ñ�Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ğ³ĞµĞ¹Ğ¼Ğ¸Ñ„Ğ¸ĞºĞ°Ñ†Ğ¸Ñ�
            gamif_result = await session.execute(
                select(UserGamification).where(UserGamification.user_id == user.id)
            )
            gamif = gamif_result.scalar_one_or_none()
            
            if not gamif:
                gamif = UserGamification(
                    user_id=user.id,
                    total_points=0,
                    level=1,
                    current_streak=0,
                    max_streak=0,
                    meals_logged=0,
                    water_ml_total=0
                )
                session.add(gamif)
                await session.commit()
                await session.refresh(gamif)
            
            return gamif
    
    async def _update_progress_in_db(self, progress: UserGamification, event_type: str, data: Dict):
        """Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ° Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ² Ğ‘Ğ”"""
        today = datetime.now().date()
        
        if event_type == "meal_logged":
            progress.last_activity_date = datetime.now()
            progress.meals_logged += 1
            
            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ²Ñ€ĞµĞ¼Ñ�
            meal_time = data.get('time', datetime.now()).time()
            meal_type = data.get('meal_type', '')
            
            if meal_type == 'breakfast' and meal_time.hour < 8:
                progress.early_breakfasts += 1
            elif meal_type == 'dinner' and meal_time.hour >= 21:
                progress.late_dinners += 1
        
        elif event_type == "water_logged":
            progress.last_activity_date = datetime.now()
            progress.water_ml_total += data.get('amount', 0)
        
        elif event_type == "weight_logged":
            progress.last_activity_date = datetime.now()
            weight = data.get('weight', 0)
            if progress.start_weight is None or progress.start_weight == 0:
                progress.start_weight = weight
            progress.current_weight = weight
        
        # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ñ�ĞµÑ€Ğ¸Ñ� Ğ´Ğ½ĞµĞ¹
        await self._update_streak(progress)
        
        # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ�
        async with get_session() as session:
            await session.merge(progress)
            await session.commit()
    
    async def _update_streak(self, progress: UserGamification):
        """Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½Ğ¸Ğµ Ñ�ĞµÑ€Ğ¸Ğ¸ Ğ´Ğ½ĞµĞ¹"""
        if not progress.last_activity_date:
            return
        
        today = datetime.now().date()
        last_activity = progress.last_activity_date.date()
        
        if today == last_activity:
            # Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ� - Ñ�ĞµÑ€Ğ¸Ñ� Ğ¿Ñ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°ĞµÑ‚Ñ�Ñ�
            if progress.current_streak == 0:
                progress.current_streak = 1
            # Ğ•Ñ�Ğ»Ğ¸ ÑƒĞ¶Ğµ Ğ±Ñ‹Ğ»Ğ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�, Ñ�ĞµÑ€Ğ¸Ñ� Ğ½Ğµ Ğ¼ĞµĞ½Ñ�ĞµÑ‚Ñ�Ñ�
        elif today == last_activity + timedelta(days=1):
            # Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ğ²Ñ‡ĞµÑ€Ğ° - ÑƒĞ²ĞµĞ»Ğ¸Ñ‡Ğ¸Ğ²Ğ°ĞµĞ¼ Ñ�ĞµÑ€Ğ¸Ñ�
            progress.current_streak += 1
        else:
            # ĞŸÑ€Ğ¾Ğ¿ÑƒÑ‰ĞµĞ½ Ğ´ĞµĞ½ÑŒ - Ñ�Ğ±Ñ€Ğ°Ñ�Ñ‹Ğ²Ğ°ĞµĞ¼ Ñ�ĞµÑ€Ğ¸Ñ�
            if progress.current_streak > progress.max_streak:
                progress.max_streak = progress.current_streak
            progress.current_streak = 1
        
        # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ ÑƒÑ€Ğ¾Ğ²ĞµĞ½ÑŒ
        progress.level = progress.total_points // 100 + 1
    
    async def _has_achievement(self, user_id: int, achievement_id: str) -> bool:
        """ĞŸÑ€Ğ¾Ğ²ĞµÑ€ĞºĞ° Ğ½Ğ°Ğ»Ğ¸Ñ‡Ğ¸Ñ� Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ� Ñƒ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
        async with get_session() as session:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ ID Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğµ
            result = await session.execute(
                select(UserAchievement).where(
                    UserAchievement.user_id == user.id,
                    UserAchievement.achievement_id == achievement_id
                )
            )
            return result.scalar_one_or_none() is not None
    
    async def _award_achievement(self, user_id: int, achievement: Achievement):
        """ĞŸÑ€Ğ¸Ñ�Ğ²Ğ¾ĞµĞ½Ğ¸Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
        async with get_session() as session:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ ID Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return
            
            # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğµ
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                points=achievement.points,
                earned_at=datetime.now()
            )
            session.add(user_achievement)
            
            # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ² Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ�
            history = AchievementHistory(
                user_id=user.id,
                achievement_id=achievement.id,
                achievement_name=achievement.name,
                achievement_description=achievement.description,
                points_earned=achievement.points,
                earned_at=datetime.now()
            )
            session.add(history)
            
            # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¾Ğ±Ñ‰ÑƒÑ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ
            gamif_result = await session.execute(
                select(UserGamification).where(UserGamification.user_id == user.id)
            )
            gamif = gamif_result.scalar_one_or_none()
            
            if gamif:
                gamif.total_points += achievement.points
                gamif.level = gamif.total_points // 100 + 1
            
            await session.commit()
    
    def _check_achievement_condition(self, achievement: Achievement, 
                                   progress: UserGamification, data: Dict) -> bool:
        """ĞŸÑ€Ğ¾Ğ²ĞµÑ€ĞºĞ° ÑƒÑ�Ğ»Ğ¾Ğ²Ğ¸Ñ� Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�"""
        condition = achievement.condition
        
        if achievement.type == AchievementType.FIRST_MEAL:
            return progress.meals_logged >= condition["count"]
        
        elif achievement.type == AchievementType.WEEK_STREAK:
            return progress.current_streak >= condition["days"]
        
        elif achievement.type == AchievementType.MONTH_STREAK:
            return progress.current_streak >= condition["days"]
        
        elif achievement.type == AchievementType.CALORIE_GOAL:
            return data.get('calorie_goal_reached', False)
        
        elif achievement.type == AchievementType.WATER_GOAL:
            return data.get('water_goal_reached', False)
        
        elif achievement.type == AchievementType.WEIGHT_LOSS:
            if progress.start_weight and progress.current_weight:
                weight_lost = progress.start_weight - progress.current_weight
                return weight_lost >= condition["kg"]
            return False
        
        elif achievement.type == AchievementType.PERFECT_DAY:
            return data.get('perfect_day', False)
        
        elif achievement.type == AchievementType.EARLY_BIRD:
            return progress.early_breakfasts >= 1
        
        elif achievement.type == AchievementType.NIGHT_OWL:
            return progress.late_dinners >= 1
        
        return False
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """ĞŸĞ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğµ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
        async with get_session() as session:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ ID Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return self._get_empty_stats()
            
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ³ĞµĞ¹Ğ¼Ğ¸Ñ„Ğ¸ĞºĞ°Ñ†Ğ¸Ğ¸
            gamif_result = await session.execute(
                select(UserGamification).where(UserGamification.user_id == user.id)
            )
            gamif = gamif_result.scalar_one_or_none()
            
            if not gamif:
                return self._get_empty_stats()
            
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹
            achievements_count = await session.execute(
                select(func.count(UserAchievement.id)).where(
                    UserAchievement.user_id == user.id
                )
            )
            achievements_count = achievements_count.scalar() or 0
            
            level = gamif.total_points // 100 + 1
            points_to_next = (level * 100) - gamif.total_points
            
            return {
                "level": level,
                "total_points": gamif.total_points,
                "points_to_next": points_to_next,
                "achievements_count": achievements_count,
                "streak_days": gamif.current_streak,
                "max_streak": gamif.max_streak,
                "meals_logged": gamif.meals_logged,
                "water_ml_total": gamif.water_ml_total,
                "current_weight": gamif.current_weight,
                "start_weight": gamif.start_weight
            }
    
    def _get_empty_stats(self) -> Dict:
        """ĞŸÑƒÑ�Ñ‚Ğ°Ñ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ´Ğ»Ñ� Ğ½Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
        return {
            "level": 1,
            "total_points": 0,
            "points_to_next": 100,
            "achievements_count": 0,
            "streak_days": 0,
            "max_streak": 0,
            "meals_logged": 0,
            "water_ml_total": 0,
            "current_weight": None,
            "start_weight": None
        }

# Ğ“Ğ»Ğ¾Ğ±Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ñ�ĞºĞ·ĞµĞ¼Ğ¿Ğ»Ñ�Ñ€ Ñ�Ğ¸Ñ�Ñ‚ĞµĞ¼Ñ‹
gamification = GamificationSystem()
