"""
🧠 Умный классификатор намерений NutriBuddy Bot
✅ Точное определение намерений без лишних вопросов
🎯 Использует базу продуктов, контекст и веса намерений
"""

import re
import logging
from typing import Dict, Any, List, Set, Tuple, Optional
from difflib import SequenceMatcher
from services.food_api import LOCAL_FOOD_DB
from utils.number_parser import parse_russian_number

logger = logging.getLogger(__name__)

class SmartIntentClassifier:
    """Умный классификатор намерений с контекстом и весами"""
    
    def __init__(self):
        # Загружаем базу продуктов для распознавания еды
        self.product_keywords = self._extract_product_keywords()
        self.product_aliases = self._extract_product_aliases()
        
        # Веса намерений
        self.intent_weights = {
            "steps": 100,      # Шаги - самый высокий приоритет
            "water": 95,       # Вода - высокий, но ниже чем шаги
            "activity": 90,     # Активность - высокий приоритет
            "food": 85,         # Еда - высокий приоритет
            "weather": 70,      # Погода - средний приоритет
            "ai": 60,           # AI запросы - ниже
            "unknown": 10       # Неизвестное - самый низкий
        }
        
        # Ключевые слова для разных намерений
        intent_keywords = {
            "water": ["вод", "пил", "вып", "жажд", "стакан", "кружк", "бутылк", "мл", "литр", "жидк"],
            "steps": ["шаг", "шагов", "шага", "шаги", "прош", "намот", "нашаг", "прошаг", "нагуля", "топал"],
            "activity": ["бег", "ходьб", "плав", "велосип", "трениров", "занима", "качал", "убир", "работал", "танцев"],
            "food": ["съел", "съела", "пожрал", "скушал", "хавал", "поел", "поели", "завтрак", "обед", "ужин", "перекус", "еш", "куш", "жрач", "трапез", "пожев", "заглот", "перехват"],
            "weather": ["погод", "температур", "градус", "жар", "холод", "дожд", "снег", "ветер", "солнц"],
            "ai": ["расскаж", "объясн", "что тако", "как", "почему", "совет", "помощ", "рецепт", "польз", "вред"]
        }
        
        # Ключевые слова для каждого намерения
        self.intent_patterns = {
            "water": [
                r'\bвода\b', r'\bводы\b', r'\bвыпил\b', r'\bвыпила\b', r'\bпопил\b',
                r'\bпопила\b', r'\bпить\b', r'\bхочу пить\b', r'\bвыпей\b', r'\bнапился\b',
                r'\bнапилась\b', r'\bстакан воды\b', r'\bводы выпил\b', r'\bводы выпила\b',
                r'\bмл\b', r'\bлитр\b', r'\bл\b', r'\bжидкость\b', r'\bжажда\b', r'\bпромочил\b'
            ],
            "steps": [
                r'\bшаг\b', r'\bшага\b', r'\bшагов\b', r'\bшаги\b', r'\bпрошел\b', r'\bпрошла\b',
                r'\bпрошагал\b', r'\bпрошагала\b', r'\bнамотал\b', r'\bнамотала\b', r'\bнашагал\b',
                r'\bнашагала\b', r'\bпрошагался\b', r'\bпрошагалась\b', r'\bнагулялся\b', r'\bнагулялась\b',
                r'\bтопал\b', r'\bпрошелся\b', r'\bпрошлась\b', r'\bшагов\b'
            ],
            "activity": [
                r'\bбегал\b', r'\bбегала\b', r'\bпробежал\b', r'\bпробежала\b', r'\bгулял\b', r'\bгуляла\b',
                r'\bплавал\b', r'\bплавала\b', r'\bзанимался\b', r'\bзанималась\b', r'\bтренировался\b',
                r'\bтренировалась\b', r'\bкачал\b', r'\bкачала\b', r'\bездила\b', r'\bездил\b',
                r'\bкатаюсь\b', r'\bубирал\b', r'\bубирала\b', r'\bработал\b', r'\bработала\b',
                r'\bтанцевал\b', r'\bтанцевала\b', r'\bзагонял\b', r'\bпахал\b', r'\bвкалывал\b',
                r'\bтрудился\b', r'\bтрудилась\b'
            ],
            "food": [
                r'\bсъел\b', r'\bсъела\b', r'\bпожрал\b', r'\bскушал\b', r'\bскушала\b', r'\bхавал\b',
                r'\bхавала\b', r'\bпоел\b', r'\bпоели\b', r'\bзавтракал\b', r'\bзавтракала\b',
                r'\bобедал\b', r'\бобедала\b', r'\bужинал\b', r'\bужинала\b', r'\bперекусил\b',
                r'\bперекусила\b', r'\bем\b', r'\bкушаю\b', r'\bпожевал\b', r'\bпожевала\b',
                r'\bзаглотил\b', r'\bзаглотила\b', r'\bперехватил\b', r'\bперехватила\b', r'\bпожрала\b'
            ],
            "weather": [
                r'\bпогод\b', r'\bпогода\b', r'\bтемператур\b', r'\bградус\b', r'\bжар\b', r'\bхолод\b',
                r'\bдожд\b', r'\bснег\b', r'\bветер\b', r'\bсолнц\b', r'\bна улице\b', r'\bодеться\b'
            ],
            "ai": [
                r'\bрасскаж\b', r'\bобъясн\b', r'\bчто так\b', r'\bкак\b', r'\bпочем\b', r'\bсовет\b',
                r'\bпомощ\b', r'\bрецепт\b', r'\bпольз\b', r'\bвред\b', r'\bподскаж\b', r'\bпосовет\b',
                r'\bпочему\b', r'\bзачем\b', r'\bкогда\b', r'\bгде\b', r'\bкто\b',
                r'\bнапиши\b', r'\bсоставь\b', r'\bпридумай\b', r'\bрасскажи\b',
                r'\bобъясни\b', r'\bпосоветуй\b', r'\bджарвис\b', r'\bкак работает\b'
            ]
        }
        
        # Паттерны для извлечения данных
        self.extraction_patterns = {
            "steps": [
                r'\b(\d+(?:\s*\d+)*)\s*(?:шаг|шага|шагов|шаги)\b',
                r'\b(\d+(?:[.,]\d+)?)\s*(?:к|тыс)\s*шаг',
                r'\b(\d+(?:\s*\d+)*)\s*шаг'
            ],
            "water": [
                r'\b(\d+(?:[.,]\d+)?)\s*(?:мл|л|литр|литров)\b',
                r'\b(\d+)\s*(?:стакан|кружка|бутылка)\b',
                r'\bстакан\b.*\bводы?\b',
                r'\bкружка\b.*\bводы?\b'
            ],
            "activity": [
                r'\b(\d+)\s*(?:мин|минут|час|часов)\b',
                r'\b(\d+(?:[.,]\d+)?)\s*(?:км|километр)\b'
            ]
        }
        
        # Типы приемов пищи
        self.meal_types = {
            "завтрак": "breakfast", "обед": "lunch", "ужин": "dinner",
            "перекус": "snack", "полдник": "snack", "ланч": "lunch"
        }
    
    def _extract_product_keywords(self) -> Set[str]:
        """Извлекает все ключевые слова продуктов из LOCAL_FOOD_DB"""
        keywords = set()
        for key, product in LOCAL_FOOD_DB.items():
            # Основное название
            name_words = product['name'].lower().split()
            keywords.update(name_words)
            
            # Ключ продукта
            key_words = key.lower().split()
            keywords.update(key_words)
            
            # Алиасы если есть
            if 'aliases' in product:
                for alias in product['aliases']:
                    alias_words = alias.lower().split()
                    keywords.update(alias_words)
        
        # Добавляем распространенные продукты
        common_products = [
            'яблоко', 'яблоки', 'банан', 'бананы', 'апельсин', 'апельсины',
            'курица', 'говядина', 'свинина', 'рыба', 'картошка', 'картофель',
            'макароны', 'спагетти', 'рис', 'хлеб', 'молоко', 'сыр', 'яйцо', 'яйца',
            'огурец', 'огурцы', 'помидор', 'помидоры', 'лук', 'чеснок',
            'морковь', 'капуста', 'салат', 'кефир', 'йогурт', 'творог',
            'кофе', 'чай', 'сок', 'колбаса', 'сосиски', 'котлета', 'котлеты'
        ]
        keywords.update(common_products)
        
        return keywords
    
    def _extract_product_aliases(self) -> Dict[str, List[str]]:
        """Извлекает синонимы продуктов"""
        aliases = {}
        for key, product in LOCAL_FOOD_DB.items():
            name = product['name'].lower()
            if name not in aliases:
                aliases[name] = []
            
            # Добавляем ключ как синоним
            if key.lower() != name:
                aliases[name].append(key.lower())
            
            # Добавляем алиасы
            if 'aliases' in product:
                for alias in product['aliases']:
                    alias_lower = alias.lower()
                    if alias_lower not in aliases:
                        aliases[alias_lower] = []
                    aliases[alias_lower].append(name)
                    aliases[alias_lower].append(key.lower())
        
        return aliases
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Умная классификация намерения
        
        Returns:
            {
                "intent": "food|water|steps|activity|weather|ai|unknown",
                "confidence": 0.0-1.0,
                "extracted_data": {...},
                "reasoning": "пояснение выбора"
            }
        """
        text_lower = text.lower().strip()
        scores = {}
        reasoning = {}
        
        # 1. Проверяем каждое намерение
        for intent, patterns in self.intent_patterns.items():
            score, intent_reasoning = self._calculate_intent_score(text_lower, intent, patterns)
            scores[intent] = score
            reasoning[intent] = intent_reasoning
        
        # 2. Специальная проверка для еды (самая сложная)
        food_score, food_reasoning = self._classify_food(text_lower)
        scores["food"] = max(scores.get("food", 0), food_score)
        reasoning["food"] = reasoning.get("food", "") + f" | {food_reasoning}"
        
        # 3. Применяем веса
        for intent in scores:
            scores[intent] *= self.intent_weights.get(intent, 1)
        
        # 4. Выбираем лучшее намерение
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent] / 100  # Нормализуем к 0-1
        
        # 5. Извлекаем данные для намерения
        extracted_data = self._extract_data_for_intent(text_lower, best_intent)
        
        result = {
            "intent": best_intent,
            "confidence": min(best_score, 1.0),
            "extracted_data": extracted_data,
            "reasoning": reasoning[best_intent],
            "all_scores": {k: round(v/100, 2) for k, v in scores.items()}
        }
        
        logger.info(f"🧠 Smart classification: {text} → {best_intent} ({best_score:.2f}) - {reasoning[best_intent]}")
        return result
    
    def _calculate_intent_score(self, text: str, intent: str, patterns: List[str]) -> Tuple[float, str]:
        """Рассчитывает оценку для намерения на основе паттернов"""
        score = 0
        matches = []
        
        for pattern in patterns:
            if re.search(pattern, text):
                score += 20
                matches.append(pattern)
        
        # Бонус за точное совпадение
        if score > 0:
            score += 10
        
        reasoning = f"Patterns: {len(matches)} matches"
        if matches:
            reasoning += f" ({', '.join(matches[:2])})"
        
        return score, reasoning
    
    def _classify_food(self, text: str) -> Tuple[float, str]:
        """Специальная классификация для еды"""
        score = 0
        reasons = []
        
        # 1. Проверяем ключевые слова продуктов
        words = text.split()
        food_words = 0
        matched_products = []
        
        for word in words:
            if word in self.product_keywords:
                food_words += 1
                matched_products.append(word)
        
        if food_words > 0:
            score += food_words * 15
            reasons.append(f"Food keywords: {food_words} ({', '.join(matched_products[:3])})")
        
        # 2. Проверяем синонимы
        for product_name, synonyms in self.product_aliases.items():
            if product_name in text:
                score += 25
                reasons.append(f"Product match: {product_name}")
                break
        
        # 3. Нечеткое совпадение с продуктами
        for product_key in LOCAL_FOOD_DB.keys():
            # Исключаем воду из проверки еды
            if 'вод' in product_key.lower():
                continue
            similarity = SequenceMatcher(None, text, product_key).ratio()
            if similarity > 0.7:
                score += int(similarity * 20)
                reasons.append(f"Fuzzy match: {product_key} ({similarity:.2f})")
                break
        
        # 4. Проверяем количество/вес (характерно для еды)
        if re.search(r'\b\d+\s*(?:г|гр|кг|шт|мл|л)\b', text):
            score += 15
            reasons.append("Has quantity/weight")
        
        # 5. Проверяем время приема пищи
        for meal_name, meal_en in self.meal_types.items():
            if meal_name in text:
                score += 20
                reasons.append(f"Meal type: {meal_name}")
                break
        
        reasoning = " | ".join(reasons) if reasons else "No food indicators"
        return score, reasoning
    
    def _extract_data_for_intent(self, text: str, intent: str) -> Dict[str, Any]:
        """Извлекает данные для конкретного намерения"""
        data = {"original_text": text}
        
        if intent == "water":
            data.update(self._extract_water_data(text))
        elif intent == "steps":
            data.update(self._extract_steps_data(text))
        elif intent == "activity":
            data.update(self._extract_activity_data(text))
        elif intent == "food":
            data.update(self._extract_food_data(text))
        elif intent == "weather":
            data.update(self._extract_weather_data(text))
        
        return data
    
    def _extract_water_data(self, text: str) -> Dict[str, Any]:
        """Извлекает данные о воде"""
        amount = None
        
        # Ищем количество в мл
        ml_match = re.search(r'(\d+)\s*мл', text)
        if ml_match:
            amount = int(ml_match.group(1))
        
        # Ищем количество в литрах
        l_match = re.search(r'(\d+(?:[.,]\d+)?)\s*л', text)
        if l_match:
            amount = int(float(l_match.group(1).replace(',', '.')) * 1000)
        
        # Ищем стаканы (примерно 200мл)
        glass_match = re.search(r'(\d+)\s*стакан', text)
        if glass_match and not amount:
            amount = int(glass_match.group(1)) * 200
        
        # Ищем кружки (примерно 250мл)
        cup_match = re.search(r'(\d+)\s*кружк', text)
        if cup_match and not amount:
            amount = int(cup_match.group(1)) * 250
        
        return {"amount": amount} if amount else {}
    
    def _extract_steps_data(self, text: str) -> Dict[str, Any]:
        """Извлекает данные о шагах"""
        steps = None
        
        # Ищем цифры
        number_match = re.search(r'(\d+(?:\s*\d+)*)\s*(?:шаг|шага|шагов|шаги)', text)
        if number_match:
            steps_str = number_match.group(1).replace(' ', '')
            try:
                steps = int(steps_str)
            except ValueError:
                pass
        
        # Ищем слова-числители
        word_numbers = {
            'один': 1, 'одна': 1, 'одно': 1,
            'два': 2, 'две': 2,
            'три': 3, 'четыре': 4, 'пять': 5,
            'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10
        }
        
        for word, num in word_numbers.items():
            if word in text and not steps:
                steps_match = re.search(f'{word}\\s*(?:шаг|шага|шагов|шаги)', text)
                if steps_match:
                    steps = num
                    break
        
        return {"steps": steps} if steps else {}
    
    def _extract_activity_data(self, text: str) -> Dict[str, Any]:
        """Извлекает данные об активности"""
        activity_type = None
        duration = None
        distance = None
        
        # Определяем тип активности
        activity_map = {
            'бег': 'бег', 'пробежка': 'бег', 'бегал': 'бег', 'бегала': 'бег',
            'ходьба': 'ходьба', 'гулял': 'ходьба', 'гуляла': 'ходьба', 'пешком': 'ходьба',
            'велосипед': 'велосипед', 'катаюсь': 'велосипед', 'ехал': 'велосипед', 'ездила': 'велосипед', 'ездил': 'велосипед',
            'плавание': 'плавание', 'плавал': 'плавание', 'плавала': 'плавание',
            'тренировка': 'тренировка', 'спортзал': 'тренировка', 'фитнес': 'тренировка', 'занимался': 'тренировка', 'занималась': 'тренировка',
            'качал': 'силовая_тренировка', 'качала': 'силовая_тренировка',
            'убирал': 'уборка', 'убирала': 'уборка',
            'работал': 'ремонт', 'работала': 'ремонт',
            'танцевал': 'танцы', 'танцевала': 'танцы'
        }
        for key, act_type in activity_map.items():
            if key in text:
                activity_type = act_type
                break
        
        # Извлекаем длительность
        duration_match = re.search(r'(\d+)\s*(?:мин|минут|час|часов)', text)
        if duration_match:
            duration = int(duration_match.group(1))
            if 'час' in text:
                duration *= 60
        
        # Извлекаем расстояние
        distance_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:км|километр)', text)
        if distance_match:
            distance = float(distance_match.group(1).replace(',', '.'))
        
        result = {}
        if activity_type:
            result["activity_type"] = activity_type
        if duration:
            result["duration"] = duration
        if distance:
            result["distance_km"] = distance
        
        return result
    
    def _extract_food_data(self, text: str) -> Dict[str, Any]:
        """Извлекает данные о еде"""
        meal_type = "snack"  # по умолчанию
        items = []
        
        # Определяем тип приема пищи
        for meal_name, meal_en in self.meal_types.items():
            if meal_name in text:
                meal_type = meal_en
                break
        
        # Извлекаем продукты (упрощенно)
        words = text.split()
        food_words = []
        
        for word in words:
            if word in self.product_keywords:
                food_words.append(word)
        
        if food_words:
            items = food_words
        
        result = {"meal_type": meal_type}
        if items:
            result["items"] = items
        
        return result
    
    def _extract_weather_data(self, text: str) -> Dict[str, Any]:
        """Извлекает данные о погоде"""
        city = None
        
        # Ищем город после предлогов
        city_match = re.search(r'(?:в|для)\s+([а-яё\-\s]+)', text)
        if city_match:
            city = city_match.group(1).strip()
        
        return {"city": city} if city else {}

# Глобальный экземпляр классификатора
smart_classifier = SmartIntentClassifier()

def classify(text: str) -> Dict[str, Any]:
    """Функция-обертка для совместимости"""
    result = smart_classifier.classify(text)
    
    # Конвертируем в старый формат для совместимости
    old_format = {
        "intent": result["intent"],
        "original_text": text
    }
    
    # Добавляем извлеченные данные
    for key, value in result["extracted_data"].items():
        old_format[key] = value
    
    return old_format
