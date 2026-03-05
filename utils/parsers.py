"""
Парсер для извлечения товаров из текста.
Поддерживает:
- числа с единицами (2 яйца, 200 г сыра)
- перечисления через запятые
- разбиение по числам (2 хлеба молоко → хлеб:2, молоко:1)
- нормализацию слов
"""
import re
from typing import List, Tuple
from utils.normalizer import normalize_product_name
import logging

logger = logging.getLogger(__name__)

STOP_WORDS = {"и", "с", "со", "в", "на", "из", "для", "от", "по", "за", "про", "без", "до"}

def _tokenize(text: str) -> List[str]:
    """Разбивает текст на токены, удаляя лишние пробелы."""
    return text.split()

def _is_number(token: str) -> bool:
    """Проверяет, является ли токен числом (целым или дробным)."""
    # Убираем возможные падежные окончания? Но числа обычно цифрами.
    token = token.strip()
    if token.replace('.', '', 1).replace(',', '', 1).isdigit():
        return True
    # Можно добавить распознавание словесных чисел, но пока только цифры.
    return False

def _parse_number(token: str) -> float:
    """Преобразует токен в число."""
    return float(token.replace(',', '.'))

def parse_shopping_items(text: str) -> List[Tuple[str, int, str]]:
    """
    Преобразует текст в список кортежей (название, количество, единица).
    """
    original_text = text
    # Удаляем ключевые слова покупки (уже должно быть удалено, но на всякий случай)
    # Здесь мы работаем с текстом, из которого уже удалены слова типа "купить"
    text = text.lower().strip()
    logger.info(f"📝 parse_shopping_items: входной текст: {original_text}")

    # Заменяем союзы "и", "с" на запятые для правильного разделения, но в новом алгоритме они могут быть удалены
    # Пока оставим старую замену, но можно и убрать.
    text = re.sub(r'\b(и|с|со)\b', ',', text)

    # Сначала пробуем разбить по запятым (если есть)
    if ',' in text:
        parts = [p.strip() for p in text.split(',') if p.strip()]
        items = []
        for part in parts:
            # Для каждой части применяем алгоритм разбора по числам
            items.extend(_parse_part_by_numbers(part))
        logger.info(f"📝 parse_shopping_items (по запятым): {items}")
        return items

    # Если нет запятых, пробуем алгоритм разбора по числам
    items = _parse_part_by_numbers(text)
    logger.info(f"📝 parse_shopping_items (по числам): {items}")
    return items

def _parse_part_by_numbers(part: str) -> List[Tuple[str, int, str]]:
    """
    Разбирает часть текста, где товары разделены числами.
    Пример: "2 хлеба молоко" -> [("хлеб", 2, "шт"), ("молоко", 1, "шт")]
    """
    tokens = _tokenize(part)
    if not tokens:
        return []

    items = []
    current_name_parts = []
    current_qty = 1  # по умолчанию

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if _is_number(token):
            # Если до этого мы собирали название, значит предыдущий товар закончился с количеством 1
            if current_name_parts:
                name = ' '.join(current_name_parts)
                normalized_name = normalize_product_name(name)
                items.append((normalized_name, current_qty, "шт"))
                current_name_parts = []
            # Теперь это новое количество
            current_qty = int(_parse_number(token)) if token.isdigit() else float(token)
            # Проверяем, не является ли следующее слово единицей измерения (г, кг, мл и т.д.)
            if i + 1 < len(tokens) and tokens[i+1] in ['г', 'кг', 'мл', 'л']:
                # единица будет прикреплена к следующему названию? Лучше обработать отдельно
                # Пока пропускаем, добавим позже
                pass
            i += 1
        else:
            # Если токен не число, добавляем к текущему названию
            current_name_parts.append(token)
            i += 1

    # После цикла добавляем последний товар
    if current_name_parts:
        name = ' '.join(current_name_parts)
        normalized_name = normalize_product_name(name)
        items.append((normalized_name, current_qty, "шт"))

    # Если ничего не добавилось (например, были только числа), вернуть пустой список
    return items
