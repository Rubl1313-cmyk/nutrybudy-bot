"""
Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚Ñ‡Ğ¸Ğº Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹ Ğ¸ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸ Ğ³ĞµĞ¹Ğ¼Ğ¸Ñ„Ğ¸ĞºĞ°Ñ†Ğ¸Ğ¸
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
@router.message(Command("Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�"))
async def cmd_achievements(message: Message):
    """ĞŸĞ¾ĞºĞ°Ğ·Ğ°Ñ‚ÑŒ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ� Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�"""
    user_id = message.from_user.id
    stats = gamification.get_user_stats(user_id)
    
    # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ñ‚ĞµĞºÑ�Ñ‚ Ñ� Ğ¾Ğ±Ñ‰ĞµĞ¹ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¾Ğ¹
    text = f"ğŸ�† <b>Ğ’Ğ°ÑˆĞ¸ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�</b>\n\n"
    text += f"ğŸ“Š <b>Ğ£Ñ€Ğ¾Ğ²ĞµĞ½ÑŒ:</b> {stats['level']}\n"
    text += f"â­� <b>Ğ�Ñ‡ĞºĞ¸:</b> {stats['total_points']}/{stats['level'] * 100}\n"
    text += f"ğŸ�¯ <b>Ğ”Ğ¾ Ñ�Ğ»ĞµĞ´ÑƒÑ�Ñ‰ĞµĞ³Ğ¾ ÑƒÑ€Ğ¾Ğ²Ğ½Ñ�:</b> {stats['points_to_next']} Ğ¾Ñ‡ĞºĞ¾Ğ²\n"
    text += f"ğŸ”¥ <b>Ğ¡ĞµÑ€Ğ¸Ñ� Ğ´Ğ½ĞµĞ¹:</b> {stats['streak_days']}\n"
    text += f"ğŸ�½ï¸� <b>ĞŸÑ€Ğ¸ĞµĞ¼Ğ¾Ğ² Ğ¿Ğ¸Ñ‰Ğ¸ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¾:</b> {stats['meals_logged']}\n\n"
    
    # ĞŸĞ¾Ğ»ÑƒÑ‡Ğ°ĞµĞ¼ Ğ¿Ğ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ½Ñ‹Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�
    user_progress = gamification._get_user_progress(user_id)
    earned_ids = user_progress.earned_achievements
    
    # Ğ¤Ğ¾Ñ€Ğ¼Ğ¸Ñ€ÑƒĞµĞ¼ Ñ�Ğ¿Ğ¸Ñ�Ğ¾Ğº Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹
    text += "ğŸ“‹ <b>ĞŸĞ¾Ğ»ÑƒÑ‡ĞµĞ½Ğ½Ñ‹Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�:</b>\n\n"
    
    if earned_ids:
        for achievement_id in earned_ids:
            achievement = gamification.achievements.get(achievement_id)
            if achievement:
                text += f"{achievement.icon} {achievement.name}\n"
                text += f"   {achievement.description} (+{achievement.points} Ğ¾Ñ‡ĞºĞ¾Ğ²)\n\n"
    else:
        text += "Ğ£ Ğ²Ğ°Ñ� Ğ¿Ğ¾ĞºĞ° Ğ½ĞµÑ‚ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹. Ğ�Ğ°Ñ‡Ğ½Ğ¸Ñ‚Ğµ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ñ‹Ğ²Ğ°Ñ‚ÑŒ ĞµĞ´Ñƒ!\n\n"
    
    # Ğ”Ğ¾Ñ�Ñ‚ÑƒĞ¿Ğ½Ñ‹Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�
    text += "ğŸ”“ <b>Ğ”Ğ¾Ñ�Ñ‚ÑƒĞ¿Ğ½Ñ‹Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�:</b>\n\n"
    
    available_achievements = [a for a in gamification.achievements.values() if a.id not in earned_ids]
    
    if available_achievements:
        for achievement in available_achievements[:5]:  # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¿ĞµÑ€Ğ²Ñ‹Ğµ 5
            text += f"ğŸ”’ {achievement.icon} {achievement.name}\n"
            text += f"   {achievement.description}\n\n"
        
        if len(available_achievements) > 5:
            text += f"... Ğ¸ ĞµÑ‰Ğµ {len(available_achievements) - 5} Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹\n"
    else:
        text += "ğŸ�‰ ĞŸĞ¾Ğ·Ğ´Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼! Ğ’Ñ‹ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ğ»Ğ¸ Ğ²Ñ�Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�!\n"
    
    # ĞšĞ»Ğ°Ğ²Ğ¸Ğ°Ñ‚ÑƒÑ€Ğ° Ñ� Ğ´ĞµĞ¹Ñ�Ñ‚Ğ²Ğ¸Ñ�Ğ¼Ğ¸
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ğŸ“Š ĞœĞ¾Ñ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ°", callback_data="stats_detail"),
                InlineKeyboardButton(text="ğŸ�† Ğ›Ğ¸Ğ´ĞµÑ€Ğ±Ğ¾Ñ€Ğ´", callback_data="leaderboard")
            ],
            [
                InlineKeyboardButton(text="ğŸ�¯ Ğ¦ĞµĞ»Ğ¸ Ğ½Ğ° Ğ´ĞµĞ½ÑŒ", callback_data="daily_goals"),
                InlineKeyboardButton(text="ğŸ“ˆ ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�", callback_data="progress")
            ]
        ]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "stats_detail")
async def stats_detail_callback(callback: CallbackQuery):
    """Ğ”ĞµÑ‚Ğ°Ğ»ÑŒĞ½Ğ°Ñ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ°"""
    user_id = callback.from_user.id
    stats = gamification.get_user_stats(user_id)
    user_progress = gamification._get_user_progress(user_id)
    
    text = f"ğŸ“Š <b>Ğ”ĞµÑ‚Ğ°Ğ»ÑŒĞ½Ğ°Ñ� Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ°</b>\n\n"
    text += f"ğŸ‘¤ ID Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»Ñ�: {user_id}\n"
    text += f"ğŸ“… ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ñ�Ñ� Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ: {user_progress.last_activity_date or 'Ğ�ĞµÑ‚ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…'}\n"
    text += f"ğŸ�½ï¸� Ğ’Ñ�ĞµĞ³Ğ¾ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ¾Ğ² Ğ¿Ğ¸Ñ‰Ğ¸: {user_progress.meals_logged}\n"
    text += f"ğŸ’§ Ğ’Ñ�ĞµĞ³Ğ¾ Ğ²Ğ¾Ğ´Ñ‹ Ğ²Ñ‹Ğ¿Ğ¸Ñ‚Ğ¾: {user_progress.water_ml} Ğ¼Ğ»\n"
    text += f"âš–ï¸� Ğ�Ğ°Ñ‡Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ²ĞµÑ�: {user_progress.start_weight or 'Ğ�Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½'} ĞºĞ³\n"
    text += f"âš–ï¸� Ğ¢ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ�: {user_progress.current_weight or 'Ğ�Ğµ ÑƒĞºĞ°Ğ·Ğ°Ğ½'} ĞºĞ³\n"
    text += f"ğŸŒ… Ğ Ğ°Ğ½Ğ½Ğ¸Ñ… Ğ·Ğ°Ğ²Ñ‚Ñ€Ğ°ĞºĞ¾Ğ²: {user_progress.early_breakfasts}\n"
    text += f"ğŸŒ™ ĞŸĞ¾Ğ·Ğ´Ğ½Ğ¸Ñ… ÑƒĞ¶Ğ¸Ğ½Ğ¾Ğ²: {user_progress.late_dinners}\n\n"
    
    # ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ´Ğ¾ Ñ�Ğ»ĞµĞ´ÑƒÑ�Ñ‰ĞµĞ³Ğ¾ ÑƒÑ€Ğ¾Ğ²Ğ½Ñ�
    current_level_points = (stats['level'] - 1) * 100
    next_level_points = stats['level'] * 100
    progress_percent = ((stats['total_points'] - current_level_points) / 100) * 100
    
    text += f"ğŸ“ˆ <b>ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ´Ğ¾ ÑƒÑ€Ğ¾Ğ²Ğ½Ñ� {stats['level'] + 1}:</b>\n"
    text += f"[{'â–ˆ' * int(progress_percent // 10)}{'â–‘' * (10 - int(progress_percent // 10))}] {progress_percent:.1f}%\n"
    text += f"{stats['total_points'] - current_level_points} / {next_level_points - current_level_points} Ğ¾Ñ‡ĞºĞ¾Ğ²\n"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "daily_goals")
async def daily_goals_callback(callback: CallbackQuery):
    """Ğ¦ĞµĞ»Ğ¸ Ğ½Ğ° Ğ´ĞµĞ½ÑŒ"""
    user_id = callback.from_user.id
    
    text = f"ğŸ�¯ <b>Ğ’Ğ°ÑˆĞ¸ Ñ†ĞµĞ»Ğ¸ Ğ½Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�</b>\n\n"
    
    # Ğ—Ğ´ĞµÑ�ÑŒ Ğ´Ğ¾Ğ»Ğ¶Ğ½Ğ° Ğ±Ñ‹Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ğ²ĞµÑ€ĞºĞ° Ñ€ĞµĞ°Ğ»ÑŒĞ½Ğ¾Ğ³Ğ¾ Ğ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ¸Ñ� Ñ†ĞµĞ»ĞµĞ¹
    # Ğ”Ğ»Ñ� Ğ¿Ñ€Ğ¸Ğ¼ĞµÑ€Ğ° Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞµĞ¼ Ğ·Ğ°Ğ³Ğ»ÑƒÑˆĞºĞ¸
    text += "ğŸ�½ï¸� <b>ĞŸÑ€Ğ¸ĞµĞ¼Ñ‹ Ğ¿Ğ¸Ñ‰Ğ¸:</b>\n"
    text += "   Ğ—Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº: âœ… Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¾\n"
    text += "   Ğ�Ğ±ĞµĞ´: â�³ Ğ�Ğ¶Ğ¸Ğ´Ğ°ĞµÑ‚Ñ�Ñ�\n"
    text += "   Ğ£Ğ¶Ğ¸Ğ½: â�³ Ğ�Ğ¶Ğ¸Ğ´Ğ°ĞµÑ‚Ñ�Ñ�\n\n"
    
    text += "ğŸ’§ <b>Ğ’Ğ¾Ğ´Ğ°:</b>\n"
    text += "   Ğ¦ĞµĞ»ÑŒ: 2000 Ğ¼Ğ»\n"
    text += "   Ğ’Ñ‹Ğ¿Ğ¸Ñ‚Ğ¾: 1200 Ğ¼Ğ» (60%)\n\n"
    
    text += "ğŸ”¥ <b>ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸:</b>\n"
    text += "   Ğ¦ĞµĞ»ÑŒ: 2000 ĞºĞºĞ°Ğ»\n"
    text += "   ĞŸĞ¾Ñ‚Ñ€ĞµĞ±Ğ»ĞµĞ½Ğ¾: 1450 ĞºĞºĞ°Ğ» (72%)\n\n"
    
    text += "ğŸ�ƒ <b>Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ:</b>\n"
    text += "   Ğ¦ĞµĞ»ÑŒ: 10000 ÑˆĞ°Ğ³Ğ¾Ğ²\n"
    text += "   ĞŸÑ€Ğ¾Ğ¹Ğ´ĞµĞ½Ğ¾: 7500 ÑˆĞ°Ğ³Ğ¾Ğ² (75%)\n"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "progress")
async def progress_callback(callback: CallbackQuery):
    """ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�"""
    await callback.message.edit_text(
        "ğŸ“ˆ <b>Ğ’Ğ°Ñˆ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�</b>\n\n"
        "Ğ˜Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·ÑƒĞ¹Ñ‚Ğµ ĞºĞ¾Ğ¼Ğ°Ğ½Ğ´Ñƒ /progress Ğ´Ğ»Ñ� Ğ´ĞµÑ‚Ğ°Ğ»ÑŒĞ½Ğ¾Ğ¹ Ñ�Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ¸ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ�",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "leaderboard")
async def leaderboard_callback(callback: CallbackQuery):
    """Ğ›Ğ¸Ğ´ĞµÑ€Ğ±Ğ¾Ñ€Ğ´ (Ğ·Ğ°Ğ³Ğ»ÑƒÑˆĞºĞ°)"""
    await callback.message.edit_text(
        "ğŸ�† <b>Ğ›Ğ¸Ğ´ĞµÑ€Ğ±Ğ¾Ñ€Ğ´</b>\n\n"
        "ğŸš§ Ğ¤ÑƒĞ½ĞºÑ†Ğ¸Ñ� Ğ² Ñ€Ğ°Ğ·Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞµ...\n\n"
        "Ğ¡ĞºĞ¾Ñ€Ğ¾ Ğ·Ğ´ĞµÑ�ÑŒ Ğ±ÑƒĞ´ĞµÑ‚ Ñ€ĞµĞ¹Ñ‚Ğ¸Ğ½Ğ³ Ğ»ÑƒÑ‡ÑˆĞ¸Ñ… Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ĞµĞ¹!",
        parse_mode="HTML"
    )
    await callback.answer()
