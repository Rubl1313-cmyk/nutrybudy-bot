"""
Обработчик планировщика питания.
Генерирует полное меню на день одним запросом к AI.
Добавлена постобработка для добавления суммарной калорийности,
исправлено дублирование, улучшен промпт для точности расчётов.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
import logging
import re
from typing import Dict

from database.db import get_session
from database.models import User
from services.meal_planner import distribute_calories
from services.deepseek_client import ask_worker_ai
from keyboards.reply import get_main_keyboard

router = Router()
logger = logging.getLogger(__name__)

AI_MAX_TOKENS = 3000
MEAL_TYPES = [
    {"key": "breakfast", "name": "🥐 Завтрак"},
    {"key": "lunch", "name": "🥗 Обед"},
    {"key": "dinner", "name": "🍲 Ужин"},
    {"key": "snack", "name": "🍎 Перекус"}
]

def postprocess_menu(menu_text: str) -> str:
    """
    Проверяет наличие итоговых калорий для каждого приёма.
    Если итог отсутствует – добавляет его, суммируя калории ингредиентов.
    Удаляет дублирующиеся строки с итогами.
    """
    lines = menu_text.split('\n')
    new_lines = []
    current_meal = None
    meal_calories = 0
    meal_lines = []
    meal_has_total = False

    for line in lines:
        # Начало нового приёма
        if re.match(r'^###?\s*(Завтрак|Обед|Ужин|Перекус)', line, re.IGNORECASE):
            # Завершаем предыдущий приём
            if current_meal and meal_lines:
                if not meal_has_total:
                    meal_lines.append(f"🔥 Всего: {meal_calories:.0f} ккал")
                new_lines.extend(meal_lines)
                new_lines.append('')
            current_meal = line
            meal_calories = 0
            meal_lines = [line]
            meal_has_total = False
        elif current_meal:
            meal_lines.append(line)
            # Ищем калории (цифра перед "ккал")
            match = re.search(r'(\d+(?:[.,]\d+)?)\s*ккал', line, re.IGNORECASE)
            if match:
                try:
                    cal = float(match.group(1).replace(',', '.'))
                    meal_calories += cal
                except:
                    pass
            # Проверяем, есть ли строка с итогом в этом приёме
            if '🔥 Всего:' in line or 'Всего калорий:' in line:
                meal_has_total = True
        else:
            new_lines.append(line)

    # Завершаем последний приём
    if current_meal and meal_lines:
        if not meal_has_total:
            meal_lines.append(f"🔥 Всего: {meal_calories:.0f} ккал")
        new_lines.extend(meal_lines)

    # Удаляем лишние пустые строки
    result = []
    prev_empty = False
    for line in new_lines:
        if line == '':
            if not prev_empty:
                result.append(line)
                prev_empty = True
        else:
            result.append(line)
            prev_empty = False

    return '\n'.join(result)

async def generate_full_meal_plan(user_data: Dict, distribution: Dict) -> str:
    """
    Генерирует полное меню на день одним запросом к AI.
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
        f"Обращайся к пользователю на «ты», не используй фразы «ваш клиент».\n\n"
        f"Для каждого приёма пищи укажи:\n"
        f"1. Название блюда\n"
        f"2. Список ингредиентов с калорийностью каждого (на порцию). Например: «Овсянка — 350 ккал».\n"
        f"3. Краткое описание приготовления (опционально)\n"
        f"4. В конце каждого приёма добавь строку с общей калорийностью, например: «🔥 Всего: 450 ккал». Убедись, что общая калорийность равна сумме калорий всех ингредиентов.\n\n"
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
        # Постобработка: добавляем суммарные калории, если их нет, убираем дубли
        content = postprocess_menu(content)
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
