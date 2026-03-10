"""
🎨 Современные клавиатуры для NutriBuddy Bot
✨ Стиль как в современных фитнес-приложениях
🚀 Умные эмодзи и интуитивная навигация
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_modern_main_menu() -> InlineKeyboardMarkup:
    """
    🏠 Современное главное меню с категориями
    """
    builder = InlineKeyboardBuilder()
    
    # Основные функции
    builder.row(
        InlineKeyboardButton(text="📸 Распознать еду", callback_data="photo_recognition"),
        InlineKeyboardButton(text="📊 Прогресс", callback_data="show_progress")
    )
    
    builder.row(
        InlineKeyboardButton(text="� Вода", callback_data="log_water"),
        InlineKeyboardButton(text="🏋️ Активность", callback_data="log_activity")
    )
    
    # Дополнительные функции
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="show_profile"),
        InlineKeyboardButton(text="🤖 AI Помощник", callback_data="ai_assistant")
    )
    
    # Инструменты
    builder.row(
        InlineKeyboardButton(text="� Статистика", callback_data="show_statistics"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
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
    builder.button(text="🥩 -5g", callback_data=f"macro_protein_{food_index}_-5")
    builder.button(text="🥩 +5g", callback_data=f"macro_protein_{food_index}_+5")
    
    # Быстрые пресеты жиров
    builder.button(text="🥑 -5g", callback_data=f"macro_fat_{food_index}_-5")
    builder.button(text="🥑 +5g", callback_data=f"macro_fat_{food_index}_+5")
    
    # Быстрые пресеты углеводов
    builder.button(text="🍚 -10g", callback_data=f"macro_carbs_{food_index}_-10")
    builder.button(text="🍚 +10g", callback_data=f"macro_carbs_{food_index}_+10")
    
    builder.adjust(2)
    
    builder.row(InlineKeyboardButton(text="✅ Готово", callback_data="close_macro_edit"))
    
    return builder.as_markup()

def get_daily_goals_keyboard() -> InlineKeyboardMarkup:
    """
    Красивая клавиатура для просмотра целей
    С прогресс-барами в названиях кнопок
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔥 Калории",
        callback_data="view_goal_calories"
    )
    
    builder.button(
        text="🥩 Белки",
        callback_data="view_goal_protein"
    )
    
    builder.button(
        text="🥑 Жиры",
        callback_data="view_goal_fat"
    )
    
    builder.button(
        text="🍚 Углеводы",
        callback_data="view_goal_carbs"
    )
    
    builder.row(InlineKeyboardButton(text="⚙️ Настроить цели", callback_data="edit_goals"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="menu_back"))
    
    builder.adjust(2)
    return builder.as_markup()

def get_time_period_keyboard() -> InlineKeyboardMarkup:
    """
    Выбор временного периода для статистики
    С интуитивными иконками
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📅 Сегодня", callback_data="stats_today")
    builder.button(text="📆 Неделя", callback_data="stats_week")
    builder.button(text="📊 Месяц", callback_data="stats_month")
    builder.button(text="📈 Год", callback_data="stats_year")
    
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="menu_back"))
    
    return builder.as_markup()

def get_meal_quick_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Быстрые действия для приёма пищи
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📸 Фото", callback_data="meal_photo")
    builder.button(text="📝 Текст", callback_data="meal_text")
    builder.button(text="🎤 Голос", callback_data="meal_voice")
    
    builder.row(InlineKeyboardButton(text="📜 История", callback_data="meal_history"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="action_cancel"))
    
    builder.adjust(3)
    return builder.as_markup()

def get_streak_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Действия со сериями достижений
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔥 Моя серия", callback_data="view_streak")
    builder.button(text="📊 Статистика", callback_data="view_statistics")
    builder.button(text="🏆 Достижения", callback_data="view_achievements")
    
    builder.adjust(1)
    return builder.as_markup()
