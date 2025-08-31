# 🚀 منصة إشارات التداول للعملات الرقمية

نظام متكامل لإشارات تداول العملات الرقمية (Spot & Futures) مع بوت تليجرام ولوحة تحكم إدارية شاملة.

## 📋 المحتويات

- [الميزات الرئيسية](#الميزات-الرئيسية)
- [التقنيات المستخدمة](#التقنيات-المستخدمة)
- [متطلبات النظام](#متطلبات-النظام)
- [التثبيت والإعداد](#التثبيت-والإعداد)
- [الاستخدام](#الاستخدام)
- [هيكل المشروع](#هيكل-المشروع)
- [المساهمة](#المساهمة)

## ✨ الميزات الرئيسية

### 🤖 بوت تليجرام
- **إشارات Spot**: إشارات تداول فورية مع 5 أهداف ووقف خسارة
- **إشارات Futures**: إشارات العقود الآجلة من أفضل 100 متداول في Binance
- **حالة السوق**: تحليل Fear & Greed ومستويات الدعم والمقاومة
- **الأجندة الاقتصادية**: أهم الأحداث الاقتصادية القادمة
- **نظام اشتراكات**: Free, Pro, Elite
- **واجهة عربية كاملة**: RTL مع إيموجي وتنسيق احترافي

### 🎛️ لوحة التحكم الإدارية
- **نظام صلاحيات متقدم (RBAC)**: Admin, Moderator, Support
- **إدارة التكاملات**: حفظ مشفر لمفاتيح API مع اختبار الاتصال
- **إدارة المدفوعات**: متابعة وإدارة المدفوعات مع NowPayments/BTCPay
- **قوالب الرسائل**: إنشاء وتعديل قوالب الرسائل
- **الرسائل العامة**: إرسال آمن مع تأكيد مزدوج
- **إدارة Futures**: 
  - إعدادات Binance Leaderboard
  - إدارة المتداولين (Follow/Unfollow)
  - قواعد توليد الإشارات
  - إدارة المخاطر والحدود

### 🔗 التكاملات
- **Binance API**: بيانات الأسعار والتداول
- **Binance Leaderboard**: أفضل 100 متداول
- **CoinGecko**: بيانات السوق العامة
- **Alternative.me**: مؤشر Fear & Greed
- **TradingEconomics**: الأجندة الاقتصادية
- **NowPayments/BTCPay**: معالجة المدفوعات

## 🛠️ التقنيات المستخدمة

### Backend
- **Flask**: إطار عمل Python للخدمات الخلفية
- **PostgreSQL**: قاعدة بيانات رئيسية
- **SQLAlchemy**: ORM للتعامل مع قاعدة البيانات
- **JWT**: نظام المصادقة والتوكن
- **Cryptography**: تشفير مفاتيح API

### Frontend
- **React**: مكتبة واجهة المستخدم
- **Tailwind CSS**: إطار عمل التصميم
- **shadcn/ui**: مكونات UI جاهزة
- **Vite**: أداة البناء والتطوير
- **React Router**: التنقل بين الصفحات

### Bot
- **aiogram 3.x**: مكتبة بوت تليجرام
- **asyncio**: البرمجة غير المتزامنة
- **aiohttp**: طلبات HTTP غير متزامنة

### DevOps
- **Docker & Docker Compose**: الحاويات والتشغيل
- **PostgreSQL**: قاعدة البيانات في حاوية
- **Nginx**: خادم الويب (للإنتاج)

## 📋 متطلبات النظام

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**
- **4GB RAM** (الحد الأدنى)
- **10GB** مساحة تخزين

## 🚀 التثبيت والإعداد

### 1. استنساخ المشروع
```bash
git clone <repository-url>
cd crypto-signals-platform
```

### 2. إعداد متغيرات البيئة
```bash
cp .env.example .env
```

قم بتعديل ملف `.env` وإضافة القيم المطلوبة:

```env
# JWT Secret (مطلوب)
JWT_SECRET=$(openssl rand -base64 48)

# Telegram Bot Token (مطلوب)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Binance API (اختياري)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key

# Trading Economics (اختياري - يستخدم guest mode افتراضياً)
TRADING_ECONOMICS_KEY=your_te_key
```

### 3. تشغيل النظام
```bash
# بناء وتشغيل جميع الخدمات
docker-compose up --build -d

# مراقبة السجلات
docker-compose logs -f
```

### 4. الوصول للنظام
- **لوحة التحكم**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **قاعدة البيانات**: localhost:5432

### 5. تسجيل الدخول الافتراضي
- **اسم المستخدم**: admin
- **كلمة المرور**: admin123
- **الدور**: Admin

⚠️ **مهم**: قم بتغيير كلمة المرور فوراً بعد أول تسجيل دخول!

## 📖 الاستخدام

### إعداد بوت تليجرام
1. أنشئ بوت جديد عبر [@BotFather](https://t.me/BotFather)
2. احصل على التوكن وأضفه في `.env`
3. أعد تشغيل الخدمات: `docker-compose restart bot`

### إعداد التكاملات
1. سجل دخول للوحة التحكم
2. اذهب إلى "التكاملات"
3. أضف مفاتيح API للخدمات المطلوبة
4. اختبر الاتصال للتأكد من صحة المفاتيح

### إرسال إشارة Spot
1. اذهب إلى "إشارات Spot"
2. أضف إشارة جديدة مع جميع البيانات
3. احفظ وأرسل للمشتركين

### إعداد Futures
1. اذهب إلى "Futures → Source"
2. اختر معايير الترتيب (ROI أو PnL)
3. اذهب إلى "Futures → Traders"
4. فعّل المتداولين المرغوب متابعتهم

## 📁 هيكل المشروع

```
crypto-signals-platform/
├── backend/                 # خدمات Flask الخلفية
│   └── crypto_signals_api/
│       ├── src/
│       │   ├── models/      # نماذج قاعدة البيانات
│       │   ├── routes/      # مسارات API
│       │   └── main.py      # نقطة الدخول
│       └── requirements.txt
├── frontend/                # واجهة React
│   └── crypto-signals-dashboard/
│       ├── src/
│       │   ├── components/  # مكونات React
│       │   ├── pages/       # صفحات التطبيق
│       │   └── lib/         # مكتبات مساعدة
│       └── package.json
├── bot/                     # بوت تليجرام
│   ├── handlers/            # معالجات الأوامر
│   ├── utils/               # وظائف مساعدة
│   ├── main.py              # نقطة الدخول
│   └── requirements.txt
├── scripts/                 # سكريبتات الإعداد
│   └── init.sql            # إعداد قاعدة البيانات
├── docs/                    # التوثيق
├── docker-compose.yml       # إعداد الحاويات
├── .env.example            # مثال متغيرات البيئة
└── README.md               # هذا الملف
```

## 🔧 أوامر مفيدة

```bash
# إيقاف جميع الخدمات
docker-compose down

# إعادة بناء خدمة معينة
docker-compose build backend
docker-compose up -d backend

# عرض السجلات
docker-compose logs backend
docker-compose logs bot
docker-compose logs frontend

# الدخول لحاوية معينة
docker-compose exec backend bash
docker-compose exec db psql -U postgres -d crypto_signals

# نسخ احتياطي لقاعدة البيانات
docker-compose exec db pg_dump -U postgres crypto_signals > backup.sql

# استعادة قاعدة البيانات
docker-compose exec -T db psql -U postgres crypto_signals < backup.sql
```

## 🔒 الأمان

- **تشفير مفاتيح API**: جميع المفاتيح مشفرة في قاعدة البيانات
- **JWT Tokens**: نظام مصادقة آمن
- **RBAC**: نظام صلاحيات متدرج
- **Audit Logs**: تسجيل جميع العمليات الحساسة
- **Rate Limiting**: حماية من الطلبات المفرطة
- **Input Validation**: التحقق من صحة جميع المدخلات

## 🚀 النشر للإنتاج

### متطلبات الخادم
- **VPS/Cloud Server** مع 4GB RAM على الأقل
- **Ubuntu 20.04+** أو **CentOS 8+**
- **Docker & Docker Compose**
- **Domain Name** مع SSL Certificate

### خطوات النشر
1. استنساخ المشروع على الخادم
2. إعداد متغيرات البيئة للإنتاج
3. إعداد Nginx كـ Reverse Proxy
4. تفعيل SSL Certificate
5. تشغيل النظام: `docker-compose -f docker-compose.prod.yml up -d`

## 📞 الدعم والمساعدة

للحصول على المساعدة أو الإبلاغ عن مشاكل:

1. تحقق من [التوثيق](./docs/)
2. راجع [الأسئلة الشائعة](./docs/FAQ.md)
3. أنشئ [Issue جديد](../../issues)

## 📄 الترخيص

هذا المشروع محمي بحقوق الطبع والنشر. جميع الحقوق محفوظة.

---

**تم التطوير بواسطة**: فريق Manus
**الإصدار**: 1.0.0
**تاريخ آخر تحديث**: أغسطس 2025

