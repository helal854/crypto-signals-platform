"""
Bot configuration settings
"""

import os
from typing import List

# Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/crypto_signals')

# Admin Configuration
ADMIN_USER_IDS: List[int] = [
    int(user_id) for user_id in os.getenv('ADMIN_USER_IDS', '').split(',') 
    if user_id.strip()
]

# Subscription Plans
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'مجاني',
        'price': 0,
        'duration_days': 30,
        'features': [
            '✅ إشارات Spot محدودة (5 يومياً)',
            '✅ إحصائيات السوق الأساسية',
            '❌ إشارات Futures',
            '❌ الأجندة الاقتصادية',
            '❌ دعم فني مخصص'
        ]
    },
    'pro': {
        'name': 'احترافي',
        'price': 50,
        'duration_days': 30,
        'features': [
            '✅ إشارات Spot غير محدودة',
            '✅ إشارات Futures (محدودة)',
            '✅ إحصائيات السوق المتقدمة',
            '✅ الأجندة الاقتصادية',
            '✅ دعم فني عبر البوت',
            '❌ Futures Leaderboard'
        ]
    },
    'elite': {
        'name': 'نخبة',
        'price': 100,
        'duration_days': 30,
        'features': [
            '✅ جميع إشارات Spot',
            '✅ جميع إشارات Futures',
            '✅ Futures Leaderboard كامل',
            '✅ إحصائيات متقدمة',
            '✅ الأجندة الاقتصادية',
            '✅ دعم فني مخصص',
            '✅ إشعارات فورية',
            '✅ تحليلات حصرية'
        ]
    }
}

# Payment Networks
PAYMENT_NETWORKS = {
    'USDT_TRC20': {
        'name': 'USDT (TRC20)',
        'symbol': 'USDT',
        'network': 'TRC20',
        'min_amount': 10
    },
    'USDT_BEP20': {
        'name': 'USDT (BEP20)',
        'symbol': 'USDT',
        'network': 'BEP20',
        'min_amount': 10
    },
    'USDT_ERC20': {
        'name': 'USDT (ERC20)',
        'symbol': 'USDT',
        'network': 'ERC20',
        'min_amount': 10
    },
    'BTC': {
        'name': 'Bitcoin',
        'symbol': 'BTC',
        'network': 'Bitcoin',
        'min_amount': 0.001
    }
}

# Message Templates
WELCOME_MESSAGE = """
🎯 <b>مرحباً بك في بوت إشارات التداول!</b>

🚀 احصل على أفضل إشارات التداول للعملات الرقمية من أفضل المتداولين في Binance

📊 <b>ما نقدمه:</b>
• إشارات Spot دقيقة ومربحة
• إشارات Futures من أفضل المتداولين
• إحصائيات السوق المباشرة
• الأجندة الاقتصادية
• مؤشر الخوف والطمع

💎 <b>ابدأ رحلتك الآن:</b>
"""

HELP_MESSAGE = """
📚 <b>دليل استخدام البوت</b>

🔹 <b>الأوامر الأساسية:</b>
/start - بدء استخدام البوت
/subscribe - الاشتراك في الخدمة
/myaccount - حسابي الشخصي
/help - عرض هذه المساعدة

🔹 <b>الإشارات:</b>
/spot - أحدث إشارات Spot
/futures - إشارات Futures
/leaderboard - ترتيب أفضل المتداولين

🔹 <b>السوق:</b>
/market - إحصائيات السوق
/feargreed - مؤشر الخوف والطمع
/schedule - الأجندة الاقتصادية

🔹 <b>الدعم:</b>
إذا كنت تواجه أي مشكلة، تواصل معنا عبر الدعم الفني
"""

# Rate Limiting
RATE_LIMIT_MESSAGES = 10  # messages per minute per user
RATE_LIMIT_WINDOW = 60    # seconds

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# External APIs
BINANCE_API_URL = 'https://api.binance.com'
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3'
FEAR_GREED_API_URL = 'https://api.alternative.me/fng'
TRADING_ECONOMICS_API_URL = 'https://api.tradingeconomics.com'

# Cache Settings
CACHE_TTL_MARKET_DATA = 300  # 5 minutes
CACHE_TTL_FEAR_GREED = 3600  # 1 hour
CACHE_TTL_SCHEDULE = 7200    # 2 hours

# Notification Settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# File Upload Settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif']

