"""
🎨 Анимация и визуальные эффекты для NutriBuddy Bot
✨ Современные анимированные прогресс-бары и эффекты
🚀 Динамические индикаторы и переходы
"""

import asyncio
from typing import List, Dict
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

class AnimationEngine:
    """🎬 Движок анимации для бота"""
    
    # Анимационные последовательности
    LOADING_FRAMES = [
        "⏳ Загрузка...",
        "🔄 Обработка...",
        "⚡ Анализ...",
        "🧠 Распознавание...",
        "✨ Почти готово...",
        "🎉 Готово!"
    ]
    
    PROGRESS_FRAMES = [
        "⚡", "✨", "🌟", "💫", "⭐", "🌠"
    ]
    
    WATER_FRAMES = [
        "💧", "💧💧", "💧💧💧", "💧💧💧💧", "💧💧💧💧💧"
    ]
    
    SUCCESS_FRAMES = [
        "🎯", "🏆", "✨", "🎉", "🌟"
    ]
    
    @staticmethod
    async def animate_loading(message: Message, frames: List[str] = None, 
                           delay: float = 0.5, iterations: int = 1) -> None:
        """
        🎬 Анимированная загрузка
        
        Args:
            message: сообщение для анимации
            frames: кадры анимации
            delay: задержка между кадрами
            iterations: количество повторений
        """
        if frames is None:
            frames = AnimationEngine.LOADING_FRAMES
        
        for _ in range(iterations):
            for frame in frames:
                try:
                    await message.edit_text(frame)
                    await asyncio.sleep(delay)
                except:
                    break
    
    @staticmethod
    def get_animated_progress_bar(current: float, total: float, 
                                style: str = 'pulse') -> str:
        """
        🌈 Анимированный прогресс-бар
        
        Args:
            current: текущее значение
            total: максимальное значение
            style: 'pulse', 'wave', 'gradient'
        """
        percentage = min((current / total) * 100, 100) if total > 0 else 0
        
        if style == 'pulse':
            # Пульсирующий эффект
            pulse_chars = ['🟢', '💚', '🟢', '⚡']
            filled = int(percentage / 10)
            bar = ''
            for i in range(10):
                if i < filled:
                    bar += pulse_chars[i % len(pulse_chars)]
                else:
                    bar += '⬜'
            return f"{bar} {percentage:.0f}%"
        
        elif style == 'wave':
            # Волновой эффект
            wave_chars = ['🔵', '🟦', '🟩', '🟨', '🟧']
            filled = int(percentage / 10)
            bar = ''
            for i in range(10):
                if i < filled:
                    bar += wave_chars[i % len(wave_chars)]
                else:
                    bar += '⬛'
            return f"{bar} {percentage:.0f}%"
        
        else:  # gradient
            # Градиентный эффект
            if percentage >= 80:
                bar = '🟢' * filled + '⬜' * (10 - filled)
            elif percentage >= 60:
                bar = '🔵' * filled + '⬜' * (10 - filled)
            elif percentage >= 40:
                bar = '🟡' * filled + '⬜' * (10 - filled)
            else:
                bar = '🔴' * filled + '⬜' * (10 - filled)
            return f"{bar} {percentage:.0f}%"
    
    @staticmethod
    def get_animated_water_level(current_ml: int, goal_ml: int = 2000) -> str:
        """
        💧 Анимированный уровень воды
        """
        percentage = min((current_ml / goal_ml) * 100, 100)
        
        # Бутылка с анимацией
        bottle_levels = [
            "💧",      # 0-20%
            "💧💧",    # 20-40%
            "💧💧💧",  # 40-60%
            "💧💧💧💧", # 60-80%
            "💧💧💧💧💧" # 80-100%
        ]
        
        level_index = min(int(percentage / 20), 4)
        water_drops = bottle_levels[level_index]
        
        return f"{water_drops} {current_ml}/{goal_ml}мл ({percentage:.0f}%)"
    
    @staticmethod
    def get_animated_streak(days: int) -> str:
        """
        🔥 Анимированная серия дней
        """
        if days == 0:
            return "🌱 Начните свою серию!"
        
        # Эффект огня для серии
        flame_effects = ["🔥", "🔥🔥", "🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"]
        
        if days >= 30:
            flames = "🔥🔥🔥🔥🔥"
            status = "🏆 Легенда!"
        elif days >= 14:
            flames = "🔥🔥🔥🔥"
            status = "🌟 На вершине!"
        elif days >= 7:
            flames = "🔥🔥🔥"
            status = "💪 Отлично!"
        elif days >= 3:
            flames = "🔥🔥"
            status = "👍 Хорошо!"
        else:
            flames = "🔥"
            status = "🚀 Начало!"
        
        return f"{flames} <b>{days} дней подряд!</b> {status}"

class VisualEffects:
    """✨ Визуальные эффекты для сообщений"""
    
    @staticmethod
    def create_typing_effect(text: str, delay: float = 0.1) -> List[str]:
        """
        ⌨️ Эффект печатания
        
        Returns:
            список кадров для анимации печатания
        """
        frames = []
        for i in range(1, len(text) + 1):
            frames.append(text[:i] + "▫️")
        frames.append(text)  # Финальный кадр без курсора
        return frames
    
    @staticmethod
    def create_countdown_effect(seconds: int) -> List[str]:
        """
        ⏱️ Эффект обратного отсчета
        
        Returns:
            список кадров для обратного отсчета
        """
        frames = []
        for i in range(seconds, 0, -1):
            frames.append(f"⏱️ {i}...")
        frames.append("🎯 Время!")
        return frames
    
    @staticmethod
    def create_celebration_effect() -> List[str]:
        """
        🎉 Эффект празднования
        
        Returns:
            список кадров для анимации празднования
        """
        return [
            "✨",
            "✨🎉",
            "✨🎉🎊",
            "✨🎉🎊🏆",
            "✨🎉🎊🏆🌟",
            "🎉🎊🏆🌟💫",
            "🎊🏆🌟💫⭐",
            "🏆🌟💫⭐🎯"
        ]
    
    @staticmethod
    def get_mood_emoji(percentage: float) -> str:
        """
        😊 Эмодзи настроения на основе процента
        
        Args:
            percentage: процент выполнения цели
        """
        if percentage >= 100:
            return "🎉"
        elif percentage >= 90:
            return "🎯"
        elif percentage >= 75:
            return "😊"
        elif percentage >= 50:
            return "🙂"
        elif percentage >= 25:
            return "😐"
        else:
            return "💪"
    
    @staticmethod
    def create_progress_chart(data: Dict[str, float], max_width: int = 20) -> str:
        """
        📊 Создание текстового графика прогресса
        
        Args:
            data: словарь с данными {'label': value}
            max_width: максимальная ширина графика
        """
        if not data:
            return "📊 Нет данных"
        
        max_value = max(data.values()) if data.values() else 1
        chart_lines = ["📊 <b>График прогресса</b>", "─" * 30]
        
        for label, value in data.items():
            # Рассчитываем ширину бара
            bar_width = int((value / max_value) * max_width)
            
            # Выбираем эмодзи для значения
            if value >= max_value * 0.9:
                bar_char = "🟢"
            elif value >= max_value * 0.7:
                bar_char = "🟡"
            elif value >= max_value * 0.5:
                bar_char = "🟠"
            else:
                bar_char = "🔴"
            
            bar = bar_char * bar_width
            chart_lines.append(f"{label:10} {bar} {value:.0f}")
        
        return "\n".join(chart_lines)

class InteractiveAnimations:
    """🎮 Интерактивные анимации"""
    
    @staticmethod
    def create_animated_keyboard(options: List[str], callback_prefix: str) -> InlineKeyboardBuilder:
        """
        🎨 Создание анимированной клавиатуры
        
        Args:
            options: список опций
            callback_prefix: префикс для callback_data
        """
        builder = InlineKeyboardBuilder()
        
        # Добавляем эмодзи к опциям
        emoji_map = {
            "да": "✅",
            "нет": "❌", 
            "далее": "➡️",
            "назад": "⬅️",
            "отмена": "❌",
            "сохранить": "💾",
            "удалить": "🗑️"
        }
        
        for option in options:
            lower_option = option.lower()
            emoji = emoji_map.get(lower_option, "🎯")
            builder.button(
                text=f"{emoji} {option}",
                callback_data=f"{callback_prefix}_{option}"
            )
        
        builder.adjust(1)
        return builder
    
    @staticmethod
    async def show_typing_animation(message: Message, text: str, 
                                   delay: float = 0.05) -> None:
        """
        ⌨️ Показать анимацию печатания
        """
        frames = VisualEffects.create_typing_effect(text, delay)
        
        for frame in frames[:-1]:  # Все кадры кроме последнего
            try:
                await message.edit_text(frame)
                await asyncio.sleep(delay)
            except:
                break
        
        # Финальный кадр
        try:
            await message.edit_text(frames[-1])
        except:
            pass

# Утилиты для анимации
class AnimationUtils:
    """🛠️ Утилиты для работы с анимациями"""
    
    @staticmethod
    def get_time_based_emoji() -> str:
        """
        🕐 Эмодзи на основе времени
        """
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "🌅"  # Утро
        elif 12 <= hour < 17:
            return "☀️"  # День
        elif 17 <= hour < 21:
            return "🌆"  # Вечер
        else:
            return "🌙"  # Ночь
    
    @staticmethod
    def get_seasonal_emoji() -> str:
        """
        🌸 Сезонные эмодзи
        """
        month = datetime.now().month
        
        if month in [12, 1, 2]:
            return "❄️"  # Зима
        elif month in [3, 4, 5]:
            return "🌸"  # Весна
        elif month in [6, 7, 8]:
            return "☀️"  # Лето
        else:
            return "🍂"  # Осень
    
    @staticmethod
    def create_motivational_quote(progress: float) -> str:
        """
        💬 Мотивационная цитата на основе прогресса
        """
        quotes = {
            (0, 25): "🌱 Каждое путешествие начинается с первого шага!",
            (26, 50): "💪 Вы на правильном пути! Продолжайте!",
            (51, 75): "🔥 Отличный прогресс! Вы почти у цели!",
            (76, 99): "_target Почти готово! Финальный рывок!",
            (100, 150): "🏆 Цель достигнута! Вы легенда!"
        }
        
        for (low, high), quote in quotes.items():
            if low <= progress <= high:
                return quote
        
        return "🚀 Продолжайте двигаться вперёд!"
