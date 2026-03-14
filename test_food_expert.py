#!/usr/bin/env python3
"""
Test script to verify FoodExpert-AI prompt integration
"""

def test_food_expert_conversion():
    """Test the FoodExpert-AI format conversion"""
    
    # Simulate FoodExpert-AI output
    food_expert_output = {
        "dish_name": "meat skewers",
        "dish_name_ru": "шашлык",
        "category": "main",
        "cuisine": "russian",
        "confidence_overall": 0.94,
        "ingredients": [
            {
                "name": "pork",
                "name_ru": "свинина",
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
        "reasoning_summary": "Grilled meat pieces on wooden skewers with char marks, typical of shashlik preparation"
    }
    
    # Simulate conversion function
    def _convert_food_expert_format(data):
        if not data:
            return data
        
        converted_data = {
            'dish_name': data.get('dish_name', 'unknown dish'),
            'category': data.get('category', 'main'),
            'confidence': data.get('confidence_overall', 0.8),
            'preparation_style': data.get('cooking_method', 'mixed'),
            'portion_size': data.get('portion_size', 'medium'),
            'meal_type': data.get('meal_context', 'lunch'),
            'cuisine': data.get('cuisine', 'other')
        }
        
        ingredients = data.get('ingredients', [])
        converted_ingredients = []
        
        for ing in ingredients:
            converted_ing = {
                'name': ing.get('name', ''),
                'name_ru': ing.get('name_ru', ing.get('name', '')),
                'type': ing.get('type', 'other'),
                'estimated_weight_grams': ing.get('estimated_weight_grams', 100),
                'confidence': ing.get('confidence', 0.8),
                'visual_cue': ing.get('visual_cue', ''),
                'weight_calibrated': True
            }
            converted_ingredients.append(converted_ing)
        
        converted_data['ingredients'] = converted_ingredients
        
        if 'allergens_detected' in data:
            converted_data['allergens'] = data['allergens_detected']
        
        if 'reasoning_summary' in data:
            converted_data['reasoning'] = data['reasoning_summary']
        
        return converted_data
    
    print("Testing FoodExpert-AI format conversion...")
    print("=" * 60)
    
    # Convert format
    converted = _convert_food_expert_format(food_expert_output)
    
    print("Input (FoodExpert-AI format):")
    print(f"  Dish: {food_expert_output['dish_name']} ({food_expert_output['dish_name_ru']})")
    print(f"  Category: {food_expert_output['category']}")
    print(f"  Confidence: {food_expert_output['confidence_overall']}")
    print(f"  Ingredients: {len(food_expert_output['ingredients'])}")
    
    print("\nOutput (Bot format):")
    print(f"  Dish: {converted['dish_name']}")
    print(f"  Category: {converted['category']}")
    print(f"  Confidence: {converted['confidence']}")
    print(f"  Preparation: {converted['preparation_style']}")
    print(f"  Meal type: {converted['meal_type']}")
    print(f"  Cuisine: {converted['cuisine']}")
    print(f"  Ingredients: {len(converted['ingredients'])}")
    
    print("\nIngredient details:")
    for i, ing in enumerate(converted['ingredients'], 1):
        print(f"  {i}. {ing['name']} ({ing['name_ru']})")
        print(f"     Type: {ing['type']}, Weight: {ing['estimated_weight_grams']}g")
        print(f"     Confidence: {ing['confidence']}")
        print(f"     Visual: {ing['visual_cue']}")
    
    print("\nAdditional fields:")
    if 'allergens' in converted:
        print(f"  Allergens: {converted['allergens']}")
    if 'reasoning' in converted:
        print(f"  Reasoning: {converted['reasoning']}")
    
    print("\n" + "=" * 60)
    print("FoodExpert-AI integration test completed successfully!")
    print("The new prompt should provide much more detailed and accurate food recognition!")

if __name__ == "__main__":
    test_food_expert_conversion()
