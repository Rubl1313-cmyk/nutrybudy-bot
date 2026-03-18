from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict

def get_meal_type_keyboard():
    """Клавиатура для выбора типа приема пищи"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🥐 Завтрак", callback_data="meal_breakfast")
    builder.button(text="🍽️ Обед", callback_data="meal_lunch")
    builder.button(text="🍽️ Ужин", callback_data="meal_dinner")
    builder.button(text="🥨 Перекус", callback_data="meal_snack")
    builder.adjust(2)
    return builder.as_markup()

def get_water_preset_keyboard():
    """Клавиатура для быстрых объемов воды"""
    builder = InlineKeyboardBuilder()
    for amount in [200, 300, 500, 1000]:
        builder.button(text=f"{amount} мл 💧", callback_data=f"water_{amount}")
    builder.adjust(2)
    return builder.as_markup()

def get_food_overview_keyboard(selected_foods: List[Dict]) -> InlineKeyboardMarkup:
    """Клавиатура для сводки продуктов."""
    buttons = []
    for i, food in enumerate(selected_foods):
        status = "✅" if food['weight'] else "⬜"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {food['name']}",
                callback_data=f"edit_food_{i}"
            )
        ])
    
    # Добавляем кнопки действий
    buttons.extend([
        [InlineKeyboardButton(text="➕ Добавить продукт", callback_data="add_product")],
        [InlineKeyboardButton(text="✅ Сохранить всё", callback_data="save_all")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_progress_menu():
    """Меню выбора периода для прогресса"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сегодня", callback_data="progress_today")
    builder.button(text="📆 Неделя", callback_data="progress_week")
    builder.button(text="🗓️ Месяц", callback_data="progress_month")
    builder.button(text="📊 Всё время", callback_data="progress_all")
    builder.adjust(2)
    return builder.as_markup()

def get_activity_type_keyboard():
    """Клавиатура для выбора типа активности"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏃 Бег", callback_data="activity_running")
    builder.button(text="🚴 Велосипед", callback_data="activity_cycling")
    builder.button(text="🏋️ Тренировка", callback_data="activity_gym")
    builder.button(text="🧘 Йога", callback_data="activity_yoga")
    builder.button(text="🚶 Ходьба", callback_data="activity_walking")
    builder.button(text="🏊 Плавание", callback_data="activity_swimming")
    builder.button(text="🤸 Другое", callback_data="activity_other")
    builder.adjust(2)
    return builder.as_markup()

def get_weight_options_keyboard():
    """Клавиатура для опций записи веса"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Только вес", callback_data="weight_only")
    builder.button(text="📊 + % жира", callback_data="weight_fat")
    builder.button(text="💪 + мышечная масса", callback_data="weight_muscle")
    builder.button(text="🧬 + все параметры", callback_data="weight_all")
    builder.adjust(2)
    return builder.as_markup()

def get_achievements_menu():
    """Меню достижений"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏆 Мои достижения", callback_data="my_achievements")
    builder.button(text="📊 Статистика", callback_data="achievement_stats")
    builder.button(text="🎯 Цели", callback_data="achievement_goals")
    builder.button(text="🏅 Лидерboard", callback_data="leaderboard")
    builder.adjust(2)
    return builder.as_markup()

def get_settings_menu():
    """Меню настроек"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔔 Напоминания", callback_data="settings_reminders")
    builder.button(text="📊 Цели", callback_data="settings_goals")
    builder.button(text=" Тема", callback_data="settings_theme")
    builder.button(text="ℹ️ О боте", callback_data="settings_about")
    builder.adjust(2)
    return builder.as_markup()

def get_language_menu():
    """Меню выбора языка"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.button(text="🇩🇪 Deutsch", callback_data="lang_de")
    builder.button(text="🇫🇷 Français", callback_data="lang_fr")
    builder.adjust(2)
    return builder.as_markup()

def get_reminders_menu():
    """Меню настроек напоминаний"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🍽️ Приёмы пищи", callback_data="reminders_meals")
    builder.button(text="💧 Вода", callback_data="reminders_water")
    builder.button(text="🏃‍♂️ Активность", callback_data="reminders_activity")
    builder.button(text="⚖️ Взвешивания", callback_data="reminders_weight")
    builder.button(text="📊 Отчёты", callback_data="reminders_reports")
    builder.button(text="🔄 Все напоминания", callback_data="reminders_all")
    builder.adjust(2)
    return builder.as_markup()

def get_goals_menu():
    """Меню управления целями"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Питание", callback_data="goals_nutrition")
    builder.button(text="💧 Вода", callback_data="goals_water")
    builder.button(text="🏃‍♂️ Активность", callback_data="goals_activity")
    builder.button(text="⚖️ Вес", callback_data="goals_weight")
    builder.adjust(2)
    return builder.as_markup()

def get_meal_plan_menu():
    """Меню плана питания"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Создать план", callback_data="meal_plan_create")
    builder.button(text="📋 Мой план", callback_data="meal_plan_view")
    builder.button(text="📊 Статистика", callback_data="meal_plan_stats")
    builder.button(text="⚙️ Настройки", callback_data="meal_plan_settings")
    builder.adjust(2)
    return builder.as_markup()

def get_ai_assistant_menu():
    """Меню AI ассистента"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Задать вопрос", callback_data="ai_ask")
    builder.button(text="📸 Распознать еду", callback_data="ai_photo")
    builder.button(text="🍽️ План питания", callback_data="ai_meal_plan")
    builder.button(text="🏃‍♂️ Тренировка", callback_data="ai_workout")
    builder.button(text="💡 Советы", callback_data="ai_tips")
    builder.button(text="📚 Помощь", callback_data="ai_help")
    builder.adjust(2)
    return builder.as_markup()

def get_profile_menu():
    """Меню профиля"""
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Данные", callback_data="profile_data")
    builder.button(text="📊 Статистика", callback_data="profile_stats")
    builder.button(text="🎯 Цели", callback_data="profile_goals")
    builder.button(text="🏆 Достижения", callback_data="profile_achievements")
    builder.button(text="⚙️ Настройки", callback_data="profile_settings")
    builder.button(text="🔄 Экспорт", callback_data="profile_export")
    builder.adjust(2)
    return builder.as_markup()

def get_confirmation_keyboard(action: str, text: str = "Подтвердить действие") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data=f"confirm_{action}")
    builder.button(text="❌ Нет", callback_data=f"cancel_{action}")
    builder.adjust(2)
    return builder.as_markup()

def get_navigation_keyboard(back_callback: str = "back", home_callback: str = "home") -> InlineKeyboardMarkup:
    """Навигационная клавиатура"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data=back_callback)
    builder.button(text="🏠 Главное меню", callback_data=home_callback)
    builder.adjust(2)
    return builder.as_markup()

def get_food_edit_keyboard(food_index: int) -> InlineKeyboardMarkup:
    """Клавиатура редактирования продукта"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить вес", callback_data=f"edit_weight_{food_index}")
    builder.button(text="🗑️ Удалить", callback_data=f"delete_food_{food_index}")
    builder.button(text="🔄 Заменить", callback_data=f"replace_food_{food_index}")
    builder.adjust(1)
    return builder.as_markup()

def get_water_quick_keyboard() -> InlineKeyboardMarkup:
    """Быстрая клавиатура для воды"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💧 200 мл", callback_data="water_quick_200")
    builder.button(text="💧 250 мл", callback_data="water_quick_250")
    builder.button(text="💧 350 мл", callback_data="water_quick_350")
    builder.button(text="💧 500 мл", callback_data="water_quick_500")
    builder.button(text="💧 750 мл", callback_data="water_quick_750")
    builder.button(text="💧 1000 мл", callback_data="water_quick_1000")
    builder.adjust(2)
    return builder.as_markup()

def get_drink_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа напитка"""
    builder = InlineKeyboardBuilder()
    builder.button(text="☕ Кофе", callback_data="drink_coffee")
    builder.button(text="🍵 Чай", callback_data="drink_tea")
    builder.button(text="🥤 Сок", callback_data="drink_juice")
    builder.button(text="🥛 Молоко", callback_data="drink_milk")
    builder.button(text="🥤 Кола", callback_data="drink_cola")
    builder.button(text="🍺 Пиво", callback_data="drink_beer")
    builder.button(text="🍷 Вино", callback_data="drink_wine")
    builder.button(text="🥃 Другое", callback_data="drink_other")
    builder.adjust(2)
    return builder.as_markup()

def get_workout_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа тренировки"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💪 Силовая", callback_data="workout_strength")
    builder.button(text="🏃 Кардио", callback_data="workout_cardio")
    builder.button(text="🧘 Растяжка", callback_data="workout_stretching")
    builder.button(text="🤸 HIIT", callback_data="workout_hiit")
    builder.button(text="🏊 Плавание", callback_data="workout_swimming")
    builder.button(text="🚴 Велотренировка", callback_data="workout_cycling")
    builder.button(text="🥊 Бокс", callback_data="workout_boxing")
    builder.button(text="🧘‍♂️ Йога", callback_data="workout_yoga")
    builder.adjust(2)
    return builder.as_markup()

def get_intensity_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора интенсивности"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Низкая", callback_data="intensity_low")
    builder.button(text="🟡 Средняя", callback_data="intensity_medium")
    builder.button(text="🔴 Высокая", callback_data="intensity_high")
    builder.button(text="⚡ Максимальная", callback_data="intensity_max")
    builder.adjust(2)
    return builder.as_markup()

def get_time_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора времени"""
    builder = InlineKeyboardBuilder()
    
    # Часы
    for hour in range(6, 24, 2):
        builder.button(text=f"{hour}:00", callback_data=f"time_{hour}_00")
    
    # Популярные времена
    builder.button(text="7:00", callback_data="time_7_00")
    builder.button(text="8:00", callback_data="time_8_00")
    builder.button(text="12:00", callback_data="time_12_00")
    builder.button(text="18:00", callback_data="time_18_00")
    builder.button(text="20:00", callback_data="time_20_00")
    
    builder.adjust(3)
    return builder.as_markup()

def get_duration_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора длительности"""
    builder = InlineKeyboardBuilder()
    
    # Популярные длительности в минутах
    durations = [15, 20, 30, 45, 60, 90, 120]
    
    for duration in durations:
        builder.button(text=f"{duration} мин", callback_data=f"duration_{duration}")
    
    builder.adjust(3)
    return builder.as_markup()

def get_weight_unit_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора единиц веса"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 кг", callback_data="unit_kg")
    builder.button(text="🇺🇸 lbs", callback_data="unit_lbs")
    builder.button(text="🇬🇧 stone", callback_data="unit_stone")
    builder.adjust(3)
    return builder.as_markup()

def get_export_menu() -> InlineKeyboardMarkup:
    """Меню экспорта данных"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 CSV", callback_data="export_csv")
    builder.button(text="📈 JSON", callback_data="export_json")
    builder.button(text="📄 PDF", callback_data="export_pdf")
    builder.button(text="📱 Excel", callback_data="export_excel")
    builder.button(text="🔄 Все данные", callback_data="export_all")
    builder.button(text="📅 За период", callback_data="export_period")
    builder.adjust(2)
    return builder.as_markup()

def get_help_menu() -> InlineKeyboardMarkup:
    """Меню помощи"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Руководство", callback_data="help_guide")
    builder.button(text="❓ FAQ", callback_data="help_faq")
    builder.button(text="🎥 Видеоуроки", callback_data="help_videos")
    builder.button(text="💬 Поддержка", callback_data="help_support")
    builder.button(text="📞 Контакты", callback_data="help_contacts")
    builder.button(text="ℹ️ О боте", callback_data="help_about")
    builder.adjust(2)
    return builder.as_markup()

def get_premium_features_menu() -> InlineKeyboardMarkup:
    """Меню премиум функций"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 AI Анализатор", callback_data="premium_ai")
    builder.button(text="📊 Детальная статистика", callback_data="premium_stats")
    builder.button(text="🍽️ Персональные планы", callback_data="premium_plans")
    builder.button(text="🏆 Расширенные достижения", callback_data="premium_achievements")
    builder.button(text="📱 Экспорт данных", callback_data="premium_export")
    builder.button(text="⚙️ Расширенные настройки", callback_data="premium_settings")
    builder.adjust(2)
    return builder.as_markup()

# Утилитарные функции

def create_back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Создать кнопку 'Назад'"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data=callback_data)
    return builder.as_markup()

def create_home_button(callback_data: str = "home") -> InlineKeyboardMarkup:
    """Создать кнопку 'Главное меню'"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Главное меню", callback_data=callback_data)
    return builder.as_markup()

def create_close_button(callback_data: str = "close") -> InlineKeyboardMarkup:
    """Создать кнопку 'Закрыть'"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Закрыть", callback_data=callback_data)
    return builder.as_markup()

def create_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "page") -> InlineKeyboardMarkup:
    """Создать клавиатуру пагинации"""
    builder = InlineKeyboardBuilder()
    
    # Первая страница
    if current_page > 1:
        builder.button(text="⏪", callback_data=f"{prefix}_1")
    
    # Предыдущая страница
    if current_page > 1:
        builder.button(text="◀️", callback_data=f"{prefix}_{current_page - 1}")
    
    # Текущая страница
    builder.button(text=f"{current_page}/{total_pages}", callback_data="current")
    
    # Следующая страница
    if current_page < total_pages:
        builder.button(text="▶️", callback_data=f"{prefix}_{current_page + 1}")
    
    # Последняя страница
    if current_page < total_pages:
        builder.button(text="⏩", callback_data=f"{prefix}_{total_pages}")
    
    builder.adjust(5)
    return builder.as_markup()
