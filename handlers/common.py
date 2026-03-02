"""
Общие команды и обработчики кнопок главного меню.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from handlers.profile import cmd_profile
from handlers.food import cmd_log_food
from handlers.water import cmd_water
from handlers.progress import cmd_progress
from handlers.shopping import cmd_shopping
from handlers.reminders import cmd_reminders
from handlers.activity import cmd_fitness
from handlers.ai_assistant import cmd_ask

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
        "• 🤖 AI Помощника\n\n"
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
        "/ask — Спросить AI помощника\n\n"
        "<b>🔹 Активность:</b>\n"
        "/fitness — Добавить тренировку\n"
        "/progress — Графики прогресса\n\n"
        "<b>🔹 Организация:</b>\n"
        "/shopping — Списки покупок\n"
        "/reminders — Напоминания\n\n"
        "💡 <b>Быстрые советы:</b>\n"
        "• Отправь фото еды для анализа\n"
        "• Отправь голосовое для вопросов к AI",
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
    await state.clear()
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard()
    )


# ---------- Обработчики кнопок главного меню ----------

@router.message(F.text == "🍽️ Дневник питания")
async def menu_food(message: Message, state: FSMContext):
    await state.clear()
    await cmd_log_food(message, state)


@router.message(F.text == "💧 Вода")
async def menu_water(message: Message, state: FSMContext):
    await state.clear()
    await cmd_water(message, state)


@router.message(F.text == "📊 Прогресс")
async def menu_progress(message: Message, state: FSMContext):
    await state.clear()
    await cmd_progress(message)  # cmd_progress не принимает state


@router.message(F.text == "📋 Списки покупок")
async def menu_shopping(message: Message, state: FSMContext):
    await state.clear()
    await cmd_shopping(message, state)


@router.message(F.text == "🔔 Напоминания")
async def menu_reminders(message: Message, state: FSMContext):
    await state.clear()
    await cmd_reminders(message, state)


@router.message(F.text == "👤 Профиль")
async def menu_profile(message: Message, state: FSMContext):
    await state.clear()
    await cmd_profile(message, state)


@router.message(F.text == "📖 Рецепты")
async def menu_recipes(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🍳 Вы можете попросить AI Помощника предложить рецепт, например: «рецепт из курицы и риса».",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "💬 AI Помощник")
async def menu_ai_assistant(message: Message, state: FSMContext):
    await state.clear()
    await cmd_ask(message, state)


@router.message(F.text == "🏋️ Активность")
async def menu_activity(message: Message, state: FSMContext):
    await state.clear()
    await cmd_fitness(message, state)


@router.message(F.text == "❓ Помощь")
async def menu_help(message: Message, state: FSMContext):
    await state.clear()
    help_text = (
        "🤖 <b>NutriBuddy – ваш персональный помощник</b>\n\n"
        "📌 <b>Основные возможности:</b>\n"
        "• <b>🍽️ Дневник питания</b> – записывайте продукты (можно фото).\n"
        "• <b>💧 Вода</b> – отслеживайте водный баланс.\n"
        "• <b>📊 Прогресс</b> – графики веса, воды, калорий (за день/неделю/месяц).\n"
        "• <b>📋 Списки покупок</b> – создавайте списки и отмечайте товары.\n"
        "• <b>🔔 Напоминания</b> – настройте уведомления о приёмах пищи.\n"
        "• <b>🏋️ Активность</b> – записывайте тренировки (авторасчёт калорий).\n\n"
        "🤖 <b>AI Помощник</b> – умный ассистент, который:\n"
        "• Отвечает на любые вопросы о питании, здоровье, тренировках.\n"
        "• Может добавлять товары в список покупок по команде.\n"
        "• Предлагает рецепты на основе ваших ингредиентов.\n"
        "• Рассказывает погоду в любом городе.\n"
        "• Поддерживает голосовой ввод (отправьте голосовое сообщение).\n\n"
        "📌 <b>Команды:</b>\n"
        "/start – приветствие\n"
        "/help – краткая справка\n"
        "/set_profile – настройка профиля\n"
        "/log_food – записать еду\n"
        "/log_water – добавить воду\n"
        "/log_weight – записать вес\n"
        "/fitness – активность\n"
        "/progress – прогресс\n"
        "/ask – спросить AI\n"
        "/shopping – списки покупок\n"
        "/reminders – напоминания\n"
        "/cancel – отмена\n\n"
        "💡 <b>Совет:</b> Отправьте фото еды – бот распознает продукты и предложит выбрать."
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_keyboard())
