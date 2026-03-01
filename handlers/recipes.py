"""
Обработчик генерации рецептов для NutriBuddy
✅ Синхронизирован с utils/states.py
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from services.cloudflare_ai import generate_recipe
from keyboards.inline import get_recipe_options_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import RecipeStates

router = Router()


@router.message(Command("recipe"))
@router.message(F.text == "📖 Рецепты")
async def cmd_recipe(message: Message, state: FSMContext):
    """Начало генерации рецепта"""
    await state.clear()
    await state.set_state(RecipeStates.entering_ingredients)
    
    await message.answer(
        "📖 <b>Генератор рецептов</b>\n\n"
        "Введите ингредиенты через запятую:\n"
        "<i>Например: курица, рис, брокколи</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(RecipeStates.entering_ingredients, F.text)
async def process_ingredients(message: Message, state: FSMContext):
    """Ввод ингредиентов"""
    ingredients = message.text.strip()
    
    if len(ingredients) < 3:
        await message.answer("❌ Введите хотя бы 2-3 ингредиента")
        return
    
    await state.update_data(ingredients=ingredients)
    await state.set_state(RecipeStates.selecting_diet)
    
    await message.answer(
        f"✅ Ингредиенты: <b>{ingredients}</b>\n\n"
        "🥗 Выберите тип питания (опционально):",
        reply_markup=get_recipe_options_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("diet_"), RecipeStates.selecting_diet)
async def process_diet(callback: CallbackQuery, state: FSMContext):
    """Выбор типа диеты"""
    diet = callback.data.split("_")[1]
    diet_map = {
        "vegetarian": "вегетарианское",
        "protein": "белковое",
        "keto": "кето",
        "lowcarb": "низкоуглеводное"
    }
    
    await state.update_data(diet=diet_map.get(diet, "обычное"))
    await state.set_state(RecipeStates.selecting_difficulty)
    
    await callback.message.edit_text(
        f"✅ Тип: <b>{diet_map.get(diet, 'обычное')}</b>\n\n"
        "👨‍🍳 Выберите сложность:\n"
        "• Лёгкая (~15 мин)\n"
        "• Средняя (~30 мин)\n"
        "• Сложная (~60 мин)\n\n"
        "Напишите: лёгкая, средняя или сложная"
    )
    await callback.answer()


@router.message(RecipeStates.selecting_difficulty, F.text)
async def process_difficulty(message: Message, state: FSMContext):
    """Выбор сложности"""
    difficulty = message.text.strip().lower()
    
    if difficulty not in ["лёгкая", "легкая", "средняя", "сложная"]:
        await message.answer("❌ Напишите: лёгкая, средняя или сложная")
        return
    
    if difficulty == "легкая":
        difficulty = "лёгкая"
    
    await state.update_data(difficulty=difficulty)
    
    data = await state.get_data()
    
    await message.answer(
        "🧑‍🍳 <b>Генерирую рецепт...</b>\n\n"
        f"🥘 {data['ingredients']}\n"
        f"🥗 {data['diet']}\n"
        f"⏱️ {difficulty}\n\n"
        "<i>Это займёт ~15 секунд...</i>",
        parse_mode="HTML"
    )
    
    # Генерация рецепта
    recipe = await generate_recipe(
        ingredients=data['ingredients'],
        diet_type=data['diet'],
        difficulty=difficulty
    )
    
    if recipe:
        await message.answer(
            f"🍽️ <b>Ваш рецепт:</b>\n\n{recipe}",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Не удалось сгенерировать рецепт.\n\n"
            "Попробуйте позже или уточните ингредиенты.",
            reply_markup=get_main_keyboard()
        )
    
    await state.clear()
