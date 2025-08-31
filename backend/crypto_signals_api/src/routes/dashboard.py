from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from src.models import db
from src.models.user import User
from src.models.telegram_user import TelegramUser
from src.models.spot_signal import SpotSignal
from src.models.futures_signal import FuturesSignal
from src.models.payment import Payment
from src.models.broadcast_message import BroadcastMessage
from src.models.integration import Integration
from src.utils.auth import token_required
from src.utils.external_apis import ExternalAPIManager

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@token_required
def get_dashboard_overview(current_user):
    """Get dashboard overview data"""
    try:
        # Date ranges
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = datetime.utcnow() - timedelta(days=7)
        month_ago = datetime.utcnow() - timedelta(days=30)
        
        # Users statistics
        total_telegram_users = TelegramUser.query.filter_by(is_active=True).count()
        new_users_today = TelegramUser.query.filter(TelegramUser.joined_at >= today).count()
        new_users_week = TelegramUser.query.filter(TelegramUser.joined_at >= week_ago).count()
        
        # Signals statistics
        spot_signals_today = SpotSignal.query.filter(SpotSignal.created_at >= today).count()
        futures_signals_today = FuturesSignal.query.filter(FuturesSignal.created_at >= today).count()
        
        spot_signals_week = SpotSignal.query.filter(SpotSignal.created_at >= week_ago).count()
        futures_signals_week = FuturesSignal.query.filter(FuturesSignal.created_at >= week_ago).count()
        
        # Payments statistics
        total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.created_at >= month_ago
        ).scalar() or 0
        
        pending_payments = Payment.query.filter_by(status='pending').count()
        
        # Broadcasts statistics
        broadcasts_sent_week = BroadcastMessage.query.filter(
            BroadcastMessage.sent_at >= week_ago,
            BroadcastMessage.status == 'sent'
        ).count()
        
        # System health
        integrations_active = Integration.query.filter_by(is_active=True).count()
        integrations_total = Integration.query.count()
        
        # Market data
        market_data = ExternalAPIManager.get_market_regime()
        btc_ticker = ExternalAPIManager.get_binance_ticker('BTCUSDT')
        
        return jsonify({
            'users': {
                'total_active': total_telegram_users,
                'new_today': new_users_today,
                'new_this_week': new_users_week
            },
            'signals': {
                'spot_today': spot_signals_today,
                'futures_today': futures_signals_today,
                'spot_this_week': spot_signals_week,
                'futures_this_week': futures_signals_week,
                'total_today': spot_signals_today + futures_signals_today
            },
            'payments': {
                'revenue_30d': float(total_revenue),
                'pending_count': pending_payments
            },
            'broadcasts': {
                'sent_this_week': broadcasts_sent_week
            },
            'system': {
                'integrations_active': integrations_active,
                'integrations_total': integrations_total,
                'system_health': 'healthy' if integrations_active > 0 else 'warning'
            },
            'market': {
                'regime': market_data.get('regime', 'غير محدد'),
                'btc_price': float(btc_ticker['lastPrice']) if btc_ticker else None,
                'btc_change_24h': float(btc_ticker['priceChangePercent']) if btc_ticker else None,
                'fear_greed': market_data.get('fear_greed')
            },
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch dashboard overview', 'details': str(e)}), 500

@dashboard_bp.route('/activity', methods=['GET'])
@token_required
def get_recent_activity(current_user):
    """Get recent system activity"""
    try:
        limit = 20
        
        # Recent signals
        recent_spot_signals = SpotSignal.query.order_by(
            SpotSignal.created_at.desc()
        ).limit(5).all()
        
        recent_futures_signals = FuturesSignal.query.order_by(
            FuturesSignal.created_at.desc()
        ).limit(5).all()
        
        # Recent broadcasts
        recent_broadcasts = BroadcastMessage.query.order_by(
            BroadcastMessage.created_at.desc()
        ).limit(5).all()
        
        # Recent payments
        recent_payments = Payment.query.order_by(
            Payment.created_at.desc()
        ).limit(5).all()
        
        # Recent users
        recent_users = TelegramUser.query.order_by(
            TelegramUser.joined_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'recent_spot_signals': [signal.to_dict() for signal in recent_spot_signals],
            'recent_futures_signals': [signal.to_dict() for signal in recent_futures_signals],
            'recent_broadcasts': [broadcast.to_dict() for broadcast in recent_broadcasts],
            'recent_payments': [payment.to_dict() for payment in recent_payments],
            'recent_users': [user.to_dict() for user in recent_users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch recent activity', 'details': str(e)}), 500

@dashboard_bp.route('/charts/users', methods=['GET'])
@token_required
def get_users_chart_data(current_user):
    """Get users growth chart data"""
    try:
        days = int(request.args.get('days', 30))
        
        # Generate date range
        end_date = datetime.utcnow().replace(hour=23, minute=59, second=59)
        start_date = end_date - timedelta(days=days)
        
        # Get daily user counts
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Count users joined on this day
            new_users = TelegramUser.query.filter(
                TelegramUser.joined_at >= current_date,
                TelegramUser.joined_at < next_date
            ).count()
            
            # Count total active users up to this day
            total_users = TelegramUser.query.filter(
                TelegramUser.joined_at <= next_date,
                TelegramUser.is_active == True
            ).count()
            
            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'new_users': new_users,
                'total_users': total_users
            })
            
            current_date = next_date
        
        return jsonify({
            'chart_data': daily_data,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch users chart data', 'details': str(e)}), 500

@dashboard_bp.route('/charts/signals', methods=['GET'])
@token_required
def get_signals_chart_data(current_user):
    """Get signals chart data"""
    try:
        days = int(request.args.get('days', 7))
        
        # Generate date range
        end_date = datetime.utcnow().replace(hour=23, minute=59, second=59)
        start_date = end_date - timedelta(days=days)
        
        # Get daily signal counts
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Count signals created on this day
            spot_signals = SpotSignal.query.filter(
                SpotSignal.created_at >= current_date,
                SpotSignal.created_at < next_date
            ).count()
            
            futures_signals = FuturesSignal.query.filter(
                FuturesSignal.created_at >= current_date,
                FuturesSignal.created_at < next_date
            ).count()
            
            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'spot_signals': spot_signals,
                'futures_signals': futures_signals,
                'total_signals': spot_signals + futures_signals
            })
            
            current_date = next_date
        
        return jsonify({
            'chart_data': daily_data,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch signals chart data', 'details': str(e)}), 500

@dashboard_bp.route('/system-status', methods=['GET'])
@token_required
def get_system_status(current_user):
    """Get system status and health checks"""
    try:
        # Database connectivity
        try:
            db.session.execute('SELECT 1')
            database_status = 'healthy'
        except Exception:
            database_status = 'error'
        
        # External APIs status
        binance_status = 'unknown'
        try:
            ticker = ExternalAPIManager.get_binance_ticker('BTCUSDT')
            binance_status = 'healthy' if ticker else 'error'
        except Exception:
            binance_status = 'error'
        
        # Integrations status
        integrations = Integration.query.all()
        integrations_status = []
        
        for integration in integrations:
            status = {
                'provider': integration.provider,
                'is_active': integration.is_active,
                'last_tested': integration.last_tested.isoformat() if integration.last_tested else None,
                'test_result': integration.test_result
            }
            integrations_status.append(status)
        
        # Overall system health
        overall_health = 'healthy'
        if database_status == 'error':
            overall_health = 'critical'
        elif binance_status == 'error':
            overall_health = 'warning'
        
        return jsonify({
            'overall_health': overall_health,
            'components': {
                'database': database_status,
                'binance_api': binance_status,
                'integrations': integrations_status
            },
            'last_checked': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch system status', 'details': str(e)}), 500

