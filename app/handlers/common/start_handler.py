"""
Обработчик команды /start
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from app.services.auth_service import AuthService
from app.keyboards.main_menu import get_main_menu_keyboard
from config import config

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_command(message: Message, current_user=None, telegram_user=None):
    """
    Обработчик команды /start
    
    Args:
        message: Сообщение от пользователя
        current_user: Текущий пользователь (из middleware)
        telegram_user: Данные Telegram пользователя (из middleware)
    """
    try:
        if current_user:
            # Пользователь уже зарегистрирован
            await message.answer(
                f"🎉 Добро пожаловать, {current_user.first_name}!\n\n"
                f"👤 Ваша роль: {config.ROLES.get(current_user.role, current_user.role)}\n\n"
                f"Выберите действие:",
                reply_markup=get_main_menu_keyboard(current_user.role)
            )
        else:
            # Новый пользователь - начинаем регистрацию
            if not telegram_user:
                await message.answer(
                    "❌ Ошибка получения данных пользователя. Попробуйте еще раз."
                )
                return
            
            # Показываем приветствие и предлагаем выбрать роль
            await message.answer(
                f"👋 Привет, {telegram_user['first_name']}!\n\n"
                f"🏢 Добро пожаловать в систему управления задачами.\n\n"
                f"Для начала работы необходимо зарегистрироваться.\n"
                f"Выберите вашу роль в компании:",
                reply_markup=get_role_selection_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Ошибка в start_command: {e}")
        await message.answer(
            "❌ Произошла ошибка. Обратитесь к администратору."
        )


def get_role_selection_keyboard():
    """Возвращает клавиатуру для выбора роли"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = []
    
    # Добавляем кнопки для каждой роли
    for role_key, role_name in config.ROLES.items():
        keyboard.append([
            InlineKeyboardButton(
                text=f"👤 {role_name}",
                callback_data=f"select_role:{role_key}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data.startswith("select_role:"))
async def handle_role_selection(callback, telegram_user=None):
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
        
        # Регистрируем пользователя
        auth_service = AuthService()
        
        if not telegram_user:
            telegram_user = {
                'user_id': callback.from_user.id,
                'username': callback.from_user.username,
                'first_name': callback.from_user.first_name,
                'last_name': callback.from_user.last_name
            }
        
        user = await auth_service.register_user(telegram_user, role)
        
        await callback.message.edit_text(
            f"✅ Регистрация завершена!\n\n"
            f"👤 Имя: {user.first_name}\n"
            f"🎭 Роль: {config.ROLES[user.role]}\n\n"
            f"Теперь вы можете пользоваться системой.",
            reply_markup=get_main_menu_keyboard(user.role)
        )
        
        await callback.answer("✅ Вы успешно зарегистрированы!")
        
    except ValueError as e:
        await callback.answer(f"❌ {str(e)}", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка регистрации пользователя: {e}")
        await callback.answer("❌ Ошибка регистрации", show_alert=True)
