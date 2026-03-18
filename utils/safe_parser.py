"""
Утилиты для безопасного парсинга пользовательского ввода
"""
import re
import logging
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)

def safe_parse_float(text: str, field_name: str = "число") -> Tuple[Optional[float], Optional[str]]:
    """
    Безопасное парсинг float из текста с расширенной обработкой
    
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
        
        # Ищем число в тексте
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
            return None, f"{field_name.capitalize()} не может быть отрицательным"
        
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
    Безопасное парсинг int из текста
    
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
        # Конвертируем в float, затем в int если целые
        result = []
        for num_str in numbers[:max_count]:
            try:
                if '.' in num_str:
                    result.append(float(num_str))
                else:
                    result.append(int(num_str))
            except ValueError:
                continue
        return result
    except Exception as e:
        logger.error(f"Error extracting numbers from '{text}': {e}")
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
    message = f"[ERROR] Ошибка ввода {field_name}: {error}"
    
    if examples:
        examples_str = ", ".join(str(ex) for ex in examples)
        message += f"\n\nПримеры: {examples_str}"
    
    return message

def clean_numeric_input(text: str) -> str:
    """
    Очищает текстовый ввод от лишних символов
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""
    
    # Убираем пробелы по краям
    cleaned = text.strip()
    
    # Заменяем запятые на точки
    cleaned = cleaned.replace(',', '.')
    
    # Убираем лишние пробелы внутри числа
    cleaned = re.sub(r'(\d+)\s+(\d+)', r'\1\2', cleaned)
    
    # Убираем все символы кроме цифр, точки, минуса, плюса
    cleaned = re.sub(r'[^\d\.\+\-]', '', cleaned)
    
    return cleaned

def validate_percentage(value: float) -> Tuple[bool, Optional[str]]:
    """
    Валидация процентного значения
    
    Args:
        value: Значение для проверки
        
    Returns:
        Tuple[bool, Optional[str]]: (валидно, ошибка)
    """
    if not (0 <= value <= 100):
        return False, "Процент должен быть от 0 до 100"
    return True, None

def validate_date_format(date_str: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация формата даты
    
    Args:
        date_str: Строка с датой
        
    Returns:
        Tuple[bool, Optional[str]]: (валидно, ошибка)
    """
    try:
        from datetime import datetime
        # Пробуем разные форматы
        formats = ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True, None
            except ValueError:
                continue
        
        return False, "Неверный формат даты. Используйте ДД.ММ.ГГГГ"
    except Exception:
        return False, "Ошибка при обработке даты"

def validate_time_format(time_str: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация формата времени
    
    Args:
        time_str: Строка со временем
        
    Returns:
        Tuple[bool, Optional[str]]: (валидно, ошибка)
    """
    try:
        from datetime import datetime
        # Пробуем разные форматы
        formats = ['%H:%M', '%H:%M:%S', '%H.%M', '%H.%M.%S']
        
        for fmt in formats:
            try:
                datetime.strptime(time_str, fmt)
                return True, None
            except ValueError:
                continue
        
        return False, "Неверный формат времени. Используйте ЧЧ:ММ"
    except Exception:
        return False, "Ошибка при обработке времени"

def extract_email(text: str) -> Optional[str]:
    """
    Извлекает email из текста
    
    Args:
        text: Текст для анализа
        
    Returns:
        Optional[str]: Найденный email или None
    """
    try:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else None
    except Exception:
        return None

def extract_phone(text: str) -> Optional[str]:
    """
    Извлекает номер телефона из текста
    
    Args:
        text: Текст для анализа
        
    Returns:
        Optional[str]: Найденный телефон или None
    """
    try:
        # Убираем все кроме цифр, плюса, минуса, скобок
        cleaned = re.sub(r'[^\d\+\-\(\)\s]', '', text)
        # Убираем пробелы
        cleaned = re.sub(r'\s', '', cleaned)
        
        # Проверяем минимальную длину
        if len(cleaned) >= 10:
            return cleaned
        return None
    except Exception:
        return None

def parse_weight_input(text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Специализированный парсер для ввода веса
    
    Args:
        text: Текст с весом
        
    Returns:
        Tuple[Optional[float], Optional[str]]: (вес, ошибка)
    """
    # Ищем паттерны вроде "70 кг", "70кг", "70.5 кг"
    patterns = [
        r'(\d+\.?\d*)\s*кг',
        r'(\d+\.?\d*)\s*kg',
        r'^(\d+\.?\d*)$'  # Просто число
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            try:
                weight = float(match.group(1))
                if 30 <= weight <= 300:
                    return weight, None
                else:
                    return None, "Вес должен быть от 30 до 300 кг"
            except ValueError:
                continue
    
    return None, "Не удалось определить вес. Используйте формат: 70 кг"

def parse_height_input(text: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Специализированный парсер для ввода роста
    
    Args:
        text: Текст с ростом
        
    Returns:
        Tuple[Optional[int], Optional[str]]: (рост, ошибка)
    """
    # Ищем паттерны вроде "175 см", "175см", "175"
    patterns = [
        r'(\d+)\s*см',
        r'(\d+)\s*cm',
        r'^(\d+)$'  # Просто число
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            try:
                height = int(match.group(1))
                if 100 <= height <= 250:
                    return height, None
                else:
                    return None, "Рост должен быть от 100 до 250 см"
            except ValueError:
                continue
    
    return None, "Не удалось определить рост. Используйте формат: 175 см"

def parse_age_input(text: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Специализированный парсер для ввода возраста
    
    Args:
        text: Текст с возрастом
        
    Returns:
        Tuple[Optional[int], Optional[str]]: (возраст, ошибка)
    """
    # Ищем паттерны вроде "25 лет", "25года", "25"
    patterns = [
        r'(\d+)\s*(?:лет|года|год|г)',
        r'(\d+)\s*(?:years?|yrs?)',
        r'^(\d+)$'  # Просто число
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            try:
                age = int(match.group(1))
                if 10 <= age <= 120:
                    return age, None
                else:
                    return None, "Возраст должен быть от 10 до 120 лет"
            except ValueError:
                continue
    
    return None, "Не удалось определить возраст. Используйте формат: 25 лет"
