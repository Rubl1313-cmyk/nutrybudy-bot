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

    "grilled salmon with pasta": "лосось с макаронами",
    "baked salmon with vegetables": "запеченный лосось с овощами",
    "chicken with rice": "курица с рисом",
    "beef stew with potatoes": "говяжье рагу с картофелем",
    "pasta with tomato sauce": "паста с томатным соусом",
    "spaghetti with meat sauce": "спагетти с мясным соусом",
    "caesar salad with chicken": "салат цезарь с курицей",
    "greek salad with feta": "греческий салат с фетой",
    "mashed potatoes with gravy": "картофельное пюре с подливкой",
    "fried eggs with bacon": "яичница с беконом",
    "omelette with cheese": "омлет с сыром",
    "pancakes with honey": "блины с мёдом",
    "fried chicken wings": "куриные крылышки жареные",
    "grilled vegetables": "овощи гриль",
    "steamed fish": "рыба на пару",
    "roasted chicken": "курица запеченная",
    "boiled potatoes": "картофель отварной",
    "mashed potatoes": "картофельное пюре",
    "fried potatoes": "картофель жареный",
    "baked potatoes": "картофель запечённый",
    "rice with vegetables": "рис с овощами",
    "buckwheat with mushrooms": "гречка с грибами",
    "pasta with cheese": "макароны с сыром",
    "spaghetti carbonara": "спагетти карбонара",
    "spaghetti bolognese": "спагетти болоньезе",
    "lasagna": "лазанья",
    "pizza margherita": "пицца маргарита",
    "pizza pepperoni": "пицца пепперони",
    "burger with fries": "бургер с картошкой фри",
    "chicken nuggets": "куриные наггетсы",
    "fish and chips": "рыба с картошкой фри",
    "sushi with salmon": "суши с лососем",
    "sashimi": "сашими",
    "ramen with pork": "рамен со свининой",
    "udon with chicken": "удон с курицей",
    "fried rice with egg": "жареный рис с яйцом",
    "dumplings with meat": "пельмени",
    "dumplings with potato": "вареники с картошкой",
    "dumplings with cherry": "вареники с вишней",
    "stuffed peppers": "фаршированный перец",
    "stuffed cabbage rolls": "голубцы",
    "meatballs in tomato sauce": "тефтели в томатном соусе",
    "chicken cutlet": "куриная котлета",
    "pork chop": "свиная отбивная",
    "beef steak": "говяжий стейк",
    "lamb chops": "бараньи отбивные",
    "grilled sausage": "жареная колбаса",
    "fried eggs": "яичница",
    "scrambled eggs": "омлет",
    "boiled egg": "яйцо варёное",
    "poached egg": "яйцо пашот",
    "oatmeal with berries": "овсянка с ягодами",
    "porridge with milk": "каша на молоке",
    "buckwheat porridge": "гречневая каша",
    "rice porridge": "рисовая каша",
    "millet porridge": "пшенная каша",
    "semolina porridge": "манная каша",
    "pancakes with jam": "блины с вареньем",
    "pancakes with sour cream": "блины со сметаной",
    "syrupy pancakes": "блины с сиропом",
    "cheesecakes": "сырники",
    "cottage cheese casserole": "творожная запеканка",
    "cabbage soup": "щи",
    "beetroot soup": "борщ",
    "fish soup": "уха",
    "mushroom soup": "грибной суп",
    "pea soup": "гороховый суп",
    "chicken soup": "куриный суп",
    "noodle soup": "суп с лапшой",
    "borscht with sour cream": "борщ со сметаной",
    "shchi with meat": "щи с мясом",
    "rassolnik": "рассольник",
    "solyanka": "солянка",
    "okroshka": "окрошка",
    "cold beet soup": "свекольник",
    "green borscht": "зелёный борщ",
    "kharcho": "харчо",
    "lagman": "лагман",
    "shurpa": "шурпа",
    "pilaf with lamb": "плов с бараниной",
    "pilaf with beef": "плов с говядиной",
    "pilaf with chicken": "плов с курицей",
    "uzbek pilaf": "узбекский плов",
    "kazan kebab": "казан-кебаб",
    "shashlik with onions": "шашлык с луком",
    "grilled meat skewers": "шашлык",
    "lula kebab": "люля-кебаб",
    "dolma": "долма",
    "manti": "манты",
    "khinkali": "хинкали",
    "chakhokhbili": "чахохбили",
    "satsivi": "сациви",
    "ajapsandali": "аджапсандали",
    "lobio": "лобио",
    "pkhali": "пхали",
    "khachapuri": "хачапури",
    "adjarian khachapuri": "хачапури по-аджарски",
    "imeretian khachapuri": "хачапури по-имеретински",
    "megrelian khachapuri": "хачапури по-мегрельски",
    "georgian cheese bread": "хачапури",
    "cheburek": "чебурек",
    "belyash": "беляш",
    "samsa": "самса",
    "pie with meat": "пирожок с мясом",
    "pie with cabbage": "пирожок с капустой",
    "pie with potato": "пирожок с картошкой",
    "pie with egg and onion": "пирожок с яйцом и луком",
    "pie with apple": "пирожок с яблоком",
    "cheese pie": "сырный пирог",
    "meat pie": "мясной пирог",
    "fish pie": "рыбный пирог",
    "cabbage pie": "пирог с капустой",
    "potato pie": "пирог с картошкой",
    "apple pie": "яблочный пирог",
    "cottage cheese pie": "творожный пирог",
    "honey cake": "медовик",
    "napoleon cake": "наполеон",
    "tiramisu": "тирамису",
    "panna cotta": "панна-котта",
    "creme brulee": "крем-брюле",
    "ice cream": "мороженое",
    "chocolate ice cream": "шоколадное мороженое",
    "strawberry ice cream": "клубничное мороженое",
    "vanilla ice cream": "ванильное мороженое",
    "fruit sorbet": "фруктовый сорбет",
    "fruit salad": "фруктовый салат",
    "fruit platter": "фруктовая тарелка",
    "cheese plate": "сырная тарелка",
    "meat platter": "мясная тарелка",
    "seafood platter": "тарелка морепродуктов",
    "vegetable platter": "овощная тарелка",
    "cold cuts": "мясная нарезка",
    "sausage platter": "колбасная нарезка",
    "cheese and ham": "сырно-ветчинная нарезка",
    "olives and cheese": "оливки с сыром",
    "pickles": "соленья",
    "marinated mushrooms": "маринованные грибы",
    "sauerkraut": "квашеная капуста",
    "kimchi": "кимчи",
    "pickled cucumbers": "солёные огурцы",
    "pickled tomatoes": "солёные помидоры",
    "pickled peppers": "маринованный перец",
    "pickled garlic": "маринованный чеснок",
    "pickled eggplant": "маринованные баклажаны",
    "pickled zucchini": "маринованные кабачки",
    "pickled squash": "маринованные патиссоны",
    "pickled mix": "ассорти маринованное",
    "canned vegetables": "консервированные овощи",
    "canned fish": "рыбные консервы",
    "sprats": "шпроты",
    "sardines": "сардины",
    "tuna in oil": "тунец в масле",
    "tuna in water": "тунец в собственном соку",
    "salted herring": "солёная сельдь",
    "smoked herring": "копчёная сельдь",
    "smoked mackerel": "копчёная скумбрия",
    "smoked salmon": "копчёный лосось",
    "smoked trout": "копчёная форель",
    "smoked eel": "копчёный угорь",
    "smoked chicken": "копчёная курица",
    "smoked meat": "копчёное мясо",
    "smoked sausage": "копчёная колбаса",
    "smoked cheese": "копчёный сыр",
    "dried fish": "сушёная рыба",
    "dried meat": "сушёное мясо",
    "jerky": "джерки",
    "bacon": "бекон",
    "ham": "ветчина",
    "prosciutto": "прошутто",
    "salami": "салями",
    "pepperoni": "пепперони",
    "chorizo": "чоризо",
    "bratwurst": "братвурст",
    "frankfurter": "франкфуртская сосиска",
    "wiener": "венская сосиска",
    "hot dog": "хот-дог",
    "bratwurst with mustard": "братвурст с горчицей",
    "currywurst": "карривурст",
    "kebab": "кебаб",
    "doner kebab": "донер-кебаб",
    "gyros": "гирос",
    "souvlaki": "сувлаки",
    "taco": "тако",
    "burrito": "буррито",
    "enchilada": "энчилада",
    "quesadilla": "кесадилья",
    "nachos": "начос",
    "tortilla chips": "тортилья чипсы",
    "guacamole": "гуакамоле",
    "salsa": "сальса",
    "sour cream": "сметана",
    "yogurt sauce": "йогуртовый соус",
    "tzatziki": "цацики",
    "hummus": "хумус",
    "baba ganoush": "баба-гануш",
    "falafel": "фалафель",
    "tabbouleh": "табуле",
    "fattoush": "фаттуш",
    "couscous": "кускус",
    "bulgur": "булгур",
    "quinoa": "киноа",
    "freekeh": "фрике",
    "lentils": "чечевица",
    "chickpeas": "нут",
    "beans": "фасоль",
    "black beans": "чёрная фасоль",
    "red beans": "красная фасоль",
    "white beans": "белая фасоль",
    "kidney beans": "фасоль",
    "pinto beans": "фасоль пинто",
    "cannellini beans": "фасоль каннеллини",
    "fava beans": "бобы фава",
    "edamame": "эдамаме",
    "soybeans": "соевые бобы",
    "tofu": "тофу",
    "tempeh": "темпе",
    "seitan": "сейтан",
    "textured vegetable protein": "текстурированный растительный белок",
    "plant-based meat": "растительное мясо",
    "vegetarian burger": "вегетарианский бургер",
    "vegan burger": "веганский бургер",
    "impossible burger": "импассибл бургер",
    "beyond burger": "бийонд бургер",
    "quinoa salad": "салат с киноа",
    "lentil soup": "чечевичный суп",
    "bean soup": "бобовый суп",
    "chickpea curry": "карри из нута",
    "lentil curry": "карри из чечевицы",
    "tofu curry": "карри с тофу",
    "vegetable curry": "овощное карри",
    "thai curry": "тайское карри",
    "green curry": "зелёное карри",
    "red curry": "красное карри",
    "yellow curry": "жёлтое карри",
    "massaman curry": "массаман карри",
    "panang curry": "пананг карри",
    "khao soi": "кхао сой",
    "pho": "фо",
    "ramen": "рамен",
    "udon": "удон",
    "soba": "соба",
    "somen": "сомэн",
    "rice noodles": "рисовая лапша",
    "glass noodles": "стеклянная лапша",
    "vermicelli": "вермишель",
    "fettuccine": "феттучине",
    "tagliatelle": "тальятелле",
    "pappardelle": "паппарделле",
    "ravioli": "равиоли",
    "tortellini": "тортеллини",
    "gnocchi": "ньокки",
    "spaetzle": "шпецле",
    "pierogi": "пироги (польские)",
    "pelmeni": "пельмени",
    "vareniki": "вареники",
    "kolduny": "колдуны",
    "zeppelini": "цеппелины",
    "cannelloni": "каннеллони",
    "manicotti": "маникотти",
    "stuffed shells": "фаршированные ракушки",
    "lasagna": "лазанья",
    "moussaka": "мусака",
    "pastitsio": "пастицио",
    "pie": "пирог",
    "quiche": "киш",
    "tart": "тарт",
    "flan": "флан",
    "clafoutis": "клафути",
    "crumble": "крамбл",
    "cobbler": "коблер",
    "pie with berries": "пирог с ягодами",
    "pie with cherries": "пирог с вишней",
    "pie with apples": "пирог с яблоками",
    "pie with peaches": "пирог с персиками",
    "pie with pears": "пирог с грушами",
    "pie with plums": "пирог со сливами",
    "pie with rhubarb": "пирог с ревенем",
    "pie with custard": "пирог с заварным кремом",
    "pie with cream": "пирог со сливками",
    "pie with chocolate": "пирог с шоколадом",
    "pie with nuts": "пирог с орехами",
    "pie with almonds": "пирог с миндалём",
    "pie with walnuts": "пирог с грецкими орехами",
    "pie with pecans": "пирог с пеканом",
    "pie with pistachios": "пирог с фисташками",
    "pie with coconut": "пирог с кокосом",
    "pie with raisins": "пирог с изюмом",
    "pie with dried apricots": "пирог с курагой",
    "pie with prunes": "пирог с черносливом",
    "pie with dates": "пирог с финиками",
    "pie with figs": "пирог с инжиром",
    "pie with poppy seeds": "пирог с маком",
    "pie with sesame seeds": "пирог с кунжутом",
    "pie with sunflower seeds": "пирог с семечками",
    "pie with pumpkin seeds": "пирог с тыквенными семечками",
    "pie with chia seeds": "пирог с семенами чиа",
    "pie with flax seeds": "пирог с семенами льна",
    "pie with hemp seeds": "пирог с конопляными семенами"
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
