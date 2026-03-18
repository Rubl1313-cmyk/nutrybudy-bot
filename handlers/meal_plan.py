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
from database.models import User, MealPlan
from services.cloudflare_manager import cf_manager
from keyboards.reply_v2 import get_main_keyboard_v2
from utils.premium_templates import loading_card, error_card
from utils.ui_templates import ProgressBar

logger = logging.getLogger(__name__)
router = Router()

class MealPlanStates(StatesGroup):
    """Состояния для планирования питания"""
    waiting_for_preferences = State()
    waiting_for_restrictions = State()

@router.message(Command("meal_plan"))
@router.message(Command("план_питания"))
async def cmd_meal_plan(message: Message, state: FSMContext):
    """Получить план питания"""
    await state.clear()
    
    # Проверяем наличие профиля
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль с помощью /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
    
    text = "🍽️ <b>План питания</b>\n\n"
    text += "Я помогу составить персональный план питания на основе ваших целей.\n\n"
    text += "📋 <b>Что нужно учесть:</b>\n"
    text += "• Ваши цели (похудение/набор/поддержание)\n"
    text += "• Калорийность и БЖУ\n"
    text += "• Предпочтения в еде\n"
    text += "• Аллергии и ограничения\n\n"
    text += "🚀 <b>Начать составление плана?</b>"
    
    keyboard = [
        ["✅ Да, составить план"],
        ["❌ Нет, спасибо"]
    ]
    
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(MealPlanStates.waiting_for_preferences)

@router.message(MealPlanStates.waiting_for_preferences)
async def process_preferences(message: Message, state: FSMContext):
    """Обработка предпочтений"""
    if message.text == "❌ Нет, спасибо":
        await state.clear()
        await message.answer("👋 Понял! Если измените решение - используйте /meal_plan", reply_markup=get_main_keyboard_v2())
        return
    
    if message.text != "✅ Да, составить план":
        await message.answer("❌ Пожалуйста, выберите вариант из меню:")
        return
    
    text = "🍽️ <b>Предпочтения в питании</b>\n\n"
    text += "Расскажите о ваших предпочтениях:\n\n"
    text += "💬 <b>Примеры:</b>\n"
    text += "• Люблю мясо, не ем рыбу\n"
    text += "• Вегетарианец, ем молочные продукты\n"
    text += "• Предпочитаю простую еду, без экзотики\n"
    text += "• Люблю овощи и злаки\n"
    text += "• Ем всё, кроме острого\n\n"
    text += "📝 <b>Опишите ваши предпочтения:</b>"
    
    await message.answer(text)
    await state.set_state(MealPlanStates.waiting_for_restrictions)

@router.message(MealPlanStates.waiting_for_restrictions)
async def process_restrictions(message: Message, state: FSMContext):
    """Обработка ограничений и составление плана"""
    preferences = message.text.strip()
    
    if len(preferences) < 5:
        await message.answer("❌ Слишком коротко. Расскажите подробнее о предпочтениях:")
        return
    
    # Показываем загрузку
    loading_msg = await message.answer(loading_card("AI составляет план питания..."))
    
    try:
        # Получаем данные пользователя
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
        
        # Формируем промпт для AI
        prompt = build_meal_plan_prompt(user, preferences)
        
        # Получаем план от AI
        ai_response = await cf_manager.get_assistant_response(
            question="Составь детальный план питания на день",
            context=prompt
        )
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Сохраняем план в базу данных
        await save_meal_plan(user.telegram_id, ai_response, preferences)
        
        # Формируем красивый ответ
        text = "🍽️ <b>Ваш персональный план питания</b>\n\n"
        text += f"📊 <b>Ваши параметры:</b>\n"
        text += f"• Цель: {user.goal}\n"
        text += f"• Калории: {user.daily_calorie_goal} ккал\n"
        text += f"• Белки: {user.daily_protein_goal} г\n"
        text += f"• Жиры: {user.daily_fat_goal} г\n"
        text += f"• Углеводы: {user.daily_carbs_goal} г\n\n"
        
        text += "📋 <b>План на день:</b>\n\n"
        text += ai_response
        
        text += "\n\n💡 <b>Советы:</b>\n"
        text += "• Пейте достаточно воды между приемами пищи\n"
        text += "• Следите за размером порций\n"
        text += "• Ешьте медленно и осознанно\n"
        text += "• Корректируйте план по самочувствию\n\n"
        
        text += "🔄 <b>Хотите другой план?</b> Используйте /meal_plan"
        
        await message.answer(text, reply_markup=get_main_keyboard_v2())
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error creating meal plan: {e}")
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Показываем ошибку
        error_msg = error_card(
            "Не удалось составить план питания",
            "Попробуйте еще раз или измените предпочтения"
        )
        await message.answer(error_msg, reply_markup=get_main_keyboard_v2())
        await state.clear()

def build_meal_plan_prompt(user: User, preferences: str) -> str:
    """Построить промпт для составления плана питания"""
    prompt = f"""
Ты - профессиональный диетолог и нутрициолог. Составь детальный план питания на день.

Данные пользователя:
- Пол: {user.gender}
- Возраст: {user.age} лет
- Вес: {user.weight} кг
- Рост: {user.height} см
- Уровень активности: {user.activity_level}
- Цель: {user.goal}

Нормы КБЖУ на день:
- Калории: {user.daily_calorie_goal} ккал
- Белки: {user.daily_protein_goal} г
- Жиры: {user.daily_fat_goal} г
- Углеводы: {user.daily_carbs_goal} г

Предпочтения пользователя:
{preferences}

Составь план питания, который:
1. Соответствует нормам КБЖУ
2. Учитывает предпочтения
3. Содержит 5-6 приемов пищи (завтрак, перекус, обед, перекус, ужин)
4. Указывает примерное время приема
5. Дает конкретные блюда с размерами порций
6. Предлагает варианты на выбор
7. Включает рекомендации по приготовлению

Формат ответа:
🌅 ЗАВТРАК (7:00-8:00)
[Блюдо 1] - [вес]г
[Блюдо 2] - [вес]г
КБЖУ: [калории] ккал | Б:[белки]г Ж:[жиры]г У:[углеводы]г

🥨 ПЕРЕКУС (10:00-11:00)
[Блюдо] - [вес]г
КБЖУ: [калории] ккал | Б:[белки]г Ж:[жиры]г У:[углеводы]г

И так далее для всех приемов пищи.

В конце укажи итоговые КБЖУ за день.
"""
    
    return prompt

async def save_meal_plan(user_id: int, plan_text: str, preferences: str):
    """Сохранить план питания в базу данных"""
    from datetime import datetime, timezone
    
    async with get_session() as session:
        # Проверяем, есть ли уже план на сегодня
        today = datetime.now(timezone.utc).date()
        
        existing_plan = session.execute(
            select(MealPlan).where(
                MealPlan.user_id == user_id,
                MealPlan.date == today
            )
        ).scalar_one_or_none()
        
        if existing_plan:
            # Обновляем существующий план
            existing_plan.planned_foods = plan_text
            existing_plan.updated_at = datetime.now(timezone.utc)
        else:
            # Создаем новый план
            meal_plan = MealPlan(
                user_id=user_id,
                date=today,
                meal_type="daily_plan",
                planned_foods=plan_text
            )
            session.add(meal_plan)
        
        await session.commit()

@router.message(Command("my_meal_plan"))
@router.message(Command("мой_план"))
async def cmd_my_meal_plan(message: Message):
    """Показать текущий план питания"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        # Получаем план на сегодня
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).date()
        
        result = await session.execute(
            select(MealPlan).where(
                MealPlan.user_id == user_id,
                MealPlan.date == today
            )
        )
        meal_plan = result.scalar_one_or_none()
        
        if not meal_plan:
            text = "📝 <b>План питания на сегодня</b>\n\n"
            text += "У вас еще нет плана на сегодня.\n\n"
            text += "🚀 <b>Составить план:</b> /meal_plan"
            await message.answer(text)
            return
        
        text = "📝 <b>Ваш план питания на сегодня</b>\n\n"
        text += meal_plan.planned_foods
        
        if meal_plan.actual_foods:
            text += "\n\n✅ <b>Фактически съедено:</b>\n"
            text += meal_plan.actual_foods
        
        text += f"\n\n🕐 <b>План создан:</b> {meal_plan.created_at.strftime('%H:%M')}"
        
        await message.answer(text)

@router.message(Command("meal_stats"))
@router.message(Command("статистика_питания"))
async def cmd_meal_stats(message: Message):
    """Статистика выполнения плана питания"""
    user_id = message.from_user.id
    
    # Получаем статистику за неделю
    stats = await get_meal_plan_stats(user_id)
    
    text = "📊 <b>Статистика выполнения плана питания</b>\n\n"
    
    # За сегодня
    today_completion = stats['today']['completion_rate']
    today_bar = ProgressBar.create_modern_bar(today_completion, 100, 15, 'default')
    
    text += f"📅 <b>Сегодня:</b>\n"
    text += f"   Выполнение плана: {today_bar}\n"
    text += f"   Приемов пищи: {stats['today']['completed']}/{stats['today']['planned']}\n\n"
    
    # За неделю
    week_completion = stats['week']['completion_rate']
    week_bar = ProgressBar.create_modern_bar(week_completion, 100, 15, 'default')
    
    text += f"📆 <b>За неделю:</b>\n"
    text += f"   Выполнение плана: {week_bar}\n"
    text += f"   Приемов пищи: {stats['week']['completed']}/{stats['week']['planned']}\n\n"
    
    # Мотивация
    if today_completion >= 90:
        text += "🎉 <b>Отлично!</b> Вы придерживаетесь плана!\n"
    elif today_completion >= 70:
        text += "💪 <b>Хорошо!</b> Стараетесь следовать плану!\n"
    else:
        text += "💡 <b>Совет:</b> Постарайтесь лучше придерживаться плана для достижения целей!\n"
    
    await message.answer(text)

async def get_meal_plan_stats(user_id: int) -> dict:
    """Получить статистику выполнения плана питания"""
    from datetime import datetime, timezone, timedelta
    
    async with get_session() as session:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        
        def get_period_stats(start_date):
            result = session.execute(
                select(MealPlan).where(
                    MealPlan.user_id == user_id,
                    MealPlan.date >= start_date
                )
            )
            plans = result.scalars().all()
            
            planned = len(plans)
            completed = sum(1 for plan in plans if plan.is_completed)
            completion_rate = (completed / planned * 100) if planned > 0 else 0
            
            return {
                'planned': planned,
                'completed': completed,
                'completion_rate': completion_rate
            }
        
        return {
            'today': get_period_stats(today_start),
            'week': get_period_stats(week_start)
        }
