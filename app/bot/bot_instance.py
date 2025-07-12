"""
Создание экземпляра Telegram бота
"""
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config


def create_bot() -> Bot:
    """
    Создает и настраивает экземпляр Telegram бота
    
    Returns:
        Bot: Настроенный экземпляр бота
    """
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True
        )
    )
    
    return bot