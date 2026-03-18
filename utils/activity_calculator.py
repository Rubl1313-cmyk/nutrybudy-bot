"""
Калькулятор целей активности
"""
import logging

logger = logging.getLogger(__name__)

def calculate_activity_calorie_goal(user) -> int:
    """
    Возвращает рекомендуемое количество калорий, которое стоит сжигать
    за счет физической активности в день, исходя из цели пользователя.
    
    Args:
        user: Объект пользователя с полями goal, daily_calorie_goal
        
    Returns:
        int: Целевые калории активности в день
    """
    # Базовая рекомендация: 300 ккал для поддержания
    base = 300
    
    if user.goal == "lose_weight":
        # Для похудения увеличиваем активность
        return base + 200  # 500 ккал
    elif user.goal == "gain_weight":
        # Для набора массы активность умеренная
        return base - 100  # 200 ккал
    else:  # maintain
        return base

def calculate_calories_burned(activity_type: str, duration: int, weight: float) -> float:
    """
    Рассчитывает сожженные калории для конкретной активности.
    
    Args:
        activity_type: Тип активности (running, cycling, gym, etc.)
        duration: Длительность в минутах
        weight: Вес пользователя в кг
        
    Returns:
        float: Сожженные калории
    """
    # MET значения для разных видов активности (Metabolic Equivalent of Task)
    met_values = {
        'running': 8.0,      # Бег
        'cycling': 6.0,      # Велосипед
        'gym': 5.0,          # Тренировка в зале
        'yoga': 2.5,         # Йога
        'walking': 3.5,      # Ходьба
        'swimming': 7.0,     # Плавание
        'other': 4.0         # Другое
    }
    
    met = met_values.get(activity_type, 4.0)
    
    # Формула: калории = MET * вес(кг) * время(часы)
    calories = met * weight * (duration / 60)
    
    return round(calories, 1)

def calculate_activity_intensity(activity_type: str, duration: int, weight: float) -> str:
    """
    Определяет интенсивность активности на основе сожженных калорий.
    
    Args:
        activity_type: Тип активности
        duration: Длительность в минутах
        weight: Вес пользователя в кг
        
    Returns:
        str: Интенсивность (low, moderate, high)
    """
    calories_burned = calculate_calories_burned(activity_type, duration, weight)
    calories_per_minute = calories_burned / duration
    
    # Пороги интенсивности в калориях в минуту
    if calories_per_minute < 5:
        return 'low'
    elif calories_per_minute < 10:
        return 'moderate'
    else:
        return 'high'

def calculate_weekly_activity_goal(user) -> dict:
    """
    Рассчитывает недельные цели активности.
    
    Args:
        user: Объект пользователя
        
    Returns:
        dict: Недельные цели по разным параметрам
    """
    daily_calorie_goal = calculate_activity_calorie_goal(user)
    
    return {
        'calories': daily_calorie_goal * 7,  # Калории за неделю
        'minutes': 300,                       # 300 минут (5 часов) в неделю
        'sessions': 5,                        # 5 тренировок в неделю
        'steps': 70000                        # 70,000 шагов в неделю (10,000 в день)
    }

def calculate_monthly_activity_goal(user) -> dict:
    """
    Рассчитывает месячные цели активности.
    
    Args:
        user: Объект пользователя
        
    Returns:
        dict: Месячные цели по разным параметрам
    """
    weekly_goal = calculate_weekly_activity_goal(user)
    
    return {
        'calories': weekly_goal['calories'] * 4,    # ~4 недели в месяце
        'minutes': weekly_goal['minutes'] * 4,
        'sessions': weekly_goal['sessions'] * 4,
        'steps': weekly_goal['steps'] * 4
    }

def get_activity_recommendations(user, current_activity: dict) -> list:
    """
    Генерирует рекомендации по активности на основе текущего прогресса.
    
    Args:
        user: Объект пользователя
        current_activity: Текущая активность за период
        
    Returns:
        list: Список рекомендаций
    """
    recommendations = []
    
    # Цели на день
    daily_goal = calculate_activity_calorie_goal(user)
    current_calories = current_activity.get('calories_burned', 0)
    
    if current_calories < daily_goal * 0.5:
        recommendations.append(
            f"💡 Вам нужно еще сжечь {daily_goal - current_calories:.0f} ккал сегодня. "
            "Попробуйте быструю 30-минутную прогулку или легкую тренировку."
        )
    elif current_calories < daily_goal:
        recommendations.append(
            f"💪 Отлично! Осталось всего {daily_goal - current_calories:.0f} ккал до дневной цели. "
            "15 минут интенсивной активности помогут достичь цели."
        )
    else:
        recommendations.append(
            "🎉 Поздравляю! Вы выполнили дневную цель по активности! "
            "Отдыхайте или добавьте легкую растяжку."
        )
    
    # Рекомендации по типу активности
    activity_types = current_activity.get('types', {})
    
    if not activity_types.get('cardio', 0):
        recommendations.append(
            "🏃 Добавьте кардио-упражнения (бег, ходьба, велосипед) для здоровья сердца."
        )
    
    if not activity_types.get('strength', 0):
        recommendations.append(
            "💪 Включите силовые тренировки для укрепления мышц и метаболизма."
        )
    
    if not activity_types.get('flexibility', 0):
        recommendations.append(
            "🧘 Не забывайте про растяжку и гибкость - это важно для профилактики травм."
        )
    
    return recommendations

def calculate_activity_score(user, period_data: dict) -> dict:
    """
    Рассчитывает оценку активности за период.
    
    Args:
        user: Объект пользователя
        period_data: Данные активности за период
        
    Returns:
        dict: Оценка по разным параметрам
    """
    daily_goal = calculate_activity_calorie_goal(user)
    days_in_period = period_data.get('days_count', 1)
    
    # Калории
    total_calories = period_data.get('total_calories', 0)
    avg_calories = total_calories / days_in_period
    calories_score = min(100, (avg_calories / daily_goal) * 100)
    
    # Минуты
    total_minutes = period_data.get('total_minutes', 0)
    avg_minutes = total_minutes / days_in_period
    minutes_goal = 60  # 60 минут в день
    minutes_score = min(100, (avg_minutes / minutes_goal) * 100)
    
    # Регулярность
    active_days = period_data.get('active_days', 0)
    regularity_score = (active_days / days_in_period) * 100
    
    # Разнообразие
    activity_types = len(period_data.get('activity_types', {}))
    diversity_score = min(100, (activity_types / 3) * 100)  # 3 типа = 100%
    
    # Общая оценка
    overall_score = (calories_score + minutes_score + regularity_score + diversity_score) / 4
    
    return {
        'calories': round(calories_score, 1),
        'minutes': round(minutes_score, 1),
        'regularity': round(regularity_score, 1),
        'diversity': round(diversity_score, 1),
        'overall': round(overall_score, 1)
    }

def get_activity_motivation(score: float, streak_days: int = 0) -> str:
    """
    Генерирует мотивационное сообщение на основе оценки активности.
    
    Args:
        score: Оценка активности (0-100)
        streak_days: Количество дней подряд с активностью
        
    Returns:
        str: Мотивационное сообщение
    """
    if score >= 90:
        if streak_days >= 7:
            return "🔥🏆 Вы чемпион! Неделя отличной активности! Продолжайте в том же духе!"
        else:
            return "🏆 Превосходная активность! Вы почти идеальны!"
    
    elif score >= 75:
        if streak_days >= 5:
            return "💪 Отличная работа! Ваша последовательность впечатляет!"
        else:
            return "💪 Очень хорошая активность! Вы на правильном пути!"
    
    elif score >= 50:
        return "👍 Неплохая активность! Добавьте еще немного для лучших результатов."
    
    elif score >= 25:
        return "💡 Есть куда расти! Попробуйте увеличить активность постепенно."
    
    else:
        return "🌱 Начните с малого! Даже 15 минут активности уже лучше, чем ничего."

def calculate_steps_calories(steps: int, weight: float, height: float, age: int, gender: str) -> float:
    """
    Рассчитывает калории, сожженные при ходьбе по количеству шагов.
    
    Args:
        steps: Количество шагов
        weight: Вес в кг
        height: Рост в см
        age: Возраст
        gender: Пол (male/female)
        
    Returns:
        float: Сожженные калории
    """
    # Средняя длина шага в метрах
    if gender == 'male':
        stride_length = (height * 0.415) / 100  # в метрах
    else:
        stride_length = (height * 0.413) / 100  # в метрах
    
    # Расстояние в км
    distance_km = (steps * stride_length) / 1000
    
    # Калории при ходьбе ~0.5 ккал на кг веса за км
    calories = 0.5 * weight * distance_km
    
    return round(calories, 1)

def get_activity_trend(historical_data: list) -> str:
    """
    Определяет тренд активности на основе исторических данных.
    
    Args:
        historical_data: Список данных активности за последние дни
        
    Returns:
        str: Тренд (increasing, decreasing, stable)
    """
    if len(historical_data) < 3:
        return 'stable'
    
    # Сравниваем последние 3 дня с предыдущими 3 днями
    recent_avg = sum(historical_data[-3:]) / 3
    previous_avg = sum(historical_data[-6:-3]) / 3 if len(historical_data) >= 6 else recent_avg
    
    difference = (recent_avg - previous_avg) / previous_avg * 100
    
    if difference > 10:
        return 'increasing'
    elif difference < -10:
        return 'decreasing'
    else:
        return 'stable'

def calculate_optimal_rest_days(user, recent_activity: list) -> int:
    """
    Рассчитывает рекомендуемое количество дней отдыха в неделю.
    
    Args:
        user: Объект пользователя
        recent_activity: Список активности за последние дни
        
    Returns:
        int: Рекомендуемое количество дней отдыха
    """
    if user.goal == "gain_weight":
        return 2  # 2 дня отдыха для набора массы
    elif user.goal == "lose_weight":
        return 1  # 1 день отдыха для похудения
    else:
        return 2  # 2 дня отдыха для поддержания

def generate_workout_suggestion(user, available_time: int, equipment: list = None) -> dict:
    """
    Генерирует предложение тренировки на основе параметров пользователя.
    
    Args:
        user: Объект пользователя
        available_time: Доступное время в минутах
        equipment: Список доступного оборудования
        
    Returns:
        dict: Предложение тренировки
    """
    suggestions = {
        'cardio': [],
        'strength': [],
        'flexibility': []
    }
    
    # Кардио предложения
    if available_time >= 30:
        suggestions['cardio'].extend([
            {'type': 'running', 'duration': 20, 'calories': calculate_calories_burned('running', 20, user.weight)},
            {'type': 'cycling', 'duration': 30, 'calories': calculate_calories_burned('cycling', 30, user.weight)}
        ])
    
    if available_time >= 15:
        suggestions['cardio'].append(
            {'type': 'walking', 'duration': 15, 'calories': calculate_calories_burned('walking', 15, user.weight)}
        )
    
    # Силовые предложения
    if equipment and 'dumbbells' in equipment:
        suggestions['strength'].append({'type': 'dumbbells', 'duration': 20, 'focus': 'full_body'})
    else:
        suggestions['strength'].append({'type': 'bodyweight', 'duration': 15, 'focus': 'basic'})
    
    # Гибкость
    if available_time >= 10:
        suggestions['flexibility'].append({'type': 'stretching', 'duration': 10})
    
    return suggestions
