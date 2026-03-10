"""
Шаблоны для красивой визуализации UI в Telegram
✨ Реплицирует стиль современных приложений
"""

class ProgressBar:
    """Красивые прогресс-бары с emoji"""
    
    @staticmethod
    def create_bar(current: float, total: float, length: int = 10, show_percentage: bool = True) -> str:
        """
        Создаёт красивый прогресс-бар
        
        Args:
            current: текущее значение
            total: максимальное значение
            length: длина бара в символах (1-20)
            show_percentage: показывать процент
        
        Returns:
            красивый бар с emoji
        """
        if total <= 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        filled = int(length * current / total) if total > 0 else 0
        empty = length - filled
        
        bar = "🟩" * filled + "⬜" * empty
        
        if show_percentage:
            return f"{bar} {percentage:.0f}%"
        return bar

    @staticmethod
    def create_bar_vertical(current: float, total: float, height: int = 5) -> str:
        """Вертикальный прогресс-бар"""
        if total <= 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        filled = int(height * current / total) if total > 0 else 0
        
        bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        return bars[min(int(percentage / 12.5), 7)]

class NutritionCard:
    """Красивые карточки питания"""
    
    @staticmethod
    def create_macro_card(protein: float, fat: float, carbs: float) -> str:
        """
        Красивая карточка макронутриентов
        
        Returns:
            отформатированная строка с данными
        """
        total_macros = protein + fat + carbs
        if total_macros == 0:
            return "📊 Нет данных"
        
        protein_pct = (protein / total_macros) * 100
        fat_pct = (fat / total_macros) * 100
        carbs_pct = (carbs / total_macros) * 100
        
        text = (
            "📊 <b>Макронутриенты</b>\n"
            f"🥩 Белки:   {protein:.0f}г ({protein_pct:.0f}%)\n"
            f"🥑 Жиры:    {fat:.0f}г ({fat_pct:.0f}%)\n"
            f"🍚 Углеводы: {carbs:.0f}г ({carbs_pct:.0f}%)"
        )
        return text

    @staticmethod
    def create_macros_pie_chart(protein: float, fat: float, carbs: float) -> str:
        """
        Круговая диаграмма БЖУ (текстовая)
        🥩 █████░░░░ 35%
        """
        total = protein + fat + carbs
        if total == 0:
            return "Нет данных"
        
        p_pct = int((protein / total) * 100)
        f_pct = int((fat / total) * 100)
        c_pct = int((carbs / total) * 100)
        
        bar_len = 10
        p_bar = "█" * int(p_pct / 10) + "░" * (bar_len - int(p_pct / 10))
        f_bar = "█" * int(f_pct / 10) + "░" * (bar_len - int(f_pct / 10))
        c_bar = "█" * int(c_pct / 10) + "░" * (bar_len - int(c_pct / 10))
        
        return (
            f"🥩 {p_bar} {p_pct}%\n"
            f"🥑 {f_bar} {f_pct}%\n"
            f"🍚 {c_bar} {c_pct}%"
        )

    @staticmethod
    def create_daily_goal_card(current_cal: float, goal_cal: float, 
                               current_protein: float, goal_protein: float,
                               current_fat: float, goal_fat: float,
                               current_carbs: float, goal_carbs: float) -> str:
        """Прогресс к дневной цели"""
        
        cal_bar = ProgressBar.create_bar(current_cal, goal_cal, 12, False)
        protein_bar = ProgressBar.create_bar(current_protein, goal_protein, 12, False)
        fat_bar = ProgressBar.create_bar(current_fat, goal_fat, 12, False)
        carbs_bar = ProgressBar.create_bar(current_carbs, goal_carbs, 12, False)
        
        cal_pct = (current_cal / goal_cal * 100) if goal_cal > 0 else 0
        protein_pct = (current_protein / goal_protein * 100) if goal_protein > 0 else 0
        fat_pct = (current_fat / goal_fat * 100) if goal_fat > 0 else 0
        carbs_pct = (current_carbs / goal_carbs * 100) if goal_carbs > 0 else 0
        
        text = (
            "📈 <b>Прогресс дня</b>\n\n"
            f"🔥 Калории\n"
            f"{cal_bar} {current_cal:.0f}/{goal_cal:.0f} ({cal_pct:.0f}%)\n\n"
            f"🥩 Белки\n"
            f"{protein_bar} {current_protein:.0f}г/{goal_protein:.0f}г ({protein_pct:.0f}%)\n\n"
            f"🥑 Жиры\n"
            f"{fat_bar} {current_fat:.0f}г/{goal_fat:.0f}г ({fat_pct:.0f}%)\n\n"
            f"🍚 Углеводы\n"
            f"{carbs_bar} {current_carbs:.0f}г/{goal_carbs:.0f}г ({carbs_pct:.0f}%)"
        )
        return text

class MealCard:
    """Красивые карточки приёмов пищи"""
    
    @staticmethod
    def create_meal_summary(meal_type: str, foods: list, total_cal: float, 
                           total_protein: float, total_fat: float, total_carbs: float) -> str:
        """
        Красивая сводка приёма пищи
        
        Args:
            meal_type: "breakfast", "lunch", "dinner", "snack"
            foods: список продуктов
            total_cal, total_protein, etc: итоговые значения
        """
        
        meal_emoji = {
            'breakfast': '🥐',
            'lunch': '🥗',
            'dinner': '🍲',
            'snack': '🍎'
        }
        
        meal_names = {
            'breakfast': 'Завтрак',
            'lunch': 'Обед',
            'dinner': 'Ужин',
            'snack': 'Перекус'
        }
        
        emoji = meal_emoji.get(meal_type, '🍽️')
        name = meal_names.get(meal_type, meal_type)
        
        # Список продуктов
        foods_text = ""
        for i, food in enumerate(foods, 1):
            weight = food.get('weight', 0)
            foods_text += f"{i}. {food['name']}: {weight:.0f}г\n"
        
        # Итоги
        text = (
            f"{emoji} <b>{name}</b>\n"
            f"{'─' * 30}\n"
            f"{foods_text}\n"
            f"{'─' * 30}\n"
            f"🔥 {total_cal:.0f} ккал | 🥩 {total_protein:.1f}г | "
            f"🥑 {total_fat:.1f}г | 🍚 {total_carbs:.1f}г"
        )
        return text

    @staticmethod
    def create_meal_timeline(meals: list) -> str:
        """
        Временная шкала приёмов пищи за день
        
        meals = [
            {'type': 'breakfast', 'time': '08:00', 'cal': 350},
            {'type': 'lunch', 'time': '13:00', 'cal': 680},
            ...
        ]
        """
        
        meal_emoji = {
            'breakfast': '🥐',
            'lunch': '🥗',
            'dinner': '🍲',
            'snack': '🍎'
        }
        
        timeline = "📅 <b>Приёмы пищи</b>\n"
        
        for i, meal in enumerate(meals):
            emoji = meal_emoji.get(meal['type'], '🍽️')
            time = meal.get('time', '??:??')
            cal = meal.get('cal', 0)
            
            if i < len(meals) - 1:
                separator = "│\n"
            else:
                separator = ""
            
            timeline += f"{emoji} {time} — {cal:.0f} ккал\n{separator}"
        
        return timeline

class WaterTracker:
    """Красивое отслеживание воды"""
    
    @staticmethod
    def create_water_bottle_chart(current_ml: float, goal_ml: float = 2000) -> str:
        """
        Визуализация бутылки воды
        
        ┏━━━━━┓
        ┃█████┃ 1500/2000 мл (75%)
        ┃█████┃
        ┃░░░░░┃
        ┗━━━━━┛
        """
        percentage = min((current_ml / goal_ml) * 100, 100)
        filled_lines = int(percentage / 20)
        
        bottle = (
            "┏━━━━━┓\n"
        )
        
        for i in range(5):
            if i < filled_lines:
                bottle += "┃█████┃\n"
            else:
                bottle += "┃░░░░░┃\n"
        
        bottle += "┗━━━━━┛\n"
        bottle += f"💧 {current_ml:.0f}/{goal_ml:.0f} мл ({percentage:.0f}%)"
        
        return bottle

    @staticmethod
    def create_water_message(current_ml: float, goal_ml: float = 2000) -> str:
        """Мотивационное сообщение о воде"""
        percentage = min((current_ml / goal_ml) * 100, 100)
        
        if percentage < 25:
            mood = "😴 Нужно пить больше воды!"
            emoji = "💧"
        elif percentage < 50:
            mood = "🙂 Хороший старт!"
            emoji = "💧💧"
        elif percentage < 75:
            mood = "😊 Почти готово!"
            emoji = "💧💧💧"
        elif percentage < 100:
            mood = "🎉 Почти у цели!"
            emoji = "💧💧💧💧"
        else:
            mood = "🏆 Дневная норма достигнута!"
            emoji = "💧💧💧💧💧"
        
        bar = ProgressBar.create_bar(current_ml, goal_ml, 15)
        
        return (
            f"{emoji} <b>{mood}</b>\n"
            f"{bar}\n"
            f"{current_ml:.0f}/{goal_ml:.0f} мл"
        )

class ActivityCard:
    """Красивые карточки активности"""
    
    @staticmethod
    def create_activity_card(activity_type: str, duration: int, calories: float) -> str:
        """
        activity_type: 'running', 'gym', 'cycling', 'yoga', 'swimming'
        """
        
        activity_emoji = {
            'running': '🏃',
            'gym': '🏋️',
            'cycling': '🚴',
            'yoga': '🧘',
            'swimming': '🏊',
            'walking': '🚶'
        }
        
        activity_names = {
            'running': 'Бег',
            'gym': 'Тренажёрный зал',
            'cycling': 'Велосипед',
            'yoga': 'Йога',
            'swimming': 'Плавание',
            'walking': 'Ходьба'
        }
        
        emoji = activity_emoji.get(activity_type, '💪')
        name = activity_names.get(activity_type, activity_type)
        
        # Визуализация времени
        minutes_per_block = 5
        blocks = int(duration / minutes_per_block)
        time_bar = "⏱️ " + "█" * blocks + f" {duration} мин"
        
        text = (
            f"{emoji} <b>{name}</b>\n"
            f"{time_bar}\n"
            f"🔥 Сожжено: {calories:.0f} ккал"
        )
        return text

class StreakCard:
    """Красивые серии достижений"""
    
    @staticmethod
    def create_streak_card(streak_days: int, max_streak: int = 0) -> str:
        """Визуализация серии дней"""
        
        if streak_days == 0:
            return "🔥 Начните серию сегодня!"
        
        flame_emojis = ["🔥"] * min(streak_days, 5)
        
        text = (
            f"{''.join(flame_emojis)} <b>Серия: {streak_days} дней подряд!</b>\n"
            f"📈 Максимум: {max_streak} дней"
        )
        
        if streak_days >= 7:
            text += "\n🏆 Неделя активности!"
        if streak_days >= 30:
            text += "\n👑 Месяц активности!"
        if streak_days >= 100:
            text += "\n💎 100 дней! Вы легенда!"
        
        return text

class StatisticsCard:
    """Статистика и графики"""
    
    @staticmethod
    def create_weekly_stats(week_data: list) -> str:
        """
        week_data = [
            {'day': 'Пн', 'cal': 1800, 'achieved': True},
            {'day': 'Вт', 'cal': 2100, 'achieved': True},
            ...
        ]
        """
        text = "📊 <b>Неделя</b>\n"
        text += "─" * 30 + "\n"
        
        for day_data in week_data:
            day = day_data['day']
            cal = day_data['cal']
            achieved = day_data.get('achieved', False)
            
            status = "✅" if achieved else "❌"
            
            # Простой бар для каждого дня
            bar_length = int(cal / 250)
            bar = "█" * min(bar_length, 8)
            
            text += f"{status} {day:3} {bar:8} {cal:.0f} ккал\n"
        
        return text

    @staticmethod
    def create_monthly_heatmap(month_data: dict) -> str:
        """
        month_data = {
            1: {'cal': 1800, 'water': 2000},
            2: {'cal': 2100, 'water': 1500},
            ...
        }
        
        Создаёт визуальную тепловую карту месяца
        """
        
        text = "🔥 <b>Активность месяца</b>\n"
        text += "Пн  Вт  Ср  Чт  Пт  Сб  Вс\n"
        
        # Условные уровни активности
        def get_heat_emoji(calories: float) -> str:
            if calories >= 2200:
                return "🔥"  # Очень активен
            elif calories >= 1800:
                return "🟠"  # Активен
            elif calories >= 1400:
                return "🟡"  # Норм
            elif calories > 0:
                return "🟢"  # Мало
            else:
                return "⬜"  # Нет данных
        
        # Упрощённая визуализация (1 строка на неделю)
        week = []
        for day in range(1, 32):
            if day in month_data:
                cal = month_data[day].get('cal', 0)
                week.append(get_heat_emoji(cal))
            else:
                week.append("⬜")
            
            if len(week) == 7:
                text += " ".join(week) + "\n"
                week = []
        
        if week:
            text += " ".join(week) + "\n"
        
        return text
