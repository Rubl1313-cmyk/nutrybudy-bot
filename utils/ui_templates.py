"""
🎨 Современные UI шаблоны для NutriBuddy Bot
✨ Стиль как в современных фитнес-приложениях
🚀 Минималистичный дизайн с умными эмодзи
"""

class ProgressBar:
    """🎯 Современные прогресс-бары с градиентами и анимацией"""
    
    # Градиентные эмодзи для разных уровней
    GRADIENTS = {
        'low': ['🔴', '🟠', '🟡'],      # 0-33%
        'medium': ['🟡', '🟢', '🔵'],    # 34-66%
        'high': ['🔵', '🟣', '🔷'],     # 67-100%
        'complete': ['🟢', '✨', '🎆']   # 100%
    }
    
    # Анимационные кадры
    ANIMATION_FRAMES = ['⚡', '✨', '🌟', '💫', '⭐']
    
    @staticmethod
    def create_modern_bar(current: float, total: float, length: int = 12, 
                         style: str = 'gradient', show_text: bool = True) -> str:
        """
        Создает современный прогресс-бар с градиентами
        
        Args:
            current: текущее значение
            total: максимальное значение  
            length: длина бара
            style: 'gradient', 'minimal', 'neon'
            show_text: показывать текст
        """
        if total <= 0:
            percentage = 0
        else:
            percentage = min((current / total) * 100, 100)
        
        filled = int(length * percentage / 100)
        empty = length - filled
        
        if style == 'gradient':
            # Градиентный стиль - одноцветный
            bar = '🟦' * filled + '⬜' * empty
        elif style == 'neon':
            # Неоновый стиль - одноцветный
            bar = '🟦' * filled + '⬜' * empty
        else:
            # Минималистичный стиль
            bar = '▓' * filled + '░' * empty
        
        if show_text:
            if percentage >= 100:
                return f"{bar} ✅ {percentage:.0f}%"
            elif percentage >= 75:
                return f"{bar} 🔥 {percentage:.0f}%"
            else:
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
    """🎨 Современные карточки питания в стиле фитнес-приложений"""
    
    # Современные эмодзи для категорий
    MODERN_EMOJIS = {
        'protein': ['💪', '🥩', '🍗', '🦴'],
        'carbs': ['🍞', '🍚', '🥔', '🌾'],
        'fat': ['🥑', '🧈', '🫒', '🥛'],
        'vitamins': ['🥬', '🥕', '🍊', '🍓']
    }
    
    @staticmethod
    def create_modern_macro_card(protein: float, fat: float, carbs: float, 
                                calories: float = 0, style: str = 'compact') -> str:
        """
        Создает современную карточку макронутриентов
        
        Args:
            style: 'compact', 'detailed', 'minimal'
        """
        total_macros = protein + fat + carbs
        if total_macros == 0:
            return "📊 Нет данных о питательности"
        
        protein_pct = (protein / total_macros) * 100
        fat_pct = (fat / total_macros) * 100
        carbs_pct = (carbs / total_macros) * 100
        
        if style == 'compact':
            # Компактный стиль
            text = (
                f"🎯 <b>КБЖУ</b>\n"
                f"💪 {protein:.0f}г ({protein_pct:.0f}%) | "
                f"🥑 {fat:.0f}г ({fat_pct:.0f}%) | "
                f"🍚 {carbs:.0f}г ({carbs_pct:.0f}%)"
            )
            if calories > 0:
                text += f"\n🔥 {calories:.0f} ккал"
        elif style == 'detailed':
            # Детальный стиль с прогресс-барами
            protein_bar = ProgressBar.create_modern_bar(protein, total_macros, 8, 'gradient', False)
            fat_bar = ProgressBar.create_modern_bar(fat, total_macros, 8, 'gradient', False)
            carbs_bar = ProgressBar.create_modern_bar(carbs, total_macros, 8, 'gradient', False)
            
            text = (
                f"📊 <b>Анализ питательности</b>\n"
                f"{'═' * 35}\n\n"
                f"💪 <b>Белки</b>\n{protein_bar} {protein:.1f}г ({protein_pct:.0f}%)\n\n"
                f"🥑 <b>Жиры</b>\n{fat_bar} {fat:.1f}г ({fat_pct:.0f}%)\n\n"
                f"🍚 <b>Углеводы</b>\n{carbs_bar} {carbs:.1f}г ({carbs_pct:.0f}%)"
            )
            if calories > 0:
                text += f"\n\n{'═' * 35}\n🔥 <b>Калории</b>: {calories:.0f} ккал"
        else:
            # Минималистичный стиль
            text = f"💪{protein:.0f}g 🥑{fat:.0f}g 🍚{carbs:.0f}g"
            if calories > 0:
                text += f" 🔥{calories:.0f}"
        
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
    def create_modern_daily_goal_card(current_cal: float, goal_cal: float, 
                                     current_protein: float, goal_protein: float,
                                     current_fat: float, goal_fat: float,
                                     current_carbs: float, goal_carbs: float,
                                     style: str = 'modern') -> str:
        """
        Создает современную карточку дневных целей с анимацией
        
        Args:
            style: 'modern', 'compact', 'detailed'
        """
        
        # Рассчитываем проценты
        cal_pct = min((current_cal / goal_cal * 100) if goal_cal > 0 else 0, 150)
        protein_pct = min((current_protein / goal_protein * 100) if goal_protein > 0 else 0, 150)
        fat_pct = min((current_fat / goal_fat * 100) if goal_fat > 0 else 0, 150)
        carbs_pct = min((current_carbs / goal_carbs * 100) if goal_carbs > 0 else 0, 150)
        
        if style == 'modern':
            # Современный стиль с градиентами
            cal_bar = ProgressBar.create_modern_bar(current_cal, goal_cal, 12, 'gradient')
            protein_bar = ProgressBar.create_modern_bar(current_protein, goal_protein, 10, 'gradient')
            fat_bar = ProgressBar.create_modern_bar(current_fat, goal_fat, 10, 'gradient')
            carbs_bar = ProgressBar.create_modern_bar(current_carbs, goal_carbs, 10, 'gradient')
            
            # Определяем статус дня
            if 90 <= cal_pct <= 110:
                status_emoji = "🎯"
                status_text = "Идеально!"
            elif cal_pct > 110:
                status_emoji = "⚡"
                status_text = "Сверхцель!"
            elif cal_pct >= 75:
                status_emoji = "👍"
                status_text = "Хорошо!"
            else:
                status_emoji = "💪"
                status_text = "Нужно больше!"
            
            text = (
                f"{status_emoji} <b>Прогресс дня</b>\n"
                f"{'═' * 40}\n"
                f"🔥 <b>Калории</b>\n{cal_bar}\n"
                f"{current_cal:.0f}/{goal_cal:.0f} ккал\n\n"
                f"💪 <b>Белки</b>\n{protein_bar}\n"
                f"{current_protein:.0f}/{goal_protein:.0f}г\n\n"
                f"🥑 <b>Жиры</b>\n{fat_bar}\n"
                f"{current_fat:.0f}/{goal_fat:.0f}г\n\n"
                f"🍚 <b>Углеводы</b>\n{carbs_bar}\n"
                f"{current_carbs:.0f}/{goal_carbs:.0f}g\n\n"
                f"{'═' * 40}\n"
                f"{status_emoji} <b>{status_text}</b>"
            )
            
        elif style == 'compact':
            # Компактный стиль
            text = (
                f"� <b>День</b>\n"
                f"🔥 {current_cal:.0f}/{goal_cal:.0f} ({cal_pct:.0f}%)\n"
                f"� {current_protein:.0f}/{goal_protein:.0f}г ({protein_pct:.0f}%)\n"
                f"🥑 {current_fat:.0f}/{goal_fat:.0f}г ({fat_pct:.0f}%)\n"
                f"🍚 {current_carbs:.0f}/{goal_carbs:.0f}г ({carbs_pct:.0f}%)"
            )
        else:
            # Детальный стиль
            text = (
                f"📈 <b>Детальный прогресс дня</b>\n"
                f"{'═' * 45}\n\n"
                f"🔥 КАЛОРИИ: {current_cal:.0f} из {goal_cal:.0f} ({cal_pct:.1f}%)\n"
                f"💪 БЕЛКИ: {current_protein:.1f}г из {goal_protein:.0f}г ({protein_pct:.1f}%)\n"
                f"🥑 ЖИРЫ: {current_fat:.1f}г из {goal_fat:.0f}г ({fat_pct:.1f}%)\n"
                f"🍚 УГЛЕВОДЫ: {current_carbs:.1f}г из {goal_carbs:.0f}г ({carbs_pct:.1f}%)"
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
