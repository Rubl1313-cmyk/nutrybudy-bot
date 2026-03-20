"""
Обработчики кнопок клавиатур для NutriBuddy Bot
"""
import logging
import re
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from database.db import get_session
from database.models import User, DrinkEntry
from keyboards.reply_v2 import get_main_keyboard_v2
from utils.premium_templates import drink_card, water_card
from utils.daily_stats import get_daily_water
from handlers.drinks import cmd_water, cmd_quick_water
from handlers.food import cmd_log_food
from handlers.common import cmd_help, cmd_start

logger = logging.getLogger(__name__)
router = Router()

# === Обработчики кнопок воды ===

@router.message(F.text.regexp(r'^💧\s*(\d+)\s*(мл|мл|стакан|стакана|литр|л)$'))
async def water_keyboard_handler(message: Message, state: FSMContext):
    """Обработка кнопок клавиатуры воды"""
    text = message.text
    
    if "1 стакан" in text:
        amount = 200
    elif "2 стакана" in text:
        amount = 400
    elif "500 мл" in text or "500мл" in text:
        amount = 500
    elif "1 литр" in text or "1л" in text:
        amount = 1000
    else:
        # Извлекаем число из текста
        match = re.search(r'(\d+)', text)
        if match:
            amount = int(match.group(1))
        else:
            await message.answer("❌ Неверный формат")
            return
    
    # Сохраняем воду как в process_quick_water
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Сначала настройте профиль")
            return
        
        drink_entry = DrinkEntry(
            user_id=user.telegram_id,
            drink_name="вода",
            amount=amount,
            calories=0
        )
        
        session.add(drink_entry)
        await session.commit()
        
        # Получаем статистику
        total_today = await get_daily_water(user.telegram_id)
        
        # Карточка
        card = water_card(amount, total_today, user.daily_water_goal)
        await message.answer(card, reply_markup=get_main_keyboard_v2())

# === Обработчики кнопок еды ===

@router.message(F.text.startswith("📸"))
async def photo_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки фото еды"""
    await state.clear()
    await message.answer(
        "📸 <b>Отправьте фото блюда</b>\n\n"
        "Я распознаю продукты и рассчитаю калории.",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.startswith("✏️"))
async def text_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки текстового ввода еды"""
    await state.clear()
    await cmd_log_food(message, state)

@router.message(F.text.startswith("⚡"))
async def quick_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки быстрого ввода еды"""
    await state.clear()
    await message.answer(
        "⚡ <b>Быстрый ввод</b>\n\n"
        "Напишите что вы съели в формате:\n"
        "• гречка 200г\n"
        "• курица 150г\n"
        "• салат 100г",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

# === Обработчики кнопок помощи ===

@router.message(F.text.startswith("📋"))
async def commands_help_handler(message: Message):
    """Показать список команд"""
    await cmd_help(message, None)

@router.message(F.text.startswith("🚀"))
async def features_help_handler(message: Message):
    """Показать возможности бота"""
    text = "🚀 <b>Возможности NutriBuddy:</b>\n\n"
    text += "🍽️ <b>Распознавание еды по фото</b>\n"
    text += "📊 <b>Отслеживание КБЖУ и калорий</b>\n"
    text += "💧 <b>Контроль водного баланса</b>\n"
    text += "⚖️ <b>Запись веса и прогресса</b>\n"
    text += "🤖 <b>AI ассистент для советов</b>\n"
    text += "📈 <b>Детальная статистика</b>\n"
    
    await message.answer(text, reply_markup=get_main_keyboard_v2(), parse_mode="HTML")

@router.message(F.text.startswith("💬"))
async def support_help_handler(message: Message):
    """Показать поддержку"""
    text = "💬 <b>Поддержка NutriBuddy:</b>\n\n"
    text += "👨‍💻 <b>Разработчик:</b> @username\n"
    text += "📧 <b>Почта:</b> support@nutribuddy.com\n"
    text += "📚 <b>Документация:</b> https://docs.nutribuddy.com\n"
    text += "💡 <b>Идеи и предложения:</b> @ideas_channel"
    
    await message.answer(text, reply_markup=get_main_keyboard_v2(), parse_mode="HTML")

# === Универсальные обработчики ===

@router.message(F.text.startswith("🏠"))
async def menu_keyboard_handler(message: Message, state: FSMContext):
    """Обработка кнопки главного меню из клавиатур"""
    await state.clear()
    await cmd_start(message)

@router.message(F.text.startswith("✅"))
async def yes_button_handler(message: Message, state: FSMContext):
    """Обработка кнопки Да"""
    await message.answer("✅ Подтверждено")

@router.message(F.text.startswith("❌"))
async def no_button_handler(message: Message, state: FSMContext):
    """Обработка кнопки Нет"""
    await message.answer("❌ Отменено")

# === Обработчики настроек ===

@router.message(F.text.startswith("📏"))
async def metric_units_handler(message: Message):
    """Метрическая система"""
    await message.answer("📏 <b>Метрическая система</b>\n\nИспользуются килограммы и сантиметры.")

# === Обработчики статистики ===

@router.message(F.text.startswith("🏃"))
async def activity_stats_handler(message: Message):
    """Статистика активности"""
    from handlers.activity import cmd_activity_stats
    await cmd_activity_stats(message)
