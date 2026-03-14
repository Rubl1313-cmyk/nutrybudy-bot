"""
🧠 Улучшенный AI-калькулятор нутриентов NutriBuddy
✨ Динамическая корректировка норм на основе прогресса
🎯 Персонализированные рекомендации с учетом множества факторов
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from services.ai_engine_manager import ai
from database.db import get_session
from database.models import User, Meal, WeightEntry, Activity

logger = logging.getLogger(__name__)

class EnhancedNutritionCalculator:
    """Улучшенный AI-калькулятор с динамической адаптацией"""
    
    def __init__(self):
        self.ai = ai
    
    async def calculate_personalized_norms(
        self,
        user_id: int,
        additional_context: Dict = None
    ) -> Dict:
        """
        Расчет персонализированных норм с AI
        
        Учитывает:
        - Базовые параметры (возраст, пол, рост, вес)
        - Динамику веса (тренд за последние 2 недели)
        - Уровень активности (из записей)
        - Климатические факторы
        - Физиологические факторы (сон, стресс)
        """
        
        # Получаем данные пользователя
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return self._get_default_norms()
        
        # Получаем динамику веса за последние 2 недели
        weight_trend = await self._get_weight_trend(user_id, days=14)
        
        # Получаем среднюю активность за последнюю неделю
        activity_level = await self._calculate_activity_level(user_id)
        
        # Формируем контекст для AI
        context = {
            "user_profile": {
                "age": user.age,
                "gender": user.gender,
                "height_cm": user.height_cm,
                "weight_kg": user.weight_kg,
                "goal": user.goal,
                "activity_level": user.activity_level
            },
            "weight_trend": weight_trend,
            "recent_activity": activity_level,
            "additional_context": additional_context or {}
        }
        
        prompt = f"""
        Ты - эксперт по нутрициологии и физиологии. Рассчитай персонализированные нормы питания.
        
        📊 ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
        {self._format_user_data(context)}
        
        🧠 ФАКТОРЫ УЧЕТА:
        
        1. **Базовый метаболизм (BMR):**
           - Используй формулу Mifflin-St Jeor как основу
           - Корректируй с учетом индивидуальных особенностей
           
        2. **Динамика веса:**
           - Потеря веса > 1 кг/неделю: увеличить калории на 10-15%
           - Набор веса > 0.5 кг/неделю: уменьшить калории на 5-10%
           - Стабильный вес: оставить текущие нормы
           
        3. **Уровень активности:**
           - Высокая активность: +300-500 ккал к норме
           - Низкая активность: -200 ккал от нормы
           
        4. **Цели пользователя:**
           - Похудение: дефицит 15-20% от TDEE
           - Набор массы: профицит 10-15% от TDEE
           - Поддержание: равенство с TDEE
           
        5. **Физиологические факторы:**
           - Плохой сон (<6 часов): +100-200 ккал
           - Высокий стресс: +50-150 ккал
           - Менструальный цикл (женщины): +100-300 ккал в лютеиновую фазу
           
        6. **Возрастные корректировки:**
           - До 25 лет: +5% к базовому метаболизму
           - 25-40 лет: базовый метаболизм
           - 40-55 лет: -5% к базовому метаболизму
           - Старше 55 лет: -10% к базовому метаболизму
           
        📋 ВЕРНИ JSON:
        {{
            "bmr": базовый метаболизм в ккал,
            "tdee": общие суточные затраты в ккал,
            "daily_calories": рекомендованные калории,
            "protein_g": белки в граммах,
            "fat_g": жиры в граммах,
            "carbs_g": углеводы в граммах,
            "water_ml": вода в миллилитрах,
            "confidence": 0-100,
            "adjustments": {{
                "weight_trend": "описание корректировки по весу",
                "activity_level": "описание корректировки по активности",
                "physiological": "описание корректировки по физиологии"
            }},
            "recommendations": [
                "персонализированная рекомендация 1",
                "персонализированная рекомендация 2"
            ]
        }}
        
        Примеры корректировок:
        - Пользователь худеет слишком быстро -> "Увеличьте калории на 200 ккал для безопасного похудения"
        - Высокая активность -> "Добавьте 300 ккал для восполнения энергии"
        - Плохой сон -> "Рекомендуем добавить 150 ккал и улучшить режим сна"
        """
        
        try:
            result = await ai.process_text(prompt, task_type="json", system_prompt="You are nutrition calculation expert. Return JSON only.")
            
            logger.info(f"🧠 Nutrition AI result success: {result.get('success', False)}")
            
            if result.get("success"):
                response_data = result.get("data", {})
                
                # Упрощённое извлечение JSON - ожидаем что AI вернёт JSON строку
                if isinstance(response_data, dict):
                    if "content" in response_data:
                        content = response_data.get("content")
                        # Если content это dict, это уже JSON структура
                        if isinstance(content, dict):
                            logger.info(f"🧠 Nutrition AI returned dict with keys: {list(content.keys())}")
                            return content
                        else:
                            # Иначе пробуем распарсить как JSON строку
                            try:
                                import json
                                parsed_data = json.loads(content)
                                logger.info(f"🧠 Nutrition parsed JSON successfully")
                                return parsed_data
                            except json.JSONDecodeError:
                                logger.warning("🧠 Nutrition response is not valid JSON, using as text")
                                return {"error": "Invalid JSON response"}
                    else:
                        return response_data
                else:
                    return {"error": "Invalid response format"}
            
            # Валидация и корректировка экстремальных значений
            parsed_data = self._validate_norms(content, user)
            
            calories = parsed_data.get('daily_calories', 0)
            logger.info(f"🧠 Enhanced AI nutrition calculated: {calories} ккал")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"🧠 Nutrition JSON decode error: {e}")
            return {"error": "JSON decode error"}
        except Exception as e:
            logger.error(f"🧠 Enhanced AI nutrition calculator error: {e}")
            return self._get_default_norms()
                
        except Exception as e:
            logger.error(f"🧠 Enhanced AI nutrition calculator error: {e}")
            return self._get_default_norms()
    
    async def analyze_progress_and_adjust(
        self,
        user_id: int,
        period_days: int = 7
    ) -> Dict:
        """
        Анализ прогресса и динамическая корректировка норм
        """
        
        # Получаем статистику за период
        stats = await self._get_period_stats(user_id, period_days)
        
        # Получаем текущие нормы
        current_norms = await self.calculate_personalized_norms(user_id)
        
        prompt = f"""
        Ты - спортивный аналитик и нутрициолог. Проанализируй прогресс и скорректируй нормы.
        
        📊 ТЕКУЩАЯ СТАТИСТИКА ({period_days} дней):
        {self._format_stats(stats)}
        
        🎯 ТЕКУЩИЕ НОРМЫ:
        {self._format_norms(current_norms)}
        
        🧠 АНАЛИЗ ПРОГРЕССА:
        
        1. **Соответствие калориям:**
           - Фактические vs плановые калории
           - Процент выполнения нормы
           - Стабильность соблюдения
           
        2. **Баланс нутриентов:**
           - Соотношение БЖУ
           - Достаточность белка
           - Качество жиров и углеводов
           
        3. **Прогресс цели:**
           - Динамика веса
           - Изменение в параметрах тела
           - Соответствие цели пользователя
           
        4. **Рекомендации по корректировке:**
           - Если дефицит > 25%: увеличить калории
           - Если профицит > 20%: уменьшить калории
           - Если мало белка: увеличить белок
           - Если мало воды: напомнить о гидратации
           
        📋 ВЕРНИ JSON:
        {{
            "progress_analysis": {{
                "calories_compliance": "процент выполнения калорий",
                "protein_adequacy": "достаточность белка",
                "water_intake": "потребление воды",
                "goal_progress": "прогресс по цели"
            }},
            "adjustments_needed": {{
                "calories": "корректировка калорий (+/- ккал)",
                "protein": "корректировка белка (+/- г)",
                "fat": "корректировка жиров (+/- г)",
                "carbs": "корректировка углеводов (+/- г)",
                "water": "корректировка воды (+/- мл)"
            }},
            "new_norms": {{
                "daily_calories": новые калории,
                "protein_g": новый белок,
                "fat_g": новые жиры,
                "carbs_g": новые углеводы,
                "water_ml": новая вода
            }},
            "recommendations": [
                "рекомендация 1",
                "рекомендация 2"
            ],
            "motivation": "мотивирующее сообщение"
        }}
        """
        
        try:
            result = await ai.process_text(prompt, task_type="json", system_prompt="You are progress analysis expert. Return JSON only.")
            
            if result.get("success"):
                response_data = result.get("data", {})
                
                # Получаем текстовый контент из разных форматов ответа
                if isinstance(response_data, dict):
                    if "content" in response_data:
                        # Если content это dict, берем его как строку
                        content = response_data.get("content")
                        if isinstance(content, dict):
                            # Если content это dict с JSON структурой, используем его напрямую
                            if "daily_calories" in content or "protein" in content or "recommendations" in content:
                                import json
                                response_text = json.dumps(content)  # Конвертируем в JSON строку
                            else:
                                response_text = str(content)
                        else:
                            response_text = str(content)
                    else:
                        response_text = str(response_data)
                else:
                    response_text = str(response_data)
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    try:
                        parsed_data = json.loads(json_match.group())
                        logger.info(f"🧠 Progress analysis completed with adjustments")
                        return parsed_data
                    except json.JSONDecodeError as e:
                        logger.error(f"🧠 Progress analysis JSON decode error: {e}")
                        return {"recommendations": ["Продолжайте в том же духе"]}
            
            return {"recommendations": ["Продолжайте в том же духе"]}
                
        except Exception as e:
            logger.error(f"🧠 Progress analysis error: {e}")
            return {"recommendations": ["Продолжайте в том же духе"]}
    
    async def get_smart_recommendations(
        self,
        user_id: int,
        situation: str,
        context: Dict = None
    ) -> Dict:
        """
        Умные рекомендации на основе ситуации и контекста
        """
        
        # Получаем профиль пользователя
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
        
        user_context = {
            "goal": user.goal if user else "maintain",
            "activity_level": user.activity_level if user else "moderate",
            "current_weight": user.weight_kg if user else 70
        }
        
        prompt = f"""
        Ты - персональный нутрициолог. Дай умные рекомендации для конкретной ситуации.
        
        📤 СИТУАЦИЯ: {situation}
        
        👤 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
        {self._format_user_data({"user_profile": user_context})}
        
        📚 ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ:
        {self._format_context(context)}
        
        🧠 ТИПОВЫЕ СИТУАЦИИ И РЕКОМЕНДАЦИИ:
        
        1. **"Пред тренировкой" (за 1-2 часа):**
           - Легкие углеводы (банан, овсянка)
           - Мало клетчатки и жиров
           - 300-500 ккал
           
        2. **"После тренировки" (в течение 2 часов):**
           - Белок + углеводы (творог, курица, рис)
           - Восстановление мышц
           - 400-600 ккал
           
        3. **"Поздний вечер" (после 20:00):**
           - Легкая белковая пища
           - Минимум углеводов
           - 200-300 ккал
           
        4. **"Загрузочный день" (выходные):**
           - Повышенные калории (+20-30%)
           - Больше углеводов
           - Запасение гликогена
           
        5. **"Разгрузочный день":**
           - Сниженные калории (-30%)
           - Больше белка и овощей
           - Мало жиров и углеводов
           
        6. **"Стрессовый день":**
           - Витамины группы B
           - Магний и калий
           - Умеренные калории
           
        7. **"Жаркая погода":**
           - Больше воды (+500-1000 мл)
           - Легкая пища
           - Электролиты
           
        📋 ВЕРНИ JSON:
        {{
            "situation_type": "тип ситуации",
            "recommendations": [
                {{
                    "category": "еда|напитки|время|количество",
                    "recommendation": "конкретная рекомендация",
                    "reason": "почему это рекомендуется"
                }}
            ],
            "meal_suggestions": [
                {{
                    "name": "название блюда",
                    "calories": калории,
                    "protein": белки,
                    "carbs": углеводы,
                    "fat": жиры
                }}
            ],
            "timing": "когда применить",
            "duration": "как долго применять",
            "warnings": ["предупреждения если есть"]
        }}
        """
        
        try:
            result = await ai.process_text(prompt, task_type="json", system_prompt="You are nutrition expert. Return JSON only.")
            
            if result.get("success"):
                response_data = result.get("data", {})
                
                # Получаем текстовый контент из разных форматов ответа
                if isinstance(response_data, dict):
                    if "content" in response_data:
                        # Если content это dict, берем его как строку
                        content = response_data.get("content")
                        if isinstance(content, dict):
                            # Если content это dict с JSON структурой, используем его напрямую
                            if "daily_calories" in content or "protein" in content or "recommendations" in content:
                                import json
                                response_text = json.dumps(content)  # Конвертируем в JSON строку
                            else:
                                response_text = str(content)
                        else:
                            response_text = str(content)
                    else:
                        response_text = str(response_data)
                else:
                    response_text = str(response_data)
                
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    import json
                    try:
                        parsed_data = json.loads(json_match.group())
                        logger.info(f"🧠 Smart recommendations generated for {situation}")
                        return parsed_data
                    except json.JSONDecodeError as e:
                        logger.error(f"🧠 Smart recommendations JSON decode error: {e}")
                        return self._get_default_recommendations(situation)
            
            return self._get_default_recommendations(situation)
                
        except Exception as e:
            logger.error(f"🧠 Smart recommendations error: {e}")
            return {"recommendations": ["Пейте достаточно воды и следите за сбалансированным питанием"]}
    
    def _get_default_recommendations(self, situation: str) -> Dict:
        """Возвращает рекомендации по умолчанию"""
        if situation == "pre_workout":
            return {
                "recommendations": [
                    "Легкий перекус за 1-2 часа до тренировки",
                    "Банан или горсть орехов",
                    "Избегайте жирной пищи перед тренировкой"
                ],
                "timing": "За 1-2 часа до",
                "duration": "Непосредственно перед тренировкой",
                "warnings": ["Не переедайте"]
            }
        elif situation == "post_workout":
            return {
                "recommendations": [
                    "Белковый прием в течение 30 минут после тренировки",
                    "Восстановление жидкости",
                    "Сложные углеводы для восполнения энергии"
                ],
                "timing": "В течение 30 минут",
                "duration": "2-3 часа после тренировки",
                "warnings": ["Не голодайте после тренировки"]
            }
        else:
            return {
                "recommendations": [
                    "Пейте достаточно воды и следите за сбалансированным питанием",
                    "Регулярные приемы пищи",
                    "Контролируйте размер порций"
                ],
                "timing": "Ежедневно",
                "duration": "Постоянно",
                "warnings": ["Проконсультируйтесь с врачом"]
            }
    
    async def _get_weight_trend(self, user_id: int, days: int) -> Dict:
        """Получает тренд веса за период"""
        async with get_session() as session:
            # Получаем внутренний ID пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"trend": "stable", "change_kg": 0}
            
            from datetime import datetime, timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            result = await session.execute(
                select(WeightEntry)
                .where(WeightEntry.user_id == user.id)
                .where(WeightEntry.datetime >= start_date)
                .order_by(WeightEntry.datetime.desc())
            )
            entries = result.scalars().all()
            
            if len(entries) < 2:
                return {"trend": "insufficient_data", "change_kg": 0}
            
            weights = [entry.weight for entry in entries]
            first_weight = weights[-1]
            last_weight = weights[0]
            change = last_weight - first_weight
            
            if abs(change) < 0.5:
                trend = "stable"
            elif change > 0:
                trend = "gaining"
            else:
                trend = "losing"
            
            return {
                "trend": trend,
                "change_kg": round(change, 1),
                "change_per_week": round(change / (days / 7), 1),
                "entries_count": len(entries)
            }
    
    async def _calculate_activity_level(self, user_id: int) -> Dict:
        """Рассчитывает фактический уровень активности"""
        async with get_session() as session:
            # Получаем внутренний ID пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"level": "unknown", "daily_calories_burned": 0}
            
            from datetime import datetime, timedelta
            start_date = datetime.now() - timedelta(days=7)
            
            result = await session.execute(
                select(Activity)
                .where(Activity.user_id == user.id)
                .where(Activity.datetime >= start_date)
            )
            activities = result.scalars().all()
            
            total_calories = sum(activity.calories_burned for activity in activities)
            daily_average = total_calories / 7
            
            # Классификация уровня активности
            if daily_average < 200:
                level = "sedentary"
            elif daily_average < 400:
                level = "light"
            elif daily_average < 600:
                level = "moderate"
            elif daily_average < 800:
                level = "active"
            else:
                level = "very_active"
            
            return {
                "level": level,
                "daily_calories_burned": round(daily_average),
                "weekly_total": total_calories,
                "activities_count": len(activities)
            }
    
    async def _get_period_stats(self, user_id: int, days: int) -> Dict:
        """Получает статистику за период"""
        async with get_session() as session:
            # Получаем внутренний ID пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {}
            
            from datetime import datetime, timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            # Статистика питания
            meals_result = await session.execute(
                select(Meal)
                .where(Meal.user_id == user.id)
                .where(Meal.datetime >= start_date)
            )
            meals = meals_result.scalars().all()
            
            total_calories = sum(meal.calories for meal in meals)
            total_protein = sum(meal.protein for meal in meals)
            total_fat = sum(meal.fat for meal in meals)
            total_carbs = sum(meal.carbs for meal in meals)
            
            return {
                "period_days": days,
                "meals_count": len(meals),
                "total_calories": total_calories,
                "daily_average_calories": total_calories / days,
                "total_protein": total_protein,
                "total_fat": total_fat,
                "total_carbs": total_carbs,
                "daily_average_protein": total_protein / days,
                "daily_average_fat": total_fat / days,
                "daily_average_carbs": total_carbs / days
            }
    
    def _format_user_data(self, data: Dict) -> str:
        """Форматирует данные пользователя для промпта"""
        if not data:
            return "Данные отсутствуют"
        
        formatted = []
        for key, value in data.items():
            if isinstance(value, dict):
                formatted.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    formatted.append(f"  {sub_key}: {sub_value}")
            else:
                formatted.append(f"{key}: {value}")
        
        return '\n'.join(formatted)
    
    def _format_stats(self, stats: Dict) -> str:
        """Форматирует статистику для промпта"""
        if not stats:
            return "Статистика отсутствует"
        
        formatted = []
        for key, value in stats.items():
            if isinstance(value, float):
                formatted.append(f"{key}: {value:.1f}")
            else:
                formatted.append(f"{key}: {value}")
        
        return '\n'.join(formatted)
    
    def _format_norms(self, norms: Dict) -> str:
        """Форматирует нормы для промпта"""
        if not norms:
            return "Нормы отсутствуют"
        
        formatted = []
        key_fields = ['daily_calories', 'protein_g', 'fat_g', 'carbs_g', 'water_ml']
        
        for key in key_fields:
            if key in norms:
                value = norms[key]
                if isinstance(value, float):
                    formatted.append(f"{key}: {value:.1f}")
                else:
                    formatted.append(f"{key}: {value}")
        
        return '\n'.join(formatted)
    
    def _format_context(self, context: Dict) -> str:
        """Форматирует контекст для промпта"""
        if not context:
            return "Контекст отсутствует"
        
        formatted = []
        for key, value in context.items():
            formatted.append(f"{key}: {value}")
        
        return '\n'.join(formatted)
    
    def _validate_norms(self, norms: Dict, user: User) -> Dict:
        """Валидирует и корректирует нормы"""
        # Минимальные и максимальные значения
        min_calories = 800
        max_calories = 10000
        
        calories = norms.get('daily_calories', 2000)
        if calories < min_calories:
            norms['daily_calories'] = min_calories
        elif calories > max_calories:
            norms['daily_calories'] = max_calories
        
        # Корректировка БЖУ пропорций
        protein = norms.get('protein_g', 50)
        fat = norms.get('fat_g', 65)
        carbs = norms.get('carbs_g', 250)
        
        # Проверка суммарных калорий от БЖУ
        protein_calories = protein * 4
        fat_calories = fat * 9
        carbs_calories = carbs * 4
        total_macro_calories = protein_calories + fat_calories + carbs_calories
        
        # Если расхождение больше 10%, корректируем
        if abs(total_macro_calories - calories) > calories * 0.1:
            factor = calories / total_macro_calories
            norms['protein_g'] = round(protein * factor)
            norms['fat_g'] = round(fat * factor)
            norms['carbs_g'] = round(carbs * factor)
        
        return norms
    
    def _get_default_norms(self) -> Dict:
        """Возвращает нормы по умолчанию"""
        return {
            "bmr": 1500,
            "tdee": 2000,
            "daily_calories": 2000,
            "protein_g": 75,
            "fat_g": 65,
            "carbs_g": 250,
            "water_ml": 2000,
            "confidence": 75,  # Увеличиваем confidence
            "adjustments": {},
            "recommendations": ["Проконсультируйтесь с нутрициологом для персонализации"]
        }

# Создаем экземпляр улучшенного калькулятора
enhanced_nutrition_calculator = EnhancedNutritionCalculator()
