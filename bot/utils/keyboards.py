"""
Keyboard layouts for the bot
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import SUBSCRIPTION_PLANS, PAYMENT_NETWORKS

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 عرض الإشارات", callback_data="view_signals"),
            InlineKeyboardButton(text="📈 إحصائيات السوق", callback_data="market_stats")
        ],
        [
            InlineKeyboardButton(text="💎 الاشتراك", callback_data="subscribe"),
            InlineKeyboardButton(text="👤 حسابي", callback_data="my_account")
        ],
        [
            InlineKeyboardButton(text="ℹ️ حول المنصة", callback_data="about"),
            InlineKeyboardButton(text="📞 الدعم الفني", callback_data="contact_support")
        ],
        [InlineKeyboardButton(text="💡 معلومات الاشتراك", callback_data="subscription_info")]
    ])
    
    return keyboard

def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Get subscription plans keyboard"""
    
    keyboard_buttons = []
    
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        if plan['price'] == 0:
            button_text = f"🆓 {plan['name']} - مجاني"
        else:
            button_text = f"💎 {plan['name']} - ${plan['price']}/شهر"
        
        keyboard_buttons.append([
            InlineKeyboardButton(text=button_text, callback_data=f"plan_{plan_id}")
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def get_payment_keyboard() -> InlineKeyboardMarkup:
    """Get payment methods keyboard"""
    
    keyboard_buttons = []
    
    for network_id, network in PAYMENT_NETWORKS.items():
        button_text = f"💳 {network['name']}"
        keyboard_buttons.append([
            InlineKeyboardButton(text=button_text, callback_data=f"payment_{network_id}")
        ])
    
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_payment")],
        [InlineKeyboardButton(text="🔙 العودة للخطط", callback_data="subscribe")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def get_signals_keyboard(subscription_type: str = 'free') -> InlineKeyboardMarkup:
    """Get signals keyboard based on subscription"""
    
    keyboard_buttons = [
        [InlineKeyboardButton(text="🔄 تحديث", callback_data="spot_signals")]
    ]
    
    if subscription_type in ['pro', 'elite']:
        keyboard_buttons.append([
            InlineKeyboardButton(text="🚀 إشارات Futures", callback_data="futures_signals")
        ])
    
    if subscription_type == 'elite':
        keyboard_buttons.append([
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")
        ])
    
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="📊 إحصائيات الإشارات", callback_data="signal_stats")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def get_futures_keyboard(subscription_type: str = 'pro') -> InlineKeyboardMarkup:
    """Get futures keyboard based on subscription"""
    
    keyboard_buttons = [
        [InlineKeyboardButton(text="🔄 تحديث", callback_data="futures_signals")]
    ]
    
    if subscription_type == 'elite':
        keyboard_buttons.append([
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")
        ])
    
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="📈 إشارات Spot", callback_data="spot_signals")],
        [InlineKeyboardButton(text="📊 إحصائيات", callback_data="signal_stats")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def get_market_keyboard() -> InlineKeyboardMarkup:
    """Get market data keyboard"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="😨 مؤشر الخوف والطمع", callback_data="fear_greed"),
            InlineKeyboardButton(text="📈 الدعم والمقاومة", callback_data="support_resistance")
        ],
        [
            InlineKeyboardButton(text="📅 الأجندة الاقتصادية", callback_data="economic_calendar"),
            InlineKeyboardButton(text="💹 أسعار العملات", callback_data="crypto_prices")
        ],
        [
            InlineKeyboardButton(text="📊 تحليل السوق", callback_data="market_analysis"),
            InlineKeyboardButton(text="🔄 تحديث البيانات", callback_data="market_stats")
        ],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    return keyboard

def get_account_keyboard() -> InlineKeyboardMarkup:
    """Get account management keyboard"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💎 ترقية الاشتراك", callback_data="upgrade_subscription"),
            InlineKeyboardButton(text="🔄 تجديد الاشتراك", callback_data="renew_subscription")
        ],
        [
            InlineKeyboardButton(text="📋 سجل المدفوعات", callback_data="payment_history"),
            InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="account_settings")
        ],
        [
            InlineKeyboardButton(text="📊 إحصائياتي", callback_data="my_stats"),
            InlineKeyboardButton(text="🔔 إدارة الإشعارات", callback_data="notification_settings")
        ],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    return keyboard

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Get admin panel keyboard"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 إحصائيات النظام", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 إدارة المستخدمين", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="📢 رسالة عامة", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="💰 إدارة المدفوعات", callback_data="admin_payments")
        ],
        [
            InlineKeyboardButton(text="⚙️ إعدادات النظام", callback_data="admin_settings"),
            InlineKeyboardButton(text="📋 سجل النشاط", callback_data="admin_logs")
        ],
        [
            InlineKeyboardButton(text="🔧 أدوات الصيانة", callback_data="admin_maintenance"),
            InlineKeyboardButton(text="📈 تقارير مفصلة", callback_data="admin_reports")
        ],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    return keyboard

def get_confirmation_keyboard(confirm_data: str, cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """Get confirmation keyboard"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ نعم", callback_data=confirm_data),
            InlineKeyboardButton(text="❌ لا", callback_data=cancel_data)
        ]
    ])
    
    return keyboard

def get_pagination_keyboard(current_page: int, total_pages: int, callback_prefix: str) -> InlineKeyboardMarkup:
    """Get pagination keyboard"""
    
    keyboard_buttons = []
    
    # Navigation buttons
    nav_buttons = []
    
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ السابق", callback_data=f"{callback_prefix}_page_{current_page - 1}")
        )
    
    nav_buttons.append(
        InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page")
    )
    
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(text="➡️ التالي", callback_data=f"{callback_prefix}_page_{current_page + 1}")
        )
    
    keyboard_buttons.append(nav_buttons)
    
    # Quick jump buttons for first and last pages
    if total_pages > 3:
        jump_buttons = []
        
        if current_page > 2:
            jump_buttons.append(
                InlineKeyboardButton(text="⏮️ الأولى", callback_data=f"{callback_prefix}_page_1")
            )
        
        if current_page < total_pages - 1:
            jump_buttons.append(
                InlineKeyboardButton(text="⏭️ الأخيرة", callback_data=f"{callback_prefix}_page_{total_pages}")
            )
        
        if jump_buttons:
            keyboard_buttons.append(jump_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Get settings keyboard"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔔 إدارة الإشعارات", callback_data="notification_settings"),
            InlineKeyboardButton(text="🌐 تغيير اللغة", callback_data="language_settings")
        ],
        [
            InlineKeyboardButton(text="🔒 الخصوصية", callback_data="privacy_settings"),
            InlineKeyboardButton(text="📱 ربط الحسابات", callback_data="account_linking")
        ],
        [
            InlineKeyboardButton(text="📊 تفضيلات الإشارات", callback_data="signal_preferences"),
            InlineKeyboardButton(text="⏰ إعدادات التوقيت", callback_data="time_settings")
        ],
        [
            InlineKeyboardButton(text="🗑️ حذف الحساب", callback_data="delete_account"),
            InlineKeyboardButton(text="🔙 العودة للحساب", callback_data="my_account")
        ]
    ])
    
    return keyboard

def get_notification_settings_keyboard(notifications_enabled: bool) -> InlineKeyboardMarkup:
    """Get notification settings keyboard"""
    
    toggle_text = "🔕 إيقاف الإشعارات" if notifications_enabled else "🔔 تفعيل الإشعارات"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=toggle_text, callback_data="toggle_notifications")],
        [
            InlineKeyboardButton(text="📊 إشعارات الإشارات", callback_data="signal_notifications"),
            InlineKeyboardButton(text="💰 إشعارات المدفوعات", callback_data="payment_notifications")
        ],
        [
            InlineKeyboardButton(text="📢 الرسائل العامة", callback_data="broadcast_notifications"),
            InlineKeyboardButton(text="🔔 إشعارات النظام", callback_data="system_notifications")
        ],
        [
            InlineKeyboardButton(text="⏰ أوقات الإشعارات", callback_data="notification_times"),
            InlineKeyboardButton(text="🔙 العودة للإعدادات", callback_data="account_settings")
        ]
    ])
    
    return keyboard

def get_help_keyboard() -> InlineKeyboardMarkup:
    """Get help keyboard"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 البدء السريع", callback_data="quick_start"),
            InlineKeyboardButton(text="📊 كيفية قراءة الإشارات", callback_data="how_to_read_signals")
        ],
        [
            InlineKeyboardButton(text="💰 طرق الدفع", callback_data="payment_methods"),
            InlineKeyboardButton(text="🔧 حل المشاكل", callback_data="troubleshooting")
        ],
        [
            InlineKeyboardButton(text="❓ الأسئلة الشائعة", callback_data="faq"),
            InlineKeyboardButton(text="📞 التواصل مع الدعم", callback_data="contact_support")
        ],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    return keyboard

def get_signal_action_keyboard(signal_id: str, signal_type: str) -> InlineKeyboardMarkup:
    """Get signal action keyboard"""
    
    keyboard_buttons = [
        [InlineKeyboardButton(text="📋 تفاصيل كاملة", callback_data=f"signal_details_{signal_id}")]
    ]
    
    if signal_type == 'futures':
        keyboard_buttons.append([
            InlineKeyboardButton(text="👤 ملف المتداول", callback_data=f"trader_profile_{signal_id}")
        ])
    
    keyboard_buttons.extend([
        [
            InlineKeyboardButton(text="⭐ إضافة للمفضلة", callback_data=f"favorite_signal_{signal_id}"),
            InlineKeyboardButton(text="📤 مشاركة", callback_data=f"share_signal_{signal_id}")
        ],
        [InlineKeyboardButton(text="🔙 العودة للإشارات", callback_data="view_signals")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

