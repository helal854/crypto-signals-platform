-- Database initialization script for Crypto Signals Platform
-- This script creates the necessary tables and initial data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (for admin panel authentication)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'support' CHECK (role IN ('admin', 'moderator', 'support')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Telegram users table (bot subscribers)
CREATE TABLE IF NOT EXISTS telegram_users (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    subscription_type VARCHAR(20) DEFAULT 'free' CHECK (subscription_type IN ('free', 'pro', 'elite')),
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Integrations table (API keys storage)
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider VARCHAR(50) NOT NULL,
    encrypted_api_key TEXT,
    encrypted_secret_key TEXT,
    is_active BOOLEAN DEFAULT false,
    last_tested TIMESTAMP WITH TIME ZONE,
    test_result VARCHAR(20) CHECK (test_result IN ('success', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider)
);

-- Message templates table
CREATE TABLE IF NOT EXISTS message_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    identifier VARCHAR(50) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    template_type VARCHAR(20) DEFAULT 'general' CHECK (template_type IN ('general', 'spot', 'futures', 'broadcast')),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spot signals table
CREATE TABLE IF NOT EXISTS spot_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('LONG', 'SHORT')),
    entry_min DECIMAL(20, 8),
    entry_max DECIMAL(20, 8),
    target_1 DECIMAL(20, 8),
    target_2 DECIMAL(20, 8),
    target_3 DECIMAL(20, 8),
    target_4 DECIMAL(20, 8),
    target_5 DECIMAL(20, 8),
    stop_loss DECIMAL(20, 8),
    support_level DECIMAL(20, 8),
    resistance_level DECIMAL(20, 8),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE
);

-- Futures signals table
CREATE TABLE IF NOT EXISTS futures_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('LONG', 'SHORT')),
    entry_price DECIMAL(20, 8),
    target_1 DECIMAL(20, 8),
    target_2 DECIMAL(20, 8),
    stop_loss DECIMAL(20, 8),
    leverage INTEGER DEFAULT 1,
    position_value DECIMAL(20, 2),
    trader_name VARCHAR(100),
    trader_profile_url TEXT,
    binance_trader_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES telegram_users(user_id),
    provider VARCHAR(50) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    transaction_id VARCHAR(255),
    payment_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Broadcast messages table
CREATE TABLE IF NOT EXISTS broadcast_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    target_audience VARCHAR(20) DEFAULT 'all' CHECK (target_audience IN ('all', 'free', 'pro', 'elite')),
    sent_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'prepared', 'sent', 'failed')),
    confirm_token VARCHAR(10),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE
);

-- Futures settings table
CREATE TABLE IF NOT EXISTS futures_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Futures traders table (from Binance Leaderboard)
CREATE TABLE IF NOT EXISTS futures_traders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    binance_trader_id VARCHAR(100) UNIQUE NOT NULL,
    trader_name VARCHAR(100),
    profile_url TEXT,
    roi_7d DECIMAL(10, 4),
    pnl_7d DECIMAL(20, 2),
    win_rate DECIMAL(5, 2),
    is_followed BOOLEAN DEFAULT false,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table (for admin actions)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_telegram_users_user_id ON telegram_users(user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_subscription ON telegram_users(subscription_type);
CREATE INDEX IF NOT EXISTS idx_spot_signals_symbol ON spot_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_spot_signals_status ON spot_signals(status);
CREATE INDEX IF NOT EXISTS idx_futures_signals_symbol ON futures_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_futures_signals_trader ON futures_signals(binance_trader_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Insert default admin user (password: admin123)
-- Note: In production, this should be changed immediately
INSERT INTO users (username, email, password_hash, role) 
VALUES ('admin', 'admin@crypto-signals.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5W', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Insert default futures settings
INSERT INTO futures_settings (setting_key, setting_value, description) VALUES
('leaderboard_source', 'binance', 'Source for futures signals (binance leaderboard)'),
('ranking_criteria', 'roi', 'Ranking criteria: roi or pnl'),
('update_interval', '15', 'Update interval in minutes'),
('max_leverage', '10', 'Maximum allowed leverage'),
('max_position_value', '1000', 'Maximum position value in USDT'),
('daily_signal_cap', '20', 'Maximum signals per day'),
('target_1_percent', '0.6', 'Target 1 percentage from entry'),
('target_2_percent', '1.2', 'Target 2 percentage from entry'),
('stop_loss_percent', '0.8', 'Stop loss percentage from entry'),
('default_position_value', '500', 'Default position value in USDT')
ON CONFLICT (setting_key) DO NOTHING;

-- Insert default message templates
INSERT INTO message_templates (name, identifier, content, template_type) VALUES
('Spot Signal Template', 'spot_signal', '**{symbol} - {side}** 🟢

**نطاق الدخول:** {entry_min} - {entry_max}

1️⃣ **الهدف الأول:** {target_1}
2️⃣ **الهدف الثاني:** {target_2}
3️⃣ **الهدف الثالث:** {target_3}
4️⃣ **الهدف الرابع:** {target_4}
5️⃣ **الهدف الخامس:** {target_5}

🧯 **وقف الخسارة:** {stop_loss}

**الدعم:** {support}
**المقاومة:** {resistance}

*الصفقه ليست نصيحه استثماريه يرجى التحليل قبل الشراء.*', 'spot'),

('Futures Signal Template', 'futures_signal', '⚡️ **صفقة Futures ({side})**
**زوج:** {symbol}
**الدخول:** {entry_price}
🎯 **T1:** {target_1}
🎯 **T2:** {target_2}
🧯 **وقف الخسارة:** {stop_loss}
📌 **الرافعة:** ×{leverage}   💵 **قيمة الصفقة:** {position_value} USDT
🕒 **وقت الصفقة:** {timestamp}
👤 **المتداول:** <a href="{trader_profile_url}">{trader_name}</a>

*الصفقه ليست نصيحه استثماريه يرجى التحليل قبل الشراء*', 'futures')
ON CONFLICT (identifier) DO NOTHING;

