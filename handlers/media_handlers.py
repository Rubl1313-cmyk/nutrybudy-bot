"""
Обработчики мультимедиа: фото (распознавание еды) и голос.
Реализован интерфейс с отдельными сообщениями для каждого продукта.
Добавлена публичная функция start_food_input для использования из других модулей.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
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

async def recognize_food_from_photo(message: Message) -> List[str]:
    """Распознаёт продукты на фото и возвращает список названий на русском."""
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

    await bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

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
    action = parts[1]  # inc, dec, set, del
    idx = int(parts[2])
    value = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else None

    if idx >= len(selected_foods):
        await callback.answer("❌ Ошибка индекса", show_alert=True)
        return

    food = selected_foods[idx]

    if action == "del":
        del selected_foods[idx]
        try:
            await callback.bot.delete_message(callback.message.chat.id, product_msg_ids[idx])
        except:
            pass
        del product_msg_ids[idx]
        await state.update_data(selected_foods=selected_foods, product_msg_ids=product_msg_ids)
        await update_totals_message(callback.message.chat.id, totals_msg_id, callback.bot, selected_foods)
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
    if new_weight > 0:
        multiplier = new_weight / 100
        food['calories'] = food['base_calories'] * multiplier
        food['protein'] = food['base_protein'] * multiplier
        food['fat'] = food['base_fat'] * multiplier
        food['carbs'] = food['base_carbs'] * multiplier
    else:
        food['calories'] = 0
        food['protein'] = 0
        food['fat'] = 0
        food['carbs'] = 0

    selected_foods[idx] = food
    await state.update_data(selected_foods=selected_foods)

    # Обновляем сообщение продукта
    weight_str = f"{food['weight']} г" if food['weight'] else "0 г"
    calories_str = f"{food['calories']:.0f} ккал" if food['weight'] else "0 ккал"
    text = (
        f"<b>{idx+1}. {food['name']}</b>\n"
        f"Вес: {weight_str} — {calories_str}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➖10", callback_data=f"weight_dec_{idx}_10_{totals_msg_id}"),
        InlineKeyboardButton(text="➕10", callback_data=f"weight_inc_{idx}_10_{totals_msg_id}"),
        InlineKeyboardButton(text="50", callback_data=f"weight_set_{idx}_50_{totals_msg_id}"),
        InlineKeyboardButton(text="100", callback_data=f"weight_set_{idx}_100_{totals_msg_id}"),
        InlineKeyboardButton(text="200", callback_data=f"weight_set_{idx}_200_{totals_msg_id}"),
        InlineKeyboardButton(text="❌", callback_data=f"weight_del_{idx}_{totals_msg_id}")
    ]])

    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Edit error: {e}")

    await update_totals_message(callback.message.chat.id, totals_msg_id, callback.bot, selected_foods)
    await callback.answer()

@router.callback_query(F.data == "add_food")
async def add_food_callback(callback: CallbackQuery, state: FSMContext):
    """Начало добавления нового продукта."""
    await callback.message.edit_text(
        "➕ Добавление продукта\n\nВведите название продукта:"
    )
    await state.set_state(FoodStates.adding_name)
    await callback.answer()

@router.message(FoodStates.adding_name, F.text)
async def process_add_name(message: Message, state: FSMContext):
    """Обработка ввода названия нового продукта."""
    name = message.text.strip()
    if not name:
        await message.answer("❌ Название не может быть пустым.")
        return
    await state.update_data(new_food_name=name)
    await message.answer(
        f"➕ Добавление продукта: <b>{name}</b>\n\nВведите вес в граммах (или /skip для пропуска):",
        parse_mode="HTML"
    )
    await state.set_state(FoodStates.adding_weight)

@router.message(FoodStates.adding_weight, F.text)
async def process_add_weight(message: Message, state: FSMContext):
    """Обработка ввода веса нового продукта и добавление его в список."""
    data = await state.get_data()
    name = data.get('new_food_name')
    text = message.text.strip().lower()

    if text == "/skip":
        weight = 0
    else:
        try:
            match = re.search(r'\d+([.,]\d+)?', message.text)
            weight = float(match.group(0).replace(',', '.')) if match else float(message.text.replace(',', '.'))
            if weight <= 0 or weight > 10000:
                raise ValueError
        except (ValueError, AttributeError):
            await message.answer("❌ Введите число от 1 до 10000 г")
            return

    food_data = await get_food_data(name)

    multiplier = weight / 100 if weight > 0 else 0
    new_food = {
        **food_data,
        'weight': weight,
        'calories': food_data['base_calories'] * multiplier,
        'protein': food_data['base_protein'] * multiplier,
        'fat': food_data['base_fat'] * multiplier,
        'carbs': food_data['base_carbs'] * multiplier
    }

    selected_foods = data.get('selected_foods', [])
    product_msg_ids = data.get('product_msg_ids', [])
    totals_msg_id = data.get('totals_msg_id')

    idx = len(selected_foods)
    selected_foods.append(new_food)

    new_msg_id = await send_product_message(
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

    await update_totals_message(message.chat.id, totals_msg_id, message.bot, selected_foods)
    await message.delete()
    await message.answer("✅ Продукт добавлен.")

@router.callback_query(F.data == "confirm_meal")
async def confirm_meal_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение приёма пищи."""
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    totals_msg_id = data.get('totals_msg_id')
    product_msg_ids = data.get('product_msg_ids', [])

    if not any(f['weight'] for f in selected_foods):
        await callback.answer("❌ Укажите вес хотя бы одного продукта", show_alert=True)
        return

    user_id = callback.from_user.id
    meal_type = data.get('meal_type', 'snack')
    ai_description = data.get('ai_description', '')

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await callback.message.answer("❌ Пользователь не найден. Сначала настройте профиль.")
            await state.clear()
            return

        total_cal = sum(f['calories'] for f in selected_foods)
        total_prot = sum(f['protein'] for f in selected_foods)
        total_fat = sum(f['fat'] for f in selected_foods)
        total_carbs = sum(f['carbs'] for f in selected_foods)

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
            if f['weight']:
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

    chat_id = callback.message.chat.id
    for msg_id in product_msg_ids:
        try:
            await callback.bot.delete_message(chat_id, msg_id)
        except:
            pass
    try:
        await callback.bot.delete_message(chat_id, totals_msg_id)
    except:
        pass

    lines = [f"🍽️ Записан приём пищи ({meal_type}):"]
    for f in selected_foods:
        if f['weight']:
            lines.append(f"• {f['name']}: {f['weight']}г — {f['calories']:.0f} ккал")
    lines.append(f"\n🔥 Всего: {total_cal:.0f} ккал")
    lines.append(f"🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г")

    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_meal")
async def cancel_meal_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода и удаление всех сообщений."""
    data = await state.get_data()
    totals_msg_id = data.get('totals_msg_id')
    product_msg_ids = data.get('product_msg_ids', [])
    chat_id = callback.message.chat.id

    for msg_id in product_msg_ids:
        try:
            await callback.bot.delete_message(chat_id, msg_id)
        except:
            pass
    try:
        await callback.bot.delete_message(chat_id, totals_msg_id)
    except:
        pass

    await callback.message.answer("❌ Ввод отменён.")
    await state.clear()
    await callback.answer()

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
        from handlers.ai_assistant import process_ai_query
        await process_ai_query(message, state, text)
    except Exception as e:
        logger.error(f"Voice error: {e}")
        await message.answer("❌ Ошибка распознавания.")
