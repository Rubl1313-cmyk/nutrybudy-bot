"""
Обработчики кнопок клавиатур для NutriBuddy Bot
"""
import logging
import re
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from database.db import get_session
from database.models import User, DrinkEntry
from keyboards.reply_v2 import get_main_keyboard_v2
from utils.premium_templates import drink_card, water_card
from utils.daily_stats import get_daily_water
from handlers.drinks import cmd_water, cmd_quick_water
from handlers.food import cmd_log_food
from handlers.common import cmd_help, cmd_start

logger = logging.getLogger(__name__)
router = Router()

# === Обработчики кнопок воды ===

@router.message(F.text.regexp(r'^💧\s*(\d+)\s*(мл|мл|стакан|стакана|литр|л)$'))
async def water_keyboard_handler(message: Message, state: FSMContext):
    """Обработка кнопок клавиатуры воды"""
    text = message.text
    
    if "1 стакан" in text:
        amount = 200
    elif "2 стакана" in text:
        amount = 400
    elif "500 мл" in text or "500мл" in text:
        amount = 500
    elif "1 литр" in text or "1л" in text:
        amount = 1000
    else:
        # Извлекаем число из текста
        match = re.search(r'(\d+)', text)
        if match:
            amount = int(match.group(1))
        else:
            await message.answer("❌ Неверный формат")
            return
    
    # Сохраняем воду как в process_quick_water
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Сначала настройте профиль")
            return
        
        drink_entry = DrinkEntry(
            user_id=user.telegram_id,
            drink_name="вода",
            amount=amount,
            calories=0
        )
        
        session.add(drink_entry)
        await session.commit()
        
        # Получаем статистику
        total_today = await get_daily_water(user.telegram_id)
        
        # Карточка
        card = water_card(amount, total_today, user.daily_water_goal)
        await message.answer(card, reply_markup=get_main_keyboard_v2())

# === Обработчики кнопок еды ===

@router.message(F.text.startswith("📸"))
async def photo_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки фото еды"""
    await state.clear()
    await message.answer(
        "📸 <b>Отправьте фото блюда</b>\n\n"
        "Я распознаю продукты и рассчитаю калории.",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.startswith("✏️"))
async def text_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки текстового ввода еды"""
    await state.clear()
    await cmd_log_food(message, state)

@router.message(F.text.startswith("⚡"))
async def quick_food_handler(message: Message, state: FSMContext):
    """Обработка кнопки быстрого ввода еды"""
    await state.clear()
    await message.answer(
        "⚡ <b>Быстрый ввод</b>\n\n"
        "Напишите что вы съели в формате:\n"
        "• гречка 200г\n"
        "• курица 150г\n"
        "• салат 100г",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

# === Обработчики кнопок помощи ===

@router.message(F.text.startswith("📋"))
async def commands_help_handler(message: Message):
    """Показать список команд"""
    await cmd_help(message, None)

@router.message(F.text.startswith("🚀"))
async def features_help_handler(message: Message):
    """Показать возможности бота"""
    text = "🚀 <b>Возможности NutriBuddy:</b>\n\n"
    text += "🍽️ <b>Распознавание еды по фото</b>\n"
    text += "📊 <b>Отслеживание КБЖУ и калорий</b>\n"
    text += "💧 <b>Контроль водного баланса</b>\n"
    text += "⚖️ <b>Запись веса и прогресса</b>\n"
    text += "🤖 <b>AI ассистент для советов</b>\n"
    text += "📈 <b>Детальная статистика</b>\n"
    
    await message.answer(text, reply_markup=get_main_keyboard_v2(), parse_mode="HTML")

@router.message(F.text.startswith("💬"))
async def support_help_handler(message: Message):
    """Показать поддержку"""
    text = "💬 <b>Поддержка NutriBuddy:</b>\n\n"
    text += "👨‍💻 <b>Разработчик:</b> @username\n"
    text += "📧 <b>Почта:</b> support@nutribuddy.com\n"
    text += "📚 <b>Документация:</b> https://docs.nutribuddy.com\n"
    text += "💡 <b>Идеи и предложения:</b> @ideas_channel"
    
    await message.answer(text, reply_markup=get_main_keyboard_v2(), parse_mode="HTML")

# === Универсальные обработчики ===

@router.message(F.text.startswith("🏠"))
async def menu_keyboard_handler(message: Message, state: FSMContext):
    """Обработка кнопки главного меню из клавиатур"""
    await state.clear()
    await cmd_start(message)

@router.message(F.text.startswith("✅"))
async def yes_button_handler(message: Message, state: FSMContext):
    """Обработка кнопки Да"""
    await message.answer("✅ Подтверждено")

@router.message(F.text.startswith("❌"))
async def no_button_handler(message: Message, state: FSMContext):
    """Обработка кнопки Нет"""
    await message.answer("❌ Отменено")

# === Обработчики настроек ===

@router.message(F.text.startswith("📏"))
async def metric_units_handler(message: Message):
    """Метрическая система"""
    await message.answer("📏 <b>Метрическая система</b>\n\nИспользуются килограммы и сантиметры.")

# === Обработчики статистики ===

@router.message(F.text.startswith("🏃"))
async def activity_stats_handler(message: Message):
    """Статистика активности"""
    from handlers.activity import cmd_activity_stats
    await cmd_activity_stats(message)

# === Недостающие обработчики кнопок ===

@router.message(F.text.lower().in_(["📈 графики", "графики"]))
async def charts_handler(message: Message):
    """Обработчик кнопки Графики - перенаправляет в прогресс"""
    from handlers.progress import cmd_progress
    await cmd_progress(message, None)

@router.message(F.text.lower().in_(["📉 тренды", "тренды"]))
async def trends_handler(message: Message):
    """Обработчик кнопки Тренды - перенаправляет в прогресс"""
    from handlers.progress import cmd_progress
    await cmd_progress(message, None)

@router.message(F.text.lower().in_(["💧 свой объем", "свой объем"]))
async def custom_water_volume_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Свой объем для воды"""
    from handlers.drinks import cmd_water
    await cmd_water(message, state)

@router.message(F.text.lower() == "🎾 другое")
async def other_activity_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Другое для активности"""
    from handlers.activity import ActivityStates
    await state.update_data(activity_type="other", activity_name="другое")
    await message.answer(
        "🎾 <b>Другая активность</b>\n\n"
        "Введите длительность в минутах (например: 30):",
        parse_mode="HTML"
    )
    await state.set_state(ActivityStates.waiting_for_duration)

@router.message(F.text.lower().in_(["🍳 завтрак", "завтрак"]))
async def breakfast_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Завтрак"""
    await state.update_data(meal_type="breakfast")
    await message.answer(
        "🍳 <b>Завтрак</b>\n\n"
        "Отправьте фото или опишите что вы съели на завтрак:",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["🍽️ обед", "обед"]))
async def lunch_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Обед"""
    await state.update_data(meal_type="lunch")
    await message.answer(
        "🍽️ <b>Обед</b>\n\n"
        "Отправьте фото или опишите что вы съели на обед:",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["🌙 ужин", "ужин"]))
async def dinner_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Ужин"""
    await state.update_data(meal_type="dinner")
    await message.answer(
        "🌙 <b>Ужин</b>\n\n"
        "Отправьте фото или опишите что вы съели на ужин:",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["🥨 перекус", "перекус"]))
async def snack_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Перекус"""
    await state.update_data(meal_type="snack")
    await message.answer(
        "🥨 <b>Перекус</b>\n\n"
        "Отправьте фото или опишите что вы съели на перекус:",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

# === Обработчики кнопок с префиксами [...] ===

@router.message(F.text.lower().in_(["👤 профиль", "профиль"]))
async def profile_settings_handler(message: Message):
    """Обработчик кнопки Профиль в настройках"""
    from handlers.profile import cmd_profile
    await cmd_profile(message, None)

@router.message(F.text.lower().in_(["🔔 уведомления", "уведомления"]))
async def notifications_settings_handler(message: Message):
    """Обработчик кнопки Уведомления в настройках"""
    await message.answer(
        "🔔 <b>Настройки уведомлений</b>\n\n"
        "Функция в разработке. Скоро вы сможете настроить:\n"
        "• Напоминания о приёмах пищи\n"
        "• Напоминания о воде\n"
        "• Напоминания о взвешивании\n\n"
        "Пока доступны только напоминания о воде!",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["📏 единицы", "единицы"]))
async def units_settings_handler(message: Message):
    """Обработчик кнопки Единицы в настройках"""
    await message.answer(
        "📏 <b>Система единиц</b>\n\n"
        "В данный момент поддерживается только метрическая система:\n"
        "• Вес: килограммы (кг)\n"
        "• Рост: сантиметры (см)\n"
        "• Объем: миллилитры (мл)\n\n"
        "Имперская система (фунты, дюймы) в разработке!",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["❌ отмена", "отмена"]))
async def cancel_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Отмена"""
    await state.clear()
    await message.answer(
        "❌ Отменено. Выберите действие:",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["⚖️ записать вес", "записать вес"]))
async def quick_weight_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Записать вес"""
    from handlers.weight import cmd_weight
    await state.clear()
    await cmd_weight(message, state)

@router.message(F.text.lower().in_(["🏃 активность", "активность"]))
async def quick_activity_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Активность"""
    from handlers.activity import cmd_fitness
    await state.clear()
    await cmd_fitness(message, state)

# === Обработчики ввода погоды и рецептов ===

@router.message(F.text.lower().in_(["🌤️ погода", "погода"]))
async def weather_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Погода - запрашивает город и показывает погоду"""
    await state.set_state("waiting_for_weather_city")
    await message.answer(
        "🌤️ <b>Погода</b>\n\n"
        "Напишите название вашего города (например: Москва, Киев, Минск):\n\n"
        "Или нажмите «🏠 Главное меню» для отмены.",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["🍳 рецепт", "рецепт"]))
async def recipe_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Рецепт - запрашивает блюдо и показывает рецепт"""
    await state.set_state("waiting_for_recipe_dish")
    await message.answer(
        "🍳 <b>Рецепты</b>\n\n"
        "Напишите название блюда, которое хотите приготовить (например: борщ, паста, салат):\n\n"
        "Или нажмите «🏠 Главное меню» для отмены.",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(lambda message: message.text and message.text.strip() not in ["🍽️ Записать еду", "💧 Вода", "🤖 AI Ассистент", "📊 Прогресс", "🏆 Достижения", "👤 Профиль", "❓ Помощь", "🏠 Главное меню", "Главное меню"])
async def weather_and_recipe_input_handler(message: Message, state: FSMContext):
    """Обработка ввода города для погоды или блюда для рецепта"""
    current_state = await state.get_state()
    text = message.text.strip()
    
    if current_state == "waiting_for_weather_city":
        try:
            from services.weather import get_weather
            
            # Показываем загрузку
            loading_msg = await message.answer("🌤️ Загружаю данные о погоде...")
            
            weather_data = await get_weather(text)
            
            if weather_data and 'temp' in weather_data:
                temp = weather_data.get('temp', 'N/A')
                condition = weather_data.get('condition', 'N/A')
                humidity = weather_data.get('humidity', 'N/A')
                wind = weather_data.get('wind', 'N/A')
                feels_like = weather_data.get('feels_like', 'N/A')
                
                # Формируем ответ
                weather_text = f"🌤️ <b>Погода в городе {text}</b>\n\n"
                weather_text += f"🌡️ <b>Температура:</b> {temp}°C\n"
                weather_text += f"🤔 <b>Ощущается как:</b> {feels_like}°C\n"
                weather_text += f"☁️ <b>Условия:</b> {condition}\n"
                weather_text += f"💧 <b>Влажность:</b> {humidity}%\n"
                weather_text += f"💨 <b>Ветер:</b> {wind} м/с\n\n"
                
                # Добавляем рекомендации
                if temp < 10:
                    weather_text += "🧥 <b>Рекомендация:</b> Оденьтесь тепло, на улице холодно!\n"
                elif temp < 20:
                    weather_text += "👕 <b>Рекомендация:</b> Прохладно, возьмите лёгкую куртку.\n"
                else:
                    weather_text += "☀️ <b>Рекомендация:</b> Тёплая погода, можно надеть футболку!\n"
                
                if condition.lower() in ['дождь', 'ливень', 'гроза']:
                    weather_text += "☔ <b>Совет:</b> Не забудьте зонт!\n"
                
                await message.answer(weather_text, reply_markup=get_main_keyboard_v2(), parse_mode="HTML")
            else:
                await message.answer(
                    f"❌ Не удалось получить погоду для города \"{text}\".\n\n"
                    "Проверьте правильность названия города и попробуйте снова.",
                    reply_markup=get_main_keyboard_v2(),
                    parse_mode="HTML"
                )
            
            await loading_msg.delete()
            await state.clear()
            
        except Exception as e:
            logger.error(f"Error getting weather for {text}: {e}")
            await message.answer(
                f"❌ Произошла ошибка при получении погоды для \"{text}\".\n"
                "Попробуйте позже или проверьте название города.",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            await state.clear()
    
    elif current_state == "waiting_for_recipe_dish":
        try:
            from services.cloudflare_manager import cf_manager
            
            # Показываем загрузку
            loading_msg = await message.answer("🍳 Ищу рецепт...")
            
            # Используем AI для получения рецепта
            prompt = f"""Пользователь хочет рецепт блюда: {text}

Пожалуйста, предоставьте:
1. Название блюда
2. Список ингредиентов с количествами
3. Пошаговую инструкцию приготовления
4. Время приготовления
5. Калорийность и БЖУ (примерно)

Форматируй ответ красиво с эмодзи."""

            result = await cf_manager.get_assistant_response(prompt)
            
            if result and 'response' in result:
                recipe_text = f"🍳 <b>Рецепт: {text}</b>\n\n"
                recipe_text += result['response']
                
                await message.answer(recipe_text, reply_markup=get_main_keyboard_v2(), parse_mode="HTML")
            else:
                await message.answer(
                    f"❌ Не удалось найти рецепт для \"{text}\".\n\n"
                    "Попробуйте другое блюдо или проверьте правильность названия.",
                    reply_markup=get_main_keyboard_v2(),
                    parse_mode="HTML"
                )
            
            await loading_msg.delete()
            await state.clear()
            
        except Exception as e:
            logger.error(f"Error getting recipe for {text}: {e}")
            await message.answer(
                f"❌ Произошла ошибка при поиске рецепта для \"{text}\".\n"
                "Попробуйте позже или другое блюдо.",
                reply_markup=get_main_keyboard_v2(),
                parse_mode="HTML"
            )
            await state.clear()

@router.message(F.text.lower().in_(["🔢 рассчитать кбжу", "рассчитать кбжу"]))
async def calculate_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Рассчитать КБЖУ"""
    await message.answer(
        "🔢 <b>Расчет КБЖУ</b>\n\n"
        "Напишите продукты и их количество, например:\n"
        "• гречка 200г\n"
        "• курица 150г\n"
        "• салат 100г\n\n"
        "Я рассчитаю калории и БЖУ!",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["💬 общий вопрос", "общий вопрос"]))
async def advice_handler(message: Message, state: FSMContext):
    """Обработчик кнопки Общий вопрос"""
    from handlers.ai_assistant import cmd_ask
    await state.clear()
    await cmd_ask(message, state)

# === Обработчики кнопок статистики ===

@router.message(F.text.lower().in_(["🔥 калории", "калории"]))
async def calories_stats_handler(message: Message):
    """Обработчик кнопки Калории"""
    await message.answer(
        "🔥 <b>Статистика калорий</b>\n\n"
        "Выберите период для просмотра статистики:\n"
        "• Сегодня\n"
        "• Неделя\n"
        "• Месяц\n\n"
        "Используйте команду /progress для детальной статистики!",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["⚖️ вес", "вес"]))
async def weight_stats_handler(message: Message):
    """Обработчик кнопки Вес"""
    await message.answer(
        "⚖️ <b>Статистика веса</b>\n\n"
        "Для просмотра динамики веса используйте:\n"
        "• /progress - выберите период\n"
        "• /weight - записать текущий вес\n\n"
        "Продолжайте записывать вес для отслеживания трендов!",
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )

@router.message(F.text.lower().in_(["💧 вода", "вода"]))
async def water_stats_handler(message: Message):
    """Обработчик кнопки Вода"""
    from handlers.drinks import cmd_water_stats
    try:
        await cmd_water_stats(message)
    except:
        await message.answer(
            "💧 <b>Статистика воды</b>\n\n"
            "Используйте /water для записи воды и просмотра статистики!",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )

@router.message(F.text.lower().in_(["🏃 активность", "активность"]))
async def activity_stats_handler(message: Message):
    """Обработчик кнопки Активность"""
    from handlers.activity import cmd_activity_stats
    try:
        await cmd_activity_stats(message)
    except:
        await message.answer(
            "🏃 <b>Статистика активности</b>\n\n"
            "Используйте /fitness для записи активности!",
            reply_markup=get_main_keyboard_v2(),
            parse_mode="HTML"
        )
