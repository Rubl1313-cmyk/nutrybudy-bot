"""
keyboards/reply_v2.py
Вспомогательные клавиатуры для бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_progress_keyboard() -> ReplyKeyboardMarkup:
    """
    Премиум клавиатура для просмотра прогресса
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="📅 Сегодня"))
    builder.add(KeyboardButton(text="📆 Неделя"))
    builder.add(KeyboardButton(text="🗓️ Месяц"))

    builder.add(KeyboardButton(text="📊 Всё время"))
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(3, 2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="📊 Выберите период..."
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
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(2, 1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="❓ Что вас интересует?..."
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
