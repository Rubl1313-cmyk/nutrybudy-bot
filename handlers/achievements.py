"""
Обработчик достижений и статистики геймификации
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.gamification import gamification
from utils.premium_templates import achievement_notification
from utils.ui_templates import ProgressBar

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("achievements"))
@router.message(Command("достижения"))
async def cmd_achievements(message: Message):
    """Показать достижения пользователя"""
    user_id = message.from_user.id
    stats = gamification.get_user_stats(user_id)
    
    # Формируем текст с общей статистикой
    text = f"🏆 <b>Ваши достижения</b>\n\n"
    text += f"📊 <b>Уровень:</b> {stats['level']}\n"
    text += f"⭐ <b>Очки:</b> {stats['total_points']}/{stats['level'] * 100}\n"
    
    # Прогресс до следующего уровня
    progress_percent = (stats['total_points'] / (stats['level'] * 100)) * 100
    progress_bar = ProgressBar.create_modern_bar(progress_percent, 100, 15, 'neon')
    text += f"🎯 <b>Прогресс до следующего уровня:</b>\n{progress_bar}\n"
    text += f"🔥 <b>Серия дней:</b> {stats['streak_days']}\n"
    text += f"🍽️ <b>Приёмов пищи записано:</b> {stats['meals_logged']}\n\n"
    
    # Получаем полученные достижения
    user_progress = gamification._get_user_progress(user_id)
    earned_ids = user_progress.earned_achievements
    
    # Формируем список достижений
    text += "📋 <b>Полученные достижения:</b>\n\n"
    
    if earned_ids:
        for achievement_id in earned_ids:
            achievement = gamification.achievements.get(achievement_id)
            if achievement:
                text += f"{achievement.icon} {achievement.name}\n"
                text += f"   {achievement.description} (+{achievement.points} очков)\n\n"
    else:
        text += "У вас пока нет достижений. Начните записывать еду!\n\n"
    
    # Доступные достижения
    text += "🎯 <b>Доступные достижения:</b>\n\n"
    
    available_achievements = [a for a in gamification.achievements.values() if a.id not in earned_ids]
    
    if available_achievements:
        # Показываем первые 5 доступных достижений
        for achievement in available_achievements[:5]:
            text += f"🔒 {achievement.icon} {achievement.name}\n"
            text += f"   {achievement.description}\n\n"
        
        if len(available_achievements) > 5:
            text += f"... и ещё {len(available_achievements) - 5} достижений\n"
    else:
        text += "🎉 Вы получили все достижения! Вы настоящий чемпион!\n"
    
    # Кнопка для подробной статистики
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Подробная статистика", callback_data="detailed_stats")],
        [InlineKeyboardButton(text="🏅 Лидерboard", callback_data="leaderboard")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "detailed_stats")
async def callback_detailed_stats(callback: CallbackQuery):
    """Подробная статистика пользователя"""
    user_id = callback.from_user.id
    stats = gamification.get_user_stats(user_id)
    
    text = f"📊 <b>Подробная статистика</b>\n\n"
    
    # Основные показатели
    text += f"👤 <b>Профиль:</b>\n"
    text += f"   Уровень: {stats['level']}\n"
    text += f"   Очки: {stats['total_points']}\n"
    text += f"   Серия дней: {stats['streak_days']}\n\n"
    
    # Прогресс по категориям
    text += f"📈 <b>Прогресс по категориям:</b>\n"
    
    # Питание
    nutrition_progress = min(stats['meals_logged'] / 30 * 100, 100)  # 30 приёмов = 100%
    nutrition_bar = ProgressBar.create_modern_bar(nutrition_progress, 100, 12, 'default')
    text += f"   🍽️ Питание: {nutrition_bar}\n"
    
    # Активность
    activity_progress = min(stats['activities_completed'] / 20 * 100, 100)  # 20 активностей = 100%
    activity_bar = ProgressBar.create_modern_bar(activity_progress, 100, 12, 'activity')
    text += f"   🏃 Активность: {activity_bar}\n"
    
    # Вес
    weight_progress = min(stats['weight_logged'] / 10 * 100, 100)  # 10 записей веса = 100%
    weight_bar = ProgressBar.create_modern_bar(weight_progress, 100, 12, 'default')
    text += f"   ⚖️ Вес: {weight_bar}\n\n"
    
    # Статистика по времени
    text += f"⏰ <b>Активность по времени:</b>\n"
    text += f"   Сегодня: {stats['today_actions']} действий\n"
    text += f"   За неделю: {stats['week_actions']} действий\n"
    text += f"   За месяц: {stats['month_actions']} действий\n\n"
    
    # Мотивационное сообщение
    if stats['streak_days'] >= 7:
        text += "🔥 <b>Потрясающая серия!</b> Вы на правильном пути!\n"
    elif stats['streak_days'] >= 3:
        text += "💪 <b>Хорошая серия!</b> Продолжайте в том же духе!\n"
    else:
        text += "🌱 <b>Начало пути!</b> Каждый день делает вас сильнее!\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к достижениям", callback_data="back_to_achievements")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "leaderboard")
async def callback_leaderboard(callback: CallbackQuery):
    """Таблица лидеров"""
    # Получаем топ-10 пользователей по очкам
    top_users = gamification.get_leaderboard(limit=10)
    
    text = f"🏆 <b>Таблица лидеров</b>\n\n"
    
    for i, user_data in enumerate(top_users, 1):
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."
        
        username = user_data.get('username', f"User#{user_data['user_id']}")
        points = user_data['total_points']
        level = user_data['level']
        
        text += f"{medal} {username} — {points} очков (уровень {level})\n"
    
    text += f"\n💡 <b>Ваше место:</b> #{gamification.get_user_rank(callback.from_user.id)}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="leaderboard")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_achievements")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "back_to_achievements")
async def callback_back_to_achievements(callback: CallbackQuery):
    """Возврат к списку достижений"""
    await cmd_achievements(callback.message)

@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    from keyboards.improved_keyboards import get_main_keyboard_v2
    
    text = "🏠 <b>Главное меню</b>\n\n"
    text += "Выберите действие:"
    
    await callback.message.edit_text(text, reply_markup=get_main_keyboard_v2())
    await callback.answer()

# Проверка и награждение достижений
async def check_achievements(user_id: int, action_type: str, value: float = 1):
    """Проверить и наградить достижения пользователя"""
    try:
        new_achievements = gamification.check_achievements(user_id, action_type, value)
        
        if new_achievements:
            for achievement in new_achievements:
                # Отправляем уведомление о новом достижении
                notification = achievement_notification(achievement.name, achievement.description)
                
                # Здесь должна быть отправка сообщения пользователю
                # await bot.send_message(user_id, notification)
                logger.info(f"User {user_id} earned achievement: {achievement.name}")
                
    except Exception as e:
        logger.error(f"Error checking achievements for user {user_id}: {e}")

# Экспорт функции для использования в других обработчиках
__all__ = ['check_achievements']
