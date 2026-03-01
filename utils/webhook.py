"""
Утилиты для управления вебхуком Telegram Bot
"""

import logging
from aiogram import Bot
from typing import Optional

logger = logging.getLogger(__name__)


async def get_webhook_info(bot: Bot) -> Optional[dict]:
    """Получает информацию о текущем вебхуке"""
    try:
        info = await bot.get_webhook_info()
        return {
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections
        }
    except Exception as e:
        logger.error(f"Failed to get webhook info: {e}")
        return None


async def set_webhook(bot: Bot, url: str, allowed_updates: Optional[list] = None) -> bool:
    """Устанавливает вебхук"""
    try:
        await bot.set_webhook(
            url=url,
            allowed_updates=allowed_updates,
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to: {url}")
        return True
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return False


async def delete_webhook(bot: Bot) -> bool:
    """Удаляет вебхук"""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted")
        return True
    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
        return False


async def validate_webhook(bot: Bot, expected_url: str) -> bool:
    """Проверяет, соответствует ли вебхук ожидаемому URL"""
    info = await get_webhook_info(bot)
    if not info:
        return False
    
    is_valid = info["url"] == expected_url
    if not is_valid:
        logger.warning(f"Webhook mismatch: expected {expected_url}, got {info['url']}")
    
    return is_valid
