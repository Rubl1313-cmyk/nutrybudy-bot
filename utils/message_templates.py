"""
Премиальные шаблоны сообщений для NutriBuddy Bot
Элегантные карточки, графики, контекстные подсказки, персонализация
"""
from datetime import datetime
import logging

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
            f"🤖 <b>Добро пожаловать в NutriBuddy</b>\n"
            f"Ваш персональный AI-ассистент по питанию и здоровью\n\n"
            f"🎯 <b>Что я могу для вас сделать:</b>\n"
            f"📸 Распознать еду по фото\n"
            f"🤖 Ответить на вопросы о питании\n"
            f"📊 Показать ваш прогресс\n"
            f"🍽️ Составить план питания\n\n"
            f"💡 <b>Начните с создания профиля</b>\n"
            f"Команда: <code>/set_profile</code>\n\n"
            f"Или просто отправьте фото еды! 📸"
        )
    
    @staticmethod
    def modern_welcome_message(user_name: str = "Пользователь", 
                               days_active: int = 0, 
                               current_streak: int = 0) -> str:
        """
        🌟 Революционное приветствие NutriBuddy 2024
        """
        # Персонализированное приветствие с эмоциями
        if days_active == 0:
            greeting_emoji = "🌟"
            status_text = "Начнём ваше путешествие к здоровью!"
            motivation_emoji = "🚀"
        elif current_streak >= 7:
            greeting_emoji = "🔥"
            status_text = f"Вы на пути к цели уже {current_streak} дней!"
            motivation_emoji = "💪"
        else:
            greeting_emoji = "👋"
            status_text = "Продолжаем наш путь к здоровью!"
            motivation_emoji = "✨"
        
        # Визуально структурированное сообщение
        text = (
            f"{greeting_emoji} <b>Привет, {user_name}!</b>\n\n"
            f"🌿 <b>NutriBuddy</b>\n"
            f"<i>{status_text}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📸 <b>Фото еды</b> → я распознаю калории\n"
            f"✍️ <b>Текстом</b> → я пойму и запишу\n"
            f"📊 <b>Прогресс</b> → ваши достижения\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{motivation_emoji} <i>Отправьте фото еды — начнём сейчас!</i>"
        )
        
        return text

    @staticmethod
    def modern_meal_success(meal_type: str, calories: float, 
                          protein: float, fat: float, carbs: float,
                          daily_progress: float = 0) -> str:
        """
        � Эмоциональное сообщение об успехе 2024
        """
        # Эмоциональные реакции на прогресс
        if daily_progress >= 100:
            emoji = "🎉"
            message = "Отлично! Вы достигли дневной цели!"
        elif daily_progress >= 75:
            emoji = "🔥"
            message = "Прекрасно! Почти у цели!"
        elif daily_progress >= 50:
            emoji = "💪"
            message = "Хорошая работа! Продолжайте в том же духе!"
        else:
            emoji = "✨"
            message = "Отличное начало дня!"
        
        text = (
            f"{emoji} <b>Приём пищи сохранён!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>Питательность:</b>\n"
            f"🔥 {calories:.0f} ккал\n"
            f"🥩 {protein:.1f}г белки\n"
            f"🥑 {fat:.1f}г жиры\n"
            f"🍚 {carbs:.1f}г углеводы\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{message}\n"
            f"<i>Продолжайте в том же духе! 💚</i>"
        )
        
        return text
        # Современные эмодзи для приемов пищи
        meal_emojis = {
            'breakfast': '🌅',
            'lunch': '☀️',
            'dinner': '�',
            'snack': '🍎',
            'meal': '🍽️'
        }
        
        meal_names = {
            'breakfast': 'Завтрак',
            'lunch': 'Обед',
            'dinner': 'Ужин',
            'snack': 'Перекус',
            'meal': 'Прием пищи'
        }
        
        emoji = meal_emojis.get(meal_type, '🍽️')
        name = meal_names.get(meal_type, meal_type)
        
        # Мотивационный статус
        if calories <= 200:
            motivation = "💚 Легкий и полезный прием!"
        elif calories <= 500:
            motivation = "💛 Отличный баланс!"
        elif calories <= 800:
            motivation = "🧡 Сытно и питательно!"
        else:
            motivation = "❤️ Энергетический заряд!"
        
        text = (
            f"{emoji} <b>{name} записан!</b>\n"
            f"{'═' * 40}\n\n"
            f"� <b>Питательность:</b>\n"
            f"🔥 {calories:.0f} ккал\n"
            f"💪 {protein:.1f}г белков\n"
            f"🥑 {fat:.1f}г жиров\n"
            f"🍚 {carbs:.1f}г углеводов\n\n"
            f"{motivation}\n\n"
            f"✅ <i>Отличная работа! Продолжайте в том же духе! 💪</i>"
        )
        
        return text

    @staticmethod
    def daily_summary(date: str, total_cal: float, goal_cal: float,
                     protein: float, fat: float, carbs: float,
                     water_ml: float, water_goal: float,
                     streak: int) -> str:
        """Дневная сводка с красивой визуализацией"""
        
        from utils.ui_templates import ProgressBar
        
        cal_bar = ProgressBar.create_bar(total_cal, goal_cal, 12)
        water_bar = ProgressBar.create_bar(water_ml, water_goal, 12)
        
        cal_pct = (total_cal / goal_cal * 100) if goal_cal > 0 else 0
        water_pct = (water_ml / water_goal * 100) if water_goal > 0 else 0
        
        # Мотивационное сообщение
        if cal_pct >= 90 and cal_pct <= 110:
            motivation = "🎯 Отличный результат! Вы на цели!"
        elif cal_pct > 110:
            motivation = "⚠️ Немного больше, чем нужно. Завтра будет лучше!"
        elif cal_pct < 80:
            motivation = "💪 Не забывайте есть! Вы недостаточно едите."
        else:
            motivation = "👍 Хороший день!"
        
        text = (
            f"📅 <b>Сводка за {date}</b>\n"
            f"{'═' * 35}\n\n"
            
            f"<b>🔥 Калории</b>\n"
            f"{cal_bar} {total_cal:.0f}/{goal_cal:.0f} ({cal_pct:.0f}%)\n\n"
            
            f"<b>📊 Макронутриенты</b>\n"
            f"🥩 Белки: {protein:.0f}г\n"
            f"🥑 Жиры: {fat:.0f}г\n"
            f"🍚 Углеводы: {carbs:.0f}г\n\n"
            
            f"<b>💧 Вода</b>\n"
            f"{water_bar} {water_ml:.0f}/{water_goal:.0f} мл ({water_pct:.0f}%)\n\n"
            
            f"🔥 <b>Серия:</b> {streak} дней!\n\n"
            
            f"<i>{motivation}</i>"
        )
        
        return text

    @staticmethod
    def progress_report_weekly(week_data: dict, avg_cal: float, 
                              goal_cal: float, achievements: list) -> str:
        """Еженедельный отчёт о прогрессе"""
        
        from utils.ui_templates import StatisticsCard
        
        achievement_text = ""
        if achievements:
            achievement_text = "\n<b>🏆 Достижения:</b>\n"
            for achievement in achievements:
                achievement_text += f"✅ {achievement}\n"
        
        text = (
            f"📊 <b>Недельный отчёт</b>\n"
            f"{'═' * 35}\n\n"
            f"<b>Среднее потребление:</b> {avg_cal:.0f} ккал\n"
            f"<b>Цель:</b> {goal_cal:.0f} ккал\n\n"
            f"<b>Дни активности:</b>\n"
            f"{StatisticsCard.create_weekly_stats(week_data)}"
            f"{achievement_text}"
        )
        
        return text

    @staticmethod
    def photo_analysis_in_progress() -> str:
        """Сообщение с анимированным процессом анализа"""
        
        # Можно использовать разные кадры анимации
        frames = [
            "🔍 Анализирую...",
            "🤖 Обрабатываю...",
            "🧠 Думаю...",
            "✨ Почти готово..."
        ]
        
        return f"{''.join(frames)}"

    @staticmethod
    def recognition_confidence(confidence: float, dish_name: str) -> str:
        """Сообщение об уверенности распознавания"""
        
        if confidence >= 0.9:
            status = "🎯 Очень высокая уверенность"
        elif confidence >= 0.7:
            status = "✅ Хорошая уверенность"
        elif confidence >= 0.5:
            status = "⚠️ Средняя уверенность"
        else:
            status = "❓ Низкая уверенность"
        
        bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        
        return (
            f"{status}\n"
            f"{bar} {confidence*100:.0f}%\n"
            f"Распознано: <b>{dish_name}</b>"
        )

    @staticmethod
    def get_progress_welcome(user_name: str) -> str:
        """
        🎨 Современное приветствие раздела прогресса
        """
        return (
            f"📊 <b>Анализ прогресса, {user_name}!</b>\n\n"
            f"🎯 Выберите период для детальной статистики:\n"
            f"📈 Сегодняшние достижения\n"
            f"📆 Недельные тренды\n"
            f"📊 Месячные результаты\n"
            f"🌟 Общая картина\n\n"
            f"✨ <i>Каждый день - это шаг к цели!</i>"
        )

    @staticmethod
    def get_progress_motivation(stats: dict, user) -> str:
        """
        🎨 Мотивирующее сообщение на основе прогресса
        """
        motivations = []
        
        # Мотивация по калориям
        if stats['avg_cal_consumed'] <= user.daily_calorie_goal:
            motivations.append("🎯 Отличная работа с калориями!")
        else:
            motivations.append("💪 Сосредоточьтесь на калорийности завтра!")
        
        # Мотивация по воде
        if stats['avg_water'] >= user.daily_water_goal:
            motivations.append("💧 Идеальная гидратация!")
        else:
            motivations.append("💦 Не забывайте пить воду!")
        
        # Мотивация по активности
        if stats['activities_count'] > 0:
            motivations.append("🏃 Продолжайте в том же духе!")
        
        # Общая мотивация
        if len(motivations) >= 2:
            motivations.append("🌟 Вы на правильном пути!")
        
        return "\n".join(motivations) if motivations else "🚀 Продолжайте двигаться к своим целям!"

    @staticmethod
    def error_friendly(error_type: str) -> str:
        """Дружелюбные сообщения об ошибках"""
        
        errors = {
            'photo_bad': (
                "❌ <b>Фото не очень хорошего качества</b>\n"
                "Попробуйте:\n"
                "• Улучшить освещение 💡\n"
                "• Приблизиться к блюду 📸\n"
                "• Избежать размытости 🎯"
            ),
            'timeout': (
                "⏱️ <b>Анализ занял слишком долго</b>\n"
                "Попробуйте отправить фото снова"
            ),
            'no_food': (
                "🤔 <b>Я не вижу еды на фото</b>\n"
                "Отправьте фото блюда (не посуды, пожалуйста!)"
            ),
            'multiple_dishes': (
                "🍽️ <b>На фото несколько блюд</b>\n"
                "Отправьте фото каждого блюда отдельно"
            ),
            'unknown': (
                "🤷 <b>Не удалось распознать</b>\n"
                "Введите данные вручную или попробуйте другое фото"
            )
        }
        
        return errors.get(error_type, "❌ Произошла ошибка. Попробуйте снова.")
