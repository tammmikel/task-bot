"""
Обработчик главного меню
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keyboards.main_menu import (
    get_main_menu_keyboard,
    get_companies_menu_keyboard,
    get_tasks_menu_keyboard,
    get_analytics_menu_keyboard
)

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("menu:"))
async def handle_menu_navigation(callback: CallbackQuery, current_user=None, user_role=None):
    """
    Обработчик навигации по меню
    
    Args:
        callback: Callback query
        current_user: Текущий пользователь
        user_role: Роль пользователя
    """
    try:
        if not current_user:
            await callback.answer("❌ Пользователь не авторизован", show_alert=True)
            return
        
        action = callback.data.split(":")[1]
        
        if action == "main":
            # Главное меню
            await callback.message.edit_text(
                f"🏠 Главное меню\n\n"
                f"Добро пожаловать, {current_user.first_name}!\n"
                f"Выберите нужное действие:",
                reply_markup=get_main_menu_keyboard(user_role)
            )
        
        elif action == "companies":
            # Меню компаний
            if user_role not in ['director', 'manager']:
                await callback.answer("❌ Недостаточно прав", show_alert=True)
                return
            
            await callback.message.edit_text(
                "🏢 Управление компаниями\n\n"
                "Выберите действие:",
                reply_markup=get_companies_menu_keyboard()
            )
        
        elif action == "tasks":
            # Меню задач
            if user_role not in ['director', 'manager']:
                await callback.answer("❌ Недостаточно прав", show_alert=True)
                return
            
            await callback.message.edit_text(
                "📋 Управление задачами\n\n"
                "Выберите действие:",
                reply_markup=get_tasks_menu_keyboard(user_role)
            )
        
        elif action == "my_tasks":
            # Мои задачи (для исполнителей)
            if user_role not in ['chief_admin', 'sysadmin']:
                await callback.answer("❌ Недостаточно прав", show_alert=True)
                return
            
            await callback.message.edit_text(
                "📋 Мои задачи\n\n"
                "Выберите действие:",
                reply_markup=get_tasks_menu_keyboard(user_role)
            )
        
        elif action == "analytics":
            # Аналитика (только для директора)
            if user_role != 'director':
                await callback.answer("❌ Недостаточно прав", show_alert=True)
                return
            
            await callback.message.edit_text(
                "📊 Аналитика и отчеты\n\n"
                "Выберите тип отчета:",
                reply_markup=get_analytics_menu_keyboard()
            )
        
        elif action == "roles":
            # Управление ролями (только для директора)
            if user_role != 'director':
                await callback.answer("❌ Недостаточно прав", show_alert=True)
                return
            
            await show_roles_menu(callback)
        
        elif action == "comments":
            # Комментарии (для исполнителей)
            if user_role not in ['chief_admin', 'sysadmin']:
                await callback.answer("❌ Недостаточно прав", show_alert=True)
                return
            
            await callback.message.edit_text(
                "📝 Работа с комментариями\n\n"
                "Здесь вы можете добавлять комментарии к задачам.",
                reply_markup=get_main_menu_keyboard(user_role)
            )
        
        elif action == "help":
            # Помощь
            await show_help_menu(callback, user_role)
        
        else:
            await callback.answer("❌ Неизвестное действие", show_alert=True)
            return
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в handle_menu_navigation: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def show_roles_menu(callback: CallbackQuery):
    """Показывает меню управления ролями"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = [
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="roles:list_users")],
        [InlineKeyboardButton(text="🎭 Назначить роль", callback_data="roles:assign")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main")]
    ]
    
    await callback.message.edit_text(
        "👥 Управление ролями\n\n"
        "Здесь вы можете управлять ролями пользователей.\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


async def show_help_menu(callback: CallbackQuery, user_role: str):
    """Показывает меню помощи"""
    help_text = get_help_text(user_role)
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_main_menu_keyboard(user_role)
    )


def get_help_text(user_role: str) -> str:
    """Возвращает текст помощи в зависимости от роли"""
    
    base_text = """ℹ️ Справка по системе

🤖 Это система управления задачами для аутсорсинговой компании.

"""
    
    if user_role == 'director':
        return base_text + """👑 Ваши возможности как Директора:

🏢 Компании:
• Создавать новые компании
• Просматривать список всех компаний

📋 Задачи:
• Создавать задачи для любой компании
• Назначать исполнителей
• Просматривать все задачи
• Возвращать задачи на доработку

📊 Аналитика:
• Просматривать общую статистику
• Отчеты по компаниям и исполнителям
• Анализ просроченных задач

👥 Управление:
• Назначать роли пользователям
• Управлять доступами"""

    elif user_role == 'manager':
        return base_text + """👔 Ваши возможности как Менеджера:

🏢 Компании:
• Создавать новые компании
• Просматривать список компаний

📋 Задачи:
• Создавать задачи
• Назначать исполнителей
• Просматривать задачи
• Возвращать задачи на доработку"""

    elif user_role == 'chief_admin':
        return base_text + """⚙️ Ваши возможности как Главного админа:

📋 Задачи:
• Просматривать назначенные вам задачи
• Изменять статус задач
• Отмечать выполнение

💬 Комментарии:
• Добавлять комментарии к задачам
• Прикреплять файлы"""

    elif user_role == 'sysadmin':
        return base_text + """🛠 Ваши возможности как Системного администратора:

📋 Задачи:
• Просматривать назначенные вам задачи
• Изменять статус задач
• Отмечать выполнение

💬 Комментарии:
• Добавлять комментарии к задачам
• Прикреплять файлы"""

    return base_text + "Обратитесь к администратору для получения дополнительной информации."
