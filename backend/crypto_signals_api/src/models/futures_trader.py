from datetime import datetime
from decimal import Decimal
from . import db

class FuturesTrader(db.Model):
    __tablename__ = 'futures_traders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    binance_trader_id = db.Column(db.String(100), unique=True, nullable=False)
    trader_name = db.Column(db.String(100))
    profile_url = db.Column(db.Text)
    roi_7d = db.Column(db.Numeric(10, 4))  # ROI percentage
    pnl_7d = db.Column(db.Numeric(20, 2))  # PnL in USDT
    win_rate = db.Column(db.Numeric(5, 2))  # Win rate percentage
    is_followed = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    signals = db.relationship('FuturesSignal', backref='trader', lazy=True, 
                            foreign_keys='FuturesSignal.binance_trader_id',
                            primaryjoin='FuturesTrader.binance_trader_id == foreign(FuturesSignal.binance_trader_id)')
    
    def __init__(self, binance_trader_id, trader_name=None, **kwargs):
        self.binance_trader_id = binance_trader_id
        self.trader_name = trader_name
        
        if 'profile_url' in kwargs:
            self.profile_url = kwargs['profile_url']
        if 'roi_7d' in kwargs:
            self.roi_7d = Decimal(str(kwargs['roi_7d']))
        if 'pnl_7d' in kwargs:
            self.pnl_7d = Decimal(str(kwargs['pnl_7d']))
        if 'win_rate' in kwargs:
            self.win_rate = Decimal(str(kwargs['win_rate']))
    
    def update_stats(self, roi_7d=None, pnl_7d=None, win_rate=None):
        """Update trader statistics"""
        if roi_7d is not None:
            self.roi_7d = Decimal(str(roi_7d))
        if pnl_7d is not None:
            self.pnl_7d = Decimal(str(pnl_7d))
        if win_rate is not None:
            self.win_rate = Decimal(str(win_rate))
        self.last_updated = datetime.utcnow()
    
    def follow(self):
        """Start following this trader"""
        self.is_followed = True
    
    def unfollow(self):
        """Stop following this trader"""
        self.is_followed = False
    
    def toggle_follow(self):
        """Toggle follow status"""
        self.is_followed = not self.is_followed
        return self.is_followed
    
    def get_performance_score(self):
        """Calculate performance score based on ROI and win rate"""
        if not self.roi_7d or not self.win_rate:
            return 0
        
        # Simple scoring: ROI weight 70%, Win rate weight 30%
        roi_score = float(self.roi_7d) * 0.7
        win_rate_score = float(self.win_rate) * 0.3
        return roi_score + win_rate_score
    
    def get_risk_level(self):
        """Determine risk level based on statistics"""
        if not self.roi_7d:
            return 'unknown'
        
        roi = float(self.roi_7d)
        if roi > 50:
            return 'high'
        elif roi > 20:
            return 'medium'
        elif roi > 0:
            return 'low'
        else:
            return 'negative'
    
    def is_data_fresh(self, max_age_hours=24):
        """Check if trader data is fresh"""
        if not self.last_updated:
            return False
        
        age = datetime.utcnow() - self.last_updated
        return age.total_seconds() < (max_age_hours * 3600)
    
    def get_signals_count(self, days=7):
        """Get count of signals from this trader in last N days"""
        # This would require a proper query with date filtering
        # For now, return a placeholder
        return len([s for s in self.signals if s.created_at and 
                   (datetime.utcnow() - s.created_at).days <= days])
    
    @staticmethod
    def get_followed_traders():
        """Get all followed traders"""
        return FuturesTrader.query.filter_by(is_followed=True).all()
    
    @staticmethod
    def get_top_performers(limit=10, criteria='roi'):
        """Get top performing traders"""
        if criteria == 'roi':
            return FuturesTrader.query.order_by(FuturesTrader.roi_7d.desc()).limit(limit).all()
        elif criteria == 'pnl':
            return FuturesTrader.query.order_by(FuturesTrader.pnl_7d.desc()).limit(limit).all()
        else:
            return FuturesTrader.query.order_by(FuturesTrader.win_rate.desc()).limit(limit).all()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'binance_trader_id': self.binance_trader_id,
            'trader_name': self.trader_name,
            'profile_url': self.profile_url,
            'roi_7d': float(self.roi_7d) if self.roi_7d else None,
            'pnl_7d': float(self.pnl_7d) if self.pnl_7d else None,
            'win_rate': float(self.win_rate) if self.win_rate else None,
            'is_followed': self.is_followed,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'performance_score': self.get_performance_score(),
            'risk_level': self.get_risk_level(),
            'is_data_fresh': self.is_data_fresh(),
            'signals_count_7d': self.get_signals_count(7)
        }
    
    def __repr__(self):
        return f'<FuturesTrader {self.trader_name} ({self.binance_trader_id})>'

