"""
services/langchain_agent.py
LangChain Agent Ñ� Ğ¸Ğ½Ñ�Ñ‚Ñ€ÑƒĞ¼ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸ Ğ´Ğ»Ñ� Ğ°Ğ²Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ¸Ğ·Ğ°Ñ†Ğ¸Ğ¸ NutriBuddy Bot
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

# ĞšĞµÑˆ Ğ°Ğ³ĞµĞ½Ñ‚Ğ¾Ğ² Ñ� Ğ¾Ñ‚Ñ�Ğ»ĞµĞ¶Ğ¸Ğ²Ğ°Ğ½Ğ¸ĞµĞ¼ Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ¸ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ�
_agents: Dict[int, Dict[str, Any]] = {}

class LangChainAgent:
    """AI Ğ°Ğ³ĞµĞ½Ñ‚ Ñ� Ğ¸Ğ½Ñ�Ñ‚Ñ€ÑƒĞ¼ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸ Ğ´Ğ»Ñ� NutriBuddy"""
    
    def __init__(self, user_id: int, state: FSMContext):
        self.user_id = user_id
        self.state = state
        self.llm = CloudflareLLM()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.user = None
        self.tools = self._create_tools()
        self.last_used = time.time()
        
        # LLM Ğ²Ñ�ĞµĞ³Ğ´Ğ° Ğ´Ğ¾Ñ�Ñ‚ÑƒĞ¿ĞµĞ½ (Ğ±ĞµĞ· Ñ�Ğ¼ÑƒĞ»Ñ�Ñ†Ğ¸Ğ¸)
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
        logger.info(f"âœ… LangChain Agent initialized for user {user_id}")

    async def load_user(self):
        """Ğ—Ğ°Ğ³Ñ€ÑƒĞ¶Ğ°ĞµÑ‚ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ¸Ğ· Ğ‘Ğ”"""
        try:
            async with get_session() as session:
                result = await session.execute(select(User).where(User.telegram_id == self.user_id))
                self.user = result.scalar_one_or_none()
                if self.user:
                    logger.info(f"âœ… User loaded: {self.user.first_name}")
                else:
                    logger.warning(f"âš ï¸� User not found: {self.user_id}")
        except Exception as e:
            logger.error(f"â�Œ Error loading user {self.user_id}: {e}")
            self.user = None

    def _get_prompt(self) -> str:
        return """Ğ¢Ñ‹ â€” Ğ¿Ñ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ AI-Ğ°Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚ Ğ¿Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� NutriBuddy.
Ğ¢Ğ²Ğ¾Ñ� Ğ·Ğ°Ğ´Ğ°Ñ‡Ğ° â€” Ğ¿Ğ¾Ğ½Ñ�Ñ‚ÑŒ, Ñ‡Ñ‚Ğ¾ Ñ…Ğ¾Ñ‡ĞµÑ‚ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ, Ğ¸ Ğ²Ñ‹Ğ·Ğ²Ğ°Ñ‚ÑŒ Ğ¿Ğ¾Ğ´Ñ…Ğ¾Ğ´Ñ�Ñ‰Ğ¸Ğ¹ Ğ¸Ğ½Ñ�Ñ‚Ñ€ÑƒĞ¼ĞµĞ½Ñ‚.
Ğ’Ñ�ĞµĞ³Ğ´Ğ° Ğ¾Ñ‚Ğ²ĞµÑ‡Ğ°Ğ¹ ĞºÑ€Ğ°Ñ�Ğ¸Ğ²Ğ¾, Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒÑ� Ñ�Ğ¼Ğ¾Ğ´Ğ·Ğ¸ Ğ¸ Ñ�Ñ‚Ñ€ÑƒĞºÑ‚ÑƒÑ€Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ñ‚ĞµĞºÑ�Ñ‚.

Ğ˜Ğ½Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ†Ğ¸Ñ� Ğ¾ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ğµ:
{user_info}

Ğ”Ğ¾Ñ�Ñ‚ÑƒĞ¿Ğ½Ñ‹Ğµ Ğ¸Ğ½Ñ�Ñ‚Ñ€ÑƒĞ¼ĞµĞ½Ñ‚Ñ‹:
{tools}

Ğ˜Ñ�Ñ‚Ğ¾Ñ€Ğ¸Ñ� Ğ´Ğ¸Ğ°Ğ»Ğ¾Ğ³Ğ°:
{chat_history}

Ğ—Ğ°Ğ¿Ñ€Ğ¾Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�: {input}
{agent_scratchpad}"""

    def _create_tools(self) -> List[StructuredTool]:
        """Ğ¡Ğ¾Ğ·Ğ´Ğ°Ñ‘Ñ‚ Ğ¸Ğ½Ñ�Ñ‚Ñ€ÑƒĞ¼ĞµĞ½Ñ‚Ñ‹ Ğ´Ğ»Ñ� Ğ°Ğ³ĞµĞ½Ñ‚Ğ°"""
        
        async def log_meal(description: str) -> str:
            """Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸. description: Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¸Ğµ ĞµĞ´Ñ‹ (Ğ½Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€, "200Ğ³ ĞºÑƒÑ€Ğ¸Ñ†Ñ‹ Ñ� Ğ³Ñ€ĞµÑ‡ĞºĞ¾Ğ¹"). Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºÑƒ Ñ� ĞšĞ‘Ğ–Ğ£."""
            try:
                # ĞŸĞ°Ñ€Ñ�Ğ¸Ğ¼ ĞµĞ´Ñƒ Ñ‡ĞµÑ€ĞµĞ· ai_processor
                result = await ai_processor.process_text_input(description, self.user_id)
                if not result.get("success"):
                    return "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ñ‚ÑŒ ĞµĞ´Ñƒ. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ¿Ğ¾Ğ´Ñ€Ğ¾Ğ±Ğ½ĞµĞµ."
                
                food_items = result["parameters"].get("food_items", [])
                meal_type = result["parameters"].get("meal_type", "main")
                
                if not food_items:
                    return "â�Œ Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹ Ğ² Ğ²Ğ°ÑˆĞµĞ¼ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğ¸."
                
                # ĞšĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¸Ğ· Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ° _per_100g Ğ² Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚ Ğ´Ğ»Ñ� save_food_to_db
                converted_food_items = []
                for item in food_items:
                    weight = item.get('quantity', 0)
                    factor = weight / 100.0
                    
                    converted_item = {
                        'name': item.get('name', 'Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚'),
                        'quantity': weight,
                        'unit': item.get('unit', 'Ğ³'),
                        'calories': item.get('calories_per_100g', 0) * factor,
                        'protein': item.get('protein_per_100g', 0) * factor,
                        'fat': item.get('fat_per_100g', 0) * factor,
                        'carbs': item.get('carbs_per_100g', 0) * factor
                    }
                    converted_food_items.append(converted_item)
                
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ‡ĞµÑ€ĞµĞ· save_food_to_db Ñ� ĞºĞ¾Ğ½Ğ²ĞµÑ€Ñ‚Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¼Ğ¸ Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸
                save_result = await food_save_service.save_food_to_db(
                    self.user_id, 
                    converted_food_items, 
                    meal_type
                )
                
                if not save_result.get("success"):
                    return f"â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�: {save_result.get('error', 'Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ°Ñ� Ğ¾ÑˆĞ¸Ğ±ĞºĞ°')}"
                
                # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ´Ğ½ĞµĞ²Ğ½ÑƒÑ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ
                daily_stats = await get_daily_stats(self.user_id)
                
                # Ğ¤Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¸Ğµ Ğ¸Ğ· Ğ¸Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ğ¾Ğ²
                description_from_items = ", ".join([
                    f"{item.get('quantity','')} {item.get('unit','Ğ³')} {item['name']}" 
                    for item in food_items
                ])
                
                # Ğ¤Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ¸Ñ€ÑƒĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ´Ğ»Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ¸
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
                logger.error(f"â�Œ Error in log_meal: {e}")
                return error_card("ai", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğ¸ ĞµĞ´Ñ‹: {str(e)}")

        async def log_water(amount_ml: int) -> str:
            """Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ²Ñ‹Ğ¿Ğ¸Ñ‚ÑƒÑ� Ğ²Ğ¾Ğ´Ñƒ. amount_ml: ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ğ² Ğ¼Ğ¸Ğ»Ğ»Ğ¸Ğ»Ğ¸Ñ‚Ñ€Ğ°Ñ…."""
            try:
                from services.soup_service import save_drink
                
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼
                result = await save_drink(self.user_id, f"Ğ²Ğ¾Ğ´Ğ° {amount_ml} Ğ¼Ğ»")
                
                # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ·Ğ° Ğ´ĞµĞ½ÑŒ
                total_today = await get_daily_water(self.user_id)
                return water_card(amount_ml, total_today, self.user.daily_water_goal)
                
            except Exception as e:
                logger.error(f"â�Œ Error in log_water: {e}")
                return error_card("database", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²Ğ¾Ğ´Ñ‹: {str(e)}")

        async def log_drink(description: str) -> str:
            """Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº. description: Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¸Ğµ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ° (Ğ½Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€, "Ñ�Ğ¾Ğº 250 Ğ¼Ğ»")."""
            try:
                from services.soup_service import save_drink
                
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼
                result = await save_drink(self.user_id, description)
                
                # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ·Ğ° Ğ´ĞµĞ½ÑŒ
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
                logger.error(f"â�Œ Error in log_drink: {e}")
                return error_card("database", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°: {str(e)}")

        async def log_weight(weight_kg: float) -> str:
            """Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ²ĞµÑ�. weight_kg: Ğ²ĞµÑ� Ğ² ĞºĞ¸Ğ»Ğ¾Ğ³Ñ€Ğ°Ğ¼Ğ¼Ğ°Ñ…."""
            try:
                from services.weight_service import save_weight
                
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼
                result = await save_weight(self.user_id, weight_kg)
                
                return weight_card(
                    weight_kg, 
                    result.get('change'), 
                    self.user.goal_weight
                )
                
            except Exception as e:
                logger.error(f"â�Œ Error in log_weight: {e}")
                return error_card("database", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ°: {str(e)}")

        async def log_activity(activity_type: str, duration_min: int) -> str:
            """Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ. activity_type: Ñ‚Ğ¸Ğ¿ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸, duration_min: Ğ´Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ Ğ² Ğ¼Ğ¸Ğ½ÑƒÑ‚Ğ°Ñ…."""
            try:
                from services.activity_service import save_activity
                from utils.activity_calculator import calculate_activity_calorie_goal
                from database.db import get_session
                from database.models import User
                from sqlalchemy import select
                
                # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼
                result = await save_activity(self.user_id, activity_type, duration_min)
                
                # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ·Ğ° Ğ´ĞµĞ½ÑŒ
                daily_total = await get_daily_activity_calories(self.user_id)
                
                # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ� Ğ´Ğ»Ñ� Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚Ğ° Ñ†ĞµĞ»Ğ¸
                async with get_session() as session:
                    user_result = await session.execute(
                        select(User).where(User.telegram_id == self.user_id)
                    )
                    user = user_result.scalar_one_or_none()
                
                # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¿ĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½ÑƒÑ� Ñ†ĞµĞ»ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
                if user:
                    activity_goal = calculate_activity_calorie_goal(user)
                else:
                    activity_goal = 300  # Ğ—Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ Ğ¿Ğ¾ ÑƒĞ¼Ğ¾Ğ»Ñ‡Ğ°Ğ½Ğ¸Ñ�
                
                return activity_card(
                    activity_type, 
                    duration_min, 
                    result.get('calories', 0),
                    daily_total,
                    activity_goal  # ĞŸĞµÑ€Ñ�Ğ¾Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ� Ñ†ĞµĞ»ÑŒ
                )
                
            except Exception as e:
                logger.error(f"â�Œ Error in log_activity: {e}")
                return error_card("database", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸: {str(e)}")

        async def show_progress(period: str = "Ğ´ĞµĞ½ÑŒ") -> str:
            """ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�. period: Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´ (Ğ´ĞµĞ½ÑŒ, Ğ½ĞµĞ´ĞµĞ»Ñ�, Ğ¼ĞµÑ�Ñ�Ñ†, Ğ²Ñ�Ñ‘ Ğ²Ñ€ĞµĞ¼Ñ�)."""
            try:
                from services.progress_service import get_progress_stats
                
                stats = await get_progress_stats(self.user_id, period)
                return progress_card(stats, period)
                
            except Exception as e:
                logger.error(f"â�Œ Error in show_progress: {e}")
                return error_card("database", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ¿Ğ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ¸Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°: {str(e)}")

        return [
            StructuredTool.from_function(
                coroutine=log_meal,
                name="log_meal",
                description="Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸. Ğ’Ñ…Ğ¾Ğ´: Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¸Ğµ ĞµĞ´Ñ‹."
            ),
            StructuredTool.from_function(
                coroutine=log_water,
                name="log_water",
                description="Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ²Ñ‹Ğ¿Ğ¸Ñ‚ÑƒÑ� Ğ²Ğ¾Ğ´Ñƒ. Ğ’Ñ…Ğ¾Ğ´: ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ğ² Ğ¼Ğ¸Ğ»Ğ»Ğ¸Ğ»Ğ¸Ñ‚Ñ€Ğ°Ñ…."
            ),
            StructuredTool.from_function(
                coroutine=log_drink,
                name="log_drink",
                description="Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ½Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº. Ğ’Ñ…Ğ¾Ğ´: Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¸Ğµ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°."
            ),
            StructuredTool.from_function(
                coroutine=log_weight,
                name="log_weight",
                description="Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ²ĞµÑ�. Ğ’Ñ…Ğ¾Ğ´: Ğ²ĞµÑ� Ğ² ĞºĞ¸Ğ»Ğ¾Ğ³Ñ€Ğ°Ğ¼Ğ¼Ğ°Ñ…."
            ),
            StructuredTool.from_function(
                coroutine=log_activity,
                name="log_activity",
                description="Ğ—Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ. Ğ’Ñ…Ğ¾Ğ´: Ñ‚Ğ¸Ğ¿ Ğ¸ Ğ´Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ."
            ),
            StructuredTool.from_function(
                coroutine=show_progress,
                name="show_progress",
                description="ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµÑ‚ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�. Ğ’Ñ…Ğ¾Ğ´: Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´."
            )
        ]

    async def handle_text(self, text: str, message: Message):
        """Ğ�Ğ±Ñ€Ğ°Ğ±Ğ°Ñ‚Ñ‹Ğ²Ğ°ĞµÑ‚ Ñ‚ĞµĞºÑ�Ñ‚Ğ¾Ğ²Ğ¾Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ"""
        try:
            if not self.user:
                await self.load_user()
                if not self.user:
                    await message.answer("â�Œ Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ñ�Ğ¾Ğ·Ğ´Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ñ‡ĞµÑ€ĞµĞ· /set_profile")
                    return

            if not self.executor:
                await message.answer(
                    "ğŸ¤– AI Ğ°Ğ³ĞµĞ½Ñ‚ Ğ½ĞµĞ´Ğ¾Ñ�Ñ‚ÑƒĞ¿ĞµĞ½. ĞŸÑ€Ğ¾Ğ²ĞµÑ€ÑŒÑ‚Ğµ Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹ĞºĞ¸ Cloudflare.",
                    parse_mode="HTML"
                )
                return

            # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ğ¸Ğ½Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ†Ğ¸Ñ� Ğ¾ Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ğµ
            user_info = (
                f"Ğ˜Ğ¼Ñ�: {self.user.first_name}\n"
                f"Ğ’ĞµÑ�: {self.user.weight} ĞºĞ³\n"
                f"Ğ Ğ¾Ñ�Ñ‚: {self.user.height} Ñ�Ğ¼\n"
                f"Ğ¦ĞµĞ»ÑŒ: {self.user.goal}\n"
                f"Ğ”Ğ½ĞµĞ²Ğ½Ğ°Ñ� Ğ½Ğ¾Ñ€Ğ¼Ğ° ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹: {self.user.daily_calorie_goal} ĞºĞºĞ°Ğ»\n"
                f"Ğ�Ğ¾Ñ€Ğ¼Ğ° Ğ²Ğ¾Ğ´Ñ‹: {self.user.daily_water_goal} Ğ¼Ğ»"
            )

            # Ğ’Ñ‹Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ°Ğ³ĞµĞ½Ñ‚Ğ°
            response = await self.executor.ainvoke({
                "input": text,
                "user_info": user_info
            })

            # Ğ�Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ¾Ñ‚Ğ²ĞµÑ‚
            await message.answer(response["output"], parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"â�Œ Error in handle_text: {e}")
            await message.answer(
                error_card("general", f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ¸: {str(e)}"),
                parse_mode="HTML"
            )

    @classmethod
    def get_for_user(cls, user_id: int, state: FSMContext):
        """ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµÑ‚ Ğ¸Ğ»Ğ¸ Ñ�Ğ¾Ğ·Ğ´Ğ°Ñ‘Ñ‚ Ğ°Ğ³ĞµĞ½Ñ‚Ğ° Ğ´Ğ»Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
        import time
        if user_id not in _agents:
            agent = cls(user_id, state)
            _agents[user_id] = {
                'agent': agent,
                'last_used': time.time()
            }
            logger.info(f"ğŸ¤– Created new agent for user {user_id}")
        else:
            # Ğ�Ğ±Ğ½Ğ¾Ğ²Ğ»Ñ�ĞµĞ¼ Ğ²Ñ€ĞµĞ¼Ñ� Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½ĞµĞ³Ğ¾ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ�
            _agents[user_id]['last_used'] = time.time()
            _agents[user_id]['agent'].last_used = time.time()
        
        return _agents[user_id]['agent']

    @classmethod
    def cleanup_inactive(cls, max_age_hours: int = 1):
        """Ğ�Ñ‡Ğ¸Ñ‰Ğ°ĞµÑ‚ Ğ½ĞµĞ°ĞºÑ‚Ğ¸Ğ²Ğ½Ñ‹Ñ… Ğ°Ğ³ĞµĞ½Ñ‚Ğ¾Ğ²"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        to_remove = []
        
        for user_id, agent_data in _agents.items():
            age_seconds = current_time - agent_data['last_used']
            if age_seconds > max_age_seconds:
                to_remove.append(user_id)
                logger.info(f"ğŸ§¹ Agent for user {user_id} inactive for {age_seconds/3600:.1f}h")
        
        for user_id in to_remove:
            del _agents[user_id]
            logger.info(f"ğŸ—‘ï¸� Cleaned up agent for user {user_id}")
        
        if to_remove:
            logger.info(f"ğŸ§¹ Cleaned {len(to_remove)} inactive agents. Active agents: {len(_agents)}")
        else:
            logger.debug(f"ğŸ§¹ No inactive agents to clean. Active agents: {len(_agents)}")
