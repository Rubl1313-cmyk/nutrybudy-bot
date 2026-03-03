"""
Парсер для извлечения товаров из текста.
Поддерживает:
- числа с единицами (2 яйца, 200 г сыра)
- перечисления через запятые и союзы "и", "с"
- нормализацию слов к именительному падежу единственного числа
"""
import re
from typing import List, Tuple
from utils.normalizer import normalize_product_name


def parse_shopping_items(text: str) -> List[Tuple[str, int, str]]:
    """
    Преобразует текст в список кортежей (название, количество, единица).
    """
    # Заменяем союзы "и", "с", "со" на запятые
    text = re.sub(r'\b(и|с|со)\b', ',', text.lower())
    
    # Разделяем по запятым
    parts = re.split(r'[,;]', text)
    items = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Разбиваем по пробелам для сложных фраз
        subparts = _split_complex_part(part)
        for subpart in subparts:
            item = _parse_single_item(subpart)
            if item:
                items.append(item)
    
    return items


def _split_complex_part(part: str) -> List[str]:
    """
    Разбивает часть, которая может содержать несколько продуктов без запятых.
    Например: "курицы морковки и риса" → ["курицы", "морковки", "риса"]
    """
    # Если есть число, не разбиваем (оставляем как единое целое)
    if re.search(r'\d', part):
        return [part]
    
    # Разбиваем по пробелам
    words = part.split()
    result = []
    current = []
    
    for word in words:
        if word in ('и', 'с', 'со'):
            if current:
                result.append(' '.join(current))
                current = []
        else:
            current.append(word)
    
    if current:
        result.append(' '.join(current))
    
    return result


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
        if qty.is_integer():
            qty = int(qty)
        name = match.group(2).strip()
        
        # Нормализуем название продукта
        name = normalize_product_name(name)
        
        # Пытаемся угадать единицу измерения
        unit_match = re.search(r'\s+(г|кг|мл|л|шт|банка|бутылка|пачка)$', name)
        if unit_match:
            unit = unit_match.group(1)
            name = name[:unit_match.start()].strip()
        else:
            unit = "шт"
        return (name, qty, unit)
    else:
        # числа нет – нормализуем и добавляем с количеством 1
        name = normalize_product_name(text)
        return (name, 1, "шт")
