from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging
from services.cloudflare_ai import analyze_food_image, transcribe_audio
from services.food_api import search_food
from keyboards.inline import get_food_selection_keyboard
from utils.states import FoodStates
from database.db import get_session
from database.models import Meal, FoodItem
from datetime import datetime

router = Router()

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file_info.file_path)
    file_data = file_bytes.read()
    
    await message.answer("🔍 Анализирую фото через Cloudflare AI...")
    
    try:
        description = await analyze_food_image(file_data)
        if not description:
            await message.answer("❌ Не удалось распознать фото. Попробуйте ещё раз.")
            return
        
        await state.update_data(ai_description=description, photo_file_id=photo.file_id)
        foods = await search_food(description)
        
        if foods:
            await message.answer(
                f"🧠 <b>Распознано:</b> {description}\n\nВыберите продукт:",
                reply_markup=get_food_selection_keyboard(foods),
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.selecting_food)
            await state.update_data(foods=foods)
        else:
            await message.answer(
                f"🧠 Описание: {description}\n\nВведите название блюда вручную:"
            )
            await state.set_state(FoodStates.manual_food_name)
    except Exception as e:
        logging.error(f"Cloudflare vision error: {e}")
        await message.answer("❌ Ошибка при анализе фото. Попробуйте позже.")

@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    voice = message.voice
    file_info = await message.bot.get_file(voice.file_id)
    file_bytes = await message.bot.download_file(file_info.file_path)
    file_data = file_bytes.read()
    
    await message.answer("🎤 Распознаю речь через Cloudflare AI...")
    
    try:
        text = await transcribe_audio(file_data)
        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return
        
        await message.answer(f"📝 <b>Распознано:</b> {text}", parse_mode="HTML")
        await state.update_data(voice_text=text)
        
        await message.answer(
            "💡 <b>Что сделать с этим текстом?</b>\n\n"
            "• /log_food — записать приём пищи\n"
            "• /shopping — добавить в список покупок\n"
            "• /recipe — сгенерировать рецепт"
        )
    except Exception as e:
        logging.error(f"Cloudflare whisper error: {e}")
        await message.answer("❌ Ошибка распознавания речи. Попробуйте ещё раз.")