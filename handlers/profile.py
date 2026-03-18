"""
handlers/profile.py
User profile handlers
"""
import logging
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router, types
from sqlalchemy import select

from database.db import get_session
from database.models import User
from keyboards.reply_v2 import get_main_keyboard_v2, get_profile_keyboard
from keyboards.reply import get_gender_keyboard
from keyboards.timezone_keyboard import get_timezone_keyboard, get_timezone_confirm_keyboard
from utils.states import ProfileStates
from utils.timezone_utils import parse_timezone_input, get_timezone_display_name
from utils.localized_commands import create_localized_command_filter

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("set_profile"))
@router.message(create_localized_command_filter("setup_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    """Start profile setup"""
    await state.clear()
    
    await message.answer(
        "👤 <b>Profile Setup</b>\n\n"
        "Let's set up your personal profile for accurate calorie calculation.\n\n"
        "Next code without changes...",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_weight)
    
@router.message(ProfileStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Process weight with safe parsing"""
    from utils.safe_parser import safe_parse_float
    
    weight, error = safe_parse_float(message.text, "weight")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "📊 <b>Examples:</b>\n"
            "• 75.5\n"
            "• 75,5\n"
            "• 75\n"
            "• 75.0 kg\n"
            "• 75.5кг",
            parse_mode="HTML"
        )
        return
    
    if weight < 30 or weight > 300:
        await message.answer(
            "❌ Weight must be between 30 and 300 kg.\n\n"
            "📊 Please enter a realistic weight:",
            parse_mode="HTML"
        )
        return
    
    # Save weight to state
    await state.update_data(weight=weight)
    
    await message.answer(
        f"✅ Weight saved: {weight} kg\n\n"
        "📏 Now enter your height in centimeters:\n\n"
        "📊 <b>Examples:</b>\n"
        "• 175\n"
        "• 175 cm\n"
        "• 175см",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_height)

@router.message(ProfileStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    """Process height with safe parsing"""
    from utils.safe_parser import safe_parse_float
    
    height, error = safe_parse_float(message.text, "height")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "📏 <b>Examples:</b>\n"
            "• 175\n"
            "• 175 cm\n"
            "• 175см",
            parse_mode="HTML"
        )
        return
    
    if height < 100 or height > 250:
        await message.answer(
            "❌ Height must be between 100 and 250 cm.\n\n"
            "📏 Please enter a realistic height:",
            parse_mode="HTML"
        )
        return
    
    # Save height to state
    await state.update_data(height=height)
    
    await message.answer(
        f"✅ Height saved: {height} cm\n\n"
        "🎂 Now enter your age:\n\n"
        "📊 <b>Examples:</b>\n"
        "• 25\n"
        "• 25 years\n"
        "• 25 лет",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_age)

@router.message(ProfileStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Process age with safe parsing"""
    from utils.safe_parser import safe_parse_float
    
    age, error = safe_parse_float(message.text, "age")
    
    if error:
        await message.answer(
            f"❌ {error}\n\n"
            "🎂 <b>Examples:</b>\n"
            "• 25\n"
            "• 25 years\n"
            "• 25 лет",
            parse_mode="HTML"
        )
        return
    
    if age < 10 or age > 120:
        await message.answer(
            "❌ Age must be between 10 and 120 years.\n\n"
            "🎂 Please enter a realistic age:",
            parse_mode="HTML"
        )
        return
    
    # Save age to state
    await state.update_data(age=int(age))
    
    await message.answer(
        f"✅ Age saved: {int(age)} years\n\n"
        "⚧️ Now select your gender:",
        reply_markup=get_gender_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_gender)

@router.message(ProfileStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    """Process gender selection"""
    gender = message.text.lower()
    
    if gender in ["мужской", "male", "м", "m"]:
        gender = "male"
    elif gender in ["женский", "female", "ж", "f"]:
        gender = "female"
    else:
        await message.answer(
            "❌ Please select your gender using the buttons below:",
            reply_markup=get_gender_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Save gender to state
    await state.update_data(gender=gender)
    
    await message.answer(
        f"✅ Gender saved: {gender}\n\n"
        "🎯 Now select your goal:",
        reply_markup=get_goal_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_goal)

@router.message(ProfileStates.waiting_for_goal)
async def process_goal(message: Message, state: FSMContext):
    """Process goal selection"""
    goal = message.text.lower()
    
    if goal in ["похудение", "lose weight", "lose_weight", "похудеть"]:
        goal = "lose_weight"
    elif goal in ["набор массы", "gain weight", "gain_weight", "набрать вес"]:
        goal = "gain_weight"
    elif goal in ["поддержание", "maintenance", "maintain", "поддерживать"]:
        goal = "maintenance"
    else:
        await message.answer(
            "❌ Please select your goal using the buttons below:",
            reply_markup=get_goal_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Save goal to state
    await state.update_data(goal=goal)
    
    await message.answer(
        f"✅ Goal saved: {goal}\n\n"
        "🏃 Now select your activity level:",
        reply_markup=get_activity_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_activity)

@router.message(ProfileStates.waiting_for_activity)
async def process_activity(message: Message, state: FSMContext):
    """Process activity level selection"""
    activity = message.text.lower()
    
    activity_mapping = {
        "минимальная": "sedentary",
        "минимальный": "sedentary",
        "sedentary": "sedentary",
        "легкая": "light",
        "лёгкая": "light",
        "light": "light",
        "умеренная": "moderate",
        "средняя": "moderate",
        "moderate": "moderate",
        "высокая": "active",
        "высокий": "active",
        "active": "active",
        "очень высокая": "very_active",
        "очень высокий": "very_active",
        "very active": "very_active"
    }
    
    if activity not in activity_mapping:
        await message.answer(
            "❌ Please select your activity level using the buttons below:",
            reply_markup=get_activity_keyboard(),
            parse_mode="HTML"
        )
        return
    
    activity_level = activity_mapping[activity]
    
    # Save activity level to state
    await state.update_data(activity_level=activity_level)
    
    await message.answer(
        f"✅ Activity level saved: {activity_level}\n\n"
        "🌍 Now select your timezone:",
        reply_markup=get_timezone_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_timezone)

@router.message(ProfileStates.waiting_for_timezone)
async def process_timezone(message: Message, state: FSMContext):
    """Process timezone selection"""
    timezone_input = message.text.strip()
    
    # Parse timezone
    timezone_offset, timezone_name = parse_timezone_input(timezone_input)
    
    if not timezone_offset:
        await message.answer(
            "❌ Invalid timezone format.\n\n"
            "🌍 Please use one of the formats:\n"
            "• UTC+3\n"
            "• +3\n"
            "• Europe/Moscow\n"
            "• Moscow\n\n"
            "Or select from the buttons below:",
            reply_markup=get_timezone_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Save timezone to state
    await state.update_data(
        timezone_offset=timezone_offset,
        timezone_name=timezone_name
    )
    
    # Show confirmation
    display_name = get_timezone_display_name(timezone_offset, timezone_name)
    
    await message.answer(
        f"✅ Timezone saved: {display_name}\n\n"
        "🏙️ Now enter your city for weather data:",
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.waiting_for_city)

@router.message(ProfileStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    """Process city input"""
    city = message.text.strip()
    
    if not city or len(city) < 2:
        await message.answer(
            "❌ Please enter a valid city name:\n\n"
            "📊 <b>Examples:</b>\n"
            "• Moscow\n"
            "• London\n"
            "• New York\n"
            "• Москва\n"
            "• Лондон",
            parse_mode="HTML"
        )
        return
    
    # Save city to state
    await state.update_data(city=city)
    
    # Get all profile data
    profile_data = await state.get_data()
    
    # Confirm profile setup
    await message.answer(
        f"✅ City saved: {city}\n\n"
        "📋 <b>Profile Summary:</b>\n\n"
        f"⚖️ Weight: {profile_data['weight']} kg\n"
        f"📏 Height: {profile_data['height']} cm\n"
        f"🎂 Age: {profile_data['age']} years\n"
        f"⚧️ Gender: {profile_data['gender']}\n"
        f"🎯 Goal: {profile_data['goal']}\n"
        f"🏃 Activity: {profile_data['activity_level']}\n"
        f"🌍 Timezone: {get_timezone_display_name(profile_data['timezone_offset'], profile_data['timezone_name'])}\n"
        f"🏙️ City: {profile_data['city']}\n\n"
        "🔍 Please confirm:\n\n"
        "✅ Save profile\n"
        "❌ Cancel and start over",
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.confirming)

@router.message(ProfileStates.confirming)
async def process_confirmation(message: Message, state: FSMContext):
    """Process profile confirmation"""
    confirmation = message.text.lower()
    
    if confirmation in ["✅ save profile", "save", "сохранить", "yes", "да"]:
        await save_profile(message, state)
    elif confirmation in ["❌ cancel", "cancel", "отмена", "no", "нет"]:
        await message.answer(
            "❌ Profile setup cancelled.\n\n"
            "🔄 To start over, use /set_profile",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )
        await state.clear()
    else:
        await message.answer(
            "❌ Please select an option:\n\n"
            "✅ Save profile\n"
            "❌ Cancel and start over",
            reply_markup=get_confirm_keyboard(),
            parse_mode="HTML"
        )

async def save_profile(message: Message, state: FSMContext):
    """Save profile to database"""
    try:
        # Get profile data
        profile_data = await state.get_data()
        
        async with get_session() as session:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Update existing user
                user.weight = profile_data['weight']
                user.height = profile_data['height']
                user.age = profile_data['age']
                user.gender = profile_data['gender']
                user.goal = profile_data['goal']
                user.activity_level = profile_data['activity_level']
                user.timezone_offset = profile_data['timezone_offset']
                user.timezone_name = profile_data['timezone_name']
                user.city = profile_data['city']
            else:
                # Create new user
                user = User(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    weight=profile_data['weight'],
                    height=profile_data['height'],
                    age=profile_data['age'],
                    gender=profile_data['gender'],
                    goal=profile_data['goal'],
                    activity_level=profile_data['activity_level'],
                    timezone_offset=profile_data['timezone_offset'],
                    timezone_name=profile_data['timezone_name'],
                    city=profile_data['city']
                )
                session.add(user)
            
            # Calculate initial nutrition goals
            from services.calculator import calculate_calorie_goal, calculate_water_goal
            from utils.activity_normalizer import normalize_activity_level
            
            normalized_activity = normalize_activity_level(profile_data['activity_level'])
            
            nutrition_goals = calculate_calorie_goal(
                weight=profile_data['weight'],
                height=profile_data['height'],
                age=profile_data['age'],
                gender=profile_data['gender'],
                activity_level=normalized_activity,
                goal=profile_data['goal']
            )
            
            # Unpack tuple: (calories, protein_g, fat_g, carbs_g)
            user.daily_calorie_goal, user.daily_protein_goal, user.daily_fat_goal, user.daily_carbs_goal = nutrition_goals
            
            # Calculate water goal
            water_goal = calculate_water_goal(
                weight=profile_data['weight'],
                activity_level=normalized_activity,
                temperature=20.0,  # Default temperature
                goal=profile_data['goal'],
                gender=profile_data['gender']
            )
            user.daily_water_goal = water_goal
            
            await session.commit()
        
        await message.answer(
            "✅ Profile saved successfully!\n\n"
            "🎉 Your personal profile is now ready.\n\n"
            "📊 Daily goals calculated based on your data:\n"
            f"🔥 Calories: {user.daily_calorie_goal:.0f} kcal\n"
            f"🥩 Protein: {user.daily_protein_goal:.1f} g\n"
            f"🧈 Fat: {user.daily_fat_goal:.1f} g\n"
            f"🍞 Carbs: {user.daily_carbs_goal:.1f} g\n"
            f"💧 Water: {user.daily_water_goal:.0f} ml\n\n"
            "🚀 You can now start tracking your nutrition!",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        await message.answer(
            "❌ Error saving profile. Please try again.\n\n"
            "🔄 Use /set_profile to start over.",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )
        await state.clear()

@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    """Show user profile"""
    await state.clear()
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Profile not found.\n\n"
                "📝 Set up your profile with /set_profile",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            return
        
        # Format profile message
        profile_text = f"👤 <b>Your Profile</b>\n\n"
        profile_text += f"⚖️ Weight: {user.weight} kg\n"
        profile_text += f"📏 Height: {user.height} cm\n"
        profile_text += f"🎂 Age: {user.age} years\n"
        profile_text += f"⚧️ Gender: {user.gender}\n"
        profile_text += f"🎯 Goal: {user.goal}\n"
        profile_text += f"🏃 Activity: {user.activity_level}\n"
        profile_text += f"🌍 Timezone: {get_timezone_display_name(user.timezone_offset, user.timezone_name)}\n"
        profile_text += f"🏙️ City: {user.city}\n\n"
        
        profile_text += f"📊 <b>Daily Goals:</b>\n"
        profile_text += f"🔥 Calories: {user.daily_calorie_goal:.0f} kcal\n"
        profile_text += f"🥩 Protein: {user.daily_protein_goal:.1f} g\n"
        profile_text += f"🧈 Fat: {user.daily_fat_goal:.1f} g\n"
        profile_text += f"🍞 Carbs: {user.daily_carbs_goal:.1f} g\n"
        profile_text += f"💧 Water: {user.daily_water_goal:.0f} ml\n\n"
        
        profile_text += "⚙️ <b>Actions:</b>\n"
        profile_text += "📝 Edit profile\n"
        profile_text += "🔄 Update goals\n"
        profile_text += "📊 View statistics"
        
        await message.answer(
            profile_text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data == "edit_profile")
async def edit_profile_callback(callback: CallbackQuery, state: FSMContext):
    """Callback for editing profile"""
    await callback.answer()
    
    await callback.message.answer(
        "📝 <b>Edit Profile</b>\n\n"
        "What would you like to edit?\n\n"
        "⚖️ Weight\n"
        "📏 Height\n"
        "🎂 Age\n"
        "⚧️ Gender\n"
        "🎯 Goal\n"
        "🏃 Activity\n"
        "🌍 Timezone\n"
        "🏙️ City",
        reply_markup=get_edit_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("edit_"))
async def process_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Process edit callbacks"""
    await callback.answer()
    
    edit_type = callback.data.replace("edit_", "")
    
    edit_messages = {
        "weight": "⚖️ Enter your new weight in kg:",
        "height": "📏 Enter your new height in cm:",
        "age": "🎂 Enter your new age:",
        "gender": "⚧️ Select your gender:",
        "goal": "🎯 Select your goal:",
        "activity": "🏃 Select your activity level:",
        "timezone": "🌍 Select your timezone:",
        "city": "🏙️ Enter your new city:"
    }
    
    edit_keyboards = {
        "weight": None,
        "height": None,
        "age": None,
        "gender": get_gender_keyboard(),
        "goal": get_goal_keyboard(),
        "activity": get_activity_keyboard(),
        "timezone": get_timezone_keyboard(),
        "city": None
    }
    
    message = edit_messages.get(edit_type, "❌ Invalid edit type")
    keyboard = edit_keyboards.get(edit_type)
    
    if keyboard:
        await callback.message.answer(message, reply_markup=keyboard, parse_mode="HTML")
    else:
        await callback.message.answer(message, parse_mode="HTML")
    
    # Set appropriate state
    state_mapping = {
        "weight": ProfileStates.waiting_for_weight,
        "height": ProfileStates.waiting_for_height,
        "age": ProfileStates.waiting_for_age,
        "gender": ProfileStates.waiting_for_gender,
        "goal": ProfileStates.waiting_for_goal,
        "activity": ProfileStates.waiting_for_activity,
        "timezone": ProfileStates.waiting_for_timezone,
        "city": ProfileStates.waiting_for_city
    }
    
    target_state = state_mapping.get(edit_type)
    if target_state:
        await state.set_state(target_state)
        await state.update_data(edit_mode=True)

# =============================================================================
# 🎨 KEYBOARD FUNCTIONS
# =============================================================================
def get_goal_keyboard() -> ReplyKeyboardMarkup:
    """Get goal selection keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔥 Lose weight")],
            [KeyboardButton(text="💪 Gain weight")],
            [KeyboardButton(text="⚖️ Maintain weight")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_activity_keyboard() -> ReplyKeyboardMarkup:
    """Get activity level keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪑 Sedentary")],
            [KeyboardButton(text="🚶 Light activity")],
            [KeyboardButton(text="🏃 Moderate activity")],
            [KeyboardButton(text="🏋️ Active")],
            [KeyboardButton(text="🔥 Very active")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    """Get confirmation keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Save profile")],
            [KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_edit_keyboard() -> InlineKeyboardMarkup:
    """Get edit profile keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚖️ Weight", callback_data="edit_weight"),
                InlineKeyboardButton(text="📏 Height", callback_data="edit_height"),
                InlineKeyboardButton(text="🎂 Age", callback_data="edit_age")
            ],
            [
                InlineKeyboardButton(text="⚧️ Gender", callback_data="edit_gender"),
                InlineKeyboardButton(text="🎯 Goal", callback_data="edit_goal"),
                InlineKeyboardButton(text="🏃 Activity", callback_data="edit_activity")
            ],
            [
                InlineKeyboardButton(text="🌍 Timezone", callback_data="edit_timezone"),
                InlineKeyboardButton(text="🏙️ City", callback_data="edit_city")
            ]
        ]
    )
    return keyboard
