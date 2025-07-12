"""
Настройка диспетчера и подключение обработчиков
"""
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.middlewares.auth_middleware import AuthMiddleware
from app.bot.middlewares.role_middleware import RoleMiddleware

# Импорт существующих обработчиков
from app.handlers.common import start_handler, help_handler, error_handler, menu_handler
from app.handlers.auth import registration_handler, role_assignment_handler
from app.handlers.company import create_company_handler, list_companies_handler
# Остальные обработчики импортируем по мере создания
# from app.handlers.task import (
#     create_task_handler, 
#     list_tasks_handler, 
#     update_task_handler,
#     task_status_handler
# )
# from app.handlers.comment import add_comment_handler
# from app.handlers.file import upload_file_handler
# from app.handlers.analytics import dashboard_handler

logger = logging.getLogger(__name__)


async def setup_dispatcher() -> Dispatcher:
    """
    Настраивает диспетчер с middleware и обработчиками
    
    Returns:
        Dispatcher: Настроенный диспетчер
    """
    # Создаем диспетчер с хранилищем состояний в памяти
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(RoleMiddleware())
    
    # Общие обработчики
    dp.include_router(start_handler.router)
    dp.include_router(help_handler.router)
    dp.include_router(menu_handler.router)
    dp.include_router(error_handler.router)
    
    # Авторизация
    dp.include_router(registration_handler.router)
    dp.include_router(role_assignment_handler.router)
    
    # Компании
    dp.include_router(create_company_handler.router)
    dp.include_router(list_companies_handler.router)
    
    # Остальные обработчики добавим по мере создания
    # dp.include_router(create_task_handler.router)
    # dp.include_router(list_tasks_handler.router)
    # dp.include_router(update_task_handler.router)
    # dp.include_router(task_status_handler.router)
    # dp.include_router(add_comment_handler.router)
    # dp.include_router(upload_file_handler.router)
    # dp.include_router(dashboard_handler.router)
    
    logger.info("Диспетчер успешно настроен")
    return dp