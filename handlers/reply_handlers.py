"""
handlers/reply_handlers.py
Обработчики для новых reply-кнопок (исправленные фильтры с эмодзи)
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.profile import cmd_profile
from handlers.progress import cmd_progress
from handlers.drinks import cmd_water
from handlers.weight import cmd_weight
from handlers.ai_assistant import cmd_ask
from handlers.common import cmd_help
from keyboards.reply_v2 import get_main_keyboard_v2

logger = logging.getLogger(__name__)
router = Router()

# === Основные кнопки ===

@router.message(F.text.lower().in_(["🍽️ записать еду", "записать еду"]))
async def food_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Food button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.common import cmd_food
    await cmd_food(message, state)

@router.message(F.text.lower().in_(["💧 вода", "вода"]))
async def water_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Water button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.drinks import cmd_water
    await cmd_water(message, state)

@router.message(F.text.lower().in_(["📊 прогресс", "прогресс"]))
async def progress_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Progress button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.progress import cmd_progress
    await cmd_progress(message, state)

@router.message(F.text.lower().in_(["🤖 ai ассистент", "ai ассистент"]))
async def ai_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: AI button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.ai_assistant import cmd_ask
    await cmd_ask(message, state)


@router.message(F.text.lower().regexp(r'^(профиль|👤 профиль)$'))
async def profile_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Profile button pressed by user {message.from_user.id}")
    # Вызываем команду показа профиля – она сама отправит нужное сообщение
    await cmd_profile(message, state)

@router.message(F.text.lower().in_(["помощь", "❓ помощь"]))
async def help_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Help button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_help(message, state)

# === Новые кнопки премиум меню ===

@router.message(F.text.lower().in_(["🏆 достижения", "достижения"]))
async def achievements_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Achievements button pressed by user {message.from_user.id}")
    await state.clear()
    from handlers.achievements import cmd_achievements
    await cmd_achievements(message)

# === Дополнительные кнопки (опционально) ===

@router.message(F.text.lower().in_(["⚖️ записать вес", "записать вес"]))
async def weight_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Weight button pressed by user {message.from_user.id}")
    await state.clear()
    await cmd_weight(message, state)  # Вызываем реальную команду веса с state

@router.message(F.text.lower().in_(["🏃 записать активность", "записать активность"]))
async def activity_button_handler(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Activity button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "🏃‍♂️ <b>Записать активность</b>\n\n"
        "Опишите активность (например: «бег 30 минут»).",
        parse_mode="HTML"
    )

# === Навигация ===

@router.message(F.text.lower().in_(["📸 фото еды", "фото еды"]))
async def photo_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки фото еды"""
    logger.info(f"🔍 REPLY HANDLER: Photo food button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "📸 <b>Отправьте фото блюда</b>\n\n"
        "AI распознает:\n"
        "• Ингредиенты и их количество\n"
        "• Калорийность и БЖУ\n"
        "• Тип приема пищи\n\n"
        "📸 Сделайте четкое фото сверху или сбоку",
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["✏️ текстом", "текстом"]))
async def text_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки текстового ввода еды"""
    logger.info(f"🔍 REPLY HANDLER: Text food button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "✏️ <b>Опишите что вы съели</b>\n\n"
        "Форматы:\n"
        "• «Гречка с курицей 200г»\n"
        "• «Салат Цезарь 150г»\n"
        "• «Яблоко 1 шт»\n"
        "• «Кофе с молоком 250мл»\n\n"
        "🔍 Укажите название и вес/количество",
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["⚡ быстрый ввод", "быстрый ввод"]))
async def quick_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки быстрого ввода еды"""
    logger.info(f"🔍 REPLY HANDLER: Quick food button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "⚡ <b>Быстрый ввод</b>\n\n"
        "Напишите что вы съели:\n"
        "• гречка 200г\n"
        "• курица 150г\n"
        "• салат 100г\n"
        "• банан 1шт\n\n"
        "🚀 Я сам определю тип приема пищи и рассчитаю КБЖУ",
        parse_mode="HTML"
    )

# === Callback обработчики для inline кнопок ===

@router.callback_query(F.data.startswith("water_"))
async def water_quick_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка быстрых кнопок воды"""
    logger.info(f"🔍 REPLY HANDLER: Water quick callback: {callback.data}")

    try:
        # Извлекаем объем из callback_data
        amount = int(callback.data.split("_")[1])
        user_id = callback.from_user.id

        # Сохраняем воду
        from handlers.drinks import process_quick_water
        await process_quick_water(callback.message, amount)

        await callback.answer(f"💧 Записано {amount} мл воды")

    except Exception as e:
        logger.error(f"Error in water quick callback: {e}")
        await callback.answer("❌ Ошибка записи воды", show_alert=True)

@router.callback_query(F.data.startswith("meal_"))
async def meal_type_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа приема пищи"""
    logger.info(f"🔍 REPLY HANDLER: Meal type callback: {callback.data}")

    try:
        meal_type = callback.data.split("_")[1]
        meal_type_names = {
            "breakfast": "🥐 Завтрак",
            "lunch": "🍽️ Обед",
            "dinner": "🍽️ Ужин",
            "snack": "🥨 Перекус"
        }

        meal_name = meal_type_names.get(meal_type, "🍽️ Прием пищи")

        # Сохраняем тип приема пищи в state для последующего использования
        await state.set_data({"meal_type": meal_type})

        await callback.message.edit_text(
            f"{meal_name} выбран!\n\n"
            f"Теперь отправьте фото или опишите что вы съели.",
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in meal type callback: {e}")
        await callback.answer("❌ Ошибка выбора типа", show_alert=True)

@router.message(F.text.lower().in_(["🏠 главное меню", "главное меню"]))
async def back_to_main_menu(message: Message, state: FSMContext):
    logger.info(f"🔍 REPLY HANDLER: Main menu button pressed by user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )
