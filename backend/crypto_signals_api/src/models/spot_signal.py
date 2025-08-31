from datetime import datetime
from decimal import Decimal
from . import db

class SpotSignal(db.Model):
    __tablename__ = 'spot_signals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # LONG or SHORT
    entry_min = db.Column(db.Numeric(20, 8))
    entry_max = db.Column(db.Numeric(20, 8))
    target_1 = db.Column(db.Numeric(20, 8))
    target_2 = db.Column(db.Numeric(20, 8))
    target_3 = db.Column(db.Numeric(20, 8))
    target_4 = db.Column(db.Numeric(20, 8))
    target_5 = db.Column(db.Numeric(20, 8))
    stop_loss = db.Column(db.Numeric(20, 8))
    support_level = db.Column(db.Numeric(20, 8))
    resistance_level = db.Column(db.Numeric(20, 8))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    def __init__(self, symbol, side, entry_min=None, entry_max=None, **kwargs):
        self.symbol = symbol.upper()
        self.side = side.upper()
        self.entry_min = Decimal(str(entry_min)) if entry_min else None
        self.entry_max = Decimal(str(entry_max)) if entry_max else None
        
        # Set targets
        for i in range(1, 6):
            target_key = f'target_{i}'
            if target_key in kwargs:
                setattr(self, target_key, Decimal(str(kwargs[target_key])))
        
        # Set other fields
        if 'stop_loss' in kwargs:
            self.stop_loss = Decimal(str(kwargs['stop_loss']))
        if 'support_level' in kwargs:
            self.support_level = Decimal(str(kwargs['support_level']))
        if 'resistance_level' in kwargs:
            self.resistance_level = Decimal(str(kwargs['resistance_level']))
    
    def get_entry_range(self):
        """Get entry range as string"""
        if self.entry_min and self.entry_max:
            return f"{self.entry_min} - {self.entry_max}"
        elif self.entry_min:
            return str(self.entry_min)
        return "Market"
    
    def get_targets_list(self):
        """Get list of targets"""
        targets = []
        for i in range(1, 6):
            target = getattr(self, f'target_{i}')
            if target:
                targets.append(float(target))
        return targets
    
    def mark_as_sent(self):
        """Mark signal as sent"""
        self.sent_at = datetime.utcnow()
        self.status = 'sent'
    
    def validate_signal(self):
        """Validate signal data"""
        errors = []
        
        if not self.symbol:
            errors.append("Symbol is required")
        
        if self.side not in ['LONG', 'SHORT']:
            errors.append("Side must be LONG or SHORT")
        
        if not any([getattr(self, f'target_{i}') for i in range(1, 6)]):
            errors.append("At least one target is required")
        
        if not self.stop_loss:
            errors.append("Stop loss is required")
        
        return len(errors) == 0, errors
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_min': float(self.entry_min) if self.entry_min else None,
            'entry_max': float(self.entry_max) if self.entry_max else None,
            'entry_range': self.get_entry_range(),
            'target_1': float(self.target_1) if self.target_1 else None,
            'target_2': float(self.target_2) if self.target_2 else None,
            'target_3': float(self.target_3) if self.target_3 else None,
            'target_4': float(self.target_4) if self.target_4 else None,
            'target_5': float(self.target_5) if self.target_5 else None,
            'targets': self.get_targets_list(),
            'stop_loss': float(self.stop_loss) if self.stop_loss else None,
            'support_level': float(self.support_level) if self.support_level else None,
            'resistance_level': float(self.resistance_level) if self.resistance_level else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
    
    def __repr__(self):
        return f'<SpotSignal {self.symbol} {self.side}>'

