"""
Общие команды: /start, /help, /cancel, и интерактивное меню помощи.
Добавлена навигация по категориям (обратно совместимо).
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
from handlers.profile import cmd_profile, edit_profile
from handlers.food import cmd_log_food
from handlers.water import cmd_water
from handlers.progress import cmd_progress
from handlers.shopping import cmd_shopping
from handlers.reminders import cmd_reminders
from handlers.activity import cmd_fitness
from handlers.ai_assistant import cmd_ask
from handlers.meal_plan import cmd_meal_plan

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Приветственное сообщение и новое главное меню."""
    await state.clear()
    welcome_text = (
        "✨ <b>Добро пожаловать в NutriBuddy!</b> ✨\n\n"
        "Я — твой персональный помощник в здоровом питании и активном образе жизни.\n"
        "Выбери раздел в меню ниже, чтобы начать."
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    """Вызывает интерактивное меню помощи."""
    await state.clear()
    await show_help_menu(message)

async def show_help_menu(event: Message | CallbackQuery):
    """Отображает главное меню помощи с инлайн-кнопками (без изменений)."""
    text = (
        "📚 <b>Разделы помощи</b>\n\n"
        "Выберите интересующую тему:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="help_profile")],
        [InlineKeyboardButton(text="🍽️ Дневник питания", callback_data="help_food")],
        [InlineKeyboardButton(text="💧 Вода", callback_data="help_water")],
        [InlineKeyboardButton(text="🏋️ Активность", callback_data="help_activity")],
        [InlineKeyboardButton(text="📊 Прогресс", callback_data="help_progress")],
        [InlineKeyboardButton(text="📋 Списки покупок", callback_data="help_shopping")],
        [InlineKeyboardButton(text="🔔 Напоминания", callback_data="help_reminders")],
        [InlineKeyboardButton(text="🤖 AI Помощник", callback_data="help_ai")],
        [InlineKeyboardButton(text="🍽️ План питания", callback_data="help_meal_plan")],
        [InlineKeyboardButton(text="📌 Советы и команды", callback_data="help_tips")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="help_close")]
    ])

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:  # CallbackQuery
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await event.answer()

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

# ========== Обработчики кнопок НОВОГО главного меню (категории) ==========

@router.message(F.text == "🍽️ Питание")
async def show_food_category(message: Message, state: FSMContext):
    """Показывает подменю питания."""
    await message.answer(
        "🍽️ <b>Раздел питания</b>\n\n"
        "Выберите действие:",
        reply_markup=get_food_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "💧 Вода и активность")
async def show_water_activity_category(message: Message, state: FSMContext):
    """Показывает подменю воды и активности."""
    await message.answer(
        "💧 <b>Вода и активность</b>\n\n"
        "Выберите действие:",
        reply_markup=get_water_activity_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Прогресс и статистика")
async def show_progress_category(message: Message, state: FSMContext):
    """Показывает подменю прогресса."""
    await message.answer(
        "📊 <b>Прогресс и статистика</b>\n\n"
        "Выберите период:",
        reply_markup=get_progress_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "📋 Списки и напоминания")
async def show_lists_category(message: Message, state: FSMContext):
    """Показывает подменю списков и напоминаний."""
    await message.answer(
        "📋 <b>Списки и напоминания</b>\n\n"
        "Выберите действие:",
        reply_markup=get_lists_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "👤 Профиль и настройки")
async def show_profile_category(message: Message, state: FSMContext):
    """Показывает подменю профиля."""
    await message.answer(
        "👤 <b>Профиль и настройки</b>\n\n"
        "Выберите действие:",
        reply_markup=get_profile_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "❓ Помощь")
async def menu_help(message: Message, state: FSMContext):
    """Показывает интерактивное меню помощи."""
    await state.clear()
    await show_help_menu(message)

# ========== Обработчики кнопок СТАРОГО главного меню (для обратной совместимости) ==========

@router.message(F.text == "🍽️ Дневник питания")
async def menu_food_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_log_food(message, state)

@router.message(F.text == "💧 Вода")
async def menu_water_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_water(message, state)

@router.message(F.text == "📊 Прогресс")
async def menu_progress_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_progress(message)

@router.message(F.text == "📋 Списки покупок")
async def menu_shopping_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_shopping(message, state)

@router.message(F.text == "🔔 Напоминания")
async def menu_reminders_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_reminders(message, state)

@router.message(F.text == "👤 Профиль")
async def menu_profile_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_profile(message, state)

@router.message(F.text == "🍽️ План питания")
async def menu_meal_plan_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_meal_plan(message, state)

@router.message(F.text == "💬 AI Помощник")
async def menu_ai_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_ask(message, state)

@router.message(F.text == "🏋️ Активность")
async def menu_activity_old(message: Message, state: FSMContext):
    await state.clear()
    await cmd_fitness(message, state)

# ========== Обработчики навигационных callback'ов для новых меню ==========

@router.callback_query(F.data == "menu_back")
async def menu_back_callback(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню."""
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_food_photo")
async def menu_food_photo(callback: CallbackQuery, state: FSMContext):
    """Запуск распознавания фото."""
    await callback.message.answer("📸 Отправьте фото еды")
    await callback.answer()

@router.callback_query(F.data == "menu_food_manual")
async def menu_food_manual(callback: CallbackQuery, state: FSMContext):
    """Ручной ввод еды."""
    await cmd_log_food(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "menu_meal_plan")
async def menu_meal_plan(callback: CallbackQuery, state: FSMContext):
    """План питания."""
    await cmd_meal_plan(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "menu_water")
async def menu_water(callback: CallbackQuery, state: FSMContext):
    """Запись воды."""
    await cmd_water(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "menu_activity")
async def menu_activity(callback: CallbackQuery, state: FSMContext):
    """Запись активности."""
    await cmd_fitness(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "menu_steps")
async def menu_steps(callback: CallbackQuery, state: FSMContext):
    """Быстрая запись шагов."""
    await callback.message.answer("👟 Введите количество шагов (например, '5000 шагов')")
    await callback.answer()

@router.callback_query(F.data == "menu_shopping")
async def menu_shopping(callback: CallbackQuery, state: FSMContext):
    """Список покупок."""
    await cmd_shopping(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "menu_reminders")
async def menu_reminders(callback: CallbackQuery, state: FSMContext):
    """Напоминания."""
    await cmd_reminders(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "menu_profile_view")
async def menu_profile_view(callback: CallbackQuery, state: FSMContext):
    """Просмотр профиля."""
    await cmd_profile(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "menu_profile_edit")
async def menu_profile_edit(callback: CallbackQuery, state: FSMContext):
    """Редактирование профиля."""
    await edit_profile(callback.message, state)
    await callback.answer()

# ========== Обработчики инлайн-кнопок помощи (без изменений) ==========

@router.callback_query(F.data.startswith("help_"))
async def help_callbacks(callback: CallbackQuery):
    data = callback.data

    if data == "help_profile":
        text = (
            "👤 <b>Профиль</b>\n\n"
            "• Настройте свои параметры: вес, рост, возраст, пол, уровень активности, цель (похудение/поддержание/набор).\n"
            "• На основе этих данных бот рассчитает ваши дневные нормы калорий, белков, жиров, углеводов и воды.\n"
            "• Нормы учитываются в прогрессе и при генерации плана питания.\n\n"
            "<b>Команда:</b> /set_profile\n"
            "<b>Кнопка в меню:</b> 👤 Профиль"
        )
    elif data == "help_food":
        text = (
            "🍽️ <b>Дневник питания</b>\n\n"
            "• Записывайте продукты вручную (например, «курица, рис, брокколи») – бот разобьёт на ингредиенты.\n"
            "• Отправьте фото еды – бот распознает продукты и предложит выбрать.\n"
            "• Для каждого продукта нужно указать вес.\n"
            "• Если продукта нет в базе, можно ввести название вручную (калории будут равны 0, но их можно добавить позже).\n\n"
            "<b>Команда:</b> /log_food\n"
            "<b>Кнопка в меню:</b> 🍽️ Дневник питания"
        )
    elif data == "help_water":
        text = (
            "💧 <b>Вода</b>\n\n"
            "• Отмечайте, сколько воды выпили. Можно выбрать предустановленный объём (200, 300, 500, 1000 мл) или ввести своё число.\n"
            "• Быстрая запись: напишите «вода 300» – бот сразу запишет 300 мл.\n"
            "• Если написать просто «вода», бот спросит, выпить или купить воду в магазине.\n"
            "• Бот показывает прогресс к дневной цели, рассчитанной в профиле.\n\n"
            "<b>Команда:</b> /log_water\n"
            "<b>Кнопка в меню:</b> 💧 Вода"
        )
    elif data == "help_activity":
        text = (
            "🏋️ <b>Активность</b>\n\n"
            "• Записывайте тренировки: ходьба, бег, велосипед, тренажёрный зал, йога, плавание.\n"
            "• Укажите длительность (минуты) – бот сам рассчитает примерные сожжённые калории.\n"
            "• Для ходьбы можно ввести количество шагов, например, «запиши 5000 шагов» – бот сохранит активность с шагами и посчитает калории.\n"
            "• Активность учитывается в прогрессе (баланс калорий).\n\n"
            "<b>Команда:</b> /fitness\n"
            "<b>Кнопка в меню:</b> 🏋️ Активность"
        )
    elif data == "help_progress":
        text = (
            "📊 <b>Прогресс</b>\n\n"
            "• Показывает графики и статистику по весу, воде, калориям и активности.\n"
            "• Можно выбрать период: день, неделя, месяц.\n"
            "• Отображается потреблённые и сожжённые калории, баланс, остаток до цели.\n"
            "• Графики строятся автоматически при наличии данных.\n\n"
            "<b>Команда:</b> /progress\n"
            "<b>Кнопка в меню:</b> 📊 Прогресс"
        )
    elif data == "help_shopping":
        text = (
            "📋 <b>Списки покупок</b>\n\n"
            "• Единый список «Покупки» создаётся автоматически.\n"
            "• Добавляйте товары простым текстом: «яйца, молоко, 2 кг яблок» – бот разберёт количество и единицы.\n"
            "• В списке есть кнопки: ➕ увеличить количество, ➖ уменьшить, ✅ отметить купленное, 🗑️ удалить товар.\n"
            "• Можно создать новый список, но рекомендуется использовать один основной.\n\n"
            "<b>Команда:</b> /shopping\n"
            "<b>Кнопка в меню:</b> 📋 Списки покупок"
        )
    elif data == "help_reminders":
        text = (
            "🔔 <b>Напоминания</b>\n\n"
            "• Настраивайте напоминания о приёме пищи, воде или своих делах.\n"
            "• Можно указать время и дни недели.\n"
            "• Быстрое создание: напишите «напомни позвонить маме в 18:00» – бот создаст напоминание (если время распознано).\n\n"
            "<b>Команда:</b> /reminders\n"
            "<b>Кнопка в меню:</b> 🔔 Напоминания"
        )
    elif data == "help_ai":
        text = (
            "🤖 <b>AI Помощник</b>\n\n"
            "• Умный ассистент на базе Cloudflare Workers AI (модель Qwen).\n"
            "• Отвечает на любые вопросы о питании, здоровье, тренировках, рецептах.\n"
            "• Может сообщить погоду в любом городе (если город не указан, используется город из профиля).\n"
            "• Умеет добавлять товары в список покупок по команде «добавь в список ...».\n"
            "• Поддерживает голосовой ввод.\n\n"
            "<b>Команда:</b> /ask\n"
            "<b>Кнопка в меню:</b> 💬 AI Помощник"
        )
    elif data == "help_meal_plan":
        text = (
            "🍽️ <b>План питания</b>\n\n"
            "• Показывает рекомендуемое распределение калорий на день (завтрак, обед, ужин, перекус) на основе вашей дневной нормы.\n"
            "• Можно сгенерировать примерное меню на день.\n"
            "• Если меню не нравится, нажмите «🔄 Другой вариант».\n"
            "• Понравившийся вариант можно сохранить кнопкой «💾 Сохранить рацион» – бот пришлёт его отдельным сообщением.\n\n"
            "<b>Команда:</b> /meal_plan\n"
            "<b>Кнопка в меню:</b> 🍽️ План питания"
        )
    elif data == "help_tips":
        text = (
            "📌 <b>Советы и команды</b>\n\n"
            "• <b>Основные команды:</b>\n"
            "/start – запустить бота\n"
            "/help – меню помощи\n"
            "/cancel – отменить действие\n"
            "/set_profile – настройка профиля\n"
            "/log_food – записать еду\n"
            "/log_water – добавить воду\n"
            "/log_weight – записать вес\n"
            "/fitness – активность\n"
            "/progress – прогресс\n"
            "/ask – спросить AI\n"
            "/shopping – списки покупок\n"
            "/reminders – напоминания\n"
        )
    elif data == "help_close":
        await callback.message.delete()
        await callback.answer()
        return
    else:
        await callback.answer()
        return

    # Для всех разделов, кроме закрытия, показываем текст и кнопку назад
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="help_back")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "help_back")
async def help_back_callback(callback: CallbackQuery):
    """Возврат в главное меню помощи."""
    await show_help_menu(callback)
