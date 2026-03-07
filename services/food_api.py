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
    "салат айсберг": {"name": "Салат Айсберг", "calories": 14, "protein": 1.0, "fat": 0.1, "carbs": 2.0},
    "салат романо": {"name": "Салат Романо", "calories": 17, "protein": 1.5, "fat": 0.3, "carbs": 2.5},
    "руккола": {"name": "Руккола", "calories": 25, "protein": 2.5, "fat": 0.5, "carbs": 3.5},
    "шпинат": {"name": "Шпинат", "calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6},
    "зелень": {"name": "Зелень (укроп, петрушка)", "calories": 35, "protein": 2.5, "fat": 0.5, "carbs": 6.0},
    "укроп": {"name": "Укроп", "calories": 43, "protein": 3.5, "fat": 1.1, "carbs": 7.0},
    "петрушка": {"name": "Петрушка", "calories": 36, "protein": 3.0, "fat": 0.8, "carbs": 6.0},
    "кинза": {"name": "Кинза", "calories": 23, "protein": 2.1, "fat": 0.5, "carbs": 3.7},
    "базилик": {"name": "Базилик", "calories": 44, "protein": 2.5, "fat": 0.6, "carbs": 5.1},
    "мята": {"name": "Мята", "calories": 70, "protein": 3.8, "fat": 0.9, "carbs": 15.0},
    "тимьян": {"name": "Тимьян", "calories": 101, "protein": 5.6, "fat": 1.7, "carbs": 24.0},
    "розмарин": {"name": "Розмарин", "calories": 131, "protein": 3.3, "fat": 5.9, "carbs": 21.0},
    "щавель": {"name": "Щавель", "calories": 22, "protein": 2.0, "fat": 0.7, "carbs": 3.0},
    "портулак": {"name": "Портулак", "calories": 20, "protein": 2.0, "fat": 0.4, "carbs": 3.4},
    "мангольд": {"name": "Мангольд (листовая свекла)", "calories": 19, "protein": 1.8, "fat": 0.2, "carbs": 3.7},
    "крапива": {"name": "Крапива молодая", "calories": 42, "protein": 2.7, "fat": 0.1, "carbs": 7.5},
    "черемша": {"name": "Черемша", "calories": 35, "protein": 2.4, "fat": 0.1, "carbs": 6.5},
    "салат фризе": {"name": "Салат Фризе", "calories": 15, "protein": 1.2, "fat": 0.2, "carbs": 2.5},
    "салат корн": {"name": "Салат Корн (полевой)", "calories": 21, "protein": 2.0, "fat": 0.4, "carbs": 3.6},
    "салат латук": {"name": "Салат Латук", "calories": 15, "protein": 1.4, "fat": 0.2, "carbs": 2.0},
    "эскариоль": {"name": "Эскариоль", "calories": 17, "protein": 1.2, "fat": 0.2, "carbs": 3.0},
    "радиккьо": {"name": "Радиккьо", "calories": 23, "protein": 1.4, "fat": 0.1, "carbs": 4.0},
    "кресс-салат": {"name": "Кресс-салат", "calories": 32, "protein": 2.6, "fat": 0.7, "carbs": 5.5},

    # ========== ОВОЩИ ==========
    "помидор": {"name": "Помидор", "calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
    "огурец": {"name": "Огурец", "calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
    "картофель": {"name": "Картофель", "calories": 77, "protein": 2.0, "fat": 0.1, "carbs": 17.0},
    "морковь": {"name": "Морковь", "calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10.0},
    "лук": {"name": "Лук репчатый", "calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9.0},
    "чеснок": {"name": "Чеснок", "calories": 149, "protein": 6.4, "fat": 0.5, "carbs": 33.0},
    "капуста": {"name": "Капуста белокочанная", "calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 5.8},
    "брокколи": {"name": "Брокколи", "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7.0},
    "цветная капуста": {"name": "Цветная капуста", "calories": 25, "protein": 2.0, "fat": 0.3, "carbs": 5.0},
    "баклажан": {"name": "Баклажан", "calories": 24, "protein": 1.0, "fat": 0.2, "carbs": 5.7},
    "кабачок": {"name": "Кабачок", "calories": 24, "protein": 0.6, "fat": 0.3, "carbs": 5.2},
    "перец болгарский": {"name": "Перец болгарский", "calories": 26, "protein": 1.2, "fat": 0.3, "carbs": 6.0},
    "перец чили": {"name": "Перец чили", "calories": 40, "protein": 2.0, "fat": 0.4, "carbs": 9.0},
    "тыква": {"name": "Тыква", "calories": 22, "protein": 1.0, "fat": 0.1, "carbs": 5.5},
    "свекла": {"name": "Свёкла", "calories": 43, "protein": 1.5, "fat": 0.1, "carbs": 9.5},
    "редис": {"name": "Редис", "calories": 20, "protein": 0.6, "fat": 0.1, "carbs": 4.0},
    "сельдерей": {"name": "Сельдерей (корень)", "calories": 42, "protein": 1.5, "fat": 0.3, "carbs": 9.2},
    "сельдерей стебель": {"name": "Сельдерей стеблевой", "calories": 16, "protein": 0.7, "fat": 0.2, "carbs": 3.0},
    "спаржа": {"name": "Спаржа", "calories": 20, "protein": 2.2, "fat": 0.2, "carbs": 4.0},
    "стручковая фасоль": {"name": "Стручковая фасоль", "calories": 31, "protein": 2.0, "fat": 0.2, "carbs": 7.0},
    "горошек": {"name": "Горошек зелёный", "calories": 60, "protein": 4.0, "fat": 0.5, "carbs": 10.0},
    "кукуруза": {"name": "Кукуруза сладкая", "calories": 70, "protein": 2.0, "fat": 1.0, "carbs": 15.0},
    "авокадо": {"name": "Авокадо", "calories": 160, "protein": 2.0, "fat": 15.0, "carbs": 9.0},
    "оливки": {"name": "Оливки", "calories": 150, "protein": 1.0, "fat": 15.0, "carbs": 3.0},
    "маслины": {"name": "Маслины", "calories": 150, "protein": 1.0, "fat": 15.0, "carbs": 3.0},
    "корнишоны": {"name": "Корнишоны маринованные", "calories": 30, "protein": 1.0, "fat": 0.0, "carbs": 5.0},
    "редиска": {"name": "Редиска", "calories": 20, "protein": 0.6, "fat": 0.1, "carbs": 4.0},
    "дайкон": {"name": "Дайкон (редис японский)", "calories": 18, "protein": 0.6, "fat": 0.1, "carbs": 4.1},
    "репа": {"name": "Репа", "calories": 32, "protein": 1.5, "fat": 0.1, "carbs": 6.3},
    "брюква": {"name": "Брюква", "calories": 37, "protein": 1.2, "fat": 0.1, "carbs": 8.0},
    "топинамбур": {"name": "Топинамбур (земляная груша)", "calories": 73, "protein": 2.0, "fat": 0.0, "carbs": 17.0},
    "батат": {"name": "Батат (сладкий картофель)", "calories": 86, "protein": 1.6, "fat": 0.1, "carbs": 20.0},
    "патиссон": {"name": "Патиссон", "calories": 19, "protein": 0.6, "fat": 0.1, "carbs": 4.3},
    "тыква мускатная": {"name": "Тыква мускатная", "calories": 45, "protein": 1.0, "fat": 0.1, "carbs": 12.0},
    "капуста краснокочанная": {"name": "Капуста краснокочанная", "calories": 31, "protein": 1.4, "fat": 0.2, "carbs": 7.0},
    "капуста савойская": {"name": "Капуста савойская", "calories": 28, "protein": 1.9, "fat": 0.1, "carbs": 6.0},
    "капуста пекинская": {"name": "Капуста пекинская", "calories": 16, "protein": 1.2, "fat": 0.2, "carbs": 3.0},
    "кольраби": {"name": "Кольраби", "calories": 27, "protein": 1.7, "fat": 0.1, "carbs": 6.2},
    "артишок": {"name": "Артишок", "calories": 47, "protein": 3.3, "fat": 0.2, "carbs": 11.0},
    "ревень": {"name": "Ревень", "calories": 16, "protein": 0.8, "fat": 0.1, "carbs": 3.8},
    "хрен": {"name": "Хрен (корень)", "calories": 58, "protein": 1.8, "fat": 0.4, "carbs": 13.0},
    "имбирь": {"name": "Имбирь (корень)", "calories": 80, "protein": 1.8, "fat": 0.8, "carbs": 18.0},
    "пастернак": {"name": "Пастернак (корень)", "calories": 75, "protein": 1.2, "fat": 0.5, "carbs": 18.0},
    "каперсы": {"name": "Каперсы маринованные", "calories": 23, "protein": 2.4, "fat": 0.9, "carbs": 5.0},
    "цуккини": {"name": "Цуккини", "calories": 21, "protein": 1.2, "fat": 0.3, "carbs": 3.1},

    # ========== ФРУКТЫ И ЯГОДЫ ==========
    "яблоко": {"name": "Яблоко", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14.0},
    "банан": {"name": "Банан", "calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23.0},
    "апельсин": {"name": "Апельсин", "calories": 47, "protein": 0.9, "fat": 0.1, "carbs": 12.0},
    "мандарин": {"name": "Мандарин", "calories": 38, "protein": 0.6, "fat": 0.2, "carbs": 9.0},
    "лимон": {"name": "Лимон", "calories": 29, "protein": 1.1, "fat": 0.3, "carbs": 9.0},
    "лайм": {"name": "Лайм", "calories": 30, "protein": 0.7, "fat": 0.2, "carbs": 11.0},
    "грейпфрут": {"name": "Грейпфрут", "calories": 42, "protein": 0.8, "fat": 0.1, "carbs": 11.0},
    "киви": {"name": "Киви", "calories": 61, "protein": 1.1, "fat": 0.5, "carbs": 15.0},
    "ананас": {"name": "Ананас", "calories": 50, "protein": 0.5, "fat": 0.1, "carbs": 13.0},
    "манго": {"name": "Манго", "calories": 60, "protein": 0.8, "fat": 0.4, "carbs": 15.0},
    "груша": {"name": "Груша", "calories": 57, "protein": 0.4, "fat": 0.1, "carbs": 15.0},
    "персик": {"name": "Персик", "calories": 39, "protein": 0.9, "fat": 0.3, "carbs": 10.0},
    "абрикос": {"name": "Абрикос", "calories": 48, "protein": 1.4, "fat": 0.4, "carbs": 11.0},
    "слива": {"name": "Слива", "calories": 46, "protein": 0.7, "fat": 0.3, "carbs": 11.0},
    "вишня": {"name": "Вишня", "calories": 50, "protein": 1.0, "fat": 0.3, "carbs": 12.0},
    "черешня": {"name": "Черешня", "calories": 50, "protein": 1.1, "fat": 0.4, "carbs": 12.0},
    "клубника": {"name": "Клубника", "calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 7.7},
    "малина": {"name": "Малина", "calories": 52, "protein": 1.2, "fat": 0.7, "carbs": 12.0},
    "ежевика": {"name": "Ежевика", "calories": 43, "protein": 1.4, "fat": 0.5, "carbs": 10.0},
    "голубика": {"name": "Голубика", "calories": 57, "protein": 0.7, "fat": 0.3, "carbs": 14.0},
    "клюква": {"name": "Клюква", "calories": 46, "protein": 0.4, "fat": 0.1, "carbs": 12.0},
    "смородина красная": {"name": "Смородина красная", "calories": 43, "protein": 0.6, "fat": 0.2, "carbs": 11.0},
    "смородина чёрная": {"name": "Смородина чёрная", "calories": 44, "protein": 1.0, "fat": 0.4, "carbs": 12.0},
    "крыжовник": {"name": "Крыжовник", "calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 12.0},
    "виноград": {"name": "Виноград", "calories": 69, "protein": 0.7, "fat": 0.2, "carbs": 18.0},
    "арбуз": {"name": "Арбуз", "calories": 30, "protein": 0.6, "fat": 0.2, "carbs": 8.0},
    "дыня": {"name": "Дыня", "calories": 34, "protein": 0.8, "fat": 0.2, "carbs": 8.0},
    "гранат": {"name": "Гранат", "calories": 83, "protein": 1.7, "fat": 1.2, "carbs": 19.0},
    "хурма": {"name": "Хурма", "calories": 70, "protein": 0.6, "fat": 0.2, "carbs": 18.0},
    "инжир": {"name": "Инжир", "calories": 74, "protein": 0.8, "fat": 0.3, "carbs": 19.0},
    "финики": {"name": "Финики", "calories": 280, "protein": 2.0, "fat": 0.2, "carbs": 70.0},
    "изюм": {"name": "Изюм", "calories": 300, "protein": 3.0, "fat": 0.5, "carbs": 75.0},
    "курага": {"name": "Курага", "calories": 240, "protein": 3.5, "fat": 0.5, "carbs": 55.0},
    "чернослив": {"name": "Чернослив", "calories": 240, "protein": 2.3, "fat": 0.4, "carbs": 60.0},
    "нектарин": {"name": "Нектарин", "calories": 44, "protein": 1.1, "fat": 0.3, "carbs": 10.5},
    "помело": {"name": "Помело", "calories": 38, "protein": 0.8, "fat": 0.0, "carbs": 9.6},
    "папайя": {"name": "Папайя", "calories": 43, "protein": 0.5, "fat": 0.3, "carbs": 11.0},
    "маракуйя": {"name": "Маракуйя", "calories": 97, "protein": 2.2, "fat": 0.7, "carbs": 23.0},
    "личи": {"name": "Личи", "calories": 66, "protein": 0.8, "fat": 0.4, "carbs": 16.5},
    "рамбутан": {"name": "Рамбутан", "calories": 82, "protein": 0.7, "fat": 0.2, "carbs": 20.0},
    "гуава": {"name": "Гуава", "calories": 68, "protein": 2.6, "fat": 1.0, "carbs": 14.0},
    "айва": {"name": "Айва", "calories": 57, "protein": 0.4, "fat": 0.1, "carbs": 15.0},
    "брусника": {"name": "Брусника", "calories": 46, "protein": 0.7, "fat": 0.5, "carbs": 9.6},
    "черника": {"name": "Черника", "calories": 44, "protein": 1.1, "fat": 0.6, "carbs": 11.0},
    "земляника": {"name": "Земляника", "calories": 34, "protein": 0.7, "fat": 0.4, "carbs": 7.5},
    "морошка": {"name": "Морошка", "calories": 40, "protein": 0.8, "fat": 0.9, "carbs": 7.4},
    "облепиха": {"name": "Облепиха", "calories": 82, "protein": 1.2, "fat": 5.4, "carbs": 5.7},
    "шиповник": {"name": "Шиповник (плоды)", "calories": 109, "protein": 1.6, "fat": 0.7, "carbs": 22.0},
    "кизил": {"name": "Кизил", "calories": 45, "protein": 1.0, "fat": 0.0, "carbs": 10.5},
    "барбарис": {"name": "Барбарис", "calories": 29, "protein": 0.0, "fat": 0.0, "carbs": 7.0},
    "шелковица": {"name": "Шелковица (тутовник)", "calories": 52, "protein": 0.7, "fat": 0.4, "carbs": 12.7},
    "ирга": {"name": "Ирга", "calories": 45, "protein": 0.0, "fat": 0.0, "carbs": 12.0},
    "рябина черноплодная": {"name": "Рябина черноплодная (арония)", "calories": 55, "protein": 1.5, "fat": 0.2, "carbs": 13.6},
    "рябина красная": {"name": "Рябина красная", "calories": 50, "protein": 1.4, "fat": 0.2, "carbs": 12.0},
    "калина": {"name": "Калина", "calories": 26, "protein": 0.0, "fat": 0.0, "carbs": 7.0},
    "фейхоа": {"name": "Фейхоа", "calories": 55, "protein": 1.0, "fat": 0.8, "carbs": 13.0},

    # ========== БОБОВЫЕ ==========
    "фасоль": {"name": "Фасоль (зерно)", "calories": 298, "protein": 21.0, "fat": 2.0, "carbs": 54.0},
    "фасоль красная": {"name": "Фасоль красная (варёная)", "calories": 127, "protein": 8.7, "fat": 0.5, "carbs": 22.8},
    "фасоль белая": {"name": "Фасоль белая (варёная)", "calories": 140, "protein": 8.2, "fat": 0.6, "carbs": 25.0},
    "горох": {"name": "Горох (лущеный)", "calories": 299, "protein": 20.0, "fat": 1.5, "carbs": 53.0},
    "горох колотый": {"name": "Горох колотый (варёный)", "calories": 118, "protein": 8.0, "fat": 0.4, "carbs": 20.0},
    "нут": {"name": "Нут (турецкий горох)", "calories": 364, "protein": 19.0, "fat": 6.0, "carbs": 61.0},
    "нут варёный": {"name": "Нут (варёный)", "calories": 164, "protein": 8.9, "fat": 2.6, "carbs": 27.4},
    "чечевица": {"name": "Чечевица (красная/зелёная)", "calories": 295, "protein": 24.0, "fat": 1.5, "carbs": 46.0},
    "чечевица варёная": {"name": "Чечевица (варёная)", "calories": 116, "protein": 9.0, "fat": 0.4, "carbs": 20.0},
    "маш": {"name": "Маш (бобы мунг)", "calories": 300, "protein": 23.0, "fat": 2.0, "carbs": 54.0},
    "маш варёный": {"name": "Маш (варёный)", "calories": 105, "protein": 7.0, "fat": 0.4, "carbs": 19.0},
    "соя": {"name": "Соя (бобы)", "calories": 446, "protein": 36.0, "fat": 20.0, "carbs": 30.0},
    "соя варёная": {"name": "Соя (варёная)", "calories": 173, "protein": 16.6, "fat": 9.0, "carbs": 10.0},
    "бобы": {"name": "Бобы конские", "calories": 341, "protein": 26.0, "fat": 1.5, "carbs": 58.0},

    # ========== ГРИБЫ ==========
    "грибы": {"name": "Грибы (свежие)", "calories": 25, "protein": 2.5, "fat": 0.5, "carbs": 3.0},
    "шампиньоны": {"name": "Шампиньоны", "calories": 27, "protein": 4.3, "fat": 1.0, "carbs": 1.0},
    "вешенки": {"name": "Вешенки", "calories": 33, "protein": 3.3, "fat": 0.4, "carbs": 6.0},
    "белые грибы": {"name": "Белые грибы (боровики)", "calories": 34, "protein": 3.7, "fat": 1.1, "carbs": 3.5},
    "подберезовики": {"name": "Подберёзовики", "calories": 31, "protein": 2.1, "fat": 0.8, "carbs": 3.7},
    "подосиновики": {"name": "Подосиновики", "calories": 30, "protein": 3.3, "fat": 0.5, "carbs": 3.5},
    "лисички": {"name": "Лисички", "calories": 32, "protein": 1.5, "fat": 1.0, "carbs": 3.0},
    "опята": {"name": "Опята", "calories": 22, "protein": 2.2, "fat": 1.2, "carbs": 2.5},
    "маслята": {"name": "Маслята", "calories": 24, "protein": 2.4, "fat": 0.7, "carbs": 3.2},
    "грузди": {"name": "Грузди", "calories": 18, "protein": 1.8, "fat": 0.5, "carbs": 2.5},
    "рыжики": {"name": "Рыжики", "calories": 22, "protein": 2.5, "fat": 0.5, "carbs": 2.6},
    "сморчки": {"name": "Сморчки", "calories": 27, "protein": 2.9, "fat": 0.4, "carbs": 4.2},
    "трюфели": {"name": "Трюфели", "calories": 75, "protein": 6.0, "fat": 4.0, "carbs": 8.0},
    "шиитаке": {"name": "Шиитаке (сушёные)", "calories": 300, "protein": 10.0, "fat": 1.0, "carbs": 70.0},
    "шиитаке свежие": {"name": "Шиитаке (свежие)", "calories": 34, "protein": 2.2, "fat": 0.5, "carbs": 6.8},

    # ========== ОРЕХИ И СЕМЕНА ==========
    "грецкий орех": {"name": "Грецкий орех", "calories": 654, "protein": 15.2, "fat": 65.2, "carbs": 13.7},
    "миндаль": {"name": "Миндаль", "calories": 609, "protein": 18.6, "fat": 53.7, "carbs": 21.3},
    "фундук": {"name": "Фундук (лещина)", "calories": 651, "protein": 15.0, "fat": 61.5, "carbs": 16.7},
    "кешью": {"name": "Кешью", "calories": 600, "protein": 18.5, "fat": 48.5, "carbs": 30.0},
    "фисташки": {"name": "Фисташки", "calories": 560, "protein": 20.0, "fat": 45.0, "carbs": 28.0},
    "арахис": {"name": "Арахис (земляной орех)", "calories": 567, "protein": 25.8, "fat": 49.2, "carbs": 16.1},
    "кедровый орех": {"name": "Кедровый орех", "calories": 673, "protein": 13.7, "fat": 68.4, "carbs": 13.1},
    "бразильский орех": {"name": "Бразильский орех", "calories": 659, "protein": 14.3, "fat": 67.1, "carbs": 12.3},
    "пекан": {"name": "Пекан", "calories": 691, "protein": 9.2, "fat": 72.0, "carbs": 13.9},
    "макадамия": {"name": "Макадамия", "calories": 718, "protein": 7.9, "fat": 75.8, "carbs": 13.8},
    "кокос": {"name": "Кокос (мякоть)", "calories": 354, "protein": 3.3, "fat": 33.5, "carbs": 15.2},
    "кокосовая стружка": {"name": "Кокосовая стружка", "calories": 592, "protein": 5.6, "fat": 46.5, "carbs": 44.4},
    "семена подсолнечника": {"name": "Семена подсолнечника", "calories": 584, "protein": 20.8, "fat": 51.5, "carbs": 20.0},
    "семена тыквы": {"name": "Семена тыквы (тыквенные семечки)", "calories": 559, "protein": 30.0, "fat": 49.0, "carbs": 11.0},
    "семена льна": {"name": "Семена льна", "calories": 534, "protein": 18.3, "fat": 42.2, "carbs": 28.9},
    "семена чиа": {"name": "Семена чиа", "calories": 486, "protein": 16.5, "fat": 30.7, "carbs": 42.1},
    "кунжут": {"name": "Кунжут (семена)", "calories": 573, "protein": 17.7, "fat": 49.7, "carbs": 23.4},
    "мак": {"name": "Мак (семена)", "calories": 525, "protein": 18.0, "fat": 41.6, "carbs": 28.0},
    "конопляное семя": {"name": "Семена конопли", "calories": 553, "protein": 31.6, "fat": 48.8, "carbs": 8.7},

    # ========== КРУПЫ, ЗЕРНОВЫЕ, МАКАРОНЫ ==========
    "гречка": {"name": "Гречневая крупа (ядрица)", "calories": 335, "protein": 12.6, "fat": 3.3, "carbs": 64.0},
    "гречка варёная": {"name": "Гречка отварная на воде", "calories": 110, "protein": 4.2, "fat": 1.1, "carbs": 21.3},
    "рис": {"name": "Рис (белый, шлифованный)", "calories": 360, "protein": 6.6, "fat": 0.7, "carbs": 79.0},
    "рис варёный": {"name": "Рис отварной на воде", "calories": 123, "protein": 2.5, "fat": 0.3, "carbs": 28.0},
    "рис бурый": {"name": "Рис бурый (нешлифованный)", "calories": 362, "protein": 7.5, "fat": 2.7, "carbs": 76.0},
    "рис дикий": {"name": "Рис дикий (чёрный)", "calories": 357, "protein": 14.7, "fat": 1.1, "carbs": 75.0},
    "овсянка": {"name": "Овсяные хлопья (геркулес)", "calories": 366, "protein": 11.9, "fat": 6.2, "carbs": 65.4},
    "овсянка варёная": {"name": "Овсяная каша на воде", "calories": 88, "protein": 3.0, "fat": 1.7, "carbs": 15.0},
    "пшено": {"name": "Пшено (пшённая крупа)", "calories": 348, "protein": 11.5, "fat": 3.3, "carbs": 69.0},
    "пшено варёное": {"name": "Пшённая каша на воде", "calories": 120, "protein": 3.6, "fat": 1.1, "carbs": 23.0},
    "перловка": {"name": "Перловая крупа", "calories": 320, "protein": 9.3, "fat": 1.1, "carbs": 73.0},
    "перловка варёная": {"name": "Перловка отварная", "calories": 123, "protein": 3.0, "fat": 0.4, "carbs": 28.0},
    "ячневая крупа": {"name": "Ячневая крупа", "calories": 324, "protein": 10.4, "fat": 1.3, "carbs": 71.0},
    "кукурузная крупа": {"name": "Кукурузная крупа", "calories": 337, "protein": 8.3, "fat": 1.2, "carbs": 75.0},
    "кукурузная каша": {"name": "Кукурузная каша на воде", "calories": 86, "protein": 2.0, "fat": 0.3, "carbs": 19.0},
    "манка": {"name": "Манная крупа", "calories": 328, "protein": 10.3, "fat": 1.0, "carbs": 70.6},
    "манка варёная": {"name": "Манная каша на воде", "calories": 80, "protein": 2.5, "fat": 0.2, "carbs": 17.0},
    "киноа": {"name": "Киноа (крупа)", "calories": 368, "protein": 14.1, "fat": 6.1, "carbs": 64.0},
    "киноа варёная": {"name": "Киноа отварная", "calories": 120, "protein": 4.4, "fat": 1.9, "carbs": 21.0},
    "булгур": {"name": "Булгур (крупа)", "calories": 342, "protein": 12.3, "fat": 1.3, "carbs": 75.9},
    "булгур варёный": {"name": "Булгур отварной", "calories": 109, "protein": 3.8, "fat": 0.4, "carbs": 24.0},
    "кускус": {"name": "Кускус (крупа)", "calories": 376, "protein": 12.8, "fat": 0.6, "carbs": 77.0},
    "кускус варёный": {"name": "Кускус отварной", "calories": 112, "protein": 3.8, "fat": 0.2, "carbs": 23.0},
    "полба": {"name": "Полба (крупа)", "calories": 338, "protein": 14.6, "fat": 2.4, "carbs": 70.0},
    "полба варёная": {"name": "Полба отварная", "calories": 127, "protein": 5.5, "fat": 0.9, "carbs": 26.0},
    "пшеничная крупа": {"name": "Пшеничная крупа (Артек, Полтавская)", "calories": 325, "protein": 11.0, "fat": 1.3, "carbs": 72.0},
    "пшеничная каша": {"name": "Пшеничная каша на воде", "calories": 105, "protein": 3.5, "fat": 0.4, "carbs": 22.0},
    "гранола": {"name": "Гранола (без сахара)", "calories": 450, "protein": 10.0, "fat": 15.0, "carbs": 65.0},
    "мюсли": {"name": "Мюсли (смесь злаков и сухофруктов)", "calories": 360, "protein": 9.0, "fat": 6.0, "carbs": 70.0},
    "макароны": {"name": "Макароны из твёрдых сортов пшеницы (сухие)", "calories": 350, "protein": 12.0, "fat": 1.5, "carbs": 72.0},
    "макароны отварные": {"name": "Макароны отварные", "calories": 140, "protein": 5.0, "fat": 0.6, "carbs": 28.0},
    "спагетти": {"name": "Спагетти (сухие)", "calories": 350, "protein": 12.0, "fat": 1.5, "carbs": 72.0},
    "спагетти отварные": {"name": "Спагетти отварные", "calories": 140, "protein": 5.0, "fat": 0.6, "carbs": 28.0},
    "лапша": {"name": "Лапша (сухая)", "calories": 350, "protein": 10.0, "fat": 1.0, "carbs": 74.0},
    "лапша отварная": {"name": "Лапша отварная", "calories": 140, "protein": 4.0, "fat": 0.4, "carbs": 30.0},
    "вермишель": {"name": "Вермишель (сухая)", "calories": 350, "protein": 10.0, "fat": 1.0, "carbs": 74.0},
    "вермишель отварная": {"name": "Вермишель отварная", "calories": 140, "protein": 4.0, "fat": 0.4, "carbs": 30.0},

    # ========== МОЛОЧНЫЕ ПРОДУКТЫ И ЯЙЦА ==========
    "молоко": {"name": "Молоко 3.2%", "calories": 60, "protein": 2.9, "fat": 3.2, "carbs": 4.7},
    "молоко 2.5%": {"name": "Молоко 2.5%", "calories": 54, "protein": 2.9, "fat": 2.5, "carbs": 4.7},
    "молоко 1.5%": {"name": "Молоко 1.5%", "calories": 45, "protein": 3.0, "fat": 1.5, "carbs": 4.7},
    "молоко 0.5%": {"name": "Молоко обезжиренное", "calories": 35, "protein": 3.0, "fat": 0.5, "carbs": 4.8},
    "кефир": {"name": "Кефир 3.2%", "calories": 59, "protein": 2.8, "fat": 3.2, "carbs": 4.0},
    "кефир 2.5%": {"name": "Кефир 2.5%", "calories": 50, "protein": 2.9, "fat": 2.5, "carbs": 4.0},
    "кефир 1%": {"name": "Кефир 1%", "calories": 38, "protein": 3.0, "fat": 1.0, "carbs": 4.0},
    "йогурт": {"name": "Йогурт натуральный 3.2%", "calories": 66, "protein": 5.0, "fat": 3.2, "carbs": 3.5},
    "йогурт греческий": {"name": "Йогурт греческий", "calories": 70, "protein": 7.0, "fat": 3.0, "carbs": 4.0},
    "творог": {"name": "Творог 5%", "calories": 145, "protein": 16.0, "fat": 5.0, "carbs": 3.0},
    "творог 9%": {"name": "Творог 9%", "calories": 169, "protein": 16.0, "fat": 9.0, "carbs": 2.0},
    "творог обезжиренный": {"name": "Творог обезжиренный", "calories": 85, "protein": 17.0, "fat": 0.5, "carbs": 2.0},
    "сметана": {"name": "Сметана 20%", "calories": 206, "protein": 2.5, "fat": 20.0, "carbs": 3.4},
    "сметана 15%": {"name": "Сметана 15%", "calories": 160, "protein": 2.6, "fat": 15.0, "carbs": 3.0},
    "сливки": {"name": "Сливки 20%", "calories": 205, "protein": 2.5, "fat": 20.0, "carbs": 4.0},
    "сливки 10%": {"name": "Сливки 10%", "calories": 119, "protein": 3.0, "fat": 10.0, "carbs": 4.0},
    "сыр": {"name": "Сыр твёрдый (Российский, Пошехонский)", "calories": 360, "protein": 24.0, "fat": 30.0, "carbs": 0.0},
    "сыр пармезан": {"name": "Сыр Пармезан", "calories": 392, "protein": 33.0, "fat": 28.0, "carbs": 4.0},
    "сыр моцарелла": {"name": "Сыр Моцарелла", "calories": 280, "protein": 22.0, "fat": 20.0, "carbs": 3.0},
    "сыр фета": {"name": "Сыр Фета", "calories": 264, "protein": 14.0, "fat": 21.0, "carbs": 4.0},
    "сыр сулугуни": {"name": "Сыр Сулугуни", "calories": 285, "protein": 20.0, "fat": 22.0, "carbs": 0.5},
    "сыр адыгейский": {"name": "Сыр Адыгейский", "calories": 240, "protein": 18.0, "fat": 16.0, "carbs": 2.0},
    "сыр плавленый": {"name": "Сыр плавленый", "calories": 290, "protein": 16.0, "fat": 23.0, "carbs": 3.0},
    "масло сливочное": {"name": "Масло сливочное 82.5%", "calories": 748, "protein": 0.5, "fat": 82.5, "carbs": 0.8},
    "масло сливочное 72%": {"name": "Масло сливочное 72.5%", "calories": 660, "protein": 0.7, "fat": 72.5, "carbs": 1.0},
    "яйцо": {"name": "Яйцо куриное (1 шт.)", "calories": 70, "protein": 5.6, "fat": 5.0, "carbs": 0.3},
    "яйцо перепелиное": {"name": "Яйцо перепелиное (1 шт.)", "calories": 14, "protein": 1.2, "fat": 1.0, "carbs": 0.1},
    "сливочное масло": {"name": "Масло сливочное", "calories": 748, "protein": 0.5, "fat": 82.5, "carbs": 0.8},
    "ряженка": {"name": "Ряженка 4%", "calories": 67, "protein": 2.8, "fat": 4.0, "carbs": 4.2},
    "варенец": {"name": "Варенец", "calories": 60, "protein": 2.8, "fat": 3.0, "carbs": 4.5},
    "снежок": {"name": "Снежок", "calories": 75, "protein": 2.8, "fat": 3.0, "carbs": 8.0},
    "простокваша": {"name": "Простокваша", "calories": 58, "protein": 2.8, "fat": 3.2, "carbs": 4.1},
    "айран": {"name": "Айран", "calories": 24, "protein": 1.1, "fat": 1.3, "carbs": 1.8},
    "кумыс": {"name": "Кумыс", "calories": 50, "protein": 2.1, "fat": 1.9, "carbs": 5.0},

    # ========== МЯСО, ПТИЦА, СУБПРОДУКТЫ ==========
    "курица": {"name": "Куриное филе (грудка)", "calories": 110, "protein": 23.0, "fat": 1.2, "carbs": 0.0},
    "куриное бедро": {"name": "Куриное бедро (с кожей)", "calories": 180, "protein": 18.0, "fat": 12.0, "carbs": 0.0},
    "куриное бедро без кожи": {"name": "Куриное бедро (без кожи)", "calories": 150, "protein": 19.0, "fat": 8.0, "carbs": 0.0},
    "куриное крыло": {"name": "Куриное крыло", "calories": 190, "protein": 18.0, "fat": 13.0, "carbs": 0.0},
    "куриная голень": {"name": "Куриная голень", "calories": 150, "protein": 17.0, "fat": 8.0, "carbs": 0.0},
    "индейка": {"name": "Индейка (филе грудки)", "calories": 115, "protein": 24.0, "fat": 1.5, "carbs": 0.0},
    "индейка бедро": {"name": "Индейка (бедро, без кожи)", "calories": 140, "protein": 20.0, "fat": 6.0, "carbs": 0.0},
    "говядина": {"name": "Говядина (вырезка)", "calories": 158, "protein": 22.0, "fat": 7.0, "carbs": 0.0},
    "говядина лопатка": {"name": "Говядина (лопатка)", "calories": 170, "protein": 20.0, "fat": 10.0, "carbs": 0.0},
    "телятина": {"name": "Телятина", "calories": 128, "protein": 20.0, "fat": 5.0, "carbs": 0.0},
    "свинина": {"name": "Свинина (вырезка)", "calories": 142, "protein": 20.0, "fat": 7.0, "carbs": 0.0},
    "свинина шея": {"name": "Свинина (шея)", "calories": 340, "protein": 14.0, "fat": 30.0, "carbs": 0.0},
    "свинина лопатка": {"name": "Свинина (лопатка)", "calories": 250, "protein": 16.0, "fat": 20.0, "carbs": 0.0},
    "баранина": {"name": "Баранина (задняя нога)", "calories": 200, "protein": 18.0, "fat": 14.0, "carbs": 0.0},
    "баранина грудинка": {"name": "Баранина (грудинка)", "calories": 280, "protein": 16.0, "fat": 24.0, "carbs": 0.0},
    "кролик": {"name": "Кролик (тушка)", "calories": 156, "protein": 21.0, "fat": 8.0, "carbs": 0.0},
    "утка": {"name": "Утка (тушка)", "calories": 308, "protein": 16.0, "fat": 28.0, "carbs": 0.0},
    "гусь": {"name": "Гусь (тушка)", "calories": 364, "protein": 15.0, "fat": 34.0, "carbs": 0.0},
    "печень куриная": {"name": "Печень куриная", "calories": 137, "protein": 20.0, "fat": 5.5, "carbs": 0.7},
    "печень говяжья": {"name": "Печень говяжья", "calories": 127, "protein": 18.0, "fat": 3.7, "carbs": 5.3},
    "сердце куриное": {"name": "Сердце куриное", "calories": 158, "protein": 16.0, "fat": 10.0, "carbs": 1.0},
    "сердце говяжье": {"name": "Сердце говяжье", "calories": 112, "protein": 16.0, "fat": 3.5, "carbs": 2.5},
    "желудки куриные": {"name": "Желудки куриные", "calories": 114, "protein": 18.0, "fat": 4.0, "carbs": 1.0},
    "язык говяжий": {"name": "Язык говяжий", "calories": 210, "protein": 15.0, "fat": 16.0, "carbs": 2.0},
    "язык свиной": {"name": "Язык свиной", "calories": 210, "protein": 15.0, "fat": 16.0, "carbs": 2.0},
    "фарш куриный": {"name": "Фарш куриный", "calories": 140, "protein": 18.0, "fat": 7.0, "carbs": 0.0},
    "фарш говяжий": {"name": "Фарш говяжий", "calories": 200, "protein": 17.0, "fat": 14.0, "carbs": 0.0},
    "фарш свиной": {"name": "Фарш свиной", "calories": 260, "protein": 14.0, "fat": 22.0, "carbs": 0.0},
    "фарш свино-говяжий": {"name": "Фарш свино-говяжий (домашний)", "calories": 230, "protein": 15.0, "fat": 18.0, "carbs": 0.0},

    # ========== РЫБА И МОРЕПРОДУКТЫ ==========
    "лосось": {"name": "Лосось (сёмга, атлантический)", "calories": 208, "protein": 20.0, "fat": 15.0, "carbs": 0.0},
    "форель": {"name": "Форель (радужная)", "calories": 148, "protein": 20.5, "fat": 6.6, "carbs": 0.0},
    "горбуша": {"name": "Горбуша", "calories": 147, "protein": 21.0, "fat": 7.0, "carbs": 0.0},
    "кета": {"name": "Кета", "calories": 127, "protein": 19.0, "fat": 5.5, "carbs": 0.0},
    "семга": {"name": "Сёмга", "calories": 208, "protein": 20.0, "fat": 15.0, "carbs": 0.0},
    "тунец": {"name": "Тунец (свежий)", "calories": 110, "protein": 24.0, "fat": 1.0, "carbs": 0.0},
    "тунец консервированный": {"name": "Тунец консервированный (в собственном соку)", "calories": 115, "protein": 23.5, "fat": 1.5, "carbs": 0.0},
    "скумбрия": {"name": "Скумбрия", "calories": 205, "protein": 18.0, "fat": 15.0, "carbs": 0.0},
    "сельдь": {"name": "Сельдь (слабосоленая)", "calories": 250, "protein": 17.0, "fat": 20.0, "carbs": 0.0},
    "сельдь атлантическая": {"name": "Сельдь атлантическая (свежая)", "calories": 158, "protein": 17.7, "fat": 9.4, "carbs": 0.0},
    "треска": {"name": "Треска (филе)", "calories": 78, "protein": 18.0, "fat": 0.7, "carbs": 0.0},
    "пикша": {"name": "Пикша", "calories": 74, "protein": 17.0, "fat": 0.5, "carbs": 0.0},
    "минтай": {"name": "Минтай", "calories": 72, "protein": 15.9, "fat": 0.9, "carbs": 0.0},
    "хек": {"name": "Хек", "calories": 86, "protein": 16.6, "fat": 2.2, "carbs": 0.0},
    "камбала": {"name": "Камбала", "calories": 90, "protein": 15.7, "fat": 3.0, "carbs": 0.0},
    "палтус": {"name": "Палтус", "calories": 102, "protein": 18.9, "fat": 2.5, "carbs": 0.0},
    "окунь морской": {"name": "Окунь морской", "calories": 103, "protein": 18.2, "fat": 3.3, "carbs": 0.0},
    "судак": {"name": "Судак", "calories": 84, "protein": 18.4, "fat": 1.1, "carbs": 0.0},
    "щука": {"name": "Щука", "calories": 84, "protein": 18.4, "fat": 1.1, "carbs": 0.0},
    "карп": {"name": "Карп", "calories": 112, "protein": 16.0, "fat": 5.3, "carbs": 0.0},
    "сазан": {"name": "Сазан", "calories": 97, "protein": 18.2, "fat": 2.7, "carbs": 0.0},
    "лещ": {"name": "Лещ", "calories": 105, "protein": 17.1, "fat": 4.4, "carbs": 0.0},
    "сом": {"name": "Сом", "calories": 115, "protein": 16.8, "fat": 5.1, "carbs": 0.0},
    "налим": {"name": "Налим", "calories": 80, "protein": 18.0, "fat": 0.6, "carbs": 0.0},
    "угорь": {"name": "Угорь (копчёный)", "calories": 280, "protein": 18.0, "fat": 23.0, "carbs": 0.0},
    "креветки": {"name": "Креветки (очищенные)", "calories": 95, "protein": 22.0, "fat": 1.5, "carbs": 0.5},
    "кальмары": {"name": "Кальмары (тушка)", "calories": 100, "protein": 18.0, "fat": 2.5, "carbs": 2.0},
    "мидии": {"name": "Мидии (очищенные)", "calories": 77, "protein": 11.0, "fat": 2.2, "carbs": 3.5},
    "осьминоги": {"name": "Осьминоги", "calories": 80, "protein": 15.0, "fat": 1.0, "carbs": 2.0},
    "устрицы": {"name": "Устрицы", "calories": 72, "protein": 9.0, "fat": 2.5, "carbs": 4.5},
    "гребешки": {"name": "Морские гребешки", "calories": 88, "protein": 17.0, "fat": 1.0, "carbs": 2.5},
    "крабы": {"name": "Крабы (мясо)", "calories": 87, "protein": 18.0, "fat": 1.0, "carbs": 0.0},
    "лангусты": {"name": "Лангусты", "calories": 90, "protein": 19.0, "fat": 1.5, "carbs": 0.0},
    "омары": {"name": "Омары (лобстеры)", "calories": 90, "protein": 19.0, "fat": 1.5, "carbs": 0.0},
    "икра красная": {"name": "Икра красная (лососевая)", "calories": 250, "protein": 31.0, "fat": 13.0, "carbs": 1.0},
    "икра черная": {"name": "Икра черная (осетровая)", "calories": 235, "protein": 28.0, "fat": 13.0, "carbs": 1.0},
    "икра минтая": {"name": "Икра минтая (пробойная)", "calories": 130, "protein": 22.0, "fat": 4.0, "carbs": 1.0},

    # ========== МАСЛА, ЖИРЫ, СОУСЫ ==========
    "масло оливковое": {"name": "Масло оливковое", "calories": 899, "protein": 0.0, "fat": 99.9, "carbs": 0.0},
    "масло подсолнечное": {"name": "Масло подсолнечное", "calories": 899, "protein": 0.0, "fat": 99.9, "carbs": 0.0},
    "масло льняное": {"name": "Масло льняное", "calories": 898, "protein": 0.0, "fat": 99.8, "carbs": 0.0},
    "масло кунжутное": {"name": "Масло кунжутное", "calories": 899, "protein": 0.0, "fat": 99.9, "carbs": 0.0},
    "масло рапсовое": {"name": "Масло рапсовое", "calories": 899, "protein": 0.0, "fat": 99.9, "carbs": 0.0},
    "масло кукурузное": {"name": "Масло кукурузное", "calories": 899, "protein": 0.0, "fat": 99.9, "carbs": 0.0},
    "масло кокосовое": {"name": "Масло кокосовое", "calories": 860, "protein": 0.0, "fat": 99.0, "carbs": 0.0},
    "масло гхи": {"name": "Масло Гхи (топлёное)", "calories": 900, "protein": 0.2, "fat": 99.5, "carbs": 0.0},
    "сало": {"name": "Сало свиное (солёное)", "calories": 800, "protein": 2.0, "fat": 90.0, "carbs": 0.0},
    "бекон": {"name": "Бекон (сырокопчёный)", "calories": 500, "protein": 12.0, "fat": 50.0, "carbs": 1.0},
    "грудинка": {"name": "Грудинка свиная (копчёная)", "calories": 550, "protein": 10.0, "fat": 55.0, "carbs": 0.0},
    "майонез": {"name": "Майонез (Провансаль, 67%)", "calories": 620, "protein": 2.5, "fat": 65.0, "carbs": 3.5},
    "сметана": {"name": "Сметана 20%", "calories": 206, "protein": 2.5, "fat": 20.0, "carbs": 3.4},
    "кефир": {"name": "Кефир 3.2%", "calories": 59, "protein": 2.8, "fat": 3.2, "carbs": 4.0},
    "йогурт натуральный": {"name": "Йогурт натуральный", "calories": 66, "protein": 5.0, "fat": 3.2, "carbs": 3.5},
    "соус соевый": {"name": "Соус соевый (классический)", "calories": 55, "protein": 7.0, "fat": 0.0, "carbs": 6.0},
    "соус томатный": {"name": "Соус томатный (кетчуп)", "calories": 90, "protein": 1.5, "fat": 0.5, "carbs": 20.0},
    "соус терияки": {"name": "Соус терияки", "calories": 85, "protein": 4.0, "fat": 0.0, "carbs": 18.0},
    "соус песто": {"name": "Соус песто (зелёный)", "calories": 500, "protein": 8.0, "fat": 48.0, "carbs": 8.0},
    "соус цезарь": {"name": "Соус Цезарь", "calories": 550, "protein": 2.0, "fat": 55.0, "carbs": 5.0},
    "горчица": {"name": "Горчица (столовая)", "calories": 67, "protein": 5.5, "fat": 4.0, "carbs": 5.0},
    "хрен": {"name": "Хрен (столовый)", "calories": 55, "protein": 1.5, "fat": 0.5, "carbs": 11.0},
    "аджика": {"name": "Аджика (острая)", "calories": 40, "protein": 1.0, "fat": 1.0, "carbs": 7.0},
    "ткемали": {"name": "Соус ткемали", "calories": 60, "protein": 1.0, "fat": 1.0, "carbs": 12.0},
    "сацебели": {"name": "Соус сацебели", "calories": 70, "protein": 1.0, "fat": 2.0, "carbs": 12.0},
    "уксус": {"name": "Уксус (винный, яблочный)", "calories": 20, "protein": 0.0, "fat": 0.0, "carbs": 1.0},

    # ========== ХЛЕБ, ВЫПЕЧКА ==========
    "хлеб": {"name": "Хлеб пшеничный (батон)", "calories": 260, "protein": 8.0, "fat": 3.0, "carbs": 50.0},
    "хлеб ржаной": {"name": "Хлеб ржаной (бородинский)", "calories": 200, "protein": 6.5, "fat": 1.2, "carbs": 42.0},
    "хлеб зерновой": {"name": "Хлеб зерновой", "calories": 250, "protein": 9.0, "fat": 4.0, "carbs": 45.0},
    "хлеб цельнозерновой": {"name": "Хлеб цельнозерновой", "calories": 230, "protein": 8.5, "fat": 2.5, "carbs": 44.0},
    "лаваш": {"name": "Лаваш армянский (тонкий)", "calories": 235, "protein": 7.5, "fat": 1.0, "carbs": 48.0},
    "лаваш кавказский": {"name": "Лаваш кавказский (пышный)", "calories": 260, "protein": 8.0, "fat": 2.5, "carbs": 52.0},
    "багет": {"name": "Багет французский", "calories": 270, "protein": 8.0, "fat": 2.5, "carbs": 55.0},
    "чиабатта": {"name": "Чиабатта", "calories": 260, "protein": 8.0, "fat": 3.0, "carbs": 50.0},
    "булочка": {"name": "Булочка сдобная", "calories": 330, "protein": 7.5, "fat": 9.0, "carbs": 55.0},
    "кекс": {"name": "Кекс (маффин, без начинки)", "calories": 340, "protein": 5.0, "fat": 15.0, "carbs": 50.0},
    "печенье": {"name": "Печенье крекер", "calories": 420, "protein": 8.0, "fat": 15.0, "carbs": 65.0},
    "печенье овсяное": {"name": "Печенье овсяное", "calories": 440, "protein": 7.0, "fat": 15.0, "carbs": 70.0},
    "пряники": {"name": "Пряники", "calories": 350, "protein": 5.0, "fat": 3.0, "carbs": 80.0},
    "вафли": {"name": "Вафли (с начинкой)", "calories": 500, "protein": 4.0, "fat": 25.0, "carbs": 65.0},
    "сухари": {"name": "Сухари (панировочные)", "calories": 350, "protein": 10.0, "fat": 2.5, "carbs": 75.0},
    "гренки": {"name": "Гренки (сухарики ржаные)", "calories": 340, "protein": 9.0, "fat": 8.0, "carbs": 60.0},

    # ========== СЛАДОСТИ, ДЕСЕРТЫ ==========
    "сахар": {"name": "Сахар (песок)", "calories": 399, "protein": 0.0, "fat": 0.0, "carbs": 99.8},
    "мёд": {"name": "Мёд натуральный", "calories": 328, "protein": 0.8, "fat": 0.0, "carbs": 80.3},
    "варенье": {"name": "Варенье (клубничное)", "calories": 260, "protein": 0.5, "fat": 0.2, "carbs": 65.0},
    "джем": {"name": "Джем", "calories": 250, "protein": 0.3, "fat": 0.1, "carbs": 62.0},
    "конфитюр": {"name": "Конфитюр", "calories": 250, "protein": 0.3, "fat": 0.1, "carbs": 62.0},
    "шоколад горький": {"name": "Шоколад горький (70-85%)", "calories": 600, "protein": 8.0, "fat": 43.0, "carbs": 36.0},
    "шоколад молочный": {"name": "Шоколад молочный", "calories": 550, "protein": 6.0, "fat": 32.0, "carbs": 57.0},
    "шоколад белый": {"name": "Шоколад белый", "calories": 550, "protein": 5.0, "fat": 32.0, "carbs": 60.0},
    "какао": {"name": "Какао-порошок (порошок)", "calories": 350, "protein": 20.0, "fat": 14.0, "carbs": 30.0},
    "халва": {"name": "Халва подсолнечная", "calories": 510, "protein": 12.0, "fat": 30.0, "carbs": 50.0},
    "козинаки": {"name": "Козинаки (из семечек)", "calories": 500, "protein": 12.0, "fat": 30.0, "carbs": 55.0},
    "мармелад": {"name": "Мармелад желейный", "calories": 320, "protein": 0.1, "fat": 0.0, "carbs": 80.0},
    "пастила": {"name": "Пастила", "calories": 310, "protein": 0.5, "fat": 0.0, "carbs": 77.0},
    "зефир": {"name": "Зефир", "calories": 300, "protein": 0.8, "fat": 0.1, "carbs": 75.0},
    "рахат-лукум": {"name": "Рахат-лукум", "calories": 350, "protein": 1.0, "fat": 1.0, "carbs": 80.0},
    "нуга": {"name": "Нуга", "calories": 400, "protein": 3.0, "fat": 10.0, "carbs": 75.0},
    "конфеты шоколадные": {"name": "Конфеты шоколадные (ассорти)", "calories": 550, "protein": 5.0, "fat": 30.0, "carbs": 60.0},
    "мороженое": {"name": "Мороженое пломбир", "calories": 230, "protein": 3.5, "fat": 15.0, "carbs": 20.0},
    "мороженое молочное": {"name": "Мороженое молочное", "calories": 130, "protein": 3.0, "fat": 3.5, "carbs": 22.0},
    "мороженое фруктовое": {"name": "Мороженое фруктовый лёд", "calories": 90, "protein": 0.0, "fat": 0.0, "carbs": 23.0},
    "сгущенка": {"name": "Молоко сгущённое (с сахаром)", "calories": 330, "protein": 7.0, "fat": 8.0, "carbs": 55.0},
    "сироп": {"name": "Сироп (кленовый, шоколадный)", "calories": 260, "protein": 0.0, "fat": 0.0, "carbs": 65.0},

    # ========== НАПИТКИ ==========
    "вода": {"name": "Вода", "calories": 0, "protein": 0.0, "fat": 0.0, "carbs": 0.0},
    "кофе": {"name": "Кофе чёрный (без сахара)", "calories": 2, "protein": 0.1, "fat": 0.0, "carbs": 0.0},
    "кофе растворимый": {"name": "Кофе растворимый (без сахара)", "calories": 4, "protein": 0.1, "fat": 0.0, "carbs": 0.5},
    "кофе с молоком": {"name": "Кофе с молоком (без сахара)", "calories": 20, "protein": 0.8, "fat": 0.8, "carbs": 2.0},
    "чай": {"name": "Чай чёрный/зелёный (без сахара)", "calories": 1, "protein": 0.0, "fat": 0.0, "carbs": 0.2},
    "сок апельсиновый": {"name": "Сок апельсиновый (свежевыжатый)", "calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 10.0},
    "сок яблочный": {"name": "Сок яблочный (осветлённый)", "calories": 46, "protein": 0.5, "fat": 0.1, "carbs": 11.0},
    "сок томатный": {"name": "Сок томатный", "calories": 18, "protein": 0.8, "fat": 0.1, "carbs": 3.5},
    "сок гранатовый": {"name": "Сок гранатовый", "calories": 64, "protein": 0.3, "fat": 0.1, "carbs": 14.5},
    "компот": {"name": "Компот (из сухофруктов)", "calories": 60, "protein": 0.2, "fat": 0.0, "carbs": 15.0},
    "морс": {"name": "Морс (ягодный)", "calories": 40, "protein": 0.1, "fat": 0.0, "carbs": 10.0},
    "квас": {"name": "Квас хлебный", "calories": 27, "protein": 0.2, "fat": 0.0, "carbs": 5.5},
    "лимонад": {"name": "Лимонад (газировка)", "calories": 40, "protein": 0.0, "fat": 0.0, "carbs": 10.0},
    "кола": {"name": "Кола", "calories": 42, "protein": 0.0, "fat": 0.0, "carbs": 10.6},
    "энергетик": {"name": "Энергетический напиток", "calories": 45, "protein": 0.0, "fat": 0.0, "carbs": 11.0},
    "вино сухое": {"name": "Вино сухое красное/белое", "calories": 70, "protein": 0.1, "fat": 0.0, "carbs": 1.5},
    "вино полусухое": {"name": "Вино полусухое", "calories": 80, "protein": 0.1, "fat": 0.0, "carbs": 3.0},
    "вино сладкое": {"name": "Вино сладкое", "calories": 110, "protein": 0.2, "fat": 0.0, "carbs": 8.0},
    "пиво": {"name": "Пиво светлое", "calories": 45, "protein": 0.5, "fat": 0.0, "carbs": 3.6},
    "шампанское": {"name": "Шампанское (брют)", "calories": 65, "protein": 0.2, "fat": 0.0, "carbs": 1.5},
    "водка": {"name": "Водка", "calories": 235, "protein": 0.0, "fat": 0.0, "carbs": 0.1},
    "коньяк": {"name": "Коньяк/Бренди", "calories": 240, "protein": 0.0, "fat": 0.0, "carbs": 1.5},
    "виски": {"name": "Виски", "calories": 235, "protein": 0.0, "fat": 0.0, "carbs": 0.1},
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
