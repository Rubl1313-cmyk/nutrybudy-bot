"""
📊 AI-аналитик прогресса NutriBuddy
✨ Умный анализ трендов и персонализированные рекомендации
🎯 Психологическая мотивация и предсказание результатов
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from services.ai_engine_manager import ai

logger = logging.getLogger(__name__)

class AIProgressAnalyzer:
    """AI-аналитик для умного анализа прогресса"""
    
    def __init__(self):
        self.ai = ai
    
    async def analyze_progress_trends(
        self,
        user_data: Dict,
        period: str = "week"
    ) -> Dict:
        """
        AI-анализ трендов прогресса
        
        Анализирует:
        - Тенденции веса и активности
        - Паттерны поведения
        - Эффективность стратегии
        - Психологические барьеры
        - Предсказания будущих результатов
        """
        
        prompt = f"""
        Ты спортивный психолог и аналитик данных. Проанализируй прогресс пользователя за {period}:

        📊 ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
        {self._format_user_data(user_data)}
        
        🧠 НУЖНО ПРОАНАЛИЗИРОВАТЬ:
        1. Тренды веса (динамика, скорость изменений)
        2. Паттерны питания (регулярность, калорийность)
        3. Активность (соответствие целям, прогресс)
        4. Психологические аспекты (мотивация, дисциплина)
        5. Эффективность текущей стратегии
        6. Риски и потенциальные проблемы
        7. Предсказания на ближайший период
        
        📋 ВЕРНИ JSON:
        {{
            "trend_analysis": {{
                "weight_trend": "растет|падает|стабилен",
                "weight_velocity": "скорость изменения кг/нед",
                "calorie_trend": "избыток|дефицит|норма",
                "activity_trend": "улучшается|стабилен|ухудшается"
            }},
            "behavior_patterns": {{
                "eating_consistency": "регулярно|нерегулярно|пропуски",
                "weekend_effect": "есть|нет",
                "stress_eating": "присутствует|отсутствует",
                "activity_pattern": "утро/вечер/случайно"
            }},
            "psychology_insights": {{
                "motivation_level": "высокая|средняя|низкая",
                "discipline_score": 0-100,
                "potential_burnout": "риск|стабильно|хорошо",
                "success_factors": ["факторы успеха"],
                "barriers": ["препятствия"]
            }},
            "strategy_effectiveness": {{
                "current_plan_score": 0-100,
                "what_works": ["что работает"],
                "what_doesnt": ["что не работает"],
                "optimization_suggestions": ["предложения по оптимизации"]
            }},
            "predictions": {{
                "next_week_weight": "прогноз веса",
                "confidence_level": 0-100,
                "risk_factors": ["факторы риска"],
                "success_probability": 0-100
            }},
            "recommendations": {{
                "immediate_actions": ["немедленные действия"],
                "weekly_focus": ["фокус на неделю"],
                "motivation_boosters": ["мотиваторы"],
                "prevention_measures": ["профилактика проблем"]
            }},
            "achievements": {{
                "milestones_reached": ["достигнутые цели"],
                "new_records": ["новые рекорды"],
                "consistency_streak": "дни подряд"
            }}
        }}
        
        Будь объективным, но мотивирующим. Используй психологические подходы.
        """
        
        try:
            result = await self.ai.process_ai_assistant(prompt)
            
            if result.get("success"):
                response_text = result.get("response", "")
                
                # Извлекаем JSON
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    ai_analysis = json.loads(json_match.group())
                    
                    # Валидация и обогащение
                    validated_analysis = self._validate_analysis(ai_analysis, user_data)
                    
                    logger.info(f"📊 AI progress analysis completed")
                    return validated_analysis
                else:
                    logger.warning("📊 AI analysis format invalid")
                    return self._fallback_analysis(user_data)
            else:
                logger.warning("📊 AI analysis failed")
                return self._fallback_analysis(user_data)
                
        except Exception as e:
            logger.error(f"📊 AI analyzer error: {e}")
            return self._fallback_analysis(user_data)
    
    async def generate_motivational_insight(
        self,
        user_profile: Dict,
        recent_progress: Dict,
        struggle_areas: List[str]
    ) -> Dict:
        """
        Генерация персонализированной мотивации
        
        Создает:
        - Психологическую поддержку
        - Индивидуальную мотивацию
        - Преодоление барьеров
        - Целеполагание
        """
        
        prompt = f"""
        Ты мотивационный коуч и психолог. Создай персонализированную мотивацию для пользователя:

        👤 ПРОФИЛЬ:
        - Имя: {user_profile.get('first_name', 'Пользователь')}
        - Цель: {user_profile.get('goal', 'не указана')}
        - Достижения: {recent_progress.get('achievements', [])}
        - Текущие проблемы: {struggle_areas}

        📊 ПОСЛЕДНИЙ ПРОГРЕСС:
        {self._format_progress(recent_progress)}

        🧠 СОЗДАЙ:
        1. Эмоциональную поддержку и признание усилий
        2. Анализ конкретных проблем и решений
        3. Персонализированную мотивацию
        4. Конкретные шаги для улучшения
        5. Позитивное видение будущего

        📋 ВЕРНИ JSON:
        {{
            "motivation_type": "поддержка|мотивация|коррекция",
            "emotional_tone": "вдохновляющий|реалистичный|строгий",
            "key_message": "основное сообщение",
            "acknowledgments": ["в чем молодец"],
            "challenge_areas": {{
                "area": "проблема",
                "solution": "решение",
                "encouragement": "поддержка"
            }},
            "action_plan": [
                {{
                    "step": "шаг",
                    "timeline": "срок",
                    "difficulty": "сложность"
                }}
            ],
            "future_vision": "видение будущего",
            "psychology_techniques": ["психологические техники"],
            "success_probability": 0-100,
            "closing_motivation": "финальная мотивация"
        }}
        
        Будь искренним, поддерживающим, но реалистичным.
        """
        
        try:
            result = await self.ai.process_ai_assistant(prompt)
            
            if result.get("success"):
                response_text = result.get("response", "")
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    motivation_data = json.loads(json_match.group())
                    
                    logger.info(f"🧠 AI motivation generated")
                    return motivation_data
                else:
                    logger.warning("🧠 AI motivation format invalid")
                    return self._fallback_motivation(user_profile, struggle_areas)
            else:
                logger.warning("🧠 AI motivation failed")
                return self._fallback_motivation(user_profile, struggle_areas)
                
        except Exception as e:
            logger.error(f"🧠 AI motivation error: {e}")
            return self._fallback_motivation(user_profile, struggle_areas)
    
    def _format_user_data(self, user_data: Dict) -> str:
        """Форматирует данные пользователя для промпта"""
        formatted = []
        
        if 'weight_entries' in user_data:
            weights = user_data['weight_entries'][-7:]  # Последние 7 записей
            formatted.append(f"Вес (последние 7 дней): {weights}")
        
        if 'meals' in user_data:
            calories = [meal.get('total_calories', 0) for meal in user_data['meals'][-7:]]
            avg_calories = sum(calories) / len(calories) if calories else 0
            formatted.append(f"Средняя калорийность: {avg_calories:.0f} ккал/день")
        
        if 'activities' in user_data:
            activities = user_data['activities'][-7:]
            total_activity = sum([act.get('duration_minutes', 0) for act in activities])
            formatted.append(f"Активность: {total_activity} мин за неделю")
        
        if 'water' in user_data:
            water = user_data['water'][-7:]
            total_water = sum([entry.get('amount', 0) for entry in water])
            formatted.append(f"Вода: {total_water} мл за неделю")
        
        return '\n'.join(formatted) if formatted else "Данные отсутствуют"
    
    def _format_progress(self, progress: Dict) -> str:
        """Форматирует прогресс для промпта"""
        formatted = []
        
        if 'weight_change' in progress:
            formatted.append(f"Изменение веса: {progress['weight_change']:.1f} кг")
        
        if 'calorie_average' in progress:
            formatted.append(f"Средние калории: {progress['calorie_average']:.0f} ккал")
        
        if 'activity_total' in progress:
            formatted.append(f"Активность: {progress['activity_total']} мин")
        
        if 'consistency_days' in progress:
            formatted.append(f"Дней подряд: {progress['consistency_days']}")
        
        return '\n'.join(formatted) if formatted else "Прогресс отсутствует"
    
    def _validate_analysis(self, analysis: Dict, user_data: Dict) -> Dict:
        """Валидация AI анализа"""
        # Проверка наличия ключевых полей
        required_keys = ['trend_analysis', 'behavior_patterns', 'psychology_insights']
        
        for key in required_keys:
            if key not in analysis:
                analysis[key] = self._get_default_section(key)
        
        # Корректировка оценок в диапазон 0-100
        if 'psychology_insights' in analysis:
            insights = analysis['psychology_insights']
            if 'discipline_score' in insights:
                insights['discipline_score'] = max(0, min(100, insights['discipline_score']))
        
        return analysis
    
    def _get_default_section(self, section_type: str) -> Dict:
        """Возвращает секцию по умолчанию"""
        defaults = {
            'trend_analysis': {
                'weight_trend': 'стабилен',
                'weight_velocity': 0,
                'calorie_trend': 'норма',
                'activity_trend': 'стабилен'
            },
            'behavior_patterns': {
                'eating_consistency': 'нерегулярно',
                'weekend_effect': 'нет',
                'stress_eating': 'отсутствует',
                'activity_pattern': 'случайно'
            },
            'psychology_insights': {
                'motivation_level': 'средняя',
                'discipline_score': 50,
                'potential_burnout': 'стабильно',
                'success_factors': [],
                'barriers': []
            }
        }
        return defaults.get(section_type, {})
    
    def _fallback_analysis(self, user_data: Dict) -> Dict:
        """Fallback анализ если AI недоступен"""
        return {
            'trend_analysis': {
                'weight_trend': 'стабилен',
                'weight_velocity': 0,
                'calorie_trend': 'норма',
                'activity_trend': 'стабилен'
            },
            'behavior_patterns': {
                'eating_consistency': 'анализ недоступен',
                'weekend_effect': 'неизвестно',
                'stress_eating': 'неизвестно',
                'activity_pattern': 'неизвестно'
            },
            'psychology_insights': {
                'motivation_level': 'средняя',
                'discipline_score': 50,
                'potential_burnout': 'стабильно',
                'success_factors': ['Продолжайте努力'],
                'barriers': ['Недостаточно данных']
            },
            'strategy_effectiveness': {
                'current_plan_score': 70,
                'what_works': ['Регулярное отслеживание'],
                'what_doesnt': ['Недостаточно данных'],
                'optimization_suggestions': ['Увеличьте точность данных']
            },
            'predictions': {
                'next_week_weight': 'Недостаточно данных',
                'confidence_level': 30,
                'risk_factors': ['Непредсказуемость'],
                'success_probability': 70
            },
            'recommendations': {
                'immediate_actions': ['Продолжайте отслеживать'],
                'weekly_focus': ['Сбор точных данных'],
                'motivation_boosters': ['Маленькие победы'],
                'prevention_measures': ['Регулярность']
            },
            'achievements': {
                'milestones_reached': [],
                'new_records': [],
                'consistency_streak': 0
            }
        }
    
    def _fallback_motivation(self, user_profile: Dict, struggle_areas: List[str]) -> Dict:
        """Fallback мотивация если AI недоступен"""
        return {
            'motivation_type': 'поддержка',
            'emotional_tone': 'реалистичный',
            'key_message': 'Продолжайте двигаться к своей цели',
            'acknowledgments': ['Вы прилагаете усилия'],
            'challenge_areas': {
                'area': struggle_areas[0] if struggle_areas else 'Неизвестно',
                'solution': 'Регулярность и последовательность',
                'encouragement': 'Каждый шаг важен'
            },
            'action_plan': [
                {
                    'step': 'Продолжайте отслеживать прогресс',
                    'timeline': 'Ежедневно',
                    'difficulty': 'Средняя'
                }
            ],
            'future_vision': 'Ваше упорство приведет к результатам',
            'psychology_techniques': ['Постановка малых целей'],
            'success_probability': 75,
            'closing_motivation': 'Вы способны достичь своей цели!'
        }

# Создаем экземпляр AI аналитика
ai_analyzer = AIProgressAnalyzer()
