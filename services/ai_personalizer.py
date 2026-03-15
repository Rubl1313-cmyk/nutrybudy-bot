"""
Сервис персонализации NutriBuddy Bot
Адаптивные приветствия, контекстные подсказки, персонализированный контент
"""
import logging
from datetime import datetime
from typing import Dict
from database.db import get_session
from database.models import User
from sqlalchemy import select

logger = logging.getLogger(__name__)

class AIPersonalizer:
    """Персонализатор AI контента"""
    
    async def get_user_context(self, user_id: int) -> Dict:
        """Получает полный контекст пользователя"""
        try:
            async with get_session() as session:
                user_result = await session.execute(select(User).where(User.telegram_id == user_id))
                user = user_result.scalar_one_or_none()
                
                if user:
                    return {
                        "user_info": {
                            "first_name": user.first_name,
                            "age": user.age,
                            "gender": user.gender,
                            "weight": user.weight,
                            "height": user.height,
                            "goal": user.goal,
                            "activity_level": user.activity_level,
                            "city": user.city
                        },
                        "goals": {
                            "daily_calorie_goal": user.daily_calorie_goal,
                            "daily_protein_goal": user.daily_protein_goal,
                            "daily_fat_goal": user.daily_fat_goal,
                            "daily_carbs_goal": user.daily_carbs_goal,
                            "daily_water_goal": user.daily_water_goal,
                            "daily_steps_goal": user.daily_steps_goal
                        },
                        "time_context": {
                            "hour": datetime.now().hour,
                            "day_of_week": datetime.now().weekday(),
                            "is_weekend": datetime.now().weekday() >= 5
                        }
                    }
                return {}
        except Exception as e:
            logger.error(f"❌ Error getting user context: {e}")
            return {}
    
    async def get_greeting(self, user_id: int) -> str:
        """Возвращает персонализированное приветствие"""
        context = await self.get_user_context(user_id)
        user_info = context.get("user_info", {})
        time_context = context.get("time_context", {})
        
        hour = time_context.get("hour", datetime.now().hour)
        name = user_info.get("first_name", "Пользователь")
        
        # Базовое приветствие по времени
        if 5 <= hour < 12:
            base = "Доброе утро"
            emoji = "🌅"
        elif 12 <= hour < 18:
            base = "Добрый день"
            emoji = "☀️"
        else:
            base = "Добрый вечер"
            emoji = "🌙"
        
        greeting = f"{emoji} {base}, {name}!"
        
        # Добавляем персонализацию на основе целей
        goal = user_info.get("goal", "")
        if goal == "weight_loss":
            greeting += " Готовы к дню похудения?"
        elif goal == "muscle_gain":
            greeting += " Сегодня день набора массы!"
        elif goal == "maintenance":
            greeting += " Поддерживаем форму!"
        
        return greeting
    
    async def get_motivational_message(self, user_id: int, progress_data: Dict) -> str:
        """Генерирует мотивационное сообщение на основе прогресса"""
        context = await self.get_user_context(user_id)
        user_info = context.get("user_info", {})
        goal = user_info.get("goal", "")
        
        calorie_progress = progress_data.get("calorie_progress", 0)
        
        if calorie_progress >= 100:
            if goal == "weight_loss":
                return "🎯 Отлично! Цель по калориям достигнута без перебора!"
            elif goal == "muscle_gain":
                return "💪 Супер! Достаточно калорий для роста мышц!"
            else:
                return "✨ Идеально! Баланс соблюден!"
        
        elif calorie_progress >= 75:
            if goal == "weight_loss":
                return "⚡ Отличный темп! Так держать!"
            elif goal == "muscle_gain":
                return "🔥 Хорошо! Можно добавить еще немного!"
            else:
                return "👍 Прекрасно! Почти у цели!"
        
        elif calorie_progress >= 50:
            return "🌱 Хорошее начало! Продолжайте в том же духе!"
        
        else:
            return "💪 День только начинается! У вас всё получится!"
    
    async def get_smart_suggestions(self, user_id: int) -> Dict[str, list]:
        """Генерирует умные предложения на основе контекста"""
        context = await self.get_user_context(user_id)
        time_context = context.get("time_context", {})
        user_info = context.get("user_info", {})
        
        hour = time_context.get("hour", datetime.now().hour)
        goal = user_info.get("goal", "")
        
        suggestions = {
            "meal_suggestions": [],
            "activity_suggestions": [],
            "water_suggestions": []
        }
        
        # Предложения еды по времени
        if 5 <= hour < 11:
            suggestions["meal_suggestions"] = [
                "🥞 Овсянка с ягодами",
                "🍳 Яичница с тостами",
                "🥛 Сырники",
                "🥤 Смузи"
            ]
        elif 11 <= hour < 15:
            suggestions["meal_suggestions"] = [
                "🍲 Куриный суп",
                "🍛 Салат Цезарь",
                "🍛 Гречка с котлетой",
                "🥗 Легкий салат"
            ]
        elif 15 <= hour < 20:
            suggestions["meal_suggestions"] = [
                "🍽️ Запеченная рыба",
                "🥩 Стейк с овощами",
                "🍝 Паста с соусом",
                "🥗 Большой салат"
            ]
        else:
            suggestions["meal_suggestions"] = [
                "🍎 Яблоко",
                "🥛 Йогурт",
                "🥜 Орехи",
                "🍌 Банан"
            ]
        
        # Предложения активности
        if goal == "weight_loss":
            suggestions["activity_suggestions"] = [
                "🚶‍♀️ 30 минут ходьбы",
                "🏃‍♀️ Легкий бег",
                "🚴‍♀️ Велотренажер",
                "🧘‍♀️ Йога"
            ]
        elif goal == "muscle_gain":
            suggestions["activity_suggestions"] = [
                "🏋️‍♀️ Силовая тренировка",
                "🏃‍♀️ Интервальный бег",
                "🤸‍♀️ Прыжки",
                "💪 Отжимания"
            ]
        else:
            suggestions["activity_suggestions"] = [
                "🚶‍♀️ Прогулка",
                "🏃‍♀️ Легкая зарядка",
                "🧘‍♀️ Растяжка",
                "🚴‍♀️ Езда на велосипеде"
            ]
        
        # Предложения воды
        suggestions["water_suggestions"] = [
            "💧 250 мл",
            "💧 500 мл", 
            "💧 750 мл",
            "💧 1 литр"
        ]
        
        return suggestions
    
    async def get_personalized_tips(self, user_id: int) -> list:
        """Генерирует персонализированные советы"""
        context = await self.get_user_context(user_id)
        user_info = context.get("user_info", {})
        goals = context.get("goals", {})
        time_context = context.get("time_context", {})
        
        tips = []
        goal = user_info.get("goal", "")
        hour = time_context.get("hour", datetime.now().hour)
        
        # Советы по целям
        if goal == "weight_loss":
            tips.extend([
                "💡 Добавьте больше белка для сытости",
                "🥗 Пейте воду перед едой",
                "🚶‍♀️ Увеличьте ежедневную активность"
            ])
        elif goal == "muscle_gain":
            tips.extend([
                "💪 Увеличьте потребление белка",
                "🏋️‍♀️ Не пропускайте тренировки",
                "😴 Спите достаточно для восстановления"
            ])
        else:
            tips.extend([
                "⚖️ Поддерживайте баланс БЖУ",
                "💧 Пейте достаточно воды",
                "🏃‍♀️ Будьте активны каждый день"
            ])
        
        # Временные советы
        if 5 <= hour < 12:
            tips.append("🌅 Утро - лучшее время для завтрака!")
        elif 12 <= hour < 18:
            tips.append("☀️ Не забывайте про обед!")
        else:
            tips.append("🌙 Легкий ужин перед сном")
        
        return tips[:3]  # Возвращаем до 3 советов

# Глобальный экземпляр
ai_personalizer = AIPersonalizer()
