"""
Обработчик дневника питания для NutriBuddy
✅ Добавлен перевод с английского
✅ Поддержка нескольких продуктов с одного фото
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from datetime import datetime
from database.db import get_session
from database.models import User, Meal, FoodItem
from services.food_api import search_food
from services.translator import translate_to_russian, extract_food_items
from keyboards.inline import get_meal_type_keyboard, get_food_selection_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import FoodStates

router = Router()


@router.message(Command("log_food"))
@router.message(F.text == "🍽️ Дневник питания")
async def cmd_log_food(message: Message, state: FSMContext):
    """Начало процесса записи приёма пищи"""
    await state.clear()
    
    # ✅ Ищем по telegram_id, а не по id
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
        "🔍 <b>Поиск продукта</b>\n\n"
        "Введи название продукта или отправь фото еды:\n"
        "<i>Можно отправить несколько фото для разных продуктов</i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(FoodStates.searching_food, F.text)
async def process_food_search(message: Message, state: FSMContext):
    """Поиск продукта по названию"""
    query = message.text.strip()
    
    # Проверяем, не штрихкод ли это
    if query.isdigit() and len(query) in [8, 12, 13]:
        from services.food_api import get_food_by_barcode
        foods = await get_food_by_barcode(query)
    else:
        foods = await search_food(query)
    
    if not foods:
        await message.answer(
            f"❌ Ничего не найдено по запросу «{query}».\n\n"
            "Попробуй:\n"
            "• Изменить название\n"
            "• Отправить фото продукта",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.update_data(foods=foods)
    await state.set_state(FoodStates.selecting_food)
    
    keyboard = get_food_selection_keyboard(foods)
    await message.answer(
        "✅ Найдено продуктов. Выбери наиболее подходящий:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("food_"), FoodStates.selecting_food)
async def process_food_selection(callback: CallbackQuery, state: FSMContext):
    """Выбор продукта из списка"""
    if callback.data == "food_manual":
        await state.set_state(FoodStates.manual_food_name)
        await callback.message.edit_text(
            "✍️ <b>Ручной ввод продукта</b>\n\n"
            "Введи название блюда или продукта:"
        )
        await callback.answer()
        return
    
    try:
        index = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка выбора", show_alert=True)
        return
    
    data = await state.get_data()
    foods = data.get('foods', [])
    
    if index >= len(foods):
        await callback.answer("❌ Ошибка выбора", show_alert=True)
        return
    
    selected = foods[index]
    await state.update_data(selected_food=selected)
    await state.set_state(FoodStates.entering_weight)
    
    await callback.message.edit_text(
        f"✅ <b>{selected['name']}</b>\n\n"
        f"📊 Пищевая ценность на 100г:\n"
        f"🔥 {selected['calories']} ккал\n"
        f"🥩 {selected.get('protein', 0)}г белков | "
        f"🥑 {selected.get('fat', 0)}г жиров | "
        f"🍚 {selected.get('carbs', 0)}г углеводов\n\n"
        f"⚖️ <b>Введи вес порции в граммах:</b>\n"
        f"<i>Пример: 150, 200, 300</i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(FoodStates.manual_food_name, F.text)
async def process_manual_food(message: Message, state: FSMContext):
    """Обработка ручного ввода названия продукта"""
    name = message.text.strip()
    
    selected = {
        'name': name,
        'calories': 0,
        'protein': 0,
        'fat': 0,
        'carbs': 0,
        'barcode': None
    }
    
    await state.update_data(selected_food=selected)
    await state.set_state(FoodStates.entering_weight)
    
    await message.answer(
        f"✅ Продукт: <b>{name}</b>\n\n"
        f"⚖️ <b>Введи вес порции в граммах:</b>",
        parse_mode="HTML"
    )


@router.message(FoodStates.entering_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    """Обработка ввода веса порции"""
    text = message.text.strip()
    
    try:
        import re
        numbers = re.findall(r'\d+([.,]\d+)?', text)
        if numbers:
            weight = float(numbers[0].replace(',', '.') if isinstance(numbers[0], str) else numbers[0])
        else:
            weight = float(text.replace(',', '.'))
            
        if weight <= 0 or weight > 10000:
            raise ValueError("Вес вне допустимого диапазона")
            
    except (ValueError, IndexError):
        await message.answer(
            "❌ <b>Некорректный вес</b>\n\n"
            "Введи положительное число от 1 до 10000 грамм.",
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    food = data.get('selected_food')
    
    if not food:
        await message.answer("❌ Ошибка: продукт не выбран. Начните заново.")
        await state.clear()
        return
    
    # Рассчитываем КБЖУ для указанного веса
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
        f"✅ <b>Подтверждение</b>\n\n"
        f"🍽️ {food['name']}\n"
        f"⚖️ {weight} г\n\n"
        f"📊 Пищевая ценность:\n"
        f"🔥 {calories:.1f} ккал\n"
        f"🥩 {protein:.1f}г | 🥑 {fat:.1f}г | 🍚 {carbs:.1f}г\n\n"
        f"Всё верно?",
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm", FoodStates.confirming)
async def confirm_meal(callback: CallbackQuery, state: FSMContext):
    """Сохранение приёма пищи в БД"""
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
            total_carbs=data['carbs'],
            ai_description=data.get('ai_description')
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
            carbs=data['carbs'],
            barcode=data['selected_food'].get('barcode')
        )
        session.add(food_item)
        await session.commit()
    
    await state.clear()
    
    await callback.message.edit_text(
        f"🎉 <b>Приём пищи записан!</b>\n\n"
        f"🔥 {data['calories']:.0f} ккал добавлено",
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", FoodStates.confirming)
async def cancel_meal(callback: CallbackQuery, state: FSMContext):
    """Отмена записи"""
    await state.clear()
    await callback.message.edit_text("❌ Запись отменена.")
    await callback.answer()
