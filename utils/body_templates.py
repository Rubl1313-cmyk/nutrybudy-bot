"""
utils/body_templates.py
Шаблоны для вывода расширенной характеристики тела
"""
import logging
from typing import Dict, Any

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
            neck_cm=getattr(user, 'neck_cm', None),
            waist_cm=getattr(user, 'waist_cm', None),
            hip_width_cm=getattr(user, 'hip_width_cm', None)
        )
        
        # Анализ тренда веса
        weight_trend = get_weight_change_trend(user.weight, previous_weights) if previous_weights else None
        
        # Формируем текст
        text = f"""
[BODY] <b>Полный анализ вашего тела</b>

[COMPOSITION] <b>Композиция тела:</b>
• Индекс массы тела (ИМТ): {body_analysis['bmi']} {body_analysis['bmi_color']} — <i>{body_analysis['bmi_status']}</i>
• Идеальный вес: {body_analysis['ideal_weights']['healthy_range']} кг
• Процент жира: {body_analysis['body_fat']}% {'[DATA]' if body_analysis['has_navy_data'] else '[ESTIMATED]'}
• Мышечная масса: {body_analysis['muscle_mass']} кг
[INFO] <i>ИМТ показывает соотношение веса к росту. Процент жира и мышечная масса помогают оценить состав тела.</i>
• Вода в организме: {body_analysis['body_water']} л ({round((body_analysis['body_water']/user.weight)*100, 1)}% от веса)
[INFO] <i>Вода составляет основную часть тела. Оптимальный уровень - 60-70% от веса.</i>
"""
        
        # Добавляем новые метрики
        if body_analysis.get('whtr'):
            status = "[OK] норма" if body_analysis['whtr'] < 0.5 else "[WARNING] выше нормы"
            text += f"• Отношение талии/рост: {body_analysis['whtr']} ({status})\n"
            text += f"  [INFO] <i>WHTR помогает оценить риски для здоровья. Значение <0.5 считается оптимальным. Ваша целевая талия: < {round(0.5*user.height)} см</i>\n"
        
        if body_analysis.get('metabolic_age'):
            age_diff = body_analysis['metabolic_age'] - user.age
            if age_diff < 0:
                age_comment = f"на {abs(age_diff)} года младше вашего реального возраста – отлично!"
            elif age_diff > 0:
                age_comment = f"на {age_diff} лет старше – стоит обратить внимание на состав тела."
            else:
                age_comment = "совпадает с вашим возрастом."
            text += f"• Метаболический возраст: {body_analysis['metabolic_age']} лет ({age_comment})\n"
        
        if body_analysis.get('absi') and body_analysis.get('absi_risk'):
            text += f"• Индекс формы тела (ABSI): {body_analysis['absi']:.3f} – {body_analysis['absi_risk']} риск\n"
            text += f"  [INFO] <i>ABSI помогает оценить распределение жира в организме. Это дополнительный показатель для мониторинга здоровья.</i>\n"
        
        if body_analysis.get('muscle_segments'):
            ms = body_analysis['muscle_segments']
            text += f"\n[MUSCLES] <b>Анализ мышечной массы:</b>\n"
            text += f"• Руки: {ms['arms']} кг ({ms['arms_percent']:.1f}% от общей массы)\n"
            text += f"• Ноги: {ms['legs']} кг ({ms['legs_percent']:.1f}%)\n"
            text += f"• Туловище: {ms['torso']} кг ({ms['torso_percent']:.1f}%)\n"
            text += f"[INFO] <i>Сбалансированное развитие всех групп мышц важно для здоровья и силовых показателей.</i>\n"
        
        # Добавляем информацию о риске висцерального жира
        if body_analysis['visceral_risk']:
            text += f"• Риск висцерального жира: {body_analysis['visceral_risk']} {body_analysis['visceral_risk_color']}\n"
            text += f"  [INFO] <i>Висцеральный жир – это жир вокруг внутренних органов. Его избыток повышает риск многих заболеваний.</i>\n"
        
        # Добавляем рекомендации
        text += f"\n[RECOMMENDATIONS] <b>Персональные рекомендации:</b>\n"
        recommendations = get_body_recommendations(body_analysis, user)
        for rec in recommendations:
            text += f"• {rec}\n"
        
        # Добавляем тренд веса
        if weight_trend:
            text += f"\n[TREND] <b>Анализ тренда веса:</b>\n"
            text += f"• {weight_trend['description']}\n"
            text += f"• Изменение за период: {weight_trend['change']:+.1f} кг\n"
            text += f"• Среднее изменение в неделю: {weight_trend['weekly_change']:+.2f} кг\n"
            text += f"[INFO] <i>{weight_trend['recommendation']}</i>\n"
        
        # Добавляем цели
        text += f"\n[GOALS] <b>Рекомендуемые цели:</b>\n"
        goals = get_body_goals(body_analysis, user)
        for goal in goals:
            text += f"• {goal}\n"
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error generating body analysis text: {e}")
        return "[ERROR] Не удалось сформировать анализ тела. Попробуйте позже."

def get_body_composition_analysis(weight: float, height: float, age: int, gender: str,
                                neck_cm: float = None, waist_cm: float = None, 
                                hip_width_cm: float = None) -> Dict[str, Any]:
    """
    Выполняет полный анализ композиции тела
    
    Args:
        weight: Вес в кг
        height: Рост в см
        age: Возраст
        gender: Пол (male/female)
        neck_cm: Обхват шеи в см
        waist_cm: Обхват талии в см
        hip_width_cm: Ширина бедер в см
        
    Returns:
        dict: Анализ композиции тела
    """
    try:
        # Базовые расчеты
        bmi = calculate_bmi(weight, height)
        bmi_status, bmi_color = get_bmi_classification(bmi)
        
        # Расчет идеального веса
        ideal_weights = calculate_ideal_weight(height, gender, age)
        
        # Расчет процента жира
        body_fat_data = calculate_body_fat_percentage(weight, height, age, gender, neck_cm, waist_cm, hip_width_cm)
        
        # Расчет мышечной массы
        muscle_mass = calculate_muscle_mass(weight, body_fat_data['percentage'])
        
        # Расчет воды в организме
        body_water = calculate_body_water(weight, age, gender)
        
        # Расчет WHTR (Waist-to-Height Ratio)
        whtr = None
        if waist_cm:
            whtr = waist_cm / height
        
        # Расчет метаболического возраста
        metabolic_age = calculate_metabolic_age(bmi, body_fat_data['percentage'], age)
        
        # Расчет ABSI (A Body Shape Index)
        absi_value = calculate_absi(weight, height, waist_cm, age, gender)
        absi_risk, absi_percentile = get_absi_risk(absi_value, age, gender)
        
        # Расчет сегментов мышечной массы
        muscle_segments = calculate_muscle_segments(muscle_mass, gender)
        
        # Оценка риска висцерального жира
        visceral_risk, visceral_color = assess_visceral_fat_risk(waist_cm, gender, body_fat_data['percentage'])
        
        return {
            'bmi': round(bmi, 1),
            'bmi_status': bmi_status,
            'bmi_color': bmi_color,
            'ideal_weights': ideal_weights,
            'body_fat': round(body_fat_data['percentage'], 1),
            'has_navy_data': body_fat_data['method'] == 'navy',
            'muscle_mass': round(muscle_mass, 1),
            'body_water': round(body_water, 1),
            'whtr': round(whtr, 2) if whtr else None,
            'metabolic_age': metabolic_age,
            'absi': round(absi_value, 3) if absi_value else None,
            'absi_risk': absi_risk,
            'absi_percentile': absi_percentile,
            'muscle_segments': muscle_segments,
            'visceral_risk': visceral_risk,
            'visceral_risk_color': visceral_color
        }
        
    except Exception as e:
        logger.error(f"Error in body composition analysis: {e}")
        return {}

def calculate_bmi(weight: float, height: float) -> float:
    """Рассчитывает ИМТ"""
    height_m = height / 100
    return weight / (height_m ** 2)

def get_bmi_classification(bmi: float) -> tuple:
    """Возвращает классификацию ИМТ и цвет"""
    if bmi < 16.5:
        return "Выраженный дефицит массы", "🔴"
    elif bmi < 18.5:
        return "Недостаточная масса", "🟡"
    elif bmi < 25:
        return "Нормальная масса", "🟢"
    elif bmi < 30:
        return "Избыточная масса", "🟡"
    elif bmi < 35:
        return "Ожирение I степени", "🟠"
    elif bmi < 40:
        return "Ожирение II степени", "🔴"
    else:
        return "Ожирение III степени", "🔴"

def calculate_ideal_weight(height: float, gender: str, age: int) -> Dict[str, str]:
    """Рассчитывает идеальный вес разными методами"""
    # Формула Девина
    if gender.lower() == 'male':
        devine = 50 + 2.3 * ((height / 2.54) - 60)
    else:
        devine = 45.5 + 2.3 * ((height / 2.54) - 60)
    
    # Формула Хамви
    if gender.lower() == 'male':
        hamwi = 48 + 2.7 * ((height / 2.54) - 60)
    else:
        hamwi = 45.5 + 2.2 * ((height / 2.54) - 60)
    
    # Формула Брока
    brock = height - 100
    
    # Здоровый диапазон (ИМТ 18.5-24.9)
    height_m = height / 100
    min_healthy = 18.5 * (height_m ** 2)
    max_healthy = 24.9 * (height_m ** 2)
    
    return {
        'devine': f"{round(devine, 1)}",
        'hamwi': f"{round(hamwi, 1)}",
        'brock': f"{round(brock, 1)}",
        'healthy_range': f"{round(min_healthy, 1)}-{round(max_healthy, 1)}"
    }

def calculate_body_fat_percentage(weight: float, height: float, age: int, gender: str,
                                neck_cm: float = None, waist_cm: float = None, 
                                hip_width_cm: float = None) -> Dict[str, Any]:
    """
    Рассчитывает процент жира в организме
    
    Returns:
        dict: {'percentage': float, 'method': str}
    """
    # Если есть обмеры по методу ВМФ США
    if neck_cm and waist_cm and hip_width_cm:
        try:
            if gender.lower() == 'male':
                body_fat = 86.010 * math.log10(waist_cm - neck_cm) + 70.64 * math.log10(height) - 36.76
            else:
                body_fat = 163.205 * math.log10(waist_cm + hip_width_cm - neck_cm) - 97.684 * math.log10(height) - 78.387
            
            return {'percentage': body_fat, 'method': 'navy'}
        except:
            pass
    
    # Запасная формула (упрощенная)
    if gender.lower() == 'male':
        body_fat = (1.20 * calculate_bmi(weight, height)) + (0.23 * age) - 16.2
    else:
        body_fat = (1.20 * calculate_bmi(weight, height)) + (0.23 * age) - 5.4
    
    return {'percentage': max(body_fat, 5), 'method': 'formula'}

def calculate_muscle_mass(weight: float, body_fat_percentage: float) -> float:
    """Рассчитывает мышечную массу"""
    # Упрощенная формула: мышечная масса = вес * (1 - процент жира) * 0.7
    # Коэффициент 0.7 учитывает, что безжировая масса включает не только мышцы
    return weight * (1 - body_fat_percentage / 100) * 0.7

def calculate_body_water(weight: float, age: int, gender: str) -> float:
    """Рассчитывает количество воды в организме"""
    # Средний процент воды в организме
    if gender.lower() == 'male':
        water_percentage = 0.60
    else:
        water_percentage = 0.55
    
    # Корректировка с возрастом
    if age > 60:
        water_percentage -= 0.05
    elif age > 40:
        water_percentage -= 0.02
    
    return weight * water_percentage

def calculate_metabolic_age(bmi: float, body_fat_percentage: float, chronological_age: int) -> int:
    """Рассчитывает метаболический возраст"""
    # Упрощенная формула
    if bmi < 25 and body_fat_percentage < 20:
        return max(chronological_age - 5, 18)
    elif bmi < 30 and body_fat_percentage < 30:
        return chronological_age
    else:
        return min(chronological_age + 5, chronological_age + 10)

def calculate_absi(weight: float, height: float, waist_cm: float, age: int, gender: str) -> float:
    """Рассчитывает индекс формы тела (ABSI)"""
    if not waist_cm:
        return None
    
    try:
        height_m = height / 100
        bmi = calculate_bmi(weight, height)
        
        # Упрощенная формула ABSI
        absi = waist_cm / (height_m ** (2/3) * (weight ** (1/6)))
        
        return absi
    except:
        return None

def get_absi_risk(absi_value: float, age: int, gender: str) -> tuple:
    """Оценивает риск по ABSI"""
    if not absi_value:
        return "Невозможно оценить", 0
    
    # Упрощенные пороговые значения
    if absi_value < 0.08:
        return "Низкий", 20
    elif absi_value < 0.09:
        return "Средний", 50
    else:
        return "Высокий", 80

def calculate_muscle_segments(muscle_mass: float, gender: str) -> Dict[str, float]:
    """Распределяет мышечную массу по сегментам"""
    # Примерное распределение мышечной массы
    if gender.lower() == 'male':
        segments = {
            'arms': 0.15,   # 15%
            'legs': 0.35,   # 35%
            'torso': 0.50   # 50%
        }
    else:
        segments = {
            'arms': 0.12,   # 12%
            'legs': 0.33,   # 33%
            'torso': 0.55   # 55%
        }
    
    result = {}
    for segment, percentage in segments.items():
        mass = muscle_mass * percentage
        result[segment] = round(mass, 1)
        result[f"{segment}_percent"] = round(percentage * 100, 1)
    
    return result

def assess_visceral_fat_risk(waist_cm: float, gender: str, body_fat_percentage: float) -> tuple:
    """Оценивает риск висцерального жира"""
    if not waist_cm:
        return "Невозможно оценить", "⚪"
    
    # Пороговые значения для обхвата талии
    if gender.lower() == 'male':
        threshold = 94  # см
    else:
        threshold = 80  # см
    
    if waist_cm < threshold:
        return "Низкий", "🟢"
    elif waist_cm < threshold + 10:
        return "Средний", "🟡"
    else:
        return "Высокий", "🔴"

def get_weight_change_trend(current_weight: float, previous_weights: list) -> Dict[str, Any]:
    """Анализирует тренд веса"""
    if not previous_weights or len(previous_weights) < 2:
        return None
    
    try:
        # Рассчитываем изменение
        first_weight = previous_weights[0]
        last_weight = previous_weights[-1]
        total_change = current_weight - first_weight
        
        # Среднее изменение в неделю
        weeks = len(previous_weights)
        weekly_change = total_change / weeks if weeks > 0 else 0
        
        # Определяем тренд
        if abs(total_change) < 0.5:
            trend = "Стабильный вес"
            recommendation = "Ваш вес стабилен. Продолжайте придерживаться текущего режима."
        elif total_change > 0:
            if weekly_change > 0.5:
                trend = "Быстрый набор веса"
                recommendation = "Вес увеличивается слишком быстро. Стоит обратить внимание на питание и активность."
            else:
                trend = "Умеренный набор веса"
                recommendation = "Вес постепенно увеличивается. Контролируйте калории и активность."
        else:
            if abs(weekly_change) > 0.5:
                trend = "Быстрая потеря веса"
                recommendation = "Вес снижается слишком быстро. Убедитесь, что это безопасно для здоровья."
            else:
                trend = "Умеренная потеря веса"
                recommendation = "Хороший темп похудения. Продолжайте в том же духе."
        
        return {
            'trend': trend,
            'description': trend,
            'change': total_change,
            'weekly_change': weekly_change,
            'recommendation': recommendation
        }
        
    except Exception as e:
        logger.error(f"Error analyzing weight trend: {e}")
        return None

def get_body_recommendations(analysis: Dict, user) -> list:
    """Генерирует персональные рекомендации"""
    recommendations = []
    
    # Рекомендации по ИМТ
    bmi = analysis.get('bmi', 0)
    if bmi < 18.5:
        recommendations.append("Увеличьте калорийность питания для достижения здорового веса")
    elif bmi > 25:
        recommendations.append("Создайте умеренный дефицит калорий для нормализации веса")
    
    # Рекомендации по проценту жира
    body_fat = analysis.get('body_fat', 0)
    if body_fat > 25 and user.gender == 'male':
        recommendations.append("Добавьте силовые тренировки для снижения процента жира")
    elif body_fat > 32 and user.gender == 'female':
        recommendations.append("Сочетайте кардио и силовые тренировки для улучшения композиции тела")
    
    # Рекомендации по мышечной массе
    muscle_mass = analysis.get('muscle_mass', 0)
    if muscle_mass < user.weight * 0.4:  # Мышцы составляют менее 40% от веса
        recommendations.append("Увеличьте потребление белка и добавьте силовые тренировки")
    
    # Рекомендации по WHTR
    whtr = analysis.get('whtr')
    if whtr and whtr > 0.5:
        recommendations.append("Сократите потребление простых углеводов и увеличьте активность")
    
    # Общие рекомендации
    recommendations.append("Пейте достаточно воды (30-40 мл на кг веса)")
    recommendations.append("Спите 7-9 часов в сутки для восстановления")
    recommendations.append("Регулярно измеряйте прогресс и корректируйте план")
    
    return recommendations[:5]  # Ограничиваем 5 рекомендациями

def get_body_goals(analysis: Dict, user) -> list:
    """Генерирует цели на основе анализа"""
    goals = []
    
    # Цель по весу
    ideal_range = analysis.get('ideal_weights', {}).get('healthy_range', '0-0')
    goals.append(f"Достичь веса в диапазоне {ideal_range} кг")
    
    # Цель по проценту жира
    body_fat = analysis.get('body_fat', 0)
    if user.gender == 'male':
        target_fat = max(10, body_fat - 5)
    else:
        target_fat = max(20, body_fat - 5)
    goals.append(f"Снизить процент жира до {target_fat}%")
    
    # Цель по мышечной массе
    current_muscle = analysis.get('muscle_mass', 0)
    target_muscle = current_muscle * 1.1  # Увеличить на 10%
    goals.append(f"Увеличить мышечную массу до {round(target_muscle, 1)} кг")
    
    # Цель по талии
    whtr = analysis.get('whtr')
    if whtr and whtr > 0.5:
        target_waist = round(0.5 * user.height)
        goals.append(f"Сократить талию до {target_waist} см")
    
    return goals[:4]  # Ограничиваем 4 целями
