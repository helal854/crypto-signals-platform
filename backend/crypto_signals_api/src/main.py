import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from src.models import db
from src.config import config

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from src.routes.auth import auth_bp
    from src.routes.integrations import integrations_bp
    from src.routes.market_data import market_data_bp
    from src.routes.signals import signals_bp
    from src.routes.payments import payments_bp
    from src.routes.templates import templates_bp
    from src.routes.broadcasts import broadcasts_bp
    from src.routes.futures import futures_bp
    from src.routes.users import users_bp
    from src.routes.dashboard import dashboard_bp
    
    # Register API routes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(integrations_bp, url_prefix='/api/integrations')
    app.register_blueprint(market_data_bp, url_prefix='/api/market-data')
    app.register_blueprint(signals_bp, url_prefix='/api/signals')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(templates_bp, url_prefix='/api/templates')
    app.register_blueprint(broadcasts_bp, url_prefix='/api/broadcasts')
    app.register_blueprint(futures_bp, url_prefix='/api/futures')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'crypto-signals-api'}, 200
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        return {
            'name': 'Crypto Signals Platform API',
            'version': '1.0.0',
            'description': 'Backend API for crypto trading signals platform',
            'endpoints': {
                'auth': '/api/auth',
                'integrations': '/api/integrations',
                'market_data': '/api/market-data',
                'signals': '/api/signals',
                'payments': '/api/payments',
                'templates': '/api/templates',
                'broadcasts': '/api/broadcasts',
                'futures': '/api/futures',
                'users': '/api/users',
                'dashboard': '/api/dashboard'
            }
        }, 200
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

