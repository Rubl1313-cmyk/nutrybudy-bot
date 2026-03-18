"""
utils/helpers.py
Вспомогательные функции для NutriBuddy Bot
"""
import logging
from datetime import datetime, date
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)

# Унифицированные функции статистики - импортируем из daily_stats
from utils.daily_stats import (
    get_daily_stats, get_daily_water, get_daily_drink_calories, 
    get_daily_activity_calories, get_period_stats
)

async def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает профиль пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        dict: Данные профиля или None
    """
    try:
        from database.db import get_session
        from database.models import User
        
        with get_session() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                return None
            
            return {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'gender': user.gender,
                'weight': user.weight,
                'height': user.height,
                'goal': user.goal,
                'activity_level': user.activity_level,
                'daily_calorie_goal': user.daily_calorie_goal,
                'daily_protein_goal': user.daily_protein_goal,
                'daily_fat_goal': user.daily_fat_goal,
                'daily_carbs_goal': user.daily_carbs_goal,
                'daily_water_goal': user.daily_water_goal,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }
    except Exception as e:
        logger.error(f"Error getting user profile for {user_id}: {e}")
        return None

def format_nutrition_value(value: float, unit: str = "г") -> str:
    """
    Форматирует значение питательного вещества
    
    Args:
        value: Числовое значение
        unit: Единица измерения
        
    Returns:
        str: Отформатированная строка
    """
    if value == 0:
        return f"0{unit}"
    elif value < 0.1:
        return f"{value:.1f}{unit}"
    elif value < 10:
        return f"{value:.1f}{unit}"
    else:
        return f"{value:.0f}{unit}"

def calculate_bmi(weight: float, height: float) -> float:
    """
    Рассчитывает ИМТ
    
    Args:
        weight: Вес в кг
        height: Рост в см
        
    Returns:
        float: Значение ИМТ
    """
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)

def get_bmi_category(bmi: float) -> str:
    """
    Возвращает категорию ИМТ
    
    Args:
        bmi: Значение ИМТ
        
    Returns:
        str: Категория ИМТ
    """
    if bmi < 18.5:
        return "Недостаточный вес"
    elif bmi < 25:
        return "Нормальный вес"
    elif bmi < 30:
        return "Избыточный вес"
    else:
        return "Ожирение"

# Старые функции для обратной совместимости
def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def format_date(dt: date) -> str:
    return dt.strftime("%d.%m.%Y")

def get_meal_type_emoji(meal_type: str) -> str:
    emojis = {
        'breakfast': '[BREAKFAST]',
        'lunch': '[LUNCH]',
        'dinner': '[DINNER]',
        'snack': '[SNACK]'
    }
    return emojis.get(meal_type, '[MEAL]')

def get_activity_type_emoji(activity_type: str) -> str:
    emojis = {
        'walking': '[WALKING]',
        'running': '[RUNNING]',
        'cycling': '[CYCLING]',
        'gym': '[GYM]',
        'yoga': '[YOGA]',
        'swimming': '[SWIMMING]',
        'hiit': '[HIIT]',
        'stretching': '[STRETCHING]',
        'dancing': '[DANCING]',
        'sports': '[SPORTS]'
    }
    return emojis.get(activity_type, '[ACTIVITY]')

def normalize_exit_command(text: str) -> str:
    """
    Нормализует текст для проверки на выход: убирает пунктуацию, лишние пробелы.
    Используется для команды "выход", "выйти" и т.п.
    """
    # Убираем все знаки препинания и лишние пробелы
    text = re.sub(r'[^\w\s]', '', text)
    text = text.strip().lower()
    return text

def is_exit_command(text: str) -> bool:
    """
    Проверяет, является ли текст командой выхода
    """
    normalized = normalize_exit_command(text)
    exit_commands = ['выход', 'выйти', 'отмена', 'cancel', 'exit', 'quit', 'стоп']
    return normalized in exit_commands

def calculate_calories_from_macros(protein: float, fat: float, carbs: float) -> float:
    """
    Рассчитывает калории из БЖУ
    
    Args:
        protein: Белки в граммах
        fat: Жиры в граммах
        carbs: Углеводы в граммах
        
    Returns:
        float: Калории
    """
    return protein * 4 + fat * 9 + carbs * 4

def calculate_macros_from_calories(calories: float, protein_ratio: float = 0.3, 
                                 fat_ratio: float = 0.3, carbs_ratio: float = 0.4) -> Dict[str, float]:
    """
    Рассчитывает БЖУ из калорий
    
    Args:
        calories: Калории
        protein_ratio: Доля белков (0-1)
        fat_ratio: Доля жиров (0-1)
        carbs_ratio: Доля углеводов (0-1)
        
    Returns:
        dict: БЖУ в граммах
    """
    # Нормализуем соотношения
    total = protein_ratio + fat_ratio + carbs_ratio
    if total != 1:
        protein_ratio /= total
        fat_ratio /= total
        carbs_ratio /= total
    
    return {
        'protein': calories * protein_ratio / 4,
        'fat': calories * fat_ratio / 9,
        'carbs': calories * carbs_ratio / 4
    }

def format_weight(weight: float) -> str:
    """
    Форматирует вес
    
    Args:
        weight: Вес в кг
        
    Returns:
        str: Отформатированный вес
    """
    return f"{weight:.1f} кг"

def format_height(height: float) -> str:
    """
    Форматирует рост
    
    Args:
        height: Рост в см
        
    Returns:
        str: Отформатированный рост
    """
    return f"{height:.0f} см"

def format_age(age: int) -> str:
    """
    Форматирует возраст
    
    Args:
        age: Возраст в годах
        
    Returns:
        str: Отформатированный возраст
    """
    return f"{age} лет"

def get_goal_emoji(goal: str) -> str:
    """
    Возвращает эмодзи для цели
    
    Args:
        goal: Цель
        
    Returns:
        str: Эмодзи
    """
    goal_emojis = {
        'похудение': '[WEIGHT_LOSS]',
        'набор': '[WEIGHT_GAIN]',
        'поддержание': '[MAINTENANCE]',
        'здоровье': '[HEALTH]',
        'спорт': '[SPORTS]'
    }
    return goal_emojis.get(goal.lower(), '[GOAL]')

def get_activity_emoji(activity_level: str) -> str:
    """
    Возвращает эмодзи для уровня активности
    
    Args:
        activity_level: Уровень активности
        
    Returns:
        str: Эмодзи
    """
    activity_emojis = {
        'низкая': '[LOW]',
        'легкая': '[LIGHT]',
        'умеренная': '[MODERATE]',
        'высокая': '[HIGH]',
        'очень высокая': '[VERY_HIGH]'
    }
    return activity_emojis.get(activity_level.lower(), '[ACTIVITY]')

def validate_date(date_string: str) -> Optional[date]:
    """
    Валидирует и преобразует строку в дату
    
    Args:
        date_string: Строка с датой
        
    Returns:
        date: Объект даты или None
    """
    try:
        # Пробуем разные форматы
        formats = ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt).date()
            except ValueError:
                continue
        return None
    except Exception:
        return None

def validate_time(time_string: str) -> Optional[datetime.time]:
    """
    Валидирует и преобразует строку во время
    
    Args:
        time_string: Строка со временем
        
    Returns:
        datetime.time: Объект времени или None
    """
    try:
        # Пробуем разные форматы
        formats = ['%H:%M', '%H:%M:%S', '%H.%M', '%H.%M.%S']
        
        for fmt in formats:
            try:
                return datetime.strptime(time_string, fmt).time()
            except ValueError:
                continue
        return None
    except Exception:
        return None

def get_period_start_date(period: str) -> date:
    """
    Возвращает начальную дату для периода
    
    Args:
        period: Период (day, week, month, year)
        
    Returns:
        date: Начальная дата
    """
    today = date.today()
    
    if period == 'day':
        return today
    elif period == 'week':
        # Начало недели (понедельник)
        days_since_monday = today.weekday()
        return today - timedelta(days=days_since_monday)
    elif period == 'month':
        # Начало месяца
        return today.replace(day=1)
    elif period == 'year':
        # Начало года
        return today.replace(month=1, day=1)
    else:
        return today

def get_period_end_date(period: str) -> date:
    """
    Возвращает конечную дату для периода
    
    Args:
        period: Период (day, week, month, year)
        
    Returns:
        date: Конечная дата
    """
    today = date.today()
    
    if period == 'day':
        return today
    elif period == 'week':
        # Конец недели (воскресенье)
        days_until_sunday = 6 - today.weekday()
        return today + timedelta(days=days_until_sunday)
    elif period == 'month':
        # Конец месяца
        if today.month == 12:
            return today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            return today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    elif period == 'year':
        # Конец года
        return today.replace(month=12, day=31)
    else:
        return today

def format_period_name(period: str) -> str:
    """
    Форматирует название периода
    
    Args:
        period: Период
        
    Returns:
        str: Отформатированное название
    """
    period_names = {
        'day': 'сегодня',
        'week': 'за неделю',
        'month': 'за месяц',
        'year': 'за год'
    }
    return period_names.get(period, 'за период')

def calculate_water_intake(weight: float, activity_level: str) -> float:
    """
    Рассчитывает норму воды
    
    Args:
        weight: Вес в кг
        activity_level: Уровень активности
        
    Returns:
        float: Норма воды в мл
    """
    # Базовая норма: 30 мл на кг веса
    base_water = weight * 30
    
    # Корректировка в зависимости от активности
    activity_multipliers = {
        'низкая': 1.0,
        'легкая': 1.1,
        'умеренная': 1.2,
        'высокая': 1.3,
        'очень высокая': 1.4
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    return base_water * multiplier

def calculate_daily_calories(weight: float, height: float, age: int, 
                           gender: str, activity_level: str, goal: str) -> float:
    """
    Рассчитывает дневную норму калорий
    
    Args:
        weight: Вес в кг
        height: Рост в см
        age: Возраст
        gender: Пол (male/female)
        activity_level: Уровень активности
        goal: Цель (похудение/набор/поддержание)
        
    Returns:
        float: Норма калорий
    """
    # Базовый метаболизм по формуле Миффлина-Сан Жеора
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Коэффициент активности
    activity_multipliers = {
        'низкая': 1.2,
        'легкая': 1.375,
        'умеренная': 1.55,
        'высокая': 1.725,
        'очень высокая': 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    tdee = bmr * multiplier
    
    # Корректировка под цель
    goal_adjustments = {
        'похудение': -500,  # Дефицит 500 ккал
        'поддержание': 0,
        'набор': 500       # Профицит 500 ккал
    }
    
    adjustment = goal_adjustments.get(goal.lower(), 0)
    return max(tdee + adjustment, 1200)  # Минимум 1200 ккал

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Обрезает текст до указанной длины
    
    Args:
        text: Текст
        max_length: Максимальная длина
        
    Returns:
        str: Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def clean_text(text: str) -> str:
    """
    Очищает текст от лишних символов
    
    Args:
        text: Текст
        
    Returns:
        str: Очищенный текст
    """
    # Убираем множественные пробелы
    text = re.sub(r'\s+', ' ', text)
    # Убираем пробелы по краям
    text = text.strip()
    return text

def is_valid_weight(weight: float) -> bool:
    """Проверяет корректность веса"""
    return 30 <= weight <= 300

def is_valid_height(height: float) -> bool:
    """Проверяет корректность роста"""
    return 100 <= height <= 250

def is_valid_age(age: int) -> bool:
    """Проверяет корректность возраста"""
    return 10 <= age <= 120

def is_valid_gender(gender: str) -> bool:
    """Проверяет корректность пола"""
    return gender.lower() in ['male', 'female', 'мужской', 'женский']

def is_valid_goal(goal: str) -> bool:
    """Проверяет корректность цели"""
    valid_goals = ['похудение', 'набор', 'поддержание', 'здоровье', 'спорт']
    return goal.lower() in valid_goals

def is_valid_activity_level(activity_level: str) -> bool:
    """Проверяет корректность уровня активности"""
    valid_levels = ['низкая', 'легкая', 'умеренная', 'высокая', 'очень высокая']
    return activity_level.lower() in valid_levels
