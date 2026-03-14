# services/feedback_collector.py

"""
Сбор обратной связи от пользователей для улучшения модели.
"""

import logging
from typing import Dict, List
from database.db import get_session
from sqlalchemy import text

logger = logging.getLogger(__name__)


async def collect_feedback(
    telegram_id: int,
    meal_id: int,
    original_prediction: Dict,
    user_corrections: Dict
):
    """
    Собирает обратную связь от пользователя для улучшения модели.
    
    Args:
        telegram_id: ID пользователя в Telegram
        meal_id: ID приёма пищи в БД
        original_prediction: Исходные данные от AI
        user_corrections: Исправления пользователя
    """
    try:
        async with get_session() as session:
            # Создаём таблицу если не существует
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS feedback_data (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT,
                    meal_id INTEGER,
                    original_dish VARCHAR(255),
                    corrected_dish VARCHAR(255),
                    original_weights JSONB,
                    corrected_weights JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Сохраняем фидбек
            await session.execute(text("""
                INSERT INTO feedback_data 
                (telegram_id, meal_id, original_dish, corrected_dish, original_weights, corrected_weights)
                VALUES 
                (:telegram_id, :meal_id, :original_dish, :corrected_dish, :original_weights, :corrected_weights)
            """), {
                "telegram_id": telegram_id,
                "meal_id": meal_id,
                "original_dish": original_prediction.get("dish_name", ""),
                "corrected_dish": user_corrections.get("corrected_dish", ""),
                "original_weights": str(original_prediction.get("ingredients", [])),
                "corrected_weights": str(user_corrections.get("corrected_weights", []))
            })
            
            await session.commit()
            logger.info(f"📊 Feedback collected for meal {meal_id}")
            
    except Exception as e:
        logger.error(f"❌ Feedback collection error: {e}")


async def get_calibration_data(telegram_id: int) -> Dict:
    """
    Получает данные для калибровки на основе истории пользователя.
    """
    try:
        async with get_session() as session:
            result = await session.execute(text("""
                SELECT original_weights, corrected_weights 
                FROM feedback_data 
                WHERE telegram_id = :telegram_id 
                ORDER BY created_at DESC 
                LIMIT 50
            """), {"telegram_id": telegram_id})
            
            rows = result.fetchall()
            
            if not rows:
                return {"weight_multiplier": 1.0}
            
            # Анализируем коррекции
            total_ratio = 0
            count = 0
            
            for original, corrected in rows:
                # Парсим JSON и сравниваем веса
                # Упрощённая логика для примера
                pass
            
            multiplier = 1.0 + (total_ratio / count) if count > 0 else 1.0
            return {"weight_multiplier": multiplier}
            
    except Exception as e:
        logger.error(f"❌ Calibration data error: {e}")
        return {"weight_multiplier": 1.0}
