from . import (
    universal,            # Универсальный обработчик с LangChain
    common,               # Базовые команды
    reply_handlers,       # Reply-кнопки
    profile,              # Профиль пользователя
    drinks,               # Учет жидкости (единый модуль)
    progress,             # Статистика и прогресс
    activity,             # Учет активности
    weight,               # Учет веса
    meal_plan,            # Планирование питания
    ai_assistant,          # AI ассистент
    food_clarification,    # Уточнение продуктов
    timezone_handlers,      # Обработчики часовых поясов
    food,                 # Запись еды
)

__all__ = [
    'universal', 'common', 'reply_handlers', 'profile', 'drinks',
    'progress', 'activity', 'weight', 'meal_plan', 'ai_assistant',
    'food_clarification', 'timezone_handlers', 'food'
]
