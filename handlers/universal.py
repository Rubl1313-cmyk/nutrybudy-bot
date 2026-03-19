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

@router.message(~F.command & ~F.text.contains(["🍽️", "💧", "🏃‍♂️", "⚖️", "📊", "🍽️", "🏆", "🤖", "👤", "⚙️", "❓", "🏠", "🚶", "🚶‍♀️", "🏃", "🏃‍♂️", "✏️", "📈", "🧠"]))
async def universal_handler(message: Message, state: FSMContext):
    """
    Универсальный обработчик всех сообщений (кроме команд)
    """
    user_id = message.from_user.id
    logger.info(f"🔍 UNIVERSAL HANDLER: Processing message from user {user_id}: {message.text[:50]}...")
    
    try:
        # Проверяем FSM-состояние перед обработкой
        current_state = await state.get_state()
        
        # Если пользователь в состоянии, не обрабатываем здесь
        if current_state and not current_state.startswith("AIStates:"):
            # Пользователь в процессе другого действия
            return
        
        # Инициализируем семафор для пользователя если нужно
        if user_id not in user_photo_semaphores:
            user_photo_semaphores[user_id] = asyncio.Semaphore(1)
        
        # Обработка в зависимости от типа контента
        if message.photo:
            await handle_photo_message(message, state)
        elif message.text:
            await handle_text_message(message, state)
        elif message.voice:
            await handle_voice_message(message, state)
        elif message.video:
            await handle_video_message(message, state)
        elif message.document:
            await handle_document_message(message, state)
        else:
            # Неизвестный тип контента
            await handle_unknown_message(message, state)
            
    except Exception as e:
        logger.error(f"Error in universal handler for user {user_id}: {e}")
        await message.answer(
            error_card(
                "Произошла ошибка обработки",
                "Попробуйте еще раз или используйте /help"
            )
        )

async def handle_photo_message(message: Message, state: FSMContext):
    """Обработка фото сообщений"""
    user_id = message.from_user.id
    
    async with user_photo_semaphores[user_id]:
        try:
            # Показываем загрузку
            loading_msg = await message.answer(
                loading_card("AI анализирует фото...")
            )
            
            # Инициализируем LangChain агент
            agent = LangChainAgent()
            
            # Получаем фото
            photo = message.photo[-1]  # Самое большое фото
            file_info = await message.bot.get_file(photo.file_id)
            
            # Скачиваем фото
            downloaded_file = await message.bot.download_file(file_info.file_path)
            
            # Обрабатываем фото через агент
            result = await agent.process_photo(
                user_id=user_id,
                photo_data=downloaded_file,
                filename=file_info.file_path
            )
            
            # Удаляем сообщение о загрузке
            await loading_msg.delete()
            
            # Отправляем результат
            if result.get('success'):
                await message.answer(
                    result['message'],
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    error_card(
                        "Не удалось распознать фото",
                        result.get('error', "Попробуйте сделать фото более качественным")
                    )
                )
                
        except Exception as e:
            logger.error(f"Error processing photo for user {user_id}: {e}")
            
            # Удаляем сообщение о загрузке если существует
            try:
                await loading_msg.delete()
            except:
                pass
            
            await message.answer(
                error_card(
                    "Ошибка обработки фото",
                    "Попробуйте еще раз"
                )
            )

async def handle_text_message(message: Message, state: FSMContext):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Проверяем FSM состояние
    current_state = await state.get_state()
    
    if current_state and current_state.startswith("AIStates:"):
        # Пользователь в диалоге с AI, обрабатываем как вопрос
        await handle_ai_question(message, state)
        return
    
    # Инициализируем LangChain агент для текста
    agent = LangChainAgent()
    
    try:
        # Показываем загрузку для сложных запросов
        if len(text) > 50 or "?" in text:
            loading_msg = await message.answer(
                loading_card("AI обрабатывает запрос...")
            )
        else:
            loading_msg = None
        
        # Обрабатываем текст через агент
        result = await agent.process_text(
            user_id=user_id,
            text=text
        )
        
        # Удаляем сообщение о загрузке
        if loading_msg:
            await loading_msg.delete()
        
        # Отправляем результат
        if result.get('success'):
            response_text = result['message']
            
            # Добавляем клавиатуру если нужно
            if result.get('suggestions'):
                builder = InlineKeyboardBuilder()
                for suggestion in result['suggestions']:
                    builder.add(
                        InlineKeyboardButton(
                            text=suggestion['text'],
                            callback_data=suggestion['callback_data']
                        )
                    )
                builder.adjust(1)
                
                await message.answer(
                    response_text,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    response_text,
                    parse_mode="HTML"
                )
        else:
            await message.answer(
                error_card(
                    "Не удалось обработать запрос",
                    result.get('error', "Попробуйте переформулировать")
                )
            )
            
    except Exception as e:
        logger.error(f"Error processing text for user {user_id}: {e}")
        
        # Удаляем сообщение о загрузке если существует
        if loading_msg:
            try:
                await loading_msg.delete()
            except:
                pass
        
        await message.answer(
            error_card(
                "Ошибка обработки текста",
                "Попробуйте еще раз"
            )
        )

async def handle_voice_message(message: Message, state: FSMContext):
    """Обработка голосовых сообщений"""
    user_id = message.from_user.id
    
    try:
        # Показываем загрузку
        loading_msg = await message.answer(
            loading_card("AI распознает голос...")
        )
        
        # Инициализируем LangChain агент
        agent = LangChainAgent()
        
        # Получаем голосовое сообщение
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        
        # Скачиваем файл
        downloaded_file = await message.bot.download_file(file_info.file_path)
        
        # Обрабатываем голос через агент
        result = await agent.process_voice(
            user_id=user_id,
            voice_data=downloaded_file,
            filename=file_info.file_path
        )
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Отправляем результат
        if result.get('success'):
            await message.answer(
                result['message'],
                parse_mode="HTML"
            )
        else:
            await message.answer(
                error_card(
                    "Не удалось распознать голос",
                    result.get('error', "Попробуйте говорить четче")
                )
            )
            
    except Exception as e:
        logger.error(f"Error processing voice for user {user_id}: {e}")
        
        try:
            await loading_msg.delete()
        except:
            pass
        
        await message.answer(
            error_card(
                "Ошибка распознавания голоса",
                "Попробуйте еще раз"
            )
        )

async def handle_video_message(message: Message, state: FSMContext):
    """Обработка видео сообщений"""
    user_id = message.from_user.id
    
    try:
        # Показываем загрузку
        loading_msg = await message.answer(
            loading_card("AI анализирует видео...")
        )
        
        # Инициализируем LangChain агент
        agent = LangChainAgent()
        
        # Получаем видео
        video = message.video
        file_info = await message.bot.get_file(video.file_id)
        
        # Скачиваем файл
        downloaded_file = await message.bot.download_file(file_info.file_path)
        
        # Обрабатываем видео через агент
        result = await agent.process_video(
            user_id=user_id,
            video_data=downloaded_file,
            filename=file_info.file_path
        )
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Отправляем результат
        if result.get('success'):
            await message.answer(
                result['message'],
                parse_mode="HTML"
            )
        else:
            await message.answer(
                error_card(
                    "Не удалось обработать видео",
                    result.get('error', "Видео может быть слишком длинным")
                )
            )
            
    except Exception as e:
        logger.error(f"Error processing video for user {user_id}: {e}")
        
        try:
            await loading_msg.delete()
        except:
            pass
        
        await message.answer(
            error_card(
                "Ошибка обработки видео",
                "Попробуйте отправить фото вместо видео"
            )
        )

async def handle_document_message(message: Message, state: FSMContext):
    """Обработка документов"""
    user_id = message.from_user.id
    
    try:
        # Проверяем тип документа
        document = message.document
        
        if document.mime_type and document.mime_type.startswith('image/'):
            # Это изображение, обрабатываем как фото
            await handle_photo_document(message, state)
        else:
            # Другой тип документа
            await message.answer(
                error_card(
                    "Неподдерживаемый тип документа",
                    "Пожалуйста, отправляйте фото или текст"
                )
            )
            
    except Exception as e:
        logger.error(f"Error processing document for user {user_id}: {e}")
        await message.answer(
            error_card(
                "Ошибка обработки документа",
                "Попробуйте другой формат"
            )
        )

async def handle_photo_document(message: Message, state: FSMContext):
    """Обработка изображения как документа"""
    user_id = message.from_user.id
    
    async with user_photo_semaphores[user_id]:
        try:
            # Показываем загрузку
            loading_msg = await message.answer(
                loading_card("AI анализирует изображение...")
            )
            
            # Инициализируем LangChain агент
            agent = LangChainAgent()
            
            # Получаем документ
            document = message.document
            file_info = await message.bot.get_file(document.file_id)
            
            # Скачиваем файл
            downloaded_file = await message.bot.download_file(file_info.file_path)
            
            # Обрабатываем фото через агент
            result = await agent.process_photo(
                user_id=user_id,
                photo_data=downloaded_file,
                filename=file_info.file_path
            )
            
            # Удаляем сообщение о загрузке
            await loading_msg.delete()
            
            # Отправляем результат
            if result.get('success'):
                await message.answer(
                    result['message'],
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    error_card(
                        "Не удалось распознать изображение",
                        result.get('error', "Попробуйте сделать фото более качественным")
                    )
                )
                
        except Exception as e:
            logger.error(f"Error processing photo document for user {user_id}: {e}")
            
            try:
                await loading_msg.delete()
            except:
                pass
            
            await message.answer(
                error_card(
                    "Ошибка обработки изображения",
                    "Попробуйте еще раз"
                )
            )

async def handle_unknown_message(message: Message, state: FSMContext):
    """Обработка неизвестных типов сообщений"""
    await message.answer(
        error_card(
            "Неподдерживаемый формат",
            "Пожалуйста, отправляйте фото, текст или голосовые сообщения"
        )
    )

async def handle_ai_question(message: Message, state: FSMContext):
    """Обработка вопроса в диалоге с AI"""
    from handlers.ai_assistant import handle_ai_conversation
    
    # Перенаправляем в обработчик AI ассистента
    await handle_ai_conversation(message, state)

@router.callback_query()
async def universal_callback_handler(callback: CallbackQuery, state: FSMContext):
    """
    Универсальный обработчик callback'ов
    """
    user_id = callback.from_user.id
    
    try:
        # Проверяем FSM состояние
        current_state = await state.get_state()
        
        # Инициализируем LangChain агент для callback'ов
        agent = LangChainAgent()
        
        # Обрабатываем callback через агент
        result = await agent.process_callback(
            user_id=user_id,
            callback_data=callback.data,
            message=callback.message
        )
        
        # Отправляем результат
        if result.get('success'):
            if result.get('edit_message'):
                await callback.message.edit_text(
                    result['message'],
                    reply_markup=result.get('reply_markup'),
                    parse_mode="HTML"
                )
            else:
                await callback.message.answer(
                    result['message'],
                    reply_markup=result.get('reply_markup'),
                    parse_mode="HTML"
                )
        else:
            await callback.answer(
                result.get('error', "Произошла ошибка"),
                show_alert=True
            )
            
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback handler for user {user_id}: {e}")
        await callback.answer(
            "Произошла ошибка",
            show_alert=True
        )

# Очистка семафоров при отключении пользователя
async def cleanup_user_semaphores(user_id: int):
    """Очистка семафоров пользователя"""
    if user_id in user_photo_semaphores:
        del user_photo_semaphores[user_id]
