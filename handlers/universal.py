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
        # Проверяем FSM-состояние перед обработкой
        current_state = await state.get_state()
        if current_state:
            logger.info(f"User {user_id} has active FSM state: {current_state}")
            # Если есть активное состояние, не обрабатываем через универсальный обработчик
            return
        
        # Получаем или создаём агента для пользователя
        agent = LangChainAgent.get_for_user(user_id, state)
        
        # Обрабатываем разные типы сообщений
        if message.photo:
            await handle_photo(message, agent, state)
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

async def handle_photo(message: Message, agent: LangChainAgent, state: FSMContext):
    """Обработка фото с параллельным анализом"""
    try:
        # Показываем загрузку
        await message.answer(
            loading_card('photo'),
            parse_mode="HTML"
        )
        
        # Запускаем анализ фото в фоне
        import asyncio
        asyncio.create_task(analyze_photo_parallel(message, agent, state))
        
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
        try:
            text = await transcribe_voice(message)
            
            if text:
                # Удаляем сообщение загрузки
                await loading_msg.delete()
                
                # Передаем текст агенту
                response = await agent.process_message(text)
                await message.answer(response, parse_mode="HTML")
            else:
                await loading_msg.edit_text(
                    "❌ Не удалось распознать речь. Попробуйте ещё раз.",
                    parse_mode="HTML"
                )
        except Exception as transcribe_error:
            logger.error(f"❌ Voice transcription error: {transcribe_error}")
            await loading_msg.edit_text(
                "❌ Ошибка при распознавании речи. Попробуйте отправить текстовое сообщение.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"❌ Error in handle_voice: {e}")
        await message.answer(
            error_card("ai", f"Ошибка обработки голоса: {str(e)}"),
            parse_mode="HTML"
        )

async def analyze_photo_parallel(message: Message, agent: LangChainAgent, state: FSMContext):
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
        
        # Анализируем фото через AI с подписью
        caption = message.caption or ""
        analysis_result = await cf_manager.analyze_food_photo(photo_bytes.read(), caption)
        
        if not analysis_result.get("success"):
            error_msg = analysis_result.get("error", "Не удалось проанализировать фото")
            logger.error(f"Photo analysis failed: {error_msg}")
            await message.answer(
                error_card("ai", f"Не удалось проанализировать фото: {error_msg}. Попробуйте ещё раз."),
                parse_mode="HTML"
            )
            return
        
        # Получаем данные о еде
        food_data = analysis_result["data"]
        
        # Генерируем уникальный ID и сохраняем данные во временное хранилище
        import uuid
        analysis_id = str(uuid.uuid4())[:8]
        
        # Сохраняем данные в FSM
        await state.update_data(photo_analysis={analysis_id: food_data})
        
        # Показываем клавиатуру выбора типа приёма пищи
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="🌅 Завтрак", callback_data=f"meal_type_breakfast_{analysis_id}")
        keyboard.button(text="☀️ Обед", callback_data=f"meal_type_lunch_{analysis_id}")
        keyboard.button(text="🌆 Ужин", callback_data=f"meal_type_dinner_{analysis_id}")
        keyboard.button(text="🍎 Перекус", callback_data=f"meal_type_snack_{analysis_id}")
        keyboard.adjust(2)
        
        await message.answer(
            "📸 <b>Фото проанализировано!</b>\n\n"
            f"🍽️ <b>Распознано:</b> {food_data.get('dish_name', 'Блюдо')}\n\n"
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
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"❌ Voice transcription failed: {error_msg}")
            # Отправляем сообщение об ошибке пользователю
            await message.answer(
                "❌ Не удалось распознать голос. Попробуйте ещё раз или напишите текст.",
                parse_mode="HTML"
            )
            return None
            
    except Exception as e:
        logger.error(f"❌ Error in transcribe_voice: {e}")
        await message.answer(
            "❌ Ошибка при распознавании речи. Попробуйте отправить текстовое сообщение.",
            parse_mode="HTML"
        )
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
        analysis_id = parts[2]
        
        # Получаем данные из FSM
        state_data = await state.get_data()
        photo_analysis = state_data.get("photo_analysis", {})
        food_data = photo_analysis.get(analysis_id)
        
        if not food_data:
            await callback.answer("❌ Данные анализа устарели. Попробуйте отправить фото заново.", show_alert=True)
            return
        
        # Получаем агента
        agent = LangChainAgent.get_for_user(callback.from_user.id, state)
        
        # Сохраняем приём пищи
        from services.food_save_service import food_save_service
        from utils.premium_templates import meal_card
        from utils.helpers import get_daily_stats
        
        # Используем save_food_to_db с детальными ингредиентами
        food_items = food_data.get("food_items", [])
        if not food_items:
            # Если нет детальных ингредиентов, создаем их из food_data
            # Конвертируем старый формат в новый
            food_items = [{
                'name': food_data.get('dish_name', 'Блюдо'),
                'quantity': food_data.get('total_weight', 100),
                'unit': 'г',
                'calories': food_data.get('total_calories', 0),
                'protein': food_data.get('total_protein', 0),
                'fat': food_data.get('total_fat', 0),
                'carbs': food_data.get('total_carbs', 0)
            }]
        
        # Сохраняем через save_food_to_db
        save_result = await food_save_service.save_food_to_db(
            callback.from_user.id,
            food_items,
            meal_type
        )
        
        if not save_result.get("success"):
            await callback.answer(
                f"❌ Ошибка сохранения: {save_result.get('error', 'Неизвестная ошибка')}",
                show_alert=True
            )
            return
        
        # Форматируем данные для карточки
        save_data = {
            'description': ", ".join([
                f"{item.get('quantity','')} {item.get('unit','г')} {item['name']}" 
                for item in food_items
            ]),
            'total_calories': save_result.get('total_calories', 0),
            'total_protein': save_result.get('total_protein', 0),
            'total_fat': save_result.get('total_fat', 0),
            'total_carbs': save_result.get('total_carbs', 0),
            'meal_type': meal_type
        }
        
        # Получаем дневную статистику
        daily_stats = await get_daily_stats(callback.from_user.id)
        
        # Формируем красивую карточку
        response = meal_card(save_data, agent.user, daily_stats)
        
        # Редактируем сообщение
        await callback.message.edit_text(
            response,
            parse_mode="HTML"
        )
        
        await callback.answer("✅ Приём пищи сохранён!")
        
        # Очищаем данные анализа из FSM после сохранения
        photo_analysis = state_data.get("photo_analysis", {})
        if analysis_id in photo_analysis:
            del photo_analysis[analysis_id]
            await state.update_data(photo_analysis=photo_analysis)
            logger.info(f"🧹 Cleaned up photo_analysis for {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in meal_type_callback: {e}")
        await callback.answer(
            "❌ Ошибка сохранения. Попробуйте ещё раз.",
            show_alert=True
        )
