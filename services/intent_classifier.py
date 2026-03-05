"""
Модуль для классификации намерений пользователя по тексту.
Использует приоритеты и строгие регулярные выражения для точного определения.
Добавлена поддержка чисел, записанных словами, и женского рода.
"""
import re
from typing import Dict, Any, Optional, List
from utils.number_parser import parse_russian_number

# Константы
MEAL_TYPES = {
    "завтрак": "breakfast",
    "обед": "lunch",
    "ужин": "dinner",
    "перекус": "snack",
    "полдник": "snack",
    "ланч": "lunch"
}

ACTIVITY_TYPES = {
    "ходьба": "walking",
    "прогулка": "walking",
    "гулял": "walking",
    "гуляла": "walking",
    "пешком": "walking",
    "бег": "running",
    "побегал": "running",
    "побегала": "running",
    "бегал": "running",
    "бегала": "running",
    "пробежка": "running",
    "пробежал": "running",
    "пробежала": "running",
    "йога": "yoga",
    "позанимался йогой": "yoga",
    "позанималась йогой": "yoga",
    "плавание": "swimming",
    "поплавал": "swimming",
    "поплавала": "swimming",
    "велосипед": "cycling",
    "покатался на велосипеде": "cycling",
    "покаталась на велосипеде": "cycling",
    "тренажёрный зал": "gym",
    "тренажерный зал": "gym",
    "тренировка": "workout",
    "потренировался": "workout",
    "потренировалась": "workout",
    "спортзал": "gym",
    "лыжи": "skiing_cross_country",
    "беговые лыжи": "skiing_cross_country",
    "горные лыжи": "skiing_downhill",
    "сноуборд": "snowboarding",
    "коньки": "skating",
    "катание на коньках": "skating",
    "фигурное катание": "ice_skating_figure"
}

# Ключевые слова для разных намерений (с учётом женского рода)
INTENT_KEYWORDS = {
    "water": [
        r'\bвода\b', r'\bводы\b', r'\bвыпил\b', r'\bвыпила\b', r'\bпопил\b',
        r'\bпопила\b', r'\bпить\b', r'\bхочу пить\b', r'\bвыпей\b', r'\bнапился\b',
        r'\bнапилась\b', r'\bстакан воды\b', r'\bводы выпил\b', r'\bводы выпила\b'
    ],
    "shopping": [
        r'\bкупить\b', r'\bсписок покупок\b', r'\bдобавь в список\b',
        r'\bнадо купить\b', r'\bзапиши в покупки\b', r'\bдобавь в покупки\b',
        r'\bкуплю\b', r'\bв список покупок\b'
    ],
    "activity": [
        r'\bтренировка\b', r'\bспорт\b', r'\bзанятие\b', r'\bпробежка\b',
        r'\bактивность\b', r'\bупражнения\b', r'\bфитнес\b'
    ],
    "reminder": [
        r'\bнапомни\b', r'\bнапоминание\b', r'\bне забудь\b', r'\bнапомни мне\b',
        r'\bсоздай напоминание\b'
    ],
    "food": [
        r'\bзапиши еду\b', r'\bдобавь еду\b', r'\bсъел\b', r'\bсъела\b',
        r'\bпоел\b', r'\bпоела\b', r'\bпокушать\b', r'\bпокушал\b', r'\bпокушала\b',
        r'\bприем пищи\b', r'\bеда\b', r'\bпоесть\b', r'\bплотно поел\b',
        r'\bплотно поела\b', r'\bчто я ел\b', r'\bчто я ела\b'
    ],
    "weather": [
        r'\bпогода\b', r'\bсколько градусов\b', r'\bтемпература\b',
        r'\bпрогноз погоды\b', r'\bкакая погода\b', r'\bна улице\b',
        r'\bтепло\b', r'\bхолодно\b'
    ],
    "ai": [
        r'\bai\b', r'\bаи\b', r'\bспроси\b', r'\bвопрос\b', r'\bскажи\b',
        r'\bпомоги\b', r'\bрецепт\b', r'\bчто такое\b', r'\bкак сделать\b',
        r'\bпочему\b', r'\bзачем\b', r'\bкогда\b', r'\bгде\b', r'\bкто\b',
        r'\bнапиши\b', r'\bсоставь\b', r'\bпридумай\b', r'\bрасскажи\b',
        r'\bобъясни\b', r'\bпосоветуй\b', r'\bджарвис\b'
    ]
}

def classify(text: str) -> Dict[str, Any]:
    """
    Определяет намерение пользователя с максимальной точностью.
    Возвращает словарь с ключом 'intent' и извлечёнными параметрами.
    """
    text_lower = text.lower().strip()
    result = {"intent": "unknown", "original_text": text}

    # ----- 1. Шаги (наивысший приоритет) -----
    steps = _extract_steps(text_lower)
    if steps is not None:
        result["intent"] = "activity"
        result["activity_type"] = "walking"
        result["steps"] = steps
        return result

    # ----- 2. Активность с длительностью или расстоянием -----
    for act_ru, act_en in ACTIVITY_TYPES.items():
        if re.search(r'\b' + re.escape(act_ru) + r'\b', text_lower):
            duration = _extract_duration(text_lower)
            distance_km = _extract_distance(text_lower)
            if duration or distance_km:
                result["intent"] = "activity"
                result["activity_type"] = act_en
                if duration:
                    result["duration"] = duration
                if distance_km:
                    result["distance_km"] = distance_km
                return result
            else:
                result["intent"] = "activity"
                result["activity_type"] = act_en
                return result

    # ----- 3. Вода (с проверкой на покупку) -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["shopping"]):
        if re.search(r'\bвода\b|\bводы\b|\bводой\b', text_lower):
            result["intent"] = "shopping"
            result["items"] = ["вода"]
            result["items_with_quantity"] = [("вода", 1, "шт")]
            return result

    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["water"]):
        result["intent"] = "water"
        amount = _extract_water_amount(text_lower)
        if amount:
            result["amount"] = amount
        return result

    # ----- 4. Покупки -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["shopping"]):
        result["intent"] = "shopping"
        cleaned = _remove_keywords(text_lower, INTENT_KEYWORDS["shopping"])
        result["cleaned_text"] = cleaned
        return result

    # ----- 5. Напоминания -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["reminder"]):
        result["intent"] = "reminder"
        title = _extract_reminder_title(text_lower)
        time = _extract_time(text_lower)
        if title:
            result["reminder_title"] = title
        if time:
            result["reminder_time"] = time
        return result

    # ----- 6. Погода -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["weather"]):
        result["intent"] = "weather"
        city = None
        match = re.search(r'(?:в|для)\s+([а-яё\-\s]+)', text_lower)
        if match:
            city = match.group(1).strip()
        else:
            match = re.search(r'(?:погода|температура|прогноз)\s+([а-яё\-\s]+)', text_lower)
            if match:
                city = match.group(1).strip()
        result["city"] = city
        return result

    # ----- 7. AI-запросы (явные) -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["ai"]):
        result["intent"] = "ai"
        return result

    # ----- 8. Приём пищи -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["food"]) or any(
        re.search(r'\b' + re.escape(meal) + r'\b', text_lower) for meal in MEAL_TYPES
    ):
        result["intent"] = "food"
        for meal_ru, meal_en in MEAL_TYPES.items():
            if re.search(r'\b' + re.escape(meal_ru) + r'\b', text_lower):
                result["meal_type"] = meal_en
                break
        cleaned = _remove_keywords(text_lower, list(MEAL_TYPES.keys()) + INTENT_KEYWORDS["food"])
        result["cleaned_text"] = cleaned
        return result

    # ----- 9. Неопределённое намерение -----
    has_separators = ',' in text_lower or re.search(r'\bи\b|\bс\b', text_lower)
    if has_separators or (' ' in text_lower and len(text_lower.split()) >= 2):
        result["intent"] = "unknown"
        result["possible_food"] = True
        return result

    # Всё остальное отправляем в AI
    result["intent"] = "ai"
    return result

    
def _extract_steps(text: str) -> Optional[int]:
    """Извлекает количество шагов из текста (цифры или слова)."""
    # Ищем ключевое слово "шаг" в разных формах
    step_match = re.search(r'\b(шаг|шага|шагов|шаги)\b', text)
    if not step_match:
        return None
    # Пытаемся найти число перед или после ключевого слова
    # Сначала ищем цифры
    digit_match = re.search(r'(\d+(?:\s*тысяч|\s*тыс)?)\s*(?:шаг|шага|шагов|шаги)', text)
    if digit_match:
        num_str = digit_match.group(1).replace('тысяч', '').replace('тыс', '').strip()
        try:
            num = int(num_str)
            if 'тыс' in digit_match.group(0) or 'тысяч' in digit_match.group(0):
                num *= 1000
            return num
        except:
            pass
    # Ищем словесное число
    # Получаем текст до ключевого слова или после
    parts = re.split(r'\b(шаг|шага|шагов|шаги)\b', text, maxsplit=1)
    # Берём часть перед ключевым словом
    before = parts[0].strip()
    if before:
        num = parse_russian_number(before)
        if num is not None:
            return int(num)
    # Если не нашли, возможно число после (например, "шагов пять")
    if len(parts) > 2:
        after = parts[2].strip()
        num = parse_russian_number(after)
        if num is not None:
            return int(num)
    return None

def _extract_duration(text: str) -> Optional[int]:
    """
    Извлекает длительность в минутах.
    Поддерживает цифры и словесные числа, а также "полчаса", "час", "минута" и т.д.
    """
    # Проверка на специальные слова
    if 'полчаса' in text:
        return 30
    if 'час' in text and not re.search(r'\d+\s*час', text):
        # Если есть слово "час" без числа, но нет других указателей, считаем 1 час
        # Но нужно проверить, не является ли это частью составного (например, "полтора часа")
        if 'полтора' in text or 'полторы' in text:
            return 90
        if 'два часа' in text or 'три часа' in text:
            # такие случаи обработаются ниже через числа
            pass
        else:
            return 60

    # Поиск числа с единицей (минуты, часы)
    # Сначала ищем цифры
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*(минут|мин|м|час|ч|часа|часов)', text)
    if match:
        num = float(match.group(1).replace(',', '.'))
        unit = match.group(2)
        if 'ч' in unit:
            num *= 60
        return int(num)

    # Ищем словесное число перед единицей
    # Попробуем найти паттерн: слово-число + (минута/час)
    patterns = [
        (r'(\b[а-яё]+(?:\s+[а-яё]+)*?)\s+(минут|мин|час|часа|часов|ч)\b', 1),
        (r'(минут|мин|час|часа|часов|ч)\s+(\b[а-яё]+(?:\s+[а-яё]+)*?)\b', 2)
    ]
    for pattern, group_idx in patterns:
        match = re.search(pattern, text)
        if match:
            num_text = match.group(group_idx)
            num = parse_russian_number(num_text)
            if num is not None:
                unit = match.group(2) if group_idx == 1 else match.group(1)
                if 'ч' in unit:
                    num *= 60
                return int(num)
    return None

def _extract_distance(text: str) -> Optional[float]:
    """Извлекает расстояние в километрах (цифры или слова)."""
    # Сначала ищем цифры
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:км|километр|километра|километров)', text)
    if match:
        return float(match.group(1).replace(',', '.'))
    # Ищем словесное число
    patterns = [
        (r'(\b[а-яё]+(?:\s+[а-яё]+)*?)\s+(?:км|километр|километра|километров)\b', 1),
        (r'(?:км|километр|километра|километров)\s+(\b[а-яё]+(?:\s+[а-яё]+)*?)\b', 1)
    ]
    for pattern, group_idx in patterns:
        match = re.search(pattern, text)
        if match:
            num_text = match.group(group_idx)
            num = parse_russian_number(num_text)
            if num is not None:
                return float(num)
    return None

def _extract_water_amount(text: str) -> Optional[int]:
    """Извлекает количество воды в миллилитрах из текста."""
    # Сначала стандартный парсер из water_parser (цифры с единицами)
    from utils.water_parser import parse_water_amount
    amount = parse_water_amount(text)
    if amount:
        return amount
    # Если не нашли, пробуем словесные числа
    # Ищем ключевые слова: литр, мл, стакан и т.д.
    for word, ml in [('литр', 1000), ('литра', 1000), ('литров', 1000),
                     ('стакан', 250), ('стакана', 250), ('стаканов', 250),
                     ('кружка', 300), ('кружки', 300), ('бутылка', 500)]:
        if word in text:
            # Ищем число перед словом
            parts = text.split(word)
            before = parts[0].strip()
            num = parse_russian_number(before)
            if num is not None:
                return int(num * ml)
            else:
                # Если числа нет, возможно подразумевается 1
                return ml
    return None

def _extract_reminder_title(text: str) -> Optional[str]:
    """Извлекает заголовок напоминания."""
    cleaned = re.sub(r'\bнапомни\b|\bне забудь\b', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'\bв\s*\d{1,2}[:.]\d{2}\b', '', cleaned)
    cleaned = cleaned.strip()
    return cleaned if cleaned else None

def _extract_time(text: str) -> Optional[str]:
    """Извлекает время в формате ЧЧ:ММ."""
    match = re.search(r'\bв\s*(\d{1,2})[:.](\d{2})\b', text)
    if match:
        return f"{match.group(1).zfill(2)}:{match.group(2)}"
    # Можно добавить распознавание словесного времени, но пока оставим
    return None

def _remove_keywords(text: str, keywords: List[str]) -> str:
    """Удаляет ключевые слова из текста."""
    for kw in keywords:
        kw_escaped = re.escape(kw)
        text = re.sub(r'\b' + kw_escaped + r'\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
