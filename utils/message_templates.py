"""
Красивые шаблоны сообщений
"""

class MessageTemplates:
    
    @staticmethod
    def welcome_message(user_name: str = "Пользователь") -> str:
        """Красивое приветствие"""
        return (
            f"👋 <b>Добро пожаловать, {user_name}!</b>\n\n"
            f"Я <b>NutriBuddy</b> — ваш персональный помощник по питанию.\n\n"
            f"<b>Что я могу делать:</b>\n"
            f"📸 <code>Распознавать</code> блюда по фото\n"
            f"🧮 <code>Считать</code> калории и макросы\n"
            f"📊 <code>Отслеживать</code> ваш прогресс\n"
            f"💪 <code>Мотивировать</code> вас к целям\n\n"
            f"<i>Начните с отправки фото блюда! 📸</i>"
        )

    @staticmethod
    def meal_recorded_success(meal_type: str, calories: float, 
                             protein: float, fat: float, carbs: float) -> str:
        """Сообщение об успешной записи приёма"""
        
        meal_emoji = {
            'breakfast': '🥐',
            'lunch': '🥗',
            'dinner': '🍲',
            'snack': '🍎'
        }
        
        emoji = meal_emoji.get(meal_type, '🍽️')
        
        return (
            f"{emoji} <b>Приём пищи записан!</b>\n"
            f"{'─' * 35}\n"
            f"🔥 Калории: {calories:.0f} ккал\n"
            f"🥩 Белки: {protein:.1f}г\n"
            f"🥑 Жиры: {fat:.1f}г\n"
            f"🍚 Углеводы: {carbs:.1f}г\n"
            f"{'─' * 35}\n"
            f"✅ <i>Отличная работа! Продолжайте так!</i>"
        )

    @staticmethod
    def daily_summary(date: str, total_cal: float, goal_cal: float,
                     protein: float, fat: float, carbs: float,
                     water_ml: float, water_goal: float,
                     streak: int) -> str:
        """Дневная сводка с красивой визуализацией"""
        
        from utils.ui_templates import ProgressBar, NutritionCard
        
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
