"""
handlers/help.py
Обработчики помощи
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu, get_help_menu

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text.lower().in_(["❓ помощь", "помощь"]))
async def cmd_help(message: Message, state: FSMContext):
    """Показать помощь"""
    await state.clear()
    
    text = "❓ <b>Помощь</b>\n\n"
    text += "Выберите раздел:\n"
    
    await message.answer(text, reply_markup=get_help_menu(), parse_mode="HTML")

@router.message(F.text.lower().in_(["📋 команды", "команды"]))
async def help_commands_handler(message: Message, state: FSMContext):
    """Список команд"""
    text = "📋 <b>Команды бота</b>\n\n"
    text += "/start - 🚀 Запуск бота\n"
    text += "/set_profile - 👤 Настроить профиль\n"
    text += "/progress - 📊 Посмотреть прогресс\n"
    text += "/achievements - 🏆 Достижения\n"
    text += "/ask - 🤖 AI Ассистент\n\n"
    text += "💡 <b>Совет:</b> Вы также можете использовать кнопки меню!"
    
    await message.answer(text, reply_markup=get_help_menu(), parse_mode="HTML")

@router.message(F.text.lower().in_(["🚀 возможности", "возможности"]))
async def help_features_handler(message: Message, state: FSMContext):
    """Возможности бота"""
    text = "🚀 <b>Возможности NutriBuddy</b>\n\n"
    text += "🍽️ <b>Учёт питания:</b>\n"
    text += "• Распознавание еды по фото\n"
    text += "• Автоматический расчёт КБЖУ\n"
    text += "• Отслеживание приёмов пищи\n\n"
    
    text += "💧 <b>Контроль воды:</b>\n"
    text += "• Учёт выпитой жидкости\n"
    text += "• Напоминания о питье\n\n"
    
    text += "🏃 <b>Активность:</b>\n"
    text += "• Запись тренировок\n"
    text += "• Подсчёт сожжённых калорий\n\n"
    
    text += "📊 <b>Прогресс:</b>\n"
    text += "• Детальная статистика\n"
    text +="• Графики и тренды\n\n"
    
    text += "🤖 <b>AI Ассистент:</b>\n"
    text += "• Ответы на вопросы\n"
    text += "• Рекомендации по питанию\n"
    text += "• Помощь в достижении целей\n\n"
    
    text += "🏆 <b>Геймификация:</b>\n"
    text += "• Достижения и награды\n"
    text +="• Система уровней\n\n"
    
    await message.answer(text, reply_markup=get_help_menu(), parse_mode="HTML")
