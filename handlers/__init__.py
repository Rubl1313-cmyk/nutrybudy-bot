from . import (
    universal,             # Универсальные обработчики
    common,               # Общие команды
    reply_handlers,        # Обработчики кнопок
    profile,              # Профиль пользователя
    drinks,               # Учет воды
    progress,             # Прогресс
    activity,             # Активность
    weight,               # Учет веса
    meal_plan,            # Планирование питания
    ai_assistant,          # AI ассистент
    timezone_handlers,      # Обработчики часовых поясов
    food,                 # Запись еды (объединена с food_clarification)
    help,                 # Помощь
    achievements,         # Достижения
)

__all__ = [
    'universal', 'common', 'reply_handlers', 'profile', 'drinks',
    'progress', 'activity', 'weight', 'meal_plan', 'ai_assistant',
    'timezone_handlers', 'food', 'help', 'achievements'
]
