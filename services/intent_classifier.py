"""
Модуль для классификации намерений пользователя по тексту.
Добавлено намерение "weather".
"""
import re
from typing import Dict, Any, Optional, List
from utils.normalizer import normalize_product_name
from utils.parsers import parse_shopping_items
from utils.time_parser import parse_time

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
    "другое": "other"
}

INTENT_KEYWORDS = {
    "water": ["вода", "выпил", "попил", "воды"],
    "shopping": ["список покупок", "купить", "добавь в список", "надо купить"],
    "activity": ["тренировка", "спорт", "занятие", "пробежка", "бег", "ходьба", "йога", "плавание", "велосипед"],
    "reminder": ["напомни", "напоминание"],
    "food": ["запиши еду", "добавь еду", "съел", "поел", "прием пищи", "еда", "запиши обед", "запиши ужин", "запиши завтрак", "запиши перекус"],
    "weather": ["погода", "сколько градусов", "температура", "прогноз погоды"],
    "ai": [
        "ai", "аи", "спроси", "вопрос", "скажи", "привет", "помоги", "рецепт",
        "что такое", "как сделать", "почему", "зачем", "когда", "где", "кто",
        "напиши", "составь", "придумай"
    ]
}


def classify(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    result = {"intent": "unknown", "text": text}

    # Вода
    if any(k in text_lower for k in INTENT_KEYWORDS["water"]) and not any(k in text_lower for k in ["список", "купить"]):
        result["intent"] = "water"
        return result

    # Активность
    for key, act_type in ACTIVITY_TYPES.items():
        if key in text_lower:
            result["intent"] = "activity"
            result["activity_type"] = act_type
            dur = _extract_duration(text)
            if dur:
                result["duration"] = dur
            return result

    # Напоминание
    if any(k in text_lower for k in INTENT_KEYWORDS["reminder"]):
        result["intent"] = "reminder"
        title = _extract_reminder_title(text)
        time = parse_time(text)
        if title:
            result["reminder_title"] = title
        if time:
            result["reminder_time"] = time
        return result

    # Список покупок
    if any(k in text_lower for k in INTENT_KEYWORDS["shopping"]):
        result["intent"] = "shopping"
        cleaned = _remove_keywords(text_lower, INTENT_KEYWORDS["shopping"])
        items = parse_shopping_items(cleaned)
        result["items"] = [item[0] for item in items]
        result["items_with_quantity"] = items
        return result

    # Приём пищи
    if any(k in text_lower for k in INTENT_KEYWORDS["food"]) or any(meal in text_lower for meal in MEAL_TYPES):
        result["intent"] = "food"
        for meal_ru, meal_en in MEAL_TYPES.items():
            if meal_ru in text_lower:
                result["meal_type"] = meal_en
                break
        cleaned = _remove_keywords(text_lower, list(MEAL_TYPES.keys()) + INTENT_KEYWORDS["food"])
        items = parse_shopping_items(cleaned)
        result["items"] = [item[0] for item in items]
        result["items_with_quantity"] = items
        return result

    # Погода
    if any(k in text_lower for k in INTENT_KEYWORDS["weather"]):
        result["intent"] = "weather"
        # Извлекаем название города
        city_match = re.search(r'в\s+([а-яё\-\s]+)', text_lower)
        if city_match:
            result["city"] = city_match.group(1).strip()
        return result

    # Явные AI-ключевые слова
    if any(k in text_lower for k in INTENT_KEYWORDS["ai"]):
        result["intent"] = "ai"
        return result

    # Всё остальное – в AI
    result["intent"] = "ai"
    return result


def _extract_duration(text: str) -> Optional[int]:
    match = re.search(r'(\d+)\s*(минут|мин|ч|час)', text.lower())
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if 'ч' in unit:
            num *= 60
        return num
    return None


def _extract_reminder_title(text: str) -> Optional[str]:
    cleaned = re.sub(r'напомни\s+', '', text, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned if cleaned else None


def _remove_keywords(text: str, keywords: List[str]) -> str:
    for kw in keywords:
        text = re.sub(r'\b' + re.escape(kw) + r'\b', '', text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text).strip()
