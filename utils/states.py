"""
Состояния FSM для различных сценариев.
Содержит все состояния, используемые в хендлерах.
"""
from aiogram.fsm.state import State, StatesGroup

class FoodStates(StatesGroup):
    """Состояния для записи еды."""
    choosing_meal_type = State()  # выбор типа приёма пищи
    searching_food = State()      # поиск продукта в базе
    selecting_food = State()      # выбор из списка найденных
    entering_weight = State()     # ввод веса
    manual_food_name = State()    # ручной ввод названия
    editing_weight = State()      # редактирование веса (в сводке)
    adding_name = State()         # добавление нового продукта (название)
    adding_weight = State()       # добавление нового продукта (вес)

class WaterStates(StatesGroup):
    """Состояния для записи воды."""
    entering_amount = State()
    confirming = State()

class ActivityStates(StatesGroup):
    """Состояния для записи активности (кроме шагов)."""
    waiting_for_type = State()
    waiting_for_duration = State()
    confirming = State()

class StepsStates(StatesGroup):
    """Состояния для записи шагов."""
    waiting_for_steps = State()

class ShoppingStates(StatesGroup):
    """Состояния для списка покупок."""
    adding_item = State()

class ReminderStates(StatesGroup):
    """Состояния для напоминаний."""
    choosing_type = State()
    entering_title = State()
    entering_time = State()
    choosing_days = State()
    confirming = State()

class AIAssistantStates(StatesGroup):
    """Состояния для AI-ассистента."""
    waiting_for_question = State()

class ProfileStates(StatesGroup):
    """Состояния для настройки профиля."""
    weight = State()
    height = State()
    age = State()
    gender = State()
    waiting_for_neck = State()      # Обхват шеи для женщин
    waiting_for_waist = State()     # Обхват талии для женщин
    waiting_for_hip = State()       # Обхват бедер для женщин
    activity = State()
    goal = State()
    city = State()

class ProgressStates(StatesGroup):
    """
    Состояния для прогресса (пока не используются, но импортируются).
    Если появятся, добавьте сюда нужные состояния.
    """
    pass

# ========== НОВОЕ СОСТОЯНИЕ ДЛЯ ЗАПИСИ ВЕСА ==========
class WeightStates(StatesGroup):
    """Состояние для ввода веса."""
    waiting_for_weight = State()
