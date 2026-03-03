"""
Сервис для планирования питания: распределение калорий и формирование промпта для AI.
"""
from typing import Dict

DEFAULT_DISTRIBUTION = {
    "breakfast": 0.30,
    "lunch": 0.35,
    "dinner": 0.25,
    "snack": 0.10
}

def distribute_calories(total_calories: float) -> Dict[str, float]:
    return {
        "breakfast": round(total_calories * DEFAULT_DISTRIBUTION["breakfast"]),
        "lunch": round(total_calories * DEFAULT_DISTRIBUTION["lunch"]),
        "dinner": round(total_calories * DEFAULT_DISTRIBUTION["dinner"]),
        "snack": round(total_calories * DEFAULT_DISTRIBUTION["snack"])
    }

def get_meal_plan_prompt(user_data: Dict) -> str:
    goal_ru = {
        "lose": "похудение",
        "maintain": "поддержание веса",
        "gain": "набор массы"
    }.get(user_data.get("goal"), "поддержание веса")

    prompt = (
        f"Составь примерное меню на один день для человека с целью «{goal_ru}». "
        f"Дневная норма калорий: {user_data['daily_calories']} ккал.\n"
        f"Меню должно включать завтрак, обед, ужин и один перекус.\n"
        f"Для каждого приёма пищи укажи название блюда и примерную калорийность.\n"
        f"Постарайся, чтобы сумма калорий соответствовала дневной норме.\n"
        f"Используй русский язык, блюда должны быть простыми и доступными."
    )
    return prompt
