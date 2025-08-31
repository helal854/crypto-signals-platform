from datetime import datetime
import random
import string
from . import db

class BroadcastMessage(db.Model):
    __tablename__ = 'broadcast_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.String(20), default='all')
    sent_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='draft')
    confirm_token = db.Column(db.String(10))
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    def __init__(self, title, content, target_audience='all', created_by=None):
        self.title = title
        self.content = content
        self.target_audience = target_audience
        self.created_by = created_by
    
    def generate_confirm_token(self):
        """Generate random confirmation token"""
        self.confirm_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return self.confirm_token
    
    def prepare_for_sending(self, estimated_targets):
        """Prepare message for sending"""
        self.generate_confirm_token()
        self.status = 'prepared'
        # Store estimated targets for reference
        return {
            'confirm_token': self.confirm_token,
            'preview': self.content,
            'targets_estimate': estimated_targets
        }
    
    def verify_and_send(self, provided_token):
        """Verify token and mark as ready to send"""
        if self.confirm_token and provided_token == self.confirm_token:
            self.status = 'sending'
            self.sent_at = datetime.utcnow()
            return True
        return False
    
    def mark_sent(self, actual_sent_count):
        """Mark message as sent with actual count"""
        self.status = 'sent'
        self.sent_count = actual_sent_count
        if not self.sent_at:
            self.sent_at = datetime.utcnow()
    
    def mark_failed(self, error_reason=None):
        """Mark message as failed"""
        self.status = 'failed'
        # Could store error reason in a separate field if needed
    
    def get_target_filter(self):
        """Get filter criteria for target audience"""
        if self.target_audience == 'all':
            return {}
        elif self.target_audience in ['free', 'pro', 'elite']:
            return {'subscription_type': self.target_audience}
        else:
            return {}
    
    def estimate_targets(self):
        """Estimate number of targets (would query TelegramUser table)"""
        # This would be implemented with actual database query
        # For now, return a placeholder
        from .telegram_user import TelegramUser
        
        filter_criteria = self.get_target_filter()
        if filter_criteria:
            # Would use: TelegramUser.query.filter_by(**filter_criteria, is_active=True).count()
            return 100  # Placeholder
        else:
            # Would use: TelegramUser.query.filter_by(is_active=True).count()
            return 500  # Placeholder
    
    def can_be_sent(self):
        """Check if message can be sent"""
        return self.status in ['draft', 'prepared'] and self.content.strip()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'target_audience': self.target_audience,
            'sent_count': self.sent_count,
            'status': self.status,
            'confirm_token': self.confirm_token if self.status == 'prepared' else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'can_be_sent': self.can_be_sent(),
            'estimated_targets': self.estimate_targets() if self.status == 'draft' else None
        }
    
    def __repr__(self):
        return f'<BroadcastMessage {self.title} {self.status}>'

