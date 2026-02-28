def calculate_water_goal(weight: float, activity: str, temperature: float = 20) -> float:
    base = weight * 30
    if activity == 'high':
        base *= 1.3
    elif activity == 'medium':
        base *= 1.1
    if temperature > 25:
        base *= 1.2
    elif temperature > 30:
        base *= 1.5
    return round(base)

def calculate_calorie_goal(weight: float, height: float, age: int, gender: str,
                          activity: str, goal: str) -> tuple:
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_factors = {'low': 1.2, 'medium': 1.55, 'high': 1.725}
    tdee = bmr * activity_factors[activity]
    
    goal_factors = {'lose': 0.85, 'maintain': 1.0, 'gain': 1.15}
    calories = tdee * goal_factors[goal]
    
    protein = (calories * 0.3) / 4
    fat = (calories * 0.25) / 9
    carbs = (calories * 0.45) / 4
    
    return round(calories), round(protein, 1), round(fat, 1), round(carbs, 1)

def calculate_activity_calories(activity_type: str, duration: int, weight: float, 
                                distance: float = 0, steps: int = 0) -> float:
    """Расчёт сожжённых калорий по типу активности"""
    met_values = {
        'walking': 3.5,
        'running': 9.8,
        'cycling': 7.5,
        'gym': 6.0,
        'yoga': 2.5,
        'swimming': 8.0,
        'hiit': 12.0,
        'stretching': 2.3,
        'dancing': 5.0,
        'sports': 7.0
    }
    
    met = met_values.get(activity_type, 5.0)
    hours = duration / 60
    
    calories = met * weight * hours
    
    if steps > 0:
        step_calories = steps * 0.04
        calories = max(calories, step_calories)
    
    if distance > 0 and activity_type == 'running':
        distance_calories = distance * weight * 1.036
        calories = max(calories, distance_calories)
    
    return round(calories, 1)

def calculate_calorie_balance(consumed: float, burned: float, goal: float) -> dict:
    """Анализ баланса калорий"""
    balance = consumed - burned
    remaining = goal - balance
    
    status = "✅ В норме"
    if balance > goal * 0.1:
        status = "⚠️ Превышение"
    elif balance < goal * 0.8:
        status = "⚠️ Недобор"
    
    return {
        'consumed': round(consumed, 1),
        'burned': round(burned, 1),
        'balance': round(balance, 1),
        'remaining': round(remaining, 1),
        'status': status
    }