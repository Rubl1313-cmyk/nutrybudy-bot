"""
Обработчик дневника питания (ручной ввод)
✅ Исправлено: ручной ввод теперь ищет в базе OpenFoodFacts
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from datetime import datetime
from typing import List, Dict, Optional

from database.db import get_session
from database.models import User, Meal, FoodItem
from services.food_api import search_food
from keyboards.inline import get_meal_type_keyboard, get_food_selection_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import FoodStates

router = Router()


@router.message(Command("log_food"))
@router.message(F.text == "🍽️ Дневник питания")
async def cmd_log_food(message: Message, state: FSMContext):
    """Начало ручного ввода приёма пищи"""
    await state.clear()

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
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
        reply_markup=get_meal_type_keyboard()
    )


@router.callback_query(F.data.startswith("meal_"), FoodStates.choosing_meal_type)
async def process_meal_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа приёма пищи"""
    meal_type = callback.data.split("_")[1]
    await state.update_data(meal_type=meal_type)
    await state.set_state(FoodStates.searching_food)
    await callback.message.edit_text(
        "🔍 Введи название продукта или отправь фото:"
    )
    await callback.answer()


@router.message(FoodStates.searching_food, F.text)
async def process_food_search(message: Message, state: FSMContext):
    """Поиск продукта по названию (первичный ввод)"""
    query = message.text.strip()
    foods = await search_food(query)

    if not foods:
        await message.answer(
            f"❌ Ничего не найдено.\n\n"
            f"📝 Введите название вручную (будет сохранено с нулевой калорийностью):",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(FoodStates.manual_food_name)
        return

    await state.update_data(foods=foods)
    await state.set_state(FoodStates.selecting_food)
    await message.answer(
        "✅ Выберите продукт:",
        reply_markup=get_food_selection_keyboard(foods[:5])
    )


@router.callback_query(F.data.startswith("food_"), FoodStates.selecting_food)
async def process_food_selection(callback: CallbackQuery, state: FSMContext):
    """Выбор продукта из списка"""
    if callback.data == "food_manual":
        await state.set_state(FoodStates.manual_food_name)
        await callback.message.edit_text("📝 Введите название продукта:")
        await callback.answer()
        return

    try:
        index = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка", show_alert=True)
        return

    data = await state.get_data()
    foods = data.get('foods', [])
    if index >= len(foods):
        await callback.answer("❌ Ошибка", show_alert=True)
        return

    selected = foods[index]
    await state.update_data(selected_food=selected)
    await state.set_state(FoodStates.entering_weight)

    await callback.message.edit_text(
        f"✅ {selected['name']}\n"
        f"📊 {selected.get('calories', 0)} ккал/100г\n\n"
        f"⚖️ Введите вес в граммах:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(FoodStates.manual_food_name, F.text)
async def process_manual_food_name(message: Message, state: FSMContext):
    """Ручной ввод названия – пытаемся найти в базе"""
    query = message.text.strip()
    if not query:
        await message.answer("❌ Введите название.")
        return

    # Сначала ищем в OpenFoodFacts
    foods = await search_food(query)
    if foods:
        # Найдены продукты – предлагаем выбрать
        await state.update_data(foods=foods)
        await state.set_state(FoodStates.selecting_food)
        await message.answer(
            f"✅ Найдено по запросу «{query}»:\n"
            f"Выберите продукт:",
            reply_markup=get_food_selection_keyboard(foods[:5])
        )
        return

    # Ничего не найдено – создаём "пустой" продукт
    selected = {
        'name': query,
        'calories': 0,
        'protein': 0,
        'fat': 0,
        'carbs': 0
    }
    await state.update_data(selected_food=selected)
    await state.set_state(FoodStates.entering_weight)

    await message.answer(
        f"⚠️ Продукт «{query}» не найден в базе.\n"
        f"Он будет сохранён с нулевой калорийностью.\n\n"
        f"⚖️ Введите вес в граммах:"
    )


@router.message(FoodStates.entering_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    """Ввод веса"""
    text = message.text.strip()
    if not text:
        await message.answer("❌ Введите число.")
        return

    try:
        import re
        match = re.search(r'\d+([.,]\d+)?', text)
        if match:
            weight = float(match.group(0).replace(',', '.'))
        else:
            weight = float(text.replace(',', '.'))
        if weight <= 0 or weight > 10000:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer("❌ Введите число от 1 до 10000 г")
        return

    data = await state.get_data()
    food = data.get('selected_food')
    if not food:
        await message.answer("❌ Ошибка. Начните заново.")
        await state.clear()
        return

    multiplier = weight / 100
    calories = food.get('calories', 0) * multiplier
    protein = food.get('protein', 0) * multiplier
    fat = food.get('fat', 0) * multiplier
    carbs = food.get('carbs', 0) * multiplier

    await state.update_data(
        weight=weight,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs
    )
    await state.set_state(FoodStates.confirming)

    await message.answer(
        f"✅ Подтверждение\n\n"
        f"🍽️ {food['name']}\n"
        f"⚖️ {weight} г\n\n"
        f"🔥 {calories:.1f} ккал\n"
        f"🥩 {protein:.1f}г | 🥑 {fat:.1f}г | 🍚 {carbs:.1f}г\n\n"
        f"Всё верно?",
        reply_markup=get_confirmation_keyboard()
    )


@router.callback_query(F.data == "confirm", FoodStates.confirming)
async def confirm_meal(callback: CallbackQuery, state: FSMContext):
    """Сохранение приёма пищи"""
    data = await state.get_data()
    user_id = callback.from_user.id

    async with get_session() as session:
        meal = Meal(
            user_id=user_id,
            meal_type=data['meal_type'],
            datetime=datetime.now(),
            total_calories=data['calories'],
            total_protein=data['protein'],
            total_fat=data['fat'],
            total_carbs=data['carbs']
        )
        session.add(meal)
        await session.flush()

        food_item = FoodItem(
            meal_id=meal.id,
            name=data['selected_food']['name'],
            weight=data['weight'],
            calories=data['calories'],
            protein=data['protein'],
            fat=data['fat'],
            carbs=data['carbs']
        )
        session.add(food_item)
        await session.commit()

    await state.clear()
    await callback.message.edit_text(
        f"✅ Записано!\n"
        f"🔥 {data['calories']:.0f} ккал"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", FoodStates.confirming)
async def cancel_meal(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отменено")
    await callback.answer()
