"""
Состояния для работы с компаниями
"""
from aiogram.fsm.state import State, StatesGroup


class CompanyCreationStates(StatesGroup):
    """Состояния для создания компании"""
    
    waiting_for_name = State()
    waiting_for_description = State()
    confirming_creation = State()


class CompanyEditStates(StatesGroup):
    """Состояния для редактирования компании"""
    
    selecting_company = State()
    selecting_field = State()
    waiting_for_new_name = State()
    waiting_for_new_description = State()
    confirming_changes = State()
