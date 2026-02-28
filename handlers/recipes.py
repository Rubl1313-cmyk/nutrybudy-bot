from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from services.cloudflare_ai import generate_recipe
from keyboards.reply import get_main_keyboard

router = Router()

@router.message(Command("recipe"))
async def cmd_recipe(message: Message):
    ingredients = message.text.replace("/recipe", "").strip()
    if not ingredients:
        await message.answer(
            "🧑‍🍳 <b>Генератор рецептов</b>\n\n"
            "Укажите ингредиенты через запятую:\n"
            "<code>/recipe картошка, лук, морковь, курица</code>",
            parse_mode="HTML"
        )
        return
    
    await message.answer("🔄 Генерирую рецепт... Это займёт около 10 секунд.")
    
    recipe = await generate_recipe(ingredients)
    
    if recipe:
        await message.answer(
            f"🍽️ <b>Ваш рецепт:</b>\n\n{recipe}",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Не удалось сгенерировать рецепт. Попробуйте позже.", reply_markup=get_main_keyboard())