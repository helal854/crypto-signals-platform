from flask import Blueprint, request, jsonify
from src.models import db
from src.models.futures_setting import FuturesSetting
from src.models.futures_trader import FuturesTrader
from src.models.futures_signal import FuturesSignal
from src.models.audit_log import AuditLog
from src.utils.auth import token_required, permission_required, get_client_info

futures_bp = Blueprint('futures', __name__)

# Futures Settings Routes
@futures_bp.route('/settings', methods=['GET'])
@permission_required('manage_futures')
def get_futures_settings(current_user):
    """Get all futures settings"""
    try:
        settings = FuturesSetting.get_all_settings()
        
        # Organize settings by category
        organized_settings = {
            'leaderboard': FuturesSetting.get_leaderboard_settings(),
            'signal_rules': FuturesSetting.get_signal_rules(),
            'risk_limits': FuturesSetting.get_risk_limits()
        }
        
        return jsonify({
            'settings': organized_settings,
            'raw_settings': settings
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch futures settings', 'details': str(e)}), 500

@futures_bp.route('/settings', methods=['POST'])
@permission_required('manage_futures')
def update_futures_settings(current_user):
    """Update futures settings"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        updated_settings = []
        
        # Update each setting
        for key, value in data.items():
            setting = FuturesSetting.set_setting(key, str(value), updated_by=current_user.id)
            updated_settings.append(setting.to_dict())
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='UPDATE_FUTURES_SETTINGS',
            table_name='futures_settings',
            new_values=data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Futures settings updated successfully',
            'updated_settings': updated_settings
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update futures settings', 'details': str(e)}), 500

# Futures Traders Routes
@futures_bp.route('/traders', methods=['GET'])
@token_required
def get_futures_traders(current_user):
    """Get futures traders with optional filtering"""
    try:
        # Get query parameters
        followed_only = request.args.get('followed_only', 'false').lower() == 'true'
        sort_by = request.args.get('sort_by', 'roi')  # roi, pnl, win_rate
        limit = int(request.args.get('limit', 50))
        
        query = FuturesTrader.query
        
        if followed_only:
            query = query.filter_by(is_followed=True)
        
        # Sort by specified criteria
        if sort_by == 'roi':
            query = query.order_by(FuturesTrader.roi_7d.desc())
        elif sort_by == 'pnl':
            query = query.order_by(FuturesTrader.pnl_7d.desc())
        elif sort_by == 'win_rate':
            query = query.order_by(FuturesTrader.win_rate.desc())
        else:
            query = query.order_by(FuturesTrader.last_updated.desc())
        
        traders = query.limit(limit).all()
        
        return jsonify({
            'traders': [trader.to_dict() for trader in traders],
            'total': query.count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch futures traders', 'details': str(e)}), 500

@futures_bp.route('/traders/<trader_id>', methods=['GET'])
@token_required
def get_futures_trader(current_user, trader_id):
    """Get specific futures trader"""
    try:
        trader = FuturesTrader.query.get(trader_id)
        
        if not trader:
            return jsonify({'error': 'Trader not found'}), 404
        
        return jsonify({'trader': trader.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch trader', 'details': str(e)}), 500

@futures_bp.route('/traders', methods=['POST'])
@permission_required('manage_futures')
def create_futures_trader(current_user):
    """Create or update futures trader"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if 'binance_trader_id' not in data:
            return jsonify({'error': 'binance_trader_id is required'}), 400
        
        # Check if trader already exists
        existing_trader = FuturesTrader.query.filter_by(
            binance_trader_id=data['binance_trader_id']
        ).first()
        
        if existing_trader:
            # Update existing trader
            trader = existing_trader
            old_values = trader.to_dict()
            
            trader.update_stats(
                roi_7d=data.get('roi_7d'),
                pnl_7d=data.get('pnl_7d'),
                win_rate=data.get('win_rate')
            )
            
            if 'trader_name' in data:
                trader.trader_name = data['trader_name']
            if 'profile_url' in data:
                trader.profile_url = data['profile_url']
            
            action = 'UPDATE_FUTURES_TRADER'
        else:
            # Create new trader
            trader = FuturesTrader(
                binance_trader_id=data['binance_trader_id'],
                trader_name=data.get('trader_name'),
                profile_url=data.get('profile_url'),
                roi_7d=data.get('roi_7d'),
                pnl_7d=data.get('pnl_7d'),
                win_rate=data.get('win_rate')
            )
            
            db.session.add(trader)
            old_values = None
            action = 'CREATE_FUTURES_TRADER'
        
        # Log the action
        ip_address, user_agent = get_client_info()
        if action == 'UPDATE_FUTURES_TRADER':
            AuditLog.log_update(
                user_id=current_user.id,
                table_name='futures_traders',
                record_id=trader.id,
                old_values=old_values,
                new_values=trader.to_dict(),
                ip_address=ip_address,
                user_agent=user_agent
            )
        else:
            AuditLog.log_create(
                user_id=current_user.id,
                table_name='futures_traders',
                record_id=trader.id,
                new_values=trader.to_dict(),
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        db.session.commit()
        
        return jsonify({
            'message': f'Trader {"updated" if existing_trader else "created"} successfully',
            'trader': trader.to_dict()
        }), 200 if existing_trader else 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create/update trader', 'details': str(e)}), 500

@futures_bp.route('/traders/<trader_id>/follow', methods=['POST'])
@permission_required('manage_futures')
def toggle_follow_trader(current_user, trader_id):
    """Toggle follow status for trader"""
    try:
        trader = FuturesTrader.query.get(trader_id)
        
        if not trader:
            return jsonify({'error': 'Trader not found'}), 404
        
        # Toggle follow status
        old_status = trader.is_followed
        new_status = trader.toggle_follow()
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='TOGGLE_FOLLOW_TRADER',
            table_name='futures_traders',
            record_id=trader.id,
            old_values={'is_followed': old_status},
            new_values={'is_followed': new_status},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': f'Trader {"followed" if new_status else "unfollowed"} successfully',
            'trader': trader.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to toggle follow status', 'details': str(e)}), 500

@futures_bp.route('/leaderboard', methods=['GET'])
@token_required
def get_leaderboard(current_user):
    """Get futures leaderboard"""
    try:
        # Get leaderboard settings
        settings = FuturesSetting.get_leaderboard_settings()
        criteria = settings.get('ranking_criteria', 'roi')
        limit = int(request.args.get('limit', 20))
        
        # Get top performers
        top_traders = FuturesTrader.get_top_performers(limit, criteria)
        
        return jsonify({
            'leaderboard': [trader.to_dict() for trader in top_traders],
            'ranking_criteria': criteria,
            'last_updated': top_traders[0].last_updated.isoformat() if top_traders else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch leaderboard', 'details': str(e)}), 500

@futures_bp.route('/followed-traders', methods=['GET'])
@token_required
def get_followed_traders(current_user):
    """Get followed traders"""
    try:
        followed_traders = FuturesTrader.get_followed_traders()
        
        return jsonify({
            'followed_traders': [trader.to_dict() for trader in followed_traders],
            'count': len(followed_traders)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch followed traders', 'details': str(e)}), 500

@futures_bp.route('/signals-by-trader/<binance_trader_id>', methods=['GET'])
@token_required
def get_signals_by_trader(current_user, binance_trader_id):
    """Get signals from specific trader"""
    try:
        limit = int(request.args.get('limit', 20))
        
        signals = FuturesSignal.query.filter_by(
            binance_trader_id=binance_trader_id
        ).order_by(FuturesSignal.created_at.desc()).limit(limit).all()
        
        # Get trader info
        trader = FuturesTrader.query.filter_by(
            binance_trader_id=binance_trader_id
        ).first()
        
        return jsonify({
            'signals': [signal.to_dict() for signal in signals],
            'trader': trader.to_dict() if trader else None,
            'total': FuturesSignal.query.filter_by(binance_trader_id=binance_trader_id).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch trader signals', 'details': str(e)}), 500

@futures_bp.route('/stats', methods=['GET'])
@token_required
def get_futures_stats(current_user):
    """Get futures statistics"""
    try:
        # Traders stats
        total_traders = FuturesTrader.query.count()
        followed_traders = FuturesTrader.query.filter_by(is_followed=True).count()
        
        # Signals stats (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_signals = FuturesSignal.query.filter(
            FuturesSignal.created_at >= week_ago
        ).count()
        
        sent_signals = FuturesSignal.query.filter(
            FuturesSignal.created_at >= week_ago,
            FuturesSignal.status == 'sent'
        ).count()
        
        # Top performer
        top_trader = FuturesTrader.query.order_by(FuturesTrader.roi_7d.desc()).first()
        
        return jsonify({
            'traders': {
                'total': total_traders,
                'followed': followed_traders,
                'top_performer': top_trader.to_dict() if top_trader else None
            },
            'signals_7d': {
                'total': recent_signals,
                'sent': sent_signals
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch futures statistics', 'details': str(e)}), 500

@futures_bp.route('/sync-leaderboard', methods=['POST'])
@permission_required('manage_futures')
def sync_leaderboard(current_user):
    """Sync leaderboard data from Binance (placeholder)"""
    try:
        # This would implement actual Binance leaderboard API integration
        # For now, we'll return a placeholder response
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action='SYNC_LEADERBOARD',
            new_values={'sync_time': datetime.utcnow().isoformat()},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Leaderboard sync initiated',
            'status': 'success',
            'synced_traders': 0,  # Placeholder
            'last_sync': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to sync leaderboard', 'details': str(e)}), 500

