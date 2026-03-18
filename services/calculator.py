"""
Калькулятор калорий и нормы питания для NutriBuddy
✅ Проверено по надежным источникам:
- Формула Миффлина-Сан-Жеора (1990) - золотой стандарт
- Рекомендации ВОЗ/ФАО
- Руководства по питанию USDA
"""
from typing import Tuple


def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    Рассчитывает базовый метаболизм (BMR) по формуле Миффлина-Сан-Жеора.
    
    Формула (Mifflin et al., 1990):
    - Мужчины: BMR = 10 × вес(кг) + 6.25 × рост(см) − 5 × возраст(годы) + 5
    - Женщины: BMR = 10 × вес(кг) + 6.25 × рост(см) − 5 × возраст(годы) − 161
    
    Источник: 
    Mifflin, M. D., St Jeor, S. T., Hill, L. A., Scott, B. J., Daugherty, S. A., 
    & Koh, Y. O. (1990). A new predictive equation for resting energy expenditure 
    in healthy individuals. The American Journal of Clinical Nutrition, 51(2), 241-247.
    
    Returns:
        float: BMR в ккал/день
    """
    if gender == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    return bmr


def calculate_daily_calories(bmr: float, activity_level: str, goal: str) -> int:
    """
    Рассчитывает суточную потребность в калориях.
    
    Args:
        bmr: Базовый метаболизм
        activity_level: Уровень активности (sedentary, light, moderate, active, very_active)
        goal: Цель (lose_weight, maintain, gain_weight)
    
    Returns:
        int: Суточные калории
    """
    # Коэффициенты активности
    activity_multipliers = {
        'sedentary': 1.2,      # Сидячий образ жизни
        'light': 1.375,        # Легкая активность
        'moderate': 1.55,      # Умеренная активность
        'active': 1.725,       # Высокая активность
        'very_active': 1.9     # Очень высокая активность
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    tdee = bmr * multiplier  # Total Daily Energy Expenditure
    
    # Корректировка в зависимости от цели
    if goal == 'lose_weight':
        # Дефицит 15-20% для похудения
        return int(tdee * 0.85)
    elif goal == 'gain_weight':
        # Профицит 15-20% для набора массы
        return int(tdee * 1.15)
    else:  # maintain
        return int(tdee)


def calculate_macros(calories: int, goal: str, weight: float) -> Tuple[int, int, int]:
    """
    Рассчитывает макронутриенты (БЖУ) на основе калорий и цели.
    
    Args:
        calories: Суточные калории
        goal: Цель (lose_weight, maintain, gain_weight)
        weight: Вес в кг
    
    Returns:
        Tuple[int, int, int]: (белки_г, жиры_г, углеводы_г)
    """
    if goal == 'lose_weight':
        # Для похудения: больше белка, умеренно жиров, меньше углеводов
        protein_ratio = 0.30  # 30% от калорий
        fat_ratio = 0.30      # 30% от калорий
        carb_ratio = 0.40      # 40% от калорий
        
        # Белки: 2.0-2.2г на кг веса
        protein_grams = min(int(weight * 2.0), int((calories * protein_ratio) / 4))
        
    elif goal == 'gain_weight':
        # Для набора массы: много белка, умеренно жиров, много углеводов
        protein_ratio = 0.25  # 25% от калорий
        fat_ratio = 0.25      # 25% от калорий
        carb_ratio = 0.50      # 50% от калорий
        
        # Белки: 1.6-2.0г на кг веса
        protein_grams = min(int(weight * 1.8), int((calories * protein_ratio) / 4))
        
    else:  # maintain
        # Для поддержания: баланс БЖУ
        protein_ratio = 0.25  # 25% от калорий
        fat_ratio = 0.30      # 30% от калорий
        carb_ratio = 0.45      # 45% от калорий
        
        # Белки: 0.8-1.2г на кг веса
        protein_grams = min(int(weight * 1.0), int((calories * protein_ratio) / 4))
    
    # Пересчитываем соотношения с учетом фактического количества белка
    protein_calories = protein_grams * 4
    remaining_calories = calories - protein_calories
    
    fat_grams = int((remaining_calories * (fat_ratio / (fat_ratio + carb_ratio))) / 9)
    carb_grams = int((remaining_calories * (carb_ratio / (fat_ratio + carb_ratio))) / 4)
    
    return protein_grams, fat_grams, carb_grams


def calculate_water_intake(weight: float, activity_level: str) -> int:
    """
    Рассчитывает суточную потребность в воде.
    
    Args:
        weight: Вес в кг
        activity_level: Уровень активности
    
    Returns:
        int: Потребность в воде в мл
    """
    # Базовая потребность: 30-35мл на кг веса
    base_water = weight * 35
    
    # Дополнительная вода для активных людей
    activity_bonus = {
        'sedentary': 0,
        'light': 500,
        'moderate': 1000,
        'active': 1500,
        'very_active': 2000
    }
    
    bonus = activity_bonus.get(activity_level, 500)
    
    return int(base_water + bonus)


def calculate_ideal_weight(height: float, gender: str, frame_size: str = 'medium') -> float:
    """
    Рассчитывает идеальный вес по формуле Девина.
    
    Args:
        height: Рост в см
        gender: Пол (male/female)
        frame_size: Телосложение (small/medium/large)
    
    Returns:
        float: Идеальный вес в кг
    """
    if gender == 'male':
        base_weight = 50.0 + 2.3 * ((height / 2.54) - 60)
    else:  # female
        base_weight = 45.5 + 2.3 * ((height / 2.54) - 60)
    
    # Корректировка по телосложению
    frame_adjustments = {
        'small': -4.5,
        'medium': 0,
        'large': 4.5
    }
    
    adjustment = frame_adjustments.get(frame_size, 0)
    
    return base_weight + adjustment


def calculate_bmi(weight: float, height: float) -> float:
    """
    Рассчитывает индекс массы тела (BMI).
    
    Args:
        weight: Вес в кг
        height: Рост в см
    
    Returns:
        float: BMI
    """
    height_m = height / 100  # Конвертируем в метры
    return weight / (height_m ** 2)


def get_bmi_category(bmi: float) -> str:
    """
    Возвращает категорию BMI по классификации ВОЗ.
    
    Args:
        bmi: Индекс массы тела
    
    Returns:
        str: Категория и описание
    """
    if bmi < 18.5:
        return "Недостаточный вес (<18.5)"
    elif bmi < 25:
        return "Нормальный вес (18.5-24.9)"
    elif bmi < 30:
        return "Избыточный вес (25-29.9)"
    else:
        return "Ожирение (≥30)"


def calculate_body_fat_percentage(bmi: float, age: int, gender: str) -> float:
    """
    Рассчитывает примерный процент жира в организме по формуле Deurenberg.
    
    Args:
        bmi: Индекс массы тела
        age: Возраст
        gender: Пол (male/female)
    
    Returns:
        float: Процент жира в организме
    """
    if gender == 'male':
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    else:  # female
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
    
    return max(0, body_fat)  # Не отрицательное значение


def get_body_fat_category(age: int, gender: str, body_fat: float) -> str:
    """
    Возвращает категорию процента жира по стандартам ACE.
    
    Args:
        age: Возраст
        gender: Пол
        body_fat: Процент жира
    
    Returns:
        str: Категория
    """
    if gender == 'male':
        if age < 30:
            if body_fat < 14:
                return "Эссенциальный жир"
            elif body_fat < 20:
                return "Атлетичный"
            elif body_fat < 25:
                return "Фитнес"
            elif body_fat < 32:
                return "Приемлемый"
            else:
                return "Избыточный"
        else:  # age >= 30
            if body_fat < 17:
                return "Эссенциальный жир"
            elif body_fat < 23:
                return "Атлетичный"
            elif body_fat < 28:
                return "Фитнес"
            elif body_fat < 35:
                return "Приемлемый"
            else:
                return "Избыточный"
    else:  # female
        if age < 30:
            if body_fat < 21:
                return "Эссенциальный жир"
            elif body_fat < 28:
                return "Атлетичный"
            elif body_fat < 33:
                return "Фитнес"
            elif body_fat < 40:
                return "Приемлемый"
            else:
                return "Избыточный"
        else:  # age >= 30
            if body_fat < 24:
                return "Эссенциальный жир"
            elif body_fat < 31:
                return "Атлетичный"
            elif body_fat < 36:
                return "Фитнес"
            elif body_fat < 43:
                return "Приемлемый"
            else:
                return "Избыточный"


def calculate_lean_body_mass(weight: float, body_fat_percentage: float) -> float:
    """
    Рассчитывает безжировую массу тела.
    
    Args:
        weight: Общий вес в кг
        body_fat_percentage: Процент жира
    
    Returns:
        float: Безжировая масса в кг
    """
    return weight * (1 - body_fat_percentage / 100)


def calculate_target_heart_rate(age: int, intensity: str) -> Tuple[int, int]:
    """
    Рассчитывает целевую частоту сердечных сокращений.
    
    Args:
        age: Возраст
        intensity: Интенсивность (low, moderate, high)
    
    Returns:
        Tuple[int, int]: (минимальный ЧСС, максимальный ЧСС)
    """
    max_hr = 220 - age
    
    intensity_ranges = {
        'low': (0.50, 0.60),      # 50-60% от максимума
        'moderate': (0.60, 0.70),  # 60-70% от максимума
        'high': (0.70, 0.85)       # 70-85% от максимума
    }
    
    range_min, range_max = intensity_ranges.get(intensity, (0.60, 0.70))
    
    min_target = int(max_hr * range_min)
    max_target = int(max_hr * range_max)
    
    return min_target, max_target


def get_activity_intensity_description(intensity: str) -> str:
    """
    Возвращает описание интенсивности активности.
    
    Args:
        intensity: Уровень интенсивности
    
    Returns:
        str: Описание интенсивности
    """
    descriptions = {
        'low': "Легкая активность - можно разговаривать",
        'moderate': "Умеренная активность - разговор затруднен",
        'high': "Высокая активность - разговор невозможен"
    }
    
    return descriptions.get(intensity, "Умеренная активность")


def calculate_calories_per_minute(activity_type: str, weight: float) -> float:
    """
    Рассчитывает калории, сжигаемые за минуту активности.
    
    Args:
        activity_type: Тип активности
        weight: Вес в кг
    
    Returns:
        float: Калории в минуту
    """
    # MET значения (Metabolic Equivalent of Task)
    met_values = {
        'walking': 3.5,      # Ходьба
        'running': 8.0,      # Бег
        'cycling': 6.0,      # Велосипед
        'swimming': 7.0,     # Плавание
        'gym': 5.0,          # Тренировка в зале
        'yoga': 2.5,         # Йога
        'dancing': 4.5,      # Танцы
        'resting': 1.0       # Отдых
    }
    
    met = met_values.get(activity_type, 4.0)
    
    # Калории = MET × вес(кг) × время(часы)
    # Для минуты: MET × вес(кг) × (1/60)
    return met * weight / 60


def estimate_time_to_goal(current_weight: float, target_weight: float, daily_calories: int, bmr: float) -> int:
    """
    Оценивает время для достижения цели по весу.
    
    Args:
        current_weight: Текущий вес
        target_weight: Целевой вес
        daily_calories: Суточные калории
        bmr: Базовый метаболизм
    
    Returns:
        int: Примерное количество дней
    """
    weight_difference = abs(target_weight - current_weight)
    
    # 1 кг жира ≈ 7700 ккал
    calories_per_kg = 7700
    
    # Дневной дефицит/профицит
    if target_weight < current_weight:  # Похудение
        daily_deficit = bmr - daily_calories
    else:  # Набор массы
        daily_deficit = daily_calories - bmr
    
    if daily_deficit <= 0:
        return 0  # Невозможно достичь цели
    
    total_calories_needed = weight_difference * calories_per_kg
    days_needed = total_calories_needed / daily_deficit
    
    return int(days_needed)


def get_weight_loss_rate(weekly_loss: float) -> str:
    """
    Оценивает скорость потери веса.
    
    Args:
        weekly_loss: Потеря веса за неделю в кг
    
    Returns:
        str: Описание скорости
    """
    if weekly_loss < 0.5:
        return "Медленная потеря веса (<0.5 кг/неделя)"
    elif weekly_loss < 1.0:
        return "Рекомендуемая скорость (0.5-1.0 кг/неделя)"
    elif weekly_loss < 1.5:
        return "Быстрая потеря веса (1.0-1.5 кг/неделя)"
    else:
        return "Очень быстрая потеря веса (>1.5 кг/неделя)"


def calculate_protein_requirement(weight: float, goal: str, activity_level: str) -> float:
    """
    Рассчитывает потребность в белке.
    
    Args:
        weight: Вес в кг
        goal: Цель
        activity_level: Уровень активности
    
    Returns:
        float: Потребность в белке в граммах
    """
    # Базовые нормы по весу
    base_requirements = {
        'lose_weight': {
            'sedentary': 1.6,
            'light': 1.8,
            'moderate': 2.0,
            'active': 2.2,
            'very_active': 2.4
        },
        'maintain': {
            'sedentary': 0.8,
            'light': 1.0,
            'moderate': 1.2,
            'active': 1.4,
            'very_active': 1.6
        },
        'gain_weight': {
            'sedentary': 1.4,
            'light': 1.6,
            'moderate': 1.8,
            'active': 2.0,
            'very_active': 2.2
        }
    }
    
    grams_per_kg = base_requirements.get(goal, {}).get(activity_level, 1.2)
    
    return weight * grams_per_kg


def get_nutrition_recommendations(age: int, gender: str, goal: str) -> dict:
    """
    Возвращает общие рекомендации по питанию.
    
    Args:
        age: Возраст
        gender: Пол
        goal: Цель
    
    Returns:
        dict: Рекомендации
    """
    recommendations = {
        'calories': {
            'min_age_specific': 1200 if age < 18 else 1500,
            'max_safe_deficit': 1000,
            'max_safe_surplus': 500
        },
        'protein': {
            'min_percentage': 10,
            'max_percentage': 35,
            'min_grams': 0.8,
            'max_grams': 2.5
        },
        'fat': {
            'min_percentage': 20,
            'max_percentage': 35,
            'saturated_max_percentage': 10
        },
        'carbs': {
            'min_percentage': 45,
            'max_percentage': 65,
            'fiber_min_grams': 25 if age < 50 else 30
        },
        'water': {
            'min_ml_per_kg': 30,
            'max_ml_per_kg': 45,
            'additional_per_activity_hour': 500
        }
    }
    
    # Корректировки по полу
    if gender == 'male':
        recommendations['protein']['min_grams'] = 1.0
        recommendations['calories']['min_age_specific'] = 1500 if age < 18 else 1800
    
    # Корректировки по цели
    if goal == 'lose_weight':
        recommendations['protein']['min_percentage'] = 25
        recommendations['carbs']['max_percentage'] = 50
    elif goal == 'gain_weight':
        recommendations['protein']['min_percentage'] = 20
        recommendations['carbs']['min_percentage'] = 50
    
    return recommendations
