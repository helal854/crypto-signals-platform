"""
Throttling middleware for rate limiting
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import time
import asyncio

class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to handle rate limiting"""
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.user_last_call = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Get user
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)
        
        user_id = user.id
        current_time = time.time()
        
        # Check if user is rate limited
        if user_id in self.user_last_call:
            time_passed = current_time - self.user_last_call[user_id]
            
            if time_passed < self.rate_limit:
                # Rate limited
                if isinstance(event, Message):
                    await event.answer(
                        "⚠️ يرجى الانتظار قليلاً قبل إرسال رسالة أخرى",
                        parse_mode='HTML'
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "⚠️ يرجى الانتظار قليلاً",
                        show_alert=True
                    )
                return
        
        # Update last call time
        self.user_last_call[user_id] = current_time
        
        # Clean old entries (older than 1 hour)
        cutoff_time = current_time - 3600
        self.user_last_call = {
            uid: last_time for uid, last_time in self.user_last_call.items()
            if last_time > cutoff_time
        }
        
        # Continue with handler
        return await handler(event, data)

