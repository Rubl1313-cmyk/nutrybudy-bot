from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """
    🌿 Революционное меню NutriBuddy 2024
    Визуальная иерархия + эмоциональный дизайн
    """
    kb = [
        # Главная функция - самый большой блок
        [KeyboardButton(text="📸 Сделать фото еды")],
        
        # Второстепенные функции
        [KeyboardButton(text="📊 Мой прогресс")],
        [KeyboardButton(text="👤 Мой профиль")],
        
        # Вспомогательная функция
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
        [KeyboardButton(text="📊 Мой прогресс")],
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
