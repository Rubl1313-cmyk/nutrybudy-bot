"""
Конфигурация NutriBuddy Bot
"""
import os
from typing import Dict, Any

# Rate limiting
RATE_LIMIT_GENERAL_REQUESTS = int(os.getenv('RATE_LIMIT_GENERAL_REQUESTS', '30'))
RATE_LIMIT_GENERAL_WINDOW = int(os.getenv('RATE_LIMIT_GENERAL_WINDOW', '60'))

RATE_LIMIT_AI_REQUESTS = int(os.getenv('RATE_LIMIT_AI_REQUESTS', '20'))
RATE_LIMIT_AI_WINDOW = int(os.getenv('RATE_LIMIT_AI_WINDOW', '60'))

RATE_LIMIT_PHOTO_REQUESTS = int(os.getenv('RATE_LIMIT_PHOTO_REQUESTS', '10'))
RATE_LIMIT_PHOTO_WINDOW = int(os.getenv('RATE_LIMIT_PHOTO_WINDOW', '60'))

# Timeouts
AI_REQUEST_TIMEOUT = int(os.getenv('AI_REQUEST_TIMEOUT', '60'))
PHOTO_ANALYSIS_TIMEOUT = int(os.getenv('PHOTO_ANALYSIS_TIMEOUT', '30'))
VOICE_TRANSCRIPTION_TIMEOUT = int(os.getenv('VOICE_TRANSCRIPTION_TIMEOUT', '30'))

# Cache
FOOD_CACHE_TTL = int(os.getenv('FOOD_CACHE_TTL', '300'))
FOOD_CACHE_LIMIT = int(os.getenv('FOOD_CACHE_LIMIT', '200'))

# FSM cleanup
FSM_DATA_TTL = int(os.getenv('FSM_DATA_TTL', '3600'))  # 1 час
