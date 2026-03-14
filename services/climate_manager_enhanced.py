"""
🌤️ Улучшенный AI-менеджер климата NutriBuddy
✨ Интеграция с реальными погодными API
🎯 AI-адаптация рекомендаций на основе погодных данных
"""

import logging
import os
import json
from typing import Dict, Optional, Any
import aiohttp
import asyncio
from datetime import datetime, timezone
from services.ai_engine_manager import ai

logger = logging.getLogger(__name__)

class EnhancedClimateManager:
    """Улучшенный менеджер климата с реальными данными о погоде"""
    
    def __init__(self):
        self.ai = ai
        self.weather_api_key = os.getenv('OPENWEATHERMAP_API_KEY')  # API ключ из переменных окружения (унифицировано)
        self.weatherapi_key = os.getenv('WEATHERAPI_KEY')  # Альтернативный API ключ
        self.weather_cache = {}
        self.cache_duration = 3600  # 1 час кэширования
    
    async def get_weather_data(
        self,
        city: str,
        country_code: str = None
    ) -> Dict:
        """
        Получает реальные данные о погоде из API
        
        Поддерживаемые API:
        - OpenWeatherMap (основной)
        - WeatherAPI (запасной)
        """
        
        # Проверяем кэш
        cache_key = f"{city}_{country_code or ''}"
        if cache_key in self.weather_cache:
            cached_data = self.weather_cache[cache_key]
            if (datetime.now().timestamp() - cached_data['timestamp']) < self.cache_duration:
                logger.info(f"🌤️ Using cached weather data for {city}")
                return cached_data['data']
        
        # Пробуем получить данные из OpenWeatherMap
        weather_data = await self._get_openweather_data(city, country_code)
        
        if not weather_data:
            # Запасной вариант: WeatherAPI
            weather_data = await self._get_weatherapi_data(city, country_code)
        
        if weather_data:
            # Сохраняем в кэш
            self.weather_cache[cache_key] = {
                'data': weather_data,
                'timestamp': datetime.now().timestamp()
            }
            
            logger.info(f"🌤️ Fresh weather data for {city}: {weather_data['temperature']}°C")
            return weather_data
        
        # Если все API недоступны, возвращаем базовые данные
        return self._get_fallback_weather(city)
    
    async def get_climate_recommendations(
        self,
        city: str,
        user_profile: Dict = None,
        current_season: str = None
    ) -> Dict:
        """
        Получает климатические рекомендации на основе реальной погоды
        
        Учитывает:
        - Температуру и влажность
        - Сезонные особенности
        - Профиль пользователя (возраст, цель, активность)
        - Время года
        """
        
        # Получаем данные о погоде
        weather_data = await self.get_weather_data(city)
        
        # Определяем сезон если не указан
        if not current_season:
            current_season = self._get_current_season()
        
        # Формируем контекст для AI
        context = {
            "weather": weather_data,
            "season": current_season,
            "user_profile": user_profile or {},
            "location": city
        }
        
        prompt = f"""
        Ты - эксперт по адаптации питания к климатическим условиям. Дай персонализированные рекомендации.
        
        🌤️ ТЕКУЩАЯ ПОГОДА:
        {self._format_weather_data(weather_data)}
        
        📅 СЕЗОН: {current_season}
        
        👤 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
        {self._format_user_profile(user_profile)}
        
        🧠 ФАКТОРЫ УЧЕТА:
        
        1. **Температурные корректировки:**
           - Жара (>25°C): +500-1000 мл воды, легкая пища, больше фруктов
           - Холод (<5°C): +300-500 ккал, теплая пища, больше жиров
           - Прохладно (5-15°C): стандартные нормы, умеренные калории
           - Комфортно (15-25°C): базовые рекомендации
           
        2. **Влажность и осадки:**
           - Высокая влажность (>70%): больше электролитов, меньше соли
           - Низкая влажность (<30%): больше воды, увлажняющие продукты
           - Дождь: витамин D, согревающая пища
           
        3. **Сезонные особенности:**
           - Весна: детокс, свежие овощи, витамины
           - Лето: гидратация, легкая пища, фрукты
           - Осень: иммунитет, теплые блюда, корнеплоды
           - Зима: калорийная пища, витамин C, согревающие специи
           
        4. **Активность и погода:**
           - Жара: тренировки утром/вечером, меньше интенсивности
           - Холод: больше разминка, защита от переохлаждения
           - Дождь: тренировки в помещении, альтернативные активности
           
        5. **Индивидуальные особенности:**
           - Возраст: дети и пожилые более чувствительны к погоде
           - Цель: похудение летом легче, зимой сложнее
           - Здоровье: хронические заболевания учитываются
           
        📋 ВЕРНИ JSON:
        {{
            "climate_analysis": {{
                "temperature_category": "жара|комфорт|прохладно|холод",
                "humidity_level": "высокая|средняя|низкая",
                "seasonal_impact": "описание сезонного влияния"
            }},
            "nutrition_adjustments": {{
                "calories": "корректировка калорий (+/- ккал)",
                "water": "корректировка воды (+/- мл)",
                "protein": "корректировка белка (+/- г)",
                "electrolytes": "потребность в электролитах"
            }},
            "food_recommendations": [
                {{
                    "category": "рекомендуемые продукты",
                    "examples": ["продукт 1", "продукт 2"],
                    "reason": "почему рекомендуется"
                }},
                {{
                    "category": "продукты для ограничения",
                    "examples": ["продукт 1", "продукт 2"],
                    "reason": "почему ограничить"
                }}
            ],
            "activity_recommendations": {{
                "best_times": "оптимальное время для активности",
                "intensity_adjustment": "корректировка интенсивности",
                "type_suggestions": ["тип активности 1", "тип активности 2"]
            }},
            "health_tips": [
                "совет по здоровью 1",
                "совет по здоровью 2"
            ],
            "warnings": [
                "предупреждение 1",
                "предупреждение 2"
            ]
        }}
        
        Примеры рекомендаций:
        
        Жара 30°C:
        - Увеличить потребление воды на 800 мл
        - Легкая пища: салаты, фрукты, кисломолочные
        - Ограничить тяжелую и жареную пищу
        - Тренировки до 10:00 и после 18:00
        
        Холод -5°C:
        - Добавить 300 ккал к рациону
        - Теплые блюда: супы, каши, горячие напитки
        - Больше жиров и сложных углеводов
        - Имбирь, корица, гвоздика в блюда
        """
        
        try:
            result = await ai.process_text(prompt, task_type="json", system_prompt="You are climate adaptation expert. Return JSON only.")
            
            logger.info(f"🌤️ Climate AI result success: {result.get('success', False)}")
            
            if result.get("success"):
                response_data = result.get("data", {})
                
                # Получаем текстовый контент из разных форматов ответа
                if isinstance(response_data, dict):
                    if "content" in response_data:
                        # Если content это dict, берем его как строку
                        content = response_data.get("content")
                        if isinstance(content, dict):
                            # Если content это dict с JSON структурой, используем его напрямую
                            if "intent" in content or "food_items" in content or "recommendations" in content:
                                import json
                                response_text = json.dumps(content)  # Конвертируем в JSON строку
                            else:
                                response_text = str(content)
                        else:
                            response_text = str(content)
                    else:
                        response_text = str(response_data)
                else:
                    response_text = str(response_data)
                
                # logger.info(f"🌤️ Climate AI response: {response_text[:200] if len(response_text) > 200 else response_text}...")  # Отключено для продакшена
                
                import re
                # Если response_text это dict с нужной структурой, используем его напрямую
                if isinstance(response_text, dict) and 'climate_adaptations' in response_text:
                    logger.info(f"🌤️ Climate parsed keys: {list(response_text.keys())}")
                    logger.info(f"🌤️ Climate recommendations generated for {city}")
                    return response_text
                
                # Если response_text это строка JSON с нужной структурой
                if isinstance(response_text, str) and response_text.startswith('{') and 'climate_adaptations' in response_text:
                    try:
                        parsed_data = json.loads(response_text)
                        logger.info(f"🌤️ Climate parsed keys: {list(parsed_data.keys())}")
                        logger.info(f"🌤️ Climate recommendations generated for {city}")
                        return parsed_data
                    except json.JSONDecodeError as e:
                        logger.error(f"🌤️ Climate JSON decode error: {e}")
                        return self._get_fallback_recommendations(weather_data)
                
                # Если response_text это dict но без climate_adaptations, ищем JSON в строковом представлении
                if isinstance(response_text, dict):
                    response_text = str(response_text)
                
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    try:
                        parsed_data = json.loads(json_match.group())
                        logger.info(f"🌤️ Climate parsed keys: {list(parsed_data.keys())}")
                        
                        logger.info(f"🌤️ Climate recommendations generated for {city}")
                        return parsed_data
                    except json.JSONDecodeError as e:
                        logger.error(f"🌤️ Climate JSON decode error: {e}")
                        logger.error(f"🌤️ Raw JSON: {json_match.group()}")
                        return self._get_fallback_recommendations(weather_data)
                else:
                    logger.warning("🌤️ Climate format invalid - no JSON found")
                    logger.warning(f"🌤️ Response text: {response_text}")
                    return self._get_fallback_recommendations(weather_data)
            else:
                error_msg = result.get("error", "Unknown error")
                logger.warning(f"🌤️ Climate AI failed: {error_msg}")
                return self._get_fallback_recommendations(weather_data)
                
        except Exception as e:
            logger.error(f"🌤️ Climate recommendations error: {e}")
            return self._get_fallback_recommendations(weather_data)
    
    async def _get_openweather_data(self, city: str, country_code: str = None) -> Optional[Dict]:
        """Получает данные из OpenWeatherMap API"""
        if not self.weather_api_key:
            logger.warning("🌤️ OpenWeatherMap API key not configured")
            return None
        
        try:
            # Формируем запрос
            location = f"{city},{country_code}" if country_code else city
            url = f"https://api.openweathermap.org/data/2.5/weather"
            
            params = {
                'q': location,
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': 'ru'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            'temperature': data['main']['temp'],
                            'feels_like': data['main']['feels_like'],
                            'humidity': data['main']['humidity'],
                            'pressure': data['main']['pressure'],
                            'description': data['weather'][0]['description'],
                            'wind_speed': data.get('wind', {}).get('speed', 0),
                            'visibility': data.get('visibility', 0) / 1000,  # в км
                            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                            'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                            'source': 'openweathermap'
                        }
                    else:
                        logger.warning(f"🌤️ OpenWeatherMap API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"🌤️ OpenWeatherMap API error: {e}")
            return None
    
    async def _get_weatherapi_data(self, city: str, country_code: str = None) -> Optional[Dict]:
        """Запасной вариант: WeatherAPI"""
        try:
            location = f"{city},{country_code}" if country_code else city
            url = f"https://api.weatherapi.com/v1/current.json"
            
            params = {
                'key': 'demo_key',  # Нужно заменить на реальный ключ
                'q': location,
                'lang': 'ru'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        current = data['current']
                        
                        return {
                            'temperature': current['temp_c'],
                            'feels_like': current['feelslike_c'],
                            'humidity': current['humidity'],
                            'pressure': current['pressure_mb'],
                            'description': current['condition']['text'],
                            'wind_speed': current['wind_kph'] / 3.6,  # конвертация в м/с
                            'visibility': current['vis_km'],
                            'source': 'weatherapi'
                        }
                    else:
                        logger.warning(f"🌤️ WeatherAPI error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"🌤️ WeatherAPI error: {e}")
            return None
    
    def _get_fallback_weather(self, city: str) -> Dict:
        """Запасной вариант если API недоступны"""
        # Базовые данные по крупным городам
        city_weather_map = {
            'москва': {'temperature': 10, 'humidity': 65, 'description': 'облачно'},
            'санкт-петербург': {'temperature': 8, 'humidity': 70, 'description': 'дождь'},
            'новосибирск': {'temperature': 5, 'humidity': 60, 'description': 'снег'},
            'екатеринбург': {'temperature': 7, 'humidity': 55, 'description': 'пасмурно'},
            'казань': {'temperature': 12, 'humidity': 68, 'description': 'ясно'},
        }
        
        city_lower = city.lower()
        if city_lower in city_weather_map:
            weather_data = city_weather_map[city_lower].copy()
            weather_data['source'] = 'fallback_map'
            return weather_data
        
        # Если город не найден, возвращаем средние данные
        return {
            'temperature': 15,
            'humidity': 60,
            'description': 'переменная облачность',
            'source': 'fallback_default'
        }
    
    def _get_fallback_recommendations(self, weather_data: Dict) -> Dict:
        """Базовые рекомендации если AI недоступен"""
        temp = weather_data.get('temperature', 20)
        
        if temp > 25:
            return {
                'climate_analysis': {'temperature_category': 'жара'},
                'nutrition_adjustments': {
                    'calories': '+200 ккал (на компенсацию пота)',
                    'water': '+800 мл',
                    'electrolytes': 'Повышенная потребность'
                },
                'food_recommendations': [
                    {'category': 'Рекомендуемые продукты', 'examples': ['огурцы', 'арбуз', 'кефир'], 'reason': 'Гидратация'},
                    {'category': 'Для ограничения', 'examples': ['жареное', 'жирное'], 'reason': 'Тяжелая пища'}
                ],
                'health_tips': ['Пейте больше воды', 'Избегайте солнца в пиковые часы']
            }
        elif temp < 5:
            return {
                'climate_analysis': {'temperature_category': 'холод'},
                'nutrition_adjustments': {
                    'calories': '+300 ккал',
                    'water': 'Стандартное количество',
                    'electrolytes': 'Стандартная потребность'
                },
                'food_recommendations': [
                    {'category': 'Рекомендуемые продукты', 'examples': ['супы', 'каши', 'горячие напитки'], 'reason': 'Согревание'},
                    {'category': 'Полезные добавки', 'examples': ['имбирь', 'корица', 'мед'], 'reason': 'Иммунитет'}
                ],
                'health_tips': ['Одевайтесь теплее', 'Укрепляйте иммунитет']
            }
        else:
            return {
                'climate_analysis': {'temperature_category': 'комфортно'},
                'nutrition_adjustments': {
                    'calories': 'Стандартная норма',
                    'water': 'Стандартная норма',
                    'electrolytes': 'Стандартная потребность'
                },
                'food_recommendations': [
                    {'category': 'Сбалансированное питание', 'examples': ['овощи', 'белки', 'крупы'], 'reason': 'Разнообразие'}
                ],
                'health_tips': ['Поддерживайте баланс питания', 'Регулярная активность']
            }
    
    def _get_current_season(self) -> str:
        """Определяет текущий сезон"""
        month = datetime.now().month
        
        if month in [12, 1, 2]:
            return 'зима'
        elif month in [3, 4, 5]:
            return 'весна'
        elif month in [6, 7, 8]:
            return 'лето'
        else:
            return 'осень'
    
    def _format_weather_data(self, weather_data: Dict) -> str:
        """Форматирует данные о погоде для промпта"""
        if not weather_data:
            return "Данные о погоде недоступны"
        
        formatted = []
        formatted.append(f"Температура: {weather_data.get('temperature', 'N/A')}°C")
        formatted.append(f"Ощущается как: {weather_data.get('feels_like', 'N/A')}°C")
        formatted.append(f"Влажность: {weather_data.get('humidity', 'N/A')}%")
        formatted.append(f"Описание: {weather_data.get('description', 'N/A')}")
        formatted.append(f"Источник: {weather_data.get('source', 'N/A')}")
        
        return '\n'.join(formatted)
    
    def _format_user_profile(self, user_profile: Dict) -> str:
        """Форматирует профиль пользователя для промпта"""
        if not user_profile:
            return "Профиль пользователя недоступен"
        
        formatted = []
        for key, value in user_profile.items():
            formatted.append(f"{key}: {value}")
        
        return '\n'.join(formatted)
    
    def clear_cache(self):
        """Очищает кэш погоды"""
        self.weather_cache.clear()
        logger.info("🌤️ Weather cache cleared")

# Создаем экземпляр улучшенного менеджера климата
enhanced_climate_manager = EnhancedClimateManager()
