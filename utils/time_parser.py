"""
Парсинг времени из текстовых выражений для напоминаний.
Поддерживает форматы:
- ЧЧ:ММ, ЧЧ.ММ
- X часов Y минут с уточнением времени суток
- X часов с уточнением времени суток
- Слова-уточнения: утра, дня, вечера, ночи
"""
import re
from typing import Optional, Tuple

# Соответствие частей суток и диапазонов часов (24-часовой формат)
TIMES_OF_DAY = {
    "ночи": (0, 3),      # ночь: 0-3
    "утра": (4, 11),     # утро: 4-11
    "дня": (12, 16),     # день: 12-16
    "вечера": (17, 23),  # вечер: 17-23
}

# Синонимы (можно расширять)
SYNONYMS = {
    "ночь": "ночи",
    "утро": "утра",
    "день": "дня",
    "вечер": "вечера",
    "полдень": "дня",
    "полночь": "ночи",
}


def _get_time_of_day(text: str) -> Optional[Tuple[int, int]]:
    """Определяет часть суток по тексту и возвращает диапазон часов."""
    for word, (start, end) in TIMES_OF_DAY.items():
        if word in text:
            return (start, end)
    for syn, target in SYNONYMS.items():
        if syn in text:
            return TIMES_OF_DAY[target]
    return None


def _adjust_hour(hour: int, tod_range: Tuple[int, int]) -> int:
    """
    Корректирует час из 12-часового формата в 24-часовой на основе времени суток.
    tod_range: (start, end) – диапазон, в который должно попадать время.
    """
    start, end = tod_range
    # Если час уже в диапазоне, оставляем как есть
    if start <= hour <= end:
        return hour
    # Если час из первой половины дня (1-11) и диапазон начинается с 12 (день/вечер), прибавляем 12
    if 1 <= hour <= 11 and start >= 12:
        return hour + 12
    # Если час 12 и диапазон ночной (0-3), превращаем в 0
    if hour == 12 and start == 0:
        return 0
    # Если час 12 и диапазон дневной (12-16), оставляем 12
    if hour == 12 and start == 12:
        return 12
    # В остальных случаях возвращаем исходный (возможно, неверный)
    return hour


def parse_time(text: str) -> Optional[str]:
    """
    Извлекает время из текста. Возвращает строку "ЧЧ:ММ" или None.
    """
    text = text.lower().strip()

    # 1. Поиск формата ЧЧ:ММ или ЧЧ.ММ
    match = re.search(r'(\d{1,2})[:.](\d{2})', text)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"

    # 2. Поиск паттерна "X час Y минут" или "X часов"
    # Сначала ищем часы и минуты
    match = re.search(r'(\d{1,2})\s*(?:час|часов|часа)(?:\s*(\d{1,2})\s*минут)?', text)
    if match:
        h = int(match.group(1))
        m = int(match.group(2)) if match.group(2) else 0
        tod_range = _get_time_of_day(text)
        if tod_range:
            h = _adjust_hour(h, tod_range)
        else:
            # Если нет уточнения времени суток, предполагаем, что час уже в 24-часовом формате
            # (но это может быть неверно, лучше вернуть None и уточнить)
            # Пока считаем, что если час 1-12 и нет уточнения, то это неопределённо
            if 1 <= h <= 12:
                return None  # Требуем уточнения
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"
        return None

    # 3. Поиск только часа со словом "час"
    match = re.search(r'(\d{1,2})\s*(?:час|часов|часа)', text)
    if match:
        h = int(match.group(1))
        tod_range = _get_time_of_day(text)
        if tod_range:
            h = _adjust_hour(h, tod_range)
        else:
            # Без уточнения – неопределённо
            return None
        return f"{h:02d}:00"

    # 4. Можно добавить парсинг словесных чисел (один, два...), но пока опустим

    return None
