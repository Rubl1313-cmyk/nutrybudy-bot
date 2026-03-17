"""
Ğ£Ñ‚Ğ¸Ğ»Ğ¸Ñ‚Ñ‹ Ğ´Ğ»Ñ� Ğ±ĞµĞ·Ğ¾Ğ¿Ğ°Ñ�Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ° Ñ‡Ğ¸Ñ�ĞµĞ» Ğ¸Ğ· Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒÑ�ĞºĞ¾Ğ³Ğ¾ Ğ²Ğ²Ğ¾Ğ´Ğ°
"""
import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def safe_parse_float(text: str, field_name: str = "Ñ‡Ğ¸Ñ�Ğ»Ğ¾") -> Tuple[Optional[float], Optional[str]]:
    """
    Ğ‘ĞµĞ·Ğ¾Ğ¿Ğ°Ñ�Ğ½Ğ¾ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ñ‚ float Ğ¸Ğ· Ñ‚ĞµĞºÑ�Ñ‚Ğ° Ñ� Ñ€Ğ°Ñ�ÑˆĞ¸Ñ€ĞµĞ½Ğ½Ğ¾Ğ¹ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ¾Ğ¹ Ğ¾ÑˆĞ¸Ğ±Ğ¾Ğº
    
    Args:
        text: Ğ¢ĞµĞºÑ�Ñ‚ Ğ´Ğ»Ñ� Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ°
        field_name: Ğ�Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿Ğ¾Ğ»Ñ� Ğ´Ğ»Ñ� Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğ¹ Ğ¾Ğ± Ğ¾ÑˆĞ¸Ğ±ĞºĞ°Ñ…
        
    Returns:
        Tuple[Optional[float], Optional[str]]: (Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ, Ğ¾ÑˆĞ¸Ğ±ĞºĞ°)
    """
    if not text or not isinstance(text, str):
        return None, f"Ğ¢ĞµĞºÑ�Ñ‚ Ğ´Ğ»Ñ� {field_name} Ğ¾Ñ‚Ñ�ÑƒÑ‚Ñ�Ñ‚Ğ²ÑƒĞµÑ‚ Ğ¸Ğ»Ğ¸ Ğ½ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚ĞµĞ½"
    
    try:
        # Ğ£Ğ±Ğ¸Ñ€Ğ°ĞµĞ¼ Ğ¿Ñ€Ğ¾Ğ±ĞµĞ»Ñ‹ Ğ¸ Ğ·Ğ°Ğ¼ĞµĞ½Ñ�ĞµĞ¼ Ğ·Ğ°Ğ¿Ñ�Ñ‚Ñ‹Ğµ Ğ½Ğ° Ñ‚Ğ¾Ñ‡ĞºĞ¸
        clean_text = text.strip().replace(',', '.')
        
        # Ğ˜Ñ‰ĞµĞ¼ Ñ‡Ğ¸Ñ�Ğ»Ğ° Ğ² Ñ‚ĞµĞºÑ�Ñ‚Ğµ
        number_match = re.search(r'[-+]?\d*\.?\d+', clean_text)
        
        if not number_match:
            return None, f"Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ½Ğ°Ğ¹Ñ‚Ğ¸ {field_name} Ğ² Ñ‚ĞµĞºÑ�Ñ‚Ğµ"
        
        number_str = number_match.group()
        value = float(number_str)
        
        # ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼ Ğ½Ğ° Ğ²Ğ°Ğ»Ğ¸Ğ´Ğ½Ñ‹Ğµ Ğ´Ğ¸Ğ°Ğ¿Ğ°Ğ·Ğ¾Ğ½Ñ‹ Ğ´Ğ»Ñ� Ñ€Ğ°Ğ·Ğ½Ñ‹Ñ… Ñ‚Ğ¸Ğ¿Ğ¾Ğ² Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
        if field_name == "Ğ²ĞµÑ�" and not (30 <= value <= 300):
            return None, f"Ğ’ĞµÑ� Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ¾Ñ‚ 30 Ğ´Ğ¾ 300 ĞºĞ³"
        
        if field_name == "Ñ€Ğ¾Ñ�Ñ‚" and not (100 <= value <= 250):
            return None, f"Ğ Ğ¾Ñ�Ñ‚ Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ¾Ñ‚ 100 Ğ´Ğ¾ 250 Ñ�Ğ¼"
        
        if field_name == "Ğ²Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚" and not (10 <= value <= 120):
            return None, f"Ğ’Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚ Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ¾Ñ‚ 10 Ğ´Ğ¾ 120 Ğ»ĞµÑ‚"
        
        if field_name in ["ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸", "Ğ±ĞµĞ»ĞºĞ¸", "Ğ¶Ğ¸Ñ€Ñ‹", "ÑƒĞ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹"] and value < 0:
            return None, f"{field_name.capitalize()} Ğ½Ğµ Ğ¼Ğ¾Ğ³ÑƒÑ‚ Ğ±Ñ‹Ñ‚ÑŒ Ğ¾Ñ‚Ñ€Ğ¸Ñ†Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğ¼Ğ¸"
        
        if field_name == "Ñ‚ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ğ°" and not (-50 <= value <= 60):
            return None, f"Ğ¢ĞµĞ¼Ğ¿ĞµÑ€Ğ°Ñ‚ÑƒÑ€Ğ° Ğ´Ğ¾Ğ»Ğ¶Ğ½Ğ° Ğ±Ñ‹Ñ‚ÑŒ Ğ¾Ñ‚ -50Â°C Ğ´Ğ¾ 60Â°C"
        
        return value, None
        
    except ValueError as e:
        return None, f"Ğ�ĞµĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ñ‹Ğ¹ Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚ {field_name}: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error parsing {field_name} from '{text}': {e}")
        return None, f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞµ {field_name}"

def safe_parse_int(text: str, field_name: str = "Ñ‡Ğ¸Ñ�Ğ»Ğ¾") -> Tuple[Optional[int], Optional[str]]:
    """
    Ğ‘ĞµĞ·Ğ¾Ğ¿Ğ°Ñ�Ğ½Ğ¾ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ñ‚ int Ğ¸Ğ· Ñ‚ĞµĞºÑ�Ñ‚Ğ°
    
    Args:
        text: Ğ¢ĞµĞºÑ�Ñ‚ Ğ´Ğ»Ñ� Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ°
        field_name: Ğ�Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿Ğ¾Ğ»Ñ� Ğ´Ğ»Ñ� Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğ¹ Ğ¾Ğ± Ğ¾ÑˆĞ¸Ğ±ĞºĞ°Ñ…
        
    Returns:
        Tuple[Optional[int], Optional[str]]: (Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ, Ğ¾ÑˆĞ¸Ğ±ĞºĞ°)
    """
    value, error = safe_parse_float(text, field_name)
    if error:
        return None, error
    
    try:
        return int(value), None
    except (ValueError, TypeError):
        return None, f"Ğ—Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ Ğ´Ğ¾Ğ»Ğ¶Ğ½Ğ¾ Ğ±Ñ‹Ñ‚ÑŒ Ñ†ĞµĞ»Ñ‹Ğ¼ Ñ‡Ğ¸Ñ�Ğ»Ğ¾Ğ¼"

def extract_multiple_numbers(text: str, max_count: int = 5) -> list:
    """
    Ğ˜Ğ·Ğ²Ğ»ĞµĞºĞ°ĞµÑ‚ Ğ²Ñ�Ğµ Ñ‡Ğ¸Ñ�Ğ»Ğ° Ğ¸Ğ· Ñ‚ĞµĞºÑ�Ñ‚Ğ°
    
    Args:
        text: Ğ¢ĞµĞºÑ�Ñ‚ Ğ´Ğ»Ñ� Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ°
        max_count: ĞœĞ°ĞºÑ�Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ¾Ğµ ĞºĞ¾Ğ»Ğ¸Ñ‡ĞµÑ�Ñ‚Ğ²Ğ¾ Ñ‡Ğ¸Ñ�ĞµĞ» Ğ´Ğ»Ñ� Ğ¸Ğ·Ğ²Ğ»ĞµÑ‡ĞµĞ½Ğ¸Ñ�
        
    Returns:
        list: Ğ¡Ğ¿Ğ¸Ñ�Ğ¾Ğº Ğ½Ğ°Ğ¹Ğ´ĞµĞ½Ğ½Ñ‹Ñ… Ñ‡Ğ¸Ñ�ĞµĞ»
    """
    try:
        numbers = re.findall(r'[-+]?\d*\.?\d+', text)
        return [float(num) for num in numbers[:max_count]]
    except Exception:
        return []

def format_parsing_error(field_name: str, error: str, examples: list = None) -> str:
    """
    Ğ¤Ğ¾Ñ€Ğ¼Ğ°Ñ‚Ğ¸Ñ€ÑƒĞµÑ‚ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ Ğ¾Ğ± Ğ¾ÑˆĞ¸Ğ±ĞºĞµ Ğ¿Ğ°Ñ€Ñ�Ğ¸Ğ½Ğ³Ğ°
    
    Args:
        field_name: Ğ�Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿Ğ¾Ğ»Ñ�
        error: Ğ¢ĞµĞºÑ�Ñ‚ Ğ¾ÑˆĞ¸Ğ±ĞºĞ¸
        examples: ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹ ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğ³Ğ¾ Ğ²Ğ²Ğ¾Ğ´Ğ°
        
    Returns:
        str: Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ¾Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ Ğ¾Ğ± Ğ¾ÑˆĞ¸Ğ±ĞºĞµ
    """
    message = f"â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ğ²Ğ²Ğ¾Ğ´Ğµ {field_name}: {error}"
    
    if examples:
        message += "\n\nğŸ’¡ <b>ĞŸÑ€Ğ¸Ğ¼ĞµÑ€Ñ‹ ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ğ¾Ğ³Ğ¾ Ğ²Ğ²Ğ¾Ğ´Ğ°:</b>\n"
        for example in examples:
            message += f"â€¢ {example}\n"
    
    return message
