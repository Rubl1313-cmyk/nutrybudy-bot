#!/usr/bin/env python3
"""
Test script to verify logging functionality
"""

import logging
import json

# Setup logging to see the output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_recognition.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def test_logging_format():
    """Test the logging format we added to food recognition"""
    
    # Simulate AI response data
    ai_response = {
        "dish_name": "beef skewers",
        "dish_name_ru": "шашлык из говядины",
        "category": "skewers",
        "cuisine": "russian",
        "confidence_overall": 0.94,
        "ingredients": [
            {
                "name": "beef",
                "name_ru": "говядина",
                "type": "protein",
                "estimated_weight_grams": 200,
                "confidence": 0.91,
                "visual_cue": "charred exterior, juicy interior, threaded on wooden skewers"
            },
            {
                "name": "onion",
                "name_ru": "лук",
                "type": "vegetable",
                "estimated_weight_grams": 30,
                "confidence": 0.75,
                "visual_cue": "caramelized pieces between meat"
            }
        ],
        "cooking_method": "grilled",
        "portion_size": "medium",
        "meal_context": "dinner",
        "allergens_detected": [],
        "reasoning_summary": "Grilled meat pieces on wooden skewers with char marks, typical of shashlik preparation",
        "visual_cues": "cylindrical meat pieces threaded on wooden sticks, charred exterior, grill marks"
    }
    
    # Test the logging format
    print("Testing AI Recognition Logging...")
    print("=" * 80)
    
    # Simulate the logging from the recognition function
    logger.info("=" * 80)
    logger.info("🤖 AI RECOGNITION RESULTS")
    logger.info("=" * 80)
    logger.info(f"📸 Model used: @cf/llava-hf/llava-1.5-7b-hf")
    logger.info(f"📊 Raw AI response type: {type(ai_response)}")
    
    # Log full AI response
    logger.info("📋 Full AI Response:")
    logger.info(json.dumps(ai_response, indent=2, ensure_ascii=False))
    
    # Log key fields
    dish_name = ai_response.get('dish_name', 'unknown')
    dish_name_ru = ai_response.get('dish_name_ru', 'unknown')
    category = ai_response.get('category', 'unknown')
    confidence = ai_response.get('confidence_overall', 0)
    cooking_method = ai_response.get('cooking_method', 'unknown')
    portion_size = ai_response.get('portion_size', 'unknown')
    cuisine = ai_response.get('cuisine', 'unknown')
    
    logger.info("🎯 KEY FIELDS FROM AI:")
    logger.info(f"   Dish Name: {dish_name}")
    logger.info(f"   Dish Name RU: {dish_name_ru}")
    logger.info(f"   Category: {category}")
    logger.info(f"   Confidence: {confidence}")
    logger.info(f"   Cooking Method: {cooking_method}")
    logger.info(f"   Portion Size: {portion_size}")
    logger.info(f"   Cuisine: {cuisine}")
    
    # Log ingredients
    ingredients = ai_response.get('ingredients', [])
    if ingredients:
        logger.info(f"🥘 Ingredients ({len(ingredients)} found):")
        for i, ing in enumerate(ingredients, 1):
            name = ing.get('name', 'unknown')
            name_ru = ing.get('name_ru', 'unknown')
            ing_type = ing.get('type', 'unknown')
            weight = ing.get('estimated_weight_grams', 0)
            conf = ing.get('confidence', 0)
            visual = ing.get('visual_cue', 'no visual cue')
            
            logger.info(f"   {i}. {name} ({name_ru})")
            logger.info(f"      Type: {ing_type}, Weight: {weight}g, Confidence: {conf}")
            logger.info(f"      Visual: {visual}")
    else:
        logger.warning("⚠️ No ingredients found in AI response!")
    
    # Log additional fields
    allergens = ai_response.get('allergens_detected', [])
    if allergens:
        logger.info(f"🚨 Allergens detected: {allergens}")
    
    reasoning = ai_response.get('reasoning_summary', '')
    if reasoning:
        logger.info(f"🧠 AI Reasoning: {reasoning}")
    
    visual_cues = ai_response.get('visual_cues', '')
    if visual_cues:
        logger.info(f"👁️ Visual Cues: {visual_cues}")
    
    logger.info("=" * 80)
    logger.info("🔄 STARTING POST-PROCESSING")
    logger.info("=" * 80)
    
    # Simulate post-processing
    logger.info("🔄 Converting FoodExpert-AI format to bot format...")
    logger.info("✅ Format conversion completed")
    logger.info(f"📊 Converted dish name: {dish_name}")
    logger.info(f"📊 Converted category: {category}")
    
    logger.info("🔧 Applying post-processing error fixes...")
    original_dish = dish_name
    final_dish = dish_name  # No change in this case
    
    if original_dish != final_dish:
        logger.info(f"🔧 DISH NAME CHANGED: '{original_dish}' → '{final_dish}'")
    else:
        logger.info(f"✅ Dish name unchanged: '{final_dish}'")
    
    logger.info("=" * 80)
    logger.info("🎉 FINAL RECOGNITION RESULT")
    logger.info("=" * 80)
    logger.info(f"🍽️ Final Dish: {final_dish}")
    logger.info(f"📂 Final Category: {category}")
    logger.info(f"📈 Final Confidence: {confidence}")
    logger.info(f"🍳 Final Cooking Method: {cooking_method}")
    logger.info("=" * 80)
    
    print("\nLogging test completed!")
    print("Check the console output and 'test_recognition.log' file for detailed logs.")
    print("=" * 80)

if __name__ == "__main__":
    test_logging_format()
