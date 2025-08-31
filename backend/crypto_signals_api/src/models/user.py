from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='support')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_templates = db.relationship('MessageTemplate', backref='creator', lazy=True)
    created_broadcasts = db.relationship('BroadcastMessage', backref='creator', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    
    def __init__(self, username, email, password, role='support'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users', 'manage_integrations', 'manage_futures'],
            'moderator': ['read', 'write', 'manage_signals', 'manage_broadcasts'],
            'support': ['read', 'manage_users_basic']
        }
        return permission in permissions.get(self.role, [])
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

