"""
Обработчик достижений и статистики геймификации
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from utils.gamification import gamification
from utils.ui_templates import ProgressBar
from keyboards.reply_v2 import get_main_keyboard_v2

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("achievements"))
@router.message(Command("достижения"))
async def cmd_achievements(message: Message):
    """Показать достижения пользователя"""
    user_id = message.from_user.id
    stats = await gamification.get_user_stats(user_id)

    # Формируем текст со статистикой
    text = f"🏆 <b>Ваши достижения</b>\n\n"
    text += f"📊 <b>Уровень:</b> {stats['level']}\n"
    text += f"⭐ <b>Очки:</b> {stats['total_points']}\n"
    text += f"🔥 <b>Серия дней:</b> {stats['streak_days']}\n"
    text += f"🍽️ <b>Приемов пищи:</b> {stats['meals_logged']}\n"
    text += f"🏃 <b>Тренировок:</b> {stats['activities_completed']}\n"
    text += f"⚖️ <b>Записей веса:</b> {stats['weight_logged']}\n\n"

    # Прогресс до следующего уровня
    next_level_points = (stats['level'] + 1) * 100
    progress_to_next = stats['total_points'] % 100
    progress_percent = (progress_to_next / 100) * 100
    progress_bar = ProgressBar.create_modern_bar(progress_percent, 100, 15, 'neon')
    
    text += f"🎯 <b>До следующего уровня:</b>\n{progress_bar}\n\n"

    # Получаем полученные достижения
    user_progress = await gamification._get_user_progress(user_id)
    earned_ids = user_progress.earned_achievements

    # Формируем список достижений
    text += f"📋 <b>Полученные достижения ({len(earned_ids)}):</b>\n\n"

    if earned_ids:
        for achievement_id in earned_ids:
            achievement = gamification.achievements.get(achievement_id)
            if achievement:
                text += f"{achievement.icon} <b>{achievement.name}</b>\n"
                text += f"   {achievement.description}\n\n"
    else:
        text += "У вас пока нет достижений.\n"
        text += "Начните записывать еду, тренироваться и следить за весом!\n\n"

    # Доступные достижения
    all_achievements = list(gamification.achievements.values())
    unearned = [a for a in all_achievements if a.id not in earned_ids]
    
    if unearned:
        text += f"\n🔒 <b>Доступно для получения ({len(unearned)}):</b>\n\n"
        for achievement in unearned[:5]:  # Показываем первые 5
            text += f"{achievement.icon} {achievement.name} - {achievement.description}\n"
        if len(unearned) > 5:
            text += f"... и ещё {len(unearned) - 5} достижений\n"

    text += f"\n💡 <i>Продолжайте вести дневник питания для получения новых достижений!</i>"

    await message.answer(
        text,
        reply_markup=get_main_keyboard_v2(),
        parse_mode="HTML"
    )
