"""
Система геймификации и достижений для NutriBuddy Bot
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Типы достижений"""
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
    """Система геймификации"""
    
    def __init__(self):
        self.achievements = self._init_achievements()
        self.user_progress = {}  # user_id -> UserProgress
    
    def _init_achievements(self) -> Dict[str, Achievement]:
        """Инициализация достижений"""
        achievements = {
            # Еда
            "first_meal": Achievement(
                "first_meal", AchievementType.FIRST_MEAL,
                "Первый шаг", "Запишите первый прием пищи",
                "🍽️", 10, {"count": 1}
            ),
            
            # Серии дней
            "week_streak": Achievement(
                "week_streak", AchievementType.WEEK_STREAK,
                "Неделя дисциплины", "Записывайте еду 7 дней подряд",
                "🔥", 50, {"days": 7}
            ),
            
            "month_streak": Achievement(
                "month_streak", AchievementType.MONTH_STREAK,
                "Месяц мастерства", "Записывайте еду 30 дней подряд",
                "💎", 200, {"days": 30}
            ),
            
            # Цели
            "calorie_goal": Achievement(
                "calorie_goal", AchievementType.CALORIE_GOAL,
                "Мастер калорий", "Выполните дневную норму калорий",
                "🎯", 30, {"type": "daily_goal", "metric": "calories"}
            ),
            
            "water_goal": Achievement(
                "water_goal", AchievementType.WATER_GOAL,
                "Гидратация", "Выпейте дневную норму воды",
                "💧", 25, {"type": "daily_goal", "metric": "water"}
            ),
            
            # Вес
            "weight_loss_1kg": Achievement(
                "weight_loss_1kg", AchievementType.WEIGHT_LOSS,
                "Первый килограмм", "Похудейте на 1 кг",
                "⚖️", 40, {"kg": 1}
            ),
            
            "weight_loss_5kg": Achievement(
                "weight_loss_5kg", AchievementType.WEIGHT_LOSS,
                "Значимый результат", "Похудейте на 5 кг",
                "🏆", 150, {"kg": 5}
            ),
            
            # Идеальный день
            "perfect_day": Achievement(
                "perfect_day", AchievementType.PERFECT_DAY,
                "Идеальный день", "Выполните все цели за день",
                "⭐", 75, {"type": "perfect_day"}
            ),
            
            # Время
            "early_bird": Achievement(
                "early_bird", AchievementType.EARLY_BIRD,
                "Жаворонок", "Запишите завтрак до 8 утра",
                "🌅", 20, {"time_before": "08:00", "meal_type": "breakfast"}
            ),
            
            "night_owl": Achievement(
                "night_owl", AchievementType.NIGHT_OWL,
                "Сова", "Запишите ужин после 9 вечера",
                "🌙", 15, {"time_after": "21:00", "meal_type": "dinner"}
            )
        }
        return achievements
    
    async def check_achievements(self, user_id: int, event_type: str, data: Dict) -> List[Achievement]:
        """Проверка достижений для события"""
        new_achievements = []
        
        # Получаем или создаем прогресс пользователя
        user_progress = self._get_user_progress(user_id)
        
        # Обновляем статистику
        self._update_progress(user_progress, event_type, data)
        
        # Проверяем каждое достижение
        for achievement in self.achievements.values():
            if achievement.id not in user_progress.earned_achievements:
                if self._check_achievement_condition(achievement, user_progress, data):
                    user_progress.earned_achievements.add(achievement.id)
                    user_progress.total_points += achievement.points
                    new_achievements.append(achievement)
                    logger.info(f"User {user_id} earned achievement: {achievement.name}")
        
        return new_achievements
    
    def _get_user_progress(self, user_id: int) -> 'UserProgress':
        """Получение прогресса пользователя"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = UserProgress(user_id)
        return self.user_progress[user_id]
    
    def _update_progress(self, progress: 'UserProgress', event_type: str, data: Dict):
        """Обновление прогресса пользователя"""
        today = datetime.now().date()
        
        if event_type == "meal_logged":
            progress.last_activity_date = today
            progress.meals_logged += 1
            progress.daily_meals += 1
            
            # Проверяем время
            meal_time = data.get('time', datetime.now()).time()
            meal_type = data.get('meal_type', '')
            
            if meal_type == 'breakfast' and meal_time.hour < 8:
                progress.early_breakfasts += 1
            elif meal_type == 'dinner' and meal_time.hour >= 21:
                progress.late_dinners += 1
        
        elif event_type == "water_logged":
            progress.last_activity_date = today
            progress.water_ml += data.get('amount', 0)
        
        elif event_type == "weight_logged":
            progress.last_weight_date = today
            weight = data.get('weight', 0)
            if progress.start_weight == 0:
                progress.start_weight = weight
            progress.current_weight = weight
    
    def _check_achievement_condition(self, achievement: Achievement, 
                                   progress: 'UserProgress', data: Dict) -> bool:
        """Проверка условия достижения"""
        condition = achievement.condition
        
        if achievement.type == AchievementType.FIRST_MEAL:
            return progress.meals_logged >= condition["count"]
        
        elif achievement.type == AchievementType.WEEK_STREAK:
            return self._get_streak_days(progress) >= condition["days"]
        
        elif achievement.type == AchievementType.MONTH_STREAK:
            return self._get_streak_days(progress) >= condition["days"]
        
        elif achievement.type == AchievementType.CALORIE_GOAL:
            return data.get('calorie_goal_reached', False)
        
        elif achievement.type == AchievementType.WATER_GOAL:
            return data.get('water_goal_reached', False)
        
        elif achievement.type == AchievementType.WEIGHT_LOSS:
            weight_lost = progress.start_weight - progress.current_weight
            return weight_lost >= condition["kg"]
        
        elif achievement.type == AchievementType.PERFECT_DAY:
            return data.get('perfect_day', False)
        
        elif achievement.type == AchievementType.EARLY_BIRD:
            return progress.early_breakfasts >= 1
        
        elif achievement.type == AchievementType.NIGHT_OWL:
            return progress.late_dinners >= 1
        
        return False
    
    def _get_streak_days(self, progress: 'UserProgress') -> int:
        """Расчет серии дней"""
        if not progress.last_activity_date:
            return 0
        
        streak = 1
        current_date = progress.last_activity_date
        
        # Проверяем предыдущие дни
        for i in range(1, 30):  # Максимум 30 дней назад
            check_date = current_date - timedelta(days=i)
            # Здесь должна быть проверка в базе данных
            # Для упрощения считаем, что если активность была, серия продолжается
            # В реальной реализации нужно проверять записи в БД
        
        return streak
    
    def get_user_level(self, user_id: int) -> int:
        """Получение уровня пользователя"""
        progress = self._get_user_progress(user_id)
        return progress.total_points // 100 + 1  # 100 очков = 1 уровень
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Получение статистики пользователя"""
        progress = self._get_user_progress(user_id)
        level = self.get_user_level(user_id)
        points_to_next = (level * 100) - progress.total_points
        
        return {
            "level": level,
            "total_points": progress.total_points,
            "points_to_next": points_to_next,
            "achievements_count": len(progress.earned_achievements),
            "streak_days": self._get_streak_days(progress),
            "meals_logged": progress.meals_logged,
            "current_weight": progress.current_weight
        }

class UserProgress:
    """Прогресс пользователя"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.total_points = 0
        self.earned_achievements = set()
        self.last_activity_date = None
        self.meals_logged = 0
        self.daily_meals = 0
        self.water_ml = 0
        self.start_weight = 0
        self.current_weight = 0
        self.last_weight_date = None
        self.early_breakfasts = 0
        self.late_dinners = 0

# Глобальный экземпляр системы
gamification = GamificationSystem()
