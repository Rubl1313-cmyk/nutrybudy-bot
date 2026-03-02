"""
FSM States для NutriBuddy
Все состояния для работы с конечным автоматом aiogram
✅ Синхронизировано со всеми handlers
"""
from aiogram.fsm.state import State, StatesGroup


# =============================================================================
# 👤 ПРОФИЛЬ
# =============================================================================

class ProfileStates(StatesGroup):
    """Состояния для настройки профиля"""
    weight = State()
    height = State()
    age = State()
    gender = State()
    activity = State()
    goal = State()
    city = State()


# =============================================================================
# 🍽️ ПИТАНИЕ
# =============================================================================

class FoodStates(StatesGroup):
    """Состояния для записи приёма пищи"""
    choosing_meal_type = State()
    searching_food = State()
    selecting_food = State()
    entering_weight = State()
    manual_food_name = State()
    confirming = State()


# =============================================================================
# 💧 ВОДА
# =============================================================================

class WaterStates(StatesGroup):
    """Состояния для записи воды"""
    entering_amount = State()
    confirming = State()


# =============================================================================
# 📋 СПИСКИ ПОКУПОК
# =============================================================================

class ShoppingStates(StatesGroup):
    """Состояния для списков покупок"""
    creating_list = State()
    renaming_list = State()
    adding_item = State()
    editing_item = State()


# =============================================================================
# 🔔 НАПОМИНАНИЯ
# =============================================================================

class ReminderStates(StatesGroup):
    """Состояния для напоминаний"""
    choosing_type = State()
    entering_title = State()
    entering_time = State()
    choosing_days = State()
    confirming = State()


# =============================================================================
# 🏋️ АКТИВНОСТЬ / ФИТНЕС
# =============================================================================

class ActivityStates(StatesGroup):
    """
    Состояния для записи активности.
    ✅ Включает ВСЕ возможные состояния для совместимости
    """
    # Выбор источника данных
    choosing_source = State()
    
    # Ввод данных (основные состояния)
    entering_duration = State()
    entering_distance = State()
    entering_calories = State()
    entering_steps = State()
    entering_type = State()
    
    # Ручной ввод (альтернативные названия)
    manual_type = State()
    manual_duration = State()
    manual_distance = State()
    manual_calories = State()
    manual_steps = State()
    
    # Загрузка GPX
    waiting_gpx = State()
    
    # Подтверждение
    confirming = State()


# =============================================================================
# ⚖️ ВЕС
# =============================================================================

class WeightStates(StatesGroup):
    """Состояния для записи веса"""
    entering_weight = State()


# =============================================================================
# 📊 ПРОГРЕСС
# =============================================================================

class ProgressStates(StatesGroup):
    """Состояния для просмотра прогресса"""
    selecting_period = State()
    selecting_metric = State()


# =============================================================================
# 📖 РЕЦЕПТЫ
# =============================================================================

class RecipeStates(StatesGroup):
    """Состояния для генерации рецептов"""
    entering_ingredients = State()
    selecting_diet = State()
    selecting_difficulty = State()

class ProgressStates(StatesGroup):
    selecting_period = State()

class MealPlanStates(StatesGroup):
    viewing_plan = State()
