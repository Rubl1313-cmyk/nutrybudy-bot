"""
ĞœĞ¾Ğ´ĞµĞ»Ğ¸ Ğ±Ğ°Ğ·Ñ‹ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ´Ğ»Ñ� NutriBuddy
âœ… Ğ’Ñ�Ğµ Ğ¼Ğ¾Ğ´ĞµĞ»Ğ¸ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒÑ�Ñ‚ Base Ğ¸Ğ· database.db
"""
from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

# Ğ˜Ğ¼Ğ¿Ğ¾Ñ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Base Ğ¸Ğ· db.py (ĞµĞ´Ğ¸Ğ½Ñ‹Ğ¹ Ğ¸Ñ�Ñ‚Ğ¾Ñ‡Ğ½Ğ¸Ğº!)
from database.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)  # Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¾ Ğ½Ğ° BigInteger
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
    daily_steps_goal = Column(Integer, default=10000)  # Ğ¦ĞµĞ»ÑŒ Ğ¿Ğ¾ ÑˆĞ°Ğ³Ğ°Ğ¼ Ğ¿Ğ¾ ÑƒĞ¼Ğ¾Ğ»Ñ‡Ğ°Ğ½Ğ¸Ñ�
    daily_activity_goal = Column(Integer, default=300)  # Ğ¦ĞµĞ»ÑŒ Ğ¿Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ñ�Ğ¼ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ¿Ğ¾ ÑƒĞ¼Ğ¾Ğ»Ñ‡Ğ°Ğ½Ğ¸Ñ�
    reminder_enabled = Column(Boolean, default=True)
    timezone = Column(String(50), default='UTC')  # Ğ§Ğ°Ñ�Ğ¾Ğ²Ğ¾Ğ¹ Ğ¿Ğ¾Ñ�Ğ°Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� (IANA Ğ¤Ğ¾Ñ€Ğ¼Ğ°Ñ‚)
    
    # ĞŸĞ¾Ğ»Ñ� Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ğ¸ Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ğ¾Ğ³Ğ¾ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ°
    neck_cm = Column(Float, nullable=True)          # Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ ÑˆĞµĞ¸ (Ğ¶ĞµĞ½Ñ‰Ğ¸Ğ½Ñ‹/Ğ±Ğ¸Ñ†ĞµĞ¿Ñ� Ğ¼ÑƒĞ¶Ñ‡Ğ¸Ğ½Ñ‹)
    waist_cm = Column(Float, nullable=True)         # Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ñ‚Ğ°Ğ»Ğ¸Ğ¸
    hip_cm = Column(Float, nullable=True)           # Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±ĞµĞ´ĞµÑ€
    wrist_cm = Column(Float, nullable=True)         # Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ·Ğ°Ğ¿Ñ�Ñ�Ñ‚ÑŒÑ�
    bicep_cm = Column(Float, nullable=True)        # Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ±Ğ¸Ñ†ĞµĞ¿Ñ�Ğ° (Ğ¼ÑƒĞ¶Ñ‡Ğ¸Ğ½Ñ‹)
    
    # Ğ�Ğ¾Ğ²Ñ‹Ğµ Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ñ‹Ğµ Ğ°Ğ½Ñ‚Ñ€Ğ¾Ğ¿Ğ¾Ğ¼ĞµÑ‚Ñ€Ğ¸Ñ‡ĞµÑ�ĞºĞ¸Ğµ Ğ¿Ğ¾Ğ»Ñ� (Ğ¾Ğ¿Ñ†Ğ¸Ğ¾Ğ½Ğ°Ğ»ÑŒĞ½Ñ‹Ğµ)
    chest_cm = Column(Float, nullable=True)          # Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ñ€ÑƒĞ´Ğ¸
    forearm_cm = Column(Float, nullable=True)        # Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ¿Ñ€ĞµĞ´Ğ¿Ğ»ĞµÑ‡ÑŒÑ�
    calf_cm = Column(Float, nullable=True)           # Ğ�Ğ±Ñ…Ğ²Ğ°Ñ‚ Ğ³Ğ¾Ğ»ĞµĞ½Ğ¸
    shoulder_width_cm = Column(Float, nullable=True) # Ğ¨Ğ¸Ñ€Ğ¸Ğ½Ğ° Ğ¿Ğ»ĞµÑ‡
    hip_width_cm = Column(Float, nullable=True)      # Ğ¨Ğ¸Ñ€Ğ¸Ğ½Ğ° Ñ‚Ğ°Ğ·Ğ°
    
    # ĞšĞµÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ñ‹ ĞºĞ¾Ğ¼Ğ¿Ğ¾Ğ·Ğ¸Ñ†Ğ¸Ğ¸ Ñ‚ĞµĞ»Ğ°
    last_bodyfat = Column(Float, nullable=True)     # ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğ¹ % Ğ¶Ğ¸Ñ€Ğ°
    last_muscle_mass = Column(Float, nullable=True) # ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ñ�Ñ� Ğ¼Ñ‹ÑˆĞµÑ‡Ğ½Ğ°Ñ� Ğ¼Ğ°Ñ�Ñ�Ğ°
    last_body_water = Column(Float, nullable=True)  # ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ñ�Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ½Ğ°Ñ� Ğ²Ğ¾Ğ´Ğ°
    
    # Ğ¦ĞµĞ»ĞµĞ²Ñ‹Ğµ Ğ¿Ğ¾ĞºĞ°Ğ·Ğ°Ñ‚ĞµĞ»Ğ¸
    goal_weight = Column(Float, nullable=True)      # Ğ¦ĞµĞ»ĞµĞ²Ğ¾Ğ¹ Ğ²ĞµÑ�
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    drink_entries = relationship("DrinkEntry", back_populates="user", cascade="all, delete-orphan")
    # water_entries ÑƒĞ´Ğ°Ğ»ĞµĞ½Ñ‹ - Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ drink_entries Ğ´Ğ»Ñ� Ğ²Ñ�ĞµÑ… Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ĞµĞ¹
    weight_entries = relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    steps_entries = relationship("StepsEntry", back_populates="user", cascade="all, delete-orphan")
    
    # Ğ“ĞµĞ¹Ğ¼Ğ¸Ñ„Ğ¸ĞºĞ°Ñ†Ğ¸Ñ�
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    gamification = relationship("UserGamification", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Meal(Base):
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    meal_type = Column(String(20))
    datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
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

class DrinkEntry(Base):
    """Ğ£Ğ½Ğ¸Ğ²ĞµÑ€Ñ�Ğ°Ğ»ÑŒĞ½Ñ‹Ğµ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ¾ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ñ�Ñ… (Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¸ + Ğ²Ğ¾Ğ´Ğ° Ğ¸Ğ· ĞµĞ´Ñ‹)"""
    __tablename__ = 'drink_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, default="Ğ²Ğ¾Ğ´Ğ°")  # Ğ�Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ: "Ğ²Ğ¾Ğ´Ğ°", "Ñ�Ğ¾Ğº", "Ğ²Ğ¾Ğ´Ğ° Ğ¸Ğ· Ñ�ÑƒĞ¿Ğ° Ğ±Ğ¾Ñ€Ñ‰"
    volume_ml = Column(Float, nullable=False)                    # Ğ�Ğ±ÑŠÑ‘Ğ¼ Ğ² Ğ¼Ğ»
    calories = Column(Float, default=0.0)                        # ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ (Ğ´Ğ»Ñ� Ñ�Ğ¾ĞºĞ¾Ğ², Ñ‡Ğ°Ñ� Ñ� Ñ�Ğ°Ñ…Ğ°Ñ€Ğ¾Ğ¼)
    source = Column(String(20), default='drink')                # Ğ˜Ñ�Ñ‚Ğ¾Ñ‡Ğ½Ğ¸Ğº: 'drink' (Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº), 'food' (Ğ¸Ğ· ĞµĞ´Ñ‹)
    reference_id = Column(Integer, nullable=True)               # ID Ñ�Ğ²Ñ�Ğ·Ğ°Ğ½Ğ½Ğ¾Ğ¹ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ (meal_id Ğ´Ğ»Ñ� Ñ�ÑƒĞ¿Ğ°)
    datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="drink_entries")

# WaterEntry ÑƒĞ´Ğ°Ğ»ĞµĞ½Ğ° - Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ ĞµĞ´Ğ¸Ğ½ÑƒÑ� DrinkEntry Ğ´Ğ»Ñ� Ğ²Ñ�ĞµÑ… Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ĞµĞ¹

class WeightEntry(Base):
    __tablename__ = 'weight_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    weight = Column(Float, nullable=False)
    datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="weight_entries")

class Activity(Base):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)
    duration = Column(Integer)
    distance = Column(Float)
    calories_burned = Column(Float)
    steps = Column(Integer, default=0)
    datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    source = Column(String(20), default='manual')

    user = relationship("User", back_populates="activities")

class StepsEntry(Base):
    """ğŸ‘� Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ¾ ÑˆĞ°Ğ³Ğ°Ñ… Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
    __tablename__ = 'steps_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    steps_count = Column(Integer, nullable=False)
    datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    source = Column(String(20), default='manual')  # manual, fitness_tracker, etc.
    notes = Column(String(255))  # ĞŸÑ€Ğ¸Ğ¼ĞµÑ‡Ğ°Ğ½Ğ¸Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�

    user = relationship("User", back_populates="steps_entries")
