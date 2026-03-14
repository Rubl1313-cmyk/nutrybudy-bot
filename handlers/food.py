"""
Обработчик ручного ввода продуктов.
Теперь использует универсальный механизм из media_handlers (process_food_items).
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.db import get_session
from database.models import User
from keyboards.inline import get_meal_type_keyboard
from keyboards.reply import get_main_keyboard
from utils.states import FoodStates

router = Router()

@router.message(Command("log_food"))
@router.message(F.text == "🍽️ Дневник питания")
async def cmd_log_food(message: Message, state: FSMContext, user_id: int = None):
    """Начало процесса записи приёма пищи."""
    await state.clear()
    if user_id is None:
        user_id = message.from_user.id

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.weight:
            await message.answer(
                "❌ Сначала настрой профиль через /set_profile",
                reply_markup=get_main_keyboard()
            )
            return

    await state.set_state(FoodStates.choosing_meal_type)
    await message.answer(
        "🍽️ <b>Выбери тип приёма пищи:</b>",
        reply_markup=get_meal_type_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("meal_"), FoodStates.choosing_meal_type)
async def process_meal_type(callback: CallbackQuery, state: FSMContext):
    """Сохраняем тип приёма пищи и переходим к вводу текста."""
    meal_type = callback.data.split("_")[1]
    await state.update_data(meal_type=meal_type)
    await state.set_state(FoodStates.searching_food)
    await callback.message.edit_text(
        "🔍 Введи название продукта или блюда (можно перечислить через запятую):"
    )
    await callback.answer()

@router.message(FoodStates.searching_food, F.text)
async def process_food_search(message: Message, state: FSMContext):
    """
    Получаем текст, разбираем на отдельные продукты и запускаем общий процесс.
    """
    text = message.text.strip()
    if not text:
        await message.answer("❌ Введите текст.")
        return

    # Разбираем текст на названия продуктов (используем парсер из shopping)
    parsed = parse_food_items(text)  # возвращает список (name, qty, unit)
    if not parsed:
        await message.answer("❌ Не удалось распознать продукты.")
        return

    # Формируем food_items с весом по умолчанию 100 г
    food_items = [{'name': name, 'weight': 100} for name, _, _ in parsed]

    # Получаем тип приёма пищи из состояния
    data = await state.get_data()
    meal_type = data.get('meal_type', 'snack')

    # Импортируем универсальный процесс (избегаем циклического импорта)
    from handlers.media_handlers import process_food_items

    # Сбрасываем список выбранных продуктов и запускаем обработку
    await state.update_data(selected_foods=[])
    await process_food_items(message, state, food_items, meal_type)
