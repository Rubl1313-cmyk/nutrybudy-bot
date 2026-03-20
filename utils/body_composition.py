"""
Утилиты для расчета состава тела на основе антропометрических данных
"""
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

def calculate_body_fat_percentage(
    gender: str, 
    age: int, 
    weight: float, 
    height: float,
    neck_cm: Optional[float] = None,
    waist_cm: Optional[float] = None,
    hip_cm: Optional[float] = None
) -> Optional[float]:
    """
    Расчет процента жировой массы по формуле ВМС (US Navy)
    
    Args:
        gender: Пол ('male' или 'female')
        age: Возраст в годах
        weight: Вес в кг
        height: Рост в см
        neck_cm: Обхват шеи в см (опционально)
        waist_cm: Обхват талии в см (опционально)
        hip_cm: Обхват бедер в см (опционально)
    
    Returns:
        Optional[float]: Процент жировой массы или None если недостаточно данных
        
    Notes:
        - Для мужчин используется формула: 495 / (1.0324 - 0.19077 * log10(waist - neck) + 0.15456 * log10(height)) - 450
        - Для женщин используется формула: 495 / (1.29579 - 0.35004 * log10(waist + hip - neck) + 0.22100 * log10(height)) - 450
        - Формула валидна для возрастов 17-66 лет
    """
    
    try:
        if gender == 'male':
            # Для мужчин нужны шея и талия
            if not neck_cm or not waist_cm:
                logger.warning("⚠️ Для расчета жира у мужчин нужны обхваты шеи и талии")
                return None
            
            # Формула ВМС для мужчин
            density = 495 / (
                1.0324 - 0.19077 * (waist_cm - neck_cm) / 10 + 0.15456 * age
            )
            
        elif gender == 'female':
            # Для женщин нужны шея, талия и бедро
            if not neck_cm or not waist_cm or not hip_cm:
                logger.warning("⚠️ Для расчета жира у женщин нужны обхваты шеи, талии и бедер")
                return None
            
            # Формула ВМС для женщин
            density = 495 / (
                1.29579 - 0.35004 * (waist_cm + hip_cm - neck_cm) / 10 + 0.22100 * age
            )
        else:
            logger.warning("⚠️ Неизвестный пол для расчета жира")
            return None
        
        body_fat_percentage = 495 / density - 450
        
        # Ограничиваем разумные пределы
        body_fat_percentage = max(3, min(body_fat_percentage, 60))
        
        logger.info(f"📊 Рассчитан процент жира: {body_fat_percentage:.1f}%")
        return body_fat_percentage
        
    except Exception as e:
        logger.error(f"❌ Ошибка при расчете процента жира: {e}")
        return None

def calculate_muscle_mass_percentage(
    gender: str,
    weight: float,
    body_fat_percentage: Optional[float] = None,
    bicep_cm: Optional[float] = None,
    forearm_cm: Optional[float] = None,
    chest_cm: Optional[float] = None
) -> Optional[float]:
    """
    Расчет процента мышечной массы
    
    Args:
        gender: Пол (male/female)
        weight: Вес в кг
        body_fat_percentage: Процент жира
        bicep_cm: Обхват бицепса в см
        forearm_cm: Обхват предплечья в см
        chest_cm: Обхват груди в см
        
    Returns:
        Процент мышечной массы или None если не хватает данных
    """
    try:
        if body_fat_percentage is None:
            logger.warning("⚠️ Для расчета мышечной массы нужен процент жира")
            return None
        
        # Базовый расчет через остаточную массу
        lean_mass = weight * (1 - body_fat_percentage / 100)
        
        # Приблизительный расчет мышечной массы (около 75% от безжировой массы)
        muscle_mass_kg = lean_mass * 0.75
        muscle_mass_percentage = (muscle_mass_kg / weight) * 100
        
        # Корректировка на основе обхватов если доступны
        if bicep_cm and forearm_cm and chest_cm:
            # Упрощенная формула корректировки на основе обхватов
            if gender == 'male':
                # Для мужчин
                size_factor = (bicep_cm + forearm_cm + chest_cm) / 100
                correction = size_factor * 2  # Приблизительная корректировка
            else:
                # Для женщин
                size_factor = (bicep_cm + forearm_cm + chest_cm) / 100
                correction = size_factor * 1.5
            
            muscle_mass_percentage += correction
        
        # Ограничиваем разумные пределы
        muscle_mass_percentage = max(20, min(muscle_mass_percentage, 60))
        
        logger.info(f"📊 Рассчитан процент мышечной массы: {muscle_mass_percentage:.1f}%")
        return muscle_mass_percentage
        
    except Exception as e:
        logger.error(f"❌ Ошибка при расчете процента мышечной массы: {e}")
        return None

def calculate_body_water_percentage(
    gender: str,
    age: int,
    weight: float,
    body_fat_percentage: Optional[float] = None
) -> Optional[float]:
    """
    Расчет процента воды в организме
    
    Args:
        gender: Пол (male/female)
        age: Возраст
        weight: Вес в кг
        body_fat_percentage: Процент жира
        
    Returns:
        Процент воды в организме или None если не хватает данных
    """
    try:
        if body_fat_percentage is None:
            # Если нет процента жира, используем средние значения
            if gender == 'male':
                water_percentage = 60.0  # Средний процент воды у мужчин
            else:
                water_percentage = 55.0  # Средний процент воды у женщин
            
            # Корректировка по возрасту
            if age > 65:
                water_percentage -= 2
            elif age < 30:
                water_percentage += 1
        else:
            # Расчет на основе процента жира
            # Мышцы содержат ~75% воды, жир ~10%
            lean_mass_percentage = 100 - body_fat_percentage
            water_percentage = (lean_mass_percentage * 0.75 + body_fat_percentage * 0.10)
            
            # Корректировка по полу
            if gender == 'male':
                water_percentage += 2
            else:
                water_percentage -= 1
            
            # Корректировка по возрасту
            if age > 65:
                water_percentage -= 2
            elif age < 30:
                water_percentage += 1
        
        # Ограничиваем разумные пределы
        water_percentage = max(40, min(water_percentage, 75))
        
        logger.info(f"📊 Рассчитан процент воды: {water_percentage:.1f}%")
        return water_percentage
        
    except Exception as e:
        logger.error(f"❌ Ошибка при расчете процента воды: {e}")
        return None

def calculate_body_composition(
    gender: str,
    age: int,
    weight: float,
    height: float,
    neck_cm: Optional[float] = None,
    waist_cm: Optional[float] = None,
    hip_cm: Optional[float] = None,
    bicep_cm: Optional[float] = None,
    forearm_cm: Optional[float] = None,
    chest_cm: Optional[float] = None
) -> Dict[str, Optional[float]]:
    """
    Комплексный расчет состава тела
    
    Args:
        gender: Пол (male/female)
        age: Возраст
        weight: Вес в кг
        height: Рост в см
        neck_cm: Обхват шеи в см
        waist_cm: Обхват талии в см
        hip_cm: Обхват бедра в см
        bicep_cm: Обхват бицепса в см
        forearm_cm: Обхват предплечья в см
        chest_cm: Обхват груди в см
        
    Returns:
        Словарь с расчетными показателями
    """
    logger.info(f"🧮 Начинаю расчет состава тела для {gender}, {age} лет, {weight}кг")
    
    # Расчет процента жира
    body_fat = calculate_body_fat_percentage(
        gender, age, weight, height, neck_cm, waist_cm, hip_cm
    )
    
    # Расчет процента мышечной массы
    muscle_mass = calculate_muscle_mass_percentage(
        gender, weight, body_fat, bicep_cm, forearm_cm, chest_cm
    )
    
    # Расчет процента воды
    body_water = calculate_body_water_percentage(
        gender, age, weight, body_fat
    )
    
    result = {
        'body_fat_percentage': body_fat,
        'muscle_mass_percentage': muscle_mass,
        'body_water_percentage': body_water
    }
    
    logger.info(f"📊 Результаты расчета: {result}")
    return result

def get_body_composition_recommendations(
    gender: str,
    age: int,
    body_fat_percentage: Optional[float],
    muscle_mass_percentage: Optional[float]
) -> Dict[str, str]:
    """
    Генерирует рекомендации на основе состава тела
    
    Args:
        gender: Пол
        age: Возраст
        body_fat_percentage: Процент жира
        muscle_mass_percentage: Процент мышечной массы
        
    Returns:
        Словарь с рекомендациями
    """
    recommendations = {}
    
    if body_fat_percentage is not None:
        if gender == 'male':
            if body_fat_percentage < 8:
                recommendations['fat'] = "⚠️ Очень низкий процент жира. Рекомендуется увеличить потребление калорий."
            elif body_fat_percentage < 15:
                recommendations['fat'] = "✅ Отличный процент жира! Продолжайте в том же духе."
            elif body_fat_percentage < 20:
                recommendations['fat'] = "👍 Хороший процент жира. Можно немного улучшить."
            elif body_fat_percentage < 25:
                recommendations['fat'] = "📈 Умеренный процент жира. Рекомендуется увеличить активность."
            else:
                recommendations['fat'] = "⚠️ Высокий процент жира. Рекомендуется диета и тренировки."
        else:
            if body_fat_percentage < 18:
                recommendations['fat'] = "⚠️ Очень низкий процент жира. Рекомендуется увеличить потребление калорий."
            elif body_fat_percentage < 22:
                recommendations['fat'] = "✅ Отличный процент жира! Продолжайте в том же духе."
            elif body_fat_percentage < 28:
                recommendations['fat'] = "👍 Хороший процент жира. Можно немного улучшить."
            elif body_fat_percentage < 32:
                recommendations['fat'] = "📈 Умеренный процент жира. Рекомендуется увеличить активность."
            else:
                recommendations['fat'] = "⚠️ Высокий процент жира. Рекомендуется диета и тренировки."
    
    if muscle_mass_percentage is not None:
        if gender == 'male':
            if muscle_mass_percentage > 45:
                recommendations['muscle'] = "💪 Отличная мышечная масса! Вы в отличной форме."
            elif muscle_mass_percentage > 40:
                recommendations['muscle'] = "👍 Хорошая мышечная масса. Продолжайте тренироваться."
            elif muscle_mass_percentage > 35:
                recommendations['muscle'] = "📈 Умеренная мышечная масса. Рекомендуется силовые тренировки."
            else:
                recommendations['muscle'] = "💪 Низкая мышечная масса. Рекомендуется увеличить силовые тренировки."
        else:
            if muscle_mass_percentage > 35:
                recommendations['muscle'] = "💪 Отличная мышечная масса! Вы в отличной форме."
            elif muscle_mass_percentage > 30:
                recommendations['muscle'] = "👍 Хорошая мышечная масса. Продолжайте тренироваться."
            elif muscle_mass_percentage > 25:
                recommendations['muscle'] = "📈 Умеренная мышечная масса. Рекомендуется силовые тренировки."
            else:
                recommendations['muscle'] = "💪 Низкая мышечная масса. Рекомендуется увеличить силовые тренировки."
    
    return recommendations
