"""
Authentication middleware for the bot
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
import logging

from utils.api_client import APIClient

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    """Middleware to handle user authentication and registration"""
    
    def __init__(self):
        self.api_client = APIClient()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Get user from event
        user: User = data.get("event_from_user")
        
        if user and not user.is_bot:
            try:
                # Try to get user from database
                user_data = await self.api_client.get_telegram_user(user.id)
                
                # Update user data in context
                data["user_data"] = user_data
                data["subscription_type"] = user_data.get("subscription_type", "free")
                
            except Exception as e:
                # User not found, register new user
                try:
                    user_data = {
                        "user_id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "language_code": user.language_code or "ar",
                        "subscription_type": "free",
                        "notifications_enabled": True
                    }
                    
                    # Register new user
                    registered_user = await self.api_client.register_telegram_user(user_data)
                    
                    # Update context
                    data["user_data"] = registered_user
                    data["subscription_type"] = "free"
                    data["is_new_user"] = True
                    
                    logger.info(f"New user registered: {user.id}")
                    
                except Exception as reg_error:
                    logger.error(f"Failed to register user {user.id}: {reg_error}")
                    # Set minimal data for error handling
                    data["user_data"] = {"user_id": user.id, "subscription_type": "free"}
                    data["subscription_type"] = "free"
        
        # Continue with the handler
        return await handler(event, data)

