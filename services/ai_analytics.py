"""
🔮 AI-аналитик с предсказаниями и инсайтами
✨ Использует Hermes 2 Pro для анализа данных и прогнозов
🎯 Предсказывает вес, мотивацию, рекомендации
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from services.ai_engine_manager import ai
from database.db import get_session
from database.models import User, WaterEntry, Activity, WeightEntry
from sqlalchemy import select, func

logger = logging.getLogger(__name__)

class AIAnalytics:
    """AI-аналитик с предсказаниями"""
    
    def __init__(self):
        self.ai = ai
    
    async def generate_comprehensive_analysis(
        self,
        user_id: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Генерирует комплексный анализ с предсказаниями
        
        Включает:
        - Анализ текущих трендов
        - Предсказание веса на 2 недели
        - Психологические инсайты
        - Персональные рекомендации
        - Мотивационные сообщения
        """
        
        # Собираем данные
        user_data = await self._collect_user_data(user_id, period_days)
        
        if not user_data["has_data"]:
            return {
                "success": False,
                "message": "Недостаточно данных для анализа. Нужны хотя бы 7 дней активности."
            }
        
        # AI-анализ
        analysis_prompt = f"""
        Ты продвинутый аналитик здоровья и нутрициологии. Проанализируй данные пользователя и дай глубокие инсайты.
        
        ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
        {self._format_data_for_ai(user_data)}
        
        Выполни детальный анализ:
        
        1. ТРЕНДЫ АНАЛИЗ:
        - Вес: динамика, скорость изменения, паттерны
        - Питание: калории, БЖУ баланс, регулярность
        - Активность: интенсивность, типы, прогресс
        - Вода: гидратация, паттерны потребления
        
        2. ПРЕДСКАЗАНИЕ ВЕСА:
        - Предскажи вес на 7 и 14 дней вперед
        - Укажи доверительный интервал (± кг)
        - Учитывай текущие тренды и цели
        
        3. ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ:
        - Мотивация: уровень, динамика, риски демотивации
        - Дисциплина: регулярность, adherence к плану
        - Поведенческие паттерны: привычки, проблемные зоны
        
        4. РИСКИ И ВОЗМОЖНОСТИ:
        - Потенциальные риски (срывы, плато, демотивация)
        - Скрытые возможности для улучшения
        - Ключевые точки роста
        
        5. ПЕРСОНАЛИЗИРОВАННЫЕ РЕКОМЕНДАЦИИ:
        - Конкретные действия на ближайшие 2 недели
        - Изменения в питании/активности
        - Мотивационные стратегии
        
        6. МОТИВАЦИОННОЕ СООБЩЕНИЕ:
        - Персональная мотивация на основе анализа
        - Поддержка и воодушевление
        
        Верни структурированный JSON с полным анализом.
        """
        
        try:
            result = await self.ai.process_text(
                prompt=analysis_prompt,
                task_type="json",
                system_prompt="Ты эксперт-аналитик. Возвращай только JSON с детальным анализом."
            )
            
            if result.get("success"):
                response_text = result.get("data", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    ai_analysis = json.loads(json_match.group())
                    
                    # Дополняем реальными данными
                    comprehensive_analysis = {
                        "user_id": user_id,
                        "analysis_period": period_days,
                        "data_summary": user_data["summary"],
                        "ai_insights": ai_analysis,
                        "generated_at": datetime.now().isoformat(),
                        "confidence": "high" if user_data["data_quality"] > 0.7 else "medium"
                    }
                    
                    logger.info(f"🔮 AI analytics completed for user {user_id}")
                    return comprehensive_analysis
                else:
                    logger.warning("🔮 AI analytics format invalid")
                    return self._fallback_analysis(user_data)
            else:
                logger.warning("🔮 AI analytics failed")
                return self._fallback_analysis(user_data)
                
        except Exception as e:
            logger.error(f"🔮 AI analytics error: {e}")
            return self._fallback_analysis(user_data)
    
    async def generate_motivational_message(
        self,
        user_id: int,
        context: str = "general"
    ) -> str:
        """
        Генерирует персонализированное мотивационное сообщение
        
        context: general, achievement, setback, plateau
        """
        
        user_data = await self._collect_user_data(user_id, 7)
        
        prompt = f"""
        Сгенерируй короткое, но мощное мотивационное сообщение для пользователя NutriBuddy.
        
        КОНТЕКСТ: {context}
        
        ДАННЫЕ ЗА ПОСЛЕДНИЕ 7 ДНЕЙ:
        - Вес: {user_data.get('weight_trend', 'стабилен')}
        - Активность: {user_data.get('activity_days', 0)} дней из 7
        - Цель гидратации: {user_data.get('hydration_goal_met', 'неизвестно')}
        
        Правила:
        - Максимальная длина: 200 символов
        - Персонализированное на основе реальных данных
        - Воодушевляющее и поддерживающее
        - Избегай клише
        - Используй эмодзи умеренно
        
        Верни только сообщение без кавычек.
        """
        
        try:
            result = await self.ai.process_text(
                prompt=prompt,
                task_type="conversation",
                system_prompt="Ты мотивационный коуч. Генерируй короткие вдохновляющие сообщения."
            )
            
            if result.get("success"):
                return result.get("data", {}).get("content", "Ты молодец, продолжай в том же духе! 💪")
            
        except Exception as e:
            logger.error(f"Motivation message error: {e}")
        
        # Fallback сообщения
        fallback_messages = {
            "general": "Каждый день — это шаг к твоей цели! 💪",
            "achievement": "Отличный результат! Ты доказал, что можешь! 🎉",
            "setback": "Потерпи, это временно. Большой путь состоит из маленьких шагов! 🌱",
            "plateau": "Плато — это не остановка, а подготовка к прорыву! 🚀"
        }
        
        return fallback_messages.get(context, fallback_messages["general"])
    
    async def predict_weight_change(
        self,
        user_id: int,
        days_ahead: int = 14
    ) -> Dict[str, Any]:
        """
        Предсказывает изменение веса с учетом трендов
        
        Возвращает:
        - Предсказанный вес
        - Доверительный интервал
        - Вероятность достижения цели
        """
        
        user_data = await self._collect_user_data(user_id, 30)
        
        if not user_data["has_data"]:
            return {
                "success": False,
                "message": "Недостаточно данных для предсказания"
            }
        
        prompt = f"""
        Ты эксперт по предсказанию веса на основе данных о питании и активности.
        
        ДАННЫЕ ПОЛЬЗОВАТЕЛЯ (30 дней):
        - Текущий вес: {user_data.get('current_weight', 'неизвестно')} кг
        - Тренд веса: {user_data.get('weight_trend', 'стабилен')}
        - Средние калории: {user_data.get('avg_calories', 'неизвестно')} ккал/день
        - Средняя активность: {user_data.get('avg_activity', 'неизвестно')} мин/день
        - Цель: {user_data.get('goal', 'неизвестно')}
        
        Предскажи вес через {days_ahead} дней.
        
        Верни JSON:
        {{
            "predicted_weight": число,
            "confidence_interval": {{
                "min": число,
                "max": число
            }},
            "probability_of_goal": 0.0-1.0,
            "key_factors": ["факторы влияющие на предсказание"],
            "recommendations": ["рекомендации для достижения цели"]
        }}
        """
        
        try:
            result = await self.ai.process_text(
                prompt=prompt,
                task_type="json",
                system_prompt="Ты предсказательный аналитик. Возвращай только JSON с числовыми предсказаниями."
            )
            
            if result.get("success"):
                response_text = result.get("data", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    prediction = json.loads(json_match.group())
                    
                    return {
                        "success": True,
                        "prediction": prediction,
                        "days_ahead": days_ahead,
                        "based_on_data_days": 30,
                        "generated_at": datetime.now().isoformat()
                    }
            
        except Exception as e:
            logger.error(f"Weight prediction error: {e}")
        
        # Fallback предсказание
        current_weight = user_data.get('current_weight', 70)
        weight_change = user_data.get('weekly_change', 0) * (days_ahead / 7)
        
        return {
            "success": True,
            "prediction": {
                "predicted_weight": round(current_weight + weight_change, 1),
                "confidence_interval": {
                    "min": round(current_weight + weight_change - 1, 1),
                    "max": round(current_weight + weight_change + 1, 1)
                },
                "probability_of_goal": 0.5,
                "key_factors": ["недостаточно данных для точного анализа"],
                "recommendations": ["продолжай вести дневник питания"]
            }
        }
    
    async def _collect_user_data(self, user_id: int, period_days: int) -> Dict[str, Any]:
        """Собирает данные пользователя за период"""
        
        start_date = datetime.now() - timedelta(days=period_days)
        
        async with get_session() as session:
            # Получаем данные пользователя по telegram_id
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"has_data": False, "message": "Пользователь не найден"}
            
            # Используем внутренний ID для запросов к дочерним таблицам
            internal_user_id = user.id
            
            # Вес
            weight_result = await session.execute(
                select(WeightEntry)
                .where(
                    WeightEntry.user_id == internal_user_id,
                    WeightEntry.datetime >= start_date
                )
                .order_by(WeightEntry.datetime.desc())
            )
            weight_entries = weight_result.scalars().all()
            
            # Активность
            activity_result = await session.execute(
                select(Activity)
                .where(
                    Activity.user_id == internal_user_id,
                    Activity.datetime >= start_date
                )
            )
            activities = activity_result.scalars().all()
            
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
            has_data = len(weight_entries) > 0 or len(activities) > 0 or len(water_entries) > 0
            
            if not has_data:
                return {"has_data": False, "message": "Нет данных за период"}
            
            # Сводная статистика
            summary = {
                "weight_entries": len(weight_entries),
                "activities": len(activities),
                "water_entries": len(water_entries),
                "activity_days": len(set(a.datetime.date() for a in activities)),
                "current_weight": weight_entries[0].weight if weight_entries else None,
                "weight_change": weight_entries[0].weight - weight_entries[-1].weight if len(weight_entries) > 1 else 0,
                "total_calories_burned": sum(a.calories_burned for a in activities),
                "total_water": sum(w.amount for w in water_entries)
            }
            
            # Оценка качества данных
            data_quality = min(1.0, (len(weight_entries) + len(activities) + len(water_entries)) / (period_days * 2))
            
            return {
                "has_data": True,
                "data_quality": data_quality,
                "summary": summary,
                "user": {
                    "goal": user.goal,
                    "target_weight": user.target_weight,
                    "daily_calorie_goal": user.daily_calorie_goal
                },
                "weight_trend": self._calculate_weight_trend(weight_entries),
                "avg_activity": sum(a.duration_minutes for a in activities) / max(len(activities), 1),
                "weekly_change": self._calculate_weekly_change(weight_entries)
            }
    
    def _calculate_weight_trend(self, weight_entries: List[WeightEntry]) -> str:
        """Рассчитывает тренд веса"""
        if len(weight_entries) < 3:
            return "недостаточно данных"
        
        recent = weight_entries[:3]
        older = weight_entries[3:6] if len(weight_entries) > 5 else weight_entries[-3:]
        
        recent_avg = sum(w.weight for w in recent) / len(recent)
        older_avg = sum(w.weight for w in older) / len(older)
        
        diff = recent_avg - older_avg
        
        if diff > 0.5:
            return "растет"
        elif diff < -0.5:
            return "снижается"
        else:
            return "стабилен"
    
    def _calculate_weekly_change(self, weight_entries: List[WeightEntry]) -> float:
        """Рассчитывает изменение веса за неделю"""
        if len(weight_entries) < 2:
            return 0.0
        
        days_diff = (weight_entries[0].datetime - weight_entries[-1].datetime).days
        weight_diff = weight_entries[0].weight - weight_entries[-1].weight
        
        return (weight_diff / days_diff) * 7 if days_diff > 0 else 0.0
    
    def _format_data_for_ai(self, user_data: Dict) -> str:
        """Форматирует данные для AI"""
        summary = user_data.get("summary", {})
        user_info = user_data.get("user", {})
        
        return f"""
        Пользователь:
        - Цель: {user_info.get('goal', 'неизвестно')}
        - Целевой вес: {user_info.get('target_weight', 'неизвестно')} кг
        - Цель по калориям: {user_info.get('daily_calorie_goal', 'неизвестно')} ккал
        
        Данные за период:
        - Записей веса: {summary.get('weight_entries', 0)}
        - Текущий вес: {summary.get('current_weight', 'неизвестно')} кг
        - Изменение веса: {summary.get('weight_change', 0):.1f} кг
        - Тренд веса: {user_data.get('weight_trend', 'стабилен')}
        
        Активность:
        - Дней с активностью: {summary.get('activity_days', 0)}
        - Всего активностей: {summary.get('activities', 0)}
        - Сожжено калорий: {summary.get('total_calories_burned', 0)}
        - Средняя длительность: {user_data.get('avg_activity', 0):.0f} минут
        
        Гидратация:
        - Записей воды: {summary.get('water_entries', 0)}
        - Всего выпито: {summary.get('total_water', 0)} мл
        
        Качество данных: {user_data.get('data_quality', 0):.1%}
        """
    
    def _fallback_analysis(self, user_data: Dict) -> Dict[str, Any]:
        """Fallback анализ если AI недоступен"""
        summary = user_data.get("summary", {})
        
        return {
            "success": True,
            "analysis_type": "basic",
            "trends": {
                "weight": user_data.get("weight_trend", "стабилен"),
                "weekly_change": user_data.get("weekly_change", 0)
            },
            "recommendations": [
                "Продолжай вести дневник питания",
                "Увеличь регулярность записей",
                "Следи за гидратацией"
            ],
            "motivation": "Ты на правильном пути! Продолжай в том же духе.",
            "confidence": "low"
        }

# Создаем экземпляр AI-аналитика
ai_analytics = AIAnalytics()
