"""
Обработчик AI-ассистента.
Использует intent_classifier для выполнения действий (например, погода) или вызова AI.
Поддерживает диалоги с контекстом. Для выхода используйте /cancel или "выход".
Голос распознаётся только на русском языке.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import asyncio

# Опциональный импорт langdetect (для проверки языка)
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect not installed. Language detection will be skipped.")

from services.deepseek_client import ask_worker_ai, DEFAULT_SYSTEM_PROMPT
from keyboards.reply import get_main_keyboard
from services.cloudflare_ai import transcribe_audio
from services.intent_classifier import classify
from utils.ai_tools import get_weather
from database.db import get_session
from database.models import User
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)

class AIAssistantStates(StatesGroup):
    waiting_for_question = State()

MAX_HISTORY = 10

async def process_voice(message: Message, state: FSMContext, is_global: bool = False):
    """
    Общая логика обработки голосового сообщения.
    Распознаёт только русский язык (проверка через langdetect, если доступно).
    """
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
        # Явно указываем язык - русский
        text = await transcribe_audio(file_data, language="ru")

        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return

        # Проверяем язык, если библиотека доступна
        if LANGDETECT_AVAILABLE:
            try:
                lang = detect(text)
                if lang != 'ru':
                    await message.answer("❌ Пожалуйста, говорите по-русски. Я понимаю только русский язык.")
                    return
            except LangDetectException:
                # Если не удалось определить язык, пропускаем
                pass
        else:
            logger.debug("Language detection skipped (langdetect not installed).")

        await message.answer(f"📝 <b>Распознано:</b>\n{text}", parse_mode="HTML")

        from handlers.universal_text_handler import handle_universal_text
        await handle_universal_text(message, state, text)

    except Exception as e:
        logger.error(f"Ошибка обработки голоса: {e}", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка при обработке голоса.")

@router.message(F.voice)
async def handle_voice_global(message: Message, state: FSMContext):
    """Обрабатывает ЛЮБОЕ голосовое сообщение вне зависимости от состояния."""
    current_state = await state.get_state()
    if current_state and any(x in current_state for x in ['Food', 'Water', 'Activity', 'Steps']):
        return

    await process_voice(message, state, is_global=True)

@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext, user_id: int = None):
    """Вход в режим AI-ассистента."""
    if user_id is None:
        user_id = message.from_user.id

    await state.set_state(AIAssistantStates.waiting_for_question)
    await state.update_data(history=[])
    await message.answer(
        "🤖 <b>Режим AI-ассистента</b>\n\n"
        "Задайте любой вопрос, и я постараюсь на него ответить.\n"
        "Я также могу сообщить погоду, если спросить 'погода в Москве'.\n"
        "Вы можете отправить текст или голосовое сообщение.\n"
        "Для выхода используйте /cancel или напишите 'выход'.\n\n"
        "Чем я могу помочь?",
        parse_mode="HTML"
    )
    logger.info(f"Пользователь {user_id} вошёл в режим AI")

@router.message(AIAssistantStates.waiting_for_question, F.voice)
async def handle_voice_question(message: Message, state: FSMContext):
    """Обработка голоса в режиме /ask."""
    await process_voice(message, state, is_global=False)

@router.message(AIAssistantStates.waiting_for_question, F.text)
async def handle_text_question(message: Message, state: FSMContext):
    """Обработка текста в режиме /ask."""
    text = message.text.strip()
    
    if text.lower() in ['выход', 'выйти', '/cancel']:
        await state.clear()
        await message.answer(
            "👋 Выход из режима AI-ассистента.\n"
            "Используйте меню для навигации.",
            reply_markup=get_main_keyboard()
        )
        return

    await process_ai_query(message, state, text)

async def process_ai_query(message: Message, state: FSMContext, query: str):
    """Основная логика: классификация и выполнение или вызов AI с контекстом."""
    if not query or not query.strip():
        await message.answer("❌ Пустой запрос. Пожалуйста, напишите что-нибудь.")
        return

    data = await state.get_data()
    history = data.get('history', [])

    intent_data = classify(query)
    intent = intent_data.get("intent")

    if intent == "weather":
        await message.answer("⏳ Узнаю погоду...")
        user_id = message.from_user.id
        city = intent_data.get("city")

        if not city:
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = result.scalar_one_or_none()
                if user and user.city:
                    city = user.city
                else:
                    city = "Москва"
                    await message.answer("ℹ️ Город не указан в профиле, используется Москва.")

        weather_info = await get_weather(city)
        await message.answer(weather_info)
        return

    await message.answer("⏳ Думаю...")
    logger.info(f"🚀 Запрос в AI от {message.from_user.id}: {query[:100]}...")

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
            logger.info(f"✅ Ответ AI получен, длина: {len(content)}")
        else:
            await message.answer("❌ Не удалось получить ответ от AI. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Исключение при запросе к AI: {e}", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка при обращении к AI.")
