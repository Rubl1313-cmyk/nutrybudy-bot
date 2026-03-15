"""
AI Handler - обрабатывает все AI запросы через новый процессор
"""
import logging
from datetime import datetime
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from services.ai_processor import ai_processor
from services.food_save_service import food_save_service
from utils.gamification import gamification
from database.db import get_session
from database.models import User, Meal
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = Router()

async def get_user_context(user_id: int) -> dict:
    """Получает контекст пользователя (профиль, история и т.д.)"""
    try:
        async with get_session() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            
            if user:
                return {
                    "profile": {
                        "id": user.id,
                        "first_name": user.first_name,
                        "age": user.age,
                        "gender": user.gender,
                        "weight": user.weight,
                        "height": user.height,
                        "goal": user.goal,
                        "activity_level": user.activity_level,
                        "daily_calorie_goal": user.daily_calorie_goal,
                        "daily_protein_goal": user.daily_protein_goal,
                        "daily_fat_goal": user.daily_fat_goal,
                        "daily_carbs_goal": user.daily_carbs_goal,
                        "daily_water_goal": user.daily_water_goal,
                        "daily_steps_goal": user.daily_steps_goal
                    }
                }
            return {"profile": None}
    except Exception as e:
        logger.error(f"❌ Error getting user context: {e}")
        return {"profile": None}

async def send_achievement_notifications(message: types.Message, achievements: list):
    """Отправляет уведомления о новых достижениях"""
    if not achievements:
        return
    
    notification_text = f"🎉 <b>Новые достижения!</b>\n\n"
    
    for achievement in achievements:
        notification_text += f"{achievement.icon} {achievement.name}\n"
        notification_text += f"   {achievement.description}\n"
        notification_text += f"   +{achievement.points} очков\n\n"
    
    stats = await gamification.get_user_stats(message.from_user.id)
    notification_text += f"📊 Всего очков: {stats['total_points']}"
    
    await message.answer(notification_text, parse_mode="HTML")

async def save_food_and_respond(message: types.Message, food_data: dict):
    """Сохраняет еду в базу и отправляет ответ"""
    try:
        user_id = message.from_user.id
        
        async with get_session() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not user:
                await message.answer(
                    "❌ Сначала создайте профиль через /set_profile",
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[[types.KeyboardButton(text="/set_profile")]],
                        resize_keyboard=True
                    )
                )
                return
            
            # Сохраняем еду в базу
            meal = Meal(
                user_id=user.id,
                ai_description=food_data.get("description", "Неизвестная еда"),
                total_calories=food_data.get("calories", 0),      # ← было calories
                total_protein=food_data.get("protein", 0),        # ← было protein
                total_fat=food_data.get("fat", 0),                # ← было fat
                total_carbs=food_data.get("carbs", 0),            # ← было carbs
                meal_type=food_data.get("meal_type", "other"),  # Добавляем тип приема пищи
                datetime=datetime.now()
            )
            session.add(meal)
            await session.commit()
            
            # Формируем ответ
            calories = food_data.get("calories", 0)
            protein = food_data.get("protein", 0)
            fat = food_data.get("fat", 0)
            carbs = food_data.get("carbs", 0)
            
            response = f"✅ <b>Записано:</b>\n"
            response += f"🍽️ {food_data.get('description', 'Неизвестная еда')}\n\n"
            response += f"🔥 Калории: {calories} ккал\n"
            response += f"🥩 Белки: {protein}г\n"
            response += f"🥑 Жиры: {fat}г\n"
            response += f"🍚 Углеводы: {carbs}г\n\n"
            
            # Добавляем прогресс по целям
            if user.daily_calorie_goal:
                calorie_progress = (calories / user.daily_calorie_goal) * 100
                response += f"📊 Прогресс по калориям: {calorie_progress:.1f}%\n"
            
            await message.answer(
                response,
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text="📸 Сделать фото еды")],
                        [types.KeyboardButton(text="📊 Мой прогресс")],
                        [types.KeyboardButton(text="🏠 Главное меню")]
                    ],
                    resize_keyboard=True
                ),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"❌ Error saving food: {e}")
        await message.answer("❌ Ошибка сохранения еды. Попробуйте еще раз.")

@router.message(F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    """Обработка фотографий"""
    await message.answer("📸 Анализирую фото...")
    
    try:
        # Получаем файл фото
        file_info = await message.bot.get_file(message.photo[-1].file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        
        # Обрабатываем через AI
        result = await ai_processor.process_photo_input(
            file_bytes.read(),
            message.from_user.id,
            caption=message.caption
        )
        
        if result.get("success") and result.get("intent") == "log_food_from_photo":
            # Форматируем результат
            photo_data = result["parameters"]
            formatted_data = ai_processor.format_photo_result(photo_data)
            
            # Сохраняем в базу
            await save_food_and_respond(message, formatted_data)
        else:
            await message.answer(
                "❌ Не удалось распознать еду на фото.\n"
                "Попробуйте сделать фото более качественным или опишите еду текстом."
            )
            
    except Exception as e:
        logger.error(f"❌ Error handling photo: {e}")
        await message.answer("❌ Ошибка обработки фото. Попробуйте еще раз.")

@router.message(F.text & ~F.command())
async def handle_text(message: types.Message, state: FSMContext):
    """Обработка текстовых сообщений"""
    # Обрабатываем через AI
    result = await ai_processor.process_text_input(
        message.text,
        message.from_user.id
    )
    
    if result.get("success"):
        intent = result["intent"]
        parameters = result["parameters"]
        
        if intent == "log_food":
            # Форматируем результат распознавания еды
            food_data = ai_processor.format_food_result(parameters)
            
            # Сохраняем еду и отвечаем пользователю
            await save_food_and_respond(message, food_data)
            
            # Проверяем достижения
            achievements = await gamification.check_achievements(
                message.from_user.id, "meal_logged", 
                {
                    "time": datetime.now(),
                    "meal_type": food_data.get("meal_type", ""),
                    "calorie_goal_reached": False  # TODO: проверить после сохранения
                }
            )
            
            # Отправляем уведомления о достижениях
            if achievements:
                await send_achievement_notifications(message, achievements)
                
        elif intent == "clarify":
            # Запрос уточнения
            await message.answer(
                f"❓ {parameters['question']}",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text="📸 Сделать фото еды")],
                        [types.KeyboardButton(text="📊 Мой прогресс")],
                        [types.KeyboardButton(text="🏠 Главное меню")]
                    ],
                    resize_keyboard=True
                )
            )
            
        elif intent == "ai_response":
            # Отправляем ответ от AI ассистента
            await message.answer(
                f"🤖 <b>AI ассистент:</b>\n\n{parameters['response']}",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text="📸 Сделать фото еды")],
                        [types.KeyboardButton(text="📊 Мой прогресс")],
                        [types.KeyboardButton(text="🏠 Главное меню")]
                    ],
                    resize_keyboard=True
                ),
                parse_mode="HTML"
            )
            
        else:
            # Неизвестный интент
            await message.answer(
                f"❓ Не поняла запрос. {parameters.get('suggestion', '')}",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text="📸 Сделать фото еды")],
                        [types.KeyboardButton(text="📊 Мой прогресс")],
                        [types.KeyboardButton(text="🏠 Главное меню")]
                    ],
                    resize_keyboard=True
                )
            )
    else:
        # Ошибка обработки
        error = result.get("parameters", {}).get("error", "Unknown error")
        await message.answer(
            f"❌ Произошла ошибка: {error}",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text="🏠 Главное меню")]
                ],
                resize_keyboard=True
            )
        )
