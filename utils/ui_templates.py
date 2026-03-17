"""
UI Templates Ğ´Ğ»Ñ� NutriBuddy Bot
ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ñ‹Ğµ ÑˆĞ°Ğ±Ğ»Ğ¾Ğ½Ñ‹ Ğ¸Ğ½Ñ‚ĞµÑ€Ñ„ĞµĞ¹Ñ�Ğ¾Ğ², ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞµĞº, Ğ³Ñ€Ğ°Ñ„Ğ¸ĞºĞ¾Ğ²
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class UITemplates:
    """ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ñ‹Ğµ UI ÑˆĞ°Ğ±Ğ»Ğ¾Ğ½Ñ‹"""
    
    @staticmethod
    def premium_profile_card(user, stats: Dict = None) -> str:
        """ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»Ñ�"""
        lines = [
            f"ğŸ‘¤ <b>{user.first_name or 'ĞŸĞ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ñ‚ĞµĞ»ÑŒ'}</b> Â· Ğ¿Ñ€Ğ¾Ñ„Ğ¸Ğ»ÑŒ",
            "â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€",
            "ğŸ“Š <b>Ğ”Ğ°Ğ½Ğ½Ñ‹Ğµ</b>",
            f"   âš–ï¸� Ğ’ĞµÑ�: <code>{user.weight}</code> ĞºĞ³  |  ğŸ“� Ğ Ğ¾Ñ�Ñ‚: <code>{user.height}</code> Ñ�Ğ¼  |  ğŸ�‚ Ğ’Ğ¾Ğ·Ñ€Ğ°Ñ�Ñ‚: <code>{user.age}</code> Ğ»ĞµÑ‚",
            f"   {('â™‚ï¸�' if user.gender=='male' else 'â™€ï¸�')} ĞŸĞ¾Ğ»: {user.gender}  |  ğŸ�¯ Ğ¦ĞµĞ»ÑŒ: {user.goal}",
            f"   ğŸ�ƒ Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ: {user.activity_level}",
            "",
            "ğŸ“ˆ <b>Ğ’Ğ°ÑˆĞ¸ Ğ½Ğ¾Ñ€Ğ¼Ñ‹</b>",
            f"   ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: <code>{user.daily_calorie_goal:,.0f}</code> ĞºĞºĞ°Ğ»  â–°â–°â–°â–°â–°â–°â–°â–°",
            f"   ğŸ¥© Ğ‘ĞµĞ»ĞºĞ¸: <code>{user.daily_protein_goal:.0f}</code> Ğ³ (30%)    â–°â–°â–°â–°â–±â–±â–±â–±",
            f"   ğŸ¥‘ Ğ–Ğ¸Ñ€Ñ‹: <code>{user.daily_fat_goal:.0f}</code> Ğ³ (30%)      â–°â–°â–°â–°â–±â–±â–±â–±",
            f"   ğŸ�š Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: <code>{user.daily_carbs_goal:.0f}</code> Ğ³ (40%) â–°â–°â–°â–°â–°â–°â–±â–±",
            f"   ğŸ’§ Ğ’Ğ¾Ğ´Ğ°: <code>{user.daily_water_goal:,.0f}</code> Ğ¼Ğ»        â–°â–°â–°â–°â–°â–°â–°â–°â–°â–°"
        ]
        if stats:
            lines.extend([
                "",
                f"âœ¨ <i>Ğ¡ĞµĞ³Ğ¾Ğ´Ğ½Ñ� Ğ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ¾ {stats['progress_percent']:.0f}% Ğ¿Ğ»Ğ°Ğ½Ğ° Ğ¿Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ñ�Ğ¼.</i>"
            ])
        return "\n".join(lines)
    
    @staticmethod
    def premium_progress_card(stats: Dict, period: str) -> str:
        """ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ°"""
        period_icons = {'day': 'ğŸ“…', 'week': 'ğŸ“†', 'month': 'ğŸ“Š'}
        icon = period_icons.get(period, 'ğŸ“Š')
        period_names = {'day': 'Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�', 'week': 'Ğ·Ğ° Ğ½ĞµĞ´ĞµĞ»Ñ�', 'month': 'Ğ·Ğ° Ğ¼ĞµÑ�Ñ�Ñ†'}
        name = period_names.get(period, 'Ğ·Ğ° Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´')
        
        # ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�-Ğ±Ğ°Ñ€Ñ‹
        calorie_progress = min((stats['calories_consumed'] / stats['calorie_goal']) * 100, 100) if stats['calorie_goal'] > 0 else 0
        protein_progress = min((stats['protein_consumed'] / stats['protein_goal']) * 100, 100) if stats['protein_goal'] > 0 else 0
        fat_progress = min((stats['fat_consumed'] / stats['fat_goal']) * 100, 100) if stats['fat_goal'] > 0 else 0
        carbs_progress = min((stats['carbs_consumed'] / stats['carbs_goal']) * 100, 100) if stats['carbs_goal'] > 0 else 0
        water_progress = min((stats['water_consumed'] / stats['water_goal']) * 100, 100) if stats['water_goal'] > 0 else 0
        
        lines = [
            f"{icon} <b>Ğ’Ğ°Ñˆ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� {name}:</b>",
            "â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€",
            f"ğŸ”¥ <b>ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸:</b>",
            f"   {UITemplates.create_progress_bar(stats['calories_consumed'], stats['calorie_goal'])}",
            f"   <code>{stats['calories_consumed']:.0f}</code> / <code>{stats['calorie_goal']:.0f}</code> ĞºĞºĞ°Ğ» ({calorie_progress:.0f}%)",
            "",
            f"ğŸ¥© <b>Ğ‘ĞµĞ»ĞºĞ¸:</b>",
            f"   {UITemplates.create_progress_bar(stats['protein_consumed'], stats['protein_goal'])}",
            f"   <code>{stats['protein_consumed']:.1f}</code> / <code>{stats['protein_goal']:.1f}</code> Ğ³ ({protein_progress:.0f}%)",
            "",
            f"ğŸ¥‘ <b>Ğ–Ğ¸Ñ€Ñ‹:</b>",
            f"   {UITemplates.create_progress_bar(stats['fat_consumed'], stats['fat_goal'])}",
            f"   <code>{stats['fat_consumed']:.1f}</code> / <code>{stats['fat_goal']:.1f}</code> Ğ³ ({fat_progress:.0f}%)",
            "",
            f"ğŸ�š <b>Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹:</b>",
            f"   {UITemplates.create_progress_bar(stats['carbs_consumed'], stats['carbs_goal'])}",
            f"   <code>{stats['carbs_consumed']:.1f}</code> / <code>{stats['carbs_goal']:.1f}</code> Ğ³ ({carbs_progress:.0f}%)",
            "",
            f"ğŸ’§ <b>Ğ’Ğ¾Ğ´Ğ°:</b>",
            f"   {UITemplates.create_progress_bar(stats['water_consumed'], stats['water_goal'])}",
            f"   <code>{stats['water_consumed']:.0f}</code> / <code>{stats['water_goal']:.0f}</code> Ğ¼Ğ» ({water_progress:.0f}%)",
            "",
            f"ğŸ’¬ <i>{UITemplates._get_progress_motivation(calorie_progress)}</i>"
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def create_progress_bar(current: float, total: float, length: int = 12) -> str:
        """Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµÑ‚ Ñ�Ğ¾Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�-Ğ±Ğ°Ñ€"""
        if total <= 0:
            percentage = 0
        else:
            percentage = min((current / total) * 100, 100)
        
        filled = int(length * percentage / 100)
        empty = length - filled
        
        # Ğ“Ñ€Ğ°Ğ´Ğ¸ĞµĞ½Ñ‚ Ğ¾Ñ‚ Ñ�Ğ¸Ğ½ĞµĞ³Ğ¾ Ğº Ğ·Ğ¾Ğ»Ğ¾Ñ‚Ğ¾Ğ¼Ñƒ
        bar = 'ğŸŸ¦' * filled + 'â¬œ' * empty
        
        # Ğ”Ğ¾Ğ±Ğ°Ğ²Ğ»Ñ�ĞµĞ¼ Ğ·Ğ²ĞµĞ·Ğ´Ğ¾Ñ‡ĞºÑƒ ĞµÑ�Ğ»Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� > 90%
        if percentage >= 90 and filled > 0:
            bar = bar[:-1] + 'â­�'
        
        return f"{bar} <code>{percentage:.0f}%</code>"
    
    @staticmethod
    def _get_progress_motivation(calorie_progress: float) -> str:
        """ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ� Ğ¿Ğ¾ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ñƒ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹"""
        if calorie_progress >= 95:
            return "Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ°Ñ� Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°! Ğ’Ñ‹ Ğ¿Ğ¾Ñ‡Ñ‚Ğ¸ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ»Ğ¸ Ñ†ĞµĞ»Ğ¸! ğŸ�¯"
        elif calorie_progress >= 80:
            return "ĞŸÑ€ĞµĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹ Ñ€ĞµĞ·ÑƒĞ»ÑŒÑ‚Ğ°Ñ‚! Ğ¢Ğ°Ğº Ğ´ĞµÑ€Ğ¶Ğ°Ñ‚ÑŒ! âš¡"
        elif calorie_progress >= 60:
            return "Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ¸Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�! ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ² Ñ‚Ğ¾Ğ¼ Ğ¶Ğµ Ğ´ÑƒÑ…Ğµ. âœ¨"
        elif calorie_progress >= 40:
            return "Ğ’Ñ‹ Ğ½Ğ° Ğ²ĞµÑ€Ğ½Ğ¾Ğ¼ Ğ¿ÑƒÑ‚Ğ¸! Ğ�Ğµ Ğ¾Ñ�Ñ‚Ğ°Ğ½Ğ°Ğ²Ğ»Ğ¸Ğ²Ğ°Ğ¹Ñ‚ĞµÑ�ÑŒ. ğŸŒ±"
        elif calorie_progress >= 20:
            return "Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞµĞµ Ğ½Ğ°Ñ‡Ğ°Ğ»Ğ¾! Ğ”ĞµĞ½ÑŒ ĞµÑ‰Ğµ Ğ² Ñ�Ğ°Ğ¼Ğ¾Ğ¼ Ñ€Ğ°Ğ·Ğ³Ğ°Ñ€Ğµ. ğŸ’ª"
        else:
            return "Ğ”ĞµĞ½ÑŒ Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ğ½Ğ°Ñ‡Ğ¸Ğ½Ğ°ĞµÑ‚Ñ�Ñ�! Ğ£ Ğ²Ğ°Ñ� Ğ²Ñ�Ñ‘ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚Ñ�Ñ�. ğŸŒ…"
    
    @staticmethod
    def premium_meal_card(meal_type: str, items: List[Dict], totals: Dict, progress: float) -> str:
        """ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸"""
        meal_icons = {'breakfast': 'ğŸ�³', 'lunch': 'ğŸ�²', 'dinner': 'ğŸ�½ï¸�', 'snack': 'ğŸ��'}
        icon = meal_icons.get(meal_type, 'ğŸ�½ï¸�')
        meal_names = {'breakfast': 'Ğ—Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº', 'lunch': 'Ğ�Ğ±ĞµĞ´', 'dinner': 'Ğ£Ğ¶Ğ¸Ğ½', 'snack': 'ĞŸĞµÑ€ĞµĞºÑƒÑ�'}
        name = meal_names.get(meal_type, 'ĞŸÑ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸')

        items_text = "\n".join([f"   {item['name']} â€“ {item.get('weight', 0)}Ğ³ Â· {item.get('calories', 0)} ĞºĞºĞ°Ğ»" for item in items])

        progress_bar = UITemplates.create_progress_bar(progress, 100)

        return (
            f"{icon} <b>{name} Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½</b>\n"
            f"â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n"
            f"{items_text}\n"
            f"â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n"
            f"ğŸ”¥ <b>Ğ˜Ñ‚Ğ¾Ğ³Ğ¾:</b> <code>{totals['calories']:.0f}</code> ĞºĞºĞ°Ğ» | "
            f"ğŸ¥©<code>{totals['protein']:.1f}</code> | ğŸ¥‘<code>{totals['fat']:.1f}</code> | ğŸ�š<code>{totals['carbs']:.1f}</code>\n\n"
            f"ğŸ“Š <b>ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ´Ğ½Ñ�:</b> {progress:.0f}%\n"
            f"{progress_bar}\n\n"
            f"ğŸ’¬ <i>{UITemplates._get_meal_motivation(progress)}</i>"
        )
    
    @staticmethod
    def _get_meal_motivation(progress: float) -> str:
        """ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ� Ğ¿Ğ¾Ñ�Ğ»Ğµ Ğ¿Ñ€Ğ¸ĞµĞ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸"""
        if progress >= 100:
            return "Ğ¦ĞµĞ»ÑŒ Ğ½Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ� Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ½ÑƒÑ‚Ğ°! Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ°Ñ� Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°! ğŸ�¯"
        elif progress >= 75:
            return "ĞŸÑ€ĞµĞºÑ€Ğ°Ñ�Ğ½Ñ‹Ğ¹ Ñ‚ĞµĞ¼Ğ¿! Ğ�Ñ�Ñ‚Ğ°Ğ»Ğ¾Ñ�ÑŒ Ñ�Ğ¾Ğ²Ñ�ĞµĞ¼ Ğ½ĞµĞ¼Ğ½Ğ¾Ğ³Ğ¾. âš¡"
        elif progress >= 50:
            return "Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ¸Ğ¹ Ñ€ĞµĞ·ÑƒĞ»ÑŒÑ‚Ğ°Ñ‚! ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ² Ñ‚Ğ¾Ğ¼ Ğ¶Ğµ Ğ´ÑƒÑ…Ğµ. âœ¨"
        elif progress >= 25:
            return "Ğ’Ñ‹ Ğ½Ğ° Ğ²ĞµÑ€Ğ½Ğ¾Ğ¼ Ğ¿ÑƒÑ‚Ğ¸. Ğ�Ğµ Ğ¾Ñ�Ñ‚Ğ°Ğ½Ğ°Ğ²Ğ»Ğ¸Ğ²Ğ°Ğ¹Ñ‚ĞµÑ�ÑŒ! ğŸŒ±"
        else:
            return "Ğ”ĞµĞ½ÑŒ Ñ‚Ğ¾Ğ»ÑŒĞºĞ¾ Ğ½Ğ°Ñ‡Ğ¸Ğ½Ğ°ĞµÑ‚Ñ�Ñ�! Ğ£ Ğ²Ğ°Ñ� Ğ²Ñ�Ñ‘ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚Ñ�Ñ�. ğŸ’ª"
    
    @staticmethod
    def premium_ai_card(response: str, model_used: str, tokens_used: int) -> str:
        """ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° AI Ğ¾Ñ‚Ğ²ĞµÑ‚Ğ°"""
        return (
            f"ğŸ¤– <b>AI Ğ�Ñ�Ñ�Ğ¸Ñ�Ñ‚ĞµĞ½Ñ‚:</b>\n"
            f"â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n"
            f"{response}\n\n"
            f"ğŸ”¹ <i>ĞœĞ¾Ğ´ĞµĞ»ÑŒ: {model_used}</i>\n"
            f"ğŸ”¹ <i>Ğ¢Ğ¾ĞºĞµĞ½Ğ¾Ğ² Ğ¸Ñ�Ğ¿Ğ¾Ğ»ÑŒĞ·Ğ¾Ğ²Ğ°Ğ½Ğ¾: {tokens_used}</i>"
        )
    
    @staticmethod
    def premium_water_card(current: int, goal: int, recent_entries: List[Dict]) -> str:
        """ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ²Ğ¾Ğ´Ñ‹"""
        progress = min((current / goal) * 100, 100) if goal > 0 else 0
        progress_bar = UITemplates.create_progress_bar(current, goal)
        
        lines = [
            "ğŸ’§ <b>Ğ’Ğ¾Ğ´Ğ½Ñ‹Ğ¹ Ğ±Ğ°Ğ»Ğ°Ğ½Ñ�</b>",
            "â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€",
            f"ğŸ“Š <b>Ğ¡ĞµĞ³Ğ¾Ğ´Ğ½Ñ� Ğ²Ñ‹Ğ¿Ğ¸Ñ‚Ğ¾:</b>",
            f"   {progress_bar}",
            f"   <code>{current}</code> / <code>{goal}</code> Ğ¼Ğ» ({progress:.0f}%)",
            "",
            f"ğŸ“� <b>ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸:</b>"
        ]
        
        for entry in recent_entries[-3:]:  # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ 3 Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸
            time_str = entry['datetime'].strftime("%H:%M")
            amount = entry['amount']
            lines.append(f"   {time_str} Â· +{amount} Ğ¼Ğ»")
        
        lines.extend([
            "",
            f"ï¿½ <i>{UITemplates._get_water_motivation(progress)}</i>"
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_water_motivation(progress: float) -> str:
        """ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ� Ğ¿Ğ¾ Ğ¿Ğ¾Ñ‚Ñ€ĞµĞ±Ğ»ĞµĞ½Ğ¸Ñ� Ğ²Ğ¾Ğ´Ñ‹"""
        if progress >= 100:
            return "Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾! Ğ�Ğ¾Ñ€Ğ¼Ğ° Ğ²Ğ¾Ğ´Ñ‹ Ğ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ°! ğŸ’§âœ¨"
        elif progress >= 75:
            return "ĞŸĞ¾Ñ‡Ñ‚Ğ¸ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ»Ğ¸ Ñ†ĞµĞ»Ğ¸! Ğ�Ñ�Ñ‚Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ½ĞµĞ¼Ğ½Ğ¾Ğ³Ğ¾! ğŸ’ª"
        elif progress >= 50:
            return "Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ°Ñ� Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°! ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ğ¸Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ! ğŸ’§"
        elif progress >= 25:
            return "Ğ�Ğ°Ñ‡Ğ°Ğ»Ğ¾ Ğ¿Ğ¾Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¾! Ğ�Ğµ Ğ·Ğ°Ğ±Ñ‹Ğ²Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ñ€Ğ¾ Ğ²Ğ¾Ğ´Ñƒ! ğŸ’¦"
        else:
            return "Ğ�Ğ°Ñ‡Ğ¸Ğ½Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ğ¸Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ! Ğ’Ğ°Ğ¶Ğ½Ğ¾ Ğ´Ğ»Ñ� Ğ·Ğ´Ğ¾Ñ€Ğ¾Ğ²ÑŒÑ�! ğŸ’§"
    
    @staticmethod
    def premium_activity_card(activities: List[Dict], total_calories: int) -> str:
        """ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
        lines = [
            "ğŸ�ƒâ€�â™‚ï¸� <b>Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�</b>",
            "â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€",
            f"ğŸ”¥ <b>Ğ¡Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹:</b> <code>{total_calories}</code> ĞºĞºĞ°Ğ»",
            "",
            f"ğŸ“� <b>Ğ—Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸:</b>"
        ]
        
        for activity in activities[-5:]:  # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ 5 Ğ·Ğ°Ğ¿Ğ¸Ñ�ĞµĞ¹
            time_str = activity['datetime'].strftime("%H:%M")
            name = activity['activity_name']
            duration = activity['duration']
            calories = activity['calories_burned']
            lines.append(f"   {time_str} Â· {name} ({duration} Ğ¼Ğ¸Ğ½) Â· {calories} ĞºĞºĞ°Ğ»")
        
        if not activities:
            lines.append("   ĞŸĞ¾ĞºĞ° Ğ½ĞµÑ‚ Ğ·Ğ°Ğ¿Ğ¸Ñ�ĞµĞ¹ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸")
        
        lines.extend([
            "",
            f"ğŸ’¬ <i>Ğ”Ğ²Ğ¸Ğ³Ğ°Ğ¹Ñ‚ĞµÑ�ÑŒ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ Ğ´Ğ»Ñ� Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ� Ñ†ĞµĞ»ĞµĞ¹! ğŸ’ª</i>"
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def premium_weight_card(current_weight: float, goal_weight: float, entries: List[Dict]) -> str:
        """ĞŸÑ€ĞµĞ¼Ğ¸Ğ°Ğ»ÑŒĞ½Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ²ĞµÑ�Ğ°"""
        difference = current_weight - goal_weight
        progress = 0
        
        if goal_weight > 0:
            if difference <= 0:  # Ğ¦ĞµĞ»ÑŒ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ½ÑƒÑ‚Ğ° Ğ¸Ğ»Ğ¸ Ğ¿ĞµÑ€ĞµĞ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ°
                progress = 100
            else:
                # Ğ”Ğ»Ñ� Ğ¿Ğ¾Ñ…ÑƒĞ´ĞµĞ½Ğ¸Ñ�: Ñ�Ñ‡Ğ¸Ñ‚Ğ°ĞµĞ¼ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� ĞºĞ°Ğº Ğ¿Ñ€Ğ¾Ñ†ĞµĞ½Ñ‚ Ğ¾Ñ‚ Ğ¸Ñ�Ñ…Ğ¾Ğ´Ğ½Ğ¾Ğ³Ğ¾ Ğ»Ğ¸ÑˆĞ½ĞµĞ³Ğ¾ Ğ²ĞµÑ�Ğ°
                # Ğ­Ñ‚Ğ¾ ÑƒĞ¿Ñ€Ğ¾Ñ‰ĞµĞ½Ğ½Ñ‹Ğ¹ Ñ€Ğ°Ñ�Ñ‡ĞµÑ‚, Ğ² Ñ€ĞµĞ°Ğ»ÑŒĞ½Ğ¾Ñ�Ñ‚Ğ¸ Ğ½ÑƒĞ¶ĞµĞ½ Ğ½Ğ°Ñ‡Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ²ĞµÑ�
                progress = max(0, min(100, 100 - (difference / abs(goal_weight)) * 100))
        
        lines = [
            "âš–ï¸� <b>Ğ’ĞµÑ� Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�</b>",
            "â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€",
            f"ğŸ“Š <b>Ğ¢ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ�:</b> <code>{current_weight:.1f}</code> ĞºĞ³",
            f"ğŸ�¯ <b>Ğ¦ĞµĞ»ĞµĞ²Ğ¾Ğ¹ Ğ²ĞµÑ�:</b> <code>{goal_weight:.1f}</code> ĞºĞ³",
            f"ğŸ“ˆ <b>Ğ Ğ°Ğ·Ğ½Ğ¸Ñ†Ğ°:</b> <code>{abs(difference):.1f}</code> ĞºĞ³ {'Ğ´Ğ¾ Ñ†ĞµĞ»Ğ¸' if difference > 0 else 'Ğ¿ĞµÑ€ĞµĞ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ¾' if difference < 0 else 'Ñ†ĞµĞ»ÑŒ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ½ÑƒÑ‚Ğ°'}",
            "",
            f"ğŸ“Š <b>ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğº Ñ†ĞµĞ»Ğ¸:</b>",
            f"   {UITemplates.create_progress_bar(progress, 100)}",
            "",
            f"ğŸ“� <b>ĞŸĞ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸:</b>"
        ]
        
        for entry in entries[-3:]:  # ĞŸĞ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¿Ğ¾Ñ�Ğ»ĞµĞ´Ğ½Ğ¸Ğµ 3 Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸
            date_str = entry['datetime'].strftime("%d.%m")
            weight = entry['weight']
            lines.append(f"   {date_str} Â· {weight:.1f} ĞºĞ³")
        
        lines.extend([
            "",
            f"ğŸ’¬ <i>{UITemplates._get_weight_motivation(progress, difference)}</i>"
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_weight_motivation(progress: float, difference: float) -> str:
        """ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ� Ğ¿Ğ¾ Ğ²ĞµÑ�Ñƒ"""
        if difference <= 0:
            return "ĞŸĞ¾Ğ·Ğ´Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼! Ğ¦ĞµĞ»ÑŒ Ğ¿Ğ¾ Ğ²ĞµÑ�Ñƒ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ½ÑƒÑ‚Ğ°! ğŸ�‰"
        elif progress >= 80:
            return "Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾! Ğ’Ñ‹ Ğ¾Ñ‡ĞµĞ½ÑŒ Ğ±Ğ»Ğ¸Ğ·ĞºĞ¾ Ğº Ñ†ĞµĞ»Ğ¸! ğŸ’ª"
        elif progress >= 50:
            return "Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ°Ñ� Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°! ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ² Ñ‚Ğ¾Ğ¼ Ğ¶Ğµ Ğ´ÑƒÑ…Ğµ! âœ¨"
        elif progress >= 25:
            return "Ğ’Ñ‹ Ğ½Ğ° Ğ²ĞµÑ€Ğ½Ğ¾Ğ¼ Ğ¿ÑƒÑ‚Ğ¸! Ğ�Ğµ Ğ¾Ñ�Ñ‚Ğ°Ğ½Ğ°Ğ²Ğ»Ğ¸Ğ²Ğ°Ğ¹Ñ‚ĞµÑ�ÑŒ! ğŸŒ±"
        else:
            return "Ğ�Ğ°Ñ‡Ğ°Ğ»Ğ¾ Ğ¿Ğ¾Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¾! Ğ£ Ğ²Ğ°Ñ� Ğ²Ñ�Ñ‘ Ğ¿Ğ¾Ğ»ÑƒÑ‡Ğ¸Ñ‚Ñ�Ñ�! ğŸ’ª"

class ProgressBar:
    """ğŸ�¯ Ğ¡Ğ¾Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ½Ñ‹Ğµ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�-Ğ±Ğ°Ñ€Ñ‹ Ñ� Ğ³Ñ€Ğ°Ğ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸ Ğ¸ Ğ°Ğ½Ğ¸Ğ¼Ğ°Ñ†Ğ¸ĞµĞ¹"""
    
    # Ğ“Ñ€Ğ°Ğ´Ğ¸ĞµĞ½Ñ‚Ğ½Ñ‹Ğµ Ñ�Ğ¼Ğ¾Ğ´Ğ·Ğ¸ Ğ´Ğ»Ñ� Ñ€Ğ°Ğ·Ğ½Ñ‹Ñ… ÑƒÑ€Ğ¾Ğ²Ğ½ĞµĞ¹
    GRADIENTS = {
        'low': ['ğŸ”´', 'ğŸŸ ', 'ğŸŸ¡'],      # 0-33%
        'medium': ['ğŸŸ¡', 'ğŸŸ¢', 'ğŸ”µ'],    # 34-66%
        'high': ['ğŸ”µ', 'ğŸŸ£', 'ğŸ”·'],     # 67-100%
        'complete': ['ğŸŸ¢', 'âœ¨', 'ğŸ�†']   # 100%
    }
    
    # Ğ�Ğ½Ğ¸Ğ¼Ğ°Ñ†Ğ¸Ğ¾Ğ½Ğ½Ñ‹Ğµ ĞºĞ°Ğ´Ñ€Ñ‹
    ANIMATION_FRAMES = ['âš¡', 'âœ¨', 'ğŸŒŸ', 'ğŸ’«', 'â­�']
    
    @staticmethod
    def create_modern_bar(current: float, total: float, length: int = 12, 
                         style: str = 'gradient', show_text: bool = True) -> str:
        """
        Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµÑ‚ Ñ�Ğ¾Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�-Ğ±Ğ°Ñ€ Ñ� Ğ³Ñ€Ğ°Ğ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸
        
        Args:
            current: Ñ‚ĞµĞºÑƒÑ‰ĞµĞµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ
            total: Ğ¼Ğ°ĞºÑ�Ğ¸Ğ¼Ğ°Ğ»ÑŒĞ½Ğ¾Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ğµ  
            length: Ğ´Ğ»Ğ¸Ğ½Ğ° Ğ±Ğ°Ñ€Ğ°
            style: 'gradient', 'minimal', 'neon'
            show_text: Ğ¿Ğ¾ĞºĞ°Ğ·Ñ‹Ğ²Ğ°Ñ‚ÑŒ Ñ‚ĞµĞºÑ�Ñ‚
        """
        if total <= 0:
            percentage = 0
        else:
            percentage = min((current / total) * 100, 100)
        
        filled = int(length * percentage / 100)
        empty = length - filled
        
        if style == 'gradient':
            # Ğ“Ñ€Ğ°Ğ´Ğ¸ĞµĞ½Ñ‚Ğ½Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ - Ğ¾Ğ´Ğ½Ğ¾Ñ†Ğ²ĞµÑ‚Ğ½Ñ‹Ğ¹
            bar = 'ğŸŸ¦' * filled + 'â¬œ' * empty
        elif style == 'neon':
            # Ğ�ĞµĞ¾Ğ½Ğ¾Ğ²Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ - Ğ¾Ğ´Ğ½Ğ¾Ñ†Ğ²ĞµÑ‚Ğ½Ñ‹Ğ¹
            bar = 'ğŸŸ¦' * filled + 'â¬œ' * empty
        else:
            # ĞœĞ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»Ğ¸Ñ�Ñ‚Ğ¸Ñ‡Ğ½Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ
            bar = 'â–“' * filled + 'â–‘' * empty
        
        if show_text:
            if percentage >= 100:
                return f"{bar} âœ… {percentage:.0f}%"
            elif percentage >= 75:
                return f"{bar} ğŸ”¥ {percentage:.0f}%"
            else:
                return f"{bar} {percentage:.0f}%"
        
        return bar

    @staticmethod
    def create_bar_vertical(current: float, total: float, height: int = 5) -> str:
        """Ğ’ĞµÑ€Ñ‚Ğ¸ĞºĞ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�-Ğ±Ğ°Ñ€"""
        if total <= 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        filled = int(height * current / total) if total > 0 else 0
        
        bars = ["â–�", "â–‚", "â–ƒ", "â–„", "â–…", "â–†", "â–‡", "â–ˆ"]
        return bars[min(int(percentage / 12.5), 7)]

class NutritionCard:
    """ğŸ�¨ Ğ¡Ğ¾Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ½Ñ‹Ğµ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ¸ Ğ¿Ğ¸Ñ‚Ğ°Ğ½Ğ¸Ñ� Ğ² Ñ�Ñ‚Ğ¸Ğ»Ğµ Ñ„Ğ¸Ñ‚Ğ½ĞµÑ�-Ğ¿Ñ€Ğ¸Ğ»Ğ¾Ğ¶ĞµĞ½Ğ¸Ğ¹"""
    
    # Ğ¡Ğ¾Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ½Ñ‹Ğµ Ñ�Ğ¼Ğ¾Ğ´Ğ·Ğ¸ Ğ´Ğ»Ñ� ĞºĞ°Ñ‚ĞµĞ³Ğ¾Ñ€Ğ¸Ğ¹
    MODERN_EMOJIS = {
        'protein': ['ğŸ’ª', 'ğŸ¥©', 'ğŸ�—', 'ğŸ¦´'],
        'carbs': ['ğŸ��', 'ğŸ�š', 'ğŸ¥”', 'ğŸŒ¾'],
        'fat': ['ğŸ¥‘', 'ğŸ§ˆ', 'ğŸ«’', 'ğŸ¥›'],
        'vitamins': ['ğŸ¥¬', 'ğŸ¥•', 'ğŸ�Š', 'ğŸ�“']
    }
    
    @staticmethod
    def create_modern_macro_card(protein: float, fat: float, carbs: float, 
                                calories: float = 0, style: str = 'compact') -> str:
        """
        Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµÑ‚ Ñ�Ğ¾Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ½ÑƒÑ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºÑƒ Ğ¼Ğ°ĞºÑ€Ğ¾Ğ½ÑƒÑ‚Ñ€Ğ¸ĞµĞ½Ñ‚Ğ¾Ğ²
        
        Args:
            style: 'compact', 'detailed', 'minimal'
        """
        total_macros = protein + fat + carbs
        if total_macros == 0:
            return "ğŸ“Š Ğ�ĞµÑ‚ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ… Ğ¾ Ğ¿Ğ¸Ñ‚Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚Ğ¸"
        
        protein_pct = (protein / total_macros) * 100
        fat_pct = (fat / total_macros) * 100
        carbs_pct = (carbs / total_macros) * 100
        
        if style == 'compact':
            # ĞšĞ¾Ğ¼Ğ¿Ğ°ĞºÑ‚Ğ½Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ
            text = (
                f"ğŸ�¯ <b>ĞšĞ‘Ğ–Ğ£</b>\n"
                f"ğŸ’ª {protein:.0f}Ğ³ ({protein_pct:.0f}%) | "
                f"ğŸ¥‘ {fat:.0f}Ğ³ ({fat_pct:.0f}%) | "
                f"ğŸ�š {carbs:.0f}Ğ³ ({carbs_pct:.0f}%)"
            )
            if calories > 0:
                text += f"\nğŸ”¥ {calories:.0f} ĞºĞºĞ°Ğ»"
        elif style == 'detailed':
            # Ğ”ĞµÑ‚Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ Ñ� Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�-Ğ±Ğ°Ñ€Ğ°Ğ¼Ğ¸
            protein_bar = ProgressBar.create_modern_bar(protein, total_macros, 8, 'gradient', False)
            fat_bar = ProgressBar.create_modern_bar(fat, total_macros, 8, 'gradient', False)
            carbs_bar = ProgressBar.create_modern_bar(carbs, total_macros, 8, 'gradient', False)
            
            text = (
                f"ğŸ“Š <b>Ğ�Ğ½Ğ°Ğ»Ğ¸Ğ· Ğ¿Ğ¸Ñ‚Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚Ğ¸</b>\n"
                f"{'â•�' * 35}\n\n"
                f"ğŸ’ª <b>Ğ‘ĞµĞ»ĞºĞ¸</b>\n{protein_bar} {protein:.1f}Ğ³ ({protein_pct:.0f}%)\n\n"
                f"ğŸ¥‘ <b>Ğ–Ğ¸Ñ€Ñ‹</b>\n{fat_bar} {fat:.1f}Ğ³ ({fat_pct:.0f}%)\n\n"
                f"ğŸ�š <b>Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹</b>\n{carbs_bar} {carbs:.1f}Ğ³ ({carbs_pct:.0f}%)"
            )
            if calories > 0:
                text += f"\n\n{'â•�' * 35}\nğŸ”¥ <b>ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸</b>: {calories:.0f} ĞºĞºĞ°Ğ»"
        else:
            # ĞœĞ¸Ğ½Ğ¸Ğ¼Ğ°Ğ»Ğ¸Ñ�Ñ‚Ğ¸Ñ‡Ğ½Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ
            text = f"ğŸ’ª{protein:.0f}g ğŸ¥‘{fat:.0f}g ğŸ�š{carbs:.0f}g"
            if calories > 0:
                text += f" ğŸ”¥{calories:.0f}"
        
        return text

    @staticmethod
    def create_macros_pie_chart(protein: float, fat: float, carbs: float) -> str:
        """
        ĞšÑ€ÑƒĞ³Ğ¾Ğ²Ğ°Ñ� Ğ´Ğ¸Ğ°Ğ³Ñ€Ğ°Ğ¼Ğ¼Ğ° Ğ‘Ğ–Ğ£ (Ñ‚ĞµĞºÑ�Ñ‚Ğ¾Ğ²Ğ°Ñ�)
        ğŸ¥© â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘ 35%
        """
        total = protein + fat + carbs
        if total == 0:
            return "Ğ�ĞµÑ‚ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…"
        
        p_pct = int((protein / total) * 100)
        f_pct = int((fat / total) * 100)
        c_pct = int((carbs / total) * 100)
        
        bar_len = 10
        p_bar = "â–ˆ" * int(p_pct / 10) + "â–‘" * (bar_len - int(p_pct / 10))
        f_bar = "â–ˆ" * int(f_pct / 10) + "â–‘" * (bar_len - int(f_pct / 10))
        c_bar = "â–ˆ" * int(c_pct / 10) + "â–‘" * (bar_len - int(c_pct / 10))
        
        return (
            f"ğŸ¥© {p_bar} {p_pct}%\n"
            f"ğŸ¥‘ {f_bar} {f_pct}%\n"
            f"ğŸ�š {c_bar} {c_pct}%"
        )

    @staticmethod
    def create_modern_daily_goal_card(current_cal: float, goal_cal: float, 
                                     current_protein: float, goal_protein: float,
                                     current_fat: float, goal_fat: float,
                                     current_carbs: float, goal_carbs: float,
                                     style: str = 'modern') -> str:
        """
        Ğ¡Ğ¾Ğ·Ğ´Ğ°ĞµÑ‚ Ñ�Ğ¾Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ½ÑƒÑ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºÑƒ Ğ´Ğ½ĞµĞ²Ğ½Ñ‹Ñ… Ñ†ĞµĞ»ĞµĞ¹ Ñ� Ğ°Ğ½Ğ¸Ğ¼Ğ°Ñ†Ğ¸ĞµĞ¹
        
        Args:
            style: 'modern', 'compact', 'detailed'
        """
        
        # Ğ Ğ°Ñ�Ñ�Ñ‡Ğ¸Ñ‚Ñ‹Ğ²Ğ°ĞµĞ¼ Ğ¿Ñ€Ğ¾Ñ†ĞµĞ½Ñ‚Ñ‹
        cal_pct = min((current_cal / goal_cal * 100) if goal_cal > 0 else 0, 150)
        protein_pct = min((current_protein / goal_protein * 100) if goal_protein > 0 else 0, 150)
        fat_pct = min((current_fat / goal_fat * 100) if goal_fat > 0 else 0, 150)
        carbs_pct = min((current_carbs / goal_carbs * 100) if goal_carbs > 0 else 0, 150)
        
        if style == 'modern':
            # Ğ¡Ğ¾Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ½Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ Ñ� Ğ³Ñ€Ğ°Ğ´Ğ¸ĞµĞ½Ñ‚Ğ°Ğ¼Ğ¸
            cal_bar = ProgressBar.create_modern_bar(current_cal, goal_cal, 12, 'gradient')
            protein_bar = ProgressBar.create_modern_bar(current_protein, goal_protein, 10, 'gradient')
            fat_bar = ProgressBar.create_modern_bar(current_fat, goal_fat, 10, 'gradient')
            carbs_bar = ProgressBar.create_modern_bar(current_carbs, goal_carbs, 10, 'gradient')
            
            # Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµĞ¼ Ñ�Ñ‚Ğ°Ñ‚ÑƒÑ� Ğ´Ğ½Ñ�
            if 90 <= cal_pct <= 110:
                status_emoji = "ğŸ�¯"
                status_text = "Ğ˜Ğ´ĞµĞ°Ğ»ÑŒĞ½Ğ¾!"
            elif cal_pct > 110:
                status_emoji = "âš¡"
                status_text = "Ğ¡Ğ²ĞµÑ€Ñ…Ñ†ĞµĞ»ÑŒ!"
            elif cal_pct >= 75:
                status_emoji = "ğŸ‘�"
                status_text = "Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ¾!"
            else:
                status_emoji = "ğŸ’ª"
                status_text = "Ğ�ÑƒĞ¶Ğ½Ğ¾ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ!"
            
            text = (
                f"{status_emoji} <b>ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ´Ğ½Ñ�</b>\n"
                f"{'â•�' * 40}\n"
                f"ğŸ”¥ <b>ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸</b>\n{cal_bar}\n"
                f"{current_cal:.0f}/{goal_cal:.0f} ĞºĞºĞ°Ğ»\n\n"
                f"ğŸ’ª <b>Ğ‘ĞµĞ»ĞºĞ¸</b>\n{protein_bar}\n"
                f"{current_protein:.0f}/{goal_protein:.0f}Ğ³\n\n"
                f"ğŸ¥‘ <b>Ğ–Ğ¸Ñ€Ñ‹</b>\n{fat_bar}\n"
                f"{current_fat:.0f}/{goal_fat:.0f}Ğ³\n\n"
                f"ğŸ�š <b>Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹</b>\n{carbs_bar}\n"
                f"{current_carbs:.0f}/{goal_carbs:.0f}g\n\n"
                f"{'â•�' * 40}\n"
                f"{status_emoji} <b>{status_text}</b>"
            )
            
        elif style == 'compact':
            # ĞšĞ¾Ğ¼Ğ¿Ğ°ĞºÑ‚Ğ½Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ
            text = (
                f"ï¿½ <b>Ğ”ĞµĞ½ÑŒ</b>\n"
                f"ğŸ”¥ {current_cal:.0f}/{goal_cal:.0f} ({cal_pct:.0f}%)\n"
                f"ï¿½ {current_protein:.0f}/{goal_protein:.0f}Ğ³ ({protein_pct:.0f}%)\n"
                f"ğŸ¥‘ {current_fat:.0f}/{goal_fat:.0f}Ğ³ ({fat_pct:.0f}%)\n"
                f"ğŸ�š {current_carbs:.0f}/{goal_carbs:.0f}Ğ³ ({carbs_pct:.0f}%)"
            )
        else:
            # Ğ”ĞµÑ‚Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ñ�Ñ‚Ğ¸Ğ»ÑŒ
            text = (
                f"ğŸ“ˆ <b>Ğ”ĞµÑ‚Ğ°Ğ»ÑŒĞ½Ñ‹Ğ¹ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ´Ğ½Ñ�</b>\n"
                f"{'â•�' * 45}\n\n"
                f"ğŸ”¥ ĞšĞ�Ğ›Ğ�Ğ Ğ˜Ğ˜: {current_cal:.0f} Ğ¸Ğ· {goal_cal:.0f} ({cal_pct:.1f}%)\n"
                f"ğŸ’ª Ğ‘Ğ•Ğ›ĞšĞ˜: {current_protein:.1f}Ğ³ Ğ¸Ğ· {goal_protein:.0f}Ğ³ ({protein_pct:.1f}%)\n"
                f"ğŸ¥‘ Ğ–Ğ˜Ğ Ğ«: {current_fat:.1f}Ğ³ Ğ¸Ğ· {goal_fat:.0f}Ğ³ ({fat_pct:.1f}%)\n"
                f"ğŸ�š Ğ£Ğ“Ğ›Ğ•Ğ’Ğ�Ğ”Ğ«: {current_carbs:.1f}Ğ³ Ğ¸Ğ· {goal_carbs:.0f}Ğ³ ({carbs_pct:.1f}%)"
            )
        
        return text

class MealCard:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ñ‹Ğµ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ¸ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ¾Ğ² Ğ¿Ğ¸Ñ‰Ğ¸"""
    
    @staticmethod
    def create_meal_summary(meal_type: str, foods: list, total_cal: float, 
                           total_protein: float, total_fat: float, total_carbs: float) -> str:
        """
        ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� Ñ�Ğ²Ğ¾Ğ´ĞºĞ° Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸
        
        Args:
            meal_type: "breakfast", "lunch", "dinner", "snack"
            foods: Ñ�Ğ¿Ğ¸Ñ�Ğ¾Ğº Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ²
            total_cal, total_protein, etc: Ğ¸Ñ‚Ğ¾Ğ³Ğ¾Ğ²Ñ‹Ğµ Ğ·Ğ½Ğ°Ñ‡ĞµĞ½Ğ¸Ñ�
        """
        
        meal_emoji = {
            'breakfast': 'ğŸ¥�',
            'lunch': 'ğŸ¥—',
            'dinner': 'ğŸ�²',
            'snack': 'ğŸ��'
        }
        
        meal_names = {
            'breakfast': 'Ğ—Ğ°Ğ²Ñ‚Ñ€Ğ°Ğº',
            'lunch': 'Ğ�Ğ±ĞµĞ´',
            'dinner': 'Ğ£Ğ¶Ğ¸Ğ½',
            'snack': 'ĞŸĞµÑ€ĞµĞºÑƒÑ�'
        }
        
        emoji = meal_emoji.get(meal_type, 'ğŸ�½ï¸�')
        name = meal_names.get(meal_type, meal_type)
        
        # Ğ¡Ğ¿Ğ¸Ñ�Ğ¾Ğº Ğ¿Ñ€Ğ¾Ğ´ÑƒĞºÑ‚Ğ¾Ğ²
        foods_text = ""
        for i, food in enumerate(foods, 1):
            weight = food.get('weight', 0)
            foods_text += f"{i}. {food['name']}: {weight:.0f}Ğ³\n"
        
        # Ğ˜Ñ‚Ğ¾Ğ³Ğ¸
        text = (
            f"{emoji} <b>{name}</b>\n"
            f"{'â”€' * 30}\n"
            f"{foods_text}\n"
            f"{'â”€' * 30}\n"
            f"ğŸ”¥ {total_cal:.0f} ĞºĞºĞ°Ğ» | ğŸ¥© {total_protein:.1f}Ğ³ | "
            f"ğŸ¥‘ {total_fat:.1f}Ğ³ | ğŸ�š {total_carbs:.1f}Ğ³"
        )
        return text

    @staticmethod
    def create_meal_timeline(meals: list) -> str:
        """
        Ğ’Ñ€ĞµĞ¼ĞµĞ½Ğ½Ğ°Ñ� ÑˆĞºĞ°Ğ»Ğ° Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ¾Ğ² Ğ¿Ğ¸Ñ‰Ğ¸ Ğ·Ğ° Ğ´ĞµĞ½ÑŒ
        
        meals = [
            {'type': 'breakfast', 'time': '08:00', 'cal': 350},
            {'type': 'lunch', 'time': '13:00', 'cal': 680},
            ...
        ]
        """
        
        meal_emoji = {
            'breakfast': 'ğŸ¥�',
            'lunch': 'ğŸ¥—',
            'dinner': 'ğŸ�²',
            'snack': 'ğŸ��'
        }
        
        timeline = "ğŸ“… <b>ĞŸÑ€Ğ¸Ñ‘Ğ¼Ñ‹ Ğ¿Ğ¸Ñ‰Ğ¸</b>\n"
        
        for i, meal in enumerate(meals):
            emoji = meal_emoji.get(meal['type'], 'ğŸ�½ï¸�')
            time = meal.get('time', '??:??')
            cal = meal.get('cal', 0)
            
            if i < len(meals) - 1:
                separator = "â”‚\n"
            else:
                separator = ""
            
            timeline += f"{emoji} {time} â€” {cal:.0f} ĞºĞºĞ°Ğ»\n{separator}"
        
        return timeline

class WaterTracker:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ¾Ğµ Ğ¾Ñ‚Ñ�Ğ»ĞµĞ¶Ğ¸Ğ²Ğ°Ğ½Ğ¸Ğµ Ğ²Ğ¾Ğ´Ñ‹"""
    
    @staticmethod
    def create_water_bottle_chart(current_ml: float, goal_ml: float = 2000) -> str:
        """
        Ğ’Ğ¸Ğ·ÑƒĞ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸Ñ� Ğ±ÑƒÑ‚Ñ‹Ğ»ĞºĞ¸ Ğ²Ğ¾Ğ´Ñ‹
        
        â”�â”�â”�â”�â”�â”�â”“
        â”ƒâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ”ƒ 1500/2000 Ğ¼Ğ» (75%)
        â”ƒâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ”ƒ
        â”ƒâ–‘â–‘â–‘â–‘â–‘â”ƒ
        â”—â”�â”�â”�â”�â”�â”›
        """
        percentage = min((current_ml / goal_ml) * 100, 100)
        filled_lines = int(percentage / 20)
        
        bottle = (
            "â”�â”�â”�â”�â”�â”�â”“\n"
        )
        
        for i in range(5):
            if i < filled_lines:
                bottle += "â”ƒâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ”ƒ\n"
            else:
                bottle += "â”ƒâ–‘â–‘â–‘â–‘â–‘â”ƒ\n"
        
        bottle += "â”—â”�â”�â”�â”�â”�â”›\n"
        bottle += f"ğŸ’§ {current_ml:.0f}/{goal_ml:.0f} Ğ¼Ğ» ({percentage:.0f}%)"
        
        return bottle

    @staticmethod
    def create_water_message(current_ml: float, goal_ml: float = 2000) -> str:
        """ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ğ¾Ğ½Ğ½Ğ¾Ğµ Ñ�Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ Ğ¾ Ğ²Ğ¾Ğ´Ğµ"""
        percentage = min((current_ml / goal_ml) * 100, 100)
        
        if percentage < 25:
            mood = "ğŸ˜´ Ğ�ÑƒĞ¶Ğ½Ğ¾ Ğ¿Ğ¸Ñ‚ÑŒ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ Ğ²Ğ¾Ğ´Ñ‹!"
            emoji = "ğŸ’§"
        elif percentage < 50:
            mood = "ğŸ™‚ Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ¸Ğ¹ Ñ�Ñ‚Ğ°Ñ€Ñ‚!"
            emoji = "ğŸ’§ğŸ’§"
        elif percentage < 75:
            mood = "ğŸ˜Š ĞŸĞ¾Ñ‡Ñ‚Ğ¸ Ğ³Ğ¾Ñ‚Ğ¾Ğ²Ğ¾!"
            emoji = "ğŸ’§ğŸ’§ğŸ’§"
        elif percentage < 100:
            mood = "ğŸ�‰ ĞŸĞ¾Ñ‡Ñ‚Ğ¸ Ñƒ Ñ†ĞµĞ»Ğ¸!"
            emoji = "ğŸ’§ğŸ’§ğŸ’§ğŸ’§"
        else:
            mood = "ğŸ�† Ğ”Ğ½ĞµĞ²Ğ½Ğ°Ñ� Ğ½Ğ¾Ñ€Ğ¼Ğ° Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ½ÑƒÑ‚Ğ°!"
            emoji = "ğŸ’§ğŸ’§ğŸ’§ğŸ’§ğŸ’§"
        
        bar = ProgressBar.create_bar(current_ml, goal_ml, 15)
        
        return (
            f"{emoji} <b>{mood}</b>\n"
            f"{bar}\n"
            f"{current_ml:.0f}/{goal_ml:.0f} Ğ¼Ğ»"
        )

class ActivityCard:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ñ‹Ğµ ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    
    @staticmethod
    def create_activity_card(activity_type: str, duration: int, calories: float) -> str:
        """
        activity_type: 'running', 'gym', 'cycling', 'yoga', 'swimming'
        """
        
        activity_emoji = {
            'running': 'ğŸ�ƒ',
            'gym': 'ğŸ�‹ï¸�',
            'cycling': 'ğŸš´',
            'yoga': 'ğŸ§˜',
            'swimming': 'ğŸ�Š',
            'walking': 'ğŸš¶'
        }
        
        activity_names = {
            'running': 'Ğ‘ĞµĞ³',
            'gym': 'Ğ¢Ñ€ĞµĞ½Ğ°Ğ¶Ñ‘Ñ€Ğ½Ñ‹Ğ¹ Ğ·Ğ°Ğ»',
            'cycling': 'Ğ’ĞµĞ»Ğ¾Ñ�Ğ¸Ğ¿ĞµĞ´',
            'yoga': 'Ğ™Ğ¾Ğ³Ğ°',
            'swimming': 'ĞŸĞ»Ğ°Ğ²Ğ°Ğ½Ğ¸Ğµ',
            'walking': 'Ğ¥Ğ¾Ğ´ÑŒĞ±Ğ°'
        }
        
        emoji = activity_emoji.get(activity_type, 'ğŸ’ª')
        name = activity_names.get(activity_type, activity_type)
        
        # Ğ’Ğ¸Ğ·ÑƒĞ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸Ñ� Ğ²Ñ€ĞµĞ¼ĞµĞ½Ğ¸
        minutes_per_block = 5
        blocks = int(duration / minutes_per_block)
        time_bar = "â�±ï¸� " + "â–ˆ" * blocks + f" {duration} Ğ¼Ğ¸Ğ½"
        
        text = (
            f"{emoji} <b>{name}</b>\n"
            f"{time_bar}\n"
            f"ğŸ”¥ Ğ¡Ğ¾Ğ¶Ğ¶ĞµĞ½Ğ¾: {calories:.0f} ĞºĞºĞ°Ğ»"
        )
        return text

class StreakCard:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ñ‹Ğµ Ñ�ĞµÑ€Ğ¸Ğ¸ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğ¹"""
    
    @staticmethod
    def create_streak_card(streak_days: int, max_streak: int = 0) -> str:
        """Ğ’Ğ¸Ğ·ÑƒĞ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸Ñ� Ñ�ĞµÑ€Ğ¸Ğ¸ Ğ´Ğ½ĞµĞ¹"""
        
        if streak_days == 0:
            return "ğŸ”¥ Ğ�Ğ°Ñ‡Ğ½Ğ¸Ñ‚Ğµ Ñ�ĞµÑ€Ğ¸Ñ� Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�!"
        
        flame_emojis = ["ğŸ”¥"] * min(streak_days, 5)
        
        text = (
            f"{''.join(flame_emojis)} <b>Ğ¡ĞµÑ€Ğ¸Ñ�: {streak_days} Ğ´Ğ½ĞµĞ¹ Ğ¿Ğ¾Ğ´Ñ€Ñ�Ğ´!</b>\n"
            f"ğŸ“ˆ ĞœĞ°ĞºÑ�Ğ¸Ğ¼ÑƒĞ¼: {max_streak} Ğ´Ğ½ĞµĞ¹"
        )
        
        if streak_days >= 7:
            text += "\nğŸ�† Ğ�ĞµĞ´ĞµĞ»Ñ� Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸!"
        if streak_days >= 30:
            text += "\nğŸ‘‘ ĞœĞµÑ�Ñ�Ñ† Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸!"
        if streak_days >= 100:
            text += "\nğŸ’� 100 Ğ´Ğ½ĞµĞ¹! Ğ’Ñ‹ Ğ»ĞµĞ³ĞµĞ½Ğ´Ğ°!"
        
        return text

class StatisticsCard:
    """Ğ¡Ñ‚Ğ°Ñ‚Ğ¸Ñ�Ñ‚Ğ¸ĞºĞ° Ğ¸ Ğ³Ñ€Ğ°Ñ„Ğ¸ĞºĞ¸"""
    
    @staticmethod
    def create_weekly_stats(week_data: list) -> str:
        """
        week_data = [
            {'day': 'ĞŸĞ½', 'cal': 1800, 'achieved': True},
            {'day': 'Ğ’Ñ‚', 'cal': 2100, 'achieved': True},
            ...
        ]
        """
        text = "ğŸ“Š <b>Ğ�ĞµĞ´ĞµĞ»Ñ�</b>\n"
        text += "â”€" * 30 + "\n"
        
        for day_data in week_data:
            day = day_data['day']
            cal = day_data['cal']
            achieved = day_data.get('achieved', False)
            
            status = "âœ…" if achieved else "â�Œ"
            
            # ĞŸÑ€Ğ¾Ñ�Ñ‚Ğ¾Ğ¹ Ğ±Ğ°Ñ€ Ğ´Ğ»Ñ� ĞºĞ°Ğ¶Ğ´Ğ¾Ğ³Ğ¾ Ğ´Ğ½Ñ�
            bar_length = int(cal / 250)
            bar = "â–ˆ" * min(bar_length, 8)
            
            text += f"{status} {day:3} {bar:8} {cal:.0f} ĞºĞºĞ°Ğ»\n"
        
        return text

    @staticmethod
    def create_monthly_heatmap(month_data: dict) -> str:
        """
        month_data = {
            1: {'cal': 1800, 'water': 2000},
            2: {'cal': 2100, 'water': 1500},
            ...
        }
        
        Ğ¡Ğ¾Ğ·Ğ´Ğ°Ñ‘Ñ‚ Ğ²Ğ¸Ğ·ÑƒĞ°Ğ»ÑŒĞ½ÑƒÑ� Ñ‚ĞµĞ¿Ğ»Ğ¾Ğ²ÑƒÑ� ĞºĞ°Ñ€Ñ‚Ñƒ Ğ¼ĞµÑ�Ñ�Ñ†Ğ°
        """
        
        text = "ğŸ”¥ <b>Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ğ¼ĞµÑ�Ñ�Ñ†Ğ°</b>\n"
        text += "ĞŸĞ½  Ğ’Ñ‚  Ğ¡Ñ€  Ğ§Ñ‚  ĞŸÑ‚  Ğ¡Ğ±  Ğ’Ñ�\n"
        
        # Ğ£Ñ�Ğ»Ğ¾Ğ²Ğ½Ñ‹Ğµ ÑƒÑ€Ğ¾Ğ²Ğ½Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
        def get_heat_emoji(calories: float) -> str:
            if calories >= 2200:
                return "ğŸ”¥"  # Ğ�Ñ‡ĞµĞ½ÑŒ Ğ°ĞºÑ‚Ğ¸Ğ²ĞµĞ½
            elif calories >= 1800:
                return "ğŸŸ "  # Ğ�ĞºÑ‚Ğ¸Ğ²ĞµĞ½
            elif calories >= 1400:
                return "ğŸŸ¡"  # Ğ�Ğ¾Ñ€Ğ¼
            elif calories > 0:
                return "ğŸŸ¢"  # ĞœĞ°Ğ»Ğ¾
            else:
                return "â¬œ"  # Ğ�ĞµÑ‚ Ğ´Ğ°Ğ½Ğ½Ñ‹Ñ…
        
        # Ğ£Ğ¿Ñ€Ğ¾Ñ‰Ñ‘Ğ½Ğ½Ğ°Ñ� Ğ²Ğ¸Ğ·ÑƒĞ°Ğ»Ğ¸Ğ·Ğ°Ñ†Ğ¸Ñ� (1 Ñ�Ñ‚Ñ€Ğ¾ĞºĞ° Ğ½Ğ° Ğ½ĞµĞ´ĞµĞ»Ñ�)
        week = []
        for day in range(1, 32):
            if day in month_data:
                cal = month_data[day].get('cal', 0)
                week.append(get_heat_emoji(cal))
            else:
                week.append("â¬œ")
            
            if len(week) == 7:
                text += " ".join(week) + "\n"
                week = []
        
        if week:
            text += " ".join(week) + "\n"
        
        return text
