python
"""
Обработчик напоминаний.
Исправлено: уникальные callback_data для подтверждения + добавлена quick_create_reminder.
Добавлено: удаление напоминаний с подтверждением.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from datetime import datetime

from database.db import get_session
from database.models import User, Reminder
from keyboards.inline import (
    get_reminder_type_keyboard,
    get_days_keyboard,
    get_confirmation_keyboard,
    get_reminders_list_keyboard  # новая клавиатура
)
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import ReminderStates

router = Router()

# ========== ОСНОВНЫЕ ОБРАБОТЧИКИ ==========

@router.message(Command("reminders"))
@router.message(F.text == "🔔 Напоминания")
async def cmd_reminders(message: Message, state: FSMContext, user_id: int = None):
    """Показать напоминания."""
    await state.clear()
    if user_id is None:
        user_id = message.from_user.id

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await message.answer(
                "❌ Сначала настройте профиль через /set_profile",
                reply_markup=get_main_keyboard()
            )
            return

        result = await session.execute(
            select(Reminder).where(
                Reminder.user_id == user.id,
                Reminder.enabled == True
            )
        )
        reminders = result.scalars().all()

        if not reminders:
            # Если нет напоминаний, показываем только кнопку создания
            text = "🔔 <b>Напоминания</b>\n\nУ тебя пока нет активных напоминаний."
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="➕ Создать напоминание", callback_data="new_reminder")]]
            )
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
            return

        text = "🔔 <b>Твои напоминания:</b>"
        keyboard = get_reminders_list_keyboard(reminders)
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.message(F.text == "➕ Создать напоминание")
async def create_reminder_button(message: Message, state: FSMContext):
    """Начать создание напоминания."""
    await state.set_state(ReminderStates.choosing_type)
    await message.answer(
        "🔔 <b>Новое напоминание</b>\n\nВыберите тип:",
        reply_markup=get_reminder_type_keyboard()
    )

@router.callback_query(F.data == "new_reminder")
async def new_reminder_callback(callback: CallbackQuery, state: FSMContext):
    """Callback для создания нового напоминания."""
    await state.set_state(ReminderStates.choosing_type)
    await callback.message.edit_text(
        "🔔 <b>Новое напоминание</b>\n\nВыберите тип:",
        reply_markup=get_reminder_type_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("reminder_info_"))
async def reminder_info_callback(callback: CallbackQuery):
    """Показывает информацию о напоминании (просто уведомление)."""
    reminder_id = int(callback.data.split("_")[2])
    await callback.answer(f"ℹ️ Напоминание ID {reminder_id}", show_alert=False)

@router.callback_query(F.data.startswith("delete_reminder_"))
async def delete_reminder_callback(callback: CallbackQuery, state: FSMContext):
    """Запрашивает подтверждение удаления напоминания."""
    reminder_id = int(callback.data.split("_")[2])
    await state.update_data(reminder_to_delete=reminder_id)
    # Запрашиваем подтверждение
    await callback.message.edit_text(
        "❓ Вы уверены, что хотите удалить это напоминание?",
        reply_markup=get_confirmation_keyboard("reminder_delete")
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_reminder_delete")
async def confirm_delete_reminder(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления."""
    data = await state.get_data()
    reminder_id = data.get('reminder_to_delete')
    if not reminder_id:
        await callback.answer("❌ Ошибка: напоминание не найдено", show_alert=True)
        return

    async with get_session() as session:
        reminder = await session.get(Reminder, reminder_id)
        if reminder and reminder.user.telegram_id == callback.from_user.id:
            # Помечаем как неактивное (мягкое удаление)
            reminder.enabled = False
            await session.commit()
            await callback.answer("✅ Напоминание удалено", show_alert=False)
        else:
            await callback.answer("❌ Напоминание не найдено или доступ запрещён", show_alert=True)
            return

    # Обновляем список напоминаний
    await state.clear()
    # Перезапускаем показ напоминаний
    await cmd_reminders(callback.message, state, user_id=callback.from_user.id)

@router.callback_query(F.data == "cancel_reminder_delete")
async def cancel_delete_reminder(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления."""
    await state.clear()
    # Возвращаемся к списку
    await cmd_reminders(callback.message, state, user_id=callback.from_user.id)


@router.callback_query(F.data.startswith("reminder_"), ReminderStates.choosing_type)
async def process_reminder_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа напоминания."""
    rem_type = callback.data.split("_")[1]
    await state.update_data(type=rem_type)

    title_map = {
        "meal": "🍽️ Приём пищи",
        "water": "💧 Выпить воды",
        "weight": "⚖️ Взвешивание",
        "custom": "📝 Своё напоминание"
    }

    if rem_type == "custom":
        await state.set_state(ReminderStates.entering_title)
        await callback.message.edit_text("📝 Введите текст напоминания:")
    else:
        await state.update_data(title=title_map.get(rem_type, "Напоминание"))
        await state.set_state(ReminderStates.entering_time)
        await callback.message.edit_text(
            f"✅ Тип: <b>{title_map[rem_type]}</b>\n\n"
            "⏰ Введите время в формате ЧЧ:ММ (например, 09:00):"
        )
    await callback.answer()


@router.message(ReminderStates.entering_title, F.text)
async def process_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    await state.set_state(ReminderStates.entering_time)
    await message.answer(
        f"✅ Текст: <b>{title}</b>\n\n"
        "⏰ Введите время в формате ЧЧ:ММ:"
    )


@router.message(ReminderStates.entering_time, F.text)
async def process_time(message: Message, state: FSMContext):
    time = message.text.strip()
    try:
        hours, minutes = map(int, time.split(":"))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError
    except:
        await message.answer("❌ Введите время в формате ЧЧ:ММ (например, 09:00)")
        return
    await state.update_data(time=time)
    await state.set_state(ReminderStates.choosing_days)
    await message.answer(
        f"✅ Время: <b>{time}</b>\n\n"
        "📅 Выберите дни:",
        reply_markup=get_days_keyboard()
    )


@router.callback_query(F.data.startswith("day_"), ReminderStates.choosing_days)
async def process_days(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    days_map = {
        "mon": "Пн", "tue": "Вт", "wed": "Ср", "thu": "Чт",
        "fri": "Пт", "sat": "Сб", "sun": "Вс", "daily": "Ежедневно"
    }
    if day == "daily":
        await state.update_data(days="daily")
    else:
        await state.update_data(days=day)

    await state.set_state(ReminderStates.confirming)
    data = await state.get_data()
    await callback.message.edit_text(
        "✅ <b>Подтверждение</b>\n\n"
        f"🔔 {data['title']}\n"
        f"⏰ {data['time']}\n"
        f"📅 {days_map.get(day, day)}\n\n"
        "Создать напоминание?",
        reply_markup=get_confirmation_keyboard("reminder")
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_reminder", ReminderStates.confirming)
async def confirm_reminder(callback: CallbackQuery, state: FSMContext):
    """Сохранение напоминания."""
    data = await state.get_data()
    telegram_id = callback.from_user.id

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await callback.answer("❌ Профиль не найден", show_alert=True)
            await state.clear()
            return

        reminder = Reminder(
            user_id=user.id,
            type=data['type'],
            title=data['title'],
            time=data['time'],
            days=data['days'],
            enabled=True
        )
        session.add(reminder)
        await session.commit()

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Напоминание создано!</b>\n\n"
        f"🔔 {data['title']} в {data['time']} ({data['days']})"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_reminder", ReminderStates.confirming)
async def cancel_reminder(callback: CallbackQuery, state: FSMContext):
    """Отмена создания."""
    await state.clear()
    await callback.message.edit_text("❌ Создание отменено.")
    await callback.answer()


# ========== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ БЫСТРОГО СОЗДАНИЯ ==========

async def quick_create_reminder(telegram_id: int, title: str, time: str, days: str = "daily") -> bool:
    """Быстрое создание напоминания без диалога."""
    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return False

        reminder = Reminder(
            user_id=user.id,
            type="custom",
            title=title,
            time=time,
            days=days,
            enabled=True
        )
        session.add(reminder)
        await session.commit()
        return True
