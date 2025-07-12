"""
Модель комментария к задаче
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Comment:
    """Модель комментария к задаче"""
    
    comment_id: int
    task_id: int
    user_id: int
    comment_text: str
    created_at: datetime
    
    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def short_text(self) -> str:
        """Возвращает короткий текст комментария"""
        if len(self.comment_text) <= 100:
            return self.comment_text
        return self.comment_text[:97] + "..."
    
    def __str__(self) -> str:
        return f"Comment(id={self.comment_id}, task_id={self.task_id})"
