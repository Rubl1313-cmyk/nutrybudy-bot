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
from utils.premium_templates import weight_card, weight_trend_card
from utils.ui_templates import ProgressBar

logger = logging.getLogger(__name__)
router = Router()

class WeightStates(StatesGroup):
    """Состояния для записи веса"""
    waiting_for_weight = State()
    waiting_for_body_fat = State()
    waiting_for_muscle_mass = State()

@router.message(Command("weight"))
@router.message(Command("вес"))
async def cmd_weight(message: Message, state: FSMContext):
    """Запись веса"""
    await state.clear()
    
    text = "⚖️ <b>Запись веса</b>\n\n"
    text += "Введите ваш вес в кг (например: 70.5):\n\n"
    text += "💡 <b>Советы для точных измерений:</b>\n"
    text += "• Взвешивайтесь утром натощак\n"
    text += "• После посещения туалета\n"
    text += "• Без одежды и обуви\n"
    text += "• Используйте одни и те же весы\n\n"
    text += "📊 <b>Дополнительно можно записать:</b>\n"
    text += "• % жировой массы\n"
    text += "• Мышечная масса\n"
    text += "• % воды в организме\n\n"
    text += "🔢 <b>Введите вес:</b>"
    
    await message.answer(text)
    await state.set_state(WeightStates.waiting_for_weight)

@router.message(WeightStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка ввода веса"""
    try:
        weight = float(message.text.replace(',', '.'))
        
        if weight <= 0:
            await message.answer("❌ Вес должен быть положительным числом. Попробуйте еще раз:")
            return
        
        if weight > 300:
            await message.answer("❌ Слишком большой вес. Максимум 300 кг. Попробуйте еще раз:")
            return
        
        # Сохраняем вес
        await state.update_data(weight=weight)
        
        # Предлагаем записать дополнительные параметры
        from keyboards.reply_v2 import get_cancel_keyboard
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Только вес")],
                [KeyboardButton(text="📊 + % жира"), KeyboardButton(text="💪 + мышечная масса")],
                [KeyboardButton(text="🧬 + все параметры")]
            ],
            resize_keyboard=True
        )
        
        text = f"⚖️ <b>Вес записан: {weight} кг</b>\n\n"
        text += "Хотите добавить дополнительные параметры?\n\n"
        text += "📈 <b>Дополнительные параметры:</b>\n"
        text += "• % жировой массы - для отслеживания состава тела\n"
        text += "• Мышечная масса - для контроля мышц\n"
        text += "• % воды - для контроля гидратации\n\n"
        text += "💡 <b>Рекомендация:</b> Для точного трекинга веса достаточно только веса"
        
        await message.answer(text, reply_markup=keyboard)
        
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число (например: 70.5):")

@router.message()
async def handle_weight_options(message: Message, state: FSMContext):
    """Обработка выбора дополнительных параметров"""
    text = message.text.lower()
    
    if "только вес" in text:
        # Сохраняем только вес
        await save_weight_entry(message, state)
    elif "жира" in text:
        await state.set_state(WeightStates.waiting_for_body_fat)
        await message.answer(
            "📊 <b>% жировой массы</b>\n\n"
            "Введите процент жира в организме (например: 15.5):\n\n"
            "💡 <b>Нормы:</b>\n"
            "• Мужчины: 10-20%\n"
            "• Женщины: 18-28%"
        )
    elif "мышечная" in text:
        await state.set_state(WeightStates.waiting_for_muscle_mass)
        await message.answer(
            "💪 <b>Мышечная масса</b>\n\n"
            "Введите мышечную массу в кг (например: 35.5):\n\n"
            "💡 <b>Средние значения:</b>\n"
            "• Мужчины: 35-45 кг\n"
            "• Женщины: 25-35 кг"
        )
    elif "все параметры" in text:
        await state.set_state(WeightStates.waiting_for_body_fat)
        await message.answer(
            "📊 <b>% жировой массы</b>\n\n"
            "Введите процент жира в организме (например: 15.5):"
        )
    else:
        await message.answer("❌ Пожалуйста, выберите вариант из меню")

@router.message(WeightStates.waiting_for_body_fat)
async def process_body_fat(message: Message, state: FSMContext):
    """Обработка % жировой массы"""
    try:
        body_fat = float(message.text.replace(',', '.'))
        
        if body_fat <= 0:
            await message.answer("❌ Процент должен быть положительным числом. Попробуйте еще раз:")
            return
        
        if body_fat > 60:
            await message.answer("❌ Слишком большой процент. Максимум 60%. Попробуйте еще раз:")
            return
        
        # Сохраняем % жира
        await state.update_data(body_fat=body_fat)
        
        # Проверяем, нужно ли еще параметры
        data = await state.get_data()
        if "muscle_mass" not in data:
            await state.set_state(WeightStates.waiting_for_muscle_mass)
            await message.answer(
                "💪 <b>Мышечная масса</b>\n\n"
                "Введите мышечную массу в кг (например: 35.5):"
            )
        else:
            # Все параметры собраны, сохраняем
            await save_weight_entry(message, state)
            
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число (например: 15.5):")

@router.message(WeightStates.waiting_for_muscle_mass)
async def process_muscle_mass(message: Message, state: FSMContext):
    """Обработка мышечной массы"""
    try:
        muscle_mass = float(message.text.replace(',', '.'))
        
        if muscle_mass <= 0:
            await message.answer("❌ Масса должна быть положительным числом. Попробуйте еще раз:")
            return
        
        if muscle_mass > 150:
            await message.answer("❌ Слишком большая масса. Максимум 150 кг. Попробуйте еще раз:")
            return
        
        # Сохраняем мышечную массу
        await state.update_data(muscle_mass=muscle_mass)
        
        # Сохраняем запись
        await save_weight_entry(message, state)
        
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число (например: 35.5):")

async def save_weight_entry(message: Message, state: FSMContext):
    """Сохранение записи веса"""
    try:
        data = await state.get_data()
        weight = data['weight']
        
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
            
            # Создаем запись о весе
            weight_entry = WeightEntry(
                user_id=user.telegram_id,
                weight=weight,
                body_fat=data.get('body_fat'),
                muscle_mass=data.get('muscle_mass'),
                body_water=data.get('body_water')
            )
            
            session.add(weight_entry)
            await session.commit()
            
            # Получаем статистику веса
            weight_stats = await get_weight_stats(user.telegram_id)
            
            # Создаем красивую карточку
            card = weight_card(weight, weight_stats, user)
            
            await message.answer(card, reply_markup=get_main_keyboard_v2())
            
            # Проверяем достижения
            from handlers.achievements import check_achievements
            await check_achievements(user.telegram_id, 'weight', weight)
            
            await state.clear()
            
    except Exception as e:
        logger.error(f"Error saving weight entry: {e}")
        await message.answer(
            "❌ Произошла ошибка сохранения. Попробуйте еще раз:",
            reply_markup=get_main_keyboard_v2()
        )
        await state.clear()

@router.message(Command("weight_stats"))
@router.message(Command("статистика_веса"))
async def cmd_weight_stats(message: Message):
    """Статистика веса"""
    user_id = message.from_user.id
    
    # Получаем статистику
    stats = await get_weight_stats(user_id)
    
    if not stats or stats['total_entries'] == 0:
        text = "📊 <b>Статистика веса</b>\n\n"
        text += "У вас еще нет записей веса.\n\n"
        text += "🚀 <b>Начните отслеживать:</b> /weight"
        
        await message.answer(text)
        return
    
    text = "📊 <b>Статистика веса</b>\n\n"
    
    # Основные показатели
    text += f"⚖️ <b>Текущий вес:</b> {stats['current_weight']} кг\n"
    text += f"📈 <b>Начальный вес:</b> {stats['start_weight']} кг\n"
    text += f"🎯 <b>Целевой вес:</b> {stats.get('goal_weight', 'не указан')} кг\n\n"
    
    # Изменения
    if stats.get('weight_change'):
        change = stats['weight_change']
        emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        text += f"{emoji} <b>Общее изменение:</b> {abs(change):.1f} кг\n\n"
    
    # За разные периоды
    if stats.get('week_change'):
        week_change = stats['week_change']
        emoji = "📈" if week_change > 0 else "📉" if week_change < 0 else "➡️"
        text += f"📆 <b>За неделю:</b> {emoji} {abs(week_change):.1f} кг\n"
    
    if stats.get('month_change'):
        month_change = stats['month_change']
        emoji = "📈" if month_change > 0 else "📉" if month_change < 0 else "➡️"
        text += f"🗓️ <b>За месяц:</b> {emoji} {abs(month_change):.1f} кг\n"
    
    text += f"\n📅 <b>Всего записей:</b> {stats['total_entries']}\n"
    text += f"📊 <b>Средний вес:</b> {stats['average_weight']:.1f} кг\n"
    
    # Тренд
    if stats.get('trend'):
        trend = stats['trend']
        if trend == 'increasing':
            text += f"\n📈 <b>Тренд:</b> Вес увеличивается"
        elif trend == 'decreasing':
            text += f"\n📉 <b>Тренд:</b> Вес снижается"
        else:
            text += f"\n➡️ <b>Тренд:</b> Вес стабилен"
    
    # Прогресс к цели
    if stats.get('goal_weight') and stats.get('start_weight'):
        goal_progress = calculate_goal_progress(stats['current_weight'], stats['start_weight'], stats['goal_weight'])
        progress_bar = ProgressBar.create_modern_bar(goal_progress, 100, 15, 'default')
        
        text += f"\n🎯 <b>Прогресс к цели:</b>\n"
        text += f"   {progress_bar}\n"
        text += f"   Осталось: {abs(stats['goal_weight'] - stats['current_weight']):.1f} кг\n"
    
    # Мотивация
    text += get_weight_motivation(stats)
    
    await message.answer(text)

@router.message(Command("weight_chart"))
@router.message(Command("график_веса"))
async def cmd_weight_chart(message: Message):
    """График веса"""
    user_id = message.from_user.id
    
    # Получаем данные для графика
    chart_data = await get_weight_chart_data(user_id)
    
    if not chart_data:
        text = "📈 <b>График веса</b>\n\n"
        text += "Недостаточно данных для построения графика.\n\n"
        text += "📊 <b>Нужно минимум 3 записи веса</b>\n"
        text += "🚀 <b>Записывайте вес регулярно:</b> /weight"
        
        await message.answer(text)
        return
    
    text = "📈 <b>График веса</b>\n\n"
    
    # Показываем последние 10 записей
    recent_data = chart_data[-10:]
    
    for entry in recent_data:
        date = entry['date'].strftime('%d.%m')
        weight = entry['weight']
        change = entry.get('change', 0)
        
        if change > 0:
            change_str = f" (+{change:.1f})"
        elif change < 0:
            change_str = f" ({change:.1f})"
        else:
            change_str = ""
        
        text += f"📅 {date}: {weight:.1f} кг{change_str}\n"
    
    text += f"\n📊 <b>Период:</b> {recent_data[0]['date'].strftime('%d.%m')} - {recent_data[-1]['date'].strftime('%d.%m')}\n"
    
    # Тренд
    if len(chart_data) >= 3:
        trend = calculate_weight_trend(chart_data)
        if trend > 0.1:
            text += "📈 <b>Тренд:</b> Рост\n"
        elif trend < -0.1:
            text += "📉 <b>Тренд:</b> Снижение\n"
        else:
            text += "➡️ <b>Тренд:</b> Стабильно\n"
    
    await message.answer(text)

# Вспомогательные функции

async def get_weight_stats(user_id: int) -> dict:
    """Получить статистику веса"""
    from datetime import datetime, timezone, timedelta
    
    async with get_session() as session:
        # Получаем все записи веса
        result = await session.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user_id
            ).order_by(WeightEntry.created_at.desc())
        )
        entries = result.scalars().all()
        
        if not entries:
            return {}
        
        # Основная статистика
        current_weight = entries[0].weight
        start_weight = entries[-1].weight
        total_entries = len(entries)
        average_weight = sum(e.weight for e in entries) / total_entries
        
        # Изменения
        weight_change = current_weight - start_weight
        
        # За неделю
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        week_entries = [e for e in entries if e.created_at >= week_ago]
        if len(week_entries) >= 2:
            week_change = week_entries[0].weight - week_entries[-1].weight
        else:
            week_change = None
        
        # За месяц
        month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        month_entries = [e for e in entries if e.created_at >= month_ago]
        if len(month_entries) >= 2:
            month_change = month_entries[0].weight - month_entries[-1].weight
        else:
            month_change = None
        
        # Тренд
        trend = None
        if len(entries) >= 3:
            recent_weights = [e.weight for e in entries[:5]]  # Последние 5 записей
            if recent_weights[-1] > recent_weights[0]:
                trend = 'increasing'
            elif recent_weights[-1] < recent_weights[0]:
                trend = 'decreasing'
            else:
                trend = 'stable'
        
        return {
            'current_weight': current_weight,
            'start_weight': start_weight,
            'total_entries': total_entries,
            'average_weight': average_weight,
            'weight_change': weight_change,
            'week_change': week_change,
            'month_change': month_change,
            'trend': trend
        }

async def get_weight_chart_data(user_id: int) -> list:
    """Получить данные для графика веса"""
    from datetime import datetime, timezone
    
    async with get_session() as session:
        result = await session.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user_id
            ).order_by(WeightEntry.created_at.asc())
        )
        entries = result.scalars().all()
        
        chart_data = []
        for i, entry in enumerate(entries):
            data = {
                'date': entry.created_at,
                'weight': entry.weight
            }
            
            # Добавляем изменение относительно предыдущей записи
            if i > 0:
                data['change'] = entry.weight - entries[i-1].weight
            
            chart_data.append(data)
        
        return chart_data

def calculate_goal_progress(current: float, start: float, goal: float) -> float:
    """Рассчитать прогресс к цели в процентах"""
    if start == goal:
        return 100
    
    if start < goal:  # Набор массы
        total_change = goal - start
        current_change = current - start
    else:  # Похудение
        total_change = start - goal
        current_change = start - current
    
    progress = (current_change / total_change) * 100
    return max(0, min(100, progress))

def calculate_weight_trend(chart_data: list) -> float:
    """Рассчитать тренд веса (положительный - рост, отрицательный - снижение)"""
    if len(chart_data) < 3:
        return 0
    
    # Берем последние 5 записей
    recent = chart_data[-5:]
    weights = [entry['weight'] for entry in recent]
    
    # Простая линейная регрессия
    n = len(weights)
    x = list(range(n))
    
    sum_x = sum(x)
    sum_y = sum(weights)
    sum_xy = sum(x[i] * weights[i] for i in range(n))
    sum_x2 = sum(x[i] ** 2 for i in range(n))
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    
    return slope

def get_weight_motivation(stats: dict) -> str:
    """Получить мотивационное сообщение о весе"""
    if not stats:
        return "\n🌱 <b>Начните свой путь!</b> Первая запись веса - это уже победа!"
    
    weight_change = stats.get('weight_change', 0)
    
    if weight_change > 0:
        if stats.get('goal_weight') and stats['goal_weight'] < stats['start_weight']:
            return "\n⚠️ <b>Вес растет!</b> Если цель - похудеть, стоит пересмотреть питание"
        else:
            return "\n💪 <b>Отличный прогресс!</b> Вес увеличивается как и планировалось"
    elif weight_change < 0:
        return "\n🎉 <b>Отлично!</b> Вес снижается, вы на правильном пути!"
    else:
        return "\n⚖️ <b>Вес стабилен!</b> Продолжайте следовать плану"
