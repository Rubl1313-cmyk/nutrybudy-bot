"""
Общие команды: /start, /help, /cancel, главное меню.
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
        "• 📖 Планирования питания\n\n"
        "🎯 <b>Начни с настройки профиля:</b>\n"
        "Нажми 👤 Профиль или /set_profile\n\n"
        "💡 <b>Совет:</b> Отправь фото еды для автоматического анализа!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message, state: FSMContext):
    """Подробная справка по всем функциям бота."""
    await state.clear()
    await message.answer(
        "📚 <b>Руководство по NutriBuddy</b>\n\n"
        "<b>🔹 Основные команды и кнопки:</b>\n\n"
        "👤 <b>Профиль</b> – настройка ваших параметров (вес, рост, возраст, пол, активность, цель, город). "
        "После заполнения бот рассчитает ваши дневные нормы калорий и БЖУ.\n\n"
        "🍽️ <b>Дневник питания</b> – запись приёмов пищи. Можно ввести название вручную, "
        "отправить фото или голосовое сообщение. Бот распознает продукты, предложит выбрать из базы, "
        "запросит вес и сохранит КБЖУ.\n\n"
        "💧 <b>Вода</b> – добавление выпитой воды. Бот показывает прогресс за день и норму.\n\n"
        "📊 <b>Прогресс</b> – статистика за день, неделю или месяц с графиками. "
        "Выбирайте период с помощью кнопок после вызова.\n\n"
        "📋 <b>Списки покупок</b> – создавайте списки продуктов, отмечайте купленное.\n\n"
        "🔔 <b>Напоминания</b> – устанавливайте напоминания о приёмах пищи, воде и т.п.\n\n"
        "📖 <b>План питания</b> – генерация персонализированного плана питания на день. "
        "Вы получите список блюд (завтрак, обед, ужин, перекус) с суммарной калорийностью. "
        "Если план не понравился, нажмите «🔄 Предложить другой вариант». "
        "Чтобы увидеть полные рецепты с ингредиентами и инструкцией, нажмите «🍽️ Показать рецепты».\n\n"
        "🏋️ <b>Активность</b> – запись тренировок. Бот сам рассчитывает сожжённые калории по типу и длительности.\n\n"
        "❓ <b>Помощь</b> – это сообщение.\n\n"
        "<i>Для отмены текущего действия используйте кнопку «❌ Отмена» или команду /cancel.</i>",
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
    """Возврат в главное меню."""
    await state.clear()
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard()
    )
