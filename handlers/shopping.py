"""
Обработчик списков покупок.
Только управление списками и товарами, без универсального обработчика текста.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.db import get_session
from database.models import User, ShoppingList, ShoppingItem
from keyboards.inline import get_shopping_lists_keyboard, get_shopping_items_keyboard
from keyboards.reply import get_main_keyboard
from utils.parsers import parse_shopping_items
from utils.states import ShoppingStates

router = Router()


async def get_or_create_default_list(telegram_id: int, session):
    """Возвращает основной список покупок пользователя (создаёт если нет)."""
    user_result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        return None

    result = await session.execute(
        select(ShoppingList)
        .where(
            ShoppingList.user_id == user.id,
            ShoppingList.is_archived == False
        )
        .order_by(ShoppingList.created_at.desc())
    )
    shopping_list = result.scalar_one_or_none()
    if not shopping_list:
        shopping_list = ShoppingList(
            user_id=user.id,
            name="Покупки",
            is_archived=False
        )
        session.add(shopping_list)
        await session.flush()
    return shopping_list


@router.message(Command("shopping"))
@router.message(F.text == "📋 Списки покупок")
async def cmd_shopping(message: Message, state: FSMContext):
    """Показать основной список покупок."""
    await state.clear()
    user_id = message.from_user.id

    async with get_session() as session:
        shopping_list = await get_or_create_default_list(user_id, session)
        if not shopping_list:
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile",
                reply_markup=get_main_keyboard()
            )
            return

        items_result = await session.execute(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == shopping_list.id)
            .order_by(ShoppingItem.is_checked, ShoppingItem.added_at)
        )
        items = items_result.scalars().all()

        if not items:
            text = f"📋 <b>{shopping_list.name}</b>\n\nСписок пуст. Напишите товары, и я спрошу, куда их добавить."
        else:
            text = f"📋 <b>{shopping_list.name}</b>\n\n"
            checked = sum(1 for i in items if i.is_checked)
            total = len(items)
            text += f"✅ {checked}/{total}\n\n"
            for item in items:
                status = "✅" if item.is_checked else "⬜"
                text += f"{status} {item.name} — {item.quantity} {item.unit}\n"

        await message.answer(
            text,
            reply_markup=get_shopping_items_keyboard(items, shopping_list.id),
            parse_mode="HTML"
        )


# ========== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ДОБАВЛЕНИЯ ТОВАРОВ ==========
# Эта функция будет импортироваться в другие модули

async def add_to_shopping_list(event, text: str):
    """
    Добавляет товары в список покупок из текста.
    event может быть Message или CallbackQuery.
    """
    user_id = event.from_user.id
    parsed = parse_shopping_items(text)
    if not parsed:
        if hasattr(event, 'message') and event.message:
            await event.message.answer("❌ Не удалось распознать товары.")
        else:
            await event.answer("❌ Не удалось распознать товары.", show_alert=True)
        return

    async with get_session() as session:
        shopping_list = await get_or_create_default_list(user_id, session)
        if not shopping_list:
            if hasattr(event, 'message') and event.message:
                await event.message.answer("❌ Не удалось получить список покупок.")
            else:
                await event.answer("❌ Не удалось получить список покупок.", show_alert=True)
            return

        added = []
        for name, qty, unit in parsed:
            item = ShoppingItem(
                list_id=shopping_list.id,
                name=name,
                quantity=qty,
                unit=unit,
                added_by=user_id
            )
            session.add(item)
            added.append(f"{name} — {qty} {unit}")
        await session.commit()

    if added:
        if hasattr(event, 'message') and event.message:
            await event.message.answer(f"✅ Добавлено в список покупок:\n" + "\n".join(added))
        else:
            await event.answer(f"✅ Добавлено в список покупок: {', '.join(added)}")


# ========== ОБРАБОТЧИКИ КНОПОК УПРАВЛЕНИЯ ==========

@router.callback_query(F.data.startswith("item_incr_"))
async def increase_quantity(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[2])
    async with get_session() as session:
        item = await session.get(ShoppingItem, item_id)
        if item:
            item.quantity += 1
            await session.commit()
            await update_list_message(callback, item.list_id)
    await callback.answer()


@router.callback_query(F.data.startswith("item_decr_"))
async def decrease_quantity(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[2])
    async with get_session() as session:
        item = await session.get(ShoppingItem, item_id)
        if item:
            if item.quantity > 1:
                item.quantity -= 1
                await session.commit()
            else:
                await session.delete(item)
                await session.commit()
            await update_list_message(callback, item.list_id)
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_item_"))
async def toggle_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[2])
    async with get_session() as session:
        item = await session.get(ShoppingItem, item_id)
        if item:
            item.is_checked = not item.is_checked
            await session.commit()
            await update_list_message(callback, item.list_id)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_item_"))
async def delete_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[2])
    async with get_session() as session:
        item = await session.get(ShoppingItem, item_id)
        if item:
            list_id = item.list_id
            await session.delete(item)
            await session.commit()
            await update_list_message(callback, list_id)
    await callback.answer()


@router.callback_query(F.data.startswith("add_item_"))
async def add_item_prompt(callback: CallbackQuery, state: FSMContext):
    list_id = int(callback.data.split("_")[2])
    await state.update_data(current_list_id=list_id)
    await state.set_state(ShoppingStates.adding_item)
    await callback.message.edit_text(
        "📝 Введите название товара (можно с количеством, например «2 яйца»):"
    )
    await callback.answer()


@router.message(ShoppingStates.adding_item, F.text)
async def add_item_manual(message: Message, state: FSMContext):
    data = await state.get_data()
    list_id = data.get('current_list_id')
    text = message.text.strip()

    async with get_session() as session:
        parsed = parse_shopping_items(text)
        for name, qty, unit in parsed:
            item = ShoppingItem(
                list_id=list_id,
                name=name,
                quantity=qty,
                unit=unit,
                added_by=message.from_user.id
            )
            session.add(item)
        await session.commit()

    await state.clear()
    await update_list_message(message, list_id, is_callback=False)


@router.callback_query(F.data.startswith("delete_list_"))
async def delete_list(callback: CallbackQuery):
    list_id = int(callback.data.split("_")[2])
    async with get_session() as session:
        lst = await session.get(ShoppingList, list_id)
        if lst:
            lst.is_archived = True
            await session.commit()
    await callback.message.answer(
        "🗑️ Список архивирован.\n\nДля создания нового просто добавьте товары.",
        reply_markup=get_main_keyboard()
    )
    try:
        await callback.message.delete()
    except:
        pass
    await callback.answer()


@router.callback_query(F.data == "back_to_lists")
async def back_to_lists(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with get_session() as session:
        shopping_list = await get_or_create_default_list(user_id, session)
        if not shopping_list:
            await callback.message.edit_text("❌ Ошибка.")
            await callback.answer()
            return
        items_result = await session.execute(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == shopping_list.id)
            .order_by(ShoppingItem.is_checked, ShoppingItem.added_at)
        )
        items = items_result.scalars().all()

        text = f"📋 <b>{shopping_list.name}</b>\n\n"
        if items:
            checked = sum(1 for i in items if i.is_checked)
            total = len(items)
            text += f"✅ {checked}/{total}\n\n"
            for item in items:
                status = "✅" if item.is_checked else "⬜"
                text += f"{status} {item.name} — {item.quantity} {item.unit}\n"
        else:
            text += "Список пуст. Напишите товары, и я спрошу, куда их добавить."

        await callback.message.edit_text(
            text,
            reply_markup=get_shopping_items_keyboard(items, shopping_list.id),
            parse_mode="HTML"
        )
    await callback.answer()


async def update_list_message(event: CallbackQuery | Message, list_id: int, is_callback: bool = True):
    async with get_session() as session:
        lst = await session.get(ShoppingList, list_id)
        if not lst:
            text = "❌ Список не найден."
            if is_callback:
                await event.message.edit_text(text, reply_markup=get_main_keyboard())
            else:
                await event.answer(text, reply_markup=get_main_keyboard())
            return

        items_result = await session.execute(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == list_id)
            .order_by(ShoppingItem.is_checked, ShoppingItem.added_at)
        )
        items = items_result.scalars().all()

        text = f"📋 <b>{lst.name}</b>\n\n"
        if items:
            checked = sum(1 for i in items if i.is_checked)
            total = len(items)
            text += f"✅ {checked}/{total}\n\n"
            for item in items:
                status = "✅" if item.is_checked else "⬜"
                text += f"{status} {item.name} — {item.quantity} {item.unit}\n"
        else:
            text += "Список пуст. Напишите товары, и я спрошу, куда их добавить."

        reply_markup = get_shopping_items_keyboard(items, list_id)

        if is_callback:
            await event.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await event.answer(text, reply_markup=reply_markup, parse_mode="HTML")
