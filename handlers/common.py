"""
Общие команды: /start, /help, /cancel, и интерактивное меню помощи.
Добавлена навигация по категориям и AI помощник.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

from keyboards.reply import get_main_keyboard
from keyboards.inline import (
    get_food_menu, get_water_activity_menu, get_progress_menu, get_profile_menu
)
# Импорты заменены на AI-обработчик (полный переход на Hermes)
from handlers.enhanced_universal_handler import EnhancedUniversalHandler
from handlers.profile import cmd_profile, display_profile
from handlers.progress import cmd_progress
from handlers.meal_plan import cmd_meal_plan
from utils.states import StepsStates
from handlers.profile import edit_profile

# Глобальный AI-обработчик
ai_handler = EnhancedUniversalHandler()

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """🎨 Современное приветствие с персонализацией"""
    await state.clear()
    
    # Получаем данные пользователя для персонализации
    user_name = message.from_user.first_name or message.from_user.username or "Пользователь"
    
    # Создаем современное приветствие
    from utils.message_templates import MessageTemplates
    welcome_text = MessageTemplates.modern_welcome_message(user_name)
    
    # Современная клавиатура
    from keyboards.improved_keyboards import get_modern_main_menu
    keyboard = get_modern_main_menu()
    
    # Добавляем информацию о профиле
    profile_text = (
        "\n\n" + "⚠️ <b>Важно:</b>\n" +
        "👤 Перед началом работы создайте профиль командой /set_profile\n" +
        "📊 Это поможет рассчитать ваши персональные нормы КБЖУ"
    )
    
    welcome_text += profile_text
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

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
        [InlineKeyboardButton(text="👤 Профиль", callback_data="help_profile_category")],
        [InlineKeyboardButton(text="💬 Умный помощник", callback_data="help_assistant_category")],
        [InlineKeyboardButton(text="🔮 Аналитика и прогнозы", callback_data="help_analytics_category")],
        [InlineKeyboardButton(text="🎮 Челленджи", callback_data="help_challenge_category")],
        [InlineKeyboardButton(text="🏆 Уровни и награды", callback_data="help_level_category")],
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
    elif data == "help_profile_category":
        text = (
            "👤 <b>Профиль</b>\n\n"
            "⚖️ <b>Данные</b> – вес, рост, возраст, пол, уровень активности, цель, город.\n"
            "📊 <b>Нормы</b> – я автоматически рассчитаю дневную норму калорий, БЖУ и воды.\n"
            "✏️ <b>Редактирование</b> – можно изменить данные в любое время."
        )
    elif data == "help_assistant_category":
        text = (
            "💬 <b>Умный помощник</b>\n\n"
            "💬 <b>Диалоговый режим</b> – просто говори что нужно, я пойму и помогу.\n"
            "   <i>Пример: «Выпил стакан воды» → я запишу</i>\n\n"
            "🌦️ <b>Погода</b> – могу сказать погоду в любом городе.\n"
            "   <i>Пример: «погода в Москве»</i>\n\n"
            "📝 <b>Советы</b> – спрашивай о питании, тренировках, здоровье.\n\n"
            "🎯 <b>Умные команды</b> – «запиши вес», «добавь активность», «какой прогресс?»\n\n"
            "❌ <b>Выход</b> – напиши «выход» или /cancel, чтобы выйти из режима."
        )
    elif data == "help_analytics_category":
        text = (
            "🔮 <b>Аналитика и прогнозы</b>\n\n"
            "📊 <b>Глубокий анализ</b> – подробный анализ твоего прогресса.\n"
            "   <i>Команда: /analytics</i>\n\n"
            "🎯 <b>Прогноз веса</b> – узнаешь свой вес через 7 и 14 дней.\n"
            "   <i>С учетом доверительного интервала</i>\n\n"
            "💡 <b>Психологические советы</b> – анализ мотивации и дисциплины.\n\n"
            "⚠️ <b>Предупреждение рисков</b> – помогу избежать срывов.\n\n"
            "📈 <b>Персональные рекомендации</b> – советы на основе твоих данных."
        )
    elif data == "help_challenge_category":
        text = (
            "🎮 <b>Челленджи и задания</b>\n\n"
            "🎯 <b>Персональные задания</b> – адаптированные под твои цели.\n"
            "   <i>Команда: /challenge</i>\n\n"
            "📅 <b>Разная длительность</b> – от 3 до 7 дней.\n\n"
            "⭐ <b>Награды</b> – получай очки за выполнение.\n\n"
            "🏆 <b>Достижения</b> – открывай новые уровни.\n\n"
            "💪 <b>Мотивация</b> – персональная поддержка и подсказки."
        )
    elif data == "help_level_category":
        text = (
            "🏆 <b>Уровни и награды</b>\n\n"
            "📊 <b>Твой уровень</b> – от Новичка до Мастера здоровья.\n"
            "   <i>Команда: /level</i>\n\n"
            "⭐ <b>Очки опыта</b> – получай за активность:\n"
            "   • Вода: 10 очков за запись\n"
            "   • Активность: 15 очков\n"
            "   • Вес: 12 очков\n"
            "   • Регулярность: 25 очков\n\n"
            "🎖️ <b>Достижения</b> – персональные под твои цели.\n\n"
            "👑 <b>Титулы</b> – Энтузиаст, Эксперт, Мастер, Легенда..."
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

@router.message(F.text == "👤 Профиль и настройки")
async def show_profile_category(message: Message, state: FSMContext):
    await message.answer(
        "👤 <b>Профиль и настройки</b>\n\n"
        "Выберите действие:",
        reply_markup=get_profile_menu(),
        parse_mode="HTML"
    )

# ========== ОБРАБОТЧИКИ ДЛЯ ГЛАВНОГО МЕНЮ ==========

@router.callback_query(F.data == "manual_food")
async def manual_food_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для добавления приема пищи из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    await state.clear()
    # Используем AI-обработчик вместо несуществующего cmd_log_food
    await ai_handler.handle_message(callback.message, state, "записать прием пищи")

@router.callback_query(F.data == "show_progress")
async def show_progress_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для прогресса из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    from handlers.progress import cmd_progress
    await cmd_progress(callback.message, state, user_id=callback.from_user.id)

async def period_callback_internal(callback: CallbackQuery, state: FSMContext):
    """🎨 Внутренний обработчик периода"""
    from utils.statistics import get_period_stats
    from datetime import datetime
    
    user_id = callback.from_user.id
    period = callback.data.split("_")[1]  # day / week / month / all
    
    # Определяем начальную дату периода
    now = datetime.utcnow()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_name = "сегодня"
    elif period == "week":
        start_date = now - timedelta(days=7)
        period_name = "за неделю"
    elif period == "month":
        start_date = now - timedelta(days=30)
        period_name = "за месяц"
    else:  # all
        start_date = now - timedelta(days=365)  # За последний год
        period_name = "за всё время"
    
    logger.info(f"🔍 DEBUG: Период {period_name}, стартовая дата: {start_date}")
    
    # Получаем статистику через универсальную функцию
    async with get_session() as session:
        stats = await get_period_stats(user_id, session, start_date)
    
    if not stats:
        await callback.message.answer("📊 Нет данных за выбранный период")
        return
    
    logger.info(f"🔍 DEBUG: Статистика получена: {len(stats)} полей")
    
    # Создаем сообщение с прогрессом
    message = f"📊 Ваш прогресс {period_name}\n\n"
    message += f"🔥 Калории: {stats['total_calories']:.0f} ккал\n"
    message += f"💧 Вода: {stats['total_water']:.0f} мл\n"
    message += f"🏃 Активность: {stats['activities_count']} раз\n"
    message += f"👞 Шаги: {stats['total_steps']:,} шагов\n"
    
    # Прогресс по целям
    goals = stats['user_goals']
    calorie_percent = (stats['avg_calories'] / goals['calories'] * 100) if goals['calories'] > 0 else 0
    water_percent = (stats['avg_water'] / goals['water'] * 100) if goals['water'] > 0 else 0
    
    message += f"\n📊 Средние значения в день:\n"
    message += f"🔥 {stats['avg_calories']:.0f}/{goals['calories']} ккал ({calorie_percent:.0f}%)\n"
    message += f"💧 {stats['avg_water']:.0f}/{goals['water']} мл ({water_percent:.0f}%)\n"
    
    logger.info(f"🔍 DEBUG: Сообщение создано, длина: {len(message)}")
    
    await callback.message.answer(message, reply_markup=get_main_keyboard())
    logger.info(f"🔍 DEBUG: Обработчик завершен успешно")

@router.callback_query(F.data == "log_water")
async def log_water_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для воды из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    # Используем AI-обработчик вместо несуществующего cmd_water
    await ai_handler.handle_message(callback.message, state, "записать воду")

@router.callback_query(F.data == "log_activity")
async def log_activity_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для активности из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    # Используем AI-обработчик вместо несуществующего cmd_fitness
    await ai_handler.handle_message(callback.message, state, "записать активность")

@router.callback_query(F.data == "show_profile")
async def show_profile_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для профиля из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    from handlers.profile import cmd_profile
    await cmd_profile(callback.message, state, user_id=callback.from_user.id)

@router.callback_query(F.data == "ai_assistant")
async def ai_assistant_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для AI помощника из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    # Используем AI-обработчик вместо несуществующего cmd_ask
    await ai_handler.handle_message(callback.message, state, "задать вопрос ассистенту")

async def handle_menu_callbacks(callback: CallbackQuery, state: FSMContext):
    """Обработка menu_* callback'ов через AI"""
    await callback.answer()
    
    # Все menu_* callback обрабатываются через AI
    if callback.data == "menu_food_photo":
        await ai_handler.handle_message(callback.message, state, "добавить еду")
    elif callback.data == "menu_water":
        await ai_handler.handle_message(callback.message, state, "записать воду")
    elif callback.data == "menu_activity":
        await ai_handler.handle_message(callback.message, state, "записать активность")
    elif callback.data == "menu_steps":
        await ai_handler.handle_message(callback.message, state, "записать шаги")
    elif callback.data == "menu_weight":
        await ai_handler.handle_message(callback.message, state, "записать вес")
    elif callback.data == "menu_plan":
        await cmd_meal_plan(callback.message, state)
    elif callback.data == "menu_ai_help":
        await ai_handler.handle_message(callback.message, state, "помощь")
    elif callback.data == "menu_food_manual":
        await ai_handler.handle_message(callback.message, state, "добавить еду вручную")
    elif callback.data == "menu_meal_plan":
        await cmd_meal_plan(callback.message, state)
    elif callback.data == "menu_ai":
        await ai_handler.handle_message(callback.message, state, "задать вопрос ассистенту")
    elif callback.data == "menu_water":
        await ai_handler.handle_message(callback.message, state, "записать воду")
    elif callback.data == "menu_activity":
        await ai_handler.handle_message(callback.message, state, "записать активность")
    elif callback.data == "menu_steps":
        await ai_handler.handle_message(callback.message, state, "записать шаги")
    elif callback.data == "menu_profile_view":
        await display_profile(callback, callback.from_user.id, state)
    elif callback.data == "menu_profile_edit":
        await edit_profile(callback.message, state, user_id=callback.from_user.id)
    elif callback.data == "menu_log_weight":
        await ai_handler.handle_message(callback.message, state, "записать вес")
    elif callback.data == "menu_back":
        await callback.message.delete()
        await callback.message.answer(
            "🏠 Главное меню",
            reply_markup=get_main_keyboard()
        )
    else:
        logger.info(f"🔍 DEBUG: Неизвестный menu callback: {callback.data}")
    await callback.answer()

@router.callback_query(F.data.startswith("progress_"))
async def progress_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для progress_ callback"""
    await period_callback_internal(callback, state)

# ========== Конец файла ==========
