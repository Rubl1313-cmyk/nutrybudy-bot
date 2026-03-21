"""
handlers/profile_new.py
Обработчики профиля - новая версия
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func

from database.db import get_session
from database.models import User, FoodEntry, DrinkEntry, ActivityEntry, WeightEntry
from keyboards.main_menu import get_main_menu, get_profile_menu
from utils.timezone_utils import get_user_local_date

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text.lower().in_(["👤 профиль", "профиль"]))
async def profile_main_handler(message: Message, state: FSMContext):
    """Главная кнопка Профиль"""
    await state.clear()
    
    await message.answer(
        "👤 <b>Профиль</b>\n\nВыберите действие:",
        reply_markup=get_profile_menu(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["📋 мои данные", "мои данные"]))
async def profile_my_data_handler(message: Message, state: FSMContext):
    """Мои данные - показ информации о профиле"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
    
    if not user:
        await message.answer(
            "❌ Профиль не найден. Сначала настройте профиль командой /set_profile",
            reply_markup=get_main_menu()
        )
        return
    
    # Считаем статистику
    today = get_user_local_date(user.timezone)
    
    food_count = await session.scalar(
        select(func.count(FoodEntry.id)).where(
            FoodEntry.user_id == user.id,
            func.date(FoodEntry.created_at) == today
        )
    )
    
    water_total = await session.scalar(
        select(func.sum(DrinkEntry.amount)).where(
            DrinkEntry.user_id == user.id,
            func.date(DrinkEntry.created_at) == today
        )
    ) or 0
    
    activity_count = await session.scalar(
        select(func.count(ActivityEntry.id)).where(
            ActivityEntry.user_id == user.id,
            func.date(ActivityEntry.created_at) == today
        )
    )
    
    text = f"📋 <b>Мои данные</b>\n\n"
    text += f"👤 <b>Имя:</b> {user.first_name or 'Не указано'}\n"
    text += f"🎂 <b>Возраст:</b> {user.age or 'Не указан'} лет\n"
    text += f"{'👨' if user.gender == 'male' else '👩' if user.gender == 'female' else '👤'} <b>Пол:</b> {user.gender or 'Не указан'}\n"
    text += f"📏 <b>Рост:</b> {user.height or 'Не указан'} см\n"
    text += f"⚖️ <b>Вес:</b> {user.weight or 'Не указан'} кг\n"
    text += f"🎯 <b>Цель:</b> {user.goal or 'Не указана'}\n"
    text += f"🏃 <b>Активность:</b> {user.activity_level or 'Не указана'}\n\n"
    text += f"📊 <b>Сегодня:</b>\n"
    text += f"• Приёмов пищи: {food_count}\n"
    text += f"• Воды выпито: {water_total} мл\n"
    text += f"• Активностей: {activity_count}\n\n"
    
    if user.daily_calorie_goal:
        text += f"🔥 <b>Нормы:</b>\n"
        text += f"• Калории: {user.daily_calorie_goal} ккал\n"
        text += f"• Белки: {user.daily_protein_goal} г\n"
        text += f"• Жиры: {user.daily_fat_goal} г\n"
        text += f"• Углеводы: {user.daily_carb_goal} г\n"
        text += f"• Вода: {user.daily_water_goal} мл\n"
    
    await message.answer(text, reply_markup=get_profile_menu(), parse_mode="HTML")

@router.message(F.text.lower().in_(["✏️ редактировать профиль", "редактировать профиль"]))
async def profile_edit_handler(message: Message, state: FSMContext):
    """Редактировать профиль"""
    await state.clear()
    
    text = "✏️ <b>Редактирование профиля</b>\n\n"
    text += "Напишите, что хотите изменить:\n\n"
    text += "• Возраст\n"
    text += "• Пол\n"
    text += "• Рост\n"
    text += "• Вес\n"
    text += "• Цель\n"
    text += "• Активность\n"
    text += "• Город\n\n"
    text += "Например: «хочу изменить вес» или «поменять рост»"
    
    await state.set_state("waiting_for_edit_choice")
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")

@router.message(F.text.lower().in_(["📊 полный анализ тела", "полный анализ тела"]))
async def profile_full_analysis_handler(message: Message, state: FSMContext):
    """Полный анализ тела"""
    user_id = message.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
    
    if not user:
        await message.answer(
            "❌ Профиль не найден. Сначала настройте профиль.",
            reply_markup=get_main_menu()
        )
        return
    
    # Расчёт индексов
    height_m = (user.height or 0) / 100 if user.height else 0
    weight = user.weight or 0
    
    bmi = weight / (height_m ** 2) if height_m > 0 else 0
    
    # BMR (Basal Metabolic Rate)
    if user.gender == 'male':
        bmr = 10 * weight + 6.25 * (user.height or 0) - 5 * (user.age or 30) + 5
    else:
        bmr = 10 * weight + 6.25 * (user.height or 0) - 5 * (user.age or 30) - 161
    
    # Интерпретация BMI
    if bmi < 18.5:
        bmi_status = "⚠️ Недостаточный вес"
    elif bmi < 25:
        bmi_status = "✅ Нормальный вес"
    elif bmi < 30:
        bmi_status = "⚠️ Избыточный вес"
    else:
        bmi_status = "⚠️ Ожирение"
    
    text = f"📊 <b>Полный анализ тела</b>\n\n"
    text += f"⚖️ <b>Индекс массы тела (ИМТ):</b> {bmi:.1f}\n"
    text += f"{bmi_status}\n\n"
    
    text += f"🔥 <b>Базальный метаболизм (BMR):</b> {bmr:.0f} ккал/день\n"
    text += f"Это количество калорий, которое ваше тело сжигает в состоянии покоя.\n\n"
    
    # TDEE (Total Daily Energy Expenditure)
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    multiplier = activity_multipliers.get(user.activity_level, 1.2)
    tdee = bmr * multiplier
    
    text += f"🏃 <b>Суточный расход калорий (TDEE):</b> {tdee:.0f} ккал/день\n"
    text += f"С учётом уровня активности: {user.activity_level or 'не указан'}\n\n"
    
    # Рекомендации по цели
    if user.goal == 'lose_weight':
        target_calories = tdee - 500
        text += f"🎯 <b>Цель: Похудение</b>\n"
        text += f"Рекомендуемая норма: {target_calories:.0f} ккал/день\n"
        text += f"Дефицит: 500 ккал/день = ~0.5 кг в неделю\n\n"
    elif user.goal == 'gain_weight':
        target_calories = tdee + 500
        text += f"🎯 <b>Цель: Набор массы</b>\n"
        text += f"Рекомендуемая норма: {target_calories:.0f} ккал/день\n"
        text += f"Профицит: 500 ккал/день = ~0.5 кг в неделю\n\n"
    else:
        target_calories = tdee
        text += f"🎯 <b>Цель: Поддержание</b>\n"
        text += f"Рекомендуемая норма: {target_calories:.0f} ккал/день\n\n"
    
    # Макронутриенты
    protein = weight * 1.6 if user.goal == 'gain_weight' else weight * 1.2
    fat = weight * 0.9
    carbs = (target_calories - (protein * 4 + fat * 9)) / 4
    
    text += f"📊 <b>Рекомендуемые макронутриенты:</b>\n"
    text += f"• Белки: {protein:.0f} г ({protein * 4:.0f} ккал)\n"
    text += f"• Жиры: {fat:.0f} г ({fat * 9:.0f} ккал)\n"
    text += f"• Углеводы: {carbs:.0f} г ({carbs * 4:.0f} ккал)\n\n"
    
    text += f"💡 <i>Эти расчёты являются приблизительными. Для точных рекомендаций обратитесь к специалисту.</i>"
    
    await message.answer(text, reply_markup=get_profile_menu(), parse_mode="HTML")
