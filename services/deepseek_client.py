"""
Клиент для DeepSeek API.
Использует официальный API DeepSeek (platform.deepseek.com).
"""
import aiohttp
import os
import logging
from typing import Optional, Dict, Any, List
import json

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# Системный промпт по умолчанию (роль AI-помощника)
DEFAULT_SYSTEM_PROMPT = (
    "Ты — NutriBuddy AI, дружелюбный помощник по питанию, здоровью и организации. "
    "Твоя задача — помогать пользователю с вопросами о еде, тренировках, планировании, "
    "а также выполнять команды, такие как добавление в список покупок или предложение рецептов. "
    "Отвечай кратко, по делу, на русском языке. Если пользователь просит что-то сделать (например, "
    "'добавь в список молоко'), используй доступные инструменты (tools), чтобы выполнить действие. "
    "Если не знаешь — честно скажи, что не знаешь."
)

# Схемы для инструментов (function calling)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_to_shopping_list",
            "description": "Добавляет товары в список покупок пользователя",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Название товара"},
                                "quantity": {"type": "integer", "description": "Количество"},
                                "unit": {"type": "string", "description": "Единица измерения (шт, кг, л и т.д.)"}
                            },
                            "required": ["name", "quantity", "unit"]
                        },
                        "description": "Список товаров для добавления"
                    }
                },
                "required": ["items"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_recipe",
            "description": "Предлагает рецепт по заданным ингредиентам или запросу",
            "parameters": {
                "type": "object",
                "properties": {
                    "ingredients": {
                        "type": "string",
                        "description": "Ингредиенты или описание блюда"
                    }
                },
                "required": ["ingredients"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Получает текущую погоду в городе",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Название города"
                    }
                },
                "required": ["city"]
            }
        }
    },
    # можно добавить другие инструменты по необходимости
]


async def ask_deepseek(
    prompt: str,
    user_id: int = None,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    tools: List[Dict] = TOOLS
) -> Dict[str, Any]:
    """
    Отправляет запрос к DeepSeek и возвращает полный ответ, включая возможные вызовы инструментов.
    """
    if not DEEPSEEK_API_KEY:
        logger.error("❌ DEEPSEEK_API_KEY not set")
        return {"error": "API ключ не настроен"}

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",  # или deepseek-reasoner, deepseek-coder
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    # Добавляем инструменты, если нужно
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=payload, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    error_text = await resp.text()
                    logger.error(f"DeepSeek API error {resp.status}: {error_text}")
                    return {"error": f"Ошибка API: {resp.status}"}
    except asyncio.TimeoutError:
        logger.error("DeepSeek API timeout")
        return {"error": "Превышено время ожидания ответа."}
    except Exception as e:
        logger.exception("DeepSeek API exception")
        return {"error": f"Ошибка: {str(e)}"}
