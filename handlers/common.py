"""
Общие команды: /start, /help, /cancel, главное меню
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Привет! Я NutriBuddy</b>\n\n"
        "🤖 <b>Твой персональный помощник</b> для:\n"
        "• 🍽️ Контроля питания\n"
        "• 💧 Водного баланса\n"
        "• 📊 Отслеживания прогресса\n"
        "• 🏋️ Фитнеса и активности\n"
        "• 📋 Списков покупок\n"
        "• 📖 Генерации рецептов\n\n"
        "🎯 <b>Начни с настройки профиля:</b>\n"
        "Нажми 👤 Профиль или /set_profile\n\n"
        "💡 <b>Совет:</b> Отправь фото еды для автоматического анализа!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📚 <b>Доступные команды:</b>\n\n"
        "<b>🔹 Основные:</b>\n"
        "/start — Запустить бота\n"
        "/help — Эта справка\n"
        "/cancel — Отменить действие\n\n"
        "<b>🔹 Профиль:</b>\n"
        "/set_profile — Настроить профиль\n"
        "/log_weight — Записать вес\n\n"
        "<b>🔹 Питание:</b>\n"
        "/log_food — Записать приём пищи\n"
        "/log_water — Добавить воду\n"
        "/recipe — Генерация рецепта\n\n"
        "<b>🔹 Активность:</b>\n"
        "/fitness — Добавить тренировку\n"
        "/progress — Графики прогресса\n\n"
        "<b>🔹 Организация:</b>\n"
        "/shopping — Списки покупок\n"
        "/reminders — Напоминания\n\n"
        "💡 <b>Быстрые советы:</b>\n"
        "• Отправь фото еды для анализа\n"
        "• Отправь голосовое для распознавания\n"
        "• Используй кнопки меню для быстрого доступа",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ <b>Действие отменено</b>\n\n"
        "Используй кнопки меню для навигации.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text == "🏠 Главное меню")
async def cmd_main_menu(message: Message, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard()
    )
