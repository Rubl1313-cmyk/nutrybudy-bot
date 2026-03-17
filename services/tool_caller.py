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
            
            if intent == "log_food":
                return await ToolCaller.handle_log_food(text, user_id, message, state)
            
            elif intent == "log_drink":
                return await ToolCaller.handle_log_drink(text, user_id, message, state)
            
            elif intent == "log_water":
                return await ToolCaller.handle_log_water(text, user_id, message, state)
            
            elif intent == "log_weight":
                return await ToolCaller.handle_log_weight(text, user_id, message, state)
            
            elif intent == "log_activity":
                return await ToolCaller.handle_log_activity(text, user_id, message, state)
            
            elif intent == "show_progress":
                return await ToolCaller.handle_show_progress(text, user_id, message, state)
            
            elif intent == "ask_ai":
                return await ToolCaller.handle_ask_ai(text, user_id, message, state)
            
            elif intent == "help":
                return await ToolCaller.handle_help(text, user_id, message, state)
            
            else:
                logger.warning(f"Unknown intent: {intent}")
                await message.answer("🤔 Я не совсем понял. Можете перефразировать?")
                return False
                
        except Exception as e:
            logger.error(f"Error in tool caller for intent {intent}: {e}")
            await message.answer("❌ Произошла ошибка. Попробуйте еще раз.")
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
                
                food_items = result["parameters"].get("food_items", [])
                meal_type = result["parameters"].get("meal_type", "main")
                
                save_result = await food_save_service.save_food_to_db(
                    user_id, 
                    food_items, 
                    meal_type
                )
                
                if save_result.get("success"):
                    # Получаем статистику и отправляем карточку
                    from utils.daily_stats import get_daily_stats
                    from database.db import get_session
                    from database.models import User
                    from sqlalchemy import select
                    
                    async with get_session() as session:
                        user_result = await session.execute(
                            select(User).where(User.telegram_id == user_id)
                        )
                        user = user_result.scalar_one_or_none()
                    
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
                        'meal_type': meal_type
                    }
                    
                    await message.answer(
                        meal_card(food_data, user, daily_stats),
                        parse_mode="HTML"
                    )
                else:
                    await message.answer(
                        f"❌ Ошибка сохранения: {save_result.get('error', 'Неизвестная ошибка')}"
                    )
                return True
            else:
                # Если AI не смог распознать, предлагаем альтернативы
                await message.answer(
                    "🤔 Не удалось распознать еду. Попробуйте:\n\n"
                    "• Описать подробнее: «200г куриной грудки с гречкой»\n"
                    "• Отправить фото блюда\n"
                    "• Использовать команду /log_food",
                    parse_mode="HTML"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error in log_food: {e}")
            return False
    
    @staticmethod
    async def handle_log_drink(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка записи напитков"""
        try:
            # Используем новый парсер напитков
            from utils.drink_parser import parse_drink
            volume, drink_name, calories = await parse_drink(text)
            
            if not volume or volume <= 0:
                await message.answer(
                    "❌ Не удалось определить количество напитка. Попробуйте еще раз:\n\n"
                    "Примеры: сок 250 мл, чай с сахаром 300, молоко 200"
                )
                return False
            
            # Сохраняем напиток
            from services.soup_service import save_drink
            result = await save_drink(user_id, text)
            
            # Получаем статистику за сегодня
            from database.db import get_session
            from database.models import User, DrinkEntry
            from sqlalchemy import func, extract
            from keyboards.reply_v2 import get_main_keyboard_v2
            from datetime import datetime
            
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await message.answer(
                        "❌ Сначала создайте профиль командой /set_profile",
                        reply_markup=get_main_keyboard_v2()
                    )
                    return False
                
                # Статистика за сегодня
                today_stats = await session.execute(
                    select(func.sum(DrinkEntry.volume_ml), func.sum(DrinkEntry.calories)).where(
                        DrinkEntry.user_id == user.id,
                        extract('day', DrinkEntry.datetime) == datetime.now().day,
                        extract('month', DrinkEntry.datetime) == datetime.now().month,
                        extract('year', DrinkEntry.datetime) == datetime.now().year
                    )
                )
                total_volume, total_calories = today_stats.first() or (0, 0)
                
                progress = (total_volume / user.daily_water_goal) * 100
                
                await message.answer(
                    f"✅ <b>Напиток записан!</b>\n\n"
                    f"🥤 {drink_name.title()}: {volume:.0f} мл\n"
                    f"🔥 Калории: {calories:.0f} ккал\n\n"
                    f"📊 <b>Всего за сегодня:</b>\n"
                    f"💦 Жидкость: {total_volume:.0f} мл\n"
                    f"🎯 Цель: {user.daily_water_goal} мл\n"
                    f"📈 Прогресс: {progress:.1f}%\n"
                    f"🔥 Калории из напитков: {total_calories:.0f} ккал\n\n"
                    f"{'🎉 Отлично!' if progress >= 100 else '💪 Продолжайте!'}",
                    reply_markup=get_main_keyboard_v2(),
                    parse_mode="HTML"
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_log_drink: {e}")
            await message.answer("❌ Ошибка при записи напитка. Попробуйте еще раз.")
            return False
    
    @staticmethod
    async def handle_log_water(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка записи воды"""
        try:
            # Извлекаем количество воды
            from services.intent_classifier import IntentClassifier
            entities = IntentClassifier.extract_entities(text, "log_water")
            
            amount = entities.get('amount_ml')
            if not amount:
                # Пробуем простой парсинг
                from utils.water_parser import parse_water_amount
                amount = parse_water_amount(text)
            
            if amount and amount > 0:
                # Сохраняем в базу
                from database.db import get_session
                from database.models import User, DrinkEntry
                from datetime import datetime
                
                async with get_session() as session:
                    # Получаем пользователя
                    user_result = await session.execute(
                        select(User).where(User.telegram_id == user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    
                    if not user:
                        await message.answer(
                            "❌ Сначала создайте профиль командой /set_profile",
                            reply_markup=get_main_keyboard_v2()
                        )
                        return False
                    
                    # Создаем запись о воде
                    water_entry = DrinkEntry(
                        user_id=user.id,
                        name='вода',
                        volume_ml=amount,
                        source='drink',
                        datetime=datetime.now()
                    )
                    session.add(water_entry)
                    await session.commit()
                    
                    # Получаем статистику за сегодня
                    from keyboards.reply_v2 import get_main_keyboard_v2
                    from sqlalchemy import func, extract
                    
                    today_stats = await session.execute(
                        select(func.sum(DrinkEntry.volume_ml)).where(
                            DrinkEntry.user_id == user.id,
                            extract('day', DrinkEntry.datetime) == datetime.now().day,
                            extract('month', DrinkEntry.datetime) == datetime.now().month,
                            extract('year', DrinkEntry.datetime) == datetime.now().year
                        )
                    )
                    today_total = today_stats.scalar() or 0
                    
                    # Формируем ответ
                    progress_percent = (today_total / user.daily_water_goal) * 100 if user.daily_water_goal else 0
                    remaining = user.daily_water_goal - today_total if user.daily_water_goal else 0
                    
                    response = f"💧 <b>Записано: {amount} мл</b>\n\n"
                    response += f"📊 <b>Сегодня выпито:</b> {today_total} мл\n"
                    response += f"🎯 <b>Норма:</b> {user.daily_water_goal} мл\n"
                    response += f"📈 <b>Прогресс:</b> {progress_percent:.0f}%\n"
                    
                    if remaining > 0:
                        response += f"💪 <b>Осталось:</b> {remaining} мл"
                    else:
                        response += f"🎉 <b>Норма выполнена!</b>"
                    
                    await message.answer(response, parse_mode="HTML")
                    return True
            else:
                await message.answer(
                    "❌ Не удалось определить количество воды.\n\n"
                    "Примеры:\n"
                    "• «Выпил 2 стакана»\n"
                    "• «500 мл воды»\n"
                    "• «1.5 литра»",
                    parse_mode="HTML"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error in log_water: {e}")
            return False
    
    @staticmethod
    async def handle_log_weight(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка записи веса"""
        try:
            # Извлекаем вес
            from services.intent_classifier import IntentClassifier
            entities = IntentClassifier.extract_entities(text, "log_weight")
            
            weight_kg = entities.get('weight_kg')
            
            if weight_kg and 30 <= weight_kg <= 300:
                # Сохраняем в базу и пересчитываем нормы
                from database.db import get_session
                from database.models import User, WeightEntry
                from datetime import datetime
                from services.calculator import calculate_calorie_goal, calculate_water_goal
                from services.body_stats import get_body_composition_analysis
                
                async with get_session() as session:
                    # Получаем пользователя
                    user_result = await session.execute(
                        select(User).where(User.telegram_id == user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    
                    if not user:
                        await message.answer(
                            "❌ Сначала создайте профиль командой /set_profile",
                            reply_markup=get_main_keyboard_v2()
                        )
                        return False
                    
                    # Получаем предыдущий вес для анализа тренда
                    previous_weights_result = await session.execute(
                        select(WeightEntry.weight).where(
                            WeightEntry.user_id == user.id
                        ).order_by(WeightEntry.datetime.desc()).limit(10)
                    )
                    previous_weights = [row[0] for row in previous_weights_result.fetchall()]
                    
                    # Сохраняем новую запись веса
                    weight_entry = WeightEntry(
                        user_id=user.id,
                        weight=weight_kg,
                        datetime=datetime.now()
                    )
                    session.add(weight_entry)
                    
                    # Обновляем вес пользователя и пересчитываем нормы
                    old_weight = user.weight
                    user.weight = weight_kg
                    
                    # Пересчитываем КБЖУ
                    calories, protein, fat, carbs = calculate_calorie_goal(
                        weight=weight_kg,
                        height=user.height,
                        age=user.age,
                        gender=user.gender,
                        activity_level=user.activity_level,
                        goal=user.goal
                    )
                    
                    water_goal = calculate_water_goal(
                        weight=weight_kg,
                        activity_level=user.activity_level,
                        temperature=20.0,
                        goal=user.goal  # Добавляем цель для расчета воды
                    )
                    
                    # Обновляем нормы
                    user.daily_calorie_goal = round(calories)
                    user.daily_protein_goal = round(protein)
                    user.daily_fat_goal = round(fat)
                    user.daily_carbs_goal = round(carbs)
                    user.daily_water_goal = round(water_goal)
                    
                    # Анализ композиции тела
                    body_analysis = get_body_composition_analysis(
                        weight=weight_kg,
                        height=user.height,
                        age=user.age,
                        gender=user.gender,
                        neck_cm=user.neck_cm,
                        waist_cm=user.waist_cm,
                        hip_cm=user.hip_cm
                    )
                    
                    # Сохраняем % жира
                    user.last_bodyfat = body_analysis['body_fat']
                    
                    await session.commit()
                    
                    # Формируем развернутый ответ
                    change = weight_kg - old_weight if old_weight else 0
                    
                    response = f"⚖️ <b>Вес записан: {weight_kg} кг</b>\n\n"
                    
                    if old_weight and abs(change) >= 0.1:
                        if change > 0:
                            response += f"📈 <b>Изменение:</b> +{change:.1f} кг\n"
                        else:
                            response += f"📉 <b>Изменение:</b> {change:.1f} кг\n"
                    
                    # Добавляем анализ композиции тела
                    response += f"\n🧬 <b>Анализ тела:</b>\n"
                    response += f"• ИМТ: {body_analysis['bmi']} {body_analysis['bmi_color']}\n"
                    response += f"• Статус: {body_analysis['bmi_status']}\n"
                    response += f"• % жира: {body_analysis['body_fat']}%\n"
                    response += f"• Мышечная масса: {body_analysis['muscle_mass']} кг\n"
                    response += f"• Вода в организме: {body_analysis['body_water']} л\n"
                    
                    # Обновленные нормы
                    response += f"\n🔥 <b>Обновленные нормы:</b>\n"
                    response += f"• Калории: {user.daily_calorie_goal} ккал/день\n"
                    response += f"• Белки: {user.daily_protein_goal} г\n"
                    response += f"• Жиры: {user.daily_fat_goal} г\n"
                    response += f"• Углеводы: {user.daily_carbs_goal} г\n"
                    response += f"• Вода: {user.daily_water_goal} мл\n"
                    
                    await message.answer(response, parse_mode="HTML")
                    return True
            else:
                await message.answer(
                    "❌ Не удалось определить вес.\n\n"
                    "Примеры:\n"
                    "• «Вес 70.5 кг»\n"
                    "• «Взвесился - 72 кг»\n"
                    "• «Мой вес 68.2»",
                    parse_mode="HTML"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error in log_weight: {e}")
            return False
    
    @staticmethod
    async def handle_log_activity(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка записи активности"""
        try:
            # Извлекаем данные активности
            from services.intent_classifier import IntentClassifier
            entities = IntentClassifier.extract_entities(text, "log_activity")
            
            activity_type = entities.get('activity_type')
            duration_min = entities.get('duration_min')
            distance_km = entities.get('distance_km')
            steps = entities.get('steps')
            
            if not activity_type:
                await message.answer(
                    "❌ Не удалось определить тип активности.\n\n"
                    "Примеры:\n"
                    "• «Пробежал 5 км за 30 минут»\n"
                    "• «Ходил 1 час»\n"
                    "• «Плавал 45 минут»",
                    parse_mode="HTML"
                )
                return False
            
            # Рассчитываем калории
            from services.activity_service import estimate_calories_burned
            
            if duration_min:
                calories = estimate_calories_burned(activity_type, duration_min)
            elif distance_km:
                # Приблизительное время для дистанции
                if activity_type == 'running':
                    duration_min = distance_km * 6  # 6 мин/км
                elif activity_type == 'walking':
                    duration_min = distance_km * 12  # 12 мин/км
                else:
                    duration_min = distance_km * 8  # среднее
                calories = estimate_calories_burned(activity_type, duration_min)
            elif steps:
                # Оцениваем время по шагам (примерно 120 шагов в минуту)
                duration_min = steps // 120
                calories = estimate_calories_burned(activity_type, duration_min)
            else:
                calories = 0
            
            # Сохраняем в базу
            from database.db import get_session
            from database.models import User, Activity
            from datetime import datetime
            
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await message.answer(
                        "❌ Сначала создайте профиль командой /set_profile",
                        reply_markup=get_main_keyboard_v2()
                    )
                    return False
                
                activity = Activity(
                    user_id=user.id,
                    activity_type=activity_type,
                    duration_min=duration_min or 0,
                    calories_burned=calories,
                    distance_km=distance_km,
                    steps=steps,
                    datetime=datetime.now()
                )
                session.add(activity)
                await session.commit()
                
                # Формируем ответ
                activity_names = {
                    'running': 'Бег',
                    'walking': 'Ходьба',
                    'workout': 'Тренировка',
                    'yoga': 'Йога',
                    'fitness': 'Фитнес',
                    'swimming': 'Плавание',
                    'cycling': 'Велосипед',
                    'other': 'Активность'
                }
                
                activity_name = activity_names.get(activity_type, 'Активность')
                
                response = f"🏃 <b>Записано: {activity_name}</b>\n\n"
                
                if duration_min:
                    response += f"⏱️ Длительность: {duration_min} мин\n"
                if distance_km:
                    response += f"📏 Дистанция: {distance_km} км\n"
                if steps:
                    response += f"👞 Шаги: {steps:,}\n"
                
                response += f"🔥 Сожжено калорий: {calories} ккал\n"
                
                await message.answer(response, parse_mode="HTML")
                return True
                
        except Exception as e:
            logger.error(f"Error in log_activity: {e}")
            return False
    
    @staticmethod
    async def handle_show_progress(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка запроса прогресса"""
        try:
            # Показываем меню выбора периода
            from keyboards.inline import get_progress_menu
            
            await message.answer(
                "📊 <b>Выберите период для статистики:</b>",
                reply_markup=get_progress_menu(),
                parse_mode="HTML"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error in show_progress: {e}")
            return False
    
    @staticmethod
    async def handle_ask_ai(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка вопроса к AI"""
        try:
            from handlers.ai_assistant import process_ai_question
            await process_ai_question(message, state)
            return True
            
        except Exception as e:
            logger.error(f"Error in ask_ai: {e}")
            return False
    
    @staticmethod
    async def handle_help(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Обработка запроса помощи"""
        try:
            from handlers.common import cmd_help
            await cmd_help(message, state)
            return True
            
        except Exception as e:
            logger.error(f"Error in help: {e}")
            return False
