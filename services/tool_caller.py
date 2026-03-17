"""
services/tool_caller.py
Ğ”Ğ¸Ñ�Ğ¿ĞµÑ‚Ñ‡ĞµÑ€ Ğ²Ñ‹Ğ·Ğ¾Ğ²Ğ° Ğ¸Ğ½Ñ�Ñ‚Ñ€ÑƒĞ¼ĞµĞ½Ñ‚Ğ¾Ğ² Ğ½Ğ° Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğµ ĞºĞ»Ğ°Ñ�Ñ�Ğ¸Ñ„Ğ¸Ñ†Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ½Ğ°Ğ¼ĞµÑ€ĞµĞ½Ğ¸Ğ¹
"""
import logging
from typing import Dict, Any, Optional
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

class ToolCaller:
    """Ğ’Ñ‹Ğ·Ñ‹Ğ²Ğ°ĞµÑ‚ Ñ�Ğ¾Ğ¾Ñ‚Ğ²ĞµÑ‚Ñ�Ñ‚Ğ²ÑƒÑ�Ñ‰Ğ¸Ğµ Ğ¸Ğ½Ñ�Ñ‚Ñ€ÑƒĞ¼ĞµĞ½Ñ‚Ñ‹ Ğ½Ğ° Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğµ Ğ½Ğ°Ğ¼ĞµÑ€ĞµĞ½Ğ¸Ğ¹ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
    
    @staticmethod
    async def call(intent: str, text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """
        Ğ’Ñ‹Ğ·Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ½ÑƒĞ¶Ğ½Ñ‹Ğ¹ Ğ¸Ğ½Ñ�Ñ‚Ñ€ÑƒĞ¼ĞµĞ½Ñ‚ Ğ¿Ğ¾ Ğ½Ğ°Ğ¼ĞµÑ€ĞµĞ½Ğ¸Ñ�
        
        Args:
            intent: Ğ�Ğ°Ğ¼ĞµÑ€ĞµĞ½Ğ¸Ğµ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            text: Ğ˜Ñ�Ñ…Ğ¾Ğ´Ğ½Ñ‹Ğ¹ Ñ‚ĞµĞºÑ�Ñ‚ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ�
            user_id: ID Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
            message: Ğ�Ğ±ÑŠĞµĞºÑ‚ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ�
            state: FSM Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ğµ
            
        Returns:
            bool: Ğ£Ñ�Ğ¿ĞµÑˆĞ½Ğ¾Ñ�Ñ‚ÑŒ Ğ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ¸Ñ�
        """
        try:
            logger.info(f"Calling tool for intent: {intent}")
            
            if intent == "log_food":
                return await ToolCaller.handle_log_food(text, user_id, message, state)
            
            elif intent == "log_drink":
                return await ToolCaller.handle_log_drink(text, user_id, message, state)
            
            elif intent == "log_water":
                return await ToolCaller.handle_log_water(text, user_id, message, state)
            
            elif intent == "log_weight":
                return await ToolCaller.handle_log_weight(text, user_id, message, state)
            
            elif intent == "log_activity":
                return await ToolCaller.handle_log_activity(text, user_id, message, state)
            
            elif intent == "show_progress":
                return await ToolCaller.handle_show_progress(text, user_id, message, state)
            
            elif intent == "ask_ai":
                return await ToolCaller.handle_ask_ai(text, user_id, message, state)
            
            elif intent == "help":
                return await ToolCaller.handle_help(text, user_id, message, state)
            
            else:
                logger.warning(f"Unknown intent: {intent}")
                await message.answer("ğŸ¤” Ğ¯ Ğ½Ğµ Ñ�Ğ¾Ğ²Ñ�ĞµĞ¼ Ğ¿Ğ¾Ğ½Ñ�Ğ». ĞœĞ¾Ğ¶ĞµÑ‚Ğµ Ğ¿ĞµÑ€ĞµÑ„Ñ€Ğ°Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒ?")
                return False
                
        except Exception as e:
            logger.error(f"Error in tool caller for intent {intent}: {e}")
            await message.answer("â�Œ ĞŸÑ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ°. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·.")
            return False
    
    @staticmethod
    async def handle_log_food(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ ĞµĞ´Ñ‹"""
        try:
            # Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Ñ�ÑƒÑ‰ĞµÑ�Ñ‚Ğ²ÑƒÑ�Ñ‰Ğ¸Ğ¹ AI Ğ¿Ñ€Ğ¾Ñ†ĞµÑ�Ñ�Ğ¾Ñ€ Ğ´Ğ»Ñ� Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ° ĞµĞ´Ñ‹
            from services.ai_processor import ai_processor
            
            result = await ai_processor.process_text_input(text, user_id)
            
            if result.get("success"):
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ‡ĞµÑ€ĞµĞ· food_save_service
                from services.food_save_service import food_save_service
                from utils.ui_templates import meal_card
                
                food_items = result["parameters"].get("food_items", [])
                meal_type = result["parameters"].get("meal_type", "main")
                
                save_result = await food_save_service.save_food_to_db(
                    user_id, 
                    food_items, 
                    meal_type
                )
                
                if save_result.get("success"):
                    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ¸ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºÑƒ
                    from utils.daily_stats import get_daily_stats
                    from database.db import get_session
                    from database.models import User
                    from sqlalchemy import select
                    
                    async with get_session() as session:
                        user_result = await session.execute(
                            select(User).where(User.telegram_id == user_id)
                        )
                        user = user_result.scalar_one_or_none()
                    
                    daily_stats = await get_daily_stats(user_id)
                    
                    # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¸Ğµ Ğ¸Ğ· Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ¾Ğ²
                    description_from_items = ", ".join([
                        f"{item.get('quantity','')} {item.get('unit','Ğ³')} {item['name']}" 
                        for item in food_items
                    ])
                    
                    # Ğ¤Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ´Ğ»Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ¸
                    food_data = {
                        'description': description_from_items,
                        'total_calories': save_result.get('total_calories', 0),
                        'total_protein': save_result.get('total_protein', 0),
                        'total_fat': save_result.get('total_fat', 0),
                        'total_carbs': save_result.get('total_carbs', 0),
                        'meal_type': meal_type
                    }
                    
                    await message.answer(
                        meal_card(food_data, user, daily_stats),
                        parse_mode="HTML"
                    )
                else:
                    await message.answer(
                        f"â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�: {save_result.get('error', 'Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ°Ñ� Ğ¾ÑˆĞ¸Ğ±ĞºĞ°')}"
                    )
                return True
            else:
                # Ğ•Ñ�Ğ»Ğ¸ AI Ğ½Ğµ Ñ�Ğ¼Ğ¾Ğ³ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ñ‚ÑŒ, Ğ¿Ñ€ĞµĞ´Ğ»Ğ°Ğ³Ğ°ĞµĞ¼ Ğ°Ğ»ÑŒÑ‚ĞµÑ€Ğ½Ğ°Ñ‚Ğ¸Ğ²Ñ‹
                await message.answer(
                    "ğŸ¤” Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ñ‚ÑŒ ĞµĞ´Ñƒ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ:\n\n"
                    "â€¢ Ğ�Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ¿Ğ¾Ğ´Ñ€Ğ¾Ğ±Ğ½ĞµĞµ: Â«200Ğ³ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğ¹ Ğ³Ñ€ÑƒĞ´ĞºĞ¸ Ñ� Ğ³Ñ€ĞµÑ‡ĞºĞ¾Ğ¹Â»\n"
                    "â€¢ Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ¸Ñ‚ÑŒ Ñ„Ğ¾Ñ‚Ğ¾ Ğ±Ğ»Ñ�Ğ´Ğ°\n"
                    "â€¢ Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñƒ /log_food",
                    parse_mode="HTML"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error in log_food: {e}")
            return False
    
    @staticmethod
    async def handle_log_drink(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²"""
        try:
            # Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ğ¿Ğ°Ñ€Ñ�ĞµÑ€ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²
            from utils.drink_parser import parse_drink
            volume, drink_name, calories = await parse_drink(text)
            
            if not volume or volume <= 0:
                await message.answer(
                    "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ğ¸Ñ‚ÑŒ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·:\n\n"
                    "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹: Ñ�Ğ¾Ğº 250 Ğ¼Ğ», Ñ‡Ğ°Ğ¹ Ñ� Ñ�Ğ°Ñ…Ğ°Ñ€Ğ¾Ğ¼ 300, Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾ 200"
                )
                return False
            
            # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº
            from services.soup_service import save_drink
            result = await save_drink(user_id, text)
            
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�
            from database.db import get_session
            from database.models import User, DrinkEntry
            from sqlalchemy import func, extract
            from keyboards.reply_v2 import get_main_keyboard_v2
            from datetime import datetime
            
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await message.answer(
                        "â�Œ Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                        reply_markup=get_main_keyboard_v2()
                    )
                    return False
                
                # Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�
                today_stats = await session.execute(
                    select(func.sum(DrinkEntry.volume_ml), func.sum(DrinkEntry.calories)).where(
                        DrinkEntry.user_id == user.id,
                        extract('day', DrinkEntry.datetime) == datetime.now().day,
                        extract('month', DrinkEntry.datetime) == datetime.now().month,
                        extract('year', DrinkEntry.datetime) == datetime.now().year
                    )
                )
                total_volume, total_calories = today_stats.first() or (0, 0)
                
                progress = (total_volume / user.daily_water_goal) * 100
                
                await message.answer(
                    f"âœ… <b>Ğ�Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½!</b>\n\n"
                    f"ğŸ¥¤ {drink_name.title()}: {volume:.0f} Ğ¼Ğ»\n"
                    f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {calories:.0f} ĞºĞºĞ°Ğ»\n\n"
                    f"ğŸ“Š <b>Ğ’Ñ�ĞµĞ³Ğ¾ Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�:</b>\n"
                    f"ğŸ’¦ Ğ–Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ: {total_volume:.0f} Ğ¼Ğ»\n"
                    f"ğŸ�¯ Ğ¦ĞµĞ»ÑŒ: {user.daily_water_goal} Ğ¼Ğ»\n"
                    f"ğŸ“ˆ ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�: {progress:.1f}%\n"
                    f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ Ğ¸Ğ· Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²: {total_calories:.0f} ĞºĞºĞ°Ğ»\n\n"
                    f"{'ğŸ�‰ Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾!' if progress >= 100 else 'ğŸ’ª ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ!'}",
                    reply_markup=get_main_keyboard_v2(),
                    parse_mode="HTML"
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Error in handle_log_drink: {e}")
            await message.answer("â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ğµ Ñ€Ğ°Ğ·.")
            return False
    
    @staticmethod
    async def handle_log_water(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²Ğ¾Ğ´Ñ‹"""
        try:
            # Ğ˜Ğ·Ğ²Ğ»ĞµĞºĞ°ĞµĞ¼ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ğ²Ğ¾Ğ´Ñ‹
            from services.intent_classifier import IntentClassifier
            entities = IntentClassifier.extract_entities(text, "log_water")
            
            amount = entities.get('amount_ml')
            if not amount:
                # ĞŸÑ€Ğ¾Ğ±ÑƒĞµĞ¼ Ğ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¾Ğ¹ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³
                from utils.water_parser import parse_water_amount
                amount = parse_water_amount(text)
            
            if amount and amount > 0:
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ² Ğ±Ğ°Ğ·Ñƒ
                from database.db import get_session
                from database.models import User, DrinkEntry
                from datetime import datetime
                
                async with get_session() as session:
                    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
                    user_result = await session.execute(
                        select(User).where(User.telegram_id == user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    
                    if not user:
                        await message.answer(
                            "â�Œ Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                            reply_markup=get_main_keyboard_v2()
                        )
                        return False
                    
                    # Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ğ·Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ¾ Ğ²Ğ¾Ğ´Ğµ
                    water_entry = DrinkEntry(
                        user_id=user.id,
                        name='Ğ²Ğ¾Ğ´Ğ°',
                        volume_ml=amount,
                        source='drink',
                        datetime=datetime.now()
                    )
                    session.add(water_entry)
                    await session.commit()
                    
                    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�
                    from keyboards.reply_v2 import get_main_keyboard_v2
                    from sqlalchemy import func, extract
                    
                    today_stats = await session.execute(
                        select(func.sum(DrinkEntry.volume_ml)).where(
                            DrinkEntry.user_id == user.id,
                            extract('day', DrinkEntry.datetime) == datetime.now().day,
                            extract('month', DrinkEntry.datetime) == datetime.now().month,
                            extract('year', DrinkEntry.datetime) == datetime.now().year
                        )
                    )
                    today_total = today_stats.scalar() or 0
                    
                    # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¾Ñ‚Ğ²ĞµÑ‚
                    progress_percent = (today_total / user.daily_water_goal) * 100 if user.daily_water_goal else 0
                    remaining = user.daily_water_goal - today_total if user.daily_water_goal else 0
                    
                    response = f"ğŸ’§ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¾: {amount} Ğ¼Ğ»</b>\n\n"
                    response += f"ğŸ“Š <b>Ğ¡ĞµĞ³Ğ¾Ğ´Ğ½Ñ� Ğ²Ñ‹Ğ¿Ğ¸Ñ‚Ğ¾:</b> {today_total} Ğ¼Ğ»\n"
                    response += f"ğŸ�¯ <b>Ğ�Ğ¾Ñ€Ğ¼Ğ°:</b> {user.daily_water_goal} Ğ¼Ğ»\n"
                    response += f"ğŸ“ˆ <b>ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�:</b> {progress_percent:.0f}%\n"
                    
                    if remaining > 0:
                        response += f"ğŸ’ª <b>Ğ�Ñ�Ñ‚Ğ°Ğ»Ğ¾Ñ�ÑŒ:</b> {remaining} Ğ¼Ğ»"
                    else:
                        response += f"ğŸ�‰ <b>Ğ�Ğ¾Ñ€Ğ¼Ğ° Ğ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ°!</b>"
                    
                    await message.answer(response, parse_mode="HTML")
                    return True
            else:
                await message.answer(
                    "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ğ¸Ñ‚ÑŒ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ğ²Ğ¾Ğ´Ñ‹.\n\n"
                    "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:\n"
                    "â€¢ Â«Ğ’Ñ‹Ğ¿Ğ¸Ğ» 2 Ñ�Ñ‚Ğ°ĞºĞ°Ğ½Ğ°Â»\n"
                    "â€¢ Â«500 Ğ¼Ğ» Ğ²Ğ¾Ğ´Ñ‹Â»\n"
                    "â€¢ Â«1.5 Ğ»Ğ¸Ñ‚Ñ€Ğ°Â»",
                    parse_mode="HTML"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error in log_water: {e}")
            return False
    
    @staticmethod
    async def handle_log_weight(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ°"""
        try:
            # Ğ˜Ğ·Ğ²Ğ»ĞµĞºĞ°ĞµĞ¼ Ğ²ĞµÑ�
            from services.intent_classifier import IntentClassifier
            entities = IntentClassifier.extract_entities(text, "log_weight")
            
            weight_kg = entities.get('weight_kg')
            
            if weight_kg and 30 <= weight_kg <= 300:
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ² Ğ±Ğ°Ğ·Ñƒ Ğ¸ Ğ¿ĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ½Ğ¾Ñ€Ğ¼Ñ‹
                from database.db import get_session
                from database.models import User, WeightEntry
                from datetime import datetime
                from services.calculator import calculate_calorie_goal, calculate_water_goal
                from services.body_stats import get_body_composition_analysis
                
                async with get_session() as session:
                    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
                    user_result = await session.execute(
                        select(User).where(User.telegram_id == user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    
                    if not user:
                        await message.answer(
                            "â�Œ Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                            reply_markup=get_main_keyboard_v2()
                        )
                        return False
                    
                    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ñ€ĞµĞ´Ñ‹Ğ´ÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ� Ğ´Ğ»Ñ� Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ñ‚Ñ€ĞµĞ½Ğ´Ğ°
                    previous_weights_result = await session.execute(
                        select(WeightEntry.weight).where(
                            WeightEntry.user_id == user.id
                        ).order_by(WeightEntry.datetime.desc()).limit(10)
                    )
                    previous_weights = [row[0] for row in previous_weights_result.fetchall()]
                    
                    # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ½Ğ¾Ğ²ÑƒÑ� Ğ·Ğ°Ğ¿Ğ¸Ñ�ÑŒ Ğ²ĞµÑ�Ğ°
                    weight_entry = WeightEntry(
                        user_id=user.id,
                        weight=weight_kg,
                        datetime=datetime.now()
                    )
                    session.add(weight_entry)
                    
                    # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ğ²ĞµÑ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ¸ Ğ¿ĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ½Ğ¾Ñ€Ğ¼Ñ‹
                    old_weight = user.weight
                    user.weight = weight_kg
                    
                    # ĞŸĞµÑ€ĞµÑ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ ĞšĞ‘Ğ–Ğ£
                    calories, protein, fat, carbs = calculate_calorie_goal(
                        weight=weight_kg,
                        height=user.height,
                        age=user.age,
                        gender=user.gender,
                        activity_level=user.activity_level,
                        goal=user.goal
                    )
                    
                    water_goal = calculate_water_goal(
                        weight=weight_kg,
                        activity_level=user.activity_level,
                        temperature=20.0,
                        goal=user.goal,  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ñ†ĞµĞ»ÑŒ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
                        gender=user.gender  # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¿Ğ¾Ğ» Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ğ²Ğ¾Ğ´Ñ‹
                    )
                    
                    # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ğ½Ğ¾Ñ€Ğ¼Ñ‹
                    user.daily_calorie_goal = round(calories)
                    user.daily_protein_goal = round(protein)
                    user.daily_fat_goal = round(fat)
                    user.daily_carbs_goal = round(carbs)
                    user.daily_water_goal = round(water_goal)
                    
                    # Ğ�Ğ½Ğ°Ğ»Ğ¸Ğ· ĞºĞ¾Ğ¼Ğ¿Ğ¾Ğ·Ğ¸Ñ†Ğ¸Ğ¸ Ñ‚ĞµĞ»Ğ°
                    body_analysis = get_body_composition_analysis(
                        weight=weight_kg,
                        height=user.height,
                        age=user.age,
                        gender=user.gender,
                        neck_cm=user.neck_cm,
                        waist_cm=user.waist_cm,
                        hip_cm=user.hip_cm
                    )
                    
                    # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ % Ğ¶Ğ¸Ñ€Ğ°
                    user.last_bodyfat = body_analysis['body_fat']
                    
                    await session.commit()
                    
                    # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ñ€Ğ°Ğ·Ğ²ĞµÑ€Ğ½ÑƒÑ‚Ñ‹Ğ¹ Ğ¾Ñ‚Ğ²ĞµÑ‚
                    change = weight_kg - old_weight if old_weight else 0
                    
                    response = f"âš–ï¸� <b>Ğ’ĞµÑ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½: {weight_kg} ĞºĞ³</b>\n\n"
                    
                    if old_weight and abs(change) >= 0.1:
                        if change > 0:
                            response += f"ğŸ“ˆ <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b> +{change:.1f} ĞºĞ³\n"
                        else:
                            response += f"ğŸ“‰ <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b> {change:.1f} ĞºĞ³\n"
                    
                    # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ· ĞºĞ¾Ğ¼Ğ¿Ğ¾Ğ·Ğ¸Ñ†Ğ¸Ğ¸ Ñ‚ĞµĞ»Ğ°
                    response += f"\nğŸ§¬ <b>Ğ�Ğ½Ğ°Ğ»Ğ¸Ğ· Ñ‚ĞµĞ»Ğ°:</b>\n"
                    response += f"â€¢ Ğ˜ĞœĞ¢: {body_analysis['bmi']} {body_analysis['bmi_color']}\n"
                    response += f"â€¢ Ğ¡Ñ‚Ğ°Ñ‚ÑƒÑ�: {body_analysis['bmi_status']}\n"
                    response += f"â€¢ % Ğ¶Ğ¸Ñ€Ğ°: {body_analysis['body_fat']}%\n"
                    response += f"â€¢ ĞœÑ‹ÑˆĞµÑ‡Ğ½Ğ°Ñ� Ğ¼Ğ°Ñ�Ñ�Ğ°: {body_analysis['muscle_mass']} ĞºĞ³\n"
                    response += f"â€¢ Ğ’Ğ¾Ğ´Ğ° Ğ² Ğ¾Ñ€Ğ³Ğ°Ğ½Ğ¸Ğ·Ğ¼Ğµ: {body_analysis['body_water']} Ğ»\n"
                    
                    # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½Ğ½Ñ‹Ğµ Ğ½Ğ¾Ñ€Ğ¼Ñ‹
                    response += f"\nğŸ”¥ <b>Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½Ğ½Ñ‹Ğµ Ğ½Ğ¾Ñ€Ğ¼Ñ‹:</b>\n"
                    response += f"â€¢ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {user.daily_calorie_goal} ĞºĞºĞ°Ğ»/Ğ´ĞµĞ½ÑŒ\n"
                    response += f"â€¢ Ğ‘ĞµĞ»ĞºĞ¸: {user.daily_protein_goal} Ğ³\n"
                    response += f"â€¢ Ğ–Ğ¸Ñ€Ñ‹: {user.daily_fat_goal} Ğ³\n"
                    response += f"â€¢ Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {user.daily_carbs_goal} Ğ³\n"
                    response += f"â€¢ Ğ’Ğ¾Ğ´Ğ°: {user.daily_water_goal} Ğ¼Ğ»\n"
                    
                    await message.answer(response, parse_mode="HTML")
                    return True
            else:
                await message.answer(
                    "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ğ¸Ñ‚ÑŒ Ğ²ĞµÑ�.\n\n"
                    "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:\n"
                    "â€¢ Â«Ğ’ĞµÑ� 70.5 ĞºĞ³Â»\n"
                    "â€¢ Â«Ğ’Ğ·Ğ²ĞµÑ�Ğ¸Ğ»Ñ�Ñ� - 72 ĞºĞ³Â»\n"
                    "â€¢ Â«ĞœĞ¾Ğ¹ Ğ²ĞµÑ� 68.2Â»",
                    parse_mode="HTML"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error in log_weight: {e}")
            return False
    
    @staticmethod
    async def handle_log_activity(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
        try:
            # Ğ˜Ğ·Ğ²Ğ»ĞµĞºĞ°ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
            from services.intent_classifier import IntentClassifier
            entities = IntentClassifier.extract_entities(text, "log_activity")
            
            activity_type = entities.get('activity_type')
            duration_min = entities.get('duration_min')
            distance_km = entities.get('distance_km')
            steps = entities.get('steps')
            
            if not activity_type:
                await message.answer(
                    "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ğ¸Ñ‚ÑŒ Ñ‚Ğ¸Ğ¿ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸.\n\n"
                    "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:\n"
                    "â€¢ Â«ĞŸÑ€Ğ¾Ğ±ĞµĞ¶Ğ°Ğ» 5 ĞºĞ¼ Ğ·Ğ° 30 Ğ¼Ğ¸Ğ½ÑƒÑ‚Â»\n"
                    "â€¢ Â«Ğ¥Ğ¾Ğ´Ğ¸Ğ» 1 Ñ‡Ğ°Ñ�Â»\n"
                    "â€¢ Â«ĞŸĞ»Ğ°Ğ²Ğ°Ğ» 45 Ğ¼Ğ¸Ğ½ÑƒÑ‚Â»",
                    parse_mode="HTML"
                )
                return False
            
            # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸
            from services.activity_service import estimate_calories_burned
            
            if duration_min:
                calories = estimate_calories_burned(activity_type, duration_min)
            elif distance_km:
                # ĞŸÑ€Ğ¸Ğ±Ğ»Ğ¸Ğ·Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ²Ñ€ĞµĞ¼Ñ� Ğ´Ğ»Ñ� Ğ´Ğ¸Ñ�Ñ‚Ğ°Ğ½Ñ†Ğ¸Ğ¸
                if activity_type == 'running':
                    duration_min = distance_km * 6  # 6 Ğ¼Ğ¸Ğ½/ĞºĞ¼
                elif activity_type == 'walking':
                    duration_min = distance_km * 12  # 12 Ğ¼Ğ¸Ğ½/ĞºĞ¼
                else:
                    duration_min = distance_km * 8  # Ñ�Ñ€ĞµĞ´Ğ½ĞµĞµ
                calories = estimate_calories_burned(activity_type, duration_min)
            elif steps:
                # Ğ�Ñ†ĞµĞ½Ğ¸Ğ²Ğ°ĞµĞ¼ Ğ²Ñ€ĞµĞ¼Ñ� Ğ¿Ğ¾ ÑˆĞ°Ğ³Ğ°Ğ¼ (Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€Ğ½Ğ¾ 120 ÑˆĞ°Ğ³Ğ¾Ğ² Ğ² Ğ¼Ğ¸Ğ½ÑƒÑ‚Ñƒ)
                duration_min = steps // 120
                calories = estimate_calories_burned(activity_type, duration_min)
            else:
                calories = 0
            
            # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ² Ğ±Ğ°Ğ·Ñƒ
            from database.db import get_session
            from database.models import User, Activity
            from datetime import datetime
            
            async with get_session() as session:
                user_result = await session.execute(
                    select(User).where(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await message.answer(
                        "â�Œ Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                        reply_markup=get_main_keyboard_v2()
                    )
                    return False
                
                activity = Activity(
                    user_id=user.id,
                    activity_type=activity_type,
                    duration_min=duration_min or 0,
                    calories_burned=calories,
                    distance_km=distance_km,
                    steps=steps,
                    datetime=datetime.now()
                )
                session.add(activity)
                await session.commit()
                
                # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¾Ñ‚Ğ²ĞµÑ‚
                activity_names = {
                    'running': 'Ğ‘ĞµĞ³',
                    'walking': 'Ğ¥Ğ¾Ğ´ÑŒĞ±Ğ°',
                    'workout': 'Ğ¢Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°',
                    'yoga': 'Ğ™Ğ¾Ğ³Ğ°',
                    'fitness': 'Ğ¤Ğ¸Ñ‚Ğ½ĞµÑ�',
                    'swimming': 'ĞŸĞ»Ğ°Ğ²Ğ°Ğ½Ğ¸Ğµ',
                    'cycling': 'Ğ’ĞµĞ»Ğ¾Ñ�Ğ¸Ğ¿ĞµĞ´',
                    'other': 'Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ'
                }
                
                activity_name = activity_names.get(activity_type, 'Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ')
                
                response = f"ğŸ�ƒ <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¾: {activity_name}</b>\n\n"
                
                if duration_min:
                    response += f"â�±ï¸� Ğ”Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ: {duration_min} Ğ¼Ğ¸Ğ½\n"
                if distance_km:
                    response += f"ğŸ“� Ğ”Ğ¸Ñ�Ñ‚Ğ°Ğ½Ñ†Ğ¸Ñ�: {distance_km} ĞºĞ¼\n"
                if steps:
                    response += f"ğŸ‘� Ğ¨Ğ°Ğ³Ğ¸: {steps:,}\n"
                
                response += f"ğŸ”¥ Ğ¡Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹: {calories} ĞºĞºĞ°Ğ»\n"
                
                await message.answer(response, parse_mode="HTML")
                return True
                
        except Exception as e:
            logger.error(f"Error in log_activity: {e}")
            return False
    
    @staticmethod
    async def handle_show_progress(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ° Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°"""
        try:
            # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¼ĞµĞ½Ñ� Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´Ğ°
            from keyboards.inline import get_progress_menu
            
            await message.answer(
                "ğŸ“Š <b>Ğ’Ñ‹Ğ±ĞµÑ€Ğ¸Ñ‚Ğµ Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´ Ğ´Ğ»Ñ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸:</b>",
                reply_markup=get_progress_menu(),
                parse_mode="HTML"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error in show_progress: {e}")
            return False
    
    @staticmethod
    async def handle_ask_ai(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�Ğ° Ğº AI"""
        try:
            from handlers.ai_assistant import process_ai_question
            await process_ai_question(message, state)
            return True
            
        except Exception as e:
            logger.error(f"Error in ask_ai: {e}")
            return False
    
    @staticmethod
    async def handle_help(text: str, user_id: int, message: Message, state: FSMContext) -> bool:
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ° Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ¸"""
        try:
            from handlers.common import cmd_help
            await cmd_help(message, state)
            return True
            
        except Exception as e:
            logger.error(f"Error in help: {e}")
            return False
