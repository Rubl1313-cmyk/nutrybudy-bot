"""
Обработчик AI-ассистента.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import json

# Новый импорт – используем ask_worker_ai из обновлённого клиента
from services.deepseek_client import ask_worker_ai, DEFAULT_SYSTEM_PROMPT
from utils.ai_tools import add_to_shopping_list, get_weather
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from services.cloudflare_ai import transcribe_audio

router = Router()
logger = logging.getLogger(__name__)


class AIAssistantStates(StatesGroup):
    waiting_for_question = State()


@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    """Вход в режим AI-ассистента."""
    await state.set_state(AIAssistantStates.waiting_for_question)
    # Сообщение уже отправлено в common.py, поэтому здесь ничего не пишем


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
        await process_ai_query(message, state, text)
    except Exception as e:
        logger.error(f"Voice error: {e}")
        await message.answer("❌ Ошибка распознавания.")


@router.message(AIAssistantStates.waiting_for_question, F.text)
async def handle_text_question(message: Message, state: FSMContext):
    await process_ai_query(message, state, message.text)


async def process_ai_query(message: Message, state: FSMContext, query: str):
    """Основная логика отправки запроса в AI и обработки ответа."""
    if not query.strip():
        await message.answer("❌ Пустой запрос.")
        return

    await message.answer("⏳ Думаю...")
    # Используем новую функцию ask_worker_ai
    response = await ask_worker_ai(
        prompt=query,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        model="@cf/qwen/qwen3-32b-instruct",
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
