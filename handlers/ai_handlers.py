"""
AI Handlers для NutriBuddy
✅ Распознавание нескольких продуктов с фото
✅ Пошаговый ввод веса для каждого
✅ Автоматический расчёт калорий
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from PIL import Image
import io
from typing import List, Dict, Any

from services.cloudflare_ai import analyze_food_image
from services.food_api import search_food
from services.translator import translate_to_russian, extract_food_items
from keyboards.inline import get_food_selection_keyboard, get_confirmation_keyboard
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)


def _prepare_image(image_bytes: bytes) -> bytes:
    """Оптимизация изображения для Cloudflare"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
    except Exception as e:
        logger.warning(f"⚠️ Image prep error: {e}")
        return image_bytes


@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """
    Обработка фото: распознавание, извлечение продуктов, запуск пошагового ввода.
    """
    try:
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()

        optimized = _prepare_image(file_data)
        await message.answer("🔍 Анализирую изображение через Cloudflare AI...")

        # Распознаём описание (на английском, подробно)
        description_en = await analyze_food_image(
            optimized,
            prompt="List all food items visible in this image. Be specific. Return as a comma-separated list of main ingredients and dishes."
        )

        if not description_en:
            await message.answer("❌ Не удалось распознать. Попробуйте ввести название вручную.")
            return

        logger.info(f"✅ Raw description: {description_en}")

        # Переводим на русский
        description_ru = await translate_to_russian(description_en)
        logger.info(f"✅ Translated description: {description_ru}")

        # Извлекаем отдельные продукты
        items = await extract_food_items(description_en)  # может вернуть список
        if not items:
            items = [description_ru]  # fallback

        logger.info(f"✅ Extracted food items: {items}")

        # Инициализируем состояние для пошагового ввода
        await state.update_data(
            pending_items=items,          # список продуктов для обработки
            current_index=0,               # индекс текущего продукта
            selected_foods=[],              # уже выбранные продукты (с весом)
            ai_description=description_ru
        )

        # Запускаем обработку первого продукта
        await process_next_food(message, state)

    except Exception as e:
        logger.error(f"❌ Photo handler error: {e}", exc_info=True)
        await message.answer("❌ Ошибка обработки фото.")


async def process_next_food(message: Message, state: FSMContext):
    """Запрашивает у пользователя выбор продукта для следующего элемента."""
    data = await state.get_data()
    items = data.get('pending_items', [])
    idx = data.get('current_index', 0)

    if idx >= len(items):
        # Все продукты обработаны
        await finish_meal(message, state)
        return

    current_food = items[idx]
    await state.update_data(current_food_name=current_food)

    # Ищем в OpenFoodFacts
    foods = await search_food(current_food)
    if not foods:
        # Если ничего не нашли, предлагаем ввести вручную
        await message.answer(
            f"🔍 Не найдено в базе для «{current_food}».\n"
            f"Введите название вручную:"
        )
        await state.set_state(FoodStates.manual_food_name)
        return

    # Показываем варианты
    await message.answer(
        f"🧠 Продукт {idx+1}/{len(items)}: «{current_food}»\n"
        f"Выберите подходящий вариант:",
        reply_markup=get_food_selection_keyboard(foods)
    )
    await state.set_state(FoodStates.selecting_food)
    await state.update_data(foods=foods)


@router.callback_query(F.data.startswith("food_"), FoodStates.selecting_food)
async def process_food_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора продукта из списка."""
    data = await state.get_data()
    foods = data.get('foods', [])

    if callback.data == "food_manual":
        await state.set_state(FoodStates.manual_food_name)
        await callback.message.edit_text("📝 Введите название вручную:")
        await callback.answer()
        return

    try:
        index = int(callback.data.split("_")[1])
        if index >= len(foods):
            raise ValueError
        selected = foods[index]
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка выбора", show_alert=True)
        return

    await state.update_data(selected_food=selected)
    await state.set_state(FoodStates.entering_weight)

    await callback.message.edit_text(
        f"✅ {selected['name']} ({selected['calories']} ккал/100г)\n\n"
        f"⚖️ Введите вес в граммах:"
    )
    await callback.answer()


@router.message(FoodStates.manual_food_name, F.text)
async def process_manual_food(message: Message, state: FSMContext):
    """Ручной ввод названия продукта (если не найден в базе)."""
    name = message.text.strip()
    # Создаём пустой продукт
    selected = {
        'name': name,
        'calories': 0,
        'protein': 0,
        'fat': 0,
        'carbs': 0
    }
    await state.update_data(selected_food=selected)
    await state.set_state(FoodStates.entering_weight)

    await message.answer(
        f"✅ Продукт: {name}\n\n"
        f"⚖️ Введите вес в граммах:"
    )


@router.message(FoodStates.entering_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    """Обработка ввода веса для текущего продукта."""
    text = message.text.strip()
    if not text:
        await message.answer("❌ Введите число.")
        return

    try:
        # Извлекаем число из текста
        import re
        match = re.search(r'\d+([.,]\d+)?', text)
        if match:
            weight = float(match.group(0).replace(',', '.'))
        else:
            weight = float(text.replace(',', '.'))
        if weight <= 0 or weight > 10000:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer("❌ Введите корректное число (граммы).")
        return

    data = await state.get_data()
    selected = data.get('selected_food')
    if not selected:
        await message.answer("❌ Ошибка состояния. Начните заново.")
        await state.clear()
        return

    # Рассчитываем КБЖУ
    multiplier = weight / 100
    calories = selected['calories'] * multiplier
    protein = selected.get('protein', 0) * multiplier
    fat = selected.get('fat', 0) * multiplier
    carbs = selected.get('carbs', 0) * multiplier

    # Сохраняем выбранный продукт с весом
    selected_foods = data.get('selected_foods', [])
    selected_foods.append({
        'name': selected['name'],
        'weight': weight,
        'calories': calories,
        'protein': protein,
        'fat': fat,
        'carbs': carbs
    })

    # Увеличиваем индекс и переходим к следующему продукту
    idx = data.get('current_index', 0) + 1
    await state.update_data(
        selected_foods=selected_foods,
        current_index=idx
    )

    # Запрашиваем следующий продукт
    await process_next_food(message, state)


async def finish_meal(message: Message, state: FSMContext):
    """Завершение ввода, сохранение приёма пищи в БД."""
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    ai_description = data.get('ai_description', '')

    if not selected_foods:
        await message.answer("❌ Ни одного продукта не добавлено.")
        await state.clear()
        return

    # Суммируем КБЖУ
    total_cal = sum(f['calories'] for f in selected_foods)
    total_prot = sum(f['protein'] for f in selected_foods)
    total_fat = sum(f['fat'] for f in selected_foods)
    total_carbs = sum(f['carbs'] for f in selected_foods)

    user_id = message.from_user.id
    meal_type = data.get('meal_type', 'snack')  # по умолчанию перекус

    async with get_session() as session:
        meal = Meal(
            user_id=user_id,
            meal_type=meal_type,
            datetime=datetime.now(),
            total_calories=total_cal,
            total_protein=total_prot,
            total_fat=total_fat,
            total_carbs=total_carbs,
            ai_description=ai_description
        )
        session.add(meal)
        await session.flush()  # чтобы получить meal.id

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

    # Формируем отчёт
    lines = [f"🍽️ Записан приём пищи ({meal_type}):"]
    for f in selected_foods:
        lines.append(f"• {f['name']}: {f['weight']}г — {f['calories']:.0f} ккал")
    lines.append(f"\n🔥 Всего: {total_cal:.0f} ккал")
    lines.append(f"🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г")

    await message.answer("\n".join(lines))
    await state.clear()
