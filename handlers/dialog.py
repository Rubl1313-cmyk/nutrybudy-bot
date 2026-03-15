"""
handlers/dialog.py
Единый обработчик всех текстовых сообщений с AI-классификацией намерений
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from services.intent_classifier import IntentClassifier
from services.tool_caller import ToolCaller

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text & ~F.command)
async def universal_message_handler(message: Message, state: FSMContext):
    """
    Универсальный обработчик текстовых сообщений.
    Классифицирует намерение и вызывает соответствующий инструмент.
    """
    user_id = message.from_user.id
    text = message.text.strip()
    
    logger.info(f"🤖 User {user_id} message: '{text[:50]}...'")
    
    try:
        # 1. Классифицируем намерение
        intent_data = await IntentClassifier.classify(text)
        intent = intent_data["intent"]
        confidence = intent_data["confidence"]
        method = intent_data.get("method", "unknown")
        
        logger.info(f"🎯 Intent: {intent} (confidence: {confidence:.2f}, method: {method})")
        
        # 2. Извлекаем сущности для дополнительного контекста
        entities = IntentClassifier.extract_entities(text, intent)
        if entities:
            logger.info(f"📋 Extracted entities: {entities}")
        
        # 3. Вызываем соответствующий инструмент
        success = await ToolCaller.call(intent, text, user_id, message, state)
        
        if success:
            logger.info(f"✅ Tool executed successfully for intent: {intent}")
        else:
            logger.warning(f"❌ Tool execution failed for intent: {intent}")
            
    except Exception as e:
        logger.error(f"🚨 Error in universal_message_handler: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке сообщения. "
            "Попробуйте переформулировать или используйте /help",
            parse_mode="HTML"
        )

@router.message(Command("chat"))
async def cmd_chat_mode(message: Message, state: FSMContext):
    """Прямой вход в режим чата с AI"""
    await message.answer(
        "🤖 <b>Режим диалога с AI</b>\n\n"
        "Теперь я понимаю любые сообщения!\n\n"
        "💡 <b>Примеры:</b>\n"
        "• «Съел на обед гречку с курицей»\n"
        "• «Выпил 2 стакана воды»\n"
        "• «Вес сегодня 72.5 кг»\n"
        "• «Пробежал 5 км за 30 минут»\n"
        "• «Покажи мой прогресс за неделю»\n"
        "• «Сколько калорий в авокадо?»\n\n"
        "Просто пишите мне на естественном языке!",
        parse_mode="HTML"
    )

@router.message(Command("test"))
async def cmd_test_intent(message: Message, state: FSMContext):
    """Тестирование классификатора намерений"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "🧪 <b>Тест классификатора</b>\n\n"
            "Использование: /test <ваш текст>\n\n"
            "Пример: /test съел 200г курицы на обед",
            parse_mode="HTML"
        )
        return
    
    test_text = args[1]
    
    try:
        # Классифицируем
        intent_data = await IntentClassifier.classify(test_text)
        entities = IntentClassifier.extract_entities(test_text, intent_data["intent"])
        
        result = f"🧪 <b>Результат анализа:</b>\n\n"
        result += f"📝 <b>Текст:</b> {test_text}\n"
        result += f"🎯 <b>Намерение:</b> {intent_data['intent']}\n"
        result += f"📊 <b>Уверенность:</b> {intent_data['confidence']:.2f}\n"
        result += f"🔧 <b>Метод:</b> {intent_data.get('method', 'unknown')}\n"
        
        if entities:
            result += f"\n📋 <b>Извлеченные сущности:</b>\n"
            for key, value in entities.items():
                result += f"• {key}: {value}\n"
        
        await message.answer(result, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in test_intent: {e}")
        await message.answer(f"❌ Ошибка: {e}", parse_mode="HTML")
