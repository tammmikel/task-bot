"""
Middleware для проверки авторизации пользователей
"""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки авторизации пользователей"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Проверяет авторизацию пользователя перед обработкой события
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Событие от Telegram
            data: Данные для обработчика
            
        Returns:
            Результат обработчика или прерывание цепочки
        """
        
        # Получаем пользователя из события
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if not user:
            logger.warning("Событие без пользователя")
            return
        
        # Проверяем, зарегистрирован ли пользователь
        try:
            db_user = await self.auth_service.get_user_by_telegram_id(user.id)
            
            if db_user:
                # Пользователь найден, добавляем его в данные
                data['current_user'] = db_user
                data['user_role'] = db_user.role
                
                # Обновляем информацию о пользователе если изменилась
                await self._update_user_info(user, db_user)
                
            else:
                # Пользователь не зарегистрирован
                data['current_user'] = None
                data['user_role'] = None
                
                # Для команд регистрации пропускаем дальше
                if isinstance(event, Message):
                    if event.text and (event.text.startswith('/start') or event.text.startswith('/register')):
                        # Добавляем информацию о новом пользователе
                        data['telegram_user'] = {
                            'user_id': user.id,
                            'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name
                        }
                        return await handler(event, data)
                
                # Для остальных команд отправляем сообщение о необходимости регистрации
                if isinstance(event, Message):
                    await event.answer(
                        "❌ Вы не зарегистрированы в системе.\n"
                        "Используйте команду /start для начала работы."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "❌ Вы не зарегистрированы в системе.",
                        show_alert=True
                    )
                
                return
        
        except Exception as e:
            logger.error(f"Ошибка проверки авторизации для пользователя {user.id}: {e}")
            return
        
        # Продолжаем обработку
        return await handler(event, data)
    
    async def _update_user_info(self, telegram_user, db_user):
        """Обновляет информацию о пользователе если она изменилась"""
        try:
            updates = {}
            
            if telegram_user.username != db_user.username:
                updates['username'] = telegram_user.username
            
            if telegram_user.first_name != db_user.first_name:
                updates['first_name'] = telegram_user.first_name
                
            if telegram_user.last_name != db_user.last_name:
                updates['last_name'] = telegram_user.last_name
            
            if updates:
                await self.auth_service.update_user(db_user.user_id, updates)
                logger.info(f"Обновлена информация пользователя {db_user.user_id}")
                
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {db_user.user_id}: {e}")