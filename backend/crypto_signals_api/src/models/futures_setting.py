from datetime import datetime
from . import db

class FuturesSetting(db.Model):
    __tablename__ = 'futures_settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, setting_key, setting_value, description=None, updated_by=None):
        self.setting_key = setting_key
        self.setting_value = setting_value
        self.description = description
        self.updated_by = updated_by
    
    @staticmethod
    def get_setting(key, default=None):
        """Get setting value by key"""
        setting = FuturesSetting.query.filter_by(setting_key=key).first()
        return setting.setting_value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None, updated_by=None):
        """Set or update setting value"""
        setting = FuturesSetting.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = value
            if description:
                setting.description = description
            setting.updated_by = updated_by
            setting.updated_at = datetime.utcnow()
        else:
            setting = FuturesSetting(key, value, description, updated_by)
            db.session.add(setting)
        return setting
    
    @staticmethod
    def get_int_setting(key, default=0):
        """Get setting as integer"""
        value = FuturesSetting.get_setting(key, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_float_setting(key, default=0.0):
        """Get setting as float"""
        value = FuturesSetting.get_setting(key, str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_bool_setting(key, default=False):
        """Get setting as boolean"""
        value = FuturesSetting.get_setting(key, str(default).lower())
        return value.lower() in ['true', '1', 'yes', 'on']
    
    @staticmethod
    def get_all_settings():
        """Get all settings as dictionary"""
        settings = FuturesSetting.query.all()
        return {setting.setting_key: setting.setting_value for setting in settings}
    
    @staticmethod
    def get_leaderboard_settings():
        """Get leaderboard-specific settings"""
        return {
            'source': FuturesSetting.get_setting('leaderboard_source', 'binance'),
            'ranking_criteria': FuturesSetting.get_setting('ranking_criteria', 'roi'),
            'update_interval': FuturesSetting.get_int_setting('update_interval', 15),
            'whitelist': FuturesSetting.get_setting('symbol_whitelist', ''),
            'blacklist': FuturesSetting.get_setting('symbol_blacklist', ''),
            'rate_limit': FuturesSetting.get_int_setting('rate_limit_per_minute', 3)
        }
    
    @staticmethod
    def get_signal_rules():
        """Get signal generation rules"""
        return {
            'target_1_percent': FuturesSetting.get_float_setting('target_1_percent', 0.6),
            'target_2_percent': FuturesSetting.get_float_setting('target_2_percent', 1.2),
            'stop_loss_percent': FuturesSetting.get_float_setting('stop_loss_percent', 0.8),
            'entry_type': FuturesSetting.get_setting('entry_type', 'market'),
            'default_position_value': FuturesSetting.get_float_setting('default_position_value', 500)
        }
    
    @staticmethod
    def get_risk_limits():
        """Get risk management limits"""
        return {
            'max_leverage': FuturesSetting.get_int_setting('max_leverage', 10),
            'max_position_value': FuturesSetting.get_float_setting('max_position_value', 1000),
            'daily_signal_cap': FuturesSetting.get_int_setting('daily_signal_cap', 20),
            'disclaimer': FuturesSetting.get_setting('risk_disclaimer', 'الصفقه ليست نصيحه استثماريه يرجى التحليل قبل الشراء')
        }
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'description': self.description,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<FuturesSetting {self.setting_key}={self.setting_value}>'

