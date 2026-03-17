"""
Клавиатуры для выбора часового пояса пользователя
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.timezone_utils import POPULAR_CITIES, POPULAR_OFFSETS

def get_timezone_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора часового пояса
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с популярными городами
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем популярные города России
    builder.row(InlineKeyboardButton(text="🇷🇺 Калининград (UTC+2)", callback_data="tz_Europe/Kaliningrad"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Москва (UTC+3)", callback_data="tz_Europe/Moscow"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Мурманск (UTC+3)", callback_data="tz_Europe/Moscow"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Санкт-Петербург (UTC+3)", callback_data="tz_Europe/Moscow"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Волгоград (UTC+3)", callback_data="tz_Europe/Moscow"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Казань (UTC+3)", callback_data="tz_Europe/Moscow"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Нижний Новгород (UTC+3)", callback_data="tz_Europe/Moscow"))
    
    # Добавляем другие крупные города России
    builder.row(InlineKeyboardButton(text="🇷🇺 Самара (UTC+4)", callback_data="tz_Europe/Samara"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Екатеринбург (UTC+5)", callback_data="tz_Asia/Yekaterinburg"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Омск (UTC+6)", callback_data="tz_Asia/Omsk"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Красноярск (UTC+7)", callback_data="tz_Asia/Krasnoyarsk"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Иркутск (UTC+8)", callback_data="tz_Asia/Irkutsk"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Владивосток (UTC+10)", callback_data="tz_Asia/Vladivostok"))
    
    # Добавляем зарубежные города
    builder.row(InlineKeyboardButton(text="🇬🇧 Лондон (UTC+0)", callback_data="tz_Europe/London"))
    builder.row(InlineKeyboardButton(text="🇫🇷 Париж (UTC+1)", callback_data="tz_Europe/Paris"))
    builder.row(InlineKeyboardButton(text="🇩🇪 Берлин (UTC+1)", callback_data="tz_Europe/Berlin"))
    builder.row(InlineKeyboardButton(text="🇮🇹 Рим (UTC+1)", callback_data="tz_Europe/Rome"))
    builder.row(InlineKeyboardButton(text="🇺🇸 Нью-Йорк (UTC-5)", callback_data="tz_America/New_York"))
    builder.row(InlineKeyboardButton(text="🇯🇵 Токио (UTC+9)", callback_data="tz_Asia/Tokyo"))
    
    # Добавляем ручной ввод
    builder.row(InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="tz_manual_input"))
    
    return builder.as_markup()

def get_manual_timezone_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для ручного ввода смещения
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с популярными смещениями
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем популярные смещения
    for i in range(0, len(POPULAR_OFFSETS), 4):
        row_buttons = []
        for j in range(i, min(i + 4, len(POPULAR_OFFSETS))):
            offset = POPULAR_OFFSETS[j]
            row_buttons.append(InlineKeyboardButton(text=offset, callback_data=f"tz_{offset}"))
        builder.row(*row_buttons)
    
    # Кнопка "назад"
    builder.row(InlineKeyboardButton(text="🔙 Назад к городам", callback_data="tz_back_to_cities"))
    
    return builder.as_markup()

def get_timezone_confirm_keyboard(tz_name: str, display_name: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для подтверждения часового пояса
    
    Args:
        tz_name: IANA идентификатор часового пояса
        display_name: Отображаемое название
        
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text=f"✅ Да, это {display_name}", callback_data=f"tz_confirm_{tz_name}"))
    builder.row(InlineKeyboardButton(text="🔄 Выбрать другой", callback_data="tz_change"))
    
    return builder.as_markup()
