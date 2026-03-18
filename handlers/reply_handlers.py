"""
handlers/reply_handlers.py
Обработчики для новых reply-кнопок
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.reply_v2 import get_main_keyboard_v2, get_activity_keyboard, get_progress_keyboard, get_water_keyboard, get_cancel_keyboard, get_confirm_keyboard, get_settings_keyboard, get_statistics_keyboard, get_back_keyboard, get_food_keyboard
from services.tool_caller import ToolCaller

logger = logging.getLogger(__name__)
router = Router()

# Обработчики для основных кнопок

@router.message(F.text.contains("Записать приём пищи"))
async def food_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🍽️ <b>Записать приём пищи</b>\n\n"
        "Напишите, что вы съели, или отправьте фото блюда.",
        reply_markup=get_food_keyboard(),
        parse_mode="HTML"
    )
    
@router.message(F.text.contains("Записать воду"))
async def water_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "💧 <b>Записать воду</b>\n\n"
        "Выберите объем:",
        reply_markup=get_water_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("Записать активность"))
async def activity_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "🏃‍♂️ <b>Записать активность</b>\n\n"
        "Выберите тип активности:",
        reply_markup=get_activity_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("⚖️ Вес"))
async def weight_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "⚖️ <b>Записать вес</b>\n\n"
        "Введите ваш вес в кг (например: 70.5):\n\n"
        "💡 <b>Совет:</b> Взвешивайтесь утром натощак для точных результатов.",
        parse_mode="HTML"
    )

@router.message(F.text.contains("Мой прогресс"))
async def progress_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "� <b>Ваш прогресс</b>\n\n"
        "Выберите период для просмотра:",
        reply_markup=get_progress_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("🍽️ План питания"))
async def meal_plan_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "🍽️ <b>План питания</b>\n\n"
        "Хотите составить персонализированный план питания?\n\n"
        "📋 <b>Что будет включено:</b>\n"
        "• Рекомендации по калориям\n"
        "• Баланс БЖУ\n"
        "• Время приемов пищи\n"
        "• Предпочтения в еде\n"
        "• Аллергии и ограничения\n\n"
        "🚀 <b>Начать составление плана?</b>",
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("🏆 Достижения"))
async def achievements_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏆 <b>Ваши достижения</b>\n\n"
        "Загружаю ваши достижения...",
        parse_mode="HTML"
    )
    
    # Здесь будет логика загрузки достижений
    # from handlers.achievements import cmd_achievements
    # await cmd_achievements(message)

@router.message(F.text.contains("🤖 AI ассистент"))
async def ai_assistant_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🤖 <b>AI Ассистент NutriBuddy</b>\n\n"
        "Я ваш персональный помощник по питанию и фитнесу!\n\n"
        "📝 <b>Что я могу помочь:</b>\n"
        "• Рассчитать калорийность блюд\n"
        "• Дать рекомендации по питанию\n"
        "• Подсказать упражнения\n"
        "• Ответить на вопросы о здоровье\n"
        "• Помочь с выбором продуктов\n\n"
        "💬 <b>Задайте ваш вопрос:</b>",
        parse_mode="HTML"
    )

@router.message(F.text.contains("👤 Профиль"))
async def profile_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👤 <b>Ваш профиль</b>\n\n"
        "Загружаю информацию о профиле...",
        parse_mode="HTML"
    )
    
    # Здесь будет логика загрузки профиля
    # from handlers.profile import cmd_profile
    # await cmd_profile(message)

@router.message(F.text.contains("⚙️ Настройки"))
async def settings_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Выберите раздел:",
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )

# Обработчики для быстрых действий

@router.message(F.text.contains("📸 Распознать еду"))
async def photo_recognition_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📸 <b>Распознавание еды по фото</b>\n\n"
        "Отправьте фото блюда, и я распознаю ингредиенты и посчитаю калории.\n\n"
        "💡 <b>Советы для лучшего распознавания:</b>\n"
        "• Фотографируйте при хорошем освещении\n"
        "• Блюдо должно занимать большую часть кадра\n"
        "• Избегайте теней и бликов\n"
        "• Фотографируйте сверху для лучших результатов",
        parse_mode="HTML"
    )

@router.message(F.text.contains("🥤 Напиток"))
async def drink_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🥤 <b>Записать напиток</b>\n\n"
        "Введите напиток и количество:\n\n"
        "💡 <b>Примеры:</b>\n"
        "• Кофе 200\n"
        "• Апельсиновый сок 300\n"
        "• Чай 250\n"
        "• Кола 500\n"
        "• Молоко 200\n\n"
        "Формат: <напиток> <объем в мл>",
        parse_mode="HTML"
    )

@router.message(F.text.contains("🎯 Цели"))
async def goals_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "🎯 <b>Управление целями</b>\n\n"
        "Выберите тип целей для настройки:",
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("📈 Статистика"))
async def stats_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "📈 <b>Статистика</b>\n\n"
        "Выберите период для просмотра:",
        reply_markup=get_statistics_keyboard(),
        parse_mode="HTML"
    )

# Обработчики для настроек

@router.message(F.text.contains("🔔 Напоминания"))
async def reminders_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "🔔 <b>Настройка напоминаний</b>\n\n"
        "Выберите тип напоминаний:",
        reply_markup=get_notifications_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("🌐 Язык"))
async def language_button_handler(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "🌐 <b>Выбор языка</b>\n\n"
        "Выберите язык интерфейса:",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("ℹ️ О боте"))
async def about_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "ℹ️ <b>О NutriBuddy Bot</b>\n\n"
        "🤖 <b>Версия:</b> 2.0.0\n"
        "📅 <b>Обновление:</b> Март 2026\n\n"
        "🌟 <b>Возможности:</b>\n"
        "• Умное распознавание еды по фото\n"
        "• Персональный AI ассистент\n"
        "• Детальная статистика прогресса\n"
        "• Геймификация и достижения\n"
        "• Персональные планы питания\n"
        "• Учет воды и активности\n\n"
        "💬 <b>Поддержка:</b> @NutriBuddy_Support\n\n"
        "⭐ <b>Оцените бота:</b> Если вам нравится наш бот, поставьте оценку!",
        parse_mode="HTML"
    )

# Обработчики для навигации

@router.message(F.text.contains("🔙 Назад"))
async def back_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🔙 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.contains("🏠 Главное меню"))
async def home_button_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

# Обработчики для ответов на кнопки

@router.message(F.text.contains("✅"))
async def positive_response_handler(message: Message, state: FSMContext):
    """Обработчик для положительных ответов"""
    text = message.text.lower()
    
    if "составить план" in text:
        # Логика для составления плана питания
        await message.answer(
            "🍽️ <b>Составление плана питания</b>\n\n"
            "Расскажите о ваших предпочтениях в питании:",
            parse_mode="HTML"
        )
    elif "да" in text:
        await message.answer(
            "✅ <b>Принято!</b>\n\n"
            "Выполняю действие...",
            parse_mode="HTML"
        )

@router.message(F.text.contains("❌"))
async def negative_response_handler(message: Message, state: FSMContext):
    """Обработчик для отрицательных ответов"""
    await state.clear()
    await message.answer(
        "❌ <b>Отменено</b>\n\n"
        "Возвращаю в главное меню...",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

# Вспомогательные функции

async def handle_unknown_button(message: Message):
    """Обработчик неизвестных кнопок"""
    await message.answer(
        "❓ <b>Неизвестная команда</b>\n\n"
        "Пожалуйста, используйте кнопки меню или команды.\n\n"
        "🏠 <b>Главное меню:</b>",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )
