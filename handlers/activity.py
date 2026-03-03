"""
Обработчик активности для NutriBuddy.
✅ Для ходьбы ввод количества шагов, для остальных типов – по времени.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from database.db import get_session
from database.models import User, Activity
from keyboards.inline import get_activity_type_keyboard, get_confirmation_keyboard
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from utils.states import ActivityStates

router = Router()

# 🔥 Калории на минуту для разных активностей (кроме ходьбы)
CALORIES_PER_MINUTE = {
    "running": 10,
    "cycling": 7,
    "gym": 6,
    "yoga": 3,
    "swimming": 8,
    "other": 5
}

# 🔥 Для ходьбы расчёт по шагам: 1 шаг ~ 0.04 ккал (среднее)
CALORIES_PER_STEP = 0.04


@router.message(Command("fitness"))
@router.message(F.text == "🏋️ Активность")
async def cmd_fitness(message: Message, state: FSMContext):
    """Начало записи активности"""
    await state.clear()
    await state.set_state(ActivityStates.manual_type)
    await message.answer(
        "🏋️ <b>Запись активности</b>\n\n"
        "Выберите тип активности:",
        reply_markup=get_activity_type_keyboard()
    )


@router.callback_query(F.data.startswith("activity_"), ActivityStates.manual_type)
async def process_activity_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа активности"""
    act_type = callback.data.split("_")[1]
    await state.update_data(activity_type=act_type)

    type_names = {
        "walking": "🚶 Ходьба",
        "running": "🏃 Бег",
        "cycling": "🚴 Велосипед",
        "gym": "🏋️ Тренажёрный зал",
        "yoga": "🧘 Йога",
        "swimming": "🏊 Плавание",
        "other": "🎾 Другое"
    }

    # Если выбран тип "walking" – запрашиваем шаги
    if act_type == "walking":
        await state.set_state(ActivityStates.manual_steps)
        await callback.message.edit_text(
            f"✅ Тип: <b>{type_names[act_type]}</b>\n\n"
            "👣 <b>Сколько шагов вы прошли?</b>\n"
            "Введите количество шагов (целое число):\n"
            "<i>Пример: 5000</i>",
            parse_mode="HTML"
        )
    else:
        # Для остальных – запрашиваем длительность
        await state.set_state(ActivityStates.manual_duration)
        await callback.message.edit_text(
            f"✅ Тип: <b>{type_names[act_type]}</b>\n\n"
            "⏱️ <b>Сколько длилась тренировка?</b>\n"
            "Введите длительность в минутах:\n"
            "<i>Пример: 30, 45, 60</i>",
            parse_mode="HTML"
        )
    await callback.answer()


# ========== ОБРАБОТКА ШАГОВ (ДЛЯ ХОДЬБЫ) ==========
@router.message(ActivityStates.manual_steps, F.text)
async def process_steps(message: Message, state: FSMContext):
    """Ввод количества шагов для ходьбы"""
    try:
        steps = int(message.text.strip())
        if steps <= 0 or steps > 100000:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите целое положительное число от 1 до 100000")
        return

    # Рассчитываем калории
    calories = steps * CALORIES_PER_STEP

    await state.update_data(
        steps=steps,
        calories=calories,
        duration=0,
        distance=0
    )
    await state.set_state(ActivityStates.confirming)

    data = await state.get_data()
    await message.answer(
        "✅ <b>Подтверждение</b>\n\n"
        f"🚶 Ходьба\n"
        f"👣 Шаги: {steps}\n"
        f"🔥 Сожжено: {calories:.1f} ккал\n\n"
        "Всё верно?",
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )


# ========== ОБРАБОТКА ДЛИТЕЛЬНОСТИ (ДЛЯ ОСТАЛЬНЫХ) ==========
@router.message(ActivityStates.manual_duration, F.text.regexp(r'^\s*\d+\s*$'))
async def process_duration(message: Message, state: FSMContext):
    """Ввод длительности для активности (не ходьба)"""
    try:
        duration = int(message.text.strip())
        if not 1 <= duration <= 480:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите число от 1 до 480 минут")
        return

    data = await state.get_data()
    act_type = data.get('activity_type', 'other')

    # Рассчитываем калории на основе длительности
    calories_per_min = CALORIES_PER_MINUTE.get(act_type, 5)
    calories = duration * calories_per_min

    await state.update_data(duration=duration, calories=calories)
    await state.set_state(ActivityStates.manual_distance)

    await message.answer(
        f"✅ Длительность: <b>{duration} мин</b>\n"
        f"🔥 Примерно: <b>{calories} ккал</b>\n\n"
        "📍 <b>Дистанция (км)</b>\n"
        "Введите дистанцию или 0, если не применимо:\n"
        "<i>Пример: 5, 10.5, 0</i>",
        parse_mode="HTML"
    )


@router.message(ActivityStates.manual_duration)  # Fallback для нечислового ввода
async def process_duration_fallback(message: Message):
    await message.answer("❌ Введите целое число (количество минут)")


@router.message(ActivityStates.manual_distance, F.text.regexp(r'^\s*\d+([.,]\d+)?\s*$'))
async def process_distance(message: Message, state: FSMContext):
    """Ввод дистанции"""
    try:
        distance = float(message.text.replace(',', '.').strip())
        if not 0 <= distance <= 200:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите число от 0 до 200 км")
        return

    await state.update_data(distance=distance)
    await state.set_state(ActivityStates.confirming)

    data = await state.get_data()
    act_type = data['activity_type']
    type_names = {
        "walking": "🚶 Ходьба",
        "running": "🏃 Бег",
        "cycling": "🚴 Велосипед",
        "gym": "🏋️ Тренажёрный зал",
        "yoga": "🧘 Йога",
        "swimming": "🏊 Плавание",
        "other": "🎾 Другое"
    }

    await message.answer(
        "✅ <b>Подтверждение</b>\n\n"
        f"🏃 {type_names.get(act_type, act_type)}\n"
        f"⏱️ {data['duration']} мин\n"
        f"📍 {distance:.1f} км\n"
        f"🔥 {data['calories']:.0f} ккал\n\n"
        "Всё верно?",
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )


@router.message(ActivityStates.manual_distance)  # Fallback
async def process_distance_fallback(message: Message):
    await message.answer("❌ Введите число (километры)")


# ========== ОБРАБОТКА ПОДТВЕРЖДЕНИЯ ==========
@router.callback_query(F.data == "confirm", ActivityStates.confirming)
async def confirm_activity(callback: CallbackQuery, state: FSMContext):
    """Сохранение активности"""
    data = await state.get_data()
    user_id = callback.from_user.id

    async with get_session() as session:
        # Получаем пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            await callback.message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        activity = Activity(
            user_id=user.id,
            activity_type=data['activity_type'],
            duration=data.get('duration', 0),
            distance=data.get('distance', 0),
            calories_burned=data['calories'],
            steps=data.get('steps', 0),
            datetime=datetime.now(),
            source='manual'
        )
        session.add(activity)
        await session.commit()

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Активность записана!</b>\n\n"
        f"🔥 Сожжено: {data['calories']:.0f} ккал",
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", ActivityStates.confirming)
async def cancel_activity(callback: CallbackQuery, state: FSMContext):
    """Отмена"""
    await state.clear()
    await callback.message.edit_text("❌ Запись отменена.")
    await callback.answer()
