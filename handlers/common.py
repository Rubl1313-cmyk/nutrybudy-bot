"""
Общие команды: /start, /help, /cancel, и интерактивное меню помощи.
Добавлена навигация по категориям и AI помощник.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from keyboards.inline import (
    get_food_menu, get_water_activity_menu, get_progress_menu,
    get_lists_menu, get_profile_menu
)
from handlers.profile import cmd_profile, edit_profile, display_profile
from handlers.food import cmd_log_food
from handlers.water import cmd_water
from handlers.progress import cmd_progress
from handlers.shopping import cmd_shopping
from handlers.reminders import cmd_reminders
from handlers.activity import cmd_fitness, process_steps_input
from handlers.ai_assistant import cmd_ask  # импорт AI команды
from handlers.meal_plan import cmd_meal_plan
from utils.states import StepsStates

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Приветственное сообщение с полным описанием возможностей."""
    await state.clear()
    welcome_text = (
        "✨ <b>Добро пожаловать в NutriBuddy!</b> ✨\n\n"
        "Я — твой персональный помощник в мире здорового питания и активного образа жизни.\n\n"
        "🔹 <b>Что я умею:</b>\n"
        "• 👤 Настраивать профиль и считать нормы\n"
        "• 🍽️ Вести дневник питания (по фото или тексту)\n"
        "• 💧 Отслеживать воду\n"
        "• 🏋️ Записывать тренировки и шаги\n"
        "• 📊 Строить графики прогресса\n"
        "• 📋 Создавать списки покупок\n"
        "• 🔔 Устанавливать напоминания\n"
        "• 🤖 Отвечать на вопросы через AI\n"
        "• 🍽️ Планировать питание и распределять калории\n\n"
        "🎯 <b>Начни с настройки профиля:</b>\n"
        "Нажми 👤 Профиль или введи /set_profile\n\n"
        "💡 <b>Совет:</b> Отправь фото еды — я распознаю продукты!\n"
        "Для подробной информации нажми ❓ Помощь."
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    """Вызывает интерактивное меню помощи."""
    await state.clear()
    await show_help_menu(message)

async def show_help_menu(event: Message | CallbackQuery):
    """Отображает главное меню помощи с инлайн-кнопками."""
    text = (
        "📚 <b>Разделы помощи</b>\n\n"
        "Выберите интересующую тему:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Питание", callback_data="help_food_category")],
        [InlineKeyboardButton(text="💧 Вода и активность", callback_data="help_water_category")],
        [InlineKeyboardButton(text="📊 Прогресс", callback_data="help_progress_category")],
        [InlineKeyboardButton(text="📋 Списки и напоминания", callback_data="help_lists_category")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="help_profile_category")],
        [InlineKeyboardButton(text="🤖 AI Помощник", callback_data="help_ai_category")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="help_close")]
    ])

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:  # CallbackQuery
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await event.answer()

@router.callback_query(F.data.startswith("help_"))
async def help_callbacks(callback: CallbackQuery):
    data = callback.data
    text = ""
    if data == "help_food_category":
        text = (
            "🍽️ <b>Питание</b>\n\n"
            "• 📸 Отправить фото еды – бот распознает продукты и предложит выбрать вес.\n"
            "• ✏️ Ввести продукты вручную – например, «курица, рис, брокколи».\n"
            "• 🍽️ План питания – сгенерировать меню на день.\n"
            "• 💬 AI Помощник – задать вопрос о питании, рецептах и т.д."
        )
    elif data == "help_water_category":
        text = (
            "💧 <b>Вода и активность</b>\n\n"
            "• 💧 Записать воду – можно выбрать объём или ввести число.\n"
            "• 👟 Записать шаги – введите количество шагов.\n"
            "• 🏃 Записать активность – бег, ходьба, велосипед и др."
        )
    elif data == "help_progress_category":
        text = (
            "📊 <b>Прогресс</b>\n\n"
            "• Просмотр статистики по калориям, воде, весу и активности за день, неделю или месяц.\n"
            "• Графики и прогресс-бары."
        )
    elif data == "help_lists_category":
        text = (
            "📋 <b>Списки и напоминания</b>\n\n"
            "• 📋 Список покупок – добавление товаров, изменение количества, отметка о покупке.\n"
            "• 🔔 Напоминания – создание напоминаний о приёме пищи, воде и других делах."
        )
    elif data == "help_profile_category":
        text = (
            "👤 <b>Профиль</b>\n\n"
            "• Просмотр и редактирование ваших данных (вес, рост, возраст, пол, активность, цель, город).\n"
            "• Бот автоматически рассчитывает нормы калорий, БЖУ и воды."
        )
    elif data == "help_ai_category":
        text = (
            "🤖 <b>AI Помощник</b>\n\n"
            "• Задайте любой вопрос о питании, здоровье, тренировках или рецептах.\n"
            "• Может сообщить погоду в любом городе.\n"
            "• Поддерживает голосовые сообщения."
        )
    elif data == "help_close":
        await callback.message.delete()
        await callback.answer()
        return

    if text:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="help_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

@router.callback_query(F.data == "help_back")
async def help_back_callback(callback: CallbackQuery):
    """Возврат в главное меню помощи."""
    await show_help_menu(callback)

@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего действия."""
    await state.clear()
    await message.answer(
        "❌ <b>Действие отменено</b>\n\n"
        "Используй кнопки меню для навигации.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "🏠 Главное меню")
async def cmd_main_menu(message: Message, state: FSMContext):
    """Возврат в главное меню."""
    await state.clear()
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "🍽️ Питание")
async def show_food_category(message: Message, state: FSMContext):
    await message.answer(
        "🍽️ <b>Раздел питания</b>\n\n"
        "Выберите действие:",
        reply_markup=get_food_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "💧 Вода и активность")
async def show_water_activity_category(message: Message, state: FSMContext):
    await message.answer(
        "💧 <b>Вода и активность</b>\n\n"
        "Выберите действие:",
        reply_markup=get_water_activity_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Прогресс и статистика")
async def show_progress_category(message: Message, state: FSMContext):
    await message.answer(
        "📊 <b>Прогресс и статистика</b>\n\n"
        "Выберите период:",
        reply_markup=get_progress_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "📋 Списки и напоминания")
async def show_lists_category(message: Message, state: FSMContext):
    await message.answer(
        "📋 <b>Списки и напоминания</b>\n\n"
        "Выберите действие:",
        reply_markup=get_lists_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "👤 Профиль и настройки")
async def show_profile_category(message: Message, state: FSMContext):
    await message.answer(
        "👤 <b>Профиль и настройки</b>\n\n"
        "Выберите действие:",
        reply_markup=get_profile_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "❓ Помощь")
async def menu_help(message: Message, state: FSMContext):
    await state.clear()
    await show_help_menu(message)

# ✅ НОВЫЙ ОБРАБОТЧИК ДЛЯ КНОПКИ "🤖 AI Помощник"
@router.message(F.text == "🤖 AI Помощник")
async def menu_ai_assistant(message: Message, state: FSMContext):
    await cmd_ask(message, state)  # вызываем команду AI

# ========== Обработчики навигационных callback'ов с передачей user_id ==========

@router.callback_query(F.data == "menu_back")
async def menu_back_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_food_photo")
async def menu_food_photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📸 Отправьте фото еды")
    await callback.answer()

@router.callback_query(F.data == "menu_food_manual")
async def menu_food_manual(callback: CallbackQuery, state: FSMContext):
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_meal_plan")
async def menu_meal_plan(callback: CallbackQuery, state: FSMContext):
    await cmd_meal_plan(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_ai")
async def menu_ai(callback: CallbackQuery, state: FSMContext):
    await cmd_ask(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_water")
async def menu_water(callback: CallbackQuery, state: FSMContext):
    await cmd_water(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_activity")
async def menu_activity(callback: CallbackQuery, state: FSMContext):
    await cmd_fitness(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_steps")
async def menu_steps(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsStates.waiting_for_steps)
    # Для шагов отдельная функция, которая принимает message, user_id не нужен
    await callback.message.answer("👟 Введите количество шагов (только число):")
    await callback.answer()

@router.callback_query(F.data == "menu_shopping")
async def menu_shopping(callback: CallbackQuery, state: FSMContext):
    await cmd_shopping(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_reminders")
async def menu_reminders(callback: CallbackQuery, state: FSMContext):
    await cmd_reminders(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_profile_view")
async def menu_profile_view(callback: CallbackQuery, state: FSMContext):
    # Вызываем универсальную функцию отображения профиля без state
    await display_profile(callback, callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_profile_edit")
async def menu_profile_edit(callback: CallbackQuery, state: FSMContext):
    await edit_profile(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()
