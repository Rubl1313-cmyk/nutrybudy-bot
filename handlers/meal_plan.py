"""
handlers/meal_plan.py
Планирование питания
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

class MealPlanStates(StatesGroup):
    """Состояния для планирования питания"""
    waiting_for_preferences = State()
    waiting_for_restrictions = State()

@router.message(Command("meal_plan"))
async def cmd_meal_plan(message: Message, state: FSMContext):
    """Получить план питания"""
    await state.clear()
    
    await message.answer(
        "🍽️ <b>План питания</b>\n\n"
        "Я составлю персональный план питания на основе ваших целей и предпочтений.\n\n"
        "📋 <b>Ваши предпочтения:</b>\n"
        "• Диета (вегетарианская, безглютеновая и т.д.)\n"
        "• Аллергии и непереносимости\n"
        "• Любимые/нелюбимые продукты\n"
        "• Количество приемов пищи в день\n\n"
        "Напишите ваши предпочтения или отправьте 0 если нет особых требований:",
        parse_mode="HTML"
    )
    await state.set_state(MealPlanStates.waiting_for_preferences)

@router.message(MealPlanStates.waiting_for_preferences)
async def process_preferences(message: Message, state: FSMContext):
    """Обработка предпочтений"""
    preferences = message.text.strip()
    
    if preferences == "0":
        preferences = "Нет особых предпочтений"
    
    await state.update_data(preferences=preferences)
    
    await message.answer(
        "🚫 <b>Ограничения и аллергии:</b>\n\n"
        "Укажите продукты, которые нужно исключить:\n\n"
        "Примеры:\n"
        "• Орехи, молоко, яйца\n"
        "• Глютен, лактоза\n"
        "• Острое, жирное\n\n"
        "Отправьте 0 если нет ограничений:",
        parse_mode="HTML"
    )
    await state.set_state(MealPlanStates.waiting_for_restrictions)

@router.message(MealPlanStates.waiting_for_restrictions)
async def process_restrictions(message: Message, state: FSMContext):
    """Обработка ограничений и создание плана"""
    restrictions = message.text.strip()
    
    if restrictions == "0":
        restrictions = "Нет ограничений"
    
    # Получаем данные пользователя
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль командой /set_profile",
                reply_markup=get_main_keyboard()
            )
            return
        
        # Формируем контекст для AI
        context = f"""
        Пользователь: {user.first_name or 'Anonymous'}
        Вес: {user.weight} кг
        Рост: {user.height} см
        Возраст: {user.age} лет
        Пол: {'мужской' if user.gender == 'male' else 'женский'}
        Цель: {user.goal}
        Норма калорий: {user.daily_calorie_goal} ккал
        Норма белков: {user.daily_protein_goal} г
        Норма жиров: {user.daily_fat_goal} г
        Норма углеводов: {user.daily_carbs_goal} г
        """
        
        # Получаем предпочтения
        meal_data = await state.get_data()
        preferences = meal_data['preferences']
        
        # Формируем запрос к AI
        ai_query = f"""
        Составь детальный план питания на один день.
        
        Цель: {user.goal}
        Калорийность: {user.daily_calorie_goal} ккал
        БЖУ: Б{user.daily_protein_goal}г Ж{user.daily_fat_goal}г У{user.daily_carbs_goal}г
        
        Предпочтения: {preferences}
        Ограничения: {restrictions}
        
        Включи:
        1. Завтрак, обед, ужин + 1-2 перекуса
        2. Точное количество каждого ингредиента в граммах
        3. Калории и БЖУ для каждого приема пищи
        4. Простые рецепты приготовления
        5. Рекомендации по времени приема
        
        Формат: четкая структура с заголовками для каждого приема пищи
        """
        
        try:
            # Отправляем "печатает..."
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            # Запрос к AI
            response = await cf_manager.ai_assistant(ai_query, context)
            
            await state.clear()
            
            await message.answer(
                f"🍽️ <b>Ваш персональный план питания</b>\n\n{response}\n\n"
                f"💡 <b>Сохраните этот план и следуйте ему!</b>\n\n"
                f"Для нового плана используйте /meal_plan",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при создании плана питания: {e}")
            await message.answer(
                "❌ Не удалось создать план питания. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )

@router.message(Command("diet"))
async def cmd_diet(message: Message, state: FSMContext):
    """Альтернативная команда для плана питания"""
    await cmd_meal_plan(message, state)

@router.message(Command("nutrition"))
async def cmd_nutrition(message: Message, state: FSMContext):
    """Советы по питанию"""
    await state.clear()
    
    try:
        # Получаем информацию о пользователе
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await message.answer(
                    "❌ Сначала настройте профиль командой /set_profile",
                    reply_markup=get_main_keyboard()
                )
                return
            
            # Формируем контекст
            context = f"""
            Пользователь: {user.first_name or 'Anonymous'}
            Вес: {user.weight} кг
            Рост: {user.height} см
            Возраст: {user.age} лет
            Пол: {'мужской' if user.gender == 'male' else 'женский'}
            Цель: {user.goal}
            Норма калорий: {user.daily_calorie_goal} ккал
            """
            
            # Запрос к AI
            ai_query = f"""
            Дай персональные рекомендации по питанию для цели: {user.goal}
            
            Включи:
            1. Основные принципы питания
            2. Рекомендуемые продукты
            3. Продукты которых стоит избегать
            4. Время приема пищи
            5. Водный баланс
            6. Дополнительные советы
            
            Будь кратким, но информативным.
            """
            
            # Отправляем "печатает..."
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            response = await cf_manager.ai_assistant(ai_query, context)
            
            await message.answer(
                f"🥗 <b>Рекомендации по питанию</b>\n\n{response}",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении рекомендаций: {e}")
        await message.answer(
            "❌ Не удалось получить рекомендации. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )

@router.callback_query(F.data == "meal_plan")
async def meal_plan_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для плана питания из меню"""
    await callback.answer()
    await cmd_meal_plan(callback.message, state)

@router.callback_query(F.data == "nutrition_tips")
async def nutrition_tips_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для советов по питанию из меню"""
    await callback.answer()
    await cmd_nutrition(callback.message, state)
