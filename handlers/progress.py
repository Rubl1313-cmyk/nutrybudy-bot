"""
handlers/progress.py
Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸ Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, Meal, Activity, DrinkEntry, WeightEntry
from keyboards.reply_v2 import get_main_keyboard_v2
from keyboards.inline import get_progress_menu

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("progress"))
async def cmd_progress(message: Message, state: FSMContext):
    """ĞŸĞ¾ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°"""
    await state.clear()
    
    await message.answer(
        "ğŸ“Š <b>Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´ Ğ´Ğ»Ñ� Ğ¿Ñ€Ğ¾Ñ�Ğ¼Ğ¾Ñ‚Ñ€Ğ° Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸:</b>",
        reply_markup=get_progress_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("progress_"))
async def progress_callback(callback: CallbackQuery, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´Ğ° Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°"""
    await callback.answer()
    
    period = callback.data.split("_")[1]  # day, week, month, all
    user_id = callback.from_user.id
    
    try:
        async with get_session() as session:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await callback.message.answer(
                    "â�Œ ĞŸĞ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ Ğ½Ğµ Ğ½Ğ°Ğ¹Ğ´ĞµĞ½. Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                    reply_markup=get_main_keyboard_v2()
                )
                return
            
            # Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµĞ¼ Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´
            from datetime import datetime, timedelta
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
                start_date = today - timedelta(days=365)
                period_name = "Ğ·Ğ° Ğ²Ñ�Ñ‘ Ğ²Ñ€ĞµĞ¼Ñ�"
            
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ
            stats = await get_period_stats(user.id, session, start_date)
            
            # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ
            message_text = await create_progress_message(user, stats, period_name)
            
            await callback.message.answer(
                    "❌ Пользователь не найден. Сначала настройте профиль командой /set_profile",
                    reply_markup=get_main_keyboard_v2()
                )
            
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ¿Ğ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°: {e}")
        await callback.message.answer(
            "â�Œ ĞŸÑ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ³Ñ€ÑƒĞ·ĞºĞµ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·.",
            reply_markup=get_main_keyboard_v2()
        )

@router.callback_query(F.data.startswith("period_"))
async def period_callback(callback: CallbackQuery, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´Ğ° (Ğ´Ğ»Ñ� Ñ�Ğ¾Ğ²Ğ¼ĞµÑ�Ñ‚Ğ¸Ğ¼Ğ¾Ñ�Ñ‚Ğ¸ Ñ� common.py)"""
    await progress_callback(callback, state)

async def get_period_stats(user_id: int, session, start_date) -> dict:
    """ĞŸĞ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğµ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸ Ğ·Ğ° Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´ - Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµÑ‚ unified Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ñ� Ğ¸Ğ· utils.daily_stats"""
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
    
    return await unified_get_period_stats(user_id, period)

async def create_progress_message(user, stats: dict, period_name: str) -> str:
    """Ğ¡Ğ¾Ğ·Ğ´Ğ°Ğ½Ğ¸Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ� Ñ� Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ¾Ğ¼"""
    
    # Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚ÑƒÑ�Ñ‹
    calorie_status = "ğŸ�¯" if stats['total_calories'] <= user.daily_calorie_goal else "âš ï¸�"
    water_status = "ğŸ’§" if stats['total_water_ml'] >= user.daily_water_goal else "ğŸ’¦"
    
    # ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ² Ğ¿Ñ€Ğ¾Ñ†ĞµĞ½Ñ‚Ğ°Ñ…
    calorie_progress = (stats['total_calories'] / user.daily_calorie_goal * 100) if user.daily_calorie_goal > 0 else 0
    water_progress = (stats['total_water_ml'] / user.daily_water_goal * 100) if user.daily_water_goal > 0 else 0
    
    # Ğ¢Ñ€ĞµĞ½Ğ´ Ğ²ĞµÑ�Ğ°
    trend_emoji = "ğŸ“ˆ" if stats['weight_trend'] and stats['weight_trend'] < 0 else "ğŸ“Š"
    weight_info = f"{trend_emoji} Ğ¢Ñ€ĞµĞ½Ğ´ Ğ²ĞµÑ�Ğ°: {stats['weight_trend']:+.1f} ĞºĞ³" if stats['weight_trend'] else ""
    
    message = (
        f"ğŸ“Š <b>Ğ’Ğ°Ñˆ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� {period_name}</b>\n\n"
        f"ğŸ”¥ <b>ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸:</b>\n"
        f"   {calorie_status} ĞŸĞ¾Ñ‚Ñ€ĞµĞ±Ğ»ĞµĞ½Ğ¾: {stats['total_calories']:.0f} ĞºĞºĞ°Ğ»\n"
        f"   ğŸ”¥ Ğ¡Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ¾: {stats['calories_burned']:.0f} ĞºĞºĞ°Ğ»\n"
        f"   âš–ï¸� Ğ‘Ğ°Ğ»Ğ°Ğ½Ñ�: {stats['total_calories'] - stats['calories_burned']:+.0f} ĞºĞºĞ°Ğ»\n"
        f"   ğŸ“Š Ğ¡Ñ€ĞµĞ´Ğ½ĞµĞµ: {stats['total_calories']:.0f}/{user.daily_calorie_goal:.0f} ĞºĞºĞ°Ğ»\n"
        f"   ğŸ“ˆ ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�: {calorie_progress:.1f}%\n\n"
        f"ğŸ’§ <b>Ğ’Ğ¾Ğ´Ğ°:</b>\n"
        f"   {water_status} Ğ’Ñ�ĞµĞ³Ğ¾: {stats['total_water_ml']:.0f} Ğ¼Ğ»\n"
        f"   ğŸ“Š Ğ¦ĞµĞ»ÑŒ: {user.daily_water_goal:.0f} Ğ¼Ğ»\n"
        f"   ğŸ“ˆ ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�: {water_progress:.1f}%\n\n"
        f"ğŸ¥© <b>Ğ‘Ğ–Ğ£:</b>\n"
        f"   ğŸ¥ª Ğ‘ĞµĞ»ĞºĞ¸: {stats['total_protein']:.1f} Ğ³\n"
        f"   ğŸ§ˆ Ğ–Ğ¸Ñ€Ñ‹: {stats['total_fat']:.1f} Ğ³\n"
        f"   ğŸ�� Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {stats['total_carbs']:.1f} Ğ³\n\n"
        f"ğŸ“ˆ <b>Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ:</b>\n"
        f"   ğŸ�½ï¸� ĞŸÑ€Ğ¸ĞµĞ¼Ğ¾Ğ² Ğ¿Ğ¸Ñ‰Ğ¸: {stats['meals_count']}\n"
        f"   ğŸ�ƒ Ğ¢Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ğº: {stats['activities_count']}\n"
    )
    
    if weight_info:
        message += f"\n{weight_info}"
    
    if stats['latest_weight']:
        message += f"\nâš–ï¸� Ğ¢ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ�: {stats['latest_weight']:.1f} ĞºĞ³"
    
    # ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ�
    if calorie_progress >= 90 and calorie_progress <= 110:
        message += f"\n\nğŸ�¯ Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ñ‹Ğ¹ Ñ€ĞµĞ·ÑƒĞ»ÑŒÑ‚Ğ°Ñ‚! Ğ’Ñ‹ Ğ½Ğ° Ñ†ĞµĞ»Ğ¸!"
    elif calorie_progress > 110:
        message += f"\n\nâš ï¸� Ğ�ĞµĞ¼Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ñ€ĞµĞ²Ñ‹ÑˆĞ°ĞµĞ¼ Ğ½Ğ¾Ñ€Ğ¼Ñƒ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹"
    else:
        message += f"\n\nğŸ’ª ĞœĞ¾Ğ¶Ğ½Ğ¾ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ¸Ñ‚ÑŒ Ğ½ĞµĞ¼Ğ½Ğ¾Ğ³Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹"
    
    return message

@router.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext):
    """Ğ‘Ñ‹Ñ�Ñ‚Ñ€Ğ°Ñ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�"""
    await state.clear()
    
    async with get_session() as session:
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "â�Œ Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�
        today = message.date
        stats = await get_period_stats(user.id, session, today)
        
        # ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�
        calorie_progress = (stats['total_calories'] / user.daily_calorie_goal * 100) if user.daily_calorie_goal > 0 else 0
        water_progress = (stats['total_water_ml'] / user.daily_water_goal * 100) if user.daily_water_goal > 0 else 0
        
        await message.answer(
            f"ğŸ“Š <b>Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�</b>\n\n"
            f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {stats['total_calories']:.0f}/{user.daily_calorie_goal:.0f} ĞºĞºĞ°Ğ» ({calorie_progress:.1f}%)\n"
            f"ğŸ’§ Ğ’Ğ¾Ğ´Ğ°: {stats['total_water_ml']:.0f}/{user.daily_water_goal:.0f} Ğ¼Ğ» ({water_progress:.1f}%)\n"
            f"ğŸ¥ª Ğ‘ĞµĞ»ĞºĞ¸: {stats['total_protein']:.1f} Ğ³\n"
            f"ğŸ§ˆ Ğ–Ğ¸Ñ€Ñ‹: {stats['total_fat']:.1f} Ğ³\n"
            f"ğŸ�� Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {stats['total_carbs']:.1f} Ğ³\n\n"
            f"ğŸ�½ï¸� ĞŸÑ€Ğ¸ĞµĞ¼Ğ¾Ğ² Ğ¿Ğ¸Ñ‰Ğ¸: {stats['meals_count']}\n"
            f"ğŸ�ƒ Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ: {stats['activities_count']} Ñ€Ğ°Ğ·",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )
