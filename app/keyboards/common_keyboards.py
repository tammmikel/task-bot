"""
Общие клавиатуры
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_confirmation_keyboard(confirm_callback: str, confirm_text: str = "✅ Подтвердить") -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру подтверждения действия
    
    Args:
        confirm_callback: Callback для подтверждения
        confirm_text: Текст кнопки подтверждения
        
    Returns:
        Клавиатура подтверждения
    """
    keyboard = [
        [InlineKeyboardButton(text=confirm_text, callback_data=confirm_callback)],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с кнопкой отмены
    
    Returns:
        Клавиатура с кнопкой отмены
    """
    keyboard = [
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_yes_no_keyboard(yes_callback: str, no_callback: str = "cancel") -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру Да/Нет
    
    Args:
        yes_callback: Callback для "Да"
        no_callback: Callback для "Нет"
        
    Returns:
        Клавиатура Да/Нет
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data=yes_callback),
            InlineKeyboardButton(text="❌ Нет", callback_data=no_callback)
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pagination_keyboard(items: list, page: int, items_per_page: int, callback_prefix: str) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с пагинацией
    
    Args:
        items: Список элементов
        page: Текущая страница (начиная с 0)
        items_per_page: Количество элементов на странице
        callback_prefix: Префикс для callback данных
        
    Returns:
        Клавиатуру с пагинацией
    """
    keyboard = []
    
    # Вычисляем общее количество страниц
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    
    # Добавляем элементы текущей страницы
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    
    for i in range(start_idx, end_idx):
        item = items[i]
        # Предполагаем, что у элемента есть атрибуты для отображения
        if hasattr(item, 'name'):
            text = item.name
        elif hasattr(item, 'title'):
            text = item.title
        else:
            text = str(item)
        
        # Обрезаем длинный текст
        if len(text) > 30:
            text = text[:27] + "..."
        
        # Предполагаем, что у элемента есть ID
        item_id = getattr(item, 'id', getattr(item, 'company_id', getattr(item, 'task_id', i)))
        
        keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"{callback_prefix}:{item_id}"
            )
        ])
    
    # Добавляем кнопки навигации если нужно
    if total_pages > 1:
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(text="◀️ Назад", callback_data=f"page:{callback_prefix}:{page-1}")
            )
        
        nav_buttons.append(
            InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop")
        )
        
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton(text="Вперед ▶️", callback_data=f"page:{callback_prefix}:{page+1}")
            )
        
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard(callback_data: str, text: str = "🔙 Назад") -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с кнопкой "Назад"
    
    Args:
        callback_data: Callback для кнопки "Назад"
        text: Текст кнопки
        
    Returns:
        Клавиатура с кнопкой "Назад"
    """
    keyboard = [
        [InlineKeyboardButton(text=text, callback_data=callback_data)]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
