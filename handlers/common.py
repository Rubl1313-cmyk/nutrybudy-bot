"""
Общие команды: /start, /help, /cancel и интерактивное меню помощи.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

from keyboards.reply_v2 import get_main_keyboard_v2, get_confirm_keyboard, get_food_keyboard, get_help_keyboard
from keyboards.inline import get_progress_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Приветствие нового пользователя"""
    await state.clear()
    
    user_name = message.from_user.first_name or "Пользователь"
    
    welcome_text = f"""✨ Добро пожаловать, {user_name}! Я ваш персональный AI ассистент по здоровью.

🤖 <b>Что я могу делать:</b>
• 🍽️ Отслеживать питание - просто опишите, что вы съели, или отправьте фото
• 💧 Отслеживать воду - напишите, сколько выпили
• 🏃‍♂️ Отслеживать активность - записывайте тренировки и упражнения
• ⚖️ Отслеживать вес - следите за изменениями веса
• 📊 Показывать прогресс - детальная статистика за любой период
• 🤖 AI ассистент - задавайте вопросы о питании и здоровье
• 🍽️ Планы питания - персональные рекомендации
• 🏆 Достижения - геймификация и мотивация

📋 <b>Быстрый старт:</b>
1. Настройте профиль: /set_profile
2. Запишите прием пищи: /food
3. Выпейте воды: /water
4. Посмотрите прогресс: /progress

⚠️ <b>Важно:</b> Сначала настройте профиль для персонализации рекомендаций!

🚀 <b>Начнём?</b>"""
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    """Показать справку"""
    await state.clear()
    
    help_text = """📖 <b>Справка по NutriBuddy Bot</b>

🤖 <b>Основные команды:</b>
/start - Запуск бота и приветствие
/help - Эта справка
/cancel - Отмена текущего действия

👤 <b>Профиль и настройки:</b>
/set_profile - Настроить личный профиль
/profile - Мой профиль
/settings - Настройки бота

🍽️ <b>Питание:</b>
/food - Записать прием пищи
/meal_plan - План питания
/ask - Задать вопрос AI ассистенту

💧 <b>Вода и напитки:</b>
/water - Записать воду
/drink - Записать напиток

🏃‍♂️ <b>Активность:</b>
/fitness - Записать тренировку
/activity - Записать активность

⚖️ <b>Вес:</b>
/weight - Записать вес
/weight_stats - Статистика веса

📊 <b>Прогресс и статистика:</b>
/progress - Мой прогресс
/stats - Детальная статистика
/achievements - Мои достижения

🤖 <b>AI ассистент:</b>
/ask - Задать вопрос
/ai_help - Помощь по AI

💡 <b>Как использовать:</b>
1. Отправляйте текстовые сообщения с описанием еды
2. Отправляйте фото блюд для распознавания
3. Используйте кнопки меню для быстрого доступа
4. Следуйте подсказкам бота

🎯 <b>Советы:</b>
• Настройте профиль для точных рекомендаций
• Записывайте питание регулярно
• Пейте достаточно воды
• Отслеживайте прогресс для мотивации"""
    
    await message.answer(
        help_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего действия"""
    await state.clear()
    
    cancel_text = """❌ <b>Действие отменено</b>

🏠 Возвращаю в главное меню...

💡 <b>Совет:</b> Используйте /help для просмотра всех команд"""
    
    await message.answer(
        cancel_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    """Начало настройки профиля"""
    await state.clear()
    
    # Сразу начинаем настройку без подтверждения
    await state.set_state({"profile_step": "age"})
    
    text = """� <b>Шаг 1: Возраст</b>

Введите ваш возраст (полных лет):

� <b>Пример:</b> 25"""
    
    await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "start_profile_setup")
async def start_profile_setup(callback: CallbackQuery, state: FSMContext):
    """Начало настройки профиля"""
    await state.set_state({"profile_step": "age"})
    
    text = """👤 <b>Шаг 1: Возраст</b>

Введите ваш возраст (полных лет):

💡 <b>Пример:</b> 25"""
    
    await callback.message.edit_text(
        text,
        reply_markup=create_back_keyboard("cancel_profile"),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_profile_setup")
async def cancel_profile_setup(callback: CallbackQuery, state: FSMContext):
    """Отмена настройки профиля"""
    await state.clear()
    
    text = """❌ <b>Настройка профиля отменена</b>

🏠 Возвращаю в главное меню..."""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext):
    """Показать детальную статистику"""
    await state.clear()
    
    stats_text = """📈 <b>Детальная статистика</b>

Выберите период для просмотра:

📅 <b>Доступные периоды:</b>
• Сегодня - текущий день
• Неделя - последние 7 дней
• Месяц - последние 30 дней
• Всё время - вся история

📊 <b>Что включает статистика:</b>
• Питание (калории, БЖУ)
• Активность (минуты, калории)
• Вес (динамика)
• Вода (потребление)
• Выполнение целей"""
    
    await message.answer(
        stats_text,
        reply_markup=get_progress_menu(),
        parse_mode="HTML"
    )

@router.message(Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    """Запись приема пищи"""
    await state.clear()
    
    food_text = """🍽️ <b>Запись приема пищи</b>

Выберите способ записи:

📸 <b>По фото:</b>
• Сделайте фото блюда
• AI распознает ингредиенты
• Автоматический расчет калорий

✍️ <b>Вручную:</b>
• Опишите что съели
• Укажите количество
• Получите расчет БЖУ

💡 <b>Примеры описаний:</b>
• "Гречка с курицей 200г"
• "Салат Цезарь 150г"
• "Яблоко 1 шт"

🚀 <b>Выберите способ:</b>"""
    
    await message.answer(
        food_text,
        reply_markup=get_food_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "help_menu")
async def help_menu_callback(callback: CallbackQuery):
    """Обработчик меню помощи"""
    help_text = """📖 <b>Меню помощи</b>

Выберите раздел:

📚 <b>Руководства:</b>
• Как начать пользоваться
• Настройка профиля
• Запись питания
• Отслеживание прогресса

❓ <b>Частые вопросы:</b>
• Как работает AI
• Точность распознавания
• Синхронизация данных
• Конфиденциальность

🎥 <b>Видеоуроки:</b>
• Основные функции
• Продвинутые возможности

💬 <b>Поддержка:</b>
• Связаться с нами
• Сообщить о проблеме"""
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_help_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    main_text = """🏠 <b>Главное меню</b>

Выберите действие:

🍽️ <b>Питание:</b>
• Записать прием пищи
• План питания
• AI ассистент

💧 <b>Здоровье:</b>
• Выпить воды
• Записать активность
• Записать вес

📊 <b>Прогресс:</b>
• Мой прогресс
• Статистика
• Достижения

⚙️ <b>Настройки:</b>
• Мой профиль
• Настройки бота"""
    
    await callback.message.edit_text(
        main_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )
    await callback.answer()

# Вспомогательные функции

def create_back_keyboard(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Создать кнопку 'Назад'"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data)]
    ])
    return keyboard

def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создать клавиатуру главного меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🍽️ Питание", callback_data="nutrition")],
        [InlineKeyboardButton(text="🏃‍♂️ Активность", callback_data="activity")],
        [InlineKeyboardButton(text="📊 Прогресс", callback_data="progress")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
    ])
    return keyboard

async def handle_unknown_command(message: Message):
    """Обработка неизвестной команды"""
    text = """❓ <b>Неизвестная команда</b>

Используйте /help для просмотра всех доступных команд.

🏠 <b>Главное меню:</b>"""
    
    await message.answer(
        text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )
