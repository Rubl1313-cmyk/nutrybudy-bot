"""
utils/premium_templates.py
Премиальные шаблоны для ответов бота
"""
from typing import Dict, Optional
from utils.ui_templates import ProgressBar

def loading_card(message: str = "Processing...") -> str:
    """Loading card for async operations"""
    return f"""
⏳ <b>{message}</b>
⏳ Пожалуйста, подождите...
"""

def error_card(error_message: str, suggestion: str = "Try again later") -> str:
    """Error card for displaying errors"""
    return f"""
❌ <b>Something went wrong</b>
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
🍽️ <b>Прием пищи записан!</b>

{'=' * 35}
🍽️ <b>{description}</b>

📊 <b>Питательность:</b>
🔥 Калории: {calories:.0f} ккал
🥩 Белки: {protein:.1f} г
🧈 Жиры: {fat:.1f} г
🍞 Углеводы: {carbs:.1f} г

📊 <b>Прогресс за сегодня:</b>
{'=' * 35}
🔥 Калории: {daily_stats.get('calories', 0):.0f}/{user.daily_calorie_goal} ккал ({cal_progress:.0f}%)
-{cal_bar} {cal_progress:.0f}%

🥩 Белки: {daily_stats.get('protein', 0):.1f}/{user.daily_protein_goal} г ({protein_progress:.0f}%)
-{protein_bar} {protein_progress:.0f}%

🧈 Жиры: {daily_stats.get('fat', 0):.1f}/{user.daily_fat_goal} г ({fat_progress:.0f}%)
-{fat_bar} {fat_progress:.0f}%

🍞 Углеводы: {daily_stats.get('carbs', 0):.1f}/{user.daily_carbs_goal} г ({carbs_progress:.0f}%)
-{carbs_bar} {carbs_progress:.0f}%

🎉 <b>Отличная работа!</b> Продолжайте в том же духе!
"""

def water_card(amount: int, total_today: int, goal: int) -> str:
    """Красивая карточка записи воды"""
    progress = (total_today / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'water')
    
    # Мотивация
    if progress >= 100:
        motivation = "🎉 <b>Отличная гидратация!</b> Цель по воде выполнена!"
    elif progress >= 75:
        motivation = "👍 <b>Отлично!</b> Осталось немного!"
    elif progress >= 50:
        motivation = "👌 <b>Хорошо!</b> Продолжайте пить воду."
    else:
        remaining = goal - total_today
        motivation = f"ℹ️ <b>Нужно больше воды!</b> Осталось выпить {remaining:.0f} мл."
    
    return f"""
💧 <b>Вода записана!</b>

{'=' * 35}
💧 <b>Выпито:</b> {amount} мл
📊 <b>Выпито за день:</b> {total_today} мл
🎯 <b>Цель:</b> {goal} мл

{bar} {progress:.0f}%

{motivation}
"""

def drink_card(amount: int, drink_name: str, calories: float, total_today: int, total_calories: int, goal: int) -> str:
    """Красивая карточка записи напитка"""
    progress = (total_today / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'water')
    
    # Иконки для разных напитков
    drink_icons = {
        'вода': '💧',
        'сок': '🧃',
        'чай': '🍵',
        'кофе': '☕',
        'молоко': '🥛',
        'кефир': '🥛',
        'газировка': '🥤',
        'компот': '🧃',
        'смузи': '🥤',
        'коктейль': '🍹'
    }
    icon = drink_icons.get(drink_name.lower(), '🥤')
    
    return f"""
{icon} <b>Напиток записан!</b>

{'=' * 35}
🥤 <b>{drink_name.title()}:</b> {amount} мл
🔥 <b>Калории:</b> {calories:.0f} ккал

📊 <b>Выпито за сегодня:</b>
💧 Жидкости: {total_today} мл
🔥 Калории из напитков: {total_calories:.0f} ккал
🎯 Цель по жидкости: {goal} мл

{bar} {progress:.0f}%

🎉 <b>Отлично!</b> Продолжайте следить за балансом!
"""

def weight_card(weight: float, change: Optional[float] = None, goal: Optional[float] = None) -> str:
    """Красивая карточка записи веса"""
    lines = [
        "⚖️ <b>Вес записан!</b>",
        "",
        f"⚖️ Текущий вес: {weight:.1f} кг"
    ]
    
    if change is not None:
        if change > 0:
            lines.append(f"📈 Изменение: +{change:.1f} кг ⬆️")
        elif change < 0:
            lines.append(f"📉 Изменение: {change:.1f} кг ⬇️")
        else:
            lines.append("➡️ Изменение: 0.0 кг ➡️")
    
    if goal is not None:
        diff = weight - goal
        if diff > 0:
            lines.append(f"🎯 До цели: +{diff:.1f} кг")
        elif diff < 0:
            lines.append(f"🎯 Цель достигнута! На {abs(diff):.1f} кг меньше цели 🎯")
        else:
            lines.append("🎯 Цель достигнута! 🎯")
    
    return "\n".join(lines)

def weight_trend_card(weights: list, goal: Optional[float] = None) -> str:
    """Красивая карточка тренда веса"""
    if not weights:
        return "⚖️ <b>Нет данных о весе</b>\n\nℹ️ Начните отслеживать вес для просмотра тренда"
    
    lines = [
        "⚖️ <b>Тренд веса</b>",
        "",
        f"ℹ️ Последние записи:"
    ]
    
    # Показываем последние 5 записей
    for weight in weights[-5:]:
        lines.append(f"⚖️ {weight:.1f} кг")
    
    if len(weights) > 1:
        change = weights[-1] - weights[0]
        if change > 0:
            lines.append(f"📈 Изменение за период: +{change:.1f} кг ⬆️")
        elif change < 0:
            lines.append(f"📉 Изменение за период: {change:.1f} кг ⬇️")
        else:
            lines.append(f"➡️ Изменение за период: 0.0 кг ➡️")
    
    if goal is not None:
        current = weights[-1]
        diff = current - goal
        if diff > 0:
            lines.append(f"🎯 До цели: +{diff:.1f} кг")
        elif diff < 0:
            lines.append(f"🎯 Цель достигнута! На {abs(diff):.1f} кг меньше цели 🎯")
        else:
            lines.append(f"🎯 Цель достигнута! 🎯")
    
    return "\n".join(lines)

def activity_card(activity_type: str, duration: int, calories_burned: float, daily_stats: Dict) -> str:
    """Красивая карточка записи активности"""
    # Иконки для разных типов активности
    activity_icons = {
        'бег': '🏃',
        'ходьба': '🚶',
        'тренировка': '🏋️',
        'йога': '🧘',
        'плавание': '🏊',
        'велосипед': '🚴',
        'танцы': '💃',
        'фитнес': '🏃',
        'спорт': '⚽'
    }
    icon = activity_icons.get(activity_type.lower(), '🏃')
    
    # Прогресс по активности
    progress = (daily_stats.get('activity_minutes', 0) / 60 * 100)  # Цель 60 минут в день
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'activity')
    
    return f"""
{icon} <b>Активность записана!</b>

{'=' * 35}
🏃 <b>Тип:</b> {activity_type.title()}
⏰ <b>Длительность:</b> {duration} минут
🔥 <b>Сожжено калорий:</b> {calories_burned:.0f} ккал

📊 <b>Активность за сегодня:</b>
⏰ Всего минут: {daily_stats.get('activity_minutes', 0)}
🔥 Всего сожжено: {daily_stats.get('calories_burned', 0):.0f} ккал

{bar} {progress:.0f}% (цель: 60 минут)

🎉 <b>Отличная работа!</b> Продолжайте быть активным! 💪
"""

def achievement_notification(achievement_name: str, description: str) -> str:
    """Уведомление о достижении"""
    return f"""
🏆 <b>Новое достижение!</b>

{'=' * 35}
🏆 <b>{achievement_name}</b>

{description}

ℹ️ <i>Проверьте все достижения в профиле!</i>
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
        rating = "🌟 Отличный день! 🌟"
        emoji = "🏆"
    elif cal_progress >= 70 and water_progress >= 70:
        rating = "👍 Хороший день! 👍"
        emoji = "😊"
    elif cal_progress >= 50 and water_progress >= 50:
        rating = "👌 Неплохой день! 👌"
        emoji = "🙂"
    else:
        rating = "📈 Есть куда расти! 💪"
        emoji = "🎯"
    
    return f"""
{emoji} <b>Ваша статистика за сегодня</b>

{'=' * 40}
🍽️ <b>Приемы пищи:</b> {stats.get('meals_count', 0)}
🔥 <b>Калории:</b> {stats.get('calories_consumed', 0):.0f} / {user.daily_calorie_goal:.0f} ккал
{cal_bar} {cal_progress:.0f}%

💧 <b>Вода:</b> {stats.get('water_consumed', 0):.0f} / {user.daily_water_goal:.0f} мл
{water_bar} {water_progress:.0f}%

🏃 <b>Активность:</b> {stats.get('activity_minutes', 0)} минут
⚖️ <b>Текущий вес:</b> {stats.get('current_weight', 'N/A')} кг

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
        rating = "🌟 Отличная неделя! 🏆"
        emoji = "🌟"
    elif cal_progress >= 75 and water_progress >= 75:
        rating = "👍 Хорошая неделя! 👍"
        emoji = "😊"
    elif cal_progress >= 60 and water_progress >= 60:
        rating = "👌 Неплохая неделя! 👌"
        emoji = "🙂"
    else:
        rating = "📈 Есть куда расти! 💪"
        emoji = "🎯"
    
    return f"""
{emoji} <b>Ваша статистика за неделю</b>

{'=' * 40}
🍽️ <b>Приемы пищи:</b> {stats.get('meals_count', 0)}
🔥 <b>Средние калории:</b> {avg_calories:.0f} / {user.daily_calorie_goal:.0f} ккал ({cal_progress:.0f}%)
💧 <b>Средняя вода:</b> {avg_water:.0f} / {user.daily_water_goal:.0f} мл ({water_progress:.0f}%)
🏃 <b>Средняя активность:</b> {avg_activity:.0f} минут в день
⚖️ <b>Изменение веса:</b> {stats.get('weight_change', 'N/A')} кг

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
