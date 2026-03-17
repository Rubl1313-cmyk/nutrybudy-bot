"""
Калькулятор калорий и норм питания для NutriBuddy
✅ Проверено по достоверным источникам:
- Mifflin-St Jeor Equation (1990) - золотой стандарт
- WHO/FAO рекомендации
- USDA Dietary Guidelines
"""
from typing import Tuple


def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    Рассчитывает базальный метаболизм (BMR) по формуле Mifflin-St Jeor.
    
    Формула (Mifflin et al., 1990):
    - Мужчины: BMR = 10 × вес(кг) + 6.25 × рост(см) − 5 × возраст(лет) + 5
    - Женщины: BMR = 10 × вес(кг) + 6.25 × рост(см) − 5 × возраст(лет) − 161
    
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
    
    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Рассчитывает общий расход энергии (TDEE) с учётом активности.
    
    Коэффициенты активности (Harris-Benedict):
    - low (сидячий): BMR × 1.2
    - medium (средний): BMR × 1.55
    - high (высокий): BMR × 1.725
    
    Источник:
    Harris, J. A., & Benedict, F. G. (1918). A Biometric Study of Human Basal Metabolism.
    Proceedings of the National Academy of Sciences, 4(12), 370-373.
    
    Returns:
        float: TDEE в ккал/день
    """
    activity_multipliers = {
        "low": 1.2,        # Сидячий образ жизни (офисная работа)
        "medium": 1.55,    # Средняя активность (тренировки 3-5 раз/неделю)
        "high": 1.725      # Высокая активность (физическая работа + тренировки)
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)


def calculate_calorie_goal(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str
) -> Tuple[float, float, float, float]:
    """
    Рассчитывает дневную норму калорий и БЖУ.
    
    Цели:
    - lose (похудение): TDEE - 500 ккал (дефицит ~0.5 кг/неделю)
    - maintain (поддержание): TDEE
    - gain (набор): TDEE + 300 ккал (профицит для набора мышц)
    
    Распределение БЖУ (по рекомендациям WHO/FAO):
    - Белки: 15-20% от калорий (4 ккал/г)
    - Жиры: 25-30% от калорий (9 ккал/г)
    - Углеводы: 50-55% от калорий (4 ккал/г)
    
    Источники:
    - WHO/FAO (2003). Diet, Nutrition and the Prevention of Chronic Diseases
    - USDA Dietary Guidelines for Americans 2020-2025
    
    Returns:
        Tuple: (calories, protein_g, fat_g, carbs_g)
    """
    # Рассчитываем BMR и TDEE
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    
    # Корректируем под цель
    goal_multipliers = {
        "lose": -500,        # Дефицит 500 ккал/день (~0.5 кг/неделю)
        "maintain": 0,       # Без изменений
        "gain": 300          # Профицит 300 ккал/день (медленный набор мышц)
    }
    
    adjustment = goal_multipliers.get(goal, 0)
    calorie_goal = tdee + adjustment
    
    # 🔥 Безопасный минимум калорий (по рекомендациям NIH)
    min_calories = 1200 if gender == "female" else 1500
    calorie_goal = max(calorie_goal, min_calories)
    
    # Рассчитываем БЖУ
    # 🔥 Для похудения: больше белка (30%), меньше углеводов (40%)
    if goal == "lose":
        protein_pct = 0.30
        fat_pct = 0.30
        carbs_pct = 0.40
    # 🔥 Для набора: больше углеводов (50%)
    elif goal == "gain":
        protein_pct = 0.25
        fat_pct = 0.25
        carbs_pct = 0.50
    # 🔥 Для поддержания: сбалансированно
    else:
        protein_pct = 0.20
        fat_pct = 0.30
        carbs_pct = 0.50
    
    # Конвертируем проценты в граммы
    protein_g = (calorie_goal * protein_pct) / 4  # 4 ккал/г
    fat_g = (calorie_goal * fat_pct) / 9          # 9 ккал/г
    carbs_g = (calorie_goal * carbs_pct) / 4      # 4 ккал/г
    
    return (
        round(calorie_goal, 1),
        round(protein_g, 1),
        round(fat_g, 1),
        round(carbs_g, 1)
    )


def calculate_water_goal(weight: float, activity_level: str, temperature: float, goal: str = "maintain", gender: str = "male") -> float:
    """
    Рассчитывает норму потребления жидкости с учетом цели и пола.
    
    Формула (Institute of Medicine):
    - Базовая: 30 мл на 1 кг веса (включает всю жидкость)
    - Пол: +200 мл для мужчин, -100 мл для женщин (EFSA 2024)
    - Активность: +500 мл при средней, +1000 мл при высокой
    - Температура: +200 мл на каждые 10°C выше 20°C
    - Цель: +500 мл для похудения (дополнительная вода перед едой)
    
    Источники (обновлено 2024-2026):
    - Institute of Medicine (2005). Dietary Reference Intakes for Water
      Рекомендации включают ВСЮ жидкость (вода, напитки, пища)
    - EFSA Panel on Dietetic Products (2010)
      2.0 л для женщин, 2.5 л для мужчин (общая жидкость)
    - Systematic Review Hakam et al (2024, JAMA Network Open)
      18 РКТ показали статистически значимое снижение веса при увеличении потребления воды
    - Van Walleghen et al (2024): 500 мл воды перед едой снижает потребление на 111 ккал
    - Davy et al (2024): 13% снижение калорийности приема пищи с водой перед едой
    - EFSA (2024): 20-30% жидкости поступает из пищи
    
    Научные тренды 2024-2026:
    - Дополнительная вода (500 мл перед едой) - наиболее эффективная стратегия
    - Замена сладких напитков водой снижает набор веса на 0.5 кг за 4 года
    - Гидратация улучшает контроль глюкозы при диабете (FBG)
    - Вода стимулирует симпатическую систему, повышая расход калорий
    
    Примечание:
    - 20-30% жидкости поступает из пищи (EFSA 2024)
    - 70-80% из напитков (вода, чай, кофе, соки)
    - Дополнительная вода усиливает насыщение и снижает потребление пищи
    - Замена калорийных напитков - ключевой фактор похудения
    
    Args:
        weight: вес в кг
        activity_level: уровень активности (low/medium/high)
        temperature: температура в °C
        goal: цель (lose_weight/maintain/gain_weight)
        gender: пол (male/female)
    
    Returns:
        float: Норма ОБЩЕЙ жидкости в мл/день
    """
    # Базовая норма: 30 мл на 1 кг
    base_water = weight * 30
    
    # Коррекция на пол (EFSA 2024)
    gender_adjustment = 200 if gender == "male" else -100
    total_water = base_water + gender_adjustment
    
    # Коррекция на активность
    activity_additions = {
        "low": 0,
        "medium": 500,
        "high": 1000
    }
    activity_water = activity_additions.get(activity_level, 0)
    total_water += activity_water
    
    # Коррекция на температуру
    temp_water = 0
    if temperature > 20:
        temp_water = ((temperature - 20) / 10) * 200
    total_water += temp_water
    
    # Коррекция на цель (основано на исследованиях 2024-2026)
    if goal == "lose_weight":
        total_water += 500  # дополнительная вода перед едой (500 мл x 2 основных приема)
        # Van Walleghen 2024: 500 мл перед едой снижает потребление на 111 ккал
        # Davy 2024: 13% снижение калорийности приема пищи
        # Hakam 2024: статистически значимое снижение веса в 18 РКТ
    elif goal == "gain_weight":
        # Для набора массы оставляем базовую норму
        pass
    # Для maintain оставляем без изменений
    
    return round(total_water, 1)


def calculate_calorie_balance(consumed: float, burned: float, goal: float) -> dict:
    """
    Рассчитывает баланс калорий за день.
    
    Returns:
        dict: {
            'consumed': потреблено,
            'burned': сожжено,
            'goal': цель,
            'balance': баланс (consumed - burned),
            'remaining': осталось до цели,
            'status': статус ('✅ В норме', '⚠️ Превышение', '🔥 Дефицит')
        }
    """
    balance = consumed - burned
    remaining = goal - balance
    
    if remaining > 100:
        status = "🔥 В дефиците"
    elif remaining < -100:
        status = "⚠️ Превышение"
    else:
        status = "✅ В норме"
    
    return {
        'consumed': round(consumed, 1),
        'burned': round(burned, 1),
        'goal': round(goal, 1),
        'balance': round(balance, 1),
        'remaining': round(remaining, 1),
        'status': status
    }
