"""
Обработчик планировщика питания.
Генерирует планы через Spoonacular API, позволяет их обновлять.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.db import get_session
from database.models import User
from services.spoonacular_client import generate_meal_plan, get_recipe_details
from keyboards.reply import get_main_keyboard
from keyboards.inline import get_meal_plan_keyboard
from utils.states import MealPlanStates

router = Router()


@router.message(Command("plan"))
@router.message(F.text == "📖 План питания")
async def cmd_plan(message: Message, state: FSMContext):
    """Начинает процесс планирования, запрашивая тип плана."""
    await state.clear()
    user_id = message.from_user.id

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile",
                reply_markup=get_main_keyboard()
            )
            return

    # Сохраняем целевую калорийность пользователя в состояние
    await state.update_data(target_calories=user.daily_calorie_goal)

    await message.answer(
        "📖 Выберите тип плана:",
        reply_markup=get_meal_plan_keyboard()
    )
    await state.set_state(MealPlanStates.waiting_for_action)


@router.callback_query(F.data == "plan_today", MealPlanStates.waiting_for_action)
async def plan_today(callback: CallbackQuery, state: FSMContext):
    """Генерирует и показывает план на сегодня."""
    await callback.message.edit_text("🔄 Генерирую план питания на сегодня...")
    data = await state.get_data()
    target_calories = data.get('target_calories', 2000)

    # 1. Получаем план от Spoonacular
    meal_plan = await generate_meal_plan(target_calories=target_calories, time_frame="day")

    if not meal_plan or 'meals' not in meal_plan:
        await callback.message.edit_text(
            "❌ Не удалось сгенерировать план. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return

    # Сохраняем план в состояние для возможности обновления
    await state.update_data(current_plan=meal_plan)

    # 2. Формируем красивое сообщение
    text = format_meal_plan_message(meal_plan)

    # 3. Создаём клавиатуру с кнопкой обновления
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Предложить другой вариант", callback_data="refresh_plan")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()
    await state.set_state(MealPlanStates.viewing_plan)


@router.callback_query(F.data == "refresh_plan", MealPlanStates.viewing_plan)
async def refresh_plan(callback: CallbackQuery, state: FSMContext):
    """Генерирует новый план взамен старого."""
    await callback.message.edit_text("🔄 Генерирую новый вариант...")
    data = await state.get_data()
    target_calories = data.get('target_calories', 2000)

    new_plan = await generate_meal_plan(target_calories=target_calories, time_frame="day")

    if not new_plan:
        await callback.message.edit_text(
            "❌ Не удалось сгенерировать новый план. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return

    await state.update_data(current_plan=new_plan)
    text = format_meal_plan_message(new_plan)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Предложить другой вариант", callback_data="refresh_plan")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


def format_meal_plan_message(meal_plan: dict) -> str:
    """Форматирует ответ от API в читаемое сообщение."""
    nutrients = meal_plan.get('nutrients', {})
    meals = meal_plan.get('meals', [])

    text = f"🍽️ <b>Ваш план питания на сегодня:</b>\n\n"
    text += f"📊 <b>Суммарно:</b>\n"
    text += f"   🔥 Калории: {nutrients.get('calories', 0):.0f} ккал\n"
    text += f"   🥩 Белки: {nutrients.get('protein', 0):.1f} г\n"
    text += f"   🥑 Жиры: {nutrients.get('fat', 0):.1f} г\n"
    text += f"   🍚 Углеводы: {nutrients.get('carbohydrates', 0):.1f} г\n\n"
    text += f"📋 <b>Приёмы пищи:</b>\n"

    for meal in meals:
        meal_type = meal.get('mealType', [])

        # Определяем тип приёма пищи по индексу (0 - завтрак, 1 - обед, 2 - ужин)
        meal_type_name = ["🥐 Завтрак", "🥗 Обед", "🍲 Ужин"]
        type_str = meal_type_name[meal.get('menuType', 0)] if 'menuType' in meal else "🍽️ Приём пищи"

        text += f"\n<b>{type_str}:</b> {meal.get('title', 'Без названия')}\n"
        text += f"   <i>Время: {meal.get('readyInMinutes', '?')} мин | Порций: {meal.get('servings', '?')}</i>\n"

        # Добавляем кнопку с деталями рецепта (опционально)
        # text += f"   [Подробнее](https://spoonacular.com/recipes/{meal.get('title', '')}-{meal.get('id', '')})\n"

    return text


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возвращает пользователя в главное меню."""
    await state.clear()
    await callback.message.edit_text("🏠 Главное меню", reply_markup=get_main_keyboard())
    await callback.answer()
