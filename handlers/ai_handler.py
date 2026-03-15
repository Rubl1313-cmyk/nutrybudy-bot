"""
AI-driven handler for all message types.
Uses real AI models through AI Model Manager.
"""
import logging
from typing import Optional
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from services.ai_processor import ai_processor
from database.db import get_session
from database.models import User, Meal, WaterEntry, Activity, StepsEntry
from sqlalchemy import select
from datetime import datetime

logger = logging.getLogger(__name__)
router = Router()

async def get_user_context(user_id: int) -> dict:
    """Fetch user profile for context."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            return {
                'age': user.age,
                'gender': user.gender,
                'height_cm': user.height,
                'weight_kg': user.weight,
                'goal': user.goal,
                'activity_level': user.activity_level,
                'city': getattr(user, 'city', None)
            }
        return {}

def _format_nutrition(nutrients: dict) -> str:
    return f"🔥 Калории: {nutrients.get('calories', 0):.0f} | 🥩 Белки: {nutrients.get('protein', 0):.1f}г | 🥑 Жиры: {nutrients.get('fat', 0):.1f}г | 🍚 Углеводы: {nutrients.get('carbs', 0):.1f}г"

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Handle photo messages: recognize food and log meal."""
    user_id = message.from_user.id
    user_context = await get_user_context(user_id)
    
    try:
        # Get the largest photo
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        image_data = file_bytes.read()
        
        # Process with real AI
        result = await ai_processor.process_photo_input(
            image_bytes=image_data,
            user_context=user_context,
            accompanying_text=message.caption
        )
        
        if result.get("intent") == "error":
            await message.answer(f"❌ Ошибка обработки фото: {result.get('error')}")
            return
        
        if result.get("intent") == "log_food":
            params = result.get("parameters", {})
            description = params.get("description", "Еда")
            nutrients = {k: params.get(k, 0) for k in ("calories", "protein", "fat", "carbs")}
            
            # Save meal to DB
            async with get_session() as session:
                # Get user
                user_result = await session.execute(select(User).where(User.telegram_id == user_id))
                user = user_result.scalar_one_or_none()
                if not user:
                    await message.answer("❌ Сначала создайте профиль через /set_profile")
                    return
                
                # Create meal entry
                meal = Meal(
                    user_id=user.id,
                    ai_description=description,
                    calories=nutrients['calories'],
                    protein=nutrients['protein'],
                    fat=nutrients['fat'],
                    carbs=nutrients['carbs'],
                    datetime=datetime.now()
                )
                session.add(meal)
                await session.commit()
            
            await message.answer(
                f"✅ Записан приём пищи: {description}\n"
                f"{_format_nutrition(nutrients)}"
            )
        else:
            # Fallback to text processing if needed
            await message.answer("🤖 Я обработал фото, но не уверен, как поступить. Попробуйте описать еду текстом.")
            
    except Exception as e:
        logger.error(f"Error processing photo: {e}", exc_info=True)
        await message.answer("❌ Ошибка обработки фото. Попробуйте еще раз.")

@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    """Handle text messages with real AI processing."""
    user_id = message.from_user.id
    user_context = await get_user_context(user_id)
    
    try:
        # Process with real AI
        result = await ai_processor.process_text_input(
            text=message.text,
            user_context=user_context
        )
        
        if result.get("intent") == "error":
            await message.answer(f"❌ Ошибка обработки: {result.get('error')}")
            return
        
        intent = result.get("intent")
        params = result.get("parameters", {})
        
        # Handle different intents
        if intent == "log_food":
            await handle_food_intent(message, params, user_id)
        elif intent == "log_water":
            await handle_water_intent(message, params, user_id)
        elif intent == "log_steps":
            await handle_steps_intent(message, params, user_id)
        elif intent == "log_activity":
            await handle_activity_intent(message, params, user_id)
        elif intent == "ai_response":
            response = params.get("response", "Я не знаю, что ответить.")
            await message.answer(response)
        else:
            await message.answer("🤖 Я не понял запрос. Попробуйте переформулировать.")
            
    except Exception as e:
        logger.error(f"Error processing text: {e}", exc_info=True)
        await message.answer("❌ Ошибка обработки. Попробуйте еще раз.")

async def handle_food_intent(message: Message, params: dict, user_id: int):
    """Handle food logging intent."""
    description = params.get("description", "Еда")
    nutrients = {k: params.get(k, 0) for k in ("calories", "protein", "fat", "carbs")}
    
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile")
            return
        
        meal = Meal(
            user_id=user.id,
            ai_description=description,
            calories=nutrients['calories'],
            protein=nutrients['protein'],
            fat=nutrients['fat'],
            carbs=nutrients['carbs'],
            datetime=datetime.now()
        )
        session.add(meal)
        await session.commit()
    
    await message.answer(
        f"✅ Записано: {description}\n"
        f"{_format_nutrition(nutrients)}"
    )

async def handle_water_intent(message: Message, params: dict, user_id: int):
    """Handle water logging intent."""
    amount = params.get("amount_ml", 0)
    
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile")
            return
        
        water_entry = WaterEntry(
            user_id=user.id,
            amount=amount,
            datetime=datetime.now()
        )
        session.add(water_entry)
        await session.commit()
    
    await message.answer(f"💧 Записано: {amount}мл воды")

async def handle_steps_intent(message: Message, params: dict, user_id: int):
    """Handle steps logging intent."""
    steps = params.get("count", 0)
    calories_burned = steps * 0.04  # ~0.04 ккал на шаг
    
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile")
            return
        
        steps_entry = StepsEntry(
            user_id=user.id,
            steps=steps,
            datetime=datetime.now()
        )
        session.add(steps_entry)
        await session.commit()
    
    await message.answer(
        f"👞 Записано: {steps:,} шагов\n"
        f"🔥 Сожжено: {calories_burned:.0f} ккал"
    )

async def handle_activity_intent(message: Message, params: dict, user_id: int):
    """Handle activity logging intent."""
    activity_type = params.get("type", "другое")
    duration = params.get("duration_min", 0)
    
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile")
            return
        
        activity = Activity(
            user_id=user.id,
            activity_type=activity_type,
            duration_minutes=duration,
            datetime=datetime.now()
        )
        session.add(activity)
        await session.commit()
    
    await message.answer(f"🏃 Записано: {activity_type} - {duration} мин")
