"""
Общие команды: /start, /help, /cancel, кнопки меню
✅ Работают в ЛЮБОМ состоянии (приоритет над FSM)
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Приветствие — сбрасывает ВСЕ состояния"""
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
    """Справка — сбрасывает состояние"""
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
    """Отмена — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "❌ <b>Действие отменено</b>\n\n"
        "Используй кнопки меню для навигации.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text == "🏠 Главное меню")
async def cmd_main_menu(message: Message, state: FSMContext):
    """Главное меню — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "🏠 <b>Главное меню</b>",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


# =============================================================================
# 🎯 КНОПКИ ГЛАВНОГО МЕНЮ (работают в ЛЮБОМ состоянии!)
# =============================================================================
# 🔥 ВАЖНО: Эти хендлеры должны быть ПОСЛЕ CommandStart и Command("cancel")
# но ДО специфичных FSM хендлеров в других файлах

@router.message(F.text == "🍽️ Дневник питания")
async def menu_food(message: Message, state: FSMContext):
    """Дневник питания — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "🍽️ <b>Дневник питания</b>\n\n"
        "Выберите тип приёма пищи или отправьте фото еды:",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "💧 Вода")
async def menu_water(message: Message, state: FSMContext):
    """Вода — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "💧 <b>Водный баланс</b>\n\n"
        "Сколько воды вы выпили?\n"
        "Выберите из предложенных или введите вручную:",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "📊 Прогресс")
async def menu_progress(message: Message, state: FSMContext):
    """Прогресс — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "📊 <b>Прогресс</b>\n\n"
        "Здесь будут ваши графики и статистика.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "📋 Списки покупок")
async def menu_shopping(message: Message, state: FSMContext):
    """Списки покупок — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "📋 <b>Списки покупок</b>\n\n"
        "Управление списками покупок.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "🔔 Напоминания")
async def menu_reminders(message: Message, state: FSMContext):
    """Напоминания — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "🔔 <b>Напоминания</b>\n\n"
        "Настройте напоминания о приёмах пищи и воде.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "👤 Профиль")
async def menu_profile(message: Message, state: FSMContext):
    """Профиль — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "👤 <b>Профиль</b>\n\n"
        "Нажмите /set_profile для настройки или просмотра.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "📖 Рецепты")
async def menu_recipes(message: Message, state: FSMContext):
    """Рецепты — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "📖 <b>Рецепты</b>\n\n"
        "Введите /recipe и ингредиенты для генерации рецепта.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "🏋️ Активность")
async def menu_activity(message: Message, state: FSMContext):
    """Активность — сбрасывает состояние"""
    await state.clear()
    await message.answer(
        "🏋️ <b>Активность</b>\n\n"
        "Записывайте тренировки и отслеживайте прогресс.",
        reply_markup=get_main_keyboard()
    )
