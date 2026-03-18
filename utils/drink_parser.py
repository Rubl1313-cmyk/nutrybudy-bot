"""
Парсер напитков - определение объёма и калорийности
"""
import re
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# База калорийности напитков (на 100 мл)
DRINK_CALORIES_DB = {
    'сок': 45,           # Средняя калорийность сока
    'апельсиновый сок': 45,
    'яблочный сок': 42,
    'томатный сок': 18,
    'ананасовый сок': 50,
    'виноградный сок': 60,
    'компот': 25,        # Компот с сахаром
    'чай': 2,            # Чай без сахара
    'чай с сахаром': 30,
    'кофе': 2,           # Кофе без сахара
    'кофе с сахаром': 15,
    'кофе с молоком': 25,
    'молоко': 42,        # Молоко 2.5%
    'кефир': 35,
    'ряженка': 40,
    'йогурт': 60,
    'газировка': 40,     # Кола, Пепси
    'кола': 40,
    'пепси': 40,
    'лимонад': 35,
    'минералка': 0,      # Минеральная вода
    'газировка': 40,
    'смузи': 80,
    'коктейль': 120,
    'какао': 75,
    'горячий шоколад': 75,
}

# Единицы измерения и их эквиваленты в мл
VOLUME_UNITS = {
    'мл': 1,
    'л': 1000,
    'стакан': 250,
    'чашка': 200,
    'бутылка': 500,
    'банка': 330,
    'пакет': 1000,
    'флакон': 50,
    'рюмка': 50,
    'шот': 50,
    'стопка': 50,
}

# Синонимы напитков
DRINK_SYNONYMS = {
    'газированная вода': 'минералка',
    'газировка': 'кола',
    'пепси кола': 'пепси',
    'кока кола': 'кола',
    'апельсиновый': 'сок',
    'яблочный': 'сок',
    'томатный': 'сок',
    'ананасовый': 'сок',
    'виноградный': 'сок',
    'черный чай': 'чай',
    'зеленый чай': 'чай',
    'кофе эспрессо': 'кофе',
    'кофе американо': 'кофе',
    'кофе капучино': 'кофе с молоком',
    'молочный коктейль': 'коктейль',
    'фруктовый смузи': 'смузи',
    'овощной смузи': 'смузи',
    'горячий шоколад': 'какао',
    'шоколадный напиток': 'какао',
}

def parse_drink_input(text: str) -> Tuple[Optional[str], Optional[int], Optional[float]]:
    """
    Парсит ввод напитка
    
    Args:
        text: Текст от пользователя
        
    Returns:
        Tuple[str, int, float]: (напиток, объём в мл, калории)
    """
    try:
        text = text.lower().strip()
        
        # Ищем напиток в тексте
        drink_name = None
        for drink in DRINK_CALORIES_DB.keys():
            if drink in text:
                drink_name = drink
                break
        
        # Проверяем синонимы
        if not drink_name:
            for synonym, canonical in DRINK_SYNONYMS.items():
                if synonym in text:
                    drink_name = canonical
                    break
        
        # Если напиток не найден, пробуем угадать
        if not drink_name:
            drink_name = guess_drink_from_text(text)
        
        if not drink_name:
            return None, None, None
        
        # Ищем объём
        volume = extract_volume(text)
        if not volume:
            # Если объём не указан, используем стандартные значения
            volume = get_default_volume(drink_name)
        
        # Рассчитываем калории
        calories = calculate_calories(drink_name, volume)
        
        logger.info(f"[DRINK] Parsed: {drink_name} {volume}мл {calories}ккал")
        
        return drink_name, volume, calories
        
    except Exception as e:
        logger.error(f"Error parsing drink input '{text}': {e}")
        return None, None, None

def guess_drink_from_text(text: str) -> Optional[str]:
    """
    Угадывает напиток по ключевым словам
    
    Args:
        text: Текст для анализа
        
    Returns:
        str: Название напитка или None
    """
    keywords = {
        'кофе': 'кофе',
        'капучино': 'кофе с молоком',
        'латте': 'кофе с молоком',
        'чай': 'чай',
        'сок': 'сок',
        'молоко': 'молоко',
        'кефир': 'кефир',
        'ряженка': 'ряженка',
        'йогурт': 'йогурт',
        'кола': 'кола',
        'пепси': 'пепси',
        'газировка': 'кола',
        'минералка': 'минералка',
        'вода': 'минералка',
        'смузи': 'смузи',
        'коктейль': 'коктейль',
        'какао': 'какао',
        'шоколад': 'какао',
        'компот': 'компот',
        'лимонад': 'лимонад',
    }
    
    text_lower = text.lower()
    
    for keyword, drink in keywords.items():
        if keyword in text_lower:
            return drink
    
    return None

def extract_volume(text: str) -> Optional[int]:
    """
    Извлекает объём из текста
    
    Args:
        text: Текст для анализа
        
    Returns:
        int: Объём в мл или None
    """
    # Ищем паттерны: "200 мл", "0.5 л", "стакан", "бутылка" и т.д.
    patterns = [
        r'(\d+(?:\.\d+)?)\s*мл',
        r'(\d+(?:\.\d+)?)\s*л',
        r'(\d+)\s*стакан',
        r'(\d+)\s*чашка',
        r'(\d+)\s*бутылка',
        r'(\d+)\s*банка',
        r'(\d+)\s*пакет',
        r'(\d+)\s*флакон',
        r'(\d+)\s*рюмка',
        r'(\d+)\s*шот',
        r'(\d+)\s*стопка',
        r'стакан',
        r'чашка',
        r'бутылка',
        r'банка',
        r'рюмка',
        r'шот',
        r'стопка',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            if match.groups():
                # Если есть число
                value = float(match.group(1))
                unit = pattern.split(r'(\d+(?:\.\d+)?)\s*')[1].strip()
                
                if unit in ['мл']:
                    return int(value)
                elif unit in ['л']:
                    return int(value * 1000)
                elif unit in VOLUME_UNITS:
                    return int(value * VOLUME_UNITS[unit])
            else:
                # Если нет числа (например, просто "стакан")
                unit = pattern.strip()
                if unit in VOLUME_UNITS:
                    return VOLUME_UNITS[unit]
    
    return None

def get_default_volume(drink_name: str) -> int:
    """
    Возвращает стандартный объём для напитка
    
    Args:
        drink_name: Название напитка
        
    Returns:
        int: Объём в мл
    """
    default_volumes = {
        'кофе': 200,
        'кофе с молоком': 250,
        'чай': 200,
        'чай с сахаром': 200,
        'сок': 250,
        'молоко': 250,
        'кефир': 250,
        'ряженка': 250,
        'йогурт': 200,
        'кола': 330,
        'пепси': 330,
        'минералка': 250,
        'газировка': 330,
        'смузи': 300,
        'коктейль': 200,
        'какао': 200,
        'компот': 250,
        'лимонад': 250,
    }
    
    return default_volumes.get(drink_name, 200)

def calculate_calories(drink_name: str, volume_ml: int) -> float:
    """
    Рассчитывает калории напитка
    
    Args:
        drink_name: Название напитка
        volume_ml: Объём в мл
        
    Returns:
        float: Калории
    """
    calories_per_100ml = DRINK_CALORIES_DB.get(drink_name, 0)
    return (calories_per_100ml * volume_ml) / 100

def format_drink_info(drink_name: str, volume_ml: int, calories: float) -> str:
    """
    Форматирует информацию о напитке
    
    Args:
        drink_name: Название напитка
        volume_ml: Объём в мл
        calories: Калории
        
    Returns:
        str: Отформатированная строка
    """
    return f"{drink_name.title()} {volume_ml}мл - {calories:.0f} ккал"

def get_drink_suggestions() -> list:
    """
    Возвращает список популярных напитков для подсказок
    
    Returns:
        list: Список напитков
    """
    popular_drinks = [
        'вода',
        'кофе',
        'чай',
        'сок',
        'молоко',
        'кефир',
        'кола',
        'смузи',
        'коктейль',
        'компот',
    ]
    
    return popular_drinks

def validate_drink_input(text: str) -> Tuple[bool, Optional[str]]:
    """
    Валидирует ввод напитка
    
    Args:
        text: Текст для валидации
        
    Returns:
        Tuple[bool, str]: (валидно, сообщение об ошибке)
    """
    if not text or len(text.strip()) < 2:
        return False, "Слишком короткое название напитка"
    
    drink_name, volume, calories = parse_drink_input(text)
    
    if not drink_name:
        return False, "Не удалось определить напиток"
    
    if not volume:
        return False, "Не удалось определить объём"
    
    if volume < 10 or volume > 2000:
        return False, "Объём должен быть от 10 до 2000 мл"
    
    return True, None

def get_nutrition_info(drink_name: str, volume_ml: int) -> Dict:
    """
    Возвращает подробную нутритивную информацию
    
    Args:
        drink_name: Название напитка
        volume_ml: Объём в мл
        
    Returns:
        dict: Нутритивная информация
    """
    calories = calculate_calories(drink_name, volume_ml)
    calories_per_100ml = DRINK_CALORIES_DB.get(drink_name, 0)
    
    # Базовая информация о БЖУ для напитков
    nutrition = {
        'calories': calories,
        'protein': 0.0,
        'fat': 0.0,
        'carbs': 0.0,
        'sugar': 0.0,
    }
    
    # Корректируем БЖУ для некоторых напитков
    if drink_name in ['молоко', 'кефир', 'ряженка']:
        nutrition['protein'] = volume_ml * 0.03  # ~3г белка на 100мл
        nutrition['fat'] = volume_ml * 0.025    # ~2.5г жира на 100мл
        nutrition['carbs'] = volume_ml * 0.05    # ~5г углеводов на 100мл
        nutrition['sugar'] = volume_ml * 0.05    # ~5г сахара на 100мл
    
    elif drink_name in ['сок', 'компот', 'смузи', 'коктейль']:
        nutrition['carbs'] = calories / 4  # Углеводы из калорий
        nutrition['sugar'] = calories / 4  # Предполагаем, что это сахар
    
    elif drink_name in ['йогурт']:
        nutrition['protein'] = volume_ml * 0.04  # ~4г белка на 100мл
        nutrition['fat'] = volume_ml * 0.02     # ~2г жира на 100мл
        nutrition['carbs'] = volume_ml * 0.06    # ~6г углеводов на 100мл
        nutrition['sugar'] = volume_ml * 0.06    # ~6г сахара на 100мл
    
    return nutrition

def is_water(drink_name: str) -> bool:
    """
    Проверяет, является ли напиток водой
    
    Args:
        drink_name: Название напитка
        
    Returns:
        bool: True если это вода
    """
    water_variants = ['вода', 'минералка', 'минеральная вода', 'газированная вода']
    return drink_name.lower() in water_variants

def get_drink_category(drink_name: str) -> str:
    """
    Возвращает категорию напитка
    
    Args:
        drink_name: Название напитка
        
    Returns:
        str: Категория
    """
    categories = {
        'hot': ['кофе', 'чай', 'какао', 'горячий шоколад'],
        'cold': ['сок', 'кола', 'пепси', 'газировка', 'минералка', 'смузи', 'коктейль'],
        'dairy': ['молоко', 'кефир', 'ряженка', 'йогурт'],
        'sweet': ['сок', 'кола', 'пепси', 'газировка', 'компот', 'лимонад', 'смузи', 'коктейль'],
        'healthy': ['вода', 'минералка', 'чай', 'кефир', 'ряженка', 'йогурт'],
    }
    
    for category, drinks in categories.items():
        if drink_name.lower() in drinks:
            return category
    
    return 'other'
