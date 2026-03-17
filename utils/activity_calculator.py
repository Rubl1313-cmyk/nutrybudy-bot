"""
Калькулятор целей активности
"""
import logging

logger = logging.getLogger(__name__)

def calculate_activity_calorie_goal(user) -> int:
    """
    Возвращает рекомендуемое количество калорий, которое стоит сжигать
    за счёт физической активности в день, исходя из цели пользователя.
    
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

def calculate_activity_steps_goal(user) -> int:
    """
    Возвращает рекомендуемое количество шагов в день исходя из цели пользователя.
    
    Args:
        user: Объект пользователя с полями goal, daily_steps_goal
        
    Returns:
        int: Целевые шаги в день
    """
    # Если у пользователя уже установлена цель, используем её
    if hasattr(user, 'daily_steps_goal') and user.daily_steps_goal:
        return user.daily_steps_goal
    
    # Базовая рекомендация: 10000 шагов
    base = 10000
    
    if user.goal == "lose_weight":
        # Для похудения увеличиваем шаги
        return base + 3000  # 13000 шагов
    elif user.goal == "gain_weight":
        # Для набора массы активность умеренная
        return base - 2000  # 8000 шагов
    else:  # maintain
        return base

def get_activity_recommendation(user) -> str:
    """
    Возвращает рекомендацию по активности на основе цели пользователя.
    
    Args:
        user: Объект пользователя
        
    Returns:
        str: Рекомендация по активности
    """
    if user.goal == "lose_weight":
        return (
            "🔥 Для похудения рекомендуется:\n"
            "• 500 ккал активности в день\n"
            "• 13000 шагов в день\n"
            "• Кардио тренировки 3-4 раза в неделю"
        )
    elif user.goal == "gain_weight":
        return (
            "💪 Для набора массы рекомендуется:\n"
            "• 200 ккал активности в день\n"
            "• 8000 шагов в день\n"
            "• Силовые тренировки 3-4 раза в неделю"
        )
    else:  # maintain
        return (
            "⚖️ Для поддержания веса рекомендуется:\n"
            "• 300 ккал активности в день\n"
            "• 10000 шагов в день\n"
            "• Сбалансированные тренировки 3-4 раза в неделю"
        )
