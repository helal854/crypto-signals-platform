from flask import Blueprint, request, jsonify
from src.models import db
from src.models.user import User
from src.models.audit_log import AuditLog
from src.utils.auth import AuthManager, get_client_info

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username']
        password = data['password']
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 401
        
        # Generate token
        token = AuthManager.generate_token(user.id, user.role)
        
        # Log successful login
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=user.id,
            action='LOGIN_SUCCESS',
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.commit()
        
        return jsonify({
            'token': token,
            'user': user.to_dict(),
            'expires_in': 24 * 3600  # 24 hours in seconds
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        # Get current user from token
        user = AuthManager.get_current_user()
        
        if user:
            # Log logout
            ip_address, user_agent = get_client_info()
            AuditLog.log_action(
                user_id=user.id,
                action='LOGOUT',
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.commit()
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    try:
        user = AuthManager.get_current_user()
        
        if not user:
            return jsonify({'error': 'Token is missing or invalid'}), 401
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        user = AuthManager.get_current_user()
        
        if not user:
            return jsonify({'error': 'Token is missing or invalid'}), 401
        
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        user.set_password(new_password)
        
        # Log password change
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=user.id,
            action='PASSWORD_CHANGE',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token validity"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'valid': False, 'error': 'No token provided'}), 400
        
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
            payload = AuthManager.verify_token(token)
            
            if not payload:
                return jsonify({'valid': False, 'error': 'Invalid token'}), 401
            
            # Check if user still exists and is active
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return jsonify({'valid': False, 'error': 'User not found or inactive'}), 401
            
            return jsonify({
                'valid': True,
                'user': user.to_dict(),
                'expires_at': payload.get('exp')
            }), 200
            
        except IndexError:
            return jsonify({'valid': False, 'error': 'Invalid token format'}), 400
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

