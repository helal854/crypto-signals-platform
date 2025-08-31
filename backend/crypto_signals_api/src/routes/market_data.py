from flask import Blueprint, jsonify
from src.utils.external_apis import ExternalAPIManager
from src.utils.auth import token_required

market_data_bp = Blueprint('market_data', __name__)

@market_data_bp.route('/news', methods=['GET'])
@token_required
def get_market_news(current_user):
    """Get market status and news"""
    try:
        # Get market regime
        market_data = ExternalAPIManager.get_market_regime()
        
        # Get support/resistance for major coins
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT']
        support_resistance = {}
        
        for symbol in symbols:
            klines = ExternalAPIManager.get_binance_klines(symbol, '1d', 50)
            support, resistance = ExternalAPIManager.calculate_support_resistance(klines)
            
            if support and resistance:
                support_resistance[symbol.replace('USDT', '')] = {
                    'support': round(support, 4),
                    'resistance': round(resistance, 4)
                }
        
        # Get current prices
        current_prices = {}
        for symbol in symbols:
            ticker = ExternalAPIManager.get_binance_ticker(symbol)
            if ticker:
                current_prices[symbol.replace('USDT', '')] = {
                    'price': float(ticker['lastPrice']),
                    'change_24h': float(ticker['priceChangePercent'])
                }
        
        return jsonify({
            'market_regime': market_data['regime'],
            'fear_greed_index': market_data['fear_greed'],
            'support_resistance': support_resistance,
            'current_prices': current_prices,
            'last_updated': ExternalAPIManager.get_binance_ticker('BTCUSDT').get('closeTime') if ExternalAPIManager.get_binance_ticker('BTCUSDT') else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch market data', 'details': str(e)}), 500

@market_data_bp.route('/schedule', methods=['GET'])
@token_required
def get_economic_schedule(current_user):
    """Get economic calendar/schedule"""
    try:
        calendar_data = ExternalAPIManager.get_trading_economics_calendar()
        
        if not calendar_data:
            return jsonify({
                'source': 'none',
                'events': [],
                'error': 'Unable to fetch economic calendar'
            }), 200
        
        return jsonify(calendar_data), 200
        
    except Exception as e:
        return jsonify({
            'source': 'error',
            'events': [],
            'error': f'Failed to fetch economic schedule: {str(e)}'
        }), 500

@market_data_bp.route('/fear-greed', methods=['GET'])
@token_required
def get_fear_greed(current_user):
    """Get Fear & Greed Index"""
    try:
        fng_data = ExternalAPIManager.get_fear_greed_index()
        
        if not fng_data:
            return jsonify({'error': 'Unable to fetch Fear & Greed Index'}), 500
        
        return jsonify(fng_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch Fear & Greed Index', 'details': str(e)}), 500

@market_data_bp.route('/ticker/<symbol>', methods=['GET'])
@token_required
def get_ticker(current_user, symbol):
    """Get ticker data for specific symbol"""
    try:
        ticker_data = ExternalAPIManager.get_binance_ticker(symbol.upper())
        
        if not ticker_data:
            return jsonify({'error': f'Unable to fetch ticker for {symbol}'}), 404
        
        return jsonify({
            'symbol': ticker_data['symbol'],
            'price': float(ticker_data['lastPrice']),
            'change_24h': float(ticker_data['priceChangePercent']),
            'volume_24h': float(ticker_data['volume']),
            'high_24h': float(ticker_data['highPrice']),
            'low_24h': float(ticker_data['lowPrice']),
            'last_updated': ticker_data['closeTime']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch ticker', 'details': str(e)}), 500

@market_data_bp.route('/support-resistance/<symbol>', methods=['GET'])
@token_required
def get_support_resistance(current_user, symbol):
    """Get support and resistance levels for symbol"""
    try:
        klines = ExternalAPIManager.get_binance_klines(symbol.upper(), '1d', 100)
        support, resistance = ExternalAPIManager.calculate_support_resistance(klines)
        
        if support is None or resistance is None:
            return jsonify({'error': f'Unable to calculate support/resistance for {symbol}'}), 404
        
        return jsonify({
            'symbol': symbol.upper(),
            'support': round(support, 6),
            'resistance': round(resistance, 6),
            'calculated_at': ExternalAPIManager.get_binance_ticker(symbol.upper()).get('closeTime') if ExternalAPIManager.get_binance_ticker(symbol.upper()) else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to calculate support/resistance', 'details': str(e)}), 500

@market_data_bp.route('/coingecko/<coins>', methods=['GET'])
@token_required
def get_coingecko_data(current_user, coins):
    """Get CoinGecko market data for specified coins"""
    try:
        coin_list = coins.split(',')
        market_data = ExternalAPIManager.get_coingecko_market_data(coin_list)
        
        if not market_data:
            return jsonify({'error': 'Unable to fetch CoinGecko data'}), 500
        
        return jsonify(market_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch CoinGecko data', 'details': str(e)}), 500

@market_data_bp.route('/overview', methods=['GET'])
@token_required
def get_market_overview(current_user):
    """Get comprehensive market overview"""
    try:
        # Get market regime
        market_regime = ExternalAPIManager.get_market_regime()
        
        # Get major cryptocurrencies data
        major_coins = ['bitcoin', 'ethereum', 'solana']
        coingecko_data = ExternalAPIManager.get_coingecko_market_data(major_coins)
        
        # Get BTC dominance and total market cap (simplified)
        btc_ticker = ExternalAPIManager.get_binance_ticker('BTCUSDT')
        
        overview = {
            'market_regime': market_regime,
            'major_coins': coingecko_data,
            'btc_price': float(btc_ticker['lastPrice']) if btc_ticker else None,
            'btc_change_24h': float(btc_ticker['priceChangePercent']) if btc_ticker else None,
            'last_updated': btc_ticker.get('closeTime') if btc_ticker else None
        }
        
        return jsonify(overview), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch market overview', 'details': str(e)}), 500

