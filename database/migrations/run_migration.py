"""
Ğ¡ĞºÑ€Ğ¸Ğ¿Ñ‚ Ğ´Ğ»Ñ� Ğ·Ğ°Ğ¿ÑƒÑ�ĞºĞ° Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ğ¸ Ğ±Ğ°Ğ·Ñ‹ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
"""
import asyncio
import logging
from database.migrations.upgrade_to_drink_entries import upgrade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Ğ—Ğ°Ğ¿ÑƒÑ�Ğº Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ğ¸"""
    try:
        logger.info("ğŸ”„ Ğ�Ğ°Ñ‡Ğ¸Ğ½Ğ°ĞµĞ¼ Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ñ� water_entries â†’ drink_entries...")
        await upgrade()
        logger.info("âœ… ĞœĞ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ñ� ÑƒÑ�Ğ¿ĞµÑˆĞ½Ğ¾ Ğ·Ğ°Ğ²ĞµÑ€ÑˆĞµĞ½Ğ°!")
    except Exception as e:
        logger.error(f"â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ¼Ğ¸Ğ³Ñ€Ğ°Ñ†Ğ¸Ğ¸: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
