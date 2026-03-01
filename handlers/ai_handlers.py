"""
AI Handlers для NutriBuddy
Обработка фото и голоса с учётом состояний FSM
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


# =============================================================================
# 📸 ОБРАБОТКА ФОТО (с учётом состояний FSM)
# =============================================================================

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото еды с улучшенным промптом"""
    try:
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        # Оптимизация изображения
        optimized = _prepare_image_for_cloudflare(file_data)
        
        await message.answer("🔍 Анализирую изображение через Cloudflare AI...")
        
        # 🔥 УЛУЧШЕННЫЙ ПРОМПТ для лучшего распознавания
        description = await analyze_food_image(
            optimized,
            prompt="""Опиши еду на этом изображении НА РУССКОМ ЯЗЫКЕ.
Укажи:
1. Основное блюдо (например, "жареная курица с овощами")
2. Гарнир (например, "картофель", "рис")
3. Овощи или соусы если видны

Отвечай кратко, 5-10 слов, только название блюда без описаний."""
        )
        
        if not description:
            # Fallback на английский
            description = await analyze_food_image(
                optimized,
                prompt="Describe this food dish in Russian. Name the main dish, side dish, and vegetables. 5-10 words only."
            )
        
        if not description:
            await message.answer(
                "❌ Не удалось распознать фото.\n\n"
                "📝 Введите название блюда вручную:"
            )
            await state.set_state(FoodStates.manual_food_name)
            return
        
        logger.info(f"✅ AI description: {description}")
        
        # 🔥 Улучшенный поиск: пробуем несколько вариантов
        foods = await search_food(description)
        
        if not foods:
            # Извлекаем ключевые слова
            keywords = description.lower().split()
            keywords = [w for w in keywords if len(w) > 3 and w not in 
                       ['с', 'и', 'на', 'в', 'для', 'из', 'the', 'with', 'and', 'on']]
            
            # Пробуем поиск по каждому ключевому слову
            for keyword in keywords[:3]:
                foods = await search_food(keyword)
                if foods:
                    logger.info(f"✅ Found via keyword: {keyword}")
                    break
        
        await state.update_data(ai_description=description)
        
        if foods:
            await message.answer(
                f"🧠 <b>Распознано:</b> {description}\n\n"
                f"Выберите продукт:",
                reply_markup=get_food_selection_keyboard(foods),
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.selecting_food)
            await state.update_data(foods=foods)
        else:
            await message.answer(
                f"🧠 <b>Описание:</b> <i>{description}</i>\n\n"
                f"📝 <b>Введите название вручную:</b>",
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.manual_food_name)
            
    except Exception as e:
        logger.error(f"❌ Photo error: {e}", exc_info=True)
        await message.answer("❌ Ошибка при анализе. Попробуйте позже.")


# =============================================================================
# 🎤 ОБРАБОТКА ГОЛОСА
# =============================================================================

@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    """Распознавание голоса через Whisper"""
    try:
        current_state = await state.get_state()
        logger.info(f"🎤 Voice received in state: {current_state}")
        
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        await message.answer("🎤 Распознаю речь...")
        
        text = await transcribe_audio(file_data)
        
        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return
        
        logger.info(f"✅ Whisper: {text[:100]}...")
        
        await message.answer(
            f"📝 <b>Распознано:</b>\n<i>{text}</i>",
            parse_mode="HTML"
        )
        
        await state.update_data(voice_text=text)
        
        # Предлагаем действия
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
