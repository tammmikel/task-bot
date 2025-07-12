"""
Обработчик регистрации пользователей
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from app.services.auth_service import AuthService
from app.keyboards.main_menu import get_main_menu_keyboard
from config import config

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("register"))
async def register_command(message: Message, current_user=None, telegram_user=None):
    """
    Обработчик команды /register
    
    Args:
        message: Сообщение от пользователя
        current_user: Текущий пользователь (из middleware)
        telegram_user: Данные Telegram пользователя (из middleware)
    """
    try:
        if current_user:
            await message.answer(
                f"ℹ️ Вы уже зарегистрированы в системе.\n\n"
                f"👤 Имя: {current_user.first_name}\n"
                f"🎭 Роль: {config.ROLES.get(current_user.role, current_user.role)}\n\n"
                f"Используйте /start для перехода в главное меню.",
                reply_markup=get_main_menu_keyboard(current_user.role)
            )
            return
        
        # Новый пользователь - начинаем регистрацию
        if not telegram_user:
            telegram_user = {
                'user_id': message.from_user.id,
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
        
        await message.answer(
            f"👋 Привет, {telegram_user['first_name']}!\n\n"
            f"🏢 Добро пожаловать в систему управления задачами.\n\n"
            f"Для регистрации выберите вашу роль в компании:",
            reply_markup=get_role_selection_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка в register_command: {e}")
        await message.answer(
            "❌ Произошла ошибка. Обратитесь к администратору."
        )


def get_role_selection_keyboard():
    """Возвращает клавиатуру для выбора роли при регистрации"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = []
    
    # Добавляем кнопки для каждой роли с описанием
    role_descriptions = {
        'director': '👑 Директор - полный доступ к системе',
        'manager': '👔 Менеджер - управление компаниями и задачами',
        'chief_admin': '⚙️ Главный админ - выполнение задач',
        'sysadmin': '🛠 Системный админ - выполнение задач'
    }
    
    for role_key, description in role_descriptions.items():
        keyboard.append([
            InlineKeyboardButton(
                text=description,
                callback_data=f"register_role:{role_key}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="❌ Отменить регистрацию", 
            callback_data="cancel_registration"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data.startswith("register_role:"))
async def handle_registration_role_selection(callback: CallbackQuery, telegram_user=None):
    """
    Обработчик выбора роли при регистрации
    
    Args:
        callback: Callback query
        telegram_user: Данные Telegram пользователя
    """
    try:
        role = callback.data.split(":")[1]
        
        if role not in config.ROLES:
            await callback.answer("❌ Неверная роль", show_alert=True)
            return
        
        # Формируем данные пользователя
        if not telegram_user:
            telegram_user = {
                'user_id': callback.from_user.id,
                'username': callback.from_user.username,
                'first_name': callback.from_user.first_name,
                'last_name': callback.from_user.last_name
            }
        
        # Регистрируем пользователя
        auth_service = AuthService()
        user = await auth_service.register_user(telegram_user, role)
        
        success_text = f"✅ Регистрация завершена успешно!\n\n"
        success_text += f"👤 Имя: {user.first_name}"
        if user.last_name:
            success_text += f" {user.last_name}"
        success_text += f"\n🎭 Роль: {config.ROLES[user.role]}\n"
        if user.username:
            success_text += f"📱 Username: @{user.username}\n"
        
        success_text += f"\n🎉 Добро пожаловать в систему!\n"
        success_text += f"Теперь вы можете пользоваться всеми доступными функциями."
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu_keyboard(user.role)
        )
        
        await callback.answer("✅ Вы успешно зарегистрированы!")
        
        # Логируем регистрацию
        logger.info(f"Новый пользователь зарегистрирован: {user.user_id} ({user.role})")
        
    except ValueError as e:
        await callback.answer(f"❌ {str(e)}", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка регистрации пользователя: {e}")
        await callback.answer("❌ Ошибка регистрации. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data == "cancel_registration")
async def cancel_registration(callback: CallbackQuery):
    """
    Отменяет процесс регистрации
    """
    try:
        await callback.message.edit_text(
            "❌ Регистрация отменена.\n\n"
            "Для начала работы с системой необходимо зарегистрироваться.\n"
            "Используйте команду /start или /register для повторной попытки."
        )
        
        await callback.answer("Регистрация отменена")
        
    except Exception as e:
        logger.error(f"Ошибка отмены регистрации: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.message(Command("whoami"))
async def whoami_command(message: Message, current_user=None, user_role=None):
    """
    Показывает информацию о текущем пользователе
    
    Args:
        message: Сообщение
        current_user: Текущий пользователь
        user_role: Роль пользователя
    """
    try:
        if not current_user:
            await message.answer(
                "❌ Вы не зарегистрированы в системе.\n"
                "Используйте /start для регистрации."
            )
            return
        
        info_text = f"👤 Информация о вашем аккаунте\n\n"
        info_text += f"🆔 ID: {current_user.user_id}\n"
        info_text += f"📝 Имя: {current_user.first_name}"
        
        if current_user.last_name:
            info_text += f" {current_user.last_name}"
        
        if current_user.username:
            info_text += f"\n📱 Username: @{current_user.username}"
        
        info_text += f"\n🎭 Роль: {config.ROLES.get(user_role, user_role)}"
        
        if current_user.phone:
            info_text += f"\n📞 Телефон: {current_user.phone}"
        
        info_text += f"\n📅 Зарегистрирован: {current_user.created_at.strftime('%d.%m.%Y в %H:%M')}"
        
        # Показываем права доступа
        info_text += f"\n\n🔐 Ваши права:\n"
        
        if user_role == 'director':
            info_text += "• Полный доступ к системе\n"
            info_text += "• Управление ролями\n"
            info_text += "• Просмотр аналитики\n"
            info_text += "• Создание компаний и задач\n"
        elif user_role == 'manager':
            info_text += "• Создание компаний\n"
            info_text += "• Создание задач\n"
            info_text += "• Управление задачами\n"
        elif user_role in ['chief_admin', 'sysadmin']:
            info_text += "• Выполнение задач\n"
            info_text += "• Комментирование задач\n"
            info_text += "• Прикрепление файлов\n"
        
        await message.answer(
            info_text,
            reply_markup=get_main_menu_keyboard(user_role)
        )
        
    except Exception as e:
        logger.error(f"Ошибка в whoami_command: {e}")
        await message.answer("❌ Произошла ошибка при получении информации.")
