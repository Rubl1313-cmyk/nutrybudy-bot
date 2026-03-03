"""
Модуль для классификации намерений пользователя по тексту.
Использует правила и словари ключевых слов.
"""
import re
from typing import Dict, Any, Optional, List
from utils.normalizer import normalize_product_name
from utils.parsers import parse_shopping_items

# Типы приёмов пищи
MEAL_TYPES = {
    "завтрак": "breakfast",
    "обед": "lunch",
    "ужин": "dinner",
    "перекус": "snack"
}

# Типы активности
ACTIVITY_TYPES = {
    "ходьба": "walking",
    "бег": "running",
    "йога": "yoga",
    "плавание": "swimming",
    "велосипед": "cycling",
    "тренажёрный зал": "gym",
    "другое": "other"
}

# Ключевые слова для определения намерений (без учёта регистра)
INTENT_KEYWORDS = {
    "food": ["запиши еду", "добавь еду", "съел", "поел", "прием пищи", "еда", "запиши обед", "запиши ужин", "запиши завтрак", "запиши перекус"],
    "water": ["вода", "выпил", "попил", "воды"],
    "shopping": ["список покупок", "купить", "добавь в список", "надо купить"],
    "activity": ["тренировка", "спорт", "занятие", "пробежка", "бег", "ходьба", "йога", "плавание", "велосипед"],
    "reminder": ["напомни", "напоминание"],
    "ai": ["ai", "аи", "спроси", "вопрос", "скажи", "привет", "помоги"]
}


def classify(text: str) -> Dict[str, Any]:
    """
    Определяет намерение пользователя по тексту.
    Возвращает словарь с ключами:
    - intent: str (food, water, shopping, activity, reminder, ai, unknown)
    - meal_type: Optional[str] (breakfast/lunch/dinner/snack) – для food
    - activity_type: Optional[str] – для activity
    - items: Optional[List[str]] – список продуктов/ингредиентов
    - duration: Optional[int] – длительность в минутах
    - reminder_title: Optional[str]
    - reminder_time: Optional[str]
    - text: исходный текст
    """
    text_lower = text.lower()
    result = {"intent": "unknown", "text": text}

    # 1. Вода (самый простой маркер)
    if any(w in text_lower for w in INTENT_KEYWORDS["water"]) and not any(w in text_lower for w in ["список", "купить"]):
        result["intent"] = "water"
        return result

    # 2. Активность
    for key, act_type in ACTIVITY_TYPES.items():
        if key in text_lower:
            result["intent"] = "activity"
            result["activity_type"] = act_type
            dur = _extract_duration(text)
            if dur:
                result["duration"] = dur
            return result

    # 3. Напоминание
    if any(k in text_lower for k in INTENT_KEYWORDS["reminder"]):
        result["intent"] = "reminder"
        # Извлекаем заголовок и время
        title = _extract_reminder_title(text)
        time = _extract_time(text)
        if title:
            result["reminder_title"] = title
        if time:
            result["reminder_time"] = time
        return result

    # 4. Список покупок
    shopping_keywords = INTENT_KEYWORDS["shopping"]
    if any(k in text_lower for k in shopping_keywords):
        result["intent"] = "shopping"
        cleaned = _remove_keywords(text_lower, shopping_keywords)
        items = parse_shopping_items(cleaned)
        result["items"] = [item[0] for item in items]
        result["items_with_quantity"] = items
        return result

    # 5. Приём пищи
    # Проверяем, есть ли ключевые слова еды или тип приёма
    food_keywords = INTENT_KEYWORDS["food"]
    if any(k in text_lower for k in food_keywords) or any(meal in text_lower for meal in MEAL_TYPES):
        result["intent"] = "food"
        # Определяем тип приёма, если есть
        for meal_ru, meal_en in MEAL_TYPES.items():
            if meal_ru in text_lower:
                result["meal_type"] = meal_en
                break
        # Удаляем ключевые слова, оставляя список продуктов
        cleaned = _remove_keywords(text_lower, list(MEAL_TYPES.keys()) + food_keywords)
        items = parse_shopping_items(cleaned)
        result["items"] = [item[0] for item in items]
        result["items_with_quantity"] = items
        return result

    # 6. Если ничего не подошло – считаем, что это запрос к AI
    result["intent"] = "ai"
    return result


def _extract_duration(text: str) -> Optional[int]:
    """Извлекает длительность в минутах."""
    match = re.search(r'(\d+)\s*(минут|мин|ч|час)', text.lower())
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if 'ч' in unit:
            num *= 60
        return num
    return None


def _extract_time(text: str) -> Optional[str]:
    """Извлекает время в формате ЧЧ:ММ."""
    match = re.search(r'(\d{1,2})[.:](\d{2})', text)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"
    return None


def _extract_reminder_title(text: str) -> Optional[str]:
    """Извлекает заголовок напоминания (убирая ключевые слова)."""
    cleaned = re.sub(r'напомни\s+', '', text, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned if cleaned else None


def _remove_keywords(text: str, keywords: List[str]) -> str:
    """Удаляет ключевые слова из текста."""
    for kw in keywords:
        text = re.sub(r'\b' + re.escape(kw) + r'\b', '', text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text).strip()
