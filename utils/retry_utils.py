"""
Утилиты для обработки таймаутов и повторных попыток
"""
import asyncio
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Кастомная ошибка таймаута"""
    pass

class RetryError(Exception):
    """Кастомная ошибка повторных попыток"""
    pass

def with_timeout(timeout_seconds: int = 60):
    """Декоратор для добавления таймаута к асинхронным функциям"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
        return wrapper
    return decorator

def with_retry(max_attempts: int = 3, delay_seconds: float = 1.0, backoff_factor: float = 2.0):
    """Декоратор для повторных попыток с экспоненциальным бэкоффом"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise RetryError(f"Failed after {max_attempts} attempts: {e}")
                    
                    # Логируем попытку
                    logger.warning(f"Function {func.__name__} attempt {attempt + 1} failed: {e}")
                    
                    # Ждем перед следующей попыткой
                    delay = delay_seconds * (backoff_factor ** attempt)
                    await asyncio.sleep(delay)
            
            # Эта строка недостижима, но для типа
            raise last_exception
        return wrapper
    return decorator

class CircuitBreaker:
    """Предохранитель для предотвращения каскадных сбоев"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs):
        """Вызов функции через предохранитель"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Проверка, можно ли попытаться сбросить предохранитель"""
        return (asyncio.get_event_loop().time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Обработка успешного вызова"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Обработка неудачного вызова"""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

# Глобальные предохранители для разных сервисов
ai_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
database_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=10.0)
