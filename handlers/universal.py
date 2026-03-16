"""
handlers/universal.py
Универсальный обработчик всех сообщений через LangChain Agent
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.langchain_agent import LangChainAgent
from utils.premium_templates import loading_card, error_card

logger = logging.getLogger(__name__)
router = Router()

@router.message(~F.command)
async def universal_handler(message: Message, state: FSMContext):
    """
    Универсальный обработчик всех сообщений (кроме команд)
    """
    user_id = message.from_user.id
    
    try:
        # Получаем или создаём агента для пользователя
        agent = LangChainAgent.get_for_user(user_id, state)
        
        # Обрабатываем разные типы сообщений
        if message.photo:
            await handle_photo(message, agent)
        elif message.voice:
            await handle_voice(message, agent)
        elif message.text:
            await agent.handle_text(message.text, message)
        else:
            await message.answer(
                "🤖 Я пока понимаю только текст, фото и голосовые сообщения.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"❌ Error in universal_handler: {e}")
        await message.answer(
            error_card("general", f"Ошибка обработки: {str(e)}"),
            parse_mode="HTML"
        )

async def handle_photo(message: Message, agent: LangChainAgent):
    """Обработка фото с параллельным анализом"""
    try:
        # Показываем загрузку
        await message.answer(
            loading_card('photo'),
            parse_mode="HTML"
        )
        
        # Запускаем анализ фото в фоне
        import asyncio
        asyncio.create_task(analyze_photo_parallel(message, agent))
        
    except Exception as e:
        logger.error(f"❌ Error in handle_photo: {e}")
        await message.answer(
            error_card("ai", f"Ошибка анализа фото: {str(e)}"),
            parse_mode="HTML"
        )

async def handle_voice(message: Message, agent: LangChainAgent):
    """Обработка голосовых сообщений"""
    try:
        # Показываем загрузку
        loading_msg = await message.answer(
            loading_card('voice'),
            parse_mode="HTML"
        )
        
        # Транскрибируем голос
        text = await transcribe_voice(message)
        
        if text:
            # Удаляем сообщение о загрузке
            await loading_msg.delete()
            
            # Передаём текст в агент
            await agent.handle_text(text, message)
        else:
            await loading_msg.edit_text(
                error_card("ai", "Не удалось распознать речь. Попробуйте ещё раз."),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"❌ Error in handle_voice: {e}")
        await message.answer(
            error_card("ai", f"Ошибка обработки голоса: {str(e)}"),
            parse_mode="HTML"
        )

async def analyze_photo_parallel(message: Message, agent: LangChainAgent):
    """
    Параллельный анализ фото с выбором типа приёма пищи
    """
    try:
        from services.cloudflare_manager import cf_manager
        from services.food_save_service import food_save_service
        from utils.premium_templates import meal_card
        
        # Скачиваем фото
        file = await message.bot.get_file(message.photo[-1].file_id)
        photo_bytes = await message.bot.download_file(file.file_path)
        
        # Анализируем фото через AI
        analysis_result = await cf_manager.analyze_food_photo(photo_bytes.read())
        
        if not analysis_result.get("success"):
            await message.answer(
                error_card("ai", "Не удалось проанализировать фото. Попробуйте ещё раз."),
                parse_mode="HTML"
            )
            return
        
        # Получаем данные о еде
        food_data = analysis_result["data"]
        
        # Показываем клавиатуру выбора типа приёма пищи
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="🌅 Завтрак", callback_data=f"meal_type_breakfast_{json.dumps(food_data)}")
        keyboard.button(text="☀️ Обед", callback_data=f"meal_type_lunch_{json.dumps(food_data)}")
        keyboard.button(text="🌆 Ужин", callback_data=f"meal_type_dinner_{json.dumps(food_data)}")
        keyboard.button(text="🍎 Перекус", callback_data=f"meal_type_snack_{json.dumps(food_data)}")
        keyboard.adjust(2)
        
        await message.answer(
            "📸 <b>Фото проанализировано!</b>\n\n"
            f"🍽️ <b>Распознано:</b> {food_data.get('description', 'Блюдо')}\n\n"
            "🍽️ <b>Выберите тип приёма пищи:</b>",
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in analyze_photo_parallel: {e}")
        await message.answer(
            error_card("ai", f"Ошибка анализа фото: {str(e)}"),
            parse_mode="HTML"
        )

async def transcribe_voice(message: Message) -> str:
    """
    Транскрибация голосового сообщения
    """
    try:
        from services.cloudflare_manager import cf_manager
        
        # Скачиваем голосовое сообщение
        file = await message.bot.get_file(message.voice.file_id)
        voice_bytes = await message.bot.download_file(file.file_path)
        
        # Транскрибируем через Cloudflare Whisper
        result = await cf_manager.transcribe_audio(voice_bytes.read())
        
        if result.get("success"):
            text = result.get("text", "")
            logger.info(f"🎤 Voice transcribed: {text[:50]}...")
            return text
        else:
            logger.error(f"❌ Voice transcription failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error in transcribe_voice: {e}")
        return None

# Callback обработчики для выбора типа приёма пищи
@router.callback_query(F.data.startswith("meal_type_"))
async def meal_type_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора типа приёма пищи после анализа фото
    """
    try:
        # Парсим callback_data
        parts = callback.data.split("_", 2)
        meal_type = parts[1]  # breakfast, lunch, dinner, snack
        food_data_json = parts[2]
        
        import json
        food_data = json.loads(food_data_json)
        
        # Получаем агента
        agent = LangChainAgent.get_for_user(callback.from_user.id, state)
        
        # Сохраняем приём пищи
        from services.food_save_service import food_save_service
        from utils.premium_templates import meal_card
        from utils.helpers import get_daily_stats
        
        save_result = await food_save_service.save_meal(
            callback.from_user.id,
            food_data,
            meal_type
        )
        
        # Получаем дневную статистику
        daily_stats = await get_daily_stats(callback.from_user.id)
        
        # Формируем красивую карточку
        response = meal_card(food_data, agent.user, daily_stats)
        
        # Редактируем сообщение
        await callback.message.edit_text(
            response,
            parse_mode="HTML"
        )
        
        await callback.answer("✅ Приём пищи сохранён!")
        
    except Exception as e:
        logger.error(f"❌ Error in meal_type_callback: {e}")
        await callback.answer(
            "❌ Ошибка сохранения. Попробуйте ещё раз.",
            show_alert=True
        )
