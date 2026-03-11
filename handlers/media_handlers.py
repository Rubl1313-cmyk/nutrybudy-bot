"""
🔧 ИСПРАВЛЕННЫЙ обработчик мультимедиа с правильной логикой
✅ Использует dish_name для поиска готового блюда, не ингредиенты
✅ Ингредиенты используются ТОЛЬКО если блюдо не найдено
✅ Никогда не выводит ингредиент как название блюда
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import traceback
import re
import asyncio
import json
import math
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime
from PIL import Image
import io

from services.cloudflare_ai import identify_food_cascade
from services.food_api import LOCAL_FOOD_DB, get_product_variants
from services.translator import translate_smart_dish_name, translate_to_russian
from services.dish_db import COMPOSITE_DISHES, get_dish_ingredients, find_matching_dishes
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem, User, WaterEntry, StepsEntry
from sqlalchemy import select
from utils.ui_templates import (
    ProgressBar, NutritionCard, MealCard, 
    WaterTracker, ActivityCard, StreakCard, StatisticsCard
)
from utils.message_templates import MessageTemplates
from keyboards.improved_keyboards import (
    get_food_recognition_result_keyboard,
    get_daily_goals_keyboard,
    get_time_period_keyboard
)
from aiogram.filters import Command
router = Router()
logger = logging.getLogger(__name__)

# Количество вариантов на одной странице
VARIANTS_PER_PAGE = 8

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def _prepare_image(image_bytes: bytes) -> bytes:
    """
    Улучшенная оптимизация изображения для Cloudflare AI.
    ✅ Добавлено: улучшение контрастности, резкости, оптимизация размера
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Улучшаем качество изображения
        from PIL import ImageEnhance
        
        # Увеличиваем резкость для лучшего распознавания
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        # Увеличиваем контрастность
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        # Легкая коррекция яркости
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        
        # Оптимизируем размер
        original_width, original_height = img.size
        
        # Если изображение слишком маленькое, увеличиваем его
        if max(original_width, original_height) < 512:
            scale_factor = 512 / max(original_width, original_height)
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Если слишком большое, уменьшаем
        elif max(original_width, original_height) > 1024:
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        # Сохраняем с оптимальным качеством
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        logger.warning(f"⚠️ Image prep error: {e}")
        return image_bytes

async def _get_food_data_cached(name: str, return_variants: bool = False) -> Union[Dict, List[Dict]]:
    """
    Получает данные продукта из локальной базы ингредиентов.
    ✅ ИСПРАВЛЕНО: правильная обработка None и проверка валидности данных
    """
    from utils.normalizer import normalize_product_name
    name_lower = name.lower().strip()
    normalized_name = normalize_product_name(name_lower)
    logger.info(f"🔍 _get_food_data_cached: исходное '{name_lower}', нормализованное '{normalized_name}', return_variants={return_variants}")

    variants = get_product_variants(normalized_name)
    logger.info(f"🔍 Найдено вариантов: {len(variants)}")

    if return_variants and len(variants) > 1:
        logger.info(f"🔍 Возвращаем список вариантов: {[v['name'] for v in variants]}")
        return variants

    if variants:
        best = variants[0]
        logger.info(f"🔍 Возвращаем лучший вариант: {best['name']} (cal: {best.get('calories')})")
        return {
            'name': best['name'],
            'key': best.get('key'),
            'base_calories': best.get('calories', 0),
            'base_protein': best.get('protein', 0),
            'base_fat': best.get('fat', 0),
            'base_carbs': best.get('carbs', 0),
            'source': 'local'
        }

    # ✅ ИСПРАВЛЕНО: всегда возвращаем словарь, никогда None
    logger.warning(f"⚠️ Варианты не найдены для '{name}', возвращаем заглушку")
    return {
        'name': name,
        'key': None,
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
            "📊 Поиск в базе блюд...",
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
    """
    Рассчитывает КБЖУ для заданного веса на основе базовых значений.
    ✅ ИСПРАВЛЕНО: правильная обработка None и 0
    """
    if weight is None:
        weight = 0
    
    weight = float(weight) if weight else 0
    
    if weight <= 0:
        return {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
    
    multiplier = weight / 100.0
    return {
        'calories': round(base.get('base_calories', 0) * multiplier, 1),
        'protein': round(base.get('base_protein', 0) * multiplier, 1),
        'fat': round(base.get('base_fat', 0) * multiplier, 1),
        'carbs': round(base.get('base_carbs', 0) * multiplier, 1)
    }

async def _send_product_card(
    chat_id: int,
    bot,
    index: int,
    food: Dict,
    totals_msg_id: int
) -> int:
    """
    Улучшенная карточка продукта с лучшей визуализацией и управлением весом.
    """
    weight = food.get('weight') or 0
    weight = float(weight) if weight else 0
    weight_str = f"{weight} г" if weight else "0 г"
    
    nutrients = _calculate_nutrients(food, weight)
    logger.info(f"📦 Рассчитано для {food['name']}: вес={weight}, ккал={nutrients['calories']}")

    # Определяем эмодзи для типа продукта
    food_name_lower = food['name'].lower()
    if any(word in food_name_lower for word in ['курица', 'мясо', 'рыба', 'говядина', 'свинина', 'индейка']):
        emoji = "🥩"
    elif any(word in food_name_lower for word in ['рис', 'макароны', 'картофель', 'хлеб', 'гречка']):
        emoji = "🍚"
    elif any(word in food_name_lower for word in ['салат', 'овощ', 'помидор', 'огурец', 'капуста', 'морковь']):
        emoji = "🥬"
    elif any(word in food_name_lower for word in ['масло', 'сыр', 'авокадо', 'орех', 'майонез']):
        emoji = "🥑"
    else:
        emoji = "🍽️"

    # Цветовая индикация калорийности
    calories = nutrients['calories']
    if calories <= 50:
        cal_emoji = "🟢"  # Низкая калорийность
    elif calories <= 150:
        cal_emoji = "🟡"  # Средняя калорийность
    else:
        cal_emoji = "🔴"  # Высокая калорийность

    text = (
        f"{emoji} <b>{index+1}. {food['name']}</b>\n"
        f"⚖️ <b>Вес:</b> {weight_str}\n"
        f"{cal_emoji} <b>КБЖУ:</b> {nutrients['calories']:.0f}ккал | "
        f"🥩{nutrients['protein']:.1f}г | 🥑{nutrients['fat']:.1f}г | 🍚{nutrients['carbs']:.1f}г"
    )
    
    # Улучшенные кнопки управления весом
    keyboard = []
    
    # Основные кнопки веса
    weight_buttons = []
    if weight >= 10:
        weight_buttons.append(InlineKeyboardButton(text="➖10г", callback_data=f"weight_dec_{index}_10_{totals_msg_id}"))
    
    weight_buttons.append(InlineKeyboardButton(text="➕10г", callback_data=f"weight_inc_{index}_10_{totals_msg_id}"))
    
    if weight_buttons:
        keyboard.append(weight_buttons)
    
    # Быстрые пресеты веса
    preset_buttons = []
    common_weights = [50, 100, 150, 200]
    for w in common_weights:
        if abs(weight - w) > 5:  # Показываем только если текущий вес сильно отличается
            preset_buttons.append(InlineKeyboardButton(text=f"{w}г", callback_data=f"weight_set_{index}_{w}_{totals_msg_id}"))
    
    if preset_buttons:
        keyboard.append(preset_buttons[:4])  # Максимум 4 пресета
    
    # Кнопка удаления
    keyboard.append([InlineKeyboardButton(text="❌ Удалить", callback_data=f"weight_del_{index}_{totals_msg_id}")])
    
    msg = await bot.send_message(chat_id, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    return msg.message_id

async def _show_final_interface(
    message: Message,
    state: FSMContext,
    selected_foods: List[Dict],
    meal_type: str
):
    """
    Улучшенный финальный интерфейс с детальной информацией о приеме пищи.
    """
    total_cal = 0
    total_prot = 0
    total_fat = 0
    total_carbs = 0
    total_weight = 0
    
    for food in selected_foods:
        nutrients = _calculate_nutrients(food, food.get('weight', 0))
        total_cal += nutrients['calories']
        total_prot += nutrients['protein']
        total_fat += nutrients['fat']
        total_carbs += nutrients['carbs']
        total_weight += food.get('weight', 0)

    # Эмодзи для типа приема пищи
    meal_emojis = {
        'breakfast': '🌅',
        'lunch': '☀️', 
        'dinner': '🌙',
        'snack': '🍎',
        'meal': '🍽️'
    }
    meal_emoji = meal_emojis.get(meal_type.lower(), '🍽️')
    
    # Анализ питательности
    nutrition_analysis = ""
    if total_cal <= 200:
        nutrition_analysis = "💚 Легкий прием пищи"
    elif total_cal <= 500:
        nutrition_analysis = "💛 Умеренный прием пищи" 
    elif total_cal <= 800:
        nutrition_analysis = "🧡 Сытный прием пищи"
    else:
        nutrition_analysis = "❤️ Очень сытный прием пищи"

    # Соотношение БЖУ
    total_macros = total_prot + total_fat + total_carbs
    if total_macros > 0:
        prot_percent = (total_prot / total_macros) * 100
        fat_percent = (total_fat / total_macros) * 100
        carbs_percent = (total_carbs / total_macros) * 100
    else:
        prot_percent = fat_percent = carbs_percent = 0

    totals_text = (
        f"{meal_emoji} <b>Приём пищи ({meal_type.title()})</b>\n"
        f"{'═' * 40}\n"
        f"🔥 <b>Калории:</b> {total_cal:.0f} ккал\n"
        f"🥩 <b>Белки:</b> {total_prot:.1f}г ({prot_percent:.0f}%)\n"
        f"🥑 <b>Жиры:</b> {total_fat:.1f}г ({fat_percent:.0f}%)\n"
        f"🍚 <b>Углеводы:</b> {total_carbs:.1f}г ({carbs_percent:.0f}%)\n"
        f"⚖️ <b>Общий вес:</b> {total_weight:.0f}г\n"
        f"{'═' * 40}\n"
        f"{nutrition_analysis}\n"
        f"📦 <b>Продуктов:</b> {len(selected_foods)}"
    )

    # Улучшенные кнопки управления
    totals_keyboard = []
    
    # Основные действия
    action_buttons = [
        InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_food"),
        InlineKeyboardButton(text="📊 Детали КБЖУ", callback_data="show_nutrition_details")
    ]
    totals_keyboard.append(action_buttons)
    
    # Финальные действия
    final_buttons = [
        InlineKeyboardButton(text="✅ Подтвердить и сохранить", callback_data="confirm_meal"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_meal")
    ]
    totals_keyboard.append(final_buttons)

    totals_msg = await message.answer(totals_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=totals_keyboard), parse_mode="HTML")

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
        meal_type=meal_type,
        total_calories=total_cal,
        total_protein=total_prot,
        total_fat=total_fat,
        total_carbs=total_carbs
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

    keyboard = []
    for variant in page_variants:
        btn_text = f"{variant['name']} ({variant['calories']} ккал)"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"select_variant_{variant['key']}")])

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

    await state.update_data(
        all_variants=variants,
        current_item=current_item,
        meal_type=meal_type,
        current_index=current_index,
        food_items=(await state.get_data()).get('pending_food_items'),
        variants_page=page,
        variants_total_pages=total_pages
    )

async def process_food_items(
    message: Message,
    state: FSMContext,
    food_items: List[Dict],
    meal_type: str,
    start_index: int = 0,
    skip_dish_check: bool = False
):
    """
    Обрабатывает список food_items последовательно.
    Сохраняет в selected_foods: name, weight и базовые КБЖУ на 100 г.
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

    if not skip_dish_check:
        from services.dish_db import find_matching_dishes
        logger.info(f"🔍 Поиск блюд для '{product_name}'")
        matches = find_matching_dishes(product_name, threshold=0.3)  # Понижаем порог до 0.3
        
        logger.info(f"🔍 Найдено совпадений: {len(matches)}")
        for match in matches:
            logger.info(f"🔍 - {match['name']} (score: {match['score']})")

        if matches:
            await state.update_data(
                pending_food_items=food_items,
                pending_index=start_index,
                pending_meal_type=meal_type,
                pending_weight=current_item.get('weight', 100),
                selected_foods=selected_foods
            )
            await _show_dish_selection_for_product(message, state, matches, current_item, meal_type)
            return

    # Ищем ингредиенты в локальной базе
    food_data = await _get_food_data_cached(product_name, return_variants=True)

    # ✅ ИСПРАВЛЕНО: правильная проверка на неизвестный продукт
    # food_data может быть списком или словарем
    if isinstance(food_data, dict) and food_data.get('source') == 'unknown':
        logger.warning(f"⚠️ Product '{product_name}' not found in database")
        # Создаем заглушку и переходим к следующему продукту
        selected_food = {
            'name': product_name,
            'weight': current_item.get('weight', 100),
            'base_calories': 0,
            'base_protein': 0,
            'base_fat': 0,
            'base_carbs': 0,
            'source': 'unknown',
            'ai_confidence': current_item.get('ai_confidence', 0.5)
        }
        selected_foods.append(selected_food)
        await state.update_data(selected_foods=selected_foods)
        await process_food_items(message, state, food_items, meal_type, start_index + 1, skip_dish_check)
        return
    elif isinstance(food_data, list) and len(food_data) == 1 and food_data[0].get('source') == 'unknown':
        logger.warning(f"⚠️ Product '{product_name}' not found in database")
        # Создаем заглушку и переходим к следующему продукту
        selected_food = {
            'name': product_name,
            'weight': current_item.get('weight', 100),
            'base_calories': 0,
            'base_protein': 0,
            'base_fat': 0,
            'base_carbs': 0,
            'source': 'unknown',
            'ai_confidence': current_item.get('ai_confidence', 0.5)
        }
        selected_foods.append(selected_food)
        await state.update_data(selected_foods=selected_foods)
        await process_food_items(message, state, food_items, meal_type, start_index + 1, skip_dish_check)
        return

    # Несколько вариантов – показываем выбор
    if isinstance(food_data, list) and len(food_data) > 1:
        total_pages = (len(food_data) + VARIANTS_PER_PAGE - 1) // VARIANTS_PER_PAGE
        await state.update_data(
            all_variants=food_data,
            current_item=current_item,
            meal_type=meal_type,
            current_index=start_index,
            pending_food_items=food_items,
            pending_weight=current_item.get('weight', 100),
            selected_foods=selected_foods,
            variants_page=0,
            variants_total_pages=total_pages
        )
        await _show_variants_page(
            message, state, food_data, current_item, meal_type,
            start_index, page=0, total_pages=total_pages
        )
        return

    # Единственный вариант (словарь)
    if isinstance(food_data, dict):
        selected_food = {
            'name': food_data['name'],
            'weight': current_item.get('weight', 100),
            'base_calories': food_data.get('base_calories', 0),
            'base_protein': food_data.get('base_protein', 0),
            'base_fat': food_data.get('base_fat', 0),
            'base_carbs': food_data.get('base_carbs', 0),
            'source': food_data.get('source', 'unknown'),
            'ai_confidence': current_item.get('ai_confidence', 0.5)
        }
    elif isinstance(food_data, list) and len(food_data) == 0:
        # Если это пустой список – заглушка и переходим к следующему
        logger.warning(f"⚠️ Варианты не найдены для '{product_name}', возвращаем заглушку")
        selected_food = {
            'name': product_name,
            'weight': current_item.get('weight', 100),
            'base_calories': 0,
            'base_protein': 0,
            'base_fat': 0,
            'base_carbs': 0,
            'source': 'unknown',
            'ai_confidence': current_item.get('ai_confidence', 0.5)
        }
    else:
        # Если это другой тип – заглушка
        selected_food = {
            'name': product_name,
            'weight': current_item.get('weight', 100),
            'base_calories': 0,
            'base_protein': 0,
            'base_fat': 0,
            'base_carbs': 0,
            'source': 'unknown',
            'ai_confidence': current_item.get('ai_confidence', 0.5)
        }

    selected_foods.append(selected_food)
    await state.update_data(selected_foods=selected_foods)
    await process_food_items(message, state, food_items, meal_type, start_index + 1, skip_dish_check)

async def _show_dish_selection_for_product(
    message: Message,
    state: FSMContext,
    matches: list,
    current_item: Dict,
    meal_type: str
):
    logger.info(f"🔍 Показываем выбор готового блюда для '{current_item['name']}', найдено совпадений: {len(matches)}")
    
    text = f"🍽 <b>«{current_item['name']}» может быть готовым блюдом</b>\n"
    text += "Найдены похожие блюда в базе:\n"
    
    await state.update_data(dish_matches=matches)
    
    keyboard = []
    for idx, match in enumerate(matches):
        btn_text = f"{match['name']} (совпадение {match['score']*100:.0f}%)"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"select_dish_idx_{idx}")])
    keyboard.append([InlineKeyboardButton(text="❌ Нет, это ингредиент", callback_data="continue_ingredient")])
    
    try:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")
    except TelegramBadRequest:
        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode="HTML")

# ========== ✅ ГЛАВНЫЕ ИСПРАВЛЕНИЯ: Правильная логика распознавания ==========

async def _show_ingredients_from_ai(
    message: Message,
    state: FSMContext,
    dish_name: str,
    ingredients: List[Dict],
    confidence: float,
    model_used: str
):
    """
    ✅ Улучшенное отображение ингредиентов когда готовое блюдо не найдено
    """
    
    logger.info(f"🥗 Showing ingredients for '{dish_name}' (not found in DB)")
    
    # Улучшенная визуализация уверенности
    filled = int(confidence * 10)
    confidence_bar = "🟩" * filled + "⬜" * (10 - filled)
    confidence_emoji = "🎯" if confidence >= 0.8 else "👁️" if confidence >= 0.6 else "🔍"
    
    # Группируем ингредиенты по типам для лучшего отображения
    ingredients_by_type = {}
    for ing in ingredients:
        ing_type = ing.get('type', 'other')
        if ing_type not in ingredients_by_type:
            ingredients_by_type[ing_type] = []
        ingredients_by_type[ing_type].append(ing)
    
    # Эмодзи для типов ингредиентов
    type_emojis = {
        'protein': '🥩',
        'vegetable': '🥬', 
        'carb': '🍚',
        'fat': '🥑',
        'sauce': '🫙',
        'garnish': '🌿',
        'other': '📦'
    }
    
    # Названия типов на русском
    type_names = {
        'protein': 'Белки',
        'vegetable': 'Овощи',
        'carb': 'Углеводы', 
        'fat': 'Жиры',
        'sauce': 'Соусы',
        'garnish': 'Гарниры',
        'other': 'Прочее'
    }
    
    text = (
        f"{confidence_emoji} <b>Распознано ({model_used})</b>\n"
        f"{'═' * 40}\n"
        f"<b>{dish_name}</b>\n"
        f"{confidence_bar} {confidence*100:.0f}% уверенности\n\n"
        f"❗ <i>Это блюдо не найдено в нашей базе готовых блюд.</i>\n"
        f"💡 <i>Но я определил ингредиенты и могу рассчитать калории!</i>\n\n"
        f"<b>🧂 Компоненты ({len(ingredients)}):</b>\n"
    )
    
    # Показываем ингредиенты сгруппированные по типам
    for ing_type, ing_list in ingredients_by_type.items():
        emoji = type_emojis.get(ing_type, '📦')
        name = type_names.get(ing_type, ing_type.title())
        
        text += f"\n{emoji} <b>{name} ({len(ing_list)}):</b>\n"
        for i, ing in enumerate(ing_list, 1):
            ing_name = ing.get('name', 'Неизвестно')
            weight = ing.get('estimated_weight_grams', 100)
            ing_confidence = ing.get('confidence', 0.8)
            
            # Индикатор уверенности для каждого ингредиента
            conf_emoji = "✅" if ing_confidence >= 0.8 else "⚠️" if ing_confidence >= 0.6 else "❓"
            text += f"  {conf_emoji} {ing_name}: ~{weight}г\n"
    
    # Общий вес
    total_weight = sum(ing.get('estimated_weight_grams', 0) for ing in ingredients)
    text += f"\n📏 <b>Общий вес:</b> ~{total_weight}г\n"
    
    text += (
        f"{'═' * 40}\n"
        f"\n💡 <b>Что будет дальше:</b>\n"
        f"• Я найду калории для каждого компонента\n"
        f"• Рассчитаю общую питательную ценность\n"
        f"• Вы сможете скорректировать веса\n"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Использовать ингредиенты", callback_data="confirm_dish_as_is")
    builder.button(text="🔄 Перераспознать", callback_data="retry_photo")
    builder.button(text="📝 Ввести вручную", callback_data="manual_food_entry")
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

async def _show_dish_selection(
    message: Message,
    state: FSMContext,
    matches: list,
    dish_data: Dict,
    model_used: str = None
):
    """
    ✅ Улучшенное отображение найденных готовых блюд с детальной информацией
    """
    
    dish_name = dish_data.get('dish_name', 'Блюдо')
    confidence = dish_data.get('confidence', 0.5)
    ingredients = dish_data.get('ingredients', [])
    meal_type = dish_data.get('meal_type', 'meal')
    cooking_method = dish_data.get('cooking_method', 'cooked')
    portion_size = dish_data.get('portion_size', 'medium')
    
    logger.info(f"🍽️ Found {len(matches)} matching dishes for '{dish_name}'")
    
    # Улучшенная визуализация уверенности с цветами
    filled = int(confidence * 10)
    confidence_bar = "🟩" * filled + "⬜" * (10 - filled)
    confidence_emoji = "🎯" if confidence >= 0.8 else "👁️" if confidence >= 0.6 else "🔍"
    
    # Эмодзи для типа приема пищи
    meal_emoji = {
        'breakfast': '🌅',
        'lunch': '☀️',
        'dinner': '🌙',
        'snack': '🍎'
    }.get(meal_type, '🍽️')
    
    # Эмодзи для способа приготовления
    cooking_emoji = {
        'grilled': '🔥',
        'fried': '🍳',
        'boiled': '🫕',
        'steamed': '💨',
        'baked': '👨‍🍳',
        'raw': '🥗',
        'roasted': '🍖'
    }.get(cooking_method, '🍽️')
    
    text = (
        f"{confidence_emoji} <b>Распознано: {dish_name}</b>\n"
        f"{'═' * 40}\n"
        f"{confidence_bar} {confidence*100:.0f}% уверенности\n"
        f"{meal_emoji} Тип: {meal_type.title()} | {cooking_emoji} {cooking_method.title()}\n"
        f"📏 Порция: {portion_size.title()}\n\n"
        f"✅ <b>Найдены совпадения в базе готовых блюд:</b>\n\n"
    )
    
    # Показываем ингредиенты которые определил AI
    if ingredients:
        text += f"<i>🧂 Определенные ингредиенты:</i>\n"
        for i, ing in enumerate(ingredients[:3], 1):  # Показываем первые 3
            ing_name = ing.get('name', 'Неизвестно')
            ing_weight = ing.get('estimated_weight_grams', 0)
            text += f"  • {ing_name} (~{ing_weight}г)\n"
        if len(ingredients) > 3:
            text += f"  • ... и еще {len(ingredients)-3} компонент(ов)\n"
        text += "\n"
    
    await state.update_data(dish_matches=matches)
    
    builder = InlineKeyboardBuilder()
    
    # Добавляем информативные кнопки для блюд
    for i, match in enumerate(matches):
        match_score = match['score'] * 100
        # Эмодзи для оценки точности
        accuracy_emoji = "🎯" if match_score >= 80 else "👁️" if match_score >= 60 else "🔍"
        
        btn_text = f"{accuracy_emoji} {match['name']} ({match_score:.0f}%)"
        builder.button(text=btn_text, callback_data=f"select_dish_idx_{i}")
    
    builder.adjust(1)
    
    # Дополнительные действия
    builder.row(
        InlineKeyboardButton(text="🔍 Разобрать на ингредиенты", callback_data="use_ingredients_instead"),
        InlineKeyboardButton(text="📝 Ввести вручную", callback_data="manual_food_entry")
    )
    builder.row(InlineKeyboardButton(text="🔄 Перераспознать", callback_data="retry_photo"))
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await state.update_data(recognized_dish=dish_data, mode="photo_selection")

# ========== ОСНОВНОЙ ИСПРАВЛЕННЫЙ ОБРАБОТЧИК ФОТО ==========

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """
    ✅ ПОЛНОСТЬЮ ПЕРЕПИСАННЫЙ ОБРАБОТЧИК ФОТО
    1. Получаем результат AI
    2. ИСПОЛЬЗУЕМ dish_name для поиска готового блюда
    3. Если не найдено - разбираем на ингредиенты
    4. НИКОГДА не используем ингредиенты как название блюд  
    """
    
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

        logger.info(f"🤖 AI raw result: {json.dumps(result, ensure_ascii=False, indent=2)}")

        await _send_progress_update(
            message.bot,
            message.chat.id,
            progress_msg.message_id,
            stage=2,
            progress=70,
            total_stages=5
        )

        # ✅ ИСПРАВЛЕНИЕ 1: Проверяем успех и наличие данных
        if result.get('success') and result.get('data'):
            dish_data = result['data']
            model_used = result.get('model', 'unknown')
            
            # ✅ ИСПРАВЛЕНИЕ 2: Извлекаем dish_name и ingredients ОТДЕЛЬНО
            dish_name_from_ai = dish_data.get('dish_name', '').strip()
            confidence = dish_data.get('confidence', 0.5)
            ingredients_from_ai = dish_data.get('ingredients', [])
            
            logger.info(f"✅ AI determined:")
            logger.info(f"   Dish: '{dish_name_from_ai}'")
            logger.info(f"   Confidence: {confidence:.0%}")
            logger.info(f"   Ingredients count: {len(ingredients_from_ai)}")
            
            # ✅ ИСПРАВЛЕНИЕ 3: Используем умный перевод для dish_name!
            dish_name_ru = await translate_smart_dish_name(dish_name_from_ai) if dish_name_from_ai else "Неизвестное блюдо"
            
            logger.info(f"✅ Smart translated dish name: '{dish_name_from_ai}' → '{dish_name_ru}'")
            
            # ✅ ИСПРАВЛЕНИЕ 4: Переводим ингредиенты (но они НЕ станут названием блюда!)
            ingredients_ru = []
            for ing in ingredients_from_ai:
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
            
            logger.info(f"✅ Translated ingredients: {[ing.get('name') for ing in ingredients_ru]}")
            
            # ✅ ИСПРАВЛЕНИЕ 5: Ищем готовое блюдо ПО НАЗВАНИЮ БЛЮДА, не по ингредиентам!
            await _send_progress_update(
                message.bot,
                message.chat.id,
                progress_msg.message_id,
                stage=3,
                progress=85,
                total_stages=5
            )

            # Ищем готовое блюдо ПО dish_name_ru
            matches = find_matching_dishes(dish_name_ru, threshold=0.5)
            
            if matches:
                logger.info(f"✅ Found {len(matches)} matching dishes for '{dish_name_ru}'")
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
                
                await state.update_data(recognized_dish=dish_data, mode="photo_selection")
                await _show_dish_selection(
                    message, state, matches, 
                    {
                        'dish_name': dish_name_ru,
                        'ingredients': ingredients_ru,
                        'confidence': confidence,
                        'model': model_used
                    }
                )
            else:
                logger.warning(f"⚠️ No matching dishes found for '{dish_name_ru}'")
                # ✅ ИСПРАВЛЕНИЕ 6: Если блюдо не найдено, показываем ингредиенты
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
                
                await state.update_data(recognized_dish=dish_data, mode="photo_recognition")
                await _show_ingredients_from_ai(
                    message, state,
                    dish_name_ru,
                    ingredients_ru,
                    confidence,
                    model_used
                )

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

# ========== ОБРАБОТЧИКИ PAGINATION ==========

@router.callback_query(F.data.startswith("variants_page_"))
async def variants_page_callback(callback: CallbackQuery, state: FSMContext):
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
    parts = callback.data.split("_", 2)  # Разделяем только на 3 части
    if len(parts) < 3:
        await callback.answer("❌ Ошибка", show_alert=True)
        return

    product_key_or_name = parts[2]  # Может быть ключ или название
    data = await state.get_data()

    # Сначала ищем по ключу
    product = None
    if product_key_or_name in LOCAL_FOOD_DB:
        product = LOCAL_FOOD_DB[product_key_or_name]
    else:
        # Если не нашли по ключу, ищем по названию
        for key, value in LOCAL_FOOD_DB.items():
            if value['name'].lower() == product_key_or_name.lower():
                product = value
                product_key_or_name = key  # Сохраняем правильный ключ
                break
    
    if not product:
        logger.error(f"❌ Продукт не найден: {product_key_or_name}")
        await callback.answer("❌ Продукт не найден", show_alert=True)
        return

    weight = data.get('pending_weight', 100)
    meal_type = data.get('pending_meal_type', 'snack')
    food_items = data.get('pending_food_items', [])
    current_index = data.get('pending_index', 0)

    selected_food = {
        'name': product['name'],
        'weight': weight,
        'base_calories': product.get('calories', 0),
        'base_protein': product.get('protein', 0),
        'base_fat': product.get('fat', 0),
        'base_carbs': product.get('carbs', 0),
        'source': 'local',
        'ai_confidence': 0.8
    }

    selected_foods = data.get('selected_foods', [])
    selected_foods.append(selected_food)
    await state.update_data(selected_foods=selected_foods)

    await callback.message.delete()
    await process_food_items(
        callback.message,
        state,
        food_items,
        meal_type,
        current_index + 1
    )
    await callback.answer()

# ========== ОБРАБОТЧИКИ ВЫБОРА БЛЮДА ==========

@router.callback_query(F.data.startswith("select_dish_idx_"))
async def select_dish_by_index_callback(callback: CallbackQuery, state: FSMContext):
    logger.info(f"🔥 Вызван select_dish_by_index_callback с data: {callback.data}")
    try:
        parts = callback.data.split("_")
        idx = int(parts[3])
    except (IndexError, ValueError) as e:
        logger.error(f"🔥 Ошибка парсинга индекса: {e}")
        await callback.answer("❌ Неверный индекс", show_alert=True)
        return
    
    data = await state.get_data()
    matches = data.get('dish_matches')
    if not matches:
        logger.error("🔥 dish_matches нет в состоянии")
        await callback.answer("❌ Данные не найдены", show_alert=True)
        return
    
    if idx >= len(matches):
        logger.error(f"🔥 Индекс {idx} вне диапазона (всего {len(matches)})")
        await callback.answer("❌ Индекс вне диапазона", show_alert=True)
        return
    
    match = matches[idx]
    dish_key = match['dish_key'].strip()
    logger.info(f"🔥 Выбрано блюдо: {match['name']}, ключ: '{dish_key}'")
    
    from services.dish_db import COMPOSITE_DISHES, get_dish_ingredients
    
    normalized_key = dish_key.lower().strip()
    
    if normalized_key not in COMPOSITE_DISHES:
        logger.warning(f"⚠️ Ключ '{normalized_key}' не найден точно, ищем fallback...")
        found_key = None
        for db_key in COMPOSITE_DISHES.keys():
            if db_key.lower() == normalized_key or normalized_key in db_key.lower() or db_key.lower() in normalized_key:
                found_key = db_key
                logger.info(f"✅ Fallback найден: '{found_key}'")
                break
        
        if not found_key:
            logger.error(f"❌ Ключ '{normalized_key}' не найден в COMPOSITE_DISHES.")
            await callback.answer("❌ Блюдо не найдено в базе", show_alert=True)
            return
        
        dish_key = found_key
    
    dish_info = COMPOSITE_DISHES[dish_key]
    logger.info(f"🍽 Найдено блюдо: {dish_info['name']}")
    
    pending_weight = data.get('pending_weight', 300)
    pending_food_items = data.get('pending_food_items', [])
    pending_index = data.get('pending_index', 0)
    meal_type = data.get('pending_meal_type', 'snack')
    selected_foods = data.get('selected_foods', [])
    
    nutrition_per_100 = dish_info.get('nutrition_per_100')
    if nutrition_per_100:
        # Готовое блюдо с собственными КБЖУ
        multiplier = pending_weight / 100.0
        selected_food = {
            'name': dish_info['name'],
            'weight': pending_weight,
            'base_calories': nutrition_per_100.get('calories', 0),
            'base_protein': nutrition_per_100.get('protein', 0),
            'base_fat': nutrition_per_100.get('fat', 0),
            'base_carbs': nutrition_per_100.get('carbs', 0),
            'source': 'composite_dish',
            'dish_key': dish_key
        }
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
    
    # Разбиваем на ингредиенты
    default_weight = dish_info.get('default_weight', 300)
    total_weight = pending_weight if 50 < pending_weight <= 1500 else default_weight
    ingredients_with_weights = get_dish_ingredients(dish_key, total_weight=total_weight)
    food_items = [{'name': ing['name'], 'weight': ing['estimated_weight_grams']} for ing in ingredients_with_weights]
    
    # Безопасная работа со списком
    if pending_food_items is not None and len(pending_food_items) > pending_index:
        pending_food_items.pop(pending_index)
        for i, item in enumerate(food_items):
            pending_food_items.insert(pending_index + i, item)
    else:
        # Если pending_food_items не существует, создаем новый список
        pending_food_items = food_items
    
    await state.update_data(pending_food_items=pending_food_items)
    
    await callback.message.delete()
    
    await process_food_items(
        callback.message,
        state,
        pending_food_items,
        meal_type,
        pending_index
    )
    await callback.answer()

# ========== ОБРАБОТЧИКИ ПОДТВЕРЖДЕНИЯ ==========

@router.callback_query(F.data == "confirm_dish_as_is")
async def confirm_dish_callback(callback: CallbackQuery, state: FSMContext):
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

    # Разворачиваем составные блюда
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

    await state.update_data(selected_foods=[])
    await process_food_items(
        callback.message,
        state,
        expanded_items,
        meal_type=dish_data.get('meal_type', 'snack'),
        skip_dish_check=True
    )

@router.callback_query(F.data == "use_ingredients_instead")
async def use_ingredients_callback(callback: CallbackQuery, state: FSMContext):
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
        meal_type=dish_data.get('meal_type', 'snack'),
        skip_dish_check=True
    )

@router.callback_query(F.data == "continue_ingredient")
async def continue_as_ingredient_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pending_index = data.get('pending_index', 0)
    pending_food_items = data.get('pending_food_items', [])
    current_item = pending_food_items[pending_index] if pending_index < len(pending_food_items) else None
    
    # Безопасность: проверяем что pending_food_items это список
    if not isinstance(pending_food_items, list) or not current_item:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return
    
    await callback.message.delete()
    
    # Ищем ингредиенты для текущего продукта
    product_name = current_item['name']
    logger.info(f"🔄 Ищем ингредиенты для '{product_name}' как ингредиент")
    
    # Ищем в базе ингредиентов
    food_data = await _get_food_data_cached(product_name, return_variants=True)
    
    # Если найдены варианты - показываем выбор
    if isinstance(food_data, list) and len(food_data) > 1:
        total_pages = (len(food_data) + VARIANTS_PER_PAGE - 1) // VARIANTS_PER_PAGE
        await _show_variants_page(
            callback.message,
            state,
            food_data,
            current_item,
            data.get('pending_meal_type', 'snack'),
            pending_index,
            0,
            total_pages
        )
        await callback.answer()
        return
    
    # Если найден один вариант - добавляем его
    if isinstance(food_data, list) and len(food_data) == 1:
        selected_foods = data.get('selected_foods', [])
        selected_food = {
            'name': food_data[0]['name'],
            'weight': current_item.get('weight', 100),
            'base_calories': food_data[0]['calories'],
            'base_protein': food_data[0]['protein'],
            'base_fat': food_data[0]['fat'],
            'base_carbs': food_data[0]['carbs'],
            'source': 'database',
            'key': food_data[0]['key'],
            'ai_confidence': current_item.get('ai_confidence', 0.5)
        }
        selected_foods.append(selected_food)
        await state.update_data(selected_foods=selected_foods)
        
        # Переходим к следующему продукту
        await process_food_items(
            callback.message,
            state,
            pending_food_items,
            data.get('pending_meal_type', 'snack'),
            pending_index + 1,
            skip_dish_check=True
        )
        await callback.answer()
        return
    
    # Если ничего не найдено - создаем заглушку и переходим дальше
    logger.warning(f"⚠️ Ингредиенты для '{product_name}' не найдены, создаем заглушку")
    selected_foods = data.get('selected_foods', [])
    selected_food = {
        'name': product_name,
        'weight': current_item.get('weight', 100),
        'base_calories': 0,
        'base_protein': 0,
        'base_fat': 0,
        'base_carbs': 0,
        'source': 'unknown',
        'ai_confidence': current_item.get('ai_confidence', 0.5)
    }
    selected_foods.append(selected_food)
    await state.update_data(selected_foods=selected_foods)
    
    # Переходим к следующему продукту
    await process_food_items(
        callback.message,
        state,
        pending_food_items,
        data.get('pending_meal_type', 'snack'),
        pending_index + 1,
        skip_dish_check=True
    )
    await callback.answer()

# ========== ОБРАБОТЧИКИ УПРАВЛЕНИЯ ВЕСОМ ==========

@router.callback_query(F.data.startswith("weight_"))
async def weight_callback(callback: CallbackQuery, state: FSMContext):
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
    try:
        idx = int(parts[2])
        value = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else None
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка парсинга", show_alert=True)
        return

    totals_msg_id_from_callback = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else totals_msg_id

    if idx >= len(selected_foods):
        await callback.answer("❌ Ошибка индекса", show_alert=True)
        return

    food = selected_foods[idx]

    if action == "del":
        # ✅ ИСПРАВЛЕНО: правильный порядок удаления э  ементов
        if idx < len(product_msg_ids):
            try:
                await callback.bot.delete_message(callback.message.chat.id, product_msg_ids[idx])
            except Exception as e:
                logger.warning(f"Could not delete product message: {e}")
        
        # Удаляем в правильном порядке
        del product_msg_ids[idx]
        del selected_foods[idx]

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

    current_weight = float(food.get('weight') or 0)

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
    selected_foods[idx] = food
    await state.update_data(selected_foods=selected_foods)

    # Обновляем карточку продукта
    weight_str = f"{new_weight} г" if new_weight else "0 г"
    nutrients = _calculate_nutrients(food, new_weight)
    
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
    total_cal = 0
    total_prot = 0
    total_fat = 0
    total_carbs = 0
    
    for food in selected_foods:
        nutrients = _calculate_nutrients(food, food.get('weight', 0))
        total_cal += nutrients['calories']
        total_prot += nutrients['protein']
        total_fat += nutrients['fat']
        total_carbs += nutrients['carbs']

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
    await callback.answer()
    await callback.message.edit_text(
        "➕ <b>Добавление продукта</b>\nВведите название:",
        parse_mode="HTML"
    )
    await state.set_state(FoodStates.adding_name)

@router.message(FoodStates.adding_name, F.text)
async def process_add_name(message: Message, state: FSMContext):
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

    food_data = await _get_food_data_cached(name, return_variants=False)

    selected_food = {
        'name': food_data['name'],
        'weight': weight,
        'base_calories': food_data.get('base_calories', 0),
        'base_protein': food_data.get('base_protein', 0),
        'base_fat': food_data.get('base_fat', 0),
        'base_carbs': food_data.get('base_carbs', 0),
        'source': food_data.get('source', 'unknown')
    }

    selected_foods = data.get('selected_foods', [])
    product_msg_ids = data.get('product_msg_ids', [])
    totals_msg_id = data.get('totals_msg_id')

    idx = len(selected_foods)
    selected_foods.append(selected_food)

    new_msg_id = await _send_product_card(
        message.chat.id,
        message.bot,
        idx,
        selected_food,
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
    try:
        await callback.answer()
    except TelegramBadRequest:
        pass

@router.callback_query(F.data == "confirm_meal")
async def confirm_meal_callback(callback: CallbackQuery, state: FSMContext):
    """
    ✅ УЛУЧШЕННАЯ версия сохранения в базу данных с детальной информацией
    """
    logger.info(f"✅ confirm_meal_callback: user={callback.from_user.id}")

    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])

    if not selected_foods or not any(f.get('weight', 0) for f in selected_foods):
        await callback.answer("❌ Укажите вес хотя бы одного продукта", show_alert=True)
        return

    user_id = callback.from_user.id
    meal_type = data.get('meal_type', 'snack')
    recognized_dish = data.get('recognized_dish', {})

    async with get_session() as session:
        try:
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                await callback.message.answer("❌ Сначала настройте профиль (/set_profile)")
                await state.clear()
                return

            # Вычисляем итоговые КБЖУ для сохранения
            total_cal = 0
            total_prot = 0
            total_fat = 0
            total_carbs = 0
            total_weight = 0
            
            for food in selected_foods:
                weight = food.get('weight', 0)
                nutrients = _calculate_nutrients(food, weight)
                total_cal += nutrients['calories']
                total_prot += nutrients['protein']
                total_fat += nutrients['fat']
                total_carbs += nutrients['carbs']
                total_weight += weight

            # Создаем улучшенную запись о приеме пищи
            meal = Meal(
                user_id=user.id,
                meal_type=meal_type,
                datetime=datetime.now(),
                total_calories=total_cal,
                total_protein=total_prot,
                total_fat=total_fat,
                total_carbs=total_carbs,
                ai_description=_create_ai_description(recognized_dish, selected_foods),
                photo_url=None  # Можно добавить сохранение фото в будущем
            )
            session.add(meal)
            await session.flush()

            # Сохраняем каждый продукт с детальной информацией
            valid_items_count = 0
            for f in selected_foods:
                weight = f.get('weight') or 0
                weight = float(weight) if weight else 0
                
                if weight > 0:
                    nutrients = _calculate_nutrients(f, weight)
                    item = FoodItem(
                        meal_id=meal.id,
                        name=f['name'],
                        weight=float(weight),
                        calories=nutrients['calories'],
                        protein=nutrients['protein'],
                        fat=nutrients['fat'],
                        carbs=nutrients['carbs'],
                        barcode=f.get('barcode')  # Для будущих сканеров штрих-кодов
                    )
                    session.add(item)
                    valid_items_count += 1

            await session.commit()
            
            logger.info(
                f"💾 Meal saved successfully: user_id={user.id}, "
                f"meal_type={meal_type}, total_cal={total_cal:.0f}, "
                f"items_count={valid_items_count}, total_weight={total_weight:.0f}g"
            )

            # Очистка интерфейса
            chat_id = callback.message.chat.id
            for msg_id in data.get('product_msg_ids', []):
                try:
                    await callback.bot.delete_message(chat_id, msg_id)
                except Exception as e:
                    logger.warning(f"Could not delete message {msg_id}: {e}")

            try:
                await callback.bot.delete_message(chat_id, data.get('totals_msg_id'))
            except Exception as e:
                logger.warning(f"Could not delete totals message: {e}")

            # ✅ УЛУЧШЕННОЕ СООБЩЕНИЕ ОБ УСПЕХЕ
            success_message = _create_success_message(meal_type, total_cal, total_prot, total_fat, total_carbs, valid_items_count)
            await callback.message.answer(success_message, parse_mode="HTML")
            
            # ========== ✅ ДНЕВНОЙ ПРОГРЕСС ==========
            await _show_daily_progress(callback, session, user, meal)
            
        except Exception as e:
            logger.error(f"❌ Error saving meal: {e}", exc_info=True)
            await session.rollback()
            await callback.message.answer("❌ Ошибка при сохранении. Попробуйте еще раз.")
            return

def _create_ai_description(recognized_dish: Dict, selected_foods: List[Dict]) -> str:
    """Создает детальное описание AI для сохранения в базу"""
    description_parts = []
    
    if recognized_dish:
        dish_name = recognized_dish.get('dish_name', '')
        confidence = recognized_dish.get('confidence', 0)
        model = recognized_dish.get('model', 'unknown')
        
        description_parts.append(f"Распознано: {dish_name}")
        description_parts.append(f"Уверенность: {confidence:.0%}")
        description_parts.append(f"Модель: {model}")
        
        ingredients = recognized_dish.get('ingredients', [])
        if ingredients:
            ing_names = [ing.get('name', '') for ing in ingredients[:5]]
            description_parts.append(f"Ингредиенты: {', '.join(ing_names)}")
    
    description_parts.append(f"Продукты: {', '.join([f['name'] for f in selected_foods])}")
    
    return ' | '.join(description_parts)

def _create_success_message(meal_type: str, total_cal: float, total_prot: float, 
                           total_fat: float, total_carbs: float, items_count: int) -> str:
    """Создает красивое сообщение об успехе"""
    
    meal_emojis = {
        'breakfast': '🌅',
        'lunch': '☀️',
        'dinner': '🌙', 
        'snack': '🍎',
        'meal': '🍽️'
    }
    emoji = meal_emojis.get(meal_type.lower(), '🍽️')
    
    return (
        f"{emoji} <b>Приём пищи сохранён!</b>\n"
        f"{'═' * 35}\n"
        f"📊 <b>Питательность:</b>\n"
        f"🔥 {total_cal:.0f} ккал\n"
        f"🥩 {total_prot:.1f}г белков\n"
        f"🥑 {total_fat:.1f}г жиров\n"
        f"🍚 {total_carbs:.1f}г углеводов\n\n"
        f"📦 Сохранено продуктов: {items_count}\n"
        f"✅ Данные добавлены в дневник"
    )

async def _show_daily_progress(callback: CallbackQuery, session, user, meal):
    """Показывает дневной прогресс после сохранения"""
    try:
        # Получаем все приёмы пищи за сегодня
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Получаем приемы пищи
        today_result = await session.execute(
            select(Meal).where(
                (Meal.user_id == user.id) &
                (Meal.datetime >= today_start) &
                (Meal.datetime <= today_end)
            )
        )
        today_meals = today_result.scalars().all()
        
        # Получаем записи о воде за сегодня
        water_result = await session.execute(
            select(WaterEntry).where(
                (WaterEntry.user_id == user.id) &
                (WaterEntry.datetime >= today_start) &
                (WaterEntry.datetime <= today_end)
            )
        )
        today_water = water_result.scalars().all()
        
        # Получаем записи о шагах за сегодня
        steps_result = await session.execute(
            select(StepsEntry).where(
                (StepsEntry.user_id == user.id) &
                (StepsEntry.datetime >= today_start) &
                (StepsEntry.datetime <= today_end)
            )
        )
        today_steps = steps_result.scalars().all()
        
        # Вычисляем дневные итоги
        daily_total_cal = sum(meal.total_calories for meal in today_meals)
        daily_total_prot = sum(meal.total_protein for meal in today_meals)
        daily_total_fat = sum(meal.total_fat for meal in today_meals)
        daily_total_carbs = sum(meal.total_carbs for meal in today_meals)
        daily_total_water = sum(water.amount for water in today_water)
        daily_total_steps = sum(steps.steps_count for steps in today_steps)
        
        # Рассчитываем сожженные калории от шагов
        steps_calories_burned = int(daily_total_steps * 0.04)  # ~0.04 ккал на шаг
        net_calories = daily_total_cal - steps_calories_burned
        
        # Получаем цели пользователя
        goal_cal = user.daily_calorie_goal or 2000
        goal_prot = user.daily_protein_goal or 150
        goal_fat = user.daily_fat_goal or 65
        goal_carbs = user.daily_carbs_goal or 250
        goal_water = user.daily_water_goal or 2000
        goal_steps = user.daily_steps_goal or 10000
        
        # ✅ Красивая карточка прогресса дня
        daily_progress = NutritionCard.create_modern_daily_goal_card(
            net_calories, goal_cal,
            daily_total_prot, goal_prot,
            daily_total_fat, goal_fat,
            daily_total_carbs, goal_carbs
        )
        
        # Добавляем информацию о сожженных калориях
        calories_info = (
            f"🔥 <b>Баланс калорий</b>\n"
            f"{'═' * 35}\n"
            f"🍽️ Потреблено: {daily_total_cal:.0f} ккал\n"
            f"👞 Сожжено: {steps_calories_burned:.0f} ккал ({daily_total_steps:,} шагов)\n"
            f"⚖️ Чистые: {net_calories:.0f} ккал\n"
        )
        
        await callback.message.answer(calories_info, parse_mode="HTML")
        
        await callback.message.answer(daily_progress, parse_mode="HTML")
        
        # ========== 💪 ПРОГРЕСС ПО ВОДЕ ==========
        water_bar = ProgressBar.create_modern_bar(daily_total_water, goal_water, 12, 'gradient')
        water_percentage = (daily_total_water / goal_water * 100) if goal_water > 0 else 0
        
        water_progress = (
            f"💧 <b>Водный баланс</b>\n"
            f"{'═' * 35}\n"
            f"💧 Выпито: {daily_total_water:.0f}мл из {goal_water:.0f}мл\n"
            f"{water_bar} {water_percentage:.0f}%\n"
        )
        
        await callback.message.answer(water_progress, parse_mode="HTML")
        
        # ========== 👞 ПРОГРЕСС ПО ШАГАМ ==========
        steps_bar = ProgressBar.create_modern_bar(daily_total_steps, goal_steps, 12, 'gradient')
        steps_percentage = (daily_total_steps / goal_steps * 100) if goal_steps > 0 else 0
        
        steps_progress = (
            f"👞 <b>Активность</b>\n"
            f"{'═' * 35}\n"
            f"👶 Шаги: {daily_total_steps:,} из {goal_steps:,}\n"
            f"{steps_bar} {steps_percentage:.0f}%\n"
        )
        
        await callback.message.answer(steps_progress, parse_mode="HTML")
        
        # ========== ✅ МОТИВАЦИОННОЕ СООБЩЕНИЕ ==========
        cal_percentage = (net_calories / goal_cal * 100) if goal_cal > 0 else 0
        water_percentage = (daily_total_water / goal_water * 100) if goal_water > 0 else 0
        steps_percentage = (daily_total_steps / goal_steps * 100) if goal_steps > 0 else 0
        
        # Умное мотивационное сообщение с учетом воды и шагов
        if cal_percentage >= 90 and cal_percentage <= 110:
            motivation = f"🎯 <b>Отличный результат!</b> Чистые калории: {net_calories:.0f} ккал - прямо на цели!"
        elif cal_percentage > 110:
            motivation = f"⚠️ <b>Превысили дневную норму!</b> Чистые калории: {net_calories:.0f} ккал. Но это лучше, чем недоедать."
        else:
            remaining_cal = goal_cal - net_calories
            motivation = f"💪 <b>Хорошая работа!</b> Осталось еще {remaining_cal:.0f} ккал до цели (чистые: {net_calories:.0f} ккал)."
        
        # Добавляем информацию о воде
        if water_percentage < 50:
            motivation += f"\n💧 <b>Не забывайте пить воду!</b> Выпито {daily_total_water:.0f}мл из {goal_water:.0f}мл."
        elif water_percentage >= 100:
            motivation += f"\n💧 <b>Отличная гидратация!</b> Цель по воде выполнена!"
        else:
            remaining_water = goal_water - daily_total_water
            motivation += f"\n💧 <b>Хорошо!</b> Осталось выпить {remaining_water:.0f}мл воды."
        
        # Добавляем информацию о шагах
        if steps_percentage < 30:
            motivation += f"\n👞 <b>Время двигаться!</b> Пройдено {daily_total_steps:,} из {goal_steps:,} шагов."
        elif steps_percentage >= 100:
            motivation += f"\n👞 <b>Супер!</b> Цель по шагам достигнута!"
        else:
            remaining_steps = goal_steps - daily_total_steps
            motivation += f"\n👞 <b>Хорошо!</b> Осталось пройти {remaining_steps:,} шагов."
        
        await callback.message.answer(motivation, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"❌ Error showing daily progress: {e}")
        # Не прерываем процесс если прогресс не показался

@router.message(Command("today"))
async def cmd_today_summary(message: Message):
    """
    ✨ Команда для просмотра дневной сводки
    /today - показывает прогресс дня
    """
    user_id = message.from_user.id
    
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Сначала настройте профиль (/set_profile)")
            return
        
        # Получаем приёмы пищи за сегодня
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        meals_result = await session.execute(
            select(Meal).where(
                (Meal.user_id == user.id) &
                (Meal.datetime >= today_start) &
                (Meal.datetime <= today_end)
            ).order_by(Meal.datetime)
        )
        today_meals = meals_result.scalars().all()
        
        # Получаем записи о воде за сегодня
        water_result = await session.execute(
            select(WaterEntry).where(
                (WaterEntry.user_id == user.id) &
                (WaterEntry.datetime >= today_start) &
                (WaterEntry.datetime <= today_end)
            )
        )
        today_water = water_result.scalars().all()
        
        # Получаем записи о шагах за сегодня
        steps_result = await session.execute(
            select(StepsEntry).where(
                (StepsEntry.user_id == user.id) &
                (StepsEntry.datetime >= today_start) &
                (StepsEntry.datetime <= today_end)
            )
        )
        today_steps = steps_result.scalars().all()
        
        # Вычисляем итоги
        daily_total_cal = sum(meal.total_calories for meal in today_meals)
        daily_total_prot = sum(meal.total_protein for meal in today_meals)
        daily_total_fat = sum(meal.total_fat for meal in today_meals)
        daily_total_carbs = sum(meal.total_carbs for meal in today_meals)
        daily_total_water = sum(water.amount for water in today_water)
        daily_total_steps = sum(steps.steps_count for steps in today_steps)
        
        # Рассчитываем сожженные калории от шагов
        steps_calories_burned = int(daily_total_steps * 0.04)  # ~0.04 ккал на шаг
        net_calories = daily_total_cal - steps_calories_burned
        
        goal_cal = user.daily_calorie_goal or 2000
        goal_prot = user.daily_protein_goal or 150
        goal_fat = user.daily_fat_goal or 65
        goal_carbs = user.daily_carbs_goal or 250
        goal_water = user.daily_water_goal or 2000
        goal_steps = user.daily_steps_goal or 10000
        
        # ✅ Красивая дневная сводка
        daily_summary = MessageTemplates.daily_summary(
            datetime.now().strftime("%d.%m.%Y"),
            daily_total_cal, goal_cal,
            daily_total_prot, daily_total_fat, daily_total_carbs,
            daily_total_water,  # вода из БД
            goal_water,  # цель воды
            0  # серия дней
        )
        
        await message.answer(daily_summary, parse_mode="HTML")
        
        # ✅ Прогресс-карточка
        daily_progress = NutritionCard.create_modern_daily_goal_card(
            net_calories, goal_cal,
            daily_total_prot, goal_prot,
            daily_total_fat, goal_fat,
            daily_total_carbs, goal_carbs
        )
        
        # Добавляем информацию о сожженных калориях
        calories_info = (
            f"🔥 <b>Баланс калорий</b>\n"
            f"{'═' * 35}\n"
            f"🍽️ Потреблено: {daily_total_cal:.0f} ккал\n"
            f"👞 Сожжено: {steps_calories_burned:.0f} ккал ({daily_total_steps:,} шагов)\n"
            f"⚖️ Чистые: {net_calories:.0f} ккал\n"
        )
        
        await message.answer(calories_info, parse_mode="HTML")
        
        await message.answer(daily_progress, parse_mode="HTML")
        
        # ========== 💪 ПРОГРЕСС ПО ВОДЕ ==========
        water_bar = ProgressBar.create_modern_bar(daily_total_water, goal_water, 12, 'gradient')
        water_percentage = (daily_total_water / goal_water * 100) if goal_water > 0 else 0
        
        water_progress = (
            f"💧 <b>Водный баланс</b>\n"
            f"{'═' * 35}\n"
            f"💧 Выпито: {daily_total_water:.0f}мл из {goal_water:.0f}мл\n"
            f"{water_bar} {water_percentage:.0f}%\n"
        )
        
        await message.answer(water_progress, parse_mode="HTML")
        
        # ========== 👞 ПРОГРЕСС ПО ШАГАМ ==========
        steps_bar = ProgressBar.create_modern_bar(daily_total_steps, goal_steps, 12, 'gradient')
        steps_percentage = (daily_total_steps / goal_steps * 100) if goal_steps > 0 else 0
        
        steps_progress = (
            f"👞 <b>Активность</b>\n"
            f"{'═' * 35}\n"
            f"👶 Шаги: {daily_total_steps:,} из {goal_steps:,}\n"
            f"{steps_bar} {steps_percentage:.0f}%\n"
        )
        
        await message.answer(steps_progress, parse_mode="HTML")
        
        # ✅ Макросы
        macros_chart = NutritionCard.create_macros_pie_chart(
            daily_total_prot, daily_total_fat, daily_total_carbs
        )
        
        await message.answer(
            f"📊 <b>Распределение макросов:</b>\n\n{macros_chart}",
            parse_mode="HTML"
        )


@router.callback_query(F.data == "cancel_meal")
async def cancel_meal_callback(callback: CallbackQuery, state: FSMContext):
    logger.info(f"❌ cancel_meal_callback: user={callback.from_user.id}")

    data = await state.get_data()
    chat_id = callback.message.chat.id

    for msg_id in data.get('product_msg_ids', []):
        try:
            await callback.bot.delete_message(chat_id, msg_id)
        except Exception as e:
            logger.warning(f"Could not delete message: {e}")

    try:
        await callback.bot.delete_message(chat_id, data.get('totals_msg_id'))
    except Exception as e:
        logger.warning(f"Could not delete totals message: {e}")

    await state.update_data(last_photo_id=None)
    await callback.message.answer("❌ Ввод отменён.")
    await state.clear()
    await _safe_answer(callback)

@router.callback_query(F.data == "action_cancel")
async def action_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")
    await callback.message.answer("❌ Отменено.")
    await _safe_answer(callback)

@router.callback_query(F.data == "food_manual")
async def food_manual_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    from handlers.food import cmd_log_food
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)
    await _safe_answer(callback)

# ========== ✅ НОВЫЕ ОБРАБОТЧИКИ ==========

@router.callback_query(F.data == "show_nutrition_details")
async def show_nutrition_details_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик для показа детальной информации о КБЖУ"""
    await callback.answer()
    
    data = await state.get_data()
    selected_foods = data.get('selected_foods', [])
    total_calories = data.get('total_calories', 0)
    total_protein = data.get('total_protein', 0)
    total_fat = data.get('total_fat', 0)
    total_carbs = data.get('total_carbs', 0)
    meal_type = data.get('meal_type', 'meal')
    
    if not selected_foods:
        await callback.message.answer("❌ Нет данных для анализа")
        return
    
    # Детальный анализ КБЖУ
    text = f"📊 <b>Детальный анализ КБЖУ</b>\n"
    text += f"{'═' * 40}\n\n"
    
    # Общая информация
    text += f"🍽️ <b>Общие показатели:</b>\n"
    text += f"🔥 Калории: {total_calories:.0f} ккал\n"
    text += f"🥩 Белки: {total_protein:.1f}г\n"
    text += f"🥑 Жиры: {total_fat:.1f}г\n"
    text += f"🍚 Углеводы: {total_carbs:.1f}г\n\n"
    
    # Анализ по продуктам
    text += f"📦 <b>Детализация по продуктам:</b>\n\n"
    
    for i, food in enumerate(selected_foods, 1):
        weight = food.get('weight', 0)
        nutrients = _calculate_nutrients(food, weight)
        
        # Процент от общего
        if total_calories > 0:
            cal_percent = (nutrients['calories'] / total_calories) * 100
        else:
            cal_percent = 0
            
        text += f"{i}. <b>{food['name']}</b> ({weight}г)\n"
        text += f"   🔥 {nutrients['calories']:.0f} ккал ({cal_percent:.1f}%)\n"
        text += f"   🥩 {nutrients['protein']:.1f}г | 🥑 {nutrients['fat']:.1f}г | 🍚 {nutrients['carbs']:.1f}г\n\n"
    
    # Рекомендации по балансу
    total_macros = total_protein + total_fat + total_carbs
    if total_macros > 0:
        prot_percent = (total_protein / total_macros) * 100
        fat_percent = (total_fat / total_macros) * 100
        carbs_percent = (total_carbs / total_macros) * 100
        
        text += f"💡 <b>Анализ баланса БЖУ:</b>\n"
        text += f"🥩 Белки: {prot_percent:.1f}% (рекомендуется 20-30%)\n"
        text += f"🥑 Жиры: {fat_percent:.1f}% (рекомендуется 20-35%)\n"
        text += f"🍚 Углеводы: {carbs_percent:.1f}% (рекомендуется 45-65%)\n\n"
        
        # Рекомендации
        if prot_percent < 20:
            text += "⚠️ Мало белков - добавьте белковые продукты\n"
        if fat_percent < 20:
            text += "⚠️ Мало жиров - добавьте полезные жиры\n"
        if carbs_percent < 45:
            text += "⚠️ Мало углеводов - добавьте сложные углеводы\n"
    
    # Калорийность по типам
    text += f"\n🔥 <b>Распределение калорий:</b>\n"
    for food in selected_foods:
        weight = food.get('weight', 0)
        nutrients = _calculate_nutrients(food, weight)
        calories_per_100g = (nutrients['calories'] / weight) * 100 if weight > 0 else 0
        
        density = "Низкая" if calories_per_100g <= 100 else "Средняя" if calories_per_100g <= 200 else "Высокая"
        text += f"• {food['name']}: {calories_per_100g:.0f} ккал/100г ({density})\n"
    
    await callback.message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "retry_photo")
async def retry_photo_callback(callback: CallbackQuery, state: FSMContext):
    """✅ Обработчик для повторного распознавания"""
    await callback.answer()
    await callback.message.delete()
    
    await state.set_state(FoodStates.choosing_meal_type)
    
    await callback.message.answer(
        "📸 Отправьте новое фото блюда для анализа:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel")
        ]])
    )

@router.callback_query(F.data == "manual_food")
async def manual_food_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для добавления приема пищи из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    await state.clear()
    from handlers.food import cmd_log_food
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)

@router.callback_query(F.data == "manual_food_entry")
async def manual_food_entry_callback(callback: CallbackQuery, state: FSMContext):
    """✅ Обработчик для ручного ввода"""
    await callback.answer()
    await callback.message.delete()
    
    await state.clear()
    from handlers.food import cmd_log_food
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)

# ========== ОБРАБОТЧИК ГОЛОСОВЫХ СООБЩЕНИЙ ==========

@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
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

async def _handle_recognition_failure(message: Message, state: FSMContext):
    """Обработчик при неудаче распознавания"""
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

