from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from database.db import get_session
from database.models import User, Meal, FoodItem
from services.food_api import search_food
from keyboards.inline import get_meal_type_keyboard, get_food_selection_keyboard, get_confirmation_keyboard
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from utils.states import FoodStates
from utils.helpers import get_meal_type_emoji

router = Router()

@router.message(Command("log_food"))
@router.message(F.text == "🍽️ Дневник питания")
async def cmd_log_food(message: Message, state: FSMContext):
    await state.set_state(FoodStates.choosing_meal_type)
    await message.answer(
        "Выбери тип приёма пищи:",
        reply_markup=get_meal_type_keyboard()
    )

@router.callback_query(F.data.startswith("meal_"))
async def process_meal_type(callback: CallbackQuery, state: FSMContext):
    meal_type = callback.data.split("_")[1]
    await state.update_data(meal_type=meal_type)
    await state.set_state(FoodStates.searching_food)
    await callback.message.edit_text(
        "🔍 Введи название продукта (или отправь фото для анализа):"
    )
    await callback.answer()

@router.message(FoodStates.searching_food, F.text)
async def process_food_search(message: Message, state: FSMContext):
    query = message.text
    foods = await search_food(query)
    if not foods:
        await message.answer("❌ Ничего не найдено. Попробуй другое название.")
        return
    await state.update_data(foods=foods)
    await state.set_state(FoodStates.selecting_food)
    await message.answer("Выбери продукт:", reply_markup=get_food_selection_keyboard(foods))

@router.callback_query(F.data.startswith("food_"))
async def process_food_selection(callback: CallbackQuery, state: FSMContext):
    if callback.data == "food_manual":
        await state.set_state(FoodStates.manual_food_name)
        await callback.message.edit_text("Введи название продукта вручную:")
        await callback.answer()
        return
    
    index = int(callback.data.split("_")[1])
    data = await state.get_data()
    foods = data['foods']
    selected = foods[index]
    await state.update_data(selected_food=selected)
    await state.set_state(FoodStates.entering_weight)
    await callback.message.edit_text(
        f"Выбрано: {selected['name']} ({selected['calories']} ккал/100г)\nВведи вес в граммах:"
    )
    await callback.answer()

@router.message(FoodStates.manual_food_name, F.text)
async def process_manual_food(message: Message, state: FSMContext):
    name = message.text
    selected = {'name': name, 'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
    await state.update_data(selected_food=selected)
    await state.set_state(FoodStates.entering_weight)
    await message.answer(f"Введи вес в граммах для '{name}':")

@router.message(FoodStates.entering_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введи положительное число (граммы)")
        return
    
    data = await state.get_data()
    food = data['selected_food']
    multiplier = weight / 100
    calories = food['calories'] * multiplier
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
        f"✅ <b>{food['name']}</b>, {weight} г\n\n"
        f"🔥 Калории: {calories:.1f} ккал\n"
        f"🥩 Белки: {protein:.1f} г | 🥑 Жиры: {fat:.1f} г | 🍚 Углеводы: {carbs:.1f} г\n\n"
        f"Всё верно?",
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "confirm", FoodStates.confirming)
async def confirm_meal(callback: CallbackQuery, state: FSMContext):
    """Сохранение приёма пищи в БД"""
    data = await state.get_data()
    user_id = callback.from_user.id
    
    # ✅ ПРАВИЛЬНО: get_session() без await
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
    await callback.message.edit_text("✅ Приём пищи записан!")
    await callback.answer()

@router.callback_query(F.data == "cancel", FoodStates.confirming)
async def cancel_meal(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Запись отменена.")
    await callback.answer()
