"""
handlers/activity.py
Обработчики учета активности
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from sqlalchemy import select

from database.db import get_session
from database.models import User, Activity
from keyboards.reply import get_main_keyboard

logger = logging.getLogger(__name__)
router = Router()

class ActivityStates(StatesGroup):
    """Состояния для записи активности"""
    waiting_for_activity_type = State()
    waiting_for_duration = State()
    waiting_for_calories = State()

@router.message(Command("fitness"))
async def cmd_fitness(message: Message, state: FSMContext):
    """Запись фитнес активности"""
    await state.clear()
    
    await message.answer(
        "🏃 <b>Запись фитнес активности</b>\n\n"
        "Выберите тип активности:\n\n"
        "• Бег\n"
        "• Ходьба\n"
        "• Велосипед\n"
        "• Плавание\n"
        "• Тренировка в зале\n"
        "• Йога\n"
        "• Другое\n\n"
        "Напишите название активности:",
        parse_mode="HTML"
    )
    await state.set_state(ActivityStates.waiting_for_activity_type)

@router.message(ActivityStates.waiting_for_activity_type)
async def process_activity_type(message: Message, state: FSMContext):
    """Обработка типа активности"""
    activity_type = message.text.strip()
    
    if not activity_type:
        await message.answer("❌ Напишите название активности:")
        return
    
    await state.update_data(activity_type=activity_type)
    
    await message.answer(
        f"⏱️ <b>Длительность активности (в минутах):</b>\n\n"
        f"Например: 30",
        parse_mode="HTML"
    )
    await state.set_state(ActivityStates.waiting_for_duration)

@router.message(ActivityStates.waiting_for_duration)
async def process_duration(message: Message, state: FSMContext):
    """Обработка длительности активности"""
    try:
        duration = int(message.text)
        
        if duration < 1 or duration > 480:  # Максимум 8 часов
            await message.answer(
                "❌ Длительность должна быть от 1 до 480 минут. Попробуйте еще раз:"
            )
            return
        
        await state.update_data(duration=duration)
        
        await message.answer(
            f"🔥 <b>Сожженные калории (опционально):</b>\n\n"
            f"Если знаете точное количество калорий, введите его.\n"
            f"Если нет, отправьте 0 и я рассчитаю автоматически.\n\n"
            f"Например: 250 или 0",
            parse_mode="HTML"
        )
        await state.set_state(ActivityStates.waiting_for_calories)
        
    except ValueError:
        await message.answer("❌ Введите корректное число. Попробуйте еще раз:")

@router.message(ActivityStates.waiting_for_calories)
async def process_calories(message: Message, state: FSMContext):
    """Обработка калорий и сохранение активности"""
    try:
        user_calories = int(message.text)
        
        if user_calories < 0 or user_calories > 5000:
            await message.answer(
                "❌ Некорректное количество калорий. Попробуйте еще раз:"
            )
            return
        
        # Получаем данные
        activity_data = await state.get_data()
        activity_type = activity_data['activity_type']
        duration = activity_data['duration']
        
        # Рассчитываем калории если не указаны
        if user_calories == 0:
            calories_burned = estimate_calories_burned(activity_type, duration)
        else:
            calories_burned = user_calories
        
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
                    reply_markup=get_main_keyboard()
                )
                return
            
            # Создаем запись об активности
            activity = Activity(
                user_id=user.id,
                activity_type=activity_type,
                duration=duration,
                calories_burned=calories_burned,
                datetime=message.date
            )
            
            session.add(activity)
            await session.commit()
        
        await state.clear()
        
        await message.answer(
            f"✅ <b>Активность записана!</b>\n\n"
            f"🏃 Тип: {activity_type}\n"
            f"⏱️ Длительность: {duration} минут\n"
            f"🔥 Сожжено калорий: {calories_burned} ккал\n\n"
            f"💪 Отличная работа!",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer("❌ Введите корректное число. Попробуйте еще раз:")
    except Exception as e:
        logger.error(f"Ошибка при записи активности: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )

def estimate_calories_burned(activity_type: str, duration: int) -> int:
    """Оценка сожженных калорий по типу активности"""
    # Базовые значения калорий в час для 70 кг человека
    calories_per_hour = {
        'бег': 600,
        'ходьба': 300,
        'велосипед': 500,
        'плавание': 400,
        'тренировка в зале': 450,
        'йога': 200,
        'другое': 350
    }
    
    activity_lower = activity_type.lower()
    
    # Ищем точное совпадение
    if activity_lower in calories_per_hour:
        base_calories = calories_per_hour[activity_lower]
    else:
        # Ищем частичное совпадение
        base_calories = 350  # По умолчанию
        for key, value in calories_per_hour.items():
            if key in activity_lower or activity_lower in key:
                base_calories = value
                break
    
    # Рассчитываем для указанной длительности
    calories_per_minute = base_calories / 60
    return int(calories_per_minute * duration)

@router.message(Command("activity"))
async def cmd_activity(message: Message, state: FSMContext):
    """Статистика активности"""
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
                reply_markup=get_main_keyboard()
            )
            return
        
        # Статистика за сегодня
        from datetime import datetime
        today = message.date
        
        activities_result = await session.execute(
            select(Activity).where(
                Activity.user_id == user.id,
                Activity.datetime >= today
            ).order_by(Activity.datetime.desc())
        )
        activities = activities_result.scalars().all()
        
        if not activities:
            await message.answer(
                "🏃 <b>Статистика активности</b>\n\n"
                "За сегодня еще нет записей активности.\n\n"
                "Для добавления активности используйте /fitness",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            return
        
        # Формируем статистику
        total_duration = sum(a.duration for a in activities)
        total_calories = sum(a.calories_burned or 0 for a in activities)
        
        message_text = (
            f"🏃 <b>Статистика активности за сегодня</b>\n\n"
            f"📊 Всего активностей: {len(activities)}\n"
            f"⏱️ Общая длительность: {total_duration} минут\n"
            f"🔥 Сожжено калорий: {total_calories} ккал\n\n"
            f"📋 <b>Последние активности:</b>\n"
        )
        
        for activity in activities[:5]:  # Показываем последние 5
            message_text += (
                f"• {activity.activity_type} - {activity.duration} мин ({activity.calories_burned} ккал)\n"
            )
        
        if len(activities) > 5:
            message_text += f"... и еще {len(activities) - 5} активностей"
        
        message_text += f"\n\nДля добавления активности используйте /fitness"
        
        await message.answer(
            message_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "log_activity")
async def log_activity_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для записи активности из меню"""
    await callback.answer()
    
    await callback.message.answer(
        "🏃 <b>Запись фитнес активности</b>\n\n"
        "Выберите тип активности:\n\n"
        "• Бег\n"
        "• Ходьба\n"
        "• Велосипед\n"
        "• Плавание\n"
        "• Тренировка в зале\n"
        "• Йога\n"
        "• Другое\n\n"
        "Напишите название активности:",
        parse_mode="HTML"
    )
    await state.set_state(ActivityStates.waiting_for_activity_type)
