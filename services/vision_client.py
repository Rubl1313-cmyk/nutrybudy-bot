"""
Vision client for food recognition using Cloudflare AI's llama-3.2-11b-vision-instruct
via existing identify_food_cascade function.
"""
import logging
from typing import Optional
from services.cloudflare_ai import identify_food_cascade

logger = logging.getLogger(__name__)

async def recognize_food_vision(image_bytes: bytes, prompt: str = "Describe the food in this image.") -> Optional[str]:
    """
    Use vision model to describe food in image.

    Args:
        image_bytes: raw image data
        prompt: prompt for the vision model

    Returns:
        Food description string or None if failed
    """
    try:
        result = await identify_food_cascade(image_bytes)
        if not result or not result.get('success'):
            logger.error(f"Vision model failed: {result}")
            return None
        
        # The result['data'] contains the description from the model
        # Based on media_handlers processing, the data includes dish_name_ru etc.
        data = result.get('data', {})
        # Try to get a readable description
        description = data.get('dish_name_ru') or data.get('name') or str(data)
        if not description:
            # Fallback: construct from ingredients if available
            ingredients = data.get('ingredients', [])
            if ingredients:
                desc_parts = [ing.get('name', '') for ing in ingredients if ing.get('name')]
                description = ", ".join(desc_parts) if desc_parts else "Food item"
            else:
                description = "Food item (unable to describe)"
        
        logger.info(f"Vision recognition result: {description}")
        return description
        
    except Exception as e:
        logger.exception("Error in vision recognition")
        return None