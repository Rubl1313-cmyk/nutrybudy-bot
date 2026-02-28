"""
AI Handlers для NutriBuddy
Обработка фото, голоса и других AI-функций через Cloudflare Workers AI
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
import json

from services.cloudflare_ai import analyze_food_image, transcribe_audio, generate_recipe
from services.food_api import search_food
from keyboards.inline import get_food_selection_keyboard, get_confirmation_keyboard
from utils.states import FoodStates
from database.db import get_session
from database.models import User, Meal, FoodItem
from datetime import datetime

# ✅ ВАЖНО: Создаём Router для этого модуля
router = Router()

logger = logging.getLogger(__name__)


# =============================================================================
# 📸 ОБРАБОТКА ФОТО (включая отправку как документ)
# =============================================================================

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обработка фото еды для анализа через Cloudflare AI"""
    try:
        # Берём фото наилучшего качества
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        await message.answer("🔍 Анализирую изображение через Cloudflare AI...")
        
        # Анализ через UForm-Gen2
        description = await analyze_food_image(
            file_data,
            prompt="Опиши еду на этом изображении. Укажи название блюда и основные ингредиенты. Отвечай кратко на русском."
        )
        
        if not description:
            await message.answer(
                "❌ Не удалось распознать изображение.\n\n"
                "Попробуйте:\n"
                "• Отправить более чёткое фото\n"
                "• Ввести название блюда вручную через /log_food"
            )
            return
        
        # Сохраняем описание для дальнейшего использования
        await state.update_data(ai_description=description, photo_file_id=photo.file_id)
        
        # Пытаемся найти продукты в базе OpenFoodFacts
        foods = await search_food(description)
        
        if foods:
            await message.answer(
                f"🧠 <b>Распознано:</b> {description}\n\n"
                f"Выберите наиболее подходящий продукт:",
                reply_markup=get_food_selection_keyboard(foods),
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.selecting_food)
            await state.update_data(foods=foods)
        else:
            await message.answer(
                f"🧠 Описание: <i>{description}</i>\n\n"
                f"Не удалось найти точное совпадение в базе продуктов.\n"
                f"Введите название блюда вручную:",
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.manual_food_name)
            
    except Exception as e:
        logger.error(f"Photo handling error: {e}", exc_info=True)
        await message.answer("❌ Ошибка при анализе фото. Попробуйте позже.")


@router.message(F.document)
async def handle_document(message: Message, state: FSMContext):
    """
    Обработка файлов, отправленных как документ (включая фото).
    Telegram иногда отправляет фото как document, если пользователь выбрал "Отправить как файл".
    """
    doc = message.document
    
    # Проверяем, что это изображение
    if not (doc.mime_type and doc.mime_type.startswith('image/')):
        return  # Игнорируем не-изображения (PDF, ZIP и т.д.)
    
    try:
        file_info = await message.bot.get_file(doc.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        await message.answer("🔍 Анализирую изображение (отправлено как файл)...")
        
        description = await analyze_food_image(
            file_data,
            prompt="Опиши еду на этом изображении. Укажи название блюда и основные ингредиенты. Отвечай кратко на русском."
        )
        
        if not description:
            await message.answer("❌ Не удалось распознать изображение.")
            return
        
        await state.update_data(ai_description=description)
        foods = await search_food(description)
        
        if foods:
            await message.answer(
                f"🧠 <b>Распознано:</b> {description}\n\n"
                f"Выберите продукт:",
                reply_markup=get_food_selection_keyboard(foods),
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.selecting_food)
            await state.update_data(foods=foods)
        else:
            await message.answer(
                f"🧠 Описание: {description}\n\n"
                f"Введите название блюда вручную:"
            )
            await state.set_state(FoodStates.manual_food_name)
            
    except Exception as e:
        logger.error(f"Document handling error: {e}", exc_info=True)
        await message.answer("❌ Ошибка при обработке файла.")


# =============================================================================
# 🎤 ОБРАБОТКА ГОЛОСОВЫХ СООБЩЕНИЙ (Whisper)
# =============================================================================

@router.message(F.voice)
async def handle_voice(message: Message, state: FSMContext):
    """Распознавание голосовых сообщений через Whisper"""
    try:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        await message.answer("🎤 Распознаю речь через Cloudflare AI...")
        
        text = await transcribe_audio(file_data)
        
        if not text:
            await message.answer(
                "❌ Не удалось распознать речь.\n\n"
                "Попробуйте:\n"
                "• Говорить чётче\n"
                "• Отправить текст вручную"
            )
            return
        
        await message.answer(
            f"📝 <b>Распознано:</b>\n<i>{text}</i>",
            parse_mode="HTML"
        )
        
        # Сохраняем текст для дальнейшего использования
        await state.update_data(voice_text=text)
        
        # Предлагаем действия с распознанным текстом
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🍽️ Записать как приём пищи")],
                [KeyboardButton(text="📋 Добавить в список покупок")],
                [KeyboardButton(text="📖 Сгенерировать рецепт")],
                [KeyboardButton(text="❌ Отмена")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "💡 <b>Что сделать с этим текстом?</b>",
            reply_markup=kb,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Voice handling error: {e}", exc_info=True)
        await message.answer("❌ Ошибка распознавания речи. Попробуйте ещё раз.")


# =============================================================================
# 🔄 ОБРАБОТКА ДЕЙСТВИЙ С РАСПОЗНАННЫМ ТЕКСТОМ
# =============================================================================

@router.message(F.text == "🍽️ Записать как приём пищи")
async def voice_to_food(message: Message, state: FSMContext):
    """Использовать распознанный голос для записи приёма пищи"""
    data = await state.get_data()
    text = data.get('voice_text')
    
    if not text:
        await message.answer("❌ Нет распознанного текста. Отправьте голосовое сообщение.")
        return
    
    # Запускаем процесс записи еды с предзаполненным названием
    await state.update_data(manual_food_name=text)
    await state.set_state(FoodStates.entering_weight)
    await message.answer(f"🍽️ <b>{text}</b>\n\nВведите вес в граммах:", parse_mode="HTML")


@router.message(F.text == "📋 Добавить в список покупок")
async def voice_to_shopping(message: Message, state: FSMContext):
    """Добавить распознанный текст в список покупок"""
    from database.models import ShoppingList, ShoppingItem
    from sqlalchemy import select
    
    data = await state.get_data()
    text = data.get('voice_text')
    
    if not text:
        await message.answer("❌ Нет распознанного текста.")
        return
    
    user_id = message.from_user.id
    
    async with get_session() as session:
        # Получаем или создаём список "Покупки"
        result = await session.execute(
            select(ShoppingList).where(
                ShoppingList.user_id == user_id,
                ShoppingList.name == "Покупки",
                ShoppingList.is_archived == False
            )
        )
        shopping_list = result.scalar_one_or_none()
        
        if not shopping_list:
            shopping_list = ShoppingList(user_id=user_id, name="Покупки")
            session.add(shopping_list)
            await session.flush()
        
        # Добавляем товар
        item = ShoppingItem(
            list_id=shopping_list.id,
            name=text,
            quantity="1",
            added_by=user_id
        )
        session.add(item)
        await session.commit()
    
    await state.update_data(voice_text=None)
    await message.answer(f"✅ <i>{text}</i> добавлено в список покупок!", parse_mode="HTML")


@router.message(F.text == "📖 Сгенерировать рецепт")
async def voice_to_recipe(message: Message, state: FSMContext):
    """Сгенерировать рецепт на основе распознанных ингредиентов"""
    data = await state.get_data()
    text = data.get('voice_text')
    
    if not text:
        await message.answer("❌ Нет распознанного текста.")
        return
    
    await message.answer("🧑‍🍳 <b>Генерирую рецепт...</b>\nЭто займёт ~10 секунд.", parse_mode="HTML")
    
    recipe = await generate_recipe(text)
    
    if recipe:
        await message.answer(
            f"🍽️ <b>Ваш рецепт:</b>\n\n{recipe}",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Не удалось сгенерировать рецепт. Попробуйте позже.")
    
    await state.update_data(voice_text=None)


@router.message(F.text == "❌ Отмена")
async def cancel_voice_action(message: Message, state: FSMContext):
    """Отмена действия с голосовым сообщением"""
    await state.update_data(voice_text=None)
    await message.answer("❌ Отменено.")


# =============================================================================
# 🧠 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

async def estimate_calories_from_description(description: str, weight: float) -> dict:
    """
    Пытается оценить КБЖУ на основе описания еды (упрощённая логика).
    В будущем можно заменить на вызов LLM для более точной оценки.
    """
    # Упрощённая эвристика (можно улучшить)
    description_lower = description.lower()
    
    # Базовые значения на 100г для разных категорий
    defaults = {
        'куриц': {'cal': 165, 'prot': 31, 'fat': 3.6, 'carb': 0},
        'рис': {'cal': 130, 'prot': 2.7, 'fat': 0.3, 'carb': 28},
        'овощ': {'cal': 25, 'prot': 1.2, 'fat': 0.2, 'carb': 5},
        'паст': {'cal': 131, 'prot': 5, 'fat': 1.1, 'carb': 25},
        'рыб': {'cal': 206, 'prot': 22, 'fat': 12, 'carb': 0},
        'яиц': {'cal': 155, 'prot': 13, 'fat': 11, 'carb': 1.1},
        'сыр': {'cal': 404, 'prot': 25, 'fat': 33, 'carb': 1.3},
        'хлеб': {'cal': 265, 'prot': 9, 'fat': 3.2, 'carb': 49},
    }
    
    # Поиск совпадений
    for keyword, values in defaults.items():
        if keyword in description_lower:
            multiplier = weight / 100
            return {
                'calories': round(values['cal'] * multiplier, 1),
                'protein': round(values['prot'] * multiplier, 1),
                'fat': round(values['fat'] * multiplier, 1),
                'carbs': round(values['carb'] * multiplier, 1)
            }
    
    # Дефолтные значения, если ничего не найдено
    return {
        'calories': round(150 * weight / 100, 1),
        'protein': round(8 * weight / 100, 1),
        'fat': round(7 * weight / 100, 1),
        'carbs': round(20 * weight / 100, 1)
    }
