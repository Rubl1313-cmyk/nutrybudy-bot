"""
services/intent_classifier.py
Умный классификатор намерений для естественного диалога
"""
import re
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Классификатор намерений пользователя с поддержкой русского языка"""
    
    # Ключевые слова и паттерны для каждого намерения
    INTENT_PATTERNS = {
        'log_food': {
            'keywords': [
                'съел', 'поел', 'покушал', 'съела', 'поела', 'покушала',
                'завтрак', 'обед', 'ужин', 'перекус', 'питание', 'еда',
                'калории', 'белки', 'жиры', 'углеводы', 'кбжу',
                'грамм', 'гр', 'кг', 'порция', 'блюдо', 'рецепт'
            ],
            'patterns': [
                r'съ(е|е́)л.*?(\d+).*?(г|гр|кг)',
                r'по(е|е́)л.*?(\d+).*?(г|гр|кг)',
                r'завтрак.*?(\d+)',
                r'обед.*?(\d+)',
                r'ужин.*?(\d+)',
                r'калори.*?(\d+)',
                r'блюдо.*?(\d+)'
            ]
        },
        
        'log_drink': {
            'keywords': [
                'выпил', 'выпила', 'вода', 'воды', 'жидкость', 'напиток', 'напитки',
                'сок', 'чай', 'кофе', 'молоко', 'кефир', 'йогурт', 'компот',
                'газировка', 'кола', 'пепси', 'лимонад', 'смузи', 'коктейль',
                'мл', 'литр', 'л', 'стакан', 'стакана', 'кружка', 'чашка', 'бутылка',
                'пить', 'пил', 'пила', 'гидратация'
            ],
            'patterns': [
                r'вып(и|и́)л.*?(\d+).*?(мл|л|стакан|кружка|чашка|бутылка)',
                r'(вода|сок|чай|кофе|молоко|кефир).*?(\d+).*?(мл|л|стакан)',
                r'(\d+).*?стакан.*?(вода|сок|чай|кофе)',
                r'(\d+).*?мл.*?(вода|сок|чай|кофе)',
                r'(\d+).*?литр.*?(вода|сок|чай|кофе)',
                r'чай.*?сахар.*?(\d+)',
                r'кофе.*?молоко.*?(\d+)',
                r'апельсиновый.*?сок.*?(\d+)',
                r'яблочный.*?сок.*?(\d+)'
            ]
        },
        
        'log_water': {
            'keywords': [
                'выпил', 'выпила', 'вода', 'воды', 'жидкость',
                'мл', 'литр', 'л', 'стакан', 'стакана', 'кружка',
                'бутылка', 'пить', 'пил', 'пила', 'гидратация'
            ],
            'patterns': [
                r'вып(и|и́)л.*?(\d+).*?(мл|л|стакан|кружка)',
                r'воды.*?(\d+).*?(мл|л|стакан)',
                r'(\d+).*?стакан',
                r'(\d+).*?мл',
                r'(\d+).*?литр'
            ]
        },
        
        'log_weight': {
            'keywords': [
                'вес', 'весит', 'кг', 'килограмм', 'взвесился', 'взвесилась',
                'масса', 'весы', 'показали', 'потяжелел', 'похудел'
            ],
            'patterns': [
                r'вес.*?(\d+\.?\d*)\s*кг',
                r'взвес(и|и́)л.*?(\d+\.?\d*)',
                r'масса.*?(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*кг',
                r'потяжелел.*?на\s*(\d+\.?\d*)',
                r'похудел.*?на\s*(\d+\.?\d*)'
            ]
        },
        
        'log_activity': {
            'keywords': [
                'пробежал', 'пробежала', 'ходил', 'ходила', 'бег', 'тренировка',
                'спорт', 'гимнастика', 'йога', 'фитнес', 'шаги', 'километр',
                'км', 'метр', 'активность', 'движение', 'упражнения'
            ],
            'patterns': [
                r'пробеж(а|а́)л.*?(\d+).*?(км|м)',
                r'ход(и|и́)л.*?(\d+).*?(км|м|шаг)',
                r'тренировк.*?(\d+).*?(мин|час)',
                r'(\d+).*?шаг',
                r'(\d+).*?км',
                r'йог.*?(\d+).*?мин'
            ]
        },
        
        'show_progress': {
            'keywords': [
                'прогресс', 'статистика', 'график', 'динамика', 'результаты',
                'изменения', 'тренд', 'сколько', 'какой', 'показать', 'посмотреть'
            ],
            'patterns': [
                r'прогресс.*?за\s*(\w+)',
                r'статистик.*?за\s*(\w+)',
                r'график.*?(\w+)',
                r'динамика.*?(\w+)',
                r'результаты.*?(\w+)',
                r'покажи.*?прогресс',
                r'сколько.*?похудел',
                r'какой.*?прогресс'
            ]
        },
        
        'ask_ai': {
            'keywords': [
                'как', 'что', 'почему', 'зачем', 'сколько', 'когда', 'где',
                'совет', 'рекомендация', 'помощь', 'объясни', 'расскажи',
                'рецепт', 'диета', 'питание', 'здоровье', 'калории'
            ],
            'patterns': [
                r'как.*?\?',
                r'что.*?\?',
                r'почему.*?\?',
                r'сколько.*?\?',
                r'совет.*?\?',
                r'рецепт.*?\?',
                r'диета.*?\?',
                r'калории.*?в'
            ]
        },
        
        'help': {
            'keywords': [
                'помощь', 'инструкция', 'помоги', 'как пользоваться', 'что умеешь',
                'команды', 'функции', 'возможности', 'начать', 'старт'
            ],
            'patterns': [
                r'помощь',
                r'инструкция',
                r'как.*?пользоваться',
                r'что.*?умеешь',
                r'команды',
                r'функции'
            ]
        }
    }
    
    @classmethod
    async def classify(cls, text: str) -> Dict[str, Any]:
        """
        Классифицирует намерение пользователя
        
        Args:
            text: Текст сообщения пользователя
            
        Returns:
            Dict с полями:
            - intent: намерение
            - confidence: уверенность (0-1)
            - entities: извлеченные сущности
            - method: метод классификации (keywords/patterns/fallback)
        """
        text_lower = text.lower().strip()
        
        # 1. Быстрая проверка по ключевым словам
        keyword_result = cls._classify_by_keywords(text_lower)
        if keyword_result['confidence'] > 0.7:
            keyword_result['method'] = 'keywords'
            return keyword_result
        
        # 2. Проверка по паттернам
        pattern_result = cls._classify_by_patterns(text_lower)
        if pattern_result['confidence'] > 0.6:
            pattern_result['method'] = 'patterns'
            return pattern_result
        
        # 3. Проверка на вопросы к AI
        if cls._is_question(text_lower):
            return {
                'intent': 'ask_ai',
                'confidence': 0.8,
                'entities': {},
                'method': 'question_detection'
            }
        
        # 4. Fallback - если ничего не определили
        return {
            'intent': 'ask_ai',
            'confidence': 0.3,
            'entities': {},
            'method': 'fallback'
        }
    
    @classmethod
    def _classify_by_keywords(cls, text: str) -> Dict[str, Any]:
        """Классификация по ключевым словам"""
        scores = {}
        
        for intent, data in cls.INTENT_PATTERNS.items():
            score = 0
            keywords_found = []
            
            for keyword in data['keywords']:
                if keyword in text:
                    score += 1
                    keywords_found.append(keyword)
            
            if score > 0:
                scores[intent] = {
                    'score': score,
                    'keywords': keywords_found,
                    'confidence': min(1.0, score / 3.0)  # Нормализация
                }
            
        if not scores:
            return {'intent': 'unknown', 'confidence': 0.0, 'entities': {}}
        
        # Выбираем намерение с максимальным счетом
        best_intent = max(scores.keys(), key=lambda k: scores[k]['score'])
        return {
            'intent': best_intent,
            'confidence': scores[best_intent]['confidence'],
            'entities': {'keywords': scores[best_intent]['keywords']}
        }
    
    @classmethod
    def _classify_by_patterns(cls, text: str) -> Dict[str, Any]:
        """Классификация по регулярным выражениям"""
        matches = {}
        
        for intent, data in cls.INTENT_PATTERNS.items():
            if 'patterns' not in data:
                continue
                
            pattern_matches = []
            for pattern in data['patterns']:
                try:
                    match = re.search(pattern, text)
                    if match:
                        pattern_matches.append({
                            'pattern': pattern,
                            'match': match.group(),
                            'groups': match.groups()
                        })
                except re.error as e:
                    logger.warning(f"Invalid regex pattern: {pattern} - {e}")
            
            if pattern_matches:
                matches[intent] = {
                    'matches': pattern_matches,
                    'confidence': min(1.0, len(pattern_matches) * 0.8)
                }
        
        if not matches:
            return {'intent': 'unknown', 'confidence': 0.0, 'entities': {}}
        
        # Выбираем намерение с максимальным количеством совпадений
        best_intent = max(matches.keys(), key=lambda k: len(matches[k]['matches']))
        return {
            'intent': best_intent,
            'confidence': matches[best_intent]['confidence'],
            'entities': {
                'patterns': matches[best_intent]['matches']
            }
        }
    
    @classmethod
    def _is_question(cls, text: str) -> bool:
        """Проверяет, является ли текст вопросом"""
        question_indicators = [
            '?', 'как', 'что', 'почему', 'зачем', 'сколько', 'когда', 'где',
            'кто', 'чей', 'который', 'какой', 'какая', 'какое', 'какие',
            'можно', 'нужно', 'надо', 'должен', 'должна'
        ]
        
        return any(indicator in text for indicator in question_indicators)
    
    @classmethod
    def extract_entities(cls, text: str, intent: str) -> Dict[str, Any]:
        """Извлечение сущностей из текста в зависимости от намерения"""
        entities = {}
        
        if intent == 'log_food':
            entities.update(cls._extract_food_entities(text))
        elif intent == 'log_water':
            entities.update(cls._extract_water_entities(text))
        elif intent == 'log_weight':
            entities.update(cls._extract_weight_entities(text))
        elif intent == 'log_activity':
            entities.update(cls._extract_activity_entities(text))
        elif intent == 'show_progress':
            entities.update(cls._extract_progress_entities(text))
        
        return entities
    
    @classmethod
    def _extract_food_entities(cls, text: str) -> Dict[str, Any]:
        """Извлечение сущностей из текста о еде"""
        entities = {}
        
        # Извлечение количества
        amount_patterns = [
            r'(\d+\.?\d*)\s*(г|гр|грамм|кг|килограмм)',
            r'(\d+\.?\d*)\s*(шт|штука|порция)',
            r'(\d+\.?\d*)\s*(мл|литр|л)',
            r'(\d+\.?\d*)\s*(стакан|чашка|ложка)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                entities['amount'] = float(match.group(1))
                entities['unit'] = match.group(2)
                break
        
        # Извлечение типа приема пищи
        meal_types = ['завтрак', 'обед', 'ужин', 'перекус', 'полдник', 'ланч']
        for meal_type in meal_types:
            if meal_type in text:
                entities['meal_type'] = meal_type
                break
        
        return entities
    
    @classmethod
    def _extract_water_entities(cls, text: str) -> Dict[str, Any]:
        """Извлечение сущностей из текста о воде"""
        entities = {}
        
        # Конвертация различных единиц в мл
        water_patterns = [
            (r'(\d+)\s*мл', 1),
            (r'(\d+)\s*л', 1000),
            (r'(\d+)\s*стакан', 250),
            (r'(\d+)\s*кружка', 300),
            (r'(\d+)\s*бутылка', 500),
        ]
        
        for pattern, multiplier in water_patterns:
            match = re.search(pattern, text)
            if match:
                entities['amount_ml'] = int(match.group(1)) * multiplier
                break
        
        return entities
    
    @classmethod
    def _extract_weight_entities(cls, text: str) -> Dict[str, Any]:
        """Извлечение сущностей из текста о весе"""
        entities = {}
        
        # Извлечение веса
        weight_patterns = [
            r'вес.*?(\d+\.?\d*)\s*кг',
            r'(\d+\.?\d*)\s*кг',
            r'взвес(и|и́)л.*?(\d+\.?\d*)',
            r'масса.*?(\d+\.?\d*)'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, text)
            if match:
                weight_value = float(match.group(1) if match.group(1) != '' else match.group(2))
                entities['weight_kg'] = weight_value
                break
        
        return entities
    
    @classmethod
    def _extract_activity_entities(cls, text: str) -> Dict[str, Any]:
        """Извлечение сущностей из текста об активности"""
        entities = {}
        
        # Тип активности
        activity_types = {
            'бег': 'running',
            'ходьба': 'walking', 
            'тренировка': 'workout',
            'йога': 'yoga',
            'фитнес': 'fitness',
            'плавание': 'swimming',
            'велосипед': 'cycling'
        }
        
        for ru_type, en_type in activity_types.items():
            if ru_type in text:
                entities['activity_type'] = en_type
                break
        
        # Дистанция
        distance_patterns = [
            r'(\d+\.?\d*)\s*км',
            r'(\d+)\s*м',
            r'(\d+)\s*километр',
            r'(\d+)\s*метр'
        ]
        
        for pattern in distance_patterns:
            match = re.search(pattern, text)
            if match:
                distance = float(match.group(1))
                if 'км' in match.group() or 'километр' in match.group():
                    entities['distance_km'] = distance
                else:
                    entities['distance_m'] = distance
                break
        
        # Длительность
        duration_patterns = [
            r'(\d+)\s*мин',
            r'(\d+)\s*час',
            r'(\d+)\s*ч'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text)
            if match:
                duration = int(match.group(1))
                if 'час' in match.group() or 'ч' in match.group():
                    entities['duration_min'] = duration * 60
                else:
                    entities['duration_min'] = duration
                break
        
        # Шаги
        steps_pattern = r'(\d+)\s*шаг'
        steps_match = re.search(steps_pattern, text)
        if steps_match:
            entities['steps'] = int(steps_match.group(1))
        
        return entities
    
    @classmethod
    def _extract_progress_entities(cls, text: str) -> Dict[str, Any]:
        """Извлечение сущностей из текста о прогрессе"""
        entities = {}
        
        # Период времени
        period_patterns = [
            (r'за\s*сегодня', 'today'),
            (r'за\s*неделю', 'week'),
            (r'за\s*месяц', 'month'),
            (r'за\s*(\d+)\s*день', 'days'),
            (r'за\s*(\d+)\s*недель', 'weeks'),
            (r'за\s*(\d+)\s*месяц', 'months')
        ]
        
        for pattern, period in period_patterns:
            match = re.search(pattern, text)
            if match:
                if period.startswith('days'):
                    entities['period_days'] = int(match.group(1))
                elif period.startswith('weeks'):
                    entities['period_weeks'] = int(match.group(1))
                elif period.startswith('months'):
                    entities['period_months'] = int(match.group(1))
                else:
                    entities['period'] = period
                break
        
        # Тип прогресса
        progress_types = ['вес', 'калории', 'вода', 'активность', 'жир', 'мышцы']
        for progress_type in progress_types:
            if progress_type in text:
                entities['progress_type'] = progress_type
                break
        
        return entities
    
    @classmethod
    async def classify_with_ai(cls, text: str) -> dict:
        """
        Определяет намерение пользователя с помощью AI-модели.
        Возвращает словарь с intent, confidence и entities.
        """
        from services.cloudflare_manager import cf_manager
        
        system_prompt = """Ты — классификатор намерений для бота по питанию.
Определи, что хочет пользователь. Варианты:
- log_food: запись еды (съел, покушал, завтрак, обед, ужин, перекус, упоминание продуктов)
- log_water: запись воды (выпил, вода, стакан, мл, литр)
- log_weight: запись веса (вес, взвесился, кг)
- log_activity: запись активности (бег, ходьба, тренировка, шаги, км)
- show_progress: показать прогресс (статистика, прогресс, график, сколько похудел)
- ask_advice: спросить совет (как, что делать, рекомендация, рецепт)
- general_chat: общий вопрос или другое

Ответь только JSON в формате:
{"intent": "одно из значений", "confidence": число от 0 до 1, "entities": {}}
Если уверен, ставь confidence > 0.7, если сомневаешься — меньше.
Не добавляй пояснений, только JSON."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        result = await cf_manager._call(
            "assistant",  # используем ту же модель, но можно и отдельную быструю
            messages,
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=100
        )

        if result.get("success"):
            try:
                # Пытаемся найти JSON в строке (на случай если есть дополнительный текст)
                data = result["data"]
                json_match = re.search(r'(\{.*\})', data, re.DOTALL)
                if json_match:
                    data = json_match.group(1)
                
                # Распарсиваем JSON
                parsed = json.loads(data)
                
                # Нормализуем поля
                intent = parsed.get("intent", "general_chat")
                confidence = parsed.get("confidence", 0.5)
                entities = parsed.get("entities", {})
                
                return {
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "method": "ai"
                }
            except Exception as e:
                logger.error(f"Failed to parse AI classification: {e}")

        # Fallback на старый метод
        return cls._classify_by_keywords(text)
    
    @classmethod
    async def classify(cls, text: str) -> dict:
        """
        Основной метод классификации с fallback.
        Сначала пробует AI, если confidence низкий или ошибка – использует keywords.
        """
        try:
            result = await cls.classify_with_ai(text)
            
            # Если AI не уверен или ошибка, используем keywords
            if result.get("method") == "ai" and result.get("confidence", 0) < 0.6:
                logger.info(f"AI confidence too low ({result.get('confidence')}), using keywords fallback")
                return cls._classify_by_keywords(text)
            
            return result
        except Exception as e:
            logger.error(f"Classification error: {e}, using keywords fallback")
            return cls._classify_by_keywords(text)
    
    @classmethod
    def classify_sync(cls, text: str) -> dict:
        """
        Синхронный метод классификации для обратной совместимости.
        """
        text_lower = text.lower().strip()
        
        # 1. Быстрая проверка по ключевым словам
        keyword_result = cls._classify_by_keywords(text_lower)
        if keyword_result['confidence'] > 0.7:
            keyword_result['method'] = 'keywords'
            return keyword_result
        
        # 2. Проверка по паттернам
        pattern_result = cls._classify_by_patterns(text_lower)
        if pattern_result['confidence'] > 0.6:
            pattern_result['method'] = 'patterns'
            return pattern_result
        
        # 3. Проверка на вопросы к AI
        if cls._is_question(text_lower):
            return {
                'intent': 'ask_ai',
                'confidence': 0.8,
                'entities': {},
                'method': 'question_detection'
            }
        
        # 4. Fallback - если ничего не определили
        return {
            'intent': 'general',
            'confidence': 0.3,
            'entities': {},
            'method': 'fallback'
        }
