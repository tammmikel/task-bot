"""
Обработчик просмотра списка компаний
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.services.company_service import CompanyService
from app.keyboards.common_keyboards import get_pagination_keyboard
from app.keyboards.main_menu import get_companies_menu_keyboard, get_back_to_main_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "company:list")
async def show_companies_list(callback: CallbackQuery, current_user=None, can_create_companies=None):
    """
    Показывает список всех компаний
    """
    try:
        if not can_create_companies:
            await callback.answer("❌ Недостаточно прав для просмотра компаний", show_alert=True)
            return
        
        await show_companies_page(callback, 0)
        
    except Exception as e:
        logger.error(f"Ошибка показа списка компаний: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("page:company_list:"))
async def handle_companies_pagination(callback: CallbackQuery):
    """
    Обрабатывает пагинацию списка компаний
    """
    try:
        page = int(callback.data.split(":")[2])
        await show_companies_page(callback, page)
        
    except Exception as e:
        logger.error(f"Ошибка пагинации компаний: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("company_details:"))
async def show_company_details(callback: CallbackQuery, current_user=None):
    """
    Показывает детали компании
    """
    try:
        company_id = int(callback.data.split(":")[1])
        
        company_service = CompanyService()
        company = await company_service.get_company_by_id(company_id)
        
        if not company:
            await callback.answer("❌ Компания не найдена", show_alert=True)
            return
        
        # Формируем текст с деталями компании
        details_text = f"🏢 Информация о компании\n\n"
        details_text += f"📝 Название: {company.name}\n"
        details_text += f"🆔 ID: {company.company_id}\n"
        
        if company.description:
            details_text += f"📄 Описание: {company.description}\n"
        else:
            details_text += f"📄 Описание: не указано\n"
        
        details_text += f"📅 Создана: {company.created_at.strftime('%d.%m.%Y в %H:%M')}\n"
        
        # Получаем информацию о создателе
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        creator = await auth_service.get_user_by_telegram_id(company.created_by)
        
        if creator:
            details_text += f"👤 Создатель: {creator.display_name}\n"
        
        # Добавляем статистику по задачам (если нужно)
        # TODO: Добавить количество задач по этой компании
        
        # Создаем клавиатуру с действиями
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Задачи компании", callback_data=f"company_tasks:{company_id}")],
            [InlineKeyboardButton(text="📝 Редактировать", callback_data=f"company_edit:{company_id}")],
            [InlineKeyboardButton(text="🔙 К списку", callback_data="company:list")]
        ]
        
        await callback.message.edit_text(
            details_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
        await callback.answer()
        
    except ValueError:
        await callback.answer("❌ Некорректный ID компании", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка показа деталей компании: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def show_companies_page(callback: CallbackQuery, page: int):
    """
    Показывает страницу со списком компаний
    
    Args:
        callback: Callback query
        page: Номер страницы
    """
    company_service = CompanyService()
    companies = await company_service.get_all_companies()
    
    if not companies:
        await callback.message.edit_text(
            "📭 Список компаний пуст\n\n"
            "Создайте первую компанию для начала работы.",
            reply_markup=get_companies_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Создаем пагинацию
    items_per_page = 8
    keyboard = get_pagination_keyboard(companies, page, items_per_page, "company_details")
    
    # Добавляем кнопку возврата в меню
    from aiogram.types import InlineKeyboardButton
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Меню компаний", callback_data="menu:companies")
    ])
    
    # Формируем заголовок
    total_companies = len(companies)
    current_page = page + 1
    total_pages = (total_companies + items_per_page - 1) // items_per_page
    
    header_text = f"🏢 Список компаний ({total_companies})\n"
    if total_pages > 1:
        header_text += f"Страница {current_page} из {total_pages}\n"
    header_text += "\nВыберите компанию для просмотра деталей:"
    
    await callback.message.edit_text(
        header_text,
        reply_markup=keyboard
    )
    
    await callback.answer()
