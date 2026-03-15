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
async def handle_voice(message: Message, state: FSMContext):
    """Handle voice messages: transcribe and process as text."""
    user_id = message.from_user.id
    user_context = await get_user_context(user_id)
    
    # Download voice
    voice = message.voice
    file_info = await message.bot.get_file(voice.file_id)
    file_bytes = await message.bot.download_file(file_info.file_path)
    voice_data = file_bytes.read()
    
    # Transcribe using existing function from ai_assistant (or create a simple one)
    from services.cloudflare_ai import transcribe_audio
    try:
        text = await transcribe_audio(voice_data, language="ru")
        if not text:
            await message.answer("❌ Не удалось распознать голосовое сообщение.")
            return
    except Exception as e:
        logger.error(f"Voice transcription failed: {e}")
        await message.answer("❌ Ошибка при распознавании голоса.")
        return
    
    # Now process the transcribed text as a regular message
    await handle_text_message(message, state, text, user_context, is_voice=True)

@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    """Handle text messages via AI processor."""
    user_id = message.from_user.id
    user_context = await get_user_context(user_id)
    await handle_text_message(message, state, message.text, user_context)

async def handle_text_message(message: Message, state: FSMContext, text: str, user_context: dict, is_voice: bool = False):
    """Common text processing logic."""
    # Get conversation history from state
    data = await state.get_data()
    history = data.get('conversation_history', [])
    
    # Process with AI brain
    result = await ai_processor.process_text_input(
        text=text,
        user_context=user_context,
        conversation_history=history
    )
    
    # Update history
    history.append(text)
    if len(history) > 10:
        history = history[-10:]
    await state.update_data(conversation_history=history)
    
    intent = result.get("intent")
    params = result.get("parameters", {})
    
    if intent == "error":
        await message.answer(f"❌ Ошибка обработки: {result.get('error')}")
        return
    
    if intent == "unknown":
        await message.answer(
            "🤔 Я не понял ваш запрос. Попробуйте переформулировать или используйте команды como /help."
        )
        return
    
    # Handle each intent
    if intent == "log_food":
        await _handle_log_food(message, params, user_id)
    elif intent == "log_water":
        await _handle_log_water(message, params, user_id)
    elif intent == "log_activity":
        await _handle_log_activity(message, params, user_id)
    elif intent == "log_steps":
        await _handle_log_steps(message, params, user_id)
    elif intent == "get_recommendations":
        await _handle_get_recommendations(message, state, user_id, user_context)
    elif intent == "set_profile":
        await _handle_set_profile(message, params, user_id, state)
    else:
        await message.answer("🤖 Запрос обработан, но действие не определено.")

async def _handle_log_food(message: Message, params: dict, user_id: int):
    description = params.get("description", "Еда")
    nutrients = {k: params.get(k, 0) for k in ("calories", "protein", "fat", "carbs")}
    
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile")
            return
        
         from database.models import Meal
         from datetime import datetime
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

async def _handle_log_water(message: Message, params: dict, user_id: int):
    amount_ml = params.get("amount_ml", 0)
    if amount_ml <= 0:
        await message.answer("❌ Укажите корректное количество воды (например, 'выпил 200 мл').")
        return
    
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile")
            return
        
        from database.models import WaterEntry
        from datetime import datetime
        water = WaterEntry(
            user_id=user.id,
            amount=amount_ml,
            datetime=datetime.now()
        )
        session.add(water)
        await session.commit()
    
    await message.answer(f"💧 Записано воды: {amount_ml} мл")

async def _handle_log_activity(message: Message, params: dict, user_id: int):
    activity_type = params.get("type", "активность")
    duration_min = params.get("duration_min", 0)
    if duration_min <= 0:
        await message.answer("❌ Укажите корректную длительность активности (например, 'бегал 30 минут').")
        return
    
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile")
            return
        
        from database.models import Activity
        from datetime import datetime
        # Simple calorie estimate: you can improve this with MET
        activity = Activity(
            user_id=user.id,
            activity_type=activity_type,
            duration=duration_min,
            calories_burned=duration_min * 5,  # rough estimate
            datetime=datetime.now()
        )
        session.add(activity)
        await session.commit()
    
    await message.answer(f"🏃 Записана активность: {activity_type} ({duration_min} мин)")

async def _handle_log_steps(message: Message, params: dict, user_id: int):
    count = params.get("count", 0)
    if count <= 0:
        await message.answer("❌ Укажите корректное количество шагов (например, 'прошел 5000 шагов').")
        return
    
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile")
            return
        
        from database.models import StepsEntry
        from datetime import datetime
        steps = StepsEntry(
            user_id=user.id,
            steps_count=count,
            datetime=datetime.now()
        )
        session.add(steps)
        await session.commit()
    
    await message.answer(f"👣 Записано шагов: {count}")

async def _handle_get_recommendations(message: Message, state: FSMContext, user_id: int, user_context: dict):
    # Get recent logs for context (simplified)
    recent_logs = {}
    async with get_session() as session:
        from sqlalchemy import select, desc
        from database.models import Meal, WaterEntry, Activity, StepsEntry
        from datetime import datetime, timedelta
        
        # Last 24 hours
        since = datetime.now() - timedelta(days=1)
        
        # Meals
        meals_result = await session.execute(
            select(Meal.description, Meal.calories)
            .where(Meal.user_id == user_id, Meal.datetime >= since)
            .order_by(desc(Meal.datetime))
            .limit(5)
        )
        recent_logs["meals"] = [{"description": r[0], "calories": r[1]} for r in meals_result]
        
        # Water
        water_result = await session.execute(
            select(WaterEntry.amount)
            .where(WaterEntry.user_id == user_id, WaterEntry.datetime >= since)
            .order_by(desc(WaterEntry.datetime))
            .limit(5)
        )
        recent_logs["water"] = [{"amount_ml": r[0]} for r in water_result]
        
        # Activity
        activity_result = await session.execute(
            select(Activity.activity_type, Activity.duration)
            .where(Activity.user_id == user_id, Activity.datetime >= since)
            .order_by(desc(Activity.datetime))
            .limit(5)
        )
        recent_logs["activities"] = [{"type": r[0], "duration_min": r[1]} for r in activity_result]
        
        # Steps
        steps_result = await session.execute(
            select(StepsEntry.steps_count)
            .where(StepsEntry.user_id == user_id, StepsEntry.datetime >= since)
            .order_by(desc(StepsEntry.datetime))
            .limit(5)
        )
        recent_logs["steps"] = [{"count": r[0]} for r in steps_result]
    
    # Generate recommendations via AI
    rec_result = await ai_processor.generate_recommendations(
        user_context=user_context,
        recent_logs=recent_logs
    )
    
    if "error" in rec_result:
        await message.answer(f"❌ Ошибка генерации рекомендаций: {rec_result['error']}")
        return
    
    # Format response
    resp = (
        f"📋 **Персональные рекомендации на сегодня:**\n\n"
        f"🔥 Калории: {rec_result.get('calories_target', 0)} ккал\n"
        f"🥩 Белки: {rec_result.get('protein_target_g', 0)}г\n"
        f"🥑 Жиры: {rec_result.get('fat_target_g', 0)}г\n"
        f"🍚 Углеводы: {rec_result.get('carbs_target_g', 0)}г\n"
        f"💧 Вода: {rec_result.get('water_target_ml', 0)} мл\n\n"
    )
    
    activity_sugg = rec_result.get("activity_suggestions", [])
    if activity_sugg:
        resp += "🏃 **Предложения по активности:**\n"
        for sugg in activity_sugg:
            resp += f"• {sugg.get('type', 'активность')} — {sugg.get('duration_min', 0)} мин\n"
        resp += "\n"
    
    advice = rec_result.get("advice", "")
    if advice:
        resp += f"💡 **Совет:** {advice}\n"
    
    await message.answer(resp, parse_mode="Markdown")

async def _handle_set_profile(message: Message, params: dict, user_id: int, state: FSMContext):
    # Update user profile with provided parameters
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer("❌ Сначала создайте профиль через /set_profile (заполните все поля).")
            return
        
        # Update fields if provided
        if 'age' in params:
            user.age = params['age']
        if 'weight_kg' in params:
            user.weight = params['weight_kg']
        if 'height_cm' in params:
            user.height = params['height_cm']
        if 'gender' in params:
            user.gender = params['gender']
        if 'activity_level' in params:
            user.activity_level = params['activity_level']
        if 'goals' in params:
            user.goal = params['goals']
        if 'city' in params:
            user.city = params['city']
        
        await session.commit()
    
    await message.answer("✅ Профиль обновлен!")

# Callback query handler for inline buttons (if needed)
@router.callback_query()
async def handle_callback(callback: CallbackQuery, state: FSMContext):
    # For simplicity, we can ignore callbacks or handle specific ones
    await callback.answer("🤖 Обработка callback через AI пока не реализована. Используйте текстовые команды.")