"""
Универсальный обработчик текстовых сообщений.
Теперь для всех случаев, связанных с едой, использует process_food_items.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import logging
from sqlalchemy import select
from datetime import datetime

from services.smart_intent_classifier import classify
from utils.water_parser import parse_water_amount
from handlers.water import add_water_quick, cmd_water
from handlers.activity import cmd_fitness
from utils.states import ActivityStates
from database.db import get_session
from database.models import User, Activity, StepsEntry
from services.activity import calculate_activity_calories
from services.weather import get_temperature as get_weather  # ✅ используем правильный модуль
from handlers.media_handlers import process_food_items

logger = logging.getLogger(__name__)
universal_router = Router()

@universal_router.message(F.text, ~F.text.startswith("/"))
async def universal_message_handler(message: Message, state: FSMContext):
    """Точка входа для всех текстовых сообщений, не начинающихся с '/'."""
    logger.info(f"🔍 UNIVERSAL HANDLER: Получено сообщение: {message.text}")
    current_state = await state.get_state()
    logger.info(f"🔍 UNIVERSAL HANDLER: Current state: {current_state}")
    
    if current_state and current_state.startswith("FoodStates"):
        logger.info(f"🔍 UNIVERSAL HANDLER: Пропускаем, состояние FoodStates")
        return
    await handle_universal_text(message, state)

async def handle_universal_text(message: Message, state: FSMContext, text: str = None):
    """Универсальный обработчик любого текста."""
    if text is None:
        text = message.text

    logger.info(f"📨 Получен текст: {text}")

    intent_data = classify(text)
    intent = intent_data.get("intent")
    confidence = intent_data.get("confidence", 0)
    reasoning = intent_data.get("reasoning", "")
    
    logger.info(f"🧠 Классификация: {intent} (уверенность: {confidence:.2f}) - {reasoning}")

    text_lower = text.lower()

    # ----- СМЕШАННЫЕ ЗАПРОСЫ -----
    # Проверяем, есть ли в тексте несколько типов намерений
    all_intents = []
    
    # Вода
    water_amount = intent_data.get("amount")
    if not water_amount:
        water_amount = parse_water_amount(text)
    if water_amount:
        all_intents.append(("water", water_amount))
    
    # Шаги
    steps = intent_data.get("steps")
    if steps:
        all_intents.append(("steps", steps))
    
    # Еда
    food_items = []
    if intent == "food":
        items = intent_data.get("items")
        if items:
            food_items = [{'name': item, 'weight': 100} for item in items]
        else:
            try:
                ai_result = await ai_integration_manager.extract_food_from_text(text)
                if ai_result and ai_result.get('success'):
                    food_items = ai_result['data'].get('food_items', [])
                else:
                    cleaned_text = text.strip()
                    if len(cleaned_text.split()) <= 3:
                        food_items = [{'name': cleaned_text, 'weight': 100}]
                    else:
                        food_items = []
            except Exception as e:
                logger.error(f"AI food extraction failed: {e}")
                cleaned_text = text.strip()
                if len(cleaned_text.split()) <= 3:
                    food_items = [{'name': cleaned_text, 'weight': 100}]
                else:
                    food_items = []
    if food_items:
        all_intents.append(("food", food_items))

    # Если intent = "unknown" но есть продукты в тексте - тоже обрабатываем как еду
    if intent == "unknown" and not food_items:
        # Проверяем есть ли известные продукты в тексте через AI
        try:
            from services.ai_integration_manager import ai_integration_manager
            ai_result = await ai_integration_manager.extract_food_from_text(text)
            if ai_result and ai_result.get('success'):
                food_items = ai_result['data'].get('food_items', [])
                if food_items:
                    all_intents.append(("food", food_items))
        except Exception as e:
            logger.error(f"AI food extraction failed: {e}")
            # Fallback: проверяем по ключевым словам еды
            text_lower = text.lower()
            food_keywords = ['курица', 'борщ', 'суп', 'салат', 'мясо', 'рыба', 'гречка', 'картошка', 'макароны', 'рис', 'хлеб', 'яйцо', 'сыр', 'молоко', 'кефир', 'творог']
            if any(keyword in text_lower for keyword in food_keywords):
                food_items = [{'name': text.strip(), 'weight': 100}]
                all_intents.append(("food", food_items))

    # Если нашли несколько намерений, обрабатываем только основное
    if len(all_intents) > 1:
        logger.info(f"🔄 Найден смешанный запрос: {[intent_type for intent_type, _ in all_intents]}")
        
        # Приоритеты: steps > water > food
        priority_order = {"steps": 1, "water": 2, "food": 3}
        
        # Сортируем по приоритету
        all_intents.sort(key=lambda x: priority_order.get(x[0], 999))
        
        # Обрабатываем только самое высокоприоритетное намерение
        main_intent, data = all_intents[0]
        logger.info(f"🎯 Основное намерение: {main_intent}")
        
        if main_intent == "water":
            await add_water_quick(message.from_user.id, data)
            await message.answer(f"✅ Записано {data} мл воды.")
        elif main_intent == "steps":
            # Записываем шаги
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == message.from_user.id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    steps_entry = StepsEntry(
                        user_id=user.id,
                        steps_count=data,
                        source='text_input'
                    )
                    session.add(steps_entry)
                    await session.commit()
                    
                    goal_steps = user.daily_steps_goal or 10000
                    percentage = (data / goal_steps * 100) if goal_steps > 0 else 0
                    
                    if percentage >= 100:
                        motivation = "🏆 Отлично! Цель по шагам достигнута!"
                    elif percentage >= 50:
                        motivation = "💪 Хорошая работа!"
                    else:
                        motivation = "🚶 Хорошее начало!"
                    
                    await message.answer(f"✅ Записано {data:,} шагов! {motivation}")
        elif main_intent == "food":
            meal_type = intent_data.get("meal_type", "snack")
            await state.update_data(selected_foods=[], meal_type=meal_type)
            await process_food_items(message, state, data, meal_type)
        return

    # Если уверенность низкая, предлагаем выбор
    if confidence < 0.3:
        await show_unknown_keyboard(message, state, text)
        return

    # ----- ВОДА (убрана ветка с покупкой) -----
    if intent == "water":
        amount = intent_data.get("amount")
        if not amount:
            amount = parse_water_amount(text)
        if amount:
            await add_water_quick(message.from_user.id, amount)
            await message.answer(f"✅ Записано {amount} мл воды.")
        else:
            await cmd_water(message, state)
        return

    # ----- ШАГИ -----
    if intent == "steps":
        steps = intent_data.get("steps")
        if steps:
            # Используем новую систему StepsEntry вместо Activity
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == message.from_user.id)
                )
                user = user_result.scalar_one_or_none()
                if not user:
                    await message.answer("❌ Сначала настройте профиль через /set_profile.")
                    return
                
                # Сохраняем в StepsEntry
                steps_entry = StepsEntry(
                    user_id=user.id,
                    steps_count=steps,
                    source='text_input'
                )
                session.add(steps_entry)
                await session.commit()
                
                # Получаем цель для мотивации
                goal_steps = user.daily_steps_goal or 10000
                percentage = (steps / goal_steps * 100) if goal_steps > 0 else 0
                
                if percentage >= 100:
                    motivation = "🏆 Отлично! Цель по шагам достигнута!"
                elif percentage >= 50:
                    motivation = "💪 Хорошая работа!"
                else:
                    motivation = "🚶 Хорошее начало!"
                
                await message.answer(f"✅ Записано {steps:,} шагов! {motivation}")
            return

    # ----- АКТИВНОСТЬ -----
    if intent == "activity":
        act_type = intent_data.get("activity_type")
        duration = intent_data.get("duration")
        distance_km = intent_data.get("distance_km")

        if distance_km and not duration:
            if act_type == "бег":
                pace = 6.0
            elif act_type == "ходьба":
                pace = 12.0
            elif act_type == "велосипед":
                pace = 4.0
            else:
                pace = 8.0
            duration = int(distance_km * pace)

        if act_type and (duration or distance_km):
            if duration and not distance_km:
                await state.update_data(activity_type=act_type, duration=duration)
                await state.set_state(ActivityStates.confirming)
                await message.answer(
                    f"🏃 Активность: {act_type}, {duration} мин. Подтвердить?",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="✅ Да", callback_data="confirm_activity")],
                        [InlineKeyboardButton(text="❌ Нет", callback_data="cancel_activity")]
                    ])
                )
                return
            else:
                user_id = message.from_user.id
                async with get_session() as session:
                    user_result = await session.execute(
                        select(User).where(User.telegram_id == user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    if not user:
                        await message.answer("❌ Сначала настройте профиль через /set_profile.")
                        return
                    
                    # Используем новую функцию с учетом пола и возраста
                    calories = calculate_activity_calories(
                        activity_type=act_type,
                        duration_minutes=duration,
                        weight_kg=user.weight or 70,
                        gender=user.gender,
                        age=user.age,
                        intensity="moderate"
                    )
                    activity = Activity(
                        user_id=user.id,
                        activity_type=act_type,
                        duration=duration,
                        distance=distance_km if distance_km else 0,
                        calories_burned=calories,
                        steps=0,
                        datetime=datetime.now(),
                        source="text"
                    )
                    session.add(activity)
                    await session.commit()
                msg_parts = [f"✅ Активность записана: {act_type}"]
                if duration:
                    msg_parts.append(f"{duration} мин")
                if distance_km:
                    msg_parts.append(f"{distance_km} км")
                msg_parts.append(f"сожжено ~{calories:.0f} ккал")
                await message.answer(" ".join(msg_parts))
                return

        if act_type:
            await state.update_data(activity_type=act_type)
            await cmd_fitness(message, state)
            return
        await cmd_fitness(message, state)
        return

    # ----- ПРИЁМ ПИЩИ -----
    if intent == "food":
        meal_type = intent_data.get("meal_type", "snack")
        items = intent_data.get("items")
        if items:
            food_items = [{'name': item, 'weight': 100} for item in items]
        else:
            # Используем AI для извлечения продуктов
            try:
                from services.ai_integration_manager import ai_integration_manager
                ai_result = await ai_integration_manager.extract_food_from_text(text)
                if ai_result and ai_result.get('success'):
                    food_items = ai_result['data'].get('food_items', [])
                else:
                    # Fallback: используем текст как название продукта
                    cleaned_text = text.strip()
                    if len(cleaned_text.split()) <= 3:
                        food_items = [{'name': cleaned_text, 'weight': 100}]
                    else:
                        await show_unknown_keyboard(message, state, text)
                        return
            except Exception as e:
                logger.error(f"AI food extraction failed: {e}")
                # Fallback: используем текст как название продукта
                cleaned_text = text.strip()
                if len(cleaned_text.split()) <= 3:
                    food_items = [{'name': cleaned_text, 'weight': 100}]
                else:
                    await show_unknown_keyboard(message, state, text)
                    return

        await state.update_data(selected_foods=[], meal_type=meal_type)
        await process_food_items(message, state, food_items, meal_type)
        return

    # ----- ПОГОДА -----
    if intent == "weather":
        user_id = message.from_user.id
        city = intent_data.get("city")
        if not city:
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = result.scalar_one_or_none()
                if user and user.city:
                    city = user.city
                else:
                    city = "Москва"
                    await message.answer("ℹ️ Город не указан в профиле, используется Москва.")
        temperature = await get_weather(city)  # возвращает float
        # Формируем текстовый ответ
        weather_text = f"🌡️ Погода в {city}: {temperature}°C"
        await message.answer(weather_text)
        return

    # ----- AI ЗАПРОСЫ -----
    if intent == "ai":
        from handlers.ai_assistant import process_single_ai_query
        await process_single_ai_query(message, text)
        return

    # ----- НЕОПРЕДЕЛЁННОЕ -----
    await show_unknown_keyboard(message, state, text)
    return

# ----- ОБРАБОТЧИКИ КНОПОК ДЛЯ НЕОПРЕДЕЛЁННЫХ ТЕКСТОВ -----

@universal_router.callback_query(lambda c: c.data == "action_cancel")
async def action_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("❌ Действие отменено.")
    await callback.answer()

# ----- ОБРАБОТЧИКИ ДЛЯ ПОДТВЕРЖДЕНИЯ АКТИВНОСТИ -----
@universal_router.callback_query(lambda c: c.data == "confirm_activity")
async def confirm_activity_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    act_type = data.get('activity_type')
    duration = data.get('duration')
    if not act_type or not duration:
        await safe_edit(callback, "❌ Ошибка: данные активности не найдены.")
        await state.clear()
        return
    calories = CALORIES_PER_MINUTE.get(act_type, 5) * duration
    user_id = callback.from_user.id
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await safe_edit(callback, "❌ Пользователь не найден.")
            await state.clear()
            return
        activity = Activity(
            user_id=user.id,
            activity_type=act_type,
            duration=duration,
            distance=0,
            calories_burned=calories,
            steps=0,
            datetime=datetime.now(),
            source="manual"
        )
        session.add(activity)
        await session.commit()
    await safe_edit(
        callback,
        f"✅ Активность записана: {act_type} {duration} мин, сожжено ~{calories} ккал."
    )
    await state.clear()
    await callback.answer()

@universal_router.callback_query(lambda c: c.data == "cancel_activity")
async def cancel_activity_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(callback, "❌ Запись активности отменена.")
    await callback.answer()

async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    """Безопасное редактирование сообщения."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug("Сообщение не изменилось, пропускаем")
        else:
            raise e

async def _show_undefined_text_keyboard(message: Message, state: FSMContext, text: str):
    """Показывает клавиатуру для неопределённого текста."""
    await state.update_data(pending_text=text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
    ])
    await message.answer(
        f"📝 Вы написали:\n«{text}»\n\n"
        "🤖 <i>AI обрабатывает ваш запрос...</i>\n"
        "Если ничего не происходит, попробуйте переформулировать.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
