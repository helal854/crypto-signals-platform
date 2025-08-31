from datetime import datetime
from . import db

class TelegramUser(db.Model):
    __tablename__ = 'telegram_users'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    subscription_type = db.Column(db.String(20), default='free')
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='telegram_user', lazy=True)
    
    def __init__(self, user_id, username=None, first_name=None, last_name=None):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def upgrade_subscription(self, new_type):
        """Upgrade user subscription"""
        valid_types = ['free', 'pro', 'elite']
        if new_type in valid_types:
            self.subscription_type = new_type
            return True
        return False
    
    def get_display_name(self):
        """Get user display name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        else:
            return f"User {self.user_id}"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'subscription_type': self.subscription_type,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'display_name': self.get_display_name()
        }
    
    def __repr__(self):
        return f'<TelegramUser {self.user_id}>'

