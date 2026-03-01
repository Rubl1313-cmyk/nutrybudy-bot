from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    """Главное меню бота"""
    kb = [
        [
            KeyboardButton(text="🍽️ Дневник питания"),
            KeyboardButton(text="💧 Вода")
        ],
        [
            KeyboardButton(text="📊 Прогресс"),
            KeyboardButton(text="📋 Списки покупок")
        ],
        [
            KeyboardButton(text="🔔 Напоминания"),
            KeyboardButton(text="👤 Профиль")
        ],
        [
            KeyboardButton(text="📖 Рецепты"),
            KeyboardButton(text="🏋️ Активность")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_keyboard():
    """Кнопка отмены"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )


def get_edit_profile_keyboard():
    """Клавиатура для редактирования профиля"""
    kb = [
        [KeyboardButton(text="✏️ Изменить профиль")],
        [KeyboardButton(text="📊 Прогресс")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
