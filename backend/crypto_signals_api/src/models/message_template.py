from datetime import datetime
from . import db

class MessageTemplate(db.Model):
    __tablename__ = 'message_templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    name = db.Column(db.String(100), nullable=False)
    identifier = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    template_type = db.Column(db.String(20), default='general')
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, identifier, content, template_type='general', created_by=None):
        self.name = name
        self.identifier = identifier
        self.content = content
        self.template_type = template_type
        self.created_by = created_by
    
    def format_message(self, **kwargs):
        """Format template with provided variables"""
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
    
    def get_variables(self):
        """Extract variables from template content"""
        import re
        variables = re.findall(r'\{(\w+)\}', self.content)
        return list(set(variables))
    
    def validate_content(self):
        """Validate template content"""
        try:
            # Try to format with dummy data to check syntax
            variables = self.get_variables()
            dummy_data = {var: f"test_{var}" for var in variables}
            self.content.format(**dummy_data)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'identifier': self.identifier,
            'content': self.content,
            'template_type': self.template_type,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'variables': self.get_variables()
        }
    
    def __repr__(self):
        return f'<MessageTemplate {self.identifier}>'

