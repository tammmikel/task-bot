"""
Модель задачи
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .base_model import BaseModel
from config import config


@dataclass
class Task(BaseModel):
    """Модель задачи"""
    
    task_id: int
    title: str
    description: Optional[str]
    company_id: int
    creator_id: int
    assignee_id: Optional[int]
    initiator_name: str
    initiator_phone: str
    priority: str
    status: str
    deadline: Optional[datetime]
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.utcnow()
        if not hasattr(self, 'updated_at') or self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @property
    def status_display(self) -> str:
        """Возвращает отображаемое название статуса"""
        return config.TASK_STATUSES.get(self.status, self.status)
    
    @property
    def priority_display(self) -> str:
        """Возвращает отображаемое название приоритета"""
        return config.TASK_PRIORITIES.get(self.priority, self.priority)
    
    @property
    def is_overdue(self) -> bool:
        """Проверяет, просрочена ли задача"""
        if not self.deadline:
            return False
        
        if self.status in ['completed', 'not_completed']:
            return False
            
        return datetime.utcnow() > self.deadline
    
    @property
    def is_completed(self) -> bool:
        """Проверяет, выполнена ли задача"""
        return self.status == 'completed'
    
    @property
    def priority_emoji(self) -> str:
        """Возвращает эмодзи для приоритета"""
        priority_emojis = {
            'urgent': '🔴',
            'normal': '🟡', 
            'low': '🟢'
        }
        return priority_emojis.get(self.priority, '⚪')
    
    @property
    def status_emoji(self) -> str:
        """Возвращает эмодзи для статуса"""
        status_emojis = {
            'new': '🆕',
            'in_progress': '⏳',
            'completed': '✅',
            'not_completed': '❌',
            'overdue': '🔴'
        }
        
        # Если задача просрочена, показываем это
        if self.is_overdue:
            return status_emojis['overdue']
            
        return status_emojis.get(self.status, '⚪')
    
    def set_status(self, new_status: str):
        """Устанавливает новый статус задачи"""
        old_status = self.status
        self.status = new_status
        self.update_timestamp()
        
        # Если задача завершена, устанавливаем время завершения
        if new_status == 'completed' and old_status != 'completed':
            self.completed_at = datetime.utcnow()
        
        # Если задача возвращена в работу, убираем время завершения
        elif new_status == 'in_progress' and old_status in ['completed', 'not_completed']:
            self.completed_at = None
    
    def __str__(self) -> str:
        return f"Task(id={self.task_id}, title='{self.title}', status='{self.status}')"
