"""
Обработчик AI-ассистента.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import json

from services.deepseek_client import ask_deepseek, DEFAULT_SYSTEM_PROMPT
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
    # Сообщение уже отправлено в common.py при нажатии кнопки, поэтому здесь можно ничего не писать


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
    """Основная логика отправки запроса в DeepSeek и обработки ответа."""
    if not query.strip():
        await message.answer("❌ Пустой запрос.")
        return

    await message.answer("⏳ Думаю...")
    response = await ask_deepseek(
        prompt=query,
        user_id=message.from_user.id,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        max_tokens=1500
    )

    if "error" in response:
        await message.answer(response["error"])
    elif response.get("choices"):
        choice = response["choices"][0]["message"]
        if choice.get("tool_calls"):
            for tool_call in choice["tool_calls"]:
                func_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                result = await execute_tool(func_name, args, message.from_user.id)
                await message.answer(result)
        else:
            await message.answer(choice.get("content", "✅ Готово."))
    else:
        await message.answer("❌ Не удалось получить ответ.")

    await state.clear()


async def execute_tool(func_name: str, args: dict, telegram_id: int) -> str:
    if func_name == "add_to_shopping_list":
        return await add_to_shopping_list(telegram_id, args.get("items", []))
    if func_name == "get_weather":
        return await get_weather(args.get("city", ""))
    return f"❌ Неизвестная команда: {func_name}"
