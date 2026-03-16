"""
handlers/food_logging.py
Обработчики для логирования еды (устаревший модуль)
"""
import logging
from aiogram import Router, F
from aiogram.types import Message

logger = logging.getLogger(__name__)

# Роутер отключен, так как функционал перенесен в universal.py
router = Router()

# NOTE: Этот модуль устарел и не используется.
# Весь функционал логирования еды перенесен в:
# - handlers/universal.py с LangChain агентом
# - services/langchain_agent.py с инструментами

# Если вам нужны специфические обработчики еды, добавьте их в universal.py
