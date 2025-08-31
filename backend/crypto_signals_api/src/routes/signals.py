from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models import db
from src.models.spot_signal import SpotSignal
from src.models.futures_signal import FuturesSignal
from src.models.audit_log import AuditLog
from src.utils.auth import token_required, permission_required, get_client_info

signals_bp = Blueprint('signals', __name__)

# Spot Signals Routes
@signals_bp.route('/spot', methods=['GET'])
@token_required
def get_spot_signals(current_user):
    """Get spot signals with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status', 'active')
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = SpotSignal.query
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        if symbol:
            query = query.filter_by(symbol=symbol.upper())
        
        # Order by creation date (newest first)
        signals = query.order_by(SpotSignal.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'signals': [signal.to_dict() for signal in signals],
            'total': query.count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch spot signals', 'details': str(e)}), 500

@signals_bp.route('/spot', methods=['POST'])
@permission_required('manage_signals')
def create_spot_signal(current_user):
    """Create new spot signal"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['symbol', 'side']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create signal
        signal = SpotSignal(
            symbol=data['symbol'],
            side=data['side'],
            entry_min=data.get('entry_min'),
            entry_max=data.get('entry_max'),
            target_1=data.get('target_1'),
            target_2=data.get('target_2'),
            target_3=data.get('target_3'),
            target_4=data.get('target_4'),
            target_5=data.get('target_5'),
            stop_loss=data.get('stop_loss'),
            support_level=data.get('support_level'),
            resistance_level=data.get('resistance_level')
        )
        
        # Validate signal
        is_valid, errors = signal.validate_signal()
        if not is_valid:
            return jsonify({'error': 'Invalid signal data', 'details': errors}), 400
        
        db.session.add(signal)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_create(
            user_id=current_user.id,
            table_name='spot_signals',
            record_id=signal.id,
            new_values=signal.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Spot signal created successfully',
            'signal': signal.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create spot signal', 'details': str(e)}), 500

@signals_bp.route('/spot/<signal_id>', methods=['PUT'])
@permission_required('manage_signals')
def update_spot_signal(current_user, signal_id):
    """Update spot signal"""
    try:
        signal = SpotSignal.query.get(signal_id)
        
        if not signal:
            return jsonify({'error': 'Signal not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Store old values for audit
        old_values = signal.to_dict()
        
        # Update fields
        updatable_fields = [
            'symbol', 'side', 'entry_min', 'entry_max',
            'target_1', 'target_2', 'target_3', 'target_4', 'target_5',
            'stop_loss', 'support_level', 'resistance_level', 'status'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(signal, field, data[field])
        
        # Validate updated signal
        is_valid, errors = signal.validate_signal()
        if not is_valid:
            return jsonify({'error': 'Invalid signal data', 'details': errors}), 400
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_update(
            user_id=current_user.id,
            table_name='spot_signals',
            record_id=signal.id,
            old_values=old_values,
            new_values=signal.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Spot signal updated successfully',
            'signal': signal.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update spot signal', 'details': str(e)}), 500

@signals_bp.route('/spot/<signal_id>/send', methods=['POST'])
@permission_required('manage_signals')
def send_spot_signal(current_user, signal_id):
    """Mark spot signal as sent"""
    try:
        signal = SpotSignal.query.get(signal_id)
        
        if not signal:
            return jsonify({'error': 'Signal not found'}), 404
        
        if signal.status != 'active':
            return jsonify({'error': 'Signal is not active'}), 400
        
        # Mark as sent
        signal.mark_as_sent()
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='SEND_SPOT_SIGNAL',
            table_name='spot_signals',
            record_id=signal.id,
            new_values={'status': 'sent', 'sent_at': signal.sent_at.isoformat()},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Spot signal marked as sent',
            'signal': signal.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send spot signal', 'details': str(e)}), 500

# Futures Signals Routes
@signals_bp.route('/futures', methods=['GET'])
@token_required
def get_futures_signals(current_user):
    """Get futures signals with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status', 'active')
        symbol = request.args.get('symbol')
        trader = request.args.get('trader')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = FuturesSignal.query
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        if symbol:
            query = query.filter_by(symbol=symbol.upper())
        
        if trader:
            query = query.filter_by(binance_trader_id=trader)
        
        # Order by creation date (newest first)
        signals = query.order_by(FuturesSignal.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'signals': [signal.to_dict() for signal in signals],
            'total': query.count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch futures signals', 'details': str(e)}), 500

@signals_bp.route('/futures', methods=['POST'])
@permission_required('manage_futures')
def create_futures_signal(current_user):
    """Create new futures signal"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['symbol', 'side', 'entry_price', 'trader_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create signal
        signal = FuturesSignal(
            symbol=data['symbol'],
            side=data['side'],
            entry_price=data['entry_price'],
            trader_name=data['trader_name'],
            target_1=data.get('target_1'),
            target_2=data.get('target_2'),
            stop_loss=data.get('stop_loss'),
            leverage=data.get('leverage', 1),
            position_value=data.get('position_value'),
            trader_profile_url=data.get('trader_profile_url'),
            binance_trader_id=data.get('binance_trader_id')
        )
        
        # Auto-calculate targets if not provided
        if not signal.target_1 or not signal.target_2:
            signal.calculate_targets_from_entry()
        
        # Auto-calculate stop loss if not provided
        if not signal.stop_loss:
            signal.calculate_stop_loss_from_entry()
        
        # Apply risk limits
        signal.apply_risk_limits()
        
        # Validate signal
        is_valid, errors = signal.validate_signal()
        if not is_valid:
            return jsonify({'error': 'Invalid signal data', 'details': errors}), 400
        
        db.session.add(signal)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_create(
            user_id=current_user.id,
            table_name='futures_signals',
            record_id=signal.id,
            new_values=signal.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Futures signal created successfully',
            'signal': signal.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create futures signal', 'details': str(e)}), 500

@signals_bp.route('/futures/<signal_id>/send', methods=['POST'])
@permission_required('manage_futures')
def send_futures_signal(current_user, signal_id):
    """Mark futures signal as sent"""
    try:
        signal = FuturesSignal.query.get(signal_id)
        
        if not signal:
            return jsonify({'error': 'Signal not found'}), 404
        
        if signal.status != 'active':
            return jsonify({'error': 'Signal is not active'}), 400
        
        # Mark as sent
        signal.mark_as_sent()
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='SEND_FUTURES_SIGNAL',
            table_name='futures_signals',
            record_id=signal.id,
            new_values={'status': 'sent', 'sent_at': signal.sent_at.isoformat()},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Futures signal marked as sent',
            'signal': signal.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send futures signal', 'details': str(e)}), 500

# Statistics Routes
@signals_bp.route('/stats', methods=['GET'])
@token_required
def get_signals_stats(current_user):
    """Get signals statistics"""
    try:
        # Get date range (default: last 7 days)
        days = int(request.args.get('days', 7))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Spot signals stats
        spot_total = SpotSignal.query.filter(SpotSignal.created_at >= start_date).count()
        spot_sent = SpotSignal.query.filter(
            SpotSignal.created_at >= start_date,
            SpotSignal.status == 'sent'
        ).count()
        
        # Futures signals stats
        futures_total = FuturesSignal.query.filter(FuturesSignal.created_at >= start_date).count()
        futures_sent = FuturesSignal.query.filter(
            FuturesSignal.created_at >= start_date,
            FuturesSignal.status == 'sent'
        ).count()
        
        # Today's stats
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        spot_today = SpotSignal.query.filter(SpotSignal.created_at >= today_start).count()
        futures_today = FuturesSignal.query.filter(FuturesSignal.created_at >= today_start).count()
        
        return jsonify({
            'period_days': days,
            'spot_signals': {
                'total': spot_total,
                'sent': spot_sent,
                'today': spot_today
            },
            'futures_signals': {
                'total': futures_total,
                'sent': futures_sent,
                'today': futures_today
            },
            'total_signals': {
                'total': spot_total + futures_total,
                'sent': spot_sent + futures_sent,
                'today': spot_today + futures_today
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch signals statistics', 'details': str(e)}), 500

@signals_bp.route('/latest', methods=['GET'])
@token_required
def get_latest_signals(current_user):
    """Get latest signals for dashboard"""
    try:
        limit = int(request.args.get('limit', 5))
        
        # Get latest spot signals
        latest_spot = SpotSignal.query.order_by(SpotSignal.created_at.desc()).limit(limit).all()
        
        # Get latest futures signals
        latest_futures = FuturesSignal.query.order_by(FuturesSignal.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'spot_signals': [signal.to_dict() for signal in latest_spot],
            'futures_signals': [signal.to_dict() for signal in latest_futures]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch latest signals', 'details': str(e)}), 500

