"""
Универсальный AI-ассистент, обрабатывающий текстовые и голосовые запросы.
Использует DeepSeek API с поддержкой function calling.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from services.deepseek_client import ask_deepseek, DEFAULT_SYSTEM_PROMPT
from utils.ai_tools import add_to_shopping_list, suggest_recipe, get_weather
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from services.translator import translate_to_russian
from services.cloudflare_ai import transcribe_audio

router = Router()
logger = logging.getLogger(__name__)


class AIAssistantStates(StatesGroup):
    waiting_for_question = State()


@router.message(Command("ask"))
@router.message(F.text == "💬 AI Помощник")
async def cmd_ask(message: Message, state: FSMContext):
    """Начать диалог с AI-помощником."""
    await state.set_state(AIAssistantStates.waiting_for_question)
    await message.answer(
        "🤖 <b>AI Помощник</b>\n\n"
        "Задайте любой вопрос или дайте команду.\n"
        "Например:\n"
        "• «добавь в список покупок 3 яйца и молоко»\n"
        "• «что приготовить из курицы и картошки?»\n"
        "• «сколько калорий в яблоке?»\n"
        "• «погода в Мурманске»\n\n"
        "Для отмены нажмите ❌ Отмена",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AIAssistantStates.waiting_for_question, F.voice)
async def handle_voice_question(message: Message, state: FSMContext):
    """Обработка голосового вопроса."""
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
        # Передаем распознанный текст в обработчик
        await process_ai_query(message, state, text)
    except Exception as e:
        logger.error(f"Voice recognition error: {e}")
        await message.answer("❌ Ошибка распознавания.")


@router.message(AIAssistantStates.waiting_for_question, F.text)
async def handle_text_question(message: Message, state: FSMContext):
    """Обработка текстового вопроса."""
    await process_ai_query(message, state, message.text)


async def process_ai_query(message: Message, state: FSMContext, query: str):
    """Общая логика обработки запроса к AI."""
    if not query.strip():
        await message.answer("❌ Пожалуйста, напишите что-нибудь.")
        return

    await message.answer("⏳ Думаю...")

    # Формируем системный промпт с учётом пользователя (можно добавить имя)
    system_prompt = (
        "Ты — NutriBuddy AI, дружелюбный помощник. "
        "Отвечай на русском, кратко и по делу. "
        "Если пользователь просит добавить в список покупок, используй инструмент add_to_shopping_list. "
        "Если просит рецепт, используй suggest_recipe или сгенерируй рецепт сам. "
        "Если просит погоду, используй get_weather. "
        "Если не уверен — честно скажи."
    )

    # Вызываем DeepSeek
    response = await ask_deepseek(
        prompt=query,
        user_id=message.from_user.id,
        system_prompt=system_prompt,
        max_tokens=1500
    )

    if "error" in response:
        await message.answer(response["error"])
        return

    # Обрабатываем возможные вызовы инструментов
    if "choices" in response and response["choices"]:
        choice = response["choices"][0]
        if "message" in choice:
            msg = choice["message"]
            # Если есть вызовы инструментов
            if "tool_calls" in msg:
                for tool_call in msg["tool_calls"]:
                    func_name = tool_call["function"]["name"]
                    args = json.loads(tool_call["function"]["arguments"])
                    result = await execute_tool(func_name, args, message.from_user.id)
                    # Отправляем результат как обычное сообщение
                    await message.answer(result)
                # После выполнения инструментов не отправляем основной ответ, т.к. результат уже отправлен
                await state.clear()
                return
            else:
                # Обычный текстовый ответ
                answer = msg.get("content", "")
                if answer:
                    await message.answer(answer, parse_mode="HTML")
                else:
                    await message.answer("✅ Готово.")
    else:
        await message.answer("❌ Не удалось получить ответ.")

    await state.clear()


async def execute_tool(func_name: str, args: dict, telegram_id: int) -> str:
    """Выполняет вызванный инструмент и возвращает результат."""
    if func_name == "add_to_shopping_list":
        items = args.get("items", [])
        return await add_to_shopping_list(telegram_id, items)
    elif func_name == "suggest_recipe":
        ingredients = args.get("ingredients", "")
        # Здесь можно либо вернуть маркер, либо вызвать генерацию рецепта через DeepSeek ещё раз.
        # Проще всего: вернуть, что рецепт будет сгенерирован, но мы уже в контексте AI, поэтому
        # AI может сам выдать рецепт, не вызывая инструмент. Оставим заглушку.
        return f"🍳 Рецепт на основе {ingredients} скоро будет готов. А пока попробуйте поискать в интернете 😉"
    elif func_name == "get_weather":
        city = args.get("city", "")
        return await get_weather(city)
    else:
        return f"❌ Неизвестный инструмент: {func_name}"
