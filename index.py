"""
Entry point для Yandex Cloud Function
"""
import json
import logging
import asyncio
from typing import Dict, Any

from config import config
from app.bot.bot_instance import create_bot
from app.bot.dispatcher import setup_dispatcher

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные переменные для переиспользования
bot = None
dp = None


async def init_bot():
    """Инициализация бота и диспетчера"""
    global bot, dp
    
    if bot is None:
        try:
            config.validate_required()
            bot = create_bot()
            dp = await setup_dispatcher()
            logger.info("Бот успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации бота: {e}")
            raise


async def process_telegram_update(event: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка Telegram update"""
    try:
        # Инициализируем бота если не инициализирован
        await init_bot()
        
        # Получаем update из тела запроса
        update_data = json.loads(event.get('body', '{}'))
        
        # Обрабатываем update
        from aiogram.types import Update
        update = Update(**update_data)
        
        await dp.feed_update(bot, update)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'ok'})
        }
        
    except Exception as e:
        logger.error(f"Ошибка обработки update: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Основной обработчик Cloud Function
    
    Args:
        event: Событие от API Gateway
        context: Контекст выполнения функции
        
    Returns:
        HTTP ответ для API Gateway
    """
    try:
        # Логируем входящий запрос в debug режиме
        if config.DEBUG:
            logger.debug(f"Получен запрос: {json.dumps(event, ensure_ascii=False, indent=2)}")
        
        # Проверяем метод запроса
        http_method = event.get('httpMethod', '').upper()
        
        if http_method == 'POST':
            # Обрабатываем Telegram webhook
            return asyncio.run(process_telegram_update(event))
        
        elif http_method == 'GET':
            # Health check
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'telegram-task-bot'
                })
            }
        
        else:
            # Неподдерживаемый метод
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        logger.error(f"Критическая ошибка в handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }


# Для локального тестирования
if __name__ == "__main__":
    # Тестовый запрос
    test_event = {
        'httpMethod': 'GET',
        'path': '/health',
        'headers': {},
        'body': ''
    }
    
    result = handler(test_event, None)
    print(json.dumps(result, ensure_ascii=False, indent=2))