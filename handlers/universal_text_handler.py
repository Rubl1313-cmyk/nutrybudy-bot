"""
Универсальный обработчик текстовых сообщений.
Если намерение не определено, показывает меню выбора.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import logging
from sqlalchemy import select

from services.intent_classifier import classify
from utils.water_parser import parse_water_amount
from handlers.food import cmd_log_food
from handlers.water import cmd_water, add_water_quick
from handlers.shopping import cmd_shopping, add_to_shopping_list
from handlers.activity import cmd_fitness
from handlers.reminders import cmd_reminders, quick_create_reminder
from handlers.media_handlers import process_next_food
from utils.parsers import parse_shopping_items
from utils.states import ActivityStates
from database.db import get_session
from database.models import User, Activity
from datetime import datetime
from utils.ai_tools import get_weather

# Убедитесь, что здесь НЕТ импорта from handlers.ai_assistant import process_ai_query

logger = logging.getLogger(__name__)
universal_router = Router()


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
                f"📝 Вы написали о воде{amount_text}.\n\nВы хотите выпить воду или купить её?",
                reply_markup=keyboard
            )
            return

    # ----- АКТИВНОСТЬ -----
    if intent == "activity":
        # Если есть шаги
        if "steps" in intent_data:
            steps = intent_data["steps"]
            # Упрощённый расчёт калорий: 0.04 ккал на шаг
            calories = round(steps * 0.04, 1)
            user_id = message.from_user.id
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                if not user:
                    await message.answer("❌ Сначала настройте профиль.")
                    return
                activity = Activity(
                    user_id=user.id,
                    activity_type="walking",
                    duration=0,
                    distance=steps * 0.00075,  # средняя длина шага 0.75 м
                    calories_burned=calories,
                    steps=steps,
                    datetime=datetime.now(),
                    source="voice"
                )
                session.add(activity)
                await session.commit()
            await message.answer(f"✅ Записано {steps} шагов (сожжено ~{calories} ккал).")
            return

        # Если нет шагов – обычная активность
        act_type = intent_data.get("activity_type")
        duration = intent_data.get("duration")
        if act_type and duration:
            # Сохраняем в состоянии для подтверждения
            await state.update_data(activity_type=act_type, duration=duration)
            await state.set_state(ActivityStates.confirming)
            await message.answer(f"🏃 Активность: {act_type}, {duration} мин. Подтвердить?",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text="✅ Да", callback_data="confirm_activity")],
                                     [InlineKeyboardButton(text="❌ Нет", callback_data="cancel_activity")]
                                 ]))
        else:
            # Неполные данные – запускаем стандартный диалог
            await cmd_fitness(message, state)
        return

    # ----- НАПОМИНАНИЯ -----
    elif intent == "reminder":
        title = intent_data.get("reminder_title")
        time = intent_data.get("reminder_time")
        if title and time:
            await quick_create_reminder(message.from_user.id, title, time, "daily")
            await message.answer(f"✅ Напоминание «{title}» на {time} создано.")
        else:
            await cmd_reminders(message, state)
        return

    # ----- СПИСОК ПОКУПОК -----
    elif intent == "shopping":
        items = intent_data.get("items")
        if items:
            await add_to_shopping_list(message, ' '.join(items))
            await message.answer("✅ Добавлено в список покупок.")
        else:
            await cmd_shopping(message, state)
        return

    # ----- ПРИЁМ ПИЩИ -----
    elif intent == "food":
        meal_type = intent_data.get("meal_type", "snack")
        items = intent_data.get("items")
        if items:
            await state.update_data(
                pending_items=items,
                current_index=0,
                selected_foods=[],
                meal_type=meal_type
            )
            await process_next_food(message, state)
        else:
            await cmd_log_food(message, state)
        return

    # ----- ПОГОДА -----
elif intent == "weather":
        user_id = message.from_user.id
        city = intent_data.get("city")  # город, если указан в тексте (например, "в Мурманске")
        
        if not city:
            # Город не указан в запросе – берём из профиля
            async with get_session() as session:
                from database.models import User
                from sqlalchemy import select
                result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = result.scalar_one_or_none()
                if user and user.city:
                    city = user.city
                else:
                    # Если и в профиле нет города, используем Москву с предупреждением
                    city = "Москва"
                    await message.answer("ℹ️ Город не указан в профиле, используется Москва. Вы можете изменить его в настройках профиля.")
        
        weather_info = await get_weather(city)
        await message.answer(weather_info)
        return

elif intent == "meal_plan":
    # Импортируем внутри, чтобы избежать циклических импортов
    from handlers.meal_plan import cmd_meal_plan
    await cmd_meal_plan(message, state)
    return

    # ----- НЕОПРЕДЕЛЁННОЕ -----
    else:
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


@universal_router.callback_query(lambda c: c.data == "water_buy")
async def water_buy_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data.get('water_amount')
    item_text = f"вода {amount} мл" if amount else "вода"
    await add_to_shopping_list(callback.message, item_text)
    await callback.message.answer("✅ Добавлено в список покупок.")
    await callback.message.delete()
    await callback.answer()


@universal_router.callback_query(lambda c: c.data == "action_cancel")
async def action_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Действие отменено.")
    await callback.answer()


# ----- ОБРАБОТЧИКИ КНОПОК ДЛЯ НЕОПРЕДЕЛЁННЫХ ТЕКСТОВ -----
@universal_router.callback_query(lambda c: c.data == "choose_shopping")
async def choose_shopping_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    await add_to_shopping_list(callback.message, text)
    await callback.message.delete()
    await callback.answer("✅ Добавлено в список покупок")


@universal_router.callback_query(lambda c: c.data == "choose_food")
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


@universal_router.callback_query(lambda c: c.data == "choose_ai")
async def choose_ai_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    # 🔥 Импорт внутри функции для избежания циклического импорта
    from handlers.ai_assistant import process_ai_query
    await process_ai_query(callback.message, state, text)
    await callback.message.delete()
    await callback.answer()


# ----- ОБРАБОТЧИКИ ДЛЯ ПОДТВЕРЖДЕНИЯ АКТИВНОСТИ -----
@universal_router.callback_query(lambda c: c.data == "confirm_activity")
async def confirm_activity_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    act_type = data.get('activity_type')
    duration = data.get('duration')
    if not act_type or not duration:
        await callback.message.edit_text("❌ Ошибка: данные активности не найдены.")
        await state.clear()
        return

    # Рассчитываем калории
    from services.activity import CALORIES_PER_MINUTE
    calories = CALORIES_PER_MINUTE.get(act_type, 5) * duration

    user_id = callback.from_user.id
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден.")
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

    await callback.message.edit_text(f"✅ Активность записана: {act_type} {duration} мин, сожжено ~{calories} ккал.")
    await state.clear()
    await callback.answer()


@universal_router.callback_query(lambda c: c.data == "cancel_activity")
async def cancel_activity_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Запись активности отменена.")
    await callback.answer()
