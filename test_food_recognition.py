#!/usr/bin/env python3
"""
Test script to verify the improved food recognition fixes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.cloudflare_ai import _fix_common_recognition_errors

def test_skewer_fix():
    """Test the skewer identification fix"""
    
    # Test case 1: Obvious salmon with bread misidentification
    test_case_1 = {
        'dish_name': 'salmon with bread',
        'category': 'fish',
        'ingredients': [
            {'name': 'salmon', 'type': 'protein', 'estimated_weight_grams': 150, 'confidence': 0.9},
            {'name': 'bread', 'type': 'carb', 'estimated_weight_grams': 50, 'confidence': 0.8}
        ],
        'preparation_style': 'grilled'
    }
    
    # Test case 2: Skewer detection
    test_case_2 = {
        'dish_name': 'grilled meat skewers',
        'category': 'meat',
        'ingredients': [
            {'name': 'beef', 'type': 'protein', 'estimated_weight_grams': 200, 'confidence': 0.9},
            {'name': 'stick', 'type': 'other', 'estimated_weight_grams': 10, 'confidence': 0.7}
        ],
        'preparation_style': 'grilled'
    }
    
    # Test case 3: Russian шашлик
    test_case_3 = {
        'dish_name': 'лосось с хлебом',  # salmon with bread in Russian
        'category': 'fish',
        'ingredients': [
            {'name': 'говядина', 'type': 'protein', 'estimated_weight_grams': 180, 'confidence': 0.9},
            {'name': 'шампур', 'type': 'other', 'estimated_weight_grams': 5, 'confidence': 0.8}
        ],
        'preparation_style': 'grilled'
    }
    
    print("Testing improved food recognition fixes...")
    print("=" * 50)
    
    # Test case 1
    print("\nTest Case 1: 'salmon with bread' (should stay as is - no skewer indicators)")
    result_1 = _fix_common_recognition_errors(test_case_1.copy())
    print(f"Result: {result_1['dish_name']} (category: {result_1.get('category', 'unknown')})")
    
    # Test case 2  
    print("\nTest Case 2: 'grilled meat skewers' (should be corrected to шашлик)")
    result_2 = _fix_common_recognition_errors(test_case_2.copy())
    print(f"Result: {result_2['dish_name']} (category: {result_2.get('category', 'unknown')})")
    
    # Test case 3
    print("\nTest Case 3: 'лосось с хлебом' with skewer indicators (should be corrected to шашлик)")
    result_3 = _fix_common_recognition_errors(test_case_3.copy())
    print(f"Result: {result_3['dish_name']} (category: {result_3.get('category', 'unknown')})")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_skewer_fix()
