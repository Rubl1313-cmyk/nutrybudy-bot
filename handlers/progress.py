"""
Обработчик прогресса и графиков для NutriBuddy
✅ Исправлено: правильное получение пользователя по telegram_id
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from datetime import datetime, timedelta
from database.db import get_session
from database.models import User, Meal, Activity, WaterEntry, WeightEntry
from services.plots import generate_weight_plot, generate_water_plot, generate_calorie_balance_plot
from services.calculator import calculate_calorie_balance
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from keyboards.inline import get_progress_options_keyboard
from utils.states import WeightStates, ProgressStates

router = Router()


@router.message(Command("progress"))
@router.message(F.text == "📊 Прогресс")
async def cmd_progress(message: Message):
    """Показать прогресс и графики"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        # ✅ ИСПРАВЛЕНО: ищем по telegram_id, а не по id!
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        # Проверка: есть ли профиль и заполнен ли
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
        "⚖️ <b>Запись веса</b>\n\n"
        "Введи свой вес в кг:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(WeightStates.entering_weight, F.text)
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


@router.callback_query(F.data.startswith("progress_"))
async def process_progress_option(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа прогресса"""
    option = callback.data.split("_")[1]
    
    messages = {
        "weight": "📈 График веса будет доступен после 3+ записей",
        "water": "💧 График воды будет доступен после 3+ записей",
        "calories": "🔥 График калорий будет доступен после 3+ дней",
        "activity": "🏃 График активности будет доступен после 3+ тренировок"
    }
    
    await callback.message.edit_text(
        messages.get(option, "📊 Данные собираются..."),
        reply_markup=get_main_keyboard()
    )
    await callback.answer()
    await state.clear()
