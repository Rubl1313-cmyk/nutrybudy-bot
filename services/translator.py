"""
Ğ¡ĞµÑ€Ğ²Ğ¸Ñ� Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ° Ğ´Ğ»Ñ� NutriBuddy â€” Ğ Ğ�Ğ¡Ğ¨Ğ˜Ğ Ğ•Ğ�Ğ�Ğ�Ğ¯ Ğ’Ğ•Ğ Ğ¡Ğ˜Ğ¯
âœ… 500+ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ¾Ğ² Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ² Ğ¸ Ğ±Ğ»Ñ�Ğ´
âœ… ĞŸÑ€Ñ�Ğ¼Ğ¾Ğµ Ğ¼Ğ°Ğ¿Ğ¿Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ AI â†’ Ğ±Ğ°Ğ·Ğ°
âœ… ĞšÑ�ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ¾Ğ²
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# ==================== ĞŸĞ Ğ¯ĞœĞ�Ğ• ĞœĞ�ĞŸĞŸĞ˜Ğ Ğ�Ğ’Ğ�Ğ�Ğ˜Ğ• AI â†’ Ğ‘Ğ�Ğ—Ğ� ====================
AI_TO_DB_MAPPING = {
    # Ğ Ğ«Ğ‘Ğ� (Ğ¾Ñ‚Ğ´ĞµĞ»ÑŒĞ½Ğ¾ Ğ¾Ñ‚ Ğ¼Ñ�Ñ�Ğ°!)
    "salmon": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ",
    "grilled salmon": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹",
    "baked salmon": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹",
    "salmon fillet": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ",
    "trout": "Ñ„Ğ¾Ñ€ĞµĞ»ÑŒ",
    "grilled trout": "Ñ„Ğ¾Ñ€ĞµĞ»ÑŒ Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�",
    "tuna": "Ñ‚ÑƒĞ½ĞµÑ†",
    "cod": "Ñ‚Ñ€ĞµÑ�ĞºĞ°",
    "mackerel": "Ñ�ĞºÑƒĞ¼Ğ±Ñ€Ğ¸Ñ�",
    "herring": "Ñ�ĞµĞ»ÑŒĞ´ÑŒ",
    "fish": "Ñ€Ñ‹Ğ±Ğ°",
    "grilled fish": "Ñ€Ñ‹Ğ±Ğ° Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�",
    "baked fish": "Ñ€Ñ‹Ğ±Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�",
    
    # Ğ¡Ğ£ĞŸĞ« (Ğ¾Ñ‚Ğ´ĞµĞ»ÑŒĞ½Ğ¾ Ğ¾Ñ‚ Ğ¾Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ñ… Ğ±Ğ»Ñ�Ğ´!)
    "borscht": "Ğ±Ğ¾Ñ€Ñ‰",
    "beet soup": "Ğ±Ğ¾Ñ€Ñ‰",
    "russian borscht": "Ğ±Ğ¾Ñ€Ñ‰",
    "shchi": "Ñ‰Ğ¸",
    "cabbage soup": "Ñ‰Ğ¸",
    "solyanka": "Ñ�Ğ¾Ğ»Ñ�Ğ½ĞºĞ°",
    "ukha": "ÑƒÑ…Ğ°",
    "fish soup": "ÑƒÑ…Ğ°",
    "chicken soup": "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿",
    "mushroom soup": "Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ¾Ğ¹ Ñ�ÑƒĞ¿",
    "pea soup": "Ğ³Ğ¾Ñ€Ğ¾Ñ…Ğ¾Ğ²Ñ‹Ğ¹ Ñ�ÑƒĞ¿",
    "noodle soup": "Ñ�ÑƒĞ¿ Ñ� Ğ»Ğ°Ğ¿ÑˆĞ¾Ğ¹",
    
    # ĞœĞ¯Ğ¡Ğ� (Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ğ½Ğ°Ñ�Ñ‚Ğ¾Ñ�Ñ‰ĞµĞµ Ğ¼Ñ�Ñ�Ğ¾)
    "beef": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°",
    "pork": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°",
    "lamb": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°",
    "veal": "Ñ‚ĞµĞ»Ñ�Ñ‚Ğ¸Ğ½Ğ°",
    "grilled beef": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ° Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�",
    "fried pork": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ° Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�",
    
    # ĞŸĞ¢Ğ˜Ğ¦Ğ�
    "chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
    "grilled chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�",
    "baked chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�",
    "chicken breast": "ĞºÑƒÑ€Ğ¸Ğ½Ğ°Ñ� Ğ³Ñ€ÑƒĞ´ĞºĞ°",
    "turkey": "Ğ¸Ğ½Ğ´ĞµĞ¹ĞºĞ°",
    
    # ĞŸĞ�Ğ¡Ğ¢Ğ� Ğ˜ Ğ“Ğ�Ğ Ğ�Ğ˜Ğ Ğ«
    "pasta": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹",
    "spaghetti": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸",
    "pasta with salmon": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼",
    "pasta with chicken": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
    "rice": "Ñ€Ğ¸Ñ�",
    "buckwheat": "Ğ³Ñ€ĞµÑ‡ĞºĞ°",
    "potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ",
    "mashed potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ",
    "fried potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹",
    
    # Ğ¡Ğ�Ğ›Ğ�Ğ¢Ğ«
    "salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚",
    "green salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚",
    "mixed salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚",
    "caesar salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ†ĞµĞ·Ğ°Ñ€ÑŒ",
    "greek salad": "Ğ³Ñ€ĞµÑ‡ĞµÑ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚",
    "olivier salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ¾Ğ»Ğ¸Ğ²ÑŒĞµ",
    
    # Ğ¥Ğ›Ğ•Ğ‘
    "bread": "Ñ…Ğ»ĞµĞ±",
    "white bread": "Ñ…Ğ»ĞµĞ± Ğ¿ÑˆĞµĞ½Ğ¸Ñ‡Ğ½Ñ‹Ğ¹",
    "black bread": "Ñ…Ğ»ĞµĞ± Ñ€Ğ¶Ğ°Ğ½Ğ¾Ğ¹",
    "bun": "Ğ±ÑƒĞ»ĞºĞ°",
    
    # Ğ‘Ğ»Ñ�Ğ´Ğ° - Ğ˜Ñ‚Ğ°Ğ»ÑŒÑ�Ğ½Ñ�ĞºĞ°Ñ� ĞºÑƒÑ…Ğ½Ñ�
    "spaghetti": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸",
    "spaghetti pasta": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸",
    "pasta spaghetti": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸",
    "spaghetti with tomato sauce": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸ Ñ� Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğ¾Ğ¼",
    "spaghetti with meat sauce": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸ Ñ� Ğ¼Ñ�Ñ�Ğ½Ñ‹Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğ¾Ğ¼",
    "spaghetti bolognese": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸ Ğ±Ğ¾Ğ»Ğ¾Ğ½ÑŒĞµĞ·Ğµ",
    "pasta": "Ğ¿Ğ°Ñ�Ñ‚Ğ°",
    "macaroni": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½",
    "penne": "Ğ¿ĞµĞ½Ğ½Ğµ",
    "fusilli": "Ñ„ÑƒĞ·Ğ¸Ğ»Ğ»Ğ¸",
    "rigatoni": "Ñ€Ğ¸Ğ³Ğ°Ñ‚Ğ¾Ğ½Ğ¸",
    "lasagna": "Ğ»Ğ°Ğ·Ğ°Ğ½ÑŒÑ�",
    "ravioli": "Ñ€Ğ°Ğ²Ğ¸Ğ¾Ğ»Ğ¸",
    "gnocchi": "Ğ½ÑŒĞ¾ĞºĞºĞ¸",
    "carbonara": "ĞºĞ°Ñ€Ğ±Ğ¾Ğ½Ğ°Ñ€Ğ°",
    "alfredo": "Ğ°Ğ»ÑŒÑ„Ñ€ĞµĞ´Ğ¾",
    "pesto": "Ğ¿ĞµÑ�Ñ‚Ğ¾",
    
    # Ğ�Ğ²Ğ¾Ñ‰Ğ¸
    "tomatoes": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹",
    "tomato": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€",
    "fresh tomatoes": "Ñ�Ğ²ĞµĞ¶Ğ¸Ğµ Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹",
    "cherry tomatoes": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ñ‡ĞµÑ€Ñ€Ğ¸",
    "plum tomatoes": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ñ�Ğ»Ğ¸Ğ²ĞºĞ°",
    "beef tomatoes": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹ Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒĞ¸",
    
    # Ğ¡Ğ¾ÑƒÑ�Ñ‹
    "tomato sauce": "Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
    "marinara sauce": "Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ°Ñ€Ğ°",
    "bolognese sauce": "Ğ±Ğ¾Ğ»Ğ¾Ğ½ÑŒĞµĞ·Ğµ",
    "alfredo sauce": "Ñ�Ğ¾ÑƒÑ� Ğ°Ğ»ÑŒÑ„Ñ€ĞµĞ´Ğ¾",
    "pesto sauce": "Ñ�Ğ¾ÑƒÑ� Ğ¿ĞµÑ�Ñ‚Ğ¾",
    "cream sauce": "Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
    "garlic sauce": "Ñ‡ĞµÑ�Ğ½Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
    "bbq sauce": "Ñ�Ğ¾ÑƒÑ� bbq",
    "soy sauce": "Ñ�Ğ¾ĞµĞ²Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
    "sweet and sour sauce": "ĞºĞ¸Ñ�Ğ»Ğ¾-Ñ�Ğ»Ğ°Ğ´ĞºĞ¸Ğ¹ Ñ�Ğ¾ÑƒÑ�",
    "hot sauce": "Ğ¾Ñ�Ñ‚Ñ€Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
    
    # Ğ‘Ğ»Ñ�Ğ´Ğ° - Ğ�Ñ�Ğ½Ğ¾Ğ²Ğ½Ñ‹Ğµ
    "grilled meat skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº",
    "meat skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº",
    "shish kebab": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº",
    "kebab": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº",
    "shashlik": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº",
    "grilled chicken skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· ĞºÑƒÑ€Ğ¸Ñ†Ñ‹",
    "grilled beef skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹",
    "grilled lamb skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ñ‹",
    "chicken skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· ĞºÑƒÑ€Ğ¸Ñ†Ñ‹",
    "beef skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ñ‹",
    "pork skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ñ‹",
    "lamb skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ğ¸Ğ· Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ñ‹",
    "grilled chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "roast chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�",
    "baked chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�",
    "fried chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ�",
    "chicken breast": "ĞºÑƒÑ€Ğ¸Ğ½Ğ°Ñ� Ğ³Ñ€ÑƒĞ´ĞºĞ°",
    
    # Ğ‘Ğ»Ñ�Ğ´Ğ° Ñ� Ñ€Ñ‹Ğ±Ğ¾Ğ¹
    "grilled salmon with pasta": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸",
    "salmon with pasta": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸",
    "grilled fish with pasta": "Ñ€Ñ‹Ğ±Ğ° Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸",
    "fish with pasta": "Ñ€Ñ‹Ğ±Ğ° Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸",
    "pasta with fish": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� Ñ€Ñ‹Ğ±Ğ¾Ğ¹",
    "pasta with salmon": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼",
    "fish pasta": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� Ñ€Ñ‹Ğ±Ğ¾Ğ¹",
    "salmon pasta": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼",
    "grilled fish salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ñ€Ñ‹Ğ±Ğ¾Ğ¹ Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "fish salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ñ€Ñ‹Ğ±Ğ¾Ğ¹",
    "seafood pasta": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� Ğ¼Ğ¾Ñ€ĞµĞ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ°Ğ¼Ğ¸",
    
    # ĞœĞµÑ‚Ğ¾Ğ´Ñ‹ Ğ¿Ñ€Ğ¸Ğ³Ğ¾Ñ‚Ğ¾Ğ²Ğ»ĞµĞ½Ğ¸Ñ�
    "grilled chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "fried chicken": "Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ� ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
    "boiled chicken": "Ğ²Ğ°Ñ€ĞµĞ½Ğ°Ñ� ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
    "baked chicken": "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ� ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
    "roasted chicken": "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ� ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
    "steamed chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ½Ğ° Ğ¿Ğ°Ñ€Ñƒ",
    "stewed chicken": "Ñ‚ÑƒÑˆĞµĞ½Ğ°Ñ� ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
    
    "grilled meat": "Ğ¼Ñ�Ñ�Ğ¾ Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "fried meat": "Ğ¶Ğ°Ñ€ĞµĞ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾",
    "boiled meat": "Ğ²Ğ°Ñ€ĞµĞ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾",
    "baked meat": "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾",
    "roasted meat": "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾",
    "stewed meat": "Ñ‚ÑƒÑˆĞµĞ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾",
    
    "grilled fish": "Ñ€Ñ‹Ğ±Ğ° Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "fried fish": "Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°",
    "boiled fish": "Ğ²Ğ°Ñ€ĞµĞ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°",
    "baked fish": "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°",
    "steamed fish": "Ñ€Ñ‹Ğ±Ğ° Ğ½Ğ° Ğ¿Ğ°Ñ€Ñƒ",
    
    # Ğ¡Ğ°Ğ»Ğ°Ñ‚Ñ‹ Ñ� ÑƒÑ‚Ğ¾Ñ‡Ğ½ĞµĞ½Ğ¸ĞµĞ¼
    "chicken pasta salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸ Ğ¸ ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
    "tuna pasta salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸ Ğ¸ Ñ‚ÑƒĞ½Ñ†Ğ¾Ğ¼",
    "seafood pasta salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸ Ğ¸ Ğ¼Ğ¾Ñ€ĞµĞ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ°Ğ¼Ğ¸",
    
    # Ğ¡Ğ°Ğ»Ğ°Ñ‚Ñ‹
    "caesar salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ†ĞµĞ·Ğ°Ñ€ÑŒ",
    "greek salad": "Ğ³Ñ€ĞµÑ‡ĞµÑ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚",
    "olivier salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ¾Ğ»Ğ¸Ğ²ÑŒĞµ",
    "russian salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ğ¾Ğ»Ğ¸Ğ²ÑŒĞµ",
    "pasta salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸",  # Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‰Ğ°ĞµĞ¼ ĞºĞ¾Ñ€Ñ€ĞµĞºÑ‚Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´
    "pasta with sauce": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� Ñ�Ğ¾ÑƒÑ�Ğ¾Ğ¼",  # Ğ�Ñ‚Ğ´ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ±Ğ»Ñ�Ğ´Ğ¾
    "borscht": "Ğ±Ğ¾Ñ€Ñ‰",
    "shchi": "Ñ‰Ğ¸",
    "solyanka": "Ñ�Ğ¾Ğ»Ñ�Ğ½ĞºĞ°",
    "ukha": "ÑƒÑ…Ğ°",
    "pilaf": "Ğ¿Ğ»Ğ¾Ğ²",
    "cutlets": "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹",
    "meat patties": "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹",
    "meatballs": "ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ñ‹",
    "pelmeni": "Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸",
    "dumplings": "Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸",
    "vareniki": "Ğ²Ğ°Ñ€ĞµĞ½Ğ¸ĞºĞ¸",
    "golubtsy": "Ğ³Ğ¾Ğ»ÑƒĞ±Ñ†Ñ‹",
    "cabbage rolls": "Ğ³Ğ¾Ğ»ÑƒĞ±Ñ†Ñ‹",
    "stuffed peppers": "Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€ĞµÑ†",
    "french meat": "Ğ¼Ñ�Ñ�Ğ¾ Ğ¿Ğ¾-Ñ„Ñ€Ğ°Ğ½Ñ†ÑƒĞ·Ñ�ĞºĞ¸",
    "buckwheat with meat": "Ğ³Ñ€ĞµÑ‡ĞºĞ° Ñ� Ğ¼Ñ�Ñ�Ğ¾Ğ¼",
    "pasta carbonara": "Ğ¿Ğ°Ñ�Ñ‚Ğ° ĞºĞ°Ñ€Ğ±Ğ¾Ğ½Ğ°Ñ€Ğ°",
    "spaghetti carbonara": "Ğ¿Ğ°Ñ�Ñ‚Ğ° ĞºĞ°Ñ€Ğ±Ğ¾Ğ½Ğ°Ñ€Ğ°",
    "pasta bolognese": "Ğ¿Ğ°Ñ�Ñ‚Ğ° Ğ±Ğ¾Ğ»Ğ¾Ğ½ÑŒĞµĞ·Ğµ",
    "spaghetti bolognese": "Ğ¿Ğ°Ñ�Ñ‚Ğ° Ğ±Ğ¾Ğ»Ğ¾Ğ½ÑŒĞµĞ·Ğµ",
    "navy-style pasta": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ğ¿Ğ¾-Ñ„Ğ»Ğ¾Ñ‚Ñ�ĞºĞ¸",
    "omelette": "Ğ¾Ğ¼Ğ»ĞµÑ‚",
    "omelet": "Ğ¾Ğ¼Ğ»ĞµÑ‚",
    "scrambled eggs": "Ñ�Ğ¸Ñ‡Ğ½Ğ¸Ñ†Ğ°",
    "fried eggs": "Ñ�Ğ¸Ñ‡Ğ½Ğ¸Ñ†Ğ°",
    "sunny side up": "Ñ�Ğ¸Ñ‡Ğ½Ğ¸Ñ†Ğ°",
    "syrniki": "Ñ�Ñ‹Ñ€Ğ½Ğ¸ĞºĞ¸",
    "cottage cheese pancakes": "Ñ�Ñ‹Ñ€Ğ½Ğ¸ĞºĞ¸",
    "oatmeal": "ĞºĞ°ÑˆĞ° Ğ¾Ğ²Ñ�Ñ�Ğ½Ğ°Ñ�",
    "oat porridge": "ĞºĞ°ÑˆĞ° Ğ¾Ğ²Ñ�Ñ�Ğ½Ğ°Ñ�",
    "hamburger": "Ğ³Ğ°Ğ¼Ğ±ÑƒÑ€Ğ³ĞµÑ€",
    "burger": "Ğ³Ğ°Ğ¼Ğ±ÑƒÑ€Ğ³ĞµÑ€",
    "cheeseburger": "Ñ‡Ğ¸Ğ·Ğ±ÑƒÑ€Ğ³ĞµÑ€",
    "pizza margherita": "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°",
    "margherita pizza": "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°",
    "pizza": "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°",
    "shawarma": "ÑˆĞ°ÑƒÑ€Ğ¼Ğ°",
    "doner kebab": "ÑˆĞ°ÑƒÑ€Ğ¼Ğ°",
    "gyro": "ÑˆĞ°ÑƒÑ€Ğ¼Ğ°",
    "philadelphia roll": "Ñ€Ğ¾Ğ»Ğ» Ñ„Ğ¸Ğ»Ğ°Ğ´ĞµĞ»ÑŒÑ„Ğ¸Ñ�",
    "philly roll": "Ñ€Ğ¾Ğ»Ğ» Ñ„Ğ¸Ğ»Ğ°Ğ´ĞµĞ»ÑŒÑ„Ğ¸Ñ�",
    "salmon roll": "Ñ€Ğ¾Ğ»Ğ» Ñ„Ğ¸Ğ»Ğ°Ğ´ĞµĞ»ÑŒÑ„Ğ¸Ñ�",
    "sushi": "Ñ�ÑƒÑˆĞ¸",
    "ramen": "Ñ€Ğ°Ğ¼ĞµĞ½",
    "mashed potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ",
    "potato puree": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ",
    "boiled rice": "Ñ€Ğ¸Ñ� Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ¾Ğ¹",
    "white rice": "Ñ€Ğ¸Ñ� Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ¾Ğ¹",
    "steamed rice": "Ñ€Ğ¸Ñ� Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ¾Ğ¹",
    "buckwheat": "Ğ³Ñ€ĞµÑ‡ĞºĞ° Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ°Ñ�",
    "buckwheat porridge": "Ğ³Ñ€ĞµÑ‡ĞºĞ° Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ°Ñ�",
    "kasha": "Ğ³Ñ€ĞµÑ‡ĞºĞ° Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ°Ñ�",
    "fried potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹",
    "home fries": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹",
    "french fries": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ñ„Ñ€Ğ¸",
    "fries": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ñ„Ñ€Ğ¸",
    "chips": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ñ„Ñ€Ğ¸",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - ĞœÑ�Ñ�Ğ¾
    "meat": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°",
    "beef": "Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ°",
    "pork": "Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ°",
    "chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
    "lamb": "Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ°",
    "turkey": "Ğ¸Ğ½Ğ´ĞµĞ¹ĞºĞ°",
    "duck": "ÑƒÑ‚ĞºĞ°",
    "rabbit": "ĞºÑ€Ğ¾Ğ»Ğ¸Ğº",
    "veal": "Ñ‚ĞµĞ»Ñ�Ñ‚Ğ¸Ğ½Ğ°",
    "ground meat": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹",
    "minced meat": "Ñ„Ğ°Ñ€Ñˆ Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹",
    "bacon": "Ğ±ĞµĞºĞ¾Ğ½",
    "ham": "Ğ²ĞµÑ‚Ñ‡Ğ¸Ğ½Ğ°",
    "sausage": "ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ°",
    "sausages": "Ñ�Ğ¾Ñ�Ğ¸Ñ�ĞºĞ¸",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - Ğ Ñ‹Ğ±Ğ°
    "fish": "Ñ‚Ñ€ĞµÑ�ĞºĞ°",
    "salmon": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ",
    "grilled salmon": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "grilled fish": "Ñ€Ñ‹Ğ±Ğ° Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "salmon fillet": "Ñ„Ğ¸Ğ»Ğµ Ğ»Ğ¾Ñ�Ğ¾Ñ�Ñ�",
    "fish fillet": "Ñ„Ğ¸Ğ»Ğµ Ñ€Ñ‹Ğ±Ñ‹",
    "red fish": "ĞºÑ€Ğ°Ñ�Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°",
    "trout": "Ñ„Ğ¾Ñ€ĞµĞ»ÑŒ",
    "grilled trout": "Ñ„Ğ¾Ñ€ĞµĞ»ÑŒ Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "tuna": "Ñ‚ÑƒĞ½ĞµÑ†",
    "grilled tuna": "Ñ‚ÑƒĞ½ĞµÑ† Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "cod": "Ñ‚Ñ€ĞµÑ�ĞºĞ°",
    "grilled cod": "Ñ‚Ñ€ĞµÑ�ĞºĞ° Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "mackerel": "Ñ�ĞºÑƒĞ¼Ğ±Ñ€Ğ¸Ñ�",
    "grilled mackerel": "Ñ�ĞºÑƒĞ¼Ğ±Ñ€Ğ¸Ñ� Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "herring": "Ñ�ĞµĞ»ÑŒĞ´ÑŒ",
    "shrimp": "ĞºÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸",
    "prawns": "ĞºÑ€ĞµĞ²ĞµÑ‚ĞºĞ¸",
    "crab": "ĞºÑ€Ğ°Ğ±",
    "lobster": "Ğ¾Ğ¼Ğ°Ñ€",
    "mussels": "Ğ¼Ğ¸Ğ´Ğ¸Ğ¸",
    "squid": "ĞºĞ°Ğ»ÑŒĞ¼Ğ°Ñ€Ñ‹",
    "octopus": "Ğ¾Ñ�ÑŒĞ¼Ğ¸Ğ½Ğ¾Ğ³",
    "caviar": "Ğ¸ĞºÑ€Ğ°",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - Ğ�Ğ²Ğ¾Ñ‰Ğ¸
    "vegetables": "Ğ¾Ğ²Ğ¾Ñ‰Ğ¸",
    "onion": "Ğ»ÑƒĞº",
    "onions": "Ğ»ÑƒĞº",
    "garlic": "Ñ‡ĞµÑ�Ğ½Ğ¾Ğº",
    "tomato": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€",
    "tomatoes": "Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹",
    "cucumber": "Ğ¾Ğ³ÑƒÑ€ĞµÑ†",
    "cucumbers": "Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹",
    "potato": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ",
    "potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ",
    "carrot": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ",
    "carrots": "Ğ¼Ğ¾Ñ€ĞºĞ¾Ğ²ÑŒ",
    "pepper": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹",
    "peppers": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹",
    "bell pepper": "Ğ¿ĞµÑ€ĞµÑ† Ğ±Ğ¾Ğ»Ğ³Ğ°Ñ€Ñ�ĞºĞ¸Ğ¹",
    "lettuce": "Ñ�Ğ°Ğ»Ğ°Ñ‚",
    "cabbage": "ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°",
    "broccoli": "Ğ±Ñ€Ğ¾ĞºĞºĞ¾Ğ»Ğ¸",
    "cauliflower": "Ñ†Ğ²ĞµÑ‚Ğ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°",
    "eggplant": "Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½",
    "zucchini": "ĞºĞ°Ğ±Ğ°Ñ‡Ğ¾Ğº",
    "pumpkin": "Ñ‚Ñ‹ĞºĞ²Ğ°",
    "beet": "Ñ�Ğ²ĞµĞºĞ»Ğ°",
    "beetroot": "Ñ�Ğ²ĞµĞºĞ»Ğ°",
    "radish": "Ñ€ĞµĞ´Ğ¸Ñ�",
    "celery": "Ñ�ĞµĞ»ÑŒĞ´ĞµÑ€ĞµĞ¹",
    "asparagus": "Ñ�Ğ¿Ğ°Ñ€Ğ¶Ğ°",
    "green beans": "Ñ�Ñ‚Ñ€ÑƒÑ‡ĞºĞ¾Ğ²Ğ°Ñ� Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ",
    "peas": "Ğ³Ğ¾Ñ€Ğ¾ÑˆĞµĞº",
    "corn": "ĞºÑƒĞºÑƒÑ€ÑƒĞ·Ğ°",
    "avocado": "Ğ°Ğ²Ğ¾ĞºĞ°Ğ´Ğ¾",
    "olives": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¸",
    "mushroom": "Ğ³Ñ€Ğ¸Ğ±Ñ‹",
    "mushrooms": "Ğ³Ñ€Ğ¸Ğ±Ñ‹",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - Ğ¤Ñ€ÑƒĞºÑ‚Ñ‹
    "fruit": "Ñ„Ñ€ÑƒĞºÑ‚Ñ‹",
    "fruits": "Ñ„Ñ€ÑƒĞºÑ‚Ñ‹",
    "apple": "Ñ�Ğ±Ğ»Ğ¾ĞºĞ¾",
    "apples": "Ñ�Ğ±Ğ»Ğ¾ĞºĞ¸",
    "banana": "Ğ±Ğ°Ğ½Ğ°Ğ½",
    "bananas": "Ğ±Ğ°Ğ½Ğ°Ğ½Ñ‹",
    "orange": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½",
    "oranges": "Ğ°Ğ¿ĞµĞ»ÑŒÑ�Ğ¸Ğ½Ñ‹",
    "tangerine": "Ğ¼Ğ°Ğ½Ğ´Ğ°Ñ€Ğ¸Ğ½",
    "lemon": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½",
    "lime": "Ğ»Ğ°Ğ¹Ğ¼",
    "grapefruit": "Ğ³Ñ€ĞµĞ¹Ğ¿Ñ„Ñ€ÑƒÑ‚",
    "kiwi": "ĞºĞ¸Ğ²Ğ¸",
    "pineapple": "Ğ°Ğ½Ğ°Ğ½Ğ°Ñ�",
    "mango": "Ğ¼Ğ°Ğ½Ğ³Ğ¾",
    "pear": "Ğ³Ñ€ÑƒÑˆĞ°",
    "peach": "Ğ¿ĞµÑ€Ñ�Ğ¸Ğº",
    "apricot": "Ğ°Ğ±Ñ€Ğ¸ĞºĞ¾Ñ�",
    "plum": "Ñ�Ğ»Ğ¸Ğ²Ğ°",
    "cherry": "Ğ²Ğ¸ÑˆĞ½Ñ�",
    "strawberry": "ĞºĞ»ÑƒĞ±Ğ½Ğ¸ĞºĞ°",
    "raspberry": "Ğ¼Ğ°Ğ»Ğ¸Ğ½Ğ°",
    "blueberry": "Ñ‡ĞµÑ€Ğ½Ğ¸ĞºĞ°",
    "grape": "Ğ²Ğ¸Ğ½Ğ¾Ğ³Ñ€Ğ°Ğ´",
    "grapes": "Ğ²Ğ¸Ğ½Ğ¾Ğ³Ñ€Ğ°Ğ´",
    "watermelon": "Ğ°Ñ€Ğ±ÑƒĞ·",
    "melon": "Ğ´Ñ‹Ğ½Ñ�",
    "pomegranate": "Ğ³Ñ€Ğ°Ğ½Ğ°Ñ‚",
    "persimmon": "Ñ…ÑƒÑ€Ğ¼Ğ°",
    "fig": "Ğ¸Ğ½Ğ¶Ğ¸Ñ€",
    "dates": "Ñ„Ğ¸Ğ½Ğ¸ĞºĞ¸",
    "raisins": "Ğ¸Ğ·Ñ�Ğ¼",
    "prunes": "Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²",
    "dried apricots": "ĞºÑƒÑ€Ğ°Ğ³Ğ°",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - ĞšÑ€ÑƒĞ¿Ñ‹
    "rice": "Ñ€Ğ¸Ñ�",
    "pasta": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹",
    "noodles": "Ğ»Ğ°Ğ¿ÑˆĞ°",
    "bread": "Ñ…Ğ»ĞµĞ±",
    "buckwheat": "Ğ³Ñ€ĞµÑ‡ĞºĞ°",
    "oatmeal": "Ğ¾Ğ²Ñ�Ñ�Ğ½ĞºĞ°",
    "oats": "Ğ¾Ğ²Ñ�Ñ�Ğ½ĞºĞ°",
    "millet": "Ğ¿ÑˆĞµĞ½Ğ¾",
    "barley": "Ğ¿ĞµÑ€Ğ»Ğ¾Ğ²ĞºĞ°",
    "quinoa": "ĞºĞ¸Ğ½Ğ¾Ğ°",
    "bulgur": "Ğ±ÑƒĞ»Ğ³ÑƒÑ€",
    "couscous": "ĞºÑƒÑ�ĞºÑƒÑ�",
    "semolina": "Ğ¼Ğ°Ğ½ĞºĞ°",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - ĞœĞ¾Ğ»Ğ¾Ñ‡Ğ½Ñ‹Ğµ
    "cheese": "Ñ�Ñ‹Ñ€",
    "milk": "Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾",
    "cream": "Ñ�Ğ»Ğ¸Ğ²ĞºĞ¸",
    "butter": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ¾Ñ‡Ğ½Ğ¾Ğµ",
    "yogurt": "Ğ¹Ğ¾Ğ³ÑƒÑ€Ñ‚",
    "kefir": "ĞºĞµÑ„Ğ¸Ñ€",
    "sour cream": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°",
    "cottage cheese": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³",
    "curd": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ³",
    "egg": "Ñ�Ğ¹Ñ†Ğ¾",
    "eggs": "Ñ�Ğ¹Ñ†Ğ¾",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - Ğ�Ñ€ĞµÑ…Ğ¸
    "nuts": "Ğ¾Ñ€ĞµÑ…Ğ¸",
    "walnuts": "Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğ¹ Ğ¾Ñ€ĞµÑ…",
    "almonds": "Ğ¼Ğ¸Ğ½Ğ´Ğ°Ğ»ÑŒ",
    "hazelnuts": "Ñ„ÑƒĞ½Ğ´ÑƒĞº",
    "peanuts": "Ğ°Ñ€Ğ°Ñ…Ğ¸Ñ�",
    "cashews": "ĞºĞµÑˆÑŒÑ�",
    "pistachios": "Ñ„Ğ¸Ñ�Ñ‚Ğ°ÑˆĞºĞ¸",
    "pine nuts": "ĞºĞµĞ´Ñ€Ğ¾Ğ²Ñ‹Ğ¹ Ğ¾Ñ€ĞµÑ…",
    "coconut": "ĞºĞ¾ĞºĞ¾Ñ�",
    "sesame seeds": "ĞºÑƒĞ½Ğ¶ÑƒÑ‚",
    "sunflower seeds": "Ñ�ĞµĞ¼ĞµĞ½Ğ° Ğ¿Ğ¾Ğ´Ñ�Ğ¾Ğ»Ğ½ĞµÑ‡Ğ½Ğ¸ĞºĞ°",
    "pumpkin seeds": "Ñ�ĞµĞ¼ĞµĞ½Ğ° Ñ‚Ñ‹ĞºĞ²Ñ‹",
    "flax seeds": "Ñ�ĞµĞ¼ĞµĞ½Ğ° Ğ»ÑŒĞ½Ğ°",
    "chia seeds": "Ñ�ĞµĞ¼ĞµĞ½Ğ° Ñ‡Ğ¸Ğ°",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - Ğ‘Ğ¾Ğ±Ğ¾Ğ²Ñ‹Ğµ
    "beans": "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ",
    "lentils": "Ñ‡ĞµÑ‡ĞµĞ²Ğ¸Ñ†Ğ°",
    "chickpeas": "Ğ½ÑƒÑ‚",
    "peas": "Ğ³Ğ¾Ñ€Ğ¾Ñ…",
    "soybeans": "Ñ�Ğ¾Ñ�",
    "tofu": "Ñ‚Ğ¾Ñ„Ñƒ",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - ĞœĞ°Ñ�Ğ»Ğ° Ğ¸ Ñ�Ğ¾ÑƒÑ�Ñ‹
    "oil": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ",
    "olive oil": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¾Ğ²Ğ¾Ğµ Ğ¼Ğ°Ñ�Ğ»Ğ¾",
    "vegetable oil": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ",
    "sunflower oil": "Ğ¼Ğ°Ñ�Ğ»Ğ¾ Ğ¿Ğ¾Ğ´Ñ�Ğ¾Ğ»Ğ½ĞµÑ‡Ğ½Ğ¾Ğµ",
    "sauce": "Ñ�Ğ¾ÑƒÑ�",
    "ketchup": "ĞºĞµÑ‚Ñ‡ÑƒĞ¿",
    "mayonnaise": "Ğ¼Ğ°Ğ¹Ğ¾Ğ½ĞµĞ·",
    "mustard": "Ğ³Ğ¾Ñ€Ñ‡Ğ¸Ñ†Ğ°",
    "soy sauce": "Ñ�Ğ¾ĞµĞ²Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
    "vinegar": "ÑƒĞºÑ�ÑƒÑ�",
    "salt": "Ñ�Ğ¾Ğ»ÑŒ",
    "pepper": "Ğ¿ĞµÑ€ĞµÑ†",
    "sugar": "Ñ�Ğ°Ñ…Ğ°Ñ€",
    "honey": "Ğ¼Ñ‘Ğ´",
    
    # Ğ˜Ğ½Ğ³Ñ€ĞµĞ´Ğ¸ĞµĞ½Ñ‚Ñ‹ - Ğ�Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¸
    "water": "Ğ²Ğ¾Ğ´Ğ°",
    "coffee": "ĞºĞ¾Ñ„Ğµ",
    "tea": "Ñ‡Ğ°Ğ¹",
    "juice": "Ñ�Ğ¾Ğº",
    "cola": "ĞºĞ¾Ğ»Ğ°",
    "lemonade": "Ğ»Ğ¸Ğ¼Ğ¾Ğ½Ğ°Ğ´",
    "beer": "Ğ¿Ğ¸Ğ²Ğ¾",
    "wine": "Ğ²Ğ¸Ğ½Ğ¾",
    "vodka": "Ğ²Ğ¾Ğ´ĞºĞ°",
    "cognac": "ĞºĞ¾Ğ½ÑŒÑ�Ğº",
    "whiskey": "Ğ²Ğ¸Ñ�ĞºĞ¸",

    "grilled salmon with pasta": "Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ñ� Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ğ°Ğ¼Ğ¸",
    "baked salmon with vegetables": "Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ Ñ� Ğ¾Ğ²Ğ¾Ñ‰Ğ°Ğ¼Ğ¸",
    "chicken with rice": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ñ� Ñ€Ğ¸Ñ�Ğ¾Ğ¼",
    "beef stew with potatoes": "Ğ³Ğ¾Ğ²Ñ�Ğ¶ÑŒĞµ Ñ€Ğ°Ğ³Ñƒ Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ĞµĞ¼",
    "pasta with tomato sauce": "Ğ¿Ğ°Ñ�Ñ‚Ğ° Ñ� Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ñ‹Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğ¾Ğ¼",
    "spaghetti with meat sauce": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸ Ñ� Ğ¼Ñ�Ñ�Ğ½Ñ‹Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğ¾Ğ¼",
    "caesar salad with chicken": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ†ĞµĞ·Ğ°Ñ€ÑŒ Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
    "greek salad with feta": "Ğ³Ñ€ĞµÑ‡ĞµÑ�ĞºĞ¸Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� Ñ„ĞµÑ‚Ğ¾Ğ¹",
    "mashed potatoes with gravy": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ Ñ� Ğ¿Ğ¾Ğ´Ğ»Ğ¸Ğ²ĞºĞ¾Ğ¹",
    "fried eggs with bacon": "Ñ�Ğ¸Ñ‡Ğ½Ğ¸Ñ†Ğ° Ñ� Ğ±ĞµĞºĞ¾Ğ½Ğ¾Ğ¼",
    "omelette with cheese": "Ğ¾Ğ¼Ğ»ĞµÑ‚ Ñ� Ñ�Ñ‹Ñ€Ğ¾Ğ¼",
    "pancakes with honey": "Ğ±Ğ»Ğ¸Ğ½Ñ‹ Ñ� Ğ¼Ñ‘Ğ´Ğ¾Ğ¼",
    "fried chicken wings": "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ ĞºÑ€Ñ‹Ğ»Ñ‹ÑˆĞºĞ¸ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğµ",
    "grilled vegetables": "Ğ¾Ğ²Ğ¾Ñ‰Ğ¸ Ğ³Ñ€Ğ¸Ğ»ÑŒ",
    "steamed fish": "Ñ€Ñ‹Ğ±Ğ° Ğ½Ğ° Ğ¿Ğ°Ñ€Ñƒ",
    "roasted chicken": "ĞºÑƒÑ€Ğ¸Ñ†Ğ° Ğ·Ğ°Ğ¿ĞµÑ‡ĞµĞ½Ğ½Ğ°Ñ�",
    "boiled potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¾Ñ‚Ğ²Ğ°Ñ€Ğ½Ğ¾Ğ¹",
    "mashed potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¿Ñ�Ñ€Ğµ",
    "fried potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹",
    "baked potatoes": "ĞºĞ°Ñ€Ñ‚Ğ¾Ñ„ĞµĞ»ÑŒ Ğ·Ğ°Ğ¿ĞµÑ‡Ñ‘Ğ½Ğ½Ñ‹Ğ¹",
    "rice with vegetables": "Ñ€Ğ¸Ñ� Ñ� Ğ¾Ğ²Ğ¾Ñ‰Ğ°Ğ¼Ğ¸",
    "buckwheat with mushrooms": "Ğ³Ñ€ĞµÑ‡ĞºĞ° Ñ� Ğ³Ñ€Ğ¸Ğ±Ğ°Ğ¼Ğ¸",
    "pasta with cheese": "Ğ¼Ğ°ĞºĞ°Ñ€Ğ¾Ğ½Ñ‹ Ñ� Ñ�Ñ‹Ñ€Ğ¾Ğ¼",
    "spaghetti carbonara": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸ ĞºĞ°Ñ€Ğ±Ğ¾Ğ½Ğ°Ñ€Ğ°",
    "spaghetti bolognese": "Ñ�Ğ¿Ğ°Ğ³ĞµÑ‚Ñ‚Ğ¸ Ğ±Ğ¾Ğ»Ğ¾Ğ½ÑŒĞµĞ·Ğµ",
    "lasagna": "Ğ»Ğ°Ğ·Ğ°Ğ½ÑŒÑ�",
    "pizza margherita": "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ¼Ğ°Ñ€Ğ³Ğ°Ñ€Ğ¸Ñ‚Ğ°",
    "pizza pepperoni": "Ğ¿Ğ¸Ñ†Ñ†Ğ° Ğ¿ĞµĞ¿Ğ¿ĞµÑ€Ğ¾Ğ½Ğ¸",
    "burger with fries": "Ğ±ÑƒÑ€Ğ³ĞµÑ€ Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾ÑˆĞºĞ¾Ğ¹ Ñ„Ñ€Ğ¸",
    "chicken nuggets": "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğµ Ğ½Ğ°Ğ³Ğ³ĞµÑ‚Ñ�Ñ‹",
    "fish and chips": "Ñ€Ñ‹Ğ±Ğ° Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾ÑˆĞºĞ¾Ğ¹ Ñ„Ñ€Ğ¸",
    "sushi with salmon": "Ñ�ÑƒÑˆĞ¸ Ñ� Ğ»Ğ¾Ñ�Ğ¾Ñ�ĞµĞ¼",
    "sashimi": "Ñ�Ğ°ÑˆĞ¸Ğ¼Ğ¸",
    "ramen with pork": "Ñ€Ğ°Ğ¼ĞµĞ½ Ñ�Ğ¾ Ñ�Ğ²Ğ¸Ğ½Ğ¸Ğ½Ğ¾Ğ¹",
    "udon with chicken": "ÑƒĞ´Ğ¾Ğ½ Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
    "fried rice with egg": "Ğ¶Ğ°Ñ€ĞµĞ½Ñ‹Ğ¹ Ñ€Ğ¸Ñ� Ñ� Ñ�Ğ¹Ñ†Ğ¾Ğ¼",
    "dumplings with meat": "Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸",
    "dumplings with potato": "Ğ²Ğ°Ñ€ĞµĞ½Ğ¸ĞºĞ¸ Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾ÑˆĞºĞ¾Ğ¹",
    "dumplings with cherry": "Ğ²Ğ°Ñ€ĞµĞ½Ğ¸ĞºĞ¸ Ñ� Ğ²Ğ¸ÑˆĞ½ĞµĞ¹",
    "stuffed peppers": "Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€ĞµÑ†",
    "stuffed cabbage rolls": "Ğ³Ğ¾Ğ»ÑƒĞ±Ñ†Ñ‹",
    "meatballs in tomato sauce": "Ñ‚ĞµÑ„Ñ‚ĞµĞ»Ğ¸ Ğ² Ñ‚Ğ¾Ğ¼Ğ°Ñ‚Ğ½Ğ¾Ğ¼ Ñ�Ğ¾ÑƒÑ�Ğµ",
    "chicken cutlet": "ĞºÑƒÑ€Ğ¸Ğ½Ğ°Ñ� ĞºĞ¾Ñ‚Ğ»ĞµÑ‚Ğ°",
    "pork chop": "Ñ�Ğ²Ğ¸Ğ½Ğ°Ñ� Ğ¾Ñ‚Ğ±Ğ¸Ğ²Ğ½Ğ°Ñ�",
    "beef steak": "Ğ³Ğ¾Ğ²Ñ�Ğ¶Ğ¸Ğ¹ Ñ�Ñ‚ĞµĞ¹Ğº",
    "lamb chops": "Ğ±Ğ°Ñ€Ğ°Ğ½ÑŒĞ¸ Ğ¾Ñ‚Ğ±Ğ¸Ğ²Ğ½Ñ‹Ğµ",
    "grilled sausage": "Ğ¶Ğ°Ñ€ĞµĞ½Ğ°Ñ� ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ°",
    "fried eggs": "Ñ�Ğ¸Ñ‡Ğ½Ğ¸Ñ†Ğ°",
    "scrambled eggs": "Ğ¾Ğ¼Ğ»ĞµÑ‚",
    "boiled egg": "Ñ�Ğ¹Ñ†Ğ¾ Ğ²Ğ°Ñ€Ñ‘Ğ½Ğ¾Ğµ",
    "poached egg": "Ñ�Ğ¹Ñ†Ğ¾ Ğ¿Ğ°ÑˆĞ¾Ñ‚",
    "oatmeal with berries": "Ğ¾Ğ²Ñ�Ñ�Ğ½ĞºĞ° Ñ� Ñ�Ğ³Ğ¾Ğ´Ğ°Ğ¼Ğ¸",
    "porridge with milk": "ĞºĞ°ÑˆĞ° Ğ½Ğ° Ğ¼Ğ¾Ğ»Ğ¾ĞºĞµ",
    "buckwheat porridge": "Ğ³Ñ€ĞµÑ‡Ğ½ĞµĞ²Ğ°Ñ� ĞºĞ°ÑˆĞ°",
    "rice porridge": "Ñ€Ğ¸Ñ�Ğ¾Ğ²Ğ°Ñ� ĞºĞ°ÑˆĞ°",
    "millet porridge": "Ğ¿ÑˆĞµĞ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ°",
    "semolina porridge": "Ğ¼Ğ°Ğ½Ğ½Ğ°Ñ� ĞºĞ°ÑˆĞ°",
    "pancakes with jam": "Ğ±Ğ»Ğ¸Ğ½Ñ‹ Ñ� Ğ²Ğ°Ñ€ĞµĞ½ÑŒĞµĞ¼",
    "pancakes with sour cream": "Ğ±Ğ»Ğ¸Ğ½Ñ‹ Ñ�Ğ¾ Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ¾Ğ¹",
    "syrupy pancakes": "Ğ±Ğ»Ğ¸Ğ½Ñ‹ Ñ� Ñ�Ğ¸Ñ€Ğ¾Ğ¿Ğ¾Ğ¼",
    "cheesecakes": "Ñ�Ñ‹Ñ€Ğ½Ğ¸ĞºĞ¸",
    "cottage cheese casserole": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ¶Ğ½Ğ°Ñ� Ğ·Ğ°Ğ¿ĞµĞºĞ°Ğ½ĞºĞ°",
    "cabbage soup": "Ñ‰Ğ¸",
    "beetroot soup": "Ğ±Ğ¾Ñ€Ñ‰",
    "fish soup": "ÑƒÑ…Ğ°",
    "mushroom soup": "Ğ³Ñ€Ğ¸Ğ±Ğ½Ğ¾Ğ¹ Ñ�ÑƒĞ¿",
    "pea soup": "Ğ³Ğ¾Ñ€Ğ¾Ñ…Ğ¾Ğ²Ñ‹Ğ¹ Ñ�ÑƒĞ¿",
    "chicken soup": "ĞºÑƒÑ€Ğ¸Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿",
    "noodle soup": "Ñ�ÑƒĞ¿ Ñ� Ğ»Ğ°Ğ¿ÑˆĞ¾Ğ¹",
    "borscht with sour cream": "Ğ±Ğ¾Ñ€Ñ‰ Ñ�Ğ¾ Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ¾Ğ¹",
    "shchi with meat": "Ñ‰Ğ¸ Ñ� Ğ¼Ñ�Ñ�Ğ¾Ğ¼",
    "rassolnik": "Ñ€Ğ°Ñ�Ñ�Ğ¾Ğ»ÑŒĞ½Ğ¸Ğº",
    "solyanka": "Ñ�Ğ¾Ğ»Ñ�Ğ½ĞºĞ°",
    "okroshka": "Ğ¾ĞºÑ€Ğ¾ÑˆĞºĞ°",
    "cold beet soup": "Ñ�Ğ²ĞµĞºĞ¾Ğ»ÑŒĞ½Ğ¸Ğº",
    "green borscht": "Ğ·ĞµĞ»Ñ‘Ğ½Ñ‹Ğ¹ Ğ±Ğ¾Ñ€Ñ‰",
    "kharcho": "Ñ…Ğ°Ñ€Ñ‡Ğ¾",
    "lagman": "Ğ»Ğ°Ğ³Ğ¼Ğ°Ğ½",
    "shurpa": "ÑˆÑƒÑ€Ğ¿Ğ°",
    "pilaf with lamb": "Ğ¿Ğ»Ğ¾Ğ² Ñ� Ğ±Ğ°Ñ€Ğ°Ğ½Ğ¸Ğ½Ğ¾Ğ¹",
    "pilaf with beef": "Ğ¿Ğ»Ğ¾Ğ² Ñ� Ğ³Ğ¾Ğ²Ñ�Ğ´Ğ¸Ğ½Ğ¾Ğ¹",
    "pilaf with chicken": "Ğ¿Ğ»Ğ¾Ğ² Ñ� ĞºÑƒÑ€Ğ¸Ñ†ĞµĞ¹",
    "uzbek pilaf": "ÑƒĞ·Ğ±ĞµĞºÑ�ĞºĞ¸Ğ¹ Ğ¿Ğ»Ğ¾Ğ²",
    "kazan kebab": "ĞºĞ°Ğ·Ğ°Ğ½-ĞºĞµĞ±Ğ°Ğ±",
    "shashlik with onions": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº Ñ� Ğ»ÑƒĞºĞ¾Ğ¼",
    "grilled meat skewers": "ÑˆĞ°ÑˆĞ»Ñ‹Ğº",
    "lula kebab": "Ğ»Ñ�Ğ»Ñ�-ĞºĞµĞ±Ğ°Ğ±",
    "dolma": "Ğ´Ğ¾Ğ»Ğ¼Ğ°",
    "manti": "Ğ¼Ğ°Ğ½Ñ‚Ñ‹",
    "khinkali": "Ñ…Ğ¸Ğ½ĞºĞ°Ğ»Ğ¸",
    "chakhokhbili": "Ñ‡Ğ°Ñ…Ğ¾Ñ…Ğ±Ğ¸Ğ»Ğ¸",
    "satsivi": "Ñ�Ğ°Ñ†Ğ¸Ğ²Ğ¸",
    "ajapsandali": "Ğ°Ğ´Ğ¶Ğ°Ğ¿Ñ�Ğ°Ğ½Ğ´Ğ°Ğ»Ğ¸",
    "lobio": "Ğ»Ğ¾Ğ±Ğ¸Ğ¾",
    "pkhali": "Ğ¿Ñ…Ğ°Ğ»Ğ¸",
    "khachapuri": "Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸",
    "adjarian khachapuri": "Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸ Ğ¿Ğ¾-Ğ°Ğ´Ğ¶Ğ°Ñ€Ñ�ĞºĞ¸",
    "imeretian khachapuri": "Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸ Ğ¿Ğ¾-Ğ¸Ğ¼ĞµÑ€ĞµÑ‚Ğ¸Ğ½Ñ�ĞºĞ¸",
    "megrelian khachapuri": "Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸ Ğ¿Ğ¾-Ğ¼ĞµĞ³Ñ€ĞµĞ»ÑŒÑ�ĞºĞ¸",
    "georgian cheese bread": "Ñ…Ğ°Ñ‡Ğ°Ğ¿ÑƒÑ€Ğ¸",
    "cheburek": "Ñ‡ĞµĞ±ÑƒÑ€ĞµĞº",
    "belyash": "Ğ±ĞµĞ»Ñ�Ñˆ",
    "samsa": "Ñ�Ğ°Ğ¼Ñ�Ğ°",
    "pie with meat": "Ğ¿Ğ¸Ñ€Ğ¾Ğ¶Ğ¾Ğº Ñ� Ğ¼Ñ�Ñ�Ğ¾Ğ¼",
    "pie with cabbage": "Ğ¿Ğ¸Ñ€Ğ¾Ğ¶Ğ¾Ğº Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ¾Ğ¹",
    "pie with potato": "Ğ¿Ğ¸Ñ€Ğ¾Ğ¶Ğ¾Ğº Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾ÑˆĞºĞ¾Ğ¹",
    "pie with egg and onion": "Ğ¿Ğ¸Ñ€Ğ¾Ğ¶Ğ¾Ğº Ñ� Ñ�Ğ¹Ñ†Ğ¾Ğ¼ Ğ¸ Ğ»ÑƒĞºĞ¾Ğ¼",
    "pie with apple": "Ğ¿Ğ¸Ñ€Ğ¾Ğ¶Ğ¾Ğº Ñ� Ñ�Ğ±Ğ»Ğ¾ĞºĞ¾Ğ¼",
    "cheese pie": "Ñ�Ñ‹Ñ€Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³",
    "meat pie": "Ğ¼Ñ�Ñ�Ğ½Ğ¾Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³",
    "fish pie": "Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³",
    "cabbage pie": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ¾Ğ¹",
    "potato pie": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾ÑˆĞºĞ¾Ğ¹",
    "apple pie": "Ñ�Ğ±Ğ»Ğ¾Ñ‡Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³",
    "cottage cheese pie": "Ñ‚Ğ²Ğ¾Ñ€Ğ¾Ğ¶Ğ½Ñ‹Ğ¹ Ğ¿Ğ¸Ñ€Ğ¾Ğ³",
    "honey cake": "Ğ¼ĞµĞ´Ğ¾Ğ²Ğ¸Ğº",
    "napoleon cake": "Ğ½Ğ°Ğ¿Ğ¾Ğ»ĞµĞ¾Ğ½",
    "tiramisu": "Ñ‚Ğ¸Ñ€Ğ°Ğ¼Ğ¸Ñ�Ñƒ",
    "panna cotta": "Ğ¿Ğ°Ğ½Ğ½Ğ°-ĞºĞ¾Ñ‚Ñ‚Ğ°",
    "creme brulee": "ĞºÑ€ĞµĞ¼-Ğ±Ñ€Ñ�Ğ»Ğµ",
    "ice cream": "Ğ¼Ğ¾Ñ€Ğ¾Ğ¶ĞµĞ½Ğ¾Ğµ",
    "chocolate ice cream": "ÑˆĞ¾ĞºĞ¾Ğ»Ğ°Ğ´Ğ½Ğ¾Ğµ Ğ¼Ğ¾Ñ€Ğ¾Ğ¶ĞµĞ½Ğ¾Ğµ",
    "strawberry ice cream": "ĞºĞ»ÑƒĞ±Ğ½Ğ¸Ñ‡Ğ½Ğ¾Ğµ Ğ¼Ğ¾Ñ€Ğ¾Ğ¶ĞµĞ½Ğ¾Ğµ",
    "vanilla ice cream": "Ğ²Ğ°Ğ½Ğ¸Ğ»ÑŒĞ½Ğ¾Ğµ Ğ¼Ğ¾Ñ€Ğ¾Ğ¶ĞµĞ½Ğ¾Ğµ",
    "fruit sorbet": "Ñ„Ñ€ÑƒĞºÑ‚Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾Ñ€Ğ±ĞµÑ‚",
    "fruit salad": "Ñ„Ñ€ÑƒĞºÑ‚Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ°Ğ»Ğ°Ñ‚",
    "fruit platter": "Ñ„Ñ€ÑƒĞºÑ‚Ğ¾Ğ²Ğ°Ñ� Ñ‚Ğ°Ñ€ĞµĞ»ĞºĞ°",
    "cheese plate": "Ñ�Ñ‹Ñ€Ğ½Ğ°Ñ� Ñ‚Ğ°Ñ€ĞµĞ»ĞºĞ°",
    "meat platter": "Ğ¼Ñ�Ñ�Ğ½Ğ°Ñ� Ñ‚Ğ°Ñ€ĞµĞ»ĞºĞ°",
    "seafood platter": "Ñ‚Ğ°Ñ€ĞµĞ»ĞºĞ° Ğ¼Ğ¾Ñ€ĞµĞ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ²",
    "vegetable platter": "Ğ¾Ğ²Ğ¾Ñ‰Ğ½Ğ°Ñ� Ñ‚Ğ°Ñ€ĞµĞ»ĞºĞ°",
    "cold cuts": "Ğ¼Ñ�Ñ�Ğ½Ğ°Ñ� Ğ½Ğ°Ñ€ĞµĞ·ĞºĞ°",
    "sausage platter": "ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ½Ğ°Ñ� Ğ½Ğ°Ñ€ĞµĞ·ĞºĞ°",
    "cheese and ham": "Ñ�Ñ‹Ñ€Ğ½Ğ¾-Ğ²ĞµÑ‚Ñ‡Ğ¸Ğ½Ğ½Ğ°Ñ� Ğ½Ğ°Ñ€ĞµĞ·ĞºĞ°",
    "olives and cheese": "Ğ¾Ğ»Ğ¸Ğ²ĞºĞ¸ Ñ� Ñ�Ñ‹Ñ€Ğ¾Ğ¼",
    "pickles": "Ñ�Ğ¾Ğ»ĞµĞ½ÑŒÑ�",
    "marinated mushrooms": "Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ³Ñ€Ğ¸Ğ±Ñ‹",
    "sauerkraut": "ĞºĞ²Ğ°ÑˆĞµĞ½Ğ°Ñ� ĞºĞ°Ğ¿ÑƒÑ�Ñ‚Ğ°",
    "kimchi": "ĞºĞ¸Ğ¼Ñ‡Ğ¸",
    "pickled cucumbers": "Ñ�Ğ¾Ğ»Ñ‘Ğ½Ñ‹Ğµ Ğ¾Ğ³ÑƒÑ€Ñ†Ñ‹",
    "pickled tomatoes": "Ñ�Ğ¾Ğ»Ñ‘Ğ½Ñ‹Ğµ Ğ¿Ğ¾Ğ¼Ğ¸Ğ´Ğ¾Ñ€Ñ‹",
    "pickled peppers": "Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€ĞµÑ†",
    "pickled garlic": "Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ñ‡ĞµÑ�Ğ½Ğ¾Ğº",
    "pickled eggplant": "Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ±Ğ°ĞºĞ»Ğ°Ğ¶Ğ°Ğ½Ñ‹",
    "pickled zucchini": "Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ ĞºĞ°Ğ±Ğ°Ñ‡ĞºĞ¸",
    "pickled squash": "Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¿Ğ°Ñ‚Ğ¸Ñ�Ñ�Ğ¾Ğ½Ñ‹",
    "pickled mix": "Ğ°Ñ�Ñ�Ğ¾Ñ€Ñ‚Ğ¸ Ğ¼Ğ°Ñ€Ğ¸Ğ½Ğ¾Ğ²Ğ°Ğ½Ğ½Ğ¾Ğµ",
    "canned vegetables": "ĞºĞ¾Ğ½Ñ�ĞµÑ€Ğ²Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾Ğ²Ğ¾Ñ‰Ğ¸",
    "canned fish": "Ñ€Ñ‹Ğ±Ğ½Ñ‹Ğµ ĞºĞ¾Ğ½Ñ�ĞµÑ€Ğ²Ñ‹",
    "sprats": "ÑˆĞ¿Ñ€Ğ¾Ñ‚Ñ‹",
    "sardines": "Ñ�Ğ°Ñ€Ğ´Ğ¸Ğ½Ñ‹",
    "tuna in oil": "Ñ‚ÑƒĞ½ĞµÑ† Ğ² Ğ¼Ğ°Ñ�Ğ»Ğµ",
    "tuna in water": "Ñ‚ÑƒĞ½ĞµÑ† Ğ² Ñ�Ğ¾Ğ±Ñ�Ñ‚Ğ²ĞµĞ½Ğ½Ğ¾Ğ¼ Ñ�Ğ¾ĞºÑƒ",
    "salted herring": "Ñ�Ğ¾Ğ»Ñ‘Ğ½Ğ°Ñ� Ñ�ĞµĞ»ÑŒĞ´ÑŒ",
    "smoked herring": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ğ°Ñ� Ñ�ĞµĞ»ÑŒĞ´ÑŒ",
    "smoked mackerel": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ğ°Ñ� Ñ�ĞºÑƒĞ¼Ğ±Ñ€Ğ¸Ñ�",
    "smoked salmon": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ñ‹Ğ¹ Ğ»Ğ¾Ñ�Ğ¾Ñ�ÑŒ",
    "smoked trout": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ğ°Ñ� Ñ„Ğ¾Ñ€ĞµĞ»ÑŒ",
    "smoked eel": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ñ‹Ğ¹ ÑƒĞ³Ğ¾Ñ€ÑŒ",
    "smoked chicken": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ğ°Ñ� ĞºÑƒÑ€Ğ¸Ñ†Ğ°",
    "smoked meat": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾",
    "smoked sausage": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ğ°Ñ� ĞºĞ¾Ğ»Ğ±Ğ°Ñ�Ğ°",
    "smoked cheese": "ĞºĞ¾Ğ¿Ñ‡Ñ‘Ğ½Ñ‹Ğ¹ Ñ�Ñ‹Ñ€",
    "dried fish": "Ñ�ÑƒÑˆÑ‘Ğ½Ğ°Ñ� Ñ€Ñ‹Ğ±Ğ°",
    "dried meat": "Ñ�ÑƒÑˆÑ‘Ğ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾",
    "jerky": "Ğ´Ğ¶ĞµÑ€ĞºĞ¸",
    "bacon": "Ğ±ĞµĞºĞ¾Ğ½",
    "ham": "Ğ²ĞµÑ‚Ñ‡Ğ¸Ğ½Ğ°",
    "prosciutto": "Ğ¿Ñ€Ğ¾ÑˆÑƒÑ‚Ñ‚Ğ¾",
    "salami": "Ñ�Ğ°Ğ»Ñ�Ğ¼Ğ¸",
    "pepperoni": "Ğ¿ĞµĞ¿Ğ¿ĞµÑ€Ğ¾Ğ½Ğ¸",
    "chorizo": "Ñ‡Ğ¾Ñ€Ğ¸Ğ·Ğ¾",
    "bratwurst": "Ğ±Ñ€Ğ°Ñ‚Ğ²ÑƒÑ€Ñ�Ñ‚",
    "frankfurter": "Ñ„Ñ€Ğ°Ğ½ĞºÑ„ÑƒÑ€Ñ‚Ñ�ĞºĞ°Ñ� Ñ�Ğ¾Ñ�Ğ¸Ñ�ĞºĞ°",
    "wiener": "Ğ²ĞµĞ½Ñ�ĞºĞ°Ñ� Ñ�Ğ¾Ñ�Ğ¸Ñ�ĞºĞ°",
    "hot dog": "Ñ…Ğ¾Ñ‚-Ğ´Ğ¾Ğ³",
    "bratwurst with mustard": "Ğ±Ñ€Ğ°Ñ‚Ğ²ÑƒÑ€Ñ�Ñ‚ Ñ� Ğ³Ğ¾Ñ€Ñ‡Ğ¸Ñ†ĞµĞ¹",
    "currywurst": "ĞºĞ°Ñ€Ñ€Ğ¸Ğ²ÑƒÑ€Ñ�Ñ‚",
    "kebab": "ĞºĞµĞ±Ğ°Ğ±",
    "doner kebab": "Ğ´Ğ¾Ğ½ĞµÑ€-ĞºĞµĞ±Ğ°Ğ±",
    "gyros": "Ğ³Ğ¸Ñ€Ğ¾Ñ�",
    "souvlaki": "Ñ�ÑƒĞ²Ğ»Ğ°ĞºĞ¸",
    "taco": "Ñ‚Ğ°ĞºĞ¾",
    "burrito": "Ğ±ÑƒÑ€Ñ€Ğ¸Ñ‚Ğ¾",
    "enchilada": "Ñ�Ğ½Ñ‡Ğ¸Ğ»Ğ°Ğ´Ğ°",
    "quesadilla": "ĞºĞµÑ�Ğ°Ğ´Ğ¸Ğ»ÑŒÑ�",
    "nachos": "Ğ½Ğ°Ñ‡Ğ¾Ñ�",
    "tortilla chips": "Ñ‚Ğ¾Ñ€Ñ‚Ğ¸Ğ»ÑŒÑ� Ñ‡Ğ¸Ğ¿Ñ�Ñ‹",
    "guacamole": "Ğ³ÑƒĞ°ĞºĞ°Ğ¼Ğ¾Ğ»Ğµ",
    "salsa": "Ñ�Ğ°Ğ»ÑŒÑ�Ğ°",
    "sour cream": "Ñ�Ğ¼ĞµÑ‚Ğ°Ğ½Ğ°",
    "yogurt sauce": "Ğ¹Ğ¾Ğ³ÑƒÑ€Ñ‚Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ğ¾ÑƒÑ�",
    "tzatziki": "Ñ†Ğ°Ñ†Ğ¸ĞºĞ¸",
    "hummus": "Ñ…ÑƒĞ¼ÑƒÑ�",
    "baba ganoush": "Ğ±Ğ°Ğ±Ğ°-Ğ³Ğ°Ğ½ÑƒÑˆ",
    "falafel": "Ñ„Ğ°Ğ»Ğ°Ñ„ĞµĞ»ÑŒ",
    "tabbouleh": "Ñ‚Ğ°Ğ±ÑƒĞ»Ğµ",
    "fattoush": "Ñ„Ğ°Ñ‚Ñ‚ÑƒÑˆ",
    "couscous": "ĞºÑƒÑ�ĞºÑƒÑ�",
    "bulgur": "Ğ±ÑƒĞ»Ğ³ÑƒÑ€",
    "quinoa": "ĞºĞ¸Ğ½Ğ¾Ğ°",
    "freekeh": "Ñ„Ñ€Ğ¸ĞºĞµ",
    "lentils": "Ñ‡ĞµÑ‡ĞµĞ²Ğ¸Ñ†Ğ°",
    "chickpeas": "Ğ½ÑƒÑ‚",
    "beans": "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ",
    "black beans": "Ñ‡Ñ‘Ñ€Ğ½Ğ°Ñ� Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ",
    "red beans": "ĞºÑ€Ğ°Ñ�Ğ½Ğ°Ñ� Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ",
    "white beans": "Ğ±ĞµĞ»Ğ°Ñ� Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ",
    "kidney beans": "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ",
    "pinto beans": "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ Ğ¿Ğ¸Ğ½Ñ‚Ğ¾",
    "cannellini beans": "Ñ„Ğ°Ñ�Ğ¾Ğ»ÑŒ ĞºĞ°Ğ½Ğ½ĞµĞ»Ğ»Ğ¸Ğ½Ğ¸",
    "fava beans": "Ğ±Ğ¾Ğ±Ñ‹ Ñ„Ğ°Ğ²Ğ°",
    "edamame": "Ñ�Ğ´Ğ°Ğ¼Ğ°Ğ¼Ğµ",
    "soybeans": "Ñ�Ğ¾ĞµĞ²Ñ‹Ğµ Ğ±Ğ¾Ğ±Ñ‹",
    "tofu": "Ñ‚Ğ¾Ñ„Ñƒ",
    "tempeh": "Ñ‚ĞµĞ¼Ğ¿Ğµ",
    "seitan": "Ñ�ĞµĞ¹Ñ‚Ğ°Ğ½",
    "textured vegetable protein": "Ñ‚ĞµĞºÑ�Ñ‚ÑƒÑ€Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğ¹ Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ñ‹Ğ¹ Ğ±ĞµĞ»Ğ¾Ğº",
    "plant-based meat": "Ñ€Ğ°Ñ�Ñ‚Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ğµ Ğ¼Ñ�Ñ�Ğ¾",
    "vegetarian burger": "Ğ²ĞµĞ³ĞµÑ‚Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ�ĞºĞ¸Ğ¹ Ğ±ÑƒÑ€Ğ³ĞµÑ€",
    "vegan burger": "Ğ²ĞµĞ³Ğ°Ğ½Ñ�ĞºĞ¸Ğ¹ Ğ±ÑƒÑ€Ğ³ĞµÑ€",
    "impossible burger": "Ğ¸Ğ¼Ğ¿Ğ°Ñ�Ñ�Ğ¸Ğ±Ğ» Ğ±ÑƒÑ€Ğ³ĞµÑ€",
    "beyond burger": "Ğ±Ğ¸Ğ¹Ğ¾Ğ½Ğ´ Ğ±ÑƒÑ€Ğ³ĞµÑ€",
    "quinoa salad": "Ñ�Ğ°Ğ»Ğ°Ñ‚ Ñ� ĞºĞ¸Ğ½Ğ¾Ğ°",
    "lentil soup": "Ñ‡ĞµÑ‡ĞµĞ²Ğ¸Ñ‡Ğ½Ñ‹Ğ¹ Ñ�ÑƒĞ¿",
    "bean soup": "Ğ±Ğ¾Ğ±Ğ¾Ğ²Ñ‹Ğ¹ Ñ�ÑƒĞ¿",
    "chickpea curry": "ĞºĞ°Ñ€Ñ€Ğ¸ Ğ¸Ğ· Ğ½ÑƒÑ‚Ğ°",
    "lentil curry": "ĞºĞ°Ñ€Ñ€Ğ¸ Ğ¸Ğ· Ñ‡ĞµÑ‡ĞµĞ²Ğ¸Ñ†Ñ‹",
    "tofu curry": "ĞºĞ°Ñ€Ñ€Ğ¸ Ñ� Ñ‚Ğ¾Ñ„Ñƒ",
    "vegetable curry": "Ğ¾Ğ²Ğ¾Ñ‰Ğ½Ğ¾Ğµ ĞºĞ°Ñ€Ñ€Ğ¸",
    "thai curry": "Ñ‚Ğ°Ğ¹Ñ�ĞºĞ¾Ğµ ĞºĞ°Ñ€Ñ€Ğ¸",
    "green curry": "Ğ·ĞµĞ»Ñ‘Ğ½Ğ¾Ğµ ĞºĞ°Ñ€Ñ€Ğ¸",
    "red curry": "ĞºÑ€Ğ°Ñ�Ğ½Ğ¾Ğµ ĞºĞ°Ñ€Ñ€Ğ¸",
    "yellow curry": "Ğ¶Ñ‘Ğ»Ñ‚Ğ¾Ğµ ĞºĞ°Ñ€Ñ€Ğ¸",
    "massaman curry": "Ğ¼Ğ°Ñ�Ñ�Ğ°Ğ¼Ğ°Ğ½ ĞºĞ°Ñ€Ñ€Ğ¸",
    "panang curry": "Ğ¿Ğ°Ğ½Ğ°Ğ½Ğ³ ĞºĞ°Ñ€Ñ€Ğ¸",
    "khao soi": "ĞºÑ…Ğ°Ğ¾ Ñ�Ğ¾Ğ¹",
    "pho": "Ñ„Ğ¾",
    "ramen": "Ñ€Ğ°Ğ¼ĞµĞ½",
    "udon": "ÑƒĞ´Ğ¾Ğ½",
    "soba": "Ñ�Ğ¾Ğ±Ğ°",
    "somen": "Ñ�Ğ¾Ğ¼Ñ�Ğ½",
    "rice noodles": "Ñ€Ğ¸Ñ�Ğ¾Ğ²Ğ°Ñ� Ğ»Ğ°Ğ¿ÑˆĞ°",
    "glass noodles": "Ñ�Ñ‚ĞµĞºĞ»Ñ�Ğ½Ğ½Ğ°Ñ� Ğ»Ğ°Ğ¿ÑˆĞ°",
    "vermicelli": "Ğ²ĞµÑ€Ğ¼Ğ¸ÑˆĞµĞ»ÑŒ",
    "fettuccine": "Ñ„ĞµÑ‚Ñ‚ÑƒÑ‡Ğ¸Ğ½Ğµ",
    "tagliatelle": "Ñ‚Ğ°Ğ»ÑŒÑ�Ñ‚ĞµĞ»Ğ»Ğµ",
    "pappardelle": "Ğ¿Ğ°Ğ¿Ğ¿Ğ°Ñ€Ğ´ĞµĞ»Ğ»Ğµ",
    "ravioli": "Ñ€Ğ°Ğ²Ğ¸Ğ¾Ğ»Ğ¸",
    "tortellini": "Ñ‚Ğ¾Ñ€Ñ‚ĞµĞ»Ğ»Ğ¸Ğ½Ğ¸",
    "gnocchi": "Ğ½ÑŒĞ¾ĞºĞºĞ¸",
    "spaetzle": "ÑˆĞ¿ĞµÑ†Ğ»Ğµ",
    "pierogi": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³Ğ¸ (Ğ¿Ğ¾Ğ»ÑŒÑ�ĞºĞ¸Ğµ)",
    "pelmeni": "Ğ¿ĞµĞ»ÑŒĞ¼ĞµĞ½Ğ¸",
    "vareniki": "Ğ²Ğ°Ñ€ĞµĞ½Ğ¸ĞºĞ¸",
    "kolduny": "ĞºĞ¾Ğ»Ğ´ÑƒĞ½Ñ‹",
    "zeppelini": "Ñ†ĞµĞ¿Ğ¿ĞµĞ»Ğ¸Ğ½Ñ‹",
    "cannelloni": "ĞºĞ°Ğ½Ğ½ĞµĞ»Ğ»Ğ¾Ğ½Ğ¸",
    "manicotti": "Ğ¼Ğ°Ğ½Ğ¸ĞºĞ¾Ñ‚Ñ‚Ğ¸",
    "stuffed shells": "Ñ„Ğ°Ñ€ÑˆĞ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ½Ñ‹Ğµ Ñ€Ğ°ĞºÑƒÑˆĞºĞ¸",
    "lasagna": "Ğ»Ğ°Ğ·Ğ°Ğ½ÑŒÑ�",
    "moussaka": "Ğ¼ÑƒÑ�Ğ°ĞºĞ°",
    "pastitsio": "Ğ¿Ğ°Ñ�Ñ‚Ğ¸Ñ†Ğ¸Ğ¾",
    "pie": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³",
    "quiche": "ĞºĞ¸Ñˆ",
    "tart": "Ñ‚Ğ°Ñ€Ñ‚",
    "flan": "Ñ„Ğ»Ğ°Ğ½",
    "clafoutis": "ĞºĞ»Ğ°Ñ„ÑƒÑ‚Ğ¸",
    "crumble": "ĞºÑ€Ğ°Ğ¼Ğ±Ğ»",
    "cobbler": "ĞºĞ¾Ğ±Ğ»ĞµÑ€",
    "pie with berries": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ñ�Ğ³Ğ¾Ğ´Ğ°Ğ¼Ğ¸",
    "pie with cherries": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ²Ğ¸ÑˆĞ½ĞµĞ¹",
    "pie with apples": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ñ�Ğ±Ğ»Ğ¾ĞºĞ°Ğ¼Ğ¸",
    "pie with peaches": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ¿ĞµÑ€Ñ�Ğ¸ĞºĞ°Ğ¼Ğ¸",
    "pie with pears": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ³Ñ€ÑƒÑˆĞ°Ğ¼Ğ¸",
    "pie with plums": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ�Ğ¾ Ñ�Ğ»Ğ¸Ğ²Ğ°Ğ¼Ğ¸",
    "pie with rhubarb": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ñ€ĞµĞ²ĞµĞ½ĞµĞ¼",
    "pie with custard": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ·Ğ°Ğ²Ğ°Ñ€Ğ½Ñ‹Ğ¼ ĞºÑ€ĞµĞ¼Ğ¾Ğ¼",
    "pie with cream": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ�Ğ¾ Ñ�Ğ»Ğ¸Ğ²ĞºĞ°Ğ¼Ğ¸",
    "pie with chocolate": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� ÑˆĞ¾ĞºĞ¾Ğ»Ğ°Ğ´Ğ¾Ğ¼",
    "pie with nuts": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ¾Ñ€ĞµÑ…Ğ°Ğ¼Ğ¸",
    "pie with almonds": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ¼Ğ¸Ğ½Ğ´Ğ°Ğ»Ñ‘Ğ¼",
    "pie with walnuts": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ³Ñ€ĞµÑ†ĞºĞ¸Ğ¼Ğ¸ Ğ¾Ñ€ĞµÑ…Ğ°Ğ¼Ğ¸",
    "pie with pecans": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ¿ĞµĞºĞ°Ğ½Ğ¾Ğ¼",
    "pie with pistachios": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ñ„Ğ¸Ñ�Ñ‚Ğ°ÑˆĞºĞ°Ğ¼Ğ¸",
    "pie with coconut": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� ĞºĞ¾ĞºĞ¾Ñ�Ğ¾Ğ¼",
    "pie with raisins": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ¸Ğ·Ñ�Ğ¼Ğ¾Ğ¼",
    "pie with dried apricots": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� ĞºÑƒÑ€Ğ°Ğ³Ğ¾Ğ¹",
    "pie with prunes": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ñ‡ĞµÑ€Ğ½Ğ¾Ñ�Ğ»Ğ¸Ğ²Ğ¾Ğ¼",
    "pie with dates": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ñ„Ğ¸Ğ½Ğ¸ĞºĞ°Ğ¼Ğ¸",
    "pie with figs": "пирог с семенами чиа",
    "pie with poppy seeds": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ğ¼Ğ°ĞºĞ¾Ğ¼",
    "pie with sesame seeds": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� ĞºÑƒĞ½Ğ¶ÑƒÑ‚Ğ¾Ğ¼",
    "pie with sunflower seeds": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ñ�ĞµĞ¼ĞµÑ‡ĞºĞ°Ğ¼Ğ¸",
    "pie with pumpkin seeds": "Ğ¿Ğ¸Ñ€Ğ¾Ğ³ Ñ� Ñ‚Ñ‹ĞºĞ²ĞµĞ½Ğ½Ñ‹Ğ¼Ğ¸ Ñ�ĞµĞ¼ĞµÑ‡ĞºĞ°Ğ¼Ğ¸",
    "pie with chia seeds": "пирог с семенами чиа",
}

# Кэш переводов
from collections import OrderedDict
import time

MAX_TRANSLATION_CACHE_SIZE = 1000
TRANSLATION_CACHE_TTL = 3600  # 1 hour in seconds

class LRUCache:
    """LRU Cache with TTL for translations"""
    def __init__(self, max_size: int, ttl: int):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
    
    def get(self, key: str) -> str:
        current_time = time.time()
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            if current_time - timestamp < self.ttl:
                # Move to the end (LRU)
                self.cache.move_to_end(key)
                return value
            else:
                # Expired cache, delete
                del self.cache[key]
        
        return None
    
    def put(self, key: str, value: str) -> None:
        current_time = time.time()
        
        # If the key already exists, update
        if key in self.cache:
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(key)
            return
        
        # Add a new key
        self.cache[key] = (value, current_time)
        
        # Check the cache size
        if len(self.cache) > self.max_size:
            # Delete the oldest element
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    def size(self) -> int:
        return len(self.cache)
    
    def clear(self) -> None:
        self.cache.clear()
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for cache checking"""
        return key in self.cache and self.get(key) is not None

_translation_cache = LRUCache(max_size=MAX_TRANSLATION_CACHE_SIZE, ttl=TRANSLATION_CACHE_TTL)

async def translate_to_russian(text: str) -> str:
    """
    ĞŸĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ¸Ñ‚ Ñ‚ĞµĞºÑ�Ñ‚ Ñ� Ğ°Ğ½Ğ³Ğ»Ğ¸Ğ¹Ñ�ĞºĞ¾Ğ³Ğ¾ Ğ½Ğ° Ñ€ÑƒÑ�Ñ�ĞºĞ¸Ğ¹ Ñ� Ğ¿Ñ€Ğ¸Ğ¾Ñ€Ğ¸Ñ‚ĞµÑ‚Ğ¾Ğ¼ Ğ»Ğ¾ĞºĞ°Ğ»ÑŒĞ½Ğ¾Ğ³Ğ¾ Ğ¼Ğ°Ğ¿Ğ¿Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ñ�.
    """
    if not isinstance(text, str) or not text.strip():
        return "Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ¾"
    
    original = text.strip()
    text_lower = original.lower()
    
    # 1. ĞŸÑ€Ğ¾Ğ²ĞµÑ€ĞºĞ° ĞºÑ�ÑˆĞ°
    if text_lower in _translation_cache:
        return _translation_cache.get(text_lower)
    
    # 2. ĞŸÑ€Ñ�Ğ¼Ğ¾Ğµ Ğ¼Ğ°Ğ¿Ğ¿Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ AI â†’ Ğ±Ğ°Ğ·Ğ° (ĞŸĞ Ğ˜Ğ�Ğ Ğ˜Ğ¢Ğ•Ğ¢)
    if text_lower in AI_TO_DB_MAPPING:
        translated = AI_TO_DB_MAPPING[text_lower]
        _translation_cache.put(text_lower, translated)
        logger.info(f"âœ¨ AI Mapping: '{original}' â†’ '{translated}'")
        return translated
    
    # 3. ĞŸĞ¾Ğ¸Ñ�Ğº Ğ¿Ğ¾ Ğ¿Ğ¾Ğ»Ğ½Ğ¾Ğ¼Ñƒ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ñ� Ğ² Ğ¼Ğ°Ğ¿Ğ¿Ğ¸Ğ½Ğ³Ğµ (Ğ±Ğ¾Ğ»ĞµĞµ Ñ�Ñ‚Ñ€Ğ¾Ğ³Ğ¸Ğ¹)
    for key, value in AI_TO_DB_MAPPING.items():
        if key == text_lower:  # Ğ¢Ğ¾Ğ»ÑŒĞºĞ¾ Ğ¿Ğ¾Ğ»Ğ½Ğ¾Ğµ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ğµ
            _translation_cache.put(text_lower, value)
            logger.info(f"âœ¨ Exact AI Mapping: '{original}' â†’ '{value}'")
            return value
    
    # 4. Google Translate (fallback) - Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ ĞµÑ�Ğ»Ğ¸ Ğ½ĞµÑ‚ Ğ¿Ğ¾Ğ»Ğ½Ğ¾Ğ³Ğ¾ Ñ�Ğ¾Ğ²Ğ¿Ğ°Ğ´ĞµĞ½Ğ¸Ñ�
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target='ru')
        translated = translator.translate(original)
        if translated and translated != original:
            _translation_cache.put(text_lower, translated)
            logger.info(f"ğŸŒ� Google: '{original}' â†’ '{translated}'")
            return translated
    except Exception as e:
        logger.warning(f"âš ï¸� Google Translate error: {e}")
    
    # 5. Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‚ Ğ¾Ñ€Ğ¸Ğ³Ğ¸Ğ½Ğ°Ğ»Ğ°
    logger.warning(f"âš ï¸� No translation for: '{original}'")
    return original

async def translate_dish_name(english_name: str) -> str:
    """
    ĞŸĞµÑ€ĞµĞ²Ğ¾Ğ´Ğ¸Ñ‚ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ±Ğ»Ñ�Ğ´Ğ° Ñ� Ğ¿Ñ€Ğ¸Ğ¾Ñ€Ğ¸Ñ‚ĞµÑ‚Ğ¾Ğ¼ Ğ½Ğ° Ğ¿Ñ€Ñ�Ğ¼Ğ¾Ğµ Ğ¼Ğ°Ğ¿Ğ¿Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ.
    """
    if not english_name or not isinstance(english_name, str):
        return "Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ¾Ğµ Ğ±Ğ»Ñ�Ğ´Ğ¾"
    
    return await translate_to_russian(english_name)

async def translate_smart_dish_name(english_name: str) -> str:
    """
    Ğ£Ğ¼Ğ½Ñ‹Ğ¹ Ğ¿ĞµÑ€ĞµĞ²Ğ¾Ğ´ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ� Ğ±Ğ»Ñ�Ğ´Ğ°:
    1. Ğ¡Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ° Ğ¿Ñ€Ğ¾Ğ±ÑƒĞµĞ¼ Ğ¿Ñ€Ñ�Ğ¼Ğ¾Ğµ Ğ¼Ğ°Ğ¿Ğ¿Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ
    2. Ğ•Ñ�Ğ»Ğ¸ Ğ½ĞµÑ‚ - Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Google Translate Ğ´Ğ»Ñ� Ñ�Ğ»Ğ¾Ğ¶Ğ½Ñ‹Ñ… Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğ¹
    """
    if not english_name or not isinstance(english_name, str):
        return "Ğ�ĞµĞ¸Ğ·Ğ²ĞµÑ�Ñ‚Ğ½Ğ¾Ğµ Ğ±Ğ»Ñ�Ğ´Ğ¾"
    
    original = english_name.strip()
    text_lower = original.lower()
    
    # 1. ĞŸÑ€Ğ¾Ğ²ĞµÑ€ĞºĞ° ĞºÑ�ÑˆĞ°
    if text_lower in _translation_cache:
        return _translation_cache[text_lower]
    
    # 2. ĞŸÑ€Ñ�Ğ¼Ğ¾Ğµ Ğ¼Ğ°Ğ¿Ğ¿Ğ¸Ñ€Ğ¾Ğ²Ğ°Ğ½Ğ¸Ğµ AI â†’ Ğ±Ğ°Ğ·Ğ° (ĞŸĞ Ğ˜Ğ�Ğ Ğ˜Ğ¢Ğ•Ğ¢)
    if text_lower in AI_TO_DB_MAPPING:
        translated = AI_TO_DB_MAPPING[text_lower]
        _translation_cache.put(text_lower, translated)
        logger.info(f"ğŸ”„ Dish AI Mapping: '{original}' â†’ '{translated}'")
        return translated
    
    # 3. Ğ”Ğ»Ñ� Ñ�Ğ»Ğ¾Ğ¶Ğ½Ñ‹Ñ… Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğ¹ Ğ±Ğ»Ñ�Ğ´ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Google Translate
    if len(original.split()) > 2:  # Ğ•Ñ�Ğ»Ğ¸ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ğ¸Ñ‚ Ğ¸Ğ· 3+ Ñ�Ğ»Ğ¾Ğ²
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='en', target='ru')
            translated = translator.translate(original)
            if translated and translated != original:
                _translation_cache.put(text_lower, translated)
                logger.info(f"ğŸŒ� Google Dish: '{original}' â†’ '{translated}'")
                return translated
        except Exception as e:
            logger.warning(f"âš ï¸� Google Translate error for dish: {e}")
    
    # 4. Ğ’Ğ¾Ğ·Ğ²Ñ€Ğ°Ñ‚ Ğ¾Ñ€Ğ¸Ğ³Ğ¸Ğ½Ğ°Ğ»Ğ°
    logger.warning(f"âš ï¸� No translation for dish: '{original}'")
    return original
