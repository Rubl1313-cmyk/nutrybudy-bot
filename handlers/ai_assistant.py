"""
Обработчик AI-ассистента.
Использует intent_classifier для выполнения действий или вызова AI.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from services.deepseek_client import ask_worker_ai, DEFAULT_SYSTEM_PROMPT
from services.intent_classifier import classify
from utils.ai_tools import get_weather, add_to_shopping_list
from handlers.reminders import quick_create_reminder
from handlers.shopping import add_to_shopping_list as shopping_add
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from services.cloudflare_ai import transcribe_audio
from handlers.universal_text_handler import handle_universal_text

router = Router()
logger = logging.getLogger(__name__)


class AIAssistantStates(StatesGroup):
    waiting_for_question = State()


@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    """Вход в режим AI-ассистента."""
    await state.set_state(AIAssistantStates.waiting_for_question)
    # Приветственное сообщение уже отправлено в common.py


@router.message(AIAssistantStates.waiting_for_question, F.voice)
async def handle_voice_question(message: Message, state: FSMContext):
    await message.answer("🎤 Распознаю речь...")
    try:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        text = await transcribe_audio(file_data)
        if not text:
            await message.answer("❌ Не удалось распознать речь.")
            return
        await message.answer(f"📝 <b>Распознано:</b>\n{text}", parse_mode="HTML")
        
        # 🔥 ВАЖНО: отправляем текст в универсальный обработчик
        from handlers.universal_text_handler import handle_universal_text
        await handle_universal_text(message, state, text)
    except Exception as e:
        logger.error(f"Voice error: {e}")
        await message.answer("❌ Ошибка распознавания.")


@router.message(AIAssistantStates.waiting_for_question, F.text)
async def handle_text_question(message: Message, state: FSMContext):
    await process_ai_query(message, state, message.text)


async def process_ai_query(message: Message, state: FSMContext, query: str):
    """Основная логика: классификация и выполнение."""
    if not query.strip():
        await message.answer("❌ Пустой запрос.")
        await state.clear()
        return

    intent_data = classify(query)
    intent = intent_data.get("intent")

    # ----- ПОГОДА -----
    if intent == "weather":
        city = intent_data.get("city", "Москва")
        result = await get_weather(city)
        await message.answer(result, parse_mode="HTML")
        await state.clear()
        return

    # ----- СПИСОК ПОКУПОК -----
    elif intent == "shopping":
        items_text = intent_data.get("text", query)
        # Удаляем ключевые слова (они уже удалены в классификаторе)
        await shopping_add(message, items_text)
        await message.answer("✅ Добавлено в список покупок.")
        await state.clear()
        return

    # ----- НАПОМИНАНИЯ -----
    elif intent == "reminder":
        title = intent_data.get("reminder_title")
        time = intent_data.get("reminder_time")
        if title and time:
            await quick_create_reminder(message.from_user.id, title, time, "daily")
            await message.answer(f"✅ Напоминание «{title}» на {time} создано.")
        else:
            await message.answer("⏰ Укажите время, например: «напомни позвонить в 18:00»")
        await state.clear()
        return

    # ----- РЕЦЕПТЫ (можно направить в AI) -----
    # Они попадут в общий AI

    # ----- ОБЩИЙ AI (intent == "ai") -----
    else:
        await message.answer("⏳ Думаю...")
        logger.info(f"🚀 Отправка в AI: {query}")
        response = await ask_worker_ai(
            prompt=query,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            model="@cf/qwen/qwen2.5-coder-32b-instruct",
            max_tokens=1500
        )
        if "error" in response:
            await message.answer(response["error"])
        elif response.get("choices"):
            content = response["choices"][0]["message"]["content"]
            await message.answer(content, parse_mode="HTML")
        else:
            await message.answer("❌ Не удалось получить ответ.")
        await state.clear()
