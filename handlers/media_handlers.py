"""
Обработчики мультимедиа: фото (распознавание еды) и голос.
Реализован интерфейс с отдельными сообщениями для каждого продукта.
Добавлена защита от повторной обработки одного и того же фото и выбор режима.
Использует LLaVA для распознавания названия блюда, затем переводит и ищет в базе.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import logging
from PIL import Image
import io
import traceback
import re
from typing import List, Dict, Optional

from services.cloudflare_ai import identify_dish_from_image, transcribe_audio, analyze_food_image
from services.food_api import search_food
from services.translator import translate_to_russian, extract_food_items
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

async def get_food_data(name: str) -> Dict:
    """Получает базовые данные продукта из локальной базы."""
    search_results = await search_food(name)
    if search_results:
        best = search_results[0]
        return {
            'name': best['name'],
            'base_calories': best.get('calories', 0),
            'base_protein': best.get('protein', 0),
            'base_fat': best.get('fat', 0),
            'base_carbs': best.get('carbs', 0)
        }
    else:
        return {
            'name': name,
            'base_calories': 0,
            'base_protein': 0,
            'base_fat': 0,
            'base_carbs': 0
        }

async def update_totals_message(chat_id: int, message_id: int, bot, selected_foods: List[Dict]):
    """Обновляет сообщение с итогами."""
    total_cal = sum(f['calories'] for f in selected_foods)
    total_prot = sum(f['protein'] for f in selected_foods)
    total_fat = sum(f['fat'] for f in selected_foods)
    total_carbs = sum(f['carbs'] for f in selected_foods)

    text = (
        f"🍽️ <b>Всего в приёме пищи:</b>\n"
        f"🔥 {total_cal:.0f} ккал | 🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_food")],
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
         InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")]
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
        if "message is not modified" in str(e):
            logger.debug("Totals message not modified, skipping")
        else:
            raise e

async def send_product_message(chat_id: int, bot, index: int, food: Dict, totals_msg_id: int) -> int:
    """Отправляет сообщение для одного продукта и возвращает его message_id."""
    weight_str = f"{food['weight']} г" if food['weight'] else "0 г"
    calories_str = f"{food['calories']:.0f} ккал" if food['weight'] else "0 ккал"

    text = (
        f"<b>{index+1}. {food['name']}</b>\n"
        f"Вес: {weight_str} — {calories_str}"
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

async def start_food_input(
    message: Message,
    state: FSMContext,
    food_names: List[str],
    meal_type: str = "snack"
):
    """
    Публичная функция для запуска интерфейса ввода продуктов.
    Используется как из обработчика фото, так и из универсального обработчика текста.
    """
    selected_foods = []
    for name in food_names:
        data = await get_food_data(name)
        selected_foods.append({
            **data,
            'weight': 0,
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0
        })

    totals_text = "🍽️ <b>Всего в приёме пищи:</b>\n🔥 0 ккал | 🥩 0.0г | 🥑 0.0г | 🍚 0.0г"
    totals_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_food")],
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
         InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")]
    ])
    totals_msg = await message.answer(totals_text, reply_markup=totals_keyboard, parse_mode="HTML")

    product_msg_ids = []
    for i, food in enumerate(selected_foods):
        msg_id = await send_product_message(message.chat.id, message.bot, i, food, totals_msg.message_id)
        product_msg_ids.append(msg_id)

    await state.update_data(
        selected_foods=selected_foods,
        totals_msg_id=totals_msg.message_id,
        product_msg_ids=product_msg_ids,
        original_items=food_names,
        meal_type=meal_type
    )

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото: распознавание блюда/ингредиентов и предложение выбора."""
    # Защита от повторной обработки
    data = await state.get_data()
    last_photo_id = data.get('last_photo_id')
    if last_photo_id == message.message_id:
        logger.info(f"📸 Повторное игнорирование фото {message.message_id}")
        return

    logger.info(f"📸 Photo received, message_id={message.message_id}, starting recognition...")
    try:
        current_state = await state.get_state()
        if current_state and not current_state.startswith("FoodStates"):
            logger.info(f"User in state {current_state}, ignoring photo")
            return

        await message.answer("🔍 Анализирую изображение через Cloudflare AI...")
        # Скачиваем и подготавливаем фото
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        optimized = _prepare_image(file_data)

        # Пытаемся определить название блюда через новую функцию
        dish_name_en = await identify_dish_from_image(optimized)
        if dish_name_en:
            dish_name_ru = await translate_to_russian(dish_name_en)
            logger.info(f"🍽 Распознано блюдо: {dish_name_ru} (оригинал: {dish_name_en})")
            # Проверяем, есть ли блюдо в базе
            dish_data = await get_food_data(dish_name_ru)
            if dish_data['base_calories'] > 0:
                # Блюдо найдено, запускаем интерфейс с одним продуктом
                await start_food_input(message, state, [dish_name_ru], meal_type="snack")
                await state.update_data(last_photo_id=message.message_id)
                return
            else:
                logger.info(f"🍽 Блюдо '{dish_name_ru}' не найдено в базе, будем использовать ингредиенты")
                # Здесь можно было бы запросить ингредиенты, но пока используем старый метод
                # (можно добавить второй запрос к модели для ингредиентов, но пока fallback)
                pass

        # Если не удалось распознать блюдо или оно не найдено, пробуем старый метод (ингредиенты)
        logger.info("No dish recognized or not in DB, trying ingredient list")
        translated_items = await recognize_food_from_photo(message)
        if not translated_items:
            await message.answer("❌ Не удалось распознать фото. Попробуйте ввести вручную через /log_food.")
            return

        await state.update_data(last_photo_id=message.message_id)
        await start_food_input(message, state, translated_items, meal_type="snack")

    except Exception as e:
        logger.error(f"❌ Photo error: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Ошибка при обработке фото. Попробуйте позже.")
        await state.clear()

async def recognize_food_from_photo(message: Message) -> List[str]:
    """Старый метод распознавания ингредиентов (на английском, с переводом)."""
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file_info.file_path)
    file_data = file_bytes.read()
    optimized = _prepare_image(file_data)

    # Используем analyze_food_image из cloudflare_ai (если она ещё есть) или отдельный запрос
    # Для простоты оставим старый вызов, но нужно импортировать analyze_food_image
    from services.cloudflare_ai import analyze_food_image
    description_en = await analyze_food_image(
        optimized,
        prompt="List all food items visible in this image. Be specific. Return as a comma-separated list."
    )
    if not description_en:
        return []
    raw_items = await extract_food_items(description_en)
    translated_items = []
    for item in raw_items:
        translated = await translate_to_russian(item)
        translated_items.append(translated)
    return translated_items

# ========== Обработчики выбора режима ==========

@router.callback_query(F.data == "food_as_dish")
async def food_as_dish_callback(callback: CallbackQuery, state: FSMContext):
    logger.info(f"🍽️ Выбрано 'Записать как блюдо', user_id={callback.from_user.id}")
    await callback.answer()
    data = await state.get_data()
    dishes = data.get('recognized_dishes', [])
    if dishes:
        dish = dishes[0]
        await start_food_input(callback.message, state, [dish['name_ru']], meal_type="snack")
    else:
        await callback.message.answer("❌ Данные не найдены")
    await callback.message.delete()

@router.callback_query(F.data == "food_as_ingredients")
async def food_as_ingredients_callback(callback: CallbackQuery, state: FSMContext):
    logger.info(f"🥗 Выбрано 'Разбить на ингредиенты', user_id={callback.from_user.id}")
    await callback.answer()
    data = await state.get_data()
    dishes = data.get('recognized_dishes', [])
    if dishes:
        all_ingredients = []
        for dish in dishes:
            all_ingredients.extend(dish.get('ingredients_ru', []))
        if all_ingredients:
            await start_food_input(callback.message, state, all_ingredients, meal_type="snack")
        else:
            logger.info("🥗 Ингредиенты не найдены, предлагаем ручной ввод")
            await callback.message.answer(
                "🥗 Не удалось распознать отдельные ингредиенты.\n"
                "Введите их вручную через запятую (например: курица, салат, сыр):"
            )
            await state.set_state(FoodStates.searching_food)
    else:
        await callback.message.answer("❌ Данные не найдены")
    await callback.message.delete()

@router.callback_query(F.data == "food_manual")
async def food_manual_callback(callback: CallbackQuery, state: FSMContext):
    logger.info(f"✏️ Выбрано 'Ввести вручную', user_id={callback.from_user.id}")
    await callback.answer()
    await callback.message.answer("📝 Введите названия продуктов через запятую:")
    await state.set_state(FoodStates.searching_food)
    await callback.message.delete()

# ========== Обработчики изменения веса продуктов (остаются без изменений) ==========
# ... (весь код weight_callback, add_food, process_add_name, process_add_weight, confirm_meal, cancel_meal и т.д.)
# Я их здесь не привожу для краткости, но они должны быть в файле.
