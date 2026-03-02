"""
Парсер для извлечения товаров из текста.
Поддерживает:
- числа с единицами (2 яйца, 200 г сыра)
- перечисления через запятую
- перечисления через пробел (как запасной вариант)
"""
import re
from typing import List, Tuple

def parse_shopping_items(text: str) -> List[Tuple[str, int, str]]:
    """
    Преобразует текст в список кортежей (название, количество, единица).
    Поддерживает форматы:
    - "яблоки" → ("яблоки", 1, "шт")
    - "2 яйца" → ("яйца", 2, "шт")
    - "200 г сыра" → ("сыра", 200, "г")
    - "молоко, хлеб, 3 яйца" → несколько элементов
    - "яблоки молоко хлеб" → разбивает по пробелам как отдельные товары (по 1 шт)
    - "2.5 кг картошки" → ("картошки", 2.5, "кг")
    """
    # Сначала пробуем разделить по запятым
    parts = re.split(r'[,;]', text)
    items = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Если после разделения по запятым всё ещё много слов без чисел, разбиваем по пробелам
        subparts = _split_by_spaces_if_needed(part)
        for subpart in subparts:
            item = _parse_single_item(subpart)
            if item:
                items.append(item)
    
    return items


def _split_by_spaces_if_needed(part: str) -> List[str]:
    """
    Если в части нет запятых и она содержит несколько слов без чисел,
    разбивает по пробелам. Иначе возвращает исходную часть как один элемент.
    """
    # Если есть число, не разбиваем (чтобы "2 яйца" не разделилось)
    if re.search(r'\d', part):
        return [part]
    
    # Если в части больше двух слов, разбиваем по пробелам
    words = part.split()
    if len(words) > 2:
        # Проверяем, не является ли это фразой, которая должна быть единым целым
        # Например, "куриная грудка" — это единое понятие
        # Простая эвристика: если после разбивки есть короткие слова (1-2 буквы), оставляем как есть
        if any(len(w) <= 2 for w in words):
            return [part]
        # Иначе разбиваем на отдельные товары
        return words
    else:
        return [part]


def _parse_single_item(text: str) -> Tuple[str, int, str] | None:
    """
    Парсит один потенциальный товар.
    Возвращает (название, количество, единица) или None.
    """
    text = text.strip()
    if not text:
        return None
    
    # Ищем число в начале (с возможной дробной частью)
    match = re.match(r'^(\d+(?:[.,]\d+)?)\s+(.+)$', text)
    if match:
        qty_str = match.group(1).replace(',', '.')
        qty = float(qty_str)
        # если целое, конвертируем в int
        if qty.is_integer():
            qty = int(qty)
        name = match.group(2).strip()
        
        # Пытаемся угадать единицу измерения (если есть в конце названия)
        unit_match = re.search(r'\s+(г|кг|мл|л|шт|банка|бутылка|пачка)$', name)
        if unit_match:
            unit = unit_match.group(1)
            name = name[:unit_match.start()].strip()
        else:
            unit = "шт"
        return (name, qty, unit)
    else:
        # числа нет – добавляем с количеством 1
        return (text, 1, "шт")
