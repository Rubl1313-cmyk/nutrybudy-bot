from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.parsers import parse_shopping_items
from handlers.media_handlers import process_food_items

router = Router()

@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """
    /search <продукт> – теперь использует универсальный механизм.
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "🔍 <b>Поиск продуктов</b>\n"
            "Использование: /search <название>\n"
            "Пример: /search курица",
            parse_mode="HTML"
        )
        return

    query = args[1].strip()
    parsed = parse_shopping_items(query)
    if not parsed:
        await message.answer("❌ Не удалось распознать продукт.")
        return

    # Берём первый продукт из распознанного (обычно один)
    name, qty, unit = parsed[0]
    food_items = [{'name': name, 'weight': 100}]  # вес по умолчанию 100 г

    await state.update_data(selected_foods=[], meal_type='snack')
    await process_food_items(message, state, food_items, meal_type='snack')
