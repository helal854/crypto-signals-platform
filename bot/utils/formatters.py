"""
Message formatters for the bot
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

def format_spot_signal(signal: Dict[str, Any], index: int = None, detailed: bool = False) -> str:
    """Format Spot signal message"""
    
    if index:
        header = f"📊 <b>إشارة Spot #{index}</b>\n"
    else:
        header = "📊 <b>إشارة Spot</b>\n"
    
    # Signal type emoji
    signal_type = signal.get('signal_type', 'buy')
    type_emoji = "🟢" if signal_type.lower() == 'buy' else "🔴"
    type_text = "شراء" if signal_type.lower() == 'buy' else "بيع"
    
    # Format price
    entry_price = signal.get('entry_price', 0)
    current_price = signal.get('current_price', entry_price)
    
    # Calculate PnL if available
    pnl_text = ""
    if signal.get('pnl') is not None:
        pnl = signal['pnl']
        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
        pnl_text = f"\n💰 الربح/الخسارة: {pnl_emoji} <b>{pnl:+.2f}%</b>"
    
    # Basic info
    text = header
    text += f"💎 العملة: <b>{signal['symbol']}</b>\n"
    text += f"{type_emoji} النوع: <b>{type_text}</b>\n"
    text += f"💵 سعر الدخول: <b>${entry_price:.4f}</b>\n"
    text += f"📈 السعر الحالي: <b>${current_price:.4f}</b>"
    text += pnl_text
    
    if detailed:
        # Add more details for detailed view
        if signal.get('target_price'):
            text += f"\n🎯 الهدف: <b>${signal['target_price']:.4f}</b>"
        
        if signal.get('stop_loss'):
            text += f"\n🛑 وقف الخسارة: <b>${signal['stop_loss']:.4f}</b>"
        
        if signal.get('confidence'):
            confidence = signal['confidence']
            confidence_emoji = "🔥" if confidence >= 80 else "⭐" if confidence >= 60 else "💡"
            text += f"\n{confidence_emoji} مستوى الثقة: <b>{confidence}%</b>"
        
        if signal.get('created_at'):
            created_time = datetime.fromisoformat(signal['created_at'].replace('Z', '+00:00'))
            text += f"\n🕐 وقت الإشارة: <b>{created_time.strftime('%Y-%m-%d %H:%M')}</b>"
    
    return text

def format_futures_signal(signal: Dict[str, Any], index: int = None, detailed: bool = False) -> str:
    """Format Futures signal message"""
    
    if index:
        header = f"🚀 <b>إشارة Futures #{index}</b>\n"
    else:
        header = "🚀 <b>إشارة Futures</b>\n"
    
    # Signal direction
    direction = signal.get('direction', 'long')
    direction_emoji = "📈" if direction.lower() == 'long' else "📉"
    direction_text = "صاعد (Long)" if direction.lower() == 'long' else "هابط (Short)"
    
    # Trader info with hyperlink
    trader_name = signal.get('trader_name', 'Unknown')
    trader_uid = signal.get('trader_uid')
    if trader_uid:
        trader_url = f"https://www.binance.com/en/futures-activity/leaderboard/user?encryptedUid={trader_uid}"
        trader_link = f"<a href='{trader_url}'>{trader_name}</a>"
    else:
        trader_link = trader_name
    
    # Format leverage
    leverage = signal.get('leverage', 1)
    leverage_text = f"{leverage}x" if leverage > 1 else "بدون رافعة"
    
    # Calculate PnL
    pnl_text = ""
    if signal.get('pnl') is not None:
        pnl = signal['pnl']
        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
        pnl_text = f"\n💰 الربح/الخسارة: {pnl_emoji} <b>{pnl:+.2f} USDT</b>"
    
    # ROI
    roi_text = ""
    if signal.get('roi') is not None:
        roi = signal['roi']
        roi_emoji = "🟢" if roi >= 0 else "🔴"
        roi_text = f"\n📊 العائد: {roi_emoji} <b>{roi:+.2f}%</b>"
    
    text = header
    text += f"💎 العملة: <b>{signal['symbol']}</b>\n"
    text += f"{direction_emoji} الاتجاه: <b>{direction_text}</b>\n"
    text += f"⚡ الرافعة: <b>{leverage_text}</b>\n"
    text += f"👤 المتداول: {trader_link}\n"
    text += f"💵 سعر الدخول: <b>${signal.get('entry_price', 0):.4f}</b>"
    text += pnl_text
    text += roi_text
    
    if detailed:
        # Add more details
        if signal.get('position_size'):
            text += f"\n📏 حجم المركز: <b>{signal['position_size']:.2f} USDT</b>"
        
        if signal.get('mark_price'):
            text += f"\n📈 سعر التسوية: <b>${signal['mark_price']:.4f}</b>"
        
        if signal.get('created_at'):
            created_time = datetime.fromisoformat(signal['created_at'].replace('Z', '+00:00'))
            text += f"\n🕐 وقت الدخول: <b>{created_time.strftime('%Y-%m-%d %H:%M')}</b>"
        
        if signal.get('status'):
            status_emoji = {"open": "🟢", "closed": "⚪", "liquidated": "🔴"}.get(signal['status'], "❓")
            status_text = {"open": "مفتوح", "closed": "مغلق", "liquidated": "مصفى"}.get(signal['status'], signal['status'])
            text += f"\n{status_emoji} الحالة: <b>{status_text}</b>"
    
    return text

def format_fear_greed(data: Dict[str, Any]) -> str:
    """Format Fear & Greed index message"""
    
    value = data.get('value', 0)
    classification = data.get('value_classification', 'Neutral')
    
    # Emoji based on value
    if value <= 20:
        emoji = "😱"
        arabic_class = "خوف شديد"
    elif value <= 40:
        emoji = "😰"
        arabic_class = "خوف"
    elif value <= 60:
        emoji = "😐"
        arabic_class = "محايد"
    elif value <= 80:
        emoji = "😊"
        arabic_class = "طمع"
    else:
        emoji = "🤑"
        arabic_class = "طمع شديد"
    
    text = f"""
😨 <b>مؤشر الخوف والطمع</b>

{emoji} <b>القيمة الحالية: {value}/100</b>
📊 التصنيف: <b>{arabic_class}</b>

🔹 <b>ماذا يعني هذا؟</b>
"""
    
    if value <= 20:
        text += "• السوق في حالة خوف شديد\n• قد تكون فرصة شراء جيدة\n• المستثمرون يبيعون بقلق"
    elif value <= 40:
        text += "• السوق في حالة خوف\n• الحذر مطلوب\n• قد تكون فرصة للشراء التدريجي"
    elif value <= 60:
        text += "• السوق في حالة محايدة\n• لا توجد مشاعر قوية\n• انتظار إشارات أوضح"
    elif value <= 80:
        text += "• السوق في حالة طمع\n• الحذر من الشراء\n• قد يكون وقت جني الأرباح"
    else:
        text += "• السوق في حالة طمع شديد\n• خطر تصحيح قريب\n• فكر في البيع أو جني الأرباح"
    
    if data.get('timestamp'):
        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        text += f"\n\n🕐 آخر تحديث: {timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    text += "\n\n⚠️ <b>تنبيه:</b> هذا المؤشر للمرجع فقط وليس نصيحة استثمارية"
    
    return text

def format_economic_calendar(events: List[Dict[str, Any]]) -> str:
    """Format economic calendar message"""
    
    if not events:
        return """
📅 <b>الأجندة الاقتصادية</b>

🔍 لا توجد أحداث اقتصادية مهمة خلال الأيام القادمة

⏰ يتم تحديث الأجندة بشكل مستمر
        """
    
    text = "📅 <b>الأجندة الاقتصادية - أهم الأحداث</b>\n\n"
    
    for event in events[:7]:  # Show max 7 events
        # Parse date
        event_date = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
        
        # Impact emoji
        impact = event.get('impact', 'medium')
        impact_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(impact, '🟡')
        
        # Format date and time
        date_str = event_date.strftime('%m/%d')
        time_str = event_date.strftime('%H:%M')
        
        text += f"{impact_emoji} <b>{event['title']}</b>\n"
        text += f"🌍 الدولة: {event.get('country', 'غير محدد')}\n"
        text += f"📅 التاريخ: {date_str} في {time_str}\n"
        
        if event.get('forecast'):
            text += f"📊 التوقع: {event['forecast']}\n"
        
        text += "\n"
    
    text += "⚠️ <b>ملاحظة:</b> هذه الأحداث قد تؤثر على أسواق العملات الرقمية"
    
    return text

def format_subscription_info(user_data: Dict[str, Any]) -> str:
    """Format user subscription information"""
    
    subscription_type = user_data.get('subscription_type', 'free')
    
    # Plan names
    plan_names = {
        'free': 'المجاني',
        'pro': 'الاحترافي',
        'elite': 'النخبة'
    }
    
    plan_name = plan_names.get(subscription_type, subscription_type)
    
    # Plan emoji
    plan_emoji = {
        'free': '🆓',
        'pro': '💎',
        'elite': '👑'
    }.get(subscription_type, '📋')
    
    text = f"""
👤 <b>حسابي الشخصي</b>

{plan_emoji} <b>خطة الاشتراك:</b> {plan_name}
    """
    
    # Subscription expiry
    if user_data.get('subscription_expires_at'):
        expires_at = datetime.fromisoformat(user_data['subscription_expires_at'].replace('Z', '+00:00'))
        days_left = (expires_at - datetime.now()).days
        
        if days_left > 0:
            text += f"📅 ينتهي في: <b>{days_left} يوم</b>\n"
        else:
            text += "⚠️ <b>انتهى الاشتراك</b>\n"
    else:
        if subscription_type == 'free':
            text += "📅 مدى الحياة (مجاني)\n"
    
    # User stats
    if user_data.get('signals_received'):
        text += f"📊 الإشارات المستلمة: <b>{user_data['signals_received']}</b>\n"
    
    if user_data.get('join_date'):
        join_date = datetime.fromisoformat(user_data['join_date'].replace('Z', '+00:00'))
        text += f"📅 تاريخ الانضمام: <b>{join_date.strftime('%Y-%m-%d')}</b>\n"
    
    # Notifications status
    notifications = user_data.get('notifications_enabled', True)
    notification_status = "🔔 مفعلة" if notifications else "🔕 معطلة"
    text += f"🔔 الإشعارات: {notification_status}\n"
    
    # Available features based on plan
    text += f"\n🔹 <b>الميزات المتاحة:</b>\n"
    
    if subscription_type == 'free':
        text += "• إشارات Spot محدودة (5 يومياً)\n"
        text += "• إحصائيات السوق الأساسية\n"
        text += "• مؤشر الخوف والطمع"
    elif subscription_type == 'pro':
        text += "• إشارات Spot غير محدودة\n"
        text += "• إشارات Futures محدودة\n"
        text += "• إحصائيات السوق المتقدمة\n"
        text += "• الأجندة الاقتصادية\n"
        text += "• دعم فني عبر البوت"
    else:  # elite
        text += "• جميع إشارات Spot\n"
        text += "• جميع إشارات Futures\n"
        text += "• Futures Leaderboard كامل\n"
        text += "• إحصائيات متقدمة\n"
        text += "• الأجندة الاقتصادية\n"
        text += "• دعم فني مخصص\n"
        text += "• إشعارات فورية\n"
        text += "• تحليلات حصرية"
    
    return text

def format_payment_history(payments: List[Dict[str, Any]]) -> str:
    """Format payment history"""
    
    text = "📋 <b>سجل المدفوعات</b>\n\n"
    
    for payment in payments:
        # Status emoji
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'failed': '❌',
            'cancelled': '🚫'
        }.get(payment['status'], '❓')
        
        # Status text
        status_text = {
            'pending': 'قيد الانتظار',
            'confirmed': 'مؤكد',
            'failed': 'فشل',
            'cancelled': 'ملغي'
        }.get(payment['status'], payment['status'])
        
        # Format date
        created_date = datetime.fromisoformat(payment['created_at'].replace('Z', '+00:00'))
        
        text += f"{status_emoji} <b>${payment['amount']}</b> - {payment['payment_method']}\n"
        text += f"📋 الخطة: {payment.get('plan', 'غير محدد')}\n"
        text += f"📅 التاريخ: {created_date.strftime('%Y-%m-%d %H:%M')}\n"
        text += f"🔄 الحالة: <b>{status_text}</b>\n\n"
    
    return text

def format_signal_stats(stats: Dict[str, Any]) -> str:
    """Format signal statistics"""
    
    text = """
📊 <b>إحصائيات الإشارات</b>

🔹 <b>إشارات Spot:</b>
"""
    
    spot_stats = stats.get('spot', {})
    text += f"• إجمالي الإشارات: <b>{spot_stats.get('total', 0)}</b>\n"
    text += f"• الإشارات الناجحة: <b>{spot_stats.get('successful', 0)}</b>\n"
    text += f"• معدل النجاح: <b>{spot_stats.get('success_rate', 0):.1f}%</b>\n"
    text += f"• متوسط الربح: <b>{spot_stats.get('avg_profit', 0):+.2f}%</b>\n"
    
    text += "\n🔹 <b>إشارات Futures:</b>\n"
    
    futures_stats = stats.get('futures', {})
    text += f"• إجمالي الإشارات: <b>{futures_stats.get('total', 0)}</b>\n"
    text += f"• الإشارات الناجحة: <b>{futures_stats.get('successful', 0)}</b>\n"
    text += f"• معدل النجاح: <b>{futures_stats.get('success_rate', 0):.1f}%</b>\n"
    text += f"• متوسط الربح: <b>{futures_stats.get('avg_profit', 0):+.2f}%</b>\n"
    
    if stats.get('last_updated'):
        last_updated = datetime.fromisoformat(stats['last_updated'].replace('Z', '+00:00'))
        text += f"\n🕐 آخر تحديث: {last_updated.strftime('%Y-%m-%d %H:%M')}"
    
    return text

def format_admin_stats(stats: Dict[str, Any]) -> str:
    """Format admin statistics"""
    
    text = """
📊 <b>إحصائيات النظام</b>

👥 <b>المستخدمون:</b>
"""
    
    users = stats.get('users', {})
    text += f"• إجمالي المستخدمين: <b>{users.get('total', 0)}</b>\n"
    text += f"• المستخدمون النشطون: <b>{users.get('active', 0)}</b>\n"
    text += f"• مستخدمون جدد اليوم: <b>{users.get('new_today', 0)}</b>\n"
    
    text += "\n💰 <b>الاشتراكات:</b>\n"
    
    subscriptions = stats.get('subscriptions', {})
    text += f"• اشتراكات مجانية: <b>{subscriptions.get('free', 0)}</b>\n"
    text += f"• اشتراكات احترافية: <b>{subscriptions.get('pro', 0)}</b>\n"
    text += f"• اشتراكات نخبة: <b>{subscriptions.get('elite', 0)}</b>\n"
    
    text += "\n💳 <b>المدفوعات:</b>\n"
    
    payments = stats.get('payments', {})
    text += f"• إجمالي المدفوعات: <b>${payments.get('total_amount', 0):,.2f}</b>\n"
    text += f"• مدفوعات اليوم: <b>${payments.get('today_amount', 0):,.2f}</b>\n"
    text += f"• مدفوعات معلقة: <b>{payments.get('pending_count', 0)}</b>\n"
    
    text += "\n📊 <b>الإشارات:</b>\n"
    
    signals = stats.get('signals', {})
    text += f"• إشارات Spot اليوم: <b>{signals.get('spot_today', 0)}</b>\n"
    text += f"• إشارات Futures اليوم: <b>{signals.get('futures_today', 0)}</b>\n"
    text += f"• إجمالي الإشارات: <b>{signals.get('total', 0)}</b>\n"
    
    if stats.get('system_uptime'):
        text += f"\n⏰ وقت تشغيل النظام: <b>{stats['system_uptime']}</b>"
    
    return text

def format_user_list(users: List[Dict[str, Any]]) -> str:
    """Format user list for admin"""
    
    if not users:
        return """
👥 <b>قائمة المستخدمين</b>

🔍 لا توجد مستخدمون مسجلون
        """
    
    text = f"👥 <b>قائمة المستخدمين ({len(users)})</b>\n\n"
    
    for user in users[:10]:  # Show max 10 users
        subscription = user.get('subscription_type', 'free')
        subscription_emoji = {
            'free': '🆓',
            'pro': '💎',
            'elite': '👑'
        }.get(subscription, '📋')
        
        name = user.get('first_name', 'Unknown')
        username = user.get('username', '')
        user_id = user.get('user_id', '')
        
        text += f"{subscription_emoji} <b>{name}</b>"
        if username:
            text += f" (@{username})"
        text += f"\n🆔 ID: <code>{user_id}</code>\n"
        
        if user.get('last_active'):
            last_active = datetime.fromisoformat(user['last_active'].replace('Z', '+00:00'))
            text += f"🕐 آخر نشاط: {last_active.strftime('%Y-%m-%d')}\n"
        
        text += "\n"
    
    if len(users) > 10:
        text += f"... و {len(users) - 10} مستخدم آخر"
    
    return text

