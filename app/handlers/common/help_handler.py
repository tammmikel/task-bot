"""
Обработчик команды /help
"""
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("help"))
async def help_command(message: Message, current_user=None, user_role=None):
    """
    Обработчик команды /help
    
    Args:
        message: Сообщение от пользователя
        current_user: Текущий пользователь
        user_role: Роль пользователя
    """
    try:
        if not current_user:
            await message.answer(
                "❌ Вы не зарегистрированы в системе.\n"
                "Используйте команду /start для начала работы."
            )
            return
        
        help_text = get_help_text_for_role(user_role)
        
        await message.answer(
            help_text,
            reply_markup=get_main_menu_keyboard(user_role)
        )
        
    except Exception as e:
        logger.error(f"Ошибка в help_command: {e}")
        await message.answer(
            "❌ Произошла ошибка при получении справки."
        )


def get_help_text_for_role(user_role: str) -> str:
    """Возвращает текст справки для конкретной роли"""
    
    base_commands = """📖 Основные команды:

/start - Главное меню
/help - Эта справка

"""
    
    if user_role == 'director':
        return f"""{base_commands}👑 Команды директора:

🏢 Управление компаниями:
• Создание новых компаний
• Просмотр всех компаний

📋 Управление задачами:
• Создание задач для любых компаний
• Назначение исполнителей
• Контроль выполнения
• Возврат задач на доработку

📊 Аналитика:
• Общая статистика по задачам
• Отчеты по компаниям
• Анализ работы исполнителей
• Просроченные задачи

👥 Управление персоналом:
• Назначение ролей сотрудникам
• Управление доступами

💡 Для начала работы выберите нужный раздел в главном меню."""

    elif user_role == 'manager':
        return f"""{base_commands}👔 Команды менеджера:

🏢 Работа с компаниями:
• Создание новых компаний
• Просмотр списка компаний

📋 Управление задачами:
• Создание задач
• Назначение исполнителей
• Контроль выполнения
• Возврат задач на доработку

💡 Для начала работы выберите нужный раздел в главном меню."""

    elif user_role == 'chief_admin':
        return f"""{base_commands}⚙️ Команды главного админа:

📋 Работа с задачами:
• Просмотр назначенных задач
• Изменение статуса задач
• Отметка о выполнении
• Возврат в работу

💬 Комментарии:
• Добавление комментариев к задачам
• Прикрепление файлов и фотографий

💡 Ваши задачи отображаются в разделе "Мои задачи"."""

    elif user_role == 'sysadmin':
        return f"""{base_commands}🛠 Команды системного администратора:

📋 Работа с задачами:
• Просмотр назначенных задач
• Изменение статуса задач
• Отметка о выполнении
• Возврат в работу

💬 Комментарии:
• Добавление комментариев к задачам
• Прикрепление файлов и фотографий

💡 Ваши задачи отображаются в разделе "Мои задачи"."""

    return f"""{base_commands}❓ Для получения дополнительной информации обратитесь к администратору."""
