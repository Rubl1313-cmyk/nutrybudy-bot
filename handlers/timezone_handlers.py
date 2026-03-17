"""
Обработчики для выбора часового пояса пользователя
"""
import logging
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.timezone_keyboard import get_manual_timezone_keyboard, get_timezone_confirm_keyboard
from utils.timezone_utils import parse_timezone_input, get_timezone_display_name
from utils.states import ProfileStates

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.startswith("tz_"))
async def process_timezone_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора часового пояса из списка"""
    tz_data = callback.data[3:]  # Убираем "tz_"
    
    if tz_data == "manual_input":
        # Показываем клавиатуру для ручного ввода
        await callback.message.edit_text(
            "✏️ <b>Ручной ввод часового пояса</b>\n\n"
            "Выберите смещение от UTC или введите в формате UTC+3:",
            reply_markup=get_manual_timezone_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(ProfileStates.waiting_for_timezone)
        await callback.answer()
        
    elif tz_data.startswith("UTC"):
        # Выбрали смещение (UTC+3, UTC-5 и т.д.)
        display_name = get_timezone_display_name(tz_data)
        await callback.message.edit_text(
            f"🕐 <b>Подтвердите выбор</b>\n\n"
            f"Вы выбрали часовой пояс: {display_name}\n\n"
            "Всё верно?",
            reply_markup=get_timezone_confirm_keyboard(tz_data, display_name),
            parse_mode="HTML"
        )
        await callback.answer()
        
    else:
        # Выбрали город из списка
        display_name = get_timezone_display_name(tz_data)
        await callback.message.edit_text(
            f"🕐 <b>Подтвердите выбор</b>\n\n"
            f"Вы выбрали часовой пояс: {display_name}\n\n"
            "Всё верно?",
            reply_markup=get_timezone_confirm_keyboard(tz_data, display_name),
            parse_mode="HTML"
        )
        await callback.answer()

@router.callback_query(F.data == "tz_back_to_cities")
async def back_to_cities(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору из городов"""
    from keyboards.timezone_keyboard import get_timezone_keyboard
    
    await callback.message.edit_text(
        "🕐 <b>Ваш часовой пояс:</b>\n\n"
        "Выберите ваш город из списка или введите смещение вручную (например, UTC+3).",
        reply_markup=get_timezone_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ProfileStates.timezone)
    await callback.answer()

@router.callback_query(F.data.startswith("tz_confirm_"))
async def confirm_timezone(callback: CallbackQuery, state: FSMContext):
    """Подтверждение выбора часового пояса"""
    tz_name = callback.data[12:]  # Убираем "tz_confirm_"
    
    # Сохраняем часовой пояс в данные профиля
    await state.update_data(timezone=tz_name)
    
    await callback.message.edit_text(
        f"✅ <b>Часовой пояс сохранен!</b>\n\n"
        f"Выбранный часовой пояс: {get_timezone_display_name(tz_name)}\n\n"
        "Теперь статистика будет учитываться по вашему местному времени!",
        parse_mode="HTML"
    )
    await callback.answer()
    
    # Продолжаем создание профиля
    await continue_profile_setup(callback.message, state)

@router.callback_query(F.data == "tz_change")
async def change_timezone(callback: CallbackQuery, state: FSMContext):
    """Изменение часового пояса"""
    from keyboards.timezone_keyboard import get_timezone_keyboard
    
    await callback.message.edit_text(
        "🕐 <b>Выберите другой часовой пояс:</b>\n\n"
        "Выберите ваш город из списка или введите смещение вручную:",
        reply_markup=get_timezone_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(ProfileStates.waiting_for_timezone)
async def process_manual_timezone(message: Message, state: FSMContext):
    """Обработка ручного ввода часового пояса"""
    text = message.text.strip()
    
    # Пытаемся распарсить ввод
    tz_name = parse_timezone_input(text)
    
    if tz_name:
        display_name = get_timezone_display_name(tz_name)
        await message.answer(
            f"🕐 <b>Подтвердите выбор</b>\n\n"
            f"Вы ввели часовой пояс: {display_name}\n\n"
            "Всё верно?",
            reply_markup=get_timezone_confirm_keyboard(tz_name, display_name),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ <b>Неверный формат</b>\n\n"
            "Пожалуйста, используйте формат UTC+3, UTC-5 или выберите из списка.\n\n"
            "Или нажмите '🔙 Назад к городам' для возврата к списку городов:",
            reply_markup=get_manual_timezone_keyboard(),
            parse_mode="HTML"
        )

async def continue_profile_setup(message: Message, state: FSMContext):
    """Продолжение настройки профиля после выбора часового пояса"""
    from handlers.profile import ask_measurement
    
    # Начинаем сбор антропометрических данных
    await ask_measurement(
        message, state,
        "Обхват шеи",
        ProfileStates.waiting_for_neck,
        "Измерьте на уровне щитовидного хряща. Лента должна прилегать, но не перетягивать.",
        25, 60
    )
