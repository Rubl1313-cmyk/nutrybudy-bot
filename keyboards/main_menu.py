"""
keyboards/main_menu.py
Основная клавиатура бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Главное меню бота
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="👤 Профиль"))
    builder.add(KeyboardButton(text="📊 Прогресс"))
    builder.add(KeyboardButton(text="🏆 Достижения"))
    builder.add(KeyboardButton(text="🤖 AI Ассистент"))
    builder.add(KeyboardButton(text="❓ Помощь"))

    builder.adjust(2, 2, 1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="✨ Выберите раздел..."
    )


def get_profile_menu() -> ReplyKeyboardMarkup:
    """
    Меню профиля
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="📋 Мои данные"))
    builder.add(KeyboardButton(text="✏️ Редактировать профиль"))
    builder.add(KeyboardButton(text="📊 Полный анализ тела"))
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(2, 2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="👤 Управление профилем..."
    )


def get_progress_menu() -> ReplyKeyboardMarkup:
    """
    Меню прогресса
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


def get_help_menu() -> ReplyKeyboardMarkup:
    """
    Меню помощи
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


def get_cancel_menu() -> ReplyKeyboardMarkup:
    """
    Клавиатура отмены
    """
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="❌ Отмена"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))

    builder.adjust(2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )
