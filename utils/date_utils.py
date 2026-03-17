"""
Утилиты для работы с датами в UTC
"""
import logging
from datetime import datetime, timezone, date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

def get_utc_now() -> datetime:
    """Получает текущее время в UTC"""
    return datetime.now(timezone.utc)

def get_utc_today() -> date:
    """Получает текущую дату в UTC"""
    return get_utc_now().date()

def get_utc_date_start(days_ago: int = 0) -> datetime:
    """Получает начало дня в UTC N дней назад"""
    return datetime.combine(
        get_utc_today() - timedelta(days=days_ago),
        datetime.min.time(),
        timezone.utc
    )

def get_utc_datetime_start(days_ago: int = 0) -> datetime:
    """Получает datetime начала дня N дней назад в UTC"""
    return get_utc_date_start(days_ago)

def format_utc_datetime(dt: datetime) -> str:
    """Форматирует datetime в UTC для логов"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def safe_date_comparison(date_field, target_date: date) -> bool:
    """Безопасное сравнение дат с учетом UTC"""
    # Преобразуем target_date в datetime UTC для сравнения
    target_datetime = datetime.combine(target_date, datetime.min.time(), timezone.utc)
    
    # Если date_field уже datetime, сравниваем напрямую
    if hasattr(date_field, 'date'):
        return date_field.date() == target_date
    else:
        return date_field == target_date
