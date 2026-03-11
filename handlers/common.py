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
from handlers.profile import cmd_profile, display_profile
from handlers.food import cmd_log_food
from handlers.water import cmd_water
from handlers.progress import cmd_progress
from handlers.activity import cmd_fitness
from handlers.ai_assistant import cmd_ask
from handlers.meal_plan import cmd_meal_plan
from utils.states import StepsStates
from handlers.weight import cmd_log_weight

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
    from handlers.food import cmd_log_food
    await cmd_log_food(callback.message, state, user_id=callback.from_user.id)

@router.callback_query(F.data == "show_progress")
async def show_progress_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для прогресса из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    from handlers.progress import cmd_progress
    await cmd_progress(callback.message, state, user_id=callback.from_user.id)

async def period_callback_internal(callback: CallbackQuery, state: FSMContext):
    """🎨 Внутренний обработчик выбора периода"""
    try:
        # 📊 Логирование для отладки
        logger.info(f"🔍 DEBUG: Внутренний обработчик: {callback.data}")
        logger.info(f"🔍 DEBUG: От пользователя: {callback.from_user.id}")
        
        period = callback.data.split("_")[1]  # day / week / month / all
        user_id = callback.from_user.id

        await callback.answer(f"📊 Загружаю статистику...")
        
        # 📊 Логирование периода
        logger.info(f"🔍 DEBUG: Период: {period}")
        
        await callback.message.delete()
        await state.clear()

        from database.db import get_session
        from database.models import User, Meal, Activity, WaterEntry, WeightEntry
        from services.plots import generate_weight_plot, generate_water_plot, generate_calorie_plot, generate_activity_plot
        from utils.ui_templates import ProgressBar, NutritionCard
        from utils.message_templates import MessageTemplates
        from sqlalchemy import select, func
        from datetime import datetime, timedelta
        from aiogram.types import BufferedInputFile

        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                logger.error(f"🔍 DEBUG: Пользователь не найден!")
                await callback.message.answer(
                    "❌ Пользователь не найден.",
                    reply_markup=get_main_keyboard()
                )
                return

            # 📊 Логирование пользователя
            logger.info(f"🔍 DEBUG: Пользователь найден: {user.first_name}")

            # Определяем диапазон дат
            today = datetime.now().date()
            if period == "day":
                start_date = today
                period_name = "сегодня"
            elif period == "week":
                start_date = today - timedelta(days=7)
                period_name = "за неделю"
            elif period == "month":
                start_date = today - timedelta(days=30)
                period_name = "за месяц"
            else:  # all
                start_date = today - timedelta(days=365)  # За последний год
                period_name = "за всё время"

            # 📊 Логирование дат
            logger.info(f"🔍 DEBUG: Период {period_name}, стартовая дата: {start_date}")

            # 📊 Получаем статистику за период
            stats = await _get_period_stats(user.id, session, start_date)
            
            # 📊 Логирование статистики
            logger.info(f"🔍 DEBUG: Статистика получена: {len(stats)} полей")
            
            # 🎨 Создаем современное сообщение с прогрессом
            progress_message = await _create_modern_progress_message(
                user, stats, period_name, period
            )
            
            # 📊 Логирование сообщения
            logger.info(f"🔍 DEBUG: Сообщение создано, длина: {len(progress_message)}")
            
            await callback.message.answer(
                progress_message, 
                reply_markup=get_main_keyboard(), 
                parse_mode="HTML"
            )

            # 📊 Генерируем графики
            await _send_progress_charts(callback, user, session, period, period_name)
            
            # 📊 Логирование завершения
            logger.info(f"🔍 DEBUG: Обработчик завершен успешно")
            
    except Exception as e:
        logger.error(f"🔍 DEBUG: Ошибка в обработчике периода: {e}")
        logger.error(f"🔍 DEBUG: Тип ошибки: {type(e)}")
        import traceback
        logger.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        
        await callback.message.answer(
            "❌ Произошла ошибка при загрузке статистики. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )

async def _get_period_stats(user_id: int, session, start_date) -> dict:
    """📊 Получение статистики за период"""
    from database.models import Meal, Activity, WaterEntry, WeightEntry
    from sqlalchemy import select, func
    from datetime import datetime
    
    # Статистика приемов пищи
    meals_result = await session.execute(
        select(Meal).where(
            Meal.user_id == user_id,
            func.date(Meal.datetime) >= start_date,
        )
    )
    meals = meals_result.scalars().all()

    # Статистика активности
    activities_result = await session.execute(
        select(Activity).where(
            Activity.user_id == user_id,
            func.date(Activity.datetime) >= start_date,
        )
    )
    activities = activities_result.scalars().all()

    # Статистика воды
    water_result = await session.execute(
        select(WaterEntry).where(
            WaterEntry.user_id == user_id,
            func.date(WaterEntry.datetime) >= start_date,
        )
    )
    water_entries = water_result.scalars().all()

    # Статистика веса
    weight_result = await session.execute(
        select(WeightEntry).where(
            WeightEntry.user_id == user_id,
            func.date(WeightEntry.datetime) >= start_date,
        )
    )
    weight_entries = weight_result.scalars().all()

    # Суммируем за период
    total_cal_consumed = sum(m.total_calories or 0 for m in meals)
    total_protein = sum(m.total_protein or 0 for m in meals)
    total_fat = sum(m.total_fat or 0 for m in meals)
    total_carbs = sum(m.total_carbs or 0 for m in meals)
    total_cal_burned = sum(a.calories_burned or 0 for a in activities)
    total_water = sum(w.amount or 0 for w in water_entries)

    # Расчёт средних
    days_count = (datetime.now().date() - start_date).days + 1
    avg_cal_consumed = total_cal_consumed / days_count if days_count else 0
    avg_protein = total_protein / days_count if days_count else 0
    avg_fat = total_fat / days_count if days_count else 0
    avg_carbs = total_carbs / days_count if days_count else 0
    avg_cal_burned = total_cal_burned / days_count if days_count else 0
    avg_water = total_water / days_count if days_count else 0

    # Тренды веса
    weight_trend = None
    if len(weight_entries) >= 2:
        start_weight = weight_entries[0].weight
        end_weight = weight_entries[-1].weight
        weight_trend = end_weight - start_weight

    return {
        'total_cal_consumed': total_cal_consumed,
        'total_protein': total_protein,
        'total_fat': total_fat,
        'total_carbs': total_carbs,
        'total_cal_burned': total_cal_burned,
        'total_water': total_water,
        'avg_cal_consumed': avg_cal_consumed,
        'avg_protein': avg_protein,
        'avg_fat': avg_fat,
        'avg_carbs': avg_carbs,
        'avg_cal_burned': avg_cal_burned,
        'avg_water': avg_water,
        'days_count': days_count,
        'meals_count': len(meals),
        'activities_count': len(activities),
        'weight_trend': weight_trend,
        'latest_weight': weight_entries[-1].weight if weight_entries else None
    }

async def _create_modern_progress_message(user, stats: dict, period_name: str, period: str) -> str:
    """🎨 Создание современного сообщения с прогрессом"""
    
    # Импортируем UI компоненты
    from utils.ui_templates import ProgressBar, NutritionCard
    from utils.message_templates import MessageTemplates
    
    # 🎯 Определяем статусы и мотивацию
    calorie_status = "🎯" if stats['avg_cal_consumed'] <= user.daily_calorie_goal else "⚠️"
    water_status = "💧" if stats['avg_water'] >= user.daily_water_goal else "💦"
    
    # 📊 Прогресс-бары
    calorie_bar = ProgressBar.create_modern_bar(
        stats['avg_cal_consumed'], user.daily_calorie_goal, style="gradient"
    )
    water_bar = ProgressBar.create_modern_bar(
        stats['avg_water'], user.daily_water_goal, style="gradient"
    )
    
    # 🎨 Карточки питательных веществ
    nutrition_card = NutritionCard.create_modern_macro_card(
        stats['avg_protein'], stats['avg_fat'], stats['avg_carbs']
    )
    
    # 🏆 Достижения и мотивация
    achievements = []
    if stats['meals_count'] >= stats['days_count'] * 3:  # 3+ приема в день
        achievements.append("🍽️ Регулярное питание")
    if stats['activities_count'] >= stats['days_count'] * 0.5:  # Активность половину дней
        achievements.append("🏃 Активность")
    if stats['avg_water'] >= user.daily_water_goal:
        achievements.append("💧 Гидратация")
    
    # 📈 Тренды
    trend_emoji = "📈" if stats['weight_trend'] and stats['weight_trend'] < 0 else "📊"
    weight_info = f"{trend_emoji} Тренд веса: {stats['weight_trend']:+.1f} кг" if stats['weight_trend'] else ""
    
    message = (
        f"📊 <b>Ваш прогресс {period_name}</b>\n\n"
        f"🔥 <b>Калории:</b>\n"
        f"   {calorie_status} Потреблено: {stats['total_cal_consumed']:.0f} ккал\n"
        f"   🔥 Сожжено: {stats['total_cal_burned']:.0f} ккал\n"
        f"   ⚖️ Баланс: {stats['total_cal_consumed'] - stats['total_cal_burned']:+.0f} ккал\n"
        f"   📊 Среднее: {stats['avg_cal_consumed']:.0f}/{user.daily_calorie_goal:.0f} ккал/день\n"
        f"   {calorie_bar}\n\n"
        f"💧 <b>Вода:</b>\n"
        f"   {water_status} Всего: {stats['total_water']:.0f} мл\n"
        f"   📊 Среднее: {stats['avg_water']:.0f}/{user.daily_water_goal:.0f} мл/день\n"
        f"   {water_bar}\n\n"
        f"{nutrition_card}\n\n"
    )
    
    # Добавляем достижения
    if achievements:
        message += f"🏆 <b>Ваши достижения:</b>\n"
        for achievement in achievements:
            message += f"   ✨ {achievement}\n"
        message += "\n"
    
    # Добавляем статистику
    message += (
        f"📈 <b>Статистика периода:</b>\n"
        f"   🍽️ Приемов пищи: {stats['meals_count']}\n"
        f"   🏃 Тренировок: {stats['activities_count']}\n"
        f"   📅 Дней в периоде: {stats['days_count']}\n"
    )
    
    if weight_info:
        message += f"   {weight_info}\n"
    
    # Мотивирующее завершение
    motivation = MessageTemplates.get_progress_motivation(stats, user)
    message += f"\n{motivation}"
    
    return message

async def _send_progress_charts(callback, user, session, period: str, period_name: str):
    """📊 Отправка графиков прогресса"""
    from services.plots import generate_weight_plot, generate_water_plot, generate_calorie_plot, generate_activity_plot
    from aiogram.types import BufferedInputFile
    
    # 📈 График веса
    weight_plot = await generate_weight_plot(user.id, session)
    if weight_plot:
        await callback.message.answer_photo(
            BufferedInputFile(weight_plot, filename="weight.png"),
            caption="📈 Динамика веса (все записи)",
        )

    # 💧 График воды
    water_plot = await generate_water_plot(
        user.id,
        session,
        period=period,
        daily_goal=user.daily_water_goal
    )
    if water_plot:
        await callback.message.answer_photo(
            BufferedInputFile(water_plot, filename="water.png"),
            caption=f"💧 Потребление воды {period_name}",
        )

    # 🔥 График калорий
    calorie_plot = await generate_calorie_plot(
        user.id,
        session,
        period=period,
        daily_goal=user.daily_calorie_goal
    )
    if calorie_plot:
        await callback.message.answer_photo(
            BufferedInputFile(calorie_plot, filename="calories.png"),
            caption=f"🔥 Потребление калорий {period_name}",
        )

    # 🏃 График активности
    activity_plot = await generate_activity_plot(
        user.id,
        session,
        period=period,
        daily_goal=None
    )
    if activity_plot:
        await callback.message.answer_photo(
            BufferedInputFile(activity_plot, filename="activity.png"),
            caption=f"🏃 Активность {period_name}",
        )

@router.callback_query(F.data == "log_water")
async def log_water_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для воды из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    from handlers.water import cmd_water
    await cmd_water(callback.message, state, user_id=callback.from_user.id)

@router.callback_query(F.data == "log_activity")
async def log_activity_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для активности из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    from handlers.activity import cmd_fitness
    await cmd_fitness(callback.message, state, user_id=callback.from_user.id)

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
    
    from handlers.ai_assistant import cmd_ask
    await cmd_ask(callback.message, state, user_id=callback.from_user.id)

async def handle_menu_callbacks(callback: CallbackQuery, state: FSMContext):
    """Обработка menu_* callback'ов"""
    from handlers.food import cmd_log_food
    from handlers.water import cmd_water
    from handlers.activity import cmd_fitness
    from handlers.meal_plan import cmd_meal_plan
    from handlers.ai_assistant import cmd_ask
    from handlers.steps import cmd_log_steps
    from utils.states import StepsStates
    
    if callback.data == "menu_food_photo":
        await callback.message.answer("📸 Отправьте фото еды")
        await callback.answer()
    
    elif callback.data == "menu_food_manual":
        await cmd_log_food(callback.message, state, user_id=callback.from_user.id)
        await callback.answer()
    
    elif callback.data == "menu_meal_plan":
        await cmd_meal_plan(callback.message, state, user_id=callback.from_user.id)
        await callback.answer()
    
    elif callback.data == "menu_ai":
        await cmd_ask(callback.message, state, user_id=callback.from_user.id)
        await callback.answer()
    
    elif callback.data == "menu_water":
        await cmd_water(callback.message, state, user_id=callback.from_user.id)
        await callback.answer()
    
    elif callback.data == "menu_activity":
        await cmd_fitness(callback.message, state, user_id=callback.from_user.id)
        await callback.answer()
    
    elif callback.data == "menu_steps":
        await state.set_state(StepsStates.waiting_for_steps)
        await callback.message.answer("👟 Введите количество шагов (только число):")
        await callback.answer()
    
    elif callback.data == "menu_profile_view":
        await display_profile(callback, callback.from_user.id, state)
        await callback.answer()
    
    elif callback.data == "menu_profile_edit":
        await edit_profile(callback.message, state, user_id=callback.from_user.id)
        await callback.answer()
    
    elif callback.data == "menu_log_weight":
        await cmd_log_weight(callback.message, state)
        await callback.answer()
    
    elif callback.data == "menu_back":
        await callback.message.delete()
        await callback.message.answer(
            "🏠 Главное меню",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
    
    else:
        logger.info(f"🔍 DEBUG: Неизвестный menu callback: {callback.data}")
        await callback.answer()

@router.callback_query(F.data == "use_ingredients_instead")
async def use_ingredients_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для 'нет, это ингредиент'"""
    await callback.answer()
    from handlers.media_handlers import use_ingredients_callback
    await use_ingredients_callback(callback, state)

@router.callback_query(F.data.startswith("progress_"))
async def progress_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для progress_ callback"""
    await period_callback_internal(callback, state)

# ========== Конец файла ==========
