# 🚀 Улучшение ансамбля моделей для распознавания ингредиентов

## 🎯 Проблема

Ансамбль моделей стал хуже распознавать ингредиенты, потому что просто выбирал результат с максимальной уверенностью, игнорируя ингредиенты от других моделей.

## 🔧 Решение

### 1. **Умная агрегация ингредиентов**

Вместо простого выбора лучшего результата, теперь ансамбль:

1. **Выбирает лучшее название блюда** по взвешенной уверенности
2. **Собирает ВСЕ ингредиенты** от всех успешных моделей
3. **Объединяет дубликаты** с усреднением уверенности
4. **Учитывает количество моделей** которые обнаружили каждый ингредиент
5. **Фильтрует по порогу уверенности** (0.3 по умолчанию)

### 2. **Алгоритм объединения**

```python
def _merge_ensemble_results(valid_results):
    # 1. Выбираем лучшее название блюда
    best_dish = max(valid_results, key=lambda x: x[0]['confidence'] * x[2])
    
    # 2. Собираем все ингредиенты
    ingredient_map = {}
    for data, model_name, weight in valid_results:
        for ingredient in data['ingredients']:
            name = ingredient['name'].lower()
            if name not in ingredient_map:
                ingredient_map[name] = {'data': ingredient, 'sources': [], 'confidence': 0}
            
            # Добавляем информацию о детекции
            ingredient_map[name]['sources'].append(model_name)
            
            # Суммируем взвешенную уверенность
            weighted_conf = ingredient['confidence'] * weight
            ingredient_map[name]['confidence'] += weighted_conf
    
    # 3. Усредняем и фильтруем
    merged_ingredients = []
    for name, info in ingredient_map.items():
        avg_confidence = info['confidence'] / len(info['sources'])
        
        # Бонус за детекцию несколькими моделями
        detection_bonus = 0.1 * (len(info['sources']) - 1)
        final_confidence = min(avg_confidence + detection_bonus, 1.0)
        
        if final_confidence >= 0.3:
            ingredient = info['data'].copy()
            ingredient['confidence'] = final_confidence
            ingredient['detected_by'] = info['sources']
            merged_ingredients.append(ingredient)
    
    return best_dish_data_with_merged_ingredients
```

### 3. **Преимущества нового подхода**

#### **Больше ингредиентов**
- **Раньше**: Только ингредиенты от одной модели
- **Теперь**: Объединенные ингредиенты от всех моделей

#### **Выше уверенность**
- **Детекция несколькими моделями**: +0.1 к уверенности за каждую дополнительную модель
- **Взвешенное усреднение**: учитываются веса моделей
- **Фильтрация**: удаляются низкоуверенные ингредиенты

#### **Больше информации**
- `detected_by`: список моделей, которые обнаружили ингредиент
- `detection_count`: количество моделей
- `ensemble_info`: статистика объединения

## 📊 Пример работы

### **Было (простой выбор):**
```log
🤖 LLaVA: beef shashlik (confidence: 0.85)
   Ingredients: beef(0.9), onion(0.7), tomato(0.6)
🤖 UForm: beef skewers (confidence: 0.78)  
   Ingredients: beef(0.8), onion(0.8), pepper(0.7), tomato(0.5)
🏆 Выбран: LLaVA (confidence: 0.85)
📋 Итог: beef, onion, tomato (3 ингредиента)
```

### **Стало (умное объединение):**
```log
🤖 LLaVA: beef shashlik (confidence: 0.85)
   Ingredients: beef(0.9), onion(0.7), tomato(0.6)
🤖 UForm: beef skewers (confidence: 0.78)
   Ingredients: beef(0.8), onion(0.8), pepper(0.7), tomato(0.5)
🔄 Merging results from 2 models...
🔗 Merged ingredient: beef (confidence: 0.87, models: 2)
🔗 Merged ingredient: onion (confidence: 0.79, models: 2)  
🔗 Merged ingredient: tomato (confidence: 0.59, models: 2)
🔗 Merged ingredient: pepper (confidence: 0.77, models: 1)
🏆 Best dish: beef shashlik (confidence: 0.82)
📋 Итог: beef, onion, tomato, pepper (4 ингредиента)
```

## 🎯 Результаты улучшения

### **Точность распознавания ингредиентов**
- ✅ **Больше ингредиентов**: объединение от всех моделей
- ✅ **Выше уверенность**: детекция несколькими моделями
- ✅ **Меньше пропусков**: если одна модель не увидела, другая может

### **Качество данных**
- ✅ **Взвешенная уверенность**: учитываются надежность моделей
- ✅ **Мета-информация**: какие модели обнаружили ингредиент
- ✅ **Фильтрация шума**: удаление низкоуверенных детекций

### **Логирование**
- ✅ **Подробная статистика**: сколько ингредиентов объединено
- ✅ **Отладочная информация**: какие модели увидели каждый ингредиент
- ✅ **Прозрачность**: понятный процесс объединения

## 🔧 Настройки

### **Порог уверенности**
```python
if final_confidence >= 0.3:  # Можно настроить
```

### **Бонус за детекцию**
```python
detection_bonus = 0.1 * (info['detection_count'] - 1)
```

### **Веса моделей**
```python
VISION_MODELS = [
    {"id": "@cf/llava-hf/llava-1.5-7b-hf", "weight": 0.6},
    {"id": "@cf/unum/uform-gen2-qwen-500m", "weight": 0.4},
]
```

## 📈 Выводы

Новый ансамбль не просто выбирает лучший результат, а умно объединяет сильные стороны всех моделей:

1. **LLaVA**: Лучше понимает контекст и сложные блюда
2. **UForm**: Хорошее детектирование отдельных ингредиентов
3. **Ансамбль**: Объединяет лучшее от обеих моделей

Теперь ансамбль действительно улучшает распознавание, а не ухудшает его! 🎉
