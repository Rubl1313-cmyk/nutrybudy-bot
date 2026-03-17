from . import (
    universal,        # Универсальный обработчик с LangChain
    ai_handler,       # Фото и медиа обработка
    common,           # Базовые команды
    reply_handlers,   # Reply-кнопки
    profile,          # Профиль пользователя
    water,            # Учет воды
    progress,         # Статистика и прогресс
    activity,         # Учет активности
    weight,           # Учет веса
    meal_plan,        # Планирование питания
    ai_assistant,     # AI ассистент
    food_clarification,  # Уточнение продуктов
    achievements      # Достижения
)

__all__ = [
    'universal', 'ai_handler', 'common', 'reply_handlers', 'profile', 'water',
    'progress', 'activity', 'weight', 'meal_plan', 'ai_assistant',
    'food_clarification', 'achievements'
]
