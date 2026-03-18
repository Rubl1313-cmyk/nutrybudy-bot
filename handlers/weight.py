"""
handlers/weight.py
Weight logging handlers
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, WeightEntry
from keyboards.reply_v2 import get_main_keyboard_v2

logger = logging.getLogger(__name__)
router = Router()

class WeightStates(StatesGroup):
    """States for weight logging"""
    waiting_for_weight = State()

@router.message(Command("log_weight"))
async def cmd_log_weight(message: Message, state: FSMContext):
    """Weight logging"""
    await state.clear()
    
    await message.answer(
        "⚖️ <b>Weight logging</b>\n\n"
        "Enter your current weight in kilograms:\n\n"
        "Example: 70.5",
        parse_mode="HTML"
    )
    await state.set_state(WeightStates.waiting_for_weight)

@router.message(WeightStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Process weight logging"""
    try:
        weight = float(message.text.replace(",", "."))
        
        if weight < 30 or weight > 300:
            await message.answer(
                "❌ Weight must be between 30 and 300 kg. Try again:"
            )
            return
        
        # Save to database
        async with get_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await message.answer(
                    "❌ First set up your profile with /set_profile",
                    reply_markup=get_main_keyboard_v2()
                )
                return
            
            # Create weight entry
            weight_entry = WeightEntry(
                user_id=user.id,
                weight=weight,
                datetime=message.date
            )
            
            session.add(weight_entry)
            
            # Update current weight in profile
            user.weight = weight
            
            # Recalculate calorie norms with new weight
            from services.calculator import calculate_calorie_goal, calculate_water_goal
            from utils.activity_normalizer import normalize_activity_level
            
            # Normalize activity level
            normalized_activity = normalize_activity_level(user.activity_level)
            
            nutrition_goals = calculate_calorie_goal(
                weight=weight,
                height=user.height,
                age=user.age,
                gender=user.gender,
                activity_level=normalized_activity,
                goal=user.goal
            )
            
            # Unpack tuple: (calories, protein_g, fat_g, carbs_g)
            user.daily_calorie_goal, user.daily_protein_goal, user.daily_fat_goal, user.daily_carbs_goal = nutrition_goals
            
            # Recalculate water norm with real temperature
            temperature = 20.0  # Default
            try:
                from services.weather import get_temperature
                temperature = await get_temperature(user.city)
            except Exception as e:
                logger.warning(f"Failed to get temperature for {user.city}: {e}")
                temperature = 20.0
                
            water_goal = calculate_water_goal(
                weight=weight,
                activity_level=normalized_activity,
                temperature=temperature,  # Real temperature
                goal=user.goal,  # Add goal for water calculation
                gender=user.gender  # Add gender for water calculation
            )
            user.daily_water_goal = water_goal
            
            await session.commit()
            
            # Get statistics
            await send_weight_statistics(message, user, session, weight)
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Enter a valid number. Try again:")
    except Exception as e:
        logger.error(f"Error logging weight: {e}")
        await message.answer(
            "❌ An error occurred. Try again.",
            reply_markup=get_main_keyboard_v2()
        )

async def send_weight_statistics(message: Message, user, session, current_weight):
    """Send weight statistics"""
    from datetime import datetime, timedelta
    from utils.timezone_utils import get_user_local_date
    
    # Use user's local date
    today_local = get_user_local_date(user)
    
    # Yesterday (in user's local time)
    yesterday = today_local - timedelta(days=1)
    yesterday_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            func.date(WeightEntry.datetime) == yesterday
        )
    )
    yesterday_weight = yesterday_result.scalar_one_or_none()
    
    # Week ago (in user's local time)
    week_ago = today_local - timedelta(days=7)
    week_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            func.date(WeightEntry.datetime) == week_ago
        )
    )
    week_weight = week_result.scalar_one_or_none()
    
    # Month ago (in user's local time)
    month_ago = today_local - timedelta(days=30)
    month_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            func.date(WeightEntry.datetime) == month_ago
        )
    )
    month_weight = month_result.scalar_one_or_none()
    
    # Minimum and maximum for last 30 days (in user's local time)
    thirty_days_ago = today_local - timedelta(days=30)
    min_max_result = await session.execute(
        select(
            func.min(WeightEntry.weight),
            func.max(WeightEntry.weight)
        ).where(
            WeightEntry.user_id == user.id,
            WeightEntry.datetime >= thirty_days_ago
        )
    )
    min_weight, max_weight = min_max_result.first()
    
    # Form message
    message_text = f"✅ <b>Weight logged!</b>\n\n"
    message_text += f"⚖️ Current weight: {current_weight:.1f} kg\n\n"
    message_text += f"📊 <b>Changes:</b>\n"
    
    if yesterday_weight:
        daily_change = current_weight - yesterday_weight
        emoji = "📈" if daily_change > 0 else "📉" if daily_change < 0 else "⚡️"
        message_text += f"{emoji} Daily: {daily_change:+.1f} kg\n"
    
    if week_weight:
        week_change = current_weight - week_weight
        emoji = "📈" if week_change > 0 else "📉" if week_change < 0 else "⚡️"
        message_text += f"{emoji} Weekly: {week_change:+.1f} kg\n"
    
    if month_weight:
        month_change = current_weight - month_weight
        emoji = "📈" if month_change > 0 else "📉" if month_change < 0 else "⚡️"
        message_text += f"{emoji} Monthly: {month_change:+.1f} kg\n"
    
    if min_weight and max_weight:
        message_text += f"\n📈 <b>Last 30 days:</b>\n"
        message_text += f"🔻 Minimum: {min_weight:.1f} kg\n"
        message_text += f"🔺 Maximum: {max_weight:.1f} kg\n"
        message_text += f"📊 Range: {max_weight - min_weight:.1f} kg\n"
    
    # Motivation
    if user.goal == "lose_weight":
        if week_weight and current_weight < week_weight:
            message_text += f"\n🎉 Excellent! Weight is decreasing!"
        else:
            message_text += f"\n💪 Keep going in the same spirit!"
    elif user.goal == "gain_weight":
        if week_weight and current_weight > week_weight:
            message_text += f"\n🎉 Excellent! Weight is increasing!"
        else:
            message_text += f"\n💪 Keep working!"
    else:
        message_text += f"\n⚖️ Weight is stable!"
    
    await message.answer(
        message_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("weight"))
async def cmd_weight(message: Message, state: FSMContext):
    """Weight statistics"""
    await state.clear()
    
    async with get_session() as session:
        # Get user
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ First set up your profile with /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Get last weight entries
        from datetime import datetime, timedelta
        thirty_days_ago = message.date - timedelta(days=30)
        
        weight_result = await session.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user.id,
                WeightEntry.datetime >= thirty_days_ago
            ).order_by(WeightEntry.datetime.desc())
        )
        weight_entries = weight_result.scalars().all()
        
        if not weight_entries:
            await message.answer(
                "⚖️ <b>Weight statistics</b>\n\n"
                "You don't have any weight entries yet.\n\n"
                "To add weight use /log_weight",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            return
        
        # Current weight
        current_weight = weight_entries[0].weight
        
        # Statistics
        message_text = f"⚖️ <b>Weight statistics</b>\n\n"
        message_text += f"📊 Current weight: {current_weight:.1f} kg\n"
        message_text += f"📅 Entries for 30 days: {len(weight_entries)}\n\n"
        
        # Last 7 entries
        message_text += f"📋 <b>Last entries:</b>\n"
        for entry in weight_entries[:7]:
            date_str = entry.datetime.strftime("%d.%m")
            message_text += f"• {date_str}: {entry.weight:.1f} kg\n"
        
        await message.answer(
            message_text,
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "log_weight")
async def log_weight_callback(callback: CallbackQuery, state: FSMContext):
    """Callback for weight logging from menu"""
    await callback.answer()
    
    await callback.message.answer(
        "⚖️ <b>Weight logging</b>\n\n"
        "Enter your current weight in kilograms:\n\n"
        "Example: 70.5",
        parse_mode="HTML"
    )
    await state.set_state(WeightStates.waiting_for_weight)
