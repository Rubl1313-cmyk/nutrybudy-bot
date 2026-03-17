"""
Ğ›Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹ Ğ´Ğ»Ñ� NutriBuddy Bot
"""
from aiogram.filters import Command
from aiogram.types import Message
from typing import Dict, Callable
import logging

logger = logging.getLogger(__name__)

# Ğ¡Ğ»Ğ¾Ğ²Ğ°Ñ€ÑŒ Ğ»Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ñ… ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´
LOCALIZED_COMMANDS = {
    # Ğ ÑƒÑ�Ñ�ĞºĞ¸Ğµ Ğ°Ğ»Ğ¸Ğ°Ñ�Ñ‹ Ğ´Ğ»Ñ� Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ñ… ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´
    "Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�": {
        "original": "achievements",
        "description": "ĞŸĞ¾ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ� Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�"
    },
    "Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�": {
        "original": "progress", 
        "description": "ĞŸĞ¾ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºÑƒ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°"
    },
    "Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ": {
        "original": "profile",
        "description": "ĞŸĞ¾ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"
    },
    "Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¸Ñ‚ÑŒ_Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ": {
        "original": "set_profile",
        "description": "Ğ�Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¸Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ"
    },
    "Ğ²Ğ¾Ğ´Ğ°": {
        "original": "water",
        "description": "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ"
    },
    "Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ_Ğ²Ğ¾Ğ´Ñƒ": {
        "original": "log_water", 
        "description": "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ"
    },
    "ĞµĞ´Ğ°": {
        "original": "log_food",
        "description": "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¸ĞµĞ¼ Ğ¿Ğ¸Ñ‰Ğ¸"
    },
    "Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ_ĞµĞ´Ñƒ": {
        "original": "log_food",
        "description": "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¸ĞµĞ¼ Ğ¿Ğ¸Ñ‰Ğ¸"
    },
    "Ğ²ĞµÑ�": {
        "original": "weight",
        "description": "ĞŸĞ¾ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ğ²ĞµÑ�"
    },
    "Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ_Ğ²ĞµÑ�": {
        "original": "log_weight",
        "description": "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ²ĞµÑ�"
    },
    "Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ": {
        "original": "fitness",
        "description": "Ğ¤Ğ¸Ñ‚Ğ½ĞµÑ� Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ"
    },
    "Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°": {
        "original": "activity",
        "description": "Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºÑƒ"
    },
    "Ğ¿Ğ»Ğ°Ğ½": {
        "original": "meal_plan",
        "description": "ĞŸĞ»Ğ°Ğ½ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�"
    },
    "Ğ´Ğ¸ĞµÑ‚Ğ°": {
        "original": "diet",
        "description": "Ğ”Ğ¸ĞµÑ‚Ğ° Ğ¸ Ğ¿Ğ»Ğ°Ğ½"
    },
    "Ñ�Ğ¿Ñ€Ğ¾Ñ�Ğ¸Ñ‚ÑŒ": {
        "original": "ask",
        "description": "Ğ—Ğ°Ğ´Ğ°Ñ‚ÑŒ Ğ²Ğ¾Ğ¿Ñ€Ğ¾Ñ� AI"
    },
    "Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ½Ğ¸Ğº": {
        "original": "ai",
        "description": "AI Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ½Ğ¸Ğº"
    },
    "Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ğ°": {
        "original": "weather",
        "description": "ĞŸĞ¾Ğ³Ğ¾Ğ´Ğ°"
    },
    "Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ°": {
        "original": "stats",
        "description": "Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ°"
    },
    "Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰ÑŒ": {
        "original": "help",
        "description": "ĞŸĞ¾Ğ¼Ğ¾Ñ‰ÑŒ"
    },
    "Ñ�Ñ‚Ğ°Ñ€Ñ‚": {
        "original": "start",
        "description": "Ğ�Ğ°Ñ‡Ğ°Ñ‚ÑŒ"
    }
}

class LocalizedCommand:
    """Ğ›Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ°Ñ� ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ°"""
    
    def __init__(self, russian_command: str, original_command: str, description: str):
        self.russian = russian_command
        self.original = original_command
        self.description = description
    
    def __str__(self):
        return f"/{self.russian} (/{self.original})"
    
    def get_help_text(self) -> str:
        return f"/{self.russian} - {self.description}"

def create_localized_command_filter(russian_command: str):
    """Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµÑ‚ Ñ„Ğ¸Ğ»ÑŒÑ‚Ñ€ Ğ´Ğ»Ñ� Ğ»Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ¾Ğ¹ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹"""
    original_command = LOCALIZED_COMMANDS.get(russian_command, {}).get("original")
    if not original_command:
        return None
    
    # Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµĞ¼ Ñ„Ğ¸Ğ»ÑŒÑ‚Ñ€, ĞºĞ¾Ñ‚Ğ¾Ñ€Ñ‹Ğ¹ Ñ€ĞµĞ°Ğ³Ğ¸Ñ€ÑƒĞµÑ‚ Ğ½Ğ° Ğ¾Ğ±Ğµ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹
    class LocalizedCommandFilter:
        def __init__(self, ru_cmd: str, en_cmd: str):
            self.ru_cmd = ru_cmd
            self.en_cmd = en_cmd
        
        async def __call__(self, message: Message) -> bool:
            text = message.text or message.caption
            if not text:
                return False
            
            # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ¾Ğ±Ğ° Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ°
            return (text.startswith(f"/{self.ru_cmd}") or 
                   text.startswith(f"/{self.en_cmd}"))
    
    return LocalizedCommandFilter(russian_command, original_command)

def get_localized_help() -> str:
    """Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ Ñ�Ğ¿Ñ€Ğ°Ğ²ĞºÑƒ Ñ� Ğ»Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¼Ğ¸ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ğ°Ğ¼Ğ¸"""
    help_text = "ğŸŒŸ <b>ĞšĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹ NutriBuddy Bot</b>\n\n"
    
    # Ğ“Ñ€ÑƒĞ¿Ğ¿Ğ¸Ñ€ÑƒĞµĞ¼ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹ Ğ¿Ğ¾ ĞºĞ°Ñ‚ĞµĞ³Ğ¾Ñ€Ğ¸Ñ�Ğ¼
    categories = {
        "ğŸ“Š ĞŸÑ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�": ["Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ", "Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¸Ñ‚ÑŒ_Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ", "Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�", "Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�", "Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ°"],
        "ğŸ�½ï¸� ĞŸĞ¸Ñ‚Ğ°Ğ½Ğ¸Ğµ": ["ĞµĞ´Ğ°", "Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ_ĞµĞ´Ñƒ", "Ğ²Ğ¾Ğ´Ğ°", "Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ_Ğ²Ğ¾Ğ´Ñƒ", "Ğ¿Ğ»Ğ°Ğ½", "Ğ´Ğ¸ĞµÑ‚Ğ°"],
        "ğŸ’ª Ğ¤Ğ¸Ñ‚Ğ½ĞµÑ�": ["Ğ²ĞµÑ�", "Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ_Ğ²ĞµÑ�", "Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ", "Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°"],
        "ğŸ¤– AI Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ½Ğ¸Ğº": ["Ñ�Ğ¿Ñ€Ğ¾Ñ�Ğ¸Ñ‚ÑŒ", "Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰Ğ½Ğ¸Ğº", "Ğ¿Ğ¾Ğ³Ğ¾Ğ´Ğ°"],
        "ğŸ”§ Ğ�Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ğµ": ["Ñ�Ñ‚Ğ°Ñ€Ñ‚", "Ğ¿Ğ¾Ğ¼Ğ¾Ñ‰ÑŒ"]
    }
    
    for category, commands in categories.items():
        help_text += f"{category}\n"
        for cmd in commands:
            if cmd in LOCALIZED_COMMANDS:
                help_text += f"  {LocalizedCommand(cmd, LOCALIZED_COMMANDS[cmd]['original'], LOCALIZED_COMMANDS[cmd]['description']).get_help_text()}\n"
        help_text += "\n"
    
    help_text += "ğŸ’¡ <i>ĞœĞ¾Ğ¶Ğ½Ğ¾ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ÑŒ ĞºĞ°Ğº Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğµ, Ñ‚Ğ°Ğº Ğ¸ Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğµ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹!</i>"
    
    return help_text

def get_command_mapping() -> Dict[str, str]:
    """Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ Ğ¼Ğ°Ğ¿Ğ¿Ğ¸Ğ½Ğ³ Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ñ… ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´ Ğ½Ğ° Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¸Ğµ"""
    return {cmd: info["original"] for cmd, info in LOCALIZED_COMMANDS.items()}

def get_all_localized_commands() -> Dict[str, LocalizedCommand]:
    """Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµÑ‚ Ğ²Ñ�Ğµ Ğ»Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñ‹"""
    return {
        cmd: LocalizedCommand(cmd, info["original"], info["description"])
        for cmd, info in LOCALIZED_COMMANDS.items()
    }

# Ğ”ĞµĞºĞ¾Ñ€Ğ°Ñ‚Ğ¾Ñ€ Ğ´Ğ»Ñ� Ğ»Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ñ… ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´
def localized_command(russian_command: str):
    """Ğ”ĞµĞºĞ¾Ñ€Ğ°Ñ‚Ğ¾Ñ€ Ğ´Ğ»Ñ� Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸ĞºĞ¾Ğ² Ğ»Ğ¾ĞºĞ°Ğ»Ğ¸Ğ·Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ñ… ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´"""
    def decorator(func: Callable):
        original_command = LOCALIZED_COMMANDS.get(russian_command, {}).get("original")
        if not original_command:
            logger.warning(f"No original command found for {russian_command}")
            return func
        
        # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ°Ñ‚Ñ€Ğ¸Ğ±ÑƒÑ‚Ñ‹ Ğ´Ğ»Ñ� Ñ€ĞµĞ³Ğ¸Ñ�Ñ‚Ñ€Ğ°Ñ†Ğ¸Ğ¸
        func.localized_commands = [russian_command, original_command]
        func.command_filter = create_localized_command_filter(russian_command)
        
        return func
    return decorator
