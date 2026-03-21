"""
handlers/reply_handlers.py
Обработчики кнопок главного меню
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu

logger = logging.getLogger(__name__)
router = Router()

# === Главное меню ===

@router.message(F.text.lower().in_(["👤 профиль", "профиль"]))
async def profile_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Профиль"""
    logger.info(f"🔍 REPLY HANDLER: Profile button pressed by user {message.from_user.id}")
    await state.clear()
    
    from handlers.profile import cmd_profile
    await cmd_profile(message, state)

@router.message(F.text.lower().in_(["📊 прогресс", "прогресс"]))
async def progress_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Прогресс"""
    logger.info(f"🔍 REPLY HANDLER: Progress button pressed by user {message.from_user.id}")
    await state.clear()
    
    from handlers.progress import cmd_progress
    await cmd_progress(message, state)

@router.message(F.text.lower().in_(["🏆 достижения", "достижения"]))
async def achievements_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Достижения"""
    logger.info(f"🔍 REPLY HANDLER: Achievements button pressed by user {message.from_user.id}")
    await state.clear()
    
    from handlers.achievements import cmd_achievements
    await cmd_achievements(message)

@router.message(F.text.lower().in_(["🤖 AI ассистент", "AI ассистент", "ai ассистент"]))
async def ai_assistant_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки AI Ассистент"""
    logger.info(f"🔍 REPLY HANDLER: AI Assistant button pressed by user {message.from_user.id}")
    
    from handlers.ai_assistant import cmd_ai_assistant
    await cmd_ai_assistant(message, state)

@router.message(F.text.lower().in_(["❓ помощь", "помощь"]))
async def help_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Помощь"""
    logger.info(f"🔍 REPLY HANDLER: Help button pressed by user {message.from_user.id}")
    await state.clear()
    
    from handlers.help import cmd_help
    await cmd_help(message, state)

# === Навигация ===

@router.message(F.text.lower().in_(["🔙 назад", "назад"]))
async def back_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Назад"""
    logger.info(f"🔍 REPLY HANDLER: Back button pressed by user {message.from_user.id}")
    await state.clear()
    
    await message.answer(
        "🏠 <b>Главное меню</b>\n\nВыберите раздел:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["🏠 главное меню", "главное меню"]))
async def main_menu_button_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Главное меню"""
    logger.info(f"🔍 REPLY HANDLER: Main Menu button pressed by user {message.from_user.id}")
    await state.clear()
    
    from handlers.common import cmd_start
    await cmd_start(message, state)
