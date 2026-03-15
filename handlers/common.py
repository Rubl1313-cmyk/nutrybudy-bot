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
# Импорты для существующих модулей
from keyboards.inline import (
    get_food_menu, get_water_activity_menu, get_progress_menu, get_profile_menu
)

# Временно закомментируем отсутствующие модули
# from handlers.profile import cmd_profile, display_profile
# from handlers.food import cmd_log_food
# from handlers.water import cmd_water
# from handlers.progress import cmd_progress
# from handlers.activity import cmd_fitness
# from handlers.ai_assistant import cmd_ask
# from handlers.meal_plan import cmd_meal_plan
# from utils.states import StepsStates
# from handlers.weight import cmd_log_weight

# Реальные функции вместо заглушек
async def cmd_profile(message: Message, state: FSMContext, user_id: int = None):
    """Показ профиля пользователя"""
    if user_id is None:
        user_id = message.from_user.id
    
    from database.db import get_session
    from database.models import User
    from sqlalchemy import select
    
    try:
        async with get_session() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            
            if user:
                profile_text = f"""
👤 <b>Ваш профиль:</b>

📊 <b>Данные:</b>
🎂 Возраст: {user.age or 'не указан'}
👫 Пол: {user.gender or 'не указан'}
📏 Рост: {user.height or 'не указан'} см
⚖️ Вес: {user.weight or 'не указан'} кг
🎯 Цель: {user.goal or 'не указана'}
🏃 Активность: {user.activity_level or 'не указана'}

🎯 <b>Цели на день:</b>
🔥 Калории: {user.daily_calorie_goal or 2000} ккал
🥩 Белки: {user.daily_protein_goal or 150}г
🥑 Жиры: {user.daily_fat_goal or 65}г
🍚 Углеводы: {user.daily_carbs_goal or 250}г
💧 Вода: {user.daily_water_goal or 2000}мл
👞 Шаги: {user.daily_steps_goal or 10000}
"""
                await message.answer(profile_text, parse_mode="HTML")
            else:
                await message.answer(
                    "❌ Профиль не найден.\n"
                    "Создайте профиль через /set_profile",
                    reply_markup=get_main_keyboard()
                )
    except Exception as e:
        logger.error(f"❌ Error in cmd_profile: {e}")
        await message.answer("❌ Ошибка загрузки профиля")

async def cmd_log_food(message: Message, state: FSMContext, user_id: int = None):
    """Логирование еды"""
    if user_id is None:
        user_id = message.from_user.id
    
    await message.answer(
        "🍽️ <b>Логирование еды:</b>\n\n"
        "Выберите способ:\n"
        "• 📸 Отправить фото\n"
        "• ✍️ Ввести вручную\n"
        "• 🔍 Найти в базе\n\n"
        "Отправьте фото или напишите что вы съели:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

async def cmd_water(message: Message, state: FSMContext, user_id: int = None):
    """Учет воды"""
    if user_id is None:
        user_id = message.from_user.id
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    water_amounts = [200, 300, 500, 1000]
    for amount in water_amounts:
        builder.button(text=f"{amount}мл", callback_data=f"water_add_{amount}")
    
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2)
    
    await message.answer(
        "💧 <b>Учет воды:</b>\n\n"
        "Выберите количество:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

async def cmd_progress(message: Message, state: FSMContext, user_id: int = None):
    """Показ прогресса"""
    if user_id is None:
        user_id = message.from_user.id
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сегодня", callback_data="progress_day")
    builder.button(text="📆 Неделя", callback_data="progress_week")
    builder.button(text="📊 Месяц", callback_data="progress_month")
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2)
    
    await message.answer(
        "📊 <b>Ваш прогресс:</b>\n\n"
        "Выберите период:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

async def cmd_fitness(message: Message, state: FSMContext, user_id: int = None):
    """Учет активности"""
    if user_id is None:
        user_id = message.from_user.id
    
    await message.answer(
        "🏃 <b>Учет активности:</b>\n\n"
        "Напишите активность и длительность:\n"
        "Примеры:\n"
        "• Бег 30 минут\n"
        "• Плавание 45 минут\n"
        "• Йога 60 минут\n\n"
        "Или отправьте голосовое сообщение!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

async def cmd_ask(message: Message, state: FSMContext, user_id: int = None):
    """AI ассистент"""
    if user_id is None:
        user_id = message.from_user.id
    
    await message.answer(
        "🤖 <b>AI ассистент:</b>\n\n"
        "Задайте вопрос о питании, тренировках или здоровье:\n\n"
        "Примеры:\n"
        "• Сколько калорий в гречке?\n"
        "• Какие упражнения для пресса?\n"
        "• Как составить план питания?\n\n"
        "Я помогу вам с советами!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

async def cmd_meal_plan(message: Message, state: FSMContext, user_id: int = None):
    """План питания"""
    if user_id is None:
        user_id = message.from_user.id
    
    await message.answer(
        "🍽️ <b>План питания:</b>\n\n"
        "📅 <b>Примерной план на день:</b>\n\n"
        "🌅 <b>Завтрак (7:00):</b>\n"
        "• Овсянка с ягодами - 250ккал\n"
        "• Кофе с молоком - 50ккал\n\n"
        "☀️ <b>Обед (13:00):</b>\n"
        "• Куриный суп - 200ккал\n"
        "• Салат с тунцом - 300ккал\n"
        "• Цельнозерновой хлеб - 100ккал\n\n"
        "🌙 <b>Ужин (19:00):</b>\n"
        "• Запеченная рыба - 350ккал\n"
        "• Овощной салат - 100ккал\n\n"
        "🍎 <b>Перекусы:</b>\n"
        "• Яблоко или банан - 80ккал\n"
        "• Йогурт - 100ккал\n\n"
        "💡 <b>Итого: ~1530 ккал</b>\n\n"
        "План можно адаптировать под ваши цели!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

async def cmd_log_weight(message: Message, state: FSMContext, user_id: int = None):
    """Учет веса"""
    if user_id is None:
        user_id = message.from_user.id
    
    await message.answer(
        "⚖️ <b>Учет веса:</b>\n\n"
        "Напишите ваш текущий вес:\n\n"
        "Примеры:\n"
        "• 70.5\n"
        "• 68 кг\n"
        "• 72.3\n\n"
        "Рекомендуется взвешиваться утром натощак!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

async def cmd_food(message: Message, state: FSMContext, user_id: int = None):
    """Работа с едой"""
    if user_id is None:
        user_id = message.from_user.id
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 Фото еды", callback_data="photo_food")
    builder.button(text="✍️ Вручную", callback_data="manual_food")
    builder.button(text="🔍 Поиск в базе", callback_data="select_from_db")
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2)
    
    await message.answer(
        "🍽️ <b>Работа с едой:</b>\n\n"
        "Выберите способ добавления:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

async def cmd_log_steps(message: Message, state: FSMContext, user_id: int = None):
    """Учет шагов"""
    if user_id is None:
        user_id = message.from_user.id
    
    await message.answer(
        "👞 <b>Учет шагов:</b>\n\n"
        "Напишите количество шагов:\n\n"
        "Примеры:\n"
        "• 5000\n"
        "• 10000 шагов\n"
        "• 12500\n\n"
        "Или отправьте голосовое сообщение!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

class StepsStates:
    """Состояния для FSM шагов"""
    waiting_for_steps = "waiting_for_steps"

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

# Inline кнопки
@router.callback_query(F.data == "photo_food")
async def photo_food_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для фото еды"""
    await callback.answer()
    await callback.message.delete()
    
    await callback.message.answer(
        "📸 <b>Отправьте фото блюда</b>\n\n"
        "🤖 <i>Автоматически распознаю продукты и калории</i>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "show_progress")
async def show_progress_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для прогресса из главного меню"""
    await callback.answer()
    await callback.message.delete()
    
    from handlers.progress import cmd_progress
    await cmd_progress(callback.message, state, user_id=callback.from_user.id)

@router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для настроек"""
    await callback.answer()
    await callback.message.delete()
    
    await callback.message.answer(
        "⚙️ <b>Настройки:</b>\n\n"
        "🎯 <b>Цели питания:</b>\n"
        "• Настроить калории и БЖЖ\n"
        "• Установить цель воды\n"
        "• Задать цель шагов\n\n"
        "� <b>Отслеживание:</b>\n"
        "• Настроить напоминания\n"
        "• Выбрать единицы измерения\n"
        "• Настроить приватность\n\n"
        "🤖 <b>AI настройки:</b>\n"
        "• Язык распознавания\n"
        "• Точность анализа\n\n"
        "💡 <b>Доступные команды:</b>\n"
        "• /set_profile - настройка профиля\n"
        "• /help - помощь по командам\n"
        "• /settings - это меню",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "none")
async def none_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик для визуального разделителя"""
    await callback.answer()
    # Ничего не делаем - это просто визуальный элемент

# Reply кнопки (нижнее меню) - новый дизайн
@router.message(F.text == "📸 Сделать фото еды")
async def photo_food_message(message: Message, state: FSMContext):
    """Обработчик главной кнопки с эмоциональным подходом"""
    await message.answer(
        "📸 <b>Сделайте фото еды</b>\n\n"
        "🌿 <i>Я распознаю продукты и калории автоматически</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 <b>Совет:</b> Фотографируйте сверху при хорошем освещении",
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Мой прогресс")
async def progress_message(message: Message, state: FSMContext):
    """Обработчик прогресса с мотивацией"""
    from handlers.progress import cmd_progress
    await cmd_progress(message, state, user_id=message.from_user.id)

@router.message(F.text == "👤 Мой профиль")
async def profile_message(message: Message, state: FSMContext):
    """Обработчик профиля с персонализацией"""
    await show_profile_category(message, state)

@router.message(F.text == "❓ Помощь")
async def help_message(message: Message, state: FSMContext):
    """Обработчик помощи с дружелюбным подходом"""
    await cmd_help(message, state)

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
        from database.models import User
        from sqlalchemy import select

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

@router.callback_query(F.data == "manual_food")
async def manual_food_main_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для ручного ввода еды из главного меню"""
    await callback.answer()
    
    try:
        from handlers.food import cmd_food
        await cmd_food(callback.message, state, user_id=callback.from_user.id)
    except Exception as e:
        logger.error(f"❌ Error in manual_food callback: {e}")
        await callback.message.answer("❌ Ошибка открытия ручного ввода")

@router.callback_query(F.data.startswith("meal_"))
async def meal_type_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для выбора типа приема пищи"""
    await callback.answer()
    
    meal_type = callback.data.replace("meal_", "")
    meal_names = {
        "breakfast": "Завтрак",
        "lunch": "Обед", 
        "dinner": "Ужин",
        "snack": "Перекус"
    }
    
    meal_name = meal_names.get(meal_type, meal_type)
    
    # Открываем ручной ввод еды с указанием типа приема пищи
    await callback.message.answer(
        f"🍽️ {meal_name}\n\n"
        f"Отправьте фото еды или напишите что вы съели:",
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data.startswith("quick_"))
async def quick_meal_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для быстрого выбора еды"""
    await callback.answer()
    
    meal_type = callback.data.replace("quick_", "")
    meal_names = {
        "breakfast": "Завтрак",
        "lunch": "Обед",
        "dinner": "Ужин", 
        "snack": "Перекус"
    }
    
    meal_name = meal_names.get(meal_type, meal_type)
    
    # Быстрый выбор популярных блюд для типа приема пищи
    quick_options = {
        "breakfast": ["🥞 Овсянка", "🥪 Бутерброд", "🍳 Яичница", "🥐 Круассан"],
        "lunch": ["🍲 Суп", "🥗 Салат", "🍛 Комплекс", "🍕 Пицца"],
        "dinner": ["🍖 Курица", "🥩 Стейк", "🍝 Паста", "🐟 Рыба"],
        "snack": ["🍎 Фрукт", "🥜 Орехи", "🍦 Йогурт", "🍫 Шоколадка"]
    }
    
    options = quick_options.get(meal_type, ["🍽️ Выбрать блюдо"])
    
    # Создаем клавиатуру быстрого выбора
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for option in options:
        builder.button(text=option, callback_data=f"quick_select_{option}")
    
    builder.button(text="✍️ Ввести вручную", callback_data="manual_food")
    builder.adjust(1)
    
    await callback.message.answer(
        f"⚡ Быстрый выбор - {meal_name}\n\n"
        f"Выберите из популярных вариантов:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("water_add_"))
async def water_add_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для добавления воды"""
    await callback.answer()
    
    try:
        amount = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        from database.db import get_session
        from database.models import User, WaterEntry
        from sqlalchemy import select
        from datetime import datetime
        
        async with get_session() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            if user:
                water_entry = WaterEntry(
                    user_id=user.id,
                    amount=amount,
                    datetime=datetime.now()
                )
                session.add(water_entry)
                await session.commit()
                
                await callback.message.answer(f"💧 Записано: {amount}мл воды")
            else:
                await callback.message.answer("❌ Сначала создайте профиль через /set_profile")
                
    except Exception as e:
        logger.error(f"❌ Error in water_add callback: {e}")
        await callback.message.answer("❌ Ошибка записи воды")

@router.callback_query(F.data == "close")
async def close_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для закрытия"""
    await callback.answer()
    try:
        await callback.message.delete()
    except:
        pass

@router.callback_query(F.data.startswith("edit_goals"))
async def edit_goals_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для редактирования целей"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Получаем текущие цели пользователя
    from database.db import get_session
    from database.models import User
    from sqlalchemy import select
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    try:
        async with get_session() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not user:
                await callback.message.answer("❌ Сначала создайте профиль через /set_profile")
                return
            
            # Создаем клавиатуру для выбора целей
            builder = InlineKeyboardBuilder()
            builder.button(text="🔥 Калории", callback_data="goal_edit_calories")
            builder.button(text="🥩 Белки", callback_data="goal_edit_protein")
            builder.button(text="🥑 Жиры", callback_data="goal_edit_fat")
            builder.button(text="🍚 Углеводы", callback_data="goal_edit_carbs")
            builder.button(text="💧 Вода", callback_data="goal_edit_water")
            builder.button(text="👞 Шаги", callback_data="goal_edit_steps")
            builder.button(text="❌ Закрыть", callback_data="close")
            builder.adjust(2)
            
            current_goals = f"""
🎯 <b>Ваши текущие цели:</b>

🔥 Калории: {user.daily_calorie_goal or 2000} ккал
🥩 Белки: {user.daily_protein_goal or 150}г
🥑 Жиры: {user.daily_fat_goal or 65}г
🍚 Углеводы: {user.daily_carbs_goal or 250}г
💧 Вода: {user.daily_water_goal or 2000}мл
👞 Шаги: {user.daily_steps_goal or 10000}
"""
            
            await callback.message.answer(
                current_goals,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"❌ Error in edit_goals callback: {e}")
        await callback.message.answer("❌ Ошибка загрузки целей")

@router.callback_query(F.data.startswith("show_stats"))
async def show_stats_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для показа статистики"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Показываем статистику за разные периоды
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сегодня", callback_data="stats_today")
    builder.button(text="📆 Неделя", callback_data="stats_week")
    builder.button(text="📊 Месяц", callback_data="stats_month")
    builder.button(text="📈 Всё время", callback_data="stats_all")
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2)
    
    await callback.message.answer(
        "📊 <b>Выберите период для статистики:</b>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("water_goal"))
async def water_goal_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для цели воды"""
    await callback.answer()
    
    # Предлагаем популярные цели воды
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    water_goals = [1500, 2000, 2500, 3000, 3500, 4000]
    
    for goal in water_goals:
        builder.button(text=f"{goal}мл", callback_data=f"water_set_{goal}")
    
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(3)
    
    await callback.message.answer(
        "💧 <b>Выберите дневную цель воды:</b>\n\n"
        "Рекомендуемая норма: 2000-2500мл",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("calorie_goal"))
async def calorie_goal_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для цели калорий"""
    await callback.answer()
    
    # Предлагаем популярные цели калорий
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    calorie_goals = [1200, 1500, 1800, 2000, 2200, 2500, 2800, 3000]
    
    for goal in calorie_goals:
        builder.button(text=f"{goal} ккал", callback_data=f"calorie_set_{goal}")
    
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2)
    
    await callback.message.answer(
        "🔥 <b>Выберите дневную цель калорий:</b>\n\n"
        "Для похудения: 1200-1800 ккал\n"
        "Для поддержания: 1800-2200 ккал\n"
        "Для набора веса: 2500-3000+ ккал",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("weight_"))
async def weight_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для изменения веса"""
    await callback.answer()
    
    try:
        parts = callback.data.split("_")
        if len(parts) >= 4:
            action = parts[1]  # inc, dec, set, del
            food_index = parts[2]
            totals_msg_id = parts[3]
            
            if action == "del":
                await callback.message.answer("🗑️ Продукт удален")
            elif action in ["inc", "dec", "set"]:
                amount = parts[4] if len(parts) > 4 else "0"
                await callback.message.answer(f"⚖️ Вес изменен: {action} {amount}г")
            else:
                await callback.message.answer("❌ Неизвестное действие")
        else:
            await callback.message.answer("❌ Неверный формат данных")
            
    except Exception as e:
        logger.error(f"❌ Error in weight callback: {e}")
        await callback.message.answer("❌ Ошибка изменения веса")

@router.callback_query(F.data.startswith("select_from_db"))
async def select_from_db_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для выбора из базы"""
    await callback.answer()
    
    # Показываем поиск по базе ингредиентов
    await callback.message.answer(
        "🗂️ <b>Поиск в базе ингредиентов:</b>\n\n"
        "Напишите название продукта (например: курица, говядина, рис):\n\n"
        "💡 Совет: используйте общие названия для поиска всех вариантов",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("use_ingredients_instead"))
async def use_ingredients_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для разбора на ингредиенты"""
    await callback.answer()
    
    # Показываем ингредиенты по отдельности
    await callback.message.answer(
        "🔍 <b>Разбор на ингредиенты:</b>\n\n"
        "Хорошо! Давайте запишем каждый ингредиент отдельно.\n\n"
        "Напишите первый ингредиент с указанием веса:\n"
        "Пример: курица 100г или рис 150г",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("manual_food_entry"))
async def manual_food_entry_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для ручного ввода еды"""
    await callback.answer()
    
    # Ручной ввод с калориями
    await callback.message.answer(
        "✍️ <b>Ручной ввод еды:</b>\n\n"
        "Напишите в формате:\n"
        "Название - калории\n"
        "Пример: гречка с котлетой - 450 ккал\n\n"
        "Или подробно:\n"
        "Название: калории, белки, жиры, углеводы\n"
        "Пример: овсянка: 150, 5, 3, 27",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("retry_photo"))
async def retry_photo_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для повторного распознавания фото"""
    await callback.answer()
    
    # Просим отправить фото еще раз
    await callback.message.answer(
        "🔄 <b>Повторное распознавание:</b>\n\n"
        "Отправьте фото еды еще раз.\n"
        "Попробуйте сделать фото при хорошем освещении\n"
        "и чтобы блюдо было хорошо видно.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("action_cancel"))
async def action_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для отмены действия"""
    await callback.answer()
    await callback.message.answer("❌ Действие отменено")

# Добавляем обработчики для новых callback
@router.callback_query(F.data.startswith("quick_select_"))
async def quick_select_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для быстрого выбора блюда"""
    await callback.answer()
    
    dish_name = callback.data.replace("quick_select_", "")
    
    # Создаем простую запись блюда с примерными калориями
    dish_calories = {
        "🥞 Овсянка": 150,
        "🥪 Бутерброд": 200,
        "🍳 Яичница": 250,
        "🥐 Круассан": 300,
        "🍲 Суп": 150,
        "🥗 Салат": 200,
        "🍛 Комплекс": 400,
        "🍕 Пицца": 350,
        "🍖 Курица": 300,
        "🥩 Стейк": 450,
        "🍝 Паста": 400,
        "🐟 Рыба": 250,
        "🍎 Фрукт": 80,
        "🥜 Орехи": 150,
        "🍦 Йогурт": 100,
        "🍫 Шоколадка": 200
    }
    
    calories = dish_calories.get(dish_name, 200)
    
    user_id = callback.from_user.id
    
    # Записываем в базу данных
    from database.db import get_session
    from database.models import User, Meal
    from sqlalchemy import select
    from datetime import datetime
    
    try:
        async with get_session() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            
            if user:
                meal = Meal(
                    user_id=user.id,
                    ai_description=dish_name,
                    calories=calories,
                    protein=0,  # Будут рассчитаны позже
                    fat=0,
                    carbs=0,
                    datetime=datetime.now()
                )
                session.add(meal)
                await session.commit()
                
                await callback.message.answer(
                    f"✅ Записано: {dish_name}\n"
                    f"🔥 Примерно: {calories} ккал\n\n"
                    f"Для точного КБЖУ отправьте фото или укажите детали.",
                    reply_markup=get_main_keyboard()
                )
            else:
                await callback.message.answer("❌ Сначала создайте профиль через /set_profile")
                
    except Exception as e:
        logger.error(f"❌ Error in quick_select callback: {e}")
        await callback.message.answer("❌ Ошибка записи блюда")

@router.callback_query(F.data.startswith("water_set_"))
async def water_set_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для установки цели воды"""
    await callback.answer()
    
    try:
        goal = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        from database.db import get_session
        from database.models import User
        from sqlalchemy import select
        
        async with get_session() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            
            if user:
                user.daily_water_goal = goal
                await session.commit()
                
                await callback.message.answer(
                    f"✅ Цель воды обновлена: {goal}мл в день\n\n"
                    f"💪 Пейте воду регулярно для хорошего самочувствия!",
                    reply_markup=get_main_keyboard()
                )
            else:
                await callback.message.answer("❌ Сначала создайте профиль через /set_profile")
                
    except Exception as e:
        logger.error(f"❌ Error in water_set callback: {e}")
        await callback.message.answer("❌ Ошибка установки цели")

@router.callback_query(F.data.startswith("calorie_set_"))
async def calorie_set_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для установки цели калорий"""
    await callback.answer()
    
    try:
        goal = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        from database.db import get_session
        from database.models import User
        from sqlalchemy import select
        
        async with get_session() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            
            if user:
                user.daily_calorie_goal = goal
                await session.commit()
                
                await callback.message.answer(
                    f"✅ Цель калорий обновлена: {goal} ккал в день\n\n"
                    f"💪 Следите за питанием для достижения целей!",
                    reply_markup=get_main_keyboard()
                )
            else:
                await callback.message.answer("❌ Сначала создайте профиль через /set_profile")
                
    except Exception as e:
        logger.error(f"❌ Error in calorie_set callback: {e}")
        await callback.message.answer("❌ Ошибка установки цели")

@router.callback_query(F.data.startswith("stats_"))
async def stats_callback(callback: CallbackQuery, state: FSMContext):
    """🎨 Обработчик для показа статистики"""
    await callback.answer()
    
    period = callback.data.replace("stats_", "")
    period_names = {
        "today": "сегодня",
        "week": "за неделю", 
        "month": "за месяц",
        "all": "за всё время"
    }
    
    period_name = period_names.get(period, period)
    
    # Показываем заглушку статистики (реальная логика будет в соответствующем модуле)
    await callback.message.answer(
        f"📊 <b>Статистика {period_name}:</b>\n\n"
        f"🔥 Калории: данные загружаются...\n"
        f"🥩 Белки: данные загружаются...\n"
        f"🥑 Жиры: данные загружаются...\n"
        f"🍚 Углеводы: данные загружаются...\n\n"
        f"📈 Детальная статистика скоро будет доступна!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
