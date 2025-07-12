"""
Модель пользователя
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .base_model import BaseModel


@dataclass
class User(BaseModel):
    """Модель пользователя системы"""
    
    user_id: int  # Telegram ID
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    role: str
    phone: Optional[str]
    is_active: bool = True
    
    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.utcnow()
        if not hasattr(self, 'updated_at') or self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def display_name(self) -> str:
        """Возвращает отображаемое имя (с username если есть)"""
        name = self.full_name
        if self.username:
            name += f" (@{self.username})"
        return name
    
    def has_role(self, role: str) -> bool:
        """Проверяет, имеет ли пользователь указанную роль"""
        return self.role == role
    
    def has_any_role(self, roles: list) -> bool:
        """Проверяет, имеет ли пользователь любую из указанных ролей"""
        return self.role in roles
