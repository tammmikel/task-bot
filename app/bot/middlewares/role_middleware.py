"""
Middleware для проверки ролей пользователей
"""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)


class RoleMiddleware(BaseMiddleware):
    """Middleware для проверки ролей пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Добавляет информацию о правах пользователя
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Событие от Telegram
            data: Данные для обработчика
        """
        
        # Получаем роль пользователя из предыдущего middleware
        user_role = data.get('user_role')
        
        if user_role:
            # Добавляем флаги прав доступа
            data['can_create_companies'] = user_role in ['director', 'manager']
            data['can_assign_roles'] = user_role == 'director'
            data['can_create_tasks'] = user_role in ['director', 'manager']
            data['can_view_analytics'] = user_role == 'director'
            data['can_execute_tasks'] = user_role in ['chief_admin', 'sysadmin']
            data['is_admin'] = user_role in ['chief_admin', 'sysadmin']
            data['is_manager'] = user_role in ['director', 'manager']
        
        # Продолжаем обработку
        return await handler(event, data)
