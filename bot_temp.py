def register_handlers():
    """Регистрация всех обработчиков"""
    # Импорты обработчиков
    from handlers.common import router as common_router
    from handlers.reply_handlers import router as reply_handlers_router
    from handlers.profile_new import router as profile_router
    from handlers.progress import router as progress_router
    from handlers.achievements import router as achievements_router
    from handlers.ai_assistant import router as ai_assistant_router
    from handlers.help import router as help_router
    from handlers.universal import router as universal_router

    # Регистрация роутеров - важен порядок!
    
    # Сначала команды и специализированные обработчики
    dp.include_router(common_router)
    dp.include_router(reply_handlers_router)  # Обработка кнопок главного меню
    dp.include_router(profile_router)  # Профиль
    dp.include_router(progress_router)  # Прогресс
    dp.include_router(achievements_router)  # Достижения
    dp.include_router(ai_assistant_router)  # AI Ассистент
    dp.include_router(help_router)  # Помощь

    # Универсальный обработчик - самый последний (обрабатывает всё, что не попало выше)
    dp.include_router(universal_router)

    # Установка middleware (исправлено для aiogram 3.x)
    from utils.middleware import SmartRateLimitMiddleware

    dp.message.middleware(SmartRateLimitMiddleware(user_rate_limiter, is_global=False))
    dp.callback_query.middleware(SmartRateLimitMiddleware(user_rate_limiter, is_global=False))
    dp.message.middleware(SmartRateLimitMiddleware(global_rate_limiter, is_global=True))
    dp.callback_query.middleware(SmartRateLimitMiddleware(global_rate_limiter, is_global=True))

    logger.info("Rate limiting middleware enabled")
    logger.info("All handlers registered")
