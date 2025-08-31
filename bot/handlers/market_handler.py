"""
Market data and statistics handler
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime

from utils.api_client import APIClient
from utils.decorators import rate_limit
from utils.formatters import format_market_data, format_fear_greed, format_economic_calendar

router = Router()

@router.message(Command('market'))
@rate_limit()
async def market_command(message: Message):
    """Handle /market command"""
    
    text = """
📊 <b>إحصائيات السوق</b>

اختر نوع البيانات التي تريد عرضها:
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="😨 مؤشر الخوف والطمع", callback_data="fear_greed"),
            InlineKeyboardButton(text="📈 الدعم والمقاومة", callback_data="support_resistance")
        ],
        [
            InlineKeyboardButton(text="📅 الأجندة الاقتصادية", callback_data="economic_calendar"),
            InlineKeyboardButton(text="💹 أسعار العملات", callback_data="crypto_prices")
        ],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

@router.message(Command('feargreed'))
@rate_limit()
async def fear_greed_command(message: Message):
    """Handle /feargreed command"""
    
    api_client = APIClient()
    try:
        fear_greed_data = await api_client.get_fear_greed_index()
        
        text = format_fear_greed(fear_greed_data)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="fear_greed")],
            [InlineKeyboardButton(text="📊 المزيد من الإحصائيات", callback_data="market_stats")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await message.answer(
            "❌ حدث خطأ في تحميل مؤشر الخوف والطمع، يرجى المحاولة مرة أخرى",
            parse_mode='HTML'
        )

@router.message(Command('schedule'))
@rate_limit()
async def schedule_command(message: Message):
    """Handle /schedule command"""
    
    api_client = APIClient()
    try:
        calendar_data = await api_client.get_economic_calendar()
        
        text = format_economic_calendar(calendar_data)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="economic_calendar")],
            [InlineKeyboardButton(text="📊 إحصائيات السوق", callback_data="market_stats")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await message.answer(
            "❌ حدث خطأ في تحميل الأجندة الاقتصادية، يرجى المحاولة مرة أخرى",
            parse_mode='HTML'
        )

@router.callback_query(F.data == "market_stats")
async def market_stats_callback(callback: CallbackQuery):
    """Handle market stats callback"""
    
    text = """
📊 <b>إحصائيات السوق</b>

اختر نوع البيانات التي تريد عرضها:
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="😨 مؤشر الخوف والطمع", callback_data="fear_greed"),
            InlineKeyboardButton(text="📈 الدعم والمقاومة", callback_data="support_resistance")
        ],
        [
            InlineKeyboardButton(text="📅 الأجندة الاقتصادية", callback_data="economic_calendar"),
            InlineKeyboardButton(text="💹 أسعار العملات", callback_data="crypto_prices")
        ],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data == "fear_greed")
async def fear_greed_callback(callback: CallbackQuery):
    """Handle fear and greed index callback"""
    
    api_client = APIClient()
    try:
        fear_greed_data = await api_client.get_fear_greed_index()
        
        text = format_fear_greed(fear_greed_data)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="fear_greed")],
            [InlineKeyboardButton(text="📊 المزيد من الإحصائيات", callback_data="market_stats")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل مؤشر الخوف والطمع", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "support_resistance")
async def support_resistance_callback(callback: CallbackQuery):
    """Handle support and resistance levels callback"""
    
    api_client = APIClient()
    try:
        sr_data = await api_client.get_support_resistance_levels()
        
        text = """
📈 <b>مستويات الدعم والمقاومة</b>

🔹 <b>العملات الرئيسية:</b>
        """
        
        for coin_data in sr_data:
            symbol = coin_data['symbol']
            current_price = coin_data['current_price']
            support_levels = coin_data['support_levels']
            resistance_levels = coin_data['resistance_levels']
            
            text += f"\n\n💰 <b>{symbol}</b>\n"
            text += f"💵 السعر الحالي: <b>${current_price:,.2f}</b>\n"
            
            if support_levels:
                text += f"🟢 الدعم: <b>${support_levels[0]:,.2f}</b>"
                if len(support_levels) > 1:
                    text += f" | <b>${support_levels[1]:,.2f}</b>"
                text += "\n"
            
            if resistance_levels:
                text += f"🔴 المقاومة: <b>${resistance_levels[0]:,.2f}</b>"
                if len(resistance_levels) > 1:
                    text += f" | <b>${resistance_levels[1]:,.2f}</b>"
                text += "\n"
        
        text += "\n\n⚠️ <b>تنبيه:</b> هذه المستويات للمرجع فقط وليست نصائح استثمارية"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="support_resistance")],
            [InlineKeyboardButton(text="📊 المزيد من الإحصائيات", callback_data="market_stats")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل مستويات الدعم والمقاومة", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "economic_calendar")
async def economic_calendar_callback(callback: CallbackQuery):
    """Handle economic calendar callback"""
    
    api_client = APIClient()
    try:
        calendar_data = await api_client.get_economic_calendar()
        
        text = format_economic_calendar(calendar_data)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="economic_calendar")],
            [InlineKeyboardButton(text="📊 إحصائيات السوق", callback_data="market_stats")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل الأجندة الاقتصادية", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "crypto_prices")
async def crypto_prices_callback(callback: CallbackQuery):
    """Handle crypto prices callback"""
    
    api_client = APIClient()
    try:
        prices_data = await api_client.get_crypto_prices()
        
        text = """
💹 <b>أسعار العملات الرقمية</b>

🔹 <b>أهم العملات:</b>
        """
        
        for coin in prices_data:
            symbol = coin['symbol']
            price = coin['price']
            change_24h = coin['change_24h']
            volume_24h = coin['volume_24h']
            
            change_emoji = "🟢" if change_24h >= 0 else "🔴"
            change_sign = "+" if change_24h >= 0 else ""
            
            text += f"\n\n💰 <b>{symbol}</b>\n"
            text += f"💵 السعر: <b>${price:,.4f}</b>\n"
            text += f"{change_emoji} التغيير 24س: <b>{change_sign}{change_24h:.2f}%</b>\n"
            text += f"📊 الحجم 24س: <b>${volume_24h:,.0f}</b>"
        
        text += f"\n\n🕐 آخر تحديث: {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="crypto_prices")],
            [InlineKeyboardButton(text="📊 المزيد من الإحصائيات", callback_data="market_stats")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل أسعار العملات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "market_analysis")
async def market_analysis_callback(callback: CallbackQuery):
    """Handle market analysis callback"""
    
    api_client = APIClient()
    try:
        analysis_data = await api_client.get_market_analysis()
        
        text = f"""
📊 <b>تحليل السوق العام</b>

🌡️ <b>حالة السوق:</b> {analysis_data['market_sentiment']}

📈 <b>الاتجاه العام:</b> {analysis_data['trend']}

💰 <b>القيمة السوقية الإجمالية:</b> ${analysis_data['total_market_cap']:,.0f}

📊 <b>هيمنة البيتكوين:</b> {analysis_data['btc_dominance']:.1f}%

🔄 <b>حجم التداول 24س:</b> ${analysis_data['total_volume_24h']:,.0f}

🔹 <b>التوصية:</b> {analysis_data['recommendation']}

⚠️ <b>ملاحظة:</b> هذا التحليل للمرجع فقط وليس نصيحة استثمارية
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="market_analysis")],
            [InlineKeyboardButton(text="📊 إحصائيات أخرى", callback_data="market_stats")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل تحليل السوق", show_alert=True)
    
    await callback.answer()

