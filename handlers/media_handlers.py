"""
Обработчики мультимедиа: фото (распознавание еды) и голос.
Реализован интерфейс с отдельными сообщениями для каждого продукта.
Добавлена публичная функция start_food_input для использования из других модулей.
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

from services.cloudflare_ai import analyze_food_image, transcribe_audio
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

async def identify_dish_from_photo(message: Message) -> Optional[Dict]:
    """
    Распознаёт название блюда на фото и возвращает словарь с названием и ингредиентами.
    """
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file_info.file_path)
    file_data = file_bytes.read()
    optimized = _prepare_image(file_data)

    # Промпт на английском, чтобы модель понимала
    prompt = (
"Analyze this food image. "
        "FIRST: Try to identify if this is a KNOWN DISH"
        "If it's a known dish, return ONLY the dish name. "
        "SECOND: If it's not a known dish or contains multiple separate items, list the MAIN visible food items (max 5). "
        "Return as a comma-separated list in English. "
        "Examples: 'caesar salad with shrimp', 'grilled chicken with rice', 'tomato, cucumber, cheese'."
    )
    description_en = await analyze_food_image(optimized, prompt=prompt, max_tokens=200)
    if not description_en:
        return None

    logger.info(f"Vision raw response: {description_en}")

    # Парсим ответ
    dish_match = re.search(r'Dish:\s*(.+?)(?:\n|$)', description_en, re.IGNORECASE)
    ingredients_match = re.search(r'Ingredients:\s*(.+)', description_en, re.IGNORECASE)

    dish_name_en = dish_match.group(1).strip() if dish_match else None
    ingredients_text = ingredients_match.group(1).strip() if ingredients_match else None

    # Если нет ингредиентов, пробуем старый метод
    if not ingredients_text:
        ingredients_text = description_en

    # Переводим название блюда на русский
    dish_name_ru = None
    if dish_name_en:
        dish_name_ru = await translate_to_russian(dish_name_en)
        logger.info(f"Translated dish name: {dish_name_en} -> {dish_name_ru}")

    # Извлекаем ингредиенты и переводим
    raw_items = await extract_food_items(ingredients_text)
    translated_items = []
    for item in raw_items:
        translated = await translate_to_russian(item)
        if translated and translated != item:
            translated_items.append(translated)
        else:
            # Если перевод не удался, оставляем оригинал (он может быть английским)
            # Попробуем поискать в локальной базе, но для отображения лучше оставить
            translated_items.append(item)

    result = {
        "dish_name": dish_name_ru,  # теперь на русском
        "ingredients": translated_items
    }
    logger.info(f"Parsed dish info: {result}")
    return result

async def recognize_food_from_photo(message: Message) -> List[str]:
    """
    Распознаёт продукты на фото и возвращает список названий на русском.
    (Старый метод, используемый как fallback)
    """
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file_info.file_path)
    file_data = file_bytes.read()
    optimized = _prepare_image(file_data)

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
    # Инициализируем список продуктов
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

    # Отправляем сообщение с итогами
    totals_text = "🍽️ <b>Всего в приёме пищи:</b>\n🔥 0 ккал | 🥩 0.0г | 🥑 0.0г | 🍚 0.0г"
    totals_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_food")],
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
         InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")]
    ])
    totals_msg = await message.answer(totals_text, reply_markup=totals_keyboard, parse_mode="HTML")

    # Отправляем сообщения для каждого продукта и сохраняем их ID
    product_msg_ids = []
    for i, food in enumerate(selected_foods):
        msg_id = await send_product_message(message.chat.id, message.bot, i, food, totals_msg.message_id)
        product_msg_ids.append(msg_id)

    # Сохраняем все данные в state
    await state.update_data(
        selected_foods=selected_foods,
        totals_msg_id=totals_msg.message_id,
        product_msg_ids=product_msg_ids,
        original_items=food_names,
        meal_type=meal_type
    )

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото: распознавание и запуск интерфейса ввода."""
    logger.info("📸 Photo received, starting recognition...")
    try:
        current_state = await state.get_state()
        if current_state and not current_state.startswith("FoodStates"):
            logger.info(f"User in state {current_state}, ignoring photo")
            return

        await message.answer("🔍 Анализирую изображение через Cloudflare AI...")

        # Сначала пытаемся распознать как готовое блюдо
        dish_info = await identify_dish_from_photo(message)
        if dish_info and dish_info.get('dish_name'):
            # Ищем блюдо в базе
            dish_data = await get_food_data(dish_info['dish_name'])
            if dish_data and dish_data.get('base_calories', 0) > 0:
                # Блюдо найдено в базе, используем как один продукт
                await start_food_input(message, state, [dish_info['dish_name']], meal_type="snack")
                return
            else:
                # Блюдо не найдено, используем ингредиенты
                logger.info(f"Dish '{dish_info['dish_name']}' not found in DB, using ingredients")
                if dish_info.get('ingredients'):
                    await start_food_input(message, state, dish_info['ingredients'], meal_type="snack")
                    return
                # Если нет ингредиентов, падаем на старый метод

        # Fallback: старый метод распознавания ингредиентов
        logger.info("Falling back to ingredient recognition")
        translated_items = await recognize_food_from_photo(message)

        if not translated_items:
            await message.answer(
                "❌ Не удалось распознать фото. Попробуйте ввести вручную через /log_food."
            )
            return

        await start_food_input(message, state, translated_items, meal_type="snack")

    except Exception as e:
        logger.error(f"❌ Photo error: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Ошибка при обработке фото. Попробуйте позже.")
        await state.clear()

# ... остальные обработчики без изменений
