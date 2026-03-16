# handlers/food_clarification.py
import logging
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.food_api import get_product_variants
from services.ai_processor import ai_processor
from utils.safe_parser import safe_parse_float

logger = logging.getLogger(__name__)
router = Router()

class FoodClarificationStates(StatesGroup):
    waiting_for_product_choice = State()   # ожидание выбора варианта продукта
    waiting_for_weight = State()           # ожидание ввода веса
    waiting_for_manual_name = State()      # ручной ввод названия

# Хранилище временных данных: {user_id: {"original_items": [...], "current_index": int, "clarified_items": [...]}}
_temp_storage = {}

@router.message(F.text, flags={"rate_limit": "food"})
async def handle_food_text(message: Message, state: FSMContext):
    """Начало обработки текста как еды (вызывается из ai_handler, если AI вернул food_items)."""
    user_id = message.from_user.id
    text = message.text

    # 1. Получаем от AI список продуктов (как раньше)
    result = await ai_processor.process_text_input(text, user_id)
    if not result.get("success") or result["intent"] != "log_food":
        # Если не еда, пробрасываем дальше (может быть другой intent)
        return False

    parameters = result["parameters"]
    food_items = parameters.get("food_items", [])

    if not food_items:
        await message.answer("🤔 Не удалось распознать продукты. Попробуйте описать подробнее.")
        return True

    # 2. Инициализируем временное хранилище
    _temp_storage[user_id] = {
        "original_items": food_items,
        "current_index": 0,
        "clarified_items": []
    }

    # 3. Начинаем уточнение первого продукта
    await clarify_next_product(message, user_id, state)
    return True

async def clarify_next_product(message: Message, user_id: int, state: FSMContext):
    """Уточняет следующий продукт в списке."""
    storage = _temp_storage.get(user_id)
    if not storage:
        return

    idx = storage["current_index"]
    if idx >= len(storage["original_items"]):
        # Все продукты уточнены – сохраняем итог
        await finish_clarification(message, user_id, state)
        return

    product = storage["original_items"][idx]
    product_name = product.get("name", "")

    # Ищем варианты в локальной базе
    variants = get_product_variants(product_name)  # функция из food_api.py

    if variants and len(variants) > 1:
        # Показываем варианты
        builder = InlineKeyboardBuilder()
        for i, var in enumerate(variants[:5]):  # максимум 5 вариантов
            cal = var.get("calories", 0)
            protein = var.get("protein", 0)
            fat = var.get("fat", 0)
            carbs = var.get("carbs", 0)
            text_button = f"{var['name']} – {cal:.0f} ккал (Б:{protein:.1f} Ж:{fat:.1f} У:{carbs:.1f})"
            builder.button(text=text_button, callback_data=f"clr_var_{idx}_{i}")
        builder.button(text="✍️ Ввести вручную", callback_data=f"clr_manual_{idx}")
        builder.button(text="❌ Пропустить", callback_data=f"clr_skip_{idx}")
        builder.adjust(1)

        await message.answer(
            f"🍽️ Уточните, что вы имели в виду под «{product_name}»?",
            reply_markup=builder.as_markup()
        )
        await state.set_state(FoodClarificationStates.waiting_for_product_choice)
    else:
        # Если вариант один или нет вариантов – используем AI-оценку и сразу запрашиваем вес
        # Можно взять первый вариант или данные от AI
        if variants:
            chosen = variants[0]
        else:
            # Используем исходные данные от AI
            chosen = {
                "name": product_name,
                "calories": product.get("calories_per_100g", 0),
                "protein": product.get("protein_per_100g", 0),
                "fat": product.get("fat_per_100g", 0),
                "carbs": product.get("carbs_per_100g", 0)
            }

        storage["clarified_items"].append({
            "name": chosen["name"],
            "calories_per_100g": chosen.get("calories", 0),
            "protein_per_100g": chosen.get("protein", 0),
            "fat_per_100g": chosen.get("fat", 0),
            "carbs_per_100g": chosen.get("carbs", 0),
            "weight": None  # будет заполнено позже
        })
        storage["current_index"] += 1
        # Запрашиваем вес
        await ask_weight(message, user_id, idx, state)

async def ask_weight(message: Message, user_id: int, idx: int, state: FSMContext):
    """Запрашивает вес для продукта с индексом idx (уже добавленного в clarified_items)."""
    storage = _temp_storage.get(user_id)
    if not storage or idx >= len(storage["clarified_items"]):
        return

    product = storage["clarified_items"][idx]
    await message.answer(
        f"⚖️ Сколько грамм «{product['name']}»? (введите число)",
        reply_markup=types.ForceReply()
    )
    # Сохраняем индекс в состоянии
    await state.update_data(current_clarify_idx=idx)
    await state.set_state(FoodClarificationStates.waiting_for_weight)

@router.message(FoodClarificationStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    storage = _temp_storage.get(user_id)
    data = await state.get_data()
    idx = data.get("current_clarify_idx")

    weight, error = safe_parse_float(message.text, "вес")
    if error:
        await message.answer(f"❌ {error}. Попробуйте ещё раз (например, 150):")
        return

    if weight <= 0 or weight > 5000:
        await message.answer("❌ Вес должен быть от 1 до 5000 грамм. Повторите:")
        return

    # Сохраняем вес
    storage["clarified_items"][idx]["weight"] = weight
    # Переходим к следующему продукту
    storage["current_index"] += 1
    await clarify_next_product(message, user_id, state)

@router.callback_query(F.data.startswith("clr_var_"))
async def variant_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = callback.data.split("_")  # clr_var_idx_varindex
    idx = int(data[2])
    var_idx = int(data[3])
    user_id = callback.from_user.id
    storage = _temp_storage.get(user_id)
    if not storage or idx >= len(storage["original_items"]):
        await callback.message.edit_text("❌ Ошибка, начните заново.")
        return

    product = storage["original_items"][idx]
    variants = get_product_variants(product["name"])
    chosen = variants[var_idx]

    storage["clarified_items"].append({
        "name": chosen["name"],
        "calories_per_100g": chosen.get("calories", 0),
        "protein_per_100g": chosen.get("protein", 0),
        "fat_per_100g": chosen.get("fat", 0),
        "carbs_per_100g": chosen.get("carbs", 0),
        "weight": None
    })

    # Удаляем клавиатуру
    await callback.message.edit_text(f"✅ Выбрано: {chosen['name']}")
    await ask_weight(callback.message, user_id, len(storage["clarified_items"]) - 1, state)

@router.callback_query(F.data.startswith("clr_manual_"))
async def manual_entry(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("✍️ Введите название продукта вручную:")
    await state.set_state(FoodClarificationStates.waiting_for_manual_name)

@router.message(FoodClarificationStates.waiting_for_manual_name)
async def process_manual_name(message: Message, state: FSMContext):
    # Просто принимаем название, потом запросим вес
    # Здесь можно также поискать в базе, но упростим
    user_id = message.from_user.id
    storage = _temp_storage.get(user_id)
    if not storage:
        await state.clear()
        return

    product_name = message.text.strip()
    # Добавляем как продукт с нулевыми данными (потом запросим вес и, возможно, КБЖУ)
    storage["clarified_items"].append({
        "name": product_name,
        "calories_per_100g": 0,
        "protein_per_100g": 0,
        "fat_per_100g": 0,
        "carbs_per_100g": 0,
        "weight": None
    })
    await ask_weight(message, user_id, len(storage["clarified_items"]) - 1, state)

@router.callback_query(F.data.startswith("clr_skip_"))
async def skip_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    storage = _temp_storage.get(user_id)
    if storage:
        # Пропускаем этот продукт (не добавляем)
        storage["current_index"] += 1
        await callback.message.edit_text("⏭️ Продукт пропущен.")
        await clarify_next_product(callback.message, user_id, state)

async def finish_clarification(message: Message, user_id: int, state: FSMContext):
    """Сохраняет уточнённые продукты в базу и отправляет итог."""
    storage = _temp_storage.pop(user_id, None)
    if not storage:
        return

    clarified = storage["clarified_items"]
    if not clarified:
        await message.answer("❌ Нет продуктов для сохранения.")
        return

    # Преобразуем в формат, ожидаемый food_save_service
    food_items_for_save = []
    for item in clarified:
        weight = item.get("weight", 100)  # если вес не указан, берём 100г
        factor = weight / 100.0
        food_items_for_save.append({
            "name": item["name"],
            "quantity": weight,
            "unit": "г",
            "calories": item["calories_per_100g"] * factor,
            "protein": item["protein_per_100g"] * factor,
            "fat": item["fat_per_100g"] * factor,
            "carbs": item["carbs_per_100g"] * factor
        })

    # Сохраняем через сервис
    from services.food_save_service import food_save_service
    result = await food_save_service.save_food_to_db(
        user_id,
        food_items_for_save,
        meal_type="unknown"  # можно определить по контексту или спросить
    )

    if result["success"]:
        await message.answer(
            f"✅ Приём пищи сохранён!\n"
            f"🔥 Калории: {result['total_calories']:.0f}\n"
            f"🥩 Белки: {result['total_protein']:.1f}\n"
            f"🥑 Жиры: {result['total_fat']:.1f}\n"
            f"🍚 Углеводы: {result['total_carbs']:.1f}"
        )
    else:
        await message.answer(f"❌ Ошибка сохранения: {result.get('error')}")

    await state.clear()
