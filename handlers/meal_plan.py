"""
Обработчик планировщика питания.
Генерирует меню по частям: завтрак, обед, ужин, перекус.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select
import logging
from typing import Dict, Optional

from database.db import get_session
from database.models import User
from services.meal_planner import distribute_calories, get_meal_plan_prompt
from services.deepseek_client import ask_worker_ai
from keyboards.reply import get_main_keyboard

router = Router()
logger = logging.getLogger(__name__)

# Константы
AI_MAX_TOKENS = 1500  # для каждого запроса достаточно
MEAL_TYPES = [
    {"key": "breakfast", "name": "🥐 Завтрак"},
    {"key": "lunch", "name": "🥗 Обед"},
    {"key": "dinner", "name": "🍲 Ужин"},
    {"key": "snack", "name": "🍎 Перекус"}
]

async def generate_meal_part(
    user_data: Dict,
    meal_key: str,
    meal_name: str,
    calories: float,
    previous_meals: str = ""
) -> str:
    """
    Генерирует один приём пищи через AI.
    """
    prompt = (
        f"Ты диетолог. Составь рецепт для {meal_name.lower()} в рамках здорового питания.\n"
        f"Цель пользователя: {user_data['goal']}\n"
        f"Пол: {user_data['gender']}, возраст: {user_data['age']}, вес: {user_data['weight']} кг, рост: {user_data['height']} см.\n"
        f"Активность: {user_data['activity_level']}\n\n"
        f"Требуемая калорийность этого приёма: {calories:.0f} ккал.\n\n"
        f"Уже сгенерировано ранее:\n{previous_meals}\n\n"
        f"Опиши рецепт кратко: название, ингредиенты с калориями (в скобках) и короткую инструкцию. "
        f"Не используй markdown, только обычный текст и эмодзи."
    )

    response = await ask_worker_ai(
        prompt=prompt,
        system_prompt="Ты полезный ассистент-диетолог. Отвечай на русском.",
        max_tokens=AI_MAX_TOKENS
    )

    if "error" in response:
        return f"❌ Ошибка генерации {meal_name}: {response['error']}"

    if response.get("choices"):
        content = response["choices"][0]["message"]["content"]
        return f"**{meal_name}** (~{calories:.0f} ккал)\n{content}\n"
    else:
        return f"❌ Не удалось сгенерировать {meal_name}."

@router.message(Command("meal_plan"))
@router.message(F.text == "🍽️ План питания")
async def cmd_meal_plan(message: Message, state: FSMContext):
    """Показывает распределение калорий и предлагает сгенерировать меню."""
    user_id = message.from_user.id

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.daily_calorie_goal:
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile.",
                reply_markup=get_main_keyboard()
            )
            return

    distribution = distribute_calories(user.daily_calorie_goal)

    text = f"🍽️ <b>Рекомендуемое распределение калорий на день</b>\n\n"
    text += f"🔥 Дневная норма: {user.daily_calorie_goal:.0f} ккал\n\n"
    for meal in MEAL_TYPES:
        text += f"{meal['name']}: <b>{distribution[meal['key']]:.0f} ккал</b>\n"
    text += f"\n<i>Это примерное распределение. Вы можете менять его под свои предпочтения.</i>"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Сгенерировать меню", callback_data="generate_full_menu")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "generate_full_menu")
async def generate_full_menu_callback(callback: CallbackQuery, state: FSMContext):
    # ✅ Сразу отвечаем на callback, чтобы Telegram не считал его устаревшим
    await callback.answer()

    user_id = callback.from_user.id
    await callback.message.edit_text("⏳ Генерирую меню... Это займёт около минуты.")

    # Получаем данные пользователя
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден.")
            return

    user_data = {
        "daily_calories": user.daily_calorie_goal,
        "goal": user.goal,
        "activity_level": user.activity_level,
        "age": user.age,
        "gender": user.gender,
        "weight": user.weight,
        "height": user.height
    }

    distribution = distribute_calories(user.daily_calorie_goal)

    # Генерируем каждый приём пищи последовательно
    full_menu = f"🍽️ <b>Меню на день ({user.daily_calorie_goal:.0f} ккал)</b>\n\n"
    previous_parts = ""

    for meal in MEAL_TYPES:
        await callback.message.edit_text(f"⏳ Генерирую {meal['name'].lower()}...")
        part = await generate_meal_part(
            user_data,
            meal['key'],
            meal['name'],
            distribution[meal['key']],
            previous_parts
        )
        full_menu += part + "\n"
        previous_parts += f"{meal['name']}: {distribution[meal['key']]:.0f} ккал\n"

    # Клавиатура
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Другой вариант", callback_data="generate_full_menu")],
        [InlineKeyboardButton(text="💾 Сохранить рацион", callback_data="save_menu")],
        [InlineKeyboardButton(text="🔙 Назад к распределению", callback_data="back_to_distribution")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    # Отправляем готовое меню
    await callback.message.edit_text(full_menu, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "save_menu")
async def save_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Сохраняет последнее сгенерированное меню."""
    # Просто отправляем копию текущего сообщения
    await callback.message.answer(
        f"📎 <b>Сохранённый рацион</b>\n\n{callback.message.text}",
        parse_mode="HTML"
    )
    await callback.answer("✅ Рацион сохранён!")

@router.callback_query(F.data == "back_to_distribution")
async def back_to_distribution_callback(callback: CallbackQuery, state: FSMContext):
    """Возвращает к сообщению с распределением калорий."""
    user_id = callback.from_user.id
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await callback.answer("❌ Профиль не найден", show_alert=True)
            return

    distribution = distribute_calories(user.daily_calorie_goal)
    text = f"🍽️ <b>Рекомендуемое распределение калорий на день</b>\n\n"
    text += f"🔥 Дневная норма: {user.daily_calorie_goal:.0f} ккал\n\n"
    for meal in MEAL_TYPES:
        text += f"{meal['name']}: <b>{distribution[meal['key']]:.0f} ккал</b>\n"
    text += f"\n<i>Это примерное распределение. Вы можете менять его под свои предпочтения.</i>"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Сгенерировать меню", callback_data="generate_full_menu")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню."""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("🏠 Главное меню", reply_markup=get_main_keyboard())
    await callback.answer()
