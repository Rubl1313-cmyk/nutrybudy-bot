# handlers/media_handlers.py
"""
Обработчики мультимедиа: фото (распознавание еды) и голос.
✅ Улучшенное распознавание через мультимодельный JSON
✅ Интеграция с image_enhancer для улучшения фото
✅ Каскадное распознавание с голосованием
✅ Интерфейс подтверждения с редактированием
✅ Исправлены все ошибки с user_id
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
import asyncio  # ← 🔥 ДОБАВИТЬ ЭТУ СТРОКУ
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from services.cloudflare_ai import (
    identify_food_multimodel,
    identify_food_cascade,
    transcribe_audio,
    _validate_food_data,
    _calibrate_weights
)
from services.food_api import search_food, get_food_data
from services.translator import translate_dish_name, translate_to_russian
from services.dish_db import find_matching_dish, COMPOSITE_DISHES, get_dish_ingredients
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem, User
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)
_SEARCH_CACHE = {}

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


# ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ ==========
async def _get_food_data_cached(name: str) -> Dict:
    """
    ✅ ИСПРАВЛЕНО: Получает данные продукта, избегая готовых блюд
    """
    from services.food_api import LOCAL_FOOD_DB, search_food
    
    name_lower = name.lower().strip()
    
    # 🔥 1. Прямой поиск в базе простых продуктов
    for key, product_item in LOCAL_FOOD_DB.items():
        if name_lower == key or name_lower == product_item["name"].lower():
            return {
                'name': product_item['name'],
                'base_calories': product_item.get('calories', 0),
                'base_protein': product_item.get('protein', 0),
                'base_fat': product_item.get('fat', 0),
                'base_carbs': product_item.get('carbs', 0),
                'source': 'local'
            }
    
    # 🔥 2. Поиск по частичному совпадению (но НЕ готовые блюда!)
    for key, product_item in LOCAL_FOOD_DB.items():
        if name_lower in key or key in name_lower:
            # 🔥 ПРОВЕРКА: это не готовое блюдо?
            if key not in COMPOSITE_DISHES:
                return {
                    'name': product_item['name'],
                    'base_calories': product_item.get('calories', 0),
                    'base_protein': product_item.get('protein', 0),
                    'base_fat': product_item.get('fat', 0),
                    'base_carbs': product_item.get('carbs', 0),
                    'source': 'local'
                }
    
    # 🔥 3. Если не нашли - используем search_food (но с фильтром)
    search_results = await search_food(name)
    if search_results:
        best = search_results[0]
        # 🔥 ПРОВЕРКА: это не готовое блюдо из COMPOSITE_DISHES?
        if best['name'].lower() not in COMPOSITE_DISHES:
            return {
                'name': best['name'],
                'base_calories': best.get('calories', 0),
                'base_protein': best.get('protein', 0),
                'base_fat': best.get('fat', 0),
                'base_carbs': best.get('carbs', 0),
                'source': best.get('source', 'local')
            }
    
    # 🔥 4. fallback - возвращаем заглушку
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


async def _start_food_input(
    message: Message,
    state: FSMContext,
    food_names: List[str],
    meal_type: str = "snack"
):
    """Запускает интерфейс ввода продуктов из списка названий."""
    selected_foods = []
    
    for name in food_names:
        data = await _get_food_data_cached(name)
        selected_foods.append({
            'name': data['name'],
            'base_calories': data['base_calories'],
            'base_protein': data['base_protein'],
            'base_fat': data['base_fat'],
            'base_carbs': data['base_carbs'],
            'weight': 0,
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
            'source': data.get('source', 'unknown')
        })
    
    totals_text = "🍽️ <b>Приём пищи:</b>\n🔥 0 ккал | 🥩 0.0г | 🥑 0.0г | 🍚 0.0г"
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
        msg_id = await _send_product_card(message.chat.id, message.bot, i, food, totals_msg.message_id)
        product_msg_ids.append(msg_id)
    
    await state.update_data(
        selected_foods=selected_foods,
        totals_msg_id=totals_msg.message_id,
        product_msg_ids=product_msg_ids,
        meal_type=meal_type,
        mode="manual"
    )
sync def _start_food_input_with_weights(
    message: Message,
    state: FSMContext,
    food_items: List[Dict],
    meal_type: str = "snack"
):
    """
    ✅ Запускает интерфейс ввода продуктов с предустановленными весами
    """
    selected_foods = []
    
    for item in food_items:
        # 🔥 Получаем данные из базы продуктов по названию
        food_data = await _get_food_data_cached(item['name'])
        
        # 🔥 Рассчитываем КБЖУ для веса от AI
        weight = item.get('weight', 100)
        nutrients = _calculate_nutrients(food_data, weight)
        
        selected_foods.append({
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
            'source': food_data.get('source', 'ai_recognition'),
            'ai_confidence': item.get('ai_confidence', 0.7)
        })
    
    # 🔥 Сразу показываем сводку с рассчитанными КБЖУ
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
    
    # 🔥 Отправляем карточки продуктов для редактирования
    product_msg_ids = []
    for i, food in enumerate(selected_foods):
        msg_id = await _send_product_card(message.chat.id, message.bot, i, food, totals_msg.message_id)
        product_msg_ids.append(msg_id)
    
    await state.update_data(
        selected_foods=selected_foods,
        totals_msg_id=totals_msg.message_id,
        product_msg_ids=product_msg_ids,
        meal_type=meal_type,
        mode="photo_ai_ingredients"
    )

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
    builder.button(text="✏️ Редактировать ингредиенты", callback_data="edit_dish_ingredients")
    builder.button(text="🔄 Перераспознать", callback_data="retry_photo")
    builder.button(text="📝 Ввести вручную", callback_data="manual_food_entry")
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await state.update_data(
        recognized_dish=dish_data,
        mode="photo_recognition"
    )


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

def _calculate_nutrients(base: Dict, weight: float) -> Dict:
    """
    ✅ Рассчитывает КБЖУ для заданного веса
    """
    if weight <= 0:
        return {
            'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0
        }
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


# ========== ОСНОВНОЙ ОБРАБОТЧИК ФОТО ==========

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото: каскадное распознавание с ПРОГРЕСС-БАРОМ."""
    data = await state.get_data()
    
    if data.get('last_photo_id') == message.message_id:
        logger.info(f"📸 Duplicate photo ignored: {message.message_id}")
        return
    
    logger.info(f"📸 Photo received, message_id={message.message_id}")
    
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
            await state.clear()
            return
        
        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=2,
            progress=70,
            total_stages=5
        )
        
# 🔥 ЕДИНЫЙ ПОДХОД ДЛЯ ВСЕХ БЛЮД
if result.get('success') and result.get('data'):
    dish_data = result['data']
    model_used = result.get('model', 'unknown')
    
    # 🔥 Перевод названия
    dish_name_en = dish_data.get('dish_name', '')
    dish_name_ru = await translate_dish_name(dish_name_en) if dish_name_en else "Неизвестное блюдо"
    
    # 🔥 Перевод ингредиентов
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
    
    # 🔥 ПРОВЕРКА: Есть ли веса от AI?
    has_weights = any(
        ing.get('estimated_weight_grams', 0) > 0 
        for ing in ingredients_ru
    )
    
    if has_weights:
        # 🔥 ЕСТЬ ВЕСА ОТ AI → Показываем ингредиенты с граммовкой
        await state.update_data(
            recognized_dish=dish_data,
            mode="photo_ai_ingredients"
        )
        await _show_dish_confirmation(message, state, dish_data, model_used)
    else:
        # 🔥 НЕТ ВЕСОВ → Пробуем найти в базе готовых блюд
        dish_name_lower = dish_name_ru.lower().strip()
        if dish_name_lower in COMPOSITE_DISHES:
            # Нашли в базе → используем веса из базы
            await state.update_data(
                recognized_dish=dish_data,
                dish_found_in_db=True,
                mode="photo_db_dish"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Использовать как готовое блюдо", callback_data="confirm_dish_db")],
                [InlineKeyboardButton(text="🔍 Разбить на ингредиенты", callback_data="use_ingredients_instead")]
            ])
            await message.answer(
                f"🍽 Найдено в базе: **{dish_name_ru}**\n"
                f"Использовать как готовое блюдо или разбить на ингредиенты?",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            # Не нашли в базе → показываем как есть
            await state.update_data(
                recognized_dish=dish_data,
                mode="photo_recognition"
            )
            await _show_dish_confirmation(message, state, dish_data, model_used)
        
    except Exception as e:
        logger.error(f"❌ Photo handler error: {e}\n{traceback.format_exc()}")
        try:
            await progress_msg.delete()
        except:
            pass
        await message.answer("❌ Ошибка при анализе фото. Попробуйте позже.")
        await state.clear()


# ========== ОБРАБОТЧИКИ ПОДТВЕРЖДЕНИЯ БЛЮДА ==========

# ========== В ФУНКЦИИ confirm_dish_callback ==========
@router.callback_query(F.data == "confirm_dish_as_is")
async def confirm_dish_callback(callback: CallbackQuery, state: FSMContext):
    """✅ ИСПРАВЛЕНО: Быстрый ответ на callback"""
    
    # 🔥 СРАЗУ ОТВЕЧАЕМ на callback (в течение 1-2 секунд)
    await callback.answer("⏳ Загружаю данные...")
    
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})
    
    if not dish_data:
        await callback.message.edit_text("❌ Данные не найдены")
        return
    
    ingredients = dish_data.get('ingredients', [])
    food_names = [ing.get('name', '') for ing in ingredients if ing.get('name')]
    
    if not food_names:
        await callback.message.edit_text("❌ Нет ингредиентов")
        return
    
    # 🔥 Показываем промежуточное сообщение
    await callback.message.edit_text(f"⏳ Загружаю {len(food_names)} продуктов...")
    
    # 🔥 Запускаем ввод с кэшированием
    await _start_food_input(
        callback.message,
        state,
        food_names,
        meal_type=dish_data.get('meal_type', 'snack')
    )
@router.callback_query(F.data == "confirm_dish_db")
async def confirm_dish_from_db_callback(callback: CallbackQuery, state: FSMContext):
    """
    ✅ ИСПРАВЛЕНО: Использует ингредиенты из COMPOSITE_DISHES с весами
    """
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})
    dish_name = dish_data.get('dish_name', 'Блюдо')
    
    # 🔥 Получаем ингредиенты из базы готовых блюд
    from services.dish_db import get_dish_ingredients, COMPOSITE_DISHES
    
    dish_name_lower = dish_name.lower().strip()
    dish_info_db = COMPOSITE_DISHES.get(dish_name_lower)
    
    if dish_info_db and dish_info_db.get('ingredients'):
        # 🔥 Используем веса из базы готовых блюд
        total_weight = 300  # Стандартная порция
        ingredients_with_weights = get_dish_ingredients(dish_name_lower, total_weight)
    else:
        # 🔥 Fallback: используем ингредиенты от AI
        ingredients_with_weights = dish_data.get('ingredients', [])
    
    if not ingredients_with_weights:
        await callback.answer("❌ Нет ингредиентов", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.edit_text("⏳ Загружаю ингредиенты...")
    
    # 🔥 Преобразуем в формат для ввода
    food_items = []
    for ing in ingredients_with_weights:
        if isinstance(ing, dict):
            name = ing.get('name', '')
            weight = ing.get('estimated_weight_grams', 0) or ing.get('weight', 100)
            if name:
                food_items.append({'name': name, 'weight': weight})
    
    if not food_items:
        await callback.answer("❌ Нет ингредиентов", show_alert=True)
        return
    
    # 🔥 ЗАПУСКАЕМ ВВОД С ВЕСАМИ (как для пасты!)
    await _start_food_input_with_weights(
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

# ========== ОБРАБОТЧИКИ ПОДТВЕРЖДЕНИЯ БЛЮДА ==========

@router.callback_query(F.data == "use_ingredients_instead")
async def use_ingredients_callback(callback: CallbackQuery, state: FSMContext):
    """
    ✅ ИСПРАВЛЕНО: Использует ингредиенты из AI-распознавания,
    а не из базы COMPOSITE_DISHES
    """
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})
    
    # 🔥 БЕРЁМ ИНГРЕДИЕНТЫ ИЗ AI-РАСПОЗНАВАНИЯ
    ai_ingredients = dish_data.get('ingredients', [])
    
    if not ai_ingredients:
        await callback.answer("❌ Нет ингредиентов от AI", show_alert=True)
        return
    
    # 🔥 ПРЕОБРАЗУЕМ AI-ингредиенты в формат для ввода
    food_items = []
    for ing in ai_ingredients:
        if isinstance(ing, dict):
            name = ing.get('name', '')
            # Берём вес из AI или устанавливаем дефолтный
            weight = ing.get('estimated_weight_grams', 0) or ing.get('weight', 100)
            if name:
                food_items.append({
                    'name': name,
                    'weight': weight,
                    'ai_confidence': ing.get('confidence', 0.7)
                })
    
    if not food_items:
        await callback.answer("❌ Нет валидных ингредиентов", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.edit_text("⏳ Загружаю данные продуктов...")
    
    # 🔥 ЗАПУСКАЕМ ВВОД С AI-ИНГРЕДИЕНТАМИ (не из базы!)
    await _start_food_input_with_weights(
        callback.message,
        state,
        food_items,
        meal_type=dish_data.get('meal_type', 'snack')
    )
    
    await state.update_data(
        ai_description=dish_data.get('dish_name', ''),
        cooking_method=dish_data.get('cooking_method', ''),
        mode="photo_ai_ingredients"  # 🔥 Новая метка режима
    )


# ========== ДОБАВИТЬ НОВУЮ ФУНКЦИЮ ПОСЛЕ _start_food_input ==========

async def _start_food_input_with_weights(
    message: Message,
    state: FSMContext,
    food_items: List[Dict],
    meal_type: str = "snack"
):
    """
    ✅ Запускает интерфейс ввода продуктов с предустановленными весами от AI
    """
    selected_foods = []
    
    for item in food_items:
        # 🔥 Получаем данные из базы продуктов по названию
        food_data = await _get_food_data_cached(item['name'])
        
        # 🔥 Рассчитываем КБЖУ для веса от AI
        weight = item.get('weight', 100)
        nutrients = _calculate_nutrients(food_data, weight)
        
        selected_foods.append({
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
            'source': food_data.get('source', 'ai_recognition'),
            'ai_confidence': item.get('ai_confidence', 0.7)
        })
    
    # 🔥 Сразу показываем сводку с рассчитанными КБЖУ
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
    
    # 🔥 Отправляем карточки продуктов для редактирования
    product_msg_ids = []
    for i, food in enumerate(selected_foods):
        msg_id = await _send_product_card(message.chat.id, message.bot, i, food, totals_msg.message_id)
        product_msg_ids.append(msg_id)
    
    await state.update_data(
        selected_foods=selected_foods,
        totals_msg_id=totals_msg.message_id,
        product_msg_ids=product_msg_ids,
        meal_type=meal_type,
        mode="photo_ai_ingredients"
    )

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
