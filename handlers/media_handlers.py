"""
handlers/media_handlers.py
Обработчики мультимедиа: фото (распознавание еды) и голос.
✅ ВЕРСИЯ: Прогресс-бар + все исправления + обработка ошибок
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
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem, User
from sqlalchemy import select
from services.dish_db import COMPOSITE_DISHES, get_dish_ingredients, find_matching_dish

router = Router()
logger = logging.getLogger(__name__)

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
        return {
            'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0
        }

    multiplier = weight / 100.0

    # Получаем базовые значения с дефолтами
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
    """
    Отправляет обновление прогресса пользователю.
    ✅ ЗЕЛЁНЫЕ КВАДРАТИКИ
    """
    try:
        stages = [
            "📸 Загрузка изображения...",
            "🔍 Анализ изображения (AI)...",
            "🧠 Обработка результатов...",
            "📊 Поиск в базе продуктов...",
            "✅ Готово!"
        ]

        current_stage = min(stage, len(stages) - 1)

        # ✅ ЗЕЛЁНЫЕ КВАДРАТИКИ
        filled = int(progress // 10)
        green_squares = "🟩" * filled
        empty_squares = "⬜" * (10 - filled)
        progress_bar = green_squares + empty_squares

        text = (
            f"🔄 <b>Анализ изображения</b>\n\n"
            f"{progress_bar}\n"
            f"<b>{progress}%</b>\n\n"
            f"<i>{stages[current_stage]}</i>\n"
            f"Шаг {current_stage + 1} из {total_stages}\n\n"
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
        # Получаем данные продукта из базы
        data = await _get_food_data_cached(name)

        # 🔥 ВАЖНО: Сохраняем базовые значения отдельно
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
        mode="manual"  # Ручной ввод, не фото
    )

async def _start_food_input_with_weights(
    message: Message,
    state: FSMContext,
    food_items: List[Dict],
    meal_type: str = "snack"
):
    """Запускает интерфейс ввода продуктов с уже указанными весами."""
    selected_foods = []

    for item in food_items:
        name = item['name']
        recognized_weight = item.get('weight', 0)

        # Получаем данные продукта из базы
        data = await _get_food_data_cached(name)

        # 🔥 Рассчитываем КБЖУ с распознанным весом
        nutrients = _calculate_nutrients(data, recognized_weight)

        selected_foods.append({
            'name': data['name'],
            'base_calories': data['base_calories'],
            'base_protein': data['base_protein'],
            'base_fat': data['base_fat'],
            'base_carbs': data['base_carbs'],
            'weight': recognized_weight,
            'calories': nutrients['calories'],
            'protein': nutrients['protein'],
            'fat': nutrients['fat'],
            'carbs': nutrients['carbs'],
            'source': data.get('source', 'unknown')
        })

    # Обновляем сообщение с итогами
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
        mode="photo_recognition"
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

    # Формируем текст ТОЛЬКО с тем, что распознал AI
    text = f"🍽 <b>Распознано ({model_used}): {dish_name}</b>\n"
    text += f"🎯 Уверенность: {confidence:.0%}\n"

    # ИСПРАВЛЕНИЕ: Убираем лишний отступ перед следующими строками
    if ingredients:
        text += f"📋 Состав: {', '.join(ingredients)}\n"

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Всё верно", callback_data="confirm_dish")],
        [InlineKeyboardButton(text="✏️ Выбрать из списка", callback_data="select_from_list")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_recognition")]
    ])

    # Отправляем сообщение
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# ========== ОСНОВНЫЕ ОБРАБОТЧИКИ ==========

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обрабатывает фото еды."""
    progress_msg = None
    try:
        # Получаем текущее состояние пользователя
        current_state = await state.get_state()
        logger.info(f"📸 handle_photo вызван. Состояние: {current_state}")

        # Проверяем, не находится ли пользователь в процессе ввода веса
        if current_state == FoodStates.waiting_for_weight.state:
            await message.answer("⏳ Пожалуйста, сначала завершите ввод веса для предыдущего продукта.")
            return

        # Проверяем, не начат ли уже приём пищи
        data = await state.get_data()
        if data.get('selected_foods'):
            # Если уже есть продукты, предлагаем добавить фото как отдельный продукт
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ Добавить как отдельный продукт", callback_data="add_photo_as_food")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_photo")]
            ])
            await message.answer(
                "📸 Вы уже добавляете продукты. Хотите добавить это фото как отдельный приём пищи?",
                reply_markup=keyboard
            )
            await state.set_state(FoodStates.waiting_for_photo_decision)
            return

        # Отправляем сообщение о начале обработки
        progress_msg = await message.answer(
            "🔄 <b>Анализ изображения</b>\n\n"
            "🟩🟩🟩🟩🟩⬜⬜⬜⬜⬜\n"
            "<b>50%</b>\n\n"
            "<i>📸 Загрузка изображения...</i>\n"
            "Шаг 1 из 5\n\n"
            "<i>⏱️ Это займёт около 15-20 секунд</i>",
            parse_mode="HTML"
        )

        # Получаем файл фото
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        image_bytes = await message.bot.download_file(file.file_path)
        image_bytes = image_bytes.read()

        # Оптимизируем изображение
        image_bytes = _prepare_image(image_bytes)

        # Обновляем прогресс
        await _send_progress_update(message.bot, message.chat.id, progress_msg.message_id, stage=1, progress=20)

        # Запускаем распознавание
        result = await identify_food_cascade(image_bytes)

        if not result or 'error' in result:
            # Пробуем мультимодельный метод
            await _send_progress_update(message.bot, message.chat.id, progress_msg.message_id, stage=2, progress=40)
            result = await identify_food_multimodel(image_bytes)

        if not result or 'error' in result:
            await message.answer("❌ Не удалось распознать еду на фото. Попробуйте другое фото или введите название вручную.")
            if progress_msg:
                await progress_msg.delete()
            return

        # Обновляем прогресс
        await _send_progress_update(message.bot, message.chat.id, progress_msg.message_id, stage=3, progress=60)

        # Проверяем, есть ли в результате блюдо или ингредиенты
        if 'dish_name' in result and result['dish_name']:
            # Это блюдо
            await _show_dish_confirmation(message, state, result, "AI")

            # Сохраняем данные в состояние
            await state.update_data(
                recognition_result=result,
                mode="dish_recognition"
            )

        elif 'items' in result and result['items']:
            # Это список продуктов
            await _send_progress_update(message.bot, message.chat.id, progress_msg.message_id, stage=4, progress=80)

            food_items = result['items']
            # Запускаем интерфейс ввода с весами
            await _start_food_input_with_weights(message, state, food_items)

        else:
            await message.answer("❌ Не удалось распознать состав блюда. Попробуйте другое фото или введите вручную.")
            if progress_msg:
                await progress_msg.delete()
            return

        # Финальное обновление прогресса
        await _send_progress_update(message.bot, message.chat.id, progress_msg.message_id, stage=5, progress=100)

        # Удаляем сообщение с прогрессом через 2 секунды
        await asyncio.sleep(2)
        if progress_msg:
            await progress_msg.delete()

    except Exception as e:
        logger.error(f"❌ Ошибка в handle_photo: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Произошла ошибка при обработке фото. Попробуйте ещё раз.")
        if progress_msg:
            await progress_msg.delete()

@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    """Обрабатывает голосовые сообщения."""
    try:
        # Получаем файл голоса
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        voice_bytes = await message.bot.download_file(file.file_path)
        voice_bytes = voice_bytes.read()

        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("🔄 <b>Распознаю голос...</b>", parse_mode="HTML")

        # Транскрибируем аудио
        text = await transcribe_audio(voice_bytes)

        if not text:
            await processing_msg.edit_text("❌ Не удалось распознать речь. Попробуйте ещё раз.")
            return

        # Удаляем сообщение о обработке
        await processing_msg.delete()

        # Отправляем распознанный текст
        await message.answer(f"📝 <b>Распознано:</b>\n{text}", parse_mode="HTML")

        # Анализируем текст на наличие продуктов
        # Простой парсинг: ищем слова, которые могут быть продуктами
        # В реальном проекте здесь может быть более сложная логика
        words = text.lower().split()
        potential_foods = []

        # Заглушка: в реальном проекте здесь должен быть вызов NLP сервиса
        # Пока просто показываем пользователю текст и предлагаем ввести продукты вручную
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить продукты вручную", callback_data="manual_food_input")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])

        await message.answer(
            "🍽 <b>Что вы хотите сделать с распознанным текстом?</b>\n"
            "Вы можете добавить продукты вручную или попробовать распознать фото.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"❌ Ошибка в handle_voice: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Произошла ошибка при обработке голоса. Попробуйте ещё раз.")

# ========== ОБРАБОТЧИКИ КОЛБЭКОВ ==========

@router.callback_query(F.data == "confirm_dish")
async def confirm_dish(callback: CallbackQuery, state: FSMContext):
    """Подтверждает распознанное блюдо."""
    try:
        data = await state.get_data()
        dish_data = data.get('recognition_result', {})
        dish_name = dish_data.get('dish_name', '')

        if not dish_name:
            await callback.answer("❌ Данные о блюде не найдены")
            return

        # Ищем блюдо в базе
        dish_info = find_matching_dish(dish_name)

        if dish_info and dish_info.get('ingredients'):
            # Создаем список продуктов из ингредиентов блюда
            food_items = []
            for ing in dish_info['ingredients']:
                food_items.append({
                    'name': ing['name'],
                    'weight': ing.get('default_weight', 100)  # Используем вес по умолчанию
                })

            # Запускаем интерфейс ввода
            await _start_food_input_with_weights(callback.message, state, food_items, meal_type="snack")
        else:
            # Если блюдо не найдено в базе, используем только название
            await _start_food_input(callback.message, state, [dish_name])

        await callback.answer("✅ Блюдо подтверждено")
        await callback.message.delete()

    except Exception as e:
        logger.error(f"❌ Ошибка в confirm_dish: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data == "select_from_list")
async def select_from_list(callback: CallbackQuery, state: FSMContext):
    """Показывает список похожих блюд для выбора."""
    try:
        data = await state.get_data()
        dish_data = data.get('recognition_result', {})
        dish_name = dish_data.get('dish_name', '')

        # Ищем похожие блюда в базе
        similar_dishes = []
        for dish_key, dish_info in COMPOSITE_DISHES.items():
            if dish_name.lower() in dish_key.lower() or dish_key.lower() in dish_name.lower():
                similar_dishes.append((dish_key, dish_info))

        if not similar_dishes:
            # Если нет похожих, предлагаем ввести вручную
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="manual_food_input")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_recognition")]
            ])
            await callback.message.edit_text(
                "❌ Похожих блюд не найдено. Хотите ввести название вручную?",
                reply_markup=keyboard
            )
            await callback.answer()
            return

        # Создаем клавиатуру со списком блюд
        builder = InlineKeyboardBuilder()
        for dish_key, _ in similar_dishes[:10]:  # Ограничиваем 10 вариантами
            builder.button(text=dish_key, callback_data=f"select_dish_{dish_key}")
        builder.button(text="❌ Отмена", callback_data="cancel_recognition")
        builder.adjust(1)

        await callback.message.edit_text(
            "🍽 <b>Выберите блюдо из списка:</b>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Ошибка в select_from_list: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data.startswith("select_dish_"))
async def select_dish(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор блюда из списка."""
    try:
        dish_key = callback.data.replace("select_dish_", "")
        dish_info = COMPOSITE_DISHES.get(dish_key)

        if not dish_info:
            await callback.answer("❌ Блюдо не найдено")
            return

        # Создаем список продуктов из ингредиентов
        food_items = []
        for ing in dish_info['ingredients']:
            food_items.append({
                'name': ing['name'],
                'weight': ing.get('default_weight', 100)
            })

        # Запускаем интерфейс ввода
        await _start_food_input_with_weights(callback.message, state, food_items, meal_type="snack")
        await callback.answer("✅ Блюдо выбрано")
        await callback.message.delete()

    except Exception as e:
        logger.error(f"❌ Ошибка в select_dish: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data == "cancel_recognition")
async def cancel_recognition(callback: CallbackQuery, state: FSMContext):
    """Отменяет распознавание."""
    await state.clear()
    await callback.message.edit_text("❌ Распознавание отменено.")
    await callback.answer()

@router.callback_query(F.data == "add_food")
async def add_food(callback: CallbackQuery, state: FSMContext):
    """Добавляет новый продукт в текущий приём пищи."""
    try:
        await callback.message.edit_text("✏️ <b>Введите название продукта:</b>", parse_mode="HTML")
        await state.set_state(FoodStates.waiting_for_food_name)
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Ошибка в add_food: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.message(FoodStates.waiting_for_food_name)
async def process_food_name(message: Message, state: FSMContext):
    """Обрабатывает ввод названия продукта."""
    try:
        food_name = message.text.strip()

        if not food_name:
            await message.answer("❌ Название не может быть пустым. Попробуйте ещё раз:")
            return

        # Получаем текущие данные
        data = await state.get_data()
        selected_foods = data.get('selected_foods', [])

        # Получаем данные о продукте
        food_data = await _get_food_data_cached(food_name)

        # Добавляем новый продукт
        new_food = {
            'name': food_data['name'],
            'base_calories': food_data['base_calories'],
            'base_protein': food_data['base_protein'],
            'base_fat': food_data['base_fat'],
            'base_carbs': food_data['base_carbs'],
            'weight': 0,
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
            'source': food_data.get('source', 'unknown')
        }

        selected_foods.append(new_food)
        index = len(selected_foods) - 1

        # Отправляем карточку продукта
        totals_msg_id = data.get('totals_msg_id')
        product_msg_id = await _send_product_card(
            message.chat.id,
            message.bot,
            index,
            new_food,
            totals_msg_id
        )

        # Обновляем список ID сообщений
        product_msg_ids = data.get('product_msg_ids', [])
        product_msg_ids.append(product_msg_id)

        # Обновляем данные в состоянии
        await state.update_data(
            selected_foods=selected_foods,
            product_msg_ids=product_msg_ids
        )

        # Обновляем сообщение с итогами
        await _update_totals_message(
            message.chat.id,
            totals_msg_id,
            message.bot,
            selected_foods,
            data.get('meal_type', 'snack')
        )

        # Подтверждаем добавление
        await message.answer(f"✅ Продукт <b>{food_data['name']}</b> добавлен. Вы можете изменить вес с помощью кнопок.",
                           parse_mode="HTML")

        # Возвращаемся в состояние редактирования
        await state.set_state(FoodStates.editing)

    except Exception as e:
        logger.error(f"❌ Ошибка в process_food_name: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Произошла ошибка при добавлении продукта. Попробуйте ещё раз.")

@router.callback_query(F.data.startswith(("weight_inc_", "weight_dec_", "weight_set_", "weight_del_")))
async def handle_weight_change(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает изменение веса продукта."""
    try:
        # Парсим callback_data
        parts = callback.data.split('_')
        action = parts[0]  # weight
        operation = parts[1]  # inc, dec, set, del
        index = int(parts[2])
        value = int(parts[3]) if operation in ['inc', 'dec', 'set'] else None
        totals_msg_id = int(parts[4]) if operation in ['inc', 'dec', 'set'] else int(parts[3])

        # Получаем текущие данные
        data = await state.get_data()
        selected_foods = data.get('selected_foods', [])

        if index >= len(selected_foods):
            await callback.answer("❌ Продукт не найден")
            return

        food = selected_foods[index]

        # Обновляем вес в зависимости от операции
        if operation == 'inc':
            food['weight'] = food.get('weight', 0) + value
        elif operation == 'dec':
            new_weight = food.get('weight', 0) - value
            food['weight'] = max(0, new_weight)
        elif operation == 'set':
            food['weight'] = value
        elif operation == 'del':
            # Удаляем продукт
            selected_foods.pop(index)

            # Удаляем сообщение с карточкой продукта
            try:
                await callback.message.delete()
            except:
                pass

            # Обновляем индексы в оставшихся сообщениях
            product_msg_ids = data.get('product_msg_ids', [])
            if index < len(product_msg_ids):
                product_msg_ids.pop(index)

            # Обновляем данные в состоянии
            await state.update_data(
                selected_foods=selected_foods,
                product_msg_ids=product_msg_ids
            )

            # Обновляем сообщение с итогами
            await _update_totals_message(
                callback.message.chat.id,
                totals_msg_id,
                callback.message.bot,
                selected_foods,
                data.get('meal_type', 'snack')
            )

            await callback.answer("✅ Продукт удалён")
            return

        # Пересчитываем КБЖУ для продукта
        nutrients = _calculate_nutrients(food, food['weight'])
        food['calories'] = nutrients['calories']
        food['protein'] = nutrients['protein']
        food['fat'] = nutrients['fat']
        food['carbs'] = nutrients['carbs']

        # Обновляем данные в состоянии
        selected_foods[index] = food
        await state.update_data(selected_foods=selected_foods)

        # Обновляем сообщение с карточкой продукта
        weight_str = f"{food['weight']} г" if food['weight'] else "0 г"
        text = (
            f"<b>{index+1}. {food['name']}</b>\n"
            f"⚖️ Вес: {weight_str}\n"
            f"🔥 {nutrients['calories']:.0f} ккал | 🥩 {nutrients['protein']:.1f}г | 🥑 {nutrients['fat']:.1f}г | 🍚 {nutrients['carbs']:.1f}г"
        )

        # Обновляем клавиатуру (она остаётся той же)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="➖10", callback_data=f"weight_dec_{index}_10_{totals_msg_id}"),
            InlineKeyboardButton(text="➕10", callback_data=f"weight_inc_{index}_10_{totals_msg_id}"),
            InlineKeyboardButton(text="50", callback_data=f"weight_set_{index}_50_{totals_msg_id}"),
            InlineKeyboardButton(text="100", callback_data=f"weight_set_{index}_100_{totals_msg_id}"),
            InlineKeyboardButton(text="200", callback_data=f"weight_set_{index}_200_{totals_msg_id}"),
            InlineKeyboardButton(text="❌", callback_data=f"weight_del_{index}_{totals_msg_id}")
        ]])

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

        # Обновляем сообщение с итогами
        await _update_totals_message(
            callback.message.chat.id,
            totals_msg_id,
            callback.message.bot,
            selected_foods,
            data.get('meal_type', 'snack')
        )

        await callback.answer(f"✅ Вес изменён: {food['weight']} г")

    except Exception as e:
        logger.error(f"❌ Ошибка в handle_weight_change: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data == "confirm_meal")
async def confirm_meal(callback: CallbackQuery, state: FSMContext):
    """Подтверждает приём пищи и сохраняет в БД."""
    try:
        data = await state.get_data()
        selected_foods = data.get('selected_foods', [])
        meal_type = data.get('meal_type', 'snack')

        if not selected_foods:
            await callback.answer("❌ Нет продуктов для сохранения")
            return

        # Получаем ID пользователя
        user_id = callback.from_user.id

        # Сохраняем в БД
        async with get_session() as session:
            # Получаем пользователя из БД
            result = await session.execute(
                select(User).where(User.telegram_id == str(user_id))
            )
            user = result.scalar_one_or_none()

            if not user:
                # Создаём пользователя, если его нет
                user = User(
                    telegram_id=str(user_id),
                    username=callback.from_user.username,
                    first_name=callback.from_user.first_name,
                    last_name=callback.from_user.last_name
                )
                session.add(user)
                await session.flush()

            # Создаём запись о приёме пищи
            meal = Meal(
                user_id=user.id,
                meal_type=meal_type,
                timestamp=datetime.utcnow()
            )
            session.add(meal)
            await session.flush()

            # Добавляем продукты
            for food in selected_foods:
                food_item = FoodItem(
                    meal_id=meal.id,
                    name=food['name'],
                    weight=food.get('weight', 0),
                    calories=food.get('calories', 0),
                    protein=food.get('protein', 0),
                    fat=food.get('fat', 0),
                    carbs=food.get('carbs', 0),
                    source=food.get('source', 'manual')
                )
                session.add(food_item)

            await session.commit()

        # Подводим итоги
        total_cal = sum(f.get('calories', 0) for f in selected_foods)
        total_prot = sum(f.get('protein', 0) for f in selected_foods)
        total_fat = sum(f.get('fat', 0) for f in selected_foods)
        total_carbs = sum(f.get('carbs', 0) for f in selected_foods)

        summary = (
            f"✅ <b>Приём пищи сохранён!</b>\n\n"
            f"🍽 Тип: {meal_type}\n"
            f"🔥 Всего: {total_cal:.0f} ккал\n"
            f"🥩 Белки: {total_prot:.1f}г\n"
            f"🥑 Жиры: {total_fat:.1f}г\n"
            f"🍚 Углеводы: {total_carbs:.1f}г\n\n"
            f"📝 Детали:\n"
        )

        for i, food in enumerate(selected_foods):
            summary += f"{i+1}. {food['name']} — {food.get('weight', 0)}г\n"

        await callback.message.edit_text(summary, parse_mode="HTML")

        # Очищаем состояние
        await state.clear()

        # Удаляем карточки продуктов
        product_msg_ids = data.get('product_msg_ids', [])
        for msg_id in product_msg_ids:
            try:
                await callback.message.bot.delete_message(callback.message.chat.id, msg_id)
            except:
                pass

    except Exception as e:
        logger.error(f"❌ Ошибка в confirm_meal: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка при сохранении")

@router.callback_query(F.data == "cancel_meal")
async def cancel_meal(callback: CallbackQuery, state: FSMContext):
    """Отменяет создание приёма пищи."""
    try:
        data = await state.get_data()

        # Удаляем карточки продуктов
        product_msg_ids = data.get('product_msg_ids', [])
        for msg_id in product_msg_ids:
            try:
                await callback.message.bot.delete_message(callback.message.chat.id, msg_id)
            except:
                pass

        # Удаляем сообщение с итогами
        await callback.message.delete()

        # Очищаем состояние
        await state.clear()

        await callback.message.answer("❌ Приём пищи отменён.")
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Ошибка в cancel_meal: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.message(FoodStates.waiting_for_photo_decision)
async def process_photo_decision(message: Message, state: FSMContext):
    """Обрабатывает решение пользователя о добавлении фото в текущий приём пищи."""
    # Этот обработчик нужен для текстовых ответов после вопроса о фото
    # Пока просто игнорируем и напоминаем о кнопках
    await message.answer("Пожалуйста, используйте кнопки для выбора действия.")

@router.callback_query(F.data == "add_photo_as_food")
async def add_photo_as_food(callback: CallbackQuery, state: FSMContext):
    """Добавляет фото как отдельный продукт в текущий приём пищи."""
    try:
        await callback.message.edit_text("📸 Отправьте фото продукта, который хотите добавить.")
        await state.set_state(FoodStates.waiting_for_photo)
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Ошибка в add_photo_as_food: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data == "cancel_photo")
async def cancel_photo(callback: CallbackQuery, state: FSMContext):
    """Отменяет добавление фото."""
    try:
        await callback.message.edit_text("❌ Добавление фото отменено.")
        await state.set_state(FoodStates.editing)
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Ошибка в cancel_photo: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.message(FoodStates.waiting_for_photo)
async def process_additional_photo(message: Message, state: FSMContext):
    """Обрабатывает дополнительное фото для добавления в текущий приём пищи."""
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото.")
        return

    progress_msg = None
    try:
        # Отправляем сообщение о начале обработки
        progress_msg = await message.answer("🔄 <b>Анализирую фото...</b>", parse_mode="HTML")

        # Получаем файл фото
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        image_bytes = await message.bot.download_file(file.file_path)
        image_bytes = image_bytes.read()

        # Оптимизируем изображение
        image_bytes = _prepare_image(image_bytes)

        # Распознаём
        result = await identify_food_cascade(image_bytes)

        if not result or 'error' in result:
            result = await identify_food_multimodel(image_bytes)

        if not result or 'error' in result:
            await progress_msg.edit_text("❌ Не удалось распознать еду на фото. Попробуйте другое фото.")
            return

        # Получаем текущие данные
        data = await state.get_data()
        selected_foods = data.get('selected_foods', [])
        totals_msg_id = data.get('totals_msg_id')

        # Обрабатываем результат
        if 'dish_name' in result and result['dish_name']:
            # Это блюдо - используем название как продукт
            food_name = result['dish_name']
            weight = result.get('ingredients', [{}])[0].get('weight', 100) if result.get('ingredients') else 100

            food_data = await _get_food_data_cached(food_name)

            new_food = {
                'name': food_data['name'],
                'base_calories': food_data['base_calories'],
                'base_protein': food_data['base_protein'],
                'base_fat': food_data['base_fat'],
                'base_carbs': food_data['base_carbs'],
                'weight': weight,
                'calories': 0,
                'protein': 0,
                'fat': 0,
                'carbs': 0,
                'source': food_data.get('source', 'unknown')
            }

            # Пересчитываем КБЖУ
            nutrients = _calculate_nutrients(new_food, weight)
            new_food['calories'] = nutrients['calories']
            new_food['protein'] = nutrients['protein']
            new_food['fat'] = nutrients['fat']
            new_food['carbs'] = nutrients['carbs']

        elif 'items' in result and result['items']:
            # Это список продуктов - берём первый
            item = result['items'][0]
            food_name = item['name']
            weight = item.get('weight', 100)

            food_data = await _get_food_data_cached(food_name)

            new_food = {
                'name': food_data['name'],
                'base_calories': food_data['base_calories'],
                'base_protein': food_data['base_protein'],
                'base_fat': food_data['base_fat'],
                'base_carbs': food_data['base_carbs'],
                'weight': weight,
                'calories': 0,
                'protein': 0,
                'fat': 0,
                'carbs': 0,
                'source': food_data.get('source', 'unknown')
            }

            # Пересчитываем КБЖУ
            nutrients = _calculate_nutrients(new_food, weight)
            new_food['calories'] = nutrients['calories']
            new_food['protein'] = nutrients['protein']
            new_food['fat'] = nutrients['fat']
            new_food['carbs'] = nutrients['carbs']
        else:
            await progress_msg.edit_text("❌ Не удалось распознать состав. Попробуйте другое фото.")
            return

        # Добавляем продукт
        selected_foods.append(new_food)
        index = len(selected_foods) - 1

        # Отправляем карточку продукта
        product_msg_id = await _send_product_card(
            message.chat.id,
            message.bot,
            index,
            new_food,
            totals_msg_id
        )

        # Обновляем список ID сообщений
        product_msg_ids = data.get('product_msg_ids', [])
        product_msg_ids.append(product_msg_id)

        # Обновляем данные в состоянии
        await state.update_data(
            selected_foods=selected_foods,
            product_msg_ids=product_msg_ids
        )

        # Обновляем сообщение с итогами
        await _update_totals_message(
            message.chat.id,
            totals_msg_id,
            message.bot,
            selected_foods,
            data.get('meal_type', 'snack')
        )

        # Удаляем сообщение о прогрессе
        await progress_msg.delete()

        # Подтверждаем добавление
        await message.answer(f"✅ Продукт <b>{new_food['name']}</b> добавлен с весом {weight} г. Вы можете изменить вес с помощью кнопок.",
                           parse_mode="HTML")

        # Возвращаемся в состояние редактирования
        await state.set_state(FoodStates.editing)

    except Exception as e:
        logger.error(f"❌ Ошибка в process_additional_photo: {e}\n{traceback.format_exc()}")
        if progress_msg:
            await progress_msg.edit_text("❌ Произошла ошибка при обработке фото.")
        else:
            await message.answer("❌ Произошла ошибка при обработке фото.")

@router.callback_query(F.data == "manual_food_input")
async def manual_food_input(callback: CallbackQuery, state: FSMContext):
    """Запускает ручной ввод продуктов."""
    try:
        await callback.message.edit_text(
            "✏️ <b>Введите названия продуктов через запятую</b>\n\n"
            "Например: <i>гречка, куриная грудка, огурец</i>",
            parse_mode="HTML"
        )
        await state.set_state(FoodStates.waiting_for_food_list)
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Ошибка в manual_food_input: {e}\n{traceback.format_exc()}")
        await callback.answer("❌ Произошла ошибка")

@router.message(FoodStates.waiting_for_food_list)
async def process_food_list(message: Message, state: FSMContext):
    """Обрабатывает список продуктов, введённый вручную."""
    try:
        text = message.text.strip()
        # Разделяем по запятой и очищаем
        food_names = [name.strip() for name in text.split(',') if name.strip()]

        if not food_names:
            await message.answer("❌ Список продуктов пуст. Попробуйте ещё раз:")
            return

        await _start_food_input(message, state, food_names)
        await message.answer(f"✅ Добавлено {len(food_names)} продуктов. Вы можете изменить вес с помощью кнопок.")

    except Exception as e:
        logger.error(f"❌ Ошибка в process_food_list: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Произошла ошибка при обработке списка. Попробуйте ещё раз.")

@router.message(FoodStates.waiting_for_weight)
async def process_weight_input(message: Message, state: FSMContext):
    """Обрабатывает ввод веса продукта вручную."""
    try:
        # Пытаемся распарсить вес
        text = message.text.strip().replace(',', '.')
        # Ищем число в тексте
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if not match:
            await message.answer("❌ Пожалуйста, введите число (вес в граммах).")
            return

        weight = float(match.group(1))
        if weight <= 0:
            await message.answer("❌ Вес должен быть положительным числом.")
            return

        # Получаем данные из состояния
        data = await state.get_data()
        selected_foods = data.get('selected_foods', [])
        current_index = data.get('current_food_index', 0)

        if current_index >= len(selected_foods):
            await state.set_state(FoodStates.editing)
            await message.answer("❌ Ошибка: продукт не найден.")
            return

        # Обновляем вес
        food = selected_foods[current_index]
        food['weight'] = weight

        # Пересчитываем КБЖУ
        nutrients = _calculate_nutrients(food, weight)
        food['calories'] = nutrients['calories']
        food['protein'] = nutrients['protein']
        food['fat'] = nutrients['fat']
        food['carbs'] = nutrients['carbs']

        selected_foods[current_index] = food
        await state.update_data(selected_foods=selected_foods)

        # Обновляем карточку продукта
        totals_msg_id = data.get('totals_msg_id')
        product_msg_ids = data.get('product_msg_ids', [])

        if current_index < len(product_msg_ids):
            try:
                await message.bot.delete_message(message.chat.id, product_msg_ids[current_index])
            except:
                pass

            # Отправляем новую карточку
            new_msg_id = await _send_product_card(
                message.chat.id,
                message.bot,
                current_index,
                food,
                totals_msg_id
            )
            product_msg_ids[current_index] = new_msg_id
            await state.update_data(product_msg_ids=product_msg_ids)

        # Обновляем итоги
        await _update_totals_message(
            message.chat.id,
            totals_msg_id,
            message.bot,
            selected_foods,
            data.get('meal_type', 'snack')
        )

        # Переходим к следующему продукту или завершаем
        if current_index + 1 < len(selected_foods):
            # Запрашиваем вес для следующего продукта
            next_food = selected_foods[current_index + 1]
            await state.update_data(current_food_index=current_index + 1)
            await message.answer(f"✏️ Введите вес для <b>{next_food['name']}</b> (в граммах):", parse_mode="HTML")
        else:
            # Все веса введены
            await state.set_state(FoodStates.editing)
            await message.answer("✅ Вес всех продуктов введён. Вы можете изменить его с помощью кнопок.")

    except Exception as e:
        logger.error(f"❌ Ошибка в process_weight_input: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Произошла ошибка. Попробуйте ещё раз.")

@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    """Универсальный обработчик отмены."""
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено.")
    await callback.answer()
