"""
Базовая модель для всех моделей данных
"""
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class BaseModel:
    """Базовая модель с общими полями"""
    
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует модель в словарь"""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, datetime):
                    result[field_name] = field_value.isoformat()
                else:
                    result[field_name] = field_value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Создает экземпляр модели из словаря"""
        # Преобразуем строки дат обратно в datetime
        for field_name in ['created_at', 'updated_at', 'deadline', 'completed_at']:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    pass
        
        return cls(**data)
    
    def update_timestamp(self):
        """Обновляет поле updated_at"""
        self.updated_at = datetime.utcnow()
