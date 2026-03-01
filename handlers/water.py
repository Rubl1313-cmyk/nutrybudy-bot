"""
Обработчик трекера воды для NutriBuddy
✅ Исправлено: regexp-фильтры не перехватывают кнопки меню
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from datetime import datetime, timedelta
from database.db import get_session
from database.models import User, WaterEntry
from keyboards.inline import get_water_preset_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard
from utils.states import WaterStates

router = Router()


@router.message(Command("log_water"))
@router.message(F.text == "💧 Вода")
async def cmd_water(message: Message, state: FSMContext):
    """Добавление записи о потреблении воды"""
    # 🔥 Сброс состояния
    await state.clear()
    
    user_id = message.from_user.id
    
    async with get_session() as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer(
                "❌ Сначала настрой профиль через /set_profile",
                reply_markup=get_main_keyboard()
            )
            return
    
    await state.set_state(WaterStates.entering_amount)
    
    # Показываем прогресс за сегодня
    today = datetime.now().date()
    async with get_session() as session:
        result = await session.execute(
            select(func.sum(WaterEntry.amount)).where(
                WaterEntry.user_id == user_id,
                func.date(WaterEntry.datetime) == today
            )
        )
        consumed = result.scalar() or 0
        goal = user.daily_water_goal
    
    progress = min(100, int(consumed / goal * 100)) if goal > 0 else 0
    
    await message.answer(
        f"💧 <b>Водный баланс</b>\n\n"
        f"📊 Выпито сегодня: {consumed:.0f} / {goal:.0f} мл\n"
        f"📈 Прогресс: {progress}%\n\n"
        f"Сколько воды вы выпили?\n"
        f"Выберите из предложенных или введите вручную:",
        reply_markup=get_water_preset_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("water_"), WaterStates.entering_amount)
async def preset_water(callback: CallbackQuery, state: FSMContext):
    """Выбор предустановленного объёма"""
    try:
        amount = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка выбора", show_alert=True)
        return
    
    await state.update_data(amount=amount)
    await state.set_state(WaterStates.confirming)
    
    await callback.message.edit_text(
        f"💧 Добавить {amount} мл воды?",
        reply_markup=get_confirmation_keyboard()
    )
    await callback.answer()


# 🔥 ИСПРАВЛЕНО: regexp-фильтр ловит ТОЛЬКО числа
@router.message(WaterStates.entering_amount, F.text.regexp(r'^\s*\d+([.,]\d+)?\s*$'))
async def manual_water(message: Message, state: FSMContext):
    """Ручной ввод объёма воды"""
    try:
        amount = float(message.text.replace(',', '.').strip())
        if not 0 < amount <= 5000:
            raise ValueError("Объём вне допустимого диапазона")
    except ValueError:
        await message.answer(
            "❌ Введите положительное число от 1 до 5000 мл\n"
            "<i>Примеры: 200, 500, 1000</i>",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(amount=amount)
    await state.set_state(WaterStates.confirming)
    
    await message.answer(
        f"💧 Добавить {amount:.0f} мл воды?",
        reply_markup=get_confirmation_keyboard()
    )


@router.callback_query(F.data == "confirm", WaterStates.confirming)
async def confirm_water(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и сохранение записи"""
    data = await state.get_data()
    amount = data.get('amount')
    
    if not amount:
        await callback.answer("❌ Ошибка: не указан объём", show_alert=True)
        return
    
    async with get_session() as session:
        entry = WaterEntry(
            user_id=callback.from_user.id,
            amount=amount,
            datetime=datetime.now()
        )
        session.add(entry)
        
        # Считаем новый прогресс
        user = await session.get(User, callback.from_user.id)
        today = datetime.now().date()
        
        result = await session.execute(
            select(func.sum(WaterEntry.amount)).where(
                WaterEntry.user_id == callback.from_user.id,
                func.date(WaterEntry.datetime) == today
            )
        )
        consumed = (result.scalar() or 0) + amount
        goal = user.daily_water_goal if user else 2000
    
    await session.commit()
    await state.clear()
    
    progress = min(100, int(consumed / goal * 100))
    emoji = "🎉" if consumed >= goal else "💧"
    
    await callback.message.edit_text(
        f"{emoji} <b>Записано {amount:.0f} мл!</b>\n\n"
        f"📊 Всего сегодня: {consumed:.0f} / {goal:.0f} мл\n"
        f"📈 Прогресс: {progress}%",
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", WaterStates.confirming)
async def cancel_water(callback: CallbackQuery, state: FSMContext):
    """Отмена добавления воды"""
    await state.clear()
    await callback.message.edit_text("❌ Отменено")
    await callback.answer()


@router.message(Command("water_stats"))
async def cmd_water_stats(message: Message):
    """Статистика потребления воды"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Сначала настрой профиль")
            return
        
        # За последнюю неделю
        week_ago = datetime.now() - timedelta(days=7)
        result = await session.execute(
            select(WaterEntry).where(
                WaterEntry.user_id == user_id,
                WaterEntry.datetime >= week_ago
            )
        )
        entries = result.scalars().all()
        
        if not entries:
            await message.answer("📊 Нет данных о потреблении воды за последнюю неделю")
            return
        
        # Группировка по дням
        from collections import defaultdict
        daily = defaultdict(float)
        for e in entries:
            day = e.datetime.date()
            daily[day] += e.amount
        
        # Формируем отчёт
        text = "💧 <b>Потребление воды за 7 дней</b>\n\n"
        for day in sorted(daily.keys(), reverse=True):
            amount = daily[day]
            bar = "█" * int(amount / user.daily_water_goal * 10)
            text += f"{day.strftime('%d.%m')}: {amount:.0f} мл {bar}\n"
        
        avg = sum(daily.values()) / len(daily)
        text += f"\n📊 Среднее: {avg:.0f} мл/день\n"
        text += f"🎯 Норма: {user.daily_water_goal:.0f} мл/день"
        
        await message.answer(text, parse_mode="HTML")
