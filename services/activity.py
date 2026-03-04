"""
Словарь для расчёта калорий на минуту активности.
Ключи соответствуют значениям activity_type из модели Activity.
Значения MET (метаболический эквивалент) основаны на Compendium of Physical Activities [citation:2][citation:4].
Для расчёта калорий используется формула: MET × вес(кг) × время(мин) / 60
"""

CALORIES_PER_MINUTE = {
    # ========== ХОДЬБА ==========
    "walking_slow": 2.0,        # медленная ходьба (< 3 км/ч) [citation:2]
    "walking": 3.5,              # ходьба (5 км/ч, средний темп) [citation:1]
    "walking_brisk": 4.5,        # быстрая ходьба (6-7 км/ч) [citation:2]
    "walking_uphill": 5.4,       # ходьба в гору [citation:4]
    "walking_downhill": 3.0,     # ходьба под гору
    "nordic_walking": 5.0,       # скандинавская ходьба
    "stair_walking": 8.0,        # ходьба по лестнице [citation:10]
    
    # ========== БЕГ ==========
    "jogging": 6.5,              # бег трусцой (8 км/ч) [citation:4]
    "running_9kmh": 8.0,         # бег 9 км/ч [citation:2]
    "running_10kmh": 10.0,       # бег 10 км/ч [citation:2]
    "running_12kmh": 11.5,       # бег 12 км/ч [citation:2]
    "running_14kmh": 14.0,       # бег 14 км/ч
    "running_16kmh": 16.0,       # бег 16 км/ч [citation:2]
    "running_cross": 9.0,        # бег по пересечённой местности [citation:10]
    "running_stairs_up": 15.0,   # бег вверх по лестнице [citation:10]
    "running_stairs": 12.0,      # бег по лестнице вверх-вниз
    
    # ========== ВЕЛОСИПЕД ==========
    "cycling_leisure": 4.0,      # велосипед, прогулочный (<10 км/ч) [citation:2]
    "cycling_light": 6.0,        # велосипед, лёгкая нагрузка (10-12 км/ч)
    "cycling_moderate": 8.0,     # велосипед, умеренная нагрузка (12-14 км/ч) [citation:2]
    "cycling_vigorous": 10.0,    # велосипед, интенсивная (14-16 км/ч) [citation:2]
    "cycling_racing": 12.0,      # велосипед, гонка (20+ км/ч) [citation:2]
    "cycling_mountain": 8.5,     # горный велосипед
    "stationary_bike": 7.0,      # велотренажёр
    
    # ========== ПЛАВАНИЕ ==========
    "swimming_slow": 5.0,        # плавание медленное (0.4 км/ч) [citation:4]
    "swimming_moderate": 7.0,    # плавание, умеренный темп [citation:2]
    "swimming_fast": 10.0,       # плавание быстрое (кроль) [citation:10]
    "swimming_breaststroke": 7.5,# брасс
    "swimming_backstroke": 7.0,  # на спине
    "swimming_butterfly": 11.0,  # баттерфляй
    "water_aerobics": 5.0,       # аквааэробика [citation:4]
    "water_polo": 10.0,          # водное поло [citation:10]
    
    # ========== ЗИМНИЕ ВИДЫ ==========
    "skiing_cross_country": 9.0,     # беговые лыжи [citation:1]
    "skiing_downhill": 5.5,          # горные лыжи [citation:1]
    "snowboarding": 5.5,             # сноуборд [citation:4]
    "skating": 7.0,                  # катание на коньках [citation:4]
    "skating_speed": 12.0,           # скоростной бег на коньках [citation:10]
    "ice_skating_figure": 5.0,       # фигурное катание [citation:10]
    "sledding": 4.0,                 # катание на санках
    "ski_mountaineering": 8.0,       # ски-альпинизм
    
    # ========== СПОРТИВНЫЕ ИГРЫ ==========
    "football": 8.0,             # футбол [citation:2]
    "basketball": 7.0,           # баскетбол [citation:2]
    "volleyball": 4.0,           # волейбол [citation:4]
    "tennis_singles": 7.5,       # теннис одиночный [citation:1]
    "tennis_doubles": 5.0,       # теннис парный
    "table_tennis": 4.5,         # настольный теннис [citation:4]
    "badminton": 5.5,            # бадминтон [citation:4]
    "squash": 12.0,              # сквош [citation:4]
    "handball": 8.0,             # гандбол [citation:4]
    "hockey": 8.0,               # хоккей [citation:4]
    "golf_carry": 5.0,           # гольф с переноской клюшек [citation:1]
    "golf_cart": 3.5,            # гольф с тележкой [citation:1]
    "baseball": 5.0,             # бейсбол
    "softball": 5.0,             # софтбол [citation:1]
    "rugby": 8.5,                # регби
    "cricket": 5.0,              # крикет [citation:4]
    
    # ========== ЕДИНОБОРСТВА ==========
    "boxing_sparring": 8.0,      # бокс (спарринг) [citation:2]
    "boxing_heavy": 12.0,        # бокс (интенсивный) [citation:10]
    "taekwondo": 8.0,            # таэквон-до [citation:1]
    "karate": 8.0,               # карате
    "judo": 7.0,                 # дзюдо [citation:4]
    "wrestling": 8.0,            # борьба
    "muay_thai": 10.0,           # муай-тай
    "kickboxing": 9.0,           # кикбоксинг
    
    # ========== ТРЕНАЖЁРНЫЙ ЗАЛ ==========
    "weightlifting_light": 4.0,  # тренировка с отягощениями, лёгкая [citation:4]
    "weightlifting_moderate": 5.0,# тренировка с отягощениями, средняя
    "weightlifting_heavy": 6.0,   # тренировка с отягощениями, интенсивная [citation:2]
    "circuit_training": 8.0,      # круговая тренировка [citation:2]
    "calisthenics_light": 4.0,    # воркаут/калистеника, лёгкая
    "calisthenics_vigorous": 8.0, # воркаут/калистеника, интенсивная [citation:2]
    "pullups_pushups": 5.0,       # подтягивания/отжимания
    "elliptical": 6.0,            # эллиптический тренажёр [citation:4]
    "rowing_machine": 7.0,        # гребной тренажёр [citation:4]
    "stair_climber": 9.0,         # степпер [citation:4]
    
    # ========== ЙОГА И РАСТЯЖКА ==========
    "yoga_gentle": 2.5,           # йога, мягкая/растяжка [citation:2]
    "yoga_hatha": 3.0,            # хатха-йога
    "yoga_power": 4.0,            # силовая йога
    "yoga_ashtanga": 6.0,         # аштанга-йога [citation:4]
    "pilates": 3.5,               # пилатес [citation:10]
    "stretching": 2.5,            # растяжка [citation:4]
    "bodyflex": 5.0,              # бодифлекс
    
    # ========== ТАНЦЫ ==========
    "dance_ballroom": 5.0,        # бальные танцы [citation:4]
    "dance_disco": 6.5,           # диско [citation:4]
    "dance_swing": 5.5,           # свинг [citation:1]
    "dance_modern": 6.0,          # современные танцы [citation:10]
    "dance_ballet": 8.0,          # балет [citation:10]
    "dance_aerobic_low": 5.0,     # аэробные танцы низкой интенсивности
    "dance_aerobic_high": 8.0,    # аэробные танцы высокой интенсивности [citation:10]
    "zumba": 7.0,                 # зумба
    
    # ========== ДОМАШНИЕ ДЕЛА ==========
    "housework_light": 3.0,       # лёгкая работа по дому (пыль, уборка) [citation:2]
    "housework_moderate": 4.0,    # уборка, мытьё полов [citation:4]
    "gardening": 4.5,             # работа в саду [citation:4]
    "mowing_lawn": 5.0,           # стрижка газона [citation:4]
    "shoveling_snow": 6.0,        # уборка снега
    "chopping_wood": 6.0,         # колка дров [citation:10]
    "moving_furniture": 6.5,      # перестановка мебели
    
    # ========== АКТИВНЫЙ ОТДЫХ ==========
    "hiking": 6.0,                # пеший туризм [citation:1]
    "climbing_rock": 8.0,         # скалолазание
    "climbing_mountain": 8.0,     # альпинизм [citation:10]
    "fishing": 3.5,               # рыбалка
    "horseback_riding_walk": 3.0, # верховая езда шагом
    "horseback_riding_trot": 5.5, # верховая езда рысью [citation:4]
    "horseback_riding_gallop": 7.0,# верховая езда галопом
    "kayaking": 5.0,              # каякинг [citation:10]
    "canoeing": 4.0,              # каноэ [citation:10]
    "surfing": 5.0,               # сёрфинг
    "windsurfing": 5.0,           # виндсёрфинг
    "skateboarding": 5.0,         # скейтбординг
    "rollerblading": 7.0,         # роликовые коньки [citation:1]
    "trampoline": 4.5,            # батут
    
    # ========== БЫТОВЫЕ АКТИВНОСТИ ==========
    "sitting": 1.0,               # сидя (покой) [citation:4]
    "standing": 1.5,              # стоя [citation:4]
    "eating": 1.5,                # приём пищи [citation:10]
    "dressing": 2.0,              # одевание [citation:10]
    "driving": 2.0,               # вождение [citation:10]
    "shopping": 2.5,              # ходьба по магазинам [citation:10]
    "cooking": 2.5,               # приготовление еды [citation:10]
    "ironing": 2.0,               # глажка [citation:10]
    "sleeping": 0.9,              # сон [citation:10]
    
    # ========== ИНТИМ ==========
    "sex_passive": 1.5,           # секс (пассивный партнёр) [citation:10]
    "sex_active": 3.0,            # секс (активный партнёр) [citation:10]
    
    # ========== ДРУГОЕ (УСРЕДНЁННОЕ) ==========
    "other": 5.0
}
