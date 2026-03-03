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
from handlers.ai_assistant import cmd_ask  # ← ВАЖНО: добавить этот импорт

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
    await cmd_progress(message)


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


@router.message(F.text == "💬 AI Помощник")
async def menu_ai_assistant(message: Message, state: FSMContext):
    await state.clear()
    from handlers.ai_assistant import cmd_ask
    await cmd_ask(message, state)


@router.message(F.text == "🏋️ Активность")
async def menu_activity(message: Message, state: FSMContext):
    await state.clear()
    await cmd_fitness(message, state)


@router.message(F.text == "❓ Помощь")
async def menu_help(message: Message, state: FSMContext):
    """Подробная справка по использованию бота."""
    await state.clear()
    help_text = (
        "🤖 <b>NutriBuddy – ваш персональный помощник</b>\n\n"
        "<b>📌 Основные возможности:</b>\n"
        "• <b>👤 Профиль</b> – настройте свои параметры (вес, рост, возраст, пол, активность, цель). Бот рассчитает ваши дневные нормы калорий, белков, жиров, углеводов и воды.\n"
        "• <b>🍽️ Дневник питания</b> – записывайте, что вы съели. Можно вводить продукты вручную, перечисляя через запятую, или отправить фото еды – бот распознает продукты и предложит выбрать.\n"
        "• <b>💧 Вода</b> – отмечайте, сколько воды выпили. Можно выбрать предустановленный объём или ввести свой. Бот покажет прогресс к дневной цели.\n"
        "• <b>📊 Прогресс</b> – графики и статистика по весу, воде, калориям и активности за день, неделю или месяц.\n"
        "• <b>📋 Списки покупок</b> – создавайте списки товаров. Добавляйте товары простым текстом (например, «яйца, молоко, 2 кг яблок»). Можно менять количество кнопками +/- и отмечать купленное.\n"
        "• <b>🔔 Напоминания</b> – настройте напоминания о приёме пищи, воде или других делах. Можно указать время и дни недели.\n"
        "• <b>🏋️ Активность</b> – записывайте тренировки: ходьба, бег, велосипед и т.д. Укажите длительность, бот сам рассчитает примерные сожжённые калории.\n"
        "• <b>💬 AI Помощник</b> – умный ассистент на базе Cloudflare Workers AI. Умеет:\n"
        "   – Отвечать на любые вопросы о питании, здоровье, тренировках.\n"
        "   – Сообщать погоду в любом городе (например, «погода в Мурманске»).\n"
        "   – Добавлять товары в список покупок (например, «добавь в список яйца и молоко»).\n"
        "   – Создавать напоминания (например, «напомни выпить таблетки в 20:00»).\n"
        "   – Предлагать рецепты (например, «рецепт из курицы и риса»).\n"
        "   – Просто общаться и помогать по любым вопросам.\n\n"
        "<b>📌 Как пользоваться:</b>\n"
        "• <b>Начните с настройки профиля</b> – нажмите 👤 Профиль или введите /set_profile.\n"
        "• <b>Для записи еды</b> – можно просто написать список продуктов (например, «курица, рис, брокколи») – бот предложит выбрать, куда добавить (в список покупок или как приём пищи). Если вы уже в режиме дневника питания, введите название продукта или отправьте фото.\n"
        "• <b>Для воды</b> – нажмите кнопку 💧 Вода или напишите «вода 300» – бот сразу запишет 300 мл. Если просто «вода», спросит, выпить или купить.\n"
        "• <b>Для списка покупок</b> – можно написать «купить яйца, молоко» – бот добавит товары. Для управления количеством используйте кнопки ➕ и ➖ в самом списке.\n"
        "• <b>Для напоминаний</b> – напишите «напомни позвонить маме в 18:00» – бот создаст напоминание. Если время не указано, попросит уточнить.\n"
        "• <b>Для AI-помощника</b> – нажмите кнопку 💬 AI Помощник или введите /ask, затем задайте вопрос или команду. Можно отправлять голосовые сообщения.\n"
        "• <b>Если бот не понимает</b> – он предложит меню выбора, куда добавить ваш текст (в список покупок, как приём пищи, спросить AI или отмена).\n\n"
        "<b>📌 Полезные команды:</b>\n"
        "/start – запустить бота\n"
        "/help – эта справка\n"
        "/set_profile – настройка профиля\n"
        "/log_food – записать еду\n"
        "/log_water – добавить воду\n"
        "/log_weight – записать вес\n"
        "/fitness – добавить активность\n"
        "/progress – прогресс\n"
        "/ask – спросить AI-помощника\n"
        "/shopping – списки покупок\n"
        "/reminders – напоминания\n"
        "/cancel – отменить текущее действие\n\n"
        "💡 <b>Советы:</b>\n"
        "• Отправляйте фото еды – бот распознает продукты и предложит выбрать.\n"
        "• Используйте голосовые сообщения – они распознаются и обрабатываются так же, как текст.\n"
        "• Если ошиблись в действии, нажмите ❌ Отмена или введите /cancel.\n"
        "• Все данные сохраняются в вашем профиле и не теряются при перезапуске.\n\n"
        "<i>Приятного использования! Если остались вопросы, просто спросите у AI-помощника.</i>"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_keyboard())
