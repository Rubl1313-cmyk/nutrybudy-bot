"""
handlers/reminder_callbacks.py
Обработчики callback для еженедельных напоминаний
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from services.reminder_service import (
    handle_weekly_update_weight,
    handle_weekly_update_measurements,
    handle_weekly_progress,
    handle_weekly_skip
)

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "weekly_update_weight")
async def weekly_update_weight_callback(callback: CallbackQuery, state: FSMContext):
    """Обновление веса из еженедельного напоминания"""
    await handle_weekly_update_weight(callback, callback.bot, state)

@router.callback_query(F.data == "weekly_update_measurements")
async def weekly_update_measurements_callback(callback: CallbackQuery, state: FSMContext):
    """Обновление обхватов из еженедельного напоминания"""
    await handle_weekly_update_measurements(callback, callback.bot, state)

@router.callback_query(F.data == "weekly_progress")
async def weekly_progress_callback(callback: CallbackQuery, state: FSMContext):
    """Показ прогресса из еженедельного напоминания"""
    await handle_weekly_progress(callback, callback.bot)

@router.callback_query(F.data == "weekly_skip")
async def weekly_skip_callback(callback: CallbackQuery, state: FSMContext):
    """Пропуск еженедельного напоминания"""
    await handle_weekly_skip(callback, callback.bot)
