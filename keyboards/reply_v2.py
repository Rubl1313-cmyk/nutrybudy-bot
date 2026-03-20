"""
keyboards/reply_v2.py
Премиальная клавиатура с современным дизайном
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_keyboard_v2() -> ReplyKeyboardMarkup:
    """
    Основная премиум клавиатура с эмодзи
    """
    builder = ReplyKeyboardBuilder()

    # 🔥 Основные действия (3 в ряд)
    builder.add(KeyboardButton(text="🍽️ Записать еду"))
    builder.add(KeyboardButton(text="💧 Вода"))
    builder.add(KeyboardButton(text="🤖 AI Ассистент"))
    
    # 📊 Прогресс и статистика
    builder.add(KeyboardButton(text="📊 Прогресс"))
    builder.add(KeyboardButton(text="📈 Статистика"))
    builder.add(KeyboardButton(text="🏆 Достижения"))
    
    # 👤 Профиль и настройки
    builder.add(KeyboardButton(text="👤 Профиль"))
    builder.add(KeyboardButton(text="⚙️ Настройки"))
    builder.add(KeyboardButton(text="❓ Помощь"))

    builder.adjust(3, 3, 3)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="✨ Выберите действие..."
    )

def get_profile_keyboard() -> ReplyKeyboardMarkup:
    """
    Премиум клавиатура для профиля
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="📊 Мои данные"))
    builder.add(KeyboardButton(text="🎯 Цели"))
    builder.add(KeyboardButton(text="🏆 Достижения"))
    
    builder.add(KeyboardButton(text="⚖️ Записать вес"))
    builder.add(KeyboardButton(text="📏 Замеры тела"))
    builder.add(KeyboardButton(text="📈 Анализ"))
    
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(3, 3, 1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="👤 Управление профилем..."
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
    Премиум клавиатура для быстрого ввода воды
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="💧 200 мл"))
    builder.add(KeyboardButton(text="💧 250 мл"))
    builder.add(KeyboardButton(text="💧 350 мл"))
    builder.add(KeyboardButton(text="💧 500 мл"))
    builder.add(KeyboardButton(text="💧 750 мл"))
    builder.add(KeyboardButton(text="💧 1000 мл"))
    
    builder.add(KeyboardButton(text="💧 Свой объем"))
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(3, 3, 2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="💧 Сколько выпили?"
    )

def get_activity_keyboard() -> ReplyKeyboardMarkup:
    """
    Премиум клавиатура для ввода активности
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="🏃 Бег"))
    builder.add(KeyboardButton(text="🚴 Велосипед"))
    builder.add(KeyboardButton(text="🏋️ Тренировка"))
    
    builder.add(KeyboardButton(text="🧘 Йога"))
    builder.add(KeyboardButton(text="🚶 Ходьба"))
    builder.add(KeyboardButton(text="🏊 Плавание"))
    
    builder.add(KeyboardButton(text="🎾 Другое"))
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(3, 3, 2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="🏃‍♂️ Какая была активность?"
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
    Премиум клавиатура для просмотра прогресса
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="📅 Сегодня"))
    builder.add(KeyboardButton(text="📆 Неделя"))
    builder.add(KeyboardButton(text="🗓️ Месяц"))
    
    builder.add(KeyboardButton(text="📊 Всё время"))
    builder.add(KeyboardButton(text="📈 Графики"))
    builder.add(KeyboardButton(text="📉 Тренды"))
    
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(3, 3, 1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="📊 Выберите период..."
    )

def get_food_keyboard() -> ReplyKeyboardMarkup:
    """
    Премиум клавиатура для записи пищи
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="📸 Фото + AI"))
    builder.add(KeyboardButton(text="✏️ Текстом"))
    builder.add(KeyboardButton(text="⚡ Быстро"))
    
    builder.add(KeyboardButton(text="🍳 Завтрак"))
    builder.add(KeyboardButton(text="🍽️ Обед"))
    builder.add(KeyboardButton(text="🌙 Ужин"))
    builder.add(KeyboardButton(text="🥨 Перекус"))
    
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(3, 4, 1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="🍽️ Как запишем прием пищи?"
    )

def get_help_keyboard() -> ReplyKeyboardMarkup:
    """
    Премиум клавиатура помощи
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="📋 Команды"))
    builder.add(KeyboardButton(text="🚀 Возможности"))
    builder.add(KeyboardButton(text="💬 Поддержка"))
    
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(2, 2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="❓ Что вас интересует?"
    )

def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    """
    Премиум клавиатура подтверждения
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="✅ Подтвердить"))
    builder.add(KeyboardButton(text="❌ Отмена"))

    builder.adjust(2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )

def get_units_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура системы единиц (только метрическая)
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="📏 Метрическая система"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    
    builder.adjust(1, 1)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Система единиц..."
    )

def get_notifications_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура настроек уведомлений (только вода)
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="💧 Напоминания о воде"))
    builder.add(KeyboardButton(text=" Главное меню"))
    
    builder.adjust(1, 1)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Настройки напоминаний..."
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
