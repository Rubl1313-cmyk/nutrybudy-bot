"""
handlers/reply_handlers.py
Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� Ğ½Ğ¾Ğ²Ñ‹Ñ… reply-ĞºĞ½Ğ¾Ğ¿Ğ¾Ğº
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.reply_v2 import get_main_keyboard_v2
from services.tool_caller import ToolCaller

logger = logging.getLogger(__name__)
router = Router()

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ñ… ĞºĞ½Ğ¾Ğ¿Ğ¾Ğº

@router.message(F.text.contains("Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸"))
async def food_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "ğŸ�½ï¸� <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸</b>\n\n"
        "Ğ�Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ, Ñ‡Ñ‚Ğ¾ Ğ²Ñ‹ Ñ�ÑŠĞµĞ»Ğ¸, Ğ¸Ğ»Ğ¸ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²ÑŒÑ‚Ğµ Ñ„Ğ¾Ñ‚Ğ¾ Ğ±Ğ»Ñ�Ğ´Ğ°.",
        parse_mode="HTML"
    )

@router.message(F.text.contains("Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ"))
async def water_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "💧 <b>Записать воду</b>\n\n"
        "Напишите, сколько вы выпили (например, «250 мл» или «2 стакана»).",
        parse_mode="HTML"
    )

@router.message(F.text.contains("Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ ÑˆĞ°Ğ³Ğ¸"))
async def steps_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👟 <b>Записать шаги</b>\n\n"
        "Напишите, сколько шагов вы сделали (например, «10000 шагов» или «8500»).",
        parse_mode="HTML"
    )

@router.message(F.text.contains("Ğ¡Ğ¿Ñ€Ğ¾Ñ�Ğ¸Ñ‚ÑŒ AI"))
async def ai_button_handler(message: Message, state: FSMContext):
    await state.clear()
    from handlers.ai_assistant import cmd_ask
    await cmd_ask(message, state)

@router.message(F.text.contains("ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�"))
async def progress_button_handler(message: Message, state: FSMContext):
    await state.clear()
    from handlers.progress import cmd_progress
    await cmd_progress(message, state)

@router.message(F.text.contains("ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"))
async def profile_button_handler(message: Message, state: FSMContext):
    await state.clear()
    from handlers.profile import cmd_profile
    await cmd_profile(message, state)

@router.message(F.text.contains("ĞŸĞ¾Ğ¼Ğ¾Ñ‰ÑŒ"))
async def help_button_handler(message: Message, state: FSMContext):
    await state.clear()
    from handlers.common import cmd_help
    await cmd_help(message, state)

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ñ… Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ğ¹

@router.message(F.text == "âš–ï¸� Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²ĞµÑ�")
async def weight_quick_handler(message: Message, state: FSMContext):
    """Ğ‘Ñ‹Ñ�Ñ‚Ñ€Ğ°Ñ� Ğ·Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ²ĞµÑ�Ğ°"""
    await state.clear()
    await message.answer(
        "âš–ï¸� <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ²ĞµÑ�Ğ°</b>\n\n"
        "ğŸ’¡ <b>Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ²Ğ°Ñˆ Ğ²ĞµÑ�:</b>\n\n"
        "ğŸ“� <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
        "â€¢ Â«70.5 ĞºĞ³Â»\n"
        "â€¢ Â«Ğ’ĞµÑ� 72Â»\n"
        "â€¢ Â«68.2Â»\n\n"
        "âš ï¸� <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°Ğ¹Ñ‚Ğµ Ğ²ĞµÑ� Ğ² Ğ¾Ğ´Ğ½Ğ¾ Ğ¸ Ñ‚Ğ¾ Ğ¶Ğµ Ğ²Ñ€ĞµĞ¼Ñ�!</b>",
        parse_mode="HTML"
    )

@router.message(F.text == "ğŸ�ƒ Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ")
async def activity_quick_handler(message: Message, state: FSMContext):
    """Ğ‘Ñ‹Ñ�Ñ‚Ñ€Ğ°Ñ� Ğ·Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    await state.clear()
    await message.answer(
        "ğŸ�ƒ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸</b>\n\n"
        "ğŸ’¡ <b>Ğ�Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ²Ğ°ÑˆÑƒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ:</b>\n\n"
        "ğŸ“� <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
        "â€¢ Â«ĞŸÑ€Ğ¾Ğ±ĞµĞ¶Ğ°Ğ» 5 ĞºĞ¼Â»\n"
        "â€¢ Â«Ğ¢Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ° 45 Ğ¼Ğ¸Ğ½ÑƒÑ‚Â»\n"
        "â€¢ Â«10000 ÑˆĞ°Ğ³Ğ¾Ğ²Â»\n"
        "â€¢ Â«Ğ™Ğ¾Ğ³Ğ° 30 Ğ¼Ğ¸Ğ½ÑƒÑ‚Â»\n\n"
        "âš¡ <b>Ğ˜Ğ»Ğ¸ Ğ²Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ñ‚Ğ¸Ğ¿ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:</b>",
        parse_mode="HTML"
    )
    
    # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ğµ Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ñ‹
    from keyboards.reply_v2 import get_activity_keyboard
    await message.answer(
        "âš¡ <b>Ğ‘Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ğµ Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ñ‹:</b>",
        reply_markup=get_activity_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "ğŸŒ¦ï¸� ĞŸĞ¾Ğ³Ğ¾Ğ´Ğ°")
async def weather_quick_handler(message: Message, state: FSMContext):
    """Ğ‘Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ğ¹ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñ‹"""
    await state.clear()
    from handlers.ai_assistant import cmd_weather
    await cmd_weather(message, state)

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ñ… Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ² Ğ²Ğ¾Ğ´Ñ‹

@router.message(F.text.startswith("ğŸ’§"))
async def water_quick_variants(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ñ… Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ² Ğ²Ğ¾Ğ´Ñ‹"""
    text = message.text
    
    # ĞŸĞ°Ñ€Ñ�Ğ¸Ğ¼ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ğ¸Ğ· ĞºĞ½Ğ¾Ğ¿ĞºĞ¸
    if "1 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½" in text:
        amount = 250
    elif "2 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½Ğ°" in text:
        amount = 500
    elif "500 Ğ¼Ğ»" in text:
        amount = 500
    elif "1 Ğ»Ğ¸Ñ‚Ñ€" in text:
        amount = 1000
    else:
        return  # Ğ�Ğµ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ°Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ´Ñ€ÑƒĞ³Ğ¸Ğµ ĞºĞ½Ğ¾Ğ¿ĞºĞ¸
    
    # Ğ’Ñ‹Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ²Ğ¾Ğ´Ñ‹
    await ToolCaller.handle_log_water(f"Ğ²Ñ‹Ğ¿Ğ¸Ğ» {amount} Ğ¼Ğ»", message.from_user.id, message, state)

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ñ… Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ² Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸

@router.message(F.text.startswith("ğŸ�ƒ"))
@router.message(F.text.startswith("ğŸš¶"))
@router.message(F.text.startswith("ğŸ�‹ï¸�"))
@router.message(F.text.startswith("ğŸ§˜"))
async def activity_quick_variants(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ñ… Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ² Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    text = message.text
    
    # Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµĞ¼ Ñ‚Ğ¸Ğ¿ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
    activity_map = {
        "ğŸ�ƒ Ğ‘ĞµĞ³": "Ğ±ĞµĞ³ 30 Ğ¼Ğ¸Ğ½ÑƒÑ‚",
        "ğŸš¶ Ğ¥Ğ¾Ğ´ÑŒĞ±Ğ°": "Ñ…Ğ¾Ğ´ÑŒĞ±Ğ° 45 Ğ¼Ğ¸Ğ½ÑƒÑ‚", 
        "ğŸ�‹ï¸� Ğ¢Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°": "Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ° 45 Ğ¼Ğ¸Ğ½ÑƒÑ‚",
        "ğŸ§˜ Ğ™Ğ¾Ğ³Ğ°": "Ğ¹Ğ¾Ğ³Ğ° 30 Ğ¼Ğ¸Ğ½ÑƒÑ‚"
    }
    
    for button_text, activity_text in activity_map.items():
        if button_text in text:
            # Ğ’Ñ‹Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
            await ToolCaller.handle_log_activity(activity_text, message.from_user.id, message, state)
            break

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� AI Ğ±Ñ‹Ñ�Ñ‚Ñ€Ñ‹Ñ… Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ¾Ğ²

@router.message(F.text == "ğŸŒ¦ï¸� ĞŸĞ¾Ğ³Ğ¾Ğ´Ğ°")
async def ai_weather_handler(message: Message, state: FSMContext):
    """Ğ—Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñ‹ Ñ‡ĞµÑ€ĞµĞ· AI"""
    from handlers.ai_assistant import cmd_weather
    await cmd_weather(message, state)

@router.message(F.text == "ğŸ�³ Ğ ĞµÑ†ĞµĞ¿Ñ‚")
async def ai_recipe_handler(message: Message, state: FSMContext):
    """Ğ—Ğ°Ğ¿Ñ€Ğ¾Ñ� Ñ€ĞµÑ†ĞµĞ¿Ñ‚Ğ° Ñ‡ĞµÑ€ĞµĞ· AI"""
    from handlers.ai_assistant import cmd_recipe
    await cmd_recipe(message, state)

@router.message(F.text == "ğŸ§® Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ğ°Ñ‚ÑŒ ĞšĞ‘Ğ–Ğ£")
async def ai_calculate_handler(message: Message, state: FSMContext):
    """Ğ Ğ°Ñ�Ñ‡ĞµÑ‚ ĞšĞ‘Ğ–Ğ£ Ñ‡ĞµÑ€ĞµĞ· AI"""
    from handlers.ai_assistant import cmd_calculate
    await cmd_calculate(message, state)

@router.message(F.text == "ğŸ’¬ Ğ�Ğ±Ñ‰Ğ¸Ğ¹ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�")
async def ai_general_handler(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ‰Ğ¸Ğ¹ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ� Ğº AI"""
    await message.answer(
        "ğŸ’¬ <b>Ğ—Ğ°Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ²Ğ°Ñˆ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�:</b>\n\n"
        "ğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
        "â€¢ Â«Ğ¡ĞºĞ¾Ğ»ÑŒĞºĞ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹ Ğ² Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾?Â»\n"
        "â€¢ Â«ĞŸĞ¾Ğ»ĞµĞ·Ğ½Ğ° Ğ»Ğ¸ Ğ³Ñ€ĞµÑ‡ĞºĞ° Ğ½Ğ° ÑƒĞ¶Ğ¸Ğ½?Â»\n"
        "â€¢ Â«ĞšĞ°ĞºĞ¸Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹ Ğ±Ğ¾Ğ³Ğ°Ñ‚Ñ‹ Ğ±ĞµĞ»ĞºĞ¾Ğ¼?Â»\n"
        "â€¢ Â«ĞŸĞ¾Ñ�Ğ¾Ğ²ĞµÑ‚ÑƒĞ¹ Ğ»ĞµĞ³ĞºĞ¸Ğ¹ ÑƒĞ¶Ğ¸Ğ½Â»\n\n"
        "â�Œ Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Â«Ğ²Ñ‹Ñ…Ğ¾Ğ´Â» Ğ´Ğ»Ñ� Ğ·Ğ°Ğ²ĞµÑ€ÑˆĞµĞ½Ğ¸Ñ� Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ°",
        parse_mode="HTML"
    )
    
    # Ğ’ĞºĞ»Ñ�Ñ‡Ğ°ĞµĞ¼ Ñ€ĞµĞ¶Ğ¸Ğ¼ Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ°
    from handlers.ai_assistant import cmd_ask
    await cmd_ask(message, state)

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ½Ğ°Ğ²Ğ¸Ğ³Ğ°Ñ†Ğ¸Ğ¸

@router.message(F.text == "ğŸ”™ Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�")
async def back_to_main_handler(message: Message, state: FSMContext):
    """Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‚ Ğ² Ğ³Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�"""
    await state.clear()
    from keyboards.reply_v2 import get_main_keyboard_v2
    await message.answer(
        "ğŸ�  <b>Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�</b>",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text == "ğŸ“� Ğ ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ")
async def edit_profile_handler(message: Message, state: FSMContext):
    """Ğ ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�"""
    from handlers.profile import cmd_set_profile
    await cmd_set_profile(message, state)

@router.message(F.text == "ğŸ§¬ ĞŸĞ¾Ğ»Ğ½Ñ‹Ğ¹ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·")
async def full_analysis_handler(message: Message, state: FSMContext):
    """ĞŸĞ¾Ğ»Ğ½Ñ‹Ğ¹ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ· Ñ‚ĞµĞ»Ğ°"""
    await state.clear()
    
    from database.db import get_session
    from database.models import User, WeightEntry
    from sqlalchemy import select
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "â�Œ Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ñ€ĞµĞ´Ñ‹Ğ´ÑƒÑ‰Ğ¸Ğµ Ğ²ĞµÑ�Ğ° Ğ´Ğ»Ñ� Ñ‚Ñ€ĞµĞ½Ğ´Ğ°
        weights_result = await session.execute(
            select(WeightEntry.weight).where(
                WeightEntry.user_id == user.id
            ).order_by(WeightEntry.datetime.desc()).limit(10)
        )
        previous_weights = [row[0] for row in weights_result.fetchall()]
        
        # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·
        from utils.body_templates import get_body_analysis_text
        analysis_text = get_body_analysis_text(user, previous_weights)
        
        await message.answer(
            analysis_text,
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

# Ğ�Ñ‚Ğ»Ğ°Ğ´Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº (Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğ¼)
@router.message(F.text)
async def debug_button_handler(message: Message):
    logger.info(f"Reply handler received: {repr(message.text)}")
    # Ğ�Ğµ Ğ¾Ñ‚Ğ²ĞµÑ‡Ğ°ĞµĞ¼ â€“ Ğ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¾ Ğ»Ğ¾Ğ³Ğ¸Ñ€ÑƒĞµĞ¼
