from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models import db
from src.models.payment import Payment
from src.models.telegram_user import TelegramUser
from src.models.audit_log import AuditLog
from src.utils.auth import token_required, permission_required, get_client_info

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/', methods=['GET'])
@token_required
def get_payments(current_user):
    """Get payments with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        provider = request.args.get('provider')
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Payment.query
        
        if status:
            query = query.filter_by(status=status)
        
        if provider:
            query = query.filter_by(provider=provider)
        
        if user_id:
            query = query.filter_by(user_id=int(user_id))
        
        # Order by creation date (newest first)
        total = query.count()
        payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch payments', 'details': str(e)}), 500

@payments_bp.route('/<payment_id>', methods=['GET'])
@token_required
def get_payment(current_user, payment_id):
    """Get specific payment"""
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({'payment': payment.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch payment', 'details': str(e)}), 500

@payments_bp.route('/', methods=['POST'])
@permission_required('manage_payments')
def create_payment(current_user):
    """Create new payment"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['user_id', 'provider', 'amount', 'currency']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify user exists
        user = TelegramUser.query.filter_by(user_id=data['user_id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create payment
        payment = Payment(
            user_id=data['user_id'],
            provider=data['provider'],
            amount=data['amount'],
            currency=data['currency'],
            transaction_id=data.get('transaction_id'),
            payment_data=data.get('payment_data', {})
        )
        
        db.session.add(payment)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_create(
            user_id=current_user.id,
            table_name='payments',
            record_id=payment.id,
            new_values=payment.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment created successfully',
            'payment': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create payment', 'details': str(e)}), 500

@payments_bp.route('/<payment_id>/sync', methods=['POST'])
@permission_required('manage_payments')
def sync_payment(current_user, payment_id):
    """Sync payment status with provider"""
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Store old status for audit
        old_status = payment.status
        
        # Here you would implement actual sync logic with payment providers
        # For now, we'll simulate a sync operation
        
        # Simulate sync result (in real implementation, this would call provider API)
        import random
        sync_results = ['completed', 'pending', 'failed']
        new_status = random.choice(sync_results)
        
        # Update payment status
        payment.update_status(new_status)
        
        # Update payment data with sync info
        payment_data = payment.get_payment_data()
        payment_data['last_sync'] = datetime.utcnow().isoformat()
        payment_data['sync_result'] = 'success'
        payment.set_payment_data(payment_data)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='SYNC_PAYMENT',
            table_name='payments',
            record_id=payment.id,
            old_values={'status': old_status},
            new_values={'status': payment.status, 'synced_at': datetime.utcnow().isoformat()},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment synced successfully',
            'payment': payment.to_dict(),
            'status_changed': old_status != payment.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to sync payment', 'details': str(e)}), 500

@payments_bp.route('/<payment_id>/cancel', methods=['POST'])
@permission_required('manage_payments')
def cancel_payment(current_user, payment_id):
    """Cancel payment"""
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if payment.status not in ['pending']:
            return jsonify({'error': 'Only pending payments can be cancelled'}), 400
        
        data = request.get_json() or {}
        reason = data.get('reason', 'Cancelled by admin')
        
        # Cancel payment
        old_status = payment.status
        payment.cancel(reason)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='CANCEL_PAYMENT',
            table_name='payments',
            record_id=payment.id,
            old_values={'status': old_status},
            new_values={'status': payment.status, 'cancelled_by': current_user.id, 'reason': reason},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment cancelled successfully',
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel payment', 'details': str(e)}), 500

@payments_bp.route('/<payment_id>/force-confirm', methods=['POST'])
@permission_required('manage_payments')
def force_confirm_payment(current_user, payment_id):
    """Force confirm payment (admin override)"""
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if payment.status == 'completed':
            return jsonify({'error': 'Payment is already completed'}), 400
        
        data = request.get_json() or {}
        transaction_id = data.get('transaction_id', f'ADMIN_OVERRIDE_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}')
        
        # Force confirm payment
        old_status = payment.status
        payment.mark_completed(transaction_id)
        
        # Update payment data
        payment_data = payment.get_payment_data()
        payment_data['force_confirmed'] = True
        payment_data['confirmed_by'] = current_user.id
        payment_data['confirmed_at'] = datetime.utcnow().isoformat()
        payment.set_payment_data(payment_data)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='FORCE_CONFIRM_PAYMENT',
            table_name='payments',
            record_id=payment.id,
            old_values={'status': old_status},
            new_values={'status': payment.status, 'confirmed_by': current_user.id, 'transaction_id': transaction_id},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment force confirmed successfully',
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to force confirm payment', 'details': str(e)}), 500

@payments_bp.route('/stats', methods=['GET'])
@token_required
def get_payment_stats(current_user):
    """Get payment statistics"""
    try:
        # Get date range (default: last 30 days)
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total payments
        total_payments = Payment.query.filter(Payment.created_at >= start_date).count()
        
        # Payments by status
        completed_payments = Payment.query.filter(
            Payment.created_at >= start_date,
            Payment.status == 'completed'
        ).count()
        
        pending_payments = Payment.query.filter(
            Payment.created_at >= start_date,
            Payment.status == 'pending'
        ).count()
        
        failed_payments = Payment.query.filter(
            Payment.created_at >= start_date,
            Payment.status == 'failed'
        ).count()
        
        cancelled_payments = Payment.query.filter(
            Payment.created_at >= start_date,
            Payment.status == 'cancelled'
        ).count()
        
        # Total revenue (completed payments only)
        revenue_query = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.created_at >= start_date,
            Payment.status == 'completed'
        ).scalar()
        
        total_revenue = float(revenue_query) if revenue_query else 0
        
        # Today's stats
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        payments_today = Payment.query.filter(Payment.created_at >= today_start).count()
        
        return jsonify({
            'period_days': days,
            'total_payments': total_payments,
            'payments_by_status': {
                'completed': completed_payments,
                'pending': pending_payments,
                'failed': failed_payments,
                'cancelled': cancelled_payments
            },
            'total_revenue': total_revenue,
            'payments_today': payments_today,
            'success_rate': round((completed_payments / total_payments * 100) if total_payments > 0 else 0, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch payment statistics', 'details': str(e)}), 500

@payments_bp.route('/providers', methods=['GET'])
@token_required
def get_payment_providers(current_user):
    """Get available payment providers"""
    try:
        providers = [
            {
                'id': 'nowpayments',
                'name': 'NOWPayments',
                'description': 'Cryptocurrency payment processor',
                'supported_currencies': ['BTC', 'ETH', 'USDT', 'LTC', 'XRP'],
                'fees': '0.5%'
            },
            {
                'id': 'btcpay',
                'name': 'BTCPay Server',
                'description': 'Self-hosted payment processor',
                'supported_currencies': ['BTC', 'LTC'],
                'fees': '0%'
            }
        ]
        
        return jsonify({'providers': providers}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch payment providers', 'details': str(e)}), 500

