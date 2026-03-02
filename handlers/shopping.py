"""
Обработчик списков покупок.
Теперь:
- Единый список "Покупки" (создаётся автоматически).
- Любой текст добавляет товары (с парсингом количества).
- Инлайн-кнопки для изменения количества и отметки.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.db import get_session
from database.models import User, ShoppingList, ShoppingItem
from keyboards.inline import get_shopping_items_keyboard
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.parsers import parse_shopping_items
from utils.states import ShoppingStates

router = Router()


async def get_or_create_default_list(user_id: int, session):
    """Возвращает основной список покупок пользователя (создаёт если нет)."""
    # Сначала получаем внутренний id пользователя
    user_result = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        return None

    # Ищем существующий неархивированный список
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
        # Создаём новый список с именем "Покупки"
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

        # Загружаем товары с сортировкой
        items_result = await session.execute(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == shopping_list.id)
            .order_by(ShoppingItem.is_checked, ShoppingItem.added_at)
        )
        items = items_result.scalars().all()

        if not items:
            text = f"📋 <b>{shopping_list.name}</b>\n\nСписок пуст. Отправьте товары (например: «яблоки, 2 литра молока»)."
        else:
            text = f"📋 <b>{shopping_list.name}</b>\n\n"
            checked = sum(1 for i in items if i.is_checked)
            total = len(items)
            text += f"✅ {checked}/{total}\n\n"
            for i, item in enumerate(items, 1):
                status = "✅" if item.is_checked else "⬜"
                text += f"{status} {item.name} — {item.quantity} {item.unit}\n"

        await message.answer(
            text,
            reply_markup=get_shopping_items_keyboard(items, shopping_list.id),
            parse_mode="HTML"
        )


@router.message(F.text, ~F.text.startswith("/"), 
                ~F.text.in_({
                    "🏠 Главное меню", 
                    "❌ Отмена", 
                    "📖 План питания", 
                    "🔄 Предложить другой вариант", 
                    "🍽️ Показать рецепты"
                }))
async def add_items_from_text(message: Message, state: FSMContext):
    """Добавляет товары в основной список из произвольного текста."""
    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        return

    async with get_session() as session:
        shopping_list = await get_or_create_default_list(user_id, session)
        if not shopping_list:
            await message.answer("❌ Ошибка: не удалось создать список.")
            return

        parsed = parse_shopping_items(text)
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

        # Обновляем отображение списка
        items_result = await session.execute(
            select(ShoppingItem)
            .where(ShoppingItem.list_id == shopping_list.id)
            .order_by(ShoppingItem.is_checked, ShoppingItem.added_at)
        )
        items = items_result.scalars().all()

        text = f"📋 <b>{shopping_list.name}</b>\n\n"
        checked = sum(1 for i in items if i.is_checked)
        total = len(items)
        text += f"✅ {checked}/{total}\n\n"
        for i, item in enumerate(items, 1):
            status = "✅" if item.is_checked else "⬜"
            text += f"{status} {item.name} — {item.quantity} {item.unit}\n"

        await message.answer(
            text,
            reply_markup=get_shopping_items_keyboard(items, shopping_list.id),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("item_incr_"))
async def increase_quantity(callback: CallbackQuery):
    """Увеличить количество товара на 1."""
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
    """Уменьшить количество товара на 1. Если станет 0, товар удаляется."""
    item_id = int(callback.data.split("_")[2])
    async with get_session() as session:
        item = await session.get(ShoppingItem, item_id)
        if item:
            if item.quantity > 1:
                item.quantity -= 1
                await session.commit()
            else:
                # Удаляем товар
                await session.delete(item)
                await session.commit()
            await update_list_message(callback, item.list_id)
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_item_"))
async def toggle_item(callback: CallbackQuery):
    """Отметить/снять отметку товара."""
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
    """Удалить товар из списка."""
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
    """Начать добавление товара вручную."""
    list_id = int(callback.data.split("_")[2])
    await state.update_data(current_list_id=list_id)
    await state.set_state(ShoppingStates.adding_item)
    await callback.message.edit_text(
        "📝 Введите название товара (можно с количеством, например «2 яйца»):"
    )
    await callback.answer()


@router.message(ShoppingStates.adding_item, F.text)
async def add_item_manual(message: Message, state: FSMContext):
    """Добавить один товар вручную."""
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
    # Возвращаемся к списку
    await update_list_message(message, list_id, is_callback=False)


@router.callback_query(F.data.startswith("delete_list_"))
async def delete_list(callback: CallbackQuery):
    """Архивировать текущий список."""
    list_id = int(callback.data.split("_")[2])
    async with get_session() as session:
        lst = await session.get(ShoppingList, list_id)
        if lst:
            lst.is_archived = True
            await session.commit()
    await callback.message.edit_text(
        "🗑️ Список архивирован.\n"
        "Для создания нового просто добавьте товары.",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_lists")
async def back_to_lists(callback: CallbackQuery):
    """Вернуться к главному списку (по сути то же, что и /shopping)."""
    # Создаём имитацию команды /shopping
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
            for i, item in enumerate(items, 1):
                status = "✅" if item.is_checked else "⬜"
                text += f"{status} {item.name} — {item.quantity} {item.unit}\n"
        else:
            text += "Список пуст. Отправьте товары (например: «яблоки, 2 литра молока»)."

        await callback.message.edit_text(
            text,
            reply_markup=get_shopping_items_keyboard(items, shopping_list.id),
            parse_mode="HTML"
        )
    await callback.answer()


async def update_list_message(event: CallbackQuery | Message, list_id: int, is_callback: bool = True):
    """Обновить сообщение со списком после изменений."""
    async with get_session() as session:
        # Получаем список
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
            for i, item in enumerate(items, 1):
                status = "✅" if item.is_checked else "⬜"
                text += f"{status} {item.name} — {item.quantity} {item.unit}\n"
        else:
            text += "Список пуст. Отправьте товары (например: «яблоки, 2 литра молока»)."

        reply_markup = get_shopping_items_keyboard(items, list_id)

        if is_callback:
            await event.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await event.answer(text, reply_markup=reply_markup, parse_mode="HTML")
