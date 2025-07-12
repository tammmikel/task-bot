"""
Сервис для работы с авторизацией и пользователями
"""
import logging
from typing import Optional, List

from app.database.repositories.user_repository import UserRepository
from app.database.models.user_model import User
from config import config

logger = logging.getLogger(__name__)


class AuthService:
    """Сервис для авторизации и управления пользователями"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Получает пользователя по Telegram ID
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Пользователь или None если не найден
        """
        try:
            return await self.user_repo.get_user_by_id(telegram_id)
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {telegram_id}: {e}")
            return None
    
    async def register_user(self, telegram_user_data: dict, role: str = None) -> User:
        """
        Регистрирует нового пользователя
        
        Args:
            telegram_user_data: Данные от Telegram
            role: Роль пользователя (если не указана, будет запрошена)
            
        Returns:
            Созданный пользователь
        """
        try:
            # Проверяем, не зарегистрирован ли уже
            existing_user = await self.get_user_by_telegram_id(telegram_user_data['user_id'])
            if existing_user:
                raise ValueError("Пользователь уже зарегистрирован")
            
            # Если роль не указана, используем роль по умолчанию
            if not role:
                role = 'sysadmin'  # По умолчанию сис-админ
            
            # Проверяем валидность роли
            if role not in config.ROLES:
                raise ValueError(f"Неверная роль: {role}")
            
            user_data = {
                'user_id': telegram_user_data['user_id'],
                'username': telegram_user_data.get('username'),
                'first_name': telegram_user_data['first_name'],
                'last_name': telegram_user_data.get('last_name'),
                'role': role,
                'is_active': True
            }
            
            user = await self.user_repo.create_user(user_data)
            logger.info(f"Зарегистрирован новый пользователь: {user.user_id} ({user.role})")
            
            return user
            
        except Exception as e:
            logger.error(f"Ошибка регистрации пользователя: {e}")
            raise
    
    async def update_user(self, user_id: int, updates: dict) -> bool:
        """
        Обновляет данные пользователя
        
        Args:
            user_id: ID пользователя
            updates: Обновления
            
        Returns:
            True если успешно
        """
        try:
            return await self.user_repo.update_user(user_id, updates)
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {user_id}: {e}")
            return False
    
    async def assign_role(self, user_id: int, new_role: str, assigner_id: int) -> bool:
        """
        Назначает роль пользователю
        
        Args:
            user_id: ID пользователя
            new_role: Новая роль
            assigner_id: ID того, кто назначает роль
            
        Returns:
            True если успешно
        """
        try:
            # Проверяем валидность роли
            if new_role not in config.ROLES:
                raise ValueError(f"Неверная роль: {new_role}")
            
            # Проверяем права назначающего
            assigner = await self.get_user_by_telegram_id(assigner_id)
            if not assigner or assigner.role != 'director':
                raise ValueError("Только директор может назначать роли")
            
            # Обновляем роль
            success = await self.user_repo.update_user(user_id, {'role': new_role})
            
            if success:
                logger.info(f"Пользователю {user_id} назначена роль {new_role} директором {assigner_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка назначения роли: {e}")
            return False
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """
        Получает пользователей по роли
        
        Args:
            role: Роль
            
        Returns:
            Список пользователей
        """
        try:
            return await self.user_repo.get_users_by_role(role)
        except Exception as e:
            logger.error(f"Ошибка получения пользователей по роли {role}: {e}")
            return []
    
    async def get_all_users(self) -> List[User]:
        """
        Получает всех пользователей
        
        Returns:
            Список всех пользователей
        """
        try:
            return await self.user_repo.get_all_users()
        except Exception as e:
            logger.error(f"Ошибка получения всех пользователей: {e}")
            return []
    
    def can_assign_roles(self, user: User) -> bool:
        """Проверяет, может ли пользователь назначать роли"""
        return user.role == 'director'
    
    def can_create_companies(self, user: User) -> bool:
        """Проверяет, может ли пользователь создавать компании"""
        return user.role in ['director', 'manager']
    
    def can_create_tasks(self, user: User) -> bool:
        """Проверяет, может ли пользователь создавать задачи"""
        return user.role in ['director', 'manager']
    
    def can_view_analytics(self, user: User) -> bool:
        """Проверяет, может ли пользователь просматривать аналитику"""
        return user.role == 'director'
    
    def is_executor(self, user: User) -> bool:
        """Проверяет, является ли пользователь исполнителем"""
        return user.role in ['chief_admin', 'sysadmin']
