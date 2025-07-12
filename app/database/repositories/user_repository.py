"""
Репозиторий для работы с пользователями
"""
import logging
from typing import Optional, List
from datetime import datetime

from .base_repository import BaseRepository
from app.database.models.user_model import User

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями"""
    
    async def create_user(self, user_data: dict) -> User:
        """
        Создает нового пользователя
        
        Args:
            user_data: Данные пользователя
            
        Returns:
            Созданный пользователь
        """
        now = datetime.utcnow()
        
        query = """
        DECLARE $user_id AS Uint64;
        DECLARE $username AS Optional<String>;
        DECLARE $first_name AS String;
        DECLARE $last_name AS Optional<String>;
        DECLARE $role AS String;
        DECLARE $phone AS Optional<String>;
        DECLARE $is_active AS Bool;
        DECLARE $created_at AS Datetime;
        DECLARE $updated_at AS Datetime;
        
        INSERT INTO users (
            user_id, username, first_name, last_name, role, phone, 
            is_active, created_at, updated_at
        ) VALUES (
            $user_id, $username, $first_name, $last_name, $role, $phone,
            $is_active, $created_at, $updated_at
        );
        """
        
        parameters = {
            '$user_id': user_data['user_id'],
            '$username': user_data.get('username'),
            '$first_name': user_data['first_name'],
            '$last_name': user_data.get('last_name'),
            '$role': user_data['role'],
            '$phone': user_data.get('phone'),
            '$is_active': user_data.get('is_active', True),
            '$created_at': now,
            '$updated_at': now
        }
        
        await self._execute_query(query, parameters)
        
        # Возвращаем созданного пользователя
        return User(
            user_id=user_data['user_id'],
            username=user_data.get('username'),
            first_name=user_data['first_name'],
            last_name=user_data.get('last_name'),
            role=user_data['role'],
            phone=user_data.get('phone'),
            is_active=user_data.get('is_active', True),
            created_at=now,
            updated_at=now
        )
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Получает пользователя по Telegram ID
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            Пользователь или None
        """
        query = """
        DECLARE $user_id AS Uint64;
        
        SELECT user_id, username, first_name, last_name, role, phone,
               is_active, created_at, updated_at
        FROM users
        WHERE user_id = $user_id AND is_active = true;
        """
        
        parameters = {'$user_id': user_id}
        row = await self._fetch_one(query, parameters)
        
        if row:
            return User(
                user_id=row['user_id'],
                username=row['username'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                role=row['role'],
                phone=row['phone'],
                is_active=row['is_active'],
                created_at=self._parse_datetime(row['created_at']),
                updated_at=self._parse_datetime(row['updated_at'])
            )
        
        return None
    
    async def update_user(self, user_id: int, updates: dict) -> bool:
        """
        Обновляет данные пользователя
        
        Args:
            user_id: ID пользователя
            updates: Словарь с обновлениями
            
        Returns:
            True если обновление прошло успешно
        """
        if not updates:
            return True
        
        # Формируем SET часть запроса
        set_parts = []
        parameters = {'$user_id': user_id, '$updated_at': datetime.utcnow()}
        
        for field, value in updates.items():
            if field in ['username', 'first_name', 'last_name', 'role', 'phone', 'is_active']:
                param_name = f'${field}'
                set_parts.append(f"{field} = {param_name}")
                parameters[param_name] = value
        
        if not set_parts:
            return True
        
        set_parts.append("updated_at = $updated_at")
        
        query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $updated_at AS Datetime;
        {' '.join([f'DECLARE {param} AS {self._get_ydb_type(updates[param[1:]])};' 
                  for param in parameters.keys() if param not in ['$user_id', '$updated_at']])}
        
        UPDATE users
        SET {', '.join(set_parts)}
        WHERE user_id = $user_id;
        """
        
        await self._execute_query(query, parameters)
        return True
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """
        Получает всех пользователей с указанной ролью
        
        Args:
            role: Роль пользователей
            
        Returns:
            Список пользователей
        """
        query = """
        DECLARE $role AS String;
        
        SELECT user_id, username, first_name, last_name, role, phone,
               is_active, created_at, updated_at
        FROM users
        WHERE role = $role AND is_active = true
        ORDER BY first_name;
        """
        
        parameters = {'$role': role}
        rows = await self._fetch_all(query, parameters)
        
        users = []
        for row in rows:
            users.append(User(
                user_id=row['user_id'],
                username=row['username'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                role=row['role'],
                phone=row['phone'],
                is_active=row['is_active'],
                created_at=self._parse_datetime(row['created_at']),
                updated_at=self._parse_datetime(row['updated_at'])
            ))
        
        return users
    
    async def get_all_users(self) -> List[User]:
        """
        Получает всех активных пользователей
        
        Returns:
            Список всех пользователей
        """
        query = """
        SELECT user_id, username, first_name, last_name, role, phone,
               is_active, created_at, updated_at
        FROM users
        WHERE is_active = true
        ORDER BY role, first_name;
        """
        
        rows = await self._fetch_all(query)
        
        users = []
        for row in rows:
            users.append(User(
                user_id=row['user_id'],
                username=row['username'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                role=row['role'],
                phone=row['phone'],
                is_active=row['is_active'],
                created_at=self._parse_datetime(row['created_at']),
                updated_at=self._parse_datetime(row['updated_at'])
            ))
        
        return users
    
    def _get_ydb_type(self, value) -> str:
        """Определяет тип YDB для значения"""
        if isinstance(value, str):
            return "Optional<String>"
        elif isinstance(value, bool):
            return "Bool"
        elif isinstance(value, int):
            return "Uint64"
        else:
            return "Optional<String>"
