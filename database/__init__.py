"""
Database package for NutriBuddy
✅ Экспортирует Base, модели и функции
"""
from database.db import Base, init_db, get_session, close_db, engine
from database.models import (
    User, FoodEntry, FoodItem, DrinkEntry, WeightEntry, Activity
)

__all__ = [
    'Base', 'engine',
    'User', 'FoodEntry', 'FoodItem', 'DrinkEntry', 'WeightEntry', 'Activity',
    'init_db', 'get_session', 'close_db'
]
