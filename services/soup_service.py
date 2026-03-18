"""
Сервис для хранения супов (еда + жидкость)
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from database.db import get_session
from database.models import User, Meal, FoodItem
from utils.unit_converter import convert_to_grams

logger = logging.getLogger(__name__)

# База данных по супам для расчета содержания воды
SOUP_WATER_CONTENT = {
    'борщ': 0.85,        # 85% жидкости
    'щи': 0.88,
    'суп': 0.85,         # Обычный суп
    'уха': 0.90,
    'рассольник': 0.86,
    'солянка': 0.82,
    'окрошка': 0.92,
    'гуляш': 0.75,       # Более густой гуляш
    'рагу': 0.70,
    'картошка': 0.80,    # Картофельное рагу
}

# Средние значения КБЖУ для супов (на 100 мл)
SOUP_NUTRITION_DEFAULTS = {
    'calories': 50,
    'protein': 2.0,
    'fat': 2.0,
    'carbs': 5.0
}

def is_soup(dish_name: str) -> bool:
    """
    Определяет, является ли блюдо супом
    """
    dish_name = dish_name.lower()
    
    # Применим названия
    soup_keywords = ['борщ', 'щи', 'уха', 'суп', 'рассольник', 'солянка', 'окрошка', 'бульон']
    
    for keyword in soup_keywords:
        if keyword in dish_name:
            return True
    
    # Проверяем по базе COMPOSITE_DISHES
    from services.food_service import COMPOSITE_DISHES, normalize_ai_dish_name
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
    from services.food_service import COMPOSITE_DISHES, normalize_ai_dish_name
    dish_key = normalize_ai_dish_name(dish_name)
    dish_info = COMPOSITE_DISHES.get(dish_key)
    
    if dish_info and 'nutrition' in dish_info:
        nutrition = dish_info['nutrition']
        factor = volume_ml / 100
        return {
            'calories': nutrition.get('calories', 50) * factor,
            'protein': nutrition.get('protein', 2.0) * factor,
            'fat': nutrition.get('fat', 2.0) * factor,
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
    Сохраняет суп как прием пищи и как запись жидкости
    
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
            
            # 1. Сохраняем как прием пищи (Meal)
            meal = Meal(
                user_id=user.id,
                meal_type=meal_type,
                date=datetime.now(timezone.utc).date(),
                created_at=datetime.now(timezone.utc),
                total_calories=nutrition['calories'],
                total_protein=nutrition['protein'],
                total_fat=nutrition['fat'],
                total_carbs=nutrition['carbs'],
                ai_description=f"{dish_name} ({volume_ml} мл)"
            )
            session.add(meal)
            await session.flush()
            
            # 2. Сохраняем ингредиенты для супа
            food_item = FoodItem(
                meal_id=meal.id,
                name=dish_name,
                quantity=volume_ml,
                unit='мл',
                calories=nutrition['calories'],
                protein=nutrition['protein'],
                fat=nutrition['fat'],
                carbs=nutrition['carbs'],
                created_at=datetime.now(timezone.utc)
            )
            session.add(food_item)
            
            # 3. Сохраняем как запись воды (если есть поддержка)
            try:
                from database.models import WaterEntry
                
                water_entry = WaterEntry(
                    user_id=user.id,
                    date=datetime.now(timezone.utc).date(),
                    volume_ml=water_volume,
                    drink_name=dish_name,
                    calories_from_food=nutrition['calories'],
                    created_at=datetime.now(timezone.utc)
                )
                session.add(water_entry)
                
            except ImportError:
                # Если модели WaterEntry нет, просто логируем
                logger.info(f"[SOUP] Water volume calculated: {water_volume}ml for {dish_name}")
            
            await session.commit()
            
            logger.info(f"[SOUP] Saved soup: {dish_name} {volume_ml}ml for user {user_id}")
            
            return {
                'meal_id': meal.id,
                'food_item_id': food_item.id,
                'water_volume': water_volume,
                'nutrition': nutrition
            }
            
    except Exception as e:
        logger.error(f"[SOUP] Error saving soup: {e}")
        raise

def get_soup_categories() -> Dict[str, list]:
    """
    Возвращает категории супов
    """
    return {
        'russian': ['борщ', 'щи', 'рассольник', 'солянка', 'уха'],
        'international': ['суп', 'бульон', 'гуляш', 'рагу'],
        'summer': ['окрошка'],
        'hearty': ['гуляш', 'рагу', 'картошка']
    }

def suggest_similar_soups(soup_name: str) -> list:
    """
    Предлагает похожие супы
    """
    soup_name = soup_name.lower()
    suggestions = []
    
    categories = get_soup_categories()
    
    for category, soups in categories.items():
        for soup in soups:
            if soup != soup_name and any(word in soup_name for word in soup.split()[:2]):
                suggestions.append(soup)
    
    return suggestions[:5]  # Максимум 5 предложений

def calculate_total_liquid(meal_items: list) -> float:
    """
    Рассчитывает общее количество жидкости в приеме пищи
    """
    total_liquid = 0.0
    
    for item in meal_items:
        if is_soup(item['name']):
            volume = convert_to_grams(item['quantity'], item.get('unit', 'г'))
            water_content = get_soup_water_content(item['name'])
            total_liquid += volume * water_content
    
    return total_liquid

async def analyze_user_soup_preferences(user_id: int) -> Dict:
    """
    Анализирует предпочтения пользователя по супам
    """
    try:
        async with get_session() as session:
            # Получаем все приемы супов пользователя
            result = await session.execute(
                select(Meal, FoodItem)
                .join(FoodItem, Meal.id == FoodItem.meal_id)
                .where(
                    Meal.user_id == user_id,
                    Meal.ai_description.ilike('%борщ%') |
                    Meal.ai_description.ilike('%щи%') |
                    Meal.ai_description.ilike('%суп%') |
                    Meal.ai_description.ilike('%уха%')
                )
                .order_by(Meal.date.desc())
            )
            
            soup_records = result.all()
            
            if not soup_records:
                return {
                    'total_soups': 0,
                    'favorite_types': [],
                    'avg_volume': 0,
                    'last_soups': []
                }
            
            # Анализируем данные
            soup_types = {}
            volumes = []
            last_soups = []
            
            for meal, food_item in soup_records[:20]:  # Последние 20 записей
                soup_name = food_item.name
                volume = food_item.quantity
                
                # Считаем типы супов
                soup_type = 'other'
                for category, soups in get_soup_categories().items():
                    if any(soup in soup_name.lower() for soup in soups):
                        soup_type = category
                        break
                
                soup_types[soup_type] = soup_types.get(soup_type, 0) + 1
                volumes.append(volume)
                
                last_soups.append({
                    'name': soup_name,
                    'volume': volume,
                    'date': meal.date
                })
            
            # Сортируем по популярности
            favorite_types = sorted(soup_types.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'total_soups': len(soup_records),
                'favorite_types': favorite_types,
                'avg_volume': sum(volumes) / len(volumes) if volumes else 0,
                'last_soups': last_soups[:10]
            }
            
    except Exception as e:
        logger.error(f"[SOUP] Error analyzing preferences: {e}")
        return {
            'total_soups': 0,
            'favorite_types': [],
            'avg_volume': 0,
            'last_soups': []
        }

def get_soup_nutrition_tips(soup_name: str) -> list:
    """
    Возвращает советы по питательности для супа
    """
    tips = []
    soup_name = soup_name.lower()
    
    # Общие советы для всех супов
    tips.append("Супы помогают поддерживать водный баланс")
    tips.append("Горячие супы улучшают пищеварение")
    
    # Специфические советы
    if 'борщ' in soup_name:
        tips.append("Борщ богат клетчаткой и витаминами")
        tips.append("Свекла в борще улучшает состав крови")
    
    elif 'щи' in soup_name:
        tips.append("Щи содержат много витамина C")
        tips.append("Капуста в щах полезна для пищеварения")
    
    elif 'уха' in soup_name:
        tips.append("Уха богата омега-3 жирными кислотами")
        tips.append("Рыбный бульон укрепляет иммунитет")
    
    elif 'окрошка' in soup_name:
        tips.append("Окрошка освежает в жаркую погоду")
        tips.append("Квас в окрошке улучшает микрофлору кишечника")
    
    elif 'гуляш' in soup_name or 'рагу' in soup_name:
        tips.append("Густые супы более сытные")
        tips.append("Мясо в супе обеспечивает белком")
    
    return tips[:5]  # Максимум 5 советов

async def get_daily_soup_stats(user_id: int, target_date: datetime.date = None) -> Dict:
    """
    Возвращает статистику по супам за день
    """
    try:
        if target_date is None:
            target_date = datetime.now(timezone.utc).date()
        
        async with get_session() as session:
            # Получаем все супы за день
            result = await session.execute(
                select(Meal, FoodItem)
                .join(FoodItem, Meal.id == FoodItem.meal_id)
                .where(
                    Meal.user_id == user_id,
                    Meal.date == target_date,
                    Meal.ai_description.ilike('%борщ%') |
                    Meal.ai_description.ilike('%щи%') |
                    Meal.ai_description.ilike('%суп%') |
                    Meal.ai_description.ilike('%уха%')
                )
            )
            
            soup_records = result.all()
            
            if not soup_records:
                return {
                    'total_soups': 0,
                    'total_volume': 0,
                    'total_liquid': 0,
                    'total_calories': 0,
                    'soup_types': {}
                }
            
            total_volume = 0
            total_liquid = 0
            total_calories = 0
            soup_types = {}
            
            for meal, food_item in soup_records:
                volume = food_item.quantity
                soup_name = food_item.name
                
                total_volume += volume
                total_liquid += calculate_total_liquid([{
                    'name': soup_name,
                    'quantity': volume,
                    'unit': 'мл'
                }])
                total_calories += meal.total_calories
                
                # Считаем типы
                soup_type = 'other'
                for category, soups in get_soup_categories().items():
                    if any(soup in soup_name.lower() for soup in soups):
                        soup_type = category
                        break
                
                soup_types[soup_type] = soup_types.get(soup_type, 0) + 1
            
            return {
                'total_soups': len(soup_records),
                'total_volume': total_volume,
                'total_liquid': total_liquid,
                'total_calories': total_calories,
                'soup_types': soup_types
            }
            
    except Exception as e:
        logger.error(f"[SOUP] Error getting daily stats: {e}")
        return {
            'total_soups': 0,
            'total_volume': 0,
            'total_liquid': 0,
            'total_calories': 0,
            'soup_types': {}
        }
