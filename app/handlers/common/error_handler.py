"""
Обработчик ошибок
"""
import logging
from aiogram import Router
from aiogram.types import ErrorEvent, Message
from aiogram.filters import ExceptionTypeFilter

logger = logging.getLogger(__name__)
router = Router()


@router.error(ExceptionTypeFilter(Exception))
async def handle_error(error_event: ErrorEvent):
    """
    Глобальный обработчик ошибок
    
    Args:
        error_event: Событие ошибки
    """
    exception = error_event.exception
    update = error_event.update
    
    # Логируем ошибку
    logger.error(
        f"Произошла ошибка: {type(exception).__name__}: {exception}",
        exc_info=exception
    )
    
    # Пытаемся отправить сообщение пользователю
    try:
        if update.message:
            await update.message.answer(
                "❌ Произошла внутренняя ошибка. "
                "Пожалуйста, попробуйте позже или обратитесь к администратору."
            )
        elif update.callback_query:
            await update.callback_query.answer(
                "❌ Произошла ошибка. Попробуйте позже.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке: {e}")


@router.message()
async def handle_unknown_message(message: Message, current_user=None):
    """
    Обработчик неизвестных сообщений
    
    Args:
        message: Сообщение
        current_user: Текущий пользователь
    """
    try:
        if not current_user:
            await message.answer(
                "❌ Вы не зарегистрированы в системе.\n"
                "Используйте команду /start для начала работы."
            )
            return
        
        # Отправляем сообщение о том, что команда не распознана
        await message.answer(
            "❓ Команда не распознана.\n\n"
            "Используйте /help для получения списка доступных команд\n"
            "или /start для возврата в главное меню."
        )
        
    except Exception as e:
        logger.error(f"Ошибка в handle_unknown_message: {e}")
