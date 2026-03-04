"""
Модуль для классификации намерений пользователя по тексту.
Использует приоритеты и строгие регулярные выражения для точного определения.
"""
import re
from typing import Dict, Any, Optional, List

# Константы
MEAL_TYPES = {
    "завтрак": "breakfast",
    "обед": "lunch",
    "ужин": "dinner",
    "перекус": "snack"
}

ACTIVITY_TYPES = {
    "ходьба": "walking",
    "бег": "running",
    "йога": "yoga",
    "плавание": "swimming",
    "велосипед": "cycling",
    "тренажёрный зал": "gym",
    "тренажерный зал": "gym",
    "тренировка": "workout",
    "прогулка": "walking"
}

# Ключевые слова для разных намерений (с учётом границ слов)
INTENT_KEYWORDS = {
    "water": [r'\bвода\b', r'\bводы\b', r'\bвыпил\b', r'\bпопил\b'],
    "shopping": [r'\bкупить\b', r'\bсписок покупок\b', r'\bдобавь в список\b', r'\bнадо купить\b'],
    "activity": [r'\bтренировка\b', r'\bспорт\b', r'\bзанятие\b', r'\bпробежка\b'],
    "reminder": [r'\bнапомни\b', r'\bнапоминание\b'],
    "food": [r'\bзапиши еду\b', r'\bдобавь еду\b', r'\bсъел\b', r'\bпоел\b', r'\bприем пищи\b', r'\bеда\b'],
    "weather": [r'\bпогода\b', r'\bсколько градусов\b', r'\bтемпература\b', r'\bпрогноз погоды\b'],
    "ai": [r'\bai\b', r'\bаи\b', r'\bспроси\b', r'\bвопрос\b', r'\bскажи\b', r'\bпомоги\b', r'\bрецепт\b',
           r'\bчто такое\b', r'\bкак сделать\b', r'\bпочему\b', r'\bзачем\b', r'\bкогда\b', r'\bгде\b', r'\bкто\b',
           r'\bнапиши\b', r'\bсоставь\b', r'\bпридумай\b']
}

def classify(text: str) -> Dict[str, Any]:
    """
    Определяет намерение пользователя с максимальной точностью.
    Возвращает словарь с ключом 'intent' и извлечёнными параметрами.
    """
    text_lower = text.lower().strip()
    result = {"intent": "unknown", "original_text": text}

    # ----- 1. Шаги (наивысший приоритет) -----
    # Ищем число перед словом "шаг" (с учётом тысяч)
    steps_match = re.search(r'(\d+)(?:\s*(?:тысяч|тыс))?\s*шаг', text_lower)
    if steps_match:
        steps = int(steps_match.group(1))
        if 'тысяч' in text_lower or 'тыс' in text_lower:
            steps *= 1000
        result["intent"] = "activity"
        result["activity_type"] = "walking"
        result["steps"] = steps
        return result

    # ----- 2. Активность с длительностью (например, "бег 30 минут") -----
    for act_ru, act_en in ACTIVITY_TYPES.items():
        if act_ru in text_lower:
            duration = _extract_duration(text_lower)
            if duration:
                result["intent"] = "activity"
                result["activity_type"] = act_en
                result["duration"] = duration
                return result
            else:
                # Если есть ключевое слово активности, но нет длительности — возможно, пользователь хочет ввести позже
                result["intent"] = "activity"
                result["activity_type"] = act_en
                return result

    # ----- 3. Вода (с проверкой на покупку) -----
    # Сначала проверяем, не является ли это покупкой воды
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["shopping"]):
        if any(re.search(r'\bвода\b|\bводы\b', text_lower) for kw in INTENT_KEYWORDS["water"]):
            # Это покупка воды, а не питьё
            result["intent"] = "shopping"
            result["items"] = ["вода"]
            result["items_with_quantity"] = [("вода", 1, "шт")]
            return result

    # Если это не покупка, проверяем намерение выпить воду
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["water"]):
        result["intent"] = "water"
        # Извлекаем количество, если есть
        amount_match = re.search(r'(\d+)\s*(?:мл|литр|л)', text_lower)
        if amount_match:
            result["amount"] = int(amount_match.group(1))
        return result

    # ----- 4. Покупки (если есть явные ключевые слова) -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["shopping"]):
        result["intent"] = "shopping"
        # Очищаем текст от ключевых слов и извлекаем товары
        cleaned = _remove_keywords(text_lower, INTENT_KEYWORDS["shopping"])
        # Здесь можно использовать parse_shopping_items из utils
        # Для простоты пока просто вернём очищенный текст
        result["cleaned_text"] = cleaned
        return result

    # ----- 5. Напоминания -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["reminder"]):
        result["intent"] = "reminder"
        # Извлекаем заголовок и время
        title = _extract_reminder_title(text_lower)
        time = _extract_time(text_lower)
        if title:
            result["reminder_title"] = title
        if time:
            result["reminder_time"] = time
        return result

    # ----- 6. Приём пищи (еда) -----
    # Проверяем наличие ключевых слов еды или названий приёмов пищи
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["food"]) or any(meal in text_lower for meal in MEAL_TYPES):
        result["intent"] = "food"
        # Определяем тип приёма пищи
        for meal_ru, meal_en in MEAL_TYPES.items():
            if meal_ru in text_lower:
                result["meal_type"] = meal_en
                break
        # Очищаем текст от ключевых слов для извлечения продуктов
        cleaned = _remove_keywords(text_lower, list(MEAL_TYPES.keys()) + INTENT_KEYWORDS["food"])
        result["cleaned_text"] = cleaned
        return result

    # ----- 7. Погода -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["weather"]):
        result["intent"] = "weather"
        # Извлекаем название города (после "в" или "для")
        city_match = re.search(r'(?:в|для)\s+([а-яё\-\s]+)', text_lower)
        if city_match:
            result["city"] = city_match.group(1).strip()
        else:
            # Если город не указан, оставляем пустым — будет использован город из профиля
            result["city"] = None
        return result

    # ----- 8. AI-запросы (явные) -----
    if any(re.search(kw, text_lower) for kw in INTENT_KEYWORDS["ai"]):
        result["intent"] = "ai"
        return result

    # ----- 9. Неопределённое намерение -----
    # Если текст содержит запятые или похож на список продуктов
    if ',' in text_lower:
        result["intent"] = "unknown"
        result["possible_food"] = True
        return result

    # Всё остальное отправляем в AI (как fallback)
    result["intent"] = "ai"
    return result

def _extract_duration(text: str) -> Optional[int]:
    """Извлекает длительность в минутах из текста."""
    match = re.search(r'(\d+)\s*(?:минут|мин|м|час|ч)', text)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if 'ч' in unit:
            num *= 60
        return num
    return None

def _extract_reminder_title(text: str) -> Optional[str]:
    """Извлекает заголовок напоминания."""
    # Убираем ключевые слова "напомни" и время, если есть
    cleaned = re.sub(r'\bнапомни\b', '', text, flags=re.IGNORECASE)
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
        # Экранируем специальные символы в ключевом слове
        kw_escaped = re.escape(kw)
        text = re.sub(r'\b' + kw_escaped + r'\b', '', text, flags=re.IGNORECASE)
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    return text
