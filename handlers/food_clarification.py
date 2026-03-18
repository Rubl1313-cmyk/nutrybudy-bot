# handlers/food_clarification.py
import logging
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.food_api import get_product_variants
from services.ai_processor import ai_processor
from services.soup_service import is_soup, save_soup
from services.soup_service import save_drink
from utils.safe_parser import safe_parse_float
from utils.premium_templates import loading_card, error_card
from utils.ui_templates import ProgressBar

logger = logging.getLogger(__name__)
router = Router()

class FoodClarificationStates(StatesGroup):
    waiting_for_product_choice = State()   # ожидание выбора варианта продукта
    waiting_for_weight = State()           # ожидание ввода веса
    waiting_for_manual_name = State()      # ручной ввод названия

@router.message(F.text, flags={"rate_limit": "food"})
async def handle_food_text(message: Message, state: FSMContext):
    """Начало обработки текста как еды (вызывается из ai_handler, если AI вернул food_items)."""
    user_id = message.from_user.id
    text = message.text

    # 1. Получаем от AI список продуктов (как раньше)
    result = await ai_processor.process_text_input(text, user_id)
    
    if not result or not result.get('food_items'):
        await message.answer("❌ Не удалось распознать продукты. Попробуйте еще раз.")
        return
    
    food_items = result['food_items']
    
    # 2. Если только один продукт - сразу запрашиваем вес
    if len(food_items) == 1:
        await state.set_state(FoodClarificationStates.waiting_for_weight)
        await state.update_data(
            selected_product=food_items[0],
            original_text=text
        )
        
        product = food_items[0]
        text = f"🍽️ <b>Определен продукт:</b> {product['name']}\n\n"
        text += f"📊 <b>Пищевая ценность на 100г:</b>\n"
        text += f"• Калории: {product['calories']} ккал\n"
        text += f"• Белки: {product['protein']} г\n"
        text += f"• Жиры: {product['fat']} г\n"
        text += f"• Углеводы: {product['carbs']} г\n\n"
        text += "⚖️ <b>Введите вес в граммах:</b>"
        
        await message.answer(text)
        return
    
    # 3. Если несколько продуктов - предлагаем выбрать
    await state.set_state(FoodClarificationStates.waiting_for_product_choice)
    await state.update_data(
        food_items=food_items,
        original_text=text
    )
    
    # Формируем клавиатуру с вариантами
    builder = InlineKeyboardBuilder()
    
    text = "🤔 <b>Найдено несколько вариантов:</b>\n\n"
    
    for i, item in enumerate(food_items, 1):
        text += f"{i}. {item['name']}\n"
        text += f"   {item['calories']} ккал на 100г\n\n"
        
        builder.add(types.InlineKeyboardButton(
            text=f"{i}. {item['name']}",
            callback_data=f"select_product:{i-1}"
        ))
    
    builder.add(types.InlineKeyboardButton(
        text="✏️ Ввести вручную",
        callback_data="manual_input"
    ))
    
    builder.adjust(1)  # По одной кнопке в строке
    
    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("select_product:"))
async def handle_product_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора продукта из списка"""
    data = await state.get_data()
    food_items = data['food_items']
    
    # Получаем индекс выбранного продукта
    product_index = int(callback.data.split(":")[1])
    selected_product = food_items[product_index]
    
    # Переходим к вводу веса
    await state.set_state(FoodClarificationStates.waiting_for_weight)
    await state.update_data(selected_product=selected_product)
    
    text = f"🍽️ <b>Выбран продукт:</b> {selected_product['name']}\n\n"
    text += f"📊 <b>Пищевая ценность на 100г:</b>\n"
    text += f"• Калории: {selected_product['calories']} ккал\n"
    text += f"• Белки: {selected_product['protein']} г\n"
    text += f"• Жиры: {selected_product['fat']} г\n"
    text += f"• Углеводы: {selected_product['carbs']} г\n\n"
    text += "⚖️ <b>Введите вес в граммах:</b>"
    
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "manual_input")
async def handle_manual_input(callback: CallbackQuery, state: FSMContext):
    """Переход к ручному вводу продукта"""
    await state.set_state(FoodClarificationStates.waiting_for_manual_name)
    
    text = "✏️ <b>Ручной ввод продукта</b>\n\n"
    text += "Введите название продукта:"
    
    await callback.message.edit_text(text)
    await callback.answer()

@router.message(FoodClarificationStates.waiting_for_manual_name)
async def handle_manual_product_name(message: Message, state: FSMContext):
    """Обработка ручного ввода названия продукта"""
    product_name = message.text.strip()
    
    if len(product_name) < 2:
        await message.answer("❌ Слишком короткое название. Попробуйте еще раз:")
        return
    
    # Ищем варианты продукта
    try:
        variants = await get_product_variants(product_name)
        
        if not variants:
            await message.answer("❌ Продукт не найден. Попробуйте другое название:")
            return
        
        if len(variants) == 1:
            # Сразу переходим к вводу веса
            product = variants[0]
            await state.set_state(FoodClarificationStates.waiting_for_weight)
            await state.update_data(selected_product=product)
            
            text = f"🍽️ <b>Найден продукт:</b> {product['name']}\n\n"
            text += f"📊 <b>Пищевая ценность на 100г:</b>\n"
            text += f"• Калории: {product['calories']} ккал\n"
            text += f"• Белки: {product['protein']} г\n"
            text += f"• Жиры: {product['fat']} г\n"
            text += f"• Углеводы: {product['carbs']} г\n\n"
            text += "⚖️ <b>Введите вес в граммах:</b>"
            
            await message.answer(text)
        else:
            # Предлагаем выбрать из вариантов
            await state.set_state(FoodClarificationStates.waiting_for_product_choice)
            await state.update_data(food_items=variants)
            
            builder = InlineKeyboardBuilder()
            text = "🤔 <b>Найдено несколько вариантов:</b>\n\n"
            
            for i, item in enumerate(variants, 1):
                text += f"{i}. {item['name']}\n"
                text += f"   {item['calories']} ккал на 100г\n\n"
                
                builder.add(types.InlineKeyboardButton(
                    text=f"{i}. {item['name']}",
                    callback_data=f"select_product:{i-1}"
                ))
            
            builder.adjust(1)
            await message.answer(text, reply_markup=builder.as_markup())
            
    except Exception as e:
        logger.error(f"Error searching product: {e}")
        await message.answer("❌ Произошла ошибка поиска. Попробуйте еще раз:")

@router.message(FoodClarificationStates.waiting_for_weight)
async def handle_weight_input(message: Message, state: FSMContext):
    """Обработка ввода веса продукта"""
    weight_text = message.text.strip()
    
    # Парсим вес
    weight = safe_parse_float(weight_text)
    
    if weight is None or weight <= 0:
        await message.answer("❌ Неверный вес. Введите положительное число (например: 100, 250.5):")
        return
    
    if weight > 10000:  # 10 кг максимум
        await message.answer("❌ Слишком большой вес. Максимум 10000 г. Попробуйте еще раз:")
        return
    
    # Получаем данные о продукте
    data = await state.get_data()
    selected_product = data['selected_product']
    original_text = data.get('original_text', '')
    
    # Рассчитываем питательную ценность
    multiplier = weight / 100
    calories = selected_product['calories'] * multiplier
    protein = selected_product['protein'] * multiplier
    fat = selected_product['fat'] * multiplier
    carbs = selected_product['carbs'] * multiplier
    
    # Сохраняем в базу данных
    try:
        from database.db import get_session
        from database.models import User, FoodEntry
        
        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await message.answer(
                    "❌ Сначала настройте профиль с помощью /set_profile"
                )
                await state.clear()
                return
            
            # Определяем тип приема пищи
            meal_type = await determine_meal_type(message.date.hour)
            
            # Создаем запись о еде
            food_entry = FoodEntry(
                user_id=user.telegram_id,
                food_name=selected_product['name'],
                calories=calories,
                protein=protein,
                fat=fat,
                carbs=carbs,
                meal_type=meal_type,
                quantity=weight,
                unit='г'
            )
            
            session.add(food_entry)
            await session.commit()
        
        # Получаем статистику за день
        from utils.daily_stats import get_daily_nutrition
        daily_stats = await get_daily_nutrition(user.telegram_id)
        
        # Создаем красивую карточку
        from utils.premium_templates import meal_card
        food_data = {
            'name': selected_product['name'],
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
            'quantity': weight,
            'unit': 'г'
        }
        
        card = meal_card(food_data, user, daily_stats)
        await message.answer(card)
        
        # Проверяем достижения
        from handlers.achievements import check_achievements
        await check_achievements(user.telegram_id, 'food', calories)
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error saving food entry: {e}")
        await message.answer("❌ Произошла ошибка сохранения. Попробуйте еще раз:")

async def determine_meal_type(hour: int) -> str:
    """Определить тип приема пищи по времени"""
    if 5 <= hour < 11:
        return "breakfast"
    elif 11 <= hour < 15:
        return "lunch"
    elif 15 <= hour < 19:
        return "dinner"
    else:
        return "snack"

@router.callback_query(F.data == "continue_as_ingredient")
async def handle_continue_as_ingredient(callback: CallbackQuery, state: FSMContext):
    """Продолжить как ингредиент для блюда"""
    await state.clear()
    
    text = "👨‍🍳 <b>Режим ингредиента</b>\n\n"
    text += "Теперь вы можете добавить этот продукт как ингредиент блюда.\n"
    text += "Используйте команду /cook для начала приготовления блюда."
    
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "cancel_food_input")
async def handle_cancel_food_input(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода еды"""
    await state.clear()
    
    text = "❌ <b>Отменено</b>\n\n"
    text += "Ввод еды отменен. Можете начать заново."
    
    await callback.message.edit_text(text)
    await callback.answer()
