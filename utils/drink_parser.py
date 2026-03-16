"""
Парсер напитков - определение объёма и калорийности
"""
import re
import logging
from typing import Tuple, Optional
from services.food_api import LOCAL_FOOD_DB

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
    'флакон': 100,
    'порция': 200,
    'glass': 250,
    'bottle': 500,
    'cup': 200,
}

def parse_drink_amount(text: str) -> Optional[float]:
    """
    Извлекает объём напитка из текста
    
    Examples:
        "200 мл" → 200
        "0.5 л" → 500
        "1 стакан" → 250
        "2 бутылки" → 1000
    """
    text = text.lower().strip()
    
    # Ищем число + единица измерения
    patterns = [
        r'(\d+\.?\d*)\s*(мл|л|стакан|чашка|бутылка|флакон|порция|glass|bottle|cup)',
        r'(\d+)\s*(стакана|чашки|бутылки|порции)',  # Множественное число
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            unit = match.group(2).replace('а', '').replace('ы', '').replace('и', '')
            
            if unit in VOLUME_UNITS:
                return amount * VOLUME_UNITS[unit]
    
    return None

def identify_drink_type(text: str) -> Tuple[str, float]:
    """
    Определяет тип напитка и его калорийность
    
    Returns:
        (напиток, калории_на_100мл)
    """
    text = text.lower()
    
    # Ищем точное совпадение
    for drink_name, calories in DRINK_CALORIES_DB.items():
        if drink_name in text:
            return drink_name, calories
    
    # Ищем по ключевым словам
    if 'сок' in text:
        return 'сок', DRINK_CALORIES_DB['сок']
    elif 'компот' in text:
        return 'компот', DRINK_CALORIES_DB['компот']
    elif 'чай' in text:
        if 'сахар' in text or 'сахаром' in text:
            return 'чай с сахаром', DRINK_CALORIES_DB['чай с сахаром']
        elif 'молоко' in text:
            return 'чай с молоком', DRINK_CALORIES_DB['чай с молоком']
        else:
            return 'чай', DRINK_CALORIES_DB['чай']
    elif 'кофе' in text:
        if 'сахар' in text or 'сахаром' in text:
            return 'кофе с сахаром', DRINK_CALORIES_DB['кофе с сахаром']
        elif 'молоко' in text:
            return 'кофе с молоком', DRINK_CALORIES_DB['кофе с молоком']
        else:
            return 'кофе', DRINK_CALORIES_DB['кофе']
    elif 'молоко' in text:
        return 'молоко', DRINK_CALORIES_DB['молоко']
    elif 'кефир' in text:
        return 'кефир', DRINK_CALORIES_DB['кефир']
    elif 'газировк' in text or 'кола' in text or 'пепси' in text:
        return 'газировка', DRINK_CALORIES_DB['газировка']
    elif 'минерал' in text:
        return 'минералка', DRINK_CALORIES_DB['минералка']
    elif 'смузи' in text:
        return 'смузи', DRINK_CALORIES_DB['смузи']
    elif 'коктейл' in text:
        return 'коктейль', DRINK_CALORIES_DB['коктейль']
    elif 'какао' in text or 'шоколад' in text:
        return 'горячий шоколад', DRINK_CALORIES_DB['горячий шоколад']
    else:
        # По умолчанию - вода
        return 'вода', 0.0

async def parse_drink(text: str) -> Tuple[Optional[float], str, float]:
    """
    Полный парсинг напитка из текста
    
    Returns:
        (объём_мл, название, калории_в_порции)
    """
    # Определяем объём
    volume = parse_drink_amount(text)
    if not volume:
        return None, "вода", 0.0
    
    # Определяем тип напитка и калорийность
    drink_name, calories_per_100 = identify_drink_type(text)
    
    # Рассчитываем калории в порции
    total_calories = calories_per_100 * volume / 100
    
    logger.info(f"🥤 Напиток определён: {drink_name} {volume}мл, {total_calories:.1f} ккал")
    
    return volume, drink_name, total_calories
