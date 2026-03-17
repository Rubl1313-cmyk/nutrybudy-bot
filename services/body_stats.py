"""
services/body_stats.py
Ğ Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ñ‹ ĞºĞ¾Ğ¼Ğ¿Ğ¾Ğ·Ğ¸Ñ†Ğ¸Ğ¸ Ñ‚ĞµĞ»Ğ° Ğ¸ Ğ°Ğ½Ğ°Ğ»Ğ¸Ñ‚Ğ¸ĞºĞ¸ Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²ÑŒÑ�
"""
import math
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Ğ˜Ğ¼Ğ¿Ğ¾Ñ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ BMR ĞºĞ°Ğ»ÑŒĞºÑƒĞ»Ñ�Ñ‚Ğ¾Ñ€
from services.calculator import calculate_bmr

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Ğ˜Ğ½Ğ´ĞµĞºÑ� Ğ¼Ğ°Ñ�Ñ�Ñ‹ Ñ‚ĞµĞ»Ğ° Ñ� Ñ‚Ğ¾Ñ‡Ğ½Ğ¾Ñ�Ñ‚ÑŒÑ� Ğ´Ğ¾ 1 Ğ·Ğ½Ğ°ĞºĞ°"""
    return round(weight_kg / ((height_cm / 100) ** 2), 1)

def interpret_bmi(bmi: float) -> Tuple[str, str]:
    """Ğ˜Ğ½Ñ‚ĞµÑ€Ğ¿Ñ€ĞµÑ‚Ğ°Ñ†Ğ¸Ñ� Ğ˜ĞœĞ¢ Ñ� Ñ†Ğ²ĞµÑ‚Ğ¾Ğ²Ğ¾Ğ¹ Ğ¸Ğ½Ğ´Ğ¸ĞºĞ°Ñ†Ğ¸ĞµĞ¹"""
    if bmi < 16.5:
        return "Ğ’Ñ‹Ñ€Ğ°Ğ¶ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ´ĞµÑ„Ğ¸Ñ†Ğ¸Ñ‚ Ğ¼Ğ°Ñ�Ñ�Ñ‹", "ğŸ”´"
    elif bmi < 18.5:
        return "Ğ�ĞµĞ´Ğ¾Ñ�Ñ‚Ğ°Ñ‚Ğ¾Ñ‡Ğ½Ğ°Ñ� Ğ¼Ğ°Ñ�Ñ�Ğ°", "ğŸŸ¡"
    elif bmi < 25:
        return "Ğ�Ğ¾Ñ€Ğ¼Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ²ĞµÑ�", "ğŸŸ¢"
    elif bmi < 30:
        return "Ğ˜Ğ·Ğ±Ñ‹Ñ‚Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ğ²ĞµÑ�", "ğŸŸ¡"
    elif bmi < 35:
        return "Ğ�Ğ¶Ğ¸Ñ€ĞµĞ½Ğ¸Ğµ I Ñ�Ñ‚ĞµĞ¿ĞµĞ½Ğ¸", "ğŸ”´"
    elif bmi < 40:
        return "Ğ�Ğ¶Ğ¸Ñ€ĞµĞ½Ğ¸Ğµ II Ñ�Ñ‚ĞµĞ¿ĞµĞ½Ğ¸", "ğŸ”´"
    else:
        return "Ğ�Ğ¶Ğ¸Ñ€ĞµĞ½Ğ¸Ğµ III Ñ�Ñ‚ĞµĞ¿ĞµĞ½Ğ¸", "ğŸ”´"

def calculate_ideal_weight(height_cm: float, gender: str) -> Dict[str, float]:
    """Ğ˜Ğ´ĞµĞ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ²ĞµÑ� Ğ¿Ğ¾ 4 Ñ„Ğ¾Ñ€Ğ¼ÑƒĞ»Ğ°Ğ¼"""
    h = height_cm
    
    # Ğ¤Ğ¾Ñ€Ğ¼ÑƒĞ»Ğ° Ğ‘Ñ€Ğ¾ĞºĞ° (ÑƒĞ»ÑƒÑ‡ÑˆĞµĞ½Ğ½Ğ°Ñ�)
    if gender == 'male':
        broca = (h - 100) * 0.9
    else:
        broca = (h - 100) * 0.85
    
    # Ğ¤Ğ¾Ñ€Ğ¼ÑƒĞ»Ğ° Ğ›Ğ¾Ñ€ĞµĞ½Ñ†Ğ°
    if gender == 'male':
        lorentz = h - 100 - (h - 150) / 4
    else:
        lorentz = h - 100 - (h - 150) / 2
    
    # Ğ¤Ğ¾Ñ€Ğ¼ÑƒĞ»Ğ° Ğ”ĞµĞ²Ğ¸Ğ½Ğ°
    if gender == 'male':
        devine = 50 + 0.91 * (h - 152.4)
    else:
        devine = 45.5 + 0.91 * (h - 152.4)
    
    # Ğ—Ğ´Ğ¾Ñ€Ğ¾Ğ²Ñ‹Ğ¹ Ğ´Ğ¸Ğ°Ğ¿Ğ°Ğ·Ğ¾Ğ½ Ğ¿Ğ¾ Ğ˜ĞœĞ¢ (18.5-24.9)
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
    """Ğ�Ñ†ĞµĞ½ĞºĞ° % Ğ¶Ğ¸Ñ€Ğ° Ğ¿Ğ¾ Ñ„Ğ¾Ñ€Ğ¼ÑƒĞ»Ğµ Ğ’ĞœI (Ğ³Ñ€ÑƒĞ±Ğ°Ñ�)"""
    if gender == 'male':
        return round(1.20 * bmi + 0.23 * age - 16.2, 1)
    else:
        return round(1.20 * bmi + 0.23 * age - 5.4, 1)

def estimate_body_fat_navy(height_cm: float, neck_cm: float, waist_cm: float, 
                          hip_cm: Optional[float] = None, gender: str = 'male') -> Optional[float]:
    """
    ĞœĞµÑ‚Ğ¾Ğ´ Ğ’ĞœĞ¡ Ğ¡Ğ¨Ğ� (Navy) - Ğ·Ğ¾Ğ»Ğ¾Ñ‚Ğ¾Ğ¹ Ñ�Ñ‚Ğ°Ğ½Ğ´Ğ°Ñ€Ñ‚ Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ğ¸
    Ğ¢Ğ¾Ñ‡Ğ½Ğ¾Ñ�Ñ‚ÑŒ: Â±3% Ğ´Ğ»Ñ� Ğ±Ğ¾Ğ»ÑŒÑˆĞ¸Ğ½Ñ�Ñ‚Ğ²Ğ° Ğ»Ñ�Ğ´ĞµĞ¹
    """
    try:
        if gender == 'male':
            # Ğ”Ğ»Ñ� Ğ¼ÑƒĞ¶Ñ‡Ğ¸Ğ½ Ğ½Ğµ Ğ½ÑƒĞ¶ĞµĞ½ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€
            if neck_cm >= waist_cm:
                return None
            log_val = math.log10(waist_cm - neck_cm)
            bf_percent = 495 / (1.0324 - 0.19077 * log_val + 0.15456 * math.log10(height_cm)) - 450
        else:
            # Ğ”Ğ»Ñ� Ğ¶ĞµĞ½Ñ‰Ğ¸Ğ½ Ğ½ÑƒĞ¶ĞµĞ½ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€
            if not hip_cm or neck_cm >= (waist_cm + hip_cm):
                return None
            log_val = math.log10(waist_cm + hip_cm - neck_cm)
            bf_percent = 495 / (1.29579 - 0.35004 * log_val + 0.22100 * math.log10(height_cm)) - 450
        
        return round(max(0, min(100, bf_percent)), 1)  # Ğ�Ğ³Ñ€Ğ°Ğ½Ğ¸Ñ‡Ğ¸Ğ²Ğ°ĞµĞ¼ 0-100%
    except (ValueError, ZeroDivisionError):
        return None

def total_body_water_watson(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Ğ�Ğ±Ñ‰Ğ°Ñ� Ğ²Ğ¾Ğ´Ğ° Ğ¾Ñ€Ğ³Ğ°Ğ½Ğ¸Ğ·Ğ¼Ğ° Ğ¿Ğ¾ Ñ„Ğ¾Ñ€Ğ¼ÑƒĞ»Ğµ Watson (1979)"""
    if gender == 'male':
        tbw = 2.447 - 0.09516 * age + 0.1074 * height_cm + 0.3362 * weight_kg
    else:
        tbw = -2.097 + 0.1069 * height_cm + 0.2466 * weight_kg
    
    return round(max(0, tbw), 1)

def estimate_muscle_mass(weight_kg: float, body_fat_percent: float) -> float:
    """ĞŸÑ€Ğ¸Ğ±Ğ»Ğ¸Ğ·Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ°Ñ� Ñ�ĞºĞµĞ»ĞµÑ‚Ğ½Ğ¾-Ğ¼Ñ‹ÑˆĞµÑ‡Ğ½Ğ°Ñ� Ğ¼Ğ°Ñ�Ñ�Ğ°"""
    fat_mass = weight_kg * (body_fat_percent / 100)
    muscle_mass = weight_kg - fat_mass
    # Ğ¡ĞºĞµĞ»ĞµÑ‚Ğ½Ğ°Ñ� Ğ¼Ğ°Ñ�Ñ�Ğ° Ğ¾Ğ±Ñ‹Ñ‡Ğ½Ğ¾ ~40% Ğ¾Ñ‚ Ğ±ĞµĞ·Ğ¶Ğ¸Ñ€Ğ¾Ğ²Ğ¾Ğ¹ Ğ¼Ğ°Ñ�Ñ�Ñ‹
    skeletal_muscle = muscle_mass * 0.4
    return round(skeletal_muscle, 1)

def visceral_fat_risk(waist_cm: float, gender: str) -> Tuple[str, str]:
    """Ğ�Ñ†ĞµĞ½ĞºĞ° Ñ€Ğ¸Ñ�ĞºĞ° Ğ²Ğ¸Ñ�Ñ†ĞµÑ€Ğ°Ğ»ÑŒĞ½Ğ¾Ğ³Ğ¾ Ğ¶Ğ¸Ñ€Ğ° Ğ¿Ğ¾ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ñƒ Ñ‚Ğ°Ğ»Ğ¸Ğ¸"""
    if gender == 'male':
        if waist_cm < 94:
            return "Ğ�Ğ¸Ğ·ĞºĞ¸Ğ¹ Ñ€Ğ¸Ñ�Ğº", "ğŸŸ¢"
        elif waist_cm < 102:
            return "ĞŸĞ¾Ğ²Ñ‹ÑˆĞµĞ½Ğ½Ñ‹Ğ¹ Ñ€Ğ¸Ñ�Ğº", "ğŸŸ¡"
        else:
            return "Ğ’Ñ‹Ñ�Ğ¾ĞºĞ¸Ğ¹ Ñ€Ğ¸Ñ�Ğº", "ğŸ”´"
    else:
        if waist_cm < 80:
            return "Ğ�Ğ¸Ğ·ĞºĞ¸Ğ¹ Ñ€Ğ¸Ñ�Ğº", "ğŸŸ¢"
        elif waist_cm < 88:
            return "ĞŸĞ¾Ğ²Ñ‹ÑˆĞµĞ½Ğ½Ñ‹Ğ¹ Ñ€Ğ¸Ñ�Ğº", "ğŸŸ¡"
        else:
            return "Ğ’Ñ‹Ñ�Ğ¾ĞºĞ¸Ğ¹ Ñ€Ğ¸Ñ�Ğº", "ğŸ”´"

def calculate_body_type(height_cm: float, wrist_cm: float, gender: str) -> str:
    """Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½Ğ¸Ğµ Ñ‚Ğ¸Ğ¿Ğ° Ñ‚ĞµĞ»Ğ¾Ñ�Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ñ� Ğ¿Ğ¾ Ğ¸Ğ½Ğ´ĞµĞºÑ�Ñƒ ĞŸĞ¸Ğ½ÑŒĞµ"""
    if not wrist_cm:
        return "Ğ�Ğµ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½"
    
    pignet_index = height_cm - (wrist_cm * 100 / height_cm)
    
    if gender == 'male':
        if pignet_index < 40:
            return "Ğ­ĞºÑ‚Ğ¾Ğ¼Ğ¾Ñ€Ñ„ (Ñ…Ñ€ÑƒĞ¿ĞºĞ¾Ğµ Ñ‚ĞµĞ»Ğ¾Ñ�Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ğµ)"
        elif pignet_index < 50:
            return "ĞœĞµĞ·Ğ¾Ğ¼Ğ¾Ñ€Ñ„ (Ğ½Ğ¾Ñ€Ğ¼Ğ°Ğ»ÑŒĞ½Ğ¾Ğµ Ñ‚ĞµĞ»Ğ¾Ñ�Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ğµ)"
        else:
            return "Ğ­Ğ½Ğ´Ğ¾Ğ¼Ğ¾Ñ€Ñ„ (Ğ¿Ğ»Ğ¾Ñ‚Ğ½Ğ¾Ğµ Ñ‚ĞµĞ»Ğ¾Ñ�Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ğµ)"
    else:
        if pignet_index < 35:
            return "Ğ­ĞºÑ‚Ğ¾Ğ¼Ğ¾Ñ€Ñ„ (Ñ…Ñ€ÑƒĞ¿ĞºĞ¾Ğµ Ñ‚ĞµĞ»Ğ¾Ñ�Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ğµ)"
        elif pignet_index < 45:
            return "ĞœĞµĞ·Ğ¾Ğ¼Ğ¾Ñ€Ñ„ (Ğ½Ğ¾Ñ€Ğ¼Ğ°Ğ»ÑŒĞ½Ğ¾Ğµ Ñ‚ĞµĞ»Ğ¾Ñ�Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ğµ)"
        else:
            return "Ğ­Ğ½Ğ´Ğ¾Ğ¼Ğ¾Ñ€Ñ„ (Ğ¿Ğ»Ğ¾Ñ‚Ğ½Ğ¾Ğµ Ñ‚ĞµĞ»Ğ¾Ñ�Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ğµ)"

def get_body_composition_analysis(weight: float, height: float, age: int, gender: str,
                                neck_cm: Optional[float] = None, waist_cm: Optional[float] = None,
                                hip_cm: Optional[float] = None, wrist_cm: Optional[float] = None,
                                chest_cm: Optional[float] = None, forearm_cm: Optional[float] = None,
                                calf_cm: Optional[float] = None, shoulder_width_cm: Optional[float] = None,
                                hip_width_cm: Optional[float] = None) -> Dict:
    """ĞŸĞ¾Ğ»Ğ½Ñ‹Ğ¹ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ· ĞºĞ¾Ğ¼Ğ¿Ğ¾Ğ·Ğ¸Ñ†Ğ¸Ğ¸ Ñ‚ĞµĞ»Ğ°"""
    
    # Ğ‘Ğ°Ğ·Ğ¾Ğ²Ñ‹Ğµ Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ñ‹
    bmi = calculate_bmi(weight, height)
    bmi_status, bmi_color = interpret_bmi(bmi)
    ideal_weights = calculate_ideal_weight(height, gender)
    
    # ĞŸÑ€Ğ¾Ñ†ĞµĞ½Ñ‚ Ğ¶Ğ¸Ñ€Ğ°
    body_fat_bmi = estimate_body_fat_bmi(bmi, age, gender)
    body_fat_navy = None
    if neck_cm and waist_cm:
        body_fat_navy = estimate_body_fat_navy(height, neck_cm, waist_cm, hip_cm, gender)
    
    body_fat = body_fat_navy if body_fat_navy else body_fat_bmi
    
    # Ğ�Ğ¾Ğ²Ñ‹Ğµ Ğ¼ĞµÑ‚Ñ€Ğ¸ĞºĞ¸
    whtr = waist_to_height_ratio(waist_cm, height) if waist_cm else None
    
    bmr = calculate_bmr(weight, height, age, gender)
    meta_age = metabolic_age(bmr, age, gender, weight, height)
    
    absi_value = absi(waist_cm, bmi, height) if waist_cm and bmi else None
    absi_risk = interpret_absi(absi_value, age, gender) if absi_value else None
    
    # Ğ¡Ğ¾Ñ�Ñ‚Ğ°Ğ² Ñ‚ĞµĞ»Ğ°
    body_water = total_body_water_watson(weight, height, age, gender)
    muscle_mass = estimate_muscle_mass(weight, body_fat)
    
    # Ğ¡ĞµĞ³Ğ¼ĞµĞ½Ñ‚Ğ°Ñ€Ğ½Ğ°Ñ� Ğ¼Ñ‹ÑˆĞµÑ‡Ğ½Ğ°Ñ� Ğ¼Ğ°Ñ�Ñ�Ğ°
    muscle_segments = segmental_muscle_mass(
        weight, body_fat,
        chest_cm, forearm_cm, calf_cm,
        shoulder_width_cm, hip_width_cm, gender
    )
    
    # Ğ Ğ¸Ñ�ĞºĞ¸
    visceral_risk = None
    visceral_risk_color = None
    if waist_cm:
        visceral_risk, visceral_risk_color = visceral_fat_risk(waist_cm, gender)
    
    # Ğ¢Ğ¸Ğ¿ Ñ‚ĞµĞ»Ğ¾Ñ�Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ñ�
    body_type = calculate_body_type(height, wrist_cm, gender) if wrist_cm else "Ğ�Ğµ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½"
    
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
        # Ğ�Ğ¾Ğ²Ñ‹Ğµ Ğ¼ĞµÑ‚Ñ€Ğ¸ĞºĞ¸
        'whtr': whtr,
        'metabolic_age': meta_age,
        'absi': absi_value,
        'absi_risk': absi_risk,
        'muscle_segments': muscle_segments,
    }

def get_weight_change_trend(current_weight: float, previous_weights: list) -> Dict:
    """Ğ�Ğ½Ğ°Ğ»Ğ¸Ğ· Ñ‚Ñ€ĞµĞ½Ğ´Ğ° Ğ²ĞµÑ�Ğ°"""
    if not previous_weights or len(previous_weights) < 2:
        return {'trend': 'stable', 'change': 0, 'period': 'Ğ½ĞµĞ´Ğ¾Ñ�Ñ‚Ğ°Ñ‚Ğ¾Ñ‡Ğ½Ğ¾ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…'}
    
    # Ğ‘ĞµÑ€ĞµĞ¼ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ 7 Ğ¸Ğ·Ğ¼ĞµÑ€ĞµĞ½Ğ¸Ğ¹
    recent_weights = previous_weights[-7:] if len(previous_weights) >= 7 else previous_weights
    oldest_weight = recent_weights[0]
    
    change = current_weight - oldest_weight
    period = len(recent_weights) - 1
    
    if abs(change) < 0.5:
        trend = 'stable'
        trend_emoji = 'â�¡ï¸�'
    elif change > 0:
        trend = 'gaining'
        trend_emoji = 'ğŸ“ˆ'
    else:
        trend = 'losing'
        trend_emoji = 'ğŸ“‰'
    
    return {
        'trend': trend,
        'trend_emoji': trend_emoji,
        'change': round(change, 1),
        'period': period,
        'rate': round(change / period, 2) if period > 0 else 0
    }

def waist_to_height_ratio(waist_cm: float, height_cm: float) -> float:
    """Ğ�Ñ‚Ğ½Ğ¾ÑˆĞµĞ½Ğ¸Ğµ Ñ‚Ğ°Ğ»Ğ¸Ğ¸ Ğº Ñ€Ğ¾Ñ�Ñ‚Ñƒ (WHtR)"""
    if not waist_cm or not height_cm:
        return None
    return round(waist_cm / height_cm, 3)

def metabolic_age(bmr: float, chronological_age: int, gender: str, weight_kg: float, height_cm: float) -> int:
    """Ğ Ğ°Ñ�Ñ‡ĞµÑ‚ Ğ¼ĞµÑ‚Ğ°Ğ±Ğ¾Ğ»Ğ¸Ñ‡ĞµÑ�ĞºĞ¾Ğ³Ğ¾ Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚Ğ°"""
    if not bmr:
        return chronological_age
    
    # Ğ¡Ñ€ĞµĞ´Ğ½Ğ¸Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ� BMR Ğ¿Ğ¾ Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚Ñƒ Ğ¸ Ğ¿Ğ¾Ğ»Ñƒ (Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ´Ğ¸Ğ°Ğ¿Ğ°Ğ·Ğ¾Ğ½)
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
    
    # Ğ�Ğ°Ñ…Ğ¾Ğ´Ğ¸Ğ¼ Ğ±Ğ»Ğ¸Ğ¶Ğ°Ğ¹ÑˆĞ¸Ğ¹ Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚
    gender_data = avg_bmr.get(gender, avg_bmr['male'])
    closest_age = chronological_age
    
    for age, avg_bmr_value in gender_data.items():
        if abs(bmr - avg_bmr_value) < abs(bmr - gender_data.get(closest_age, bmr)):
            closest_age = age
    
    return closest_age

def absi(waist_cm: float, bmi: float, height_cm: float) -> float:
    """Ğ˜Ğ½Ğ´ĞµĞºÑ� Ñ„Ğ¾Ñ€Ğ¼Ñ‹ Ñ‚ĞµĞ»Ğ° (A Body Shape Index)"""
    if not waist_cm or not bmi or not height_cm:
        return None
    
    height_m = height_cm / 100
    waist_m = waist_cm / 100
    
    # ABSI Ñ„Ğ¾Ñ€Ğ¼ÑƒĞ»Ğ°
    absi_value = waist_m / (bmi ** (2/3) * (height_m ** 0.5))
    return round(absi_value, 3)

def interpret_absi(absi_value: float, age: int, gender: str) -> str:
    """Ğ˜Ğ½Ñ‚ĞµÑ€Ğ¿Ñ€ĞµÑ‚Ğ°Ñ†Ğ¸Ñ� Ñ€Ğ¸Ñ�ĞºĞ° ABSI"""
    if not absi_value:
        return "Ğ½ĞµĞ´Ğ¾Ñ�Ñ‚Ğ°Ñ‚Ğ¾Ñ‡Ğ½Ğ¾ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…"
    
    # Ğ£Ğ¿Ñ€Ğ¾Ñ‰ĞµĞ½Ğ½Ñ‹Ğµ Ğ¿Ğ¾Ñ€Ğ¾Ğ³Ğ¸ Ñ€Ğ¸Ñ�ĞºĞ° (Ğ·Ğ°Ğ²Ğ¸Ñ�Ñ�Ñ‚ Ğ¾Ñ‚ Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚Ğ°, Ğ¿Ğ¾Ğ»Ğ° Ğ¸ Ğ¿Ğ¾Ğ¿ÑƒĞ»Ñ�Ñ†Ğ¸Ğ¸)
    # Ğ­Ñ‚Ğ¾ Ğ¿Ñ€Ğ¸Ğ±Ğ»Ğ¸Ğ·Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ´ĞµĞ¼Ğ¾Ğ½Ñ�Ñ‚Ñ€Ğ°Ñ†Ğ¸Ğ¸
    risk_thresholds = {
        'male': {20: 0.078, 30: 0.080, 40: 0.082, 50: 0.084, 60: 0.086},
        'female': {20: 0.077, 30: 0.079, 40: 0.081, 50: 0.083, 60: 0.085}
    }
    
    gender_thresholds = risk_thresholds.get(gender, risk_thresholds['male'])
    
    # Ğ�Ğ°Ñ…Ğ¾Ğ´Ğ¸Ğ¼ Ğ±Ğ»Ğ¸Ğ¶Ğ°Ğ¹ÑˆĞ¸Ğ¹ Ğ¿Ğ¾Ñ€Ğ¾Ğ³
    threshold = gender_thresholds.get(age, gender_thresholds.get(30, 0.080))
    
    if absi_value < threshold - 0.005:
        return "Ğ½Ğ¸Ğ·ĞºĞ¸Ğ¹"
    elif absi_value < threshold + 0.005:
        return "Ñ�Ñ€ĞµĞ´Ğ½Ğ¸Ğ¹"
    else:
        return "Ğ²Ñ‹Ñ�Ğ¾ĞºĞ¸Ğ¹"

def segmental_muscle_mass(weight: float, body_fat_percent: float,
                          chest_cm: float = None, forearm_cm: float = None,
                          calf_cm: float = None, shoulder_width_cm: float = None,
                          hip_width_cm: float = None, gender: str = 'male') -> Dict:
    """
    ĞŸÑ€Ğ¸Ğ±Ğ»Ğ¸Ğ·Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğ¹ Ñ€Ğ°Ñ�Ñ‡Ñ‘Ñ‚ Ğ¼Ñ‹ÑˆĞµÑ‡Ğ½Ğ¾Ğ¹ Ğ¼Ğ°Ñ�Ñ�Ñ‹ Ğ¿Ğ¾ Ñ�ĞµĞ³Ğ¼ĞµĞ½Ñ‚Ğ°Ğ¼.
    Ğ•Ñ�Ğ»Ğ¸ ĞµÑ�Ñ‚ÑŒ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ñ‹, ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ñ€Ğ°Ñ�Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½Ğ¸Ğµ.
    """
    fat_mass = weight * body_fat_percent / 100
    lean_mass = weight - fat_mass

    # Ğ‘Ğ°Ğ·Ğ¾Ğ²Ğ¾Ğµ Ñ€Ğ°Ñ�Ğ¿Ñ€ĞµĞ´ĞµĞ»ĞµĞ½Ğ¸Ğµ (ÑƒÑ�Ñ€ĞµĞ´Ğ½Ñ‘Ğ½Ğ½Ğ¾Ğµ)
    base = {
        'arms': lean_mass * 0.12,
        'legs': lean_mass * 0.32,
        'trunk': lean_mass * 0.56
    }

    # ĞšĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°, ĞµÑ�Ğ»Ğ¸ ĞµÑ�Ñ‚ÑŒ Ğ´Ğ¾Ğ¿Ğ¾Ğ»Ğ½Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğµ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ñ‹
    if chest_cm and forearm_cm and calf_cm:
        # ĞŸÑ€Ğ¸Ğ¼ĞµÑ€: Ñ‡ĞµĞ¼ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ Ğ¾Ğ±Ñ…Ğ²Ğ°Ñ‚Ñ‹ Ğ¾Ñ‚Ğ½Ğ¾Ñ�Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾ Ñ�Ñ€ĞµĞ´Ğ½Ğ¸Ñ…, Ñ‚ĞµĞ¼ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ Ğ¼Ñ‹ÑˆĞµÑ‡Ğ½Ğ¾Ğ¹ Ğ¼Ğ°Ñ�Ñ�Ñ‹ Ğ² Ñ�Ğ¾Ğ¾Ñ‚Ğ²ĞµÑ‚Ñ�Ñ‚Ğ²ÑƒÑ�Ñ‰ĞµĞ¼ Ñ�ĞµĞ³Ğ¼ĞµĞ½Ñ‚Ğµ
        # Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Ñ€ĞµĞ³Ñ€ĞµÑ�Ñ�Ğ¸Ğ¾Ğ½Ğ½Ñ‹Ğµ ĞºĞ¾Ñ�Ñ„Ñ„Ğ¸Ñ†Ğ¸ĞµĞ½Ñ‚Ñ‹ (ÑƒĞ¿Ñ€Ğ¾Ñ‰Ñ‘Ğ½Ğ½Ğ¾)
        avg_forearm = 28 if gender == 'male' else 24
        avg_calf = 38 if gender == 'male' else 35
        avg_chest = 100 if gender == 'male' else 90

        arm_factor = forearm_cm / avg_forearm
        leg_factor = calf_cm / avg_calf
        trunk_factor = chest_cm / avg_chest

        total_factor = arm_factor + leg_factor + trunk_factor
        if total_factor > 0:
            # Ğ¿ĞµÑ€ĞµĞ½Ğ°Ğ·Ğ½Ğ°Ñ‡Ğ°ĞµĞ¼ Ğ¿Ñ€Ğ¾Ğ¿Ğ¾Ñ€Ñ†Ğ¸Ğ¸
            base['arms'] = lean_mass * (arm_factor / total_factor)
            base['legs'] = lean_mass * (leg_factor / total_factor)
            base['trunk'] = lean_mass * (trunk_factor / total_factor)

    return {k: round(v, 1) for k, v in base.items()}
