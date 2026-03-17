"""
Сервис для сохранения супов (еда + жидкость)
"""
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from database.db import get_session
from database.models import User, Meal, DrinkEntry
from services.dish_db import COMPOSITE_DISHES, normalize_ai_dish_name
from utils.drink_parser import parse_drink

logger = logging.getLogger(__name__)

# База данных по супам для расчёта содержания воды
SOUP_WATER_CONTENT = {
    'борщ': 0.85,        # 85% жидкости
    'щи': 0.88,
    'суп': 0.85,         # Обычный суп
    'уха': 0.90,
    'рассольник': 0.86,
    'солянка': 0.82,
    'окрошка': 0.92,
    'гуляш': 0.75,       # Более густой
    'рагу': 0.70,
    'картошка': 0.80,    # Картофельное рагу
}

# Средние значения КБЖУ для супов (на 100 мл)
SOUP_NUTRITION_DEFAULTS = {
    'calories': 50,
    'protein': 2.0,
    'fat': 1.5,
    'carbs': 5.0,
}

def is_soup(dish_name: str) -> bool:
    """
    Определяет, является ли блюдо супом
    """
    dish_name = dish_name.lower()
    
    # Прямые названия
    soup_keywords = ['борщ', 'щи', 'уха', 'суп', 'рассольник', 'солянка', 'окрошка', 'бульон']
    
    for keyword in soup_keywords:
        if keyword in dish_name:
            return True
    
    # Проверяем по базе COMPOSITE_DISHES
    dish_key = normalize_ai_dish_name(dish_name)
    dish_info = COMPOSITE_DISHES.get(dish_key)
    
    if dish_info and dish_info.get('category') == 'soup':
        return True
    
    return False

def get_soup_water_content(dish_name: str) -> float:
    """
    Определяет содержание воды в супе
    """
    dish_name = dish_name.lower()
    
    # Ищем точное совпадение
    for soup_name, water_content in SOUP_WATER_CONTENT.items():
        if soup_name in dish_name:
            return water_content
    
    # По умолчанию - 85% воды
    return 0.85

def get_soup_nutrition(dish_name: str, volume_ml: float) -> dict:
    """
    Рассчитывает КБЖУ для супа
    
    Args:
        dish_name: Название супа
        volume_ml: Объём в мл
        
    Returns:
        dict с калориями, белками, жирами, углеводами
    """
    # Проверяем базу COMPOSITE_DISHES
    dish_key = normalize_ai_dish_name(dish_name)
    dish_info = COMPOSITE_DISHES.get(dish_key)
    
    if dish_info and 'nutrition_per_100' in dish_info:
        nutrition = dish_info['nutrition_per_100']
        factor = volume_ml / 100
        
        return {
            'calories': nutrition.get('calories', 50) * factor,
            'protein': nutrition.get('protein', 2.0) * factor,
            'fat': nutrition.get('fat', 1.5) * factor,
            'carbs': nutrition.get('carbs', 5.0) * factor,
        }
    else:
        # Используем значения по умолчанию
        factor = volume_ml / 100
        return {
            key: value * factor 
            for key, value in SOUP_NUTRITION_DEFAULTS.items()
        }

async def save_soup(user_id: int, dish_name: str, volume_ml: float, meal_type: str = "soup"):
    """
    Сохраняет суп как приём пищи и как запись жидкости
    
    Returns:
        dict с ID созданных записей
    """
    try:
        # Рассчитываем КБЖУ
        nutrition = get_soup_nutrition(dish_name, volume_ml)
        
        # Рассчитываем объём жидкости
        water_content = get_soup_water_content(dish_name)
        water_volume = volume_ml * water_content
        
        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # 1. Сохраняем как приём пищи (Meal)
            meal = Meal(
                user_id=user.id,
                meal_type=meal_type,
                datetime=datetime.now(),
                total_calories=nutrition['calories'],
                total_protein=nutrition['protein'],
                total_fat=nutrition['fat'],
                total_carbs=nutrition['carbs'],
                ai_description=f"{dish_name} ({volume_ml} мл)"
            )
            session.add(meal)
            await session.flush()
            
            # 2. Сохраняем жидкость (DrinkEntry)
            drink = DrinkEntry(
                user_id=user.id,
                name=f"вода из {dish_name}",
                volume_ml=water_volume,
                calories=0.0,  # Воду из супа считаем безкалорийной
                source='food',  # Источник - еда (суп)
                reference_id=meal.id,  # Ссылка на связанный прием пищи
                datetime=datetime.now(timezone.utc)
            )
            session.add(drink)
            await session.commit()
            
            logger.info(f"🍲 Суп сохранён: {dish_name} {volume_ml}мл = {nutrition['calories']:.1f}ккал + {water_volume:.0f}мл воды")
            
            return {
                "meal_id": meal.id,
                "drink_id": drink.id,
                "calories": nutrition['calories'],
                "water_volume": water_volume
            }
            
    except Exception as e:
        logger.error(f"Ошибка при сохранении супа: {e}")
        raise

async def save_drink(user_id: int, text: str):
    """
    Сохраняет напиток из текстового описания
    
    Returns:
        dict с информацией о сохранённом напитке
    """
    try:
        # Парсим напиток
        volume, drink_name, calories = await parse_drink(text)
        
        if not volume:
            raise ValueError("Не удалось определить объём напитка")
        
        async with get_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Сохраняем напиток
            drink = DrinkEntry(
                user_id=user.id,
                name=drink_name,
                volume_ml=volume,
                calories=calories,
                source='drink',  # Источник - напиток
                datetime=datetime.now(timezone.utc)
            )
            session.add(drink)
            await session.commit()
            
            logger.info(f"🥤 Напиток сохранён: {drink_name} {volume}мл, {calories:.1f}ккал")
            
            return {
                "drink_id": drink.id,
                "name": drink_name,
                "volume": volume,
                "calories": calories
            }
            
    except Exception as e:
        logger.error(f"Ошибка при сохранении напитка: {e}")
        raise
