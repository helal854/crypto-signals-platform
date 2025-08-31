import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # External APIs
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    TRADING_ECONOMICS_KEY = os.getenv('TRADING_ECONOMICS_KEY', '')
    TE_GUEST = os.getenv('TE_GUEST', 'guest:guest')
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'default-encryption-key-change-in-production')
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Futures Settings
    FUTURES_MAX_LEVERAGE = int(os.getenv('FUTURES_MAX_LEVERAGE', '10'))
    FUTURES_MAX_POSITION_VALUE = float(os.getenv('FUTURES_MAX_POSITION_VALUE', '1000'))
    FUTURES_DAILY_SIGNAL_CAP = int(os.getenv('FUTURES_DAILY_SIGNAL_CAP', '20'))
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

