"""
AI Handlers для NutriBuddy
✅ Добавлен перевод с английского на русский
✅ Поддержка нескольких продуктов с одного фото
✅ Исправлено распознавание еды
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import logging
from PIL import Image
import io
from typing import List

from services.cloudflare_ai import analyze_food_image, transcribe_audio
from services.food_api import search_food
from services.translator import translate_to_russian, extract_food_items
from keyboards.inline import get_food_selection_keyboard
from utils.states import FoodStates
from database.db import get_session
from database.models import User, Meal, FoodItem
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)


def _bytes_to_array(image_bytes: bytes) -> List[int]:
    """Конвертирует bytes в список целых чисел 0-255"""
    return list(image_bytes)


def _prepare_image_for_cloudflare(image_bytes: bytes) -> bytes:
    """Оптимизирует изображение для Cloudflare AI"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        logger.warning(f"⚠️ Image prep fallback: {e}")
        return image_bytes


@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """
    Обработка фото еды с переводом и детекцией нескольких продуктов.
    """
    try:
        current_state = await state.get_state()
        logger.info(f"📸 Photo in state: {current_state}")
        
        # Разрешаем фото только в нужных состояниях
        if current_state not in [FoodStates.searching_food, None, 'None']:
            logger.info(f"⚠️ Ignoring photo in state: {current_state}")
            return
        
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        optimized = _prepare_image_for_cloudflare(file_data)
        
        await message.answer("🔍 Анализирую изображение через Cloudflare AI...")
        
        # 🔥 Улучшенный промпт для детального описания
        description = await analyze_food_image(
            optimized,
            prompt="Describe all food items in this image in detail. List each food item separately. Include main dish, side dishes, vegetables, and sauces. Be specific about ingredients."
        )
        
        if not description or len(description) < 5 or len(description) > 500:
            await message.answer(
                "❌ Не удалось распознать фото.\n\n"
                "📝 <b>Введите название блюда вручную:</b>\n"
                "<i>Например: «курица с овощами», «гречка с мясом»</i>",
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.manual_food_name)
            return
        
        logger.info(f"✅ AI description (EN): {description}")
        
        # 🔥 Переводим описание на русский
        description_ru = await translate_to_russian(description)
        logger.info(f"✅ AI description (RU): {description_ru}")
        
        # 🔥 Извлекаем отдельные продукты
        food_items = await extract_food_items(description)
        logger.info(f"✅ Extracted food items: {food_items}")
        
        # Сохраняем описание
        await state.update_data(ai_description=description_ru, photo_file_id=photo.file_id)
        
        # 🔥 Ищем каждый продукт в базе
        all_foods = []
        for item in food_items[:3]:  # Максимум 3 продукта
            item_ru = await translate_to_russian(item)
            foods = await search_food(item_ru)
            if foods:
                all_foods.extend(foods[:2])  # Максимум 2 варианта на продукт
        
        if not all_foods:
            # Пробуем поиск по полному описанию
            all_foods = await search_food(description_ru)
        
        if all_foods:
            await message.answer(
                f"🧠 <b>Распознано:</b> {description_ru}\n\n"
                f"📋 <b>Найдено продуктов:</b> {len(all_foods)}\n\n"
                f"Выберите продукт:",
                reply_markup=get_food_selection_keyboard(all_foods[:5]),
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.selecting_food)
            await state.update_data(foods=all_foods)
        else:
            await message.answer(
                f"🧠 <b>Описание:</b> <i>{description_ru}</i>\n\n"
                f"❌ Не найдено в базе продуктов.\n\n"
                f"📝 <b>Введите название вручную:</b>",
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.manual_food_name)
            
    except Exception as e:
        logger.error(f"❌ Photo error: {e}", exc_info=True)
        await message.answer("❌ Ошибка анализа. Попробуйте позже.")


@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    """Распознавание голоса через Whisper"""
    try:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        await message.answer("🎤 Распознаю речь...")
        
        text = await transcribe_audio(file_data)
        
        if not text:
            await message.answer("❌ Не удалось распознать.")
            return
        
        logger.info(f"✅ Whisper: {text[:100]}...")
        
        await message.answer(f"📝 <b>Распознано:</b>\n<i>{text}</i>", parse_mode="HTML")
        await state.update_data(voice_text=text)
        
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🍽️ Записать как еду")],
                [KeyboardButton(text="📋 В список покупок")],
                [KeyboardButton(text="📖 Рецепт из этого")],
                [KeyboardButton(text="❌ Отмена")]
            ],
            resize_keyboard=True
        )
        await message.answer("💡 Что сделать с текстом?", reply_markup=kb)
        
    except Exception as e:
        logger.error(f"❌ Voice error: {e}")
        await message.answer("❌ Ошибка распознавания.")
