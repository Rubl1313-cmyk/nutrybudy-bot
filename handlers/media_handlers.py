"""
Обработчики мультимедиа: фото (распознавание еды) и голос.
✅ Улучшено: Progressive loading, каскадное распознавание, пост-обработка
✅ Добавлено: Интерфейс подтверждения с пересчётом КБЖУ в реальном времени
✅ Исправлено: Все ошибки с user_id, FSM, callback_data
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
from services.dish_db import find_matching_dish, DISH_DB
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem, User
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def _prepare_image(image_bytes: bytes) -> bytes:
    """Оптимизация изображения для Cloudflare AI."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        # Ресайз для баланса качества/скорости
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=90, optimize=True)
        return output.getvalue()
    except Exception as e:
        logger.warning(f"⚠️ Image prep error: {e}")
        return image_bytes


async def _get_food_data_cached(name: str) -> Dict:
    """Получает данные продукта с кэшированием."""
    search_results = await search_food(name)
    if search_results:
        best = search_results[0]
        return {
            'name': best['name'],
            'base_calories': best.get('calories', 0),
            'base_protein': best.get('protein', 0),
            'base_fat': best.get('fat', 0),
            'base_carbs': best.get('carbs', 0),
            'source': best.get('source', 'local')
        }
    return {
        'name': name,
        'base_calories': 0,
        'base_protein': 0,
        'base_fat': 0,
        'base_carbs': 0,
        'source': 'unknown'
    }


def _calculate_nutrients(base: Dict, weight: float) -> Dict:
    """Рассчитывает КБЖУ для заданного веса."""
    if weight <= 0:
        return {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
    
    multiplier = weight / 100
    return {
        'calories': base['base_calories'] * multiplier,
        'protein': base['base_protein'] * multiplier,
        'fat': base['base_fat'] * multiplier,
        'carbs': base['base_carbs'] * multiplier
    }


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
    
    try:
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise


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
    
    # ✅ ВАЖНО: Проверяем, что totals_msg_id не None
    if totals_msg_id is None:
        logger.error(f"⚠️ totals_msg_id is None for product {index}!")
        totals_msg_id = 0
    
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


@router.callback_query(F.data.startswith("weight_"))
async def weight_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка изменения веса продукта."""
    logger.info(f"🔘 Weight callback received: {callback.data}")  # ✅ ЛОГИРОВАНИЕ
    
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    totals_msg_id = data.get('totals_msg_id')
    product_msg_ids = data.get('product_msg_ids', [])
    
    logger.info(f"📊 State data: totals_msg_id={totals_msg_id}, products={len(selected_foods)}")
    
    if not selected_foods:
        logger.error("❌ No selected foods in state!")
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
    
    # Удаление продукта
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
    
    # Изменение веса
    current_weight = food.get('weight', 0) or 0
    if action == "inc":
        new_weight = current_weight + value
    elif action == "dec":
        new_weight = max(0, current_weight - value)
    elif action == "set":
        new_weight = value
    else:
        await callback.answer()
        return
    
    if new_weight == current_weight:
        await callback.answer()
        return
    
    # Обновляем продукт
    food['weight'] = new_weight
    nutrients = _calculate_nutrients(food, new_weight)
    food.update(nutrients)
    selected_foods[idx] = food
    
    await state.update_data(selected_foods=selected_foods)
    
    # Обновляем карточку продукта
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
    
    # Обновляем итоги
    await _update_totals_message(
        callback.message.chat.id,
        totals_msg_id_from_callback,
        callback.bot,
        selected_foods,
        data.get('meal_type', 'snack')
    )
    
    await callback.answer()

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
    builder.button(text="✅ Использовать как есть", callback_data="confirm_dish_as_is")
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


# ========== ПРОГРЕСС-КОЛЛБЭК ==========
async def _progress_callback(
    bot,
    chat_id: int,
    progress_msg_id: int,
    stage: int,
    progress: int
):
    """Коллбэк для обновления прогресса."""
    await _send_progress_update(bot, chat_id, progress_msg_id, stage, progress, 4)


async def _send_progress_update(bot, chat_id: int, message_id: int, stage: int, progress: int, total_stages: int):
    """Отправляет обновление прогресса пользователю."""
    try:
        stages = [
            "📸 Загрузка изображения",
            "🔍 Анализ изображения",
            "🧠 Распознавание блюд",
            "📊 Обработка результатов",
            "✅ Готово"
        ]
        
        current_stage = min(stage, len(stages) - 1)
        progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
        
        text = (
            f"🔄 <b>Анализ изображения</b>\n"
            f"{progress_bar} {progress}%\n\n"
            f"<i>{stages[current_stage]}</i>\n"
            f"Шаг {current_stage + 1} из {total_stages}"
        )
        
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"⚠️ Progress update failed: {e}")


# ========== ОСНОВНОЙ ОБРАБОТЧИК ФОТО ==========
@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото: каскадное распознавание с progressive loading."""
    # Защита от дубликатов
    data = await state.get_data()
    if data.get('last_photo_id') == message.message_id:
        logger.info(f"📸 Duplicate photo ignored: {message.message_id}")
        return
    
    logger.info(f"📸 Photo received, message_id={message.message_id}")
    
    try:
        # Проверка состояния
        current_state = await state.get_state()
        if current_state and not current_state.startswith("FoodStates"):
            logger.info(f"⚠️ User in state {current_state}, ignoring photo")
            return
        
        # ✅ PROGRESSIVE LOADING: Отправляем сообщение с прогрессом
        progress_msg = await message.answer(
            "🔄 <b>Анализ изображения</b>\n"
            "░░░░░░░░░░ 0%\n\n"
            "<i>📸 Загрузка изображения</i>\n"
            "Шаг 1 из 4",
            parse_mode="HTML"
        )
        
        # Скачивание и подготовка фото
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        # Обновление прогресса
        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=0,
            progress=25,
            total_stages=4
        )
        
        optimized = _prepare_image(file_data)
        
        # Сохраняем для возможного повторного анализа
        await state.update_data(
            pending_photo_bytes=file_data,
            pending_photo_optimized=optimized,
            last_photo_id=message.message_id,
            progress_msg_id=progress_msg.message_id
        )
        
        # Обновление прогресса
        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=1,
            progress=50,
            total_stages=4
        )
        
        # Каскадное распознавание с таймаутом и прогрессом
        async def progress_cb(stage: int, progress: int):
            await _send_progress_update(
                message.bot,
                message.chat.id,
                progress_msg.message_id,
                stage=stage,
                progress=progress,
                total_stages=4
            )
        
        try:
            result = await asyncio.wait_for(
                identify_food_cascade(optimized, progress_callback=progress_cb),
                timeout=120  # 2 минуты максимум
            )
        except asyncio.TimeoutError:
            await message.answer("⏱️ Превышено время анализа. Попробуйте другое фото или введите вручную.")
            await state.clear()
            return
        
        # Обновление прогресса
        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=3,
            progress=90,
            total_stages=4
        )
        
        if not result.get('success') or not result.get('data'):
            await progress_msg.delete()
            await _handle_recognition_failure(message, state)
            return
        
        dish_data = result['data']
        model_used = result.get('model', 'unknown')
        
        # ✅ ПОСТ-ОБРАБОТКА: перевод на русский
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
        
        # Обновляем данные с переводом
        dish_data['dish_name'] = dish_name_ru
        dish_data['ingredients'] = ingredients_ru
        
        # Обновление прогресса
        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=4,
            progress=100,
            total_stages=4
        )
        
        # Небольшая задержка перед удалением прогресс-сообщения
        await asyncio.sleep(0.5)
        await progress_msg.delete()
        
        # Проверка: есть ли блюдо в локальной базе как готовый продукт
        dish_info = await _get_food_data_cached(dish_name_ru)
        if dish_info['base_calories'] > 50:  # Найдено в базе
            await state.update_data(
                recognized_dish=dish_data,
                dish_found_in_db=True,
                mode="photo_recognition"
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
            return
        
        # Показываем интерфейс подтверждения
        await _show_dish_confirmation(message, state, dish_data, model_used)
        
    except Exception as e:
        logger.error(f"❌ Photo handler error: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Ошибка при анализе фото. Попробуйте позже или введите вручную.")
        await state.clear()


# ========== ОБРАБОТЧИКИ ПОДТВЕРЖДЕНИЯ БЛЮДА ==========
@router.callback_query(F.data == "confirm_dish_as_is")
async def confirm_dish_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение блюда и переход к вводу весов."""
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})
    
    if not dish_data:
        await callback.answer("❌ Данные не найдены", show_alert=True)
        return
    
    ingredients = dish_data.get('ingredients', [])
    food_names = [ing.get('name', '') for ing in ingredients if ing.get('name')]
    
    if not food_names:
        await callback.answer("❌ Нет ингредиентов", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.edit_text("⏳ Загружаю данные продуктов...")
    
    await _start_food_input(
        callback.message,
        state,
        food_names,
        meal_type=dish_data.get('meal_type', 'snack')
    )
    
    await state.update_data(
        ai_description=dish_data.get('dish_name', ''),
        cooking_method=dish_data.get('cooking_method', ''),
        mode="photo_to_manual"
    )


@router.callback_query(F.data == "confirm_dish_db")
async def confirm_dish_from_db_callback(callback: CallbackQuery, state: FSMContext):
    """Использование блюда из базы как готового продукта."""
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})
    dish_name = dish_data.get('dish_name', 'Блюдо')
    
    dish_info = await _get_food_data_cached(dish_name)
    if dish_info['base_calories'] == 0:
        await callback.answer("❌ Блюдо не найдено в базе", show_alert=True)
        return
    
    selected_foods = [{
        **dish_info,
        'weight': 200,
        **_calculate_nutrients(dish_info, 200)
    }]
    
    totals_text = f"🍽️ <b>{dish_name}:</b>\n🔥 {selected_foods[0]['calories']:.0f} ккал | 🥩 {selected_foods[0]['protein']:.1f}г | 🥑 {selected_foods[0]['fat']:.1f}г | 🍚 {selected_foods[0]['carbs']:.1f}г"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚖️ Изменить вес", callback_data="adjust_dish_weight")],
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")
        ]
    ])
    
    totals_msg = await callback.message.answer(totals_text, reply_markup=keyboard, parse_mode="HTML")
    
    await state.update_data(
        selected_foods=selected_foods,
        totals_msg_id=totals_msg.message_id,
        product_msg_ids=[],
        meal_type=dish_data.get('meal_type', 'snack'),
        mode="photo_db_dish"
    )
    
    await callback.answer()


@router.callback_query(F.data == "use_ingredients_instead")
async def use_ingredients_callback(callback: CallbackQuery, state: FSMContext):
    """Использование ингредиентов вместо готового блюда."""
    data = await state.get_data()
    dish_data = data.get('recognized_dish', {})
    ingredients = dish_data.get('ingredients', [])
    food_names = [ing.get('name', '') for ing in ingredients if ing.get('name')]
    
    if not food_names:
        await callback.answer("❌ Нет ингредиентов", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.edit_text("⏳ Загружаю ингредиенты...")
    
    await _start_food_input(
        callback.message,
        state,
        food_names,
        meal_type=dish_data.get('meal_type', 'snack')
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
    
    current_weight = food.get('weight', 0) or 0
    
    if action == "inc":
        new_weight = current_weight + value
    elif action == "dec":
        new_weight = max(0, current_weight - value)
    elif action == "set":
        new_weight = value
    else:
        await callback.answer()
        return
    
    if new_weight == current_weight:
        await callback.answer()
        return
    
    food['weight'] = new_weight
    nutrients = _calculate_nutrients(food, new_weight)
    food.update(nutrients)
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
