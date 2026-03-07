"""
Обработчик поиска продуктов с КБЖУ.
✅ Команда /search
✅ Inline-кнопки с КБЖУ
✅ Интеграция с существующим вводом веса
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.states import FoodStates
from services.food_search import search_with_autocomplete, format_kbzu
from keyboards.reply import get_cancel_keyboard
from handlers.food import process_weight

router = Router()


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """
    /search <продукт>
    Пример: /search курица
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "🔍 <b>Поиск продуктов</b>\n"
            "Использование: /search <название>\n"
            "Пример: /search гречка",
            parse_mode="HTML"
        )
        return
    
    query = args[1]
    await perform_search(message, state, query)


async def perform_search(message: Message, state: FSMContext, query: str):
    """Выполняет поиск и показывает результаты с КБЖУ."""
    results = await search_with_autocomplete(query, limit=10)
    
    if not results:
        await message.answer(
            f"❌ Ничего не найдено по запросу «{query}».\n"
            "Попробуйте другое название или введите вручную.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # 🔥 Формируем inline-клавиатуру с КБЖУ
    builder = InlineKeyboardBuilder()
    for i, item in enumerate(results):
        kbzu_str = format_kbzu(item)
        kb_text = f"{item['name']} — {kbzu_str}"
        builder.button(
            text=kb_text,
            callback_data=f"food_select_{i}_{query}"
        )
    
    builder.adjust(1)
    builder.button(text="📝 Ввести вручную", callback_data="food_manual_entry")
    builder.button(text="❌ Отмена", callback_data="food_search_cancel")
    
    # 🔥 Сообщение с результатами и КБЖУ
    text = f"🔍 <b>Найдено по запросу «{query}»:</b>\n\n"
    for i, item in enumerate(results[:5], 1):
        kbzu_str = format_kbzu(item)
        text += f"{i}. <b>{item['name']}</b>\n"
        text += f"   {kbzu_str} (на 100г)\n\n"
    
    if len(results) > 5:
        text += f"... и ещё {len(results) - 5} (см. кнопки ниже)\n"
    
    await message.answer(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    # Сохраняем результаты в state
    await state.update_data(search_results=results, search_query=query)


@router.callback_query(F.data.startswith("food_select_"))
async def food_select_callback(callback: CallbackQuery, state: FSMContext):
    """
    ✅ УЛУЧШЕНО: Поддержка выбора готовых блюд с ингредиентами
    """
    data = await state.get_data()
    results = data.get("search_results", [])
    
    try:
        parts = callback.data.split("_")
        index = int(parts[2])
        
        if index >= len(results):
            await callback.answer("❌ Ошибка выбора", show_alert=True)
            return
        
        selected = results[index]
        
        # 🔥 ПРОВЕРКА: Это готовое блюдо или ингредиент?
        if selected.get('source') == 'composite_dish':
            # 🔥 Для готовых блюд - загружаем ингредиенты из базы
            from services.dish_db import get_dish_ingredients
            dish_key = selected.get('dish_key', selected['name'].lower())
            ingredients = get_dish_ingredients(dish_key, total_weight=300)
            
            await state.update_data(
                selected_dish=selected,
                dish_ingredients=ingredients,
                meal_type=data.get("meal_type", "snack")
            )
            
            # 🔥 Показываем блюдо с ингредиентами
            kbzu_str = format_kbzu(selected)
            await callback.message.edit_text(
                f"✅ <b>{selected['name']}</b>\n"
                f"📊 {kbzu_str} (на порцию)\n"
                f"🥘 Ингредиенты: {len(ingredients)} шт\n"
                f"⚖️ Введите общий вес порции (или используйте рекомендуемый):",
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.entering_dish_weight)
        else:
            # 🔥 Обычный ингредиент
            await state.update_data(
                selected_food=selected,
                meal_type=data.get("meal_type", "snack")
            )
            await state.set_state(FoodStates.entering_weight)
            kbzu_str = format_kbzu(selected)
            await callback.message.edit_text(
                f"✅ <b>{selected['name']}</b>\n"
                f"📊 {kbzu_str} (на 100г)\n"
                f"⚖️ Введите вес в граммах:",
                parse_mode="HTML"
            )
        
        await callback.answer()
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка", show_alert=True)


@router.message(FoodStates.entering_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    """
    🔥 Обработка веса для готового блюда
    """
    text = message.text.strip()
    try:
        import re
        match = re.search(r'\d+([.,]\d+)?', text)
        weight = float(match.group(0).replace(',', '.')) if match else float(text.replace(',', '.'))
        if weight <= 0 or weight > 5000:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer("❌ Введите число от 1 до 5000 г")
        return
    
    data = await state.get_data()
    selected_dish = data.get('selected_dish')
    ingredients = data.get('dish_ingredients', [])
    
    if not selected_dish:
        await message.answer("❌ Ошибка. Начните заново.")
        await state.clear()
        return
    
    # 🔥 Масштабируем ингредиенты пропорционально весу
    base_weight = 300  # Базовый вес порции
    multiplier = weight / base_weight
    
    selected_foods = []
    for ing in ingredients:
        ing_weight = ing.get('estimated_weight_grams', 100) * multiplier
        food_data = await _get_food_data_cached(ing['name'])
        nutrients = _calculate_nutrients(food_data, ing_weight)
        
        selected_foods.append({
            'name': ing['name'],
            'weight': ing_weight,
            'calories': nutrients['calories'],
            'protein': nutrients['protein'],
            'fat': nutrients['fat'],
            'carbs': nutrients['carbs']
        })
    
    await state.update_data(selected_foods=selected_foods)
    await finish_meal(message, state)
@router.callback_query(F.data == "food_manual_entry")
async def food_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Ручной ввод продукта."""
    await state.set_state(FoodStates.manual_food_name)
    await callback.message.edit_text("📝 Введите название продукта:")
    await callback.answer()


@router.callback_query(F.data == "food_search_cancel")
async def food_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена поиска."""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Поиск отменён.", reply_markup=get_cancel_keyboard())
    await callback.answer()
