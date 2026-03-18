"""
UI Templates для NutriBuddy Bot
Премиальные шаблоны интерфейсов, карточки, графики
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ProgressBar:
    """Progress bar utility for creating visual progress indicators"""
    
    @staticmethod
    def create_modern_bar(progress: float, max_value: float = 100, length: int = 10, style: str = 'default') -> str:
        """Create a modern progress bar with different styles"""
        # Ensure progress is within bounds
        progress = max(0, min(progress, max_value))
        filled_length = int((progress / max_value) * length)
        
        # Style definitions
        styles = {
            'default': {'filled': '=', 'empty': '-'},
            'neon': {'filled': '#', 'empty': '-'},
            'protein': {'filled': 'P', 'empty': '-'},
            'fat': {'filled': 'F', 'empty': '-'},
            'carbs': {'filled': 'C', 'empty': '-'},
            'water': {'filled': 'W', 'empty': '-'},
            'activity': {'filled': 'A', 'empty': '-'}
        }
        
        style_config = styles.get(style, styles['default'])
        filled_char = style_config['filled']
        empty_char = style_config['empty']
        
        # Create bar
        bar = filled_char * filled_length + empty_char * (length - filled_length)
        percentage = (progress / max_value) * 100
        
        return f"{bar} {percentage:.1f}%"
    
    @staticmethod
    def create_simple_bar(progress: float, max_value: float = 100, length: int = 10) -> str:
        """Create a simple progress bar"""
        progress = max(0, min(progress, max_value))
        filled_length = int((progress / max_value) * length)
        bar = '=' * filled_length + '-' * (length - filled_length)
        percentage = (progress / max_value) * 100
        return f"{bar} {percentage:.0f}%"

class UITemplates:
    """Премиальные UI шаблоны"""
    
    @staticmethod
    def premium_profile_card(user, stats: Dict = None) -> str:
        """Премиальная карточка профиля"""
        lines = [
            f"[PROFILE] <b>{user.first_name or 'Пользователь'}</b> · профиль",
            "────────────────────────────────────────────────────",
            "[INFO] <b>Данные</b>",
            f"   [WEIGHT] Вес: <code>{user.weight}</code> кг  |  [HEIGHT] Рост: <code>{user.height}</code> см  |  [AGE] Возраст: <code>{user.age}</code> лет",
            f"   {('[MALE]' if user.gender=='male' else '[FEMALE]')} Пол: {user.gender}  |  [GOAL] Цель: {user.goal}",
            f"   [ACTIVITY] Активность: {user.activity_level}",
            "",
            "[NORMS] <b>Ваши нормы</b>",
            f"   [CALORIES] Калории: <code>{user.daily_calorie_goal:,.0f}</code> ккал ██████████",
            f"   [PROTEIN] Белки: <code>{user.daily_protein_goal:.0f}</code> г (30%)    ████████▌▌▌",
            f"   [FAT] Жиры: <code>{user.daily_fat_goal:.0f}</code> г (30%)      ████████▌▌▌",
            f"   [CARBS] Углеводы: <code>{user.daily_carbs_goal:.0f}</code> г (40%) █████████▌▌",
            f"   [WATER] Вода: <code>{user.daily_water_goal:,.0f}</code> мл        ████████████"
        ]
        if stats:
            lines.extend([
                "",
                f"[SUCCESS] <i>Сегодня выполнено {stats['progress_percent']:.0f}% плана по калориям.</i>"
            ])
        return "\n".join(lines)
    
    @staticmethod
    def premium_progress_card(stats: Dict, period: str) -> str:
        """Премиальная карточка прогресса"""
        period_icons = {'day': '[DAY]', 'week': '[WEEK]', 'month': '[MONTH]'}
        icon = period_icons.get(period, '[MONTH]')
        period_names = {'day': 'сегодня', 'week': 'за неделю', 'month': 'за месяц'}
        name = period_names.get(period, 'за период')
        
        # Прогресс-бары
        calorie_progress = min((stats['calories_consumed'] / stats['calorie_goal']) * 100, 100) if stats['calorie_goal'] > 0 else 0
        protein_progress = min((stats['protein_consumed'] / stats['protein_goal']) * 100, 100) if stats['protein_goal'] > 0 else 0
        fat_progress = min((stats['fat_consumed'] / stats['fat_goal']) * 100, 100) if stats['fat_goal'] > 0 else 0
        carbs_progress = min((stats['carbs_consumed'] / stats['carbs_goal']) * 100, 100) if stats['carbs_goal'] > 0 else 0
        water_progress = min((stats['water_consumed'] / stats['water_goal']) * 100, 100) if stats['water_goal'] > 0 else 0
        
        lines = [
            f"{icon} <b>Ваш прогресс {name}:</b>",
            "────────────────────────────────────────────────────",
            f"[CALORIES] <b>Калории:</b>",
            f"   {UITemplates.create_progress_bar(stats['calories_consumed'], stats['calorie_goal'])}",
            f"   <code>{stats['calories_consumed']:.0f}</code> / <code>{stats['calorie_goal']:.0f}</code> ккал ({calorie_progress:.0f}%)",
            "",
            f"[PROTEIN] <b>Белки:</b>",
            f"   {UITemplates.create_progress_bar(stats['protein_consumed'], stats['protein_goal'])}",
            f"   <code>{stats['protein_consumed']:.1f}</code> / <code>{stats['protein_goal']:.1f}</code> г ({protein_progress:.0f}%)",
            "",
            f"[FAT] <b>Жиры:</b>",
            f"   {UITemplates.create_progress_bar(stats['fat_consumed'], stats['fat_goal'])}",
            f"   <code>{stats['fat_consumed']:.1f}</code> / <code>{stats['fat_goal']:.1f}</code> г ({fat_progress:.0f}%)",
            "",
            f"[CARBS] <b>Углеводы:</b>",
            f"   {UITemplates.create_progress_bar(stats['carbs_consumed'], stats['carbs_goal'])}",
            f"   <code>{stats['carbs_consumed']:.1f}</code> / <code>{stats['carbs_goal']:.1f}</code> г ({carbs_progress:.0f}%)",
            "",
            f"[WATER] <b>Вода:</b>",
            f"   {UITemplates.create_progress_bar(stats['water_consumed'], stats['water_goal'])}",
            f"   <code>{stats['water_consumed']:.0f}</code> / <code>{stats['water_goal']:.0f}</code> мл ({water_progress:.0f}%)",
            "",
            f"[MOTIVATION] <i>{UITemplates._get_progress_motivation(calorie_progress)}</i>"
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def create_progress_bar(current: float, total: float, length: int = 12) -> str:
        """Создает современный прогресс-бар"""
        if total <= 0:
            percentage = 0
        else:
            percentage = min((current / total) * 100, 100)
        
        filled = int(length * percentage / 100)
        empty = length - filled
        
        # Градиент от синего к зеленому
        bar = '██' * filled + '░░' * empty
        
        # Добавляем звёздочку если прогресс > 90%
        if percentage >= 90 and filled > 0:
            bar = bar[:-1] + '★'
        
        return f"{bar} <code>{percentage:.0f}%</code>"
    
    @staticmethod
    def _get_progress_motivation(calorie_progress: float) -> str:
        """Мотивация по прогрессу калорий"""
        if calorie_progress >= 95:
            return "Отличная работа! Вы достигли цели! 🏆"
        elif calorie_progress >= 80:
            return "Прекрасный результат! Так держать! 💪"
        elif calorie_progress >= 60:
            return "Хороший прогресс! Продолжайте в том же духе! 👍"
        elif calorie_progress >= 40:
            return "Вы на правильном пути! Не останавливайтесь! 🎯"
        elif calorie_progress >= 20:
            return "Хорошее начало! Вперед к цели! 🚀"
        else:
            return "Начните с малого, каждый шаг важен! 🌟"
    
    @staticmethod
    def achievement_card(achievement) -> str:
        """Карточка достижения"""
        return f"""
🏆 <b>{achievement.name}</b>
{achievement.description}
<i>Получено: {achievement.earned_at.strftime('%d.%m.%Y')}</i>
        """.strip()
    
    @staticmethod
    def stats_summary(stats: Dict) -> str:
        """Сводка статистики"""
        return f"""
📊 <b>Ваша статистика</b>
────────────────────────────────────────────────────
🍽 <b>Приемов пищи:</b> {stats['meals_count']}
💧 <b>Выпито воды:</b> {stats['water_consumed']:.0f} мл
🏃 <b>Активность:</b> {stats['activity_minutes']} минут
⚖️ <b>Текущий вес:</b> {stats['current_weight']:.1f} кг
        """.strip()
    
    @staticmethod
    def meal_card(meal) -> str:
        """Карточка приема пищи"""
        return f"""
🍽 <b>{meal.dish_name}</b>
{meal.calories:.0f} ккал | Б:{meal.protein:.0f}г Ж:{meal.fat:.0f}г У:{meal.carbs:.0f}г
<i>{meal.datetime.strftime('%H:%M')}</i>
        """.strip()
    
    @staticmethod
    def water_card(amount: float, goal: float) -> str:
        """Карточка воды"""
        progress = min((amount / goal) * 100, 100)
        bar = UITemplates.create_progress_bar(amount, goal)
        
        return f"""
💧 <b>Водный баланс</b>
{bar}
{amount:.0f} / {goal:.0f} мл ({progress:.0f}%)
        """.strip()
    
    @staticmethod
    def welcome_message(user) -> str:
        """Приветственное сообщение"""
        greetings = [
            "Добро пожаловать! 👋",
            "Рада видеть вас! 😊",
            "Привет! 🌟",
            "Здравствуйте! 👋"
        ]
        
        import random
        greeting = random.choice(greetings)
        
        return f"""
{greeting}

Я ваш персональный помощник по питанию NutriBuddy! 🥗

<b>Что я могу для вас сделать:</b>
🔍 Анализировать фото еды и считать калории
📊 Отслеживать ваш прогресс и статистику
💧 Напоминать о питьевом режиме
🏃 Учитывать вашу физическую активность
🎯 Помогать достигать целей по питанию

<b>Начнем с создания вашего профиля!</b>
Используйте команду /set_profile для персонализации

<b>Или просто отправьте фото еды!</b>
Я сразу проанализирую и покажу информацию

🌟 <i>Каждый день - это шаг к здоровой жизни!</i>
        """.strip()
    
    @staticmethod
    def help_message() -> str:
        """Сообщение помощи"""
        return f"""
📖 <b>Справка по NutriBuddy Bot</b>

<b>🎯 Основные команды:</b>
/start - Начать работу с ботом
/set_profile - Настроить персональный профиль
/profile - Посмотреть свой профиль
/log_food - Записать прием пищи
/log_water - Записать употребление воды
/log_weight - Записать вес
/log_activity - Записать активность
/progress - Посмотреть прогресс
/stats - Статистика за период
/ask - Задать вопрос AI-ассистенту
/weather - Погода и рекомендации
/recipe - Рецепты
/calculate - Калькулятор КБЖУ
/meal_plan - План питания
/help - Эта справка

<b>📸 Работа с фото:</b>
Просто отправьте фото еды, и я:
• Распознаю продукты
• Посчитаю калории, БЖУ
• Дам рекомендации
• Сохраню в дневник

<b>💡 Советы:</b>
• Фото должно быть четким и хорошо освещенным
• Еда должна занимать основную часть кадра
• Можно отправлять несколько фото за раз
• Работаем с русскими и международными блюдами

<b>🎨 Особенности:</b>
• Умный AI-анализ еды
• Персональные рекомендации
• Отслеживание прогресса
• Напоминания и советы
• Современный интерфейс

<b>❓ Вопросы?</b>
Используйте /ask для общения с AI-ассистентом
Я помогу с советами по питанию, рецептами и ответами на вопросы

🌟 <i>Начните здоровый образ жизни уже сегодня!</i>
        """.strip()
    
    @staticmethod
    def error_message(error_type: str, details: str = "") -> str:
        """Сообщение об ошибке"""
        error_messages = {
            "photo_error": "Не удалось обработать фото. Попробуйте сделать фото более четким.",
            "profile_error": "Сначала настройте профиль командой /set_profile",
            "database_error": "Временная проблема с базой данных. Попробуйте позже.",
            "ai_error": "AI-сервис недоступен. Попробуйте позже.",
            "general_error": "Произошла ошибка. Попробуйте еще раз."
        }
        
        message = error_messages.get(error_type, error_messages["general_error"])
        if details:
            message += f"\n\n<i>Детали: {details}</i>"
        
        return f"""
❌ <b>Ошибка</b>

{message}

🔧 Если проблема повторяется, используйте /ask для связи с поддержкой.
        """.strip()
