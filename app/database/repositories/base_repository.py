"""
Базовый репозиторий для работы с данными
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database.connection import get_ydb_connection

logger = logging.getLogger(__name__)


class BaseRepository:
    """Базовый класс для всех репозиториев"""
    
    def __init__(self):
        self.connection = None
    
    async def _get_connection(self):
        """Получает подключение к базе данных"""
        if not self.connection:
            self.connection = await get_ydb_connection()
        return self.connection
    
    async def _execute_query(self, query: str, parameters: Dict[str, Any] = None) -> Any:
        """
        Выполняет запрос к базе данных
        
        Args:
            query: SQL запрос
            parameters: Параметры запроса
            
        Returns:
            Результат выполнения запроса
        """
        try:
            conn = await self._get_connection()
            result = await conn.execute_query(query, parameters or {})
            return result
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            logger.error(f"Запрос: {query}")
            logger.error(f"Параметры: {parameters}")
            raise
    
    def _prepare_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Подготавливает datetime для вставки в YDB"""
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Парсит datetime из YDB"""
        if not dt_str:
            return None
        try:
            # YDB возвращает datetime в ISO формате
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    async def _fetch_one(self, query: str, parameters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Выполняет запрос и возвращает одну запись"""
        result = await self._execute_query(query, parameters)
        
        if result and len(result) > 0 and len(result[0].rows) > 0:
            # Преобразуем результат в словарь
            row = result[0].rows[0]
            columns = [column.name for column in result[0].columns]
            return dict(zip(columns, row))
        
        return None
    
    async def _fetch_all(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Выполняет запрос и возвращает все записи"""
        result = await self._execute_query(query, parameters)
        
        if result and len(result) > 0:
            columns = [column.name for column in result[0].columns]
            return [dict(zip(columns, row)) for row in result[0].rows]
        
        return []
