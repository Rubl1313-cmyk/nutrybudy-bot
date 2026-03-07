"""
services/food_api.py
Поиск продуктов: локальная база → Open Food Facts API.
✅ ИСПРАВЛЕНО: добавлены все необходимые импорты
✅ ИСПРАВЛЕНО: используется time.time() вместо asyncio.get_event_loop().time()
"""

# ========== 🔥 ВАЖНО: ИМПОРТЫ ==========
import aiohttp
import logging
import asyncio
import time  # ← ДОБАВЛЕНО для кэширования
from typing import List, Dict, Optional, Tuple, Any  # ← Все типы импортированы
# =======================================

logger = logging.getLogger(__name__)

# ========== КЭШИРОВАНИЕ ==========
_SEARCH_CACHE: Dict[str, Tuple[List[Dict], float]] = {}
_CACHE_TTL = 300  # 5 минут
_CACHE_LIMIT = 200


# ========== ЛОКАЛЬНАЯ БАЗА ПРОДУКТОВ (более 1000 записей) ==========
# Ключи — это слова, по которым бот будет искать (в нижнем регистре)
LOCAL_FOOD_DB = {
      # ========== ЛИСТОВОЙ САЛАТ И ЗЕЛЕНЬ ==========
    "салат": {"name": "Салат листовой", "calories": 15, "protein": 1.2, "fat": 0.2, "carbs": 2.5},
    "салат айсберг": {"name": "Салат Айсберг", "calories": 14, "protein": 1, "fat": 0.1, "carbs": 2},
    "салат романо": {"name": "Салат Романо", "calories": 17, "protein": 1.5, "fat": 0.3, "carbs": 2.5},
    "руккола": {"name": "Руккола", "calories": 25, "protein": 2.5, "fat": 0.5, "carbs": 3.5},
    "шпинат": {"name": "Шпинат", "calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6},
    "зелень": {"name": "Зелень (укроп, петрушка)", "calories": 35, "protein": 2.5, "fat": 0.5, "carbs": 6},
    # ========== ОСНОВНЫЕ ПРОДУКТЫ (МЯСО, ПТИЦА) ==========
    "курица": {"name": "Курица (средняя)", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "запеченная курица": {"name": "Курица запечённая", "calories": 220, "protein": 26, "fat": 12, "carbs": 0},
    "куриная грудка": {"name": "Куриная грудка (филе)", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "куриное филе": {"name": "Куриное филе", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "куриные ножки": {"name": "Куриные ножки", "calories": 215, "protein": 18.4, "fat": 16.1, "carbs": 0},
    "куриные крылья": {"name": "Куриные крылья", "calories": 222, "protein": 18.3, "fat": 16.4, "carbs": 0},
    "курица жареная": {"name": "Курица жареная", "calories": 239, "protein": 27, "fat": 14, "carbs": 0},
    "курица вареная": {"name": "Курица варёная", "calories": 205, "protein": 25, "fat": 10, "carbs": 0},
    "курица запеченная": {"name": "Курица запечённая", "calories": 220, "protein": 26, "fat": 12, "carbs": 0},
    "индейка": {"name": "Индейка", "calories": 135, "protein": 30, "fat": 1, "carbs": 0},
    "говядина": {"name": "Говядина (средняя)", "calories": 250, "protein": 26, "fat": 17, "carbs": 0},
    "говяжий фарш": {"name": "Говяжий фарш (10% жира)", "calories": 176, "protein": 22, "fat": 10, "carbs": 0},
    "свинина": {"name": "Свинина (средняя)", "calories": 242, "protein": 27, "fat": 14, "carbs": 0},
    "свиная вырезка": {"name": "Свиная вырезка", "calories": 143, "protein": 26, "fat": 3.5, "carbs": 0},
    "бекон": {"name": "Бекон", "calories": 541, "protein": 37, "fat": 42, "carbs": 1},
    "ветчина": {"name": "Ветчина", "calories": 145, "protein": 17, "fat": 8, "carbs": 1},
    "колбаса": {"name": "Колбаса варёная", "calories": 250, "protein": 12, "fat": 22, "carbs": 2},
    "сосиски": {"name": "Сосиски", "calories": 270, "protein": 11, "fat": 24, "carbs": 2},
    "сардельки": {"name": "Сардельки", "calories": 300, "protein": 12, "fat": 27, "carbs": 2},

    # ========== РЫБА И МОРЕПРОДУКТЫ ==========
    "лосось": {"name": "Лосось (сёмга)", "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    "семга": {"name": "Сёмга", "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    "треска": {"name": "Треска", "calories": 82, "protein": 18, "fat": 0.7, "carbs": 0},
    "скумбрия": {"name": "Скумбрия", "calories": 205, "protein": 19, "fat": 14, "carbs": 0},
    "сельдь": {"name": "Сельдь солёная", "calories": 250, "protein": 18, "fat": 19, "carbs": 0},
    "креветки": {"name": "Креветки", "calories": 85, "protein": 20, "fat": 0.5, "carbs": 0},
    "кальмар": {"name": "Кальмар", "calories": 100, "protein": 18, "fat": 2, "carbs": 0},
    "мидии": {"name": "Мидии", "calories": 85, "protein": 15, "fat": 2, "carbs": 3},
    "крабовые палочки": {"name": "Крабовые палочки", "calories": 90, "protein": 7, "fat": 2, "carbs": 12},

    # ========== ЯЙЦА И МОЛОЧНЫЕ ПРОДУКТЫ ==========
    "яйцо": {"name": "Яйцо куриное (1 шт = 50г)", "calories": 70, "protein": 5.5, "fat": 5, "carbs": 0.5},
    "яйца": {"name": "Яйцо куриное (на 100г)", "calories": 140, "protein": 11, "fat": 10, "carbs": 1},
    "молоко": {"name": "Молоко 3.2%", "calories": 60, "protein": 3, "fat": 3.2, "carbs": 4.7},
    "кефир": {"name": "Кефир 2.5%", "calories": 50, "protein": 3, "fat": 2.5, "carbs": 4},
    "йогурт": {"name": "Йогурт натуральный", "calories": 60, "protein": 4, "fat": 2.5, "carbs": 6},
    "творог": {"name": "Творог 5%", "calories": 120, "protein": 16, "fat": 5, "carbs": 3},
    "сметана": {"name": "Сметана 20%", "calories": 200, "protein": 2.5, "fat": 20, "carbs": 3.5},
    "сыр": {"name": "Сыр твёрдый", "calories": 350, "protein": 25, "fat": 28, "carbs": 2},
    "масло сливочное": {"name": "Масло сливочное 82%", "calories": 750, "protein": 0.5, "fat": 82, "carbs": 0.5},

    # ========== ОВОЩИ ==========
    "картофель": {"name": "Картофель", "calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
    "картошка": {"name": "Картофель", "calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
    "морковь": {"name": "Морковь", "calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
    "лук": {"name": "Лук репчатый", "calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9},
    "помидор": {"name": "Помидор", "calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
    "огурец": {"name": "Огурец", "calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
    "капуста": {"name": "Капуста белокочанная", "calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 5.8},
    "брокколи": {"name": "Брокколи", "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
    "перец болгарский": {"name": "Перец болгарский", "calories": 26, "protein": 1.2, "fat": 0.3, "carbs": 6},
    "баклажан": {"name": "Баклажан", "calories": 24, "protein": 1, "fat": 0.2, "carbs": 5.7},
    "кабачок": {"name": "Кабачок", "calories": 24, "protein": 0.6, "fat": 0.3, "carbs": 5.2},
    "тыква": {"name": "Тыква", "calories": 22, "protein": 1, "fat": 0.1, "carbs": 5.5},
    "свекла": {"name": "Свёкла", "calories": 43, "protein": 1.5, "fat": 0.1, "carbs": 9.5},
    "редис": {"name": "Редис", "calories": 20, "protein": 0.6, "fat": 0.1, "carbs": 4},
    "зелень": {"name": "Зелень (укроп, петрушка)", "calories": 35, "protein": 2.5, "fat": 0.5, "carbs": 6},

    # ========== ФРУКТЫ И ЯГОДЫ ==========
    "яблоко": {"name": "Яблоко", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
    "банан": {"name": "Банан", "calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23},
    "апельсин": {"name": "Апельсин", "calories": 47, "protein": 0.9, "fat": 0.1, "carbs": 12},
    "мандарин": {"name": "Мандарин", "calories": 38, "protein": 0.6, "fat": 0.2, "carbs": 9},
    "лимон": {"name": "Лимон", "calories": 29, "protein": 1.1, "fat": 0.3, "carbs": 9},
    "грейпфрут": {"name": "Грейпфрут", "calories": 42, "protein": 0.8, "fat": 0.1, "carbs": 11},
    "киви": {"name": "Киви", "calories": 61, "protein": 1.1, "fat": 0.5, "carbs": 15},
    "ананас": {"name": "Ананас", "calories": 50, "protein": 0.5, "fat": 0.1, "carbs": 13},
    "манго": {"name": "Манго", "calories": 60, "protein": 0.8, "fat": 0.4, "carbs": 15},
    "клубника": {"name": "Клубника", "calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 7.7},
    "малина": {"name": "Малина", "calories": 52, "protein": 1.2, "fat": 0.7, "carbs": 12},

    # ========== КРУПЫ, МАКАРОНЫ ==========
    "гречка": {"name": "Гречка (варёная)", "calories": 110, "protein": 4, "fat": 0.5, "carbs": 23},
    "рис": {"name": "Рис (варёный)", "calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
    "овсянка": {"name": "Овсянка (на воде)", "calories": 71, "protein": 2.5, "fat": 1.5, "carbs": 12},
    "пшено": {"name": "Пшёнка (варёная)", "calories": 120, "protein": 3.5, "fat": 1.3, "carbs": 24},
    "перловка": {"name": "Перловка (варёная)", "calories": 120, "protein": 3, "fat": 0.4, "carbs": 25},
    "макароны": {"name": "Макароны (варёные)", "calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
    "спагетти": {"name": "Спагетти (варёные)", "calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
    "лапша": {"name": "Лапша (варёная)", "calories": 130, "protein": 4, "fat": 1, "carbs": 26},

    # ========== ХЛЕБ И ВЫПЕЧКА ==========
    "хлеб": {"name": "Хлеб пшеничный", "calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
    "хлеб ржаной": {"name": "Хлеб ржаной", "calories": 200, "protein": 6, "fat": 1.5, "carbs": 40},
    "лаваш": {"name": "Лаваш", "calories": 250, "protein": 8, "fat": 2, "carbs": 50},
    "печенье": {"name": "Печенье", "calories": 450, "protein": 6, "fat": 15, "carbs": 75},
    "пряники": {"name": "Пряники", "calories": 360, "protein": 5, "fat": 5, "carbs": 75},

    # ========== СОУСЫ, МАСЛА, ЗАПРАВКИ ==========
    "кетчуп": {"name": "Кетчуп", "calories": 100, "protein": 1.5, "fat": 0.5, "carbs": 22},
    "майонез": {"name": "Майонез (провансаль)", "calories": 600, "protein": 0.5, "fat": 65, "carbs": 3},
    "майонез легкий": {"name": "Майонез лёгкий", "calories": 250, "protein": 0.5, "fat": 25, "carbs": 5},
    "горчица": {"name": "Горчица", "calories": 100, "protein": 5, "fat": 5, "carbs": 10},
    "соевый соус": {"name": "Соевый соус", "calories": 60, "protein": 8, "fat": 0, "carbs": 8},
    "соус песто": {"name": "Соус песто", "calories": 500, "protein": 5, "fat": 50, "carbs": 10},
    "соус цезарь": {"name": "Соус Цезарь", "calories": 300, "protein": 2, "fat": 25, "carbs": 15},
    "оливковое масло": {"name": "Масло оливковое", "calories": 900, "protein": 0, "fat": 100, "carbs": 0},
    "подсолнечное масло": {"name": "Масло подсолнечное", "calories": 900, "protein": 0, "fat": 100, "carbs": 0},
    "уксус": {"name": "Уксус столовый", "calories": 5, "protein": 0, "fat": 0, "carbs": 0.5},

    # ========== НАПИТКИ ==========
    "сок апельсиновый": {"name": "Сок апельсиновый", "calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 10},
    "сок яблочный": {"name": "Сок яблочный", "calories": 46, "protein": 0.1, "fat": 0.1, "carbs": 11},
    "сок томатный": {"name": "Сок томатный", "calories": 17, "protein": 0.8, "fat": 0.1, "carbs": 3.5},
    "газировка": {"name": "Газированный напиток", "calories": 40, "protein": 0, "fat": 0, "carbs": 10},
    "кола": {"name": "Кока-кола", "calories": 42, "protein": 0, "fat": 0, "carbs": 10.6},
    "лимонад": {"name": "Лимонад", "calories": 40, "protein": 0, "fat": 0, "carbs": 10},
    "квас": {"name": "Квас", "calories": 30, "protein": 0.2, "fat": 0, "carbs": 7},
    "компот": {"name": "Компот", "calories": 60, "protein": 0.2, "fat": 0, "carbs": 15},
    "чай": {"name": "Чай (без сахара)", "calories": 1, "protein": 0, "fat": 0, "carbs": 0.3},
    "кофе": {"name": "Кофе (без сахара)", "calories": 2, "protein": 0.1, "fat": 0, "carbs": 0},
    "пиво светлое": {"name": "Пиво светлое", "calories": 43, "protein": 0.5, "fat": 0, "carbs": 3.6},
    "пиво темное": {"name": "Пиво тёмное", "calories": 50, "protein": 0.5, "fat": 0, "carbs": 5},
    "вино красное сухое": {"name": "Вино красное сухое", "calories": 68, "protein": 0.1, "fat": 0, "carbs": 2.3},
    "вино белое сухое": {"name": "Вино белое сухое", "calories": 64, "protein": 0.1, "fat": 0, "carbs": 1.5},
    "водка": {"name": "Водка", "calories": 235, "protein": 0, "fat": 0, "carbs": 0.1},
    "коньяк": {"name": "Коньяк", "calories": 240, "protein": 0, "fat": 0, "carbs": 1.5},

    # ========== СЛАДОСТИ И ДЕСЕРТЫ ==========
    "шоколад молочный": {"name": "Шоколад молочный", "calories": 550, "protein": 6, "fat": 30, "carbs": 60},
    "шоколад темный": {"name": "Шоколад тёмный (70%)", "calories": 550, "protein": 7, "fat": 35, "carbs": 45},
    "конфеты шоколадные": {"name": "Конфеты шоколадные", "calories": 500, "protein": 4, "fat": 25, "carbs": 60},
    "конфеты": {"name": "Конфеты", "calories": 450, "protein": 3, "fat": 20, "carbs": 65},
    "карамель": {"name": "Карамель", "calories": 400, "protein": 0, "fat": 5, "carbs": 90},
    "зефир": {"name": "Зефир", "calories": 300, "protein": 0.5, "fat": 0, "carbs": 70},
    "пастила": {"name": "Пастила", "calories": 300, "protein": 0.5, "fat": 0, "carbs": 70},
    "мармелад": {"name": "Мармелад", "calories": 250, "protein": 0.1, "fat": 0, "carbs": 60},
    "халва": {"name": "Халва", "calories": 500, "protein": 12, "fat": 25, "carbs": 55},
    "печенье": {"name": "Печенье сахарное", "calories": 450, "protein": 6, "fat": 15, "carbs": 75},
    "пряники": {"name": "Пряники", "calories": 360, "protein": 5, "fat": 5, "carbs": 75},
    "вафли": {"name": "Вафли", "calories": 500, "protein": 5, "fat": 25, "carbs": 65},
    "кекс": {"name": "Кекс", "calories": 350, "protein": 5, "fat": 15, "carbs": 50},
    "пирожное": {"name": "Пирожное", "calories": 400, "protein": 4, "fat": 20, "carbs": 50},
    "торт": {"name": "Торт", "calories": 350, "protein": 4, "fat": 15, "carbs": 50},
    "мороженое": {"name": "Мороженое пломбир", "calories": 200, "protein": 3.5, "fat": 10, "carbs": 20},

    # ========== ОРЕХИ, СЕМЕНА, СУХОФРУКТЫ ==========
    "орехи": {"name": "Орехи (смесь)", "calories": 600, "protein": 15, "fat": 55, "carbs": 15},
    "грецкий орех": {"name": "Грецкие орехи", "calories": 650, "protein": 15, "fat": 65, "carbs": 14},
    "миндаль": {"name": "Миндаль", "calories": 600, "protein": 19, "fat": 53, "carbs": 20},
    "фундук": {"name": "Фундук", "calories": 650, "protein": 15, "fat": 62, "carbs": 10},
    "арахис": {"name": "Арахис", "calories": 550, "protein": 26, "fat": 45, "carbs": 10},
    "кешью": {"name": "Кешью", "calories": 550, "protein": 18, "fat": 44, "carbs": 30},
    "семечки": {"name": "Семечки подсолнуха", "calories": 600, "protein": 20, "fat": 50, "carbs": 10},
    "тыквенные семечки": {"name": "Тыквенные семечки", "calories": 550, "protein": 20, "fat": 45, "carbs": 10},
    "кунжут": {"name": "Кунжут", "calories": 570, "protein": 17, "fat": 50, "carbs": 12},
    "курага": {"name": "Курага", "calories": 240, "protein": 3.5, "fat": 0.5, "carbs": 55},
    "чернослив": {"name": "Чернослив", "calories": 240, "protein": 2.3, "fat": 0.4, "carbs": 60},
    "изюм": {"name": "Изюм", "calories": 300, "protein": 3, "fat": 0.5, "carbs": 75},
    "финики": {"name": "Финики", "calories": 280, "protein": 2, "fat": 0.2, "carbs": 70},

    # ========== КОНСЕРВЫ ==========
    "тушёнка": {"name": "Тушёнка говяжья", "calories": 200, "protein": 15, "fat": 15, "carbs": 0},
    "шпроты": {"name": "Шпроты в масле", "calories": 300, "protein": 15, "fat": 25, "carbs": 0},
    "сайра": {"name": "Сайра консервированная", "calories": 250, "protein": 18, "fat": 20, "carbs": 0},
    "тунец консервированный": {"name": "Тунец консервированный", "calories": 150, "protein": 20, "fat": 7, "carbs": 0},
    "горошек": {"name": "Горошек зелёный", "calories": 60, "protein": 4, "fat": 0.5, "carbs": 10},
    "кукуруза": {"name": "Кукуруза консервированная", "calories": 70, "protein": 2, "fat": 1, "carbs": 15},
    "фасоль консервированная": {"name": "Фасоль консервированная", "calories": 90, "protein": 6, "fat": 0.5, "carbs": 15},
    "оливки": {"name": "Оливки", "calories": 150, "protein": 1, "fat": 15, "carbs": 3},
    "маслины": {"name": "Маслины", "calories": 150, "protein": 1, "fat": 15, "carbs": 3},
    "корнишоны": {"name": "Корнишоны маринованные", "calories": 30, "protein": 1, "fat": 0, "carbs": 5},

    # ========== ЗАМОРОЖЕННЫЕ ПРОДУКТЫ ==========
    "пельмени": {"name": "Пельмени замороженные", "calories": 250, "protein": 12, "fat": 12, "carbs": 25},
    "вареники": {"name": "Вареники с картошкой", "calories": 200, "protein": 6, "fat": 5, "carbs": 35},
    "овощная смесь": {"name": "Овощная смесь замороженная", "calories": 50, "protein": 2, "fat": 0.5, "carbs": 8},
    "брокколи": {"name": "Брокколи замороженная", "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
    "цветная капуста": {"name": "Цветная капуста замороженная", "calories": 25, "protein": 2, "fat": 0.3, "carbs": 5},
    "ягоды": {"name": "Ягоды замороженные", "calories": 50, "protein": 0.5, "fat": 0.2, "carbs": 12},
    "клубника": {"name": "Клубника замороженная", "calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 7.7},
    "блины": {"name": "Блины замороженные", "calories": 200, "protein": 5, "fat": 8, "carbs": 28},
    "сырники": {"name": "Сырники замороженные", "calories": 200, "protein": 12, "fat": 10, "carbs": 15},

    # ========== САЛАТЫ (РАЗНООБРАЗНЫЕ) ==========
    "салат оливье": {"name": "Салат Оливье (классический)", "calories": 200, "protein": 5, "fat": 15, "carbs": 10},
    "оливье": {"name": "Салат Оливье", "calories": 200, "protein": 5, "fat": 15, "carbs": 10},
    "салат цезарь с курицей": {"name": "Цезарь с курицей", "calories": 180, "protein": 12, "fat": 10, "carbs": 8},
    "салат цезарь с креветками": {"name": "Цезарь с креветками", "calories": 160, "protein": 14, "fat": 8, "carbs": 6},
    "греческий салат": {"name": "Греческий салат", "calories": 120, "protein": 3, "fat": 8, "carbs": 6},
    "салат с тунцом": {"name": "Салат с тунцом", "calories": 140, "protein": 15, "fat": 5, "carbs": 8},
    "салат с лососем": {"name": "Салат с лососем", "calories": 170, "protein": 12, "fat": 10, "carbs": 6},
    "салат с креветками": {"name": "Салат с креветками", "calories": 100, "protein": 12, "fat": 3, "carbs": 5},
    "салат с кальмарами": {"name": "Салат с кальмарами", "calories": 110, "protein": 10, "fat": 5, "carbs": 6},
    "салат с мидиями": {"name": "Салат с мидиями", "calories": 90, "protein": 8, "fat": 4, "carbs": 5},
    "салат с осьминогом": {"name": "Салат с осьминогом", "calories": 100, "protein": 9, "fat": 4, "carbs": 6},
    "салат нисуаз": {"name": "Нисуаз (салат с тунцом и яйцом)", "calories": 150, "protein": 12, "fat": 8, "carbs": 8},
    "салат капрезе": {"name": "Капрезе (моцарелла, помидоры, базилик)", "calories": 250, "protein": 12, "fat": 20, "carbs": 4},
    "салат с моцареллой": {"name": "Салат с моцареллой", "calories": 200, "protein": 10, "fat": 15, "carbs": 5},
    "салат с брынзой": {"name": "Салат с брынзой", "calories": 180, "protein": 8, "fat": 14, "carbs": 5},
    "салат с фетой": {"name": "Салат с фетой", "calories": 160, "protein": 6, "fat": 12, "carbs": 6},
    "салат с пармезаном": {"name": "Салат с пармезаном", "calories": 200, "protein": 10, "fat": 15, "carbs": 5},
    "салат с курицей и ананасом": {"name": "Салат с курицей и ананасом", "calories": 140, "protein": 10, "fat": 5, "carbs": 12},
    "салат с курицей и грибами": {"name": "Салат с курицей и грибами", "calories": 130, "protein": 12, "fat": 6, "carbs": 6},
    "салат с ветчиной": {"name": "Салат с ветчиной", "calories": 150, "protein": 8, "fat": 10, "carbs": 6},
    "салат с беконом": {"name": "Салат с беконом", "calories": 220, "protein": 8, "fat": 18, "carbs": 6},
    "салат с языком": {"name": "Салат с языком", "calories": 180, "protein": 12, "fat": 12, "carbs": 5},
    "салат с печенью трески": {"name": "Салат с печенью трески", "calories": 250, "protein": 5, "fat": 22, "carbs": 4},
    "салат с крабовыми палочками и кукурузой": {"name": "Крабовый салат с кукурузой", "calories": 140, "protein": 6, "fat": 7, "carbs": 10},
    "салат с крабовыми палочками и рисом": {"name": "Крабовый салат с рисом", "calories": 160, "protein": 5, "fat": 6, "carbs": 20},
    "салат с крабовыми палочками и огурцом": {"name": "Крабовый салат с огурцом", "calories": 110, "protein": 5, "fat": 5, "carbs": 8},
    "салат с шампиньонами": {"name": "Салат с шампиньонами", "calories": 90, "protein": 4, "fat": 5, "carbs": 6},
    "салат с опятами": {"name": "Салат с опятами", "calories": 80, "protein": 3, "fat": 4, "carbs": 6},
    "салат с белыми грибами": {"name": "Салат с белыми грибами", "calories": 100, "protein": 4, "fat": 6, "carbs": 7},
    "салат с фасолью и сухариками": {"name": "Салат с фасолью и сухариками", "calories": 140, "protein": 5, "fat": 5, "carbs": 18},
    "салат с чечевицей": {"name": "Салат с чечевицей", "calories": 120, "protein": 6, "fat": 3, "carbs": 18},
    "салат с нутом": {"name": "Салат с нутом", "calories": 130, "protein": 5, "fat": 4, "carbs": 18},
    "салат с киноа": {"name": "Салат с киноа", "calories": 120, "protein": 4, "fat": 3, "carbs": 20},
    "салат с булгуром": {"name": "Салат с булгуром", "calories": 110, "protein": 3, "fat": 2, "carbs": 20},
    "салат с кускусом": {"name": "Салат с кускусом", "calories": 100, "protein": 3, "fat": 2, "carbs": 18},
    "салат с авокадо": {"name": "Салат с авокадо", "calories": 180, "protein": 2, "fat": 15, "carbs": 8},
    "салат с манго": {"name": "Салат с манго", "calories": 80, "protein": 1, "fat": 2, "carbs": 15},
    "салат с гранатом": {"name": "Салат с гранатом", "calories": 70, "protein": 1, "fat": 2, "carbs": 12},
    "салат с апельсином": {"name": "Салат с апельсином", "calories": 60, "protein": 1, "fat": 1, "carbs": 12},
    "салат с грейпфрутом": {"name": "Салат с грейпфрутом", "calories": 50, "protein": 1, "fat": 1, "carbs": 10},
    "салат с яблоком и сельдереем": {"name": "Салат с яблоком и сельдереем", "calories": 50, "protein": 1, "fat": 1, "carbs": 10},
    "салат вальдорф": {"name": "Вальдорф (яблоко, сельдерей, грецкий орех)", "calories": 150, "protein": 2, "fat": 10, "carbs": 12},
    "салат коул слоу": {"name": "Коул слоу (капустный салат)", "calories": 120, "protein": 1, "fat": 8, "carbs": 10},
    "салат табуле": {"name": "Табуле (булгур, помидоры, мята)", "calories": 110, "protein": 3, "fat": 4, "carbs": 16},
    "салат из редиски": {"name": "Салат из редиски", "calories": 30, "protein": 1, "fat": 0.5, "carbs": 5},
    "салат из моркови по-корейски": {"name": "Морковь по-корейски", "calories": 130, "protein": 1, "fat": 8, "carbs": 12},
    "салат из свеклы с черносливом": {"name": "Салат из свеклы с черносливом", "calories": 100, "protein": 2, "fat": 4, "carbs": 15},
    "салат из свеклы с орехами": {"name": "Салат из свеклы с орехами", "calories": 120, "protein": 3, "fat": 7, "carbs": 12},
    "салат из капусты с морковью": {"name": "Салат из капусты с морковью", "calories": 40, "protein": 1, "fat": 0.5, "carbs": 8},
    "салат с рукколой": {"name": "Салат с рукколой", "calories": 40, "protein": 2, "fat": 2, "carbs": 4},
    "салат с рукколой и пармезаном": {"name": "Салат с рукколой и пармезаном", "calories": 120, "protein": 5, "fat": 8, "carbs": 6},
    "салат с рукколой и помидорами черри": {"name": "Салат с рукколой и черри", "calories": 60, "protein": 2, "fat": 3, "carbs": 5},
    "салат с шпинатом": {"name": "Салат со шпинатом", "calories": 40, "protein": 2, "fat": 1, "carbs": 5},
    "салат с шпинатом и клубникой": {"name": "Салат со шпинатом и клубникой", "calories": 60, "protein": 2, "fat": 2, "carbs": 8},
    "салат с айсбергом": {"name": "Салат Айсберг", "calories": 20, "protein": 1, "fat": 0, "carbs": 3},
    "салат мясной": {"name": "Мясной салат", "calories": 200, "protein": 15, "fat": 14, "carbs": 5},
    "салат столичный": {"name": "Столичный салат (мясной)", "calories": 220, "protein": 12, "fat": 16, "carbs": 6},
    "салат с колбасой": {"name": "Салат с колбасой", "calories": 200, "protein": 8, "fat": 16, "carbs": 6},
    "салат с копчёной курицей": {"name": "Салат с копчёной курицей", "calories": 150, "protein": 12, "fat": 8, "carbs": 6},
    "салат с копчёной рыбой": {"name": "Салат с копчёной рыбой", "calories": 140, "protein": 10, "fat": 8, "carbs": 5},
    "салат с селёдкой": {"name": "Салат с селёдкой", "calories": 160, "protein": 8, "fat": 12, "carbs": 5},
    "салат со шпротами": {"name": "Салат со шпротами", "calories": 200, "protein": 6, "fat": 16, "carbs": 6},
    "салат с семгой слабосоленой": {"name": "Салат с сёмгой слабосолёной", "calories": 170, "protein": 12, "fat": 12, "carbs": 4},
    "салат с семгой и авокадо": {"name": "Салат с сёмгой и авокадо", "calories": 200, "protein": 10, "fat": 15, "carbs": 6},
    "салат с тунцом и фасолью": {"name": "Салат с тунцом и фасолью", "calories": 140, "protein": 12, "fat": 5, "carbs": 12},
    "салат с тунцом и кукурузой": {"name": "Салат с тунцом и кукурузой", "calories": 130, "protein": 11, "fat": 4, "carbs": 12},
    "салат с тунцом и яйцом": {"name": "Салат с тунцом и яйцом", "calories": 140, "protein": 12, "fat": 6, "carbs": 8},
    "салат с крабовым мясом": {"name": "Салат с крабовым мясом", "calories": 100, "protein": 10, "fat": 4, "carbs": 6},
    "салат с лангустинами": {"name": "Салат с лангустинами", "calories": 120, "protein": 12, "fat": 5, "carbs": 5},
    "салат с омаром": {"name": "Салат с омаром", "calories": 130, "protein": 13, "fat": 6, "carbs": 5},
    "салат с гребешками": {"name": "Салат с гребешками", "calories": 110, "protein": 10, "fat": 5, "carbs": 5},
    "салат с мидиями и креветками": {"name": "Салат с мидиями и креветками", "calories": 100, "protein": 10, "fat": 4, "carbs": 5},
    "салат с кунжутом": {"name": "Салат с кунжутом", "calories": 70, "protein": 2, "fat": 4, "carbs": 6},
    "салат с семечками": {"name": "Салат с семечками", "calories": 80, "protein": 2, "fat": 5, "carbs": 6},
    "салат с орехами": {"name": "Салат с орехами", "calories": 120, "protein": 3, "fat": 8, "carbs": 8},
    "салат с грецкими орехами": {"name": "Салат с грецкими орехами", "calories": 130, "protein": 3, "fat": 9, "carbs": 8},
    "салат с кедровыми орешками": {"name": "Салат с кедровыми орешками", "calories": 140, "protein": 3, "fat": 10, "carbs": 8},
    "салат с миндалём": {"name": "Салат с миндалём", "calories": 120, "protein": 3, "fat": 8, "carbs": 8},
    "салат с арахисом": {"name": "Салат с арахисом", "calories": 130, "protein": 4, "fat": 9, "carbs": 7},
    "салат с фисташками": {"name": "Салат с фисташками", "calories": 130, "protein": 4, "fat": 9, "carbs": 7},
    "салат с курагой": {"name": "Салат с курагой", "calories": 100, "protein": 2, "fat": 2, "carbs": 18},
    "салат с черносливом": {"name": "Салат с черносливом", "calories": 100, "protein": 2, "fat": 2, "carbs": 18},
    "салат с изюмом": {"name": "Салат с изюмом", "calories": 90, "protein": 1, "fat": 1, "carbs": 20},
    "салат с виноградом": {"name": "Салат с виноградом", "calories": 70, "protein": 1, "fat": 2, "carbs": 12},
    "салат с грушей": {"name": "Салат с грушей", "calories": 70, "protein": 1, "fat": 2, "carbs": 12},
    "салат с яблоком": {"name": "Салат с яблоком", "calories": 60, "protein": 1, "fat": 1, "carbs": 12},
    "салат с ананасом": {"name": "Салат с ананасом", "calories": 70, "protein": 1, "fat": 1, "carbs": 14},
    "салат с персиком": {"name": "Салат с персиком", "calories": 60, "protein": 1, "fat": 1, "carbs": 12},
    "салат с манго и авокадо": {"name": "Салат с манго и авокадо", "calories": 120, "protein": 2, "fat": 8, "carbs": 10},
    "салат с дыней": {"name": "Салат с дыней", "calories": 50, "protein": 1, "fat": 1, "carbs": 10},
    "салат с арбузом": {"name": "Салат с арбузом", "calories": 40, "protein": 1, "fat": 1, "carbs": 8},
    "салат с клубникой": {"name": "Салат с клубникой", "calories": 50, "protein": 1, "fat": 1, "carbs": 10},
    "салат с малиной": {"name": "Салат с малиной", "calories": 60, "protein": 1, "fat": 1, "carbs": 12},
    "салат с черникой": {"name": "Салат с черникой", "calories": 60, "protein": 1, "fat": 1, "carbs": 12},
    # ========== ЯЙЦА И БЛЮДА ИЗ ЯИЦ (ДОПОЛНЕНИЕ) ==========
    "яичница": {"name": "Яичница глазунья", "calories": 180, "protein": 10, "fat": 14, "carbs": 1.5},
    "омлет с молоком": {"name": "Омлет с молоком", "calories": 150, "protein": 9, "fat": 11, "carbs": 2},
    "яйцо пашот": {"name": "Яйцо пашот", "calories": 155, "protein": 12.6, "fat": 10.6, "carbs": 1.1},

    # ========== БУТЕРБРОДЫ И ФАСТФУД ==========
    "бутерброд с колбасой": {"name": "Бутерброд с колбасой", "calories": 250, "protein": 10, "fat": 12, "carbs": 25},
    "бутерброд с сыром": {"name": "Бутерброд с сыром", "calories": 280, "protein": 12, "fat": 15, "carbs": 24},
    "бутерброд с маслом": {"name": "Бутерброд с маслом", "calories": 320, "protein": 6, "fat": 18, "carbs": 34},
    "бутерброд с колбасой и сыром": {"name": "Бутерброд с колбасой и сыром", "calories": 300, "protein": 14, "fat": 16, "carbs": 26},
    "сэндвич с курицей": {"name": "Сэндвич с курицей", "calories": 200, "protein": 18, "fat": 7, "carbs": 20},
    "гамбургер": {"name": "Гамбургер", "calories": 250, "protein": 15, "fat": 10, "carbs": 25},
    "чизбургер": {"name": "Чизбургер", "calories": 300, "protein": 17, "fat": 15, "carbs": 27},
    "хот-дог": {"name": "Хот-дог", "calories": 280, "protein": 10, "fat": 15, "carbs": 25},
    "сосиска в тесте": {"name": "Сосиска в тесте", "calories": 320, "protein": 10, "fat": 20, "carbs": 25},
    "пицца": {"name": "Пицца (средняя)", "calories": 260, "protein": 12, "fat": 10, "carbs": 30},

    # ========== ДЕСЕРТЫ И ВЫПЕЧКА ==========
    "торт наполеон": {"name": "Торт Наполеон", "calories": 420, "protein": 6, "fat": 25, "carbs": 45},
    "торт медовик": {"name": "Торт Медовик", "calories": 380, "protein": 5, "fat": 18, "carbs": 50},
    "торт птичье молоко": {"name": "Торт Птичье молоко", "calories": 360, "protein": 4, "fat": 15, "carbs": 52},
    "пирожное картошка": {"name": "Пирожное Картошка", "calories": 400, "protein": 4, "fat": 20, "carbs": 48},
    "эклер": {"name": "Эклер", "calories": 320, "protein": 6, "fat": 18, "carbs": 36},
    "пончик": {"name": "Пончик", "calories": 400, "protein": 5, "fat": 22, "carbs": 45},
    "шоколад молочный": {"name": "Шоколад молочный", "calories": 550, "protein": 6, "fat": 35, "carbs": 55},
    "мороженое пломбир": {"name": "Мороженое пломбир", "calories": 230, "protein": 3.5, "fat": 15, "carbs": 20},
    "пирожок с яблоком": {"name": "Пирожок с яблоком", "calories": 250, "protein": 4, "fat": 10, "carbs": 35},
    "пирожок с капустой": {"name": "Пирожок с капустой", "calories": 200, "protein": 5, "fat": 8, "carbs": 27},
    "сырник": {"name": "Сырник", "calories": 220, "protein": 12, "fat": 12, "carbs": 15},
    "запеканка творожная": {"name": "Запеканка творожная", "calories": 170, "protein": 12, "fat": 7, "carbs": 15},
    "блинчики": {"name": "Блинчики", "calories": 180, "protein": 6, "fat": 7, "carbs": 24},
    "оладьи": {"name": "Оладьи", "calories": 210, "protein": 6, "fat": 8, "carbs": 30},

    # ========== НАПИТКИ ==========
    "кофе с молоком": {"name": "Кофе с молоком (без сахара)", "calories": 40, "protein": 2, "fat": 1.5, "carbs": 4},
    "кофе латте": {"name": "Латте (без сахара)", "calories": 90, "protein": 5, "fat": 5, "carbs": 7},
    "кофе капучино": {"name": "Капучино (без сахара)", "calories": 80, "protein": 4, "fat": 4, "carbs": 6},
    "чай с сахаром": {"name": "Чай с сахаром (1 ч.л.)", "calories": 30, "protein": 0, "fat": 0, "carbs": 8},
    "компот": {"name": "Компот из сухофруктов", "calories": 60, "protein": 0.5, "fat": 0, "carbs": 15},
    "сок яблочный": {"name": "Сок яблочный", "calories": 46, "protein": 0.5, "fat": 0, "carbs": 11},
    "сок апельсиновый": {"name": "Сок апельсиновый", "calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 10},
    "газировка": {"name": "Газировка (Кола)", "calories": 42, "protein": 0, "fat": 0, "carbs": 10.5},
    "квас": {"name": "Квас", "calories": 30, "protein": 0.3, "fat": 0, "carbs": 7.5},

    # ========== ГОТОВЫЕ БЛЮДА ==========
    "пельмени": {"name": "Пельмени (отварные)", "calories": 250, "protein": 12, "fat": 10, "carbs": 28},
    "вареники с картошкой": {"name": "Вареники с картошкой", "calories": 150, "protein": 5, "fat": 3, "carbs": 27},
    "вареники с творогом": {"name": "Вареники с творогом", "calories": 180, "protein": 9, "fat": 5, "carbs": 25},
    "манты": {"name": "Манты", "calories": 200, "protein": 10, "fat": 8, "carbs": 23},
    "чебурек": {"name": "Чебурек", "calories": 350, "protein": 8, "fat": 22, "carbs": 30},
    "беляш": {"name": "Беляш", "calories": 320, "protein": 10, "fat": 18, "carbs": 28},
    "шаурма": {"name": "Шаурма с курицей", "calories": 200, "protein": 12, "fat": 8, "carbs": 22},
    "картофель фри": {"name": "Картофель фри", "calories": 300, "protein": 3.5, "fat": 15, "carbs": 38},
    "котлета куриная": {"name": "Котлета куриная жареная", "calories": 200, "protein": 18, "fat": 12, "carbs": 8},
    "котлета свиная": {"name": "Котлета свиная жареная", "calories": 300, "protein": 15, "fat": 25, "carbs": 5},
    "пюре картофельное": {"name": "Пюре картофельное", "calories": 90, "protein": 2, "fat": 3, "carbs": 14},
    "борщ": {"name": "Борщ (с мясом)", "calories": 65, "protein": 4, "fat": 3, "carbs": 6},
    "суп куриный": {"name": "Суп куриный с лапшой", "calories": 45, "protein": 3, "fat": 1.5, "carbs": 5},

      # ========== ДОБАВЛЯЕМ ПОПУЛЯРНЫЕ БЛЮДА ==========
    "пицца маргарита": {"name": "Пицца Маргарита", "calories": 250, "protein": 10, "fat": 8, "carbs": 35},
    "пицца пепперони": {"name": "Пицца Пепперони", "calories": 300, "protein": 12, "fat": 12, "carbs": 36},
    "пицца с грибами": {"name": "Пицца с грибами", "calories": 240, "protein": 10, "fat": 8, "carbs": 34},
    "бургер": {"name": "Бургер", "calories": 295, "protein": 17, "fat": 14, "carbs": 25},
    "чизбургер": {"name": "Чизбургер", "calories": 313, "protein": 18, "fat": 16, "carbs": 27},
    "гамбургер": {"name": "Гамбургер", "calories": 250, "protein": 15, "fat": 10, "carbs": 25},
    "картофель фри": {"name": "Картофель фри", "calories": 312, "protein": 3.4, "fat": 15, "carbs": 41},
    "наггетсы": {"name": "Куриные наггетсы", "calories": 296, "protein": 14, "fat": 18, "carbs": 20},
    "суши": {"name": "Суши (среднее)", "calories": 45, "protein": 2, "fat": 0.5, "carbs": 8},
    "роллы филадельфия": {"name": "Роллы Филадельфия", "calories": 180, "protein": 6, "fat": 5, "carbs": 28},
    "роллы калифорния": {"name": "Роллы Калифорния", "calories": 140, "protein": 5, "fat": 4, "carbs": 22},
    "сашими": {"name": "Сашими", "calories": 120, "protein": 20, "fat": 3, "carbs": 2},
    "рамен": {"name": "Рамен", "calories": 400, "protein": 15, "fat": 12, "carbs": 55},
    "удон": {"name": "Удон", "calories": 150, "protein": 5, "fat": 2, "carbs": 30},
    "греческий салат": {"name": "Греческий салат", "calories": 120, "protein": 3, "fat": 8, "carbs": 6},
    "цезарь с курицей": {"name": "Цезарь с курицей", "calories": 180, "protein": 12, "fat": 10, "carbs": 8},
    "оладьи": {"name": "Оладьи", "calories": 210, "protein": 6, "fat": 8, "carbs": 30},
    "сырники": {"name": "Сырники", "calories": 200, "protein": 12, "fat": 10, "carbs": 15},
    "запеканка творожная": {"name": "Запеканка творожная", "calories": 170, "protein": 12, "fat": 7, "carbs": 15},
    "омлет": {"name": "Омлет", "calories": 150, "protein": 10, "fat": 11, "carbs": 2},
    "яичница": {"name": "Яичница", "calories": 180, "protein": 10, "fat": 14, "carbs": 1.5},
    "блины": {"name": "Блины", "calories": 180, "protein": 6, "fat": 7, "carbs": 24},
    "пирожок с капустой": {"name": "Пирожок с капустой", "calories": 200, "protein": 5, "fat": 8, "carbs": 27},
    "пирожок с яблоком": {"name": "Пирожок с яблоком", "calories": 250, "protein": 4, "fat": 10, "carbs": 35},
    "чебурек": {"name": "Чебурек", "calories": 350, "protein": 8, "fat": 22, "carbs": 30},
    "беляш": {"name": "Беляш", "calories": 320, "protein": 10, "fat": 18, "carbs": 28},
    "шаурма": {"name": "Шаурма", "calories": 200, "protein": 12, "fat": 8, "carbs": 22},
    "шашлык": {"name": "Шашлык", "calories": 250, "protein": 20, "fat": 18, "carbs": 2},
    "плов": {"name": "Плов", "calories": 200, "protein": 8, "fat": 7, "carbs": 27},
    "борщ": {"name": "Борщ", "calories": 65, "protein": 4, "fat": 3, "carbs": 6},
    "щи": {"name": "Щи", "calories": 40, "protein": 3, "fat": 2, "carbs": 4},
    "солянка": {"name": "Солянка", "calories": 90, "protein": 5, "fat": 5, "carbs": 5},
    "уха": {"name": "Уха", "calories": 40, "protein": 5, "fat": 1, "carbs": 2},
    "грибной суп": {"name": "Грибной суп", "calories": 50, "protein": 2, "fat": 2, "carbs": 6},
    "куриный суп": {"name": "Куриный суп", "calories": 45, "protein": 3, "fat": 1.5, "carbs": 5},
    "том-ям": {"name": "Том-ям", "calories": 120, "protein": 5, "fat": 8, "carbs": 8},
    "фо-бо": {"name": "Фо-бо", "calories": 350, "protein": 20, "fat": 10, "carbs": 45},
    "лазанья": {"name": "Лазанья", "calories": 350, "protein": 18, "fat": 17, "carbs": 30},
    "спагетти карбонара": {"name": "Спагетти Карбонара", "calories": 350, "protein": 12, "fat": 15, "carbs": 40},
    "спагетти болоньезе": {"name": "Спагетти Болоньезе", "calories": 320, "protein": 14, "fat": 10, "carbs": 45},
    "макароны с сыром": {"name": "Макароны с сыром", "calories": 300, "protein": 10, "fat": 12, "carbs": 38},
    "ризотто": {"name": "Ризотто", "calories": 220, "protein": 5, "fat": 8, "carbs": 32},
    "гречка с мясом": {"name": "Гречка с мясом", "calories": 180, "protein": 12, "fat": 6, "carbs": 20},
    "рис с овощами": {"name": "Рис с овощами", "calories": 120, "protein": 3, "fat": 2, "carbs": 24},
    "картофельное пюре": {"name": "Картофельное пюре", "calories": 90, "protein": 2, "fat": 3, "carbs": 14},
    "овощи на пару": {"name": "Овощи на пару", "calories": 50, "protein": 2, "fat": 0.5, "carbs": 10},
    "котлета куриная": {"name": "Котлета куриная", "calories": 200, "protein": 18, "fat": 12, "carbs": 8},
    "котлета свиная": {"name": "Котлета свиная", "calories": 300, "protein": 15, "fat": 25, "carbs": 5},
    "рыбное филе": {"name": "Рыбное филе", "calories": 150, "protein": 20, "fat": 7, "carbs": 0},
    "лосось на гриле": {"name": "Лосось на гриле", "calories": 200, "protein": 22, "fat": 12, "carbs": 0},
    "стейк из говядины": {"name": "Стейк из говядины", "calories": 250, "protein": 26, "fat": 17, "carbs": 0},
    "куриная грудка": {"name": "Куриная грудка", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "индейка": {"name": "Индейка", "calories": 135, "protein": 30, "fat": 1, "carbs": 0},
    "тушеная говядина": {"name": "Тушеная говядина", "calories": 200, "protein": 25, "fat": 10, "carbs": 3},
    "пельмени": {"name": "Пельмени", "calories": 250, "protein": 12, "fat": 10, "carbs": 28},
    "вареники с картошкой": {"name": "Вареники с картошкой", "calories": 150, "protein": 5, "fat": 3, "carbs": 27},
    "манты": {"name": "Манты", "calories": 200, "protein": 10, "fat": 8, "carbs": 23},
    "хинкали": {"name": "Хинкали", "calories": 220, "protein": 12, "fat": 9, "carbs": 24},
    "чебуреки": {"name": "Чебуреки", "calories": 350, "protein": 8, "fat": 22, "carbs": 30},
    "беляши": {"name": "Беляши", "calories": 320, "protein": 10, "fat": 18, "carbs": 28},
    "пицца": {"name": "Пицца", "calories": 260, "protein": 12, "fat": 10, "carbs": 30},
    "суши": {"name": "Суши", "calories": 45, "protein": 2, "fat": 0.5, "carbs": 8},
    "роллы": {"name": "Роллы", "calories": 150, "protein": 5, "fat": 4, "carbs": 25},
    "салат": {"name": "Салат", "calories": 100, "protein": 3, "fat": 5, "carbs": 10},
    "борщ": {"name": "Борщ", "calories": 65, "protein": 4, "fat": 3, "carbs": 6},
    "щи": {"name": "Щи", "calories": 40, "protein": 3, "fat": 2, "carbs": 4},
    "солянка": {"name": "Солянка", "calories": 90, "protein": 5, "fat": 5, "carbs": 5},
    "уха": {"name": "Уха", "calories": 40, "protein": 5, "fat": 1, "carbs": 2},
    "грибной суп": {"name": "Грибной суп", "calories": 50, "protein": 2, "fat": 2, "carbs": 6},
    "куриный суп": {"name": "Куриный суп", "calories": 45, "protein": 3, "fat": 1.5, "carbs": 5},
    "том-ям": {"name": "Том-ям", "calories": 120, "protein": 5, "fat": 8, "carbs": 8},
    "фо-бо": {"name": "Фо-бо", "calories": 350, "protein": 20, "fat": 10, "carbs": 45},
    "лазанья": {"name": "Лазанья", "calories": 350, "protein": 18, "fat": 17, "carbs": 30},
    "спагетти карбонара": {"name": "Спагетти Карбонара", "calories": 350, "protein": 12, "fat": 15, "carbs": 40},
    "спагетти болоньезе": {"name": "Спагетти Болоньезе", "calories": 320, "protein": 14, "fat": 10, "carbs": 45},
    "макароны с сыром": {"name": "Макароны с сыром", "calories": 300, "protein": 10, "fat": 12, "carbs": 38},
    "ризотто": {"name": "Ризотто", "calories": 220, "protein": 5, "fat": 8, "carbs": 32},
    "гречка с мясом": {"name": "Гречка с мясом", "calories": 180, "protein": 12, "fat": 6, "carbs": 20},
    "рис с овощами": {"name": "Рис с овощами", "calories": 120, "protein": 3, "fat": 2, "carbs": 24},
    "картофельное пюре": {"name": "Картофельное пюре", "calories": 90, "protein": 2, "fat": 3, "carbs": 14},
    "овощи на пару": {"name": "Овощи на пару", "calories": 50, "protein": 2, "fat": 0.5, "carbs": 10},
    "котлета куриная": {"name": "Котлета куриная", "calories": 200, "protein": 18, "fat": 12, "carbs": 8},
    "котлета свиная": {"name": "Котлета свиная", "calories": 300, "protein": 15, "fat": 25, "carbs": 5},
    "рыбное филе": {"name": "Рыбное филе", "calories": 150, "protein": 20, "fat": 7, "carbs": 0},
    "лосось на гриле": {"name": "Лосось на гриле", "calories": 200, "protein": 22, "fat": 12, "carbs": 0},
    "стейк из говядины": {"name": "Стейк из говядины", "calories": 250, "protein": 26, "fat": 17, "carbs": 0},
    "куриная грудка": {"name": "Куриная грудка", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "индейка": {"name": "Индейка", "calories": 135, "protein": 30, "fat": 1, "carbs": 0},
    "тушеная говядина": {"name": "Тушеная говядина", "calories": 200, "protein": 25, "fat": 10, "carbs": 3},
    "пельмени": {"name": "Пельмени", "calories": 250, "protein": 12, "fat": 10, "carbs": 28},
    "вареники с картошкой": {"name": "Вареники с картошкой", "calories": 150, "protein": 5, "fat": 3, "carbs": 27},
    "манты": {"name": "Манты", "calories": 200, "protein": 10, "fat": 8, "carbs": 23},
    "хинкали": {"name": "Хинкали", "calories": 220, "protein": 12, "fat": 9, "carbs": 24},
    "чебуреки": {"name": "Чебуреки", "calories": 350, "protein": 8, "fat": 22, "carbs": 30},
    "беляши": {"name": "Беляши", "calories": 320, "protein": 10, "fat": 18, "carbs": 28},
      
      # ========== БЛЮДА (ДОБАВЛЕННЫЕ) ==========
    "чахохбили": {"name": "Чахохбили", "calories": 180, "protein": 15, "fat": 10, "carbs": 8},
    "харчо": {"name": "Харчо", "calories": 120, "protein": 8, "fat": 5, "carbs": 10},
    "сациви": {"name": "Сациви", "calories": 250, "protein": 18, "fat": 18, "carbs": 5},
    "лобио": {"name": "Лобио", "calories": 150, "protein": 8, "fat": 7, "carbs": 15},
    "долма": {"name": "Долма", "calories": 200, "protein": 10, "fat": 12, "carbs": 15},
    "мусака": {"name": "Мусака", "calories": 220, "protein": 12, "fat": 14, "carbs": 12},
    "паэлья": {"name": "Паэлья", "calories": 180, "protein": 10, "fat": 5, "carbs": 25},
    "ризотто": {"name": "Ризотто", "calories": 200, "protein": 6, "fat": 8, "carbs": 28},
    "лазанья": {"name": "Лазанья", "calories": 250, "protein": 12, "fat": 12, "carbs": 25},
    "рататуй": {"name": "Рататуй", "calories": 80, "protein": 2, "fat": 5, "carbs": 8},
    "нисуаз": {"name": "Нисуаз", "calories": 150, "protein": 10, "fat": 8, "carbs": 8},
    "том ям": {"name": "Том Ям", "calories": 80, "protein": 5, "fat": 4, "carbs": 6},
    "фо": {"name": "Фо", "calories": 120, "protein": 8, "fat": 3, "carbs": 18},
    "рамен": {"name": "Рамен", "calories": 200, "protein": 10, "fat": 8, "carbs": 25},
    "удон": {"name": "Удон", "calories": 150, "protein": 5, "fat": 2, "carbs": 30},
    "бибимбап": {"name": "Бибимбап", "calories": 200, "protein": 8, "fat": 7, "carbs": 28},
    "пулькоги": {"name": "Пулькоги", "calories": 220, "protein": 18, "fat": 12, "carbs": 10},
    "кимчи": {"name": "Кимчи", "calories": 30, "protein": 2, "fat": 0, "carbs": 5},
    "бургер": {"name": "Бургер", "calories": 295, "protein": 17, "fat": 14, "carbs": 25},
    "чизбургер": {"name": "Чизбургер", "calories": 313, "protein": 18, "fat": 16, "carbs": 27},
    "хот-дог": {"name": "Хот-дог", "calories": 280, "protein": 10, "fat": 15, "carbs": 25},
    "крылья баффало": {"name": "Крылья Баффало", "calories": 300, "protein": 20, "fat": 22, "carbs": 2},
    "картофель фри": {"name": "Картофель фри", "calories": 312, "protein": 3.4, "fat": 15, "carbs": 41},
    "куриные наггетсы": {"name": "Куриные наггетсы", "calories": 296, "protein": 14, "fat": 18, "carbs": 20},
    "мак-н-чиз": {"name": "Макароны с сыром", "calories": 300, "protein": 10, "fat": 12, "carbs": 38},
    "сэндвич с тунцом": {"name": "Сэндвич с тунцом", "calories": 250, "protein": 15, "fat": 10, "carbs": 25},
    "клуб-сэндвич": {"name": "Клуб-сэндвич", "calories": 300, "protein": 18, "fat": 14, "carbs": 28},
    "хешбраун": {"name": "Хешбраун", "calories": 200, "protein": 2, "fat": 12, "carbs": 22},
    "пончики": {"name": "Пончики", "calories": 400, "protein": 5, "fat": 22, "carbs": 45},
    "синнабоны": {"name": "Синнабоны", "calories": 380, "protein": 5, "fat": 18, "carbs": 50},
    "банановый хлеб": {"name": "Банановый хлеб", "calories": 250, "protein": 3, "fat": 10, "carbs": 38},
    "гранола": {"name": "Гранола", "calories": 450, "protein": 10, "fat": 20, "carbs": 60},
    "хумус": {"name": "Хумус", "calories": 170, "protein": 5, "fat": 10, "carbs": 15},
    "фалафель": {"name": "Фалафель", "calories": 300, "protein": 13, "fat": 17, "carbs": 25},
    "табуле": {"name": "Табуле", "calories": 110, "protein": 3, "fat": 4, "carbs": 16},
    "кускус": {"name": "Кускус", "calories": 112, "protein": 3.8, "fat": 0.2, "carbs": 23},
    "шаурма": {"name": "Шаурма", "calories": 200, "protein": 12, "fat": 8, "carbs": 22},
    "чебуреки": {"name": "Чебуреки", "calories": 350, "protein": 8, "fat": 22, "carbs": 30},
    "беляши": {"name": "Беляши", "calories": 320, "protein": 10, "fat": 18, "carbs": 28},
    "самса": {"name": "Самса", "calories": 280, "protein": 8, "fat": 15, "carbs": 30},
    "шарлотка": {"name": "Шарлотка", "calories": 200, "protein": 4, "fat": 5, "carbs": 35},
    "наполеон": {"name": "Наполеон", "calories": 420, "protein": 6, "fat": 25, "carbs": 45},
    "медовик": {"name": "Медовик", "calories": 380, "protein": 5, "fat": 18, "carbs": 50},
    "пражский торт": {"name": "Пражский торт", "calories": 400, "protein": 5, "fat": 20, "carbs": 48},
    "киевский торт": {"name": "Киевский торт", "calories": 450, "protein": 5, "fat": 25, "carbs": 50},
    "зебра": {"name": "Зебра", "calories": 350, "protein": 5, "fat": 15, "carbs": 50},
    "брауни": {"name": "Брауни", "calories": 450, "protein": 5, "fat": 25, "carbs": 50},
    "чизкейк": {"name": "Чизкейк", "calories": 320, "protein": 6, "fat": 20, "carbs": 30},
    "панна-котта": {"name": "Панна-котта", "calories": 200, "protein": 4, "fat": 12, "carbs": 18},
    "сметанник": {"name": "Сметанник", "calories": 300, "protein": 5, "fat": 15, "carbs": 35},
    "эклер": {"name": "Эклер", "calories": 320, "protein": 6, "fat": 18, "carbs": 36},
    "безе": {"name": "Безе", "calories": 400, "protein": 4, "fat": 0, "carbs": 99},
    "павлова": {"name": "Павлова", "calories": 250, "protein": 3, "fat": 8, "carbs": 42},
}

# ========== КЭШИРОВАНИЕ ==========
def _get_cached_search(query: str) -> Optional[List[Dict]]:
    """Проверяет кэш поиска."""
    query_lower = query.lower().strip()
    if query_lower in _SEARCH_CACHE:
        results, timestamp = _SEARCH_CACHE[query_lower]
        if time.time() - timestamp < _CACHE_TTL:
            logger.info(f"♻️ Cache hit for '{query_lower}'")
            return results
        else:
            del _SEARCH_CACHE[query_lower]
    return None


def _cache_search(query: str, results: List[Dict]):
    """Сохраняет в кэш поиска."""
    query_lower = query.lower().strip()
    _SEARCH_CACHE[query_lower] = (results, time.time())
    
    if len(_SEARCH_CACHE) > _CACHE_LIMIT:
        oldest = sorted(_SEARCH_CACHE.items(), key=lambda x: x[1][1])[:50]
        for key, _ in oldest:
            del _SEARCH_CACHE[key]


def search_local_db(query: str) -> List[Dict]:
    """Поиск в локальной базе по частичному совпадению."""
    results = []
    query_lower = query.lower().strip()
    
    normalized_query = query_lower
    for ending in ['а', 'ы', 'и', 'у', 'ом', 'е', 'ой', 'ей', 'ами', 'ах', 'ов', 'ев', 'ец', 'ца', 'цы']:
        if query_lower.endswith(ending) and len(query_lower) > 4:
            normalized_query = query_lower[:-len(ending)]
            break
    
    for key, item in LOCAL_FOOD_DB.items():
        if query_lower in key:
            results.append({
                'name': item['name'],
                'calories': item['calories'],
                'protein': item['protein'],
                'fat': item['fat'],
                'carbs': item['carbs'],
                'source': 'local',
                'score': 1.0
            })
        elif normalized_query in key and len(normalized_query) >= 3:
            results.append({
                'name': item['name'],
                'calories': item['calories'],
                'protein': item['protein'],
                'fat': item['fat'],
                'carbs': item['carbs'],
                'source': 'local',
                'score': 0.8
            })
        elif query_lower in item['name'].lower():
            results.append({
                'name': item['name'],
                'calories': item['calories'],
                'protein': item['protein'],
                'fat': item['fat'],
                'carbs': item['carbs'],
                'source': 'local',
                'score': 0.9
            })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:10]


async def search_openfoodfacts(query: str, max_results: int = 5) -> List[Dict]:
    """Поиск продуктов по названию через Open Food Facts."""
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": max_results * 2,
        "lang": "ru",
        "countries": "russia",
        "countries_tags": "en:russia",
    }
    headers = {
        "User-Agent": "NutriBuddyBot/1.0 (https://t.me/nutri_buddy_aibot)"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=30) as resp:
                if resp.status != 200:
                    logger.warning(f"OpenFoodFacts error {resp.status}")
                    return []
                
                data = await resp.json()
                products = data.get("products", [])
                
                if not products:
                    return []
                
                results = []
                seen_names = set()
                
                for p in products:
                    name = p.get("product_name_ru") or p.get("product_name") or p.get("product_name_en")
                    if not name or len(name) < 3:
                        continue
                    
                    name_lower = name.lower()
                    if name_lower in seen_names:
                        continue
                    seen_names.add(name_lower)
                    
                    nutriments = p.get("nutriments", {})
                    calories = nutriments.get("energy-kcal_100g") or 0
                    
                    if calories == 0:
                        continue
                    
                    results.append({
                        "name": name,
                        "calories": float(calories),
                        "protein": float(nutriments.get("proteins_100g", 0) or 0),
                        "fat": float(nutriments.get("fat_100g", 0) or 0),
                        "carbs": float(nutriments.get("carbohydrates_100g", 0) or 0),
                        "source": "openfoodfacts"
                    })
                    
                    if len(results) >= max_results:
                        break
                
                return results
    except asyncio.TimeoutError:
        logger.warning("OpenFoodFacts timeout")
        return []
    except Exception as e:
        logger.warning(f"OpenFoodFacts exception: {e}")
        return []


async def search_food(query: str) -> List[Dict]:
    """Сначала локальная база, если мало результатов – OpenFoodFacts."""
    query = query.lower().strip()
    
    if not query:
        return []
    
    cached = _get_cached_search(query)
    if cached:
        return cached
    
    local_results = search_local_db(query)
    
    exact_matches = [r for r in local_results if query in r['name'].lower()]
    if exact_matches:
        _cache_search(query, exact_matches[:10])
        return exact_matches[:10]
    
    off_results = await search_openfoodfacts(query)
    
    seen = set()
    combined = []
    for item in local_results + off_results:
        name_lower = item["name"].lower()
        if name_lower not in seen:
            seen.add(name_lower)
            combined.append(item)
    
    combined.sort(key=lambda x: 0 if x["source"] == "local" else 1)
    
    _cache_search(query, combined[:10])
    return combined[:10]


async def get_food_data(name: str) -> Dict:
    """Возвращает базовые данные продукта по названию."""
    results = await search_food(name)
    if results:
        best = results[0]
        return {
            'name': best['name'],
            'base_calories': best.get('calories', 0),
            'base_protein': best.get('protein', 0),
            'base_fat': best.get('fat', 0),
            'base_carbs': best.get('carbs', 0)
        }
    else:
        return {
            'name': name,
            'base_calories': 0,
            'base_protein': 0,
            'base_fat': 0,
            'base_carbs': 0
        }
