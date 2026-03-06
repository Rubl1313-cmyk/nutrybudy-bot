"""
Обработчик AI-ассистента.
Поддерживает два режима:
- Однократные ответы (без истории, автоматический выход)
- Диалоговый режим (с историей, выход по команде)
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import asyncio

from services.deepseek_client import ask_worker_ai, DEFAULT_SYSTEM_PROMPT
from keyboards.reply import get_main_keyboard
from services.cloudflare_ai import transcribe_audio
from services.intent_classifier import classify
from utils.ai_tools import get_weather
from utils.helpers import normalize_exit_command
from database.db import get_session
from database.models import User
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)

class AIAssistantStates(StatesGroup):
    waiting_for_question = State()  # диалоговый режим

MAX_HISTORY = 10

# ==================== ОДНОКРАТНЫЕ ОТВЕТЫ (ВНЕ ДИАЛОГА) ====================
async def process_single_ai_query(message: Message, query: str):
    """
    Однократный запрос к AI без сохранения истории.
    Используется для ответов на вопросы, заданные вне диалогового режима.
    """
    if not query or not query.strip():
        await message.answer("❌ Пустой запрос. Пожалуйста, напишите что-нибудь.")
        return

    await message.answer("⏳ Думаю...")
    logger.info(f"🚀 Однократный запрос в AI от {message.from_user.id}: {query[:100]}...")

    try:
        response = await ask_worker_ai(
            prompt=query,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            model="@cf/qwen/qwen2.5-coder-32b-instruct",
            max_tokens=3000
        )

        if "error" in response:
            error_msg = response["error"]
            logger.error(f"Ошибка AI: {error_msg}")
            await message.answer(f"❌ Ошибка при обращении к AI: {error_msg}")
        elif response.get("choices"):
            content = response["choices"][0]["message"]["content"]
            if len(content) > 4000:
                parts = [content[i:i+4000] for i in range(0, len(content), 4000)]
                for part in parts:
                    await message.answer(part, parse_mode="HTML")
            else:
                await message.answer(content, parse_mode="HTML")
            logger.info(f"✅ Однократный ответ AI получен, длина: {len(content)}")
        else:
            await message.answer("❌ Не удалось получить ответ от AI. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Исключение при запросе к AI: {e}", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка при обращении к AI.")

# ==================== ДИАЛОГОВЫЙ РЕЖИМ ====================
async def process_voice(message: Message, state: FSMContext):
    """Обработка голоса в диалоговом режиме."""
    await message.answer("🎤 Распознаю речь...")
    try:
        voice = message.voice
        if voice.duration > 120:
            await message.answer("⏱️ Слишком длинное голосовое сообщение. Пожалуйста, запишите короче (до 2 минут).")
            return

        file_info = await message.bot.get_file(voice.file_id)
        try:
            file_bytes = await asyncio.wait_for(
                message.bot.download_file(file_info.file_path),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            await message.answer("❌ Таймаут при скачивании голосового сообщения. Попробуйте ещё раз.")
            return

        file_data = file_bytes.read()
        text = await transcribe_audio(file_data, language="ru")

        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return

        await message.answer(f"📝 <b>Распознано:</b>\n{text}", parse_mode="HTML")

        # Отправляем в диалоговый обработчик
        await process_dialog_query(message, state, text)

    except Exception as e:
        logger.error(f"Ошибка обработки голоса: {e}", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка при обработке голоса.")

async def process_dialog_query(message: Message, state: FSMContext, query: str):
    """Обработка запроса в диалоговом режиме с сохранением истории."""
    data = await state.get_data()
    history = data.get('history', [])

    system_prompt = DEFAULT_SYSTEM_PROMPT
    if history:
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in history[-MAX_HISTORY:]
        ])
        system_prompt += f"\n\nИстория диалога:\n{history_text}"

    try:
        response = await ask_worker_ai(
            prompt=query,
            system_prompt=system_prompt,
            model="@cf/qwen/qwen2.5-coder-32b-instruct",
            max_tokens=3000
        )

        if "error" in response:
            error_msg = response["error"]
            logger.error(f"Ошибка AI: {error_msg}")
            await message.answer(f"❌ Ошибка при обращении к AI: {error_msg}")
        elif response.get("choices"):
            content = response["choices"][0]["message"]["content"]
            
            # Сохраняем историю
            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": content})
            if len(history) > MAX_HISTORY * 2:
                history = history[-MAX_HISTORY*2:]
            await state.update_data(history=history)

            if len(content) > 4000:
                parts = [content[i:i+4000] for i in range(0, len(content), 4000)]
                for part in parts:
                    await message.answer(part, parse_mode="HTML")
            else:
                await message.answer(content, parse_mode="HTML")
            logger.info(f"✅ Диалоговый ответ AI получен, длина: {len(content)}")
        else:
            await message.answer("❌ Не удалось получить ответ от AI. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Исключение при запросе к AI: {e}", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка при обращении к AI.")

# ==================== ВХОД В ДИАЛОГОВЫЙ РЕЖИМ ====================
@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    """Вход в режим диалога с AI-ассистентом."""
    user_id = message.from_user.id

    await state.set_state(AIAssistantStates.waiting_for_question)
    await state.update_data(history=[])
    await message.answer(
        "🤖 <b>Режим AI-ассистента (диалог)</b>\n\n"
        "Задавайте любые вопросы, я буду помнить контекст беседы.\n"
        "Для выхода из режима напишите 'выход' или используйте /cancel.\n\n"
        "Чем я могу помочь?",
        parse_mode="HTML"
    )
    logger.info(f"Пользователь {user_id} вошёл в диалоговый режим AI")

# ==================== ОБРАБОТКА В ДИАЛОГОВОМ РЕЖИМЕ ====================
@router.message(AIAssistantStates.waiting_for_question, F.voice)
async def handle_voice_dialog(message: Message, state: FSMContext):
    """Голос в диалоговом режиме."""
    await process_voice(message, state)

@router.message(AIAssistantStates.waiting_for_question, F.text)
async def handle_text_dialog(message: Message, state: FSMContext):
    """Текст в диалоговом режиме."""
    raw_text = message.text
    text = raw_text.strip()
    normalized = normalize_exit_command(text)

    # Проверка выхода из диалога
    if normalized in ['выход', 'выйти', 'выходи', 'завершить', 'закончить', 'стоп', 'хватит', '/cancel']:
        await state.clear()
        await message.answer(
            "👋 Выход из режима диалога.\n"
            "Используйте меню для навигации.",
            reply_markup=get_main_keyboard()
        )
        return

    await process_dialog_query(message, state, text)

# ==================== ОБРАБОТКА ГОЛОСА ВНЕ ДИАЛОГА ====================
@router.message(F.voice)
async def handle_voice_global(message: Message, state: FSMContext):
    """Голос вне диалога – распознаём и обрабатываем как текст."""
    current_state = await state.get_state()
    if current_state and any(x in current_state for x in ['Food', 'Water', 'Activity', 'Steps']):
        return

    await message.answer("🎤 Распознаю речь...")
    try:
        voice = message.voice
        if voice.duration > 120:
            await message.answer("⏱️ Слишком длинное голосовое сообщение. Пожалуйста, запишите короче (до 2 минут).")
            return

        file_info = await message.bot.get_file(voice.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        text = await transcribe_audio(file_data, language="ru")

        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return

        await message.answer(f"📝 <b>Распознано:</b>\n{text}", parse_mode="HTML")

        # Передаём в универсальный обработчик (там будет классификация)
        from handlers.universal_text_handler import handle_universal_text
        await handle_universal_text(message, state, text)

    except Exception as e:
        logger.error(f"Ошибка обработки голоса: {e}", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка при обработке голоса.")
