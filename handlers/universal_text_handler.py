"""
Универсальный обработчик текстовых сообщений.
Если намерение не определено, показывает меню выбора.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import logging
from sqlalchemy import select
from datetime import datetime

from services.intent_classifier import classify
from utils.water_parser import parse_water_amount
from utils.helpers import normalize_exit_command
from handlers.food import cmd_log_food, process_next_food, process_food_search
from handlers.water import cmd_water, add_water_quick
from handlers.shopping import cmd_shopping, add_to_shopping_list, update_list_message, get_or_create_default_list
from handlers.activity import cmd_fitness
from handlers.reminders import cmd_reminders, quick_create_reminder
from utils.parsers import parse_shopping_items
from utils.states import ActivityStates, FoodStates, AIAssistantStates
from database.db import get_session
from database.models import User, Activity
from utils.ai_tools import get_weather
from services.activity import CALORIES_PER_MINUTE
from handlers.ai_assistant import process_single_ai_query  # для однократных ответов
from keyboards.reply import get_main_keyboard

logger = logging.getLogger(__name__)
universal_router = Router()

@universal_router.message(
    F.text, 
    ~F.text.startswith("/"),
    ~StateFilter(FoodStates)  # 🔥 Исключаем состояния FoodStates
)
async def universal_message_handler(message: Message, state: FSMContext):
    """Точка входа для всех текстовых сообщений."""
    await handle_universal_text(message, state)

async def handle_universal_text(message: Message, state: FSMContext, text: str = None):
    """Универсальный обработчик любого текста."""
    if text is None:
        text = message.text
    logger.info(f"📨 Получен текст: {text}")

    # Получаем текущее состояние
    current_state_str = await state.get_state()

    # ========== ЕСЛИ МЫ В ДИАЛОГОВОМ РЕЖИМЕ AI ==========
    if current_state_str == AIAssistantStates.waiting_for_question:
        # Всё, что в диалоговом режиме, обрабатывается ai_assistant, поэтому просто возвращаемся
        # (этот случай не должен сюда попадать, т.к. роутер ai_assistant перехватывает раньше)
        return

    # ========== ОБРАБОТКА НАМЕРЕНИЙ ==========
    intent_data = classify(text)
    intent = intent_data.get("intent")
    text_lower = text.lower()

    # ----- ВОДА -----
    if intent == "water":
        amount = parse_water_amount(text)
        logger.info(f"💧 Извлечено количество воды: {amount}")

        if "купить" in text_lower or "покупки" in text_lower:
            item_text = f"вода {amount} мл" if amount else "вода"
            await add_to_shopping_list(message, item_text)
            await message.answer("✅ Добавлено в список покупок.")
            return

        elif "выпил" in text_lower or "попил" in text_lower or "выпила" in text_lower or "попила" in text_lower:
            if amount:
                success = await add_water_quick(message.from_user.id, amount)
                if success:
                    await message.answer(f"✅ Записано {amount} мл воды.")
                else:
                    await message.answer(
                        "❌ Пользователь не найден. Сначала настройте профиль через /set_profile.",
                        reply_markup=get_main_keyboard()
                    )
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
                f"📝 Вы написали о воде{amount_text}.\n\nВы хотите выпить воду или купить её?",
                reply_markup=keyboard
            )
            return

    # ----- АКТИВНОСТЬ -----
    if intent == "activity":
        act_type = intent_data.get("activity_type")
        duration = intent_data.get("duration")
        distance_km = intent_data.get("distance_km")
        steps = intent_data.get("steps")

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
            cleaned = intent_data.get("cleaned_text", "")
            if cleaned:
                await add_to_shopping_list(message, cleaned)
                await message.answer("✅ Добавлено в список покупок.")
            else:
                await cmd_shopping(message, state)
        return

    # ----- ПРИЁМ ПИЩИ -----
    if intent == "food":
        meal_type = intent_data.get("meal_type", "snack")
        items = intent_data.get("items")
        cleaned = intent_data.get("cleaned_text", "")

        if cleaned:
            await state.update_data(pending_food_text=cleaned)

        if not meal_type:
            await state.update_data(food_intent_data=intent_data)
            await cmd_log_food(message, state)
        else:
            if items:
                from handlers.media_handlers import start_food_input
                await start_food_input(message, state, items, meal_type)
            elif cleaned:
                await state.update_data(meal_type=meal_type)
                await state.set_state(FoodStates.searching_food)
                fake_message = message
                fake_message.text = cleaned
                await process_food_search(fake_message, state)
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

    # ----- AI-ЗАПРОСЫ (ОДНОКРАТНЫЕ) -----
    if intent == "ai":
        # Проверяем, не является ли это коротким словом без вопроса
        words = text.split()
        question_words = ["что", "как", "почему", "зачем", "кто", "где", "когда", "сколько", "?"]
        if len(words) <= 2 and not any(q in text_lower for q in question_words):
            # Короткое слово без вопроса - считаем unknown и показываем меню
            logger.info(f"Short text '{text}' classified as AI, but treating as unknown")
            # Переходим к блоку unknown (не делаем return)
        else:
            logger.info(f"🤖 AI запрос вне режима от {message.from_user.id}: {text}")
            await process_single_ai_query(message, text)
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
        f"📝 Вы написали:\n«{text}»\n\nКуда это добавить?",
        reply_markup=keyboard
    )
    return

# ========== ОБРАБОТЧИКИ КНОПОК ==========
@universal_router.callback_query(F.data == "water_drink")
async def water_drink_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data.get('water_amount')
    user_id = callback.from_user.id

    await callback.answer()

    try:
        if amount:
            success = await add_water_quick(user_id, amount)
            if success:
                await callback.message.answer(f"✅ Записано {amount} мл воды.")
            else:
                await callback.message.answer(
                    "❌ Пользователь не найден. Сначала настройте профиль через /set_profile.",
                    reply_markup=get_main_keyboard()
                )
        else:
            await cmd_water(callback.message, state)
    except Exception as e:
        logger.error(f"water_drink_callback: {e}", exc_info=True)
        await callback.message.answer("❌ Произошла внутренняя ошибка.")
    finally:
        try:
            await callback.message.delete()
        except:
            pass

@universal_router.callback_query(F.data == "water_buy")
async def water_buy_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data.get('water_amount')
    item_text = f"вода {amount} мл" if amount else "вода"

    await callback.answer()

    try:
        await add_to_shopping_list(callback, item_text)
        await callback.message.answer("✅ Добавлено в список покупок.")
    except Exception as e:
        logger.error(f"water_buy_callback: {e}", exc_info=True)
        await callback.message.answer("❌ Произошла внутренняя ошибка.")
    finally:
        try:
            await callback.message.delete()
        except:
            pass

@universal_router.callback_query(F.data == "action_cancel")
async def action_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("❌ Действие отменено.")

@universal_router.callback_query(F.data == "choose_shopping")
async def choose_shopping_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    await callback.answer()
    await add_to_shopping_list(callback, text)

    async with get_session() as session:
        shopping_list = await get_or_create_default_list(callback.from_user.id, session, callback)
        if shopping_list:
            await update_list_message(callback, shopping_list.id)

    try:
        await callback.message.delete()
    except:
        pass

@universal_router.callback_query(F.data == "choose_food")
async def choose_food_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    # Сохраняем текст для использования в food.py
    await state.update_data(pending_food_text=text)
    await callback.answer()
    # Вызываем команду записи еды, передавая user_id
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)
    try:
        await callback.message.delete()
    except:
        pass

@universal_router.callback_query(F.data == "choose_ai")
async def choose_ai_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    await callback.answer()
    await process_single_ai_query(callback.message, text)
    try:
        await callback.message.delete()
    except:
        pass

# ========== ОБРАБОТЧИКИ ДЛЯ ПОДТВЕРЖДЕНИЯ АКТИВНОСТИ ==========
@universal_router.callback_query(F.data == "confirm_activity")
async def confirm_activity_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    act_type = data.get('activity_type')
    duration = data.get('duration')
    if not act_type or not duration:
        await callback.answer()
        await safe_edit(callback, "❌ Ошибка: данные активности не найдены.")
        await state.clear()
        return

    user_id = callback.from_user.id
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await callback.answer()
            await safe_edit(callback, "❌ Пользователь не найден.")
            await state.clear()
            return
        weight = user.weight or 70

    met = CALORIES_PER_MINUTE.get(act_type, 5)
    calories = met * weight * (duration / 60)

    async with get_session() as session:
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

    await callback.answer()
    await safe_edit(
        callback,
        f"✅ Активность записана: {act_type} {duration} мин, сожжено ~{calories:.0f} ккал."
    )
    await state.clear()

@universal_router.callback_query(F.data == "cancel_activity")
async def cancel_activity_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await safe_edit(callback, "❌ Запись активности отменена.")

async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    """Безопасное редактирование сообщения с обработкой ошибки 'message not modified'."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug("Сообщение не изменилось, пропускаем")
        else:
            raise e
