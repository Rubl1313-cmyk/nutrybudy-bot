"""
Common commands: /start, /help, /cancel, and interactive help menu.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

from keyboards.reply_v2 import get_main_keyboard_v2
from keyboards.inline import get_progress_menu
from utils.localized_commands import create_localized_command_filter

router = Router()

@router.message(Command("start"))
@router.message(create_localized_command_filter("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Welcome new user"""
    await state.clear()
    
    user_name = message.from_user.first_name or "User"
    
    welcome_text = f"""✨ Welcome, {user_name}! I'm your personal AI health assistant.

🤖 <b>What I can do:</b>
• 🍽️ Track meals - just describe what you ate, or send a photo
• 💧 Track water - write how much you drank
• 🏃 Track activity and steps - "ran 5 km" or "10000 steps"
• ⚖️ Analyze weight and progress - show graphs and give predictions
• 🧮 Calculate body composition - body mass index (BMI), fat percentage, muscle mass and norms
• 🤖 Answer any questions about nutrition, training and health

💬 <b>How to communicate?</b>
Just write me everything you think is necessary.
I'll understand what you need: log food, show progress or give advice.

👉 <b>Examples:</b>
• "Today for lunch I ate 200g chicken breast with buckwheat"
• "Drank 3 glasses of water"
• "What's my progress for the week?"
• "Suggest a dinner recipe with high protein content"

<b>⚠️ Important:</b> For accurate calorie calculation and personal recommendations, first set up your profile with /set_profile

Choose an action in the menu below or just ask a question."""
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(Command("help"))
@router.message(create_localized_command_filter("help"))
async def cmd_help(message: Message, state: FSMContext):
    """Show help menu"""
    await state.clear()
    
    help_text = """🆘 <b>Help & Commands</b>

📋 <b>Main Commands:</b>
• /start - Start bot and see main features
• /set_profile - Set up your personal profile
• /profile - View your profile information
• /progress - View your progress statistics
• /weight - View weight statistics
• /cancel - Cancel current operation

🍽️ <b>Food Tracking:</b>
• Just describe what you ate: "200g chicken with rice"
• Send a photo of your meal for AI recognition
• Use specific weights for accuracy

💧 <b>Water Tracking:</b>
• "Drank 1 glass of water"
• "500ml water"
• "2 cups of water"

🏃 <b>Activity Tracking:</b>
• "Ran 5 km in 30 minutes"
• "10000 steps today"
• "Gym workout for 1 hour"

⚖️ <b>Weight Tracking:</b>
• "Weight 75.5 kg"
• Use /log_weight for detailed tracking

📊 <b>Progress Analysis:</b>
• "Show my progress for the week"
• "How am I doing with calories?"
• "Weight change this month"

🤖 <b>AI Assistant:</b>
• Ask any nutrition questions
• Request recipe suggestions
• Get workout advice
• Calculate nutritional values

💡 <b>Tips:</b>
• Set up your profile first for personalized recommendations
• Be specific with weights and amounts
• Use photos for easier food tracking
• Check progress regularly"""
    
    await message.answer(
        help_text,
        reply_markup=get_help_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("cancel"))
@router.message(create_localized_command_filter("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation"""
    await state.clear()
    
    await message.answer(
        "❌ Operation cancelled.\n\n"
        "🔄 What would you like to do next?",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery, state: FSMContext):
    """Help callback from inline keyboard"""
    await callback.answer()
    await cmd_help(callback.message, state)

@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Cancel callback from inline keyboard"""
    await callback.answer()
    await cmd_cancel(callback.message, state)

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Return to main menu"""
    await callback.answer()
    await state.clear()
    
    await callback.message.answer(
        "🏠 <b>Main Menu</b>\n\n"
        "Choose an action below:",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("period_"))
async def period_callback(callback: CallbackQuery, state: FSMContext):
    """Handle period selection from progress menu"""
    await callback.answer(f"📊 Loading statistics...")
    
    # Import and call progress handler
    from handlers.progress import process_progress_period
    
    # Create mock callback with correct data
    class MockCallback:
        def __init__(self, original_callback, data):
            self.message = original_callback.message
            self.from_user = original_callback.from_user
            self.data = data
    
    mock_callback = MockCallback(callback, callback.data)
    await process_progress_period(mock_callback, state)

@router.callback_query(F.data == "manual_food")
async def manual_food_callback(callback: CallbackQuery, state: FSMContext):
    """Handle manual food entry callback"""
    await callback.answer()
    
    await callback.message.answer(
        "🍽️ <b>Manual Food Entry</b>\n\n"
        "Describe what you ate:\n\n"
        "📊 <b>Examples:</b>\n"
        "• 200g chicken breast with rice\n"
        "• Salad with vegetables and olive oil\n"
        "• Pasta with tomato sauce\n"
        "• Oatmeal with berries\n\n"
        "Be specific with weights for accurate tracking!",
        parse_mode="HTML"
    )
    
    # Set state for manual food entry
    from utils.states import FoodStates
    await state.set_state(FoodStates.waiting_for_food_description)

@router.callback_query(F.data == "water")
async def water_callback(callback: CallbackQuery, state: FSMContext):
    """Handle water tracking callback"""
    await callback.answer()
    
    await callback.message.answer(
        "💧 <b>Water Tracking</b>\n\n"
        "How much water did you drink?\n\n"
        "📊 <b>Examples:</b>\n"
        "• 1 glass\n"
        "• 250ml\n"
        "• 500ml\n"
        "• 1 liter\n"
        "• 2 cups",
        parse_mode="HTML"
    )
    
    # Set state for water entry
    from utils.states import WaterStates
    await state.set_state(WaterStates.waiting_for_water)

@router.callback_query(F.data == "activity")
async def activity_callback(callback: CallbackQuery, state: FSMContext):
    """Handle activity tracking callback"""
    await callback.answer()
    
    await callback.message.answer(
        "🏃 <b>Activity Tracking</b>\n\n"
        "Describe your activity:\n\n"
        "📊 <b>Examples:</b>\n"
        "• Ran 5 km in 30 minutes\n"
        "• 10000 steps today\n"
        "• Gym workout for 1 hour\n"
        "• Yoga class 45 minutes\n"
        "• Swimming 30 minutes",
        parse_mode="HTML"
    )
    
    # Set state for activity entry
    from utils.states import ActivityStates
    await state.set_state(ActivityStates.waiting_for_activity)

@router.callback_query(F.data == "weight")
async def weight_callback(callback: CallbackQuery, state: FSMContext):
    """Handle weight tracking callback"""
    await callback.answer()
    
    await callback.message.answer(
        "⚖️ <b>Weight Tracking</b>\n\n"
        "Enter your current weight:\n\n"
        "📊 <b>Examples:</b>\n"
        "• 75.5\n"
        "• 75.5 kg\n"
        "• 75,5\n"
        "• 75.5кг",
        parse_mode="HTML"
    )
    
    # Set state for weight entry
    from utils.states import WeightStates
    await state.set_state(WeightStates.waiting_for_weight)

@router.callback_query(F.data == "progress")
async def progress_callback(callback: CallbackQuery, state: FSMContext):
    """Handle progress viewing callback"""
    await callback.answer()
    
    await callback.message.answer(
        "📊 <b>Progress Statistics</b>\n\n"
        "Select time period:",
        reply_markup=get_progress_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery, state: FSMContext):
    """Handle profile viewing callback"""
    await callback.answer()
    
    # Import and call profile handler
    from handlers.profile import cmd_profile
    await cmd_profile(callback.message, state)

@router.callback_query(F.data == "ai_assistant")
async def ai_assistant_callback(callback: CallbackQuery, state: FSMContext):
    """Handle AI assistant callback"""
    await callback.answer()
    
    await callback.message.answer(
        "🤖 <b>AI Assistant</b>\n\n"
        "I can help you with:\n\n"
        "🍽️ <b>Nutrition:</b>\n"
        "• Recipe suggestions\n"
        "• Nutritional information\n"
        "• Diet advice\n"
        "• Meal planning\n\n"
        "🏋️ <b>Fitness:</b>\n"
        "• Workout recommendations\n"
        "• Exercise form tips\n"
        "• Training plans\n"
        "• Recovery advice\n\n"
        "🧠 <b>Health:</b>\n"
        "• General health questions\n"
        "• Lifestyle tips\n"
        "• Stress management\n"
        "• Sleep advice\n\n"
        "Just ask me anything! 🤔",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery, state: FSMContext):
    """Handle settings callback"""
    await callback.answer()
    
    await callback.message.answer(
        "⚙️ <b>Settings</b>\n\n"
        "Manage your bot settings:\n\n"
        "👤 Edit Profile\n"
        "🎯 Update Goals\n"
        "🌍 Change Timezone\n"
        "🔔 Notifications\n"
        "📊 Privacy Settings\n\n"
        "Use /set_profile to update your information",
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )

@router.message()
async def universal_text_handler(message: Message, state: FSMContext):
    """Universal text handler for all messages"""
    # Check if user is in a specific state
    current_state = await state.get_state()
    
    if current_state:
        # Let state-specific handlers process the message
        return
    
    # Process as general query
    await process_general_query(message)

async def process_general_query(message: Message):
    """Process general user queries"""
    text = message.text.lower()
    
    # Check for water tracking
    if any(word in text for word in ['выпил', 'выпила', 'воды', 'воду', 'стакан', 'стакана', 'мл', 'литр']):
        await handle_water_query(message)
        return
    
    # Check for steps tracking
    if any(word in text for word in ['шагов', 'шага', 'шаг', 'пробежал', 'пробежала', 'прошел', 'прошла']):
        await handle_steps_query(message)
        return
    
    # Check for weight tracking
    if any(word in text for word in ['вес', 'весу', 'вешу', 'кг', 'килограмм']):
        await handle_weight_query(message)
        return
    
    # Check for food tracking
    if any(word in text for word in ['съел', 'съела', 'ел', 'ела', 'завтрак', 'обед', 'ужин', 'грамм', 'г']):
        await handle_food_query(message)
        return
    
    # Check for progress queries
    if any(word in text for word in ['прогресс', 'статистика', 'динамика', 'изменения']):
        await handle_progress_query(message)
        return
    
    # Default: AI assistant response
    await handle_ai_query(message)

async def handle_water_query(message: Message):
    """Handle water tracking queries"""
    # Import water handler
    from handlers.drinks import process_water_text
    await process_water_text(message)

async def handle_steps_query(message: Message):
    """Handle steps tracking queries"""
    # Import activity handler
    from handlers.activity import process_activity_text
    await process_activity_text(message)

async def handle_weight_query(message: Message):
    """Handle weight tracking queries"""
    # Import weight handler
    from handlers.weight import cmd_log_weight
    from aiogram.fsm.context import FSMContext
    state = FSMContext()
    await cmd_log_weight(message, state)

async def handle_food_query(message: Message):
    """Handle food tracking queries"""
    # Import food handler
    from handlers.universal import process_food_text
    await process_food_text(message)

async def handle_progress_query(message: Message):
    """Handle progress queries"""
    await message.answer(
        "📊 <b>Progress Statistics</b>\n\n"
        "To view your progress, use the Progress button in the menu or type:\n\n"
        "• /progress - main progress\n"
        "• /weight - weight statistics\n\n"
        "You can also ask:\n"
        "• \"Show my progress for the week\"\n"
        "• \"How am I doing with calories?\"",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

async def handle_ai_query(message: Message):
    """Handle AI assistant queries"""
    # Import AI assistant
    from handlers.ai_assistant import process_ai_query
    await process_ai_query(message)

# =============================================================================
# 🎨 KEYBOARD FUNCTIONS
# =============================================================================
def get_help_keyboard() -> InlineKeyboardMarkup:
    """Get help menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Profile", callback_data="profile"),
                InlineKeyboardButton(text="📊 Progress", callback_data="progress")
            ],
            [
                InlineKeyboardButton(text="🍽️ Food", callback_data="manual_food"),
                InlineKeyboardButton(text="💧 Water", callback_data="water")
            ],
            [
                InlineKeyboardButton(text="🏃 Activity", callback_data="activity"),
                InlineKeyboardButton(text="⚖️ Weight", callback_data="weight")
            ],
            [
                InlineKeyboardButton(text="🤖 AI Assistant", callback_data="ai_assistant"),
                InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ]
        ]
    )
    return keyboard

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Get settings menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Edit Profile", callback_data="edit_profile"),
                InlineKeyboardButton(text="🎯 Update Goals", callback_data="update_goals")
            ],
            [
                InlineKeyboardButton(text="🌍 Timezone", callback_data="timezone"),
                InlineKeyboardButton(text="🔔 Notifications", callback_data="notifications")
            ],
            [
                InlineKeyboardButton(text="📊 Privacy", callback_data="privacy"),
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ]
        ]
    )
    return keyboard
