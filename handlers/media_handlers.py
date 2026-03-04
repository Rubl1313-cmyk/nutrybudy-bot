"""
Обработчики мультимедиа: фото (распознавание еды) и голос.
Теперь с переводом английских названий на русский.
Исправлена ошибка с переменной description_ru.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from PIL import Image
import io
import traceback
import re
from typing import List

from services.cloudflare_ai import analyze_food_image, transcribe_audio
from services.food_api import search_food
from services.translator import translate_to_russian, extract_food_items
from keyboards.inline import get_food_selection_keyboard, get_confirmation_keyboard
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem, User
from datetime import datetime
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)

def _prepare_image(image_bytes: bytes) -> bytes:
    """Оптимизация изображения для Cloudflare."""
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

# ========== ОБРАБОТКА ФОТО ==========

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """
    Обрабатывает фото еды, переводит названия и запускает пошаговый ввод.
    """
    logger.info("📸 Photo received, starting recognition...")
    try:
        current_state = await state.get_state()
        if current_state and not current_state.startswith("FoodStates"):
            logger.info(f"User in state {current_state}, ignoring photo")
            return

        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        optimized = _prepare_image(file_data)

        await message.answer("🔍 Анализирую изображение через Cloudflare AI...")
        description_en = await analyze_food_image(
            optimized,
            prompt="List all food items visible in this image. Be specific. Return as a comma-separated list."
        )

        if not description_en:
            await message.answer(
                "❌ Не удалось распознать фото. Попробуйте ввести вручную через /log_food."
            )
            return

        logger.info(f"✅ Raw description (en): {description_en}")

        # Извлекаем отдельные продукты (на английском)
        raw_items = await extract_food_items(description_en)
        logger.info(f"✅ Extracted raw items: {raw_items}")

        # Переводим каждый элемент на русский
        translated_items = []
        for item in raw_items:
            translated = await translate_to_russian(item)
            translated_items.append(translated)
        logger.info(f"✅ Translated items: {translated_items}")

        # ✅ Формируем читаемое описание на русском
        description_ru = ", ".join(translated_items) if translated_items else description_en

        await message.answer(f"🧠 <b>Распознано:</b> {description_ru}", parse_mode="HTML")

        await state.update_data(
            pending_items=translated_items,
            current_index=0,
            selected_foods=[],
            ai_description=description_en
        )

        # Запускаем обработку первого продукта
        await process_next_food(message, state)

    except Exception as e:
        logger.error(f"❌ Photo error: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Ошибка при обработке фото. Попробуйте позже.")
        await state.clear()

# ========== ПУБЛИЧНАЯ ФУНКЦИЯ ДЛЯ МНОЖЕСТВЕННОГО ВВОДА ==========
# Используется в универсальном обработчике текста

async def process_next_food(message: Message, state: FSMContext):
    """
    Обрабатывает следующий продукт из списка (публичная версия).
    """
    data = await state.get_data()
    items = data.get('pending_items', [])
    idx = data.get('current_index', 0)

    if idx >= len(items):
        await _finish_meal(message, state)
        return

    current_food = items[idx].strip()
    await state.update_data(current_food_name=current_food)

    foods = await search_food(current_food)
    if not foods:
        await message.answer(
            f"🔍 Для «{current_food}» ничего не найдено. Введите название вручную:"
        )
        await state.set_state(FoodStates.manual_food_name)
        return

    await state.update_data(foods=foods)
    await state.set_state(FoodStates.selecting_food)

    await message.answer(
        f"🔍 Продукт {idx+1}/{len(items)}: «{current_food}»\nВыберите подходящий вариант:",
        reply_markup=get_food_selection_keyboard(foods)
    )

@router.callback_query(F.data.startswith("food_"), FoodStates.selecting_food)
async def process_food_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    foods = data.get('foods', [])

    if callback.data == "food_manual":
        await state.set_state(FoodStates.manual_food_name)
        await callback.message.edit_text("📝 Введите название продукта вручную:")
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
        f"✅ {selected['name']} ({selected['calories']} ккал/100г)\n\n⚖️ Введите вес в граммах:"
    )
    await callback.answer()

@router.message(FoodStates.manual_food_name, F.text)
async def process_manual_food(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("❌ Название не может быть пустым.")
        return

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
        f"✅ Продукт: {name}\n\n⚖️ Введите вес в граммах:"
    )

@router.message(FoodStates.entering_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("❌ Введите число.")
        return

    try:
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

    selected_foods = data.get('selected_foods', [])
    selected_foods.append({
        'name': selected['name'],
        'weight': weight,
        'calories': calories,
        'protein': protein,
        'fat': fat,
        'carbs': carbs
    })

    idx = data.get('current_index', 0) + 1
    await state.update_data(selected_foods=selected_foods, current_index=idx)

    await process_next_food(message, state)

async def _finish_meal(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    ai_description = data.get('ai_description', '')

    if not selected_foods:
        await message.answer("❌ Ни одного продукта не добавлено.")
        await state.clear()
        return

    total_cal = sum(f['calories'] for f in selected_foods)
    total_prot = sum(f['protein'] for f in selected_foods)
    total_fat = sum(f['fat'] for f in selected_foods)
    total_carbs = sum(f['carbs'] for f in selected_foods)

    user_id = message.from_user.id
    meal_type = data.get('meal_type', 'snack')

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Пользователь не найден. Сначала настройте профиль.")
            await state.clear()
            return

        meal = Meal(
            user_id=user.id,
            meal_type=meal_type,
            datetime=datetime.now(),
            total_calories=total_cal,
            total_protein=total_prot,
            total_fat=total_fat,
            total_carbs=total_carbs,
            ai_description=ai_description
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

# ========== ОБРАБОТКА ГОЛОСА ==========

@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    try:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        text = await transcribe_audio(file_data)
        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return
        # Перенаправляем в AI-ассистент
        from handlers.ai_assistant import process_ai_query
        await process_ai_query(message, state, text)
    except Exception as e:
        logger.error(f"Voice error: {e}")
        await message.answer("❌ Ошибка распознавания.")
