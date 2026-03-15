"""
Обработчик достижений и статистики геймификации
"""
import logging
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.gamification import gamification

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
    text += f"🎯 <b>До следующего уровня:</b> {stats['points_to_next']} очков\n"
    text += f"🔥 <b>Серия дней:</b> {stats['streak_days']}\n"
    text += f"🍽️ <b>Приемов пищи записано:</b> {stats['meals_logged']}\n\n"
    
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
    text += "🔓 <b>Доступные достижения:</b>\n\n"
    
    available_achievements = [a for a in gamification.achievements.values() if a.id not in earned_ids]
    
    if available_achievements:
        for achievement in available_achievements[:5]:  # Показываем первые 5
            text += f"🔒 {achievement.icon} {achievement.name}\n"
            text += f"   {achievement.description}\n\n"
        
        if len(available_achievements) > 5:
            text += f"... и еще {len(available_achievements) - 5} достижений\n"
    else:
        text += "🎉 Поздравляем! Вы получили все достижения!\n"
    
    # Клавиатура с действиями
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats_detail"),
                InlineKeyboardButton(text="🏆 Лидерборд", callback_data="leaderboard")
            ],
            [
                InlineKeyboardButton(text="🎯 Цели на день", callback_data="daily_goals"),
                InlineKeyboardButton(text="📈 Прогресс", callback_data="progress")
            ]
        ]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "stats_detail")
async def stats_detail_callback(callback: CallbackQuery):
    """Детальная статистика"""
    user_id = callback.from_user.id
    stats = gamification.get_user_stats(user_id)
    user_progress = gamification._get_user_progress(user_id)
    
    text = f"📊 <b>Детальная статистика</b>\n\n"
    text += f"👤 ID пользователя: {user_id}\n"
    text += f"📅 Последняя активность: {user_progress.last_activity_date or 'Нет данных'}\n"
    text += f"🍽️ Всего приемов пищи: {user_progress.meals_logged}\n"
    text += f"💧 Всего воды выпито: {user_progress.water_ml} мл\n"
    text += f"⚖️ Начальный вес: {user_progress.start_weight or 'Не указан'} кг\n"
    text += f"⚖️ Текущий вес: {user_progress.current_weight or 'Не указан'} кг\n"
    text += f"🌅 Ранних завтраков: {user_progress.early_breakfasts}\n"
    text += f"🌙 Поздних ужинов: {user_progress.late_dinners}\n\n"
    
    # Прогресс до следующего уровня
    current_level_points = (stats['level'] - 1) * 100
    next_level_points = stats['level'] * 100
    progress_percent = ((stats['total_points'] - current_level_points) / 100) * 100
    
    text += f"📈 <b>Прогресс до уровня {stats['level'] + 1}:</b>\n"
    text += f"[{'█' * int(progress_percent // 10)}{'░' * (10 - int(progress_percent // 10))}] {progress_percent:.1f}%\n"
    text += f"{stats['total_points'] - current_level_points} / {next_level_points - current_level_points} очков\n"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "daily_goals")
async def daily_goals_callback(callback: CallbackQuery):
    """Цели на день"""
    user_id = callback.from_user.id
    
    text = f"🎯 <b>Ваши цели на сегодня</b>\n\n"
    
    # Здесь должна быть проверка реального выполнения целей
    # Для примера используем заглушки
    text += "🍽️ <b>Приемы пищи:</b>\n"
    text += "   Завтрак: ✅ Записано\n"
    text += "   Обед: ⏳ Ожидается\n"
    text += "   Ужин: ⏳ Ожидается\n\n"
    
    text += "💧 <b>Вода:</b>\n"
    text += "   Цель: 2000 мл\n"
    text += "   Выпито: 1200 мл (60%)\n\n"
    
    text += "🔥 <b>Калории:</b>\n"
    text += "   Цель: 2000 ккал\n"
    text += "   Потреблено: 1450 ккал (72%)\n\n"
    
    text += "🏃 <b>Активность:</b>\n"
    text += "   Цель: 10000 шагов\n"
    text += "   Пройдено: 7500 шагов (75%)\n"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "progress")
async def progress_callback(callback: CallbackQuery):
    """Прогресс"""
    await callback.message.edit_text(
        "📈 <b>Ваш прогресс</b>\n\n"
        "Используйте команду /progress для детальной статистики питания",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "leaderboard")
async def leaderboard_callback(callback: CallbackQuery):
    """Лидерборд (заглушка)"""
    await callback.message.edit_text(
        "🏆 <b>Лидерборд</b>\n\n"
        "🚧 Функция в разработке...\n\n"
        "Скоро здесь будет рейтинг лучших пользователей!",
        parse_mode="HTML"
    )
    await callback.answer()
