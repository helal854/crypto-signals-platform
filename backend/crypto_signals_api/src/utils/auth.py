from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from jose import JWTError, jwt
from src.models.user import User

class AuthManager:
    @staticmethod
    def generate_token(user_id, role):
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=current_app.config.get('JWT_EXPIRATION_HOURS', 24)),
            'iat': datetime.utcnow()
        }
        
        secret = current_app.config.get('JWT_SECRET', 'default-secret')
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        return jwt.encode(payload, secret, algorithm=algorithm)
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return payload"""
        try:
            secret = current_app.config.get('JWT_SECRET', 'default-secret')
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            payload = jwt.decode(token, secret, algorithms=[algorithm])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def get_current_user():
        """Get current user from request token"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
            payload = AuthManager.verify_token(token)
            if not payload:
                return None
            
            user = User.query.get(payload['user_id'])
            return user
        except (IndexError, KeyError):
            return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = AuthManager.get_current_user()
        if not user:
            return jsonify({'error': 'Token is missing or invalid'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'User account is disabled'}), 401
        
        return f(current_user=user, *args, **kwargs)
    return decorated

def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = AuthManager.get_current_user()
            if not user:
                return jsonify({'error': 'Token is missing or invalid'}), 401
            
            if not user.is_active:
                return jsonify({'error': 'User account is disabled'}), 401
            
            if user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(current_user=user, *args, **kwargs)
        return decorated
    return decorator

def permission_required(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = AuthManager.get_current_user()
            if not user:
                return jsonify({'error': 'Token is missing or invalid'}), 401
            
            if not user.is_active:
                return jsonify({'error': 'User account is disabled'}), 401
            
            if not user.has_permission(permission):
                return jsonify({'error': f'Permission {permission} required'}), 403
            
            return f(current_user=user, *args, **kwargs)
        return decorated
    return decorator

def get_client_info():
    """Get client IP and user agent from request"""
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    return ip_address, user_agent

