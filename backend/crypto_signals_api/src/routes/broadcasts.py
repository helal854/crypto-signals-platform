from flask import Blueprint, request, jsonify
from src.models import db
from src.models.broadcast_message import BroadcastMessage
from src.models.telegram_user import TelegramUser
from src.models.audit_log import AuditLog
from src.utils.auth import token_required, permission_required, get_client_info

broadcasts_bp = Blueprint('broadcasts', __name__)

@broadcasts_bp.route('/', methods=['GET'])
@token_required
def get_broadcasts(current_user):
    """Get all broadcast messages"""
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        query = BroadcastMessage.query
        
        if status:
            query = query.filter_by(status=status)
        
        broadcasts = query.order_by(BroadcastMessage.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'broadcasts': [broadcast.to_dict() for broadcast in broadcasts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch broadcasts', 'details': str(e)}), 500

@broadcasts_bp.route('/<broadcast_id>', methods=['GET'])
@token_required
def get_broadcast(current_user, broadcast_id):
    """Get specific broadcast message"""
    try:
        broadcast = BroadcastMessage.query.get(broadcast_id)
        
        if not broadcast:
            return jsonify({'error': 'Broadcast not found'}), 404
        
        return jsonify({'broadcast': broadcast.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch broadcast', 'details': str(e)}), 500

@broadcasts_bp.route('/', methods=['POST'])
@permission_required('manage_broadcasts')
def create_broadcast(current_user):
    """Create new broadcast message"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create broadcast
        broadcast = BroadcastMessage(
            title=data['title'],
            content=data['content'],
            target_audience=data.get('target_audience', 'all'),
            created_by=current_user.id
        )
        
        db.session.add(broadcast)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_create(
            user_id=current_user.id,
            table_name='broadcast_messages',
            record_id=broadcast.id,
            new_values=broadcast.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Broadcast created successfully',
            'broadcast': broadcast.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create broadcast', 'details': str(e)}), 500

@broadcasts_bp.route('/<broadcast_id>', methods=['PUT'])
@permission_required('manage_broadcasts')
def update_broadcast(current_user, broadcast_id):
    """Update broadcast message"""
    try:
        broadcast = BroadcastMessage.query.get(broadcast_id)
        
        if not broadcast:
            return jsonify({'error': 'Broadcast not found'}), 404
        
        if broadcast.status not in ['draft']:
            return jsonify({'error': 'Only draft broadcasts can be edited'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Store old values for audit
        old_values = broadcast.to_dict()
        
        # Update fields
        updatable_fields = ['title', 'content', 'target_audience']
        for field in updatable_fields:
            if field in data:
                setattr(broadcast, field, data[field])
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_update(
            user_id=current_user.id,
            table_name='broadcast_messages',
            record_id=broadcast.id,
            old_values=old_values,
            new_values=broadcast.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Broadcast updated successfully',
            'broadcast': broadcast.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update broadcast', 'details': str(e)}), 500

@broadcasts_bp.route('/<broadcast_id>/prepare', methods=['POST'])
@permission_required('manage_broadcasts')
def prepare_broadcast(current_user, broadcast_id):
    """Prepare broadcast for sending (generate confirmation token)"""
    try:
        broadcast = BroadcastMessage.query.get(broadcast_id)
        
        if not broadcast:
            return jsonify({'error': 'Broadcast not found'}), 404
        
        if not broadcast.can_be_sent():
            return jsonify({'error': 'Broadcast cannot be sent'}), 400
        
        # Get estimated target count
        filter_criteria = broadcast.get_target_filter()
        
        if filter_criteria:
            estimated_targets = TelegramUser.query.filter_by(**filter_criteria, is_active=True).count()
        else:
            estimated_targets = TelegramUser.query.filter_by(is_active=True).count()
        
        # Prepare broadcast
        preparation_data = broadcast.prepare_for_sending(estimated_targets)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='PREPARE_BROADCAST',
            table_name='broadcast_messages',
            record_id=broadcast.id,
            new_values={
                'status': 'prepared',
                'confirm_token': broadcast.confirm_token,
                'estimated_targets': estimated_targets
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Broadcast prepared for sending',
            'broadcast': broadcast.to_dict(),
            'preparation_data': preparation_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to prepare broadcast', 'details': str(e)}), 500

@broadcasts_bp.route('/<broadcast_id>/confirm', methods=['POST'])
@permission_required('manage_broadcasts')
def confirm_broadcast(current_user, broadcast_id):
    """Confirm and send broadcast message"""
    try:
        broadcast = BroadcastMessage.query.get(broadcast_id)
        
        if not broadcast:
            return jsonify({'error': 'Broadcast not found'}), 404
        
        if broadcast.status != 'prepared':
            return jsonify({'error': 'Broadcast must be prepared first'}), 400
        
        data = request.get_json()
        if not data or 'confirm_token' not in data:
            return jsonify({'error': 'Confirmation token is required'}), 400
        
        provided_token = data['confirm_token']
        
        # Verify token and mark as ready to send
        if not broadcast.verify_and_send(provided_token):
            return jsonify({'error': 'Invalid confirmation token'}), 400
        
        # Here you would trigger the actual sending process
        # For now, we'll simulate it by marking as sent
        
        # Get actual target users
        filter_criteria = broadcast.get_target_filter()
        
        if filter_criteria:
            target_users = TelegramUser.query.filter_by(**filter_criteria, is_active=True).all()
        else:
            target_users = TelegramUser.query.filter_by(is_active=True).all()
        
        actual_sent_count = len(target_users)
        
        # Mark as sent
        broadcast.mark_sent(actual_sent_count)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='SEND_BROADCAST',
            table_name='broadcast_messages',
            record_id=broadcast.id,
            new_values={
                'status': 'sent',
                'sent_count': actual_sent_count,
                'sent_at': broadcast.sent_at.isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Broadcast sent successfully',
            'broadcast': broadcast.to_dict(),
            'sent_count': actual_sent_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send broadcast', 'details': str(e)}), 500

@broadcasts_bp.route('/<broadcast_id>', methods=['DELETE'])
@permission_required('delete')
def delete_broadcast(current_user, broadcast_id):
    """Delete broadcast message"""
    try:
        broadcast = BroadcastMessage.query.get(broadcast_id)
        
        if not broadcast:
            return jsonify({'error': 'Broadcast not found'}), 404
        
        if broadcast.status == 'sent':
            return jsonify({'error': 'Cannot delete sent broadcasts'}), 400
        
        # Store data for audit log
        old_values = broadcast.to_dict()
        
        # Log the deletion
        ip_address, user_agent = get_client_info()
        AuditLog.log_delete(
            user_id=current_user.id,
            table_name='broadcast_messages',
            record_id=broadcast.id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Delete broadcast
        db.session.delete(broadcast)
        db.session.commit()
        
        return jsonify({'message': 'Broadcast deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete broadcast', 'details': str(e)}), 500

@broadcasts_bp.route('/audiences', methods=['GET'])
@token_required
def get_target_audiences(current_user):
    """Get available target audiences with counts"""
    try:
        # Get counts for each audience type
        all_users = TelegramUser.query.filter_by(is_active=True).count()
        free_users = TelegramUser.query.filter_by(is_active=True, subscription_type='free').count()
        pro_users = TelegramUser.query.filter_by(is_active=True, subscription_type='pro').count()
        elite_users = TelegramUser.query.filter_by(is_active=True, subscription_type='elite').count()
        
        audiences = [
            {
                'id': 'all',
                'name': 'جميع المستخدمين',
                'description': 'إرسال لجميع المستخدمين النشطين',
                'count': all_users
            },
            {
                'id': 'free',
                'name': 'المستخدمين المجانيين',
                'description': 'المستخدمين بالاشتراك المجاني',
                'count': free_users
            },
            {
                'id': 'pro',
                'name': 'مستخدمي Pro',
                'description': 'المستخدمين بالاشتراك المدفوع Pro',
                'count': pro_users
            },
            {
                'id': 'elite',
                'name': 'مستخدمي Elite',
                'description': 'المستخدمين بالاشتراك المدفوع Elite',
                'count': elite_users
            }
        ]
        
        return jsonify({'audiences': audiences}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch target audiences', 'details': str(e)}), 500

@broadcasts_bp.route('/stats', methods=['GET'])
@token_required
def get_broadcast_stats(current_user):
    """Get broadcast statistics"""
    try:
        # Total broadcasts
        total_broadcasts = BroadcastMessage.query.count()
        
        # Broadcasts by status
        draft_broadcasts = BroadcastMessage.query.filter_by(status='draft').count()
        sent_broadcasts = BroadcastMessage.query.filter_by(status='sent').count()
        failed_broadcasts = BroadcastMessage.query.filter_by(status='failed').count()
        
        # Total messages sent
        total_sent_query = db.session.query(db.func.sum(BroadcastMessage.sent_count)).filter(
            BroadcastMessage.status == 'sent'
        ).scalar()
        
        total_messages_sent = int(total_sent_query) if total_sent_query else 0
        
        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_broadcasts = BroadcastMessage.query.filter(
            BroadcastMessage.created_at >= week_ago
        ).count()
        
        return jsonify({
            'total_broadcasts': total_broadcasts,
            'broadcasts_by_status': {
                'draft': draft_broadcasts,
                'sent': sent_broadcasts,
                'failed': failed_broadcasts
            },
            'total_messages_sent': total_messages_sent,
            'recent_broadcasts': recent_broadcasts
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch broadcast statistics', 'details': str(e)}), 500

