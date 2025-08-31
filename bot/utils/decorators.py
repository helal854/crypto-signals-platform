"""
Decorators for bot handlers
"""

import asyncio
import time
from functools import wraps
from typing import Dict, Set
from aiogram.types import Message, CallbackQuery

from config.settings import ADMIN_USER_IDS, RATE_LIMIT_MESSAGES, RATE_LIMIT_WINDOW
from utils.api_client import APIClient

# Rate limiting storage
user_message_counts: Dict[int, list] = {}
user_last_message: Dict[int, float] = {}

def rate_limit(max_messages: int = RATE_LIMIT_MESSAGES, window: int = RATE_LIMIT_WINDOW):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(event, *args, **kwargs):
            user_id = event.from_user.id
            current_time = time.time()
            
            # Initialize user data if not exists
            if user_id not in user_message_counts:
                user_message_counts[user_id] = []
            
            # Clean old messages outside the window
            user_message_counts[user_id] = [
                msg_time for msg_time in user_message_counts[user_id]
                if current_time - msg_time < window
            ]
            
            # Check rate limit
            if len(user_message_counts[user_id]) >= max_messages:
                # Rate limited
                if isinstance(event, Message):
                    await event.answer(
                        "⚠️ <b>تم تجاوز الحد المسموح</b>\n\n"
                        f"يمكنك إرسال {max_messages} رسائل كل {window} ثانية فقط.\n"
                        "يرجى الانتظار قليلاً قبل المحاولة مرة أخرى.",
                        parse_mode='HTML'
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        f"تم تجاوز الحد المسموح. انتظر {window} ثانية.",
                        show_alert=True
                    )
                return
            
            # Add current message to count
            user_message_counts[user_id].append(current_time)
            user_last_message[user_id] = current_time
            
            # Execute the original function
            return await func(event, *args, **kwargs)
        
        return wrapper
    return decorator

def admin_required(func):
    """Admin access required decorator"""
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        user_id = event.from_user.id
        
        if user_id not in ADMIN_USER_IDS:
            if isinstance(event, Message):
                await event.answer(
                    "❌ <b>غير مصرح لك بالوصول</b>\n\n"
                    "هذا الأمر متاح للمديرين فقط.",
                    parse_mode='HTML'
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "❌ غير مصرح لك بالوصول لهذه الوظيفة",
                    show_alert=True
                )
            return
        
        return await func(event, *args, **kwargs)
    
    return wrapper

def subscription_required(allowed_plans: list):
    """Subscription required decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(event, *args, **kwargs):
            user_id = event.from_user.id
            
            try:
                api_client = APIClient()
                user_data = await api_client.get_telegram_user(user_id)
                subscription_type = user_data.get('subscription_type', 'free')
                
                if subscription_type not in allowed_plans:
                    # Get plan names for display
                    plan_names = {
                        'free': 'المجاني',
                        'pro': 'الاحترافي',
                        'elite': 'النخبة'
                    }
                    
                    required_plans_text = ' أو '.join([plan_names.get(plan, plan) for plan in allowed_plans])
                    
                    if isinstance(event, Message):
                        await event.answer(
                            f"💎 <b>اشتراك مطلوب</b>\n\n"
                            f"هذه الميزة متاحة لأصحاب الاشتراك {required_plans_text} فقط.\n\n"
                            "يمكنك الترقية باستخدام /subscribe",
                            parse_mode='HTML'
                        )
                    elif isinstance(event, CallbackQuery):
                        await event.answer(
                            f"💎 اشتراك {required_plans_text} مطلوب لهذه الميزة",
                            show_alert=True
                        )
                    return
                
                return await func(event, *args, **kwargs)
                
            except Exception as e:
                if isinstance(event, Message):
                    await event.answer(
                        "❌ حدث خطأ في التحقق من الاشتراك، يرجى المحاولة مرة أخرى",
                        parse_mode='HTML'
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "❌ حدث خطأ في التحقق من الاشتراك",
                        show_alert=True
                    )
                return
        
        return wrapper
    return decorator

def log_user_action(action: str, details: str = None):
    """Log user action decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(event, *args, **kwargs):
            user_id = event.from_user.id
            
            # Execute the original function first
            result = await func(event, *args, **kwargs)
            
            # Log the action (fire and forget)
            asyncio.create_task(
                log_action_async(user_id, action, details)
            )
            
            return result
        
        return wrapper
    return decorator

async def log_action_async(user_id: int, action: str, details: str = None):
    """Async function to log user action"""
    try:
        api_client = APIClient()
        log_data = {
            'user_id': user_id,
            'action': action,
            'details': details,
            'action_type': 'user'
        }
        await api_client._make_request('POST', '/admin/logs', json=log_data)
    except Exception:
        # Ignore logging errors to not affect main functionality
        pass

def typing_action(func):
    """Show typing action decorator"""
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        if isinstance(event, Message):
            # Send typing action
            await event.bot.send_chat_action(
                chat_id=event.chat.id,
                action="typing"
            )
        
        return await func(event, *args, **kwargs)
    
    return wrapper

def error_handler(func):
    """Error handling decorator"""
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        try:
            return await func(event, *args, **kwargs)
        except Exception as e:
            # Log error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in {func.__name__}: {e}")
            
            # Send error message to user
            error_text = (
                "❌ <b>حدث خطأ غير متوقع</b>\n\n"
                "يرجى المحاولة مرة أخرى أو التواصل مع الدعم الفني إذا استمرت المشكلة."
            )
            
            if isinstance(event, Message):
                await event.answer(error_text, parse_mode='HTML')
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ حدث خطأ غير متوقع", show_alert=True)
    
    return wrapper

def maintenance_mode(func):
    """Maintenance mode decorator"""
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        # Check if system is in maintenance mode
        try:
            api_client = APIClient()
            settings = await api_client.get_system_settings()
            
            if not settings.get('system_active', True):
                maintenance_text = (
                    "🔧 <b>النظام تحت الصيانة</b>\n\n"
                    "نعتذر، النظام غير متاح حالياً بسبب أعمال الصيانة.\n"
                    "يرجى المحاولة مرة أخرى لاحقاً.\n\n"
                    "شكراً لتفهمكم."
                )
                
                if isinstance(event, Message):
                    await event.answer(maintenance_text, parse_mode='HTML')
                elif isinstance(event, CallbackQuery):
                    await event.answer("🔧 النظام تحت الصيانة", show_alert=True)
                return
        except Exception:
            # If can't check maintenance mode, allow access
            pass
        
        return await func(event, *args, **kwargs)
    
    return wrapper

