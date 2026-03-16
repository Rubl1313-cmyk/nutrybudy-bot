"""
utils/premium_templates.py
Премиум-шаблоны для красивых ответов бота с эмодзи и прогресс-барами
"""
from typing import Dict, Optional
from utils.ui_templates import ProgressBar

def meal_card(food_data: Dict, user, daily_stats: Dict) -> str:
    """Красивая карточка сохранённого приёма пищи"""
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
🍽️ <b>Приём пищи сохранён!</b>

{'═' * 35}
🍲 <b>{description}</b>

🔥 <b>Питательность:</b>
🔥 Калории: {calories:.0f} ккал
🥩 Белки: {protein:.1f} г
🥑 Жиры: {fat:.1f} г
🍚 Углеводы: {carbs:.1f} г

📊 <b>Ваш прогресс за сегодня</b>
{'═' * 35}
🔥 Калории: {daily_stats.get('calories', 0):.0f}/{user.daily_calorie_goal} ккал ({cal_progress:.0f}%)
{cal_bar} {cal_progress:.0f}%

🥩 Белки: {daily_stats.get('protein', 0):.1f}/{user.daily_protein_goal} г ({protein_progress:.0f}%)
{protein_bar} {protein_progress:.0f}%

🥑 Жиры: {daily_stats.get('fat', 0):.1f}/{user.daily_fat_goal} г ({fat_progress:.0f}%)
{fat_bar} {fat_progress:.0f}%

🍚 Углеводы: {daily_stats.get('carbs', 0):.1f}/{user.daily_carbs_goal} г ({carbs_progress:.0f}%)
{carbs_bar} {carbs_progress:.0f}%

💪 <b>Отличная работа!</b> Продолжайте в том же духе!
"""

def water_card(amount: int, total_today: int, goal: int) -> str:
    """Красивая карточка записи воды"""
    progress = (total_today / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'water')
    
    # Мотивация
    if progress >= 100:
        motivation = "🎉 <b>Отличная гидратация!</b> Цель по воде выполнена!"
    elif progress >= 75:
        motivation = "💪 <b>Отлично!</b> Осталось немного!"
    elif progress >= 50:
        motivation = "👍 <b>Хорошо!</b> Продолжайте пить воду."
    else:
        remaining = goal - total_today
        motivation = f"💧 <b>Нужно больше воды!</b> Осталось выпить {remaining:.0f} мл."
    
    return f"""
💧 <b>Вода записана!</b>

{'═' * 35}
➕ <b>Выпито:</b> {amount} мл
📊 <b>Всего за день:</b> {total_today} мл
🎯 <b>Цель:</b> {goal} мл

{bar} {progress:.0f}%

{motivation}
"""

def drink_card(amount: int, drink_name: str, calories: float, total_today: int, total_calories: int, goal: int) -> str:
    """Красивая карточка записи напитка"""
    progress = (total_today / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'water')
    
    # Иконка для типа напитка
    drink_icons = {
        'вода': '💧',
        'сок': '🧃',
        'чай': '🍵',
        'кофе': '☕',
        'молоко': '🥛',
        'кефир': '🥛',
        'газировка': '🥤',
        'компот': '🍹',
        'смузи': '🥤',
        'коктейль': '🍹'
    }
    icon = drink_icons.get(drink_name.lower(), '🥤')
    
    return f"""
{icon} <b>Напиток записан!</b>

{'═' * 35}
🥤 <b>{drink_name.title()}:</b> {amount} мл
🔥 <b>Калории:</b> {calories:.0f} ккал

📊 <b>Всего за сегодня:</b>
💦 Жидкость: {total_today} мл
🔥 Калории из напитков: {total_calories:.0f} ккал
🎯 Цель по жидкости: {goal} мл

{bar} {progress:.0f}%

💪 <b>Отлично!</b> Продолжайте следить за балансом!
"""

def weight_card(weight: float, change: Optional[float] = None, goal: Optional[float] = None) -> str:
    """Красивая карточка записи веса"""
    # Определяем изменение
    if change is not None:
        if change > 0:
            change_text = f"📈 +{change:.1f} кг"
            change_emoji = "📈"
        elif change < 0:
            change_text = f"📉 {change:.1f} кг"
            change_emoji = "📉"
        else:
            change_text = "➡️ 0.0 кг"
            change_emoji = "➡️"
    else:
        change_text = ""
        change_emoji = ""
    
    # Прогресс к цели
    progress_text = ""
    if goal is not None:
        diff = goal - weight
        if diff > 0:
            progress_text = f"🎯 До цели: {diff:.1f} кг"
        elif diff < 0:
            progress_text = f"🏆 Цель превышена на {abs(diff):.1f} кг!"
        else:
            progress_text = "🎉 Цель достигнута!"
    
    return f"""
⚖️ <b>Вес записан!</b>

{'═' * 35}
🏋️ <b>Текущий вес:</b> {weight:.1f} кг
{change_emoji} <b>Изменение:</b> {change_text}
{progress_text}

💪 <b>Продолжайте отслеживать прогресс!</b>
"""

def activity_card(activity_type: str, duration: int, calories: float, daily_total: int, goal: int) -> str:
    """Красивая карточка записи активности"""
    progress = (daily_total / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'activity')
    
    # Иконки для типов активности
    activity_icons = {
        'бег': '🏃',
        'ходьба': '🚶',
        'велосипед': '🚴',
        'плавание': '🏊',
        'тренировка': '💪',
        'йога': '🧘',
        'фитнес': '🏋️'
    }
    icon = activity_icons.get(activity_type.lower(), '🏃')
    
    return f"""
{icon} <b>Активность записана!</b>

{'═' * 35}
🏃 <b>Тип:</b> {activity_type.title()}
⏱️ <b>Длительность:</b> {duration} мин
🔥 <b>Калории:</b> {calories:.0f} ккал

📊 <b>Прогресс за день:</b>
🔥 Всего потрачено: {daily_total} ккал
🎯 Цель: {goal} ккал

{bar} {progress:.0f}%

💪 <b>Отличная тренировка!</b>
"""

def progress_card(stats: Dict, period: str = "день") -> str:
    """Красивая карточка прогресса за период"""
    period_icons = {
        'день': '📅',
        'неделя': '📆',
        'месяц': '📊',
        'всё время': '🏆'
    }
    icon = period_icons.get(period.lower(), '📊')
    
    return f"""
{icon} <b>Ваш прогресс за {period}</b>

{'═' * 35}
🍽️ <b>Питание:</b>
🔥 Калории: {stats.get('avg_calories', 0):.0f} ккал/день
🥩 Белки: {stats.get('avg_protein', 0):.1f} г/день
🥑 Жиры: {stats.get('avg_fat', 0):.1f} г/день
🍚 Углеводы: {stats.get('avg_carbs', 0):.1f} г/день

💧 <b>Гидратация:</b>
💦 Жидкость: {stats.get('avg_water', 0):.0f} мл/день

⚖️ <b>Вес:</b>
🏋️ Изменение: {stats.get('weight_change', 0):+.1f} кг

🏃 <b>Активность:</b>
🔥 Потрачено калорий: {stats.get('total_activity', 0):.0f} ккал

💪 <b>Продолжайте в том же духе!</b>
"""

def achievement_card(achievement: Dict) -> str:
    """Красивая карточка достижения"""
    icons = {
        'bronze': '🥉',
        'silver': '🥈',
        'gold': '🥇',
        'platinum': '🏆',
        'diamond': '💎'
    }
    
    icon = icons.get(achievement.get('rarity', 'bronze'), '🥉')
    
    return f"""
🎉 <b>Новое достижение!</b>

{'═' * 35}
{icon} <b>{achievement.get('name', 'Достижение')}</b>

📝 <b>Описание:</b> {achievement.get('description', '')}

🎯 <b>Категория:</b> {achievement.get('category', 'Общее')}

⭐ <b>Редкость:</b> {achievement.get('rarity', 'обычное').title()}

🎊 <b>Поздравляем!</b> Вы молодец!
"""

def error_card(error_type: str, message: str) -> str:
    """Красивая карточка ошибки"""
    error_icons = {
        'validation': '⚠️',
        'database': '🗄️',
        'ai': '🤖',
        'network': '🌐',
        'general': '❌'
    }
    
    icon = error_icons.get(error_type, '❌')
    
    return f"""
{icon} <b>Произошла ошибка</b>

{'═' * 35}
📝 <b>Тип:</b> {error_type.title()}
💬 <b>Сообщение:</b> {message}

🔧 <b>Что делать:</b> Попробуйте ещё раз или обратитесь в поддержку.

💡 <b>Совет:</b> Если ошибка повторяется, возможно, нужно проверить настройки.
"""

def loading_card(operation: str) -> str:
    """Красивая карточка загрузки"""
    loading_icons = {
        'photo': '📸',
        'voice': '🎤',
        'analysis': '🔍',
        'saving': '💾',
        'stats': '📊'
    }
    
    icon = loading_icons.get(operation, '⏳')
    
    return f"""
{icon} <b>Обработка...</b>

{'═' * 35}
⏳ Пожалуйста, подождите немного...

🤖 AI анализирует ваш запрос...

⚡ Это может занять несколько секунд.
"""
