from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """
    ğŸŒ¿ Ğ ĞµĞ²Ğ¾Ğ»Ñ�Ñ†Ğ¸Ğ¾Ğ½Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ� NutriBuddy 2024
    Ğ’Ğ¸Ğ·ÑƒĞ°Ğ»ÑŒĞ½Ğ°Ñ� Ğ¸ĞµÑ€Ğ°Ñ€Ñ…Ğ¸Ñ� + Ñ�Ğ¼Ğ¾Ñ†Ğ¸Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ´Ğ¸Ğ·Ğ°Ğ¹Ğ½
    """
    kb = [
        # Ğ“Ğ»Ğ°Ğ²Ğ½Ğ°Ñ� Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ñ� - Ñ�Ğ°Ğ¼Ñ‹Ğ¹ Ğ±Ğ¾Ğ»ÑŒÑˆĞ¾Ğ¹ Ğ±Ğ»Ğ¾Ğº
        [KeyboardButton(text="ğŸ“¸ Ğ¡Ğ´ĞµĞ»Ğ°Ñ‚ÑŒ Ñ„Ğ¾Ñ‚Ğ¾ ĞµĞ´Ñ‹")],
        
        # Ğ’Ñ‚Ğ¾Ñ€Ğ¾Ñ�Ñ‚ĞµĞ¿ĞµĞ½Ğ½Ñ‹Ğµ Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ğ¸
        [KeyboardButton(text="ğŸ“Š ĞœĞ¾Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�")],
        [KeyboardButton(text="ğŸ‘¤ ĞœĞ¾Ğ¹ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ")],
        
        # Ğ’Ñ�Ğ¿Ğ¾Ğ¼Ğ¾Ğ³Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ°Ñ� Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ñ�
        [KeyboardButton(text="â�“ ĞŸĞ¾Ğ¼Ğ¾Ñ‰ÑŒ")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°")]],
        resize_keyboard=True
    )

def get_edit_profile_keyboard():
    kb = [
        [KeyboardButton(text="âœ�ï¸� Ğ˜Ğ·Ğ¼ĞµĞ½Ğ¸Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ")],
        [KeyboardButton(text="ğŸ“Š ĞœĞ¾Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�")],
        [KeyboardButton(text="ğŸ�  Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="â™‚ï¸� ĞœÑƒĞ¶Ñ�ĞºĞ¾Ğ¹")],
            [KeyboardButton(text="â™€ï¸� Ğ–ĞµĞ½Ñ�ĞºĞ¸Ğ¹")]
        ],
        resize_keyboard=True
    )

def get_activity_level_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ğŸª‘ Ğ¡Ğ¸Ğ´Ñ�Ñ‡Ğ¸Ğ¹")],
            [KeyboardButton(text="ğŸš¶ Ğ¡Ñ€ĞµĞ´Ğ½Ğ¸Ğ¹")],
            [KeyboardButton(text="ğŸ�ƒ Ğ’Ñ‹Ñ�Ğ¾ĞºĞ¸Ğ¹")]
        ],
        resize_keyboard=True
    )

def get_goal_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="â¬‡ï¸� ĞŸĞ¾Ñ…ÑƒĞ´ĞµĞ½Ğ¸Ğµ")],
            [KeyboardButton(text="â�¡ï¸� ĞŸĞ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ğµ")],
            [KeyboardButton(text="â¬†ï¸� Ğ�Ğ°Ğ±Ğ¾Ñ€ Ğ¼Ğ°Ñ�Ñ�Ñ‹")]
        ],
        resize_keyboard=True
    )
