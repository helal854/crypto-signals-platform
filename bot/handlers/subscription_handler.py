"""
Subscription handler for managing user subscriptions
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config.settings import SUBSCRIPTION_PLANS, PAYMENT_NETWORKS
from utils.api_client import APIClient
from utils.keyboards import get_subscription_keyboard, get_payment_keyboard
from utils.decorators import rate_limit
from utils.qr_generator import generate_payment_qr

router = Router()

class SubscriptionStates(StatesGroup):
    selecting_plan = State()
    selecting_payment = State()
    confirming_payment = State()

@router.message(Command('subscribe'))
@rate_limit()
async def subscribe_command(message: Message, state: FSMContext):
    """Handle /subscribe command"""
    
    await state.set_state(SubscriptionStates.selecting_plan)
    
    text = """
💎 <b>اختر خطة الاشتراك</b>

اختر الخطة التي تناسب احتياجاتك في التداول:
    """
    
    keyboard = get_subscription_keyboard()
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

@router.callback_query(F.data == "subscribe")
async def subscribe_callback(callback: CallbackQuery, state: FSMContext):
    """Handle subscribe callback"""
    
    await state.set_state(SubscriptionStates.selecting_plan)
    
    text = """
💎 <b>اختر خطة الاشتراك</b>

اختر الخطة التي تناسب احتياجاتك في التداول:
    """
    
    keyboard = get_subscription_keyboard()
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data.startswith("plan_"))
async def plan_selected(callback: CallbackQuery, state: FSMContext):
    """Handle plan selection"""
    
    plan_id = callback.data.split("_")[1]
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    
    if not plan:
        await callback.answer("خطة غير صحيحة", show_alert=True)
        return
    
    await state.update_data(selected_plan=plan_id)
    
    if plan['price'] == 0:
        # Free plan - activate immediately
        api_client = APIClient()
        try:
            await api_client.activate_subscription(
                user_id=callback.from_user.id,
                plan=plan_id
            )
            
            success_text = """
🎉 <b>تم تفعيل الاشتراك المجاني!</b>

✅ تم تفعيل اشتراكك المجاني بنجاح
📅 مدة الاشتراك: 30 يوم
🎯 يمكنك الآن الاستفادة من الميزات المتاحة

🔹 <b>ما يمكنك فعله الآن:</b>
• عرض إشارات Spot المحدودة
• متابعة إحصائيات السوق
• استخدام الأوامر الأساسية

💎 يمكنك الترقية لخطة مدفوعة في أي وقت للحصول على المزيد من الميزات
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 عرض الإشارات", callback_data="view_signals")],
                [InlineKeyboardButton(text="📈 إحصائيات السوق", callback_data="market_stats")],
                [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
            ])
            
            await callback.message.edit_text(
                success_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            await callback.answer("حدث خطأ في تفعيل الاشتراك", show_alert=True)
        
        await state.clear()
        await callback.answer()
        return
    
    # Paid plan - show payment options
    await state.set_state(SubscriptionStates.selecting_payment)
    
    text = f"""
💰 <b>الدفع - {plan['name']}</b>

💵 <b>المبلغ:</b> ${plan['price']}
📅 <b>المدة:</b> {plan['duration_days']} يوم

🔹 <b>الميزات المشمولة:</b>
"""
    
    for feature in plan['features']:
        text += f"\n{feature}"
    
    text += "\n\n💳 <b>اختر طريقة الدفع:</b>"
    
    keyboard = get_payment_keyboard()
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data.startswith("payment_"))
async def payment_selected(callback: CallbackQuery, state: FSMContext):
    """Handle payment method selection"""
    
    payment_method = callback.data.split("_")[1]
    network_info = PAYMENT_NETWORKS.get(payment_method)
    
    if not network_info:
        await callback.answer("طريقة دفع غير صحيحة", show_alert=True)
        return
    
    data = await state.get_data()
    plan_id = data.get('selected_plan')
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    
    await state.update_data(payment_method=payment_method)
    await state.set_state(SubscriptionStates.confirming_payment)
    
    # Generate payment address and QR code
    api_client = APIClient()
    try:
        payment_data = await api_client.create_payment_invoice(
            user_id=callback.from_user.id,
            plan=plan_id,
            payment_method=payment_method,
            amount=plan['price']
        )
        
        payment_address = payment_data['address']
        invoice_id = payment_data['invoice_id']
        
        await state.update_data(
            payment_address=payment_address,
            invoice_id=invoice_id
        )
        
        # Generate QR code
        qr_file = await generate_payment_qr(payment_address, plan['price'], network_info['symbol'])
        
        text = f"""
💳 <b>تفاصيل الدفع</b>

💰 <b>المبلغ:</b> ${plan['price']} {network_info['symbol']}
🌐 <b>الشبكة:</b> {network_info['network']}
📋 <b>العنوان:</b>

<code>{payment_address}</code>

⚠️ <b>تعليمات مهمة:</b>
• أرسل المبلغ المحدد بالضبط
• استخدم الشبكة المحددة فقط
• لا ترسل من منصة تداول مباشرة
• احفظ hash المعاملة للمتابعة

⏰ <b>انتهاء صلاحية الفاتورة:</b> 30 دقيقة

🔔 سيتم تفعيل اشتراكك تلقائياً عند تأكيد الدفع
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ تم الدفع", callback_data=f"payment_done_{invoice_id}")],
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_payment")],
            [InlineKeyboardButton(text="🔄 تحديث الحالة", callback_data=f"check_payment_{invoice_id}")]
        ])
        
        if qr_file:
            await callback.message.answer_photo(
                photo=qr_file,
                caption=text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        
    except Exception as e:
        error_text = """
❌ <b>خطأ في إنشاء الفاتورة</b>

حدث خطأ أثناء إنشاء فاتورة الدفع. يرجى المحاولة مرة أخرى أو التواصل مع الدعم الفني.
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 إعادة المحاولة", callback_data="subscribe")],
            [InlineKeyboardButton(text="📞 الدعم الفني", callback_data="contact_support")]
        ])
        
        await callback.message.edit_text(
            error_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("payment_done_"))
async def payment_done(callback: CallbackQuery, state: FSMContext):
    """Handle payment confirmation"""
    
    invoice_id = callback.data.split("_")[2]
    
    text = """
⏳ <b>جاري التحقق من الدفع...</b>

يرجى الانتظار بينما نتحقق من معاملة الدفع. قد تستغرق هذه العملية بضع دقائق.

🔔 ستصلك رسالة تأكيد فور تأكيد الدفع
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 تحديث الحالة", callback_data=f"check_payment_{invoice_id}")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    # Check payment status
    api_client = APIClient()
    try:
        payment_status = await api_client.check_payment_status(invoice_id)
        
        if payment_status['status'] == 'confirmed':
            await payment_confirmed(callback, state, invoice_id)
        elif payment_status['status'] == 'failed':
            await payment_failed(callback, state, invoice_id)
        
    except Exception as e:
        pass  # Will be checked again when user clicks refresh
    
    await callback.answer()

@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment_status(callback: CallbackQuery, state: FSMContext):
    """Check payment status"""
    
    invoice_id = callback.data.split("_")[2]
    
    api_client = APIClient()
    try:
        payment_status = await api_client.check_payment_status(invoice_id)
        
        if payment_status['status'] == 'confirmed':
            await payment_confirmed(callback, state, invoice_id)
        elif payment_status['status'] == 'failed':
            await payment_failed(callback, state, invoice_id)
        else:
            await callback.answer("لم يتم تأكيد الدفع بعد، يرجى المحاولة مرة أخرى خلال دقائق", show_alert=True)
    
    except Exception as e:
        await callback.answer("خطأ في التحقق من حالة الدفع", show_alert=True)

async def payment_confirmed(callback: CallbackQuery, state: FSMContext, invoice_id: str):
    """Handle confirmed payment"""
    
    data = await state.get_data()
    plan_id = data.get('selected_plan')
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    
    success_text = f"""
🎉 <b>تم تأكيد الدفع بنجاح!</b>

✅ تم تفعيل اشتراك {plan['name']}
📅 مدة الاشتراك: {plan['duration_days']} يوم
💰 المبلغ المدفوع: ${plan['price']}

🔹 <b>الميزات المفعلة:</b>
"""
    
    for feature in plan['features']:
        success_text += f"\n{feature}"
    
    success_text += "\n\n🚀 <b>يمكنك الآن الاستفادة من جميع الميزات!</b>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 عرض الإشارات", callback_data="view_signals")],
        [InlineKeyboardButton(text="👤 حسابي", callback_data="my_account")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        success_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await state.clear()

async def payment_failed(callback: CallbackQuery, state: FSMContext, invoice_id: str):
    """Handle failed payment"""
    
    error_text = """
❌ <b>فشل في تأكيد الدفع</b>

لم نتمكن من تأكيد دفعتك. الأسباب المحتملة:
• لم يتم إرسال المبلغ الصحيح
• تم استخدام شبكة خاطئة
• انتهت صلاحية الفاتورة

💡 <b>ماذا تفعل الآن؟</b>
• تحقق من تفاصيل المعاملة
• تواصل مع الدعم الفني إذا كنت متأكداً من الدفع
• أنشئ فاتورة جديدة
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 إنشاء فاتورة جديدة", callback_data="subscribe")],
        [InlineKeyboardButton(text="📞 الدعم الفني", callback_data="contact_support")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        error_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await state.clear()

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Cancel payment process"""
    
    text = """
❌ <b>تم إلغاء عملية الدفع</b>

يمكنك العودة للاشتراك في أي وقت تريد.

💡 الاشتراك المجاني متاح دائماً للبدء
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 الاشتراك مرة أخرى", callback_data="subscribe")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await state.clear()
    await callback.answer()

