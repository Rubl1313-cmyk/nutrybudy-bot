"""
Обработчик дневника питания (ручной ввод)
✅ Поддержка составных блюд: разбивка на компоненты, пошаговый ввод
✅ Проверка полноты профиля через is_profile_complete
✅ Запоминание ранее введённого текста из universal_text_handler
✅ Возможность пропустить продукт при множественном вводе
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from datetime import datetime
from typing import List, Dict

from database.db import get_session
from database.models import User, Meal, FoodItem
from services.food_api import search_food
from keyboards.inline import get_meal_type_keyboard, get_food_selection_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import FoodStates
from handlers.profile import is_profile_complete

router = Router()

def split_food_text(text: str) -> List[str]:
    """
    Разбивает текст на отдельные компоненты (продукты).
    Разделители: запятая, "и", "с", "из", "со", "от", "на", "в".
    """
    import re
    text = re.sub(r'\b(и|с|со|из|от|на|в)\b', ',', text.lower())
    parts = [p.strip() for p in text.split(',') if p.strip()]
    return parts

async def perform_food_search(message: Message, state: FSMContext, search_text: str):
    """Выполняет поиск продуктов и переводит состояние в selecting_food."""
    foods = await search_food(search_text)
    if not foods:
        await message.answer(
            f"❌ Ничего не найдено по запросу «{search_text}».\n\n"
            f"📝 Введите название вручную (будет сохранено с нулевой калорийностью):",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(FoodStates.manual_food_name)
        return
    await state.update_data(foods=foods)
    await state.set_state(FoodStates.selecting_food)
    # Показываем кнопку пропуска, если есть pending_items (множественный ввод)
    data = await state.get_data()
    show_skip = 'pending_items' in data
    await message.answer(
        "✅ Выберите продукт:",
        reply_markup=get_food_selection_keyboard(foods[:5], show_skip=show_skip)
    )

async def handle_food_text(message: Message, state: FSMContext, text: str):
    """Универсальная обработка текста с продуктами (один или несколько)."""
    components = split_food_text(text)
    if len(components) > 1:
        # составное блюдо – инициализируем множественный ввод
        await state.update_data(pending_items=components, current_index=0, selected_foods=[])
        await process_next_food(message, state)
    else:
        await perform_food_search(message, state, text)

async def process_next_food(message: Message, state: FSMContext):
    """Обрабатывает следующий продукт из списка pending_items"""
    data = await state.get_data()
    pending = data.get('pending_items', [])
    idx = data.get('current_index', 0)
    if idx >= len(pending):
        await finish_meal(message, state)
        return
    current = pending[idx]
    await state.update_data(current_food_name=current)

    # Выполняем поиск для текущего продукта, с возможностью пропуска
    await perform_food_search(message, state, current)

@router.message(Command("log_food"))
@router.message(F.text == "🍽️ Дневник питания")
async def cmd_log_food(message: Message, state: FSMContext, user_id: int = None):
    """Начало процесса записи приёма пищи."""
    if user_id is None:
        user_id = message.from_user.id

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user or not await is_profile_complete(user):
            await message.answer(
                "❌ Сначала полностью настройте профиль через /set_profile.\n"
                "Необходимо заполнить: вес, рост, возраст, пол, уровень активности, цель и город.",
                reply_markup=get_main_keyboard()
            )
            return

    # НЕ очищаем состояние, чтобы сохранить pending_food_text
    await state.set_state(FoodStates.choosing_meal_type)
    await message.answer(
        "🍽️ <b>Выбери тип приёма пищи:</b>\n\n"
        "💡 <i>Можно сразу отправить фото еды — я распознаю продукты!</i>",
        reply_markup=get_meal_type_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("meal_"), FoodStates.choosing_meal_type)
async def process_meal_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа приёма пищи."""
    # Сразу отвечаем на callback, чтобы избежать таймаута
    await callback.answer()
    
    meal_type = callback.data.split("_")[1]
    await state.update_data(meal_type=meal_type)
    
    # Проверяем, есть ли сохранённый текст для поиска
    data = await state.get_data()
    pending_text = data.get('pending_food_text')
    if pending_text:
        # Удаляем его, чтобы не использовать повторно
        await state.update_data(pending_food_text=None)
        # Обрабатываем текст (разбиваем на компоненты, если есть запятые)
        await handle_food_text(callback.message, state, pending_text)
    else:
        await state.set_state(FoodStates.searching_food)
        await callback.message.edit_text(
            "🔍 Введи название продукта или блюда (можно перечислить через запятую):"
        )

@router.message(FoodStates.searching_food, F.text)
async def process_food_search(message: Message, state: FSMContext):
    """Поиск продуктов – поддерживает составные блюда"""
    text = message.text.strip()
    await handle_food_text(message, state, text)

@router.callback_query(F.data.startswith("food_"), FoodStates.selecting_food)
async def process_food_selection(callback: CallbackQuery, state: FSMContext):
    if callback.data == "food_manual":
        await state.set_state(FoodStates.manual_food_name)
        await callback.message.edit_text("📝 Введите название продукта:")
        await callback.answer()
        return

    if callback.data == "food_skip":
        # Пропускаем текущий продукт, переходим к следующему
        data = await state.get_data()
        idx = data.get('current_index', 0)
        pending = data.get('pending_items', [])
        if pending:
            # Увеличиваем индекс и переходим к следующему
            await state.update_data(current_index=idx + 1)
            await process_next_food(callback.message, state)
        else:
            # Если нет pending_items, просто возвращаемся к поиску
            await state.set_state(FoodStates.searching_food)
            await callback.message.edit_text("🔍 Введи название продукта или блюда:")
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
    """Ручной ввод названия – сначала пробуем поиск"""
    query = message.text.strip()
    if not query:
        await message.answer("❌ Введите название.")
        return

    foods = await search_food(query)
    if foods:
        await state.update_data(foods=foods)
        await state.set_state(FoodStates.selecting_food)
        data = await state.get_data()
        show_skip = 'pending_items' in data
        await message.answer(
            f"✅ Найдено по запросу «{query}»:\n"
            f"Выберите продукт:",
            reply_markup=get_food_selection_keyboard(foods[:5], show_skip=show_skip)
        )
        return

    # ничего не нашли – создаём пустой продукт
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
    text = message.text.strip()
    if not text:
        await message.answer("❌ Введите число.")
        return

    try:
        import re
        match = re.search(r'\d+([.,]\d+)?', text)
        weight = float(match.group(0).replace(',', '.')) if match else float(text.replace(',', '.'))
        if weight <= 0 or weight > 10000:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer("❌ Введите число от 1 до 10000 г")
        return

    data = await state.get_data()
    selected = data.get('selected_food')
    if not selected:
        await message.answer("❌ Ошибка. Начните заново.")
        await state.clear()
        return

    multiplier = weight / 100
    calories = selected.get('calories', 0) * multiplier
    protein = selected.get('protein', 0) * multiplier
    fat = selected.get('fat', 0) * multiplier
    carbs = selected.get('carbs', 0) * multiplier

    # Сохраняем выбранный продукт в список
    selected_foods = data.get('selected_foods', [])
    selected_foods.append({
        'name': selected['name'],
        'weight': weight,
        'calories': calories,
        'protein': protein,
        'fat': fat,
        'carbs': carbs
    })

    # Если есть pending_items (множественный ввод), увеличиваем индекс и переходим к следующему
    pending = data.get('pending_items')
    if pending:
        idx = data.get('current_index', 0) + 1
        await state.update_data(selected_foods=selected_foods, current_index=idx)
        await process_next_food(message, state)
    else:
        # одиночный продукт – сразу завершаем
        await state.update_data(selected_foods=selected_foods)
        await finish_meal(message, state)

async def finish_meal(message: Message, state: FSMContext):
    """Завершение ввода, сохранение приёма пищи"""
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    if not selected_foods:
        await message.answer("❌ Ни одного продукта не добавлено.")
        await state.clear()
        return

    total_cal = sum(f['calories'] for f in selected_foods)
    total_prot = sum(f['protein'] for f in selected_foods)
    total_fat = sum(f['fat'] for f in selected_foods)
    total_carbs = sum(f['carbs'] for f in selected_foods)

    user_telegram_id = message.from_user.id
    meal_type = data.get('meal_type', 'snack')

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден.")
            await state.clear()
            return

        meal = Meal(
            user_id=user.id,
            meal_type=meal_type,
            datetime=datetime.now(),
            total_calories=total_cal,
            total_protein=total_prot,
            total_fat=total_fat,
            total_carbs=total_carbs
        )
        session.add(meal)
        await session.flush()

        for f in selected_foods:
            item = FoodItem(
                meal_id=meal.id,
                name=f['name'],
                weight=f['weight'],
                calories=f['calories'],
                protein=f['protein'],
                fat=f['fat'],
                carbs=f['carbs']
            )
            session.add(item)
        await session.commit()

    lines = [f"🍽️ Записан приём пищи ({meal_type}):"]
    for f in selected_foods:
        lines.append(f"• {f['name']}: {f['weight']}г — {f['calories']:.0f} ккал")
    lines.append(f"\n🔥 Всего: {total_cal:.0f} ккал")
    lines.append(f"🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г")

    await message.answer("\n".join(lines))
    await state.clear()
