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

@router.message(F.text.lower().in_(["🍽️ записать приём пищи", "записать приём пищи", "записать прием пищи"]))
async def food_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Food button pressed by user {message.from_user.id}")
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

@router.message(F.text.lower().in_(["💧 записать воду", "записать воду"]))
async def water_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Water button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.drinks import cmd_water
    await cmd_water(message, state)

@router.message(F.text.lower().in_(["📊 прогресс", "прогресс"]))
async def progress_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Progress button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.progress import cmd_progress
    await cmd_progress(message, state)

@router.message(F.text.lower().in_(["🤖 спросить ai", "спросить ai"]))
async def ai_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: AI button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.ai_assistant import cmd_ask
    await cmd_ask(message, state)


@router.message(F.text.lower().regexp(r'^(профиль|👤 профиль)$'))
async def profile_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Profile button pressed by user {message.from_user.id}")
    # Вызываем команду показа профиля – она сама отправит нужное сообщение
    await cmd_profile(message, state)

@router.message(F.text.lower().in_(["помощь", "❓ помощь"]))
async def help_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Help button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_help(message, state)  # Вызываем реальную команду помощи с state

# === Дополнительные кнопки (опционально) ===

@router.message(F.text.lower().in_(["⚖️ записать вес", "записать вес"]))
async def weight_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Weight button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_weight(message, state)  # Вызываем реальную команду веса с state

@router.message(F.text.lower().in_(["🏃 записать активность", "записать активность"]))
async def activity_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Activity button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "🏃‍♂️ <b>Записать активность</b>\n\n"
        "Опишите активность (например: «бег 30 минут»).",
        parse_mode="HTML"
    )

# === Навигация ===

@router.message(F.text.lower().in_(["🏠 главное меню", "главное меню"]))
async def back_to_main_menu(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Main menu button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )
