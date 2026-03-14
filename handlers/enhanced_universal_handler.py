"""
🚀 Enhanced Universal Handler - Улучшенный универсальный обработчик NutriBuddy
✨ Полная замена rule-based компонентов на AI
🎯 Интеграция с Enhanced AI Integration Manager
"""

import logging
from typing import Dict, List, Optional, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy import select
from services.ai_integration_manager import ai_integration_manager
from services.food_save_service import food_save_service
from database.db import get_session
from database.models import User, WaterEntry, Activity, WeightEntry, StepsEntry
from keyboards.reply import get_main_keyboard
from keyboards.improved_keyboards import get_daily_goals_keyboard
from utils.unit_converter import convert_to_grams

logger = logging.getLogger(__name__)
router = Router()

class EnhancedUniversalHandler:
    """Улучшенный универсальный обработчик с полной AI-интеграцией"""
    
    def __init__(self):
        self.ai_manager = ai_integration_manager
    
    async def handle_message(
        self,
        message: Message,
        state: FSMContext,
        text: str = None
    ) -> None:
        """
        Основной обработчик сообщений с AI
        
        Обрабатывает:
        - Классификацию намерений
        - Парсинг еды, воды, активности
        - Вопросы и команды помощи
        - Многозадачные запросы
        """
        
        if text is None:
            text = message.text
        
        user_id = message.from_user.id
        
        try:
            logger.info(f"🚀 Enhanced handler processing: {text[:50]}...")
            
            # Получаем контекст пользователя
            context = await self._get_user_context(user_id, state)
            
            # Получаем историю диалога
            history = await self._get_conversation_history(user_id, state)
            
            # Обрабатываем через AI Integration Manager
            result = await self.ai_manager.process_user_input(
                text=text,
                user_id=user_id,
                context=context,
                history=history,
                task_type='auto'
            )
            
            # Выполняем действия
            await self._execute_actions(result, message, state)
            
            # Отправляем ответ
            await self._send_response(result, message)
            
        except Exception as e:
            logger.error(f"🚀 Enhanced handler error: {e}")
            await message.answer(
                "❌ Произошла ошибка при обработке запроса",
                reply_markup=get_main_keyboard()
            )
    
    async def handle_callback(
        self,
        callback: CallbackQuery,
        state: FSMContext
    ) -> None:
        """
        Обработчик callback с AI
        
        Обрабатывает:
        - Запросы рекомендаций
        - Анализ прогресса
        - Климатическую адаптацию
        - Быстрые действия (вода, активность, вес)
        """
        
        user_id = callback.from_user.id
        callback_data = callback.data
        
        try:
            logger.info(f"🚀 Enhanced callback processing: {callback_data}")
            
            # Обработка быстрых действий (вода, активность, вес)
            if callback_data.startswith('water_add_'):
                await self._handle_water_quick_add(callback, callback_data)
                return
            elif callback_data.startswith('weight_'):
                await self._handle_weight_quick_action(callback, callback_data)
                return
            
            # Парсим callback_data для AI действий
            action_data = self._parse_callback_data(callback_data)
            
            if not action_data:
                await callback.answer("❌ Неверный формат callback")
                return
            
            action_type = action_data.get('type')
            action_params = action_data.get('params', {})
            
            # Выполняем действие
            if action_type == 'get_recommendations':
                await self._handle_recommendations_callback(callback, state, action_params)
            elif action_type == 'analyze_progress':
                await self._handle_progress_analysis_callback(callback, state, action_params)
            elif action_type == 'climate_adaptation':
                await self._handle_climate_callback(callback, state, action_params)
            else:
                await callback.answer("❌ Неизвестное действие")
                
        except Exception as e:
            logger.error(f"🚀 Enhanced callback error: {e}")
            await callback.answer("❌ Ошибка при обработке запроса")
    
    async def handle_command(
        self,
        message: Message,
        state: FSMContext,
        command: str,
        args: List[str] = None
    ) -> None:
        """
        Обработчик команд с AI
        
        Поддерживаемые команды:
        /analyze - анализ прогресса
        /recommendations - персональные рекомендации
        /climate - климатические рекомендации
        /norms - расчет норм
        """
        
        user_id = message.from_user.id
        
        try:
            logger.info(f"🚀 Enhanced command processing: /{command}")
            
            # Получаем контекст
            context = await self._get_user_context(user_id, state)
            context['command'] = command
            context['args'] = args or []
            
            # Определяем тип задачи
            task_mapping = {
                'analyze': 'progress_analysis',
                'recommendations': 'recommendations',
                'climate': 'climate_adaptation',
                'norms': 'nutrition_calculation'
            }
            
            task_type = task_mapping.get(command, 'multi_task')
            
            # Обрабатываем через AI Integration Manager
            result = await self.ai_manager.process_user_input(
                text=f"Команда: /{command} {' '.join(args) if args else ''}",
                user_id=user_id,
                context=context,
                task_type=task_type
            )
            
            # Выполняем действия
            await self._execute_actions(result, message, state)
            
            # Отправляем ответ
            await self._send_response(result, message)
            
        except Exception as e:
            logger.error(f"🚀 Enhanced command error: {e}")
            await message.answer(
                "❌ Ошибка при выполнении команды",
                reply_markup=get_main_keyboard()
            )
    
    async def _execute_actions(
        self,
        result: Dict,
        message: Message,
        state: FSMContext
    ) -> None:
        """Выполняет действия из результата AI"""
        
        actions = result.get('actions', [])
        user_id = message.from_user.id
        
        for action in actions:
            action_type = action.get('type')
            action_data = action.get('data', {})
            
            try:
                if action_type == 'save_food':
                    await self._save_food(user_id, action_data, message)
                elif action_type == 'save_water':
                    await self._save_water(user_id, action_data, message)
                elif action_type == 'save_activity':
                    await self._save_activity(user_id, action_data, message)
                elif action_type == 'save_steps':
                    await self._save_steps(user_id, action_data, message)
                elif action_type == 'save_weight':
                    await self._save_weight(user_id, action_data, message)
                elif action_type == 'update_norms':
                    await self._update_norms(user_id, action_data, message)
                elif action_type == 'climate_adaptation':
                    await self._apply_climate_adaptation(user_id, action_data, message)
                else:
                    logger.warning(f"🚀 Unknown action type: {action_type}")
                    
            except Exception as e:
                logger.error(f"🚀 Action execution error ({action_type}): {e}")
    
    async def _send_response(
        self,
        result: Dict,
        message: Message
    ) -> None:
        """Отправляет ответ пользователю"""
        
        response_text = result.get('response', 'Запрос обработан')
        confidence = result.get('confidence', 0)
        needs_clarification = result.get('needs_clarification', False)
        
        # Добавляем информацию о уверенности
        if confidence < 70:
            response_text += f"\n\n🤔 Уверенность: {confidence}%"
        
        # Добавляем запрос уточнения если нужно
        if needs_clarification:
            clarification = result.get('clarification', 'Пожалуйста, уточните запрос')
            response_text += f"\n\n❓ {clarification}"
        
        # Добавляем информацию о действиях
        actions = result.get('actions', [])
        if actions:
            response_text += f"\n\n✅ Выполнено действий: {len(actions)}"
        
        await message.answer(response_text, reply_markup=get_daily_goals_keyboard())
    
    async def _save_food(
        self,
        user_id: int,
        food_data: Dict,
        original_message: Message
    ) -> None:
        """Сохраняет информацию о еде через унифицированный сервис"""
        
        try:
            food_items = food_data.get('food_items', [])
            meal_type = food_data.get('meal_type', 'main')
            
            if not food_items:
                await original_message.answer("❌ Нет продуктов для сохранения")
                return
            
            # Используем унифицированный сервис сохранения
            result = await food_save_service.save_food_to_db(
                user_id=user_id,
                food_items=food_items,
                meal_type=meal_type
            )
            
            if result.get("success"):
                await original_message.answer(
                    f"✅ {result.get('message')}\n"
                    f"🔥 Всего калорий: {result.get('total_calories', 0):.0f} ккал"
                )
            else:
                await original_message.answer(f"❌ {result.get('error', 'Ошибка сохранения')}")
                
        except Exception as e:
            logger.error(f"🚀 Error saving food via service: {e}")
            await original_message.answer("❌ Ошибка при сохранении еды")
    
    async def _save_water(
        self,
        user_id: int,
        water_data: Dict,
        original_message: Message
    ) -> None:
        """Сохраняет информацию о воде"""
        
        try:
            amount_ml = water_data.get('amount_ml', 0)
            
            if amount_ml <= 0:
                return
            
            async with get_session() as session:
                # Получаем пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await original_message.answer("❌ Сначала создайте профиль")
                    return
                
                # Сохраняем запись о воде
                from datetime import datetime
                
                water_entry = WaterEntry(
                    user_id=user.id,
                    datetime=datetime.now(),
                    amount=amount_ml
                )
                session.add(water_entry)
                await session.commit()
                
                logger.info(f"🚀 Saved water entry: {amount_ml} ml for user {user_id}")
                
        except Exception as e:
            logger.error(f"🚀 Error saving water: {e}")
    
    async def _save_activity(
        self,
        user_id: int,
        activity_data: Dict,
        original_message: Message
    ) -> None:
        """Сохраняет информацию об активности"""
        
        try:
            activity_type = activity_data.get('activity_type', 'неизвестно')
            duration = activity_data.get('duration', 30)
            calories = activity_data.get('calories_estimate', 200)
            
            async with get_session() as session:
                # Получаем пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await original_message.answer("❌ Сначала создайте профиль")
                    return
                
                # Сохраняем запись об активности
                from datetime import datetime
                
                activity = Activity(
                    user_id=user.id,
                    datetime=datetime.now(),
                    activity_type=activity_type,
                    duration=duration,
                    calories_burned=calories
                )
                session.add(activity)
                await session.commit()
                
                logger.info(f"🚀 Saved activity: {activity_type} ({duration} min) for user {user_id}")
                
        except Exception as e:
            logger.error(f"🚀 Error saving activity: {e}")
    
    async def _save_steps(
        self,
        user_id: int,
        steps_data: Dict,
        original_message: Message
    ) -> None:
        """Сохраняет информацию о шагах"""
        
        try:
            steps_count = steps_data.get('steps_count', 0)
            
            if steps_count <= 0:
                return
            
            async with get_session() as session:
                # Получаем пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await original_message.answer("❌ Сначала создайте профиль")
                    return
                
                # Сохраняем запись о шагах
                from datetime import datetime
                
                steps_entry = StepsEntry(
                    user_id=user.id,
                    datetime=datetime.now(),
                    steps_count=steps_count,
                    source='ai_enhanced'
                )
                session.add(steps_entry)
                await session.commit()
                
                logger.info(f"🚀 Saved steps: {steps_count} for user {user_id}")
                
        except Exception as e:
            logger.error(f"🚀 Error saving steps: {e}")
    
    async def _save_weight(
        self,
        user_id: int,
        weight_data: Dict,
        original_message: Message
    ) -> None:
        """Сохраняет информацию о весе"""
        
        try:
            weight_kg = weight_data.get('weight_kg', 0)
            
            if weight_kg <= 0 or weight_kg > 300:
                await original_message.answer("❌ Некорректный вес")
                return
            
            async with get_session() as session:
                # Получаем пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await original_message.answer("❌ Сначала создайте профиль")
                    return
                
                # Сохраняем запись о весе
                from datetime import datetime
                
                weight_entry = WeightEntry(
                    user_id=user.id,
                    datetime=datetime.now(),
                    weight=weight_kg
                )
                session.add(weight_entry)
                await session.commit()
                
                logger.info(f"🚀 Saved weight: {weight_kg} kg for user {user_id}")
                
        except Exception as e:
            logger.error(f"🚀 Error saving weight: {e}")
    
    async def _update_norms(
        self,
        user_id: int,
        norms_data: Dict,
        original_message: Message
    ) -> None:
        """Обновляет нормы питания"""
        
        try:
            async with get_session() as session:
                # Получаем пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await original_message.answer("❌ Сначала создайте профиль")
                    return
                
                # Обновляем нормы
                user.daily_calorie_goal = norms_data.get('daily_calories', user.daily_calorie_goal)
                user.daily_protein_goal = norms_data.get('protein_g', getattr(user, 'daily_protein_goal', None))
                user.daily_fat_goal = norms_data.get('fat_g', getattr(user, 'daily_fat_goal', None))
                user.daily_carbs_goal = norms_data.get('carbs_g', getattr(user, 'daily_carbs_goal', None))
                
                await session.commit()
                
                logger.info(f"🚀 Updated norms for user {user_id}")
                
        except Exception as e:
            logger.error(f"🚀 Error updating norms: {e}")
    
    async def _apply_climate_adaptation(
        self,
        user_id: int,
        climate_data: Dict,
        original_message: Message
    ) -> None:
        """Применяет климатическую адаптацию"""
        
        # Климатические рекомендации обычно не требуют сохранения в БД
        # Они используются для информирования пользователя
        logger.info(f"🚀 Applied climate adaptation for user {user_id}")
    
    async def _handle_recommendations_callback(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        params: Dict
    ) -> None:
        """Обработчик callback для получения рекомендаций"""
        
        user_id = callback.from_user.id
        recommendation_type = params.get('type', 'nutrition')
        
        result = await self.ai_manager.get_personalized_recommendations(
            user_id=user_id,
            recommendation_type=recommendation_type,
            context=params
        )
        
        # Формируем ответ
        recommendations = result.get('recommendations', [])
        response_text = f"📋 **Рекомендации ({recommendation_type}):**\\n\\n"
        
        for i, rec in enumerate(recommendations[:5], 1):  # Ограничиваем количество
            if isinstance(rec, dict):
                response_text += f"{i}. {rec.get('recommendation', str(rec))}\\n"
            else:
                response_text += f"{i}. {rec}\\n"
        
        await callback.message.edit_text(response_text, parse_mode="Markdown")
        await callback.answer()
    
    async def _handle_progress_analysis_callback(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        params: Dict
    ) -> None:
        """Обработчик callback для анализа прогресса"""
        
        user_id = callback.from_user.id
        period_days = params.get('period_days', 7)
        
        result = await self.ai_manager.analyze_progress_and_adapt(
            user_id=user_id,
            period_days=period_days
        )
        
        # Формируем ответ
        progress_analysis = result.get('progress_analysis', {})
        adaptations = result.get('adaptations', {})
        recommendations = result.get('recommendations', [])
        
        response_text = "📊 **Анализ прогресса:**\\n\\n"
        
        if progress_analysis:
            for key, value in progress_analysis.items():
                response_text += f"• {key}: {value}\\n"
        
        if adaptations:
            response_text += "\\n🔧 **Рекомендуемые корректировки:**\\n\\n"
            for key, value in adaptations.items():
                response_text += f"• {key}: {value}\\n"
        
        if recommendations:
            response_text += "\\n💡 **Рекомендации:**\\n\\n"
            for i, rec in enumerate(recommendations[:3], 1):
                response_text += f"{i}. {rec}\\n"
        
        await callback.message.edit_text(response_text, parse_mode="Markdown")
        await callback.answer()
    
    async def _handle_climate_callback(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        params: Dict
    ) -> None:
        """Обработчик callback для климатических рекомендаций"""
        
        user_id = callback.from_user.id
        city = params.get('city', 'Москва')
        
        result = await self.ai_manager.get_personalized_recommendations(
            user_id=user_id,
            recommendation_type='climate',
            context={'city': city}
        )
        
        # Формируем ответ
        climate_analysis = result.get('recommendations', {})
        food_recommendations = climate_analysis.get('food_recommendations', [])
        health_tips = climate_analysis.get('health_tips', [])
        
        response_text = f"🌤️ **Климатические рекомендации для {city}:**\\n\\n"
        
        if food_recommendations:
            response_text += "🍽 **Рекомендации по питанию:**\\n"
            for food_rec in food_recommendations[:3]:
                if isinstance(food_rec, dict):
                    response_text += f"• {food_rec.get('category', '')}: {food_rec.get('examples', [])}\\n"
                else:
                    response_text += f"• {food_rec}\\n"
        
        if health_tips:
            response_text += "\\n💡 **Советы по здоровью:**\\n"
            for tip in health_tips[:3]:
                response_text += f"• {tip}\\n"
        
        await callback.message.edit_text(response_text, parse_mode="Markdown")
        await callback.answer()
    
    def _parse_callback_data(self, callback_data: str) -> Optional[Dict]:
        """Парсит callback_data"""
        try:
            import json
            return json.loads(callback_data)
        except:
            # Формат water_add_100, weight_dec_1_10_123
            if '_' in callback_data and ':' not in callback_data:
                parts = callback_data.split('_')
                if len(parts) >= 3:
                    return {
                        'type': f"{parts[0]}_{parts[1]}",
                        'params': {
                            'value': parts[2] if len(parts) == 3 else '_'.join(parts[2:])
                        }
                    }
            
            # Простой формат: type:param1=value1,param2=value2
            parts = callback_data.split(':', 1)
            if len(parts) != 2:
                return None
            
            action_type = parts[0]
            params_str = parts[1]
            
            params = {}
            for param in params_str.split(','):
                key_value = param.split('=', 1)
                if len(key_value) == 2:
                    params[key_value[0]] = key_value[1]
            
            return {
                'type': action_type,
                'params': params
            }
    
    async def _get_user_context(
        self,
        user_id: int,
        state: FSMContext
    ) -> Dict:
        """Получает контекст пользователя"""
        try:
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if user:
                    context = {
                        'age': user.age,
                        'gender': user.gender,
                        'goal': user.goal,
                        'activity_level': user.activity_level,
                        'daily_calorie_goal': user.daily_calorie_goal
                    }
                    
                    # Добавляем состояние FSM
                    current_state = await state.get_state()
                    if current_state:
                        context['current_state'] = current_state
                    
                    return context
                else:
                    return {}
        except Exception as e:
            logger.error(f"🚀 Error getting user context: {e}")
            return {}
    
    async def _get_conversation_history(
        self,
        user_id: int,
        state: FSMContext
    ) -> List[str]:
        """Получает историю диалога"""
        try:
            data = await state.get_data()
            history = data.get('conversation_history', [])
            return history[-10:]  # Последние 10 сообщений
        except Exception as e:
            logger.error(f"🚀 Error getting conversation history: {e}")
            return []

    async def _handle_water_quick_add(self, callback: CallbackQuery, callback_data: str):
        """Обработка быстрого добавления воды"""
        try:
            # Парсим количество воды: water_add_200
            parts = callback_data.split('_')
            if len(parts) >= 3:
                amount = int(parts[2])
            else:
                amount = 200  # по умолчанию
            
            user_id = callback.from_user.id
            
            # Сохраняем воду
            from database.db import get_session
            from database.models import User, WaterEntry
            from sqlalchemy import select
            from datetime import datetime
            
            async with get_session() as session:
                # Находим пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await callback.answer("❌ Пользователь не найден", show_alert=True)
                    return
                
                # Добавляем запись о воде
                water_entry = WaterEntry(
                    user_id=user.id,
                    amount=amount,
                    datetime=datetime.now()
                )
                session.add(water_entry)
                await session.commit()
            
            await callback.answer(f"💧 +{amount} мл добавлено!", show_alert=False)
            
            # Обновляем сообщение если нужно
            if callback.message:
                await callback.message.edit_text(
                    f"💧 Вода записана: +{amount} мл",
                    reply_markup=None
                )
                
        except Exception as e:
            logger.error(f"🚀 Error in water quick add: {e}")
            await callback.answer("❌ Ошибка при добавлении воды", show_alert=True)

    async def _handle_weight_quick_action(self, callback: CallbackQuery, callback_data: str):
        """Обработка быстрых действий с весом"""
        try:
            # Парсим действие: weight_inc_1_0_5 или weight_dec_1_0_5
            parts = callback_data.split('_')
            if len(parts) >= 4:
                action = parts[1]  # inc/dec
                kg = float(parts[2])
                g = float(parts[3])
                weight_change = kg + g/10
            else:
                await callback.answer("❌ Неверный формат", show_alert=True)
                return
            
            user_id = callback.from_user.id
            
            # Получаем текущий вес и сохраняем новый
            from database.db import get_session
            from database.models import User, WeightEntry
            from sqlalchemy import select
            from datetime import datetime
            
            async with get_session() as session:
                # Находим пользователя
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user or not user.weight:
                    await callback.answer("❌ Сначала укажите вес в профиле", show_alert=True)
                    return
                
                # Рассчитываем новый вес
                if action == 'inc':
                    new_weight = user.weight + weight_change
                    emoji = "📈"
                else:
                    new_weight = user.weight - weight_change
                    emoji = "📉"
                
                # Обновляем вес в профиле
                user.weight = new_weight
                
                # Добавляем запись истории
                weight_entry = WeightEntry(
                    user_id=user.id,
                    weight=new_weight,
                    datetime=datetime.now()
                )
                session.add(weight_entry)
                await session.commit()
            
            await callback.answer(f"{emoji} Вес обновлён: {new_weight:.1f} кг", show_alert=False)
            
            # Обновляем сообщение
            if callback.message:
                await callback.message.edit_text(
                    f"{emoji} Вес обновлён: {new_weight:.1f} кг",
                    reply_markup=None
                )
                
        except Exception as e:
            logger.error(f"🚀 Error in weight quick action: {e}")
            await callback.answer("❌ Ошибка при обновлении веса", show_alert=True)

# Создаем экземпляр улучшенного обработчика
enhanced_handler = EnhancedUniversalHandler()

# Регистрируем обработчики с фильтром, чтобы не перехватывать команды
@router.message(F.text & ~F.command())
async def enhanced_message_handler(message: Message, state: FSMContext):
    """Enhanced обработчик сообщений - только текст, не команды"""
    await enhanced_handler.handle_message(message, state)

@router.callback_query()
async def enhanced_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Enhanced обработчик callback"""
    await enhanced_handler.handle_callback(callback, state)

@router.message(Command("analyze"))
async def enhanced_analyze_command(message: Message, state: FSMContext):
    """Команда анализа прогресса"""
    await enhanced_handler.handle_command(message, state, "analyze")

@router.message(Command("recommendations"))
async def enhanced_recommendations_command(message: Message, state: FSMContext):
    """Команда получения рекомендаций"""
    await enhanced_handler.handle_command(message, state, "recommendations")

@router.message(Command("climate"))
async def enhanced_climate_command(message: Message, state: FSMContext):
    """Команда климатических рекомендаций"""
    await enhanced_handler.handle_command(message, state, "climate")

@router.message(Command("norms"))
async def enhanced_norms_command(message: Message, state: FSMContext):
    """Команда расчета норм"""
    await enhanced_handler.handle_command(message, state, "norms")

logger.info("🚀 Enhanced Universal Handler loaded")
