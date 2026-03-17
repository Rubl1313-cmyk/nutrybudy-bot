"""
services/langchain_agent.py
LangChain Agent с инструментами для автоматизации NutriBuddy Bot
"""
import os
import logging
import asyncio
import time
from typing import Dict, Any, Optional, List
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import StructuredTool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from sqlalchemy import select

from database.db import get_session
from database.models import User
from services.cloudflare_llm import CloudflareLLM
from services.ai_processor import ai_processor
from services.food_save_service import food_save_service
from utils.premium_templates import (
    meal_card, water_card, weight_card, 
    activity_card, progress_card, achievement_card, error_card
)
from utils.helpers import get_daily_stats
from utils.daily_stats import get_daily_water, get_daily_drink_calories, get_daily_activity_calories

logger = logging.getLogger(__name__)

# Кеш агентов с отслеживанием времени использования
_agents: Dict[int, Dict[str, Any]] = {}

class LangChainAgent:
    """AI агент с инструментами для NutriBuddy"""
    
    def __init__(self, user_id: int, state: FSMContext):
        self.user_id = user_id
        self.state = state
        self.llm = CloudflareLLM()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.user = None
        self.tools = self._create_tools()
        self.last_used = time.time()
        
        # LLM всегда доступен (без эмуляции)
        self.agent = create_react_agent(
            llm=self.llm.llm,
            tools=self.tools,
            prompt=PromptTemplate.from_template(self._get_prompt())
        )
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=5,
            verbose=True
        )
        logger.info(f"✅ LangChain Agent initialized for user {user_id}")

    async def load_user(self):
        """Загружает пользователя из БД"""
        try:
            async with get_session() as session:
                result = await session.execute(select(User).where(User.telegram_id == self.user_id))
                self.user = result.scalar_one_or_none()
                if self.user:
                    logger.info(f"✅ User loaded: {self.user.first_name}")
                else:
                    logger.warning(f"⚠️ User not found: {self.user_id}")
        except Exception as e:
            logger.error(f"❌ Error loading user {self.user_id}: {e}")
            self.user = None

    def _get_prompt(self) -> str:
        return """Ты — премиальный AI-ассистент по питанию NutriBuddy.
Твоя задача — понять, что хочет пользователь, и вызвать подходящий инструмент.
Всегда отвечай красиво, используя эмодзи и структурированный текст.

Информация о пользователе:
{user_info}

Доступные инструменты:
{tools}

История диалога:
{chat_history}

Запрос пользователя: {input}
{agent_scratchpad}"""

    def _create_tools(self) -> List[StructuredTool]:
        """Создаёт инструменты для агента"""
        
        async def log_meal(description: str) -> str:
            """Записывает приём пищи. description: описание еды (например, "200г курицы с гречкой"). Возвращает карточку с КБЖУ."""
            try:
                # Парсим еду через ai_processor
                result = await ai_processor.process_text_input(description, self.user_id)
                if not result.get("success"):
                    return "❌ Не удалось распознать еду. Попробуйте описать подробнее."
                
                food_items = result["parameters"].get("food_items", [])
                meal_type = result["parameters"].get("meal_type", "main")
                
                if not food_items:
                    return "❌ Не удалось распознать продукты в вашем сообщении."
                
                # Конвертируем данные из формата _per_100g в формат для save_food_to_db
                converted_food_items = []
                for item in food_items:
                    weight = item.get('quantity', 0)
                    factor = weight / 100.0
                    
                    converted_item = {
                        'name': item.get('name', 'Неизвестный продукт'),
                        'quantity': weight,
                        'unit': item.get('unit', 'г'),
                        'calories': item.get('calories_per_100g', 0) * factor,
                        'protein': item.get('protein_per_100g', 0) * factor,
                        'fat': item.get('fat_per_100g', 0) * factor,
                        'carbs': item.get('carbs_per_100g', 0) * factor
                    }
                    converted_food_items.append(converted_item)
                
                # Сохраняем через save_food_to_db с конвертированными ингредиентами
                save_result = await food_save_service.save_food_to_db(
                    self.user_id, 
                    converted_food_items, 
                    meal_type
                )
                
                if not save_result.get("success"):
                    return f"❌ Ошибка сохранения: {save_result.get('error', 'Неизвестная ошибка')}"
                
                # Получаем дневную статистику
                daily_stats = await get_daily_stats(self.user_id)
                
                # Форматируем описание из ингредиентов
                description_from_items = ", ".join([
                    f"{item.get('quantity','')} {item.get('unit','г')} {item['name']}" 
                    for item in food_items
                ])
                
                # Форматируем данные для карточки
                food_data = {
                    'description': description_from_items,
                    'total_calories': save_result.get('total_calories', 0),
                    'total_protein': save_result.get('total_protein', 0),
                    'total_fat': save_result.get('total_fat', 0),
                    'total_carbs': save_result.get('total_carbs', 0),
                    'meal_type': meal_type
                }
                
                return meal_card(food_data, self.user, daily_stats)
                
            except Exception as e:
                logger.error(f"❌ Error in log_meal: {e}")
                return error_card("ai", f"Ошибка при сохранении еды: {str(e)}")

        async def log_water(amount_ml: int) -> str:
            """Записывает выпитую воду. amount_ml: количество в миллилитрах."""
            try:
                from services.soup_service import save_drink
                
                # Сохраняем
                result = await save_drink(self.user_id, f"вода {amount_ml} мл")
                
                # Получаем статистику за день
                total_today = await get_daily_water(self.user_id)
                return water_card(amount_ml, total_today, self.user.daily_water_goal)
                
            except Exception as e:
                logger.error(f"❌ Error in log_water: {e}")
                return error_card("database", f"Ошибка при записи воды: {str(e)}")

        async def log_drink(description: str) -> str:
            """Записывает напиток. description: описание напитка (например, "сок 250 мл")."""
            try:
                from services.soup_service import save_drink
                
                # Сохраняем
                result = await save_drink(self.user_id, description)
                
                # Получаем статистику за день
                total_today = await get_daily_water(self.user_id)
                total_calories = await get_daily_drink_calories(self.user_id)
                
                return drink_card(
                    result['volume'], 
                    result['name'], 
                    result['calories'],
                    total_today, 
                    total_calories, 
                    self.user.daily_water_goal
                )
                
            except Exception as e:
                logger.error(f"❌ Error in log_drink: {e}")
                return error_card("database", f"Ошибка при записи напитка: {str(e)}")

        async def log_weight(weight_kg: float) -> str:
            """Записывает вес. weight_kg: вес в килограммах."""
            try:
                from services.weight_service import save_weight
                
                # Сохраняем
                result = await save_weight(self.user_id, weight_kg)
                
                return weight_card(
                    weight_kg, 
                    result.get('change'), 
                    self.user.goal_weight
                )
                
            except Exception as e:
                logger.error(f"❌ Error in log_weight: {e}")
                return error_card("database", f"Ошибка при записи веса: {str(e)}")

        async def log_activity(activity_type: str, duration_min: int) -> str:
            """Записывает активность. activity_type: тип активности, duration_min: длительность в минутах."""
            try:
                from services.activity_service import save_activity
                from utils.activity_calculator import calculate_activity_calorie_goal
                from database.db import get_session
                from database.models import User
                from sqlalchemy import select
                
                # Сохраняем
                result = await save_activity(self.user_id, activity_type, duration_min)
                
                # Получаем статистику за день
                daily_total = await get_daily_activity_calories(self.user_id)
                
                # Получаем пользователя для расчета цели
                async with get_session() as session:
                    user_result = await session.execute(
                        select(User).where(User.telegram_id == self.user_id)
                    )
                    user = user_result.scalar_one_or_none()
                
                # Рассчитываем персонализированную цель активности
                if user:
                    activity_goal = calculate_activity_calorie_goal(user)
                else:
                    activity_goal = 300  # Значение по умолчанию
                
                return activity_card(
                    activity_type, 
                    duration_min, 
                    result.get('calories', 0),
                    daily_total,
                    activity_goal  # Персонализированная цель
                )
                
            except Exception as e:
                logger.error(f"❌ Error in log_activity: {e}")
                return error_card("database", f"Ошибка при записи активности: {str(e)}")

        async def show_progress(period: str = "день") -> str:
            """Показывает прогресс. period: период (день, неделя, месяц, всё время)."""
            try:
                from services.progress_service import get_progress_stats
                
                stats = await get_progress_stats(self.user_id, period)
                return progress_card(stats, period)
                
            except Exception as e:
                logger.error(f"❌ Error in show_progress: {e}")
                return error_card("database", f"Ошибка при получении прогресса: {str(e)}")

        return [
            StructuredTool.from_function(
                coroutine=log_meal,
                name="log_meal",
                description="Записывает приём пищи. Вход: описание еды."
            ),
            StructuredTool.from_function(
                coroutine=log_water,
                name="log_water",
                description="Записывает выпитую воду. Вход: количество в миллилитрах."
            ),
            StructuredTool.from_function(
                coroutine=log_drink,
                name="log_drink",
                description="Записывает напиток. Вход: описание напитка."
            ),
            StructuredTool.from_function(
                coroutine=log_weight,
                name="log_weight",
                description="Записывает вес. Вход: вес в килограммах."
            ),
            StructuredTool.from_function(
                coroutine=log_activity,
                name="log_activity",
                description="Записывает активность. Вход: тип и длительность."
            ),
            StructuredTool.from_function(
                coroutine=show_progress,
                name="show_progress",
                description="Показывает прогресс. Вход: период."
            )
        ]

    async def handle_text(self, text: str, message: Message):
        """Обрабатывает текстовое сообщение"""
        try:
            if not self.user:
                await self.load_user()
                if not self.user:
                    await message.answer("❌ Сначала создайте профиль через /set_profile")
                    return

            if not self.executor:
                await message.answer(
                    "🤖 AI агент недоступен. Проверьте настройки Cloudflare.",
                    parse_mode="HTML"
                )
                return

            # Формируем информацию о пользователе
            user_info = (
                f"Имя: {self.user.first_name}\n"
                f"Вес: {self.user.weight} кг\n"
                f"Рост: {self.user.height} см\n"
                f"Цель: {self.user.goal}\n"
                f"Дневная норма калорий: {self.user.daily_calorie_goal} ккал\n"
                f"Норма воды: {self.user.daily_water_goal} мл"
            )

            # Вызываем агента
            response = await self.executor.ainvoke({
                "input": text,
                "user_info": user_info
            })

            # Отправляем ответ
            await message.answer(response["output"], parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"❌ Error in handle_text: {e}")
            await message.answer(
                error_card("general", f"Ошибка обработки: {str(e)}"),
                parse_mode="HTML"
            )

    @classmethod
    def get_for_user(cls, user_id: int, state: FSMContext):
        """Получает или создаёт агента для пользователя"""
        import time
        if user_id not in _agents:
            agent = cls(user_id, state)
            _agents[user_id] = {
                'agent': agent,
                'last_used': time.time()
            }
            logger.info(f"🤖 Created new agent for user {user_id}")
        else:
            # Обновляем время последнего использования
            _agents[user_id]['last_used'] = time.time()
            _agents[user_id]['agent'].last_used = time.time()
        
        return _agents[user_id]['agent']

    @classmethod
    def cleanup_inactive(cls, max_age_hours: int = 1):
        """Очищает неактивных агентов"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        to_remove = []
        
        for user_id, agent_data in _agents.items():
            age_seconds = current_time - agent_data['last_used']
            if age_seconds > max_age_seconds:
                to_remove.append(user_id)
                logger.info(f"🧹 Agent for user {user_id} inactive for {age_seconds/3600:.1f}h")
        
        for user_id in to_remove:
            del _agents[user_id]
            logger.info(f"🗑️ Cleaned up agent for user {user_id}")
        
        if to_remove:
            logger.info(f"🧹 Cleaned {len(to_remove)} inactive agents. Active agents: {len(_agents)}")
        else:
            logger.debug(f"🧹 No inactive agents to clean. Active agents: {len(_agents)}")
