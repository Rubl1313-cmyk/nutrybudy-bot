"""
handlers/drinks.py
Обработчики напитков - универсальная система учета жидкостей
Поддерживает воду, соки, чай, кофе и другие напитки с калориями
"""
import logging
from datetime import datetime, timezone
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, DrinkEntry
from keyboards.reply_v2 import get_main_keyboard_v2
from utils.states import DrinkStates, WaterStates
from utils.drink_parser import parse_drink
from utils.daily_stats import get_daily_water
from utils.premium_templates import drink_card, water_card
from utils.ui_templates import ProgressBar

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("water"))
@router.message(Command("вода"))
async def cmd_water(message: Message, state: FSMContext):
    """Записать потребление воды"""
    await state.clear()
    
    # Проверяем наличие пользователя и профиля
    from database.db import get_session
    from database.models import User
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.daily_water_goal:
            await message.answer(
                "❌ Сначала настройте профиль с помощью /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
    
    text = "💧 <b>Записать воду</b>\n\n"
    text += "Введите количество воды в мл (например: 200, 500):\n\n"
    text += "💡 <b>Популярные объемы:</b>\n"
    text += "• 200 мл - стакан\n"
    text += "• 250 мл - стандартный стакан\n"
    text += "• 350 мл - большая кружка\n"
    text += "• 500 мл - бутылка\n"
    text += "• 1000 мл - литр"
    
    await message.answer(text)
    await state.set_state(WaterStates.entering_amount)

@router.message(Command("drink"))
@router.message(Command("напиток"))
async def cmd_drink(message: Message, state: FSMContext):
    """Записать любой напиток"""
    await state.clear()

    text = "🥤 <b>Записать напиток</b>\n\n"
    text += "Введите напиток и количество:\n\n"
    text += "💡 <b>Примеры:</b>\n"
    text += "• Кофе 200\n"
    text += "• Апельсиновый сок 300\n"
    text += "• Чай 250\n"
    text += "• Кола 500\n"
    text += "• Молоко 200\n\n"
    text += "Формат: <напиток> <объем в мл>"

    await message.answer(text)
    await state.set_state(DrinkStates.waiting_for_drink)

@router.message(WaterStates.entering_amount, lambda message: message.text and message.text.isdigit())
async def process_water_amount(message: Message, state: FSMContext):
    """Обработка количества воды"""
    try:
        amount = int(message.text)

        if amount <= 0:
            await message.answer("❌ Количество должно быть положительным числом. Попробуйте еще раз:")
            return

        if amount > 2000:
            await message.answer("❌ Слишком большой объем. Максимум 2000 мл за раз. Попробуйте еще раз:")
            return

        # Сохраняем в базу данных
        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()

            if not user:
                await message.answer(
                    "❌ Сначала настройте профиль с помощью /set_profile",
                    reply_markup=get_main_keyboard_v2()
                )
                await state.clear()
                return

            # Создаем запись о напитке (вода)
            drink_entry = DrinkEntry(
                user_id=user.telegram_id,
                drink_name="вода",
                amount=amount,
                calories=0,
                created_at=datetime.now(timezone.utc)
            )

            session.add(drink_entry)
            await session.commit()

            # Получаем статистику за день
            total_today = await get_daily_water(user.telegram_id)

            # Создаем красивую карточку
            card = water_card(amount, total_today, user.daily_water_goal)

            await message.answer(card, reply_markup=get_main_keyboard_v2())

            # Проверяем достижения
            from handlers.achievements import check_achievements
            await check_achievements(user.telegram_id, 'water', amount)

            await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число (например: 200):")

@router.message(DrinkStates.waiting_for_drink, lambda message: message.text and message.text.isdigit())
async def process_drink_amount(message: Message, state: FSMContext):
    """Обработка количества напитка (когда введено только число)"""
    try:
        amount = int(message.text)

        if amount <= 0:
            await message.answer("❌ Количество должно быть положительным числом. Попробуйте еще раз:")
            return

        if amount > 2000:
            await message.answer("❌ Слишком большой объем. Максимум 2000 мл за раз. Попробуйте еще раз:")
            return

        # Сохраняем в базу данных
        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()

            if not user:
                await message.answer(
                    "❌ Сначала настройте профиль с помощью /set_profile",
                    reply_markup=get_main_keyboard_v2()
                )
                await state.clear()
                return

            # Создаем запись о напитке (вода по умолчанию)
            drink_entry = DrinkEntry(
                user_id=user.telegram_id,
                drink_name="вода",
                amount=amount,
                calories=0,
                created_at=datetime.now(timezone.utc)
            )

            session.add(drink_entry)
            await session.commit()

            # Получаем статистику за день
            total_today = await get_daily_water(user.telegram_id)

            # Создаем красивую карточку
            card = water_card(amount, total_today, user.daily_water_goal)

            await message.answer(card, reply_markup=get_main_keyboard_v2())

            # Проверяем достижения
            from handlers.achievements import check_achievements
            await check_achievements(user.telegram_id, 'water', amount)

            await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат. Введите число (например: 200):")

@router.message(F.text.regexp(r'^[а-яё]+\s+\d+$'))
async def process_drink(message: Message, state: FSMContext):
    """Обработка напитков с калориями"""
    current_state = await state.get_state()

    if current_state and "waiting_for_drink" in str(current_state):
        try:
            from utils.safe_parser import safe_parse_float

            # Парсим сообщение
            drink_data = parse_drink(message.text)

            if not drink_data or not drink_data.get('name'):
                await message.answer(
                    "❌ Не удалось распознать напиток. Попробуйте еще раз:\n\n"
                    "Пример: Кофе 200"
                )
                return

            name = drink_data['name']
            volume = drink_data['amount']
            calories = drink_data['calories']

            # Валидация объема
            if volume < 10 or volume > 2000:
                await message.answer("❌ Объём должен быть от 10 до 2000 мл")
                return

            # Сохраняем в базу данных
            async with get_session() as session:
                # Получаем пользователя
                result = await session.execute(
                    select(User).where(User.telegram_id == message.from_user.id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    await message.answer(
                        "❌ Сначала настройте профиль с помощью /set_profile",
                        reply_markup=get_main_keyboard_v2()
                    )
                    await state.clear()
                    return

                # Создаем запись о напитке
                drink_entry = DrinkEntry(
                    user_id=user.telegram_id,
                    drink_name=name,
                    amount=volume,
                    calories=calories,
                    created_at=datetime.now(timezone.utc)
                )

                session.add(drink_entry)
                await session.commit()

                # Получаем статистику за день
                total_today = await get_daily_water(user.telegram_id)

                # Создаем красивую карточку
                card = drink_card(
                    volume,
                    name,
                    calories,
                    total_today,
                    calories,
                    user.daily_water_goal
                )
                
                await message.answer(card, reply_markup=get_main_keyboard_v2())
                
                # Проверяем достижения
                from handlers.achievements import check_achievements
                await check_achievements(user.telegram_id, 'drink', drink_data['amount'])
                
                await state.clear()
                
        except Exception as e:
            logger.error(f"Error processing drink: {e}")
            await message.answer("❌ Произошла ошибка. Попробуйте еще раз:")

@router.message(Command("water_stats"))
@router.message(Command("статистика_воды"))
async def cmd_water_stats(message: Message):
    """Показать статистику потребления воды"""
    user_id = message.from_user.id
    
    # Получаем статистику за разные периоды
    stats = await get_water_stats_by_periods(user_id)
    
    text = "💧 <b>Статистика потребления воды</b>\n\n"
    
    # Получаем цель по воде
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        goal = user.daily_water_goal if user else 2000
    
    # Сегодня
    today_progress = min(stats['today'] / goal * 100, 100)
    today_bar = ProgressBar.create_modern_bar(today_progress, 100, 15, 'water')
    
    text += f"📅 <b>Сегодня:</b>\n"
    text += f"   Выпито: {stats['today']} мл\n"
    text += f"   Цель: {goal} мл\n"
    text += f"   Прогресс: {today_bar}\n\n"
    
    # За неделю
    week_goal = goal * 7
    week_progress = min(stats['week'] / week_goal * 100, 100)
    week_bar = ProgressBar.create_modern_bar(week_progress, 100, 15, 'water')
    
    text += f"📆 <b>За неделю:</b>\n"
    text += f"   Выпито: {stats['week']} мл\n"
    text += f"   Цель: {week_goal} мл\n"
    text += f"   Прогресс: {week_bar}\n\n"
    
    # За месяц
    month_goal = goal * 30
    month_progress = min(stats['month'] / month_goal * 100, 100)
    month_bar = ProgressBar.create_modern_bar(month_progress, 100, 15, 'water')
    
    text += f"🗓️ <b>За месяц:</b>\n"
    text += f"   Выпито: {stats['month']} мл\n"
    text += f"   Цель: {month_goal} мл\n"
    text += f"   Прогресс: {month_bar}\n\n"
    
    # Мотивация
    if stats['today'] >= goal:
        text += "🎉 <b>Отлично!</b> Вы выполнили дневную норму воды!\n"
    elif stats['today'] >= goal * 0.75:
        text += "💪 <b>Хорошо!</b> Осталось немного до цели!\n"
    elif stats['today'] >= goal * 0.5:
        text += "👍 <b>Неплохо!</b> Продолжайте пить воду!\n"
    else:
        text += "💡 <b>Пейте больше воды!</b> Это важно для здоровья!\n"
    
    await message.answer(text)

async def get_water_stats_by_periods(user_id: int) -> dict:
    """Получить статистику потребления воды по периодам"""
    from datetime import datetime, timezone, timedelta
    
    async with get_session() as session:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        
        # Функция для получения статистики за период
        async def get_period_stats(start_date):
            result = await session.execute(
                select(func.sum(DrinkEntry.amount)).where(
                    DrinkEntry.user_id == user_id,
                    DrinkEntry.created_at >= start_date
                )
            )
            total = result.scalar() or 0
            return total
        
        return {
            'today': await get_period_stats(today_start),
            'week': await get_period_stats(week_start),
            'month': await get_period_stats(month_start)
        }

@router.message(Command("quick_water"))
@router.message(Command("быстрая_вода"))
async def cmd_quick_water(message: Message):
    """Быстрая запись стандартных объемов воды"""
    from keyboards.reply_v2 import get_water_keyboard
    
    text = "💧 <b>Быстрая запись воды</b>\n\n"
    text += "Выберите объем:"
    
    await message.answer(text, reply_markup=get_water_keyboard())

@router.message(F.text.startswith("💧"))
async def process_quick_water(message: Message):
    """Обработка быстрой записи воды"""
    text = message.text
    
    if text.startswith("💧"):
        try:
            # Извлекаем объем
            amount_str = text.split()[1]
            amount = int(amount_str.replace("мл", ""))
            
            # Сохраняем как обычную воду
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
                    calories=0,
                    created_at=datetime.now(timezone.utc)
                )
                
                session.add(drink_entry)
                await session.commit()
                
                # Получаем статистику
                total_today = await get_daily_water(user.telegram_id)
                
                # Карточка
                card = water_card(amount, total_today, user.daily_water_goal)
                await message.answer(card, reply_markup=get_main_keyboard_v2())
                
        except (ValueError, IndexError):
            await message.answer("❌ Неверный формат. Попробуйте еще раз:")
