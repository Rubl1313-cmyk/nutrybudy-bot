"""
👞 Обработчик шагов для NutriBuddy Bot
✨ Современная система отслеживания шагов с геймификацией
🎯 Умная мотивация и красивый интерфейс
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from datetime import datetime
from typing import Optional

from database.db import get_session
from database.models import User, StepsEntry
from sqlalchemy import select
from utils.ui_templates import ProgressBar
from utils.message_templates import MessageTemplates

def calculate_steps_goal(user: User) -> int:
    """
    Рассчитывает цель по шагам на основе данных пользователя
    """
    # Базовые цели
    base_goals = {
        'sedentary': 6000,      # Сидячий образ жизни
        'light': 8000,          # Легкая активность
        'moderate': 10000,      # Умеренная активность
        'active': 12000,        # Активный образ жизни
        'very_active': 15000    # Очень активный
    }
    
    # Определяем базовую цель по уровню активности
    activity_level = user.activity_level or 'moderate'
    base_goal = base_goals.get(activity_level, 10000)
    
    # Корректировка по возрасту
    if user.age:
        if user.age < 30:
            age_factor = 1.1      # Молодежь может больше
        elif user.age < 50:
            age_factor = 1.0      # Стандарт
        elif user.age < 65:
            age_factor = 0.9      # Снижаем немного
        else:
            age_factor = 0.8      # Пожилым меньше
    else:
        age_factor = 1.0
    
    # Корректировка по полу
    if user.gender == 'male':
        gender_factor = 1.1       # Мужчины обычно больше ходят
    elif user.gender == 'female':
        gender_factor = 0.95      # Женщины немного меньше
    else:
        gender_factor = 1.0
    
    # Корректировка по цели (вес, поддержание, набор)
    if user.goal == 'lose_weight':
        goal_factor = 1.2         # Для похудения нужно больше
    elif user.goal == 'gain_weight':
        goal_factor = 0.9         # Для набора веса можно меньше
    else:
        goal_factor = 1.0         # Поддержание - стандарт
    
    # Итоговая цель
    final_goal = int(base_goal * age_factor * gender_factor * goal_factor)
    
    # Ограничиваем разумными пределами
    final_goal = max(4000, min(25000, final_goal))
    
    return final_goal

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("steps"))
async def cmd_steps(message: Message):
    """
    👞 Команда для записи шагов
    /steps - показывает меню шагов
    """
    user_id = message.from_user.id
    
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ <b>Сначала создайте профиль!</b>\n"
                "Используйте команду /set_profile",
                parse_mode="HTML"
            )
            return
        
        # Показываем красивое меню шагов
        await _show_steps_menu(message, user)

async def _show_steps_menu(message: Message, user: User):
    """Показывает современное меню шагов"""
    
    # Получаем шаги за сегодня
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    async with get_session() as session:
        steps_result = await session.execute(
            select(StepsEntry).where(
                (StepsEntry.user_id == user.id) &
                (StepsEntry.datetime >= today_start) &
                (StepsEntry.datetime <= today_end)
            )
        )
        today_steps = steps_result.scalars().all()
        
        total_steps = sum(steps.steps_count for steps in today_steps)
        goal_steps = user.daily_steps_goal or calculate_steps_goal(user)
        
        # Создаем красивый прогресс-бар
        steps_bar = ProgressBar.create_modern_bar(total_steps, goal_steps, 15, 'gradient')
        steps_percentage = min((total_steps / goal_steps * 100) if goal_steps > 0 else 0, 200)  # Ограничим 200%
        
        # Современное меню
        builder = InlineKeyboardBuilder()
        
        # Быстрые кнопки
        quick_values = [
            ("🚶 5,000", "steps_quick_5000"),
            ("🚶‍♀️ 10,000", "steps_quick_10000"),
            ("🏃 15,000", "steps_quick_15000"),
            ("🏃‍♂️ 20,000", "steps_quick_20000")
        ]
        
        for i, (text, callback) in enumerate(quick_values):
            if i % 2 == 0:
                row = [InlineKeyboardButton(text=text, callback_data=callback)]
            else:
                row.append(InlineKeyboardButton(text=text, callback_data=callback))
                builder.row(*row)
        
        # Дополнительные кнопки
        builder.row(
            InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="steps_manual"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="steps_stats")
        )
        
        builder.row(InlineKeyboardButton(text="⚙️ Настроить цель", callback_data="steps_set_goal"))
        builder.row(InlineKeyboardButton(text="🧠 Рассчитать цель", callback_data="steps_auto_goal"))
        
        # Красивое сообщение
        welcome_text = (
            f"👞 <b>Трекер шагов</b>\n"
            f"{'═' * 35}\n\n"
            f"📅 <b>Сегодня</b>\n"
            f"👶 Шаги: {total_steps:,} из {goal_steps:,}\n"
            f"{steps_bar} {steps_percentage:.1f}%\n\n"
            f"💡 <b>Запишите свои шаги:</b>"
        )
        
        await message.answer(welcome_text, reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data.startswith("steps_quick_"))
async def steps_quick_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик быстрых кнопок шагов"""
    try:
        steps_count = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await callback.answer("❌ Пользователь не найден", show_alert=True)
                return
            
            # Сохраняем шаги
            steps_entry = StepsEntry(
                user_id=user.id,
                steps_count=steps_count,
                source='quick_button'
            )
            session.add(steps_entry)
            await session.commit()
            
            # Показываем результат
            await _show_steps_result(callback, user, steps_count)
            
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка в steps_quick_callback: {e}")
        await callback.answer("❌ Неверное значение шагов", show_alert=True)

@router.callback_query(F.data == "steps_manual")
async def steps_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Начинает ручной ввод шагов"""
    await callback.answer()
    
    await callback.message.edit_text(
        "✏️ <b>Введите количество шагов:</b>\n\n"
        "Например: 8500 или 12,345",
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние ожидания ввода
    await state.set_state("waiting_steps_input")

@router.message(F.text, F.state == "waiting_steps_input")
async def steps_input_handler(message: Message, state: FSMContext):
    """Обработчик ручного ввода шагов"""
    current_state = await state.get_state()
    
    if current_state != "waiting_steps_input":
        return
    
    try:
        # Очищаем текст от лишних символов
        steps_text = message.text.replace(",", "").replace(" ", "").replace("\u202f", "")
        steps_count = int(steps_text)
        
        if steps_count < 0 or steps_count > 100000:
            await message.answer(
                "❌ <b>Неверное значение!</b>\n"
                "Введите количество шагов от 0 до 100,000",
                parse_mode="HTML"
            )
            return
        
        user_id = message.from_user.id
        
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await message.answer("❌ Пользователь не найден")
                await state.clear()
                return
            
            # Сохраняем шаги
            steps_entry = StepsEntry(
                user_id=user.id,
                steps_count=steps_count,
                source='manual',
                notes=f"Введено: {message.text}"
            )
            session.add(steps_entry)
            await session.commit()
            
            # Показываем результат
            await _show_steps_result(message, user, steps_count)
            
    except ValueError:
        await message.answer(
            "❌ <b>Неверный формат!</b>\n"
            "Введите число, например: 8500",
            parse_mode="HTML"
        )
    finally:
        await state.clear()

@router.callback_query(F.data == "steps_stats")
async def steps_stats_callback(callback: CallbackQuery):
    """Показывает статистику шагов"""
    user_id = callback.from_user.id
    
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Получаем статистику за последние 7 дней
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        
        steps_result = await session.execute(
            select(StepsEntry).where(
                (StepsEntry.user_id == user.id) &
                (StepsEntry.datetime >= week_ago)
            ).order_by(StepsEntry.datetime.desc())
        )
        steps_entries = steps_result.scalars().all()
        
        if not steps_entries:
            await callback.answer("📊 Пока нет записей о шагах", show_alert=True)
            return
        
        # Статистика
        total_week = sum(steps.steps_count for steps in steps_entries)
        avg_daily = total_week / 7 if steps_entries else 0
        max_steps = max(steps.steps_count for steps in steps_entries) if steps_entries else 0
        
        # Сегодняшние шаги
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_steps = sum(steps.steps_count for steps in steps_entries if steps.datetime >= today_start)
        
        stats_text = (
            f"📊 <b>Статистика шагов</b>\n"
            f"{'═' * 35}\n\n"
            f"📅 <b>Последние 7 дней</b>\n"
            f"👶 Всего: {total_week:,} шагов\n"
            f"📈 В среднем: {avg_daily:.0f} шагов/день\n"
            f"🏆 Максимум: {max_steps:,} шагов\n\n"
            f"📅 <b>Сегодня</b>\n"
            f"👶 Шагов: {today_steps:,}\n"
            f"🎯 Цель: {user.daily_steps_goal or 10000:,} шагов\n"
        )
        
        await callback.message.edit_text(stats_text, parse_mode="HTML")
        await callback.answer()

@router.callback_query(F.data == "steps_auto_goal")
async def steps_auto_goal_callback(callback: CallbackQuery):
    """Рассчитывает и устанавливает цель по шагам на основе данных профиля"""
    user_id = callback.from_user.id
    
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Рассчитываем цель
        auto_goal = calculate_steps_goal(user)
        
        # Обновляем цель
        user.daily_steps_goal = auto_goal
        await session.commit()
        
        # Показываем результат с объяснением
        explanation = (
            f"🧠 <b>Автоматический расчет цели</b>\n\n"
            f"📊 <b>Ваши данные:</b>\n"
            f"👤 Пол: {user.gender or 'не указан'}\n"
            f"🎂 Возраст: {user.age or 'не указан'}\n"
            f"🏃 Активность: {user.activity_level or 'умеренная'}\n"
            f"🎯 Цель: {user.goal or 'поддержание'}\n\n"
            f"🎯 <b>Рассчитанная цель: {auto_goal:,} шагов</b>\n\n"
            f"💡 <b>Как рассчитано:</b>\n"
            f"• База: {user.activity_level or 'умеренная'} активность\n"
            f"• Корректировка по возрасту и полу\n"
            f"• Учет цели (похудение/набор/поддержание)\n\n"
            f"✅ <b>Цель установлена!</b>\n"
            f"Можете изменить её в любой момент через ⚙️ Настроить цель"
        )
        
        await callback.message.edit_text(explanation, parse_mode="HTML")
        await callback.answer()

@router.callback_query(F.data == "steps_set_goal")
async def steps_set_goal_callback(callback: CallbackQuery, state: FSMContext):
    """Начинает установку цели по шагам"""
    await callback.answer()
    
    await callback.message.edit_text(
        "⚙️ <b>Установите цель по шагам:</b>\n\n"
        "Рекомендуемая цель: 10,000 шагов в день\n\n"
        "Введите новое значение (например: 8000, 12000, 15000):",
        parse_mode="HTML"
    )
    
    await state.set_state("waiting_steps_goal")

@router.message(F.text, F.state == "waiting_steps_goal")
async def steps_goal_input_handler(message: Message, state: FSMContext):
    """Обработчик установки цели по шагам"""
    current_state = await state.get_state()
    
    if current_state != "waiting_steps_goal":
        return
    
    try:
        steps_text = message.text.replace(",", "").replace(" ", "").replace("\u202f", "")
        goal_steps = int(steps_text)
        
        if goal_steps < 1000 or goal_steps > 50000:
            await message.answer(
                "❌ <b>Неверное значение!</b>\n"
                "Введите цель от 1,000 до 50,000 шагов",
                parse_mode="HTML"
            )
            return
        
        user_id = message.from_user.id
        
        async with get_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await message.answer("❌ Пользователь не найден")
                await state.clear()
                return
            
            # Обновляем цель
            user.daily_steps_goal = goal_steps
            await session.commit()
            
            success_text = (
                f"✅ <b>Цель обновлена!</b>\n\n"
                f"🎯 Новая цель: {goal_steps:,} шагов в день\n"
                f"💪 Отличная мотивация для достижения результатов!"
            )
            
            await message.answer(success_text, parse_mode="HTML")
            
    except ValueError:
        await message.answer(
            "❌ <b>Неверный формат!</b>\n"
            "Введите число, например: 10000",
            parse_mode="HTML"
        )
    finally:
        await state.clear()

async def _show_steps_result(message: Message, user: User, steps_count: int):
    """Показывает результат записи шагов"""
    
    # Получаем общее количество шагов за сегодня
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    async with get_session() as session:
        steps_result = await session.execute(
            select(StepsEntry).where(
                (StepsEntry.user_id == user.id) &
                (StepsEntry.datetime >= today_start) &
                (StepsEntry.datetime <= today_end)
            )
        )
        today_steps = steps_result.scalars().all()
        
        total_steps = sum(steps.steps_count for steps in today_steps)
        goal_steps = user.daily_steps_goal or calculate_steps_goal(user)
        
        # Прогресс-бар
        steps_bar = ProgressBar.create_modern_bar(total_steps, goal_steps, 15, 'gradient')
        steps_percentage = min((total_steps / goal_steps * 100) if goal_steps > 0 else 0, 200)  # Ограничим 200%
        
        # Умная мотивация
        if steps_percentage >= 150:
            motivation = "🏆 <b>Супер-чемпион!</b> Вы превзошли все ожидания!"
        elif steps_percentage >= 120:
            motivation = "🌟 <b>Феноменально!</b> Вы на невероятном уровне!"
        elif steps_percentage >= 100:
            motivation = "🏆 <b>Цель достигнута!</b> Вы потрясающе двигаетесь!"
        elif steps_percentage >= 80:
            motivation = "🔥 <b>Отлично!</b> Почти у цели, продолжайте!"
        elif steps_percentage >= 50:
            motivation = "💪 <b>Хорошая работа!</b> Вы на правильном пути!"
        else:
            remaining = goal_steps - total_steps
            motivation = f"🚶 <b>Хорошее начало!</b> Осталось еще {remaining:,} шагов."
        
        result_text = (
            f"✅ <b>Шаги записаны!</b>\n"
            f"{'═' * 35}\n\n"
            f"👶 Добавлено: {steps_count:,} шагов\n"
            f"📊 Всего за день: {total_steps:,} шагов\n"
            f"🎯 Цель: {goal_steps:,} шагов\n\n"
            f"{steps_bar} {steps_percentage:.1f}%\n\n"
            f"{motivation}"
        )
        
        await message.answer(result_text, parse_mode="HTML")
