"""
🎨 AI-персонализатор контента NutriBuddy
✨ Адаптирует контент под пользователя в реальном времени
🎯 Персонализирует сообщения, рекомендации, интерфейс
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from services.ai_engine_manager import ai
from database.db import get_session
from database.models import User, WaterEntry, Activity, WeightEntry
from sqlalchemy import select

logger = logging.getLogger(__name__)

class AIPersonalizer:
    """AI-персонализатор контента"""
    
    def __init__(self):
        self.ai = ai
        self.persona_cache = {}  # Кэш персон на 24 часа
    
    async def get_user_persona(self, user_id: int) -> Dict[str, Any]:
        """
        Создает персонализированный профиль пользователя
        
        Включает:
        - Психологический портрет
        - Поведенческие паттерны
        - Мотивационные триггеры
        - Коммуникационный стиль
        - Предпочтения в контенте
        """
        
        # Проверяем кэш
        if user_id in self.persona_cache:
            cached = self.persona_cache[user_id]
            if (datetime.now() - cached["created_at"]).total_seconds() < 86400:  # 24 часа
                return cached["persona"]
        
        # Собираем данные для анализа
        user_data = await self._collect_persona_data(user_id)
        
        if not user_data["has_data"]:
            return self._create_default_persona()
        
        # AI-анализ для создания персоны
        persona_prompt = f"""
        Ты психолог-аналитик и эксперт по коммуникации. Создай детальный психологический портрет пользователя NutriBuddy.
        
        ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
        {self._format_persona_data(user_data)}
        
        Проанализируй и создай персонализированный профиль:
        
        1. ПСИХОЛОГИЧЕСКИЙ ПОРТРЕТ:
        - Тип личности (аналитик, творческий, практик, социал)
        - Уровень самодисциплины (1-10)
        - Мотивационный тип (внутренний, внешний, смешанный)
        - Отношение к правилам и структуре
        - Стрессоустойчивость
        
        2. ПОВЕДЕНЧЕСКИЕ ПАТТЕРНЫ:
        - Регулярность использования приложения
        - Предпочитаемое время активности
        - Типы записей (подробные, краткие, регулярные)
        - Реакция на достижения/неудачи
        
        3. МОТИВАЦИОННЫЕ ТРИГГЕРЫ:
        - Что мотивирует (цифры, прогресс, похвала, соревнование)
        - Что демотивирует (рутинность, медленный прогресс, критика)
        - Лучший формат обратной связи
        
        4. КОММУНИКАЦИОННЫЙ СТИЛЬ:
        - Предпочитаемый тон (формальный, дружелюбный, мотивирующий)
        - Длина сообщений (краткие, подробные)
        - Использование эмодзи и юмора
        - Восприимчивость к разным типам контента
        
        5. ПРЕДПОЧТЕНИЯ КОНТЕНТА:
        - Формат рекомендаций (текст, списки, таблицы, инфографика)
        - Частота напоминаний
        - Типы советов (практические, мотивирующие, образовательные)
        - Интересующие темы (рецепты, тренировки, психология)
        
        6. ПЕРСОНАЛИЗИРОВАННЫЙ ПОДХОД:
        - Ключевые слова и фразы для коммуникации
        - Избегаемые темы и выражения
        - Оптимальное время для коммуникации
        - Стратегия удержания мотивации
        
        Верни детальный JSON с полным профилем персоны.
        """
        
        try:
            result = await self.ai.process_text(
                prompt=persona_prompt,
                task_type="json",
                system_prompt="Ты психолог-аналитик. Создавай точные и полезные профили личности."
            )
            
            if result.get("success"):
                response_text = result.get("data", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    persona = json.loads(json_match.group())
                    
                    # Сохраняем в кэш
                    self.persona_cache[user_id] = {
                        "persona": persona,
                        "created_at": datetime.now()
                    }
                    
                    logger.info(f"🎨 Persona created for user {user_id}")
                    return persona
            
        except Exception as e:
            logger.error(f"Persona creation error: {e}")
        
        return self._create_default_persona()
    
    async def personalize_message(
        self,
        user_id: int,
        base_message: str,
        message_type: str = "general"
    ) -> str:
        """
        Персонализирует сообщение под пользователя
        
        message_type: motivation, recommendation, reminder, achievement, education
        """
        
        persona = await self.get_user_persona(user_id)
        
        personalization_prompt = f"""
        Адаптируй сообщение под психологический профиль пользователя.
        
        БАЗОВОЕ СООБЩЕНИЕ:
        {base_message}
        
        ТИП СООБЩЕНИЯ: {message_type}
        
        ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
        - Тип личности: {persona.get('personality_type', 'неизвестен')}
        - Коммуникационный стиль: {persona.get('communication_style', 'нейтральный')}
        - Мотивационные триггеры: {', '.join(persona.get('motivation_triggers', []))}
        - Предпочитаемый тон: {persona.get('preferred_tone', 'дружелюбный')}
        - Восприимчивость к эмодзи: {persona.get('emoji_tolerance', 'умеренная')}
        
        Правила адаптации:
        1. Используй предпочитаемый тон и стиль
        2. Включи мотивационные триггеры пользователя
        3. Адаптируй длину и сложность сообщения
        4. Используй подходящее количество эмодзи
        5. Учитывай психологические особенности
        
        Верни только адаптированное сообщение без дополнительных объяснений.
        """
        
        try:
            result = await self.ai.process_text(
                prompt=personalization_prompt,
                task_type="conversation",
                system_prompt="Ты мастер персонализации контента. Адаптируй сообщения под индивидуальные особенности."
            )
            
            if result.get("success"):
                return result.get("data", {}).get("content", base_message)
            
        except Exception as e:
            logger.error(f"Message personalization error: {e}")
        
        return base_message
    
    async def generate_personalized_recommendations(
        self,
        user_id: int,
        context: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Генерирует персонализированные рекомендации
        
        context: nutrition, activity, motivation, lifestyle
        """
        
        persona = await self.get_user_persona(user_id)
        user_data = await self._collect_persona_data(user_id)
        
        recommendations_prompt = f"""
        Создай персонализированные рекомендации на основе профиля пользователя.
        
        КОНТЕКСТ: {context}
        
        ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
        {self._format_persona_data(user_data)}
        
        ПСИХОЛОГИЧЕСКИЙ ПОРТРЕТ:
        - Тип личности: {persona.get('personality_type', 'неизвестен')}
        - Уровень дисциплины: {persona.get('discipline_level', 5)}/10
        - Мотивационные триггеры: {', '.join(persona.get('motivation_triggers', []))}
        - Предпочитаемый формат: {persona.get('content_preferences', {}).get('format', 'текст')}
        
        Создай 3-5 персонализированных рекомендаций:
        
        1. Каждая рекомендация должна соответствовать типу личности
        2. Использовать мотивационные триггеры
        3. Быть практической и выполнимой
        4. Учитывать текущий уровень дисциплины
        5. Соответствовать контексту
        
        Верни JSON:
        {{
            "recommendations": [
                {{
                    "title": "краткий заголовок",
                    "description": "подробное описание",
                    "category": "nutrition/activity/motivation/lifestyle",
                    "difficulty": "easy/medium/hard",
                    "priority": "high/medium/low",
                    "personalization_note": "почему это подходит именно этому пользователю"
                }}
            ]
        }}
        """
        
        try:
            result = await self.ai.process_text(
                prompt=recommendations_prompt,
                task_type="json",
                system_prompt="Ты персональный консультант. Создавай рекомендации, которые действительно сработают."
            )
            
            if result.get("success"):
                response_text = result.get("data", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    recommendations_data = json.loads(json_match.group())
                    
                    return recommendations_data.get("recommendations", [])
            
        except Exception as e:
            logger.error(f"Recommendations generation error: {e}")
        
        return self._get_default_recommendations(context)
    
    async def optimize_communication_timing(self, user_id: int) -> Dict[str, Any]:
        """
        Определяет оптимальное время для коммуникации с пользователем
        """
        
        user_data = await self._collect_persona_data(user_id)
        
        timing_prompt = f"""
        Проанализируй паттерны активности пользователя и определи оптимальное время для коммуникации.
        
        ДАННЫЕ АКТИВНОСТИ:
        {self._format_activity_patterns(user_data)}
        
        Учти:
        - Время суток активности
        - Частоту использования приложения
        - Типы действий в разное время
        - Психологические особенности
        
        Верни JSON:
        {{
            "optimal_times": [
                {{
                    "time": "HH:MM",
                    "day_type": "weekday/weekend",
                    "reason": "почему это время оптимально",
                    "message_types": ["motivation", "reminder", "education"]
                }}
            ],
            "avoid_times": [
                {{
                    "time": "HH:MM",
                    "reason": "почему избегать это время"
                }}
            ],
            "frequency_recommendation": "количество сообщений в день",
            "best_days": ["понедельник", "среда", "пятница"]
        }}
        """
        
        try:
            result = await self.ai.process_text(
                prompt=timing_prompt,
                task_type="json",
                system_prompt="Тайминг-аналитик. Определяй лучшие моменты для коммуникации."
            )
            
            if result.get("success"):
                response_text = result.get("data", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    timing_data = json.loads(json_match.group())
                    
                    return timing_data
            
        except Exception as e:
            logger.error(f"Timing optimization error: {e}")
        
        return self._get_default_timing()
    
    async def _collect_persona_data(self, user_id: int) -> Dict[str, Any]:
        """Собирает данные для создания персоны"""
        
        start_date = datetime.now() - timedelta(days=30)
        
        async with get_session() as session:
            # Получаем данные пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"has_data": False}
            
            # Активность за 30 дней
            activity_result = await session.execute(
                select(Activity)
                .where(
                    Activity.user_id == user_id,
                    Activity.datetime >= start_date
                )
                .order_by(Activity.datetime.desc())
            )
            activities = activity_result.scalars().all()
            
            # Вес за 30 дней
            weight_result = await session.execute(
                select(WeightEntry)
                .where(
                    WeightEntry.user_id == user_id,
                    WeightEntry.datetime >= start_date
                )
                .order_by(WeightEntry.datetime.desc())
            )
            weight_entries = weight_result.scalars().all()
            
            # Вода за 30 дней
            water_result = await session.execute(
                select(WaterEntry)
                .where(
                    WaterEntry.user_id == user_id,
                    WaterEntry.datetime >= start_date
                )
                .order_by(WaterEntry.datetime.desc())
            )
            water_entries = water_result.scalars().all()
            
            # Анализ паттернов
            activity_hours = [a.datetime.hour for a in activities]
            activity_days = [a.datetime.strftime("%A") for a in activities]
            
            return {
                "has_data": True,
                "user_info": {
                    "goal": user.goal,
                    "age": user.age,
                    "gender": user.gender,
                    "activity_level": user.activity_level
                },
                "activity_patterns": {
                    "total_activities": len(activities),
                    "active_days": len(set(activity_days)),
                    "preferred_hours": self._get_most_common_hours(activity_hours),
                    "preferred_days": self._get_most_common_days(activity_days),
                    "avg_duration": sum(a.duration_minutes for a in activities) / max(len(activities), 1)
                },
                "consistency": {
                    "weight_entries": len(weight_entries),
                    "water_entries": len(water_entries),
                    "streak_days": self._calculate_streak_days(activities, weight_entries, water_entries),
                    "regularity_score": self._calculate_regularity(activities, weight_entries, water_entries)
                }
            }
    
    def _get_most_common_hours(self, hours: List[int]) -> List[int]:
        """Возвращает самые частые часы активности"""
        if not hours:
            return [9, 12, 18]  # Default times
        
        from collections import Counter
        hour_counts = Counter(hours)
        return [hour for hour, count in hour_counts.most_common(3)]
    
    def _get_most_common_days(self, days: List[str]) -> List[str]:
        """Возвращает самые частые дни активности"""
        if not days:
            return ["понедельник", "среда", "пятница"]
        
        from collections import Counter
        day_counts = Counter(days)
        return [day for day, count in day_counts.most_common(3)]
    
    def _calculate_streak_days(self, activities, weights, waters) -> int:
        """Рассчитывает текущий стрик (дней подряд)"""
        # Упрощенный расчет
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
    
    def _calculate_regularity(self, activities, weights, waters) -> float:
        """Рассчитывает регулярность (0-1)"""
        total_days = 30
        active_days = len(set(
            [a.datetime.date() for a in activities] +
            [w.datetime.date() for w in weights] +
            [w.datetime.date() for w in waters]
        ))
        
        return min(1.0, active_days / total_days)
    
    def _format_persona_data(self, user_data: Dict) -> str:
        """Форматирует данные для AI"""
        if not user_data.get("has_data"):
            return "Недостаточно данных для анализа"
        
        user_info = user_data.get("user_info", {})
        patterns = user_data.get("activity_patterns", {})
        consistency = user_data.get("consistency", {})
        
        return f"""
        Пользователь:
        - Цель: {user_info.get('goal', 'неизвестно')}
        - Возраст: {user_info.get('age', 'неизвестно')}
        - Пол: {user_info.get('gender', 'неизвестно')}
        - Уровень активности: {user_info.get('activity_level', 'неизвестно')}
        
        Паттерны активности:
        - Всего активностей: {patterns.get('total_activities', 0)}
        - Активных дней: {patterns.get('active_days', 0)}
        - Предпочитаемые часы: {patterns.get('preferred_hours', [])}
        - Предпочитаемые дни: {patterns.get('preferred_days', [])}
        - Средняя длительность: {patterns.get('avg_duration', 0):.0f} минут
        
        Последовательность:
        - Записей веса: {consistency.get('weight_entries', 0)}
        - Записей воды: {consistency.get('water_entries', 0)}
        - Текущий стрик: {consistency.get('streak_days', 0)} дней
        - Регулярность: {consistency.get('regularity_score', 0):.1%}
        """
    
    def _format_activity_patterns(self, user_data: Dict) -> str:
        """Форматирует паттерны активности для AI"""
        patterns = user_data.get("activity_patterns", {})
        
        return f"""
        Часы активности: {patterns.get('preferred_hours', [])}
        Дни активности: {patterns.get('preferred_days', [])}
        Всего активностей: {patterns.get('total_activities', 0)}
        Средняя длительность: {patterns.get('avg_duration', 0):.0f} минут
        """
    
    def _create_default_persona(self) -> Dict[str, Any]:
        """Создает персона по умолчанию"""
        return {
            "personality_type": "универсальный",
            "discipline_level": 5,
            "motivation_triggers": ["прогресс", "достижения", "здоровье"],
            "communication_style": "дружелюбный",
            "preferred_tone": "поддерживающий",
            "emoji_tolerance": "умеренная",
            "content_preferences": {
                "format": "текст",
                "length": "средний",
                "topics": ["питание", "активность"]
            }
        }
    
    def _get_default_recommendations(self, context: str) -> List[Dict[str, Any]]:
        """Возвращает рекомендации по умолчанию"""
        base_recommendations = {
            "nutrition": [
                {
                    "title": "Пейте больше воды",
                    "description": "Начните день со стакана воды для улучшения метаболизма",
                    "category": "nutrition",
                    "difficulty": "easy",
                    "priority": "high"
                }
            ],
            "activity": [
                {
                    "title": "Добавьте 10 минут активности",
                    "description": "Короткая прогулка после еды улучшает пищеварение",
                    "category": "activity",
                    "difficulty": "easy",
                    "priority": "medium"
                }
            ],
            "motivation": [
                {
                    "title": "Отмечайте маленькие победы",
                    "description": "Каждый записанный прием пищи — это уже достижение",
                    "category": "motivation",
                    "difficulty": "easy",
                    "priority": "high"
                }
            ]
        }
        
        return base_recommendations.get(context, base_recommendations["motivation"])
    
    def _get_default_timing(self) -> Dict[str, Any]:
        """Возвращает настройки времени по умолчанию"""
        return {
            "optimal_times": [
                {
                    "time": "09:00",
                    "day_type": "weekday",
                    "reason": "Утренняя мотивация на день",
                    "message_types": ["motivation", "reminder"]
                },
                {
                    "time": "18:00",
                    "day_type": "weekday",
                    "reason": "Вечерний обзор дня",
                    "message_types": ["reminder", "education"]
                }
            ],
            "avoid_times": [
                {
                    "time": "06:00",
                    "reason": "Раннее утро"
                },
                {
                    "time": "23:00",
                    "reason": "Позднее вечер"
                }
            ],
            "frequency_recommendation": "2-3 сообщения в день",
            "best_days": ["понедельник", "среда", "пятница"]
        }

# Создаем экземпляр AI-персонализатора
ai_personalizer = AIPersonalizer()
