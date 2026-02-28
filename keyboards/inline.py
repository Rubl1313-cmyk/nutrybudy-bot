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
        builder.button(text=f"{amount} мл", callback_data=f"water_{amount}")
    builder.adjust(2)
    return builder.as_markup()

def get_food_selection_keyboard(foods):
    builder = InlineKeyboardBuilder()
    for i, food in enumerate(foods[:5]):
        builder.button(
            text=f"{food['name']} – {food['calories']} ккал",
            callback_data=f"food_{i}"
        )
    builder.button(text="🔄 Другое название", callback_data="food_manual")
    builder.adjust(1)
    return builder.as_markup()

def get_activity_type_keyboard():
    builder = InlineKeyboardBuilder()
    activities = [
        ("🚶 Ходьба", "walking"),
        ("🏃 Бег", "running"),
        ("🚴 Велосипед", "cycling"),
        ("🏋️ Тренажёрный зал", "gym"),
        ("🧘 Йога", "yoga"),
        ("🏊 Плавание", "swimming"),
        ("💪 HIIT", "hiit"),
        ("🤸 Растяжка", "stretching"),
        ("💃 Танцы", "dancing"),
        ("⚽ Спорт", "sports")
    ]
    for text, value in activities:
        builder.button(text=text, callback_data=f"activity_{value}")
    builder.adjust(2)
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
    builder.button(text="🗑 Удалить список", callback_data=f"delete_list_{list_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_days_keyboard():
    builder = InlineKeyboardBuilder()
    days = [
        ("Пн", "mon"), ("Вт", "tue"), ("Ср", "wed"),
        ("Чт", "thu"), ("Пт", "fri"), ("Сб", "sat"), ("Вс", "sun")
    ]
    for text, value in days:
        builder.button(text=text, callback_data=f"day_{value}")
    builder.button(text="Ежедневно", callback_data="day_daily")
    builder.adjust(4)
    return builder.as_markup()