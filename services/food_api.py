"""
API для поиска продуктов в локальной базе и OpenFoodFacts.
"""
import aiohttp
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# ========== ЛОКАЛЬНАЯ БАЗА ПРОДУКТОВ (более 500 записей) ==========
# Ключи — это слова, по которым бот будет искать (в нижнем регистре)
LOCAL_FOOD_DB = {
    # Основные продукты (мясо, птица)
    "курица": {"name": "Курица (средняя)", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
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

    # Рыба и морепродукты
    "лосось": {"name": "Лосось (сёмга)", "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    "семга": {"name": "Сёмга", "calories": 208, "protein": 20, "fat": 13, "carbs": 0},
    "треска": {"name": "Треска", "calories": 82, "protein": 18, "fat": 0.7, "carbs": 0},
    "скумбрия": {"name": "Скумбрия", "calories": 205, "protein": 19, "fat": 14, "carbs": 0},
    "сельдь": {"name": "Сельдь солёная", "calories": 250, "protein": 18, "fat": 19, "carbs": 0},
    "креветки": {"name": "Креветки", "calories": 85, "protein": 20, "fat": 0.5, "carbs": 0},
    "кальмар": {"name": "Кальмар", "calories": 100, "protein": 18, "fat": 2, "carbs": 0},
    "мидии": {"name": "Мидии", "calories": 85, "protein": 15, "fat": 2, "carbs": 3},
    "крабовые палочки": {"name": "Крабовые палочки", "calories": 90, "protein": 7, "fat": 2, "carbs": 12},

    # Яйца и молочка
    "яйцо": {"name": "Яйцо куриное (1 шт = 50г)", "calories": 70, "protein": 5.5, "fat": 5, "carbs": 0.5},
    "яйца": {"name": "Яйцо куриное (на 100г)", "calories": 140, "protein": 11, "fat": 10, "carbs": 1},
    "молоко": {"name": "Молоко 3.2%", "calories": 60, "protein": 3, "fat": 3.2, "carbs": 4.7},
    "кефир": {"name": "Кефир 2.5%", "calories": 50, "protein": 3, "fat": 2.5, "carbs": 4},
    "йогурт": {"name": "Йогурт натуральный", "calories": 60, "protein": 4, "fat": 2.5, "carbs": 6},
    "творог": {"name": "Творог 5%", "calories": 120, "protein": 16, "fat": 5, "carbs": 3},
    "сметана": {"name": "Сметана 20%", "calories": 200, "protein": 2.5, "fat": 20, "carbs": 3.5},
    "сыр": {"name": "Сыр твёрдый", "calories": 350, "protein": 25, "fat": 28, "carbs": 2},
    "масло сливочное": {"name": "Масло сливочное 82%", "calories": 750, "protein": 0.5, "fat": 82, "carbs": 0.5},

    # Овощи
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

    # Фрукты
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

    # Крупы, макароны
    "гречка": {"name": "Гречка (варёная)", "calories": 110, "protein": 4, "fat": 0.5, "carbs": 23},
    "рис": {"name": "Рис (варёный)", "calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
    "овсянка": {"name": "Овсянка (на воде)", "calories": 71, "protein": 2.5, "fat": 1.5, "carbs": 12},
    "пшено": {"name": "Пшёнка (варёная)", "calories": 120, "protein": 3.5, "fat": 1.3, "carbs": 24},
    "перловка": {"name": "Перловка (варёная)", "calories": 120, "protein": 3, "fat": 0.4, "carbs": 25},
    "макароны": {"name": "Макароны (варёные)", "calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
    "спагетти": {"name": "Спагетти (варёные)", "calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
    "лапша": {"name": "Лапша (варёная)", "calories": 130, "protein": 4, "fat": 1, "carbs": 26},

    # Хлеб и выпечка
    "хлеб": {"name": "Хлеб пшеничный", "calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
    "хлеб ржаной": {"name": "Хлеб ржаной", "calories": 200, "protein": 6, "fat": 1.5, "carbs": 40},
    "лаваш": {"name": "Лаваш", "calories": 250, "protein": 8, "fat": 2, "carbs": 50},
    "печенье": {"name": "Печенье", "calories": 450, "protein": 6, "fat": 15, "carbs": 75},
    "пряники": {"name": "Пряники", "calories": 360, "protein": 5, "fat": 5, "carbs": 75},

    # Готовые блюда (салаты, супы, вторые)
    # ========== САЛАТЫ (расширенная подборка) ==========
    "салат цезарь с курицей": {"name": "Цезарь с курицей", "calories": 180, "protein": 12, "fat": 10, "carbs": 8},
    "салат цезарь с креветками": {"name": "Цезарь с креветками", "calories": 160, "protein": 14, "fat": 8, "carbs": 6},
    "салат греческий": {"name": "Греческий салат", "calories": 120, "protein": 3, "fat": 8, "carbs": 6},
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
    "салат с сыром фета": {"name": "Салат с сыром фета", "calories": 160, "protein": 6, "fat": 12, "carbs": 6},
    "салат с пармезаном": {"name": "Салат с пармезаном", "calories": 200, "protein": 10, "fat": 15, "carbs": 5},
    "салат с голубым сыром": {"name": "Салат с голубым сыром", "calories": 220, "protein": 8, "fat": 18, "carbs": 6},
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
    "салат с редисом и огурцом": {"name": "Салат с редисом и огурцом", "calories": 30, "protein": 1, "fat": 0.5, "carbs": 5},
    "салат из редиски": {"name": "Салат из редиски", "calories": 30, "protein": 1, "fat": 0.5, "carbs": 5},
    "салат из моркови по-корейски": {"name": "Морковь по-корейски", "calories": 130, "protein": 1, "fat": 8, "carbs": 12},
    "салат из свеклы с черносливом": {"name": "Салат из свеклы с черносливом", "calories": 100, "protein": 2, "fat": 4, "carbs": 15},
    "салат из свеклы с орехами": {"name": "Салат из свеклы с орехами", "calories": 120, "protein": 3, "fat": 7, "carbs": 12},
    "салат из капусты с морковью": {"name": "Салат из капусты с морковью", "calories": 40, "protein": 1, "fat": 0.5, "carbs": 8},
    "салат из пекинской капусты": {"name": "Салат из пекинской капусты", "calories": 30, "protein": 1, "fat": 0.3, "carbs": 5},
    "салат с рукколой": {"name": "Салат с рукколой", "calories": 40, "protein": 2, "fat": 2, "carbs": 4},
    "салат с рукколой и пармезаном": {"name": "Салат с рукколой и пармезаном", "calories": 120, "protein": 5, "fat": 8, "carbs": 6},
    "салат с рукколой и помидорами черри": {"name": "Салат с рукколой и черри", "calories": 60, "protein": 2, "fat": 3, "carbs": 5},
    "салат с шпинатом": {"name": "Салат со шпинатом", "calories": 40, "protein": 2, "fat": 1, "carbs": 5},
    "салат с шпинатом и клубникой": {"name": "Салат со шпинатом и клубникой", "calories": 60, "protein": 2, "fat": 2, "carbs": 8},
    "салат с айсбергом": {"name": "Салат Айсберг", "calories": 20, "protein": 1, "fat": 0, "carbs": 3},
    "салат с радиччо": {"name": "Салат Радиччо", "calories": 25, "protein": 1, "fat": 0, "carbs": 4},
    "салат с фризе": {"name": "Салат Фризе", "calories": 20, "protein": 1, "fat": 0, "carbs": 3},
    "салат с корном": {"name": "Салат Корн", "calories": 20, "protein": 1, "fat": 0, "carbs": 3},
    "салат мясной": {"name": "Мясной салат", "calories": 200, "protein": 15, "fat": 14, "carbs": 5},
    "салат столичный": {"name": "Столичный салат (мясной)", "calories": 220, "protein": 12, "fat": 16, "carbs": 6},
    "салат московский": {"name": "Московский салат", "calories": 180, "protein": 10, "fat": 12, "carbs": 8},
    "салат охотничий": {"name": "Охотничий салат", "calories": 190, "protein": 12, "fat": 13, "carbs": 7},
    "салат с колбасой": {"name": "Салат с колбасой", "calories": 200, "protein": 8, "fat": 16, "carbs": 6},
    "салат с сосисками": {"name": "Салат с сосисками", "calories": 180, "protein": 7, "fat": 14, "carbs": 7},
    "салат с копчёной курицей": {"name": "Салат с копчёной курицей", "calories": 150, "protein": 12, "fat": 8, "carbs": 6},
    "салат с копчёной рыбой": {"name": "Салат с копчёной рыбой", "calories": 140, "protein": 10, "fat": 8, "carbs": 5},
    "салат с селёдкой": {"name": "Салат с селёдкой", "calories": 160, "protein": 8, "fat": 12, "carbs": 5},
    "салат с килькой": {"name": "Салат с килькой", "calories": 150, "protein": 7, "fat": 11, "carbs": 5},
    "салат со шпротами": {"name": "Салат со шпротами", "calories": 200, "protein": 6, "fat": 16, "carbs": 6},
    "салат с семгой слабосоленой": {"name": "Салат с сёмгой слабосолёной", "calories": 170, "protein": 12, "fat": 12, "carbs": 4},
    "салат с семгой и авокадо": {"name": "Салат с сёмгой и авокадо", "calories": 200, "protein": 10, "fat": 15, "carbs": 6},
    "салат с тунцом и фасолью": {"name": "Салат с тунцом и фасолью", "calories": 140, "protein": 12, "fat": 5, "carbs": 12},
    "салат с тунцом и кукурузой": {"name": "Салат с тунцом и кукурузой", "calories": 130, "protein": 11, "fat": 4, "carbs": 12},
    "салат с тунцом и яйцом": {"name": "Салат с тунцом и яйцом", "calories": 140, "protein": 12, "fat": 6, "carbs": 8},
    "салат с крабом": {"name": "Салат с крабом", "calories": 100, "protein": 10, "fat": 4, "carbs": 6},
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

    "борщ": {"name": "Борщ", "calories": 50, "protein": 2, "fat": 1.5, "carbs": 7},
    "щи": {"name": "Щи", "calories": 40, "protein": 1.5, "fat": 1, "carbs": 6},
    "солянка": {"name": "Солянка", "calories": 80, "protein": 5, "fat": 4, "carbs": 6},
    "уха": {"name": "Уха", "calories": 40, "protein": 5, "fat": 1, "carbs": 2},
    "рассольник": {"name": "Рассольник", "calories": 50, "protein": 2, "fat": 1.5, "carbs": 6},
    "харчо": {"name": "Харчо", "calories": 80, "protein": 5, "fat": 4, "carbs": 6},
    "лагман": {"name": "Лагман", "calories": 110, "protein": 6, "fat": 4, "carbs": 12},
    "том ям": {"name": "Том Ям", "calories": 60, "protein": 4, "fat": 2.5, "carbs": 5},

    "пельмени": {"name": "Пельмени (варёные)", "calories": 250, "protein": 12, "fat": 12, "carbs": 25},
    "вареники": {"name": "Вареники с картошкой", "calories": 200, "protein": 6, "fat": 5, "carbs": 35},
    "манты": {"name": "Манты", "calories": 250, "protein": 12, "fat": 12, "carbs": 25},
    "хинкали": {"name": "Хинкали", "calories": 250, "protein": 12, "fat": 12, "carbs": 25},
    "чебуреки": {"name": "Чебуреки", "calories": 350, "protein": 10, "fat": 20, "carbs": 30},

    "пицца": {"name": "Пицца", "calories": 250, "protein": 10, "fat": 12, "carbs": 28},
    "бургер": {"name": "Бургер", "calories": 300, "protein": 15, "fat": 15, "carbs": 25},

    # 🔥 КОТЛЕТЫ И МАКАРОНЫ
    "котлета": {"name": "Котлета мясная", "calories": 250, "protein": 15, "fat": 18, "carbs": 10},
    "котлеты": {"name": "Котлеты мясные", "calories": 250, "protein": 15, "fat": 18, "carbs": 10},
    "котлета куриная": {"name": "Котлета куриная", "calories": 180, "protein": 18, "fat": 10, "carbs": 5},
    "котлета рыбная": {"name": "Котлета рыбная", "calories": 150, "protein": 14, "fat": 8, "carbs": 6},
    "котлета по-киевски": {"name": "Котлета по-киевски", "calories": 350, "protein": 18, "fat": 28, "carbs": 8},
    "макароны с котлетой": {"name": "Макароны с котлетой", "calories": 380, "protein": 20, "fat": 19, "carbs": 35},
    "макароны по-флотски": {"name": "Макароны по-флотски", "calories": 300, "protein": 15, "fat": 12, "carbs": 35},

    # ========== НАПИТКИ (безалкогольные) ==========
    "сок апельсиновый": {"name": "Сок апельсиновый", "calories": 45, "protein": 0.7, "fat": 0.2, "carbs": 10},
    "сок яблочный": {"name": "Сок яблочный", "calories": 46, "protein": 0.1, "fat": 0.1, "carbs": 11},
    "сок томатный": {"name": "Сок томатный", "calories": 17, "protein": 0.8, "fat": 0.1, "carbs": 3.5},
    "сок вишневый": {"name": "Сок вишнёвый", "calories": 47, "protein": 0.5, "fat": 0.1, "carbs": 11},
    "сок гранатовый": {"name": "Сок гранатовый", "calories": 64, "protein": 0.3, "fat": 0.1, "carbs": 14},
    "сок мультифрукт": {"name": "Сок мультифруктовый", "calories": 50, "protein": 0.3, "fat": 0.1, "carbs": 12},
    "газировка": {"name": "Газированный напиток", "calories": 40, "protein": 0, "fat": 0, "carbs": 10},
    "кола": {"name": "Кока-кола", "calories": 42, "protein": 0, "fat": 0, "carbs": 10.6},
    "пепси": {"name": "Пепси-кола", "calories": 42, "protein": 0, "fat": 0, "carbs": 10.6},
    "спрайт": {"name": "Спрайт", "calories": 40, "protein": 0, "fat": 0, "carbs": 10},
    "фанта": {"name": "Фанта", "calories": 48, "protein": 0, "fat": 0, "carbs": 12},
    "лимонад": {"name": "Лимонад", "calories": 40, "protein": 0, "fat": 0, "carbs": 10},
    "квас": {"name": "Квас", "calories": 30, "protein": 0.2, "fat": 0, "carbs": 7},
    "компот": {"name": "Компот", "calories": 60, "protein": 0.2, "fat": 0, "carbs": 15},
    "морс": {"name": "Морс", "calories": 45, "protein": 0.1, "fat": 0, "carbs": 11},
    "чай": {"name": "Чай (без сахара)", "calories": 1, "protein": 0, "fat": 0, "carbs": 0.3},
    "чай с сахаром": {"name": "Чай с сахаром (1 ч.л.)", "calories": 20, "protein": 0, "fat": 0, "carbs": 5},
    "кофе": {"name": "Кофе (без сахара)", "calories": 2, "protein": 0.1, "fat": 0, "carbs": 0},
    "кофе с молоком": {"name": "Кофе с молоком", "calories": 30, "protein": 1, "fat": 1, "carbs": 4},
    "какао": {"name": "Какао на молоке", "calories": 70, "protein": 3, "fat": 3, "carbs": 8},

    # ========== АЛКОГОЛЬ ==========
    "пиво светлое": {"name": "Пиво светлое", "calories": 43, "protein": 0.5, "fat": 0, "carbs": 3.6},
    "пиво темное": {"name": "Пиво тёмное", "calories": 50, "protein": 0.5, "fat": 0, "carbs": 5},
    "вино красное сухое": {"name": "Вино красное сухое", "calories": 68, "protein": 0.1, "fat": 0, "carbs": 2.3},
    "вино белое сухое": {"name": "Вино белое сухое", "calories": 64, "protein": 0.1, "fat": 0, "carbs": 1.5},
    "вино полусладкое": {"name": "Вино полусладкое", "calories": 85, "protein": 0.1, "fat": 0, "carbs": 5},
    "шампанское": {"name": "Шампанское", "calories": 78, "protein": 0.2, "fat": 0, "carbs": 5},
    "водка": {"name": "Водка", "calories": 235, "protein": 0, "fat": 0, "carbs": 0.1},
    "коньяк": {"name": "Коньяк", "calories": 240, "protein": 0, "fat": 0, "carbs": 1.5},
    "виски": {"name": "Виски", "calories": 235, "protein": 0, "fat": 0, "carbs": 0.1},
    "ром": {"name": "Ром", "calories": 220, "protein": 0, "fat": 0, "carbs": 0},
    "джин": {"name": "Джин", "calories": 220, "protein": 0, "fat": 0, "carbs": 0},
    "ликёр": {"name": "Ликёр", "calories": 300, "protein": 0, "fat": 0, "carbs": 30},
    "коктейль": {"name": "Алкогольный коктейль", "calories": 200, "protein": 1, "fat": 2, "carbs": 15},

    # ========== СЛАДОСТИ И ЗАКУСКИ ==========
    "шоколад молочный": {"name": "Шоколад молочный", "calories": 550, "protein": 6, "fat": 30, "carbs": 60},
    "шоколад темный": {"name": "Шоколад тёмный", "calories": 550, "protein": 7, "fat": 35, "carbs": 45},
    "конфеты шоколадные": {"name": "Конфеты шоколадные", "calories": 500, "protein": 4, "fat": 25, "carbs": 60},
    "карамель": {"name": "Карамель", "calories": 400, "protein": 0, "fat": 5, "carbs": 90},
    "зефир": {"name": "Зефир", "calories": 300, "protein": 0.5, "fat": 0, "carbs": 70},
    "пастила": {"name": "Пастила", "calories": 300, "protein": 0.5, "fat": 0, "carbs": 70},
    "мармелад": {"name": "Мармелад", "calories": 250, "protein": 0.1, "fat": 0, "carbs": 60},
    "халва": {"name": "Халва", "calories": 500, "protein": 12, "fat": 25, "carbs": 55},
    "печенье овсяное": {"name": "Печенье овсяное", "calories": 400, "protein": 6, "fat": 10, "carbs": 70},
    "печенье сахарное": {"name": "Печенье сахарное", "calories": 450, "protein": 6, "fat": 15, "carbs": 75},
    "вафли": {"name": "Вафли", "calories": 500, "protein": 5, "fat": 25, "carbs": 65},
    "пряники": {"name": "Пряники", "calories": 360, "protein": 5, "fat": 5, "carbs": 75},
    "кекс": {"name": "Кекс", "calories": 350, "protein": 5, "fat": 15, "carbs": 50},
    "пирожное": {"name": "Пирожное", "calories": 400, "protein": 4, "fat": 20, "carbs": 50},
    "торт": {"name": "Торт", "calories": 350, "protein": 4, "fat": 15, "carbs": 50},
    "мороженое": {"name": "Мороженое пломбир", "calories": 200, "protein": 3.5, "fat": 10, "carbs": 20},
    "чипсы": {"name": "Чипсы картофельные", "calories": 500, "protein": 5, "fat": 25, "carbs": 60},
    "сухарики": {"name": "Сухарики", "calories": 350, "protein": 10, "fat": 5, "carbs": 70},
    "орехи": {"name": "Орехи (смесь)", "calories": 600, "protein": 15, "fat": 55, "carbs": 15},
    "арахис": {"name": "Арахис", "calories": 550, "protein": 26, "fat": 45, "carbs": 10},
    "фисташки": {"name": "Фисташки", "calories": 560, "protein": 20, "fat": 45, "carbs": 17},
    "семечки": {"name": "Семечки подсолнуха", "calories": 600, "protein": 20, "fat": 50, "carbs": 10},

    # ========== СОУСЫ, МАСЛА, ПРИПРАВЫ ==========
    "кетчуп": {"name": "Кетчуп", "calories": 100, "protein": 1.5, "fat": 0.5, "carbs": 22},
    "майонез": {"name": "Майонез", "calories": 600, "protein": 0.5, "fat": 65, "carbs": 3},
    "горчица": {"name": "Горчица", "calories": 100, "protein": 5, "fat": 5, "carbs": 10},
    "соевый соус": {"name": "Соевый соус", "calories": 60, "protein": 8, "fat": 0, "carbs": 8},
    "соус песто": {"name": "Соус песто", "calories": 500, "protein": 5, "fat": 50, "carbs": 10},
    "соус цезарь": {"name": "Соус Цезарь", "calories": 300, "protein": 2, "fat": 25, "carbs": 15},
    "оливковое масло": {"name": "Масло оливковое", "calories": 900, "protein": 0, "fat": 100, "carbs": 0},
    "подсолнечное масло": {"name": "Масло подсолнечное", "calories": 900, "protein": 0, "fat": 100, "carbs": 0},
    "сливочное масло": {"name": "Масло сливочное", "calories": 750, "protein": 0.5, "fat": 82, "carbs": 0.5},
    "маргарин": {"name": "Маргарин", "calories": 700, "protein": 0.5, "fat": 75, "carbs": 1},
    "уксус": {"name": "Уксус столовый", "calories": 5, "protein": 0, "fat": 0, "carbs": 0.5},

    # ========== БАКАЛЕЯ ==========
    "мука пшеничная": {"name": "Мука пшеничная", "calories": 340, "protein": 10, "fat": 1, "carbs": 70},
    "мука ржаная": {"name": "Мука ржаная", "calories": 300, "protein": 8, "fat": 1, "carbs": 60},
    "сахар": {"name": "Сахар", "calories": 400, "protein": 0, "fat": 0, "carbs": 100},
    "соль": {"name": "Соль", "calories": 0, "protein": 0, "fat": 0, "carbs": 0},
    "сода": {"name": "Сода пищевая", "calories": 0, "protein": 0, "fat": 0, "carbs": 0},
    "крахмал": {"name": "Крахмал картофельный", "calories": 350, "protein": 0, "fat": 0, "carbs": 85},
    "желатин": {"name": "Желатин", "calories": 350, "protein": 85, "fat": 0, "carbs": 0},
    "разрыхлитель": {"name": "Разрыхлитель теста", "calories": 0, "protein": 0, "fat": 0, "carbs": 0},
    "какао-порошок": {"name": "Какао-порошок", "calories": 350, "protein": 20, "fat": 15, "carbs": 35},
    "сухие дрожжи": {"name": "Дрожжи сухие", "calories": 100, "protein": 10, "fat": 2, "carbs": 15},

    # ========== КОНСЕРВЫ ==========
    "тушёнка": {"name": "Тушёнка говяжья", "calories": 200, "protein": 15, "fat": 15, "carbs": 0},
    "шпроты": {"name": "Шпроты в масле", "calories": 300, "protein": 15, "fat": 25, "carbs": 0},
    "сайра": {"name": "Сайра консервированная", "calories": 250, "protein": 18, "fat": 20, "carbs": 0},
    "тунец консервированный": {"name": "Тунец консервированный", "calories": 150, "protein": 20, "fat": 7, "carbs": 0},
    "горошек зелёный": {"name": "Горошек зелёный", "calories": 60, "protein": 4, "fat": 0.5, "carbs": 10},
    "кукуруза консервированная": {"name": "Кукуруза консервированная", "calories": 70, "protein": 2, "fat": 1, "carbs": 15},
    "фасоль консервированная": {"name": "Фасоль консервированная", "calories": 90, "protein": 6, "fat": 0.5, "carbs": 15},
    "оливки": {"name": "Оливки", "calories": 150, "protein": 1, "fat": 15, "carbs": 3},
    "маслины": {"name": "Маслины", "calories": 150, "protein": 1, "fat": 15, "carbs": 3},
    "ананас консервированный": {"name": "Ананас консервированный", "calories": 60, "protein": 0.5, "fat": 0, "carbs": 15},

    # ========== ЗАМОРОЖЕННЫЕ ПРОДУКТЫ ==========
    "пельмени замороженные": {"name": "Пельмени замороженные", "calories": 250, "protein": 12, "fat": 12, "carbs": 25},
    "вареники замороженные": {"name": "Вареники замороженные", "calories": 200, "protein": 6, "fat": 5, "carbs": 35},
    "овощная смесь": {"name": "Овощная смесь замороженная", "calories": 50, "protein": 2, "fat": 0.5, "carbs": 8},
    "брокколи замороженная": {"name": "Брокколи замороженная", "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
    "ягоды замороженные": {"name": "Ягоды замороженные", "calories": 50, "protein": 0.5, "fat": 0.2, "carbs": 12},
    "клубника замороженная": {"name": "Клубника замороженная", "calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 7.7},
    "блины": {"name": "Блины замороженные", "calories": 200, "protein": 5, "fat": 8, "carbs": 28},
    "сырники": {"name": "Сырники замороженные", "calories": 200, "protein": 12, "fat": 10, "carbs": 15},

    # ========== ГОТОВЫЕ БЛЮДА (ДОПОЛНИТЕЛЬНО) ==========
    "блины с мясом": {"name": "Блины с мясом", "calories": 250, "protein": 12, "fat": 10, "carbs": 25},
    "блины с творогом": {"name": "Блины с творогом", "calories": 230, "protein": 10, "fat": 8, "carbs": 30},
    "оладьи": {"name": "Оладьи", "calories": 220, "protein": 6, "fat": 9, "carbs": 30},
    "запеканка творожная": {"name": "Запеканка творожная", "calories": 180, "protein": 12, "fat": 8, "carbs": 15},
    "омлет": {"name": "Омлет", "calories": 150, "protein": 10, "fat": 11, "carbs": 2},
    "яичница": {"name": "Яичница", "calories": 200, "protein": 12, "fat": 16, "carbs": 1},
}


# ========== ПОИСК В ЛОКАЛЬНОЙ БАЗЕ ==========
def search_local_db(query: str) -> List[Dict]:
    """Поиск в локальной базе по частичному совпадению."""
    results = []
    query_lower = query.lower().strip()
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


# ========== ПОИСК В OPENFOODFACTS (ВНЕШНИЙ API) ==========
async def search_openfoodfacts(query: str, max_results: int = 5) -> List[Dict]:
    """
    Поиск продуктов в OpenFoodFacts (бесплатно, без ключа).
    """
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
        "language": "ru"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.warning(f"OpenFoodFacts error {resp.status}")
                    return []
                data = await resp.json()
                products = data.get('products', [])
                results = []
                seen_names = set()
                for p in products:
                    name = p.get('product_name', '') or p.get('product_name_en', '') or 'Неизвестно'
                    if not name or len(name) < 3 or name in seen_names:
                        continue
                    nutriments = p.get('nutriments', {})
                    # Исключаем напитки и приправы
                    exclude = ['напиток', 'вода', 'сок', 'лимонад', 'соус', 'кетчуп', 'приправа', 'специи']
                    if any(kw in name.lower() for kw in exclude):
                        continue
                    results.append({
                        'name': name,
                        'calories': nutriments.get('energy-kcal_100g', 0) or 0,
                        'protein': nutriments.get('proteins_100g', 0) or 0,
                        'fat': nutriments.get('fat_100g', 0) or 0,
                        'carbs': nutriments.get('carbohydrates_100g', 0) or 0,
                        'source': 'openfoodfacts'
                    })
                    seen_names.add(name)
                    if len(results) >= max_results:
                        break
                return results
    except Exception as e:
        logger.warning(f"OpenFoodFacts exception: {e}")
        return []


# ========== ОСНОВНАЯ ФУНКЦИЯ ПОИСКА ==========
async def search_food(query: str, max_results: int = 5) -> List[Dict]:
    """
    Основная функция поиска продуктов.
    Сначала ищет в локальной базе, затем в OpenFoodFacts.
    """
    query = query.strip().lower()
    if not query:
        return []

    # 1. Локальный поиск
    local_results = search_local_db(query)
    if local_results:
        logger.info(f"✅ Found locally: {len(local_results)} results for '{query}'")
        return local_results[:max_results]

    # 2. Поиск в OpenFoodFacts
    logger.info(f"🌐 Searching OpenFoodFacts for '{query}'")
    off_results = await search_openfoodfacts(query, max_results)
    if off_results:
        return off_results

    # 3. Ничего не найдено
    logger.info(f"❌ No results for '{query}'")
    return []
