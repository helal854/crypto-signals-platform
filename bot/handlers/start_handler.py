"""
Start and welcome handler
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config.settings import WELCOME_MESSAGE, HELP_MESSAGE, SUBSCRIPTION_PLANS
from utils.api_client import APIClient
from utils.keyboards import get_main_menu_keyboard, get_subscription_keyboard
from utils.decorators import rate_limit

router = Router()

@router.message(CommandStart())
@rate_limit()
async def start_command(message: Message, state: FSMContext):
    """Handle /start command"""
    
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Register user in backend
    api_client = APIClient()
    user_data = {
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'language_code': message.from_user.language_code or 'ar'
    }
    
    try:
        await api_client.register_telegram_user(user_data)
    except Exception as e:
        # Log error but continue
        pass
    
    # Send welcome message
    keyboard = get_main_menu_keyboard()
    
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

@router.message(Command('help'))
@rate_limit()
async def help_command(message: Message):
    """Handle /help command"""
    
    await message.answer(
        HELP_MESSAGE,
        parse_mode='HTML'
    )

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    """Handle main menu callback"""
    
    keyboard = get_main_menu_keyboard()
    
    await callback.message.edit_text(
        WELCOME_MESSAGE,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery):
    """Handle about callback"""
    
    about_text = """
🏢 <b>حول منصة إشارات التداول</b>

🎯 <b>مهمتنا:</b>
نهدف إلى توفير أفضل إشارات التداول للعملات الرقمية من خلال تتبع أداء أفضل المتداولين في منصة Binance

📊 <b>خدماتنا:</b>
• تحليل مستمر لأداء أفضل 100 متداول في Binance
• إشارات Spot دقيقة مع نسب ربح عالية
• إشارات Futures من المتداولين المحترفين
• إحصائيات السوق المباشرة والمحدثة
• الأجندة الاقتصادية المؤثرة على الأسواق

🔒 <b>الأمان:</b>
جميع بياناتك محمية ومشفرة، ولا نطلب أي معلومات حساسة

📞 <b>الدعم:</b>
فريق دعم فني متاح 24/7 لمساعدتك
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        about_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data == "subscription_info")
async def subscription_info_callback(callback: CallbackQuery):
    """Handle subscription info callback"""
    
    info_text = """
💎 <b>خطط الاشتراك</b>

اختر الخطة التي تناسب احتياجاتك:
    """
    
    # Add subscription plans details
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        info_text += f"\n\n🔹 <b>{plan['name']}</b>"
        if plan['price'] > 0:
            info_text += f" - ${plan['price']}/شهر"
        else:
            info_text += " - مجاني"
        
        for feature in plan['features']:
            info_text += f"\n{feature}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 اشترك الآن", callback_data="subscribe")],
        [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        info_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data == "contact_support")
async def contact_support_callback(callback: CallbackQuery):
    """Handle contact support callback"""
    
    support_text = """
📞 <b>الدعم الفني</b>

🔹 <b>طرق التواصل:</b>
• البوت: أرسل رسالة هنا وسيتم الرد عليك
• البريد الإلكتروني: support@cryptosignals.com
• تليجرام: @CryptoSignalsSupport

🔹 <b>أوقات العمل:</b>
متاح 24/7 للرد على استفساراتك

🔹 <b>الأسئلة الشائعة:</b>
• كيف أشترك في الخدمة؟
• كيف أتابع الإشارات؟
• كيف أجدد اشتراكي؟
• مشاكل في الدفع؟

💬 <b>أرسل رسالتك الآن وسنرد عليك في أقرب وقت</b>
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        support_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.message(F.text)
async def handle_text_message(message: Message):
    """Handle general text messages (support requests)"""
    
    # Check if user is not using commands
    if not message.text.startswith('/'):
        # This could be a support message
        support_text = """
📨 <b>تم استلام رسالتك</b>

شكراً لتواصلك معنا! تم إرسال رسالتك إلى فريق الدعم الفني وسيتم الرد عليك في أقرب وقت ممكن.

⏰ <b>وقت الاستجابة المتوقع:</b> خلال 24 ساعة

🔔 ستصلك رسالة تأكيد عند الرد على استفسارك
        """
        
        keyboard = get_main_menu_keyboard()
        
        await message.answer(
            support_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        # TODO: Forward message to support team
        # This would be implemented with the admin notification system

