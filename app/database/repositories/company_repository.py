"""
Репозиторий для работы с компаниями
"""
import logging
from typing import Optional, List
from datetime import datetime

from .base_repository import BaseRepository
from app.database.models.company_model import Company

logger = logging.getLogger(__name__)


class CompanyRepository(BaseRepository):
    """Репозиторий для работы с компаниями"""
    
    async def create_company(self, company_data: dict) -> Company:
        """
        Создает новую компанию
        
        Args:
            company_data: Данные компании
            
        Returns:
            Созданная компания
        """
        now = datetime.utcnow()
        
        # Получаем следующий ID для компании
        company_id = await self._get_next_company_id()
        
        query = """
        DECLARE $company_id AS Uint64;
        DECLARE $name AS String;
        DECLARE $description AS Optional<String>;
        DECLARE $created_by AS Uint64;
        DECLARE $is_active AS Bool;
        DECLARE $created_at AS Datetime;
        DECLARE $updated_at AS Datetime;
        
        INSERT INTO companies (
            company_id, name, description, created_by, is_active, created_at, updated_at
        ) VALUES (
            $company_id, $name, $description, $created_by, $is_active, $created_at, $updated_at
        );
        """
        
        parameters = {
            '$company_id': company_id,
            '$name': company_data['name'],
            '$description': company_data.get('description'),
            '$created_by': company_data['created_by'],
            '$is_active': company_data.get('is_active', True),
            '$created_at': now,
            '$updated_at': now
        }
        
        await self._execute_query(query, parameters)
        
        return Company(
            company_id=company_id,
            name=company_data['name'],
            description=company_data.get('description'),
            created_by=company_data['created_by'],
            is_active=company_data.get('is_active', True),
            created_at=now,
            updated_at=now
        )
    
    async def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """
        Получает компанию по ID
        
        Args:
            company_id: ID компании
            
        Returns:
            Компания или None
        """
        query = """
        DECLARE $company_id AS Uint64;
        
        SELECT company_id, name, description, created_by, is_active, created_at, updated_at
        FROM companies
        WHERE company_id = $company_id AND is_active = true;
        """
        
        parameters = {'$company_id': company_id}
        row = await self._fetch_one(query, parameters)
        
        if row:
            return Company(
                company_id=row['company_id'],
                name=row['name'],
                description=row['description'],
                created_by=row['created_by'],
                is_active=row['is_active'],
                created_at=self._parse_datetime(row['created_at']),
                updated_at=self._parse_datetime(row['updated_at'])
            )
        
        return None
    
    async def get_all_companies(self) -> List[Company]:
        """
        Получает все активные компании
        
        Returns:
            Список компаний
        """
        query = """
        SELECT company_id, name, description, created_by, is_active, created_at, updated_at
        FROM companies
        WHERE is_active = true
        ORDER BY name;
        """
        
        rows = await self._fetch_all(query)
        
        companies = []
        for row in rows:
            companies.append(Company(
                company_id=row['company_id'],
                name=row['name'],
                description=row['description'],
                created_by=row['created_by'],
                is_active=row['is_active'],
                created_at=self._parse_datetime(row['created_at']),
                updated_at=self._parse_datetime(row['updated_at'])
            ))
        
        return companies
    
    async def update_company(self, company_id: int, updates: dict) -> bool:
        """
        Обновляет компанию
        
        Args:
            company_id: ID компании
            updates: Обновления
            
        Returns:
            True если успешно
        """
        if not updates:
            return True
        
        set_parts = []
        parameters = {'$company_id': company_id, '$updated_at': datetime.utcnow()}
        
        for field, value in updates.items():
            if field in ['name', 'description', 'is_active']:
                param_name = f'${field}'
                set_parts.append(f"{field} = {param_name}")
                parameters[param_name] = value
        
        if not set_parts:
            return True
        
        set_parts.append("updated_at = $updated_at")
        
        query = f"""
        DECLARE $company_id AS Uint64;
        DECLARE $updated_at AS Datetime;
        {' '.join([f'DECLARE {param} AS {self._get_ydb_type(updates[param[1:]])};' 
                  for param in parameters.keys() if param not in ['$company_id', '$updated_at']])}
        
        UPDATE companies
        SET {', '.join(set_parts)}
        WHERE company_id = $company_id;
        """
        
        await self._execute_query(query, parameters)
        return True
    
    async def search_companies(self, search_term: str) -> List[Company]:
        """
        Ищет компании по названию
        
        Args:
            search_term: Поисковый запрос
            
        Returns:
            Список найденных компаний
        """
        query = """
        DECLARE $search_term AS String;
        
        SELECT company_id, name, description, created_by, is_active, created_at, updated_at
        FROM companies
        WHERE is_active = true AND (
            String::Contains(LOWER(name), LOWER($search_term)) OR
            String::Contains(LOWER(description), LOWER($search_term))
        )
        ORDER BY name;
        """
        
        parameters = {'$search_term': search_term}
        rows = await self._fetch_all(query, parameters)
        
        companies = []
        for row in rows:
            companies.append(Company(
                company_id=row['company_id'],
                name=row['name'],
                description=row['description'],
                created_by=row['created_by'],
                is_active=row['is_active'],
                created_at=self._parse_datetime(row['created_at']),
                updated_at=self._parse_datetime(row['updated_at'])
            ))
        
        return companies
    
    async def _get_next_company_id(self) -> int:
        """Получает следующий ID для новой компании"""
        query = """
        SELECT MAX(company_id) AS max_id FROM companies;
        """
        
        row = await self._fetch_one(query)
        
        if row and row['max_id'] is not None:
            return row['max_id'] + 1
        else:
            return 1
    
    def _get_ydb_type(self, value) -> str:
        """Определяет тип YDB для значения"""
        if isinstance(value, str):
            return "String"
        elif isinstance(value, bool):
            return "Bool"
        elif isinstance(value, int):
            return "Uint64"
        else:
            return "Optional<String>"
