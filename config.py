import os
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (для локальной разработки)
load_dotenv()


class Config:
    """Конфигурация приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    WEBHOOK_SECRET: Optional[str] = os.getenv("WEBHOOK_SECRET")
    
    # YDB настройки
    YDB_ENDPOINT: str = os.getenv("YDB_ENDPOINT", "")
    YDB_DATABASE: str = os.getenv("YDB_DATABASE", "")
    YDB_CREDENTIALS_TYPE: str = os.getenv("YDB_CREDENTIALS_TYPE", "metadata")  # metadata, sa_key, token
    YDB_SERVICE_ACCOUNT_KEY: Optional[str] = os.getenv("YDB_SERVICE_ACCOUNT_KEY")
    YDB_TOKEN: Optional[str] = os.getenv("YDB_TOKEN")
    
    # Логирование
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Файловое хранилище (Object Storage)
    S3_ENDPOINT: Optional[str] = os.getenv("S3_ENDPOINT")
    S3_ACCESS_KEY: Optional[str] = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = os.getenv("S3_SECRET_KEY")
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET")
    
    # Настройки приложения
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
    ALLOWED_FILE_TYPES: list = ["jpg", "jpeg", "png", "pdf", "doc", "docx", "txt"]
    
    # Роли пользователей
    ROLES = {
        "director": "Директор",
        "manager": "Менеджер", 
        "chief_admin": "Главный админ",
        "sysadmin": "Системный администратор"
    }
    
    # Статусы задач
    TASK_STATUSES = {
        "new": "Новая",
        "in_progress": "В работе",
        "completed": "Выполнена",
        "not_completed": "Не выполнена",
        "overdue": "Просрочена"
    }
    
    # Приоритеты задач
    TASK_PRIORITIES = {
        "urgent": "Срочная",
        "normal": "Обычная", 
        "low": "Не очень срочная"
    }
    
    @classmethod
    def validate_required(cls) -> bool:
        """Проверяет наличие обязательных переменных окружения"""
        required_vars = ["BOT_TOKEN", "YDB_ENDPOINT", "YDB_DATABASE"]
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
        
        return True


# Создаем экземпляр конфигурации
config = Config()
