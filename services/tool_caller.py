"""
services/tool_caller.py
Диспетчер вызова инструментов на основе классифицированных намерений
"""
import logging
from typing import Dict, Any, Optional
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

class ToolCaller:
    """Вызывает соответствующие инструменты на основе намерений пользователя"""
    
    @staticmethod
    async def call(intent: str, text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """
        Вызывает нужный инструмент по намерению
        
        Args:
            intent: Намерение пользователя
            text: Исходный текст сообщения
            user_id: ID пользователя
            message: Объект сообщения
            state: FSM состояние
            
        Returns:
            bool: Успешность выполнения
        """
        try:
            logger.info(f"Calling tool for intent: {intent}")
            
            # Маршрутизация по намерениям
            if intent == "log_food":
                return await ToolCaller.handle_log_food(text, user_id, message, state)
            
            elif intent == "log_water":
                return await ToolCaller.handle_log_water(text, user_id, message, state)
            
            elif intent == "log_weight":
                return await ToolCaller.handle_log_weight(text, user_id, message, state)
            
            elif intent == "log_activity":
                return await ToolCaller.handle_log_activity(text, user_id, message, state)
            
            elif intent == "show_progress":
                return await ToolCaller.handle_show_progress(text, user_id, message, state)
            
            elif intent == "show_profile":
                return await ToolCaller.handle_show_profile(text, user_id, message, state)
            
            elif intent == "weather":
                return await ToolCaller.handle_weather(text, user_id, message, state)
            
            elif intent == "recipe":
                return await ToolCaller.handle_recipe(text, user_id, message, state)
            
            elif intent == "calculate_nutrition":
                return await ToolCaller.handle_calculate_nutrition(text, user_id, message, state)
            
            elif intent == "general_qa":
                return await ToolCaller.handle_general_qa(text, user_id, message, state)
            
            elif intent == "help":
                return await ToolCaller.handle_help(text, user_id, message, state)
            
            else:
                logger.warning(f"Unknown intent: {intent}")
                await message.answer("[THINKING] Я не совсем понял. Можете перефразировать?")
                return False
                
        except Exception as e:
            logger.error(f"Error in tool caller for intent {intent}: {e}")
            await message.answer("[ERROR] Произошла ошибка. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_log_food(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка записи еды"""
        try:
            # Используем существующий AI процессор для парсинга еды
            from services.ai_processor import ai_processor
            
            result = await ai_processor.process_text_input(text, user_id)
            
            if result.get("success"):
                # Сохраняем через food_save_service
                from services.food_save_service import food_save_service
                from utils.ui_templates import meal_card
                
                food_items = result.get("food_items", [])
                save_result = await food_save_service.save_food_entry(
                    user_id=user_id,
                    food_items=food_items,
                    meal_type=result.get("meal_type", "snack"),
                    description=result.get("description", text)
                )
                
                if save_result.get("success"):
                    # Получаем статистику и отправляем карточку
                    from utils.daily_stats import get_daily_stats
                    from database.db import get_session
                    from database.models import User
                    
                    with get_session() as session:
                        user = session.query(User).filter(User.telegram_id == user_id).first()
                    
                    daily_stats = await get_daily_stats(user_id)
                    
                    # Формируем описание из ингредиентов
                    description_from_items = ", ".join([
                        f"{item.get('quantity','')} {item.get('unit','г')} {item['name']}" 
                        for item in food_items
                    ])
                    
                    # Форматируем данные для карточки
                    food_data = {
                        'description': description_from_items,
                        'total_calories': save_result.get('total_calories', 0),
                        'total_protein': save_result.get('total_protein', 0),
                        'total_fat': save_result.get('total_fat', 0),
                        'total_carbs': save_result.get('total_carbs', 0),
                        'meal_type': result.get("meal_type", "snack")
                    }
                    
                    card_text = meal_card(food_data, user, daily_stats)
                    await message.answer(card_text)
                else:
                    await message.answer(
                        f"[ERROR] Ошибка сохранения: {save_result.get('error', 'Неизвестная ошибка')}"
                    )
                return True
            else:
                # Если AI не смог распознать, предлагаем альтернативы
                await message.answer(
                    "[THINKING] Не удалось распознать еду. Попробуйте:\n\n"
                    "• Отправить фото еды\n"
                    "• Описать подробнее: 'гречка с курицей 200г'\n"
                    "• Использовать формат: 'продукт вес'"
                )
                return True
                
        except Exception as e:
            logger.error(f"Error in handle_log_food: {e}")
            await message.answer("[ERROR] Ошибка при записи еды. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_log_water(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка записи воды"""
        try:
            from utils.drink_parser import parse_drink_input
            from services.drink_save_service import drink_save_service
            from utils.message_templates import water_logged
            
            # Парсим ввод воды
            drink_name, volume, calories = parse_drink_input(text)
            
            if drink_name and volume:
                # Сохраняем запись воды
                save_result = await drink_save_service.save_drink_entry(
                    user_id=user_id,
                    drink_name=drink_name,
                    volume_ml=volume,
                    calories=calories
                )
                
                if save_result.get("success"):
                    # Получаем статистику за сегодня
                    from utils.daily_stats import get_daily_water
                    from database.db import get_session
                    from database.models import User
                    
                    with get_session() as session:
                        user = session.query(User).filter(User.telegram_id == user_id).first()
                    
                    total_today = await get_daily_water(user_id)
                    
                    # Отправляем подтверждение
                    response_text = water_logged(volume, total_today, user.daily_water_goal)
                    await message.answer(response_text)
                else:
                    await message.answer(f"[ERROR] Ошибка сохранения: {save_result.get('error')}")
            else:
                await message.answer(
                    "[ERROR] Не удалось распознать объем воды. Попробуйте:\n\n"
                    "• '200 мл воды'\n"
                    "• '1 стакан'\n"
                    "• '500 мл'"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_log_water: {e}")
            await message.answer("[ERROR] Ошибка при записи воды. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_log_weight(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка записи веса"""
        try:
            from utils.safe_parser import safe_parse_float
            from services.weight_save_service import weight_save_service
            from utils.message_templates import weight_logged
            
            # Извлекаем вес из текста
            weight, error = safe_parse_float(text, "вес")
            
            if weight and 30 <= weight <= 300:  # Валидация веса
                # Сохраняем запись веса
                save_result = await weight_save_service.save_weight_entry(
                    user_id=user_id,
                    weight=weight
                )
                
                if save_result.get("success"):
                    # Получаем динамику веса
                    change = save_result.get("change_from_previous")
                    
                    # Отправляем подтверждение
                    response_text = weight_logged(weight, change)
                    await message.answer(response_text)
                else:
                    await message.answer(f"[ERROR] Ошибка сохранения: {save_result.get('error')}")
            else:
                await message.answer(
                    "[ERROR] Укажите вес в кг. Например:\n\n"
                    "• '70.5 кг'\n"
                    "• 'вес 68'\n"
                    "• '72'"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_log_weight: {e}")
            await message.answer("[ERROR] Ошибка при записи веса. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_log_activity(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка записи активности"""
        try:
            from services.activity_save_service import activity_save_service
            from utils.message_templates import activity_logged
            
            # Извлекаем данные об активности
            # TODO: Добавить парсинг активности
            activity_type = "тренировка"  # По умолчанию
            duration = 30  # По умолчанию 30 минут
            calories_burned = 200  # По умолчанию
            
            # Сохраняем запись активности
            save_result = await activity_save_service.save_activity_entry(
                user_id=user_id,
                activity_type=activity_type,
                duration_minutes=duration,
                calories_burned=calories_burned
            )
            
            if save_result.get("success"):
                # Отправляем подтверждение
                response_text = activity_logged(activity_type, duration, calories_burned)
                await message.answer(response_text)
            else:
                await message.answer(f"[ERROR] Ошибка сохранения: {save_result.get('error')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_log_activity: {e}")
            await message.answer("[ERROR] Ошибка при записи активности. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_show_progress(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка просмотра прогресса"""
        try:
            from handlers.common import period_callback
            
            # Определяем период из текста
            period = "today"  # По умолчанию
            
            if "неделя" in text.lower() or "week" in text.lower():
                period = "week"
            elif "месяц" in text.lower() or "month" in text.lower():
                period = "month"
            elif "все время" in text.lower() or "all" in text.lower():
                period = "all"
            
            # Создаем фейковый callback для переиспользования логики
            class FakeCallback:
                def __init__(self, data):
                    self.data = data
                    self.from_user = message.from_user
            
            fake_callback = FakeCallback(f"period_{period}")
            
            # Вызываем обработчик прогресса
            await period_callback(fake_callback, state)
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_show_progress: {e}")
            await message.answer("[ERROR] Ошибка при загрузке прогресса. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_show_profile(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка просмотра профиля"""
        try:
            from handlers.common import show_profile_main_callback
            
            # Создаем фейковый callback
            class FakeCallback:
                def __init__(self):
                    self.from_user = message.from_user
            
            fake_callback = FakeCallback()
            
            # Вызываем обработчик профиля
            await show_profile_main_callback(fake_callback, state)
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_show_profile: {e}")
            await message.answer("[ERROR] Ошибка при загрузке профиля. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_weather(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка запроса погоды"""
        try:
            from services.weather import get_weather
            from utils.message_templates import ai_response_message
            
            # Извлекаем город из текста
            city = "Москва"  # По умолчанию
            
            # TODO: Добавить парсинг города из текста
            
            # Получаем погоду
            weather_data = await get_weather(city)
            
            if weather_data:
                response_text = (
                    f"[WEATHER] <b>Погода в {city}</b>\n\n"
                    f"[TEMP] Температура: {weather_data.get('temp', 'N/A')}°C\n"
                    f"[CONDITION] {weather_data.get('condition', 'N/A')}\n"
                    f"[HUMIDITY] Влажность: {weather_data.get('humidity', 'N/A')}%\n"
                    f"[WIND] Ветер: {weather_data.get('wind', 'N/A')} м/с"
                )
                
                await message.answer(response_text)
            else:
                await message.answer("[ERROR] Не удалось получить погоду. Попробуйте позже.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_weather: {e}")
            await message.answer("[ERROR] Ошибка при получении погоды. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_recipe(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка запроса рецепта"""
        try:
            from services.ai_processor import ai_processor
            from utils.message_templates import ai_response_message
            
            # Используем AI для генерации рецепта
            result = await ai_processor.process_text_input(f"рецепт: {text}", user_id)
            
            if result.get("success"):
                response_text = ai_response_message(
                    result.get("response", "Не удалось сгенерировать рецепт."),
                    "recipe"
                )
                await message.answer(response_text)
            else:
                await message.answer("[ERROR] Не удалось сгенерировать рецепт. Попробуйте перефразировать запрос.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_recipe: {e}")
            await message.answer("[ERROR] Ошибка при генерации рецепта. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_calculate_nutrition(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка расчета КБЖУ"""
        try:
            from services.ai_processor import ai_processor
            from utils.message_templates import ai_response_message
            
            # Используем AI для расчета КБЖУ
            result = await ai_processor.process_text_input(f"рассчитать КБЖУ: {text}", user_id)
            
            if result.get("success"):
                response_text = ai_response_message(
                    result.get("response", "Не удалось рассчитать КБЖУ."),
                    "analysis"
                )
                await message.answer(response_text)
            else:
                await message.answer("[ERROR] Не удалось рассчитать КБЖУ. Укажите продукты и их вес.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_calculate_nutrition: {e}")
            await message.answer("[ERROR] Ошибка при расчете КБЖУ. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_general_qa(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка общего вопроса"""
        try:
            from services.ai_processor import ai_processor
            from utils.message_templates import ai_response_message
            
            # Используем AI для ответа на вопрос
            result = await ai_processor.process_text_input(text, user_id)
            
            if result.get("success"):
                response_text = ai_response_message(
                    result.get("response", "Не удалось ответить на вопрос."),
                    "general"
                )
                await message.answer(response_text)
            else:
                await message.answer("[THINKING] Я не смог понять вопрос. Попробуйте перефразировать.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_general_qa: {e}")
            await message.answer("[ERROR] Ошибка при обработке вопроса. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_help(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка запроса помощи"""
        try:
            from utils.message_templates import help_message
            
            # Отправляем справку
            help_text = help_message()
            await message.answer(help_text)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_help: {e}")
            await message.answer("[ERROR] Ошибка при загрузке справки. Попробуйте еще раз.")
            return False

# Глобальный экземпляр диспетчера
tool_caller = ToolCaller()
