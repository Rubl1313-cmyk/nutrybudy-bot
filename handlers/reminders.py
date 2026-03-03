
"""
Обработчик напоминаний
✅ Проверка пользователя, обработка confirm/cancel
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.db import get_session
from database.models import User, Reminder
from keyboards.inline import (
    get_reminder_type_keyboard,
    get_days_keyboard,
    get_confirmation_keyboard
)
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import ReminderStates

router = Router()


@router.message(Command("reminders"))
@router.message(F.text == "🔔 Напоминания")
async def cmd_reminders(message: Message, state: FSMContext):
    """Показать напоминания"""
    await state.clear()
    telegram_id = message.from_user.id

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
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

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Создать напоминание")],
                [KeyboardButton(text="🏠 Главное меню")]
            ],
            resize_keyboard=True
        )

        if not reminders:
            await message.answer(
                "🔔 <b>Напоминания</b>\n\n"
                "У тебя пока нет активных напоминаний.\n\n"
                "Нажми ➕ Создать напоминание",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            return

        text = "🔔 <b>Твои напоминания:</b>\n\n"
        for rem in reminders:
            text += f"• {rem.title} — {rem.time} ({rem.days})\n"
        text += "\n<i>Нажми ➕ чтобы добавить ещё</i>"

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text == "➕ Создать напоминание")
async def create_reminder_button(message: Message, state: FSMContext):
    """Начать создание напоминания"""
    await state.set_state(ReminderStates.choosing_type)
    await message.answer(
        "🔔 <b>Новое напоминание</b>\n\nВыберите тип:",
        reply_markup=get_reminder_type_keyboard()
    )


@router.callback_query(F.data == "new_reminder")
async def new_reminder_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReminderStates.choosing_type)
    await callback.message.edit_text(
        "🔔 <b>Новое напоминание</b>\n\nВыберите тип:",
        reply_markup=get_reminder_type_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reminder_"), ReminderStates.choosing_type)
async def process_reminder_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа напоминания"""
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
        reply_markup=get_confirmation_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "confirm", ReminderStates.confirming)
async def confirm_reminder(callback: CallbackQuery, state: FSMContext):
    """Сохранение напоминания"""
    data = await state.get_data()
    telegram_id = callback.from_user.id

    async with get_session() as session:
        # Получаем пользователя по telegram_id
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


@router.callback_query(F.data == "cancel", ReminderStates.confirming)
async def cancel_reminder(callback: CallbackQuery, state: FSMContext):
    """Отмена создания"""
    await state.clear()
    await callback.message.edit_text("❌ Создание отменено.")
    await callback.answer()

async def quick_create_reminder(telegram_id: int, title: str, time: str, days: str = "daily"):
    """Быстрое создание напоминания без диалога."""
    from database.db import get_session
    from database.models import User, Reminder
    from sqlalchemy import select

    async with get_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return
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
