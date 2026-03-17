"""
Утилиты для работы с часовыми поясами пользователей
"""
from datetime import datetime, timezone
from typing import Dict, Optional
import pytz

# Популярные города России и мира с их часовыми поясами
POPULAR_CITIES = {
    'Калининград': 'Europe/Kaliningrad',      # UTC+2
    'Москва': 'Europe/Moscow',                # UTC+3
    'Санкт-Петербург': 'Europe/Moscow',
    'Мурманск': 'Europe/Moscow',              # UTC+3
    'Архангельск': 'Europe/Moscow',           # UTC+3
    'Волгоград': 'Europe/Moscow',             # UTC+3
    'Казань': 'Europe/Moscow',                 # UTC+3
    'Нижний Новгород': 'Europe/Moscow',        # UTC+3
    'Самара': 'Europe/Samara',                 # UTC+4
    'Екатеринбург': 'Asia/Yekaterinburg',      # UTC+5
    'Омск': 'Asia/Omsk',                       # UTC+6
    'Красноярск': 'Asia/Krasnoyarsk',          # UTC+7
    'Иркутск': 'Asia/Irkutsk',                  # UTC+8
    'Якутск': 'Asia/Yakutsk',                  # UTC+9
    'Владивосток': 'Asia/Vladivostok',          # UTC+10
    'Магадан': 'Asia/Magadan',                  # UTC+11
    'Камчатка': 'Asia/Kamchatka',               # UTC+12
    
    # Другие крупные города мира
    'Лондон': 'Europe/London',                 # UTC+0
    'Париж': 'Europe/Paris',                   # UTC+1
    'Берлин': 'Europe/Berlin',                 # UTC+1
    'Рим': 'Europe/Rome',                       # UTC+1
    'Нью-Йорк': 'America/New_York',           # UTC-5
    'Лос-Анджелес': 'America/Los_Angeles',     # UTC-8
    'Токио': 'Asia/Tokyo',                     # UTC+9
    'Пекин': 'Asia/Shanghai',                  # UTC+8
    'Дубай': 'Asia/Dubai',                     # UTC+4
    'Сингапур': 'Asia/Singapore',               # UTC+8
    'Сидней': 'Australia/Sydney',              # UTC+10
}

# Популярные смещения для ручного ввода
POPULAR_OFFSETS = [
    'UTC-12', 'UTC-11', 'UTC-10', 'UTC-9', 'UTC-8', 'UTC-7',
    'UTC-6', 'UTC-5', 'UTC-4', 'UTC-3', 'UTC-2', 'UTC-1',
    'UTC+0', 'UTC+1', 'UTC+2', 'UTC+3', 'UTC+4', 'UTC+5',
    'UTC+6', 'UTC+7', 'UTC+8', 'UTC+9', 'UTC+10', 'UTC+11', 'UTC+12'
]

def get_user_local_date(user_timezone: str) -> datetime.date:
    """
    Получает текущую локальную дату пользователя
    
    Args:
        user_timezone: Часовой пояс в формате IANA (например, 'Europe/Moscow')
        
    Returns:
        datetime.date: Локальная дата пользователя
    """
    try:
        tz = pytz.timezone(user_timezone)
        now_local = datetime.now(tz)
        return now_local.date()
    except Exception:
        # Если часовой пояс некорректный, используем UTC
        return datetime.now(timezone.utc).date()

def get_user_local_datetime(user_timezone: str) -> datetime:
    """
    Получает текущую локальную дату и время пользователя
    
    Args:
        user_timezone: Часовой пояс в формате IANA (например, 'Europe/Moscow')
        
    Returns:
        datetime: Локальная дата и время пользователя
    """
    try:
        tz = pytz.timezone(user_timezone)
        return datetime.now(tz)
    except Exception:
        # Если часовой пояс некорректный, используем UTC
        return datetime.now(timezone.utc)

def convert_utc_to_local(utc_datetime: datetime, user_timezone: str) -> datetime:
    """
    Преобразует UTC время в локальное время пользователя
    
    Args:
        utc_datetime: UTC datetime
        user_timezone: Часовой пояс пользователя
        
    Returns:
        datetime: Локальное время пользователя
    """
    try:
        if utc_datetime.tzinfo is None:
            utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
        
        tz = pytz.timezone(user_timezone)
        return utc_datetime.astimezone(tz)
    except Exception:
        # Если часовой пояс некорректный, возвращаем UTC
        return utc_datetime

def parse_timezone_input(text: str) -> Optional[str]:
    """
    Парсит ввод часового пояса от пользователя
    
    Args:
        text: Текст от пользователя
        
    Returns:
        str: IANA идентификатор часового пояса или None
    """
    text = text.strip().upper()
    
    # Проверяем прямое соответствие городам
    for city, tz in POPULAR_CITIES.items():
        if city.upper() in text or tz.upper() in text:
            return tz
    
    # Проверяем смещения
    for offset in POPULAR_OFFSETS:
        if offset in text:
            return offset
    
    return None

def get_timezone_display_name(tz_name: str) -> str:
    """
    Получает отображаемое имя часового пояса
    
    Args:
        tz_name: IANA идентификатор часового пояса
        
    Returns:
        str: Отображаемое имя
    """
    # Ищем город по IANA идентификатору
    for city, tz in POPULAR_CITIES.items():
        if tz == tz_name:
            return f"{city} ({tz_name})"
    
    # Если не нашли в городах, возвращаем как есть
    return tz_name
