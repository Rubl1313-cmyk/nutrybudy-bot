"""
AI Handlers для NutriBuddy - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
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

# 🔥 Хранилище для предотвращения дубликатов (в памяти)
processed_photos = {}


def _bytes_to_array(image_bytes: bytes) -> List[int]:
    """Конвертирует bytes в список целых чисел 0-255"""
    return list(image_bytes)


def _prepare_image_for_cloudflare(image_bytes: bytes) -> bytes:
    """Оптимизирует изображение"""
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


def _extract_keywords(description: str) -> str:
    """
    Извлекает ключевые слова из описания для поиска.
    Пример: "A roasted chicken with herbs" → "roasted chicken"
    """
    # Простая эвристика: берём первые 2-3 слова
    words = description.lower().split()
    # Убираем артикли и предлоги
    stopwords = {'a', 'an', 'the', 'with', 'on', 'in', 'at', 'to', 'and', 'or'}
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    return ' '.join(keywords[:3])  # Первые 3 ключевых слова


async def handle_photo(message: Message, state: FSMContext):
    """
    Обработка фото еды с улучшенным поиском.
    """
    try:
        photo = message.photo[-1]
        file_id = photo.file_id
        
        # 🔥 Проверка на дубликат (последние 10 фото)
        user_id = message.from_user.id
        if user_id in processed_photos:
            if processed_photos[user_id].get(file_id):
                logger.info(f"⚠️ Duplicate photo from user {user_id}")
                await message.answer("🔄 Я уже анализировал это фото. Если хотите записать блюдо, введите название вручную.")
                return
        
        file_info = await message.bot.get_file(file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        # Оптимизация
        optimized = _prepare_image_for_cloudflare(file_data)
        
        await message.answer("🔍 Анализирую изображение через Cloudflare AI...")
        
        # 🔥 Улучшенный промпт для получения короткого названия
        description = await analyze_food_image(
            optimized,
            prompt="What food is in this image? Return ONLY the main dish/product name in Russian, 2-3 words maximum. Example: 'жареная курица' or 'греческий салат'. No descriptions, just the name."
        )
        
        if not description:
            # Пробуем английский промпт как fallback
            description = await analyze_food_image(
                optimized,
                prompt="What food is in this image? Return ONLY the main dish name in English, 2-3 words."
            )
        
        if not description:
            await message.answer(
                "❌ Не удалось распознать фото.\n\n"
                "Попробуйте:\n"
                "• Отправить более чёткое фото\n"
                "• Ввести название блюда вручную через /log_food"
            )
            return
        
        logger.info(f"✅ AI description: {description}")
        
        # 🔥 Извлекаем ключевые слова для поиска
        keywords = _extract_keywords(description)
        logger.info(f"🔍 Search keywords: {keywords}")
        
        # Ищем в OpenFoodFacts
        foods = await search_food(keywords)
        
        # 🔥 Если не нашли, пробуем перевести/упростить
        if not foods and 'chicken' in description.lower():
            foods = await search_food("курица")
        elif not foods and 'salad' in description.lower():
            foods = await search_food("салат")
        elif not foods and 'rice' in description.lower():
            foods = await search_food("рис")
        
        # Сохраняем в state
        await state.update_data(ai_description=description, photo_file_id=file_id)
        
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
            # 🔁 Предлагаем ручной ввод
            await message.answer(
                f"🧠 <b>Описание:</b> <i>{description}</i>\n\n"
                f"❌ Не найдено в базе продуктов.\n\n"
                f"📝 <b>Введите название блюда вручную:</b>\n"
                f"<i>Например: «курица жареная», «гречка с мясом»</i>",
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.manual_food_name)
        
        # 🔥 Запоминаем, что обработали это фото
        if user_id not in processed_photos:
            processed_photos[user_id] = {}
        processed_photos[user_id][file_id] = True
        
        # Очищаем старые записи (храним последние 10)
        if len(processed_photos[user_id]) > 10:
            oldest_key = list(processed_photos[user_id].keys())[0]
            del processed_photos[user_id][oldest_key]
            
    except Exception as e:
        logger.error(f"❌ Photo handling error: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при анализе фото.\n"
            "Попробуйте позже или введите название вручную."
        )


@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    """Распознавание голоса"""
    try:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        await message.answer("🎤 Распознаю речь...")
        
        text = await transcribe_audio(file_data)
        
        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return
        
        await message.answer(
            f"📝 <b>Распознано:</b>\n<i>{text}</i>",
            parse_mode="HTML"
        )
        
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
