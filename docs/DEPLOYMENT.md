# دليل النشر - منصة إشارات التداول

## نظرة عامة
هذا الدليل يوضح كيفية نشر منصة إشارات التداول في البيئة الإنتاجية باستخدام Docker.

## متطلبات النظام

### الحد الأدنى للمتطلبات:
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 50GB SSD
- **Network:** 100 Mbps

### المتطلبات الموصى بها:
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 100GB SSD
- **Network:** 1 Gbps

## البرامج المطلوبة

```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Git
sudo apt update
sudo apt install git -y

# Nginx (للـ SSL)
sudo apt install nginx certbot python3-certbot-nginx -y
```

## خطوات النشر

### 1. تحضير الخادم

```bash
# إنشاء مستخدم للتطبيق
sudo useradd -m -s /bin/bash cryptosignals
sudo usermod -aG docker cryptosignals

# إنشاء مجلدات العمل
sudo mkdir -p /opt/crypto-signals
sudo chown cryptosignals:cryptosignals /opt/crypto-signals

# التبديل للمستخدم الجديد
sudo su - cryptosignals
cd /opt/crypto-signals
```

### 2. تحميل الكود

```bash
# استنساخ المشروع
git clone https://github.com/your-username/crypto-signals-platform.git .

# إعداد الصلاحيات
chmod +x scripts/*.sh
```

### 3. إعداد متغيرات البيئة

```bash
# نسخ ملف البيئة
cp .env.production .env

# تحرير الملف وإدخال القيم الحقيقية
nano .env
```

**المتغيرات المطلوبة:**
```env
# Database
DB_PASSWORD=your_secure_database_password
REDIS_PASSWORD=your_secure_redis_password

# JWT & Encryption
JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters
ENCRYPTION_KEY=your_encryption_key_exactly_32_characters

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# APIs
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
COINGECKO_API_KEY=your_coingecko_api_key
TRADINGECONOMICS_API_KEY=your_trading_economics_api_key

# Payments
NOWPAYMENTS_API_KEY=your_nowpayments_api_key
BTCPAY_API_KEY=your_btcpay_api_key
BTCPAY_URL=https://your-btcpay-server.com

# Domain
DOMAIN=your-domain.com
```

### 4. إعداد SSL Certificate

```bash
# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com

# نسخ الشهادات
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
sudo chown cryptosignals:cryptosignals nginx/ssl/*
```

### 5. بناء وتشغيل الخدمات

```bash
# بناء الصور
docker-compose -f docker-compose.prod.yml build

# تشغيل قاعدة البيانات أولاً
docker-compose -f docker-compose.prod.yml up -d database redis

# انتظار تشغيل قاعدة البيانات
sleep 30

# تشغيل باقي الخدمات
docker-compose -f docker-compose.prod.yml up -d
```

### 6. التحقق من التشغيل

```bash
# فحص حالة الخدمات
docker-compose -f docker-compose.prod.yml ps

# فحص السجلات
docker-compose -f docker-compose.prod.yml logs -f

# اختبار الصحة
curl -f https://your-domain.com/health
curl -f https://your-domain.com/api/health
```

## إعداد المراقبة (اختياري)

```bash
# تشغيل خدمات المراقبة
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# الوصول للمراقبة
# Prometheus: http://your-domain.com:9090
# Grafana: http://your-domain.com:3001
```

## النسخ الاحتياطية

### إعداد النسخ الاحتياطية التلقائية:

```bash
# إنشاء سكريبت النسخ الاحتياطي
cat > /opt/crypto-signals/scripts/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/crypto-signals/backups"
mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
docker exec crypto_signals_db_prod pg_dump -U crypto_user crypto_signals | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# نسخ احتياطي للملفات
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /opt/crypto-signals --exclude=/opt/crypto-signals/backups

# حذف النسخ القديمة (أكثر من 7 أيام)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/crypto-signals/scripts/backup.sh

# إضافة مهمة cron للنسخ الاحتياطي اليومي
echo "0 2 * * * /opt/crypto-signals/scripts/backup.sh" | crontab -
```

## الصيانة

### تحديث النظام:

```bash
# إيقاف الخدمات
docker-compose -f docker-compose.prod.yml down

# تحديث الكود
git pull origin main

# إعادة بناء الصور
docker-compose -f docker-compose.prod.yml build

# تشغيل الخدمات
docker-compose -f docker-compose.prod.yml up -d
```

### مراقبة الأداء:

```bash
# مراقبة استخدام الموارد
docker stats

# فحص السجلات
docker-compose -f docker-compose.prod.yml logs -f [service_name]

# فحص مساحة القرص
df -h
docker system df
```

## استكشاف الأخطاء

### مشاكل شائعة:

1. **خطأ في الاتصال بقاعدة البيانات:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs database
   ```

2. **مشاكل SSL:**
   ```bash
   sudo certbot renew --dry-run
   ```

3. **نفاد مساحة القرص:**
   ```bash
   docker system prune -a
   ```

4. **مشاكل الذاكرة:**
   ```bash
   docker-compose -f docker-compose.prod.yml restart
   ```

## الأمان

### إعدادات الأمان الموصى بها:

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# إعداد جدار الحماية
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# تعطيل تسجيل الدخول بـ root
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# إعداد fail2ban
sudo apt install fail2ban -y
```

## الدعم

للحصول على الدعم:
- راجع ملف `TROUBLESHOOTING.md`
- تحقق من السجلات في `/opt/crypto-signals/logs/`
- تواصل مع فريق التطوير

---

**ملاحظة:** تأكد من تحديث جميع كلمات المرور والمفاتيح قبل النشر في الإنتاج.

