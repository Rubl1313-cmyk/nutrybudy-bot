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

def get_shopping_lists_keyboard(lists):
    builder = InlineKeyboardBuilder()
    for lst in lists:
        builder.button(
            text=f"📋 {lst.name}",
            callback_data=f"shopping_list_{lst.id}"
        )
    builder.button(text="➕ Новый список", callback_data="new_shopping_list")
    builder.adjust(1)
    return builder.as_markup()

def get_shopping_items_keyboard(items, list_id):
    """
    Клавиатура для отображения товаров в списке покупок с кнопками управления.
    """
    builder = InlineKeyboardBuilder()
    for item in items[:10]:
        status = "✅" if item.is_checked else "⬜"
        # Кнопка с названием товара (для информации)
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {item.name} — {item.quantity} {item.unit}",
                callback_data=f"item_info_{item.id}"
            )
        )
        # Ряд с кнопками управления
        builder.row(
            InlineKeyboardButton(text="➖", callback_data=f"item_decr_{item.id}"),
            InlineKeyboardButton(text="➕", callback_data=f"item_incr_{item.id}"),
            InlineKeyboardButton(
                text="✅" if not item.is_checked else "↩️",
                callback_data=f"toggle_item_{item.id}"
            ),
            InlineKeyboardButton(text="🗑️", callback_data=f"delete_item_{item.id}"),
            width=4
        )
    builder.row(
        InlineKeyboardButton(text="➕ Добавить товар", callback_data=f"add_item_{list_id}"),
        InlineKeyboardButton(text="🗑️ Удалить список", callback_data=f"delete_list_{list_id}"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_lists"),
        width=2
    )
    return builder.as_markup()

def get_days_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Пн", callback_data="day_mon")
    builder.button(text="Вт", callback_data="day_tue")
    builder.button(text="Ср", callback_data="day_wed")
    builder.button(text="Чт", callback_data="day_thu")
    builder.button(text="Пт", callback_data="day_fri")
    builder.button(text="Сб", callback_data="day_sat")
    builder.button(text="Вс", callback_data="day_sun")
    builder.button(text="Ежедневно", callback_data="day_daily")
    builder.adjust(4)
    return builder.as_markup()

def get_reminder_type_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🍽️ Приём пищи", callback_data="reminder_meal")
    builder.button(text="💧 Вода", callback_data="reminder_water")
    builder.button(text="⚖️ Взвешивание", callback_data="reminder_weight")
    builder.button(text="📝 Своё", callback_data="reminder_custom")
    builder.adjust(2)
    return builder.as_markup()

def get_reminders_list_keyboard(reminders):
    """
    Создаёт inline-клавиатуру для списка напоминаний.
    Каждое напоминание отображается в виде строки с названием, временем и кнопкой удаления.
    """
    builder = InlineKeyboardBuilder()
    for rem in reminders:
        # Кнопка с информацией о напоминании (название и время)
        info_text = f"{rem.title} — {rem.time}"
        builder.row(
            InlineKeyboardButton(text=info_text, callback_data=f"reminder_info_{rem.id}"),
            InlineKeyboardButton(text="❌", callback_data=f"delete_reminder_{rem.id}"),
            width=2
        )
    # Кнопка для создания нового напоминания
    builder.row(InlineKeyboardButton(text="➕ Создать напоминание", callback_data="new_reminder"))
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

def get_lists_menu() -> InlineKeyboardMarkup:
    """Подменю «Списки и напоминания»."""
    buttons = [
        [InlineKeyboardButton(text="📋 Список покупок", callback_data="menu_shopping")],
        [InlineKeyboardButton(text="🔔 Напоминания", callback_data="menu_reminders")],
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
