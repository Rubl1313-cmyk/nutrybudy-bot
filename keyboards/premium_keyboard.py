"""
keyboards/premium_keyboard.py
Премиальная клавиатура с современным дизайном
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# ═══════════════════════════════════════════════════════════════
# 🎨 ГЛАВНОЕ МЕНЮ - ПРЕМИУМ ДИЗАЙН
# ═══════════════════════════════════════════════════════════════

def get_premium_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Основная премиум клавиатура с эмодзи и структурой
    """
    builder = ReplyKeyboardBuilder()

    # 🔥 Основные действия (самые важные)
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


# ═══════════════════════════════════════════════════════════════
# 🍽️ МЕНЮ ПИТАНИЯ
# ═══════════════════════════════════════════════════════════════

def get_premium_food_keyboard() -> ReplyKeyboardMarkup:
    """Премиум клавиатура для записи еды"""
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
        input_field_placeholder="🍽️ Как запишем прием пищи?"
    )


def get_premium_water_keyboard() -> ReplyKeyboardMarkup:
    """Премиум клавиатура для воды"""
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
        input_field_placeholder="💧 Сколько выпили?"
    )


def get_premium_activity_keyboard() -> ReplyKeyboardMarkup:
    """Премиум клавиатура для активности"""
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
        input_field_placeholder="🏃‍♂️ Какая была активность?"
    )


# ═══════════════════════════════════════════════════════════════
# 📊 МЕНЮ ПРОГРЕССА
# ═══════════════════════════════════════════════════════════════

def get_premium_progress_keyboard() -> ReplyKeyboardMarkup:
    """Премиум клавиатура прогресса"""
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
        input_field_placeholder="📊 Выберите период..."
    )


# ═══════════════════════════════════════════════════════════════
# 👤 МЕНЮ ПРОФИЛЯ
# ═══════════════════════════════════════════════════════════════

def get_premium_profile_keyboard() -> ReplyKeyboardMarkup:
    """Премиум клавиатура профиля"""
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
        input_field_placeholder="👤 Управление профилем..."
    )


# ═══════════════════════════════════════════════════════════════
# ⚙️ МЕНЮ НАСТРОЕК
# ═══════════════════════════════════════════════════════════════

def get_premium_settings_keyboard() -> ReplyKeyboardMarkup:
    """Премиум клавиатура настроек"""
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="🔔 Уведомления"))
    builder.add(KeyboardButton(text="📊 Цели"))
    builder.add(KeyboardButton(text="🌍 Часовой пояс"))
    
    builder.add(KeyboardButton(text="📏 Единицы"))
    builder.add(KeyboardButton(text="🎨 Тема"))
    builder.add(KeyboardButton(text="📤 Экспорт"))
    
    builder.add(KeyboardButton(text="ℹ️ О боте"))
    builder.add(KeyboardButton(text="🔙 Назад"))

    builder.adjust(3, 3, 2)

    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="⚙️ Настройки..."
    )


# ═══════════════════════════════════════════════════════════════
# 🔙 НАВИГАЦИЯ
# ═══════════════════════════════════════════════════════════════

def get_premium_back_keyboard() -> ReplyKeyboardMarkup:
    """Простая клавиатура с кнопкой Назад"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔙 Назад"))
    builder.add(KeyboardButton(text="🏠 В главное меню"))
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Нажмите для навигации..."
    )


def get_premium_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура отмены"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отмена"))
    builder.add(KeyboardButton(text="🔙 Назад"))
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="..."
    )


def get_premium_confirm_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="✅ Подтвердить"))
    builder.add(KeyboardButton(text="❌ Отмена"))
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


# ═══════════════════════════════════════════════════════════════
# 🎯 INLINE КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════

def get_premium_inline_progress() -> InlineKeyboardMarkup:
    """Inline клавиатура для прогресса"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📅 Сегодня", callback_data="progress_today")
    builder.button(text="📆 Неделя", callback_data="progress_week")
    builder.button(text="🗓️ Месяц", callback_data="progress_month")
    builder.button(text="📊 Всё время", callback_data="progress_all")
    
    builder.adjust(2)
    return builder.as_markup()


def get_premium_inline_meal_type() -> InlineKeyboardMarkup:
    """Inline клавиатура типа приема пищи"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🌅 Завтрак", callback_data="meal_breakfast")
    builder.button(text="🌞 Обед", callback_data="meal_lunch")
    builder.button(text="🌆 Ужин", callback_data="meal_dinner")
    builder.button(text="🍪 Перекус", callback_data="meal_snack")
    
    builder.adjust(2)
    return builder.as_markup()


def get_premium_inline_water_quick() -> InlineKeyboardMarkup:
    """Inline быстрые кнопки воды"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="💧 200", callback_data="water_200")
    builder.button(text="💧 250", callback_data="water_250")
    builder.button(text="💧 350", callback_data="water_350")
    builder.button(text="💧 500", callback_data="water_500")
    builder.button(text="💧 750", callback_data="water_750")
    builder.button(text="💧 1000", callback_data="water_1000")
    
    builder.adjust(3)
    return builder.as_markup()


def get_premium_inline_navigation(
    back_callback: str = "back",
    home_callback: str = "home"
) -> InlineKeyboardMarkup:
    """Универсальная навигационная клавиатура"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔙 Назад", callback_data=back_callback)
    builder.button(text="🏠 Главное меню", callback_data=home_callback)
    
    builder.adjust(2)
    return builder.as_markup()


def get_premium_inline_close() -> InlineKeyboardMarkup:
    """Кнопка закрытия"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Закрыть", callback_data="close")
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════
# 🎨 УНИВЕРСАЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def create_premium_button(
    text: str,
    callback: str = None,
    emoji: str = ""
) -> InlineKeyboardButton:
    """Создать премиум кнопку"""
    return InlineKeyboardButton(
        text=f"{emoji} {text}" if emoji else text,
        callback_data=callback
    )


def create_premium_reply_button(
    text: str,
    emoji: str = ""
) -> KeyboardButton:
    """Создать премиум reply кнопку"""
    return KeyboardButton(
        text=f"{emoji} {text}" if emoji else text
    )
