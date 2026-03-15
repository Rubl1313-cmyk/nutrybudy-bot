"""
🤖 AI Engine Manager - Упрощенная версия с Llama Vision
📸 Llama Vision - распознавание еды по фото
🧠 Hermes - ВСЁ остальное (ассистент, аналитика, персонализация)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .llama_vision_engine import llama_vision
from .hermes_engine import hermes

logger = logging.getLogger(__name__)

class AIEngineManager:
    """Менеджер AI движков с Llama Vision для фото"""
    
    def __init__(self):
        self.engines = {
            "llama_vision": llama_vision,
            "hermes": hermes
        }
        
        # Маршрутизация задач по движкам
        self.task_routing = {
            "food_recognition": "llama_vision",
            "text_generation": "hermes",
            "function_calling": "hermes",
            "analytics": "hermes",
            "personalization": "hermes",
            "gamification": "hermes",
            "assistant": "hermes"
        }
        
        logger.info("🤖 AI Engine Manager: инициализирован с Llama Vision")
    
    async def recognize_food(self, image_data: bytes) -> Dict[str, Any]:
        """
        Распознать еду по фото (ТОЛЬКО Llama Vision)
        
        Args:
            image_data: Байты изображения
            
        Returns:
            Dict с результатом распознавания и КБЖУ
        """
        try:
            logger.info("📸 AI Manager: маршрутизирую на Llama Vision для распознавания еды")
            
            # Используем ТОЛЬКО Llama Vision для распознавания еды
            result = await self.engines["llama_vision"].recognize_food(image_data)
            
            if result.get("success"):
                logger.info(f"📸 AI Manager: Llama Vision успешно распознала еду")
                return result
            else:
                logger.error(f"📸 AI Manager: Llama Vision не смогла распознать еду")
                return result
                
        except Exception as e:
            logger.error(f"🤖 AI Manager: ошибка распознавания еды {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    async def process_text(self, prompt: str, system_prompt: str = None, task_type: str = "text_generation") -> Dict[str, Any]:
        """
        Обработать текстовый запрос (ТОЛЬКО Hermes)
        
        Args:
            prompt: Текстовый запрос
            system_prompt: Системный промпт
            task_type: Тип задачи
            
        Returns:
            Dict с результатом обработки
        """
        try:
            logger.info(f"🧠 AI Manager: маршрутизирую на Hermes для задачи '{task_type}'")
            
            # Проверяем что это не распознавание еды
            if task_type == "food_recognition":
                logger.warning("🚫 AI Manager: попытка распознавания еды через текст - перенаправляю на Hermes")
            
            # Используем ТОЛЬКО Hermes для всех текстовых задач
            result = await self.engines["hermes"].process_text(prompt, system_prompt, task_type)
            
            if result.get("success"):
                logger.info(f"🧠 AI Manager: Hermes успешно обработал запрос")
                return result
            else:
                logger.error(f"🧠 AI Manager: Hermes не смог обработать запрос")
                return result
                
        except Exception as e:
            logger.error(f"🤖 AI Manager: ошибка обработки текста {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    async def process_function_call(self, prompt: str, available_functions: List[Dict]) -> Dict[str, Any]:
        """
        Выполнить вызов функции через Hermes (ТОЛЬКО Hermes)
        
        Args:
            prompt: Промпт для AI
            available_functions: Список доступных функций
            
        Returns:
            Dict с результатом выполнения
        """
        try:
            logger.info(f"🔧 AI Manager: маршрутизирую на Hermes для function call")
            
            # Используем ТОЛЬКО Hermes для вызова функций
            result = await self.engines["hermes"].process_function_call(prompt, available_functions)
            
            if result.get("success"):
                logger.info(f"🔧 AI Manager: Hermes успешно выполнил function call")
                return result
            else:
                logger.error(f"🔧 AI Manager: Hermes не смог выполнить function call")
                return result
                
        except Exception as e:
            logger.error(f"🤖 AI Manager: ошибка вызова функции {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Получить статус всех движков"""
        status = {}
        
        for engine_name, engine in self.engines.items():
            try:
                status[engine_name] = {
                    "name": engine.name if hasattr(engine, 'name') else engine_name,
                    "version": engine.version if hasattr(engine, 'version') else 'unknown',
                    "status": "active",
                    "capabilities": getattr(engine, 'task_types', ['text_processing'])
                }
            except Exception as e:
                status[engine_name] = {
                    "name": engine_name,
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "success": True,
            "engines": status,
            "routing": self.task_routing
        }

# Глобальный экземпляр
ai = AIEngineManager()

# Удобные функции для использования
async def recognize_food(image_data: bytes) -> Dict[str, Any]:
    """Распознать еду по фото"""
    return await ai.recognize_food(image_data)

async def process_text(prompt: str, system_prompt: str = None, task_type: str = "text_generation") -> Dict[str, Any]:
    """Обработать текстовый запрос"""
    return await ai.process_text(prompt, system_prompt, task_type)

async def process_function_call(function_name: str, args: Dict) -> Dict[str, Any]:
    """Выполнить вызов функции"""
    return await ai.process_function_call(function_name, args)
