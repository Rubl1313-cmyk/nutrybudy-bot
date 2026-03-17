from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict

def get_meal_type_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="ğŸ¥� Ğ—Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº", callback_data="meal_breakfast")
    builder.button(text="ğŸ¥— Ğ�Ğ±ĞµĞ´", callback_data="meal_lunch")
    builder.button(text="ğŸ�² Ğ£Ğ¶Ğ¸Ğ½", callback_data="meal_dinner")
    builder.button(text="ğŸ�� ĞŸĞµÑ€ĞµĞºÑƒÑ�", callback_data="meal_snack")
    builder.adjust(2)
    return builder.as_markup()

def get_water_preset_keyboard():
    builder = InlineKeyboardBuilder()
    for amount in [200, 300, 500, 1000]:
        builder.button(text=f"{amount} Ğ¼Ğ» ğŸ’§", callback_data=f"water_{amount}")
    builder.adjust(2)
    return builder.as_markup()

def get_food_overview_keyboard(selected_foods: List[Dict]) -> InlineKeyboardMarkup:
    """ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ñ�Ğ²Ğ¾Ğ´ĞºĞ¸ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ²."""
    buttons = []
    for i, food in enumerate(selected_foods):
        status = "âœ…" if food['weight'] else "â¬œ"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {food['name']}",
                callback_data=f"edit_food_{i}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="â�• Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ¸Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚", callback_data="add_food")
    ])
    buttons.append([
        InlineKeyboardButton(text="âœ… ĞŸĞ¾Ğ´Ñ‚Ğ²ĞµÑ€Ğ´Ğ¸Ñ‚ÑŒ", callback_data="confirm_meal"),
        InlineKeyboardButton(text="â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°", callback_data="cancel_meal")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_food_edit_keyboard() -> InlineKeyboardMarkup:
    """ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ñ€ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ� Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ°."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="â†©ï¸� Ğ�Ğ°Ğ·Ğ°Ğ´", callback_data="back_to_overview")]
    ])

def get_food_selection_keyboard(foods: List[dict]):
    """ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ° â€“ Ğ‘Ğ•Ğ— Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€Ğ° show_skip"""
    builder = InlineKeyboardBuilder()
    for i, food in enumerate(foods[:5]):
        # ğŸ”¥ Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ‘Ğ–Ğ£ Ğº ĞºĞ½Ğ¾Ğ¿ĞºĞ°Ğ¼
        kb_text = (
            f"{food['name']} â€” {food.get('calories', 0):.0f} ĞºĞºĞ°Ğ» | "
            f"Ğ‘:{food.get('protein', 0):.1f} Ğ–:{food.get('fat', 0):.1f} Ğ£:{food.get('carbs', 0):.1f}"
        )
        builder.button(
            text=kb_text,
            callback_data=f"food_{i}"
        )
    builder.button(text="ğŸ”„ Ğ’Ğ²ĞµÑ�Ñ‚Ğ¸ Ğ²Ñ€ÑƒÑ‡Ğ½ÑƒÑ�", callback_data="food_manual")
    builder.adjust(1)
    return builder.as_markup()
def get_confirmation_keyboard(action: str = ""):
    """
    Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ğ°Ñ� ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ¿Ğ¾Ğ´Ñ‚Ğ²ĞµÑ€Ğ¶Ğ´ĞµĞ½Ğ¸Ñ�.
    action Ğ¼Ğ¾Ğ¶ĞµÑ‚ Ğ±Ñ‹Ñ‚ÑŒ Ğ¿ÑƒÑ�Ñ‚Ñ‹Ğ¼ (Ğ´Ğ»Ñ� Ğ¾Ğ±Ñ‰Ğ¸Ñ… Ñ�Ğ»ÑƒÑ‡Ğ°ĞµĞ²) Ğ¸Ğ»Ğ¸ Ñ�Ğ¿ĞµÑ†Ğ¸Ñ„Ğ¸Ñ‡Ğ½Ñ‹Ğ¼, Ğ½Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€ "reminder_delete".
    """
    builder = InlineKeyboardBuilder()
    if action:
        builder.button(text="âœ… Ğ”Ğ°", callback_data=f"confirm_{action}")
        builder.button(text="â�Œ Ğ�ĞµÑ‚", callback_data=f"cancel_{action}")
    else:
        builder.button(text="âœ… Ğ”Ğ°", callback_data="confirm")
        builder.button(text="â�Œ Ğ�ĞµÑ‚", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()

def get_progress_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="ğŸ“… Ğ¡ĞµĞ³Ğ¾Ğ´Ğ½Ñ�", callback_data="progress_day")
    builder.button(text="ğŸ“† Ğ�ĞµĞ´ĞµĞ»Ñ�", callback_data="progress_week")
    builder.button(text="ğŸ“† ĞœĞµÑ�Ñ�Ñ†", callback_data="progress_month")
    builder.adjust(3)
    return builder.as_markup()

def get_activity_type_keyboard():
    """
    ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ñ‚Ğ¸Ğ¿Ğ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸.
    Ğ£Ğ±Ñ€Ğ°Ğ½Ğ° Ñ…Ğ¾Ğ´ÑŒĞ±Ğ°, Ñ‚Ğ°Ğº ĞºĞ°Ğº Ğ´Ğ»Ñ� Ğ½ĞµÑ‘ ĞµÑ�Ñ‚ÑŒ Ğ¾Ñ‚Ğ´ĞµĞ»ÑŒĞ½Ñ‹Ğ¹ Ğ¿ÑƒĞ½ĞºÑ‚ "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ ÑˆĞ°Ğ³Ğ¸".
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="ğŸ�ƒ Ğ‘ĞµĞ³", callback_data="activity_running")
    builder.button(text="ğŸš´ Ğ’ĞµĞ»Ğ¾Ñ�Ğ¸Ğ¿ĞµĞ´", callback_data="activity_cycling")
    builder.button(text="ğŸ�‹ï¸� Ğ¢Ñ€ĞµĞ½Ğ°Ğ¶Ñ‘Ñ€Ğ½Ñ‹Ğ¹ Ğ·Ğ°Ğ»", callback_data="activity_gym")
    builder.button(text="ğŸ§˜ Ğ™Ğ¾Ğ³Ğ°", callback_data="activity_yoga")
    builder.button(text="ğŸ�Š ĞŸĞ»Ğ°Ğ²Ğ°Ğ½Ğ¸Ğµ", callback_data="activity_swimming")
    builder.button(text="ğŸ�¾ Ğ”Ñ€ÑƒĞ³Ğ¾Ğµ", callback_data="activity_other")
    builder.adjust(2)
    return builder.as_markup()

# ========== Ğ�Ğ�Ğ’Ğ«Ğ• Ğ�Ğ�Ğ’Ğ˜Ğ“Ğ�Ğ¦Ğ˜Ğ�Ğ�Ğ�Ğ«Ğ• ĞœĞ•Ğ�Ğ® ==========

def get_food_menu() -> InlineKeyboardMarkup:
    """ĞŸĞ¾Ğ´Ğ¼ĞµĞ½Ñ� Ñ€Ğ°Ğ·Ğ´ĞµĞ»Ğ° Â«ĞŸĞ¸Ñ‚Ğ°Ğ½Ğ¸ĞµÂ»."""
    buttons = [
        [InlineKeyboardButton(text="ğŸ“¸ Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ¸Ñ‚ÑŒ Ñ„Ğ¾Ñ‚Ğ¾ ĞµĞ´Ñ‹", callback_data="menu_food_photo")],
        [InlineKeyboardButton(text="âœ�ï¸� Ğ’Ğ²ĞµÑ�Ñ‚Ğ¸ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹ Ğ²Ñ€ÑƒÑ‡Ğ½ÑƒÑ�", callback_data="menu_food_manual")],
        [InlineKeyboardButton(text="ğŸ�½ï¸� ĞŸĞ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�", callback_data="menu_meal_plan")],
        [InlineKeyboardButton(text="ğŸ”™ Ğ�Ğ°Ğ·Ğ°Ğ´", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_water_activity_menu() -> InlineKeyboardMarkup:
    """ĞŸĞ¾Ğ´Ğ¼ĞµĞ½Ñ� Â«Ğ’Ğ¾Ğ´Ğ° Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒÂ»."""
    buttons = [
        [InlineKeyboardButton(text="ğŸ’§ Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ", callback_data="menu_water")],
        [InlineKeyboardButton(text="ğŸ�ƒ Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ", callback_data="menu_activity")],
        [InlineKeyboardButton(text="ğŸ‘Ÿ Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ ÑˆĞ°Ğ³Ğ¸", callback_data="menu_steps")],
        [InlineKeyboardButton(text="ğŸ”™ Ğ�Ğ°Ğ·Ğ°Ğ´", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_progress_menu() -> InlineKeyboardMarkup:
    """ĞŸÑ€Ğ¾Ñ�Ñ‚Ğ¾Ğµ Ğ¼ĞµĞ½Ñ� Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°."""
    buttons = [
        [InlineKeyboardButton(text="ğŸ“ˆ Ğ—Ğ° Ğ´ĞµĞ½ÑŒ", callback_data="progress_day")],
        [InlineKeyboardButton(text="ğŸ“Š Ğ—Ğ° Ğ½ĞµĞ´ĞµĞ»Ñ�", callback_data="progress_week")],
        [InlineKeyboardButton(text="ğŸ“‰ Ğ—Ğ° Ğ¼ĞµÑ�Ñ�Ñ†", callback_data="progress_month")],
        [InlineKeyboardButton(text="ğŸ”™ Ğ�Ğ°Ğ·Ğ°Ğ´", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_profile_menu() -> InlineKeyboardMarkup:
    """ĞŸÑ€Ğ¾Ñ�Ñ‚Ğ¾Ğµ Ğ¼ĞµĞ½Ñ� Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�."""
    buttons = [
        [InlineKeyboardButton(text="ğŸ‘¤ ĞŸÑ€Ğ¾Ñ�Ğ¼Ğ¾Ñ‚Ñ€ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�", callback_data="menu_profile_view")],
        [InlineKeyboardButton(text="âœ�ï¸� Ğ ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ", callback_data="menu_profile_edit")],
        [InlineKeyboardButton(text="âš–ï¸� Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²ĞµÑ�", callback_data="menu_log_weight")],
        [InlineKeyboardButton(text="ğŸ”™ Ğ�Ğ°Ğ·Ğ°Ğ´", callback_data="menu_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
