from aiogram.fsm.state import State, StatesGroup


class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()
    activity = State()
    goal = State()
    city = State()


class FoodStates(StatesGroup):
    choosing_meal_type = State()
    searching_food = State()
    selecting_food = State()
    entering_weight = State()
    manual_food_name = State()
    confirming = State()


class WaterStates(StatesGroup):
    entering_amount = State()
    confirming = State()


class ShoppingStates(StatesGroup):
    creating_list = State()
    renaming_list = State()
    adding_item = State()
    editing_item = State()


class ReminderStates(StatesGroup):
    choosing_type = State()
    entering_title = State()
    entering_time = State()
    choosing_days = State()


class ActivityStates(StatesGroup):
    choosing_source = State()
    manual_type = State()
    manual_duration = State()
    manual_distance = State()
    manual_calories = State()
    manual_steps = State()
    waiting_gpx = State()


class WeightStates(StatesGroup):
    entering_weight = State()
