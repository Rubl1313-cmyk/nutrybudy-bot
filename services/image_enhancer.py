# services/image_enhancer.py
"""
Улучшение изображений для лучшего распознавания еды.
✅ Контраст, яркость, резкость
✅ Уменьшение шума
✅ Мульти-скейл для каскадного распознавания
"""

import logging
from PIL import Image, ImageEnhance, ImageFilter
import io
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)


def enhance_food_image(image_bytes: bytes) -> Tuple[bytes, dict]:
    """
    Улучшает изображение для лучшего распознавания еды.
    
    Args:
        image_bytes: Исходные байты изображения
        
    Returns:
        Кортеж (улучшенные байты, метаданные улучшений)
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        metadata = {
            'original_size': img.size,
            'enhancements_applied': []
        }
        
        # Конвертация в RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
            metadata['enhancements_applied'].append('rgb_convert')
        
        # Автоматическая коррекция контраста (+20%)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        metadata['enhancements_applied'].append('contrast_1.2')
        
        # Автоматическая коррекция яркости (+10%)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        metadata['enhancements_applied'].append('brightness_1.1')
        
        # Увеличение резкости (+30%)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)
        metadata['enhancements_applied'].append('sharpness_1.3')
        
        # Уменьшение шума (для тёмных фото)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        metadata['enhancements_applied'].append('denoise')
        
        # Оптимизация размера
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        metadata['final_size'] = img.size
        
        # Сохранение в JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=90, optimize=True)
        
        logger.info(f"✅ Image enhanced: {metadata}")
        return output.getvalue(), metadata
        
    except Exception as e:
        logger.error(f"❌ Image enhancement failed: {e}")
        return image_bytes, {'error': str(e)}


def create_multi_scale_images(image_bytes: bytes) -> List[Dict]:
    """
    Создаёт несколько версий изображения разных размеров для cascade recognition.
    
    Args:
        image_bytes: Исходные байты изображения
        
    Returns:
        Список словарей с версиями изображений
    """
    scales = [
        (1024, 1024, 'large'),
        (512, 512, 'medium'),
        (256, 256, 'small')
    ]
    
    results = []
    
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        for width, height, scale_name in scales:
            img_copy = img.copy()
            img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            img_copy.save(output, format='JPEG', quality=85)
            
            results.append({
                'scale': scale_name,
                'bytes': output.getvalue(),
                'size': (width, height)
            })
        
        logger.info(f"✅ Created {len(results)} scaled images")
        return results
        
    except Exception as e:
        logger.error(f"❌ Multi-scale creation failed: {e}")
        # Возвращаем хотя бы оригинал
        return [{
            'scale': 'original',
            'bytes': image_bytes,
            'size': 'unknown'
        }]


def detect_image_quality(image_bytes: bytes) -> Dict:
    """
    Оценивает качество изображения для принятия решения об улучшении.
    
    Args:
        image_bytes: Байты изображения
        
    Returns:
        Словарь с метриками качества
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Конвертируем в grayscale для анализа
        gray = img.convert('L')
        
        # Вычисляем гистограмму
        histogram = gray.histogram()
        
        # Оценка контраста (разброс значений)
        min_val = next((i for i, v in enumerate(histogram) if v > 0), 0)
        max_val = next((i for i, v in reversed(list(enumerate(histogram))) if v > 0), 255)
        contrast_range = max_val - min_val
        
        # Оценка яркости (среднее значение)
        total_pixels = img.width * img.height
        brightness = sum(i * v for i, v in enumerate(histogram)) / total_pixels
        
        # Оценка резкости (через лапласиан)
        img_rgb = img.convert('RGB') if img.mode != 'RGB' else img
        img_filtered = img_rgb.filter(ImageFilter.FIND_EDGES)
        sharpness = sum(img_filtered.convert('L').histogram()) / total_pixels
        
        quality = {
            'contrast_range': contrast_range,
            'brightness': brightness,
            'sharpness': sharpness,
            'size': img.size,
            'needs_enhancement': contrast_range < 150 or brightness < 80 or brightness > 200
        }
        
        logger.info(f"📊 Image quality: {quality}")
        return quality
        
    except Exception as e:
        logger.error(f"❌ Quality detection failed: {e}")
        return {
            'needs_enhancement': True,
            'error': str(e)
        }
