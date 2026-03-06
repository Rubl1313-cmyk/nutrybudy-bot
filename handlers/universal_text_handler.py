"""
Универсальный обработчик текстовых сообщений.
✅ Исправлено: добавлен импорт StateFilter
✅ Исправлено: правильная проверка состояний
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter  # ← 🔥 ДОБАВЛЕНО!
from aiogram.exceptions import TelegramBadRequest
import logging
from sqlalchemy import select
from datetime import datetime
from services.intent_classifier import classify
from utils.water_parser import parse_water_amount
from handlers.food import cmd_log_food
from handlers.water import cmd_water, add_water_quick
from handlers.shopping import cmd_shopping, add_to_shopping_list, update_list_message, get_or_create_default_list
from handlers.activity import cmd_fitness
from handlers.reminders import cmd_reminders, quick_create_reminder
from utils.parsers import parse_shopping_items
from utils.states import ActivityStates, FoodStates  # ← 🔥 Добавлен импорт FoodStates
from database.db import get_session
from database.models import User, Activity
from utils.ai_tools import get_weather
from services.activity import CALORIES_PER_MINUTE

logger = logging.getLogger(__name__)
universal_router = Router()


@universal_router.message(F.text, ~F.text.startswith("/"))
async def universal_message_handler(message: Message, state: FSMContext):
    """Точка входа для всех текстовых сообщений, не начинающихся с '/'."""
    # 🔥 ПРОВЕРКА: не перехватываем если пользователь в состоянии ввода еды
    current_state = await state.get_state()
    if current_state and current_state.startswith("FoodStates"):
        return  # Пропускаем, пусть обрабатывает food.py
    
    await handle_universal_text(message, state)


async def handle_universal_text(message: Message, state: FSMContext, text: str = None):
    """Универсальный обработчик любого текста."""
    if text is None:
        text = message.text
    
    logger.info(f"📨 Получен текст: {text}")
    
    intent_data = classify(text)
    intent = intent_data.get("intent")
    text_lower = text.lower()
    
    # ----- ВОДА -----
    if intent == "water":
        amount = parse_water_amount(text)
        
        if "купить" in text_lower or "покупки" in text_lower:
            item_text = f"вода {amount} мл" if amount else "вода"
            await add_to_shopping_list(message, item_text)
            await message.answer("✅ Добавлено в список покупок.")
            return
        elif "выпил" in text_lower or "попил" in text_lower:
            if amount:
                await add_water_quick(message.from_user.id, amount)
                await message.answer(f"✅ Записано {amount} мл воды.")
            else:
                await cmd_water(message, state)
            return
        else:
            await state.update_data(water_amount=amount)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💧 Выпить воду", callback_data="water_drink")],
                [InlineKeyboardButton(text="📋 Купить воду", callback_data="water_buy")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
            ])
            amount_text = f" ({amount} мл)" if amount else ""
            await message.answer(
                f"📝 Вы написали о воде{amount_text}.\nВы хотите выпить воду или купить её?",
                reply_markup=keyboard
            )
            return
    
    # ----- АКТИВНОСТЬ -----
    if intent == "activity":
        act_type = intent_data.get("activity_type")
        duration = intent_data.get("duration")
        distance_km = intent_data.get("distance_km")
        steps = intent_data.get("steps")
        
        # Если есть шаги (приоритет)
        if steps:
            user_id = message.from_user.id
            calories = round(steps * 0.04, 1)
            
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await message.answer("❌ Сначала настройте профиль через /set_profile.")
                    return
                
                activity = Activity(
                    user_id=user.id,
                    activity_type="walking",
                    duration=0,
                    distance=steps * 0.00075,
                    calories_burned=calories,
                    steps=steps,
                    datetime=datetime.now(),
                    source="text"
                )
                session.add(activity)
                await session.commit()
            
            await message.answer(f"✅ Записано {steps} шагов (сожжено ~{calories} ккал).")
            return
        
        # Если есть расстояние, но нет длительности – рассчитываем длительность по темпу
        if distance_km and not duration:
            if act_type == "running":
                pace = 6.0
            elif act_type == "walking":
                pace = 12.0
            elif act_type == "cycling":
                pace = 4.0
            else:
                pace = 8.0
            duration = int(distance_km * pace)
        
        # Если есть длительность или расстояние
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
                    
                    weight = user.weight or 70
                    met = CALORIES_PER_MINUTE.get(act_type, 5)
                    
                    if not duration:
                        pass
                    
                    calories = met * weight * (duration / 60)
                    
                    async with get_session() as session:
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
    
    # ----- НАПОМИНАНИЯ -----
    if intent == "reminder":
        title = intent_data.get("reminder_title")
        time = intent_data.get("reminder_time")
        
        if title and time:
            await quick_create_reminder(message.from_user.id, title, time, "daily")
            await message.answer(f"✅ Напоминание «{title}» на {time} создано.")
        else:
            await cmd_reminders(message, state)
        return
    
    # ----- СПИСОК ПОКУПОК -----
    if intent == "shopping":
        items = intent_data.get("items")
        if items:
            await add_to_shopping_list(message, ' '.join(items))
            await message.answer("✅ Добавлено в список покупок.")
        else:
            await cmd_shopping(message, state)
        return
    
    # ----- ПРИЁМ ПИЩИ -----
    if intent == "food":
        meal_type = intent_data.get("meal_type", "snack")
        items = intent_data.get("items")
        
        if items:
            from handlers.media_handlers import start_food_input
            await start_food_input(message, state, items, meal_type)
        else:
            await cmd_log_food(message, state)
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
        
        weather_info = await get_weather(city)
        await message.answer(weather_info)
        return
    
    # ----- НЕОПРЕДЕЛЁННОЕ -----
    await state.update_data(pending_text=text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 В список покупок", callback_data="choose_shopping")],
        [InlineKeyboardButton(text="🍽️ Записать как приём пищи", callback_data="choose_food")],
        [InlineKeyboardButton(text="🤖 Спросить AI", callback_data="choose_ai")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
    ])
    await message.answer(
        f"📝 Вы написали:\n«{text}»\nКуда это добавить?",
        reply_markup=keyboard
    )
    return


# ----- ОБРАБОТЧИКИ КНОПОК ДЛЯ ВОДЫ -----
@universal_router.callback_query(F.data == "water_drink")
async def water_drink_callback(callback: CallbackQuery, state: FSMContext):
    """✅ Исправлено: правильный порядок операций"""
    data = await state.get_data()
    amount = data.get('water_amount')
    
    # ✅ Сначала отвечаем на callback
    await callback.answer()
    
    if amount:
        await add_water_quick(callback.from_user.id, amount)
        await callback.message.answer(f"✅ Записано {amount} мл воды.")
        await callback.message.delete()
    else:
        await callback.message.delete()
        await cmd_water(callback.message, state)


@universal_router.callback_query(F.data == "water_buy")
async def water_buy_callback(callback: CallbackQuery, state: FSMContext):
    """✅ Исправлено: правильный порядок операций"""
    data = await state.get_data()
    amount = data.get('water_amount')
    item_text = f"вода {amount} мл" if amount else "вода"
    
    # ✅ Сначала отвечаем на callback
    await callback.answer()
    
    await add_to_shopping_list(callback.message, item_text)
    await callback.message.answer("✅ Добавлено в список покупок.")
    await callback.message.delete()


@universal_router.callback_query(F.data == "action_cancel")
async def action_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """✅ Исправлено: правильный порядок операций"""
    # ✅ Сначала отвечаем на callback
    await callback.answer()
    
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Действие отменено.", reply_markup=get_main_keyboard())


# ----- ОБРАБОТЧИКИ КНОПОК ДЛЯ НЕОПРЕДЕЛЁННЫХ ТЕКСТОВ -----
@universal_router.callback_query(F.data == "choose_shopping")
async def choose_shopping_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    await add_to_shopping_list(callback, text)
    
    async with get_session() as session:
        shopping_list = await get_or_create_default_list(callback.from_user.id, session, callback)
        if shopping_list:
            await update_list_message(callback, shopping_list.id)
    
    await callback.message.delete()
    await callback.answer("✅ Добавлено в список покупок")


@universal_router.callback_query(F.data == "choose_food")
async def choose_food_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    items = [name for name, _, _ in parse_shopping_items(text)]
    
    await state.update_data(
        pending_items=items,
        current_index=0,
        selected_foods=[],
        meal_type="snack"
    )
    await process_next_food(callback.message, state)
    await callback.message.delete()
    await callback.answer()


@universal_router.callback_query(F.data == "choose_ai")
async def choose_ai_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    from handlers.ai_assistant import process_ai_query
    await process_ai_query(callback.message, state, text)
    await callback.message.delete()
    await callback.answer()


# ----- ОБРАБОТЧИКИ ДЛЯ ПОДТВЕРЖДЕНИЯ АКТИВНОСТИ -----
@universal_router.callback_query(F.data == "confirm_activity")
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


@universal_router.callback_query(F.data == "cancel_activity")
async def cancel_activity_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(callback, "❌ Запись активности отменена.")
    await callback.answer()


# ----- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ -----
async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    """Безопасное редактирование сообщения с обработкой ошибки 'message not modified'."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug("Сообщение не изменилось, пропускаем")
        else:
            raise e


async def process_next_food(message: Message, state: FSMContext):
    """Обрабатывает следующий продукт из списка pending_items"""
    from handlers.food import process_food_search
    data = await state.get_data()
    pending = data.get('pending_items', [])
    idx = data.get('current_index', 0)
    
    if idx >= len(pending):
        await finish_meal(message, state)
        return
    
    current = pending[idx]
    await state.update_data(current_food_name=current)
    
    from services.food_api import search_food
    foods = await search_food(current)
    
    if not foods:
        await message.answer(
            f"🔍 Для «{current}» ничего не найдено.\nВведите название вручную:"
        )
        await state.set_state(FoodStates.manual_food_name)
        return
    
    await state.update_data(foods=foods)
    await state.set_state(FoodStates.selecting_food)
    
    from keyboards.inline import get_food_selection_keyboard
    await message.answer(
        f"🔍 Продукт {idx+1}/{len(pending)}: «{current}»\nВыберите подходящий вариант:",
        reply_markup=get_food_selection_keyboard(foods[:5])
    )


async def finish_meal(message: Message, state: FSMContext):
    """Завершение ввода, сохранение приёма пищи"""
    from database.models import Meal, FoodItem
    from sqlalchemy import select
    
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    
    if not selected_foods:
        await message.answer("❌ Ни одного продукта не добавлено.")
        await state.clear()
        return
    
    total_cal = sum(f['calories'] for f in selected_foods)
    total_prot = sum(f['protein'] for f in selected_foods)
    total_fat = sum(f['fat'] for f in selected_foods)
    total_carbs = sum(f['carbs'] for f in selected_foods)
    
    user_telegram_id = message.from_user.id
    meal_type = data.get('meal_type', 'snack')
    
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден.")
            await state.clear()
            return
        
        meal = Meal(
            user_id=user.id,
            meal_type=meal_type,
            datetime=datetime.now(),
            total_calories=total_cal,
            total_protein=total_prot,
            total_fat=total_fat,
            total_carbs=total_carbs
        )
        session.add(meal)
        await session.flush()
        
        for f in selected_foods:
            item = FoodItem(
                meal_id=meal.id,
                name=f['name'],
                weight=f['weight'],
                calories=f['calories'],
                protein=f['protein'],
                fat=f['fat'],
                carbs=f['carbs']
            )
            session.add(item)
        
        await session.commit()
    
    lines = [f"🍽️ Записан приём пищи ({meal_type}):"]
    for f in selected_foods:
        lines.append(f"• {f['name']}: {f['weight']}г — {f['calories']:.0f} ккал")
    lines.append(f"\n🔥 Всего: {total_cal:.0f} ккал")
    lines.append(f"🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г")
    
    await message.answer("\n".join(lines))
    await state.clear()


# 🔥 ИМПОРТ В КОНЦЕ ФАЙЛА (для избежания циклических импортов)
from keyboards.reply import get_main_keyboard
