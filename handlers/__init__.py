from . import (
    dialog,          # Универсальный обработчик текстовых сообщений
    ai_handler,      # Фото и медиа обработка
    common,          # Базовые команды
    reply_handlers,  # Reply-кнопки
    profile,         # Профиль пользователя
    water,           # Учет воды
    progress,        # Статистика и прогресс
    activity,        # Учет активности
    weight,          # Учет веса
    meal_plan,       # Планирование питания
    ai_assistant,    # AI ассистент
    food             # 
)

__all__ = [
    'dialog', 'ai_handler', 'common', 'reply_handlers', 'profile', 'water',
    'progress', 'activity', 'weight', 'meal_plan', 'ai_assistant', 'food'
]
