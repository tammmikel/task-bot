"""
Подключение к YDB базе данных
"""
import asyncio
import logging
from typing import Optional
import ydb

from config import config

logger = logging.getLogger(__name__)


class YDBConnection:
    """Класс для работы с YDB подключением"""
    
    def __init__(self):
        self._driver: Optional[ydb.Driver] = None
        self._pool: Optional[ydb.SessionPool] = None
    
    async def connect(self) -> None:
        """Создает подключение к YDB"""
        try:
            # Настройка credentials
            if config.YDB_CREDENTIALS_TYPE == "metadata":
                # Используем metadata service (для Cloud Function)
                credentials = ydb.iam.MetadataUrlCredentials()
            elif config.YDB_CREDENTIALS_TYPE == "sa_key":
                # Используем service account key
                credentials = ydb.iam.ServiceAccountCredentials.from_file(
                    config.YDB_SERVICE_ACCOUNT_KEY
                )
            elif config.YDB_CREDENTIALS_TYPE == "token":
                # Используем токен
                credentials = ydb.AccessTokenCredentials(config.YDB_TOKEN)
            else:
                raise ValueError(f"Неподдерживаемый тип credentials: {config.YDB_CREDENTIALS_TYPE}")
            
            # Создаем driver
            driver_config = ydb.DriverConfig(
                endpoint=config.YDB_ENDPOINT,
                database=config.YDB_DATABASE,
                credentials=credentials
            )
            
            self._driver = ydb.Driver(driver_config)
            await asyncio.get_event_loop().run_in_executor(
                None, self._driver.wait, 5
            )
            
            # Создаем session pool
            self._pool = ydb.SessionPool(self._driver)
            
            logger.info("Успешно подключились к YDB")
            
        except Exception as e:
            logger.error(f"Ошибка подключения к YDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Закрывает подключение к YDB"""
        try:
            if self._driver:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._driver.stop
                )
                self._driver = None
                self._pool = None
                logger.info("Отключились от YDB")
        except Exception as e:
            logger.error(f"Ошибка отключения от YDB: {e}")
    
    def get_pool(self) -> ydb.SessionPool:
        """Возвращает session pool"""
        if not self._pool:
            raise RuntimeError("YDB подключение не установлено")
        return self._pool
    
    async def execute_query(self, query: str, parameters: dict = None):
        """
        Выполняет запрос к YDB
        
        Args:
            query: SQL запрос
            parameters: Параметры запроса
            
        Returns:
            Результат выполнения запроса
        """
        if not self._pool:
            await self.connect()
        
        def _execute():
            return self._pool.retry_operation_sync(
                lambda session: session.transaction().execute(
                    query,
                    parameters or {},
                    commit_tx=True,
                    settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
                )
            )
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _execute)
            return result
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            raise


# Глобальный экземпляр подключения
ydb_connection = YDBConnection()


async def get_ydb_connection() -> YDBConnection:
    """Возвращает подключение к YDB"""
    if not ydb_connection._pool:
        await ydb_connection.connect()
    return ydb_connection