"""
Модуль для классификации намерений пользователя по тексту.
Использует приоритеты и строгие регулярные выражения для точного определения.
Добавлено распознавание расстояния в километрах и улучшен парсинг длительности.
"""
import re
from typing import Dict, Any, Optional, List

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
    "пешком": "walking",
    "бег": "running",
    "побегал": "running",
    "бегал": "running",
    "пробежка": "running",
    "пробежал": "running",
    "йога": "yoga",
    "позанимался йогой": "yoga",
    "плавание": "swimming",
    "поплавал": "swimming",
    "велосипед": "cycling",
    "покатался на велосипеде": "cycling",
    "тренажёрный зал": "gym",
    "тренажерный зал": "gym",
    "тренировка": "workout",
    "потренировался": "workout",
    "спортзал": "gym",
    "лыжи": "skiing_cross_country",
    "беговые лыжи": "skiing_cross_country",
    "горные лыжи": "skiing_downhill",
    "сноуборд": "snowboarding",
    "коньки": "skating",
    "катание на коньках": "skating",
    "фигурное катание": "ice_skating_figure"
}

# Ключевые слова для разных намерений (с учётом границ слов)
INTENT_KEYWORDS = {
    "water": [
        r'\bвода\b', r'\bводы\b', r'\bвыпил\b', r'\bпопил\b', r'\bпить\b',
        r'\bхочу пить\b', r'\bвыпей\b', r'\bнапился\b', r'\bстакан воды\b',
        r'\bводы выпил\b'
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
        r'\bзапиши еду\b', r'\bдобавь еду\b', r'\bсъел\b', r'\bпоел\b',
        r'\bприем пищи\b', r'\bеда\b', r'\bпокушать\b', r'\bпокушал\b',
        r'\bпоесть\b', r'\bплотно поел\b', r'\bчто я ел\b'
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
        r'\bобъясни\b', r'\bпосоветуй\b'
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
    steps_match = re.search(r'(\d+)(?:\s*(?:тысяч|тыс|к|км))?\s*(?:шаг|шага|шагов|шаги)', text_lower)
    if steps_match:
        steps = int(steps_match.group(1))
        if any(x in text_lower for x in ['тысяч', 'тыс', 'к']):
            steps *= 1000
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
                # Есть ключевое слово активности, но нет параметров
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
        amount_match = re.search(r'(\d+)\s*(?:мл|литр|л|бутыл[а-я]*)', text_lower)
        if amount_match:
            result["amount"] = int(amount_match.group(1))
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

    # ----- 6. Приём пищи -----
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

    # ----- 7. Погода -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["weather"]):
        result["intent"] = "weather"
        city_match = re.search(r'(?:в|для)\s+([а-яё\-\s]+)', text_lower)
        if city_match:
            result["city"] = city_match.group(1).strip()
        else:
            result["city"] = None
        return result

    # ----- 8. AI-запросы (явные) -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["ai"]):
        result["intent"] = "ai"
        return result

    # ----- 9. Неопределённое намерение -----
    if ',' in text_lower:
        result["intent"] = "unknown"
        result["possible_food"] = True
        return result

    # Всё остальное отправляем в AI (как fallback)
    result["intent"] = "ai"
    return result

def _extract_duration(text: str) -> Optional[int]:
    """
    Извлекает длительность в минутах.
    Поддерживает форматы: "30 минут", "1 час", "2 часа 30 минут", "полчаса", "час".
    """
    # Проверка на словесные обозначения
    if re.search(r'\bполчаса\b', text):
        return 30
    if re.search(r'\bчас\b', text) and not re.search(r'\bполчаса\b', text):
        # Проверим, нет ли рядом числа (например, "1 час" обработается ниже)
        # Если есть слово "час" без числа, считаем 60 минут
        if not re.search(r'\d+\s*час', text):
            return 60

    # Поиск числа с единицей (минуты, часы)
    match = re.search(r'(\d+)\s*(минут|мин|м|час|ч|часа|часов)', text)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if 'ч' in unit:
            num *= 60
        return num

    # Поиск только числа, если рядом есть слово "минут" или "час" (уже покрыто выше)
    # Дополнительно: "30 мин" уже покрыто, но "30" без единицы не будем считать длительностью
    return None

def _extract_distance(text: str) -> Optional[float]:
    """Извлекает расстояние в километрах."""
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:км|километр|километра|километров)', text)
    if match:
        dist_str = match.group(1).replace(',', '.')
        return float(dist_str)
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
    return None

def _remove_keywords(text: str, keywords: List[str]) -> str:
    """Удаляет ключевые слова из текста."""
    for kw in keywords:
        kw_escaped = re.escape(kw)
        text = re.sub(r'\b' + kw_escaped + r'\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
