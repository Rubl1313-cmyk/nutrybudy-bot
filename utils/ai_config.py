"""
🤖 AI Configuration Manager - Настройки AI компонентов NutriBuddy
✨ Централизованное управление всеми AI параметрами
🎯 Легкая конфигурация и тестирование
"""

import os
from typing import Dict, Optional

class AIConfig:
    """Конфигурация AI компонентов"""
    
    # OpenWeatherMap API ключ
    WEATHER_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
    
    # WeatherAPI ключ (запасной)
    WEATHERAPI_KEY = os.getenv('WEATHERAPI_KEY', 'demo_key')
    
    # Настройки Enhanced AI Parser
    PARSER_CONFIDENCE_THRESHOLD = 70  # Порог уверенности для запроса уточнения
    PARSER_MAX_CONTEXT_HISTORY = 5  # Максимальное количество сообщений в истории
    
    # Настройки Enhanced Nutrition Calculator
    NUTRITION_MIN_CALORIES = 800  # Минимальные калории
    NUTRITION_MAX_CALORIES = 10000  # Максимальные калории
    NUTRITION_MIN_PROTEIN = 30  # Минимальный белок
    NUTRITION_MAX_PROTEIN = 500  # Максимальный белок
    
    # Настройки Climate Manager
    CLIMATE_CACHE_DURATION = 3600  # Длительность кэша погоды в секундах
    CLIMATE_FALLBACK_CITY = 'Москва'  # Город по умолчанию
    
    # Настройки AI Integration Manager
    INTEGRATION_MAX_ACTIONS = 10  # Максимальное количество действий за запрос
    INTEGRATION_TIMEOUT = 30  # Таймаут обработки в секундах
    
    # Настройки Enhanced Universal Handler
    HANDLER_MAX_HISTORY = 10  # Максимальная история диалога
    HANDLER_SEMANTIC_VALIDATION = True  # Включить семантическую валидацию
    
    @classmethod
    def get_weather_config(cls) -> Dict:
        """Получает конфигурацию погодных сервисов"""
        return {
            'openweathermap_key': cls.WEATHER_API_KEY,
            'weatherapi_key': cls.WEATHERAPI_KEY,
            'cache_duration': cls.CLIMATE_CACHE_DURATION,
            'fallback_city': cls.CLIMATE_FALLBACK_CITY
        }
    
    @classmethod
    def get_parser_config(cls) -> Dict:
        """Получает конфигурацию парсера"""
        return {
            'confidence_threshold': cls.PARSER_CONFIDENCE_THRESHOLD,
            'max_context_history': cls.PARSER_MAX_CONTEXT_HISTORY
        }
    
    @classmethod
    def get_nutrition_config(cls) -> Dict:
        """Получает конфигурацию калькулятора нутриентов"""
        return {
            'min_calories': cls.NUTRITION_MIN_CALORIES,
            'max_calories': cls.NUTRITION_MAX_CALORIES,
            'min_protein': cls.NUTRITION_MIN_PROTEIN,
            'max_protein': cls.NUTRITION_MAX_PROTEIN
        }
    
    @classmethod
    def get_integration_config(cls) -> Dict:
        """Получает конфигурацию интеграции"""
        return {
            'max_actions': cls.INTEGRATION_MAX_ACTIONS,
            'timeout': cls.INTEGRATION_TIMEOUT
        }
    
    @classmethod
    def get_handler_config(cls) -> Dict:
        """Получает конфигурацию обработчика"""
        return {
            'max_history': cls.HANDLER_MAX_HISTORY,
            'semantic_validation': cls.HANDLER_SEMANTIC_VALIDATION
        }
    
    @classmethod
    def validate_config(cls) -> Dict:
        """Валидирует конфигурацию"""
        issues = []
        
        # Проверяем API ключи
        if not cls.WEATHER_API_KEY:
            issues.append("Отсутствует OpenWeatherMap API ключ")
        
        # Проверяем пороги
        if cls.NUTRITION_MIN_CALORIES >= cls.NUTRITION_MAX_CALORIES:
            issues.append("Некорректные пороги калорий")
        
        if cls.PARSER_CONFIDENCE_THRESHOLD < 0 or cls.PARSER_CONFIDENCE_THRESHOLD > 100:
            issues.append("Некорректный порог уверенности парсера")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @classmethod
    def get_all_config(cls) -> Dict:
        """Получает всю конфигурацию"""
        return {
            'weather': cls.get_weather_config(),
            'parser': cls.get_parser_config(),
            'nutrition': cls.get_nutrition_config(),
            'integration': cls.get_integration_config(),
            'handler': cls.get_handler_config(),
            'validation': cls.validate_config()
        }

# Создаем экземпляр конфигурации
ai_config = AIConfig()
