"""
handlers/meal_plan.py
ĞŸĞ»Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from sqlalchemy import select

from database.db import get_session
from database.models import User
from services.cloudflare_manager import cf_manager
from keyboards.reply_v2 import get_main_keyboard_v2

logger = logging.getLogger(__name__)
router = Router()

class MealPlanStates(StatesGroup):
    """Ğ¡Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ¿Ğ»Ğ°Ğ½Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ� Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"""
    waiting_for_preferences = State()
    waiting_for_restrictions = State()

@router.message(Command("meal_plan"))
async def cmd_meal_plan(message: Message, state: FSMContext):
    """ĞŸĞ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚ÑŒ Ğ¿Ğ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"""
    await state.clear()
    
    await message.answer(
        "ğŸ�½ï¸� <b>ĞŸĞ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�</b>\n\n"
        "Ğ¯ Ñ�Ğ¾Ñ�Ñ‚Ğ°Ğ²Ğ»Ñ� Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¿Ğ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ½Ğ° Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğµ Ğ²Ğ°ÑˆĞ¸Ñ… Ñ†ĞµĞ»ĞµĞ¹ Ğ¸ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ğ¹.\n\n"
        "ğŸ“‹ <b>Ğ’Ğ°ÑˆĞ¸ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ñ�:</b>\n"
        "â€¢ Ğ”Ğ¸ĞµÑ‚Ğ° (Ğ²ĞµĞ³ĞµÑ‚Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ�ĞºĞ°Ñ�, Ğ±ĞµĞ·Ğ³Ğ»Ñ�Ñ‚ĞµĞ½Ğ¾Ğ²Ğ°Ñ� Ğ¸ Ñ‚.Ğ´.)\n"
        "â€¢ Ğ�Ğ»Ğ»ĞµÑ€Ğ³Ğ¸Ğ¸ Ğ¸ Ğ½ĞµĞ¿ĞµÑ€ĞµĞ½Ğ¾Ñ�Ğ¸Ğ¼Ğ¾Ñ�Ñ‚Ğ¸\n"
        "â€¢ Ğ›Ñ�Ğ±Ğ¸Ğ¼Ñ‹Ğµ/Ğ½ĞµĞ»Ñ�Ğ±Ğ¸Ğ¼Ñ‹Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹\n"
        "â€¢ ĞšĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ¾Ğ² Ğ¿Ğ¸Ñ‰Ğ¸ Ğ² Ğ´ĞµĞ½ÑŒ\n\n"
        "Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ²Ğ°ÑˆĞ¸ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ñ� Ğ¸Ğ»Ğ¸ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²ÑŒÑ‚Ğµ 0 ĞµÑ�Ğ»Ğ¸ Ğ½ĞµÑ‚ Ğ¾Ñ�Ğ¾Ğ±Ñ‹Ñ… Ñ‚Ñ€ĞµĞ±Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğ¹:",
        parse_mode="HTML"
    )
    await state.set_state(MealPlanStates.waiting_for_preferences)

@router.message(MealPlanStates.waiting_for_preferences)
async def process_preferences(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¿Ñ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ğ¹"""
    preferences = message.text.strip()
    
    if preferences == "0":
        preferences = "Ğ�ĞµÑ‚ Ğ¾Ñ�Ğ¾Ğ±Ñ‹Ñ… Ğ¿Ñ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ğ¹"
    
    await state.update_data(preferences=preferences)
    
    await message.answer(
        "ğŸš« <b>Ğ�Ğ³Ñ€Ğ°Ğ½Ğ¸Ñ‡ĞµĞ½Ğ¸Ñ� Ğ¸ Ğ°Ğ»Ğ»ĞµÑ€Ğ³Ğ¸Ğ¸:</b>\n\n"
        "Ğ£ĞºĞ°Ğ¶Ğ¸Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹, ĞºĞ¾Ñ‚Ğ¾Ñ€Ñ‹Ğµ Ğ½ÑƒĞ¶Ğ½Ğ¾ Ğ¸Ñ�ĞºĞ»Ñ�Ñ‡Ğ¸Ñ‚ÑŒ:\n\n"
        "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:\n"
        "â€¢ Ğ�Ñ€ĞµÑ…Ğ¸, Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾, Ñ�Ğ¹Ñ†Ğ°\n"
        "â€¢ Ğ“Ğ»Ñ�Ñ‚ĞµĞ½, Ğ»Ğ°ĞºÑ‚Ğ¾Ğ·Ğ°\n"
        "â€¢ Ğ�Ñ�Ñ‚Ñ€Ğ¾Ğµ, Ğ¶Ğ¸Ñ€Ğ½Ğ¾Ğµ\n\n"
        "Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²ÑŒÑ‚Ğµ 0 ĞµÑ�Ğ»Ğ¸ Ğ½ĞµÑ‚ Ğ¾Ğ³Ñ€Ğ°Ğ½Ğ¸Ñ‡ĞµĞ½Ğ¸Ğ¹:",
        parse_mode="HTML"
    )
    await state.set_state(MealPlanStates.waiting_for_restrictions)

@router.message(MealPlanStates.waiting_for_restrictions)
async def process_restrictions(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ¾Ğ³Ñ€Ğ°Ğ½Ğ¸Ñ‡ĞµĞ½Ğ¸Ğ¹ Ğ¸ Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ½Ğ¸Ğµ Ğ¿Ğ»Ğ°Ğ½Ğ°"""
    restrictions = message.text.strip()
    
    if restrictions == "0":
        restrictions = "Ğ�ĞµÑ‚ Ğ¾Ğ³Ñ€Ğ°Ğ½Ğ¸Ñ‡ĞµĞ½Ğ¸Ğ¹"
    
    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
    async with get_session() as session:
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
        
        # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ´Ğ»Ñ� AI
        user_profile = {
            'name': user.first_name or 'Anonymous',
            'weight': user.weight,
            'height': user.height,
            'age': user.age,
            'gender': user.gender,
            'goal': user.goal,
            'daily_calories': user.daily_calorie_goal,
            'daily_protein': user.daily_protein_goal,
            'daily_fat': user.daily_fat_goal,
            'daily_carbs': user.daily_carbs_goal,
            'city': user.city
        }
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ñ�
        meal_data = await state.get_data()
        preferences = meal_data['preferences']
        
        # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğº AI
        ai_query = f"""
        Ğ¡Ğ¾Ñ�Ñ‚Ğ°Ğ²ÑŒ Ğ´ĞµÑ‚Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¿Ğ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ½Ğ° Ğ¾Ğ´Ğ¸Ğ½ Ğ´ĞµĞ½ÑŒ.
        
        Ğ¦ĞµĞ»ÑŒ: {user.goal}
        ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹Ğ½Ğ¾Ñ�Ñ‚ÑŒ: {user.daily_calorie_goal} ĞºĞºĞ°Ğ»
        Ğ‘Ğ–Ğ£: Ğ‘{user.daily_protein_goal}Ğ³ Ğ–{user.daily_fat_goal}Ğ³ Ğ£{user.daily_carbs_goal}Ğ³
        
        ĞŸÑ€ĞµĞ´Ğ¿Ğ¾Ñ‡Ñ‚ĞµĞ½Ğ¸Ñ�: {preferences}
        Ğ�Ğ³Ñ€Ğ°Ğ½Ğ¸Ñ‡ĞµĞ½Ğ¸Ñ�: {restrictions}
        
        Ğ’ĞºĞ»Ñ�Ñ‡Ğ¸:
        1. Ğ—Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº, Ğ¾Ğ±ĞµĞ´, ÑƒĞ¶Ğ¸Ğ½ + 1-2 Ğ¿ĞµÑ€ĞµĞºÑƒÑ�Ğ°
        2. Ğ¢Ğ¾Ñ‡Ğ½Ğ¾Ğµ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ ĞºĞ°Ğ¶Ğ´Ğ¾Ğ³Ğ¾ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ° Ğ² Ğ³Ñ€Ğ°Ğ¼Ğ¼Ğ°Ñ…
        3. ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ Ğ¸ Ğ‘Ğ–Ğ£ Ğ´Ğ»Ñ� ĞºĞ°Ğ¶Ğ´Ğ¾Ğ³Ğ¾ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸
        4. ĞŸÑ€Ğ¾Ñ�Ñ‚Ñ‹Ğµ Ñ€ĞµÑ†ĞµĞ¿Ñ‚Ñ‹ Ğ¿Ñ€Ğ¸Ğ³Ğ¾Ñ‚Ğ¾Ğ²Ğ»ĞµĞ½Ğ¸Ñ�
        5. Ğ ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´Ğ°Ñ†Ğ¸Ğ¸ Ğ¿Ğ¾ Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ¸ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ°
        
        Ğ¤Ğ¾Ñ€Ğ¼Ğ°Ñ‚: Ñ‡ĞµÑ‚ĞºĞ°Ñ� Ñ�Ñ‚Ñ€ÑƒĞºÑ‚ÑƒÑ€Ğ° Ñ� Ğ·Ğ°Ğ³Ğ¾Ğ»Ğ¾Ğ²ĞºĞ°Ğ¼Ğ¸ Ğ´Ğ»Ñ� ĞºĞ°Ğ¶Ğ´Ğ¾Ğ³Ğ¾ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸
        """
        
        try:
            # Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ "Ğ¿ĞµÑ‡Ğ°Ñ‚Ğ°ĞµÑ‚..."
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            # Ğ—Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğº AI Ñ� Ğ¿Ñ€Ğ°Ğ²Ğ¸Ğ»ÑŒĞ½Ñ‹Ğ¼Ğ¸ Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€Ğ°Ğ¼Ğ¸
            response_dict = await cf_manager.ai_assistant(
                message=ai_query,
                history=[],
                user_profile=user_profile
            )
            
            response = response_dict.get('response', 'Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ�Ğ¾Ğ·Ğ´Ğ°Ñ‚ÑŒ Ğ¿Ğ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�')
            
            await state.clear()
            
            await message.answer(
                f"ğŸ�½ï¸� <b>Ğ’Ğ°Ñˆ Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¿Ğ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�</b>\n\n{response}\n\n"
                f"ğŸ’¡ <b>Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ğ¸Ñ‚Ğµ Ñ�Ñ‚Ğ¾Ñ‚ Ğ¿Ğ»Ğ°Ğ½ Ğ¸ Ñ�Ğ»ĞµĞ´ÑƒĞ¹Ñ‚Ğµ ĞµĞ¼Ñƒ!</b>\n\n"
                f"Ğ”Ğ»Ñ� Ğ½Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ğ¿Ğ»Ğ°Ğ½Ğ° Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ /meal_plan",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ½Ğ¸Ğ¸ Ğ¿Ğ»Ğ°Ğ½Ğ° Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�: {e}")
            await message.answer(
                "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ�Ğ¾Ğ·Ğ´Ğ°Ñ‚ÑŒ Ğ¿Ğ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¿Ğ¾Ğ·Ğ¶Ğµ.",
                reply_markup=get_main_keyboard_v2()
            )

@router.message(Command("diet"))
async def cmd_diet(message: Message, state: FSMContext):
    """Ğ�Ğ»ÑŒÑ‚ĞµÑ€Ğ½Ğ°Ñ‚Ğ¸Ğ²Ğ½Ğ°Ñ� ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ° Ğ´Ğ»Ñ� Ğ¿Ğ»Ğ°Ğ½Ğ° Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"""
    await cmd_meal_plan(message, state)

@router.message(Command("nutrition"))
async def cmd_nutrition(message: Message, state: FSMContext):
    """Ğ¡Ğ¾Ğ²ĞµÑ‚Ñ‹ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"""
    await state.clear()
    
    try:
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¸Ğ½Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ†Ğ¸Ñ� Ğ¾ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ğµ
        async with get_session() as session:
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
            
            # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ´Ğ»Ñ� AI
            user_profile = {
                'name': user.first_name or 'Anonymous',
                'weight': user.weight,
                'height': user.height,
                'age': user.age,
                'gender': user.gender,
                'goal': user.goal,
                'daily_calories': user.daily_calorie_goal,
                'daily_protein': user.daily_protein_goal,
                'daily_fat': user.daily_fat_goal,
                'daily_carbs': user.daily_carbs_goal,
                'city': user.city
            }
            
            # Ğ—Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğº AI
            ai_query = f"""
            Ğ”Ğ°Ğ¹ Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğµ Ñ€ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´Ğ°Ñ†Ğ¸Ğ¸ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ´Ğ»Ñ� Ñ†ĞµĞ»Ğ¸: {user.goal}
            
            Ğ’ĞºĞ»Ñ�Ñ‡Ğ¸:
            1. Ğ�Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ğµ Ğ¿Ñ€Ğ¸Ğ½Ñ†Ğ¸Ğ¿Ñ‹ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�
            2. Ğ ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´ÑƒĞµĞ¼Ñ‹Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹
            3. ĞŸÑ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹ ĞºĞ¾Ñ‚Ğ¾Ñ€Ñ‹Ñ… Ñ�Ñ‚Ğ¾Ğ¸Ñ‚ Ğ¸Ğ·Ğ±ĞµĞ³Ğ°Ñ‚ÑŒ
            4. Ğ’Ñ€ĞµĞ¼Ñ� Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸
            5. Ğ’Ğ¾Ğ´Ğ½Ñ‹Ğ¹ Ğ±Ğ°Ğ»Ğ°Ğ½Ñ�
            6. Ğ”Ğ¾Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ñ�Ğ¾Ğ²ĞµÑ‚Ñ‹
            
            Ğ‘ÑƒĞ´ÑŒ ĞºÑ€Ğ°Ñ‚ĞºĞ¸Ğ¼, Ğ½Ğ¾ Ğ¸Ğ½Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ¸Ğ²Ğ½Ñ‹Ğ¼.
            """
            
            # Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ "Ğ¿ĞµÑ‡Ğ°Ñ‚Ğ°ĞµÑ‚..."
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            # Ğ—Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğº AI Ñ� Ğ¿Ñ€Ğ°Ğ²Ğ¸Ğ»ÑŒĞ½Ñ‹Ğ¼Ğ¸ Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€Ğ°Ğ¼Ğ¸
            response_dict = await cf_manager.ai_assistant(
                message=ai_query,
                history=[],
                user_profile=user_profile
            )
            
            response = response_dict.get('response', 'Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚ÑŒ Ñ€ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´Ğ°Ñ†Ğ¸Ğ¸')
            
            await message.answer(
                f"ğŸ¥— <b>Ğ ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´Ğ°Ñ†Ğ¸Ğ¸ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�</b>\n\n{response}",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ¿Ğ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğ¸ Ñ€ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´Ğ°Ñ†Ğ¸Ğ¹: {e}")
        await message.answer(
            "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚ÑŒ Ñ€ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´Ğ°Ñ†Ğ¸Ğ¸. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¿Ğ¾Ğ·Ğ¶Ğµ.",
            reply_markup=get_main_keyboard_v2()
        )

@router.callback_query(F.data == "meal_plan")
async def meal_plan_callback(callback: CallbackQuery, state: FSMContext):
    """Callback Ğ´Ğ»Ñ� Ğ¿Ğ»Ğ°Ğ½Ğ° Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ¸Ğ· Ğ¼ĞµĞ½Ñ�"""
    await callback.answer()
    await cmd_meal_plan(callback.message, state)

@router.callback_query(F.data == "nutrition_tips")
async def nutrition_tips_callback(callback: CallbackQuery, state: FSMContext):
    """Callback Ğ´Ğ»Ñ� Ñ�Ğ¾Ğ²ĞµÑ‚Ğ¾Ğ² Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ¸Ğ· Ğ¼ĞµĞ½Ñ�"""
    await callback.answer()
    await cmd_nutrition(callback.message, state)
