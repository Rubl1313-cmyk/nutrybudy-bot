"""
handlers/reply_handlers.py
Обработчики для новых reply-кнопок (исправленные фильтры с эмодзи)
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from handlers.profile import cmd_profile
from handlers.progress import cmd_progress
from handlers.drinks import cmd_water
from handlers.weight import cmd_weight
from handlers.ai_assistant import cmd_ask
from handlers.common import cmd_help
from keyboards.reply_v2 import get_main_keyboard_v2

logger = logging.getLogger(__name__)
router = Router()

# === Основные кнопки ===

@router.message(F.text.startswith("🍽️"))
async def food_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 🍽️ button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "🍽️ <b>Записать приём пищи</b>\n\n"
        "Отправьте фото блюда или напишите что вы съели.\n\n"
        "Примеры:\n"
        "• 200г гречки с курицей\n"
        "• салат цезарь\n"
        "• яблоко 2шт",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("💧"))
async def water_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 💧 button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_water(message)  # Вызываем реальную команду воды

@router.message(F.text.startswith("🤖"))
async def ai_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 🤖 button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_ask(message)  # Вызываем реальную команду AI

@router.message(F.text.startswith("📊"))
async def progress_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 📊 button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_progress(message)  # Вызываем реальную команду прогресса

@router.message(F.text.startswith("👤"))
async def profile_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 👤 button pressed by user {message.from_user.id}")
    # Вызываем команду показа профиля – она сама отправит нужное сообщение
    await cmd_profile(message, state)

@router.message(F.text.startswith("❓"))
async def help_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: ❓ button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_help(message)  # Вызываем реальную команду помощи

# === Дополнительные кнопки (опционально) ===

@router.message(F.text.startswith("⚖️"))
async def weight_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: ⚖️ button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_weight(message)  # Вызываем реальную команду веса

@router.message(F.text.startswith("🏃"))
async def activity_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 🏃 button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "🏃‍♂️ <b>Записать активность</b>\n\n"
        "Опишите активность (например: «бег 30 минут»).",
        parse_mode="HTML"
    )

# === Навигация ===

@router.message(F.text == "🏠 Главное меню")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

# === Общий обработчик для неизвестных сообщений ===

@router.message()
async def unknown_message_handler(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        return  # команды обрабатываются в других роутерах
    await message.answer(
        "❌ Пожалуйста, используйте кнопки меню.",
        reply_markup=get_main_keyboard_v2()
    )
