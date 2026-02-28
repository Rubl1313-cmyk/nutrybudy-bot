# Добавьте эту функцию после handle_photo и handle_voice:

@router.message(F.document)
async def handle_document(message: Message, state: FSMContext):
    """Обработка фото, отправленных как документ"""
    doc = message.document
    
    # Проверяем, что это изображение
    if not (doc.mime_type and doc.mime_type.startswith('image/')):
        return  # Игнорируем не-изображения
    
    await message.answer("🔍 Анализирую изображение (отправлено как документ)...")
    
    try:
        file_info = await message.bot.get_file(doc.file_id)
        file_bytes = await message.bot.download_file(file_info.file_path)
        file_data = file_bytes.read()
        
        description = await analyze_food_image(file_data)
        if not description:
            await message.answer("❌ Не удалось распознать изображение.")
            return
        
        await state.update_data(ai_description=description)
        foods = await search_food(description)
        
        if foods:
            from keyboards.inline import get_food_selection_keyboard
            await message.answer(
                f"🧠 <b>Распознано:</b> {description}\n\nВыберите продукт:",
                reply_markup=get_food_selection_keyboard(foods),
                parse_mode="HTML"
            )
            await state.set_state(FoodStates.selecting_food)
            await state.update_data(foods=foods)
        else:
            await message.answer(
                f"🧠 Описание: {description}\n\nВведите название блюда вручную:"
            )
            await state.set_state(FoodStates.manual_food_name)
            
    except Exception as e:
        import logging
        logging.error(f"Document processing error: {e}")
        await message.answer("❌ Ошибка при обработке файла. Попробуйте отправить как фото.")
