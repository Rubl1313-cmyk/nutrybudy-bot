"""
Database package for NutriBuddy
✅ Импортируем модели ДО инициализации БД
"""
from database.models import Base, User, Meal, FoodItem, WaterEntry, WeightEntry, ShoppingList, ShoppingItem, Reminder, Activity
from database.db import init_db, get_session, close_db

__all__ = [
    'Base',
    'User', 'Meal', 'FoodItem', 'WaterEntry', 'WeightEntry',
    'ShoppingList', 'ShoppingItem', 'Reminder', 'Activity',
    'init_db', 'get_session', 'close_db'
]
