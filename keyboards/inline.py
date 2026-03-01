from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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


def get_food_selection_keyboard(foods):
    builder = InlineKeyboardBuilder()
    for i, food in enumerate(foods[:5]):
        builder.button(
            text=f"{food['name']} — {food['calories']} ккал",
            callback_data=f"food_{i}"
        )
    builder.button(text="🔄 Ввести вручную", callback_data="food_manual")
    builder.adjust(1)
    return builder.as_markup()


def get_confirmation_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="confirm")
    builder.button(text="❌ Нет", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


def get_shopping_lists_keyboard(lists):
    builder = InlineKeyboardBuilder()
    for lst in lists:
        unchecked = len([i for i in lst.items if not i.is_checked])
        builder.button(
            text=f"📋 {lst.name} ({unchecked})",
            callback_data=f"shopping_list_{lst.id}"
        )
    builder.button(text="➕ Новый список", callback_data="new_shopping_list")
    builder.adjust(1)
    return builder.as_markup()


def get_shopping_items_keyboard(items, list_id):
    builder = InlineKeyboardBuilder()
    for item in items[:10]:
        status = "✅" if item.is_checked else "⬜"
        builder.button(
            text=f"{status} {item.name}",
            callback_data=f"toggle_item_{item.id}"
        )
    builder.button(text="➕ Добавить товар", callback_data=f"add_item_{list_id}")
    builder.button(text="🗑️ Удалить список", callback_data=f"delete_list_{list_id}")
    builder.button(text="🔙 Назад", callback_data="back_to_lists")
    builder.adjust(1)
    return builder.as_markup()


def get_fitness_source_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⌚ Apple Watch", callback_data="fitness_apple")
    builder.button(text="📱 Google Fit", callback_data="fitness_google")
    builder.button(text="✍️ Ручной ввод", callback_data="fitness_manual")
    builder.button(text="📁 Загрузить GPX", callback_data="fitness_gpx")
    builder.adjust(2)
    return builder.as_markup()


def get_activity_type_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚶 Ходьба", callback_data="activity_walking")
    builder.button(text="🏃 Бег", callback_data="activity_running")
    builder.button(text="🚴 Велосипед", callback_data="activity_cycling")
    builder.button(text="🏋️ Тренажёрный зал", callback_data="activity_gym")
    builder.button(text="🧘 Йога", callback_data="activity_yoga")
    builder.button(text="🏊 Плавание", callback_data="activity_swimming")
    builder.button(text="🎾 Другое", callback_data="activity_other")
    builder.adjust(2)
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


def get_recipe_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🥗 Вегетарианское", callback_data="diet_vegetarian")
    builder.button(text="🥩 Белковое", callback_data="diet_protein")
    builder.button(text="🥑 Кето", callback_data="diet_keto")
    builder.button(text="🍚 Низкоуглеводное", callback_data="diet_lowcarb")
    builder.adjust(2)
    return builder.as_markup()


def get_profile_edit_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить вес", callback_data="edit_weight")
    builder.button(text="✏️ Изменить цель", callback_data="edit_goal")
    builder.button(text="🔄 Пересчитать нормы", callback_data="recalculate")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_progress_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 Вес", callback_data="progress_weight")
    builder.button(text="💧 Вода", callback_data="progress_water")
    builder.button(text="🔥 Калории", callback_data="progress_calories")
    builder.button(text="🏃 Активность", callback_data="progress_activity")
    builder.adjust(2)
    return builder.as_markup()


def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="back")
    return builder.as_markup()


def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    return builder.as_markup()
