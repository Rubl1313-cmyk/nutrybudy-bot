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

from services.intent_classifier import classify
from utils.water_parser import parse_water_amount
from handlers.water import add_water_quick, cmd_water
from handlers.activity import cmd_fitness
from utils.parsers import parse_food_items
from utils.states import ActivityStates
from database.db import get_session
from database.models import User, Activity
from services.activity import CALORIES_PER_MINUTE
from utils.ai_tools import get_weather
# Новый импорт
from handlers.media_handlers import process_food_items

logger = logging.getLogger(__name__)
universal_router = Router()

@universal_router.message(F.text, ~F.text.startswith("/"))
async def universal_message_handler(message: Message, state: FSMContext):
    """Точка входа для всех текстовых сообщений, не начинающихся с '/'."""
    current_state = await state.get_state()
    if current_state and current_state.startswith("FoodStates"):
        return
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

    # ----- ПРИЁМ ПИЩИ (НОВЫЙ УНИВЕРСАЛЬНЫЙ МЕХАНИЗМ) -----
    if intent == "food":
        meal_type = intent_data.get("meal_type", "snack")
        # Если классификатор выделил отдельные продукты, используем их
        items = intent_data.get("items")
        if items:
            food_items = [{'name': item, 'weight': 100} for item in items]
        else:
            # Иначе разбираем исходный текст через парсер
            parsed = parse_food_items(text)
            if not parsed:
                # Если не удалось распознать, показываем клавиатуру выбора (старое поведение)
                await show_unknown_keyboard(message, state, text)
                return
            food_items = [{'name': name, 'weight': 100} for name, _, _ in parsed]

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
        weather_info = await get_weather(city)
        await message.answer(weather_info)
        return

    # ----- НЕОПРЕДЕЛЁННОЕ -----
    await state.update_data(pending_text=text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Записать как приём пищи", callback_data="choose_food")],
        [InlineKeyboardButton(text="🤖 Спросить AI", callback_data="choose_ai")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
    ])
    await message.answer(
        f"📝 Вы написали:\n«{text}»\nКуда это добавить?",
        reply_markup=keyboard
    )
    return

# ----- ОБРАБОТЧИКИ КНОПОК ДЛЯ НЕОПРЕДЕЛЁННЫХ ТЕКСТОВ -----

@universal_router.callback_query(lambda c: c.data == "choose_food")
async def choose_food_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора «Записать как приём пищи» для неопределённого текста."""
    data = await state.get_data()
    text = data.get('pending_text', '')
    parsed = parse_shopping_items(text)
    if not parsed:
        await callback.answer("❌ Не удалось распознать продукты.", show_alert=True)
        return
    food_items = [{'name': name, 'weight': 100} for name, _, _ in parsed]
    await state.update_data(selected_foods=[], meal_type='snack')
    await process_food_items(callback.message, state, food_items, meal_type='snack')
    # ✅ УДАЛЕНО: await callback.message.delete()
    await callback.answer()

@universal_router.callback_query(lambda c: c.data == "choose_ai")
async def choose_ai_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    from handlers.ai_assistant import process_single_ai_query
    await process_single_ai_query(callback.message, text)
    await callback.message.delete()
    await callback.answer()

# ----- ОБРАБОТЧИКИ КНОПОК ДЛЯ ВОДЫ -----
@universal_router.callback_query(lambda c: c.data == "water_drink")
async def water_drink_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data.get('water_amount')
    if amount:
        await add_water_quick(callback.from_user.id, amount)
        await callback.message.answer(f"✅ Записано {amount} мл воды.")
    else:
        await cmd_water(callback.message, state)
    await callback.message.delete()
    await callback.answer()


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

async def show_unknown_keyboard(message: Message, state: FSMContext, text: str):
    """Показывает клавиатуру для неопределённого текста."""
    await state.update_data(pending_text=text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Записать как приём пищи", callback_data="choose_food")],
        [InlineKeyboardButton(text="🤖 Спросить AI", callback_data="choose_ai")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
    ])
    await message.answer(
        f"📝 Вы написали:\n«{text}»\nКуда это добавить?",
        reply_markup=keyboard
    )
