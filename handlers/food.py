"""
Food handling - delegates to AI processor
"""
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from services.ai_processor import ai_processor
from database.db import get_session
from database.models import User
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(types.Message)
async def cmd_log_food(message: types.Message, state: FSMContext, user_id: int = None):
    """Handle food logging command - delegates to AI processor"""
    if user_id is None:
        user_id = message.from_user.id
    
    # Проверяем, есть ли пользователь в базе
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Сначала создайте профиль через /set_profile\n\n"
                "Это поможет мне рассчитывать ваши нормы КБЖУ и давать персонализированные рекомендации.",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text="/set_profile")],
                        [types.KeyboardButton(text="🏠 Главное меню")]
                    ],
                    resize_keyboard=True
                )
            )
            return
    
    # Используем AI процессор для обработки еды
    try:
        # Если есть фото, обрабатываем через AI
        if message.photo:
            await message.answer("📸 Анализирую фото еды...")
            
            # Получаем файл фото
            file_info = await message.bot.get_file(message.photo[-1].file_id)
            file_bytes = await message.bot.download_file(file_info.file_path)
            
            # Обрабатываем через AI
            result = await ai_processor.process_photo_input(
                user_id=user_id,
                image_bytes=file_bytes.read(),
                context="food_logging"
            )
            
            if result.get("success"):
                food_data = result.get("data", {})
                await message.answer(
                    f"✅ <b>Распознано:</b>\n"
                    f"🍽️ {food_data.get('description', 'Неизвестное блюдо')}\n"
                    f"🔥 {food_data.get('calories', 0)} ккал\n"
                    f"🥩 {food_data.get('protein', 0)}г\n"
                    f"🥑 {food_data.get('fat', 0)}г\n"
                    f"🍚 {food_data.get('carbs', 0)}г\n\n"
                    f"💡 Записать в дневник?",
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                types.InlineKeyboardButton(text="✅ Да", callback_data="confirm_food"),
                                types.InlineKeyboardButton(text="❌ Нет", callback_data="cancel_food")
                            ]
                        ]
                    ),
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    "❌ Не удалось распознать еду на фото.\n"
                    "Попробуйте сделать фото более качественным или опишите еду текстом."
                )
        
        # Если есть текст, обрабатываем через AI
        elif message.text and message.text != "/log_food":
            await message.answer("🤖 Анализирую описание еды...")
            
            result = await ai_processor.process_text_input(
                user_id=user_id,
                text=message.text,
                context="food_logging"
            )
            
            if result.get("success"):
                food_data = result.get("data", {})
                await message.answer(
                    f"✅ <b>Распознано:</b>\n"
                    f"🍽️ {food_data.get('description', 'Неизвестное блюдо')}\n"
                    f"🔥 {food_data.get('calories', 0)} ккал\n"
                    f"🥩 {food_data.get('protein', 0)}г\n"
                    f"🥑 {food_data.get('fat', 0)}г\n"
                    f"🍚 {food_data.get('carbs', 0)}г\n\n"
                    f"💡 Записать в дневник?",
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                types.InlineKeyboardButton(text="✅ Да", callback_data="confirm_food"),
                                types.InlineKeyboardButton(text="❌ Нет", callback_data="cancel_food")
                            ]
                        ]
                    ),
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    "❌ Не удалось распознать еду из текста.\n"
                    "Попробуйте описать более подробно, например: '200г куриной грудки с рисом'"
                )
        
        # Если это команда, показываем инструкции
        else:
            await message.answer(
                "🍽️ <b>Логирование еды:</b>\n\n"
                "📸 <b>Способ 1:</b> Отправьте фото блюда\n"
                "🤖 <b>Способ 2:</b> Напишите что вы съели\n\n"
                "💡 <b>Примеры:</b>\n"
                "• '200г гречки с котлетой'\n"
                "• 'овсянка на молоке с бананом'\n"
                "• 'салат цезарь с курицей'\n\n"
                "Я автоматически распознаю продукты и рассчитаю КБЖУ!",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text="🏠 Главное меню")]
                    ],
                    resize_keyboard=True
                ),
                parse_mode="HTML"
            )
    
    except Exception as e:
        logger.error(f"Error in food logging: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке еды. Попробуйте еще раз."
        )