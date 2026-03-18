"""
Модели данных NutriBuddy Bot
Базовые модели для работы с базой данных через SQLAlchemy
"""
from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

# Импортируем Base из db.py (основной класс для всех моделей)
from database.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)  # ID пользователя в Telegram
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
    daily_steps_goal = Column(Integer, default=10000)  # Цель по шагам по умолчанию
    daily_activity_goal = Column(Integer, default=300)  # Цель по активности в минутах по умолчанию
    reminder_enabled = Column(Boolean, default=True)
    timezone = Column(String(50), default='UTC')  # Часовой пояс пользователя (IANA формат)
    
    # Антропометрические данные для расширенного анализа
    neck_cm = Column(Float, nullable=True)          # Обхват шеи (женщины/бицепс мужчины)
    waist_cm = Column(Float, nullable=True)         # Обхват талии
    hip_cm = Column(Float, nullable=True)           # Обхват бедра
    wrist_cm = Column(Float, nullable=True)         # Обхват запястья
    bicep_cm = Column(Float, nullable=True)        # Обхват бицепса (мужчины/женщины)
    
    # Дополнительные антропометрические данные (опциональные)
    chest_cm = Column(Float, nullable=True)          # Обхват груди
    forearm_cm = Column(Float, nullable=True)        # Обхват предплечья
    calf_cm = Column(Float, nullable=True)           # Обхват голени
    shoulder_width_cm = Column(Float, nullable=True) # Ширина плеч
    hip_width_cm = Column(Float, nullable=True)      # Ширина таза
    
    # Целевые показатели состава тела
    goal_weight = Column(Float, nullable=True)      # Целевой вес
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Связи с другими таблицами
    food_entries = relationship("FoodEntry", back_populates="user", cascade="all, delete-orphan")
    water_entries = relationship("WaterEntry", back_populates="user", cascade="all, delete-orphan")
    drink_entries = relationship("DrinkEntry", back_populates="user", cascade="all, delete-orphan")
    weight_entries = relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    activity_entries = relationship("ActivityEntry", back_populates="user", cascade="all, delete-orphan")
    steps_entries = relationship("StepsEntry", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")

class FoodEntry(Base):
    __tablename__ = 'food_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    food_name = Column(String(255), nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fiber = Column(Float, default=0)
    sugar = Column(Float, default=0)
    sodium = Column(Float, default=0)
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    quantity = Column(Float, default=1)  # Количество порций
    unit = Column(String(20), default='шт')  # Единица измерения
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связь с пользователем
    user = relationship("User", back_populates="food_entries")

class WaterEntry(Base):
    __tablename__ = 'water_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    amount = Column(Float, nullable=False)  # в мл
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связь с пользователем
    user = relationship("User", back_populates="water_entries")

class DrinkEntry(Base):
    __tablename__ = 'drink_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    drink_name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)  # в мл
    calories = Column(Float, nullable=False)
    sugar = Column(Float, default=0)
    caffeine = Column(Float, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связь с пользователем
    user = relationship("User", back_populates="drink_entries")

class WeightEntry(Base):
    __tablename__ = 'weight_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    weight = Column(Float, nullable=False)  # в кг
    body_fat = Column(Float, nullable=True)  # % жировой массы
    muscle_mass = Column(Float, nullable=True)  # кг мышечной массы
    body_water = Column(Float, nullable=True)  # % воды в организме
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связь с пользователем
    user = relationship("User", back_populates="weight_entries")

class ActivityEntry(Base):
    __tablename__ = 'activity_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    activity_type = Column(String(50), nullable=False)  # walking, running, cycling, gym, etc.
    duration = Column(Integer, nullable=False)  # в минутах
    calories_burned = Column(Float, nullable=False)
    distance = Column(Float, nullable=True)  # в км
    intensity = Column(String(20), default='moderate')  # low, moderate, high
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связь с пользователем
    user = relationship("User", back_populates="activity_entries")

class StepsEntry(Base):
    __tablename__ = 'steps_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    steps_count = Column(Integer, nullable=False)
    source = Column(String(20), default='manual')  # manual, fitbit, apple_watch, etc.
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связь с пользователем
    user = relationship("User", back_populates="steps_entries")

class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=False)
    icon = Column(String(10), nullable=False)  # эмодзи для отображения
    category = Column(String(20), nullable=False)  # weight, nutrition, activity, streak
    condition_type = Column(String(20), nullable=False)  # weight_loss, calories_burned, steps_count, etc.
    condition_value = Column(Float, nullable=False)  # пороговое значение
    points = Column(Integer, default=10)  # очки за достижение
    is_secret = Column(Boolean, default=False)  # скрытые достижения
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserAchievement(Base):
    __tablename__ = 'user_achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    earned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связи
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")

class MealPlan(Base):
    __tablename__ = 'meal_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    date = Column(DateTime, nullable=False)
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    planned_foods = Column(Text, nullable=True)  # JSON с планируемыми блюдами
    actual_foods = Column(Text, nullable=True)  # JSON с фактически съеденным
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class DailyStats(Base):
    __tablename__ = 'daily_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    date = Column(DateTime, nullable=False)
    calories_consumed = Column(Float, default=0)
    protein_consumed = Column(Float, default=0)
    fat_consumed = Column(Float, default=0)
    carbs_consumed = Column(Float, default=0)
    water_consumed = Column(Float, default=0)
    steps_taken = Column(Integer, default=0)
    calories_burned = Column(Float, default=0)
    activity_minutes = Column(Integer, default=0)
    weight_change = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
