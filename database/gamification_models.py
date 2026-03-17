"""
Модели для геймификации
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime, timezone

class UserAchievement(Base):
    """Достижения пользователя"""
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(String(50), nullable=False)  # ID достижения из gamification.py
    earned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    points = Column(Integer, nullable=False)  # Очки за достижение
    
    # Связи
    user = relationship("User", back_populates="achievements")

class UserGamification(Base):
    """Статистика геймификации пользователя"""
    __tablename__ = 'user_gamification'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True, unique=True)
    total_points = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    max_streak = Column(Integer, default=0, nullable=False)
    meals_logged = Column(Integer, default=0, nullable=False)
    water_ml_total = Column(Integer, default=0, nullable=False)
    start_weight = Column(Float, nullable=True)
    current_weight = Column(Float, nullable=True)
    last_activity_date = Column(DateTime, nullable=True)
    early_breakfasts = Column(Integer, default=0, nullable=False)
    late_dinners = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Связи
    user = relationship("User", back_populates="gamification")

class AchievementHistory(Base):
    """История получения достижений"""
    __tablename__ = 'achievement_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(String(50), nullable=False)
    achievement_name = Column(String(100), nullable=False)
    achievement_description = Column(String(255), nullable=False)
    points_earned = Column(Integer, nullable=False)
    earned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Связи
    user = relationship("User")
