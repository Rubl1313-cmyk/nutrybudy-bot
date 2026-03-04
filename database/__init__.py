"""
Database package for NutriBuddy
✅ Экспортирует Base, модели и функции
"""
from database.db import Base, init_db, get_session, close_db, engine
from database.models import (
    User, Meal, FoodItem, WaterEntry, WeightEntry,
    ShoppingList, ShoppingItem, Reminder, Activity
)

__all__ = [
    'Base', 'engine',
    'User', 'Meal', 'FoodItem', 'WaterEntry', 'WeightEntry',
    'ShoppingList', 'ShoppingItem', 'Reminder', 'Activity',
    'init_db', 'get_session', 'close_db'
]
