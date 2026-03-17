"""
services/body_stats.py
Расширенные расчеты композиции тела и аналитики здоровья
"""
import math
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Импортируем BMR калькулятор
from services.calculator import calculate_bmr

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Индекс массы тела с точностью до 1 знака"""
    return round(weight_kg / ((height_cm / 100) ** 2), 1)

def interpret_bmi(bmi: float) -> Tuple[str, str]:
    """Интерпретация ИМТ с цветовой индикацией"""
    if bmi < 16.5:
        return "Выраженный дефицит массы", "🔴"
    elif bmi < 18.5:
        return "Недостаточная масса", "🟡"
    elif bmi < 25:
        return "Нормальный вес", "🟢"
    elif bmi < 30:
        return "Избыточный вес", "🟡"
    elif bmi < 35:
        return "Ожирение I степени", "🔴"
    elif bmi < 40:
        return "Ожирение II степени", "🔴"
    else:
        return "Ожирение III степени", "🔴"

def calculate_ideal_weight(height_cm: float, gender: str) -> Dict[str, float]:
    """Идеальный вес по 4 формулам"""
    h = height_cm
    
    # Формула Брока (улучшенная)
    if gender == 'male':
        broca = (h - 100) * 0.9
    else:
        broca = (h - 100) * 0.85
    
    # Формула Лоренца
    if gender == 'male':
        lorentz = h - 100 - (h - 150) / 4
    else:
        lorentz = h - 100 - (h - 150) / 2
    
    # Формула Девина
    if gender == 'male':
        devine = 50 + 0.91 * (h - 152.4)
    else:
        devine = 45.5 + 0.91 * (h - 152.4)
    
    # Здоровый диапазон по ИМТ (18.5-24.9)
    healthy_min = 18.5 * (h/100) ** 2
    healthy_max = 24.9 * (h/100) ** 2
    
    return {
        'broca': round(broca, 1),
        'lorentz': round(lorentz, 1),
        'devine': round(devine, 1),
        'healthy_min': round(healthy_min, 1),
        'healthy_max': round(healthy_max, 1),
        'healthy_range': f"{round(healthy_min, 1)}-{round(healthy_max, 1)}"
    }

def estimate_body_fat_bmi(bmi: float, age: int, gender: str) -> float:
    """Оценка % жира по формуле ВМI (грубая)"""
    if gender == 'male':
        return round(1.20 * bmi + 0.23 * age - 16.2, 1)
    else:
        return round(1.20 * bmi + 0.23 * age - 5.4, 1)

def estimate_body_fat_navy(height_cm: float, neck_cm: float, waist_cm: float, 
                          hip_cm: Optional[float] = None, gender: str = 'male') -> Optional[float]:
    """
    Метод ВМС США (Navy) - золотой стандарт антропометрии
    Точность: ±3% для большинства людей
    """
    try:
        if gender == 'male':
            # Для мужчин не нужен обхват бедер
            if neck_cm >= waist_cm:
                return None
            log_val = math.log10(waist_cm - neck_cm)
            bf_percent = 495 / (1.0324 - 0.19077 * log_val + 0.15456 * math.log10(height_cm)) - 450
        else:
            # Для женщин нужен обхват бедер
            if not hip_cm or neck_cm >= (waist_cm + hip_cm):
                return None
            log_val = math.log10(waist_cm + hip_cm - neck_cm)
            bf_percent = 495 / (1.29579 - 0.35004 * log_val + 0.22100 * math.log10(height_cm)) - 450
        
        return round(max(0, min(100, bf_percent)), 1)  # Ограничиваем 0-100%
    except (ValueError, ZeroDivisionError):
        return None

def total_body_water_watson(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Общая вода организма по формуле Watson (1979)"""
    if gender == 'male':
        tbw = 2.447 - 0.09516 * age + 0.1074 * height_cm + 0.3362 * weight_kg
    else:
        tbw = -2.097 + 0.1069 * height_cm + 0.2466 * weight_kg
    
    return round(max(0, tbw), 1)

def estimate_muscle_mass(weight_kg: float, body_fat_percent: float) -> float:
    """Приблизительная скелетно-мышечная масса"""
    fat_mass = weight_kg * (body_fat_percent / 100)
    muscle_mass = weight_kg - fat_mass
    # Скелетная масса обычно ~40% от безжировой массы
    skeletal_muscle = muscle_mass * 0.4
    return round(skeletal_muscle, 1)

def visceral_fat_risk(waist_cm: float, gender: str) -> Tuple[str, str]:
    """Оценка риска висцерального жира по обхвату талии"""
    if gender == 'male':
        if waist_cm < 94:
            return "Низкий риск", "🟢"
        elif waist_cm < 102:
            return "Повышенный риск", "🟡"
        else:
            return "Высокий риск", "🔴"
    else:
        if waist_cm < 80:
            return "Низкий риск", "🟢"
        elif waist_cm < 88:
            return "Повышенный риск", "🟡"
        else:
            return "Высокий риск", "🔴"

def calculate_body_type(height_cm: float, wrist_cm: float, gender: str) -> str:
    """Определение типа телосложения по индексу Пинье"""
    if not wrist_cm:
        return "Не определен"
    
    pignet_index = height_cm - (wrist_cm * 100 / height_cm)
    
    if gender == 'male':
        if pignet_index < 40:
            return "Эктоморф (хрупкое телосложение)"
        elif pignet_index < 50:
            return "Мезоморф (нормальное телосложение)"
        else:
            return "Эндоморф (плотное телосложение)"
    else:
        if pignet_index < 35:
            return "Эктоморф (хрупкое телосложение)"
        elif pignet_index < 45:
            return "Мезоморф (нормальное телосложение)"
        else:
            return "Эндоморф (плотное телосложение)"

def get_body_composition_analysis(weight: float, height: float, age: int, gender: str,
                                neck_cm: Optional[float] = None, waist_cm: Optional[float] = None,
                                hip_cm: Optional[float] = None, wrist_cm: Optional[float] = None,
                                chest_cm: Optional[float] = None, forearm_cm: Optional[float] = None,
                                calf_cm: Optional[float] = None, shoulder_width_cm: Optional[float] = None,
                                hip_width_cm: Optional[float] = None) -> Dict:
    """Полный анализ композиции тела"""
    
    # Базовые расчеты
    bmi = calculate_bmi(weight, height)
    bmi_status, bmi_color = interpret_bmi(bmi)
    ideal_weights = calculate_ideal_weight(height, gender)
    
    # Процент жира
    body_fat_bmi = estimate_body_fat_bmi(bmi, age, gender)
    body_fat_navy = None
    if neck_cm and waist_cm:
        body_fat_navy = estimate_body_fat_navy(height, neck_cm, waist_cm, hip_cm, gender)
    
    body_fat = body_fat_navy if body_fat_navy else body_fat_bmi
    
    # Новые метрики
    whtr = waist_to_height_ratio(waist_cm, height) if waist_cm else None
    
    bmr = calculate_bmr(weight, height, age, gender)
    meta_age = metabolic_age(bmr, age, gender, weight, height)
    
    absi_value = absi(waist_cm, bmi, height) if waist_cm and bmi else None
    absi_risk = interpret_absi(absi_value, age, gender) if absi_value else None
    
    # Состав тела
    body_water = total_body_water_watson(weight, height, age, gender)
    muscle_mass = estimate_muscle_mass(weight, body_fat)
    
    # Сегментарная мышечная масса
    muscle_segments = segmental_muscle_mass(
        weight, body_fat,
        chest_cm, forearm_cm, calf_cm,
        shoulder_width_cm, hip_width_cm, gender
    )
    
    # Риски
    visceral_risk = None
    visceral_risk_color = None
    if waist_cm:
        visceral_risk, visceral_risk_color = visceral_fat_risk(waist_cm, gender)
    
    # Тип телосложения
    body_type = calculate_body_type(height, wrist_cm, gender) if wrist_cm else "Не определен"
    
    return {
        'bmi': bmi,
        'bmi_status': bmi_status,
        'bmi_color': bmi_color,
        'ideal_weights': ideal_weights,
        'body_fat_bmi': body_fat_bmi,
        'body_fat_navy': body_fat_navy,
        'body_fat': body_fat,
        'body_water': body_water,
        'muscle_mass': muscle_mass,
        'visceral_risk': visceral_risk,
        'visceral_risk_color': visceral_risk_color,
        'body_type': body_type,
        'has_navy_data': body_fat_navy is not None,
        # Новые метрики
        'whtr': whtr,
        'metabolic_age': meta_age,
        'absi': absi_value,
        'absi_risk': absi_risk,
        'muscle_segments': muscle_segments,
    }

def get_weight_change_trend(current_weight: float, previous_weights: list) -> Dict:
    """Анализ тренда веса"""
    if not previous_weights or len(previous_weights) < 2:
        return {'trend': 'stable', 'change': 0, 'period': 'недостаточно данных'}
    
    # Берем последние 7 измерений
    recent_weights = previous_weights[-7:] if len(previous_weights) >= 7 else previous_weights
    oldest_weight = recent_weights[0]
    
    change = current_weight - oldest_weight
    period = len(recent_weights) - 1
    
    if abs(change) < 0.5:
        trend = 'stable'
        trend_emoji = '➡️'
    elif change > 0:
        trend = 'gaining'
        trend_emoji = '📈'
    else:
        trend = 'losing'
        trend_emoji = '📉'
    
    return {
        'trend': trend,
        'trend_emoji': trend_emoji,
        'change': round(change, 1),
        'period': period,
        'rate': round(change / period, 2) if period > 0 else 0
    }

def waist_to_height_ratio(waist_cm: float, height_cm: float) -> float:
    """Отношение талии к росту (WHtR)"""
    if not waist_cm or not height_cm:
        return None
    return round(waist_cm / height_cm, 3)

def metabolic_age(bmr: float, chronological_age: int, gender: str, weight_kg: float, height_cm: float) -> int:
    """Расчет метаболического возраста"""
    if not bmr:
        return chronological_age
    
    # Средние значения BMR по возрасту и полу (расширенный диапазон)
    avg_bmr = {
        'male': {
            15: 1600, 18: 1650, 20: 1680, 25: 1700, 30: 1750, 35: 1750, 40: 1750, 
            45: 1700, 50: 1650, 55: 1600, 60: 1550, 65: 1500, 70: 1450, 75: 1400, 80: 1350
        },
        'female': {
            15: 1300, 18: 1350, 20: 1350, 25: 1350, 30: 1350, 35: 1350, 40: 1350, 
            45: 1350, 50: 1300, 55: 1250, 60: 1200, 65: 1150, 70: 1100, 75: 1050, 80: 1000
        }
    }
    
    # Находим ближайший возраст
    gender_data = avg_bmr.get(gender, avg_bmr['male'])
    closest_age = chronological_age
    
    for age, avg_bmr_value in gender_data.items():
        if abs(bmr - avg_bmr_value) < abs(bmr - gender_data.get(closest_age, bmr)):
            closest_age = age
    
    return closest_age

def absi(waist_cm: float, bmi: float, height_cm: float) -> float:
    """Индекс формы тела (A Body Shape Index)"""
    if not waist_cm or not bmi or not height_cm:
        return None
    
    height_m = height_cm / 100
    waist_m = waist_cm / 100
    
    # ABSI формула
    absi_value = waist_m / (bmi ** (2/3) * (height_m ** 0.5))
    return round(absi_value, 3)

def interpret_absi(absi_value: float, age: int, gender: str) -> str:
    """Интерпретация риска ABSI"""
    if not absi_value:
        return "недостаточно данных"
    
    # Упрощенные пороги риска (зависят от возраста, пола и популяции)
    # Это приблизительные значения для демонстрации
    risk_thresholds = {
        'male': {20: 0.078, 30: 0.080, 40: 0.082, 50: 0.084, 60: 0.086},
        'female': {20: 0.077, 30: 0.079, 40: 0.081, 50: 0.083, 60: 0.085}
    }
    
    gender_thresholds = risk_thresholds.get(gender, risk_thresholds['male'])
    
    # Находим ближайший порог
    threshold = gender_thresholds.get(age, gender_thresholds.get(30, 0.080))
    
    if absi_value < threshold - 0.005:
        return "низкий"
    elif absi_value < threshold + 0.005:
        return "средний"
    else:
        return "высокий"

def segmental_muscle_mass(weight: float, body_fat_percent: float,
                          chest_cm: float = None, forearm_cm: float = None,
                          calf_cm: float = None, shoulder_width_cm: float = None,
                          hip_width_cm: float = None, gender: str = 'male') -> Dict:
    """
    Приблизительный расчёт мышечной массы по сегментам.
    Если есть обхваты, корректируем распределение.
    """
    fat_mass = weight * body_fat_percent / 100
    lean_mass = weight - fat_mass

    # Базовое распределение (усреднённое)
    base = {
        'arms': lean_mass * 0.12,
        'legs': lean_mass * 0.32,
        'trunk': lean_mass * 0.56
    }

    # Корректировка, если есть дополнительные обхваты
    if chest_cm and forearm_cm and calf_cm:
        # Пример: чем больше обхваты относительно средних, тем больше мышечной массы в соответствующем сегменте
        # Используем регрессионные коэффициенты (упрощённо)
        avg_forearm = 28 if gender == 'male' else 24
        avg_calf = 38 if gender == 'male' else 35
        avg_chest = 100 if gender == 'male' else 90

        arm_factor = forearm_cm / avg_forearm
        leg_factor = calf_cm / avg_calf
        trunk_factor = chest_cm / avg_chest

        total_factor = arm_factor + leg_factor + trunk_factor
        if total_factor > 0:
            # переназначаем пропорции
            base['arms'] = lean_mass * (arm_factor / total_factor)
            base['legs'] = lean_mass * (leg_factor / total_factor)
            base['trunk'] = lean_mass * (trunk_factor / total_factor)

    return {k: round(v, 1) for k, v in base.items()}
