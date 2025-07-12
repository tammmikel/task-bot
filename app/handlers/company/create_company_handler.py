"""
Обработчик создания компаний
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.company_service import CompanyService
from app.states.company_states import CompanyCreationStates
from app.keyboards.main_menu import get_companies_menu_keyboard, get_back_to_main_keyboard
from app.keyboards.common_keyboards import get_confirmation_keyboard, get_cancel_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "company:create")
async def start_company_creation(callback: CallbackQuery, state: FSMContext, current_user=None, can_create_companies=None):
    """
    Начинает процесс создания компании
    """
    try:
        if not can_create_companies:
            await callback.answer("❌ Недостаточно прав для создания компаний", show_alert=True)
            return
        
        await state.set_state(CompanyCreationStates.waiting_for_name)
        
        await callback.message.edit_text(
            "🏢 Создание новой компании\n\n"
            "📝 Введите название компании:\n\n"
            "ℹ️ Название должно быть от 2 до 100 символов",
            reply_markup=get_cancel_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка начала создания компании: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.message(CompanyCreationStates.waiting_for_name)
async def process_company_name(message: Message, state: FSMContext, current_user=None):
    """
    Обрабатывает ввод названия компании
    """
    try:
        company_name = message.text.strip()
        
        # Валидация названия
        company_service = CompanyService()
        if not company_service.validate_company_name(company_name):
            await message.answer(
                "❌ Некорректное название компании.\n\n"
                "Требования:\n"
                "• От 2 до 100 символов\n"
                "• Без специальных символов < > \" ' &\n\n"
                "Попробуйте еще раз:",
                reply_markup=get_cancel_keyboard()
            )
            return
        
        # Проверяем уникальность названия
        existing_companies = await company_service.search_companies(company_name)
        for company in existing_companies:
            if company.name.lower() == company_name.lower():
                await message.answer(
                    f"❌ Компания с названием '{company_name}' уже существует.\n\n"
                    "Введите другое название:",
                    reply_markup=get_cancel_keyboard()
                )
                return
        
        # Сохраняем название и переходим к описанию
        await state.update_data(company_name=company_name)
        await state.set_state(CompanyCreationStates.waiting_for_description)
        
        await message.answer(
            f"✅ Название: {company_name}\n\n"
            "📝 Теперь введите описание компании:\n\n"
            "ℹ️ Описание необязательно, но поможет лучше идентифицировать компанию.\n"
            "Максимум 500 символов.\n\n"
            "Для пропуска описания отправьте: -",
            reply_markup=get_cancel_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки названия компании: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=get_cancel_keyboard()
        )


@router.message(CompanyCreationStates.waiting_for_description)
async def process_company_description(message: Message, state: FSMContext, current_user=None):
    """
    Обрабатывает ввод описания компании
    """
    try:
        description = message.text.strip()
        
        # Если пользователь ввел "-", пропускаем описание
        if description == "-":
            description = None
        else:
            # Валидация описания
            company_service = CompanyService()
            if not company_service.validate_company_description(description):
                await message.answer(
                    "❌ Описание слишком длинное (максимум 500 символов).\n\n"
                    "Попробуйте еще раз или отправьте '-' для пропуска:",
                    reply_markup=get_cancel_keyboard()
                )
                return
        
        # Получаем данные из состояния
        data = await state.get_data()
        company_name = data['company_name']
        
        # Сохраняем описание и показываем подтверждение
        await state.update_data(company_description=description)
        await state.set_state(CompanyCreationStates.confirming_creation)
        
        confirmation_text = f"🏢 Подтверждение создания компании\n\n"
        confirmation_text += f"📝 Название: {company_name}\n"
        
        if description:
            confirmation_text += f"📄 Описание: {description}\n\n"
        else:
            confirmation_text += f"📄 Описание: не указано\n\n"
        
        confirmation_text += "Создать компанию?"
        
        await message.answer(
            confirmation_text,
            reply_markup=get_confirmation_keyboard("confirm_company_creation", "Создать компанию")
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки описания компании: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=get_cancel_keyboard()
        )


@router.callback_query(F.data == "confirm_company_creation")
async def confirm_company_creation(callback: CallbackQuery, state: FSMContext, current_user=None):
    """
    Подтверждает создание компании
    """
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        company_name = data['company_name']
        company_description = data.get('company_description')
        
        # Создаем компанию
        company_service = CompanyService()
        company = await company_service.create_company(
            name=company_name,
            description=company_description,
            created_by=current_user.user_id
        )
        
        # Очищаем состояние
        await state.clear()
        
        success_text = f"✅ Компания успешно создана!\n\n"
        success_text += f"🏢 Название: {company.name}\n"
        success_text += f"🆔 ID: {company.company_id}\n"
        
        if company.description:
            success_text += f"📄 Описание: {company.description}\n"
        
        success_text += f"\n👤 Создатель: {current_user.display_name}"
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_companies_menu_keyboard()
        )
        
        await callback.answer("✅ Компания создана!")
        
    except ValueError as e:
        await callback.answer(f"❌ {str(e)}", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка создания компании: {e}")
        await callback.answer("❌ Ошибка создания компании", show_alert=True)


@router.callback_query(F.data == "cancel")
async def cancel_company_creation(callback: CallbackQuery, state: FSMContext):
    """
    Отменяет создание компании
    """
    try:
        await state.clear()
        
        await callback.message.edit_text(
            "❌ Создание компании отменено.",
            reply_markup=get_companies_menu_keyboard()
        )
        
        await callback.answer("Операция отменена")
        
    except Exception as e:
        logger.error(f"Ошибка отмены создания компании: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)
