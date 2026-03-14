"""
🎨 Современные клавиатуры для NutriBuddy Bot
✨ Стиль как в современных фитнес-приложениях
🚀 Умные эмодзи и интуитивная навигация
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_modern_main_menu() -> InlineKeyboardMarkup:
    """
    🤖 Современное AI-меню NutriBuddy
    """
    builder = InlineKeyboardBuilder()
    
    # Основные AI-функции
    builder.row(
        InlineKeyboardButton(text="📸 Отправить фото", callback_data="photo_food"),
        InlineKeyboardButton(text="🎙️ Голосовое сообщение", callback_data="voice_food")
    )
    
    builder.row(
        InlineKeyboardButton(text="✍️ Написать текстом", callback_data="text_food"),
        InlineKeyboardButton(text="📊 Мой прогресс", callback_data="show_progress")
    )
    
    # AI-инструменты
    builder.row(
        InlineKeyboardButton(text="🤖 AI Ассистент", callback_data="ai_assistant"),
        InlineKeyboardButton(text="👤 Профиль", callback_data="show_profile")
    )
    
    # Дополнительно
    builder.row(
        InlineKeyboardButton(text="� Вода", callback_data="log_water"),
        InlineKeyboardButton(text="🏋️ Активность", callback_data="log_activity")
    )
    
    return builder.as_markup()

def get_modern_food_keyboard() -> InlineKeyboardMarkup:
    """
    🍽️ Современная клавиатура для работы с едой
    """
    builder = InlineKeyboardBuilder()
    
    # Основные действия
    builder.row(
        InlineKeyboardButton(text="📸 Распознать по фото", callback_data="photo_food"),
        InlineKeyboardButton(text="✍️ Ввести вручную", callback_data="manual_food")
    )
    
    # Быстрые опции
    builder.row(
        InlineKeyboardButton(text="🥐 Завтрак", callback_data="quick_breakfast"),
        InlineKeyboardButton(text="🥗 Обед", callback_data="quick_lunch")
    )
    
    builder.row(
        InlineKeyboardButton(text="🍲 Ужин", callback_data="quick_dinner"),
        InlineKeyboardButton(text="🍎 Перекус", callback_data="quick_snack")
    )
    
    # История и статистика
    builder.row(
        InlineKeyboardButton(text="📜 Сегодня", callback_data="today_summary"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="food_stats")
    )
    
    return builder.as_markup()

def get_modern_water_keyboard(current_ml: int, goal_ml: int = 2000) -> InlineKeyboardMarkup:
    """
    💧 Современная клавиатура для отслеживания воды
    """
    builder = InlineKeyboardBuilder()
    
    # Быстрые добавки
    builder.row(
        InlineKeyboardButton(text="💧 +100мл", callback_data="water_add_100"),
        InlineKeyboardButton(text="💧 +200мл", callback_data="water_add_200"),
        InlineKeyboardButton(text="💧 +250мл", callback_data="water_add_250")
    )
    
    builder.row(
        InlineKeyboardButton(text="🥤 +500мл", callback_data="water_add_500"),
        InlineKeyboardButton(text="🫙 +1000мл", callback_data="water_add_1000")
    )
    
    # Прогресс
    percentage = min((current_ml / goal_ml) * 100, 100)
    progress_emoji = "🎯" if percentage >= 100 else "👍" if percentage >= 75 else "💪" if percentage >= 50 else "💧"
    
    builder.row(
        InlineKeyboardButton(
            text=f"{progress_emoji} {current_ml}/{goal_ml}мл ({percentage:.0f}%)", 
            callback_data="water_progress"
        )
    )
    
    # Управление
    builder.row(
        InlineKeyboardButton(text="📊 График", callback_data="water_chart"),
        InlineKeyboardButton(text="⚙️ Цель", callback_data="water_goal")
    )
    
    return builder.as_markup()

def get_food_recognition_result_keyboard(
    has_matches: bool = True,
    can_use_ai_ingredients: bool = True
) -> InlineKeyboardMarkup:
    """
    🎨 Современная клавиатура для результатов распознавания еды
    """
    builder = InlineKeyboardBuilder()
    
    if has_matches:
        builder.button(
            text="🍽️ Выбрать из базы",
            callback_data="select_from_db"
        )
    
    if can_use_ai_ingredients:
        builder.button(
            text="🔍 Разобрать на ингредиенты",
            callback_data="use_ingredients_instead"
        )
    
    builder.button(
        text="✍️ Ввести вручную",
        callback_data="manual_food_entry"
    )
    
    builder.button(
        text="🔄 Перераспознать",
        callback_data="retry_photo"
    )
    
    builder.button(
        text="❌ Отмена",
        callback_data="action_cancel"
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_daily_goals_keyboard() -> InlineKeyboardMarkup:
    """
    🎯 Клавиатура для дневных целей
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Изменить цели", callback_data="edit_goals"),
        InlineKeyboardButton(text="📈 Статистика", callback_data="show_stats")
    )
    
    builder.row(
        InlineKeyboardButton(text="💧 Цель воды", callback_data="water_goal"),
        InlineKeyboardButton(text="🏋️ Цель калорий", callback_data="calorie_goal")
    )
    
    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
        InlineKeyboardButton(text="❌ Закрыть", callback_data="close")
    )
    
    return builder.as_markup()

def get_time_period_keyboard() -> InlineKeyboardMarkup:
    """
    ⏰ Клавиатура выбора периода
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Сегодня", callback_data="period_today"),
        InlineKeyboardButton(text="📆 Неделя", callback_data="period_week")
    )
    
    builder.row(
        InlineKeyboardButton(text="📊 Месяц", callback_data="period_month"),
        InlineKeyboardButton(text="📈 Всё время", callback_data="period_all")
    )
    
    builder.row(
        InlineKeyboardButton(text="❌ Закрыть", callback_data="close")
    )
    
    return builder.as_markup()

def get_macro_adjustment_keyboard(food_index: int, totals_msg_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для быстрого редактирования макронутриентов
    """
    builder = InlineKeyboardBuilder()
    
    # Быстрые пресеты веса
    builder.row(
        InlineKeyboardButton(text="➖10г", callback_data=f"weight_dec_{food_index}_10_{totals_msg_id}"),
        InlineKeyboardButton(text="➖50г", callback_data=f"weight_dec_{food_index}_50_{totals_msg_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="➕10г", callback_data=f"weight_inc_{food_index}_10_{totals_msg_id}"),
        InlineKeyboardButton(text="➕50г", callback_data=f"weight_inc_{food_index}_50_{totals_msg_id}")
    )
    
    # Быстрые пресеты
    builder.row(
        InlineKeyboardButton(text="100г", callback_data=f"weight_set_{food_index}_100_{totals_msg_id}"),
        InlineKeyboardButton(text="150г", callback_data=f"weight_set_{food_index}_150_{totals_msg_id}"),
        InlineKeyboardButton(text="200г", callback_data=f"weight_set_{food_index}_200_{totals_msg_id}")
    )
    
    # Управление
    builder.row(
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"weight_del_{food_index}_{totals_msg_id}"),
        InlineKeyboardButton(text="✅ Готово", callback_data="close_macro_edit")
    )
    
    return builder.as_markup()
