"""
Модель файла
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TaskFile:
    """Модель файла, прикрепленного к задаче"""
    
    file_id: int
    task_id: int
    user_id: int
    file_name: str
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    created_at: datetime
    
    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def size_human_readable(self) -> str:
        """Возвращает размер файла в читаемом формате"""
        if not self.file_size:
            return "Неизвестно"
        
        size = self.file_size
        units = ['Б', 'КБ', 'МБ', 'ГБ']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    @property
    def file_extension(self) -> str:
        """Возвращает расширение файла"""
        if '.' in self.file_name:
            return self.file_name.split('.')[-1].lower()
        return ""
    
    def __str__(self) -> str:
        return f"TaskFile(id={self.file_id}, name='{self.file_name}')"
