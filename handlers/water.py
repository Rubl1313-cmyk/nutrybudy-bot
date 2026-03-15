"""
handlers/water.py
Обработчики учета воды
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, WaterEntry
from keyboards.reply_v2 import get_main_keyboard_v2
from utils.water_parser import parse_water_amount

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("log_water"))
async def cmd_log_water(message: Message, state: FSMContext):
    """Запись потребления воды"""
    await state.clear()
    
    await message.answer(
        "💧 <b>Запись потребления воды</b>\n\n"
        "Напишите количество выпитой воды:\n\n"
        "Примеры:\n"
        "• 200\n"
        "• 250 мл\n"
        "• 0.5 л\n"
        "• 1 стакан\n"
        "• 1 бутылка",
        parse_mode="HTML"
    )

@router.message(F.text.regexp(r'(\d+\.?\d*)\s*(мл|л|стакан|бутылка|glass|bottle)?'))
async def process_water(message: Message, state: FSMContext):
    """Обработка записи воды"""
    try:
        # Парсим количество воды
        amount_ml = parse_water_amount(message.text)
        
        if not amount_ml or amount_ml <= 0:
            await message.answer(
                "❌ Не удалось определить количество воды. Попробуйте еще раз:\n\n"
                "Примеры: 200, 250 мл, 0.5 л, 1 стакан"
            )
            return
        
        if amount_ml > 5000:  # Защита от слишком больших значений
            await message.answer(
                "❌ Слишком большое количество. Максимум 5 литров за раз."
            )
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
                    "❌ Сначала настройте профиль командой /set_profile",
                    reply_markup=get_main_keyboard_v2()
                )
                return
            
            # Создаем запись о воде
            water_entry = WaterEntry(
                user_id=user.id,
                amount=amount_ml,
                datetime=message.date
            )
            
            session.add(water_entry)
            await session.commit()
            
            # Получаем статистику за сегодня
            today = message.date
            water_result = await session.execute(
                select(func.sum(WaterEntry.amount)).where(
                    WaterEntry.user_id == user.id,
                    func.date(WaterEntry.datetime) == today
                )
            )
            total_water = water_result.scalar() or 0
            
            progress = (total_water / user.daily_water_goal) * 100
            
            await message.answer(
                f"✅ <b>Вода записана!</b>\n\n"
                f"💧 Выпито: {amount_ml} мл\n"
                f"📊 Всего за сегодня: {total_water} мл\n"
                f"🎯 Цель: {user.daily_water_goal} мл\n"
                f"📈 Прогресс: {progress:.1f}%\n\n"
                f"{'🎉 Отлично!' if progress >= 100 else '💪 Продолжайте!'}",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при записи воды: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=get_main_keyboard_v2()
        )

@router.message(Command("water"))
async def cmd_water(message: Message, state: FSMContext):
    """Статистика потребления воды"""
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
        today = message.date
        water_result = await session.execute(
            select(func.sum(WaterEntry.amount)).where(
                WaterEntry.user_id == user.id,
                func.date(WaterEntry.datetime) == today
            )
        )
        total_water = water_result.scalar() or 0
        
        # Статистика за неделю
        from datetime import datetime, timedelta
        week_ago = today - timedelta(days=7)
        
        week_result = await session.execute(
            select(func.sum(WaterEntry.amount)).where(
                WaterEntry.user_id == user.id,
                func.date(WaterEntry.datetime) >= week_ago
            )
        )
        week_total = week_result.scalar() or 0
        
        progress = (total_water / user.daily_water_goal) * 100
        remaining = max(0, user.daily_water_goal - total_water)
        
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
            f"💧 <b>Статистика воды</b>\n\n"
            f"📅 Сегодня: {total_water} мл\n"
            f"🎯 Цель: {user.daily_water_goal} мл\n"
            f"📈 Прогресс: {progress:.1f}%\n"
            f"💦 Осталось: {remaining:.0f} мл\n"
            f"📊 Неделя: {week_total} мл\n\n"
            f"{status}\n\n"
            f"Для записи воды используйте /log_water",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "log_water")
async def log_water_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для записи воды из меню"""
    await callback.answer()
    
    await callback.message.answer(
        "💧 <b>Запись потребления воды</b>\n\n"
        "Напишите количество выпитой воды:\n\n"
        "Примеры:\n"
        "• 200\n"
        "• 250 мл\n"
        "• 0.5 л\n"
        "• 1 стакан\n"
        "• 1 бутылка",
        parse_mode="HTML"
    )
