"""
Модели базы данных для NutriBuddy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    weight = Column(Float)
    height = Column(Float)
    age = Column(Integer)
    gender = Column(String)  # male/female
    activity_level = Column(String)  # low/medium/high
    goal = Column(String)  # lose/maintain/gain
    city = Column(String)
    daily_water_goal = Column(Float)
    daily_calorie_goal = Column(Float)
    daily_protein_goal = Column(Float)
    daily_fat_goal = Column(Float)
    daily_carbs_goal = Column(Float)
    reminder_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    water_entries = relationship("WaterEntry", back_populates="user", cascade="all, delete-orphan")
    weight_entries = relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    shopping_lists = relationship("ShoppingList", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")


class Meal(Base):
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    meal_type = Column(String)  # breakfast/lunch/dinner/snack
    datetime = Column(DateTime, default=datetime.utcnow)
    total_calories = Column(Float)
    total_protein = Column(Float)
    total_fat = Column(Float)
    total_carbs = Column(Float)
    photo_url = Column(String)
    ai_description = Column(Text)
    
    user = relationship("User", back_populates="meals")
    foods = relationship("FoodItem", back_populates="meal", cascade="all, delete-orphan")


class FoodItem(Base):
    __tablename__ = 'food_items'
    
    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey('meals.id', ondelete="CASCADE"))
    name = Column(String)
    weight = Column(Float)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)
    barcode = Column(String)
    
    meal = relationship("Meal", back_populates="foods")


class WaterEntry(Base):
    __tablename__ = 'water_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    amount = Column(Float)
    datetime = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="water_entries")


class WeightEntry(Base):
    __tablename__ = 'weight_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    weight = Column(Float)
    datetime = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="weight_entries")


class ShoppingList(Base):
    __tablename__ = 'shopping_lists'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="shopping_lists")
    items = relationship("ShoppingItem", back_populates="list", cascade="all, delete-orphan")


class ShoppingItem(Base):
    __tablename__ = 'shopping_items'
    
    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey('shopping_lists.id', ondelete="CASCADE"))
    name = Column(String)
    quantity = Column(String)
    is_checked = Column(Boolean, default=False)
    added_by = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    list = relationship("ShoppingList", back_populates="items")


class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    type = Column(String)  # meal/water/weight/custom
    title = Column(String)
    time = Column(String)  # "HH:MM"
    days = Column(String)  # "mon,tue,wed" или "daily"
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reminders")


class Activity(Base):
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    activity_type = Column(String)  # walking/running/cycling/gym
    duration = Column(Integer)  # minutes
    distance = Column(Float)  # km
    calories_burned = Column(Float)
    steps = Column(Integer)
    datetime = Column(DateTime, default=datetime.utcnow)
    source = Column(String)  # manual/apple_watch/google_fit
    
    user = relationship("User", back_populates="activities")
