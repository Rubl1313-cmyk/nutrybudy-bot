"""
Обработчик планировщика питания.
Генерирует дневной план через Spoonacular API, переводит названия блюд,
позволяет обновлять план и просматривать полные рецепты.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.db import get_session
from database.models import User
from services.spoonacular_client import generate_meal_plan, get_recipe_details
from services.translator import translate_to_russian
from keyboards.reply import get_main_keyboard
from utils.states import MealPlanStates

router = Router()


@router.message(Command("plan"))
@router.message(F.text == "📖 План питания")
async def cmd_plan(message: Message, state: FSMContext):
    """Генерирует и показывает план питания на сегодня."""
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

    target_calories = user.daily_calorie_goal

    await message.answer("🔄 Генерирую план питания на сегодня...")

    meal_plan = await generate_meal_plan(target_calories=target_calories, time_frame="day")

    if not meal_plan or 'meals' not in meal_plan:
        await message.answer(
            "❌ Не удалось сгенерировать план. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return

    # Переводим названия блюд на русский
    for meal in meal_plan['meals']:
        meal['title'] = await translate_to_russian(meal['title'])

    # Сохраняем план в состоянии
    await state.update_data(current_plan=meal_plan)
    await state.set_state(MealPlanStates.viewing_plan)

    # Формируем текст с названиями блюд
    text = format_meal_plan_titles(meal_plan)

    # Клавиатура: обновить план / показать рецепты
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Предложить другой вариант", callback_data="refresh_plan")],
        [InlineKeyboardButton(text="🍽️ Показать рецепты", callback_data="show_recipes")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "refresh_plan", MealPlanStates.viewing_plan)
async def refresh_plan(callback: CallbackQuery, state: FSMContext):
    """Генерирует новый план взамен старого."""
    await callback.message.edit_text("🔄 Генерирую новый вариант...")
    data = await state.get_data()
    target_calories = data.get('target_calories', 2000)  # нужно сохранять при первом вызове

    # Получаем актуальную цель из состояния или заново из БД
    # В cmd_plan мы не сохранили target_calories в state, поэтому лучше перечитать из БД
    user_id = callback.from_user.id
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await callback.message.edit_text(
                "❌ Пользователь не найден.",
                reply_markup=get_main_keyboard()
            )
            return
        target_calories = user.daily_calorie_goal

    new_plan = await generate_meal_plan(target_calories=target_calories, time_frame="day")

    if not new_plan:
        await callback.message.edit_text(
            "❌ Не удалось сгенерировать новый план. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return

    # Переводим названия
    for meal in new_plan['meals']:
        meal['title'] = await translate_to_russian(meal['title'])

    await state.update_data(current_plan=new_plan)
    text = format_meal_plan_titles(new_plan)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Предложить другой вариант", callback_data="refresh_plan")],
        [InlineKeyboardButton(text="🍽️ Показать рецепты", callback_data="show_recipes")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "show_recipes", MealPlanStates.viewing_plan)
async def show_recipes(callback: CallbackQuery, state: FSMContext):
    """Показывает полные рецепты всех блюд из текущего плана."""
    data = await state.get_data()
    meal_plan = data.get('current_plan')
    if not meal_plan:
        await callback.answer("❌ План не найден", show_alert=True)
        return

    meals = meal_plan.get('meals', [])
    if not meals:
        await callback.answer("❌ В плане нет блюд", show_alert=True)
        return

    await callback.message.edit_text("🍽️ Загружаю рецепты...")

    for meal in meals:
        recipe_id = meal.get('id')
        details = await get_recipe_details(recipe_id)
        if details:
            text = format_recipe_details(details)
            await callback.message.answer(text, parse_mode="HTML")
        else:
            await callback.message.answer(f"❌ Не удалось загрузить рецепт для {meal.get('title', 'блюда')}")

    # После отправки всех рецептов возвращаемся к плану
    text = format_meal_plan_titles(meal_plan)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Предложить другой вариант", callback_data="refresh_plan")],
        [InlineKeyboardButton(text="🍽️ Показать рецепты", callback_data="show_recipes")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.message.delete()  # удаляем сообщение "Загружаю рецепты"
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возвращает пользователя в главное меню."""
    await state.clear()
    await callback.message.edit_text("🏠 Главное меню", reply_markup=get_main_keyboard())
    await callback.answer()


def format_meal_plan_titles(meal_plan: dict) -> str:
    """Формирует текст с названиями блюд и суммарными КБЖУ."""
    nutrients = meal_plan.get('nutrients', {})
    meals = meal_plan.get('meals', [])

    text = f"🍽️ <b>Ваш план питания на сегодня:</b>\n\n"
    text += f"📊 <b>Суммарно:</b>\n"
    text += f"   🔥 Калории: {nutrients.get('calories', 0):.0f} ккал\n"
    text += f"   🥩 Белки: {nutrients.get('protein', 0):.1f} г\n"
    text += f"   🥑 Жиры: {nutrients.get('fat', 0):.1f} г\n"
    text += f"   🍚 Углеводы: {nutrients.get('carbohydrates', 0):.1f} г\n\n"
    text += f"📋 <b>Приёмы пищи:</b>\n"

    meal_type_names = ["🥐 Завтрак", "🥗 Обед", "🍲 Ужин", "🍎 Перекус"]
    for i, meal in enumerate(meals):
        type_name = meal_type_names[i] if i < len(meal_type_names) else "🍽️ Приём пищи"
        text += f"\n<b>{type_name}:</b> {meal.get('title', 'Без названия')}\n"
        text += f"   <i>Время: {meal.get('readyInMinutes', '?')} мин | Порций: {meal.get('servings', '?')}</i>\n"

    return text


def format_recipe_details(details: dict) -> str:
    """Формирует текст с полным рецептом (переведённым)."""
    text = f"🍽️ <b>{details.get('title', 'Рецепт')}</b>\n\n"
    text += f"⏱️ Время: {details.get('readyInMinutes', '?')} мин | 🍽️ Порций: {details.get('servings', '?')}\n\n"

    if details.get('summary'):
        text += f"📝 <i>{details['summary']}</i>\n\n"

    text += "🛒 <b>Ингредиенты:</b>\n"
    for ing in details.get('ingredients', []):
        text += f"• {ing.get('original', '')}\n"

    if details.get('instructions'):
        text += f"\n👨‍🍳 <b>Приготовление:</b>\n{details['instructions']}"

    return text
