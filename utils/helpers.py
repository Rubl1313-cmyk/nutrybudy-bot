from datetime import datetime

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def format_date(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y")

def get_meal_type_emoji(meal_type: str) -> str:
    emojis = {
        'breakfast': '🥐',
        'lunch': '🥗',
        'dinner': '🍲',
        'snack': '🍎'
    }
    return emojis.get(meal_type, '🍽️')

def get_activity_type_emoji(activity_type: str) -> str:
    emojis = {
        'walking': '🚶',
        'running': '🏃',
        'cycling': '🚴',
        'gym': '🏋️',
        'yoga': '🧘',
        'swimming': '🏊',
        'hiit': '💪',
        'stretching': '🤸',
        'dancing': '💃',
        'sports': '⚽'
    }
    return emojis.get(activity_type, '🏃')