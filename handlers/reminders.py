from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import get_session
from database.models import Reminder
from sqlalchemy import select
from keyboards.reply import get_main_keyboard
from utils.states import ReminderStates

router = Router()

@router.message(Command("reminders"))
async def list_reminders(message: Message):
    user_id = message.from_user.id
    async with get_session() as session:
        result = await session.execute(
            select(Reminder).where(Reminder.user_id == user_id)
        )
        reminders = result.scalars().all()
        
        if not reminders:
            await message.answer(
                "🔔 У вас нет напоминаний.\n\n"
                "Используйте /add_reminder для создания."
            )
        else:
            text = "🔔 <b>Ваши напоминания:</b>\n\n"
            for r in reminders:
                status = "✅" if r.enabled else "❌"
                text += f"{status} {r.title} — {r.time} ({r.days})\n"
            await message.answer(text, parse_mode="HTML")

@router.message(Command("add_reminder"))
async def add_reminder(message: Message, state: FSMContext):
    await state.set_state(ReminderStates.entering_title)
    await message.answer("🔔 Введите название напоминания:")

@router.message(ReminderStates.entering_title, F.text)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ReminderStates.entering_time)
    await message.answer("⏰ Введите время в формате ЧЧ:ММ (например, 09:00):")

@router.message(ReminderStates.entering_time, F.text)
async def process_time(message: Message, state: FSMContext):
    time = message.text.strip()
    if len(time) != 5 or time[2] != ':':
        await message.answer("❌ Неверный формат. Используйте ЧЧ:ММ")
        return
    
    await state.update_data(time=time)
    await state.set_state(ReminderStates.choosing_days)
    await message.answer("📅 Выберите дни (отправьте команду /daily для ежедневно):")

@router.message(ReminderStates.choosing_days, F.text)
async def process_days(message: Message, state: FSMContext):
    days = message.text.lower()
    if days == '/daily':
        days = 'daily'
    
    data = await state.get_data()
    
    async with get_session() as session:
        reminder = Reminder(
            user_id=message.from_user.id,
            type='custom',
            title=data['title'],
            time=data['time'],
            days=days
        )
        session.add(reminder)
        await session.commit()
    
    await state.clear()
    await message.answer(f"✅ Напоминание '{data['title']}' создано!", reply_markup=get_main_keyboard())