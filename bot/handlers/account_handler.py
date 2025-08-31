"""
Account management handler
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime, timedelta

from utils.api_client import APIClient
from utils.decorators import rate_limit
from utils.formatters import format_subscription_info, format_payment_history
from config.settings import SUBSCRIPTION_PLANS

router = Router()

@router.message(Command('myaccount'))
@rate_limit()
async def my_account_command(message: Message):
    """Handle /myaccount command"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(message.from_user.id)
        
        text = format_subscription_info(user_data)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💎 ترقية الاشتراك", callback_data="upgrade_subscription"),
                InlineKeyboardButton(text="🔄 تجديد الاشتراك", callback_data="renew_subscription")
            ],
            [
                InlineKeyboardButton(text="📋 سجل المدفوعات", callback_data="payment_history"),
                InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="account_settings")
            ],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await message.answer(
            "❌ حدث خطأ في تحميل بيانات الحساب، يرجى المحاولة مرة أخرى",
            parse_mode='HTML'
        )

@router.callback_query(F.data == "my_account")
async def my_account_callback(callback: CallbackQuery):
    """Handle my account callback"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(callback.from_user.id)
        
        text = format_subscription_info(user_data)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💎 ترقية الاشتراك", callback_data="upgrade_subscription"),
                InlineKeyboardButton(text="🔄 تجديد الاشتراك", callback_data="renew_subscription")
            ],
            [
                InlineKeyboardButton(text="📋 سجل المدفوعات", callback_data="payment_history"),
                InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="account_settings")
            ],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل بيانات الحساب", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "upgrade_subscription")
async def upgrade_subscription_callback(callback: CallbackQuery):
    """Handle upgrade subscription callback"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(callback.from_user.id)
        current_plan = user_data.get('subscription_type', 'free')
        
        text = f"""
💎 <b>ترقية الاشتراك</b>

📋 <b>خطتك الحالية:</b> {SUBSCRIPTION_PLANS[current_plan]['name']}

🔹 <b>الخطط المتاحة للترقية:</b>
        """
        
        keyboard_buttons = []
        
        if current_plan == 'free':
            text += f"\n\n🔸 <b>احترافي</b> - ${SUBSCRIPTION_PLANS['pro']['price']}/شهر"
            text += "\n• إشارات Spot غير محدودة"
            text += "\n• إشارات Futures محدودة"
            text += "\n• إحصائيات متقدمة"
            
            text += f"\n\n🔸 <b>نخبة</b> - ${SUBSCRIPTION_PLANS['elite']['price']}/شهر"
            text += "\n• جميع الميزات"
            text += "\n• Futures Leaderboard"
            text += "\n• دعم فني مخصص"
            
            keyboard_buttons = [
                [InlineKeyboardButton(text="🔸 احترافي", callback_data="upgrade_to_pro")],
                [InlineKeyboardButton(text="🔸 نخبة", callback_data="upgrade_to_elite")]
            ]
            
        elif current_plan == 'pro':
            text += f"\n\n🔸 <b>نخبة</b> - ${SUBSCRIPTION_PLANS['elite']['price']}/شهر"
            text += "\n• جميع إشارات Futures"
            text += "\n• Futures Leaderboard كامل"
            text += "\n• دعم فني مخصص"
            text += "\n• تحليلات حصرية"
            
            keyboard_buttons = [
                [InlineKeyboardButton(text="🔸 ترقية للنخبة", callback_data="upgrade_to_elite")]
            ]
            
        else:  # elite
            text = """
👑 <b>أنت مشترك في أعلى خطة!</b>

🎉 تتمتع بجميع الميزات المتاحة في المنصة

💎 شكراً لك على ثقتك بنا
            """
            keyboard_buttons = []
        
        keyboard_buttons.append([InlineKeyboardButton(text="🔙 العودة للحساب", callback_data="my_account")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل خيارات الترقية", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data.startswith("upgrade_to_"))
async def upgrade_to_plan_callback(callback: CallbackQuery):
    """Handle upgrade to specific plan"""
    
    plan = callback.data.split("_")[2]  # pro or elite
    
    # Redirect to subscription flow
    from handlers.subscription_handler import plan_selected
    
    # Simulate plan selection
    callback.data = f"plan_{plan}"
    await plan_selected(callback, None)

@router.callback_query(F.data == "renew_subscription")
async def renew_subscription_callback(callback: CallbackQuery):
    """Handle renew subscription callback"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(callback.from_user.id)
        current_plan = user_data.get('subscription_type', 'free')
        expires_at = user_data.get('subscription_expires_at')
        
        if current_plan == 'free':
            text = """
💡 <b>الاشتراك المجاني</b>

الاشتراك المجاني لا يحتاج لتجديد، يتم تجديده تلقائياً كل شهر.

💎 يمكنك الترقية لخطة مدفوعة للحصول على المزيد من الميزات
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💎 ترقية الاشتراك", callback_data="upgrade_subscription")],
                [InlineKeyboardButton(text="🔙 العودة للحساب", callback_data="my_account")]
            ])
            
        else:
            plan_info = SUBSCRIPTION_PLANS[current_plan]
            
            if expires_at:
                expires_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                days_left = (expires_date - datetime.now()).days
                
                if days_left > 7:
                    text = f"""
🔄 <b>تجديد الاشتراك</b>

📋 <b>خطتك الحالية:</b> {plan_info['name']}
📅 <b>تنتهي في:</b> {days_left} يوم
💰 <b>سعر التجديد:</b> ${plan_info['price']}

💡 يمكنك التجديد الآن أو انتظار قرب انتهاء الاشتراك
                    """
                else:
                    text = f"""
⚠️ <b>اشتراكك ينتهي قريباً!</b>

📋 <b>خطتك الحالية:</b> {plan_info['name']}
📅 <b>تنتهي في:</b> {days_left} يوم
💰 <b>سعر التجديد:</b> ${plan_info['price']}

🚨 جدد اشتراكك الآن لتجنب انقطاع الخدمة
                    """
            else:
                text = f"""
🔄 <b>تجديد الاشتراك</b>

📋 <b>خطتك الحالية:</b> {plan_info['name']}
💰 <b>سعر التجديد:</b> ${plan_info['price']}
                """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 تجديد الآن", callback_data=f"plan_{current_plan}")],
                [InlineKeyboardButton(text="💎 ترقية بدلاً من التجديد", callback_data="upgrade_subscription")],
                [InlineKeyboardButton(text="🔙 العودة للحساب", callback_data="my_account")]
            ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل معلومات التجديد", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "payment_history")
async def payment_history_callback(callback: CallbackQuery):
    """Handle payment history callback"""
    
    api_client = APIClient()
    try:
        payments = await api_client.get_user_payments(callback.from_user.id)
        
        if not payments:
            text = """
📋 <b>سجل المدفوعات</b>

🔍 لا توجد مدفوعات مسجلة

💡 ستظهر هنا جميع مدفوعاتك عند إجراء أول عملية دفع
            """
        else:
            text = format_payment_history(payments)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="payment_history")],
            [InlineKeyboardButton(text="🔙 العودة للحساب", callback_data="my_account")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل سجل المدفوعات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "account_settings")
async def account_settings_callback(callback: CallbackQuery):
    """Handle account settings callback"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(callback.from_user.id)
        
        notifications_enabled = user_data.get('notifications_enabled', True)
        language = user_data.get('language_code', 'ar')
        
        text = f"""
⚙️ <b>إعدادات الحساب</b>

👤 <b>معلومات الحساب:</b>
• الاسم: {user_data.get('first_name', 'غير محدد')}
• اسم المستخدم: @{user_data.get('username', 'غير محدد')}
• تاريخ التسجيل: {user_data.get('created_at', 'غير محدد')[:10]}

🔔 <b>الإشعارات:</b> {'مفعلة' if notifications_enabled else 'معطلة'}
🌐 <b>اللغة:</b> العربية

💡 يمكنك تعديل هذه الإعدادات حسب تفضيلاتك
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔕 إيقاف الإشعارات" if notifications_enabled else "🔔 تفعيل الإشعارات",
                    callback_data="toggle_notifications"
                )
            ],
            [InlineKeyboardButton(text="🗑️ حذف الحساب", callback_data="delete_account")],
            [InlineKeyboardButton(text="🔙 العودة للحساب", callback_data="my_account")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل الإعدادات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "toggle_notifications")
async def toggle_notifications_callback(callback: CallbackQuery):
    """Handle toggle notifications callback"""
    
    api_client = APIClient()
    try:
        result = await api_client.toggle_user_notifications(callback.from_user.id)
        
        if result['notifications_enabled']:
            await callback.answer("🔔 تم تفعيل الإشعارات", show_alert=True)
        else:
            await callback.answer("🔕 تم إيقاف الإشعارات", show_alert=True)
        
        # Refresh settings page
        await account_settings_callback(callback)
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحديث الإعدادات", show_alert=True)

@router.callback_query(F.data == "delete_account")
async def delete_account_callback(callback: CallbackQuery):
    """Handle delete account callback"""
    
    text = """
⚠️ <b>حذف الحساب</b>

🚨 <b>تحذير:</b> هذا الإجراء لا يمكن التراجع عنه!

عند حذف حسابك سيتم:
• حذف جميع بياناتك الشخصية
• إلغاء اشتراكك الحالي
• حذف سجل المدفوعات
• منعك من استخدام البوت

💡 <b>بدائل أخرى:</b>
• إيقاف الإشعارات مؤقتاً
• إلغاء الاشتراك المدفوع والعودة للمجاني

❓ هل أنت متأكد من رغبتك في حذف الحساب؟
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ نعم، احذف حسابي", callback_data="confirm_delete_account")],
        [InlineKeyboardButton(text="🔙 لا، العودة للإعدادات", callback_data="account_settings")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data == "confirm_delete_account")
async def confirm_delete_account_callback(callback: CallbackQuery):
    """Handle confirm delete account callback"""
    
    api_client = APIClient()
    try:
        await api_client.delete_telegram_user(callback.from_user.id)
        
        text = """
✅ <b>تم حذف الحساب</b>

تم حذف حسابك وجميع بياناتك بنجاح.

شكراً لاستخدامك خدماتنا. يمكنك إنشاء حساب جديد في أي وقت بإرسال /start

🙏 نتمنى لك التوفيق في رحلتك الاستثمارية
        """
        
        await callback.message.edit_text(
            text,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في حذف الحساب", show_alert=True)
    
    await callback.answer()

