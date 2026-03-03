"""
Универсальный обработчик текстовых сообщений.
Вынесен в отдельный модуль для избежания циклических импортов.
"""
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from services.intent_classifier import classify
from utils.water_parser import parse_water_amount
from handlers.food import cmd_log_food
from handlers.water import cmd_water, add_water_quick
from handlers.shopping import cmd_shopping, add_to_shopping_list
from handlers.activity import cmd_fitness
from handlers.reminders import cmd_reminders, quick_create_reminder
from handlers.ai_assistant import process_ai_query
from handlers.media_handlers import process_next_food
from utils.states import ActivityStates
from database.db import get_session
from database.models import User

universal_router = Router()


@universal_router.message(
    lambda message: message.text and not message.text.startswith("/") and message.text not in {
        "🏠 Главное меню", "❌ Отмена", "📊 Прогресс", "💧 Вода",
        "📋 Списки покупок", "👤 Профиль", "🔔 Напоминания",
        "💬 AI Помощник", "🏋️ Активность", "❓ Помощь"
    }
)
async def handle_universal_text(message: Message, state: FSMContext):
    """Универсальный обработчик любого текста."""
    text = message.text
    intent_data = classify(text)
    intent = intent_data.get("intent")

    # Особый случай: вода с объёмом
    if intent == "water":
        amount = parse_water_amount(text)
        if amount is not None:
            # Есть явный объём – сразу добавляем воду
            await add_water_quick(message.from_user.id, amount)
            await message.answer(f"✅ Записано {amount} мл воды.")
            return
        else:
            # Нет объёма – предлагаем выбор: записать воду или добавить в список покупок
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💧 Выпить воду", callback_data="water_drink")],
                [InlineKeyboardButton(text="📋 Купить воду", callback_data="water_buy")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
            ])
            await message.answer(
                f"📝 Вы написали о воде.\n\nВы хотите выпить воду или купить её в магазине?",
                reply_markup=keyboard
            )
            return

    if intent == "activity":
        act_type = intent_data.get("activity_type")
        duration = intent_data.get("duration")
        if act_type and duration:
            await state.update_data(activity_type=act_type, duration=duration)
            await state.set_state(ActivityStates.confirming)
            await message.answer(f"🏃 Активность: {act_type}, {duration} мин. Подтвердить?")
        else:
            await cmd_fitness(message, state)

    elif intent == "reminder":
        title = intent_data.get("reminder_title")
        time = intent_data.get("reminder_time")
        if title and time:
            await quick_create_reminder(message.from_user.id, title, time, "daily")
            await message.answer(f"✅ Напоминание «{title}» на {time} создано.")
        else:
            await cmd_reminders(message, state)

    elif intent == "shopping":
        items = intent_data.get("items")
        if items:
            await add_to_shopping_list(message, ' '.join(items))
            await message.answer("✅ Добавлено в список покупок.")
        else:
            await cmd_shopping(message, state)

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

    else:  # intent == "ai"
        await process_ai_query(message, state, text)


# Обработчики inline-кнопок для воды
@universal_router.callback_query(lambda c: c.data == "water_drink")
async def water_drink_callback(callback, state):
    await callback.message.delete()
    await cmd_water(callback.message, state)
    await callback.answer()

@universal_router.callback_query(lambda c: c.data == "water_buy")
async def water_buy_callback(callback, state):
    await callback.message.delete()
    await add_to_shopping_list(callback.message, "вода")
    await callback.answer()

@universal_router.callback_query(lambda c: c.data == "action_cancel")
async def action_cancel_callback(callback, state):
    await callback.message.delete()
    await callback.message.answer("❌ Действие отменено.")
    await callback.answer()
