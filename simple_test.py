#!/usr/bin/env python3
"""
Simple test to verify the skewer identification logic
"""

def test_skewer_logic():
    """Test the skewer identification logic directly"""
    
    # Simulate the key logic from _fix_common_recognition_errors
    def check_skewer_fix(dish_name, ingredient_names):
        skewer_keywords = ['skewer', 'kebab', 'shashlik', 'шашлик', 'шампур', 'шпажка', 'stick']
        meat_keywords = ['beef', 'pork', 'chicken', 'lamb', 'meat', 'говядина', 'свинина', 'курица', 'баранина', 'мясо']
        
        # Check for skewer identification
        if (any(skewer in dish_name.lower() for skewer in skewer_keywords) or 
            any(skewer in ' '.join(ingredient_names).lower() for skewer in skewer_keywords)) and \
           any(meat in ingredient_names for meat in meat_keywords):
            return 'шашлик', 'meat', 'grilled'
        
        # Check for salmon with bread correction
        if ('salmon' in dish_name.lower() or 'лосось' in dish_name.lower()) and \
           ('bread' in dish_name.lower() or 'хлеб' in dish_name.lower()):
            skewer_indicators = ['grilled', 'stick', 'skewer', 'kebab', 'шампур', 'шашлик']
            if any(indicator in dish_name.lower() for indicator in skewer_indicators) or \
               any(indicator in ' '.join(ingredient_names).lower() for indicator in skewer_indicators):
                return 'шашлик', 'meat', 'grilled'
        
        return dish_name, 'unknown', 'unknown'
    
    print("Testing skewer identification logic...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            'name': 'salmon with bread',
            'ingredients': ['salmon', 'bread'],
            'expected': 'salmon with bread'  # Should NOT change - no skewer indicators
        },
        {
            'name': 'grilled meat skewers', 
            'ingredients': ['beef', 'stick'],
            'expected': 'шашлик'  # Should change to шашлик
        },
        {
            'name': 'лосось с хлебом',
            'ingredients': ['говядина', 'шампур'],
            'expected': 'шашлик'  # Should change to шашлик
        },
        {
            'name': 'шашлик из курицы',
            'ingredients': ['курица', 'шашлик'],
            'expected': 'шашлик'  # Should remain шашлик
        },
        {
            'name': 'grilled salmon',
            'ingredients': ['salmon'],
            'expected': 'grilled salmon'  # Should NOT change - it's actually fish
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        result_name, result_category, result_style = check_skewer_fix(
            test['name'], 
            test['ingredients']
        )
        
        status = "PASS" if result_name == test['expected'] else "FAIL"
        print(f"\nTest {i}: {status}")
        print(f"  Input: {test['name']} + {test['ingredients']}")
        print(f"  Expected: {test['expected']}")
        print(f"  Got: {result_name}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_skewer_logic()
