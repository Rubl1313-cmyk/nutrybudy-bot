"""
Универсальный обработчик текстовых сообщений.
Вынесен в отдельный модуль для избежания циклических импортов.
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from services.intent_classifier import classify
from handlers.food import cmd_log_food
from handlers.water import cmd_water
from handlers.shopping import cmd_shopping, add_to_shopping_list
from handlers.activity import cmd_fitness
from handlers.reminders import cmd_reminders, quick_create_reminder
from handlers.ai_assistant import process_ai_query
from handlers.media_handlers import process_next_food
from utils.states import ActivityStates
from database.db import get_session
from database.models import User

# Создаём отдельный роутер для универсального обработчика
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

    if intent == "water":
        await cmd_water(message, state)

    elif intent == "activity":
        act_type = intent_data.get("activity_type")
        duration = intent_data.get("duration")
        if act_type and duration:
            # Сохраняем и переходим к подтверждению
            await state.update_data(activity_type=act_type, duration=duration)
            await state.set_state(ActivityStates.confirming)
            await message.answer(f"🏃 Активность: {act_type}, {duration} мин. Подтвердить?")
        else:
            await cmd_fitness(message, state)

    elif intent == "reminder":
        title = intent_data.get("reminder_title")
        time = intent_data.get("reminder_time")
        if title and time:
            # Быстрое создание
            await quick_create_reminder(message.from_user.id, title, time, "daily")
            await message.answer(f"✅ Напоминание «{title}» на {time} создано.")
        else:
            await cmd_reminders(message, state)

    elif intent == "shopping":
        items = intent_data.get("items")
        if items:
            # Добавляем все товары в список
            await add_to_shopping_list(message, ' '.join(items))
            await message.answer("✅ Добавлено в список покупок.")
        else:
            await cmd_shopping(message, state)

    elif intent == "food":
        meal_type = intent_data.get("meal_type", "snack")
        items = intent_data.get("items")
        if items:
            # Запускаем множественный ввод
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
