"""
Simple test for Backend APIs
"""

import requests
import json
from flask import Flask
from flask_cors import CORS

# Create a simple test Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def health_check():
    return {'status': 'ok', 'message': 'Backend is running'}

@app.route('/api/test')
def test_endpoint():
    return {
        'status': 'success',
        'data': {
            'message': 'Test endpoint working',
            'features': [
                'Authentication',
                'User Management',
                'Signal Management',
                'Payment Processing',
                'Market Data',
                'External Integrations'
            ]
        }
    }

@app.route('/api/market/test')
def test_market_data():
    # Mock market data
    return {
        'status': 'success',
        'data': {
            'btc_price': 43250.00,
            'eth_price': 2650.00,
            'fear_greed_index': 65,
            'top_symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        }
    }

@app.route('/api/signals/test')
def test_signals():
    # Mock signals data
    return {
        'status': 'success',
        'data': {
            'spot_signals': 15,
            'futures_signals': 8,
            'active_traders': 25,
            'total_profit': 12450.75
        }
    }

if __name__ == '__main__':
    print("🚀 Starting Backend Test Server...")
    print("📊 Available endpoints:")
    print("   - GET /")
    print("   - GET /api/test")
    print("   - GET /api/market/test")
    print("   - GET /api/signals/test")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)

