from datetime import datetime
import json
from . import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.String(36))
    old_values = db.Column(db.Text)  # JSON
    new_values = db.Column(db.Text)  # JSON
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, action, **kwargs):
        self.user_id = user_id
        self.action = action
        
        if 'table_name' in kwargs:
            self.table_name = kwargs['table_name']
        if 'record_id' in kwargs:
            self.record_id = kwargs['record_id']
        if 'old_values' in kwargs:
            self.set_old_values(kwargs['old_values'])
        if 'new_values' in kwargs:
            self.set_new_values(kwargs['new_values'])
        if 'ip_address' in kwargs:
            self.ip_address = kwargs['ip_address']
        if 'user_agent' in kwargs:
            self.user_agent = kwargs['user_agent']
    
    def set_old_values(self, values):
        """Set old values as JSON"""
        if isinstance(values, dict):
            self.old_values = json.dumps(values, default=str)
        else:
            self.old_values = values
    
    def set_new_values(self, values):
        """Set new values as JSON"""
        if isinstance(values, dict):
            self.new_values = json.dumps(values, default=str)
        else:
            self.new_values = values
    
    def get_old_values(self):
        """Get old values as dictionary"""
        if self.old_values:
            try:
                return json.loads(self.old_values)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_new_values(self):
        """Get new values as dictionary"""
        if self.new_values:
            try:
                return json.loads(self.new_values)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_changes(self):
        """Get dictionary of changes (field -> [old, new])"""
        old_vals = self.get_old_values()
        new_vals = self.get_new_values()
        changes = {}
        
        # Find changed fields
        all_fields = set(old_vals.keys()) | set(new_vals.keys())
        for field in all_fields:
            old_val = old_vals.get(field)
            new_val = new_vals.get(field)
            if old_val != new_val:
                changes[field] = [old_val, new_val]
        
        return changes
    
    @staticmethod
    def log_action(user_id, action, table_name=None, record_id=None, 
                   old_values=None, new_values=None, ip_address=None, user_agent=None):
        """Create new audit log entry"""
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)
        return log_entry
    
    @staticmethod
    def log_create(user_id, table_name, record_id, new_values, ip_address=None, user_agent=None):
        """Log record creation"""
        return AuditLog.log_action(
            user_id=user_id,
            action=f'CREATE_{table_name.upper()}',
            table_name=table_name,
            record_id=record_id,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_update(user_id, table_name, record_id, old_values, new_values, ip_address=None, user_agent=None):
        """Log record update"""
        return AuditLog.log_action(
            user_id=user_id,
            action=f'UPDATE_{table_name.upper()}',
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_delete(user_id, table_name, record_id, old_values, ip_address=None, user_agent=None):
        """Log record deletion"""
        return AuditLog.log_action(
            user_id=user_id,
            action=f'DELETE_{table_name.upper()}',
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'old_values': self.get_old_values(),
            'new_values': self.get_new_values(),
            'changes': self.get_changes(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id}>'

