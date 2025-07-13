"""
Подключение к YDB базе данных
"""
import asyncio
import logging
from typing import Optional
import ydb
import threading

from config import config

logger = logging.getLogger(__name__)


class YDBConnection:
    """Класс для работы с YDB подключением"""
    
    def __init__(self):
        self._driver: Optional[ydb.Driver] = None
        self._pool: Optional[ydb.SessionPool] = None
        self._lock = threading.Lock()
    
    async def connect(self) -> None:
        """Создает подключение к YDB"""
        if self._pool is not None:
            return
            
        with self._lock:
            if self._pool is not None:
                return
                
            try:
                # Настройка credentials
                if config.YDB_CREDENTIALS_TYPE == "metadata":
                    credentials = ydb.iam.MetadataUrlCredentials()
                elif config.YDB_CREDENTIALS_TYPE == "sa_key":
                    credentials = ydb.iam.ServiceAccountCredentials.from_file(
                        config.YDB_SERVICE_ACCOUNT_KEY
                    )
                elif config.YDB_CREDENTIALS_TYPE == "token":
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
                self._driver.wait(timeout=10)
                self._pool = ydb.SessionPool(self._driver)
                
                logger.info("Успешно подключились к YDB")
                
            except Exception as e:
                logger.error(f"Ошибка подключения к YDB: {e}")
                self._cleanup()
                raise
    
    def connect_sync(self) -> None:
        """Синхронная версия подключения к YDB"""
        if self._pool is not None:
            return
            
        with self._lock:
            if self._pool is not None:
                return
                
            try:
                # Настройка credentials
                if config.YDB_CREDENTIALS_TYPE == "metadata":
                    credentials = ydb.iam.MetadataUrlCredentials()
                elif config.YDB_CREDENTIALS_TYPE == "sa_key":
                    credentials = ydb.iam.ServiceAccountCredentials.from_file(
                        config.YDB_SERVICE_ACCOUNT_KEY
                    )
                elif config.YDB_CREDENTIALS_TYPE == "token":
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
                self._driver.wait(timeout=10)
                self._pool = ydb.SessionPool(self._driver)
                
                logger.info("Успешно подключились к YDB (sync)")
                
            except Exception as e:
                logger.error(f"Ошибка подключения к YDB: {e}")
                self._cleanup()
                raise
    
    def _cleanup(self):
        """Очищает ресурсы"""
        if self._driver:
            try:
                self._driver.stop()
            except:
                pass
            self._driver = None
        self._pool = None
    
    async def disconnect(self) -> None:
        """Закрывает подключение к YDB"""
        try:
            if self._driver:
                self._driver.stop()
                
            self._cleanup()
            logger.info("Отключились от YDB")
        except Exception as e:
            logger.error(f"Ошибка отключения от YDB: {e}")
    
    def get_pool(self) -> ydb.SessionPool:
        """Возвращает session pool"""
        if not self._pool:
            raise RuntimeError("YDB подключение не установлено")
        return self._pool
    
    def execute_query(self, query: str, parameters: dict = None):
        """
        Выполняет запрос к YDB по примеру из вашего файла
        
        Args:
            query: SQL запрос
            parameters: Параметры запроса
            
        Returns:
            Результат выполнения запроса
        """
        if not self._pool:
            self.connect_sync()
        
        print(f"[DEBUG CONNECTION] Получили параметры: {parameters}")
        logger.info(f"Выполняем запрос с параметрами: {parameters}")
        
        def callee(session):
            print(f"[DEBUG CONNECTION] В callee, параметры: {parameters}")
            if parameters:
                print(f"[DEBUG CONNECTION] Передаем параметры в execute...")
                return session.transaction().execute(
                    query, 
                    parameters,  # Передаем как есть, как в вашем примере
                    commit_tx=True,
                    settings=ydb.BaseRequestSettings().with_timeout(30).with_operation_timeout(25)
                )
            else:
                print(f"[DEBUG CONNECTION] Выполняем без параметров...")
                return session.transaction().execute(
                    query,
                    commit_tx=True,
                    settings=ydb.BaseRequestSettings().with_timeout(30).with_operation_timeout(25)
                )
        
        try:
            print(f"[DEBUG CONNECTION] Вызываем retry_operation_sync...")
            result = self._pool.retry_operation_sync(callee)
            print(f"[DEBUG CONNECTION] Запрос выполнен успешно!")
            return result
        except Exception as e:
            print(f"[DEBUG CONNECTION] ОШИБКА YDB: {e}")
            logger.error(f"Ошибка выполнения запроса: {e}")
            self._cleanup()
            raise


# Глобальный экземпляр подключения
ydb_connection = YDBConnection()


def get_ydb_connection() -> YDBConnection:
    """Возвращает подключение к YDB"""
    if not ydb_connection._pool:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            ydb_connection.connect_sync()
        else:
            loop.run_until_complete(ydb_connection.connect())
    return ydb_connection