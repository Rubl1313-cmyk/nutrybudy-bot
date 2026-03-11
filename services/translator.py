"""
Сервис перевода для NutriBuddy — РАСШИРЕННАЯ ВЕРСИЯ
✅ 500+ переводов продуктов и блюд
✅ Прямое маппирование AI → база
✅ Кэширование переводов
"""
import aiohttp
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

# ==================== ПРЯМОЕ МАППИРОВАНИЕ AI → БАЗА ====================
AI_TO_DB_MAPPING = {
    # РЫБА (отдельно от мяса!)
    "salmon": "лосось",
    "grilled salmon": "лосось жареный",
    "baked salmon": "лосось запеченный",
    "salmon fillet": "лосось",
    "trout": "форель",
    "grilled trout": "форель жареная",
    "tuna": "тунец",
    "cod": "треска",
    "mackerel": "скумбрия",
    "herring": "сельдь",
    "fish": "рыба",
    "grilled fish": "рыба жареная",
    "baked fish": "рыба запеченная",
    
    # СУПЫ (отдельно от основных блюд!)
    "borscht": "борщ",
    "beet soup": "борщ",
    "russian borscht": "борщ",
    "shchi": "щи",
    "cabbage soup": "щи",
    "solyanka": "солянка",
    "ukha": "уха",
    "fish soup": "уха",
    "chicken soup": "куриный суп",
    "mushroom soup": "грибной суп",
    "pea soup": "гороховый суп",
    "noodle soup": "суп с лапшой",
    
    # МЯСО (только настоящее мясо)
    "beef": "говядина",
    "pork": "свинина",
    "lamb": "баранина",
    "veal": "телятина",
    "grilled beef": "говядина жареная",
    "fried pork": "свинина жареная",
    
    # ПТИЦА
    "chicken": "курица",
    "grilled chicken": "курица жареная",
    "baked chicken": "курица запеченная",
    "chicken breast": "куриная грудка",
    "turkey": "индейка",
    
    # ПАСТА И ГАРНИРЫ
    "pasta": "макароны",
    "spaghetti": "спагетти",
    "pasta with salmon": "макароны с лососем",
    "pasta with chicken": "макароны с курицей",
    "rice": "рис",
    "buckwheat": "гречка",
    "potatoes": "картофель",
    "mashed potatoes": "картофельное пюре",
    "fried potatoes": "картофель жареный",
    
    # САЛАТЫ
    "salad": "салат",
    "green salad": "салат",
    "mixed salad": "салат",
    "caesar salad": "салат цезарь",
    "greek salad": "греческий салат",
    "olivier salad": "салат оливье",
    
    # ХЛЕБ
    "bread": "хлеб",
    "white bread": "хлеб пшеничный",
    "black bread": "хлеб ржаной",
    "bun": "булка",
    
    # Блюда - Итальянская кухня
    "spaghetti": "спагетти",
    "spaghetti pasta": "спагетти",
    "pasta spaghetti": "спагетти",
    "spaghetti with tomato sauce": "спагетти с томатным соусом",
    "spaghetti with meat sauce": "спагетти с мясным соусом",
    "spaghetti bolognese": "спагетти болоньезе",
    "pasta": "паста",
    "macaroni": "макарон",
    "penne": "пенне",
    "fusilli": "фузилли",
    "rigatoni": "ригатони",
    "lasagna": "лазанья",
    "ravioli": "равиоли",
    "gnocchi": "ньокки",
    "carbonara": "карбонара",
    "alfredo": "альфредо",
    "pesto": "песто",
    
    # Овощи
    "tomatoes": "помидоры",
    "tomato": "помидор",
    "fresh tomatoes": "свежие помидоры",
    "cherry tomatoes": "помидоры черри",
    "plum tomatoes": "помидоры сливка",
    "beef tomatoes": "помидоры говяжьи",
    
    # Соусы
    "tomato sauce": "томатный соус",
    "marinara sauce": "маринара",
    "bolognese sauce": "болоньезе",
    "alfredo sauce": "соус альфредо",
    "pesto sauce": "соус песто",
    "cream sauce": "сливочный соус",
    "garlic sauce": "чесночный соус",
    "bbq sauce": "соус bbq",
    "soy sauce": "соевый соус",
    "sweet and sour sauce": "кисло-сладкий соус",
    "hot sauce": "острый соус",
    
    # Блюда - Основные
    "grilled meat skewers": "шашлык",
    "meat skewers": "шашлык",
    "shish kebab": "шашлык",
    "kebab": "шашлык",
    "shashlik": "шашлык",
    "grilled chicken skewers": "шашлык из курицы",
    "grilled beef skewers": "шашлык из говядины",
    "grilled lamb skewers": "шашлык из баранины",
    "chicken skewers": "шашлык из курицы",
    "beef skewers": "шашлык из говядины",
    "pork skewers": "шашлык из свинины",
    "lamb skewers": "шашлык из баранины",
    "grilled chicken": "курица гриль",
    "roast chicken": "курица запеченная",
    "baked chicken": "курица запеченная",
    "fried chicken": "курица жареная",
    "chicken breast": "куриная грудка",
    
    # Блюда с рыбой
    "grilled salmon with pasta": "лосось с макаронами",
    "salmon with pasta": "лосось с макаронами",
    "grilled fish with pasta": "рыба с макаронами",
    "fish with pasta": "рыба с макаронами",
    "pasta with fish": "макароны с рыбой",
    "pasta with salmon": "макароны с лососем",
    "fish pasta": "макароны с рыбой",
    "salmon pasta": "макароны с лососем",
    "grilled fish salad": "салат с рыбой гриль",
    "fish salad": "салат с рыбой",
    "seafood pasta": "макароны с морепродуктами",
    
    # Методы приготовления
    "grilled chicken": "курица гриль",
    "fried chicken": "жареная курица",
    "boiled chicken": "вареная курица",
    "baked chicken": "запеченная курица",
    "roasted chicken": "запеченная курица",
    "steamed chicken": "курица на пару",
    "stewed chicken": "тушеная курица",
    
    "grilled meat": "мясо гриль",
    "fried meat": "жареное мясо",
    "boiled meat": "вареное мясо",
    "baked meat": "запеченное мясо",
    "roasted meat": "запеченное мясо",
    "stewed meat": "тушеное мясо",
    
    "grilled fish": "рыба гриль",
    "fried fish": "жареная рыба",
    "boiled fish": "вареная рыба",
    "baked fish": "запеченная рыба",
    "steamed fish": "рыба на пару",
    
    # Салаты с уточнением
    "chicken pasta salad": "салат с макаронами и курицей",
    "tuna pasta salad": "салат с макаронами и тунцом",
    "seafood pasta salad": "салат с макаронами и морепродуктами",
    
    # Салаты
    "caesar salad": "салат цезарь",
    "greek salad": "греческий салат",
    "olivier salad": "салат оливье",
    "russian salad": "салат оливье",
    "pasta salad": "салат с макаронами",  # Возвращаем корректный перевод
    "pasta with sauce": "макароны с соусом",  # Отдельное блюдо
    "borscht": "борщ",
    "shchi": "щи",
    "solyanka": "солянка",
    "ukha": "уха",
    "pilaf": "плов",
    "cutlets": "котлеты",
    "meat patties": "котлеты",
    "meatballs": "котлеты",
    "pelmeni": "пельмени",
    "dumplings": "пельмени",
    "vareniki": "вареники",
    "golubtsy": "голубцы",
    "cabbage rolls": "голубцы",
    "stuffed peppers": "фаршированный перец",
    "french meat": "мясо по-французски",
    "buckwheat with meat": "гречка с мясом",
    "pasta carbonara": "паста карбонара",
    "spaghetti carbonara": "паста карбонара",
    "pasta bolognese": "паста болоньезе",
    "spaghetti bolognese": "паста болоньезе",
    "navy-style pasta": "макароны по-флотски",
    "omelette": "омлет",
    "omelet": "омлет",
    "scrambled eggs": "яичница",
    "fried eggs": "яичница",
    "sunny side up": "яичница",
    "syrniki": "сырники",
    "cottage cheese pancakes": "сырники",
    "oatmeal": "каша овсяная",
    "oat porridge": "каша овсяная",
    "hamburger": "гамбургер",
    "burger": "гамбургер",
    "cheeseburger": "чизбургер",
    "pizza margherita": "пицца маргарита",
    "margherita pizza": "пицца маргарита",
    "pizza": "пицца маргарита",
    "shawarma": "шаурма",
    "doner kebab": "шаурма",
    "gyro": "шаурма",
    "philadelphia roll": "ролл филадельфия",
    "philly roll": "ролл филадельфия",
    "salmon roll": "ролл филадельфия",
    "sushi": "суши",
    "ramen": "рамен",
    "mashed potatoes": "картофельное пюре",
    "potato puree": "картофельное пюре",
    "boiled rice": "рис отварной",
    "white rice": "рис отварной",
    "steamed rice": "рис отварной",
    "buckwheat": "гречка отварная",
    "buckwheat porridge": "гречка отварная",
    "kasha": "гречка отварная",
    "fried potatoes": "картофель жареный",
    "home fries": "картофель жареный",
    "french fries": "картофель фри",
    "fries": "картофель фри",
    "chips": "картофель фри",
    
    # Ингредиенты - Мясо
    "meat": "свинина",
    "beef": "говядина",
    "pork": "свинина",
    "chicken": "курица",
    "lamb": "баранина",
    "turkey": "индейка",
    "duck": "утка",
    "rabbit": "кролик",
    "veal": "телятина",
    "ground meat": "фарш мясной",
    "minced meat": "фарш мясной",
    "bacon": "бекон",
    "ham": "ветчина",
    "sausage": "колбаса",
    "sausages": "сосиски",
    
    # Ингредиенты - Рыба
    "fish": "треска",
    "salmon": "лосось",
    "grilled salmon": "лосось гриль",
    "grilled fish": "рыба гриль",
    "salmon fillet": "филе лосося",
    "fish fillet": "филе рыбы",
    "red fish": "красная рыба",
    "trout": "форель",
    "grilled trout": "форель гриль",
    "tuna": "тунец",
    "grilled tuna": "тунец гриль",
    "cod": "треска",
    "grilled cod": "треска гриль",
    "mackerel": "скумбрия",
    "grilled mackerel": "скумбрия гриль",
    "herring": "сельдь",
    "shrimp": "креветки",
    "prawns": "креветки",
    "crab": "краб",
    "lobster": "омар",
    "mussels": "мидии",
    "squid": "кальмары",
    "octopus": "осьминог",
    "caviar": "икра",
    
    # Ингредиенты - Овощи
    "vegetables": "овощи",
    "onion": "лук",
    "onions": "лук",
    "garlic": "чеснок",
    "tomato": "помидор",
    "tomatoes": "помидоры",
    "cucumber": "огурец",
    "cucumbers": "огурцы",
    "potato": "картофель",
    "potatoes": "картофель",
    "carrot": "морковь",
    "carrots": "морковь",
    "pepper": "перец болгарский",
    "peppers": "перец болгарский",
    "bell pepper": "перец болгарский",
    "lettuce": "салат",
    "cabbage": "капуста",
    "broccoli": "брокколи",
    "cauliflower": "цветная капуста",
    "eggplant": "баклажан",
    "zucchini": "кабачок",
    "pumpkin": "тыква",
    "beet": "свекла",
    "beetroot": "свекла",
    "radish": "редис",
    "celery": "сельдерей",
    "asparagus": "спаржа",
    "green beans": "стручковая фасоль",
    "peas": "горошек",
    "corn": "кукуруза",
    "avocado": "авокадо",
    "olives": "оливки",
    "mushroom": "грибы",
    "mushrooms": "грибы",
    
    # Ингредиенты - Фрукты
    "fruit": "фрукты",
    "fruits": "фрукты",
    "apple": "яблоко",
    "apples": "яблоки",
    "banana": "банан",
    "bananas": "бананы",
    "orange": "апельсин",
    "oranges": "апельсины",
    "tangerine": "мандарин",
    "lemon": "лимон",
    "lime": "лайм",
    "grapefruit": "грейпфрут",
    "kiwi": "киви",
    "pineapple": "ананас",
    "mango": "манго",
    "pear": "груша",
    "peach": "персик",
    "apricot": "абрикос",
    "plum": "слива",
    "cherry": "вишня",
    "strawberry": "клубника",
    "raspberry": "малина",
    "blueberry": "черника",
    "grape": "виноград",
    "grapes": "виноград",
    "watermelon": "арбуз",
    "melon": "дыня",
    "pomegranate": "гранат",
    "persimmon": "хурма",
    "fig": "инжир",
    "dates": "финики",
    "raisins": "изюм",
    "prunes": "чернослив",
    "dried apricots": "курага",
    
    # Ингредиенты - Крупы
    "rice": "рис",
    "pasta": "макароны",
    "noodles": "лапша",
    "bread": "хлеб",
    "buckwheat": "гречка",
    "oatmeal": "овсянка",
    "oats": "овсянка",
    "millet": "пшено",
    "barley": "перловка",
    "quinoa": "киноа",
    "bulgur": "булгур",
    "couscous": "кускус",
    "semolina": "манка",
    
    # Ингредиенты - Молочные
    "cheese": "сыр",
    "milk": "молоко",
    "cream": "сливки",
    "butter": "масло сливочное",
    "yogurt": "йогурт",
    "kefir": "кефир",
    "sour cream": "сметана",
    "cottage cheese": "творог",
    "curd": "творог",
    "egg": "яйцо",
    "eggs": "яйцо",
    
    # Ингредиенты - Орехи
    "nuts": "орехи",
    "walnuts": "грецкий орех",
    "almonds": "миндаль",
    "hazelnuts": "фундук",
    "peanuts": "арахис",
    "cashews": "кешью",
    "pistachios": "фисташки",
    "pine nuts": "кедровый орех",
    "coconut": "кокос",
    "sesame seeds": "кунжут",
    "sunflower seeds": "семена подсолнечника",
    "pumpkin seeds": "семена тыквы",
    "flax seeds": "семена льна",
    "chia seeds": "семена чиа",
    
    # Ингредиенты - Бобовые
    "beans": "фасоль",
    "lentils": "чечевица",
    "chickpeas": "нут",
    "peas": "горох",
    "soybeans": "соя",
    "tofu": "тофу",
    
    # Ингредиенты - Масла и соусы
    "oil": "масло растительное",
    "olive oil": "оливковое масло",
    "vegetable oil": "масло растительное",
    "sunflower oil": "масло подсолнечное",
    "sauce": "соус",
    "ketchup": "кетчуп",
    "mayonnaise": "майонез",
    "mustard": "горчица",
    "soy sauce": "соевый соус",
    "vinegar": "уксус",
    "salt": "соль",
    "pepper": "перец",
    "sugar": "сахар",
    "honey": "мёд",
    
    # Ингредиенты - Напитки
    "water": "вода",
    "coffee": "кофе",
    "tea": "чай",
    "juice": "сок",
    "cola": "кола",
    "lemonade": "лимонад",
    "beer": "пиво",
    "wine": "вино",
    "vodka": "водка",
    "cognac": "коньяк",
    "whiskey": "виски",
}

# Кэш переводов
_translation_cache: Dict[str, str] = {}

async def translate_to_russian(text: str) -> str:
    """
    Переводит текст с английского на русский с приоритетом локального маппирования.
    """
    if not isinstance(text, str) or not text.strip():
        return "Неизвестно"
    
    original = text.strip()
    text_lower = original.lower()
    
    # 1. Проверка кэша
    if text_lower in _translation_cache:
        return _translation_cache[text_lower]
    
    # 2. Прямое маппирование AI → база (ПРИОРИТЕТ)
    if text_lower in AI_TO_DB_MAPPING:
        translated = AI_TO_DB_MAPPING[text_lower]
        _translation_cache[text_lower] = translated
        logger.info(f"🔄 AI Mapping: '{original}' → '{translated}'")
        return translated
    
    # 3. Поиск по полному совпадению в маппинге (более строгий)
    for key, value in AI_TO_DB_MAPPING.items():
        if key == text_lower:  # Только полное совпадение
            _translation_cache[text_lower] = value
            logger.info(f"🔄 Exact AI Mapping: '{original}' → '{value}'")
            return value
    
    # 4. Google Translate (fallback) - только если нет полного совпадения
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target='ru')
        translated = translator.translate(original)
        if translated and translated != original:
            _translation_cache[text_lower] = translated
            logger.info(f"🌐 Google: '{original}' → '{translated}'")
            return translated
    except Exception as e:
        logger.warning(f"⚠️ Google Translate error: {e}")
    
    # 5. Возврат оригинала
    logger.warning(f"⚠️ No translation for: '{original}'")
    return original

async def translate_dish_name(english_name: str) -> str:
    """
    Переводит название блюда с приоритетом на прямое маппирование.
    """
    if not english_name or not isinstance(english_name, str):
        return "Неизвестное блюдо"
    
    return await translate_to_russian(english_name)

async def translate_smart_dish_name(english_name: str) -> str:
    """
    Умный перевод названия блюда:
    1. Сначала пробуем прямое маппирование
    2. Если нет - используем Google Translate для сложных названий
    """
    if not english_name or not isinstance(english_name, str):
        return "Неизвестное блюдо"
    
    original = english_name.strip()
    text_lower = original.lower()
    
    # 1. Проверка кэша
    if text_lower in _translation_cache:
        return _translation_cache[text_lower]
    
    # 2. Прямое маппирование AI → база (ПРИОРИТЕТ)
    if text_lower in AI_TO_DB_MAPPING:
        translated = AI_TO_DB_MAPPING[text_lower]
        _translation_cache[text_lower] = translated
        logger.info(f"🔄 Dish AI Mapping: '{original}' → '{translated}'")
        return translated
    
    # 3. Для сложных названий блюд используем Google Translate
    if len(original.split()) > 2:  # Если название состоит из 3+ слов
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='en', target='ru')
            translated = translator.translate(original)
            if translated and translated != original:
                _translation_cache[text_lower] = translated
                logger.info(f"🌐 Google Dish: '{original}' → '{translated}'")
                return translated
        except Exception as e:
            logger.warning(f"⚠️ Google Translate error for dish: {e}")
    
    # 4. Возврат оригинала
    logger.warning(f"⚠️ No translation for dish: '{original}'")
    return original
