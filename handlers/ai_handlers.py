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
    return list(image_bytes)


def _prepare_image_for_cloudflare(image_bytes: bytes) -> bytes:
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
    try:
        current_state = await state.get_state()
        logger.info(f"📸 Photo in state: {current_state}")
        
        if current_state not in [FoodStates.searching_food, None, 'None']:
            logger.info(f"⚠️ Ignoring photo in state: {current_state}")
            return
        
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        optimized = _prepare_image_for_cloudflare(file_data)
        
        await message.answer("🔍 Анализирую изображение...")
        
        description = await analyze_food_image(
            optimized,
            prompt="What food is in this image? Return ONLY the dish name in Russian, 2-4 words maximum."
        )
        
        if not description or len(description) < 3 or len(description) > 100:
            description = await analyze_food_image(
                optimized,
                prompt="Describe this food dish in Russian. Name the main food item only, 2-4 words."
            )
        
        if not description or any(word in description.lower() for word in ['кусочелом', 'куром', 'садеемошам']):
            logger.warning(f"⚠️ Invalid description: {description}")
            await message.answer(
                "❌ Не удалось распознать фото.\n\n"
                "📝 <b>Введите название блюда вручную:</b>",
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.manual_food_name)
            return
        
        logger.info(f"✅ Recognized: {description}")
        
        foods = await search_food(description)
        
        if not foods:
            keywords = description.lower().split()
            keywords = [w for w in keywords if len(w) > 3 and w not in 
                       ['с', 'и', 'на', 'в', 'для', 'из', 'the', 'with', 'and', 'on', 'at']]
            
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
        await message.answer("❌ Ошибка анализа. Попробуйте позже.")


@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
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
