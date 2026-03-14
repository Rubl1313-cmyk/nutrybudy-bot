"""
🤖 Обновленный AI-ассистент с Function Calling
✨ Интегрирует все новые AI-возможности
🎯 Умный диалоговый режим с выполнением действий
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from services.ai_engine_manager import ai
from services.smart_ai_assistant import smart_assistant
from services.ai_analytics import ai_analytics
from services.ai_personalizer import ai_personalizer
from services.ai_gamification import ai_gamification
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from database.db import get_session
from database.models import User
from sqlalchemy import select

router = Router()
logger = logging.getLogger(__name__)

class AIAssistantStates(StatesGroup):
    """Состояния умного помощника"""
    waiting_for_question = State()  # диалоговый режим
    analytics_mode = State()  # режим аналитики
    challenge_mode = State()  # режим челленджей

@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    """Вход в режим диалога с умным помощником"""
    user_id = message.from_user.id
    
    # Проверяем наличие пользователя
    async with get_session() as session:
        user_result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Сначала создайте профиль командой /set_profile",
                reply_markup=get_main_keyboard()
            )
            return
    
    # Получаем персонализированное приветствие
    persona = await ai_personalizer.get_user_persona(user_id)
    welcome_message = await ai_personalizer.personalize_message(
        user_id,
        f"💬 Привет! Я твой персональный помощник NutriBuddy. "
        f"Можешь общаться со мной как с настоящим помощником - просто говори что тебе нужно!",
        "motivation"
    )
    
    await message.answer(welcome_message, reply_markup=get_cancel_keyboard())
    await state.set_state(AIAssistantStates.waiting_for_question)
    
    # Сохраняем историю диалога
    await state.update_data(
        conversation_history=[],
        user_id=user_id,
        session_start=datetime.now()
    )

@router.message(Command("analytics"))
async def cmd_analytics(message: Message, state: FSMContext):
    """Аналитика и предсказания"""
    user_id = message.from_user.id
    
    # Генерируем комплексный анализ
    analysis = await ai_analytics.generate_comprehensive_analysis(user_id)
    
    # Проверяем наличие данных анализа (не поле success, т.к. его нет в успешном ответе)
    if not analysis or not analysis.get("data_summary"):
        await message.answer(
            "❌ Недостаточно данных для анализа. Ведите дневник хотя бы 7 дней!",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Формируем красивое сообщение с анализом
    ai_insights = analysis.get("ai_insights", {})
    
    analytics_message = f"""
📊 <b>Анализ твоего прогресса</b>

🎯 <b>Тренды:</b>
• Вес: {ai_insights.get('trends', {}).get('weight', 'стабилен')}
• Изменение за неделю: {ai_insights.get('trends', {}).get('weekly_change', 0):.1f} кг

🔮 <b>Прогноз на 14 дней:</b>
• Вес: {ai_insights.get('weight_prediction', {}).get('predicted_weight', 'недостаточно данных')} кг
• Доверительный интервал: ±{ai_insights.get('weight_prediction', {}).get('confidence_interval', {}).get('max', 0) - ai_insights.get('weight_prediction', {}).get('confidence_interval', {}).get('min', 0):.1f} кг

💡 <b>Психологические советы:</b>
• Мотивация: {ai_insights.get('psychology', {}).get('motivation_level', 'неизвестно')}
• Дисциплина: {ai_insights.get('psychology', {}).get('discipline_score', 'неизвестно')}
• Риски: {', '.join(ai_insights.get('risks', ['нет данных']))}

🎯 <b>Рекомендации:</b>
{chr(10).join(f"• {rec}" for rec in ai_insights.get('recommendations', ['Продолжай в том же духе'])[:3])}

💬 <b>Мотивация от помощника:</b>
{ai_insights.get('motivation', 'Ты молодец, продолжай!')}
"""
    
    await message.answer(analytics_message, parse_mode="HTML", reply_markup=get_main_keyboard())

@router.message(Command("challenge"))
async def cmd_challenge(message: Message, state: FSMContext):
    """Персонализированные челленджи"""
    user_id = message.from_user.id
    
    # Генерируем динамический челлендж
    challenge = await ai_gamification.generate_dynamic_challenge(user_id)
    
    if not challenge.get("id"):
        await message.answer(
            "❌ Не удалось создать челлендж. Попробуйте позже!",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Формируем сообщение с челленджем
    challenge_message = f"""
🎮 <b>{challenge.get('icon', '🎯')} {challenge.get('name', 'Новый челлендж')}</b>

{challenge.get('description', 'Описание недоступно')}

📅 <b>Длительность:</b> {challenge.get('duration_days', 7)} дней
⭐ <b>Сложность:</b> {challenge.get('difficulty', 'medium')}
🏆 <b>Награда:</b> {challenge.get('rewards', {}).get('xp', 0)} XP

📋 <b>Задания:</b>
"""
    
    daily_tasks = challenge.get("daily_tasks", [])
    for task in daily_tasks[:3]:  # Показываем первые 3 дня
        challenge_message += f"\n<b>День {task.get('day', '?')}:</b> {task.get('task', 'Задание')}"
    
    challenge_message += f"""

💡 <b>Почему этот челлендж для тебя:</b>
{challenge.get('personalization', 'Персонализированный под твои цели')}

💪 <b>Мотивация:</b>
{challenge.get('motivation_quote', 'Ты можешь это сделать!')}
"""
    
    # Сохраняем челлендж в состояние
    await state.set_data({"active_challenge": challenge})
    
    await message.answer(challenge_message, parse_mode="HTML", reply_markup=get_main_keyboard())

@router.message(Command("level"))
async def cmd_level(message: Message):
    """Уровень и достижения"""
    user_id = message.from_user.id
    
    # Рассчитываем уровень
    level_info = await ai_gamification.calculate_user_level(user_id)
    
    # Генерируем достижения
    achievements = await ai_gamification.generate_personalized_achievements(user_id)
    
    # Формируем сообщение
    level_message = f"""
🏆 <b>Твой уровень: {level_info['level']}</b>
👑 <b>Титул: {level_info['title']}</b>

⭐ <b>Опыт:</b> {level_info['current_xp']} XP
📈 <b>До следующего уровня:</b> {level_info['xp_to_next']} XP
🎯 <b>Прогресс:</b> {level_info['progress_percent']:.1f}%

📊 <b>Опыт по категориям:</b>
💧 Вода: {level_info.get('xp_breakdown', {}).get('water', 0)} XP
🏃 Активность: {level_info.get('xp_breakdown', {}).get('activity', 0)} XP
⚖️ Вес: {level_info.get('xp_breakdown', {}).get('weight', 0)} XP
🔥 Последовательность: {level_info.get('xp_breakdown', {}).get('consistency', 0)} XP
✨ Идеальные дни: {level_info.get('xp_breakdown', {}).get('perfect_days', 0)} XP

🎖️ <b>Достижения ({len(achievements)}):</b>
"""
    
    for achievement in achievements[:5]:  # Показываем первые 5
        level_message += f"\n{achievement.get('icon', '🏆')} {achievement.get('name', 'Достижение')}"
    
    await message.answer(level_message, parse_mode="HTML", reply_markup=get_main_keyboard())

@router.message(AIAssistantStates.waiting_for_question)
async def handle_ai_question(message: Message, state: FSMContext):
    """Обработка вопросов в AI-ассистенте"""
    user_id = message.from_user.id
    question = message.text
    
    # Получаем историю диалога
    data = await state.get_data()
    conversation_history = data.get("conversation_history", [])
    
    # Обрабатываем умный запрос
    result = await smart_assistant.process_smart_request(
        user_id=user_id,
        message=question,
        conversation_history=conversation_history
    )
    
    if result.get("success"):
        response_text = result.get("response", "Извините, не удалось обработать запрос")
        function_calls = result.get("function_calls", [])
        
        # Показываем результаты выполненных функций
        if function_calls:
            results_text = "\n\n✅ <b>Выполнено:</b>\n"
            for call in function_calls:
                if call.get("success"):
                    func_result = call.get("result", {})
                    if isinstance(func_result, dict):
                        results_text += f"• {func_result.get('message', 'Действие выполнено')}\n"
                    else:
                        results_text += f"• {func_result}\n"
                else:
                    results_text += f"• ❌ {call.get('result', 'Ошибка')}\n"
            
            response_text += results_text
        
        # Добавляем в историю
        conversation_history.append({"role": "user", "content": question})
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Ограничиваем историю
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        await state.update_data(conversation_history=conversation_history)
        
        await message.answer(response_text, parse_mode="HTML")
    else:
        await message.answer(
            "❌ " + result.get("error", "Произошла ошибка"),
            reply_markup=get_cancel_keyboard()
        )

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Выход из режимов AI-ассистента"""
    await state.clear()
    await message.answer(
        "👋 Режим завершен. Возвращаюсь в главное меню.",
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Выход по кнопке"""
    await state.clear()
    await callback.message.edit_text(
        "👋 Режим завершен. Возвращаюсь в главное меню.",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

# Экспорт для использования в других модулях
async def process_ai_assistant_query(user_id: int, query: str) -> str:
    """Обработка запроса от умного помощника из других модулей"""
    try:
        result = await smart_assistant.process_smart_request(
            user_id=user_id,
            message=query,
            conversation_history=[]
        )
        
        if result.get("success"):
            return result.get("response", "Извините, не удалось обработать запрос")
        else:
            return "❌ " + result.get("error", "Произошла ошибка")
    
    except Exception as e:
        logger.error(f"Smart assistant query error: {e}")
        return "❌ Временные технические проблемы. Попробуйте позже."

# Регистрация роутера
def register_ai_handlers(dp):
    """Регистрация обработчиков умного помощника"""
    dp.include_router(router)
    logger.info("💬 Smart assistant handlers registered")
