"""
utils/body_templates.py
Шаблоны для вывода расширенной характеристики тела
"""
import logging
from typing import Dict, Any

from services.body_stats import get_body_composition_analysis, get_weight_change_trend

logger = logging.getLogger(__name__)

def get_body_analysis_text(user, previous_weights: list = None) -> str:
    """
    Формирует развернутый текст анализа композиции тела
    
    Args:
        user: Объект пользователя из базы данных
        previous_weights: Список предыдущих весов для анализа тренда
        
    Returns:
        str: Отформатированный текст с HTML-разметкой
    """
    try:
        # Получаем полный анализ композиции тела
        body_analysis = get_body_composition_analysis(
            weight=user.weight,
            height=user.height,
            age=user.age,
            gender=user.gender,
            neck_cm=user.neck_cm,
            waist_cm=user.waist_cm,
            hip_cm=user.hip_cm,
            wrist_cm=getattr(user, 'wrist_cm', None),
            chest_cm=getattr(user, 'chest_cm', None),
            forearm_cm=getattr(user, 'forearm_cm', None),
            calf_cm=getattr(user, 'calf_cm', None),
            shoulder_width_cm=getattr(user, 'shoulder_width_cm', None),
            hip_width_cm=getattr(user, 'hip_width_cm', None)
        )
        
        # Анализ тренда веса
        weight_trend = get_weight_change_trend(user.weight, previous_weights) if previous_weights else None
        
        # Формируем текст
        text = f"""
🧬 <b>Полный анализ вашего тела</b>

📊 <b>Композиция тела:</b>
• Индекс массы тела (ИМТ): {body_analysis['bmi']} {body_analysis['bmi_color']} — <i>{body_analysis['bmi_status']}</i>
• Идеальный вес: {body_analysis['ideal_weights']['healthy_range']} кг
• Процент жира: {body_analysis['body_fat']}% {'🎯' if body_analysis['has_navy_data'] else '📊'}
• Мышечная масса: {body_analysis['muscle_mass']} кг
💡 <i>ИМТ показывает соотношение веса к росту. Процент жира и мышечная масса помогают оценить состав тела.</i>
• Вода в организме: {body_analysis['body_water']} л ({round((body_analysis['body_water']/user.weight)*100, 1)}% от веса)
💡 <i>Вода составляет основную часть тела. Оптимальный уровень - 60-70% от веса.</i>
"""
        
        # Добавляем новые метрики
        if body_analysis.get('whtr'):
            status = "✅ норма" if body_analysis['whtr'] < 0.5 else "⚠️ выше нормы"
            text += f"• Отношение талии/рост: {body_analysis['whtr']} ({status})\n"
            text += f"  💡 <i>WHTR помогает оценить риски для здоровья. Значение <0.5 считается оптимальным. Ваша целевая талия: < {round(0.5*user.height)} см</i>\n"
        
        if body_analysis.get('metabolic_age'):
            age_diff = body_analysis['metabolic_age'] - user.age
            if age_diff < 0:
                age_comment = f"на {abs(age_diff)} года младше вашего реального возраста – отлично!"
            elif age_diff > 0:
                age_comment = f"на {age_diff} лет старше – стоит обратить внимание на состав тела."
            else:
                age_comment = "совпадает с вашим возрастом."
            text += f"• Метаболический возраст: {body_analysis['metabolic_age']} лет ({age_comment})\n"
            text += f"  💡 <i>Показывает 'возраст' вашего обмена веществ. Если младше реального – отлично, если старше – стоит улучшить физическую активность.</i>\n"
        
        if body_analysis.get('absi') and body_analysis.get('absi_risk'):
            text += f"• Индекс формы тела (ABSI): {body_analysis['absi']:.3f} – {body_analysis['absi_risk']} риск\n"
            text += f"  💡 <i>ABSI помогает оценить распределение жира в организме. Это дополнительный показатель для мониторинга здоровья.</i>\n"
        
        if body_analysis.get('muscle_segments'):
            ms = body_analysis['muscle_segments']
            text += f"• Мышечная масса по сегментам:\n  💪 Руки: {ms['arms']} кг | Ноги: {ms['legs']} кг | Туловище: {ms['trunk']} кг\n  💡 Позволяет оценить равномерность развития. Больше обхваты – больше мышц в этой зоне.\n"
        
        # Добавляем информацию о риске висцерального жира
        if body_analysis['visceral_risk']:
            text += f"• Риск висцерального жира: {body_analysis['visceral_risk']} {body_analysis['visceral_risk_color']}\n"
            text += f"  💡 <i>Висцеральный жир – это жир вокруг внутренних органов. Его уровень важен для оценки общего состояния здоровья.</i>\n"
        
        # Добавляем тип телосложения
        if body_analysis['body_type'] != "Не определен":
            text += f"• Тип телосложения: {body_analysis['body_type']}\n"
            text += f"  💡 <i>Определяется по строению скелета. Влияет на распределение жира и мышц, но не является ограничением для достижения целей.</i>\n"
        
        text += f"""
🔥 <b>Обмен веществ:</b>
• Базовый метаболизм (BMR): ~{int(user.daily_calorie_goal * 0.7)} ккал/день
• Общий расход (TDEE): {user.daily_calorie_goal} ккал/день
• Энергия на переваривание пищи: ~{int(user.daily_calorie_goal * 0.1)} ккал/день
💡 <i>Базовый метаболизм - это энергия, которую тело тратит в состоянии покоя (дыхание, сердцебиение). Общий расход включает все ежедневные активности.</i>

💧 <b>Водный баланс:</b>
• Общая норма жидкости: {user.daily_water_goal} мл/день
• В том числе чистой воды: ~{int(user.daily_water_goal * 0.75)} мл/день
💡 <i>При цели "похудение" норма увеличена на 500 мл (дополнительная вода перед едой). Исследования 2024-2026 показывают: 500 мл перед едой снижают потребление на 111 ккал.</i>
"""
        
        # Добавляем тренд веса
        if weight_trend and weight_trend['period'] > 0:
            text += f"""
📈 <b>Динамика веса:</b>
• Тренд: {weight_trend['trend_emoji']} {weight_trend['trend']}
• Изменение: {weight_trend['change']:+.1f} кг за {weight_trend['period']} взвешиваний
• Средний темп: {weight_trend['rate']:+.2f} кг за неделю
💡 <i>Показывает, как меняется ваш вес со временем. Положительный темп - набор веса, отрицательный - похудение.</i>
"""
        
        # Добавляем рекомендации на основе анализа
        text += f"""
🎯 <b>Персональные рекомендации:</b>
"""
        
        # Рекомендации по ИМТ
        bmi = body_analysis['bmi']
        if bmi < 18.5:
            text += "• 📈 Ваш ИМТ ниже нормы. Рекомендуется профицит калорий +300-500 ккал\n"
        elif bmi >= 25:
            text += "• 📉 Ваш ИМТ выше нормы. Рекомендуется дефицит калорий -300-500 ккал\n"
        else:
            text += "• ✅ Ваш ИМТ в норме. Поддерживайте текущий калораж\n"
        
        # Рекомендации по % жира
        body_fat = body_analysis['body_fat']
        if user.gender == 'male':
            if body_fat > 20:
                text += "• 🏃 Рекомендуется увеличить кардио-нагрузки до 3-5 раз в неделю\n"
            elif body_fat < 8:
                text += "• 💪 Ваш % жира низкий. Фокусируйтесь на силовых тренировках\n"
        else:
            if body_fat > 30:
                text += "• 🏃 Рекомендуется увеличить кардио-нагрузки до 3-5 раз в неделю\n"
            elif body_fat < 15:
                text += "• 💪 Ваш % жира низкий. Фокусируйтесь на силовых тренировках\n"
        
        # Рекомендации по воде
        text += f"• 💧 Пейте воду регулярно: {user.daily_water_goal // 4} мл каждые 4 часа\n"
        
        # Рекомендации по белку
        protein_per_kg = user.daily_protein_goal / user.weight
        text += f"• 🥩 Белок: {protein_per_kg:.1f}г на 1 кг веса ({user.daily_protein_goal}г в день)\n"
        
        # Добавляем мотивационное сообщение
        text += f"""
💪 <b>Ваша цель:</b> {user.goal.replace('_', ' ').title()}
🎯 <b>Прогноз достижения:</b> {'~4-6 месяцев' if user.goal == 'lose_weight' else '~2-3 месяца'} при текущем темпе

📝 <b>Совет дня:</b> {_get_daily_tip(user, body_analysis)}
"""
        
        return text
        
    except Exception as e:
        logger.error(f"Error generating body analysis: {e}")
        return "❌ Не удалось сформировать анализ тела. Попробуйте позже."

def get_body_summary_text(user) -> str:
    """
    Краткая сводка по телу для быстрых уведомлений
    
    Args:
        user: Объект пользователя
        
    Returns:
        str: Краткий текст с основными показателями
    """
    try:
        body_analysis = get_body_composition_analysis(
            weight=user.weight,
            height=user.height,
            age=user.age,
            gender=user.gender,
            neck_cm=user.neck_cm,
            waist_cm=user.waist_cm,
            hip_cm=user.hip_cm
        )
        
        text = f"""
⚖️ <b>Ваша сводка:</b>
• Вес: {user.weight} кг
• ИМТ: {body_analysis['bmi']} {body_analysis['bmi_color']}
• % жира: {body_analysis['body_fat']}%
• Норма калорий: {user.daily_calorie_goal} ккал
"""
        
        return text
        
    except Exception as e:
        logger.error(f"Error generating body summary: {e}")
        return "❌ Не удалось получить сводку"

def get_progress_comparison_text(current_user, previous_user_data: Dict) -> str:
    """
    Сравнение текущих показателей с предыдущими
    
    Args:
        current_user: Текущий объект пользователя
        previous_user_data: Словарь с предыдущими данными
        
    Returns:
        str: Текст сравнения с изменениями
    """
    try:
        text = "📊 <b>Сравнение показателей:</b>\n\n"
        
        # Сравнение веса
        old_weight = previous_user_data.get('weight', current_user.weight)
        weight_change = current_user.weight - old_weight
        if abs(weight_change) >= 0.1:
            emoji = "📈" if weight_change > 0 else "📉"
            text += f"• Вес: {old_weight} → {current_user.weight} кг {emoji} {weight_change:+.1f} кг\n"
        
        # Сравнение ИМТ
        old_height = previous_user_data.get('height', current_user.height)
        old_bmi = old_weight / ((old_height / 100) ** 2)
        current_bmi = current_user.weight / ((current_user.height / 100) ** 2)
        bmi_change = current_bmi - old_bmi
        if abs(bmi_change) >= 0.1:
            text += f"• ИМТ: {old_bmi:.1f} → {current_bmi:.1f} {bmi_change:+.1f}\n"
        
        # Сравнение норм калорий
        old_calories = previous_user_data.get('daily_calorie_goal', current_user.daily_calorie_goal)
        calories_change = current_user.daily_calorie_goal - old_calories
        if calories_change != 0:
            text += f"• Норма калорий: {old_calories} → {current_user.daily_calorie_goal} ккал ({calories_change:+.0f})\n"
        
        return text
        
    except Exception as e:
        logger.error(f"Error generating progress comparison: {e}")
        return "❌ Не удалось сравнить показатели"

def _get_daily_tip(user, body_analysis: Dict) -> str:
    """
    Генерирует ежедневный совет на основе данных пользователя
    
    Args:
        user: Объект пользователя
        body_analysis: Анализ композиции тела
        
    Returns:
        str: Персональный совет
    """
    tips = []
    
    # Советы по ИМТ
    bmi = body_analysis['bmi']
    if bmi < 18.5:
        tips.append("Добавьте калорийные перекусы между основными приемами пищи")
    elif bmi >= 25:
        tips.append("Замените один прием пищи на овощной салат с белком")
    else:
        tips.append("Поддерживайте баланс между белками, жирами и углеводами")
    
    # Советы по % жира
    body_fat = body_analysis['body_fat']
    if body_fat > 25:
        tips.append("Увеличьте потребление клетчатки до 25-30г в день")
    elif body_fat < 12:
        tips.append("Убедитесь, что получаете достаточно здоровых жиров")
    
    # Советы по цели
    if user.goal == 'lose_weight':
        tips.append("Создайте небольшой дефицит калорий через питание, не через голод")
    elif user.goal == 'gain_weight':
        tips.append("Добавьте силовые тренировки 3 раза в неделю")
    else:
        tips.append("Поддерживайте регулярный режим питания и тренировок")
    
    # Советы по воде
    tips.append("Начинайте день со стакана воды для запуска метаболизма")
    
    # Выбираем случайный совет
    import random
    return random.choice(tips)

def get_body_goals_text(user) -> str:
    """
    Текст с целями и прогрессом
    
    Args:
        user: Объект пользователя
        
    Returns:
        str: Текст с целями
    """
    try:
        goal_texts = {
            'lose_weight': 'Похудение',
            'maintain': 'Поддержание веса', 
            'gain_weight': 'Набор массы'
        }
        
        current_goal = goal_texts.get(user.goal, 'Не указана')
        
        text = f"""
🎯 <b>Ваши цели:</b>
• Основная цель: {current_goal}
• Целевой вес: {user.weight} кг (текущий)
• Дневная норма калорий: {user.daily_calorie_goal} ккал
• Белки: {user.daily_protein_goal}г | Жиры: {user.daily_fat_goal}г | Углеводы: {user.daily_carbs_goal}г
• Вода: {user.daily_water_goal} мл

📈 <b>Рекомендуемый темп изменений:</b>
• Безопасный темп похудения: 0.5-1 кг в неделю
• Безопасный темп набора: 0.25-0.5 кг в неделю
• Для поддержания: стабильность ±0.5 кг
"""
        
        return text
        
    except Exception as e:
        logger.error(f"Error generating body goals: {e}")
        return "❌ Не удалось получить цели"
