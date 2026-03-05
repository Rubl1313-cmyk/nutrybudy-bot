"""
Общие команды: /start, /help, /cancel, и интерактивное меню помощи.
Добавлена навигация по категориям и AI помощник.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from keyboards.reply import get_main_keyboard
from keyboards.inline import (
    get_food_menu, get_water_activity_menu, get_progress_menu,
    get_lists_menu, get_profile_menu
)
from handlers.profile import cmd_profile, display_profile
from handlers.food import cmd_log_food
from handlers.water import cmd_water
from handlers.progress import cmd_progress
from handlers.shopping import cmd_shopping
from handlers.reminders import cmd_reminders
from handlers.activity import cmd_fitness
from handlers.ai_assistant import cmd_ask
from handlers.meal_plan import cmd_meal_plan
from utils.states import StepsStates

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Приветственное сообщение — лаконичное и современное."""
    await state.clear()
    welcome_text = (
        "🚀 <b>Добро пожаловать в NutriBuddy!</b>\n\n"
        "Твой умный помощник для здорового питания и активного образа жизни.\n\n"
        "⚡️ <b>Быстрый старт:</b>\n"
        "1. Настрой профиль → /set_profile или кнопка 👤 Профиль\n"
        "2. Начинай записывать еду, воду и тренировки\n"
        "3. Следи за прогрессом и получай рекомендации\n\n"
        "✨ <b>Возможности:</b>\n"
        "• Распознавание еды по фото\n"
        "• AI-ассистент с поддержкой диалога\n"
        "• Планировщик питания\n"
        "• Графики прогресса\n\n"
        "👇 Выбери раздел в меню или просто напиши вопрос."
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
        "Выбери тему, чтобы узнать подробнее:"
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
    if data == "help_food_category":
        text = (
            "🍽️ <b>Питание</b>\n\n"
            "📸 <b>Фото еды</b> – отправь фото, я распознаю продукты и предложу ввести вес.\n"
            "   <i>Пример: сфотографируй тарелку с едой</i>\n\n"
            "✏️ <b>Ручной ввод</b> – напиши продукты через запятую.\n"
            "   <i>Пример: «гречка, куриная грудка, огурец»</i>\n\n"
            "🍽️ <b>План питания</b> – сгенерирую меню на день с учётом твоих норм.\n\n"
            "🔍 <b>Поиск продукта</b> – просто название, и я покажу калорийность и БЖУ.\n"
            "   <i>Пример: «авокадо»</i>"
        )
    elif data == "help_water_category":
        text = (
            "💧 <b>Вода и активность</b>\n\n"
            "💧 <b>Записать воду</b> – выбери объём из предложенных или введи вручную.\n"
            "   <i>Пример: «250 мл» или «стакан воды»</i>\n\n"
            "👟 <b>Записать шаги</b> – введи количество шагов, я пересчитаю в километры и калории.\n"
            "   <i>Пример: «прошёл 5000 шагов»</i>\n\n"
            "🏃 <b>Записать активность</b> – выбери тип тренировки и укажи длительность.\n"
            "   <i>Пример: «бег 30 минут»</i>"
        )
    elif data == "help_progress_category":
        text = (
            "📊 <b>Прогресс</b>\n\n"
            "📈 <b>Статистика</b> – просмотр потреблённых калорий, воды, веса и активности.\n"
            "📅 <b>Периоды</b> – можно посмотреть статистику за день, неделю или месяц.\n"
            "📉 <b>Графики</b> – наглядная динамика изменений веса и потребления."
        )
    elif data == "help_lists_category":
        text = (
            "📋 <b>Списки и напоминания</b>\n\n"
            "📝 <b>Список покупок</b> – добавляй товары, меняй количество, отмечай купленное.\n"
            "   <i>Пример: «купить 2 яйца, молоко»</i>\n\n"
            "🔔 <b>Напоминания</b> – создавай напоминания о приёме пищи, воде или других делах.\n"
            "   <i>Пример: «напомни выпить воду в 15:00»</i>"
        )
    elif data == "help_profile_category":
        text = (
            "👤 <b>Профиль</b>\n\n"
            "⚖️ <b>Данные</b> – вес, рост, возраст, пол, уровень активности, цель, город.\n"
            "📊 <b>Нормы</b> – я автоматически рассчитаю дневную норму калорий, БЖУ и воды.\n"
            "✏️ <b>Редактирование</b> – можно изменить данные в любое время."
        )
    elif data == "help_ai_category":
        text = (
            "🤖 <b>AI Помощник</b>\n\n"
            "💬 <b>Диалоговый режим</b> – задавай вопросы, я помню контекст беседы.\n"
            "   <i>Пример: «Какой рецепт пасты?» → «А с морепродуктами?»</i>\n\n"
            "🌦️ <b>Погода</b> – могу сказать погоду в любом городе.\n"
            "   <i>Пример: «погода в Москве»</i>\n\n"
            "📝 <b>Советы</b> – спрашивай о питании, тренировках, здоровье.\n\n"
            "❌ <b>Выход</b> – напиши «выход» или /cancel, чтобы выйти из режима."
        )
    elif data == "help_close":
        await callback.message.delete()
        await callback.answer()
        return
    elif data == "help_back":
        await show_help_menu(callback)
        return
    else:
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

@router.message(F.text == "🤖 AI Помощник")
async def menu_ai_assistant(message: Message, state: FSMContext):
    await cmd_ask(message, state)

# ========== Обработчики навигационных callback'ов ==========

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
    await display_profile(callback, callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "menu_profile_edit")
async def menu_profile_edit(callback: CallbackQuery, state: FSMContext):
    await edit_profile(callback.message, state, user_id=callback.from_user.id)
    await callback.answer()
