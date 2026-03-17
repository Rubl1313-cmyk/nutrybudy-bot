# handlers/food_clarification.py
import logging
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.food_api import get_product_variants
from services.ai_processor import ai_processor
from services.soup_service import is_soup, save_soup
from utils.safe_parser import safe_parse_float

logger = logging.getLogger(__name__)
router = Router()

class FoodClarificationStates(StatesGroup):
    waiting_for_product_choice = State()   # Ğ¾Ğ¶Ğ¸Ğ´Ğ°Ğ½Ğ¸Ğµ Ğ²Ñ‹Ğ±Ğ¾Ñ€Ğ° Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ° Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ°
    waiting_for_weight = State()           # Ğ¾Ğ¶Ğ¸Ğ´Ğ°Ğ½Ğ¸Ğµ Ğ²Ğ²Ğ¾Ğ´Ğ° Ğ²ĞµÑ�Ğ°
    waiting_for_manual_name = State()      # Ñ€ÑƒÑ‡Ğ½Ğ¾Ğ¹ Ğ²Ğ²Ğ¾Ğ´ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ñ�

@router.message(F.text, flags={"rate_limit": "food"})
async def handle_food_text(message: Message, state: FSMContext):
    """Ğ�Ğ°Ñ‡Ğ°Ğ»Ğ¾ Ğ¾Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ¸ Ñ‚ĞµĞºÑ�Ñ‚Ğ° ĞºĞ°Ğº ĞµĞ´Ñ‹ (Ğ²Ñ‹Ğ·Ñ‹Ğ²Ğ°ĞµÑ‚Ñ�Ñ� Ğ¸Ğ· ai_handler, ĞµÑ�Ğ»Ğ¸ AI Ğ²ĞµÑ€Ğ½ÑƒĞ» food_items)."""
    user_id = message.from_user.id
    text = message.text

    # 1. ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¾Ñ‚ AI Ñ�Ğ¿Ğ¸Ñ�Ğ¾Ğº Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ² (ĞºĞ°Ğº Ñ€Ğ°Ğ½ÑŒÑˆĞµ)
    result = await ai_processor.process_text_input(text, user_id)
    if not result.get("success") or result["intent"] != "log_food":
        # Ğ•Ñ�Ğ»Ğ¸ Ğ½Ğµ ĞµĞ´Ğ°, Ğ¿Ñ€Ğ¾Ğ±Ñ€Ğ°Ñ�Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ´Ğ°Ğ»ÑŒÑˆĞµ (Ğ¼Ğ¾Ğ¶ĞµÑ‚ Ğ±Ñ‹Ñ‚ÑŒ Ğ´Ñ€ÑƒĞ³Ğ¾Ğ¹ intent)
        return False

    parameters = result["parameters"]
    food_items = parameters.get("food_items", [])

    if not food_items:
        await message.answer("ğŸ¤” Ğ�Ğµ ÑƒĞ´Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ€Ğ°Ñ�Ğ¿Ğ¾Ğ·Ğ½Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ Ğ¾Ğ¿Ğ¸Ñ�Ğ°Ñ‚ÑŒ Ğ¿Ğ¾Ğ´Ñ€Ğ¾Ğ±Ğ½ĞµĞµ.")
        return True

    # 2. ĞŸÑ€Ğ¾Ğ²ĞµÑ€Ñ�ĞµĞ¼, Ğ½Ğµ Ñ�Ğ²Ğ»Ñ�ĞµÑ‚Ñ�Ñ� Ğ»Ğ¸ Ñ�Ñ‚Ğ¾ Ñ�ÑƒĞ¿Ğ¾Ğ¼
    dish_name = parameters.get("description", text)
    if is_soup(dish_name):
        # Ğ­Ñ‚Ğ¾ Ñ�ÑƒĞ¿ - Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ ĞºĞ°Ğº ĞµĞ´Ğ° + Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ
        try:
            # Ğ�Ñ†ĞµĞ½Ğ¸Ğ²Ğ°ĞµĞ¼ Ğ¾Ğ±ÑŠÑ‘Ğ¼ Ñ�ÑƒĞ¿Ğ° (ĞµÑ�Ğ»Ğ¸ Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½, Ñ�Ñ‡Ğ¸Ñ‚Ğ°ĞµĞ¼ 300 Ğ¼Ğ»)
            volume_ml = 300  # Ğ¡Ñ‚Ğ°Ğ½Ğ´Ğ°Ñ€Ñ‚Ğ½Ğ°Ñ� Ğ¿Ğ¾Ñ€Ñ†Ğ¸Ñ� Ñ�ÑƒĞ¿Ğ°
            
            # Ğ˜Ñ‰ĞµĞ¼ ÑƒĞ¿Ğ¾Ğ¼Ğ¸Ğ½Ğ°Ğ½Ğ¸Ğµ Ğ¾Ğ±ÑŠÑ‘Ğ¼Ğ° Ğ² Ñ‚ĞµĞºÑ�Ñ‚Ğµ
            import re
            volume_match = re.search(r'(\d+)\s*(Ğ¼Ğ»|Ğ»|Ñ�Ñ‚Ğ°ĞºĞ°Ğ½)', text.lower())
            if volume_match:
                amount = float(volume_match.group(1))
                unit = volume_match.group(2)
                if unit == 'Ğ»':
                    volume_ml = amount * 1000
                elif unit == 'Ñ�Ñ‚Ğ°ĞºĞ°Ğ½':
                    volume_ml = amount * 250
                else:
                    volume_ml = amount
            
            # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ�ÑƒĞ¿
            result = await save_soup(user_id, dish_name, volume_ml)
            
            await message.answer(
                f"ğŸ�² <b>Ğ¡ÑƒĞ¿ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ‘Ğ½!</b>\n\n"
                f"ğŸ¥£ {dish_name.title()}: {volume_ml} Ğ¼Ğ»\n"
                f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {result['calories']:.0f} ĞºĞºĞ°Ğ»\n"
                f"ğŸ’§ Ğ–Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ: {result['water_volume']:.0f} Ğ¼Ğ»\n\n"
                f"âœ… Ğ£Ñ‡Ñ‚ĞµĞ½Ğ¾ Ğ¸ ĞºĞ°Ğº ĞµĞ´Ğ°, Ğ¸ ĞºĞ°Ğº Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ!",
                parse_mode="HTML"
            )
            return True
            
        except Exception as e:
            logger.error(f"Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğ¸ Ñ�ÑƒĞ¿Ğ°: {e}")
            await message.answer("â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ñ€Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ğ¸ Ñ�ÑƒĞ¿Ğ°. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ·.")
            return True

    # 3. Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ² FSM state
    await state.update_data({
        "food_clarification": {
            "original_items": food_items,
            "current_index": 0,
            "clarified_items": []
        }
    })

    # 4. Ğ�Ğ°Ñ‡Ğ¸Ğ½Ğ°ĞµĞ¼ ÑƒÑ‚Ğ¾Ñ‡Ğ½ĞµĞ½Ğ¸Ğµ Ğ¿ĞµÑ€Ğ²Ğ¾Ğ³Ğ¾ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ°
    await clarify_next_product(message, user_id, state)
    return True

async def clarify_next_product(message: Message, user_id: int, state: FSMContext):
    """Ğ£Ñ‚Ğ¾Ñ‡Ğ½Ñ�ĞµÑ‚ Ñ�Ğ»ĞµĞ´ÑƒÑ�Ñ‰Ğ¸Ğ¹ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚ Ğ² Ñ�Ğ¿Ğ¸Ñ�ĞºĞµ."""
    data = await state.get_data()
    storage = data.get("food_clarification")
    if not storage:
        return

    idx = storage["current_index"]
    if idx >= len(storage["original_items"]):
        # Ğ’Ñ�Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹ ÑƒÑ‚Ğ¾Ñ‡Ğ½ĞµĞ½Ñ‹ â€“ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ¸Ñ‚Ğ¾Ğ³
        await finish_clarification(message, user_id, state)
        return

    product = storage["original_items"][idx]
    product_name = product.get("name", "")

    # Ğ˜Ñ‰ĞµĞ¼ Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ñ‹ Ğ² Ğ»Ğ¾ĞºĞ°Ğ»ÑŒĞ½Ğ¾Ğ¹ Ğ±Ğ°Ğ·Ğµ
    variants = get_product_variants(product_name)  # Ñ„ÑƒĞ½ĞºÑ†Ğ¸Ñ� Ğ¸Ğ· food_api.py

    if variants and len(variants) > 1:
        # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ñ‹
        builder = InlineKeyboardBuilder()
        for i, var in enumerate(variants[:5]):  # Ğ¼Ğ°ĞºÑ�Ğ¸Ğ¼ÑƒĞ¼ 5 Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ²
            cal = var.get("calories", 0)
            protein = var.get("protein", 0)
            fat = var.get("fat", 0)
            carbs = var.get("carbs", 0)
            text_button = f"{var['name']} â€“ {cal:.0f} ĞºĞºĞ°Ğ» (Ğ‘:{protein:.1f} Ğ–:{fat:.1f} Ğ£:{carbs:.1f})"
            builder.button(text=text_button, callback_data=f"clr_var_{idx}_{i}")
        builder.button(text="âœ�ï¸� Ğ’Ğ²ĞµÑ�Ñ‚Ğ¸ Ğ²Ñ€ÑƒÑ‡Ğ½ÑƒÑ�", callback_data=f"clr_manual_{idx}")
        builder.button(text="â�Œ ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�Ñ‚Ğ¸Ñ‚ÑŒ", callback_data=f"clr_skip_{idx}")
        builder.adjust(1)

        await message.answer(
            f"ğŸ�½ï¸� Ğ£Ñ‚Ğ¾Ñ‡Ğ½Ğ¸Ñ‚Ğµ, Ñ‡Ñ‚Ğ¾ Ğ²Ñ‹ Ğ¸Ğ¼ĞµĞ»Ğ¸ Ğ² Ğ²Ğ¸Ğ´Ñƒ Ğ¿Ğ¾Ğ´ Â«{product_name}Â»?",
            reply_markup=builder.as_markup()
        )
        await state.set_state(FoodClarificationStates.waiting_for_product_choice)
    else:
        # Ğ•Ñ�Ğ»Ğ¸ Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚ Ğ¾Ğ´Ğ¸Ğ½ Ğ¸Ğ»Ğ¸ Ğ½ĞµÑ‚ Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚Ğ¾Ğ² â€“ Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ AI-Ğ¾Ñ†ĞµĞ½ĞºÑƒ Ğ¸ Ñ�Ñ€Ğ°Ğ·Ñƒ Ğ·Ğ°Ğ¿Ñ€Ğ°ÑˆĞ¸Ğ²Ğ°ĞµĞ¼ Ğ²ĞµÑ�
        # ĞœĞ¾Ğ¶Ğ½Ğ¾ Ğ²Ğ·Ñ�Ñ‚ÑŒ Ğ¿ĞµÑ€Ğ²Ñ‹Ğ¹ Ğ²Ğ°Ñ€Ğ¸Ğ°Ğ½Ñ‚ Ğ¸Ğ»Ğ¸ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾Ñ‚ AI
        if variants:
            chosen = variants[0]
        else:
            # Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Ğ¸Ñ�Ñ…Ğ¾Ğ´Ğ½Ñ‹Ğµ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğµ Ğ¾Ñ‚ AI
            chosen = {
                "name": product_name,
                "calories": product.get("calories_per_100g", 0),
                "protein": product.get("protein_per_100g", 0),
                "fat": product.get("fat_per_100g", 0),
                "carbs": product.get("carbs_per_100g", 0)
            }

        storage["clarified_items"].append({
            "name": chosen["name"],
            "calories_per_100g": chosen.get("calories", 0),
            "protein_per_100g": chosen.get("protein", 0),
            "fat_per_100g": chosen.get("fat", 0),
            "carbs_per_100g": chosen.get("carbs", 0),
            "weight": None  # Ğ±ÑƒĞ´ĞµÑ‚ Ğ·Ğ°Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ¾ Ğ¿Ğ¾Ğ·Ğ¶Ğµ
        })
        storage["current_index"] += 1
        await state.update_data({"food_clarification": storage})
        # Ğ—Ğ°Ğ¿Ñ€Ğ°ÑˆĞ¸Ğ²Ğ°ĞµĞ¼ Ğ²ĞµÑ�
        await ask_weight(message, user_id, idx, state)

async def ask_weight(message: Message, user_id: int, idx: int, state: FSMContext):
    """Ğ—Ğ°Ğ¿Ñ€Ğ°ÑˆĞ¸Ğ²Ğ°ĞµÑ‚ Ğ²ĞµÑ� Ğ´Ğ»Ñ� Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ° Ñ� Ğ¸Ğ½Ğ´ĞµĞºÑ�Ğ¾Ğ¼ idx (ÑƒĞ¶Ğµ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»ĞµĞ½Ğ½Ğ¾Ğ³Ğ¾ Ğ² clarified_items)."""
    data = await state.get_data()
    storage = data.get("food_clarification")
    if not storage or idx >= len(storage["clarified_items"]):
        return

    product = storage["clarified_items"][idx]
    await message.answer(
        f"âš–ï¸� Ğ¡ĞºĞ¾Ğ»ÑŒĞºĞ¾ Ğ³Ñ€Ğ°Ğ¼Ğ¼ Â«{product['name']}Â»? (Ğ²Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ñ‡Ğ¸Ñ�Ğ»Ğ¾)",
        reply_markup=types.ForceReply()
    )
    # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ¸Ğ½Ğ´ĞµĞºÑ� Ğ² Ñ�Ğ¾Ñ�Ñ‚Ğ¾Ñ�Ğ½Ğ¸Ğ¸
    await state.update_data(current_clarify_idx=idx)
    await state.set_state(FoodClarificationStates.waiting_for_weight)

@router.message(FoodClarificationStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    storage = data.get("food_clarification")
    idx = data.get("current_clarify_idx")

    weight, error = safe_parse_float(message.text, "Ğ²ĞµÑ�")
    if error:
        await message.answer(f"â�Œ {error}. ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ· (Ğ½Ğ°Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€, 150):")
        return

    if weight <= 0 or weight > 5000:
        await message.answer("â�Œ Ğ’ĞµÑ� Ğ´Ğ¾Ğ»Ğ¶ĞµĞ½ Ğ±Ñ‹Ñ‚ÑŒ Ğ¾Ñ‚ 1 Ğ´Ğ¾ 5000 Ğ³Ñ€Ğ°Ğ¼Ğ¼. ĞŸĞ¾Ğ²Ñ‚Ğ¾Ñ€Ğ¸Ñ‚Ğµ:")
        return

    # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ğ²ĞµÑ�
    storage["clarified_items"][idx]["weight"] = weight
    # ĞŸĞµÑ€ĞµÑ…Ğ¾Ğ´Ğ¸Ğ¼ Ğº Ñ�Ğ»ĞµĞ´ÑƒÑ�Ñ‰ĞµĞ¼Ñƒ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñƒ
    storage["current_index"] += 1
    await state.update_data({"food_clarification": storage})
    await clarify_next_product(message, user_id, state)

@router.callback_query(F.data.startswith("clr_var_"))
async def variant_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = callback.data.split("_")  # clr_var_idx_varindex
    idx = int(data[2])
    var_idx = int(data[3])
    user_id = callback.from_user.id
    state_data = await state.get_data()
    storage = state_data.get("food_clarification")
    if not storage or idx >= len(storage["original_items"]):
        await callback.message.edit_text("â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ°, Ğ½Ğ°Ñ‡Ğ½Ğ¸Ñ‚Ğµ Ğ·Ğ°Ğ½Ğ¾Ğ²Ğ¾.")
        return

    product = storage["original_items"][idx]
    variants = get_product_variants(product["name"])
    chosen = variants[var_idx]

    storage["clarified_items"].append({
        "name": chosen["name"],
        "calories_per_100g": chosen.get("calories", 0),
        "protein_per_100g": chosen.get("protein", 0),
        "fat_per_100g": chosen.get("fat", 0),
        "carbs_per_100g": chosen.get("carbs", 0),
        "weight": None  # Ğ±ÑƒĞ´ĞµÑ‚ Ğ·Ğ°Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ¾ Ğ¿Ğ¾Ğ·Ğ¶Ğµ
    })
    await state.update_data({"food_clarification": storage})
    
    # Ğ£Ğ´Ğ°Ğ»Ñ�ĞµĞ¼ ĞºĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ñƒ
    await callback.message.edit_text(f"âœ… Ğ’Ñ‹Ğ±Ñ€Ğ°Ğ½Ğ¾: {chosen['name']}")
    await ask_weight(callback.message, user_id, len(storage["clarified_items"]) - 1, state)

@router.callback_query(F.data.startswith("clr_manual_"))
async def manual_entry(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("âœ�ï¸� Ğ’Ğ²ĞµĞ´Ğ¸Ñ‚Ğµ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ° Ğ²Ñ€ÑƒÑ‡Ğ½ÑƒÑ�:")
    await state.set_state(FoodClarificationStates.waiting_for_manual_name)

@router.message(FoodClarificationStates.waiting_for_manual_name)
async def process_manual_name(message: Message, state: FSMContext):
    # ĞŸÑ€Ğ¾Ñ�Ñ‚Ğ¾ Ğ¿Ñ€Ğ¸Ğ½Ğ¸Ğ¼Ğ°ĞµĞ¼ Ğ½Ğ°Ğ·Ğ²Ğ°Ğ½Ğ¸Ğµ, Ğ¿Ğ¾Ñ‚Ğ¾Ğ¼ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ¸Ğ¼ Ğ²ĞµÑ�
    # Ğ—Ğ´ĞµÑ�ÑŒ Ğ¼Ğ¾Ğ¶Ğ½Ğ¾ Ñ‚Ğ°ĞºĞ¶Ğµ Ğ¿Ğ¾Ğ¸Ñ�ĞºĞ°Ñ‚ÑŒ Ğ² Ğ±Ğ°Ğ·Ğµ, Ğ½Ğ¾ ÑƒĞ¿Ñ€Ğ¾Ñ�Ñ‚Ğ¸Ğ¼
    user_id = message.from_user.id
    state_data = await state.get_data()
    storage = state_data.get("food_clarification")
    if not storage:
        await state.clear()
        return

    product_name = message.text.strip()
    # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ ĞºĞ°Ğº Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚ Ñ� Ğ½ÑƒĞ»ĞµĞ²Ñ‹Ğ¼Ğ¸ Ğ´Ğ°Ğ½Ğ½Ñ‹Ğ¼Ğ¸ (Ğ¿Ğ¾Ñ‚Ğ¾Ğ¼ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�Ğ¸Ğ¼ Ğ²ĞµÑ� Ğ¸, Ğ²Ğ¾Ğ·Ğ¼Ğ¾Ğ¶Ğ½Ğ¾, ĞšĞ‘Ğ–Ğ£)
    storage["clarified_items"].append({
        "name": product_name,
        "calories_per_100g": 0,
        "protein_per_100g": 0,
        "fat_per_100g": 0,
        "carbs_per_100g": 0,
        "weight": None
    })
    await state.update_data({"food_clarification": storage})
    await ask_weight(message, user_id, len(storage["clarified_items"]) - 1, state)

@router.callback_query(F.data.startswith("clr_skip_"))
async def skip_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    data = await state.get_data()
    storage = data.get("food_clarification")
    if storage:
        # ĞŸÑ€Ğ¾Ğ¿ÑƒÑ�ĞºĞ°ĞµĞ¼ Ñ�Ñ‚Ğ¾Ñ‚ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚ (Ğ½Ğµ Ğ´Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼)
        storage["current_index"] += 1
        await state.update_data({"food_clarification": storage})
        await callback.message.edit_text("â�­ï¸� ĞŸÑ€Ğ¾Ğ´ÑƒĞºÑ‚ Ğ¿Ñ€Ğ¾Ğ¿ÑƒÑ‰ĞµĞ½.")
        await clarify_next_product(callback.message, user_id, state)

async def finish_clarification(message: Message, user_id: int, state: FSMContext):
    """Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµÑ‚ ÑƒÑ‚Ğ¾Ñ‡Ğ½Ñ‘Ğ½Ğ½Ñ‹Ğµ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ñ‹ Ğ² Ğ±Ğ°Ğ·Ñƒ Ğ¸ Ğ¾Ñ‚Ğ¿Ñ€Ğ°Ğ²Ğ»Ñ�ĞµÑ‚ Ğ¸Ñ‚Ğ¾Ğ³."""
    data = await state.get_data()
    storage = data.get("food_clarification")
    if not storage:
        return

    clarified = storage["clarified_items"]
    if not clarified:
        await message.answer("â�Œ Ğ�ĞµÑ‚ Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ² Ğ´Ğ»Ñ� Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�.")
        await state.clear()
        return

    # ĞŸÑ€ĞµĞ¾Ğ±Ñ€Ğ°Ğ·ÑƒĞµĞ¼ Ğ² Ñ„Ğ¾Ñ€Ğ¼Ğ°Ñ‚, Ğ¾Ğ¶Ğ¸Ğ´Ğ°ĞµĞ¼Ñ‹Ğ¹ food_save_service
    food_items_for_save = []
    for item in clarified:
        weight = item.get("weight", 100)  # ĞµÑ�Ğ»Ğ¸ Ğ²ĞµÑ� Ğ½Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½, Ğ±ĞµÑ€Ñ‘Ğ¼ 100Ğ³
        factor = weight / 100.0
        food_items_for_save.append({
            "name": item["name"],
            "quantity": weight,
            "unit": "Ğ³",
            "calories": item["calories_per_100g"] * factor,
            "protein": item["protein_per_100g"] * factor,
            "fat": item["fat_per_100g"] * factor,
            "carbs": item["carbs_per_100g"] * factor
        })

    # Ğ¡Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ�ĞµĞ¼ Ñ‡ĞµÑ€ĞµĞ· Ñ�ĞµÑ€Ğ²Ğ¸Ñ�
    from services.food_save_service import food_save_service
    result = await food_save_service.save_food_to_db(
        user_id,
        food_items_for_save,
        meal_type="unknown"  # Ğ¼Ğ¾Ğ¶Ğ½Ğ¾ Ğ¾Ğ¿Ñ€ĞµĞ´ĞµĞ»Ğ¸Ñ‚ÑŒ Ğ¿Ğ¾ ĞºĞ¾Ğ½Ñ‚ĞµĞºÑ�Ñ‚Ñƒ Ğ¸Ğ»Ğ¸ Ñ�Ğ¿Ñ€Ğ¾Ñ�Ğ¸Ñ‚ÑŒ
    )

    if result["success"]:
        await message.answer(
            f"âœ… ĞŸÑ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ‘Ğ½!\n"
            f"ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {result['total_calories']:.0f}\n"
            f"ğŸ¥© Ğ‘ĞµĞ»ĞºĞ¸: {result['total_protein']:.1f}\n"
            f"ğŸ¥‘ Ğ–Ğ¸Ñ€Ñ‹: {result['total_fat']:.1f}\n"
            f"ğŸ�š Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {result['total_carbs']:.1f}"
        )
    else:
        await message.answer(f"â�Œ Ğ�ÑˆĞ¸Ğ±ĞºĞ° Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½ĞµĞ½Ğ¸Ñ�: {result.get('error')}")

    await state.clear()
