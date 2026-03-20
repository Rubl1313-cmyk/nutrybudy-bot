"""
Премиальные шаблоны сообщений для NutriBuddy Bot
Элегантные карточки, графики, контекстные подсказки, персонализация
"""
from datetime import datetime
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class MessageTemplates:
    """Премиальные шаблоны сообщений"""
    
    @staticmethod
    def premium_welcome_message(user_name: str) -> str:
        """Современное премиальное приветствие"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Доброе утро"
            emoji = "🌅"
        elif 12 <= hour < 18:
            greeting = "Добрый день"
            emoji = "☀️"
        else:
            greeting = "Добрый вечер"
            emoji = "🌙"
        
        return (
            f"{emoji} <b>{greeting}, {user_name}!</b>\n\n"
            f"[WELCOME] <b>Добро пожаловать в NutriBuddy</b>\n"
            f"Ваш персональный AI-ассистент по питанию и здоровью\n\n"
            f"[FEATURES] <b>Что я могу для вас сделать:</b>\n"
            f"[CAMERA] Распознать еду по фото\n"
            f"[CHAT] Ответить на вопросы о питании\n"
            f"[STATS] Показать ваш прогресс\n"
            f"[PLAN] Составить план питания\n\n"
            f"[ACTION] <b>Начните с создания профиля</b>\n"
            f"Команда: <code>/set_profile</code>\n\n"
            f"Или просто отправьте фото еды! [CAMERA]"
        )
    
    @staticmethod
    def modern_welcome_message(user_name: str = "Пользователь", 
                               days_active: int = 0, 
                               current_streak: int = 0) -> str:
        """
        [REVOLUTION] Революционное приветствие NutriBuddy 2024
        """
        # Персонализированное приветствие с эмоциями
        if days_active == 0:
            greeting_emoji = "🚀"
            status_text = "Начнём ваше путешествие к здоровью!"
            motivation_emoji = "🚀"
        elif current_streak >= 7:
            greeting_emoji = "🔥"
            status_text = f"Вы на пути к цели уже {current_streak} дней!"
            motivation_emoji = "💪"
        else:
            greeting_emoji = "👋"
            status_text = "Продолжаем наш путь к здоровью!"
            motivation_emoji = "⭐"
        
        # Визуально структурированное сообщение
        text = (
            f"{greeting_emoji} <b>Привет, {user_name}!</b>\n\n"
            f"[LOGO] <b>NutriBuddy</b>\n"
            f"<i>{status_text}</i>\n\n"
            f"[LINE] =====================================\n\n"
            f"⚡ <b>Фото еды</b> → я распознаю калории\n"
            f"✍️ <b>Текстом</b> → я пойму и запишу\n"
            f"📊 <b>Прогресс</b> → ваши достижения\n\n"
            f"[LINE] =====================================\n\n"
            f"{motivation_emoji} <i>Отправьте фото еды — начнём сейчас!</i>"
        )
        
        return text
    
    @staticmethod
    def success_food_logged(dish_name: str, calories: float, 
                          protein: float, fat: float, carbs: float,
                          daily_progress: float = 0) -> str:
        """
        [EMOTIONAL] Эмоциональное сообщение об успехе 2024
        """
        # Эмоциональные реакции на прогресс
        if daily_progress >= 100:
            emoji = "[PARTY]"
            message = "Отлично! Вы достигли дневной цели!"
        elif daily_progress >= 75:
            emoji = "🔥"
            message = "Прекрасно! Почти у цели!"
        elif daily_progress >= 50:
            emoji = "💪"
            message = "Хорошая работа! Продолжайте в том же духе!"
        else:
            emoji = "⭐"
            message = "Отличное начало дня!"
        
        text = (
            f"{emoji} <b>Приём пищи сохранён!</b>\n\n"
            f"🍽️ <b>{dish_name}</b>\n\n"
            f"📊 <b>Питательность:</b>\n"
            f"🔥 Калории: {calories:.0f} ккал\n"
            f"🥩 Белки: {protein:.1f} г\n"
            f"🧈 Жиры: {fat:.1f} г\n"
            f"🍞 Углеводы: {carbs:.1f} г\n\n"
            f"📊 <b>{message}</b>\n"
            f"ℹ️ <i>Продолжайте в том же духе! 💪</i>"
        )
        
        return text
    
    @staticmethod
    def water_logged(amount: int, total_today: int, goal: int) -> str:
        """Красивое сообщение о записи воды"""
        progress = (total_today / goal * 100) if goal > 0 else 0
        
        if progress >= 100:
            emoji = "[PARTY]"
            message = "Отличная гидратация! Цель достигнута!"
        elif progress >= 80:
            emoji = "[GOOD]"
            message = "Отлично! Осталось немного!"
        elif progress >= 50:
            emoji = "[OK]"
            message = "Хорошо! Продолжайте пить воду!"
        else:
            emoji = "[INFO]"
            message = "Нужно больше воды для баланса!"
        
        return (
            f"{emoji} <b>Вода записана!</b>\n\n"
            f"[WATER] Выпито: {amount} мл\n"
            f"[TOTAL] Всего за день: {total_today} мл\n"
            f"[GOAL] Цель: {goal} мл\n"
            f"[PROGRESS] Прогресс: {progress:.0f}%\n\n"
            f"[MESSAGE] {message}"
        )
    
    @staticmethod
    def weight_logged(weight: float, change: Optional[float] = None) -> str:
        """Сообщение о записи веса с динамикой"""
        if change is not None:
            if change > 0:
                trend = f"[UP] +{change:.1f} кг"
            elif change < 0:
                trend = f"[DOWN] {change:.1f} кг"
            else:
                trend = "[STABLE] без изменений"
        else:
            trend = "[INFO] первая запись"
        
        return (
            f"[WEIGHT] <b>Вес записан!</b>\n\n"
            f"[CURRENT] Текущий вес: {weight:.1f} кг\n"
            f"[TREND] Динамика: {trend}\n\n"
            f"[INFO] <i>Регулярный учёт веса помогает достичь целей! 📈</i>"
        )
    
    @staticmethod
    def activity_logged(activity_type: str, duration: int, calories_burned: float) -> str:
        """Сообщение о записи активности"""
        activity_emojis = {
            "бег": "[RUNNING]",
            "ходьба": "[WALKING]", 
            "тренировка": "[GYM]",
            "йога": "[YOGA]",
            "плавание": "[SWIMMING]",
            "велосипед": "[CYCLING]",
            "танцы": "[DANCING]",
            "фитнес": "[FITNESS]"
        }
        
        emoji = activity_emojis.get(activity_type.lower(), "[ACTIVITY]")
        
        return (
            f"{emoji} <b>Активность записана!</b>\n\n"
            f"[TYPE] Тип: {activity_type.title()}\n"
            f"[TIME] Длительность: {duration} минут\n"
            f"[CALORIES] Сожжено калорий: {calories_burned:.0f} ккал\n\n"
            f"[INFO] <i>Отличная работа! Продолжайте быть активным! 💪</i>"
        )
    
    @staticmethod
    def progress_summary(period: str, stats: Dict, user) -> str:
        """Сводка прогресса за период"""
        period_names = {
            "day": "сегодня",
            "week": "за неделю", 
            "month": "за месяц",
            "all": "за всё время"
        }
        
        period_name = period_names.get(period, "за период")
        
        # Прогресс по калориям
        cal_progress = (stats.get('calories_consumed', 0) / user.daily_calorie_goal * 100) if user.daily_calorie_goal else 0
        
        # Оценка прогресса
        if cal_progress >= 90:
            rating = "🌟 Отлично!"
            emoji = "🏆"
        elif cal_progress >= 75:
            rating = "👍 Хорошо!"
            emoji = "👍"
        elif cal_progress >= 50:
            rating = "👌 Неплохо!"
            emoji = "😐"
        else:
            rating = "📈 Можно лучше!"
            emoji = "🎯"
        
        text = (
            f"📊 <b>Прогресс {period_name}:</b>\n\n"
            f"🍽️ Приёмов пищи: {stats.get('meals_count', 0)}\n"
            f"🔥 Калории: {stats.get('calories_consumed', 0):.0f} / {user.daily_calorie_goal:.0f} ккал ({cal_progress:.0f}%)\n"
            f"💧 Вода: {stats.get('water_consumed', 0):.0f} / {user.daily_water_goal:.0f} мл\n"
            f"🏃 Активность: {stats.get('activity_minutes', 0)} минут\n"
            f"⚖️ Вес: {stats.get('current_weight', 'N/A')} кг\n\n"
            f"{emoji} {rating}"
        )
        
        return text
    
    @staticmethod
    def ai_response_message(response: str, context: str = "general") -> str:
        """Форматирование ответа AI"""
        context_emojis = {
            "nutrition": "📊",
            "recipe": "📝", 
            "advice": "💡",
            "analysis": "🔍",
            "general": "[AI]"
        }
        
        emoji = context_emojis.get(context, "🤖")
        
        return (
            f"{emoji} <b>Ответ AI-ассистента:</b>\n\n"
            f"{response}\n\n"
            f"ℹ️ <i>Есть ещё вопросы? Просто спросите! 🤖</i>"
        )
    
    @staticmethod
    def error_message(error_type: str, details: str = "") -> str:
        """Красивое сообщение об ошибке"""
        error_messages = {
            "photo_error": "⚡ Не удалось обработать фото. Попробуйте сделать фото более чётким.",
            "profile_error": "👤 Сначала настройте профиль командой /set_profile",
            "database_error": "🗄️ Временная проблема с базой данных. Попробуйте позже.",
            "ai_error": "🤖 AI-сервис временно недоступен. Попробуйте позже.",
            "network_error": "🌐 Проблемы с соединением. Проверьте интернет.",
            "general_error": "❌ Произошла ошибка. Попробуйте ещё раз."
        }
        
        message = error_messages.get(error_type, error_messages["general_error"])
        
        if details:
            message += f"\n\n📋 <i>Детали: {details}</i>"
        
        return (
            f"❌ <b>Произошла ошибка</b>\n\n"
            f"{message}\n\n"
            f"🆘 <i>Если проблема повторяется, используйте /ask для связи с поддержкой.</i>"
        )
    
    @staticmethod
    def achievement_unlocked(achievement_name: str, description: str) -> str:
        """Сообщение о разблокированном достижении"""
        return (
            f"🏆 <b>Новое достижение!</b>\n\n"
            f"🏆 <b>{achievement_name}</b>\n"
            f"{description}\n\n"
            f"ℹ️ <i>Проверьте все достижения в профиле! 🏆</i>"
        )
    
    @staticmethod
    def daily_tip(tip_text: str) -> str:
        """Ежедневный совет"""
        return (
            f"💡 <b>Совет дня:</b>\n\n"
            f"💡 {tip_text}\n\n"
            f"ℹ️ <i>Следуйте советам для достижения целей! 🌟</i>"
        )
    
    @staticmethod
    def reminder_message(reminder_type: str, time: str) -> str:
        """Сообщение-напоминание"""
        reminder_messages = {
            "water": "💧 Не забывайте пить воду! 💧",
            "meal": "🍽️ Время приёма пищи! 🍽️",
            "activity": "🏃 Время для активности! 🏃",
            "sleep": "😴 Время отдыхать! 😴",
            "weigh": "⚖️ Время взвешиваться! ⚖️"
        }
        
        message = reminder_messages.get(reminder_type, "⏰ Напоминание")
        
        return (
            f"{message}\n\n"
            f"⏰ {time}\n\n"
            f"ℹ️ <i>Регулярность — ключ к успеху! 🔑</i>"
        )
    
    @staticmethod
    def motivational_message(progress_percentage: float, goal_type: str = "general") -> str:
        """Мотивационное сообщение"""
        if progress_percentage >= 95:
            return "🌟 Превосходно! Вы почти у цели! 🎯"
        elif progress_percentage >= 80:
            return "👍 Отлично! Продолжайте в том же духе! 💪"
        elif progress_percentage >= 60:
            return "👌 Хорошо! Продолжайте двигаться! 🏃"
        elif progress_percentage >= 40:
            return "📈 Есть куда расти! Не сдавайтесь! 📈"
        else:
            return "🌟 Каждое начало важно! Продолжайте! 🌟"
    
    @staticmethod
    def help_message() -> str:
        """Справка по боту"""
        return (
            f"❓ <b>Справка по NutriBuddy Bot</b>\n\n"
            f"📋 <b>Основные команды:</b>\n"
            f"/start - Начать работу\n"
            f"/set_profile - Настроить профиль\n"
            f"/profile - Посмотреть профиль\n"
            f"/help - Эта справка\n\n"
            f"🚀 <b>Возможности:</b>\n"
            f"⚡ 📸 Распознавание еды по фото\n"
            f"🤖 AI-ассистент по питанию\n"
            f"📊 Отслеживание прогресса\n"
            f"📝 Умные напоминания\n\n"
            f"ℹ️ <i>Просто отправьте фото еды или задайте вопрос! 🤖</i>"
        )
    
    @staticmethod
    def profile_summary(user, stats: Dict) -> str:
        """Сводка профиля"""
        return (
            f"👤 <b>Ваш профиль</b>\n\n"
            f"ℹ️ <b>Данные:</b>\n"
            f"⚖️ Вес: {user.weight} кг | 📏 Рост: {user.height} см\n"
            f"🎂 Возраст: {user.age} лет | 👫 Пол: {user.gender}\n"
            f"🎯 Цель: {user.goal} | 🏃 Активность: {user.activity_level}\n\n"
            f"📊 <b>Нормы:</b>\n"
            f"🔥 Калории: {user.daily_calorie_goal:.0f} ккал\n"
            f"🥩 Белки: {user.daily_protein_goal:.0f} г\n"
            f"🧈 Жиры: {user.daily_fat_goal:.0f} г\n"
            f"🍞 Углеводы: {user.daily_carbs_goal:.0f} г\n"
            f"💧 Вода: {user.daily_water_goal:.0f} мл\n\n"
            f"📅 <b>Сегодня:</b>\n"
            f"🍽️ Приёмов: {stats.get('meals_count', 0)}\n"
            f"🔥 Калории: {stats.get('calories_consumed', 0):.0f}/{user.daily_calorie_goal:.0f}\n"
            f"💧 Вода: {stats.get('water_consumed', 0):.0f}/{user.daily_water_goal:.0f} мл"
        )
