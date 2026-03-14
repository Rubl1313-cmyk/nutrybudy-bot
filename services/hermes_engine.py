"""
🧠 Hermes Engine - для ВСЕГО кроме распознавания еды
✨ Умный ассистент, аналитика, персонализация, геймификация
🎯 Function calling для выполнения действий бота
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class HermesEngine:
    """Hermes Engine для умного ассистента и аналитики"""
    
    def __init__(self):
        self.name = "Hermes 2 Pro"
        self.version = "Mistral 7B"
        self.task_types = ["text_generation", "function_calling", "analytics", "personalization", "gamification"]
        
        # Cloudflare AI настройки
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.cloudflare_api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.hermes_model_id = os.getenv("HERMES_MODEL_ID", "@cf/meta/llama-3.1-8b-instruct")
        
        logger.info(f"🧠 Hermes: инициализирован с моделью {self.hermes_model_id}")
        
        if not all([self.cloudflare_account_id, self.cloudflare_api_token]):
            logger.warning("🧠 Hermes: отсутствуют Cloudflare учетные данные, будет использована эмуляция")
            self.use_real_api = False
        else:
            self.use_real_api = True
            logger.info("🧠 Hermes: Cloudflare AI настроен для реальной работы")
    
    async def process_text(self, prompt: str, system_prompt: str = None, task_type: str = "text_generation") -> Dict[str, Any]:
        """
        Обработать текстовый запрос
        
        Args:
            prompt: Запрос пользователя
            system_prompt: Системный промпт
            task_type: Тип задачи
            
        Returns:
            Dict с результатом обработки
        """
        try:
            logger.info(f"🧠 Hermes: обрабатываю запрос типа '{task_type}'")
            
            # Определяем системный промпт в зависимости от типа задачи
            if not system_prompt:
                system_prompt = self._get_system_prompt(task_type)
            
            # Выполняем запрос к Hermes
            response = await self._call_hermes(prompt, system_prompt, task_type)
            
            if response.get("success"):
                # Пост-обработка ответа
                processed_response = self._post_process_response(response.get("data", ""), task_type)
                
                result = {
                    "success": True,
                    "data": processed_response,
                    "task_type": task_type,
                    "processing_time": datetime.now().isoformat()
                }
                
                logger.info(f"🧠 Hermes: успешно обработан запрос типа '{task_type}'")
                return result
            else:
                return response
                
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка обработки {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    async def process_function_call(self, prompt: str, available_functions: List[Dict]) -> Dict[str, Any]:
        """
        Обработать запрос с function calling
        
        Args:
            prompt: Запрос пользователя
            available_functions: Список доступных функций
            
        Returns:
            Dict с результатом и вызванными функциями
        """
        try:
            logger.info(f"🧠 Hermes: обрабатываю function call")
            
            system_prompt = f"""
Ты - умный помощник NutriBuddy. У тебя есть доступ к функциям для помощи пользователю.

Доступные функции:
{json.dumps(available_functions, ensure_ascii=False, indent=2)}

Правила:
1. Анализируй запрос пользователя
2. Вызывай нужные функции для выполнения задачи
3. Отвечай в дружелюбном тоне
4. Не давай медицинских советов
5. Рекомендуй консультироваться с врачами

Формат ответа:
{{
  "content": "твой ответ пользователю",
  "function_calls": [
    {{
      "name": "имя_функции",
      "arguments": {{"параметр": "значение"}}
    }}
  ]
}}
"""
            
            response = await self._call_hermes(prompt, system_prompt, "function_calling")
            
            if response.get("success"):
                # Парсим function calls
                parsed_response = self._parse_function_response(response.get("data", ""))
                
                result = {
                    "success": True,
                    "data": parsed_response,
                    "task_type": "function_calling"
                }
                
                logger.info(f"🧠 Hermes: успешно обработан function call")
                return result
            else:
                return response
                
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка function call {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    async def get_analytics(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Получить аналитику и прогнозы
        
        Args:
            user_data: Данные пользователя
            
        Returns:
            Dict с аналитикой
        """
        try:
            logger.info(f"🧠 Hermes: генерирую аналитику")
            
            system_prompt = """
Ты - аналитик по питанию и здоровью. Проанализируй данные пользователя и дай рекомендации.

Проанализируй:
1. Тренды в питании
2. Достижение целей по КБЖУ
3. Рекомендации по улучшению
4. Прогноз на ближайшую неделю

Формат ответа:
{
  "trends": {
    "calories": "тренд калорий",
    "protein": "тренд белков", 
    "fat": "тренд жиров",
    "carbs": "тренд углеводов"
  },
  "goals_progress": {
    "calories_goal": "прогресс по калориям",
    "protein_goal": "прогресс по белкам",
    "water_goal": "прогресс по воде"
  },
  "recommendations": [
    "рекомендация 1",
    "рекомендация 2"
  ],
  "predictions": {
    "weight_forecast": "прогноз веса",
    "nutrition_tips": "советы по питанию"
  }
}
"""
            
            prompt = f"""
Проанализируй данные пользователя:
{json.dumps(user_data, ensure_ascii=False, indent=2)}

Дай подробную аналитику и рекомендации.
"""
            
            response = await self._call_hermes(prompt, system_prompt, "analytics")
            
            if response.get("success"):
                parsed_response = self._parse_json_response(response.get("data", ""))
                
                result = {
                    "success": True,
                    "data": parsed_response,
                    "task_type": "analytics"
                }
                
                logger.info(f"🧠 Hermes: успешно сгенерирована аналитика")
                return result
            else:
                return response
                
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка аналитики {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    async def _call_hermes(self, prompt: str, system_prompt: str, task_type: str) -> Dict[str, Any]:
        """Вызов Hermes через Cloudflare Workers AI"""
        try:
            if self.use_real_api:
                return await self._call_cloudflare_ai(prompt, system_prompt, task_type)
            else:
                logger.warning("🧠 Hermes: используем эмуляцию (нет Cloudflare ключей)")
                return await self._fallback_emulation(task_type, prompt)
                
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка вызова {e}")
            return await self._fallback_emulation(task_type, prompt)
    
    async def _call_cloudflare_ai(self, prompt: str, system_prompt: str, task_type: str) -> Dict[str, Any]:
        """Реальный вызов Cloudflare Workers AI"""
        try:
            import aiohttp
            
            # Формируем полный промпт
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            # Формируем запрос к Cloudflare Workers AI
            url = f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_account_id}/ai/run/{self.hermes_model_id}"
            
            headers = {
                "Authorization": f"Bearer {self.cloudflare_api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": full_prompt,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            logger.info(f"🧠 Hermes: отправляю запрос к Cloudflare AI ({task_type})")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Извлекаем ответ
                        content = result.get("result", {}).get("response", "")
                        
                        if content:
                            logger.info(f"🧠 Hermes: получен ответ от Cloudflare AI")
                            return {
                                "success": True,
                                "data": content
                            }
                        else:
                            logger.error("🧠 Hermes: пустой ответ от Cloudflare AI")
                            return {
                                "success": False,
                                "error": "Пустой ответ от AI",
                                "data": ""
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"🧠 Hermes: Cloudflare API error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"API error {response.status}: {error_text}",
                            "data": ""
                        }
                        
        except aiohttp.ClientError as e:
            logger.error(f"🧠 Hermes: ошибка сети Cloudflare AI {e}")
            return await self._fallback_emulation(task_type, prompt)
        except asyncio.TimeoutError:
            logger.error("🧠 Hermes: timeout Cloudflare AI")
            return await self._fallback_emulation(task_type, prompt)
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка Cloudflare AI {e}")
            return await self._fallback_emulation(task_type, prompt)
    
    async def _fallback_emulation(self, task_type: str, prompt: str = "") -> Dict[str, Any]:
        """Fallback эмуляция если Cloudflare AI недоступен"""
        try:
            await asyncio.sleep(0.5)  # Эмуляция задержки
            
            # В зависимости от типа задачи возвращаем разные ответы
            if task_type == "function_calling":
                mock_response = """
{
  "content": "Я помогу вам с этим! Давайте проанализируем вашу ситуацию.",
  "function_calls": [
    {
      "name": "get_user_progress",
      "arguments": {"period": "week"}
    }
  ]
}
"""
            elif task_type == "analytics":
                mock_response = """
{
  "trends": {
    "calories": "стабильное потребление в пределах нормы",
    "protein": "недостаток белка, рекомендуется увеличить",
    "fat": "нормальный уровень жиров",
    "carbs": "избыток углеводов, рекомендуется снизить"
  },
  "goals_progress": {
    "calories_goal": "85% выполнения дневной цели",
    "protein_goal": "70% выполнения дневной цели",
    "water_goal": "95% выполнения дневной цели"
  },
  "recommendations": [
    "Увеличить потребление белка на 20-30г в день",
    "Снизить количество быстрых углеводов",
    "Добавить больше овощей в рацион"
  ],
  "predictions": {
    "weight_forecast": "При сохранении текущего режима вес останется стабильным",
    "nutrition_tips": "Рекомендуется добавить белковые перекусы"
  }
}
"""
            elif task_type == "json":
                # Проверяем контекст для определения типа ответа
                if "climate" in prompt or "weather" in prompt or "temperature" in prompt:
                    mock_response = """
{
  "climate_adaptations": {
    "temperature_adjustments": "Увеличить калории на 200-300 ккал в холодную погоду",
    "food_recommendations": [
      "Теплые супы и горячие блюда",
      "Больше жиров и сложных углеводов",
      "Имбирь, корица, гвоздика в блюда"
    ],
    "hydration_tips": "Теплые напитки, избегать ледяной воды",
    "activity_recommendations": "Интенсивная тренировка для согрева"
  },
  "weather_impact": {
    "metabolism_boost": 15,
    "calorie_needs": "+250 ккал",
    "risk_factors": ["Обморожение", "Гипотермия"]
  }
}
"""
                elif "nutrition" in prompt or "calories" in prompt or "protein" in prompt or "кбжу" in prompt:
                    mock_response = """
{
  "daily_calories": 2000,
  "protein": 120,
  "fat": 65,
  "carbs": 250,
  "water_ml": 2000,
  "adjustments": {
    "activity_multiplier": 1.2,
    "goal_adjustment": "-200 ккал для похудения",
    "metabolic_age": 25
  },
  "recommendations": [
    "Увеличить потребление белка на 20г",
    "Снизить количество быстрых углеводов",
    "Добавить больше овощей в рацион"
  ]
}
"""
                else:
                    # Для JSON задач возвращаем разные ответы в зависимости от контекста
                    mock_response = """
{
  "intent": "food",
  "confidence": 85,
  "entities": {
    "food_items": [
      {"name": "курица", "quantity": 200, "unit": "г"},
      {"name": "гречка", "quantity": 150, "unit": "г"}
    ]
  },
  "response": "Записал прием пищи: 200г курицы и 150г гречки",
  "actions": [{"type": "save_food", "data": {"meal_type": "обед"}}],
  "needs_clarification": false
}
"""
            else:
                mock_response = """
{
  "content": "Я понимаю ваш запрос. Давайте разберем ситуацию подробнее и найдем наилучшее решение для вас."
}
"""
            
            return {
                "success": True,
                "data": mock_response
            }
            
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка эмуляции {e}")
            return {
                "success": False,
                "error": f"Ошибка эмуляции: {e}",
                "data": ""
            }
    
    def _get_system_prompt(self, task_type: str) -> str:
        """Получить системный промпт для типа задачи"""
        prompts = {
            "text_generation": """
Ты - полезный помощник по питанию и здоровью NutriBuddy.
Отвечай кратко, по делу, дружелюбно.
Не давай медицинских советов - рекомендуй консультироваться с врачами.
""",
            "personalization": """
Ты - персональный ассистент по питанию.
Учитывай цели и предпочтения пользователя.
Давай персонализированные рекомендации.
""",
            "gamification": """
Ты - мотивационный помощник.
Поддерживай пользователя в достижении целей.
Используй игровой подход для мотивации.
""",
            "meal_plan": """
Ты - эксперт по питанию и диетолог.
Составляй детальные планы питания на основе данных пользователя.
Учитывай калорийность, цели, возраст, пол, активность.
Используй сезонные продукты и климатические особенности.
Включай подробные рецепты с ингредиентами и калорийностью.
""",
            "food_parsing": """
Ты - эксперт по распознаванию еды.
Анализируй текст о еде и извлекай точную информацию.
Определяй продукты, количество, единицы измерения.
Учитывай синонимы и разговорные названия.
""",
            "water_parsing": """
Ты - эксперт по гидратации.
Анализируй текст о потреблении воды.
Определяй точный объем в миллилитрах.
Учитывай разные ёмкости (кружка, стакан, бутылка).
""",
            "activity_parsing": """
Ты - эксперт по физической активности.
Анализируй текст о тренировках и активности.
Определяй тип активности, продолжительность, интенсивность.
Рассчитывай расход калорий.
""",
            "nutrition_calculation": """
Ты - диетолог и нутрициолог.
Рассчитывай нормы КБЖУ на основе данных пользователя.
Учитывай возраст, пол, вес, рост, активность, цели.
Давай точные рекомендации по калорийности.
""",
            "analytics": """
Ты - аналитик по питанию и здоровью.
Анализируй данные пользователя и давай рекомендации.
Определяй тренды, проблемы, достижения.
Формируй детальные отчеты с советами.
"""
        }
        
        return prompts.get(task_type, prompts["text_generation"])
    
    def _parse_function_response(self, response_text: str) -> Dict[str, Any]:
        """Парсинг ответа с function calls"""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx + 1]
                return json.loads(json_str)
            else:
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            logger.error(f"🧠 Hermes: ошибка парсинга function response {e}")
            return {
                "content": response_text,
                "function_calls": []
            }
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка обработки function response {e}")
            return {
                "content": response_text,
                "function_calls": []
            }
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Парсинг JSON ответа"""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx + 1]
                parsed_json = json.loads(json_str)
                return {
                    "content": parsed_json,
                    "type": "json",
                    "raw_text": response_text
                }
            else:
                # Пробуем распарсить весь текст как JSON
                parsed_json = json.loads(response_text)
                return {
                    "content": parsed_json,
                    "type": "json",
                    "raw_text": response_text
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"🧠 Hermes: ошибка парсинга JSON {e}")
            logger.error(f"🧠 Raw response: {response_text[:200]}...")
            return {
                "content": response_text,
                "type": "text",
                "error": f"JSON decode error: {e}"
            }
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка обработки JSON {e}")
            return {
                "content": response_text,
                "type": "text",
                "error": f"Processing error: {e}"
            }
    
    def _post_process_response(self, response_data: str, task_type: str) -> Dict[str, Any]:
        """Пост-обработка ответа"""
        try:
            if task_type == "function_calling":
                return self._parse_function_response(response_data)
            elif task_type == "analytics" or task_type == "json":
                return self._parse_json_response(response_data)
            else:
                return {
                    "content": response_data,
                    "type": "text"
                }
        except Exception as e:
            logger.error(f"🧠 Hermes: ошибка пост-обработки {e}")
            return {
                "content": response_data,
                "type": "text"
            }
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Информация о движке"""
        return {
            "name": self.name,
            "version": self.version,
            "task_types": self.task_types,
            "description": "Универсальный движок для умного ассистента и аналитики",
            "capabilities": [
                "Генерация текста",
                "Function calling",
                "Аналитика данных",
                "Персонализация",
                "Геймификация"
            ]
        }

# Глобальный экземпляр
hermes = HermesEngine()
