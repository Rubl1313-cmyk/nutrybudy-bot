"""
Локализованные команды для NutriBuddy Bot
"""
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F
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
    help_text = "[HELP] <b>Команды NutriBuddy Bot</b>\n\n"
    
    # Группируем команды по категориям
    categories = {
        "[PROFILE] Профиль и прогресс": ["профиль", "настроить_профиль", "прогресс", "достижения", "статистика"],
        "[FOOD] Питание": ["еда", "записать_еду", "вода", "записать_воду", "план", "диета"],
        "[FITNESS] Фитнес": ["вес", "записать_вес", "активность", "тренировка"],
        "[AI] AI и помощь": ["спросить", "помощник", "погода", "помощь", "старт"]
    }
    
    for category, commands in categories.items():
        help_text += f"{category}\n"
        for cmd in commands:
            if cmd in LOCALIZED_COMMANDS:
                help_text += f"/{cmd} - {LOCALIZED_COMMANDS[cmd]['description']}\n"
        help_text += "\n"
    
    help_text += "[INFO] <i>Также можно использовать английские версии команд!</i>"
    
    return help_text

def register_localized_handlers(router):
    """Регистрирует обработчики для локализованных команд"""
    
    for ru_cmd, cmd_info in LOCALIZED_COMMANDS.items():
        en_cmd = cmd_info["original"]
        
        # Создаем фильтр для обеих команд
        filter_obj = create_localized_command_filter(ru_cmd)
        
        if filter_obj:
            # Динамически создаем обработчик
            @router.message(filter_obj)
            async def handle_localized_command(message: Message, ru_cmd=ru_cmd, en_cmd=en_cmd):
                """Обработчик локализованной команды"""
                logger.info(f"[COMMAND] Получена локализованная команда: {message.text}")
                
                # Здесь можно добавить логику перенаправления на оригинальные обработчики
                # Например, можно изменить message.text на английскую команду и пропустить дальше
                
                # Временно просто отвечаем справкой
                await message.answer(
                    f"[COMMAND] Команда {message.text} принята!\n\n"
                    f"[INFO] Оригинальная команда: /{en_cmd}\n"
                    f"[INFO] Функционал в разработке..."
                )

def get_command_mapping() -> dict:
    """Возвращает маппинг русских команд на английские"""
    return {ru: info["original"] for ru, info in LOCALIZED_COMMANDS.items()}

def resolve_command(text: str) -> str:
    """Определяет оригинальную команду по локализованному тексту"""
    if not text or not text.startswith("/"):
        return text
    
    # Убираем слэш и параметры
    cmd = text.split()[0][1:].lower()
    
    # Ищем в маппинге
    for ru_cmd, en_cmd in get_command_mapping().items():
        if cmd == ru_cmd.lower():
            return f"/{en_cmd}"
    
    # Возвращаем как есть если не нашли
    return text

def is_localized_command(text: str) -> bool:
    """Проверяет, является ли текст локализованной командой"""
    if not text or not text.startswith("/"):
        return False
    
    cmd = text.split()[0][1:].lower()
    return cmd in LOCALIZED_COMMANDS

def get_all_commands() -> list:
    """Возвращает список всех локализованных команд"""
    return list(LOCALIZED_COMMANDS.keys())

def get_command_info(command: str) -> dict:
    """Возвращает информацию о команде"""
    return LOCALIZED_COMMANDS.get(command, {})

def create_command_keyboard():
    """Создает клавиатуру с основными командами"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    # Основные команды
    main_commands = [
        ["Профиль", "Прогресс"],
        ["Записать еду", "Записать воду"],
        ["Спросить AI", "Помощь"]
    ]
    
    keyboard = []
    for row in main_commands:
        keyboard.append([KeyboardButton(text=cmd) for cmd in row])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите команду или введите текст..."
    )

# Декоратор для локализованных команд
def localized_command(russian_command: str):
    """Декоратор для создания обработчиков локализованных команд"""
    def decorator(func):
        filter_obj = create_localized_command_filter(russian_command)
        if filter_obj:
            return router.message(filter_obj)(func)
        return func
    return decorator

# Утилиты для работы с командами
class CommandUtils:
    """Утилиты для работы с локализованными командами"""
    
    @staticmethod
    def extract_command_args(text: str) -> tuple:
        """Извлекает команду и аргументы из текста"""
        if not text:
            return None, None
        
        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        return command, args
    
    @staticmethod
    def format_command_help(command: str) -> str:
        """Форматирует справку для команды"""
        info = get_command_info(command)
        if not info:
            return f"[ERROR] Команда /{command} не найдена"
        
        return (
            f"[COMMAND] /{command}\n"
            f"[DESCRIPTION] {info['description']}\n"
            f"[ALIAS] Также доступна как /{info['original']}"
        )
    
    @staticmethod
    def validate_command(text: str) -> bool:
        """Валидирует команду"""
        if not text or not text.startswith("/"):
            return False
        
        cmd = text.split()[0][1:].lower()
        return cmd in LOCALIZED_COMMANDS or cmd in [info["original"] for info in LOCALIZED_COMMANDS.values()]
