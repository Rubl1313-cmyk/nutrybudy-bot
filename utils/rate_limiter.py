"""
Rate limiting для защиты от спама
"""
import time
import asyncio
from typing import Dict, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Базовый класс rate limiting"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
    
    async def is_allowed(self, key: str) -> bool:
        """Проверка, разрешен ли запрос"""
        now = time.time()
        requests = self.requests[key]
        
        # Удаляем старые запросы
        while requests and requests[0] <= now - self.time_window:
            requests.popleft()
        
        # Проверяем лимит
        if len(requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {key}: {len(requests)}/{self.max_requests}")
            return False
        
        # Добавляем новый запрос
        requests.append(now)
        return True
    
    async def wait_if_needed(self, key: str):
        """Ожидание, если превышен лимит"""
        while not await self.is_allowed(key):
            await asyncio.sleep(1)

class UserRateLimiter(RateLimiter):
    """Rate limiting для пользователей"""
    
    def __init__(self):
        # Разные лимиты для разных типов запросов
        self.limits = {
            'ai_requests': RateLimiter(max_requests=10, time_window=60),  # 10 запросов в минуту
            'db_operations': RateLimiter(max_requests=100, time_window=60),  # 100 операций в минуту
            'photo_upload': RateLimiter(max_requests=5, time_window=60),  # 5 фото в минуту
            'profile_updates': RateLimiter(max_requests=3, time_window=60),  # 3 обновления профиля в минуту
        }
    
    async def is_allowed(self, user_id: int, request_type: str) -> bool:
        """Проверка лимита для конкретного типа запроса"""
        if request_type not in self.limits:
            return True
        
        key = f"{user_id}:{request_type}"
        return await self.limits[request_type].is_allowed(key)
    
    async def wait_if_needed(self, user_id: int, request_type: str):
        """Ожидание, если превышен лимит"""
        if request_type not in self.limits:
            return
        
        key = f"{user_id}:{request_type}"
        await self.limits[request_type].wait_if_needed(key)

class GlobalRateLimiter(RateLimiter):
    """Глобальный rate limiting для защиты от DDoS"""
    
    def __init__(self):
        super().__init__(max_requests=1000, time_window=60)  # 1000 запросов в минуту всего
    
    async def is_allowed(self) -> bool:
        """Проверка глобального лимита"""
        return await super().is_allowed("global")

# Глобальные экземпляры
user_rate_limiter = UserRateLimiter()
global_rate_limiter = GlobalRateLimiter()

async def check_rate_limit(user_id: int, request_type: str) -> bool:
    """Удобная функция для проверки rate limit"""
    return await user_rate_limiter.is_allowed(user_id, request_type)

async def wait_rate_limit(user_id: int, request_type: str):
    """Удобная функция для ожидания rate limit"""
    await user_rate_limiter.wait_if_needed(user_id, request_type)

def rate_limit_decorator(request_type: str):
    """Декоратор для rate limiting"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Извлекаем user_id из аргументов
            user_id = None
            for arg in args:
                if hasattr(arg, 'from_user'):
                    user_id = arg.from_user.id
                    break
                elif isinstance(arg, int):
                    user_id = arg
            
            if user_id and not await check_rate_limit(user_id, request_type):
                # Если превышен лимит, отправляем сообщение
                from aiogram.types import Message
                message = args[0] if args and isinstance(args[0], Message) else None
                if message:
                    await message.answer(
                        f"⚠️ Слишком много запросов! Подождите немного.\n"
                        f"Лимит: {user_rate_limiter.limits[request_type].max_requests} запросов в минуту",
                        parse_mode="HTML"
                    )
                return
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
