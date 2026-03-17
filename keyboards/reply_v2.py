"""
keyboards/reply_v2.py
Ğ�Ğ¾Ğ²Ğ°Ñ� Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ°Ñ� ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ñ� ÑƒĞ»ÑƒÑ‡ÑˆĞµĞ½Ğ½Ñ‹Ğ¼ Ğ´Ğ¸Ğ·Ğ°Ğ¹Ğ½Ğ¾Ğ¼
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard_v2() -> ReplyKeyboardMarkup:
    """
    Ğ�Ğ¾Ğ²Ğ°Ñ� Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ°Ñ� ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ñ� 2 Ñ�Ñ‚Ñ€Ğ¾ĞºĞ°Ğ¼Ğ¸ Ğ¿Ğ¾ 3 ĞºĞ½Ğ¾Ğ¿ĞºĞ¸
    """
    builder = ReplyKeyboardBuilder()
    
    # ĞŸĞµÑ€Ğ²Ğ°Ñ� Ñ�Ñ‚Ñ€Ğ¾ĞºĞ°
    builder.add(KeyboardButton(text="ğŸ�½ï¸� Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸"))
    builder.add(KeyboardButton(text="ğŸ’§ Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ"))
    builder.add(KeyboardButton(text="ğŸ¤– Ğ¡Ğ¿Ñ€Ğ¾Ñ�Ğ¸Ñ‚ÑŒ AI"))
    
    # Ğ’Ñ‚Ğ¾Ñ€Ğ°Ñ� Ñ�Ñ‚Ñ€Ğ¾ĞºĞ°
    builder.add(KeyboardButton(text="ğŸ“Š ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�"))
    builder.add(KeyboardButton(text="ğŸ‘¤ ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"))
    builder.add(KeyboardButton(text="â�“ ĞŸĞ¾Ğ¼Ğ¾Ñ‰ÑŒ"))
    
    # Ğ�Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹ĞºĞ°
    builder.adjust(3, 3)  # 3 ĞºĞ½Ğ¾Ğ¿ĞºĞ¸ Ğ² ĞºĞ°Ğ¶Ğ´Ğ¾Ğ¹ Ñ�Ñ‚Ñ€Ğ¾ĞºĞµ
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ¸Ğ»Ğ¸ Ğ²Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ğµ..."
    )

def get_profile_keyboard() -> ReplyKeyboardMarkup:
    """
    ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ğ¹ Ğ² Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ğµ
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="ğŸ“� Ğ ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"))
    builder.add(KeyboardButton(text="ğŸ§¬ ĞŸĞ¾Ğ»Ğ½Ñ‹Ğ¹ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·"))
    builder.add(KeyboardButton(text="âš–ï¸� Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²ĞµÑ�"))
    builder.add(KeyboardButton(text="ğŸ”™ Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�"))
    
    builder.adjust(2, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ğµ..."
    )

def get_quick_actions_keyboard() -> ReplyKeyboardMarkup:
    """
    ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ñ… Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ğ¹ (Ğ¿Ğ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµÑ‚Ñ�Ñ� Ğ´Ğ¾Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾)
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="âš–ï¸� Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²ĞµÑ�"))
    builder.add(KeyboardButton(text="ğŸ�ƒ Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ"))
    builder.add(KeyboardButton(text="ğŸŒ¦ï¸� ĞŸĞ¾Ğ³Ğ¾Ğ´Ğ°"))
    
    builder.adjust(3)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Ğ‘Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ğµ Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ñ�..."
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ğ¾Ñ‚Ğ¼ĞµĞ½Ñ‹ Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ğ¹
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°"))
    builder.add(KeyboardButton(text="ğŸ”™ Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�"))
    
    builder.adjust(2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_water_keyboard() -> ReplyKeyboardMarkup:
    """
    ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ğ±Ñ‹Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ¾ Ğ²Ğ²Ğ¾Ğ´Ğ° Ğ²Ğ¾Ğ´Ñ‹
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="ğŸ’§ 1 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½"))
    builder.add(KeyboardButton(text="ğŸ’§ 2 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½Ğ°"))
    builder.add(KeyboardButton(text="ğŸ’§ 500 Ğ¼Ğ»"))
    builder.add(KeyboardButton(text="ğŸ’§ 1 Ğ»Ğ¸Ñ‚Ñ€"))
    builder.add(KeyboardButton(text="ğŸ”™ Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_activity_keyboard() -> ReplyKeyboardMarkup:
    """
    ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ğ±Ñ‹Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ¾ Ğ²Ğ²Ğ¾Ğ´Ğ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="ğŸ�ƒ Ğ‘ĞµĞ³"))
    builder.add(KeyboardButton(text="ğŸš¶ Ğ¥Ğ¾Ğ´ÑŒĞ±Ğ°"))
    builder.add(KeyboardButton(text="ğŸ�‹ï¸� Ğ¢Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°"))
    builder.add(KeyboardButton(text="ğŸ§˜ Ğ™Ğ¾Ğ³Ğ°"))
    builder.add(KeyboardButton(text="ğŸ”™ Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_ai_keyboard() -> ReplyKeyboardMarkup:
    """
    ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ñ… AI-Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ¾Ğ²
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="ğŸŒ¦ï¸� ĞŸĞ¾Ğ³Ğ¾Ğ´Ğ°"))
    builder.add(KeyboardButton(text="ğŸ�³ Ğ ĞµÑ†ĞµĞ¿Ñ‚"))
    builder.add(KeyboardButton(text="ğŸ§® Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ğ°Ñ‚ÑŒ ĞšĞ‘Ğ–Ğ£"))
    builder.add(KeyboardButton(text="ğŸ’¬ Ğ�Ğ±Ñ‰Ğ¸Ğ¹ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�"))
    builder.add(KeyboardButton(text="ğŸ”™ Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�"))
    
    builder.adjust(3, 2)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )
