"""
Улучшенные интерактивные клавиатуры с лучшей визуализацией
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_food_recognition_result_keyboard(
    has_matches: bool = True,
    can_use_ai_ingredients: bool = True
) -> InlineKeyboardMarkup:
    """
    Красивая клавиатура для результатов распознавания
    С иконками и эмодзи
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
        text="✏️ Ввести вручную",
        callback_data="manual_food_entry"
    )
    
    builder.button(
        text="🔄 Пересканировать",
        callback_data="retry_photo"
    )
    
    builder.button(
        text="❌ Отмена",
        callback_data="action_cancel"
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_macro_adjustment_keyboard(food_index: int, totals_msg_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для быстрого редактирования макронутриентов
    Со стрелками и предустановками
    """
    builder = InlineKeyboardBuilder()
    
    # Быстрые пресеты белков
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
