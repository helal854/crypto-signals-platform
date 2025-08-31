from flask import Blueprint, request, jsonify
from src.models import db
from src.models.user import User
from src.models.telegram_user import TelegramUser
from src.models.audit_log import AuditLog
from src.utils.auth import token_required, permission_required, get_client_info

users_bp = Blueprint('users', __name__)

# Admin Users Routes
@users_bp.route('/admin', methods=['GET'])
@permission_required('manage_users')
def get_admin_users(current_user):
    """Get all admin users"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch admin users', 'details': str(e)}), 500

@users_bp.route('/admin/<user_id>', methods=['GET'])
@permission_required('manage_users')
def get_admin_user(current_user, user_id):
    """Get specific admin user"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user', 'details': str(e)}), 500

@users_bp.route('/admin', methods=['POST'])
@permission_required('manage_users')
def create_admin_user(current_user):
    """Create new admin user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Validate role
        valid_roles = ['admin', 'moderator', 'support']
        if data['role'] not in valid_roles:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data['role']
        )
        
        db.session.add(user)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_create(
            user_id=current_user.id,
            table_name='users',
            record_id=user.id,
            new_values=user.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Admin user created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create admin user', 'details': str(e)}), 500

@users_bp.route('/admin/<user_id>', methods=['PUT'])
@permission_required('manage_users')
def update_admin_user(current_user, user_id):
    """Update admin user"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Store old values for audit
        old_values = user.to_dict()
        
        # Update fields
        if 'username' in data:
            # Check if new username already exists
            existing = User.query.filter(
                User.username == data['username'],
                User.id != user_id
            ).first()
            if existing:
                return jsonify({'error': 'Username already exists'}), 400
            user.username = data['username']
        
        if 'email' in data:
            # Check if new email already exists
            existing = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
        
        if 'role' in data:
            valid_roles = ['admin', 'moderator', 'support']
            if data['role'] not in valid_roles:
                return jsonify({'error': 'Invalid role'}), 400
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_update(
            user_id=current_user.id,
            table_name='users',
            record_id=user.id,
            old_values=old_values,
            new_values=user.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Admin user updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update admin user', 'details': str(e)}), 500

# Telegram Users Routes
@users_bp.route('/telegram', methods=['GET'])
@token_required
def get_telegram_users(current_user):
    """Get telegram users with optional filtering"""
    try:
        # Get query parameters
        subscription_type = request.args.get('subscription_type')
        is_active = request.args.get('is_active')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        query = TelegramUser.query
        
        if subscription_type:
            query = query.filter_by(subscription_type=subscription_type)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        total = query.count()
        users = query.order_by(TelegramUser.joined_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch telegram users', 'details': str(e)}), 500

@users_bp.route('/telegram/<int:user_id>', methods=['GET'])
@token_required
def get_telegram_user(current_user, user_id):
    """Get specific telegram user"""
    try:
        user = TelegramUser.query.filter_by(user_id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch telegram user', 'details': str(e)}), 500

@users_bp.route('/telegram/<int:user_id>/subscription', methods=['PUT'])
@permission_required('manage_users_basic')
def update_telegram_user_subscription(current_user, user_id):
    """Update telegram user subscription"""
    try:
        user = TelegramUser.query.filter_by(user_id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data or 'subscription_type' not in data:
            return jsonify({'error': 'subscription_type is required'}), 400
        
        old_subscription = user.subscription_type
        new_subscription = data['subscription_type']
        
        # Update subscription
        if user.upgrade_subscription(new_subscription):
            # Log the action
            ip_address, user_agent = get_client_info()
            AuditLog.log_action(
                user_id=current_user.id,
                action='UPDATE_TELEGRAM_USER_SUBSCRIPTION',
                table_name='telegram_users',
                record_id=str(user.user_id),
                old_values={'subscription_type': old_subscription},
                new_values={'subscription_type': new_subscription},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.commit()
            
            return jsonify({
                'message': 'Subscription updated successfully',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid subscription type'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update subscription', 'details': str(e)}), 500

@users_bp.route('/telegram/<int:user_id>/toggle-active', methods=['POST'])
@permission_required('manage_users_basic')
def toggle_telegram_user_active(current_user, user_id):
    """Toggle telegram user active status"""
    try:
        user = TelegramUser.query.filter_by(user_id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        old_status = user.is_active
        user.is_active = not user.is_active
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='TOGGLE_TELEGRAM_USER_ACTIVE',
            table_name='telegram_users',
            record_id=str(user.user_id),
            old_values={'is_active': old_status},
            new_values={'is_active': user.is_active},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to toggle user status', 'details': str(e)}), 500

@users_bp.route('/stats', methods=['GET'])
@token_required
def get_users_stats(current_user):
    """Get users statistics"""
    try:
        # Admin users stats
        total_admin_users = User.query.count()
        active_admin_users = User.query.filter_by(is_active=True).count()
        
        admin_by_role = {
            'admin': User.query.filter_by(role='admin').count(),
            'moderator': User.query.filter_by(role='moderator').count(),
            'support': User.query.filter_by(role='support').count()
        }
        
        # Telegram users stats
        total_telegram_users = TelegramUser.query.count()
        active_telegram_users = TelegramUser.query.filter_by(is_active=True).count()
        
        telegram_by_subscription = {
            'free': TelegramUser.query.filter_by(subscription_type='free').count(),
            'pro': TelegramUser.query.filter_by(subscription_type='pro').count(),
            'elite': TelegramUser.query.filter_by(subscription_type='elite').count()
        }
        
        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        new_telegram_users = TelegramUser.query.filter(
            TelegramUser.joined_at >= week_ago
        ).count()
        
        return jsonify({
            'admin_users': {
                'total': total_admin_users,
                'active': active_admin_users,
                'by_role': admin_by_role
            },
            'telegram_users': {
                'total': total_telegram_users,
                'active': active_telegram_users,
                'by_subscription': telegram_by_subscription,
                'new_this_week': new_telegram_users
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch users statistics', 'details': str(e)}), 500

