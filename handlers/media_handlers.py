"""
Обработчики мультимедиа: фото (распознавание еды) и голос.
✅ Полная обработка множественных ингредиентов с выбором вариантов
✅ Сохранение весов от AI
✅ Подробное логирование
✅ Пагинация при большом количестве вариантов (кнопка "Еще")
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from PIL import Image
import io
import traceback
import re
import asyncio
import json
import math
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime

from services.cloudflare_ai import identify_food_cascade
from services.food_api import LOCAL_FOOD_DB, get_product_variants
from services.translator import translate_dish_name, translate_to_russian
from services.dish_db import COMPOSITE_DISHES, get_dish_ingredients, find_matching_dishes
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem, User
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)

# Количество вариантов на одной странице
VARIANTS_PER_PAGE = 5

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def _prepare_image(image_bytes: bytes) -> bytes:
    """Оптимизация изображения для Cloudflare AI."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=90, optimize=True)
        return output.getvalue()
    except Exception as e:
        logger.warning(f"⚠️ Image prep error: {e}")
        return image_bytes

async def _get_food_data_cached(name: str, return_variants: bool = False) -> Union[Dict, List[Dict]]:
    """
    Получает данные продукта из локальной базы ингредиентов.
    Если return_variants=True и есть несколько вариантов, возвращает список.
    """
    name_lower = name.lower().strip()
    logger.info(f"🔍 _get_food_data_cached: ищем '{name_lower}', return_variants={return_variants}")

    variants = get_product_variants(name_lower)
    logger.info(f"🔍 Найдено вариантов: {len(variants)}")

    if return_variants and len(variants) > 1:
        logger.info(f"🔍 Возвращаем список вариантов: {[v['name'] for v in variants]}")
        return variants

    if variants:
        best = variants[0]
        logger.info(f"🔍 Возвращаем лучший вариант: {best['name']} (cal: {best.get('calories')})")
        return {
            'name': best['name'],
            'base_calories': best.get('calories', 0),
            'base_protein': best.get('protein', 0),
            'base_fat': best.get('fat', 0),
            'base_carbs': best.get('carbs', 0),
            'source': 'local',
            'key': best.get('key', name_lower)
        }

    logger.warning(f"🔍 Варианты не найдены, возвращаем заглушку для '{name}'")
    return {
        'name': name,
        'base_calories': 0,
        'base_protein': 0,
        'base_fat': 0,
        'base_carbs': 0,
        'source': 'unknown'
    }

async def _safe_edit_message(bot, chat_id: int, message_id: int, text: str, reply_markup=None, parse_mode="HTML"):
    """Безопасное редактирование сообщения с обработкой ошибок."""
    try:
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            logger.debug(f"⚠️ Message not modified: {message_id}")
            return False
        elif "query is too old" in str(e).lower():
            logger.warning(f"⏱️ Query too old for message {message_id}")
            return False
        else:
            logger.error(f"❌ Edit error: {e}")
            return False
    except Exception as e:
        logger.error(f"❌ Unexpected edit error: {e}")
        return False

async def _send_progress_update(
    bot,
    chat_id: int,
    progress_msg_id: int,
    stage: int,
    progress: int,
    total_stages: int = 5
):
    """Отправляет обновление прогресса пользователю."""
    try:
        stages = [
            "📸 Загрузка изображения...",
            "🔍 Анализ изображения (AI)...",
            "🧠 Обработка результатов...",
            "📊 Поиск в базе продуктов...",
            "✅ Готово!"
        ]
        current_stage = min(stage, len(stages) - 1)
        filled = int(progress // 10)
        green_squares = "🟩" * filled
        empty_squares = "⬜" * (10 - filled)
        progress_bar = green_squares + empty_squares

        text = (
            f"🔄 <b>Анализ изображения</b>\n"
            f"{progress_bar}\n"
            f"<b>{progress}%</b>\n"
            f"<i>{stages[current_stage]}</i>\n"
            f"Шаг {current_stage + 1} из {total_stages}\n"
            f"<i>⏱️ Это займёт около 15-20 секунд</i>"
        )
        await _safe_edit_message(bot, chat_id, progress_msg_id, text)
    except Exception as e:
        logger.warning(f"⚠️ Progress update failed: {e}")

def _calculate_nutrients(base: Dict, weight: float) -> Dict:
    """Рассчитывает КБЖУ для заданного веса."""
    if weight <= 0:
        return {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
    multiplier = weight / 100.0
    base_calories = float(base.get('base_calories', 0) or 0)
    base_protein = float(base.get('base_protein', 0) or 0)
    base_fat = float(base.get('base_fat', 0) or 0)
    base_carbs = float(base.get('base_carbs', 0) or 0)
    return {
        'calories': round(base_calories * multiplier, 1),
        'protein': round(base_protein * multiplier, 1),
        'fat': round(base_fat * multiplier, 1),
        'carbs': round(base_carbs * multiplier, 1)
    }

async def _send_product_card(
    chat_id: int,
    bot,
    index: int,
    food: Dict,
    totals_msg_id: int
) -> int:
    """Отправляет карточку продукта с кнопками управления весом."""
    weight = food.get('weight', 0) or 0
    weight_str = f"{weight} г" if weight else "0 г"
    nutrients = _calculate_nutrients(food, weight)

    text = (
        f"<b>{index+1}. {food['name']}</b>\n"
        f"⚖️ Вес: {weight_str}\n"
        f"🔥 {nutrients['calories']:.0f} ккал | 🥩 {nutrients['protein']:.1f}г | 🥑 {nutrients['fat']:.1f}г | 🍚 {nutrients['carbs']:.1f}г"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➖10", callback_data=f"weight_dec_{index}_10_{totals_msg_id}"),
        InlineKeyboardButton(text="➕10", callback_data=f"weight_inc_{index}_10_{totals_msg_id}"),
        InlineKeyboardButton(text="50", callback_data=f"weight_set_{index}_50_{totals_msg_id}"),
        InlineKeyboardButton(text="100", callback_data=f"weight_set_{index}_100_{totals_msg_id}"),
        InlineKeyboardButton(text="200", callback_data=f"weight_set_{index}_200_{totals_msg_id}"),
        InlineKeyboardButton(text="❌", callback_data=f"weight_del_{index}_{totals_msg_id}")
    ]])
    msg = await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")
    return msg.message_id

async def _show_final_interface(
    message: Message,
    state: FSMContext,
    selected_foods: List[Dict],
    meal_type: str
):
    """Показывает итоговый интерфейс с карточками продуктов."""
    total_cal = sum(f['calories'] for f in selected_foods)
    total_prot = sum(f['protein'] for f in selected_foods)
    total_fat = sum(f['fat'] for f in selected_foods)
    total_carbs = sum(f['carbs'] for f in selected_foods)

    totals_text = (
        f"🍽️ <b>Приём пищи ({meal_type}):</b>\n"
        f"🔥 {total_cal:.0f} ккал | 🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г"
    )

    totals_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_food")],
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")
        ]
    ])

    totals_msg = await message.answer(totals_text, reply_markup=totals_keyboard, parse_mode="HTML")

    product_msg_ids = []
    for i, food in enumerate(selected_foods):
        logger.info(f"📦 Creating product card for {food['name']} with weight {food.get('weight')}")
        msg_id = await _send_product_card(
            message.chat.id,
            message.bot,
            i,
            food,
            totals_msg.message_id
        )
        product_msg_ids.append(msg_id)

    await state.update_data(
        selected_foods=selected_foods,
        totals_msg_id=totals_msg.message_id,
        product_msg_ids=product_msg_ids,
        meal_type=meal_type
    )

async def _show_variants_page(
    message: Message,
    state: FSMContext,
    variants: List[Dict],
    current_item: Dict,
    meal_type: str,
    current_index: int,
    page: int,
    total_pages: int
):
    """
    Отображает одну страницу со списком вариантов продукта.
    """
    start = page * VARIANTS_PER_PAGE
    end = min(start + VARIANTS_PER_PAGE, len(variants))
    page_variants = variants[start:end]

    # Формируем клавиатуру
    keyboard = []
    for variant in page_variants:
        btn_text = f"{variant['name']} ({variant['calories']} ккал)"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"select_variant_{variant['key']}")])

    # Навигационные кнопки
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"variants_page_{page-1}"))
    if page + 1 < total_pages:
        remaining = len(variants) - end
        nav_buttons.append(InlineKeyboardButton(text=f"➡️ Еще ({remaining})", callback_data=f"variants_page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")])

    text = (
        f"🔍 Для «{current_item['name']}» найдено {len(variants)} вариантов "
        f"(страница {page+1}/{total_pages}):\n"
        f"Выберите подходящий:"
    )

    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

    # Сохраняем состояние для навигации
    await state.update_data(
        all_variants=variants,
        current_item=current_item,
        meal_type=meal_type,
        current_index=current_index,
        food_items= (await state.get_data()).get('pending_food_items'),
        variants_page=page,
        variants_total_pages=total_pages
    )

async def process_food_items(
    message: Message,
    state: FSMContext,
    food_items: List[Dict],
    meal_type: str,
    start_index: int = 0
):
    """
    Обрабатывает список food_items последовательно.
    Сначала проверяет, не является ли продукт готовым блюдом.
    Если да – показывает список готовых блюд.
    Иначе – обрабатывает как ингредиент с выбором вариантов.
    """
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])

    if start_index >= len(food_items):
        logger.info(f"✅ Все продукты обработаны, всего: {len(selected_foods)}")
        await _show_final_interface(message, state, selected_foods, meal_type)
        return

    current_item = food_items[start_index]
    product_name = current_item['name']
    logger.info(f"🔄 Обрабатываем продукт {start_index+1}/{len(food_items)}: {current_item}")

    # 1. Ищем готовые блюда по названию продукта
    from services.dish_db import find_matching_dishes
    matches = find_matching_dishes(product_name, threshold=0.5)  # используем высокий порог

    if matches:
        # Найдены готовые блюда – показываем список для выбора
        # Сохраняем контекст для продолжения после выбора
        await state.update_data(
            pending_food_items=food_items,
            pending_index=start_index,
            pending_meal_type=meal_type,
            pending_weight=current_item.get('weight', 100),
            selected_foods=selected_foods
        )
        # Показываем список готовых блюд (используем существующую функцию)
        await _show_dish_selection_for_product(message, state, matches, current_item, meal_type)
        return

    # 2. Если готовых блюд нет – ищем ингредиенты
    # Получаем все варианты для текущего продукта как ингредиента
    variants = await _get_food_data_cached(product_name, return_variants=True)

    # Если вариантов нет или один – обрабатываем как единичный продукт
    if not isinstance(variants, list) or len(variants) == 0:
        # Fallback: если список пуст, создаём заглушку
        food_data = {
            'name': product_name,
            'base_calories': 0,
            'base_protein': 0,
            'base_fat': 0,
            'base_carbs': 0,
            'source': 'unknown'
        }
        weight = current_item.get('weight', 100)
        nutrients = _calculate_nutrients(food_data, weight)

        selected_food = {
            'name': food_data['name'],
            'base_calories': food_data['base_calories'],
            'base_protein': food_data['base_protein'],
            'base_fat': food_data['base_fat'],
            'base_carbs': food_data['base_carbs'],
            'weight': weight,
            'calories': nutrients['calories'],
            'protein': nutrients['protein'],
            'fat': nutrients['fat'],
            'carbs': nutrients['carbs'],
            'source': 'unknown',
            'ai_confidence': current_item.get('ai_confidence', 0.5)
        }

        selected_foods.append(selected_food)
        await state.update_data(selected_foods=selected_foods)
        await process_food_items(message, state, food_items, meal_type, start_index + 1)
        return

    if len(variants) == 1:
        # Единственный вариант – сразу добавляем
        variant = variants[0]
        food_data = {
            'name': variant['name'],
            'base_calories': variant.get('calories', 0),
            'base_protein': variant.get('protein', 0),
            'base_fat': variant.get('fat', 0),
            'base_carbs': variant.get('carbs', 0),
            'source': 'local'
        }
        weight = current_item.get('weight', 100)
        nutrients = _calculate_nutrients(food_data, weight)

        selected_food = {
            'name': food_data['name'],
            'base_calories': food_data['base_calories'],
            'base_protein': food_data['base_protein'],
            'base_fat': food_data['base_fat'],
            'base_carbs': food_data['base_carbs'],
            'weight': weight,
            'calories': nutrients['calories'],
            'protein': nutrients['protein'],
            'fat': nutrients['fat'],
            'carbs': nutrients['carbs'],
            'source': 'local',
            'ai_confidence': current_item.get('ai_confidence', 0.8)
        }

        selected_foods.append(selected_food)
        await state.update_data(selected_foods=selected_foods)
        await process_food_items(message, state, food_items, meal_type, start_index + 1)
        return

    # Несколько вариантов – нужен выбор с пагинацией
    total_pages = math.ceil(len(variants) / VARIANTS_PER_PAGE)

    await state.update_data(
        pending_food_items=food_items,
        pending_index=start_index,
        pending_meal_type=meal_type,
        pending_weight=current_item.get('weight', 100),
        selected_foods=selected_foods
    )

    await _show_variants_page(
        message, state, variants, current_item, meal_type,
        current_index=start_index, page=0, total_pages=total_pages
    )

async def _show_dish_selection_for_product(
    message: Message,
    state: FSMContext,
    matches: list,
    current_item: Dict,
    meal_type: str
):
    """Показывает список готовых блюд для текущего продукта."""
    text = f"🍽 <b>«{current_item['name']}» может быть готовым блюдом</b>\n\n"
    text += "Найдены похожие блюда в базе:\n"

    # Сохраняем matches в состоянии для доступа по индексу
    await state.update_data(dish_matches=matches)

    builder = InlineKeyboardBuilder()
    for idx, match in enumerate(matches):
        btn_text = f"{match['name']} (совпадение {match['score']*100:.0f}%)"
        builder.button(text=btn_text, callback_data=f"select_dish_idx_{idx}")
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="❌ Нет, это ингредиент", callback_data="continue_ingredient")
    )

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    # Контекст для продолжения уже сохранён в состоянии (pending_food_items, pending_index и т.д.)

# ========== ОБРАБОТЧИК ПАГИНАЦИИ ==========

@router.callback_query(F.data.startswith("variants_page_"))
async def variants_page_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик переключения страниц при выборе вариантов."""
    page = int(callback.data.split("_")[2])
    data = await state.get_data()

    variants = data.get('all_variants')
    current_item = data.get('current_item')
    meal_type = data.get('meal_type')
    current_index = data.get('current_index')
    total_pages = data.get('variants_total_pages', 1)

    if not variants or not current_item:
        await callback.answer("❌ Ошибка: данные не найдены", show_alert=True)
        await callback.message.delete()
        return

    await _show_variants_page(
        callback.message, state, variants, current_item, meal_type,
        current_index, page, total_pages
    )
    await callback.answer()
    await callback.message.delete()

# ========== ОБРАБОТЧИК ВЫБОРА ВАРИАНТА ==========

@router.callback_query(F.data.startswith("select_variant_"))
async def select_variant_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора варианта продукта."""
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("❌ Ошибка", show_alert=True)
        return

    product_key = parts[2]
    data = await state.get_data()

    if product_key not in LOCAL_FOOD_DB:
        await callback.answer("❌ Продукт не найден", show_alert=True)
        return

    product = LOCAL_FOOD_DB[product_key]
    weight = data.get('pending_weight', 100)
    meal_type = data.get('pending_meal_type', 'snack')
    food_items = data.get('pending_food_items', [])
    current_index = data.get('pending_index', 0)

    # Создаём запись для выбранного продукта
    food_data = {
        'name': product['name'],
        'base_calories': product.get('calories', 0),
        'base_protein': product.get('protein', 0),
        'base_fat': product.get('fat', 0),
        'base_carbs': product.get('carbs', 0),
        'source': 'local'
    }
    nutrients = _calculate_nutrients(food_data, weight)

    selected_food = {
        'name': food_data['name'],
        'base_calories': food_data['base_calories'],
        'base_protein': food_data['base_protein'],
        'base_fat': food_data['base_fat'],
        'base_carbs': food_data['base_carbs'],
        'weight': weight,
        'calories': nutrients['calories'],
        'protein': nutrients['protein'],
        'fat': nutrients['fat'],
        'carbs': nutrients['carbs'],
        'source': 'local',
        'ai_confidence': 0.8
    }

    # Добавляем в список выбранных
    selected_foods = data.get('selected_foods', [])
    selected_foods.append(selected_food)
    await state.update_data(selected_foods=selected_foods)

    # Переходим к следующему продукту
    await callback.message.delete()
    await process_food_items(
        callback.message,
        state,
        food_items,
        meal_type,
        current_index + 1
    )
    await callback.answer()

# ========== ОСНОВНОЙ ОБРАБОТЧИК ФОТО ==========

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото: каскадное распознавание с прогресс-баром."""
    data = await state.get_data()

    if data.get('last_photo_id') == message.message_id:
        logger.info(f"📸 Duplicate photo ignored: {message.message_id}")
        return

    logger.info(f"📸 Photo received, message_id={message.message_id}")

    progress_msg = None
    try:
        current_state = await state.get_state()
        if current_state and not current_state.startswith("FoodStates"):
            logger.info(f"⚠️ User in state {current_state}, ignoring photo")
            return

        progress_msg = await message.answer(
            "🔄 <b>Анализ изображения</b>\n"
            "🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜\n"
            "<b>0%</b>\n"
            "<i>📸 Загрузка изображения...</i>\n"
            "Шаг 1 из 5\n"
            "<i>⏱️ Это займёт около 15-20 секунд</i>",
            parse_mode="HTML"
        )

        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=0,
            progress=10,
            total_stages=5
        )

        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()

        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=0,
            progress=20,
            total_stages=5
        )
        optimized = _prepare_image(file_data)

        await state.update_data(
            pending_photo_bytes=file_data,
            pending_photo_optimized=optimized,
            last_photo_id=message.message_id,
            progress_msg_id=progress_msg.message_id
        )

        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=1,
            progress=30,
            total_stages=5
        )

        async def progress_callback(stage: int, progress: int):
            mapped_progress = 30 + (progress // 2)
            await _send_progress_update(
                message.bot,
                message.chat.id,
                progress_msg.message_id,
                stage=1,
                progress=mapped_progress,
                total_stages=5
            )

        try:
            result = await asyncio.wait_for(
                identify_food_cascade(optimized, progress_callback=progress_callback),
                timeout=120
            )
        except asyncio.TimeoutError:
            await _safe_edit_message(
                message.bot,
                message.chat.id,
                progress_msg.message_id,
                "⏱️ Превышено время анализа. Попробуйте другое фото."
            )
            if progress_msg:
                await progress_msg.delete()
            await state.clear()
            return

        # Логируем полный ответ AI
        logger.info(f"🤖 AI raw result: {json.dumps(result, ensure_ascii=False, indent=2)}")

        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=2,
            progress=70,
            total_stages=5
        )

        if result.get('success') and result.get('data'):
            dish_data = result['data']
            model_used = result.get('model', 'unknown')

            # Перевод названия
            dish_name_en = dish_data.get('dish_name', '')
            dish_name_ru = await translate_dish_name(dish_name_en) if dish_name_en else "Неизвестное блюдо"

            # Перевод ингредиентов
            ingredients_ru = []
            for ing in dish_data.get('ingredients', []):
                if isinstance(ing, dict):
                    ing_name = ing.get('name', '')
                    if ing_name:
                        translated = await translate_to_russian(ing_name)
                        ingredients_ru.append({
                            **ing,
                            'name': translated,
                            'original_name': ing_name
                        })
                elif isinstance(ing, str):
                    translated = await translate_to_russian(ing)
                    ingredients_ru.append({
                        'name': translated,
                        'original_name': ing,
                        'type': 'other',
                        'estimated_weight_grams': 100,
                        'confidence': 0.7
                    })

            dish_data['dish_name'] = dish_name_ru
            dish_data['ingredients'] = ingredients_ru

            await _send_progress_update(
                message.bot,
                message.chat.id,
                progress_msg.message_id,
                stage=3,
                progress=85,
                total_stages=5
            )

            await _send_progress_update(
                message.bot,
                message.chat.id,
                progress_msg.message_id,
                stage=4,
                progress=100,
                total_stages=5
            )
            await asyncio.sleep(0.3)
            if progress_msg:
                await progress_msg.delete()
                progress_msg = None

            # Ищем похожие готовые блюда
            matches = find_matching_dishes(dish_name_ru, dish_data.get('ingredients', []))

            if matches:
                # Показываем список для выбора
                await state.update_data(recognized_dish=dish_data, mode="photo_selection")
                await _show_dish_selection(message, state, matches, dish_data, model_used)
            else:
                # Нет совпадений – сразу переходим к ингредиентам
                await state.update_data(recognized_dish=dish_data, mode="photo_recognition")
                await _show_dish_confirmation(message, state, dish_data, model_used)

        else:
            if progress_msg:
                await progress_msg.delete()
            await _handle_recognition_failure(message, state)

    except Exception as e:
        logger.error(f"❌ Photo handler error: {e}\n{traceback.format_exc()}")
        if progress_msg:
            try:
                await progress_msg.delete()
            except:
                pass
        await message.answer("❌ Ошибка при анализе фото. Попробуйте позже.")
        await state.clear()

# ========== ФУНКЦИИ ПОКАЗА ВАРИАНТОВ ==========

async def _show_dish_selection(
    message: Message,
    state: FSMContext,
    matches: list,
    dish_data: Dict,
    model_used: str
):
    """Показывает пользователю список похожих готовых блюд."""
    text = f"🍽 <b>Распознано ({model_used}): {dish_data.get('dish_name', 'Блюдо')}</b>\n"
    text += f"🎯 Уверенность: {dish_data.get('confidence', 0.5):.0%}\n\n"
    text += "Найдены похожие готовые блюда в базе:\n"

    builder = InlineKeyboardBuilder()
    for i, match in enumerate(matches):
        btn_text = f"{match['name']} (совпадение {match['score']*100:.0f}%)"
        builder.button(text=btn_text, callback_data=f"select_dish_{match['dish_key']}")

    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="🔍 Разобрать на ингредиенты", callback_data="use_ingredients_instead"),
        InlineKeyboardButton(text="📝 Ввести вручную", callback_data="manual_food_entry")
    )
    builder.row(InlineKeyboardButton(text="🔄 Перераспознать", callback_data="retry_photo"))

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await state.update_data(recognized_dish=dish_data, mode="photo_selection")

async def _show_dish_confirmation(
    message: Message,
    state: FSMContext,
    dish_data: Dict,
    model_used: str
):
    """Показывает распознанное блюдо с возможностью редактирования."""
    dish_name = dish_data.get('dish_name', 'Блюдо')
    confidence = dish_data.get('confidence', 0.5)
    ingredients = dish_data.get('ingredients', [])

    text = f"🍽 <b>Распознано ({model_used}): {dish_name}</b>\n"
    text += f"🎯 Уверенность: {confidence:.0%}\n"

    if ingredients:
        text += "<b>Ингредиенты:</b>\n"
        for i, ing in enumerate(ingredients):
            name = ing.get('name', 'Неизвестно')
            weight = ing.get('estimated_weight_grams', 100)
            text += f"• {i+1}. {name}: ~{weight}г\n"

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Использовать ингредиенты", callback_data="confirm_dish_as_is")
    builder.button(text="🔄 Перераспознать", callback_data="retry_photo")
    builder.button(text="📝 Ввести вручную", callback_data="manual_food_entry")
    builder.adjust(1)

    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await state.update_data(recognized_dish=dish_data, mode="photo_recognition")

async def _handle_recognition_failure(message: Message, state: FSMContext):
    """Обработка случая, когда распознавание не удалось."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ввести продукты вручную", callback_data="food_manual")],
        [InlineKeyboardButton(text="🔄 Попробовать ещё раз", callback_data="retry_photo")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
    ])
    await message.answer(
        "❌ Не удалось распознать блюдо.\n"
        "Возможные причины:\n"
        "• Фото слишком тёмное/размытое\n"
        "• Блюдо нестандартное или сложное\n"
        "• На фото несколько блюд одновременно\n"
        "Что делать:",
        reply_markup=keyboard
    )
    await state.update_data(last_photo_id=message.message_id)

# ========== ОБРАБОТЧИКИ ПОДТВЕРЖДЕНИЯ БЛЮДА ==========

@router.callback_query(F.data == "confirm_dish_as_is")
async def confirm_dish_callback(callback: CallbackQuery, state: FSMContext):
    """Использует ингредиенты, распознанные AI, с сохранением весов."""
    await callback.answer("⏳ Загружаю данные...")

    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})

    if not dish_data:
        await callback.message.edit_text("❌ Данные не найдены")
        return

    ingredients = dish_data.get('ingredients', [])
    if not ingredients:
        await callback.message.edit_text("❌ Нет ингредиентов")
        return

    # Формируем список food_items с весами (если есть)
    food_items = []
    for ing in ingredients:
        name = ing.get('name', '')
        weight = ing.get('estimated_weight_grams', 0) or ing.get('weight', 100)
        confidence = ing.get('confidence', 0.7)
        if name:
            food_items.append({
                'name': name,
                'weight': weight,
                'ai_confidence': confidence
            })

    # Разворачиваем составные блюда (если AI ошибочно определил ингредиент как готовое блюдо)
    expanded_items = []
    for item in food_items:
        name_lower = item['name'].lower()
        if name_lower in COMPOSITE_DISHES:
            dish_ings = get_dish_ingredients(name_lower, total_weight=item['weight'])
            for d_ing in dish_ings:
                expanded_items.append({
                    'name': d_ing['name'],
                    'weight': d_ing['estimated_weight_grams'],
                    'ai_confidence': item['ai_confidence']
                })
        else:
            expanded_items.append(item)

    await callback.message.edit_text(f"⏳ Загружаю {len(expanded_items)} продуктов...")

    # Сбрасываем предыдущие выбранные продукты и начинаем обработку
    await state.update_data(selected_foods=[])
    await process_food_items(
        callback.message,
        state,
        expanded_items,
        meal_type=dish_data.get('meal_type', 'snack')
    )

@router.callback_query(F.data == "confirm_dish_db")
async def confirm_dish_from_db_callback(callback: CallbackQuery, state: FSMContext):
    """Использует ингредиенты из базы готовых блюд с весами."""
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})
    dish_name = dish_data.get('dish_name', 'Блюдо')

    dish_key = dish_name.lower().strip()
    if dish_key in COMPOSITE_DISHES:
        default_weight = COMPOSITE_DISHES[dish_key].get('default_weight', 300)
    else:
        default_weight = 300

    # Определяем вес порции: используем вес от AI, если он разумный
    ai_ingredients = dish_data.get('ingredients', [])
    ai_total_weight = sum(ing.get('estimated_weight_grams', 0) for ing in ai_ingredients)
    if 50 < ai_total_weight < 1500:
        total_weight = ai_total_weight
    else:
        total_weight = default_weight

    ingredients_with_weights = get_dish_ingredients(dish_key, total_weight=total_weight)

    if not ingredients_with_weights:
        await callback.answer("❌ Блюдо не найдено в базе", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text("⏳ Загружаю ингредиенты...")

    food_items = [{'name': ing['name'], 'weight': ing['estimated_weight_grams']} for ing in ingredients_with_weights]
    logger.info(f"🍔 food_items для готового блюда: {food_items}")

    await state.update_data(selected_foods=[])
    await process_food_items(
        callback.message,
        state,
        food_items,
        meal_type=dish_data.get('meal_type', 'snack')
    )

    await state.update_data(
        ai_description=dish_data.get('dish_name', ''),
        cooking_method=dish_data.get('cooking_method', ''),
        mode="photo_db_dish"
    )

@router.callback_query(F.data == "use_ingredients_instead")
async def use_ingredients_callback(callback: CallbackQuery, state: FSMContext):
    """Использует ингредиенты, полученные от AI, без разворачивания составных блюд."""
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})
    ai_ingredients = dish_data.get('ingredients', [])

    if not ai_ingredients:
        await callback.answer("❌ Нет ингредиентов от AI", show_alert=True)
        return

    food_items = []
    for ing in ai_ingredients:
        if isinstance(ing, dict):
            name = ing.get('name', '')
            if not name:
                continue
            weight = ing.get('estimated_weight_grams', 0) or ing.get('weight', 100)
            food_items.append({
                'name': name,
                'weight': weight,
                'ai_confidence': ing.get('confidence', 0.7)
            })
        elif isinstance(ing, str):
            food_items.append({
                'name': ing,
                'weight': 100,
                'ai_confidence': 0.5
            })

    if not food_items:
        await callback.answer("❌ Нет валидных ингредиентов", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text("⏳ Загружаю данные продуктов...")

    await state.update_data(selected_foods=[])
    await process_food_items(
        callback.message,
        state,
        food_items,
        meal_type=dish_data.get('meal_type', 'snack')
    )

    await state.update_data(
        ai_description=dish_data.get('dish_name', ''),
        cooking_method=dish_data.get('cooking_method', ''),
        mode="photo_ai_ingredients"
    )

@router.callback_query(F.data.startswith("select_dish_"))
async def select_dish_callback(callback: CallbackQuery, state: FSMContext):
    """Выбор готового блюда из списка."""
    dish_key = callback.data.split("_", 2)[2]  # select_dish_ключ
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})

    if dish_key not in COMPOSITE_DISHES:
        await callback.answer("❌ Блюдо не найдено", show_alert=True)
        return

    dish_info = COMPOSITE_DISHES[dish_key]
    default_weight = dish_info.get('default_weight', 300)

    ai_ingredients = dish_data.get('ingredients', [])
    ai_total_weight = sum(ing.get('estimated_weight_grams', 0) for ing in ai_ingredients)
    if 50 < ai_total_weight < 1500:
        total_weight = ai_total_weight
    else:
        total_weight = default_weight

    # Получаем КБЖУ на 100г из базы (если есть)
    nutrition_per_100 = dish_info.get('nutrition_per_100')
    if nutrition_per_100:
        # Используем готовые КБЖУ
        multiplier = total_weight / 100.0
        selected_food = {
            'name': dish_info['name'],
            'base_calories': nutrition_per_100.get('calories', 0),
            'base_protein': nutrition_per_100.get('protein', 0),
            'base_fat': nutrition_per_100.get('fat', 0),
            'base_carbs': nutrition_per_100.get('carbs', 0),
            'weight': total_weight,
            'calories': nutrition_per_100.get('calories', 0) * multiplier,
            'protein': nutrition_per_100.get('protein', 0) * multiplier,
            'fat': nutrition_per_100.get('fat', 0) * multiplier,
            'carbs': nutrition_per_100.get('carbs', 0) * multiplier,
            'source': 'composite_dish',
            'dish_key': dish_key
        }
        await state.update_data(selected_foods=[selected_food], meal_type=dish_data.get('meal_type', 'snack'))
        # Показываем карточку блюда
        totals_msg = await callback.message.answer(
            f"🍽️ <b>Выбрано блюдо: {dish_info['name']}</b>\n"
            f"⚖️ Вес порции: {total_weight} г\n"
            f"🔥 {selected_food['calories']:.0f} ккал | 🥩 {selected_food['protein']:.1f}г | 🥑 {selected_food['fat']:.1f}г | 🍚 {selected_food['carbs']:.1f}г",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➖10", callback_data=f"weight_dec_0_10_{totals_msg.message_id}"),
                 InlineKeyboardButton(text="➕10", callback_data=f"weight_inc_0_10_{totals_msg.message_id}")],
                [InlineKeyboardButton(text="50", callback_data=f"weight_set_0_50_{totals_msg.message_id}"),
                 InlineKeyboardButton(text="100", callback_data=f"weight_set_0_100_{totals_msg.message_id}"),
                 InlineKeyboardButton(text="200", callback_data=f"weight_set_0_200_{totals_msg.message_id}")],
                [InlineKeyboardButton(text="🔍 Разобрать на ингредиенты", callback_data=f"explode_dish_{dish_key}")],
                [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
                 InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")]
            ])
        )
        await state.update_data(totals_msg_id=totals_msg.message_id)
        await callback.message.delete()
        await callback.answer()
        return

    # Если нет готовых КБЖУ, используем старую логику разбивки на ингредиенты
    ingredients_with_weights = get_dish_ingredients(dish_key, total_weight=total_weight)

    if not ingredients_with_weights:
        await callback.answer("❌ Не удалось получить ингредиенты", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text("⏳ Загружаю ингредиенты...")

    food_items = [{'name': ing['name'], 'weight': ing['estimated_weight_grams']} for ing in ingredients_with_weights]
    logger.info(f"🍔 food_items для готового блюда: {food_items}")

    await state.update_data(selected_foods=[])
    await process_food_items(
        callback.message,
        state,
        food_items,
        meal_type=dish_data.get('meal_type', 'snack')
    )

    await state.update_data(
        ai_description=dish_data.get('dish_name', ''),
        cooking_method=dish_data.get('cooking_method', ''),
        mode="photo_db_dish"
    )

@router.callback_query(F.data.startswith("explode_dish_"))
async def explode_dish_callback(callback: CallbackQuery, state: FSMContext):
    """Разбирает готовое блюдо на ингредиенты для ручной корректировки."""
    dish_key = callback.data.split("_", 2)[2]
    data = await state.get_data()

    selected_foods = data.get('selected_foods', [])
    if selected_foods:
        current_weight = selected_foods[0].get('weight', 300)
    else:
        current_weight = 300

    from services.dish_db import get_dish_ingredients
    ingredients_with_weights = get_dish_ingredients(dish_key, total_weight=current_weight)
    food_items = [{'name': ing['name'], 'weight': ing['estimated_weight_grams']} for ing in ingredients_with_weights]

    await state.update_data(selected_foods=[])
    await process_food_items(callback.message, state, food_items, meal_type=data.get('meal_type', 'snack'))
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "retry_photo")
async def retry_photo_callback(callback: CallbackQuery, state: FSMContext):
    """Повторное распознавание фото."""
    data = await state.get_data()
    photo_optimized = data.get('pending_photo_optimized')

    if not photo_optimized:
        await callback.answer("❌ Фото не найдено", show_alert=True)
        return

    await callback.answer("🔄 Перераспознаю...")
    await callback.message.edit_text("🔄 Повторный анализ...")

    result = await identify_food_cascade(photo_optimized)

    if result.get('success') and result.get('data'):
        dish_data = result['data']
        dish_name_ru = await translate_dish_name(dish_data.get('dish_name', ''))
        ingredients_ru = []
        for ing in dish_data.get('ingredients', []):
            if isinstance(ing, dict) and ing.get('name'):
                ingredients_ru.append({
                    **ing,
                    'name': await translate_to_russian(ing['name']),
                    'original_name': ing['name']
                })
        dish_data['dish_name'] = dish_name_ru
        dish_data['ingredients'] = ingredients_ru

        await state.update_data(recognized_dish=dish_data)
        await _show_dish_confirmation(
            callback.message,
            state,
            dish_data,
            result.get('model', 'unknown')
        )
    else:
        await _handle_recognition_failure(callback.message, state)

    await callback.answer()

@router.callback_query(F.data == "manual_food_entry")
async def manual_food_callback(callback: CallbackQuery, state: FSMContext):
    """Переход к ручному вводу."""
    await state.clear()
    from handlers.food import cmd_log_food
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data.startswith("select_dish_for_product_"))
async def select_dish_for_product_callback(callback: CallbackQuery, state: FSMContext):
    """Выбор готового блюда для текущего продукта."""
    dish_key = callback.data.replace("select_dish_for_product_", "")
    data = await state.get_data()

    # Получаем данные блюда из базы
    from services.dish_db import COMPOSITE_DISHES, get_dish_ingredients
    if dish_key not in COMPOSITE_DISHES:
        await callback.answer("❌ Блюдо не найдено", show_alert=True)
        return

    dish_info = COMPOSITE_DISHES[dish_key]
    default_weight = dish_info.get('default_weight', 300)
    weight = data.get('pending_weight', 100)  # используем вес, заданный пользователем

    # Проверяем, есть ли готовое КБЖУ
    nutrition_per_100 = dish_info.get('nutrition_per_100')
    if nutrition_per_100:
        # Используем готовое КБЖУ
        multiplier = weight / 100.0
        selected_food = {
            'name': dish_info['name'],
            'base_calories': nutrition_per_100.get('calories', 0),
            'base_protein': nutrition_per_100.get('protein', 0),
            'base_fat': nutrition_per_100.get('fat', 0),
            'base_carbs': nutrition_per_100.get('carbs', 0),
            'weight': weight,
            'calories': nutrition_per_100.get('calories', 0) * multiplier,
            'protein': nutrition_per_100.get('protein', 0) * multiplier,
            'fat': nutrition_per_100.get('fat', 0) * multiplier,
            'carbs': nutrition_per_100.get('carbs', 0) * multiplier,
            'source': 'composite_dish',
            'dish_key': dish_key
        }
        # Добавляем к выбранным продуктам
        selected_foods = data.get('selected_foods', [])
        selected_foods.append(selected_food)
        await state.update_data(selected_foods=selected_foods)
        # Продолжаем со следующим продуктом
        await callback.message.delete()
        await process_food_items(
            callback.message,
            state,
            data.get('pending_food_items'),
            data.get('pending_meal_type'),
            data.get('pending_index', 0) + 1
        )
        await callback.answer()
        return

    # Если нет готового КБЖУ, разбиваем на ингредиенты
    ingredients_with_weights = get_dish_ingredients(dish_key, total_weight=weight)
    food_items = [{'name': ing['name'], 'weight': ing['estimated_weight_grams']} for ing in ingredients_with_weights]

    # Заменяем текущий элемент на список ингредиентов
    pending_items = data.get('pending_food_items')
    pending_items.pop(data.get('pending_index'))
    pending_items[data.get('pending_index'):data.get('pending_index')] = food_items

    await state.update_data(pending_food_items=pending_items)
    await callback.message.delete()
    await process_food_items(
        callback.message,
        state,
        pending_items,
        data.get('pending_meal_type'),
        data.get('pending_index')
    )
    await callback.answer()

@router.callback_query(F.data.startswith("continue_as_ingredient_"))
async def continue_as_ingredient_callback(callback: CallbackQuery, state: FSMContext):
    """Пользователь решил, что это не готовое блюдо, а ингредиент."""
    product_name = callback.data.replace("continue_as_ingredient_", "")
    data = await state.get_data()
    await callback.message.delete()
    # Просто продолжаем обработку как ингредиент
    await process_food_items(
        callback.message,
        state,
        data.get('pending_food_items'),
        data.get('pending_meal_type'),
        data.get('pending_index')
    )
    await callback.answer()

@router.callback_query(F.data.startswith("select_dish_idx_"))
async def select_dish_by_index_callback(callback: CallbackQuery, state: FSMContext):
    """Выбор готового блюда по индексу."""
    try:
        idx = int(callback.data.split("_")[3])
    except (IndexError, ValueError):
        await callback.answer("❌ Неверный индекс", show_alert=True)
        return

    data = await state.get_data()
    matches = data.get('dish_matches')
    if not matches or idx >= len(matches):
        await callback.answer("❌ Данные не найдены", show_alert=True)
        return

    match = matches[idx]
    dish_key = match['dish_key']
    pending_food_items = data.get('pending_food_items')
    pending_index = data.get('pending_index')
    meal_type = data.get('pending_meal_type')
    weight = data.get('pending_weight', 100)

    # Очищаем временные данные
    await state.update_data(dish_matches=None)

    # Получаем информацию о блюде из базы
    from services.dish_db import COMPOSITE_DISHES, get_dish_ingredients
    if dish_key not in COMPOSITE_DISHES:
        await callback.answer("❌ Блюдо не найдено", show_alert=True)
        return

    dish_info = COMPOSITE_DISHES[dish_key]

    # Проверяем, есть ли готовое КБЖУ
    nutrition_per_100 = dish_info.get('nutrition_per_100')
    if nutrition_per_100:
        # Используем готовое КБЖУ
        multiplier = weight / 100.0
        selected_food = {
            'name': dish_info['name'],
            'base_calories': nutrition_per_100.get('calories', 0),
            'base_protein': nutrition_per_100.get('protein', 0),
            'base_fat': nutrition_per_100.get('fat', 0),
            'base_carbs': nutrition_per_100.get('carbs', 0),
            'weight': weight,
            'calories': nutrition_per_100.get('calories', 0) * multiplier,
            'protein': nutrition_per_100.get('protein', 0) * multiplier,
            'fat': nutrition_per_100.get('fat', 0) * multiplier,
            'carbs': nutrition_per_100.get('carbs', 0) * multiplier,
            'source': 'composite_dish',
            'dish_key': dish_key
        }
        selected_foods = data.get('selected_foods', [])
        selected_foods.append(selected_food)
        await state.update_data(selected_foods=selected_foods)

        await callback.message.delete()
        await process_food_items(
            callback.message,
            state,
            pending_food_items,
            meal_type,
            pending_index + 1
        )
        await callback.answer()
        return

    # Если нет готового КБЖУ, разбиваем на ингредиенты
    default_weight = dish_info.get('default_weight', 300)
    # Используем вес, заданный пользователем, если он разумный
    total_weight = weight if 50 < weight < 1500 else default_weight

    ingredients_with_weights = get_dish_ingredients(dish_key, total_weight=total_weight)
    food_items = [{'name': ing['name'], 'weight': ing['estimated_weight_grams']} for ing in ingredients_with_weights]

    # Заменяем текущий элемент на список ингредиентов
    pending_food_items.pop(pending_index)
    for i, item in enumerate(food_items):
        pending_food_items.insert(pending_index + i, item)

    await state.update_data(pending_food_items=pending_food_items)
    await callback.message.delete()
    await process_food_items(
        callback.message,
        state,
        pending_food_items,
        meal_type,
        pending_index  # начинаем с первого ингредиента вместо удалённого продукта
    )
    await callback.answer()

@router.callback_query(F.data == "continue_ingredient")
async def continue_as_ingredient_callback(callback: CallbackQuery, state: FSMContext):
    """Пользователь решил, что это не готовое блюдо, а ингредиент."""
    data = await state.get_data()
    await callback.message.delete()
    # Просто продолжаем обработку как ингредиент
    await process_food_items(
        callback.message,
        state,
        data.get('pending_food_items'),
        data.get('pending_meal_type'),
        data.get('pending_index')
    )
    await callback.answer()
# ========== ОБРАБОТЧИКИ УПРАВЛЕНИЯ ВЕСОМ ==========

@router.callback_query(F.data.startswith("weight_"))
async def weight_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка изменения веса продукта."""
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    totals_msg_id = data.get('totals_msg_id')
    product_msg_ids = data.get('product_msg_ids', [])

    if not selected_foods:
        await callback.answer("❌ Нет данных", show_alert=True)
        return

    parts = callback.data.split('_')
    if len(parts) < 4:
        await callback.answer("❌ Ошибка формата", show_alert=True)
        return

    action = parts[1]
    idx = int(parts[2])
    value = int(parts[3]) if parts[3].isdigit() else None
    totals_msg_id_from_callback = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else totals_msg_id

    if idx >= len(selected_foods):
        await callback.answer("❌ Ошибка индекса", show_alert=True)
        return

    food = selected_foods[idx]

    if action == "del":
        del selected_foods[idx]
        if idx < len(product_msg_ids):
            try:
                await callback.bot.delete_message(callback.message.chat.id, product_msg_ids[idx])
            except:
                pass
            del product_msg_ids[idx]

        await state.update_data(
            selected_foods=selected_foods,
            product_msg_ids=product_msg_ids
        )
        await _update_totals_message(
            callback.message.chat.id,
            totals_msg_id_from_callback,
            callback.bot,
            selected_foods,
            data.get('meal_type', 'snack')
        )
        await callback.answer("✅ Продукт удалён")
        return

    if value is None:
        await callback.answer("❌ Нет значения", show_alert=True)
        return

    current_weight = float(food.get('weight', 0) or 0)

    if action == "inc":
        new_weight = current_weight + value
    elif action == "dec":
        new_weight = max(0, current_weight - value)
    elif action == "set":
        new_weight = float(value)
    else:
        await callback.answer()
        return

    if new_weight == current_weight:
        await callback.answer()
        return

    food['weight'] = new_weight

    base_data = {
        'base_calories': food.get('base_calories', food.get('calories', 0)),
        'base_protein': food.get('base_protein', food.get('protein', 0)),
        'base_fat': food.get('base_fat', food.get('fat', 0)),
        'base_carbs': food.get('base_carbs', food.get('carbs', 0))
    }

    if current_weight > 0 and base_data['base_calories'] == 0:
        multiplier = 100.0 / current_weight
        base_data['base_calories'] = food.get('calories', 0) * multiplier
        base_data['base_protein'] = food.get('protein', 0) * multiplier
        base_data['base_fat'] = food.get('fat', 0) * multiplier
        base_data['base_carbs'] = food.get('carbs', 0) * multiplier

    nutrients = _calculate_nutrients(base_data, new_weight)

    food.update({
        'weight': new_weight,
        'calories': nutrients['calories'],
        'protein': nutrients['protein'],
        'fat': nutrients['fat'],
        'carbs': nutrients['carbs'],
        'base_calories': base_data['base_calories'],
        'base_protein': base_data['base_protein'],
        'base_fat': base_data['base_fat'],
        'base_carbs': base_data['base_carbs']
    })

    selected_foods[idx] = food
    await state.update_data(selected_foods=selected_foods)

    weight_str = f"{new_weight} г" if new_weight else "0 г"
    text = (
        f"<b>{idx+1}. {food['name']}</b>\n"
        f"⚖️ Вес: {weight_str}\n"
        f"🔥 {nutrients['calories']:.0f} ккал | 🥩 {nutrients['protein']:.1f}г | 🥑 {nutrients['fat']:.1f}г | 🍚 {nutrients['carbs']:.1f}г"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➖10", callback_data=f"weight_dec_{idx}_10_{totals_msg_id_from_callback}"),
        InlineKeyboardButton(text="➕10", callback_data=f"weight_inc_{idx}_10_{totals_msg_id_from_callback}"),
        InlineKeyboardButton(text="50", callback_data=f"weight_set_{idx}_50_{totals_msg_id_from_callback}"),
        InlineKeyboardButton(text="100", callback_data=f"weight_set_{idx}_100_{totals_msg_id_from_callback}"),
        InlineKeyboardButton(text="200", callback_data=f"weight_set_{idx}_200_{totals_msg_id_from_callback}"),
        InlineKeyboardButton(text="❌", callback_data=f"weight_del_{idx}_{totals_msg_id_from_callback}")
    ]])

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except TelegramBadRequest:
        pass

    await _update_totals_message(
        callback.message.chat.id,
        totals_msg_id_from_callback,
        callback.bot,
        selected_foods,
        data.get('meal_type', 'snack')
    )
    await callback.answer()

async def _update_totals_message(
    chat_id: int,
    message_id: int,
    bot,
    selected_foods: List[Dict],
    meal_type: str = "snack"
):
    """Обновляет сообщение с итогами КБЖУ."""
    total_cal = sum(f.get('calories', 0) for f in selected_foods)
    total_prot = sum(f.get('protein', 0) for f in selected_foods)
    total_fat = sum(f.get('fat', 0) for f in selected_foods)
    total_carbs = sum(f.get('carbs', 0) for f in selected_foods)

    text = (
        f"🍽️ <b>Приём пищи ({meal_type}):</b>\n"
        f"🔥 {total_cal:.0f} ккал | 🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_food")],
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")
        ]
    ])
    await _safe_edit_message(bot, chat_id, message_id, text, keyboard)

# ========== ДОБАВЛЕНИЕ НОВОГО ПРОДУКТА ==========

@router.callback_query(F.data == "add_food")
async def add_food_callback(callback: CallbackQuery, state: FSMContext):
    """Начало добавления нового продукта."""
    await callback.answer()
    await callback.message.edit_text(
        "➕ <b>Добавление продукта</b>\nВведите название:",
        parse_mode="HTML"
    )
    await state.set_state(FoodStates.adding_name)

@router.message(FoodStates.adding_name, F.text)
async def process_add_name(message: Message, state: FSMContext):
    """Обработка названия нового продукта."""
    name = message.text.strip()
    if not name:
        await message.answer("❌ Название не может быть пустым.")
        return

    await state.update_data(new_food_name=name)
    await message.answer(
        f"➕ <b>{name}</b>\nВведите вес в граммах (или /skip):",
        parse_mode="HTML"
    )
    await state.set_state(FoodStates.adding_weight)

@router.message(FoodStates.adding_weight, F.text)
async def process_add_weight(message: Message, state: FSMContext):
    """Обработка веса нового продукта."""
    data = await state.get_data()
    name = data.get('new_food_name')
    text = message.text.strip().lower()

    if text == "/skip":
        weight = 0
    else:
        try:
            match = re.search(r'\d+([.,]\d+)?', message.text)
            weight = float(match.group(0).replace(',', '.')) if match else float(message.text.replace(',', '.'))
            if not (0 < weight <= 10000):
                raise ValueError
        except (ValueError, AttributeError):
            await message.answer("❌ Введите число от 1 до 10000")
            return

    food_data = await _get_food_data_cached(name)
    nutrients = _calculate_nutrients(food_data, weight)

    new_food = {
        **food_data,
        'weight': weight,
        **nutrients
    }

    selected_foods = data.get('selected_foods', [])
    product_msg_ids = data.get('product_msg_ids', [])
    totals_msg_id = data.get('totals_msg_id')

    idx = len(selected_foods)
    selected_foods.append(new_food)

    new_msg_id = await _send_product_card(
        message.chat.id,
        message.bot,
        idx,
        new_food,
        totals_msg_id
    )
    product_msg_ids.append(new_msg_id)

    await state.update_data(
        selected_foods=selected_foods,
        product_msg_ids=product_msg_ids
    )
    await _update_totals_message(
        message.chat.id,
        totals_msg_id,
        message.bot,
        selected_foods,
        data.get('meal_type', 'snack')
    )

    await message.delete()
    await message.answer("✅ Продукт добавлен.")

# ========== ПОДТВЕРЖДЕНИЕ И СОХРАНЕНИЕ ==========

async def _safe_answer(callback: CallbackQuery):
    """Безопасный ответ на callback."""
    try:
        await callback.answer()
    except TelegramBadRequest:
        pass

@router.callback_query(F.data == "confirm_meal")
async def confirm_meal_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение приёма пищи."""
    logger.info(f"✅ confirm_meal_callback: user={callback.from_user.id}")

    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])

    if not selected_foods or not any(f.get('weight', 0) for f in selected_foods):
        await callback.answer("❌ Укажите вес хотя бы одного продукта", show_alert=True)
        return

    user_id = callback.from_user.id
    meal_type = data.get('meal_type', 'snack')

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            await callback.message.answer("❌ Сначала настройте профиль (/set_profile)")
            await state.clear()
            return

        total_cal = sum(f.get('calories', 0) for f in selected_foods)
        total_prot = sum(f.get('protein', 0) for f in selected_foods)
        total_fat = sum(f.get('fat', 0) for f in selected_foods)
        total_carbs = sum(f.get('carbs', 0) for f in selected_foods)

        meal = Meal(
            user_id=user.id,
            meal_type=meal_type,
            datetime=datetime.now(),
            total_calories=total_cal,
            total_protein=total_prot,
            total_fat=total_fat,
            total_carbs=total_carbs,
            ai_description=data.get('ai_description', '')
        )
        session.add(meal)
        await session.flush()

        for f in selected_foods:
            if f.get('weight', 0) > 0:
                item = FoodItem(
                    meal_id=meal.id,
                    name=f['name'],
                    weight=f['weight'],
                    calories=f.get('calories', 0),
                    protein=f.get('protein', 0),
                    fat=f.get('fat', 0),
                    carbs=f.get('carbs', 0)
                )
                session.add(item)

        await session.commit()

        chat_id = callback.message.chat.id
        for msg_id in data.get('product_msg_ids', []):
            try:
                await callback.bot.delete_message(chat_id, msg_id)
            except:
                pass

        try:
            await callback.bot.delete_message(chat_id, data.get('totals_msg_id'))
        except:
            pass

        lines = [f"🍽️ <b>Записан приём пищи ({meal_type}):</b>"]
        for f in selected_foods:
            if f.get('weight', 0) > 0:
                lines.append(f"• {f['name']}: {f['weight']}г — {f.get('calories', 0):.0f} ккал")

        lines.append(f"\n🔥 Всего: {total_cal:.0f} ккал")
        lines.append(f"🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г")

        await callback.message.answer("\n".join(lines), parse_mode="HTML")
        await state.clear()
        await _safe_answer(callback)

@router.callback_query(F.data == "cancel_meal")
async def cancel_meal_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода."""
    logger.info(f"❌ cancel_meal_callback: user={callback.from_user.id}")

    data = await state.get_data()
    chat_id = callback.message.chat.id

    for msg_id in data.get('product_msg_ids', []):
        try:
            await callback.bot.delete_message(chat_id, msg_id)
        except:
            pass

    try:
        await callback.bot.delete_message(chat_id, data.get('totals_msg_id'))
    except:
        pass

    await state.update_data(last_photo_id=None)
    await callback.message.answer("❌ Ввод отменён.")
    await state.clear()
    await _safe_answer(callback)

@router.callback_query(F.data == "action_cancel")
async def action_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена действия."""
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("❌ Отменено.")
    await _safe_answer(callback)

@router.callback_query(F.data == "food_manual")
async def food_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Переход к ручному вводу."""
    await state.clear()
    from handlers.food import cmd_log_food
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)
    await _safe_answer(callback)

# ========== ОБРАБОТЧИК ГОЛОСОВЫХ СООБЩЕНИЙ ==========

@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    """Обработка голосовых сообщений."""
    logger.info(f"🎤 Voice received from user {message.from_user.id}")

    try:
        await message.answer("🎧 Распознаю голос...")

        file_info = await message.bot.get_file(message.voice.file_id)
        audio_bytes = await message.bot.download_file(file_info.file_path)
        audio_data = audio_bytes.read()

        from services.cloudflare_ai import transcribe_audio
        text = await transcribe_audio(audio_data, language="ru")

        if not text:
            await message.answer("❌ Не удалось распознать речь. Попробуйте говорить чётче или введите текст.")
            return

        logger.info(f"🎤 Transcribed: {text}")

        from handlers.universal_text_handler import process_natural_language
        await process_natural_language(message, state, text)

    except Exception as e:
        logger.error(f"❌ Voice handler error: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Ошибка при обработке голоса.")
