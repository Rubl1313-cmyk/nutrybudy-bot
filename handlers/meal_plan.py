"""
Обработчик планировщика питания.
Показывает распределение калорий по приёмам пищи и генерирует примерное меню.
Добавлена кнопка сохранения рациона и надёжная разбивка длинных сообщений.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select
import re
import logging
from typing import List, Tuple

from database.db import get_session
from database.models import User
from services.meal_planner import distribute_calories, get_meal_plan_prompt
from services.deepseek_client import ask_worker_ai
from keyboards.reply import get_main_keyboard

router = Router()
logger = logging.getLogger(__name__)


def split_message(text: str, max_length: int = 4096) -> List[str]:
    """
    Разбивает длинный текст на части, стараясь не разрывать слова.
    Учитывает HTML-теги, закрывая их в конце каждой части.
    
    Args:
        text: Исходный текст (может содержать HTML-теги)
        max_length: Максимальная длина одной части
    
    Returns:
        Список частей текста, готовых к отправке
    """
    parts = []
    while len(text) > max_length:
        # Ищем последний пробел перед лимитом
        split_at = text.rfind(' ', 0, max_length)
        if split_at == -1:
            split_at = max_length
        part = text[:split_at].rstrip()
        text = text[split_at:].lstrip()
        if part:
            parts.append(part)
    if text:
        parts.append(text)

    # Закрываем HTML-теги в каждой части
    final_parts = []
    open_tags = []
    for part in parts:
        part_with_tags, open_tags = _close_html_tags(part, open_tags)
        final_parts.append(part_with_tags)

    logger.info(f"📄 Сообщение разбито на {len(final_parts)} частей")
    return final_parts


def _close_html_tags(html: str, open_tags: List[str] = None) -> Tuple[str, List[str]]:
    """
    Закрывает незакрытые HTML-теги в части и возвращает список открытых тегов для следующей части.
    """
    if open_tags is None:
        open_tags = []
    tag_pattern = re.compile(r'<(/?)(\w+)[^>]*>')
    stack = open_tags.copy()

    for match in tag_pattern.finditer(html):
        is_closing = match.group(1) == '/'
        tag_name = match.group(2)

        if not is_closing:
            stack.append(tag_name)
        elif stack and stack[-1] == tag_name:
            stack.pop()

    if stack:
        html += ''.join(f'</{tag}>' for tag in reversed(stack))

    return html, stack


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

    meal_names = {
        "breakfast": "🥐 Завтрак",
        "lunch": "🥗 Обед",
        "dinner": "🍲 Ужин",
        "snack": "🍎 Перекус"
    }
    text = f"🍽️ <b>Рекомендуемое распределение калорий на день</b>\n\n"
    text += f"🔥 Дневная норма: {user.daily_calorie_goal:.0f} ккал\n\n"
    for key, name in meal_names.items():
        text += f"{name}: <b>{distribution[key]:.0f} ккал</b>\n"
    text += f"\n<i>Это примерное распределение. Вы можете менять его под свои предпочтения.</i>"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Сгенерировать примерное меню", callback_data="generate_menu")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def generate_menu(user_id: int, variation: str = "") -> tuple[str, bool]:
    """
    Вспомогательная функция для генерации меню.
    Возвращает (текст ответа, успех).
    """
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return "❌ Пользователь не найден.", False

    user_data = {
        "daily_calories": user.daily_calorie_goal,
        "goal": user.goal,
        "activity_level": user.activity_level,
        "age": user.age,
        "gender": user.gender,
        "weight": user.weight,
        "height": user.height
    }
    prompt = get_meal_plan_prompt(user_data) + " " + variation

    response = await ask_worker_ai(
        prompt=prompt,
        system_prompt="Ты полезный ассистент. Отвечай на русском.",
        max_tokens=1500
    )

    if "error" in response:
        return response["error"], False

    if response.get("choices"):
        content = response["choices"][0]["message"]["content"]
        return content, True
    else:
        return "❌ Не удалось сгенерировать меню.", False


@router.callback_query(F.data == "generate_menu")
async def generate_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Генерирует первое меню."""
    user_id = callback.from_user.id
    try:
        await callback.message.edit_text("⏳ Генерирую примерное меню...")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise

    content, success = await generate_menu(user_id)

    if success:
        await state.update_data(last_menu=content)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Другой вариант", callback_data="regenerate_menu")],
            [InlineKeyboardButton(text="💾 Сохранить рацион", callback_data="save_menu")],
            [InlineKeyboardButton(text="🔙 Назад к распределению", callback_data="back_to_distribution")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])

        # Разбиваем длинный текст
        message_parts = split_message(content)
        if not message_parts:
            await callback.message.edit_text("❌ Не удалось сгенерировать меню.")
            await callback.answer()
            return

        # Первая часть — редактируем исходное сообщение
        await callback.message.edit_text(message_parts[0], reply_markup=keyboard, parse_mode="HTML")

        # Остальные части — отправляем как новые сообщения
        for i, part in enumerate(message_parts[1:], start=2):
            try:
                await callback.message.answer(part, parse_mode="HTML")
                logger.info(f"Отправлена часть {i}/{len(message_parts)}")
            except Exception as e:
                logger.error(f"Ошибка при отправке части {i}: {e}")
    else:
        await callback.message.edit_text(content)

    await callback.answer()


@router.callback_query(F.data == "regenerate_menu")
async def regenerate_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Генерирует другой вариант меню."""
    user_id = callback.from_user.id
    try:
        await callback.message.edit_text("⏳ Генерирую другой вариант...")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise

    content, success = await generate_menu(user_id, variation="Предложи другой вариант меню, отличный от предыдущего.")

    if success:
        await state.update_data(last_menu=content)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Ещё вариант", callback_data="regenerate_menu")],
            [InlineKeyboardButton(text="💾 Сохранить рацион", callback_data="save_menu")],
            [InlineKeyboardButton(text="🔙 Назад к распределению", callback_data="back_to_distribution")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])

        message_parts = split_message(content)
        if not message_parts:
            await callback.message.edit_text("❌ Не удалось сгенерировать меню.")
            await callback.answer()
            return

        await callback.message.edit_text(message_parts[0], reply_markup=keyboard, parse_mode="HTML")

        for i, part in enumerate(message_parts[1:], start=2):
            try:
                await callback.message.answer(part, parse_mode="HTML")
                logger.info(f"Отправлена часть {i}/{len(message_parts)}")
            except Exception as e:
                logger.error(f"Ошибка при отправке части {i}: {e}")
    else:
        await callback.message.edit_text(content)

    await callback.answer()


@router.callback_query(F.data == "save_menu")
async def save_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Сохраняет последнее сгенерированное меню."""
    data = await state.get_data()
    last_menu = data.get('last_menu')
    if not last_menu:
        await callback.answer("❌ Нет сохранённого рациона", show_alert=True)
        return

    await callback.message.answer(
        f"📎 <b>Сохранённый рацион</b>\n\n{last_menu}",
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
    meal_names = {
        "breakfast": "🥐 Завтрак",
        "lunch": "🥗 Обед",
        "dinner": "🍲 Ужин",
        "snack": "🍎 Перекус"
    }
    text = f"🍽️ <b>Рекомендуемое распределение калорий на день</b>\n\n"
    text += f"🔥 Дневная норма: {user.daily_calorie_goal:.0f} ккал\n\n"
    for key, name in meal_names.items():
        text += f"{name}: <b>{distribution[key]:.0f} ккал</b>\n"
    text += f"\n<i>Это примерное распределение. Вы можете менять его под свои предпочтения.</i>"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Сгенерировать примерное меню", callback_data="generate_menu")],
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
