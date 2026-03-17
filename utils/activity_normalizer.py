"""
Нормализация уровней активности
"""
import logging

logger = logging.getLogger(__name__)

# Маппинг русских названий на английские
ACTIVITY_MAPPING = {
    'минимальная': 'low',
    'низкая': 'low',
    'сидячий': 'low',
    'малоподвижный': 'low',
    
    'умеренная': 'medium',
    'средняя': 'medium',
    'умеренная активность': 'medium',
    'нормальная': 'medium',
    
    'высокая': 'high',
    'интенсивная': 'high',
    'высокая активность': 'high',
    'очень активный': 'high',
    'спортсмен': 'high',
    
    # Прямые английские варианты
    'low': 'low',
    'medium': 'medium',
    'high': 'high',
}

# Коэффициенты активности
ACTIVITY_MULTIPLIERS = {
    'low': 1.2,
    'medium': 1.55,
    'high': 1.9
}

def normalize_activity_level(activity_level: str) -> str:
    """
    Нормализует уровень активности в стандартный формат
    
    Args:
        activity_level: Уровень активности (русский или английский)
        
    Returns:
        str: Нормализованный уровень активности ('low', 'medium', 'high')
    """
    if not activity_level:
        return 'medium'  # По умолчанию
    
    activity_lower = activity_level.lower().strip()
    
    # Проверяем прямое соответствие
    if activity_lower in ACTIVITY_MAPPING:
        return ACTIVITY_MAPPING[activity_lower]
    
    # Проверяем частичные совпадения
    for key, value in ACTIVITY_MAPPING.items():
        if key in activity_lower or activity_lower in key:
            return value
    
    # По умолчанию
    logger.warning(f"Unknown activity level: {activity_level}, using 'medium'")
    return 'medium'

def get_activity_multiplier(activity_level: str) -> float:
    """
    Получает коэффициент активности
    
    Args:
        activity_level: Уровень активности (любой формат)
        
    Returns:
        float: Коэффициент активности
    """
    normalized = normalize_activity_level(activity_level)
    return ACTIVITY_MULTIPLIERS.get(normalized, 1.55)
