"""
keyboards/reply_v2.py
Новая основная клавиатура с улучшенным дизайном
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard_v2() -> ReplyKeyboardMarkup:
    """
    Основная клавиатура с эмодзи
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="🍽️ Записать прием пищи"))
    builder.add(KeyboardButton(text="💧 Записать воду"))
    builder.add(KeyboardButton(text="🤖 Спросить AI"))
    builder.add(KeyboardButton(text="📊 Прогресс"))
    builder.add(KeyboardButton(text="👤 Профиль"))
    builder.add(KeyboardButton(text="❓ Помощь"))
    
    builder.adjust(3, 3)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )

def get_profile_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для действий в профиле
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="✏️ Редактировать профиль"))
    builder.add(KeyboardButton(text="📊 Полный анализ"))
    builder.add(KeyboardButton(text="⚖️ Записать вес"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )

def get_quick_actions_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура быстрых действий (показывается дополнительно)
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="[WEIGHT] Записать вес"))
    builder.add(KeyboardButton(text="[ACTIVITY] Активность"))
    builder.add(KeyboardButton(text="[WEATHER] Погода"))
    
    builder.adjust(3)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Быстрые действия..."
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для отмены действий
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="[CANCEL] Отмена"))
    builder.add(KeyboardButton(text="[MENU] Главное меню"))
    
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )

def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура настроек
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="[PROFILE] Профиль"))
    builder.add(KeyboardButton(text="[NOTIFICATIONS] Уведомления"))
    builder.add(KeyboardButton(text="[UNITS] Единицы"))
    builder.add(KeyboardButton(text="[MENU] Главное меню"))
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Настройки..."
    )

def get_water_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для быстрого ввода воды
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="💧 1 стакан"))
    builder.add(KeyboardButton(text="💧 2 стакана"))
    builder.add(KeyboardButton(text="💧 500 мл"))
    builder.add(KeyboardButton(text="💧 1 литр"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите объем..."
    )

def get_activity_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для быстрого ввода активности
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="[RUNNING] Бег"))
    builder.add(KeyboardButton(text="[WALKING] Ходьба"))
    builder.add(KeyboardButton(text="[GYM] Тренировка"))
    builder.add(KeyboardButton(text="[YOGA] Йога"))
    builder.add(KeyboardButton(text="[MENU] Главное меню"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите активность..."
    )

def get_ai_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для быстрых AI-запросов
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="[WEATHER] Погода"))
    builder.add(KeyboardButton(text="[RECIPE] Рецепт"))
    builder.add(KeyboardButton(text="[CALCULATE] Рассчитать КБЖУ"))
    builder.add(KeyboardButton(text="[ADVICE] Общий вопрос"))
    builder.add(KeyboardButton(text="[MENU] Главное меню"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите тип запроса..."
    )

def get_progress_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для просмотра прогресса
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="📅 Сегодня"))
    builder.add(KeyboardButton(text="📅 Неделя"))
    builder.add(KeyboardButton(text="📅 Месяц"))
    builder.add(KeyboardButton(text="📊 Всё время"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите период..."
    )

def get_food_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для записи пищи
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="📸 Фото еды"))
    builder.add(KeyboardButton(text="✏️ Текстом"))
    builder.add(KeyboardButton(text="⚡ Быстрый ввод"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Как записать прием пищи..."
    )

def get_help_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура помощи
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="📋 Команды"))
    builder.add(KeyboardButton(text="🚀 Возможности"))
    builder.add(KeyboardButton(text="💬 Поддержка"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Что вас интересует..."
    )

def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура подтверждения
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="✅ Да"))
    builder.add(KeyboardButton(text="❌ Нет"))
    
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите вариант..."
    )

def get_units_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура выбора системы единиц
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="📏 Метрические"))
    builder.add(KeyboardButton(text="📏 Имперские"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(2, 1)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите систему единиц..."
    )

def get_notifications_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура настроек уведомлений
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="� Напоминания о воде"))
    builder.add(KeyboardButton(text="🔔 Напоминания о еде"))
    builder.add(KeyboardButton(text="🔔 Напоминания об активности"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Настройки уведомлений..."
    )

def get_statistics_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура статистики
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="🔥 Калории"))
    builder.add(KeyboardButton(text="⚖️ Вес"))
    builder.add(KeyboardButton(text="💧 Вода"))
    builder.add(KeyboardButton(text="🏃 Активность"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите статистику..."
    )

def get_back_keyboard() -> ReplyKeyboardMarkup:
    """
    Простая клавиатура с кнопкой "Назад"
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔙 Назад"))
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Нажмите для возврата..."
    )

def get_empty_keyboard() -> ReplyKeyboardMarkup:
    """
    Пустая клавиатура (скрывает клавиатуру)
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[],
        one_time_keyboard=False
    )
