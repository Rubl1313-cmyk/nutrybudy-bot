"""
Cloudflare Workers AI Integration for NutriBuddy
✅ Улучшено: более точные промпты для распознавания еды
✅ Добавлено: валидация и пост-обработка результатов
"""
import aiohttp
import os
import logging
import asyncio
import json
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.error("❌ Cloudflare credentials not set")
    BASE_URL = None
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# Модели (порядок важен: сначала LLaVA, потом UForm)
VISION_MODELS = [
    "@cf/llava-hf/llava-1.5-7b-hf",
    "@cf/unum/uform-gen2-qwen-500m",
]

WHISPER_MODELS = [
    "@cf/openai/whisper",
    "@cf/openai/whisper-large-v3-turbo",
]

def _bytes_to_array(image_bytes: bytes) -> list:
    """Конвертирует байты изображения в массив для API."""
    return list(image_bytes)

def _extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Извлекает JSON из текста, удаляя возможные экранирования.
    ✅ Улучшено: обработка различных форматов JSON
    """
    if not text:
        return None
    
    # Пробуем найти JSON в тексте
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1 or end <= start:
        # Пробуем найти JSON в markdown блоке
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
            start = 0
            end = len(text) - 1
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
            start = 0
            end = len(text) - 1
    
    if start == -1 or end == -1:
        return None
    
    json_str = text[start:end+1]
    
    # Удаляем экранирование
    json_str = json_str.replace('\\_', '_').replace('\\"', '"')
    json_str = json_str.replace('\\n', ' ').replace('\\t', ' ')
    
    try:
        data = json.loads(json_str)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}. Text: {text[:200]}...")
        return None

def _validate_food_data(data: Dict) -> bool:
    """
    Проверяет, что распознанные данные выглядят правдоподобно.
    ✅ Добавлено: расширенная валидация
    """
    if not isinstance(data, dict):
        return False
    
    dish = data.get('dish_name', '')
    ingredients = data.get('ingredients', [])
    
    # Проверка названия блюда
    if not dish or len(dish) < 3:
        return False
    
    # Проверка ингредиентов
    if not isinstance(ingredients, list):
        return False
    
    if len(ingredients) < 1:
        return False
    
    # Проверка на чрезмерные повторы
    unique_ingredients = set()
    for ing in ingredients:
        if isinstance(ing, str):
            unique_ingredients.add(ing.lower().strip())
        elif isinstance(ing, dict):
            ing_name = ing.get('name', '')
            if ing_name:
                unique_ingredients.add(ing_name.lower().strip())
    
    if len(unique_ingredients) < len(ingredients) * 0.5:
        logger.warning(f"Validation failed: too many repeats in ingredients: {ingredients}")
        return False
    
    # Проверка на бессмысленные ингредиенты
    meaningless = ['and', 'the', 'with', 'on', 'in', 'a', 'an', 'to', 'of']
    valid_count = sum(1 for ing in unique_ingredients if ing not in meaningless and len(ing) > 2)
    
    if valid_count < 1:
        logger.warning(f"Validation failed: no valid ingredients")
        return False
    
    return True

async def identify_food_multimodel(
    image_bytes: bytes,
    prompt: str = None,
    max_tokens: int = 500,
    temperature: float = 0.1
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Пробует несколько vision-моделей для распознавания еды.
    Возвращает (data, model_name) или (None, None) при неудаче.
    ✅ Улучшено: более точный промпт по умолчанию
    """
    if not BASE_URL:
        return None, None
    
    image_array = _bytes_to_array(image_bytes)
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # УЛУЧШЕННЫЙ промпт по умолчанию
    if prompt is None:
        prompt = """You are a professional food nutritionist and image recognition expert. Analyze this food image with extreme precision and return structured data.

Return a JSON object with the following structure:
{
    "dish_name": "Specific dish name in English (e.g., 'Grilled chicken with vegetables', 'Caesar salad', 'Pasta carbonara')",
    "ingredients": [
        "ingredient1",
        "ingredient2",
        "ingredient3"
    ],
    "confidence": 0.95,
    "meal_type": "breakfast|lunch|dinner|snack",
    "cooking_method": "grilled|fried|boiled|baked|steamed|raw",
    "estimated_portion": "small|medium|large"
}

DETAILED RULES:
1. DISH NAME: Be very specific. Don't say "meat dish", say "Grilled chicken breast with herbs"
2. INGREDIENTS: List EVERY visible component:
   - Main protein (chicken, beef, fish, tofu, etc.)
   - Vegetables (tomatoes, cucumbers, lettuce, etc.)
   - Carbohydrates (rice, pasta, bread, potatoes)
   - Sauces and dressings (mayonnaise, ketchup, olive oil)
   - Garnishes and herbs (parsley, basil, lemon)
3. COOKING METHOD: Identify from visual cues:
   - Grill marks = grilled
   - Golden brown crust = fried or baked
   - Steaming = steamed
   - Raw appearance = raw/salad
4. PORTION SIZE: Estimate based on typical plate size
5. MEAL TYPE: Infer from dish type and portion

EXAMPLES:
Image: Grilled salmon with vegetables
Output: {
    "dish_name": "Grilled salmon with roasted vegetables",
    "ingredients": ["salmon fillet", "broccoli", "bell peppers", "zucchini", "olive oil", "lemon", "herbs"],
    "confidence": 0.92,
    "meal_type": "dinner",
    "cooking_method": "grilled",
    "estimated_portion": "medium"
}

Image: Caesar salad
Output: {
    "dish_name": "Caesar salad with chicken",
    "ingredients": ["romaine lettuce", "grilled chicken breast", "parmesan cheese", "croutons", "caesar dressing", "lemon"],
    "confidence": 0.95,
    "meal_type": "lunch",
    "cooking_method": "grilled",
    "estimated_portion": "medium"
}

Return ONLY valid JSON, no additional text or explanations."""
    
    for model in VISION_MODELS:
        try:
            url = f"{BASE_URL}{model}"
            payload = {
                "image": image_array,
                "prompt": prompt,
                "max_tokens": max_tokens,
            }
            
            # Добавляем параметры, специфичные для модели
            if model == "@cf/llava-hf/llava-1.5-7b-hf":
                payload["temperature"] = temperature
            # UForm не поддерживает temperature
            
            logger.info(f"🤖 Trying vision model: {model}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        description = result.get("result", {}).get("description", "").strip()
                        
                        if description:
                            logger.info(f"📝 Raw AI response: {description[:300]}...")
                            
                            data = _extract_json_from_text(description)
                            
                            if data and _validate_food_data(data):
                                logger.info(f"✅ Model {model} returned valid and plausible JSON")
                                return data, model
                            else:
                                logger.warning(f"⚠️ Model {model} returned invalid or implausible data: {data}")
                        else:
                            logger.warning(f"⚠️ Model {model} returned empty description")
                    else:
                        error_text = await resp.text()
                        logger.warning(f"❌ Model {model} failed with status {resp.status}: {error_text[:200]}")
                        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Model {model} timeout after 60 seconds")
            continue
        except Exception as e:
            logger.warning(f"❌ Model {model} error: {e}")
            continue
    
    logger.error("❌ All vision models failed to return valid JSON")
    return None, None

# Для обратной совместимости оставляем старые функции
async def identify_dish_from_image(image_bytes: bytes) -> Optional[str]:
    """Возвращает только название блюда (строку) или None."""
    data, _ = await identify_food_multimodel(image_bytes, max_tokens=50)
    if data:
        return data.get("dish_name")
    return None

async def analyze_food_image(image_bytes: bytes, prompt: str = None) -> Optional[str]:
    """Возвращает текстовое описание (ингредиенты) или None."""
    if prompt is None:
        prompt = "List all food items visible in this image. Be specific. Return as a comma-separated list."
    
    data, _ = await identify_food_multimodel(image_bytes, prompt=prompt, max_tokens=150)
    if data and "ingredients" in data:
        return ", ".join(data["ingredients"])
    return None

# Транскрибация (без изменений)
async def _convert_ogg_to_wav(ogg_bytes: bytes) -> Optional[bytes]:
    """Конвертирует OGG в WAV."""
    try:
        if len(ogg_bytes) > 20 * 1024 * 1024:
            return None
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f_in:
            f_in.write(ogg_bytes)
            in_path = f_in.name
        
        out_path = in_path.replace('.ogg', '.wav')
        
        try:
            cmd = ['ffmpeg', '-i', in_path, '-ar', '16000', '-ac', '1', '-acodec', 'pcm_s16le', '-y', out_path]
            process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await process.communicate()
            
            if process.returncode != 0:
                return None
            
            with open(out_path, 'rb') as f:
                return f.read()
        finally:
            try:
                os.unlink(in_path)
                if os.path.exists(out_path):
                    os.unlink(out_path)
            except:
                pass
    except Exception as e:
        logger.exception(f"Conversion error: {e}")
        return None

async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    """Распознавание голоса через Cloudflare Whisper."""
    if not BASE_URL:
        return None
    
    try:
        wav_bytes = await _convert_ogg_to_wav(audio_bytes)
        if not wav_bytes:
            return None
        
        audio_array = list(wav_bytes)
        payload = {"audio": audio_array, "language": language}
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"}
        
        for model in WHISPER_MODELS:
            try:
                url = f"{BASE_URL}{model}"
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "").strip()
                            if text:
                                return text
            except Exception:
                continue
        
        return None
    except Exception as e:
        logger.exception(f"Transcription error: {e}")
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
