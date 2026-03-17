"""
handlers/weight.py
Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ°
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
    """Ğ¡Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ°"""
    waiting_for_weight = State()

@router.message(Command("log_weight"))
async def cmd_log_weight(message: Message, state: FSMContext):
    """Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ²ĞµÑ�Ğ°"""
    await state.clear()
    
    await message.answer(
        "âš–ï¸� <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ²ĞµÑ�Ğ°</b>\n\n"
        "Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ²Ğ°Ñˆ Ñ‚ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ� Ğ² ĞºĞ¸Ğ»Ğ¾Ğ³Ñ€Ğ°Ğ¼Ğ¼Ğ°Ñ…:\n\n"
        "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: 70.5",
        parse_mode="HTML"
    )
    await state.set_state(WeightStates.waiting_for_weight)

@router.message(WeightStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ°"""
    try:
        weight = float(message.text.replace(",", "."))
        
        if weight < 30 or weight > 300:
            await message.answer(
                "â�Œ Ğ’ĞµÑ� Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ¾Ñ‚ 30 Ğ´Ğ¾ 300 ĞºĞ³. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·:"
            )
            return
        
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
                    reply_markup=get_main_keyboard_v2()
                )
                return
            
            # Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ğ·Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ¾ Ğ²ĞµÑ�Ğµ
            weight_entry = WeightEntry(
                user_id=user.id,
                weight=weight,
                datetime=message.date
            )
            
            session.add(weight_entry)
            
            # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ñ‚ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ� Ğ² Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ğµ
            user.weight = weight
            
            # ĞŸĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ½Ğ¾Ñ€Ğ¼Ñ‹ ĞšĞ‘Ğ–Ğ£ Ñ� Ğ½Ğ¾Ğ²Ñ‹Ğ¼ Ğ²ĞµÑ�Ğ¾Ğ¼
            from services.calculator import calculate_calorie_goal, calculate_water_goal
            from utils.activity_normalizer import normalize_activity_level
            
            # Ğ�Ğ¾Ñ€Ğ¼Ğ°Ğ»Ğ¸Ğ·ÑƒĞµĞ¼ ÑƒÑ€Ğ¾Ğ²ĞµĞ½ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
            normalized_activity = normalize_activity_level(user.activity_level)
            
            nutrition_goals = calculate_calorie_goal(
                weight=weight,
                height=user.height,
                age=user.age,
                gender=user.gender,
                activity_level=normalized_activity,
                goal=user.goal
            )
            
            # Ğ Ğ°Ñ�Ğ¿Ğ°ĞºĞ¾Ğ²Ñ‹Ğ²Ğ°ĞµĞ¼ ĞºĞ¾Ñ€Ñ‚ĞµĞ¶: (calories, protein_g, fat_g, carbs_g)
            user.daily_calorie_goal, user.daily_protein_goal, user.daily_fat_goal, user.daily_carbs_goal = nutrition_goals
            
            # ĞŸĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ½Ğ¾Ñ€Ğ¼Ñƒ Ğ²Ğ¾Ğ´Ñ‹ Ñ� Ñ€ĞµĞ°Ğ»ÑŒĞ½Ğ¾Ğ¹ Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ğ¾Ğ¹
            temperature = 20.0  # ĞŸĞ¾ ÑƒĞ¼Ğ¾Ğ»Ñ‡Ğ°Ğ½Ğ¸Ñ�
            try:
                from services.weather import get_temperature
                temperature = await get_temperature(user.city)
            except Exception as e:
                logger.warning(f"Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚ÑŒ Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ñƒ Ğ´Ğ»Ñ� {user.city}: {e}")
                temperature = 20.0
                
            water_goal = calculate_water_goal(
                weight=weight,
                activity_level=normalized_activity,
                temperature=temperature,  # Ğ ĞµĞ°Ğ»ÑŒĞ½Ğ°Ñ� Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ğ°
                goal=user.goal,  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ñ†ĞµĞ»ÑŒ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
                gender=user.gender  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¿Ğ¾Ğ» Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
            )
            user.daily_water_goal = water_goal
            
            await session.commit()
            
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ
            await send_weight_statistics(message, user, session, weight)
        
        await state.clear()
        
    except ValueError:
        await message.answer("â�Œ Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğµ Ñ‡Ğ¸Ñ�Ğ»Ğ¾. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·:")
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ°: {e}")
        await message.answer(
            "â�Œ ĞŸÑ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ°. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·.",
            reply_markup=get_main_keyboard_v2()
        )

async def send_weight_statistics(message: Message, user, session, current_weight):
    """Отправляет статистику по весу"""
    from datetime import datetime, timedelta
    from utils.timezone_utils import get_user_local_date
    
    # Используем локальную дату пользователя
    today_local = get_user_local_date(user)
    
    # Вчера (в локальном времени пользователя)
    yesterday = today_local - timedelta(days=1)
    yesterday_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            func.date(WeightEntry.datetime) == yesterday
        )
    )
    yesterday_weight = yesterday_result.scalar_one_or_none()
    
    # Неделю назад (в локальном времени пользователя)
    week_ago = today_local - timedelta(days=7)
    week_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            func.date(WeightEntry.datetime) == week_ago
        )
    )
    week_weight = week_result.scalar_one_or_none()
    
    # Месяц назад (в локальном времени пользователя)
    month_ago = today_local - timedelta(days=30)
    month_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            func.date(WeightEntry.datetime) == month_ago
        )
    )
    month_weight = month_result.scalar_one_or_none()
    
    # Минимальный и максимальный за последние 30 дней (в локальном времени пользователя)
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
    
    # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ
    message_text = f"âœ… <b>Ğ’ĞµÑ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½!</b>\n\n"
    message_text += f"âš–ï¸� Ğ¢ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ�: {current_weight:.1f} ĞºĞ³\n\n"
    message_text += f"ğŸ“Š <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ñ�:</b>\n"
    
    if yesterday_weight:
        daily_change = current_weight - yesterday_weight
        emoji = "ğŸ“ˆ" if daily_change > 0 else "ğŸ“‰" if daily_change < 0 else "â�¡ï¸�"
        message_text += f"{emoji} Ğ—Ğ° Ğ´ĞµĞ½ÑŒ: {daily_change:+.1f} ĞºĞ³\n"
    
    if week_weight:
        week_change = current_weight - week_weight
        emoji = "ğŸ“ˆ" if week_change > 0 else "ğŸ“‰" if week_change < 0 else "â�¡ï¸�"
        message_text += f"{emoji} Ğ—Ğ° Ğ½ĞµĞ´ĞµĞ»Ñ�: {week_change:+.1f} ĞºĞ³\n"
    
    if month_weight:
        month_change = current_weight - month_weight
        emoji = "ğŸ“ˆ" if month_change > 0 else "ğŸ“‰" if month_change < 0 else "â�¡ï¸�"
        message_text += f"{emoji} Ğ—Ğ° Ğ¼ĞµÑ�Ñ�Ñ†: {month_change:+.1f} ĞºĞ³\n"
    
    if min_weight and max_weight:
        message_text += f"\nğŸ“� <b>Ğ—Ğ° Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ 30 Ğ´Ğ½ĞµĞ¹:</b>\n"
        message_text += f"ğŸ”» ĞœĞ¸Ğ½Ğ¸Ğ¼ÑƒĞ¼: {min_weight:.1f} ĞºĞ³\n"
        message_text += f"ğŸ”º ĞœĞ°ĞºÑ�Ğ¸Ğ¼ÑƒĞ¼: {max_weight:.1f} ĞºĞ³\n"
        message_text += f"ğŸ“Š Ğ Ğ°Ğ·Ğ¼Ğ°Ñ…: {max_weight - min_weight:.1f} ĞºĞ³\n"
    
    # ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ�
    if user.goal == "lose_weight":
        if week_weight and current_weight < week_weight:
            message_text += f"\nğŸ�‰ Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾! Ğ’ĞµÑ� Ñ�Ğ½Ğ¸Ğ¶Ğ°ĞµÑ‚Ñ�Ñ�!"
        else:
            message_text += f"\nğŸ’ª ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ² Ñ‚Ğ¾Ğ¼ Ğ¶Ğµ Ğ´ÑƒÑ…Ğµ!"
    elif user.goal == "gain_weight":
        if week_weight and current_weight > week_weight:
            message_text += f"\nğŸ�‰ Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾! Ğ’ĞµÑ� Ñ€Ğ°Ñ�Ñ‚ĞµÑ‚!"
        else:
            message_text += f"\nğŸ’ª ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°Ñ‚ÑŒ!"
    else:
        message_text += f"\nâš–ï¸� Ğ’ĞµÑ� Ñ�Ñ‚Ğ°Ğ±Ğ¸Ğ»ĞµĞ½!"
    
    await message.answer(
        message_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("weight"))
async def cmd_weight(message: Message, state: FSMContext):
    """Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ²ĞµÑ�Ğ°"""
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
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ°
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
                "âš–ï¸� <b>Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ²ĞµÑ�Ğ°</b>\n\n"
                "Ğ£ Ğ²Ğ°Ñ� ĞµÑ‰Ğµ Ğ½ĞµÑ‚ Ğ·Ğ°Ğ¿Ğ¸Ñ�ĞµĞ¹ Ğ²ĞµÑ�Ğ°.\n\n"
                "Ğ”Ğ»Ñ� Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ¸Ñ� Ğ²ĞµÑ�Ğ° Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ /log_weight",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            return
        
        # Ğ¢ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ�
        current_weight = weight_entries[0].weight
        
        # Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ°
        message_text = f"âš–ï¸� <b>Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ²ĞµÑ�Ğ°</b>\n\n"
        message_text += f"ğŸ“Š Ğ¢ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ�: {current_weight:.1f} ĞºĞ³\n"
        message_text += f"ğŸ“… Ğ—Ğ°Ğ¿Ğ¸Ñ�ĞµĞ¹ Ğ·Ğ° 30 Ğ´Ğ½ĞµĞ¹: {len(weight_entries)}\n\n"
        
        # ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ 7 Ğ·Ğ°Ğ¿Ğ¸Ñ�ĞµĞ¹
        message_text += f"ğŸ“‹ <b>ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸:</b>\n"
        for entry in weight_entries[:7]:
            date_str = entry.datetime.strftime("%d.%m")
            message_text += f"â€¢ {date_str}: {entry.weight:.1f} ĞºĞ³\n"
        
        await message.answer(
            message_text,
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "log_weight")
async def log_weight_callback(callback: CallbackQuery, state: FSMContext):
    """Callback Ğ´Ğ»Ñ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ° Ğ¸Ğ· Ğ¼ĞµĞ½Ñ�"""
    await callback.answer()
    
    await callback.message.answer(
        "âš–ï¸� <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ²ĞµÑ�Ğ°</b>\n\n"
        "Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ²Ğ°Ñˆ Ñ‚ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ� Ğ² ĞºĞ¸Ğ»Ğ¾Ğ³Ñ€Ğ°Ğ¼Ğ¼Ğ°Ñ…:\n\n"
        "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: 70.5",
        parse_mode="HTML"
    )
    await state.set_state(WeightStates.waiting_for_weight)
