from datetime import datetime
from cryptography.fernet import Fernet
import base64
import os
from . import db

class Integration(db.Model):
    __tablename__ = 'integrations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    provider = db.Column(db.String(50), unique=True, nullable=False)
    encrypted_api_key = db.Column(db.Text)
    encrypted_secret_key = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    last_tested = db.Column(db.DateTime)
    test_result = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, provider):
        self.provider = provider
    
    @staticmethod
    def _get_encryption_key():
        """Get or generate encryption key"""
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            # Generate a new key if not provided
            key = Fernet.generate_key().decode()
        
        # Ensure key is properly formatted for Fernet
        try:
            if isinstance(key, str):
                key = key.encode()
            # Pad or truncate to 32 bytes, then base64 encode
            key = base64.urlsafe_b64encode(key[:32].ljust(32, b'0'))
            return key
        except Exception:
            # Fallback to a default key (not secure for production)
            return base64.urlsafe_b64encode(b'default-key-change-in-production'[:32].ljust(32, b'0'))
    
    def set_api_key(self, api_key):
        """Encrypt and store API key"""
        if api_key:
            fernet = Fernet(self._get_encryption_key())
            self.encrypted_api_key = fernet.encrypt(api_key.encode()).decode()
    
    def set_secret_key(self, secret_key):
        """Encrypt and store secret key"""
        if secret_key:
            fernet = Fernet(self._get_encryption_key())
            self.encrypted_secret_key = fernet.encrypt(secret_key.encode()).decode()
    
    def get_api_key(self):
        """Decrypt and return API key"""
        if self.encrypted_api_key:
            try:
                fernet = Fernet(self._get_encryption_key())
                return fernet.decrypt(self.encrypted_api_key.encode()).decode()
            except Exception:
                return None
        return None
    
    def get_secret_key(self):
        """Decrypt and return secret key"""
        if self.encrypted_secret_key:
            try:
                fernet = Fernet(self._get_encryption_key())
                return fernet.decrypt(self.encrypted_secret_key.encode()).decode()
            except Exception:
                return None
        return None
    
    def get_masked_api_key(self):
        """Return masked API key for display"""
        if self.encrypted_api_key:
            return f"{self.provider}_key_********"
        return None
    
    def get_masked_secret_key(self):
        """Return masked secret key for display"""
        if self.encrypted_secret_key:
            return f"{self.provider}_secret_********"
        return None
    
    def update_test_result(self, success, error_message=None):
        """Update test result"""
        self.last_tested = datetime.utcnow()
        self.test_result = 'success' if success else 'failed'
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_keys=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'provider': self.provider,
            'is_active': self.is_active,
            'last_tested': self.last_tested.isoformat() if self.last_tested else None,
            'test_result': self.test_result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_keys:
            # Only include actual keys for internal use
            data['api_key'] = self.get_api_key()
            data['secret_key'] = self.get_secret_key()
        else:
            # Include masked keys for display
            data['masked_api_key'] = self.get_masked_api_key()
            data['masked_secret_key'] = self.get_masked_secret_key()
        
        return data
    
    def __repr__(self):
        return f'<Integration {self.provider}>'

