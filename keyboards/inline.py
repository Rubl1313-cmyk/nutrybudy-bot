from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict

def get_meal_type_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🥐 Завтрак", callback_data="meal_breakfast")
    builder.button(text="🥗 Обед", callback_data="meal_lunch")
    builder.button(text="🍲 Ужин", callback_data="meal_dinner")
    builder.button(text="🍎 Перекус", callback_data="meal_snack")
    builder.adjust(2)
    return builder.as_markup()

def get_water_preset_keyboard():
    builder = InlineKeyboardBuilder()
    for amount in [200, 300, 500, 1000]:
        builder.button(text=f"{amount} мл 💧", callback_data=f"water_{amount}")
    builder.adjust(2)
    return builder.as_markup()

def get_food_overview_keyboard(selected_foods: List[Dict]) -> InlineKeyboardMarkup:
    """Клавиатура для сводки продуктов."""
    buttons = []
    for i, food in enumerate(selected_foods):
        status = "✅" if food['weight'] else "⬜"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {food['name']}",
                callback_data=f"edit_food_{i}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_food")
    ])
    buttons.append([
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_meal"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_meal")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_food_edit_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для редактирования продукта."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_overview")]
    ])

def get_food_selection_keyboard(foods: List[dict]):
    """Клавиатура выбора продукта – БЕЗ параметра show_skip"""
    builder = InlineKeyboardBuilder()
    for i, food in enumerate(foods[:5]):
        # 🔥 Добавляем БЖУ к кнопкам
        kb_text = (
            f"{food['name']} — {food.get('calories', 0):.0f} ккал | "
            f"Б:{food.get('protein', 0):.1f} Ж:{food.get('fat', 0):.1f} У:{food.get('carbs', 0):.1f}"
        )
        builder.button(
            text=kb_text,
            callback_data=f"food_{i}"
        )
    builder.button(text="🔄 Ввести вручную", callback_data="food_manual")
    builder.adjust(1)
    return builder.as_markup()
def get_confirmation_keyboard(action: str = ""):
    """
    Универсальная клавиатура подтверждения.
    action может быть пустым (для общих случаев) или специфичным, например "reminder_delete".
    """
    builder = InlineKeyboardBuilder()
    if action:
        builder.button(text="✅ Да", callback_data=f"confirm_{action}")
        builder.button(text="❌ Нет", callback_data=f"cancel_{action}")
    else:
        builder.button(text="✅ Да", callback_data="confirm")
        builder.button(text="❌ Нет", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()

def get_progress_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сегодня", callback_data="progress_day")
    builder.button(text="📆 Неделя", callback_data="progress_week")
    builder.button(text="📆 Месяц", callback_data="progress_month")
    builder.adjust(3)
    return builder.as_markup()

def get_activity_type_keyboard():
    """
    Клавиатура для выбора типа активности.
    Убрана ходьба, так как для неё есть отдельный пункт "Записать шаги".
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🏃 Бег", callback_data="activity_running")
    builder.button(text="🚴 Велосипед", callback_data="activity_cycling")
    builder.button(text="🏋️ Тренажёрный зал", callback_data="activity_gym")
    builder.button(text="🧘 Йога", callback_data="activity_yoga")
    builder.button(text="🏊 Плавание", callback_data="activity_swimming")
    builder.button(text="🎾 Другое", callback_data="activity_other")
    builder.adjust(2)
    return builder.as_markup()

# ========== НОВЫЕ НАВИГАЦИОННЫЕ МЕНЮ ==========

def get_food_menu() -> InlineKeyboardMarkup:
    """Подменю раздела «Питание»."""
    buttons = [
        [InlineKeyboardButton(text="📸 Отправить фото еды", callback_data="menu_food_photo")],
        [InlineKeyboardButton(text="✏️ Ввести продукты вручную", callback_data="menu_food_manual")],
        [InlineKeyboardButton(text="🍽️ План питания", callback_data="menu_meal_plan")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_water_activity_menu() -> InlineKeyboardMarkup:
    """Подменю «Вода и активность»."""
    buttons = [
        [InlineKeyboardButton(text="💧 Записать воду", callback_data="menu_water")],
        [InlineKeyboardButton(text="🏃 Записать активность", callback_data="menu_activity")],
        [InlineKeyboardButton(text="👟 Записать шаги", callback_data="menu_steps")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_progress_menu() -> InlineKeyboardMarkup:
    """Подменю «Прогресс»."""
    buttons = [
        [InlineKeyboardButton(text="📈 За день", callback_data="progress_day")],
        [InlineKeyboardButton(text="📊 За неделю", callback_data="progress_week")],
        [InlineKeyboardButton(text="📉 За месяц", callback_data="progress_month")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_profile_menu() -> InlineKeyboardMarkup:
    """Подменю «Профиль»."""
    buttons = [
        [InlineKeyboardButton(text="👤 Просмотр профиля", callback_data="menu_profile_view")],
        [InlineKeyboardButton(text="✏️ Редактировать профиль", callback_data="menu_profile_edit")],
        [InlineKeyboardButton(text="⚖️ Записать вес", callback_data="menu_log_weight")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
