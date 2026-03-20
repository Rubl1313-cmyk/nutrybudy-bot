"""
utils/premium_messages.py
Премиальные шаблоны сообщений с современным дизайном
"""
from typing import Dict, Optional, List
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 🎨 ОФОРМЛЕНИЕ И СТИЛИ
# ═══════════════════════════════════════════════════════════════

class PremiumStyle:
    """Стили для премиум оформления"""
    
    # Разделители
    DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    DIVIDER_DASH = "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"
    DIVIDER_DOT = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"
    
    # Уголки
    CORNER_TL = "┌"
    CORNER_TR = "┐"
    CORNER_BL = "└"
    CORNER_BR = "┘"
    
    # Эмодзи по категориям
    EMOJIS = {
        'food': ['🍽️', '🍔', '🥗', '🍕', '🍜', '🍱'],
        'water': ['💧', '🥤', '☕', '🍵', '🧃', '🍶'],
        'activity': ['🏃', '🚴', '🏋️', '🧘', '🏊', '🎾'],
        'weight': ['⚖️', '📊', '📈', '📉', '🎯'],
        'success': ['✅', '🎉', '🏆', '⭐', '🌟', '💫'],
        'error': ['❌', '⚠️', '🚫', '❗'],
        'info': ['ℹ️', '💡', '📌', '🔔'],
        'profile': ['👤', '👤‍💼', '🎯', '🏆'],
    }


# ═══════════════════════════════════════════════════════════════
# 🎯 ПРОГРЕСС БАРЫ
# ═══════════════════════════════════════════════════════════════

class PremiumProgressBar:
    """Премиум прогресс бары"""
    
    @staticmethod
    def create(
        current: float,
        total: float,
        length: int = 10,
        style: str = "modern"
    ) -> str:
        """Создать прогресс бар"""
        if total <= 0:
            percentage = 0
        else:
            percentage = min((current / total) * 100, 100)
        
        filled = int(length * percentage / 100)
        empty = length - filled
        
        styles = {
            'modern': {'filled': '▰', 'empty': '▱'},
            'classic': {'filled': '█', 'empty': '░'},
            'line': {'filled': '━', 'empty': '─'},
            'block': {'filled': '⬛', 'empty': '⬜'},
            'circle': {'filled': '🔴', 'empty': '⚪'},
            'star': {'filled': '⭐', 'empty': '☆'},
        }
        
        style_config = styles.get(style, styles['modern'])
        bar = style_config['filled'] * filled + style_config['empty'] * empty
        
        return bar, percentage
    
    @staticmethod
    def create_with_label(
        current: float,
        total: float,
        label: str,
        length: int = 10,
        style: str = "modern",
        show_values: bool = True
    ) -> str:
        """Создать прогресс бар с лейблом"""
        bar, percentage = PremiumProgressBar.create(current, total, length, style)
        
        if show_values:
            return f"{label}\n{bar} <code>{percentage:.0f}%</code> ({current:.0f}/{total:.0f})"
        else:
            return f"{label}\n{bar} <code>{percentage:.0f}%</code>"
    
    @staticmethod
    def create_nutrition_bars(stats: Dict, goals: Dict) -> str:
        """Создать прогресс бары для БЖУ"""
        lines = []
        
        # Калории
        cal_bar, cal_pct = PremiumProgressBar.create(
            stats.get('calories', 0),
            goals.get('calories', 2000),
            style='modern'
        )
        lines.append(f"🔥 Калории: {cal_bar} <code>{cal_pct:.0f}%</code>")
        
        # Белки
        prot_bar, prot_pct = PremiumProgressBar.create(
            stats.get('protein', 0),
            goals.get('protein', 150),
            style='classic'
        )
        lines.append(f"🥩 Белки:   {prot_bar} <code>{prot_pct:.0f}%</code>")
        
        # Жиры
        fat_bar, fat_pct = PremiumProgressBar.create(
            stats.get('fat', 0),
            goals.get('fat', 65),
            style='classic'
        )
        lines.append(f"🧈 Жиры:    {fat_bar} <code>{fat_pct:.0f}%</code>")
        
        # Углеводы
        carb_bar, carb_pct = PremiumProgressBar.create(
            stats.get('carbs', 0),
            goals.get('carbs', 250),
            style='classic'
        )
        lines.append(f"🍞 Углеводы:{carb_bar} <code>{carb_pct:.0f}%</code>")
        
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════
# 📦 КАРТОЧКИ
# ═══════════════════════════════════════════════════════════════

class PremiumCards:
    """Премиум карточки"""
    
    @staticmethod
    def welcome(user_name: str) -> str:
        """Приветственная карточка"""
        return f"""
{PremiumStyle.DIVIDER}
✨ <b>Добро пожаловать, {user_name}!</b> ✨
{PremiumStyle.DIVIDER}

🤖 <b>Я — ваш персональный AI помощник</b>
   по здоровому питанию <b>NutriBuddy</b>!

🎯 <b>Что я умею:</b>
├ 📸 Распознаю еду по фото
├ 📊 Считаю калории и БЖУ
├ 💧 Контролирую водный баланс
├ 🏃 Учитываю активность
├ 📈 Строю графики прогресса
└ 🏆 Мотивирую к достижению целей

⚡ <b>Начните прямо сейчас:</b>
├ 🍽️ Запишите прием пищи
├ 💧 Выпейте воды
└ 👤 Настройте профиль

{PremiumStyle.DIVIDER_DOT}
🌟 <i>Ваш путь к здоровой жизни начинается здесь!</i>
{PremiumStyle.DIVIDER}
"""

    @staticmethod
    def food_logged(
        food_name: str,
        calories: float,
        protein: float,
        fat: float,
        carbs: float,
        meal_type: str = "",
        daily_stats: Dict = None,
        goals: Dict = None
    ) -> str:
        """Карточка записи еды"""
        meal_emojis = {
            'breakfast': '🌅',
            'lunch': '🌞',
            'dinner': '🌆',
            'snack': '🍪'
        }
        meal_names = {
            'breakfast': 'Завтрак',
            'lunch': 'Обед',
            'dinner': 'Ужин',
            'snack': 'Перекус'
        }
        
        emoji = meal_emojis.get(meal_type, '🍽️')
        name = meal_names.get(meal_type, meal_type)
        
        lines = [
            f"{PremiumStyle.DIVIDER}",
            f"{emoji} <b>{name} записан!</b>",
            f"{PremiumStyle.DIVIDER}",
            f"",
            f"🍽️ <b>{food_name}</b>",
            f"",
            f"📊 <b>Пищевая ценность:</b>",
            f"├ 🔥 Калории:  <code>{calories:.0f} ккал</code>",
            f"├ 🥩 Белки:    <code>{protein:.1f} г</code>",
            f"├ 🧈 Жиры:     <code>{fat:.1f} г</code>",
            f"└ 🍞 Углеводы: <code>{carbs:.1f} г</code>",
        ]
        
        if daily_stats and goals:
            lines.extend([
                f"",
                f"{PremiumStyle.DIVIDER_DASH}",
                f"📊 <b>Прогресс за сегодня:</b>",
            ])
            
            # Прогресс по калориям
            cal_bar, cal_pct = PremiumProgressBar.create(
                daily_stats.get('calories', 0),
                goals.get('calories', 2000)
            )
            lines.append(f"└ 🔥 Калории: {cal_bar} <code>{cal_pct:.0f}%</code>")
        
        lines.extend([
            f"",
            f"{PremiumStyle.DIVIDER}",
            f"🎉 <i>Отличная работа! Так держать!</i>",
            f"{PremiumStyle.DIVIDER}"
        ])
        
        return '\n'.join(lines)
    
    @staticmethod
    def water_logged(
        amount: float,
        total: float,
        goal: float
    ) -> str:
        """Карточка записи воды"""
        percentage = min((total / goal) * 100, 100)
        
        # Мотивация в зависимости от прогресса
        if percentage >= 100:
            motivation = "🎉 <b>Цель достигнута!</b>"
            emoji = "🏆"
        elif percentage >= 75:
            motivation = "👍 <b>Отлично!</b> Осталось немного!"
            emoji = "💪"
        elif percentage >= 50:
            motivation = "👌 <b>Хорошо!</b> Продолжайте!"
            emoji = "💧"
        else:
            motivation = "💡 <b>Пейте больше воды!</b>"
            emoji = "⚠️"
        
        bar, _ = PremiumProgressBar.create(total, goal, style='modern')
        
        return f"""
{PremiumStyle.DIVIDER}
💧 <b>Вода записана!</b>
{PremiumStyle.DIVIDER}

🥤 <b>Выпито:</b> <code>{amount:.0f} мл</code>
📊 <b>За день:</b> <code>{total:.0f} мл</code>
🎯 <b>Цель:</b> <code>{goal:.0f} мл</code>

{bar} <code>{percentage:.0f}%</code>

{PremiumStyle.DIVIDER_DASH}
{emoji} {motivation}
{PremiumStyle.DIVIDER}
"""

    @staticmethod
    def weight_logged(
        weight: float,
        previous_weight: Optional[float] = None,
        goal: Optional[float] = None
    ) -> str:
        """Карточка записи веса"""
        lines = [
            f"{PremiumStyle.DIVIDER}",
            f"⚖️ <b>Вес записан!</b>",
            f"{PremiumStyle.DIVIDER}",
            f"",
            f"📊 <b>Текущий вес:</b> <code>{weight:.1f} кг</code>",
        ]
        
        if previous_weight:
            diff = weight - previous_weight
            if diff > 0:
                lines.append(f"📈 <b>Изменение:</b> <code>+{diff:.1f} кг</code> ⬆️")
            elif diff < 0:
                lines.append(f"📉 <b>Изменение:</b> <code>{diff:.1f} кг</code> ⬇️")
            else:
                lines.append(f"➡️ <b>Изменение:</b> <code>0.0 кг</code>")
        
        if goal:
            diff_to_goal = weight - goal
            if diff_to_goal > 0:
                lines.append(f"🎯 <b>До цели:</b> <code>{diff_to_goal:.1f} кг</code>")
            elif diff_to_goal < 0:
                lines.append(f"🎉 <b>Цель превышена!</b> <code>{abs(diff_to_goal):.1f} кг</code>")
            else:
                lines.append(f"🎉 <b>Цель достигнута!</b>")
        
        lines.extend([
            f"",
            f"{PremiumStyle.DIVIDER}",
            f"💡 <i>Взвешивайтесь регулярно для точной статистики!</i>",
            f"{PremiumStyle.DIVIDER}"
        ])
        
        return '\n'.join(lines)
    
    @staticmethod
    def activity_logged(
        activity_type: str,
        duration: int,
        calories: float,
        daily_stats: Dict = None
    ) -> str:
        """Карточка записи активности"""
        activity_emojis = {
            'running': '🏃',
            'walking': '🚶',
            'cycling': '🚴',
            'gym': '🏋️',
            'yoga': '🧘',
            'swimming': '🏊',
            'other': '🎾'
        }
        
        emoji = activity_emojis.get(activity_type, '🏃')
        
        lines = [
            f"{PremiumStyle.DIVIDER}",
            f"{emoji} <b>Активность записана!</b>",
            f"{PremiumStyle.DIVIDER}",
            f"",
            f"🏃 <b>Тип:</b> <code>{activity_type.title()}</code>",
            f"⏱️ <b>Длительность:</b> <code>{duration} мин</code>",
            f"🔥 <b>Сожжено:</b> <code>{calories:.0f} ккал</code>",
        ]
        
        if daily_stats:
            total_minutes = daily_stats.get('activity_minutes', 0)
            progress = min((total_minutes / 60) * 100, 100)
            bar, _ = PremiumProgressBar.create(total_minutes, 60)
            
            lines.extend([
                f"",
                f"{PremiumStyle.DIVIDER_DASH}",
                f"📊 <b>За сегодня:</b>",
                f"├ ⏱️ Минут: <code>{total_minutes}</code>",
                f"└ {bar} <code>{progress:.0f}%</code> (цель: 60 мин)",
            ])
        
        lines.extend([
            f"",
            f"{PremiumStyle.DIVIDER}",
            f"💪 <i>Продолжайте быть активным!</i>",
            f"{PremiumStyle.DIVIDER}"
        ])
        
        return '\n'.join(lines)
    
    @staticmethod
    def progress_summary(
        stats: Dict,
        goals: Dict,
        period: str = "сегодня"
    ) -> str:
        """Сводка прогресса"""
        period_emojis = {
            'сегодня': '📅',
            'неделю': '📆',
            'месяц': '🗓️',
            'всё время': '📊'
        }
        
        emoji = period_emojis.get(period, '📊')
        
        lines = [
            f"{PremiumStyle.DIVIDER}",
            f"{emoji} <b>Прогресс за {period}</b>",
            f"{PremiumStyle.DIVIDER}",
            f"",
            f"🍽️ <b>Питание:</b>",
        ]
        
        # Прогресс по калориям
        cal_bar, cal_pct = PremiumProgressBar.create(
            stats.get('calories', 0),
            goals.get('calories', 2000)
        )
        lines.append(f"└ 🔥 Калории: {cal_bar} <code>{cal_pct:.0f}%</code>")
        
        # Прогресс по воде
        water_bar, water_pct = PremiumProgressBar.create(
            stats.get('water', 0),
            goals.get('water', 2000)
        )
        lines.append(f"└ 💧 Вода: {water_bar} <code>{water_pct:.0f}%</code>")
        
        # Прогресс по активности
        activity_bar, activity_pct = PremiumProgressBar.create(
            stats.get('activity_minutes', 0),
            60
        )
        lines.append(f"└ 🏃 Активность: {activity_bar} <code>{activity_pct:.0f}%</code>")
        
        # Общая статистика
        lines.extend([
            f"",
            f"{PremiumStyle.DIVIDER_DASH}",
            f"📊 <b>Детали:</b>",
            f"├ 🍽️ Приемов пищи: <code>{stats.get('meals_count', 0)}</code>",
            f"├ 🥩 Белков: <code>{stats.get('protein', 0):.0f} г</code>",
            f"├ 🧈 Жиров: <code>{stats.get('fat', 0):.0f} г</code>",
            f"├ 🍞 Углеводов: <code>{stats.get('carbs', 0):.0f} г</code>",
            f"└ ⚖️ Вес: <code>{stats.get('weight', '—')} кг</code>",
        ])
        
        # Мотивация
        avg_progress = (cal_pct + water_pct + activity_pct) / 3
        if avg_progress >= 90:
            motivation = "🏆 <b>Великолепно!</b> Вы супергерой!"
        elif avg_progress >= 70:
            motivation = "💪 <b>Отлично!</b> Так держать!"
        elif avg_progress >= 50:
            motivation = "👍 <b>Хорошо!</b> Можно лучше!"
        else:
            motivation = "🎯 <b>Есть куда расти!</b> Не сдавайтесь!"
        
        lines.extend([
            f"",
            f"{PremiumStyle.DIVIDER}",
            f"{motivation}",
            f"{PremiumStyle.DIVIDER}"
        ])
        
        return '\n'.join(lines)
    
    @staticmethod
    def profile_card(user: Dict) -> str:
        """Карточка профиля"""
        gender_emoji = '👨' if user.get('gender') == 'male' else '👩'
        goal_emoji = {'weight_loss': '📉', 'gain': '📈', 'maintain': '⚖️'}.get(
            user.get('goal'), '🎯'
        )
        
        lines = [
            f"{PremiumStyle.DIVIDER}",
            f"👤 <b>Ваш профиль</b>",
            f"{PremiumStyle.DIVIDER}",
            f"",
            f"📊 <b>Основные данные:</b>",
            f"├ {gender_emoji} Пол: <code>{user.get('gender', '—')}</code>",
            f"├ 🎂 Возраст: <code>{user.get('age', '—')} лет</code>",
            f"├ 📏 Рост: <code>{user.get('height', '—')} см</code>",
            f"├ ⚖️ Вес: <code>{user.get('weight', '—')} кг</code>",
            f"└ {goal_emoji} Цель: <code>{user.get('goal', '—')}</code>",
            f"",
            f"🎯 <b>Цели на день:</b>",
            f"├ 🔥 Калории: <code>{user.get('daily_calorie_goal', '—')} ккал</code>",
            f"├ 🥩 Белки: <code>{user.get('daily_protein_goal', '—')} г</code>",
            f"├ 🧈 Жиры: <code>{user.get('daily_fat_goal', '—')} г</code>",
            f"├ 🍞 Углеводы: <code>{user.get('daily_carbs_goal', '—')} г</code>",
            f"└ 💧 Вода: <code>{user.get('daily_water_goal', '—')} мл</code>",
        ]
        
        if user.get('city'):
            lines.append(f"└ 🌍 Город: <code>{user.get('city')}</code>")
        
        lines.extend([
            f"",
            f"{PremiumStyle.DIVIDER}",
            f"💡 <i>Используйте /set_profile для редактирования</i>",
            f"{PremiumStyle.DIVIDER}"
        ])
        
        return '\n'.join(lines)
    
    @staticmethod
    def achievement_earned(
        name: str,
        description: str,
        icon: str = "🏆"
    ) -> str:
        """Уведомление о достижении"""
        return f"""
{PremiumStyle.DIVIDER}
{icon} <b>Новое достижение!</b> {icon}
{PremiumStyle.DIVIDER}

🏆 <b>{name}</b>

{description}

{PremiumStyle.DIVIDER_DOT}
🌟 <i>Поздравляем с достижением!</i>
{PremiumStyle.DIVIDER}
"""

    @staticmethod
    def help_message() -> str:
        """Справка"""
        return f"""
{PremiumStyle.DIVIDER}
📖 <b>Справка NutriBuddy</b>
{PremiumStyle.DIVIDER}

🎯 <b>Основные команды:</b>
├ /start — Запуск бота
├ /set_profile — Настройка профиля
├ /profile — Мой профиль
├ /food — Записать еду
├ /water — Записать воду
├ /weight — Записать вес
├ /activity — Активность
├ /progress — Прогресс
├ /stats — Статистика
├ /achievements — Достижения
├ /ask — AI ассистент
└ /help — Эта справка

📸 <b>Работа с фото:</b>
Просто отправьте фото еды — AI
распознает продукты и посчитает
калории автоматически!

💡 <b>Советы:</b>
├ Фотографируйте при хорошем свете
├ Заполняйте кадр блюдом
├ Указывайте вес для точности
└ Записывайте всё, что съели

{PremiumStyle.DIVIDER_DOT}
❓ <b>Остались вопросы?</b> Используйте /ask
{PremiumStyle.DIVIDER}
"""

    @staticmethod
    def error_message(
        message: str,
        suggestion: str = ""
    ) -> str:
        """Сообщение об ошибке"""
        lines = [
            f"{PremiumStyle.DIVIDER}",
            f"❌ <b>Ошибка</b>",
            f"{PremiumStyle.DIVIDER}",
            f"",
            f"⚠️ {message}",
        ]
        
        if suggestion:
            lines.extend([
                f"",
                f"💡 <b>Совет:</b> {suggestion}",
            ])
        
        lines.extend([
            f"",
            f"{PremiumStyle.DIVIDER}",
            f"🔧 <i>Попробуйте еще раз или обратитесь в поддержку</i>",
            f"{PremiumStyle.DIVIDER}"
        ])
        
        return '\n'.join(lines)
    
    @staticmethod
    def loading_message(action: str = "Обработка") -> str:
        """Сообщение о загрузке"""
        return f"""
{PremiumStyle.DIVIDER_DOT}
⏳ <b>{action}...</b>
⏳ Пожалуйста, подождите
{PremiumStyle.DIVIDER_DOT}
"""


# ═══════════════════════════════════════════════════════════════
# 🎯 МОТИВАТОРЫ
# ═══════════════════════════════════════════════════════════════

class Motivators:
    """Мотивационные сообщения"""
    
    MESSAGES = {
        'morning': [
            "☀️ Доброе утро! Новый день — новые возможности!",
            "🌅 Начинайте день с правильного завтрака!",
            "✨ Сегодня отличный день для здоровых привычек!",
        ],
        'meal': [
            "🍽️ Осознанное питание — путь к здоровью!",
            "💡 Помните: вы — то, что вы едите!",
            "🎯 Каждый прием пищи важен для цели!",
        ],
        'water': [
            "💧 Вода — источник жизни и энергии!",
            "🌊 Пейте воду до того, как почувствуете жажду!",
            "💦 Каждая капля приближает к цели!",
        ],
        'activity': [
            "🏃 Движение — это жизнь!",
            "💪 Каждая тренировка делает вас сильнее!",
            "🔥 Сжигайте калории, набирайтесь сил!",
        ],
        'progress': [
            "📈 Ваш прогресс впечатляет!",
            "🌟 Вы на правильном пути!",
            "🎯 Цель ближе, чем кажется!",
        ],
        'evening': [
            "🌙 Отличный день! Гордитесь собой!",
            "⭐ Завтра будет еще лучше!",
            "🌟 Отдыхайте — мышцы растут во сне!",
        ],
    }
    
    @staticmethod
    def get(category: str = 'general') -> str:
        """Получить мотивационное сообщение"""
        import random
        messages = Motivators.MESSAGES.get(category, ['🌟 Продолжайте в том же духе!'])
        return random.choice(messages)
    
    @staticmethod
    def by_progress(percentage: float, category: str = 'general') -> str:
        """Мотивация по прогрессу"""
        if percentage >= 95:
            return "🏆 <b>Великолепно!</b> Вы достигли цели!"
        elif percentage >= 80:
            return "💪 <b>Отлично!</b> Почти у цели!"
        elif percentage >= 60:
            return "👍 <b>Хорошо!</b> Продолжайте!"
        elif percentage >= 40:
            return "📈 <b>Неплохо!</b> Можно лучше!"
        elif percentage >= 20:
            return "🚀 <b>Начало положено!</b> Вперед!"
        else:
            return "🌟 <b>Главное — начать!</b> Вы сможете!"
