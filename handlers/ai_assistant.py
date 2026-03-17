"""
handlers/ai_assistant.py
Ğ”Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ¾Ğ²Ñ‹Ğ¹ AI Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚
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
from keyboards.reply import get_main_keyboard

logger = logging.getLogger(__name__)
router = Router()

class AIStates(StatesGroup):
    """Ğ¡Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ° Ñ� AI"""
    in_conversation = State()

@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    """Ğ�Ğ°Ñ‡Ğ°Ñ‚ÑŒ Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³ Ñ� AI Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚Ğ¾Ğ¼"""
    await state.clear()
    await state.set_state(AIStates.in_conversation)
    await state.update_data(conversation_history=[])  # Ğ˜Ğ½Ğ¸Ñ†Ğ¸Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ�
    
    await message.answer(
        "ğŸ¤– <b>AI Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚</b>\n\n"
        "Ğ¯ Ğ³Ğ¾Ñ‚Ğ¾Ğ² Ğ¿Ğ¾Ğ¼Ğ¾Ñ‡ÑŒ Ğ²Ğ°Ğ¼ Ñ� Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�Ğ°Ğ¼Ğ¸ Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ğ¸, Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°Ñ…, Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²ÑŒĞµ Ğ¸ Ğ¼Ğ½Ğ¾Ğ³Ğ¾Ğ¼ Ğ´Ñ€ÑƒĞ³Ğ¾Ğ¼!\n\n"
        "ğŸ’¡ <b>Ğ§Ñ‚Ğ¾ Ñ� Ğ¼Ğ¾Ğ³Ñƒ:</b>\n"
        "â€¢ Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ğ°Ñ‚ÑŒ ĞšĞ‘Ğ–Ğ£ Ğ±Ğ»Ñ�Ğ´\n"
        "â€¢ Ğ”Ğ°Ñ‚ÑŒ Ñ€ĞµĞºĞ¾Ğ¼ĞµĞ½Ğ´Ğ°Ñ†Ğ¸Ğ¸ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�\n"
        "â€¢ ĞŸĞ¾Ğ´Ñ�ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ñ€ĞµÑ†ĞµĞ¿Ñ‚Ñ‹\n"
        "â€¢ Ğ Ğ°Ñ�Ñ�ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ğ¾ Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ğµ\n"
        "â€¢ ĞŸĞ¾Ğ¼Ğ¾Ñ‡ÑŒ Ñ� Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°Ğ¼Ğ¸\n\n"
        "ğŸ“� <b>Ğ—Ğ°Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ²Ğ°Ñˆ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�:</b>\n\n"
        "â�Œ Ğ”Ğ»Ñ� Ğ²Ñ‹Ñ…Ğ¾Ğ´Ğ° Ğ½Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ \"Ğ²Ñ‹Ñ…Ğ¾Ğ´\" Ğ¸Ğ»Ğ¸ /cancel",
        parse_mode="HTML"
    )

@router.message(AIStates.in_conversation)
async def process_ai_question(message: Message, state: FSMContext):
    """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ° Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�Ğ¾Ğ² Ğº AI"""
    user_question = message.text.strip()
    
    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€ĞºĞ° Ğ½Ğ° Ğ²Ñ‹Ñ…Ğ¾Ğ´
    if user_question.lower() in ["Ğ²Ñ‹Ñ…Ğ¾Ğ´", "exit", "quit", "/cancel"]:
        await state.clear()
        await message.answer(
            "ğŸ‘‹ <b>Ğ”Ğ¸Ğ°Ğ»Ğ¾Ğ³ Ğ·Ğ°Ğ²ĞµÑ€ÑˆĞµĞ½</b>\n\n"
            "Ğ’Ñ�ĞµĞ³Ğ´Ğ° Ñ€Ğ°Ğ´ Ğ¿Ğ¾Ğ¼Ğ¾Ñ‡ÑŒ! Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ /ask Ğ´Ğ»Ñ� Ğ½Ğ¾Ğ²Ğ¾Ğ³Ğ¾ Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ°.",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        return
    
    try:
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ� Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ°
        state_data = await state.get_data()
        conversation_history = state_data.get('conversation_history', [])
        
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¸Ğ½Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ†Ğ¸Ñ� Ğ¾ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ğµ Ğ´Ğ»Ñ� ĞºĞ¾Ğ½Ñ‚ĞµĞºÑ�Ñ‚Ğ°
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ´Ğ»Ñ� AI
            user_profile = None
            if user and user.weight and user.height and user.age:
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
        
        # Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ "Ğ¿ĞµÑ‡Ğ°Ñ‚Ğ°ĞµÑ‚..."
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        # ĞšĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ� Ğ² Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚ Ğ´Ğ»Ñ� cloudflare_manager
        converted_history = [{'role': item['role'], 'content': item['message']} for item in conversation_history]
        
        # Ğ—Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğº AI Ñ� Ğ¿Ñ€Ğ°Ğ²Ğ¸Ğ»ÑŒĞ½Ñ‹Ğ¼Ğ¸ Ğ¿Ğ°Ñ€Ğ°Ğ¼ĞµÑ‚Ñ€Ğ°Ğ¼Ğ¸ Ğ¸ Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸ĞµĞ¹
        response_dict = await cf_manager.ai_assistant(
            message=user_question,
            history=converted_history,  # ĞŸĞµÑ€ĞµĞ´Ğ°ĞµĞ¼ Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ� Ğ² Ğ¿Ñ€Ğ°Ğ²Ğ¸Ğ»ÑŒĞ½Ğ¾Ğ¼ Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğµ
            user_profile=user_profile
        )
        
        response = response_dict.get('response', 'Ğ˜Ğ·Ğ²Ğ¸Ğ½Ğ¸Ñ‚Ğµ, Ğ¿Ñ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ°')
        
        # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ� Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ°
        conversation_history.append({
            'role': 'user',
            'message': user_question
        })
        conversation_history.append({
            'role': 'assistant', 
            'message': response
        })
        
        # Ğ�Ğ³Ñ€Ğ°Ğ½Ğ¸Ñ‡Ğ¸Ğ²Ğ°ĞµĞ¼ Ğ¸Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ� Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğ¼Ğ¸ 10 Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ñ�Ğ¼Ğ¸ (5 Ğ¿Ğ°Ñ€)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        await state.update_data(conversation_history=conversation_history)
        
        await message.answer(
            f"ğŸ¤– <b>AI Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚:</b>\n\n{response}\n\n"
            f"ğŸ’¡ <b>ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³!</b>\n"
            f"â�Œ Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ \"Ğ²Ñ‹Ñ…Ğ¾Ğ´\" Ğ´Ğ»Ñ� Ğ·Ğ°Ğ²ĞµÑ€ÑˆĞµĞ½Ğ¸Ñ�",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞµ AI Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�Ğ°: {e}")
        await message.answer(
            "â�Œ ĞŸÑ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ°. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¿ĞµÑ€ĞµÑ„Ğ¾Ñ€Ğ¼ÑƒĞ»Ğ¸Ñ€Ğ¾Ğ²Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ�.\n\n"
            "â�Œ Ğ˜Ğ»Ğ¸ Ğ½Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ \"Ğ²Ñ‹Ñ…Ğ¾Ğ´\" Ğ´Ğ»Ñ� Ğ·Ğ°Ğ²ĞµÑ€ÑˆĞµĞ½Ğ¸Ñ� Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ°.",
            parse_mode="HTML"
        )

@router.message(Command("ai"))
async def cmd_ai(message: Message, state: FSMContext):
    """Ğ�Ğ»ÑŒÑ‚ĞµÑ€Ğ½Ğ°Ñ‚Ğ¸Ğ²Ğ½Ğ°Ñ� ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ° Ğ´Ğ»Ñ� AI"""
    await cmd_ask(message, state)

@router.message(Command("weather"))
async def cmd_weather(message: Message, state: FSMContext):
    """Ğ£Ğ·Ğ½Ğ°Ñ‚ÑŒ Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñƒ"""
    await state.clear()
    
    try:
        # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ³Ğ¾Ñ€Ğ¾Ğ´ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.city:
                await message.answer(
                    "â�Œ Ğ£ĞºĞ°Ğ·Ğ°Ğ½ Ğ³Ğ¾Ñ€Ğ¾Ğ´. Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ¾Ğ¹ /set_profile",
                    reply_markup=get_main_keyboard()
                )
                return
            
            city = user.city
            
            # Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ "Ğ¿ĞµÑ‡Ğ°Ñ‚Ğ°ĞµÑ‚..."
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            # Ğ—Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñ‹ Ñ‡ĞµÑ€ĞµĞ· Ñ€ĞµĞ°Ğ»ÑŒĞ½Ğ¾Ğµ API
            from services.weather import get_weather
            weather_data = await get_weather(city)
            
            if weather_data:
                temp = weather_data.get('temp', 'N/A')
                
                # ĞĞ²Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ¸Ñ‡ĞµÑ�ĞºĞ¸ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ğ§Ğ°Ñ�Ğ¾Ğ²Ğ¾Ğ¹ Ğ¿Ğ¾Ñ�Ğ°Ñ‰ĞµĞ½Ğ¸Ğµ, ĞµÑ�Ğ»Ğ¸ Ğ¾Ğ½Ğ¾ Ğ¾Ñ‚Ğ»Ğ¸Ñ‡Ğ°ĞµÑ‚Ñ�Ñ�
                if 'timezone' in weather_data and weather_data['timezone'] != user.timezone:
                    from database.db import get_session
                    from database.models import User
                    from sqlalchemy import select
                    
                    async with get_session() as session:
                        await session.execute(
                            select(User).where(User.telegram_id == message.from_user.id)
                        )
                        user_obj = await session.scalar_one_or_none()
                        
                        if user_obj:
                            old_timezone = user_obj.timezone
                            user_obj.timezone = weather_data['timezone']
                            await session.commit()
                            logger.info(f"🌍 ĞĞ²Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ¸Ñ‡ĞµÑ�ĞºĞ¸ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½ Ğ§Ğ°Ñ�Ğ¾Ğ²Ğ¾Ğ¹ Ğ¿Ğ¾Ñ�Ğ°Ñ‰ĞµĞ½Ğ¸Ğµ: {old_timezone} → {weather_data['timezone']} (Ğ³Ğ¾Ñ€Ğ¾Ğ´: {city})")
                condition = weather_data.get('condition', 'Ğ½ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ¾')
                humidity = weather_data.get('humidity', 'N/A')
                wind = weather_data.get('wind', 'N/A')
                
                response = (f"ğŸŒ¡ï¸� <b>Ğ¢ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ğ°:</b> {temp}Â°C\n"
                           f"â˜�ï¸� <b>Ğ¡Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ğµ:</b> {condition}\n"
                           f"ğŸ’§ <b>Ğ’Ğ»Ğ°Ğ¶Ğ½Ğ¾Ñ�Ñ‚ÑŒ:</b> {humidity}%\n"
                           f"ğŸ’¨ <b>Ğ’ĞµÑ‚ĞµÑ€:</b> {wind} Ğ¼/Ñ�")
            else:
                response = "Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚ÑŒ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾ Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ğµ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¿Ğ¾Ğ·Ğ¶Ğµ."
            
            await message.answer(
                f"ğŸŒ¦ï¸� <b>ĞŸĞ¾Ğ³Ğ¾Ğ´Ğ° Ğ² {city}</b>\n\n{response}",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ¿Ğ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğ¸ Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñ‹: {e}")
        await message.answer(
            "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚ÑŒ Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñƒ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¿Ğ¾Ğ·Ğ¶Ğµ.",
            reply_markup=get_main_keyboard()
        )

@router.message(Command("recipe"))
async def cmd_recipe(message: Message, state: FSMContext):
    """ĞŸĞ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚ÑŒ Ñ€ĞµÑ†ĞµĞ¿Ñ‚"""
    await state.clear()
    
    await message.answer(
        "ğŸ�³ <b>ĞŸĞ¾Ğ´Ğ±Ğ¾Ñ€ Ñ€ĞµÑ†ĞµĞ¿Ñ‚Ğ°</b>\n\n"
        "Ğ�Ğ°Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ, ĞºĞ°ĞºĞ¾Ğ¹ Ñ€ĞµÑ†ĞµĞ¿Ñ‚ Ğ²Ñ‹ Ñ…Ğ¾Ñ‚Ğ¸Ñ‚Ğµ:\n\n"
        "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹:\n"
        "â€¢ Ğ ĞµÑ†ĞµĞ¿Ñ‚ ĞºÑƒÑ€Ğ¸Ğ½Ğ¾Ğ¹ Ğ³Ñ€ÑƒĞ´ĞºĞ¸\n"
        "â€¢ ĞšĞ°Ğº Ğ¿Ñ€Ğ¸Ğ³Ğ¾Ñ‚Ğ¾Ğ²Ğ¸Ñ‚ÑŒ Ğ¿Ğ°Ñ�Ñ‚Ñƒ\n"
        "â€¢ Ğ‘Ğ»Ñ�Ğ´Ğ¾ Ğ¸Ğ· Ğ³Ñ€ĞµÑ‡ĞºĞ¸\n"
        "â€¢ Ğ¡Ğ°Ğ»Ğ°Ñ‚ Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
        parse_mode="HTML"
    )
    await state.set_state(AIStates.in_conversation)

@router.message(Command("calculate"))
async def cmd_calculate(message: Message, state: FSMContext):
    """Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ğ°Ñ‚ÑŒ ĞšĞ‘Ğ–Ğ£ Ğ±Ğ»Ñ�Ğ´Ğ°"""
    await state.clear()
    
    await message.answer(
        "ğŸ§® <b>Ğ Ğ°Ñ�Ñ‡ĞµÑ‚ ĞšĞ‘Ğ–Ğ£ Ğ±Ğ»Ñ�Ğ´Ğ°</b>\n\n"
        "Ğ�Ğ¿Ğ¸ÑˆĞ¸Ñ‚Ğµ Ğ±Ğ»Ñ�Ğ´Ğ¾ Ğ¸ ĞµĞ³Ğ¾ Ñ�Ğ¾Ñ�Ñ‚Ğ°Ğ²:\n\n"
        "ĞŸÑ€Ğ¸Ğ¼ĞµÑ€:\n"
        "ĞšÑƒÑ€Ğ¸Ğ½Ğ°Ñ� Ğ³Ñ€ÑƒĞ´ĞºĞ° 200Ğ³, Ñ€Ğ¸Ñ� 100Ğ³, Ğ¾Ğ²Ğ¾Ñ‰Ğ¸ 150Ğ³",
        parse_mode="HTML"
    )
    await state.set_state(AIStates.in_conversation)

@router.callback_query(F.data == "ai_assistant")
async def ai_assistant_callback(callback: CallbackQuery, state: FSMContext):
    """Callback Ğ´Ğ»Ñ� AI Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚Ğ° Ğ¸Ğ· Ğ¼ĞµĞ½Ñ�"""
    await callback.answer()
    await cmd_ask(callback.message, state)

@router.callback_query(F.data == "ask_weather")
async def ask_weather_callback(callback: CallbackQuery, state: FSMContext):
    """Callback Ğ´Ğ»Ñ� Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ñ‹ Ğ¸Ğ· Ğ¼ĞµĞ½Ñ�"""
    await callback.answer()
    await cmd_weather(callback.message, state)

@router.callback_query(F.data == "get_recipe")
async def get_recipe_callback(callback: CallbackQuery, state: FSMContext):
    """Callback Ğ´Ğ»Ñ� Ñ€ĞµÑ†ĞµĞ¿Ñ‚Ğ° Ğ¸Ğ· Ğ¼ĞµĞ½Ñ�"""
    await callback.answer()
    await cmd_recipe(callback.message, state)
