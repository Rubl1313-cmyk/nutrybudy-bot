"""
Парсер для извлечения товаров из текста.
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
    - "2.5 кг картошки" → ("картошки", 2.5, "кг") – дробные числа
    """
    # Разделяем по запятым и точкам с запятой
    parts = re.split(r'[,;]', text)
    items = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Ищем число в начале (с возможной дробной частью)
        match = re.match(r'^(\d+(?:[.,]\d+)?)\s+(.+)$', part)
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
            items.append((name, qty, unit))
        else:
            # числа нет – добавляем с количеством 1
            items.append((part, 1, "шт"))
    return items
