"""
Модель компании
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .base_model import BaseModel


@dataclass
class Company(BaseModel):
    """Модель компании"""
    
    company_id: int
    name: str
    description: Optional[str]
    created_by: int  # ID пользователя, создавшего компанию
    is_active: bool = True
    
    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.utcnow()
        if not hasattr(self, 'updated_at') or self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @property
    def short_description(self) -> str:
        """Возвращает короткое описание компании"""
        if not self.description:
            return "Без описания"
        
        if len(self.description) <= 50:
            return self.description
        
        return self.description[:47] + "..."
    
    def __str__(self) -> str:
        return f"Company(id={self.company_id}, name='{self.name}')"
