"""
Ğ�Ğ±Ñ‰Ğ¸Ğµ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹: /start, /help, /cancel, Ğ¸ Ğ¸Ğ½Ñ‚ĞµÑ€Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ� Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ¸.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

from keyboards.reply_v2 import get_main_keyboard_v2
from keyboards.inline import get_progress_menu
from utils.localized_commands import create_localized_command_filter

router = Router()

@router.message(Command("start") | create_localized_command_filter("Ñ�Ñ‚Ğ°Ñ€Ñ‚"))
async def cmd_start(message: Message, state: FSMContext):
    """ĞŸÑ€Ğ¸Ğ²ĞµÑ‚Ñ�Ñ‚Ğ²Ğ¸Ğµ Ğ½Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
    await state.clear()
    
    user_name = message.from_user.first_name or "ĞŸĞ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ"
    
    welcome_text = f"""âœ¨ ĞŸÑ€Ğ¸Ğ²ĞµÑ‚, {user_name}! Ğ¯ â€” Ğ²Ğ°Ñˆ Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ AI-Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ½Ğ¸Ğº Ğ¿Ğ¾ Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²ÑŒÑ�.

ğŸ¤– <b>Ğ§Ñ‚Ğ¾ Ñ� ÑƒĞ¼ĞµÑ�:</b>
â€¢ ğŸ�½ï¸� Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸ â€” Ğ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¾ Ğ¾Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ, Ñ‡Ñ‚Ğ¾ Ñ�ÑŠĞµĞ»Ğ¸, Ğ¸Ğ»Ğ¸ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²ÑŒÑ‚Ğµ Ñ„Ğ¾Ñ‚Ğ¾
â€¢ ğŸ’§ Ğ�Ñ‚Ñ�Ğ»ĞµĞ¶Ğ¸Ğ²Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ â€” Ğ½Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ, Ñ�ĞºĞ¾Ğ»ÑŒĞºĞ¾ Ğ²Ñ‹Ğ¿Ğ¸Ğ»Ğ¸
â€¢ ğŸ�ƒ Ğ£Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°Ñ‚ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ğ¸ ÑˆĞ°Ğ³Ğ¸ â€” Â«Ğ¿Ñ€Ğ¾Ğ±ĞµĞ¶Ğ°Ğ» 5 ĞºĞ¼Â» Ğ¸Ğ»Ğ¸ Â«10000 ÑˆĞ°Ğ³Ğ¾Ğ²Â»
â€¢ âš–ï¸� Ğ�Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒ Ğ²ĞµÑ� Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� â€” Ğ¿Ğ¾ĞºĞ°Ğ¶Ñƒ Ğ³Ñ€Ğ°Ñ„Ğ¸ĞºĞ¸ Ğ¸ Ğ´Ğ°Ğ¼ Ğ¿Ñ€Ğ¾Ğ³Ğ½Ğ¾Ğ·
â€¢ ğŸ§¬ Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°Ñ‚ÑŒ ĞºĞ¾Ğ¼Ğ¿Ğ¾Ğ·Ğ¸Ñ†Ğ¸Ñ� Ñ‚ĞµĞ»Ğ° â€” Ğ¸Ğ½Ğ´ĞµĞºÑ� Ğ¼Ğ°Ñ�Ñ�Ñ‹ Ñ‚ĞµĞ»Ğ° (Ğ˜ĞœĞ¢), Ğ¿Ñ€Ğ¾Ñ†ĞµĞ½Ñ‚ Ğ¶Ğ¸Ñ€Ğ°, Ğ¼Ñ‹ÑˆĞµÑ‡Ğ½ÑƒÑ� Ğ¼Ğ°Ñ�Ñ�Ñƒ Ğ¸ Ğ½Ğ¾Ñ€Ğ¼Ñ‹
â€¢ ğŸ¤– Ğ�Ñ‚Ğ²ĞµÑ‡Ğ°Ñ‚ÑŒ Ğ½Ğ° Ğ»Ñ�Ğ±Ñ‹Ğµ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�Ñ‹ Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ğ¸, Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°Ñ… Ğ¸ Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²ÑŒĞµ

ğŸ’¬ <b>ĞšĞ°Ğº Ğ¾Ğ±Ñ‰Ğ°Ñ‚ÑŒÑ�Ñ�?</b>
ĞŸÑ€Ğ¾Ñ�Ñ‚Ğ¾ Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ¼Ğ½Ğµ Ğ²Ñ�Ñ‘, Ñ‡Ñ‚Ğ¾ Ñ�Ñ‡Ğ¸Ñ‚Ğ°ĞµÑ‚Ğµ Ğ½ÑƒĞ¶Ğ½Ñ‹Ğ¼.
Ğ¯ Ñ�Ğ°Ğ¼ Ğ¿Ğ¾Ğ¹Ğ¼Ñƒ, Ñ‡Ñ‚Ğ¾ Ğ½ÑƒĞ¶Ğ½Ğ¾: Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ ĞµĞ´Ñƒ, Ğ¿Ğ¾ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ¸Ğ»Ğ¸ Ğ´Ğ°Ñ‚ÑŒ Ñ�Ğ¾Ğ²ĞµÑ‚.

ğŸ‘‰ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:</b>
â€¢ Â«Ğ¡ĞµĞ³Ğ¾Ğ´Ğ½Ñ� Ğ½Ğ° Ğ¾Ğ±ĞµĞ´ Ñ�ÑŠĞµĞ» 200Ğ³ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğ¹ Ğ³Ñ€ÑƒĞ´ĞºĞ¸ Ñ� Ğ³Ñ€ĞµÑ‡ĞºĞ¾Ğ¹Â»
â€¢ Â«Ğ’Ñ‹Ğ¿Ğ¸Ğ»Ğ° 3 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½Ğ° Ğ²Ğ¾Ğ´Ñ‹Â»
â€¢ Â«ĞšĞ°ĞºĞ¾Ğ¹ Ñƒ Ğ¼ĞµĞ½Ñ� Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ·Ğ° Ğ½ĞµĞ´ĞµĞ»Ñ�?Â»
â€¢ Â«ĞŸĞ¾Ñ�Ğ¾Ğ²ĞµÑ‚ÑƒĞ¹ Ñ€ĞµÑ†ĞµĞ¿Ñ‚ ÑƒĞ¶Ğ¸Ğ½Ğ° Ñ� Ğ²Ñ‹Ñ�Ğ¾ĞºĞ¸Ğ¼ Ñ�Ğ¾Ğ´ĞµÑ€Ğ¶Ğ°Ğ½Ğ¸ĞµĞ¼ Ğ±ĞµĞ»ĞºĞ°Â»

<b>âš ï¸� Ğ’Ğ°Ğ¶Ğ½Ğ¾:</b> Ğ”Ğ»Ñ� Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğ³Ğ¾ Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° ĞšĞ‘Ğ–Ğ£ Ğ¸ Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ñ… Ñ€ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´Ğ°Ñ†Ğ¸Ğ¹ Ñ�Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile

Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ğµ Ğ² Ğ¼ĞµĞ½Ñ� Ğ½Ğ¸Ğ¶Ğµ Ğ¸Ğ»Ğ¸ Ğ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¾ Ğ·Ğ°Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�."""
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("help") | create_localized_command_filter("Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰ÑŒ"))
async def cmd_help(message: Message, state: FSMContext):
    """Ğ’Ñ‹Ğ·Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ¸Ğ½Ñ‚ĞµÑ€Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ� Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ¸."""
    await state.clear()
    await show_help_menu(message)

@router.message(Command("cancel"))
@router.message(F.text == "â�Œ Ğ�Ñ‚Ğ¼ĞµĞ½Ğ°")
async def cmd_cancel(message: Message, state: FSMContext):
    """Ğ�Ñ‚Ğ¼ĞµĞ½Ğ° Ñ‚ĞµĞºÑƒÑ‰ĞµĞ³Ğ¾ Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ñ�."""
    await state.clear()
    await message.answer(
        "â�Œ <b>Ğ”ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ğµ Ğ¾Ñ‚Ğ¼ĞµĞ½ĞµĞ½Ğ¾</b>\n\n"
        "Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹ ĞºĞ½Ğ¾Ğ¿ĞºĞ¸ Ğ¼ĞµĞ½Ñ� Ğ´Ğ»Ñ� Ğ½Ğ°Ğ²Ğ¸Ğ³Ğ°Ñ†Ğ¸Ğ¸.",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text == "ğŸ�  Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�")
async def cmd_main_menu(message: Message, state: FSMContext):
    """Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‚ Ğ² Ğ³Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�."""
    await state.clear()
    await message.answer(
        "ğŸ�  <b>Ğ“Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ�</b>",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

async def show_help_menu(event: Message | CallbackQuery):
    """Ğ�Ñ‚Ğ¾Ğ±Ñ€Ğ°Ğ¶Ğ°ĞµÑ‚ Ğ³Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ� Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ¸ Ñ� Ğ¸Ğ½Ğ»Ğ°Ğ¹Ğ½-ĞºĞ½Ğ¾Ğ¿ĞºĞ°Ğ¼Ğ¸."""
    text = (
        "ğŸ“š <b>Ğ Ğ°Ğ·Ğ´ĞµĞ»Ñ‹ Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ¸</b>\n\n"
        "Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸ Ñ‚ĞµĞ¼Ñƒ, Ñ‡Ñ‚Ğ¾Ğ±Ñ‹ ÑƒĞ·Ğ½Ğ°Ñ‚ÑŒ Ğ¿Ğ¾Ğ´Ñ€Ğ¾Ğ±Ğ½ĞµĞµ:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ğŸ�½ï¸� ĞŸĞ¸Ñ‚Ğ°Ğ½Ğ¸Ğµ", callback_data="help_food")],
        [InlineKeyboardButton(text="ğŸ’§ Ğ’Ğ¾Ğ´Ğ° Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ", callback_data="help_water")],
        [InlineKeyboardButton(text="ğŸ“Š ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�", callback_data="help_progress")],
        [InlineKeyboardButton(text="ğŸ‘¤ ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ", callback_data="help_profile")],
        [InlineKeyboardButton(text="ğŸ¤– AI ĞŸĞ¾Ğ¼Ğ¾Ñ‰Ğ½Ğ¸Ğº", callback_data="help_ai")],
        [InlineKeyboardButton(text="â�Œ Ğ—Ğ°ĞºÑ€Ñ‹Ñ‚ÑŒ", callback_data="help_close")]
    ])

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:  # CallbackQuery
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await event.answer()

@router.callback_query(F.data.startswith("help_"))
async def help_callbacks(callback: CallbackQuery):
    data = callback.data
    if data == "help_food":
        text = (
            "ğŸ�½ï¸� <b>ĞŸĞ¸Ñ‚Ğ°Ğ½Ğ¸Ğµ</b>\n\n"
            "ğŸ“¸ <b>Ğ¤Ğ¾Ñ‚Ğ¾ ĞµĞ´Ñ‹</b> â€“ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²ÑŒ Ñ„Ğ¾Ñ‚Ğ¾, Ñ� Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ñ� Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹ Ğ¸ Ğ¿Ñ€ĞµĞ´Ğ»Ğ¾Ğ¶Ñƒ Ğ²Ğ²ĞµÑ�Ñ‚Ğ¸ Ğ²ĞµÑ�.\n"
            "   <i>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Ñ�Ñ„Ğ¾Ñ‚Ğ¾Ğ³Ñ€Ğ°Ñ„Ğ¸Ñ€ÑƒĞ¹ Ñ‚Ğ°Ñ€ĞµĞ»ĞºÑƒ Ñ� ĞµĞ´Ğ¾Ğ¹</i>\n\n"
            "âœ�ï¸� <b>Ğ ÑƒÑ‡Ğ½Ğ¾Ğ¹ Ğ²Ğ²Ğ¾Ğ´</b> â€“ Ğ½Ğ°Ğ¿Ğ¸ÑˆĞ¸ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹ Ñ‡ĞµÑ€ĞµĞ· Ğ·Ğ°Ğ¿Ñ�Ñ‚ÑƒÑ�.\n"
            "   <i>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Â«Ğ³Ñ€ĞµÑ‡ĞºĞ°, ĞºÑƒÑ€Ğ¸Ğ½Ğ°Ñ� Ğ³Ñ€ÑƒĞ´ĞºĞ°, Ğ¾Ğ³ÑƒÑ€ĞµÑ†Â»</i>\n\n"
            "ğŸ�½ï¸� <b>ĞŸĞ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�</b> â€“ Ñ�Ğ³ĞµĞ½ĞµÑ€Ğ¸Ñ€ÑƒÑ� Ğ¼ĞµĞ½Ñ� Ğ½Ğ° Ğ´ĞµĞ½ÑŒ Ñ� ÑƒÑ‡Ñ‘Ñ‚Ğ¾Ğ¼ Ñ‚Ğ²Ğ¾Ğ¸Ñ… Ğ½Ğ¾Ñ€Ğ¼.\n\n"
            "ğŸ”� <b>ĞŸĞ¾Ğ¸Ñ�Ğº Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ°</b> â€“ Ğ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¾ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ, Ğ¸ Ñ� Ğ¿Ğ¾ĞºĞ°Ğ¶Ñƒ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ğ¸ Ğ‘Ğ–Ğ£.\n"
            "   <i>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Â«Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾Â»</i>"
        )
    elif data == "help_water":
        text = (
            "ğŸ’§ <b>Ğ’Ğ¾Ğ´Ğ° Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ</b>\n\n"
            "ğŸ’§ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ</b> â€“ Ğ²Ñ‹Ğ±ĞµÑ€Ğ¸ Ğ¾Ğ±ÑŠÑ‘Ğ¼ Ğ¸Ğ· Ğ¿Ñ€ĞµĞ´Ğ»Ğ¾Ğ¶ĞµĞ½Ğ½Ñ‹Ñ… Ğ¸Ğ»Ğ¸ Ğ²Ğ²ĞµĞ´Ğ¸ Ğ²Ñ€ÑƒÑ‡Ğ½ÑƒÑ�.\n"
            "   <i>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Â«250 Ğ¼Ğ»Â» Ğ¸Ğ»Ğ¸ Â«Ñ�Ñ‚Ğ°ĞºĞ°Ğ½ Ğ²Ğ¾Ğ´Ñ‹Â»</i>\n\n"
            "ğŸ‘Ÿ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ ÑˆĞ°Ğ³Ğ¸</b> â€“ Ğ²Ğ²ĞµĞ´Ğ¸ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ ÑˆĞ°Ğ³Ğ¾Ğ², Ñ� Ğ¿ĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ğ°Ñ� Ğ² ĞºĞ¸Ğ»Ğ¾Ğ¼ĞµÑ‚Ñ€Ñ‹ Ğ¸ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸.\n"
            "   <i>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Â«Ğ¿Ñ€Ğ¾ÑˆÑ‘Ğ» 5000 ÑˆĞ°Ğ³Ğ¾Ğ²Â»</i>\n\n"
            "ğŸ�ƒ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ</b> â€“ Ğ²Ñ‹Ğ±ĞµÑ€Ğ¸ Ñ‚Ğ¸Ğ¿ Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ¸ Ğ¸ ÑƒĞºĞ°Ğ¶Ğ¸ Ğ´Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ.\n"
            "   <i>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Â«Ğ±ĞµĞ³ 30 Ğ¼Ğ¸Ğ½ÑƒÑ‚Â»</i>"
        )
    elif data == "help_progress":
        text = (
            "ğŸ“Š <b>ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�</b>\n\n"
            "ğŸ“ˆ <b>Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ°</b> â€“ Ğ¿Ñ€Ğ¾Ñ�Ğ¼Ğ¾Ñ‚Ñ€ Ğ¿Ğ¾Ñ‚Ñ€ĞµĞ±Ğ»Ñ‘Ğ½Ğ½Ñ‹Ñ… ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹, Ğ²Ğ¾Ğ´Ñ‹, Ğ²ĞµÑ�Ğ° Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸.\n"
            "ğŸ“… <b>ĞŸĞµÑ€Ğ¸Ğ¾Ğ´Ñ‹</b> â€“ Ğ¼Ğ¾Ğ¶Ğ½Ğ¾ Ğ¿Ğ¾Ñ�Ğ¼Ğ¾Ñ‚Ñ€ĞµÑ‚ÑŒ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ·Ğ° Ğ´ĞµĞ½ÑŒ, Ğ½ĞµĞ´ĞµĞ»Ñ� Ğ¸Ğ»Ğ¸ Ğ¼ĞµÑ�Ñ�Ñ†.\n"
            "ğŸ“‰ <b>Ğ“Ñ€Ğ°Ñ„Ğ¸ĞºĞ¸</b> â€“ Ğ½Ğ°Ğ³Ğ»Ñ�Ğ´Ğ½Ğ°Ñ� Ğ´Ğ¸Ğ½Ğ°Ğ¼Ğ¸ĞºĞ° Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğ¹ Ğ²ĞµÑ�Ğ° Ğ¸ Ğ¿Ğ¾Ñ‚Ñ€ĞµĞ±Ğ»ĞµĞ½Ğ¸Ñ�."
        )
    elif data == "help_profile":
        text = (
            "ğŸ‘¤ <b>ĞŸÑ€Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ</b>\n\n"
            "âš–ï¸� <b>Ğ”Ğ°Ğ½Ğ½Ñ‹Ğµ</b> â€“ Ğ²ĞµÑ�, Ñ€Ğ¾Ñ�Ñ‚, Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚, Ğ¿Ğ¾Ğ», ÑƒÑ€Ğ¾Ğ²ĞµĞ½ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸, Ñ†ĞµĞ»ÑŒ, Ğ³Ğ¾Ñ€Ğ¾Ğ´.\n"
            "ğŸ“Š <b>Ğ�Ğ¾Ñ€Ğ¼Ñ‹</b> â€“ Ñ� Ğ°Ğ²Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ¸Ñ‡ĞµÑ�ĞºĞ¸ Ñ€Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ğ°Ñ� Ğ´Ğ½ĞµĞ²Ğ½ÑƒÑ� Ğ½Ğ¾Ñ€Ğ¼Ñƒ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹, Ğ‘Ğ–Ğ£ Ğ¸ Ğ²Ğ¾Ğ´Ñ‹.\n"
            "âœ�ï¸� <b>Ğ ĞµĞ´Ğ°ĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ</b> â€“ Ğ¼Ğ¾Ğ¶Ğ½Ğ¾ Ğ¸Ğ·Ğ¼ĞµĞ½Ğ¸Ñ‚ÑŒ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ² Ğ»Ñ�Ğ±Ğ¾Ğµ Ğ²Ñ€ĞµĞ¼Ñ�."
        )
    elif data == "help_ai":
        text = (
            "ğŸ¤– <b>AI ĞŸĞ¾Ğ¼Ğ¾Ñ‰Ğ½Ğ¸Ğº</b>\n\n"
            "ğŸ’¬ <b>Ğ”Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ¾Ğ²Ñ‹Ğ¹ Ñ€ĞµĞ¶Ğ¸Ğ¼</b> â€“ Ğ·Ğ°Ğ´Ğ°Ğ²Ğ°Ğ¹ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�Ñ‹, Ñ� Ğ¿Ğ¾Ğ¼Ğ½Ñ� ĞºĞ¾Ğ½Ñ‚ĞµĞºÑ�Ñ‚ Ğ±ĞµÑ�ĞµĞ´Ñ‹.\n"
            "   <i>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Â«ĞšĞ°ĞºĞ¾Ğ¹ Ñ€ĞµÑ†ĞµĞ¿Ñ‚ Ğ¿Ğ°Ñ�Ñ‚Ñ‹?Â» â†’ Â«Ğ� Ñ� Ğ¼Ğ¾Ñ€ĞµĞ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ°Ğ¼Ğ¸?Â»</i>\n\n"
            "ğŸŒ¦ï¸� <b>ĞŸĞ¾Ğ³Ğ¾Ğ´Ğ°</b> â€“ Ğ¼Ğ¾Ğ³Ñƒ Ñ�ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñƒ Ğ² Ğ»Ñ�Ğ±Ğ¾Ğ¼ Ğ³Ğ¾Ñ€Ğ¾Ğ´Ğµ.\n"
            "   <i>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Â«Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ğ° Ğ² ĞœĞ¾Ñ�ĞºĞ²ĞµÂ»</i>\n\n"
            "ğŸ“� <b>Ğ¡Ğ¾Ğ²ĞµÑ‚Ñ‹</b> â€“ Ñ�Ğ¿Ñ€Ğ°ÑˆĞ¸Ğ²Ğ°Ğ¹ Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ğ¸, Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°Ñ…, Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²ÑŒĞµ.\n\n"
            "â�Œ <b>Ğ’Ñ‹Ñ…Ğ¾Ğ´</b> â€“ Ğ½Ğ°Ğ¿Ğ¸ÑˆĞ¸ Â«Ğ²Ñ‹Ñ…Ğ¾Ğ´Â» Ğ¸Ğ»Ğ¸ /cancel, Ñ‡Ñ‚Ğ¾Ğ±Ñ‹ Ğ²Ñ‹Ğ¹Ñ‚Ğ¸ Ğ¸Ğ· Ñ€ĞµĞ¶Ğ¸Ğ¼Ğ°."
        )
    elif data == "help_close":
        await callback.message.delete()
        await callback.answer()
        return
    else:
        await callback.answer()
        return

    if text:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ğŸ”™ Ğ�Ğ°Ğ·Ğ°Ğ´", callback_data="help_back")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

@router.callback_query(F.data == "help_back")
async def help_back_callback(callback: CallbackQuery):
    """Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‚ Ğ² Ğ³Ğ»Ğ°Ğ²Ğ½Ğ¾Ğµ Ğ¼ĞµĞ½Ñ� Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ¸."""
    await show_help_menu(callback)

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ´Ğ»Ñ� reply-ĞºĞ½Ğ¾Ğ¿Ğ¾Ğº Ğ¸Ğ· Ñ�Ñ‚Ğ°Ñ€Ğ¾Ğ³Ğ¾ common.py
@router.message(F.text == "ğŸ“Š ĞœĞ¾Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�")
async def progress_message(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ° Ñ� Ğ¼Ğ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸ĞµĞ¹"""
    from handlers.progress import cmd_progress
    await cmd_progress(message, state)

@router.message(F.text == "ğŸ‘¤ ĞœĞ¾Ğ¹ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ")
async def profile_message(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ� Ñ� Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸ĞµĞ¹"""
    from handlers.profile import cmd_profile
    await cmd_profile(message, state)

@router.message(F.text == "â�“ ĞŸĞ¾Ğ¼Ğ¾Ñ‰ÑŒ")
async def help_message(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ¸ Ñ� Ğ´Ñ€ÑƒĞ¶ĞµĞ»Ñ�Ğ±Ğ½Ñ‹Ğ¼ Ğ¿Ğ¾Ğ´Ñ…Ğ¾Ğ´Ğ¾Ğ¼"""
    await cmd_help(message, state)

# Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ´Ğ»Ñ� callback Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°
async def period_callback_internal(callback: CallbackQuery, state: FSMContext):
    """Ğ’Ğ½ÑƒÑ‚Ñ€ĞµĞ½Ğ½Ğ¸Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´Ğ°"""
    try:
        period = callback.data.split("_")[1]  # day / week / month / all
        user_id = callback.from_user.id

        await callback.answer(f"ğŸ“Š Ğ—Ğ°Ğ³Ñ€ÑƒĞ¶Ğ°Ñ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ...")
        await callback.message.delete()
        await state.clear()

        from database.db import get_session
        from database.models import User
        from sqlalchemy import select
        from datetime import datetime, timedelta

        async with get_session() as session:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                await callback.message.answer(
                    "â�Œ ĞŸĞ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ Ğ½Ğµ Ğ½Ğ°Ğ¹Ğ´ĞµĞ½.",
                    reply_markup=get_main_keyboard_v2()
                )
                return

            # Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµĞ¼ Ğ´Ğ¸Ğ°Ğ¿Ğ°Ğ·Ğ¾Ğ½ Ğ´Ğ°Ñ‚
            today = datetime.now().date()
            if period == "day":
                start_date = today
                period_name = "Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�"
            elif period == "week":
                start_date = today - timedelta(days=7)
                period_name = "Ğ·Ğ° Ğ½ĞµĞ´ĞµĞ»Ñ�"
            elif period == "month":
                start_date = today - timedelta(days=30)
                period_name = "Ğ·Ğ° Ğ¼ĞµÑ�Ñ�Ñ†"
            else:  # all
                start_date = today - timedelta(days=365)  # Ğ—Ğ° Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğ¹ Ğ³Ğ¾Ğ´
                period_name = "Ğ·Ğ° Ğ²Ñ�Ñ‘ Ğ²Ñ€ĞµĞ¼Ñ�"

            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ·Ğ° Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´
            from utils.daily_stats import get_period_stats as unified_get_period_stats
            
            # Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµĞ¼ Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´ Ğ½Ğ° Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğµ start_date
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            if start_date == today:
                period = "day"
            elif start_date == today - timedelta(days=7):
                period = "week"
            elif start_date == today - timedelta(days=30):
                period = "month"
            else:
                period = "all"
            
            stats = await unified_get_period_stats(user.id, period)
            
            # Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ Ñ� Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ¾Ğ¼
            progress_message = await _create_progress_message(user, stats, period_name, period)
            
            await callback.message.answer(
                progress_message, 
                reply_markup=get_main_keyboard_v2(), 
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Error in period callback: {e}")
        await callback.message.answer(
            "â�Œ ĞŸÑ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ³Ñ€ÑƒĞ·ĞºĞµ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·.",
            reply_markup=get_main_keyboard_v2()
        )


async def _create_progress_message(user, stats: dict, period_name: str, period: str) -> str:
    """Ğ¡Ğ¾Ğ·Ğ´Ğ°Ğ½Ğ¸Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ� Ñ� Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ¾Ğ¼"""
    
    # Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚ÑƒÑ�Ñ‹ Ğ¸ Ğ¼Ğ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ�
    calorie_status = "ğŸ�¯" if stats['total_calories'] <= user.daily_calorie_goal else "âš ï¸�"
    water_status = "ğŸ’§" if stats['total_water_ml'] >= user.daily_water_goal else "ğŸ’¦"
    
    # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ
    message = f"ğŸ“Š <b>Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° {period_name}</b>\n\n"
    
    # ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸
    message += f"ğŸ”¥ <b>ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸:</b> {stats['total_calories']:.0f} ĞºĞºĞ°Ğ»\n"
    message += f"   Ğ�Ğ¾Ñ€Ğ¼Ğ°: {user.daily_calorie_goal:.0f} ĞºĞºĞ°Ğ» {calorie_status}\n\n"
    
    # Ğ‘Ğ–Ğ£
    message += f"ğŸ�½ï¸� <b>Ğ‘Ğ–Ğ£:</b>\n"
    message += f"   ğŸ¥© Ğ‘ĞµĞ»ĞºĞ¸: {stats['total_protein']:.1f}Ğ³\n"
    message += f"   ğŸ¥‘ Ğ–Ğ¸Ñ€Ñ‹: {stats['total_fat']:.1f}Ğ³\n"
    message += f"   ğŸ�š Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {stats['total_carbs']:.1f}Ğ³\n\n"
    
    # Ğ’Ğ¾Ğ´Ğ°
    message += f"ğŸ’§ <b>Ğ’Ğ¾Ğ´Ğ°:</b> {stats['total_water_ml']:.0f} Ğ¼Ğ»\n"
    message += f"   Ğ�Ğ¾Ñ€Ğ¼Ğ°: {user.daily_water_goal:.0f} Ğ¼Ğ» {water_status}\n\n"
    
    # Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ
    if stats['calories_burned'] > 0:
        message += f"ğŸ�ƒ <b>Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ:</b> {stats['calories_burned']:.0f} ĞºĞºĞ°Ğ» Ñ�Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ¾\n"
        message += f"   Ğ¢Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ğº: {stats['activities_count']}\n\n"
    
    # Ğ’ĞµÑ�
    if stats['weight_trend'] is not None:
        trend_emoji = "ğŸ“ˆ" if stats['weight_trend'] > 0 else "ğŸ“‰" if stats['weight_trend'] < 0 else "â�¡ï¸�"
        message += f"âš–ï¸� <b>Ğ’ĞµÑ�:</b> {stats['latest_weight']:.1f} ĞºĞ³ {trend_emoji}\n"
        if stats['weight_trend'] != 0:
            message += f"   Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ: {stats['weight_trend']:+.1f} ĞºĞ³ Ğ·Ğ° {period_name}\n\n"
    
    # ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ�
    if stats['total_calories'] <= user.daily_calorie_goal and stats['total_water_ml'] >= user.daily_water_goal:
        message += "ğŸ�‰ <b>Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ°Ñ� Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°!</b> Ğ’Ñ‹ Ğ¿Ñ€Ğ¸Ğ´ĞµÑ€Ğ¶Ğ¸Ğ²Ğ°ĞµÑ‚ĞµÑ�ÑŒ Ğ½Ğ¾Ñ€Ğ¼ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹ Ğ¸ Ğ²Ğ¾Ğ´Ñ‹!"
    elif stats['total_calories'] <= user.daily_calorie_goal:
        message += "ğŸ’ª <b>Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ¾!</b> ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ Ğ² Ğ½Ğ¾Ñ€Ğ¼Ğµ, Ğ½Ğµ Ğ·Ğ°Ğ±Ñ‹Ğ²Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ğ¸Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ!"
    elif stats['total_water_ml'] >= user.daily_water_goal:
        message += "ğŸ’§ <b>Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾!</b> Ğ’Ğ¾Ğ´Ğ½Ñ‹Ğ¹ Ñ€ĞµĞ¶Ğ¸Ğ¼ Ñ�Ğ¾Ğ±Ğ»Ñ�Ğ´ĞµĞ½, Ñ�Ğ»ĞµĞ´Ğ¸Ñ‚Ğµ Ğ·Ğ° ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ñ�Ğ¼Ğ¸!"
    else:
        message += "ğŸ“� <b>Ğ¡Ğ¾Ğ²ĞµÑ‚:</b> Ğ¡Ñ‚Ğ°Ñ€Ğ°Ğ¹Ñ‚ĞµÑ�ÑŒ Ñ�Ğ¾Ğ±Ğ»Ñ�Ğ´Ğ°Ñ‚ÑŒ Ğ½Ğ¾Ñ€Ğ¼Ñ‹ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹ Ğ¸ Ğ¿Ğ¸Ñ‚ÑŒ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ Ğ²Ğ¾Ğ´Ñ‹."
    
    return message

# Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº callback
@router.callback_query()
async def universal_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ²Ñ�ĞµÑ… callback"""
    data = callback.data
    
    # Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° period_ callback
    if data.startswith("period_"):
        await period_callback_internal(callback, state)
        return
    
    # Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° progress_ callback
    if data.startswith("progress_"):
        await period_callback_internal(callback, state)
        return
    
    # Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° help_ callback
    if data.startswith("help_"):
        await help_callbacks(callback)
        return
    
    # Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° edit_ callback - Ğ¿ĞµÑ€ĞµĞ½Ğ°Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ² profile.py
    if data.startswith("edit_"):
        # Ğ˜Ğ¼Ğ¿Ğ¾Ñ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¸ Ğ²Ñ‹Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ¸Ğ· profile.py
        from handlers.profile import process_edit_callback
        await process_edit_callback(callback, state)
        return
    
    # Ğ”Ñ€ÑƒĞ³Ğ¸Ğµ callback
    logger.warning(f"Unknown callback: {data}")
    await callback.answer()
