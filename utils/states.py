"""
Состояния FSM для различных сценариев.
"""
from aiogram.fsm.state import State, StatesGroup

class FoodStates(StatesGroup):
    selecting_food = State()
    entering_weight = State()
    manual_food_name = State()
    editing_weight = State()
    adding_name = State()
    adding_weight = State()

class WaterStates(StatesGroup):
    entering_amount = State()
    confirming = State()

class ActivityStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_duration = State()
    confirming = State()

class StepsStates(StatesGroup):
    waiting_for_steps = State()

class ShoppingStates(StatesGroup):
    adding_item = State()

class ReminderStates(StatesGroup):
    choosing_type = State()
    entering_title = State()
    entering_time = State()
    choosing_days = State()
    confirming = State()

class AIAssistantStates(StatesGroup):
    waiting_for_question = State()

class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()
    activity = State()
    goal = State()
    city = State()
