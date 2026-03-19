"""
handlers/profile.py
Обработчики профиля пользователя
"""
import logging
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router, types
from sqlalchemy import select

from database.db import get_session
from database.models import User
from keyboards.reply_v2 import get_main_keyboard_v2, get_profile_keyboard, get_cancel_keyboard, get_confirm_keyboard, get_back_keyboard
from keyboards.reply import get_gender_keyboard
from keyboards.timezone_keyboard import get_timezone_keyboard, get_timezone_confirm_keyboard
from utils.states import ProfileStates
from utils.timezone_utils import parse_timezone_input, get_timezone_display_name
from utils.city_timezone import get_timezone_from_city

logger = logging.getLogger(__name__)
router = Router()

class ProfileStates(StatesGroup):
    """Состояния для настройки профиля"""
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_activity_level = State()
    waiting_for_goal = State()
    waiting_for_city = State()
    waiting_for_timezone = State()

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    """Начало настройки профиля"""
    await state.clear()
    
    user_name = message.from_user.first_name or "Пользователь"
    
    text = f"""👤 <b>Настройка профиля</b>

Привет, {user_name}! Давайте настроим ваш персональный профиль.

🎯 <b>Зачем это нужно:</b>
• Точный расчет суточных норм калорий и БЖУ
• Персональные рекомендации по питанию
• Корректный отслеживание прогресса
• Адаптированные планы тренировок

📋 <b>Что мы узнаем:</b>
• Возраст, пол, рост, вес
• Уровень физической активности
• Ваши цели (похудение/набор/поддержание)
• Часовой пояс для корректного времени

⏱️ <b>Это займет около 2 минут</b>

🚀 <b>Начнем?</b>"""
    
    await message.answer(
        text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "✅ Начать настройку")
async def start_profile_setup(message: Message, state: FSMContext):
    """Начало процесса настройки"""
    await state.set_state(ProfileStates.waiting_for_age)
    
    text = """👤 <b>Шаг 1: Возраст</b>

Введите ваш возраст (полных лет):

💡 <b>Пример:</b> 25

📝 <b>Важно:</b> Возраст нужен для точного расчета метаболизма"""
    
    await message.answer(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True
        ),
        parse_mode="HTML"
    )

@router.message(ProfileStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Обработка возраста"""
    try:
        age = int(message.text)
        
        if age < 10 or age > 120:
            await message.answer(
                "❌ Возраст должен быть от 10 до 120 лет. Попробуйте еще раз:"
            )
            return
        
        await state.update_data(age=age)
        await state.set_state(ProfileStates.waiting_for_gender)
        
        text = """👤 <b>Шаг 2: Пол</b>

Выберите ваш пол:

🔬 <b>Зачем это нужно:</b>
• Разные формулы расчета БЖУ
• Разные нормы калорийности"""
        
        await message.answer(
            text,
            reply_markup=get_gender_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введите число (например: 25):"
        )

@router.message(ProfileStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    """Обработка пола"""
    gender = message.text.lower()
    
    if "муж" in gender or "male" in gender:
        gender = "male"
    elif "жен" in gender or "female" in gender:
        gender = "female"
    else:
        await message.answer(
            "❌ Пожалуйста, выберите пол из предложенных вариантов:"
        )
        return
    
    await state.update_data(gender=gender)
    await state.set_state(ProfileStates.waiting_for_height)
    
    text = """👤 <b>Шаг 3: Рост</b>

Введите ваш рост в сантиметрах:

💡 <b>Пример:</b> 175

📏 <b>Совет:</b> Рост измеряйте без обуви"""
    
    await message.answer(
        text,
        parse_mode="HTML"
    )

@router.message(ProfileStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    """Обработка роста"""
    try:
        height = int(message.text)
        
        if height < 100 or height > 250:
            await message.answer(
                "❌ Рост должен быть от 100 до 250 см. Попробуйте еще раз:"
            )
            return
        
        await state.update_data(height=height)
        await state.set_state(ProfileStates.waiting_for_weight)
        
        text = """👤 <b>Шаг 4: Вес</b>

Введите ваш текущий вес в килограммах:

💡 <b>Пример:</b> 70.5

⚖️ <b>Совет:</b> Взвешивайтесь утром натощак для точности"""
        
        await message.answer(
            text,
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введите число (например: 70.5):"
        )

@router.message(ProfileStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка веса"""
    try:
        weight = float(message.text.replace(',', '.'))
        
        if weight < 30 or weight > 300:
            await message.answer(
                "❌ Вес должен быть от 30 до 300 кг. Попробуйте еще раз:"
            )
            return
        
        await state.update_data(weight=weight)
        await state.set_state(ProfileStates.waiting_for_activity_level)
        
        text = """👤 <b>Шаг 5: Уровень активности</b>

Выберите ваш уровень физической активности:

🏃‍♂️ <b>Варианты:</b>
• Минимальный - сидячая работа, мало движения
• Низкий - легкая активность 1-3 раза в неделю
• Средний - умеренная активность 3-5 раз в неделю
• Высокий - интенсивная активность 6-7 раз в неделю
• Очень высокий - тяжелая физическая работа"""
        
        await message.answer(
            text,
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введите число (например: 70.5):"
        )

@router.message(ProfileStates.waiting_for_activity_level)
async def process_activity_level(message: Message, state: FSMContext):
    """Обработка уровня активности"""
    activity_text = message.text.lower()
    
    activity_mapping = {
        "минимальный": "sedentary",
        "низкий": "light", 
        "средний": "moderate",
        "высокий": "active",
        "очень высокий": "very_active"
    }
    
    activity_level = None
    for key, value in activity_mapping.items():
        if key in activity_text:
            activity_level = value
            break
    
    if not activity_level:
        await message.answer(
            "❌ Пожалуйста, выберите уровень активности из предложенных вариантов:"
        )
        return
    
    await state.update_data(activity_level=activity_level)
    await state.set_state(ProfileStates.waiting_for_goal)
    
    text = """👤 <b>Шаг 6: Ваша цель</b>

Что вы хотите достичь?

🎯 <b>Цели:</b>
• Похудение - снижение веса
• Набор массы - увеличение мышечной массы
• Поддержание - сохранение текущего веса"""
    
    await message.answer(
        text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )

@router.message(ProfileStates.waiting_for_goal)
async def process_goal(message: Message, state: FSMContext):
    """Обработка цели"""
    goal_text = message.text.lower()
    
    if "похуд" in goal_text:
        goal = "lose_weight"
    elif "набор" in goal_text:
        goal = "gain_weight"
    elif "поддерж" in goal_text:
        goal = "maintain"
    else:
        await message.answer(
            "❌ Пожалуйста, выберите цель из предложенных вариантов:"
        )
        return
    
    await state.update_data(goal=goal)
    await state.set_state(ProfileStates.waiting_for_city)
    
    text = """👤 <b>Шаг 7: Город</b>

Введите ваш город (необязательно):

🌍 <b>Зачем это нужно:</b>
• Учет климатических особенностей
• Локальные рекомендации"""
    
    await message.answer(
        text,
        parse_mode="HTML"
    )

@router.message(ProfileStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    """Обработка города с автоматическим определением часового пояса"""
    city = message.text.strip()
    
    # Автоматически определяем часовой пояс из города
    if city:
        timezone = get_timezone_from_city(city)
        if timezone:
            await state.update_data(city=city, timezone=timezone)
            logger.info(f"🌍 Автоматически определен часовой пояс для города '{city}': {timezone}")
            
            # Показываем подтверждение и завершаем настройку
            timezone_display = get_timezone_display_name(timezone)
            text = f"""👤 <b>Город и часовой пояс определены</b>

🌍 Город: {city}
🕐 Часовой пояс: {timezone_display}

✅ Часовой пояс определен автоматически на основе вашего города

🔔 <b>Напоминания:</b>
• Напоминания будут приходить с учетом вашего часового пояса
• Время записей будет корректным

🚀 <b>Завершить настройку?</b>"""
            
            await message.answer(
                text,
                reply_markup=get_confirm_keyboard(),
                parse_mode="HTML"
            )
            return
        else:
            # Если город не найден, предлагаем выбор часового пояса
            await state.update_data(city=city)
            await state.set_state(ProfileStates.waiting_for_timezone)
            
            text = f"""👤 <b>Шаг 8: Часовой пояс</b>

⚠️ Не удалось определить часовой пояс для города "{city}"

Выберите ваш часовой пояс вручную:

🕐 <b>Важно:</b>
• Для корректного времени записей
• Для своевременных напоминаний"""
            
            await message.answer(
                text,
                reply_markup=get_timezone_keyboard(),
                parse_mode="HTML"
            )
            return
    else:
        # Если город не указан, переходим к выбору часового пояса
        await state.update_data(city=None)
        await state.set_state(ProfileStates.waiting_for_timezone)
        
        text = """👤 <b>Шаг 8: Часовой пояс</b>

Город не указан. Выберите ваш часовой пояс:

🕐 <b>Важно:</b>
• Для корректного времени записей
• Для своевременных напоминаний"""
        
        await message.answer(
            text,
            reply_markup=get_timezone_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("timezone_"))
async def process_timezone(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора часового пояса"""
    timezone_offset = callback.data.split("_")[1]
    
    await state.update_data(timezone=timezone_offset)
    await state.set_state(ProfileStates.waiting_for_timezone)
    
    timezone_name = get_timezone_display_name(timezone_offset)
    
    text = f"""👤 <b>Подтверждение часового пояса</b>

Выбран часовой пояс: {timezone_name}

✅ <b>Все готово для сохранения профиля!</b>

📋 <b>Ваши данные:</b>"""
    
    # Получаем все данные
    data = await state.get_data()
    
    profile_summary = f"""
• Возраст: {data['age']} лет
• Пол: {'Мужской' if data['gender'] == 'male' else 'Женский'}
• Рост: {data['height']} см
• Вес: {data['weight']} кг
• Активность: {data['activity_level']}
• Цель: {data['goal']}
• Часовой пояс: {timezone_name}"""
    
    if data.get('city'):
        profile_summary += f"\n• Город: {data['city']}"
    
    keyboard = [
        [InlineKeyboardButton(text="✅ Сохранить профиль", callback_data="save_profile")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_profile")]
    ]
    
    await callback.message.edit_text(
        text + profile_summary,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "save_profile")
async def save_profile(callback: CallbackQuery, state: FSMContext):
    """Сохранение профиля"""
    try:
        data = await state.get_data()
        user_id = callback.from_user.id
        
        # Расчет суточных норм
        daily_calories = calculate_daily_calories(data)
        daily_protein = calculate_daily_protein(data, daily_calories)
        daily_fat = calculate_daily_fat(daily_calories)
        daily_carbs = calculate_daily_carbs(daily_calories, daily_protein, daily_fat)
        
        async for session in get_session():
            # Проверяем, существует ли пользователь
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Обновляем существующего пользователя
                user.age = data['age']
                user.gender = data['gender']
                user.height = data['height']
                user.weight = data['weight']
                user.activity_level = data['activity_level']
                user.goal = data['goal']
                user.city = data.get('city')
                user.timezone = data['timezone']
                user.daily_calorie_goal = daily_calories
                user.daily_protein_goal = daily_protein
                user.daily_fat_goal = daily_fat
                user.daily_carbs_goal = daily_carbs
                user.daily_water_goal = calculate_daily_water(data['weight'])
                user.daily_steps_goal = 10000
                user.daily_activity_goal = calculate_daily_activity(data['activity_level'])
                user.updated_at = datetime.now()
            else:
                # Создаем нового пользователя
                user = User(
                    telegram_id=user_id,
                    username=callback.from_user.username,
                    first_name=callback.from_user.first_name,
                    age=data['age'],
                    gender=data['gender'],
                    height=data['height'],
                    weight=data['weight'],
                    activity_level=data['activity_level'],
                    goal=data['goal'],
                    city=data.get('city'),
                    timezone=data['timezone'],
                    daily_calorie_goal=daily_calories,
                    daily_protein_goal=daily_protein,
                    daily_fat_goal=daily_fat,
                    daily_carbs_goal=daily_carbs,
                    daily_water_goal=calculate_daily_water(data['weight']),
                    daily_steps_goal=10000,
                    daily_activity_goal=calculate_daily_activity(data['activity_level'])
                )
                session.add(user)
            
            await session.commit()
        
        # Формируем сообщение об успехе
        success_text = f"""🎉 <b>Профиль успешно сохранен!</b>

📊 <b>Ваши суточные нормы:</b>
• Калории: {daily_calories} ккал
• Белки: {daily_protein} г
• Жиры: {daily_fat} г
• Углеводы: {daily_carbs} г
• Вода: {calculate_daily_water(data['weight'])} мл
• Шаги: 10,000
• Активность: {calculate_daily_activity(data['activity_level'])} мин

🚀 <b>Что дальше?</b>
• Начните记录ать питание: /food
• Выпейте воды: /water
• Запишите активность: /fitness

💡 <b>Совет:</b> Регулярное ведение дневника поможет достичь целей быстрее!"""
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )
        
        await state.clear()
        await callback.answer("Профиль сохранен!")
        
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        await callback.answer("❌ Ошибка сохранения профиля", show_alert=True)

@router.callback_query(F.data == "cancel_profile")
async def cancel_profile(callback: CallbackQuery, state: FSMContext):
    """Отмена настройки профиля"""
    await state.clear()
    
    text = """❌ <b>Настройка профиля отменена</b>

🏠 Возвращаю в главное меню..."""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    """Показать профиль"""
    await state.clear()
    
    async for session in get_session():
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            text = """👤 <b>Профиль не найден</b>

Сначала настройте профиль:

/set_profile - Настроить профиль"""
            
            await message.answer(
                text,
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            return
        
        # Формируем информацию о профиле
        profile_text = f"""👤 <b>Ваш профиль</b>

📋 <b>Основные данные:</b>
• Имя: {user.first_name or 'Не указано'}
• Возраст: {user.age} лет
• Пол: {'Мужской' if user.gender == 'male' else 'Женский'}
• Рост: {user.height} см
• Вес: {user.weight} кг
• Активность: {user.activity_level}
• Цель: {user.goal}"""
        
        if user.city:
            profile_text += f"\n• Город: {user.city}"
        
        profile_text += f"""

📊 <b>Суточные нормы:</b>
• Калории: {user.daily_calorie_goal} ккал
• Белки: {user.daily_protein_goal} г
• Жиры: {user.daily_fat_goal} г
• Углеводы: {user.daily_carbs_goal} г
• Вода: {user.daily_water_goal} мл
• Шаги: {user.daily_steps_goal}
• Активность: {user.daily_activity_goal} мин

⏰ <b>Часовой пояс:</b> {get_timezone_display_name(user.timezone) if user.timezone else 'UTC'}

💧 <b>Жидкости:</b> {user.daily_water_goal} мл"""
        
        await message.answer(
            profile_text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )

@router.message(F.text.contains("✅ Завершить настройку"))
async def complete_profile_setup(message: Message, state: FSMContext):
    """Завершение настройки профиля"""
    data = await state.get_data()
    
    async for session in get_session():
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем данные пользователя
            user.age = data.get('age')
            user.gender = data.get('gender')
            user.height = data.get('height')
            user.weight = data.get('weight')
            user.activity_level = data.get('activity_level')
            user.goal = data.get('goal')
            user.city = data.get('city')
            user.timezone = data.get('timezone', 'UTC')
            
            # Рассчитываем цели
            user.daily_calorie_goal = calculate_daily_calories(data)
            macros = calculate_macros(data)
            user.daily_protein_goal = macros['protein']
            user.daily_fat_goal = macros['fat']
            user.daily_carbs_goal = macros['carbs']
            user.daily_water_goal = calculate_daily_water(data)
            user.daily_steps_goal = calculate_daily_steps(data)
            user.daily_activity_goal = calculate_daily_activity(data)
            
            await session.commit()
            
            text = f"""✅ <b>Профиль успешно настроен!</b>

👤 <b>Ваши данные:</b>
🎂 Возраст: {data.get('age')} лет
👫 Пол: {'Мужской' if data.get('gender') == 'male' else 'Женский'}
📏 Рост: {data.get('height')} см
⚖️ Вес: {data.get('weight')} кг
🏃 Активность: {data.get('activity_level')}
🎯 Цель: {data.get('goal')}
🌍 Город: {data.get('city') or 'Не указан'}
🕐 Часовой пояс: {get_timezone_display_name(data.get('timezone', 'UTC'))}

🔥 <b>Ваши цели:</b>
Калории: {user.daily_calorie_goal} ккал
Белки: {user.daily_protein_goal}г
Жиры: {user.daily_fat_goal}г
Углеводы: {user.daily_carbs_goal}г
Вода: {user.daily_water_goal} мл
Шаги: {user.daily_steps_goal}
Активность: {user.daily_activity_goal} мин

🚀 <b>Готово к работе!</b>"""
            
            await message.answer(
                text,
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Ошибка при сохранении профиля. Попробуйте еще раз.",
                reply_markup=get_main_keyboard_v2()
            )
    
    await state.clear()

@router.message(F.text.contains("🔄 Изменить часовой пояс"))
async def change_timezone(message: Message, state: FSMContext):
    """Изменение часового пояса вручную"""
    await state.set_state(ProfileStates.waiting_for_timezone)
    
    text = """🕐 <b>Выберите часовой пояс</b>

Выберите ваш часовой пояс из списка:"""
    
    await message.answer(
        text,
        reply_markup=get_timezone_keyboard(),
        parse_mode="HTML"
    )

# Вспомогательные функции для расчета

def calculate_daily_calories(data: dict) -> int:
    """Расчет суточной калорийности по формуле Миффлина-Джеора"""
    age = data['age']
    gender = data['gender']
    height = data['height']
    weight = data['weight']
    activity_level = data['activity_level']
    
    # Базовый метаболизм
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Коэффициент активности
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    daily_calories = int(bmr * multiplier)
    
    # Корректировка в зависимости от цели
    goal = data['goal']
    if goal == 'lose_weight':
        daily_calories = int(daily_calories * 0.85)  # -15%
    elif goal == 'gain_weight':
        daily_calories = int(daily_calories * 1.15)  # +15%
    
    return daily_calories

def calculate_daily_protein(data: dict, calories: int) -> int:
    """Расчет суточной нормы белка"""
    weight = data['weight']
    goal = data['goal']
    
    if goal == 'gain_weight':
        protein_per_kg = 2.0  # 2г на кг для набора массы
    elif goal == 'lose_weight':
        protein_per_kg = 1.8  # 1.8г на кг для похудения
    else:
        protein_per_kg = 1.2  # 1.2г на кг для поддержания
    
    return int(weight * protein_per_kg)

def calculate_daily_fat(calories: int) -> int:
    """Расчет суточной нормы жиров"""
    return int((calories * 0.25) / 9)  # 25% калорий из жиров

def calculate_daily_carbs(calories: int, protein: int, fat: int) -> int:
    """Расчет суточной нормы углеводов"""
    protein_calories = protein * 4
    fat_calories = fat * 9
    remaining_calories = calories - protein_calories - fat_calories
    
    return int(remaining_calories / 4)  # 4 калории на г углеводов

def calculate_daily_water(weight: float) -> int:
    """Расчет суточной нормы воды"""
    return int(weight * 35)  # 35мл на кг веса

def calculate_daily_activity(activity_level: str) -> int:
    """Расчет суточной нормы активности"""
    activity_goals = {
        'sedentary': 30,
        'light': 45,
        'moderate': 60,
        'active': 75,
        'very_active': 90
    }
    
    return activity_goals.get(activity_level, 60)

def calculate_daily_steps(data: dict) -> int:
    """Расчет суточной нормы шагов на основе профиля пользователя"""
    age = data.get('age', 30)
    gender = data.get('gender', 'male')
    activity_level = data.get('activity_level', 'moderate')
    goal = data.get('goal', 'maintain')
    
    # Базовые цели по уровню активности
    base_steps = {
        'sedentary': 6000,      # Сидячий образ жизни
        'light': 8000,          # Легкая активность
        'moderate': 10000,      # Умеренная активность
        'active': 12000,        # Активный образ жизни
        'very_active': 15000    # Очень активный
    }
    
    base_goal = base_steps.get(activity_level, 10000)
    
    # Корректировка по возрасту
    if age < 30:
        age_factor = 1.1  # Молодые могут больше
    elif age > 65:
        age_factor = 0.8  # Пожилым нужно меньше
    else:
        age_factor = 1.0
    
    # Корректировка по полу
    if gender == 'male':
        gender_factor = 1.1  # Мужчины обычно больше ходят
    else:
        gender_factor = 0.95  # Женщины обычно меньше
    
    # Корректировка по цели
    if goal == 'lose_weight':
        goal_factor = 1.2  # Для похудения нужно больше шагов
    elif goal == 'gain_weight':
        goal_factor = 0.9  # Для набора массы можно меньше
    else:
        goal_factor = 1.0  # Поддержание веса
    
    # Итоговый расчет
    daily_steps = int(base_goal * age_factor * gender_factor * goal_factor)
    
    # Ограничиваем разумные пределы
    daily_steps = max(4000, min(daily_steps, 20000))
    
    logger.info(f"📊 Рассчитана цель по шагам: {daily_steps} (база: {base_goal}, возраст: {age_factor}, пол: {gender_factor}, цель: {goal_factor})")
    
    return daily_steps

def calculate_macros(data: dict) -> dict:
    """Расчет макронутриентов"""
    calories = calculate_daily_calories(data)
    
    protein = calculate_daily_protein(data, calories)
    fat = calculate_daily_fat(calories)
    carbs = calculate_daily_carbs(calories, protein, fat)
    
    return {
        'protein': protein,
        'fat': fat,
        'carbs': carbs
    }

@router.message(F.text.lower().regexp(r'(редактировать профиль|записать прием пищи)'))
async def edit_profile_or_food_button(message: Message, state: FSMContext):
    """Обработка кнопки редактирования профиля или добавления пищи"""
    if "редактировать" in message.text.lower():
        from handlers.common import cmd_set_profile
        await cmd_set_profile(message, state)
    else:
        logger.info(f"🔍 REPLY HANDLER: Food button pressed by user {message.from_user.id}")
        await state.clear()
        await message.answer(
            "🍽️ <b>Записать приём пищи</b>\n\n"
            "Отправьте фото блюда или напишите что вы съели.\n\n"
            "Примеры:\n"
            "• 200г гречки с курицей\n"
            "• салат цезарь\n"
            "• яблоко 2шт",
            parse_mode="HTML"
        )

@router.message(F.text.lower().regexp(r'(полный анализ|прогресс)'))
async def full_analysis_or_progress_button(message: Message, state: FSMContext):
    """Обработка кнопки полного анализа или прогресса"""
    if "полный анализ" in message.text.lower():
        await message.answer("📊 <b>Полный анализ</b>\n\nФункция полного анализа находится в разработке...", reply_markup=get_main_keyboard_v2(), parse_mode="HTML")
    else:
        logger.info(f"🔍 REPLY HANDLER: Progress button pressed by user {message.from_user.id}")
        await state.clear()
        await cmd_progress(message, state)

@router.message(F.text.lower().regexp(r'(записать вес|записывать вес)'))
async def record_weight_button(message: Message, state: FSMContext):
    """Обработка кнопки записи веса"""
    logger.info(f"🔍 REPLY HANDLER: Weight button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_weight(message, state)

@router.message(F.text.lower().regexp(r'(главное меню|вернуться в главное меню)'))
async def main_menu_from_profile(message: Message, state: FSMContext):
    """Возврат в главное меню из профиля"""
    logger.info(f"🔍 REPLY HANDLER: Main menu button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.common import cmd_start
    await cmd_start(message)
