"""
📸 Llama Vision Engine - ТОЛЬКО для распознавания еды по фото
✨ Специализированный на анализе изображений с продуктами
🎯 Возвращает структурированные данные о блюде с КБЖУ
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class LlamaVisionEngine:
    """Llama Vision Engine для распознавания еды по фото"""
    
    def __init__(self):
        self.name = "Llama Vision"
        self.version = "3.2 11B Vision"
        self.task_types = ["food_recognition"]
        
        # Cloudflare AI настройки
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.cloudflare_api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.model_id = os.getenv("LLAMA_VISION_MODEL_ID", "@cf/meta/llama-3.2-11b-vision-instruct")
        
        logger.info(f"📸 Llama Vision: инициализирован с моделью {self.model_id}")
        
        if not all([self.cloudflare_account_id, self.cloudflare_api_token]):
            logger.error("📸 Llama Vision: отсутствуют Cloudflare учетные данные - реальный AI недоступен")
            self.use_real_api = False
            raise ValueError("Cloudflare credentials required for real AI operation")
        else:
            self.use_real_api = True
            logger.info("📸 Llama Vision: Cloudflare AI настроен для реальной работы")
        
    async def recognize_food(self, image_data: bytes) -> Dict[str, Any]:
        """
        Распознать еду на фото и рассчитать КБЖУ
        
        Args:
            image_data: Байты изображения
            
        Returns:
            Dict с результатом распознавания и КБЖУ
        """
        try:
            logger.info(f"📸 Llama Vision: начинаю распознавание еды")
            
            # Системный промпт для распознавания еды
            system_prompt = """
Ты - эксперт по анализу еды на фотографиях. Твоя задача - определить блюдо и его ингредиенты.

Анализируй изображение и возвращай ТОЛЬКО JSON в формате:
{
  "dish_name": "название блюда на русском языке",
  "category": "soup|main|salad|snack|dessert|drink",
  "ingredients": [
    {
      "name": "название ингредиента",
      "weight_estimate": "оценочный вес в граммах",
      "confidence": "уверенность распознавания 0-100"
    }
  ],
  "nutrition_per_100g": {
    "calories": "калории",
    "protein": "белки в г",
    "fat": "жиры в г", 
    "carbs": "углеводы в г"
  },
  "total_nutrition": {
    "calories": "общие калории",
    "protein": "общие белки в г",
    "fat": "общие жиры в г",
    "carbs": "общие углеводы в г"
  },
  "preparation_style": "fried|boiled|baked|grilled|raw|mixed",
  "confidence": "общая уверенность 0-100"
}

Правила:
1. Определи основное блюдо
2. Перечисли все видимые ингредиенты
3. Оцени примерный вес каждого ингредиента
4. Рассчитай КБЖУ на 100г и общие значения
5. Укажи стиль приготовления
6. Верни ТОЛЬКО JSON без дополнительного текста
"""
            
            # Запрос к Llama Vision
            response = await self._call_llama_vision(image_data, system_prompt)
            
            if response.get("success"):
                # Обрабатываем результат
                parsed_data = self._parse_llama_response(response.get("data", ""))
                
                if parsed_data:
                    # Рассчитываем КБЖУ если нужно
                    nutrition_data = self._calculate_nutrition(parsed_data)
                    
                    result = {
                        "success": True,
                        "data": {
                            **parsed_data,
                            "nutrition": nutrition_data,
                            "recognition_time": datetime.now().isoformat()
                        }
                    }
                    
                    logger.info(f"📸 Llama Vision: распознано блюдо '{parsed_data.get('dish_name')}'")
                    return result
                else:
                    return {
                        "success": False,
                        "error": "Не удалось распознать структуру блюда",
                        "data": {}
                    }
            else:
                return response
                
        except Exception as e:
            logger.error(f"📸 Llama Vision: ошибка распознавания {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    async def _call_llama_vision(self, image_data: bytes, system_prompt: str) -> Dict[str, Any]:
        """Вызов Llama Vision через Cloudflare Workers AI"""
        try:
            if self.use_real_api:
                return await self._call_cloudflare_ai(image_data, system_prompt)
            else:
                logger.error("📸 Llama Vision: реальный AI недоступен - отсутствуют учетные данные Cloudflare")
                raise ValueError("Real AI requires Cloudflare credentials")
                
        except Exception as e:
            logger.error(f"📸 Llama Vision: ошибка вызова {e}")
            raise
    
    async def _call_cloudflare_ai(self, image_data: bytes, system_prompt: str) -> Dict[str, Any]:
        """Реальный вызов Cloudflare Workers AI"""
        try:
            import base64
            import aiohttp
            
            # Конвертируем изображение в base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Формируем запрос к Cloudflare Workers AI
            url = f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_account_id}/ai/run/{self.model_id}"
            
            headers = {
                "Authorization": f"Bearer {self.cloudflare_api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "image": f"data:image/jpeg;base64,{image_b64}",
                "prompt": system_prompt,
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            logger.info(f"📸 Llama Vision: отправляю запрос к Cloudflare AI")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Извлекаем ответ
                        content = result.get("result", {}).get("response", "")
                        
                        if content:
                            logger.info(f"📸 Llama Vision: получен ответ от Cloudflare AI")
                            return {
                                "success": True,
                                "data": content
                            }
                        else:
                            logger.error("📸 Llama Vision: пустой ответ от Cloudflare AI")
                            return {
                                "success": False,
                                "error": "Пустой ответ от AI",
                                "data": ""
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"📸 Llama Vision: Cloudflare API error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"API error {response.status}: {error_text}",
                            "data": ""
                        }
                        
        except aiohttp.ClientError as e:
            logger.error(f"📸 Llama Vision: ошибка сети Cloudflare AI {e}")
            raise
        except asyncio.TimeoutError:
            logger.error("📸 Llama Vision: timeout Cloudflare AI")
            raise
        except Exception as e:
            logger.error(f"📸 Llama Vision: ошибка Cloudflare AI {e}")
            raise
    
    async def _fallback_emulation(self) -> Dict[str, Any]:
        """Fallback эмуляция если Cloudflare AI недоступен"""
        try:
            await asyncio.sleep(1)  # Эмуляция задержки
            
            # Пример ответа от Llama Vision
            mock_response = """
{
  "dish_name": "борщ",
  "category": "soup",
  "ingredients": [
    {
      "name": "свекла",
      "weight_estimate": 80,
      "confidence": 95
    },
    {
      "name": "капуста",
      "weight_estimate": 60,
      "confidence": 90
    },
    {
      "name": "картофель",
      "weight_estimate": 100,
      "confidence": 85
    },
    {
      "name": "морковь",
      "weight_estimate": 40,
      "confidence": 80
    },
    {
      "name": "говядина",
      "weight_estimate": 120,
      "confidence": 90
    }
  ],
  "nutrition_per_100g": {
    "calories": 65,
    "protein": 3.5,
    "fat": 2.8,
    "carbs": 8.2
  },
  "total_nutrition": {
    "calories": 280,
    "protein": 15,
    "fat": 12,
    "carbs": 35
  },
  "preparation_style": "boiled",
  "confidence": 88
}
"""
            
            return {
                "success": True,
                "data": mock_response
            }
            
        except Exception as e:
            logger.error(f"📸 Llama Vision: ошибка эмуляции {e}")
            return {
                "success": False,
                "error": f"Ошибка эмуляции: {e}",
                "data": ""
            }
    
    def _parse_llama_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Парсинг ответа от Llama"""
        try:
            # Ищем JSON в ответе
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx + 1]
                return json.loads(json_str)
            else:
                # Если JSON не найден, пробуем распарсить весь ответ
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            logger.error(f"📸 Llama Vision: ошибка парсинга JSON {e}")
            return None
        except Exception as e:
            logger.error(f"📸 Llama Vision: ошибка обработки ответа {e}")
            return None
    
    def _calculate_nutrition(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Расчет КБЖУ на основе ингредиентов"""
        try:
            ingredients = parsed_data.get("ingredients", [])
            total_weight = sum(ing.get("weight_estimate", 0) for ing in ingredients)
            
            if total_weight == 0:
                return parsed_data.get("total_nutrition", {})
            
            # База данных КБЖУ продуктов (упрощенная)
            nutrition_db = {
                "свекла": {"calories": 43, "protein": 1.6, "fat": 0.2, "carbs": 9.6},
                "капуста": {"calories": 27, "protein": 1.8, "fat": 0.1, "carbs": 6.3},
                "картофель": {"calories": 77, "protein": 2.0, "fat": 0.1, "carbs": 17.5},
                "морковь": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 9.6},
                "говядина": {"calories": 250, "protein": 26.0, "fat": 15.0, "carbs": 0.0},
                "курица": {"calories": 165, "protein": 20.0, "fat": 9.0, "carbs": 0.0},
                "свиной фарш": {"calories": 280, "protein": 16.0, "fat": 22.0, "carbs": 0.0},
                "рис": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28.0},
                "гречка": {"calories": 110, "protein": 4.2, "fat": 1.2, "carbs": 21.0},
                "макароны": {"calories": 140, "protein": 5.0, "fat": 1.1, "carbs": 28.0},
                "лук": {"calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9.3},
                "масло растительное": {"calories": 884, "protein": 0.0, "fat": 100.0, "carbs": 0.0},
                "сметана": {"calories": 201, "protein": 3.0, "fat": 20.0, "carbs": 3.2},
                "томаты": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
                "огурцы": {"calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
                "сыр": {"calories": 350, "protein": 25.0, "fat": 28.0, "carbs": 1.0}
            }
            
            # Рассчитываем общие КБЖУ
            total_nutrition = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
            
            for ingredient in ingredients:
                name = ingredient.get("name", "").lower()
                weight = ingredient.get("weight_estimate", 0)
                
                # Ищем продукт в базе
                product_nutrition = None
                for product_name, nutrition in nutrition_db.items():
                    if product_name in name or name in product_name:
                        product_nutrition = nutrition
                        break
                
                if product_nutrition:
                    # Рассчитываем КБЖУ для веса ингредиента
                    factor = weight / 100  # КБЖУ на 100г
                    total_nutrition["calories"] += product_nutrition["calories"] * factor
                    total_nutrition["protein"] += product_nutrition["protein"] * factor
                    total_nutrition["fat"] += product_nutrition["fat"] * factor
                    total_nutrition["carbs"] += product_nutrition["carbs"] * factor
            
            # Округляем значения
            for key in total_nutrition:
                total_nutrition[key] = round(total_nutrition[key], 1)
            
            logger.info(f"📸 Llama Vision: рассчитано КБЖУ - {total_nutrition}")
            
            return {
                "calculated": True,
                "total_weight": total_weight,
                "nutrition": total_nutrition,
                "ingredients_count": len(ingredients)
            }
            
        except Exception as e:
            logger.error(f"📸 Llama Vision: ошибка расчета КБЖУ {e}")
            return parsed_data.get("total_nutrition", {})
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Информация о движке"""
        return {
            "name": self.name,
            "version": self.version,
            "task_types": self.task_types,
            "description": "Специализированный движок для распознавания еды по фото",
            "capabilities": [
                "Распознавание блюд",
                "Определение ингредиентов", 
                "Расчет КБЖУ",
                "Оценка веса ингредиентов"
            ]
        }

# Глобальный экземпляр
llama_vision = LlamaVisionEngine()

# Удобная функция для использования
async def recognize_food_from_llama(image_data: bytes) -> Dict[str, Any]:
    """Распознать еду по фото через Llama Vision"""
    return await llama_vision.recognize_food(image_data)
