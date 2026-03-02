"""
Модели базы данных для NutriBuddy
✅ Все модели используют Base из database.db
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# 🔥 Импортируем Base из db.py (единый источник!)
from database.db import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    weight = Column(Float)
    height = Column(Float)
    age = Column(Integer)
    gender = Column(String(10))
    activity_level = Column(String(20))
    goal = Column(String(20))
    city = Column(String(100))
    daily_water_goal = Column(Float)
    daily_calorie_goal = Column(Float)
    daily_protein_goal = Column(Float)
    daily_fat_goal = Column(Float)
    daily_carbs_goal = Column(Float)
    reminder_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    water_entries = relationship("WaterEntry", back_populates="user", cascade="all, delete-orphan")
    weight_entries = relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    shopping_lists = relationship("ShoppingList", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")


class Meal(Base):
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    meal_type = Column(String(20))
    datetime = Column(DateTime, default=datetime.utcnow, index=True)
    total_calories = Column(Float)
    total_protein = Column(Float)
    total_fat = Column(Float)
    total_carbs = Column(Float)
    photo_url = Column(String(500))
    ai_description = Column(Text)
    
    user = relationship("User", back_populates="meals")
    foods = relationship("FoodItem", back_populates="meal", cascade="all, delete-orphan")


class FoodItem(Base):
    __tablename__ = 'food_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_id = Column(Integer, ForeignKey('meals.id', ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    weight = Column(Float)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)
    barcode = Column(String(50))
    
    meal = relationship("Meal", back_populates="foods")


class WaterEntry(Base):
    __tablename__ = 'water_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    datetime = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="water_entries")


class WeightEntry(Base):
    __tablename__ = 'weight_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    weight = Column(Float, nullable=False)
    datetime = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="weight_entries")


class ShoppingList(Base):
    __tablename__ = 'shopping_lists'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="shopping_lists")
    items = relationship("ShoppingItem", back_populates="list", cascade="all, delete-orphan")


class ShoppingItem(Base):
    __tablename__ = 'shopping_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey('shopping_lists.id', ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    quantity = Column(String(100))
    is_checked = Column(Boolean, default=False)
    added_by = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    list = relationship("ShoppingList", back_populates="items")


class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20))
    title = Column(String(255), nullable=False)
    time = Column(String(5))
    days = Column(String(50))
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reminders")


class Activity(Base):
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)
    duration = Column(Integer)
    distance = Column(Float)
    calories_burned = Column(Float)
    steps = Column(Integer, default=0)
    datetime = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(20), default='manual')
    
    user = relationship("User", back_populates="activities")
