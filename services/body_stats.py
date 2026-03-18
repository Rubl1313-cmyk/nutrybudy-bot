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
        return "Выраженный дефицит массы", "[RED]"
    elif bmi < 18.5:
        return "Недостаточная масса", "[YELLOW]"
    elif bmi < 25:
        return "Нормальный вес", "[GREEN]"
    elif bmi < 30:
        return "Избыточный вес", "[YELLOW]"
    elif bmi < 35:
        return "Ожирение I степени", "[RED]"
    elif bmi < 40:
        return "Ожирение II степени", "[RED]"
    else:
        return "Ожирение III степени", "[RED]"

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
    """Оценка % жира по формуле ВОИ (грубая)"""
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
            return "Низкий риск", "[GREEN]"
        elif waist_cm < 102:
            return "Повышенный риск", "[YELLOW]"
        else:
            return "Высокий риск", "[RED]"
    else:
        if waist_cm < 80:
            return "Низкий риск", "[GREEN]"
        elif waist_cm < 88:
            return "Повышенный риск", "[YELLOW]"
        else:
            return "Высокий риск", "[RED]"

def calculate_whtr(waist_cm: float, height_cm: float) -> float:
    """Waist-to-Height Ratio (отношение талии к росту)"""
    return round(waist_cm / height_cm, 2)

def interpret_whtr(whtr: float) -> Tuple[str, str]:
    """Интерпретация WHTR"""
    if whtr < 0.5:
        return "Здоровое соотношение", "[GREEN]"
    elif whtr < 0.6:
        return "Повышенное внимание", "[YELLOW]"
    else:
        return "Высокий риск", "[RED]"

def calculate_whr(waist_cm: float, hip_cm: float) -> float:
    """Waist-to-Hip Ratio (отношение талии к бедрам)"""
    return round(waist_cm / hip_cm, 2)

def interpret_whr(whr: float, gender: str) -> Tuple[str, str]:
    """Интерпретация WHR"""
    if gender == 'male':
        if whr < 0.9:
            return "Низкий риск", "[GREEN]"
        elif whr < 1.0:
            return "Умеренный риск", "[YELLOW]"
        else:
            return "Высокий риск", "[RED]"
    else:
        if whr < 0.8:
            return "Низкий риск", "[GREEN]"
        elif whr < 0.85:
            return "Умеренный риск", "[YELLOW]"
        else:
            return "Высокий риск", "[RED]"

def calculate_bmr_harris_benedict(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """BMR по формуле Харриса-Бенедикта (1919, пересмотренная 1984)"""
    if gender == 'male':
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    
    return round(bmr, 0)

def calculate_bmr_mifflin(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """BMR по формуле Миффлина-Сан Жеора (1990)"""
    if gender == 'male':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    return round(bmr, 0)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Расчет суточных калорий с учетом активности"""
    activity_multipliers = {
        'sedentary': 1.2,      # Сидячий образ жизни
        'light': 1.375,        # Легкая активность (1-3 дня в неделю)
        'moderate': 1.55,      # Умеренная активность (3-5 дней в неделю)
        'active': 1.725,       # Высокая активность (6-7 дней в неделю)
        'very_active': 1.9     # Очень высокая активность
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    return round(bmr * multiplier, 0)

def calculate_body_density(height_cm: float, neck_cm: float, waist_cm: float, 
                         hip_cm: Optional[float], gender: str) -> Optional[float]:
    """Расчет плотности тела по методу Джексона-Поллока"""
    try:
        if gender == 'male':
            # Формула для мужчин (3 складки)
            # Здесь нужны складки: грудь, живот, бедро
            # Упрощенная версия с талией и шеей
            if neck_cm >= waist_cm:
                return None
            density = 1.112 - (0.00043499 * (waist_cm - neck_cm)) + (0.00000055 * (waist_cm - neck_cm) ** 2) - (0.00028826 * height_cm)
        else:
            # Формула для женщин (3 складки)
            # Здесь нужны складки: трицепс, надподвздошная, бедро
            # Упрощенная версия
            if not hip_cm or neck_cm >= (waist_cm + hip_cm):
                return None
            density = 1.097 - (0.00046971 * (waist_cm + hip_cm - neck_cm)) + (0.00000056 * (waist_cm + hip_cm - neck_cm) ** 2) - (0.00012828 * height_cm)
        
        return round(density, 4)
    except (ValueError, ZeroDivisionError):
        return None

def body_fat_siri_formula(body_density: float) -> Optional[float]:
    """Расчет % жира по формуле Siri (1961)"""
    if not body_density or body_density <= 0:
        return None
    
    try:
        bf_percent = (4.95 / body_density - 4.5) * 100
        return round(max(0, min(100, bf_percent)), 1)
    except (ValueError, ZeroDivisionError):
        return None

def calculate_ffmi(weight_kg: float, body_fat_percent: float, height_cm: float) -> float:
    """Fat-Free Mass Index (индекс безжировой массы)"""
    lean_mass = weight_kg * (1 - body_fat_percent / 100)
    height_m = height_cm / 100
    ffmi = lean_mass / (height_m ** 2)
    return round(ffmi, 2)

def interpret_ffmi(ffmi: float, gender: str) -> Tuple[str, str]:
    """Интерпретация FFMI"""
    if gender == 'male':
        if ffmi < 16:
            return "Низкая мышечная масса", "[YELLOW]"
        elif ffmi < 20:
            return "Средняя мышечная масса", "[GREEN]"
        elif ffmi < 25:
            return "Высокая мышечная масса", "[GREEN]"
        else:
            return "Очень высокая мышечная масса", "[BLUE]"
    else:
        if ffmi < 14:
            return "Низкая мышечная масса", "[YELLOW]"
        elif ffmi < 17:
            return "Средняя мышечная масса", "[GREEN]"
        elif ffmi < 20:
            return "Высокая мышечная масса", "[GREEN]"
        else:
            return "Очень высокая мышечная масса", "[BLUE]"

def calculate_metabolic_age(bmi: float, body_fat_percent: float, chronological_age: int) -> int:
    """Расчет метаболического возраста"""
    # Упрощенная формула на основе ИМТ и % жира
    age_factor = 0
    
    # Корректировка на основе ИМТ
    if bmi < 18.5:
        age_factor += -2
    elif 18.5 <= bmi < 25:
        age_factor += 0
    elif 25 <= bmi < 30:
        age_factor += 3
    else:
        age_factor += 7
    
    # Корректировка на основе % жира
    if body_fat_percent < 15:
        age_factor += -3
    elif 15 <= body_fat_percent < 20:
        age_factor += 0
    elif 20 <= body_fat_percent < 25:
        age_factor += 2
    elif 25 <= body_fat_percent < 30:
        age_factor += 5
    else:
        age_factor += 8
    
    metabolic_age = chronological_age + age_factor
    return max(18, min(100, metabolic_age))

def calculate_protein_needs(weight_kg: float, activity_level: str, goal: str = 'maintain') -> float:
    """Расчет потребности в белке"""
    base_protein = {
        'sedentary': 0.8,
        'light': 1.0,
        'moderate': 1.2,
        'active': 1.4,
        'very_active': 1.6
    }
    
    protein_per_kg = base_protein.get(activity_level, 1.2)
    
    # Корректировка под цель
    if goal == 'muscle_gain':
        protein_per_kg += 0.3
    elif goal == 'fat_loss':
        protein_per_kg += 0.2
    
    return round(weight_kg * protein_per_kg, 1)

def calculate_water_needs(weight_kg: float, activity_level: str, climate: str = 'moderate') -> float:
    """Расчет потребности в воде"""
    base_water = weight_kg * 0.03  # 30 мл на кг
    
    # Корректировка на активность
    activity_adjustment = {
        'sedentary': 0,
        'light': 0.5,
        'moderate': 1.0,
        'active': 1.5,
        'very_active': 2.0
    }
    
    # Корректировка на климат
    climate_adjustment = {
        'cold': -0.5,
        'moderate': 0,
        'hot': 1.0,
        'very_hot': 1.5
    }
    
    total_water = base_water + activity_adjustment.get(activity_level, 0) + climate_adjustment.get(climate, 0)
    return round(max(1.5, total_water), 1)  # Минимум 1.5 литра

def calculate_ideal_body_measurements(height_cm: float, gender: str, wrist_cm: Optional[float] = None) -> Dict[str, float]:
    """Расчет идеальных обхватов тела"""
    # Упрощенные формулы на основе роста
    height_m = height_cm / 100
    
    if gender == 'male':
        # Идеальные обхватов для мужчин
        chest = height_cm * 0.55
        waist = height_cm * 0.45
        hips = chest * 0.85
        biceps = chest * 0.36
        thighs = hips * 0.6
        neck = chest * 0.37
    else:
        # Идеальные обхватов для женщин
        chest = height_cm * 0.52
        waist = height_cm * 0.38
        hips = chest * 1.1
        biceps = chest * 0.33
        thighs = hips * 0.65
        neck = chest * 0.35
    
    # Корректировка на основе запястья (если доступно)
    if wrist_cm and gender == 'male':
        # Формула для мужчин на основе запястья
        frame_factor = wrist_cm / height_cm
        if frame_factor < 0.095:  # Тонкий костяк
            multiplier = 0.95
        elif frame_factor > 0.105:  # Широкий костяк
            multiplier = 1.05
        else:  # Средний костяк
            multiplier = 1.0
        
        for key in measurements:
            measurements[key] *= multiplier
    
    measurements = {
        'chest': round(chest, 1),
        'waist': round(waist, 1),
        'hips': round(hips, 1),
        'biceps': round(biceps, 1),
        'thighs': round(thighs, 1),
        'neck': round(neck, 1)
    }
    
    return measurements

def calculate_body_shape_score(measurements: Dict[str, float], gender: str) -> float:
    """Расчет оценки телосложения (0-100)"""
    try:
        if gender == 'male':
            # Оценка для мужчин (V-форма идеальна)
            waist_to_chest = measurements['waist'] / measurements['chest']
            chest_to_hips = measurements['chest'] / measurements['hips']
            
            # Идеальные соотношения
            ideal_waist_chest = 0.7
            ideal_chest_hips = 1.18
            
            score = 100 - (abs(waist_to_chest - ideal_waist_chest) * 100) - (abs(chest_to_hips - ideal_chest_hips) * 50)
        else:
            # Оценка для женщин (песочные часы идеальны)
            waist_to_chest = measurements['waist'] / measurements['chest']
            waist_to_hips = measurements['waist'] / measurements['hips']
            
            # Идеальные соотношения
            ideal_waist_chest = 0.75
            ideal_waist_hips = 0.7
            
            score = 100 - (abs(waist_to_chest - ideal_waist_chest) * 100) - (abs(waist_to_hips - ideal_waist_hips) * 100)
        
        return round(max(0, min(100, score)), 1)
    except:
        return 50.0  # Средняя оценка по умолчанию

def generate_health_summary(user_data: Dict) -> Dict[str, Any]:
    """Генерирует сводку здоровья на всех метрик"""
    try:
        weight = user_data.get('weight', 0)
        height = user_data.get('height', 0)
        age = user_data.get('age', 0)
        gender = user_data.get('gender', 'male')
        
        # Базовые расчеты
        bmi = calculate_bmi(weight, height)
        bmi_status, bmi_color = interpret_bmi(bmi)
        
        # Идеальный вес
        ideal_weights = calculate_ideal_weight(height, gender)
        
        # BMR и TDEE
        bmr = calculate_bmr_mifflin(weight, height, age, gender)
        activity_level = user_data.get('activity_level', 'moderate')
        tdee = calculate_tdee(bmr, activity_level)
        
        # Оценка % жира
        body_fat = estimate_body_fat_bmi(bmi, age, gender)
        
        # Вода в организме
        body_water = total_body_water_watson(weight, height, age, gender)
        
        # Мышечная масса
        muscle_mass = estimate_muscle_mass(weight, body_fat)
        
        # Метаболический возраст
        metabolic_age = calculate_metabolic_age(bmi, body_fat, age)
        
        # Потребности в питании
        protein_needs = calculate_protein_needs(weight, activity_level)
        water_needs = calculate_water_needs(weight, activity_level)
        
        # Риски по обхватам (если доступны)
        waist_cm = user_data.get('waist_cm')
        hip_cm = user_data.get('hip_cm')
        
        visceral_risk = None
        whtr = None
        whr = None
        
        if waist_cm:
            visceral_risk, visceral_color = visceral_fat_risk(waist_cm, gender)
            whtr = calculate_whtr(waist_cm, height)
            whtr_status, whtr_color = interpret_whtr(whtr)
            
            if hip_cm:
                whr = calculate_whr(waist_cm, hip_cm)
                whr_status, whr_color = interpret_whr(whr, gender)
        
        return {
            'bmi': {
                'value': bmi,
                'status': bmi_status,
                'color': bmi_color
            },
            'ideal_weight': ideal_weights,
            'metabolism': {
                'bmr': bmr,
                'tdee': tdee,
                'metabolic_age': metabolic_age
            },
            'body_composition': {
                'body_fat_percent': body_fat,
                'muscle_mass_kg': muscle_mass,
                'body_water_liters': body_water
            },
            'nutrition_needs': {
                'protein_grams': protein_needs,
                'water_liters': water_needs
            },
            'health_risks': {
                'visceral_fat': visceral_risk,
                'whtr': whtr,
                'whr': whr
            },
            'overall_score': calculate_overall_health_score(bmi, body_fat, metabolic_age, visceral_risk)
        }
        
    except Exception as e:
        logger.error(f"Error generating health summary: {e}")
        return {}

def calculate_overall_health_score(bmi: float, body_fat: float, metabolic_age: int, visceral_risk: Optional[str]) -> float:
    """Расчет общей оценки здоровья (0-100)"""
    try:
        score = 100
        
        # Штраф за ИМТ
        if bmi < 18.5:
            score -= 20
        elif 18.5 <= bmi < 25:
            pass  # Идеально
        elif 25 <= bmi < 30:
            score -= 10
        else:
            score -= 30
        
        # Штраф за % жира
        if body_fat < 10:
            score -= 15
        elif 10 <= body_fat < 20:
            pass  # Идеально для мужчин
        elif 20 <= body_fat < 25:
            score -= 5
        elif 25 <= body_fat < 30:
            score -= 15
        else:
            score -= 25
        
        # Штраф за метаболический возраст
        # (предполагаем хронологический возраст 30 для расчета)
        age_diff = metabolic_age - 30
        if age_diff > 0:
            score -= min(age_diff * 2, 20)
        
        # Штраф за риск висцерального жира
        if visceral_risk:
            if visceral_risk == "Высокий риск":
                score -= 15
            elif visceral_risk == "Повышенный риск":
                score -= 5
        
        return round(max(0, min(100, score)), 1)
    except:
        return 50.0
