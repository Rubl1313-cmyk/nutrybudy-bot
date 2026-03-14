"""
🍽️ Meal Planner - Распределение калорий по приемам пищи
✨ Умное распределение КБЖУ на день
🎯 Учитывает цели и предпочтения пользователя
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MealPlanner:
    """Планировщик приемов пищи"""
    
    def __init__(self):
        self.meal_types = {
            "breakfast": {"name": "Завтрак", "percentage": 0.25, "time_range": (7, 10)},
            "lunch": {"name": "Обед", "percentage": 0.35, "time_range": (12, 14)},
            "dinner": {"name": "Ужин", "percentage": 0.30, "time_range": (18, 20)},
            "snack": {"name": "Перекус", "percentage": 0.10, "time_range": (10, 11)}
        }
    
    async def distribute_calories(
        self, 
        daily_calories: float,
        daily_protein: float,
        daily_fat: float,
        daily_carbs: float,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Распределить калории и КБЖУ по приемам пищи
        
        Args:
            daily_calories: Дневная норма калорий
            daily_protein: Дневная норма белка
            daily_fat: Дневная норма жиров
            daily_carbs: Дневная норма углеводов
            preferences: Предпочтения пользователя
            
        Returns:
            Dict с распределенным планом
        """
        try:
            logger.info(f"🍽️ Meal Planner: распределяю {daily_calories} ккал на день")
            
            preferences = preferences or {}
            
            # Распределяем по приемам пищи
            meal_plan = {}
            total_assigned = 0
            
            for meal_type, meal_info in self.meal_types.items():
                if meal_type == "snack" and not preferences.get("include_snacks", True):
                    continue
                
                percentage = meal_info["percentage"]
                
                # Корректируем процент в зависимости от предпочтений
                if preferences.get(f"skip_{meal_type}", False):
                    continue
                
                if preferences.get(f"large_{meal_type}", False):
                    percentage += 0.05
                
                # Рассчитываем КБЖУ для приема пищи
                meal_calories = daily_calories * percentage
                meal_protein = daily_protein * percentage
                meal_fat = daily_fat * percentage
                meal_carbs = daily_carbs * percentage
                
                meal_plan[meal_type] = {
                    "name": meal_info["name"],
                    "time_range": meal_info["time_range"],
                    "calories": round(meal_calories, 1),
                    "protein": round(meal_protein, 1),
                    "fat": round(meal_fat, 1),
                    "carbs": round(meal_carbs, 1),
                    "percentage": round(percentage * 100, 1),
                    "suggestions": await self._get_meal_suggestions(
                        meal_type, 
                        meal_calories,
                        preferences
                    )
                }
                
                total_assigned += percentage
            
            # Проверяем что все калории распределены
            if total_assigned < 1.0:
                remaining = 1.0 - total_assigned
                # Добавляем остаток к основному приему пищи
                main_meal = preferences.get("main_meal", "dinner")
                if main_meal in meal_plan:
                    meal_plan[main_meal]["calories"] += daily_calories * remaining
                    meal_plan[main_meal]["protein"] += daily_protein * remaining
                    meal_plan[main_meal]["fat"] += daily_fat * remaining
                    meal_plan[main_meal]["carbs"] += daily_carbs * remaining
                    meal_plan[main_meal]["percentage"] += round(remaining * 100, 1)
            
            logger.info(f"🍽️ Meal Planner: успешно распределено {len(meal_plan)} приемов пищи")
            
            return {
                "success": True,
                "daily_targets": {
                    "calories": daily_calories,
                    "protein": daily_protein,
                    "fat": daily_fat,
                    "carbs": daily_carbs
                },
                "meal_plan": meal_plan,
                "total_meals": len(meal_plan),
                "preferences": preferences
            }
            
        except Exception as e:
            logger.error(f"🍽️ Meal Planner: ошибка распределения {e}")
            return {
                "success": False,
                "error": str(e),
                "meal_plan": {}
            }
    
    async def _get_meal_suggestions(
        self, 
        meal_type: str, 
        calories: float,
        preferences: Dict[str, Any]
    ) -> List[str]:
        """Получить предложения для приема пищи"""
        try:
            # База предложений по типам приема пищи
            suggestions_db = {
                "breakfast": [
                    "Овсяная каша с ягодами и орехами",
                    "Яичница с цельнозерновым хлебом",
                    "Гречневая каша с молоком",
                    "Творог с фруктами",
                    "Смузи с протеином"
                ],
                "lunch": [
                    "Куриная грудка с гречкой и овощами",
                    "Запеченная рыба с рисом",
                    "Суп с цельнозерновым хлебом",
                    "Паста с индейкой и томатным соусом",
                    "Салат с курицей и авокадо"
                ],
                "dinner": [
                    "Запеченная курица с овощами",
                    "Рыба на гриле с салатом",
                    "Творожная запеканка",
                    "Овощное рагу с индейкой",
                    "Легкий суп с цельнозерновыми хлебцами"
                ],
                "snack": [
                    "Греческий йогурт с орехами",
                    "Яблоко с арахисовой пастой",
                    "Протеиновый батончик",
                    "Орехи и сухофрукты",
                    "Морковь с хумусом"
                ]
            }
            
            base_suggestions = suggestions_db.get(meal_type, [])
            
            # Фильтруем по предпочтениям
            filtered_suggestions = []
            for suggestion in base_suggestions:
                # Проверяем диетические ограничения
                if preferences.get("vegetarian", False) and any(
                    word in suggestion.lower() for word in ["курица", "мясо", "рыба", "индейка"]
                ):
                    continue
                
                if preferences.get("no_dairy", False) and any(
                    word in suggestion.lower() for word in ["молоко", "творог", "йогурт", "сыр"]
                ):
                    continue
                
                filtered_suggestions.append(suggestion)
            
            # Если после фильтрации ничего не осталось, возвращаем базовые
            if not filtered_suggestions:
                filtered_suggestions = base_suggestions[:3]
            
            return filtered_suggestions[:3]  # Возвращаем до 3 предложений
            
        except Exception as e:
            logger.error(f"🍽️ Meal Planner: ошибка получения предложений {e}")
            return []
    
    async def optimize_meal_timing(
        self, 
        meal_plan: Dict[str, Any], 
        schedule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Оптимизировать время приемов пищи под расписание
        
        Args:
            meal_plan: План приемов пищи
            schedule: Расписание пользователя
            
        Returns:
            Оптимизированный план с временем
        """
        try:
            optimized_plan = {}
            
            for meal_type, meal_info in meal_plan.items():
                if meal_type not in self.meal_types:
                    continue
                
                time_range = self.meal_types[meal_type]["time_range"]
                preferred_time = schedule.get(f"{meal_type}_time")
                
                if preferred_time:
                    # Используем предпочтительное время
                    meal_info["preferred_time"] = preferred_time
                else:
                    # Рекомендуем время из диапазона
                    meal_info["recommended_time"] = f"{time_range[0]}:00"
                
                optimized_plan[meal_type] = meal_info
            
            return {
                "success": True,
                "optimized_plan": optimized_plan,
                "schedule_tips": self._get_schedule_tips(schedule)
            }
            
        except Exception as e:
            logger.error(f"🍽️ Meal Planner: ошибка оптимизации времени {e}")
            return {
                "success": False,
                "error": str(e),
                "optimized_plan": {}
            }
    
    def _get_schedule_tips(self, schedule: Dict[str, Any]) -> List[str]:
        """Получить советы по расписанию"""
        tips = []
        
        if schedule.get("wake_time", 0) < 6:
            tips.append("Ранний подъем - рекомендуем легкий завтрак в 6:30")
        
        if schedule.get("sleep_time", 0) > 23:
            tips.append("Поздний отход ко сну - избегайте плотного ужина после 20:00")
        
        if schedule.get("work_start", 0) <= 8:
            tips.append("Ранний начало работы - подготовьте завтрак с вечера")
        
        return tips

# Глобальный экземпляр
meal_planner = MealPlanner()

# Удобная функция для использования
async def distribute_calories(
    daily_calories: float,
    daily_protein: float,
    daily_fat: float,
    daily_carbs: float,
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Распределить калории по приемам пищи"""
    return await meal_planner.distribute_calories(
        daily_calories, daily_protein, daily_fat, daily_carbs, preferences
    )
