"""
Инструменты для AI-ассистента.
"""
from database.db import get_session
from database.models import ShoppingItem
from handlers.shopping import get_or_create_default_list
from services.weather import get_temperature


async def add_to_shopping_list(telegram_id: int, items: list) -> str:
    async with get_session() as session:
        shopping_list = await get_or_create_default_list(telegram_id, session)
        if not shopping_list:
            return "❌ Не удалось получить список."

        added = []
        for item in items:
            shopping_item = ShoppingItem(
                list_id=shopping_list.id,
                name=item["name"],
                quantity=int(item.get("quantity", 1)),
                unit=item.get("unit", "шт"),
                added_by=telegram_id
            )
            session.add(shopping_item)
            added.append(f"{item['name']} — {item.get('quantity', 1)} {item.get('unit', 'шт')}")
        await session.commit()
        return f"✅ Добавлено:\n" + "\n".join(added) if added else "❌ Ничего не добавлено."


async def get_weather(city: str) -> str:
    temp = await get_temperature(city)
    return f"🌆 {city}: {temp}°C"
