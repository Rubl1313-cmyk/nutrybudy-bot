from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.db import get_session
from database.models import ShoppingList, ShoppingItem
from keyboards.inline import get_shopping_lists_keyboard, get_shopping_items_keyboard
from keyboards.reply import get_main_keyboard
from utils.states import ShoppingStates

router = Router()


@router.message(Command("shopping"))
@router.message(F.text == "📋 Списки покупок")
async def cmd_shopping(message: Message, state: FSMContext):
    await state.clear()
    
    user_id = message.from_user.id
    
    async with get_session() as session:
        result = await session.execute(
            select(ShoppingList).where(
                ShoppingList.user_id == user_id,
                ShoppingList.is_archived == False
            )
        )
        lists = result.scalars().all()
        
        if not lists:
            await message.answer(
                "📋 <b>Списки покупок</b>\n\n"
                "У тебя пока нет списков.\n\n"
                "Нажми ➕ Новый список, чтобы создать первый!",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            return
        
        await message.answer(
            "📋 <b>Твои списки:</b>",
            reply_markup=get_shopping_lists_keyboard(lists),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "new_shopping_list")
async def new_list(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ShoppingStates.creating_list)
    await callback.message.edit_text(
        "📝 <b>Новый список</b>\n\nВведи название:"
    )
    await callback.answer()


@router.message(ShoppingStates.creating_list, F.text)
async def create_list(message: Message, state: FSMContext):
    name = message.text.strip()
    user_id = message.from_user.id
    
    async with get_session() as session:
        new_list = ShoppingList(user_id=user_id, name=name)
        session.add(new_list)
        await session.commit()
    
    await state.clear()
    
    await message.answer(
        f"✅ <b>Список '{name}' создан!</b>",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("shopping_list_"))
async def view_list(callback: CallbackQuery):
    try:
        list_id = int(callback.data.split("_")[2])
        
        async with get_session() as session:
            result = await session.execute(
                select(ShoppingList).where(ShoppingList.id == list_id)
            )
            lst = result.scalar_one_or_none()
            
            if not lst:
                await callback.answer("❌ Список не найден", show_alert=True)
                return
            
            items_result = await session.execute(
                select(ShoppingItem).where(ShoppingItem.list_id == list_id)
            )
            items = items_result.scalars().all()
            
            if not items:
                text = f"📋 <b>{lst.name}</b>\n\nПусто. Добавь товары!"
            else:
                text = f"📋 <b>{lst.name}</b>\n\n"
                for item in items:
                    status = "✅" if item.is_checked else "⬜"
                    text += f"{status} {item.name} — {item.quantity}\n"
            
            await callback.message.edit_text(
                text,
                reply_markup=get_shopping_items_keyboard(items, list_id),
                parse_mode="HTML"
            )
            
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_item_"))
async def toggle_item(callback: CallbackQuery):
    try:
        item_id = int(callback.data.split("_")[2])
        
        async with get_session() as session:
            item = await session.get(ShoppingItem, item_id)
            if item:
                item.is_checked = not item.is_checked
                await session.commit()
        
        await view_list(callback)
        
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("delete_list_"))
async def delete_list(callback: CallbackQuery):
    try:
        list_id = int(callback.data.split("_")[2])
        
        async with get_session() as session:
            lst = await session.get(ShoppingList, list_id)
            if lst:
                lst.is_archived = True
                await session.commit()
        
        await callback.message.edit_text(
            "🗑️ Список архивирован",
            reply_markup=get_main_keyboard()
        )
        
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка", show_alert=True)
    
    await callback.answer()
