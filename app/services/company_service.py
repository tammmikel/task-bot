"""
Сервис для работы с компаниями
"""
import logging
from typing import Optional, List

from app.database.repositories.company_repository import CompanyRepository
from app.database.models.company_model import Company

logger = logging.getLogger(__name__)


class CompanyService:
    """Сервис для работы с компаниями"""
    
    def __init__(self):
        self.company_repo = CompanyRepository()
    
    async def create_company(self, name: str, description: str, created_by: int) -> Company:
        """
        Создает новую компанию
        
        Args:
            name: Название компании
            description: Описание компании
            created_by: ID создателя
            
        Returns:
            Созданная компания
        """
        try:
            # Проверяем, не существует ли уже компания с таким названием
            existing_companies = await self.search_companies(name)
            for company in existing_companies:
                if company.name.lower() == name.lower():
                    raise ValueError(f"Компания с названием '{name}' уже существует")
            
            company_data = {
                'name': name.strip(),
                'description': description.strip() if description else None,
                'created_by': created_by
            }
            
            company = await self.company_repo.create_company(company_data)
            logger.info(f"Создана новая компания: {company.name} (ID: {company.company_id})")
            
            return company
            
        except Exception as e:
            logger.error(f"Ошибка создания компании: {e}")
            raise
    
    async def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """
        Получает компанию по ID
        
        Args:
            company_id: ID компании
            
        Returns:
            Компания или None
        """
        try:
            return await self.company_repo.get_company_by_id(company_id)
        except Exception as e:
            logger.error(f"Ошибка получения компании {company_id}: {e}")
            return None
    
    async def get_all_companies(self) -> List[Company]:
        """
        Получает все компании
        
        Returns:
            Список компаний
        """
        try:
            return await self.company_repo.get_all_companies()
        except Exception as e:
            logger.error(f"Ошибка получения списка компаний: {e}")
            return []
    
    async def search_companies(self, search_term: str) -> List[Company]:
        """
        Ищет компании по названию
        
        Args:
            search_term: Поисковый запрос
            
        Returns:
            Список найденных компаний
        """
        try:
            if not search_term.strip():
                return await self.get_all_companies()
            
            return await self.company_repo.search_companies(search_term.strip())
        except Exception as e:
            logger.error(f"Ошибка поиска компаний: {e}")
            return []
    
    async def update_company(self, company_id: int, updates: dict) -> bool:
        """
        Обновляет компанию
        
        Args:
            company_id: ID компании
            updates: Обновления
            
        Returns:
            True если успешно
        """
        try:
            # Если обновляется название, проверяем уникальность
            if 'name' in updates:
                new_name = updates['name'].strip()
                existing_companies = await self.search_companies(new_name)
                for company in existing_companies:
                    if company.name.lower() == new_name.lower() and company.company_id != company_id:
                        raise ValueError(f"Компания с названием '{new_name}' уже существует")
                
                updates['name'] = new_name
            
            # Очищаем описание
            if 'description' in updates and updates['description']:
                updates['description'] = updates['description'].strip()
            
            success = await self.company_repo.update_company(company_id, updates)
            
            if success:
                logger.info(f"Обновлена компания {company_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка обновления компании {company_id}: {e}")
            return False
    
    async def deactivate_company(self, company_id: int) -> bool:
        """
        Деактивирует компанию
        
        Args:
            company_id: ID компании
            
        Returns:
            True если успешно
        """
        try:
            return await self.update_company(company_id, {'is_active': False})
        except Exception as e:
            logger.error(f"Ошибка деактивации компании {company_id}: {e}")
            return False
    
    def validate_company_name(self, name: str) -> bool:
        """
        Проверяет валидность названия компании
        
        Args:
            name: Название компании
            
        Returns:
            True если название валидно
        """
        if not name or not name.strip():
            return False
        
        name = name.strip()
        
        # Проверяем длину
        if len(name) < 2 or len(name) > 100:
            return False
        
        # Проверяем на недопустимые символы
        invalid_chars = ['<', '>', '"', "'", '&']
        if any(char in name for char in invalid_chars):
            return False
        
        return True
    
    def validate_company_description(self, description: str) -> bool:
        """
        Проверяет валидность описания компании
        
        Args:
            description: Описание компании
            
        Returns:
            True если описание валидно
        """
        if not description:
            return True  # Описание может быть пустым
        
        description = description.strip()
        
        # Проверяем длину
        if len(description) > 500:
            return False
        
        return True