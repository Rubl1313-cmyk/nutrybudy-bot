"""
Интеллектуальные клавиатуры для NutriBuddy Bot
Адаптивные, контекстные, премиальные
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict
from datetime import datetime

class SmartKeyboard:
    """Интеллектуальные клавиатуры с адаптацией под контекст"""
    
    @staticmethod
    def quick_actions(user_context: Dict) -> InlineKeyboardMarkup:
        """Генерирует клавиатуру с предсказанными действиями на основе контекста."""
        builder = InlineKeyboardBuilder()
        hour = user_context.get('hour', datetime.now().hour)
        last_actions = user_context.get('last_actions', [])

        # Утренние действия
        if 5 <= hour < 11:
            builder.button(text="🍳 Записать завтрак", callback_data="quick_breakfast")
            builder.button(text="💧 Выпить воды", callback_data="water_add_250")
        # Дневные
        elif 11 <= hour < 17:
            builder.button(text="🍲 Записать обед", callback_data="quick_lunch")
            builder.button(text="🏃‍♂️ Активность", callback_data="menu_activity")
        # Вечерние
        else:
            builder.button(text="🍽️ Записать ужин", callback_data="quick_dinner")
            builder.button(text="⚖️ Записать вес", callback_data="menu_log_weight")

        # Если пользователь часто записывает воду, добавим кнопку воды
        if last_actions.count('water') > 2:
            builder.button(text="💧 +250 мл", callback_data="water_add_250")

        builder.button(text="📊 Прогресс", callback_data="show_progress")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def food_selection_with_recent(foods: List[Dict], recent: List[str]) -> InlineKeyboardMarkup:
        """Клавиатура выбора продукта с учётом недавних."""
        builder = InlineKeyboardBuilder()
        # Сначала недавние
        for name in recent[:3]:
            builder.button(text=f"🔄 {name}", callback_data=f"food_recent_{name}")
        # Затем результаты поиска
        for i, food in enumerate(foods[:5]):
            builder.button(
                text=f"{food['name']} — {food.get('calories', 0):.0f} ккал",
                callback_data=f"food_{i}"
            )
        builder.button(text="✍️ Ввести вручную", callback_data="food_manual")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def contextual_meal_suggestions(meal_type: str, user_preferences: Dict) -> InlineKeyboardMarkup:
        """Контекстные предложения блюд на основе предпочтений"""
        builder = InlineKeyboardBuilder()
        
        # Предложения на основе типа приема пищи
        if meal_type == "breakfast":
            suggestions = [
                "🥞 Овсянка с ягодами",
                "🍳 Яичница с тостами",
                "🥛 Сырники",
                "🥤 Смузи"
            ]
        elif meal_type == "lunch":
            suggestions = [
                "🍲 Куриный суп",
                "🍛 Салат Цезарь",
                "🍛 Гречка с котлетой",
                "🍕 Пицца"
            ]
        elif meal_type == "dinner":
            suggestions = [
                "🍽️ Запеченная рыба",
                "🥩 Стейк с овощами",
                "🍛 Салат с тунцом",
                "🍝 Паста"
            ]
        else:  # snack
            suggestions = [
                "🍎 Яблоко",
                "🥛 Йогурт",
                "🥜 Орехи",
                "🍌 Банан"
            ]
        
        for suggestion in suggestions:
            builder.button(text=suggestion, callback_data=f"quick_select_{suggestion}")
        
        builder.button(text="✍️ Ввести вручную", callback_data="manual_food")
        builder.button(text="📸 Сделать фото", callback_data="photo_food")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def premium_progress_options() -> InlineKeyboardMarkup:
        """Премиальные опции прогресса"""
        builder = InlineKeyboardBuilder()
        builder.button(text="📅 Сегодня", callback_data="progress_day")
        builder.button(text="📆 Неделя", callback_data="progress_week")
        builder.button(text="📊 Месяц", callback_data="progress_month")
        builder.button(text="🏆 Достижения", callback_data="achievements")
        builder.button(text="📈 Графики", callback_data="show_charts")
        builder.button(text="❌ Закрыть", callback_data="close")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def smart_water_suggestions(current_intake: int, daily_goal: int) -> InlineKeyboardMarkup:
        """Умные предложения воды на основе текущего потребления"""
        builder = InlineKeyboardBuilder()
        
        remaining = daily_goal - current_intake
        
        if remaining <= 0:
            builder.button(text="🎯 Цель достигнута!", callback_data="water_goal_met")
        elif remaining <= 250:
            builder.button(text=f"💧 Допить {remaining} мл", callback_data=f"water_add_{remaining}")
        else:
            # Предлагаем стандартные порции
            amounts = [200, 250, 300, 500]
            for amount in amounts:
                if amount <= remaining:
                    builder.button(text=f"💧 +{amount} мл", callback_data=f"water_add_{amount}")
        
        builder.button(text="📊 Статистика воды", callback_data="water_stats")
        builder.button(text="⚙️ Изменить цель", callback_data="edit_water_goal")
        builder.button(text="❌ Закрыть", callback_data="close")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def contextual_main_menu(user_context: Dict) -> InlineKeyboardMarkup:
        """Контекстное главное меню"""
        builder = InlineKeyboardBuilder()
        hour = user_context.get('hour', datetime.now().hour)
        
        # Адаптивные кнопки на основе времени
        if 5 <= hour < 11:
            builder.button(text="🍳 Завтрак", callback_data="meal_breakfast")
            builder.button(text="📊 Прогресс", callback_data="show_progress")
        elif 11 <= hour < 17:
            builder.button(text="🍲 Обед", callback_data="meal_lunch")
            builder.button(text="💧 Вода", callback_data="log_water")
        else:
            builder.button(text="🍽️ Ужин", callback_data="meal_dinner")
            builder.button(text="📊 Прогресс", callback_data="show_progress")
        
        # Постоянные кнопки
        builder.button(text="👤 Профиль", callback_data="show_profile")
        builder.button(text="🤖 AI Ассистент", callback_data="ai_assistant")
        builder.button(text="⚙️ Настройки", callback_data="settings")
        
        builder.adjust(2)
        return builder.as_markup()

class PremiumKeyboard:
    """Премиальные стили клавиатур"""
    
    @staticmethod
    def luxury_main_menu() -> InlineKeyboardMarkup:
        """Роскошное главное меню"""
        builder = InlineKeyboardBuilder()
        
        # Первая строка - основные действия
        builder.button(text="📸 🍽️ Фото еды", callback_data="photo_food")
        builder.button(text="📊 📈 Прогресс", callback_data="show_progress")
        
        # Вторая строка - питание
        builder.button(text="🍳 🍽️ Питание", callback_data="food_menu")
        builder.button(text="💧 💦 Вода", callback_data="water_menu")
        
        # Третья строка - активность
        builder.button(text="🏃 🏃 Активность", callback_data="activity_menu")
        builder.button(text="⚖️ ⚖️ Вес", callback_data="weight_menu")
        
        # Четвертая строка - аналитика
        builder.button(text="👤 👤 Профиль", callback_data="show_profile")
        builder.button(text="🤖 🤖 AI Помощь", callback_data="ai_assistant")
        
        # Пятая строка - настройки
        builder.button(text="⚙️ ⚙️ Настройки", callback_data="settings")
        
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def gradient_progress_bar(current: float, total: float, length: int = 12) -> str:
        """Градиентный прогресс-бар"""
        if total <= 0:
            percentage = 0
        else:
            percentage = min((current / total) * 100, 100)
        
        filled = int(length * percentage / 100)
        empty = length - filled
        
        # Градиент от синего к золотому
        gradient_chars = ['🟦', '🟦', '🟦', '🟦', '🟨', '🟩', '🟨', '🟦']
        
        bar = ""
        for i in range(length):
            if i < filled:
                bar += gradient_chars[i % len(gradient_chars)]
            else:
                bar += '⬜'
        
        # Добавляем звездочку если прогресс высокий
        if percentage >= 90:
            bar = bar[:-1] + '⭐'
        
        return f"{bar} <code>{percentage:.0f}%</code>"
    
    @staticmethod
    def animated_loading_button(text: str, callback_data: str) -> InlineKeyboardButton:
        """Анимированная кнопка загрузки"""
        return InlineKeyboardButton(text=f"⏳ {text}", callback_data=callback_data)
    
    @staticmethod
    def success_button(text: str, callback_data: str) -> InlineKeyboardButton:
        """Кнопка успеха"""
        return InlineKeyboardButton(text=f"✅ {text}", callback_data=callback_data)
    
    @staticmethod
    def warning_button(text: str, callback_data: str) -> InlineKeyboardButton:
        """Кнопка предупреждения"""
        return InlineKeyboardButton(text=f"⚠️ {text}", callback_data=callback_data)

def get_modern_main_menu() -> InlineKeyboardMarkup:
    """
    🌿 Эмоциональное меню NutriBuddy 2024
    Визуальная иерархия + мотивация
    """
    builder = InlineKeyboardBuilder()
    
    # Главная CTA кнопка - самая заметная
    builder.row(
        InlineKeyboardButton(text="📸 Сделать фото еды", callback_data="photo_food")
    )
    
    # Разделитель для визуального отделения
    builder.row(
        InlineKeyboardButton(text="━━━━━━━━━━━━━", callback_data="none")
    )
    
    # Второстепенные действия
    builder.row(
        InlineKeyboardButton(text="📊 Мой прогресс", callback_data="show_progress")
    )
    
    builder.row(
        InlineKeyboardButton(text="👤 Мой профиль", callback_data="show_profile")
    )
    
    return builder.as_markup()

def get_motivational_food_keyboard() -> InlineKeyboardMarkup:
    """
    🌿 Мотивационная клавиатура для еды
    Эмоциональный подход к выбору
    """
    builder = InlineKeyboardBuilder()
    
    # Основные приемы пищи с эмotions
    builder.row(
        InlineKeyboardButton(text="🌅 Завтрак", callback_data="meal_breakfast"),
        InlineKeyboardButton(text="☀️ Обед", callback_data="meal_lunch")
    )
    
    builder.row(
        InlineKeyboardButton(text="🌙 Ужин", callback_data="meal_dinner"),
        InlineKeyboardButton(text="🍎 Перекус", callback_data="meal_snack")
    )
    
    return builder.as_markup()

def get_modern_food_keyboard() -> InlineKeyboardMarkup:
    """
    🍽️ Современная клавиатура для работы с едой
    """
    builder = InlineKeyboardBuilder()
    
    # Основные действия
    builder.row(
        InlineKeyboardButton(text="📸 Распознать по фото", callback_data="photo_food"),
        InlineKeyboardButton(text="✍️ Ввести вручную", callback_data="manual_food")
    )
    
    # Быстрые опции
    builder.row(
        InlineKeyboardButton(text="🥐 Завтрак", callback_data="quick_breakfast"),
        InlineKeyboardButton(text="🥗 Обед", callback_data="quick_lunch")
    )
    
    builder.row(
        InlineKeyboardButton(text="🍲 Ужин", callback_data="quick_dinner"),
        InlineKeyboardButton(text="🍎 Перекус", callback_data="quick_snack")
    )
    
    # История и статистика
    builder.row(
        InlineKeyboardButton(text="📜 Сегодня", callback_data="today_summary"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="food_stats")
    )
    
    return builder.as_markup()

def get_modern_water_keyboard(current_ml: int, goal_ml: int = 2000) -> InlineKeyboardMarkup:
    """
    💧 Современная клавиатура для отслеживания воды
    """
    builder = InlineKeyboardBuilder()
    
    # Быстрые добавки
    builder.row(
        InlineKeyboardButton(text="💧 +100мл", callback_data="water_add_100"),
        InlineKeyboardButton(text="💧 +200мл", callback_data="water_add_200"),
        InlineKeyboardButton(text="💧 +250мл", callback_data="water_add_250")
    )
    
    builder.row(
        InlineKeyboardButton(text="🥤 +500мл", callback_data="water_add_500"),
        InlineKeyboardButton(text="🫙 +1000мл", callback_data="water_add_1000")
    )
    
    # Прогресс
    percentage = min((current_ml / goal_ml) * 100, 100)
    progress_emoji = "🎯" if percentage >= 100 else "👍" if percentage >= 75 else "💪" if percentage >= 50 else "💧"
    
    builder.row(
        InlineKeyboardButton(
            text=f"{progress_emoji} {current_ml}/{goal_ml}мл ({percentage:.0f}%)", 
            callback_data="water_progress"
        )
    )
    
    # Управление
    builder.row(
        InlineKeyboardButton(text="📊 График", callback_data="water_chart"),
        InlineKeyboardButton(text="⚙️ Цель", callback_data="water_goal")
    )
    
    return builder.as_markup()

def get_food_recognition_result_keyboard(
    has_matches: bool = True,
    can_use_ai_ingredients: bool = True
) -> InlineKeyboardMarkup:
    """
    🎨 Современная клавиатура для результатов распознавания еды
    """
    builder = InlineKeyboardBuilder()
    
    if has_matches:
        builder.button(
            text="🍽️ Выбрать из базы",
            callback_data="select_from_db"
        )
    
    if can_use_ai_ingredients:
        builder.button(
            text="🔍 Разобрать на ингредиенты",
            callback_data="use_ingredients_instead"
        )
    
    builder.button(
        text="✍️ Ввести вручную",
        callback_data="manual_food_entry"
    )
    
    builder.button(
        text="🔄 Перераспознать",
        callback_data="retry_photo"
    )
    
    builder.button(
        text="❌ Отмена",
        callback_data="action_cancel"
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_daily_goals_keyboard() -> InlineKeyboardMarkup:
    """
    🎯 Клавиатура для дневных целей
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Изменить цели", callback_data="edit_goals"),
        InlineKeyboardButton(text="📈 Статистика", callback_data="show_stats")
    )
    
    builder.row(
        InlineKeyboardButton(text="💧 Цель воды", callback_data="water_goal"),
        InlineKeyboardButton(text="🏋️ Цель калорий", callback_data="calorie_goal")
    )
    
    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
        InlineKeyboardButton(text="❌ Закрыть", callback_data="close")
    )
    
    return builder.as_markup()

def get_time_period_keyboard() -> InlineKeyboardMarkup:
    """
    ⏰ Клавиатура выбора периода
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Сегодня", callback_data="period_today"),
        InlineKeyboardButton(text="📆 Неделя", callback_data="period_week")
    )
    
    builder.row(
        InlineKeyboardButton(text="📊 Месяц", callback_data="period_month"),
        InlineKeyboardButton(text="📈 Всё время", callback_data="period_all")
    )
    
    builder.row(
        InlineKeyboardButton(text="❌ Закрыть", callback_data="close")
    )
    
    return builder.as_markup()

def get_macro_adjustment_keyboard(food_index: int, totals_msg_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для быстрого редактирования макронутриентов
    """
    builder = InlineKeyboardBuilder()
    
    # Быстрые пресеты веса
    builder.row(
        InlineKeyboardButton(text="➖10г", callback_data=f"weight_dec_{food_index}_10_{totals_msg_id}"),
        InlineKeyboardButton(text="➖50г", callback_data=f"weight_dec_{food_index}_50_{totals_msg_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="➕10г", callback_data=f"weight_inc_{food_index}_10_{totals_msg_id}"),
        InlineKeyboardButton(text="➕50г", callback_data=f"weight_inc_{food_index}_50_{totals_msg_id}")
    )
    
    # Быстрые пресеты
    builder.row(
        InlineKeyboardButton(text="100г", callback_data=f"weight_set_{food_index}_100_{totals_msg_id}"),
        InlineKeyboardButton(text="150г", callback_data=f"weight_set_{food_index}_150_{totals_msg_id}"),
        InlineKeyboardButton(text="200г", callback_data=f"weight_set_{food_index}_200_{totals_msg_id}")
    )
    
    # Управление
    builder.row(
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"weight_del_{food_index}_{totals_msg_id}"),
        InlineKeyboardButton(text="✅ Готово", callback_data="close_macro_edit")
    )
    
    return builder.as_markup()
