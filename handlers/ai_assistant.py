"""
Обработчик AI-ассистента.
Использует intent_classifier для выполнения действий или вызова AI.
Улучшена обработка голоса и добавлены проверки ошибок.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import asyncio

from services.deepseek_client import ask_worker_ai, DEFAULT_SYSTEM_PROMPT
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from services.cloudflare_ai import transcribe_audio

router = Router()
logger = logging.getLogger(__name__)

class AIAssistantStates(StatesGroup):
    waiting_for_question = State()

async def process_voice(message: Message, state: FSMContext, is_global: bool = False):
    """
    Общая логика обработки голосового сообщения.
    is_global=True означает, что обработчик вызван вне состояния /ask.
    """
    await message.answer("🎤 Распознаю речь...")
    try:
        voice = message.voice
        # Проверка длительности голосового сообщения (опционально)
        if voice.duration > 120:  # больше 2 минут
            await message.answer("⏱️ Слишком длинное голосовое сообщение. Пожалуйста, запишите короче (до 2 минут).")
            return

        file_info = await message.bot.get_file(voice.file_id)
        # Асинхронное скачивание с таймаутом
        try:
            file_bytes = await asyncio.wait_for(
                message.bot.download_file(file_info.file_path),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            await message.answer("❌ Таймаут при скачивании голосового сообщения. Попробуйте ещё раз.")
            return

        file_data = file_bytes.read()
        text = await transcribe_audio(file_data)

        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return

        await message.answer(f"📝 <b>Распознано:</b>\n{text}", parse_mode="HTML")

        # Если это глобальный обработчик (не в режиме /ask), передаём в универсальный
        from handlers.universal_text_handler import handle_universal_text
        await handle_universal_text(message, state, text)

    except Exception as e:
        logger.error(f"Ошибка обработки голоса: {e}", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка при обработке голоса.")

# Глобальный обработчик голосовых сообщений (работает всегда)
@router.message(F.voice)
async def handle_voice_global(message: Message, state: FSMContext):
    """Обрабатывает ЛЮБОЕ голосовое сообщение вне зависимости от состояния."""
    await process_voice(message, state, is_global=True)

@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    """Вход в режим AI-ассистента."""
    await state.set_state(AIAssistantStates.waiting_for_question)
    await message.answer(
        "🤖 <b>Режим AI-ассистента</b>\n\n"
        "Задайте любой вопрос, и я постараюсь на него ответить.\n"
        "Вы можете отправить текст или голосовое сообщение.\n\n"
        "Для выхода используйте /cancel",
        parse_mode="HTML"
    )
    logger.info(f"Пользователь {message.from_user.id} вошёл в режим AI")

@router.message(AIAssistantStates.waiting_for_question, F.voice)
async def handle_voice_question(message: Message, state: FSMContext):
    """Обработка голоса в режиме /ask."""
    await process_voice(message, state, is_global=False)

@router.message(AIAssistantStates.waiting_for_question, F.text)
async def handle_text_question(message: Message, state: FSMContext):
    """Обработка текста в режиме /ask."""
    await process_ai_query(message, state, message.text)

async def process_ai_query(message: Message, state: FSMContext, query: str):
    """Основная логика отправки запроса в AI и обработки ответа."""
    if not query or not query.strip():
        await message.answer("❌ Пустой запрос. Пожалуйста, напишите что-нибудь.")
        return

    await message.answer("⏳ Думаю...")
    logger.info(f"🚀 Запрос в AI от {message.from_user.id}: {query[:100]}...")

    try:
        response = await ask_worker_ai(
            prompt=query,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            model="@cf/qwen/qwen2.5-coder-32b-instruct",
            max_tokens=1500
        )

        if "error" in response:
            error_msg = response["error"]
            logger.error(f"Ошибка AI: {error_msg}")
            await message.answer(f"❌ Ошибка при обращении к AI: {error_msg}")
        elif response.get("choices"):
            content = response["choices"][0]["message"]["content"]
            # Проверяем длину ответа (Telegram лимит 4096 символов)
            if len(content) > 4000:
                # Разбиваем на части, если слишком длинный
                parts = [content[i:i+4000] for i in range(0, len(content), 4000)]
                for part in parts:
                    await message.answer(part, parse_mode="HTML")
            else:
                await message.answer(content, parse_mode="HTML")
            logger.info(f"✅ Ответ AI получен, длина: {len(content)}")
        else:
            await message.answer("❌ Не удалось получить ответ от AI. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Исключение при запросе к AI: {e}", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка при обращении к AI.")
    finally:
        # Выходим из режима /ask после ответа (или ошибки)
        await state.clear()
