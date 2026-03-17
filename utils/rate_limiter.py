"""
Rate limiting для защиты от спама
"""
import logging
import os
import time
from typing import Dict, Set, Optional
from collections import defaultdict, deque
import asyncio
from datetime import datetime, timedelta
from aiogram.types import Message

logger = logging.getLogger(__name__)

class RateLimiter:
    """Базовый класс rate limiting с потокобезопасностью"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
        self._locks = {}  # Блокировки для каждого ключа
    
    async def is_allowed(self, key: str) -> bool:
        """Проверка, разрешен ли запрос"""
        # Получаем или создаем блокировку для этого ключа
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        
        async with self._locks[key]:
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
    """Rate limiting для пользователей с настраиваемыми лимитами"""
    
    def __init__(self):
        # Читаем лимиты из переменных окружения
        self.limits = {
            'general': RateLimiter(
                max_requests=int(os.getenv('RATE_LIMIT_GENERAL_REQUESTS', '30')),  # 30 по умолчанию
                time_window=int(os.getenv('RATE_LIMIT_GENERAL_WINDOW', '60'))     # 60 секунд
            ),
            'ai_requests': RateLimiter(
                max_requests=int(os.getenv('RATE_LIMIT_AI_REQUESTS', '20')),  # 20 по умолчанию
                time_window=int(os.getenv('RATE_LIMIT_AI_WINDOW', '60'))     # 60 секунд
            ),
            'db_operations': RateLimiter(
                max_requests=int(os.getenv('RATE_LIMIT_DB_REQUESTS', '200')),
                time_window=int(os.getenv('RATE_LIMIT_DB_WINDOW', '60'))
            ),
            'photo_upload': RateLimiter(
                max_requests=int(os.getenv('RATE_LIMIT_PHOTO_REQUESTS', '10')),
                time_window=int(os.getenv('RATE_LIMIT_PHOTO_WINDOW', '60'))
            ),
            'profile_updates': RateLimiter(
                max_requests=int(os.getenv('RATE_LIMIT_PROFILE_REQUESTS', '5')),
                time_window=int(os.getenv('RATE_LIMIT_PROFILE_WINDOW', '60'))
            )
        }
        
        # Логируем установленные лимиты
        logger.info(f"Rate limits configured: General={self.limits['general'].max_requests}/min, "
                   f"AI={self.limits['ai_requests'].max_requests}/min, "
                   f"DB={self.limits['db_operations'].max_requests}/min, "
                   f"Photo={self.limits['photo_upload'].max_requests}/min, "
                   f"Profile={self.limits['profile_updates'].max_requests}/min")
    
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
