from flask import Blueprint, request, jsonify
from src.models import db
from src.models.integration import Integration
from src.models.audit_log import AuditLog
from src.utils.auth import token_required, permission_required, get_client_info
from src.utils.external_apis import ExternalAPIManager

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/', methods=['GET'])
@permission_required('manage_integrations')
def get_integrations(current_user):
    """Get all integrations"""
    try:
        integrations = Integration.query.all()
        return jsonify({
            'integrations': [integration.to_dict() for integration in integrations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch integrations', 'details': str(e)}), 500

@integrations_bp.route('/<provider>', methods=['GET'])
@permission_required('manage_integrations')
def get_integration(current_user, provider):
    """Get specific integration"""
    try:
        integration = Integration.query.filter_by(provider=provider).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        return jsonify({'integration': integration.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch integration', 'details': str(e)}), 500

@integrations_bp.route('/<provider>', methods=['POST', 'PUT'])
@permission_required('manage_integrations')
def save_integration(current_user, provider):
    """Save or update integration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Find existing integration or create new one
        integration = Integration.query.filter_by(provider=provider).first()
        is_new = integration is None
        
        if is_new:
            integration = Integration(provider=provider)
            db.session.add(integration)
        
        # Store old values for audit log
        old_values = integration.to_dict() if not is_new else {}
        
        # Update API key if provided
        if 'api_key' in data and data['api_key']:
            integration.set_api_key(data['api_key'])
        
        # Update secret key if provided
        if 'secret_key' in data and data['secret_key']:
            integration.set_secret_key(data['secret_key'])
        
        # Update active status
        if 'is_active' in data:
            integration.is_active = bool(data['is_active'])
        
        # Log the action
        ip_address, user_agent = get_client_info()
        action = 'CREATE_INTEGRATION' if is_new else 'UPDATE_INTEGRATION'
        AuditLog.log_action(
            user_id=current_user.id,
            action=action,
            table_name='integrations',
            record_id=integration.id,
            old_values=old_values if not is_new else None,
            new_values=integration.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Integration saved successfully',
            'integration': integration.to_dict()
        }), 200 if not is_new else 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save integration', 'details': str(e)}), 500

@integrations_bp.route('/<provider>/test', methods=['POST'])
@permission_required('manage_integrations')
def test_integration(current_user, provider):
    """Test integration connection"""
    try:
        integration = Integration.query.filter_by(provider=provider).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Get decrypted keys
        api_key = integration.get_api_key()
        secret_key = integration.get_secret_key()
        
        # Test connection based on provider
        success = False
        message = "Unknown provider"
        
        if provider.lower() == 'binance':
            success, message = ExternalAPIManager.test_binance_connection(api_key, secret_key)
        elif provider.lower() == 'tradingeconomics':
            success, message = ExternalAPIManager.test_trading_economics_connection(api_key)
        elif provider.lower() in ['nowpayments', 'btcpay']:
            # For payment providers, we'll implement specific tests later
            success, message = True, "Connection test not implemented yet"
        else:
            success, message = False, f"Unknown provider: {provider}"
        
        # Update test result
        integration.update_test_result(success, message if not success else None)
        
        # Log the test
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action=f'TEST_INTEGRATION_{provider.upper()}',
            table_name='integrations',
            record_id=integration.id,
            new_values={'test_result': 'success' if success else 'failed', 'message': message},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'success': success,
            'message': message,
            'last_tested': integration.last_tested.isoformat() if integration.last_tested else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to test integration', 'details': str(e)}), 500

@integrations_bp.route('/<provider>/toggle', methods=['POST'])
@permission_required('manage_integrations')
def toggle_integration(current_user, provider):
    """Toggle integration active status"""
    try:
        integration = Integration.query.filter_by(provider=provider).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Store old status for audit
        old_status = integration.is_active
        
        # Toggle status
        integration.is_active = not integration.is_active
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action=f'TOGGLE_INTEGRATION_{provider.upper()}',
            table_name='integrations',
            record_id=integration.id,
            old_values={'is_active': old_status},
            new_values={'is_active': integration.is_active},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': f'Integration {"activated" if integration.is_active else "deactivated"}',
            'is_active': integration.is_active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to toggle integration', 'details': str(e)}), 500

@integrations_bp.route('/<provider>', methods=['DELETE'])
@permission_required('manage_integrations')
def delete_integration(current_user, provider):
    """Delete integration"""
    try:
        integration = Integration.query.filter_by(provider=provider).first()
        
        if not integration:
            return jsonify({'error': 'Integration not found'}), 404
        
        # Store data for audit log
        old_values = integration.to_dict()
        
        # Log the deletion
        ip_address, user_agent = get_client_info()
        AuditLog.log_action(
            user_id=current_user.id,
            action=f'DELETE_INTEGRATION_{provider.upper()}',
            table_name='integrations',
            record_id=integration.id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Delete integration
        db.session.delete(integration)
        db.session.commit()
        
        return jsonify({'message': 'Integration deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete integration', 'details': str(e)}), 500

@integrations_bp.route('/providers', methods=['GET'])
@token_required
def get_available_providers(current_user):
    """Get list of available integration providers"""
    try:
        providers = [
            {
                'id': 'binance',
                'name': 'Binance',
                'description': 'Binance API for market data and trading',
                'fields': [
                    {'name': 'api_key', 'label': 'API Key', 'type': 'password', 'required': True},
                    {'name': 'secret_key', 'label': 'Secret Key', 'type': 'password', 'required': True}
                ]
            },
            {
                'id': 'tradingeconomics',
                'name': 'Trading Economics',
                'description': 'Economic calendar and indicators',
                'fields': [
                    {'name': 'api_key', 'label': 'API Key', 'type': 'password', 'required': False}
                ]
            },
            {
                'id': 'nowpayments',
                'name': 'NOWPayments',
                'description': 'Cryptocurrency payment processing',
                'fields': [
                    {'name': 'api_key', 'label': 'API Key', 'type': 'password', 'required': True}
                ]
            },
            {
                'id': 'btcpay',
                'name': 'BTCPay Server',
                'description': 'Self-hosted payment processor',
                'fields': [
                    {'name': 'api_key', 'label': 'API Key', 'type': 'password', 'required': True},
                    {'name': 'server_url', 'label': 'Server URL', 'type': 'text', 'required': True}
                ]
            }
        ]
        
        return jsonify({'providers': providers}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch providers', 'details': str(e)}), 500

