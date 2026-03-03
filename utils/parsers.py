"""
Парсер для извлечения товаров из текста.
Поддерживает:
- числа с единицами (2 яйца, 200 г сыра)
- перечисления через запятые
- разбиение по пробелам, если нет чисел
- нормализацию слов
"""
import re
from typing import List, Tuple
from utils.normalizer import normalize_product_name

# Союзы и предлоги, которые не должны быть товарами
STOP_WORDS = {"и", "с", "со", "в", "на", "из", "для", "от", "по", "за", "про", "без", "до"}


def parse_shopping_items(text: str) -> List[Tuple[str, int, str]]:
    """
    Преобразует текст в список кортежей (название, количество, единица).
    """
    # Заменяем союзы "и", "с" на запятые для правильного разделения
    text = re.sub(r'\b(и|с|со)\b', ',', text.lower())

    # Разделяем по запятым
    parts = re.split(r'[,;]', text)
    items = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Разбиваем часть на отдельные компоненты
        subparts = _split_part(part)
        for subpart in subparts:
            item = _parse_single_item(subpart)
            if item:
                items.append(item)

    return items


def _split_part(part: str) -> List[str]:
    """
    Разбивает часть текста на отдельные товары.
    Если есть число, оставляет как единое целое.
    Иначе разбивает по пробелам, удаляя стоп-слова.
    """
    # Если есть число, не разбиваем
    if re.search(r'\d', part):
        return [part]

    # Разбиваем по пробелам
    words = part.split()
    result = []
    for word in words:
        if word not in STOP_WORDS:
            result.append(word)
    return result if result else [part]


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

        # Нормализуем название
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
        # Нет числа – нормализуем и добавляем с количеством 1
        name = normalize_product_name(text)
        return (name, 1, "шт")
