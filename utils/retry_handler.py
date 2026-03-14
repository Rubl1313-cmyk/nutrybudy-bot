"""
Утилиты для повторных попыток AI операций
"""
import logging
import asyncio
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

async def ai_operation_with_retry(
    operation: Callable,
    *args,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    **kwargs
) -> Any:
    """
    Выполняет AI операцию с несколькими попытками
    
    Args:
        operation: Асинхронная функция для выполнения
        max_retries: Максимальное количество попыток
        retry_delay: Задержка между попытками в секундах
        
    Returns:
        Результат операции или None если все попытки неудачны
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            result = await operation(*args, **kwargs)
            return result
        except Exception as e:
            last_error = e
            logger.warning(f"AI операция не удалась (попытка {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
    
    logger.error(f"AI операция провалена после {max_retries} попыток: {last_error}")
    return None
