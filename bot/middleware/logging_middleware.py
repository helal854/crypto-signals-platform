"""
Logging middleware for the bot
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import logging
import time

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """Middleware to log user interactions"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        start_time = time.time()
        
        # Get user info
        user = data.get("event_from_user")
        user_id = user.id if user else "Unknown"
        
        # Log the event
        if isinstance(event, Message):
            event_type = "message"
            event_info = f"text: {event.text[:50] if event.text else 'No text'}"
        elif isinstance(event, CallbackQuery):
            event_type = "callback"
            event_info = f"data: {event.data}"
        else:
            event_type = type(event).__name__
            event_info = "Unknown event"
        
        logger.info(f"User {user_id} - {event_type}: {event_info}")
        
        try:
            # Execute handler
            result = await handler(event, data)
            
            # Log success
            execution_time = time.time() - start_time
            logger.info(f"User {user_id} - {event_type} processed successfully in {execution_time:.3f}s")
            
            return result
            
        except Exception as e:
            # Log error
            execution_time = time.time() - start_time
            logger.error(f"User {user_id} - {event_type} failed after {execution_time:.3f}s: {e}")
            raise

