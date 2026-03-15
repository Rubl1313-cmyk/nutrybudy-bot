"""
Общие команды: /start, /help, /cancel, и интерактивное меню помощи.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

from keyboards.reply_v2 import get_main_keyboard_v2
from keyboards.inline import get_progress_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Приветствие нового пользователя"""
    await state.clear()
    
    user_name = message.from_user.first_name or "Пользователь"
    
    welcome_text = f"""✨ Привет, {user_name}! Я — ваш персональный AI-помощник по здоровью.

🤖 <b>Что я умею:</b>
• 🍽️ **Записывать приём пищи** — просто опишите, что съели, или отправьте фото
• 💧 **Отслеживать воду** — напишите, сколько выпили
• 🏃 **Учитывать активность и шаги** — «пробежал 5 км» или «10000 шагов»
• ⚖️ **Анализировать вес и прогресс** — покажу графики и дам прогноз
• 🧬 **Рассчитывать композицию тела** — индекс массы тела (ИМТ), процент жира, мышечную массу и нормы
• 🤖 **Отвечать на любые вопросы** о питании, тренировках и здоровье

💬 <b>Как общаться?</b>
Просто пишите мне всё, что считаете нужным, на естественном языке.
Я сам пойму, что нужно: записать еду, показать прогресс или дать совет.

👉 <b>Примеры:</b>
• «Сегодня на обед съел 200г куриной грудки с гречкой»
• «Выпила 3 стакана воды»
• «Какой у меня прогресс за неделю?»
• «Посоветуй рецепт ужина с высоким содержанием белка»

<b>⚠️ Важно:</b> Для точного расчета КБЖУ и персональных рекомендаций сначала настройте профиль командой /set_profile

**Выберите действие в меню ниже или просто задайте вопрос.**"""
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    """Вызывает интерактивное меню помощи."""
    await state.clear()
    await show_help_menu(message)

@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего действия."""
    await state.clear()
    await message.answer(
        "❌ <b>Действие отменено</b>\n\n"
        "Используй кнопки меню для навигации.",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text == "🏠 Главное меню")
async def cmd_main_menu(message: Message, state: FSMContext):
    """Возврат в главное меню."""
    await state.clear()
    await message.answer(
        "🏠 <b>Главное меню</b>",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

async def show_help_menu(event: Message | CallbackQuery):
    """Отображает главное меню помощи с инлайн-кнопками."""
    text = (
        "📚 <b>Разделы помощи</b>\n\n"
        "Выбери тему, чтобы узнать подробнее:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Питание", callback_data="help_food")],
        [InlineKeyboardButton(text="💧 Вода и активность", callback_data="help_water")],
        [InlineKeyboardButton(text="📊 Прогресс", callback_data="help_progress")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="help_profile")],
        [InlineKeyboardButton(text="🤖 AI Помощник", callback_data="help_ai")],
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
    if data == "help_food":
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
    elif data == "help_water":
        text = (
            "💧 <b>Вода и активность</b>\n\n"
            "💧 <b>Записать воду</b> – выбери объём из предложенных или введи вручную.\n"
            "   <i>Пример: «250 мл» или «стакан воды»</i>\n\n"
            "👟 <b>Записать шаги</b> – введи количество шагов, я пересчитаю в километры и калории.\n"
            "   <i>Пример: «прошёл 5000 шагов»</i>\n\n"
            "🏃 <b>Записать активность</b> – выбери тип тренировки и укажи длительность.\n"
            "   <i>Пример: «бег 30 минут»</i>"
        )
    elif data == "help_progress":
        text = (
            "📊 <b>Прогресс</b>\n\n"
            "📈 <b>Статистика</b> – просмотр потреблённых калорий, воды, веса и активности.\n"
            "📅 <b>Периоды</b> – можно посмотреть статистику за день, неделю или месяц.\n"
            "📉 <b>Графики</b> – наглядная динамика изменений веса и потребления."
        )
    elif data == "help_profile":
        text = (
            "👤 <b>Пррофиль</b>\n\n"
            "⚖️ <b>Данные</b> – вес, рост, возраст, пол, уровень активности, цель, город.\n"
            "📊 <b>Нормы</b> – я автоматически рассчитаю дневную норму калорий, БЖУ и воды.\n"
            "✏️ <b>Редактирование</b> – можно изменить данные в любое время."
        )
    elif data == "help_ai":
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

# Обработчики для reply-кнопок из старого common.py
@router.message(F.text == "📊 Мой прогресс")
async def progress_message(message: Message, state: FSMContext):
    """Обработчик прогресса с мотивацией"""
    from handlers.progress import cmd_progress
    await cmd_progress(message, state)

@router.message(F.text == "👤 Мой профиль")
async def profile_message(message: Message, state: FSMContext):
    """Обработчик профиля с персонализацией"""
    from handlers.profile import cmd_profile
    await cmd_profile(message, state)

@router.message(F.text == "❓ Помощь")
async def help_message(message: Message, state: FSMContext):
    """Обработчик помощи с дружелюбным подходом"""
    await cmd_help(message, state)

# Обработчик для callback прогресса
async def period_callback_internal(callback: CallbackQuery, state: FSMContext):
    """Внутренний обработчик выбора периода"""
    try:
        period = callback.data.split("_")[1]  # day / week / month / all
        user_id = callback.from_user.id

        await callback.answer(f"📊 Загружаю статистику...")
        await callback.message.delete()
        await state.clear()

        from database.db import get_session
        from database.models import User
        from sqlalchemy import select
        from datetime import datetime, timedelta

        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                await callback.message.answer(
                    "❌ Пользователь не найден.",
                    reply_markup=get_main_keyboard_v2()
                )
                return

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

            # Получаем статистику за период
            stats = await _get_period_stats(user.id, session, start_date)
            
            # Создаем сообщение с прогрессом
            progress_message = await _create_progress_message(user, stats, period_name, period)
            
            await callback.message.answer(
                progress_message, 
                reply_markup=get_main_keyboard_v2(), 
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Error in period callback: {e}")
        await callback.message.answer(
            "❌ Произошла ошибка при загрузке статистики. Попробуйте еще раз.",
            reply_markup=get_main_keyboard_v2()
        )

async def _get_period_stats(user_id: int, session, start_date) -> dict:
    """Получение статистики за период"""
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

async def _create_progress_message(user, stats: dict, period_name: str, period: str) -> str:
    """Создание сообщения с прогрессом"""
    
    # Определяем статусы и мотивацию
    calorie_status = "🎯" if stats['avg_cal_consumed'] <= user.daily_calorie_goal else "⚠️"
    water_status = "💧" if stats['avg_water'] >= user.daily_water_goal else "💦"
    
    # Формируем сообщение
    message = f"📊 <b>Статистика {period_name}</b>\n\n"
    
    # Калории
    message += f"🔥 <b>Калории:</b> {stats['total_cal_consumed']:.0f} ккал\n"
    message += f"   Среднее: {stats['avg_cal_consumed']:.0f} ккал/день {calorie_status}\n"
    message += f"   Норма: {user.daily_calorie_goal:.0f} ккал\n\n"
    
    # БЖУ
    message += f"🥩 <b>Белки:</b> {stats['total_protein']:.0f}г (среднее {stats['avg_protein']:.0f}г/день)\n"
    message += f"🥑 <b>Жиры:</b> {stats['total_fat']:.0f}г (среднее {stats['avg_fat']:.0f}г/день)\n"
    message += f"🍚 <b>Углеводы:</b> {stats['total_carbs']:.0f}г (среднее {stats['avg_carbs']:.0f}г/день)\n\n"
    
    # Вода
    message += f"💧 <b>Вода:</b> {stats['total_water']:.0f} мл\n"
    message += f"   Среднее: {stats['avg_water']:.0f} мл/день {water_status}\n"
    message += f"   Норма: {user.daily_water_goal:.0f} мл\n\n"
    
    # Активность
    if stats['total_cal_burned'] > 0:
        message += f"🏃 <b>Активность:</b> {stats['total_cal_burned']:.0f} ккал сожжено\n"
        message += f"   Тренировок: {stats['activities_count']}\n\n"
    
    # Вес
    if stats['weight_trend'] is not None:
        trend_emoji = "📈" if stats['weight_trend'] > 0 else "📉" if stats['weight_trend'] < 0 else "➡️"
        message += f"⚖️ <b>Вес:</b> {stats['latest_weight']:.1f} кг {trend_emoji}\n"
        if stats['weight_trend'] != 0:
            message += f"   Изменение: {stats['weight_trend']:+.1f} кг за {period_name}\n\n"
    
    # Мотивация
    if stats['avg_cal_consumed'] <= user.daily_calorie_goal and stats['avg_water'] >= user.daily_water_goal:
        message += "🎉 <b>Отличная работа!</b> Вы придерживаетесь норм калорий и воды!"
    elif stats['avg_cal_consumed'] <= user.daily_calorie_goal:
        message += "💪 <b>Хорошо!</b> Калории в норме, не забывайте пить воду!"
    elif stats['avg_water'] >= user.daily_water_goal:
        message += "💧 <b>Отлично!</b> Водный режим соблюден, следите за калориями!"
    else:
        message += "📝 <b>Совет:</b> Старайтесь соблюдать нормы калорий и пить больше воды."
    
    return message

# Универсальный обработчик callback
@router.callback_query()
async def universal_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Универсальный обработчик всех callback"""
    data = callback.data
    
    # Обработка period_ callback
    if data.startswith("period_"):
        await period_callback_internal(callback, state)
        return
    
    # Обработка help_ callback
    if data.startswith("help_"):
        await help_callbacks(callback)
        return
    
    # Другие callback
    logger.warning(f"Unknown callback: {data}")
    await callback.answer()
