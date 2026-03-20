"""
services/langchain_agent.py
LangChain Agent с инструментами для автоматизации NutriBuddy Bot
"""
import os
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from aiogram.fsm.context import FSMContext
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import StructuredTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory

from database.db import get_session
from database.models import User
from services.ai_processor import ai_processor
from services.weather import get_weather
from services.cloudflare_llm import cloudflare_llm
from utils.daily_stats import get_daily_stats

logger = logging.getLogger(__name__)

# Кеш агентов с отслеживанием времени использования
_agents: Dict[int, Dict[str, Any]] = {}
_agents_lock = asyncio.Lock()  # Блокировка для потокобезопасности

class LangChainAgent:
    """AI агент с инструментами для NutriBuddy"""
    
    def __init__(self, user_id: int, state: FSMContext):
        self.user_id = user_id
        self.state = state
        self.user = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._create_tools()
        self.last_used = time.time()
        
        # LLM встроенный
        self.llm = cloudflare_llm
        self.agent = create_react_agent(
            llm=self.llm.llm,
            tools=self.tools,
            memory=self.memory,
            max_iterations=5,
            verbose=True
        )
        logger.info(f"[AGENT] LangChain Agent initialized for user {user_id}")

    async def load_user(self):
        """Загружает пользователя из БД"""
        try:
            async with get_session() as session:
                result = await session.execute(select(User).where(User.telegram_id == self.user_id))
                self.user = result.scalar_one_or_none()
                if self.user:
                    logger.info(f"[AGENT] User loaded: {self.user.first_name}")
                else:
                    logger.warning(f"[AGENT] User not found: {self.user_id}")
        except Exception as e:
            logger.error(f"[AGENT] Error loading user {self.user_id}: {e}")
            self.user = None

    def _get_prompt(self) -> str:
        return """Ты — премиальный AI-ассистент по питанию NutriBuddy.
Твоя задача — понимать, что хочет пользователь, и вызывать подходящий инструмент.
Всегда отвечай кратко, по делу и используй структурированный текст.

Информация о пользователе:
{user_info}

Доступные инструменты:
{tools}

История диалога:
{chat_history}

Запрос пользователя: {input}
{agent_scratchpad}"""

    def _create_tools(self) -> List[StructuredTool]:
        """Создает инструменты для агента"""
        
        async def log_food(description: str) -> str:
            """Записывает прием пищи. description: описание еды (например, "200г курицы с гречкой"). Возвращает карточку с КБЖУ."""
            try:
                # Парсим еду через ai_processor
                result = await ai_processor.process_text_input(description, self.user_id)
                if not result.get("success"):
                    return "[ERROR] Не удалось распознать еду. Попробуйте описать подробнее."
                
                food_items = result["parameters"].get("food_items", [])
                meal_type = result["parameters"].get("meal_type", "main")
                
                if not food_items:
                    return "[ERROR] Не удалось распознать продукты в вашем сообщении."
                
                # Сохраняем через food_save_service
                from services.food_save_service import food_save_service
                from utils.ui_templates import food_entry_card
                
                save_result = await food_save_service.save_food_entry(
                    user_id=self.user_id,
                    food_items=food_items,
                    meal_type=meal_type,
                    description=description
                )
                
                if save_result.get("success"):
                    # Получаем статистику
                    daily_stats = await get_daily_stats(self.user_id)
                    
                    # Формируем карточку
                    from database.db import get_session
                    with get_session() as session:
                        user = session.query(User).filter(User.telegram_id == self.user_id).first()
                    
                    food_data = {
                        'description': description,
                        'total_calories': save_result.get('total_calories', 0),
                        'total_protein': save_result.get('total_protein', 0),
                        'total_fat': save_result.get('total_fat', 0),
                        'total_carbs': save_result.get('total_carbs', 0),
                        'meal_type': meal_type
                    }
                    
                    card_text = food_entry_card(food_data, user, daily_stats)
                    return f"[SUCCESS] Прием пищи записан!\n\n{card_text}"
                else:
                    return f"[ERROR] Ошибка сохранения: {save_result.get('error')}"
                    
            except Exception as e:
                logger.error(f"[AGENT] Error in log_food: {e}")
                return "[ERROR] Ошибка при записи приема пищи"

        async def log_water(amount: str) -> str:
            """Записывает воду. amount: объем (например, "200мл", "1 стакан", "500мл"). Возвращает подтверждение."""
            try:
                from utils.drink_parser import parse_drink_input
                from services.drink_save_service import drink_save_service
                from utils.message_templates import water_logged
                
                # Парсим ввод
                drink_name, volume, calories = parse_drink_input(amount)
                
                if not drink_name or not volume:
                    return "[ERROR] Не удалось распознать объем. Укажите в формате: \"200мл\", \"1 стакан\", \"500мл\""
                
                # Сохраняем
                save_result = await drink_save_service.save_drink_entry(
                    user_id=self.user_id,
                    drink_name=drink_name,
                    volume_ml=volume,
                    calories=calories
                )
                
                if save_result.get("success"):
                    # Получаем статистику
                    from utils.daily_stats import get_daily_water
                    from database.db import get_session
                    with get_session() as session:
                        user = session.query(User).filter(User.telegram_id == self.user_id).first()
                    
                    total_today = await get_daily_water(self.user_id)
                    
                    # Формируем ответ
                    response_text = water_logged(volume, total_today, user.daily_water_goal)
                    return response_text
                else:
                    return f"[ERROR] Ошибка сохранения: {save_result.get('error')}"
                    
            except Exception as e:
                logger.error(f"[AGENT] Error in log_water: {e}")
                return "[ERROR] Ошибка при записи воды"

        async def get_weather_info(city: str = "") -> str:
            """Получает погоду. city: город (опционально). Возвращает погоду для города пользователя или указанного."""
            try:
                # Используем город пользователя или указанный
                target_city = city if city else (self.user.city if self.user else "Москва")
                
                weather_data = await get_weather(target_city)
                
                if weather_data:
                    return (
                        f"[WEATHER] Погода в {target_city}\n"
                        f"[TEMP] Температура: {weather_data.get('temp', 'N/A')}°C\n"
                        f"[CONDITION] {weather_data.get('condition', 'N/A')}\n"
                        f"[HUMIDITY] Влажность: {weather_data.get('humidity', 'N/A')}%\n"
                        f"[WIND] Ветер: {weather_data.get('wind', 'N/A')} м/с"
                    )
                else:
                    return "[ERROR] Не удалось получить погоду. Попробуйте позже."
                    
            except Exception as e:
                logger.error(f"[AGENT] Error in get_weather: {e}")
                return "[ERROR] Ошибка при получении погоды"

        async def get_today_stats() -> str:
            """Получает статистику за сегодня. Возвращает КБЖУ, воду, активность и прогресс."""
            try:
                from utils.daily_stats import get_daily_stats
                
                stats = await get_daily_stats(self.user_id)
                
                if not stats:
                    return "[INFO] За сегодня еще нет данных. Начните с записи приема пищи!"
                
                # Формируем красивый ответ
                progress_cal = (stats.get('calories_consumed', 0) / self.user.daily_calorie_goal * 100) if self.user else 0
                progress_water = (stats.get('water_consumed', 0) / self.user.daily_water_goal * 100) if self.user else 0
                
                return (
                    f"[STATS] Ваша статистика за сегодня:\n\n"
                    f"[CALORIES] Калории: {stats.get('calories_consumed', 0):.0f}/{self.user.daily_calorie_goal if self.user else 2000:.0f} ккал ({progress_cal:.0f}%)\n"
                    f"[WATER] Вода: {stats.get('water_consumed', 0):.0f}/{self.user.daily_water_goal if self.user else 2000:.0f} мл ({progress_water:.0f}%)\n"
                    f"[FOOD_ENTRIES] Приемов пищи: {stats.get('meals_count', 0)}\n"
                    f"[ACTIVITY] Активность: {stats.get('activity_minutes', 0)} минут\n"
                    f"[STEPS] Шаги: {stats.get('steps_count', 0)}"
                )
                
            except Exception as e:
                logger.error(f"[AGENT] Error in get_today_stats: {e}")
                return "[ERROR] Ошибка при получении статистики"

        async def get_user_profile() -> str:
            """Получает профиль пользователя. Возвращает данные профиля и цели."""
            try:
                if not self.user:
                    return "[ERROR] Профиль не найден. Сначала создайте профиль командой /set_profile"
                
                return (
                    f"[PROFILE] Ваш профиль:\n\n"
                    f"[INFO] {self.user.first_name or 'Пользователь'}\n"
                    f"[WEIGHT] Вес: {self.user.weight} кг\n"
                    f"[HEIGHT] Рост: {self.user.height} см\n"
                    f"[AGE] Возраст: {self.user.age} лет\n"
                    f"[GOAL] Цель: {self.user.goal}\n"
                    f"[ACTIVITY] Активность: {self.user.activity_level}\n\n"
                    f"[TARGETS] Цели на день:\n"
                    f"[CALORIES] Калории: {self.user.daily_calorie_goal:.0f} ккал\n"
                    f"[PROTEIN] Белки: {self.user.daily_protein_goal:.0f} г\n"
                    f"[FAT] Жиры: {self.user.daily_fat_goal:.0f} г\n"
                    f"[CARBS] Углеводы: {self.user.daily_carbs_goal:.0f} г\n"
                    f"[WATER] Вода: {self.user.daily_water_goal:.0f} мл"
                )
                
            except Exception as e:
                logger.error(f"[AGENT] Error in get_user_profile: {e}")
                return "[ERROR] Ошибка при получении профиля"

        async def calculate_nutrition(food_description: str) -> str:
            """Рассчитывает КБЖУ для еды. food_description: описание еды. Возвращает КБЖУ без записи."""
            try:
                result = await ai_processor.process_text_input(f"рассчитать КБЖУ: {food_description}", self.user_id)
                
                if result.get("success") and result.get("food_items"):
                    food_items = result["food_items"]
                    total_cal = sum(item.get('calories', 0) for item in food_items)
                    total_prot = sum(item.get('protein', 0) for item in food_items)
                    total_fat = sum(item.get('fat', 0) for item in food_items)
                    total_carbs = sum(item.get('carbs', 0) for item in food_items)
                    
                    return (
                        f"[NUTRITION] КБЖУ для: {food_description}\n\n"
                        f"[CALORIES] Калории: {total_cal:.0f} ккал\n"
                        f"[PROTEIN] Белки: {total_prot:.1f} г\n"
                        f"[FAT] Жиры: {total_fat:.1f} г\n"
                        f"[CARBS] Углеводы: {total_carbs:.1f} г"
                    )
                else:
                    return "[ERROR] Не удалось рассчитать КБЖУ. Опишите продукты подробнее."
                    
            except Exception as e:
                logger.error(f"[AGENT] Error in calculate_nutrition: {e}")
                return "[ERROR] Ошибка при расчете КБЖУ"

        async def get_recipe(dish_name: str) -> str:
            """Получает рецепт. dish_name: название блюда. Возвращает рецепт и рекомендации."""
            try:
                result = await ai_processor.process_text_input(f"рецепт: {dish_name}", self.user_id)
                
                if result.get("success"):
                    return f"[RECIPE] {result.get('response', 'Рецепт не найден')}"
                else:
                    return "[ERROR] Не удалось найти рецепт. Попробуйте другое блюдо."
                    
            except Exception as e:
                logger.error(f"[AGENT] Error in get_recipe: {e}")
                return "[ERROR] Ошибка при получении рецепта"

        # Создаем инструменты
        tools = [
            StructuredTool.from_function(
                log_food,
                name="log_food",
                description="Записывает прием пищи. Используй когда пользователь хочет поесть или описывает еду."
            ),
            StructuredTool.from_function(
                log_water,
                name="log_water", 
                description="Записывает воду. Используй когда пользователь говорит о воде или питье."
            ),
            StructuredTool.from_function(
                get_weather_info,
                name="get_weather",
                description="Получает погоду. Используй когда пользователь спрашивает о погоде."
            ),
            StructuredTool.from_function(
                get_today_stats,
                name="get_today_stats",
                description="Получает статистику за сегодня. Используй когда пользователь хочет узнать свой прогресс."
            ),
            StructuredTool.from_function(
                get_user_profile,
                name="get_user_profile",
                description="Получает профиль пользователя. Используй когда пользователь спрашивает о своих данных."
            ),
            StructuredTool.from_function(
                calculate_nutrition,
                name="calculate_nutrition",
                description="Рассчитывает КБЖУ для еды. Используй когда пользователь хочет узнать калорийность без записи."
            ),
            StructuredTool.from_function(
                get_recipe,
                name="get_recipe",
                description="Получает рецепт. Используй когда пользователь просит рецепт блюда."
            )
        ]
        
        return tools

    async def process_message(self, message: str) -> str:
        """Обрабатывает сообщение пользователя"""
        try:
            # Загружаем данные пользователя
            await self.load_user()
            
            # Формируем контекст
            user_info = ""
            if self.user:
                user_info = f"""
Имя: {self.user.first_name or 'Пользователь'}
Вес: {self.user.weight} кг
Рост: {self.user.height} см
Возраст: {self.user.age} лет
Цель: {self.user.goal}
Активность: {self.user.activity_level}
Дневная цель калорий: {self.user.daily_calorie_goal:.0f} ккал
Дневная цель воды: {self.user.daily_water_goal:.0f} мл"""
            else:
                user_info = "Пользователь не найден. Попросите создать профиль командой /set_profile"
            
            # Выполняем агент
            result = await self.agent.arun(
                input=message,
                user_info=user_info,
                tools="\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools]),
                chat_history=self.memory.chat_memory.messages,
                agent_scratchpad=""
            )
            
            # Обновляем время использования
            self.last_used = time.time()
            
            return result
            
        except Exception as e:
            logger.error(f"[AGENT] Error processing message: {e}")
            return "[ERROR] Произошла ошибка. Попробуйте переформулировать запрос."

async def get_agent(user_id: int, state: FSMContext) -> LangChainAgent:
    """Получает или создает агента для пользователя"""
    async with _agents_lock:
        # Проверяем кеш
        if user_id in _agents:
            agent_data = _agents[user_id]
            agent = agent_data['agent']
            
            # Проверяем, не устарел ли агент (30 минут)
            if time.time() - agent_data['created'] > 1800:
                logger.info(f"[AGENT] Creating new agent for user {user_id} (expired)")
                del _agents[user_id]
            else:
                logger.info(f"[AGENT] Using existing agent for user {user_id}")
                return agent
        
        # Создаем нового агента
        logger.info(f"[AGENT] Creating new agent for user {user_id}")
        agent = LangChainAgent(user_id, state)
        
        # Сохраняем в кеш
        _agents[user_id] = {
            'agent': agent,
            'created': time.time()
        }
        
        return agent

async def cleanup_expired_agents():
    """Очищает устаревших агентов"""
    async with _agents_lock:
        current_time = time.time()
        expired_users = []
        
        for user_id, agent_data in _agents.items():
            if current_time - agent_data['created'] > 3600:  # 1 час
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del _agents[user_id]
            logger.info(f"[AGENT] Cleaned up expired agent for user {user_id}")

# Методы для обработки разных типов сообщений
def add_processing_methods(cls):
    """Добавляет методы обработки сообщений к классу LangChainAgent"""
    
    async def process_text(self, user_id: int, text: str) -> dict:
        """Обрабатывает текстовое сообщение"""
        try:
            response = await self.process_message(text)
            return {"success": True, "message": response}
        except Exception as e:
            logger.error(f"process_text error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def process_photo(self, user_id: int, photo_data: bytes, filename: str) -> dict:
        """Обрабатывает фото"""
        try:
            from services.cloudflare_manager import cf_manager
            result = await cf_manager.parse_food_image(photo_data)
            if not result.get("success"):
                return {"success": False, "error": result.get("error", "Неизвестная ошибка")}
            
            analysis = result.get("analysis", {})
            dish_name = analysis.get("dish_name", "блюдо")
            calories = analysis.get("estimated_total_calories", 0)
            protein = analysis.get("estimated_total_protein", 0)
            fat = analysis.get("estimated_total_fat", 0)
            carbs = analysis.get("estimated_total_carbs", 0)
            
            message = (
                f"🍽️ <b>{dish_name}</b>\n\n"
                f"📊 Калории: {calories:.0f} ккал\n"
                f"🥩 Белки: {protein:.1f} г\n"
                f"🧈 Жиры: {fat:.1f} г\n"
                f"🍞 Углеводы: {carbs:.1f} г\n\n"
                f"✅ Распознано. Хотите сохранить?"
            )
            
            return {"success": True, "message": message, "data": analysis}
        except Exception as e:
            logger.error(f"process_photo error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def process_voice(self, user_id: int, voice_data: bytes, filename: str) -> dict:
        """Обрабатывает голосовое сообщение"""
        try:
            from services.cloudflare_manager import cf_manager
            result = await cf_manager.transcribe_audio(voice_data)
            if not result.get("success"):
                return {"success": False, "error": result.get("error", "Не удалось распознать голос")}
            
            transcription = result.get("transcription", "")
            return await self.process_text(user_id, transcription)
        except Exception as e:
            logger.error(f"process_voice error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def process_callback(self, user_id: int, callback_data: str, message) -> dict:
        """Обрабатывает callback"""
        return {"success": True, "message": "Callback обработан"}

    # Добавляем методы к классу
    cls.process_text = process_text
    cls.process_photo = process_photo
    cls.process_voice = process_voice
    cls.process_callback = process_callback
    
    return cls

# Применяем декоратор к уже существующему классу
LangChainAgent = add_processing_methods(LangChainAgent)

# Фоновая задача для очистки
async def start_cleanup_task():
    """Запускает фоновую задачу очистки"""
    while True:
        try:
            await cleanup_expired_agents()
            await asyncio.sleep(900)  # 15 минут
        except Exception as e:
            logger.error(f"[AGENT] Error in cleanup task: {e}")
            await asyncio.sleep(60)  # 1 минута при ошибке
