import requests
import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
from flask import current_app

class ExternalAPIManager:
    """Manager for external API integrations"""
    
    @staticmethod
    def get_binance_ticker(symbol='BTCUSDT'):
        """Get ticker data from Binance"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"Binance API error: {e}")
            return None
    
    @staticmethod
    def get_binance_klines(symbol='BTCUSDT', interval='1d', limit=100):
        """Get klines data from Binance for support/resistance calculation"""
        try:
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"Binance klines API error: {e}")
            return None
    
    @staticmethod
    def calculate_support_resistance(klines_data):
        """Calculate support and resistance levels from klines"""
        if not klines_data:
            return None, None
        
        try:
            # Extract high and low prices
            highs = [float(kline[2]) for kline in klines_data]  # High prices
            lows = [float(kline[3]) for kline in klines_data]   # Low prices
            
            # Simple support/resistance calculation
            resistance = max(highs[-20:])  # Highest high in last 20 periods
            support = min(lows[-20:])      # Lowest low in last 20 periods
            
            return support, resistance
        except Exception as e:
            current_app.logger.error(f"Support/Resistance calculation error: {e}")
            return None, None
    
    @staticmethod
    def get_fear_greed_index():
        """Get Fear & Greed Index from Alternative.me"""
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                fng_data = data['data'][0]
                return {
                    'value': int(fng_data['value']),
                    'value_classification': fng_data['value_classification'],
                    'timestamp': fng_data['timestamp']
                }
        except Exception as e:
            current_app.logger.error(f"Fear & Greed API error: {e}")
        
        return None
    
    @staticmethod
    def get_coingecko_market_data(coins=['bitcoin', 'ethereum', 'solana']):
        """Get market data from CoinGecko"""
        try:
            coins_str = ','.join(coins)
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coins_str,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"CoinGecko API error: {e}")
            return None
    
    @staticmethod
    def get_trading_economics_calendar():
        """Get economic calendar from TradingEconomics"""
        try:
            # Try with API key first
            api_key = current_app.config.get('TRADING_ECONOMICS_KEY')
            
            if api_key:
                url = f"https://api.tradingeconomics.com/calendar"
                headers = {'Authorization': f'Client {api_key}'}
                params = {
                    'c': 'guest:guest',  # Fallback credentials
                    'f': 'json'
                }
            else:
                # Use guest mode
                url = "https://api.tradingeconomics.com/calendar"
                params = {
                    'c': current_app.config.get('TE_GUEST', 'guest:guest'),
                    'f': 'json'
                }
                headers = {}
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Filter for next 7 days
                today = datetime.now()
                week_later = today + timedelta(days=7)
                
                filtered_events = []
                for event in data[:50]:  # Limit to first 50 events
                    try:
                        event_date = datetime.fromisoformat(event.get('Date', '').replace('T', ' ').split('.')[0])
                        if today <= event_date <= week_later:
                            filtered_events.append({
                                'date': event_date.strftime('%Y-%m-%d'),
                                'time': event_date.strftime('%H:%M'),
                                'country': event.get('Country', ''),
                                'event': event.get('Event', ''),
                                'importance': event.get('Importance', 'Low'),
                                'actual': event.get('Actual', ''),
                                'forecast': event.get('Forecast', ''),
                                'previous': event.get('Previous', '')
                            })
                    except (ValueError, TypeError):
                        continue
                
                return {
                    'source': 'TradingEconomics',
                    'events': filtered_events[:20]  # Limit to 20 events
                }
            else:
                # Fallback to mock data
                return ExternalAPIManager._get_mock_economic_calendar()
                
        except Exception as e:
            current_app.logger.error(f"TradingEconomics API error: {e}")
            return ExternalAPIManager._get_mock_economic_calendar()
    
    @staticmethod
    def _get_mock_economic_calendar():
        """Fallback mock economic calendar"""
        today = datetime.now()
        return {
            'source': 'Mock Data',
            'events': [
                {
                    'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'time': '14:30',
                    'country': 'US',
                    'event': 'Non-Farm Payrolls',
                    'importance': 'High',
                    'actual': '',
                    'forecast': '200K',
                    'previous': '187K'
                },
                {
                    'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'time': '12:30',
                    'country': 'US',
                    'event': 'CPI (Consumer Price Index)',
                    'importance': 'High',
                    'actual': '',
                    'forecast': '3.2%',
                    'previous': '3.1%'
                },
                {
                    'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'time': '18:00',
                    'country': 'US',
                    'event': 'Federal Reserve Interest Rate Decision',
                    'importance': 'High',
                    'actual': '',
                    'forecast': '5.25%',
                    'previous': '5.25%'
                }
            ]
        }
    
    @staticmethod
    def test_binance_connection(api_key=None, secret_key=None):
        """Test Binance API connection"""
        try:
            if api_key and secret_key:
                # Test authenticated endpoint
                url = "https://api.binance.com/api/v3/account"
                # This would require proper signature - for now just test public endpoint
                pass
            
            # Test public endpoint
            url = "https://api.binance.com/api/v3/ping"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    @staticmethod
    def test_trading_economics_connection(api_key=None):
        """Test TradingEconomics API connection"""
        try:
            url = "https://api.tradingeconomics.com/calendar"
            params = {'c': 'guest:guest', 'f': 'json'}
            
            if api_key:
                headers = {'Authorization': f'Client {api_key}'}
            else:
                headers = {}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    @staticmethod
    def get_market_regime():
        """Determine market regime based on Fear & Greed and price trends"""
        try:
            # Get Fear & Greed Index
            fng_data = ExternalAPIManager.get_fear_greed_index()
            
            # Get BTC price trend
            btc_ticker = ExternalAPIManager.get_binance_ticker('BTCUSDT')
            
            regime = "مستقر"  # Default: Stable
            
            if fng_data and btc_ticker:
                fng_value = fng_data['value']
                price_change = float(btc_ticker.get('priceChangePercent', 0))
                
                if fng_value >= 75 and price_change > 5:
                    regime = "صاعد بقوة"  # Strongly Bullish
                elif fng_value >= 55 and price_change > 2:
                    regime = "صاعد"  # Bullish
                elif fng_value <= 25 and price_change < -5:
                    regime = "هابط بقوة"  # Strongly Bearish
                elif fng_value <= 45 and price_change < -2:
                    regime = "هابط"  # Bearish
                else:
                    regime = "مستقر"  # Stable
            
            return {
                'regime': regime,
                'fear_greed': fng_data,
                'btc_change': btc_ticker.get('priceChangePercent') if btc_ticker else None
            }
        except Exception as e:
            current_app.logger.error(f"Market regime calculation error: {e}")
            return {'regime': 'غير محدد', 'fear_greed': None, 'btc_change': None}

