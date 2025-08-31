"""
Admin handler for administrative functions
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config.settings import ADMIN_USER_IDS
from utils.api_client import APIClient
from utils.decorators import rate_limit, admin_required
from utils.formatters import format_admin_stats, format_user_list

router = Router()

class AdminStates(StatesGroup):
    broadcasting = State()
    user_management = State()

@router.message(Command('admin'))
@rate_limit()
@admin_required
async def admin_command(message: Message):
    """Handle /admin command"""
    
    text = """
👑 <b>لوحة الإدارة</b>

مرحباً بك في لوحة التحكم الإدارية

🔹 <b>الوظائف المتاحة:</b>
• إحصائيات النظام
• إدارة المستخدمين
• إرسال رسائل عامة
• إدارة الاشتراكات
• مراقبة المدفوعات
    """
    
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
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

@router.callback_query(F.data == "admin_stats")
@admin_required
async def admin_stats_callback(callback: CallbackQuery):
    """Handle admin stats callback"""
    
    api_client = APIClient()
    try:
        stats = await api_client.get_admin_statistics()
        
        text = format_admin_stats(stats)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📊 تفاصيل أكثر", callback_data="detailed_stats")],
            [InlineKeyboardButton(text="🔙 لوحة الإدارة", callback_data="admin_panel")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل الإحصائيات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "admin_users")
@admin_required
async def admin_users_callback(callback: CallbackQuery):
    """Handle admin users callback"""
    
    api_client = APIClient()
    try:
        users = await api_client.get_telegram_users(limit=20)
        
        text = format_user_list(users)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 البحث عن مستخدم", callback_data="search_user"),
                InlineKeyboardButton(text="📊 إحصائيات المستخدمين", callback_data="user_stats")
            ],
            [
                InlineKeyboardButton(text="🚫 حظر مستخدم", callback_data="ban_user"),
                InlineKeyboardButton(text="✅ إلغاء حظر", callback_data="unban_user")
            ],
            [InlineKeyboardButton(text="🔙 لوحة الإدارة", callback_data="admin_panel")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل قائمة المستخدمين", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
@admin_required
async def admin_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    """Handle admin broadcast callback"""
    
    await state.set_state(AdminStates.broadcasting)
    
    text = """
📢 <b>إرسال رسالة عامة</b>

أرسل الرسالة التي تريد إرسالها لجميع المستخدمين

⚠️ <b>تنبيه:</b>
• ستصل الرسالة لجميع المستخدمين المفعلين
• تأكد من صحة المحتوى قبل الإرسال
• يمكن إلغاء العملية بإرسال /cancel

✍️ اكتب رسالتك الآن:
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_broadcast")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.message(AdminStates.broadcasting)
@admin_required
async def handle_broadcast_message(message: Message, state: FSMContext):
    """Handle broadcast message input"""
    
    broadcast_text = message.text
    
    text = f"""
📢 <b>معاينة الرسالة العامة</b>

📝 <b>الرسالة:</b>
{broadcast_text}

❓ هل تريد إرسال هذه الرسالة لجميع المستخدمين؟
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ نعم، أرسل الرسالة", callback_data="confirm_broadcast")],
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_broadcast")]
    ])
    
    await state.update_data(broadcast_message=broadcast_text)
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

@router.callback_query(F.data == "confirm_broadcast")
@admin_required
async def confirm_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    """Confirm and send broadcast message"""
    
    data = await state.get_data()
    broadcast_message = data.get('broadcast_message')
    
    if not broadcast_message:
        await callback.answer("❌ لم يتم العثور على الرسالة", show_alert=True)
        return
    
    api_client = APIClient()
    try:
        result = await api_client.send_broadcast_message(
            message=broadcast_message,
            sender_id=callback.from_user.id
        )
        
        success_text = f"""
✅ <b>تم إرسال الرسالة العامة</b>

📊 <b>إحصائيات الإرسال:</b>
• تم الإرسال لـ {result['sent_count']} مستخدم
• فشل الإرسال لـ {result['failed_count']} مستخدم
• إجمالي المستخدمين: {result['total_users']}

🕐 وقت الإرسال: {result['sent_at']}
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 تفاصيل الإرسال", callback_data="broadcast_details")],
            [InlineKeyboardButton(text="🔙 لوحة الإدارة", callback_data="admin_panel")]
        ])
        
        await callback.message.edit_text(
            success_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في إرسال الرسالة", show_alert=True)
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_broadcast")
@admin_required
async def cancel_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    """Cancel broadcast operation"""
    
    await state.clear()
    
    text = """
❌ <b>تم إلغاء الرسالة العامة</b>

يمكنك العودة لإرسال رسالة جديدة في أي وقت
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 رسالة جديدة", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔙 لوحة الإدارة", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data == "admin_payments")
@admin_required
async def admin_payments_callback(callback: CallbackQuery):
    """Handle admin payments callback"""
    
    api_client = APIClient()
    try:
        payments = await api_client.get_recent_payments(limit=10)
        
        if not payments:
            text = """
💰 <b>إدارة المدفوعات</b>

🔍 لا توجد مدفوعات حديثة

📊 يمكنك مراجعة الإحصائيات العامة للمدفوعات
            """
        else:
            text = "💰 <b>آخر المدفوعات</b>\n\n"
            
            for payment in payments:
                status_emoji = {
                    'pending': '⏳',
                    'confirmed': '✅',
                    'failed': '❌',
                    'cancelled': '🚫'
                }.get(payment['status'], '❓')
                
                text += f"{status_emoji} <b>${payment['amount']}</b> - {payment['payment_method']}\n"
                text += f"👤 المستخدم: {payment['user_id']}\n"
                text += f"📅 التاريخ: {payment['created_at'][:16]}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 إحصائيات المدفوعات", callback_data="payment_stats"),
                InlineKeyboardButton(text="🔍 البحث في المدفوعات", callback_data="search_payments")
            ],
            [
                InlineKeyboardButton(text="✅ تأكيد يدوي", callback_data="manual_confirm"),
                InlineKeyboardButton(text="❌ إلغاء دفعة", callback_data="cancel_payment_admin")
            ],
            [InlineKeyboardButton(text="🔙 لوحة الإدارة", callback_data="admin_panel")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل المدفوعات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "admin_settings")
@admin_required
async def admin_settings_callback(callback: CallbackQuery):
    """Handle admin settings callback"""
    
    api_client = APIClient()
    try:
        settings = await api_client.get_system_settings()
        
        text = f"""
⚙️ <b>إعدادات النظام</b>

🔹 <b>إعدادات عامة:</b>
• حالة النظام: {'🟢 نشط' if settings['system_active'] else '🔴 معطل'}
• التسجيل الجديد: {'🟢 مفتوح' if settings['registration_open'] else '🔴 مغلق'}
• الإشعارات: {'🟢 مفعلة' if settings['notifications_enabled'] else '🔴 معطلة'}

🔹 <b>إعدادات الاشتراكات:</b>
• الاشتراك المجاني: {'🟢 متاح' if settings['free_plan_enabled'] else '🔴 معطل'}
• حد الإشارات المجانية: {settings['free_signals_limit']} يومياً

🔹 <b>إعدادات المدفوعات:</b>
• المدفوعات: {'🟢 مفعلة' if settings['payments_enabled'] else '🔴 معطلة'}
• التحقق التلقائي: {'🟢 مفعل' if settings['auto_verification'] else '🔴 معطل'}
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 تبديل حالة النظام", callback_data="toggle_system"),
                InlineKeyboardButton(text="👥 تبديل التسجيل", callback_data="toggle_registration")
            ],
            [
                InlineKeyboardButton(text="🔔 تبديل الإشعارات", callback_data="toggle_notifications_system"),
                InlineKeyboardButton(text="💰 تبديل المدفوعات", callback_data="toggle_payments")
            ],
            [InlineKeyboardButton(text="🔙 لوحة الإدارة", callback_data="admin_panel")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل الإعدادات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "admin_logs")
@admin_required
async def admin_logs_callback(callback: CallbackQuery):
    """Handle admin logs callback"""
    
    api_client = APIClient()
    try:
        logs = await api_client.get_audit_logs(limit=10)
        
        if not logs:
            text = """
📋 <b>سجل النشاط</b>

🔍 لا توجد أنشطة مسجلة حديثاً
            """
        else:
            text = "📋 <b>آخر الأنشطة</b>\n\n"
            
            for log in logs:
                action_emoji = {
                    'login': '🔐',
                    'payment': '💰',
                    'subscription': '📝',
                    'signal': '📊',
                    'broadcast': '📢',
                    'admin': '👑'
                }.get(log['action_type'], '📝')
                
                text += f"{action_emoji} <b>{log['action']}</b>\n"
                text += f"👤 المستخدم: {log['user_id']}\n"
                text += f"📅 التوقيت: {log['created_at'][:16]}\n"
                if log.get('details'):
                    text += f"📝 التفاصيل: {log['details'][:50]}...\n"
                text += "\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 تحديث", callback_data="admin_logs"),
                InlineKeyboardButton(text="🔍 بحث متقدم", callback_data="search_logs")
            ],
            [
                InlineKeyboardButton(text="📊 إحصائيات النشاط", callback_data="activity_stats"),
                InlineKeyboardButton(text="🗑️ مسح السجلات القديمة", callback_data="clear_old_logs")
            ],
            [InlineKeyboardButton(text="🔙 لوحة الإدارة", callback_data="admin_panel")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل السجلات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "admin_panel")
@admin_required
async def admin_panel_callback(callback: CallbackQuery):
    """Return to admin panel"""
    
    text = """
👑 <b>لوحة الإدارة</b>

مرحباً بك في لوحة التحكم الإدارية

🔹 <b>الوظائف المتاحة:</b>
• إحصائيات النظام
• إدارة المستخدمين
• إرسال رسائل عامة
• إدارة الاشتراكات
• مراقبة المدفوعات
    """
    
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
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

# Helper function to check if user is admin
def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_USER_IDS

