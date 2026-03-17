"""
Система геймификации и достижений для NutriBuddy Bot с сохранением в БД
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
        """Проверка достижений для события с сохранением в БД"""
        new_achievements = []
        
        # Получаем или создаем прогресс пользователя из БД
        user_progress = await self._get_user_progress(user_id)
        
        # Обновляем статистику
        await self._update_progress_in_db(user_progress, event_type, data)
        
        # Проверяем каждое достижение
        for achievement in self.achievements.values():
            if not await self._has_achievement(user_id, achievement.id):
                if self._check_achievement_condition(achievement, user_progress, data):
                    await self._award_achievement(user_id, achievement)
                    new_achievements.append(achievement)
                    logger.info(f"User {user_id} earned achievement: {achievement.name}")
        
        return new_achievements
    
    async def _get_user_progress(self, user_id: int) -> UserGamification:
        """Получение прогресса пользователя из БД"""
        async with get_session() as session:
            # Сначала ищем пользователя в основной таблице
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User {user_id} not found in main table")
                raise ValueError(f"User {user_id} not found")
            
            # Получаем или создаем геймификацию
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
        """Обновление прогресса пользователя в БД"""
        today = datetime.now().date()
        
        if event_type == "meal_logged":
            progress.last_activity_date = datetime.now()
            progress.meals_logged += 1
            
            # Проверяем время
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
        
        # Обновляем серию дней
        await self._update_streak(progress)
        
        # Сохраняем изменения
        async with get_session() as session:
            await session.merge(progress)
            await session.commit()
    
    async def _update_streak(self, progress: UserGamification):
        """Обновление серии дней"""
        if not progress.last_activity_date:
            return
        
        today = datetime.now().date()
        last_activity = progress.last_activity_date.date()
        
        if today == last_activity:
            # Активность сегодня - серия продолжается
            if progress.current_streak == 0:
                progress.current_streak = 1
            # Если уже была активность сегодня, серия не меняется
        elif today == last_activity + timedelta(days=1):
            # Активность вчера - увеличиваем серию
            progress.current_streak += 1
        else:
            # Пропущен день - сбрасываем серию
            if progress.current_streak > progress.max_streak:
                progress.max_streak = progress.current_streak
            progress.current_streak = 1
        
        # Обновляем уровень
        progress.level = progress.total_points // 100 + 1
    
    async def _has_achievement(self, user_id: int, achievement_id: str) -> bool:
        """Проверка наличия достижения у пользователя"""
        async with get_session() as session:
            # Получаем ID пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Проверяем достижение
            result = await session.execute(
                select(UserAchievement).where(
                    UserAchievement.user_id == user.id,
                    UserAchievement.achievement_id == achievement_id
                )
            )
            return result.scalar_one_or_none() is not None
    
    async def _award_achievement(self, user_id: int, achievement: Achievement):
        """Присвоение достижения пользователю"""
        async with get_session() as session:
            # Получаем ID пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return
            
            # Добавляем достижение
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                points=achievement.points,
                earned_at=datetime.now()
            )
            session.add(user_achievement)
            
            # Добавляем в историю
            history = AchievementHistory(
                user_id=user.id,
                achievement_id=achievement.id,
                achievement_name=achievement.name,
                achievement_description=achievement.description,
                points_earned=achievement.points,
                earned_at=datetime.now()
            )
            session.add(history)
            
            # Обновляем общую статистику
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
        """Проверка условия достижения"""
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
        """Получение статистики пользователя"""
        async with get_session() as session:
            # Получаем ID пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return self._get_empty_stats()
            
            # Получаем статистику геймификации
            gamif_result = await session.execute(
                select(UserGamification).where(UserGamification.user_id == user.id)
            )
            gamif = gamif_result.scalar_one_or_none()
            
            if not gamif:
                return self._get_empty_stats()
            
            # Получаем количество достижений
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
        """Пустая статистика для нового пользователя"""
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

# Глобальный экземпляр системы
gamification = GamificationSystem()
