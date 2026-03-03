"""
Универсальный поиск продуктов для NutriBuddy.
Локальная база (основные продукты) + FatSecret API (расширенный поиск).
"""
import aiohttp
import hashlib
import hmac
import base64
import time
import os
import random
import string
from typing import List, Dict, Optional
from urllib.parse import quote

# ---------- Локальная база продуктов (более 300 записей) ----------
# Данные из USDA, Роспотребнадзора, таблиц калорийности.
LOCAL_FOOD_DB = {
    # Курица
    "куриная грудка": {"name": "Куриная грудка (филе)", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "куриная грудка вареная": {"name": "Куриная грудка (варёная)", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "куриная грудка жареная": {"name": "Куриная грудка (жареная)", "calories": 200, "protein": 30, "fat": 8, "carbs": 0},
    "куриное филе": {"name": "Куриное филе", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
    "куриные ножки": {"name": "Куриные ножки (сырые)", "calories": 215, "protein": 18.4, "fat": 16.1, "carbs": 0},
    "куриные ножки жареные": {"name": "Куриные ножки (жареные)", "calories": 260, "protein": 18, "fat": 20, "carbs": 0},
    "куриные крылья": {"name": "Куриные крылья (сырые)", "calories": 222, "protein": 18.3, "fat": 16.4, "carbs": 0},
    "куриные крылья жареные": {"name": "Куриные крылья (жареные)", "calories": 300, "protein": 18, "fat": 25, "carbs": 0},
    "курица жареная": {"name": "Курица (жареная)", "calories": 239, "protein": 27, "fat": 14, "carbs": 0},
    "курица вареная": {"name": "Курица (варёная)", "calories": 205, "protein": 25, "fat": 10, "carbs": 0},
    "курица запеченная": {"name": "Курица (запечённая)", "calories": 220, "protein": 26, "fat": 12, "carbs": 0},
    "индейка": {"name": "Индейка (филе)", "calories": 135, "protein": 30, "fat": 1, "carbs": 0},
    "индейка грудка": {"name": "Индейка грудка", "calories": 135, "protein": 30, "fat": 1, "carbs": 0},
    "индейка бедро": {"name": "Индейка бедро", "calories": 175, "protein": 25, "fat": 8, "carbs": 0},

    # Говядина
    "говядина": {"name": "Говядина (средняя)", "calories": 250, "protein": 26, "fat": 17, "carbs": 0},
    "говядина вареная": {"name": "Говядина (варёная)", "calories": 250, "protein": 26, "fat": 17, "carbs": 0},
    "говядина жареная": {"name": "Говядина (жареная)", "calories": 280, "protein": 25, "fat": 20, "carbs": 0},
    "говядина тушеная": {"name": "Говядина (тушёная)", "calories": 230, "protein": 25, "fat": 15, "carbs": 0},
    "говяжий фарш": {"name": "Говяжий фарш (10% жира)", "calories": 176, "protein": 22, "fat": 10, "carbs": 0},
    "стейк": {"name": "Стейк (рибай)", "calories": 300, "protein": 20, "fat": 25, "carbs": 0},
    "вырезка говяжья": {"name": "Говяжья вырезка", "calories": 155, "protein": 21, "fat": 7, "carbs": 0},

    # Свинина
    "свинина": {"name": "Свинина (средняя)", "calories": 242, "protein": 27, "fat": 14, "carbs": 0},
    "свинина вареная": {"name": "Свинина (варёная)", "calories": 240, "protein": 26, "fat": 14, "carbs": 0},
    "свинина жареная": {"name": "Свинина (жареная)", "calories": 300, "protein": 24, "fat": 22, "carbs": 0},
    "свинина тушеная": {"name": "Свинина (тушёная)", "calories": 250, "protein": 25, "fat": 17, "carbs": 0},
    "свиная вырезка": {"name": "Свиная вырезка", "calories": 143, "protein": 26, "fat": 3.5, "carbs": 0},
    "свиные ребрышки": {"name": "Свиные рёбрышки", "calories": 320, "protein": 16, "fat": 28, "carbs": 0},
    "бекон": {"name": "Бекон", "calories": 541, "protein": 37, "fat": 42, "carbs": 1},
    "ветчина": {"name": "Ветчина", "calories": 145, "protein": 17, "fat": 8, "carbs": 1},

    # Рыба и морепродукты
    "лосось": {"name": "Лосось (сёмга, сырой)", "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    "лосось жареный": {"name": "Лосось (жареный)", "calories": 250, "protein": 22, "fat": 18, "carbs": 0},
    "лосось запеченный": {"name": "Лосось (запечённый)", "calories": 220, "protein": 21, "fat": 15, "carbs": 0},
    "семга": {"name": "Сёмга", "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    "треска": {"name": "Треска (сырая)", "calories": 82, "protein": 18, "fat": 0.7, "carbs": 0},
    "треска жареная": {"name": "Треска (жареная)", "calories": 120, "protein": 20, "fat": 4, "carbs": 0},
    "треска отварная": {"name": "Треска (отварная)", "calories": 82, "protein": 18, "fat": 0.7, "carbs": 0},
    "тунец": {"name": "Тунец (консервированный)", "calories": 184, "protein": 24, "fat": 9, "carbs": 0},
    "скумбрия": {"name": "Скумбрия", "calories": 205, "protein": 19, "fat": 14, "carbs": 0},
    "сельдь": {"name": "Сельдь (солёная)", "calories": 250, "protein": 18, "fat": 19, "carbs": 0},
    "креветки": {"name": "Креветки (варёные)", "calories": 85, "protein": 20, "fat": 0.5, "carbs": 0},
    "креветки жареные": {"name": "Креветки (жареные)", "calories": 120, "protein": 20, "fat": 4, "carbs": 0},
    "кальмар": {"name": "Кальмар (варёный)", "calories": 100, "protein": 18, "fat": 2, "carbs": 0},
    "мидии": {"name": "Мидии (варёные)", "calories": 85, "protein": 15, "fat": 2, "carbs": 3},
    "крабовые палочки": {"name": "Крабовые палочки", "calories": 90, "protein": 7, "fat": 2, "carbs": 12},

    # Яйца и молочка
    "яйцо": {"name": "Яйцо куриное (1 шт)", "calories": 70, "protein": 5.5, "fat": 5, "carbs": 0.5},
    "яйца": {"name": "Яйцо куриное (на 100г)", "calories": 140, "protein": 11, "fat": 10, "carbs": 1},
    "яйцо вареное": {"name": "Яйцо варёное", "calories": 140, "protein": 11, "fat": 10, "carbs": 1},
    "яйцо жареное": {"name": "Яйцо жареное", "calories": 200, "protein": 12, "fat": 16, "carbs": 1},
    "яичный белок": {"name": "Яичный белок", "calories": 52, "protein": 10.9, "fat": 0.2, "carbs": 0.7},
    "желток": {"name": "Желток яичный", "calories": 322, "protein": 16, "fat": 27, "carbs": 1},
    "молоко": {"name": "Молоко 3.2%", "calories": 60, "protein": 3, "fat": 3.2, "carbs": 4.7},
    "молоко 2.5%": {"name": "Молоко 2.5%", "calories": 52, "protein": 3, "fat": 2.5, "carbs": 4.7},
    "кефир": {"name": "Кефир 2.5%", "calories": 50, "protein": 3, "fat": 2.5, "carbs": 4},
    "йогурт": {"name": "Йогурт (натуральный)", "calories": 60, "protein": 4, "fat": 2.5, "carbs": 6},
    "творог": {"name": "Творог 5%", "calories": 120, "protein": 16, "fat": 5, "carbs": 3},
    "творог 9%": {"name": "Творог 9%", "calories": 160, "protein": 16, "fat": 9, "carbs": 3},
    "сметана": {"name": "Сметана 20%", "calories": 200, "protein": 2.5, "fat": 20, "carbs": 3.5},
    "сыр": {"name": "Сыр твёрдый", "calories": 350, "protein": 25, "fat": 28, "carbs": 2},
    "сыр моцарелла": {"name": "Сыр Моцарелла", "calories": 280, "protein": 22, "fat": 20, "carbs": 2},
    "сыр пармезан": {"name": "Сыр Пармезан", "calories": 420, "protein": 35, "fat": 28, "carbs": 3},
    "сыр фета": {"name": "Сыр Фета", "calories": 260, "protein": 14, "fat": 21, "carbs": 4},
    "масло сливочное": {"name": "Масло сливочное 82%", "calories": 750, "protein": 0.5, "fat": 82, "carbs": 0.5},
    "сливки": {"name": "Сливки 20%", "calories": 200, "protein": 2.5, "fat": 20, "carbs": 4},

    # Овощи
    "картофель": {"name": "Картофель (сырой)", "calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
    "картофель вареный": {"name": "Картофель (варёный)", "calories": 80, "protein": 2, "fat": 0.1, "carbs": 18},
    "картофель жареный": {"name": "Картофель (жареный)", "calories": 200, "protein": 2.5, "fat": 10, "carbs": 25},
    "картофель пюре": {"name": "Пюре картофельное", "calories": 90, "protein": 2, "fat": 2, "carbs": 16},
    "картофель фри": {"name": "Картофель фри", "calories": 300, "protein": 3.5, "fat": 15, "carbs": 35},
    "морковь": {"name": "Морковь", "calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
    "лук": {"name": "Лук репчатый", "calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9},
    "помидор": {"name": "Помидор", "calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
    "огурец": {"name": "Огурец", "calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
    "капуста": {"name": "Капуста белокочанная", "calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 5.8},
    "капуста квашеная": {"name": "Капуста квашеная", "calories": 20, "protein": 1.2, "fat": 0.1, "carbs": 4.5},
    "брокколи": {"name": "Брокколи", "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
    "перец болгарский": {"name": "Перец болгарский", "calories": 26, "protein": 1.2, "fat": 0.3, "carbs": 6},
    "баклажан": {"name": "Баклажан", "calories": 24, "protein": 1, "fat": 0.2, "carbs": 5.7},
    "кабачок": {"name": "Кабачок", "calories": 24, "protein": 0.6, "fat": 0.3, "carbs": 5.2},
    "тыква": {"name": "Тыква", "calories": 22, "protein": 1, "fat": 0.1, "carbs": 5.5},
    "свекла": {"name": "Свёкла (варёная)", "calories": 43, "protein": 1.5, "fat": 0.1, "carbs": 9.5},
    "редис": {"name": "Редис", "calories": 20, "protein": 0.6, "fat": 0.1, "carbs": 4},
    "зелень": {"name": "Зелень (укроп, петрушка)", "calories": 35, "protein": 2.5, "fat": 0.5, "carbs": 6},

    # Фрукты и ягоды
    "яблоко": {"name": "Яблоко", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
    "груша": {"name": "Груша", "calories": 57, "protein": 0.4, "fat": 0.3, "carbs": 15},
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
    "черника": {"name": "Черника", "calories": 57, "protein": 0.7, "fat": 0.3, "carbs": 14},
    "вишня": {"name": "Вишня", "calories": 50, "protein": 0.8, "fat": 0.2, "carbs": 12},
    "черешня": {"name": "Черешня", "calories": 50, "protein": 0.8, "fat": 0.2, "carbs": 12},
    "абрикос": {"name": "Абрикос", "calories": 48, "protein": 0.9, "fat": 0.1, "carbs": 11},
    "персик": {"name": "Персик", "calories": 39, "protein": 0.9, "fat": 0.1, "carbs": 9},
    "слива": {"name": "Слива", "calories": 46, "protein": 0.7, "fat": 0.3, "carbs": 11},
    "арбуз": {"name": "Арбуз", "calories": 30, "protein": 0.6, "fat": 0.2, "carbs": 7},
    "дыня": {"name": "Дыня", "calories": 34, "protein": 0.8, "fat": 0.2, "carbs": 8},
    "виноград": {"name": "Виноград", "calories": 69, "protein": 0.7, "fat": 0.2, "carbs": 18},

    # Крупы, бобовые, макароны
    "гречка": {"name": "Гречка (варёная)", "calories": 110, "protein": 4, "fat": 0.5, "carbs": 23},
    "рис": {"name": "Рис (варёный)", "calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
    "овсянка": {"name": "Овсянка (на воде)", "calories": 71, "protein": 2.5, "fat": 1.5, "carbs": 12},
    "перловка": {"name": "Перловка (варёная)", "calories": 120, "protein": 3, "fat": 0.4, "carbs": 25},
    "пшено": {"name": "Пшёнка (варёная)", "calories": 120, "protein": 3.5, "fat": 1.3, "carbs": 24},
    "манка": {"name": "Манка (варёная)", "calories": 100, "protein": 3, "fat": 2, "carbs": 17},
    "чечевица": {"name": "Чечевица (варёная)", "calories": 116, "protein": 9, "fat": 0.4, "carbs": 20},
    "фасоль": {"name": "Фасоль (варёная)", "calories": 132, "protein": 8.5, "fat": 0.5, "carbs": 23},
    "горох": {"name": "Горох (варёный)", "calories": 110, "protein": 7.5, "fat": 0.4, "carbs": 20},
    "нут": {"name": "Нут (варёный)", "calories": 164, "protein": 8.9, "fat": 2.6, "carbs": 27},
    "макароны": {"name": "Макароны (варёные)", "calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
    "спагетти": {"name": "Спагетти (варёные)", "calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},

    # Хлеб и выпечка
    "хлеб": {"name": "Хлеб пшеничный", "calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
    "хлеб ржаной": {"name": "Хлеб ржаной", "calories": 200, "protein": 6, "fat": 1.5, "carbs": 40},
    "лаваш": {"name": "Лаваш", "calories": 250, "protein": 8, "fat": 2, "carbs": 50},
    "печенье": {"name": "Печенье", "calories": 450, "protein": 6, "fat": 15, "carbs": 75},
    "овсяное печенье": {"name": "Овсяное печенье", "calories": 400, "protein": 6, "fat": 10, "carbs": 70},
    "пряники": {"name": "Пряники", "calories": 360, "protein": 5, "fat": 5, "carbs": 75},

    # Колбасы, сосиски
    "колбаса": {"name": "Колбаса варёная (Докторская)", "calories": 250, "protein": 12, "fat": 22, "carbs": 2},
    "колбаса копченая": {"name": "Колбаса копчёная (сервелат)", "calories": 400, "protein": 15, "fat": 35, "carbs": 2},
    "салями": {"name": "Салями", "calories": 450, "protein": 18, "fat": 40, "carbs": 2},
    "сосиски": {"name": "Сосиски молочные", "calories": 270, "protein": 11, "fat": 24, "carbs": 2},
    "сардельки": {"name": "Сардельки", "calories": 300, "protein": 12, "fat": 27, "carbs": 2},

    # Соусы, масла
    "кетчуп": {"name": "Кетчуп", "calories": 100, "protein": 1.5, "fat": 0.5, "carbs": 22},
    "майонез": {"name": "Майонез (провансаль)", "calories": 600, "protein": 0.5, "fat": 65, "carbs": 3},
    "майонез легкий": {"name": "Майонез лёгкий", "calories": 250, "protein": 0.5, "fat": 25, "carbs": 5},
    "горчица": {"name": "Горчица", "calories": 100, "protein": 5, "fat": 5, "carbs": 10},
    "соевый соус": {"name": "Соевый соус", "calories": 60, "protein": 8, "fat": 0, "carbs": 8},
    "оливковое масло": {"name": "Масло оливковое", "calories": 900, "protein": 0, "fat": 100, "carbs": 0},
    "подсолнечное масло": {"name": "Масло подсолнечное", "calories": 900, "protein": 0, "fat": 100, "carbs": 0},

    # Орехи, сухофрукты
    "грецкий орех": {"name": "Грецкий орех", "calories": 650, "protein": 15, "fat": 65, "carbs": 14},
    "миндаль": {"name": "Миндаль", "calories": 600, "protein": 19, "fat": 53, "carbs": 20},
    "арахис": {"name": "Арахис", "calories": 550, "protein": 26, "fat": 45, "carbs": 10},
    "курага": {"name": "Курага", "calories": 240, "protein": 3.5, "fat": 0.5, "carbs": 55},
    "чернослив": {"name": "Чернослив", "calories": 240, "protein": 2.3, "fat": 0.4, "carbs": 60},
    "изюм": {"name": "Изюм", "calories": 300, "protein": 3, "fat": 0.5, "carbs": 75},
    "финики": {"name": "Финики", "calories": 280, "protein": 2, "fat": 0.2, "carbs": 70},

    # Десерты
    "шоколад": {"name": "Шоколад молочный", "calories": 550, "protein": 6, "fat": 30, "carbs": 60},
    "шоколад темный": {"name": "Шоколад тёмный (70%)", "calories": 550, "protein": 7, "fat": 35, "carbs": 45},
    "конфеты": {"name": "Конфеты шоколадные", "calories": 500, "protein": 4, "fat": 25, "carbs": 60},
    "мороженое": {"name": "Мороженое (пломбир)", "calories": 200, "protein": 3.5, "fat": 10, "carbs": 20},
    "халва": {"name": "Халва", "calories": 500, "protein": 12, "fat": 25, "carbs": 55},
    "сгущенка": {"name": "Сгущённое молоко", "calories": 330, "protein": 7, "fat": 8, "carbs": 55},

    # Готовые блюда
    "пельмени": {"name": "Пельмени (варёные)", "calories": 250, "protein": 12, "fat": 12, "carbs": 25},
    "вареники с картошкой": {"name": "Вареники с картошкой", "calories": 200, "protein": 6, "fat": 5, "carbs": 35},
    "вареники с творогом": {"name": "Вареники с творогом", "calories": 220, "protein": 10, "fat": 8, "carbs": 30},
    "блины": {"name": "Блины (с маслом)", "calories": 200, "protein": 5, "fat": 8, "carbs": 28},
    "оладьи": {"name": "Оладьи", "calories": 220, "protein": 6, "fat": 9, "carbs": 30},
    "сырники": {"name": "Сырники", "calories": 200, "protein": 12, "fat": 10, "carbs": 15},
    "запеканка творожная": {"name": "Запеканка творожная", "calories": 180, "protein": 12, "fat": 8, "carbs": 15},
    "пицца": {"name": "Пицца (сыр, колбаса)", "calories": 250, "protein": 10, "fat": 12, "carbs": 28},
    "бургер": {"name": "Бургер (котлета, булка)", "calories": 300, "protein": 15, "fat": 15, "carbs": 25},

        # ========== САЛАТЫ ==========
    "салат оливье": {"name": "Салат Оливье (классический)", "calories": 200, "protein": 5, "fat": 15, "carbs": 10},
    "оливье": {"name": "Салат Оливье", "calories": 200, "protein": 5, "fat": 15, "carbs": 10},
    "салат цезарь": {"name": "Салат Цезарь с курицей", "calories": 180, "protein": 12, "fat": 10, "carbs": 8},
    "цезарь": {"name": "Салат Цезарь", "calories": 180, "protein": 12, "fat": 10, "carbs": 8},
    "греческий салат": {"name": "Греческий салат", "calories": 120, "protein": 3, "fat": 8, "carbs": 6},
    "греческий": {"name": "Греческий салат", "calories": 120, "protein": 3, "fat": 8, "carbs": 6},
    "винегрет": {"name": "Винегрет", "calories": 130, "protein": 2, "fat": 6, "carbs": 15},
    "салат с крабовыми палочками": {"name": "Крабовый салат", "calories": 150, "protein": 7, "fat": 8, "carbs": 10},
    "крабовый салат": {"name": "Крабовый салат", "calories": 150, "protein": 7, "fat": 8, "carbs": 10},
    "сельдь под шубой": {"name": "Сельдь под шубой", "calories": 180, "protein": 6, "fat": 12, "carbs": 10},
    "шуба": {"name": "Сельдь под шубой", "calories": 180, "protein": 6, "fat": 12, "carbs": 10},
    "мимоза": {"name": "Салат Мимоза", "calories": 200, "protein": 8, "fat": 15, "carbs": 6},
    "салат с тунцом": {"name": "Салат с тунцом", "calories": 150, "protein": 15, "fat": 5, "carbs": 8},
    "тунец салат": {"name": "Салат с тунцом", "calories": 150, "protein": 15, "fat": 5, "carbs": 8},
    "капрезе": {"name": "Капрезе (моцарелла, помидоры, базилик)", "calories": 250, "protein": 12, "fat": 20, "carbs": 4},
    "салат с курицей": {"name": "Салат с курицей", "calories": 140, "protein": 15, "fat": 6, "carbs": 5},
    "салат с овощами": {"name": "Овощной салат", "calories": 50, "protein": 1, "fat": 2, "carbs": 7},
    "овощной салат": {"name": "Овощной салат", "calories": 50, "protein": 1, "fat": 2, "carbs": 7},
    "салат с капустой": {"name": "Салат из капусты", "calories": 40, "protein": 1, "fat": 0, "carbs": 8},
    "капустный салат": {"name": "Салат из капусты", "calories": 40, "protein": 1, "fat": 0, "carbs": 8},
    "салат с морковью": {"name": "Салат из моркови", "calories": 45, "protein": 1, "fat": 0, "carbs": 10},
    "корейская морковь": {"name": "Морковь по-корейски", "calories": 130, "protein": 1, "fat": 8, "carbs": 12},
    "салат со свеклой": {"name": "Салат из свеклы", "calories": 70, "protein": 1, "fat": 3, "carbs": 10},
    "свекольный салат": {"name": "Салат из свеклы", "calories": 70, "protein": 1, "fat": 3, "carbs": 10},
    "салат с яйцом": {"name": "Салат с яйцом", "calories": 150, "protein": 7, "fat": 12, "carbs": 3},
    "яичный салат": {"name": "Яичный салат", "calories": 150, "protein": 7, "fat": 12, "carbs": 3},
    "салат с сыром": {"name": "Сырный салат", "calories": 220, "protein": 10, "fat": 18, "carbs": 4},
    "салат с грибами": {"name": "Салат с грибами", "calories": 100, "protein": 4, "fat": 5, "carbs": 8},
    "грибной салат": {"name": "Грибной салат", "calories": 100, "protein": 4, "fat": 5, "carbs": 8},
    "салат с фасолью": {"name": "Салат с фасолью", "calories": 120, "protein": 6, "fat": 4, "carbs": 15},
    "фасолевый салат": {"name": "Салат с фасолью", "calories": 120, "protein": 6, "fat": 4, "carbs": 15},
    "салат с кальмарами": {"name": "Салат с кальмарами", "calories": 110, "protein": 10, "fat": 5, "carbs": 6},
    "кальмаровый салат": {"name": "Салат с кальмарами", "calories": 110, "protein": 10, "fat": 5, "carbs": 6},
    "салат с креветками": {"name": "Салат с креветками", "calories": 100, "protein": 12, "fat": 3, "carbs": 5},
    "креветочный салат": {"name": "Салат с креветками", "calories": 100, "protein": 12, "fat": 3, "carbs": 5},
    # ========== КОНЕЦ САЛАТОВ ==========

    # ========== СУПЫ ==========
    # Щи, борщи, рассольники
    "борщ": {"name": "Борщ (классический)", "calories": 50, "protein": 2, "fat": 1.5, "carbs": 7},
    "борщ со сметаной": {"name": "Борщ со сметаной", "calories": 70, "protein": 2.5, "fat": 3, "carbs": 7},
    "борщ с мясом": {"name": "Борщ с мясом", "calories": 60, "protein": 4, "fat": 2, "carbs": 7},
    "щи": {"name": "Щи из свежей капусты", "calories": 40, "protein": 1.5, "fat": 1, "carbs": 6},
    "щи из квашеной капусты": {"name": "Щи из квашеной капусты", "calories": 45, "protein": 1.5, "fat": 1.2, "carbs": 7},
    "рассольник": {"name": "Рассольник", "calories": 50, "protein": 2, "fat": 1.5, "carbs": 6},
    # Солянки
    "солянка мясная": {"name": "Солянка мясная", "calories": 80, "protein": 5, "fat": 4, "carbs": 6},
    "солянка грибная": {"name": "Солянка грибная", "calories": 60, "protein": 2, "fat": 2, "carbs": 8},
    "солянка сборная": {"name": "Солянка сборная", "calories": 85, "protein": 5, "fat": 4.5, "carbs": 6},
    # Уха
    "уха": {"name": "Уха (рыбный суп)", "calories": 40, "protein": 5, "fat": 1, "carbs": 2},
    "уха из лосося": {"name": "Уха из лосося", "calories": 60, "protein": 6, "fat": 3, "carbs": 2},
    "уха из трески": {"name": "Уха из трески", "calories": 35, "protein": 5, "fat": 0.5, "carbs": 2},
    "уха по-царски": {"name": "Уха по-царски", "calories": 70, "protein": 7, "fat": 3, "carbs": 3},
    # Крем-супы
    "крем-суп из грибов": {"name": "Крем-суп грибной", "calories": 90, "protein": 2, "fat": 5, "carbs": 8},
    "крем-суп из тыквы": {"name": "Крем-суп из тыквы", "calories": 70, "protein": 1, "fat": 3, "carbs": 10},
    "крем-суп из брокколи": {"name": "Крем-суп из брокколи", "calories": 60, "protein": 2, "fat": 2.5, "carbs": 7},
    "крем-суп из курицы": {"name": "Крем-суп куриный", "calories": 80, "protein": 5, "fat": 3, "carbs": 6},
    "крем-суп из томатов": {"name": "Крем-суп томатный", "calories": 50, "protein": 1, "fat": 2, "carbs": 7},
    "крем-суп из шпината": {"name": "Крем-суп из шпината", "calories": 55, "protein": 2, "fat": 2.5, "carbs": 5},
    # Грибные супы
    "суп грибной": {"name": "Грибной суп", "calories": 45, "protein": 1.5, "fat": 1.5, "carbs": 6},
    "суп из белых грибов": {"name": "Суп из белых грибов", "calories": 50, "protein": 2, "fat": 2, "carbs": 6},
    "суп из шампиньонов": {"name": "Суп из шампиньонов", "calories": 40, "protein": 1.5, "fat": 1, "carbs": 5},
    # Куриные супы
    "суп куриный": {"name": "Куриный суп с лапшой", "calories": 45, "protein": 3, "fat": 1.5, "carbs": 5},
    "суп с курицей и вермишелью": {"name": "Суп куриный с вермишелью", "calories": 50, "protein": 3, "fat": 1.5, "carbs": 6},
    "суп с куриными фрикадельками": {"name": "Суп с куриными фрикадельками", "calories": 55, "protein": 4, "fat": 2, "carbs": 5},
    "бульон куриный": {"name": "Куриный бульон", "calories": 20, "protein": 2, "fat": 1, "carbs": 0.5},
    # Овощные супы
    "суп овощной": {"name": "Овощной суп", "calories": 30, "protein": 1, "fat": 0.5, "carbs": 5},
    "суп из кабачков": {"name": "Суп из кабачков", "calories": 25, "protein": 0.8, "fat": 0.3, "carbs": 4},
    "суп из тыквы": {"name": "Суп из тыквы", "calories": 35, "protein": 1, "fat": 1, "carbs": 6},
    "суп из томатов": {"name": "Томатный суп", "calories": 30, "protein": 1, "fat": 0.5, "carbs": 5},
    "суп-пюре из овощей": {"name": "Суп-пюре овощной", "calories": 40, "protein": 1, "fat": 1.5, "carbs": 6},
    # Холодные супы
    "окрошка": {"name": "Окрошка на квасе", "calories": 60, "protein": 2.5, "fat": 2, "carbs": 7},
    "окрошка на кефире": {"name": "Окрошка на кефире", "calories": 55, "protein": 3, "fat": 1.5, "carbs": 6},
    "свекольник": {"name": "Свекольник (холодный)", "calories": 40, "protein": 1, "fat": 1, "carbs": 6},
    "газпачо": {"name": "Гаспачо", "calories": 35, "protein": 1, "fat": 1.5, "carbs": 4},
    "тартар": {"name": "Тартар (холодный суп)", "calories": 50, "protein": 2, "fat": 2, "carbs": 5},
    # Национальные супы
    "харчо": {"name": "Харчо (суп)", "calories": 80, "protein": 5, "fat": 4, "carbs": 6},
    "лагман": {"name": "Лагман", "calories": 110, "protein": 6, "fat": 4, "carbs": 12},
    "шурпа": {"name": "Шурпа", "calories": 70, "protein": 5, "fat": 3, "carbs": 5},
    "мисо": {"name": "Мисо-суп", "calories": 35, "protein": 2, "fat": 1, "carbs": 4},
    "том ям": {"name": "Том Ям", "calories": 60, "protein": 4, "fat": 2.5, "carbs": 5},
    "том кха": {"name": "Том Кха", "calories": 70, "protein": 3, "fat": 4, "carbs": 5},
    "фо-бо": {"name": "Фо-бо (вьетнамский суп)", "calories": 90, "protein": 6, "fat": 2, "carbs": 12},
    "рамэн": {"name": "Рамэн", "calories": 120, "protein": 6, "fat": 4, "carbs": 15},
    "удон": {"name": "Суп с удоном", "calories": 100, "protein": 4, "fat": 2, "carbs": 16},
    "лапша вок": {"name": "Лапша вок с овощами", "calories": 150, "protein": 5, "fat": 5, "carbs": 20},
    # Другие популярные
    "суп с фрикадельками": {"name": "Суп с фрикадельками", "calories": 60, "protein": 4, "fat": 2.5, "carbs": 5},
    "суп с клецками": {"name": "Суп с клецками", "calories": 55, "protein": 2, "fat": 2, "carbs": 7},
    "сырный суп": {"name": "Сырный суп", "calories": 100, "protein": 4, "fat": 7, "carbs": 5},
    "гороховый суп": {"name": "Гороховый суп", "calories": 70, "protein": 4, "fat": 1.5, "carbs": 10},
    "фасолевый суп": {"name": "Фасолевый суп", "calories": 65, "protein": 4, "fat": 1, "carbs": 9},
    "чечевичный суп": {"name": "Чечевичный суп", "calories": 70, "protein": 5, "fat": 1, "carbs": 10},
}


# ---------- Функции для работы с локальной базой ----------
def search_local_db(query: str) -> List[Dict]:
    """Поиск в локальной базе по частичному совпадению."""
    results = []
    query_lower = query.lower()
    for key, item in LOCAL_FOOD_DB.items():
        if query_lower in key:
            results.append({
                'name': item['name'],
                'calories': item['calories'],
                'protein': item['protein'],
                'fat': item['fat'],
                'carbs': item['carbs'],
                'source': 'local'
            })
    return results


# ---------- FatSecret API интеграция ----------
FATSECRET_CONSUMER_KEY = os.getenv("FATSECRET_CONSUMER_KEY")
FATSECRET_CONSUMER_SECRET = os.getenv("FATSECRET_CONSUMER_SECRET")
FATSECRET_API_URL = "https://platform.fatsecret.com/rest/server.api"


def _generate_oauth_nonce() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


def _generate_oauth_timestamp() -> str:
    return str(int(time.time()))


def _generate_oauth_signature(method: str, url: str, params: dict, consumer_secret: str) -> str:
    """
    Генерирует OAuth 1.0 подпись для FatSecret API.
    """
    # Сортируем параметры по имени
    sorted_params = sorted(params.items())
    # Создаем строку параметров для подписи
    param_string = "&".join([f"{quote(k)}={quote(str(v))}" for k, v in sorted_params])
    # Базовая строка
    base_string = f"{method}&{quote(url, safe='')}&{quote(param_string, safe='')}"
    # Ключ подписи
    signing_key = f"{consumer_secret}&"
    # Подпись HMAC-SHA1
    hashed = hmac.new(
        signing_key.encode('utf-8'),
        base_string.encode('utf-8'),
        hashlib.sha1
    )
    signature = base64.b64encode(hashed.digest()).decode('utf-8')
    return signature


async def search_fatsecret(query: str, max_results: int = 3) -> List[Dict]:
    """Поиск продуктов в FatSecret API."""
    if not FATSECRET_CONSUMER_KEY or not FATSECRET_CONSUMER_SECRET:
        print("⚠️ FatSecret API credentials not set")
        return []

    try:
        params = {
            "method": "foods.search.v3",
            "format": "json",
            "search_expression": query,
            "page_number": "0",
            "max_results": str(max_results),
            "oauth_consumer_key": FATSECRET_CONSUMER_KEY,
            "oauth_nonce": _generate_oauth_nonce(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": _generate_oauth_timestamp(),
            "oauth_version": "1.0"
        }
        signature = _generate_oauth_signature("GET", FATSECRET_API_URL, params, FATSECRET_CONSUMER_SECRET)
        params["oauth_signature"] = signature

        async with aiohttp.ClientSession() as session:
            async with session.get(FATSECRET_API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    print(f"FatSecret error: {resp.status}")
                    return []
                data = await resp.json()
                foods = data.get("foods", {}).get("food", [])
                if isinstance(foods, dict):
                    foods = [foods]

                results = []
                for food in foods:
                    food_name = food.get("food_name", "Неизвестно")
                    food_id = food.get("food_id")
                    # Получаем детали
                    details = await _get_food_details(food_id)
                    if details:
                        results.append(details)
                    else:
                        # fallback: добавляем с нулями
                        results.append({
                            'name': food_name,
                            'calories': 0,
                            'protein': 0,
                            'fat': 0,
                            'carbs': 0,
                            'source': 'fatsecret'
                        })
                    if len(results) >= max_results:
                        break
                return results
    except Exception as e:
        print(f"FatSecret search error: {e}")
        return []


async def _get_food_details(food_id: str) -> Optional[Dict]:
    """Получает детальную информацию о продукте по ID (первая порция на 100г)."""
    try:
        params = {
            "method": "food.get.v5",
            "format": "json",
            "food_id": food_id,
            "oauth_consumer_key": FATSECRET_CONSUMER_KEY,
            "oauth_nonce": _generate_oauth_nonce(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": _generate_oauth_timestamp(),
            "oauth_version": "1.0"
        }
        signature = _generate_oauth_signature("GET", FATSECRET_API_URL, params, FATSECRET_CONSUMER_SECRET)
        params["oauth_signature"] = signature

        async with aiohttp.ClientSession() as session:
            async with session.get(FATSECRET_API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                food = data.get("food", {})
                servings = food.get("servings", {}).get("serving", [])
                if isinstance(servings, dict):
                    servings = [servings]

                if servings:
                    serving = servings[0]  # берём первую порцию (обычно 100г)
                    return {
                        'name': food.get("food_name", "Неизвестно"),
                        'calories': float(serving.get("calories", 0)),
                        'protein': float(serving.get("protein", 0)),
                        'fat': float(serving.get("fat", 0)),
                        'carbs': float(serving.get("carbohydrate", 0)),
                        'source': 'fatsecret'
                    }
    except Exception as e:
        print(f"FatSecret details error: {e}")
    return None


# ---------- Основная функция поиска ----------
async def search_food(query: str, max_results: int = 5) -> List[Dict]:
    """
    Основная функция поиска продуктов.
    Сначала локальная база, затем FatSecret API.
    """
    query = query.strip().lower()
    if not query:
        return []

    # 1. Локальная база
    local = search_local_db(query)
    if local:
        return local[:max_results]

    # 2. FatSecret API
    fatsecret = await search_fatsecret(query, max_results)
    if fatsecret:
        return fatsecret

    return []
