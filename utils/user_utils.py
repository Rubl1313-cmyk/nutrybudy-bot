"""
utils/user_utils.py
Утилиты для работы с пользователями
"""
import logging
from typing import Optional
from database.db import get_session
from database.models import User
from sqlalchemy import select

logger = logging.getLogger(__name__)

async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """
    Безопасное получение пользователя по telegram_id с полной проверкой
    
    Args:
        telegram_id: Telegram ID пользователя
        
    Returns:
        Optional[User]: Объект пользователя или None если не найден
    """
    try:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                logger.debug(f"✅ User found: {user.id} (telegram_id: {telegram_id})")
            else:
                logger.warning(f"⚠️ User not found: telegram_id {telegram_id}")
                
            return user
            
    except Exception as e:
        logger.error(f"❌ Error getting user {telegram_id}: {e}")
        return None

async def ensure_user_exists(telegram_id: int, username: str = None, first_name: str = None) -> Optional[User]:
    """
    Гарантированное создание пользователя если он не существует
    
    Args:
        telegram_id: Telegram ID пользователя
        username: Имя пользователя в Telegram
        first_name: Имя пользователя
        
    Returns:
        Optional[User]: Объект пользователя (существующий или созданный)
    """
    try:
        # Сначала проверяем существует ли пользователь
        user = await get_user_by_telegram_id(telegram_id)
        
        if user:
            # Обновляем данные если они изменились
            if username and user.username != username:
                user.username = username
                logger.info(f"📝 Updated username for user {user.id}: {username}")
            
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                logger.info(f"📝 Updated first_name for user {user.id}: {first_name}")
            
            # Сохраняем изменения если были
            if username or first_name:
                async with get_session() as session:
                    await session.commit()
                    
            return user
        
        # Создаем нового пользователя
        async with get_session() as session:
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            logger.info(f"👤 Created new user: {new_user.id} (telegram_id: {telegram_id})")
            return new_user
            
    except Exception as e:
        logger.error(f"❌ Error ensuring user exists {telegram_id}: {e}")
        return None

async def is_user_active(telegram_id: int) -> bool:
    """
    Проверяет активен ли пользователь (существует в базе)
    
    Args:
        telegram_id: Telegram ID пользователя
        
    Returns:
        bool: True если пользователь существует, False если нет
    """
    user = await get_user_by_telegram_id(telegram_id)
    return user is not None

async def get_user_profile_completion(user: User) -> dict:
    """
    Возвращает информацию о заполненности профиля пользователя
    
    Args:
        user: Объект пользователя
        
    Returns:
        dict: Информация о заполненности профиля
    """
    completion = {
        'total_fields': 0,
        'filled_fields': 0,
        'completion_percentage': 0,
        'missing_critical': []
    }
    
    # Критически важные поля
    critical_fields = {
        'weight': user.weight,
        'height': user.height,
        'age': user.age,
        'gender': user.gender,
        'activity_level': user.activity_level,
        'goal': user.goal
    }
    
    # Дополнительные поля
    additional_fields = {
        'city': user.city,
        'timezone': user.timezone
    }
    
    all_fields = {**critical_fields, **additional_fields}
    completion['total_fields'] = len(all_fields)
    
    # Считаем заполненные поля
    for field_name, field_value in all_fields.items():
        if field_value is not None and field_value != '':
            completion['filled_fields'] += 1
        elif field_name in critical_fields:
            completion['missing_critical'].append(field_name)
    
    # Процент заполненности
    if completion['total_fields'] > 0:
        completion['completion_percentage'] = (completion['filled_fields'] / completion['total_fields']) * 100
    
    return completion
