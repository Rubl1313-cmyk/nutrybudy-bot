"""
Ğ�Ñ‡Ğ¸Ñ�Ñ‚ĞºĞ° ÑƒÑ�Ñ‚Ğ°Ñ€ĞµĞ²ÑˆĞ¸Ñ… Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… FSM
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from typing import List

logger = logging.getLogger(__name__)

class FSMCleanupService:
    """Ğ¡ĞµÑ€Ğ²Ğ¸Ñ� Ğ¾Ñ‡Ğ¸Ñ�Ñ‚ĞºĞ¸ ÑƒÑ�Ñ‚Ğ°Ñ€ĞµĞ²ÑˆĞ¸Ñ… Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… FSM"""
    
    def __init__(self, storage: RedisStorage, ttl_seconds: int = 3600):
        self.storage = storage
        self.ttl = ttl_seconds
    
    async def cleanup_expired_photo_data(self, state: FSMContext):
        """Ğ�Ñ‡Ğ¸Ñ‰Ğ°ĞµÑ‚ ÑƒÑ�Ñ‚Ğ°Ñ€ĞµĞ²ÑˆĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ° Ñ„Ğ¾Ñ‚Ğ¾"""
        try:
            data = await state.get_data()
            photo_analysis = data.get('photo_analysis', {})
            
            if not photo_analysis:
                return
            
            current_time = datetime.now(timezone.utc)
            expired_keys = []
            
            for analysis_id, analysis_data in photo_analysis.items():
                # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ²Ñ€ĞµĞ¼Ñ� Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ½Ğ¸Ñ� Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
                created_at = analysis_data.get('created_at')
                if not created_at:
                    continue
                
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
                if current_time - created_at > timedelta(seconds=self.ttl):
                    expired_keys.append(analysis_id)
            
            # Ğ£Ğ´Ğ°Ğ»Ñ�ĞµĞ¼ ÑƒÑ�Ñ‚Ğ°Ñ€ĞµĞ²ÑˆĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ
            if expired_keys:
                for key in expired_keys:
                    del photo_analysis[key]
                    logger.info(f"ğŸ§¹ Cleaned up expired photo analysis: {key}")
                
                await state.update_data(photo_analysis=photo_analysis)
                logger.info(f"ğŸ§¹ Cleaned up {len(expired_keys)} expired photo analyses")
        
        except Exception as e:
            logger.error(f"Error cleaning up photo data: {e}")
    
    async def cleanup_all_expired_data(self, storage: RedisStorage):
        """Ğ�Ñ‡Ğ¸Ñ‰Ğ°ĞµÑ‚ Ğ²Ñ�Ğµ ÑƒÑ�Ñ‚Ğ°Ñ€ĞµĞ²ÑˆĞ¸Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ FSM"""
        try:
            # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ²Ñ�Ğµ ĞºĞ»Ñ�Ñ‡Ğ¸ Ğ¸Ğ· Redis
            keys = await storage.redis.keys("fsm:*")
            
            current_time = datetime.now(timezone.utc)
            cleaned_count = 0
            
            for key in keys:
                try:
                    data = await storage.redis.get(key)
                    if not data:
                        continue
                    
                    # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ²Ñ€ĞµĞ¼Ñ� Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½ĞµĞ³Ğ¾ Ğ¾Ğ±Ğ½Ğ¾Ğ²Ğ»ĞµĞ½Ğ¸Ñ�
                    ttl = await storage.redis.ttl(key)
                    if ttl == -1:  # Ğ�ĞµÑ‚ TTL
                        # Ğ£Ñ�Ñ‚Ğ°Ğ½Ğ°Ğ²Ğ»Ğ¸Ğ²Ğ°ĞµĞ¼ TTL ĞµÑ�Ğ»Ğ¸ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ½ĞµÑ‚ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ Ñ‡Ğ°Ñ�Ğ°
                        await storage.redis.expire(key, self.ttl)
                        cleaned_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing key {key}: {e}")
                    continue
            
            if cleaned_count > 0:
                logger.info(f"ğŸ§¹ Set TTL for {cleaned_count} FSM keys")
        
        except Exception as e:
            logger.error(f"Error in FSM cleanup: {e}")

# Ğ“Ğ»Ğ¾Ğ±Ğ°Ğ»ÑŒĞ½Ğ°Ñ� Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ñ� Ğ´Ğ»Ñ� Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´Ğ¸Ñ‡ĞµÑ�ĞºĞ¾Ğ¹ Ğ¾Ñ‡Ğ¸Ñ�Ñ‚ĞºĞ¸
async def periodic_fsm_cleanup(storage: RedisStorage):
    """ĞŸĞµÑ€Ğ¸Ğ¾Ğ´Ğ¸Ñ‡ĞµÑ�ĞºĞ°Ñ� Ğ¾Ñ‡Ğ¸Ñ�Ñ‚ĞºĞ° FSM Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…"""
    cleanup_service = FSMCleanupService(storage)
    
    while True:
        try:
            await cleanup_service.cleanup_all_expired_data(storage)
            await asyncio.sleep(300)  # ĞšĞ°Ğ¶Ğ´Ñ‹Ğµ 5 Ğ¼Ğ¸Ğ½ÑƒÑ‚
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")
            await asyncio.sleep(60)  # ĞŸÑ€Ğ¸ Ğ¾ÑˆĞ¸Ğ±ĞºĞµ Ğ¶Ğ´ĞµĞ¼ 1 Ğ¼Ğ¸Ğ½ÑƒÑ‚Ñƒ
