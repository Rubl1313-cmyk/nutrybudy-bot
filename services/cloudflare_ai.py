# services/cloudflare_ai.py
"""
Cloudflare Workers AI Integration for NutriBuddy
✅ Улучшенное распознавание еды с весами, ингредиентами и КБЖУ
✅ Мультимодельный режим с fallback
✅ Каскадное распознавание с голосованием
✅ Валидация и постобработка результатов
"""

import aiohttp
import os
import logging
import asyncio
import json
import io
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image

logger = logging.getLogger(__name__)

# ========== КОНФИГУРАЦИЯ ==========
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Модели для распознавания еды (порядок важен: сначала более точные)
VISION_MODELS = [
    "@cf/llava-hf/llava-1.5-7b-hf",      # Лучшая для общих объектов
    "@cf/unum/uform-gen2-qwen-500m",     # Быстрая, хороша для текста
]

# Модели для транскрибации аудио
WHISPER_MODELS = [
    "@cf/openai/whisper",
    "@cf/openai/whisper-large-v3-turbo",
]

# ========== ПРОМПТЫ ==========

FOOD_RECOGNITION_PROMPT = """
You are a professional food nutritionist AI. Analyze this food image and return EXACT JSON:

{
  "dish_name": "точное название блюда на русском языке",
  "confidence": 0.0-1.0,
  "main_ingredient": "главный белковый продукт (мясо, рыба, яйца, тофу)",
  "ingredients": [
    {"name": "продукт на русском", "type": "main|side|garnish|sauce", "estimated_weight_grams": 0-1000}
  ],
  "cooking_method": "жареный|вареный|запеченный|сырой|на гриле|тушеный",
  "portion_size": "small|medium|large",
  "total_estimated_calories": 0-2000,
  "notes": "дополнительные наблюдения (видимый соус, масло и т.д.)"
}

RULES:
1. Main ingredient = primary protein source (meat, fish, eggs, tofu)
2. Side = vegetables, grains, potatoes, pasta
3. Garnish = herbs, lemon, decorative items, small additions
4. Sauce = any visible sauces, dressings, oils, mayo
5. Estimate weights based on standard portions:
   - Small portion: 150-200g total
   - Medium portion: 250-350g total  
   - Large portion: 400-500g+ total
6. For mixed dishes (салат, рагу, суп), estimate each component separately
7. If uncertain about weight, use realistic estimates based on visual cues
8. Return ONLY valid JSON, no other text. No markdown, no code blocks.

Example output:
{
  "dish_name": "Цезарь с курицей",
  "confidence": 0.85,
  "main_ingredient": "куриная грудка",
  "ingredients": [
    {"name": "куриная грудка", "type": "main", "estimated_weight_grams": 150},
    {"name": "салат романо", "type": "side", "estimated_weight_grams": 100},
    {"name": "сыр пармезан", "type": "side", "estimated_weight_grams": 30},
    {"name": "сухарики", "type": "garnish", "estimated_weight_grams": 20},
    {"name": "соус цезарь", "type": "sauce", "estimated_weight_grams": 40}
  ],
  "cooking_method": "на гриле",
  "portion_size": "medium",
  "total_estimated_calories": 450,
  "notes": "видимая заправка, курица без кожи"
}
"""

SIMPLE_FOOD_PROMPT = """
You are a precise food recognition AI. Look at this image and describe exactly what you see. 
Return a JSON object with:
- "dish_name": a short, specific name of the dish in Russian (if known, otherwise in English)
- "ingredients": list of main visible ingredients in Russian (each as a string)

Only output valid JSON, no other text. Do not escape characters.

Example: {"dish_name": "жареная курица с овощами", "ingredients": ["курица", "помидоры", "огурцы", "лимон"]}
"""

INGREDIENTS_ONLY_PROMPT = """
List all food items visible in this image. Be specific. Return as a comma-separated list in Russian.
Example: курица, помидоры, огурцы, лимон, соус
"""

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def _prepare_image(image_bytes: bytes) -> bytes:
    """
    Оптимизация изображения для Cloudflare AI.
    - Конвертирует в RGB
    - Уменьшает до 1024x1024
    - Сжимает в JPEG с качеством 85%
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Конвертируем в RGB (если есть альфа-канал)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Уменьшаем размер
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        # Сохраняем в JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        
        return output.getvalue()
    except Exception as e:
        logger.warning(f"⚠️ Image prep error: {e}")
        return image_bytes


def _bytes_to_array(image_bytes: bytes) -> list:
    """Конвертирует байты в массив для Cloudflare API."""
    return list(image_bytes)


def _extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Извлекает JSON из текста, удаляя возможные экранирования и markdown.
    """
    if not text:
        return None
    
    # Удаляем markdown блоки кода
    text = text.replace('```json', '').replace('```', '')
    
    # Находим начало и конец JSON
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1 or end <= start:
        return None
    
    json_str = text[start:end+1]
    
    # Удаляем экранирование
    json_str = json_str.replace('\\_', '_').replace('\\"', '"').replace('\\n', ' ')
    
    try:
        data = json.loads(json_str)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}")
        return None


def _validate_food_data(data: Dict) -> bool:
    """
    Проверяет, что распознанные данные выглядят правдоподобно.
    """
    if not isinstance(data, dict):
        return False
    
    dish = data.get('dish_name', '')
    ingredients = data.get('ingredients', [])
    
    # Проверка названия блюда
    if not dish or len(dish) < 3:
        return False
    
    # Проверка ингредиентов
    if not isinstance(ingredients, list) or len(ingredients) < 1:
        return False
    
    # Проверка на чрезмерные повторы
    unique_ingredients = set(ing.get('name', '') for ing in ingredients)
    if len(unique_ingredients) < len(ingredients) * 0.5:
        logger.warning(f"Validation failed: too many repeats in ingredients")
        return False
    
    # Проверка весов (если есть)
    for ing in ingredients:
        weight = ing.get('estimated_weight_grams', 0)
        if weight < 0 or weight > 2000:
            logger.warning(f"Validation failed: unrealistic weight {weight}g")
            return False
    
    return True


def _validate_simple_food_data(data: Dict) -> bool:
    """
    Упрощённая валидация для простого формата.
    """
    if not isinstance(data, dict):
        return False
    
    dish = data.get('dish_name', '')
    ingredients = data.get('ingredients', [])
    
    if not dish or len(dish) < 3:
        return False
    
    if not isinstance(ingredients, list) or len(ingredients) < 1:
        return False
    
    return True


# ========== ОСНОВНЫЕ ФУНКЦИИ ==========

async def identify_food_multimodel(
    image_bytes: bytes,
    prompt: str = None,
    max_tokens: int = 500,
    temperature: float = 0.0
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Пробует несколько vision-моделей для распознавания еды.
    Возвращает (data, model_name) или (None, None) при неудаче.
    
    Args:
        image_bytes: Байты изображения
        prompt: Промпт для AI (по умолчанию FOOD_RECOGNITION_PROMPT)
        max_tokens: Максимальное количество токенов в ответе
        temperature: Температура генерации (0.0 = детерминировано)
    
    Returns:
        Кортеж (распознанные данные, название модели) или (None, None)
    """
    if not BASE_URL:
        logger.error("❌ Cloudflare BASE_URL not configured")
        return None, None
    
    # Подготовка изображения
    optimized = _prepare_image(image_bytes)
    image_array = _bytes_to_array(optimized)
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Используем улучшенный промпт по умолчанию
    if prompt is None:
        prompt = FOOD_RECOGNITION_PROMPT
    
    logger.info(f"🔍 Starting food recognition with {len(VISION_MODELS)} models")
    
    for model in VISION_MODELS:
        try:
            url = f"{BASE_URL}{model}"
            payload = {
                "image": image_array,
                "prompt": prompt,
                "max_tokens": max_tokens,
            }
            
            # Добавляем temperature только для моделей которые его поддерживают
            if model == "@cf/llava-hf/llava-1.5-7b-hf":
                payload["temperature"] = temperature
            
            logger.info(f"🤖 Trying vision model: {model}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        description = result.get("result", {}).get("description", "").strip()
                        
                        if description:
                            data = _extract_json_from_text(description)
                            
                            # Выбираем валидатор в зависимости от промпта
                            if prompt == FOOD_RECOGNITION_PROMPT:
                                is_valid = _validate_food_data(data) if data else False
                            else:
                                is_valid = _validate_simple_food_data(data) if data else False
                            
                            if data and is_valid:
                                logger.info(f"✅ Model {model} returned valid JSON")
                                logger.debug(f"📊 Data: {data}")
                                return data, model
                            else:
                                logger.warning(f"⚠️ Model {model} returned invalid data: {data}")
                        else:
                            logger.warning(f"⚠️ Model {model} returned empty description")
                    else:
                        error_text = await resp.text()
                        logger.warning(f"⚠️ Model {model} failed with status {resp.status}: {error_text[:200]}")
                        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Model {model} timeout")
        except Exception as e:
            logger.warning(f"❌ Model {model} error: {e}")
            continue
    
    logger.error("❌ All vision models failed to return valid JSON")
    return None, None


async def identify_dish_from_image(image_bytes: bytes) -> Optional[str]:
    """
    Возвращает только название блюда (строку) или None.
    Упрощённая версия для быстрого распознавания.
    """
    data, model = await identify_food_multimodel(
        image_bytes, 
        prompt=SIMPLE_FOOD_PROMPT, 
        max_tokens=100
    )
    
    if data:
        return data.get("dish_name")
    return None


async def analyze_food_image(image_bytes: bytes, prompt: str = None) -> Optional[str]:
    """
    Возвращает текстовое описание (ингредиенты) или None.
    Fallback функция для старого формата.
    """
    if prompt is None:
        prompt = INGREDIENTS_ONLY_PROMPT
    
    data, model = await identify_food_multimodel(
        image_bytes, 
        prompt=prompt, 
        max_tokens=200
    )
    
    if data:
        # Если есть ingredients в новом формате
        if "ingredients" in data:
            if isinstance(data["ingredients"], list):
                return ", ".join(data["ingredients"])
        # Если есть description в старом формате
        if "description" in data:
            return data["description"]
    
    return None


async def identify_food_cascade(image_bytes: bytes) -> Dict:
    """
    Каскадное распознавание: несколько моделей + консенсус.
    Возвращает объединённые результаты.
    
    Returns:
        Словарь с распознанными данными и метаинформацией
    """
    results = []
    
    # 1. LLaVA (лучше для общих объектов)
    result1, model1 = await identify_food_multimodel(
        image_bytes, 
        prompt=FOOD_RECOGNITION_PROMPT,
    )
    if result1:
        results.append(("llava", result1, 0.5))
    
    # 2. UForm (лучше для текста и деталей)
    result2, model2 = await identify_food_multimodel(
        image_bytes,
        prompt=FOOD_RECOGNITION_PROMPT,
    )
    if result2:
        results.append(("uform", result2, 0.3))
    
    # Консенсус
    if len(results) >= 2:
        return _consensus_results(results)
    elif len(results) == 1:
        return {
            "data": results[0][1],
            "model": results[0][0],
            "consensus": False,
            "confidence": results[0][2]
        }
    
    return {"data": None, "model": None, "consensus": False, "confidence": 0}


def _consensus_results(results: List[Tuple]) -> Dict:
    """
    Объединяет результаты нескольких моделей.
    """
    # Берём dish_name по большинству
    dish_names = [r[1].get("dish_name") for r in results if r[1].get("dish_name")]
    main_dish = max(set(dish_names), key=dish_names.count) if dish_names else "Неизвестно"
    
    # Объединяем ингредиенты
    all_ingredients = []
    seen_names = set()
    
    for _, data, weight in results:
        for ing in data.get("ingredients", []):
            ing_name = ing.get("name", "")
            if ing_name and ing_name not in seen_names:
                ing["source_confidence"] = weight
                all_ingredients.append(ing)
                seen_names.add(ing_name)
    
    # Усредняем confidence
    avg_confidence = sum(r[1].get("confidence", 0.5) for r in results) / len(results)
    
    return {
        "data": {
            "dish_name": main_dish,
            "ingredients": all_ingredients,
            "confidence": avg_confidence,
            "consensus": True
        },
        "model": "consensus",
        "consensus": True,
        "confidence": avg_confidence
    }


# ========== ТРАНСКРИБАЦИЯ АУДИО ==========

async def _convert_ogg_to_wav(ogg_bytes: bytes) -> Optional[bytes]:
    """
    Конвертирует OGG в WAV для Whisper.
    """
    try:
        # Проверка размера (макс 20MB)
        if len(ogg_bytes) > 20 * 1024 * 1024:
            logger.warning("⚠️ Audio file too large (>20MB)")
            return None
        
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f_in:
            f_in.write(ogg_bytes)
            in_path = f_in.name
        
        out_path = in_path.replace('.ogg', '.wav')
        
        try:
            # Конвертация через ffmpeg
            cmd = [
                'ffmpeg', 
                '-i', in_path, 
                '-ar', '16000', 
                '-ac', '1', 
                '-acodec', 'pcm_s16le', 
                '-y', 
                out_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode != 0:
                logger.error("❌ FFmpeg conversion failed")
                return None
            
            with open(out_path, 'rb') as f:
                return f.read()
                
        finally:
            # Очистка временных файлов
            try:
                os.unlink(in_path)
                if os.path.exists(out_path):
                    os.unlink(out_path)
            except:
                pass
                
    except Exception as e:
        logger.exception(f"❌ Conversion error: {e}")
        return None


async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """
    Распознавание голоса через Cloudflare Whisper.
    
    Args:
        audio_bytes: Байты аудио (OGG формат из Telegram)
        language: Язык распознавания (по умолчанию русский)
    
    Returns:
        Распознанный текст или None при ошибке
    """
    if not BASE_URL:
        logger.error("❌ Cloudflare BASE_URL not configured")
        return None
    
    try:
        # Конвертация OGG → WAV
        wav_bytes = await _convert_ogg_to_wav(audio_bytes)
        if not wav_bytes:
            logger.error("❌ Audio conversion failed")
            return None
        
        audio_array = list(wav_bytes)
        
        payload = {
            "audio": audio_array,
            "language": language
        }
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        for model in WHISPER_MODELS:
            try:
                url = f"{BASE_URL}{model}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "").strip()
                            
                            if text:
                                logger.info(f"✅ Transcription successful: {text[:50]}...")
                                return text
                            
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Model {model} timeout")
            except Exception as e:
                logger.warning(f"❌ Model {model} error: {e}")
                continue
        
        logger.error("❌ All whisper models failed")
        return None
        
    except Exception as e:
        logger.exception(f"❌ Transcription error: {e}")
        return None


# ========== БЫСТРЫЕ УТИЛИТЫ ==========

async def get_food_recognition_summary(image_bytes: bytes) -> Dict:
    """
    Быстрое получение сводки по распознанной еде.
    Удобно для превью перед полным анализом.
    
    Returns:
        Словарь с краткой информацией о блюде
    """
    data, model = await identify_food_multimodel(
        image_bytes,
        prompt=SIMPLE_FOOD_PROMPT,
        max_tokens=150
    )
    
    if not data:
        return {
            "success": False,
            "dish_name": None,
            "ingredients_count": 0,
            "model": None
        }
    
    ingredients = data.get("ingredients", [])
    
    return {
        "success": True,
        "dish_name": data.get("dish_name"),
        "ingredients_count": len(ingredients),
        "ingredients": ingredients[:5],  # Первые 5 ингредиентов
        "model": model,
        "confidence": data.get("confidence", 0.5)
    }


async def batch_recognize_foods(image_bytes_list: List[bytes]) -> List[Dict]:
    """
    Пакетное распознавание нескольких изображений.
    Используется для обработки очереди фото.
    
    Args:
        image_bytes_list: Список байтов изображений
    
    Returns:
        Список результатов распознавания
    """
    results = []
    
    for i, image_bytes in enumerate(image_bytes_list):
        logger.info(f"📸 Processing image {i+1}/{len(image_bytes_list)}")
        
        data, model = await identify_food_multimodel(image_bytes)
        
        results.append({
            "index": i,
            "success": data is not None,
            "data": data,
            "model": model
        })
        
        # Небольшая задержка чтобы не превысить лимиты API
        if i < len(image_bytes_list) - 1:
            await asyncio.sleep(0.5)
    
    return results
