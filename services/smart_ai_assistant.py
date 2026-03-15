"""
🤖 Умный AI-ассистент с Function Calling
✨ Использует Hermes 2 Pro для вызова функций бота
🎯 Может выполнять действия напрямую из диалога
"""

import logging
from typing import Dict, List, Any, Optional
from services.ai_engine_manager import ai  # Исправленный импорт
from utils.retry_handler import ai_operation_with_retry  # Добавляем retry логику
from database.db import get_session
from database.models import User, WaterEntry, Activity, WeightEntry, StepsEntry
from sqlalchemy import select
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SmartAIAssistant:
    """Умный AI-ассистент с function calling"""
    
    def __init__(self):
        self.ai = ai
        self.functions = self._define_functions()
    
    def _define_functions(self) -> List[Dict]:
        """Определяет доступные функции для AI"""
        return [
            {
                "name": "log_water",
                "description": "Записать потребление воды",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "integer",
                            "description": "Количество воды в миллилитрах"
                        },
                        "user_id": {
                            "type": "integer", 
                            "description": "ID пользователя"
                        }
                    },
                    "required": ["amount", "user_id"]
                }
            },
            {
                "name": "log_activity",
                "description": "Записать физическую активность",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "activity_type": {
                            "type": "string",
                            "description": "Тип активности (бег, ходьба, тренажер и т.д.)"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Длительность в минутах"
                        },
                        "calories_burned": {
                            "type": "integer",
                            "description": "Сожженные калории"
                        },
                        "user_id": {
                            "type": "integer",
                            "description": "ID пользователя"
                        }
                    },
                    "required": ["activity_type", "duration_minutes", "user_id"]
                }
            },
            {
                "name": "log_weight",
                "description": "Записать вес",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "weight": {
                            "type": "number",
                            "description": "Вес в килограммах"
                        },
                        "user_id": {
                            "type": "integer",
                            "description": "ID пользователя"
                        }
                    },
                    "required": ["weight", "user_id"]
                }
            },
            {
                "name": "get_user_stats",
                "description": "Получить статистику пользователя",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "ID пользователя"
                        },
                        "period": {
                            "type": "string",
                            "description": "Период (today, week, month)"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_nutrition_recommendations",
                "description": "Получить персонализированные рекомендации по питанию",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "ID пользователя"
                        },
                        "goal": {
                            "type": "string",
                            "description": "Цель (lose, maintain, gain)"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        ]
    
    async def process_smart_request(
        self,
        user_id: int,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Обрабатывает умный запрос с function calling
        
        Может выполнять действия бота напрямую из текста
        """
        
        system_prompt = f"""
        Ты умный ассистент NutriBuddy. Ты можешь выполнять действия бота через вызов функций.
        
        Пользователь говорит: "{message}"
        
        Анализируй запрос и:
        1. Если нужно выполнить действие (записать воду, активность, вес) - вызови соответствующую функцию
        2. Если нужна информация - получи статистику через функции
        3. Если нужен совет - используй рекомендации
        4. Отвечай естественно, как персональный ассистент
        
        Примеры:
        - "Выпил стакан воды" → вызови log_water(200)
        - "Бегал 30 минут" → вызови log_activity("бег", 30)
        - "Сколько я весил вчера?" → вызови get_user_stats()
        - "Посоветуй что съесть для похудения" → вызови get_nutrition_recommendations()
        
        ID пользователя: {user_id}
        """
        
        def get_available_functions(self) -> List[Dict]:
            """Получить список доступных функций"""
            return self.functions
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем историю диалога если есть
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Последние 5 сообщений
        
        messages.append({"role": "user", "content": message})
        
         try:
             # Выполняем AI запрос с retry логикой через Hermes
             ai_result = await ai_operation_with_retry(
                 self.ai.engines["hermes"].process_function_call,
                 prompt=message,
                 available_functions=self.functions
             )
            
            if ai_result.get("success"):
                tool_calls = ai_result.get("data", {}).get("tool_calls", [])
                response_text = ai_result.get("data", {}).get("content", "")
                
                # Выполняем вызванные функции
                function_results = []
                for tool_call in tool_calls:
                    func_name = tool_call.get("name")
                    func_args = tool_call.get("arguments", {})
                    
                    try:
                        func_result = await self._execute_function(func_name, func_args)
                        function_results.append({
                            "function": func_name,
                            "result": func_result,
                            "success": True
                        })
                    except Exception as e:
                        logger.error(f"Function execution error: {e}")
                        function_results.append({
                            "function": func_name,
                            "result": str(e),
                            "success": False
                        })
                
                return {
                    "success": True,
                    "response": response_text,
                    "function_calls": function_results,
                    "model": ai_result.get("model", "hermes_2_pro")
                }
            else:
                return {
                    "success": False,
                    "error": ai_result.get("error", "Unknown error"),
                    "response": "Извините, временные технические проблемы."
                }
                
        except Exception as e:
            logger.error(f"Smart assistant error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Извините, произошла ошибка при обработке запроса."
            }
    
    async def _execute_function(self, func_name: str, args: Dict) -> Any:
        """Выполняет вызванную функцию"""
        
        if func_name == "log_water":
            return await self._log_water(args["user_id"], args["amount"])
        
        elif func_name == "log_activity":
            return await self._log_activity(
                args["user_id"], 
                args["activity_type"], 
                args["duration_minutes"],
                args.get("calories_burned")
            )
        
        elif func_name == "log_weight":
            return await self._log_weight(args["user_id"], args["weight"])
        
        elif func_name == "get_user_stats":
            return await self._get_user_stats(args["user_id"], args.get("period", "today"))
        
        elif func_name == "get_nutrition_recommendations":
            return await self._get_nutrition_recommendations(
                args["user_id"], 
                args.get("goal", "maintain")
            )
        
        else:
            raise ValueError(f"Unknown function: {func_name}")
    
    async def _log_water(self, user_id: int, amount: int) -> Dict:
        """Записывает воду"""
        async with get_session() as session:
            # Проверяем существование пользователя
            from database.models import User
            from sqlalchemy import select
            
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {
                    "success": False,
                    "error": "Пользователь не найден"
                }
            
            water_entry = WaterEntry(
                user_id=user.id,  # Используем ID из базы, а не telegram_id
                amount=amount,
                datetime=datetime.now()
            )
            session.add(water_entry)
            await session.commit()
            
            return {
                "success": True,
                "message": f"Записано {amount} мл воды",
                "amount": amount
            }
    
    async def _log_activity(
        self, 
        user_id: int, 
        activity_type: str, 
        duration_minutes: int,
        calories_burned: Optional[int] = None
    ) -> Dict:
        """Записывает активность"""
        
        # Расчет калорий если не указаны
        if not calories_burned:
            calories_burned = self._estimate_calories(activity_type, duration_minutes)
        
        async with get_session() as session:
            # Проверяем существование пользователя
            from database.models import User
            from sqlalchemy import select
            
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {
                    "success": False,
                    "error": "Пользователь не найден"
                }
            
            activity = Activity(
                user_id=user.id,  # Используем ID из базы, а не telegram_id
                activity_type=activity_type,
                duration=duration_minutes,
                calories_burned=calories_burned,
                datetime=datetime.now()
            )
            session.add(activity)
            await session.commit()
            
            return {
                "success": True,
                "message": f"Записана активность: {activity_type} {duration_minutes} мин",
                "calories_burned": calories_burned
            }
    
    async def _log_weight(self, user_id: int, weight: float) -> Dict:
        """Записывает вес"""
        async with get_session() as session:
            # Проверяем существование пользователя
            from database.models import User
            from sqlalchemy import select
            
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {
                    "success": False,
                    "error": "Пользователь не найден"
                }
            
            weight_entry = WeightEntry(
                user_id=user.id,  # Используем ID из базы, а не telegram_id
                weight=weight,
                datetime=datetime.now()
            )
            session.add(weight_entry)
            await session.commit()
            
            return {
                "success": True,
                "message": f"Записан вес: {weight} кг",
                "trend": await self._get_weight_trend(user.id)
            }
    
    async def _get_user_stats(self, user_id: int, period: str) -> Dict:
        """Получает статистику пользователя"""
        # Здесь можно использовать существующую логику из progress.py
        return {
            "period": period,
            "water": await self._get_period_water(user_id, period),
            "activities": await self._get_period_activities(user_id, period),
            "weight_entries": await self._get_period_weights(user_id, period)
        }
    
    async def _get_nutrition_recommendations(self, user_id: int, goal: str) -> Dict:
        """Получает рекомендации по питанию"""
        # Используем AI для генерации рекомендаций
        prompt = f"""
        Дай персонализированные рекомендации по питанию для цели: {goal}
        
        Учти:
        - Цель: {goal}
        - Рекомендации должны быть практичными
        - Включи конкретные продукты и блюда
        - Укажи частоту приема пищи
        
        Верни JSON с рекомендациями.
        """
        
        result = await self.ai.process_text(prompt, task_type="json")
        
        return {
            "goal": goal,
            "recommendations": result.get("data", {}).get("content", "Рекомендации временно недоступны")
        }
    
    # Helper методы
    def _estimate_calories(self, activity_type: str, duration_minutes: int) -> int:
        """Оценивает калории для активности"""
        calories_per_minute = {
            "бег": 10,
            "ходьба": 4,
            "тренажер": 8,
            "плавание": 11,
            "йога": 3,
            "велосипед": 7
        }
        
        return calories_per_minute.get(activity_type.lower(), 5) * duration_minutes
    
    async def _get_today_water(self, user_id: int) -> int:
        """Получает количество воды за сегодня"""
        async with get_session() as session:
            result = await session.execute(
                select(WaterEntry).where(
                    WaterEntry.user_id == user_id,
                    WaterEntry.datetime >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                )
            )
            entries = result.scalars().all()
            return sum(entry.amount for entry in entries)
    
    async def _get_weight_trend(self, user_db_id: int) -> str:
        """Получает тренд веса"""
        async with get_session() as session:
            result = await session.execute(
                select(WeightEntry)
                .where(WeightEntry.user_id == user_db_id)
                .order_by(WeightEntry.datetime.desc())
                .limit(7)
            )
            entries = result.scalars().all()
            
            if len(entries) < 2:
                return "недостаточно данных"
            
            weights = [entry.weight for entry in entries]
            recent_avg = sum(weights[:3]) / 3
            older_avg = sum(weights[3:6]) / 3 if len(weights) > 3 else recent_avg
            
            if recent_avg < older_avg - 0.5:
                return "снижается"
            elif recent_avg > older_avg + 0.5:
                return "растет"
            else:
                return "стабилен"

# Создаем экземпляр умного ассистента
smart_assistant = SmartAIAssistant()
