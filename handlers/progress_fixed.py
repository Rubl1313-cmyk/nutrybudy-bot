async def show_today_progress(message: Message):
    """Показать прогресс за сегодня"""
    user_id = message.from_user.id
    
    try:
        # Получаем статистику за сегодня
        stats = await get_today_stats(user_id)
        
        if not stats:
            text = "📅 <b>Прогресс за сегодня</b>\n\n"
            text += "У вас еще нет записей на сегодня.\n\n"
            text += "🚀 <b>Начните отслеживать:</b>\n"
            text += "• /food - записать прием пищи\n"
            text += "• /water - выпить воды\n"
            text += "• /fitness - записать активность\n"
            text += "• /weight - записать вес"
            
            await message.answer(text, reply_markup=get_main_keyboard_v2())
            return
        
        # Получаем цели пользователя
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
        if not user:
            await message.answer("❌ Профиль не найден", reply_markup=get_cancel_keyboard())
            return
        
        text = "📅 <b>Прогресс за сегодня</b>\n\n"
        
        # Питание
        if stats['calories_consumed'] > 0:
            calorie_progress = min(stats['calories_consumed'] / user.daily_calorie_goal * 100, 100)
            calorie_bar = ProgressBar.create_modern_bar(calorie_progress, 100, 15, 'neon')
            
            text += f"🍽️ <b>Питание:</b>\n"
            text += f"   Калории: {stats['calories_consumed']}/{user.daily_calorie_goal} ккал\n"
            text += f"   Прогресс: {calorie_bar}\n"
            
            if stats['protein_consumed'] > 0:
                protein_progress = min(stats['protein_consumed'] / user.daily_protein_goal * 100, 100)
                protein_bar = ProgressBar.create_modern_bar(protein_progress, 100, 12, 'protein')
                text += f"   Белки: {stats['protein_consumed']:.1f}/{user.daily_protein_goal} г {protein_bar}\n"
            
            if stats['water_consumed'] > 0:
                water_progress = min(stats['water_consumed'] / user.daily_water_goal * 100, 100)
                water_bar = ProgressBar.create_modern_bar(water_progress, 100, 12, 'water')
                text += f"   Вода: {stats['water_consumed']}/{user.daily_water_goal} мл {water_bar}\n"
            
            text += "\n"
        
        # Активность
        if stats['activity_minutes'] > 0:
            activity_progress = min(stats['activity_minutes'] / 60 * 100, 100)  # Цель 60 минут
            activity_bar = ProgressBar.create_modern_bar(activity_progress, 100, 12, 'activity')
            
            text += f"🏃‍♂️ <b>Активность:</b>\n"
            text += f"   Минуты: {stats['activity_minutes']}/60 мин\n"
            text += f"   Прогресс: {activity_bar}\n"
            text += f"   Калории сожжено: {stats['calories_burned']:.0f} ккал\n\n"
        
        # Вес
        if stats.get('weight'):
            text += f"⚖️ <b>Вес:</b>\n"
            text += f"   Текущий: {stats['weight']} кг\n"
            if stats.get('weight_change'):
                change = stats['weight_change']
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                text += f"   Изменение: {emoji} {abs(change):.1f} кг\n\n"
        
        # Мотивация
        text += get_motivation_message(stats, user)
        
        await message.answer(text, reply_markup=get_main_keyboard_v2())
        
    except Exception as e:
        logger.error(f"Error in show_today_progress: {e}")
        await message.answer(
            "⚠️ Временная проблема с базой данных. Попробуйте позже или обратитесь к разработчику.",
            reply_markup=get_main_keyboard_v2()
        )
