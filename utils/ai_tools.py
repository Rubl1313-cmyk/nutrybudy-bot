"""
Функции, которые AI может вызывать через function calling.
"""
import logging
from database.db import get_session
from database.models import User, ShoppingList, ShoppingItem
from utils.parsers import parse_shopping_items
from handlers.shopping import get_or_create_default_list
from services.weather import get_temperature

logger = logging.getLogger(__name__)


async def add_to_shopping_list(telegram_id: int, items: list) -> str:
    """
    Добавляет товары в список покупок пользователя.
    items: список словарей [{"name": "яйца", "quantity": 3, "unit": "шт"}, ...]
    """
    async with get_session() as session:
        shopping_list = await get_or_create_default_list(telegram_id, session)
        if not shopping_list:
            return "❌ Не удалось получить список покупок."

        added = []
        for item in items:
            try:
                name = item["name"]
                qty = int(item.get("quantity", 1))
                unit = item.get("unit", "шт")
            except (KeyError, ValueError):
                continue

            shopping_item = ShoppingItem(
                list_id=shopping_list.id,
                name=name,
                quantity=qty,
                unit=unit,
                added_by=telegram_id
            )
            session.add(shopping_item)
            added.append(f"{name} — {qty} {unit}")

        await session.commit()

    if added:
        return f"✅ Добавлено в список покупок:\n" + "\n".join(added)
    else:
        return "❌ Не удалось добавить товары."


async def suggest_recipe(ingredients: str) -> str:
    """
    Заглушка – здесь можно вызвать Spoonacular или просто вернуть сообщение,
    что AI сгенерирует рецепт. Мы оставим это на усмотрение AI, т.к. он сам может
    сгенерировать рецепт без внешнего API.
    """
    # Возвращаем специальный маркер, который означает, что AI должен сам сгенерировать рецепт.
    return "GENERATE_RECIPE"


async def get_weather(city: str) -> str:
    """Получает погоду в городе."""
    temp = await get_temperature(city)
    return f"🌆 {city}: {temp}°C"
