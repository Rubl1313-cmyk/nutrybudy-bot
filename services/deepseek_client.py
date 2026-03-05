"""
Клиент для обращения к собственному Cloudflare Worker.
Worker использует модель qwen2.5-coder-32b-instruct.
"""
import aiohttp
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

WORKER_URL = os.getenv("WORKER_URL")
WORKER_API_KEY = os.getenv("WORKER_API_KEY")

DEFAULT_SYSTEM_PROMPT = (
    "Ты — Джарвис, дружелюбный помощник по питанию и здоровому образу жизни. "
    "Отвечай на русском языке подробно и полно. Твой стиль — лёгкий, с юмором, но без излишнего панибратства. "
    "Можешь пошутить, посоветовать что-то смешное, но всегда оставайся полезным. "
    "Если просят рецепт, обязательно перечисли все ингредиенты и дай пошаговую инструкцию до конца. "
    "Завершай ответ всегда. "
)

async def ask_worker_ai(
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    model: str = "@cf/qwen/qwen2.5-coder-32b-instruct",
    temperature: float = 0.7,
    max_tokens: int = 3000   # увеличено до 3000 для рецептов
) -> Optional[Dict[str, Any]]:
    if not WORKER_URL or not WORKER_API_KEY:
        logger.error("❌ WORKER_URL or WORKER_API_KEY not set")
        return {"error": "Worker credentials not configured"}

    headers = {
        "Authorization": f"Bearer {WORKER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "systemPrompt": system_prompt,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Увеличиваем таймаут до 60 секунд
            async with session.post(WORKER_URL, headers=headers, json=payload, timeout=60) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "usage" in data:
                        logger.info(f"📊 Использовано токенов: {data['usage']}")
                    return data
                else:
                    error_text = await resp.text()
                    logger.error(f"Worker error {resp.status}: {error_text}")
                    return {"error": f"Worker error: {resp.status}"}
    except asyncio.TimeoutError:
        logger.error("❌ Worker request timeout after 60 seconds")
        return {"error": "Request timeout, please try again later"}
    except Exception as e:
        logger.exception("Worker request exception")
        return {"error": f"Exception: {str(e)}"}
