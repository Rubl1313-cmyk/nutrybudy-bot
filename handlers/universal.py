"""
handlers/universal.py
Универсальный обработчик всех сообщений через LangChain Agent
"""
import asyncio
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.langchain_agent import LangChainAgent
from utils.premium_templates import loading_card, error_card

logger = logging.getLogger(__name__)
router = Router()

# Семафоры для обработки фото по пользователям
user_photo_semaphores = {}

@router.message(~F.command)
async def universal_handler(message: Message, state: FSMContext):
    """
    Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ²Ñ�ĞµÑ… Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğ¹ (ĞºÑ€Ğ¾Ğ¼Ğµ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´)
    """
    user_id = message.from_user.id
    
    try:
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ FSM-Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ğµ Ğ¿ĞµÑ€ĞµĞ´# Проверяем FSM-состояние перед обработкой
        current_state = await state.get_state()
        if current_state:
            logger.info(f"User {user_id} has active FSM state: {current_state}")
            # Если есть активное состояние, сообщаем пользователю о необходимости завершить действие
            await message.answer(
                "⚠️ <b>У вас есть незавершённое действие</b>\n\n"
                "Пожалуйста, завершите текущее действие или нажмите /cancel для отмены.\n"
                "После этого вы сможете продолжить работу с ботом.",
                parse_mode="HTML"
            )
            return
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¸Ğ»Ğ¸ Ñ�Ğ¾Ğ·Ğ´Ğ°Ñ‘Ğ¼ Ğ°Ğ³ĞµĞ½Ñ‚Ğ° Ğ´Ğ»Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
        agent = LangChainAgent.get_for_user(user_id, state)
        
        # Ğ�Ğ±Ñ€Ğ°Ğ±Ğ°Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ñ€Ğ°Ğ·Ğ½Ñ‹Ğµ Ñ‚Ğ¸Ğ¿Ñ‹ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğ¹
        if message.photo:
            await handle_photo(message, agent, state)
        elif message.voice:
            await handle_voice(message, agent)
        elif message.text:
            # Сначала пробуем обработать через food_clarification
            from handlers.food_clarification import handle_food_text
            if await handle_food_text(message, state):
                return  # Если food_clarification обработал, выходим
            # Иначе передаем в AI агент
            await agent.handle_text(message.text, message)
        else:
            await message.answer(
                "ğŸ¤– Ğ¯ Ğ¿Ğ¾ĞºĞ° Ğ¿Ğ¾Ğ½Ğ¸Ğ¼Ğ°Ñ� Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ñ‚ĞµĞºÑ�Ñ‚, Ñ„Ğ¾Ñ‚Ğ¾ Ğ¸ Ğ³Ğ¾Ğ»Ğ¾Ñ�Ğ¾Ğ²Ñ‹Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ�.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"â�Œ Error in universal_handler: {e}")
        await message.answer(
            error_card("general", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ¸: {str(e)}"),
            parse_mode="HTML"
        )

async def handle_photo(message: Message, agent: LangChainAgent, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ñ„Ğ¾Ñ‚Ğ¾ Ñ� Ğ¿Ğ°Ñ€Ğ°Ğ»Ğ»ĞµĞ»ÑŒĞ½Ñ‹Ğ¼ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¾Ğ¼"""
    try:
        # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ·Ğ°Ğ³Ñ€ÑƒĞ·ĞºÑƒ
        await message.answer(
            loading_card('photo'),
            parse_mode="HTML"
        )
        
        # Проверяем, не обрабатывается ли уже фото для этого пользователя
        user_id = message.from_user.id
        if user_id not in user_photo_semaphores:
            user_photo_semaphores[user_id] = asyncio.Semaphore(1)
        
        # Запускаем анализ фото с семафором
        import asyncio
        asyncio.create_task(analyze_photo_with_semaphore(message, agent, state, user_photo_semaphores[user_id]))
        
    except Exception as e:
        logger.error(f"â�Œ Error in handle_photo: {e}")
        await message.answer(
            error_card("ai", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ñ„Ğ¾Ñ‚Ğ¾: {str(e)}"),
            parse_mode="HTML"
        )

async def handle_voice(message: Message, agent: LangChainAgent):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ³Ğ¾Ğ»Ğ¾Ñ�Ğ¾Ğ²Ñ‹Ñ… Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğ¹"""
    try:
        # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ·Ğ°Ğ³Ñ€ÑƒĞ·ĞºÑƒ
        loading_msg = await message.answer(
            loading_card('voice'),
            parse_mode="HTML"
        )
        
        # Ğ¢Ñ€Ğ°Ğ½Ñ�ĞºÑ€Ğ¸Ğ±Ğ¸Ñ€ÑƒĞµĞ¼ Ğ³Ğ¾Ğ»Ğ¾Ñ�
        try:
            text = await transcribe_voice(message)
            
            if text:
                # Ğ£Ğ´Ğ°Ğ»Ñ�ĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ Ğ·Ğ°Ğ³Ñ€ÑƒĞ·ĞºĞ¸
                await loading_msg.delete()
                
                # ĞŸĞµÑ€ĞµĞ´Ğ°ĞµĞ¼ Ñ‚ĞµĞºÑ�Ñ‚ Ğ°Ğ³ĞµĞ½Ñ‚Ñƒ
                response = await agent.process_message(text)
                await message.answer(response, parse_mode="HTML")
            else:
                await loading_msg.edit_text(
                    "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ñ‚ÑŒ Ñ€ĞµÑ‡ÑŒ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ·.",
                    parse_mode="HTML"
                )
        except Exception as transcribe_error:
            logger.error(f"â�Œ Voice transcription error: {transcribe_error}")
            await loading_msg.edit_text(
                "â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ğ²Ğ°Ğ½Ğ¸Ğ¸ Ñ€ĞµÑ‡Ğ¸. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ¸Ñ‚ÑŒ Ñ‚ĞµĞºÑ�Ñ‚Ğ¾Ğ²Ğ¾Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"â�Œ Error in handle_voice: {e}")
        await message.answer(
            error_card("ai", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ¸ Ğ³Ğ¾Ğ»Ğ¾Ñ�Ğ°: {str(e)}"),
            parse_mode="HTML"
        )

async def analyze_photo_with_semaphore(message: Message, agent: LangChainAgent, state: FSMContext, semaphore: asyncio.Semaphore):
    """
    ĞŸĞ°Ñ€Ğ°Ğ»Ğ»ĞµĞ»ÑŒĞ½Ñ‹Ğ¹ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ· Ñ„Ğ¾Ñ‚Ğ¾ Ñ� Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ¾Ğ¼ Ñ‚Ğ¸Ğ¿Ğ° Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸ Ñ� Ñ�ĞµĞ¼Ğ°Ñ„Ğ¾Ñ€Ğ¾Ğ¼
    """
    async with semaphore:
        try:
            from services.cloudflare_manager import cf_manager
            from services.food_save_service import food_save_service
            from utils.premium_templates import meal_card
            
            # Ğ¡ĞºĞ°Ñ‡Ğ¸Ğ²Ğ°ĞµĞ¼ Ñ„Ğ¾Ñ‚Ğ¾
            file = await message.bot.get_file(message.photo[-1].file_id)
            photo_bytes = await message.bot.download_file(file.file_path)
            
            # Ğ�Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€ÑƒĞµĞ¼ Ñ„Ğ¾Ñ‚Ğ¾ Ñ‡ĞµÑ€ĞµĞ· AI Ñ� Ğ¿Ğ¾Ğ´Ğ¿Ğ¸Ñ�ÑŒÑ�
            caption = message.caption or ""
            analysis_result = await cf_manager.analyze_food_photo(photo_bytes.read(), caption)
            
            if not analysis_result.get("success"):
                error_msg = analysis_result.get("error", "Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¿Ñ€Ğ¾Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒ Ñ„Ğ¾Ñ‚Ğ¾")
                logger.error(f"Photo analysis failed: {error_msg}")
                await message.answer(
                    error_card("ai", f"Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¿Ñ€Ğ¾Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒ Ñ„Ğ¾Ñ‚Ğ¾: {error_msg}. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ·."),
                    parse_mode="HTML"
                )
                return
            
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾ ĞµĞ´Ğµ
            food_data = analysis_result["data"]
            
            # Ğ“ĞµĞ½ĞµÑ€Ğ¸Ñ€ÑƒĞµĞ¼ ÑƒĞ½Ğ¸ĞºĞ°Ğ»ÑŒĞ½Ñ‹Ğ¹ ID Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ²Ğ¾Ğ²Ñ€ĞµĞ¼Ğ½Ğ¾Ğµ Ñ…Ñ€Ğ°Ğ½Ğ¸Ğ»Ğ¸Ñ‰Ğµ
            import uuid
            analysis_id = str(uuid.uuid4())[:8]
            
            # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ² FSM
            await state.update_data(photo_analysis={analysis_id: food_data})
            
            # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ñƒ Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ñ‚Ğ¸Ğ¿Ğ° Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸
            keyboard = InlineKeyboardBuilder()
            keyboard.button(text="ğŸŒ… Ğ—Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº", callback_data=f"meal_type_breakfast_{analysis_id}")
            keyboard.button(text="â˜€ï¸� Ğ�Ğ±ĞµĞ´", callback_data=f"meal_type_lunch_{analysis_id}")
            keyboard.button(text="ğŸŒ† Ğ£Ğ¶Ğ¸Ğ½", callback_data=f"meal_type_dinner_{analysis_id}")
            keyboard.button(text="ğŸ�� ĞŸĞµÑ€ĞµĞºÑƒÑ�", callback_data=f"meal_type_snack_{analysis_id}")
            keyboard.adjust(2)
            
            await message.answer(
                "ğŸ“¸ <b>Ğ¤Ğ¾Ñ‚Ğ¾ Ğ¿Ñ€Ğ¾Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¾!</b>\n\n"
                f"ğŸ�½ï¸� <b>Ğ Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ğ½Ğ¾:</b> {food_data.get('dish_name', 'Ğ‘Ğ»Ñ�Ğ´Ğ¾')}\n\n"
                "ğŸ�½ï¸� <b>Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ñ‚Ğ¸Ğ¿ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸:</b>",
                reply_markup=keyboard.as_markup(),
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"â�Œ Error in analyze_photo_with_semaphore: {e}")
            await message.answer(
                error_card("ai", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ñ„Ğ¾Ñ‚Ğ¾: {str(e)}"),
                parse_mode="HTML"
            )

async def transcribe_voice(message: Message) -> str:
    """
    Ğ¢Ñ€Ğ°Ğ½Ñ�ĞºÑ€Ğ¸Ğ±Ğ°Ñ†Ğ¸Ñ� Ğ³Ğ¾Ğ»Ğ¾Ñ�Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ�
    """
    from utils.retry_utils import with_retry
    
    @with_retry(max_attempts=3, delay_seconds=1)
    async def _transcribe():
        from services.cloudflare_manager import cf_manager
        
        # Ğ¡ĞºĞ°Ñ‡Ğ¸Ğ²Ğ°ĞµĞ¼ Ğ³Ğ¾Ğ»Ğ¾Ñ�Ğ¾Ğ²Ğ¾Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ
        file = await message.bot.get_file(message.voice.file_id)
        voice_bytes = await message.bot.download_file(file.file_path)
        
        # Ğ¢Ñ€Ğ°Ğ½Ñ�ĞºÑ€Ğ¸Ğ±Ğ¸Ñ€ÑƒĞµĞ¼ Ñ‡ĞµÑ€ĞµĞ· Cloudflare Whisper
        result = await cf_manager.transcribe_audio(voice_bytes.read())
        
        if result.get("success"):
            text = result.get("text", "")
            logger.info(f"ğŸ�¤ Voice transcribed: {text[:50]}...")
            return text
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"â�Œ Voice transcription failed: {error_msg}")
            # Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ Ğ¾Ğ± Ğ¾ÑˆĞ¸Ğ±ĞºĞµ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            await message.answer(
                "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ñ‚ÑŒ Ğ³Ğ¾Ğ»Ğ¾Ñ�. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ· Ğ¸Ğ»Ğ¸ Ğ½Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ñ‚ĞµĞºÑ�Ñ‚.",
                parse_mode="HTML"
            )
            return None
    
    try:
        return await _transcribe()
    except Exception as e:
        logger.error(f"â�Œ Error in transcribe_voice: {e}")
        await message.answer(
            "â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ğ²Ğ°Ğ½Ğ¸Ğ¸ Ñ€ĞµÑ‡Ğ¸. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ¸Ñ‚ÑŒ Ñ‚ĞµĞºÑ�Ñ‚Ğ¾Ğ²Ğ¾Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ.",
            parse_mode="HTML"
        )
        return None

# Callback Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ñ‚Ğ¸Ğ¿Ğ° Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸
@router.callback_query(F.data.startswith("meal_type_"))
async def meal_type_callback(callback: CallbackQuery, state: FSMContext):
    """
    Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ñ‚Ğ¸Ğ¿Ğ° Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸ Ğ¿Ğ¾Ñ�Ğ»Ğµ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ñ„Ğ¾Ñ‚Ğ¾
    """
    try:
        # ĞŸĞ°Ñ€Ñ�Ğ¸Ğ¼ callback_data
        parts = callback.data.split("_", 2)
        meal_type = parts[1]  # breakfast, lunch, dinner, snack
        analysis_id = parts[2]
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¸Ğ· FSM
        state_data = await state.get_data()
        photo_analysis = state_data.get("photo_analysis", {})
        food_data = photo_analysis.get(analysis_id)
        
        if not food_data:
            await callback.answer("â�Œ Ğ”Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° ÑƒÑ�Ñ‚Ğ°Ñ€ĞµĞ»Ğ¸. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ¸Ñ‚ÑŒ Ñ„Ğ¾Ñ‚Ğ¾ Ğ·Ğ°Ğ½Ğ¾Ğ²Ğ¾.", show_alert=True)
            return
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ°Ğ³ĞµĞ½Ñ‚Ğ°
        agent = LangChainAgent.get_for_user(callback.from_user.id, state)
        
        # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸
        from services.food_save_service import food_save_service
        from utils.premium_templates import meal_card
        from utils.helpers import get_daily_stats
        
        # Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ save_food_to_db Ñ� Ğ´ĞµÑ‚Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¼Ğ¸ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸
        food_items = food_data.get("food_items", [])
        
        # Ğ’Ñ�ĞµĞ³Ğ´Ğ° ĞºĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ Ğ¸Ğ· Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ° _per_100g Ğ² Ğ¸Ñ‚Ğ¾Ğ³Ğ¾Ğ²Ñ‹Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ�
        converted_food_items = []
        for item in food_items:
            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼, ĞµÑ�Ñ‚ÑŒ Ğ»Ğ¸ ĞºĞ»Ñ�Ñ‡Ğ¸ _per_100g
            if 'calories_per_100g' in item:
                weight = item.get('quantity', 0)
                factor = weight / 100.0
                
                converted_item = {
                    'name': item.get('name', 'Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚'),
                    'quantity': weight,
                    'unit': item.get('unit', 'Ğ³'),
                    'calories': item.get('calories_per_100g', 0) * factor,
                    'protein': item.get('protein_per_100g', 0) * factor,
                    'fat': item.get('fat_per_100g', 0) * factor,
                    'carbs': item.get('carbs_per_100g', 0) * factor
                }
                converted_food_items.append(converted_item)
            else:
                # Ğ•Ñ�Ğ»Ğ¸ ÑƒĞ¶Ğµ Ğ² Ğ¿Ñ€Ğ°Ğ²Ğ¸Ğ»ÑŒĞ½Ğ¾Ğ¼ Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğµ, Ğ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¾ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼
                converted_food_items.append(item)
        
        # Ğ•Ñ�Ğ»Ğ¸ Ğ¿Ğ¾Ñ�Ğ»Ğµ ĞºĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ°Ñ†Ğ¸Ğ¸ Ğ½ĞµÑ‚ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ¾Ğ², Ñ�Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ğ¸Ğ· food_data
        if not converted_food_items:
            converted_food_items = [{
                'name': food_data.get('dish_name', 'Ğ‘Ğ»Ñ�Ğ´Ğ¾'),
                'quantity': food_data.get('total_weight', 100),
                'unit': 'Ğ³',
                'calories': food_data.get('total_calories', 0),
                'protein': food_data.get('total_protein', 0),
                'fat': food_data.get('total_fat', 0),
                'carbs': food_data.get('total_carbs', 0)
            }]
        
        # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ‡ĞµÑ€ĞµĞ· save_food_to_db Ñ� ĞºĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¼Ğ¸ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸
        save_result = await food_save_service.save_food_to_db(
            callback.from_user.id,
            converted_food_items,
            meal_type
        )
        
        if not save_result.get("success"):
            await callback.answer(
                f"â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�: {save_result.get('error', 'Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ°Ñ� Ğ¾ÑˆĞ¸Ğ±ĞºĞ°')}",
                show_alert=True
            )
            return
        
        # Ğ¤Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ´Ğ»Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ¸
        save_data = {
            'description': ", ".join([
                f"{item.get('quantity','')} {item.get('unit','Ğ³')} {item['name']}" 
                for item in food_items
            ]),
            'total_calories': save_result.get('total_calories', 0),
            'total_protein': save_result.get('total_protein', 0),
            'total_fat': save_result.get('total_fat', 0),
            'total_carbs': save_result.get('total_carbs', 0),
            'meal_type': meal_type
        }
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ´Ğ½ĞµĞ²Ğ½ÑƒÑ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ
        daily_stats = await get_daily_stats(callback.from_user.id)
        
        # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ ĞºÑ€Ğ°Ñ�Ğ¸Ğ²ÑƒÑ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºÑƒ
        response = meal_card(save_data, agent.user, daily_stats)
        
        # Ğ ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ
        await callback.message.edit_text(
            response,
            parse_mode="HTML"
        )
        
        await callback.answer("âœ… ĞŸÑ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ‘Ğ½!")
        
        # Ğ�Ñ‡Ğ¸Ñ‰Ğ°ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ğ¸Ğ· FSM Ğ¿Ğ¾Ñ�Ğ»Ğµ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�
        photo_analysis = state_data.get("photo_analysis", {})
        if analysis_id in photo_analysis:
            del photo_analysis[analysis_id]
            await state.update_data(photo_analysis=photo_analysis)
            logger.info(f"ğŸ§¹ Cleaned up photo_analysis for {analysis_id}")
        
    except Exception as e:
        logger.error(f"â�Œ Error in meal_type_callback: {e}")
        await callback.answer(
            "â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ·.",
            show_alert=True
        )
