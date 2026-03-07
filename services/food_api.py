"""
services/food_api.py
Поиск продуктов: только локальная база ингредиентов.
OpenFoodFacts отключён.
"""
import aiohttp
import logging
import asyncio
import time
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ========== КЭШИРОВАНИЕ ==========
_SEARCH_CACHE: Dict[str, Tuple[List[Dict], float]] = {}
_CACHE_TTL = 300  # 5 минут
_CACHE_LIMIT = 200

# ========== ЛОКАЛЬНАЯ БАЗА ИНГРЕДИЕНТОВ (только простые продукты) ==========
# Ключи — слова в нижнем регистре (единственное число, именительный падеж)
LOCAL_FOOD_DB = {
    # ========== ЛИСТОВОЙ САЛАТ И ЗЕЛЕНЬ ==========
    "салат": {"name": "Салат листовой", "calories": 15, "protein": 1.2, "fat": 0.2, "carbs": 2.5},
    "салат айсберг": {"name": "Салат Айсберг", "calories": 14, "protein": 1, "fat": 0.1, "carbs": 2},
    "салат романо": {"name": "Салат Романо", "calories": 17, "protein": 1.5, "fat": 0.3, "carbs": 2.5},
    "руккола": {"name": "Руккола", "calories": 25, "protein": 2.5, "fat": 0.5, "carbs": 3.5},
    "шпинат": {"name": "Шпинат", "calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6},
    "зелень": {"name": "Зелень (укроп, петрушка)", "calories": 35, "protein": 2.5, "fat": 0.5, "carbs": 6},
    "укроп": {"name": "Укроп", "calories": 43, "protein": 3.5, "fat": 1.1, "carbs": 7},
    "петрушка": {"name": "Петрушка", "calories": 36, "protein": 3, "fat": 0.8, "carbs": 6},
    "кинза": {"name": "Кинза", "calories": 23, "protein": 2.1, "fat": 0.5, "carbs": 3.7},
    "базилик": {"name": "Базилик", "calories": 44, "protein": 2.5, "fat": 0.6, "carbs": 5.1},
    "мята": {"name": "Мята", "calories": 70, "protein": 3.8, "fat": 0.9, "carbs": 15},
    "тимьян": {"name": "Тимьян", "calories": 101, "protein": 5.6, "fat": 1.7, "carbs": 24},
    "розмарин": {"name": "Розмарин", "calories": 131, "protein": 3.3, "fat": 5.9, "carbs": 21},

    # ========== ОВОЩИ ==========
    "помидор": {"name": "Помидор", "calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
    "огурец": {"name": "Огурец", "calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
    "картофель": {"name": "Картофель", "calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
    "морковь": {"name": "Морковь", "calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
    "лук": {"name": "Лук репчатый", "calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9},
    "чеснок": {"name": "Чеснок", "calories": 149, "protein": 6.4, "fat": 0.5, "carbs": 33},
    "капуста": {"name": "Капуста белокочанная", "calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 5.8},
    "брокколи": {"name": "Брокколи", "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
    "цветная капуста": {"name": "Цветная капуста", "calories": 25, "protein": 2, "fat": 0.3, "carbs": 5},
    "баклажан": {"name": "Баклажан", "calories": 24, "protein": 1, "fat": 0.2, "carbs": 5.7},
    "кабачок": {"name": "Кабачок", "calories": 24, "protein": 0.6, "fat": 0.3, "carbs": 5.2},
    "перец болгарский": {"name": "Перец болгарский", "calories": 26, "protein": 1.2, "fat": 0.3, "carbs": 6},
    "перец чили": {"name": "Перец чили", "calories": 40, "protein": 2, "fat": 0.4, "carbs": 9},
    "тыква": {"name": "Тыква", "calories": 22, "protein": 1, "fat": 0.1, "carbs": 5.5},
    "свекла": {"name": "Свёкла", "calories": 43, "protein": 1.5, "fat": 0.1, "carbs": 9.5},
    "редис": {"name": "Редис", "calories": 20, "protein": 0.6, "fat": 0.1, "carbs": 4},
    "сельдерей": {"name": "Сельдерей", "calories": 16, "protein": 0.7, "fat": 0.2, "carbs": 3},
    "спаржа": {"name": "Спаржа", "calories": 20, "protein": 2.2, "fat": 0.2, "carbs": 4},
    "стручковая фасоль": {"name": "Стручковая фасоль", "calories": 31, "protein": 2, "fat": 0.2, "carbs": 7},
    "горошек": {"name": "Горошек зелёный", "calories": 60, "protein": 4, "fat": 0.5, "carbs": 10},
    "кукуруза": {"name": "Кукуруза сладкая", "calories": 70, "protein": 2, "fat": 1, "carbs": 15},
    "авокадо": {"name": "Авокадо", "calories": 160, "protein": 2, "fat": 15, "carbs": 9},
    "оливки": {"name": "Оливки", "calories": 150, "protein": 1, "fat": 15, "carbs": 3},
    "маслины": {"name": "Маслины", "calories": 150, "protein": 1, "fat": 15, "carbs": 3},
    "корнишоны": {"name": "Корнишоны маринованные", "calories": 30, "protein": 1, "fat": 0, "carbs": 5},

    # ========== ФРУКТЫ И ЯГОДЫ ==========
    "яблоко": {"name": "Яблоко", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
    "банан": {"name": "Банан", "calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23},
    "апельсин": {"name": "Апельсин", "calories": 47, "protein": 0.9, "fat": 0.1, "carbs": 12},
    "мандарин": {"name": "Мандарин", "calories": 38, "protein": 0.6, "fat": 0.2, "carbs": 9},
    "лимон": {"name": "Лимон", "calories": 29, "protein": 1.1, "fat": 0.3, "carbs": 9},
    "лайм": {"name": "Лайм", "calories": 30, "protein": 0.7, "fat": 0.2, "carbs": 11},
    "грейпфрут": {"name": "Грейпфрут", "calories": 42, "protein": 0.8, "fat": 0.1, "carbs": 11},
    "киви": {"name": "Киви", "calories": 61, "protein": 1.1, "fat": 0.5, "carbs": 15},
    "ананас": {"name": "Ананас", "calories": 50, "protein": 0.5, "fat": 0.1, "carbs": 13},
    "манго": {"name": "Манго", "calories": 60, "protein": 0.8, "fat": 0.4, "carbs": 15},
    "груша": {"name": "Груша", "calories": 57, "protein": 0.4, "fat": 0.1, "carbs": 15},
    "персик": {"name": "Персик", "calories": 39, "protein": 0.9, "fat": 0.3, "carbs": 10},
    "абрикос": {"name": "Абрикос", "calories": 48, "protein": 1.4, "fat": 0.4, "carbs": 11},
    "слива": {"name": "Слива", "calories": 46, "protein": 0.7, "fat": 0.3, "carbs": 11},
    "вишня": {"name": "Вишня", "calories": 50, "protein": 1, "fat": 0.3, "carbs": 12},
    "черешня": {"name": "Черешня", "calories": 50, "protein": 1.1, "fat": 0.4, "carbs": 12},
    "клубника": {"name": "Клубника", "calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 7.7},
    "малина": {"name": "Малина", "calories": 52, "protein": 1.2, "fat": 0.7, "carbs": 12},
    "ежевика": {"name": "Ежевика", "calories": 43, "protein": 1.4, "fat": 0.5, "carbs": 10},
    "голубика": {"name": "Голубика", "calories": 57, "protein": 0.7, "fat": 0.3, "carbs": 14},
    "клюква": {"name": "Клюква", "calories": 46, "protein": 0.4, "fat": 0.1, "carbs": 12},
    "смородина красная": {"name": "Смородина красная", "calories": 43, "protein": 0.6, "fat": 0.2, "carbs": 11},
    "смородина чёрная": {"name": "Смородина чёрная", "calories": 44, "protein": 1, "fat": 0.4, "carbs": 12},
    "крыжовник": {"name": "Крыжовник", "calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 12},
    "виноград": {"name": "Виноград", "calories": 69, "protein": 0.7, "fat": 0.2, "carbs": 18},
    "арбуз": {"name": "Арбуз", "calories": 30, "protein": 0.6, "fat": 0.2, "carbs": 8},
    "дыня": {"name": "Дыня", "calories": 34, "protein": 0.8, "fat": 0.2, "carbs": 8},
    "гранат": {"name": "Гранат", "calories": 83, "protein": 1.7, "fat": 1.2, "carbs": 19},
    "хурма": {"name": "Хурма", "calories": 70, "protein": 0.6, "fat": 0.2, "carbs": 18},
    "инжир": {"name": "Инжир", "calories": 74, "protein": 0.8, "fat": 0.3, "carbs": 19},
    "финики": {"name": "Финики", "calories": 280, "protein": 2, "fat": 0.2, "carbs": 70},
    "изюм": {"name": "Изюм", "calories": 300, "protein": 3, "fat": 0.5, "carbs": 75},
    "курага": {"name": "Курага", "calories": 240, "protein": 3.5, "fat": 0.5, "carbs": 55},
    "чернослив": {"name": "Чернослив", "calories": 240, "protein": 2.3, "fat": 0.4, "carbs": 60},

    # ========== МЯСО, ПТИЦА, ЯЙЦА ==========
    "курица": {"name": "Курица (средняя)", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "куриная грудка": {"name": "Куриная грудка (филе)", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "куриное бедро": {"name": "Куриное бедро", "calories": 215, "protein": 18.4, "fat": 16.1, "carbs": 0},
    "куриное крыло": {"name": "Куриное крыло", "calories": 222, "protein": 18.3, "fat": 16.4, "carbs": 0},
    "куриная печень": {"name": "Куриная печень", "calories": 119, "protein": 17, "fat": 5, "carbs": 1},
    "индейка": {"name": "Индейка", "calories": 135, "protein": 30, "fat": 1, "carbs": 0},
    "индюшиная грудка": {"name": "Индюшиная грудка", "calories": 135, "protein": 30, "fat": 1, "carbs": 0},
    "утка": {"name": "Утка", "calories": 337, "protein": 19, "fat": 28, "carbs": 0},
    "говядина": {"name": "Говядина (средняя)", "calories": 250, "protein": 26, "fat": 17, "carbs": 0},
    "говяжий фарш": {"name": "Говяжий фарш (10% жира)", "calories": 176, "protein": 22, "fat": 10, "carbs": 0},
    "говяжья печень": {"name": "Говяжья печень", "calories": 135, "protein": 20, "fat": 4, "carbs": 6},
    "свинина": {"name": "Свинина (средняя)", "calories": 242, "protein": 27, "fat": 14, "carbs": 0},
    "свиная вырезка": {"name": "Свиная вырезка", "calories": 143, "protein": 26, "fat": 3.5, "carbs": 0},
    "бекон": {"name": "Бекон", "calories": 541, "protein": 37, "fat": 42, "carbs": 1},
    "ветчина": {"name": "Ветчина", "calories": 145, "protein": 17, "fat": 8, "carbs": 1},
    "колбаса": {"name": "Колбаса варёная", "calories": 250, "protein": 12, "fat": 22, "carbs": 2},
    "сосиски": {"name": "Сосиски", "calories": 270, "protein": 11, "fat": 24, "carbs": 2},
    "сардельки": {"name": "Сардельки", "calories": 300, "protein": 12, "fat": 27, "carbs": 2},
    "баранина": {"name": "Баранина", "calories": 250, "protein": 25, "fat": 16, "carbs": 0},
    "кролик": {"name": "Кролик", "calories": 173, "protein": 33, "fat": 3.5, "carbs": 0},
    "яйцо": {"name": "Яйцо куриное (1 шт = 50г)", "calories": 70, "protein": 5.5, "fat": 5, "carbs": 0.5},
    "яичный белок": {"name": "Яичный белок", "calories": 52, "protein": 11, "fat": 0.2, "carbs": 0.7},
    "яичный желток": {"name": "Яичный желток", "calories": 322, "protein": 16, "fat": 26, "carbs": 3.6},

    # ========== РЫБА И МОРЕПРОДУКТЫ ==========
    "лосось": {"name": "Лосось (сёмга)", "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    "семга": {"name": "Сёмга", "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    "треска": {"name": "Треска", "calories": 82, "protein": 18, "fat": 0.7, "carbs": 0},
    "минтай": {"name": "Минтай", "calories": 72, "protein": 17, "fat": 0.9, "carbs": 0},
    "хек": {"name": "Хек", "calories": 86, "protein": 17, "fat": 2, "carbs": 0},
    "скумбрия": {"name": "Скумбрия", "calories": 205, "protein": 19, "fat": 14, "carbs": 0},
    "сельдь": {"name": "Сельдь солёная", "calories": 250, "protein": 18, "fat": 19, "carbs": 0},
    "тунец": {"name": "Тунец", "calories": 130, "protein": 24, "fat": 4, "carbs": 0},
    "форель": {"name": "Форель", "calories": 148, "protein": 20, "fat": 7, "carbs": 0},
    "креветки": {"name": "Креветки", "calories": 85, "protein": 20, "fat": 0.5, "carbs": 0},
    "кальмар": {"name": "Кальмар", "calories": 100, "protein": 18, "fat": 2, "carbs": 0},
    "мидии": {"name": "Мидии", "calories": 85, "protein": 15, "fat": 2, "carbs": 3},
    "устрицы": {"name": "Устрицы", "calories": 70, "protein": 7, "fat": 2, "carbs": 4},
    "краб": {"name": "Краб", "calories": 87, "protein": 18, "fat": 1, "carbs": 0},
    "крабовые палочки": {"name": "Крабовые палочки", "calories": 90, "protein": 7, "fat": 2, "carbs": 12},
    "икра красная": {"name": "Икра красная", "calories": 250, "protein": 25, "fat": 15, "carbs": 3},
    "икра чёрная": {"name": "Икра чёрная", "calories": 280, "protein": 27, "fat": 16, "carbs": 3},

    # ========== МОЛОЧНЫЕ ПРОДУКТЫ ==========
    "молоко": {"name": "Молоко 3.2%", "calories": 60, "protein": 3, "fat": 3.2, "carbs": 4.7},
    "кефир": {"name": "Кефир 2.5%", "calories": 50, "protein": 3, "fat": 2.5, "carbs": 4},
    "йогурт": {"name": "Йогурт натуральный", "calories": 60, "protein": 4, "fat": 2.5, "carbs": 6},
    "творог": {"name": "Творог 5%", "calories": 120, "protein": 16, "fat": 5, "carbs": 3},
    "творог обезжиренный": {"name": "Творог обезжиренный", "calories": 70, "protein": 15, "fat": 0.3, "carbs": 2},
    "сметана": {"name": "Сметана 20%", "calories": 200, "protein": 2.5, "fat": 20, "carbs": 3.5},
    "сливки": {"name": "Сливки 20%", "calories": 200, "protein": 2.5, "fat": 20, "carbs": 4},
    "сыр": {"name": "Сыр твёрдый", "calories": 350, "protein": 25, "fat": 28, "carbs": 2},
    "пармезан": {"name": "Пармезан", "calories": 430, "protein": 38, "fat": 29, "carbs": 4},
    "моцарелла": {"name": "Моцарелла", "calories": 280, "protein": 22, "fat": 20, "carbs": 2},
    "фета": {"name": "Фета", "calories": 265, "protein": 14, "fat": 21, "carbs": 4},
    "брынза": {"name": "Брынза", "calories": 260, "protein": 18, "fat": 20, "carbs": 3},
    "сулугуни": {"name": "Сулугуни", "calories": 290, "protein": 20, "fat": 22, "carbs": 2},
    "масло сливочное": {"name": "Масло сливочное 82%", "calories": 750, "protein": 0.5, "fat": 82, "carbs": 0.5},
    "маргарин": {"name": "Маргарин", "calories": 700, "protein": 0.5, "fat": 80, "carbs": 1},

    # ========== КРУПЫ, МАКАРОНЫ, БОБОВЫЕ ==========
    "гречка": {"name": "Гречка (варёная)", "calories": 110, "protein": 4, "fat": 0.5, "carbs": 23},
    "рис": {"name": "Рис (варёный)", "calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
    "рис бурый": {"name": "Рис бурый (варёный)", "calories": 111, "protein": 2.6, "fat": 0.9, "carbs": 23},
    "овсянка": {"name": "Овсянка (на воде)", "calories": 71, "protein": 2.5, "fat": 1.5, "carbs": 12},
    "манка": {"name": "Манка (варёная)", "calories": 120, "protein": 3, "fat": 0.4, "carbs": 25},
    "пшено": {"name": "Пшено (варёное)", "calories": 120, "protein": 3.5, "fat": 1.3, "carbs": 24},
    "перловка": {"name": "Перловка (варёная)", "calories": 120, "protein": 3, "fat": 0.4, "carbs": 25},
    "булгур": {"name": "Булгур (варёный)", "calories": 83, "protein": 3.1, "fat": 0.2, "carbs": 18},
    "кускус": {"name": "Кускус (варёный)", "calories": 112, "protein": 3.8, "fat": 0.2, "carbs": 23},
    "киноа": {"name": "Киноа (варёная)", "calories": 120, "protein": 4, "fat": 2, "carbs": 21},
    "макароны": {"name": "Макароны (варёные)", "calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
    "спагетти": {"name": "Спагетти (варёные)", "calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
    "лапша": {"name": "Лапша (варёная)", "calories": 130, "protein": 4, "fat": 1, "carbs": 26},
    "вермишель": {"name": "Вермишель (варёная)", "calories": 130, "protein": 4, "fat": 1, "carbs": 26},
    "фасоль": {"name": "Фасоль (варёная)", "calories": 90, "protein": 6, "fat": 0.5, "carbs": 15},
    "чечевица": {"name": "Чечевица (варёная)", "calories": 116, "protein": 9, "fat": 0.4, "carbs": 20},
    "нут": {"name": "Нут (варёный)", "calories": 164, "protein": 9, "fat": 3, "carbs": 27},
    "горох": {"name": "Горох (варёный)", "calories": 118, "protein": 8, "fat": 0.4, "carbs": 21},

    # ========== ХЛЕБ И ВЫПЕЧКА ==========
    "хлеб": {"name": "Хлеб пшеничный", "calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
    "хлеб ржаной": {"name": "Хлеб ржаной", "calories": 200, "protein": 6, "fat": 1.5, "carbs": 40},
    "батон": {"name": "Батон", "calories": 260, "protein": 8, "fat": 3, "carbs": 50},
    "лаваш": {"name": "Лаваш", "calories": 275, "protein": 9, "fat": 2, "carbs": 56},
    "булочка": {"name": "Булочка", "calories": 300, "protein": 9, "fat": 5, "carbs": 55},
    "сухарики": {"name": "Сухарики", "calories": 350, "protein": 10, "fat": 5, "carbs": 70},
    "печенье": {"name": "Печенье", "calories": 450, "protein": 6, "fat": 15, "carbs": 75},
    "пряники": {"name": "Пряники", "calories": 360, "protein": 5, "fat": 5, "carbs": 75},
    "крекер": {"name": "Крекер", "calories": 450, "protein": 7, "fat": 15, "carbs": 70},

    # ========== ОРЕХИ, СЕМЕНА ==========
    "грецкий орех": {"name": "Грецкие орехи", "calories": 650, "protein": 15, "fat": 65, "carbs": 14},
    "миндаль": {"name": "Миндаль", "calories": 600, "protein": 19, "fat": 53, "carbs": 20},
    "фундук": {"name": "Фундук", "calories": 650, "protein": 15, "fat": 62, "carbs": 10},
    "арахис": {"name": "Арахис", "calories": 550, "protein": 26, "fat": 45, "carbs": 10},
    "кешью": {"name": "Кешью", "calories": 550, "protein": 18, "fat": 44, "carbs": 30},
    "пекан": {"name": "Пекан", "calories": 690, "protein": 9, "fat": 72, "carbs": 14},
    "фисташки": {"name": "Фисташки", "calories": 560, "protein": 20, "fat": 45, "carbs": 28},
    "кедровые орехи": {"name": "Кедровые орехи", "calories": 673, "protein": 14, "fat": 68, "carbs": 13},
    "семечки": {"name": "Семечки подсолнуха", "calories": 600, "protein": 20, "fat": 50, "carbs": 10},
    "тыквенные семечки": {"name": "Тыквенные семечки", "calories": 550, "protein": 20, "fat": 45, "carbs": 10},
    "кунжут": {"name": "Кунжут", "calories": 570, "protein": 17, "fat": 50, "carbs": 12},
    "лён": {"name": "Семя льна", "calories": 534, "protein": 18, "fat": 42, "carbs": 29},
    "чиа": {"name": "Семена чиа", "calories": 486, "protein": 17, "fat": 31, "carbs": 42},

    # ========== СОУСЫ, МАСЛА, ПРИПРАВЫ ==========
    "кетчуп": {"name": "Кетчуп", "calories": 100, "protein": 1.5, "fat": 0.5, "carbs": 22},
    "майонез": {"name": "Майонез (провансаль)", "calories": 600, "protein": 0.5, "fat": 65, "carbs": 3},
    "майонез легкий": {"name": "Майонез лёгкий", "calories": 250, "protein": 0.5, "fat": 25, "carbs": 5},
    "горчица": {"name": "Горчица", "calories": 100, "protein": 5, "fat": 5, "carbs": 10},
    "соевый соус": {"name": "Соевый соус", "calories": 60, "protein": 8, "fat": 0, "carbs": 8},
    "соус песто": {"name": "Соус песто", "calories": 500, "protein": 5, "fat": 50, "carbs": 10},
    "соус цезарь": {"name": "Соус Цезарь", "calories": 300, "protein": 2, "fat": 25, "carbs": 15},
    "томатная паста": {"name": "Томатная паста", "calories": 100, "protein": 5, "fat": 1, "carbs": 20},
    "томатный соус": {"name": "Томатный соус", "calories": 80, "protein": 2, "fat": 2, "carbs": 15},
    "бешамель": {"name": "Соус Бешамель", "calories": 150, "protein": 4, "fat": 12, "carbs": 8},
    "оливковое масло": {"name": "Масло оливковое", "calories": 900, "protein": 0, "fat": 100, "carbs": 0},
    "подсолнечное масло": {"name": "Масло подсолнечное", "calories": 900, "protein": 0, "fat": 100, "carbs": 0},
    "уксус": {"name": "Уксус столовый", "calories": 5, "protein": 0, "fat": 0, "carbs": 0.5},
    "соль": {"name": "Соль", "calories": 0, "protein": 0, "fat": 0, "carbs": 0},
    "перец": {"name": "Перец чёрный молотый", "calories": 255, "protein": 11, "fat": 3, "carbs": 65},
    "сахар": {"name": "Сахар", "calories": 400, "protein": 0, "fat": 0, "carbs": 100},
    "мёд": {"name": "Мёд", "calories": 300, "protein": 0.3, "fat": 0, "carbs": 80},
    "корица": {"name": "Корица", "calories": 247, "protein": 4, "fat": 1, "carbs": 81},
    "ваниль": {"name": "Ваниль", "calories": 288, "protein": 0, "fat": 0, "carbs": 12},
    "какао": {"name": "Какао-порошок", "calories": 228, "protein": 20, "fat": 14, "carbs": 58},

    # ========== НАПИТКИ ==========
    "вода": {"name": "Вода", "calories": 0, "protein": 0, "fat": 0, "carbs": 0},
    "сок апельсиновый": {"name": "Сок апельсиновый", "calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 10},
    "сок яблочный": {"name": "Сок яблочный", "calories": 46, "protein": 0.1, "fat": 0.1, "carbs": 11},
    "сок томатный": {"name": "Сок томатный", "calories": 17, "protein": 0.8, "fat": 0.1, "carbs": 3.5},
    "кофе": {"name": "Кофе (без сахара)", "calories": 2, "protein": 0.1, "fat": 0, "carbs": 0},
    "чай": {"name": "Чай (без сахара)", "calories": 1, "protein": 0, "fat": 0, "carbs": 0.3},
    "газировка": {"name": "Газировка (Кола)", "calories": 42, "protein": 0, "fat": 0, "carbs": 10.6},
    "квас": {"name": "Квас", "calories": 30, "protein": 0.2, "fat": 0, "carbs": 7},
    "пиво светлое": {"name": "Пиво светлое", "calories": 43, "protein": 0.5, "fat": 0, "carbs": 3.6},
    "вино красное сухое": {"name": "Вино красное сухое", "calories": 68, "protein": 0.1, "fat": 0, "carbs": 2.3},
    "вино белое сухое": {"name": "Вино белое сухое", "calories": 64, "protein": 0.1, "fat": 0, "carbs": 1.5},

    # ========== КОНСЕРВЫ ==========
    "тушёнка": {"name": "Тушёнка говяжья", "calories": 200, "protein": 15, "fat": 15, "carbs": 0},
    "шпроты": {"name": "Шпроты в масле", "calories": 300, "protein": 15, "fat": 25, "carbs": 0},
    "тунец консервированный": {"name": "Тунец консервированный", "calories": 150, "protein": 20, "fat": 7, "carbs": 0},
    "горошек консервированный": {"name": "Горошек зелёный консервированный", "calories": 60, "protein": 4, "fat": 0.5, "carbs": 10},
    "кукуруза консервированная": {"name": "Кукуруза консервированная", "calories": 70, "protein": 2, "fat": 1, "carbs": 15},
    "фасоль консервированная": {"name": "Фасоль консервированная", "calories": 90, "protein": 6, "fat": 0.5, "carbs": 15},
    "ананас консервированный": {"name": "Ананас консервированный", "calories": 60, "protein": 0.5, "fat": 0, "carbs": 15},
    "персик консервированный": {"name": "Персик консервированный", "calories": 70, "protein": 0.5, "fat": 0, "carbs": 18},
}

# ========== КЭШИРОВАНИЕ ПОИСКА ==========
def _get_cached_search(query: str) -> Optional[List[Dict]]:
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
    # Простейшее удаление окончаний (можно улучшить)
    for ending in ['а', 'ы', 'и', 'у', 'ом', 'е', 'ой', 'ей', 'ами', 'ах', 'ов', 'ев']:
        if query_lower.endswith(ending) and len(query_lower) > 4:
            normalized_query = query_lower[:-len(ending)]
            break

    for key, item in LOCAL_FOOD_DB.items():
        if query_lower == key:
            results.append({
                'name': item['name'],
                'calories': item['calories'],
                'protein': item['protein'],
                'fat': item['fat'],
                'carbs': item['carbs'],
                'source': 'local',
                'score': 1.0
            })
        elif query_lower in key:
            results.append({
                'name': item['name'],
                'calories': item['calories'],
                'protein': item['protein'],
                'fat': item['fat'],
                'carbs': item['carbs'],
                'source': 'local',
                'score': 0.9
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
                'score': 0.85
            })

    # Убираем дубликаты по имени
    seen = set()
    unique_results = []
    for r in results:
        if r['name'] not in seen:
            seen.add(r['name'])
            unique_results.append(r)

    unique_results.sort(key=lambda x: x['score'], reverse=True)
    return unique_results[:15]

async def search_food(query: str) -> List[Dict]:
    """Поиск только в локальной базе (OpenFoodFacts отключён)."""
    query = query.lower().strip()
    if not query:
        return []

    cached = _get_cached_search(query)
    if cached:
        return cached

    local_results = search_local_db(query)
    _cache_search(query, local_results[:10])
    return local_results[:10]

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
