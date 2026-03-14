"""
🚀 AI Integration Manager - Централизованная система интеграции AI
✨ Объединение всех AI-компонентов в единую систему
🎯 Многозадачная обработка с умной маршрутизацией
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from sqlalchemy import select
from services.enhanced_ai_parser import enhanced_ai_parser
from services.ai_nutrition_calculator_enhanced import enhanced_nutrition_calculator
from services.climate_manager_enhanced import enhanced_climate_manager
from services.ai_engine_manager import ai
from database.db import get_session
from database.models import User, Meal, WeightEntry, Activity

logger = logging.getLogger(__name__)

class AIIntegrationManager:
    """
    Централизованный менеджер интеграции AI
    
    Объединяет:
    - Enhanced AI Parser (улучшенный парсинг)
    - Enhanced Nutrition Calculator (динамические нормы)
    - Enhanced Climate Manager (реальная погода)
    - Multi-task prompting (единая обработка)
    """
    
    def __init__(self):
        self.parser = enhanced_ai_parser
        self.nutrition_calc = enhanced_nutrition_calculator
        self.climate_manager = enhanced_climate_manager
        self.ai = ai
        
        # Регистрируем обработчики для разных задач
        self.task_handlers = {
            'intent_classification': self._handle_intent_classification,
            'food_parsing': self._handle_food_parsing,
            'water_parsing': self._handle_water_parsing,
            'activity_parsing': self._handle_activity_parsing,
            'nutrition_calculation': self._handle_nutrition_calculation,
            'climate_adaptation': self._handle_climate_adaptation,
            'meal_plan': self._handle_meal_plan,
            'multi_task': self._handle_multi_task
        }
    
    async def process_user_input(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None,
        task_type: str = 'auto'
    ) -> Dict:
        """
        Основной метод обработки пользовательского ввода
        
        Args:
            text: текст пользователя
            user_id: ID пользователя
            context: дополнительный контекст
            history: история диалога
            task_type: тип обработки (auto/multi_task/intent/etc.)
        
        Returns:
            {
                "success": bool,
                "task_type": str,
                "result": Dict,
                "actions": List[Dict],
                "response": str,
                "confidence": int,
                "needs_clarification": bool
            }
        """
        
        try:
            logger.info(f"🚀 Processing user input: {text[:50]}...")
            
            # Автоматическое определение типа задачи
            if task_type == 'auto':
                task_type = await self._determine_task_type(text, context, history)
            
            # Получаем соответствующий обработчик
            handler = self.task_handlers.get(task_type, self._handle_fallback)
            
            # Выполняем обработку
            result = await handler(text, user_id, context, history)
            
            # Пост-обработка и обогащение результата
            enriched_result = await self._enrich_result(result, user_id, context)
            
            logger.info(f"🚀 Task {task_type} completed successfully")
            return enriched_result
            
        except Exception as e:
            logger.error(f"🚀 AI Integration Manager error: {e}")
            return {
                "success": False,
                "task_type": task_type,
                "result": {},
                "actions": [],
                "response": "Извините, произошла ошибка при обработке запроса",
                "confidence": 0,
                "needs_clarification": True,
                "error": str(e)
            }
    
    async def get_personalized_recommendations(
        self,
        user_id: int,
        recommendation_type: str,
        context: Dict = None
    ) -> Dict:
        """
        Получает персонализированные рекомендации
        
        Args:
            user_id: ID пользователя
            recommendation_type: тип рекомендаций (nutrition/activity/climate/health)
            context: дополнительный контекст
        
        Returns:
            {
                "success": bool,
                "recommendations": List[Dict],
                "personalization_factors": Dict,
                "confidence": int
            }
        """
        
        try:
            logger.info(f"🚀 Getting personalized recommendations: {recommendation_type}")
            
            # Получаем базовый профиль пользователя
            user_profile = await self._get_user_profile(user_id)
            
            if recommendation_type == 'nutrition':
                result = await self.nutrition_calc.calculate_personalized_norms(user_id, context)
            elif recommendation_type == 'climate':
                city = user_profile.get('city', 'Москва')
                result = await self.climate_manager.get_climate_recommendations(city, user_profile)
            elif recommendation_type == 'activity':
                result = await self._get_activity_recommendations(user_id, context)
            elif recommendation_type == 'health':
                result = await self._get_health_recommendations(user_id, context)
            else:
                result = {"recommendations": ["Тип рекомендаций не поддерживается"]}
            
            return {
                "success": True,
                "recommendations": result.get('recommendations', []),
                "personalization_factors": user_profile,
                "confidence": result.get('confidence', 70)
            }
            
        except Exception as e:
            logger.error(f"🚀 Recommendations error: {e}")
            return {
                "success": False,
                "recommendations": ["Временные технические проблемы"],
                "personalization_factors": {},
                "confidence": 0
            }
    
    async def analyze_progress_and_adapt(
        self,
        user_id: int,
        period_days: int = 7
    ) -> Dict:
        """
        Анализ прогресса и адаптация норм
        
        Args:
            user_id: ID пользователя
            period_days: период анализа в днях
        
        Returns:
            {
                "success": bool,
                "progress_analysis": Dict,
                "adaptations": Dict,
                "new_norms": Dict,
                "recommendations": List[str]
            }
        """
        
        try:
            logger.info(f"🚀 Analyzing progress and adapting norms for user {user_id}")
            
            # Анализируем прогресс
            progress_analysis = await self.nutrition_calc.analyze_progress_and_adjust(user_id, period_days)
            
            # Получаем климатические рекомендации
            user_profile = await self._get_user_profile(user_id)
            city = user_profile.get('city', 'Москва')
            climate_recommendations = await self.climate_manager.get_climate_recommendations(city, user_profile)
            
            # Объединяем рекомендации
            combined_recommendations = self._combine_recommendations(
                progress_analysis.get('recommendations', []),
                climate_recommendations.get('health_tips', [])
            )
            
            return {
                "success": True,
                "progress_analysis": progress_analysis,
                "adaptations": progress_analysis.get('adjustments_needed', {}),
                "new_norms": progress_analysis.get('new_norms', {}),
                "recommendations": combined_recommendations,
                "climate_factors": climate_recommendations.get('climate_analysis', {})
            }
            
        except Exception as e:
            logger.error(f"🚀 Progress analysis error: {e}")
            return {
                "success": False,
                "progress_analysis": {},
                "adaptations": {},
                "new_norms": {},
                "recommendations": ["Произошла ошибка при анализе прогресса"]
            }
    
    async def _determine_task_type(
        self,
        text: str,
        context: Dict = None,
        history: List[str] = None
    ) -> str:
        """
        Автоматическое определение типа задачи
        
        Priority:
        1. Явно указанный тип в контексте
        2. Классификация намерений через AI
        3. Эвристики на основе ключевых слов
        """
        
        # 1. Проверяем контекст
        if context and 'task_type' in context:
            return context['task_type']
        
        # 2. Быстрая классификация через AI
        intent_result = await self.parser.classify_intent_enhanced(text, context, history)
        intent = intent_result.get('intent', 'other')
        
        # 3. Маппинг намерений на типы задач
        task_mapping = {
            'food': 'food_parsing',
            'water': 'water_parsing',
            'activity': 'activity_parsing',
            'steps': 'activity_parsing',
            'weight': 'nutrition_calculation',
            'question': 'multi_task',
            'help': 'multi_task'
        }
        
        return task_mapping.get(intent, 'multi_task')
    
    async def _handle_intent_classification(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None
    ) -> Dict:
        """Обработчик классификации намерений"""
        result = await self.parser.classify_intent_enhanced(text, context, history)
        
        return {
            "success": True,
            "task_type": "intent_classification",
            "result": result,
            "actions": [{"type": "classify_intent", "data": result}],
            "response": self._generate_intent_response(result),
            "confidence": result.get('confidence', 0),
            "needs_clarification": result.get('needs_clarification', False)
        }
    
    async def _handle_food_parsing(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None
    ) -> Dict:
        """Обработчик парсинга еды"""
        result = await self.parser.parse_food_enhanced(text, context)
        
        actions = []
        if result.get('food_items'):
            actions.append({
                "type": "save_food",
                "data": {
                    "food_items": result['food_items'],
                    "meal_type": result.get('meal_type', 'неизвестно')
                }
            })
        
        return {
            "success": True,
            "task_type": "food_parsing",
            "result": result,
            "actions": actions,
            "response": self._generate_food_response(result),
            "confidence": result.get('total_confidence', 0),
            "needs_clarification": result.get('needs_clarification', False)
        }
    
    async def _handle_water_parsing(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None
    ) -> Dict:
        """Обработчик парсинга воды"""
        result = await self.parser.parse_water_enhanced(text, context)
        
        actions = []
        if result.get('amount_ml'):
            actions.append({
                "type": "save_water",
                "data": {
                    "amount_ml": result['amount_ml']
                }
            })
        
        return {
            "success": True,
            "task_type": "water_parsing",
            "result": result,
            "actions": actions,
            "response": self._generate_water_response(result),
            "confidence": result.get('confidence', 0),
            "needs_clarification": result.get('needs_clarification', False)
        }
    
    async def _handle_activity_parsing(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None
    ) -> Dict:
        """Обработчик парсинга активности"""
        result = await self.parser.parse_activity_enhanced(text, context)
        
        actions = []
        if result.get('activity_type'):
            actions.append({
                "type": "save_activity",
                "data": {
                    "activity_type": result['activity_type'],
                    "duration_minutes": result.get('duration_minutes', 30),
                    "intensity": result.get('intensity', 'средняя'),
                    "calories_estimate": result.get('calories_estimate', 200)
                }
            })
        
        return {
            "success": True,
            "task_type": "activity_parsing",
            "result": result,
            "actions": actions,
            "response": self._generate_activity_response(result),
            "confidence": result.get('confidence', 0),
            "needs_clarification": result.get('needs_clarification', False)
        }
    
    async def _handle_nutrition_calculation(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None
    ) -> Dict:
        """Обработчик расчета нутриентов"""
        result = await self.nutrition_calc.calculate_personalized_norms(user_id, context)
        
        return {
            "success": True,
            "task_type": "nutrition_calculation",
            "result": result,
            "actions": [{"type": "update_norms", "data": result}],
            "response": self._generate_nutrition_response(result),
            "confidence": result.get('confidence', 0),
            "needs_clarification": False
        }
    
    async def _handle_climate_adaptation(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None
    ) -> Dict:
        """Обработчик климатической адаптации"""
        user_profile = await self._get_user_profile(user_id)
        city = user_profile.get('city', 'Москва')
        
        result = await self.climate_manager.get_climate_recommendations(city, user_profile)
        
        return {
            "success": True,
            "task_type": "climate_adaptation",
            "result": result,
            "actions": [{"type": "climate_adaptation", "data": result}],
            "response": self._generate_climate_response(result),
            "confidence": 80,
            "needs_clarification": False
        }
    
    async def _handle_multi_task(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None
    ) -> Dict:
        """Обработчик многозадачной обработки"""
        # Используем комбинацию существующих методов парсера
        # Сначала классифицируем намерение
        intent_result = await self.parser.classify_intent_enhanced(text, context, history)
        
        # Затем парсим в зависимости от намерения
        if intent_result.get('intent') == 'food':
            result = await self.parser.parse_food_enhanced(text, context, history)
        elif intent_result.get('intent') == 'water':
            result = await self.parser.parse_water_enhanced(text)
        elif intent_result.get('intent') == 'activity':
            result = await self.parser.parse_activity_enhanced(text)
        else:
            # Для других намерений используем базовый результат
            result = intent_result
        
        # Проверяем что результат не None
        if result is None:
            logger.warning("🚀 Multi-task parse returned None, using fallback")
            result = {
                "intent": "other",
                "confidence": 0,
                "entities": {},
                "response": f"Не удалось обработать запрос: {text}",
                "actions": [],
                "needs_clarification": True
            }
        
        return {
            "success": True,
            "task_type": "multi_task",
            "result": result,
            "actions": result.get('actions', []),
            "response": result.get('response', 'Обработано'),
            "confidence": result.get('confidence', 0),
            "needs_clarification": result.get('needs_clarification', False)
        }
    
    async def _handle_fallback(
        self,
        text: str,
        user_id: int,
        context: Dict = None,
        history: List[str] = None
    ) -> Dict:
        """Fallback обработчик"""
        return {
            "success": False,
            "task_type": "fallback",
            "result": {},
            "actions": [],
            "response": "Извините, не удалось обработать запрос. Попробуйте переформулировать.",
            "confidence": 0,
            "needs_clarification": True
        }
    
    async def _enrich_result(
        self,
        result: Dict,
        user_id: int,
        context: Dict = None
    ) -> Dict:
        """Обогащение результата дополнительной информацией"""
        
        # Добавляем временную метку
        result['timestamp'] = datetime.now().isoformat()
        result['user_id'] = user_id
        
        # Добавляем контекстную информацию
        if context:
            result['context_used'] = True
            result['context_factors'] = list(context.keys())
        
        # Добавляем информацию о конфиденциальности
        if 'confidence' not in result:
            result['confidence'] = 50
        
        # Добавляем информацию о необходимости уточнения
        if 'needs_clarification' not in result:
            result['needs_clarification'] = False
        
        return result
    
    async def _get_user_profile(self, user_id: int) -> Dict:
        """Получает профиль пользователя"""
        try:
            from database.db import get_session
            from database.models import User
            from sqlalchemy import select
            
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if user:
                    return {
                        'age': user.age,
                        'gender': user.gender,
                        'height_cm': user.height,
                        'weight_kg': user.weight,
                        'goal': user.goal,
                        'activity_level': user.activity_level,
                        'city': getattr(user, 'city', 'Москва')
                    }
                else:
                    return {}
        except Exception as e:
            logger.error(f"🚀 Error getting user profile: {e}")
            return {}
    
    async def _get_activity_recommendations(
        self,
        user_id: int,
        context: Dict = None
    ) -> Dict:
        """Получает рекомендации по активности"""
        user_profile = await self._get_user_profile(user_id)
        goal = user_profile.get('goal', 'maintain')
        activity_level = user_profile.get('activity_level', 'moderate')
        
        recommendations = []
        
        if goal == 'lose_weight':
            recommendations.extend([
                "Кардиотренировки 3-4 раза в неделю по 30-45 минут",
                "Силовые тренировки 2-3 раза в неделю",
                "Ежедневная ходьба 8000-10000 шагов"
            ])
        elif goal == 'muscle_gain':
            recommendations.extend([
                "Силовые тренировки 3-4 раза в неделю",
                "Достаточное потребление белка (1.6-2г на кг веса)",
                "Отдых и восстановление между тренировками"
            ])
        else:
            recommendations.extend([
                "Разнообразные виды активности для поддержания формы",
                "Регулярные тренировки 3-4 раза в неделю",
                "Больше движения в повседневной жизни"
            ])
        
        return {
            "recommendations": recommendations,
            "confidence": 80
        }
    
    async def _get_health_recommendations(
        self,
        user_id: int,
        context: Dict = None
    ) -> Dict:
        """Получает рекомендации по здоровью"""
        user_profile = await self._get_user_profile(user_id)
        age = user_profile.get('age', 30)
        
        recommendations = []
        
        if age > 40:
            recommendations.extend([
                "Регулярный контроль холестерина",
                "Достаточное потребление кальция и витамина D",
                "Умеренные кардионагрузки"
            ])
        
        recommendations.extend([
            "Регулярный сон 7-8 часов",
            "Сбалансированное питание",
            "Управление стрессом",
            "Регулярные медицинские осмотры"
        ])
        
        return {
            "recommendations": recommendations,
            "confidence": 75
        }
    
    def _combine_recommendations(
        self,
        recommendations1: List[str],
        recommendations2: List[str]
    ) -> List[str]:
        """Объединяет рекомендации без дублирования"""
        combined = list(set(recommendations1 + recommendations2))
        return combined[:10]  # Ограничиваем количество
    
    def _generate_intent_response(self, result: Dict) -> str:
        """Генерирует ответ для классификации намерений"""
        intent = result.get('intent', 'other')
        confidence = result.get('confidence', 0)
        
        if result.get('needs_clarification'):
            return result.get('clarification', 'Пожалуйста, уточните ваш запрос')
        
        responses = {
            'food': 'Готовлю записать прием пищи',
            'water': 'Готовлю записать потребление воды',
            'activity': 'Готовлю записать активность',
            'steps': 'Готовлю записать шаги',
            'weight': 'Готовлю записать вес',
            'question': 'Готовлю ответить на ваш вопрос',
            'help': 'Готовлю помочь вам'
        }
        
        return responses.get(intent, 'Готовлю помочь вам')
    
    async def _handle_meal_plan(self, text: str, user_id: int, context: Dict = None) -> Dict:
        """Обработка генерации плана питания"""
        try:
            # Получаем профиль пользователя
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    return {
                        "success": False,
                        "error": "Профиль не найден. Создайте профиль командой /set_profile"
                    }
                
                # Формируем промпт для генерации меню
                prompt = f"""
                Составь план питания на день для пользователя:
                - Калорийность: {user.daily_calories or 2000} ккал
                - Цель: {user.goal or 'поддержание веса'}
                - Возраст: {user.age or 30} лет
                - Пол: {user.gender or 'мужской'}
                - Активность: {user.activity_level or 'средняя'}
                - Город: {user.city or 'Москва'}
                
                Используй сезонные продукты и учитывай климатические особенности.
                Для каждого приёма пищи укажи:
                1. Название блюда
                2. Список ингредиентов с калорийностью каждого (на порцию)
                3. Краткое описание приготовления
                4. В конце каждого приёма добавь строку с общей калорийностью
                
                Старайся, чтобы блюда были полезными, вкусными и соответствовали указанной калорийности.
                Используй русский язык и эмодзи. Заверши ответ обязательно.
                """
            
            # Вызываем AI для генерации меню
            response = await self.ai.process_text(prompt, task_type="meal_plan")
            
            if not response.get("success"):
                return {
                    "success": False,
                    "error": f"Ошибка генерации меню: {response.get('error', 'Unknown error')}"
                }
            
            # Правильное извлечение ответа от AI
            content = response.get("data", {}).get("content", "")
            if not content:
                content = response.get("data", "")  # fallback на случай, если data — строка
            
            return {
                "success": True,
                "response": content,
                "task_type": "meal_plan",
                "confidence": 90
            }
            
        except Exception as e:
            logger.error(f"Ошибка при генерации плана питания: {e}")
            return {
                "success": False,
                "error": "Не удалось сгенерировать план питания"
            }
    
    def _generate_food_response(self, result: Dict) -> str:
        """Генерирует ответ для парсинга еды"""
        food_items = result.get('food_items', [])
        confidence = result.get('total_confidence', 0)
        
        if result.get('needs_clarification'):
            return result.get('clarification', 'Уточните, пожалуйста, что именно вы съели')
        
        if not food_items:
            return 'Не удалось распознать продукты. Попробуйте описать подробнее.'
        
        item_names = [item.get('name', 'неизвестно') for item in food_items]
        return f'Распознано продуктов: {len(food_items)}\\n{", ".join(item_names)}'
    
    def _generate_water_response(self, result: Dict) -> str:
        """Генерирует ответ для парсинга воды"""
        amount = result.get('amount_ml', 0)
        confidence = result.get('confidence', 0)
        
        if result.get('needs_clarification'):
            return result.get('clarification', 'Уточните, пожалуйста, количество воды')
        
        return f'Распознано воды: {amount} мл'
    
    def _generate_activity_response(self, result: Dict) -> str:
        """Генерирует ответ для парсинга активности"""
        activity_type = result.get('activity_type', 'неизвестно')
        duration = result.get('duration_minutes', 0)
        confidence = result.get('confidence', 0)
        
        if result.get('needs_clarification'):
            return result.get('clarification', 'Уточните, пожалуйста, тип и длительность активности')
        
        return f'Распознана активность: {activity_type} ({duration} мин)'
    
    def _generate_nutrition_response(self, result: Dict) -> str:
        """Генерирует ответ для расчета нутриентов"""
        calories = result.get('daily_calories', 0)
        protein = result.get('protein_g', 0)
        
        return f'Рассчитаны нормы: {calories} ккал, белок {protein}г'
    
    def _generate_climate_response(self, result: Dict) -> str:
        """Генерирует ответ для климатических рекомендаций"""
        temp_category = result.get('climate_analysis', {}).get('temperature_category', 'неизвестно')
        
        return f'Климатические рекомендации для температуры: {temp_category}'
    
    def get_system_status(self) -> Dict:
        """Возвращает статус системы AI интеграции"""
        return {
            "integration_manager": "active",
            "enhanced_parser": "active",
            "enhanced_nutrition_calculator": "active",
            "enhanced_climate_manager": "active",
            "available_tasks": list(self.task_handlers.keys()),
            "cache_status": {
                "weather_cache_size": len(self.climate_manager.weather_cache),
                "cache_duration": self.climate_manager.cache_duration
            },
            "timestamp": datetime.now().isoformat()
        }

# Создаем глобальный экземпляр менеджера интеграции
ai_integration_manager = AIIntegrationManager()
