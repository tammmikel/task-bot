"""
Главное меню бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard(user_role: str) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру главного меню в зависимости от роли пользователя
    
    Args:
        user_role: Роль пользователя
        
    Returns:
        Клавиатура главного меню
    """
    keyboard = []
    
    # Общие кнопки для всех
    
    # Кнопки для директора
    if user_role == 'director':
        keyboard.extend([
            [InlineKeyboardButton(text="🏢 Компании", callback_data="menu:companies")],
            [InlineKeyboardButton(text="📋 Задачи", callback_data="menu:tasks")],
            [InlineKeyboardButton(text="📊 Аналитика", callback_data="menu:analytics")],
            [InlineKeyboardButton(text="👥 Управление ролями", callback_data="menu:roles")]
        ])
    
    # Кнопки для менеджера
    elif user_role == 'manager':
        keyboard.extend([
            [InlineKeyboardButton(text="🏢 Компании", callback_data="menu:companies")],
            [InlineKeyboardButton(text="📋 Задачи", callback_data="menu:tasks")]
        ])
    
    # Кнопки для главного админа и сис-админов
    elif user_role in ['chief_admin', 'sysadmin']:
        keyboard.extend([
            [InlineKeyboardButton(text="📋 Мои задачи", callback_data="menu:my_tasks")],
            [InlineKeyboardButton(text="📝 Комментарии", callback_data="menu:comments")]
        ])
    
    # Общие кнопки для всех
    keyboard.append([InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu:help")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_companies_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню для работы с компаниями"""
    keyboard = [
        [InlineKeyboardButton(text="➕ Создать компанию", callback_data="company:create")],
        [InlineKeyboardButton(text="📝 Список компаний", callback_data="company:list")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_tasks_menu_keyboard(user_role: str) -> InlineKeyboardMarkup:
    """Меню для работы с задачами"""
    keyboard = []
    
    if user_role in ['director', 'manager']:
        keyboard.extend([
            [InlineKeyboardButton(text="➕ Создать задачу", callback_data="task:create")],
            [InlineKeyboardButton(text="📋 Все задачи", callback_data="task:list_all")]
        ])
    
    # Для исполнителей
    if user_role in ['chief_admin', 'sysadmin']:
        keyboard.extend([
            [InlineKeyboardButton(text="📋 Мои задачи", callback_data="task:list_my")],
            [InlineKeyboardButton(text="⏳ Активные задачи", callback_data="task:list_active")]
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_analytics_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню аналитики (только для директора)"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Общая статистика", callback_data="analytics:general")],
        [InlineKeyboardButton(text="🏢 По компаниям", callback_data="analytics:companies")],
        [InlineKeyboardButton(text="👥 По исполнителям", callback_data="analytics:executors")],
        [InlineKeyboardButton(text="⏰ Просроченные", callback_data="analytics:overdue")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main")]
    ])
