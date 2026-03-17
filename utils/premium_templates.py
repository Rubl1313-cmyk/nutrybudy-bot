"""
utils/premium_templates.py
ĞŸÑ€ĞµĞ¼Ğ¸ÑƒĞ¼-ÑˆĞ°Ğ±Ğ»Ğ¾Ğ½Ñ‹ Ğ´Ğ»Ñ� ĞºÑ€Ğ°Ñ�Ğ¸Ğ²Ñ‹Ñ… Ğ¾Ñ‚Ğ²ĞµÑ‚Ğ¾Ğ² Ğ±Ğ¾Ñ‚Ğ° Ñ� Ñ�Ğ¼Ğ¾Ğ´Ğ·Ğ¸ Ğ¸ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�-Ğ±Ğ°Ñ€Ğ°Ğ¼Ğ¸
"""
from typing import Dict, Optional
from utils.ui_templates import ProgressBar

def meal_card(food_data: Dict, user, daily_stats: Dict) -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ‘Ğ½Ğ½Ğ¾Ğ³Ğ¾ Ğ¿Ñ€Ğ¸Ñ‘Ğ¼Ğ° Ğ¿Ğ¸Ñ‰Ğ¸"""
    calories = food_data.get('calories', 0)
    protein = food_data.get('protein', 0)
    fat = food_data.get('fat', 0)
    carbs = food_data.get('carbs', 0)
    description = food_data.get('description', 'Ğ‘Ğ»Ñ�Ğ´Ğ¾')
    
    # ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ¿Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ñ�Ğ¼
    cal_progress = (daily_stats.get('calories', 0) / user.daily_calorie_goal * 100) if user.daily_calorie_goal else 0
    cal_bar = ProgressBar.create_modern_bar(cal_progress, 100, 12, 'neon')
    
    # ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ¿Ğ¾ Ğ‘Ğ–Ğ£
    protein_progress = (daily_stats.get('protein', 0) / user.daily_protein_goal * 100) if user.daily_protein_goal else 0
    protein_bar = ProgressBar.create_modern_bar(protein_progress, 100, 8, 'protein')
    
    fat_progress = (daily_stats.get('fat', 0) / user.daily_fat_goal * 100) if user.daily_fat_goal else 0
    fat_bar = ProgressBar.create_modern_bar(fat_progress, 100, 8, 'fat')
    
    carbs_progress = (daily_stats.get('carbs', 0) / user.daily_carbs_goal * 100) if user.daily_carbs_goal else 0
    carbs_bar = ProgressBar.create_modern_bar(carbs_progress, 100, 8, 'carbs')
    
    return f"""
ğŸ�½ï¸� <b>ĞŸÑ€Ğ¸Ñ‘Ğ¼ Ğ¿Ğ¸Ñ‰Ğ¸ Ñ�Ğ¾Ñ…Ñ€Ğ°Ğ½Ñ‘Ğ½!</b>

{'â•�' * 35}
ğŸ�² <b>{description}</b>

ğŸ”¥ <b>ĞŸĞ¸Ñ‚Ğ°Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ:</b>
ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {calories:.0f} ĞºĞºĞ°Ğ»
ğŸ¥© Ğ‘ĞµĞ»ĞºĞ¸: {protein:.1f} Ğ³
ğŸ¥‘ Ğ–Ğ¸Ñ€Ñ‹: {fat:.1f} Ğ³
ğŸ�š Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {carbs:.1f} Ğ³

ğŸ“Š <b>Ğ’Ğ°Ñˆ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�</b>
{'â•�' * 35}
ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {daily_stats.get('calories', 0):.0f}/{user.daily_calorie_goal} ĞºĞºĞ°Ğ» ({cal_progress:.0f}%)
{cal_bar} {cal_progress:.0f}%

ğŸ¥© Ğ‘ĞµĞ»ĞºĞ¸: {daily_stats.get('protein', 0):.1f}/{user.daily_protein_goal} Ğ³ ({protein_progress:.0f}%)
{protein_bar} {protein_progress:.0f}%

ğŸ¥‘ Ğ–Ğ¸Ñ€Ñ‹: {daily_stats.get('fat', 0):.1f}/{user.daily_fat_goal} Ğ³ ({fat_progress:.0f}%)
{fat_bar} {fat_progress:.0f}%

ğŸ�š Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {daily_stats.get('carbs', 0):.1f}/{user.daily_carbs_goal} Ğ³ ({carbs_progress:.0f}%)
{carbs_bar} {carbs_progress:.0f}%

ğŸ’ª <b>Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ°Ñ� Ñ€Ğ°Ğ±Ğ¾Ñ‚Ğ°!</b> ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ² Ñ‚Ğ¾Ğ¼ Ğ¶Ğµ Ğ´ÑƒÑ…Ğµ!
"""

def water_card(amount: int, total_today: int, goal: int) -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²Ğ¾Ğ´Ñ‹"""
    progress = (total_today / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'water')
    
    # ĞœĞ¾Ñ‚Ğ¸Ğ²Ğ°Ñ†Ğ¸Ñ�
    if progress >= 100:
        motivation = "ğŸ�‰ <b>Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ°Ñ� Ğ³Ğ¸Ğ´Ñ€Ğ°Ñ‚Ğ°Ñ†Ğ¸Ñ�!</b> Ğ¦ĞµĞ»ÑŒ Ğ¿Ğ¾ Ğ²Ğ¾Ğ´Ğµ Ğ²Ñ‹Ğ¿Ğ¾Ğ»Ğ½ĞµĞ½Ğ°!"
    elif progress >= 75:
        motivation = "ğŸ’ª <b>Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾!</b> Ğ�Ñ�Ñ‚Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ½ĞµĞ¼Ğ½Ğ¾Ğ³Ğ¾!"
    elif progress >= 50:
        motivation = "ğŸ‘� <b>Ğ¥Ğ¾Ñ€Ğ¾ÑˆĞ¾!</b> ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ¿Ğ¸Ñ‚ÑŒ Ğ²Ğ¾Ğ´Ñƒ."
    else:
        remaining = goal - total_today
        motivation = f"ğŸ’§ <b>Ğ�ÑƒĞ¶Ğ½Ğ¾ Ğ±Ğ¾Ğ»ÑŒÑˆĞµ Ğ²Ğ¾Ğ´Ñ‹!</b> Ğ�Ñ�Ñ‚Ğ°Ğ»Ğ¾Ñ�ÑŒ Ğ²Ñ‹Ğ¿Ğ¸Ñ‚ÑŒ {remaining:.0f} Ğ¼Ğ»."
    
    return f"""
ğŸ’§ <b>Ğ’Ğ¾Ğ´Ğ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ°!</b>

{'â•�' * 35}
â�• <b>Ğ’Ñ‹Ğ¿Ğ¸Ñ‚Ğ¾:</b> {amount} Ğ¼Ğ»
ğŸ“Š <b>Ğ’Ñ�ĞµĞ³Ğ¾ Ğ·Ğ° Ğ´ĞµĞ½ÑŒ:</b> {total_today} Ğ¼Ğ»
ğŸ�¯ <b>Ğ¦ĞµĞ»ÑŒ:</b> {goal} Ğ¼Ğ»

{bar} {progress:.0f}%

{motivation}
"""

def drink_card(amount: int, drink_name: str, calories: float, total_today: int, total_calories: int, goal: int) -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°"""
    progress = (total_today / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'water')
    
    # Ğ˜ĞºĞ¾Ğ½ĞºĞ° Ğ´Ğ»Ñ� Ñ‚Ğ¸Ğ¿Ğ° Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ°
    drink_icons = {
        'Ğ²Ğ¾Ğ´Ğ°': 'ğŸ’§',
        'Ñ�Ğ¾Ğº': 'ğŸ§ƒ',
        'Ñ‡Ğ°Ğ¹': 'ğŸ�µ',
        'ĞºĞ¾Ñ„Ğµ': 'â˜•',
        'Ğ¼Ğ¾Ğ»Ğ¾ĞºĞ¾': 'ğŸ¥›',
        'ĞºĞµÑ„Ğ¸Ñ€': 'ğŸ¥›',
        'Ğ³Ğ°Ğ·Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°': 'ğŸ¥¤',
        'ĞºĞ¾Ğ¼Ğ¿Ğ¾Ñ‚': 'ğŸ�¹',
        'Ñ�Ğ¼ÑƒĞ·Ğ¸': 'ğŸ¥¤',
        'ĞºĞ¾ĞºÑ‚ĞµĞ¹Ğ»ÑŒ': 'ğŸ�¹'
    }
    icon = drink_icons.get(drink_name.lower(), 'ğŸ¥¤')
    
    return f"""
{icon} <b>Ğ�Ğ°Ğ¿Ğ¸Ñ‚Ğ¾Ğº Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½!</b>

{'â•�' * 35}
ğŸ¥¤ <b>{drink_name.title()}:</b> {amount} Ğ¼Ğ»
ğŸ”¥ <b>ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸:</b> {calories:.0f} ĞºĞºĞ°Ğ»

ğŸ“Š <b>Ğ’Ñ�ĞµĞ³Ğ¾ Ğ·Ğ° Ñ�ĞµĞ³Ğ¾Ğ´Ğ½Ñ�:</b>
ğŸ’¦ Ğ–Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ: {total_today} Ğ¼Ğ»
ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸ Ğ¸Ğ· Ğ½Ğ°Ğ¿Ğ¸Ñ‚ĞºĞ¾Ğ²: {total_calories:.0f} ĞºĞºĞ°Ğ»
ğŸ�¯ Ğ¦ĞµĞ»ÑŒ Ğ¿Ğ¾ Ğ¶Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚Ğ¸: {goal} Ğ¼Ğ»

{bar} {progress:.0f}%

ğŸ’ª <b>Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ¾!</b> ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ñ�Ğ»ĞµĞ´Ğ¸Ñ‚ÑŒ Ğ·Ğ° Ğ±Ğ°Ğ»Ğ°Ğ½Ñ�Ğ¾Ğ¼!
"""

def weight_card(weight: float, change: Optional[float] = None, goal: Optional[float] = None) -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ²ĞµÑ�Ğ°"""
    # Ğ�Ğ¿Ñ€ĞµĞ´ĞµĞ»Ñ�ĞµĞ¼ Ğ¸Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ
    if change is not None:
        if change > 0:
            change_text = f"ğŸ“ˆ +{change:.1f} ĞºĞ³"
            change_emoji = "ğŸ“ˆ"
        elif change < 0:
            change_text = f"ğŸ“‰ {change:.1f} ĞºĞ³"
            change_emoji = "ğŸ“‰"
        else:
            change_text = "â�¡ï¸� 0.0 ĞºĞ³"
            change_emoji = "â�¡ï¸�"
    else:
        change_text = ""
        change_emoji = ""
    
    # ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğº Ñ†ĞµĞ»Ğ¸
    progress_text = ""
    if goal is not None:
        diff = goal - weight
        if diff > 0:
            progress_text = f"ğŸ�¯ Ğ”Ğ¾ Ñ†ĞµĞ»Ğ¸: {diff:.1f} ĞºĞ³"
        elif diff < 0:
            progress_text = f"ğŸ�† Ğ¦ĞµĞ»ÑŒ Ğ¿Ñ€ĞµĞ²Ñ‹ÑˆĞµĞ½Ğ° Ğ½Ğ° {abs(diff):.1f} ĞºĞ³!"
        else:
            progress_text = "ğŸ�‰ Ğ¦ĞµĞ»ÑŒ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ³Ğ½ÑƒÑ‚Ğ°!"
    
    return f"""
âš–ï¸� <b>Ğ’ĞµÑ� Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½!</b>

{'â•�' * 35}
ğŸ�‹ï¸� <b>Ğ¢ĞµĞºÑƒÑ‰Ğ¸Ğ¹ Ğ²ĞµÑ�:</b> {weight:.1f} ĞºĞ³
{change_emoji} <b>Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ:</b> {change_text}
{progress_text}

ğŸ’ª <b>ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ¾Ñ‚Ñ�Ğ»ĞµĞ¶Ğ¸Ğ²Ğ°Ñ‚ÑŒ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�!</b>
"""

def activity_card(activity_type: str, duration: int, calories: float, daily_total: int, goal: int) -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ¸ Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸"""
    progress = (daily_total / goal * 100) if goal > 0 else 0
    bar = ProgressBar.create_modern_bar(progress, 100, 12, 'activity')
    
    # Ğ˜ĞºĞ¾Ğ½ĞºĞ¸ Ğ´Ğ»Ñ� Ñ‚Ğ¸Ğ¿Ğ¾Ğ² Ğ°ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚Ğ¸
    activity_icons = {
        'Ğ±ĞµĞ³': 'ğŸ�ƒ',
        'Ñ…Ğ¾Ğ´ÑŒĞ±Ğ°': 'ğŸš¶',
        'Ğ²ĞµĞ»Ğ¾Ñ�Ğ¸Ğ¿ĞµĞ´': 'ğŸš´',
        'Ğ¿Ğ»Ğ°Ğ²Ğ°Ğ½Ğ¸Ğµ': 'ğŸ�Š',
        'Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°': 'ğŸ’ª',
        'Ğ¹Ğ¾Ğ³Ğ°': 'ğŸ§˜',
        'Ñ„Ğ¸Ñ‚Ğ½ĞµÑ�': 'ğŸ�‹ï¸�'
    }
    icon = activity_icons.get(activity_type.lower(), 'ğŸ�ƒ')
    
    return f"""
{icon} <b>Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ Ğ·Ğ°Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ°!</b>

{'â•�' * 35}
ğŸ�ƒ <b>Ğ¢Ğ¸Ğ¿:</b> {activity_type.title()}
â�±ï¸� <b>Ğ”Ğ»Ğ¸Ñ‚ĞµĞ»ÑŒĞ½Ğ¾Ñ�Ñ‚ÑŒ:</b> {duration} Ğ¼Ğ¸Ğ½
ğŸ”¥ <b>ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸:</b> {calories:.0f} ĞºĞºĞ°Ğ»

ğŸ“Š <b>ĞŸÑ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ·Ğ° Ğ´ĞµĞ½ÑŒ:</b>
ğŸ”¥ Ğ’Ñ�ĞµĞ³Ğ¾ Ğ¿Ğ¾Ñ‚Ñ€Ğ°Ñ‡ĞµĞ½Ğ¾: {daily_total} ĞºĞºĞ°Ğ»
ğŸ�¯ Ğ¦ĞµĞ»ÑŒ: {goal} ĞºĞºĞ°Ğ»

{bar} {progress:.0f}%

ğŸ’ª <b>Ğ�Ñ‚Ğ»Ğ¸Ñ‡Ğ½Ğ°Ñ� Ñ‚Ñ€ĞµĞ½Ğ¸Ñ€Ğ¾Ğ²ĞºĞ°!</b>
"""

def progress_card(stats: Dict, period: str = "Ğ´ĞµĞ½ÑŒ") -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ�Ğ° Ğ·Ğ° Ğ¿ĞµÑ€Ğ¸Ğ¾Ğ´"""
    period_icons = {
        'Ğ´ĞµĞ½ÑŒ': 'ğŸ“…',
        'Ğ½ĞµĞ´ĞµĞ»Ñ�': 'ğŸ“†',
        'Ğ¼ĞµÑ�Ñ�Ñ†': 'ğŸ“Š',
        'Ğ²Ñ�Ñ‘ Ğ²Ñ€ĞµĞ¼Ñ�': 'ğŸ�†'
    }
    icon = period_icons.get(period.lower(), 'ğŸ“Š')
    
    return f"""
{icon} <b>Ğ’Ğ°Ñˆ Ğ¿Ñ€Ğ¾Ğ³Ñ€ĞµÑ�Ñ� Ğ·Ğ° {period}</b>

{'â•�' * 35}
ğŸ�½ï¸� <b>ĞŸĞ¸Ñ‚Ğ°Ğ½Ğ¸Ğµ:</b>
ğŸ”¥ ĞšĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¸: {stats.get('avg_calories', 0):.0f} ĞºĞºĞ°Ğ»/Ğ´ĞµĞ½ÑŒ
ğŸ¥© Ğ‘ĞµĞ»ĞºĞ¸: {stats.get('avg_protein', 0):.1f} Ğ³/Ğ´ĞµĞ½ÑŒ
ğŸ¥‘ Ğ–Ğ¸Ñ€Ñ‹: {stats.get('avg_fat', 0):.1f} Ğ³/Ğ´ĞµĞ½ÑŒ
ğŸ�š Ğ£Ğ³Ğ»ĞµĞ²Ğ¾Ğ´Ñ‹: {stats.get('avg_carbs', 0):.1f} Ğ³/Ğ´ĞµĞ½ÑŒ

ğŸ’§ <b>Ğ“Ğ¸Ğ´Ñ€Ğ°Ñ‚Ğ°Ñ†Ğ¸Ñ�:</b>
ğŸ’¦ Ğ–Ğ¸Ğ´ĞºĞ¾Ñ�Ñ‚ÑŒ: {stats.get('avg_water', 0):.0f} Ğ¼Ğ»/Ğ´ĞµĞ½ÑŒ

âš–ï¸� <b>Ğ’ĞµÑ�:</b>
ğŸ�‹ï¸� Ğ˜Ğ·Ğ¼ĞµĞ½ĞµĞ½Ğ¸Ğµ: {stats.get('weight_change', 0):+.1f} ĞºĞ³

ğŸ�ƒ <b>Ğ�ĞºÑ‚Ğ¸Ğ²Ğ½Ğ¾Ñ�Ñ‚ÑŒ:</b>
ğŸ”¥ ĞŸĞ¾Ñ‚Ñ€Ğ°Ñ‡ĞµĞ½Ğ¾ ĞºĞ°Ğ»Ğ¾Ñ€Ğ¸Ğ¹: {stats.get('total_activity', 0):.0f} ĞºĞºĞ°Ğ»

ğŸ’ª <b>ĞŸÑ€Ğ¾Ğ´Ğ¾Ğ»Ğ¶Ğ°Ğ¹Ñ‚Ğµ Ğ² Ñ‚Ğ¾Ğ¼ Ğ¶Ğµ Ğ´ÑƒÑ…Ğµ!</b>
"""

def achievement_card(achievement: Dict) -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ñ�"""
    icons = {
        'bronze': 'ğŸ¥‰',
        'silver': 'ğŸ¥ˆ',
        'gold': 'ğŸ¥‡',
        'platinum': 'ğŸ�†',
        'diamond': 'ğŸ’�'
    }
    
    icon = icons.get(achievement.get('rarity', 'bronze'), 'ğŸ¥‰')
    
    return f"""
ğŸ�‰ <b>Ğ�Ğ¾Ğ²Ğ¾Ğµ Ğ´Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğµ!</b>

{'â•�' * 35}
{icon} <b>{achievement.get('name', 'Ğ”Ğ¾Ñ�Ñ‚Ğ¸Ğ¶ĞµĞ½Ğ¸Ğµ')}</b>

ğŸ“� <b>Ğ�Ğ¿Ğ¸Ñ�Ğ°Ğ½Ğ¸Ğµ:</b> {achievement.get('description', '')}

ğŸ�¯ <b>ĞšĞ°Ñ‚ĞµĞ³Ğ¾Ñ€Ğ¸Ñ�:</b> {achievement.get('category', 'Ğ�Ğ±Ñ‰ĞµĞµ')}

â­� <b>Ğ ĞµĞ´ĞºĞ¾Ñ�Ñ‚ÑŒ:</b> {achievement.get('rarity', 'Ğ¾Ğ±Ñ‹Ñ‡Ğ½Ğ¾Ğµ').title()}

ğŸ�Š <b>ĞŸĞ¾Ğ·Ğ´Ñ€Ğ°Ğ²Ğ»Ñ�ĞµĞ¼!</b> Ğ’Ñ‹ Ğ¼Ğ¾Ğ»Ğ¾Ğ´ĞµÑ†!
"""

def error_card(error_type: str, message: str) -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ¸"""
    error_icons = {
        'validation': 'âš ï¸�',
        'database': 'ğŸ—„ï¸�',
        'ai': 'ğŸ¤–',
        'network': 'ğŸŒ�',
        'general': 'â�Œ'
    }
    
    icon = error_icons.get(error_type, 'â�Œ')
    
    return f"""
{icon} <b>ĞŸÑ€Ğ¾Ğ¸Ğ·Ğ¾ÑˆĞ»Ğ° Ğ¾ÑˆĞ¸Ğ±ĞºĞ°</b>

{'â•�' * 35}
ğŸ“� <b>Ğ¢Ğ¸Ğ¿:</b> {error_type.title()}
ğŸ’¬ <b>Ğ¡Ğ¾Ğ¾Ğ±Ñ‰ĞµĞ½Ğ¸Ğµ:</b> {message}

ğŸ”§ <b>Ğ§Ñ‚Ğ¾ Ğ´ĞµĞ»Ğ°Ñ‚ÑŒ:</b> ĞŸĞ¾Ğ¿Ñ€Ğ¾Ğ±ÑƒĞ¹Ñ‚Ğµ ĞµÑ‰Ñ‘ Ñ€Ğ°Ğ· Ğ¸Ğ»Ğ¸ Ğ¾Ğ±Ñ€Ğ°Ñ‚Ğ¸Ñ‚ĞµÑ�ÑŒ Ğ² Ğ¿Ğ¾Ğ´Ğ´ĞµÑ€Ğ¶ĞºÑƒ.

ğŸ’¡ <b>Ğ¡Ğ¾Ğ²ĞµÑ‚:</b> Ğ•Ñ�Ğ»Ğ¸ Ğ¾ÑˆĞ¸Ğ±ĞºĞ° Ğ¿Ğ¾Ğ²Ñ‚Ğ¾Ñ€Ñ�ĞµÑ‚Ñ�Ñ�, Ğ²Ğ¾Ğ·Ğ¼Ğ¾Ğ¶Ğ½Ğ¾, Ğ½ÑƒĞ¶Ğ½Ğ¾ Ğ¿Ñ€Ğ¾Ğ²ĞµÑ€Ğ¸Ñ‚ÑŒ Ğ½Ğ°Ñ�Ñ‚Ñ€Ğ¾Ğ¹ĞºĞ¸.
"""

def loading_card(operation: str) -> str:
    """ĞšÑ€Ğ°Ñ�Ğ¸Ğ²Ğ°Ñ� ĞºĞ°Ñ€Ñ‚Ğ¾Ñ‡ĞºĞ° Ğ·Ğ°Ğ³Ñ€ÑƒĞ·ĞºĞ¸"""
    loading_icons = {
        'photo': 'ğŸ“¸',
        'voice': 'ğŸ�¤',
        'analysis': 'ğŸ”�',
        'saving': 'ğŸ’¾',
        'stats': 'ğŸ“Š'
    }
    
    icon = loading_icons.get(operation, 'â�³')
    
    return f"""
{icon} <b>Ğ�Ğ±Ñ€Ğ°Ğ±Ğ¾Ñ‚ĞºĞ°...</b>

{'â•�' * 35}
â�³ ĞŸĞ¾Ğ¶Ğ°Ğ»ÑƒĞ¹Ñ�Ñ‚Ğ°, Ğ¿Ğ¾Ğ´Ğ¾Ğ¶Ğ´Ğ¸Ñ‚Ğµ Ğ½ĞµĞ¼Ğ½Ğ¾Ğ³Ğ¾...

ğŸ¤– AI Ğ°Ğ½Ğ°Ğ»Ğ¸Ğ·Ğ¸Ñ€ÑƒĞµÑ‚ Ğ²Ğ°Ñˆ Ğ·Ğ°Ğ¿Ñ€Ğ¾Ñ�...

âš¡ Ğ­Ñ‚Ğ¾ Ğ¼Ğ¾Ğ¶ĞµÑ‚ Ğ·Ğ°Ğ½Ñ�Ñ‚ÑŒ Ğ½ĞµÑ�ĞºĞ¾Ğ»ÑŒĞºĞ¾ Ñ�ĞµĞºÑƒĞ½Ğ´.
"""
