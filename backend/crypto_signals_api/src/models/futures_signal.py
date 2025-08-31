from datetime import datetime
from decimal import Decimal
from . import db

class FuturesSignal(db.Model):
    __tablename__ = 'futures_signals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # LONG or SHORT
    entry_price = db.Column(db.Numeric(20, 8))
    target_1 = db.Column(db.Numeric(20, 8))
    target_2 = db.Column(db.Numeric(20, 8))
    stop_loss = db.Column(db.Numeric(20, 8))
    leverage = db.Column(db.Integer, default=1)
    position_value = db.Column(db.Numeric(20, 2))
    trader_name = db.Column(db.String(100))
    trader_profile_url = db.Column(db.Text)
    binance_trader_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    def __init__(self, symbol, side, entry_price, trader_name=None, **kwargs):
        self.symbol = symbol.upper()
        self.side = side.upper()
        self.entry_price = Decimal(str(entry_price))
        self.trader_name = trader_name
        
        # Set targets
        if 'target_1' in kwargs:
            self.target_1 = Decimal(str(kwargs['target_1']))
        if 'target_2' in kwargs:
            self.target_2 = Decimal(str(kwargs['target_2']))
        
        # Set other fields
        if 'stop_loss' in kwargs:
            self.stop_loss = Decimal(str(kwargs['stop_loss']))
        if 'leverage' in kwargs:
            self.leverage = int(kwargs['leverage'])
        if 'position_value' in kwargs:
            self.position_value = Decimal(str(kwargs['position_value']))
        if 'trader_profile_url' in kwargs:
            self.trader_profile_url = kwargs['trader_profile_url']
        if 'binance_trader_id' in kwargs:
            self.binance_trader_id = kwargs['binance_trader_id']
    
    def calculate_targets_from_entry(self, target_1_percent=0.6, target_2_percent=1.2):
        """Calculate targets based on entry price and percentages"""
        if not self.entry_price:
            return
        
        entry = float(self.entry_price)
        multiplier = 1 if self.side == 'LONG' else -1
        
        self.target_1 = Decimal(str(entry * (1 + (target_1_percent / 100) * multiplier)))
        self.target_2 = Decimal(str(entry * (1 + (target_2_percent / 100) * multiplier)))
    
    def calculate_stop_loss_from_entry(self, stop_loss_percent=0.8):
        """Calculate stop loss based on entry price and percentage"""
        if not self.entry_price:
            return
        
        entry = float(self.entry_price)
        multiplier = -1 if self.side == 'LONG' else 1
        
        self.stop_loss = Decimal(str(entry * (1 + (stop_loss_percent / 100) * multiplier)))
    
    def apply_risk_limits(self, max_leverage=10, max_position_value=1000):
        """Apply risk management limits"""
        if self.leverage and self.leverage > max_leverage:
            self.leverage = max_leverage
        
        if self.position_value and float(self.position_value) > max_position_value:
            self.position_value = Decimal(str(max_position_value))
    
    def mark_as_sent(self):
        """Mark signal as sent"""
        self.sent_at = datetime.utcnow()
        self.status = 'sent'
    
    def get_formatted_timestamp(self):
        """Get formatted timestamp for display"""
        if self.created_at:
            return self.created_at.strftime("%Y-%m-%d %H:%M UTC")
        return ""
    
    def validate_signal(self):
        """Validate signal data"""
        errors = []
        
        if not self.symbol:
            errors.append("Symbol is required")
        
        if self.side not in ['LONG', 'SHORT']:
            errors.append("Side must be LONG or SHORT")
        
        if not self.entry_price:
            errors.append("Entry price is required")
        
        if not self.target_1 and not self.target_2:
            errors.append("At least one target is required")
        
        if not self.stop_loss:
            errors.append("Stop loss is required")
        
        if not self.trader_name:
            errors.append("Trader name is required")
        
        return len(errors) == 0, errors
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': float(self.entry_price) if self.entry_price else None,
            'target_1': float(self.target_1) if self.target_1 else None,
            'target_2': float(self.target_2) if self.target_2 else None,
            'stop_loss': float(self.stop_loss) if self.stop_loss else None,
            'leverage': self.leverage,
            'position_value': float(self.position_value) if self.position_value else None,
            'trader_name': self.trader_name,
            'trader_profile_url': self.trader_profile_url,
            'binance_trader_id': self.binance_trader_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'formatted_timestamp': self.get_formatted_timestamp()
        }
    
    def __repr__(self):
        return f'<FuturesSignal {self.symbol} {self.side} by {self.trader_name}>'

