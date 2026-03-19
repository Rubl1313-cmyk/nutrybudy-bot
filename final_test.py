import asyncio
from database.db import engine, Base
from database.models import User, WeightEntry, FoodEntry, DrinkEntry, ActivityEntry
from sqlalchemy import inspect

async def final_test():
    """Финальная проверка всей системы"""
    
    print("=== FINAL SYSTEM TEST ===")
    
    # 1. Проверяем таблицы
    async with engine.connect() as conn:
        db_tables = await conn.run_sync(lambda conn: inspect(conn).get_table_names())
        model_tables = Base.metadata.tables.keys()
        
        missing_tables = set(model_tables) - set(db_tables)
        
        if missing_tables:
            print(f"ERROR: Missing tables: {missing_tables}")
            return False
        else:
            print("OK: All tables exist")
        
        # 2. Проверяем колонки weight_entries
        weight_columns = await conn.run_sync(lambda conn: inspect(conn).get_columns('weight_entries'))
        weight_column_names = [col['name'] for col in weight_columns]
        
        expected_weight_columns = ['id', 'user_id', 'weight', 'body_fat', 'muscle_mass', 'body_water', 'created_at']
        missing_weight_columns = set(expected_weight_columns) - set(weight_column_names)
        
        if missing_weight_columns:
            print(f"ERROR: Missing weight columns: {missing_weight_columns}")
            return False
        else:
            print("OK: All weight columns exist")
        
        # 3. Проверяем колонки food_entries
        food_columns = await conn.run_sync(lambda conn: inspect(conn).get_columns('food_entries'))
        food_column_names = [col['name'] for col in food_columns]
        
        expected_food_columns = ['id', 'user_id', 'food_name', 'calories', 'protein', 'fat', 'carbs', 'fiber', 'sugar', 'sodium', 'meal_type', 'quantity', 'unit', 'created_at']
        missing_food_columns = set(expected_food_columns) - set(food_column_names)
        
        if missing_food_columns:
            print(f"ERROR: Missing food columns: {missing_food_columns}")
            return False
        else:
            print("OK: All food columns exist")
        
        # 4. Проверяем колонки drink_entries
        drink_columns = await conn.run_sync(lambda conn: inspect(conn).get_columns('drink_entries'))
        drink_column_names = [col['name'] for col in drink_columns]
        
        expected_drink_columns = ['id', 'user_id', 'drink_name', 'amount', 'calories', 'sugar', 'caffeine', 'created_at']
        missing_drink_columns = set(expected_drink_columns) - set(drink_column_names)
        
        if missing_drink_columns:
            print(f"ERROR: Missing drink columns: {missing_drink_columns}")
            return False
        else:
            print("OK: All drink columns exist")
    
    print("\n=== ALL TESTS PASSED ===")
    return True

if __name__ == "__main__":
    result = asyncio.run(final_test())
    print(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
