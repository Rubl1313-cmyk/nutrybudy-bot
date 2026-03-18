"""
utils/premium_templates.py
Премиальные шаблоны для ответов бота
"""
from typing import Dict, Optional
from utils.ui_templates import ProgressBar

def loading_card(message: str = "Processing...") -> str:
    """Loading card for async operations"""
    return f"""
[LOADING] <b>{message}</b>
⏳ Пожалуйста, подождите...
"""

def error_card(error_message: str, suggestion: str = "Try again later") -> str:
    """Error card for displaying errors"""
    return f"""
[ERROR] <b>Something went wrong</b>
❌ {error_message}

💡 <i>{suggestion}</i>
"""

def meal_card(food_data: Dict, user, daily_stats: Dict) -> str:
    """Красивая карточка приема пищи"""
    calories = food_data.get('calories', 0)
    protein = food_data.get('protein', 0)
    fat = food_data.get('fat', 0)
    carbs = food_data.get('carbs', 0)
    description = food_data.get('description', 'Блюдо')
    
    # Прогресс по калориям
    cal_progress = (daily_stats.get('calories', 0) / user.daily_calorie_goal * 100) if user.daily_calorie_goal else 0
    cal_bar = ProgressBar.create_modern_bar(cal_progress, 100, 12, 'neon')
    
    # Прогресс по БЖУ
    protein_progress = (daily_stats.get('protein', 0) / user.daily_protein_goal * 100) if user.daily_protein_goal else 0
    protein_bar = ProgressBar.create_modern_bar(protein_progress, 100, 8, 'protein')
    
    fat_progress = (daily_stats.get('fat', 0) / user.daily_fat_goal * 100) if user.daily_fat_goal else 0
    fat_bar = ProgressBar.create_modern_bar(fat_progress, 100, 8, 'fat')
    
    carbs_progress = (daily_stats.get('carbs', 0) / user.daily_carbs_goal * 100) if user.daily_carbs_goal else 0
    carbs_bar = ProgressBar.create_modern_bar(carbs_progress, 100, 8, 'carbs')
    
    return f"""
[FOOD] <b>Прием пищи записан!</b>

{'=' * 35}
[FOOD] <b>{description}</b>

[CALORIES] <b>Питательность:</b>
[CALORIES] Калории: {calories:.0f} ккал
[PROTEIN] Белки: {protein:.1f} г
[FAT] Жиры: {fat:.1f} г
[CARBS] Углеводы: {carbs:.1f} г

[PROGRESS] <b>Прогресс за сегодня:</b>
{'=' * 35}
[CALORIES] Калории: {daily_stats.get('calories', 0):.0f}/{user.daily_calorie_goal} ккал ({cal_progress:.0f}%)
-{cal_bar} {cal_progress:.0f}%

[PROTEIN] Белки: {daily_stats.get('protein', 0):.1f}/{user.daily_protein_goal} г ({protein_progress:.0f}%)
-{protein_bar} {protein_progress:.0f}%

[FAT] Жиры: {daily_stats.get('fat', 0):.1f}/{user.daily_fat_goal} г ({fat_progress:.0f}%)
-{fat_bar} {fat_progress:.0f}%

[CARBS] Углеводы: {daily_stats.get('carbs', 0):.1f}/{user.daily_carbs_goal} г ({carbs_progress:.0f}%)
-{carbs_bar} {carbs_progress:.0f}%

[SUCCESS] <b>Отличная работа!</b> Продолжайте в том же духе!
"""

def water_card(amount: int, total_today: int, goal: int) -> str:
    """Красивая карточка записи воды"""
    progress = (total_today / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'water')
    
    # Мотивация
    if progress >= 100:
        motivation = "[SUCCESS] <b>Отличная гидратация!</b> Цель по воде выполнена!"
    elif progress >= 75:
        motivation = "[GOOD] <b>Отлично!</b> Осталось немного!"
    elif progress >= 50:
        motivation = "[OK] <b>Хорошо!</b> Продолжайте пить воду."
    else:
        remaining = goal - total_today
        motivation = f"[INFO] <b>Нужно больше воды!</b> Осталось выпить {remaining:.0f} мл."
    
    return f"""
[WATER] <b>Вода записана!</b>

{'=' * 35}
[WATER] <b>Выпито:</b> {amount} мл
[GOAL] <b>Выпито за день:</b> {total_today} мл
[TARGET] <b>Цель:</b> {goal} мл

{bar} {progress:.0f}%

{motivation}
"""

def drink_card(amount: int, drink_name: str, calories: float, total_today: int, total_calories: int, goal: int) -> str:
    """Красивая карточка записи напитка"""
    progress = (total_today / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'water')
    
    # Иконки для разных напитков
    drink_icons = {
        'вода': '[WATER]',
        'сок': '[JUICE]',
        'чай': '[TEA]',
        'кофе': '[COFFEE]',
        'молоко': '[MILK]',
        'кефир': '[KEFIR]',
        'газировка': '[SODA]',
        'компот': '[COMPOTE]',
        'смузи': '[SMOOTHIE]',
        'коктейль': '[COCKTAIL]'
    }
    icon = drink_icons.get(drink_name.lower(), '[DRINK]')
    
    return f"""
{icon} <b>Напиток записан!</b>

{'=' * 35}
[DRINK] <b>{drink_name.title()}:</b> {amount} мл
[CALORIES] <b>Калории:</b> {calories:.0f} ккал

[PROGRESS] <b>Выпито за сегодня:</b>
[WATER] Жидкости: {total_today} мл
[CALORIES] Калории из напитков: {total_calories:.0f} ккал
[TARGET] Цель по жидкости: {goal} мл

{bar} {progress:.0f}%

[SUCCESS] <b>Отлично!</b> Продолжайте следить за балансом!
"""

def weight_card(weight: float, change: Optional[float] = None, goal: Optional[float] = None) -> str:
    """Красивая карточка записи веса"""
    lines = [
        "[WEIGHT] <b>Вес записан!</b>",
        "",
        f"[WEIGHT] Текущий вес: {weight:.1f} кг"
    ]
    
    if change is not None:
        if change > 0:
            lines.append(f"[TREND] Изменение: +{change:.1f} кг ⬆️")
        elif change < 0:
            lines.append(f"[TREND] Изменение: {change:.1f} кг ⬇️")
        else:
            lines.append("[TREND] Изменение: 0.0 кг ➡️")
    
    if goal is not None:
        diff = weight - goal
        if diff > 0:
            lines.append(f"[GOAL] До цели: +{diff:.1f} кг")
        elif diff < 0:
            lines.append(f"[GOAL] Цель достигнута! На {abs(diff):.1f} кг меньше цели 🎯")
        else:
            lines.append("[GOAL] Цель достигнута! 🎯")
    
    return "\n".join(lines)

def activity_card(activity_type: str, duration: int, calories_burned: float, daily_stats: Dict) -> str:
    """Красивая карточка записи активности"""
    # Иконки для разных типов активности
    activity_icons = {
        'бег': '[RUNNING]',
        'ходьба': '[WALKING]',
        'тренировка': '[GYM]',
        'йога': '[YOGA]',
        'плавание': '[SWIMMING]',
        'велосипед': '[CYCLING]',
        'танцы': '[DANCING]',
        'фитнес': '[FITNESS]',
        'спорт': '[SPORT]'
    }
    icon = activity_icons.get(activity_type.lower(), '[ACTIVITY]')
    
    # Прогресс по активности
    progress = (daily_stats.get('activity_minutes', 0) / 60 * 100)  # Цель 60 минут в день
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'activity')
    
    return f"""
{icon} <b>Активность записана!</b>

{'=' * 35}
[ACTIVITY] <b>Тип:</b> {activity_type.title()}
[TIME] <b>Длительность:</b> {duration} минут
[CALORIES] <b>Сожжено калорий:</b> {calories_burned:.0f} ккал

[PROGRESS] <b>Активность за сегодня:</b>
[TIME] Всего минут: {daily_stats.get('activity_minutes', 0)}
[CALORIES] Всего сожжено: {daily_stats.get('calories_burned', 0):.0f} ккал

{bar} {progress:.0f}% (цель: 60 минут)

[SUCCESS] <b>Отличная работа!</b> Продолжайте быть активным! 💪
"""

def achievement_notification(achievement_name: str, description: str) -> str:
    """Уведомление о достижении"""
    return f"""
🏆 <b>Новое достижение!</b>

{'=' * 35}
[ACHIEVEMENT] <b>{achievement_name}</b>

{description}

[INFO] <i>Проверьте все достижения в профиле!</i>
"""

def daily_summary(stats: Dict, user) -> str:
    """Ежедневная сводка"""
    # Прогресс по калориям
    cal_progress = (stats.get('calories_consumed', 0) / user.daily_calorie_goal * 100) if user.daily_calorie_goal else 0
    cal_bar = ProgressBar.create_modern_bar(cal_progress, 100, 15, 'neon')
    
    # Прогресс по воде
    water_progress = (stats.get('water_consumed', 0) / user.daily_water_goal * 100) if user.daily_water_goal else 0
    water_bar = ProgressBar.create_modern_bar(water_progress, 100, 15, 'water')
    
    # Оценка дня
    if cal_progress >= 90 and water_progress >= 90:
        rating = "[EXCELLENT] Отличный день! 🌟"
        emoji = "🏆"
    elif cal_progress >= 70 and water_progress >= 70:
        rating = "[GOOD] Хороший день! 👍"
        emoji = "😊"
    elif cal_progress >= 50 and water_progress >= 50:
        rating = "[OK] Неплохой день! 👌"
        emoji = "🙂"
    else:
        rating = "[NEED_IMPROVEMENT] Есть куда расти! 💪"
        emoji = "🎯"
    
    return f"""
{emoji} <b>Ваша статистика за сегодня</b>

{'=' * 40}
[FOOD_ENTRIES] <b>Приемы пищи:</b> {stats.get('meals_count', 0)}
[CALORIES] <b>Калории:</b> {stats.get('calories_consumed', 0):.0f} / {user.daily_calorie_goal:.0f} ккал
{cal_bar} {cal_progress:.0f}%

[WATER] <b>Вода:</b> {stats.get('water_consumed', 0):.0f} / {user.daily_water_goal:.0f} мл
{water_bar} {water_progress:.0f}%

[ACTIVITY] <b>Активность:</b> {stats.get('activity_minutes', 0)} минут
[WEIGHT] <b>Текущий вес:</b> {stats.get('current_weight', 'N/A')} кг

{rating}
"""

def weekly_summary(stats: Dict, user) -> str:
    """Недельная сводка"""
    # Средние значения за неделю
    avg_calories = stats.get('calories_consumed', 0) / 7
    avg_water = stats.get('water_consumed', 0) / 7
    avg_activity = stats.get('activity_minutes', 0) / 7
    
    # Прогресс относительно целей
    cal_progress = (avg_calories / user.daily_calorie_goal * 100) if user.daily_calorie_goal else 0
    water_progress = (avg_water / user.daily_water_goal * 100) if user.daily_water_goal else 0
    
    # Оценка недели
    if cal_progress >= 90 and water_progress >= 90:
        rating = "[EXCELLENT] Отличная неделя! 🏆"
        emoji = "🌟"
    elif cal_progress >= 75 and water_progress >= 75:
        rating = "[GOOD] Хорошая неделя! 👍"
        emoji = "😊"
    elif cal_progress >= 60 and water_progress >= 60:
        rating = "[OK] Неплохая неделя! 👌"
        emoji = "🙂"
    else:
        rating = "[NEED_IMPROVEMENT] Есть куда расти! 💪"
        emoji = "🎯"
    
    return f"""
{emoji} <b>Ваша статистика за неделю</b>

{'=' * 40}
[FOOD_ENTRIES] <b>Приемы пищи:</b> {stats.get('meals_count', 0)}
[CALORIES] <b>Средние калории:</b> {avg_calories:.0f} / {user.daily_calorie_goal:.0f} ккал ({cal_progress:.0f}%)
[WATER] <b>Средняя вода:</b> {avg_water:.0f} / {user.daily_water_goal:.0f} мл ({water_progress:.0f}%)
[ACTIVITY] <b>Средняя активность:</b> {avg_activity:.0f} минут в день
[WEIGHT] <b>Изменение веса:</b> {stats.get('weight_change', 'N/A')} кг

{rating}
"""

def motivational_message(progress_percentage: float, goal_type: str = "general") -> str:
    """Мотивационное сообщение в зависимости от прогресса"""
    messages = {
        "calories": {
            95: "Превосходно! Вы почти достигли цели по калориям! 🎯",
            80: "Отлично! Вы на правильном пути! 💪",
            60: "Хорошо! Продолжайте в том же духе! 👍",
            40: "Неплохо! Но можно лучше! 📈",
            20: "Начало хорошее! Вперед к цели! 🚀"
        },
        "water": {
            95: "Идеально! Вы достаточно пьете воду! 💧",
            80: "Отлично! Осталось совсем немного! 💪",
            60: "Хорошо! Не забывайте про воду! 💧",
            40: "Нужно больше воды! Пейте регулярно! 💧",
            20: "Начинайте пить больше воды! 💧"
        },
        "activity": {
            95: "Вы чемпион активности! 🏆",
            80: "Отличная форма! Продолжайте! 💪",
            60: "Хорошая активность! Так держать! 👍",
            40: "Нужно больше движения! Начните с малого! 🚶",
            20: "Время начать двигаться! Каждый шаг counts! 👟"
        },
        "general": {
            95: "Вы на верном пути! Цель близко! 🎯",
            80: "Прекрасный прогресс! Продолжайте! 💪",
            60: "Хороший результат! Вперед! 👍",
            40: "Есть куда расти! Не сдавайтесь! 📈",
            20: "Каждое начало важно! Продолжайте! 🌟"
        }
    }
    
    # Выбираем подходящее сообщение
    goal_messages = messages.get(goal_type, messages["general"])
    
    for threshold in sorted(goal_messages.keys(), reverse=True):
        if progress_percentage >= threshold:
            return goal_messages[threshold]
    
    return goal_messages[20]  # Минимальное сообщение по умолчанию
