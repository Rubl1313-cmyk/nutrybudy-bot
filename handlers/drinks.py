"""
Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ² - Ğ·Ğ°Ğ¼ĞµĞ½Ğ° water.py
ĞŸĞ¾Ğ´Ğ´ĞµÑ€Ğ¶Ğ¸Ğ²Ğ°ĞµÑ‚ Ğ²Ğ¾Ğ´Ñƒ, Ñ�Ğ¾ĞºĞ¸, Ñ‡Ğ°Ğ¹, ĞºĞ¾Ñ„Ğµ Ğ¸ Ğ´Ñ€ÑƒĞ³Ğ¸Ğµ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¸ Ñ� ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ñ�Ğ¼Ğ¸
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, DrinkEntry
from keyboards.reply_v2 import get_main_keyboard_v2
from utils.drink_parser import parse_drink
from utils.daily_stats import get_daily_water
from services.soup_service import save_drink
from utils.localized_commands import create_localized_command_filter

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("log_drink"))
async def cmd_log_drink(message: Message, state: FSMContext):
    """Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ¿Ğ¾Ñ‚Ñ€ĞµĞ±Ğ»ĞµĞ½Ğ¸Ñ� Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸ (Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²)"""
    await state.clear()
    
    await message.answer(
        "ğŸ’§ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸</b>\n\n"
        "Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ, Ñ‡Ñ‚Ğ¾ Ğ²Ñ‹ Ğ²Ñ‹Ğ¿Ğ¸Ğ»Ğ¸ Ğ¸ Ñ�ĞºĞ¾Ğ»ÑŒĞºĞ¾:\n\n"
        "â€¢ <b>Ğ’Ğ¾Ğ´Ğ°:</b> 200 Ğ¼Ğ», 1 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½, 0.5 Ğ»\n"
        "â€¢ <b>Ğ¡Ğ¾ĞºĞ¸:</b> Ñ�Ğ¾Ğº 250 Ğ¼Ğ», Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ğº 200\n"
        "â€¢ <b>Ğ§Ğ°Ğ¹/ĞºĞ¾Ñ„Ğµ:</b> Ñ‡Ğ°Ğ¹ Ñ� Ñ�Ğ°Ñ…Ğ°Ñ€Ğ¾Ğ¼ 300, ĞºĞ¾Ñ„Ğµ Ñ� Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾Ğ¼ 150\n"
        "â€¢ <b>ĞœĞ¾Ğ»Ğ¾Ñ‡Ğ½Ñ‹Ğµ:</b> Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾ 250, ĞºĞµÑ„Ğ¸Ñ€ 200, Ğ¹Ğ¾Ğ³ÑƒÑ€Ñ‚ 150\n"
        "â€¢ <b>Ğ”Ñ€ÑƒĞ³Ğ¾Ğµ:</b> Ğ³Ğ°Ğ·Ğ¸Ñ€Ğ¾Ğ²ĞºĞ° 330, ĞºĞ¾Ğ¼Ğ¿Ğ¾Ñ‚ 200, Ñ�Ğ¼ÑƒĞ·Ğ¸ 250\n\n"
        "ğŸ¤– Ğ¯ Ğ°Ğ²Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ¸Ñ‡ĞµÑ�ĞºĞ¸ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ� Ñ‚Ğ¸Ğ¿ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ° Ğ¸ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸!",
        parse_mode="HTML"
    )

@router.message(Command("log_water") | create_localized_command_filter("Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ_Ğ²Ğ¾Ğ´Ñƒ"))
async def cmd_log_water(message: Message, state: FSMContext):
    """Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ²Ğ¾Ğ´Ñ‹ (Ğ´Ğ»Ñ� Ñ�Ğ¾Ğ²Ğ¼ĞµÑ�Ñ‚Ğ¸Ğ¼Ğ¾Ñ�Ñ‚Ğ¸)"""
    return await cmd_log_drink(message, state)

@router.message(Command("drink"))
@router.message(Command("water") | create_localized_command_filter("Ğ²Ğ¾Ğ´Ğ°"))
async def cmd_drink_stats(message: Message, state: FSMContext):
    """Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ¿Ğ¾Ñ‚Ñ€ĞµĞ±Ğ»ĞµĞ½Ğ¸Ñ� Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸"""
    await state.clear()
    
    async with get_session() as session:
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль командой /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ� Ñ� ÑƒÑ‡ĞµÑ‚Ğ¾Ğ¼ Ñ‡Ğ°Ñ�Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ğ¿Ğ¾Ñ�Ñ�Ğ°
        from utils.timezone_utils import get_user_local_date
        
        # Ğ�Ğ±Ñ‰Ğ°Ñ� Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ
        total_volume = await get_daily_water(user.id, user.timezone)
        
        # ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ Ğ¸Ğ· Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²
        from utils.daily_stats import get_daily_drink_calories
        total_calories = await get_daily_drink_calories(user.id, user.timezone)
        
        # Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ·Ğ° Ğ½ĞµĞ´ĞµĞ»Ñ�
        from datetime import timedelta
        today_local = get_user_local_date(user.timezone)
        week_ago = today_local - timedelta(days=7)
        
        week_result = await session.execute(
            select(func.sum(DrinkEntry.volume_ml)).where(
                DrinkEntry.user_id == user.id,
                func.date(DrinkEntry.datetime) >= week_ago
            )
        )
        week_total = week_result.scalar() or 0
        
        # ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�
        progress = (total_volume / user.daily_water_goal) * 100
        remaining = max(0, user.daily_water_goal - total_volume)
        
        # Ğ¡Ñ‚Ğ°Ñ‚ÑƒÑ�
        if progress >= 100:
            status = "ğŸ�‰ Ğ¦ĞµĞ»ÑŒ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ½ÑƒÑ‚Ğ°!"
        elif progress >= 75:
            status = "ğŸ’ª Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾!"
        elif progress >= 50:
            status = "ğŸ‘� Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ¾"
        elif progress >= 25:
            status = "ğŸ’§ Ğ�ÑƒĞ¶Ğ½Ğ° Ğ²Ğ¾Ğ´Ğ°"
        else:
            status = "ğŸš¨ ĞŸĞµĞ¹Ñ‚Ğµ Ğ²Ğ¾Ğ´Ñƒ!"
        
        await message.answer(
            f"ğŸ’§ <b>Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸</b>\n\n"
            f"ğŸ“… <b>Ğ¡ĞµĞ³Ğ¾Ğ´Ğ½Ñ�:</b>\n"
            f"ğŸ’¦ Ğ’Ñ�ĞµĞ³Ğ¾ Ğ²Ñ‹Ğ¿Ğ¸Ñ‚Ğ¾: {total_volume:.0f} Ğ¼Ğ»\n"
            f"ğŸ�¯ Ğ¦ĞµĞ»ÑŒ: {user.daily_water_goal} Ğ¼Ğ»\n"
            f"ğŸ“ˆ ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�: {progress:.1f}%\n"
            f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ Ğ¸Ğ· Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²: {total_calories:.0f} ĞºĞºĞ°Ğ»\n"
            f"ğŸ’¦ Ğ�Ñ�Ñ‚Ğ°Ğ»Ğ¾Ñ�ÑŒ: {remaining:.0f} Ğ¼Ğ»\n\n"
            f"ğŸ“Š <b>Ğ�ĞµĞ´ĞµĞ»Ñ�:</b> {week_total:.0f} Ğ¼Ğ»\n\n"
            f"{status}\n\n"
            f"Ğ”Ğ»Ñ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ /log_drink",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

@router.message(F.text.regexp(r'(\d+\.?\d*)\s*(Ğ¼Ğ»|Ğ»|Ñ�Ñ‚Ğ°ĞºĞ°Ğ½|Ñ‡Ğ°ÑˆĞºĞ°|Ğ±ÑƒÑ‚Ñ‹Ğ»ĞºĞ°|glass|bottle|cup)?'))
async def process_drink(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°"""
    try:
        # ĞŸÑ€Ğ¾Ğ±ÑƒĞµĞ¼ Ñ€Ğ°Ñ�Ğ¿Ğ°Ñ€Ñ�Ğ¸Ñ‚ÑŒ ĞºĞ°Ğº Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº
        volume, drink_name, calories = await parse_drink(message.text)
        
        if not volume or volume <= 0:
            await message.answer(
                "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ğ¸Ñ‚ÑŒ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·:\n\n"
                "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹: 200 Ğ¼Ğ», 250, 0.5 Ğ», 1 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½"
            )
            return
        
        if volume > 5000:  # Ğ—Ğ°Ñ‰Ğ¸Ñ‚Ğ° Ğ¾Ñ‚ Ñ�Ğ»Ğ¸ÑˆĞºĞ¾Ğ¼ Ğ±Ğ¾Ğ»ÑŒÑˆĞ¸Ñ… Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğ¹
            await message.answer(
                "â�Œ Ğ¡Ğ»Ğ¸ÑˆĞºĞ¾Ğ¼ Ğ±Ğ¾Ğ»ÑŒÑˆĞ¾Ğµ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾. ĞœĞ°ĞºÑ�Ğ¸Ğ¼ÑƒĞ¼ 5 Ğ»Ğ¸Ñ‚Ñ€Ğ¾Ğ² Ğ·Ğ° Ñ€Ğ°Ğ·."
            )
            return
        
        # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº
        result = await save_drink(message.from_user.id, message.text)
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ� Ñ� ÑƒÑ‡ĞµÑ‚Ğ¾Ğ¼ Ñ‡Ğ°Ñ�Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ğ¿Ğ¾Ñ�Ñ�Ğ°
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = user_result.scalar_one_or_none()
            
            # Ğ�Ğ±Ñ‰Ğ°Ñ� Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ
            total_volume = await get_daily_water(user.id, user.timezone)
            
            # ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ Ğ¸Ğ· Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²
            total_calories = await get_daily_drink_calories(user.id, user.timezone)
            
            progress = (total_volume / user.daily_water_goal) * 100
            
            # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¾Ñ‚Ğ²ĞµÑ‚
            if calories > 0:
                calorie_info = f"\nğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {calories:.0f} ĞºĞºĞ°Ğ»"
            else:
                calorie_info = ""
            
            await message.answer(
                f"âœ… <b>Ğ–Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ°!</b>\n\n"
                f"ğŸ’§ {drink_name.title()}: {volume:.0f} Ğ¼Ğ»{calorie_info}\n\n"
                f"ğŸ“Š <b>Ğ’Ñ�ĞµĞ³Ğ¾ Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�:</b>\n"
                f"ğŸ’¦ Ğ–Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ: {total_volume:.0f} Ğ¼Ğ»\n"
                f"ğŸ�¯ Ğ¦ĞµĞ»ÑŒ: {user.daily_water_goal} Ğ¼Ğ»\n"
                f"ğŸ“ˆ ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�: {progress:.1f}%\n"
                f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ Ğ¸Ğ· Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²: {total_calories:.0f} ĞºĞºĞ°Ğ»\n\n"
                f"{'ğŸ�‰ Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾!' if progress >= 100 else 'ğŸ’ª ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ!'}",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°: {e}")
        await message.answer(
            "â�Œ ĞŸÑ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ°. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·.",
            reply_markup=get_main_keyboard_v2()
        )

@router.callback_query(F.data == "log_water")
@router.callback_query(F.data == "log_drink")
async def log_drink_callback(callback: CallbackQuery, state: FSMContext):
    """Callback Ğ´Ğ»Ñ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸ Ğ¸Ğ· Ğ¼ĞµĞ½Ñ�"""
    await callback.answer()
    
    await callback.message.answer(
        "ğŸ’§ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸</b>\n\n"
        "Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ, Ñ‡Ñ‚Ğ¾ Ğ²Ñ‹ Ğ²Ñ‹Ğ¿Ğ¸Ğ»Ğ¸ Ğ¸ Ñ�ĞºĞ¾Ğ»ÑŒĞºĞ¾:\n\n"
        "â€¢ <b>Ğ’Ğ¾Ğ´Ğ°:</b> 200 Ğ¼Ğ», 1 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½, 0.5 Ğ»\n"
        "â€¢ <b>Ğ¡Ğ¾ĞºĞ¸:</b> Ñ�Ğ¾Ğº 250 Ğ¼Ğ», Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ğº 200\n"
        "â€¢ <b>Ğ§Ğ°Ğ¹/ĞºĞ¾Ñ„Ğµ:</b> Ñ‡Ğ°Ğ¹ Ñ� Ñ�Ğ°Ñ…Ğ°Ñ€Ğ¾Ğ¼ 300, ĞºĞ¾Ñ„Ğµ Ñ� Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾Ğ¼ 150\n"
        "â€¢ <b>ĞœĞ¾Ğ»Ğ¾Ñ‡Ğ½Ñ‹Ğµ:</b> Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾ 250, ĞºĞµÑ„Ğ¸Ñ€ 200, Ğ¹Ğ¾Ğ³ÑƒÑ€Ñ‚ 150\n"
        "â€¢ <b>Ğ”Ñ€ÑƒĞ³Ğ¾Ğµ:</b> Ğ³Ğ°Ğ·Ğ¸Ñ€Ğ¾Ğ²ĞºĞ° 330, ĞºĞ¾Ğ¼Ğ¿Ğ¾Ñ‚ 200, Ñ�Ğ¼ÑƒĞ·Ğ¸ 250\n\n"
        "ğŸ¤– Ğ¯ Ğ°Ğ²Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ¸Ñ‡ĞµÑ�ĞºĞ¸ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ� Ñ‚Ğ¸Ğ¿ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ° Ğ¸ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸!",
        parse_mode="HTML"
    )
