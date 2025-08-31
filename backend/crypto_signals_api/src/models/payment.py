from datetime import datetime
from decimal import Decimal
import json
from . import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = db.Column(db.BigInteger, db.ForeignKey('telegram_users.user_id'))
    provider = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='pending')
    transaction_id = db.Column(db.String(255))
    payment_data = db.Column(db.Text)  # JSON data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, provider, amount, currency, **kwargs):
        self.user_id = user_id
        self.provider = provider
        self.amount = Decimal(str(amount))
        self.currency = currency.upper()
        
        if 'transaction_id' in kwargs:
            self.transaction_id = kwargs['transaction_id']
        if 'payment_data' in kwargs:
            self.set_payment_data(kwargs['payment_data'])
    
    def set_payment_data(self, data):
        """Set payment data as JSON"""
        if isinstance(data, dict):
            self.payment_data = json.dumps(data)
        else:
            self.payment_data = data
    
    def get_payment_data(self):
        """Get payment data as dictionary"""
        if self.payment_data:
            try:
                return json.loads(self.payment_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def update_status(self, new_status, transaction_id=None):
        """Update payment status"""
        valid_statuses = ['pending', 'completed', 'failed', 'cancelled']
        if new_status in valid_statuses:
            self.status = new_status
            if transaction_id:
                self.transaction_id = transaction_id
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def mark_completed(self, transaction_id=None):
        """Mark payment as completed"""
        return self.update_status('completed', transaction_id)
    
    def mark_failed(self, reason=None):
        """Mark payment as failed"""
        if reason:
            data = self.get_payment_data()
            data['failure_reason'] = reason
            self.set_payment_data(data)
        return self.update_status('failed')
    
    def cancel(self, reason=None):
        """Cancel payment"""
        if reason:
            data = self.get_payment_data()
            data['cancellation_reason'] = reason
            self.set_payment_data(data)
        return self.update_status('cancelled')
    
    def get_display_amount(self):
        """Get formatted amount for display"""
        return f"{self.amount} {self.currency}"
    
    def is_pending(self):
        """Check if payment is pending"""
        return self.status == 'pending'
    
    def is_completed(self):
        """Check if payment is completed"""
        return self.status == 'completed'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'amount': float(self.amount),
            'currency': self.currency,
            'display_amount': self.get_display_amount(),
            'status': self.status,
            'transaction_id': self.transaction_id,
            'payment_data': self.get_payment_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Payment {self.id} {self.get_display_amount()} {self.status}>'

