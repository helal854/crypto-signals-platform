"""
Signals handler for Spot and Futures trading signals
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime, timedelta

from utils.api_client import APIClient
from utils.decorators import rate_limit, subscription_required
from utils.formatters import format_spot_signal, format_futures_signal, format_signal_stats
from utils.keyboards import get_signals_keyboard, get_futures_keyboard

router = Router()

@router.message(Command('spot'))
@rate_limit()
@subscription_required(['free', 'pro', 'elite'])
async def spot_signals_command(message: Message):
    """Handle /spot command"""
    
    api_client = APIClient()
    try:
        # Get user subscription to determine limits
        user_data = await api_client.get_telegram_user(message.from_user.id)
        subscription_type = user_data.get('subscription_type', 'free')
        
        # Get spot signals based on subscription
        if subscription_type == 'free':
            limit = 5
        else:
            limit = 20
        
        signals = await api_client.get_spot_signals(limit=limit)
        
        if not signals:
            text = """
📊 <b>إشارات Spot</b>

🔍 لا توجد إشارات متاحة حالياً

⏰ يتم تحديث الإشارات بشكل مستمر، تحقق مرة أخرى قريباً
            """
        else:
            text = f"📊 <b>أحدث إشارات Spot</b>\n\n"
            
            for i, signal in enumerate(signals[:5], 1):
                text += format_spot_signal(signal, i)
                text += "\n" + "─" * 30 + "\n"
            
            if subscription_type == 'free' and len(signals) > 5:
                text += "\n💎 <b>ترقية لخطة مدفوعة لرؤية المزيد من الإشارات</b>"
        
        keyboard = get_signals_keyboard(subscription_type)
        
        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await message.answer(
            "❌ حدث خطأ في تحميل الإشارات، يرجى المحاولة مرة أخرى",
            parse_mode='HTML'
        )

@router.message(Command('futures'))
@rate_limit()
@subscription_required(['pro', 'elite'])
async def futures_signals_command(message: Message):
    """Handle /futures command"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(message.from_user.id)
        subscription_type = user_data.get('subscription_type', 'free')
        
        if subscription_type == 'pro':
            limit = 10
        else:  # elite
            limit = 20
        
        signals = await api_client.get_futures_signals(limit=limit)
        
        if not signals:
            text = """
🚀 <b>إشارات Futures</b>

🔍 لا توجد إشارات متاحة حالياً

⏰ يتم تحديث الإشارات بشكل مستمر، تحقق مرة أخرى قريباً
            """
        else:
            text = f"🚀 <b>أحدث إشارات Futures</b>\n\n"
            
            for i, signal in enumerate(signals[:5], 1):
                text += format_futures_signal(signal, i)
                text += "\n" + "─" * 30 + "\n"
            
            if subscription_type == 'pro' and len(signals) > 5:
                text += "\n💎 <b>ترقية لخطة النخبة لرؤية المزيد من الإشارات</b>"
        
        keyboard = get_futures_keyboard(subscription_type)
        
        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await message.answer(
            "❌ حدث خطأ في تحميل الإشارات، يرجى المحاولة مرة أخرى",
            parse_mode='HTML'
        )

@router.message(Command('leaderboard'))
@rate_limit()
@subscription_required(['elite'])
async def leaderboard_command(message: Message):
    """Handle /leaderboard command"""
    
    api_client = APIClient()
    try:
        leaderboard = await api_client.get_futures_leaderboard(limit=10)
        
        if not leaderboard:
            text = """
🏆 <b>ترتيب أفضل المتداولين</b>

🔍 لا توجد بيانات متاحة حالياً

⏰ يتم تحديث الترتيب كل ساعة
            """
        else:
            text = "🏆 <b>ترتيب أفضل المتداولين (Futures)</b>\n\n"
            
            for i, trader in enumerate(leaderboard, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}️⃣"
                
                # Create hyperlink for trader name
                trader_url = f"https://www.binance.com/en/futures-activity/leaderboard/user?encryptedUid={trader['encrypted_uid']}"
                trader_name = f"<a href='{trader_url}'>{trader['nickname']}</a>"
                
                text += f"{emoji} <b>{trader_name}</b>\n"
                text += f"💰 PNL: <b>{trader['pnl']:+.2f} USDT</b>\n"
                text += f"📊 ROI: <b>{trader['roi']:+.2f}%</b>\n"
                text += f"📈 معدل الربح: <b>{trader['win_rate']:.1f}%</b>\n"
                text += f"🔢 عدد الصفقات: <b>{trader['trade_count']}</b>\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh_leaderboard")],
            [InlineKeyboardButton(text="📊 إشارات Futures", callback_data="view_futures")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await message.answer(
            "❌ حدث خطأ في تحميل الترتيب، يرجى المحاولة مرة أخرى",
            parse_mode='HTML'
        )

@router.callback_query(F.data == "view_signals")
async def view_signals_callback(callback: CallbackQuery):
    """Handle view signals callback"""
    
    text = """
📊 <b>اختر نوع الإشارات</b>

🔹 <b>Spot:</b> إشارات التداول الفوري
🔹 <b>Futures:</b> إشارات التداول بالرافعة المالية

💡 اختر النوع الذي تريد متابعته
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Spot", callback_data="spot_signals"),
            InlineKeyboardButton(text="🚀 Futures", callback_data="futures_signals")
        ],
        [InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await callback.answer()

@router.callback_query(F.data == "spot_signals")
async def spot_signals_callback(callback: CallbackQuery):
    """Handle spot signals callback"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(callback.from_user.id)
        subscription_type = user_data.get('subscription_type', 'free')
        
        if subscription_type == 'free':
            limit = 5
        else:
            limit = 20
        
        signals = await api_client.get_spot_signals(limit=limit)
        
        if not signals:
            text = """
📊 <b>إشارات Spot</b>

🔍 لا توجد إشارات متاحة حالياً

⏰ يتم تحديث الإشارات بشكل مستمر، تحقق مرة أخرى قريباً
            """
        else:
            text = f"📊 <b>أحدث إشارات Spot</b>\n\n"
            
            for i, signal in enumerate(signals[:5], 1):
                text += format_spot_signal(signal, i)
                text += "\n" + "─" * 30 + "\n"
            
            if subscription_type == 'free' and len(signals) > 5:
                text += "\n💎 <b>ترقية لخطة مدفوعة لرؤية المزيد من الإشارات</b>"
        
        keyboard = get_signals_keyboard(subscription_type)
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل الإشارات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "futures_signals")
async def futures_signals_callback(callback: CallbackQuery):
    """Handle futures signals callback"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(callback.from_user.id)
        subscription_type = user_data.get('subscription_type', 'free')
        
        if subscription_type == 'free':
            await callback.answer("💎 ترقية لخطة مدفوعة للوصول لإشارات Futures", show_alert=True)
            return
        
        if subscription_type == 'pro':
            limit = 10
        else:  # elite
            limit = 20
        
        signals = await api_client.get_futures_signals(limit=limit)
        
        if not signals:
            text = """
🚀 <b>إشارات Futures</b>

🔍 لا توجد إشارات متاحة حالياً

⏰ يتم تحديث الإشارات بشكل مستمر، تحقق مرة أخرى قريباً
            """
        else:
            text = f"🚀 <b>أحدث إشارات Futures</b>\n\n"
            
            for i, signal in enumerate(signals[:5], 1):
                text += format_futures_signal(signal, i)
                text += "\n" + "─" * 30 + "\n"
            
            if subscription_type == 'pro' and len(signals) > 5:
                text += "\n💎 <b>ترقية لخطة النخبة لرؤية المزيد من الإشارات</b>"
        
        keyboard = get_futures_keyboard(subscription_type)
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل الإشارات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "leaderboard")
async def leaderboard_callback(callback: CallbackQuery):
    """Handle leaderboard callback"""
    
    api_client = APIClient()
    try:
        user_data = await api_client.get_telegram_user(callback.from_user.id)
        subscription_type = user_data.get('subscription_type', 'free')
        
        if subscription_type != 'elite':
            await callback.answer("💎 ترقية لخطة النخبة للوصول للترتيب الكامل", show_alert=True)
            return
        
        leaderboard = await api_client.get_futures_leaderboard(limit=10)
        
        if not leaderboard:
            text = """
🏆 <b>ترتيب أفضل المتداولين</b>

🔍 لا توجد بيانات متاحة حالياً

⏰ يتم تحديث الترتيب كل ساعة
            """
        else:
            text = "🏆 <b>ترتيب أفضل المتداولين (Futures)</b>\n\n"
            
            for i, trader in enumerate(leaderboard, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}️⃣"
                
                # Create hyperlink for trader name
                trader_url = f"https://www.binance.com/en/futures-activity/leaderboard/user?encryptedUid={trader['encrypted_uid']}"
                trader_name = f"<a href='{trader_url}'>{trader['nickname']}</a>"
                
                text += f"{emoji} <b>{trader_name}</b>\n"
                text += f"💰 PNL: <b>{trader['pnl']:+.2f} USDT</b>\n"
                text += f"📊 ROI: <b>{trader['roi']:+.2f}%</b>\n"
                text += f"📈 معدل الربح: <b>{trader['win_rate']:.1f}%</b>\n"
                text += f"🔢 عدد الصفقات: <b>{trader['trade_count']}</b>\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh_leaderboard")],
            [InlineKeyboardButton(text="📊 إشارات Futures", callback_data="futures_signals")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل الترتيب", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "refresh_leaderboard")
async def refresh_leaderboard_callback(callback: CallbackQuery):
    """Refresh leaderboard data"""
    
    await leaderboard_callback(callback)

@router.callback_query(F.data == "signal_stats")
async def signal_stats_callback(callback: CallbackQuery):
    """Handle signal statistics callback"""
    
    api_client = APIClient()
    try:
        stats = await api_client.get_signal_statistics()
        
        text = format_signal_stats(stats)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 عرض الإشارات", callback_data="view_signals")],
            [InlineKeyboardButton(text="🔄 تحديث", callback_data="signal_stats")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل الإحصائيات", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data.startswith("signal_details_"))
async def signal_details_callback(callback: CallbackQuery):
    """Handle signal details callback"""
    
    signal_id = callback.data.split("_")[2]
    
    api_client = APIClient()
    try:
        signal = await api_client.get_signal_details(signal_id)
        
        if signal['type'] == 'spot':
            text = format_spot_signal(signal, detailed=True)
        else:
            text = format_futures_signal(signal, detailed=True)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 العودة للإشارات", callback_data="view_signals")]
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.answer("❌ حدث خطأ في تحميل تفاصيل الإشارة", show_alert=True)
    
    await callback.answer()

