"""
🔧 Исправленный обработчик мультимедиа с безопасной работой с FSM
✅ Правильная обработка состояний и сообщений
✅ Безопасное удаление и редактирование сообщений
✅ Централизованная обработка ошибок
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

from services.ai_engine_manager import ai  # Исправленный импорт
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

# Безопасная функция редактирования сообщения
async def _safe_edit_message(message: Message, text: str, reply_markup=None, parse_mode="HTML"):
    """Безопасное редактирование сообщения с полной обработкой ошибок"""
    try:
        await message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug(f"Message not modified: {e}")
            return True
        elif "message to edit not found" in str(e):
            logger.warning(f"Message not found for edit: {e}")
            return False
        else:
            logger.error(f"Telegram error editing message: {e}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error editing message: {e}")
        return False

# Безопасная функция удаления сообщения
async def _safe_delete_message(message: Message):
    """Безопасное удаление сообщения с обработкой ошибок"""
    try:
        await message.delete()
        return True
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            logger.debug(f"Message not found for delete: {e}")
            return True
        elif "message can't be deleted" in str(e):
            logger.warning(f"Message can't be deleted: {e}")
            return False
        else:
            logger.error(f"Telegram error deleting message: {e}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error deleting message: {e}")
        return False

# Безопасная функция ответа на callback
async def _safe_callback_answer(callback: CallbackQuery, text: str = None):
    """Безопасный ответ на callback с обработкой ошибок"""
    try:
        await callback.answer(text)
        return True
    except TelegramBadRequest as e:
        if "query is too old" in str(e):
            logger.debug(f"Callback too old: {e}")
            return True
        elif "invalid query" in str(e):
            logger.warning(f"Invalid callback query: {e}")
            return False
        else:
            logger.error(f"Telegram error answering callback: {e}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error answering callback: {e}")
        return False

# Безопасная обработка фото в отдельном потоке
async def _process_image_in_thread(image_data: bytes) -> Dict:
    """Обработка изображения в отдельном потоке чтобы не блокировать event loop"""
    def _process_sync():
        try:
            image = Image.open(io.BytesIO(image_data))
            # Конвертируем в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Оптимизируем размер если слишком большой
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Сохраняем в буфер
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            
            return {
                "success": True,
                "data": buffer.getvalue(),
                "size": len(buffer.getvalue()),
                "original_size": len(image_data)
            }
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {"success": False, "error": str(e)}
    
    # Выполняем в отдельном потоке
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_sync)

async def _process_llama_result(parsed_data: Dict) -> Dict:
    """Обработка результата от Llama с валидацией"""
    try:
        if not parsed_data or not isinstance(parsed_data, dict):
            return {
                "success": False,
                "error": "Invalid response format",
                "data": {}
            }
        
        # Валидация обязательных полей
        required_fields = ["dish_name", "ingredients", "confidence"]
        for field in required_fields:
            if field not in parsed_data:
                return {
                    "success": False,
                    "error": f"Missing required field: {field}",
                    "data": {}
                }
        
        return {
            "success": True,
            "data": parsed_data
        }
    except Exception as e:
        logger.error(f"Error processing Llama result: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {}
        }

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото с улучшенной обработкой ошибок и FSM"""
    user_id = message.from_user.id
    
    try:
        # Очищаем состояние перед началом новой обработки
        await state.clear()
        await state.set_state(FoodStates.waiting_for_food_confirmation)
        
        # Проверяем наличие пользователя
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await message.answer(
                    "❌ Сначала создайте профиль командой /set_profile",
                    reply_markup=get_daily_goals_keyboard()
                )
                await state.clear()
                return
        
        # Получаем фото наибольшего размера
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        
        # Проверяем размер файла
        max_file_size = 10 * 1024 * 1024  # 10MB лимит
        if file_info.file_size > max_file_size:
            await message.answer(
                f"❌ Фото слишком большое. Максимальный размер: {max_file_size // (1024*1024)} МБ",
                reply_markup=get_daily_goals_keyboard()
            )
            await state.clear()
            return
        
        # Проверяем размер изображения
        max_dimensions = (4096, 4096)  # 4K x 4K максимум
        if (file_info.width and file_info.height and 
            (file_info.width > max_dimensions[0] or file_info.height > max_dimensions[1])):
            await message.answer(
                f"❌ Слишком большое разрешение. Максимальное: {max_dimensions[0]}x{max_dimensions[1]}",
                reply_markup=get_daily_goals_keyboard()
            )
            await state.clear()
            return
        
        # Скачиваем и обрабатываем фото
        downloaded_file = await message.bot.download_file(file_info.file_path)
        
        # Обрабатываем изображение в отдельном потоке
        processed = await _process_image_in_thread(downloaded_file)
        
        if not processed["success"]:
            await message.answer(
                f"❌ Ошибка обработки фото: {processed.get('error', 'неизвестная ошибка')}",
                reply_markup=get_daily_goals_keyboard()
            )
            await state.clear()
            return
        
        # Отправляем сообщение о обработке
        progress_msg = await message.answer("🔍 Анализирую фото...")
        
        # Распознаем еду через новый AI Manager
        try:
            recognition_result = await ai.recognize_food(processed["data"])
            
            if not recognition_result.get("success"):
                await _safe_edit_message(
                    progress_msg,
                    f"❌ Не удалось распознать еду: {recognition_result.get('error', 'ошибка распознавания')}",
                    reply_markup=get_daily_goals_keyboard()
                )
                await state.clear()
                return
            
            # Получаем данные от Llama Vision
            data = recognition_result.get("data", {})
            dish_name = data.get("dish_name", "Неизвестное блюдо")
            ingredients = data.get("ingredients", [])
            confidence = data.get("confidence", 0)
            
            # Получаем рассчитанные КБЖУ
            nutrition_data = data.get("nutrition", {})
            total_nutrition = nutrition_data.get("nutrition", {})
            
            # Сохраняем данные в состоянии
            await state.update_data(
                recognized_dish=dish_name,
                ingredients=ingredients,
                confidence=confidence,
                nutrition=total_nutrition,
                original_photo_file_id=photo.file_id,
                progress_message_id=progress_msg.message_id
            )
            
            # Формируем сообщение с результатом
            result_text = f"""
🍽️ <b>Распознано: {dish_name}</b>

📊 <b>Уверенность:</b> {confidence:.1f}%

🥘 <b>Ингредиенты:</b>
{chr(10).join(f"• {ing.get('name', 'Неизвестный ингредиент')} (~{ing.get('weight_estimate', 0)}г)" for ing in ingredients[:5])}
{f"• и ещё {len(ingredients)-5} ингредиентов..." if len(ingredients) > 5 else ""}

📈 <b>Пищевая ценность:</b>
• Калории: {total_nutrition.get('calories', 0)} ккал
• Белки: {total_nutrition.get('protein', 0)} г
• Жиры: {total_nutrition.get('fat', 0)} г
• Углеводы: {total_nutrition.get('carbs', 0)} г

✅ Всё верно?
"""
            
            # Проверяем наличие совпадений для клавиатуры
            has_matches = bool(dish_name and dish_name != "Неизвестное блюдо")
            can_use_ai_ingredients = bool(ingredients)
            
            keyboard = get_food_recognition_result_keyboard(
                has_matches=has_matches,
                can_use_ai_ingredients=can_use_ai_ingredients
            )
            
            await _safe_edit_message(
                progress_msg,
                result_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        except asyncio.TimeoutError:
            await _safe_edit_message(
                progress_msg,
                "⏰ Время ожидания истекло. Попробуйте еще раз.",
                reply_markup=get_daily_goals_keyboard()
            )
            await state.clear()
            
        except Exception as e:
            logger.error(f"Error in photo recognition: {e}")
            await _safe_edit_message(
                progress_msg,
                "❌ Произошла ошибка при распознавании. Попробуйте еще раз.",
                reply_markup=get_daily_goals_keyboard()
            )
            await state.clear()
            
    except Exception as e:
        logger.error(f"Critical error in handle_photo: {e}")
        await message.answer(
            "❌ Произошла критическая ошибка. Попробуйте еще раз.",
            reply_markup=get_daily_goals_keyboard()
        )
        await state.clear()

@router.callback_query(F.data == "confirm_food")
async def confirm_food_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение распознанной еды с безопасной обработкой"""
    user_id = callback.from_user.id
    
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        dish_name = data.get("recognized_dish")
        ingredients = data.get("ingredients", [])
        
        if not dish_name:
            await _safe_callback_answer(callback, "❌ Данные о распознавании утеряны")
            await state.clear()
            return
        
        # Проверяем наличие пользователя
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await _safe_callback_answer(callback, "❌ Пользователь не найден")
                await state.clear()
                return
        
        # Ищем блюдо в базе
        matching_dishes = find_matching_dishes(dish_name)
        
        if matching_dishes:
            # Нашли готовое блюдо
            dish_info = matching_dishes[0]
            meal_type = "main"
            
            # Создаем запись о приеме пищи
            new_meal = Meal(
                user_id=user.id,
                meal_type=meal_type,
                datetime=datetime.now(),
                total_calories=dish_info.get("calories", 0),
                total_protein=dish_info.get("protein", 0),
                total_fat=dish_info.get("fat", 0),
                total_carbs=dish_info.get("carbs", 0)
            )
            
            session.add(new_meal)
            await session.commit()
            
            # Добавляем ингредиенты
            for ingredient_name in dish_info.get("ingredients", []):
                food_item = FoodItem(
                    meal_id=new_meal.id,
                    name=ingredient_name,
                    weight=100,  # по умолчанию 100г
                    calories=dish_info.get("calories", 0) // len(dish_info.get("ingredients", [1])),
                    protein=0, fat=0, carbs=0  # будем рассчитывать позже
                )
                session.add(food_item)
            
            await session.commit()
            
            # Формируем сообщение об успехе
            success_text = f"""
✅ <b>Добавлено: {dish_name}</b>

📊 <b>Пищевая ценность:</b>
• Калории: {dish_info.get('calories', 0)} ккал
• Белки: {dish_info.get('protein', 0)} г
• Жиры: {dish_info.get('fat', 0)} г
• Углеводы: {dish_info.get('carbs', 0)} г

💪 Отлично! Продолжай в том же духе!
"""
            
            # Безопасно редактируем или отправляем новое сообщение
            if callback.message:
                success = await _safe_edit_message(
                    callback.message,
                    success_text,
                    reply_markup=get_daily_goals_keyboard(),
                    parse_mode="HTML"
                )
                if not success:
                    await callback.message.answer(success_text, reply_markup=get_daily_goals_keyboard(), parse_mode="HTML")
            else:
                await callback.message.answer(success_text, reply_markup=get_daily_goals_keyboard(), parse_mode="HTML")
            
            await _safe_callback_answer(callback, "✅ Блюдо добавлено!")
            
        else:
            # Блюдо не найдено, предлагаем варианты
            await _show_dish_selection_for_product(callback, state, dish_name)
            return
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in confirm_food_callback: {e}")
        await _safe_callback_answer(callback, "❌ Произошла ошибка")
        await state.clear()

async def _show_dish_selection_for_product(callback: CallbackQuery, state: FSMContext, dish_name: str):
    """Показ вариантов выбора блюда с безопасной обработкой"""
    try:
        # Получаем варианты продуктов
        variants = get_product_variants(dish_name)
        
        if not variants:
            await _safe_callback_answer(callback, "❌ Варианты не найдены")
            await state.clear()
            return
        
        # Формируем клавиатуру с вариантами
        builder = InlineKeyboardBuilder()
        
        for variant in variants:
            builder.row(
                InlineKeyboardButton(
                    text=f"{variant['name']} ({variant['calories']} ккал)",
                    callback_data=f"select_product_{variant.get('key', variant['name'])}"
                )
            )
        
        builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_food_selection"))
        
        keyboard = builder.as_markup()
        
        # Формируем сообщение
        text = f"""
🔍 <b>Выберите точный вариант:</b>

Не удалось однозначно определить "{dish_name}".

Выберите подходящий вариант из списка:
"""
        
        # Безопасно редактируем сообщение
        if callback.message:
            success = await _safe_edit_message(
                callback.message,
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            if not success:
                await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
        await _safe_callback_answer(callback)
        
    except Exception as e:
        logger.error(f"Error in _show_dish_selection_for_product: {e}")
        await _safe_callback_answer(callback, "❌ Ошибка при загрузке вариантов")
        await state.clear()

@router.callback_query(F.data.startswith("select_product_"))
async def select_product_callback(callback: CallbackQuery, state: FSMContext):
    """Выбор конкретного продукта с безопасной обработкой"""
    user_id = callback.from_user.id
    
    try:
        # Извлекаем идентификатор продукта (key или name)
        parts = callback.data.split("_", 2)
        if len(parts) < 3:
            await _safe_callback_answer(callback, "❌ Неверный формат продукта")
            await state.clear()
            return
        
        product_key_or_name = parts[2]
        
        # Ищем продукт в базе по key или name (LOCAL_FOOD_DB это плоский словарь)
        product = LOCAL_FOOD_DB.get(product_key_or_name)
        
        # Если не нашли по ключу, ищем по name и алиасам
        if not product:
            for key, item in LOCAL_FOOD_DB.items():
                if (item.get("name") == product_key_or_name or 
                    product_key_or_name in item.get("aliases", [])):
                    product = item
                    break
        
        if not product:
            await _safe_callback_answer(callback, "❌ Продукт не найден")
            await state.clear()
            return
        
        # Проверяем наличие пользователя
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await _safe_callback_answer(callback, "❌ Пользователь не найден")
                await state.clear()
                return
        
        # Создаем запись о приеме пищи
        new_meal = Meal(
            user_id=user.id,
            meal_type="main",
            datetime=datetime.now(),
            total_calories=product.get("calories", 0),
            total_protein=product.get("protein", 0),
            total_fat=product.get("fat", 0),
            total_carbs=product.get("carbs", 0)
        )
        
        session.add(new_meal)
        await session.commit()
        
        # Добавляем продукт как ингредиент
        food_item = FoodItem(
            meal_id=new_meal.id,
            name=product.get("name", "Неизвестный продукт"),
            weight=100,
            calories=product.get("calories", 0),
            protein=product.get("protein", 0),
            fat=product.get("fat", 0),
            carbs=product.get("carbs", 0)
        )
        
        session.add(food_item)
        await session.commit()
        
        # Формируем сообщение об успехе
        success_text = f"""
✅ <b>Добавлено: {product.get('name')}</b>

📊 <b>Пищевая ценность (на 100г):</b>
• Калории: {product.get('calories', 0)} ккал
• Белки: {product.get('protein', 0)} г
• Жиры: {product.get('fat', 0)} г
• Углеводы: {product.get('carbs', 0)} г

💪 Отлично! Продолжай в том же духе!
"""
        
        # Безопасно редактируем или отправляем сообщение
        if callback.message:
            success = await _safe_edit_message(
                callback.message,
                success_text,
                reply_markup=get_daily_goals_keyboard(),
                parse_mode="HTML"
            )
            if not success:
                await callback.message.answer(success_text, reply_markup=get_daily_goals_keyboard(), parse_mode="HTML")
        else:
            await callback.message.answer(success_text, reply_markup=get_daily_goals_keyboard(), parse_mode="HTML")
        
        await _safe_callback_answer(callback, "✅ Продукт добавлен!")
        await state.clear()
        
    except ValueError:
        await _safe_callback_answer(callback, "❌ Неверный формат продукта")
        await state.clear()
    except Exception as e:
        logger.error(f"Error in select_product_callback: {e}")
        await _safe_callback_answer(callback, "❌ Произошла ошибка")
        await state.clear()

@router.callback_query(F.data == "cancel_food_selection")
async def cancel_food_selection_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена выбора продукта с безопасной обработкой"""
    try:
        await state.clear()
        
        cancel_text = "❌ Выбор отменен"
        
        if callback.message:
            success = await _safe_edit_message(
                callback.message,
                cancel_text,
                reply_markup=get_daily_goals_keyboard()
            )
            if not success:
                await callback.message.answer(cancel_text, reply_markup=get_daily_goals_keyboard())
        else:
            await callback.message.answer(cancel_text, reply_markup=get_daily_goals_keyboard())
        
        await _safe_callback_answer(callback, "Выбор отменен")
        
    except Exception as e:
        logger.error(f"Error in cancel_food_selection_callback: {e}")
        await _safe_callback_answer(callback, "❌ Ошибка при отмене")

@router.callback_query(F.data == "retry_recognition")
async def retry_recognition_callback(callback: CallbackQuery, state: FSMContext):
    """Повторное распознавание с очисткой состояния"""
    try:
        await state.clear()
        
        if callback.message:
            success = await _safe_edit_message(
                callback.message,
                "📸 Отправьте новое фото для распознавания",
                reply_markup=get_daily_goals_keyboard()
            )
            if not success:
                await callback.message.answer("📸 Отправьте новое фото для распознавания", reply_markup=get_daily_goals_keyboard())
        else:
            await callback.message.answer("📸 Отправьте новое фото для распознавания", reply_markup=get_daily_goals_keyboard())
        
        await _safe_callback_answer(callback, "Готов к повторному распознаванию")
        
    except Exception as e:
        logger.error(f"Error in retry_recognition_callback: {e}")
        await _safe_callback_answer(callback, "❌ Ошибка при подготовке к повтору")

# Экспорт для использования в других модулях
async def safe_process_photo(message: Message, state: FSMContext):
    """Безопасная обработка фото для использования из других модулей"""
    return await handle_photo(message, state)
