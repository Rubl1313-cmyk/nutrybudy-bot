"""
handlers/reply_handlers.py
Обработчики для новых reply-кнопок (исправленные фильтры с эмодзи)
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from handlers.profile import cmd_profile  # <-- импортируем функцию профиля
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
        "Напишите, что вы съели, или отправьте фото блюда.\n\n"
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
    await message.answer(
        "💧 <b>Записать воду</b>\n\n"
        "Сколько воды вы выпили?\n\n"
        "Примеры:\n"
        "• 250мл\n"
        "• 1 стакан\n"
        "• 500мл бутылка",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("🤖"))
async def ai_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 🤖 button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "🤖 <b>Спросить AI</b>\n\n"
        "Задайте любой вопрос о питании, тренировках или здоровье.\n\n"
        "Примеры:\n"
        "• Сколько калорий в гречке?\n"
        "• Помоги составить меню на день\n"
        "• Какой белок лучше для мышц?",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("📊"))
async def progress_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 📊 button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "📊 <b>Прогресс</b>\n\n"
        "📈 Ваш прогресс за сегодня:\n"
        "Калории: 1,250 / 2,000 ккал\n"
        "Белки: 65g / 150g\n"
        "Жиры: 45g / 65g\n"
        "Углеводы: 150g / 250g\n\n"
        "💪 Отлично продолжайте!",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("👤"))
async def profile_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: 👤 button pressed by user {message.from_user.id}")
    # Вызываем команду показа профиля – она сама отправит нужное сообщение
    await cmd_profile(message, state)

@router.message(F.text.startswith("❓"))
async def help_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❓ <b>Помощь</b>\n\n"
        "Используйте /help для подробной справки.",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

# === Дополнительные кнопки (опционально) ===

@router.message(F.text.startswith("⚖️"))
async def weight_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "⚖️ <b>Записать вес</b>\n\n"
        "Введите ваш вес в кг (например: 70.5):",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("🏃"))
async def activity_button_handler(message: Message, state: FSMContext):
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
