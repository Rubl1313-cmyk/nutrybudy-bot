from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """Главное меню с категориями."""
    kb = [
        [KeyboardButton(text="🍽️ Питание")],
        [KeyboardButton(text="💧 Вода и активность")],
        [KeyboardButton(text="📊 Прогресс и статистика")],
        [KeyboardButton(text="📋 Списки и напоминания")],
        [KeyboardButton(text="👤 Профиль и настройки")],
        [KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def get_edit_profile_keyboard():
    kb = [
        [KeyboardButton(text="✏️ Изменить профиль")],
        [KeyboardButton(text="📊 Прогресс")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="♂️ Мужской")],
            [KeyboardButton(text="♀️ Женский")]
        ],
        resize_keyboard=True
    )

def get_activity_level_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪑 Сидячий")],
            [KeyboardButton(text="🚶 Средний")],
            [KeyboardButton(text="🏃 Высокий")]
        ],
        resize_keyboard=True
    )

def get_goal_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬇️ Похудение")],
            [KeyboardButton(text="➡️ Поддержание")],
            [KeyboardButton(text="⬆️ Набор массы")]
        ],
        resize_keyboard=True
    )
