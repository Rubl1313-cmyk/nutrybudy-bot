from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """
    Основное меню NutriBuddy 2026
    Визуальная иерархия + премиальный дизайн
    """
    kb = [
        # Основные функции - самый большой блок
        [KeyboardButton(text="🍽️ Записать приём пищи")],
        
        # Второстепенные функции
        [KeyboardButton(text="💧 Вода")],
        [KeyboardButton(text="🏃‍♂️ Активность")],
        [KeyboardButton(text="⚖️ Вес")],
        
        # Статистика и прогресс
        [KeyboardButton(text="📊 Прогресс")],
        [KeyboardButton(text="🍽️ План питания")],
        [KeyboardButton(text="🏆 Достижения")],
        
        # AI и профиль
        [KeyboardButton(text="🤖 AI ассистент")],
        [KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="⚙️ Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def get_edit_profile_keyboard():
    """Клавиатура редактирования профиля"""
    kb = [
        [KeyboardButton(text="✅ Изменить профиль")],
        [KeyboardButton(text="📊 Мой прогресс")],
        [KeyboardButton(text="🏆 Достижения")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_food_keyboard():
    """Клавиатура для записи еды"""
    kb = [
        [KeyboardButton(text="📸 Распознать еду")],
        [KeyboardButton(text="✍️ Ввести вручную")],
        [KeyboardButton(text="🍽️ Избранное")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_water_keyboard():
    """Клавиатура для записи воды"""
    kb = [
        [KeyboardButton(text="💧 200 мл")],
        [KeyboardButton(text="💧 250 мл")],
        [KeyboardButton(text="💧 350 мл")],
        [KeyboardButton(text="💧 500 мл")],
        [KeyboardButton(text="💧 750 мл")],
        [KeyboardButton(text="💧 1000 мл")],
        [KeyboardButton(text="🥤 Другой напиток")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_activity_keyboard():
    """Клавиатура для записи активности"""
    kb = [
        [KeyboardButton(text="🏃 Бег")],
        [KeyboardButton(text="🚴 Велосипед")],
        [KeyboardButton(text="🏋️ Тренировка")],
        [KeyboardButton(text="🧘 Йога")],
        [KeyboardButton(text="🚶 Ходьба")],
        [KeyboardButton(text="🏊 Плавание")],
        [KeyboardButton(text="🤸 Другое")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_weight_keyboard():
    """Клавиатура для записи веса"""
    kb = [
        [KeyboardButton(text="⚖️ Только вес")],
        [KeyboardButton(text="📊 + % жира")],
        [KeyboardButton(text="💪 + мышечная масса")],
        [KeyboardButton(text="🧬 + все параметры")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_progress_keyboard():
    """Клавиатура для просмотра прогресса"""
    kb = [
        [KeyboardButton(text="📅 Сегодня")],
        [KeyboardButton(text="📆 Неделя")],
        [KeyboardButton(text="🗓️ Месяц")],
        [KeyboardButton(text="📊 Всё время")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_meal_plan_keyboard():
    """Клавиатура для плана питания"""
    kb = [
        [KeyboardButton(text="🍽️ Создать план")],
        [KeyboardButton(text="📋 Мой план")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_achievements_keyboard():
    """Клавиатура достижений"""
    kb = [
        [KeyboardButton(text="🏆 Мои достижения")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🎯 Цели")],
        [KeyboardButton(text="🏅 Лидерboard")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_ai_assistant_keyboard():
    """Клавиатура AI ассистента"""
    kb = [
        [KeyboardButton(text="💬 Задать вопрос")],
        [KeyboardButton(text="📸 Распознать еду")],
        [KeyboardButton(text="🍽️ План питания")],
        [KeyboardButton(text="🏃‍♂️ Тренировка")],
        [KeyboardButton(text="💡 Советы")],
        [KeyboardButton(text="📚 Помощь")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_profile_keyboard():
    """Клавиатура профиля"""
    kb = [
        [KeyboardButton(text="👤 Данные")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🎯 Цели")],
        [KeyboardButton(text="🏆 Достижения")],
        [KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="🔄 Экспорт")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_settings_keyboard():
    """Клавиатура настроек"""
    kb = [
        [KeyboardButton(text="🔔 Напоминания")],
        [KeyboardButton(text="📊 Цели")],
        [KeyboardButton(text="🌐 Язык")],
        [KeyboardButton(text="🎨 Тема")],
        [KeyboardButton(text="🔄 Синхронизация")],
        [KeyboardButton(text="ℹ️ О боте")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_reminders_keyboard():
    """Клавиатура настроек напоминаний"""
    kb = [
        [KeyboardButton(text="🍽️ Приёмы пищи")],
        [KeyboardButton(text="💧 Вода")],
        [KeyboardButton(text="🏃‍♂️ Активность")],
        [KeyboardButton(text="⚖️ Взвешивания")],
        [KeyboardButton(text="📊 Отчёты")],
        [KeyboardButton(text="🔄 Все напоминания")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_goals_keyboard():
    """Клавиатура управления целями"""
    kb = [
        [KeyboardButton(text="📊 Питание")],
        [KeyboardButton(text="💧 Вода")],
        [KeyboardButton(text="🏃‍♂️ Активность")],
        [KeyboardButton(text="⚖️ Вес")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_language_keyboard():
    """Клавиатура выбора языка"""
    kb = [
        [KeyboardButton(text="🇷🇺 Русский")],
        [KeyboardButton(text="🇬🇧 English")],
        [KeyboardButton(text="🇩🇪 Deutsch")],
        [KeyboardButton(text="🇫🇷 Français")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_theme_keyboard():
    """Клавиатура выбора темы"""
    kb = [
        [KeyboardButton(text="🌞 Светлая")],
        [KeyboardButton(text="🌙 Тёмная")],
        [KeyboardButton(text="🌈 Авто")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_help_keyboard():
    """Клавиатура помощи"""
    kb = [
        [KeyboardButton(text="📖 Руководство")],
        [KeyboardButton(text="❓ FAQ")],
        [KeyboardButton(text="🎥 Видеоуроки")],
        [KeyboardButton(text="💬 Поддержка")],
        [KeyboardButton(text="📞 Контакты")],
        [KeyboardButton(text="ℹ️ О боте")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_export_keyboard():
    """Клавиатура экспорта данных"""
    kb = [
        [KeyboardButton(text="📊 CSV")],
        [KeyboardButton(text="📈 JSON")],
        [KeyboardButton(text="📄 PDF")],
        [KeyboardButton(text="📱 Excel")],
        [KeyboardButton(text="🔄 Все данные")],
        [KeyboardButton(text="📅 За период")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_premium_keyboard():
    """Клавиатура премиум функций"""
    kb = [
        [KeyboardButton(text="🤖 AI Анализатор")],
        [KeyboardButton(text="📊 Детальная статистика")],
        [KeyboardButton(text="🍽️ Персональные планы")],
        [KeyboardButton(text="🏆 Расширенные достижения")],
        [KeyboardButton(text="📱 Экспорт данных")],
        [KeyboardButton(text="⚙️ Расширенные настройки")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_workout_keyboard():
    """Клавиатура тренировок"""
    kb = [
        [KeyboardButton(text="💪 Силовая")],
        [KeyboardButton(text="🏃 Кардио")],
        [KeyboardButton(text="🧘 Растяжка")],
        [KeyboardButton(text="🤸 HIIT")],
        [KeyboardButton(text="🏊 Плавание")],
        [KeyboardButton(text="🚴 Велотренировка")],
        [KeyboardButton(text="🥊 Бокс")],
        [KeyboardButton(text="🧘‍♂️ Йога")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_intensity_keyboard():
    """Клавиатура выбора интенсивности"""
    kb = [
        [KeyboardButton(text="🟢 Низкая")],
        [KeyboardButton(text="🟡 Средняя")],
        [KeyboardButton(text="🔴 Высокая")],
        [KeyboardButton(text="⚡ Максимальная")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_duration_keyboard():
    """Клавиатура выбора длительности"""
    kb = [
        [KeyboardButton(text="15 мин")],
        [KeyboardButton(text="20 мин")],
        [KeyboardButton(text="30 мин")],
        [KeyboardButton(text="45 мин")],
        [KeyboardButton(text="60 мин")],
        [KeyboardButton(text="90 мин")],
        [KeyboardButton(text="120 мин")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_drink_type_keyboard():
    """Клавиатура выбора типа напитка"""
    kb = [
        [KeyboardButton(text="☕ Кофе")],
        [KeyboardButton(text="🍵 Чай")],
        [KeyboardButton(text="🥤 Сок")],
        [KeyboardButton(text="🥛 Молоко")],
        [KeyboardButton(text="🥤 Кола")],
        [KeyboardButton(text="🍺 Пиво")],
        [KeyboardButton(text="🍷 Вино")],
        [KeyboardButton(text="🥃 Другое")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_meal_type_keyboard():
    """Клавиатура выбора типа приема пищи"""
    kb = [
        [KeyboardButton(text="🥐 Завтрак")],
        [KeyboardButton(text="🍽️ Обед")],
        [KeyboardButton(text="🍽️ Ужин")],
        [KeyboardButton(text="🥨 Перекус")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_weight_unit_keyboard():
    """Клавиатура выбора единиц веса"""
    kb = [
        [KeyboardButton(text="🇷🇺 кг")],
        [KeyboardButton(text="🇺🇸 lbs")],
        [KeyboardButton(text="🇬🇧 stone")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_confirmation_keyboard():
    """Клавиатура подтверждения"""
    kb = [
        [KeyboardButton(text="✅ Да")],
        [KeyboardButton(text="❌ Нет")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_navigation_keyboard():
    """Навигационная клавиатура"""
    kb = [
        [KeyboardButton(text="🔙 Назад")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_back_keyboard():
    """Клавиатура с кнопкой 'Назад'"""
    kb = [
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_home_keyboard():
    """Клавиатура с кнопкой 'Главное меню'"""
    kb = [
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Утилитарные функции

def create_simple_keyboard(buttons: list) -> ReplyKeyboardMarkup:
    """Создать простую клавиатуру из списка кнопок"""
    kb = [[KeyboardButton(text=button)] for button in buttons]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def create_grid_keyboard(buttons: list, columns: int = 2) -> ReplyKeyboardMarkup:
    """Создать клавиатуру с кнопками в сетке"""
    kb = []
    for i in range(0, len(buttons), columns):
        row = buttons[i:i + columns]
        kb.append([KeyboardButton(text=button) for button in row])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def create_menu_keyboard(menu_items: dict) -> ReplyKeyboardMarkup:
    """Создать клавиатуру из словаря {текст: callback_data}"""
    kb = []
    for text, _ in menu_items.items():
        kb.append([KeyboardButton(text=text)])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
