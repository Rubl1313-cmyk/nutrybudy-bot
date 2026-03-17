"""
handlers/profile.py
Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
"""
import logging
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router, types
from sqlalchemy import select

from database.db import get_session
from database.models import User
from keyboards.reply_v2 import get_main_keyboard_v2, get_profile_keyboard
from keyboards.reply import get_gender_keyboard
from utils.states import ProfileStates
from utils.localized_commands import create_localized_command_filter

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("set_profile") | create_localized_command_filter("Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¸Ñ‚ÑŒ_Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"))
async def cmd_set_profile(message: Message, state: FSMContext):
    """Ğ�Ğ°Ñ‡Ğ°Ğ»Ğ¾ Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹ĞºĞ¸ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�"""
    await state.clear()
    
    await message.answer(
        "ğŸ‘¤ <b>Ğ�Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹ĞºĞ° Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�</b>\n\n"
        "Ğ”Ğ°Ğ²Ğ°Ğ¹Ñ‚Ğµ Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¸Ğ¼ Ğ²Ğ°Ñˆ Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ´Ğ»Ñ� Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğ³Ğ¾ Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° ĞšĞ‘Ğ–Ğ£.\n\n"
        "Ğ�Ğ°Ñ‡Ğ½ĞµĞ¼ Ñ� Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ¾Ğ³Ğ¾:\n\n"
        "ğŸ“� <b>Ğ’Ğ°Ñˆ Ğ²ĞµÑ� (Ğ² ĞºĞ³):</b>\n"
        "Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 70.5",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.weight)

@router.message(ProfileStates.weight)
async def process_weight(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ²ĞµÑ�Ğ° Ñ� Ğ±ĞµĞ·Ğ¾Ğ¿Ğ°Ñ�Ğ½Ñ‹Ğ¼ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ¾Ğ¼"""
    from utils.safe_parser import safe_parse_float
    
    weight, error = safe_parse_float(message.text, "Ğ²ĞµÑ�")
    
    if error:
        await message.answer(
            f"â�Œ {error}\n\n"
            "ğŸ“� <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
            "â€¢ 75.5\n"
            "â€¢ 80 ĞºĞ³\n"
            "â€¢ 72,3",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°")]],
                resize_keyboard=True,
                one_time_keyboard=True
            ),
            parse_mode="HTML"
        )
        return
    
    await state.update_data(weight=weight)
    await message.answer(
        "ğŸ“� <b>Ğ’Ğ°Ñˆ Ñ€Ğ¾Ñ�Ñ‚ (Ğ² Ñ�Ğ¼):</b>\n"
        "Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 175",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.height)

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ñ€Ğ¾Ñ�Ñ‚Ğ° Ñ� Ğ±ĞµĞ·Ğ¾Ğ¿Ğ°Ñ�Ğ½Ñ‹Ğ¼ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ¾Ğ¼"""
    from utils.safe_parser import safe_parse_int
    
    height, error = safe_parse_int(message.text, "Ñ€Ğ¾Ñ�Ñ‚")
    
    if error:
        await message.answer(
            f"â�Œ {error}\n\n"
            "ğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
            "â€¢ 175\n"
            "â€¢ 180 Ñ�Ğ¼\n"
            "â€¢ 165",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(height=height)
    await message.answer(
        "ğŸ�‚ <b>Ğ’Ğ°Ñˆ Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚:</b>\n"
        "Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 25",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.age)

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚Ğ° Ñ� Ğ±ĞµĞ·Ğ¾Ğ¿Ğ°Ñ�Ğ½Ñ‹Ğ¼ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ¾Ğ¼"""
    from utils.safe_parser import safe_parse_int
    
    age, error = safe_parse_int(message.text, "Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚")
    
    if error:
        await message.answer(
            f"â�Œ {error}\n\n"
            "ğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
            "â€¢ 25\n"
            "â€¢ 30 Ğ»ĞµÑ‚\n"
            "â€¢ 22",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(age=age)
    await message.answer(
        "âš§ï¸� <b>Ğ’Ğ°Ñˆ Ğ¿Ğ¾Ğ»:</b>\n\n"
        "Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ¸Ğ· ĞºĞ½Ğ¾Ğ¿Ğ¾Ğº Ğ½Ğ¸Ğ¶Ğµ:",
        parse_mode="HTML",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(ProfileStates.gender)

@router.message(ProfileStates.gender)
async def process_gender(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¿Ğ¾Ğ»Ğ°"""
    gender_text = message.text.lower()
    
    if "Ğ¼ÑƒĞ¶Ñ�ĞºĞ¾Ğ¹" in gender_text:
        gender = "male"
    elif "Ğ¶ĞµĞ½Ñ�ĞºĞ¸Ğ¹" in gender_text:
        gender = "female"
    else:
        await message.answer("â�Œ Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ 'ĞœÑƒĞ¶Ñ�ĞºĞ¾Ğ¹' Ğ¸Ğ»Ğ¸ 'Ğ–ĞµĞ½Ñ�ĞºĞ¸Ğ¹'")
        return
    
    await state.update_data(gender=gender)
    
    # Ğ”Ğ°Ğ»ĞµĞµ ĞºĞ¾Ğ´ Ğ±ĞµĞ· Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğ¹...
    if gender == "female":
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="ğŸ“� Ğ’Ğ²ĞµÑ�Ñ‚Ğ¸ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ ÑˆĞµĞ¸", callback_data="add_neck")
        builder.button(text="â�­ï¸� ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ ÑˆĞµÑ�", callback_data="skip_neck")
        builder.adjust(1)
        
        await message.answer(
            "ğŸ“� <b>Ğ�Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ</b>\n\n"
            "Ğ”Ğ»Ñ� Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğ³Ğ¾ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ğ¶Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ğ¹ Ğ¼Ğ°Ñ�Ñ�Ñ‹ Ğ½ÑƒĞ¶Ğ½Ñ‹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ñ‹.\n\n"
            "ğŸ“� <b>Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ ÑˆĞµĞ¸ (Ğ² Ñ�Ğ¼):</b>\n"
            "Ğ˜Ğ»Ğ¸ Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚Ğµ, Ğ½Ğ°Ğ¶Ğ°Ğ² ĞºĞ½Ğ¾Ğ¿ĞºÑƒ Ğ½Ğ¸Ğ¶Ğµ:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_neck)
    elif gender == "male":
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="ğŸ“� Ğ’Ğ²ĞµÑ�Ñ‚Ğ¸ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ�", callback_data="add_wrist")
        builder.button(text="â�­ï¸� ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒĞµ", callback_data="skip_wrist")
        builder.adjust(1)
        
        await message.answer(
            "ğŸ“� <b>Ğ�Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ</b>\n\n"
            "Ğ”Ğ»Ñ� Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğ³Ğ¾ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ğ¼Ñ‹ÑˆĞµÑ‡Ğ½Ğ¾Ğ¹ Ğ¼Ğ°Ñ�Ñ�Ñ‹ Ğ¸ Ğ¶Ğ¸Ñ€Ğ° Ğ½ÑƒĞ¶Ğ½Ñ‹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ñ‹.\n\n"
            "ğŸ“� <b>Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ� (Ğ² Ñ�Ğ¼):</b>\n"
            "Ğ˜Ğ»Ğ¸ Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚Ğµ, Ğ½Ğ°Ğ¶Ğ°Ğ² ĞºĞ½Ğ¾Ğ¿ĞºÑƒ Ğ½Ğ¸Ğ¶Ğµ:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_wrist)
    else:
        # ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�ĞºĞ°ĞµĞ¼ Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ�
        await show_activity_keyboard(message, state)

@router.message(ProfileStates.waiting_for_neck)
async def process_neck(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° ÑˆĞµĞ¸"""
    from utils.safe_parser import safe_parse_float
    
    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼, Ğ½Ğµ Ñ…Ğ¾Ñ‡ĞµÑ‚ Ğ»Ğ¸ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ
    if message.text.lower() in ["Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", "Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚", "skip", "Ğ´Ğ°Ğ»ĞµĞµ"]:
        await message.answer(
            "ğŸ“� <b>Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ñ‚Ğ°Ğ»Ğ¸Ğ¸ (Ğ² Ñ�Ğ¼):</b>\n"
            "Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 70",
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_waist)
        return
    
    neck, error = safe_parse_float(message.text, "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ ÑˆĞµĞ¸")
    
    if error:
        await message.answer(
            f"â�Œ {error}\n\n"
            "ğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
            "â€¢ 34\n"
            "â€¢ 35.5 Ñ�Ğ¼",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(neck_cm=neck)
    await message.answer(
        "ğŸ“� <b>Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ñ‚Ğ°Ğ»Ğ¸Ğ¸ (Ğ² Ñ�Ğ¼):</b>\n"
        "Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 70",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_waist)

@router.message(ProfileStates.waiting_for_waist)
async def process_waist(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ñ‚Ğ°Ğ»Ğ¸Ğ¸"""
    from utils.safe_parser import safe_parse_float
    
    waist, error = safe_parse_float(message.text, "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ñ‚Ğ°Ğ»Ğ¸Ğ¸")
    
    if error:
        await message.answer(
            f"â�Œ {error}\n\n"
            "ğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
            "â€¢ 70\n"
            "â€¢ 68.5 Ñ�Ğ¼",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(waist_cm=waist)
    await message.answer(
        "ğŸ“� <b>Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€ (Ğ² Ñ�Ğ¼):</b>\n"
        "Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 95",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_hip)

@router.message(ProfileStates.waiting_for_hip)
async def process_hip(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ±ĞµĞ´ĞµÑ€"""
    from utils.safe_parser import safe_parse_float
    
    hip, error = safe_parse_float(message.text, "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€")
    
    if error:
        await message.answer(
            f"â�Œ {error}\n\n"
            "ğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
            "â€¢ 95\n"
            "â€¢ 97.5 Ñ�Ğ¼",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(hip_cm=hip)
    
    # ĞŸĞµÑ€ĞµÑ…Ğ¾Ğ´Ğ¸Ğ¼ Ğº Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
    await show_activity_keyboard(message, state)

@router.message(ProfileStates.waiting_for_wrist)
async def process_wrist(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ� Ğ´Ğ»Ñ� Ğ¼ÑƒĞ¶Ñ‡Ğ¸Ğ½"""
    from utils.safe_parser import safe_parse_float
    
    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼, Ğ½Ğµ Ñ…Ğ¾Ñ‡ĞµÑ‚ Ğ»Ğ¸ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ
    if message.text.lower() in ["Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", "Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚", "skip", "Ğ´Ğ°Ğ»ĞµĞµ"]:
        await message.answer(
            "ğŸ’ª <b>Ğ”Ğ¾Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ·Ğ°Ğ¼ĞµÑ€Ñ‹ (Ğ½ĞµĞ¾Ğ±Ñ�Ğ·Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ¾)</b>\n\n"
            "Ğ”Ğ»Ñ� Ğ±Ğ¾Ğ»ĞµĞµ Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğ³Ğ¾ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ğ¼Ğ¾Ğ¶Ğ½Ğ¾ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ¸Ñ‚ÑŒ:\n\n"
            "ğŸ“� <b>Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ° (Ğ² Ñ�Ğ¼):</b>\n"
            "Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 32\n\n"
            "Ğ˜Ğ»Ğ¸ Ğ½Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Â«ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒÂ»",
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_bicep)
        return
    
    wrist, error = safe_parse_float(message.text, "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ�")
    
    if error:
        await message.answer(
            f"â�Œ {error}\n\n"
            "ğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
            "â€¢ 17\n"
            "â€¢ 18.5 Ñ�Ğ¼",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(wrist_cm=wrist)
# Ğ”Ğ»Ñ� Ğ¼ÑƒĞ¶Ñ‡Ğ¸Ğ½ Ğ¼Ğ¾Ğ¶Ğ½Ğ¾ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ¸Ñ‚ÑŒ ĞµÑ‰Ğµ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ñ‹ Ğ¿Ğ¾ Ğ¶ĞµĞ»Ğ°Ğ½Ğ¸Ñ�
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    builder.button(text="ğŸ“� Ğ’Ğ²ĞµÑ�Ñ‚Ğ¸ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ°", callback_data="add_bicep")
    builder.button(text="â�­ï¸� ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", callback_data="skip_measurements")
    builder.adjust(1)
    
    await message.answer(
        "ğŸ’ª <b>Ğ”Ğ¾Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ·Ğ°Ğ¼ĞµÑ€Ñ‹ (Ğ½ĞµĞ¾Ğ±Ñ�Ğ·Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ¾)</b>\n\n"
        "Ğ”Ğ»Ñ� Ğ±Ğ¾Ğ»ĞµĞµ Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğ³Ğ¾ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ğ¼Ğ¾Ğ¶Ğ½Ğ¾ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ¸Ñ‚ÑŒ:\n\n"
        "ğŸ“� <b>Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ° (Ğ² Ñ�Ğ¼):</b>\n"
        "Ğ˜Ğ»Ğ¸ Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚Ğµ, Ğ½Ğ°Ğ¶Ğ°Ğ² ĞºĞ½Ğ¾Ğ¿ĞºÑƒ Ğ½Ğ¸Ğ¶Ğµ:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_bicep)

@router.message(ProfileStates.waiting_for_bicep)
async def process_bicep(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ° Ğ´Ğ»Ñ� Ğ¼ÑƒĞ¶Ñ‡Ğ¸Ğ½"""
    from utils.safe_parser import safe_parse_float
    
    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼, Ğ½Ğµ Ñ…Ğ¾Ñ‡ĞµÑ‚ Ğ»Ğ¸ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ
    if message.text.lower() in ["Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", "Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚", "skip", "Ğ´Ğ°Ğ»ĞµĞµ"]:
        await show_activity_keyboard(message, state)
        return
    
    bicep, error = safe_parse_float(message.text, "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ°")
    
    if error:
        await message.answer(
            f"â�Œ {error}\n\n"
            "ğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>\n"
            "â€¢ 32\n"
            "â€¢ 33.5 Ñ�Ğ¼",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(bicep_cm=bicep)
    await show_activity_keyboard(message, state)


async def show_activity_keyboard(message: Message, state: FSMContext):
    """ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ñƒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ĞœĞ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ°Ñ�")],
            [KeyboardButton(text="Ğ›ĞµĞ³ĞºĞ°Ñ�")],
            [KeyboardButton(text="Ğ£Ğ¼ĞµÑ€ĞµĞ½Ğ½Ğ°Ñ�")],
            [KeyboardButton(text="Ğ’Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�")],
            [KeyboardButton(text="Ğ�Ñ‡ĞµĞ½ÑŒ Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "ğŸ�ƒ <b>Ğ£Ñ€Ğ¾Ğ²ĞµĞ½ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:</b>\n\n"
        "â€¢ ĞœĞ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ°Ñ� - Ñ�Ğ¸Ğ´Ñ�Ñ‡Ğ°Ñ� Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°, Ğ½ĞµÑ‚ Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ğº\n"
        "â€¢ Ğ›ĞµĞ³ĞºĞ°Ñ� - Ğ»ĞµĞ³ĞºĞ¸Ğµ Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ¸ 1-3 Ñ€Ğ°Ğ·Ğ° Ğ² Ğ½ĞµĞ´ĞµĞ»Ñ�\n"
        "â€¢ Ğ£Ğ¼ĞµÑ€ĞµĞ½Ğ½Ğ°Ñ� - Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ¸ 3-5 Ñ€Ğ°Ğ·Ğ° Ğ² Ğ½ĞµĞ´ĞµĞ»Ñ�\n"
        "â€¢ Ğ’Ñ‹Ñ�Ğ¾ĞºĞ°Ñ� - Ğ¸Ğ½Ñ‚ĞµĞ½Ñ�Ğ¸Ğ²Ğ½Ñ‹Ğµ Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ¸ 5-6 Ñ€Ğ°Ğ· Ğ² Ğ½ĞµĞ´ĞµĞ»Ñ�\n"
        "â€¢ Ğ�Ñ‡ĞµĞ½ÑŒ Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ� - ĞµĞ¶ĞµĞ´Ğ½ĞµĞ²Ğ½Ñ‹Ğµ Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ¸",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.activity)

@router.message(ProfileStates.activity)
async def process_activity(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° ÑƒÑ€Ğ¾Ğ²Ğ½Ñ� Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    activity = message.text.lower()
    
    activity_map = {
        "Ğ¼Ğ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ°Ñ�": 1.2,
        "Ğ»ĞµĞ³ĞºĞ°Ñ�": 1.375,
        "ÑƒĞ¼ĞµÑ€ĞµĞ½Ğ½Ğ°Ñ�": 1.55,
        "Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�": 1.725,
        "Ğ¾Ñ‡ĞµĞ½ÑŒ Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�": 1.9
    }
    
    if activity not in activity_map:
        await message.answer("â�Œ Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ¾Ğ´Ğ¸Ğ½ Ğ¸Ğ· Ğ¿Ñ€ĞµĞ´Ğ»Ğ¾Ğ¶ĞµĞ½Ğ½Ñ‹Ñ… Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ²")
        return
    
    activity_level = activity_map[activity]
    await state.update_data(activity_level=activity)  # Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ�Ñ‚Ñ€Ğ¾ĞºÑƒ, Ğ° Ğ½Ğµ Ñ‡Ğ¸Ñ�Ğ»Ğ¾
    
    # ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ»Ñ� Ñ†ĞµĞ»Ğ¸
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ĞŸĞ¾Ñ…ÑƒĞ´ĞµĞ½Ğ¸Ğµ")],
            [KeyboardButton(text="ĞŸĞ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ğµ")],
            [KeyboardButton(text="Ğ�Ğ°Ğ±Ğ¾Ñ€ Ğ¼Ğ°Ñ�Ñ�Ñ‹")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "ğŸ�¯ <b>Ğ’Ğ°ÑˆĞ° Ñ†ĞµĞ»ÑŒ:</b>\n\n"
        "â€¢ ĞŸĞ¾Ñ…ÑƒĞ´ĞµĞ½Ğ¸Ğµ - Ğ´ĞµÑ„Ğ¸Ñ†Ğ¸Ñ‚ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹\n"
        "â€¢ ĞŸĞ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ğµ - Ğ±Ğ°Ğ»Ğ°Ğ½Ñ� ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹\n"
        "â€¢ Ğ�Ğ°Ğ±Ğ¾Ñ€ Ğ¼Ğ°Ñ�Ñ�Ñ‹ - Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ñ†Ğ¸Ñ‚ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.goal)

@router.message(ProfileStates.goal)
async def process_goal(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ñ†ĞµĞ»Ğ¸"""
    goal = message.text.lower()
    
    goal_map = {
        "Ğ¿Ğ¾Ñ…ÑƒĞ´ĞµĞ½Ğ¸Ğµ": "lose_weight",
        "Ğ¿Ğ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ğµ": "maintain",
        "Ğ½Ğ°Ğ±Ğ¾Ñ€ Ğ¼Ğ°Ñ�Ñ�Ñ‹": "gain_weight"
    }
    
    if goal not in goal_map:
        await message.answer("â�Œ Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ¾Ğ´Ğ¸Ğ½ Ğ¸Ğ· Ğ¿Ñ€ĞµĞ´Ğ»Ğ¾Ğ¶ĞµĞ½Ğ½Ñ‹Ñ… Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ²")
        return
    
    goal_type = goal_map[goal]
    await state.update_data(goal=goal_type)
    
    await message.answer(
        "ğŸ�™ï¸� <b>Ğ’Ğ°Ñˆ Ğ³Ğ¾Ñ€Ğ¾Ğ´:</b>\n"
        "Ğ�ÑƒĞ¶ĞµĞ½ Ğ´Ğ»Ñ� Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½Ğ¸Ñ� Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñ‹ Ğ¸ ÑƒÑ‡ĞµÑ‚Ğ° ĞºĞ»Ğ¸Ğ¼Ğ°Ñ‚Ğ° Ğ² Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ°Ñ….\n\n"
        "Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: ĞœĞ¾Ñ�ĞºĞ²Ğ°",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.city)

@router.message(ProfileStates.city)
async def process_city(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ³Ğ¾Ñ€Ğ¾Ğ´Ğ° Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğµ Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�"""
    city = message.text.strip()
    await state.update_data(city=city)
    
    # Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ¾Ğ¹ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ (Ğ±ĞµĞ· Ğ¾Ñ‡Ğ¸Ñ�Ñ‚ĞºĞ¸ Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ñ�)
    await save_profile(message, state, clear_state=False)
    
    # Ğ—Ğ°Ñ‚ĞµĞ¼ Ğ½Ğ°Ñ‡Ğ¸Ğ½Ğ°ĞµĞ¼ Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½ÑƒÑ� Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ�
    await ask_measurement(
        message, state,
        "Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ñ€ÑƒĞ´Ğ¸",
        ProfileStates.waiting_for_chest,
        "Ğ˜Ğ·Ğ¼ĞµÑ€Ñ�ĞµÑ‚Ñ�Ñ� Ğ½Ğ° ÑƒÑ€Ğ¾Ğ²Ğ½Ğµ Ñ�Ğ¾Ñ�ĞºĞ¾Ğ², Ğ² Ñ�Ğ¿Ğ¾ĞºĞ¾Ğ¹Ğ½Ğ¾Ğ¼ Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ğ¸ (Ğ½Ğµ Ğ½Ğ° Ğ²Ğ´Ğ¾Ñ…Ğµ). Ğ›ĞµĞ½Ñ‚Ğ° Ğ³Ğ¾Ñ€Ğ¸Ğ·Ğ¾Ğ½Ñ‚Ğ°Ğ»ÑŒĞ½Ğ¾.",
        50, 200
    )

async def ask_measurement(message: Message, state: FSMContext, 
                        measurement_name: str, next_state: State, 
                        instruction: str, min_val: float, max_val: float):
    """Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ğ°Ñ� Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ° Ğ¸Ğ·Ğ¼ĞµÑ€ĞµĞ½Ğ¸Ñ�"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="â�­ï¸� ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        f"ğŸ“� <b>Ğ Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ğ°Ñ� Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ�</b>\n\n"
        f"ğŸ“� <b>{measurement_name} (Ğ² Ñ�Ğ¼):</b>\n\n"
        f"ğŸ’¡ <b>Ğ˜Ğ½Ñ�Ñ‚Ñ€ÑƒĞºÑ†Ğ¸Ñ�:</b> {instruction}\n\n"
        f"Ğ˜Ğ»Ğ¸ Ğ½Ğ°Ğ¶Ğ¼Ğ¸Ñ‚Ğµ Â«ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒÂ», ĞµÑ�Ğ»Ğ¸ Ğ½ĞµÑ‚ Ñ�Ğ°Ğ½Ñ‚Ğ¸Ğ¼ĞµÑ‚Ñ€Ğ¾Ğ²Ğ¾Ğ¹ Ğ»ĞµĞ½Ñ‚Ñ‹:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(next_state)

@router.message(ProfileStates.waiting_for_chest)
async def process_chest(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ³Ñ€ÑƒĞ´Ğ¸"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", "â�­ï¸� Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ"]:
        await state.update_data(chest_cm=None)
    else:
        chest, error = safe_parse_float(message.text, "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ñ€ÑƒĞ´Ğ¸")
        if error or chest < 50 or chest > 200:
            await message.answer("â�Œ Ğ�ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ· Ğ¸Ğ»Ğ¸ Ğ½Ğ°Ğ¶Ğ¼Ğ¸Ñ‚Ğµ Â«ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒÂ».")
            return
        await state.update_data(chest_cm=chest)
    
    # Ğ¡Ğ»ĞµĞ´ÑƒÑ�Ñ‰Ğ¸Ğ¹ Ğ·Ğ°Ğ¼ĞµÑ€ - Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ�
    await ask_measurement(
        message, state,
        "Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ�",
        ProfileStates.waiting_for_forearm,
        "Ğ¡Ğ°Ğ¼Ğ¾Ğµ ÑˆĞ¸Ñ€Ğ¾ĞºĞ¾Ğµ Ğ¼ĞµÑ�Ñ‚Ğ¾ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ� (Ñ‡ÑƒÑ‚ÑŒ Ğ½Ğ¸Ğ¶Ğµ Ğ»Ğ¾ĞºÑ‚Ñ�). Ğ ÑƒĞºĞ° Ñ€Ğ°Ñ�Ñ�Ğ»Ğ°Ğ±Ğ»ĞµĞ½Ğ°, Ğ²Ğ¸Ñ�Ğ¸Ñ‚ Ñ�Ğ²Ğ¾Ğ±Ğ¾Ğ´Ğ½Ğ¾.",
        20, 50
    )

@router.message(ProfileStates.waiting_for_forearm)
async def process_forearm(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ�"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", "â�­ï¸� Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ"]:
        await state.update_data(forearm_cm=None)
    else:
        forearm, error = safe_parse_float(message.text, "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ�")
        if error or forearm < 20 or forearm > 50:
            await message.answer("â�Œ Ğ�ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ· Ğ¸Ğ»Ğ¸ Ğ½Ğ°Ğ¶Ğ¼Ğ¸Ñ‚Ğµ Â«ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒÂ».")
            return
        await state.update_data(forearm_cm=forearm)
    
    # Ğ¡Ğ»ĞµĞ´ÑƒÑ�Ñ‰Ğ¸Ğ¹ Ğ·Ğ°Ğ¼ĞµÑ€ - Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ğ¾Ğ»ĞµĞ½Ğ¸
    await ask_measurement(
        message, state,
        "Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ğ¾Ğ»ĞµĞ½Ğ¸",
        ProfileStates.waiting_for_calf,
        "Ğ¡Ğ°Ğ¼Ğ¾Ğµ ÑˆĞ¸Ñ€Ğ¾ĞºĞ¾Ğµ Ğ¼ĞµÑ�Ñ‚Ğ¾ Ğ¸ĞºÑ€Ñ‹ (Ğ¾Ğ±Ñ‹Ñ‡Ğ½Ğ¾ Ñ‡ÑƒÑ‚ÑŒ Ğ½Ğ¸Ğ¶Ğµ ĞºĞ¾Ğ»ĞµĞ½Ğ°). Ğ¡Ñ‚Ğ¾Ñ�, Ğ²ĞµÑ� Ñ€Ğ°Ğ²Ğ½Ğ¾Ğ¼ĞµÑ€Ğ½Ğ¾ Ğ½Ğ° Ğ¾Ğ±Ğµ Ğ½Ğ¾Ğ³Ğ¸.",
        25, 60
    )

@router.message(ProfileStates.waiting_for_calf)
async def process_calf(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ³Ğ¾Ğ»ĞµĞ½Ğ¸"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", "â�­ï¸� Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ"]:
        await state.update_data(calf_cm=None)
    else:
        calf, error = safe_parse_float(message.text, "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ğ¾Ğ»ĞµĞ½Ğ¸")
        if error or calf < 25 or calf > 60:
            await message.answer("â�Œ Ğ�ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ· Ğ¸Ğ»Ğ¸ Ğ½Ğ°Ğ¶Ğ¼Ğ¸Ñ‚Ğµ Â«ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒÂ».")
            return
        await state.update_data(calf_cm=calf)
    
    # Ğ¡Ğ»ĞµĞ´ÑƒÑ�Ñ‰Ğ¸Ğ¹ Ğ·Ğ°Ğ¼ĞµÑ€ - ÑˆĞ¸Ñ€Ğ¸Ğ½Ğ° Ğ¿Ğ»ĞµÑ‡
    await ask_measurement(
        message, state,
        "Ğ¨Ğ¸Ñ€Ğ¸Ğ½Ğ° Ğ¿Ğ»ĞµÑ‡",
        ProfileStates.waiting_for_shoulder_width,
        "Ğ Ğ°Ñ�Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ğµ Ğ¼ĞµĞ¶Ğ´Ñƒ Ğ°ĞºÑ€Ğ¾Ğ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¼Ğ¸ Ñ‚Ğ¾Ñ‡ĞºĞ°Ğ¼Ğ¸ (ĞºÑ€Ğ°Ğ¹Ğ½Ğ¸Ğµ ĞºĞ¾Ñ�Ñ‚Ğ½Ñ‹Ğµ Ğ²Ñ‹Ñ�Ñ‚ÑƒĞ¿Ñ‹ Ğ¿Ğ»ĞµÑ‡). Ğ›ÑƒÑ‡ÑˆĞµ Ñ� Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ½Ğ¸ĞºĞ¾Ğ¼.",
        30, 60
    )

@router.message(ProfileStates.waiting_for_shoulder_width)
async def process_shoulder_width(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° ÑˆĞ¸Ñ€Ğ¸Ğ½Ñ‹ Ğ¿Ğ»ĞµÑ‡"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", "â�­ï¸� Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ"]:
        await state.update_data(shoulder_width_cm=None)
    else:
        shoulder_width, error = safe_parse_float(message.text, "ÑˆĞ¸Ñ€Ğ¸Ğ½Ğ° Ğ¿Ğ»ĞµÑ‡")
        if error or shoulder_width < 30 or shoulder_width > 60:
            await message.answer("â�Œ Ğ�ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ· Ğ¸Ğ»Ğ¸ Ğ½Ğ°Ğ¶Ğ¼Ğ¸Ñ‚Ğµ Â«ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒÂ».")
            return
        await state.update_data(shoulder_width_cm=shoulder_width)
    
    # ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğ¹ Ğ·Ğ°Ğ¼ĞµÑ€ - ÑˆĞ¸Ñ€Ğ¸Ğ½Ğ° Ñ‚Ğ°Ğ·Ğ°
    await ask_measurement(
        message, state,
        "Ğ¨Ğ¸Ñ€Ğ¸Ğ½Ğ° Ñ‚Ğ°Ğ·Ğ°",
        ProfileStates.waiting_for_hip_width,
        "Ğ Ğ°Ñ�Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ğµ Ğ¼ĞµĞ¶Ğ´Ñƒ Ğ³Ñ€ĞµĞ±Ğ½Ñ�Ğ¼Ğ¸ Ğ¿Ğ¾Ğ´Ğ²Ğ·Ğ´Ğ¾ÑˆĞ½Ñ‹Ñ… ĞºĞ¾Ñ�Ñ‚ĞµĞ¹ (Ñ�Ğ°Ğ¼Ñ‹Ğµ ÑˆĞ¸Ñ€Ğ¾ĞºĞ¸Ğµ Ñ‚Ğ¾Ñ‡ĞºĞ¸ Ñ‚Ğ°Ğ·Ğ°).",
        25, 50
    )

@router.message(ProfileStates.waiting_for_hip_width)
async def process_hip_width(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° ÑˆĞ¸Ñ€Ğ¸Ğ½Ñ‹ Ñ‚Ğ°Ğ·Ğ° Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�"""
    from utils.safe_parser import safe_parse_float
    
    if message.text.lower() in ["Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", "â�­ï¸� Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ"]:
        await state.update_data(hip_width_cm=None)
    else:
        hip_width, error = safe_parse_float(message.text, "ÑˆĞ¸Ñ€Ğ¸Ğ½Ğ° Ñ‚Ğ°Ğ·Ğ°")
        if error or hip_width < 25 or hip_width > 50:
            await message.answer("â�Œ Ğ�ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ· Ğ¸Ğ»Ğ¸ Ğ½Ğ°Ğ¶Ğ¼Ğ¸Ñ‚Ğµ Â«ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒÂ».")
            return
        await state.update_data(hip_width_cm=hip_width)
    
    # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ·Ğ°Ğ¼ĞµÑ€Ñ‹, Ğ½Ğµ Ñ‚Ñ€Ğ¾Ğ³Ğ°Ñ� Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ğ¾Ğ¹ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ
    await save_extended_measurements(message, state)

async def save_extended_measurements(message: Message, state: FSMContext):
    """Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğµ Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ñ… Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ñ… Ğ·Ğ°Ğ¼ĞµÑ€Ğ¾Ğ²"""
    
    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¸Ğ· Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ñ�
    profile_data = await state.get_data()
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ·Ğ°Ğ¼ĞµÑ€Ñ‹
            if 'chest_cm' in profile_data:
                user.chest_cm = profile_data['chest_cm']
            if 'forearm_cm' in profile_data:
                user.forearm_cm = profile_data['forearm_cm']
            if 'calf_cm' in profile_data:
                user.calf_cm = profile_data['calf_cm']
            if 'shoulder_width_cm' in profile_data:
                user.shoulder_width_cm = profile_data['shoulder_width_cm']
            if 'hip_width_cm' in profile_data:
                user.hip_width_cm = profile_data['hip_width_cm']
            
            await session.commit()
            
            # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ Ğ¾Ğ± ÑƒÑ�Ğ¿ĞµÑˆĞ½Ğ¾Ğ¼ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğ¸
            await message.answer(
                "âœ… <b>Ğ Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ·Ğ°Ğ¼ĞµÑ€Ñ‹ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ñ‹!</b>\n\n"
                "Ğ¢ĞµĞ¿ĞµÑ€ÑŒ Ğ² Ğ²Ğ°ÑˆĞµĞ¼ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ğµ Ğ´Ğ¾Ñ�Ñ‚ÑƒĞ¿Ğ½Ñ‹ Ğ´Ğ¾Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ¼ĞµÑ‚Ñ€Ğ¸ĞºĞ¸ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ñ‚ĞµĞ»Ğ°.\n"
                "Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ /profile Ğ´Ğ»Ñ� Ğ¿Ñ€Ğ¾Ñ�Ğ¼Ğ¾Ñ‚Ñ€Ğ° Ğ¿Ğ¾Ğ»Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�.",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

async def save_profile(message: Message, state: FSMContext, clear_state=False):
    """Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğµ Ğ¿Ğ¾Ğ»Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ� Ñ� Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ğ¾Ğ¹ Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸ĞµĞ¹"""
    
    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ²Ñ�Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ
    profile_data = await state.get_data()
    
    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ½Ğ°Ğ»Ğ¸Ñ‡Ğ¸Ğµ Ğ¾Ğ±Ñ�Ğ·Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ñ… Ğ¿Ğ¾Ğ»ĞµĞ¹
    required_fields = ['weight', 'height', 'age', 'gender', 'activity_level', 'goal', 'city']
    missing = [field for field in required_fields if field not in profile_data]
    if missing:
        await message.answer(
            f"â�Œ Ğ�Ğ±Ğ½Ğ°Ñ€ÑƒĞ¶ĞµĞ½Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ°: Ğ¾Ñ‚Ñ�ÑƒÑ‚Ñ�Ñ‚Ğ²ÑƒÑ�Ñ‚ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ: {', '.join(missing)}.\n"
            f"ĞŸĞ¾Ğ¶Ğ°Ğ»ÑƒĞ¹Ñ�Ñ‚Ğ°, Ğ½Ğ°Ñ‡Ğ½Ğ¸Ñ‚Ğµ Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹ĞºÑƒ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ� Ğ·Ğ°Ğ½Ğ¾Ğ²Ğ¾ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile"
        )
        await state.clear()
        return
    
    weight = profile_data['weight']
    height = profile_data['height']
    age = profile_data['age']
    gender = profile_data['gender']
    activity_level = profile_data['activity_level']
    goal = profile_data['goal']
    city = profile_data['city']
    
    # ĞŸÑ€ĞµĞ¾Ğ±Ñ€Ğ°Ğ·ÑƒĞµĞ¼ Ñ€ÑƒÑ�Ñ�ĞºĞ¾Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ² Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¹ ĞºĞ¾Ğ´ Ğ´Ğ»Ñ� ĞºĞ°Ğ»ÑŒĞºÑƒĞ»Ñ�Ñ‚Ğ¾Ñ€Ğ°
    activity_map_calc = {
        "Ğ¼Ğ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ°Ñ�": "low",
        "Ğ»ĞµĞ³ĞºĞ°Ñ�": "medium", 
        "ÑƒĞ¼ĞµÑ€ĞµĞ½Ğ½Ğ°Ñ�": "medium",
        "Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�": "high",
        "Ğ¾Ñ‡ĞµĞ½ÑŒ Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�": "high"
    }
    activity_calc = activity_map_calc.get(activity_level, "medium")
    
    # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ ĞšĞ‘Ğ–Ğ£ Ñ� Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ğ½Ğ¸ĞµĞ¼ ĞºĞ°Ğ»ÑŒĞºÑƒĞ»Ñ�Ñ‚Ğ¾Ñ€Ğ°
    from services.calculator import calculate_calorie_goal, calculate_water_goal
    
    nutrition_goals = calculate_calorie_goal(
        weight=weight,
        height=height, 
        age=age,
        gender=gender,
        activity_level=activity_calc,  # Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğ¹ ĞºĞ¾Ğ´
        goal=goal
    )
    
    # Ğ Ğ°Ñ�Ğ¿Ğ°ĞºĞ¾Ğ²Ñ‹Ğ²Ğ°ĞµĞ¼ ĞºĞ¾Ñ€Ñ‚ĞµĞ¶: (calories, protein_g, fat_g, carbs_g)
    daily_calorie_goal, daily_protein_goal, daily_fat_goal, daily_carbs_goal = nutrition_goals
    
    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ€ĞµĞ°Ğ»ÑŒĞ½ÑƒÑ� Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ñƒ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
    temperature = 20.0  # ĞŸĞ¾ ÑƒĞ¼Ğ¾Ğ»Ñ‡Ğ°Ğ½Ğ¸Ñ�
    try:
        from services.weather import get_temperature
        temperature = await get_temperature(city)
    except Exception as e:
        logger.warning(f"Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚ÑŒ Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ñƒ Ğ´Ğ»Ñ� {city}: {e}")
        temperature = 20.0
    
    water_goal = calculate_water_goal(
        weight=weight,
        activity_level=activity_level,
        temperature=temperature,  # Ğ ĞµĞ°Ğ»ÑŒĞ½Ğ°Ñ� Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ğ°
        goal=goal,  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ñ†ĞµĞ»ÑŒ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
        gender=gender  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¿Ğ¾Ğ» Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
    )
    daily_water_goal = water_goal
    
    # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ² Ğ±Ğ°Ğ·Ñƒ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.weight = weight
            user.height = height
            user.age = age
            user.gender = gender
            user.activity_level = activity_level  # Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ�Ñ‚Ñ€Ğ¾ĞºÑƒ, Ğ° Ğ½Ğµ Ñ‡Ğ¸Ñ�Ğ»Ğ¾
            user.goal = goal
            user.city = city
            user.daily_calorie_goal = round(daily_calorie_goal)
            user.daily_protein_goal = round(daily_protein_goal)
            user.daily_fat_goal = round(daily_fat_goal)
            user.daily_carbs_goal = round(daily_carbs_goal)
            user.daily_water_goal = round(daily_water_goal)
            
            # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ†ĞµĞ»ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
            from utils.activity_calculator import calculate_activity_calorie_goal
            user.daily_activity_goal = calculate_activity_calorie_goal(user)
            
            # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ
            if gender == "female":
                user.neck_cm = profile_data.get('neck_cm')
                user.waist_cm = profile_data.get('waist_cm')
                user.hip_cm = profile_data.get('hip_cm')
            elif gender == "male":
                user.wrist_cm = profile_data.get('wrist_cm')
                user.bicep_cm = profile_data.get('bicep_cm')
            
            # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ½Ğ¾Ğ²Ñ‹Ğµ Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ
            user.chest_cm = profile_data.get('chest_cm')
            user.forearm_cm = profile_data.get('forearm_cm')
            user.calf_cm = profile_data.get('calf_cm')
            user.shoulder_width_cm = profile_data.get('shoulder_width_cm')
            user.hip_width_cm = profile_data.get('hip_width_cm')
            
            await session.commit()
    
    if clear_state:
        await state.clear()
        
        await message.answer(
            f"âœ… <b>ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ÑƒÑ�Ğ¿ĞµÑˆĞ½Ğ¾ Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾ĞµĞ½!</b>\n\n"
            f"ğŸ‘¤ <b>Ğ’Ğ°ÑˆĞ¸ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ:</b>\n"
            f"ğŸ“� Ğ’ĞµÑ�: {weight} ĞºĞ³\n"
            f"ğŸ“� Ğ Ğ¾Ñ�Ñ‚: {height} Ñ�Ğ¼\n"
            f"ğŸ�‚ Ğ’Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚: {age} Ğ»ĞµÑ‚\n"
            f"âš§ï¸� ĞŸĞ¾Ğ»: {'ĞœÑƒĞ¶Ñ�ĞºĞ¾Ğ¹' if gender == 'male' else 'Ğ–ĞµĞ½Ñ�ĞºĞ¸Ğ¹'}\n"
            f"ğŸ�¯ Ğ¦ĞµĞ»ÑŒ: {message.text}\n"
            f"ğŸ�™ï¸� Ğ“Ğ¾Ñ€Ğ¾Ğ´: {city}\n\n"
            f"ğŸ“Š <b>Ğ’Ğ°ÑˆĞ¸ Ğ½Ğ¾Ñ€Ğ¼Ñ‹:</b>\n"
            f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {round(daily_calorie_goal)} ĞºĞºĞ°Ğ»/Ğ´ĞµĞ½ÑŒ\n"
            f"ğŸ¥© Ğ‘ĞµĞ»ĞºĞ¸: {round(daily_protein_goal)} Ğ³/Ğ´ĞµĞ½ÑŒ\n"
            f"ğŸ§ˆ Ğ–Ğ¸Ñ€Ñ‹: {round(daily_fat_goal)} Ğ³/Ğ´ĞµĞ½ÑŒ\n"
            f"ğŸ�� Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {round(daily_carbs_goal)} Ğ³/Ğ´ĞµĞ½ÑŒ\n"
            f"ğŸ’§ Ğ’Ğ¾Ğ´Ğ°: {round(daily_water_goal)} Ğ¼Ğ»/Ğ´ĞµĞ½ÑŒ\n\n"
            f"Ğ¢ĞµĞ¿ĞµÑ€ÑŒ Ğ²Ñ‹ Ğ¼Ğ¾Ğ¶ĞµÑ‚Ğµ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ÑŒ Ğ²Ñ�Ğµ Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ğ¸ Ğ±Ğ¾Ñ‚Ğ°!",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

@router.message(Command("profile") | create_localized_command_filter("Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"))
async def cmd_profile(message: Message, state: FSMContext):
    """ĞŸÑ€Ğ¾Ñ�Ğ¼Ğ¾Ñ‚Ñ€ Ñ‚ĞµĞºÑƒÑ‰ĞµĞ³Ğ¾ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�"""
    await state.clear()
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "â�Œ ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ½Ğµ Ğ½Ğ°Ğ¹Ğ´ĞµĞ½. Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ñ‚ĞµĞºÑ�Ñ‚ Ñ� Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğ¼Ğ¸ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğ¼Ğ¸
        profile_text = f"""ğŸ‘¤ <b>Ğ’Ğ°Ñˆ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ</b>

ğŸ“� <b>Ğ�Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ğµ Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€Ñ‹:</b>
â€¢ Ğ’ĞµÑ�: {user.weight} ĞºĞ³
â€¢ Ğ Ğ¾Ñ�Ñ‚: {user.height} Ñ�Ğ¼
â€¢ Ğ’Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚: {user.age} Ğ»ĞµÑ‚
â€¢ ĞŸĞ¾Ğ»: {'ĞœÑƒĞ¶Ñ�ĞºĞ¾Ğ¹' if user.gender == 'male' else 'Ğ–ĞµĞ½Ñ�ĞºĞ¸Ğ¹'}
â€¢ Ğ“Ğ¾Ñ€Ğ¾Ğ´: {user.city}
â€¢ Ğ¦ĞµĞ»ÑŒ: {user.goal}

ï¿½ <b>Ğ’Ğ°ÑˆĞ¸ Ğ½Ğ¾Ñ€Ğ¼Ñ‹:</b>
â€¢ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {user.daily_calorie_goal} ĞºĞºĞ°Ğ»/Ğ´ĞµĞ½ÑŒ
â€¢ Ğ‘ĞµĞ»ĞºĞ¸: {user.daily_protein_goal} Ğ³/Ğ´ĞµĞ½ÑŒ
â€¢ Ğ–Ğ¸Ñ€Ñ‹: {user.daily_fat_goal} Ğ³/Ğ´ĞµĞ½ÑŒ
â€¢ Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {user.daily_carbs_goal} Ğ³/Ğ´ĞµĞ½ÑŒ
â€¢ Ğ’Ğ¾Ğ´Ğ°: {user.daily_water_goal} Ğ¼Ğ»/Ğ´ĞµĞ½ÑŒ

ğŸ“� <b>Ğ�Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ�:</b>
"""
        
        # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ±Ğ°Ğ·Ğ¾Ğ²Ñ‹Ğµ Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ
        if user.gender == "female":
            if user.neck_cm:
                profile_text += f"â€¢ Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ ÑˆĞµĞ¸: {user.neck_cm} Ñ�Ğ¼\n"
            if user.waist_cm:
                profile_text += f"â€¢ Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ñ‚Ğ°Ğ»Ğ¸Ğ¸: {user.waist_cm} Ñ�Ğ¼\n"
            if user.hip_cm:
                profile_text += f"â€¢ Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€: {user.hip_cm} Ñ�Ğ¼\n"
        elif user.gender == "male":
            if user.wrist_cm:
                profile_text += f"â€¢ Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ�: {user.wrist_cm} Ñ�Ğ¼\n"
            if user.bicep_cm:
                profile_text += f"â€¢ Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ°: {user.bicep_cm} Ñ�Ğ¼\n"
        
        # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ
        extended_measurements = []
        if user.chest_cm:
            extended_measurements.append(f"Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ñ€ÑƒĞ´Ğ¸: {user.chest_cm} Ñ�Ğ¼")
        if user.forearm_cm:
            extended_measurements.append(f"Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ�: {user.forearm_cm} Ñ�Ğ¼")
        if user.calf_cm:
            extended_measurements.append(f"Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ğ¾Ğ»ĞµĞ½Ğ¸: {user.calf_cm} Ñ�Ğ¼")
        if user.shoulder_width_cm:
            extended_measurements.append(f"Ğ¨Ğ¸Ñ€Ğ¸Ğ½Ğ° Ğ¿Ğ»ĞµÑ‡: {user.shoulder_width_cm} Ñ�Ğ¼")
        if user.hip_width_cm:
            extended_measurements.append(f"Ğ¨Ğ¸Ñ€Ğ¸Ğ½Ğ° Ñ‚Ğ°Ğ·Ğ°: {user.hip_width_cm} Ñ�Ğ¼")
        
        if extended_measurements:
            profile_text += "\nğŸ“� <b>Ğ Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ·Ğ°Ğ¼ĞµÑ€Ñ‹:</b>\n"
            for measurement in extended_measurements:
                profile_text += f"â€¢ {measurement}\n"
        else:
            profile_text += "â€¢ Ğ Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ·Ğ°Ğ¼ĞµÑ€Ñ‹: Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½Ñ‹\n"
        
        profile_text += "\nğŸ”§ Ğ”Ğ»Ñ� Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ� Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ /edit_profile"
        
        await message.answer(
            profile_text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )

@router.message(Command("edit_profile"))
async def cmd_edit_profile(message: Message, state: FSMContext):
    """Ğ�Ğ°Ñ‡Ğ°Ğ»Ğ¾ Ñ€ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ� Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�"""
    await state.clear()
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "â�Œ ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ½Ğµ Ğ½Ğ°Ğ¹Ğ´ĞµĞ½. Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ ID Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ´Ğ»Ñ� Ñ€ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ�
        await state.update_data(user_id=user.id, original_data=user.__dict__.copy())
        
        # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ñƒ Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€Ğ° Ğ´Ğ»Ñ� Ñ€ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ�
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ğŸ“� Ğ’ĞµÑ�", callback_data="edit_weight")],
            [InlineKeyboardButton(text="ğŸ“� Ğ Ğ¾Ñ�Ñ‚", callback_data="edit_height")],
            [InlineKeyboardButton(text="ğŸ�‚ Ğ’Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚", callback_data="edit_age")],
            [InlineKeyboardButton(text="âš§ï¸� ĞŸĞ¾Ğ»", callback_data="edit_gender")],
            [InlineKeyboardButton(text="ğŸ�™ï¸� Ğ“Ğ¾Ñ€Ğ¾Ğ´", callback_data="edit_city")],
            [InlineKeyboardButton(text="ğŸ�¯ Ğ¦ĞµĞ»ÑŒ", callback_data="edit_goal")],
            [InlineKeyboardButton(text="ğŸ“� Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚Ñ‹", callback_data="edit_measurements")],
            [InlineKeyboardButton(text="â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°", callback_data="edit_cancel")]
        ])
        
        await message.answer(
            "ğŸ”§ <b>Ğ ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�</b>\n\n"
            "Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€, ĞºĞ¾Ñ‚Ğ¾Ñ€Ñ‹Ğ¹ Ñ…Ğ¾Ñ‚Ğ¸Ñ‚Ğµ Ğ¸Ğ·Ğ¼ĞµĞ½Ğ¸Ñ‚ÑŒ:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

async def process_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€Ğ° Ğ´Ğ»Ñ� Ñ€ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ�"""
    action = callback.data.split("_")[1]
    
    if action == "cancel":
        await state.clear()
        await callback.message.answer(
            "â�Œ Ğ ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¾Ñ‚Ğ¼ĞµĞ½ĞµĞ½Ğ¾",
            reply_markup=get_main_keyboard_v2()
        )
        return
    
    # Ğ£Ñ�Ñ‚Ğ°Ğ½Ğ°Ğ²Ğ»Ğ¸Ğ²Ğ°ĞµĞ¼ Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ğµ Ğ² Ğ·Ğ°Ğ²Ğ¸Ñ�Ğ¸Ğ¼Ğ¾Ñ�Ñ‚Ğ¸ Ğ¾Ñ‚ Ğ²Ñ‹Ğ±Ñ€Ğ°Ğ½Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€Ğ°
    if action == "weight":
        await callback.message.answer("ğŸ“� Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ²ĞµÑ� (Ğ² ĞºĞ³):")
        await state.set_state(ProfileStates.weight)
    elif action == "height":
        await callback.message.answer("ğŸ“� Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ€Ğ¾Ñ�Ñ‚ (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.height)
    elif action == "age":
        await callback.message.answer("ğŸ�‚ Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚:")
        await state.set_state(ProfileStates.age)
    elif action == "gender":
        await callback.message.answer(
            "âš§ï¸� Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ¿Ğ¾Ğ»:",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(ProfileStates.gender)
    elif action == "city":
        await callback.message.answer("ğŸ�™ï¸� Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ³Ğ¾Ñ€Ğ¾Ğ´:")
        await state.set_state(ProfileStates.city)
    elif action == "goal":
        await show_goal_keyboard(callback.message, state)
    elif action == "measurements":
        await show_measurements_keyboard(callback.message, state)
    elif action == "neck":
        await callback.message.answer("ğŸ“� Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ ÑˆĞµĞ¸ (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_neck)
    elif action == "waist":
        await callback.message.answer("â­• Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ñ‚Ğ°Ğ»Ğ¸Ğ¸ (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_waist)
    elif action == "hip":
        await callback.message.answer("ğŸ�‘ Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€ (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_hip)
    elif action == "wrist":
        await callback.message.answer("âŒš Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ� (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_wrist)
    elif action == "bicep":
        await callback.message.answer("ğŸ’ª Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ° (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_bicep)
    elif action == "extended":
        await show_extended_measurements_keyboard(callback.message, state)
    elif action == "chest":
        await callback.message.answer("ğŸ“Š Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ñ€ÑƒĞ´Ğ¸ (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_chest)
    elif action == "forearm":
        await callback.message.answer("ğŸ’ª Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ� (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_forearm)
    elif action == "calf":
        await callback.message.answer("ğŸ¦µ Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ğ¾Ğ»ĞµĞ½Ğ¸ (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_calf)
    elif action == "shoulder_width":
        await callback.message.answer("ğŸ“� Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²ÑƒÑ� ÑˆĞ¸Ñ€Ğ¸Ğ½Ñƒ Ğ¿Ğ»ĞµÑ‡ (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_shoulder_width)
    elif action == "hip_width":
        await callback.message.answer("ğŸ“� Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²ÑƒÑ� ÑˆĞ¸Ñ€Ğ¸Ğ½Ñƒ Ñ‚Ğ°Ğ·Ğ° (Ğ² Ñ�Ğ¼):")
        await state.set_state(ProfileStates.waiting_for_hip_width)
    
    await callback.answer()

async def show_extended_measurements_keyboard(message: Message, state: FSMContext):
    """ĞŸĞ¾ĞºĞ°Ğ· ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ñ‹ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ñ… Ğ·Ğ°Ğ¼ĞµÑ€Ğ¾Ğ²"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ğŸ“Š Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ñ€ÑƒĞ´Ğ¸", callback_data="edit_chest")],
        [InlineKeyboardButton(text="ğŸ’ª Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ�", callback_data="edit_forearm")],
        [InlineKeyboardButton(text="ğŸ¦µ Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ğ¾Ğ»ĞµĞ½Ğ¸", callback_data="edit_calf")],
        [InlineKeyboardButton(text="ğŸ“� Ğ¨Ğ¸Ñ€Ğ¸Ğ½Ğ° Ğ¿Ğ»ĞµÑ‡", callback_data="edit_shoulder_width")],
        [InlineKeyboardButton(text="ğŸ“� Ğ¨Ğ¸Ñ€Ğ¸Ğ½Ğ° Ñ‚Ğ°Ğ·Ğ°", callback_data="edit_hip_width")],
        [InlineKeyboardButton(text="â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°", callback_data="edit_cancel")]
    ])
    
    await message.answer(
        "ğŸ“� <b>Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ·Ğ°Ğ¼ĞµÑ€:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� Ğ±Ğ°Ğ·Ğ¾Ğ²Ñ‹Ñ… Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ñ… Ğ·Ğ°Ğ¼ĞµÑ€Ğ¾Ğ²
@router.message(ProfileStates.waiting_for_neck)
async def process_edit_neck(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° ÑˆĞµĞ¸"""
    await process_measurement_edit(message, state, "neck_cm", "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ ÑˆĞµĞ¸")

@router.message(ProfileStates.waiting_for_waist)
async def process_edit_waist(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ñ‚Ğ°Ğ»Ğ¸Ğ¸"""
    await process_measurement_edit(message, state, "waist_cm", "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ñ‚Ğ°Ğ»Ğ¸Ğ¸")

@router.message(ProfileStates.waiting_for_hip)
async def process_edit_hip(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ±ĞµĞ´ĞµÑ€"""
    await process_measurement_edit(message, state, "hip_cm", "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€")

@router.message(ProfileStates.waiting_for_wrist)
async def process_edit_wrist(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ�"""
    await process_measurement_edit(message, state, "wrist_cm", "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ�")

@router.message(ProfileStates.waiting_for_bicep)
async def process_edit_bicep(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ğ° Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ°"""
    await process_measurement_edit(message, state, "bicep_cm", "Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ°")

# Ğ”ÑƒĞ±Ğ»Ğ¸Ñ€ÑƒÑ�Ñ‰Ğ¸Ğµ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ ÑƒĞ´Ğ°Ğ»ĞµĞ½Ñ‹ - Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµÑ‚Ñ�Ñ� ÑƒĞ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ process_measurement_edit

async def process_measurement_edit(message: Message, state: FSMContext, field_name: str, field_display: str):
    """Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ğ°Ñ� Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ñ� Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ¸ Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ·Ğ°Ğ¼ĞµÑ€Ğ°"""
    from utils.safe_parser import safe_parse_float
    
    value, error = safe_parse_float(message.text, field_display)
    if error:
        await message.answer(f"â�Œ {error}\nĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ·:")
        return
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == (await state.get_data()).get('user_id'))
        )
        user = result.scalar_one_or_none()
        
        if user:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ€Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ Ğ¸Ğ· Ğ±Ğ°Ğ·Ñ‹ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
            old_value = getattr(user, field_name, 'Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½')
            
            setattr(user, field_name, value)
            await session.commit()
            
            # ĞšĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ°Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ñ€Ğ°Ğ·Ğ½Ğ¸Ñ†Ñƒ
            if isinstance(old_value, (int, float)) and isinstance(value, (int, float)):
                diff_text = f"{value - old_value:+.1f}"
            else:
                diff_text = f"{value} (Ğ±Ñ‹Ğ»Ğ¾: {old_value})"
            
            await message.answer(
                f"âœ… <b>{field_display.title()} Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½!</b>\n\n"
                f"ğŸ“� <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b>\n"
                f"Ğ‘Ñ‹Ğ»Ğ¾: {old_value}\n"
                f"Ğ¡Ñ‚Ğ°Ğ»Ğ¾: {value}\n"
                f"Ğ Ğ°Ğ·Ğ½Ğ¸Ñ†Ğ°: {diff_text}\n\n"
                f"ğŸ’¡ ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ÑƒÑ�Ğ¿ĞµÑˆĞ½Ğ¾ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½!",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

async def show_goal_keyboard(message: Message, state: FSMContext):
    """ĞŸĞ¾ĞºĞ°Ğ· ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ñ‹ Ğ´Ğ»Ñ� Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ñ†ĞµĞ»Ğ¸"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ĞŸĞ¾Ñ…ÑƒĞ´ĞµĞ½Ğ¸Ğµ")],
            [KeyboardButton(text="ĞŸĞ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ğµ")],
            [KeyboardButton(text="Ğ�Ğ°Ğ±Ğ¾Ñ€ Ğ¼Ğ°Ñ�Ñ�Ñ‹")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "ğŸ�¯ <b>Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ½Ğ¾Ğ²ÑƒÑ� Ñ†ĞµĞ»ÑŒ:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.goal)

async def show_measurements_keyboard(message: Message, state: FSMContext):
    """ĞŸĞ¾ĞºĞ°Ğ· ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ñ‹ Ğ´Ğ»Ñ� Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ğ·Ğ°Ğ¼ĞµÑ€Ğ¾Ğ²"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ğŸ“� Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ ÑˆĞµĞ¸", callback_data="edit_neck")],
        [InlineKeyboardButton(text="â­• Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ñ‚Ğ°Ğ»Ğ¸Ğ¸", callback_data="edit_waist")],
        [InlineKeyboardButton(text="ğŸ�‘ Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€", callback_data="edit_hip")],
        [InlineKeyboardButton(text="âŒš Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ�", callback_data="edit_wrist")],
        [InlineKeyboardButton(text="ğŸ’ª Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ°", callback_data="edit_bicep")],
        [InlineKeyboardButton(text="ğŸ“Š Ğ Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ·Ğ°Ğ¼ĞµÑ€Ñ‹", callback_data="edit_extended")],
        [InlineKeyboardButton(text="â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°", callback_data="edit_cancel")]
    ])
    
    await message.answer(
            "ğŸ“� <b>Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ·Ğ°Ğ¼ĞµÑ€ Ğ´Ğ»Ñ� Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ�:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@router.message(ProfileStates.weight)
async def process_edit_weight(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ²ĞµÑ�Ğ°"""
    from utils.safe_parser import safe_parse_float
    
    weight, error = safe_parse_float(message.text, "Ğ²ĞµÑ�")
    if error:
        await message.answer(f"â�Œ {error}\nĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ·:")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_weight = original_data.get('weight', 'Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.weight = weight
            # ĞŸĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ñ†ĞµĞ»Ğ¸
            from services.calculator import calculate_calorie_goal, calculate_water_goal
            
            activity_map_calc = {
                "Ğ¼Ğ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ°Ñ�": "low",
                "Ğ»ĞµĞ³ĞºĞ°Ñ�": "medium",
                "ÑƒĞ¼ĞµÑ€ĞµĞ½Ğ½Ğ°Ñ�": "medium",
                "Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�": "high",
                "Ğ¾Ñ‡ĞµĞ½ÑŒ Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�": "high"
            }
            activity_calc = activity_map_calc.get(user.activity_level, "medium")
            
            nutrition_goals = calculate_calorie_goal(
                weight=weight,
                height=user.height,
                age=user.age,
                gender=user.gender,
                activity_level=activity_calc,
                goal=user.goal
            )
            
            daily_calorie_goal, daily_protein_goal, daily_fat_goal, daily_carbs_goal = nutrition_goals
            
            try:
                from services.weather import get_temperature
                temperature = await get_temperature(user.city)
            except:
                temperature = 20.0
                
            water_goal = calculate_water_goal(
                weight=weight,
                activity_level=user.activity_level,
                temperature=temperature,
                goal=user.goal,  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ñ†ĞµĞ»ÑŒ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
                gender=user.gender  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¿Ğ¾Ğ» Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
            )
            
            user.daily_calorie_goal = round(daily_calorie_goal)
            user.daily_protein_goal = round(daily_protein_goal)
            user.daily_fat_goal = round(daily_fat_goal)
            user.daily_carbs_goal = round(daily_carbs_goal)
            user.daily_water_goal = round(water_goal)
            
            await session.commit()
            
            await message.answer(
                f"âœ… <b>Ğ’ĞµÑ� Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½!</b>\n\n"
                f"ğŸ“� <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b>\n"
                f"Ğ‘Ñ‹Ğ»Ğ¾: {old_weight} ĞºĞ³\n"
                f"Ğ¡Ñ‚Ğ°Ğ»Ğ¾: {weight} ĞºĞ³\n"
                f"Ğ Ğ°Ğ·Ğ½Ğ¸Ñ†Ğ°: {weight - old_weight:+.1f} ĞºĞ³\n\n"
                f"ğŸ“Š <b>Ğ�Ğ¾Ğ²Ñ‹Ğµ Ğ½Ğ¾Ñ€Ğ¼Ñ‹:</b>\n"
                f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {user.daily_calorie_goal} ĞºĞºĞ°Ğ»/Ğ´ĞµĞ½ÑŒ\n"
                f"ğŸ’§ Ğ’Ğ¾Ğ´Ğ°: {user.daily_water_goal} Ğ¼Ğ»/Ğ´ĞµĞ½ÑŒ\n\n"
                f"ğŸ’¡ Ğ’Ñ�Ğµ Ñ†ĞµĞ»Ğ¸ Ğ°Ğ²Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ¸Ñ‡ĞµÑ�ĞºĞ¸ Ğ¿ĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ğ°Ğ½Ñ‹!",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.height)
async def process_edit_height(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ñ€Ğ¾Ñ�Ñ‚Ğ°"""
    from utils.safe_parser import safe_parse_int
    
    height, error = safe_parse_int(message.text, "Ñ€Ğ¾Ñ�Ñ‚")
    if error:
        await message.answer(f"â�Œ {error}\nĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ·:")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_height = original_data.get('height', 'Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.height = height
            await session.commit()
            
            await message.answer(
                f"âœ… <b>Ğ Ğ¾Ñ�Ñ‚ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½!</b>\n\n"
                f"ğŸ“� <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b>\n"
                f"Ğ‘Ñ‹Ğ»Ğ¾: {old_height} Ñ�Ğ¼\n"
                f"Ğ¡Ñ‚Ğ°Ğ»Ğ¾: {height} Ñ�Ğ¼\n"
                f"Ğ Ğ°Ğ·Ğ½Ğ¸Ñ†Ğ°: {height - old_height:+d} Ñ�Ğ¼\n\n"
                f"ğŸ’¡ Ğ ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´ÑƒĞµÑ‚Ñ�Ñ� Ğ¿ĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ğ°Ñ‚ÑŒ Ñ†ĞµĞ»Ğ¸ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.age)
async def process_edit_age(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚Ğ°"""
    from utils.safe_parser import safe_parse_int
    
    age, error = safe_parse_int(message.text, "Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚")
    if error:
        await message.answer(f"â�Œ {error}\nĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ·:")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_age = original_data.get('age', 'Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.age = age
            await session.commit()
            
            await message.answer(
                f"âœ… <b>Ğ’Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½!</b>\n\n"
                f"ğŸ�‚ <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b>\n"
                f"Ğ‘Ñ‹Ğ»Ğ¾: {old_age} Ğ»ĞµÑ‚\n"
                f"Ğ¡Ñ‚Ğ°Ğ»Ğ¾: {age} Ğ»ĞµÑ‚\n"
                f"Ğ Ğ°Ğ·Ğ½Ğ¸Ñ†Ğ°: {age - old_age:+d} Ğ»ĞµÑ‚\n\n"
                f"ğŸ’¡ Ğ ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´ÑƒĞµÑ‚Ñ�Ñ� Ğ¿ĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ğ°Ñ‚ÑŒ Ñ†ĞµĞ»Ğ¸ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.gender)
async def process_edit_gender(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ¿Ğ¾Ğ»Ğ°"""
    gender_text = message.text.lower()
    
    if "Ğ¼ÑƒĞ¶Ñ�ĞºĞ¾Ğ¹" in gender_text:
        gender = "male"
        gender_display = "ĞœÑƒĞ¶Ñ�ĞºĞ¾Ğ¹"
    elif "Ğ¶ĞµĞ½Ñ�ĞºĞ¸Ğ¹" in gender_text:
        gender = "female"
        gender_display = "Ğ–ĞµĞ½Ñ�ĞºĞ¸Ğ¹"
    else:
        await message.answer("â�Œ Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ 'ĞœÑƒĞ¶Ñ�ĞºĞ¾Ğ¹' Ğ¸Ğ»Ğ¸ 'Ğ–ĞµĞ½Ñ�ĞºĞ¸Ğ¹'")
        return
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_gender = original_data.get('gender', 'Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½')
    old_display = "ĞœÑƒĞ¶Ñ�ĞºĞ¾Ğ¹" if old_gender == 'male' else "Ğ–ĞµĞ½Ñ�ĞºĞ¸Ğ¹" if old_gender == 'female' else old_gender
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.gender = gender
            await session.commit()
            
            await message.answer(
                f"âœ… <b>ĞŸĞ¾Ğ» Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½!</b>\n\n"
                f"âš§ï¸� <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b>\n"
                f"Ğ‘Ñ‹Ğ»Ğ¾: {old_display}\n"
                f"Ğ¡Ñ‚Ğ°Ğ»Ğ¾: {gender_display}\n\n"
                f"ğŸ’¡ Ğ ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´ÑƒĞµÑ‚Ñ�Ñ� Ğ¿ĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ğ°Ñ‚ÑŒ Ñ†ĞµĞ»Ğ¸ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.city)
async def process_edit_city(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ğ³Ğ¾Ñ€Ğ¾Ğ´Ğ°"""
    city = message.text.strip()
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_city = original_data.get('city', 'Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½')
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.city = city
            
            # ĞŸĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ñ†ĞµĞ»ÑŒ Ğ¿Ğ¾ Ğ²Ğ¾Ğ´Ğµ Ñ� ÑƒÑ‡ĞµÑ‚Ğ¾Ğ¼ Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñ‹
            try:
                from services.weather import get_temperature
                from services.calculator import calculate_water_goal
                
                temperature = await get_temperature(city)
                water_goal = calculate_water_goal(
                    weight=user.weight,
                    activity_level=user.activity_level,
                    temperature=temperature,
                    goal=user.goal,  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ñ†ĞµĞ»ÑŒ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
                    gender=user.gender  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¿Ğ¾Ğ» Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
                )
                user.daily_water_goal = round(water_goal)
                
                weather_info = f"\nğŸ’§ <b>Ğ�Ğ¾Ğ²Ğ°Ñ� Ñ†ĞµĞ»ÑŒ Ğ¿Ğ¾ Ğ²Ğ¾Ğ´Ğµ:</b> {user.daily_water_goal} Ğ¼Ğ»/Ğ´ĞµĞ½ÑŒ (ÑƒÑ‡Ñ‚ĞµĞ½Ğ° Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ğ°)"
            except:
                weather_info = ""
            
            await session.commit()
            
            await message.answer(
                f"âœ… <b>Ğ“Ğ¾Ñ€Ğ¾Ğ´ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½!</b>\n\n"
                f"ğŸ�™ï¸� <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b>\n"
                f"Ğ‘Ñ‹Ğ»Ğ¾: {old_city}\n"
                f"Ğ¡Ñ‚Ğ°Ğ»Ğ¾: {city}\n{weather_info}\n\n"
                f"ğŸ’¡ ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ÑƒÑ�Ğ¿ĞµÑˆĞ½Ğ¾ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½!",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()

@router.message(ProfileStates.goal)
async def process_edit_goal(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ� Ñ†ĞµĞ»Ğ¸"""
    goal_text = message.text.lower()
    
    goal_map = {
        "Ğ¿Ğ¾Ñ…ÑƒĞ´ĞµĞ½Ğ¸Ğµ": "lose_weight",
        "Ğ¿Ğ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸Ğµ": "maintain",
        "Ğ½Ğ°Ğ±Ğ¾Ñ€ Ğ¼Ğ°Ñ�Ñ�Ñ‹": "gain_weight"
    }
    
    if goal_text not in goal_map:
        await message.answer("â�Œ Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ¸Ğ· Ğ¿Ñ€ĞµĞ´Ğ»Ğ¾Ğ¶ĞµĞ½Ğ½Ñ‹Ñ… Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ²")
        return
    
    goal_type = goal_map[goal_text]
    
    data = await state.get_data()
    original_data = data.get('original_data', {})
    old_goal = original_data.get('goal', 'Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½Ğ°')
    old_display = old_goal.replace('_', ' ').title() if old_goal != 'Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½Ğ°' else old_goal
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == data['user_id'])
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.goal = goal_type
            
            # ĞŸĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ñ†ĞµĞ»Ğ¸
            from services.calculator import calculate_calorie_goal
            
            activity_map_calc = {
                "Ğ¼Ğ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ°Ñ�": "low",
                "Ğ»ĞµĞ³ĞºĞ°Ñ�": "medium",
                "ÑƒĞ¼ĞµÑ€ĞµĞ½Ğ½Ğ°Ñ�": "medium",
                "Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�": "high",
                "Ğ¾Ñ‡ĞµĞ½ÑŒ Ğ²Ñ‹Ñ�Ğ¾ĞºĞ°Ñ�": "high"
            }
            activity_calc = activity_map_calc.get(user.activity_level, "medium")
            
            nutrition_goals = calculate_calorie_goal(
                weight=user.weight,
                height=user.height,
                age=user.age,
                gender=user.gender,
                activity_level=activity_calc,
                goal=goal_type
            )
            
            daily_calorie_goal, daily_protein_goal, daily_fat_goal, daily_carbs_goal = nutrition_goals
            
            user.daily_calorie_goal = round(daily_calorie_goal)
            user.daily_protein_goal = round(daily_protein_goal)
            user.daily_fat_goal = round(daily_fat_goal)
            user.daily_carbs_goal = round(daily_carbs_goal)
            
            # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ†ĞµĞ»ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ¿Ñ€Ğ¸ Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğ¸ Ñ†ĞµĞ»Ğ¸
            from utils.activity_calculator import calculate_activity_calorie_goal
            user.daily_activity_goal = calculate_activity_calorie_goal(user)
            
            await session.commit()
            
            profile_text = ""
            profile_text += f"â€¢ Ğ“Ğ¾Ñ€Ğ¾Ğ´: {user.city}\n"
            profile_text += f"â€¢ Ğ¦ĞµĞ»ÑŒ: {user.goal}\n\n"
            profile_text += f"ğŸ“Š <b>Ğ’Ğ°ÑˆĞ¸ Ğ½Ğ¾Ñ€Ğ¼Ñ‹:</b>\n"
            profile_text += f"â€¢ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {user.daily_calorie_goal} ĞºĞºĞ°Ğ»/Ğ´ĞµĞ½ÑŒ\n"
            profile_text += f"â€¢ Ğ‘ĞµĞ»ĞºĞ¸: {user.daily_protein_goal} Ğ³/Ğ´ĞµĞ½ÑŒ\n"
            profile_text += f"â€¢ Ğ–Ğ¸Ñ€Ñ‹: {user.daily_fat_goal} Ğ³/Ğ´ĞµĞ½ÑŒ\n"
            profile_text += f"â€¢ Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {user.daily_carbs_goal} Ğ³/Ğ´ĞµĞ½ÑŒ\n"
            profile_text += f"â€¢ Ğ’Ğ¾Ğ´Ğ°: {user.daily_water_goal} Ğ¼Ğ»/Ğ´ĞµĞ½ÑŒ\n\n"
            profile_text += "ğŸ“� <b>Ğ�Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ�:</b>\n"
            
            await message.answer(
                f"âœ… <b>Ğ¦ĞµĞ»ÑŒ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½Ğ°!</b>\n\n"
                f"ğŸ�¯ <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b>\n"
                f"Ğ‘Ñ‹Ğ»Ğ¾: {old_display}\n"
                f"Ğ¡Ñ‚Ğ°Ğ»Ğ¾: {message.text}\n\n"
                f"{profile_text}",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
    
    await state.clear()
