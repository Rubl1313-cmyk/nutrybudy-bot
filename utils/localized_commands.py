"""
Локализованные команды для NutriBuddy Bot
"""
from aiogram.filters import Command
from aiogram.types import Message
from typing import Dict, Callable
import logging

logger = logging.getLogger(__name__)

# Словарь локализованных команд
LOCALIZED_COMMANDS = {
    # Русские алиасы для английских команд
    "достижения": {
        "original": "achievements",
        "description": "Показать достижения и прогресс"
    },
    "прогресс": {
        "original": "progress", 
        "description": "Показать статистику прогресса"
    },
    "профиль": {
        "original": "profile",
        "description": "Показать профиль"
    },
    "настроить_профиль": {
        "original": "set_profile",
        "description": "Настроить профиль"
    },
    "вода": {
        "original": "water",
        "description": "Записать воду"
    },
    "записать_воду": {
        "original": "log_water", 
        "description": "Записать воду"
    },
    "еда": {
        "original": "log_food",
        "description": "Записать прием пищи"
    },
    "записать_еду": {
        "original": "log_food",
        "description": "Записать прием пищи"
    },
    "вес": {
        "original": "weight",
        "description": "Показать вес"
    },
    "записать_вес": {
        "original": "log_weight",
        "description": "Записать вес"
    },
    "активность": {
        "original": "fitness",
        "description": "Фитнес и активность"
    },
    "тренировка": {
        "original": "activity",
        "description": "Записать тренировку"
    },
    "план": {
        "original": "meal_plan",
        "description": "План питания"
    },
    "диета": {
        "original": "diet",
        "description": "Диета и план"
    },
    "спросить": {
        "original": "ask",
        "description": "Задать вопрос AI"
    },
    "помощник": {
        "original": "ai",
        "description": "AI помощник"
    },
    "погода": {
        "original": "weather",
        "description": "Погода"
    },
    "статистика": {
        "original": "stats",
        "description": "Статистика"
    },
    "помощь": {
        "original": "help",
        "description": "Помощь"
    },
    "старт": {
        "original": "start",
        "description": "Начать"
    }
}

class LocalizedCommand:
    """Локализованная команда"""
    
    def __init__(self, russian_command: str, original_command: str, description: str):
        self.russian = russian_command
        self.original = original_command
        self.description = description
    
    def __str__(self):
        return f"/{self.russian} (/{self.original})"
    
    def get_help_text(self) -> str:
        return f"/{self.russian} - {self.description}"

def create_localized_command_filter(russian_command: str):
    """Создает фильтр для локализованной команды"""
    original_command = LOCALIZED_COMMANDS.get(russian_command, {}).get("original")
    if not original_command:
        return None
    
    # Создаем фильтр, который реагирует на обе команды
    class LocalizedCommandFilter:
        def __init__(self, ru_cmd: str, en_cmd: str):
            self.ru_cmd = ru_cmd
            self.en_cmd = en_cmd
        
        async def __call__(self, message: Message) -> bool:
            text = message.text or message.caption
            if not text:
                return False
            
            # Проверяем оба варианта
            return (text.startswith(f"/{self.ru_cmd}") or 
                   text.startswith(f"/{self.en_cmd}"))
    
    return LocalizedCommandFilter(russian_command, original_command)

def get_localized_help() -> str:
    """Возвращает справку с локализованными командами"""
    help_text = "🌟 <b>Команды NutriBuddy Bot</b>\n\n"
    
    # Группируем команды по категориям
    categories = {
        "📊 Профиль и прогресс": ["профиль", "настроить_профиль", "прогресс", "достижения", "статистика"],
        "🍽️ Питание": ["еда", "записать_еду", "вода", "записать_воду", "план", "диета"],
        "💪 Фитнес": ["вес", "записать_вес", "активность", "тренировка"],
        "🤖 AI помощник": ["спросить", "помощник", "погода"],
        "🔧 Основные": ["старт", "помощь"]
    }
    
    for category, commands in categories.items():
        help_text += f"{category}\n"
        for cmd in commands:
            if cmd in LOCALIZED_COMMANDS:
                help_text += f"  {LocalizedCommand(cmd, LOCALIZED_COMMANDS[cmd]['original'], LOCALIZED_COMMANDS[cmd]['description']).get_help_text()}\n"
        help_text += "\n"
    
    help_text += "💡 <i>Можно использовать как русские, так и английские команды!</i>"
    
    return help_text

def get_command_mapping() -> Dict[str, str]:
    """Возвращает маппинг русских команд на английские"""
    return {cmd: info["original"] for cmd, info in LOCALIZED_COMMANDS.items()}

def get_all_localized_commands() -> Dict[str, LocalizedCommand]:
    """Возвращает все локализованные команды"""
    return {
        cmd: LocalizedCommand(cmd, info["original"], info["description"])
        for cmd, info in LOCALIZED_COMMANDS.items()
    }

# Декоратор для локализованных команд
def localized_command(russian_command: str):
    """Декоратор для обработчиков локализованных команд"""
    def decorator(func: Callable):
        original_command = LOCALIZED_COMMANDS.get(russian_command, {}).get("original")
        if not original_command:
            logger.warning(f"No original command found for {russian_command}")
            return func
        
        # Добавляем атрибуты для регистрации
        func.localized_commands = [russian_command, original_command]
        func.command_filter = create_localized_command_filter(russian_command)
        
        return func
    return decorator
