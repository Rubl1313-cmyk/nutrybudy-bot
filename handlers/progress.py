"""
Обработчик прогресса и графиков
✅ Исправлено: добавлен импорт WeightStates
"""
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from datetime import datetime, timedelta
from database.db import get_session
from database.models import User, Meal, Activity, WaterEntry, WeightEntry
from services.plots import generate_weight_plot, generate_water_plot, generate_calorie_balance_plot
from services.calculator import calculate_calorie_balance
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import WeightStates  # ✅ ВАЖНО: импорт состояния для веса!

router = Router()


@router.message(Command("progress"))
@router.message(F.text == "📊 Прогресс")
async def cmd_progress(message: Message):
    """Показать прогресс и графики"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        # ✅ ПРОВЕРКА: есть ли профиль
        user = await session.get(User, user_id)
        
        if not user or not user.weight or not user.height:
            await message.answer(
                "❌ <b>Сначала настройте профиль!</b>\n\n"
                "Нажмите 👤 Профиль или введите /set_profile\n"
                "Это нужно для расчёта ваших индивидуальных норм.",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            return
        
        today = datetime.now().date()
        
        # Считаем потреблённые калории за сегодня
        meals_result = await session.execute(
            select(func.sum(Meal.total_calories)).where(
                Meal.user_id == user_id,
                func.date(Meal.datetime) == today
            )
        )
        consumed = meals_result.scalar() or 0
        
        # Считаем сожжённые калории за сегодня
        activities_result = await session.execute(
            select(func.sum(Activity.calories_burned)).where(
                Activity.user_id == user_id,
                func.date(Activity.datetime) == today
            )
        )
        burned = activities_result.scalar() or 0
        
        # Считаем выпитую воду за сегодня
        water_result = await session.execute(
            select(func.sum(WaterEntry.amount)).where(
                WaterEntry.user_id == user_id,
                func.date(WaterEntry.datetime) == today
            )
        )
        water = water_result.scalar() or 0
        
        # Рассчитываем баланс
        balance = calculate_calorie_balance(consumed, burned, user.daily_calorie_goal)
        
        # Формируем сообщение
        text = (
            f"📊 <b>Прогресс за сегодня</b>\n\n"
            f"🔥 <b>Калории:</b>\n"
            f"   Потреблено: {balance['consumed']} ккал\n"
            f"   Сожжено: {balance['burned']} ккал\n"
            f"   Баланс: {balance['balance']} ккал\n"
            f"   Осталось: {balance['remaining']} ккал\n"
            f"   Статус: {balance['status']}\n\n"
            f"💧 <b>Вода:</b> {water} / {user.daily_water_goal} мл\n"
        )
        
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        
        # Генерируем графики
        weight_plot = await generate_weight_plot(user_id, session)
        if weight_plot:
            await message.answer_photo(
                BufferedInputFile(weight_plot, filename="weight.png"),
                caption="📈 Динамика веса"
            )
        
        calorie_plot = await generate_calorie_balance_plot(user_id, session)
        if calorie_plot:
            await message.answer_photo(
                BufferedInputFile(calorie_plot, filename="calories.png"),
                caption="🔥 Баланс калорий за 7 дней"
            )


@router.message(Command("log_weight"))
async def cmd_log_weight(message: Message, state: FSMContext):
    """Быстрая запись веса"""
    await state.set_state(WeightStates.entering_weight)
    await message.answer(
        "⚖️ Введите ваш вес в кг:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(WeightStates.entering_weight, F.text)  # ✅ Теперь WeightStates определён!
async def process_weight_log(message: Message, state: FSMContext):
    """Сохранение веса"""
    try:
        weight = float(message.text.replace(',', '.'))
        
        async with get_session() as session:
            # Записываем в историю
            entry = WeightEntry(
                user_id=message.from_user.id,
                weight=weight,
                datetime=datetime.now()
            )
            session.add(entry)
            
            # Обновляем текущий вес пользователя
            user = await session.get(User, message.from_user.id)
            if user:
                user.weight = weight
            await session.commit()
        
        await state.clear()
        await message.answer(
            f"✅ Вес {weight} кг записан!",
            reply_markup=get_main_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите корректное число")
