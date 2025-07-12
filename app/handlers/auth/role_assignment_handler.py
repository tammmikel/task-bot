"""
Обработчик назначения ролей (только для директора)
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.auth_service import AuthService
from app.keyboards.common_keyboards import get_pagination_keyboard, get_confirmation_keyboard, get_cancel_keyboard
from app.keyboards.main_menu import get_main_menu_keyboard
from config import config

logger = logging.getLogger(__name__)
router = Router()


class RoleAssignmentStates(StatesGroup):
    """Состояния для назначения ролей"""
    selecting_user = State()
    selecting_role = State()
    confirming_assignment = State()


@router.callback_query(F.data == "roles:list_users")
async def show_users_list(callback: CallbackQuery, current_user=None, user_role=None):
    """
    Показывает список всех пользователей (только для директора)
    """
    try:
        if user_role != 'director':
            await callback.answer("❌ Недостаточно прав", show_alert=True)
            return
        
        auth_service = AuthService()
        users = await auth_service.get_all_users()
        
        if not users:
            await callback.message.edit_text(
                "👥 Список пользователей пуст\n\n"
                "Пока что в системе нет других пользователей.",
                reply_markup=get_main_menu_keyboard(user_role)
            )
            await callback.answer()
            return
        
        # Сортируем пользователей по ролям
        users_by_role = {}
        for user in users:
            if user.role not in users_by_role:
                users_by_role[user.role] = []
            users_by_role[user.role].append(user)
        
        # Формируем текст со списком пользователей
        users_text = "👥 Список пользователей системы\n\n"
        
        for role, role_users in users_by_role.items():
            role_name = config.ROLES.get(role, role)
            users_text += f"🎭 {role_name} ({len(role_users)}):\n"
            
            for user in role_users:
                users_text += f"• {user.display_name}"
                if user.user_id == current_user.user_id:
                    users_text += " (вы)"
                users_text += "\n"
            
            users_text += "\n"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = [
            [InlineKeyboardButton(text="🎭 Назначить роль", callback_data="roles:assign")],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main")]
        ]
        
        await callback.message.edit_text(
            users_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка показа списка пользователей: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "roles:assign")
async def start_role_assignment(callback: CallbackQuery, state: FSMContext, current_user=None, user_role=None):
    """
    Начинает процесс назначения роли
    """
    try:
        if user_role != 'director':
            await callback.answer("❌ Недостаточно прав", show_alert=True)
            return
        
        auth_service = AuthService()
        users = await auth_service.get_all_users()
        
        # Исключаем самого директора из списка
        other_users = [user for user in users if user.user_id != current_user.user_id]
        
        if not other_users:
            await callback.message.edit_text(
                "👥 Нет пользователей для назначения ролей\n\n"
                "В системе пока что нет других пользователей.",
                reply_markup=get_main_menu_keyboard(user_role)
            )
            await callback.answer()
            return
        
        await state.set_state(RoleAssignmentStates.selecting_user)
        await state.update_data(users=other_users)
        
        await show_users_for_role_assignment(callback, other_users, 0)
        
    except Exception as e:
        logger.error(f"Ошибка начала назначения роли: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("assign_role_user:"))
async def select_user_for_role_assignment(callback: CallbackQuery, state: FSMContext):
    """
    Выбирает пользователя для назначения роли
    """
    try:
        user_id = int(callback.data.split(":")[1])
        
        # Получаем информацию о пользователе
        auth_service = AuthService()
        selected_user = await auth_service.get_user_by_telegram_id(user_id)
        
        if not selected_user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        await state.update_data(selected_user=selected_user)
        await state.set_state(RoleAssignmentStates.selecting_role)
        
        # Показываем выбор роли
        current_role_name = config.ROLES.get(selected_user.role, selected_user.role)
        
        text = f"👤 Выбран пользователь: {selected_user.display_name}\n"
        text += f"🎭 Текущая роль: {current_role_name}\n\n"
        text += "Выберите новую роль:"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_role_selection_keyboard_for_assignment(selected_user.role)
        )
        
        await callback.answer()
        
    except ValueError:
        await callback.answer("❌ Некорректный ID пользователя", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка выбора пользователя для назначения роли: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("assign_new_role:"))
async def select_new_role(callback: CallbackQuery, state: FSMContext):
    """
    Выбирает новую роль для пользователя
    """
    try:
        new_role = callback.data.split(":")[1]
        
        if new_role not in config.ROLES:
            await callback.answer("❌ Неверная роль", show_alert=True)
            return
        
        data = await state.get_data()
        selected_user = data['selected_user']
        
        # Проверяем, не пытается ли назначить ту же роль
        if selected_user.role == new_role:
            await callback.answer("❌ Пользователь уже имеет эту роль", show_alert=True)
            return
        
        await state.update_data(new_role=new_role)
        await state.set_state(RoleAssignmentStates.confirming_assignment)
        
        # Показываем подтверждение
        old_role_name = config.ROLES.get(selected_user.role, selected_user.role)
        new_role_name = config.ROLES.get(new_role, new_role)
        
        confirmation_text = f"🎭 Подтверждение назначения роли\n\n"
        confirmation_text += f"👤 Пользователь: {selected_user.display_name}\n"
        confirmation_text += f"📝 Текущая роль: {old_role_name}\n"
        confirmation_text += f"🆕 Новая роль: {new_role_name}\n\n"
        confirmation_text += "Подтвердить назначение роли?"
        
        await callback.message.edit_text(
            confirmation_text,
            reply_markup=get_confirmation_keyboard("confirm_role_assignment", "✅ Назначить роль")
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка выбора новой роли: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "confirm_role_assignment")
async def confirm_role_assignment(callback: CallbackQuery, state: FSMContext, current_user=None):
    """
    Подтверждает назначение роли
    """
    try:
        data = await state.get_data()
        selected_user = data['selected_user']
        new_role = data['new_role']
        
        # Назначаем роль
        auth_service = AuthService()
        success = await auth_service.assign_role(
            user_id=selected_user.user_id,
            new_role=new_role,
            assigner_id=current_user.user_id
        )
        
        await state.clear()
        
        if success:
            old_role_name = config.ROLES.get(selected_user.role, selected_user.role)
            new_role_name = config.ROLES.get(new_role, new_role)
            
            success_text = f"✅ Роль успешно назначена!\n\n"
            success_text += f"👤 Пользователь: {selected_user.display_name}\n"
            success_text += f"🎭 Новая роль: {new_role_name}\n"
            success_text += f"📝 Предыдущая роль: {old_role_name}\n\n"
            success_text += f"Пользователь уведомлен об изменении роли."
            
            await callback.message.edit_text(
                success_text,
                reply_markup=get_main_menu_keyboard(current_user.role)
            )
            
            await callback.answer("✅ Роль назначена!")
            
            # TODO: Отправить уведомление пользователю об изменении роли
            
        else:
            await callback.answer("❌ Ошибка назначения роли", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка подтверждения назначения роли: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def show_users_for_role_assignment(callback: CallbackQuery, users: list, page: int = 0):
    """Показывает список пользователей для назначения роли"""
    items_per_page = 5
    keyboard = get_pagination_keyboard(users, page, items_per_page, "assign_role_user")
    
    # Заменяем callback для пользователей
    for row in keyboard.inline_keyboard[:-1]:  # Исключаем последнюю строку с навигацией
        for button in row:
            if button.callback_data.startswith("assign_role_user:"):
                user_id = int(button.callback_data.split(":")[1])
                user = next((u for u in users if u.user_id == user_id), None)
                if user:
                    role_name = config.ROLES.get(user.role, user.role)
                    button.text = f"{user.display_name} ({role_name})"
    
    # Добавляем кнопку отмены
    from aiogram.types import InlineKeyboardButton
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
    ])
    
    total_users = len(users)
    current_page = page + 1
    total_pages = (total_users + items_per_page - 1) // items_per_page
    
    header_text = f"👥 Выберите пользователя для назначения роли\n"
    if total_pages > 1:
        header_text += f"Страница {current_page} из {total_pages}\n"
    header_text += f"\nВсего пользователей: {total_users}"
    
    await callback.message.edit_text(header_text, reply_markup=keyboard)
    await callback.answer()


def get_role_selection_keyboard_for_assignment(current_role: str):
    """Возвращает клавиатуру для выбора новой роли"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = []
    
    for role_key, role_name in config.ROLES.items():
        if role_key != current_role:  # Исключаем текущую роль
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🎭 {role_name}",
                    callback_data=f"assign_new_role:{role_key}"
                )
            ])
    
    keyboard.append([
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data == "cancel")
async def cancel_role_assignment(callback: CallbackQuery, state: FSMContext, user_role=None):
    """Отменяет назначение роли"""
    try:
        await state.clear()
        
        await callback.message.edit_text(
            "❌ Назначение роли отменено.",
            reply_markup=get_main_menu_keyboard(user_role)
        )
        
        await callback.answer("Операция отменена")
        
    except Exception as e:
        logger.error(f"Ошибка отмены назначения роли: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)
