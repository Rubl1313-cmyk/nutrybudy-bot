"""
handlers/universal.py
Универсальный обработчик всех сообщений с автоопределением намерений через LangChain
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, FoodEntry, DrinkEntry, ActivityEntry
from services.langchain_agent import get_agent
from keyboards.main_menu import get_main_menu

logger = logging.getLogger(__name__)
router = Router()

# Состояния для FSM
class UniversalStates:
    waiting_for_confirmation = "waiting_for_confirmation"

@router.message(~F.command & ~F.photo & ~F.document)
async def universal_message_handler(message: Message, state: FSMContext):
    """
    Универсальный обработчик всех текстовых сообщений
    Автоопределяет намерение через LangChain и выполняет действие
    """
    user_id = message.from_user.id
    user_text = message.text

    # Проверяем, не находится ли пользователь в другом диалоге (AI Ассистент)
    current_state = await state.get_state()
    if current_state == "ai_conversation":
        return  # Пропускаем, это обрабатывает AI Ассистент

    try:
        # Показываем индикатор загрузки
        loading_msg = await message.answer("🤖 Анализирую...")

        # Получаем агента для пользователя
        agent = await get_agent(user_id, state)

        # Обрабатываем сообщение через агента
        result = await agent.process_message(user_text)

        # Удаляем сообщение о загрузке
        await loading_msg.delete()

        # Выводим результат
        await message.answer(result, reply_markup=get_main_menu(), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in universal handler: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при обработке. Попробуйте ещё раз.",
            reply_markup=get_main_menu()
        )

@router.message(F.photo)
async def universal_photo_handler(message: Message, state: FSMContext):
    """
    Обработчик фотографий еды (когда отправляют как фото)
    Распознаёт еду через Vision модель и сохраняет в БД
    """
    user_id = message.from_user.id

    try:
        # Показываем индикатор загрузки
        loading_msg = await message.answer("📸 Анализирую фото...")

        # Получаем фото (берём наилучшее качество - последнее в списке)
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        photo_data = await message.bot.download_file(file_info.file_path)

        # Распознаём еду через Vision модель (напрямую, без агента)
        from services.cloudflare_manager import cf_manager
        from services.ai_processor import ai_processor
        
        result = await cf_manager.parse_food_image(photo_data.read())
        
        await loading_msg.delete()

        if result.get("success"):
            # Обрабатываем результат через ai_processor (расчёт КБЖУ)
            photo_result = await ai_processor.process_photo_input(
                photo_data.read(), 
                user_id
            )
            
            if photo_result.get("success"):
                # Сохраняем в БД
                from services.food_save_service import food_save_service
                from utils.ui_templates import food_entry_card
                from utils.daily_stats import get_daily_stats
                from database.db import get_session
                from database.models import User
                
                params = photo_result["parameters"]
                
                save_result = await food_save_service.save_food_entry(
                    user_id=user_id,
                    food_items=params["ingredients"],
                    meal_type=params["meal_type"],
                    description=params["dish_name"]
                )
                
                if save_result.get("success"):
                    # Получаем статистику и пользователя
                    daily_stats = await get_daily_stats(user_id)
                    with get_session() as session:
                        user = session.query(User).filter(User.telegram_id == user_id).first()
                    
                    food_data = {
                        'description': params["dish_name"],
                        'total_calories': save_result.get('total_calories', 0),
                        'total_protein': save_result.get('total_protein', 0),
                        'total_fat': save_result.get('total_fat', 0),
                        'total_carbs': save_result.get('total_carbs', 0),
                        'meal_type': params["meal_type"]
                    }
                    
                    card_text = food_entry_card(food_data, user, daily_stats)
                    await message.answer(
                        f"✅ <b>Еда сохранена!</b>\n\n{card_text}",
                        reply_markup=get_main_menu(),
                        parse_mode="HTML"
                    )
                else:
                    await message.answer(
                        f"❌ Ошибка сохранения: {save_result.get('error')}",
                        reply_markup=get_main_menu()
                    )
            else:
                await message.answer(
                    "❌ Не удалось распознать еду на фото. Попробуйте отправить другое фото.",
                    reply_markup=get_main_menu()
                )
        else:
            await message.answer(
                f"❌ Ошибка распознавания: {result.get('error')}",
                reply_markup=get_main_menu()
            )

    except Exception as e:
        logger.error(f"Error processing photo: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при обработке фото. Попробуйте ещё раз.",
            reply_markup=get_main_menu()
        )

@router.message(F.document)
async def universal_document_handler(message: Message, state: FSMContext):
    """
    Обработчик файлов (когда отправляют фото как файл)
    Распознаёт еду через Vision модель и сохраняет в БД
    """
    user_id = message.from_user.id

    # Проверяем, это изображение (по MIME типу или расширению)
    document = message.document
    is_image = (
        document.mime_type and document.mime_type.startswith('image/') or
        document.file_name and any(document.file_name.lower().endswith(ext) 
                                   for ext in ['.jpg', '.jpeg', '.png', '.webp'])
    )

    if not is_image:
        return  # Не изображение, пропускаем

    try:
        # Показываем индикатор загрузки
        loading_msg = await message.answer("📸 Анализирую изображение...")

        # Получаем файл
        file_info = await message.bot.get_file(document.file_id)
        photo_data = await message.bot.download_file(file_info.file_path)

        # Распознаём еду через Vision модель
        from services.cloudflare_manager import cf_manager
        from services.ai_processor import ai_processor
        
        result = await cf_manager.parse_food_image(photo_data.read())
        
        await loading_msg.delete()

        if result.get("success"):
            # Обрабатываем результат через ai_processor (расчёт КБЖУ)
            photo_result = await ai_processor.process_photo_input(
                photo_data.read(), 
                user_id
            )
            
            if photo_result.get("success"):
                # Сохраняем в БД
                from services.food_save_service import food_save_service
                from utils.ui_templates import food_entry_card
                from utils.daily_stats import get_daily_stats
                from database.db import get_session
                from database.models import User
                
                params = photo_result["parameters"]
                
                save_result = await food_save_service.save_food_entry(
                    user_id=user_id,
                    food_items=params["ingredients"],
                    meal_type=params["meal_type"],
                    description=params["dish_name"]
                )
                
                if save_result.get("success"):
                    # Получаем статистику и пользователя
                    daily_stats = await get_daily_stats(user_id)
                    with get_session() as session:
                        user = session.query(User).filter(User.telegram_id == user_id).first()
                    
                    food_data = {
                        'description': params["dish_name"],
                        'total_calories': save_result.get('total_calories', 0),
                        'total_protein': save_result.get('total_protein', 0),
                        'total_fat': save_result.get('total_fat', 0),
                        'total_carbs': save_result.get('total_carbs', 0),
                        'meal_type': params["meal_type"]
                    }
                    
                    card_text = food_entry_card(food_data, user, daily_stats)
                    await message.answer(
                        f"✅ <b>Еда сохранена!</b>\n\n{card_text}",
                        reply_markup=get_main_menu(),
                        parse_mode="HTML"
                    )
                else:
                    await message.answer(
                        f"❌ Ошибка сохранения: {save_result.get('error')}",
                        reply_markup=get_main_menu()
                    )
            else:
                await message.answer(
                    "❌ Не удалось распознать еду на фото. Попробуйте отправить другое фото.",
                    reply_markup=get_main_menu()
                )
        else:
            await message.answer(
                f"❌ Ошибка распознавания: {result.get('error')}",
                reply_markup=get_main_menu()
            )

    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при обработке файла. Попробуйте ещё раз.",
            reply_markup=get_main_menu()
        )
