"""
Клиент для обращения к собственному Cloudflare Worker.
Worker использует модель qwen2.5-coder-32b-instruct.
"""
import aiohttp
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

WORKER_URL = os.getenv("WORKER_URL")           # URL вашего Worker, например https://nutribudy-ai.workers.dev
WORKER_API_KEY = os.getenv("WORKER_API_KEY")   # ключ, заданный в Worker

DEFAULT_SYSTEM_PROMPT = (
"Ты — Джарвис, дружелюбный помощник по питанию и здоровому образу жизни. Отвечай на русском языке подробно, но по делу. Если просят рецепт, давай полный рецепт со всеми ингредиентами и шагами, не сокращая."
)


async def ask_worker_ai(
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    model: str = "@cf/qwen/qwen2.5-coder-32b-instruct",  # ← новая модель
    temperature: float = 0.7,
    max_tokens: int = 3000
) -> Optional[Dict[str, Any]]:
    """
    Отправляет запрос к собственному Cloudflare Worker и возвращает ответ.
    """
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
            async with session.post(WORKER_URL, headers=headers, json=payload, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    error_text = await resp.text()
                    logger.error(f"Worker error {resp.status}: {error_text}")
                    return {"error": f"Worker error: {resp.status}"}
    except Exception as e:
        logger.exception("Worker request exception")
        return {"error": f"Exception: {str(e)}"}
