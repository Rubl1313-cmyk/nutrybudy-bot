"""
Система напоминаний для NutriBuddy Bot
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, and_
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message

from database.db import get_session
from database.models import User, WeightEntry
from utils.body_composition import calculate_body_composition, get_body_composition_recommendations

logger = logging.getLogger(__name__)

class ReminderService:
    """Сервис напоминаний"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def check_weekly_reminders(self):
        """Проверка еженедельных напоминаний"""
        logger.info("🔔 Проверка еженедельных напоминаний")
        
        async with get_session() as session:
            # Получаем всех пользователей с включенными напоминаниями
            result = await session.execute(
                select(User).where(User.reminder_enabled == True)
            )
            users = result.scalars().all()
            
            for user in users:
                if await self._should_send_weekly_reminder(user):
                    await self._send_weekly_reminder(user)
    
    async def _should_send_weekly_reminder(self, user: User) -> bool:
        """Проверка нужно ли отправлять еженедельное напоминание"""
        try:
            # Проверяем когда последний раз пользователь обновлял вес/обхваты
            week_ago = datetime.now() - timedelta(days=7)
            
            async with get_session() as session:
                # Проверяем вес
                weight_result = await session.execute(
                    select(WeightEntry).where(
                        and_(
                            WeightEntry.user_id == user.telegram_id,
                            WeightEntry.created_at >= week_ago
                        )
                    ).order_by(WeightEntry.created_at.desc())
                )
                recent_weight = weight_result.scalar_one_or_none()
            
            # Если нет записей за последнюю неделю, отправляем напоминание
            if recent_weight is None:
                logger.info(f"📅 Пользователю {user.telegram_id} нужно напоминание об обновлении данных")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке напоминания для {user.telegram_id}: {e}")
            return False
    
    async def _send_weekly_reminder(self, user: User):
        """Отправка еженедельного напоминания"""
        try:
            text = f"""📅 <b>Еженедельное обновление данных</b>

👋 Привет, {user.first_name or 'Пользователь'}!

📊 <b>Время обновить показатели!</b>

🔍 <b>Что нужно обновить:</b>
• ⚖️ Текущий вес
• 📏 Обхваты (шея, талия, бедра)

💡 <b>Зачем это нужно:</b>
• Точный расчет состава тела
• Отслеживание прогресса
• Коррекция целей питания
• Мотивация и достижения

📈 <b>Ваши текущие цели:</b>
• Калории: {user.daily_calorie_goal or 2000} ккал
• Белки: {user.daily_protein_goal or 150}г
• Жиры: {user.daily_fat_goal or 65}г
• Углеводы: {user.daily_carbs_goal or 250}г
• Шаги: {user.daily_steps_goal or 10000}

🚀 <b>Обновить данные?</b>"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="⚖️ Обновить вес", callback_data="weekly_update_weight"),
                    InlineKeyboardButton(text="📏 Обновить обхваты", callback_data="weekly_update_measurements")
                ],
                [
                    InlineKeyboardButton(text="📊 Мой прогресс", callback_data="weekly_progress"),
                    InlineKeyboardButton(text="🔕 Пропустить", callback_data="weekly_skip")
                ]
            ])
            
            await self.bot.send_message(
                user.telegram_id,
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
            logger.info(f"✅ Отправлено еженедельное напоминание пользователю {user.telegram_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке напоминания {user.telegram_id}: {e}")

async def create_body_composition_report(user: User) -> str:
    """Создание отчета о составе тела"""
    try:
        # Расчет состава тела на основе обхватов
        composition = calculate_body_composition(
            gender=user.gender,
            age=user.age or 30,
            weight=user.weight or 70,
            height=user.height or 170,
            neck_cm=user.neck_cm,
            waist_cm=user.waist_cm,
            hip_cm=user.hip_cm,
            bicep_cm=user.bicep_cm,
            forearm_cm=user.forearm_cm,
            chest_cm=user.chest_cm
        )
        
        # Получение рекомендаций
        recommendations = get_body_composition_recommendations(
            gender=user.gender,
            age=user.age or 30,
            body_fat_percentage=composition.get('body_fat_percentage'),
            muscle_mass_percentage=composition.get('muscle_mass_percentage')
        )
        
        text = f"""📊 <b>Анализ состава тела</b>

👤 <b>Данные:</b>
• Пол: {'Мужской' if user.gender == 'male' else 'Женский'}
• Возраст: {user.age or 'Не указан'} лет
• Вес: {user.weight or 'Не указан'} кг
• Рост: {user.height or 'Не указан'} см

📈 <b>Расчетные показатели:</b>"""
        
        if composition.get('body_fat_percentage'):
            text += f"""
• Жировая масса: {composition['body_fat_percentage']:.1f}%"""
        
        if composition.get('muscle_mass_percentage'):
            text += f"""
• Мышечная масса: {composition['muscle_mass_percentage']:.1f}%"""
        
        if composition.get('body_water_percentage'):
            text += f"""
• Вода в организме: {composition['body_water_percentage']:.1f}%"""
        
        text += "\n\n💡 <b>Рекомендации:</b>"
        
        if recommendations.get('fat'):
            text += f"\n{recommendations['fat']}"
        
        if recommendations.get('muscle'):
            text += f"\n{recommendations['muscle']}"
        
        if not composition.get('body_fat_percentage'):
            text += "\n⚠️ Для точного расчета состава тела нужны обхваты шеи, талии и бедер"
        
        return text
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании отчета о составе тела: {e}")
        return "❌ Не удалось рассчитать состав тела. Проверьте введенные данные."

async def get_measurement_update_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для обновления обхватов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📏 Шея", callback_data="measure_neck"),
            InlineKeyboardButton(text="📏 Талия", callback_data="measure_waist"),
            InlineKeyboardButton(text="📏 Бедра", callback_data="measure_hip")
        ],
        [
            InlineKeyboardButton(text="💪 Бицепс", callback_data="measure_bicep"),
            InlineKeyboardButton(text="💪 Предплечье", callback_data="measure_forearm"),
            InlineKeyboardButton(text="📊 Грудь", callback_data="measure_chest")
        ],
        [
            InlineKeyboardButton(text="📊 Анализ состава тела", callback_data="analyze_body_composition"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")
        ]
    ])

# Обработчики для напоминаний
async def handle_weekly_update_weight(callback, bot: Bot, state):
    """Обработка обновления веса из еженедельного напоминания"""
    await state.set_state("weekly_weight_update")
    
    text = """⚖️ <b>Обновление веса</b>

Введите ваш текущий вес в килограммах:

💡 <b>Пример:</b> 75.5"""
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="weekly_reminder_menu")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

async def handle_weekly_update_measurements(callback, bot: Bot, state):
    """Обработка обновления обхватов из еженедельного напоминания"""
    text = """📏 <b>Обновление обхватов</b>

Выберите какие обхваты хотите обновить:

💡 <b>Важно:</b>
• Замеряйте утром натощак
• Используйте гибкую ленту
• Не затягивайте слишком туго"""
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_measurement_update_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

async def handle_weekly_progress(callback, bot: Bot):
    """Показ прогресса из еженедельного напоминания"""
    # Здесь можно показать краткий прогресс
    text = """📊 <b>Ваш прогресс за неделю</b>

🔥 Обновите данные для точного анализа:
• Вес и обхваты
• Состав тела
• Коррекция целей

🚀 <b>Продолжайте в том же духе!</b>"""
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚖️ Обновить вес", callback_data="weekly_update_weight")],
            [InlineKeyboardButton(text="📏 Обновить обхваты", callback_data="weekly_update_measurements")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="weekly_skip")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

async def handle_weekly_skip(callback, bot: Bot):
    """Пропуск еженедельного напоминания"""
    text = """🔕 <b>Напоминание пропущено</b>

📅 Следующее напоминание через неделю

💡 <b>Совет:</b>
Регулярное обновление данных помогает точнее отслеживать прогресс!

🏠 <b>Главное меню</b>"""
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()
