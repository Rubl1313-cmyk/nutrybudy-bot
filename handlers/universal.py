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

@router.message(F.photo & ~F.document)
async def universal_photo_handler(message: Message, state: FSMContext):
    """
    Обработчик фотографий еды (когда отправляют как фото, НЕ как файл)
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
        
        # Читаем байты ОДИН раз и сохраняем
        photo_bytes = photo_data.read()

        # Распознаём еду через Vision модель (напрямую, без агента)
        from services.cloudflare_manager import cf_manager
        from services.ai_processor import ai_processor

        result = await cf_manager.parse_food_image(photo_bytes)

        await loading_msg.delete()

        if result.get("success"):
            # Используем результат напрямую (без повторного вызова parse_food_image)
            data = result.get("analysis", {})
            ingredients = data.get("ingredients", [])
            
            # Получаем красивое название блюда от Vision модели
            dish_name = data.get("dish_name", "Неизвестное блюдо")
            
            # Формируем список ингредиентов для отображения
            ingredients_list = []
            for ing in ingredients:
                name = ing.get("name", "")
                weight = ing.get("weight_grams", 0)
                if name and weight > 0:
                    ingredients_list.append(f"• {name} ({weight}г)")
            
            ingredients_text = "\n".join(ingredients_list) if ingredients_list else ""

            # Рассчитываем КБЖУ на основе ингредиентов
            nutrition_db = {
                # Английские названия
                "chicken": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
                "chicken breast": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
                "beef": {"calories": 250, "protein": 26, "fat": 15, "carbs": 0},
                "fish": {"calories": 206, "protein": 22, "fat": 12, "carbs": 0},
                "salmon": {"calories": 208, "protein": 20, "fat": 13, "carbs": 0},
                "tuna": {"calories": 144, "protein": 23, "fat": 5, "carbs": 0},
                "egg": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
                "eggs": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
                "rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
                "pasta": {"calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
                "potato": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
                "potatoes": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
                "bread": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
                "vegetable": {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5},
                "vegetables": {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5},
                "tomato": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
                "cucumber": {"calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
                "lettuce": {"calories": 15, "protein": 1.4, "fat": 0.2, "carbs": 2.9},
                "cabbage": {"calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 6},
                "carrot": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
                "broccoli": {"calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
                "oil": {"calories": 884, "protein": 0, "fat": 100, "carbs": 0},
                "butter": {"calories": 717, "protein": 0.9, "fat": 81, "carbs": 0.1},
                "cheese": {"calories": 402, "protein": 25, "fat": 33, "carbs": 1.3},
                "fruit": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                "apple": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                "banana": {"calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23},
                # Русские названия (для Vision модели)
                "курица": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
                "куриная грудка": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
                "говядина": {"calories": 250, "protein": 26, "fat": 15, "carbs": 0},
                "рыба": {"calories": 206, "protein": 22, "fat": 12, "carbs": 0},
                "лосось": {"calories": 208, "protein": 20, "fat": 13, "carbs": 0},
                "тунец": {"calories": 144, "protein": 23, "fat": 5, "carbs": 0},
                "яйцо": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
                "яйца": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
                "рис": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
                "паста": {"calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
                "картофель": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
                "хлеб": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
                "овощи": {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5},
                "томаты": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
                "помидоры": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
                "огурец": {"calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
                "салат": {"calories": 15, "protein": 1.4, "fat": 0.2, "carbs": 2.9},
                "капуста": {"calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 6},
                "морковь": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
                "брокколи": {"calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
                "масло": {"calories": 884, "protein": 0, "fat": 100, "carbs": 0},
                "сливочное масло": {"calories": 717, "protein": 0.9, "fat": 81, "carbs": 0.1},
                "сыр": {"calories": 402, "protein": 25, "fat": 33, "carbs": 1.3},
                "фрукты": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                "яблоко": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                "банан": {"calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23},
                "свекла": {"calories": 43, "protein": 1.6, "fat": 0.2, "carbs": 10},
                "лук": {"calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9.3},
                "чеснок": {"calories": 149, "protein": 6.4, "fat": 0.5, "carbs": 33},
                "сметана": {"calories": 198, "protein": 2.4, "fat": 20, "carbs": 4.6},
                "мясо": {"calories": 250, "protein": 26, "fat": 15, "carbs": 0},
                "свинина": {"calories": 265, "protein": 27, "fat": 17, "carbs": 0},
                "баранина": {"calories": 294, "protein": 25, "fat": 21, "carbs": 0},
                "репа": {"calories": 28, "protein": 0.9, "fat": 0.1, "carbs": 6},
                "перец": {"calories": 31, "protein": 1, "fat": 0.3, "carbs": 6},
                "паприка": {"calories": 282, "protein": 14, "fat": 13, "carbs": 54},
                "соль": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0},
                "черный перец": {"calories": 251, "protein": 10, "fat": 3.3, "carbs": 64},
                "зелень": {"calories": 36, "protein": 3, "fat": 0.8, "carbs": 6},
            }

            total_calories = 0
            total_protein = 0
            total_fat = 0
            total_carbs = 0

            for ingredient in ingredients:
                name = ingredient.get("name", "").lower()
                weight = ingredient.get("weight_grams", 0)

                nutrition = None
                for key, value in nutrition_db.items():
                    if key.lower() in name or name in key.lower():
                        nutrition = value
                        break

                if not nutrition:
                    ing_type = ingredient.get("type", "")
                    if "protein" in ing_type:
                        nutrition = {"calories": 150, "protein": 25, "fat": 5, "carbs": 0}
                    elif "carb" in ing_type:
                        nutrition = {"calories": 120, "protein": 3, "fat": 0.5, "carbs": 25}
                    elif "vegetable" in ing_type:
                        nutrition = {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5}
                    elif "fat" in ing_type:
                        nutrition = {"calories": 800, "protein": 0, "fat": 90, "carbs": 0}
                    elif "herb" in ing_type or "spice" in ing_type or "salt" in ing_type:
                        nutrition = {"calories": 5, "protein": 0.2, "fat": 0.1, "carbs": 1}
                    elif "dairy" in ing_type:
                        nutrition = {"calories": 100, "protein": 5, "fat": 5, "carbs": 5}
                    else:
                        nutrition = {"calories": 100, "protein": 5, "fat": 3, "carbs": 15}

                total_calories += (nutrition["calories"] * weight) / 100
                total_protein += (nutrition["protein"] * weight) / 100
                total_fat += (nutrition["fat"] * weight) / 100
                total_carbs += (nutrition["carbs"] * weight) / 100

            # Определяем meal_type из category
            category = data.get("category", "main")
            meal_type_map = {
                "breakfast": "breakfast",
                "lunch": "main",
                "dinner": "main",
                "main": "main",
                "salad": "snack",
                "side": "side",
                "snack": "snack",
                "dessert": "dessert",
                "soup": "main",
                "drink": "drink"
            }
            meal_type = meal_type_map.get(category, "main")

            # Сохраняем в БД
            from services.food_save_service import food_save_service
            from utils.ui_templates import food_entry_card
            from utils.daily_stats import get_daily_stats
            from database.db import get_session
            from database.models import User
            from services.dish_db import dish_identifier

            # Определяем блюдо по ингредиентам через базу данных
            # Преобразуем список словарей в список строк (названий ингредиентов)
            ingredient_names = [ing.get("name", "") for ing in ingredients if ing.get("name")]
            dish_result = dish_identifier.identify_dish(ingredient_names)
            
            # Используем красивое название от Vision модели как основное
            # База данных используется только для уточнения КБЖУ
            if dish_result.get("success"):
                dish_data = dish_result.get("dish", {})
                nutrition_per_100 = dish_data.get("nutrition_per_100", {})
                
                # Рассчитываем КБЖУ на основе веса
                total_weight = sum(ing.get("weight_grams", 100) for ing in ingredients)
                factor = total_weight / 100.0
                
                total_calories = nutrition_per_100.get("calories", 0) * factor
                total_protein = nutrition_per_100.get("protein", 0) * factor
                total_fat = nutrition_per_100.get("fat", 0) * factor
                total_carbs = nutrition_per_100.get("carbs", 0) * factor

            # Сохраняем в БД с рассчитанными КБЖУ
            save_result = await food_save_service.save_food_to_db(
                user_id=user_id,
                food_items=[{
                    "name": dish_name,
                    "calories": total_calories,
                    "protein": total_protein,
                    "fat": total_fat,
                    "carbs": total_carbs,
                    "quantity": sum(ing.get("weight_grams", 100) for ing in ingredients),
                    "unit": "г"
                }],
                meal_type=meal_type
            )

            if save_result.get("success"):
                # Получаем статистику и пользователя
                daily_stats = await get_daily_stats(user_id)
                async with get_session() as session:
                    user = await session.execute(select(User).where(User.telegram_id == user_id))
                    user = user.scalar_one_or_none()

                # Формируем красивое сообщение с блюдом и ингредиентами
                food_data = {
                    'description': dish_name,
                    'total_calories': total_calories,
                    'total_protein': total_protein,
                    'total_fat': total_fat,
                    'total_carbs': total_carbs,
                    'meal_type': meal_type
                }

                card_text = food_entry_card(food_data, user, daily_stats)
                
                # Добавляем список ингредиентов
                full_message = f"✅ <b>Еда сохранена!</b>\n\n{card_text}"
                if ingredients_text:
                    full_message += f"\n\n📋 <b>Состав:</b>\n{ingredients_text}"
                
                await message.answer(
                    full_message,
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
        
        # Логгируем информацию о файле
        logger.info(f"[DOCUMENT] File ID: {document.file_id}")
        logger.info(f"[DOCUMENT] File name: {document.file_name}")
        logger.info(f"[DOCUMENT] MIME type: {document.mime_type}")
        logger.info(f"[DOCUMENT] File size: {file_info.file_size}")
        
        photo_data = await message.bot.download_file(file_info.file_path)
        
        # Логгируем размер загруженных данных
        photo_bytes = photo_data.read()
        logger.info(f"[DOCUMENT] Downloaded data size: {len(photo_bytes)} bytes")

        # Распознаём еду через Vision модель
        from services.cloudflare_manager import cf_manager
        from services.ai_processor import ai_processor
        
        result = await cf_manager.parse_food_image(photo_bytes)
        
        await loading_msg.delete()

        if result.get("success"):
            # Используем результат напрямую (без повторного вызова parse_food_image)
            data = result.get("analysis", {})
            ingredients = data.get("ingredients", [])
            
            # Получаем красивое название блюда от Vision модели
            dish_name = data.get("dish_name", "Неизвестное блюдо")
            
            # Формируем список ингредиентов для отображения
            ingredients_list = []
            for ing in ingredients:
                name = ing.get("name", "")
                weight = ing.get("weight_grams", 0)
                if name and weight > 0:
                    ingredients_list.append(f"• {name} ({weight}г)")
            
            ingredients_text = "\n".join(ingredients_list) if ingredients_list else ""

            # Рассчитываем КБЖУ на основе ингредиентов
            nutrition_db = {
                "chicken": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
                "chicken breast": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
                "beef": {"calories": 250, "protein": 26, "fat": 15, "carbs": 0},
                "fish": {"calories": 206, "protein": 22, "fat": 12, "carbs": 0},
                "salmon": {"calories": 208, "protein": 20, "fat": 13, "carbs": 0},
                "tuna": {"calories": 144, "protein": 23, "fat": 5, "carbs": 0},
                "egg": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
                "eggs": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
                "rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
                "pasta": {"calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
                "potato": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
                "potatoes": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
                "bread": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
                "vegetable": {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5},
                "vegetables": {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5},
                "tomato": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
                "cucumber": {"calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
                "lettuce": {"calories": 15, "protein": 1.4, "fat": 0.2, "carbs": 2.9},
                "cabbage": {"calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 6},
                "carrot": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
                "broccoli": {"calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
                "oil": {"calories": 884, "protein": 0, "fat": 100, "carbs": 0},
                "butter": {"calories": 717, "protein": 0.9, "fat": 81, "carbs": 0.1},
                "cheese": {"calories": 402, "protein": 25, "fat": 33, "carbs": 1.3},
                "fruit": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                "apple": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
                "banana": {"calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23},
            }

            total_calories = 0
            total_protein = 0
            total_fat = 0
            total_carbs = 0

            for ingredient in ingredients:
                name = ingredient.get("name", "").lower()
                weight = ingredient.get("weight_grams", 0)

                nutrition = None
                for key, value in nutrition_db.items():
                    if key in name:
                        nutrition = value
                        break

                if not nutrition:
                    ing_type = ingredient.get("type", "")
                    if "protein" in ing_type:
                        nutrition = {"calories": 150, "protein": 25, "fat": 5, "carbs": 0}
                    elif "carb" in ing_type:
                        nutrition = {"calories": 120, "protein": 3, "fat": 0.5, "carbs": 25}
                    elif "vegetable" in ing_type:
                        nutrition = {"calories": 25, "protein": 1, "fat": 0.3, "carbs": 5}
                    elif "fat" in ing_type:
                        nutrition = {"calories": 800, "protein": 0, "fat": 90, "carbs": 0}
                    else:
                        nutrition = {"calories": 100, "protein": 5, "fat": 3, "carbs": 15}

                total_calories += (nutrition["calories"] * weight) / 100
                total_protein += (nutrition["protein"] * weight) / 100
                total_fat += (nutrition["fat"] * weight) / 100
                total_carbs += (nutrition["carbs"] * weight) / 100

            # Определяем meal_type из category
            category = data.get("category", "main")
            meal_type_map = {
                "breakfast": "breakfast",
                "lunch": "main",
                "dinner": "main",
                "main": "main",
                "salad": "snack",
                "side": "side",
                "snack": "snack",
                "dessert": "dessert",
                "soup": "main",
                "drink": "drink"
            }
            meal_type = meal_type_map.get(category, "main")

            # Сохраняем в БД
            from services.food_save_service import food_save_service
            from utils.ui_templates import food_entry_card
            from utils.daily_stats import get_daily_stats
            from database.db import get_session
            from database.models import User
            from services.dish_db import dish_identifier

            # Определяем блюдо по ингредиентам через базу данных
            # Преобразуем список словарей в список строк (названий ингредиентов)
            ingredient_names = [ing.get("name", "") for ing in ingredients if ing.get("name")]
            dish_result = dish_identifier.identify_dish(ingredient_names)
            
            # Используем красивое название от Vision модели как основное
            # База данных используется только для уточнения КБЖУ
            if dish_result.get("success"):
                dish_data = dish_result.get("dish", {})
                nutrition_per_100 = dish_data.get("nutrition_per_100", {})
                
                # Рассчитываем КБЖУ на основе веса
                total_weight = sum(ing.get("weight_grams", 100) for ing in ingredients)
                factor = total_weight / 100.0
                
                total_calories = nutrition_per_100.get("calories", 0) * factor
                total_protein = nutrition_per_100.get("protein", 0) * factor
                total_fat = nutrition_per_100.get("fat", 0) * factor
                total_carbs = nutrition_per_100.get("carbs", 0) * factor

            # Сохраняем в БД с рассчитанными КБЖУ
            save_result = await food_save_service.save_food_to_db(
                user_id=user_id,
                food_items=[{
                    "name": dish_name,
                    "calories": total_calories,
                    "protein": total_protein,
                    "fat": total_fat,
                    "carbs": total_carbs,
                    "quantity": sum(ing.get("weight_grams", 100) for ing in ingredients),
                    "unit": "г"
                }],
                meal_type=meal_type
            )

            if save_result.get("success"):
                # Получаем статистику и пользователя
                daily_stats = await get_daily_stats(user_id)
                async with get_session() as session:
                    user = await session.execute(select(User).where(User.telegram_id == user_id))
                    user = user.scalar_one_or_none()

                # Формируем красивое сообщение с блюдом и ингредиентами
                food_data = {
                    'description': dish_name,
                    'total_calories': total_calories,
                    'total_protein': total_protein,
                    'total_fat': total_fat,
                    'total_carbs': total_carbs,
                    'meal_type': meal_type
                }

                card_text = food_entry_card(food_data, user, daily_stats)
                
                # Добавляем список ингредиентов
                full_message = f"✅ <b>Еда сохранена!</b>\n\n{card_text}"
                if ingredients_text:
                    full_message += f"\n\n📋 <b>Состав:</b>\n{ingredients_text}"
                
                await message.answer(
                    full_message,
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
                f"❌ Ошибка распознавания: {result.get('error')}",
                reply_markup=get_main_menu()
            )

    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при обработке файла. Попробуйте ещё раз.",
            reply_markup=get_main_menu()
        )
