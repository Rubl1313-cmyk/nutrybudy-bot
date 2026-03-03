"""
Универсальный обработчик текстовых сообщений.
Если намерение не определено, показывает меню выбора.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import logging

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

logger = logging.getLogger(__name__)
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
    logger.info(f"📨 Получен текст: {text}")

    intent_data = classify(text)
    intent = intent_data.get("intent")
    text_lower = text.lower()

    # ----- ВОДА (спецобработка) -----
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

    # ----- ОСТАЛЬНЫЕ НАМЕРЕНИЯ (activity, reminder, shopping, food, ai) -----
    # ... (остальной код без изменений) ...


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

@universal_router.callback_query(lambda c: c.data == "choose_ai")
async def choose_ai_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('pending_text', '')
    # 🔥 ИМПОРТ ВНУТРИ ФУНКЦИИ
    from handlers.ai_assistant import process_ai_query
    await process_ai_query(callback.message, state, text)
    await callback.message.delete()
    await callback.answer()
