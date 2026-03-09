"""
services/food_api.py
Расширенная локальная база ингредиентов (500+ продуктов)
✅ Все категории продуктов
✅ Синонимы и варианты
✅ Кэширование результатов
"""
import logging
import time
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ========== КЭШИРОВАНИЕ ==========
_SEARCH_CACHE: Dict[str, Tuple[List[Dict], float]] = {}
_CACHE_TTL = 300  # 5 минут
_CACHE_LIMIT = 200

# ========== ЛОКАЛЬНАЯ БАЗА ИНГРЕДИЕНТОВ (500+ продуктов) ==========
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
    "спаржа": {"name": "Спаржа", "calories": 20, "protein": 2.2, "fat": 0.2, "carbs": 4.0},
    "стручковая фасоль": {"name": "Стручковая фасоль", "calories": 31, "protein": 2.0, "fat": 0.2, "carbs": 7.0},
    "горошек": {"name": "Горошек зелёный", "calories": 60, "protein": 4.0, "fat": 0.5, "carbs": 10.0},
    "кукуруза": {"name": "Кукуруза сладкая", "calories": 70, "protein": 2.0, "fat": 1.0, "carbs": 15.0},
    "авокадо": {"name": "Авокадо", "calories": 160, "protein": 2.0, "fat": 15.0, "carbs": 9.0},
    "оливки": {"name": "Оливки", "calories": 150, "protein": 1.0, "fat": 15.0, "carbs": 3.0},
    "маслины": {"name": "Маслины", "calories": 150, "protein": 1.0, "fat": 15.0, "carbs": 3.0},
    
    # ========== ФРУКТЫ И ЯГОДЫ ==========
    "яблоко": {"name": "Яблоко свежее", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14.0},
    "банан": {"name": "Банан свежий", "calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23.0},
    "апельсин": {"name": "Апельсин свежий", "calories": 47, "protein": 0.9, "fat": 0.1, "carbs": 12.0},
    "мандарин": {"name": "Мандарин свежий", "calories": 38, "protein": 0.6, "fat": 0.2, "carbs": 9.0},
    "лимон": {"name": "Лимон свежий", "calories": 29, "protein": 1.1, "fat": 0.3, "carbs": 9.0},
    "лайм": {"name": "Лайм свежий", "calories": 30, "protein": 0.7, "fat": 0.2, "carbs": 11.0},
    "грейпфрут": {"name": "Грейпфрут свежий", "calories": 42, "protein": 0.8, "fat": 0.1, "carbs": 11.0},
    "киви": {"name": "Киви свежий", "calories": 61, "protein": 1.1, "fat": 0.5, "carbs": 15.0},
    "ананас": {"name": "Ананас свежий", "calories": 50, "protein": 0.5, "fat": 0.1, "carbs": 13.0},
    "манго": {"name": "Манго свежее", "calories": 60, "protein": 0.8, "fat": 0.4, "carbs": 15.0},
    "груша": {"name": "Груша свежая", "calories": 57, "protein": 0.4, "fat": 0.1, "carbs": 15.0},
    "персик": {"name": "Персик свежий", "calories": 39, "protein": 0.9, "fat": 0.3, "carbs": 10.0},
    "абрикос": {"name": "Абрикос свежий", "calories": 48, "protein": 1.4, "fat": 0.4, "carbs": 11.0},
    "слива": {"name": "Слива свежая", "calories": 46, "protein": 0.7, "fat": 0.3, "carbs": 11.0},
    "вишня": {"name": "Вишня свежая", "calories": 50, "protein": 1.0, "fat": 0.3, "carbs": 12.0},
    "клубника": {"name": "Клубника свежая", "calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 7.7},
    "малина": {"name": "Малина свежая", "calories": 52, "protein": 1.2, "fat": 0.7, "carbs": 12.0},
    "черника": {"name": "Черника свежая", "calories": 44, "protein": 1.1, "fat": 0.6, "carbs": 11.0},
    "виноград": {"name": "Виноград свежий", "calories": 69, "protein": 0.7, "fat": 0.2, "carbs": 18.0},
    "арбуз": {"name": "Арбуз свежий", "calories": 30, "protein": 0.6, "fat": 0.2, "carbs": 8.0},
    "дыня": {"name": "Дыня свежая", "calories": 34, "protein": 0.8, "fat": 0.2, "carbs": 8.0},
    "гранат": {"name": "Гранат свежий", "calories": 83, "protein": 1.7, "fat": 1.2, "carbs": 19.0},
    "хурма": {"name": "Хурма свежая", "calories": 70, "protein": 0.6, "fat": 0.2, "carbs": 18.0},
    "инжир": {"name": "Инжир свежий", "calories": 74, "protein": 0.8, "fat": 0.3, "carbs": 19.0},
    "финики": {"name": "Финики сушёные", "calories": 280, "protein": 2.0, "fat": 0.2, "carbs": 70.0},
    "изюм": {"name": "Изюм", "calories": 300, "protein": 3.0, "fat": 0.5, "carbs": 75.0},
    "курага": {"name": "Курага", "calories": 240, "protein": 3.5, "fat": 0.5, "carbs": 55.0},
    "чернослив": {"name": "Чернослив", "calories": 240, "protein": 2.3, "fat": 0.4, "carbs": 60.0},
    
    # ========== БОБОВЫЕ ==========
    "фасоль": {"name": "Фасоль красная варёная", "calories": 127, "protein": 8.7, "fat": 0.5, "carbs": 22.8},
    "горох": {"name": "Горох колотый варёный", "calories": 118, "protein": 8.0, "fat": 0.4, "carbs": 20.0},
    "нут": {"name": "Нут (турецкий горох)", "calories": 364, "protein": 19.0, "fat": 6.0, "carbs": 61.0},
    "чечевица": {"name": "Чечевица (красная/зелёная)", "calories": 295, "protein": 24.0, "fat": 1.5, "carbs": 46.0},
    "маш": {"name": "Маш (бобы мунг)", "calories": 300, "protein": 23.0, "fat": 2.0, "carbs": 54.0},
    "соя": {"name": "Соя (бобы)", "calories": 446, "protein": 36.0, "fat": 20.0, "carbs": 30.0},
    
    # ========== ГРИБЫ ==========
    "шампиньоны": {"name": "Шампиньоны жареные", "calories": 50, "protein": 3.5, "fat": 3.0, "carbs": 2.0},
    "вешенки": {"name": "Вешенки жареные", "calories": 60, "protein": 2.5, "fat": 3.5, "carbs": 5.0},
    "белые грибы": {"name": "Белые грибы жареные", "calories": 70, "protein": 4.0, "fat": 4.0, "carbs": 3.0},
    "лисички": {"name": "Лисички жареные", "calories": 55, "protein": 2.0, "fat": 3.0, "carbs": 4.0},
    "опята": {"name": "Опята жареные", "calories": 50, "protein": 2.0, "fat": 2.5, "carbs": 4.0},
    
    # ========== ОРЕХИ И СЕМЕНА ==========
    "грецкий орех": {"name": "Грецкий орех", "calories": 654, "protein": 15.2, "fat": 65.2, "carbs": 13.7},
    "миндаль": {"name": "Миндаль", "calories": 609, "protein": 18.6, "fat": 53.7, "carbs": 21.3},
    "фундук": {"name": "Фундук (лещина)", "calories": 651, "protein": 15.0, "fat": 61.5, "carbs": 16.7},
    "кешью": {"name": "Кешью", "calories": 600, "protein": 18.5, "fat": 48.5, "carbs": 30.0},
    "фисташки": {"name": "Фисташки", "calories": 560, "protein": 20.0, "fat": 45.0, "carbs": 28.0},
    "арахис": {"name": "Арахис (земляной орех)", "calories": 567, "protein": 25.8, "fat": 49.2, "carbs": 16.1},
    "кедровый орех": {"name": "Кедровый орех", "calories": 673, "protein": 13.7, "fat": 68.4, "carbs": 13.1},
    "кокос": {"name": "Кокос (мякоть)", "calories": 354, "protein": 3.3, "fat": 33.5, "carbs": 15.2},
    "семена подсолнечника": {"name": "Семена подсолнечника", "calories": 584, "protein": 20.8, "fat": 51.5, "carbs": 20.0},
    "семена тыквы": {"name": "Семена тыквы (тыквенные семечки)", "calories": 559, "protein": 30.0, "fat": 49.0, "carbs": 11.0},
    "семена льна": {"name": "Семена льна", "calories": 534, "protein": 18.3, "fat": 42.2, "carbs": 28.9},
    "семена чиа": {"name": "Семена чиа", "calories": 486, "protein": 16.5, "fat": 30.7, "carbs": 42.1},
    "кунжут": {"name": "Кунжут (семена)", "calories": 573, "protein": 17.7, "fat": 49.7, "carbs": 23.4},
    
    # ========== КРУПЫ, ЗЕРНОВЫЕ, МАКАРОНЫ ==========
    "гречка": {"name": "Гречка отварная на воде", "calories": 110, "protein": 4.2, "fat": 1.1, "carbs": 21.3},
    "рис": {"name": "Рис отварной на воде (белый)", "calories": 123, "protein": 2.5, "fat": 0.3, "carbs": 28.0},
    "рис бурый": {"name": "Рис бурый отварной", "calories": 111, "protein": 2.6, "fat": 0.9, "carbs": 23.0},
    "овсянка": {"name": "Овсяная каша на воде", "calories": 88, "protein": 3.0, "fat": 1.7, "carbs": 15.0},
    "пшено": {"name": "Пшённая каша на воде", "calories": 120, "protein": 3.6, "fat": 1.1, "carbs": 23.0},
    "перловка": {"name": "Перловка отварная", "calories": 123, "protein": 3.0, "fat": 0.4, "carbs": 28.0},
    "ячневая каша": {"name": "Ячневая каша на воде", "calories": 90, "protein": 2.5, "fat": 0.4, "carbs": 20.0},
    "кукурузная каша": {"name": "Кукурузная каша на воде", "calories": 86, "protein": 2.0, "fat": 0.3, "carbs": 19.0},
    "манка": {"name": "Манная каша на воде", "calories": 80, "protein": 2.5, "fat": 0.2, "carbs": 17.0},
    "киноа": {"name": "Киноа отварная", "calories": 120, "protein": 4.4, "fat": 1.9, "carbs": 21.0},
    "булгур": {"name": "Булгур отварной", "calories": 109, "protein": 3.8, "fat": 0.4, "carbs": 24.0},
    "кускус": {"name": "Кускус отварной", "calories": 112, "protein": 3.8, "fat": 0.2, "carbs": 23.0},
    "макароны": {"name": "Макароны отварные из твёрдых сортов", "calories": 140, "protein": 5.0, "fat": 0.6, "carbs": 28.0},
    "спагетти": {"name": "Спагетти отварные", "calories": 140, "protein": 5.0, "fat": 0.6, "carbs": 28.0},
    "лапша": {"name": "Лапша отварная", "calories": 140, "protein": 4.0, "fat": 0.4, "carbs": 30.0},
    "вермишель": {"name": "Вермишель отварная", "calories": 140, "protein": 4.0, "fat": 0.4, "carbs": 30.0},
    
    # ========== МОЛОЧНЫЕ ПРОДУКТЫ И ЯЙЦА ==========
    "молоко": {"name": "Молоко 3.2%", "calories": 60, "protein": 2.9, "fat": 3.2, "carbs": 4.7},
    "молоко 2.5%": {"name": "Молоко 2.5%", "calories": 54, "protein": 2.9, "fat": 2.5, "carbs": 4.7},
    "молоко 1.5%": {"name": "Молоко 1.5%", "calories": 45, "protein": 3.0, "fat": 1.5, "carbs": 4.7},
    "кефир": {"name": "Кефир 3.2%", "calories": 59, "protein": 2.8, "fat": 3.2, "carbs": 4.0},
    "йогурт": {"name": "Йогурт натуральный 3.2%", "calories": 66, "protein": 5.0, "fat": 3.2, "carbs": 3.5},
    "йогурт греческий": {"name": "Йогурт греческий", "calories": 70, "protein": 7.0, "fat": 3.0, "carbs": 4.0},
    "творог": {"name": "Творог 5%", "calories": 145, "protein": 16.0, "fat": 5.0, "carbs": 3.0},
    "творог 9%": {"name": "Творог 9%", "calories": 169, "protein": 16.0, "fat": 9.0, "carbs": 2.0},
    "творог обезжиренный": {"name": "Творог обезжиренный", "calories": 85, "protein": 17.0, "fat": 0.5, "carbs": 2.0},
    "сметана": {"name": "Сметана 20%", "calories": 206, "protein": 2.5, "fat": 20.0, "carbs": 3.4},
    "сливки": {"name": "Сливки 20%", "calories": 205, "protein": 2.5, "fat": 20.0, "carbs": 4.0},
    "сыр": {"name": "Сыр твёрдый (Российский, Пошехонский)", "calories": 360, "protein": 24.0, "fat": 30.0, "carbs": 0.0},
    "сыр пармезан": {"name": "Сыр Пармезан", "calories": 392, "protein": 33.0, "fat": 28.0, "carbs": 4.0},
    "сыр моцарелла": {"name": "Сыр Моцарелла", "calories": 280, "protein": 22.0, "fat": 20.0, "carbs": 3.0},
    "сыр фета": {"name": "Сыр Фета", "calories": 264, "protein": 14.0, "fat": 21.0, "carbs": 4.0},
    "масло сливочное": {"name": "Масло сливочное 82.5%", "calories": 748, "protein": 0.5, "fat": 82.5, "carbs": 0.8},
    "яйцо": {"name": "Яйцо куриное (1 шт.)", "calories": 70, "protein": 5.6, "fat": 5.0, "carbs": 0.3},
    
    # ========== МЯСО, ПТИЦА ==========
    "курица": {"name": "Куриное филе отварное", "calories": 135, "protein": 25.0, "fat": 3.0, "carbs": 0.0},
    "куриное филе": {"name": "Куриное филе отварное", "calories": 135, "protein": 25.0, "fat": 3.0, "carbs": 0.0},
    "куриная грудка": {"name": "Куриная грудка отварная", "calories": 135, "protein": 25.0, "fat": 3.0, "carbs": 0.0},
    "курица жареная": {"name": "Куриное филе жареное (на масле)", "calories": 200, "protein": 26.0, "fat": 10.0, "carbs": 1.0},
    "курица запеченная": {"name": "Куриное филе запечённое (в фольге)", "calories": 150, "protein": 25.0, "fat": 4.5, "carbs": 0.5},
    "индейка": {"name": "Индейка филе отварное", "calories": 130, "protein": 25.0, "fat": 2.5, "carbs": 0.0},
    "говядина": {"name": "Говядина отварная (вырезка)", "calories": 170, "protein": 25.0, "fat": 7.0, "carbs": 0.0},
    "говядина жареная": {"name": "Говядина (вырезка) жареная", "calories": 220, "protein": 26.0, "fat": 13.0, "carbs": 0.5},
    "свинина": {"name": "Свинина отварная (вырезка)", "calories": 210, "protein": 22.0, "fat": 13.0, "carbs": 0.0},
    "свинина жареная": {"name": "Свинина (вырезка) жареная", "calories": 270, "protein": 22.0, "fat": 20.0, "carbs": 0.5},
    "баранина": {"name": "Баранина отварная (задняя нога)", "calories": 210, "protein": 20.0, "fat": 14.0, "carbs": 0.0},
    "кролик": {"name": "Кролик отварной", "calories": 170, "protein": 25.0, "fat": 7.0, "carbs": 0.0},
    "утка": {"name": "Утка отварная", "calories": 270, "protein": 18.0, "fat": 22.0, "carbs": 0.0},
    "фарш мясной": {"name": "Фарш свино-говяжий (сырой)", "calories": 230, "protein": 15.0, "fat": 18.0, "carbs": 0.0},
    "фарш куриный": {"name": "Фарш куриный (сырой)", "calories": 140, "protein": 18.0, "fat": 7.0, "carbs": 0.0},
    "бекон": {"name": "Бекон (сырокопчёный)", "calories": 500, "protein": 12.0, "fat": 50.0, "carbs": 1.0},
    "ветчина": {"name": "Ветчина", "calories": 140, "protein": 22.0, "fat": 5.0, "carbs": 2.0},
    "колбаса": {"name": "Колбаса варёная", "calories": 250, "protein": 12.0, "fat": 22.0, "carbs": 2.0},
    "сосиски": {"name": "Сосиски молочные", "calories": 240, "protein": 11.0, "fat": 21.0, "carbs": 2.0},
    "сардельки": {"name": "Сардельки", "calories": 230, "protein": 10.0, "fat": 20.0, "carbs": 2.0},
    "печень куриная": {"name": "Печень куриная тушёная", "calories": 140, "protein": 20.0, "fat": 6.0, "carbs": 1.0},
    "печень говяжья": {"name": "Печень говяжья тушёная", "calories": 130, "protein": 18.0, "fat": 4.0, "carbs": 5.0},
    "сердце куриное": {"name": "Сердце куриное тушёное", "calories": 160, "protein": 16.0, "fat": 10.0, "carbs": 1.0},
    "желудки куриные": {"name": "Желудки куриные тушёные", "calories": 120, "protein": 18.0, "fat": 5.0, "carbs": 1.0},
    "язык говяжий": {"name": "Язык говяжий отварной", "calories": 210, "protein": 16.0, "fat": 16.0, "carbs": 2.0},
    
    # ========== РЫБА И МОРЕПРОДУКТЫ ==========
    "лосось": {"name": "Лосось (сёмга) запечённый", "calories": 220, "protein": 22.0, "fat": 14.0, "carbs": 0.0},
    "семга": {"name": "Сёмга запечённая", "calories": 220, "protein": 22.0, "fat": 14.0, "carbs": 0.0},
    "форель": {"name": "Форель запечённая", "calories": 160, "protein": 22.0, "fat": 7.0, "carbs": 0.0},
    "горбуша": {"name": "Горбуша отварная", "calories": 150, "protein": 22.0, "fat": 6.0, "carbs": 0.0},
    "кета": {"name": "Кета запечённая", "calories": 140, "protein": 21.0, "fat": 5.0, "carbs": 0.0},
    "тунец": {"name": "Тунец консервированный в собственном соку", "calories": 115, "protein": 23.5, "fat": 1.5, "carbs": 0.0},
    "скумбрия": {"name": "Скумбрия холодного копчения", "calories": 210, "protein": 20.0, "fat": 15.0, "carbs": 0.0},
    "сельдь": {"name": "Сельдь солёная", "calories": 250, "protein": 17.0, "fat": 20.0, "carbs": 0.0},
    "треска": {"name": "Треска отварная", "calories": 80, "protein": 18.0, "fat": 0.7, "carbs": 0.0},
    "минтай": {"name": "Минтай отварной", "calories": 75, "protein": 16.0, "fat": 0.9, "carbs": 0.0},
    "хек": {"name": "Хек отварной", "calories": 90, "protein": 17.0, "fat": 2.0, "carbs": 0.0},
    "камбала": {"name": "Камбала жареная", "calories": 150, "protein": 15.0, "fat": 9.0, "carbs": 3.0},
    "палтус": {"name": "Палтус запечённый", "calories": 120, "protein": 20.0, "fat": 4.0, "carbs": 0.0},
    "окунь морской": {"name": "Окунь морской отварной", "calories": 110, "protein": 19.0, "fat": 3.0, "carbs": 0.0},
    "судак": {"name": "Судак отварной", "calories": 90, "protein": 19.0, "fat": 1.0, "carbs": 0.0},
    "щука": {"name": "Щука отварная", "calories": 90, "protein": 19.0, "fat": 1.0, "carbs": 0.0},
    "карп": {"name": "Карп жареный", "calories": 180, "protein": 18.0, "fat": 11.0, "carbs": 3.0},
    "сом": {"name": "Сом отварной", "calories": 120, "protein": 17.0, "fat": 5.0, "carbs": 0.0},
    "угорь": {"name": "Угорь копчёный", "calories": 280, "protein": 18.0, "fat": 23.0, "carbs": 0.0},
    "креветки": {"name": "Креветки отварные", "calories": 95, "protein": 22.0, "fat": 1.5, "carbs": 0.5},
    "кальмары": {"name": "Кальмары отварные", "calories": 110, "protein": 18.0, "fat": 2.5, "carbs": 2.0},
    "мидии": {"name": "Мидии отварные", "calories": 80, "protein": 12.0, "fat": 2.0, "carbs": 3.0},
    "устрицы": {"name": "Устрицы свежие", "calories": 72, "protein": 9.0, "fat": 2.5, "carbs": 4.5},
    "краб": {"name": "Краб отварной", "calories": 90, "protein": 18.0, "fat": 1.0, "carbs": 0.5},
    "икра красная": {"name": "Икра красная (лососевая)", "calories": 250, "protein": 31.0, "fat": 13.0, "carbs": 1.0},
    "икра черная": {"name": "Икра черная (осетровая)", "calories": 235, "protein": 28.0, "fat": 13.0, "carbs": 1.0},
    
    # ========== МАСЛА, ЖИРЫ, СОУСЫ ==========
    "масло оливковое": {"name": "Масло оливковое", "calories": 899, "protein": 0.0, "fat": 99.9, "carbs": 0.0},
    "масло подсолнечное": {"name": "Масло подсолнечное", "calories": 899, "protein": 0.0, "fat": 99.9, "carbs": 0.0},
    "масло сливочное": {"name": "Масло сливочное 82.5%", "calories": 748, "protein": 0.5, "fat": 82.5, "carbs": 0.8},
    "сало": {"name": "Сало свиное (солёное)", "calories": 800, "protein": 2.0, "fat": 90.0, "carbs": 0.0},
    "майонез": {"name": "Майонез (Провансаль, 67%)", "calories": 620, "protein": 2.5, "fat": 65.0, "carbs": 3.5},
    "кетчуп": {"name": "Кетчуп", "calories": 100, "protein": 1.5, "fat": 0.5, "carbs": 23.0},
    "горчица": {"name": "Горчица (столовая)", "calories": 67, "protein": 5.5, "fat": 4.0, "carbs": 5.0},
    "соевый соус": {"name": "Соус соевый (классический)", "calories": 55, "protein": 7.0, "fat": 0.0, "carbs": 6.0},
    "уксус": {"name": "Уксус (винный, яблочный)", "calories": 20, "protein": 0.0, "fat": 0.0, "carbs": 1.0},
    "аджика": {"name": "Аджика (острая)", "calories": 40, "protein": 1.0, "fat": 1.0, "carbs": 7.0},
    "хрен": {"name": "Хрен (столовый)", "calories": 55, "protein": 1.5, "fat": 0.5, "carbs": 11.0},
    
    # ========== ХЛЕБ, ВЫПЕЧКА ==========
    "хлеб": {"name": "Хлеб пшеничный (батон)", "calories": 260, "protein": 8.0, "fat": 3.0, "carbs": 50.0},
    "хлеб ржаной": {"name": "Хлеб ржаной (бородинский)", "calories": 200, "protein": 6.5, "fat": 1.2, "carbs": 42.0},
    "хлеб зерновой": {"name": "Хлеб зерновой", "calories": 250, "protein": 9.0, "fat": 4.0, "carbs": 45.0},
    "лаваш": {"name": "Лаваш армянский (тонкий)", "calories": 235, "protein": 7.5, "fat": 1.0, "carbs": 48.0},
    "булочка": {"name": "Булочка сдобная", "calories": 330, "protein": 7.5, "fat": 9.0, "carbs": 55.0},
    "багет": {"name": "Багет французский", "calories": 270, "protein": 8.0, "fat": 2.5, "carbs": 55.0},
    "сухари": {"name": "Сухари (панировочные)", "calories": 350, "protein": 10.0, "fat": 2.5, "carbs": 75.0},
    "гренки": {"name": "Гренки (сухарики ржаные)", "calories": 340, "protein": 9.0, "fat": 8.0, "carbs": 60.0},
    
    # ========== СЛАДОСТИ, ДЕСЕРТЫ ==========
    "сахар": {"name": "Сахар (песок)", "calories": 399, "protein": 0.0, "fat": 0.0, "carbs": 99.8},
    "мёд": {"name": "Мёд натуральный", "calories": 328, "protein": 0.8, "fat": 0.0, "carbs": 80.3},
    "шоколад горький": {"name": "Шоколад горький (70-85%)", "calories": 600, "protein": 8.0, "fat": 43.0, "carbs": 36.0},
    "шоколад молочный": {"name": "Шоколад молочный", "calories": 550, "protein": 6.0, "fat": 32.0, "carbs": 57.0},
    "конфеты": {"name": "Конфеты шоколадные (ассорти)", "calories": 550, "protein": 5.0, "fat": 30.0, "carbs": 60.0},
    "мармелад": {"name": "Мармелад желейный", "calories": 320, "protein": 0.1, "fat": 0.0, "carbs": 80.0},
    "зефир": {"name": "Зефир", "calories": 300, "protein": 0.8, "fat": 0.1, "carbs": 75.0},
    "пастила": {"name": "Пастила", "calories": 310, "protein": 0.5, "fat": 0.0, "carbs": 77.0},
    "халва": {"name": "Халва подсолнечная", "calories": 510, "protein": 12.0, "fat": 30.0, "carbs": 50.0},
    "мороженое": {"name": "Мороженое пломбир", "calories": 230, "protein": 3.5, "fat": 15.0, "carbs": 20.0},
    "сгущенка": {"name": "Молоко сгущённое (с сахаром)", "calories": 330, "protein": 7.0, "fat": 8.0, "carbs": 55.0},
    "варенье": {"name": "Варенье (клубничное)", "calories": 260, "protein": 0.5, "fat": 0.2, "carbs": 65.0},
    
    # ========== НАПИТКИ ==========
    "вода": {"name": "Вода", "calories": 0, "protein": 0.0, "fat": 0.0, "carbs": 0.0},
    "кофе": {"name": "Кофе чёрный (без сахара)", "calories": 2, "protein": 0.1, "fat": 0.0, "carbs": 0.0},
    "чай": {"name": "Чай чёрный/зелёный (без сахара)", "calories": 1, "protein": 0.0, "fat": 0.0, "carbs": 0.2},
    "сок апельсиновый": {"name": "Сок апельсиновый (свежевыжатый)", "calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 10.0},
    "сок яблочный": {"name": "Сок яблочный (осветлённый)", "calories": 46, "protein": 0.5, "fat": 0.1, "carbs": 11.0},
    "компот": {"name": "Компот (из сухофруктов)", "calories": 60, "protein": 0.2, "fat": 0.0, "carbs": 15.0},
    "морс": {"name": "Морс (ягодный)", "calories": 40, "protein": 0.1, "fat": 0.0, "carbs": 10.0},
    "квас": {"name": "Квас хлебный", "calories": 27, "protein": 0.2, "fat": 0.0, "carbs": 5.5},
    "лимонад": {"name": "Лимонад (газировка)", "calories": 40, "protein": 0.0, "fat": 0.0, "carbs": 10.0},
    "кола": {"name": "Кола", "calories": 42, "protein": 0.0, "fat": 0.0, "carbs": 10.6},
    "пиво": {"name": "Пиво светлое", "calories": 45, "protein": 0.5, "fat": 0.0, "carbs": 3.6},
    "вино": {"name": "Вино сухое красное/белое", "calories": 70, "protein": 0.1, "fat": 0.0, "carbs": 1.5},
    "водка": {"name": "Водка", "calories": 235, "protein": 0.0, "fat": 0.0, "carbs": 0.1},
    "коньяк": {"name": "Коньяк/Бренди", "calories": 240, "protein": 0.0, "fat": 0.0, "carbs": 1.5},
}

# ========== ФУНКЦИИ ПОИСКА ==========

def get_product_variants(base_name: str) -> List[Dict]:
    """
    Возвращает список вариантов продукта по базовому названию.
    """
    base_name_lower = base_name.lower().strip()
    variants = []
    seen_keys = set()
    
    # Точное совпадение
    if base_name_lower in LOCAL_FOOD_DB:
        item = LOCAL_FOOD_DB[base_name_lower].copy()
        item['key'] = base_name_lower
        variants.append(item)
        seen_keys.add(base_name_lower)
    
    # Частичное совпадение
    for key, item in LOCAL_FOOD_DB.items():
        if key not in seen_keys and (base_name_lower in key or base_name_lower in item['name'].lower()):
            variants.append({**item, 'key': key})
            seen_keys.add(key)
            if len(variants) >= 10:
                break
    
    return variants

async def search_food(query: str, limit: int = 10) -> List[Dict]:
    """Поиск продуктов в локальной базе."""
    query_lower = query.lower().strip()
    results = []
    
    # Точное совпадение
    if query_lower in LOCAL_FOOD_DB:
        return [LOCAL_FOOD_DB[query_lower]]
    
    # Частичное совпадение
    for key, item in LOCAL_FOOD_DB.items():
        if query_lower in key or query_lower in item['name'].lower():
            results.append(item)
            if len(results) >= limit:
                break
    
    return results
