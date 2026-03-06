"""
Обработчик планировщика питания.
Генерирует полное меню на день одним запросом к AI.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
import logging
from typing import Dict

from database.db import get_session
from database.models import User
from services.meal_planner import distribute_calories
from services.deepseek_client import ask_worker_ai
from keyboards.reply import get_main_keyboard
from handlers.profile import is_profile_complete

router = Router()
logger = logging.getLogger(__name__)

# Константы
AI_MAX_TOKENS = 3000  # увеличено для полного меню
MEAL_TYPES = [
    {"key": "breakfast", "name": "🥐 Завтрак"},
    {"key": "lunch", "name": "🥗 Обед"},
    {"key": "dinner", "name": "🍲 Ужин"},
    {"key": "snack", "name": "🍎 Перекус"}
]

async def generate_full_meal_plan(user_data: Dict, distribution: Dict) -> str:
    """
    Генерирует полное меню на день одним запросом к AI с учётом разнообразия.
    """
    prompt = (
        f"Ты диетолог. Составь разнообразное меню на один день для человека со следующими параметрами:\n"
        f"Цель: {user_data['goal']}\n"
        f"Пол: {user_data['gender']}, возраст: {user_data['age']}, вес: {user_data['weight']} кг, рост: {user_data['height']} см.\n"
        f"Активность: {user_data['activity_level']}\n"
        f"Дневная норма калорий: {user_data['daily_calories']:.0f} ккал.\n\n"
        f"Распределение калорий по приёмам:\n"
        f"- Завтрак: {distribution['breakfast']:.0f} ккал\n"
        f"- Обед: {distribution['lunch']:.0f} ккал\n"
        f"- Ужин: {distribution['dinner']:.0f} ккал\n"
        f"- Перекус: {distribution['snack']:.0f} ккал\n\n"
        f"ВАЖНО: Составь меню так, чтобы блюда были максимально разнообразными и не повторялись по типу в один день. "
        f"Например, если на обед суп, то на ужин должно быть второе блюдо (не суп). Если на обед салат, то на ужин горячее блюдо. "
        f"Избегай повторения одних и тех же ингредиентов в разных приёмах пищи.\n\n"
        f"Для каждого приёма пищи укажи:\n"
        f"1. Название блюда\n"
        f"2. Список ингредиентов с примерной калорийностью (на порцию)\n"
        f"3. Краткое описание приготовления (опционально)\n\n"
        f"Старайся, чтобы блюда были полезными, вкусными и соответствовали указанной калорийности. "
        f"Используй русский язык, обычный текст и эмодзи. Заверши ответ обязательно."
    )

    response = await ask_worker_ai(
        prompt=prompt,
        system_prompt="Ты полезный ассистент-диетолог. Отвечай на русском. Составляй разнообразные, не повторяющиеся рецепты.",
        max_tokens=AI_MAX_TOKENS
    )

    if "error" in response:
        return f"❌ Ошибка генерации меню: {response['error']}"

    if response.get("choices"):
        content = response["choices"][0]["message"]["content"]
        return content
    else:
        return "❌ Не удалось сгенерировать меню."

@router.message(Command("meal_plan"))
@router.message(F.text == "🍽️ План питания")
async def cmd_meal_plan(message: Message, state: FSMContext, user_id: int = None):
    """Показывает распределение калорий и предлагает сгенерировать меню."""
    if user_id is None:
        user_id = message.from_user.id

    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        # Проверяем наличие всех необходимых полей
        if not user or not await is_profile_complete(user):
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile (заполните все данные: вес, рост, возраст, пол, активность, цель, город).",
                reply_markup=get_main_keyboard()
            )
            return

        if not user.daily_calorie_goal:
            await message.answer(
                "❌ В вашем профиле не рассчитана норма калорий. Пожалуйста, перезаполните профиль через /set_profile.",
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
    """Генерирует полное меню одним запросом."""
    await callback.answer()

    user_id = callback.from_user.id
    await callback.message.edit_text("⏳ Генерирую меню... Это займёт около минуты.")

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

    full_menu = await generate_full_meal_plan(user_data, distribution)
    full_menu = f"🍽️ <b>Меню на день ({user.daily_calorie_goal:.0f} ккал)</b>\n\n{full_menu}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Другой вариант", callback_data="generate_full_menu")],
        [InlineKeyboardButton(text="💾 Сохранить рацион", callback_data="save_menu")],
        [InlineKeyboardButton(text="🔙 Назад к распределению", callback_data="back_to_distribution")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    # Если ответ слишком длинный, разбиваем на части
    if len(full_menu) > 4000:
        parts = [full_menu[i:i+4000] for i in range(0, len(full_menu), 4000)]
        await callback.message.edit_text(parts[0] + "...", reply_markup=keyboard, parse_mode="HTML")
        for part in parts[1:]:
            await callback.message.answer(part, parse_mode="HTML")
    else:
        await callback.message.edit_text(full_menu, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "save_menu")
async def save_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Сохраняет последнее сгенерированное меню."""
    await callback.answer("✅ Рацион сохранён!")
    await callback.message.answer(
        f"📎 <b>Сохранённый рацион</b>\n\n{callback.message.text}",
        parse_mode="HTML"
    )

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
