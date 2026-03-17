"""
Обработчики напитков - замена water.py
Поддерживает воду, соки, чай, кофе и другие напитки с калориями
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, DrinkEntry
from keyboards.reply_v2 import get_main_keyboard_v2
from utils.drink_parser import parse_drink
from utils.water_parser import parse_water_amount
from services.soup_service import save_drink
from utils.localized_commands import create_localized_command_filter

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("log_drink"))
async def cmd_log_drink(message: Message, state: FSMContext):
    """Запись потребления жидкости (напитков)"""
    await state.clear()
    
    await message.answer(
        "💧 <b>Запись жидкости</b>\n\n"
        "Напишите, что вы выпили и сколько:\n\n"
        "• <b>Вода:</b> 200 мл, 1 стакан, 0.5 л\n"
        "• <b>Соки:</b> сок 250 мл, апельсиновый сок 200\n"
        "• <b>Чай/кофе:</b> чай с сахаром 300, кофе с молоком 150\n"
        "• <b>Молочные:</b> молоко 250, кефир 200, йогурт 150\n"
        "• <b>Другое:</b> газировка 330, компот 200, смузи 250\n\n"
        "🤖 Я автоматически определю тип напитка и калории!",
        parse_mode="HTML"
    )

@router.message(Command("log_water") | create_localized_command_filter("записать_воду"))
async def cmd_log_water(message: Message, state: FSMContext):
    """Запись воды (для совместимости)"""
    return await cmd_log_drink(message, state)

@router.message(Command("drink"))
@router.message(Command("water") | create_localized_command_filter("вода"))
async def cmd_drink_stats(message: Message, state: FSMContext):
    """Статистика потребления жидкости"""
    await state.clear()
    
    async with get_session() as session:
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль командой /set_profile",
                reply_markup=get_main_keyboard_v2()
            )
            return
        
        # Статистика за сегодня
        from datetime import datetime, timedelta
        today = message.date
        
        # Общая жидкость
        drink_result = await session.execute(
            select(func.sum(DrinkEntry.volume_ml)).where(
                DrinkEntry.user_id == user.id,
                func.date(DrinkEntry.datetime) == today
            )
        )
        total_volume = drink_result.scalar() or 0
        
        # Калории из напитков
        calories_result = await session.execute(
            select(func.sum(DrinkEntry.calories)).where(
                DrinkEntry.user_id == user.id,
                func.date(DrinkEntry.datetime) == today
            )
        )
        total_calories = calories_result.scalar() or 0
        
        # Статистика за неделю
        week_ago = today - timedelta(days=7)
        
        week_result = await session.execute(
            select(func.sum(DrinkEntry.volume_ml)).where(
                DrinkEntry.user_id == user.id,
                func.date(DrinkEntry.datetime) >= week_ago
            )
        )
        week_total = week_result.scalar() or 0
        
        # Прогресс
        progress = (total_volume / user.daily_water_goal) * 100
        remaining = max(0, user.daily_water_goal - total_volume)
        
        # Статус
        if progress >= 100:
            status = "🎉 Цель достигнута!"
        elif progress >= 75:
            status = "💪 Отлично!"
        elif progress >= 50:
            status = "👍 Хорошо"
        elif progress >= 25:
            status = "💧 Нужна вода"
        else:
            status = "🚨 Пейте воду!"
        
        await message.answer(
            f"💧 <b>Статистика жидкости</b>\n\n"
            f"📅 <b>Сегодня:</b>\n"
            f"💦 Всего выпито: {total_volume:.0f} мл\n"
            f"🎯 Цель: {user.daily_water_goal} мл\n"
            f"📈 Прогресс: {progress:.1f}%\n"
            f"🔥 Калории из напитков: {total_calories:.0f} ккал\n"
            f"💦 Осталось: {remaining:.0f} мл\n\n"
            f"📊 <b>Неделя:</b> {week_total:.0f} мл\n\n"
            f"{status}\n\n"
            f"Для записи жидкости используйте /log_drink",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

@router.message(F.text.regexp(r'(\d+\.?\d*)\s*(мл|л|стакан|чашка|бутылка|glass|bottle|cup)?'))
async def process_drink(message: Message, state: FSMContext):
    """Обработка записи напитка"""
    try:
        # Пробуем распарсить как напиток
        volume, drink_name, calories = await parse_drink(message.text)
        
        if not volume or volume <= 0:
            await message.answer(
                "❌ Не удалось определить количество. Попробуйте еще раз:\n\n"
                "Примеры: 200 мл, 250, 0.5 л, 1 стакан"
            )
            return
        
        if volume > 5000:  # Защита от слишком больших значений
            await message.answer(
                "❌ Слишком большое количество. Максимум 5 литров за раз."
            )
            return
        
        # Сохраняем напиток
        result = await save_drink(message.from_user.id, message.text)
        
        # Получаем статистику за сегодня
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = user_result.scalar_one_or_none()
            
            today_result = await session.execute(
                select(func.sum(DrinkEntry.volume_ml)).where(
                    DrinkEntry.user_id == user.id,
                    func.date(DrinkEntry.datetime) == message.date
                )
            )
            total_volume = today_result.scalar() or 0
            
            calories_result = await session.execute(
                select(func.sum(DrinkEntry.calories)).where(
                    DrinkEntry.user_id == user.id,
                    func.date(DrinkEntry.datetime) == message.date
                )
            )
            total_calories = calories_result.scalar() or 0
            
            progress = (total_volume / user.daily_water_goal) * 100
            
            # Формируем ответ
            if calories > 0:
                calorie_info = f"\n🔥 Калории: {calories:.0f} ккал"
            else:
                calorie_info = ""
            
            await message.answer(
                f"✅ <b>Жидкость записана!</b>\n\n"
                f"💧 {drink_name.title()}: {volume:.0f} мл{calorie_info}\n\n"
                f"📊 <b>Всего за сегодня:</b>\n"
                f"💦 Жидкость: {total_volume:.0f} мл\n"
                f"🎯 Цель: {user.daily_water_goal} мл\n"
                f"📈 Прогресс: {progress:.1f}%\n"
                f"🔥 Калории из напитков: {total_calories:.0f} ккал\n\n"
                f"{'🎉 Отлично!' if progress >= 100 else '💪 Продолжайте!'}",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при записи напитка: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=get_main_keyboard_v2()
        )

@router.callback_query(F.data == "log_water")
@router.callback_query(F.data == "log_drink")
async def log_drink_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для записи жидкости из меню"""
    await callback.answer()
    
    await callback.message.answer(
        "💧 <b>Запись жидкости</b>\n\n"
        "Напишите, что вы выпили и сколько:\n\n"
        "• <b>Вода:</b> 200 мл, 1 стакан, 0.5 л\n"
        "• <b>Соки:</b> сок 250 мл, апельсиновый сок 200\n"
        "• <b>Чай/кофе:</b> чай с сахаром 300, кофе с молоком 150\n"
        "• <b>Молочные:</b> молоко 250, кефир 200, йогурт 150\n"
        "• <b>Другое:</b> газировка 330, компот 200, смузи 250\n\n"
        "🤖 Я автоматически определю тип напитка и калории!",
        parse_mode="HTML"
    )
