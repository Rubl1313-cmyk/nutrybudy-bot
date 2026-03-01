"""
Обработчик активности и фитнес-данных для NutriBuddy
✅ Синхронизирован с utils/states.py
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from datetime import datetime, timedelta
from database.db import get_session
from database.models import User, Activity
from keyboards.inline import (
    get_fitness_source_keyboard,
    get_activity_type_keyboard,
    get_confirmation_keyboard
)
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import ActivityStates

router = Router()


@router.message(Command("fitness"))
@router.message(F.text == "🏋️ Активность")
async def cmd_fitness(message: Message, state: FSMContext):
    """Начало записи активности"""
    await state.clear()
    await state.set_state(ActivityStates.choosing_source)
    
    await message.answer(
        "🏋️ <b>Запись активности</b>\n\n"
        "Выберите источник данных:",
        reply_markup=get_fitness_source_keyboard()
    )


@router.callback_query(F.data.startswith("fitness_"), ActivityStates.choosing_source)
async def process_source(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора источника"""
    source = callback.data.split("_")[1]
    await state.update_data(source=source)
    
    if source == "manual":
        await state.set_state(ActivityStates.manual_type)
        await callback.message.edit_text(
            "🏃 <b>Тип активности</b>\n\n"
            "Выберите тип или введите вручную:",
            reply_markup=get_activity_type_keyboard()
        )
    elif source == "gpx":
        await state.set_state(ActivityStates.waiting_gpx)
        await callback.message.edit_text(
            "📁 <b>Загрузка GPX</b>\n\n"
            "Отправьте файл в формате .gpx"
        )
    else:
        # Apple Watch / Google Fit — заглушка
        await callback.answer("🔜 Синхронизация в разработке", show_alert=True)
    
    await callback.answer()


@router.message(ActivityStates.waiting_gpx, F.document)
async def process_gpx(message: Message, state: FSMContext):
    """Обработка загрузки GPX файла"""
    doc = message.document
    if not doc.file_name.endswith('.gpx'):
        await message.answer("❌ Пожалуйста, отправьте файл в формате .gpx")
        return
    
    await message.answer("🔄 Обрабатываю файл...")
    
    # Заглушка: в реальной версии здесь парсинг GPX
    await state.update_data(
        duration=30,
        distance=5.0,
        calories=300,
        activity_type="running"
    )
    await state.set_state(ActivityStates.confirming)
    
    await message.answer(
        "✅ <b>Данные из GPX:</b>\n\n"
        "🏃 Бег\n"
        "⏱️ 30 минут\n"
        "📍 5.0 км\n"
        "🔥 300 ккал\n\n"
        "Подтвердить?",
        reply_markup=get_confirmation_keyboard()
    )


@router.callback_query(F.data.startswith("activity_"), ActivityStates.manual_type)
async def process_activity_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа активности"""
    act_type = callback.data.split("_")[1]
    await state.update_data(activity_type=act_type)
    await state.set_state(ActivityStates.manual_duration)
    
    await callback.message.edit_text(
        f"✅ Тип: <b>{act_type}</b>\n\n"
        "⏱️ Введите длительность в минутах:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ActivityStates.manual_duration, F.text)
async def process_duration(message: Message, state: FSMContext):
    """Ввод длительности"""
    try:
        duration = int(message.text.strip())
        if not 1 <= duration <= 1440:
            raise ValueError
            
        await state.update_data(duration=duration)
        await state.set_state(ActivityStates.manual_distance)
        
        await message.answer(
            f"✅ Длительность: <b>{duration} мин</b>\n\n"
            "📍 Введите дистанцию в км (или 0):"
        )
    except ValueError:
        await message.answer("❌ Введите число от 1 до 1440 минут")


@router.message(ActivityStates.manual_distance, F.text)
async def process_distance(message: Message, state: FSMContext):
    """Ввод дистанции"""
    try:
        distance = float(message.text.replace(',', '.').strip())
        if not 0 <= distance <= 100:
            raise ValueError
            
        await state.update_data(distance=distance)
        await state.set_state(ActivityStates.manual_calories)
        
        await message.answer(
            f"✅ Дистанция: <b>{distance} км</b>\n\n"
            "🔥 Введите сожжённые калории (или 0 для авто-расчёта):"
        )
    except ValueError:
        await message.answer("❌ Введите число от 0 до 100 км")


@router.message(ActivityStates.manual_calories, F.text)
async def process_calories(message: Message, state: FSMContext):
    """Ввод калорий"""
    try:
        calories = int(message.text.strip())
        if not 0 <= calories <= 5000:
            raise ValueError
            
        await state.update_data(calories=calories)
        await state.set_state(ActivityStates.confirming)
        
        data = await state.get_data()
        
        await message.answer(
            "✅ <b>Подтверждение</b>\n\n"
            f"🏃 {data['activity_type']}\n"
            f"⏱️ {data['duration']} мин\n"
            f"📍 {data['distance']} км\n"
            f"🔥 {data['calories']} ккал\n\n"
            "Всё верно?",
            reply_markup=get_confirmation_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите число от 0 до 5000 ккал")


@router.callback_query(F.data == "confirm", ActivityStates.confirming)
async def confirm_activity(callback: CallbackQuery, state: FSMContext):
    """Сохранение активности"""
    data = await state.get_data()
    user_id = callback.from_user.id
    
    async with get_session() as session:
        activity = Activity(
            user_id=user_id,
            activity_type=data['activity_type'],
            duration=data['duration'],
            distance=data['distance'],
            calories_burned=data['calories'],
            steps=data.get('steps', 0),
            datetime=datetime.now(),
            source=data.get('source', 'manual')
        )
        session.add(activity)
        await session.commit()
    
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ <b>Активность записана!</b>\n\n"
        f"🔥 +{data['calories']} ккал к сегодняшнему балансу",
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", ActivityStates.confirming)
async def cancel_activity(callback: CallbackQuery, state: FSMContext):
    """Отмена записи активности"""
    await state.clear()
    await callback.message.edit_text("❌ Запись отменена.")
    await callback.answer()


@router.message(Command("today_activity"))
async def cmd_today_activity(message: Message):
    """Показать активность за сегодня"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        today = datetime.now().date()
        
        result = await session.execute(
            select(
                func.sum(Activity.duration),
                func.sum(Activity.distance),
                func.sum(Activity.calories_burned)
            ).where(
                Activity.user_id == user_id,
                func.date(Activity.datetime) == today
            )
        )
        
        duration, distance, calories = result.one()
        
        if not duration:
            await message.answer(
                "🏋️ <b>Сегодня нет записей активности</b>\n\n"
                "Нажми 🏋️ Активность, чтобы добавить тренировку",
                parse_mode="HTML"
            )
            return
        
        await message.answer(
            f"🏋️ <b>Активность за сегодня</b>\n\n"
            f"⏱️ Всего: {duration} минут\n"
            f"📍 Дистанция: {distance:.1f} км\n"
            f"🔥 Сожжено: {calories:.0f} ккал",
            parse_mode="HTML"
        )
