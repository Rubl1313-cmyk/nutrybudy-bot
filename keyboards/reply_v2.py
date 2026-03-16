"""
keyboards/reply_v2.py
Новая основная клавиатура с улучшенным дизайном
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard_v2() -> ReplyKeyboardMarkup:
    """
    Новая основная клавиатура с 2 строками по 3 кнопки
    """
    builder = ReplyKeyboardBuilder()
    
    # Первая строка
    builder.add(KeyboardButton(text="🍽️ Записать приём пищи"))
    builder.add(KeyboardButton(text="💧 Записать воду"))
    builder.add(KeyboardButton(text="🤖 Спросить AI"))
    
    # Вторая строка
    builder.add(KeyboardButton(text="📊 Прогресс"))
    builder.add(KeyboardButton(text="👤 Профиль"))
    builder.add(KeyboardButton(text="❓ Помощь"))
    
    # Настройка
    builder.adjust(3, 3)  # 3 кнопки в каждой строке
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Напишите или выберите действие..."
    )

def get_profile_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура профиля с кнопкой полного анализа
    """
    builder = ReplyKeyboardBuilder()
    
    # Первая строка
    builder.add(KeyboardButton(text="📝 Редактировать профиль"))
    builder.add(KeyboardButton(text="🧬 Полный анализ"))
    builder.add(KeyboardButton(text="⚖️ Записывать вес"))
    
    # Вторая строка
    builder.add(KeyboardButton(text="🔙 Главное меню"))
    
    # Настройка
    builder.adjust(3, 2)  # 3 кнопки в первой строке, 1 во второй
    
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
    
    builder.add(KeyboardButton(text="⚖️ Записать вес"))
    builder.add(KeyboardButton(text="🏃 Активность"))
    builder.add(KeyboardButton(text="🌦️ Погода"))
    
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
    builder.add(KeyboardButton(text="❌ Отмена"))
    builder.add(KeyboardButton(text="🔙 Главное меню"))
    
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_profile_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для действий в профиле
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="📝 Редактировать профиль"))
    builder.add(KeyboardButton(text="🧬 Полный анализ"))
    builder.add(KeyboardButton(text="⚖️ Записать вес"))
    builder.add(KeyboardButton(text="🔙 Главное меню"))
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
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
    builder.add(KeyboardButton(text="🔙 Главное меню"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_activity_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для быстрого ввода активности
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="🏃 Бег"))
    builder.add(KeyboardButton(text="🚶 Ходьба"))
    builder.add(KeyboardButton(text="🏋️ Тренировка"))
    builder.add(KeyboardButton(text="🧘 Йога"))
    builder.add(KeyboardButton(text="🔙 Главное меню"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_ai_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для быстрых AI-запросов
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="🌦️ Погода"))
    builder.add(KeyboardButton(text="🍳 Рецепт"))
    builder.add(KeyboardButton(text="🧮 Рассчитать КБЖУ"))
    builder.add(KeyboardButton(text="💬 Общий вопрос"))
    builder.add(KeyboardButton(text="🔙 Главное меню"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )
