"""
Утилиты для безопасного парсинга чисел из пользовательского ввода
"""
import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def safe_parse_float(text: str, field_name: str = "число") -> Tuple[Optional[float], Optional[str]]:
    """
    Безопасно парсит float из текста с расширенной обработкой ошибок
    
    Args:
        text: Текст для парсинга
        field_name: Название поля для сообщений об ошибках
        
    Returns:
        Tuple[Optional[float], Optional[str]]: (значение, ошибка)
    """
    if not text or not isinstance(text, str):
        return None, f"Текст для {field_name} отсутствует или некорректен"
    
    try:
        # Убираем пробелы и заменяем запятые на точки
        clean_text = text.strip().replace(',', '.')
        
        # Ищем числа в тексте
        number_match = re.search(r'[-+]?\d*\.?\d+', clean_text)
        
        if not number_match:
            return None, f"Не удалось найти {field_name} в тексте"
        
        number_str = number_match.group()
        value = float(number_str)
        
        # Проверяем на валидные диапазоны для разных типов данных
        if field_name == "вес" and not (30 <= value <= 300):
            return None, f"Вес должен быть от 30 до 300 кг"
        
        if field_name == "рост" and not (100 <= value <= 250):
            return None, f"Рост должен быть от 100 до 250 см"
        
        if field_name == "возраст" and not (10 <= value <= 120):
            return None, f"Возраст должен быть от 10 до 120 лет"
        
        if field_name in ["калории", "белки", "жиры", "углеводы"] and value < 0:
            return None, f"{field_name.capitalize()} не могут быть отрицательными"
        
        if field_name == "температура" and not (-50 <= value <= 60):
            return None, f"Температура должна быть от -50°C до 60°C"
        
        return value, None
        
    except ValueError as e:
        return None, f"Некорректный формат {field_name}: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error parsing {field_name} from '{text}': {e}")
        return None, f"Ошибка при обработке {field_name}"

def safe_parse_int(text: str, field_name: str = "число") -> Tuple[Optional[int], Optional[str]]:
    """
    Безопасно парсит int из текста
    
    Args:
        text: Текст для парсинга
        field_name: Название поля для сообщений об ошибках
        
    Returns:
        Tuple[Optional[int], Optional[str]]: (значение, ошибка)
    """
    value, error = safe_parse_float(text, field_name)
    if error:
        return None, error
    
    try:
        return int(value), None
    except (ValueError, TypeError):
        return None, f"Значение должно быть целым числом"

def extract_multiple_numbers(text: str, max_count: int = 5) -> list:
    """
    Извлекает все числа из текста
    
    Args:
        text: Текст для анализа
        max_count: Максимальное количество чисел для извлечения
        
    Returns:
        list: Список найденных чисел
    """
    try:
        numbers = re.findall(r'[-+]?\d*\.?\d+', text)
        return [float(num) for num in numbers[:max_count]]
    except Exception:
        return []

def format_parsing_error(field_name: str, error: str, examples: list = None) -> str:
    """
    Форматирует сообщение об ошибке парсинга
    
    Args:
        field_name: Название поля
        error: Текст ошибки
        examples: Примеры корректного ввода
        
    Returns:
        str: Формированное сообщение об ошибке
    """
    message = f"❌ Ошибка при вводе {field_name}: {error}"
    
    if examples:
        message += "\n\n💡 <b>Примеры корректного ввода:</b>\n"
        for example in examples:
            message += f"• {example}\n"
    
    return message
