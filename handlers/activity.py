"""
handlers/activity.py
Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ ÑƒÑ‡ĞµÑ‚Ğ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from sqlalchemy import select

from database.db import get_session
from database.models import User, Activity
from keyboards.reply import get_main_keyboard

logger = logging.getLogger(__name__)
router = Router()

class ActivityStates(StatesGroup):
    """Ğ¡Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    waiting_for_activity_type = State()
    waiting_for_duration = State()
    waiting_for_calories = State()

@router.message(Command("fitness"))
async def cmd_fitness(message: Message, state: FSMContext):
    """Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ñ„Ğ¸Ñ‚Ğ½ĞµÑ� Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    await state.clear()
    
    await message.answer(
        "ğŸ�ƒ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ñ„Ğ¸Ñ‚Ğ½ĞµÑ� Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸</b>\n\n"
        "Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ñ‚Ğ¸Ğ¿ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:\n\n"
        "â€¢ Ğ‘ĞµĞ³\n"
        "â€¢ Ğ¥Ğ¾Ğ´ÑŒĞ±Ğ°\n"
        "â€¢ Ğ’ĞµĞ»Ğ¾Ñ�Ğ¸Ğ¿ĞµĞ´\n"
        "â€¢ ĞŸĞ»Ğ°Ğ²Ğ°Ğ½Ğ¸Ğµ\n"
        "â€¢ Ğ¢Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ° Ğ² Ğ·Ğ°Ğ»Ğµ\n"
        "â€¢ Ğ™Ğ¾Ğ³Ğ°\n"
        "â€¢ Ğ”Ñ€ÑƒĞ³Ğ¾Ğµ\n\n"
        "Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:",
        parse_mode="HTML"
    )
    await state.set_state(ActivityStates.waiting_for_activity_type)

@router.message(ActivityStates.waiting_for_activity_type)
async def process_activity_type(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ñ‚Ğ¸Ğ¿Ğ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    activity_type = message.text.strip()
    
    if not activity_type:
        await message.answer("â�Œ Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:")
        return
    
    await state.update_data(activity_type=activity_type)
    
    await message.answer(
        f"â�±ï¸� <b>Ğ”Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸ (Ğ² Ğ¼Ğ¸Ğ½ÑƒÑ‚Ğ°Ñ…):</b>\n\n"
        f"Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 30",
        parse_mode="HTML"
    )
    await state.set_state(ActivityStates.waiting_for_duration)

@router.message(ActivityStates.waiting_for_duration)
async def process_duration(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ´Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    try:
        duration = int(message.text)
        
        if duration < 1 or duration > 480:  # ĞœĞ°ĞºÑ�Ğ¸Ğ¼ÑƒĞ¼ 8 Ñ‡Ğ°Ñ�Ğ¾Ğ²
            await message.answer(
                "â�Œ Ğ”Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ Ğ´Ğ¾Ğ»Ğ¶Ğ½Ğ° Ğ±Ñ‹Ñ‚ÑŒ Ğ¾Ñ‚ 1 Ğ´Ğ¾ 480 Ğ¼Ğ¸Ğ½ÑƒÑ‚. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·:"
            )
            return
        
        await state.update_data(duration=duration)
        
        await message.answer(
            f"ğŸ”¥ <b>Ğ¡Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ½Ñ‹Ğµ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ (Ğ¾Ğ¿Ñ†Ğ¸Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ğ¾):</b>\n\n"
            f"Ğ•Ñ�Ğ»Ğ¸ Ğ·Ğ½Ğ°ĞµÑ‚Ğµ Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğµ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹, Ğ²Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ ĞµĞ³Ğ¾.\n"
            f"Ğ•Ñ�Ğ»Ğ¸ Ğ½ĞµÑ‚, Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²ÑŒÑ‚Ğµ 0 Ğ¸ Ñ� Ñ€Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ğ°Ñ� Ğ°Ğ²Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ¸Ñ‡ĞµÑ�ĞºĞ¸.\n\n"
            f"Ğ�Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€: 250 Ğ¸Ğ»Ğ¸ 0",
            parse_mode="HTML"
        )
        await state.set_state(ActivityStates.waiting_for_calories)
        
    except ValueError:
        await message.answer("â�Œ Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ Ñ‡Ğ¸Ñ�Ğ»Ğ¾. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·:")

@router.message(ActivityStates.waiting_for_calories)
async def process_calories(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹ Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğµ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    try:
        user_calories = int(message.text)
        
        if user_calories < 0 or user_calories > 5000:
            await message.answer(
                "â�Œ Ğ�ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·:"
            )
            return
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ
        activity_data = await state.get_data()
        activity_type = activity_data['activity_type']
        duration = activity_data['duration']
        
        # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ ĞµÑ�Ğ»Ğ¸ Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½Ñ‹
        if user_calories == 0:
            calories_burned = estimate_calories_burned(activity_type, duration)
        else:
            calories_burned = user_calories
        
        # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ² Ğ±Ğ°Ğ·Ñƒ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
        async with get_session() as session:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await message.answer(
                    "â�Œ Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                    reply_markup=get_main_keyboard()
                )
                return
            
            # Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ğ·Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ¾Ğ± Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
            activity = Activity(
                user_id=user.id,
                activity_type=activity_type,
                duration=duration,
                calories_burned=calories_burned,
                datetime=message.date
            )
            
            session.add(activity)
            await session.commit()
        
        await state.clear()
        
        await message.answer(
            f"âœ… <b>Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ°!</b>\n\n"
            f"ğŸ�ƒ Ğ¢Ğ¸Ğ¿: {activity_type}\n"
            f"â�±ï¸� Ğ”Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ: {duration} Ğ¼Ğ¸Ğ½ÑƒÑ‚\n"
            f"ğŸ”¥ Ğ¡Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹: {calories_burned} ĞºĞºĞ°Ğ»\n\n"
            f"ğŸ’ª Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ°Ñ� Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°!",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer("â�Œ Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ Ñ‡Ğ¸Ñ�Ğ»Ğ¾. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·:")
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸: {e}")
        await message.answer(
            "â�Œ ĞŸÑ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ°. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·.",
            reply_markup=get_main_keyboard()
        )

def estimate_calories_burned(activity_type: str, duration: int) -> int:
    """Ğ�Ñ†ĞµĞ½ĞºĞ° Ñ�Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ½Ñ‹Ñ… ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹ Ğ¿Ğ¾ Ñ‚Ğ¸Ğ¿Ñƒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    # Ğ‘Ğ°Ğ·Ğ¾Ğ²Ñ‹Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ� ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹ Ğ² Ñ‡Ğ°Ñ� Ğ´Ğ»Ñ� 70 ĞºĞ³ Ñ‡ĞµĞ»Ğ¾Ğ²ĞµĞºĞ°
    calories_per_hour = {
        'Ğ±ĞµĞ³': 600,
        'Ñ…Ğ¾Ğ´ÑŒĞ±Ğ°': 300,
        'Ğ²ĞµĞ»Ğ¾Ñ�Ğ¸Ğ¿ĞµĞ´': 500,
        'Ğ¿Ğ»Ğ°Ğ²Ğ°Ğ½Ğ¸Ğµ': 400,
        'Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ° Ğ² Ğ·Ğ°Ğ»Ğµ': 450,
        'Ğ¹Ğ¾Ğ³Ğ°': 200,
        'Ğ´Ñ€ÑƒĞ³Ğ¾Ğµ': 350
    }
    
    activity_lower = activity_type.lower()
    
    # Ğ˜Ñ‰ĞµĞ¼ Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ğµ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğµ
    if activity_lower in calories_per_hour:
        base_calories = calories_per_hour[activity_lower]
    else:
        # Ğ˜Ñ‰ĞµĞ¼ Ñ‡Ğ°Ñ�Ñ‚Ğ¸Ñ‡Ğ½Ğ¾Ğµ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğµ
        base_calories = 350  # ĞŸĞ¾ ÑƒĞ¼Ğ¾Ğ»Ñ‡Ğ°Ğ½Ğ¸Ñ�
        for key, value in calories_per_hour.items():
            if key in activity_lower or activity_lower in key:
                base_calories = value
                break
    
    # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ´Ğ»Ñ� ÑƒĞºĞ°Ğ·Ğ°Ğ½Ğ½Ğ¾Ğ¹ Ğ´Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚Ğ¸
    calories_per_minute = base_calories / 60
    return int(calories_per_minute * duration)

@router.message(Command("activity"))
async def cmd_activity(message: Message, state: FSMContext):
    """Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
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
                reply_markup=get_main_keyboard()
            )
            return
        
        # Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�
        from datetime import datetime
        today = message.date
        
        activities_result = await session.execute(
            select(Activity).where(
                Activity.user_id == user.id,
                Activity.datetime >= today
            ).order_by(Activity.datetime.desc())
        )
        activities = activities_result.scalars().all()
        
        if not activities:
            await message.answer(
                "ğŸ�ƒ <b>Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸</b>\n\n"
                "Ğ—Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ� ĞµÑ‰Ğµ Ğ½ĞµÑ‚ Ğ·Ğ°Ğ¿Ğ¸Ñ�ĞµĞ¹ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸.\n\n"
                "Ğ”Ğ»Ñ� Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ñ� Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ /fitness",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            return
        
        # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ
        total_duration = sum(a.duration for a in activities)
        total_calories = sum(a.calories_burned or 0 for a in activities)
        
        message_text = (
            f"ğŸ�ƒ <b>Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�</b>\n\n"
            f"ğŸ“Š Ğ’Ñ�ĞµĞ³Ğ¾ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ĞµĞ¹: {len(activities)}\n"
            f"â�±ï¸� Ğ�Ğ±Ñ‰Ğ°Ñ� Ğ´Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ: {total_duration} Ğ¼Ğ¸Ğ½ÑƒÑ‚\n"
            f"ğŸ”¥ Ğ¡Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹: {total_calories} ĞºĞºĞ°Ğ»\n\n"
            f"ğŸ“‹ <b>ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:</b>\n"
        )
        
        for activity in activities[:5]:  # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ 5
            message_text += (
                f"â€¢ {activity.activity_type} - {activity.duration} Ğ¼Ğ¸Ğ½ ({activity.calories_burned} ĞºĞºĞ°Ğ»)\n"
            )
        
        if len(activities) > 5:
            message_text += f"... Ğ¸ ĞµÑ‰Ğµ {len(activities) - 5} Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ĞµĞ¹"
        
        message_text += f"\n\nĞ”Ğ»Ñ� Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ñ� Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ /fitness"
        
        await message.answer(
            message_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "log_activity")
async def log_activity_callback(callback: CallbackQuery, state: FSMContext):
    """Callback Ğ´Ğ»Ñ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ¸Ğ· Ğ¼ĞµĞ½Ñ�"""
    await callback.answer()
    
    await callback.message.answer(
        "ğŸ�ƒ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ñ„Ğ¸Ñ‚Ğ½ĞµÑ� Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸</b>\n\n"
        "Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ñ‚Ğ¸Ğ¿ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:\n\n"
        "â€¢ Ğ‘ĞµĞ³\n"
        "â€¢ Ğ¥Ğ¾Ğ´ÑŒĞ±Ğ°\n"
        "â€¢ Ğ’ĞµĞ»Ğ¾Ñ�Ğ¸Ğ¿ĞµĞ´\n"
        "â€¢ ĞŸĞ»Ğ°Ğ²Ğ°Ğ½Ğ¸Ğµ\n"
        "â€¢ Ğ¢Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ° Ğ² Ğ·Ğ°Ğ»Ğµ\n"
        "â€¢ Ğ™Ğ¾Ğ³Ğ°\n"
        "â€¢ Ğ”Ñ€ÑƒĞ³Ğ¾Ğµ\n\n"
        "Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:",
        parse_mode="HTML"
    )
    await state.set_state(ActivityStates.waiting_for_activity_type)
