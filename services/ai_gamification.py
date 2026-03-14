"""
🎮 AI-геймификация NutriBuddy
✨ Адаптивная система достижений и челленджей
🎯 Персонализированные награды и мотивация
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from services.ai_engine_manager import ai
from services.ai_personalizer import ai_personalizer
from database.db import get_session
from database.models import User, WaterEntry, Activity, WeightEntry
from sqlalchemy import select

logger = logging.getLogger(__name__)

class AIGamification:
    """AI-геймификация с адаптивной системой"""
    
    def __init__(self):
        self.ai = ai
        self.personalizer = ai_personalizer
        self.achievement_templates = self._init_achievement_templates()
        self.challenge_templates = self._init_challenge_templates()
    
    def _init_achievement_templates(self) -> List[Dict]:
        """Инициализирует шаблоны достижений"""
        return [
            {
                "id": "first_week",
                "name": "Первая неделя",
                "description": "Активно использовать бот неделю",
                "category": "consistency",
                "difficulty": "easy",
                "xp_reward": 100,
                "icon": "🌟"
            },
            {
                "id": "hydration_master",
                "name": "Мастер гидратации",
                "description": "Выпивать 2 литра воды 7 дней подряд",
                "category": "water",
                "difficulty": "medium",
                "xp_reward": 150,
                "icon": "💧"
            },
            {
                "id": "activity_champion",
                "name": "Чемпион активности",
                "description": "Тренироваться 5 дней в неделю",
                "category": "activity",
                "difficulty": "medium",
                "xp_reward": 200,
                "icon": "🏃"
            },
            {
                "id": "weight_tracker",
                "name": "Весо-следопыт",
                "description": "Записывать вес 14 дней подряд",
                "category": "tracking",
                "difficulty": "medium",
                "xp_reward": 180,
                "icon": "⚖️"
            },
            {
                "id": "calorie_consistent",
                "name": "Калорийный консистент",
                "description": "Держаться в пределах цели по калориям 5 дней",
                "category": "nutrition",
                "difficulty": "hard",
                "xp_reward": 250,
                "icon": "🔥"
            },
            {
                "id": "perfect_week",
                "name": "Идеальная неделя",
                "description": "Выполнить все ежедневные цели 7 дней подряд",
                "category": "perfect",
                "difficulty": "hard",
                "xp_reward": 500,
                "icon": "👑"
            }
        ]
    
    def _init_challenge_templates(self) -> List[Dict]:
        """Инициализирует шаблоны челленджей"""
        return [
            {
                "id": "water_week",
                "name": "Водная неделя",
                "description": "Выпивай 2.5 литра воды каждый день",
                "duration_days": 7,
                "category": "water",
                "difficulty": "medium",
                "xp_reward": 300,
                "icon": "💦"
            },
            {
                "id": "activity_boost",
                "name": "Активный буст",
                "description": "30 минут активности каждый день",
                "duration_days": 5,
                "category": "activity",
                "difficulty": "medium",
                "xp_reward": 250,
                "icon": "⚡"
            },
            {
                "id": "no_sugar",
                "name": "Без сахара",
                "description": "Избегать добавленного сахара 3 дня",
                "duration_days": 3,
                "category": "nutrition",
                "difficulty": "hard",
                "xp_reward": 200,
                "icon": "🚫"
            },
            {
                "id": "step_master",
                "name": "Мастер шагов",
                "description": "10000 шагов каждый день",
                "duration_days": 7,
                "category": "activity",
                "difficulty": "hard",
                "xp_reward": 400,
                "icon": "👟"
            }
        ]
    
    async def generate_personalized_achievements(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Генерирует персонализированные достижения для пользователя
        
        Адаптирует под:
        - Уровень пользователя
        - Психологический профиль
        - Текущие цели
        - Историю достижений
        """
        
        # Получаем профиль пользователя
        persona = await self.personalizer.get_user_persona(user_id)
        user_data = await self._collect_gamification_data(user_id)
        
        if not user_data["has_data"]:
            return self._get_starter_achievements()
        
        # AI-генерация персонализированных достижений
        achievement_prompt = f"""
        Создай персонализированные достижения для пользователя NutriBuddy.
        
        ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
        {self._format_gamification_data(user_data)}
        
        ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ:
        - Тип личности: {persona.get('personality_type', 'неизвестен')}
        - Уровень дисциплины: {persona.get('discipline_level', 5)}/10
        - Мотивационные триггеры: {', '.join(persona.get('motivation_triggers', []))}
        
        Создай 3-5 персонализированных достижений:
        
        1. Адаптируй сложность под уровень дисциплины
        2. Используй мотивационные триггеры
        3. Учитывай текущие цели и паттерны
        4. Создай достижения для разных категорий (вода, активность, питание, последовательность)
        5. Достижения должны быть выполнимыми, но не слишком легкими
        
        Каждое достижение включи:
        - Уникальное название
        - Понятное описание
        - Категорию
        - Сложность (easy/medium/hard)
        - Награду в XP
        - Иконку (эмодзи)
        - Персонализацию (почему это подходит пользователю)
        
        Верни JSON с массивом достижений.
        """
        
        try:
            result = await self.ai.process_text(
                prompt=achievement_prompt,
                task_type="json",
                system_prompt="Ты гейм-дизайнер. Создавай мотивирующие и персонализированные достижения."
            )
            
            if result.get("success"):
                response_text = result.get("data", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    achievements = json.loads(json_match.group())
                    
                    # Добавляем базовые достижения
                    all_achievements = self._add_base_achievements(achievements.get("achievements", []))
                    
                    logger.info(f"🎮 Generated {len(all_achievements)} achievements for user {user_id}")
                    return all_achievements
            
        except Exception as e:
            logger.error(f"Achievement generation error: {e}")
        
        return self._get_adaptive_achievements(user_data)
    
    async def generate_dynamic_challenge(
        self,
        user_id: int,
        challenge_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Генерирует динамический челлендж
        
        challenge_type: water, activity, nutrition, weight, auto (автоматический выбор)
        """
        
        persona = await self.personalizer.get_user_persona(user_id)
        user_data = await self._collect_gamification_data(user_id)
        
        # Определяем тип челленджа
        if challenge_type == "auto":
            challenge_type = self._select_optimal_challenge_type(user_data, persona)
        
        challenge_prompt = f"""
        Создай персонализированный челлендж для пользователя NutriBuddy.
        
        ТИП ЧЕЛЛЕНДЖА: {challenge_type}
        
        ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
        {self._format_gamification_data(user_data)}
        
        ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ:
        - Тип личности: {persona.get('personality_type', 'неизвестен')}
        - Уровень дисциплины: {persona.get('discipline_level', 5)}/10
        - Мотивационные триггеры: {', '.join(persona.get('motivation_triggers', []))}
        
        Создай челлендж который:
        1. Соответствует типу и сложности для пользователя
        2. Использует мотивационные триггеры
        3. Выполним за 3-7 дней
        4. Помогает достичь текущих целей
        5. Интересен и мотивирующ
        
        Верни JSON:
        {{
            "id": "уникальный_id",
            "name": "название челленджа",
            "description": "подробное описание",
            "category": "{challenge_type}",
            "duration_days": 3-7,
            "difficulty": "easy/medium/hard",
            "daily_tasks": [
                {{
                    "day": 1,
                    "task": "задание на день",
                    "target": "конкретная цель"
                }}
            ],
            "rewards": {{
                "xp": количество_XP,
                "achievement": "название достижения",
                "bonus": "дополнительная награда"
            }},
            "personalization": "почему этот челлендж подходит пользователю",
            "motivation_quote": "мотивационная цитата"
        }}
        """
        
        try:
            result = await self.ai.process_text(
                prompt=challenge_prompt,
                task_type="json",
                system_prompt="Ты гейм-дизайнер. Создавай увлекательные и полезные челленджи."
            )
            
            if result.get("success"):
                response_text = result.get("data", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    challenge = json.loads(json_match.group())
                    
                    # Добавляем метаданные
                    challenge.update({
                        "user_id": user_id,
                        "created_at": datetime.now().isoformat(),
                        "status": "active",
                        "progress": 0
                    })
                    
                    logger.info(f"🎮 Generated {challenge_type} challenge for user {user_id}")
                    return challenge
            
        except Exception as e:
            logger.error(f"Challenge generation error: {e}")
        
        return self._get_template_challenge(challenge_type)
    
    async def calculate_user_level(self, user_id: int) -> Dict[str, Any]:
        """
        Рассчитывает уровень и прогресс пользователя
        """
        
        user_data = await self._collect_gamification_data(user_id)
        
        if not user_data["has_data"]:
            return {
                "level": 1,
                "current_xp": 0,
                "xp_to_next": 100,
                "progress_percent": 0,
                "title": "Новичок",
                "total_achievements": 0
            }
        
        # Расчет XP на основе активности
        xp_breakdown = {
            "water": user_data.get("water_days", 0) * 10,
            "activity": user_data.get("activity_count", 0) * 15,
            "weight": user_data.get("weight_days", 0) * 12,
            "consistency": user_data.get("streak_days", 0) * 25,
            "perfect_days": user_data.get("perfect_days", 0) * 50
        }
        
        total_xp = sum(xp_breakdown.values())
        
        # Расчет уровня (прогрессивная шкала)
        level_thresholds = [0, 100, 250, 500, 1000, 1750, 2750, 4000, 5500, 7500, 10000]
        
        current_level = 1
        for i, threshold in enumerate(level_thresholds):
            if total_xp >= threshold:
                current_level = i + 1
            else:
                break
        
        xp_to_next = level_thresholds[min(current_level, len(level_thresholds) - 1)] - total_xp
        xp_from_prev = total_xp - level_thresholds[current_level - 2] if current_level > 1 else total_xp
        xp_needed = level_thresholds[current_level - 1] - level_thresholds[current_level - 2] if current_level > 1 else 100
        
        progress_percent = (xp_from_prev / xp_needed * 100) if xp_needed > 0 else 100
        
        # Титулы по уровням
        titles = [
            "Новичок", "Энтузиаст", "Практик", "Эксперт", "Мастер",
            "Чемпион", "Легенда", "Гуру", "Магистр", "Просветленный", "Бог здоровья"
        ]
        
        title = titles[min(current_level - 1, len(titles) - 1)]
        
        return {
            "level": current_level,
            "current_xp": total_xp,
            "xp_to_next": max(0, xp_to_next),
            "progress_percent": min(100, progress_percent),
            "title": title,
            "total_achievements": user_data.get("achievements_count", 0),
            "xp_breakdown": xp_breakdown
        }
    
    async def generate_motivational_content(
        self,
        user_id: int,
        context: str = "general"
    ) -> Dict[str, Any]:
        """
        Генерирует мотивационный контент с учетом геймификации
        """
        
        user_level = await self.calculate_user_level(user_id)
        persona = await self.personalizer.get_user_persona(user_id)
        
        motivation_prompt = f"""
        Создай мотивационный контент для пользователя NutriBuddy с учетом геймификации.
        
        КОНТЕКСТ: {context}
        
        УРОВЕНЬ ПОЛЬЗОВАТЕЛЯ:
        - Уровень: {user_level['level']}
        - Титул: {user_level['title']}
        - XP: {user_level['current_xp']}
        - Прогресс: {user_level['progress_percent']:.1f}%
        
        ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ:
        - Тип личности: {persona.get('personality_type', 'неизвестен')}
        - Мотивационные триггеры: {', '.join(persona.get('motivation_triggers', []))}
        
        Создай контент включающий:
        1. Персонализированное мотивационное сообщение
        2. Отсылку к текущему уровню/титулу
        3. Использование мотивационных триггеров
        4. Подсказку для прогресса к следующему уровню
        5. Эмодзи соответствующие настроению
        
        Верни JSON:
        {{
            "motivation_message": "основное мотивационное сообщение",
            "level_reference": "отсылка к уровню/титулу",
            "progress_tip": "совет для прогресса",
            "achievement_preview": "предстоящее достижение",
            "emoji_set": ["подходящие эмодзи"]
        }}
        """
        
        try:
            result = await self.ai.process_text(
                prompt=motivation_prompt,
                task_type="json",
                system_prompt="Ты мотивационный коуч с элементами геймификации. Создавай вдохновляющий контент."
            )
            
            if result.get("success"):
                response_text = result.get("data", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    motivation_content = json.loads(json_match.group())
                    
                    logger.info(f"🎮 Generated motivation content for user {user_id}")
                    return motivation_content
            
        except Exception as e:
            logger.error(f"Motivation content error: {e}")
        
        return self._get_default_motivation(user_level, context)
    
    async def _collect_gamification_data(self, user_id: int) -> Dict[str, Any]:
        """Собирает данные для геймификации"""
        
        start_date = datetime.now() - timedelta(days=30)
        
        async with get_session() as session:
            # Получаем данные пользователя по telegram_id
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"has_data": False}
            
            # Используем внутренний ID для запросов к дочерним таблицам
            internal_user_id = user.id
            
            # Активность
            activity_result = await session.execute(
                select(Activity)
                .where(
                    Activity.user_id == internal_user_id,
                    Activity.datetime >= start_date
                )
            )
            activities = activity_result.scalars().all()
            
            # Вес
            weight_result = await session.execute(
                select(WeightEntry)
                .where(
                    WeightEntry.user_id == internal_user_id,
                    WeightEntry.datetime >= start_date
                )
            )
            weight_entries = weight_result.scalars().all()
            
            # Вода
            water_result = await session.execute(
                select(WaterEntry)
                .where(
                    WaterEntry.user_id == internal_user_id,
                    WaterEntry.datetime >= start_date
                )
            )
            water_entries = water_result.scalars().all()
            
            # Анализ данных
            activity_days = len(set(a.datetime.date() for a in activities))
            weight_days = len(set(w.datetime.date() for w in weight_entries))
            water_days = len(set(w.datetime.date() for w in water_entries))
            
            # Идеальные дни (все типы записей)
            all_days = set()
            all_days.update([a.datetime.date() for a in activities])
            all_days.update([w.datetime.date() for w in weight_entries])
            all_days.update([w.datetime.date() for w in water_entries])
            
            perfect_days = 0
            for day in all_days:
                day_activities = [a for a in activities if a.datetime.date() == day]
                day_weights = [w for w in weight_entries if w.datetime.date() == day]
                day_waters = [w for w in water_entries if w.datetime.date() == day]
                
                if day_activities and day_weights and day_waters:
                    perfect_days += 1
            
            return {
                "has_data": True,
                "user_info": {
                    "goal": user.goal,
                    "daily_calorie_goal": user.daily_calorie_goal,
                    "target_weight": user.target_weight
                },
                "activity_count": len(activities),
                "activity_days": activity_days,
                "weight_days": weight_days,
                "water_days": water_days,
                "perfect_days": perfect_days,
                "streak_days": self._calculate_streak(activities, weight_entries, water_entries),
                "achievements_count": 0  # Здесь можно добавить подсчет достижений
            }
    
    def _calculate_streak(self, activities, weights, waters) -> int:
        """Рассчитывает текущий стрик"""
        dates = set()
        dates.update([a.datetime.date() for a in activities])
        dates.update([w.datetime.date() for w in weights])
        dates.update([w.datetime.date() for w in waters])
        
        if not dates:
            return 0
        
        sorted_dates = sorted(dates, reverse=True)
        streak = 0
        current_date = datetime.now().date()
        
        for date in sorted_dates:
            if date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break
        
        return streak
    
    def _format_gamification_data(self, user_data: Dict) -> str:
        """Форматирует данные для AI"""
        if not user_data.get("has_data"):
            return "Недостаточно данных для анализа"
        
        user_info = user_data.get("user_info", {})
        
        return f"""
        Пользователь:
        - Цель: {user_info.get('goal', 'неизвестно')}
        - Целевой вес: {user_info.get('target_weight', 'неизвестно')} кг
        - Цель по калориям: {user_info.get('daily_calorie_goal', 'неизвестно')} ккал
        
        Активность за 30 дней:
        - Всего активностей: {user_data.get('activity_count', 0)}
        - Дней с активностью: {user_data.get('activity_days', 0)}
        - Дней с записями веса: {user_data.get('weight_days', 0)}
        - Дней с записями воды: {user_data.get('water_days', 0)}
        - Идеальных дней: {user_data.get('perfect_days', 0)}
        - Текущий стрик: {user_data.get('streak_days', 0)} дней
        """
    
    def _select_optimal_challenge_type(self, user_data: Dict, persona: Dict) -> str:
        """Выбирает оптимальный тип челленджа"""
        
        # Анализируем слабые места
        water_ratio = user_data.get("water_days", 0) / 30
        activity_ratio = user_data.get("activity_days", 0) / 30
        weight_ratio = user_data.get("weight_days", 0) / 30
        
        if water_ratio < 0.5:
            return "water"
        elif activity_ratio < 0.5:
            return "activity"
        elif weight_ratio < 0.5:
            return "weight"
        else:
            return "nutrition"
    
    def _add_base_achievements(self, personalized: List[Dict]) -> List[Dict]:
        """Добавляет базовые достижения к персонализированным"""
        # Добавляем несколько базовых достижений
        base_ids = ["first_week", "hydration_master"]
        base_achievements = [a for a in self.achievement_templates if a["id"] in base_ids]
        
        return base_achievements + personalized[:3]  # Максимум 5 достижений
    
    def _get_starter_achievements(self) -> List[Dict]:
        """Возвращает достижения для новичков"""
        return [
            self.achievement_templates[0],  # first_week
            self.achievement_templates[1],  # hydration_master
        ]
    
    def _get_adaptive_achievements(self, user_data: Dict) -> List[Dict]:
        """Возвращает адаптивные достижения"""
        if user_data.get("streak_days", 0) >= 7:
            return [a for a in self.achievement_templates if a["category"] == "consistency"]
        else:
            return [a for a in self.achievement_templates if a["difficulty"] == "easy"]
    
    def _get_template_challenge(self, challenge_type: str) -> Dict[str, Any]:
        """Возвращает шаблонный челлендж"""
        for template in self.challenge_templates:
            if template["category"] == challenge_type:
                return {
                    **template,
                    "user_id": 0,
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                    "progress": 0
                }
        
        return self.challenge_templates[0]  # Default
    
    def _get_default_motivation(self, user_level: Dict, context: str) -> Dict[str, Any]:
        """Возвращает мотивацию по умолчанию"""
        return {
            "motivation_message": f"Ты {user_level['title']}! Продолжай в том же духе! 💪",
            "level_reference": f"Уровень {user_level['level']} — это отличный результат!",
            "progress_tip": "Продолжай вести дневник, чтобы достичь следующего уровня",
            "achievement_preview": "Следующее достижение ждет тебя!",
            "emoji_set": ["💪", "🌟", "🎯"]
        }

# Создаем экземпляр AI-геймификации
ai_gamification = AIGamification()
