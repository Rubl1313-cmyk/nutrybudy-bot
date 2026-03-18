"""
Database package for NutriBuddy
✅ Экспортирует Base, модели и функции
"""
from database.db import Base, init_db, get_session, close_db, engine
from database.models import (
    User, FoodEntry, DrinkEntry, WeightEntry, ActivityEntry
)

__all__ = [
    'Base', 'engine',
    'User', 'FoodEntry', 'DrinkEntry', 'WeightEntry', 'ActivityEntry',
    'init_db', 'get_session', 'close_db'
]
