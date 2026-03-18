"""
Система геймификации и достижений для NutriBuddy Bot с сохранением в БД
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Типы достижений"""
    FIRST_MEAL = "first_meal"
    WEEK_STREAK = "week_streak"
    MONTH_STREAK = "month_streak"
    CALORIE_GOAL = "calorie_goal"
    WATER_GOAL = "water_goal"
    ACTIVITY_GOAL = "activity_goal"
    WEIGHT_GOAL = "weight_goal"
    PERFECT_DAY = "perfect_day"
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"

class Achievement:
    """Класс достижения"""
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
    """Система геймификации с сохранением в БД"""
    
    def __init__(self):
        self.achievements = self._init_achievements()
    
    def _init_achievements(self) -> Dict[str, Achievement]:
        """Инициализация достижений"""
        achievements = {
            # Еда
            "first_meal": Achievement(
                "first_meal", AchievementType.FIRST_MEAL,
                "Первый шаг", "Запишите первый прием пищи",
                "[MEAL]", 10, {"count": 1}
            ),
            
            # Серии дней
            "week_streak": Achievement(
                "week_streak", AchievementType.WEEK_STREAK,
                "Неделя подряд", "Используйте бот 7 дней подряд",
                "[WEEK]", 50, {"days": 7}
            ),
            
            "month_streak": Achievement(
                "month_streak", AchievementType.MONTH_STREAK,
                "Месяц подряд", "Используйте бот 30 дней подряд",
                "[MONTH]", 200, {"days": 30}
            ),
            
            # Цели по калориям
            "calorie_goal_week": Achievement(
                "calorie_goal_week", AchievementType.CALORIE_GOAL,
                "Мастер калорий", "Выполняйте цель по калориям неделю",
                "[CALORIES]", 75, {"days": 7, "goal_met": True}
            ),
            
            # Цели по воде
            "water_goal_week": Achievement(
                "water_goal_week", AchievementType.WATER_GOAL,
                "Гидратация", "Выполняйте цель по воде неделю",
                "[WATER]", 60, {"days": 7, "goal_met": True}
            ),
            
            # Цели по активности
            "activity_goal_week": Achievement(
                "activity_goal_week", AchievementType.ACTIVITY_GOAL,
                "Энергия", "Выполняйте цель по активности неделю",
                "[ACTIVITY]", 80, {"days": 7, "goal_met": True}
            ),
            
            # Идеальный день
            "perfect_day": Achievement(
                "perfect_day", AchievementType.PERFECT_DAY,
                "Идеальный день", "Выполните все цели за день",
                "[PERFECT]", 100, {"goals_met": "all"}
            ),
            
            # Ранние птицы
            "early_bird": Achievement(
                "early_bird", AchievementType.EARLY_BIRD,
                "Ранняя пташка", "Запишите завтрак до 8 утра",
                "[MORNING]", 30, {"meal_before": "08:00"}
            ),
            
            # Совы
            "night_owl": Achievement(
                "night_owl", AchievementType.NIGHT_OWL,
                "Сова", "Запишите ужин после 9 вечера",
                "[EVENING]", 25, {"meal_after": "21:00"}
            )
        }
        
        return achievements
    
    async def check_achievements(self, user_id: int, action: str, data: Dict = None) -> List[Achievement]:
        """
        Проверяет достижения для пользователя
        
        Args:
            user_id: ID пользователя
            action: Тип действия (meal, water, activity, etc.)
            data: Данные для проверки условий
            
        Returns:
            List[Achievement]: Список разблокированных достижений
        """
        try:
            from database.db import get_session
            from database.models import User, UserAchievement
            
            unlocked = []
            
            with get_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    return []
                
                # Проверяем каждое достижение
                for achievement_id, achievement in self.achievements.items():
                    # Проверяем, не получено ли уже достижение
                    existing = session.query(UserAchievement).filter(
                        UserAchievement.user_id == user.id,
                        UserAchievement.achievement_id == achievement_id
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Проверяем условия достижения
                    if await self._check_achievement_condition(user, achievement, action, data, session):
                        # Сохраняем достижение в БД
                        user_achievement = UserAchievement(
                            user_id=user.id,
                            achievement_id=achievement_id,
                            earned_at=datetime.utcnow()
                        )
                        session.add(user_achievement)
                        session.commit()
                        
                        unlocked.append(achievement)
                        logger.info(f"[ACHIEVEMENT] User {user_id} unlocked: {achievement.name}")
            
            return unlocked
            
        except Exception as e:
            logger.error(f"Error checking achievements for user {user_id}: {e}")
            return []
    
    async def _check_achievement_condition(self, user, achievement: Achievement, 
                                        action: str, data: Dict, session) -> bool:
        """Проверяет условия конкретного достижения"""
        condition = achievement.condition
        
        if achievement.type == AchievementType.FIRST_MEAL:
            return action == "meal" and condition["count"] == 1
        
        elif achievement.type == AchievementType.WEEK_STREAK:
            if action != "daily_check":
                return False
            # Проверяем серию дней
            streak_days = await self._get_user_streak(user.id, session)
            return streak_days >= condition["days"]
        
        elif achievement.type == AchievementType.MONTH_STREAK:
            if action != "daily_check":
                return False
            streak_days = await self._get_user_streak(user.id, session)
            return streak_days >= condition["days"]
        
        elif achievement.type == AchievementType.CALORIE_GOAL:
            if action != "daily_check":
                return False
            return await self._check_goal_streak(user.id, "calories", condition["days"], session)
        
        elif achievement.type == AchievementType.WATER_GOAL:
            if action != "daily_check":
                return False
            return await self._check_goal_streak(user.id, "water", condition["days"], session)
        
        elif achievement.type == AchievementType.ACTIVITY_GOAL:
            if action != "daily_check":
                return False
            return await self._check_goal_streak(user.id, "activity", condition["days"], session)
        
        elif achievement.type == AchievementType.PERFECT_DAY:
            if action != "daily_check":
                return False
            return await self._check_perfect_day(user.id, session)
        
        elif achievement.type == AchievementType.EARLY_BIRD:
            if action != "meal":
                return False
            meal_time = data.get("time", datetime.now()).time()
            target_time = datetime.strptime(condition["meal_before"], "%H:%M").time()
            return meal_time <= target_time
        
        elif achievement.type == AchievementType.NIGHT_OWL:
            if action != "meal":
                return False
            meal_time = data.get("time", datetime.now()).time()
            target_time = datetime.strptime(condition["meal_after"], "%H:%M").time()
            return meal_time >= target_time
        
        return False
    
    async def _get_user_streak(self, user_id: int, session) -> int:
        """Получает серию дней использования бота"""
        try:
            from database.models import FoodEntry, DrinkEntry, ActivityEntry
            from datetime import date
            
            today = date.today()
            streak = 0
            
            # Проверяем каждый день назад
            for i in range(365):  # Максимум год назад
                check_date = today - timedelta(days=i)
                
                # Проверяем, была ли активность в этот день
                has_activity = (
                    session.query(FoodEntry).filter(
                        FoodEntry.user_id == user_id,
                        FoodEntry.date == check_date
                    ).first() or
                    session.query(DrinkEntry).filter(
                        DrinkEntry.user_id == user_id,
                        DrinkEntry.date == check_date
                    ).first() or
                    session.query(ActivityEntry).filter(
                        ActivityEntry.user_id == user_id,
                        ActivityEntry.date == check_date
                    ).first()
                )
                
                if has_activity:
                    streak += 1
                else:
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"Error calculating streak for user {user_id}: {e}")
            return 0
    
    async def _check_goal_streak(self, user_id: int, goal_type: str, days: int, session) -> bool:
        """Проверяет серию выполнения целей"""
        try:
            from database.models import User
            from utils.daily_stats import get_daily_stats
            from datetime import date
            
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            today = date.today()
            
            for i in range(days):
                check_date = today - timedelta(days=i)
                stats = await get_daily_stats(user_id, check_date)
                
                if goal_type == "calories":
                    goal_met = stats.get('calories_consumed', 0) >= user.daily_calorie_goal * 0.9  # 90% от цели
                elif goal_type == "water":
                    goal_met = stats.get('water_consumed', 0) >= user.daily_water_goal * 0.9
                elif goal_type == "activity":
                    goal_met = stats.get('activity_minutes', 0) >= 30  # Минимум 30 минут
                else:
                    goal_met = False
                
                if not goal_met:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking goal streak for user {user_id}: {e}")
            return False
    
    async def _check_perfect_day(self, user_id: int, session) -> bool:
        """Проверяет идеальный день"""
        try:
            from database.models import User
            from utils.daily_stats import get_daily_stats
            from datetime import date
            
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            today = date.today()
            stats = await get_daily_stats(user_id, today)
            
            # Проверяем все цели
            calorie_goal_met = stats.get('calories_consumed', 0) >= user.daily_calorie_goal * 0.9
            water_goal_met = stats.get('water_consumed', 0) >= user.daily_water_goal * 0.9
            activity_goal_met = stats.get('activity_minutes', 0) >= 30
            has_meals = stats.get('meals_count', 0) >= 3  # Минимум 3 приема пищи
            
            return calorie_goal_met and water_goal_met and activity_goal_met and has_meals
            
        except Exception as e:
            logger.error(f"Error checking perfect day for user {user_id}: {e}")
            return False
    
    async def get_user_achievements(self, user_id: int) -> List[Dict]:
        """Получает все достижения пользователя"""
        try:
            from database.db import get_session
            from database.models import User, UserAchievement
            
            with get_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    return []
                
                achievements = session.query(UserAchievement).filter(
                    UserAchievement.user_id == user.id
                ).order_by(UserAchievement.earned_at.desc()).all()
                
                result = []
                for user_achievement in achievements:
                    achievement = self.achievements.get(user_achievement.achievement_id)
                    if achievement:
                        result.append({
                            'id': achievement.id,
                            'name': achievement.name,
                            'description': achievement.description,
                            'icon': achievement.icon,
                            'points': achievement.points,
                            'earned_at': user_achievement.earned_at
                        })
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting user achievements for {user_id}: {e}")
            return []
    
    async def get_user_points(self, user_id: int) -> int:
        """Получает общее количество очков пользователя"""
        try:
            achievements = await self.get_user_achievements(user_id)
            return sum(achievement['points'] for achievement in achievements)
        except Exception as e:
            logger.error(f"Error getting user points for {user_id}: {e}")
            return 0
    
    async def get_user_level(self, user_id: int) -> Dict:
        """Получает уровень пользователя"""
        try:
            points = await self.get_user_points(user_id)
            
            # Уровни: каждые 100 очков = новый уровень
            level = points // 100 + 1
            points_to_next = ((level) * 100) - points
            progress = (points % 100)
            
            return {
                'level': level,
                'points': points,
                'points_to_next': points_to_next,
                'progress': progress
            }
            
        except Exception as e:
            logger.error(f"Error getting user level for {user_id}: {e}")
            return {'level': 1, 'points': 0, 'points_to_next': 100, 'progress': 0}
    
    def get_achievement_progress(self, user_id: int, achievement_id: str) -> Dict:
        """Получает прогресс по достижению"""
        try:
            achievement = self.achievements.get(achievement_id)
            if not achievement:
                return {}
            
            # TODO: Реализовать расчет прогресса для каждого типа достижения
            # Это требует более сложной логики для отслеживания прогресса
            
            return {
                'achievement_id': achievement_id,
                'name': achievement.name,
                'current': 0,
                'target': 1,
                'progress': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting achievement progress for {user_id}: {e}")
            return {}
    
    async def get_leaderboard(self, period: str = "all", limit: int = 10) -> List[Dict]:
        """Получает таблицу лидеров"""
        try:
            from database.db import get_session
            from database.models import User, UserAchievement
            from sqlalchemy import func
            
            with get_session() as session:
                # Получаем всех пользователей с их достижениями
                query = session.query(
                    User.telegram_id,
                    User.first_name,
                    func.count(UserAchievement.id).label('achievements_count'),
                    func.sum(self.achievements['achievement_id'].points).label('total_points')
                ).outerjoin(UserAchievement).group_by(User.id)
                
                # Фильтрация по периоду (TODO: добавить фильтрацию по дате)
                if period == "week":
                    pass  # TODO: добавить фильтрацию за неделю
                elif period == "month":
                    pass  # TODO: добавить фильтрацию за месяц
                
                results = query.order_by(func.sum(UserAchievement.points).desc()).limit(limit).all()
                
                leaderboard = []
                for i, (telegram_id, first_name, achievements_count, total_points) in enumerate(results, 1):
                    leaderboard.append({
                        'position': i,
                        'telegram_id': telegram_id,
                        'name': first_name or f"User_{telegram_id}",
                        'achievements_count': achievements_count or 0,
                        'total_points': total_points or 0
                    })
                
                return leaderboard
                
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

# Глобальная экземпляр системы геймификации
gamification_system = GamificationSystem()

async def check_achievements(user_id: int, action: str, data: Dict = None) -> List[Achievement]:
    """Проверяет достижения для пользователя"""
    return await gamification_system.check_achievements(user_id, action, data)

async def get_user_achievements(user_id: int) -> List[Dict]:
    """Получает достижения пользователя"""
    return await gamification_system.get_user_achievements(user_id)

async def get_user_points(user_id: int) -> int:
    """Получает очки пользователя"""
    return await gamification_system.get_user_points(user_id)

async def get_user_level(user_id: int) -> Dict:
    """Получает уровень пользователя"""
    return await gamification_system.get_user_level(user_id)

async def get_leaderboard(period: str = "all", limit: int = 10) -> List[Dict]:
    """Получает таблицу лидеров"""
    return await gamification_system.get_leaderboard(period, limit)

def format_achievement_message(achievement: Achievement) -> str:
    """Форматирует сообщение о достижении"""
    return (
        f"[ACHIEVEMENT] <b>Новое достижение!</b>\n\n"
        f"{achievement.icon} <b>{achievement.name}</b>\n"
        f"{achievement.description}\n"
        f"[POINTS] +{achievement.points} очков\n\n"
        f"[INFO] <i>Проверьте все достижения в профиле!</i>"
    )

def format_level_info(level_info: Dict) -> str:
    """Форматирует информацию об уровне"""
    return (
        f"[LEVEL] <b>Уровень {level_info['level']}</b>\n"
        f"[POINTS] Очки: {level_info['points']}\n"
        f"[PROGRESS] Прогресс: {level_info['progress']}/100\n"
        f"[NEXT] До следующего уровня: {level_info['points_to_next']} очков"
    )
