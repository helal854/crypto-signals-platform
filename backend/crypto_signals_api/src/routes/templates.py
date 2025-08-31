from flask import Blueprint, request, jsonify
from src.models import db
from src.models.message_template import MessageTemplate
from src.models.audit_log import AuditLog
from src.utils.auth import token_required, permission_required, get_client_info

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/', methods=['GET'])
@token_required
def get_templates(current_user):
    """Get all message templates"""
    try:
        template_type = request.args.get('type')
        
        query = MessageTemplate.query
        
        if template_type:
            query = query.filter_by(template_type=template_type)
        
        templates = query.order_by(MessageTemplate.created_at.desc()).all()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch templates', 'details': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['GET'])
@token_required
def get_template(current_user, template_id):
    """Get specific template"""
    try:
        template = MessageTemplate.query.get(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch template', 'details': str(e)}), 500

@templates_bp.route('/by-identifier/<identifier>', methods=['GET'])
@token_required
def get_template_by_identifier(current_user, identifier):
    """Get template by identifier"""
    try:
        template = MessageTemplate.query.filter_by(identifier=identifier).first()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch template', 'details': str(e)}), 500

@templates_bp.route('/', methods=['POST'])
@permission_required('write')
def create_template(current_user):
    """Create new message template"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'identifier', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if identifier already exists
        existing = MessageTemplate.query.filter_by(identifier=data['identifier']).first()
        if existing:
            return jsonify({'error': 'Template identifier already exists'}), 400
        
        # Create template
        template = MessageTemplate(
            name=data['name'],
            identifier=data['identifier'],
            content=data['content'],
            template_type=data.get('template_type', 'general'),
            created_by=current_user.id
        )
        
        # Validate template content
        is_valid, error_message = template.validate_content()
        if not is_valid:
            return jsonify({'error': 'Invalid template content', 'details': error_message}), 400
        
        db.session.add(template)
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_create(
            user_id=current_user.id,
            table_name='message_templates',
            record_id=template.id,
            new_values=template.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Template created successfully',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create template', 'details': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['PUT'])
@permission_required('write')
def update_template(current_user, template_id):
    """Update message template"""
    try:
        template = MessageTemplate.query.get(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Store old values for audit
        old_values = template.to_dict()
        
        # Check if identifier is being changed and if it conflicts
        if 'identifier' in data and data['identifier'] != template.identifier:
            existing = MessageTemplate.query.filter_by(identifier=data['identifier']).first()
            if existing:
                return jsonify({'error': 'Template identifier already exists'}), 400
        
        # Update fields
        updatable_fields = ['name', 'identifier', 'content', 'template_type']
        for field in updatable_fields:
            if field in data:
                setattr(template, field, data[field])
        
        # Validate updated template content
        is_valid, error_message = template.validate_content()
        if not is_valid:
            return jsonify({'error': 'Invalid template content', 'details': error_message}), 400
        
        # Log the action
        ip_address, user_agent = get_client_info()
        AuditLog.log_update(
            user_id=current_user.id,
            table_name='message_templates',
            record_id=template.id,
            old_values=old_values,
            new_values=template.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Template updated successfully',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update template', 'details': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['DELETE'])
@permission_required('delete')
def delete_template(current_user, template_id):
    """Delete message template"""
    try:
        template = MessageTemplate.query.get(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Store data for audit log
        old_values = template.to_dict()
        
        # Log the deletion
        ip_address, user_agent = get_client_info()
        AuditLog.log_delete(
            user_id=current_user.id,
            table_name='message_templates',
            record_id=template.id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Delete template
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete template', 'details': str(e)}), 500

@templates_bp.route('/<template_id>/preview', methods=['POST'])
@token_required
def preview_template(current_user, template_id):
    """Preview template with sample data"""
    try:
        template = MessageTemplate.query.get(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        data = request.get_json() or {}
        variables = data.get('variables', {})
        
        try:
            # Get template variables
            template_vars = template.get_variables()
            
            # Use provided variables or create sample data
            sample_data = {}
            for var in template_vars:
                if var in variables:
                    sample_data[var] = variables[var]
                else:
                    # Create sample data based on variable name
                    if 'symbol' in var.lower():
                        sample_data[var] = 'BTCUSDT'
                    elif 'price' in var.lower():
                        sample_data[var] = '45000.00'
                    elif 'target' in var.lower():
                        sample_data[var] = '46000.00'
                    elif 'stop' in var.lower():
                        sample_data[var] = '44000.00'
                    elif 'trader' in var.lower():
                        sample_data[var] = 'أحمد المتداول'
                    elif 'date' in var.lower() or 'time' in var.lower():
                        sample_data[var] = '2024-01-15 14:30'
                    else:
                        sample_data[var] = f'sample_{var}'
            
            # Format template
            formatted_message = template.format_message(**sample_data)
            
            return jsonify({
                'preview': formatted_message,
                'variables_used': sample_data,
                'template_variables': template_vars
            }), 200
            
        except ValueError as e:
            return jsonify({'error': 'Template formatting error', 'details': str(e)}), 400
        
    except Exception as e:
        return jsonify({'error': 'Failed to preview template', 'details': str(e)}), 500

@templates_bp.route('/types', methods=['GET'])
@token_required
def get_template_types(current_user):
    """Get available template types"""
    try:
        types = [
            {
                'id': 'general',
                'name': 'عام',
                'description': 'قوالب عامة للرسائل'
            },
            {
                'id': 'spot_signal',
                'name': 'إشارة Spot',
                'description': 'قوالب إشارات التداول الفوري'
            },
            {
                'id': 'futures_signal',
                'name': 'إشارة Futures',
                'description': 'قوالب إشارات العقود الآجلة'
            },
            {
                'id': 'welcome',
                'name': 'ترحيب',
                'description': 'رسائل الترحيب بالمستخدمين الجدد'
            },
            {
                'id': 'notification',
                'name': 'إشعار',
                'description': 'إشعارات النظام والتحديثات'
            },
            {
                'id': 'subscription',
                'name': 'اشتراك',
                'description': 'رسائل متعلقة بالاشتراكات'
            }
        ]
        
        return jsonify({'types': types}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch template types', 'details': str(e)}), 500

@templates_bp.route('/variables', methods=['GET'])
@token_required
def get_common_variables(current_user):
    """Get common template variables"""
    try:
        variables = {
            'spot_signal': [
                'symbol', 'side', 'entry_min', 'entry_max', 'target_1', 'target_2', 
                'target_3', 'target_4', 'target_5', 'stop_loss', 'support_level', 
                'resistance_level', 'created_at'
            ],
            'futures_signal': [
                'symbol', 'side', 'entry_price', 'target_1', 'target_2', 'stop_loss',
                'leverage', 'position_value', 'trader_name', 'trader_profile_url',
                'created_at'
            ],
            'general': [
                'user_name', 'user_id', 'date', 'time', 'platform_name'
            ],
            'subscription': [
                'user_name', 'subscription_type', 'expiry_date', 'amount', 'currency'
            ]
        }
        
        return jsonify({'variables': variables}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch template variables', 'details': str(e)}), 500

