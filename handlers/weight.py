"""
handlers/weight.py
Обработчики записи веса
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, WeightEntry
from keyboards.reply_v2 import get_main_keyboard_v2

logger = logging.getLogger(__name__)
router = Router()

class WeightStates(StatesGroup):
    """Состояния для записи веса"""
    waiting_for_weight = State()

@router.message(Command("log_weight"))
async def cmd_log_weight(message: Message, state: FSMContext):
    """Запись веса"""
    await state.clear()
    
    await message.answer(
        "⚖️ <b>Запись веса</b>\n\n"
        "Введите ваш текущий вес в килограммах:\n\n"
        "Пример: 70.5",
        parse_mode="HTML"
    )
    await state.set_state(WeightStates.waiting_for_weight)

@router.message(WeightStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка записи веса"""
    try:
        weight = float(message.text.replace(",", "."))
        
        if weight < 30 or weight > 300:
            await message.answer(
                "❌ Вес должен быть от 30 до 300 кг. Попробуйте еще раз:"
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
            
            # Создаем запись о весе
            weight_entry = WeightEntry(
                user_id=user.id,
                weight=weight,
                datetime=message.date
            )
            
            session.add(weight_entry)
            
            # Обновляем текущий вес в профиле
            user.weight = weight
            
            # Пересчитываем нормы КБЖУ с новым весом
            from services.calculator import calculate_calorie_goal, calculate_water_goal
            nutrition_goals = calculate_calorie_goal(
                weight=weight,
                height=user.height,
                age=user.age,
                gender=user.gender,
                activity_level=user.activity_level,
                goal=user.goal
            )
            
            # Распаковываем кортеж: (calories, protein_g, fat_g, carbs_g)
            user.daily_calorie_goal, user.daily_protein_goal, user.daily_fat_goal, user.daily_carbs_goal = nutrition_goals
            
            # Пересчитываем норму воды с реальной температурой
            temperature = 20.0  # По умолчанию
            try:
                from services.weather import get_temperature
                temperature = await get_temperature(user.city)
            except Exception as e:
                logger.warning(f"Не удалось получить температуру для {user.city}: {e}")
                temperature = 20.0
                
            water_goal = calculate_water_goal(
                weight=weight,
                activity_level=user.activity_level,
                temperature=temperature  # Реальная температура
            )
            user.daily_water_goal = water_goal
            
            await session.commit()
            
            # Получаем статистику
            await send_weight_statistics(message, user, session, weight)
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Введите корректное число. Попробуйте еще раз:")
    except Exception as e:
        logger.error(f"Ошибка при записи веса: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=get_main_keyboard_v2()
        )

async def send_weight_statistics(message: Message, user, session, current_weight):
    """Отправка статистики по весу"""
    from datetime import datetime, timedelta
    
    today = message.date
    
    # Вчера
    yesterday = today - timedelta(days=1)
    yesterday_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            WeightEntry.datetime == yesterday
        )
    )
    yesterday_weight = yesterday_result.scalar_one_or_none()
    
    # Неделя назад
    week_ago = today - timedelta(days=7)
    week_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            WeightEntry.datetime == week_ago
        )
    )
    week_weight = week_result.scalar_one_or_none()
    
    # Месяц назад
    month_ago = today - timedelta(days=30)
    month_result = await session.execute(
        select(WeightEntry.weight).where(
            WeightEntry.user_id == user.id,
            WeightEntry.datetime == month_ago
        )
    )
    month_weight = month_result.scalar_one_or_none()
    
    # Минимальный и максимальный вес за последние 30 дней
    thirty_days_ago = today - timedelta(days=30)
    min_max_result = await session.execute(
        select(
            func.min(WeightEntry.weight),
            func.max(WeightEntry.weight)
        ).where(
            WeightEntry.user_id == user.id,
            WeightEntry.datetime >= thirty_days_ago
        )
    )
    min_weight, max_weight = min_max_result.first()
    
    # Формируем сообщение
    message_text = f"✅ <b>Вес записан!</b>\n\n"
    message_text += f"⚖️ Текущий вес: {current_weight:.1f} кг\n\n"
    message_text += f"📊 <b>Изменения:</b>\n"
    
    if yesterday_weight:
        daily_change = current_weight - yesterday_weight
        emoji = "📈" if daily_change > 0 else "📉" if daily_change < 0 else "➡️"
        message_text += f"{emoji} За день: {daily_change:+.1f} кг\n"
    
    if week_weight:
        week_change = current_weight - week_weight
        emoji = "📈" if week_change > 0 else "📉" if week_change < 0 else "➡️"
        message_text += f"{emoji} За неделю: {week_change:+.1f} кг\n"
    
    if month_weight:
        month_change = current_weight - month_weight
        emoji = "📈" if month_change > 0 else "📉" if month_change < 0 else "➡️"
        message_text += f"{emoji} За месяц: {month_change:+.1f} кг\n"
    
    if min_weight and max_weight:
        message_text += f"\n📏 <b>За последние 30 дней:</b>\n"
        message_text += f"🔻 Минимум: {min_weight:.1f} кг\n"
        message_text += f"🔺 Максимум: {max_weight:.1f} кг\n"
        message_text += f"📊 Размах: {max_weight - min_weight:.1f} кг\n"
    
    # Мотивация
    if user.goal == "lose_weight":
        if week_weight and current_weight < week_weight:
            message_text += f"\n🎉 Отлично! Вес снижается!"
        else:
            message_text += f"\n💪 Продолжайте в том же духе!"
    elif user.goal == "gain_weight":
        if week_weight and current_weight > week_weight:
            message_text += f"\n🎉 Отлично! Вес растет!"
        else:
            message_text += f"\n💪 Продолжайте работать!"
    else:
        message_text += f"\n⚖️ Вес стабилен!"
    
    await message.answer(
        message_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("weight"))
async def cmd_weight(message: Message, state: FSMContext):
    """Статистика веса"""
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
        
        # Получаем последние записи веса
        from datetime import datetime, timedelta
        thirty_days_ago = message.date - timedelta(days=30)
        
        weight_result = await session.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user.id,
                WeightEntry.datetime >= thirty_days_ago
            ).order_by(WeightEntry.datetime.desc())
        )
        weight_entries = weight_result.scalars().all()
        
        if not weight_entries:
            await message.answer(
                "⚖️ <b>Статистика веса</b>\n\n"
                "У вас еще нет записей веса.\n\n"
                "Для добавления веса используйте /log_weight",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            return
        
        # Текущий вес
        current_weight = weight_entries[0].weight
        
        # Статистика
        message_text = f"⚖️ <b>Статистика веса</b>\n\n"
        message_text += f"📊 Текущий вес: {current_weight:.1f} кг\n"
        message_text += f"📅 Записей за 30 дней: {len(weight_entries)}\n\n"
        
        # Последние 7 записей
        message_text += f"📋 <b>Последние записи:</b>\n"
        for entry in weight_entries[:7]:
            date_str = entry.datetime.strftime("%d.%m")
            message_text += f"• {date_str}: {entry.weight:.1f} кг\n"
        
        await message.answer(
            message_text,
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "log_weight")
async def log_weight_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для записи веса из меню"""
    await callback.answer()
    
    await callback.message.answer(
        "⚖️ <b>Запись веса</b>\n\n"
        "Введите ваш текущий вес в килограммах:\n\n"
        "Пример: 70.5",
        parse_mode="HTML"
    )
    await state.set_state(WeightStates.waiting_for_weight)
