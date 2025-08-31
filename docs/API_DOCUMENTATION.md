# توثيق API - منصة إشارات التداول

## نظرة عامة
هذا التوثيق يغطي جميع نقاط النهاية (endpoints) المتاحة في API منصة إشارات التداول.

**Base URL:** `https://your-domain.com/api`

## المصادقة

جميع نقاط النهاية المحمية تتطلب JWT token في header:

```http
Authorization: Bearer <your_jwt_token>
```

### الحصول على Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password",
  "role": "admin"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

## نقاط النهاية

### 1. المصادقة (Authentication)

#### تسجيل الدخول
```http
POST /api/auth/login
```

#### تسجيل الخروج
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

#### تحديث Token
```http
POST /api/auth/refresh
Authorization: Bearer <token>
```

#### تغيير كلمة المرور
```http
PUT /api/auth/change-password
Authorization: Bearer <token>

{
  "current_password": "old_password",
  "new_password": "new_password"
}
```

### 2. إدارة المستخدمين (Users)

#### قائمة المستخدمين
```http
GET /api/users
Authorization: Bearer <token>
```

#### إنشاء مستخدم جديد
```http
POST /api/users
Authorization: Bearer <token>

{
  "username": "new_user",
  "password": "password",
  "role": "moderator",
  "is_active": true
}
```

#### تحديث مستخدم
```http
PUT /api/users/{user_id}
Authorization: Bearer <token>

{
  "username": "updated_user",
  "role": "support",
  "is_active": false
}
```

#### حذف مستخدم
```http
DELETE /api/users/{user_id}
Authorization: Bearer <token>
```

### 3. مستخدمي تليجرام (Telegram Users)

#### قائمة مستخدمي تليجرام
```http
GET /api/telegram-users
Authorization: Bearer <token>
```

#### تحديث اشتراك مستخدم
```http
PUT /api/telegram-users/{user_id}/subscription
Authorization: Bearer <token>

{
  "subscription_type": "premium",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### 4. التكاملات (Integrations)

#### قائمة التكاملات
```http
GET /api/integrations
Authorization: Bearer <token>
```

#### حفظ مفاتيح API
```http
POST /api/integrations
Authorization: Bearer <token>

{
  "provider": "binance",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret",
  "is_active": true
}
```

#### اختبار اتصال
```http
POST /api/integrations/{integration_id}/test
Authorization: Bearer <token>
```

#### تحديث حالة التكامل
```http
PUT /api/integrations/{integration_id}/toggle
Authorization: Bearer <token>
```

### 5. بيانات السوق (Market Data)

#### مؤشر الخوف والطمع
```http
GET /api/market/fear-greed
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "value": 65,
    "value_classification": "Greed",
    "timestamp": "2024-01-15T10:30:00Z",
    "arabic_classification": "طمع"
  }
}
```

#### مستويات الدعم والمقاومة
```http
GET /api/market/support-resistance?symbol=BTCUSDT
```

#### أسعار العملات الرقمية
```http
GET /api/market/prices
```

#### الأجندة الاقتصادية
```http
GET /api/market/economic-calendar?days=7
```

### 6. الإشارات (Signals)

#### قائمة إشارات Spot
```http
GET /api/signals/spot
Authorization: Bearer <token>
```

#### إنشاء إشارة Spot جديدة
```http
POST /api/signals/spot
Authorization: Bearer <token>

{
  "symbol": "BTCUSDT",
  "signal_type": "buy",
  "entry_price": 43250.00,
  "target_prices": [44000.00, 45000.00, 46000.00],
  "stop_loss": 42000.00,
  "confidence": 85,
  "analysis": "تحليل فني يشير إلى اتجاه صاعد"
}
```

#### تحديث حالة إشارة
```http
PUT /api/signals/spot/{signal_id}/status
Authorization: Bearer <token>

{
  "status": "hit_target_1",
  "notes": "تم الوصول للهدف الأول"
}
```

#### قائمة إشارات Futures
```http
GET /api/signals/futures
Authorization: Bearer <token>
```

#### إنشاء إشارة Futures
```http
POST /api/signals/futures
Authorization: Bearer <token>

{
  "symbol": "BTCUSDT",
  "signal_type": "long",
  "entry_price": 43250.00,
  "target_prices": [44000.00, 45000.00],
  "stop_loss": 42000.00,
  "leverage": 10,
  "risk_percentage": 2.0,
  "trader_name": "أحمد محمد"
}
```

### 7. المدفوعات (Payments)

#### قائمة المدفوعات
```http
GET /api/payments
Authorization: Bearer <token>
```

#### إنشاء فاتورة دفع
```http
POST /api/payments/invoice
Authorization: Bearer <token>

{
  "user_id": 123,
  "amount": 50.0,
  "currency": "USDT",
  "subscription_type": "premium",
  "payment_method": "crypto"
}
```

#### تحديث حالة دفعة
```http
PUT /api/payments/{payment_id}/status
Authorization: Bearer <token>

{
  "status": "confirmed",
  "transaction_hash": "0x123..."
}
```

#### مزامنة المدفوعات
```http
POST /api/payments/{payment_id}/sync
Authorization: Bearer <token>
```

### 8. قوالب الرسائل (Templates)

#### قائمة القوالب
```http
GET /api/templates
Authorization: Bearer <token>
```

#### إنشاء قالب جديد
```http
POST /api/templates
Authorization: Bearer <token>

{
  "name": "إشارة شراء BTC",
  "identifier": "btc_buy_signal",
  "content": "🚀 إشارة شراء جديدة\n\n💰 العملة: {symbol}\n📈 السعر: {price}\n🎯 الهدف: {target}"
}
```

#### معاينة قالب
```http
POST /api/templates/{template_id}/preview
Authorization: Bearer <token>

{
  "variables": {
    "symbol": "BTCUSDT",
    "price": "43250",
    "target": "45000"
  }
}
```

### 9. الرسائل العامة (Broadcasts)

#### قائمة الرسائل العامة
```http
GET /api/broadcasts
Authorization: Bearer <token>
```

#### إنشاء رسالة عامة
```http
POST /api/broadcasts
Authorization: Bearer <token>

{
  "title": "تحديث مهم",
  "content": "رسالة مهمة لجميع المستخدمين",
  "target_audience": "all",
  "requires_confirmation": true,
  "scheduled_at": "2024-01-15T15:00:00Z"
}
```

#### إرسال رسالة عامة
```http
POST /api/broadcasts/{broadcast_id}/send
Authorization: Bearer <token>
```

### 10. Futures المتقدمة

#### إعدادات Futures
```http
GET /api/futures/settings
Authorization: Bearer <token>
```

#### تحديث إعدادات Futures
```http
PUT /api/futures/settings
Authorization: Bearer <token>

{
  "leaderboard_enabled": true,
  "max_risk_percentage": 5.0,
  "min_confidence_score": 70,
  "auto_close_enabled": true
}
```

#### Leaderboard المتداولين
```http
GET /api/futures/leaderboard
```

#### إضافة متداول جديد
```http
POST /api/futures/traders
Authorization: Bearer <token>

{
  "name": "أحمد محمد",
  "binance_uid": "123456789",
  "is_active": true,
  "risk_score": 3
}
```

### 11. لوحة المعلومات (Dashboard)

#### إحصائيات عامة
```http
GET /api/dashboard/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_users": 1234,
    "active_signals": 42,
    "total_revenue": 12345.67,
    "system_status": "healthy"
  }
}
```

#### بيانات الرسوم البيانية
```http
GET /api/dashboard/charts
Authorization: Bearer <token>
```

#### حالة النظام
```http
GET /api/dashboard/system-status
Authorization: Bearer <token>
```

## رموز الاستجابة

| Code | Description |
|------|-------------|
| 200  | نجح الطلب |
| 201  | تم إنشاء المورد بنجاح |
| 400  | خطأ في البيانات المرسلة |
| 401  | غير مصرح بالوصول |
| 403  | ممنوع الوصول |
| 404  | المورد غير موجود |
| 500  | خطأ في الخادم |

## تنسيق الاستجابة

جميع الاستجابات تتبع التنسيق التالي:

```json
{
  "status": "success|error",
  "data": {},
  "message": "رسالة توضيحية",
  "errors": []
}
```

## معدل الطلبات (Rate Limiting)

- **API عام:** 100 طلب/دقيقة
- **تسجيل الدخول:** 5 محاولات/دقيقة
- **إنشاء الإشارات:** 10 طلبات/دقيقة

## أمثلة بـ cURL

### تسجيل الدخول والحصول على إشارات:

```bash
# تسجيل الدخول
TOKEN=$(curl -s -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password","role":"admin"}' \
  | jq -r '.data.access_token')

# الحصول على الإشارات
curl -H "Authorization: Bearer $TOKEN" \
  https://your-domain.com/api/signals/spot
```

### إنشاء إشارة جديدة:

```bash
curl -X POST https://your-domain.com/api/signals/spot \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "signal_type": "buy",
    "entry_price": 43250.00,
    "target_prices": [44000.00, 45000.00],
    "stop_loss": 42000.00,
    "confidence": 85
  }'
```

## WebSocket (قادم قريباً)

سيتم إضافة دعم WebSocket للتحديثات الفورية:
- تحديثات الأسعار
- إشارات جديدة
- تحديثات حالة الإشارات

---

للمزيد من المعلومات، راجع الكود المصدري أو تواصل مع فريق التطوير.

