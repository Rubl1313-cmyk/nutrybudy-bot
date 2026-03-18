"""
Конвертер единиц измерения для продуктов
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Справка средних весов продуктов в граммах
UNIT_WEIGHTS = {
    # Фрукты
    "яблоко": 150,
    "банан": 120,
    "апельсин": 200,
    "лимон": 60,
    "груша": 140,
    "персик": 100,
    "слива": 40,
    "киви": 80,
    
    # Овощи
    "картофель": 100,
    "картофелина": 100,
    "лук": 70,
    "луковица": 70,
    "морковь": 80,
    "морковка": 80,
    "свекла": 150,
    "огурец": 100,
    "помидор": 100,
    "чеснок": 5,
    "зубчик": 5,
    
    # Яйца
    "яйцо": 50,
    "яйца": 50,
    
    # Хлебобулочные изделия
    "хлеб": 30,
    "кусок": 30,
    "ломтик": 20,
    "батон": 400,
    
    # Молочные продукты
    "стакан": 200,  # молоко, кефир
    "чашка": 150,   # творог, йогурт
    "ложка": 15,    # сметана, масло
    "столовая ложка": 15,
    "чайная ложка": 5,
    
    # Крупы и макароны
    "стакан": 200,  # крупа
    "горсть": 50,
    
    # Мясо и птица
    "курица": 150,  # бедро, грудка
    "котлета": 80,
    "отбивная": 120,
    "сосиска": 50,
    "колбаса": 50,
    
    # Рыба
    "рыба": 150,
    "кусок": 100,
    
    # Орехи
    "горсть": 30,
    "щепотка": 2,
    
    # Сладости
    "шоколадка": 100,
    "конфета": 15,
    "печенье": 80,
    "вафля": 80,
    "булочка": 80,
}

def convert_to_grams(name: str, quantity: float, unit: str) -> float:
    """
    Конвертирует количество и единицу измерения в граммы
    
    Args:
        name: Название продукта
        quantity: Количество
        unit: Единица измерения (шт, г, кг, мл, ложка, стакан и т.д.)
        
    Returns:
        Вес в граммах
    """
    try:
        # Если уже в граммах
        if unit in ['г', 'гр', 'gram', 'грамм', 'граммов']:
            return float(quantity)
        
        # Если в килограммах
        elif unit in ['кг', 'kg', 'килограмм', 'килограммов']:
            return float(quantity) * 1000
        
        # Если в миллилитрах (для воды ~1г = 1мл)
        elif unit in ['мл', 'ml', 'миллилитр', 'миллилитров']:
            return float(quantity)
        
        # Если в литрах
        elif unit in ['л', 'l', 'литр']:
            return float(quantity) * 1000
        
        # Если в штуках - ищем средний вес
        elif unit in ['шт', 'штука', 'штуки', 'штук']:
            name_lower = name.lower().strip()
            
            # Ищем точное совпадение
            if name_lower in UNIT_WEIGHTS:
                return float(quantity) * UNIT_WEIGHTS[name_lower]
            
            # Ищем по ключевым словам
            for key, weight in UNIT_WEIGHTS.items():
                if key in name_lower:
                    return float(quantity) * weight
            
            # Если не нашли, используем средний вес 100г
            logger.warning(f"[WARNING] Неизвестный продукт для конвертации: {name}, используем 100г за шт")
            return float(quantity) * 100
        
        # Ложки
        elif unit in ['ложка', 'ложки', 'ложек', 'столовая ложка', 'столовых ложек']:
            return float(quantity) * 15
        
        elif unit in ['чайная ложка', 'чайных ложек']:
            return float(quantity) * 5
        
        # Стаканы
        elif unit in ['стакан', 'стакана', 'стаканов']:
            return float(quantity) * 200
        
        # Чашки
        elif unit in ['чашка', 'чашки', 'чашек']:
            return float(quantity) * 150
        
        # Щепотки
        elif unit in ['щепотка', 'щепотки']:
            return float(quantity) * 1
        
        # Пучки
        elif unit in ['пучок', 'пучка', 'пучков']:
            return float(quantity) * 5
        
        # Куски
        elif unit in ['кусок', 'куска', 'кусков']:
            return float(quantity) * 50
        
        # Ломтики
        elif unit in ['ломтик', 'ломтика', 'ломтиков']:
            return float(quantity) * 20
        
        # Горсти
        elif unit in ['горсть', 'горсти']:
            return float(quantity) * 50
        
        # Если неизвестная единица, возвращаем как есть (предположим граммы)
        else:
            logger.warning(f"[WARNING] Неизвестная единица измерения: {unit}, используем как есть")
            return float(quantity)
            
    except (ValueError, TypeError) as e:
        logger.error(f"[ERROR] Ошибка конвертации {name} {quantity} {unit}: {e}")
        return float(quantity)  # Fallback

def get_unit_info(name: str, quantity: float, unit: str) -> Dict:
    """
    Возвращает информацию о конвертации для логирования
    
    Returns:
        Dict с информацией о конвертации
    """
    original_weight = quantity
    grams = convert_to_grams(name, quantity, unit)
    
    return {
        'original_weight': original_weight,
        'original_unit': unit,
        'converted_grams': grams,
        'name': name,
        'conversion_applied': grams != original_weight or unit not in ['г', 'гр', 'gram']
    }
