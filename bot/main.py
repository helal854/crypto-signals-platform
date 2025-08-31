"""
Main bot application
"""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Import handlers
from handlers import (
    start_handler,
    subscription_handler,
    signals_handler,
    market_handler,
    account_handler,
    admin_handler
)

# Import middleware
from middleware.auth_middleware import AuthMiddleware
from middleware.logging_middleware import LoggingMiddleware
from middleware.throttling_middleware import ThrottlingMiddleware

# Import configuration
from config.settings import BOT_TOKEN, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot"""
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    
    # Setup middleware (order matters!)
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))
    
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Register handlers
    dp.include_router(start_handler.router)
    dp.include_router(subscription_handler.router)
    dp.include_router(signals_handler.router)
    dp.include_router(market_handler.router)
    dp.include_router(account_handler.router)
    dp.include_router(admin_handler.router)
    
    logger.info("🚀 بدء تشغيل بوت إشارات التداول...")
    
    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {e}")
        sys.exit(1)

