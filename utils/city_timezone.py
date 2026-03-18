"""
Утилиты для работы с часовыми поясами и городами
"""
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Словарь основных городов России и их часовых поясов
CITY_TIMEZONE_MAP = {
    # Москва и область (UTC+3)
    "москва": "Europe/Moscow",
    "санкт-петербург": "Europe/Moscow", 
    "спб": "Europe/Moscow",
    "новосибирск": "Asia/Novosibirsk",  # UTC+7
    "екатеринбург": "Asia/Yekaterinburg",  # UTC+5
    "нижний новгород": "Europe/Moscow",
    "казань": "Europe/Moscow",
    "челябинск": "Asia/Yekaterinburg",
    "омск": "Asia/Omsk",  # UTC+6
    "самара": "Europe/Samara",  # UTC+4
    "ростов-на-дону": "Europe/Moscow",
    "уфа": "Europe/Samara",
    "красноярск": "Asia/Krasnoyarsk",  # UTC+7
    "пермь": "Asia/Yekaterinburg",
    "воронеж": "Europe/Moscow",
    "волгоград": "Europe/Volgograd",  # UTC+4
    "краснодар": "Europe/Moscow",
    "саратов": "Europe/Samara",
    "тюмень": "Asia/Yekaterinburg",
    "тольятти": "Europe/Samara",
    "ижевск": "Europe/Samara",
    "барнаул": "Asia/Novosibirsk",
    "ульяновск": "Europe/Samara",
    "иркутск": "Asia/Irkutsk",  # UTC+8
    "хабаровск": "Asia/Khabarovsk",  # UTC+10
    "ярославль": "Europe/Moscow",
    "мурманск": "Europe/Moscow",
    "чебоксары": "Europe/Moscow",
    "тверь": "Europe/Moscow",
    "кузнецк": "Asia/Novosibirsk",
    "новокузнецк": "Asia/Novosibirsk",
    "брянск": "Europe/Moscow",
    "сургут": "Asia/Yekaterinburg",
    "смоленск": "Europe/Moscow",
    "орёл": "Europe/Moscow",
    "белгород": "Europe/Moscow",
    "владимир": "Europe/Moscow",
    "архангельск": "Europe/Moscow",
    "калуга": "Europe/Moscow",
    "ставрополь": "Europe/Moscow",
    "сочи": "Europe/Moscow",
    "златоуст": "Asia/Yekaterinburg",
    "тамбов": "Europe/Moscow",
    "грозный": "Europe/Moscow",
    "петрозаводск": "Europe/Moscow",
    "псков": "Europe/Moscow",
    "абакан": "Asia/Krasnoyarsk",
    "норильск": "Asia/Krasnoyarsk",
    "сыктывкар": "Europe/Moscow",
    "майкоп": "Europe/Moscow",
    "нальчик": "Europe/Moscow",
    "хасавюрт": "Europe/Moscow",
    "ставрополь": "Europe/Moscow",
    "терек": "Europe/Moscow",
    "дербент": "Europe/Moscow",
    "кызыл": "Asia/Krasnoyarsk",
    "магадан": "Asia/Magadan",  # UTC+11
    "петропавловск-камчатский": "Asia/Kamchatka",  # UTC+12
    "южно-сахалинск": "Asia/Sakhalin",  # UTC+10
    "анадырь": "Asia/Anadyr",  # UTC+12
    "биробиджан": "Asia/Vladivostok",  # UTC+10
    "якутск": "Asia/Yakutsk",  # UTC+9
    "петропавловск": "Asia/Novosibirsk",
    "усть-каменогорск": "Asia/Almaty",
    "павлодар": "Asia/Almaty",
    "семей": "Asia/Almaty",
    "актобе": "Asia/Aqtobe",
    "атирау": "Asia/Aqtau",
    "кызылорда": "Asia/Qyzylorda",
    "шымкент": "Asia/Tashkent",
    "ташкент": "Asia/Tashkent",
    "самарканд": "Asia/Tashkent",
    "бухара": "Asia/Tashkent",
    "фергана": "Asia/Tashkent",
    "навои": "Asia/Tashkent",
    "нукус": "Asia/Tashkent",
    "душанбе": "Asia/Dushanbe",
    "худжанд": "Asia/Dushanbe",
    "бишкек": "Asia/Bishkek",
    "ош": "Asia/Bishkek",
    "ашхабад": "Asia/Ashgabat",
    "алматы": "Asia/Almaty",
    "астана": "Asia/Almaty",
    "минск": "Europe/Minsk",
    "гомель": "Europe/Minsk",
    "витебск": "Europe/Minsk",
    "гродно": "Europe/Minsk",
    "брест": "Europe/Minsk",
    "могилёв": "Europe/Minsk",
    "киев": "Europe/Kyiv",
    "харьков": "Europe/Kyiv",
    "одесса": "Europe/Kyiv",
    "днепр": "Europe/Kyiv",
    "донецк": "Europe/Kyiv",
    "запорожье": "Europe/Kyiv",
    "львов": "Europe/Kyiv",
    "кривой рог": "Europe/Kyiv",
    "николаев": "Europe/Kyiv",
    "мариуполь": "Europe/Kyiv",
    "луганск": "Europe/Kyiv",
    "севастополь": "Europe/Kyiv",
    "винница": "Europe/Kyiv",
    "херсон": "Europe/Kyiv",
    "полтава": "Europe/Kyiv",
    "чернигов": "Europe/Kyiv",
    "черкассы": "Europe/Kyiv",
    "житомир": "Europe/Kyiv",
    "сумы": "Europe/Kyiv",
    "ровно": "Europe/Kyiv",
    "тернополь": "Europe/Kyiv",
    "ивано-франковск": "Europe/Kyiv",
    "луцк": "Europe/Kyiv",
    "белая церковь": "Europe/Kyiv",
    "краматорск": "Europe/Kyiv",
    "мелитополь": "Europe/Kyiv",
    "керчь": "Europe/Kyiv",
    "евпатория": "Europe/Kyiv",
    "ялта": "Europe/Kyiv",
    "феодосия": "Europe/Kyiv",
    "алушта": "Europe/Kyiv",
    "джанкой": "Europe/Kyiv",
    "хмельницкий": "Europe/Kyiv",
    "черновцы": "Europe/Kyiv",
    "ужгород": "Europe/Kyiv",
    "чернигов": "Europe/Kyiv",
    "кременчуг": "Europe/Kyiv",
    "горловка": "Europe/Kyiv",
    "лутугино": "Europe/Kyiv",
    "новомосковск": "Europe/Kyiv",
    "бровары": "Europe/Kyiv",
    "обухов": "Europe/Kyiv",
    "борисполь": "Europe/Kyiv",
    "ирпень": "Europe/Kyiv",
    "буча": "Europe/Kyiv",
    "вышгород": "Europe/Kyiv",
    "слуцк": "Europe/Minsk",
    "солигорск": "Europe/Minsk",
    "мозырь": "Europe/Minsk",
    "лида": "Europe/Minsk",
    "пинск": "Europe/Minsk",
    "барановичи": "Europe/Minsk",
    "орша": "Europe/Minsk",
    "могилёв": "Europe/Minsk",
    "бобруйск": "Europe/Minsk",
    "гродно": "Europe/Minsk",
    "новогрудок": "Europe/Minsk",
    "слоним": "Europe/Minsk",
    "волковыск": "Europe/Minsk",
    "пружаны": "Europe/Minsk",
    "ивье": "Europe/Minsk",
    "навагрудак": "Europe/Minsk",
    "островец": "Europe/Minsk",
    "сморгонь": "Europe/Minsk",
    "коссово": "Europe/Minsk",
    "дятлово": "Europe/Minsk",
    "лиски": "Europe/Moscow",
    "георгиевск": "Europe/Moscow",
    "пятигорск": "Europe/Moscow",
    "кисловодск": "Europe/Moscow",
    "железноводск": "Europe/Moscow",
    "минеральные воды": "Europe/Moscow",
    "ессентуки": "Europe/Moscow",
    "зеленогорск": "Europe/Moscow",
    "колпино": "Europe/Moscow",
    "пушкин": "Europe/Moscow",
    "красное село": "Europe/Moscow",
    "гатчина": "Europe/Moscow",
    "люберцы": "Europe/Moscow",
    "мытищи": "Europe/Moscow",
    "реутов": "Europe/Moscow",
    "железнодорожный": "Europe/Moscow",
    "балашиха": "Europe/Moscow",
    "подольск": "Europe/Moscow",
    "домодедово": "Europe/Moscow",
    "красногорск": "Europe/Moscow",
    "химки": "Europe/Moscow",
    "королёв": "Europe/Moscow",
    "одинцово": "Europe/Moscow",
    "долгопрудный": "Europe/Moscow",
    "лобня": "Europe/Moscow",
    "краснознаменск": "Europe/Moscow",
    "фрязино": "Europe/Moscow",
    "электросталь": "Europe/Moscow",
    "щёлково": "Europe/Moscow",
    "ивантеевка": "Europe/Moscow",
    "пушкино": "Europe/Moscow",
    "ногинск": "Europe/Moscow",
    "старая купавна": "Europe/Moscow",
    "отрадное": "Europe/Moscow",
    "железнодорожный": "Europe/Moscow",
    "клин": "Europe/Moscow",
    "серпухов": "Europe/Moscow",
    "обухово": "Europe/Moscow",
    "раменское": "Europe/Moscow",
    "бронницы": "Europe/Moscow",
    "павловский посад": "Europe/Moscow",
    "электрогорск": "Europe/Moscow",
    "заречье": "Europe/Moscow",
    "куровское": "Europe/Moscow",
    "дмитров": "Europe/Moscow",
    "дубна": "Europe/Moscow",
    "фряново": "Europe/Moscow",
    "ядром": "Europe/Moscow",
    "шаховская": "Europe/Moscow",
    "рютино": "Europe/Moscow",
    "лотошино": "Europe/Moscow",
    "талдом": "Europe/Moscow",
    "краснозаводск": "Europe/Moscow",
    "горки": "Europe/Moscow",
    "новоивановское": "Europe/Moscow",
    "первомайское": "Europe/Moscow",
    "вороновское": "Europe/Moscow",
    "кленовское": "Europe/Moscow",
    "сосенское": "Europe/Moscow",
    "воскресенское": "Europe/Moscow",
    "михайловское": "Europe/Moscow",
    "рождественно": "Europe/Moscow",
    "барвиха": "Europe/Moscow",
    "иллинское": "Europe/Moscow",
    "загорянский": "Europe/Moscow",
    "краснопахорское": "Europe/Moscow",
    "москва": "Europe/Moscow",
    "москва": "Europe/Moscow"
}

def get_timezone_from_city(city_name: str) -> Optional[str]:
    """
    Определяет часовой пояс по названию города
    
    Args:
        city_name: Название города (в нижнем регистре)
        
    Returns:
        Часовой пояс в формате IANA или None если не найден
    """
    if not city_name:
        return None
    
    # Нормализуем название города
    city_normalized = city_name.lower().strip()
    
    # Ищем точное совпадение
    if city_normalized in CITY_TIMEZONE_MAP:
        timezone = CITY_TIMEZONE_MAP[city_normalized]
        logger.info(f"🌍 Найден часовой пояс для города '{city_name}': {timezone}")
        return timezone
    
    # Ищем частичное совпадение
    for city, timezone in CITY_TIMEZONE_MAP.items():
        if city_normalized in city or city in city_normalized:
            logger.info(f"🌍 Найден часовой пояс по частичному совпадению '{city_name}' → '{city}': {timezone}")
            return timezone
    
    # Если не нашли, используем Moscow по умолчанию для России
    logger.warning(f"⚠️ Часовой пояс для города '{city_name}' не найден, используем Moscow")
    return "Europe/Moscow"

def get_timezone_display_name(timezone: str) -> str:
    """
    Возвращает человекочитаемое название часового пояса
    
    Args:
        timezone: Часовой пояс в формате IANA
        
    Returns:
        Человекочитаемое название
    """
    display_names = {
        "Europe/Moscow": "Москва (UTC+3)",
        "Asia/Novosibirsk": "Новосибирск (UTC+7)",
        "Asia/Yekaterinburg": "Екатеринбург (UTC+5)",
        "Europe/Samara": "Самара (UTC+4)",
        "Asia/Omsk": "Омск (UTC+6)",
        "Europe/Volgograd": "Волгоград (UTC+4)",
        "Asia/Krasnoyarsk": "Красноярск (UTC+7)",
        "Asia/Irkutsk": "Иркутск (UTC+8)",
        "Asia/Khabarovsk": "Хабаровск (UTC+10)",
        "Asia/Magadan": "Магадан (UTC+11)",
        "Asia/Kamchatka": "Петропавловск-Камчатский (UTC+12)",
        "Asia/Sakhalin": "Южно-Сахалинск (UTC+10)",
        "Asia/Anadyr": "Анадырь (UTC+12)",
        "Asia/Vladivostok": "Владивосток (UTC+10)",
        "Asia/Yakutsk": "Якутск (UTC+9)",
        "Asia/Almaty": "Алматы (UTC+6)",
        "Asia/Qyzylorda": "Кызылорда (UTC+5)",
        "Asia/Aqtau": "Атырау (UTC+5)",
        "Asia/Aqtobe": "Актобе (UTC+5)",
        "Asia/Tashkent": "Ташкент (UTC+5)",
        "Asia/Dushanbe": "Душанбе (UTC+5)",
        "Asia/Bishkek": "Бишкек (UTC+6)",
        "Asia/Ashgabat": "Ашхабад (UTC+5)",
        "Europe/Minsk": "Минск (UTC+3)",
        "Europe/Kyiv": "Киев (UTC+2)"
    }
    
    return display_names.get(timezone, timezone)

def parse_timezone_input(text: str) -> Optional[str]:
    """
    Парсит ввод пользователя для определения часового пояса
    
    Args:
        text: Текст от пользователя (название города или часовой пояс)
        
    Returns:
        Часовой пояс в формате IANA или None
    """
    if not text:
        return None
    
    text_normalized = text.lower().strip()
    
    # Если пользователь ввел название города
    timezone = get_timezone_from_city(text_normalized)
    if timezone:
        return timezone
    
    # Если пользователь ввел часовой пояс напрямую
    if "/" in text:
        # Проверяем валидность IANA формата
        if text in [tz for tz in set(CITY_TIMEZONE_MAP.values())]:
            return text
    
    return None
