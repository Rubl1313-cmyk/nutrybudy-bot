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
from typing import List, Dict, Optional
from datetime import datetime

from services.cloudflare_ai import identify_food_multimodel, identify_food_cascade, transcribe_audio, analyze_food_image
from services.image_enhancer import enhance_food_image, create_multi_scale_images, detect_image_quality
from services.food_api import search_food, get_food_data
from services.translator import translate_dish_name, translate_to_russian, extract_food_items
from services.dish_db import find_matching_dish
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem, User
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

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


async def get_food_data_from_db(name: str) -> Dict:
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
    """Обновляет сообщение с итогами КБЖУ."""
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
        if "message is not modified" in str(e):
            logger.debug("Totals message not modified, skipping")
        else:
            raise e


async def send_product_message(chat_id: int, bot, index: int, food: Dict, totals_msg_id: int) -> int:
    """Отправляет сообщение для одного продукта и возвращает его message_id."""
    weight_str = f"{food['weight']} г" if food['weight'] else "0 г"
    
    # 🔥 Рассчитываем КБЖУ для текущего веса
    multiplier = food['weight'] / 100 if food['weight'] else 0
    calories_str = f"{food['calories']:.0f} ккал" if food['weight'] else "0 ккал"
    protein_str = f"{food['protein']:.1f}г" if food['weight'] else "0г"
    fat_str = f"{food['fat']:.1f}г" if food['weight'] else "0г"
    carbs_str = f"{food['carbs']:.1f}г" if food['weight'] else "0г"
    
    text = (
        f"<b>{index+1}. {food['name']}</b>\n"
        f"⚖️ Вес: {weight_str}\n"
        f"🔥 {calories_str} | 🥩 {protein_str} | 🥑 {fat_str} | 🍚 {carbs_str}"
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
        data = await get_food_data_from_db(name)
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
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")
        ]
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


# ========== ОСНОВНОЙ ОБРАБОТЧИК ФОТО ==========

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото: улучшенное распознавание через мультимодельный JSON."""
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
        
        await message.answer("🔍 Анализирую изображение через AI (мультимодельный режим)...")
        
        # Скачиваем и подготавливаем фото
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        optimized = _prepare_image(file_data)
        
        # ✅ СОХРАНЯЕМ ФОТО В STATE ДЛЯ ПОВТОРНОЙ ОБРАБОТКИ
        await state.update_data(
            pending_photo_bytes=file_data,
            pending_photo_optimized=optimized,
            last_photo_id=message.message_id
        )
        
        # Используем новую мультимодельную функцию
        food_data, used_model = await identify_food_multimodel(optimized)
        
        if food_data and isinstance(food_data, dict):
            # ✅ ИСПРАВЛЕНО: Правильная обработка нового формата ингредиентов
            dish_name_en = food_data.get('dish_name', '')
            ingredients_en = food_data.get('ingredients', [])
            
            logger.info(f"🍽 Распознано моделью {used_model}: блюдо='{dish_name_en}', ингредиенты={ingredients_en}")
            
            # ✅ ИСПРАВЛЕНО: Перевод названия блюда
            dish_name_ru = await translate_dish_name(dish_name_en) if dish_name_en else ""
            
            # ✅ ИСПРАВЛЕНО: Извлекаем names из словарей ингредиентов перед переводом
            ingredients_ru = []
            for ing in ingredients_en:
                if isinstance(ing, dict):
                    # Новый формат: {"name": "...", "type": "...", "estimated_weight_grams": ...}
                    ing_name = ing.get('name', '')
                    if ing_name:
                        translated = await translate_to_russian(ing_name)
                        ingredients_ru.append(translated)
                elif isinstance(ing, str):
                    # Старый формат: просто строка
                    translated = await translate_to_russian(ing)
                    ingredients_ru.append(translated)
            
            logger.info(f"🍽 Переведённые ингредиенты: {ingredients_ru}")
            
            # Сначала проверяем, есть ли блюдо в продуктовой базе по названию
            dish_info = await get_food_data(dish_name_ru) if dish_name_ru else {'base_calories': 0}
            
            if dish_info['base_calories'] > 0:
                # Блюдо найдено в продуктовой базе - предлагаем выбор
                await state.update_data(
                    recognized_dish=dish_name_ru,
                    recognized_ingredients=ingredients_ru,
                    last_photo_id=message.message_id
                )
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Использовать блюдо", callback_data="confirm_dish")],
                    [InlineKeyboardButton(text="🔍 Разбить на ингредиенты", callback_data="reject_dish")]
                ])
                await message.answer(
                    f"🍽 Распознано блюдо: **{dish_name_ru}**.\n"
                    f"Хотите использовать его как готовое блюдо или разбить на ингредиенты?",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                return
            
            # Если не найдено, используем ингредиенты
            if ingredients_ru:
                await start_food_input(message, state, ingredients_ru, meal_type="snack")
                await state.update_data(last_photo_id=message.message_id)
                return
            else:
                # Нет ни названия, ни ингредиентов - предлагаем ручной ввод
                await message.answer(
                    "❌ Не удалось распознать состав блюда.\n"
                    "Пожалуйста, введите продукты вручную:",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="food_manual")],
                        [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
                    ])
                )
                await state.update_data(last_photo_id=message.message_id)
                return
        
        # Если JSON не получен, пробуем fallback на analyze_food_image
        logger.info("Falling back to analyze_food_image for ingredients")
        description = await analyze_food_image(optimized)
        if description:
            ingredients_en = await extract_food_items(description)
            ingredients_ru = [await translate_to_russian(ing) for ing in ingredients_en]
            if ingredients_ru:
                await start_food_input(message, state, ingredients_ru, meal_type="snack")
                await state.update_data(last_photo_id=message.message_id)
                return
        
        # Полный провал
        await message.answer(
            "❌ Не удалось распознать фото. Попробуйте:\n"
            "• Отправить более чёткое фото\n"
            "• Ввести продукты вручную",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="food_manual")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")]
            ])
        )
        await state.update_data(last_photo_id=message.message_id)
        
    except Exception as e:
        logger.error(f"❌ Photo error: {e}\n{traceback.format_exc()}")
        await message.answer("❌ Ошибка при обработке фото. Попробуйте позже.")
        await state.clear()

async def _analyze_ai_response(ai_ Dict) -> Dict:
    """
    Обрабатывает ответ от AI, улучшает оценки весов и сопоставляет с базой.
    """
    if not ai_data or not isinstance(ai_data, dict):
        return {"error": "Invalid AI response"}
    
    result = {
        "dish_name": ai_data.get("dish_name", "Неизвестное блюдо"),
        "confidence": ai_data.get("confidence", 0.5),
        "ingredients": [],
        "total_calories": 0,
        "total_protein": 0,
        "total_fat": 0,
        "total_carbs": 0,
        "cooking_method": ai_data.get("cooking_method", ""),
        "portion_size": ai_data.get("portion_size", "medium")
    }
    
    # Стандартные веса порций для калибровки
    STANDARD_PORTIONS = {
        "small": {"total": 200, "main": 100, "side": 70, "sauce": 30},
        "medium": {"total": 350, "main": 150, "side": 150, "sauce": 50},
        "large": {"total": 500, "main": 200, "side": 250, "sauce": 50}
    }
    
    portion_size = ai_data.get("portion_size", "medium")
    portion_std = STANDARD_PORTIONS.get(portion_size, STANDARD_PORTIONS["medium"])
    
    ingredients = ai_data.get("ingredients", [])
    
    # 🔥 Калибровка весов
    total_estimated_weight = sum(
        ing.get("estimated_weight_grams", 0) 
        for ing in ingredients
    )
    
    # Если AI не указал веса или они нереалистичны
    if total_estimated_weight < 100 or total_estimated_weight > 1500:
        logger.info(f"⚖️ Recalibrating weights: {total_estimated_weight}g → {portion_std['total']}g")
        ingredients = _redistribute_weights(ingredients, portion_std)
    
    # 🔥 Сопоставление с базой продуктов и расчёт КБЖУ
    for ing in ingredients:
        product_data = await _match_with_database(ing["name"])
        
        weight = ing.get("estimated_weight_grams", 100)
        
        multiplier = weight / 100
        calories = product_data.get("calories", 0) * multiplier
        protein = product_data.get("protein", 0) * multiplier
        fat = product_data.get("fat", 0) * multiplier
        carbs = product_data.get("carbs", 0) * multiplier
        
        result["ingredients"].append({
            "name": product_data.get("name", ing["name"]),
            "type": ing.get("type", "side"),
            "weight": weight,
            "calories": round(calories, 1),
            "protein": round(protein, 1),
            "fat": round(fat, 1),
            "carbs": round(carbs, 1),
            "confidence": ing.get("confidence", 0.7),
            "ai_name": ing["name"]
        })
        
        result["total_calories"] += calories
        result["total_protein"] += protein
        result["total_fat"] += fat
        result["total_carbs"] += carbs
    
    return result


def _redistribute_weights(ingredients: List[Dict], portion_std: Dict) -> List[Dict]:
    """Перераспределяет веса ингредиентов по стандарту порции."""
    if not ingredients:
        return ingredients
    
    # Группируем по типам
    by_type = {"main": [], "side": [], "garnish": [], "sauce": []}
    for ing in ingredients:
        ing_type = ing.get("type", "side")
        by_type.get(ing_type, by_type["side"]).append(ing)
    
    # Распределяем веса
    for ing_type, items in by_type.items():
        if not items:
            continue
        target_weight = portion_std.get(ing_type, portion_std["side"])
        weight_per_item = target_weight / len(items)
        for item in items:
            item["estimated_weight_grams"] = int(weight_per_item)
    
    return ingredients


async def _match_with_database(product_name: str) -> Dict:
    """Ищет продукт в базе и возвращает лучшие совпадения."""
    results = await search_food(product_name)
    if results:
        return {
            "name": results[0].get("name", product_name),
            "calories": results[0].get("calories", 0),
            "protein": results[0].get("protein", 0),
            "fat": results[0].get("fat", 0),
            "carbs": results[0].get("carbs", 0)
        }
    
    # Если не найдено, возвращаем заглушку
    return {
        "name": product_name,
        "calories": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0
    }


async def _show_food_confirmation(message: Message, state: FSMContext, analyzed: Dict):
    """Показывает распознанное блюдо с возможностью редактирования."""
    
    text = f"🍽 <b>Распознано: {analyzed['dish_name']}</b>\n"
    text += f"🔥 ~{analyzed['total_calories']:.0f} ккал\n"
    text += f"🥩 {analyzed['total_protein']:.1f}г | 🥑 {analyzed['total_fat']:.1f}г | 🍚 {analyzed['total_carbs']:.1f}г\n\n"
    text += "<b>Ингредиенты:</b>\n"
    
    builder = InlineKeyboardBuilder()
    
    for i, ing in enumerate(analyzed['ingredients']):
        text += f"• {ing['name']}: {ing['weight']}г — {ing['calories']:.0f} ккал\n"
        builder.button(
            text=f"✏️ {ing['name']} ({ing['weight']}г)",
            callback_data=f"edit_ing_{i}_{ing['weight']}"
        )
    
    builder.button(text="✅ Всё верно", callback_data="confirm_photo_meal")
    builder.button(text="❌ Перераспознать", callback_data="retry_photo")
    builder.button(text="📝 Ввести вручную", callback_data="manual_food_entry")
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


# ========== ОБРАБОТЧИКИ РЕДАКТИРОВАНИЯ ИНГРЕДИЕНТОВ ==========

@router.callback_query(F.data.startswith("edit_ing_"))
async def edit_ingredient_callback(callback: CallbackQuery, state: FSMContext):
    """Редактирование веса ингредиента."""
    data = callback.data.split("_")
    idx = int(data[2])
    current_weight = int(data[3])
    
    await state.update_data(editing_index=idx, editing_weight=current_weight)
    
    builder = InlineKeyboardBuilder()
    for weight in [50, 100, 150, 200, 250, 300]:
        builder.button(text=f"{weight}г", callback_data=f"set_weight_{idx}_{weight}")
    builder.adjust(3)
    builder.button(text="↩️ Назад", callback_data="back_to_confirmation")
    
    await callback.message.edit_text(
        f"✏️ Выберите вес для ингредиента #{idx+1}:\n"
        f"Текущий: {current_weight}г",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_weight_"))
async def set_weight_callback(callback: CallbackQuery, state: FSMContext):
    """Установка нового веса ингредиента."""
    data = callback.data.split("_")
    idx = int(data[2])
    new_weight = int(data[3])
    
    state_data = await state.get_data()
    ingredients = state_data.get('recognized_ingredients', [])
    
    if idx < len(ingredients):
        # Пересчитываем КБЖУ для нового веса
        ing = ingredients[idx]
        old_weight = ing['weight']
        multiplier = new_weight / old_weight if old_weight > 0 else 1
        
        ing['weight'] = new_weight
        ing['calories'] = round(ing['calories'] * multiplier, 1)
        ing['protein'] = round(ing['protein'] * multiplier, 1)
        ing['fat'] = round(ing['fat'] * multiplier, 1)
        ing['carbs'] = round(ing['carbs'] * multiplier, 1)
        
        ingredients[idx] = ing
        
        # Пересчитываем итоги
        total_cal = sum(i['calories'] for i in ingredients)
        total_prot = sum(i['protein'] for i in ingredients)
        total_fat = sum(i['fat'] for i in ingredients)
        total_carbs = sum(i['carbs'] for i in ingredients)
        
        await state.update_data(
            recognized_ingredients=ingredients,
            total_calories=total_cal,
            total_protein=total_prot,
            total_fat=total_fat,
            total_carbs=total_carbs
        )
        
        await callback.message.edit_text(f"✅ Вес изменён на {new_weight}г")
        await asyncio.sleep(0.5)
        await _show_food_confirmation(callback.message, state, state_data)
    
    await callback.answer()


@router.callback_query(F.data == "back_to_confirmation")
async def back_to_confirmation_callback(callback: CallbackQuery, state: FSMContext):
    """Возврат к подтверждению."""
    state_data = await state.get_data()
    analyzed = {
        'dish_name': state_data.get('recognized_dish', 'Блюдо'),
        'ingredients': state_data.get('recognized_ingredients', []),
        'total_calories': state_data.get('total_calories', 0),
        'total_protein': state_data.get('total_protein', 0),
        'total_fat': state_data.get('total_fat', 0),
        'total_carbs': state_data.get('total_carbs', 0)
    }
    await _show_food_confirmation(callback.message, state, analyzed)
    await callback.answer()


# ========== ОБРАБОТЧИКИ ПОДТВЕРЖДЕНИЯ БЛЮДА ==========

async def safe_answer_callback(callback: CallbackQuery):
    """Безопасный вызов callback.answer с обработкой ошибок."""
    try:
        await callback.answer()
    except TelegramBadRequest as e:
        logger.warning(f"Failed to answer callback: {e}")


async def safe_delete_message(message: Message):
    """Безопасное удаление сообщения с обработкой ошибок."""
    try:
        await message.delete()
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            logger.debug("Message already deleted, skipping")
        else:
            logger.warning(f"Failed to delete message: {e}")


@router.callback_query(F.data == "confirm_photo_meal")
async def confirm_photo_meal_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение распознанного блюда."""
    logger.info(f"✅ confirm_photo_meal_callback вызван")
    
    data = await state.get_data()
    ingredients = data.get('recognized_ingredients', [])
    
    if not ingredients:
        await callback.answer("❌ Нет данных", show_alert=True)
        return
    
    user_id = callback.from_user.id
    meal_type = data.get('meal_type', 'snack')
    dish_name = data.get('recognized_dish', 'Распознанное блюдо')
    
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            await callback.message.answer("❌ Пользователь не найден.")
            await state.clear()
            return
        
        total_cal = sum(f['calories'] for f in ingredients)
        total_prot = sum(f['protein'] for f in ingredients)
        total_fat = sum(f['fat'] for f in ingredients)
        total_carbs = sum(f['carbs'] for f in ingredients)
        
        meal = Meal(
            user_id=user.id,
            meal_type=meal_type,
            datetime=datetime.now(),
            total_calories=total_cal,
            total_protein=total_prot,
            total_fat=total_fat,
            total_carbs=total_carbs,
            ai_description=dish_name,
            photo_url=None
        )
        session.add(meal)
        await session.flush()
        
        for f in ingredients:
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
    lines.append(f"🍽 <b>{dish_name}</b>")
    for f in ingredients:
        lines.append(f"• {f['name']}: {f['weight']}г — {f['calories']:.0f} ккал")
    lines.append(f"\n🔥 Всего: {total_cal:.0f} ккал")
    lines.append(f"🥩 {total_prot:.1f}г | 🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г")
    
    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "retry_photo")
async def retry_photo_callback(callback: CallbackQuery, state: FSMContext):
    """
    ✅ ПОВТОРНОЕ РАСПОЗНАВАНИЕ ФОТО
    Теперь реально перезапускает процесс распознавания
    """
    logger.info(f"🔄 retry_photo_callback вызван")
    
    data = await state.get_data()
    photo_bytes = data.get('pending_photo_bytes')
    photo_optimized = data.get('pending_photo_optimized')
    
    if not photo_bytes and not photo_optimized:
        await callback.answer("❌ Фото не найдено. Отправьте фото заново.", show_alert=True)
        return
    
    # Отвечаем на callback
    await callback.answer("🔄 Перераспознаю...")
    
    # Редактируем сообщение
    await callback.message.edit_text("🔄 Повторный анализ изображения...")
    
    # Используем сохранённое фото
    optimized = photo_optimized if photo_optimized else _prepare_image(photo_bytes)
    
    try:
        # Повторный вызов распознавания
        cascade_result = await identify_food_cascade(optimized)
        
        if cascade_result.get('data'):
            food_data = cascade_result['data']
            analyzed = await _analyze_ai_response(food_data)
            
            await state.update_data(
                recognized_dish=analyzed["dish_name"],
                recognized_ingredients=analyzed["ingredients"],
                total_calories=analyzed["total_calories"],
                total_protein=analyzed["total_protein"],
                total_fat=analyzed["total_fat"],
                total_carbs=analyzed["total_carbs"],
                cascade_confidence=cascade_result.get('confidence', 0)
            )
            
            await _show_food_confirmation(callback.message, state, analyzed)
            return
        
        # Если снова не удалось
        await callback.message.edit_text(
            "❌ Не удалось распознать повторно.\n"
            "Попробуйте отправить другое фото или ввести вручную:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="food_manual")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")]
            ])
        )
        
    except Exception as e:
        logger.error(f"❌ Retry photo error: {e}\n{traceback.format_exc()}")
        await callback.message.edit_text("❌ Ошибка при повторном распознавании.")
        await state.clear()


@router.callback_query(F.data == "manual_food_entry")
async def manual_food_callback(callback: CallbackQuery, state: FSMContext):
    """Переход к ручному вводу."""
    await state.clear()
    from handlers.food import cmd_log_food
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()


# ========== ОСТАЛЬНЫЕ ОБРАБОТЧИКИ (без изменений) ==========

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
    action = parts[1]
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
    
    weight_str = f"{food['weight']} г" if food['weight'] else "0 г"
    calories_str = f"{food['calories']:.0f} ккал" if food['weight'] else "0 ккал"
    protein_str = f"{food['protein']:.1f}г" if food['weight'] else "0г"
    fat_str = f"{food['fat']:.1f}г" if food['weight'] else "0г"
    carbs_str = f"{food['carbs']:.1f}г" if food['weight'] else "0г"
    
    text = (
        f"<b>{idx+1}. {food['name']}</b>\n"
        f"⚖️ Вес: {weight_str}\n"
        f"🔥 {calories_str} | 🥩 {protein_str} | 🥑 {fat_str} | 🍚 {carbs_str}"
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
    await safe_answer_callback(callback)
    await callback.message.edit_text(
        "➕ Добавление продукта\nВведите название продукта:"
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
        f"➕ Добавление продукта: <b>{name}</b>\nВведите вес в граммах (или /skip для пропуска):",
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
            if weight <= 0 or weight > 10000:
                raise ValueError
        except (ValueError, AttributeError):
            await message.answer("❌ Введите число от 1 до 10000 г")
            return
    
    food_data = await get_food_data_from_db(name)
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
    logger.info(f"✅ confirm_meal_callback вызван")
    
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    totals_msg_id = data.get('totals_msg_id')
    product_msg_ids = data.get('product_msg_ids', [])
    
    if not any(f['weight'] for f in selected_foods):
        await safe_answer_callback(callback)
        await callback.message.answer("❌ Укажите вес хотя бы одного продукта")
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
            await safe_answer_callback(callback)
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
    
    await state.update_data(last_photo_id=None)
    
    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await state.clear()
    await safe_answer_callback(callback)


@router.callback_query(F.data == "cancel_meal")
async def cancel_meal_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода приёма пищи."""
    logger.info(f"❌ cancel_meal_callback вызван")
    
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
    
    await state.update_data(last_photo_id=None)
    
    await callback.message.answer("❌ Ввод отменён.")
    await state.clear()
    await safe_answer_callback(callback)


@router.callback_query(F.data == "action_cancel")
async def action_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена действия."""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Действие отменено.")
    await callback.answer()


@router.callback_query(F.data == "food_manual")
async def food_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Переход к ручному вводу продуктов."""
    await state.clear()
    from handlers.food import cmd_log_food
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()
